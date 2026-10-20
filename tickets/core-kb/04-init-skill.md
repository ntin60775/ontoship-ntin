# 04: init skill

**What to build:** the `init` skill: create or update the managed block in a project's
`AGENTS.md` and add the `.gitignore` lines the KB requires. Idempotent; touches nothing
outside its own block.

**Blocked by:** 01 (done); follows 03 (done).

**Status:** ready-for-agent

- [ ] `skills/init/SKILL.md` has DSH frontmatter and describes the managed block
      (`<!-- BEGIN ontoship -->` … `<!-- END ontoship -->`), its content (entry point,
      KB index, maintain commands), and the `.gitignore` lines (`.gitmark/`, `*-map.html`,
      `.scratch/`).
- [ ] Running init twice makes no change (second run: no diff).
- [ ] A project `AGENTS.md` without the block gets it; an existing block is replaced only
      inside the markers; text outside the markers is untouched.
- [ ] No registry, no provenance, no writes outside `AGENTS.md` and `.gitignore`.
- [ ] The skill can run on a temp repo and on this repo.

**What can I demo when this is done?** In a temp repo: run init, show the block in
`AGENTS.md` and the three `.gitignore` lines; run init again, show `git diff` empty.
