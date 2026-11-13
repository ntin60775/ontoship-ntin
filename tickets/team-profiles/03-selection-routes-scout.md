# 03: Выбор исполнителя, маршруты и scout

**Спека:** [team-profiles](../../docs/plans/team-profiles.md), «Готово» 1, 3, 5.

**Блокируется:** 02

**Что построить:** правило выбора исполнителя в скилле `chain`: сигнал
стека — указатель архитектора в спеке/continue.md; выбор пресета+маршрута
при спавне продолжаемой сессии и при пенсии/handoff (не на каждый тикет);
неоднозначность — остановка с вопросом; выбор называется в отчёте
(кандидаты, id, причина). Per-call маршруты через `read` реестра:
исполнитель — `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`/`max`,
scout — `qwen-token-plan/qwen3.8-flash`/`medium`; дефолт маршрута в
`agentOptions` — страховка. Пресет `scout` (read/grep/glob/web, без
write); `scout` в allowlist всех трёх ролей.

**Демо-путь:** два кандидата в реестре → оркестратор по указателю
выбирает ожидаемого, маршрут назван в отчёте; scout спавнится ролью.

**Критерии приёмки:**

- [x] Правило выбора — артефакт: текст chain + вывод контрактного теста
      (указатель, выбор при спавне/handoff, два кандидата 1C/не-1C,
      неоднозначность → стоп); ожидание: «Готово» 3; на базе chain без
      правила выбора (красная проба).
- [x] Маршруты — артефакт: схема реестра с provider, per-call read,
      отчёт выбора; ожидание: исполнитель deepseek-flash/max, scout
      qwen3.8-flash/medium, полная форма provider/model+level;
      «Готово» 5; на базе нет.
- [x] Scout — артефакт: вывод контрактного теста композиции (scout:
      read/grep/glob/web без write; scout в allowlist architect/
      orchestrator/executor); ожидание: «Готово» 1, scout у всех ролей;
      на базе пресета нет.
- [x] Live — артефакт: спавн с per-call маршрутом, спавн scout, отчёт
      выбора; ожидание: маршрут и выбор наблюдаемы; на базе нет.

## Доказательства

Срезы: `ontoship-ntin` — ветка `tp03-selection-routes-scout`,
коммиты `0642724` (раздел «Выбор исполнителя», контрактные тесты),
`499dafe`, `b7c25d3` и `d031833` (правки панели: приоритет маршрута,
scout без дефолта, доказательства);
`ontoship-team` — ветка `tp03-scout-routes`, коммиты `7346ade` (пресет
scout, allowlist, `agentOptions`, образец реестра, тесты), `d354d74`,
`779cf4f` и `a5b5b0c` (правки панели: scout без дефолта, compaction,
дельты, README).
Базы: ntin `dd372cf` (main на старте прохода), team `38a8f15`. Логи —
`03-evidence/`.

**Правило выбора (критерий 1).** `skills/chain/SKILL.md`, раздел
«Выбор исполнителя»: указатель архитектора в спеке/continue.md
(`Исполнитель: <id>`) → id из реестра
`<profile>/ontoship/executors.json` → иначе дефолт `executor`;
неоднозначность (id не из реестра или указатели расходятся) —
остановка с вопросом; пресет и маршрут выбираются при спавне
продолжаемой сессии и при пенсии/handoff, не на каждый тикет;
маршрут — per-call через `read` реестра в полной форме
`provider/model` + level; приоритет источников: проектный факт в
continue.md главнее записи реестра, затем реестр, затем дефолт хоста;
`agentOptions` — страховка; выбор называется в отчёте.
`tests/test_skill_chain.py::test_executor_selection_rule` — 16 passed в
файле, 757 passed в наборе (`core-tests.log`). Тест держит указатель,
гранулярность, двух кандидатов (`executor`/`1c-executor`), дефолт,
стоп при неоднозначности, отчёт выбора, полную форму маршрута,
приоритет источников, `read` реестра, заморозку allowlist,
`agentOptions` и реестр панели в `.agents/config.toml`; 16 мутаций
краснят (`_body_mutated` проверяет, что замена изменила текст).
Красная проба на базе `dd372cf` с новым тестовым файлом — 12 failed /
4 passed; `test_executor_selection_rule` падает на
`selection: missing section «выбор исполнителя»` —
`core-base-red.log`, `core-base-red-selection.log`.

