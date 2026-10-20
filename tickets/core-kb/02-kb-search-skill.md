# 02: kb-search skill

**What to build:** the user-facing `kb-search` skill: how an agent searches the KB
instead of grepping, when to index, how to read `search` results, and the
search-before-writing discipline. It wraps the engine from ticket 01.

**Blocked by:** 01 (done).

**Status:** done (2026-10-20)

- [x] `skills/kb-search/SKILL.md` has DSH frontmatter (`name`, `description`; the body
      says when to use it: find where something is documented, before reading files at
      random, before writing a new doc).
- [x] The body names the commands (`index`, `search`, `map`, `stat`, `version`), the
      `--json` contract, and the `.gitmark/` derived-artifact rule. No `inventory`, no
      `serve`, no registry.
- [x] It degrades honestly: no index → say "build the index" and give the command; no
      hits → say so; never invent a doc.
- [x] It fits the core: no provenance, no Reel, no acceptance chord.

**What can I demo when this is done?** A fresh session in this repo asks the skill to
find the canon; it runs `search "canon"` and returns `docs/decisions/ontoship-core.md`
with a snippet.

## Evidence (2026-10-20)

- **Delivered:** `skills/kb-search/SKILL.md` (142 lines) is the user-facing wrapper around
  the ticket-01 engine. Body sections: when to use, run the engine, the five commands,
  how to search, honest degradation, search before writing, and `.gitmark/` as derived.
- **Frontmatter:** `name: kb-search` (kebab-case, matches the bundle directory) and a
  328-character quoted `description` (DSH catalog cap 500). PyYAML parses it; DSH
  discovered the skill and listed `kb-search` in the session catalog after the
  project-local `.dsh/skills/kb-search` symlink appeared.
- **Contract:** `tests/test_skill_kb_search.py` — 11 tests: discoverable bundle and
  frontmatter, the five commands, `--json`, `.gitmark/`, the honest-degradation phrases,
  the six forbidden entities (`inventory`, `serve`, `registry`, `provenance`, `reel`,
  `acceptance chord`), and the description-with-`': '` YAML trap.
- **Mutation probe:** the contract checker rejects a missing `map` command, an injected
  `inventory`, a missing `name`, and an unquoted description. The check can fail.
- **Suite / lint:** `python3 -m pytest tests/ -q` → **142 passed in 1.26 s** (131 engine +
  11 skill), stdlib + pytest, no Node. `lint --strict` → exit 0 (`✓ чисто`, 20 files);
  `index` → 20 files, 84 chunks, 34 links.
- **Degradation probe (temp KB):** without an index, `search` exits 1 with
  `Индекс не найден — запусти gitmark index`; `stat --json` → `{"indexed": false}`.
  After `index`, `search xyzzy` prints `ничего не найдено` and exits 0.
- **Fresh-session demo:** a subagent with no conversation context reported `kb-search`
  in its catalog, loaded it with the `skill` tool, ran
  `python3 skills/kb-search/gitmark.py search "canon"`, selected
  `docs/decisions/ontoship-core.md` over the `docs/decisions/README.md` index, and
  returned the snippet for `docs/decisions/ontoship-core.md:12` (`# OntoShip core — the
  canon …`). It opened the file to confirm and used no grep/find/rg.
- **Scope:** the demo used the gitignored project-local install root
  `.dsh/skills/kb-search` (a symlink); `scripts/install.sh` remains ticket 05.
  `kb-curate`/`init` are not built yet. No browser was needed.

**Remaining:** ticket 03 (`kb-curate` + ontology) follows; 04–06 follow in order.
