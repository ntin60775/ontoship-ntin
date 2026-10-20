# 02: kb-search skill

**What to build:** the user-facing `kb-search` skill: how an agent searches the KB
instead of grepping, when to index, how to read `search` results, and the
search-before-writing discipline. It wraps the engine from ticket 01.

**Blocked by:** 01 (implemented; 01 changes may still be uncommitted).

**Status:** ready-for-agent

- [ ] `skills/kb-search/SKILL.md` has DSH frontmatter (`name`, `description`; the body
      says when to use it: find where something is documented, before reading files at
      random, before writing a new doc).
- [ ] The body names the commands (`index`, `search`, `map`, `stat`, `version`), the
      `--json` contract, and the `.gitmark/` derived-artifact rule. No `inventory`, no
      `serve`, no registry.
- [ ] It degrades honestly: no index → say "build the index" and give the command; no
      hits → say so; never invent a doc.
- [ ] It fits the core: no provenance, no Reel, no acceptance chord.

**What can I demo when this is done?** A fresh session in this repo asks the skill to
find the canon; it runs `search "canon"` and returns `docs/decisions/ontoship-core.md`
with a snippet.
