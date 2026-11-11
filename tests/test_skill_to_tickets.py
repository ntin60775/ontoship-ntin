"""Contract for the to-tickets skill (workflow-skills ticket 02).

The bundle must be discoverable as ``<root>/to-tickets/SKILL.md``, carry the
phase-2 slicing mechanism (tracer-bullet vertical slices, demo path, base-commit
criteria, blocking edges, comprehension check) and stay agent-invoked: invoked
right after the plan gate; the frontmatter carries no ``disable-model-invocation``.

spec: docs/plans/workflow-skills.md#готово — skills/to-tickets/SKILL.md
spec: docs/decisions/ontoship-core.md#три фазы — one ask question per ticket,
criteria fall on the base commit, no file:line anchors
spec: docs/plans/to-tickets-agent.md#готово — agent invocation: the frontmatter
carries no ``disable-model-invocation``; «Скилл вызывает агент» in the body
spec: docs/plans/evidence-verification.md#готово — every acceptance criterion
names an observable artifact and a spec-sourced expectation in both "Срезы"
and "Порядок"; a green test is a signal to read the artifact, not proof
spec: docs/plans/standards-autoship.md#готово — «Готово» 6: to-tickets несёт
тикетные грани бывшего чек-листа критика (покрытость «Готово», рёбра,
демо-пути, падение критериев) как самопроверку основной сессии и проверяет
запись гейта проекций до нарезки; записи нет — остановка вопросом, тихий
пропуск невозможен. Инвариант evidence-verification «нарезка замыкается
критиком» выведен из эксплуатации решением 17 стандартов-автошипа: его тест
уходит тем же изменением (canon: docs/decisions/ontoship-core.md#одно
правило качества), снятые формулировки запуска критика под запретом
spec: docs/plans/understanding-check.md#готово — step 3 of "Порядок" is
a comprehension check: the agent asks about its own understanding of every
slice («Задумка тикета N, как я её понял: … Верно?», self-sufficient);
a mismatch sends the slice back for rewording before publication; the
retired quiz wording stays out of the skill and the runbook, and inside
this test lives only in mutation probes and the contract ban (решения 1–5)
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
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
    "сверка понимания",
    "file:line",
    "что я могу показать",
    ".scratch/<slug>/issues/",
    "один вопрос на тикет",
    "принять как предложено",
    "два-три предложения, не отчёт",
    # bundle reference with the guard phrase (bundle-references ticket 01)
    "../testing/references/quality-rule.md",
    "файл бандла — первоисточник",
    "проект переопределяет его документом `docs/reference/quality-rule.md`",
    "написал свой, бери его",
    "вызывает агент",
    "сигнал к чтению артефакта, не доказательство",
)
EVIDENCE_SECTIONS = ("Срезы", "Порядок")
EVIDENCE_SECTION_PHRASES = ("наблюдаемый артефакт", "ожидание из спеки")
CARRIERS_PHRASE = "вывод команды, строка лога, файл, живая проба"
GATE_PHRASES = (
    "запись гейта проекций",
    "отчёт триажа",
    "записи нет — остановка и вопрос оператору",
    "тихий пропуск гейта не делается",
    "скилл `critic`",
)
SELF_CHECK_PHRASES = (
    "самопроверка нарезки",
    "после приёмки последнего тикета нарезки",
    "тикетные грани бывшего чек-листа критика",
    "по носителям, названным в строках",
    "новых спек",
    "блокирующие рёбра отражают реальные зависимости",
    "демо-путь",
    "падают на базовом коммите",
)
GATE_CONTRADICTIONS = (
    "запись гейта не проверяется",
    "тихий пропуск допустим",
)
CHECK_SECTION_PHRASES = (
    "сверка понимания",
    "как я её понял",
    "верно?",
)
CHECK_FORBIDDEN_PHRASES = (
    "квиз перед публикацией",
    "что я увижу и где",
)
FORBIDDEN_PHRASES = (
    "нарезка — решение оператора",
    "проверяем на дереве",
    "файл проекта — первоисточник",
    "единственный источник",
    # retired user-invocation wording (to-tickets-agent): the skill is
    # agent-invoked right after the plan gate
    "вызывает пользователь",
    "вызванный пользователем скилл",
    "не запускай самостоятельно",
    # retired critic-trigger wording (standards-autoship decision 17):
    # the projection gate stands before slicing, the ticket facets live
    # in the slicing self-check
    "критик замыкает нарезку",
    "запуск критика до первого ship",
    "нарезка не закончена без критика",
    "критика запускает агент сам",
    "до первого ship",
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


def _sections(body: str) -> dict[str, str]:
    """Split the body into ``## `` sections keyed by heading text."""
    sections: dict[str, str] = {}
    current: str | None = None
    chunks: list[str] = []
    for line in body.splitlines():
        if line.startswith("## "):
            if current is not None:
                sections[current] = "\n".join(chunks)
            current = line[3:].strip()
            chunks = []
        elif current is not None:
            chunks.append(line)
    if current is not None:
        sections[current] = "\n".join(chunks)
    return sections


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
    if "disable-model-invocation" in fields:
        errors.append("frontmatter: disable-model-invocation must be absent — "
                      "the slicing follows the plan gate and is agent-invoked")
    if "вызывает пользователь" in description.lower():
        errors.append("frontmatter: description must call the agent "
                      "(«Скилл вызывает агент.»), not the user")

    lowered = re.sub(r"\s+", " ", body.lower())
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            errors.append(f"body: forbidden phrase {phrase!r}")
    sections = _sections(body)
    for title in EVIDENCE_SECTIONS:
        if title not in sections:
            errors.append(f"body: missing section {title!r}")
            continue
        section = re.sub(r"\s+", " ", sections[title].lower())
        for phrase in EVIDENCE_SECTION_PHRASES:
            if phrase not in section:
                errors.append(f"body: section {title!r} must require {phrase!r}")
    if "Срезы" in sections and CARRIERS_PHRASE not in re.sub(
            r"\s+", " ", sections["Срезы"].lower()):
        errors.append(f"body: section 'Срезы' must list the carriers "
                      f"({CARRIERS_PHRASE!r})")
    if "Порядок" in sections:
        sequence = re.sub(r"\s+", " ", sections["Порядок"].lower())
        for phrase in GATE_PHRASES:
            if phrase not in sequence:
                errors.append(f"body: section 'Порядок' must carry {phrase!r}")
        for phrase in GATE_CONTRADICTIONS:
            if phrase in sequence:
                errors.append(f"body: section 'Порядок' carries "
                              f"contradictory phrase {phrase!r}")
        for phrase in SELF_CHECK_PHRASES:
            if phrase not in sequence:
                errors.append(f"body: section 'Порядок' must carry {phrase!r}")
        gate_at = sequence.find("запись гейта проекций")
        offer_at = sequence.find("предложи срезы")
        if gate_at >= 0 and offer_at >= 0 and gate_at > offer_at:
            errors.append("body: the projection gate check must precede "
                          "the slicing offer")
        publish_at = sequence.find("опубликуй принятые тикеты")
        check_at = sequence.find("самопроверка нарезки")
        if publish_at >= 0 and check_at >= 0 and check_at < publish_at:
            errors.append("body: the slicing self-check must follow "
                          "the ticket publication")
        for phrase in CHECK_SECTION_PHRASES:
            if phrase not in sequence:
                errors.append(f"body: section 'Порядок' must carry {phrase!r}")
        for phrase in CHECK_FORBIDDEN_PHRASES:
            if phrase in sequence:
                errors.append(f"body: section 'Порядок' carries "
                              f"forbidden phrase {phrase!r}")
    anchor = ANCHOR_RE.search(text)
    if anchor:
        errors.append(f"body: file:line anchor {anchor.group(0)!r}")
    # .zcode stays banned here: this skill names no channel roots.
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


