# Evidence — тикет 03 «Живая проба маршрутизации и протокола»

Юнит `deliver`, спека deliver.md, «Готово» 3, 4, 6, «Протокол deliver»,
«Контракт акта», решения 6–7. База нарезки: ядро `40c0dc6`, реестр
`v0.2.0` (`f7c479e`).

## Поколения (фиксированы до сессий)

- Ядро-срез: worktree `ontoship-ntin-wt-dlv03`, sha `8c7bd4d` (main после
  merge тикетов 01/02), путь
  `/home/prog7/home/dev/contrib/forks/ontoship-ntin-wt-dlv03`.
- Реестр: `/home/prog7/home/dev/personal/consumer-registry`, sha `b276e3c`
  (main после merge тикета 02).
- Baseline обновлений: чекаут тега `v0.7.0` = `51dc54f`,
  `/tmp/dlv03/core-v0.7.0` (X2 — copy, X3 — link, созданы драйвером до сессий).
- Красная база: чекаут `40c0dc6`, `/tmp/dlv03/core-base` (продюсер PR,
  потребитель XR).
- Install-лог setup: `install-setup.log` (sha и пути всех поколений).

## Изолированный хост

- `DSH_HOME=/tmp/dlv03-dsh-home` — копия профиля web: team/stack-строки
  (`ontoship-team`, `ontoship-team-1c`, `dsh-1c-contour`) сняты из deps и
  bundles package.json копии, симлинки и ontoship-каталог профиля удалены;
  4 относительных симлинка @local перевязаны на абсолюты (перенос копии);
  4 dangling-симлинка — паритет с живым профилем (там тоже dangling).
  `pnpm-lock.yaml` копии не правился (хост одноразовый).
- Порт 3096, PID 526655 (обёртка 526653), лог `/tmp/dlv03/work/host.log`; живой GUI 3080
  не перезапускался, живой профиль не менялся.
- credential: launch-токен из лога хоста → v2-cookie (`interactions=none`
  для unary-вызовов, `interactions=answer` для WS-моста); файлы cookie —
  в /tmp/dlv03/work, права 600, в артефакты не попадают. **Фактическая
  поверхность:** вне контекста ship-сессии драйвера; сессии пробы имели
  файловый доступ к /tmp/dlv03/work и читали host.log (инцидент 3) и
  планировочное дерево чекаута ядра (инцидент 4) — требование «credential
  вне контекста агента» соблюдено для драйвера, но не изолировано от
  сессий пробы; названо, не замалчивается.
- Модель сессий пробы: профильный дефолт
  `qwen-token-plan-deepseek/deepseek-v4.1-flash-1017/max` (selectModel не
  вызывался), preset `standard`. Каталог маршрутов хоста: `model-catalog.json`.

## Механика ведения (прецеденты tp11/ctb04 + факт этой пробы)

- Unary API: session/create {cwd, agentPreset} → session/prompt {mode:queue}
  → session/wait {timeoutMs, afterSeq} → session/events (история) →
  session/projections (tokenUsage). Драйвер: `drv.py`, раннер `run.py`.
- **Факт пробы: профиль несёт legacy-ask** (`tool-ask-user` mode по
  умолчанию `legacy` — блокирующий, без foreground-таймаута; проекция
  userQuestions пуста, pendingInput=['question'] держится сколько угодно).
  Unary `userQuestions/answer` отвечает только на continued-вопросы
  (timed-режим) — в этой пробе не применим. Ответ драйвера идёт как у GUI:
  WS `/api/remote.mux` (interactions=answer) → поток `$events` →
  forwarded waterfall `user-questions/request` → POST `/api/$events/result`
  {clientId, eventId, outcome:{kind:'result', value:{answers:[...]}}}.
  Мост: `ask-bridge.mjs`, лог `bridge.log`, сырые ask/answer —
  `ask-*.json`/`answer-*.json`. **Правки панели кода драйвера** (после
  пробы, фактические ответы не менялись): run.py — удалён мёртвый
  `answer_ask` (ответы давал мост), исправлен рендерер tool-результатов
  (`data.message.content`/`toolCallId`; транскрипты перегенерированы из
  `*-events.json`, отказ установщика S2 теперь в tool-результате seq 110),
  громкие ошибки JSON; ask-bridge.mjs — снята не использовавшаяся
  approval-ветка (событий `approval/request` в пробе не было), снят
  custom-fallback (ответы S1/S4/S5 совпали с label опций дословно —
  `answer-*.json`), ошибки чтения политики громкие; drv.py — cookie
  создаётся сразу с правами 600. Зависимость моста: node + `ws` (пакет
  DSH-чекаута `apps/cli/node_modules/ws`) — отклонение от stdlib названо.
  Первый экземпляр моста (18:40:26) залогировал ask S1 как `log-only`:
  файл политик ещё не существовал (раннер регистрирует политику при
  старте; S1-start был раньше моста); мост перезапущен после регистрации
  политики, pending-ask доставлен и отвечен (18:41:47). Исходники
  механики: DSH checkout
  `packages/api/gateway/src/stream-protocol.ts`,
  `packages/interaction/tool-ask-user/src/index.ts` (mode default legacy).
