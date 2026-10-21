---
node_type: index
title: Docs — master index
service: _platform
status: active
updated: 2026-10-21
links:
  relates_to: [../AGENTS.md, decisions/README.md, plans/README.md, ops/README.md, reference/README.md]
---

# Docs

The knowledge base of the OntoShip core. It is deliberately small: the canon, the
sources it came from, and the decisions that follow from them. Process history and the
strict profile live in the `ontoship-zcode` repository, not here.

- [decisions/](decisions/README.md) — decisions of record. Start with
  [ontoship-core.md](decisions/ontoship-core.md), the canon.
- [plans/](plans/README.md) — durable plan contracts. [core-kb.md](plans/core-kb.md), the
  installable KB core, is complete (tickets 01–06); the next unit has no plan yet.
- [ops/](ops/README.md) — operational runbooks. Start with
  [continue.md](ops/continue.md), the canonical start: state, open work and environment
  facts.
- [reference/](reference/README.md) — cross-cutting references.
  [sources.md](reference/sources.md) — the three sources and what was adopted from each;
  [testing.md](reference/testing.md) — spec, invariant and target tests.
- [ontology.md](ontology.md) — the type vocabulary, frontmatter, typed links and the
  invariants lint enforces; I2 reads its `node_type` table.
