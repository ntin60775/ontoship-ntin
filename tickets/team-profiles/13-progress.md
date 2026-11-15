# Тикет 13 — прогресс ship

Тикет: [13-orchestrator-schedule.md](13-orchestrator-schedule.md). Спека:
[team-profiles.md](../../docs/plans/team-profiles.md), «Готово» 1, 10,
решения 19, 22.

- [x] Публикация (основной checkout, `cdf559c`): решение 22, тикет 13,
      виды, continue, индекс.
- [x] Worktrees tp13-schedule (ntin/team/stack от публикации/релизов).
- [x] Team v0.2.1 `eea68d1`: `tool-schedule` у orchestrator, контрактный
      тест, релиз/тег; **124 passed**, build зелёный;
      красная проба на базе v0.2.0 — 1 failed / 35 passed.
- [x] Стек `fc645f1`: строка tool-schedule у 1c-orchestrator, пин v0.2.1,
      паритет **25 passed** (dev через team-worktree до merge); P1 панели —
      закоммиченный симлинк `node_modules` убран, `.gitignore` — без слэша.
- [x] Live-проба на изолированном хосте 3093: listTools содержит
      schedule_*, `schedule_create`/`view`/`delete` живые; task
      `schedule-bbdc964e…` снята; 4 пробные сессии удалены.
- [x] Ранний merge team main (eea68d1 до панели) — исправлен reset'ом на
      `d36d483`; ветка/тег сохранены; расхождение названо в отчёте.
- [x] Один прогон ревью-панели + один проход правок.
- [x] Dev/prod финально, merge трёх репо, автоприёмка.
- [x] Автоприёмка 2026-11-15 (запись по диктовке); пенсия
      исполнителя-8 на границе 13/07, пробу 07 ведёт исполнитель-9.
