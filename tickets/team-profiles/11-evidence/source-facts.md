# Источники фактов (DSH 0.2.2-rc.2)

Пути — от checkout `/home/prog7/home/dev/contrib/forks/deepseek-harness`,
номера строк — на 2026-11-15. Факты ниже проверены кодом; живые
подтверждения — в файлах `01`–`09` этой папки.

## API и транспорт

- Префикс API: `packages/client/connection/src/api-path.ts:7` — `/api`.
- Конверт запроса: `packages/client/connection/src/rpc.ts:81`
  (`ClientRequest`), схема — `packages/client/connection/src/rpc-schema.ts:36`:
  `client-request {type, rpcId, method, payload:{args}}`; ответ —
  `server-response {result:{ok, value|error}}`. Живой пример клиента —
  `apps/web/tests/smoke-real.e2e.ts:93` (`remoteRpc`).
- Методы сессий (Remote-имена = путь `/api/session/<имя>`):
  `packages/api/session-controller/src/index.ts`:
  `create` — 310, `selectModel` — 320, `delete` — 454, `prompt` — 485,
  `events` — 560, `state` — 593, `wait` — 615, `follow` — 627
  (stream, WebSocket-носитель `/api/remote.mux`), `projections` — 638.
- Типы запросов/ответов: `packages/api/session-controller/src/types.ts`:
  `SessionCreateRequest` — 279, `SessionDeleteRequest` — 321,
  `SessionPromptRequest` — 351, `SessionAddress` — 434,
  `SessionPageRequest` — 500, `SessionWaitRequest` — 656,
  `SessionState` — 638, `SessionEventsPage` — 682.
- `session/prompt` возвращает `SessionPromptValue {accepted:true}`
  (`types.ts:362`); запись в inbox — `commands.prompt` (`index.ts:484`).
- Очередь входа: `SessionQueuedItem` (`placement:'queued'|'steering'|'context'`,
  `rpcId`) — `types.ts:629`; пассивный снимок `session/state` собирается в
  `src/state/controller.ts:218`.
- `session/wait`: таймаут по умолчанию **30 000 мс** — `src/state/controller.ts:18`;
  `afterSeq`/`maxMessages` — 57–58; ожидание не отменяет ход — 50–52.
- `session/events`: страница назад по `address`, `cursor`, `records`,
  `hasMore` (`index.ts:559`; `types.ts:500`).
- `session/delete`: закрывает live-agent, работу останавливает только
  при `stopActivity`; иначе `session/live` с `activity` — 
  `src/commands.ts:255–300`; коды `session/live` — 62–70,
  `session/not-found` — 283.
- `session/follow` — поток, GUI берёт его по WebSocket
  `/api/remote.mux` (`packages/api/gateway/src/stream-protocol.ts:7`);
  оркестратору для чтения достаточно `wait`/`events` (разведка
  поток не проверяла — названный пробел).

## Авторизация: launch-токен и cookie

- Launch-токен: 32 случайных байта base64url (43 симв.), один на
  процесс (`PROCESS_LAUNCH_TOKENS` WeakMap по корневому контексту) —
  `packages/client/connection/src/browser-auth.ts:22, 61–68`; печать URL —
  `rpc-host.ts:197` и старт `dsh web`.
- `/connect?token=…&interactions=none|answer` → 302 на
  `./api/remote.mux` + **v2-cookie** `{version:2, authority, id:PeerId,
  issuedAt, expiresAt}` — `browser-auth.ts:314–350`.
- `/?token=…` → 303 на `./` + **v1-cookie** `{version:1, authority,
  issuedAt, expiresAt}` — `browser-auth.ts:263–290`.
- Cookie: `HttpOnly; SameSite=Strict; Max-Age=2592000`; срок —
  `cookieMaxAgeDays` по умолчанию **30 дней** —
  `packages/client/connection/src/index.ts:107–139`.
- Подпись — HMAC секретом из записи
  `client-connection/browser-session` файла `$DSH_HOME/.credentials.yaml`
  (`browser-auth.ts:182–196`; хранилище —
  `packages/credentials/credentials-local/src/index.ts:1–6`).
- v2-cookie несёт `PeerId`, который живёт в памяти процесса:
  проверка — `browser-auth.ts:371–383`, поиск peer —
  `rpc-host.ts:126–142`. После рестарта запись peer-а исчезает → 401.
- v1-cookie — stateless-HMAC, проверяется тем же секретом; после
  рестарта продолжает работать (живая проба `09-iso3-v1-after-restart.json`).
- Токен и cookie — owner-доступ: разграничения прав на методы сессий
  нет; любой владелец cookie видит и правит все сессии хоста.

## Планировщик и лимиты

- Запрет планировщика — по глубине делегирования:
  `packages/schedule/schedule/src/index.ts:655–671`
  (`delegationDepthOf(agent) > 0` → `subagent_session`), то же в
  `packages/schedule/tool-schedule/src/index.ts:299–309`.
- Инструмент планировщика виден только пресетам, где объявлен
  `tool-schedule`: в team-бандле это `preset-architect`
  (`/home/prog7/home/dev/contrib/forks/ontoship-team/cordis.patch.yml`, блок
  `preset-architect`); у `preset-orchestrator`/`preset-executor` строки нет —
  это факт композиции, не политики.
- Маршрут по умолчанию — профильный `agent-default-model`; на 03:15
  2026-11-15 живой профиль нёс `qwen-token-plan/qwen3.8-flash/medium`
  (`~/.dsh/profiles/web/cordis.patch.yml:96–101`, факт окружения; файл
  менялся во время разведки — репозиторий на него не опирается).
- Лимиты субагентов: `maxActiveSubagents` (дефолт 8) и `maxDepth`
  (дефолт 1) — `packages/subagent/subagent/src/index.ts:188–197`;
  лимит активных детей проверяется при спавне
  (`subagent/src/manager.ts:337, 718`) — отказ, не очередь. Живой
  профиль: `maxActiveSubagents: 4`, `maxDepth: 3` —
  `~/.dsh/profiles/web/cordis.patch.yml` (факт окружения, не репо).
- Кэпа числа сессий в `packages/api/session-controller` нет; живые
  пробы — `06-limits-multi-session.log` (5 одновременных сессий).
- HTTP-тело запроса к API ограничено 300 МиБ —
  `packages/client/connection/src/http-bridge.ts:13`.

## Хранение сессии

- Каталог: `~/.dsh/sessions/<projectKey(cwd)>/<sessionId>/`;
  `projectKey`/`projectDir`/`sessionDir` — 
  `packages/session/session-persistence-jsonl/src/format.ts:215–290`.
- Файлы: `session.lock` и `session.v4.jsonl.zstd` (zstd-JSONL,
  `logSuffix` — `format.ts:40–42`); первая строка — заголовок
  `{type:'session', version:4, id, createdAt, cwd, delegationDepth,
  agentPreset}`, далее по событию на строку (`seq`, `time`, `type`,
  `data`). Живой сэмпл — `10-storage-format.md`.
- `delegationDepth` в заголовке — ключевой факт для планировщика:
  API-сессия пишет `0`.

## GUI и список сессий

- `session/list` отдаёт строки с `parentSessionId`, `origin`,
  `running`, `projections.values` (`agentPreset`, `title`,
  `modelSelection`, `subagent`, `inbox`); API-сессии видны в GUI
  (живой список 371, создание/удаление сразу отражается).
- Заголовок «Имя · Роль» пишется событием `session/title` при создании
  (`03-live-events-page.json`, seq 4); механизм — плагин имён тикета 09.
