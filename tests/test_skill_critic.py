"""Contract for the critic skill (standards-autoship ticket 04).

The bundle keeps the name ``critic`` and is rewritten into the projection
validation skill (plan-gate decision 16): a model-invoked skill the agent
launches right after the spec is approved at the plan gate, before slicing —
one run per unit. The main session generates dynamic semantic slices from the
spec (seed: the critic checklist and the eight plan-validation projections),
each slice runs in a subordinate session (``subagent``, spawn) with a role
prompt and a goal on artifact input; the flash pool is named, the main session
picks the model per slice with a reason in the report, checked against the
live catalog. Findings pass the main session's triage (confirm/reject with a
reason, overengineering check); disputed ones go to the operator via ask. The
triage report in the unit's tracker folder is the projection gate record:
without it slicing does not proceed. The retired plan-critic wording (run
after the last ticket, whole tickets as input, no fallback) stays banned.

The old contract of review-config ticket 03 and the DSH branch of
dsh-adaptation ticket 04 are retired by decision 16: the critic gate becomes
the projection gate, one skill and one gate; their tests left with this
rewrite (canon: docs/decisions/ontoship-core.md#одно правило качества —
a retired rule's tests leave with the same change).

spec: docs/plans/standards-autoship.md#готово — «Готово» 5: скилл critic
      переписан, имя бандла сохраняется; запуск сразу после план-гейта до
      нарезки; динамические срезы, семя, подчинённые сессии, flash-пул,
      выбор модели с причиной, триаж, отчёт — запись гейта проекций
spec: docs/plans/standards-autoship.md#решения план-гейта — решения 15–17:
      пул flash и выбор модели под срез, один скилл и один гейт, порядок
      «проекции до нарезки»
spec: docs/plans/standards-autoship.md#ограничения — проекции не запускаются
      на модели сессии молча: фолбэк называется в отчёте, провал и на
      фолбэке — остановка и вопрос оператору
spec: docs/plans/canon-section-in-bundles.md#готово — шапка критика
      ссылается на методную секцию бандла, не на путь канона
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

REQUIRED_PHRASES = (
    "агент запускает",
    "сразу после утверждения спеки на план-гейте",
    "до нарезки",
    "не командой оператора",
    "один прогон на юнит",
    "docs/plans/<slug>.md",
    "смысловые срезы",
    "динамические",
    "семя генерации",
    "подчинённая сессия",
    "`subagent` (spawn, не `subagent_fork`)",
    "ролевым промптом и целью",
    "вход среза артефактный",
    "не ход исполнения",
    "все срезы стартуют в одном сообщении",
    "триаж",
    "оверинжиниринг",
    "спорное — оператору",
    "отчёт триажа",
    "tickets/<slug>/",
    "запись гейта проекций",
    "без записи гейта нарезка не идёт",
    "решения план-гейта не перепрашиваются",
    "../ship/references/method-phases.md",
    "идентификаторы подчинённых сессий",
)

SEED_HEADING = "семя срезов"
SEED_PHRASES = (
    "чек-лист критика",
    "восемь проекций",
    "покрытость «готово»",
    "связность",
    "рёбра",
    "демо-пути",
    "честность критериев",
    "цена доказательства",
    "покрытие, порядок, доказательства, власть, время, окружение, термины, риск",
)

RUN_HEADING = "исполнение срезов"
POOL_PHRASES = (
    "пул валидации — flash",
    "`deepseek-account/deepseek-flash` с уровнем `max`",
    "`qwen-token-plan/qwen3.8-flash` с уровнем `xhigh`",
    "модель под срез выбирает основная сессия",
    "причина выбора",
    "`list_subagent_models`",
)
SESSION_MODEL_PHRASES = (
    "runtime-контекста",
    "`powered by <model>`",
    "спроси оператора",
    "подтверди модель",
    "нет ни строки, ни подтверждения — остановка и названный пробел",
)
FALLBACK_PHRASES = (
    "молчаливый запуск на модели сессии не делается",
    "провал и на фолбэке — остановка и вопрос оператору",
    "«валидацию провёл исполнитель» законным исходом не является",
)

TRIAGE_HEADING = "триаж"
TRIAGE_PHRASES = (
    "подтверждается или отвергается с причиной",
    "оверинжиниринг",
    "спорное — оператору ask-инструментом хоста",
    "решения план-гейта не перепрашиваются",
)

REPORT_HEADING = "отчёт и гейт проекций"
REPORT_PHRASES = (
    "отчёт триажа — артефакт в папке юнита локального трекера",
    "tickets/<slug>/",
    "он же запись гейта проекций",
    "модели срезов с причинами выбора",
    "идентификаторы подчинённых сессий",
    "находки с вердиктами триажа",
    "без записи гейта нарезка не идёт",
    "to-tickets проверяет её до нарезки",
)

# The retired plan-critic wording (review-config 03, dsh-adaptation 04):
# decision 16 turns the critic gate into the projection gate, decision 17
# moves the run before slicing. Planting any of these back reddens.
RETIRED_PHRASES = (
    "сразу после приёмки последнего тикета",
    "до первого ship",
    "тикеты юнита целиком",
    "нет фолбэка на модель сессии",
    "критик плана",
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
    """Strip matching YAML quotes; the skill keeps its description quoted."""
    if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
        return value[1:-1]
    return value


def _normalized_lower(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower())


def _drop_phrase(text: str, phrase: str) -> str:
    """Remove every occurrence of a phrase regardless of case and internal
    line wrapping (runs of whitespace inside the phrase match any run)."""
    pattern = re.escape(phrase).replace("\\ ", r"\s+")
    return re.sub(pattern, "", text, flags=re.IGNORECASE)


def _section(body: str, heading: str) -> str:
    """Body of one ``## `` section matched case-insensitively by its heading;
    a ``### `` subsection belongs to its parent section."""
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
                      "the projection validation is a model-invoked skill")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")
    for phrase in RETIRED_PHRASES:
        if phrase in lowered:
            errors.append(f"body: retired plan-critic phrase {phrase!r}")

    scoped = (
        (SEED_HEADING, SEED_PHRASES, "seed"),
        (RUN_HEADING, POOL_PHRASES, "pool"),
        (RUN_HEADING, SESSION_MODEL_PHRASES, "session-model"),
        (RUN_HEADING, FALLBACK_PHRASES, "fallback"),
        (TRIAGE_HEADING, TRIAGE_PHRASES, "triage"),
        (REPORT_HEADING, REPORT_PHRASES, "report"),
    )
    for heading, phrases, label in scoped:
        section = _normalized_lower(_section(body, heading))
        if not section:
            errors.append(f"{label}: missing section «{heading}»")
            continue
        for phrase in phrases:
            if phrase not in section:
                errors.append(f"{label}: section «{heading}» lost {phrase!r}")

    # .zcode stays banned here: this skill names no channel roots.
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: имя бандла
    critic сохраняется, скилл переписан в проекционную валидацию."""
    assert SKILL.is_file(), "the critic skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "critic"
    assert SKILL.parent.name == fields["name"], "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_is_model_invoked_before_slicing():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: агент
    запускает проекции сразу после утверждения спеки на план-гейте, до
    нарезки, не командой оператора; один прогон на юнит (решение 17)."""
    fields, body = _parse(SKILL.read_text("utf-8"))
    assert "disable-model-invocation" not in fields
    lowered = _normalized_lower(body)
    assert "агент запускает" in lowered
    assert "сразу после утверждения спеки на план-гейте" in lowered
    assert "до нарезки" in lowered
    assert "не командой оператора" in lowered
    assert "один прогон на юнит" in lowered


