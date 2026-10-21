---
node_type: index
title: Plans
service: _platform
status: active
updated: 2026-10-21
links:
  part_of: [../README.md]
  relates_to: [core-kb.md, ../decisions/ontoship-core.md, ../ops/continue.md]
---

# Plans

Plan contracts (`node_type: plan`) — durable specs of one unit. Tickets are ephemeral
and do not live here; `to-tickets` publishes them to `.scratch/<slug>/issues/` or a
tracker after the plan gate.

- [core-kb.md](core-kb.md) — the first unit: installable KB core (approved; complete,
  tickets 01–06).

There is no plan for the next unit yet: the operator approves one before tickets are
cut. The open work is recorded in [continue.md](../ops/continue.md).
