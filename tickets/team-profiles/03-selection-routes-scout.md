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

## Ревью-панель

Один прогон, роли ядра из `.agents/config.toml`: `reviewer-spec`,
`reviewer-tests`, `reviewer-code`, `reviewer-kb` — маршрут
`qwen-token-plan/qwen3.8-flash`, `xhigh`, сверен живым
`list_subagent_models` (доступны `medium`/`xhigh`, дефолт `xhigh`);
модель сессии — `deepseek-account/deepseek-flash`, `max`; независимость
соблюдена, фолбэков нет. Паков нет — роли пака не запускались. Лимит
детей хоста 4: три роли (spec, tests, code) стартовали в одном
сообщении, `reviewer-kb` — по освободившемуся слоту; прогон один,
`reviewer-code` ответил с задержкой, повторной пробы на задержку не
запускалось (норма ожидания вердикта).

Сырых находок 29 (7 spec, 4 tests, 9 kb, 9 code); после дедупликации
23 — 2 P1, 7 P2, 14 P3. Вердикты: `reviewer-spec` — «вернуть»,
`reviewer-tests` — «принять с находками», `reviewer-kb` — «принять с
находками», `reviewer-code` — «вернуть» по снимку
`0642724`/`7346ade`; его P1 к моменту вердикта уже был снят правкой
панели.

P1 и судьба:

- **`agentPreset: scout` у architect/executor** (spec, code): дефолт
  перехватывал ревью-панель и срезы критика; снят, allowlist и
  `agentOptions` оставлены, панель наследует пресет родителя
  (`d354d74`).
- **Live-критерий не доказан** (spec, tests): до merge — named gap;
  после merge закрыт живой пробой без рестарта — reinstall, сессия
  оркестратора, спавн `scout` (раздел «Live», `586daf5`).

P2 и судьба:

- **Приоритет источников маршрута** (spec): chain называет «проектный
  факт в continue.md главнее записи реестра, затем дефолт хоста»
  (`499dafe`).
- **Зацепка имени `scout`** (spec): перенесена на 04/09 в `leads.md`;
  механизм в 03 не строился (`499dafe`).
- **README: `scout` по умолчанию у executor** (kb): исправлено
  (`a5b5b0c`).
- **README/образец: дубли маршрута и расхождение записи
  `1c-executor`** (kb, code): образец сокращён до `executor` + `scout`,
  JSON-блок из README убран, образец — единственный носитель значений
  (`d354d74`, `a5b5b0c`).
- **Коммиты в доказательствах не держали описанное состояние** (kb):
  правки панели закоммичены, доказательства перецитированы
  (`d354d74`, `779cf4f`, `499dafe`, `b7c25d3`, `a5b5b0c`,
  `d031833`, `8ee0c48`).
- **У scout нет compaction** (code): группа добавлена как у остальных
  ролей (`a5b5b0c`).
- **Инвариант «полная копия standard» разошёлся с кодом** (code):
  дельта `architect` и исключение `scout` названы в шапке патча и
  README (`a5b5b0c`).

P3 и судьба:

- `1c-executor` в образце (spec, code) — убран (`d354d74`).
- KB-справочник с прежним `!!js`-выражением (spec) — обновлён
  (`499dafe`).
- Страховка не покрывает не-дефолтного ребёнка (spec, code) — граница
  названа в README, chain требует явных полей (`499dafe`, `a5b5b0c`).
- Docstring завышал набор мутаций (tests, code) — исправлен
  (`499dafe`).
- Шапка `composition.spec.ts` без трассировки тикета 03 (tests) —
  добавлена (`779cf4f`).
- Заголовок `team-base-red.log` без команды и базы (tests) — лог
  перегенерирован (`499dafe`).
- Омонимия per-call (kb) — разведены выбор роли и передача полей
  (`b7c25d3`).
- Шортхенд ожидания критерия 2 (kb) — назван в «Разборе расхождений».
- Расхождение маршрута chain-исполнителя и записи реестра (kb) —
  приоритет назван в chain и в «Разборе расхождений».
- Стековый id закрытым списком в норме (code) — переведён в класс с
  примером (`b7c25d3`).
