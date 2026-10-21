"""Lint path arguments: two guards against a silent empty selection.

The guards close one harm: a path that does not select a KB file skips the
per-file checks and looks like a clean full run ("✓ чисто", exit 0). Guard 1
refuses a missing path; guard 2 refuses a path that exists but matches no rel
(directory, "./"-prefix, absolute, gitignored, empty arg). The CLI reports the
refusal on stderr with exit 2 (usage class, distinct from exit 1 = ERR under
--strict) and replaces control characters in the message.

Traceability: each test carries ``spec: docs/plans/core-kb.md#готово-3`` or
``invariant: path selection cannot silently narrow to nothing``. The matrix has
a negative/mutation probe: bypassing ``_lint_path_guards`` must reproduce the
silent-clean harm, so the matrix is able to fail when the guard is removed.
"""
from __future__ import annotations

import subprocess
import sys
import unicodedata
from pathlib import Path

import pytest

from conftest import ENGINE


@pytest.fixture()
def kb(tmp_path: Path) -> Path:
    docs = tmp_path / "docs"
    (docs / "reference").mkdir(parents=True)
    (docs / "ops").mkdir()
    (docs / "notes").mkdir()
    (docs / "services").mkdir()
    (docs / "README.md").write_text(
        "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n", encoding="utf-8")
    (docs / "reference" / "README.md").write_text(
        "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n", encoding="utf-8")
    # aa — I2 (node_type outside the vocabulary): the single selected file
    (docs / "reference" / "aa.md").write_text(
        "---\nnode_type: bogus_type\ntitle: AA\n---\n\n# AA\n", encoding="utf-8")
    # bb — I2 + I6 (supersedes aa, which is not deprecated): outside the selection
    (docs / "reference" / "bb.md").write_text(
        "---\nnode_type: bogus_type\ntitle: BB\nlinks:\n  supersedes: [aa.md]\n---\n\n# BB\n",
        encoding="utf-8")
    # cc — a broken link (I4, global) and an orphan (I3, per-file): one file, both families
    (docs / "reference" / "cc.md").write_text(
        "---\nnode_type: reference\ntitle: CC\n---\n\n[битая](./nope.md)\n", encoding="utf-8")
    # dd — gitignored: on disk, but iter_md does not return it
    (docs / "reference" / "dd.md").write_text(
        "---\nnode_type: reference\ntitle: DD\n---\n\n# DD\n", encoding="utf-8")
    (tmp_path / ".gitignore").write_text(
        "docs/reference/dd.md\n**/*.tmp\n", encoding="utf-8")  # second rule unsupported: WARN is non-empty, pinning guard-before-WARN
    # xx — I1: load-bearing docs/ops/ without frontmatter (per-file)
    (docs / "ops" / "xx.md").write_text("# XX без frontmatter\n", encoding="utf-8")
    # notes/ without README — I5 (global) for both folders without an index
    (docs / "notes" / "n1.md").write_text("# N1\n", encoding="utf-8")
    # a card outside the schema value list — I9 (global), not selectable by the path
    (docs / "services" / "_schema.md").write_text(
        "---\nnode_type: schema\ncard_type: card\nrequired: [env]\n"
        "values: env: prod|stage\nlinks:\n  relates_to: [../README.md]\n---\n\n# Схема\n",
        encoding="utf-8")
    (docs / "services" / "cards.md").write_text(
        "---\nnode_type: card\ntitle: Карточка\nservice: demo\nstatus: active\n"
        "card_type: card\nenv: bogus_env\nlinks:\n  relates_to: [../README.md]\n---\n\n# Карточка\n",
        encoding="utf-8")
    return tmp_path


# ── refusal on a missing path (engine, guard 1) ─────────────────────────────


def test_nonexistent_path_named_refusal(kb: Path, gm):
    """invariant: path selection cannot silently narrow to nothing."""
    with pytest.raises(gm.LintPathError, match="docs/plans/nope\\.md") as ei:
        gm.cmd_lint(kb, ["docs/plans/nope.md"])
    assert str(ei.value).startswith("путь не найден: ")


def test_every_missing_path_is_named(kb: Path, gm):
    """invariant: guard 1 names every missing path, not only the first."""
    with pytest.raises(gm.LintPathError) as ei:
        gm.cmd_lint(kb, ["docs/aa-nope.md", "docs/bb-nope.md"])
    assert "docs/aa-nope.md" in str(ei.value) and "docs/bb-nope.md" in str(ei.value)


def test_refusal_class_is_not_catch_all_valueerror(gm):
    """invariant: only LintPathError is a usage refusal."""
    assert issubclass(gm.LintPathError, ValueError)
    assert gm.LintPathError is not ValueError


