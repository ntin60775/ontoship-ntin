---
node_type: runbook
title: Continue development from this repo
service: _platform
status: active
updated: 2026-10-21
tags: [runbook, start, handoff, core-kb]
links:
  relates_to: [../README.md, ../decisions/ontoship-core.md, ../plans/core-kb.md, ../../tickets/README.md]
---

# Continue development from this repo

This is the **canonical start**. The session snapshot `.scratch/handoff-current.md` is
ephemeral; use this runbook and the tickets, not the snapshot, as the source of truth.

## Where we are

Repo: `/home/prog7/home/dev/contrib/forks/ontoship-dsh` (git). It is
self-contained: the engine baseline is vendored, the tickets are tracked, the plan is
approved.

| commit | what |
|---|---|
| `cfad6e9` | skeleton, canon, sources |
| `31e11fb` | plan `core-kb` |
| `f1cd8bf` | testing amendment: target tests, ESEM 2026 |
| `030c81a` | plan approved (`active`), ticket order |
| `b148d1f` | self-contained start: vendor baseline, tickets, this runbook |
| `eb678d8` | ticket 01: trimmed engine, 131 tests |
| `e5a2ced` | ticket 02 start prompt |
| `4b10f95` | ticket 02: `kb-search` SKILL.md and its contract test |
| `f189889` | docs: ticket 02 closed; ticket 03 ready |
| `054279d` | docs(ops): sharpen the ticket 03 start prompt |
| `118fe99` | ticket 03: `kb-curate` skill, ontology model, 149 tests |
| `6c1cce6` | docs(ops): close ticket 03, hand off to 04 |
| `90f0846` | ticket 04: `init` skill and its contract test |
| `dce10f0` | ticket 05: `scripts/install.sh` and its contract test |
| `88fc09a` | ticket 06: dogfood — the managed block in `AGENTS.md` |

Tickets 01–06 are **implemented and committed**; the first unit `core-kb` is complete and
dogfooded. `skills/kb-search/gitmark.py` (1302 lines), the three skills, `scripts/install.sh`
and `tests/` (162 passed) are in place; `lint --strict` is clean. This repo's `AGENTS.md`
now carries the 747-byte managed block, and `.dsh/skills` has the three links with
`--check` 0. `index` = 24 files / 119 chunks / 36 links; `search "canon"` and
`search "target test"` return the expected docs; `map` and `stat --json` work. There is
**no next ticket**: the next unit needs an operator decision and a plan first.

## Where things live

- `AGENTS.md` — the entry point; it carries the managed ontoship block (ticket 06) that
  points at the installed engine and the maintain commands.
- `docs/decisions/ontoship-core.md` — the canon (3 artefacts, 3 phases, 2 separations,
  1 quality rule; spec durable / tickets ephemeral).
- `docs/reference/testing.md` — spec / invariant / target tests, quality bar, agentic loop.
- `docs/reference/sources.md` — OntoShip (vakovalskii), Pocock, ESEM 2026; the 53%
  correction.
- `docs/plans/core-kb.md` — the approved spec of the first unit.
- `docs/ontology.md` — this repo's ontology copy and the only I2 type vocabulary; I8
  compares its body from the first `## ` with `skills/kb-curate/ontology.md`.
- `tickets/core-kb/01…06.md` — the execution tickets (local tracker, not KB).
- `vendor/ontoship-zcode/` — the engine baseline (MIT) and its baseline tests; ticket 01
  copies and trims it into `skills/kb-search/`.
- `skills/kb-search/` — the trimmed engine (ticket 01) and the user-facing `SKILL.md`
  (ticket 02): `index`, `search`, `lint`, `map`, `stat`, `version`; no
  `inventory`/`serve`/I7. Harness-agnostic CLI (stdlib only); ignores both `.dsh` and
  `.zcode` install roots.
- `skills/kb-curate/` — the shipped ontology model `ontology.md` and the curation
  `SKILL.md` (ticket 03): CREATE / UPDATE / DEPRECATE / LINK / REINDEX; I7 stays out.
- `skills/init/` — the `init` `SKILL.md` (ticket 04): the managed block
  (`<!-- BEGIN ontoship -->` … `<!-- END ontoship -->`), its five marker cases, and the
  three `.gitignore` lines. Idempotent; writes only `AGENTS.md` and `.gitignore`.
- `scripts/install.sh` — the project-local install (ticket 05): default symlinks,
  `--copy` a detached copy, `--check` drift (exit 0/1, names each skill); idempotent;
  writes only `<project>/.dsh/skills`; does not run init.