- Ask канала свежей установки — нога оператора: драйвер отвечает выбором
  матрицы (S1/S5 — link, S4 — copy); ответ моста — дословный label опции
  («link (Recommended)» / «copy»). Ask удаления drifted-копии (S2) —
  не отвечается, протокол стоит на ask (нога оператора, пробел пробы).

## Решение оператора по бюджету (2026-11-17, ask в сессии ship)

Страж бюджета тикета (≤2.5M) оператором снят в сессии ship 2026-11-17
(дословный ответ оператора на ask о метрике счётчика: «я не ставил стража
статус теста ? пройден ?»); tokenUsage сессий называется фактом в evidence,
остановок по бюджету нет.
Метрика счётчика: uncachedInputTokens / outputTokens / cacheReadTokens
(кэш контекста перечитывается каждый шаг; красная сессия 28 шагов —
65k/20k/1.05M).

## Инциденты (названы)

1. **Orphan-сессия первого старта.** Первый запуск S1 (18:09) прерван
   сообщением оператора; bash-обёртка умерла, python-раннер остался жить
   и создал сессию `session-4ee0b605…` (дубль S1, тот же парафраз и cwd).
   Второй запуск (18:17) создал рабочую S1 `session-13c1ae52…`. Orphan
   обнаружен по двум pending-ask одного содержания при подключении моста;
   удалён `session/delete {stopActivity:true}` до всякой записи в X1
   (обе сессии стояли на ask канала, X1 не тронут — `ls` до удаления).
   Артефакт: `orphan-delete.json`. Раннер первого старта также нёс
   busy-loop на input-required (исправлено sleep 20 в run.py до матрицы).
2. **Legacy-ask вместо timed** — назван выше как факт механики, не дефект
   пробы: deliver спрашивает канал в обоих режимах одинаково; различие —
   только транспорт ответа драйвера.
3. **Красная сессия прочитала host.log драйвера.** Разведка файлов привела
   сессию к `cat … host.log` (лог изолированного хоста с launch-токеном;
   host.log имел права 0644, cookie-файлы создавались до chmod 600 —
   окно прав названо, drv.py исправлен панелью).
   Токен отредактирован в артефакте (`RED-events.json`,
   `<REDACTED-launch-token>`); повторный скан всех артефактов по значениям
   токена и cookie — чисто. Cookie-файлы и `.credentials.yaml` сессия не
   читала (сверка команд транскрипта). Токен изолированного хоста
   инвалидируется уборкой (остановка хоста + снос DSH_HOME); живой профиль
   не затронут. Урок драйверу: credential-носители не класть в каталог,
   видимый сессиям пробы (зацепка в leads).

