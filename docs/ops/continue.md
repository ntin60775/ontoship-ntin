---
node_type: runbook
title: Продолжение разработки из этого репозитория
service: _platform
status: active
updated: 2026-10-22
tags: [runbook, start, handoff, core-kb, harness, workflow]
links:
  relates_to: [../README.md, ../decisions/ontoship-core.md, ../plans/core-kb.md, ../plans/harness-agnostic.md, ../plans/workflow-skills.md, ../plans/install-dry-run.md, ../reference/harnesses.md, ../../tickets/README.md]
---

# Продолжение разработки из этого репозитория

Это **канонический старт**. Снимок сессии `.scratch/handoff-current.md` эфемерен;
источник истины — этот runbook и тикеты, а не снимок.

## Где мы

Репозиторий: `/home/prog7/home/dev/contrib/forks/ontoship-ntin` (git). Он
самодостаточен: база движка вендорена, тикеты отслеживаются, три юнита завершены.
Каталог переименован из `ontoship-dsh`; исторические логи в `.scratch/ticket-06/`
сохраняют старое имя.

| коммит | что |
|---|---|
| `cfad6e9` | скелет, канон, источники |
| `31e11fb` | план `core-kb` |
| `f1cd8bf` | поправка о тестировании: target-тесты, ESEM 2026 |
| `030c81a` | план утверждён (`active`), порядок тикетов |
| `b148d1f` | самодостаточный старт: вендорная база, тикеты, этот runbook |
| `eb678d8` | тикет 01: урезанный движок, 131 тест |
| `e5a2ced` | стартовый промпт тикета 02 |
| `4b10f95` | тикет 02: `kb-search` SKILL.md и его контрактный тест |
| `f189889` | docs: тикет 02 закрыт; тикет 03 готов |
| `054279d` | docs(ops): уточнён стартовый промпт тикета 03 |
| `118fe99` | тикет 03: скилл `kb-curate`, модель онтологии, 149 тестов |
| `6c1cce6` | docs(ops): закрыт тикет 03, передача в 04 |
| `90f0846` | тикет 04: скилл `init` и его контрактный тест |
| `dce10f0` | тикет 05: `scripts/install.sh` и его контрактный тест |
| `88fc09a` | тикет 06: dogfood — управляемый блок в `AGENTS.md` |
| `1e9851c` | тикет 06 `workflow-skills`: спека dogfood-прогона `install-dry-run` |
| `82aeb6b` | тикет 06 `workflow-skills`: два тикета игрушечного юнита |
| `10a78bd` | тикет 06 `workflow-skills`: `--dry-run` установщика, 226 passed |

Первый юнит `core-kb` завершён и проверен на dogfood. Второй юнит
`harness-agnostic` закоммичен 2026-10-21 (`0767142`): один project-local корень
`.agents/skills`. Третий юнит `workflow-skills` закрыт 2026-10-22: четыре скилла
фаз с контрактными тестами, установка семи бандлов, сквозной dogfood.
Итог: `skills/kb-search/gitmark.py` (1305 строк), семь скиллов, `scripts/install.sh`,
`tests/` — **226 passed**; `lint --strict` чистый (44 файла); `index` покрывает
44 markdown-файла; `.agents/skills` — семь ссылок, `--check` → 0; `map` и
`stat --json` работают.

Dogfood провёл игрушечный юнит `install-dry-run` через три фазы: спека → два
тикета → один срез до локального merge. Подробности и пробелы — в
[tickets/workflow-skills/06-dogfood.md](../../tickets/workflow-skills/06-dogfood.md).
Спека и код утверждены оператором после отчёта, 2026-10-22; гейт прошёл задним
числом — это записано как процессный дефект прогона. Детализацию семи решений
оператор оценивает отдельно. PR-путь не проверен — remote нет.

