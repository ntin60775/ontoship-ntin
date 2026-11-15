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
      `methodContract: 2`; тесты бандла **117 passed** (build +
      typecheck зелёные).
- [x] Нормы chain: раздел «Гибридный READ-канал», контракт 2 и правило
      bump с категорией «обязательные механизмы ведения», тик с
      API-снимком, сверка результата durable log, пенсия по tokenUsage
      (500k/600k — проектный факт), три состояния тишины, steer/queue;
      `tests/test_skill_chain.py` **24 passed**; красная проба на базе —
      шаг ниже.
- [x] Стек: пин team v0.2.0 (`96a4853`) и строка read-инструмента у
      1c-orchestrator; паритетный тест — 25 passed.
- [x] Живая проба на изолированном хосте: чтение работающего ребёнка
      (`running`/`tokenUsage`/events по имени), read-only отказ,
      credential после рестарта, match контракта 2 на изолированном хосте
      и mismatch на живом (`12-evidence/`).
- [x] Dev-проверки: ntin 776 passed, team 118, stack 25, chain/canon 99,
      красная проба на базе — 22 нарушения.
- [ ] Один прогон ревью-панели + один проход правок.
- [ ] Проверки dev/prod по репозиториям, merge трёх репо, снос worktree.
- [ ] Автоприёмка (запись по диктовке).
