"""Contract for the to-tickets skill (workflow-skills ticket 02).

The bundle must be discoverable as ``<root>/to-tickets/SKILL.md``, carry the
phase-2 slicing mechanism (tracer-bullet vertical slices, demo path, base-commit
criteria, blocking edges, comprehension check) and stay user-invoked: the
frontmatter pins ``disable-model-invocation: true``.

spec: docs/plans/workflow-skills.md#готово — skills/to-tickets/SKILL.md
spec: docs/decisions/ontoship-core.md#три фазы — one ask question per ticket,
criteria fall on the base commit, no file:line anchors
spec: docs/plans/evidence-verification.md#готово — every acceptance criterion
names an observable artifact and a spec-sourced expectation in both "Срезы"
and "Порядок"; a green test is a signal to read the artifact, not proof;
slicing ends with the critic run — после приёмки последнего тикета нарезки
запуск критика до первого ship, нарезка не закончена без критика (решение 7)
spec: docs/plans/understanding-check.md#готово — step 3 of "Порядок" is
a comprehension check: the agent asks about its own understanding of every
slice («Задумка тикета N, как я её понял: … Верно?», self-sufficient);
a mismatch sends the slice back for rewording before publication; the
retired quiz wording stays out of the skill and the runbook, and inside
this test lives only in mutation probes and the contract ban (решения 1–5)
invariant: docs/plans/workflow-skills.md#ограничения — the model never invokes this skill
invariant: docs/decisions/ontoship-core.md#три фазы — a user-invoked skill never calls another user-invoked skill
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
    "вызывает пользователь",
    "сигнал к чтению артефакта, не доказательство",
)
EVIDENCE_SECTIONS = ("Срезы", "Порядок")
EVIDENCE_SECTION_PHRASES = ("наблюдаемый артефакт", "ожидание из спеки")
CARRIERS_PHRASE = "вывод команды, строка лога, файл, живая проба"
CRITIC_TRIGGER_PHRASES = (
    "после приёмки последнего тикета нарезки",
    "запуск критика до первого ship",
    "нарезка не закончена без критика",
)
CRITIC_CONTRADICTIONS = (
    "не запускается",
    "не нужен",
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
    if fields.get("disable-model-invocation", "").lower() != "true":
        errors.append("frontmatter: disable-model-invocation must be true "
                      "(the model never invokes this skill)")

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
        for phrase in CRITIC_TRIGGER_PHRASES:
            if phrase not in sequence:
                errors.append(f"body: section 'Порядок' must carry {phrase!r}")
        for phrase in CRITIC_CONTRADICTIONS:
            if phrase in sequence:
                errors.append(f"body: section 'Порядок' carries "
                              f"contradictory phrase {phrase!r}")
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


def test_skill_is_user_invoked_only():
    """invariant: docs/plans/workflow-skills.md#ограничения — the model never invokes this skill; the skill calls no user skill."""
    fields, body = _parse(SKILL.read_text("utf-8"))
    assert fields.get("disable-model-invocation", "").lower() == "true"
    lowered = re.sub(r"\s+", " ", body.lower())
    assert "может звать модельные скиллы" in lowered
    assert "не вызывает других пользовательских скиллов" not in lowered


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


def test_slicing_ends_with_the_critic_run():
    """spec: docs/plans/evidence-verification.md#готово — после приёмки
    последнего тикета нарезки — запуск критика до первого ship; нарезка не
    закончена без критика (решение 7). Фразы ищутся в разделе «Порядок»."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = re.sub(r"\s+", " ", _sections(body).get("Порядок", "").lower())
    assert section, "section 'Порядок' is missing from the skill body"
    for phrase in CRITIC_TRIGGER_PHRASES:
        assert phrase in section, f"the phrase {phrase!r} is missing from 'Порядок'"


def test_critic_trigger_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check can fail: потеря триггера, сдвиг момента, ослабление
    «не закончена» и отрицание запуска критика красят контракт to-tickets
    (мутационные пробы)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_trigger = text.replace("Нарезка не закончена без критика",
                              "Нарезка закончена публикацией", 1)
    assert no_trigger != text
    assert any("нарезка не закончена без критика" in error
               for error in _contract_errors(no_trigger))

    late = text.replace("до первого ship", "после первого ship", 1)
    assert late != text
    assert any("запуск критика до первого ship" in error
               for error in _contract_errors(late))

    every_ticket = text.replace("последнего тикета нарезки",
                                "каждого тикета нарезки", 1)
    assert every_ticket != text
    assert any("после приёмки последнего тикета нарезки" in error
               for error in _contract_errors(every_ticket))

    no_run = text.replace("запуск критика до первого ship",
                          "критик до первого ship не нужен", 1)
    assert no_run != text
    assert any("не нужен" in error for error in _contract_errors(no_run))
    assert any("запуск критика до первого ship" in error
               for error in _contract_errors(no_run))

    negated = text.replace("критика запускает агент сам",
                           "критик не запускается сам", 1)
    assert negated != text
    assert any("не запускается" in error
               for error in _contract_errors(negated))


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    assert root not in text
    leaked = text + f"\nInstall into {root}/skills instead.\n"
    assert any(root in error for error in _contract_errors(leaked))


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the contract check rejects a missing flag, an anchor, and regressions."""
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
