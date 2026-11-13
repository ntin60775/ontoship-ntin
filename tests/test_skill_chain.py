"""Contract for the chain skill (standards-autoship ticket 06).

The bundle must be discoverable as ``<root>/chain/SKILL.md`` and carry the
autonomous-chain orchestrator of decision 13: a clean session started by the
operator command after the accepted slicing and the projection gate, tickets
led in blocking-edge order, ONE continuable executor session receiving the
tickets sequentially via ``send_message`` (a new executor per ticket is
forbidden), compact fact reports, green-contour verification and recorded
auto-acceptance with the leads register. Budget guards of both orchestrator
and executor work by volume estimate and a conservative threshold — the token
counter is unavailable to the agent (a named gap); executor retirement with a
handoff prompt happens at a ticket boundary; there is no compaction. An
exception stops the chain and transfers the state to continue.md. The final
report (decision 14, «Готово» 11) is a fact report with the spec's «Готово»
items proven, demo paths, gaps, the leads register and mermaid diagrams of key
decisions and use cases; its durable copy lives in the unit's tracker folder.
The orchestrator only writes the durable copy and ends the chain: the
planning-session agent presents and defends the decision from that copy (the
operator transfers it; there is no cross-session messaging), acceptance is
the ask «принять/вернуть» and a return opens work on the findings.

The managed init block names the chain launch command («Готово» 9): that
contract lives in test_skill_init.py (the BLOCK literal and ENTRY_RULES);
the bundle-list parity of eleven names lives in test_install.py.

spec: docs/plans/standards-autoship.md#готово — «Готово» 7, 11, 9: бандл
chain, финальный отчёт, команда запуска в блоке init
spec: docs/plans/standards-autoship.md#готово — «Готово» 15 (тикет 09,
решение 20): скилл называет источник инициирующего промпта — сессия
планирования пишет его в continue.md («Стартовый промпт») финальным шагом
to-tickets или командой «орк-промт», оператор переносит промпт в новую
корневую сессию оркестратора; промпт — указатель, не пересказ
spec: docs/plans/standards-autoship.md#решения план-гейта — решения 12, 13,
14: носитель цепочки, архитектура (чистая сессия, один продолжаемый
исполнитель, стражи бюджета, пенсия, остановка, компакта нет), финишная
приёмка с отчётом и защитой решения
spec: docs/plans/standards-autoship.md#ограничения — компакта нет, счётчик
токенов недоступен, живая проба в temp-проекте
spec: docs/plans/team-profiles.md#готово — «Готово» 3 и 5 (тикет 03):
выбор исполнителя по указателю стека и реестру, дефолт `executor`,
неоднозначность — остановка с вопросом; маршрут per-call через `read`
реестра в полной форме, `agentOptions` — страховка; решения 5 и 16.
invariant: docs/plans/harness-agnostic.md#готово — skill texts name no harness root
invariant: docs/decisions/ontoship-core.md#одно правило качества — the
contract check can fail (mutations redden)
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "chain" / "SKILL.md"
NAME_RE = re.compile(r"[a-z0-9]+(?:-[a-z0-9]+)*")
DESCRIPTION_MAX = 500
ANCHOR_RE = re.compile(r"\b[\w-]+(?:\.[\w-]+)+:\d+")

# Whole-body anchors: the model invocation, the clean-session start with the
# operator command, the method-section reference with its guard phrase.
REQUIRED_PHRASES = (
    "скилл вызывает модель",
    "ручной вызов `/ship`",
    "чистой сессии по команде оператора «цепочка»",
    "один юнит за запуск",
    "один тикет за проход ship",
    "новая сессия без контекста планирования",
    "корневая сессия хоста, открытая оператором",
    "не субагент сессии планирования",
    "связаны только файлами",
    "межсессионного messaging и управления нет",
    "../ship/references/method-phases.md",
    "файл бандла — первоисточник",
    "проект переопределяет его документом `docs/reference/method-phases.md`",
    "написал свой, бери его",
    "docs/plans/<slug>.md",
    "docs/ops/continue.md",
    "tickets/<slug>/",
)
# «Вход и порядок рёбер»: the projection-gate record and the slicing
# acceptance gate the entry, the blocking-edge order leads the tickets.
ENTRY_PHRASES = (
    "запись гейта проекций",
    "отчёт триажа",
    "записи нет — остановка и вопрос оператору",
    "тихий пропуск гейта не делается",
    "нарезка не принята оператором (записи приёмки в тикетах или continue.md нет) — остановка и вопрос",
    "по блокирующим рёбрам",
    "после всех своих блокеров",
    "в порядке публикации",
    "последовательный порядок сохраняется",
)
# «Исполнитель»: one continuable session, sequential handover, compact fact
# reports, the green contour verified on artifacts, recorded auto-acceptance.
EXECUTOR_PHRASES = (
    "одна продолжаемая подчинённая сессия-исполнитель",
    "последовательно",
    "`subagent`",
    "spawn, не `subagent_fork`",
    "`send_message`",
    "по одному",
    "новый исполнитель на каждый тикет не спавнится",
    "скиллом `ship`",
    "один проход от worktree до merge",
    "компактный, фактами",
    "рассказ не заменяет артефактов",
    "проверяет зелёные гейты по артефактам",
    "критерии приёмки закрыты доказательствами",
    "панель после одного прохода правок без незакрытых p1/p2",
    "проверки dev/prod пройдены",
    "механические гейты пака зелёные",
    "точки остановки спеки пройдены",
    "фиксирует автоприёмку записью в тикете трекера",
    "p3 уходят в реестр зацепок юнита",
    "незакрытое или остановка — вопрос оператору",
    "автоприёмка не делается, цепочка стоит",
)
# «Стражи бюджета»: the named token-counter gap, volume estimate and the
# conservative threshold, retirement with handoff at the ticket boundary,
# the orchestrator guard, no compaction.
BUDGET_PHRASES = (
    "счётчик токенов агенту недоступен",
    "названный пробел",
    "inspector-profile",
    "стражи бюджета оркестратора и исполнителя",
    "по оценке объёма и консервативному порогу",
    "порог называется в финальном отчёте",
    "на границе тикета, не внутри прохода",
    "пенсия исполнителя",
    "handoff-промптом",
    "handoff-промпт — вход новой сессии",
    "компакта нет",
    "страж оркестратора",
    "остановка цепочки с передачей состояния в continue.md",
    "замена оркестратора — новая чистая сессия по команде оператора",
)
# «Остановка цепочки»: an exception stops the chain, the state goes to
# continue.md, the operator gets the question, resuming is a clean session.
STOP_PHRASES = (
    "исключение",
    "останавливает цепочку",
    "«открытая работа»",
    "юнит, тикет, на чём остановились, что дальше",
    "вопрос оператору",
    "возобновление — по команде оператора в чистой сессии",
    "тихое продолжение после исключения не делается",
)
# «Финальный отчёт и приёмка»: the report form of decision 14 — an
# independent pin of the required items, not a re-extraction from the skill.
# The orchestrator fixes the durable copy and ends the chain; the planning
# session's agent presents and defends it (file-only link, decision 13).
REPORT_PHRASES = (
    "финальный отчёт фактами",
    "пункты «готово» спеки с доказательствами",
    "демо-пути тикетов и их прогоны",
    "пробелы — названные, не выдуманные",
    "реестр зацепок юнита",
    "mermaid-диаграммы ключевых решений и юз-кейсов",
    "durable-копия отчёта",
    "оркестратор фиксирует её и завершает цепочку",
    "презентацию, защиту решения и ask несёт агент сессии планирования",
    "оператор переносит отчёт в сессию планирования",
    "приёмка — ask «принять/вернуть»",
    "в поле вопроса — одно предложение с решением",
    "в описаниях вариантов — следствия выбора",
    "возврат открывает работу по находкам",
    "отчёт фактами стоит в чате перед вызовом",
)
# «Визуализация»: one ticket-DAG is the source of truth; the orchestrator
# computes TWO derived static views (decision 19) and keeps them in the unit's
# tracker folder: the graph is a mermaid block, the Kanban a markdown table.
# blocked is computed from the edges; the ready-frontier is computed and read
# from the Kanban ready column, not rendered as a separate third block;
# Temporal status colors, no host code. The live DSH panel is the external
# plugin ontoship-chain-board: the orchestrator calls its tool once at the
# chain start and the board opens only in the orchestrator session (operator
# decision 2026-11-12); the ReactFlow+ELK panel stays a future unit.
VIZ_PHRASES = (
    "источник истины — тикеты и блокирующие рёбра",
    "оркестратор вычисляет виды",
    "не ведёт их отдельно",
    "два производных вида",
    "граф зависимостей — mermaid-блок",
    "kanban — markdown-таблица",
    "колонку blocked оркестратор вычисляет",
    "не проставляет руками",
    "ready-frontier читается колонкой ready",
    "отдельный третий блок не рендерится",
    "цвета статусов — лексика temporal",
    "mermaid",
    "рендерит виды из тикетов",
    "без кода хоста",
    "живая панель dsh — внешний плагин",
    "один раз вызывает инструмент",
    "`ontoship_board_open`",
    "доска открывается в сессии оркестратора",
    "исполнитель и сессия планирования инструмент не вызывают",
    "инструмента нет в сессии — назови пробел",
    "доска — визуализация, не гейт",
)
FORBIDDEN_PHRASES = (
    # the retired or rejected flows: a user-only orchestrator, compaction,
    # a fresh executor per ticket, parallel tickets, acceptance without the
    # report, the retired critic gate.
    "disable-model-invocation",
    "компактируй",
    "сжимай контекст",
    "спавни нового исполнителя на каждый тикет",
    "тикеты идут параллельно",
    "тикеты параллельно",
    "параллельные исполнители",
    "приёмка словом без отчёта",
    "живое демо перед ask",
    "критик-гейт",
    "zcode",
    "gen_agents",
    "план-мод",
)
# «Когда использовать»: the entry-prompt source (decision 20) — the planning
# session writes the prompt into continue.md («Стартовый промпт») via the
# final to-tickets step or the manual command «орк-промт»; the operator
# transfers it to the new root orchestrator session; the prompt is a pointer
# (command, unit address, state pointer), not a state retelling.
SOURCE_PHRASES = (
    "инициирующий промпт пишет сессия планирования",
    "«стартовый промпт»",
    "финальный шаг to-tickets",
    "«орк-промт»",
    "оператор переносит промпт",
    "указатель на состояние",
    "не пересказ",
)
# «Выбор исполнителя» (тикет 03 team-profiles): preset and route are chosen
# once per continuable session — at spawn and at retirement/handoff, not per
# ticket; the stack signal is the architect's pointer in the spec/continue.md;
# the registry route is read per-call in full provider/model+level form;
# ambiguity stops the chain with a question; the selection is named in the
# report (candidates, id, reason); agentOptions is the fallback, not the
# source; the reviewer panel registry stays in .agents/config.toml.
SELECTION_PHRASES = (
    "указатель архитектора",
    "спеке юнита или `continue.md`",
    "`исполнитель: <id>`",
    "`<profile>/ontoship/executors.json`",
    "`{id, provider, model, level}`",
    "allowlist заморожен при apply",
    "маршруты читаются live",
    "id из реестра",
    "кандидаты — универсальный `executor` и стековый `1c-executor`",
    "дефолт `executor`",
    "неоднозначность: остановка с вопросом",
    "тихий выбор не делается",
    "при спавне сессии-исполнителя и при пенсии/handoff",
    "не на каждый тикет",
    "per-call",
    "`read` реестра",
    "`provider/model` плюс level",
    "полями вызова",
    "`agentoptions`",
    "страховка, не источник маршрута",
    "выбор называется в отчёте: кандидаты, выбранный id и причина",
    "`.agents/config.toml`",
)
WHEN_HEADING = "когда использовать"
ENTRY_HEADING = "вход и порядок рёбер"
EXECUTOR_HEADING = "исполнитель"
SELECTION_HEADING = "выбор исполнителя"
BUDGET_HEADING = "стражи бюджета"
STOP_HEADING = "остановка цепочки"
REPORT_HEADING = "финальный отчёт и приёмка"
VIZ_HEADING = "визуализация: один dag — производные виды"


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
                      "the chain orchestrator is a model skill "
                      "(standards-autoship decision 12)")

    lowered = _normalized_lower(body)
    for phrase in REQUIRED_PHRASES:
        if phrase not in lowered:
            errors.append(f"body: missing required phrase {phrase!r}")

    when = _section(lowered, WHEN_HEADING)
    if not when:
        errors.append("when: missing section «Когда использовать»")
    else:
        if "чистой сессии по команде оператора «цепочка»" not in when:
            errors.append("when: the clean-session operator command «цепочка» "
                          "left the section")
        for phrase in SOURCE_PHRASES:
            if phrase not in when:
                errors.append(f"when: section «Когда использовать» lost {phrase!r}")

    for heading, label, phrases in (
        (ENTRY_HEADING, "entry", ENTRY_PHRASES),
        (EXECUTOR_HEADING, "executor", EXECUTOR_PHRASES),
        (SELECTION_HEADING, "selection", SELECTION_PHRASES),
        (BUDGET_HEADING, "budget", BUDGET_PHRASES),
        (STOP_HEADING, "stop", STOP_PHRASES),
        (REPORT_HEADING, "report", REPORT_PHRASES),
        (VIZ_HEADING, "viz", VIZ_PHRASES),
    ):
        section = _section(lowered, heading)
        if not section:
            errors.append(f"{label}: missing section «{heading}»")
            continue
        for phrase in phrases:
            if phrase not in section:
                errors.append(f"{label}: section «{heading}» lost {phrase!r}")

    full_text = _normalized_lower(text)
    for phrase in FORBIDDEN_PHRASES:
        if phrase in full_text:
            errors.append(f"body: forbidden retired-flow phrase {phrase!r}")
    anchor = ANCHOR_RE.search(text)
    if anchor:
        errors.append(f"body: file:line anchor {anchor.group(0)!r}")
    for root in (".dsh", ".zcode", ".qoder"):
        if root in text:
            errors.append(f"forbidden harness root {root!r}")
    return errors


def _body_mutated(text: str, old: str, new: str, count: int = 1) -> str:
    """Replace a phrase in the body, tolerating the 80-column wrap: runs of
    whitespace inside the phrase match any run. The mutation must change the
    text; the caller asserts the contract reddens."""
    pattern = re.escape(old).replace("\\ ", r"\s+")
    mutated = re.sub(pattern, new, text, count=count, flags=re.IGNORECASE)
    assert mutated != text, f"the mutation must change the text: {old!r}"
    return mutated


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 7: новый
    модельный скилл-оркестратор, бандл chain."""
    assert SKILL.is_file(), "the chain skill is missing"
    fields, _ = _parse(SKILL.read_text("utf-8"))
    assert fields["name"] == "chain"
    assert SKILL.parent.name == fields["name"], \
        "bundle directory must match the skill name"
    assert 3 <= len(_unquote(fields["description"])) <= DESCRIPTION_MAX
    assert _contract_errors(SKILL.read_text("utf-8")) == []