def test_slices_are_dynamic_and_generated_from_the_spec():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: основная
    сессия генерирует смысловые срезы из спеки — динамические, не
    фиксированный обход."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "генерирует смысловые срезы из спеки" in lowered
    assert "динамические" in lowered
    assert "семя генерации" in lowered


def test_seed_carries_the_checklist_and_the_eight_projections():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: семя —
    чек-лист критика и восемь проекций прецедента валидации плана; фразы
    ищутся в разделе «Семя срезов»."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, SEED_HEADING))
    assert section, "section «Семя срезов» is missing"
    for phrase in SEED_PHRASES:
        assert phrase in section, f"the seed lost {phrase!r}"


def test_slices_run_in_subordinate_sessions_on_artifact_input():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: каждый
    срез исполняет подчинённая сессия (subagent, spawn) с ролевым промптом
    и целью; вход артефактный, не ход исполнения."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, RUN_HEADING))
    assert section, "section «Исполнение срезов» is missing"
    for phrase in ("подчинённая сессия",
                   "`subagent` (spawn, не `subagent_fork`)",
                   "ролевым промптом и целью",
                   "все срезы стартуют в одном сообщении",
                   "вход среза артефактный",
                   "не ход исполнения"):
        assert phrase in section, f"the run section lost {phrase!r}"


def test_flash_pool_and_per_slice_model_choice():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 15:
    пул flash (deepseek-flash/max, qwen3.8-flash/xhigh), модель под срез
    выбирает основная сессия с причиной в отчёте, сверка с живым каталогом."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, RUN_HEADING))
    assert section, "section «Исполнение срезов» is missing"
    for phrase in POOL_PHRASES:
        assert phrase in section, f"the pool contract lost {phrase!r}"


