"""Contract for the ship skill (workflow-skills ticket 03, review-config
ticket 04, ship-isolation ticket 01, standards-autoship ticket 05).

The bundle must be discoverable as ``<root>/ship/SKILL.md`` and carry the
phase-3 single pass — worktree, implementation, proof tests, exactly one
review pass, dev/prod checks, the pack mechanical gates, merge — with stop
points read from the spec's «Ограничения» section, review yielding leads
instead of a convergence loop, and readiness independent of a remote: a local
commit in the target branch and a named sync gap, catch-up when the remote
appears later, never a faked PR.

Step one demands an isolated worktree unconditionally (ship-isolation
ticket 01): the phrase «изолированный worktree» lives in step 1 of the
«Один проход» section, and the permissive «или ветку» is forbidden
anywhere in the skill file, frontmatter included.

standards-autoship ticket 05 (decisions 10, 11, 15) flips the executor:
the frontmatter drops ``disable-model-invocation`` — model invocation
stays open; core-team-boundaries ticket 03 (decision 3) removes the
driver context lines: the chain mechanism lives in the team bundle and
drives the model invocation from there, the core names the manual
``/ship`` channel; ticket
acceptance is automatic on the fully green contour (criteria proven, panel
after one fix pass without open P1/P2, dev/prod passed, pack gates green,
stop points passed), P3 is triaged in the same pass, anything open or a stop
is an operator question; the pass carries the pack mechanical-gate step
(configs-as-data executed by the core); the panel assembles from core and
pack roles, ``reviewer-code`` receives the standards sources in priority
order; an unavailable route stops the pass — no model fallback. The critic
gate becomes the projection gate (decision 16): the unit's first ship needs
the triage-report record.

The review pass runs as a specialists panel (review-config ticket 04): roles
from ``.agents/config.toml`` run in parallel in one pass, the executor
deduplicates findings into one report; a role's input is its scope and
checklist, its output a verdict and findings with priorities and leads;
independence is artifacts, never the run's story. Routes and levels are
checked against the live host listing before launch; a base-set or pack
role missing from the config is a named gap in the report, not a silent
skip.

spec: docs/plans/workflow-skills.md#готово — skills/ship/SKILL.md
spec: docs/plans/standards-autoship.md#готово — «Готово» 3 (часть ship), 8, 9:
model invocation, auto-acceptance, pack gates, core+pack panel
spec: docs/plans/standards-autoship.md#решения план-гейта — решения 10, 11,
15, 16: зелёный контур автоприёмки, ship вызывает модель, гейт проекций
вместо критик-гейта
spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3, решение 3:
контекстные строки ship о драйвере сняты, ручной канал /ship назван,
снятые формулировки драйвера под запретом
spec: docs/decisions/ontoship-core.md#три фазы — one pass, stop points from
«Ограничения», review gives leads
spec: docs/plans/review-config.md#готово — ship ведёт ревью панелью
spec: docs/plans/review-config.md#ограничения — панель один прогон,
пропущенная роль названа
spec: docs/plans/ship-isolation.md#готово — шаг 1 безусловный изолированный
worktree, «или ветку» запрещена во всём тексте скилла
spec: docs/plans/canon-section-in-bundles.md#готово — шапка ship называет
методную секцию своего бандла, не путь канона
invariant: docs/decisions/ontoship-core.md#три фазы — one review pass, no convergence loop
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

import test_canon_sync  # reuse: the panel-run anchors, not duplicated

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "ship" / "SKILL.md"
PANEL_FILE = REPO / "skills" / "ship" / "references" / "review-panel.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
ANCHOR_RE = re.compile(r"\b[\w-]+(?:\.[\w-]+)+:\d+")
PASS_STEPS = ("**worktree", "**реализация", "**доказательные тесты",
              "**один прогон ревью", "**проверки dev и prod",
              "**механические гейты пака", "**merge")
REQUIRED_PHRASES = (
    "один проход",
    "worktree",
    "доказательные тесты",
    "один прогон ревью",
    "зацепки, а не цикл сходимости",
    "p1/p2 исправляются в этом проходе",
    "p3 — не долг, а триаж",
    "остановись",
    "точки остановки",
    "раздела «ограничения» спеки",
    "dev-окружении",
    "prod-проверки",
    "git remote -v",
    "локальный коммит",
    "названный пробел",
    "не имитируй",
    "отчёт фактами стоит в чате перед вызовом",
    "в поле вопроса — одно предложение",
    "docs/plans/<slug>.md",
    "references/method-phases.md",
    "три фазы",
    "ручной канал — команда `/ship`",
    "один тикет за запуск",
    "готовность прохода — коммит в целевой ветке",
    "входит в готовность",
    "недоступны (origin нет)",
    "догон",
)
FORBIDDEN_PHRASES = (
    "повторяй прогоны ревью",
    "до нуля находок",
    "создай pull request",
    "или ветку",
    "файл проекта — первоисточник",
    "единственный источник",
    # standards-autoship 05: the retired user-only invocation and the
    # unconditional acceptance ask (decisions 10, 11).
    "disable-model-invocation",
    "модель его не вызывает",
    "скилл вызывает только пользователь",
    "не запускай самостоятельно",
    "приёмка тикета идёт отдельным ask-вопросом",
    "критик-гейт",
    # core-team-boundaries 03 («Готово» 3, decision 3): the driver context
    # lines left the core — the chain mechanism lives in the team bundle;
    # ship names the manual channel, model invocation stays open via the
    # absent disable-model-invocation flag.
    "в автономной цепочке",
    "оркестратор передаёт тикет",
    "оркестратор ведёт тикеты",
    "скилл вызывает модель",
)
PANEL_PHRASES = (
    "ревью-панель",
    "параллельно в одном прогоне",
    "один отчёт",
    "дедуплицируй",
    "область и чек-лист",
    "вердикт",
    "приоритет",
    "зацепк",
    "артефакты",
    "не ход исполнения",
    ".agents/config.toml",
    "маршрут и уровень каждой роли",
    "повторная проба",
    "затем остановка",
    "базового набора",
    "пропуск в отчёте",
    "references/review-panel.md",
    "справочник `references/review-panel.md`",
    "процедура запуска ролей — в том же `references/review-panel.md`",
    "файл бандла — первоисточник",
    "проект переопределяет его документом `docs/reference/review-panel.md`",
    "написал свой, бери его",
    "бери её оттуда",
)
# standards-autoship 05: the panel assembles from core and pack roles
# («Готово» 3); a role without a config section is a named gap for both.
ASSEMBLY_PHRASES = (
    "панель собирается из ролей ядра и ролей паков",
    ".agents/packs/",
    "чек-лист роли пака берётся из файла её манифеста",
    "модель роли назначает реестр, не пак",
    "без секции в конфиге не запускается",
    "молчаливая подмена не делается",
)
# standards-autoship 05, decision 10: the green contour of auto-acceptance.
AUTOSHIP_PHRASES = (
    "автоприёмка тикета на полном зелёном контуре",
    "без ask",
    "критерии приёмки закрыты доказательствами",
    "панель после одного раунда правок без незакрытых p1/p2",
    "проверки dev/prod пройдены",
    "механические гейты пака зелёные",
    "точки остановки спеки пройдены",
    "синхронизация названа",
    "пак без гейтов назван пробелом",
    "p3 не блокируют автоприёмку",
    "у каждой зацепки исход в этом проходе",
    "незакрытое или остановка — вопрос оператору",
    "tickets/<slug>/",
)
# standards-autoship 05, «Готово» 8: the mechanical-gate step of the pass.
GATE_STEP_PHRASES = (
    "конфиги-данные исполняет ядро",
    "run_gates.py",
    "без shell-интерпретации",
    "expect_exit",
    "прочитай вывод каждого гейта",
    "шаг называет ноль",
    "красный гейт — находка",
    "повторный прогон гейтов — механическая проверка",
    "паков нет",
    "пак без гейтов",
    "не зелёный гейт",
)
# An unavailable role route stops the pass: no model fallback.
ROUTE_STOP_PHRASES = (
    "недоступная пара — остановка прохода и вопрос оператору",
    "одна повторная проба, затем остановка прохода",
    "«ревью провёл исполнитель» законным исходом не является",
)
# The model-distinctness rule is retired: a role route may match the session
# model. Any return of the old wording reddens.
RETIRED_MODEL_RULE = (
    "независимость по умолчанию",
    "отличной от сессионной",
    "модель сессии",
    "модели сессии",
    "powered by",
    "не-сессионную модель",
    "автоприёмка на таком контуре не делается",
)
# standards-autoship 05, decision 8: reviewer-code standards input.
STANDARDS_PHRASES = (
    "источники стандартов в порядке приоритета",
    "канон > стандарты проекта > пак команды > пак стека > базовый документ",
    "источник называется во входе роли",
    "неразрешимый конфликт норм — вопрос оператору",
    "docs/reference/baseline-standards.md",
)
# standards-autoship 05, decision 16: the projection gate replaces the
# critic gate; the record is the triage report in the unit's tracker folder.
PROJECTION_GATE_PHRASES = (
    "гейт проекций",
    "до первого ship юнита",
    "записи гейта проекций",
    "отчёт триажа",
    "tickets/<slug>/",
    "запись прогона",
    "тихий пропуск гейта не делается",
)
# The DSH branch (dsh-adaptation ticket 01): spawn with an explicit route and
# effort in one message; routes are checked against the live host listing,
# generated role definitions are a ZCode-only step; the operator command is
# `/ship`; the worktree tool falls back to plain git.
DSH_COMMON_PHRASES = (
    "`subagent`",
    "spawn, не `subagent_fork`",
    "`provider`",
    "`model`",
    "`reasoning_effort`",
    "`list_subagent_models`",
    "в одном сообщении",
)
DSH_SKILL_PHRASES = DSH_COMMON_PHRASES + (
    "`/ship`",
    "`create_worktree`",
    "`git worktree`",
    "сгенерированные определения ролей не нужны",
)
DSH_PANEL_PHRASES = DSH_COMMON_PHRASES + (
    "`.agents/config.toml`",
    "дедуплицируется",
    "недоступная пара — остановка прохода и вопрос оператору",
    "одна повторная проба, затем остановка прохода",
)
DSH_PANEL_HEADING = "### dsh — рабочий способ"


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


def _pass_step_one(lowered: str) -> str:
    """Slice step 1 inside the «Один проход» section; empty when absent.

    Slicing is anchored to the section header so a phrase carried out of
    step 1 into the intro (even with a ``**Worktree`` marker there) is
    still caught as a loss. The text is whitespace-normalized, so the next
    «## » header is searched as ``" ## "``.
    """
    section_start = lowered.find("## один проход")
    if section_start == -1:
        return ""
    section_end = lowered.find(" ## ", section_start + 1)
    if section_end == -1:
        section_end = len(lowered)
    section = lowered[section_start:section_end]
    step_end = section.find("**реализация")
    if step_end != -1:
        section = section[:step_end]
    return section


def _pass_gate_step(lowered: str) -> str:
    """Slice the mechanical-gate step between its marker and the merge step."""
    start = lowered.find("**механические гейты пака")
    if start == -1:
        return ""
    end = lowered.find("**merge", start + 1)
    return lowered[start:end] if end != -1 else lowered[start:]


def _section(lowered: str, heading: str) -> str:
    """Slice one ``## `` section of the whitespace-normalized body."""
    start = lowered.find(f"## {heading}")
    if start == -1:
        return ""
    end = lowered.find(" ## ", start + 1)
    return lowered[start:end] if end != -1 else lowered[start:]


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
                      "ship stays model-invocable (the team chain drives it) "
                      "alongside the manual /ship channel "
                      "(core-team-boundaries decision 3)")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    if "изолированный worktree" not in _pass_step_one(lowered):
        errors.append("body: step 1 must demand «изолированный worktree»")
    for phrase in PANEL_PHRASES:
        if phrase not in lowered:
            errors.append(f"panel: missing required phrase {phrase!r}")
    for phrase in ASSEMBLY_PHRASES:
        if phrase not in lowered:
            errors.append(f"assembly: missing required phrase {phrase!r}")
    for phrase in DSH_SKILL_PHRASES:
        if phrase not in lowered:
            errors.append(f"dsh: missing required phrase {phrase!r}")

    gate_step = _pass_gate_step(lowered)
    if not gate_step:
        errors.append("gates: the mechanical-gate step of the pass is missing")
    else:
        for phrase in GATE_STEP_PHRASES:
            if phrase not in gate_step:
                errors.append(f"gates: the gate step lost {phrase!r}")

    autoship = _section(lowered, "автоприёмка")
    if not autoship:
        errors.append("autoship: missing section «Автоприёмка»")
    else:
        for phrase in AUTOSHIP_PHRASES:
            if phrase not in autoship:
                errors.append(f"autoship: section «Автоприёмка» lost {phrase!r}")

    panel = _section(lowered, "ревью-панель")
    if not panel:
        errors.append("panel: missing section «Ревью-панель»")
    else:
        for phrase in ROUTE_STOP_PHRASES:
            if phrase not in panel:
                errors.append(f"panel: the panel section lost {phrase!r}")
        for phrase in STANDARDS_PHRASES:
            if phrase not in panel:
                errors.append(f"standards: the panel section lost {phrase!r}")

    for phrase in RETIRED_MODEL_RULE:
        if phrase in lowered:
            errors.append(f"retired model rule {phrase!r} is back")

    projection = _section(lowered, "гейт проекций")
    if not projection:
        errors.append("projection: missing section «Гейт проекций»")
    else:
        for phrase in PROJECTION_GATE_PHRASES:
            if phrase not in projection:
                errors.append(f"projection: the gate section lost {phrase!r}")

    full_text = _normalized_lower(text)
    for phrase in FORBIDDEN_PHRASES:
        if phrase in full_text:
            errors.append(f"body: forbidden convergence-loop, PR-imitation or "
                          f"retired-flow phrase {phrase!r}")
    anchor = ANCHOR_RE.search(text)
    if anchor:
        errors.append(f"body: file:line anchor {anchor.group(0)!r}")
    # .zcode stays banned here: this skill names no channel roots.
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/workflow-skills.md#готово — skills/ship/SKILL.md."""
    assert SKILL.is_file(), "the ship skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "ship"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_manual_ship_is_the_core_channel():
    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3, решение 3:
    контекстные строки о драйвере сняты — цепочку ведёт team-бандл, ядро
    называет ручной канал `/ship` на один тикет; frontmatter без
    disable-model-invocation (модельный вызов остаётся открытым), скилл
    зовёт модельные скиллы, но не другой пользовательский."""
    text = SKILL.read_text("utf-8")
    fields, body = _parse(text)
    assert "disable-model-invocation" not in fields
    lowered = _normalized_lower(body)
    assert "ручной канал — команда `/ship`" in lowered
    assert "один тикет за запуск" in lowered
    assert "может звать модельные скиллы" in lowered
    assert "не другой пользовательский" in lowered
    full = _normalized_lower(text)
    for phrase in ("в автономной цепочке", "оркестратор передаёт тикет",
                   "оркестратор ведёт тикеты", "скилл вызывает модель"):
        assert phrase not in full, \
            f"the retired driver phrase {phrase!r} survives in ship"


def test_skill_carries_the_single_pass():
    """spec: docs/decisions/ontoship-core.md#три фазы — one pass, steps in order.
    spec: docs/plans/standards-autoship.md#готово — «Готово» 8: шаг
    механических гейтов пака стоит между проверками dev/prod и merge."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    positions = [lowered.find(step) for step in PASS_STEPS]
    assert all(position >= 0 for position in positions), \
        f"a pass step is missing: {list(zip(PASS_STEPS, positions))}"
    assert positions == sorted(positions), \
        "the pass steps must appear in worktree → … → gates → merge order"