def test_skill_is_agent_invoked():
    """spec: docs/plans/to-tickets-agent.md#готово — скилл вызывает агент:
    frontmatter без disable-model-invocation, description зовёт агента, тело
    несёт «Скилл вызывает агент» без снятых пользовательских формулировок;
    инвариант user-invoked выведен из эксплуатации, и его тест уходит тем же
    изменением (canon: docs/decisions/ontoship-core.md#одно правило
    качества)."""
    fields, body = _parse(SKILL.read_text("utf-8"))
    assert "disable-model-invocation" not in fields
    assert "вызывает агент" in _unquote(fields.get("description", ""))
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "скилл вызывает агент" in lowered
    assert "вызывает пользователь" not in lowered
    assert "вызванный пользователем скилл" not in lowered
    assert "не запускай самостоятельно" not in lowered


def test_skill_carries_the_slicing_mechanism():
    """spec: docs/plans/workflow-skills.md#готово — slices, demo path;
    spec: docs/plans/understanding-check.md#готово — comprehension check."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    for phrase in ("вертикальные срезы", "демо-путь", "базовом коммите",
                   "блокирующие рёбра", "сверка понимания",
                   "что я могу показать"):
        assert phrase in lowered, f"the slicing phrase {phrase!r} is missing"


def test_criteria_fall_on_the_base_commit():
    """spec: docs/decisions/ontoship-core.md#три фазы — criteria fail on base."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "падают на базовом коммите" in lowered
    assert "должен упасть" in lowered
    assert "проверяем на дереве" not in lowered
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
    assert "каждый файл несёт" in re.sub(r"\s+", " ", body.lower())


