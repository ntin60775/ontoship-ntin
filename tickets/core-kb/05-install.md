# 05: install channel

**What to build:** `scripts/install.sh` — project-local install of the core. It creates
`<project>/.dsh/skills/{kb-search,kb-curate,init}` as symlinks to this repo by default
(`--copy` for a detached install), and `--check` reports drift. It links the skills; it
does not run the init skill.

**Blocked by:** 02, 03, 04 (all done; the skill directories exist).

**Status:** ready-for-agent

- [ ] `scripts/install.sh <project>` creates `.dsh/skills/` and one symlink per skill to
      `<repo>/skills/<name>`; the target layout is exactly what DSH discovers (rank 100).
- [ ] A second run makes no change (idempotent); `--check` exits 0 when all links point
      at this repo and names each missing/wrong link with exit 1 otherwise.
- [ ] `--copy` copies the skill directories instead of linking; `--check` accepts either
      a correct symlink or a correct copy.
- [ ] No writes outside `<project>/.dsh/skills`; no `.zcode`, no global install, no
      Playwright/browser dependency.
- [ ] A test covers: fresh install, idempotent second run, `--check` clean, remove a link
      → `--check` names it and exits 1, `--copy` produces real directories.

**What can I demo when this is done?** Install into a temp repo; `ls -l .dsh/skills`
shows three links; run again (no change); `--check` exits 0; delete one link, `--check`
exits 1 and names it; `--copy` into another temp repo produces three real directories.
