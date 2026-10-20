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
| `eb678d8` | ticket 01: trimmed engine, 131 tests |
| `e5a2ced` | ticket 02 start prompt |
| `4b10f95` | ticket 02: `kb-search` SKILL.md and its contract test |
| `f189889` | docs: ticket 02 closed; ticket 03 ready |

Tickets 01 and 02 are **implemented and committed**: `skills/kb-search/gitmark.py`
(1302 lines), `skills/kb-search/SKILL.md`, `tests/` (142 passed), `lint --strict` clean.
The `kb-search` skill is contract-tested and a fresh session found the canon with
`search "canon"`. Nothing else is built yet: no `kb-curate`/`init` `SKILL.md`, no
`scripts/`. Next is ticket 03.

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
- `skills/kb-search/` — the trimmed engine (ticket 01) and the user-facing `SKILL.md`
  (ticket 02): `index`, `search`, `lint`, `map`, `stat`, `version`; no
  `inventory`/`serve`/I7. Harness-agnostic CLI (stdlib only); ignores both `.dsh` and
  `.zcode` install roots.
- `tests/` — engine and skill-contract tests; run `python3 -m pytest tests/ -q`
  (stdlib + pytest, no Node).
- `.dsh/skills/kb-search` — the gitignored project-local demo install (a symlink); the
  installer itself is ticket 05.
- `.scratch/handoff-current.md` — the previous session snapshot (ephemeral).

## Ticket order

**01 engine → 02 kb-search → 03 kb-curate/ontology → 04 init → 05 install → 06 dogfood.**

01 and 02 are implemented and committed; 03 is next. 04 is unblocked by 01 but follows
03 in order; 05 waits for 02–04 and 06 waits for 05. Install comes after the skills
exist; it links them, it does not run init.

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
  to get `mcp__playwright-mcp__*` in new sessions. Tickets 01–02 did not need the browser;
  do not fake E2E if it is absent.
- Python 3.13, stdlib only for the engine; `pytest` is available. `node/npm/npx` are not
  in PATH; the engine must not need Node.

## Start prompt

```text
Мы продолжаем работу в /home/prog7/home/dev/contrib/forks/ontoship-dsh — чистый
OntoShip-core (DSH). План core-kb утверждён; репозиторий самодостаточен.

Прочитай по порядку: AGENTS.md, docs/ops/continue.md,
docs/decisions/ontoship-core.md, docs/reference/testing.md, docs/reference/sources.md,
docs/plans/core-kb.md, tickets/README.md, tickets/core-kb/03-kb-curate-ontology.md.

Тикеты 01 (движок) и 02 (kb-search) реализованы и закоммичены:
skills/kb-search/gitmark.py (1302 строки), skills/kb-search/SKILL.md, tests/ (142 passed),
lint --strict чистый. Не переделывай движок и kb-search; не смешивай их изменения с
коммитом 03.

Сделай тикет 03: skills/kb-curate/SKILL.md, skills/kb-curate/ontology.md и docs/ontology.md.
Модель: node types, frontmatter, типизированные связи, инварианты I1–I6 и I8–I10; I7
(registry) вне ядра. SKILL.md — как CREATE / UPDATE / DEPRECATE / LINK / REINDEX:
классифицировать, разместить, frontmatter, связать, обновить индекс папки. docs/ontology.md —
единственный носитель словаря типов для I2 (таблица `| node_type ...`); I8 сравнивает тело
от первого `## ` с skills/kb-curate/ontology.md, в плоском репо расхождение = ERR. Без
новых инвариантов, без registry-таблиц, без provenance, Reel, acceptance chord.

Сначала исследуй, как lint читает docs/ontology.md, I2 и I8 (движок уже готов), потом
реализуй. Веди TodoWrite по шагам тикета. Проверка — spec/invariant: документ с node_type,
body-ссылкой и ссылкой из README папки проходит lint; удалить node_type → ERR I1; битая
ссылка → ERR I4; lint --strict exit 1. Если добавляешь матрицу — негативная/мутационная
проба. Лог прогона читай.

Demo: добавить документ в docs/reference/, связать из docs/reference/README.md, lint
--strict чистый; убрать node_type → ERR I1, exit 1.

Если нужен браузер, проверь mcp__playwright-mcp__*; если его нет — попроси оператора
перезапустить DSH, не имитируй E2E.

В конце отчёт фактами: что сделано, чем доказано, что осталось; обнови
tickets/core-kb/03-kb-curate-ontology.md и docs/ops/continue.md. Один тикет за прогон;
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