def test_step_one_demands_an_isolated_worktree():
    """spec: docs/plans/ship-isolation.md#готово — шаг 1: безусловный
    изолированный worktree; «или ветку» запрещена во всём файле скилла."""
    text = SKILL.read_text("utf-8")
    lowered = _normalized_lower(_parse(text)[1])
    step1 = _pass_step_one(lowered)
    assert step1, "the «Один проход» section or its step 1 is missing"
    assert "отдели изолированный worktree" in step1, \
        "step 1 lost the unconditional isolated worktree imperative"
    assert "или ветку" not in _normalized_lower(text), \
        "the permissive «или ветку» leaked back into the skill file"


def test_stop_points_come_from_the_spec():
    """spec: docs/plans/workflow-skills.md#готово — stop points from «Ограничения».
    spec: docs/plans/standards-autoship.md#готово — «Готово» 8: точки
    остановки из «Ограничений» спеки не меняются."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "точки остановки" in lowered
    assert "раздела «ограничения» спеки" in lowered
    assert "docs/plans/<slug>.md" in lowered
    assert "не из вкуса исполнителя" in lowered
    assert "проход стоит" in lowered


def test_review_is_one_pass_and_yields_leads():
    """invariant: docs/decisions/ontoship-core.md#три фазы — one review pass; leads, fix the named findings, stop."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "один прогон ревью" in lowered
    assert "зацепки, а не цикл сходимости" in lowered
    assert "p1/p2 исправляются в этом проходе" in lowered
    assert "p3 — не долг, а триаж" in lowered
    assert "остановись" in lowered
    for phrase in FORBIDDEN_PHRASES[:2]:
        assert phrase not in lowered, f"convergence-loop phrase {phrase!r} leaked"