def test_cli_catches_only_lintpatherror_behaviorally(kb: Path, gm, monkeypatch, capsys):
    """invariant: a plain ValueError inside lint is an internal error, not exit 2."""
    def _boom(root, paths=None):
        raise ValueError("внутренняя проба: симуляция будущего бага в теле lint")

    monkeypatch.setattr(gm, "cmd_lint", _boom)
    with pytest.raises(ValueError, match="внутренняя проба"):
        gm.main(["--root", str(kb), "lint", "docs/reference/aa.md"])
    assert "gitmark:" not in capsys.readouterr().err

    def _refuse(root, paths=None):
        raise gm.LintPathError("путь не найден: docs/reference/aa.md")

    monkeypatch.setattr(gm, "cmd_lint", _refuse)
    with pytest.raises(SystemExit) as ei:
        gm.main(["--root", str(kb), "lint", "docs/reference/aa.md"])
    assert ei.value.code == 2


# ── refusal on an existing but unselectable path (guard 2) ─────────────────


@pytest.mark.parametrize("bad,shown", [
    ("docs/reference", "docs/reference"),          # directory
    ("./docs/reference/aa.md", "./docs/reference/aa.md"),  # "./"-prefix
    ("/etc/passwd", "/etc/passwd"),                # absolute path outside the KB
    ("", "(пустой аргумент)"),                     # empty string (exists as root)
    ("docs/reference/dd.md", "docs/reference/dd.md"),  # gitignored: on disk, not in iter_md
])
def test_existing_but_unselectable_path_refuses(kb: Path, gm, bad: str, shown: str):
    """spec: docs/plans/core-kb.md#готово-3 — an existing non-KB path is a refusal."""
    with pytest.raises(gm.LintPathError, match="не выбирает ни одного файла KB") as ei:
        gm.cmd_lint(kb, [bad])
    assert shown in str(ei.value)


def test_whitespace_only_argument_gets_placeholder(kb: Path, gm):
    """invariant: a degenerate argument is still named after control stripping."""
    with pytest.raises(gm.LintPathError) as ei:
        gm.cmd_lint(kb, ["\t"])
    assert "(пустой аргумент)" in str(ei.value)


def test_stat_failure_hands_decision_to_guard2(kb: Path, gm, monkeypatch):
    """invariant: EACCES is not "not found"; guard 2 decides by rel index."""
    orig = gm.Path.exists

    def raising(self, _orig=orig):
        if self.as_posix().endswith("docs/secret.md"):
            raise PermissionError(13, "Permission denied")
        return _orig(self)

    monkeypatch.setattr(gm.Path, "exists", raising)
    with pytest.raises(gm.LintPathError, match="не выбирает ни одного файла KB") as ei:
        gm.cmd_lint(kb, ["docs/secret.md"])
    assert "docs/secret.md" in str(ei.value)


def test_unicode_forms_are_byte_exact(kb: Path, gm):
    """invariant: selection is byte-exact; an NFC/NFD mismatch is a named refusal."""
    word_nfd = unicodedata.normalize("NFD", "ёмкость")
    (kb / "docs" / "notes" / (word_nfd + ".md")).write_text("# Ё\n", encoding="utf-8")
    nfd = "docs/notes/" + word_nfd + ".md"
    nfc = "docs/notes/" + unicodedata.normalize("NFC", "ёмкость") + ".md"
    assert isinstance(gm.cmd_lint(kb, [nfd]), dict)
    with pytest.raises(gm.LintPathError, match="путь не найден") as ei:
        gm.cmd_lint(kb, [nfc])
    assert nfc in str(ei.value)


def test_mixed_paths_refuse_naming_only_missing(kb: Path, gm):
    """invariant: a mixed selection refuses and names only the missing path."""
    with pytest.raises(gm.LintPathError) as ei:
        gm.cmd_lint(kb, ["docs/reference/aa.md", "docs/nope.md"])
    msg = str(ei.value)
    assert "docs/nope.md" in msg and "путь не найден" in msg
    assert "docs/reference/aa.md" not in msg


def test_canonical_path_does_not_refuse(kb: Path, gm):
    """spec: docs/plans/core-kb.md#готово-3 — a canonical path is a valid selection."""
    r = gm.cmd_lint(kb, ["docs/reference/aa.md"])
    assert isinstance(r, dict) and r["checked"] > 0


