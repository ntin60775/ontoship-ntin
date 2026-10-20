"""Trimmed GitMark engine: commands, discovery, resolvers, lint invariants.

Each test names its justification: ``spec: docs/plans/core-kb.md#<clause>``,
``invariant: I<n>``, or ``target: <observed failure>``. The suite is stdlib +
pytest only; no Node.
"""
from __future__ import annotations

import ast
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ENGINE, REPO, load_engine


# ── surface: one file, trimmed commands, package root ──────────────────────


def test_engine_is_one_auditable_file(gm):
    """spec: docs/plans/core-kb.md#done-4 — one file, no package layout."""
    assert ENGINE.is_file()
    assert ENGINE.parent == REPO / "skills" / "kb-search"
    assert not list(ENGINE.parent.glob("gitmark/*.py"))


def test_cmd_lint_is_short_and_orchestrates_helpers(gm):
    """spec: docs/plans/core-kb.md#done-4 — cmd_lint <= 80 lines, helpers in-file."""
    tree = ast.parse(ENGINE.read_text("utf-8"))
    fn = next(n for n in tree.body
              if isinstance(n, ast.FunctionDef) and n.name == "cmd_lint")
    assert fn.end_lineno - fn.lineno + 1 <= 80, "cmd_lint grew back past the budget"
    called = {n.func.id for n in ast.walk(fn)
              if isinstance(n, ast.Call) and isinstance(n.func, ast.Name)}
    assert {"_lint_path_guards", "_lint_link_graph", "_lint_readme_index",
            "_lint_per_doc", "_lint_global"} <= called


def test_package_root_in_this_repo(gm):
    """spec: docs/plans/core-kb.md#done-4 — PKG_ROOT works in the repo layout."""
    assert gm.PKG_ROOT == REPO
    assert gm.pkg_version() == gm.VERSION


@pytest.mark.parametrize("install", [".dsh", ".zcode"])
def test_package_root_in_an_install_copy(tmp_path: Path, install: str):
    """spec: docs/plans/core-kb.md#done-4 — PKG_ROOT works in a .dsh or .zcode copy."""
    dst = tmp_path / install / "skills" / "kb-search"
    dst.mkdir(parents=True)
    shutil.copy2(ENGINE, dst / "gitmark.py")
    mod = load_engine(dst / "gitmark.py", name=f"gitmark_{install.strip('.')}_copy")
    assert mod.PKG_ROOT == tmp_path / install
    assert mod.pkg_version() == mod.VERSION


def test_removed_commands_and_registry_symbols_are_gone(gm, tmp_path: Path, capsys):
    """spec: docs/plans/core-kb.md#done-4 — inventory/serve and I7 are absent."""
    for name in ("cmd_inventory", "cmd_serve", "inventory_issues",
                 "COMMANDS_DIR", "REGISTRY_REL", "PLANS_INDEX_REL"):
        assert not hasattr(gm, name), f"{name} survived the trim"
    for command in ("inventory", "serve"):
        with pytest.raises(SystemExit) as ei:
            gm.main(["--root", str(tmp_path), command])
        assert ei.value.code == 2
    assert "invalid choice" in capsys.readouterr().err


def test_lint_never_emits_i7(gm, tmp_path: Path):
    """spec: docs/plans/core-kb.md#done-4 — a registry-looking KB is not I7."""
    docs = tmp_path / "docs" / "reference"
    docs.mkdir(parents=True)
    (tmp_path / "docs" / "README.md").write_text(
        "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n", encoding="utf-8")
    (docs / "commands.md").write_text(
        "---\nnode_type: reference\ntitle: Registry\nlinks:\n  part_of: [README.md]\n---\n\n"
        "# Registry\n\n<!-- BEGIN inventory:commands -->\n<!-- END inventory:commands -->\n",
        encoding="utf-8")
    r = gm.cmd_lint(tmp_path)
    assert all(code != "I7" for _, code, _, _ in r["issues"])


