# Tickets

Local execution tracker. One file per ticket, blockers first. Tickets are **not KB
documents**: no frontmatter, no ontology invariants, no plan registry. They are tracked
only so a fresh clone can continue the work; a closed ticket is marked done and keeps its
evidence in the tracker (the operator may remove a closed unit's tickets; git keeps the
history).

The durable contract is in [`docs/plans/`](../docs/plans/README.md). The first unit
`core-kb` is closed: all six tickets are done (2026-10-21), and there is no next ticket
yet. The tickets are in [`core-kb/`](core-kb/01-engine.md), in execution order.

| # | ticket | blocked by |
|---|---|---|
| 01 | [engine](core-kb/01-engine.md) | — |
| 02 | [kb-search skill](core-kb/02-kb-search-skill.md) | 01 |
| 03 | [kb-curate + ontology](core-kb/03-kb-curate-ontology.md) | 01 |
| 04 | [init skill](core-kb/04-init-skill.md) | 01 |
| 05 | [install](core-kb/05-install.md) | 02, 03, 04 |
| 06 | [dogfood](core-kb/06-dogfood.md) | 05 |
