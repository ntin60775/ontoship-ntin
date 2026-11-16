# Проверки критериев (worktree ctb05-spec-move, база 9fc1c21; team 03969fa)

## Критерий 1: дерево путей + сохранность содержания
```
-- ядро (ожидание: файлов нет):
ls: невозможно получить доступ к 'docs/plans/team-profiles.md': Нет такого файла или каталога
ls: невозможно получить доступ к 'tickets/team-profiles/07-live-proof.md': Нет такого файла или каталога
ls: невозможно получить доступ к 'tickets/team-profiles/08-suite-kb-08-protocol.md': Нет такого файла или каталога
-- team (ожидание: файлы есть):
/home/prog7/home/dev/contrib/forks/ontoship-team/docs/plans/README.md
/home/prog7/home/dev/contrib/forks/ontoship-team/docs/plans/team-profiles.md
/home/prog7/home/dev/contrib/forks/ontoship-team/tickets/README.md
/home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/07-live-proof.md
/home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/08-suite-kb-08-protocol.md
/home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/dag.md
/home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/kanban.md
-- sha256 тикетов 07/08 (база ядра → team):
e992dc4c8e9e3545f28db17c4da285473fb4bcb012f48ac91af606f1e684f71d  -
e992dc4c8e9e3545f28db17c4da285473fb4bcb012f48ac91af606f1e684f71d  /home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/07-live-proof.md
60649c0860936bc8a7ce0c7a3d75f6e7f2cbe705c2a5f2113063e3ad911480b8  -
60649c0860936bc8a7ce0c7a3d75f6e7f2cbe705c2a5f2113063e3ad911480b8  /home/prog7/home/dev/contrib/forks/ontoship-team/tickets/team-profiles/08-suite-kb-08-protocol.md
```
Спека: diff содержания — только форма ссылок (spec-link-form.diff):
frontmatter relates_to (6 носителей ядра) → адреса-проза в теле; 5 inline-линков
(3× гейт проекций, roles.py, config.toml) → проза «носитель: ontoship-ntin/<путь>».
Решения 1–24, триаж, уточнения нарезки, Готово 1–12, Рамки, Ограничения, Контекст — без правок.
Тикеты 07/08 перенесены побайтово (sha256 совпали); их линк на спеку
../../docs/plans/team-profiles.md резолвится внутри team.

## Критерий 2: висящие ссылки ядра на перенесённое = 0; lint --strict чист
```
-- markdown-линки на перенесённые пути (docs, tickets, skills, tests; *.md, *.py):
0
-- frontmatter-ссылки на team-profiles.md:
0
-- lint --strict (лог: lint.log):
scope: 135 файлов исключено по 1 префиксам
✓ чисто  (57 файлов · —)
```
Носители правок: docs/plans/README.md (стаб + frontmatter),
docs/plans/core-team-boundaries.md (frontmatter relates_to),
docs/plans/standards-autoship.md (2 приписки решения 14),
docs/ops/continue.md (2 линка + абзац юнита «Порядка тикетов» — запись переноса),
tickets/README.md (шапка юнита, строки 07/08, заметка переноса, заморозка sa08),
16 закрытых тикетов/progress tickets/team-profiles/ (шапка «Спека» → адрес-проза).

## Критерий 3: маркеры на перенесённую спеку = 0; test_traceability зелёный
```
0
-- перетыкание (4 маркера):
tests/test_canon_sync.py:548:    """spec: docs/decisions/ontoship-core.md#три фазы — решение 23 (team-profiles 14;
tests/test_skill_grilling.py:702:    """spec: docs/decisions/ontoship-core.md#три фазы — решение 23 (team-profiles 14;
1243:    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3 (перенос
1253:    """spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3 (перенос
-- pytest tests/test_traceability.py:
2 passed in 0.03s
```
Носители норм: тривиальность (решение 23) — канон «Три фазы» (дословная оговорка,
паритет зеркала); ссылка init на team-бандл — core-team-boundaries «Готово» 3
(решение 15 team-profiles инкорпорировано). Маркеры тестов тривиальности перетыкнуты
на канон, не на core-team-boundaries: спека границ норму тривиальности не несёт —
тривиальное решение агента (обратимо, малое влияние, требование «durable-носитель»
полностью соблюдено), названо в отчёте.

## Критерий 4: виды dag/kanban
```
-- ядро: строки графа/таблицы 07/08:
0
-- team: 07/08 в графе и таблице:
8
23:| 07 | живая проба на fin-agent (universal) | 06, 10, 11, 12, 13, 14 | — | ready | да |
24:| 08 | набор, KB и протокол 08 | 07 | 07 | blocked | нет |
```
Записи переноса: абзац юнита «Порядка тикетов» continue.md, leads.md (шапка),
tickets/README.md (заметка), шапки видов ядра и team. Закрытые тикеты 01–06,
09–14, evidence 01–06/09–14, 00-projection-report.md остаются в ядре.

## Полный набор и prod-проверка
```
-- pytest -q (лог: core-suite.log):
784 passed in 10.96s
-- install.sh --check (main-чекout, selfhost-симлинки; worktree drift — артефакт
   отсутствия нетрекаемых симлинков .agents/skills, diff не трогает skills/ и scripts/):
check: ok
```
