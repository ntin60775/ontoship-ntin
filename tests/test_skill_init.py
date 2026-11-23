"""Contract for the init skill and the managed block it writes.

The skill is prose: its "code" is the text an agent follows. These checks pin
the shipped artifact — the DSH frontmatter, the four files init owns
(AGENTS.md, .gitignore, the role registry .agents/config.toml and the
docs/ops/continue.md skeleton), the marker cases, the verbatim DSH block, the
continue skeleton and the bootstrap contract — and prove the check can fail
(mutation probe). ZCode rails and the marketplace channel left the project by
a direct operator decision; the skill names no ZCode root and no generator.

spec: docs/plans/harness-agnostic.md#готово — skills/init/SKILL.md, the managed
      block, .gitignore (five lines), the project-local skill root
spec: docs/plans/entry-and-continuity.md#готово — init создаёт скелет
      docs/ops/continue.md при отсутствии: пять разделов дословно;
      существующий файл не перезаписывается, отчёт называет created или
      unchanged; контракт владения — четыре файла
spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3: чек-лист
      скелета несёт четыре перехода текущего потока (проекционная
      валидация до нарезки — standards-autoship решение 17, самопроверка
      после приёмки нарезки вместо передачи в цепочку — решение 3);
      трёхпереходный список entry-and-continuity вытеснен, якорь чек-листа
      перетыкнут сюда
spec: docs/plans/review-config.md#готово — реестр ролей .agents/config.toml,
      названный пробел без источника моделей, совпадение модели критика —
      рекомендация в отчёте
spec: docs/plans/dsh-adaptation.md#готово — стандартная раскладка шести ролей,
      запись без ask при живых маршрутах (ZCode-ветка выведена решением
      оператора; хроника — continue.md)
spec: docs/plans/standards-autoship.md#готово — «Готово» 9 (тикет 05): init
      пишет стандартную раскладку с пулом flash, независимость по умолчанию —
      норма реестра, секция пула в существующем конфиге — названный пропуск
spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3, решение 3:
      блок init несёт команды ядра, словарь ведения (цепочка, орк-промт)
      снят и под запретом; скелет continue.md несёт чек-лист текущего
      потока без передачи в цепочку; паритет блока сохранён (шаблон
      скилла, этот литерал, AGENTS.md)
spec: docs/plans/deliver.md#готово — «Готово» 2: строка «Команды» блока
      несёт команду поставки/обновления со ссылкой на скилл deliver;
      пины блока и ENTRY_RULES обновлены тем же срезом
invariant: docs/plans/workflow-skills.md#ограничения — no registry, provenance,
      Reel or acceptance chord
invariant: docs/plans/harness-agnostic.md#готово — no harness root named
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "init" / "SKILL.md"
BEGIN = "<!-- BEGIN ontoship -->"
END = "<!-- END ontoship -->"
# One rail (DSH): the five-line .gitignore set with the literal skill root
# and the pack root (operator decision 2026-11-11, ticket 02 hook).
GITIGNORE = (".gitmark/", "*-map.html", ".scratch/", ".agents/skills/",
             ".agents/packs/")
CORE_ROLES = ("reviewer-spec", "reviewer-tests", "reviewer-code", "reviewer-kb", "critic",
              "curator")
# The ownership contract (entry-and-continuity «Готово» 2): the four files,
# the count phrase and the docs/ prohibition narrowed to the skeleton
# exclusion. Single source: the needles, the list check and the mutations
# all read these constants (panel dwfrun-dee2378e).
OWNED_FILES = ("AGENTS.md", ".gitignore", ".agents/config.toml",
               "docs/ops/continue.md")
OWNERSHIP_COUNT = "Четыре файла, ничего больше"
# norm-fixes/01 (проба deliver/03, инцидент 6): новые файлы кончаются
# переводом строки по шаблону; правило сохранения байтов — только для
# существующих. Клауза запинена и мутации краснят.
NEW_FILE_NEWLINE_RULE = (
    "Новые файлы — байт-в-байт по шаблону, включая завершающий перевод строки",
    "относится только к существующим файлам",
)
# logika K10: the description and the ownership section must agree with case 2
# of the marker table — insertion puts one separator blank line before the
# block, outside the markers.
SEPARATOR_CLAUSE = "при вставке — одна пустая строка-разделитель перед блоком"
SEPARATOR_EXCEPTION = ("одна пустая строка-разделитель перед блоком "
                       "при его вставке")
DOCS_EXCLUSION = ("не пишет ничего в `docs/`, кроме скелета "
                  "`docs/ops/continue.md` при отсутствии файла")
BOOTSTRAP_NEEDLES = (
    OWNERSHIP_COUNT,
    ".agents/config.toml",
    "назови пробел и остановись",
    "Модель сессии",
    "рекомендуется отличной от модели сессии",
    "назови его в отчёте",
    "пропуск",
    "не дописывай",
    "не трогай",
    "Сверь роли ядра",
    "`critic`, `curator` — с секциями конфига",
) + CORE_ROLES

# One rail: the harness is DSH, picked by the host tool the session carries,
# not by a path. A session without the tools stops with a named gap — there
# is no second branch to fall back to.
HARNESS_NEEDLES = (
    "Харнесс — DSH",
    "определяется доступным инструментом хоста",
    "`list_subagent_models`",
    "`subagent`",
    "Нет — назови пробел и остановись",
    "на чужом харнессе он не работает",
)

# The bootstrap section carries the standard layout (operator decision
# 2026-11-16, critic model replaced by operator decision 2026-11-22,
# curator level dropped to `low` by operator decision 2026-11-23;
# supersedes dsh-adaptation decision 5): six routes and levels
# shipped one table, written without an ask when every route is live,
# deviation named in the report.
LAYOUT_NEEDLES = (
    "**Стандартная раскладка.**",
    "`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`",
    "`qwen-token-plan-max/qwen4-max`",
    "| `reviewer-spec`, `reviewer-tests`, `reviewer-code`, `reviewer-kb` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `max` |",
    "| `critic` | `qwen-token-plan-max/qwen4-max` | `xhigh` |",
    "| `curator` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `low` |",
    "запиши её без ask",
    "назови отклонение от стандарта",
    "спроси оператора",
    "runtime-контекст",
    "`<provider>/<model>`",
    "штатный дефолт модели",
)

# standards-autoship 05 («Готово» 9, decision 15): the registry carries the
# validation pool beside the role routes; init writes the standard flash pool
# with the layout, checks it against the live catalog by the same rule, and
# names the independence norm. The pool section is part of the registry: an
# existing config without it is a named gap, not a silent append.
POOL_NEEDLES = (
    "**Пул валидации.**",
    "`[validation]`",
    "`deepseek-account/deepseek-flash`",
    "с уровнем `max`",
    "Сверь маршруты и уровни пула с живым каталогом",
    "пиши без ask",
    "Независимость по умолчанию — норма реестра",
    "ревьюеры идут на модели, отличной от сессионной",
    "Секция пула валидации `[validation]`",
)

FORBIDDEN = ("registry", "provenance", "reel", "acceptance chord", "inventory",
             "serve", ".dsh", ".qoder", "commands.md",
             # the ZCode purge (operator decision): the skill names no ZCode
             # root, tool or generator, anywhere, in any case.
             "zcode", ".zcode", "ListModels", "gen_agents", "план-мод",
             "навыковый корень канала")
# review-loose-ends: the registry wording must stay neutral to role growth, so
# the two old wordings are forbidden anywhere in the skill, in any case.
# hooks: the counted bootstrap question is forbidden the same way.
FORBIDDEN_WORDINGS = ("реестр ролей ревью", "бутстрап ролей ревью", "шестой вопрос")

# hooks: a digit or a Russian numeral — nominative or the oblique case forms —
# right before «рол…» (optionally «ревью-рол…») is a stale role-count snapshot.
# The left lookbehind keeps a numeral hidden inside a word («внутри роли»,
# «смотри роли», «опять роль») from firing. Declared blind spots: a count
# after the noun («Ролей ядра — шесть») and ordinal numerals before the noun
# itself («шестая роль»); ordinals before «вопрос» carry their own guard below.
COUNTED_ROLE = re.compile(
    r"(?<![а-яёa-z\d])"
    r"(?:\d+"
    r"|один|одна|одно|одни|одной|одному"
    r"|дв[ае]|двух|двум|двумя"
    r"|три|тр[ие]|трём|трем|тр[её]х|тремя"
    r"|четыре|четыр[её]х|четырём|четырем|четырьмя"
    r"|пять|пяти|пятью"
    r"|шесть|шести|шестью"
    r"|семь|семи|семью"
    r"|восемь|восьми|восемью"
    r"|девять|девяти|девятью"
    r"|десять|десяти|десятью)"
    r"\s+(?:ревью-)?рол",
    re.IGNORECASE,
)

# A counted bootstrap question — an ordinal right before «вопрос» — is the
# same stale snapshot; the neutral skill wording is «Отдельный вопрос».
ORDINAL_QUESTION = re.compile(
    r"(?<![а-яёa-z\d])"
    r"(?:перв|втор|трет|четв[её]рт|пят|шест|седьм|восьм|девят|десят)[а-яё]*"
    r"\s+вопрос",
    re.IGNORECASE,
)

# The managed block, pinned independently of the skill text: the expected
# value is this literal, not a re-extraction. The root is literal:
# `.agents/skills` — the single installer channel; there is no placeholder
# to substitute.
BLOCK = """\
<!-- BEGIN ontoship -->
## База знаний (OntoShip)

