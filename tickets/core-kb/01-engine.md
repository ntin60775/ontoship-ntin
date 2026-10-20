# 01: Engine — vendor, trim, extract lint helpers

**What to build:** a vendored, trimmed GitMark engine in `skills/kb-search/gitmark.py`
that indexes and searches the KB, lints the core ontology, renders the map, and reports
stats — one auditable Python-stdlib file, no registries.

**Blocked by:** None (can start immediately).

**Status:** done (2026-10-20)

- [x] `skills/kb-search/gitmark.py` exists as one file, based on the vendored baseline
      `vendor/ontoship-zcode/gitmark.py` (MIT, attribution kept), with `.dsh` and
      `.zcode` in `EXCLUDE_DIRS`; `PKG_ROOT` works both in this repo and in copy
      installs under `.dsh/` and `.zcode/`.
- [x] Commands `index`, `search`, `lint`, `map`, `stat`, `version` work; `inventory` and
      `serve` are absent.
- [x] `lint` checks I1–I6 and I8–I10; I7 is absent; `--strict` exits 1 on any ERR and 0
      on a clean KB.
- [x] `cmd_lint` is an orchestration of extracted helpers (28 lines): path guards, link
      graph, per-doc checks, global checks. Behaviour of the remaining invariants is
      unchanged.
- [x] `tests/` covers the trimmed engine: index/search, gitignore fallback, lint path
      guards, I1/I4, map/stat; the suite runs with `python3 -m pytest tests/ -q` and does
      not require `node`. Baseline tests adapted; inventory/registry tests are gone.
- [x] No new invariants, no new registry, no `file:line` anchors in the code comments
      that would rot.

**What can I demo when this is done?** In a temp repo with two docs and one broken link:
`index` writes `.gitmark/index.db`; `search` finds a doc; `lint --strict` exits 1 on the
broken link; fixing the link makes it exit 0; `map` writes HTML; `stat --json` is valid
JSON. Then the same on this repository's own `docs/`.

## Evidence (2026-10-20)

- **Shape:** `skills/kb-search/gitmark.py` is 1302 lines; `cmd_lint` is 28 lines and calls
  `_lint_path_guards`, `_lint_link_graph`, `_lint_readme_index`, `_lint_per_doc` and
  `_lint_global`. The file carries the ontoship-zcode MIT attribution.
- **Trim:** `inventory`, `serve`, `inventory_issues` and I7 are absent from the module and
  from `--help`; `.dsh` and `.zcode` are in `EXCLUDE_DIRS`; `PKG_ROOT` resolves to the repo
  root here and to `.dsh` / `.zcode` in copy installs (all exercised by tests).
- **Tests:** `python3 -m pytest tests/ -q` → **131 passed in 1.21 s**, stdlib + pytest,
  no Node. Every test names `spec:` or `invariant:`; the path matrix and the redact matrix
  each carry a mutation probe.
- **Differential against the vendor baseline:** on a KB exercising I1/I2/I3/I4/I5/I6/I9/I10,
  the trimmed `cmd_lint` returns the same issues and `checked` count as the baseline after
  dropping I7, for both a full run and a path-selected run; both guards refuse with the
  same messages.
- **Live mutation probes (engine restored byte-for-byte afterward):**
  - path guards bypassed → `tests/test_lint_paths.py`: **20 failed, 8 passed** (including
    the silent-clean probe);
  - `.dsh` or `.zcode` dropped from `EXCLUDE_DIRS` → the install-roots exclusion test fails;
  - `redact_lite` dropped from the lint print → redacted-output E2E fails (secret leaks);
  - `fs_resolve` forced to succeed → **6 I4/fs_resolve tests fail**.
- **Temp demo:** 3-file KB: `index` writes `.gitmark/index.db`; `search platypus` finds the
  note; broken link → `ERR I4`, `lint --strict` exit 1; fixed link → `✓ чисто`, exit 0;
  `map` writes HTML; `stat --json` is valid JSON.
- **This repo:** `index` → 19 files, 67 chunks, 34 links; `lint --strict` → exit 0
  (`✓ чисто`); `map` → 19 files, 34 refs, 0 unreached; `stat --json` valid.
- **Not yet covered:** I8 against a real `skills/kb-curate/ontology.md` waits for ticket
  03 (synthetic I8 tests pass now); full dogfood is ticket 06. No browser was needed.

**Remaining:** ticket 02 (`kb-search` SKILL.md) follows.