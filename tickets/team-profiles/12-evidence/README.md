# Тикет 12 — артефакты живой пробы READ-канала

Проба 2026-11-15 на DSH 0.2.2-rc.2. Профиль — изолированный хост
(копия `DSH_HOME`, порт 3092, лог `/tmp/tp12-live.log`); живой GUI
(PID 3746641) не перезапускался. Team-бандл в профиле — worktree
`ontoship-team-wt-tp12` (v0.2.0, `methodContract: 2`), строка
`tool-session-read` с конфигом пробы (`url` 3092, `logPath` — лог хоста).
Launch-токены и cookie в артефактах вырезаны.

## Цикл

1. Создана API-сессия `orchestrator` (`session-008281f9-…`, «Лев ·
   Оркестратор») в `/tmp/tp12-live-work`.
2. Prompt: спавн `tp12-child` (executor, `bash sleep 25`), затем
   `session_read`: `list`, `projections`, `events` по родителю и имени,
   попытка write-метода, ожидание ребёнка.
3. Ребёнок `90dd7ca8-…` («Рада · Исполнитель») прочитан **работающим**:
   `running: true`, `tokenUsage` (uncachedInput 7316, output 160),
   записи хода читаются; write-метод отвергнут схемой инструмента
   («method must be one of …»); ребёнок ответил `child-done`
   (`01-live-*`, `01-live-tool-records-first.json`).
4. Хост перезапущен; та же сессия продолжила работу. Новый prompt:
   спавн `tp12-child2` (executor, `bash sleep 5`), чтение по имени
   спавна через `events`/`projections`/`list`; имя разрешено каталогом
   `subagent/catalog` (`01-live-tool-records-after-restart.json`), потому
   что `session/list` имени спавна не несёт — это исправленный по ходу
   прохода дефект, покрытый тестом.
5. После рестарта credential перевыпущен внутри плагина (новый
   launch-токен из лога, v1-cookie); чтение сработало без ошибок.
6. Контракт: изолированный хост — `{contract: 2, absent: false}`
   (match), живой хост — `{contract: 1, absent: false}` (mismatch к
   ожиданию скилла 2; `04-contract-match-mismatch.txt`).

## Файлы

- `01-live-orch-wait-first.json`, `01-live-orch-events-first.json` —
  сырые ответы `session/wait`/`session/events` первого цикла;
- `01-live-orch-wait-after-restart.json`,
  `01-live-orch-events-after-restart.json` — второй цикл после рестарта;
- `01-live-tool-records-*.json` — извлечение `tool/call`/`tool/result`
  (аргументы и результаты `session_read`, `subagent`,
  `cordis_inspect_query`);
- `02-isolated-host-startup.log` — старт хоста (токен вырезан);
- `04-contract-match-mismatch.txt` — обе версии контракта;
- `05-redaction-scan.txt` — скан артефактов на секреты;
- `06-team-build.log`, `07-team-tests.log` — сборка и тесты team-бандла
  (118 passed, v0.2.0);
- `08-stack-tests.log` — тесты стека от нового пина (25 passed);
- `09-chain-tests.log`, `10-canon-sync-tests.log` — контракты chain и
  канона (99 passed);
- `11-ntin-dev-pytest.log` — полный набор ntin в worktree (776 passed);
- `12-red-on-base.log` — красная проба chain на базе `63d44e3`
  (22 нарушения: гибридных норм на базе нет).