- Точка входа: [`docs/README.md`](docs/README.md) — главный индекс KB; у каждой папки
  есть индекс `README.md`.
- Ищи до ответа или записи: загрузи скилл `kb-search`. Движок лежит в
  `.agents/skills/kb-search/gitmark.py`; корень — `.agents/skills`.
- Новые или обновлённые документы: загрузи скилл `kb-curate` — сначала поиск, никогда
  не дублируй.
- Сопровождение после правки документов:

  ```sh
  python3 .agents/skills/kb-search/gitmark.py index
  python3 .agents/skills/kb-search/gitmark.py lint --strict
  python3 .agents/skills/kb-search/gitmark.py map -o docs-map.html
  ```

- KB — это markdown + git: `.gitmark/`, `*-map.html` и `.scratch/` производные или
  эфемерные — никогда не коммитятся.

## Вход в работу (OntoShip)

- Изменения этого проекта идут через ship-флоу: скилл `ship` исполняет
  один тикет за запуск — вручную командой `/ship`; свободные правки
  в обход тикета не делаются — прямые решения оператора выше этого
  правила.
- Запрос плана открывает draft-спеку через скилл `grilling`; режим плана
  харнесса не используется.
- Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):
  сессия продолжается оттуда и берёт следующий тикет оттуда же.
- Команды: «стартуй юнит» — открыть draft-спеку; `ship` — командой
  `/ship` или «исполняй тикет N»; «деплой и обновление [имя_проекта]» —
  скилл `deliver`.
<!-- END ontoship -->
"""

# Rule clauses of the entry section (docs/plans/entry-and-continuity.md,
# «Готово» 1, 3; dsh-adaptation consequence 2; core-team-boundaries 03,
# «Готово» 3, decision 3; deliver 01, «Готово» 2): one anchor per clause,
# so a dropped clause reddens with its own name. The ship clause names
# the manual `/ship` channel; the command bullet names the core commands
# only — the chain launch and the entry-prompt regeneration left for the
# team bundle; the deliver clause names the delivery/update command.
ENTRY_RULES = (
    "свободные правки в обход тикета не",
    "Запрос плана открывает draft-спеку через скилл `grilling`",
    "харнесса не используется",
    "Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):",
    "скилл `ship` исполняет",
    "один тикет за запуск — вручную",
    "командой `/ship`",
    "`/ship` или «исполняй тикет N»",
    "«деплой и обновление [имя_проекта]» —",
    "скилл `deliver`",
)

# core-team-boundaries 03 («Готово» 3, decision 3): the retired chain
# vocabulary must not return into the managed block — the chain mechanism
# and the entry-prompt rule live in the team bundle, the block carries the
# core commands.
BLOCK_RETIRED = (
    "в автономной цепочке",
    "«цепочка»",
    "скилл `chain`",
    "«орк-промт»",
    "инициирующий промпт",
)

# The continue.md skeleton shipped by init: the five section headings and the
# create-if-absent contract come from entry-and-continuity «Готово» 2; the
# four-transition checklist of the current flow comes from core-team-boundaries
# «Готово» 3 (the old three-transition list is superseded). The frontmatter,
# the intro line and the section bodies are the template's own prose, pinned
# verbatim here independently of the skill text — the expected value is this
# literal, not a re-extraction.
CONTINUE_SKELETON = """\
---
node_type: runbook
title: Продолжение работы над проектом
service: _platform
status: active
updated: <дата>
---

# Продолжение работы над проектом

Это канонический старт каждой сессии. Источник истины — этот файл и тикеты,
не память сессии.

## Состояние

Где проект: закрытые юниты и тикеты, открытый юнит, последний merge.

## Открытая работа

Что исполняется: юнит, тикет, на чём остановились, что дальше.

## Порядок тикетов

Юниты и тикеты в порядке исполнения; блокировки отмечены.

## Что осталось

Отложенная работа: пункт с условием возврата.

## Стартовый промпт

