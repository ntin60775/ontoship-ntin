---
node_type: index
title: Документация — главный индекс
service: _platform
status: active
updated: 2026-10-23
links:
  relates_to: [../AGENTS.md, decisions/README.md, plans/README.md, ops/README.md, reference/README.md]
---

# Документация

База знаний ядра OntoShip. Она намеренно мала: канон, источники, из которых он вырос,
и решения, которые из них следуют. История процесса и строгий профиль живут в
репозитории `ontoship-zcode`, не здесь.

- [decisions/](decisions/README.md) — решения записи. Начни с
  [ontoship-core.md](decisions/ontoship-core.md), канона.
- [plans/](plans/README.md) — durable-контракты планов. [core-kb.md](plans/core-kb.md),
  устанавливаемое ядро KB, завершён (тикеты 01–06);
  [harness-agnostic.md](plans/harness-agnostic.md) — один project-local корень
  `.agents/skills` для zcode, DSH и Qoder (завершён; тикеты 01–04);
  [workflow-skills.md](plans/workflow-skills.md) — фазы метода как скиллы
  (завершена 2026-10-22; тикеты 01–06); [install-dry-run.md](plans/install-dry-run.md) —
  игрушечный юнит dogfood-прогона, утверждён 2026-10-23 (открыт тикет 02).
- [ops/](ops/README.md) — операционные runbook'и. Начни с
  [continue.md](ops/continue.md), канонического старта: состояние, открытая работа и
  факты окружения.
- [reference/](reference/README.md) — сквозные справочники.
  [sources.md](reference/sources.md) — три источника и что из каждого взято;
  [testing.md](reference/testing.md) — spec-, инвариантные и target-тесты;
  [harnesses.md](reference/harnesses.md) — совместимость zcode, DSH и Qoder.
- [ontology.md](ontology.md) — словарь типов, frontmatter, типизированные ссылки и
  инварианты, которые проверяет lint; I2 читает его таблицу `node_type`.
