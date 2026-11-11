"""KB-корпус и `gitmark.scope.json`: scope режет корпус в `iter_md`.

Traceability: каждый тест несёт ``spec: docs/plans/kb-scope.md#готово-N`` или
``invariant: <statement>``. Ожидания берутся из литералов спеки (списки
префиксов, строка `scope: …`, exit-коды 0/1/2), а не пересчитываются движком.

Мутационная проба: снятие фильтра (`iter_corpus` без scope) обязано вернуть
исключённые файлы обратно в корпус — иначе матрица не умеет падать.
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from conftest import ENGINE, make_git_repo

PREFIXES = ["snapshots/", "apps/web/tests/expected/"]
KEEP = ["docs/README.md", "docs/keep.md", "snapshots-notes/keep2.md"]
CUT = ["apps/web/tests/expected/shot.md", "snapshots/excl.md"]


def _repo(tmp_path: Path) -> Path:
    """Пять md: три внутри KB, два — ожидаемый вывод тестов и снапшоты."""
    return make_git_repo(tmp_path, {
        "docs/README.md": "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n",
        "docs/keep.md": "---\nnode_type: reference\ntitle: Keep\n---\n\nZEBRA\n",
        "snapshots-notes/keep2.md": "# Keep2\n\nMARBLE\n",
        "snapshots/excl.md": "# Excl\n\nQUARTZ\n",
        "apps/web/tests/expected/shot.md": "# Shot\n\nONYX\n",
    })


def _scope(root: Path, payload) -> Path:
    body = payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False)
    path = root / "gitmark.scope.json"
    path.write_text(body, encoding="utf-8")
    return path


def _rels(root: Path, gm) -> list:
    return sorted(p.relative_to(root).as_posix() for p in gm.iter_md(root))


def _run(root: Path, *argv: str):
    # encoding=utf-8: вывод движка — UTF-8, и прогон не должен зависеть от
    # локали оболочки (LC_ALL=C ломает text=True без явной кодировки)
    return subprocess.run([sys.executable, str(ENGINE), "--root", str(root), *argv],
                          capture_output=True, text=True, encoding="utf-8",
                          timeout=120)


# ── корпус: срезка и обратная совместимость ────────────────────────────────


def test_scope_absent_keeps_todays_corpus(tmp_path: Path, gm):
    """invariant: absence of gitmark.scope.json keeps today's corpus."""
    root = _repo(tmp_path)
    assert _rels(root, gm) == sorted(KEEP + CUT)


def test_scope_cuts_lint_corpus(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-1 — excluded files leave `checked`."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": PREFIXES})
    r = gm.cmd_lint(root)
    assert r["checked"] == len(KEEP)
    assert [i[2] for i in r["issues"] if i[2] in CUT] == []
    assert r["scope_excluded"] == len(CUT)
    assert r["scope_prefix_count"] == len(PREFIXES)


def test_scope_cuts_index_stat_search_map(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-1 — тот же срез у index, stat, search, map."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": PREFIXES})
    idx = gm.cmd_index(root)
    assert idx["files"] == len(KEEP)
    assert gm.cmd_stat(root)["files"] == len(KEEP)
    # trigram-поиск не матчит «QUARTZ» с «ZEBRA» как соседние слова; ожидание
    # проверяемое: исключённого файла в результатах нет, оставшийся — есть
    assert all(r["path"] not in CUT for r in gm.cmd_search(root, "QUARTZ ONYX"))
    assert any(r["path"] == "docs/keep.md" for r in gm.cmd_search(root, "ZEBRA"))
    html = root / "kb-map.html"
    m = gm.cmd_map(root, html)
    assert m["files"] == len(KEEP)
    body = html.read_text(encoding="utf-8")
    assert "snapshots/excl.md" not in body and "docs/keep.md" in body


