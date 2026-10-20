# 04: init skill

**What to build:** the `init` skill: create or update the managed block in a project's
`AGENTS.md` and add the `.gitignore` lines the KB requires. Idempotent; touches nothing
outside its own block.

**Blocked by:** 01 (done); follows 03 (done).

**Status:** done (2026-10-21)

- [x] `skills/init/SKILL.md` has DSH frontmatter and describes the managed block
      (`<!-- BEGIN ontoship -->` … `<!-- END ontoship -->`), its content (entry point,
      KB index, maintain commands), and the `.gitignore` lines (`.gitmark/`, `*-map.html`,
      `.scratch/`).
- [x] Running init twice makes no change (second run: no diff).
- [x] A project `AGENTS.md` without the block gets it; an existing block is replaced only
      inside the markers; text outside the markers is untouched.
- [x] No registry, no provenance, no writes outside `AGENTS.md` and `.gitignore`.
- [x] The skill can run on a temp repo and on this repo.

**What can I demo when this is done?** In a temp repo: run init, show the block in
`AGENTS.md` and the three `.gitignore` lines; run init again, show `git diff` empty.

## Evidence (2026-10-21)

- **Delivered in `90f0846`:** `skills/init/SKILL.md` (131 lines): DSH frontmatter
  (`name: init`, a 353-character quoted description), the two files it owns, the five
  marker cases, the verbatim block, the `.gitignore` rules, verification and report.
  `tests/test_skill_init.py` (4 tests) pins the artifact and probes the check. No engine,
  `kb-search`, `kb-curate` or `docs/` change.
- **DSH facts that shaped it** (read from `deepseek-harness/packages/context/agent-instructions`):
  candidates `AGENTS.md`/`CLAUDE.md`; project root = the first ancestor with `.git`; files
  load from that root down to the cwd; user-global `~/.dsh/AGENTS.md` and
  `~/.agents/AGENTS.md`; a 64 KiB instruction budget. The block is 747 bytes and points
  at the installed engine path `.dsh/skills/kb-search/gitmark.py` (ticket 05's layout).
- **Block:** entry point (`docs/README.md` and folder indexes), the `kb-search`/`kb-curate`
  skills, the three maintain commands (`index`, `lint --strict`, `map`), and the
  derived/ephemeral rule (`.gitmark/`, `*-map.html`, `.scratch/`). The contract test pins
  the block byte-for-byte against an independent literal and requires exactly one marker
  pair.
- **Temp matrix** (`.scratch/ticket-04/run.log`; the driver extracts the shipped block, so
  the run exercises the artifact): **A** empty repo → exactly `AGENTS.md` + `.gitignore`,
  the block and the three lines; second run → `git status` empty and `git diff` empty.
  **B** existing project text → appended after one blank line, every existing line
  preserved. **C** old block with text before/after → replaced only inside the markers,
  outside bytes preserved, `[WARN]`. **D** reversed markers → `[FAIL]`, both files
  byte-identical. **E** partial `.gitignore` with no trailing newline and a comment → only
  `*-map.html` and `.scratch/` appended, comment and order kept. **F** CRLF file → outside
  bytes preserved, block written with CRLF, second run unchanged.
- **This repo:** init appended 20 lines to `AGENTS.md` (`.gitignore` already had the three
  lines); the second run was byte-identical (`sha256 cb98a056…`), and the change was
  reverted — ticket 06 adopts the block during dogfood. Log `repo-run.log`, diff
  `repo.diff`.
- **Tests / lint:** `python3 -m pytest tests/ -q` → **153 passed** (149 prior + 4);
  `lint --strict` → exit 0 (24 files). The mutation probe rejects a missing END marker, a
  renamed `*-map.html` rule, an injected registry/`commands.md`, a missing `name`, an
  unquoted description and an edited block.
- **Scope:** no registry, provenance, Reel, acceptance chord, `inventory` or `serve`; no
  write outside `AGENTS.md` and `.gitignore` (case A checks the directory); no `scripts/`
  yet (ticket 05).

**Remaining:** ticket 05 (`scripts/install.sh`) is next; 06 follows.