Текст, с которого открывается сессия. Чек-лист фазовых переходов:
вычитка спеки перед план-гейтом — скилл `grilling`; проекционная
валидация после план-гейта, до нарезки — скилл `critic`; самопроверка
после приёмки нарезки — скилл `to-tickets`; ревью-панель перед merge —
скилл `ship`.
"""

CONTINUE_FENCE = re.compile(r"^```markdown\n(.*?)^```$", re.MULTILINE | re.DOTALL)
# Blind spots of the fence (panel dwfrun-dee2378e): the tag must be
# ```markdown at column zero and the fence must be the only one in the file.
# A ```md tag, an indent or a trailing space after the tag reads as "no
# fence"; a second ```markdown block anywhere in the skill (for example a
# skeleton example in the prose) reads as "two fences". _continue_skeleton
# names each case; the regex itself cannot tell them apart.

CONTINUE_SECTIONS = ("Состояние", "Открытая работа", "Порядок тикетов",
                     "Что осталось", "Стартовый промпт")

# Rule clauses of the continue step (entry-and-continuity «Готово» 2): the
# create-if-absent condition and action, the single substitution, both report
# words, the non-overwrite negation and the idempotency sentence. Checked on
# whitespace-flattened text, so an 80-column wrap cannot hide a clause.
CONTINUE_RULES = (
    "Файла нет — создай каталог `docs/ops` и запиши в него файл `continue.md`",
    "сегодняшняя дата в формате YYYY-MM-DD вместо `<дата>` в поле `updated`",
    "отчёт называет `created`",
    "Файл существует — не правь его ни байта",
    "отчёт называет `unchanged`",
    "последующие запуски init его не читают и не меняют",
)

# The phase-transition checklist carried by the skeleton's «Стартовый промпт»
# section: one anchor per transition. core-team-boundaries 03 («Готово» 3):
# the checklist names the current core flow — the projection gate stands
# before slicing, the self-check closes it; the retired «критик после
# нарезки» wording and the chain handoff stay out.
TRANSITION_CHECKLIST = (
    "вычитка спеки перед план-гейтом — скилл `grilling`",
    "проекционная валидация после план-гейта, до нарезки — скилл `critic`",
    "самопроверка после приёмки нарезки — скилл `to-tickets`",
    "ревью-панель перед merge — скилл `ship`",
)

BLOCK_FENCE = re.compile(
    r"^````[^\n]*\n(<!-- BEGIN ontoship -->\n.*?^<!-- END ontoship -->\n)^````$",
    re.MULTILINE | re.DOTALL,
)

GITIGNORE_FENCE = re.compile(
    r"^```text\n((?:\.gitmark/\n).*?)^```$",
    re.MULTILINE | re.DOTALL,
)


def _parse_skill(text: str) -> tuple[dict[str, str], str]:
    """Parse the single-line YAML frontmatter the skill uses."""
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


def _blocks(text: str) -> list[str]:
    """The four-backtick fenced ontoship blocks, in file order."""
    return BLOCK_FENCE.findall(text)


def _gitignore_sets(text: str) -> list[tuple[str, ...]]:
    """The ```text gitignore sets, in file order, one line per rule."""
    return [tuple(match.splitlines()) for match in GITIGNORE_FENCE.findall(text)]


def _branch(text: str, heading: str, next_heading: str) -> str:
    """Text between two section headings; empty when the pair is missing."""
    match = re.search(
        rf"^{re.escape(heading)}\n(.*?)(?=^{re.escape(next_heading)}\n|\Z)",
        text, re.MULTILINE | re.DOTALL)
    return match.group(1) if match else ""


def _mentions(text: str, term: str) -> bool:
    """Word-boundary match for words; plain substring for paths such as `.zcode`.
    Both sides are case-folded, so a CamelCase tool name fires like `ListModels`."""
    lowered = text.lower()
    term_lower = term.lower()
    if term[0].isalnum() and term[-1].isalnum():
        return re.search(rf"\b{re.escape(term_lower)}\b", lowered) is not None
    return term_lower in lowered


def _declared_core_roles(text: str) -> tuple[list[str], bool]:
    """Role names of the check list, parsed from the skill's own enumeration.

    The list line is «Сверь роли ядра — `a`, `b`, … — с секциями конфига»;
    whitespace is flattened first because the prose wraps at 80 columns.
    Returns the names and whether the anchor phrase was found at all; every
    backticked token of the span must be a role-shaped name.
    """
    flattened = re.sub(r"\s+", " ", text)
    match = re.search(r"Сверь роли ядра — (.*?) — с секциями конфига", flattened)
    if not match:
        return [], False
    tokens = re.findall(r"`([^`]+)`", match.group(1))
    roles = [token for token in tokens if re.fullmatch(r"[a-z0-9][a-z0-9-]*", token)]
    return roles, len(roles) == len(tokens)


def _continue_skeleton(text: str) -> str:
    """The fenced ```markdown skeleton of docs/ops/continue.md, or a failure."""
    matches = CONTINUE_FENCE.findall(text)
    if not matches:
        raise ValueError("no ```markdown fence at column zero: the skeleton "
                         "fence tag or its indentation changed")
    if len(matches) > 1:
        raise ValueError(f"expected one ```markdown fence, found {len(matches)}: "
                         "a second skeleton block appeared in the skill")
    return matches[0]


def _contract_errors(text: str) -> list[str]:
    """Every violated init contract; empty means the skill is sound."""
    try:
        fields, body = _parse_skill(text)
    except ValueError as exc:
        return [str(exc)]

    errors: list[str] = []
    if fields.get("name") != "init":
        errors.append("frontmatter: name must be init")
    raw_description = fields.get("description", "")
    description = _unquote(raw_description)
    if not description:
        errors.append("frontmatter: missing description")
    elif len(description) > 500:
        errors.append(f"frontmatter: description is {len(description)} chars "
                      "(catalog cap 500)")
    if ": " in description and not (raw_description.startswith('"')
                                    and raw_description.endswith('"')):
        errors.append("frontmatter: description contains ': ' and must be quoted")
    for owned in OWNED_FILES:
        if owned not in description:
            errors.append(f"frontmatter: description misses {owned!r}")
    if SEPARATOR_CLAUSE not in re.sub(r"\s+", " ", description):
        errors.append("frontmatter: description misses the insertion-separator "
                      "clause")

    for needle in ("AGENTS.md", ".gitignore", BEGIN, END, "docs/README.md",
                   "kb-search", "kb-curate", "gitmark.py index",
                   "gitmark.py lint --strict", "gitmark.py map -o docs-map.html",
                   ".agents/skills/", "идемпотент", "вне маркеров", "одну пустую строку",
                   "уже актуален", "замени только внутренний текст",
                   "создай его, содержащим ровно блок ниже",
                   "[WARN]", "[FAIL]"):
        if needle not in body:
            errors.append(f"body: missing {needle!r}")

    flat_body = re.sub(r"\s+", " ", body)
    for needle in NEW_FILE_NEWLINE_RULE:
        if needle not in flat_body:
            errors.append(f"new-file newline rule missing: {needle!r}")
    for needle in HARNESS_NEEDLES:
        if needle not in flat_body:
            errors.append(f"harness: missing {needle!r}")

    for needle in BOOTSTRAP_NEEDLES:
        if needle not in flat_body:
            errors.append(f"bootstrap: missing {needle!r}")

    layout = _branch(body, "## 5. Бутстрап ролей", "## 6. Проверь")
    if not layout:
        errors.append("layout: the bootstrap section is missing")
    else:
        for needle in LAYOUT_NEEDLES:
            if needle not in layout:
                errors.append(f"layout: missing {needle!r}")
        # The pool clauses wrap at 80 columns: check the flattened section.
        flat_layout = re.sub(r"\s+", " ", layout)
        for needle in POOL_NEEDLES:
            if needle not in flat_layout:
                errors.append(f"pool: missing {needle!r}")

    for term in FORBIDDEN:
        if _mentions(text, term):
            errors.append(f"forbidden entity {term!r}")

    # Whitespace is flattened first: the skill prose wraps at 80 columns, so a
    # wording returned across a line break must still redden (panel probe).
    lowered = re.sub(r"\s+", " ", text.lower())
    for phrase in FORBIDDEN_WORDINGS:
        if phrase in lowered:
            errors.append(f"forbidden wording {phrase!r}")

    counted_role = COUNTED_ROLE.search(text)
    if counted_role:
        errors.append(f"bootstrap: a counted role snapshot {counted_role.group(0)!r}")

    counted_question = ORDINAL_QUESTION.search(text)
    if counted_question:
        errors.append(f"bootstrap: a counted question {counted_question.group(0)!r}")

    declared, well_formed = _declared_core_roles(text)
    if not well_formed:
        errors.append("bootstrap: the check list carries a non-role token")
    if not declared:
        errors.append("bootstrap: the core-role check list anchor is missing")
    else:
        for role in CORE_ROLES:
            if role not in declared:
                errors.append(f"bootstrap: the check list misses the {role} role")
        for role in declared:
            if role not in CORE_ROLES:
                errors.append(f"bootstrap: the check list names a phantom {role} role")
        if sorted(declared) != sorted(CORE_ROLES):
            errors.append("bootstrap: the check list is not a permutation of "
                          "the core roles (duplicate entry?)")

    blocks = _blocks(text)
    if len(blocks) != 1:
        errors.append(f"block: expected one fenced ontoship block, got {len(blocks)}")
    else:
        got = blocks[0]
        if got != BLOCK:
            errors.append("block: the fenced ontoship block is not its verbatim "
                          "DSH template")
        for marker in (BEGIN, END):
            if got.count(marker) != 1:
                errors.append(f"block: expected exactly one {marker!r}")
        # Entry-section clauses: one named error per lost clause, so a
        # dropped core command or ship wording reddens with its own name.
        flat_got = re.sub(r"\s+", " ", got)
        for rule in ENTRY_RULES:
            if rule not in flat_got:
                errors.append(f"block: entry rule missing {rule!r}")
        for phrase in BLOCK_RETIRED:
            if phrase in flat_got:
                errors.append(f"block: retired chain vocabulary {phrase!r}")

    gitignore_sets = _gitignore_sets(text)
    if gitignore_sets != [GITIGNORE]:
        errors.append("gitignore: the fenced set is not the verbatim five-line set")

    # The single channel root is literal, not a placeholder: both the block
    # line and the .gitignore set name `.agents/skills`.
    if ".agents/skills/kb-search/gitmark.py" not in text:
        errors.append("body: the literal skill root is missing")

    # The continue skeleton: exactly one ```markdown fence carrying the
    # verbatim template with the five sections (entry-and-continuity).
    try:
        skeleton = _continue_skeleton(text)
    except ValueError as exc:
        errors.append(str(exc))
    else:
        if skeleton != CONTINUE_SKELETON:
            errors.append("continue: the fenced skeleton is not the verbatim template")
        for section in CONTINUE_SECTIONS:
            if f"## {section}" not in skeleton:
                errors.append(f"continue: the skeleton misses the {section} section")
        flat_skeleton = re.sub(r"\s+", " ", skeleton)
        for item in TRANSITION_CHECKLIST:
            if item not in flat_skeleton:
                errors.append(f"continue: the skeleton misses checklist item {item!r}")

    # The continue rules and the ownership contract, whitespace-flattened
    # (case kept — the clause anchors name sentence openings): the prose wraps
    # at 80 columns.
    flat_text = re.sub(r"\s+", " ", text)
    for rule in CONTINUE_RULES:
        if rule not in flat_text:
            errors.append(f"continue: missing rule {rule!r}")
    if OWNERSHIP_COUNT not in flat_text:
        errors.append("ownership: missing the four-file count")
    if DOCS_EXCLUSION not in flat_text:
        errors.append("ownership: the docs/ prohibition is not narrowed to "
                      "the continue skeleton exclusion")
    if SEPARATOR_EXCEPTION not in flat_text:
        errors.append("ownership: the insertion-separator exception is missing")

    # The ownership list itself: all four files as bullets between the section
    # anchor and the prohibition paragraph (panel dwfrun-dee2378e: dropping
    # the skeleton bullet must redden, not just the count phrase).
    own_start = body.find("**Чем владеет init.**")
    own_end = body.find("Init пишет эти четыре файла")
    if own_start == -1 or own_end == -1 or own_start >= own_end:
        errors.append("ownership: the ownership section anchors are missing")
    else:
        list_part = body[own_start:own_end]
        for owned in OWNED_FILES:
            if f"- `{owned}`" not in list_part:
                errors.append(f"ownership: the list misses the {owned} file bullet")

    return errors


def test_skill_is_a_discoverable_directory_bundle():
    """spec: docs/plans/core-kb.md#рамки — skills/init/SKILL.md."""
    assert SKILL.is_file(), "the init skill is missing"
    assert SKILL.parent.name == "init", "bundle directory must match the skill name"
    text = SKILL.read_text("utf-8")
    fields, _ = _parse_skill(text)
    assert fields["name"] == "init"
    assert 3 <= len(_unquote(fields["description"])) <= 500
    assert _contract_errors(text) == []


def test_block_is_verbatim_and_has_one_marker_pair():
    """spec: docs/plans/harness-agnostic.md#готово, docs/plans/dsh-adaptation.md#готово —
    один управляемый блок (DSH с `/ship`), дословный, с одной парой маркеров."""
    text = SKILL.read_text("utf-8")
    assert _blocks(text) == [BLOCK]
    # The prose marker, the template and the verification grep each name the pair.
    assert text.count(BEGIN) == text.count(END) == 3


def test_entry_section_rules_are_pinned_and_mutation_reddens():
    """spec: docs/plans/entry-and-continuity.md#готово (1, 3) — секция
    «Вход в работу»: ship-правило с `/ship`, запрет план-режима без
    харнесс-ветки, состояние и команды."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == [], "the unmutated carrier must be clean"
    assert _blocks(text) == [BLOCK]
    flat_block = re.sub(r"\s+", " ", BLOCK)
    for rule in ENTRY_RULES:
        assert rule in flat_block, f"entry rule missing: {rule!r}"

    for rule in ENTRY_RULES:
        if rule not in BLOCK:
            continue  # wrapped across a line break: pinned on the flat block above
        mutated_block = BLOCK.replace(rule, "", 1)
        mutated = text.replace(BLOCK, mutated_block, 1)
        assert _contract_errors(mutated), f"removal of {rule!r} did not redden"

    # The plan-mode clause stays a negation: flipping it reddens.
    flipped = text.replace("харнесса не используется", "харнесса используется", 1)
    assert flipped != text
    assert _contract_errors(flipped), "negation flip did not redden"

    # Step order: the state rule and the command bullet swap.
    state = ("- Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):\n"
             "  сессия продолжается оттуда и берёт следующий тикет оттуда же.\n")
    commands = ("- Команды: «стартуй юнит» — открыть draft-спеку; `ship` — командой\n"
                "  `/ship` или «исполняй тикет N»; «деплой и обновление [имя_проекта]» —\n"
                "  скилл `deliver`.\n")
    assert state in text and commands in text
    swapped = text.replace(state + commands, commands + state)
    assert swapped != text
    assert _contract_errors(swapped), "step-order swap did not redden"


def test_block_carries_no_chain_vocabulary():
    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3, решение 3:
    блок init несёт команды ядра; словарь ведения снят — «цепочка»,
    «орк-промт», модельный вызов в автономной цепочке живут в team-бандле.
    Мутации: возврат команды цепочки, команды «орк-промт» и снятой
    user-only формулировки краснят контракт; паритет блока держит
    test_repo_managed_block_matches_the_init_block."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == [], "the unmutated carrier must be clean"
    flat_block = re.sub(r"\s+", " ", BLOCK)
    for phrase in BLOCK_RETIRED:
        assert phrase not in flat_block, \
            f"the retired phrase {phrase!r} survives in the block"
    assert "один тикет за запуск — вручную" in flat_block

    chain_back = text.replace(
        "скилл `deliver`.",
        "скилл `deliver`; «цепочка» — автономная цепочка\n"
        "  в чистой сессии, скилл `chain`.", 1)
    assert chain_back != text
    errors = _contract_errors(chain_back)
    assert any("retired chain vocabulary '«цепочка»'" in error
               for error in errors), errors
    assert any("retired chain vocabulary 'скилл `chain`'" in error
               for error in errors), errors

    orc_back = text.replace(
        "скилл `deliver`.",
        "скилл `deliver`; «орк-промт» — инициирующий\n"
        "  промпт оркестратора в continue.md, скилл `to-tickets`.", 1)
    assert orc_back != text
    errors = _contract_errors(orc_back)
    assert any("retired chain vocabulary '«орк-промт»'" in error
               for error in errors), errors
    assert any("retired chain vocabulary 'инициирующий промпт'" in error
               for error in errors), errors

    reverted = text.replace(
        "скилл `ship` исполняет\n"
        "  один тикет за запуск — вручную командой `/ship`;",
        "скилл `ship` вызывается\n"
        "  командой `/ship`, один тикет за запуск;", 1)
    assert reverted != text
    errors = _contract_errors(reverted)
    assert any("скилл `ship` исполняет" in error for error in errors)
    assert any("один тикет за запуск — вручную" in error for error in errors)


def test_continue_skeleton_clauses_are_pinned():
    """spec: docs/plans/entry-and-continuity.md#готово (2) — три случая
    контракта (создание при отсутствии, не-перезапись, идемпотентность)
    запинены как клаузы прозы скилла, вместе с пятью разделами;
    spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3: чек-лист
    четырёх переходов текущего потока; поведение доказывает живой прогон —
    демонстрация тикета и полигон юнита, не этот тест (панель
    dwfrun-dee2378e об имени)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == [], "the unmutated carrier must be clean"
    assert _continue_skeleton(text) == CONTINUE_SKELETON
    flat = re.sub(r"\s+", " ", text)
    for rule in CONTINUE_RULES:
        assert rule in flat, f"continue rule missing: {rule!r}"
    for item in TRANSITION_CHECKLIST:
        assert item in flat, f"checklist item missing: {item!r}"
    description = _unquote(_parse_skill(text)[0]["description"])
    for owned in OWNED_FILES:
        assert owned in description, f"description misses {owned}"


def test_continue_skeleton_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    continue contract rejects a lost or edited skeleton, a lost section, a
    lost checklist item, a flipped create condition, a flipped non-overwrite
    negation, lost report words, the lost date format, the lost idempotency
    clause, a description missing an owned file, a dropped ownership-list
    bullet and a re-widened docs/ prohibition."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    dropped = text.replace(CONTINUE_SKELETON, "", 1)
    assert dropped != text
    assert any("verbatim template" in error
               for error in _contract_errors(dropped))

    renamed_section = text.replace("## Что осталось", "## Остатки", 1)
    assert renamed_section != text
    assert any("Что осталось" in error
               for error in _contract_errors(renamed_section))

    lost_item = text.replace(
        "самопроверка\nпосле приёмки нарезки — скилл `to-tickets`;", "", 1)
    assert lost_item != text
    assert any("checklist item" in error
               for error in _contract_errors(lost_item))

    flipped_condition = text.replace("Файла нет — создай каталог",
                                     "Файл есть — создай каталог", 1)
    assert flipped_condition != text
    assert any("missing rule" in error
               for error in _contract_errors(flipped_condition))

    flipped_negation = text.replace("Файл существует — не правь его ни байта",
                                    "Файл существует — правь его по шаблону", 1)
    assert flipped_negation != text
    assert any("не правь его ни байта" in error
               for error in _contract_errors(flipped_negation))

    lost_created = text.replace("отчёт называет\n`created`", "файл создан", 1)
    assert lost_created != text
    assert any("отчёт называет `created`" in error
               for error in _contract_errors(lost_created))

    rewidened = text.replace("кроме скелета\n`docs/ops/continue.md` при отсутствии файла",
                             "", 1)
    assert rewidened != text
    assert any("docs/ prohibition" in error
               for error in _contract_errors(rewidened))

    three_files = text.replace(OWNERSHIP_COUNT, "Три файла, ничего больше", 1)
    assert three_files != text
    assert any("four-file count" in error
               for error in _contract_errors(three_files))

    lost_date_format = text.replace("в формате YYYY-MM-DD", "", 1)
    assert lost_date_format != text
    assert any("сегодняшняя дата в формате YYYY-MM-DD" in error
               for error in _contract_errors(lost_date_format))

    lost_idempotency = text.replace("не читают и не меняют", "", 1)
    assert lost_idempotency != text
    assert any("последующие запуски init его не читают и не меняют" in error
               for error in _contract_errors(lost_idempotency))

    lost_unchanged = text.replace("отчёт называет `unchanged`", "", 1)
    assert lost_unchanged != text
    assert any("отчёт называет `unchanged`" in error
               for error in _contract_errors(lost_unchanged))

    lost_description = text.replace(
        " и скелет docs/ops/continue.md, когда файла нет", "", 1)
    lost_description = lost_description.replace(
        " и docs/ops/continue.md, а в AGENTS.md", ", а в AGENTS.md", 1)
    assert lost_description != text
    assert any("description misses 'docs/ops/continue.md'" in error
               for error in _contract_errors(lost_description))

    lost_bullet = text.replace(
        "- `docs/ops/continue.md` — скелет состояния работы: init создаёт его, только\n"
        "  когда файла нет; существующий файл init не открывает и не правит.\n", "", 1)
    assert lost_bullet != text
    assert any("the list misses the docs/ops/continue.md file bullet" in error
               for error in _contract_errors(lost_bullet))


def test_gitignore_set_is_five_lines():
    """spec: docs/plans/harness-agnostic.md#готово (с припиской 2026-11-02),
    docs/plans/dsh-adaptation.md#решения (следствие 2), операторское решение
    о чистке ZCode — DSH пишет строки `.gitmark/`, `*-map.html`,
    `.scratch/`, literal корень `.agents/skills/`; пятая строка
    `.agents/packs/` — решение оператора 2026-11-11 при приёмке тикета 02
    standards-autoship (зацепка закрыта после приёмки тикета 03)."""
    text = SKILL.read_text("utf-8")
    assert _gitignore_sets(text) == [GITIGNORE]
    assert len(GITIGNORE) == 5


def test_harness_is_dsh_only():
    """spec: docs/plans/dsh-adaptation.md#решения (следствие 2) — харнесс
    определяется доступным инструментом хоста, не путём; без `subagent` и
    `list_subagent_models` init останавливается с названным пробелом: второй
    ветки нет."""
    text = SKILL.read_text("utf-8")
    flat = re.sub(r"\s+", " ", text)
    for phrase in HARNESS_NEEDLES:
        assert phrase in flat, f"harness rule missing: {phrase!r}"

    no_subagent = text.replace("`list_subagent_models` и `subagent`",
                               "`list_subagent_models`", 1)
    assert no_subagent != text
    assert any("harness: missing" in error for error in _contract_errors(no_subagent))

    by_path = re.sub(r"Нет — назови пробел и остановись", "Нет — определи по пути",
                     text, count=1)
    assert by_path != text
    assert any("harness: missing" in error for error in _contract_errors(by_path))


def test_bootstrap_carries_the_standard_layout():
    """spec: docs/plans/dsh-adaptation.md#решения — стандартная раскладка
    шести ролей: таблица с маршрутами и уровнями, запись без ask, когда
    маршруты живы, и названное отклонение в остальных случаях."""
    text = SKILL.read_text("utf-8")
    layout = _branch(text, "## 5. Бутстрап ролей", "## 6. Проверь")
    assert layout, "the bootstrap section is missing"
    for needle in LAYOUT_NEEDLES:
        assert needle in layout, f"bootstrap section lost {needle!r}"


def test_standard_layout_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the bootstrap contract rejects a lost standard table, a drifted route, a
    drifted level, a lost without-ask rule, a lost deviation report and a
    lost level-default clause."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_table = text.replace("**Стандартная раскладка.**", "Раскладка ролей:", 1)
    assert no_table != text
    assert any("**Стандартная раскладка.**" in error
               for error in _contract_errors(no_table))

    drifted = text.replace("`qwen-token-plan-max/qwen4-max`",
                           "`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`", 1)
    assert drifted != text
    assert any("`qwen-token-plan-max/qwen4-max`" in error
               for error in _contract_errors(drifted))

    drifted_level = text.replace(
        "| `critic` | `qwen-token-plan-max/qwen4-max` | `xhigh` |",
        "| `critic` | `qwen-token-plan-max/qwen4-max` | `medium` |", 1)
    assert drifted_level != text
    assert any("| `critic` |" in error
               for error in _contract_errors(drifted_level))

    drifted_curator_level = text.replace(
        "| `curator` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `low` |",
        "| `curator` | `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017` | `high` |",
        1)
    assert drifted_curator_level != text
    assert any("| `curator` |" in error
               for error in _contract_errors(drifted_curator_level))

    no_askless = text.replace("запиши её без ask",
                              "спроси модель каждой роли", 1)
    assert no_askless != text
    assert any("запиши её без ask" in error
               for error in _contract_errors(no_askless))

    no_deviation = text.replace("назови отклонение от стандарта",
                                "назови выбор", 1)
    assert no_deviation != text
    assert any("назови отклонение от стандарта" in error
               for error in _contract_errors(no_deviation))

    no_level_default = text.replace("штатный дефолт модели", "дефолт харнесса", 1)
    assert no_level_default != text
    assert any("штатный дефолт модели" in error
               for error in _contract_errors(no_level_default))


def test_bootstrap_writes_the_validation_pool():
    """spec: docs/plans/standards-autoship.md#готово — «Готово» 9: init пишет
    стандартную раскладку с пулом flash; маршруты и уровни пула сверяются с
    живым каталогом по тому же правилу, независимость по умолчанию — норма
    реестра; секция пула в существующем конфиге — названный пропуск."""
    text = SKILL.read_text("utf-8")
    layout = _branch(text, "## 5. Бутстрап ролей", "## 6. Проверь")
    assert layout, "the bootstrap section is missing"
    flat_layout = re.sub(r"\s+", " ", layout)
    for needle in POOL_NEEDLES:
        assert needle in flat_layout, f"bootstrap section lost {needle!r}"
    assert "Для паков назови итог" in text


def test_pool_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the pool contract rejects a lost pool marker, a drifted pool route, a
    lost pool level, a lost live-catalog check, a lost independence norm,
    a lost session-model difference and a lost existing-config pool gap."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    for old, new, needle in (
        ("**Пул валидации.**", "Пул:", "**Пул валидации.**"),
        ("`deepseek-account/deepseek-flash`", "`deepseek-account/deepseek-max`",
         "`deepseek-account/deepseek-flash`"),
        ("с уровнем `max`", "с уровнем `high`", "с уровнем `max`"),
        ("Сверь маршруты и уровни пула с живым каталогом",
         "Сверь маршруты пула с конфигом",
         "Сверь маршруты и уровни пула с живым каталогом"),
        ("Независимость по умолчанию — норма реестра",
         "Независимость — по выбору оператора",
         "Независимость по умолчанию — норма реестра"),
        ("ревьюеры идут на модели, отличной от сессионной",
         "ревьюеры идут на любой модели",
         "ревьюеры идут на модели, отличной от сессионной"),
        ("Секция пула валидации `[validation]`", "Секция пула",
         "Секция пула валидации `[validation]`"),
    ):
        # Whitespace-flexible replace: the clause may wrap at 80 columns,
        # the line structure of the rest of the skill stays intact.
        pattern = re.escape(old).replace("\\ ", r"\s+")
        mutated = re.sub(pattern, new, text, count=1)
        assert mutated != text, f"the mutation must change the text: {old!r}"
        assert any(f"pool: missing {needle!r}" in error
                   for error in _contract_errors(mutated)), \
            (old, _contract_errors(mutated))


def test_init_owns_exactly_four_files():
    """spec: docs/plans/review-config.md#готово, docs/plans/entry-and-continuity.md#готово —
    контракт «два файла» расширен до трёх (AGENTS.md, .gitignore,
    .agents/config.toml), затем до четырёх: скелет docs/ops/continue.md;
    запрет docs/ сужен до исключения скелета при отсутствии файла."""
    text = SKILL.read_text("utf-8")
    assert OWNERSHIP_COUNT in text
    assert ".agents/config.toml" in text
    assert "docs/ops/continue.md" in text
    flat = re.sub(r"\s+", " ", text)
    assert DOCS_EXCLUSION in flat


def test_insertion_separator_is_named_not_contradicted():
    """spec: docs/plans/entry-and-continuity.md#готово — case 2 of the marker
    table inserts one separator blank line before the block; the description
    and the ownership section carry that, so «only between the markers» does
    not contradict the insertion (logika K10)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    dropped = text.replace(f" ({SEPARATOR_CLAUSE})", "", 1)
    assert dropped != text
    assert any("insertion-separator clause" in error
               for error in _contract_errors(dropped))

    no_body = re.sub(
        r"одна пустая\s+строка-разделитель перед блоком\s+при его вставке",
        "граница блока", text, count=1)
    assert no_body != text
    assert any("insertion-separator exception" in error
               for error in _contract_errors(no_body))


def test_bootstrap_names_core_roles_and_their_routes():
    """spec: docs/plans/review-config.md#готово — перечень ролей ядра и их
    маршруты: реестр .agents/config.toml, проверка секций по ролям ядра."""
    text = SKILL.read_text("utf-8")
    for role in CORE_ROLES:
        assert role in text, f"core role {role} is not named"
    assert "активных" in text or "живым каталогом" in text
    assert ".agents/config.toml" in text


def test_critic_model_difference_is_a_recommendation():
    """spec: docs/plans/review-config.md#готово — для critic отличие модели от
    сессионной — рекомендация; совпадение допустимо и называется в отчёте
    (поправка 2026-11-09)."""
    text = SKILL.read_text("utf-8")
    flat = re.sub(r"\s+", " ", text)
    assert "рекомендуется отличной от модели сессии" in flat
    assert "назови его в отчёте" in flat
    assert "отказом оно не является" in flat


def test_existing_config_is_untouched_and_a_new_role_is_a_named_gap():
    """spec: docs/plans/review-config.md#ограничения — новая роль ядра при
    существующем конфиге: названный пропуск, без молчаливой дописки."""
    text = SKILL.read_text("utf-8")
    assert "не трогай" in text
    assert "пропуск" in text
    assert "не дописывай" in text


def test_no_model_source_stops_with_a_named_gap():
    """spec: docs/plans/review-config.md#готово — деградация без источника
    моделей — названный пробел."""
    text = SKILL.read_text("utf-8")
    assert "назови пробел и остановись" in text


def test_bootstrap_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    bootstrap contract rejects a lost registry, a lost core role, a lost
    warning and a lost gap rule."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_registry = text.replace(".agents/config.toml", ".agents/roles.toml")
    assert no_registry != text
    assert any(".agents/config.toml" in error for error in _contract_errors(no_registry))

    # "kritic" does not contain the needle, so the replacement really removes it.
    no_critic = text.replace("critic", "kritic")
    assert no_critic != text
    assert any("critic" in error for error in _contract_errors(no_critic))

    no_warning = text.replace("назови его в отчёте", "перевыбор")
    assert no_warning != text
    assert any("назови его в отчёте" in error
               for error in _contract_errors(no_warning))

    no_gap = text.replace("назови пробел и остановись", "остановись")
    assert no_gap != text
    assert any("назови пробел и остановись" in error for error in _contract_errors(no_gap))


def test_zcode_purge_contract_can_fail():
    """invariant: docs/ops/continue.md#снятие-zcode-рельсов — the contract rejects a
    returned ZCode root, host tool, generator, plan-mode parenthetical or a
    placeholder channel root, each named once, in any case."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    for leaked in ("\nUse `.zcode/skills` as the second root.\n",
                   "\nListModels marks the session model.\n",
                   "\nRun gen_agents.py from the init bundle.\n",
                   "\nВ ZCode — план-мод не используется.\n"):
        mutated = text + leaked
        assert _contract_errors(mutated), f"a returned rail {leaked!r} did not redden"