4. **Сессии пробы читали планировочное дерево.** Чекаут ядра (link-источник)
   — репозиторий планирования: сессии, исследуя дерево, нашли и прочитали
   тикет 03, continue.md, docs/plans, драйвер-файлы /tmp/dlv03/work
   (S2 seq 89 — tickets/deliver; S4 seq 51–109 — work/ask-policy.json,
   install-setup.log; S5 seq 107 — continue.md main-чекаута; RED seq 106–117 —
   continue.md, docs/plans, тикет 03, skills/deliver/SKILL.md среза).
   **Влияние на критерии:** критерий 1 не затронут — первый вызов skill
   deliver (seq 18–19) предшествует всем чтениям (seq 51+), маршрутизация
   свежей сессии доказана до контаминации; ноги протокола — механические
   факты (check: ok, отказ установщика, акты, diff), сверены драйвером
   независимо. **Снято:** «красная сессия сама назвала пробел» как
   независимое свидетельство — RED назвала пробел после чтения тикета 03;
   краснота критерия 8 — механический факт (deliver в каталоге базы нет,
   0 skill-вызовов), не свидетельство сессии. Предпосылка «без контекста
   планирования» соблюдена разговорно (свежие сессии), но не файловно;
   названный пробел пробы. Зацепка: distribution-only чекаут (skills/ +
   scripts/, без tickets/docs) для будущих проб — leads.

6. **Рецидив завершающих newline в init-исполнении.** S4 записала все три
   файла без завершающего `\n` (AGENTS.md, .gitignore, continue.md),
   S5 и S4b — AGENTS.md без `\n` с ручной самоправкой; S4b .gitignore и
   continue.md снова без `\n`. Скилл init и тесты ядра корректны
   (804 passed, идемпотентность охранена); дефект — исполнение модели
   (правило «не добавляй завершающий перевод строки, которого в файле не
   было» переносится на новые файлы). Идемпотентность повторного init
   при этом держится (строковая логика, s1/s4b-init-rerun.log). Зацепка:
   явная формулировка шаблона init «новый файл кончается переводом
   строки» — кандидат следующего юнита ядра (leads).

## Участники

| проект | роль | установка | init | реестр |
|---|---|---|---|---|
| P1 | продюсер K1 presence | ядро link (срез) + реестр link | да (драйвер, setup) | файл есть (старт ведения драйвером, setup) |
| P2 | продюсер K2 контроль | ядро link (срез) + реестр link | **нет** (блока нет) | файл есть (старт ведения драйвером, setup) |
| P3 | продюсер K3 absence | ядро link (срез) | да (драйвер, setup) | **скилла нет** |
| PR | продюсер красной пробы | ядро link (база 40c0dc6) | нет | нет |
| X1 | потребитель S1 | свежая link (сессия) | сессией | — |
| X2 | потребитель S2 | baseline copy v0.7.0 (драйвер) | — | — |
| X3 | потребитель S3 | baseline link v0.7.0 (драйвер) → обновление link (сессия) | сессией при обновлении | — |
| X4 | потребитель S4 | свежая copy (сессия) | сессией | — |
| X5 | потребитель S5 | свежая link (сессия) | сессией | — |
| XR | потребитель красной пробы | ядро link базы (красная сессия) | красной сессией | — |

X1 несёт предсозданный `docs/ops/continue.md` с проектным содержанием
(коммит setup) — init сессии обязан оставить его unchanged (G-22).
Старт ведения P1/P2 исполнен драйвером в setup по правилам скилла
реестра (каркас → machine/project по факту, gitignore-строка, предупреждение
о сносе `.agents`); факт назван — критерий 4 допускает setup или сессию.
Удостоверение продюсеров (pwd/toplevel/readlink deliver, check):
`setup-verify.log`.

## Таблица маршрутов

| сессия | парафраз | session id | первый ход skill deliver | нога протокола | check: ok |
|---|---|---|---|---|---|
| S1 | «деплой и обновление X1» | session-13c1ae52… | assistant seq 19 / tool/call seq 20: TOOL skill {"name":"deliver"} | свежая link X1 | check: ok ✅ |
| S2 | «поставь онтошип в X2» | session-9801dda7… | TOOL skill {"name":"deliver"} (первый вызов) | отказ drifted-копии, остановка на ask | — (поставки не было) |
| S3 | «раскатай ядро в X3» | session-89b8d3fd… | TOOL skill {"name":"deliver"} (первый вызов) | обновление link X3 v0.7.0→срез, 0 ask | check: ok ✅ |
| S4 | «раскатай ядро в X4» | session-8ee45971… | TOOL skill {"name":"deliver"} (первый вызов) | свежая copy X4 (блока нет) | check: ok ✅ |
| S5 | «поставь онтошип в X5» | session-cecc2f85… | TOOL skill {"name":"deliver"} (первый вызов) | свежая link X5, absence | check: ok ✅ |
| S4b | «раскатай ядро в X4» | session-272672c1… | TOOL skill deliver (seq 18) | свежая copy X4 + старт ведения P2b сессией (решение 7), clean-контур | check: ok ✅ |
| RED | «поставь онтошип в XR» | session-5d91e0cd… | **вызова skill deliver нет** (0 skill-вызовов) | база: установка напрямую, пробел назван сессией | check: ok (база) |