**Маршруты (критерий 2).** `executors.example.json` — записи `executor`
(`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`, `max`) и `scout`
(`qwen-token-plan/qwen3.8-flash`, `medium`), полная форма
`provider/model` + level. `tests/unit/routes.spec.ts` (6) проверяет
схему, полную форму и оба маршрута; негативная проба «без provider» не
проходит схему; реестр без записи `scout` валиден — allowlist ролей
добавляет scout литералом. Схема `{id, provider, model, level}` и
деградации — `executors.spec.ts` (16). Живой реестр профиля web:
`executors.json` sha256 `c4a87eb1…`, запись scout
`qwen-token-plan/qwen3.8-flash/medium`; бэкап `5c155543…` —
`profile-registry.txt`. Per-call маршрут проверен живьём спавном:
сессия ребёнка `session-a716c5db…`, дескриптор и `request/header`
дали `qwen-token-plan/qwen3.8-flash` + `medium` —
`live-route-probe.txt`. Отчёт выбора: кандидаты `executor`,
`1c-executor`, `scout`; выбран маршрут scout-записи, причина —
проверка per-call полей из реестра. `npm test` — 76 passed,
`npm run build`/`typecheck` чисто — `team-tests.log`, `team-build.log`.
Красная проба на базе `38a8f15`: composition падает на отсутствии
`preset-scout`, routes — на отсутствии `executors.example.json` —
`team-base-red.log`.

**Scout (критерий 3).** `cordis.patch.yml`: `preset-scout` (id `scout`,
order 31, персона на русском с секциями); инструменты `read`,
`read_image`, `glob`, `grep`, `web_search`, `web_fetch`; нет `write`,
`edit`, `apply_patch`, `bash`, `ask_user_question`, `subagent`,
`subagent_fork`, `todo_write`. `scout` в allowlist spawn всех трёх
ролей: `!!js` union реестра и литерала `'scout'` (Set снимает дубль,
если запись scout есть в реестре); дефолт ребёнка у architect и
executor не задан — пресет наследуется от родителя, поэтому панель ship
не превращается в скаутов; у оркестратора дефолт `executor`.
`agentOptions` несёт дефолтный маршрут ребёнка (страховка).
`tests/unit/composition.spec.ts` — 31 passed: матрица scout, allowlist
трёх ролей, отсутствие дефолта scout у architect/executor
(`agentPreset` undefined), маршруты `agentOptions`, негативные пробы
(удаление строки web, добавление write). README: таблица ролей,
дельта, установка, границы.

**Live (критерий 4) — проба выполнена без рестарта.** После ff-merge
(ntin `8ee0c48`, team `a5b5b0c`), переустановки бандла
(`plugin_manager remove_bundle` + `install_bundle`) и подключения к живому
хосту по launch-токену из `/run/user/1000/dsh-web.log` (v2-cookie,
`/connect`) создана сессия оркестратора
`session-8a224f20-db0c-4b0d-9ebc-787da7210891` (`agentPreset:
orchestrator`, cwd `/tmp/tp03-live-scout`). Enum `agent_preset` живой
сессии: `["executor","1c-executor","scout"]` — allowlist пересчитан из
реестра после reinstall. Оркестратор прочитал реестр и спавнил
`scout-live` с `agent_preset: scout`, per-call маршрутом
`qwen-token-plan`/`qwen3.8-flash`/`medium`; сессия ребёнка
`37905736-c6bc-4a98-887d-de987cda3189`, `agentPreset: scout`,
descriptor и `request/header` совпали с маршрутом; инструменты ребёнка —
`read`, `read_image`, `glob`, `grep`, `web_search`, `web_fetch`, без
`write`/`edit`/`bash`/`ask`/`subagent`; ответ «готово». Отчёт выбора:
кандидаты `executor`, `1c-executor`, `scout`; выбран `scout`, причина —
запись реестра совпадает с заданным маршрутом лёгкой разведки.
Хост не перезапускался (PID 3746641); `install_bundle` вернул
`restart-required` только из-за чужой строки `1c-contour`, новые строки
активны (`preset-scout` — `fiberPhase: active`). Артефакты:
`03-evidence/live-scout.txt`, `live-scout-orchestrator-session.jsonl`,
`live-scout-child-session.jsonl`, `plugin-rows.txt`.

**Разбор расхождений.** Живой спавн scout выполнен после merge
(`live-scout.txt`), до merge был named gap — он снят. Ожидание критерия 2 в шапке тикета
дано шортхендом «исполнитель deepseek-flash/max»; полная форма спеки
(«Готово» 5) и артефакта —
`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`/`max`. Маршрут
chain-исполнителя (проектный факт `continue.md`:
`deepseek-account/deepseek-flash`, `max`) и запись `executor` в реестре
(`qwen-token-plan-deepseek/…`) расходятся; норма chain называет
приоритет: явный проектный факт главнее записи реестра. Для цепочки
этого проекта действует `deepseek-account/deepseek-flash` (так спавнен
исполнитель-4), запись `executor` остаётся маршрутом team-роли в
проектах без своего факта. Остальные проверки совпали. Панель — один
прогон, рассрочка 3+1; вердикты и судьба находок — ниже.