def test_version_cli(gm):
    """spec: docs/plans/core-kb.md#done-2 — version reports the package version."""
    r = subprocess.run([sys.executable, str(ENGINE), "version"],
                       capture_output=True, text=True, timeout=60)
    assert r.returncode == 0
    assert r.stdout.strip() == f"gitmark {gm.VERSION}"


# ── index / search / stat / map ────────────────────────────────────────────


def _index_kb(root: Path) -> Path:
    (root / "docs" / "reference").mkdir(parents=True)
    (root / "docs" / "README.md").write_text(
        "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n"
        "[reference](reference/README.md) · [note](reference/note.md)\n", encoding="utf-8")
    (root / "docs" / "reference" / "README.md").write_text(
        "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n", encoding="utf-8")
    (root / "docs" / "reference" / "note.md").write_text(
        "---\nnode_type: reference\ntitle: Note\nlinks:\n  part_of: [README.md]\n---\n\n"
        "# Note\n\nThe platypus swims in the index.\n", encoding="utf-8")
    return root


def test_index_search_and_stat(gm, tmp_path: Path):
    """spec: docs/plans/core-kb.md#done-2 — index writes .gitmark/index.db, search finds a doc."""
    root = _index_kb(tmp_path)
    r = gm.cmd_index(root)
    assert (root / ".gitmark" / "index.db").is_file()
    assert r["files"] == 3 and r["chunks"] >= 3 and r["links"] == 2
    hits = gm.cmd_search(root, "platypus")
    assert hits and hits[0]["path"] == "docs/reference/note.md"
    s = gm.cmd_stat(root)
    assert s["indexed"] is True and s["files"] == 3 and s["links"] == 2


def test_search_before_index_is_a_named_refusal(gm, tmp_path: Path):
    """spec: docs/plans/core-kb.md#done-2 — search without an index tells the operator."""
    with pytest.raises(SystemExit, match="Индекс не найден"):
        gm.cmd_search(tmp_path, "anything")


def _clean_kb(root: Path) -> Path:
    (root / "docs" / "reference").mkdir(parents=True)
    (root / "docs" / "README.md").write_text(
        "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n"
        "[reference](reference/README.md)\n", encoding="utf-8")
    (root / "docs" / "reference" / "README.md").write_text(
        "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n\n"
        "[note](note.md)\n", encoding="utf-8")
    (root / "docs" / "reference" / "note.md").write_text(
        "---\nnode_type: reference\ntitle: Note\nlinks:\n  part_of: [README.md]\n---\n\n"
        "# Note\n\nThe platypus swims.\n", encoding="utf-8")
    return root


def test_cli_clean_kb_lint_strict_exit0(tmp_path: Path):
    """spec: docs/plans/core-kb.md#done-3 — lint --strict is 0 on a clean KB."""
    root = _clean_kb(tmp_path)
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(root), "lint", "--strict"],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr
    assert "чисто" in r.stdout


def test_demo_flow_red_green(gm, tmp_path: Path):
    """spec: docs/plans/core-kb.md#done-2 — index/search, a broken link is red, fixing it is green."""
    root = _clean_kb(tmp_path)
    note = root / "docs" / "reference" / "note.md"
    note.write_text(
        "---\nnode_type: reference\ntitle: Note\nlinks:\n  part_of: [README.md]\n---\n\n"
        "# Note\n\nThe platypus swims. [gone](missing.md)\n", encoding="utf-8")
    assert gm.cmd_index(root)["files"] == 3
    assert gm.cmd_search(root, "platypus")[0]["path"] == "docs/reference/note.md"
    assert [i for i in gm.cmd_lint(root)["issues"] if i[1] == "I4"]
    note.write_text(
        "---\nnode_type: reference\ntitle: Note\nlinks:\n  part_of: [README.md]\n---\n\n"
        "# Note\n\nThe platypus swims.\n", encoding="utf-8")
    r = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(root), "lint", "--strict"],
        capture_output=True, text=True, timeout=60)
    assert r.returncode == 0, r.stdout + r.stderr


