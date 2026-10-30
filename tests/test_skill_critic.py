"""Contract for the critic skill (review-config ticket 03).

The bundle must be discoverable as ``<root>/critic/SKILL.md`` and carry the
plan-critic contract: a model-invoked skill (no ``disable-model-invocation``)
the agent launches right after the unit's last ticket is accepted, before
the first ship — one run per unit, reading the spec and every ticket whole,
on a model that differs from the session model with no fallback, reporting
findings to the operator before the first ship and never re-asking plan-gate
decisions. The checklist additionally carries the two evidence items of
evidence-verification ticket 02: the price question — which «Готово» items
will be expensive to prove and could be simplified or split before code —
and the coverage check by carriers named in the «Готово» lines of new specs
(decisions 2 and 5).

spec: docs/plans/review-config.md#готово — skills/critic/SKILL.md, модельный
      скилл критика: запуск сразу после приёмки последнего тикета, чек-лист,
      один прогон на юнит, модель ≠ сессионная, без фолбэка
spec: docs/plans/evidence-verification.md#готово — критик спрашивает про
      дорогую верификацию и сверяет носители по строкам новых спек
spec: docs/decisions/ontoship-core.md#три фазы — критик плана: находки
      оператору до ship, решения план-гейта не перепрашиваются
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "critic" / "SKILL.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
CHECKLIST = ("покрытость", "связность", "рёбра", "демо-пути", "честность критериев")
EVIDENCE_PHRASES = (
    "дорого доказывать",
    "упростить или разрезать до кода",
    "по носителям, названным в строках",
    "новых спек",
)
REQUIRED_PHRASES = (
    "сразу после приёмки последнего тикета",
    "до первого ship",
    "не командой оператора",
    "один прогон на юнит",
    "спеку",
    "тикеты юнита целиком",
    "артефакты",
    "не ход исполнения",
    "отличаться от модели сессии",
    "нет фолбэка на модель сессии",
    ".agents/config.toml",
    "решения план-гейта не перепрашиваются",
    "находки оператору до первого ship",
    "docs/plans/<slug>.md",
    "docs/decisions/ontoship-core.md",
    "приоритет",
    "зацепка",
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


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


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
    if "disable-model-invocation" in fields:
        errors.append("frontmatter: disable-model-invocation must be absent — "
                      "the critic is a model-invoked skill")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for phrase in EVIDENCE_PHRASES:
        if phrase not in lowered:
            errors.append(f"checklist: missing evidence phrase {phrase!r}")
    for item in CHECKLIST:
        if item not in lowered:
            errors.append(f"checklist: missing {item!r}")
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/review-config.md#готово — skills/critic/SKILL.md."""
    assert SKILL.is_file(), "the critic skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "critic"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_is_model_invoked():
    """spec: docs/plans/review-config.md#готово — критик — модельный скилл:
    без disable-model-invocation, агент запускает его сам."""
    fields, body = _parse(SKILL.read_text("utf-8"))
    assert "disable-model-invocation" not in fields
    lowered = _normalized_lower(body)
    assert "агент запускает" in lowered
    assert "один прогон на юнит" in lowered
    assert "до первого ship" in lowered
    assert "не командой оператора" in lowered


def test_model_must_differ_from_the_session_model_with_no_fallback():
    """spec: docs/plans/review-config.md#готово — модель критика из
    .agents/config.toml, сверка при запуске: ≠ сессионная, иначе остановка;
    фолбэка нет (решение 14)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert ".agents/config.toml" in lowered
    assert "отличаться от модели сессии" in lowered
    assert "остановка и вопрос оператору" in lowered
    assert "нет фолбэка на модель сессии" in lowered


def test_critic_reads_artifacts_not_the_run():
    """spec: docs/plans/review-config.md#готово — независимость: роль не видит
    хода исполнения, она читает артефакты."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "артефакты" in lowered
    assert "не ход исполнения" in lowered
    assert "спеку" in lowered
    assert "тикеты юнита целиком" in lowered


def test_checklist_covers_the_five_spec_items():
    """spec: docs/plans/review-config.md#готово — чек-лист критика: покрытость
    «Готово», связность, рёбра, демо-пути, честность критериев."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    for item in CHECKLIST:
        assert item in lowered, f"checklist item {item!r} is missing"


def test_checklist_asks_the_price_of_evidence():
    """spec: docs/plans/evidence-verification.md#готово — в чек-лист входит
    вопрос: какие пункты «Готово» будет дорого доказывать и нельзя ли
    упростить или разрезать до кода (решение 5)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "дорого доказывать" in lowered
    assert "упростить или разрезать до кода" in lowered