def test_sync_without_remote_is_honest():
    """spec: docs/plans/workflow-skills.md#ревизия-2026-11-23 — готовность
    без remote: локальный коммит в целевой ветке и названный sync-пробел,
    проход не останавливается, PR не имитируется."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "git remote -v" in lowered
    assert "локальный коммит" in lowered
    assert "названный пробел" in lowered
    assert "не останавливает проход" in lowered
    assert "не имитируй" in lowered
    assert "создай pull request" not in lowered


def test_remote_appearing_later_is_caught_up():
    """spec: docs/plans/workflow-skills.md#ревизия-2026-11-23 — remote
    появился позже: ближайший проход пушит неотправленные коммиты и называет
    догон; проверка remote идёт в каждом проходе, без памяти прогонов."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _section(_normalized_lower(body), "синхронизация")
    assert section, "the «Синхронизация» section is missing"
    assert "в каждом проходе" in section
    assert "появился позже" in section
    assert "догон" in section
    assert "git push -u origin" in section
    assert "sync: догнал" in section


def test_auto_acceptance_on_the_green_contour():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 10:
    автоприёмка тикета на полном зелёном контуре без ask; P3 — триаж в
    том же проходе (правка или ишью), а не долг; незакрытое или
    остановка — вопрос оператору."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _section(_normalized_lower(body), "автоприёмка")
    assert section, "the «Автоприёмка» section is missing"
    for phrase in AUTOSHIP_PHRASES:
        assert phrase in section, f"the green contour lost {phrase!r}"