## Ноги S2 ([s2-verify.log](s2-verify.log), верификация драйвером)

- Парафраз «поставь онтошип в X2» — не литерал блока; маршрут — description
  (первый вызов TOOL skill {"name":"deliver"}).
- Сессия: источник из realpath link-бандла, X2 найден соседним чекаутом,
  baseline распознан как copy v0.7.0 (10 бандлов побайтно равны тегу,
  deliver нет), канал copy — обновление тем же каналом, без ask.
- Установщик отказал до записей: `install: copy differs:
  /tmp/dlv03/X2/.agents/skills/kb-search (remove it to reinstall)`
  (транскрипт, seq ~110); сессия назвала отказ и спросила удаление
  (ask «Удаление drifted-копий», опции: удалить/сменить канал/не трогать).
- Мост не ответил (policy stop-on-ask) — протокол стоит на ask;
  молчаливого обхода нет. Ask зафиксирован: `ask-S2-973e2eaa.json`.
- X2 после: git status — только `?? .agents/` (baseline драйвера),
  10 бандлов, deliver нет, `check: ok` от v0.7.0 — сессия не писала.
- Реестр P1: записей не добавлено (акт только S1) — поставки не было.
- Сессия S2 удалена драйвером после фиксации транскрипта
  (`S2-delete.json`, stopActivity:true).
- tokenUsage S2: 25078 / 7737 / 261888.

## Ноги S1 (верификация драйвером, `s1-verify.log`, `s1-init-rerun.log`)

- X1: `check: ok` от среза; git status после поставки — только `.agents/`,
  `.gitignore`, `AGENTS.md`; `docs/ops/continue.md` — проектный маркер цел,
  diff 0 (G-22); readlink deliver → worktree среза.
- Идемпотентный init: драйвер закоммитил состояние поставки и исполнил
  повторный init по кейсам скилла — все четыре файла unchanged,
  `git diff` 0 строк, `git status` 0 строк.
- Акт P1 (`registry.local.json`): consumers[0] X1/project/active,
  version `v0.7.0-15-g8c7bd4d` (git describe среза, тега v0.8.0 ещё нет),
  since 2026-11-17; deploy_log: action «rollout X1», result ok,
  at 2026-11-17T16:44:03Z, actor «deliver (lead, сессия P1)», to та же
  версия, from отсутствует (свежая); followup fresh-session/consumer:X1
  done=false; acceptance[] пуст; updated_at изменился (каркас 1970 →
  2026-11-17T16:44:03Z). Валидатор на заполненном реестре — OK.
- tokenUsage S1: uncachedInput 47474 / output 14248 / cacheRead 924416;
  26 шагов, 1 ход (ask канала отвечен мостом внутри хода).

## Красная проба (критерий 8)

База `40c0dc6`: продюсер PR (ядро link базы, 10 бандлов, deliver нет —
`ls PR/.agents/skills` в логе), свежая сессия `session-5d91e0cd…`, парафраз
«поставь онтошип в XR». Транскрипт `RED-transcript.md`: 0 вызовов
инструмента skill; сессия поставила ядро установщиком напрямую и сама
назвала пробел: «В этом поколении ядра нет бандла deliver — маршрута
«поставь онтошип» в каталоге скиллов нет». tokenUsage: 65299/20291/1053952
(uncachedInput/output/cacheRead), 28 шагов. Артефакты: RED-events.json,
RED-projections.json, red-create.json, red-prompt.json, red-wait1.json.

## Ноги S3 ([s3-verify.log](s3-verify.log), [final-verify.log](final-verify.log), верификация драйвером)

- Парафраз «раскатай ядро в X3»: знаменательные лексемы {раскатай, ядро} —
  пересечение с description и блоком пустое (G-24, лексическая сверка
  драйвером); маршрут — чистая семантика description.
