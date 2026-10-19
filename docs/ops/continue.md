---
node_type: runbook
title: Continue development from this repo
service: _platform
status: active
updated: 2026-10-19
tags: [runbook, start, handoff, core-kb]
links:
  relates_to: [../README.md, ../decisions/ontoship-core.md, ../plans/core-kb.md, ../../tickets/README.md]
---

# Continue development from this repo

This is the **canonical start**. The session snapshot `.scratch/handoff-current.md` is
ephemeral; use this runbook and the tickets, not the snapshot, as the source of truth.

## Where we are

Repo: `/home/prog7/home/dev/contrib/forks/ontoship-dsh` (git, clean). It is
self-contained: the engine baseline is vendored, the tickets are tracked, the plan is
approved.

| commit | what |
|---|---|
| `cfad6e9` | skeleton, canon, sources |
| `31e11fb` | plan `core-kb` |
| `f1cd8bf` | testing amendment: target tests, ESEM 2026 |
| `030c81a` | plan approved (`active`), ticket order |
| `b148d1f` | self-contained start: vendor baseline, tickets, this runbook |

Nothing is implemented yet: no `skills/`, no `tests/`, no `scripts/`. Ticket 01 is the
first deliverable.

## Where things live

- `docs/decisions/ontoship-core.md` — the canon (3 artefacts, 3 phases, 2 separations,
  1 quality rule; spec durable / tickets ephemeral).
- `docs/reference/testing.md` — spec / invariant / target tests, quality bar, agentic loop.
- `docs/reference/sources.md` — OntoShip (vakovalskii), Pocock, ESEM 2026; the 53%
  correction.
- `docs/plans/core-kb.md` — the approved spec of the first unit.
- `tickets/core-kb/01…06.md` — the execution tickets (local tracker, not KB).
- `vendor/ontoship-zcode/` — the engine baseline (MIT) and its baseline tests; ticket 01
  copies and trims it into `skills/kb-search/`.
- `.scratch/handoff-current.md` — the previous session snapshot (ephemeral).

## Ticket order

**01 engine → 02 kb-search → 03 kb-curate/ontology → 04 init → 05 install → 06 dogfood.**

01 is `ready-for-agent`; the rest are blocked by their predecessors. Install comes after
the skills exist; it links them, it does not run init.

## Environment facts

- DSH runs from `/home/prog7/home/dev/contrib/forks/deepseek-harness` under Node
  `/home/prog7/.local/share/node-lts/bin/node`; web PID in `/run/user/1000/dsh-web.pid`,
  log `/run/user/1000/dsh-web.log`.
- DSH skill roots: `<project>/.dsh/skills` (rank 100), `<project>/.agents/skills` (200),
  `~/.dsh/skills` (400). A skill is `<name>/SKILL.md` or flat `<name>.md`; nested
  `**/SKILL.md` is not discovered. Frontmatter needs `name` and `description`;
  `user-invocable` / `disable-model-invocation` are supported.
- **Playwright MCP:** configured in `~/.dsh/profiles/web/cordis.patch.yml` (backup
  `cordis.patch.yml.bak-20261019`): `@deepseek-ai/dsh-browser-use` +
  `@deepseek-ai/dsh-experimental-browser-use-playwright-mcp` (`mode: launch`,
  `headless: true`, `executablePath: /usr/bin/chromium`). The running DSH predates the
  patch: restart it (`kill $(cat /run/user/1000/dsh-web.pid)` then `~/.local/bin/dsh-web`)
  to get `mcp__playwright-mcp__*` in new sessions. Ticket 01 does not need the browser;
  do not fake E2E if it is absent.
- Python 3.13, stdlib only for the engine; `pytest` is available. `node/npm/npx` are not
  in PATH; the engine must not need Node.

## Start prompt

```text
Мы начинаем работу в /home/prog7/home/dev/contrib/forks/ontoship-dsh — это чистый
OntoShip-core (DSH). План core-kb утверждён, репозиторий самодостаточен.

Прочитай по порядку: AGENTS.md, docs/ops/continue.md,
docs/decisions/ontoship-core.md, docs/reference/testing.md, docs/reference/sources.md,
docs/plans/core-kb.md, tickets/README.md, tickets/core-kb/01-engine.md.

Начни с тикета 01 (движок). Базовая версия уже вендорена в
vendor/ontoship-zcode/gitmark.py (MIT) вместе с тестами; скопируй её в
skills/kb-search/gitmark.py, вырежи inventory/serve/I7, разбери cmd_lint на helpers
внутри файла (≤80 строк), добавь .dsh в EXCLUDE_DIRS, адаптируй тесты из
vendor/ontoship-zcode/tests/ в tests/ (без node). Один файл; без реестров,
провенанса, Reel.

Сначала исследуй, потом реализуй. Веди TodoWrite по шагам тикета. Тесты —
spec/invariant/target; у новой матрицы — негативная/мутационная проба; лог прогона
читай. Канон не переоткрывай; если реальный конфликт — останови и спроси оператора.

В конце отчёт фактами: что сделано, чем доказано, что осталось; обнови
tickets/core-kb/01-engine.md и docs/ops/continue.md.

Если нужен браузер, проверь mcp__playwright-mcp__*; если его нет — попроси оператора
перезапустить DSH (конфиг уже в профиле), не имитируй E2E.
```

## Rules of continuation

- One ticket per run; do not batch. Research before writing.
- Evidence: a test that proves a spec clause, guards an invariant or reproduces a real
  failure; a new matrix gets a negative/mutation probe; read the run log.
- No registries, inventory, provenance line, Reel, acceptance chord, issue counter, or
  automatic grill → tickets chain.
- Do not copy the `ontoship-zcode` `docs/`; it is the strict profile/history.
- Update this runbook with the next state at the end of a run; keep it short.