def test_question_form_survives_for_the_operator():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 10:
    незакрытое или остановка — вопрос оператору; прежняя форма ask-прохода
    (отчёт фактами в чате перед вызовом, решение в поле вопроса, следствия
    выбора в описаниях вариантов) перенесена в раздел «Автоприёмка»."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "отчёт фактами стоит в чате перед вызовом" in lowered
    assert "в поле вопроса — одно предложение" in lowered
    assert "следствия выбора, не доказательства" in lowered
    assert "приёмка тикета идёт отдельным ask-вопросом" not in lowered, \
        "the unconditional acceptance ask is retired (decision 10)"


def test_pass_carries_the_pack_gate_step():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 8: шаг
    механических гейтов пака; конфиги-данные исполняет ядро, вывод
    прочитан, красный гейт — находка, повторный прогон — не ревью."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    step = _pass_gate_step(_normalized_lower(body))
    assert step, "the mechanical-gate step is missing from the pass"
    for phrase in GATE_STEP_PHRASES:
        assert phrase in step, f"the gate step lost {phrase!r}"


def test_panel_assembles_core_and_pack_roles():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 3: ship
    собирает панель из ролей ядра и ролей паков; чек-лист роли пака — файл
    её манифеста, модель назначает реестр; роль без секции — названный
    пропуск, молчаливая подмена не делается."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    for phrase in ASSEMBLY_PHRASES:
        assert phrase in lowered, f"the panel assembly lost {phrase!r}"


def test_reviewer_code_gets_standards_in_priority_order():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 8:
    reviewer-code получает источники стандартов в порядке приоритета
    (канон > стандарты проекта > пак команды > пак стека > базовый
    документ); источник называется во входе роли, конфликт — оператору."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _section(_normalized_lower(body), "ревью-панель")
    assert section, "the «Ревью-панель» section is missing"
    for phrase in STANDARDS_PHRASES:
        assert phrase in section, f"the standards input lost {phrase!r}"