def test_registry_wording_contract_can_fail():
    """invariant: docs/plans/review-loose-ends.md#готово — the wording contract
    rejects the old registry phrase and the old bootstrap heading brought back,
    each once and in any case."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    reverted_body = text.replace("реестр ролей:", "реестр ролей ревью:", 1)
    assert reverted_body != text
    assert any("реестр ролей ревью" in error
               for error in _contract_errors(reverted_body))

    reverted_heading = text.replace("## 5. Бутстрап ролей\n",
                                    "## 5. Бутстрап ролей ревью\n")
    assert reverted_heading != text
    assert any("бутстрап ролей ревью" in error
               for error in _contract_errors(reverted_heading))

    # Case-insensitive: a capitalised return in the description is caught too.
    reverted_description = text.replace("реестр ролей .agents/config.toml",
                                        "Реестр ролей ревью .agents/config.toml")
    assert reverted_description != text
    assert any("реестр ролей ревью" in error
               for error in _contract_errors(reverted_description))

    # A wording wrapped across a line break is caught too.
    wrapped_return = text.replace("реестр ролей:", "реестр ролей\n  ревью:", 1)
    assert wrapped_return != text
    assert any("реестр ролей ревью" in error
               for error in _contract_errors(wrapped_return))


def test_role_count_contract_can_fail():
    """invariant: docs/plans/review-loose-ends.md#цель — формулировки ролей
    нейтральны к росту их числа: the contract rejects a counted check list,
    a counted bootstrap question, a returned review-role count, a phantom
    role and a dropped role in the check list."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    counted_list = text.replace("Сверь роли ядра —", "Сверь шесть ролей ядра —", 1)
    assert counted_list != text
    assert any("counted role snapshot" in error
               for error in _contract_errors(counted_list))

    counted_review = text.replace("Ревью-роли могут делить",
                                  "Четыре ревью-роли могут делить", 1)
    assert counted_review != text
    assert any("counted role snapshot" in error
               for error in _contract_errors(counted_review))

    # The counted-question guard stays armed even though the old curator
    # question wording left the skill with the per-role ask: any ordinal
    # before «вопрос» reddens on injection.
    injected = text + "\nШестой вопрос — модель роли `curator`.\n"
    assert any("counted question" in error
               for error in _contract_errors(injected))

    phantom = text.replace("`reviewer-spec`, `reviewer-tests`,",
                           "`reviewer-spec`, `reviewer-tests`, `extra-role`,", 1)
    assert phantom != text
    assert any("phantom extra-role role" in error
               for error in _contract_errors(phantom))

    dropped = text.replace("`reviewer-spec`, `reviewer-tests`, `reviewer-code`,",
                           "`reviewer-spec`, `reviewer-tests`,", 1)
    assert dropped != text
    assert any("misses the reviewer-code role" in error
               for error in _contract_errors(dropped))

    # Panel probes (dwfrun-71b03204): a duplicate entry, a non-role token,
    # the instrumental case, the next ordinal question, a rephrased anchor
    # and the numeral hidden inside a word.
    duplicated = text.replace("`reviewer-kb`, `critic`, `curator`",
                              "`reviewer-kb`, `critic`, `curator`, `reviewer-kb`", 1)
    assert duplicated != text
    assert any("not a permutation" in error
               for error in _contract_errors(duplicated))

    alien_token = text.replace("`critic`, `curator` — с секциями",
                               "`critic`, `Extra` — с секциями", 1)
    assert alien_token != text
    assert any("non-role token" in error
               for error in _contract_errors(alien_token))

    instrumental = text.replace("Сверь роли ядра —",
                                 "Сверь шестью ролями ядра —", 1)
    assert instrumental != text
    assert any("counted role snapshot" in error
               for error in _contract_errors(instrumental))

    next_ordinal = text + "\nСедьмой вопрос — модель роли `curator`.\n"
    assert any("counted question" in error
               for error in _contract_errors(next_ordinal))

    rephrased_anchor = text.replace("Сверь роли ядра —", "Проверь роли ядра —", 1)
    assert rephrased_anchor != text
    assert any("check list anchor is missing" in error
               for error in _contract_errors(rephrased_anchor))

    # A numeral hidden inside a word must not fire (panel probe: «смотри
    # роли», «опять роль» had redden a word-boundary-less regex).
    for innocent in ("смотри роли", "опять роль", "внутри роли"):
        assert COUNTED_ROLE.search(innocent) is None, innocent


