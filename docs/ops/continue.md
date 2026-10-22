---
node_type: runbook
title: Продолжение разработки из этого репозитория
service: _platform
status: active
updated: 2026-10-22
tags: [runbook, start, handoff, core-kb, harness]
links:
  relates_to: [../README.md, ../decisions/ontoship-core.md, ../plans/core-kb.md, ../plans/harness-agnostic.md, ../plans/workflow-skills.md, ../reference/harnesses.md, ../../tickets/README.md]
---

# Продолжение разработки из этого репозитория

Это **канонический старт**. Снимок сессии `.scratch/handoff-current.md` эфемерен;
источник истины — этот runbook и тикеты, а не снимок.

## Где мы

Репозиторий: `/home/prog7/home/dev/contrib/forks/ontoship-ntin` (git). Он
самодостаточен: база движка вендорена, тикеты отслеживаются, первые два юнита
завершены.
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

Тикеты 01–06 **реализованы и закоммичены**; первый юнит `core-kb` завершён и проверен
на dogfood. Второй юнит `harness-agnostic` (тикеты 01–04) **закоммичен 2026-10-21**
(`0767142`). Итог: `skills/kb-search/gitmark.py`
(1305 строк), три скилла, `scripts/install.sh` и `tests/` (тогда 168 passed);
`lint --strict` чистый. `AGENTS.md` этого репозитория несёт управляемый блок на
1046 байт, `.agents/skills` содержит три ссылки с `--check` 0, а `.dsh` удалён.
`index` покрывает 30 markdown-файлов; `search "canon"` и `search "target test"`
возвращают ожидаемые документы; `map` и `stat --json` работают. На тот момент
следующего тикета не было.

Оператор выбрал третий юнит — workflow-скиллы (`grilling`, `to-tickets`, `ship`,
`testing`). Спека
[docs/plans/workflow-skills.md](../plans/workflow-skills.md) утверждена на
план-гейте 2026-10-21; нарезка прошла по правилу канона: агент оценил план и
вынес нарезку ask-инструментом, один вопрос на тикет. Правило нарезки и передачи
решений зафиксировано в каноне (`5f483eb`, `2b9be95`). Тикет 01 (`grilling`)
сделан: `skills/grilling/SKILL.md` + 12 контрактных проверок, **180 passed**
(`0c8a862`); `lint --strict` чистый (38 файлов). Тикет 02 (`to-tickets`) сделан
тем же порядком: скилл с `disable-model-invocation: true` и 11 контрактных
проверок, **191 passed** (`ccb7dc0`). Тикет 03 (`ship`) сделан тем же порядком:
скилл с `disable-model-invocation: true` и 11 контрактных проверок, **202
passed** (`45a0584`); `lint --strict` чистый (40 файлов). Тикет 04 (`testing`)
сделан тем же порядком: модельный скилл — носитель правила качества — и 15
контрактных проверок, **217 passed** (`de3b34d`); `lint --strict` чистый
(41 файл). Следующий — тикет 05.

