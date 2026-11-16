# Проверки критериев (worktree ctb05-spec-move, база 9fc1c21; team 03969fa + правки панели)

База нарезки тикета — `88c8825` (историческая); исполнение и красные
пробы — на текущем main `9fc1c21` (база среза), как в предшествующих
тикетах юнита.

## Критерий 1: дерево путей + сохранность содержания

Команды: `ls <пути>` в обоих репо; `sha256sum`; `git show 9fc1c21:<путь> | sha256sum`.

```
-- ядро (ожидание: файлов нет):
ls: docs/plans/team-profiles.md: Нет такого файла или каталога
ls: tickets/team-profiles/07-live-proof.md: Нет такого файла или каталога
ls: tickets/team-profiles/08-suite-kb-08-protocol.md: Нет такого файла или каталога
-- team (ожидание: файлы есть):
ontoship-team/docs/plans/team-profiles.md
ontoship-team/docs/plans/README.md
ontoship-team/tickets/README.md
ontoship-team/tickets/team-profiles/07-live-proof.md
ontoship-team/tickets/team-profiles/08-suite-kb-08-protocol.md
ontoship-team/tickets/team-profiles/dag.md
ontoship-team/tickets/team-profiles/kanban.md
-- sha256 тикетов (база ядра → team), побайтово:
07: e992dc4c8e9e3545f28db17c4da285473fb4bcb012f48ac91af606f1e684f71d (совпал)
08: 60649c0860936bc8a7ce0c7a3d75f6e7f2cbe705c2a5f2113063e3ad911480b8 (совпал)
```

Спека (diff базы ядра против team-копии — spec-link-form.diff):
изменена только форма ссылок и метаданные правки — frontmatter
`relates_to` (6 носителей ядра) снят, информация перенесена в проза-абзац
«Связанные носители ядра (адреса-проза)» (те же 6 путей); 5 inline-линков
(3× гейт проекций, roles.py, config.toml) → проза «носитель:
ontoship-ntin/<путь>»; 3 bare-пути ядра (`.agents/config.toml` ×2,
трекер) префиксованы адресами-проза (правки панели, форма решения 8);
`updated` поднят 2026-11-16 → 2026-11-17 (метаданные правки формы);
финальный newline добавлен (в базе отсутствовал). Нормативное
содержание — решения 1–24, триаж, уточнения нарезки, «Готово» 1–12,
«Рамки», «Ограничения», «Контекст» — без правок. Тикет 08 без финального
newline — в базе его нет, побайтовость сохранена (sha256), не правился.
Линк тикетов 07/08 на спеку `../../docs/plans/team-profiles.md`
резолвится внутри team.

## Критерий 2: висящие ссылки ядра на перенесённое = 0; lint --strict чист

Команды (скоуп: docs/ tickets/ skills/ tests/, *.md и *.py, без 05-evidence):

```sh
grep -rn "](.*plans/team-profiles\.md\|](.*team-profiles/07-live-proof\|](.*team-profiles/08-suite" \
  docs/ tickets/ skills/ tests/ --include="*.md" --include="*.py" | grep -v 05-evidence
# вывод: пусто (0)
grep -rn "relates_to:.*team-profiles\.md\|part_of:.*team-profiles\.md" docs/
# вывод: пусто (0)
python3 skills/kb-search/gitmark.py lint --strict   # лог: lint.log
# ✓ чисто (57 файлов · —), exit 0
```

Носители правок: docs/plans/README.md (стаб + frontmatter),
docs/plans/core-team-boundaries.md (frontmatter relates_to),
docs/plans/standards-autoship.md (2 приписки решения 14),
docs/ops/continue.md (2 линка + абзац юнита «Порядка тикетов» — запись
переноса), tickets/README.md (шапка юнита, строки 07/08, заметка
переноса, статус 07, заморозка sa08), 16 закрытых тикетов/progress
tickets/team-profiles/ (шапка «Спека» → адрес-проза, обёртка ≤80).
В team: docs/reference/dsh-preset-allowlist.md — мёртвый адрес
перенесённой спеки заменён team-локальным (панель kb P2).

## Критерий 3: маркеры на перенесённую спеку = 0; test_traceability зелёный

Команды:

```sh
grep -rn "spec: docs/plans/team-profiles\|invariant: docs/plans/team-profiles" tests/ --include="*.py"
# вывод: пусто (0)
grep -n "spec: docs/decisions/ontoship-core.md#три фазы — решение 23" \
  tests/test_canon_sync.py tests/test_skill_grilling.py
# test_canon_sync.py:548, test_skill_grilling.py:702
grep -n "spec: docs/plans/core-team-boundaries.md#готово — «Готово» 3 (перенос" tests/test_skill_init.py
# test_skill_init.py:1243, 1253
python3 -m pytest tests/test_traceability.py -q   # 2 passed
```

