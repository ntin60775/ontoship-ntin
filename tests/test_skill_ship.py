"""Contract for the ship skill (workflow-skills ticket 03, review-config
ticket 04, ship-isolation ticket 01).

The bundle must be discoverable as ``<root>/ship/SKILL.md`` and carry the
phase-3 single pass — worktree, implementation, proof tests, exactly one
review pass, dev/prod checks, merge — with stop points read from the spec's
«Ограничения» section, review yielding leads instead of a convergence loop,
and honest degradation without a remote: a local commit and a named gap,
never a faked PR.

Step one demands an isolated worktree unconditionally (ship-isolation
ticket 01): the phrase «изолированный worktree» lives in step 1 of the
«Один проход» section, and the permissive «или ветку» is forbidden
anywhere in the skill file, frontmatter included.

The review pass runs as a specialists panel (review-config ticket 04): roles
from ``.agents/config.toml`` run in parallel in one pass, the executor
deduplicates findings into one report; a role's input is its scope and
checklist, its output a verdict and findings with priorities and leads;
independence is artifacts, never the run's story. Definition models are
checked against the config before launch and regenerated on drift
(decision 9); the check covers the model and the reasoning level (onto-doc
decision 4). An unavailable role model falls back to the session model,
marked in the report (decision 14); a failure on the fallback too means one
retry and a stop (decision 4); a base-set role missing from the config is a
named gap in the report, not a silent skip; the critic gate must hold before
a unit's first ship.

spec: docs/plans/workflow-skills.md#готово — skills/ship/SKILL.md
spec: docs/plans/workflow-skills.md#ограничения — ship is model-inaccessible
spec: docs/decisions/ontoship-core.md#три фазы — one pass, stop points from
«Ограничения», review gives leads
spec: docs/plans/review-config.md#готово — ship ведёт ревью панелью
spec: docs/plans/review-config.md#ограничения — панель один прогон,
пропущенная роль названа, критик-гейт перед первым ship юнита
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

import test_canon_sync  # reuse: the ZCode panel-run anchors, not duplicated

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "ship" / "SKILL.md"
PANEL_FILE = REPO / "skills" / "ship" / "references" / "review-panel.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
ANCHOR_RE = re.compile(r"\b[\w-]+(?:\.[\w-]+)+:\d+")
PASS_STEPS = ("**worktree", "**реализация", "**доказательные тесты",
              "**один прогон ревью", "**проверки dev и prod", "**merge")
REQUIRED_PHRASES = (
    "один проход",
    "worktree",
    "доказательные тесты",
    "один прогон ревью",
    "зацепки, а не цикл сходимости",
    "исправь названные находки",
    "доложи остальные",
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
    "вызывает пользователь",
)
FORBIDDEN_PHRASES = (
    "повторяй прогоны ревью",
    "до нуля находок",
    "создай pull request",
    "или ветку",
    "файл проекта — первоисточник",
    "единственный источник",
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
    "фолбэк на модель сессии",
    "пометкой в отчёте",
    "повторная проба",
    "затем остановка",
    "базового набора",
    "пропуск в отчёте",
    "критик-гейт",
    "до первого ship юнита",
    "запись прогона",
    "references/review-panel.md",
    "справочник `references/review-panel.md`",
    "процедура запуска ролей — в том же `references/review-panel.md`",
    "файл бандла — первоисточник",
    "проект переопределяет его документом `docs/reference/review-panel.md`",
    "написал свой, бери его",
    "бери её оттуда",
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
    "какая роль и почему пошла на модели сессии",
)
DSH_PANEL_PHRASES = DSH_COMMON_PHRASES + (
    "`.agents/config.toml`",
    "дедуплицируется",
    "фолбэк на модель сессии с пометкой",
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
    if fields.get("disable-model-invocation", "").lower() != "true":
        errors.append("frontmatter: disable-model-invocation must be true "
                      "(the model never invokes this skill)")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    if "изолированный worktree" not in _pass_step_one(lowered):
        errors.append("body: step 1 must demand «изолированный worktree»")
    for phrase in PANEL_PHRASES:
        if phrase not in lowered:
            errors.append(f"panel: missing required phrase {phrase!r}")
    for phrase in DSH_SKILL_PHRASES:
        if phrase not in lowered:
            errors.append(f"dsh: missing required phrase {phrase!r}")
    full_text = _normalized_lower(text)
    for phrase in FORBIDDEN_PHRASES:
        if phrase in full_text:
            errors.append(f"body: forbidden convergence-loop or PR-imitation "
                          f"phrase {phrase!r}")
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


def test_skill_is_user_invoked_only():
    """spec: docs/plans/workflow-skills.md#ограничения — ship is model-inaccessible."""
    fields, body = _parse(SKILL.read_text("utf-8"))
    assert fields.get("disable-model-invocation", "").lower() == "true"
    lowered = _normalized_lower(body)
    assert "вызывает пользователь" in lowered
    assert "модель его не вызывает" in lowered
    assert "может звать модельные скиллы" in lowered
    assert "не другой пользовательский" in lowered


def test_skill_carries_the_single_pass():
    """spec: docs/decisions/ontoship-core.md#три фазы — one pass, steps in order."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    positions = [lowered.find(step) for step in PASS_STEPS]
    assert all(position >= 0 for position in positions), \
        f"a pass step is missing: {list(zip(PASS_STEPS, positions))}"
    assert positions == sorted(positions), \
        "the pass steps must appear in worktree → … → merge order"


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
    """spec: docs/plans/workflow-skills.md#готово — stop points from «Ограничения»."""
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
    assert "исправь названные находки" in lowered
    assert "доложи остальные" in lowered
    assert "остановись" in lowered
    for phrase in FORBIDDEN_PHRASES[:2]:
        assert phrase not in lowered, f"convergence-loop phrase {phrase!r} leaked"