Второй юнит проверил Qoder свежими сессиями: все три скилла видны, `kb-search` и
`kb-curate` загружены, поиск вернул канон. DSH и zcode живой каталог не подтвердили:
DSH `headless` падает с `MISSING_CREDENTIAL`, у zcode нет headless-режима. Точные
пробелы — в разделе [Факты окружения](#факты-окружения).

## Что осталось (по проекту)

Юниты core-kb и harness-agnostic закрыты, третий юнит workflow-skills идёт. Ниже
открытые пункты в порядке зависимостей; исполнение — один тикет за прогон.

1. **Workflow-скиллы — все четыре сделаны.** `grilling` (интервью → спека),
   `to-tickets` (tracer-bullet), `ship` (однопроходная поставка) и `testing`
   (spec-, инвариантные и target-тесты) существуют как скиллы с контрактными
   тестами. [README](../../README.md) называет все четыре; канон описывает три
   фазы.
2. **Механика ship — скиллы есть, установки нет.** Проход ship определяют канон
   и скиллы `ship` и `testing`; канал установки расширит тикет 05. План-гейт
   пройден 2026-10-21: [workflow-skills.md](../plans/workflow-skills.md)
   утверждён.
3. **Тикеты 05–06 не начаты.** Нарезка сделана 2026-10-21
   ([tickets/workflow-skills/](../../tickets/workflow-skills/01-grilling.md));
   тикеты 01–04 закрыты. Один тикет за прогон.
4. **Определение готовности не показано.** Ни один сквозной прогон не провёл тикет
   из свежей сессии через план → тикеты → ship → `main`. У репозитория нет remote и
   CI (`git remote -v` пуст), поэтому путь PR/merge не проверен; если DoD требует
   PR, remote — решение оператора.

**Замечание о проверке каталога.** Qoder 0.4.8 проверен свежей сессией 2026-10-21:
инструмент `Skill` загрузил `kb-search`, скилл вернул ожидаемую строку, а
`gitmark.py search "canon"` — `docs/decisions/ontoship-core.md`. DSH и zcode живой
каталог не показали; пробелы зафиксированы ниже и не подменяются файловой
раскладкой.

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
- `docs/ontology.md` — копия онтологии этого репозитория и единственный словарь типов
  для I2; I8 сравнивает её тело с первого заголовка `## ` с
  `skills/kb-curate/ontology.md`.
- `tickets/core-kb/01…06.md` — тикеты исполнения (локальный трекер, не KB); все шесть
  сделаны, юнит закрыт.
- `tickets/harness-agnostic/01…04.md` — тикеты второго юнита; все четыре сделаны,
  юнит закрыт.
- `tickets/workflow-skills/01…06.md` — тикеты третьего юнита; 01–04 сделаны,
  05–06 не начаты.
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
- `scripts/install.sh` — project-local установка (тикет 01 второго юнита): по
  умолчанию ссылки, `--copy` — отсоединённая копия, `--check` — расхождение (код 0/1,
  называет каждый скилл) и предупреждение о legacy-корнях; идемпотентна; пишет только
  `<project>/.agents/skills`; init не запускает.
- `tests/` — тесты движка, контрактов скиллов и установки; запуск
  `python3 -m pytest tests/ -q` (217 passed; stdlib + pytest, без Node).
- `.agents/skills/` — project-local установка под gitignore, проверенная dogfood в
  тикете 04: три ссылки (`kb-search`, `kb-curate`, `init`),
  `scripts/install.sh --check "$PWD"` выходит с кодом 0. `.dsh` удалён.
- `.scratch/handoff-current.md` — снимок предыдущей сессии (эфемерный).

## Порядок тикетов

`core-kb`: **01 движок → 02 kb-search → 03 kb-curate/ontology → 04 init →
05 install → 06 dogfood.** Все шесть сделаны; юнит закрыт.

`harness-agnostic`: **01 корень установки → 02 переносимые скиллы/init →
03 справочник харнессов → 04 dogfood на трёх.** Все четыре сделаны; юнит закрыт.

`workflow-skills`: **01 grilling → 02 to-tickets → 03 ship → 04 testing →
05 install → 06 dogfood.** 01–04 сделаны; 05 открыт, 06 — после 05.
Спека утверждена, нарезка готова — не переоткрывай её. Открытая работа —
в разделе [Что осталось (по проекту)](#что-осталось-по-проекту).

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
Юниты core-kb (тикеты 01–06) и harness-agnostic (тикеты 01–04) завершены. Третий
юнит workflow-skills: спека docs/plans/workflow-skills.md утверждена, тикеты
01–04 сделаны (grilling, to-tickets, ship, testing; 217 passed, lint --strict
чистый, 41 файл). Установка пока ставит три скилла — канал расширит тикет 05.

Прочитай по порядку: AGENTS.md, docs/ops/continue.md,
docs/decisions/ontoship-core.md, docs/reference/harnesses.md,
docs/reference/testing.md, docs/reference/sources.md, docs/plans/core-kb.md,
docs/plans/harness-agnostic.md, tickets/README.md,
tickets/harness-agnostic/04-dogfood.md.

Следующий тикет — 05 (install): семь скиллов в <project>/.agents/skills —
kb-search, kb-curate, init, grilling, to-tickets, ship, testing; --check
называет каждый; идемпотентность, --copy и предупреждения о legacy-корнях
сохраняются; tests/test_install.py обновлён. Читай спеку
docs/plans/workflow-skills.md и tickets/workflow-skills/05-install.md. Канон
не переоткрывай; нарезка утверждена.

Если оператор просит проверить состояние: scripts/install.sh --check "$PWD" → 0;
python3 .agents/skills/kb-search/gitmark.py index; lint --strict → 0;
search "canon" → docs/decisions/ontoship-core.md; search "target test" →
docs/reference/testing.md; stat --json валиден; map пишет docs-map.html (игнорируется).
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
