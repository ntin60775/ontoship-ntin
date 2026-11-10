"""Contract for the init skill and the managed blocks it writes.

The skill is prose: its "code" is the text an agent follows. These checks pin the
shipped artifact — the DSH frontmatter, the four files init owns (AGENTS.md,
.gitignore, the role registry .agents/config.toml and the docs/ops/continue.md
skeleton), the marker cases, the verbatim DSH and ZCode blocks, the continue
skeleton and the bootstrap contract — and prove the check can fail (mutation
probe).

spec: docs/plans/harness-agnostic.md#готово — skills/init/SKILL.md, the managed blocks,
      .gitignore (four lines), harness-neutral prose
spec: docs/plans/dsh-adaptation.md#готово — «Готово» 2: харнесс по инструменту,
      блок DSH с `/ship`, четыре строки в DSH и шесть в ZCode, конфиг из
      `list_subagent_models` без генератора, ZCode-ветка сохранена
spec: docs/plans/entry-and-continuity.md#готово — init создаёт скелет
      docs/ops/continue.md при отсутствии: пять разделов и чек-лист трёх
      переходов дословно; существующий файл не перезаписывается, отчёт
      называет created или unchanged; контракт владения — четыре файла
spec: docs/plans/review-config.md#готово — init спрашивает модели ролей ядра
      ask-ом, пишет .agents/config.toml и запускает генератор из бандла
spec: docs/plans/onto-doc.md#готово — init спрашивает куратора шестым вопросом:
      рекомендация — дефолт решения 3 по правилу отклонения решения 9, уровень —
      максимум из доступных, без уровней ключ опускается
invariant: docs/plans/workflow-skills.md#ограничения — no registry, provenance, Reel or
      acceptance chord
invariant: docs/plans/harness-agnostic.md#готово — no harness root named
"""
from __future__ import annotations

import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SKILL = REPO / "skills" / "init" / "SKILL.md"
BEGIN = "<!-- BEGIN ontoship -->"
END = "<!-- END ontoship -->"
# Two harness branches (dsh-adaptation, technical consequences 1 and 2): the
# host tool picks the branch, and each branch writes its own managed block and
# .gitignore set. DSH needs four lines; ZCode adds the generated definitions
# and the vendored workflows.
GITIGNORE_DSH = (".gitmark/", "*-map.html", ".scratch/", "<навыковый корень>/")
GITIGNORE_ZCODE = GITIGNORE_DSH + (".zcode/agents/", ".zcode/workflows/")
CORE_ROLES = ("reviewer-spec", "reviewer-tests", "reviewer-code", "reviewer-kb", "critic",
              "curator")
# Channel-neutral template: the skill-bundle root is substituted at run time
# (.agents/skills for the installer, .zcode/skills for the marketplace plugin).
GENERATOR_LINE = "python3 <навыковый корень>/init/gen_agents.py <корень проекта>"
CURATOR_DEFAULT = "account:zai-individual-coding-plan/GLM-5.3-Flash"
# The ownership contract (entry-and-continuity «Готово» 2): the four files,
# the count phrase and the docs/ prohibition narrowed to the skeleton
# exclusion. Single source: the needles, the list check and the mutations
# all read these constants (panel dwfrun-dee2378e).
OWNED_FILES = ("AGENTS.md", ".gitignore", ".agents/config.toml",
               "docs/ops/continue.md")
OWNERSHIP_COUNT = "Четыре файла, ничего больше"
DOCS_EXCLUSION = ("не пишет ничего в `docs/`, кроме скелета "
                  "`docs/ops/continue.md` при отсутствии файла")
