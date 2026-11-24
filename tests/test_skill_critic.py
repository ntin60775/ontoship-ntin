"""Contract for the critic skill — the projection consilium.

The bundle keeps the name ``critic`` and becomes a consilium: three members
on three distinct ``[validation]`` routes read the whole spec and a full
checklist, each with a primary focus; members are isolated; the chairman on
``[agents.critic]`` merges their raw reports without adding findings or
verdicts; the main session triages and writes the gate report. One run per
unit; quorum is two of three; no model fallback. The retired slice wording
stays banned.

spec: docs/plans/critic-consilium.md#готово — пункты 1, 7, 9:
      контракт консилиума, отчёт гейта, тесты
invariant: docs/decisions/ontoship-core.md#одно правило качества —
      the contract check can fail
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no
      harness root
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "critic" / "SKILL.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500

FOCUS_PHRASES = (
    "три брифа",
    "чек-лист критика и восемь проекций",
    "покрытость «Готово», связность, рёбра, демо-пути, честность критериев, "
    "цена доказательства",
    "покрытие, порядок, доказательства, власть, время, окружение, термины, риск",
    "Фокусы — 3/3/2",
    "ровно один основной фокус",
    "объединение фокусов = восемь",
    "причину выбора маршрута и фокуса",
    "Находки вне фокуса принимаются",
)
MEMBER_PHRASES = (
    "`subagent` (spawn, не `subagent_fork`)",
    "Все три члена стартуют в одном сообщении",
    "Маршруты различны по модели",
    "отчёты других членов и сводка председателя не передаются",
    "`tickets/<slug>/00-consilium/<member>.md`",
    "маршрут, уровень, фокус, статус, находки или «находок нет»",
    "проекция, приоритет P1/P2/P3, место, утверждение, доказательство, "
    "что править",
)
POOL_PHRASES = (
    "Пул валидации — flash",
    "секция `[validation]`",
    "Стандартная раскладка — три различных flash-маршрута",
    "конкретные маршруты в скилле не хардкодятся",
    "`list_subagent_models`",
    "слот члена выпадает",
    "подмены занятым маршрутом нет",
    "Живых различных моделей меньше двух — остановка",
    "Пул без трёх живых моделей — два члена, кворум",
)
FAILURE_PHRASES = (
    "Одна повторная проба на члена и на председателя",
    "Живой член — вернул пригодный сырой отчёт",
    "пустой или битый отчёт — выпавший для кворума",
    "Кворум — не меньше двух живых членов",
    "председатель называет выпавшего и его фокус-проекции",
    "Кворумный пробел принимает оператор до нарезки",
    "Падение или битая сводка председателя — одна повторная проба, затем стоп",
    "отчёт гейта не пишется",
    "Молчаливой подмены маршрута, модели сессии или «ревью исполнителем» нет",
)
CHAIRMAN_PHRASES = (
    "отдельный `subagent` на `[agents.critic]`",
    "Вход: спека, ростер",
    "и сырые отчёты",
    "`tickets/<slug>/00-consilium/chairman.md`",
    "покрытие всех восьми проекций",
    "источник (член и маршрут), поддержку, группу дедупа",
    "расхождения: конкурирующие находки по одному пункту",
    "молчание члена — не dissent",
    "Новых находок и вердиктов председатель не добавляет",
    "все сырые находки учтены, потерь нет",
    "Битая или неполная сводка — отказ председателя",
    "Основная сессия сверяет сводку с сырыми отчётами",
)
TRIAGE_PHRASES = (
    "Находки сводки проходят триаж основной сессии",
    "подтверждается или отвергается с причиной",
    "оверинжиниринг",
    "Спорное — оператору ask-инструментом хоста",
    "Решения план-гейта не перепрашиваются",
    "«Выбрали не так» — не находка",
    "оператор решает — править спеку или принять риск",
)
REPORT_PHRASES = (
    "`tickets/<slug>/00-projection-report.md`",
    "прогон: дата, спека, один прогон",
    "состав: члены (маршрут, уровень, фокус, статус, идентификатор)",
    "председатель (маршрут, уровень, статус, идентификатор)",
    "ссылки на сырые отчёты и сводку",
    "триаж находок — подтверждена или отвергнута, причина",
    "расхождения и пробелы покрытия, включая кворумный",
    "решения оператора и запись гейта",
    "`to-tickets` проверяет файл",
)
PROBE_PHRASES = (
    "Ручная проба — исключение",
    "тестовый фикстур в папке юнита, не `docs/plans/`",
    "`tickets/<slug>/00-probe-report.md`",
    "матрицу «засев × член»",
    "Поведенческие ветки кворума и стопа пробой не проверяются — названный пробел",
)

SECTIONS = (
    ("семя и фокусы", FOCUS_PHRASES, "focus"),
    ("члены", MEMBER_PHRASES, "members"),
    ("пул и маршруты", POOL_PHRASES, "pool"),
    ("отказы и кворум", FAILURE_PHRASES, "failure"),
    ("председатель", CHAIRMAN_PHRASES, "chairman"),
    ("триаж", TRIAGE_PHRASES, "triage"),
    ("отчёт и гейт проекций", REPORT_PHRASES, "report"),
    ("ручная проба", PROBE_PHRASES, "probe"),
)

REQUIRED_PHRASES = (
    "один прогон на юнит",
    "Вход — спека `docs/plans/<slug>.md`",
    "три члена консилиума",
    "председатель сводит",
    "основная сессия триажит",
    "Независимый взгляд на спеку",
    "../ship/references/method-phases.md",
)

# The retired plan-critic and slice wording: a return reddens.
RETIRED_PHRASES = (
    "срез",
    "Семя срезов",
    "Исполнение срезов",
    "модель под срез",
    "под срез",
    "динамические срезы",
    "сразу после приёмки последнего тикета",
    "до первого ship",
    "находки оператору до первого ship",
    "модель роли `critic` назначает",
    "рекомендация, не запрет",
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
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _drop_phrase(text: str, phrase: str) -> str:
    pattern = re.escape(phrase).replace("\\ ", r"\s+")
    return re.sub(pattern, "", text, flags=re.IGNORECASE)


def _section(body: str, heading: str) -> str:
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
    if "disable-model-invocation" in fields:
        errors.append("frontmatter: disable-model-invocation must be absent — "
                      "the consilium is a model-invoked skill")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase.lower() not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for phrase in RETIRED_PHRASES:
        if phrase.lower() in lowered:
            errors.append(f"body: retired phrase {phrase!r} is back")

    for heading, phrases, label in SECTIONS:
        section = _normalized_lower(_section(body, heading))
        if not section:
            errors.append(f"{label}: missing section «{heading}»")
            continue
        for phrase in phrases:
            if phrase.lower() not in section:
                errors.append(f"{label}: section «{heading}» lost {phrase!r}")

    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/critic-consilium.md#готово — пункт 1: имя бандла
    critic сохраняется, контракт — консилиум."""
    assert SKILL.is_file(), "the critic skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "critic"
    assert SKILL.parent.name == fields["name"]
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_is_model_invoked_before_slicing():
    """spec: docs/plans/critic-consilium.md#готово — пункт 1: агент
    запускает консилиум после план-гейта, до нарезки; один прогон."""
    fields, body = _parse(SKILL.read_text("utf-8"))
    assert "disable-model-invocation" not in fields
    lowered = _normalized_lower(body)
    assert "агент запускает консилиум" in lowered
    assert "сразу после утверждения спеки на план-гейте" in lowered
    assert "до нарезки" in lowered
    assert "не командой оператора" in lowered
    assert "один прогон на юнит" in lowered