def test_root_md_selection_is_scoped_not_empty(tmp_path: Path, gm):
    """invariant: a selected root .md is checked by I4, not silently dropped."""
    docs = tmp_path / "docs"
    (docs / "reference").mkdir(parents=True)
    (docs / "README.md").write_text(
        "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n", encoding="utf-8")
    (docs / "reference" / "README.md").write_text(
        "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n", encoding="utf-8")
    (docs / "reference" / "aa.md").write_text(
        "---\nnode_type: bogus_type\ntitle: AA\n---\n\n# AA\n", encoding="utf-8")
    (tmp_path / "README.md").write_text(
        "# Root с битой ссылкой [x](./nope.md)\n", encoding="utf-8")
    r = gm.cmd_lint(tmp_path, ["README.md"])

    def codes(rel, code):
        return any(i[2] == rel and i[1] == code for i in r["issues"])

    assert codes("README.md", "I4")
    assert not codes("docs/reference/aa.md", "I2")
    full = gm.cmd_lint(tmp_path)
    assert any(i[2] == "docs/reference/aa.md" and i[1] == "I2" for i in full["issues"])


# ── selection semantics, one representative per family ─────────────────────


def test_selection_narrows_only_per_file_checks(kb: Path, gm):
    """spec: docs/plans/core-kb.md#готово-3 — paths narrow I1/I2/I3/I6 only."""
    r = gm.cmd_lint(kb, ["docs/reference/aa.md"])

    def codes(rel, code):
        return any(i[2] == rel and i[1] == code for i in r["issues"])

    assert codes("docs/reference/aa.md", "I2")
    assert not codes("docs/reference/bb.md", "I2")
    assert not codes("docs/ops/xx.md", "I1")
    assert not codes("docs/reference/cc.md", "I3")
    assert not codes("docs/reference/bb.md", "I6")
    assert codes("docs/reference/cc.md", "I4")
    assert any(i[1] == "I5" and i[2] in ("docs/notes/", "docs/ops/") for i in r["issues"])
    assert any(i[1] == "I9" and i[2] == "docs/services/cards.md" for i in r["issues"])
    assert any(i[1] == "I10" for i in r["issues"])
    assert r["checked"] == len(list(gm.iter_md(kb)))


def test_full_run_reports_all_per_file_issues(kb: Path, gm):
    """spec: docs/plans/core-kb.md#готово-3 — no paths means every per-file check."""
    r = gm.cmd_lint(kb)

    def codes(rel, code):
        return any(i[2] == rel and i[1] == code for i in r["issues"])

    assert codes("docs/reference/aa.md", "I2") and codes("docs/reference/bb.md", "I2")
    assert codes("docs/ops/xx.md", "I1") and codes("docs/reference/cc.md", "I3")
    assert codes("docs/reference/bb.md", "I6")


def test_guard_mutation_probe_reopens_silent_clean(gm, tmp_path: Path, monkeypatch):
    """invariant/mutation probe: bypassing _lint_path_guards makes a directory path
    select nothing and report a clean KB — the exact harm the matrix guards."""
    docs = tmp_path / "docs"
    (docs / "reference").mkdir(parents=True)
    (docs / "README.md").write_text(
        "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n"
        "[reference](reference/README.md)\n", encoding="utf-8")
    (docs / "reference" / "README.md").write_text(
        "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n", encoding="utf-8")
    (docs / "reference" / "aa.md").write_text(
        "---\nnode_type: bogus_type\ntitle: AA\n---\n\n# AA\n", encoding="utf-8")
    # Control: the unmutated guard refuses the directory.
    with pytest.raises(gm.LintPathError, match="не выбирает ни одного файла KB"):
        gm.cmd_lint(tmp_path, ["docs/reference"])
    # Mutation: without the guard, the same call is "clean" — the matrix can fail.
    monkeypatch.setattr(gm, "_lint_path_guards", lambda root, rels, paths: None)
    r = gm.cmd_lint(tmp_path, ["docs/reference"])
    assert r["checked"] == 3
    assert r["issues"] == []


# ── CLI E2E: exit codes, channels, message hygiene ─────────────────────────


def _run(kb: Path, *argv: str):
    return subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(kb), "lint", *argv],
        capture_output=True, text=True, timeout=60,
    )


def test_cli_refusal_exit2_stderr_stdout_empty(kb: Path):
    """spec: docs/plans/core-kb.md#готово-3 — refusal before any check: stdout empty, exit 2."""
    r = _run(kb, "--strict", "docs/plans/nope.md")
    assert r.returncode == 2, f"rc={r.returncode}, stderr={r.stderr!r}"
    assert "gitmark: путь не найден: docs/plans/nope.md" in r.stderr
    assert r.stdout == ""
    assert "чисто" not in r.stdout + r.stderr


