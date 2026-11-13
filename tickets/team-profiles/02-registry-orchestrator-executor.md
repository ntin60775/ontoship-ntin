# 02: Реестр исполнителей и пресеты orchestrator/executor

**Спека:** [team-profiles](../../docs/plans/team-profiles.md), «Готово» 1, 2.

**Блокируется:** 01

**Что построить:** хост-плагин `ontoship-executors` в team-бандле, строка
ДО деклараций пресетов; путь через `ctx.get('profileContext').dir`;
читает `<profile>/ontoship/executors.json` один раз при apply; схема —
массив `{id, provider, model, level}`, запись `executor` обязательна;
отдаёт синхронный `executors()` (массив id) для `!!js`-allowlist;
валидирует и дедуплицирует, при ошибке/пустом/без `executor` — громкий
лог и дефолт `["executor"]`. Пресеты `orchestrator` (read-only fs,
subagent, send_message, ask) и `executor` (рабочие инструменты, без ask);
spawn-инструмент оркестратора с `agentPreset: executor` и
`allowedAgentPresets` через `!!js`, `modelSelection: true`.

**Демо-путь:** `executors.json` с двумя id → новая сессия оркестратора,
enum `agent_preset` показывает оба; битый файл → дефолт `["executor"]`;
спавн исполнителя.

**Критерии приёмки:**

- [x] Плагин реестра — артефакт: вывод контрактных тестов
      (profileContext.dir, чтение один раз, схема, валидация/дедуп,
      дефолт при ошибке/пустом/без executor); ожидание: «Готово» 2;
      на базе плагина нет.
- [x] Allowlist — артефакт: тесты `[]`, дубли, без `executor`,
      неизвестный id; ожидание: enum из реестра, неизвестный id — отказ
      при вызове, `agentPreset: executor`; на базе нет.
- [x] Композиция orchestrator/executor — артефакт: вывод контрактного
      теста (orchestrator: read-only fs + subagent + send_message + ask;
      executor: рабочие инструменты, без ask); ожидание: «Готово» 1, 8;
      на базе пресетов нет.
- [x] Live — артефакт: id сессии оркестратора, enum с двумя id,
      спавн ребёнка-исполнителя; ожидание: спавн работает; на базе нет.

## Доказательства

Срез — репозиторий `ontoship-team` (ветка `main`): коммит `c4cc35d`
(реестр, пресеты, тесты). Worktree `ontoship-ntin-wt-tp02` (ветка
`tp02-registry-orchestrator-executor`, база `ee1cef9`) несёт только
запись доказательств. Логи — `02-evidence/`.

**Реестр (критерий 1).** `cordis.patch.yml`: `ontoship-executors`
(`ontoship-team/executors`) стоит ДО деклараций пресетов, рядом
`ontoship-team` (авто-имя), ниже `preset-architect`,
`preset-orchestrator`, `preset-executor`. Плагин: путь через
`profileContext.dir` (не `DSH_PROFILE_DIR`), чтение
`<profile>/ontoship/executors.json` один раз при apply, схема
`{id, provider, model, level}`, дедуп, громкий дефолт `["executor"]` при
отсутствии файла, битом JSON, не массиве, пустом массиве, записи не по
схеме или без `executor`; неизвестный id не фильтруется — отказ даёт
хост при вызове. Тесты `tests/unit/executors.spec.ts` (15): путь,
схема, все деградации с маркером в логе, дубли с предупреждением,
env-подмена при живом `profileContext`, read-once (правка файла после
apply не меняет allowlist), `executors()` возвращает копию.
`npm test` — **63 passed** (executors 16, composition 24, naming 19,
manifest 4), `build` и `typecheck` чисто —
`02-evidence/build-test.log`, `test-verbose.log`.

**Allowlist (критерий 2).** Пресет `orchestrator`: `tool-subagent` несёт
`agentPreset: executor` и
`allowedAgentPresets: !!js "ctx.get('ontoshipExecutors').executors()"`,
`modelSelection: true`, `modelDiscovery: true`; строка реестра выше
пресетов — контрактный тест композиции. Живой enum `agent_preset` —
`["executor","1c-executor"]` из файла профиля; `agentPreset: executor`
даёт дефолт при опущенном id. `[]`, дубли, без `executor` и неизвестный
id покрыты тестами реестра: `[]`/без `executor` — дефолт, дубли —
схлопывание, неизвестный id сохраняется до вызова. Механика
`!!js`-выражения и «неизвестный id — отказ при вызове» — проба
[dsh-preset-allowlist.md](../../docs/reference/dsh-preset-allowlist.md)
(DSH 0.2.2-rc.2): сервис вызывается из выражения, неизвестный id
допустим до вызова.