Носители норм: тривиальность (решение 23) — канон «Три фазы» (дословная
оговорка, паритет зеркала); ссылка init на team-бандл —
core-team-boundaries «Готово» 3 и решение 3 (решение 15 team-profiles
инкорпорировано; носитель после переноса — ontoship-team/docs/plans/
team-profiles.md). Отклонение от буквы критерия 3 (назван только
core-team-boundaries) — см. «Разбор расхождений», п. 2.

## Критерий 4: виды dag/kanban

Команды:

```sh
grep -n "T07\|T08\|| 07 \|| 08 " tickets/team-profiles/dag.md tickets/team-profiles/kanban.md
# вывод: пусто (0 строк графа/таблицы; шапки несут запись переноса прозой)
grep -c "T07\|T08" ontoship-team/tickets/team-profiles/dag.md        # 8
grep -n "| 07 \|| 08 " ontoship-team/tickets/team-profiles/kanban.md
# 07 ready (проба остановлена — проза), 08 blocked
```

Записи переноса: абзац юнита «Порядка тикетов» continue.md, leads.md
(шапка), tickets/README.md (заметка), шапки видов ядра и team. Закрытые
тикеты 01–06, 09–14, evidence 01–06/09–14, 00-projection-report.md
остаются в ядре. Агрегация блокеров 07 в видах team названа в шапках
(панель code/spec P3) — см. «Разбор расхождений», п. 5.

## Полный набор и prod-проверка

```
python3 -m pytest -q          # 784 passed (лог: core-suite.log), exit 0
bash scripts/install.sh --check .   # main-чекout: check: ok (10 бандлов)
```

Гейты пака: `.agents/packs/` отсутствует — ноль гейтов.

## Разбор расхождений ожидание/факт (testing.md, «Артефакт доказательства»)

1. **install.sh --check: ожидание `check: ok`, факт — drift 10 бандлов
   в worktree.** Не дефект: selfhost-симлинки `.agents/skills` не
   трекаются git и живут только в main-чекoutе; в worktree каталог пуст,
   установщик честно видит drift. На main `check: ok`; diff среза не
   трогает `skills/` и `scripts/` (git diff --stat пуст по ним).
   Поведение правильное: канал установки не затронут переносом docs.
2. **Маркеры тривиальности: ожидание критерия 3 — перетыкание на
   core-team-boundaries, факт — канон «Три фазы».** Не дефект
   трассировки: носитель нормы тривиальности после переноса — канон
   (дословная оговорка в «Три фазы», паритет зеркала сторожится тестом);
   спека границ норму не несёт, указатель на неё был бы ложным
   маркером. Требование «durable-носитель ядра, test_traceability
   зелёный, маркеров на перенесённый путь 0» выполнено полностью.
   Отклонение от буквы критерия названо; правка формулировки «Готово» 5 —
   только решением оператора, подтверждение отклонения — на приёмке
   (вопрос оператору). Записано в тикете («Расхождения») и leads юнита.
3. **База: ожидание — база нарезки `88c8825` (шапка тикета), факт —
   исполнение и красные пробы на `9fc1c21`.** Не дефект: база нарезки —
   исторический коммит публикации тикетов; ship исполняется от текущего
   main (практика тикетов 01–04 юнита). Красные пробы воспроизведены
   именно на базе среза `9fc1c21` (02-red-base.md).
4. **Сохранность спеки: ожидание «содержание не меняется», факт —
   diff формы ссылок + проза-абзац бывших relates_to + updated +
   префиксы bare-путей + финальный newline.** Не дефект: нормативное
   содержание (решения, Готово, Рамки, Ограничения, Контекст) не
   тронуто; изменения — названное исключение формы ссылок (решение 8,
   триаж S2) и метаданные правки. Абзац «Связанные носители ядра»
   переносит информацию frontmatter в тело (те же 6 путей), новой
   информации не несёт. Формулировка evidence уточнена (панель code P3).
5. **Блокеры 07: ожидание вида «полные блокеры — в шапке тикета»,
   факт — шапка 07 называет 14, виды несут 06, 10–14.** Не дефект
   среза: расхождение унаследовано от видов ядра (агрегация рёбер
   истории нарезки); тикеты перенесены побайтово, шапка не правлена.
   Виды team называют агрегацию в шапках; синхронизация шапки 07 —
   содержательное решение оператора (зацепка в leads юнита).

Иных расхождений ожидание/факт не было.