BOOTSTRAP_NEEDLES = (
    OWNERSHIP_COUNT,
    ".agents/config.toml",
    "назови пробел и остановись",
    "активные модели",
    "модель сессии",
    "рекомендуется отличной от модели сессии",
    "назови его в отчёте",
    "пропуск",
    "не дописывай",
    "не трогай",
    GENERATOR_LINE,
    "Сверь роли ядра",
    "`critic`, `curator` — с секциями конфига",
    "Отдельный вопрос — модель роли `curator`",
    CURATOR_DEFAULT,
    "пока она в списке активных",
    "назови отклонение от дефолта",
    "максимум из доступных уровней выбранной модели",
    "тот же список активных моделей шага 1",
    "У модели без уровней ключ `level` опусти",
) + CORE_ROLES

# Harness selection (dsh-adaptation, technical consequence 2): the tool the
# host exposes picks the branch; neither or both stops with an operator
# question. The DSH branch lists routes, keeps the session model from runtime
# context, writes `<provider>/<model>` with the maximum effort and skips the
# generator; the ZCode branch keeps `ListModels`, `[current]`, six lines and
# the bundled generator.
HARNESS_NEEDLES = (
    "определяется доступным инструментом",
    "не путём и не файлом проекта",
    "`list_subagent_models`",
    "`subagent`",
    "`ListModels`",
    "Ни одного или оба",
    "задай вопрос оператору и остановись",
    "DSH-ветка пишет блок DSH с командой `/ship`",
    "ZCode-ветка — блок ZCode",
)
DSH_BRANCH_NEEDLES = (
    "`list_subagent_models`",
    "runtime-контекст",
    "`<provider>/<model>`",
    "спроси оператора",
    "`gen_agents.py` не запускай",
    "`.zcode/agents/`",
    "`.zcode/workflows/`",
    "не создавай",
    "дефолт модели",
    # Standard delivery (2026-11-10): the six core roles ship one layout,
    # written without an ask when every route and level is live.
    "**Стандартная раскладка.**",
    "`qwen-token-plan/qwen3.8-flash`",
    "`qwen-token-plan/qwen3.8-max`",
    "`xhigh`",
    "`medium`",
    "запиши её без ask",
    "назови отклонение от стандарта",
)
ZCODE_BRANCH_NEEDLES = (
    "`ListModels`",
    "[current]",
    GENERATOR_LINE,
    "перезапуск",
)
FORBIDDEN = ("registry", "provenance", "reel", "acceptance chord", "inventory",
             "serve", ".dsh", ".qoder", "commands.md")
# .zcode left the list with the marketplace-plugin channel: .zcode/skills is a
# legitimate skill-bundle root now, and .zcode/agents is the generator's home.
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

# The two managed blocks, pinned independently of the skill text: the expected
# values are these literals, not re-extractions. DSH carries `/ship` and the
# `.agents/skills` root; ZCode stays as it was and keeps both roots.
BLOCK_DSH = """\
<!-- BEGIN ontoship -->
## База знаний (OntoShip)

- Точка входа: [`docs/README.md`](docs/README.md) — главный индекс KB; у каждой папки
  есть индекс `README.md`.
- Ищи до ответа или записи: загрузи скилл `kb-search`. Движок лежит в
  `<навыковый корень>/kb-search/gitmark.py`; корень — `.agents/skills`.
- Новые или обновлённые документы: загрузи скилл `kb-curate` — сначала поиск, никогда
  не дублируй.
- Сопровождение после правки документов:

  ```sh
  python3 <навыковый корень>/kb-search/gitmark.py index
  python3 <навыковый корень>/kb-search/gitmark.py lint --strict
  python3 <навыковый корень>/kb-search/gitmark.py map -o docs-map.html
  ```

- KB — это markdown + git: `.gitmark/`, `*-map.html` и `.scratch/` производные или
  эфемерные — никогда не коммитятся.

## Вход в работу (OntoShip)

- Изменения этого проекта идут через ship-флоу: скилл `ship` вызывается
  командой `/ship`, один тикет за запуск; свободные правки в обход тикета
  не делаются — прямые решения оператора выше этого правила.
- Запрос плана открывает draft-спеку через скилл `grilling`; режим плана
  харнесса (в ZCode — план-мод) не используется.
- Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):
  сессия продолжается оттуда и берёт следующий тикет оттуда же.
- Команды: «стартуй юнит» — открыть draft-спеку; `ship` — командой
  `/ship` или «исполняй тикет N».
<!-- END ontoship -->
"""