def test_unavailable_route_stops_the_pass():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 15:
    маршрут роли берётся из реестра; недоступная пара останавливает проход,
    фолбэка на другую модель нет."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _section(_normalized_lower(body), "ревью-панель")
    assert section, "the «Ревью-панель» section is missing"
    for phrase in ROUTE_STOP_PHRASES:
        assert phrase in section, f"the route rule lost {phrase!r}"


def test_projection_gate_holds_before_the_units_first_ship():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 16:
    критик-гейт становится гейтом проекций; юнит не идёт в первый ship без
    записи гейта проекций — отчёта триажа в папке юнита трекера."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _section(_normalized_lower(body), "гейт проекций")
    assert section, "the «Гейт проекций» section is missing"
    for phrase in PROJECTION_GATE_PHRASES:
        assert phrase in section, f"the projection gate lost {phrase!r}"


def test_skill_anchors_to_the_bundle_section():
    """spec: docs/plans/canon-section-in-bundles.md#готово — the skill cites
    its own bundle section; the canon path leaves the body."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "references/method-phases.md" in lowered
    assert "три фазы" in lowered
    assert "docs/decisions/ontoship-core.md" not in lowered


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: docs/plans/harness-agnostic.md#готово — no harness-specific skill root in skill texts."""
    text = SKILL.read_text("utf-8")
    assert root not in text
    leaked = text + f"\nInstall into {root}/skills instead.\n"
    assert any(root in error for error in _contract_errors(leaked))


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check rejects a restored invocation flag, a loop, a fake PR, a
    stop-point regression, an anchor, a missing name, a lost isolated-worktree
    word, the phrase carried out of step 1, the «или ветку» comeback, the
    retired user-only invocation and the retired acceptance ask."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    restored_flag = text.replace("---\n", "---\ndisable-model-invocation: true\n", 1)
    assert restored_flag != text
    assert any("disable-model-invocation" in error
               for error in _contract_errors(restored_flag))

    looped = text.replace("P3 — не долг, а триаж",
                          "повторяй прогоны ревью до нуля находок", 1)
    assert looped != text
    errors = _contract_errors(looped)
    assert any("повторяй прогоны ревью" in error for error in errors)
    assert any("до нуля находок" in error for error in errors)
    assert any("p3 — не долг, а триаж" in error for error in errors)

    fake_pr = text.replace("проход оканчивается локальным коммитом",
                           "создай pull request в удалённый репозиторий", 1)
    assert fake_pr != text
    assert any("создай pull request" in error for error in _contract_errors(fake_pr))

    relocated = text.replace("раздела «Ограничения» спеки",
                             "раздела «Готово» спеки", 1)
    assert relocated != text
    assert any("раздела «ограничения» спеки" in error
               for error in _contract_errors(relocated))

    anchored = text.replace("## Один проход",
                            "## Один проход\n\nСмотри `skills/ship/SKILL.md:42`.", 1)
    assert anchored != text
    assert any("SKILL.md:42" in error for error in _contract_errors(anchored))

    weakened = text.replace("Отдели изолированный worktree", "Отдели worktree", 1)
    assert weakened != text, "mutation must change the text"
    assert any("изолированный worktree" in error
               for error in _contract_errors(weakened))

    moved_out = weakened.replace(
        "## Синхронизация",
        "## Синхронизация\n\nИзолированный worktree обязателен.", 1)
    assert moved_out != weakened
    assert any("step 1" in error for error in _contract_errors(moved_out))

    moved_before = weakened.replace(
        "## Когда использовать",
        "## Когда использовать\n\n**Worktree.** Изолированный worktree "
        "обязателен.", 1)
    assert moved_before != weakened
    assert any("step 1" in error for error in _contract_errors(moved_before))

    reverted = text.replace(
        "worktree от базового коммита",
        "worktree или ветку от базового коммита", 1)
    assert reverted != text
    assert any("или ветку" in error for error in _contract_errors(reverted))

    reverted_header = text.replace('description: "Фаза 3', 'description: "Фаза 3, worktree или ветку', 1)
    assert reverted_header != text
    assert any("или ветку" in error for error in _contract_errors(reverted_header))

    stuffed = text.replace("отчёт фактами стоит в чате перед вызовом",
                           "отчёт фактами входит в поле вопроса", 1)
    assert stuffed != text
    assert any("отчёт фактами стоит в чате перед вызовом" in error
               for error in _contract_errors(stuffed))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))

    # The carrier wraps the phrase at 80 columns; the probe tolerates the
    # wrap so a reflow does not hide the mutation.
    user_only = re.sub(r"Ручной\s+канал\s+—\s+команда\s+`/ship`",
                       "Скилл вызывает только пользователь", text, count=1)
    assert user_only != text
    errors = _contract_errors(user_only)
    assert any("скилл вызывает только пользователь" in error for error in errors)
    assert any("ручной канал — команда `/ship`" in error for error in errors)

    driver_back = text.replace(
        "- Проход один:",
        "- В автономной цепочке оркестратор передаёт тикет исполнителю.\n"
        "- Проход один:", 1)
    assert driver_back != text
    errors = _contract_errors(driver_back)
    assert any("в автономной цепочке" in error for error in errors)
    assert any("оркестратор передаёт тикет" in error for error in errors)

    ask_back = text.replace("Незакрытое или остановка — вопрос оператору",
                            "Приёмка тикета идёт отдельным ask-вопросом", 1)
    assert ask_back != text
    errors = _contract_errors(ask_back)
    assert any("приёмка тикета идёт отдельным ask-вопросом" in error
               for error in errors)
    assert any("незакрытое или остановка — вопрос оператору" in error
               for error in errors)


