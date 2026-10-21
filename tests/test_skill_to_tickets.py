"""Contract for the to-tickets skill (workflow-skills ticket 02).

The bundle must be discoverable as ``<root>/to-tickets/SKILL.md``, carry the
phase-2 slicing mechanism (tracer-bullet vertical slices, demo path, base-commit
criteria, blocking edges, quiz) and stay user-invoked: the frontmatter pins
``disable-model-invocation: true``.

spec: docs/plans/workflow-skills.md#готово — skills/to-tickets/SKILL.md
spec: docs/decisions/ontoship-core.md#три фазы — one ask question per ticket,
criteria fall on the base commit, no file:line anchors
invariant: the model never invokes this skill
invariant: skill texts name no harness root (harness-agnostic)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "to-tickets" / "SKILL.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
ANCHOR_RE = re.compile(r"\b[\w-]+(?:\.[\w-]+)+:\d+")
REQUIRED_PHRASES = (
    "вертикальные срезы",
    "демо-путь",
    "базовом коммите",
    "блокирующие рёбра",
    "квиз",
    "file:line",
    "что я могу показать",
    ".scratch/<slug>/issues/",
    "один вопрос на тикет",
    "принять как предложено",
    "вызывает пользователь",
)


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
    if fields.get("disable-model-invocation", "").lower() != "true":
        errors.append("frontmatter: disable-model-invocation must be true "
                      "(the model never invokes this skill)")

    lowered = re.sub(r"\s+", " ", body.lower())
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    anchor = ANCHOR_RE.search(text)
    if anchor:
        errors.append(f"body: file:line anchor {anchor.group(0)!r}")
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/workflow-skills.md#готово — skills/to-tickets/SKILL.md."""
    assert SKILL.is_file(), "the to-tickets skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "to-tickets"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_is_user_invoked_only():
    """invariant: the model never invokes this skill (canon, «Три фазы»)."""
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields.get("disable-model-invocation", "").lower() == "true"


def test_skill_carries_the_slicing_mechanism():
    """spec: docs/plans/workflow-skills.md#готово — slices, demo path, quiz."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    for phrase in ("вертикальные срезы", "демо-путь", "базовом коммите",
                   "блокирующие рёбра", "квиз", "что я могу показать"):
        assert phrase in lowered, f"the slicing phrase {phrase!r} is missing"


def test_criteria_fall_on_the_base_commit():
    """spec: docs/decisions/ontoship-core.md#три фазы — criteria fail on base."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "падают на базовом коммите" in lowered
    assert "что я могу показать" in lowered


def test_no_file_line_anchors():
    """spec: docs/decisions/ontoship-core.md#три фазы — anchors rot."""
    text = SKILL.read_text("utf-8")
    assert ANCHOR_RE.search(text) is None, "the skill text carries a file:line anchor"
    assert "file:line" in text, "the rule against anchors must be stated"


def test_tickets_publish_location():
    """spec: docs/plans/workflow-skills.md#готово — .scratch or project tracker."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    assert ".scratch/<slug>/issues/" in body
    assert "tickets/<slug>/" in body


def test_slicing_handoff_follows_the_canon():
    """spec: docs/decisions/ontoship-core.md#три фазы — one ask question per ticket."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "один вопрос на тикет" in lowered
    assert "принять как предложено" in lowered
    assert "изменить формулировку" in lowered
    assert "режут план; тикет принимают или нет" in lowered


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: harness-agnostic — no harness-specific skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    assert root not in text
    leaked = text + f"\nInstall into {root}/skills instead.\n"
    assert any(root in error for error in _contract_errors(leaked))


def test_contract_check_can_fail():
    """invariant: the contract check rejects a missing flag and a real anchor."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_flag = "\n".join(line for line in text.splitlines()
                             if not line.startswith("disable-model-invocation:"))
    assert missing_flag != text
    assert any("disable-model-invocation" in error
               for error in _contract_errors(missing_flag))

    anchored = text.replace("## Срезы", "## Срезы\n\nСмотри `skills/kb-search/gitmark.py:42`.", 1)
    assert anchored != text
    assert any("gitmark.py:42" in error for error in _contract_errors(anchored))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))