def test_slicing_handoff_follows_the_canon():
    """spec: docs/decisions/ontoship-core.md#три фазы — agent decides; one ask per ticket."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "решение о нарезке принимаешь ты" in lowered
    assert "нарезка — решение оператора" not in lowered
    assert "один вопрос на тикет" in lowered
    assert "выдержка в два-три предложения, не отчёт" in lowered
    assert "принять как предложено" in lowered
    assert "изменить формулировку" in lowered
    assert "режут план; тикет принимают или нет" in lowered


def test_criteria_carry_artifact_and_expectation():
    """spec: docs/plans/evidence-verification.md#готово — artifact + spec-sourced expectation in every criterion, in both sections."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    sections = _sections(body)
    for title in EVIDENCE_SECTIONS:
        section = re.sub(r"\s+", " ", sections.get(title, "").lower())
        assert section, f"section {title!r} is missing from the skill body"
        for phrase in EVIDENCE_SECTION_PHRASES:
            assert phrase in section, (
                f"section {title!r} lost the requirement {phrase!r}")
    slices = re.sub(r"\s+", " ", sections.get("Срезы", "").lower())
    assert CARRIERS_PHRASE in slices, "the carriers list is missing from 'Срезы'"
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "сигнал к чтению артефакта, не доказательство" in lowered