def test_stat_json_contract(gm, tmp_path: Path):
    """spec: docs/plans/core-kb.md#done-2 — stat --json always emits valid JSON."""
    before = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(tmp_path), "stat", "--json"],
        capture_output=True, text=True, timeout=60)
    assert before.returncode == 0
    assert json.loads(before.stdout) == {"indexed": False}
    _index_kb(tmp_path)
    gm.cmd_index(tmp_path)
    after = subprocess.run(
        [sys.executable, str(ENGINE), "--root", str(tmp_path), "stat", "--json"],
        capture_output=True, text=True, timeout=60)
    assert after.returncode == 0
    data = json.loads(after.stdout)
    assert data["indexed"] is True and data["files"] == 3


def test_map_writes_self_contained_html(gm, tmp_path: Path):
    """spec: docs/plans/core-kb.md#done-2 — map writes HTML."""
    root = _index_kb(tmp_path)
    out = root / "docs-map.html"
    r = gm.cmd_map(root, out)
    assert out.is_file() and r["files"] == 3 and r["refs"] >= 1
    html = out.read_text("utf-8")
    assert html.startswith("<!doctype html>") and "GitMark" in html
    assert "platypus" in html


# ── discovery: git / .gitignore fallback / install roots ──────────────────


def test_install_roots_are_never_indexed(gm, tmp_path: Path):
    """invariant: .dsh (DSH) and .zcode (zcode) installs are not duplicated into the corpus."""
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "README.md").write_text("# KB\n", encoding="utf-8")
    for install in (".dsh", ".zcode"):
        hidden = tmp_path / install / "skills" / "kb-search" / "SKILL.md"
        hidden.parent.mkdir(parents=True, exist_ok=True)
        hidden.write_text("# copied skill\n", encoding="utf-8")
    for with_git in (False, True):
        if with_git:
            subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
        found = {p.relative_to(tmp_path).as_posix() for p in gm.iter_md(tmp_path)}
        assert ".dsh" in gm.EXCLUDE_DIRS and ".zcode" in gm.EXCLUDE_DIRS
        assert "docs/README.md" in found
        for install in (".dsh", ".zcode"):
            assert not any(rel.startswith(install + "/") for rel in found), \
                f"{install} leaked into the corpus (git={with_git})"


def test_gitignore_excludes_dirs_and_files(gm, tmp_path: Path):
    """invariant: the no-git fallback honours dir/file rules from .gitignore."""
    (tmp_path / ".gitignore").write_text(".scratch/\ndraft.md\n", encoding="utf-8")
    (tmp_path / ".scratch").mkdir()
    (tmp_path / ".scratch" / "report.md").write_text("ephemeral", encoding="utf-8")
    (tmp_path / "draft.md").write_text("draft", encoding="utf-8")
    (tmp_path / "keep.md").write_text("keep", encoding="utf-8")
    found = {p.name for p in gm.iter_md(tmp_path)}
    assert "report.md" not in found and "draft.md" not in found
    assert "keep.md" in found


def test_gitignore_wildcard(gm, tmp_path: Path):
    """invariant: one-segment '*' rules match file names."""
    (tmp_path / ".gitignore").write_text("*-map.html\n", encoding="utf-8")
    dir_pats, file_pats, path_pats, unsupported = gm.parse_gitignore(tmp_path)
    assert dir_pats == [] and path_pats == [] and unsupported == []
    assert file_pats == ["*-map.html"]
    assert gm._wild_match("docs-map.html", "*-map.html")
    assert not gm._wild_match("notes.md", "*-map.html")


