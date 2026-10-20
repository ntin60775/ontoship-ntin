---
node_type: runbook
title: Continue development from this repo
service: _platform
status: active
updated: 2026-10-20
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

Ticket 01 is **implemented and tested**: `skills/kb-search/gitmark.py` (1302 lines) and
`tests/` (131 passed). Nothing else is built yet: no `kb-search`/`kb-curate`/`init`
`SKILL.md`, no `scripts/`. Next is ticket 02.

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
- `skills/kb-search/gitmark.py` — the trimmed engine (ticket 01): `index`, `search`,
  `lint`, `map`, `stat`, `version`; no `inventory`/`serve`/I7. Harness-agnostic CLI
  (stdlib only); ignores both `.dsh` and `.zcode` install roots.
- `tests/` — engine tests; run `python3 -m pytest tests/ -q` (stdlib + pytest, no Node).
- `.scratch/handoff-current.md` — the previous session snapshot (ephemeral).

## Ticket order

**01 engine → 02 kb-search → 03 kb-curate/ontology → 04 init → 05 install → 06 dogfood.**

01 is implemented and committed; 02 is ready. 03–06 are blocked by their predecessors.
Install comes after the skills exist; it links them, it does not run init.

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
Мы продолжаем работу в /home/prog7/home/dev/contrib/forks/ontoship-dsh — чистый
OntoShip-core (DSH). План core-kb утверждён; репозиторий самодостаточен.

Прочитай по порядку: AGENTS.md, docs/ops/continue.md,
docs/decisions/ontoship-core.md, docs/reference/testing.md, docs/reference/sources.md,
docs/plans/core-kb.md, tickets/README.md, tickets/core-kb/01-engine.md,
tickets/core-kb/02-kb-search-skill.md.

Тикет 01 (движок) уже реализован и закоммичен: skills/kb-search/gitmark.py (1302 строки),
tests/ (131 passed), lint --strict чистый. Не переделывай движок и не смешивай его
изменения с коммитом 02.

Сделай тикет 02: skills/kb-search/SKILL.md — user-facing навык поиска по КБ.
DSH frontmatter (name, description); тело: когда использовать (найти, где
документировано; перед чтением файлов наугад; перед новым доком), команды
index/search/map/stat/version, --json, .gitmark/ — производное; без inventory,
serve, registry. Деградация честная: нет индекса — назвать команду; нет хитов —
сказать; не выдумывать документы. Без провенанса, Reel, acceptance chord.

Сначала исследуй: как DSH обнаруживает скиллы, формат frontmatter, как SKILL.md
соотносится с CLI движка. Потом реализуй. Веди TodoWrite по шагам тикета. Проверка —
spec/invariant: frontmatter и обязательные команды, отсутствие запрещённых сущностей;
если добавляешь матрицу — негативная/мутационная проба. Лог прогона читай.

Demo: fresh session в этом репо просит навык найти canon; он запускает
`python3 skills/kb-search/gitmark.py search "canon"` и возвращает
docs/decisions/ontoship-core.md со сниппетом.

Если нужен браузер, проверь mcp__playwright-mcp__*; если его нет — попроси оператора
перезапустить DSH (конфиг уже в профиле), не имитируй E2E.

В конце отчёт фактами: что сделано, чем доказано, что осталось; обнови
tickets/core-kb/02-kb-search-skill.md и docs/ops/continue.md. Один тикет за прогон;
канон не переоткрывай; при реальном конфликте останови и спроси оператора.
```

## Rules of continuation

- One ticket per run; do not batch. Research before writing.
- Evidence: a test that proves a spec clause, guards an invariant or reproduces a real
  failure; a new matrix gets a negative/mutation probe; read the run log.
- No registries, inventory, provenance line, Reel, acceptance chord, issue counter, or
  automatic grill → tickets chain.
- Do not copy the `ontoship-zcode` `docs/`; it is the strict profile/history.
- Update this runbook with the next state at the end of a run; keep it short.