def test_step_three_is_a_comprehension_check():
    """spec: docs/plans/understanding-check.md#готово — шаг 3 «Порядка» —
    сверка понимания: вопрос агента о собственном понимании каждого среза,
    самодостаточный; фразы ищутся в разделе «Порядок», не по всему телу."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = re.sub(r"\s+", " ", _sections(body).get("Порядок", "").lower())
    assert section, "section 'Порядок' is missing from the skill body"
    for phrase in CHECK_SECTION_PHRASES:
        assert phrase in section, f"the phrase {phrase!r} is missing from 'Порядок'"
    for phrase in CHECK_FORBIDDEN_PHRASES:
        assert phrase not in section, (
            f"the retired phrase {phrase!r} survives in 'Порядок'")


def _step_three_block(text: str) -> str:
    """Return the full step-3 block inside «Порядок»: the ``3. `` line and
    its continuation lines, up to the next numbered step. A ``3. `` line
    elsewhere in the skill must not steer a probe."""
    lines = text.splitlines()
    order = next(i for i, line in enumerate(lines) if line == "## Порядок")
    start = next(i for i in range(order + 1, len(lines))
                 if lines[i].startswith("3. "))
    end = next(i for i in range(start + 1, len(lines))
               if re.match(r"\d+\. ", lines[i]))
    return "\n".join(lines[start:end])


def test_comprehension_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check can fail: возврат «квиза», потеря «как я её понял»
    и удаление шага 3 красят контракт to-tickets (мутационные пробы,
    решение 4 understanding-check)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    # The full retired step text carries both forbidden phrases; planting it
    # back must trip the ban, not just the missing-phrase check.
    old_step = (
        "3. Квиз перед публикацией: два-три проверочных вопроса оператору "
        "о срезах и\n"
        "   рёбрах; среди них — «что я увижу и где»: какой артефакт покажет "
        "тикет и где\n"
        "   его читать; расхождение в понимании — возврат в `grilling`."
    )
    quiz_back = text.replace(_step_three_block(text), old_step, 1)
    assert quiz_back != text
    assert any("must carry 'сверка понимания'" in error
               for error in _contract_errors(quiz_back))
    assert any("forbidden phrase 'квиз перед публикацией'" in error
               for error in _contract_errors(quiz_back))
    assert any("forbidden phrase 'что я увижу и где'" in error
               for error in _contract_errors(quiz_back))

    no_phrase = text.replace("как я её понял", "как он задуман", 1)
    assert no_phrase != text
    assert any("must carry 'как я её понял'" in error
               for error in _contract_errors(no_phrase))

    no_step = text.replace(_step_three_block(text) + "\n", "", 1)
    assert no_step != text
    errors = _contract_errors(no_step)
    assert any("must carry 'сверка понимания'" in error for error in errors)
    assert any("must carry 'как я её понял'" in error for error in errors)
    assert any("must carry 'верно?'" in error for error in errors)


def test_evidence_contract_can_fail():
    """invariant: docs/plans/evidence-verification.md#готово — losing the artifact requirement or a section fails the contract."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    # The phrase may be wrapped across lines in «Срезы»; mutating the word
    # itself kills the requirement after whitespace normalisation.
    no_artifact = text.replace("наблюдаемый", "обычный", 1)
    assert no_artifact != text
    assert any("section 'Срезы' must require 'наблюдаемый артефакт'" in error
               for error in _contract_errors(no_artifact))

    # The same requirement must be catchable when it dies in «Порядок» too.
    no_artifact_anywhere = text.replace("наблюдаемый", "обычный")
    assert no_artifact_anywhere != no_artifact
    assert any("section 'Порядок' must require 'наблюдаемый артефакт'" in error
               for error in _contract_errors(no_artifact_anywhere))

    no_section = text.replace("## Порядок", "## Ход работы", 1)
    assert no_section != text
    assert any("missing section 'Порядок'" in error
               for error in _contract_errors(no_section))


def test_projection_gate_is_checked_before_slicing():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 6: to-tickets
    проверяет запись гейта проекций до нарезки; записи нет — остановка
    вопросом, тихий пропуск невозможен. Фразы ищутся в разделе «Порядок»,
    проверка гейта стоит раньше предложения срезов."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = re.sub(r"\s+", " ", _sections(body).get("Порядок", "").lower())
    assert section, "section 'Порядок' is missing from the skill body"
    for phrase in GATE_PHRASES:
        assert phrase in section, f"the phrase {phrase!r} is missing from 'Порядок'"
    for phrase in GATE_CONTRADICTIONS:
        assert phrase not in section, \
            f"the contradictory phrase {phrase!r} survives in 'Порядок'"
    gate_at = section.find("запись гейта проекций")
    offer_at = section.find("предложи срезы")
    assert -1 < gate_at < offer_at, \
        "the gate check must stand before the slicing offer"


def test_slicing_carries_the_self_check():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 6: тикетные
    грани бывшего чек-листа критика (покрытость «Готово» по носителям,
    рёбра, демо-пути, падение критериев) — самопроверка основной сессии
    после приёмки последнего тикета нарезки (решение 17). Формулировки
    покрытости «по носителям, названным в строках» и «новых спек»
    унаследованы от evidence-verification (решение 2) и перенесены сюда
    решением 17 — источник фраз шире, чем «Готово» 6."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = re.sub(r"\s+", " ", _sections(body).get("Порядок", "").lower())
    assert section, "section 'Порядок' is missing from the skill body"
    for phrase in SELF_CHECK_PHRASES:
        assert phrase in section, f"the phrase {phrase!r} is missing from 'Порядок'"
    publish_at = section.find("опубликуй принятые тикеты")
    check_at = section.find("самопроверка нарезки")
    assert -1 < publish_at < check_at, \
        "the self-check must follow the ticket publication"