def test_members_read_the_whole_spec_with_three_two_three_focuses():
    """spec: docs/plans/critic-consilium.md#готово — пункт 1, решение 1:
    три члена, весь спек, фокусы 3/3/2, покрытие восьми, находки вне
    фокуса принимаются."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "семя и фокусы"))
    assert section, "section «Семя и фокусы» is missing"
    for phrase in FOCUS_PHRASES:
        assert phrase.lower() in section, f"the focus contract lost {phrase!r}"


def test_members_are_isolated_and_write_raw_reports():
    """spec: docs/plans/critic-consilium.md#готово — пункты 1, 7, решение 8:
    spawn в одном сообщении, изоляция, сырой отчёт члена."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "члены"))
    assert section, "section «Члены» is missing"
    for phrase in MEMBER_PHRASES:
        assert phrase.lower() in section, f"the member contract lost {phrase!r}"


def test_pool_routes_are_distinct_and_dead_routes_do_not_substitute():
    """spec: docs/plans/critic-consilium.md#готово — пункт 2, решения 2,
    6, 9: три различных flash-маршрута, мёртвый слот выпадает."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "пул и маршруты"))
    assert section, "section «Пул и маршруты» is missing"
    for phrase in POOL_PHRASES:
        assert phrase.lower() in section, f"the pool contract lost {phrase!r}"


def test_quorum_and_chairman_failure_stop_the_pass():
    """spec: docs/plans/critic-consilium.md#готово — решения 3, 9, 10:
    кворум 2 из 3, выпавший и его фокус, стоп председателя."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "отказы и кворум"))
    assert section, "section «Отказы и кворум» is missing"
    for phrase in FAILURE_PHRASES:
        assert phrase.lower() in section, f"the failure contract lost {phrase!r}"