def test_gitignore_path_rules_are_not_dropped(gm, tmp_path: Path):
    """invariant: path-anchored .gitignore rules are honoured, not lost silently."""
    (tmp_path / ".gitignore").write_text(
        "build/\n.dsh/plugins/\n.dsh/.backup-*\ndrafts/secret.md\n", encoding="utf-8")
    for rel in ("docs/live.md", ".dsh/plugins/x.md", "drafts/secret.md", "build/b.md",
                ".dsh/.backup-20260101-000000/rules/r.md"):
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("текст", encoding="utf-8")
    hidden = (".dsh/plugins/x.md", "drafts/secret.md", "build/b.md",
              ".dsh/.backup-20260101-000000/rules/r.md")
    for source in (gm.iter_md_fallback, gm.iter_md):
        found = {p.relative_to(tmp_path).as_posix() for p in source(tmp_path)}
        assert "docs/live.md" in found, f"{source.__name__}: live document lost"
        for rel in hidden:
            assert rel not in found, f"{source.__name__}: {rel} leaked into the index"


def test_iter_md_takes_the_list_from_git(gm, tmp_path: Path):
    """invariant: with git available, nested .gitignore rules are respected."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / "docs" / "nested").mkdir(parents=True)
    (tmp_path / "docs" / "nested" / ".gitignore").write_text("hidden.md\n", encoding="utf-8")
    (tmp_path / "docs" / "nested" / "hidden.md").write_text("скрытый", encoding="utf-8")
    (tmp_path / "docs" / "nested" / "shown.md").write_text("видимый", encoding="utf-8")
    assert gm.git_md_files(tmp_path) is not None
    found = {p.relative_to(tmp_path).as_posix() for p in gm.iter_md(tmp_path)}
    assert "docs/nested/shown.md" in found
    assert "docs/nested/hidden.md" not in found


def test_unsupported_rules_warn_when_git_is_absent(gm, tmp_path: Path, monkeypatch):
    """invariant: the fallback names the .gitignore rules it cannot execute."""
    (tmp_path / ".gitignore").write_text("!keep.md\n**/generated\n", encoding="utf-8")
    monkeypatch.setattr(gm, "git_md_files", lambda root: None)
    warnings = gm.gitignore_warnings(tmp_path)
    assert any("!keep.md" in w for w in warnings)
    assert any("**/generated" in w for w in warnings)


def test_no_gitignore_warnings_on_the_git_path(gm, tmp_path: Path):
    """invariant: the git path needs no fallback warnings."""
    subprocess.run(["git", "init", "-q"], cwd=tmp_path, check=True)
    (tmp_path / ".gitignore").write_text("!keep.md\n", encoding="utf-8")
    assert gm.gitignore_warnings(tmp_path) == []


# ── frontmatter and link resolution ────────────────────────────────────────


def test_parse_frontmatter_nested_links_inline(gm):
    """invariant: the stdlib frontmatter parser keeps nested links."""
    fm = gm.parse_frontmatter(
        "---\nnode_type: runbook\ntitle: T\n"
        "links:\n  part_of: [../README.md]\n  relates_to: [a.md, b.md]\n---\n"
    )
    assert fm["links"] == {"part_of": ["../README.md"], "relates_to": ["a.md", "b.md"]}
    assert "part_of" not in fm


def test_parse_frontmatter_nested_links_block_list(gm):
    """invariant: nested links may be a block list."""
    fm = gm.parse_frontmatter("---\nlinks:\n  relates_to:\n    - a.md\n    - b.md\n---\n")
    assert fm["links"] == {"relates_to": ["a.md", "b.md"]}


def test_parse_frontmatter_scalar_after_links_stays_on_top(gm):
    """invariant: a scalar after a links block is a top-level key."""
    fm = gm.parse_frontmatter("---\nlinks:\n  part_of: [README.md]\nstatus: active\n---\n")
    assert fm["links"] == {"part_of": ["README.md"]}
    assert fm["status"] == "active"


def test_parse_frontmatter_top_level_list_still_works(gm):
    """invariant: top-level block lists keep working."""
    fm = gm.parse_frontmatter("---\ntags:\n  - a\n  - b\n---\n")
    assert fm["tags"] == ["a", "b"]


def _fs_fixture(tmp_path: Path) -> Path:
    (tmp_path / "docs" / "ops").mkdir(parents=True)
    (tmp_path / "docs" / "README.md").write_text("# KB\n", encoding="utf-8")
    (tmp_path / "docs" / "ops" / "dev-contour.md").write_text("# Контур\n", encoding="utf-8")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.bsl").write_text("// код\n", encoding="utf-8")
    (tmp_path / "my file.md").write_text("# Пробел\n", encoding="utf-8")
    return tmp_path


def test_fs_resolve_checks_directories_and_non_md_files(gm, tmp_path: Path):
    """invariant: I4's strict resolver checks directories and code files too."""
    root = _fs_fixture(tmp_path)
    assert gm.fs_resolve(root, "docs/README.md", "ops")[0] is True
    assert gm.fs_resolve(root, "docs/README.md", "../src/module.bsl")[0] is True
    assert gm.fs_resolve(root, "docs/README.md", "../src/gone.bsl")[0] is False
    assert gm.fs_resolve(root, "docs/README.md", "ops/gone")[0] is False