- Было: link baseline v0.7.0 (10 ссылок в core-v0.7.0), `--check` 11 drifted;
  стало: 11 ссылок в worktree среза (readlink всего каталога — в логе),
  `check: ok`. Канал link сохранён, ask не было (0 ask за сессию).
- Init X3: 4 файла created, повторный проход unchanged (отчёт сессии).
- Акт P1: `update X3`, from `v0.7.0` → to `v0.7.0-15-g8c7bd4d`, result ok,
  at 2026-11-17T16:53:07Z, followup fresh-session/consumer:X3 done=false;
  consumers: X1 и X3, updated_at изменился. Валидатор OK.
- **Наблюдение (зацепка, не дефект критерия):** прежней записи X3 в
  реестре не было (baseline без акта); `from` сессия взяла из факта прежних
  ссылок (тег baseline-дерева) и назвала это явно. Контракт акта определяет
  `from` как прежнее `consumers[].version` и не описывает случай отсутствия
  записи — формулировка на уточнение (leads).
- Открытый followup X1 сверен перед поставкой (контракт акта), закрытия
  нет — оставлен открытым.
- tokenUsage S3: 56623 / 11675 / 788480; 24 шага, 1 ход.

## Ноги S4 (верификация драйвером, `final-verify.log`)

- Контрольный контур K2: продюсер P2 **без init** — AGENTS.md и блока нет
  (gitignore P2 несёт только строку реестра). Парафраз «раскатай ядро в X4»
  маршрутизирован через description (первый вызов TOOL skill deliver) —
  блок-маршрут исключён конструктивно (G-2).
- Свежая copy: 11 бандлов скопированы (deliver — каталог, не симлинк),
  `check: ok`; канал спрошен (ask), мост ответил «copy» (выбор матрицы).
- Init X4: 4 файла created, идемпотентность сверена хэшами (отчёт сессии).
- Акт P2: `rollout X4`, to `unknown` (контракт: copy без прежней записи —
  unknown с названным пробелом), версия источника в note потребителя;
  consumers[X4].state active, since 2026-11-17, updated_at изменился.
  Валидатор OK.
- **Наблюдение (зацепка):** followup «свежая сессия потребителя» сессия не
  писала — буквальное чтение контракта «после обновления» (S4 — свежий
  rollout); S1 на свежем rollout followup писал. Разночтение формулировки
  контракта — на уточнение (leads), критерий 4 требует followup после
  обновления (S3 — написан).
- tokenUsage S4: 70755 / 21285 / 1345536; 30 шагов, 1 ход.

## Ноги S5 (верификация драйвером, `final-verify.log`)

- Продюсер P3: ядро link + init, скилла consumer-registry в каталоге нет
  (11 бандлов, реестра нет). Парафраз «поставь онтошип в X5» — description.
- Свежая link X5: `check: ok`, init 4 файла created, git status — только
  `.agents/` и файлы init.
- **Absence (критерий 5):** файла реестра в P3 нет (`ls` — отсутствие),
  fallback-записи нет; фраза названного пробела в финальном отчёте сессии:
  «Акт rollout в реестр не записан — пробел: скилла consumer-registry в
  контуре P3 нет… По контракту deliver при отсутствии скилла реестр не
  ведётся». Предложение поставить реестр — без действия (граница: deliver
  не ставит реестр продюсерам сам).
- tokenUsage S5: 65936 / 19668 / 1506560; 32 шага, 1 ход.

## Ноги S4b (clean-контур, решение оператора 2026-11-18; [s4b-verify.log](s4b-verify.log))

Перегон закрывает две находки панели: ветку решения 7 (deliver сам
стартует ведение при отсутствующем файле) и дефект init S4 (X4 пересобран).
Оператор выбрал вариант «S4b на clean-контуре» ask-ом 2026-11-18.

- **Clean-контур:** продюсер P2b — ядро link из distribution-only чекаута
  `core-dist` (sparse skills/ + scripts/ + корневые файлы репо, sha
  `8c7bd4d`, git describe `v0.7.0-15-g8c7bd4d`) + реестр link из `reg-dist`
  (sparse skills/ + scripts/, sha `b276e3c`); tickets/docs планирования в
  чекаутах отсутствуют; без init (блока нет), файл реестра отсутствует.
  X4 сброшен драйвером до базового коммита (удалены untracked-артефакты
  поставки S4 — /tmp, воспроизводимо).