def test_coverage_is_verified_by_carriers_of_new_specs():
    """spec: docs/plans/evidence-verification.md#готово — покрытость «Готово»
    сверяется по носителям, названным в строках новых спек (решение 2)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "по носителям, названным в строках" in lowered
    assert "новых спек" in lowered


def test_evidence_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check can fail: потеря вопроса о цене доказательства или сверки
    носителей красит контракт критика."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_price = text.replace("дорого доказывать", "дорого проверять", 1)
    assert no_price != text
    assert any("дорого доказывать" in error
               for error in _contract_errors(no_price))

    no_split = text.replace("упростить или разрезать до кода", "упростить", 1)
    assert no_split != text
    assert any("упростить или разрезать до кода" in error
               for error in _contract_errors(no_split))

    no_carriers = text.replace("по носителям, названным в строках",
                               "по носителям из тикетов", 1)
    assert no_carriers != text
    assert any("по носителям, названным в строках" in error
               for error in _contract_errors(no_carriers))

    # The description also says «новых спек»; the mutation must hit the body
    # checklist, so it targets the body-only sentence opening.
    old_specs_too = text.replace("У новых спек", "У всех спек", 1)
    assert old_specs_too != text
    assert any("новых спек" in error
               for error in _contract_errors(old_specs_too))


def test_findings_go_to_the_operator_before_the_first_ship():
    """spec: docs/decisions/ontoship-core.md#три фазы — находки идут оператору
    до ship."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "находки оператору до первого ship" in lowered
    assert "приоритет" in lowered
    assert "зацепка" in lowered


def test_plan_gate_decisions_are_not_reasked():
    """spec: docs/plans/review-config.md#ограничения — критик не перевыбирает
    решения план-гейта."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "решения план-гейта не перепрашиваются" in lowered


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check rejects a model-invocation flag, a lost refusal, a lost
    checklist item, a leaked harness root and a missing name."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    model_locked = text.replace("---\n", "---\ndisable-model-invocation: true\n", 1)
    assert model_locked != text
    assert any("disable-model-invocation" in error
               for error in _contract_errors(model_locked))

    no_refusal = text.replace("нет фолбэка на модель сессии", "фолбэк запрещён", 1)
    assert no_refusal != text
    assert any("нет фолбэка на модель сессии" in error
               for error in _contract_errors(no_refusal))

    # The word sits in the description and in the checklist item body; the
    # mutation must remove every occurrence or the check stays green.
    no_edge_item = text.replace("рёбра", "связи").replace("Рёбра", "Связи")
    assert no_edge_item != text
    assert any("рёбра" in error for error in _contract_errors(no_edge_item))

    leaked_install_root = text + "\nЗапусти критика из .zcode/skills.\n"
    assert any(".zcode" in error for error in _contract_errors(leaked_install_root))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))

    silent_launch = text.replace("сразу после приёмки последнего тикета",
                                 "после влития всех тикетов", 1)
    assert silent_launch != text
    assert any("сразу после приёмки последнего тикета" in error
               for error in _contract_errors(silent_launch))


@pytest.mark.parametrize(
    ("needle", "replacement"),
    [
        ("спеку", "план"),
        ("артефакты", "материалы"),
        ("приоритет", "важность"),
        ("зацепка", "указатель"),
    ],
)
def test_every_short_marker_has_a_failing_probe(needle: str, replacement: str) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    removing any required phrase, however short, reddens the contract
    (зацепка P3-2 тикета 03, закрыта по команде оператора)."""
    text = SKILL.read_text("utf-8")
    mutated = text.replace(needle, replacement)
    assert mutated != text, f"the mutation must remove {needle!r}"
    errors = _contract_errors(mutated)
    assert any(f"missing required phrase '{needle}'" in error for error in errors), errors


def test_no_forbidden_harness_root():
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific
    skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    for root in (".dsh", ".zcode", ".qoder"):
        assert root not in text
        leaked = text + f"\nInstall into {root}/skills instead.\n"
        assert any(root in error for error in _contract_errors(leaked))
