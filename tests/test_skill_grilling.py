"""Contract for the grilling skill (workflow-skills ticket 01).

The bundle must be discoverable as ``<root>/grilling/SKILL.md`` and carry the
phase-1 mechanism: design tree, frontier rounds with numbered questions and a
recommended answer, facts-vs-decisions split, and the spec exit at the plan gate.
The frontier additionally asks the price-of-evidence question of
evidence-verification ticket 03 before the spec is written (spec decision 5).
The exit section additionally carries the control read of the draft spec
before the plan gate of evidence-verification ticket 04 (spec decision 7).

spec: docs/plans/workflow-skills.md#готово — skills/grilling/SKILL.md
spec: docs/plans/workflow-skills.md#ограничения — no strict-profile apparatus,
autonomous flag is out of scope for v1
spec: docs/plans/evidence-verification.md#готово — во фронтир входит вопрос
«как каждый пункт будет доказываться и что будет дорого» до написания спеки
spec: docs/plans/evidence-verification.md#готово — контрольная вычитка спеки
перед план-гейтом: носители шагов, условные решения, числа, противоречия
между разделами
invariant: docs/decisions/ontoship-core.md#три фазы — the agent never answers for the operator
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
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
    "ask-инструмент хоста",
    "поле вопроса несёт само решение",
    "не свидетельства",
    "вне рамок",
    "не выдумывай",
)
FORBIDDEN = ("challenger", "provenance", "реестр")
EVIDENCE_PHRASES = (
    "цена доказательства входит во фронтир",
    "задай вопрос",
    "как каждый пункт будет доказываться и что будет дорого",
    "до написания спеки",
    "переформулируются или разрезаются на фронтире",
)
EVIDENCE_CONTRADICTION = "после написания спеки"
FRONTIER_HEADING = "дерево дизайна и фронтир"
EXIT_HEADING = "готовность и выход"
PROOFREAD_PHRASES = (
    "контрольная вычитка",
    "перед план-гейтом",
    "носители шагов",
    "условные решения",
    "числа",
    "противоречия между разделами",
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


def _section(body: str, heading: str) -> str:
    """Body of one ``## `` section matched case-insensitively by its heading."""
    lowered = body.lower()
    start = lowered.find(f"## {heading}")
    if start < 0:
        return ""
    return body[start:].split("\n## ", 1)[0]


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
    frontier = re.sub(r"\s+", " ", _section(body, FRONTIER_HEADING).lower())
    for phrase in EVIDENCE_PHRASES:
        if phrase not in frontier:
            errors.append(f"frontier: missing evidence phrase {phrase!r}")
    if EVIDENCE_CONTRADICTION in frontier:
        errors.append(f"frontier: contradictory phrase {EVIDENCE_CONTRADICTION!r}")
    proofread = re.sub(r"\s+", " ", _section(body, EXIT_HEADING).lower())
    for phrase in PROOFREAD_PHRASES:
        if phrase not in proofread:
            errors.append(f"exit: missing proofread phrase {phrase!r}")
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
                   "ask-инструмент хоста",
                   "docs/plans/<slug>.md", "цель / готово / рамки / ограничения / контекст",
                   "план-гейт"):
        assert phrase in lowered, f"the mechanism phrase {phrase!r} is missing"


def test_frontier_goes_through_the_host_ask_tool():
    """invariant: docs/decisions/ontoship-core.md#три фазы — frontier reaches the
    operator through the host ask tool, not as a wall of chat questions."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "ask-инструмент хоста" in lowered
    assert "полотно вопросов в чате — дефект" in lowered


def test_ask_question_field_carries_the_decision_not_the_report():
    """invariant: docs/decisions/ontoship-core.md#три фазы — the ask question
    field carries the decision, not the report; evidence stays in chat before
    the call, option descriptions carry consequences."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "поле вопроса несёт само решение" in lowered
    assert "идут в чат текстом перед вызовом" in lowered
    assert "следствие выбора, не свидетельства" in lowered


