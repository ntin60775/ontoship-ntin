# 03: kb-curate + ontology

**What to build:** the curation rules and the shipped ontology model: node types,
frontmatter properties, typed links, and the invariants I1–I6 and I8–I10 (I7 is out).
The same model ships in `skills/kb-curate/ontology.md` and lives in `docs/ontology.md`
for this repo; lint I8 checks that the bodies agree from the first `## ` heading.

**Blocked by:** 01.

**Status:** blocked

- [ ] `skills/kb-curate/SKILL.md` tells the agent how to CREATE / UPDATE / DEPRECATE /
      LINK / REINDEX a doc: classify, place, frontmatter, link, update the folder index.
- [ ] `skills/kb-curate/ontology.md` is the shipped model; `docs/ontology.md` is this
      repo's copy; `lint --strict` passes I8 (same body from the first `## `).
- [ ] The model names the core invariants I1–I6 and I8–I10, and says plainly that I7
      (registry) is out of the core.
- [ ] Adding a doc with `node_type`, a body link and a folder index link passes lint;
      removing `node_type` gives I1; a broken link gives I4.
- [ ] No new invariant is introduced; no registry table is required.

**What can I demo when this is done?** Add a doc to `docs/reference/`, link it from the
folder README, run `lint --strict` (clean); remove its `node_type`, run lint again (ERR
I1, exit 1).
