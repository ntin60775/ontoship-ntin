---
node_type: plan
title: core-kb — installable KB core
service: _platform
status: draft
updated: 2026-10-19
links:
  relates_to: [../decisions/ontoship-core.md, ../reference/sources.md]
---

# core-kb — installable KB core

The first unit of the clean repo: a project can install the core locally and get a
working knowledge base — index, search, ontology lint, map — with **no registries** and
**no inventory command**.

## Goal

A DSH project installs the core into its own `.dsh/skills/` and gets a searchable,
lintable markdown KB: `index`, `search`, `lint`, `map`, `stat`, `version`. The engine is
one auditable Python-stdlib file; the install is idempotent; the skills are discovered by
DSH without a restart.

## Done

1. `scripts/install.sh <project>` creates `.dsh/skills/{kb-search,kb-curate,init}`
   (symlinks to this repo by default, `--copy` for a detached install) and runs the init
   step; a second run makes no change (idempotent) and `--check` reports drift.
2. In a temp repo with a minimal KB: `gitmark.py index` writes `.gitmark/index.db`;
   `search "<word>"` returns the doc; `lint --strict` exits 0; `map` writes HTML;
   `stat --json` returns valid JSON.
3. In the same temp repo, a broken body link and a load-bearing doc without
   `node_type` produce `ERR I4` / `ERR I1`, and `lint --strict` exits 1.
4. The engine file has no `inventory` or `serve` command and no I7; `cmd_lint` is an
   orchestration of extracted helpers (≤ 80 lines); the file stays one file
   (≤ ~1300 lines); the trimmed engine's tests pass.
5. A fresh DSH session in the temp repo lists `kb-search`, `kb-curate`, `init` in the
   skill catalog (the catalog is discovered from `.dsh/skills`).
6. This repository's own `docs/` passes `lint --strict` after `init` + `index`
   (dogfood), and `search "canon"` finds the canon.

## Scope

- `skills/kb-search/SKILL.md`, `skills/kb-search/gitmark.py` — the vendored engine,
  trimmed and adapted to `.dsh` paths.
- `skills/kb-curate/SKILL.md`, `skills/kb-curate/ontology.md` — the ontology rules and
  the shipped model (I1–I6, I8–I10; I7 is out).
- `skills/init/SKILL.md` — the managed block in `AGENTS.md`, the `.gitignore` lines.
- `scripts/install.sh` — project-local install, symlink/copy, `--check`.
- `tests/` — engine tests adapted to the trimmed surface; install idempotence test.
- `docs/` — this repo's own KB: index, ontology, decisions (already started).

## Constraints

- No registries, no `inventory`, no `serve`, no I7. No provenance line, Reel, acceptance
  chord, issue counter, or automatic grill → tickets chain.
- Project-local install only; the global Playwright MCP is the host default, not part of
  this unit.
- One engine file; no new invariants; DSH skill frontmatter (`name`, `description`,
  `user-invocable` / `disable-model-invocation` where it matters).
- The vendored engine is MIT; keep the attribution and the minimal-diff rule.

## Context

Sources and the canon: [ontoship-core.md](../decisions/ontoship-core.md),
[sources.md](../reference/sources.md). Decisions already taken: install channel
project-local `.dsh/skills`; first slice is install + KB core; the engine is vendored
from `ontoship-zcode`.

**Engine review (2026-10-19).** The 1570-line `gitmark.py` is not spaghetti: 53
functions, median 12 lines, no global mutable state, clear section banners, independent
commands. The complexity is concentrated in `cmd_lint` (134 lines, 47 branch nodes) and
in the embedded HTML/JS of `_MAP_HTML`; the rest is domain surface. The real problem is
the **product surface**, not the control flow: the file bundles index/search, ontology
lint, the **registry generator** (`inventory`, I7), the HTML map, and an HTTP server.
The canon rejects mandatory registries, so `inventory` and I7 go; `serve` goes; `map`
stays (optional, cheap). `cmd_lint` is split into helpers **inside the file** (link
graph, per-doc checks, global checks); a module split is deferred until the trimmed file
still exceeds the threshold. This keeps the "one file you can audit in an afternoon"
property and avoids a package layout for its own sake.

DSH skill roots (fact): `<project>/.dsh/skills` (rank 100), `<project>/.agents/skills`
(200), `~/.dsh/skills` (400); a skill is `<name>/SKILL.md` or flat `<name>.md`; nested
`**/SKILL.md` is not discovered. This defines the install layout.

Tickets are not part of this contract: they are ephemeral and will be published to
`.scratch/core-kb/issues/` by `to-tickets` after the plan gate.
