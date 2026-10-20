---
node_type: reference
title: Ontology model
service: _platform
status: active
updated: 2026-10-20
tags: [ontology, kb, curation, invariants, node-types]
links:
  part_of: [README.md]
  relates_to: [decisions/ontoship-core.md, reference/testing.md, plans/core-kb.md]
---

# Ontology model

The KB's semantic layer: node types, frontmatter, typed links and the invariants lint
enforces. This is the project copy; the package ships the same model in
`skills/kb-curate/ontology.md`. I8 compares the two bodies from the first `## ` heading,
so edit them in one change. `docs/ontology.md` is the only type vocabulary I2 reads.

## Semantic layer

A document's type is its `node_type`. The table below is the whole vocabulary: I2 rejects
a `node_type` that is not listed, and `docs/ontology.md` is the only place I2 reads it.
A new type is a new row here — there is no code list to edit. If the ontology file or its
`| node_type ` table is absent, the engine falls back to a built-in list; with an
ontology present, this table is authoritative.

| node_type | what it is | lives in |
|---|---|---|
| `index` | folder index: what the folder holds and links to its documents | every folder's `README.md` |
| `decision` | decision of record: what was decided and why | `docs/decisions/` |
| `plan` | durable spec of one unit: goal, done, scope, constraints, context | `docs/plans/` |
| `reference` | durable explanatory page: a topic, a source, a rule | `docs/reference/`; `docs/ontology.md` is the root-level model |
| `runbook` | operational procedure an operator can run | `docs/ops/` |
| `guide` | task-oriented how-to | any `docs/` folder that fits |
| `gotcha` | non-obvious pitfall and its workaround | next to the thing it warns about |
| `service` | service card: one service's contract | `docs/services/<service>/` |
| `report` | analysis or evidence produced by a run | any `docs/` folder that fits |
| `ticket` | opt-in KB ticket for a multi-day epic; never the default and never the local tracker's ticket files | wherever the project keeps opt-in KB tickets |
| `schema` | card schema for its folder: `card_type`, `required`, `values` | the folder whose cards it governs |

## Frontmatter

Frontmatter is YAML between the first pair of `---` fences. Every curated document
carries `node_type`, `title`, `service`, `status` and `updated`; `tags` and `links` are
added when they carry meaning. The header below is the norm:

```yaml
---
node_type: reference
title: What this document answers
service: _platform
status: active
updated: 2026-10-20
tags: [topic, subtopic]
links:
  part_of: [README.md]
  relates_to: [testing.md]
---
```

| field | role | checked by |
|---|---|---|
| `node_type` | one row of the table above | I1 in load-bearing folders; I2 vocabulary |
| `title` | one-line human title | review; the map falls back to the H1 or the filename |
| `service` | owning service, or `_platform` for cross-cutting docs | I2 warn when outside the per-repo service vocabulary |
| `status` | `active`, `draft`, `deprecated` or `archived` | I2 warn when outside the four values |
| `updated` | date of the last substantive edit, `YYYY-MM-DD` | review |
| `tags` | retrieval terms, a YAML list | not checked |
| `links` | typed links block (next section) | I4 targets; I3 connectivity; I6 `supersedes` |

## Typed links

`links` is a mapping of link type to one or more paths relative to the document.

| link type | meaning |
|---|---|
| `documents` | this document is about the target |
| `depends_on` | the target is a prerequisite; a change to it may require a change here |
| `supersedes` | this document replaces the target; the target must be `deprecated` or `archived` (I6) |
| `relates_to` | lateral association; neither prerequisite nor replacement |
| `implemented_by` | the target implements this decision, plan or rule (code, test, script) |
| `part_of` | this document belongs to the target section or folder index |

The values are repo paths, not URLs: I4 resolves every one from the document's directory
and fails on a target that a reader cannot open. A scalar is accepted, but a list is the
norm. Body links are untyped: they are navigation, still checked by I4, and still count
as graph edges for I3. Use `supersedes` only together with the old document's
`deprecated`/`archived` status.

## Invariants

Lint enforces these. `ERR` fails `lint --strict` (exit 1); `WARN` is hygiene that must be
read and explained. I7 is not here: the registry/inventory invariant is outside the
core, so there is no `inventory` command and no required registry table.

| id | invariant | check | level |
|---|---|---|---|
| I1 | load-bearing documents declare a type | a document in `docs/reference/`, `docs/ops/`, `docs/plans/`, `docs/decisions/` or `docs/services/` (except `README.md`) has frontmatter with `node_type` | ERR |
| I2 | controlled vocabularies | `node_type` is in the table above; `service` and `status` are in their vocabularies | ERR for `node_type`; WARN for `service`/`status` |
| I3 | no orphans | a load-bearing document has at least one incoming or outgoing link (frontmatter counts) | WARN |
| I4 | links resolve | every body link and every frontmatter link exists from the document's directory | ERR |
| I5 | every folder has an index | every folder under `docs/` has `README.md` | WARN |
| I6 | a replacement retires its target | a `supersedes` target has `status: deprecated` or `status: archived` | WARN |
| I8 | one ontology model | `docs/ontology.md` and the shipped `skills/kb-curate/ontology.md` agree from the first `## ` heading | ERR in the package repo; WARN when the package is external |
| I9 | card schemas are enforced | a `schema` document governs its folder through `card_type`, `required` and `values`; cards use the declared type, carry every required field and stay within the value lists | ERR |
| I10 | the index chain is closed | every `docs/` subsection `README.md` is reachable by a body link from its parent's `README.md` | ERR |

## Changing the model

1. Edit the `node_type` table in the project's `docs/ontology.md`.
2. In the package source repository, copy the body from the first `## ` heading into
   `skills/kb-curate/ontology.md`; after an install the package copy is external and I8
   reports drift as `WARN`, while the project copy stays authoritative.
3. Migrate documents before you remove a type; I2 names every straggler.
4. Rebuild the index and run `gitmark.py lint --strict`.

No other invariant is added by this document. I7 (registry) is the only invariant
deliberately left out of the core.