def test_repo_managed_block_matches_the_init_block():
    """invariant: docs/plans/harness-agnostic.md#готово (п. 6),
    docs/plans/dsh-adaptation.md#готово (2) — собственный блок репозитория
    равен DSH-шаблону init: корень в блоке literal, подстановки нет;
    прогон init из другой копии бандла перепишет блок — ожидаемое поведение,
    не дефект."""
    import re as _re

    agents = (REPO / "AGENTS.md").read_text("utf-8")
    match = _re.search(
        rf"{_re.escape(BEGIN)}\n(.*?){_re.escape(END)}", agents, _re.DOTALL)
    assert match, "the managed block is missing from AGENTS.md"
    inner = match.group(1)
    expected = BLOCK.replace(f"{BEGIN}\n", "").replace(f"\n{END}", "")
    assert inner.strip("\n") == expected.strip("\n")


PACK_DISCOVERY_NEEDLES = (
    ".agents/packs/",
    "validate_pack.py",
    "reviewer-<kontur>-<aspect>",
    "невалидный манифест",
    "бутстрап-вопросом",
    "останови шаг",
    "ask поднимает оркестратор",
    "Конфиг существует",
    "Конфига нет",
    "канон > стандарты проекта > пак команды > пак стека > базовый документ",
)


def _pack_discovery_missing(text: str) -> list[str]:
    layout = _branch(text, "## 5. Бутстрап ролей", "## 6. Проверь")
    if not layout:
        return ["bootstrap section missing"]
    marker = "**Паки стандартов.**"
    if marker not in layout:
        return ["pack block missing"]
    block = layout.split(marker, 1)[1]
    flat = re.sub(r"\s+", " ", block)
    return [needle for needle in PACK_DISCOVERY_NEEDLES if needle not in flat]


