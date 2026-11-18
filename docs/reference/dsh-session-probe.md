---
node_type: reference
title: Ведение сессий DSH через API и изолированный хост пробы
service: _platform
status: active
updated: 2026-11-18
tags: [dsh, api, session, probe, isolated-host, ask, websocket, credential]
links:
  part_of: [README.md]
  relates_to: [harnesses.md, ../ops/continue.md, ../plans/deliver.md]
  implemented_by:
    - ../../tickets/deliver/03-evidence/drv.py
    - ../../tickets/deliver/03-evidence/run.py
    - ../../tickets/deliver/03-evidence/ask-bridge.mjs
---

# Ведение сессий DSH через API и изолированный хост пробы

Как создавать и вести свежие сессии DSH без GUI (живые пробы
маршрутизации, самодостаточности, протоколов) и как отвечать на ask
сессии из драйвера. Механика сверена на DSH 0.2.2-rc.2; рабочий код
драйвера — в evidence тикета deliver/03 (ссылки `implemented_by`),
прецеденты — tp11 (`tickets/team-profiles/11-session-flow.md`), ctb04
(`tickets/core-team-boundaries/04-evidence/`), deliver/03
(`tickets/deliver/03-evidence/README.md`). Знание durable: при утере
кода драйвер восстанавливается по этому справочнику.

## Изолированный хост

Живой GUI оператора не перезапускается без решения оператора; проба
идёт на своем хосте с копией профиля.

1. Скопируй `DSH_HOME` выборочно: `profiles/`, `.credentials.yaml`,
   корневой `cordis.patch.yml`, `.anonymous-user-id`. Не копируй
   `sessions/`, `attachments/`, `storages/`, `state/` — хост одноразовый,
   чужие сессии и планировщик не нужны.
2. В копии `profiles/<профиль>/package.json` сними строки контуров,
   которых проба не должна нести (team/stack): deps и `dsh.profile.bundles`;
   удали их симлинки из `node_modules` и каталоги профиля контуров.
   `pnpm-lock.yaml` копии не правь (при переустановке снятые пакеты
   вернулись бы — хост одноразовый, назови факт).
3. Относительные симлинки `node_modules`, указывающие вне профиля,
   при переносе копии ломаются: перевяжи на абсолюты, вычисленные от
  оригинального расположения. Dangling-симлинки живого профиля сохрани как
   есть (паритет).
4. Старт из чекаута DSH:
   `node --import tsx/esm apps/cli/src/bin.ts web --no-open --port <порт>`
   с `DSH_HOME=<копия>`; node вне PATH — добавь каталог бинарников
   (факт окружения — continue.md, «Факты окружения»). Launch-токен
   печатается в stdout/лог строкой `dsh web: http://host:port/?token=…`.

## Авторизация драйвера

- Launch-токен живёт жизнь процесса; после рестарта — новый, старый 401.
- v2-cookie: `GET /connect?token=…&interactions=none|answer` → redirect +
  `Set-Cookie`; срок 30 дней, после рестарта хоста мертва (peer в памяти).
- v1-cookie: `GET /?token=…` → stateless-HMAC, переживает рестарт; секрет
  в `$DSH_HOME/.credentials.yaml`.
- `interactions=answer` нужен для приёма forwarded events (WS-мост);
  unary-вызовы работают и с `none`.
- Credential драйвера (лог хоста с токеном, cookie-файлы) держи вне
  дерева, видимого сессиям пробы: сессии исследуют файловую систему и
  читают найденное (инцидент deliver/03). Cookie-файл создавай сразу
  с правами 600.

## Unary API сессий

Формат: `POST /api/<method>`, тело
`{"type":"client-request","rpcId":"…","method":"<method>","payload":{"args":{…}}}`;
аргументы метода — по именам параметров (большинство — `request`,
`session/list` — `_request`).

| метод | аргументы | результат |
|---|---|---|
| `session/create` | `{request:{cwd, agentPreset}}` | `{sessionId, agentPreset}` |
| `session/selectModel` | `{request:{sessionId, provider, model, reasoningEffort}}` | выбор модели сессии |
| `session/prompt` | `{request:{requestId, sessionId, mode:'queue'\|'steer', content:[{type:'text',text}]}}` | `{accepted:true}`, ход исполняет хост |
| `session/wait` | `{request:{sessionId, timeoutMs?, afterSeq?, maxMessages?}}` | `{reason:'idle'\|'input-required'\|'timeout', state, output:{records}}` |
| `session/events` | `{request:{address:{kind:'session',sessionId}, maxMessages, beforeSeq?}}` | страницы истории назад, `hasMore` |
| `session/state` | `{request:{sessionId}}` | `{cursor, active, running, queue, pendingInput}` |
| `session/projections` | `{request:{sessionId}}` | `values.tokenUsage`, `sessionStats`, `title`, `userQuestions` |
| `session/list` | `{"_request":{}}` | строки сессий |
| `session/delete` | `{request:{sessionId, stopActivity?}}` | `{deleted:true}`; идущая работа блокирует без `stopActivity` |