def test_gate_step_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    gate-step contract rejects a lost runner, a lost no-shell rule, a lost
    expect_exit check, a lost read-the-output order, a lost zero-gates case
    and a gate step carried out of the pass."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    for old, new, needle in (
        ("run_gates.py", "исполнитель бандла", "run_gates.py"),
        ("без shell-интерпретации", "через shell", "без shell-интерпретации"),
        ("expect_exit", "ожидаемый код", "expect_exit"),
        ("Прочитай вывод каждого гейта", "Смотри сводку гейтов",
         "прочитай вывод каждого гейта"),
        ("шаг называет ноль", "шаг молчит", "шаг называет ноль"),
        ("конфиги-данные исполняет ядро", "конфиги исполняет пак",
         "конфиги-данные исполняет ядро"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    no_step = _body_mutated(text, "**Механические гейты пака.**", "**Гейты.**")
    assert any("mechanical-gate step" in error
               for error in _contract_errors(no_step))


def test_auto_acceptance_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    auto-acceptance contract rejects a lost green-contour condition, a lost
    P3 triage, a lost operator question, a blocking P3 and a lost section."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    for old, new, needle in (
        ("критерии приёмки закрыты доказательствами", "критерии закрыты",
         "критерии приёмки закрыты доказательствами"),
        ("панель после одного раунда правок без незакрытых P1/P2",
         "панель без находок", "панель после одного раунда правок без незакрытых p1/p2"),
        ("механические гейты пака зелёные", "гейты пройдены",
         "механические гейты пака зелёные"),
        ("P3 не блокируют автоприёмку", "P3 тоже блокирует юнита",
         "p3 не блокируют автоприёмку"),
        ("Незакрытое или остановка — вопрос оператору",
         "Незакрытое закрывает исполнитель", "незакрытое или остановка — вопрос оператору"),
    ):
        mutated = text.replace(old, new, 1)
        assert mutated != text, f"the mutation must change the text: {old!r}"
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    no_section = text.replace("## Автоприёмка", "## Приёмка", 1)
    assert no_section != text
    assert any("missing section «Автоприёмка»" in error
               for error in _contract_errors(no_section))