def test_bootstrap_discovers_and_registers_packs():
    """spec: docs/plans/standards-autoship.md#готово — init обнаруживает
    .agents/packs/, валидирует манифесты валидатором бандла pack, называет
    пропуски; роли паков регистрируются бутстрап-вопросом, существующий
    конфиг не трогается; приоритет норм назван."""
    text = SKILL.read_text("utf-8")
    assert _pack_discovery_missing(text) == []
    assert "Для паков назови итог" in text


def test_missing_registry_section_stops_the_bootstrap():
    """spec: docs/plans/standards-autoship.md#готово — реестр без секции
    роли или пула останавливает шаг до ответа оператора; в делегированном
    прогоне ask поднимает оркестратор; формулировка «предложи добавить»
    не возвращается (пробел жил в отчёте и не доходил до решения)."""
    text = SKILL.read_text("utf-8")
    assert "предложи добавить" not in text
    assert text.count("останови шаг") >= 3
    assert "ask поднимает оркестратор" in text


def test_pack_discovery_contract_can_fail():
    """spec: docs/plans/standards-autoship.md#готово — контракт обнаружения
    паков умеет падать: потеря каждого носителя краснит проверку. Мутация
    живёт внутри блока паков: «Конфиг существует»/«Конфига нет» есть и в
    бутстрапе ядра, их удаление там не снимает блок паков."""
    text = SKILL.read_text("utf-8")
    assert _pack_discovery_missing(text) == []
    marker = "**Паки стандартов.**"
    head, block = text.split(marker, 1)
    for needle in PACK_DISCOVERY_NEEDLES:
        pattern = re.escape(needle).replace("\\ ", r"\s+")
        mutated_block = re.sub(pattern, "", block, count=1, flags=re.IGNORECASE)
        assert mutated_block != block, \
            f"the mutation must change the text: {needle!r}"
        mutated = head + marker + mutated_block
        assert needle in _pack_discovery_missing(mutated), needle