Без `selectModel` сессия берёт профильный `agent-default-model`. Модель
сессии и preset называй в evidence пробы. `wait` не отменяет ход;
`records` — newest-first. Дети удаляются отдельно от родителя.

## Ask сессии: два режима и ответ драйвера

`tool-ask-user` имеет два режима (конфиг профиля):

- **legacy (дефолт)** — блокирующий ask без foreground-таймаута; сессия
  стоит на ask сколько угодно, `pendingInput:['question']`, проекция
  `userQuestions` пуста. Unary-ответ неприменим.
- **timed** — foreground-ожидание (дефолт 120 с) → результат `pending` →
  вопрос становится `continued`; ответ — unary
  `POST /api/userQuestions/answer`
  `{agentId:<sessionId>, callId, answer:{answers:[{id, selected:[label], custom?}]}}`.

Для legacy-ask отвечай как GUI — через forwarded waterfall:

1. WS `ws://host:port/api/remote.mux` с cookie `interactions=answer`.
2. Открой поток: `{"type":"open","streamId":"ev1","endpoint":"$events","payload":{"args":{}}}`.
3. Прими `{"type":"item","value":{"type":"ready","clientId":…}}`;
   pending-события доставляются новому клиенту при подключении.
4. На `{"type":"waterfall","event":"user-questions/request","eventId":…,"agentId":<sessionId>,"request":{questions,…}}`
   ответь `POST /api/$events/result` с
   `payload.args = {clientId, eventId, outcome:{kind:'result', value:{answers:[{id, selected:[label]}]}}}`.
   Label бери дословный из опций вопроса; `selected:[]` + `custom` —
   свободный ответ. Не отвечай на ask, который нога оператора должна
   оставить открытой (остановка протокола на ask — доказательство).

Мост — один на все сессии пробы; политики ответов — файл
`{sessionId: {policy, name}}`, перечитывай на каждое событие; отсутствие
политики логируй громко, не подставляй молчаливый дефолт.

## Чтение хода и транскрипт

- Вызовы инструментов — content-части `tool-call` внутри
  `assistant/message` (name, arguments-строка JSON); reasoning — части
  `reasoning` (cue маршрутизации виден там).
- Результаты — события `tool/result`: контент в `data.message.content`,
  id вызова — `data.message.toolCallId` (не `data.content`).
- Первые события журнала несут permission/preset, sandbox/mode,
  approval/policy — факты среды сессии для evidence.
- Файлы журнала: `$DSH_HOME/sessions/<projectKey(cwd)>/<sessionId>/session.v4.jsonl.zstd`
  (zstd-JSONL, forensic-чтение).

## Дизайн пробы (уроки deliver/03)

- **Поколение фиксировано:** sha и путь link-дерева — в install-логе до
  сессий; правка дерева во время пробы делает пробу недействительной.
- **Distribution-only чекаут:** link-источник пробы — sparse-чекаут
  `skills/` + `scripts/` (+ корневые файлы репо), без `tickets/` и
  `docs/`: иначе сессии находят и читают планировочный контекст (тикет с
  матрицей ожиданий, спеку, драйвер-файлы) и свидетельства перестают быть
  независимыми. Первый вызов skill до чтений — сверяй seq.
- **Свежая сессия на каждый парафраз:** после первого парафраза текст
  скилла в истории — второй маршрутизируется «по памяти», не описанием.
- **Блок vs description:** если литерал команды есть и в блоке init, и в
  description скилла, парафраз-литерал не дискриминирует канал;
  блок-маршрут доказывается reasoning-трассой (cue AGENTS.md),
  description — контуром без блока.
- **Бюджет:** `tokenUsage` = uncachedInputTokens / outputTokens /
  cacheReadTokens; cacheRead — перечитывание кэша контекста каждый шаг,
  не новая работа; метрику стража называй явно.
- **Уборка обязательна:** остановка хоста и моста, снос копии DSH_HOME
  (включая копию credential), temp-проектов и чекаутов, cookie/токен-файлов;
  скан остатков и запись в evidence; живой профиль/GUI не тронуты.