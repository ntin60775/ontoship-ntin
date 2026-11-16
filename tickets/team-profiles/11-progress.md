# Тикет 11 — прогресс ship

Тикет: [11-session-flow.md](11-session-flow.md). Спека:
team-profiles.md (носитель: `ontoship-team/docs/plans/team-profiles.md`), «Готово» 11, решение 20.

- [x] Статусная запись цепочки (основной checkout, `dc5c4c1`): continue,
      kanban, dag — тикет 11 в работе.
- [x] Решение оператора о стопе после отчёта (основной checkout,
      `aaecc89`): continue.md «Где мы» и «Порядок тикетов».
- [x] Worktree `ontoship-ntin-wt-tp11`, ветка `tp11-session-recon` от
      `dc5c4c1` (`create_worktree` упал без node в PATH — запасной
      `git worktree`).
- [x] Разведка 8 вопросов: живые логи в `11-evidence/`: пробный цикл
      02:42–02:43, лимиты 02:44, scheduler 02:51, гибрид 02:50,
      изолированный хост 02:46–02:48 и фокусная cookie-проба.
- [x] Живой пробный цикл: сессия `executor` «Игнат · Исполнитель» →
      prompt/wait/state/events → спавн scout «Аким · Скаут» → удаление;
      5 одновременных сессий; планировщик в корневой API-сессии создал
      задачу, делегированный ребёнок получил `subagent_session`; гибрид —
      чтение хода работающего ребёнка через `session/events`
      (`mode: continuable`). Пробные сессии удалены, GUI-список вернулся
      к 371, задача снята, пустой каталог хранилища удалён.
- [x] Изолированный хост (копия `DSH_HOME`, порт 3091): v2-cookie
      умирает на рестарте, v1-cookie живёт; продолжение persisted-сессии;
      обрыв хода на kill хоста (`turn/end aborted/disposed`), повторный
      prompt после рестарта.
- [x] Curated-сводка evidence: `11-evidence/README.md`, `source-facts.md`,
      `10-storage-format.md`.
- [x] Отчёт фактов и оценка вариантов — раздел «Отчёт разведки» в тикете 11.
- [x] Dev-проверки worktree: pytest **772 passed**, `gitmark lint
      --strict` чист, `install.sh --check` (основной checkout) `check: ok`;
      паков нет — механических гейтов ноль.
- [x] Один прогон ревью-панели (4 роли: spec, tests, code, kb) — все
      «принять с находками», P1 нет; инцидент доставки вердиктов записан
      в отчёт.
- [x] Один проход правок по находкам: точечные сырые снимки
      (`01-live-queue-state.json`, `01-live-afterseq.json`,
      `01-live-timings.json`, `04-live-child-row.json`,
      `08-hybrid-delete-job-block.json`, `07-sched-catalog-final.json`,
      `09-live-host-log-perm.txt`, `05-cleanup-storage.txt`), уточнены
      цитаты и числа, дрейф строк source-facts исправлен, секреты/префиксы
      вычищены.
- [x] Проверки после прохода правок: docs-only правки, покрыты
      prod-прогоном на main — 772 passed, lint чист.
- [x] Prod-проверки после merge: pytest 772 / lint / check на main
      (`11-evidence/11-prod-checks.log`); независимая перепроверка
      оркестратора — 772 passed.
- [x] Merge в main (ff `476da04`), снос worktree, автоприёмка
      2026-11-15 (запись по диктовке); цепочка — стоп-гейт оператора
      перед 07.