- **Маршрутизация:** первый вызов — skill deliver (seq 18), затем
  consumer-registry (seq 23). Планировочных чтений нет (скан событий по
  tickets/docs/plans/continue/work/drv/host.log — 0; чтения
  core-dist/skills/init/SKILL.md — шаблон init, легитимный протокол).
- **Нога:** свежая copy X4 — 11 бандлов, `check: ok`; канал спрошен,
  мост ответил «copy» (дословный label).
- **Решение 7 исполнено сессией:** файла реестра P2b нет → сессия
  скопировала каркас, заполнила machine (hostname prog7, operator prog7)
  и project (P2b, путь, описание из README) по факту, добавила
  gitignore-строку `.agents/registry.local.json`, выдала предупреждение
  «снос P2b/.agents уничтожает реестр (бэкапа в v1 нет)» — финальный
  отчёт транскрипта.
- **Акт:** rollout X4, to `unknown` (контракт copy без прежней записи),
  result ok, at 2026-11-18T07:53:37Z, consumer X4 active since 2026-11-18,
  версия источника в note; валидатор OK ([P2b-registry-final.json](P2b-registry-final.json)).
  Followup на свежем rollout не писан (буквальное чтение контракта,
  зацепка leads — как S4).
- **Init X4:** AGENTS.md байт-в-байт шаблон (сессия сама дописала
  завершающий `\n`); **.gitignore и continue.md записаны без завершающего
  `\n`** — рецидив дефекта исполнения (инцидент 6). Идемпотентность
  доказана как есть: драйверский повторный init по кейсам скилла —
  diff 0, status 0 ([s4b-init-rerun.log](s4b-init-rerun.log)); init
  строки не добавляет и байты не нормализует, поэтому второй прогон
  ничего не меняет.
- tokenUsage S4b: 70709 / 20211 / 1572608; 36 шагов, 1 ход.

## Критерий → артефакт → ожидание

| # | критерий | артефакт | ожидание из спеки/тикета | краснота на базе |
|---|---|---|---|---|
| 1 | маршрутизация: первый ход skill deliver | транскрипты S1–S5 (первый TOOL skill), таблица маршрутов | «Готово» 4, G-1–G-3, G-24 | RED-transcript: 0 skill-вызовов, deliver в каталоге базы нет |
| 2 | удостоверение сессий | README (host/порт/preset/модель/cwd), setup-verify.log (pwd/toplevel/readlink), install-setup.log (sha+путь), *-create.json, model-catalog.json | «Готово» 4, G-10–G-12 | удостоверение не собирается: скилла нет |
| 3 | ноги протокола | s1-verify.log, s1-init-rerun.log, final-verify.log, транскрипты S1–S4, S2 ask | «Готово» 3, G-9, G-22 | протокол исполняет deliver, на базе его нет |
| 4 | presence-акт | P1-registry-final.json, P2-registry-final.json, транскрипты S1/S3/S4, валидаторы в final-verify.log | «Готово» 6, контракт акта, G-6/G-7/G-9 | коннектора и реестра DSH нет |
| 5 | absence | S5-transcript.md (фраза пробела), final-verify.log (файла нет) | «Готово» 6, решение 2 | deliver нет |
| 6 | ask-ноги — пробелы | раздел «Пробелы пробы», ask-S2 (остановка) | «Рамки», G-1 | — |
| 7 | уборка | раздел «Уборка» (после merge) | «Готово» 4, G-13 | — |
| 8 | красная проба маршрутизации | RED-transcript.md, RED-events.json, red-*.json | правило нарезки | сама проба — краснота базы |

## Сводка tokenUsage (страж снят оператором, факт)

| сессия | uncachedInput | output | cacheRead | шаги | ходы |
|---|---|---|---|---|---|
| RED | 65299 | 20291 | 1053952 | 28 | 1 |
| S1 | 47474 | 14248 | 924416 | 26 | 1 |
| S2 | 25078 | 7737 | 261888 | 11 | 1 |
| S3 | 56623 | 11675 | 788480 | 24 | 1 |
| S4 | 70755 | 21285 | 1345536 | 30 | 1 |
| S5 | 65936 | 19668 | 1506560 | 43 | 1 |
| S4b | 70709 | 20211 | 1572608 | 36 | 1 |

