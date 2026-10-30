"""Contract for the role registry and the agent-definition generator.

The generator is the zcode adapter mechanism of the unit: `.agents/config.toml`
names the roles (`[agents.<name>]`, required key `model`) and
`skills/init/gen_agents.py` (carried by the init bundle, so an installed
project can run it) keeps one definition per role in `.zcode/agents/` with
the configured model. These checks pin the observable effects: validation
distinguishes unknown (warn) from invalid (fail), definitions carry the
configured model, a rerun with an unchanged config rewrites nothing, a model
drift is named and fixed by regeneration, and a missing config writes nothing.

spec: docs/plans/review-config.md#готово — schema `.agents/config.toml` (секция
      `[agents.<name>]`, ключ `model`; незнакомое — предупреждение, неверное —
      отказ); генерация по одному определению на роль, сверка модели,
      перегенерация при расхождении
spec: docs/plans/review-config.md#рамки — определения ролей производные от
      конфига: `.zcode/agents/` в `.gitignore`, не коммитятся
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
GEN = REPO / "skills" / "init" / "gen_agents.py"

CORE_ROLES = ("reviewer-spec", "reviewer-tests", "reviewer-code", "reviewer-kb", "critic")


def run(project: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python3", str(GEN), str(project)],
        capture_output=True,
        text=True,
        check=False,
    )


def write_config(project: Path, model_of: dict[str, str], extra: str = "") -> None:
    lines = []
    for name, model in model_of.items():
        lines.append(f"[agents.{name}]")
        lines.append(f'model = "{model}"')
        lines.append("")
    (project / ".agents").mkdir(parents=True, exist_ok=True)
    (project / ".agents" / "config.toml").write_text("\n".join(lines) + extra, encoding="utf-8")


def core_config(project: Path, model: str = "provider-a/model-x") -> None:
    write_config(project, {name: model for name in CORE_ROLES})


def definitions(project: Path) -> dict[str, str]:
    agents_dir = project / ".zcode" / "agents"
    if not agents_dir.is_dir():
        return {}
    return {p.name: p.read_text(encoding="utf-8") for p in sorted(agents_dir.glob("*.md"))}


def frontmatter_model(text: str) -> str | None:
    """The `model:` value of a definition's frontmatter, quotes stripped."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("model:"):
            value = line[len("model:"):].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "'\"":
                value = value[1:-1]
            return value
    return None


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    return root


def test_one_definition_per_role_with_configured_model(project: Path) -> None:
    models = {name: f"provider-{i}/model-{i}" for i, name in enumerate(CORE_ROLES, start=1)}
    write_config(project, models)
    result = run(project)
    assert result.returncode == 0, result.stderr
    files = definitions(project)
    assert set(files) == {f"{name}.md" for name in CORE_ROLES}
    for name, model in models.items():
        assert frontmatter_model(files[f"{name}.md"]) == model
    for name in CORE_ROLES:
        assert name in result.stdout


def test_rerun_with_unchanged_config_rewrites_nothing(project: Path) -> None:
    core_config(project)
    assert run(project).returncode == 0
    agents_dir = project / ".zcode" / "agents"
    before = {
        p.name: (p.stat().st_ino, p.stat().st_mtime_ns, p.read_bytes())
        for p in sorted(agents_dir.iterdir())
    }
    result = run(project)
    assert result.returncode == 0, result.stderr
    after = {
        p.name: (p.stat().st_ino, p.stat().st_mtime_ns, p.read_bytes())
        for p in sorted(agents_dir.iterdir())
    }
    assert before == after


def test_model_drift_is_named_and_regenerated(project: Path) -> None:
    core_config(project)
    assert run(project).returncode == 0
    write_config(project, {**{n: "provider-a/model-x" for n in CORE_ROLES}, "critic": "provider-b/model-y"})
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert "critic" in result.stdout
    assert "provider-a/model-x" in result.stdout
    assert "provider-b/model-y" in result.stdout
    assert frontmatter_model(definitions(project)["critic.md"]) == "provider-b/model-y"


def test_no_config_writes_nothing(project: Path) -> None:
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert not (project / ".zcode").exists()


def test_unknown_section_and_key_warn_but_do_not_fail(project: Path) -> None:
    write_config(
        project,
        {"reviewer-spec": "provider-a/model-x"},
        extra="[unknown-section]\nkey = 1\n\n[agents.reviewer-tests]\nmodel = \"provider-a/model-x\"\nstrange = true\n",
    )
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert "unknown-section" in result.stderr
    assert "strange" in result.stderr
    assert "'agents'" not in result.stderr  # the known section itself is not unknown
    assert set(definitions(project)) == {"reviewer-spec.md", "reviewer-tests.md"}