def test_session_model_comes_from_the_runtime_context():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: сверка с
    живым каталогом; модель сессии — из runtime-контекста, при
    неоднозначности подтверждение оператора, без источника — остановка."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, RUN_HEADING))
    assert section, "section «Исполнение срезов» is missing"
    for phrase in SESSION_MODEL_PHRASES:
        assert phrase in section, f"the session-model contract lost {phrase!r}"


def test_fallback_is_named_and_failure_stops_the_run():
    """spec: docs/plans/standards-autoship.md#ограничения — проекции не
    запускаются на модели сессии молча: фолбэк называется в отчёте, провал
    и на фолбэке — остановка и вопрос оператору."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, RUN_HEADING))
    assert section, "section «Исполнение срезов» is missing"
    for phrase in FALLBACK_PHRASES:
        assert phrase in section, f"the fallback contract lost {phrase!r}"


def test_triage_confirms_or_rejects_with_a_reason():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: триаж
    основной сессии — подтверждение/отвержение с причиной, проверка
    оверинжиниринга; спорное — оператору ask-ом."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, TRIAGE_HEADING))
    assert section, "section «Триаж» is missing"
    for phrase in TRIAGE_PHRASES:
        assert phrase in section, f"the triage contract lost {phrase!r}"


def test_report_is_the_projection_gate_record():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: отчёт
    триажа — артефакт в папке юнита трекера, он же запись гейта проекций;
    без записи нарезка не идёт."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    section = _normalized_lower(_section(body, REPORT_HEADING))
    assert section, "section «Отчёт и гейт проекций» is missing"
    for phrase in REPORT_PHRASES:
        assert phrase in section, f"the report contract lost {phrase!r}"


def test_plan_gate_decisions_are_not_reasked():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 5: триаж не
    перевыбирает решения план-гейта — они приняты оператором."""
    body = _parse(SKILL.read_text("utf-8"))[1]
    lowered = _normalized_lower(body)
    assert "решения план-гейта не перепрашиваются" in lowered


def test_retired_plan_critic_wording_is_banned():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решения
    16–17: критик-гейт становится гейтом проекций, прогон идёт до нарезки;
    снятые формулировки старого критика под запретом контракта — возврат
    любой из них краснит (мутационные пробы)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for phrase in RETIRED_PHRASES:
        planted = text + f"\n{phrase.capitalize()}.\n"
        errors = _contract_errors(planted)
        assert any(f"retired plan-critic phrase {phrase!r}" in error
                   for error in errors), errors


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the contract check rejects a model-invocation flag, a lost gate record,
    a lost triage reason, a leaked harness root and a missing name."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    model_locked = text.replace("---\n", "---\ndisable-model-invocation: true\n", 1)
    assert model_locked != text
    assert any("disable-model-invocation" in error
               for error in _contract_errors(model_locked))

    no_gate = text.replace("Без записи гейта нарезка не идёт",
                           "Нарезка идёт без записи", 1)
    assert no_gate != text
    assert any("без записи гейта нарезка не идёт" in error
               for error in _contract_errors(no_gate))

    no_reason = text.replace("подтверждается\nили отвергается с причиной",
                             "подтверждается\nили отвергается", 1)
    assert no_reason != text
    assert any("подтверждается или отвергается с причиной" in error
               for error in _contract_errors(no_reason))

    no_seed = text.replace("## Семя срезов", "## Список проверок", 1)
    assert no_seed != text
    assert any("missing section «семя срезов»" in error
               for error in _contract_errors(no_seed))

    leaked_install_root = text + "\nЗапусти проекции из .zcode/skills.\n"
    assert any(".zcode" in error for error in _contract_errors(leaked_install_root))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))


@pytest.mark.parametrize("phrase", REQUIRED_PHRASES)
def test_every_required_phrase_has_a_failing_probe(phrase: str) -> None:
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    removing any required phrase, however short, reddens the contract."""
    text = SKILL.read_text("utf-8")
    mutated = _drop_phrase(text, phrase)
    assert mutated != text, f"the mutation must remove {phrase!r}"
    errors = _contract_errors(mutated)
    assert any(f"missing required phrase {phrase!r}" in error
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

    # invariant: the contract check reddens on a relink to the canon path.
    text = SKILL.read_text("utf-8")
    relinked = text.replace("../ship/references/method-phases.md",
                            "docs/decisions/ontoship-core.md")
    assert relinked != text
    assert any("../ship/references/method-phases.md" in error
               for error in _contract_errors(relinked))