Новых токенов (uncachedInput+output) суммарно: **516 989** (401 874 входных
+ 115 115 выходных, 7 сессий включая S4b); cacheRead суммарно ~6.3M — перечитывание кэша контекста
каждый шаг (не новая работа). Orphan-сессия `session-4ee0b605` (инцидент 1)
в таблицу не входит: удалена до ног протокола, её usage не сохранялся.
Шаги — `sessionStats.steps` проекций (S5: 43, включая шаги после финального
отчёта; транскрипт фиксирует ход до turn/end).

## Прочие наблюдения (зацепки, не дефекты пробы)

- Init в X-проектах пишет стандартную раскладку, где ревьюеры совпадают с
  моделью сессии пробы (flash-1017); сессии S4/S5 назвали совпадение в
  отчёте. Норма независимости — норма реестра/панели, не init; на живом
  профиле оператора модель сессии иная. Факт среды пробы.
- Финальный отчёт S3 несёт декоративную вставку shields.io — косметический
  шум, на критерии не влияет.
- Разночтения формулировок контракта акта (from без прежней записи;
  followup на свежем rollout) — зацепки в leads, критерии не нарушены.

- **Init S4 записал файлы без завершающих newline** (AGENTS.md кончается
  `>`, .gitignore — `/`, continue.md — `.`; шаблон init и тест
  test_skill_init.py требуют завершающий `\n`); S5 тот же дефект правила
  вручную в своей сессии. Дефект исполнения init сессией S4, не скилла
  (набор ядра 804 passed, идемпотентность init охранена тестами);
  X4 как поставлен — не байт-в-байт шаблон, повторный init изменил бы
  файлы. Названо; исправление — решением оператора (перегон S4b или
  драйверская правка байтов + повторный прогон).

## Индекс артефактов

- Транскрипты: [S1](S1-transcript.md), [S2](S2-transcript.md),
  [S3](S3-transcript.md), [S4](S4-transcript.md), [S5](S5-transcript.md),
  [RED](RED-transcript.md) (текст ассистента, вызовы инструментов с
  аргументами, результаты усечены до 1800 символов, таймстемпы).
- Сырые события сессий: `S1-events.json` … `S5-events.json`,
  `RED-events.json` (полные события API; RED — с редактурой токена).
- Создание сессий: [RED-create.json](RED-create.json) (unary response),
  `S1-create-card.json` … `S5-create-card.json`, `RED-create-card.json`
  (list-строка + проекции + первые события журнала; unary create response
  S1–S5 раннером не сохранялся — пробел драйвера, назван панелью;
  create-карточки собраны после панели, пока хост жив),
  [list-final.json](list-final.json) (список сессий хоста до уборки).
- Блок-маршрут S1: [s1-block-cue.json](s1-block-cue.json) (reasoning seq 19).
- S4b (clean-контур): [S4b-transcript.md](S4b-transcript.md),
  `S4b-events.json`, `S4b-projections.json`, `S4b-create-card.json`,
  `S4b-run.log`, [s4b-verify.log](s4b-verify.log),
  [s4b-init-rerun.log](s4b-init-rerun.log),
  [P2b-registry-final.json](P2b-registry-final.json).
- Верификация после панели: [s2-verify.log](s2-verify.log),
  [s3-verify.log](s3-verify.log), [setup-log.log](setup-log.log)
  (diff профиля, симлинки, git log базовых коммитов, маркер X1).
- Проекции (tokenUsage, sessionStats): `S1-projections.json` …
  `S5-projections.json`, `RED-projections.json`.
- Создание/промпты: `red-create.json`, `red-prompt.json`, `red-wait1.json`,
  `red-sid.env`, `list-initial.json` (0 сессий на старте),
  `model-catalog.json` (каталог маршрутов хоста).
- Setup: [install-setup.log](install-setup.log) (sha и пути поколений,
  установки продюсеров и baseline), [setup-verify.log](setup-verify.log)
  (удостоверение продюсеров, валидаторы каркасов),
  [setup-init-registry.log](setup-init-registry.log) (init P1/P3 и старт
  ведения P1/P2 драйвером).