# team-profiles 04 («Готово» 6, решение 15; спека перенесена в
# ontoship-team, носитель нормы — core-team-boundaries «Готово» 3):
# init называет team-бандл ссылкой в §5/отчёте — роли команды поставляет
# DSH-бандл пресетов уровня профиля, не пак стандартов. Имени личного
# репозитория и литералов маршрутов в навыке нет: init остаётся реестром
# панели и куратора, а канал поставки бандла — профиль, не проект.
TEAM_REFERENCE_NEEDLES = (
    "**Роли команды.**",
    "DSH-бандл пресетов уровня профиля, не пак стандартов",
    "init бандл не устанавливает",
    "Установку сверь перечнем бандлов профиля (`plugin_manager`)",
    "назови его в отчёте ссылкой на установленный бандл профиля",
    "без имени личного репозитория и без литералов маршрутов",
    "инструмента нет — назови пробел",
)
TEAM_REPORT_NEEDLE = (
    "Для ролей команды назови team-бандл ссылкой на установленный бандл"
)
PERSONAL_REPO_NAME = "ontoship-team"
ROUTE_TOKENS = ("qwen", "deepseek", "xhigh", "/max", "/high")


def _team_paragraph(text: str) -> str:
    """Блок «Роли команды» в §5: до блока конфига или до конца шага."""
    layout = _branch(text, "## 5. Бутстрап ролей", "## 6. Проверь")
    marker = "**Роли команды.**"
    if marker not in layout:
        return ""
    block = layout.split(marker, 1)[1]
    return marker + block.split("**Конфиг существует.**", 1)[0]