def test_one_corpus_number_for_all_commands(tmp_path: Path, gm):
    """invariant: every command reads the corpus through the same definition."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": PREFIXES})
    gm.cmd_index(root)
    lint = gm.cmd_lint(root)
    assert lint["checked"] == gm.cmd_stat(root)["files"] == len(KEEP)
    assert len(list(gm.iter_md(root))) == len(KEEP)


def test_fallback_without_git_respects_scope(tmp_path: Path, gm, monkeypatch):
    """invariant: docs/plans/kb-scope.md#готово-2 — the corpus does not depend on
    git availability."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": PREFIXES})

    def _no_git(*a, **kw):
        raise FileNotFoundError("git недоступен")

    monkeypatch.setattr(gm.subprocess, "run", _no_git)
    assert _rels(root, gm) == KEEP


def test_filter_removal_puts_files_back(tmp_path: Path, gm, monkeypatch):
    """invariant: the matrix can fail — bypassing the filter restores the corpus."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": PREFIXES})
    assert _rels(root, gm) == KEEP
    monkeypatch.setattr(gm, "read_scope", lambda r: [])
    assert _rels(root, gm) == sorted(KEEP + CUT)


# ── формат префикса (решение 16) ───────────────────────────────────────────


def test_slashed_prefix_cuts_subtree_only(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-1 — `snapshots/` не трогает `snapshots-notes/`."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": ["snapshots/"]})
    assert _rels(root, gm) == sorted(KEEP + ["apps/web/tests/expected/shot.md"])


def test_prefix_naming_a_file_works(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-3 — префикс без `/` обязан именовать файл."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": ["docs/keep.md"]})
    assert _rels(root, gm) == sorted(["docs/README.md", "snapshots-notes/keep2.md"]
                                     + CUT)


def test_slashed_prefix_may_name_an_absent_folder(tmp_path: Path, gm):
    """invariant: a slashed folder prefix is a rule, not a promise the folder exists."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": ["nope/"]})
    assert _rels(root, gm) == sorted(KEEP + CUT)


# ── отказы: 5 причин «Готово» 3 + 3 из «Ограничений» (решения 8 и 16) ──────


@pytest.mark.parametrize("payload,needle", [
    ("{oops", "не JSON"),
    ({"exclude_prefixes": "snapshots/"}, "не список"),
    ({"exclude_prefixes": [1]}, "не строка"),
    ({"exclude_prefixes": [], "include": ["docs"]}, "неизвестный ключ"),
    ({"exclude_prefixes": ["snapshots"]}, "обязан заканчиваться '/'"),
    ({"exclude_prefixes": [""]}, "пустой"),
    ({"exclude_prefixes": ["/tmp/x/"]}, "абсолютный"),
    ({"exclude_prefixes": ["docs/../secrets/"]}, "не может уходить из репозитория"),
])
def test_invalid_scope_refuses(tmp_path: Path, gm, payload, needle):
    """spec: docs/plans/kb-scope.md#готово-3 — каждый случай битого scope именован."""
    root = _repo(tmp_path)
    _scope(root, payload)
    with pytest.raises(gm.ScopeError, match=needle):
        list(gm.iter_md(root))


def test_refusal_class_stays_a_named_usage_error(gm):
    """invariant: only a named usage refusal is exit 2, not any ValueError."""
    assert issubclass(gm.ScopeError, gm.LintPathError)
    assert gm.ScopeError is not ValueError


def test_refusal_keeps_stdout_empty_and_exits_two(tmp_path: Path):
    """invariant: a bad scope refuses before any check — stderr, rc 2, empty stdout."""
    root = _repo(tmp_path)
    _scope(root, "{oops")
    for cmd in (["lint"], ["lint", "--strict"], ["index"], ["map", "-o", "m.html"],
                ["search", "ZEBRA"], ["stat", "--json"]):
        r = _run(root, *cmd)
        assert r.returncode == 2, f"{cmd}: rc={r.returncode}, stderr={r.stderr!r}"
        assert r.stdout == "", f"{cmd}: stdout обязан быть пуст, получено {r.stdout!r}"
        assert "gitmark: " in r.stderr and "не JSON" in r.stderr, f"{cmd}: {r.stderr!r}"


