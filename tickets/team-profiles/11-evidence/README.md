# Тикет 11 — артефакты разведки API-ведения сессий DSH

Разведка выполнена 2026-11-15 на DSH **0.2.2-rc.2**
(`/home/prog7/home/dev/contrib/forks/deepseek-harness`). Живой хост —
`http://127.0.0.1:3080` (PID 3746641, launch-токен из
`/run/user/1000/dsh-web.log`); изолированный хост — копия `DSH_HOME`
(`/tmp/tp11-dsh-home`) на порту 3091, живой GUI не перезапускался.
Launch-токены, cookie и ключи в артефактах вырезаны
(`<REDACTED-launch-token>`, `<REDACTED-cookie>`, `<REDACTED-secret>`);
длины и payload-ы сохранены. Записи `requestBody` содержат `rpcId` и
полное тело запроса — вызов воспроизводим при живом токене.

## Пробный цикл на живом хосте (демо-путь тикета)

| шаг | факт | файл |
|---|---|---|
| `session/create` | сессия `session-60f6f2cc-1bd9-405e-b31b-cfd8975158aa`, пресет `executor`, cwd `/tmp/tp11-probe` | `01-live-create.txt` |
| проекции | `session/title` = «Игнат · Исполнитель», `agentPreset` = executor, `blank` = true, маршрут ещё не выбран | `03-live-events-page.json` (seq 4), `05-cleanup-projections.json` |
| `session/selectModel` | маршрут сессии выставляется после создания: `qwen-token-plan/qwen3.8-flash/medium` | `01-live-prompt-first.txt` |
| `session/prompt` | unary, `{accepted:true}` за ~70 мс; ответ и ход — не в ответе вызова | `01-live-prompt-first.txt` |
| `session/wait` | `reason: idle`, `output.records` — `assistant/message` seq 17 «recon-ready» | `01-live-wait-first.json` |
| очередь | второй prompt (bash `sleep 5`) + третий в `mode: queue`; в `session/state` очередь `[{placement:"queued", rpcId:…}]`; `wait` вернулся через 7,3 с: ответы seq 33 «slow-done», seq 40 «queued-done» | `01-live-prompt-queue.txt`, `02-live-wait-two-turns.json` |
| спавн ребёнка | prompt 4: родитель вызвал `subagent` с `agent_preset=scout`; ребёнок `533d2cd0-4b8a-44f5-9b3d-491f00e32f8b`, `origin=subagent`, пресет `scout`, заголовок «Аким · Скаут», `parentSessionId` = родитель; ответ родителя «tp11-scout · scout-ok · scout-ok» | `04-live-wait-subagent.json` |
| история | `session/events` — 70 записей, cursor 69: `session/title`, `user/message`, `assistant/message`, `tool/call`, `tool/result`, `step/end`, `turn/end` | `03-live-events-page.json` |
| уборка | `session/delete` родителя и ребёнка → `{deleted:true}`; список GUI вернулся к 371; каталоги сессий удалены | `05-cleanup-delete-*.json`, `05-cleanup-list-summary.json` |

Сырой формат ответа `session/wait` (с `stream`-трассой `assistant/message`)
— `02-live-wait-two-turns.json`.

## Изолированный хост: токен, cookie, рестарт, обрыв хода

Копия `DSH_HOME` (`rsync` без `sessions/`), профиль `web` со всеми
шестью бандлами (в первом запуске относительные симлинки клона не
резолвились — исправлено на абсолютные, старт без `skipping profile
bundle`). Живой хост не трогали.

- **Фокусная проба cookie** (`iso3`): токен A → `/connect` v2-cookie
  (302) и `/?token=` v1-cookie (303). После рестарта хоста: v2-cookie
  → **401 unauthorized** (`09-iso3-v2-after-restart.json`), v1-cookie
  → **200** (`09-iso3-v1-after-restart.json`); свежий v2 по новому
  токену → 200 (`09-iso3-v2-fresh-after-restart.json`); старый
  launch-токен → **401** (`09-iso3-old-launch-token-after-restart.json`);
  токены A и B различны (`09-iso3-token-a-after-restart.json`).
  Payload-ы: `09-iso3-auth-a.json`, `09-iso3-auth-b.json`.
- **Рестарт с сессией** (`iso2`): S1 `session-3438ba39-0923-4245-81af-76c4915fbaba`
  создана и отвечена, хост перезапущен; старая v1-cookie работает
  (`09-iso2-old-cookie-after-restart.json`), S1 продолжил новый prompt и
  отдал «iso2-two» вместе с прежним «iso2-one»
  (`09-iso2-s1-wait-after-restart.json`).
- **Обрыв хода kill-ом хоста** (`iso2`): S2
  `session-9ad61977-f27b-4fa7-94db-9a3518da8d64`, prompt с bash `sleep 30`,
  хост убит через 3 с; после рестарта S2 в списке, `active:false`,
  история доигрывает `turn/end` с `{kind:'aborted', reason:{kind:'disposed'}}`
  (`09-iso2-s2-events-after-kill.json`), новый prompt принят и отвечен
  «iso2-after-crash» (`09-iso2-s2-wait-after-crash.json`).
- **Старые токены после kill** — 401 (`09-iso2-old-tokens-after-kill.json`);
  старые v1-cookie при этом работают (`09-iso2-old-cookie-after-kill.json`).