def _team_reference_missing(text: str) -> list[str]:
    """Нарушения ссылки init на team-бандл; пусто — навык звучит верно."""
    paragraph = _team_paragraph(text)
    if not paragraph:
        return ["team-bundle reference block missing"]
    flat = re.sub(r"\s+", " ", paragraph)
    missing = [needle for needle in TEAM_REFERENCE_NEEDLES if needle not in flat]
    if PERSONAL_REPO_NAME in text.lower():
        missing.append("personal repo name is named")
    missing.extend(f"route literal {token!r}" for token in ROUTE_TOKENS
                   if token in flat.lower())
    report = re.sub(r"\s+", " ", text.split("## 7. Отчёт", 1)[-1])
    if TEAM_REPORT_NEEDLE not in report:
        missing.append("report line names the bundle by reference")
    return missing


def test_team_bundle_is_named_by_reference():
    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3 (перенос
    team-profiles 05; бывш. «Готово» 6 team-profiles, решение 15):
    init называет team-бандл ссылкой в §5 и отчёте; роли команды — DSH-бандл
    пресетов уровня профиля, не пак; имени личного репозитория и литералов
    маршрутов нет. Красная проба — на базе team-profiles 04 (секции не было)."""
    text = SKILL.read_text("utf-8")
    assert _team_reference_missing(text) == []


def test_team_reference_contract_can_fail():
    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3 (перенос
    team-profiles 05; бывш. «Готово» 6 team-profiles, решение 15):
    проверка ссылки init умеет падать — потеря каждого якоря, возврат имени
    личного репозитория, литерала маршрута и потеря строки отчёта краснят
    её. Ожидаемые значения — из «Готово» 3 и решения 3 спеки границ
    (решение 15 team-profiles инкорпорировано решением 3; носитель после
    переноса — ontoship-team/docs/plans/team-profiles.md), не из текста
    навыка."""
    text = SKILL.read_text("utf-8")
    assert _team_reference_missing(text) == []

    for needle in TEAM_REFERENCE_NEEDLES:
        pattern = re.escape(needle).replace("\\ ", r"\s+")
        mutated = re.sub(pattern, "", text, count=1, flags=re.IGNORECASE)
        assert mutated != text, f"the mutation must change the text: {needle!r}"
        assert _team_reference_missing(mutated), needle

    assert _team_reference_missing(
        text.replace("**Роли команды.**", f"**Роли команды** `{PERSONAL_REPO_NAME}`.", 1))
    assert _team_reference_missing(
        text.replace("пакет и версия", "пакет, версия и маршрут "
                     "`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`/`max`", 1))
    assert _team_reference_missing(
        text.replace(TEAM_REPORT_NEEDLE, "Для ролей команды назови бандл пакетом.", 1))


def test_new_file_newline_rule_is_pinned_and_mutation_reddens():
    """spec: docs/plans/entry-and-continuity.md#готово (2) — уточнение
    случая «файл отсутствует»: новый файл байт-в-байт по шаблону, включая
    завершающий перевод строки; граница правила сохранения байтов (только
    существующие файлы) запинена; удаление клаузы и снятие границы краснят
    (рецидив исполнения S4/S5/S4b пробы deliver/03, ишью norm-fixes/01)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == [], "the unmutated carrier must be clean"
    flat = re.sub(r"\s+", " ", text)
    for rule in NEW_FILE_NEWLINE_RULE:
        assert rule in flat, f"new-file newline rule missing: {rule!r}"

    for rule in NEW_FILE_NEWLINE_RULE:
        pattern = re.escape(rule).replace("\\ ", r"\s+")
        mutated = re.sub(pattern, "", text, count=1)
        assert mutated != text, f"the mutation must change the text: {rule!r}"
        assert _contract_errors(mutated), f"removal of {rule!r} did not redden"

    widened = text.replace("относится только к существующим файлам",
                           "относится ко всем файлам", 1)
    assert widened != text
    assert _contract_errors(widened), "scope widening did not redden"
