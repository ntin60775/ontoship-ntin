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