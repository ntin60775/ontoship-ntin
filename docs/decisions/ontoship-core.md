---
node_type: decision
title: OntoShip core — the canon
service: _platform
status: active
updated: 2026-10-19
tags: [canon, method, kb, grilling, tickets, ship, testing]
links:
  relates_to: [../README.md, ../reference/sources.md]
---

# OntoShip core — the canon

Decision of 2026-10-19: return to the original idea and keep it as the arbiter. A rule
that contradicts this page belongs to the **strict profile** (the `ontoship-zcode`
line) or to history — never to the default.

## What OntoShip is

**Transfer of the method.** A new operator picks up a repository and drives work to a
PR with an agent the way the author would — without the author in the loop. The KB is
the substrate (markdown + git, derived artefacts regenerated); **the product is the
workflow**. The ontology is optional; simplicity is an operational property (one
stdlib engine, auditable in an afternoon).

## Three sources

1. **OntoShip** — KB + an 11-step dev-flow; 40 minutes to 2 hours; 191 bugs caught by
   the independent review; proof by existence on a live KB.
2. **Matt Pocock** — `grilling` (design tree, frontier, rounds) and `to-tickets`
   (tracer bullets, blocking edges, quiz). Decisions and publication stay with the
   operator.
3. **The operator's testing strategy** — a test proves a spec clause or guards an
   invariant; scenarios are agentic (MCP); stale tests are deleted.

Details and exact quotes: [sources.md](../reference/sources.md).

## Three artefacts

- **KB** — durable knowledge: markdown + git, deterministic search, typed links and
  folder indexes (optional), everything derived regenerated.
- **spec** — durable contract of one unit: `Goal / Done / Scope / Constraints /
  Context`, one file in `docs/plans/<slug>.md`. Written by `grilling`, approved by the
  operator through the plan gate.
- **ticket** — ephemeral slice of the spec: `.scratch/<slug>/issues/NN-*.md` or a real
  tracker. Tracer bullet, blocking edges, demo path, acceptance criteria. Written by
  `to-tickets` by hand.

**Durable ≠ ephemeral.** The spec lives in the KB; the ticket does not. The ticket
references the spec; the spec keeps no ticket ledger. KB tickets are an opt-in for
multi-day epics, never the default.

## Three phases

1. **grilling** — the interview. Facts are the agent's job; decisions are the
   operator's. Rounds over the frontier; a question that depends on another open
   question waits for the next round. Done when the frontier is empty and the operator
   confirms a shared understanding. Output: the spec, approved at the plan gate. An
   autonomous mode exists as an **explicit flag** for reversible, fact-backed decisions;
   it is not the default, and it carries no challenger/provenance apparatus.
2. **to-tickets** — by hand: tracer bullets, blocking edges, a quiz before publication.
   Every acceptance criterion must fail at the base commit; a ticket with no answer to
   "what can I demo?" is a horizontal slice. No `file:line` anchors — they rot.
3. **ship** — one pass: worktree → implement → evidence tests → one review run →
   dev/prod checks → merge. Stop-points come from the spec's `Constraints`. A review
   pass is leads, not a convergence loop: fix cited findings, report the rest, stop.

The transitions are manual, except grill → spec. `to-tickets` is **user-invoked**;
`grilling` is model-invoked. A user-invoked skill may call model-invoked skills, never
another user-invoked one.

## One quality rule

A test has exactly two legitimate purposes:

1. **prove a spec clause** — the observable behaviour the customer asked for;
2. **guard a project invariant** — what must never break, even when the spec is silent.

A test with neither purpose is an orphan: it cannot be justified and cannot be removed
by a rule. Consequences:

- traceability in the test name or comment: `spec: <path>#<criterion>` or
  `invariant: I<n>`;
- the expected value comes from the spec, a literal or a worked example — never
  recomputed the way the code computes it;
- a new matrix ships with a negative/mutation probe: the test must be able to fail;
- coverage is counted in spec clauses and invariants, not lines or test count;
- when a spec clause or an invariant is retired, its tests go in the same change.

The six channels are the instruments: unit/contract, E2E/smoke, expected output,
recorded replay, browser/snapshot, performance. Channels are **how** a test proves;
spec/invariant is **what** it proves.

## E2E

The **global Playwright MCP is the mandatory default**; everything beyond it is supplied
by the project. The plugin does not ship a browser. It checks the channel
(`mcp__playwright-mcp__*` or `mcp__playwright__*`) and, when it is absent, degrades
honestly and names the gap — it never imitates a scenario with a hand-written safe path.

## Out of the default (strict profile)

Provenance line as an entry condition; quote carrier; Reel; plan acceptance chord;
issue counter; automatic grilling → tickets chain; drift mini-grill; unit check;
cap/round history in the skill; a mandatory plan registry; `file:line` anchors in
tickets. These may live in the strict profile (the `strict` branch/tag of the zcode
line), but not in the core.

## Definition of done

A fresh session, a clean repository, only the core: a ticket reaches `main`, and the
operator can explain every gate. If the author is needed, the return did not happen.
