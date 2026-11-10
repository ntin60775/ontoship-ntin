"""Contract for the project-local install channel.

The installer is the only thing that puts the core into a project's universal skill
root, so these checks pin its observable effects: the `.agents/skills` layout, idempotence,
drift and legacy reporting, and the refusal to write or destroy anything outside its
destination.

spec: docs/plans/workflow-skills.md#готово — skills in <project>/.agents/skills;
      link/copy; idempotent; --check names each missing or drifted skill
spec: docs/plans/onto-doc.md#готово — the install channel carries the
      onto-doc bundle: it joins the rest
spec: docs/plans/review-loose-ends.md#готово — the installer array is the
      machine source: the bundle index, the usage listing, this file's tuple
      and the AGENTS.md layout row agree with it, both ways; harnesses.md
      carries no count before «скилл»/«бандл»
spec: docs/plans/canon-section-in-bundles.md#готово — link и copy ставят
      method-phases.md, ссылки скиллов на секции резолвятся в дереве
      установки
invariant: docs/plans/harness-agnostic.md#готово — writes only <project>/.agents/skills; --check is read-only and deletes nothing
"""
from __future__ import annotations

import hashlib
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "scripts" / "install.sh"
SKILLS = ("kb-search", "kb-curate", "init", "grilling", "to-tickets", "ship", "testing", "critic", "onto-doc")

# Method-section files shipped inside the bundles (bundle-references 01);
# listed from disk, so a new references/ file joins this check by itself.
REFERENCES = sorted(
    (path.parent.parent.name, f"references/{path.name}")
    for path in REPO.glob("skills/*/references/*.md")
)


def run(project: Path, *flags: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(INSTALL), *flags, str(project)],
        capture_output=True,
        text=True,
        check=False,
    )


