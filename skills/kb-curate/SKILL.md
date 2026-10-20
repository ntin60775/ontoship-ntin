---
name: kb-curate
description: "Create, update, deprecate, link and reindex markdown knowledge-base documents under docs/. Use before adding or editing a doc: classify its node_type from docs/ontology.md, place it in the right folder, write the frontmatter, add typed links and a link from the folder README, then rebuild the index and run lint --strict."
---

# KB curation

Use this skill whenever a document under `docs/` is created, changed, deprecated or
linked. The KB is markdown plus git: the document is the source of truth, the folder
`README.md` is its index, and `.gitmark/` is derived. The model — node types,
frontmatter, typed links and invariants I1–I6 and I8–I10 — is in `docs/ontology.md`; the
package ships the same body in `skills/kb-curate/ontology.md` (I8).

Search before writing: use the `kb-search` skill, or run
`python3 skills/kb-search/gitmark.py search "<terms>"`. If an existing doc covers the
topic, update it instead of creating a duplicate.

## The five operations

| operation | when |
|---|---|
| CREATE | no existing doc covers the topic |
| UPDATE | the doc exists but its content, scope or links changed |
| DEPRECATE | the doc is replaced or no longer true |
| LINK | two docs should be connected, or a doc is orphaned |
| REINDEX | after any markdown change, to rebuild search and prove lint |

## CREATE

1. **Classify.** Pick one `node_type` from the table in `docs/ontology.md`. Do not invent
   a type in frontmatter: I2 rejects it. If no row fits, add a row deliberately (see
   "Change the model") before writing the doc.
2. **Place.** Put the doc where the type lives: `index` → `README.md`; `decision` →
   `docs/decisions/`; `plan` → `docs/plans/`; `reference` → `docs/reference/`; `runbook`
   → `docs/ops/`; a service card → `docs/services/<service>/`. Every `docs/` folder has
   a `README.md` (I5).
3. **Frontmatter.** Write the standard header: `node_type`, `title`, `service`, `status`,
   `updated`; add `tags` and `links` where they carry meaning. Use `service: _platform`
   for a cross-cutting doc. In `docs/reference/`, `docs/ops/`, `docs/plans/`,
   `docs/decisions/` and `docs/services/`, a missing `node_type` is I1.
4. **Link.** Add at least one meaningful link, typed or in the body, so the doc is not an
   orphan (I3). Typed links go in `links:` and use the keys in the model: `documents`,
   `depends_on`, `supersedes`, `relates_to`, `implemented_by`, `part_of`. Paths are
   relative to the doc and must exist exactly (I4).
5. **Index the folder.** Add a bullet to the folder's `README.md` with the title and a
   one-line summary, and link the doc from the README body. If the folder is a new
   subsection, also link its `README.md` from the parent `README.md` (I10).
6. **Reindex and verify.** Run the commands in REINDEX; read the lint output.

## UPDATE

1. Search and read the doc; read its folder `README.md` too, so the summary stays true.
2. Keep `node_type` unless the document's role changed. A type exists to describe the
   document, not to silence a vocabulary error.
3. Update `title`, `updated`, `tags` and `links` with the content. Re-check every path
   you touched; I4 resolves from the doc, not from the repository root.
4. If the scope changed, update the README summary and the parent index.
5. Reindex and verify.

## DEPRECATE

1. Set `status: deprecated` (or `archived` for a retired section). Keep the file: the
   history and the inbound links are still useful.
2. When a replacement exists, the replacement declares `links: supersedes: [old.md]`.
   I6 requires the old doc to be `deprecated` or `archived`; a supersedes link to an
   active doc is a warning.
3. Mark the old doc in the folder `README.md` and link the replacement.
4. Reindex and verify.

## LINK

- Use a typed link when the relation has a name; use a body link for navigation and
  prose. Both are checked by I4.
- `documents` — about; `depends_on` — prerequisite; `supersedes` — replacement;
  `relates_to` — lateral; `implemented_by` — code/test/script that implements it;
  `part_of` — section membership.
- Link from the folder `README.md` for every new doc. A doc with no in/out link is an
  orphan for load-bearing types (I3).
- Do not link by basename when the target is in another folder: write the path a reader
  would open. A basename-only match is not a traversable link.

## REINDEX

```sh
python3 skills/kb-search/gitmark.py index
python3 skills/kb-search/gitmark.py lint --strict
```

After a project-local install the engine is at `.dsh/skills/kb-search/gitmark.py`; use
that path in place of `skills/kb-search/gitmark.py`.

`index` rebuilds `.gitmark/index.db`; it is derived and never committed. `lint` checks
I1–I6 and I8–I10; `--strict` exits 1 when any `ERR` remains. Fix the finding, rerun, and
read the output — a clean summary is `✓ чисто`. After the index, search for the new doc
to confirm it is retrievable.

## Change the model

The type table is the vocabulary: add or remove a row in `docs/ontology.md`, then mirror
the body from the first `## ` heading into `skills/kb-curate/ontology.md` (I8). In this
repository both files are local and a divergence is an `ERR`; after a project-local
install the package copy is external and divergence is a `WARN`. Migrate docs before
removing a type; I2 names the stragglers. No new invariant is introduced: I7 (registry)
stays out of the core, and there is no required registry table or inventory command.