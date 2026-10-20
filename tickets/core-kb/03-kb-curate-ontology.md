# 03: kb-curate + ontology

**What to build:** the curation rules and the shipped ontology model: node types,
frontmatter properties, typed links, and the invariants I1–I6 and I8–I10 (I7 is out).
The same model ships in `skills/kb-curate/ontology.md` and lives in `docs/ontology.md`
for this repo; lint I8 checks that the bodies agree from the first `## ` heading.

**Blocked by:** 01 (done).

**Status:** done (2026-10-20)

- [x] `skills/kb-curate/SKILL.md` tells the agent how to CREATE / UPDATE / DEPRECATE /
      LINK / REINDEX a doc: classify, place, frontmatter, link, update the folder index.
- [x] `skills/kb-curate/ontology.md` is the shipped model; `docs/ontology.md` is this
      repo's copy; `lint --strict` passes I8 (same body from the first `## `).
- [x] The model names the core invariants I1–I6 and I8–I10, and says plainly that I7
      (registry) is out of the core.
- [x] Adding a doc with `node_type`, a body link and a folder index link passes lint;
      removing `node_type` gives I1; a broken link gives I4.
- [x] No new invariant is introduced; no registry table is required.

**What can I demo when this is done?** Add a doc to `docs/reference/`, link it from the
folder README, run `lint --strict` (clean); remove its `node_type`, run lint again (ERR
I1, exit 1).

## Evidence (2026-10-20)

- **Delivered in `118fe99`:** `skills/kb-curate/ontology.md` (105 lines; the shipped
  model), `docs/ontology.md` (119 lines; the project twin and the only I2 type
  vocabulary), `skills/kb-curate/SKILL.md` (103 lines; the five operations), the
  `docs/README.md` index bullet, and `tests/test_skill_kb_curate.py` (7 tests).
- **Model:** 11 node types in the `| node_type` table (`index`, `decision`, `plan`,
  `reference`, `runbook`, `guide`, `gotcha`, `service`, `report`, `ticket`, `schema`),
  the frontmatter field table, six typed link keys (`documents`, `depends_on`,
  `supersedes`, `relates_to`, `implemented_by`, `part_of`), and I1–I6 plus I8–I10. I7 is
  named as registry/inventory and explicitly out; no registry table, provenance, Reel or
  acceptance chord.
- **I2/I8:** `node_types(REPO)` returns exactly the 11 rows parsed from
  `docs/ontology.md`; every `node_type` in `docs/` is in the table. The body from the
  first `## ` is equal in `docs/ontology.md` and `skills/kb-curate/ontology.md` (the test
  extracts it independently), and `ontology_twin_issues(REPO) == []`; the flat-repo
  divergence path is the engine's ERR (existing engine test), the external-package path
  is WARN.
- **Tests:** `python3 -m pytest tests/ -q` → **149 passed** (142 prior + 7
  new), no Node. The new tests parse the skill contract (with a mutation probe for a
  missing operation, model, name, quote and an injected provenance line), parse the I2
  table and the exact I1–I6/I8–I10 set, assert the I8 twin, assert the repository KB has
  no lint errors, and run the demo matrix.
- **Demo matrix (`tests/…::test_demo_doc_passes_then_i1_and_i4_fail_strict`):** a temp
  KB built from the shipped ontology passes `lint --strict` (exit 0); removing
  `node_type` gives ERR I1 and exit 1; replacing the body link gives ERR I4 and exit 1.
- **Live demo in this repo:** added `docs/reference/demo-curation.md`, linked it from
  `docs/reference/README.md`, `lint --strict` → `✓ чисто` (24 files, exit 0); removed
  `node_type` → `ERR I1 docs/reference/demo-curation.md`, exit 1; restored the type and
  broke the body link → `ERR I4 … битая ссылка → missing.md`, exit 1; removed the demo
  doc, restored the README, `index` → 23 files / 106 chunks / 35 links, `lint --strict`
  → `✓ чисто` (23 files, exit 0). Logs: `.scratch/ticket-03/demo-*.log`.
- **Scope:** no engine or `kb-search` change; commit `118fe99` touches exactly five files
  (`docs/README.md`, `docs/ontology.md`, `skills/kb-curate/SKILL.md`,
  `skills/kb-curate/ontology.md`, `tests/test_skill_kb_curate.py`).

**Remaining:** ticket 04 (`init`) is next; 05 and 06 follow in order.