def test_role_without_model_fails_with_named_error(project: Path) -> None:
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(
        '[agents.reviewer-spec]\n[agents.critic]\nmodel = "provider-a/model-x"\n',
        encoding="utf-8",
    )
    result = run(project)
    assert result.returncode == 1
    assert "reviewer-spec" in result.stderr
    assert "model" in result.stderr


def test_broken_toml_fails(project: Path) -> None:
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text("[agents.critic\nmodel = \n", encoding="utf-8")
    result = run(project)
    assert result.returncode == 1
    assert result.stderr.strip()


@pytest.mark.parametrize(
    ("body", "named", "needle"),
    [
        ('[agents.critic]\nmodel = 5\n', "critic", "'model' must be a non-empty string"),
        ('[agents.critic]\nmodel = true\n', "critic", "'model' must be a non-empty string"),
        ('[agents.critic]\nmodel = ""\n', "critic", "'model' must be a non-empty string"),
        ('[agents.critic]\nmodel = "  "\n', "critic", "'model' must be a non-empty string"),
        ('[agents.critic]\nmodel = "a\\nb"\n', "critic", "control characters"),
        ('[agents."../evil"]\nmodel = "m"\n', "../evil", "invalid role name"),
        ('[agents.".."]\nmodel = "m"\n', "..", "invalid role name"),
        ('agents.critic = "m"\n', "critic", "must be a table"),
    ],
)
def test_invalid_config_fails_with_named_error(
    project: Path, body: str, named: str, needle: str
) -> None:
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(body, encoding="utf-8")
    result = run(project)
    assert result.returncode == 1
    assert named in result.stderr
    assert needle in result.stderr
    assert not (project / ".zcode").exists()


def test_zcode_as_regular_file_fails_without_traceback(project: Path) -> None:
    write_config(project, {"critic": "provider-a/model-x"})
    (project / ".zcode").write_text("not a directory", encoding="utf-8")
    result = run(project)
    assert result.returncode == 1
    assert "cannot write" in result.stderr
    assert "Traceback" not in result.stderr


def test_model_with_special_characters_roundtrips(project: Path) -> None:
    # TOML literal string keeps the quote and the backslash in the value
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(
        '[agents.critic]\nmodel = \'a"b\\c\'\n', encoding="utf-8"
    )
    assert run(project).returncode == 0
    text = definitions(project)["critic.md"]
    assert 'model: "a\\"b\\\\c"' in text  # YAML-escaped exactly so
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert "critic: ok" in result.stdout


def test_foreign_file_with_a_role_name_is_refused_not_overwritten(
    project: Path,
) -> None:
    """spec: docs/plans/review-config.md#готово — определения производные
    от конфига; генератор не затирает чужой файл, совпавший с ролью по имени
    (зацепка P3-3 тикета 01, закрыта по команде оператора)."""
    write_config(
        project,
        {"critic": "provider-a/model-x", "reviewer-spec": "provider-a/model-x"},
    )
    agents = project / ".zcode" / "agents"
    agents.mkdir(parents=True)
    (agents / "critic.md").write_text("рукописная заметка про критика\n", encoding="utf-8")
    result = run(project)
    assert result.returncode == 1
    assert "critic.md" in result.stderr
    assert "refusing" in result.stderr
    # Preflight: a conflict blocks the whole run, nothing is written
    assert (agents / "critic.md").read_text(encoding="utf-8") == "рукописная заметка про критика\n"
    assert not (agents / "reviewer-spec.md").exists()


def test_handcrafted_file_with_the_marker_is_regenerated(project: Path) -> None:
    # A drifted file carrying the generated marker is the generator's own
    # output: rewritten, not refused.
    write_config(project, {"critic": "provider-a/model-x"})
    target = project / ".zcode" / "agents"
    target.mkdir(parents=True)
    (target / "critic.md").write_text(
        '---\nmodel: "old/model"\n---\n\n# critic\n\n'
        "Определение производное, но текст разошёлся.\n",
        encoding="utf-8",
    )
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert frontmatter_model(definitions(project)["critic.md"]) == "provider-a/model-x"


