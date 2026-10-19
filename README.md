# OntoShip for DSH

> **A project knowledge base is just `markdown` + a `README` index + `git`.**
> Nothing simpler works better.

OntoShip is a method for **transferring engineering practice**: a deterministic
markdown knowledge base, an interview that stress-tests a plan before code exists,
tracer-bullet tickets, and a gated one-ticket-at-a-time ship flow.

This repo is a **clean re-founding**, not a fork of the zcode texts. It goes back to
three sources and keeps only what they actually say:

1. **OntoShip** (vakovalskii) — the KB and the 11-step dev-flow. The product is the
   workflow; the KB is the substrate; the ontology is optional; simplicity is an
   operational property.
2. **Matt Pocock** — `grilling` (design tree, frontier, rounds) and `to-tickets`
   (tracer bullets, blocking edges, quiz). Decisions and ticket publication stay with
   the operator.
3. **The operator's testing strategy** — a test proves a spec clause, guards a project
   invariant, or reproduces a real failure (target test); scenarios are agentic (MCP), not
   hand-written safe paths; stale tests are deleted.

The canon is one page: [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md).
Sources and what was adopted from each: [docs/reference/sources.md](docs/reference/sources.md).

**Start here:** [docs/ops/continue.md](docs/ops/continue.md) — the state, the ticket
order and the start prompt. The first unit is [core-kb](docs/plans/core-kb.md); its
tickets are tracked in [tickets/core-kb/](tickets/core-kb/01-engine.md).

## Status

**Pre-alpha, self-contained.** The repo carries the canon, the plan, the tracked tickets
and the vendored engine baseline (`vendor/ontoship-zcode/`). The core is being built:
four skills (`grilling`, `to-tickets`, `ship`, `testing`), the GitMark engine, and the
install channel. The previous line
([ontoship-zcode](https://github.com/ntin60775/ontoship-zcode)) is kept as the **strict
profile** and history — not the default.

## Licence

MIT — see [LICENSE](LICENSE).