def test_valid_scope_does_not_refuse(tmp_path: Path):
    """invariant: a well-formed scope file is not a usage error."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": PREFIXES})
    r = _run(root, "lint", "--strict")
    assert r.returncode in (0, 1), f"rc={r.returncode}, stderr={r.stderr!r}"


# ── строка об исключениях (готово 4) ────────────────────────────────────────


def test_scope_line_appears_with_exclusions(tmp_path: Path):
    """spec: docs/plans/kb-scope.md#готово-4 — литерал строки и числа из фикстуры."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": PREFIXES})
    r = _run(root, "lint")
    assert f"scope: {len(CUT)} файлов исключено по {len(PREFIXES)} префиксам" in r.stdout, r.stdout


def test_no_scope_line_without_a_scope_file(tmp_path: Path):
    """invariant: no scope file means no scope line — silence is not faked as clean."""
    root = _repo(tmp_path)
    r = _run(root, "lint")
    assert "scope:" not in r.stdout, r.stdout


def test_empty_scope_list_still_prints_no_counts(tmp_path: Path):
    """spec: docs/plans/kb-scope.md#готово-4 — пустой excludes не печатает строку."""
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": []})
    r = _run(root, "lint")
    assert "scope:" not in r.stdout, r.stdout


def test_dead_prefix_still_reports_zero(tmp_path: Path):
    """spec: docs/plans/kb-scope.md#готово-4 — строка печатается, когда scope объявлен.

    Мёртвое правило (префикс есть, исключений ноль) остаётся видимым: молчание
    про ноль исключений отличимо от отсутствия scope-файла.
    """
    root = _repo(tmp_path)
    _scope(root, {"exclude_prefixes": ["nope/"]})
    r = _run(root, "lint")
    assert "scope: 0 файлов исключено по 1 префиксам" in r.stdout, r.stdout
    assert r.stdout.rstrip().endswith(")") , f"итог обязан остаться последней строкой: {r.stdout!r}"


def test_refusal_writes_no_files(tmp_path: Path):
    """invariant: a refused run leaves the tree untouched — no index, no map."""
    root = _repo(tmp_path)
    _scope(root, "{oops")
    r = _run(root, "map", "-o", str(root / "m.html"))
    assert r.returncode == 2 and not (root / "m.html").exists(), r.stderr
    r = _run(root, "index")
    assert r.returncode == 2 and not (root / ".gitmark" / "index.db").exists(), r.stderr