def test_render_names_the_running_generator(project: Path) -> None:
    # The definition names the generator that actually ran: the absolute
    # path when run from outside the project, the bundle path inside it
    # (зацепка P3-1 тикета 02, закрыта по команде оператора).
    write_config(project, {"critic": "provider-a/model-x"})
    assert run(project).returncode == 0
    assert str(GEN.resolve()) in definitions(project)["critic.md"]

    installed = project / ".agents" / "skills" / "init"
    installed.mkdir(parents=True)
    shutil.copyfile(GEN, installed / "gen_agents.py")
    result = subprocess.run(
        ["python3", str(installed / "gen_agents.py"), str(project)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    assert ".agents/skills/init/gen_agents.py" in definitions(project)["critic.md"]


def test_refusal_guard_is_load_bearing(project: Path) -> None:
    # With the marker emptied the guard never fires and the foreign file
    # is silently clobbered — the exact behaviour the refusal test forbids.
    write_config(project, {"critic": "provider-a/model-x"})
    agents = project / ".zcode" / "agents"
    agents.mkdir(parents=True)
    (agents / "critic.md").write_text("рукописный файл\n", encoding="utf-8")
    broken = project / "gen_broken.py"
    broken.write_text(
        GEN.read_text(encoding="utf-8").replace(
            'MARKER = "Определение производное"',
            'MARKER = ""',
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        ["python3", str(broken), str(project)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert (agents / "critic.md").read_text(encoding="utf-8") != "рукописный файл\n"


LEVEL_BODY = (
    '[agents.reviewer-spec]\nmodel = "provider-a/model-x"\nlevel = "max"\n'
    '[agents.critic]\nmodel = "provider-a/model-x"\n'
)


def test_level_yields_thoughtlevel_and_absence_omits_it(project: Path) -> None:
    """spec: docs/plans/onto-doc.md#готово — gen_agents выучивает `level`
    и пишет `thoughtLevel` в определение; роль без ключа остаётся без строки
    (решение 6)."""
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(LEVEL_BODY, encoding="utf-8")
    result = run(project)
    assert result.returncode == 0, result.stderr
    files = definitions(project)
    assert "thoughtLevel: max" in files["reviewer-spec.md"]
    assert "level" not in result.stderr  # the known key no longer warns
    assert "thoughtLevel" not in files["critic.md"]


def test_unknown_level_value_passes_through(project: Path) -> None:
    """spec: docs/plans/onto-doc.md#готово — незнакомое значение `level`
    проходит до сверки при запуске роли (решение 4)."""
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(
        '[agents.critic]\nmodel = "provider-a/model-x"\nlevel = "banana"\n',
        encoding="utf-8",
    )
    result = run(project)
    assert result.returncode == 0, result.stderr
    assert "thoughtLevel: banana" in definitions(project)["critic.md"]


@pytest.mark.parametrize(
    ("body", "needle"),
    [
        ('[agents.critic]\nmodel = "m"\nlevel = ""\n', "must be a non-empty string"),
        ('[agents.critic]\nmodel = "m"\nlevel = "  "\n', "must be a non-empty string"),
        ('[agents.critic]\nmodel = "m"\nlevel = 5\n', "must be a non-empty string"),
        ('[agents.critic]\nmodel = "m"\nlevel = true\n', "must be a non-empty string"),
    ],
)
def test_invalid_level_fails_with_named_error(
    project: Path, body: str, needle: str
) -> None:
    """spec: docs/plans/onto-doc.md#готово — пустая строка `level` —
    именованный отказ; невалидное значение не проходит молча."""
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(body, encoding="utf-8")
    result = run(project)
    assert result.returncode == 1
    assert "level" in result.stderr
    assert needle in result.stderr
    assert not (project / ".zcode").exists()


def test_thoughtlevel_render_is_load_bearing(project: Path) -> None:
    # With the thoughtLevel line dropped from the renderer the definition
    # carries no level — the exact loss test_level_yields_thoughtlevel_...
    # forbids.
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(LEVEL_BODY, encoding="utf-8")
    broken = project / "gen_broken.py"
    broken.write_text(
        GEN.read_text(encoding="utf-8").replace(
            "level_line = f'thoughtLevel: {level}\\n' if level else \"\"",
            'level_line = ""',
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        ["python3", str(broken), str(project)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0
    assert "thoughtLevel" not in definitions(project)["reviewer-spec.md"]


def test_empty_level_guard_is_load_bearing(project: Path) -> None:
    # With the level check muted the empty value is accepted silently —
    # the exact behaviour test_invalid_level_fails_with_named_error forbids.
    (project / ".agents").mkdir(parents=True)
    (project / ".agents" / "config.toml").write_text(
        '[agents.critic]\nmodel = "m"\nlevel = ""\n', encoding="utf-8"
    )
    broken = project / "gen_broken.py"
    broken.write_text(
        GEN.read_text(encoding="utf-8").replace(
            "if level is not None and (not isinstance(level, str) or not level.strip()):",
            "if False:",
        ),
        encoding="utf-8",
    )
    result = subprocess.run(
        ["python3", str(broken), str(project)],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0


def test_repo_gitignores_agent_definitions() -> None:
    gitignore = (REPO / ".gitignore").read_text(encoding="utf-8")
    assert ".zcode/agents/" in gitignore
    probe = subprocess.run(
        ["git", "-C", str(REPO), "check-ignore", "-q", ".zcode/agents/probe.md"],
        capture_output=True,
        text=True,
        check=False,
    )
    assert probe.returncode == 0, ".zcode/agents/probe.md is not ignored"
