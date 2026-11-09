---
node_type: index
title: Документация — главный индекс
service: _platform
status: active
updated: 2026-11-09
links:
  relates_to: [../AGENTS.md, decisions/README.md, plans/README.md, ops/README.md, reference/README.md]
---

# Документация

База знаний ядра OntoShip. Она намеренно мала: канон, источники, из которых он вырос,
и решения, которые из них следуют. История процесса и строгий профиль живут в
репозитории `ontoship-zcode`, не здесь.

- [decisions/](decisions/README.md) — решения записи. Начни с
  [ontoship-core.md](decisions/ontoship-core.md), канона.
- [plans/](plans/README.md) — durable-контракты планов. Завершены:
  [core-kb.md](plans/core-kb.md) — устанавливаемое ядро KB (тикеты 01–06);
  [harness-agnostic.md](plans/harness-agnostic.md) — project-local корни
  каналов: `.agents/skills` и `.zcode/skills` (тикеты 01–04); [workflow-skills.md](plans/workflow-skills.md) —
  фазы метода как скиллы (тикеты 01–06);
  [install-dry-run.md](plans/install-dry-run.md) — игрушечный юнит
  dogfood-прогона (тикеты 01–02); [review-config.md](plans/review-config.md) —
  конфиг субагентов, ревью-панель и критик плана (тикеты 01–05);
  [evidence-verification.md](plans/evidence-verification.md) — артефакт
  доказательства вместо семафора (тикеты 01–04); мини-юниты
  [ship-isolation.md](plans/ship-isolation.md) — изолированный worktree для
  шипа; [understanding-check.md](plans/understanding-check.md) — сверка
  понимания вместо квиза; [onto-doc.md](plans/onto-doc.md) — тяжёлая
  док-часть, fan-out кураторов (завершён 2026-11-01, тикеты 01–05);
  [review-loose-ends.md](plans/review-loose-ends.md) — сторож паритета
  бандлов и нейтральные формулировки реестра ролей (завершён 2026-11-01,
  тикет 01 влит и принят).
- [dsh-adaptation.md](plans/dsh-adaptation.md) — DSH первым классом: скиллы,
  `init`, панель, критик и онто-док на нативных инструментах (утверждена
  2026-11-06; тикеты 01–04 приняты 2026-11-09, тикет 05 в работе).
- [ops/](ops/README.md) — операционные runbook'и. Начни с
  [continue.md](ops/continue.md), канонического старта: состояние, открытая работа и
  факты окружения.
- [reference/](reference/README.md) — сквозные справочники.
  [sources.md](reference/sources.md) — три источника и что из каждого взято;
  [testing.md](reference/testing.md) — spec-, инвариантные и target-тесты;
  [harnesses.md](reference/harnesses.md) — совместимость zcode, DSH и Qoder;
  DSH первый класс для ревью-панели и онто-дока, ZCode — legacy;
  [review-roles.md](reference/review-roles.md) — контракты ревью-ролей и регламент паков;
  [text-style.md](reference/text-style.md) — канон текстов: скиллы, правила,
  справочники, сообщения гейтов.
- [ontology.md](ontology.md) — словарь типов, frontmatter, типизированные ссылки и
  инварианты, которые проверяет lint; I2 читает его таблицу `node_type`.