def test_gate_and_self_check_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the contract check can fail: потеря проверки гейта, ослабление
    остановки, возврат критик-триггера и перенос самопроверки раньше
    публикации красят контракт to-tickets (мутационные пробы)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_gate = text.replace("проверь запись гейта проекций",
                           "прочитай спеку ещё раз", 1)
    assert no_gate != text
    assert any("must carry 'запись гейта проекций'" in error
               for error in _contract_errors(no_gate))

    silent = text.replace("тихий\n   пропуск гейта не делается",
                          "тихий пропуск допустим", 1)
    assert silent != text
    errors = _contract_errors(silent)
    assert any("тихий пропуск гейта не делается" in error for error in errors)
    assert any("contradictory phrase 'тихий пропуск допустим'" in error
               for error in errors)

    no_stop = text.replace("Записи нет — остановка и вопрос\n   оператору",
                           "Записи нет — продолжай", 1)
    assert no_stop != text
    assert any("записи нет — остановка и вопрос оператору" in error
               for error in _contract_errors(no_stop))

    critic_back = text.replace(
        "6. **Самопроверка нарезки.**",
        "6. **Критик замыкает нарезку.** Нарезка не закончена без критика; "
        "запуск критика до первого ship; критика запускает агент сам. "
        "**Самопроверка нарезки.**", 1)
    assert critic_back != text
    errors = _contract_errors(critic_back)
    for phrase in ("критик замыкает нарезку",
                   "нарезка не закончена без критика",
                   "запуск критика до первого ship",
                   "критика запускает агент сам"):
        assert any(f"forbidden phrase {phrase!r}" in error
                   for error in errors), (phrase, errors)

    no_carriers = text.replace("по носителям,\n   названным в строках",
                               "по тикетам", 1)
    assert no_carriers != text
    assert any("по носителям, названным в строках" in error
               for error in _contract_errors(no_carriers))

    early_check = text.replace(
        "2. Предложи срезы",
        "2. Самопроверка нарезки (ранний дубль): после приёмки последнего "
        "тикета нарезки.\n2. Предложи срезы", 1)
    assert early_check != text
    assert any("self-check must follow" in error
               for error in _contract_errors(early_check))


def _drop_phrase(text: str, phrase: str) -> str:
    """Remove every occurrence of a phrase regardless of case and internal
    line wrapping, keeping the line structure (section headings survive)."""
    pattern = re.escape(phrase).replace("\\ ", r"\s+")
    return re.sub(pattern, "", text, flags=re.IGNORECASE)