def test_scope_file_replacing_folder_refuses(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-3 — «не читается» назван, а не проглочен."""
    root = _repo(tmp_path)
    (root / "gitmark.scope.json").mkdir()
    with pytest.raises(gm.ScopeError, match="не читается"):
        list(gm.iter_md(root))


def test_dangling_symlink_scope_refuses(tmp_path: Path, gm):
    """invariant: a dangling scope symlink is a refusal, not an absent file."""
    root = _repo(tmp_path)
    (root / "gitmark.scope.json").symlink_to(root / "nowhere.json")
    with pytest.raises(gm.ScopeError, match="не читается"):
        list(gm.iter_md(root))


def test_json_scalar_instead_of_object_refuses(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-3 — «ожидался объект» назван."""
    root = _repo(tmp_path)
    _scope(root, '["snapshots/"]')
    with pytest.raises(gm.ScopeError, match="ожидался объект"):
        list(gm.iter_md(root))


def test_deeply_nested_json_is_a_refusal_not_a_traceback(tmp_path: Path):
    """invariant: pathological JSON still exits 2 with empty stdout, no traceback."""
    root = _repo(tmp_path)
    _scope(root, "[" * 20000)
    r = _run(root, "lint")
    assert r.returncode == 2, f"rc={r.returncode}, stderr={r.stderr[-200:]!r}"
    assert r.stdout == ""
    assert "Traceback" not in r.stderr


# ── тикет 02: поле scope в stat --json и две строки при выборке ─────────────


def _repo_mixed(tmp_path: Path) -> Path:
    """Смешанная фикстура: 3 ERR I4 + 2 WARN (I3 в выборке, I5 на каталог).

    `docs/keep.md` и `docs/orphan.md` — будущая выборка; `docs/other.md` и
    `snapshots/shot.md` — вне её; `docs/sub/` без README даёт I5-WARN с
    каталожным path, который не обязан попадать в «вне выборки» никогда.
    """
    return make_git_repo(tmp_path, {
        "docs/README.md": "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n",
        "docs/keep.md": "---\nnode_type: reference\ntitle: Keep\n"
                       "links:\n  relates_to: [README.md]\n---\n\n[битая](./nope.md)\n",
        "docs/orphan.md": "---\nnode_type: reference\ntitle: Orphan\n---\n\n# Orphan\n",
        "docs/other.md": "---\nnode_type: reference\ntitle: Other\n"
                         "links:\n  relates_to: [README.md]\n---\n\n[битая](./nope2.md)\n",
        "docs/sub/x.md": "---\nnode_type: reference\ntitle: X\n"
                         "links:\n  relates_to: [../README.md]\n---\n\n# X\n",
        "snapshots/shot.md": "---\nnode_type: reference\ntitle: Shot\n---\n\n[битая](./nope3.md)\n",
    })


def _counts(stdout: str, prefix: str) -> tuple:
    """(ERR, WARN) из строки вида `в выборке: 1 ERR · 2 WARN`."""
    line = next(l for l in stdout.splitlines() if l.startswith(prefix + ": "))
    err, warn = line.split(": ", 1)[1].split(" · ")
    return int(err.split()[0]), int(warn.split()[0])


def _position(stdout: str, prefix: str) -> int:
    return next(i for i, l in enumerate(stdout.splitlines()) if l.startswith(prefix + ": "))


def test_selection_prints_two_lines(tmp_path: Path):
    """spec: docs/plans/kb-scope.md#готово-5 — находки разделены по выборке."""
    root = _repo_mixed(tmp_path)
    r = _run(root, "lint", "docs/keep.md", "docs/orphan.md")
    in_sel = _counts(r.stdout, "в выборке")
    out_sel = _counts(r.stdout, "вне выборки")
    # независимое ожидание из фикстуры: ERR I4 — keep (внутри), other + shot
    # (снаружи); WARN — orphan I3 внутри (per-file, выбран), docs/sub/ I5 снаружи.
    # Per-file проверки (I1/I2/I3/I6) вне выборки не считаются — контракт ядра,
    # поэтому «вне выборки» = глобальные находки (I4/I5) на остальных путях
    assert in_sel == (1, 1), f"в выборке ожидалось 1 ERR · 1 WARN, факт {in_sel}"
    assert out_sel == (2, 1), f"вне выборки ожидалось 2 ERR · 1 WARN, факт {out_sel}"
    # порядок: «в выборке» → «вне выборки» → итог последним (рецепт tail -1)
    lines = r.stdout.splitlines()
    i_in, i_out = _position(r.stdout, "в выборке"), _position(r.stdout, "вне выборки")
    assert i_out == i_in + 1, f"строки обязаны идти парой подряд: {lines[i_in:i_out + 2]}"
    assert lines[-1].endswith(")") and lines[-1] != lines[i_out], "итог — последняя строка"


def test_dir_finding_stays_outside_selection(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-5 — I5 на каталог не «в выборке»."""
    root = _repo_mixed(tmp_path)
    full = gm.cmd_lint(root)
    sel = gm.cmd_lint(root, ["docs/keep.md", "docs/orphan.md"])
    assert {i[2] for i in full["issues"] if i[1] == "I5"} == {"docs/sub/"}
    assert not [i for i in sel["issues"] if i[1] == "I5" and i[2] in ("docs/keep.md", "docs/orphan.md")]
    # выборка только keep.md: I3 на orphan не считается (per-file вне выборки),
    # поэтому снаружи остаются два I4 и один I5
    assert "в выборке: 1 ERR · 0 WARN" in (out := _run(root, "lint", "docs/keep.md").stdout)
    assert "вне выборки: 2 ERR · 1 WARN" in out


def test_no_selection_lines_without_paths(tmp_path: Path):
    """invariant: docs/plans/kb-scope.md#готово-5 — без путей пар строк нет."""
    root = _repo_mixed(tmp_path)
    r = _run(root, "lint")
    assert "в выборке" not in r.stdout and "вне выборки" not in r.stdout, r.stdout


def test_checked_is_full_corpus_under_selection(tmp_path: Path, gm):
    """invariant: docs/plans/kb-scope.md#готово-5 — выборка не сужает корпус."""
    root = _repo_mixed(tmp_path)
    full = gm.cmd_lint(root)
    sel = gm.cmd_lint(root, ["docs/keep.md"])
    assert sel["checked"] == full["checked"] == 6
    broken = {i[2] for i in full["issues"] if i[1] == "I4"}
    broken_sel = {i[2] for i in sel["issues"] if i[1] == "I4"}
    assert broken == broken_sel == {"docs/keep.md", "docs/other.md", "snapshots/shot.md"}


def test_stat_json_carries_scope(tmp_path: Path):
    """spec: docs/plans/kb-scope.md#готово-7 — поле scope с числами из фикстуры."""
    root = _repo_mixed(tmp_path)
    _scope(root, {"exclude_prefixes": ["snapshots/"]})
    assert _run(root, "index").returncode == 0
    data = json.loads(_run(root, "stat", "--json").stdout)
    assert data["scope"] == {"excluded_files": 1, "prefix_count": 1}, data


def test_stat_json_scope_is_zero_without_file(tmp_path: Path):
    """spec: docs/plans/kb-scope.md#готово-7 — без scope-файла поле на месте с нулями."""
    root = _repo_mixed(tmp_path)
    assert _run(root, "index").returncode == 0
    data = json.loads(_run(root, "stat", "--json").stdout)
    assert data["scope"] == {"excluded_files": 0, "prefix_count": 0}, data


def test_stat_json_scope_present_before_any_index(tmp_path: Path):
    """invariant: docs/plans/kb-scope.md#готово-7 — машинный контракт не исчезает."""
    root = _repo_mixed(tmp_path)
    data = json.loads(_run(root, "stat", "--json").stdout)
    assert data["indexed"] is False and "scope" in data, data


def test_exit_codes_unchanged_under_selection(tmp_path: Path):
    """invariant: выборка не вводит новых кодов — 0 чистый, 1 ERR под --strict,
    2 отказ использования (решение 7 спеки kb-scope)."""
    root = _repo_mixed(tmp_path)
    assert _run(root, "lint", "docs/keep.md", "--strict").returncode == 1
    assert _run(root, "lint", "docs/nope.md", "--strict").returncode == 2
    clean = _repo(tmp_path / "clean")
    _scope(clean, {"exclude_prefixes": ["snapshots/", "apps/"]})
    assert _run(clean, "lint", "--strict").returncode == 0


# ── тикет 03: scope над глобальными проверками — I10 и рёбра графа ─────────


def _repo_chain(tmp_path: Path) -> Path:
    """KB с индексами: docs/, docs/reference/, docs/gen/ и docs/gen/deep/.

    docs/README.md ссылается на docs/gen/ только во frontmatter — I10 смотрит в
    тело, поэтому до срезки находка законна. Ожидание считано по фикстуре, не
    движком: ровно 2 ERR I10 (docs/README.md → docs/gen/, docs/gen/README.md →
    docs/gen/deep/), никаких прочих находок.
    """
    return make_git_repo(tmp_path, {
        "docs/README.md": "---\nnode_type: index\ntitle: KB\n"
                          "links:\n  relates_to: [gen/README.md]\n---\n\n# KB\n\n"
                          "[Справочник](reference/)\n",
        "docs/reference/README.md": "---\nnode_type: index\ntitle: Ref\n---\n\n# Ref\n\n[X](x.md)\n",
        "docs/reference/x.md": "---\nnode_type: reference\ntitle: X\n---\n\n[Индекс](README.md)\n",
        "docs/gen/README.md": "---\nnode_type: index\ntitle: Gen\n---\n\n# Gen\n\n[X](../reference/x.md)\n",
        "docs/gen/deep/README.md": "---\nnode_type: index\ntitle: Deep\n---\n\n# Deep\n",
    })


def _findings(root: Path, gm, code: str) -> list:
    return sorted((i[0], i[2]) for i in gm.cmd_lint(root)["issues"] if i[1] == code)


def _all_findings(root: Path, gm) -> list:
    """Все находки (уровень, код, путь) — сверка, что срез не добавил прочего."""
    return sorted((i[0], i[1], i[2]) for i in gm.cmd_lint(root)["issues"])


def _cut(root: Path, prefixes) -> Path:
    """Записать gitmark.scope.json и обновить индекс: корпус движка = корпус git."""
    _scope(root, {"exclude_prefixes": list(prefixes)})
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    return root


I10_BEFORE = [("ERR", "docs/README.md"), ("ERR", "docs/gen/README.md")]


def test_i10_cut_subtree_silences_the_parent(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-1 — исключённый подраздел вне цепочки.

    До среза находка законна, после — её нет: docs/gen/ больше не KB, и
    родительский индекс не обязан на него ссылаться.
    """
    root = _repo_chain(tmp_path)
    assert _all_findings(root, gm) == [("ERR", "I10", "docs/README.md"),
                                       ("ERR", "I10", "docs/gen/README.md")]
    assert _all_findings(_cut(root, ["docs/gen/"]), gm) == []
    assert _run(root, "lint", "--strict").returncode == 0


def test_i10_cut_index_makes_no_finding_on_itself(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-1 — ни ERR I10 на срезанном README.

    Срезан только docs/gen/README.md, его подраздел docs/gen/deep/ остаётся в
    корпусе: находка на исключённом пути исчезает и новой не появляется — без
    индекса родителя цепочка обрывается, а не додумывается.
    """
    root = _cut(_repo_chain(tmp_path), ["docs/gen/README.md"])
    assert _findings(root, gm, "I10") == []


def test_i10_without_scope_is_untouched(tmp_path: Path, gm):
    """invariant: без scope-файла и по мёртвому префиксу цепочка считается как раньше."""
    root = _repo_chain(tmp_path)
    assert _findings(root, gm, "I10") == I10_BEFORE
    assert _findings(_cut(root, ["nope/"]), gm, "I10") == I10_BEFORE


def test_i10_chain_needs_the_root_index_in_the_corpus(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-1 — без docs/README.md в корпусе цепочки нет."""
    root = _cut(_repo_chain(tmp_path), ["docs/README.md"])
    assert _findings(root, gm, "I10") == []


def test_i10_never_reaches_outside_docs(tmp_path: Path, gm):
    """invariant: I10 остаётся цепочкой docs/ — подраздел вне docs/ не затрагивается.

    `skills/README.md` не ссылается на `skills/kb/`, и это не находка: ни до
    срезки, ни после.
    """
    root = make_git_repo(tmp_path, {
        "docs/README.md": "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n",
        "skills/README.md": "# Skills\n",
        "skills/kb/README.md": "# KB skill\n",
    })
    assert _findings(root, gm, "I10") == []
    assert _findings(_cut(root, ["skills/"]), gm, "I10") == []


def _repo_edge(tmp_path: Path, links_out: bool) -> Path:
    """docs/gen/ как единственный мост к docs/x.md — наружу или только внутрь.

    `links_out=True` — у docs/x.md есть исходящая ссылка в docs/gen/snap.md;
    `links_out=False` — связь docs/x.md была только входящей из docs/gen/.
    До срезки оба дерева чистые: в корпусе все цели на месте.
    """
    body = "[Снапшот](gen/snap.md)\n" if links_out else "# X\n"
    return make_git_repo(tmp_path, {
        "docs/README.md": "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n[Gen](gen/)\n",
        "docs/x.md": "---\nnode_type: reference\ntitle: X\n---\n\n" + body,
        "docs/gen/README.md": "---\nnode_type: index\ntitle: Gen\n---\n\n[X](../x.md)\n",
        "docs/gen/snap.md": "---\nnode_type: reference\ntitle: Snap\n"
                            "links:\n  relates_to: [README.md]\n---\n\n# Snap\n",
    })


def test_edge_to_an_excluded_target_is_not_an_orphan(tmp_path: Path, gm):
    """spec: docs/plans/kb-scope.md#готово-1 — срез не создаёт мнимых сирот.

    docs/x.md ведёт в docs/gen/snap.md: цель вне корпуса, но существует на
    файловой системе — связь настоящая, читатель до неё дойдёт.
    """
    root = _repo_edge(tmp_path, links_out=True)
    assert _all_findings(root, gm) == []
    assert _run(root, "lint", "--strict").returncode == 0
    root = _cut(root, ["docs/gen/"])
    assert _all_findings(root, gm) == []
    assert _run(root, "lint", "--strict").returncode == 0


def test_orphan_of_a_dead_link_target_stays_reported(tmp_path: Path, gm):
    """invariant: I3 остаётся fail-closed — цели нет на ФС, сирота остаётся."""
    root = _repo_edge(tmp_path, links_out=True)
    (root / "docs/gen/snap.md").unlink()
    subprocess.run(["git", "add", "-A"], cwd=root, check=True)
    # цель удалена с диска: `ERR I4` на docs/x.md живёт и до срезки, и после
    # (fs_resolve смотрит на ФС), сиротой x.md становится только после срезки —
    # до неё его спасает входящая связь из docs/gen/README.md, которая в корпусе
    assert _all_findings(root, gm) == [("ERR", "I4", "docs/x.md")]
    assert _all_findings(_cut(root, ["docs/gen/"]), gm) == [("ERR", "I4", "docs/x.md"),
                                                            ("WARN", "I3", "docs/x.md")]


def test_inbound_only_from_a_cut_subtree_stays_an_orphan(tmp_path: Path, gm):
    """invariant: I3 — связность KB решают документы KB, чужое дерево не оправдание.

    Решение оператора (2026-11-11): исходящая связь резолвится по ФС, входящая
    из исключённого поддерева — нет. docs/x.md никуда не ведёт, и единственным
    его связчиком был docs/gen/README.md, который больше не KB.
    """
    root = _repo_edge(tmp_path, links_out=False)
    assert _all_findings(root, gm) == []
    root = _cut(root, ["docs/gen/"])
    assert _all_findings(root, gm) == [("WARN", "I3", "docs/x.md")]


def test_soft_graph_edges_stay_in_the_corpus(tmp_path: Path, gm):
    """invariant: мягкий граф index остаётся по корпусу — ФС-рёбра только для I3.

    Без scope ребро docs/x.md → docs/gen/snap.md в таблице `links` есть; с
    обрезанным docs/gen/ рёбер вне корпуса нет ни у кого.
    """
    import sqlite3

    def edges(root: Path) -> set:
        gm.cmd_index(root)
        con = sqlite3.connect(root / ".gitmark" / "index.db")
        got = set(con.execute("SELECT src, dst FROM links").fetchall())
        con.close()
        return got

    full = _repo_edge(tmp_path / "full", links_out=True)
    assert ("docs/x.md", "docs/gen/snap.md") in edges(full)
    cut = _cut(_repo_edge(tmp_path / "cut", links_out=True), ["docs/gen/"])
    corpus = set(_rels(cut, gm))
    assert corpus == {"docs/README.md", "docs/x.md"}
    got = edges(cut)
    assert all(src in corpus and dst in corpus for src, dst in got), got
    # тот же корпус у `map`: узла и ребра вне выборки в HTML нет
    html = cut / "kb-map.html"
    gm.cmd_map(cut, html)
    body = html.read_text("utf-8")
    assert "docs/gen/snap.md" not in body and "docs/x.md" in body


def test_i10_unreadable_readme_in_corpus_stays_a_finding(tmp_path: Path, gm):
    """invariant: I10 fail-closed — нечитаемый README в корпусе остаётся находкой.

    Гейт-находка 12 переживает переписывание цепочки на корпус: файл в выборке
    есть, а читается не — находка, а не молчаливый пропуск подцепочки. Висячий
    symlink для этого не годится: `git_md_files` берёт только `is_file()`, такой
    путь в корпус не попадает.
    """
    import os
    root = _repo_chain(tmp_path)
    target = root / "docs/reference/README.md"
    target_relative = "docs/reference/README.md"
    target.chmod(0o000)
    if target.exists() and not os.access(target, os.R_OK):
        expected = "unreadable"
    else:
        pytest.skip("права на чтение не снимаются (прогон от root)")
    try:
        found = [i for i in gm.cmd_lint(root)["issues"]
                 if i[1] == "I10" and "не читается" in i[3]]
        assert [i[2] for i in found] == ["docs/reference/README.md"], found
        assert _findings(root, gm, "I10") == sorted(I10_BEFORE + [("ERR", target_relative)])
        # срез узла: README уходит из корпуса — вместе с ним уходит fail-closed
        # находка, а ссылки родителя на docs/reference/ больше не требуется.
        # `git add` тут не нужен и не пройдёт: файл не читается, а scope-файл
        # корпус видит и неотслеживаемым (`ls-files -o`)
        _scope(root, {"exclude_prefixes": ["docs/reference/"]})
        assert _findings(root, gm, "I10") == I10_BEFORE
    finally:
        target.chmod(0o644)


def test_edge_leaving_the_repo_is_not_a_relation(tmp_path: Path, gm):
    """invariant: связь за корнем репозитория сироту не оправдывает — узел вне KB.

    Консервативный gate в `resolve_edge`: `fs_resolve` проверяет такую цель
    «там, куда ведёт» (I4 молчит, файл на месте), но рёбра связности из неё не
    делает — узлы графа не уходят за корень.
    """
    sibling = tmp_path / "sibling"
    sibling.mkdir()
    (sibling / "note.md").write_text("# Note\n", encoding="utf-8")
    root = make_git_repo(tmp_path / "repo", {
        "docs/README.md": "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n",
        "docs/x.md": "---\nnode_type: reference\ntitle: X\n---\n\n"
                     "[Заметка](../../sibling/note.md)\n",
    })
    assert _all_findings(root, gm) == [("WARN", "I3", "docs/x.md")]


def test_i10_chain_normalizes_forms_once(tmp_path: Path, gm):
    """invariant: I10 — цель в теле и путь README сверяются в NFC (оба направления).

    Подраздел записан на диске в NFD (`de\u0301cor`), ссылка в индексе — в NFC
    (`d\u00e9cor`). Имя файла для чтения берётся из git как есть, сравнение —
    нормализованное: на базе этот кейс даёт ложный `ERR I10` («Ограничения»
    спеки: нормализация целей — NFC). `ERR I4` остаётся: строгая адресность
    `fs_resolve` проверяет байтовое имя на диске и в рамки среза не входит.
    """
    nfd, nfc = "de\u0301cor", "d\u00e9cor"
    assert nfd != nfc
    root = make_git_repo(tmp_path, {
        "docs/README.md": "---\nnode_type: index\ntitle: KB\n---\n\n# KB\n\n"
                          f"[Декор]({nfc}/)\n",
        f"docs/{nfd}/README.md": "---\nnode_type: index\ntitle: Decor\n---\n\n# Decor\n",
    })
    assert _findings(root, gm, "I10") == []
    assert _all_findings(root, gm) == [("ERR", "I4", "docs/README.md")]
