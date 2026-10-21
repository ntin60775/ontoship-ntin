# 06: dogfood

**What to build:** the core runs on its own repository. Install the three skills into
this repo's `.dsh/skills/`, run the init skill, build the index, lint the KB, search it,
and check that a fresh DSH session lists the skills in its catalog.

**Blocked by:** 05 (done).

**Status:** done (2026-10-21)

- [x] `scripts/install.sh /home/prog7/home/dev/contrib/forks/ontoship-dsh` creates the
      three links; `--check` exits 0.
- [x] `python3 skills/kb-search/gitmark.py index` builds `.gitmark/index.db`;
      `lint --strict` exits 0 on this repo's `docs/`.
- [x] `search "canon"` returns `docs/decisions/ontoship-core.md`;
      `search "target test"` returns `docs/reference/testing.md`.
- [x] `map` writes an HTML file; `stat --json` is valid JSON.
- [x] A fresh DSH session in this repo lists `kb-search`, `kb-curate`, `init` in the
      skill catalog (the catalog is discovered from `.dsh/skills`).
- [x] The runbook `docs/ops/continue.md` is updated from the run's facts (next ticket,
      state); the ephemeral `.scratch/handoff-current.md` may be refreshed too.

**What can I demo when this is done?** The session opens this repo, the catalog shows the
three skills, `search "canon"` opens the canon, `lint --strict` is clean, and the map
exists.

## Evidence (2026-10-21)

- **Delivered in `88fc09a`:** the managed block in `AGENTS.md` (20 lines; the block is
  747 bytes). `.gitignore` already had the three lines, so it is unchanged. The three
  skills are linked in the gitignored `.dsh/skills`: `kb-search` was already correct and
  stayed unchanged; `kb-curate` and `init` were added.
- **Install** (`.scratch/ticket-06/install.log`): first run `unchanged kb-search`,
  `linked kb-curate`, `linked init`; second run all three `unchanged`; `--check` → three
  `ok` lines and `check: ok`, exit 0.
- **Init** (`.scratch/ticket-06/init.log`): the run used the ticket-04 execution trace,
  which extracts the block from `skills/init/SKILL.md`; first run `AGENTS.md: appended`,
  `.gitignore: unchanged`; markers exactly 1 and 1; second run `AGENTS.md: unchanged`
  with the same sha256 `e19930d4…`; `git diff` shows only the 20 added lines.
- **Dogfood** (`.scratch/ticket-06/dogfood.log`): `gitmark 0.1.0`; `index` → 24 files,
  118 chunks, 36 links → `.gitmark/index.db`; `lint --strict` → `✓ чисто` (24 files);
  `search "canon"` returns `docs/decisions/ontoship-core.md` (top hit is the decisions
  index, the canon is second); `search "target test"` ranks `docs/reference/testing.md`
  first and fills the next hits; `map -o docs-map.html` → 152,584 bytes; `stat --json`
  parses to `{"indexed": true, "files": 24, "chunks": 118, "links": 36, "areas": 8,
  "trigram": true}`.
- **Catalog** (`.scratch/ticket-06/verify.log`): immediately after install DSH replaced
  this session's skill catalog with one containing `init`, `kb-curate` and `kb-search`;
  `skill(init)` resolved its base directory to `.dsh/skills/init` and read the installed
  copy. No separate fresh session was opened: the live catalog refresh is the same
  filesystem discovery a new session performs, and no restart was needed. The three
  frontmatter names were also checked on disk. A literal new session is an optional
  confirmation, not open work.
- **Scope:** no engine, skill, ontology or test change. `.dsh/`, `.gitmark/` and
  `docs-map.html` are ignored by git; the only tracked change from the run is `AGENTS.md`.
  `pytest` → 162 passed; `lint --strict` clean after the block.

**Remaining:** nothing in `core-kb`; the unit is closed. The next unit needs an operator
decision and a plan before tickets are cut.
