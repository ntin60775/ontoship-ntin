# 01: Engine — vendor, trim, extract lint helpers

**What to build:** a vendored, trimmed GitMark engine in `skills/kb-search/gitmark.py`
that indexes and searches the KB, lints the core ontology, renders the map, and reports
stats — one auditable Python-stdlib file, no registries.

**Blocked by:** None (can start immediately).

**Status:** ready-for-agent

- [ ] `skills/kb-search/gitmark.py` exists as one file, based on the vendored baseline
      `vendor/ontoship-zcode/gitmark.py` (MIT, attribution kept), with `.dsh` in
      `EXCLUDE_DIRS`; `PKG_ROOT` works both in this repo and in a copy install under
      `.dsh/`.
- [ ] Commands `index`, `search`, `lint`, `map`, `stat`, `version` work; `inventory` and
      `serve` are absent.
- [ ] `lint` checks I1–I6 and I8–I10; I7 is absent; `--strict` exits 1 on any ERR and 0
      on a clean KB.
- [ ] `cmd_lint` is an orchestration of extracted helpers (≤ 80 lines): path guards, link
      graph, per-doc checks, global checks. Behaviour of the remaining invariants is
      unchanged.
- [ ] `tests/` covers the trimmed engine: index/search, gitignore fallback, lint path
      guards, I1/I4, map/stat; the suite runs with `python3 -m pytest tests/ -q` and does
      not require `node`. Adapt the baseline tests from `vendor/ontoship-zcode/tests/`;
      inventory/registry tests are gone.
- [ ] No new invariants, no new registry, no `file:line` anchors in the code comments
      that would rot.

**What can I demo when this is done?** In a temp repo with two docs and one broken link:
`index` writes `.gitmark/index.db`; `search` finds a doc; `lint --strict` exits 1 on the
broken link; fixing the link makes it exit 0; `map` writes HTML; `stat --json` is valid
JSON. Then the same on this repository's own `docs/`.