def test_chairman_merges_without_findings_or_verdicts():
    """spec: docs/plans/critic-consilium.md#готово — решение 5: вход
    председателя, сводка с атрибуцией, без новых находок и вердиктов."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "председатель"))
    assert section, "section «Председатель» is missing"
    for phrase in CHAIRMAN_PHRASES:
        assert phrase.lower() in section, f"the chairman contract lost {phrase!r}"


def test_triage_keeps_operator_decisions_and_plan_gate():
    """spec: docs/plans/critic-consilium.md#готово — triage: подтверждение
    с причиной, спорное оператору, решения план-гейта не перепрашиваются."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "триаж"))
    assert section, "section «Триаж» is missing"
    for phrase in TRIAGE_PHRASES:
        assert phrase.lower() in section, f"the triage contract lost {phrase!r}"


def test_gate_report_is_the_file_to_tickets_reads():
    """spec: docs/plans/critic-consilium.md#готово — пункт 7, решение 8:
    файл гейта, состав, ссылки, триаж, решения, запись."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "отчёт и гейт проекций"))
    assert section, "section «Отчёт и гейт проекций» is missing"
    for phrase in REPORT_PHRASES:
        assert phrase.lower() in section, f"the report contract lost {phrase!r}"


def test_manual_probe_is_an_exception_not_a_gate():
    """spec: docs/plans/critic-consilium.md#готово — пункт 10, решение 11:
    ручная проба, фикстур в папке юнита, матрица, названный пробел."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, "ручная проба"))
    assert section, "section «Ручная проба» is missing"
    for phrase in PROBE_PHRASES:
        assert phrase.lower() in section, f"the probe contract lost {phrase!r}"


def test_retired_slice_and_plan_critic_wording_is_banned():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    planting any retired slice or plan-critic phrase reddens the contract."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for phrase in RETIRED_PHRASES:
        planted = text + f"\n{phrase.capitalize()}.\n"
        errors = _contract_errors(planted)
        assert any(f"retired phrase {phrase!r}" in error for error in errors), \
            (phrase, errors)


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the contract rejects a model-invocation flag, a lost gate file, a lost
    quorum, a lost chairman ban and a leaked harness root."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    model_locked = text.replace("---\n", "---\ndisable-model-invocation: true\n", 1)
    assert any("disable-model-invocation" in error
               for error in _contract_errors(model_locked))

    no_gate = text.replace("`tickets/<slug>/00-projection-report.md`",
                           "`tickets/<slug>/`", 1)
    assert any("00-projection-report.md" in error
               for error in _contract_errors(no_gate))

    no_quorum = text.replace("Кворум — не меньше двух живых членов",
                             "Кворум — не меньше одного", 1)
    assert any("Кворум — не меньше двух" in error
               for error in _contract_errors(no_quorum))

    no_ban = text.replace("Новых находок и вердиктов председатель не добавляет",
                          "Председатель добавляет находки", 1)
    assert any("Новых находок и вердиктов" in error
               for error in _contract_errors(no_ban))

    leaked = text + "\nЗапусти проекции из .zcode/skills.\n"
    assert any(".zcode" in error for error in _contract_errors(leaked))


@pytest.mark.parametrize("phrase", REQUIRED_PHRASES)
def test_every_required_phrase_has_a_failing_probe(phrase: str):
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    removing any required phrase reddens the contract."""
    text = SKILL.read_text("utf-8")
    mutated = _drop_phrase(text, phrase)
    assert mutated != text, f"the mutation must remove {phrase!r}"
    errors = _contract_errors(mutated)
    assert any(f"missing required phrase {phrase!r}" in error
               for error in errors), errors


SCOPED_PROBE_CASES = tuple(
    (label, heading, phrase)
    for heading, phrases, label in SECTIONS
    for phrase in phrases
)


@pytest.mark.parametrize(
    ("label", "heading", "phrase"), SCOPED_PROBE_CASES,
    ids=[f"{label}:{phrase[:24]}" for label, _heading, phrase in SCOPED_PROBE_CASES])
def test_every_scoped_phrase_has_a_failing_probe(label: str, heading: str,
                                                 phrase: str):
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    removing any scoped phrase reddens its section check."""
    text = SKILL.read_text("utf-8")
    mutated = _drop_phrase(text, phrase)
    assert mutated != text, f"the mutation must remove {phrase!r}"
    errors = _contract_errors(mutated)
    assert any(f"{label}: section «{heading}» lost {phrase!r}" in error
               for error in errors), errors


def test_no_forbidden_harness_root():
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific
    skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    for root in (".dsh", ".zcode", ".qoder"):
        assert root not in text
        leaked = text + f"\nInstall into {root}/skills instead.\n"
        assert any(root in error for error in _contract_errors(leaked))


def test_critic_anchors_to_the_bundle_section():
    """spec: docs/plans/canon-section-in-bundles.md#готово — шапка критика
    называет методную секцию бандла; путь канона уходит из тела."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "../ship/references/method-phases.md" in lowered
    assert "docs/decisions/ontoship-core.md" not in lowered

    text = SKILL.read_text("utf-8")
    relinked = text.replace("../ship/references/method-phases.md",
                            "docs/decisions/ontoship-core.md")
    assert any("../ship/references/method-phases.md" in error
               for error in _contract_errors(relinked))
