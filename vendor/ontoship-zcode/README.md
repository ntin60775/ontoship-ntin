# Vendored GitMark baseline

Source: `ontoship-zcode` (`git@github.com:ntin60775/ontoship-zcode.git`), HEAD
`5528ae1`; the engine file is unchanged since `86941ab`. Licence: MIT (see `LICENSE`).

This is the **baseline**, not the deliverable. Ticket 01 copies it into
`skills/kb-search/gitmark.py` and trims it for the core.

| file | what |
|---|---|
| `gitmark.py` | the 1570-line engine baseline (index/search/lint/inventory/map/serve) |
| `tests/test_gitmark.py` | baseline tests; inventory/registry-heavy — ticket 01 drops those |
| `tests/test_lint_paths.py` | lint path-guard matrix — keep and adapt |
| `tests/test_gitmark_redact.py` | `redact_lite` matrix — keep and adapt |
| `LICENSE` | MIT, © vakovalskii and OntoShip contributors / 1cprog7 |

Not copied: the source repo's `docs/` (strict profile and history), workflows, plans, and
anything that depends on `.zcode` or on the host's agent runtime.
