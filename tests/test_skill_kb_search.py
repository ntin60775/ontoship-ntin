"""Contract for the user-facing kb-search skill.

The skill is a directory bundle beside the engine. DSH discovers it as
``<root>/<name>/SKILL.md`` and requires YAML ``name`` and ``description``; these
checks pin that and the ticket-02 surface, not the prose.

spec: docs/plans/core-kb.md#рамки — skills/kb-search/SKILL.md
spec: docs/plans/core-kb.md#ограничения — DSH frontmatter; no inventory/serve/registry,
no provenance, Reel, acceptance chord
invariant: docs/plans/core-kb.md#рамки — the skill reports only what the engine returns
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "kb-search" / "SKILL.md"
SCOPE_HEADING = "## KB-корпус и `gitmark.scope.json`"
SCOPE_LINE = "scope: <N> файлов исключено по <K> префиксам"
REINDEX_ANCHORS = ("Правка `gitmark.scope.json`", "обязателен `index`")
COMMANDS = ("index", "search", "map", "stat", "version")
FORBIDDEN = ("inventory", "serve", "registry", "provenance", "reel", "acceptance chord")
DESCRIPTION_MAX = 500
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")


def _parse(text: str) -> tuple[dict[str, str], str]:
    """Parse the simple single-line YAML frontmatter this skill uses."""
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        raise ValueError("SKILL.md must start with YAML frontmatter")
    try:
        close = lines.index("---", 1)
    except ValueError:
        raise ValueError("unterminated YAML frontmatter") from None
    fields: dict[str, str] = {}
    for line in lines[1:close]:
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        key, sep, value = line.partition(":")
        if not sep:
            raise ValueError(f"frontmatter line is not a key: {line!r}")
        fields[key.strip()] = value.strip()
    return fields, "\n".join(lines[close + 1:])


def _unquote(value: str) -> str:
    """Strip matching YAML quotes; the skill keeps its description quoted."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _contract_errors(text: str) -> list[str]:
    """Return every violated skill contract; empty means the skill is sound."""
    try:
        fields, body = _parse(text)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    name = fields.get("name", "")
    raw_description = fields.get("description", "")
    description = _unquote(raw_description)
    if not name:
        errors.append("frontmatter: missing name")
    elif not NAME_RE.fullmatch(name):
        errors.append(f"frontmatter: invalid kebab-case name {name!r}")
    if not description:
        errors.append("frontmatter: missing description")
    elif len(description) > DESCRIPTION_MAX:
        errors.append(f"frontmatter: description is {len(description)} chars "
                      f"(catalog cap {DESCRIPTION_MAX})")
    if ": " in description and not (raw_description.startswith('"')
                                    and raw_description.endswith('"')):
        errors.append("frontmatter: description contains ': ' and must be quoted")
    for command in COMMANDS:
        if f"gitmark.py {command}" not in body:
            errors.append(f"body: missing command {command!r}")
    if "--json" not in body:
        errors.append("body: missing --json contract")
    if ".gitmark/" not in body:
        errors.append("body: missing derived-artifact rule for .gitmark/")
    lowered = re.sub(r"\s+", " ", body.lower())
    for phrase in ("нет индекса", "ничего не найдено", "не выдумывай"):
        if phrase not in lowered:
            errors.append(f"body: missing honest-degradation phrase {phrase!r}")
    for term in FORBIDDEN:
        if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
            errors.append(f"forbidden entity {term!r}")
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/core-kb.md#рамки — skills/kb-search/SKILL.md."""
    assert SKILL.is_file(), "the user-facing skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "kb-search"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_description_with_a_colon_stays_valid_yaml():
    """invariant: docs/plans/core-kb.md#ограничения — unquoted ': ' in the description drops the skill from the DSH catalog."""
    fields, _ = _parse(SKILL.read_text("utf-8"))
    raw = fields["description"]
    assert ": " in _unquote(raw)
    assert raw.startswith('"') and raw.endswith('"')


