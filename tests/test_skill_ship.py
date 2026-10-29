"""Contract for the ship skill (workflow-skills ticket 03, review-config ticket 04).

The bundle must be discoverable as ``<root>/ship/SKILL.md`` and carry the
phase-3 single pass — worktree, implementation, proof tests, exactly one
review pass, dev/prod checks, merge — with stop points read from the spec's
«Ограничения» section, review yielding leads instead of a convergence loop,
and honest degradation without a remote: a local commit and a named gap,
never a faked PR.

The review pass runs as a specialists panel (review-config ticket 04): roles
from ``.agents/config.toml`` run in parallel in one pass, the executor
deduplicates findings into one report; a role's input is its scope and
checklist, its output a verdict and findings with priorities and leads;
independence is artifacts, never the run's story. Definition models are
checked against the config before launch and regenerated on drift
(decision 9); an unavailable role model falls back to the session model,
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
invariant: docs/decisions/ontoship-core.md#три фазы — one review pass, no convergence loop
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "ship" / "SKILL.md"
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
    "docs/decisions/ontoship-core.md",
    "три фазы",
    "вызывает пользователь",
)
FORBIDDEN_PHRASES = (
    "повторяй прогоны ревью",
    "до нуля находок",
    "создай pull request",
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
    "модель определения",
    "перегенерируй",
    "фолбэк на модель сессии",
    "пометкой в отчёте",
    "повторная проба",
    "затем остановка",
    "базового набора",
    "пропуск в отчёте",
    "критик-гейт",
    "до первого ship юнита",
    "запись прогона",
    "docs/reference/review-roles.md",
    "docs/reference/harnesses.md",
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
    if fields.get("disable-model-invocation", "").lower() != "true":
        errors.append("frontmatter: disable-model-invocation must be true "
                      "(the model never invokes this skill)")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for phrase in PANEL_PHRASES:
        if phrase not in lowered:
            errors.append(f"panel: missing required phrase {phrase!r}")
    for phrase in FORBIDDEN_PHRASES:
        if phrase in lowered:
            errors.append(f"body: forbidden convergence-loop or PR-imitation "
                          f"phrase {phrase!r}")
    anchor = ANCHOR_RE.search(text)
    if anchor:
        errors.append(f"body: file:line anchor {anchor.group(0)!r}")
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


def test_skill_anchors_to_the_canon():
    """spec: docs/decisions/ontoship-core.md#три фазы — the skill cites its phase."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "docs/decisions/ontoship-core.md" in lowered
    assert "три фазы" in lowered


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
    regression, an anchor, and a missing name."""
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
    assert "docs/reference/review-roles.md" in lowered


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


def test_panel_checks_definitions_before_launch():
    """spec: docs/plans/review-config.md#готово — до запуска ролей сверка
    модели определения с конфигом, расхождение — перегенерация (решение 9);
    способы запуска живут в матрице харнессов, не в тексте скилла."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "модель определения" in lowered
    assert "перегенерируй" in lowered
    assert "docs/reference/harnesses.md" in lowered


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
    a lost retry-and-stop, a silent base-set skip, a lost regeneration and a
    lost critic gate."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

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

    no_regen = text.replace("перегенерируй", "перепиши", 1)
    assert no_regen != text
    assert any("перегенерируй" in error
               for error in _contract_errors(no_regen))

    no_gate = text.replace("Критик-гейт", "Проверка критика", 1)
    assert no_gate != text
    assert any("критик-гейт" in error for error in _contract_errors(no_gate))
