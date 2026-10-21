# OntoShip (DSH) — entry point

OntoShip is a method and a project-local package: a **markdown + git knowledge base**
with deterministic search, an interview that resolves a plan before code exists,
tracer-bullet tickets, and a gated ship flow — all on the host's native primitives.

> The canon is [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md).
> It is the arbiter: a rule that contradicts it belongs to the strict profile or to
> history, not to the default.

## Start here

- **Continue** → [docs/ops/continue.md](docs/ops/continue.md) — state, open work,
  ticket order, environment facts, start prompt.
- **The canon** → [docs/decisions/ontoship-core.md](docs/decisions/ontoship-core.md)
- **Sources** → [docs/reference/sources.md](docs/reference/sources.md)
- **The KB** → [docs/README.md](docs/README.md)

## Layout

```
docs/          the KB: canon, testing, sources, plans, ops
tickets/       local execution tracker (not KB; closed tickets keep evidence)
vendor/        ontoship-zcode engine baseline (MIT); ticket 01 trims it
skills/        the core skills: kb-search, kb-curate, init
scripts/       project-local install channel (link/copy/check)
tests/         engine, skill-contract and install tests
```

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

The engine baseline is `vendor/ontoship-zcode/gitmark.py`; ticket 01 produces
`skills/kb-search/gitmark.py`. Once it exists:

```bash
python3 skills/kb-search/gitmark.py index    # rebuild the index after editing docs
python3 skills/kb-search/gitmark.py lint     # ontology checks
python3 skills/kb-search/gitmark.py map -o docs-map.html
```

<!-- BEGIN ontoship -->
## Knowledge base (OntoShip)

- Entry point: [`docs/README.md`](docs/README.md) — the KB master index; every folder has
  a `README.md` index.
- Search before answering or writing: load the `kb-search` skill. The engine is at
  `.dsh/skills/kb-search/gitmark.py` for direct use.
- New or updated docs: load the `kb-curate` skill — search first, never duplicate.
- Maintain after editing docs:

  ```sh
  python3 .dsh/skills/kb-search/gitmark.py index
  python3 .dsh/skills/kb-search/gitmark.py lint --strict
  python3 .dsh/skills/kb-search/gitmark.py map -o docs-map.html
  ```

- The KB is markdown + git: `.gitmark/`, `*-map.html` and `.scratch/` are derived or
  ephemeral — never committed.
<!-- END ontoship -->
