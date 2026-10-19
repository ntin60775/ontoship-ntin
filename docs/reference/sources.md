---
node_type: reference
title: Sources of the core idea
service: _platform
status: active
updated: 2026-10-19
tags: [sources, ontoship, grilling, to-tickets, testing]
links:
  relates_to: [README.md, ../decisions/ontoship-core.md]
---

# Sources of the core idea

The core is a composition of three sources. This page records what each one actually
says, what was adopted, and what was deliberately left out. All three are MIT.

## 1. OntoShip — KB + dev-flow

[vakovalskii/ontoship](https://github.com/vakovalskii/ontoship) ·
[dev-flow skill](https://github.com/vakovalskii/ontoship/blob/main/skills/dev-flow/SKILL.md) ·
[positioning ADR](https://github.com/vakovalskii/ontoship/blob/main/docs/decisions/ontoship-positioning.md)

- **Idea:** markdown + a README index + git. Everything derived (index, HTML graph,
  registries) is regenerated. One self-contained Python-stdlib CLI. The ontology is
  optional: "Use it or ignore it; the tool doesn't force it."
- **Proof by existence:** on a live project, 421 docs, 568 links, 88 READMEs, 617 KB
  commits; `gitmark index` rebuilds in 1.5 s with ~50 MB RAM.
- **dev-flow:** research → tasks → goal → spec (markdown in the KB) → worktree →
  implement → tests → independent review → dev-tests → prod-tests → ship. Roughly
  40 minutes to 2 hours; an independent reviewer caught 191 bugs before prod.
- **Positioning:** the product is the workflow (operator + agent → PR), not the search.
  The goal is transfer: a new operator reaches a PR without the author in the loop.

**Adopted:** the KB as substrate, the dev-flow skeleton, the worktree, the independent
review, the "product is the workflow" positioning, the simplicity property, and the
transfer metric (new operator → first PR without the author).

**Left out:** a mandatory ontology, a registry of plans/commands as a gate, and the
idea that every process detail must be written down as prose.

## 2. Matt Pocock — grilling and to-tickets

[mattpocock/skills](https://github.com/mattpocock/skills) ·
[grilling skill](https://github.com/mattpocock/skills/blob/main/skills/productivity/grilling/SKILL.md) ·
[to-tickets skill](https://github.com/mattpocock/skills/blob/main/skills/engineering/to-tickets/SKILL.md)

- **grilling:** map the subject as a design tree; each round asks the whole **frontier**
  (decisions whose prerequisites are settled), numbered, each with a recommended answer.
  **Facts are the agent's job; decisions are the user's.** "An agent running grilling
  that answers its own decisions has broken the skill." Done when the frontier is empty
  and the user confirms a shared understanding.
- **to-tickets:** tracer-bullet vertical slices, each demoable, each with blocking edges;
  a quiz before publication; local files under `.scratch/<feature>/issues/` or a real
  tracker; no `file:line` anchors (they go stale); acceptance criteria must fail at the
  base commit. `disable-model-invocation: true` — the agent never calls it.

**Adopted:** the interview mechanism and the fact/decision split; the tracer-bullet
ticket, blocking edges, the quiz, the demo path, and the "criteria must fail at base"
rule; tickets as ephemeral execution artefacts.

**Left out:** the zcode fork's inversions — autonomous grilling, an automatic
grilling → to-tickets chain, KB tickets with a status machine and a plan registry.

## 3. The operator's testing strategy

Recorded in the research note of 2026-10-19; the claims below are the operator's.

- **Purpose:** a test proves a **spec clause** (what the customer asked for) or guards a
  **project invariant**. Nothing else justifies a test.
- **Evidence-based testing:** `spec → invariant → proof → test`, not `spec → test`.
  The expected value comes from an independent source (spec, literal, worked example),
  never recomputed the way the code computes it.
- **Unit tests are smoke:** the model rarely errs on algorithm logic; deployment,
  version and integration edges are where the failures live. Test logic where a proof
  or an invariant exists, not "just in case".
- **Browser/E2E creates new context:** screenshots and real UI state are information the
  code and logs do not have. Backend tests often duplicate the logs.
- **Hand-written scenario E2E is a safe-path trap:** it grows faster than the code and
  quality does not follow. Scenarios belong to an **agent via MCP**, acting as a user;
  the agent reads logs and code, and its main product is a **diagnostic report** with a
  problematic data slice — a coding LLM fixes from it in one shot.
- **Agentic E2E complements deterministic checks**, it does not replace them; the agent
  reads the proofs in the logs too.
- **Delete stale tests:** in practice tests outrank specs; manual filtering of tests —
  removing outdated and ineffective synthetic ones — is a first-class step.

**Adopted:** all of it, as the quality rule of the canon. The six channels (unit/contract,
E2E/smoke, expected output, recorded replay, browser/snapshot, performance) are the
instruments; spec/invariant is the purpose axis.

## Licence

- OntoShip — MIT, © vakovalskii and OntoShip contributors.
- mattpocock/skills — MIT, © 2026 Matt Pocock.
- Text in this repository is an adaptation with attribution; the method is free to use.
