# 02: Реестр исполнителей и пресеты orchestrator/executor

**Спека:** team-profiles (носитель: `ontoship-team/docs/plans/team-profiles.md`), «Готово» 1, 2.

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
`npm test` — **64 passed** (executors 16, composition 25, naming 19,
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
схлопывание, неизвестный id сохраняется до вызова. Механика `!!js`-выражения —
проба allowlist (носитель: `ontoship-team/docs/reference/dsh-preset-allowlist.md`;
на момент записи — `docs/reference/dsh-preset-allowlist.md` ядра)
(DSH 0.2.2-rc.2): сервис вызывается из выражения, неизвестный id
допустим до вызова; независимый носитель отказа — код хоста
`packages/subagent/tool-subagent/src/preset-selection.ts` («Unknown agent
preset» при спавне) и его контрактный тест; живьём отказ показан ниже.

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

## Ревью-панель

Один прогон, роли ядра из `.agents/config.toml`: `reviewer-spec`,
`reviewer-tests`, `reviewer-code`, `reviewer-kb` — маршрут
`qwen-token-plan/qwen3.8-flash`, `xhigh`, сверен живым
`list_subagent_models`; модель сессии — `deepseek-account/deepseek-flash`,
независимость соблюдена, фолбэков нет. Лимит детей хоста 4: три роли
стартовали в одном сообщении, `reviewer-kb` — по освободившемуся слоту;
прогон один, повторных проб на задержку не запускалось (норма тикета 01
про задержку роли). Вердикты: все четыре — «принять с находками»;
P1 нет. После дедупликации 7 P2 и 12 P3; все P2 закрыты одним проходом
правок (`f90d482`, `38a8f15`), 8 P3 закрыты, 12 открытых — в
`tickets/team-profiles/leads.md`.

P2 и судьба:

- **Конфликт read-only оркестратора с обязанностями chain** (spec, code):
  композиция оставлена по критерию тикета; носитель решения
  переадресован тикету 04 (метод-носители, текст chain) и оператору —
  в доказательствах и `leads.md` (запись «Оркестратор без write против
  обязанностей chain»).
- **Ложная формулировка про fork** (spec, code, kb): сужена до цепочных
  пресетов; у `architect` fork — копия standard (`f90d482`).
- **`disabled` не наследовался от группы** (tests): `walk` наследует
  выключенность родителя, группа сама включена — как `Entry.disabled`
  в loader; добавлена мутационная проба «выключенная группа снимает
  детей» (`38a8f15`).
- **Дефолт реестра сравнивался с константой кода** (tests): в тестах —
  литерал `["executor"]` из спеки, `DEFAULT_EXECUTORS` заморожен
  (`38a8f15`).
- **`ctx`-зависимый `disabled` молча считался выключенным** (tests):
  выражение вычисляется с фейковым `ctx`; ошибки выражений не глушатся,
  ошибка — красный тест (`38a8f15`).
- **Байтовый дрейф профильного `cordis.patch.yml`** (kb): назван в
  доказательствах и `profile-sha256.txt` (EOF +1 байт между проходами,
  mtime 15:07; строковых изменений нет, причина не установлена).
- **`leads.md` не переписан** (kb): обновлён — order закрыт, имя ребёнка
  сужено до `scout`, ask — GUI-ответчик, tool-plugin-manager — только у
  `architect`.

P3, закрытые этим проходом: trim полей реестра, freeze дефолта, jsdoc
без «замороженного», затенение `value`, строгий `catch`, `todo_write` в
контракте executor, `agentPreset: undefined` у executor, дельты ролей в
README, переименование теста неизвестного id, цитата кода хоста для
отказа при вызове, глобальные строки хоста в живой записи. Открытые —
`tickets/team-profiles/leads.md` (12 записей, в т. ч. read-only/chain,
живой дефолт битого файла, управление детьми у executor, дрейф EOF).

## Автоприёмка

**Тикет 02 принят автоприёмкой 2026-11-13** — оркестратор цепочки
(корневая сессия `lead`) проверил полный зелёный контур по артефактам:

1. Критерии 1–4 закрыты доказательствами. Оркестратор независимо
   перепроверил: `npm test` в репо `ontoship-team` на `38a8f15` —
   **64 passed** (4 файла); живой лог оркестратора — 16 инструментов,
   write/edit/bash отсутствуют, ask и subagent на месте; дочерняя
   сессия executor — write/edit/bash на месте, ask отсутствует; enum
   `agent_preset` = `["executor","1c-executor"]` из файла реестра;
   негативная проба — «Unknown agent preset: 1c-executor» при вызове;
   `executors.json` профиля — схема `{id, provider, model, level}`.
2. Панель: один прогон, один проход правок, открытых P1/P2 нет
   (7 P2 после дедупликации закрыты, в т. ч. конфликт read-only/chain —
   переадресацией с названным носителем: тикет 04 и решение оператора,
   запись в leads.md; решение выносится оператору оркестратором).
3. Dev/prod: dev — сборка и набор зелёные; prod — реестр, пресеты,
   спавн и отказ неизвестного id работают живьём. Названные пробелы:
   живой round-trip ask (GUI-ответчик, тикет 07), живой дефолт битого
   реестра (рестарт-проход 06/07).
4. Механические гейты пака: паков нет, ноль назван.
5. Точки остановки «Ограничений» пройдены (раздел доказательств).

Merge ff в main = `622d0bd`, worktree `ontoship-ntin-wt-tp02` и ветка
снесены. Репо `ontoship-team`: коммиты `c4cc35d`, `f90d482`, `38a8f15`;
remote нет — названный пробел. Двенадцать открытых P3 — в `leads.md`,
автоприёмку не блокируют. Конфликт read-only оркестратора с
обязанностями chain решён оператором ask 2026-11-13: read-only
сохраняется, записи пишет исполнитель по диктовке оркестратора;
носитель правки нормы — тикет 04 (решение записано в тикете 04).