- `tests/` — engine, skill-contract and install tests; run
  `python3 -m pytest tests/ -q` (162 passed; stdlib + pytest, no Node).
- `.dsh/skills/` — the gitignored project-local install, dogfooded by ticket 06: three
  links (`kb-search`, `kb-curate`, `init`), `scripts/install.sh --check` exits 0.
- `.scratch/handoff-current.md` — the previous session snapshot (ephemeral).

## Ticket order

**01 engine → 02 kb-search → 03 kb-curate/ontology → 04 init → 05 install → 06 dogfood.**

All six are done; `core-kb` is closed. There is no ticket 07: the next unit must be
planned, approved by the operator and cut into tickets before code starts. Do not invent
a ticket or reopen the canon.

## Environment facts

- DSH runs from `/home/prog7/home/dev/contrib/forks/deepseek-harness` under Node
  `/home/prog7/.local/share/node-lts/bin/node`; web PID in `/run/user/1000/dsh-web.pid`,
  log `/run/user/1000/dsh-web.log`.
- DSH skill roots: `<project>/.dsh/skills` (rank 100), `<project>/.agents/skills` (200),
  `~/.dsh/skills` (400). A skill is `<name>/SKILL.md` or flat `<name>.md`; nested
  `**/SKILL.md` is not discovered. A directory symlink is stat'ed and followed (a broken
  link is ignored), so an install may link a bundle. Frontmatter needs `name` and
  `description`; `user-invocable` / `disable-model-invocation` are supported. The
  filesystem provider watches the roots: after ticket 06's install the running session's
  catalog gained `init`, `kb-curate` and `kb-search` without a restart.
- **Playwright MCP:** configured in `~/.dsh/profiles/web/cordis.patch.yml` (backup
  `cordis.patch.yml.bak-20261019`): `@deepseek-ai/dsh-browser-use` +
  `@deepseek-ai/dsh-experimental-browser-use-playwright-mcp` (`mode: launch`,
  `headless: true`, `executablePath: /usr/bin/chromium`). The running DSH predates the
  patch: restart it (`kill $(cat /run/user/1000/dsh-web.pid)` then `~/.local/bin/dsh-web`)
  to get `mcp__playwright-mcp__*` in new sessions. Tickets 01–06 did not need the browser;
  do not fake E2E if it is absent.
- Python 3.13, stdlib only for the engine; `pytest` is available. `node/npm/npx` are not
  in PATH; the engine must not need Node.

## Start prompt

```text
Мы продолжаем работу в /home/prog7/home/dev/contrib/forks/ontoship-dsh — чистый
OntoShip-core (DSH). Юнит core-kb (тикеты 01–06) завершён, закоммичен и dogfooded:
движок, три скилла (kb-search, kb-curate, init), scripts/install.sh, 162 passed,
lint --strict чистый; AGENTS.md содержит ontoship-блок, .dsh/skills — три ссылки,
--check 0.

Прочитай по порядку: AGENTS.md, docs/ops/continue.md,
docs/decisions/ontoship-core.md, docs/reference/testing.md, docs/reference/sources.md,
docs/plans/core-kb.md, tickets/README.md, tickets/core-kb/06-dogfood.md.

Тикета 07 нет. Не придумывай следующий тикет и не переоткрывай канон: следующий юнит
выбирает оператор. Если он называет workflow-скиллы (grilling, to-tickets, ship,
testing), сначала нужен утверждённый план; grilling ещё не реализован — назови это,
не начинай код без плана.

Если оператор просит проверить состояние: scripts/install.sh --check "$PWD" → 0;
python3 .dsh/skills/kb-search/gitmark.py index; lint --strict → 0;
search "canon" → docs/decisions/ontoship-core.md; search "target test" →
docs/reference/testing.md; stat --json валиден; map пишет docs-map.html (игнорируется).
.dsh/, .gitmark/, .scratch/ и *-map.html не коммитятся.

В конце отчёт фактами: что сделано, чем доказано, что осталось. Один тикет за прогон;
при реальном конфликте останови и спроси оператора.
```

## Rules of continuation

- One ticket per run; do not batch. Research before writing.
- Evidence: a test that proves a spec clause, guards an invariant or reproduces a real
  failure; a new matrix gets a negative/mutation probe; read the run log.
- No registries, inventory, provenance line, Reel, acceptance chord, issue counter, or
  automatic grill → tickets chain.
- Do not copy the `ontoship-zcode` `docs/`; it is the strict profile/history.
- Update this runbook with the next state at the end of a run; keep it short.