BLOCK_ZCODE = """\
<!-- BEGIN ontoship -->
## База знаний (OntoShip)

- Точка входа: [`docs/README.md`](docs/README.md) — главный индекс KB; у каждой папки
  есть индекс `README.md`.
- Ищи до ответа или записи: загрузи скилл `kb-search`. Движок лежит в
  `<навыковый корень>/kb-search/gitmark.py`; корень — `.agents/skills` или
  `.zcode/skills`, по каналу установки.
- Новые или обновлённые документы: загрузи скилл `kb-curate` — сначала поиск, никогда
  не дублируй.
- Сопровождение после правки документов:

  ```sh
  python3 <навыковый корень>/kb-search/gitmark.py index
  python3 <навыковый корень>/kb-search/gitmark.py lint --strict
  python3 <навыковый корень>/kb-search/gitmark.py map -o docs-map.html
  ```

- KB — это markdown + git: `.gitmark/`, `*-map.html` и `.scratch/` производные или
  эфемерные — никогда не коммитятся.

## Вход в работу (OntoShip)

- Изменения этого проекта идут через ship-флоу: скилл `ship` по команде
  оператора, один тикет за запуск; свободные правки в обход тикета не
  делаются — прямые решения оператора выше этого правила.
- Запрос плана открывает draft-спеку через скилл `grilling`; режим плана
  харнесса (в ZCode — план-мод) не используется.
- Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):
  сессия продолжается оттуда и берёт следующий тикет оттуда же.
- Команды: «стартуй юнит» — открыть draft-спеку; «исполняй тикет N» — ship
  тикета N.
<!-- END ontoship -->
"""

BLOCKS = (BLOCK_DSH, BLOCK_ZCODE)

# Rule clauses of the entry section (docs/plans/entry-and-continuity.md,
# «Готово» 1, 3): one anchor per clause, so a dropped clause reddens with its
# own name. The ship clause is the harness branch: DSH names `/ship`, ZCode
# keeps the operator-command wording.
ENTRY_RULES_COMMON = (
    "свободные правки в обход тикета не",
    "Запрос плана открывает draft-спеку через скилл `grilling`",
    "харнесса (в ZCode — план-мод) не используется",
    "Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):",
)
ENTRY_RULES_DSH = (
    "скилл `ship` вызывается",
    "командой `/ship`",
    "`/ship` или «исполняй тикет N»",
)
ENTRY_RULES_ZCODE = (
    "идут через ship-флоу: скилл `ship` по команде",
    "«исполняй тикет N» — ship",
)

