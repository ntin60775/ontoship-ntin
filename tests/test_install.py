"""Contract for the project-local install channel.

The installer is the only thing that puts the core into a project's universal skill
root, so these checks pin its observable effects: the `.agents/skills` layout, idempotence,
drift and legacy reporting, and the refusal to write or destroy anything outside its
destination.

spec: docs/plans/workflow-skills.md#готово — seven skills in <project>/.agents/skills;
      link/copy; idempotent; --check names each missing or drifted skill
invariant: docs/plans/harness-agnostic.md#готово — writes only <project>/.agents/skills; --check is read-only and deletes nothing
"""
from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
INSTALL = REPO / "scripts" / "install.sh"
SKILLS = ("kb-search", "kb-curate", "init", "grilling", "to-tickets", "ship", "testing")


def run(project: Path, *flags: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [str(INSTALL), *flags, str(project)],
        capture_output=True,
        text=True,
        check=False,
    )


def output(result: subprocess.CompletedProcess[str]) -> str:
    return result.stdout + result.stderr


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


def test_fresh_install_links_seven_skills_and_writes_nothing_else(
    project: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch,
) -> None:
    """spec: docs/plans/workflow-skills.md#готово — seven links under .agents/skills."""
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
    """spec: docs/plans/workflow-skills.md#готово — `--check` exits 0 when all seven links point at this repo."""
    install = run(project)
    assert install.returncode == 0, output(install)
    before = tree(project)

    result = run(project, "--check")
    assert result.returncode == 0, output(result)
    assert "check: ok" in result.stdout
    for name in SKILLS:
        assert f"ok {name}" in result.stdout
    assert tree(project) == before, "--check must not write"


def test_check_on_a_fresh_project_names_all_seven_without_writing(tmp_path: Path) -> None:
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
    """spec: docs/plans/workflow-skills.md#готово — `--copy` produces seven real directories, not links."""
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


def test_dry_run_rejects_check_and_copy(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — --check conflicts; --copy is ticket 02."""
    project = tmp_path / "fresh"
    project.mkdir()
    before = tree(project)

    with_check = run(project, "--dry-run", "--check")
    assert with_check.returncode == 2
    assert "mutually exclusive" in output(with_check)

    with_copy = run(project, "--dry-run", "--copy")
    assert with_copy.returncode == 2
    assert "not implemented" in output(with_copy)

    assert tree(project) == before


def test_usage_names_dry_run(tmp_path: Path) -> None:
    """spec: docs/plans/install-dry-run.md#готово — usage and the script header name the mode."""
    result = run(tmp_path, "--help")
    assert result.returncode == 0, output(result)
    assert "--dry-run" in result.stdout

    header = INSTALL.read_text(encoding="utf-8").splitlines()[:12]
    assert any("--dry-run" in line for line in header), "the script header must document --dry-run"