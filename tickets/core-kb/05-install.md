# 05: install channel

**What to build:** `scripts/install.sh` — project-local install of the core. It creates
`<project>/.dsh/skills/{kb-search,kb-curate,init}` as symlinks to this repo by default
(`--copy` for a detached install), and `--check` reports drift. It links the skills; it
does not run the init skill.

**Blocked by:** 02, 03, 04 (all done; the skill directories exist).

**Status:** done (2026-10-21)

- [x] `scripts/install.sh <project>` creates `.dsh/skills/` and one symlink per skill to
      `<repo>/skills/<name>`; the target layout is exactly what DSH discovers (rank 100).
- [x] A second run makes no change (idempotent); `--check` exits 0 when all links point
      at this repo and names each missing/wrong link with exit 1 otherwise.
- [x] `--copy` copies the skill directories instead of linking; `--check` accepts either
      a correct symlink or a correct copy.
- [x] No writes outside `<project>/.dsh/skills`; no `.zcode`, no global install, no
      Playwright/browser dependency.
- [x] A test covers: fresh install, idempotent second run, `--check` clean, remove a link
      → `--check` names it and exits 1, `--copy` produces real directories.

**What can I demo when this is done?** Install into a temp repo; `ls -l .dsh/skills`
shows three links; run again (no change); `--check` exits 0; delete one link, `--check`
exits 1 and names it; `--copy` into another temp repo produces three real directories.

## Evidence (2026-10-21)

- **Delivered in `dce10f0`:** `scripts/install.sh` (209 lines, executable) and
  `tests/test_install.py` (9 tests). No engine, skill, ontology or KB change.
- **DSH discovery facts** (read from
  `deepseek-harness/packages/skill/skill-filesystem/src/index.ts`): the project root is
  the nearest ancestor with `.git`; `<project>/.dsh/skills` is rank 100; a skill is a
  directory bundle `<root>/<name>/SKILL.md` (or a flat `<root>/<name>.md`, not used here);
  a directory symlink is stat'ed and followed, a broken link is ignored, and the
  resource base stays the link path. The install layout is exactly that bundle layout.
- **Behaviour:** default install writes one absolute symlink per skill; `--copy` copies
  the bundle and drops `__pycache__`/`*.pyc`; `--check` accepts a symlink that resolves
  to this repo (absolute or relative) or a directory whose files equal the source
  (`diff -rq -x __pycache__ -x '*.pyc'`), and names each missing/wrong entry with exit 1.
  Preflight refuses to replace a non-symlink in link mode or a differing copy in copy
  mode, and aborts the whole run before writing, so there is no half install. `--check`
  writes nothing.
- **Demo** (`.scratch/ticket-05/demo.log`): fresh temp repo → three links, second run
  `unchanged`, `--check` 0; remove `kb-curate` → `drift: kb-curate: missing`, exit 1;
  `--copy` into another temp repo → three real directories, `--check` 0.
- **Tests / lint:** `python3 -m pytest tests/ -q` → **162 passed** (153 prior + 9);
  `lint --strict` → exit 0 (24 files); logs `.scratch/ticket-05/`. Mutation probes: a
  wrong symlink target, a missing link, an edited copy and a deleted copy all fail with
  the skill named. The idempotence check compares inode, mtime, content and link target,
  not just paths.
- **Scope:** writes only `<project>/.dsh/skills` (plus its `.dsh` parent); no `.zcode`,
  no `$HOME` write, no global install, no browser/Playwright; init is not run.

**Remaining:** ticket 06 (dogfood) is next.
