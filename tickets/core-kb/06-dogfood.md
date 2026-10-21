# 06: dogfood

**What to build:** the core runs on its own repository. Install the three skills into
this repo's `.dsh/skills/`, run the init skill, build the index, lint the KB, search it,
and check that a fresh DSH session lists the skills in its catalog.

**Blocked by:** 05 (done).

**Status:** ready-for-agent

- [ ] `scripts/install.sh /home/prog7/home/dev/contrib/forks/ontoship-dsh` creates the
      three links; `--check` exits 0.
- [ ] `python3 skills/kb-search/gitmark.py index` builds `.gitmark/index.db`;
      `lint --strict` exits 0 on this repo's `docs/`.
- [ ] `search "canon"` returns `docs/decisions/ontoship-core.md`;
      `search "target test"` returns `docs/reference/testing.md`.
- [ ] `map` writes an HTML file; `stat --json` is valid JSON.
- [ ] A fresh DSH session in this repo lists `kb-search`, `kb-curate`, `init` in the
      skill catalog (the catalog is discovered from `.dsh/skills`).
- [ ] The runbook `docs/ops/continue.md` is updated from the run's facts (next ticket,
      state); the ephemeral `.scratch/handoff-current.md` may be refreshed too.

**What can I demo when this is done?** The session opens this repo, the catalog shows the
three skills, `search "canon"` opens the canon, `lint --strict` is clean, and the map
exists.
