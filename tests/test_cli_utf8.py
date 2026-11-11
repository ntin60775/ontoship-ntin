"""CLI output in a non-UTF-8 locale: the C-locale crash, reproduced and fixed.

target: C-locale CLI crash — UnicodeEncodeError, one-byte stdout, the honest
exit code replaced by the crash code. Incident source: the «Разбор
расхождений ожидание/факт» section of kb-scope ticket 03
(tickets/kb-scope/03-scope-over-global-checks.md), measured 2026-11-10.
The fix is one point, `_force_utf8_output` in `main`; these tests run the
CLI as a subprocess with the C-locale env and decode its output as UTF-8.

The input half of the C locale (argv surrogates) stays out of the unit:
queries and fixture paths are ASCII, Cyrillic lives in file content and in
the engine's output strings. The refusal contract on undecodable argv is
guarded separately — it is output behavior, not input handling.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ENGINE, make_git_repo

C_LOCALE = {"LC_ALL": "C", "PYTHONUTF8": "0", "PYTHONCOERCECLOCALE": "0"}


def _kb(tmp_path: Path) -> Path:
    """A clean KB with Cyrillic content and headings; paths stay ASCII —
    the C-locale filesystem encoding cannot create Cyrillic names."""
    return make_git_repo(tmp_path, {
        "docs/README.md": "---\nnode_type: index\ntitle: КБ\n---\n\n# КБ\n\n"
                          "[справка](reference/README.md)\n",
        "docs/reference/README.md":
            "---\nnode_type: index\ntitle: Справка\n---\n\n# Справка\n\n"
            "[заметка](note.md)\n",
        "docs/reference/note.md":
            "---\nnode_type: reference\ntitle: Заметка\nservice: _platform\n"
            "status: active\nupdated: 2026-11-11\nlinks:\n  part_of: [README.md]\n---\n\n"
            "# Заметка\n\nКириллица в тексте, маркер ZEBRA и [индекс](README.md).\n",
    })


def _run(root: Path, *argv: str, locale: dict | None = None):
    # PYTHONIOENCODING is dropped: it would force the stream encoding
    # independently of the locale and green the targets even on the base.
    env = {**os.environ, **(C_LOCALE if locale is None else locale)}
    env.pop("PYTHONIOENCODING", None)
    return subprocess.run([sys.executable, str(ENGINE), "--root", str(root), *argv],
                          capture_output=True, text=True, encoding="utf-8",
                          env=env, timeout=60)


def test_lint_clean_kb_prints_utf8_and_exits_zero(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — lint on a clean KB in the
    C locale: readable output, exit 0, no Traceback (base: crash)."""
    root = _kb(tmp_path)
    r = _run(root, "lint", "--strict")
    assert r.returncode == 0, r.stderr[-500:]
    assert "✓ чисто" in r.stdout
    assert "Traceback" not in r.stderr


def test_scope_line_survives_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — the incident's crash line
    `scope:` prints in the C locale (the project-tree repro)."""
    root = _kb(tmp_path)
    (root / "gitmark.scope.json").write_text(
        json.dumps({"exclude_prefixes": ["docs/reference/"]}), encoding="utf-8")
    r = _run(root, "lint", "--strict")
    assert r.returncode == 0, r.stderr[-500:]
    assert "scope: 2 файлов исключено по 1 префиксам" in r.stdout
    assert "✓ чисто" in r.stdout


def test_lint_dirty_kb_honest_exit_in_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — ERR under --strict gives the
    honest exit 1 with the finding printed, not a crash."""
    root = _kb(tmp_path)
    note = root / "docs" / "reference" / "note.md"
    note.write_text(note.read_text("utf-8").replace("(README.md)", "(missing.md)"),
                    encoding="utf-8")
    r = _run(root, "lint", "--strict")
    assert r.returncode == 1, r.stderr[-500:]
    assert "I4" in r.stdout, r.stdout[-500:]
    assert "Traceback" not in r.stderr


