# 01: Каркас team-бандла и пресет architect

**Спека:** [team-profiles](../../docs/plans/team-profiles.md), «Готово» 1, 7.

**Блокируется:** —

**Что построить:** отдельный репозиторий `ontoship-team`: `package.json`
(`dsh.bundle.patch`, `engines.dsh`), сборка, тестовый контур. Пресет
`architect`: русская персона, набор инструментов (read, web, ask, skills,
fs-write для спек), `modelSelection: true` на spawn-инструменте.
**Авто-имя:** каждый агент с заданной ролью автоматически получает имя
при старте сессии (для корневых — нативный session-title/персона;
механизм называется в тикете). Установка `link:`-бандлом в профиль.

**Демо-путь:** новая сессия с пресетом `architect` показывает персону,
инструменты с ask и авто-имя роли.

**Критерии приёмки:**

- [x] Каркас репо — артефакт: `package.json` (`dsh.bundle.patch`,
      `engines.dsh`), вывод сборки; ожидание: бандл ставится
      `plugin_manager` link, композиция монтируется; на базе репо нет.
- [x] Композиция architect — артефакт: вывод контрактного теста
      (набор инструментов: ask_user_question, read, web, skills,
      fs-write; modelSelection); ожидание: «Готово» 1; на базе пресета
      нет.
- [x] Авто-имя роли — артефакт: имя агента/сессии при старте отражает
      роль; ожидание: каждый ролевой агент именован автоматически;
      на базе механизма нет.
- [x] Live-smoke — артефакт: id новой сессии с пресетом architect,
      наблюдаемые персона/инструменты/ask; ожидание: сессия архитектора
      работает; на базе пресета нет.

## Доказательства

Срез — отдельный репозиторий (спека, решение 3):
`/home/prog7/home/dev/contrib/forks/ontoship-team`, ветка `main`,
коммит `d69105c` (12 файлов, 3576 строк). Worktree
`ontoship-ntin-wt-tp01` (ветка `tp01-team-bundle-architect`, база
`8cb6b20`) несёт только запись доказательств этого тикета; код юнита
живёт в новом репозитории. Вывод сборки, набор и логи:
`/tmp/tp01-evidence/{build-test.log,test-verbose.log}`.

**Каркас (критерий 1).** `package.json`: `ontoship-team@0.1.0`,
`dsh.bundle.patch` → `./cordis.patch.yml`, `engines.dsh`
`>=0.2.2-rc.2 <0.3.0`; `main`/`types` — в `lib`, сборка `tsc`,
`lib` в `.gitignore` (как у `dsh-1c-contour`), тестовый контур `vitest`.
`npm run typecheck` и `npm run build` — чисто; `npm test` — **30
passed** (3 файла). Диапазон `engines.dsh` проверен тем же вызовом, что
у DSH (`semver.satisfies(..., { includePrerelease: true })`):
`0.2.2-rc.2` admitted, `0.2.2-rc.1` и `0.3.0` отсечены.

**Композиция (критерий 2).** `cordis.patch.yml`: строка
`preset-architect` (`@deepseek-ai/dsh-agent-preset`, `id: architect`,
имя «Архитектор», `order: 20`, описание) — копия `standard` из
`@deepseek-ai/dsh-web-app` без группы `planning` и строк
`workflow-ptc`/`tool-workflow`. Контрактный тест
`tests/unit/composition.spec.ts` (11 tests): матрица инструментов из
строк композиции по каталогу DSH 0.2.2-rc.2 — `ask_user_question`,
`read`, `read_image`, `write`, `edit`, `glob`, `grep`, `web_search`,
`web_fetch`, `skill`, `subagent`/`subagent_fork`; `modelSelection` и
`modelDiscovery` на spawn; отсутствие план-мода и workflow; негативные
пробы (удаление строк ask/subagent, добавление plan-mode); русская
персона с секциями и единственной переменной `{{model}}`. Живой набор
инструментов сессии (ниже) совпал с матрицей.

**Авто-имя (критерий 3).** Хост-плагин `ontoship-team` — корневой
экспорт бандла, строка ДО декларации пресета. Подписан на
`agent/created` (основной путь: свежая сессия с пресетом не пишет
`agent-preset/selected`, пресет лежит в заголовке) и
`agent-preset/selected` (выбор в пустой сессии); имя —
`sessionTitle.rename` в `name` декларации пресета (источник `user` —
заголовок закреплён); детей не переименовывает: имя ребёнка задаёт
нативный аргумент `name` спавна. Тесты `tests/unit/naming.spec.ts`
(16): корень именуется; ребёнок, чужая роль и закреплённый заголовок —
нет; отказ реестра пресетов даёт id пресета; отказ `rename` не валит
создание агента; пустой/кривой конфиг ролей громко выключает авто-имя.

**Live-smoke (критерий 4).** Dev-канал `link:`:
`plugin_manager install_bundle` с target — каталог клона; профиль
`~/.dsh/profiles/web`. Состояние до/после — sha256
`/tmp/tp01-profile-before.sha256` / `/tmp/tp01-profile-after.sha256`;
`package.json` профиля получил зависимость
`"ontoship-team": "link:/home/prog7/home/dev/contrib/forks/ontoship-team"`
и бандл в `dsh.profile.bundles`; `cordis.patch.yml` профиля не тронут
(sha совпал). Строки профиля: `include:ontoship-team` — `active`,
`include:preset-architect` — `active` (`/tmp/tp01-evidence/plugin-rows.txt`).
Диагностика установки назвала неактивной чужую строку `1c-contour`;
причина внешняя (её `lib` пересобран после старта хоста, HMR отдал
старый модуль `paths.js`), наши строки активны — зацепка в отчёте.

Сессия `session-da5ed40c-0eae-456b-8f55-bc56a5900ca7`, cwd
`/tmp/tp01-architect-smoke`, создана через API живого хоста
(`session/create`, `agentPreset: architect`). Лог:
`/tmp/tp01-evidence/live-session.jsonl`, системный промпт —
`system-prompt.txt`:

- заголовок сессии `agentPreset: architect`, `parentSession: null`;
- `session/title` seq 4 = «Архитектор», `source: {kind: user}`,
  `messageSeqs: []` — имя стоит до первого сообщения, модель его не
  перегенерирует;
- персона в `system/message`: секции «## Роль», «## Команда»,
  «## Как писать», «## Границы»; `{{model}}` отрендерен в
  `qwen4-max-preview`; английской дефолтной персоны нет;
- инструменты `request/header`: `ask_user_question`, `read`,
  `read_image`, `write`, `edit`, `glob`, `grep`, `web_search`,
  `web_fetch`, `skill`, `subagent`, `subagent_fork`, `send_message`;
  `exit_plan_mode` и `workflow` отсутствуют — дельта копии видна живьём;
- маршрут — дефолт профиля `qwen-token-plan-max/qwen4-max-preview`
  (пресет модель на верхнем уровне не несёт, «Ограничения»);
- ответ модели: «Я архитектор OntoShip — аналитик-планировщик…» — роль
  работает.