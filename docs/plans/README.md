---
node_type: index
title: Планы
service: _platform
status: active
updated: 2026-10-22
links:
  part_of: [../README.md]
  relates_to: [core-kb.md, harness-agnostic.md, workflow-skills.md, install-dry-run.md, ../decisions/ontoship-core.md, ../ops/continue.md]
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
  записи (dogfood-прогон 2026-10-22; утверждён оператором задним числом, детализация
  решений — на оценке).

Три юнита закрыты; план dogfood-прогона утверждён после отчёта задним числом.
Открытая работа и пробелы харнессов записаны в
[continue.md](../ops/continue.md).