- Верификация ног: [s1-verify.log](s1-verify.log),
  [s1-init-rerun.log](s1-init-rerun.log) (повторный init X1),
  [final-verify.log](final-verify.log) (X3/X4/X5, реестры, поколения),
  [g24-lexical.log](g24-lexical.log) (лексическая сверка G-24).
- Наборы: [core-suite.log](core-suite.log) (804 passed),
  [lint.log](lint.log) (59 файлов чисто), [prod-checks.log](prod-checks.log)
  (copy 11 бандлов, selfhost main).
- Реестры: [P1-registry-final.json](P1-registry-final.json) (акты S1+S3),
  [P2-registry-final.json](P2-registry-final.json) (акт S4).
- Ask/ответы моста: `ask-S2-973e2eaa.json` (остановка), `ask-S1-*.json`,
  `ask-S4-*.json`, `ask-S5-*.json`, `answer-S1-*.json`, `answer-S4-*.json`,
  `answer-S5-*.json`; [bridge.log](bridge.log) (телеметрия моста).
- Телеметрия раннера: [runner-matrix.log](runner-matrix.log) (значимые
  строки; полный runner.log — 15M busy-loop шума orphan-раннера — вырезан,
  инцидент 1), `S1-run.log` … `S5-run.log` (вывод раннеров; **S1-run.log
  не доказательство**: строка «stopped_on_ask=True tokenUsage=None» —
  false positive раннера до правки детектора answered-ask и чтения
  проекций; транскрипт S1 и bridge.log фиксируют отвеченный ask и
  завершение хода, инцидент 1).
- Уборка: [orphan-delete.json](orphan-delete.json) (удаление дубля S1;
  session id — в runner-matrix.log и инциденте 1; X1 до удаления не тронут —
  git log X1: setup-коммит predates поставку, удаление 18:41:45 до ответа
  моста 18:41:47), `S2-delete.json`.
- Драйвер: [drv.py](drv.py) (HTTP-клиент), [run.py](run.py) (раннер),
  [ask-bridge.mjs](ask-bridge.mjs) (WS-мост ответов) — версии после правок
  панели; фактическое поведение пробы — в bridge.log/runner-matrix.log.
- Init продюсеров: [init-output-p1/](init-output-p1/),
  [init-output-p3/](init-output-p3/) (файлы init P1/P3 байт-в-байт).

## Уборка (после merge)

(заполняется после merge: список целей, скан остатков, живой профиль не тронут)

## Пробелы пробы (названные)

- **Контаминация планировочным деревом** (инцидент 4): сессии исходной
  матрицы читали тикет/спеку/драйвер-файлы через чекаут ядра; критерий 1
  и механические ноги не затронуты, свидетельство RED снято; S4b на
  clean-контуре (distribution-only чекауты) — без планировочных чтений,
  названный пробел исходной матрицы закрыт одной чистой сессией по
  решению оператора; полный перегон матрицы не делался (решение оператора).
- **Ветка решения 7 закрыта S4b** (deliver сам стартует ведение при
  отсутствующем файле); дефект init S4 закрыт пересборкой X4 в S4b
  (байт-дефект .gitignore/continue.md назван, инцидент 6, идемпотентность
  доказана как есть).

- Ask-ноги не исполняются: поиск X при ненахождении, удаление drifted-копии
  (S2 стоит на ask), смена канала, чекаут copy-продюсера (критерий 6).
- acceptance[] deliver не заполняет — акт оператора, пробел v1.
- Credential-носители драйвера (host.log, cookie) лежали в /tmp/dlv03/work,
  видимом сессиям пробы; красная сессия прочитала host.log (инцидент 3).
  Токен изолированного хоста инвалидируется уборкой; зацепка драйверу —
  изолировать credential от дерева пробы (leads).
- Повторный вызов init полной сессией не делался: идемпотентность доказана
  драйверским повторным прогоном по кейсам скилла (X1, s1-init-rerun.log)
  и сверкой хэшей сессий S3/S4/S5.
- WS-поток session/follow, session/cancel, steer — не использовались
  (ведения хватило unary + $events-мост).