def test_fs_resolve_decodes_url_encoding_and_strips_selectors(gm, tmp_path: Path):
    """invariant: I4 checks the path a reader actually opens."""
    root = _fs_fixture(tmp_path)
    assert gm.fs_resolve(root, "docs/README.md", "../my%20file.md")[0] is True
    assert gm.fs_resolve(root, "docs/README.md", "../my file.md:12-34")[0] is True
    assert gm.fs_resolve(root, "docs/README.md", "ops/dev-contour.md#шаг")[0] is True


def test_fs_resolve_checks_a_path_that_leaves_the_repo(gm, tmp_path: Path):
    """invariant: a relative link outside the repo is checked where it leads."""
    root = tmp_path / "repo"
    (root / "docs").mkdir(parents=True)
    (root / "docs" / "README.md").write_text("# KB\n", encoding="utf-8")
    (tmp_path / "sibling").mkdir()
    (tmp_path / "sibling" / "note.md").write_text("# Сосед\n", encoding="utf-8")
    assert gm.fs_resolve(root, "docs/README.md", "../../sibling/note.md")[0] is True
    assert gm.fs_resolve(root, "docs/README.md", "../../nowhere/note.md")[0] is False


def test_fs_resolve_unwraps_an_angle_bracket_destination(gm, tmp_path: Path):
    """invariant: an angle-bracket absolute target is out of scope, not broken."""
    root = _fs_fixture(tmp_path)
    assert gm.fs_resolve(root, "docs/README.md", "</home/nobody/file.pdf>") == (True, None)


def test_fs_resolve_skips_external_anchors_and_root_absolute(gm, tmp_path: Path):
    """invariant: external URIs, anchors and /root paths get no verdict."""
    root = _fs_fixture(tmp_path)
    for href in ("https://example.com/x.md", "mailto:a@b.c", "#якорь", "/docs/README.md"):
        assert gm.fs_resolve(root, "docs/README.md", href) == (True, None)


# ── lint: I1/I2/I3/I4/I5/I6/I8/I9/I10 ──────────────────────────────────────