def output(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


# A digit or a Russian numeral — nominative plus the oblique case forms that
# precede a counted noun — right before «скилл»/«бандл»: a stale count snapshot.
# The left lookbehind keeps a numeral hidden inside a word («смотри скиллы»)
# from firing. Declared blind spots: instrumental forms («девятью»), compound
# numerals («двадцать один»), a count after the noun and a count separated
# from the noun by another word.
COUNTED_NOUN = re.compile(
    r"(?<![а-яёa-z\d])"
    r"(?:\d+"
    r"|один|одна|одно|одни"
    r"|дв[ае]|двух|двумя"
    r"|три|тр[её]х|тремя"
    r"|четыре|четыр[её]х"
    r"|пять|пяти"
    r"|шесть|шести"
    r"|семь|семи"
    r"|восемь|восьми"
    r"|девять|девяти"
    r"|десять|десяти)"
    r"\s+(?:скилл|бандл)",
    re.IGNORECASE,
)


def _usage_listing(source: str) -> list[str]:
    """Bundle names as the usage heredoc lists them under the (default) row.

    The listing is the indented name rows after the "(default)" row; a row that
    starts an option description ends it. Name-shaped tokens only, so a
    reworded header row with the same listing stays green.
    """
    if "cat <<'EOF'" not in source:
        return []
    usage = source.split("cat <<'EOF'\n", 1)[1].split("\nEOF", 1)[0]
    names: list[str] = []
    in_listing = False
    for line in usage.splitlines():
        if not in_listing:
            if "(default)" in line:
                in_listing = True
            continue
        stripped = line.strip()
        if not stripped or stripped.startswith("--") or not line.startswith("  "):
            break
        names.extend(part for part in (piece.strip() for piece in stripped.split(","))
                     if re.fullmatch(r"[a-z0-9][a-z0-9-]*", part))
    return names


def _parity_errors(root: Path) -> list[str]:
    """Every violated bundle-parity rule; empty means the carriers agree.

    The installer array is the machine source; the parsed variable is not
    named SKILLS — that name is taken by this module's tuple, itself a carrier
    under check.
    """
    errors: list[str] = []
    install = root / "scripts" / "install.sh"
    if not install.is_file():
        return ["parity: scripts/install.sh is missing"]
    source = install.read_text("utf-8")
    match = re.search(r"^readonly SKILLS=\(([^)]*)\)", source, re.MULTILINE)
    if not match:
        return ["parity: install.sh carries no readonly SKILLS array"]
    bundles = match.group(1).split()

    index = root / "skills" / "README.md"
    listed: list[str] = []
    if not index.is_file():
        errors.append("parity: skills/README.md is missing")
    else:
        listed = re.findall(r"^- \[([a-z0-9-]+)/\]\(",
                            index.read_text("utf-8"), re.MULTILINE)
    for name in bundles:
        if name not in listed:
            errors.append(f"parity: skills/README.md misses the {name} bundle")
    for name in listed:
        if name not in bundles:
            errors.append(f"parity: skills/README.md lists a phantom {name} bundle")
    if sorted(listed) != sorted(bundles):
        errors.append("parity: skills/README.md is not a permutation of the "
                      "installer array (duplicate row?)")

    names = _usage_listing(source)
    if names != bundles:
        errors.append(f"parity: the usage listing {names} drifts from "
                      f"the installer array {bundles}")

    own_source = root / "tests" / "test_install.py"
    if not own_source.is_file():
        errors.append("parity: tests/test_install.py is missing")
    else:
        declared_match = re.search(r"^SKILLS = \(([^)]*)\)",
                                   own_source.read_text("utf-8"), re.MULTILINE)
        if not declared_match:
            errors.append("parity: tests/test_install.py carries no SKILLS tuple")
        else:
            declared = [part.strip().strip("\"'")
                        for part in declared_match.group(1).split(",")
                        if part.strip()]
            if declared != bundles:
                errors.append("parity: the test tuple drifts from the installer array")

    agents = root / "AGENTS.md"
    if not agents.is_file():
        errors.append("parity: AGENTS.md is missing")
    elif not re.search(r"^skills/\s+.*skills/README\.md",
                       agents.read_text("utf-8"), re.MULTILINE):
        errors.append("parity: the AGENTS.md layout row does not point at skills/README.md")
    return errors


def tree(root: Path) -> dict[str, tuple[str, int, int, str]]:
    """Every entry under root: kind, inode, mtime and content or link target.

    Inodes and mtimes make the comparison catch a rewritten-but-equal file or a
    replaced symlink, which a content-only diff would miss.
    """
    rows: dict[str, tuple[str, int, int, str]] = {}
    for dirpath, dirnames, filenames in os.walk(root, followlinks=False):
        base = Path(dirpath)
        for name in dirnames + filenames:
            path = base / name
            stat = path.lstat()
            if path.is_symlink():
                kind, extra = "link", os.readlink(path)
            elif path.is_dir():
                kind, extra = "dir", ""
            else:
                kind = "file"
                extra = hashlib.sha256(path.read_bytes()).hexdigest()
            rows[str(path.relative_to(root))] = (kind, stat.st_ino, stat.st_mtime_ns, extra)
    return rows


def assert_links(project: Path) -> None:
    dest = project / ".agents" / "skills"
    assert dest.is_dir() and not dest.is_symlink()
    for name in SKILLS:
        path = dest / name
        assert path.is_symlink(), f"{name} is not a symlink"
        assert path.resolve() == (REPO / "skills" / name).resolve()
        assert (path / "SKILL.md").is_file()


def assert_no_derived_files(directory: Path) -> None:
    assert not list(directory.rglob("__pycache__"))
    assert not list(directory.rglob("*.pyc"))


@pytest.fixture
def project(tmp_path: Path) -> Path:
    root = tmp_path / "project"
    root.mkdir()
    (root / "AGENTS.md").write_text("# project\n", encoding="utf-8")
    (root / ".gitignore").write_text(".scratch/\n", encoding="utf-8")
    (root / "docs").mkdir()
    (root / "docs" / "README.md").write_text("# docs\n", encoding="utf-8")
    return root


def test_installer_is_executable() -> None:
    """spec: docs/plans/harness-agnostic.md#готово — `scripts/install.sh <project>` is the install channel."""
    assert INSTALL.is_file()
    assert os.access(INSTALL, os.X_OK), "install.sh must be executable"


def test_bundle_carriers_stay_in_parity_with_the_installer() -> None:
    """spec: docs/plans/review-loose-ends.md#готово — the installer array is the
    machine source; the index, the usage listing, this file's tuple and the
    AGENTS.md layout row agree with it, both ways: no missing, no phantom."""
    assert _parity_errors(REPO) == []


def test_parity_can_fail(tmp_path: Path) -> None:
    """invariant: docs/plans/review-loose-ends.md#готово — the parity check
    catches a dropped index row, a phantom bundle, a cut layout link and a
    deleted index (mutation probes)."""
    assert _parity_errors(REPO) == []

    install_source = INSTALL.read_text("utf-8")
    index_source = (REPO / "skills" / "README.md").read_text("utf-8")
    agents_source = (REPO / "AGENTS.md").read_text("utf-8")
    own_source = Path(__file__).read_text("utf-8")

    def carriers(readme: str | None, agents: str = agents_source) -> Path:
        root = tmp_path / "carriers"
        shutil.rmtree(root, ignore_errors=True)
        (root / "scripts").mkdir(parents=True)
        (root / "skills").mkdir()
        (root / "tests").mkdir(parents=True)
        (root / "scripts" / "install.sh").write_text(install_source, "utf-8")
        if readme is not None:
            (root / "skills" / "README.md").write_text(readme, "utf-8")
        (root / "AGENTS.md").write_text(agents, "utf-8")
        (root / "tests" / "test_install.py").write_text(own_source, "utf-8")
        return root

    # A dropped index row: the kb-curate entry with its wrapped second line.
    kept: list[str] = []
    skipping = False
    for line in index_source.splitlines(keepends=True):
        if line.startswith("- ["):
            skipping = line.startswith("- [kb-curate/")
        if not skipping:
            kept.append(line)
    dropped_row = "".join(kept)
    assert dropped_row != index_source
    errors = _parity_errors(carriers(dropped_row))
    assert any("misses the kb-curate bundle" in error for error in errors), errors

    # A phantom bundle joins the index.
    phantom = index_source + "- [extra-skill/](extra-skill/SKILL.md) — фантом.\n"
    errors = _parity_errors(carriers(phantom))
    assert any("lists a phantom extra-skill bundle" in error for error in errors), errors

    # A duplicated index row keeps both names present yet is not equality
    # (panel probe: the old two-way membership check stayed green on it).
    ship_row = next(line for line in index_source.splitlines()
                    if line.startswith("- [ship/]"))
    duplicated = index_source.replace(ship_row, ship_row + "\n" + ship_row, 1)
    errors = _parity_errors(carriers(duplicated))
    assert any("not a permutation" in error for error in errors), errors

    # The AGENTS.md layout row loses the pointer to the index.
    cut_link = agents_source.replace("индекс — skills/README.md", "индекс")
    assert cut_link != agents_source
    errors = _parity_errors(carriers(index_source, cut_link))
    assert any("does not point at skills/README.md" in error for error in errors), errors

    # The index is gone.
    errors = _parity_errors(carriers(None))
    assert any("skills/README.md is missing" in error for error in errors), errors

def test_harnesses_carries_no_bundle_count() -> None:
    """spec: docs/plans/review-loose-ends.md#готово — harnesses.md and
    skills/README.md name no count before «скилл»/«бандл» (the second file
    added with the marketplace-plugin channel, panel mp-01)."""
    for rel in ("docs/reference/harnesses.md", "skills/README.md"):
        text = (REPO / rel).read_text("utf-8")
        match = COUNTED_NOUN.search(text)
        assert match is None, \
            f"{rel}: a count snapshot before a counted noun: {match.group(0)!r}"
    text = (REPO / "docs" / "reference" / "harnesses.md").read_text("utf-8")
    # «Готово» 3: the enumeration is replaced by a pointer, so the pointer must be there.
    assert "skills/README.md" in text, "harnesses.md must point at the skills index"
    # The guard catches oblique-case counts too (panel probe: «восьми бандлов»).
    probe = text.replace("состав называет индекс", "состав из девяти скиллов называет")
    assert COUNTED_NOUN.search(probe) is not None, "oblique-case counts must redden"
    # A numeral hidden inside a word must not fire (probe of the left lookbehind).
    assert COUNTED_NOUN.search("смотри скиллы и внутри бандла") is None


def test_onto_doc_joins_the_install_channel(project: Path) -> None:
    """spec: docs/plans/onto-doc.md#готово — onto-doc joins the install
    channel; all three carriers name it: the installer list, the usage line
    and the link/check output."""
    source = INSTALL.read_text("utf-8")
    assert re.search(r"readonly SKILLS=.*\bonto-doc\b", source), \
        "install.sh must list the onto-doc bundle"
    usage = run(project, "--help")
    assert usage.returncode == 0, output(usage)
    assert "onto-doc" in usage.stdout, "the usage line must name onto-doc"

    install = run(project)
    assert install.returncode == 0, output(install)
    assert any(f"onto-doc -> " in line or f"unchanged onto-doc" in line
               for line in install.stdout.splitlines())
    check = run(project, "--check")
    assert check.returncode == 0, output(check)
    assert "ok onto-doc (link)" in check.stdout


def test_fresh_install_links_every_bundle_and_writes_nothing_else(
    project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """spec: docs/plans/onto-doc.md#готово — every bundle linked under .agents/skills."""
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    before = tree(project)
    result = run(project)
    assert result.returncode == 0, output(result)
    assert_links(project)

    after = tree(project)
    added = set(after) - set(before)
    assert added, "the install created nothing"
    assert all(path == ".agents" or path.startswith(".agents/") for path in added), added
    for path, state in before.items():
        assert after[path] == state, f"install touched pre-existing {path}"

    for legacy in (".dsh", ".zcode", ".qoder"):
        assert not (project / legacy).exists(), f"install wrote into {legacy}"
    assert not list(home.iterdir()), "install wrote into $HOME (no global install)"
    for name in SKILLS:
        assert name in result.stdout


def test_second_install_is_idempotent(project: Path) -> None:
    """spec: docs/plans/workflow-skills.md#готово — a second run makes no change."""
    first = run(project)
    assert first.returncode == 0, output(first)
    before = tree(project)

    second = run(project)
    assert second.returncode == 0, output(second)
    assert tree(project) == before
    assert all(f"unchanged {name}" in second.stdout for name in SKILLS)


def test_check_is_clean_and_read_only(project: Path) -> None:
    """spec: docs/plans/workflow-skills.md#готово — `--check` exits 0 when every link points at this repo."""
    install = run(project)
    assert install.returncode == 0, output(install)
    before = tree(project)

    result = run(project, "--check")
    assert result.returncode == 0, output(result)
    assert "check: ok" in result.stdout
    for name in SKILLS:
        assert f"ok {name}" in result.stdout
    assert tree(project) == before, "--check must not write"


def test_check_on_a_fresh_project_names_every_missing_skill_without_writing(tmp_path: Path) -> None:
    """spec: docs/plans/workflow-skills.md#готово — every missing skill is named; the check still writes nothing."""
    fresh = tmp_path / "fresh"
    fresh.mkdir()
    result = run(fresh, "--check")
    assert result.returncode == 1
    for name in SKILLS:
        assert f"drift: {name}:" in output(result)
    assert not (fresh / ".agents").exists()


def test_check_names_each_missing_or_wrong_link(project: Path) -> None:
    """spec: docs/plans/workflow-skills.md#готово — a missing or wrong link is named with exit 1 (mutation probe)."""
    install = run(project)
    assert install.returncode == 0, output(install)
    dest = project / ".agents" / "skills"

    (dest / "kb-curate").unlink()
    missing = run(project, "--check")
    assert missing.returncode == 1
    assert any(line.startswith("drift: kb-curate:") for line in output(missing).splitlines())
    assert any(line.startswith("ok kb-search") for line in output(missing).splitlines())

    relink = run(project)
    assert relink.returncode == 0, output(relink)
    (dest / "ship").unlink()
    missing_workflow = run(project, "--check")
    assert missing_workflow.returncode == 1
    assert any(line.startswith("drift: ship:")
               for line in output(missing_workflow).splitlines())
    assert any(line.startswith("ok testing")
               for line in output(missing_workflow).splitlines())

    relink = run(project)
    assert relink.returncode == 0, output(relink)
    (dest / "init").unlink()
    os.symlink(REPO / "skills" / "kb-search", dest / "init")
    wrong = run(project, "--check")
    assert wrong.returncode == 1
    drift = [line for line in output(wrong).splitlines() if line.startswith("drift: init:")]
    assert drift, "a wrong symlink must be named"
    assert "wrong symlink" in drift[0]


def test_check_warns_about_legacy_entries_without_deleting_them(project: Path) -> None:
    """spec: docs/plans/harness-agnostic.md#готово — legacy .dsh/.zcode/.qoder links warn, never fail."""
    install = run(project)
    assert install.returncode == 0, output(install)

    dsh = project / ".dsh" / "skills"
    dsh.mkdir(parents=True)
    os.symlink(REPO / "skills" / "kb-search", dsh / "kb-search")
    (project / ".zcode").mkdir()
    os.symlink(REPO / "skills", project / ".zcode" / "skills")
    qoder = project / ".qoder" / "skills"
    qoder.mkdir(parents=True)
    os.symlink(REPO / "skills" / "init", qoder / "init")

    before = tree(project)
    result = run(project, "--check")
    assert result.returncode == 0, output(result)
    assert "check: ok" in result.stdout
    text = output(result)
    assert "warning: legacy .dsh/skills/kb-search" in text
    assert "(100)" in text and "(200)" in text and "shadows" in text
    assert "warning: legacy .zcode/skills ->" in text
    assert "warning: legacy .qoder/skills/init" in text
    assert tree(project) == before, "--check must not touch a legacy entry"


def test_install_does_not_touch_a_legacy_entry(project: Path) -> None:
    """invariant: docs/plans/harness-agnostic.md#готово — the installer writes only .agents/skills and deletes no legacy link."""
    dsh = project / ".dsh" / "skills"
    dsh.mkdir(parents=True)
    legacy = dsh / "kb-search"
    os.symlink(REPO / "skills" / "kb-search", legacy)
    before = tree(project)

    result = run(project)
    assert result.returncode == 0, output(result)
    assert_links(project)
    after = tree(project)
    for path, state in before.items():
        assert after[path] == state, f"install touched legacy {path}"
    assert legacy.is_symlink() and legacy.resolve() == (REPO / "skills" / "kb-search").resolve()


def test_copy_install_is_detached(tmp_path: Path) -> None:
    """spec: docs/plans/workflow-skills.md#готово — `--copy` produces real directories, not links."""
    project = tmp_path / "copied"
    project.mkdir()
    result = run(project, "--copy")
    assert result.returncode == 0, output(result)

    dest = project / ".agents" / "skills"
    for name in SKILLS:
        path = dest / name
        assert path.is_dir() and not path.is_symlink(), f"{name} is not a real directory"
        assert (path / "SKILL.md").is_file()
    assert (dest / "kb-search" / "gitmark.py").is_file()
    assert_no_derived_files(dest)

    check = run(project, "--check")
    assert check.returncode == 0, output(check)
    for name in SKILLS:
        assert f"ok {name} (copy)" in check.stdout


def test_second_copy_run_is_idempotent_and_detects_drift(tmp_path: Path) -> None:
    """spec: docs/plans/workflow-skills.md#готово — copies are checked by content; a changed or missing copy drifts."""
    project = tmp_path / "copied"
    project.mkdir()
    first = run(project, "--copy")
    assert first.returncode == 0, output(first)
    before = tree(project)

    second = run(project, "--copy")
    assert second.returncode == 0, output(second)
    assert tree(project) == before
    assert all(f"unchanged {name}" in second.stdout for name in SKILLS)

    # Mutation probe: a byte of drift inside a copy must be reported, with its name.
    (project / ".agents" / "skills" / "kb-curate" / "SKILL.md").write_text(
        "edited\n", encoding="utf-8")
    drifted = run(project, "--check")
    assert drifted.returncode == 1
    assert any(line.startswith("drift: kb-curate:")
               for line in output(drifted).splitlines())

    shutil.rmtree(project / ".agents" / "skills" / "init")
    missing = run(project, "--check")
    assert missing.returncode == 1
    assert any(line.startswith("drift: init:") for line in output(missing).splitlines())


def test_copy_install_refuses_to_overwrite_a_drifted_copy(tmp_path: Path) -> None:
    """invariant: docs/plans/harness-agnostic.md#готово — a drifted copy is never overwritten and no half install happens."""
    project = tmp_path / "copied"
    project.mkdir()
    first = run(project, "--copy")
    assert first.returncode == 0, output(first)

    drifted = project / ".agents" / "skills" / "ship" / "SKILL.md"
    drifted.write_text("edited\n", encoding="utf-8")
    before = tree(project)

    second = run(project, "--copy")
    assert second.returncode != 0
    assert "copy differs" in output(second)
    assert drifted.read_text("utf-8") == "edited\n"
    assert tree(project) == before, "--copy must not overwrite or half-install"


def test_install_refuses_to_clobber_a_real_directory(project: Path) -> None:
    """invariant: docs/plans/harness-agnostic.md#готово — a detached copy is never replaced by a link, and no half install happens."""
    occupied = project / ".agents" / "skills" / "kb-search"
    occupied.mkdir(parents=True)
    sentinel = occupied / "SKILL.md"
    sentinel.write_text("detached\n", encoding="utf-8")

    result = run(project)
    assert result.returncode != 0
    assert "refusing to replace" in output(result)
    assert sentinel.read_text("utf-8") == "detached\n"
    assert not (project / ".agents" / "skills" / "kb-curate").exists()
    assert not (project / ".agents" / "skills" / "init").exists()


def test_dry_run_plans_a_link_install_without_writing(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — --dry-run prints the link plan and writes nothing."""
    project = tmp_path / "fresh"
    project.mkdir()
    before = tree(project)

    result = run(project, "--dry-run")
    assert result.returncode == 0, output(result)

    dest = project / ".agents" / "skills"
    assert f"would create {dest}" in result.stdout
    for name in SKILLS:
        assert f"would link {name} -> {REPO / 'skills' / name}" in result.stdout
    plan = [line for line in result.stdout.splitlines() if line.startswith("would link ")]
    assert len(plan) == len(SKILLS), plan
    assert not (project / ".agents").exists(), "--dry-run must not create the install root"
    assert tree(project) == before


def test_dry_run_reports_a_complete_link_install_as_unchanged(project: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — an existing install is planned as unchanged, tree untouched."""
    install = run(project)
    assert install.returncode == 0, output(install)
    before = tree(project)

    result = run(project, "--dry-run")
    assert result.returncode == 0, output(result)
    for name in SKILLS:
        assert f"would leave {name} unchanged" in result.stdout
    plan = [line for line in result.stdout.splitlines() if line.startswith("would leave ")]
    assert len(plan) == len(SKILLS), plan
    assert "would create" not in result.stdout
    assert "would link" not in result.stdout
    assert tree(project) == before


def test_dry_run_runs_preflight_and_refuses_like_a_real_install(project: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — the plan refuses a path a real install would refuse."""
    occupied = project / ".agents" / "skills" / "kb-search"
    occupied.mkdir(parents=True)
    sentinel = occupied / "SKILL.md"
    sentinel.write_text("detached\n", encoding="utf-8")
    before = tree(project)

    result = run(project, "--dry-run")
    assert result.returncode == 1
    assert "refusing to replace" in output(result)
    assert sentinel.read_text("utf-8") == "detached\n"
    assert not (project / ".agents" / "skills" / "kb-curate").exists()
    assert tree(project) == before


def test_dry_run_refuses_a_blocked_install_root(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — a blocked root is refused, never planned as writable."""
    project = tmp_path / "blocked-root"
    project.mkdir()
    (project / ".agents").mkdir()
    (project / ".agents" / "skills").write_text("not a directory\n", encoding="utf-8")
    before = tree(project)

    result = run(project, "--dry-run")
    assert result.returncode == 1
    assert "refusing to replace a non-directory" in output(result)
    assert "would link" not in result.stdout, "a refused install must not print a plan"
    assert tree(project) == before

    parent_blocked = tmp_path / "blocked-parent"
    parent_blocked.mkdir()
    (parent_blocked / ".agents").write_text("not a directory\n", encoding="utf-8")
    parent_before = tree(parent_blocked)

    result = run(parent_blocked, "--dry-run")
    assert result.returncode == 1
    assert "refusing to replace a non-directory" in output(result)
    assert tree(parent_blocked) == parent_before


def test_dry_run_rejects_check(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — --check conflicts with --dry-run."""
    project = tmp_path / "fresh"
    project.mkdir()
    before = tree(project)

    with_check = run(project, "--dry-run", "--check")
    assert with_check.returncode == 2
    assert "mutually exclusive" in output(with_check)

    assert tree(project) == before


def test_dry_run_plans_a_copy_install_without_writing(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — --dry-run --copy prints the copy plan and writes nothing."""
    project = tmp_path / "fresh"
    project.mkdir()
    before = tree(project)

    result = run(project, "--dry-run", "--copy")
    assert result.returncode == 0, output(result)

    dest = project / ".agents" / "skills"
    assert f"would create {dest}" in result.stdout
    for name in SKILLS:
        assert f"would copy {name} -> {dest / name}" in result.stdout
    plan = [line for line in result.stdout.splitlines() if line.startswith("would copy ")]
    assert len(plan) == len(SKILLS), plan
    assert not (project / ".agents").exists(), "--dry-run must not create the install root"
    assert tree(project) == before


def test_dry_run_reports_a_complete_copy_install_as_unchanged(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — an existing detached copy is planned as unchanged, tree untouched."""
    project = tmp_path / "copied"
    project.mkdir()
    install = run(project, "--copy")
    assert install.returncode == 0, output(install)
    before = tree(project)

    result = run(project, "--dry-run", "--copy")
    assert result.returncode == 0, output(result)
    for name in SKILLS:
        assert f"would leave {name} unchanged" in result.stdout
    plan = [line for line in result.stdout.splitlines() if line.startswith("would leave ")]
    assert len(plan) == len(SKILLS), plan
    assert "would create" not in result.stdout
    assert "would copy" not in result.stdout
    assert tree(project) == before


def test_dry_run_copy_refuses_a_drifted_copy_like_a_real_install(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — a drifted copy gets copy differs, exit 1, no write."""
    project = tmp_path / "copied"
    project.mkdir()
    install = run(project, "--copy")
    assert install.returncode == 0, output(install)
    drifted = project / ".agents" / "skills" / "ship" / "SKILL.md"
    drifted.write_text("edited\n", encoding="utf-8")
    before = tree(project)

    result = run(project, "--dry-run", "--copy")
    assert result.returncode == 1
    assert "copy differs" in output(result)
    assert drifted.read_text("utf-8") == "edited\n"
    assert tree(project) == before


def test_usage_names_dry_run(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — usage and the script header name the mode."""
    result = run(tmp_path, "--help")
    assert result.returncode == 0, output(result)
    assert "--dry-run" in result.stdout

    header = INSTALL.read_text(encoding="utf-8").splitlines()[:12]
    assert any("--dry-run" in line for line in header), "the script header must document --dry-run"


def test_install_carries_bundle_references(tmp_path: Path) -> None:
    """spec: docs/plans/bundle-references.md#готово — both install forms
    deliver the bundles' references/: links resolve into the repo bundles,
    a detached copy carries the files, and --check names a copy that lost
    one (spec «Готово» 4; the runner channel is proved by ticket 03)."""
    linked = tmp_path / "linked"
    linked.mkdir()
    install = run(linked)
    assert install.returncode == 0, output(install)
    for name, ref in REFERENCES:
        assert (linked / ".agents" / "skills" / name / ref).is_file(), \
            f"{name}/{ref} missing after link install"

    copied = tmp_path / "copied"
    copied.mkdir()
    copy = run(copied, "--copy")
    assert copy.returncode == 0, output(copy)
    for name, ref in REFERENCES:
        assert (copied / ".agents" / "skills" / name / ref).is_file(), \
            f"{name}/{ref} missing after copy install"

    # Mutation probe: references/ lost from a copy drifts --check by name.
    # The green --check before the mutation pins the drift on this file.
    before = run(copied, "--check")
    assert before.returncode == 0, output(before)
    (copied / ".agents" / "skills" / "ship" / "references"
     / "review-panel.md").unlink()
    drifted = run(copied, "--check")
    assert drifted.returncode == 1
    assert any(line.startswith("drift: ship:")
               for line in output(drifted).splitlines())


# Method-section references inside shipped skill bodies: a bundle-relative
# path to method-phases.md or quality-rule.md must resolve inside the
# installed tree (canon-section-in-bundles 01).
SECTION_REF = re.compile(
    r"((?:\.\./[a-z0-9-]+/)?references/(?:method-phases|quality-rule)\.md)")


def _section_refs_resolve(project: Path) -> list[str]:
    errors: list[str] = []
    dest = project / ".agents" / "skills"
    for name in SKILLS:
        text = (dest / name / "SKILL.md").read_text("utf-8")
        for ref in SECTION_REF.findall(text):
            if not (dest / name / ref).is_file():
                errors.append(f"{name}: {ref} does not resolve after install")
    return errors


def test_method_section_references_resolve_after_install(tmp_path: Path) -> None:
    """spec: docs/plans/canon-section-in-bundles.md#готово — link и copy
    ставят method-phases.md; каждая ссылка скилла на секцию (и на
    quality-rule.md) резолвится в дереве установки."""
    linked = tmp_path / "linked"
    linked.mkdir()
    install = run(linked)
    assert install.returncode == 0, output(install)
    assert (linked / ".agents" / "skills" / "ship" / "references"
            / "method-phases.md").is_file()
    assert _section_refs_resolve(linked) == []

    copied = tmp_path / "copied"
    copied.mkdir()
    copy = run(copied, "--copy")
    assert copy.returncode == 0, output(copy)
    assert (copied / ".agents" / "skills" / "ship" / "references"
            / "method-phases.md").is_file()
    assert _section_refs_resolve(copied) == []

    # Mutation probe: a dangling section reference in a copy reddens with
    # the skill's name. The wrong target still matches the section-reference
    # shape, so the failure is the missing file, not the regex.
    critic_body = (copied / ".agents" / "skills" / "critic" / "SKILL.md")
    critic_body.write_text(
        critic_body.read_text("utf-8")
        .replace("../ship/references/method-phases.md",
                 "../grilling/references/method-phases.md"), "utf-8")
    errors = _section_refs_resolve(copied)
    assert any(error.startswith("critic:") for error in errors), errors


def test_copy_install_carries_the_role_registry(tmp_path: Path) -> None:
    """spec: docs/plans/role-registry.md#готово-4 — the bundle is installed
    whole, so roles.py rides along into a detached copy install."""
    project = tmp_path / "copied"
    project.mkdir()
    result = run(project, "--copy")
    assert result.returncode == 0, output(result)

    registry = project / ".agents" / "skills" / "init" / "roles.py"
    assert registry.is_file(), "the init bundle must carry roles.py"