- Первичный прогон (payload v2-куки, до фокусной пробы) —
  `09-isolated-auth.txt`, `09-isolated-host-*-startup.log`.
- v1 index-cookie на **живом** хосте: `GET /?token=…` → 303 + cookie,
  `POST /api/session/list` → 200 (`09-live-index-cookie-*`).

## Карта вопросов тикета

| # | вопрос | ответ (кратко) | файлы |
|---|---|---|---|
| 1 | семантика `session/prompt` | unary-квитанция `{accepted:true}`, ход идёт в хосте; `queue`/`steer`; несколько prompt подряд; состояние очереди в `session/state` | `01-live-prompt-first.txt`, `01-live-prompt-queue.txt`, `02-live-wait-two-turns.json` |
| 2 | чтение вывода | `session/wait` (блокирует до idle/input-required/timeout, отдаёт `assistant/message` newest-first, `afterSeq` — инкремент), `session/events` (страницы всей истории), `session/projections` (снимок), файлы `~/.dsh/sessions/<hash>/<id>/session.v4.jsonl.zstd` | `01-live-wait-first.json`, `02-live-wait-two-turns.json`, `03-live-events-page.json`, `10-storage-format.md` |
| 3 | launch-токен и cookie | токен — 43 симв. base64url на процесс, печатается в stdout/лог, новый после рестарта, старый → 401; `/connect` → v2-cookie (PeerId в памяти, срок 30 дней, после рестарта 401); `/?token=` → v1-cookie (HMAC на диске, 30 дней, переживает рестарт); перевыпуск — повторный обмен с текущим токеном; истечение — 401 | `09-iso3-*`, `09-iso2-*`, `09-isolated-auth.txt`, `09-live-index-cookie-*` |
| 4 | лимиты сессий | кэпа числа/одновременности сессий в коде нет; 5 сессий созданы, запущены и отвечены одновременно, отказа нет; лимит `maxActiveSubagents: 4`, `maxDepth: 3` относится к субагентам, не к сессиям | `06-limits-multi-session.log` |
| 5 | уборка | `session/delete {sessionId, stopActivity?}` → `{deleted:true}`; сессия с ходом/фоновой job без `stopActivity` → `session/live`; с `stopActivity:true` — удаление и остановка; повторное удаление — `session/not-found`; каталог сессии удаляется, GUI-список обновляется; дети удаляются отдельно | `05-cleanup-*.json`, `05-cleanup-storage.txt`, `05-cleanup-list-summary.json` |
| 6 | планировщик в корневой API-сессии | запрет — по глубине делегирования: `delegationDepth 0` (API-корень) `schedule_create` **доступен**: задача `schedule-44fdcf3b-88c5-49a0-b621-6c9abd2c1961` создана; делегированный ребёнок (глубина 1) получил `{code:'subagent_session', message:'A delegated subagent cannot use scheduled tasks.'}`; задача снята через `schedule/edit` | `07-sched-*.json`, `07-live-wait-scheduler.json` |
| 7 | пресет, имя, спавн | `session/create` с `agentPreset` применяет персону/инструменты; `session/title` «Игнат · Исполнитель» пишется при создании (плагин имён тикета 09), ребёнок «Аким · Скаут»; API-корень спавнит детей (`subagent`, глубина 1, режим continuable); маршрут — `session/selectModel` | `03-live-events-page.json`, `04-live-wait-subagent.json`, `08-hybrid-child-rows.json`, `05-cleanup-projections.json` |
| 8 | надёжность | prompt — unary, оборвав связь клиент не отменяет ход; после чистого рестарта persisted-сессия продолжается; после kill-а хода `turn/end aborted/disposed`, сессия открывается и продолжается новым prompt; старая v2-cookie недействительна, v1 — действительна, токен нужен новый | `09-iso2-*`, `09-iso3-*` |

## Очистка проб

Список живого хоста до и после — **371 сессия**
(`05-cleanup-list-summary.json`), все пробные сессии удалены
(`session/delete`), каталог `/tmp/tp11-probe` в `~/.dsh/sessions/`
освобождён и снят; задача планировщика снята
(`07-sched-catalog-after-delete.json`), кроме прежних задач хоста в
каталоге ничего не осталось. Изолированный хост остановлен, его
сессии удалены; копия `DSH_HOME` — временная, вне репозитория.

## Как воспроизвести

```sh
# launch-токен живого хоста (значение — переменной, не в файл):
TOKEN=$(grep -m1 'dsh web:' /run/user/1000/dsh-web.log | sed 's/.*token=//')
# v2-cookie API-оператора:
curl -D headers -o /dev/null "http://127.0.0.1:3080/connect?token=$TOKEN&interactions=none"
# вызов метода:
curl -s -X POST http://127.0.0.1:3080/api/session/wait \
  -H 'content-type: application/json' -H "cookie: $COOKIE" \
  -d '{"type":"client-request","rpcId":"probe","method":"session/wait",
       "payload":{"args":{"request":{"sessionId":"<id>","timeoutMs":120000}}}}'
```

Изолированный хост: `DSH_HOME=/tmp/tp11-dsh-home` (копия профиля),
`node --import tsx/esm apps/cli/src/bin.ts web --no-open --port 3091` из
checkout DSH; launch-токен — в stdout. Рестарт — только на изолированном
хосте; живой GUI не перезапускается без решения оператора.