def test_index_prints_in_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — index prints its ✓ line."""
    r = _run(_kb(tmp_path), "index")
    assert r.returncode == 0, r.stderr[-500:]
    assert "✓ index" in r.stdout


def test_human_stat_prints_in_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — human stat prints the · line."""
    root = _kb(tmp_path)
    assert _run(root, "index").returncode == 0
    r = _run(root, "stat")
    assert r.returncode == 0, r.stderr[-500:]
    assert "GitMark ·" in r.stdout


def test_stat_json_stays_ascii_in_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — stat --json is ASCII-only
    and never crashed; the guard keeps it valid JSON."""
    root = _kb(tmp_path)
    assert _run(root, "index").returncode == 0
    r = _run(root, "stat", "--json")
    assert r.returncode == 0, r.stderr[-500:]
    assert json.loads(r.stdout)["files"] == 3


def test_search_prints_cyrillic_heading_in_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — search prints the Cyrillic
    heading; the query is ASCII (argv input half stays out of the unit)."""
    root = _kb(tmp_path)
    assert _run(root, "index").returncode == 0
    r = _run(root, "search", "ZEBRA")
    assert r.returncode == 0, r.stderr[-500:]
    assert "docs/reference/note.md" in r.stdout
    assert "Заметка" in r.stdout


def test_help_prints_in_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — argparse usage carries
    Cyrillic descriptions and prints before any command dispatch."""
    r = _run(tmp_path, "--help")
    assert r.returncode == 0, r.stderr[-500:]
    assert "корень репо" in r.stdout


def test_refusal_contract_readable_in_c_locale(tmp_path: Path):
    """target: C-locale CLI crash (kb-scope/03) — the refusal contract is not
    replaced: exit 2, empty stdout, readable message text in stderr
    (base: backslashreplace escapes instead of the text)."""
    root = _kb(tmp_path)
    r = _run(root, "lint", "docs/nope.md")
    assert r.returncode == 2 and r.stdout == ""
    assert "gitmark: путь не найден: docs/nope.md" in r.stderr
    (root / "gitmark.scope.json").write_text("{broken", encoding="utf-8")
    r2 = _run(root, "lint")
    assert r2.returncode == 2 and r2.stdout == ""
    assert "gitmark.scope.json: не JSON" in r2.stderr


@pytest.mark.parametrize("locale", [C_LOCALE, {}], ids=["c-locale", "utf8-locale"])
def test_refusal_survives_undecodable_argv(tmp_path: Path, locale: dict):
    """target: cu01 review panel — reconfigure without errors= reset stderr
    to strict and crashed the refusal on an argv surrogate (regression
    against base 9220f93, which exits 2 in both locales)."""
    root = _kb(tmp_path)
    r = _run(root, "lint", "docs/\udcffnope.md", locale=locale)
    assert r.returncode == 2, r.stderr[-500:]
    assert r.stdout == ""
    assert "gitmark:" in r.stderr
    assert "Traceback" not in r.stderr


def test_force_utf8_output_sets_encoding_and_errors(monkeypatch, gm):
    """invariant: the guard reconfigures both streams with UTF-8 and
    backslashreplace — the refusal contract on argv surrogates depends on it."""
    class Recording:
        def __init__(self):
            self.calls = []

        def reconfigure(self, **kw):
            self.calls.append(kw)

    out, err = Recording(), Recording()
    monkeypatch.setattr(gm.sys, "stdout", out)
    monkeypatch.setattr(gm.sys, "stderr", err)
    gm._force_utf8_output()
    want = {"encoding": "utf-8", "errors": "backslashreplace"}
    assert out.calls == [want]
    assert err.calls == [want]


def test_force_utf8_output_leaves_foreign_stream_alone(monkeypatch, gm):
    """invariant: a test-overridden stream without reconfigure stays untouched
    — the ticket's «ветка недоступна — поведение не меняется»."""
    class Foreign:
        pass

    out, err = Foreign(), Foreign()
    monkeypatch.setattr(gm.sys, "stdout", out)
    monkeypatch.setattr(gm.sys, "stderr", err)
    gm._force_utf8_output()


def test_force_utf8_output_under_capsys(gm, capsys):
    """invariant: the pytest capture stream survives the guard and prints."""
    gm._force_utf8_output()
    print("✓ чисто")
    assert "✓ чисто" in capsys.readouterr().out