def test_skill_names_the_kb_search_commands_and_json_contract():
    """spec: docs/plans/core-kb.md#цель — index/search/map/stat/version, --json."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    for command in COMMANDS:
        assert f"gitmark.py {command}" in body, f"{command} is not runnable from the body"
    assert "search \"canon\" --json" in body
    assert ".gitmark/" in body
    assert ".agents/skills" in body


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """spec: docs/plans/harness-agnostic.md#готово — the universal root only;
    .zcode/skills is back on the ban list: the marketplace-plugin channel
    left the project with the ZCode purge."""
    text = SKILL.read_text("utf-8")
    assert root not in text
    leaked = text + f"\nInstall into {root}/skills instead.\n"
    assert any(root in error for error in _contract_errors(leaked))


@pytest.mark.parametrize("term", FORBIDDEN)
def test_skill_omits_a_forbidden_entity(term: str):
    """spec: docs/plans/core-kb.md#ограничения — no registry/inventory/serve/provenance."""
    text = SKILL.read_text("utf-8")
    assert not re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE), \
        f"SKILL.md mentions the out-of-scope entity {term!r}"


def test_skill_degrades_honestly():
    """invariant: docs/plans/core-kb.md#рамки — the skill reports only what the engine returns."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "нет индекса" in lowered
    assert "gitmark.py index" in body
    assert "ничего не найдено" in lowered
    assert "не выдумывай" in lowered


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the contract check rejects a missing command and a forbidden entity."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_command = text.replace("gitmark.py map", "gitmark.py overview", 1)
    assert missing_command != text
    assert any("map" in error for error in _contract_errors(missing_command))

    leaked_entity = text.replace("# Поиск по KB", "# Поиск по KB\n\nRun `inventory`.", 1)
    assert leaked_entity != text
    assert any("inventory" in error for error in _contract_errors(leaked_entity))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))

    unquoted_description = "\n".join(
        "description: " + _unquote(line[len("description: "):])
        if line.startswith("description: ") else line
        for line in text.splitlines())
    assert unquoted_description != text
    assert any("must be quoted" in error
               for error in _contract_errors(unquoted_description))


# ── the scope rule: full text lives in this skill (kb-scope decision 13) ───


def _scope_section(text: str) -> str:
    """The scope section body: from its heading to the next `## ` heading."""
    start = text.find(SCOPE_HEADING)
    if start < 0:
        return ""
    rest = text[start + len(SCOPE_HEADING):]
    end = rest.find("\n## ")
    return rest if end < 0 else rest[:end]


def _scope_contract_errors(text: str) -> list[str]:
    """Every violated scope-rule anchor; empty means the carrier is complete.

    Anchors come from the spec literals (docs/plans/kb-scope.md «Готово» 3/4/8,
    decisions 13/16/17/18/19), not from the engine code.
    """
    section = _scope_section(text)
    if not section:
        return [f"scope: missing section {SCOPE_HEADING!r}"]
    flat = re.sub(r"\s+", " ", section)
    errors: list[str] = []
    needles = (
        ("carrier file", "gitmark.scope.json"),
        ("root placement", "в корне репозитория"),
        ("single key", "единственный ключ `exclude_prefixes`"),
        ("trailing slash", "заканчиваться `/`"),
        ("file prefix", "существующий файл"),
        ("refusal stderr", "stderr"),
        ("refusal exit", "exit 2"),
        ("refusal empty stdout", "stdout пуст"),
        ("refusal before checks", "ни одна проверка не выполнена"),
        ("scope line literal", SCOPE_LINE),
        ("zero exclusions visible", "при нуле исключённых"),
        ("stat scope field", "поле `scope`"),
        ("seam symbol", "шов `iter_corpus`"),
        ("facade named", "фасад"),
        ("I10 by corpus", "`I10` (`index_chain_issues`)"),
        ("I10 chain absent", "цепочки нет"),
        ("I3 filesystem resolve", "`I3` (`resolve_edge`)"),
        ("I3 fs_resolve", "`fs_resolve`"),
        ("I3 incoming link", "Входящая связь из исключённого поддерева сироту не"),
        ("I3 outside root", "за корнем репозитория"),
        ("reindex obligation", "обязателен `index`"),
    )
    for label, needle in needles:
        if needle not in flat:
            errors.append(f"scope: missing {label} ({needle!r})")
    for command in ("index", "search", "stat", "map", "lint"):
        if command not in flat:
            errors.append(f"scope: corpus not shared with {command!r}")
    if re.search(r"\d+\s+отказывающ", flat):
        errors.append("scope: refusal reasons carry a count (must stay neutral)")
    if re.search(r"gitmark\.py:\d+", flat):
        errors.append("scope: code place named by line, not by symbol")
    return errors


def test_skill_carries_the_full_scope_rule():
    """spec: docs/plans/kb-scope.md#готово-8 — the full corpus/scope rule lives
    in skills/kb-search/SKILL.md (decision 13), including decisions 18–19."""
    assert _scope_contract_errors(SKILL.read_text("utf-8")) == []


@pytest.mark.parametrize("mutation, label", [
    (lambda t: t.replace(SCOPE_HEADING, "## Корпус", 1), "missing section"),
    (lambda t: t.replace("шов `iter_corpus`", "шов `iter_md`", 1), "seam symbol"),
    (lambda t: t.replace(SCOPE_LINE, "scope: исключено несколько файлов", 1),
     "scope line literal"),
    (lambda t: t.replace("обязателен\n`index`", "желателен\n`index`", 1),
     "reindex obligation"),
    (lambda t: t.replace("цепочки нет и проверять нечего", "цепочка есть", 1),
     "I10 chain absent"),
    (lambda t: t.replace("Входящая связь из исключённого поддерева сироту не",
                         "Связь из поддерева", 1), "I3 incoming link"),
    (lambda t: t.replace("Отказывающие причины:",
                         "12 отказывающих причин:", 1), "count"),
    (lambda t: t.replace("exit 2, stdout пуст", "exit 1, stdout пуст", 1),
     "refusal exit"),
])
def test_scope_contract_can_fail(mutation, label):
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    scope contract reddens on a lost or drifted anchor."""
    text = SKILL.read_text("utf-8")
    assert _scope_contract_errors(text) == []
    mutated = mutation(text)
    assert mutated != text, "mutation did not touch the carrier"
    assert any(label in error for error in _scope_contract_errors(mutated))


def _reindex_errors(text: str) -> list[str]:
    flat = re.sub(r"\s+", " ", text)
    return [f"reindex: missing anchor {anchor!r}"
            for anchor in REINDEX_ANCHORS if anchor not in flat]


def test_reindex_after_scope_edit_is_obliged_by_both_carriers():
    """spec: docs/plans/kb-scope.md#готово-8 — AGENTS.md «Сопровождение» and the
    skill both oblige `index` after a gitmark.scope.json edit (panel finding,
    operator decision 2026-11-10)."""
    agents = (REPO / "AGENTS.md").read_text("utf-8")
    assert _reindex_errors(agents) == []
    assert _reindex_errors(SKILL.read_text("utf-8")) == []


def test_reindex_obligation_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — a
    weakened obligation in either carrier reddens the anchor check."""
    carriers = ((REPO / "AGENTS.md").read_text("utf-8"),
                SKILL.read_text("utf-8"))
    for text in carriers:
        assert _reindex_errors(text) == []
        flat = re.sub(r"\s+", " ", text)
        weakened = flat.replace("обязателен `index`", "желателен `index`", 1)
        assert weakened != flat
        assert any("обязателен" in error for error in _reindex_errors(weakened))