- Авто-имя `scout` как корневой сессии (code) — граница названа в
  README (`a5b5b0c`).
- Опечатка «эагерно» (kb) — исправлена (`499dafe`).
- `kanban.md`/`dag.md` (03 в `ready`) и устаревшая строка
  `continue.md` (kb) — запись приёмки и производных видов оркестратора;
  исполнитель их не правит.

Открытых P1/P2 после прохода нет; live закрыт после merge. В
`leads.md` закрыта зацепка «дефолт маршрута в норме chain», «имя
ребёнка scout» перенесено на 04/09, «сторож дрейфа копии standard»
оставлен открытым (кандидат тикета 06).

**Разбор расхождений.** Живой спавн scout выполнен после merge
(`live-scout.txt`), до merge был named gap — он снят. Ожидание
критерия 2 в шапке тикета дано шортхендом «исполнитель
deepseek-flash/max»; полная форма спеки
(«Готово» 5) и артефакта —
`qwen-token-plan-deepseek/deepseek-v4.1-flash-1017`/`max`. Маршрут
chain-исполнителя (проектный факт `continue.md`:
`deepseek-account/deepseek-flash`, `max`) и запись `executor` в реестре
(`qwen-token-plan-deepseek/…`) расходятся; норма chain называет
приоритет: явный проектный факт главнее записи реестра. Для цепочки
этого проекта действует `deepseek-account/deepseek-flash` (так спавнен
исполнитель-4), запись `executor` остаётся маршрутом team-роли в
проектах без своего факта. Остальные проверки совпали. Панель — один
прогон, рассрочка 3+1; вердикты и судьба находок — в разделе
«Ревью-панель».

## Автоприёмка

**Тикет 03 принят автоприёмкой 2026-11-13** — оркестратор цепочки
(корневая сессия `lead`) проверил полный зелёный контур по артефактам:

1. Критерии 1–4 закрыты доказательствами. Оркестратор независимо
   перепроверил: core `python3 -m pytest tests/ -q` — **757 passed**;
   team `npm test` на `a5b5b0c` — **76 passed**; `gitmark lint
   --strict` чист; `install.sh --check` — `check: ok`. Live-критерий
   закрыт без рестарта: `preset-scout` active после reinstall (хост
   PID 3746641 не перезапускался), сессия оркестратора
   `session-8a224f20-…`, enum `["executor","1c-executor","scout"]`,
   спавн `scout-live` с per-call маршрутом
   `qwen-token-plan/qwen3.8-flash/medium`, ребёнок `37905736-…` —
   дескриптор и инструменты совпали (read/grep/glob/web, без
   write/bash/ask), отчёт выбора на месте (`03-evidence/live-scout*`).
2. Панель: один прогон, один проход правок, открытых P1/P2 нет
   (29 сырых → 23 после дедупликации: 2 P1 / 7 P2 / 14 P3; P1.1 снят
   правкой `d354d74`, P1.2 live — закрыт живой пробой после merge по
   решению оператора ask 2026-11-13 «merge и попытка без рестарта»).
   Раздел «Ревью-панель» отсутствовал при первой проверке — дописан
   исполнителем до приёмки (`c6f820d`).
3. Dev/prod: dev — наборы и сборка зелёные; prod — reinstall, живая
   сессия и спавн scout работают без рестарта. Названные пробелы
   прежних тикетов (живая смена роли после рестарта, PR-путь
   team-репо) остаются в leads.md.
4. Механические гейты пака: паков нет, ноль назван (`gates.txt`).
5. Точки остановки «Ограничений» пройдены; решение оператора по
   live-критерию исполнено полностью (merge → reinstall → проба →
   успех).

Merge: ntin ff `8ee0c48` + evidence `586daf5` + раздел панели
`c6f820d`; team ff `a5b5b0c`. Worktree `ontoship-ntin-wt-tp03` и
`ontoship-team-wt-tp03` снесены, ветки удалены. Проход ручной
(«шип тикет 3»), исполнитель-4 (~215 ходов) — пенсия на границе
следующего тикета по стражу бюджета. Открытые P3 — в `leads.md`
(зацепка имени scout перенесена на 04/09, сторож дрейфа standard —
кандидат 06), автоприёмку не блокируют.