def test_degradation_without_remote_is_honest():
    """spec: docs/plans/workflow-skills.md#готово — local commit and named gap."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "git remote -v" in lowered
    assert "локальный коммит" in lowered
    assert "названный пробел" in lowered
    assert "не имитируй" in lowered
    assert "создай pull request" not in lowered


def test_acceptance_ask_carries_the_decision_not_the_report():
    """invariant: docs/decisions/ontoship-core.md#три фазы — the acceptance ask
    carries the decision, not the report; the factual report stays in chat
    before the call, option descriptions carry consequences."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "приёмка тикета идёт отдельным ask-вопросом" in lowered
    assert "отчёт фактами стоит в чате перед вызовом" in lowered
    assert "в поле вопроса — одно предложение" in lowered
    assert "следствия выбора, не доказательства" in lowered


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
    contract check rejects a missing flag, a loop, a fake PR, a stop-point
    regression, an anchor, a missing name, a lost isolated-worktree word,
    the phrase carried out of step 1 (into the intro or another section),
    and the «или ветку» comeback."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_flag = "\n".join(line for line in text.splitlines()
                             if not line.startswith("disable-model-invocation:"))
    assert missing_flag != text
    assert any("disable-model-invocation" in error
               for error in _contract_errors(missing_flag))

    looped = text.replace("доложи остальные",
                          "повторяй прогоны ревью до нуля находок", 1)
    assert looped != text
    errors = _contract_errors(looped)
    assert any("повторяй прогоны ревью" in error for error in errors)
    assert any("до нуля находок" in error for error in errors)
    assert any("доложи остальные" in error for error in errors)

    fake_pr = text.replace("локальным коммитом в целевую ветку",
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
        "## Деградация без remote",
        "## Деградация без remote\n\nИзолированный worktree обязателен.", 1)
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
    (решение 9 в DSH-виде: генератора определений нет, расхождение —
    фолбэк, не перегенерация); процедура запуска живёт в
    references/review-panel.md бандла, скилл ведёт в неё и требует брать
    процедуру оттуда.
    spec: docs/plans/onto-doc.md#готово — сверка расширена с модели до
    модели и уровня (решение 4)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "маршрут и уровень каждой роли" in lowered
    assert "references/review-panel.md" in lowered
    assert "бери её оттуда" in lowered


def test_panel_fallback_is_marked_and_failure_stops():
    """spec: docs/plans/review-config.md#готово — недоступная модель роли:
    фолбэк на модель сессии с пометкой в отчёте (решение 14); провал и на
    фолбэке — одна повторная проба, затем остановка (решение 4)."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "фолбэк на модель сессии" in lowered
    assert "пометкой в отчёте" in lowered
    assert "повторная проба" in lowered
    assert "затем остановка" in lowered


def test_panel_names_missing_base_set_roles():
    """spec: docs/plans/review-config.md#ограничения — роль базового набора
    без секции в конфиге не запускается, а называется в отчёте пропуском."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "базового набора" in lowered
    assert "пропуск в отчёте" in lowered


def test_critic_gate_holds_before_the_units_first_ship():
    """spec: docs/plans/review-config.md#ограничения — критик-гейт: юнит не
    идёт в первый ship без прогона критика; проход подтверждает гейт ссылкой
    на запись прогона."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "критик-гейт" in lowered
    assert "до первого ship юнита" in lowered
    assert "запись прогона" in lowered


def test_panel_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    panel contract rejects a lost deduplication order, a lost fallback mark,
    a lost retry-and-stop, a silent base-set skip, a lost regeneration, a
    lost level in the definition check and a lost critic gate."""
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

    unmarked = text.replace("с пометкой в отчёте", "без пометки", 1)
    assert unmarked != text
    assert any("пометкой в отчёте" in error
               for error in _contract_errors(unmarked))

    no_stop = text.replace("затем остановка прохода", "затем продолжение", 1)
    assert no_stop != text
    assert any("затем остановка" in error for error in _contract_errors(no_stop))

    silent_skip = text.replace("назови её пропуск в отчёте",
                               "запусти её на модели сессии", 1)
    assert silent_skip != text
    assert any("пропуск в отчёте" in error
               for error in _contract_errors(silent_skip))

    no_take = text.replace("бери её оттуда", "бери из описания", 1)
    assert no_take != text
    assert any("бери её оттуда" in error
               for error in _contract_errors(no_take))

    no_gate = text.replace("Критик-гейт", "Проверка критика", 1)
    assert no_gate != text
    assert any("критик-гейт" in error for error in _contract_errors(no_gate))


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
    phrase that survives only in the ZCode or Qoder section does not satisfy
    the DSH contract. The text is whitespace-normalized, like the rest of the
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
    дедуплицирован, недоступная модель — фолбэк на модель сессии с пометкой,
    провал — повторная проба и остановка; ZCode-раздел снят вместе с рельсами,
    старая строка «DSH и Qoder — вне плана» заменена Qoder-пробелом.
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
    two tokens), a lost live route check, a lost fallback mark, a lost
    deduplication, a lost config source, a lost section heading, a lost Qoder
    gap, a resurrected «DSH и Qoder — вне плана» line and a lost ZCode
    anchor."""
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

    no_fallback = text.replace("фолбэк на модель сессии с пометкой",
                               "фолбэк на модель сессии", 1)
    assert no_fallback != text
    assert any("фолбэк на модель сессии с пометкой" in error
               for error in _panel_errors(no_fallback))

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

    rewritten = text.replace(test_canon_sync.PANEL_RUN_ANCHORS[0],
                             "Определение роли задаётся конфигом", 1)
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