def _doc(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def test_i1_load_bearing_doc_without_frontmatter(gm, tmp_path: Path):
    """invariant: I1 — a load-bearing docs/ document must declare node_type."""
    _doc(tmp_path, "docs/reference/bare.md", "# Bare\n")
    issues = [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I1"]
    assert len(issues) == 1 and issues[0][0] == "ERR"
    assert issues[0][2] == "docs/reference/bare.md"


def test_i1_exempts_readme_and_non_load_bearing_docs(gm, tmp_path: Path):
    """invariant: I1 — README indexes and docs/notes/ are outside the rule."""
    _doc(tmp_path, "docs/reference/README.md", "# Reference\n")
    _doc(tmp_path, "docs/notes/free.md", "# Free\n")
    issues = [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I1"]
    assert issues == []


def test_i2_type_vocabulary_comes_from_the_ontology(gm, tmp_path: Path):
    """invariant: I2 — docs/ontology.md is the single type vocabulary."""
    _doc(tmp_path, "docs/ontology.md",
         "# Ontology\n\n| node_type | what |\n|---|---|\n| `wallet` | a wallet |\n")
    doc = _doc(tmp_path, "docs/reference/w.md", "---\nnode_type: wallet\ntitle: W\n---\n\n# W\n")
    assert [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I2"] == []
    doc.write_text("---\nnode_type: nosuchtype\ntitle: W\n---\n\n# W\n", encoding="utf-8")
    assert [i for i in gm.cmd_lint(tmp_path)["issues"]
            if i[1] == "I2" and "вне словаря" in i[3]] != []


def test_i2_falls_back_without_an_ontology(gm, tmp_path: Path):
    """invariant: I2 — the built-in vocabulary is used when docs/ontology.md is absent."""
    (tmp_path / "docs").mkdir()
    assert gm.node_types(tmp_path) == gm.NODE_TYPES


def test_i3_a_frontmatter_link_is_not_an_orphan(gm, tmp_path: Path):
    """invariant: I3 — frontmatter links count as connectivity."""
    _doc(tmp_path, "docs/README.md", "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n")
    _doc(tmp_path, "docs/note.md",
         "---\nnode_type: runbook\ntitle: Заметка\nlinks:\n  part_of: [README.md]\n---\n\n"
         "# Заметка\n")
    assert [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I3"] == []


def _link_fixture(root: Path, href: str) -> Path:
    _doc(root, "docs/README.md", "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n")
    _doc(root, "CONTEXT.md", "---\nnode_type: reference\ntitle: Контекст\n---\n\n# Контекст\n")
    _doc(root, "docs/reference/README.md",
         f"---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n\n[CONTEXT]({href})\n")
    return root


def test_i4_catches_a_link_only_the_basename_saves(gm, tmp_path: Path):
    """invariant: I4 — a basename-only match is not a traversable link."""
    repo = _link_fixture(tmp_path, "../CONTEXT.md")
    assert [i for i in gm.cmd_lint(repo)["issues"] if i[1] == "I4"] != []


def test_i4_accepts_an_exact_link(gm, tmp_path: Path):
    """invariant: I4 — exact file and directory links pass."""
    repo = _link_fixture(tmp_path, "../../CONTEXT.md")
    assert [i for i in gm.cmd_lint(repo)["issues"] if i[1] == "I4"] == []


def test_i4_skips_a_root_absolute_link(gm, tmp_path: Path):
    """invariant: I4 — a root-absolute /… link gets no verdict."""
    repo = _link_fixture(tmp_path, "/docs/README.md")
    assert [i for i in gm.cmd_lint(repo)["issues"] if i[1] == "I4"] == []


def test_i4_hints_the_target_the_basename_would_save(gm, tmp_path: Path):
    """invariant: I4 — the finding names the soft-resolved target."""
    _doc(tmp_path, "docs/README.md", "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n")
    _doc(tmp_path, "docs/ops/dev-contour.md",
         "---\nnode_type: runbook\ntitle: Контур\n---\n\n# Контур\n")
    _doc(tmp_path, "docs/reference/configuration.md",
         "---\nnode_type: reference\ntitle: Настройка\n---\n\n[контур](dev-contour.md)\n")
    msgs = [i[3] for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I4"]
    assert len(msgs) == 1 and "docs/ops/dev-contour.md" in msgs[0]


def test_i4_catches_broken_body_and_frontmatter_links(gm, tmp_path: Path):
    """invariant: I4 — body, documents and depends_on are all checked."""
    _doc(tmp_path, "docs/README.md", "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n")
    _doc(tmp_path, "docs/reference/README.md",
         "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n")
    _doc(tmp_path, "docs/reference/note.md",
         "---\nnode_type: reference\ntitle: Заметка\nservice: _platform\n"
         "links:\n  documents: [../../nope_does_not_exist]\n"
         "  depends_on: [../missing_doc.md]\n---\n\n"
         "Тело: [битая ссылка](../../nope2.md)\n")
    i4 = [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I4"]
    assert len(i4) == 3, i4
    assert any("documents:" in i[3] for i in i4) and any("depends_on:" in i[3] for i in i4)


def test_i4_checks_non_md_targets(gm, tmp_path: Path):
    """invariant: I4 — a code file is checked like a .md target."""
    _doc(tmp_path, "docs/README.md",
         "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n"
         "[код](../src/module.bsl) · [нет](../src/gone.bsl)\n")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "module.bsl").write_text("// код\n", encoding="utf-8")
    msgs = [i[3] for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I4"]
    assert len(msgs) == 1 and "gone.bsl" in msgs[0]


def test_i4_ignores_a_link_title(gm, tmp_path: Path):
    """invariant: I4 — [x](doc.md "title") is a valid link."""
    _doc(tmp_path, "docs/README.md", "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n")
    _doc(tmp_path, "docs/note.md",
         "---\nnode_type: reference\ntitle: Заметка\n---\n\n"
         '[README](README.md "индекс папки")\n')
    assert [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I4"] == []


def test_i5_names_a_folder_without_a_readme(gm, tmp_path: Path):
    """invariant: I5 — every docs/ folder carries its README index."""
    _doc(tmp_path, "docs/README.md", "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n")
    _doc(tmp_path, "docs/ops/note.md", "# Note\n")
    warns = [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I5"]
    assert any(i[2] == "docs/ops/" for i in warns)


def test_i6_catches_a_scalar_supersedes(gm, tmp_path: Path):
    """invariant: I6 — a scalar supersedes is checked, not skipped."""
    _doc(tmp_path, "docs/README.md", "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n")
    _doc(tmp_path, "docs/old.md",
         "---\nnode_type: reference\ntitle: Старое\nstatus: active\n---\n\n# Старое\n")
    _doc(tmp_path, "docs/new.md",
         "---\nnode_type: reference\ntitle: Новое\nlinks:\n  supersedes: old.md\n---\n\n"
         "# Новое\n")
    assert [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I6"] != []


def _ontology_twin(root: Path, body: str) -> None:
    _doc(root, "docs/ontology.md", f"# Project ontology\n\n{body}\n")
    _doc(root, "skills/kb-curate/ontology.md", f"# Shipped ontology\n\n{body}\n")


def test_i8_flat_layout_blocks_ontology_drift(gm, tmp_path: Path, monkeypatch):
    """invariant: I8 — in the repo layout project and shipped models must match."""
    monkeypatch.setattr(gm, "PKG_ROOT", tmp_path)
    _ontology_twin(tmp_path, "## Semantic layer\n\n| node_type | what |\n|---|---|\n| `reference` | doc |")
    assert [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I8"] == []
    _doc(tmp_path, "skills/kb-curate/ontology.md",
         "# Shipped ontology\n\n## Semantic layer\n\n| node_type | what |\n|---|---|\n"
         "| `runbook` | doc |")
    issues = [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I8"]
    assert issues and issues[0][0] == "ERR"


def test_i8_warns_when_the_package_is_external(gm, tmp_path: Path, monkeypatch):
    """invariant: I8 — an external .dsh package gets a WARN, not an ERR."""
    monkeypatch.setattr(gm, "PKG_ROOT", tmp_path / "package")
    _doc(tmp_path, "docs/ontology.md", "# Project\n\n## Semantic layer\n\n| a | b |\n")
    _doc(tmp_path / "package", "skills/kb-curate/ontology.md",
         "# Package\n\n## Semantic layer\n\n| c | d |\n")
    issues = [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I8"]
    assert issues and issues[0][0] == "WARN"


ONTOLOGY = """# GitMark ontology

## Semantic layer

| node_type | what it is | lives in |
|---|---|---|
| `reference` | a spec | `docs/reference/` |
| `index` | a folder index | any `README.md` |
| `schema` | a card schema | the cards' folder |
| `wallet` | a wallet card | `wallets/` |
"""


def _cards_fixture(tmp_path: Path) -> Path:
    _doc(tmp_path, "docs/README.md", "# KB\n")
    _doc(tmp_path, "docs/ontology.md", ONTOLOGY)
    _doc(tmp_path, "wallets/README.md", "# Кошельки\n")
    _doc(tmp_path, "wallets/_schema.md",
         "---\nnode_type: schema\ntitle: Кошелёк\ncard_type: wallet\n"
         "required: [uid, kind, balance]\n"
         'values: ["kind: карта|счёт"]\n---\n\n# Схема\n')
    _doc(tmp_path, "wallets/main.md",
         "---\nnode_type: wallet\ntitle: Основной\nuid: main\nkind: карта\n"
         "balance: 100\n---\n\nПроза вольная: схема её не ограничивает.\n")
    return tmp_path


def test_i9_requires_declared_type_in_a_card_folder(gm, tmp_path: Path):
    """invariant: I9 — a card without node_type is an error, not a silent skip."""
    repo = _cards_fixture(tmp_path)
    _doc(repo, "wallets/bare.md", "---\ntitle: Без типа\n---\n\nПроза.\n")
    msgs = [i[3] for i in gm.cmd_lint(repo)["issues"] if i[1] == "I9"]
    assert any("без объявленного типа" in m for m in msgs)


def test_i9_reports_a_type_the_folder_schema_does_not_declare(gm, tmp_path: Path):
    """invariant: I9 — the card cannot choose a schema by itself."""
    repo = _cards_fixture(tmp_path)
    _doc(repo, "wallets/alien.md",
         "---\nnode_type: reference\ntitle: Чужой\n---\n\nПроза.\n")
    msgs = [i[3] for i in gm.cmd_lint(repo)["issues"] if i[1] == "I9"]
    assert any("не объявлен схемой" in m for m in msgs)


def test_i9_requires_schema_fields(gm, tmp_path: Path):
    """invariant: I9 — a missing required field is an ERR naming the field."""
    repo = _cards_fixture(tmp_path)
    _doc(repo, "wallets/no-kind.md",
         "---\nnode_type: wallet\ntitle: Без вида\nuid: x\nbalance: 1\n---\n\nПроза.\n")
    assert [i[3] for i in gm.cmd_lint(repo)["issues"] if i[1] == "I9"] == [
        "нет обязательного поля: kind"]


def test_i9_keeps_schema_values_within_the_list(gm, tmp_path: Path):
    """invariant: I9 — a value outside the schema list is an ERR."""
    repo = _cards_fixture(tmp_path)
    _doc(repo, "wallets/bad-kind.md",
         "---\nnode_type: wallet\ntitle: Плохой\nuid: y\nkind: наличные\nbalance: 2\n---\n\n"
         "Проза.\n")
    msgs = [i[3] for i in gm.cmd_lint(repo)["issues"] if i[1] == "I9"]
    assert any("поле kind" in m and "вне списка" in m for m in msgs)


def test_i9_leaves_a_conforming_card_and_its_prose_alone(gm, tmp_path: Path):
    """invariant: I9 — README and schema are not cards; prose is free."""
    repo = _cards_fixture(tmp_path)
    assert [i for i in gm.cmd_lint(repo)["issues"] if i[1] == "I9"] == []


def test_i10_requires_a_body_link_to_each_subsection(gm, tmp_path: Path):
    """invariant: I10 — every docs/ subsection README is linked from its parent."""
    _doc(tmp_path, "docs/README.md",
         "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n"
         "[reference](reference/README.md)\n")
    _doc(tmp_path, "docs/reference/README.md",
         "---\nnode_type: index\ntitle: Reference\n---\n\n# Reference\n")
    _doc(tmp_path, "docs/ops/README.md",
         "---\nnode_type: index\ntitle: Ops\n---\n\n# Ops\n")
    issues = [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I10"]
    assert any(i[2] == "docs/README.md" and "docs/ops/" in i[3] for i in issues)
    _doc(tmp_path, "docs/README.md",
         "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n"
         "[reference](reference/README.md) · [ops](ops/)\n")
    assert [i for i in gm.cmd_lint(tmp_path)["issues"] if i[1] == "I10"] == []