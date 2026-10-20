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

Tickets 01–04 are **implemented and committed**: `skills/kb-search/gitmark.py`
(1302 lines), `skills/kb-search/SKILL.md`, `skills/kb-curate/SKILL.md`,
`skills/kb-curate/ontology.md`, `docs/ontology.md`, `skills/init/SKILL.md`, `tests/`
(153 passed), `lint --strict` clean. The three skills are contract-tested; the ontology
model is one body in two copies (I8); the init block is 747 bytes and its temp-repo matrix
covers create/append/replace/fail/idempotence. This repo's `AGENTS.md` does **not** carry
the block yet — ticket 06 runs init here. Nothing else is built yet: no `scripts/`. Next
is ticket 05.

## Where things live

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
- `tests/` — engine and skill-contract tests; run `python3 -m pytest tests/ -q`
  (153 passed; stdlib + pytest, no Node).
- `.dsh/skills/kb-search` — the gitignored project-local demo install (a symlink); the
  installer itself is ticket 05.
- `.scratch/handoff-current.md` — the previous session snapshot (ephemeral).

## Ticket order

**01 engine → 02 kb-search → 03 kb-curate/ontology → 04 init → 05 install → 06 dogfood.**

01–04 are implemented and committed; 05 is next. 05 waits for 02–04 and 06 waits for 05.
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
  to get `mcp__playwright-mcp__*` in new sessions. Tickets 01–04 did not need the browser;
  do not fake E2E if it is absent.
- Python 3.13, stdlib only for the engine; `pytest` is available. `node/npm/npx` are not
  in PATH; the engine must not need Node.

## Start prompt

```text
Мы продолжаем работу в /home/prog7/home/dev/contrib/forks/ontoship-dsh — чистый
OntoShip-core (DSH). План core-kb утверждён; репозиторий самодостаточен.

Прочитай по порядку: AGENTS.md, docs/ops/continue.md,
docs/decisions/ontoship-core.md, docs/reference/testing.md, docs/reference/sources.md,
docs/plans/core-kb.md, tickets/README.md, tickets/core-kb/05-install.md.

Тикеты 01–04 реализованы и закоммичены: skills/kb-search/gitmark.py (1302 строки),
skills/kb-search/SKILL.md, skills/kb-curate/SKILL.md, skills/kb-curate/ontology.md,
docs/ontology.md, skills/init/SKILL.md, tests/ (153 passed), lint --strict чистый.
Не переделывай движок, kb-search, kb-curate/ontology и init; не смешивай их изменения
с коммитом 05.

Сделай тикет 05: scripts/install.sh <project> — проект-локальная установка ядра в
<project>/.dsh/skills/{kb-search,kb-curate,init}: симлинки на этот репозиторий по
умолчанию, --copy для отсоединённой копии, --check для дрейфа (exit 0/1, называет
каждый отсутствующий или неверный линк). Второй запуск идемпотентен; никаких записей
вне <project>/.dsh/skills; без .zcode, глобальной установки и Playwright. Install
линкует скиллы и не запускает init. Сначала исследуй, как DSH обнаруживает скиллы
(<root>/<name>/SKILL.md, rank 100), потом реализуй. Веди TodoWrite по шагам тикета.

Проверка — spec: свежая установка в temp-репо (три линка), второй запуск без изменений,
--check 0; удалить линк → --check 1 и имя; --copy → три реальных каталога; тест на это.
Если добавляешь матрицу — негативная/мутационная проба. Лог прогона читай.

Demo: install в temp-репо; ls -l .dsh/skills показывает три ссылки; повторный запуск
без изменений; --check 0; удалить линк → --check 1 и имя; --copy в другой temp-репо —
три реальных каталога.

Если нужен браузер, проверь mcp__playwright-mcp__*; если его нет — попроси оператора
перезапустить DSH, не имитируй E2E.

В конце отчёт фактами: что сделано, чем доказано, что осталось; обнови
tickets/core-kb/05-install.md и docs/ops/continue.md. Один тикет за прогон;
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