@pytest.mark.parametrize("phrase", GATE_PHRASES + SELF_CHECK_PHRASES)
def test_every_gate_and_self_check_phrase_has_a_failing_probe(phrase: str) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    removing any gate or self-check phrase, however short, reddens the
    «Порядок» contract (зацепка P3-2 ревью-панели тикета 04)."""
    text = SKILL.read_text("utf-8")
    mutated = _drop_phrase(text, phrase)
    assert mutated != text, f"the mutation must remove {phrase!r}"
    errors = _contract_errors(mutated)
    assert any(f"must carry {phrase!r}" in error for error in errors), errors


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    assert root not in text
    leaked = text + f"\nInstall into {root}/skills instead.\n"
    assert any(root in error for error in _contract_errors(leaked))


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check rejects a planted ``disable-model-invocation`` flag, a lost
    agent-invocation anchor, a retired user-invocation wording, an anchor,
    and regressions."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    planted = text.replace("---\n", "---\ndisable-model-invocation: true\n", 1)
    assert planted != text
    assert any("disable-model-invocation must be absent" in error
               for error in _contract_errors(planted))

    # Case-insensitive, every occurrence: the spec's «Ограничения» — the
    # probe must not survive a register change in the carrier.
    no_agent = _body_mutated_ci(text, "вызывает агент")
    assert any("вызывает агент" in error
               for error in _contract_errors(no_agent))

    user_back = _body_mutated(
        text,
        "Скилл вызывает агент: нарезка идёт ask-проходом после план-гейта "
        "и гейта проекций.",
        "Скилл вызывает пользователь; модель его не вызывает.")
    errors = _contract_errors(user_back)
    assert any("forbidden phrase 'вызывает пользователь'" in error
               for error in errors)
    assert any("missing required phrase 'вызывает агент'" in error
               for error in errors)

    bullet_back = text.replace(
        "## Когда использовать",
        "## Когда использовать\n\n"
        "- Не запускай самостоятельно: frontmatter несёт флаг.", 1)
    assert bullet_back != text
    assert any("forbidden phrase 'не запускай самостоятельно'" in error
               for error in _contract_errors(bullet_back))

    anchored = text.replace("## Срезы", "## Срезы\n\nСмотри `skills/kb-search/gitmark.py:42`.", 1)
    assert anchored != text
    assert any("gitmark.py:42" in error for error in _contract_errors(anchored))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))

    operator_decides = text.replace("Решение о нарезке принимаешь ты",
                                    "Нарезка — решение оператора", 1)
    assert operator_decides != text
    assert any("нарезка — решение оператора" in error
               for error in _contract_errors(operator_decides))

    weakened = text.replace("каждый критерий должен упасть",
                            "каждый критерий проверяем на дереве", 1)
    assert weakened != text
    assert any("проверяем на дереве" in error
               for error in _contract_errors(weakened))

    unbounded = text.replace("выдержка в два-три предложения, не отчёт",
                             "выдержка любой длины", 1)
    assert unbounded != text
    assert any("два-три предложения, не отчёт" in error
               for error in _contract_errors(unbounded))


def test_artifact_rule_comes_from_the_testing_bundle():
    """spec: docs/plans/bundle-references.md#готово — «Артефакт и ожидание»
    ведёт в references/ бандла testing (../testing/references/quality-rule.md)
    с guard-фразой: файл бандла — первоисточник, проект переопределяет его
    документом docs/reference/quality-rule.md — написал свой, бери его.
    Проектный носитель v0.3.0 из среза убран."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "../testing/references/quality-rule.md" in lowered
    assert "файл бандла — первоисточник" in lowered
    assert "проект переопределяет его документом " \
           "`docs/reference/quality-rule.md`" in lowered
    assert "написал свой, бери его" in lowered
    assert "docs/reference/testing.md" not in lowered


def _body_mutated(text: str, old: str, new: str, count: int = 1) -> str:
    """Replace in a whitespace-normalized body, frontmatter intact: a probe
    that survives any reflow of the carrier. count=-1 hits every occurrence —
    a phrase the carrier repeats (the guard now lives in two blocks)."""
    body = _parse(text)[1]
    flat = re.sub(r"\s+", " ", body)
    mutated = flat.replace(old, new, count)
    assert mutated != flat, "the mutation must change the body"
    return text.replace(body, mutated, 1)


def _body_mutated_ci(text: str, old: str) -> str:
    """Remove every case variant of a phrase from the whitespace-normalized
    body (frontmatter intact): the spec's «case-insensitive, все вхождения»."""
    body = _parse(text)[1]
    flat = re.sub(r"\s+", " ", body)
    mutated = re.sub(re.escape(old), "", flat, flags=re.IGNORECASE)
    assert mutated != flat, "the mutation must change the body"
    return text.replace(body, mutated, 1)


def test_reference_guard_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the contract rejects a lost bundle reference, a lost guard phrase, a
    priority inversion, an only-source claim and a renamed override doc."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_ref = text.replace("../testing/references/quality-rule.md",
                          "../testing/references/absent-rule.md")
    assert no_ref != text
    assert any("../testing/references/quality-rule.md" in error
               for error in _contract_errors(no_ref))

    no_guard = _body_mutated(text, "написал свой, бери его", "проект решает сам",
                             count=-1)
    assert any("написал свой, бери его" in error
               for error in _contract_errors(no_guard))

    inverted = _body_mutated(text, "Файл бандла — первоисточник",
                             "Файл проекта — первоисточник")
    assert any("файл проекта — первоисточник" in error
               for error in _contract_errors(inverted))

    only_source = _body_mutated(text, "Файл бандла — первоисточник",
                                "Файл бандла — единственный источник")
    assert any("единственный источник" in error
               for error in _contract_errors(only_source))

    renamed = _body_mutated(text, "docs/reference/quality-rule.md",
                            "docs/reference/review-panel.md")
    assert any("проект переопределяет его документом "
               "`docs/reference/quality-rule.md`" in error
               for error in _contract_errors(renamed))
