# OntoShip (DSH) — entry point

OntoShip is a method and a project-local package: a **markdown + git knowledge base**
with deterministic search, an interview that resolves a plan before code exists,
tracer-bullet tickets, and a gated ship flow — all on the host's native primitives.

> The canon is [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md).
> It is the arbiter: a rule that contradicts it belongs to the strict profile or to
> history, not to the default.

## Start here

- **The canon** → [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md)
- **Sources** → [docs/reference/sources.md](docs/reference/sources.md)
- **The KB** → [docs/README.md](docs/README.md)

## Principle

Markdown + git is the source of truth. Everything derived — the search index, the
HTML graph — is regenerated, never committed as truth. Every folder's `README.md` is
its index; never let a doc become an orphan. Search the KB before answering or
writing a new doc.

## Shape

- **KB** is durable; **spec** is durable; **tickets** are ephemeral.
- **Facts** are the agent's job; **decisions** are the operator's.
- A test proves a **spec clause** or guards a **project invariant** — nothing else.
- Rules live in mechanisms (host gates, prompts, tests, the engine) or they do not
  live at all.

## Maintain

When the GitMark engine is vendored:

```bash
python3 skills/kb-search/gitmark.py index    # rebuild the index after editing docs
python3 skills/kb-search/gitmark.py lint     # ontology checks
python3 skills/kb-search/gitmark.py map -o docs-map.html
```
