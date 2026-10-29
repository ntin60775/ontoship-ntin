---
node_type: index
title: Планы
service: _platform
status: active
updated: 2026-10-29
links:
  part_of: [../README.md]
  relates_to: [core-kb.md, harness-agnostic.md, workflow-skills.md, install-dry-run.md, review-config.md, evidence-verification.md, ../decisions/ontoship-core.md, ../ops/continue.md]
---

# Планы

Контракты планов (`node_type: plan`) — durable-спеки одного юнита. Тикеты эфемерны и
здесь не живут; `to-tickets` публикует их в `.scratch/<slug>/issues/` или трекер
после план-гейта.

- [core-kb.md](core-kb.md) — первый юнит: устанавливаемое ядро KB (утверждён;
  завершён, тикеты 01–06).
- [harness-agnostic.md](harness-agnostic.md) — один project-local корень
  `.agents/skills` для zcode, DSH и Qoder (утверждён 2026-10-21; завершён, тикеты
  01–04).
- [workflow-skills.md](workflow-skills.md) — фазы метода как скиллы: `grilling`,
  `to-tickets`, `ship`, `testing` (утверждена 2026-10-21; завершена 2026-10-22,
  тикеты 01–06).
- [install-dry-run.md](install-dry-run.md) — режим `--dry-run` установщика: план без
  записи (утверждён и завершён 2026-10-23, тикеты 01–02).
- [review-config.md](review-config.md) — проектный конфиг субагентов, панель
  ревью-специалистов и критик плана (утверждён 2026-10-28, решения 1–14; завершён
  2026-10-29, тикеты 01–05).
- [evidence-verification.md](evidence-verification.md) — артефакт доказательства
  вместо красно-зелёного семафора: носители в «Готово», разбор расхождений,
  ранняя оценка цены доказательства (утверждён 2026-10-29, решения 1–6;
  нарезка тикетов).

Пять юнитов закрыты: четыре основных и игрушечный `install-dry-run`
(2026-10-23); `review-config` закрыт 2026-10-29. Шестой юнит
`evidence-verification` утверждён на план-гейте 2026-10-29 — нарезка тикетов.
Открытая работа и пробелы харнессов
записаны в [continue.md](../ops/continue.md).
