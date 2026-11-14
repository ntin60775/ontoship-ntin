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
spec: docs/plans/team-profiles.md#готово — «Готово» 6, 9 (тикет 04):
контекстный промпт юнита в промпте спавна; проверка `methodContract`
(версия 1) через сервис плагина бандла с остановкой при mismatch или
отсутствии; записи цепочки пишет исполнитель по диктовке read-only
оркестратора, композиция пресетов не меняется; решение оператора
ask 2026-11-13.
spec: docs/plans/team-profiles.md#готово — «Готово» 10 (тикет 10,
решение 19): опрос исполнителя по таймеру — норма chain: таймер при
старте/возобновлении цепочки (каждые 5 минут, доставка в сессию
оркестратора), по тику — статус-запрос, сверка артефактов, todo и
корректировка; ответ исполнителя одной строкой; пауза при
остановке/финале; оператору — только отклонения и остановки.
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
    "проверь метод-контракт (раздел «метод-контракт»)",
    "остановка с вопросом оператору до чтения тикетов",
    "бандла в профиле нет — проверки нет",
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
    "передаёт тикеты по одному через `send_message`",
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
    "полный зелёный контур даёт автоприёмку",
    "p3 уходят в реестр зацепок юнита",
    "незакрытое или остановка — вопрос оператору",
    "автоприёмка не делается, цепочка стоит",
    # the context prompt of the unit: the spawn prompt points at files and
    # carries the chosen preset/route and the contract version.
    "промпт спавна — контекстный промпт юнита",
    "адрес юнита (спека",
    "выбранные пресет и маршрут",
    "версия метод-контракта",
    "пересказ спеки в промпт не кладётся",
    # the dictation norm: the orchestrator composition is read-only; chain
    # records are written by the executor by dictation and verified back.
    "композиция оркестратора — read-only",
    "записи цепочки",
    "пишет исполнитель по диктовке",
    "оркестратор проверяет гейты по артефактам, формирует текст записи",
    "передаёт его `send_message`",
    "исполнитель пишет и коммитит, оркестратор читает и сверяет",
    "композиция пресетов при этом не меняется",
    "гибель исполнителя",
    "стоп-состояние передаётся через оператора или сессию планирования",
    # the polling norm: the executor answers a status request in one line.
    "статус-запрос оркестратора не остаётся без ответа",
    "отвечает одной строкой",
    "текущий шаг ship, что делает, блокировки",
)
# «Опрос исполнителя по таймеру» (тикет 10 team-profiles, решение 19):
# the timer is a chain norm, not one session's practice — created at chain
# start and at resume (schedule_create, every 5 minutes, delivery into the
# orchestrator session; a resumed session creates it anew); each tick is a
# one-line status request, artifact verification without waiting for the
# answer, todo update and a correction message on deviation; an exception
# stops the chain by the stop norms; at stop/final the timer is paused
# (schedule_edit active false); the operator sees only deviations and stops.
TIMER_PHRASES = (
    "оркестратор заводит таймер опроса при старте цепочки",
    "при возобновлении",
    "`schedule_create`",
    "доставка в сессию оркестратора",
    "каждые 5 минут",
    "при возобновлении в новой сессии таймер создаётся заново",
    "по каждому тику",
    "статус-запрос `send_message`",
    "одна строка",
    "сверяет артефакты, не дожидаясь ответа",
    "`git log` и `git status`",
    "worktree тикета и основного checkout",
    "прогресс-файл тикета",
    "состав панели",
    "обновляет свой `todo`",
    "корректирует исполнителя",
    "оператору — только отклонения и остановки",
    "останавливает цепочку по нормам раздела",
    "при остановке и при финале цепочки оркестратор приостанавливает таймер",
    "`schedule_edit` с `active: false`",
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
    "диктует её исполнителю",
    "пишет исполнитель, оркестратор читает и сверяет",
    "исполнителя нет — запись идёт через оператора или сессию планирования",
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
    "оркестратор фиксирует её записью исполнителя по диктовке",
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
    # report, the retired critic gate, the orchestrator writing chain records
    # itself (operator decision ask 2026-11-13: read-only composition, records
    # are dictated to the executor).
    "disable-model-invocation",
    "фиксирует автоприёмку записью в тикете трекера",
    "оркестратор пишет записи",
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
    "кандидаты — универсальный `executor` и стековый id (например, `1c-executor`)",
    "дефолт `executor`",
    "неоднозначность: остановка с вопросом",
    "тихий выбор не делается",
    "при спавне сессии-исполнителя и при пенсии/handoff",
    "не на каждый тикет",
    "per-call",
    "`read` реестра",
    "`provider/model` плюс level",
    "уходят в вызов",
    "для любого выбранного пресета, не только дефолтного",
    "`agentoptions`",
    "страховка, не источник маршрута",
    "выбор называется в отчёте: кандидаты, выбранный id и причина",
    "приоритет источников маршрута",
    "явный проектный факт в `continue.md` главнее записи реестра",
    "дефолт хоста (наследование от оркестратора)",
    "`.agents/config.toml`",
)
# «Метод-контракт» (тикет 04 team-profiles, решения 9 и оператора
# ask 2026-11-13): the contract carrier is the team bundle manifest; the
# expected version is the method release (a literal in this skill); the check
# runs through the plugin service (read-only inspect provider) and stops the
# chain with a question on mismatch or absence; the version bumps with the
# method release that changes the carrying norms.
CONTRACT_PHRASES = (
    "эталон — релиз метода",
    "`ontoship.methodcontract`",
    "(версия 1)",
    "ожидаемую версию носит этот скилл",
    "через сервис плагина бандла",
    "`cordis_inspect_list`",
    "провайдер `ontoshipteam`",
    "метод `methodcontract`",
    "`cordis_inspect_query`",
    "без входных параметров",
    "`contract` (версия бандла; 0 — контракта нет)",
    "`absent`",
    "равен ожиданию версии 1 и `absent: false`",
    "контракт совпал: цепочка продолжает",
    "не равен 1 или `absent: true`",
    "остановка с вопросом",
    "тихий выбор и «договоримся по ходу» не делаются",
    "провайдера нет",
    "провайдер `config`",
    "метод `listconfigs`",
    "`{\"entry\": \"ontoship-contract\"}`",
    "бандл в профиле старый",
    "unknown entry id",
    "проверки нет",
    "проект без team-бандла",
    "поднимается вместе с релизом метода",
    "bump манифеста бандла и ожидания скилла",
)
WHEN_HEADING = "когда использовать"
ENTRY_HEADING = "вход и порядок рёбер"
CONTRACT_HEADING = "метод-контракт"
EXECUTOR_HEADING = "исполнитель"
SELECTION_HEADING = "выбор исполнителя"
BUDGET_HEADING = "стражи бюджета"
STOP_HEADING = "остановка цепочки"
REPORT_HEADING = "финальный отчёт и приёмка"
VIZ_HEADING = "визуализация: один dag — производные виды"
TIMER_HEADING = "опрос исполнителя по таймеру"


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
        (CONTRACT_HEADING, "contract", CONTRACT_PHRASES),
        (EXECUTOR_HEADING, "executor", EXECUTOR_PHRASES),
        (SELECTION_HEADING, "selection", SELECTION_PHRASES),
        (BUDGET_HEADING, "budget", BUDGET_PHRASES),
        (STOP_HEADING, "stop", STOP_PHRASES),
        (REPORT_HEADING, "report", REPORT_PHRASES),
        (VIZ_HEADING, "viz", VIZ_PHRASES),
        (TIMER_HEADING, "timer", TIMER_PHRASES),
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
        ("Проверь метод-контракт (раздел «Метод-контракт»)",
         "Проверь нарезку", "проверь метод-контракт"),
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
        ("передаёт тикеты по одному через `send_message`",
         "передаёт тикеты новым спавном",
         "передаёт тикеты по одному через `send_message`"),
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
    provider/model плюс level для любого выбранного пресета, agentOptions —
    страховка; приоритет проектного факта над реестром и фолбэк на дефолт
    хоста названы; выбор называется в отчёте. Мутации: потеря указателя,
    гранулярности, дефолта, остановки, отчёта, полной формы маршрута,
    заморозки allowlist, приоритета источников и панельного реестра
    краснят контракт; литерал scout в allowlist сторожит team-тест
    composition.spec.ts."""
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
        ("кандидаты — универсальный `executor` и стековый id (например, `1c-executor`)",
         "кандидаты — один `executor`", "1c-executor"),
        ("Выбор называется в отчёте: кандидаты, выбранный id и причина",
         "Выбор называется в отчёте одним id",
         "выбор называется в отчёте: кандидаты"),
        ("`provider/model` плюс level", "одна model", "`provider/model` плюс level"),
        ("для любого выбранного пресета, не только дефолтного",
         "только для дефолтного пресета",
         "для любого выбранного пресета, не только дефолтного"),
        ("явный проектный факт в `continue.md` главнее записи реестра",
         "реестр главнее проектного факта",
         "явный проектный факт в `continue.md` главнее записи реестра"),
        ("дефолт хоста (наследование от оркестратора)",
         "дефолт хоста без наследования",
         "дефолт хоста (наследование от оркестратора)"),
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


def test_method_contract_check():
    """spec: docs/plans/team-profiles.md#готово — «Готово» 6, 9 (тикет 04):
    `methodContract` (версия 1) в манифесте team-бандла, эталон — релиз
    метода; `chain` проверяет контракт через сервис плагина бандла
    (`cordis_inspect_query`, провайдер `OntoShipTeam`, метод
    `methodContract`) и останавливается с вопросом при mismatch или
    отсутствии; версия поднимается вместе с релизом метода. Мутации:
    потеря ожидания, ветки совпадения, стопа, ветки «провайдера нет»,
    правила bump и самой секции краснят контракт."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    section = _section(_normalized_lower(_parse(text)[1]), CONTRACT_HEADING)
    assert section, "the contract section is missing"
    for phrase in CONTRACT_PHRASES:
        assert phrase in section, f"the phrase {phrase!r} left «Метод-контракт»"

    for old, new, needle in (
        ("`ontoship.methodContract` (версия 1)",
         "`ontoship.methodContract` (любая версия)", "(версия 1)"),
        ("эталон — релиз метода", "эталон — скилл chain", "эталон — релиз метода"),
        ("ожидаемую версию носит этот скилл",
         "ожидаемую версию носит whoever", "ожидаемую версию носит этот скилл"),
        ("через сервис плагина бандла", "через файл проекта",
         "через сервис плагина бандла"),
        ("без входных параметров", "с ожиданием",
         "без входных параметров"),
        ("`contract` равен ожиданию версии 1 и `absent: false`",
         "`contract` не проверяется",
         "равен ожиданию версии 1"),
        ("не равен 1 или `absent: true`", "любое значение подходит",
         "не равен 1 или `absent: true`"),
        ("тихий выбор и «договоримся по ходу» не делаются",
         "выбор по ходу допустим", "тихий выбор"),
        ("провайдера нет", "провайдер есть", "провайдера нет"),
        ("бандл в профиле старый", "бандл в профиле свежий",
         "бандл в профиле старый"),
        ("unknown entry id", "entry есть", "unknown entry id"),
        ("поднимается вместе с релизом метода",
         "поднимается отдельно от релиза", "поднимается вместе с релизом метода"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    missing_section = _body_mutated(text, "## Метод-контракт", "## Служебное")
    assert any("метод-контракт" in error
               for error in _contract_errors(missing_section))


def test_chain_records_are_dictated():
    """spec: docs/plans/team-profiles.md#готово — «Готово» 6 (тикет 04),
    решение оператора ask 2026-11-13: композиция orchestrator read-only;
    записи цепочки (автоприёмка в тикете, continue.md, производные виды,
    durable-копия отчёта) пишет исполнитель по диктовке оркестратора —
    оркестратор проверяет гейты, формирует текст, передаёт `send_message`,
    исполнитель пишет и коммитит, оркестратор сверяет; композиция пресетов
    не меняется, гибель исполнителя — стоп через оператора/сессию
    планирования. Мутации краснят: потеря read-only, диктовки, сверки и
    возврат снятой нормы «оркестратор фиксирует автоприёмку»."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    lowered = _normalized_lower(_parse(text)[1])
    executor = _section(lowered, EXECUTOR_HEADING)
    assert "композиция оркестратора — read-only" in executor
    assert "пишет исполнитель по диктовке" in executor
    assert "исполнитель пишет и коммитит, оркестратор читает и сверяет" in executor
    assert "композиция пресетов при этом не меняется" in executor
    assert "стоп-состояние передаётся через оператора или сессию планирования" in executor
    stop = _section(lowered, STOP_HEADING)
    assert "диктует её исполнителю" in stop

    for old, new, needle in (
        ("Композиция оркестратора — read-only",
         "Композиция оркестратора — с правкой файлов",
         "композиция оркестратора — read-only"),
        ("оркестратор читает и сверяет", "оркестратор не сверяет",
         "оркестратор читает и сверяет"),
        ("Композиция пресетов при этом не меняется",
         "Композиция пресетов при этом меняется",
         "композиция пресетов при этом не меняется"),
        ("Гибель исполнителя — записи больше не диктуются",
         "Сбой исполнителя — записи не диктуются", "гибель исполнителя"),
        ("диктует её исполнителю", "передаёт её молча", "диктует её исполнителю"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    dictated = _body_mutated(text, "пишет исполнитель по диктовке",
                             "пишет оркестратор сам", count=2)
    assert any("пишет исполнитель по диктовке" in error
               for error in _contract_errors(dictated)), _contract_errors(dictated)

    restored = text + "\n\nОркестратор фиксирует автоприёмку записью в тикете трекера.\n"
    errors = _contract_errors(restored)
    assert any("фиксирует автоприёмку записью в тикете трекера" in error
               for error in errors), errors


def test_context_prompt_of_unit():
    """spec: docs/plans/team-profiles.md#готово — «Готово» 6 (тикет 04):
    контекстный промпт юнита в промпте спавна исполнителя: адрес юнита
    (спека, тикеты), состояние continue.md, выбранные пресет и маршрут,
    версия метод-контракта и норма отчёта; пересказ спеки не дублируется.
    Мутации: потеря адреса, состояния, выбранных пресета/маршрута, версии
    контракта и запрета пересказа краснят контракт."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    executor = _section(_normalized_lower(_parse(text)[1]), EXECUTOR_HEADING)
    assert "промпт спавна — контекстный промпт юнита" in executor
    for phrase in ("адрес юнита (спека", "тикеты `tickets/<slug>/`",
                   "состояние\n`docs/ops/continue.md`".replace("\n", " "),
                   "выбранные пресет и маршрут", "версия метод-контракта",
                   "норма отчёта", "пересказ спеки в промпт не кладётся"):
        assert phrase in executor, f"the phrase {phrase!r} left «Исполнитель»"

    for old, new, needle in (
        ("Промпт спавна — контекстный промпт юнита",
         "Промпт спавна — короткая команда", "промпт спавна — контекстный промпт юнита"),
        ("выбранные пресет и маршрут", "маршрут уточняется позже",
         "выбранные пресет и маршрут"),
        ("версия метод-контракта", "версия не нужна", "версия метод-контракта"),
        ("Пересказ спеки в промпт не кладётся",
         "Пересказ спеки в промпт кладётся", "пересказ спеки в промпт не кладётся"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))


def test_polling_timer_norm():
    """spec: docs/plans/team-profiles.md#готово — «Готово» 10 (тикет 10,
    решение 19): опрос исполнителя по таймеру — норма chain, а не практика
    одной сессии: оркестратор заводит таймер при старте/возобновлении
    цепочки (`schedule_create`, каждые 5 минут, доставка в сессию
    оркестратора); при возобновлении в новой сессии таймер создаётся
    заново; по каждому тику — статус-запрос одной строкой, сверка
    артефактов без ожидания ответа (git log/status worktree и основного
    checkout, прогресс-файл, состав панели), обновление своего todo и
    корректировка при отклонении; исключение или точка остановки —
    остановка по нормам chain; при остановке/финале таймер
    приостанавливается; оператору — только отклонения и остановки.
    Мутации: потеря старта/возобновления, интервала, доставки, состава
    тика и паузы краснят контракт."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    lowered = _normalized_lower(_parse(text)[1])
    timer = _section(lowered, TIMER_HEADING)
    assert timer, "the polling-timer section is missing"
    for phrase in TIMER_PHRASES:
        assert phrase in timer, \
            f"the phrase {phrase!r} left «Опрос исполнителя по таймеру»"

    for old, new, needle in (
        ("Оркестратор заводит таймер опроса при старте цепочки",
         "Оркестратор не заводит таймер опроса при старте цепочки",
         "заводит таймер опроса при старте цепочки"),
        ("при возобновлении в новой сессии таймер создаётся заново",
         "при возобновлении в новой сессии таймер наследуется",
         "таймер создаётся заново"),
        ("каждые 5 минут", "каждые 30 минут", "каждые 5 минут"),
        ("доставка в сессию оркестратора", "доставка в сессию исполнителя",
         "доставка в сессию оркестратора"),
        ("шлёт исполнителю статус-запрос `send_message`",
         "шлёт исполнителю статус-запрос голосом",
         "статус-запрос `send_message`"),
        ("сверяет артефакты, не дожидаясь ответа",
         "сверяет артефакты после ответа", "сверяет артефакты"),
        ("обновляет свой `todo`", "свой `todo` не обновляет",
         "обновляет свой `todo`"),
        ("корректирует исполнителя", "корректировку откладывает",
         "корректирует исполнителя"),
        ("оператору — только отклонения и остановки",
         "оператору — каждый тик",
         "оператору — только отклонения и остановки"),
        ("при остановке и при финале цепочки оркестратор "
         "приостанавливает таймер",
         "при остановке и при финале цепочки таймер продолжает идти",
         "при остановке и при финале цепочки оркестратор"),
        ("`schedule_edit` с `active: false`", "`schedule_edit` с `active: true`",
         "`schedule_edit` с `active: false`"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    no_interval = _body_mutated(text, "каждые 5 минут", "")
    assert any("каждые 5 минут" in error
               for error in _contract_errors(no_interval))

    no_pause = _body_mutated(text, "оркестратор приостанавливает таймер", "")
    assert any("при остановке и при финале цепочки" in error
               for error in _contract_errors(no_pause))

    missing_section = _body_mutated(
        text, "## Опрос исполнителя по таймеру", "## Служебное")
    assert any("опрос исполнителя по таймеру" in error
               for error in _contract_errors(missing_section))


def test_executor_answers_status_request():
    """spec: docs/plans/team-profiles.md#готово — «Готово» 10 (тикет 10,
    решение 19): исполнитель отвечает на статус-запрос оркестратора одной
    строкой — текущий шаг ship, что делает, блокировки; статус-запрос не
    остаётся без ответа. Мутации: рассказ вместо строки, пропущенный ответ
    и потеря состава строки краснят контракт."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []
    executor = _section(_normalized_lower(_parse(text)[1]), EXECUTOR_HEADING)
    assert "статус-запрос оркестратора не остаётся без ответа" in executor
    assert "отвечает одной строкой" in executor
    assert "текущий шаг ship, что делает, блокировки" in executor

    for old, new, needle in (
        ("Статус-запрос оркестратора не остаётся без ответа",
         "Статус-запрос оркестратора можно пропустить",
         "статус-запрос оркестратора не остаётся без ответа"),
        ("отвечает одной строкой", "отвечает подробным рассказом",
         "отвечает одной строкой"),
        ("текущий шаг ship, что делает, блокировки",
         "текущий шаг ship и всё",
         "текущий шаг ship, что делает, блокировки"),
    ):
        mutated = _body_mutated(text, old, new)
        assert any(needle in error for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))

    no_answer = _body_mutated(text, "отвечает одной строкой", "")
    errors = _contract_errors(no_answer)
    assert any("отвечает одной строкой" in error for error in errors)


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
        ("Композиция оркестратора — read-only",
         "Композиция оркестратора — с правкой файлов",
         "композиция оркестратора — read-only"),
        ("Композиция пресетов при этом не меняется",
         "Композиция пресетов при этом меняется",
         "композиция пресетов при этом не меняется"),
        ("оркестратор читает и сверяет", "оркестратор не сверяет",
         "оркестратор читает и сверяет"),
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
        ("оркестратор фиксирует её записью исполнителя по диктовке",
         "оркестратор фиксирует её сам",
         "оркестратор фиксирует её записью исполнителя"),
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
