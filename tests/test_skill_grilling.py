"""Contract for the grilling skill (workflow-skills ticket 01).

The bundle must be discoverable as ``<root>/grilling/SKILL.md`` and carry the
phase-1 mechanism: design tree, frontier rounds with numbered questions and a
recommended answer, facts-vs-decisions split, and the spec exit at the plan gate.

spec: docs/plans/workflow-skills.md#готово — skills/grilling/SKILL.md
spec: docs/plans/workflow-skills.md#ограничения — no strict-profile apparatus,
autonomous flag is out of scope for v1
invariant: the agent never answers for the operator
invariant: skill texts name no harness root (harness-agnostic)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "grilling" / "SKILL.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
REQUIRED_PHRASES = (
    "дерево дизайна",
    "фронтир",
    "рекомендованный ответ",
    "факты — работа агента",
    "сломал скилл",
    "молчание оператора — не согласие",
    "docs/plans/<slug>.md",
    "цель / готово / рамки / ограничения / контекст",
    "план-гейт",
    "один вопрос на тикет",
    "вне рамок",
    "не выдумывай",
)
FORBIDDEN = ("challenger", "provenance", "реестр")


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

    lowered = re.sub(r"\s+", " ", body.lower())
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for term in FORBIDDEN:
        if re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE):
            errors.append(f"forbidden strict-profile entity {term!r}")
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/workflow-skills.md#готово — skills/grilling/SKILL.md."""
    assert SKILL.is_file(), "the grilling skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "grilling"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_carries_the_interview_mechanism():
    """spec: docs/plans/workflow-skills.md#готово — rounds, frontier, exit, gate."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    for phrase in ("дерево дизайна", "фронтир", "рекомендованный ответ",
                   "docs/plans/<slug>.md", "цель / готово / рамки / ограничения / контекст",
                   "план-гейт"):
        assert phrase in lowered, f"the mechanism phrase {phrase!r} is missing"


def test_agent_never_answers_for_the_operator():
    """invariant: the agent never answers for the operator; silence is not consent."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "факты — работа агента" in lowered
    assert "сломал скилл" in lowered
    assert "молчание оператора — не согласие" in lowered


def test_slicing_handoff_follows_the_canon():
    """spec: docs/decisions/ontoship-core.md#три фазы — one ask question per ticket."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    assert "один вопрос на тикет" in body


def test_autonomous_flag_is_out_of_scope_for_v1():
    """spec: docs/plans/workflow-skills.md#решения план-гейта — flag deferred."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "автономный режим" in lowered
    assert "вне рамок" in lowered


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: harness-agnostic — no harness-specific skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    assert root not in text
    leaked = text + f"\nInstall into {root}/skills instead.\n"
    assert any(root in error for error in _contract_errors(leaked))


@pytest.mark.parametrize("term", FORBIDDEN)
def test_skill_omits_strict_profile_entities(term: str):
    """spec: docs/decisions/ontoship-core.md#вне умолчания — no strict profile."""
    text = SKILL.read_text("utf-8")
    assert not re.search(rf"\b{re.escape(term)}\b", text, re.IGNORECASE), \
        f"SKILL.md mentions the strict-profile entity {term!r}"


def test_contract_check_can_fail():
    """invariant: the contract check rejects a missing phrase and a forbidden entity."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_phrase = re.sub("дерево дизайна", "список идей", text, flags=re.IGNORECASE)
    assert missing_phrase != text
    assert any("дерево дизайна" in error for error in _contract_errors(missing_phrase))

    leaked_entity = text.replace("# Skill: grilling",
                                 "# Skill: grilling\n\nApparatus: challenger.", 1)
    assert leaked_entity != text
    assert any("challenger" in error for error in _contract_errors(leaked_entity))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))
