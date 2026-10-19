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

**Adopted:** all of it, as the quality rule of the canon, plus a third test class —
**target tests** — from the ESEM 2026 evidence below. The six channels (unit/contract,
E2E/smoke, expected output, recorded replay, browser/snapshot, performance) are the
instruments; spec/invariant/target is the purpose axis.

### Evidence: ESEM 2026 — targeted unit tests with LLM agents

Jiayu Liu and Yanjun Wu, *Beyond Heuristics? Rethinking Targeted Unit Test Generation in
the Era of LLM Agents*, ESEM 2026, LIPIcs vol. 394, 47:1–47:21,
[DOI 10.4230/LIPIcs.ESEM.2026.47](https://doi.org/10.4230/LIPIcs.ESEM.2026.47).

- **Design:** 210 real-world Java **runtime exception** bugs from 66 projects. The agent
  gets the buggy codebase, the exception type and the line-level location; it must produce
  a JUnit suite that triggers that exception at that line. No spec, no patch —
  reproduction only.
- **Results:** 89.5% (Claude Code + GPT-5; 325.8 s, $1.09 per bug), 87.6% (OpenHands +
  GPT-5), 65.2% (OpenCode + DeepSeek-V3.2; $0.04), versus UnitCon 49.6%, EvoSuite 39.4%,
  Randoop 21.3%.
- **Quality caveats:** in a manual sample of 90 successes, 5.6% are degenerate paths
  (artificial inputs such as raw nulls into internal methods), 16.7% bypass public entry
  workflows to manipulate private APIs/internal singletons, and 72.2% have low semantic
  clarity. Generated tests are structurally more fragile than developer tests.
- **Failure modes:** Insufficient Exploration 41.5%, Inadequate Reasoning 25.5%, Tool
  Misuse 14.0%, Incorrect Focus 11.5%.
- **Boundaries:** Java runtime exceptions only; the authors argue the core capabilities
  are language-agnostic, but logical/assertion bugs may need spec context and concurrency
  bugs are out of scope.

**What the paper supports:** target tests generated by LLM agents against a known failure
are far more effective at reproduction than coverage-oriented/heuristic tools; the loop is
code exploration → execution feedback → refinement.

**What it does not support:** the paper does not measure TDD, does not compare
spec-derived tests with target tests, and **does not report 53%**. The closest number is
UnitCon's 49.6%. The "53%" and the claim that ordinary unit tests miss half the bugs are
the operator's broader argument (possibly from another source) and must be cited
separately. The baselines are test-generation tools, not developer-written TDD suites.

## Licence

- OntoShip — MIT, © vakovalskii and OntoShip contributors.
- mattpocock/skills — MIT, © 2026 Matt Pocock.
- Text in this repository is an adaptation with attribution; the method is free to use.
