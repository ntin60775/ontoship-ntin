# Тикет 12 — прогресс ship

Тикет: [12-hybrid-read-channel.md](12-hybrid-read-channel.md). Спека:
[team-profiles.md](../../docs/plans/team-profiles.md), «Готово» 12, решение 21.

- [x] Публикация тикета 12 (основной checkout, `63d44e3`): спека-дельта,
      тикет, виды, индексы, continue, leads.
- [x] Worktree `ntin-wt-tp12` (tp12-hybrid-read), team-worktree
      `ontoship-team-wt-tp12` (tp12-read), stack-worktree
      `ontoship-team-1c-wt-tp12` (tp12-pin).
- [x] Team-бандл: хост-плагин `ontoship-session-read` (read-only
      `session_read`: list/wait/events/projections, credential-цикл
      внутри, allowlist в коде, конфиг URL/лога, компактные проекции,
      адресация ребёнка), композиция orchestrator; v0.2.0,
      `methodContract: 2`; тесты бандла **123 passed** (build +
      typecheck зелёные); финальный релиз — `d36d483`, тег `v0.2.0`.
- [x] Нормы chain: раздел «Гибридный READ-канал», контракт 2 и правило
      bump с категорией «обязательные механизмы ведения», тик с
      API-снимком, сверка результата durable log, пенсия по tokenUsage
      (пороги — проектный факт continue.md; литералы в скилл не носятся), три состояния тишины, steer/queue;
      `tests/test_skill_chain.py` **24 passed**; красная проба на базе —
      шаг ниже.
- [x] Стек: пин team v0.2.0 (`d36d483`, тег `v0.2.0`) и строка
      read-инструмента у 1c-orchestrator; паритетный тест — 25 passed;
      финальный коммит стека — `ce613af`.
- [x] Живая проба на изолированном хосте: чтение работающего ребёнка
      (`running`/`tokenUsage`/events по имени), read-only отказ,
      credential после рестарта, match контракта 2 на изолированном хосте
      и mismatch на живом (`12-evidence/`).
- [x] Dev-проверки: ntin 776 passed, team 123, stack 25, chain 24 +
      canon 75, красная проба на базе — 22 нарушения, композиционная
      краснота на базе — 1 failed / 34 passed.
- [x] Один прогон ревью-панели: spec/tests «принять с находками», code и
      kb «вернуть» (P1 — порядок `events` и устаревшие хеши/логи после
      перевыпуска, P2 — таймаут `wait`, литералы порогов, README стека,
      сироты, разрешение имени без parentSessionId); один проход правок
      закрыл P1/P2/P3, team 123 passed, релиз `d36d483` перевыпущен, стек
      `15c4287` перепинен, логи пересняты.
- [x] Prod-проверки после merge: ntin 776/lint/check, team 123, stack 25
      (`12-evidence/15-prod-checks.log`); merge трёх репо, worktree снесены.
- [ ] Автоприёмка (запись по диктовке).