def test_cli_refusal_without_strict_is_still_exit2(kb: Path):
    """spec: docs/plans/core-kb.md#готово-3 — exit 2 is unconditional."""
    r = _run(kb, "docs/plans/nope.md")
    assert r.returncode == 2, f"без --strict отказ обязан оставаться rc 2, rc={r.returncode}"
    assert "gitmark: путь не найден: docs/plans/nope.md" in r.stderr


def test_cli_dir_argument_refuses_instead_of_silent_clean(kb: Path):
    """spec: docs/plans/core-kb.md#готово-3 — a directory is a refusal, not a clean run."""
    r = _run(kb, "--strict", "docs/reference")
    assert r.returncode == 2
    assert "gitmark: путь не выбирает ни одного файла KB: docs/reference" in r.stderr
    assert r.stdout == "" and "чисто" not in r.stderr


def test_cli_mixed_paths_exit2(kb: Path):
    """spec: docs/plans/core-kb.md#готово-3 — a mixed selection refuses on the missing path."""
    r = _run(kb, "--strict", "docs/reference/aa.md", "docs/nope.md")
    assert r.returncode == 2
    assert "docs/nope.md" in r.stderr and "docs/reference/aa.md" not in r.stderr


def test_cli_control_chars_stripped_from_refusal(kb: Path):
    """invariant: argv is untrusted text; controls are replaced, never cut."""
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(kb), "lint",
         "docs/\x1b[2J\x7f\u009b\u202efake строка\nERR I9 подделка-nope"],
        capture_output=True, timeout=60,
    )
    assert r.returncode == 2
    raws = [(b"\x1b", "ESC"), (b"\x7f", "DEL"), ("\u009b".encode(), "C1 CSI"),
            ("\u202e".encode(), "bidi RLO"), ("\u2028".encode(), "LSEP"),
            ("\u200b".encode(), "ZWSP")]
    for raw, name in raws:
        assert raw not in r.stderr, f"{name} дошёл до stderr"
    assert r.stderr.count(b"\n") == 1, "перевод строки подделал вторую строку"
    assert b"\nERR" not in r.stderr, "подделанная строка отчёта встала началом строки"
    assert b"[WARN]" not in r.stderr, "WARN напечатан до отказа — порядок сломан"
    assert b"docs/" in r.stderr and b"fake" in r.stderr
    assert "подделка".encode() in r.stderr
    assert "строка".encode() in r.stderr
    assert "·".encode() in r.stderr


def test_cli_refusal_replaces_controls_without_gluing(kb: Path):
    """invariant: removing controls would glue a non-existent path into an existing one."""
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(kb), "lint", "docs/README\n.md"],
        capture_output=True, timeout=60,
    )
    assert r.returncode == 2
    assert "docs/README·.md".encode() in r.stderr
    assert b"README.md" not in r.stderr.replace("README\xc2\xb7".encode(), b"")


def test_cli_refusal_masks_secret_in_path(kb: Path):
    """invariant: a secret in argv does not leak to stderr."""
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(kb), "lint",
         "docs/x?token=ghp_FAKETOKEN12345"],
        capture_output=True, text=True, timeout=60,
    )
    assert r.returncode == 2
    assert "ghp_FAKETOKEN12345" not in r.stderr
    assert "[REDACTED]" in r.stderr


def test_cli_guard2_message_also_strips_controls(kb: Path):
    """invariant: control stripping is a property of the refusal print, not guard 1."""
    (kb / "docs" / "e\x1bsc").mkdir()
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(kb), "lint", "--strict", "docs/e\x1bsc"],
        capture_output=True, timeout=60,
    )
    assert r.returncode == 2
    assert b"\x1b" not in r.stderr
    assert b"[WARN]" not in r.stderr
    assert "не выбирает ни одного файла KB".encode() in r.stderr


def test_cli_existing_path_keeps_previous_exit_and_channels(kb: Path, gm):
    """spec: docs/plans/core-kb.md#готово-3 — a valid path keeps stdout, summary, strict exit."""
    r = _run(kb, "--strict", "docs/reference/aa.md")
    assert r.returncode == 1
    assert "node_type='bogus_type' вне словаря" in r.stdout
    assert "docs/reference/cc.md" in r.stdout
    assert "нет README.md" in r.stdout
    assert f"({len(list(gm.iter_md(kb)))} файлов" in r.stdout


def test_cli_without_strict_dirty_kb_still_exit0(kb: Path):
    """spec: docs/plans/core-kb.md#готово-3 — without --strict even ERR does not change exit."""
    r = _run(kb, "docs/reference/aa.md")
    assert r.returncode == 0, r.stderr[-500:]