Второй юнит проверил Qoder свежими сессиями: все три скилла видны, `kb-search` и
`kb-curate` загружены, поиск вернул канон. DSH и zcode живой каталог не подтвердили:
DSH `headless` падает с `MISSING_CREDENTIAL`, у zcode нет headless-режима. Точные
пробелы — в разделе [Факты окружения](#факты-окружения).

## Что осталось (по проекту)

Три юнита закрыты. Ниже открытые пункты; исполнение — один тикет за прогон.

1. **Тикет 02 `install-dry-run` не начат.** Copy-режим `--dry-run`: сейчас
   `--dry-run --copy` отказывает с кодом 2. Тикет 01 сделан (`10a78bd`).
   [Спека](../plans/install-dry-run.md) — черновик dogfood-прогона.
2. **Детализация решений `install-dry-run` — на оценке оператора.** Семь решений
   записаны в [спеке](../plans/install-dry-run.md); план утверждён задним числом
   2026-10-22. Правка решения идёт новой спекой, не правкой утверждённой.
3. **Живой план-гейт и приёмка тикетов не проводились.** В dogfood-прогоне
   оператор не отвечал на раунд `grilling` и не принимал тикеты отдельными
   вопросами; прогон шёл по рекомендованным умолчаниям. Следующий реальный юнит
   должен пройти эти гейты вживую.
4. **PR-путь не проверен.** `git remote -v` пуст, CI нет; merge в dogfood был
   локальным fast-forward. Если определение готовности требует PR, remote —
   решение оператора.
5. **DSH и zcode не показали живой каталог скиллов.** Пробелы окружения, не
   проекта; подробности ниже.

**Замечание о проверке каталога.** Qoder 0.4.8 проверен свежей сессией 2026-10-21:
инструмент `Skill` загрузил `kb-search`, скилл вернул ожидаемую строку, а
`gitmark.py search "canon"` — `docs/decisions/ontoship-core.md`. DSH и zcode живой
каталог не показали; пробелы зафиксированы ниже и не подменяются файловой
раскладкой. В сессии dogfood 2026-10-22 хост видел `grilling`, `ship` и `testing`
как доступные скиллы, а `to-tickets` скрыл маркером
`disable-model-invocation: true` — как задумано.

## Что где лежит

- `AGENTS.md` — точка входа; несёт управляемый блок ontoship (тикет 06), который
  указывает на установленный движок и команды сопровождения.
- `docs/decisions/ontoship-core.md` — канон (3 артефакта, 3 фазы, 2 разделения,
  1 правило качества; спека durable / тикеты эфемерны).
- `docs/reference/testing.md` — spec-, инвариантные и target-тесты, планка качества,
  агентный цикл.
- `docs/reference/sources.md` — OntoShip (vakovalskii), Pocock, ESEM 2026;
  поправка про 53 %.
- `docs/reference/harnesses.md` — матрица zcode 3.16.2, DSH и Qoder 0.4.8: корни
  `.agents/skills`, ранги, `AGENTS.md`, источники и запасные варианты.
- `docs/plans/core-kb.md` — утверждённая, завершённая спека первого юнита
  (тикеты 01–06).
- `docs/plans/harness-agnostic.md` — утверждённая, завершённая спека второго юнита
  (тикеты 01–04): один project-local корень `.agents/skills`.
- `docs/plans/workflow-skills.md` — завершённая спека третьего юнита (тикеты 01–06):
  четыре скилла фаз, `grilling`, `to-tickets`, `ship`, `testing`.
- `docs/plans/install-dry-run.md` — игрушечная спека dogfood-прогона: режим
  `--dry-run` установщика. Утверждена задним числом 2026-10-22; детализация
  решений — на оценке оператора.
- `docs/ontology.md` — копия онтологии этого репозитория и единственный словарь типов
  для I2; I8 сравнивает её тело с первого заголовка `## ` с
  `skills/kb-curate/ontology.md`.
- `tickets/core-kb/01…06.md` — тикеты исполнения (локальный трекер, не KB); все шесть
  сделаны, юнит закрыт.
- `tickets/harness-agnostic/01…04.md` — тикеты второго юнита; все четыре сделаны,
  юнит закрыт.
- `tickets/workflow-skills/01…06.md` — тикеты третьего юнита; все шесть сделаны,
  юнит закрыт. 06 хранит отчёт dogfood-прогона и его пробелы.
- `tickets/install-dry-run/01…02.md` — игрушечный юнит прогона: 01 сделан и влит,
  02 (copy-режим) открыт.
- `vendor/ontoship-zcode/` — база движка (MIT) и её базовые тесты; тикет 01 копирует
  и урезает её в `skills/kb-search/`.
- `skills/kb-search/` — урезанный движок (тикет 01) и пользовательский `SKILL.md`
  (тикет 02): `index`, `search`, `lint`, `map`, `stat`, `version`; без
  `inventory`/`serve`/I7. CLI не зависит от харнесса (только stdlib); не индексирует
  `.agents`, а `.dsh` и `.zcode` остаются legacy-исключениями.
- `skills/kb-curate/` — поставляемая модель онтологии `ontology.md` и
  курирующий `SKILL.md` (тикет 03): CREATE / UPDATE / DEPRECATE / LINK / REINDEX;
  I7 остаётся вне ядра.
- `skills/init/` — `SKILL.md` скилла `init` (тикет 04): управляемый блок
  (`<!-- BEGIN ontoship -->` … `<!-- END ontoship -->`), его пять случаев маркеров и
  четыре строки `.gitignore`. Идемпотентен; пишет только `AGENTS.md` и `.gitignore`.
- `skills/grilling/` — скилл фазы 1 (тикет 01 `workflow-skills`): интервью по
  фронтиру, нумерованные вопросы с рекомендованным ответом, выход в спеку
  `docs/plans/<slug>.md` на план-гейт; автономный флаг вне рамок v1.
- `skills/to-tickets/` — скилл фазы 2 (тикет 02 `workflow-skills`): tracer-bullet
  срезы, демо-путь, критерии на базовом коммите, `disable-model-invocation: true`;
  публикация в `.scratch/<slug>/issues/` или трекер.
- `skills/ship/` — скилл фазы 3 (тикет 03 `workflow-skills`): один проход
  worktree → реализация → доказательные тесты → один прогон ревью → проверки
  dev/prod → merge; точки остановки из «Ограничений» спеки; ревью даёт зацепки;
  без remote — локальный коммит и названный пробел.
- `skills/testing/` — скилл правила качества (тикет 04 `workflow-skills`):
  три класса теста (spec, инвариант, target), трассируемость
  `spec:` / `invariant:` / `target:`, независимый источник ожидаемого
  значения, планка target-теста, агентный цикл из семи шагов, каналы —
  инструменты; модельный — запрета вызова нет, недоступны модели только
  `to-tickets` и `ship`.
- `scripts/install.sh` — project-local установка (тикет 01 второго юнита; тикет 05
  `workflow-skills` расширил её до семи бандлов; тикет 06 добавил `--dry-run`):
  по умолчанию ссылки, `--copy` — отсоединённая копия, `--check` — расхождение
  (код 0/1, называет каждый скилл) и предупреждение о legacy-корнях, `--dry-run` —
  план `would create` / `would link` / `would leave … unchanged` без записи и с тем
  же preflight (код 1 на занятом пути); идемпотентна; пишет только
  `<project>/.agents/skills`; init не запускает. `--dry-run --copy` пока код 2.
- `tests/` — тесты движка, контрактов скиллов, установки и сторож трассировки;
  запуск `python3 -m pytest tests/ -q` (226 passed; stdlib + pytest, без Node).
- `.agents/skills/` — project-local установка под gitignore: тикет 04 проверил
  три ссылки (`kb-search`, `kb-curate`, `init`), тикет 05 добавил четыре
  (`grilling`, `to-tickets`, `ship`, `testing`); `scripts/install.sh --check
  "$PWD"` выходит с кодом 0. `.dsh` удалён.
- `.scratch/handoff-current.md` — снимок предыдущей сессии (эфемерный).

## Порядок тикетов

`core-kb`: **01 движок → 02 kb-search → 03 kb-curate/ontology → 04 init →
05 install → 06 dogfood.** Все шесть сделаны; юнит закрыт.

`harness-agnostic`: **01 корень установки → 02 переносимые скиллы/init →
03 справочник харнессов → 04 dogfood на трёх.** Все четыре сделаны; юнит закрыт.

`workflow-skills`: **01 grilling → 02 to-tickets → 03 ship → 04 testing →
05 install → 06 dogfood.** Все шесть сделаны; юнит закрыт 2026-10-22.

`install-dry-run` (игрушечный юнит dogfood): **01 link-режим → 02 copy-режим.**
01 сделан; 02 открыт. Открытая работа — в разделе
[Что осталось (по проекту)](#что-осталось-по-проекту).

## Факты окружения

- DSH запускается из `/home/prog7/home/dev/contrib/forks/deepseek-harness` под Node
  `/home/prog7/.local/share/node-lts/bin/node`. На 2026-10-21 веб-сервер не запущен:
  PID в `/run/user/1000/dsh-web.pid` устарел, порт не слушается, лог
  `/run/user/1000/dsh-web.log` оканчивается сетевыми ошибками. `dsh headless`
  завершается до сессии с `MISSING_CREDENTIAL: llm-deepseek: no API key`;
  `DEEPSEEK_API_KEY` не выставлен. **Живой каталог DSH не проверен** — это пробел
  окружения, а не проекта.
- Корни скиллов DSH: `<project>/.dsh/skills` (ранг 100),
  `<project>/.agents/skills` (200), `~/.dsh/skills` (400). Скилл — это
  `<name>/SKILL.md` или плоский `<name>.md`; вложенный `**/SKILL.md` не
  обнаруживается. Символическая ссылка на каталог проверяется через stat и
  разыменовывается, поэтому установка может ссылаться на бандл. В этом репозитории
  `.dsh` удалён; `.agents` имеет ранг ниже и найден без него.
- **Qoder 0.4.8 (проверено 2026-10-21):** две свежие сессии. Первая загрузила
  `kb-search` через инструмент `Skill`, и поиск вернул
  `docs/decisions/ontoship-core.md`; вторая перечислила все три project-local скилла
  (`kb-search`, `kb-curate`, `init`) и загрузила `kb-curate` из
  `.agents/skills/kb-curate`. Загрузка идёт из project-local `.agents/skills` при
  `skills.loadFromAgentsDirectory: true`.
- **zcode 3.16.2 (частично проверено):** сканирует workspace `.zcode/skills` и
  `.agents/skills` (`app.asar`, `resolveAncestorWorkspaceRoots`). Headless-режима нет:
  `zcode --help` поднимает GUI и не печатает справку. **Живой каталог workspace не
  проверен**; файловая раскладка `.agents/skills` на месте.
- Матрица и источники: [docs/reference/harnesses.md](../reference/harnesses.md).
- **Playwright MCP:** настроен в `~/.dsh/profiles/web/cordis.patch.yml` (резервная
  копия `cordis.patch.yml.bak-20261019`): `@deepseek-ai/dsh-browser-use` +
  `@deepseek-ai/dsh-experimental-browser-use-playwright-mcp` (`mode: launch`,
  `headless: true`, `executablePath: /usr/bin/chromium`). Пока DSH не запущен, патч не
  действует. Если запускать — (`~/.local/bin/dsh-web`), новые сессии получат
  `mcp__playwright-mcp__*`. Тикетам 01–04 браузер не понадобился; если его нет, не
  подделывай E2E.
- Python 3.13, для движка только stdlib; `pytest` доступен. `node/npm/npx` нет в
  PATH; движок не должен требовать Node.

## Стартовый промпт

```text
Мы продолжаем работу в /home/prog7/home/dev/contrib/forks/ontoship-ntin — OntoShip-core.
Юниты core-kb (тикеты 01–06), harness-agnostic (01–04) и workflow-skills (01–06)
завершены. Итог: семь скиллов, установка в .agents/skills (--check → 0), 226 passed,
lint --strict чистый (44 файла). Dogfood-прогон 06 провёл игрушечный юнит
install-dry-run: тикет 01 влит (10a78bd), тикет 02 (copy-режим) открыт, спека
docs/plans/install-dry-run.md утверждена задним числом 2026-10-22.

Прочитай по порядку: AGENTS.md, docs/ops/continue.md,
docs/decisions/ontoship-core.md, docs/reference/harnesses.md,
docs/reference/testing.md, docs/reference/sources.md,
docs/plans/workflow-skills.md, docs/plans/install-dry-run.md, tickets/README.md,
tickets/workflow-skills/06-dogfood.md.

Открыто: оценка оператором детализации семи решений install-dry-run и тикет 02.
PR-путь не проверен: remote нет. Живой план-гейт и приёмку тикетов повторить на
следующем реальном юните.

Если оператор просит проверить состояние: scripts/install.sh --check "$PWD" → 0;
scripts/install.sh --dry-run "$PWD" → семь would leave … unchanged, диск не меняется;
python3 .agents/skills/kb-search/gitmark.py index; lint --strict → 0;
search "canon" → docs/decisions/ontoship-core.md; search "target test" →
docs/reference/testing.md в топ-3 (первым идёт tickets/workflow-skills/04-testing.md —
так было и на базовом коммите); stat --json валиден; map пишет docs-map.html.
.agents/skills/, .gitmark/, .scratch/ и *-map.html не коммитятся.

В конце отчёт фактами: что сделано, чем доказано, что осталось. Один тикет за прогон;
при реальном конфликте останови и спроси оператора.
```

## Правила продолжения

- Один тикет за прогон; не пакетируй. Исследуй до того, как писать.
- Перед предложением нарезки агент сам оценивает сложность плана; если резать
  нужно, нарезка идёт в ask-инструмент, ровно один вопрос на тикет: выдержка про
  тикет и варианты действий по нему (канон, «Три фазы»).
- Доказательство: тест, который доказывает пункт спеки, охраняет инвариант или
  воспроизводит реальный сбой; новая матрица получает негативную или мутационную
  пробу; читай лог прогона.
- Никаких реестров, inventory, строки provenance, Reel, аккорда приёмки, счётчика
  issue и автоматической цепочки grill → tickets.
- Не копируй `docs/` из `ontoship-zcode`; это строгий профиль и история.
- Обновляй этот runbook новым состоянием в конце прогона; держи его коротким.