**Композиция (критерий 3).** `tests/unit/composition.spec.ts` (24):
orchestrator — `read`, `read_image`, `glob`, `grep`, `subagent`,
`send_message`, `ask_user_question`, `skill`, без `write`, `edit`,
`apply_patch`, `bash`, fork; tool-fs с `write: false`, `edit: false`,
`applyPatch: false`. Executor — `read`, `write`, `edit`, `bash`, `glob`,
`grep`, веб, `skill`, `subagent`, `todo_write`, без `ask` и без
`allowedAgentPresets`. Персоны обеих ролей — русские с секциями,
`{{model}}` — единственная переменная. Order-конвенция: корневые 20–29
(architect 20, orchestrator 21), служебные 30–39 (executor 30) —
закреплена тестом и README; список ролей авто-имени покрывает три
пресета (инвариант «каждый id роли имеет декларацию»).

**Live (критерий 4).** Профиль `~/.dsh/profiles/web`, dev-канал `link:`.
Файл реестра `ontoship/executors.json` (sha256 `5c1555…`) —
записи `executor` и `1c-executor` с маршрутом
`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`/`max`. Строки профиля
(`02-evidence/plugin-rows.txt`): `ontoship-executors`, `ontoship-team`,
`preset-orchestrator`, `preset-executor` — `active` (пресет с
`!!js`-allowlist смонтировался, значит выражение вычислено). Сессия
`session-4c7b3d48-ed22-4910-b3ce-6a84e0031a6f` (cwd
`/tmp/tp02-orchestrator-smoke`, создана через API живого хоста с
`agentPreset: orchestrator`): заголовок «Оркестратор» (seq 4, source
user), инструменты ask/read/read_image/glob/grep/skill/subagent/
send_message/wait_agent/list_agents — без write/edit/bash; глобальные
строки хоста (`working_directory`, `create_worktree`, `cordis_inspect*`,
`ontoship_board_open`) приходят не из композиции пресета, поэтому
«read-only fs» — гарантия уровня бандла, а не всего процесса. Один ход:
read `executors.json` → спавн `subagent` с `agent_preset: executor`,
`name: executor-02` и маршрутом из файла; результат «started subagent
executor-02» (`meta.name`); дочерняя сессия `b67d72f7-…`:
`agentPreset: executor`, `parentSession` = родитель, `origin: subagent`,
`delegationDepth: 1`; заголовок ребёнка — fallback по его промпту, не
роль: плагин детей не переименовывает. Ответ родителя называет маршрут
из реестра. Логи: `02-evidence/live-excerpt.txt`,
`live-orchestrator-session.jsonl`, `live-executor-child-session.jsonl`.

**Профиль и установка.** `remove_bundle` + `install_bundle` вернули
`application: restart-required` (`unmanaged-plugin`), как в тикете 01;
новые строки при этом активны, пресеты работают. Файлы профиля
(`package.json`, `cordis.patch.yml`, `pnpm-lock.yaml`) в этом проходе
побайтно не изменились — before/after в `02-evidence/profile-sha256.txt`.
Названный дрейф между проходами: тикет 01-evidence записал итогом своего
remove/install `cordis.patch.yml` = `3b93bb6f…` (+1 байт EOF); к началу
прохода 02 файл снова `c2d162e8…` (mtime 15:07, 4671 байт) — строковых
изменений нет, разница только в завершающем переводе строки; причина
возврата не установлена, наш проход файл не менял. Чужая строка
`1c-contour` по-прежнему неактивна по внешней причине (HMR отдаёт
модуль из периода до пересборки её `lib`) — не наш дефект, не трогали.

**Точки остановки «Ограничений».** Пресеты не несут модель на верхнем
уровне; реестр читается один раз, allowlist заморожен, маршруты live
(чтение в прогоне); `require` в выражении нет, путь через
`profileContext.dir`; лимиты детей не нарушены (один ребёнок); правок
1C-DSH нет; механических гейтов пака нет (`.agents/packs` пуст) — ноль
назван.

**Расхождения ожидание/факт.** Не было. Названные пробелы:
(1) `ask_user_question` живьём — только в схеме: blocking-вопрос ждёт
ответа UI/оператора, а `userQuestions.answer` Remote закрывает только
continued/timed-вопрос; живой round-trip требует ответчика в GUI —
зацепка (оператор/тикет 07); (2) живой дефолт при битом файле не
показан — реестр читается при apply, для перечитывания нужен рестарт
DSH; дефолты покрыты контрактными тестами; (3) оркестратор без
`write`: обязанности chain «запись автоприёмки в тикет» и «состояние в
continue.md» требуют write — композиция сделана по критерию тикета
(read-only fs), конфликт норм назван; его носитель — тикет 04
(метод-носители, текст chain) и решение оператора, не тикет 06
(релиз и поставка), а живая цепочка тикета 07 на этой композиции
упрётся в него до правки нормы.