# The continue.md skeleton shipped by init (docs/plans/entry-and-continuity.md,
# «Готово» 2). The five section headings and the three-transition checklist are
# the spec's requirement; the frontmatter, the intro line and the section
# bodies are the template's own prose, pinned verbatim here independently of
# the skill text — the expected value is this literal, not a re-extraction.
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
вычитка спеки перед план-гейтом — скилл `grilling`; критик после нарезки —
скилл `to-tickets`; ревью-панель перед merge — скилл `ship`.
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
# section: one anchor per transition.
TRANSITION_CHECKLIST = (
    "вычитка спеки перед план-гейтом — скилл `grilling`",
    "критик после нарезки — скилл `to-tickets`",
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
    """Word-boundary match for words; plain substring for paths such as `.zcode`."""
    lowered = text.lower()
    if term[0].isalnum() and term[-1].isalnum():
        return re.search(rf"\b{re.escape(term)}\b", lowered) is not None
    return term in lowered


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

    for needle in ("AGENTS.md", ".gitignore", BEGIN, END, "docs/README.md",
                   "kb-search", "kb-curate", "gitmark.py index",
                   "gitmark.py lint --strict", "gitmark.py map -o docs-map.html",
                   ".agents/skills/", "идемпотент", "вне маркеров", "одну пустую строку",
                   "уже актуален", "замени только внутренний текст",
                   "создай его, содержащим ровно блок выбранной ветки ниже",
                   "[WARN]", "[FAIL]"):
        if needle not in body:
            errors.append(f"body: missing {needle!r}")

    flat_body = re.sub(r"\s+", " ", body)
    for needle in HARNESS_NEEDLES:
        if needle not in flat_body:
            errors.append(f"harness: missing {needle!r}")

    for needle in BOOTSTRAP_NEEDLES:
        if needle not in body:
            errors.append(f"bootstrap: missing {needle!r}")

    dsh = _branch(body, "### DSH", "### ZCode")
    zcode = _branch(body, "### ZCode", "## 6. Проверь")
    if not dsh:
        errors.append("branches: the DSH bootstrap section is missing")
    else:
        for needle in DSH_BRANCH_NEEDLES:
            if needle not in dsh:
                errors.append(f"dsh: missing {needle!r}")
    if not zcode:
        errors.append("branches: the ZCode bootstrap section is missing")
    else:
        for needle in ZCODE_BRANCH_NEEDLES:
            if needle not in zcode:
                errors.append(f"zcode: missing {needle!r}")

    for term in FORBIDDEN:
        if _mentions(text, term):
            errors.append(f"forbidden entity {term!r}")

    # Whitespace is flattened first: the skill prose wraps at 80 columns, so a
    # wording returned across a line break must still redden (panel probe).
    flattened = re.sub(r"\s+", " ", text.lower())
    for phrase in FORBIDDEN_WORDINGS:
        if phrase in flattened:
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
    if len(blocks) != len(BLOCKS):
        errors.append(f"block: expected {len(BLOCKS)} fenced ontoship blocks, "
                      f"got {len(blocks)}")
    else:
        for got, expected in zip(blocks, BLOCKS):
            if got != expected:
                errors.append("block: a fenced ontoship block is not its "
                              "verbatim DSH/ZCode template")
            for marker in (BEGIN, END):
                if got.count(marker) != 1:
                    errors.append(f"block: expected exactly one {marker!r}")

    gitignore_sets = _gitignore_sets(text)
    if gitignore_sets != [GITIGNORE_DSH, GITIGNORE_ZCODE]:
        errors.append("gitignore: the two fenced sets are not the verbatim "
                      "DSH four-line and ZCode six-line sets")

    # The channel line is a placeholder rule; both channel roots are named in
    # the prose around it, so a plugin-installed init writes its own root.
    for root in (".agents/skills/", ".zcode/skills/"):
        if root not in text:
            errors.append(f"body: the channel root {root!r} is missing")

    # The substitution rule: without it init writes the placeholder verbatim.
    # Whitespace is flattened: the prose wraps at 80 columns.
    flattened = re.sub(r"\s+", " ", text)
    for phrase in ("подставь корень канала установки",
                   "при сравнении и при записи"):
        if phrase not in flattened:
            errors.append(f"body: missing substitution rule {phrase!r}")

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

    # The continue rules and the ownership contract, whitespace-flattened:
    # the prose wraps at 80 columns.
    for rule in CONTINUE_RULES:
        if rule not in flattened:
            errors.append(f"continue: missing rule {rule!r}")
    if OWNERSHIP_COUNT not in flattened:
        errors.append("ownership: missing the four-file count")
    if DOCS_EXCLUSION not in flattened:
        errors.append("ownership: the docs/ prohibition is not narrowed to "
                      "the continue skeleton exclusion")

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


def test_blocks_are_verbatim_and_each_has_one_marker_pair():
    """spec: docs/plans/harness-agnostic.md#готово, docs/plans/dsh-adaptation.md#готово —
    два управляемых блока (DSH с `/ship` и ZCode), каждый дословный, с одной
    парой маркеров."""
    text = SKILL.read_text("utf-8")
    assert _blocks(text) == list(BLOCKS)
    # The prose marker, two templates and the verification grep each name the pair.
    assert text.count(BEGIN) == text.count(END) == 4


def test_entry_section_rules_are_pinned_and_mutation_reddens():
    """spec: docs/plans/entry-and-continuity.md#готово (1, 3),
    docs/plans/dsh-adaptation.md#готово (2) — секция «Вход в работу» в двух
    ветках: общие правила и различие ship-команды (`/ship` только в DSH)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == [], "the unmutated carrier must be clean"
    assert _blocks(text) == list(BLOCKS)
    dsh, zcode = (re.sub(r"\s+", " ", block) for block in _blocks(text))
    for rule in ENTRY_RULES_COMMON:
        assert rule in dsh, f"common entry rule missing in DSH: {rule!r}"
        assert rule in zcode, f"common entry rule missing in ZCode: {rule!r}"
    for rule in ENTRY_RULES_DSH:
        assert rule in dsh, f"DSH entry rule missing: {rule!r}"
    for rule in ENTRY_RULES_ZCODE:
        assert rule in zcode, f"ZCode entry rule missing: {rule!r}"
    assert "/ship" not in zcode

    dsh_block = _blocks(text)[0]
    for rule in ENTRY_RULES_DSH:
        mutated_block = dsh_block.replace(rule, "", 1)
        assert mutated_block != dsh_block, f"removal of {rule!r} changed nothing"
        mutated = text.replace(dsh_block, mutated_block, 1)
        assert _contract_errors(mutated), f"removal of {rule!r} did not redden"

    flipped = text.replace("харнесса (в ZCode — план-мод) не используется",
                           "харнесса (в ZCode — план-мод) используется")
    assert flipped != text
    assert _contract_errors(flipped), "negation flip did not redden"

    # Step order in the DSH block: the state rule and the command bullet swap.
    state = ("- Состояние и порядок работы — [docs/ops/continue.md](docs/ops/continue.md):\n"
             "  сессия продолжается оттуда и берёт следующий тикет оттуда же.\n")
    commands = ("- Команды: «стартуй юнит» — открыть draft-спеку; `ship` — командой\n"
                "  `/ship` или «исполняй тикет N».\n")
    assert state in text and commands in text
    swapped = text.replace(state + commands, commands + state)
    assert swapped != text
    assert _contract_errors(swapped), "step-order swap did not redden"


def test_continue_skeleton_clauses_are_pinned():
    """spec: docs/plans/entry-and-continuity.md#готово (2) — три случая
    контракта (создание при отсутствии, не-перезапись, идемпотентность)
    запинены как клаузы прозы скилла, вместе с пятью разделами и чек-листом
    трёх переходов; поведение доказывает живой прогон — демонстрация тикета
    и полигон юнита, не этот тест (панель dwfrun-dee2378e об имени)."""
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

    lost_item = text.replace("критик после нарезки —\nскилл `to-tickets`;", "", 1)
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


def test_gitignore_sets_are_four_for_dsh_and_six_for_zcode():
    """spec: docs/plans/harness-agnostic.md#готово (с припиской 2026-11-02),
    docs/plans/dsh-adaptation.md#решения (следствие 2) — DSH пишет четыре
    строки (`.gitmark/`, `*-map.html`, `.scratch/`, корень), ZCode — те же
    шесть: добавляются `.zcode/agents/` и `.zcode/workflows/`."""
    text = SKILL.read_text("utf-8")
    assert _gitignore_sets(text) == [GITIGNORE_DSH, GITIGNORE_ZCODE]
    assert len(GITIGNORE_DSH) == 4
    assert len(GITIGNORE_ZCODE) == 6


def test_harness_is_chosen_by_the_host_tool():
    """spec: docs/plans/dsh-adaptation.md#решения (следствие 2) — харнесс
    определяется доступным инструментом хоста, не путём: DSH — `subagent` и
    `list_subagent_models`, ZCode — `ListModels`; ни одного или оба — вопрос
    оператору и остановка."""
    text = SKILL.read_text("utf-8")
    flat = re.sub(r"\s+", " ", text)
    for phrase in HARNESS_NEEDLES:
        assert phrase in flat, f"harness rule missing: {phrase!r}"
    assert "не путём и не файлом проекта" in flat

    no_subagent = text.replace("`list_subagent_models` и `subagent`",
                               "`list_subagent_models`", 1)
    assert no_subagent != text
    assert any("harness: missing" in error for error in _contract_errors(no_subagent))

    by_path = re.sub(r"не путём и не файлом\s+проекта", "по пути проекта",
                     text, count=1)
    assert by_path != text
    assert any("harness: missing" in error for error in _contract_errors(by_path))

    no_block_choice = text.replace(
        "DSH-ветка пишет блок DSH с командой `/ship`", "", 1)
    assert no_block_choice != text
    assert any("harness: missing" in error for error in _contract_errors(no_block_choice))


def test_dsh_branch_writes_four_lines_and_skips_the_generator():
    """spec: docs/plans/dsh-adaptation.md#готово (2), следствия 1–3 — DSH-ветка:
    маршруты из `list_subagent_models`, `<provider>/<model>`, максимум уровня,
    модель сессии из runtime-контекста, четыре строки и никакого генератора."""
    text = SKILL.read_text("utf-8")
    dsh = _branch(text, "### DSH", "### ZCode")
    assert dsh, "the DSH bootstrap section is missing"
    for needle in DSH_BRANCH_NEEDLES:
        assert needle in dsh, f"DSH branch lost {needle!r}"
    assert GENERATOR_LINE not in dsh
    assert "четыре строки" in text
    assert "/ship" in _blocks(text)[0]
    assert ".zcode/skills" not in _blocks(text)[0]


def test_zcode_branch_keeps_listmodels_and_generator():
    """spec: docs/plans/dsh-adaptation.md#ограничения — ZCode legacy: шесть
    строк, `ListModels` с `[current]`, генератор определений и перезапуск
    хоста сохранены."""
    text = SKILL.read_text("utf-8")
    zcode = _branch(text, "### ZCode", "## 6. Проверь")
    assert zcode, "the ZCode bootstrap section is missing"
    for needle in ZCODE_BRANCH_NEEDLES:
        assert needle in zcode, f"ZCode branch lost {needle!r}"
    assert "шесть строк" in text


def test_dsh_branch_carries_the_standard_layout():
    """spec: docs/plans/dsh-adaptation.md#решения — стандартная раскладка
    шести ролей в DSH-ветке `init`: таблица с маршрутами и уровнями, запись
    без ask, когда маршруты живы, и названное отклонение в остальных случаях.
    """
    dsh = _branch(SKILL.read_text("utf-8"), "### DSH", "### ZCode")
    assert dsh
    for needle in ("**Стандартная раскладка.**",
                   "`qwen-token-plan/qwen3.8-flash`",
                   "`qwen-token-plan/qwen3.8-max`",
                   "`xhigh`", "`medium`",
                   "запиши её без ask",
                   "назови отклонение от стандарта"):
        assert needle in dsh, f"DSH branch lost the standard needle {needle!r}"


def test_standard_layout_branch_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества —
    the DSH branch contract rejects a lost standard table, a drifted level, a
    lost without-ask rule and a lost deviation report."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_table = text.replace("**Стандартная раскладка.**", "Раскладка ролей:", 1)
    assert no_table != text
    assert any("**Стандартная раскладка.**" in error
               for error in _contract_errors(no_table))

    drifted = text.replace("`qwen-token-plan/qwen3.8-max`",
                           "`qwen-token-plan/qwen3.8-flash`", 1)
    assert drifted != text
    assert any("`qwen-token-plan/qwen3.8-max`" in error
               for error in _contract_errors(drifted))

    no_medium = text.replace("`medium`", "`high`", 1)
    assert no_medium != text
    assert any("`medium`" in error for error in _contract_errors(no_medium))

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


def test_dsh_branch_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    DSH branch contract rejects a lost host-tool choice, a lost live route
    listing, a lost runtime session model, a restored generator and a lost
    four-line set."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_tool = text.replace("`list_subagent_models`", "`models`")
    assert no_tool != text
    assert any("harness: missing" in error for error in _contract_errors(no_tool))

    no_listmodels = text.replace("`ListModels`", "`models`")
    assert no_listmodels != text
    assert any("harness: missing" in error for error in _contract_errors(no_listmodels))

    no_runtime = text.replace("runtime-контекст", "описание сессии")
    assert no_runtime != text
    assert any("dsh: missing" in error for error in _contract_errors(no_runtime))

    restored_generator = text.replace(
        "`gen_agents.py` не запускай",
        "запусти `gen_agents.py`")
    assert restored_generator != text
    assert any("dsh: missing" in error for error in _contract_errors(restored_generator))

    lost_four = text.replace("\n".join(GITIGNORE_DSH) + "\n", "", 1)
    assert lost_four != text
    assert any("gitignore: the two fenced sets" in error
               for error in _contract_errors(lost_four))


def test_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    contract check rejects a missing marker, line, name or a leaked entity."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    missing_end = text.replace(f"\n{END}\n", "\n", 1)
    assert missing_end != text
    assert any("fenced ontoship block" in error for error in _contract_errors(missing_end))

    missing_rule = text.replace("\n*-map.html\n", "\n*-map.html.bak\n", 1)
    assert missing_rule != text
    assert any("gitignore: the two fenced sets" in error
               for error in _contract_errors(missing_rule))

    leaked_entity = text + "\nCreate the docs/reference/commands.md registry.\n"
    assert any("registry" in error for error in _contract_errors(leaked_entity))

    leaked_qoder_root = text + "\nInstall into .qoder/skills instead.\n"
    assert any(".qoder" in error for error in _contract_errors(leaked_qoder_root))

    leaked_legacy_root = text + "\nKeep the old .dsh/skills link.\n"
    assert any(".dsh" in error for error in _contract_errors(leaked_legacy_root))

    missing_name = "\n".join(line for line in text.splitlines()
                             if not line.startswith("name:"))
    assert any("name" in error for error in _contract_errors(missing_name))

    unquoted_description = "\n".join(
        "description: " + _unquote(line[len('description: "'):-1])
        if line.startswith('description: "') else line
        for line in text.splitlines())
    assert unquoted_description != text
    assert any("must be quoted" in error
               for error in _contract_errors(unquoted_description))

    edited_block = text.replace("## База знаний (OntoShip)",
                                "## База знаний (изменено)", 1)
    assert any("verbatim" in error for error in _contract_errors(edited_block))

    no_substitution = text.replace("подставь корень канала установки", "корень канала")
    assert no_substitution != text
    assert any("substitution rule" in error
               for error in _contract_errors(no_substitution))


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


def test_bootstrap_asks_core_role_models_from_active_host_models():
    """spec: docs/plans/review-config.md#готово — вопрос по ролям текущей версии
    ядра, выбор из доступных моделей хоста."""
    text = SKILL.read_text("utf-8")
    for role in CORE_ROLES:
        assert role in text, f"core role {role} is not named"
    assert "ask" in text
    assert "активные модели" in text


def test_critic_model_difference_is_a_recommendation():
    """spec: docs/plans/review-config.md#готово — для critic отличие модели от
    сессионной — рекомендация; совпадение допустимо и называется в отчёте
    (поправка 2026-11-09)."""
    text = SKILL.read_text("utf-8")
    assert "рекомендуется отличной от модели сессии" in text
    assert "назови его в отчёте" in text
    assert "отказом оно не является" in re.sub(r"\s+", " ", text)


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


def test_bootstrap_runs_the_bundled_generator_on_zcode_only():
    """spec: docs/plans/review-config.md#готово, docs/plans/dsh-adaptation.md#решения —
    генератор определений доступен установленному проекту в ZCode-ветке; в
    DSH-ветке он не запускается (определений ролей там нет)."""
    text = SKILL.read_text("utf-8")
    assert GENERATOR_LINE in _branch(text, "### ZCode", "## 6. Проверь")
    assert GENERATOR_LINE not in _branch(text, "### DSH", "### ZCode")


def test_bootstrap_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    bootstrap contract rejects a lost registry, a lost core role, a lost
    warning, a lost gap rule and a lost generator path."""
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

    no_generator = text.replace(GENERATOR_LINE, "gen.py")
    assert no_generator != text
    assert any(GENERATOR_LINE in error for error in _contract_errors(no_generator))


def test_curator_contract_can_fail():
    """invariant: docs/decisions/ontoship-core.md#одно правило качества — the
    curator bootstrap rejects a lost sixth role (in the check list itself, not
    just any mention), a lost active-list guard, a lost deviation rule, a lost
    level rule and a lost level source (onto-doc solution 9 mutations)."""
    text = SKILL.read_text("utf-8")
    assert _contract_errors(text) == []

    no_curator = text.replace("curator", "kurator")
    assert no_curator != text
    assert any("curator" in error for error in _contract_errors(no_curator))

    # The named mutation: the sixth role dropped from the check list itself.
    no_list = text.replace("`critic`, `curator` — с секциями", "`critic` — с секциями")
    assert no_list != text
    assert any("`critic`, `curator` — с секциями конфига" in error
               for error in _contract_errors(no_list))

    # Solution 9's guard: the default is recommended only while it is active.
    no_guard = text.replace(" пока она в списке активных", "")
    assert no_guard != text
    assert any("пока она в списке активных" in error for error in _contract_errors(no_guard))

    no_deviation = text.replace("и назови отклонение от дефолта.", "")
    assert no_deviation != text
    assert any("назови отклонение от дефолта" in error for error in _contract_errors(no_deviation))

    no_level = text.replace("максимум из доступных уровней выбранной модели",
                            "заданный конфигом уровень")
    assert no_level != text
    assert any("максимум из доступных уровней выбранной модели" in error
               for error in _contract_errors(no_level))

    no_source = text.replace("тот же список активных моделей шага 1",
                             "отдельный каталог уровней")
    assert no_source != text
    assert any("тот же список активных моделей шага 1" in error
               for error in _contract_errors(no_source))

    no_omit = text.replace("У модели без уровней ключ `level` опусти.", "")
    assert no_omit != text
    assert any("У модели без уровней ключ `level` опусти" in error
               for error in _contract_errors(no_omit))


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

    counted_question = text.replace("Отдельный вопрос — модель роли `curator`",
                                    "Шестой вопрос — модель роли `curator`")
    assert counted_question != text
    assert any("шестой вопрос" in error
               for error in _contract_errors(counted_question))

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

    next_ordinal = text.replace("Отдельный вопрос — модель роли `curator`",
                                "Седьмой вопрос — модель роли `curator`")
    assert next_ordinal != text
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


def test_repo_managed_block_matches_the_installer_substitution():
    """invariant: docs/plans/harness-agnostic.md#готово (п. 6, с припиской
    2026-11-02), docs/plans/dsh-adaptation.md#готово (2) — собственный блок
    репозитория равен DSH-шаблону init после подстановки `.agents/skills`;
    прогон init из другой копии бандла перепишет блок — ожидаемое поведение,
    не дефект."""
    import re as _re

    agents = (REPO / "AGENTS.md").read_text("utf-8")
    match = _re.search(
        rf"{_re.escape(BEGIN)}\n(.*?){_re.escape(END)}", agents, _re.DOTALL)
    assert match, "the managed block is missing from AGENTS.md"
    expected = BLOCK_DSH.replace("<навыковый корень>", ".agents/skills")
    inner = match.group(1)
    assert inner.strip("\n") == expected.replace(f"{BEGIN}\n", "").replace(
        f"\n{END}", "").strip("\n")