def test_agent_never_answers_for_the_operator():
    """invariant: docs/decisions/ontoship-core.md#три фазы — the agent never answers for the operator; silence is not consent."""
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


def test_frontier_asks_the_price_of_evidence():
    """spec: docs/plans/evidence-verification.md#готово — во фронтир входит
    вопрос «как каждый пункт будет доказываться и что будет дорого» — до
    написания спеки; дорогие пункты переформулируются или разрезаются на
    фронтире (решение 5). Проверяется по месту: фразы ищутся внутри раздела
    «Дерево дизайна и фронтир», не по всему телу скилла."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = re.sub(r"\s+", " ", _section(body, FRONTIER_HEADING).lower())
    for phrase in EVIDENCE_PHRASES:
        assert phrase in section, f"the phrase {phrase!r} is missing from the frontier section"
    assert EVIDENCE_CONTRADICTION not in section, \
        "the frontier section must not carry the contradicting wording"


def test_evidence_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check can fail: потеря вопроса, сдвиг момента, отрицание
    членства во фронтире и потеря императива красят контракт grilling
    (мутационные пробы)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_price = text.replace("и что будет дорого", "и сколько это стоит", 1)
    assert no_price != text
    assert any("как каждый пункт будет доказываться" in error
               for error in _contract_errors(no_price))

    late = text.replace("до написания спеки", "после написания спеки", 1)
    assert late != text
    assert any("до написания спеки" in error for error in _contract_errors(late))

    no_member = text.replace("входит во фронтир", "не входит во фронтир", 1)
    assert no_member != text
    assert any("цена доказательства входит во фронтир" in error
               for error in _contract_errors(no_member))

    no_imperative = text.replace("Задай вопрос", "Обсуди", 1)
    assert no_imperative != text
    assert any("задай вопрос" in error for error in _contract_errors(no_imperative))


def test_spec_gets_a_control_read_before_the_plan_gate():
    """spec: docs/plans/evidence-verification.md#готово — контрольная вычитка
    спеки перед план-гейтом: носители шагов, условные решения, числа,
    противоречия между разделами (решение 7). Фразы ищутся внутри раздела
    «Готовность и выход», не по всему телу скилла."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = re.sub(r"\s+", " ", _section(body, EXIT_HEADING).lower())
    for phrase in PROOFREAD_PHRASES:
        assert phrase in section, \
            f"the phrase {phrase!r} is missing from the exit section"


def test_proofread_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check can fail: потеря названия шага, сдвиг момента и выпадение
    элемента перечня красят контракт grilling (мутационные пробы)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_step = text.replace("Контрольная вычитка", "Финальный просмотр", 1)
    assert no_step != text
    assert any("контрольная вычитка" in error
               for error in _contract_errors(no_step))

    late = text.replace("перед план-гейтом", "после план-гейта", 1)
    assert late != text
    assert any("перед план-гейтом" in error for error in _contract_errors(late))

    no_carriers = text.replace("носители шагов", "шаги", 1)
    assert no_carriers != text
    assert any("носители шагов" in error
               for error in _contract_errors(no_carriers))

    no_contradictions = text.replace("противоречия между разделами",
                                     "несостыковки", 1)
    assert no_contradictions != text
    assert any("противоречия между разделами" in error
               for error in _contract_errors(no_contradictions))


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific skill root in skill texts."""
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
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the contract check rejects a missing phrase and a forbidden entity."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_phrase = re.sub("дерево дизайна", "список идей", text, flags=re.IGNORECASE)
    assert missing_phrase != text
    assert any("дерево дизайна" in error for error in _contract_errors(missing_phrase))

    stuffed = text.replace("Поле вопроса несёт само решение",
                           "Поле вопроса несёт отчёт и доказательства", 1)
    assert stuffed != text
    assert any("поле вопроса несёт само решение" in error
               for error in _contract_errors(stuffed))

    leaked_entity = text.replace("# Skill: grilling",
                                 "# Skill: grilling\n\nApparatus: challenger.", 1)
    assert leaked_entity != text
    assert any("challenger" in error for error in _contract_errors(leaked_entity))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))