def test_skill_is_model_invoked():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 12:
    носитель цепочки — модельный скилл-оркестратор; ручной `/ship` на один
    тикет сохраняется вне цепочки."""
    text = SKILL.read_text("utf-8")
    fields, body = _parse(text)
    assert "disable-model-invocation" not in fields
    lowered = _normalized_lower(body)
    assert "скилл вызывает модель" in lowered
    assert "ручной вызов `/ship`" in lowered


def test_clean_session_start_and_operator_command():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 13:
    оркестратор всегда в чистой сессии; старт по команде оператора после
    нарезки и гейта проекций. Чистая сессия — корневая сессия хоста,
    открытая оператором, не субагент планирования; планирование и
    оркестратор связаны только файлами (вариант 1, решение 19)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    lowered = _normalized_lower(text)
    when = _section(lowered, WHEN_HEADING)
    assert "чистой сессии по команде оператора «цепочка»" in when
    assert "новая сессия без контекста планирования" in when
    assert "корневая сессия хоста, открытая оператором" in when
    assert "не субагент сессии планирования" in when
    assert "связаны только файлами" in when

    renamed = _body_mutated(text, "по команде оператора «цепочка»",
                            "по команде оператора «chain-run»")
    assert any("«цепочка»" in error for error in _contract_errors(renamed))

    forked = _body_mutated(text, "новая сессия без контекста планирования",
                           "сессия с контекстом планирования")
    assert any("без контекста планирования" in error
               for error in _contract_errors(forked))

    subagent_orch = _body_mutated(
        text, "корневая сессия хоста, открытая оператором",
        "субагент сессии планирования")
    assert any("корневая сессия хоста" in error
               for error in _contract_errors(subagent_orch))


def test_prompt_source_is_named():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 15 (тикет 09,
    решение 20): скилл называет источник инициирующего промпта — сессия
    планирования пишет его в continue.md («Стартовый промпт») финальным
    шагом to-tickets после приёмки нарезки и самопроверки или ручной
    командой «орк-промт»; оператор переносит промпт в новую корневую
    сессию оркестратора; промпт — команда «цепочка», адрес юнита и
    указатель на состояние, не пересказ. Мутации: потеря источника,
    переноса оператором, указателя и ручной команды краснят контракт."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    when = _section(_normalized_lower(_parse(text)[1]), WHEN_HEADING)
    for phrase in SOURCE_PHRASES:
        assert phrase in when, f"the phrase {phrase!r} left «Когда использовать»"

    for old, new, needle in (
        ("Инициирующий промпт пишет сессия планирования",
         "Инициирующий промпт пишет оркестратор",
         "инициирующий промпт пишет сессия планирования"),
        ("финальный шаг to-tickets", "шаг ship", "финальный шаг to-tickets"),
        ("Оператор переносит промпт", "Промпт передаётся автоматически",
         "оператор переносит промпт"),
        ("указатель на состояние, не пересказ",
         "пересказ состояния", "указатель на состояние"),
        ("«орк-промт»", "«орк-промпт»", "«орк-промт»"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    no_source = _body_mutated(
        text, "Инициирующий промпт пишет сессия планирования", "")
    errors = _contract_errors(no_source)
    assert any("инициирующий промпт пишет сессия планирования" in error
               for error in errors)


def test_entry_checks_projection_gate_and_edges():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 7: читает
    continue.md, тикеты и спеку, ведёт тикеты в порядке рёбер; запись гейта
    проекций и приёмка нарезки — входные гейты chain."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for old, new, needle in (
        ("Сверь запись гейта проекций", "Сверь отчёт критика",
         "запись гейта проекций"),
        ("Записи нет — остановка и вопрос оператору",
         "Записи нет — продолжай", "записи нет — остановка и вопрос оператору"),
        ("тихий пропуск гейта не делается", "пропуск гейта допустим",
         "тихий пропуск гейта не делается"),
        ("Нарезка не принята оператором", "Нарезку принимать не нужно",
         "нарезка не принята оператором"),
        ("по блокирующим рёбрам", "по алфавиту", "по блокирующим рёбрам"),
        ("после всех своих блокеров", "до своих блокеров",
         "после всех своих блокеров"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))


def test_one_continuable_executor_sequential():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 13:
    одна продолжаемая подчинённая сессия-исполнитель ведёт тикеты
    последовательно; передача через send_message, новый исполнитель на
    тикет не спавнится."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for old, new, needle in (
        ("Одна продолжаемая подчинённая сессия-исполнитель",
         "Новая подчинённая сессия на каждый тикет",
         "одна продолжаемая подчинённая сессия-исполнитель"),
        ("через `send_message`", "новым спавном", "`send_message`"),
        ("Новый исполнитель на каждый тикет не спавнится",
         "Новый исполнитель спавнится на каждый тикет",
         "новый исполнитель на каждый тикет не спавнится"),
        ("передаёт тикеты по одному", "передаёт все тикеты сразу",
         "по одному"),
        ("Отчёт исполнителя оркестратору — компактный, фактами",
         "Отчёт исполнителя — подробный рассказ", "компактный, фактами"),
        ("Рассказ не заменяет артефактов", "Рассказ заменяет артефакты",
         "рассказ не заменяет артефактов"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    per_ticket = _body_mutated(
        text, "Новый исполнитель на каждый тикет не спавнится",
        "Спавни нового исполнителя на каждый тикет")
    errors = _contract_errors(per_ticket)
    assert any("спавни нового исполнителя на каждый тикет" in error
               for error in errors)


def test_executor_selection_rule():
    """spec: docs/plans/team-profiles.md#готово — «Готово» 3 и 5 (тикет 03):
    сигнал стека — указатель архитектора в спеке/continue.md; оркестратор
    читает указатель, берёт id из реестра, иначе дефолт executor; два
    кандидата (универсальный executor и стековый 1c-executor) выбираются
    указателем; неоднозначность — остановка с вопросом; пресет и маршрут
    выбираются при спавне продолжаемой сессии и при пенсии/handoff, не на
    каждый тикет; маршрут — per-call через read реестра в полной форме
    provider/model плюс level, agentOptions — страховка; выбор называется
    в отчёте. Мутации: потеря указателя, гранулярности, дефолта, остановки,
    отчёта, полной формы маршрута, заморозки allowlist и литерала scout
    краснят контракт."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    selection = _section(_normalized_lower(_parse(text)[1]), SELECTION_HEADING)
    assert selection, "the selection section is missing"
    for phrase in SELECTION_PHRASES:
        assert phrase in selection, f"the phrase {phrase!r} left «Выбор исполнителя»"

    for old, new, needle in (
        ("Указатель архитектора", "Указатель оркестратора",
         "указатель архитектора"),
        ("при спавне сессии-исполнителя и при пенсии/handoff",
         "на каждый тикет", "при спавне сессии-исполнителя"),
        ("не на каждый тикет", "на каждый тикет", "не на каждый тикет"),
        ("указателя нет — дефолт `executor`",
         "указателя нет — дефолт `1c-executor`", "дефолт `executor`"),
        ("неоднозначность: остановка с вопросом",
         "неоднозначность решается выбором",
         "неоднозначность: остановка с вопросом"),
        ("тихий выбор не делается", "выбор делается молча",
         "тихий выбор не делается"),
        ("кандидаты — универсальный `executor` и стековый `1c-executor`",
         "кандидаты — один `executor`", "1c-executor"),
        ("Выбор называется в отчёте: кандидаты, выбранный id и причина",
         "Выбор называется в отчёте одним id",
         "выбор называется в отчёте: кандидаты"),
        ("`provider/model` плюс level", "одна model", "`provider/model` плюс level"),
        ("`read` реестра", "пересказ реестра", "`read` реестра"),
        ("allowlist заморожен при apply", "allowlist читается при вызове",
         "allowlist заморожен при apply"),
        ("`agentOptions` строки spawn — страховка, не источник маршрута",
         "дефолт в профиле — страховка, не источник маршрута", "`agentoptions`"),
        ("Реестр панели ревьюеров остаётся в `.agents/config.toml`",
         "Реестр панели переезжает в скилл", "`.agents/config.toml`"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    no_pointer = _body_mutated(text, "Указатель архитектора", "")
    errors = _contract_errors(no_pointer)
    assert any("указатель архитектора" in error for error in errors)

    no_ambiguity = _body_mutated(
        text, "неоднозначность: остановка с вопросом", "")
    errors = _contract_errors(no_ambiguity)
    assert any("неоднозначность: остановка с вопросом" in error for error in errors)


def test_green_contour_and_auto_acceptance():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 10
    в цепочке: оркестратор проверяет зелёные гейты по артефактам и фиксирует
    автоприёмку; P3 — реестр зацепок, незакрытое или остановка — вопрос."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for old, new, needle in (
        ("проверяет зелёные гейты по артефактам тикета",
         "верит отчёту исполнителя", "проверяет зелёные гейты по артефактам"),
        ("критерии приёмки закрыты доказательствами",
         "критерии приёмки названы", "критерии приёмки закрыты доказательствами"),
        ("панель после одного прохода правок без незакрытых P1/P2",
         "панель без находок", "панель после одного прохода правок без незакрытых p1/p2"),
        ("проверки dev/prod пройдены", "проверки пропущены",
         "проверки dev/prod пройдены"),
        ("механические гейты пака зелёные", "гейты пака не проверяются",
         "механические гейты пака зелёные"),
        ("точки остановки спеки пройдены", "точки остановки не смотрятся",
         "точки остановки спеки пройдены"),
        ("фиксирует автоприёмку записью в тикете трекера",
         "принимает тикет словом", "фиксирует автоприёмку записью в тикете трекера"),
        ("P3 уходят в реестр зацепок юнита", "P3 блокируют приёмку",
         "p3 уходят в реестр зацепок юнита"),
        ("Незакрытое или остановка — вопрос оператору",
         "Незакрытое закрывается на ходу",
         "незакрытое или остановка — вопрос оператору"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))


def test_budget_guards_and_retirement():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 7: страж
    бюджета оркестратора и исполнителя (оценка объёма, консервативный
    порог, счётчик токенов недоступен — названный пробел); пенсия
    исполнителя с handoff-промптом на границе тикета; компакта нет."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for old, new, needle in (
        ("Счётчик токенов агенту недоступен", "Счётчик токенов читается",
         "счётчик токенов агенту недоступен"),
        ("по оценке объёма и консервативному порогу",
         "по точному счётчику токенов", "по оценке объёма и консервативному порогу"),
        ("на границе тикета, не внутри прохода", "внутри прохода",
         "на границе тикета, не внутри прохода"),
        ("Пенсия исполнителя: на границе тикета",
         "Замена исполнителя: на границе тикета", "пенсия исполнителя"),
        ("с handoff-промптом", "без handoff", "handoff-промптом"),
        ("Handoff-промпт — вход новой сессии", "Новая сессия начинает с нуля",
         "handoff-промпт — вход новой сессии"),
        ("компакта нет", "компакт разрешён", "компакта нет"),
        ("Страж оркестратора", "Бюджет оркестратора не сторожится",
         "страж оркестратора"),
        ("замена оркестратора — новая чистая сессия по команде оператора",
         "оркестратор продолжает сам",
         "замена оркестратора — новая чистая сессия по команде оператора"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    compacted = _body_mutated(text, "компакта нет", "компактируй контекст")
    errors = _contract_errors(compacted)
    assert any("компактируй" in error for error in errors)
    assert any("компакта нет" in error for error in errors)


def test_stop_transfers_state_to_continue():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 7: остановка
    цепочки с передачей состояния в continue.md; исключение останавливает
    цепочку вопросом, возобновление — в чистой сессии."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for old, new, needle in (
        ("останавливает цепочку", "продолжает цепочку", "останавливает цепочку"),
        ("«Открытая работа»", "«Состояние»", "«открытая работа»"),
        ("юнит, тикет, на чём остановились, что дальше",
         "только номер тикета", "юнит, тикет, на чём остановились, что дальше"),
        ("Возобновление — по команде оператора в чистой сессии",
         "Возобновление автоматическое",
         "возобновление — по команде оператора в чистой сессии"),
        ("Тихое продолжение после исключения не делается",
         "После исключения продолжай тихо",
         "тихое продолжение после исключения не делается"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))


def test_final_report_form_and_acceptance():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 14,
    «Готово» 11: отчёт фактами (пункты «Готово» с доказательствами,
    демо-пути, пробелы, реестр зацепок) + mermaid-диаграммы ключевых решений
    и юз-кейсов + защита решения в сессии планирования; durable-копия
    в папке тикетов юнита; приёмка — ask «принять/вернуть», возврат
    открывает работу по находкам."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for old, new, needle in (
        ("mermaid-диаграммы ключевых решений и юз-кейсов",
         "диаграммы по желанию", "mermaid-диаграммы ключевых решений и юз-кейсов"),
        ("Durable-копия отчёта лежит в папке юнита трекера",
         "Отчёт живёт только в чате", "durable-копия отчёта"),
        ("пункты «Готово» спеки с доказательствами",
         "пункты «Готово» спеки списком", "пункты «готово» спеки с доказательствами"),
        ("демо-пути тикетов и их прогоны", "демо-пути не показываются",
         "демо-пути тикетов и их прогоны"),
        ("Презентацию, защиту решения и ask несёт агент сессии планирования",
         "Презентацию несёт оркестратор",
         "презентацию, защиту решения и ask несёт агент сессии планирования"),
        ("оркестратор фиксирует её и завершает цепочку",
         "оркестратор продолжает цепочку",
         "оркестратор фиксирует её и завершает цепочку"),
        ("Приёмка — ask «принять/вернуть»", "Приёмка словом без отчёта",
         "приёмка — ask «принять/вернуть»"),
        ("Возврат открывает работу по находкам", "Возврат закрывает юнит",
         "возврат открывает работу по находкам"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    word_only = _body_mutated(text, "Приёмка — ask «принять/вернуть»",
                              "Приёмка словом без отчёта")
    errors = _contract_errors(word_only)
    assert any("приёмка словом без отчёта" in error for error in errors)


def test_viz_derived_views_from_one_dag():
    """spec: docs/plans/standards-autoship.md#решения план-гейта — решение 19:
    один ticket-DAG (markdown+git) — источник истины; оркестратор
    вычисляет два производных статических вида — граф (mermaid-блок)
    и Kanban (markdown-таблица), файлы в папке юнита трекера; blocked
    вычисляется из рёбер, ready-frontier читается колонкой ready
    (отдельный третий блок не рендерится), цвета Temporal, без кода
    хоста; живая панель DSH — внешний плагин, оркестратор роутится на
    его инструмент один раз (приписка 2026-11-12), доска только
    в сессии оркестратора."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    for old, new, needle in (
        ("не ведёт их отдельно", "ведёт их отдельно", "не ведёт их отдельно"),
        ("два производных вида", "три производных вида",
         "два производных вида"),
        ("граф зависимостей — mermaid-блок",
         "граф зависимостей — произвольный формат",
         "граф зависимостей — mermaid-блок"),
        ("Kanban — markdown-таблица", "Kanban — произвольный формат",
         "kanban — markdown-таблица"),
        ("отдельный третий блок не рендерится",
         "третий блок рендерится отдельно",
         "отдельный третий блок не рендерится"),
        ("Колонку blocked оркестратор вычисляет",
         "Колонку blocked оркестратор проставляет",
         "колонку blocked оркестратор вычисляет"),
        ("не проставляет руками", "проставляет руками",
         "не проставляет руками"),
        ("цвета статусов — лексика Temporal", "цвета статусов произвольные",
         "цвета статусов — лексика temporal"),
        ("без кода хоста", "кодом хоста", "без кода хоста"),
        ("один раз вызывает инструмент", "вызывает инструмент на каждом тикете",
         "один раз вызывает инструмент"),
        ("доска открывается в сессии оркестратора",
         "доска открывается в любой сессии",
         "доска открывается в сессии оркестратора"),
        ("исполнитель и сессия планирования инструмент не вызывают",
         "исполнитель тоже вызывает инструмент",
         "исполнитель и сессия планирования инструмент не вызывают"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))


def test_contract_check_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check rejects a restored invocation flag, a lost command, a
    file:line anchor, a missing name, parallel tickets and a harness root."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    restored_flag = text.replace("---\n", "---\ndisable-model-invocation: true\n", 1)
    assert restored_flag != text
    assert any("disable-model-invocation" in error
               for error in _contract_errors(restored_flag))

    anchored = text.replace("## Исполнитель",
                            "## Исполнитель\n\nСмотри `skills/chain/SKILL.md:42`.", 1)
    assert anchored != text
    assert any("SKILL.md:42" in error for error in _contract_errors(anchored))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert missing_name != text
    assert any("name" in error for error in _contract_errors(missing_name))

    parallel = _body_mutated(text, "тикеты идут последовательно",
                             "тикеты идут параллельно")
    errors = _contract_errors(parallel)
    assert any("тикеты идут параллельно" in error for error in errors)

    rooted = text.replace("## Честность", "## Честность\n\nКорень `.zcode/skills`.", 1)
    assert rooted != text
    assert any(".zcode" in error for error in _contract_errors(rooted))


@pytest.mark.parametrize("root", (".dsh", ".zcode", ".qoder"))
def test_skill_names_no_harness_root(root: str):
    """invariant: docs/plans/harness-agnostic.md#готово — текст скилла не
    называет корни харнессов."""
    assert root not in SKILL.read_text("utf-8")