def test_route_stop_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    route-stop contract rejects a lost stop on an unavailable pair, a lost
    retry rule and a lost ban on self-review; a planted model-distinctness
    rule reddens."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    for old, new in (
        ("недоступная пара — остановка прохода и вопрос оператору",
         "недоступная пара — выбор другой модели"),
        ("Одна повторная проба, затем остановка прохода",
         "Повторные пробы до сходимости"),
        ("«ревью провёл исполнитель» законным исходом не является",
         "«ревью провёл исполнитель» допустимо"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(old.lower() in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    planted = text + "\nРевьюеры идут на модели, отличной от сессионной.\n"
    assert any("retired model rule" in error
               for error in _contract_errors(planted))


def test_projection_gate_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    projection-gate contract rejects a restored critic gate, a lost record,
    a silent skip and a lost section."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    critic_back = text.replace("## Гейт проекций", "## Критик-гейт", 1)
    assert critic_back != text
    errors = _contract_errors(critic_back)
    assert any("критик-гейт" in error for error in errors)
    assert any("missing section «Гейт проекций»" in error for error in errors)

    no_record = _body_mutated(text, "без записи гейта проекций",
                              "без записи критика")
    assert any("записи гейта проекций" in error
               for error in _contract_errors(no_record))

    silent = _body_mutated(text, "тихий пропуск гейта не делается",
                           "тихий пропуск гейта допустим")
    assert any("тихий пропуск гейта не делается" in error
               for error in _contract_errors(silent))


def test_panel_runs_roles_from_config_in_one_pass():
    """spec: docs/plans/review-config.md#готово — роли из конфига параллельно
    в одном прогоне, исполнитель дедуплицирует находки в один отчёт."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "ревью-панель" in lowered
    assert ".agents/config.toml" in lowered
    assert "параллельно в одном прогоне" in lowered
    assert "один отчёт" in lowered
    assert "дедуплицируй" in lowered
    assert "references/review-panel.md" in lowered


def test_panel_role_input_output_and_independence():
    """spec: docs/plans/review-config.md#готово — вход роли: область и
    чек-лист; выход: вердикт и находки с приоритетами и зацепками;
    независимость — артефакты, не ход исполнения."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "область и чек-лист" in lowered
    assert "вердикт" in lowered
    assert "приоритет" in lowered
    assert "зацепк" in lowered
    assert "артефакты" in lowered
    assert "не ход исполнения" in lowered


def test_panel_checks_routes_and_levels_before_launch():
    """spec: docs/plans/review-config.md#готово — до запуска ролей сверка
    (решение 9 в DSH-виде: генератора определений нет, недоступная пара —
    остановка); процедура запуска живёт в
    references/review-panel.md бандла, скилл ведёт в неё и требует брать
    процедуру оттуда.
    spec: docs/plans/onto-doc.md#готово — сверка расширена с модели до
    модели и уровня (решение 4)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "маршрут и уровень каждой роли" in lowered
    assert "references/review-panel.md" in lowered
    assert "бери её оттуда" in lowered


def test_panel_names_missing_roles():
    """spec: docs/plans/review-config.md#ограничения — роль базового набора
    без секции в конфиге не запускается, а называется в отчёте пропуском.
    spec: docs/plans/standards-autoship.md#готово — «Готово» 3: то же
    правило для ролей паков."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "базового набора" in lowered
    assert "пропуск в отчёте" in lowered
    assert "без секции в конфиге не запускается" in lowered
    assert "молчаливая подмена не делается" in lowered


def test_panel_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    panel contract rejects a lost deduplication order, a lost fallback mark,
    a lost retry-and-stop, a silent role skip, a lost level in the route
    check, a lost pack assembly and a lost projection gate."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_level = text.replace("маршрут и уровень каждой роли",
                            "маршрут каждой роли", 1)
    assert no_level != text
    assert any("маршрут и уровень каждой роли" in error
               for error in _contract_errors(no_level))

    no_dedup = text.replace("Дедуплицируй повторяющиеся находки — ",
                            "Собери находки подряд — ", 1)
    assert no_dedup != text, "mutation must change the text"
    assert any("дедуплицируй" in error for error in _contract_errors(no_dedup))

    no_stop = text.replace("затем остановка прохода", "затем продолжение", 1)
    assert no_stop != text
    assert any("затем остановка" in error for error in _contract_errors(no_stop))

    silent_skip = text.replace("назови её пропуск в отчёте",
                               "запусти её молча", 1)
    assert silent_skip != text
    assert any("пропуск в отчёте" in error
               for error in _contract_errors(silent_skip))

    no_take = text.replace("бери её оттуда", "бери из описания", 1)
    assert no_take != text
    assert any("бери её оттуда" in error for error in _contract_errors(no_take))

    no_packs = text.replace("Панель собирается из ролей ядра и ролей паков",
                            "Панель собирается из ролей ядра", 1)
    assert no_packs != text
    assert any("панель собирается из ролей ядра и ролей паков" in error
               for error in _contract_errors(no_packs))

    no_gate = text.replace("Гейт проекций", "Проверка проекций", 1)
    assert no_gate != text
    assert any("missing section «Гейт проекций»" in error
               for error in _contract_errors(no_gate))


def test_panel_references_come_from_the_bundle():
    """spec: docs/plans/bundle-references.md#готово — контракты и процедуру
    запуска панели скилл берёт из references/review-panel.md своего бандла;
    guard-фраза в шаге: файл бандла — первоисточник, проект переопределяет
    его документом docs/reference/review-panel.md — написал свой, бери его.
    Проектные носители v0.3.0 из шага убраны."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "справочник `references/review-panel.md`" in lowered
    assert "процедура запуска ролей — в том же `references/review-panel.md`" in lowered
    assert "файл бандла — первоисточник" in lowered
    assert "проект переопределяет его документом " \
           "`docs/reference/review-panel.md`" in lowered
    assert "написал свой, бери его" in lowered
    assert "docs/reference/review-roles.md" not in lowered
    assert "docs/reference/harnesses.md" not in lowered


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
    the contract rejects a lost guard phrase, a priority inversion, an
    only-source claim and a renamed override doc (replace probes on the
    exact carrier fragments, case and wrapping included)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_guard = _body_mutated(text, "написал свой, бери его", "берёт проект",
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

    renamed = _body_mutated(text, "docs/reference/review-panel.md",
                            "docs/reference/review-roles.md")
    assert any("проект переопределяет его документом "
               "`docs/reference/review-panel.md`" in error
               for error in _contract_errors(renamed))

    unwrapped = _body_mutated(text,
                              "справочник `references/review-panel.md` "
                              "этого бандла",
                              "справочник матрицы проекта")
    errors = _contract_errors(unwrapped)
    assert any("справочник `references/review-panel.md`" in error
               for error in errors)


def _panel_dsh_section(text: str) -> str:
    """Slice the DSH launch section; empty when its heading is absent.

    The slice is delimited by the DSH heading and the next `###` heading, so a
    phrase that survives only in the Qoder section does not satisfy the DSH
    contract. The text is whitespace-normalized, like the rest of the
    contract checks.
    """
    lowered = _normalized_lower(text)
    start = lowered.find(DSH_PANEL_HEADING)
    if start == -1:
        return ""
    end = lowered.find(" ### ", start + 1)
    if end == -1:
        end = len(lowered)
    return lowered[start:end]


def _panel_errors(text: str) -> list[str]:
    """Return every violated DSH panel contract; empty means the file is sound.

    spec: docs/plans/dsh-adaptation.md#готово — DSH-раздел панели: роль идёт
    через `subagent` (spawn, не `subagent_fork`) с `provider`, `model` и
    `reasoning_effort` из конфига, все роли в одном сообщении, отчёт один и
    дедуплицирован; ZCode-раздел снят вместе с рельсами.
    DSH-фразы ищутся только в DSH-секции, якоря panel-run — по всему файлу.
    """
    lowered = _normalized_lower(text)
    errors: list[str] = []
    section = _panel_dsh_section(text)
    if not section:
        errors.append(f"dsh-panel: missing section {DSH_PANEL_HEADING!r}")
    else:
        for phrase in DSH_PANEL_PHRASES:
            if phrase.lower() not in section:
                errors.append(f"dsh-panel: DSH section lost {phrase!r}")
    if "dsh и qoder — вне плана" in lowered:
        errors.append("dsh-panel: the retired «DSH и Qoder — вне плана» line is back")
    if "qoder" not in lowered:
        errors.append("dsh-panel: the Qoder gap is not named")
    for phrase in test_canon_sync.PANEL_RUN_ANCHORS:
        if phrase.lower() not in lowered:
            errors.append(f"dsh-panel: lost panel-run anchor {phrase!r}")
    if "zcode" in lowered:
        errors.append("dsh-panel: a ZCode section is back")
    return errors


def test_dsh_panel_procedure_is_named():
    """spec: docs/plans/dsh-adaptation.md#готово — «Готово» 3: DSH-раздел
    панели в references/review-panel.md; ZCode-раздел снят с рельсами,
    старая строка «DSH и Qoder — вне плана» заменена Qoder-пробелом."""
    assert _panel_errors(PANEL_FILE.read_text("utf-8")) == []


def test_dsh_ship_branch_is_named():
    """spec: docs/plans/dsh-adaptation.md#готово — «Готово» 3: сверка в ship
    идёт по `list_subagent_models`, сгенерированные определения ролей не
    нужны, ship вызывается как `/ship`, worktree — `create_worktree` или
    `git worktree`."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    for phrase in DSH_SKILL_PHRASES:
        assert phrase in lowered, f"DSH ship branch lost {phrase!r}"


def test_dsh_panel_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the DSH panel contract rejects a lost spawn (guarded as one relation, not
    two tokens), a lost live route check, a lost route-stop rule, a lost
    deduplication, a lost config source, a lost section heading, a lost
    Qoder gap, a resurrected «DSH и Qoder — вне плана» line and a lost
    panel-run anchor."""
    text = PANEL_FILE.read_text("utf-8")
    assert _panel_errors(text) == []

    no_spawn = re.sub(r"spawn, не\s+`subagent_fork`", "spawn и `subagent_fork`",
                      text, count=1)
    assert no_spawn != text
    assert any("spawn, не `subagent_fork`" in error
               for error in _panel_errors(no_spawn))

    no_routes = text.replace("`list_subagent_models`", "`models`", 1)
    assert no_routes != text
    assert any("`list_subagent_models`" in error for error in _panel_errors(no_routes))

    no_stop = text.replace("Недоступная пара — остановка прохода и вопрос оператору",
                           "Недоступная пара — выбор другой модели", 1)
    assert no_stop != text
    assert any("lost panel-run anchor" in error for error in _panel_errors(no_stop))

    zcode_back = text + "\n### zcode — рабочий способ\n\nГенератор пишет определения.\n"
    assert any("ZCode section is back" in error
               for error in _panel_errors(zcode_back))

    no_dedup = text.replace("дедуплицируется", "собирается", 1)
    assert no_dedup != text
    assert any("дедуплицируется" in error for error in _panel_errors(no_dedup))

    no_config = text.replace("берётся из `.agents/config.toml`",
                              "берётся из конфига", 1)
    assert no_config != text
    assert any("`.agents/config.toml`" in error for error in _panel_errors(no_config))

    no_heading = text.replace(f"{DSH_PANEL_HEADING}\n\n", "", 1)
    assert no_heading != text
    assert any("missing section" in error for error in _panel_errors(no_heading))

    no_qoder = text.replace("Qoder", "другой харнесс")
    assert no_qoder != text
    assert any("Qoder" in error for error in _panel_errors(no_qoder))

    resurrected = text.replace("### Qoder — вне плана",
                               "### DSH и Qoder — вне плана", 1)
    assert resurrected != text
    assert any("DSH и Qoder" in error for error in _panel_errors(resurrected))

    rewritten = re.sub(re.escape(test_canon_sync.PANEL_RUN_ANCHORS[0]),
                       "Определение роли задаётся конфигом", text,
                       count=1, flags=re.IGNORECASE)
    assert rewritten != text
    assert any("panel-run anchor" in error
               for error in _panel_errors(rewritten))


def test_dsh_ship_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the ship contract rejects a lost `/ship`, a lost create_worktree, a lost
    live route check, a restored generator requirement and a lost spawn."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_command = text.replace("`/ship`", "`ship`", 1)
    assert no_command != text
    assert any("`/ship`" in error for error in _contract_errors(no_command))

    no_create = text.replace("`create_worktree`", "`git worktree`")
    assert no_create != text
    assert any("`create_worktree`" in error for error in _contract_errors(no_create))

    no_live = text.replace("`list_subagent_models`", "`models`", 1)
    assert no_live != text
    assert any("`list_subagent_models`" in error
               for error in _contract_errors(no_live))

    generator = text.replace("Сгенерированные определения ролей не нужны",
                             "Сгенерированные определения ролей обязательны", 1)
    assert generator != text
    assert any("сгенерированные определения ролей не нужны" in error
               for error in _contract_errors(generator))

    no_fork = text.replace("spawn, не `subagent_fork`",
                           "spawn и `subagent_fork`", 1)
    assert no_fork != text
    assert any("spawn, не `subagent_fork`" in error
               for error in _contract_errors(no_fork))
