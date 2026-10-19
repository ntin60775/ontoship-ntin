---
node_type: reference
title: Testing — spec, invariants, target tests
service: _platform
status: active
updated: 2026-10-19
tags: [testing, target-tests, tdd, evidence, agents, esem2026]
links:
  relates_to: [README.md, ../decisions/ontoship-core.md, sources.md]
---

# Testing — spec, invariants, target tests

The quality rule of the canon has **three** legitimate purposes for a test, not two:

1. **Spec test** — proves a clause of the spec: the observable behaviour the customer
   asked for. Acceptance criteria live here.
2. **Invariant guard** — protects a project invariant: what must never break, even when
   the spec is silent.
3. **Target test** — reproduces a real failure (bug, incident, production report). It is
   generated **from the failure**, not from the spec: given the codebase, the exception
   or symptom, and the location, the agent writes a test that makes the failure happen.

A test with none of the three is an orphan: it cannot be justified and cannot be removed
by a rule. A test that merely restates the implementation is not evidence.

## Why target tests are a separate class

A spec test is a **projection** of the spec into executable form — partial and distorted.
It checks what the spec author thought to write, at the seam they chose. In practice tests
can acquire priority over the spec (Microsoft's reward-hacking observation, cited by the
operator), and a stale test then protects a requirement that no longer exists. A target
test does not encode a spec projection at all: it encodes an observed failure, so it does
not conflict with the spec and cannot be "gamed" by re-wording it.

Target tests are the strongest evidence for a **fix**: the test must fail on the buggy
tree and pass after the fix, and it must reproduce the real failure path — not an
artificial exception.

## What the ESEM 2026 study actually shows

Jiayu Liu and Yanjun Wu, *Beyond Heuristics? Rethinking Targeted Unit Test Generation in
the Era of LLM Agents*, ESEM 2026, LIPIcs vol. 394, 47:1–47:21,
[DOI 10.4230/LIPIcs.ESEM.2026.47](https://doi.org/10.4230/LIPIcs.ESEM.2026.47).

**Design.** 210 real-world Java **runtime exception** bugs from 66 projects. The agent gets
the buggy codebase, the exception type and the line-level location; it must produce a
JUnit suite that triggers that exception at that line (execution oracle: exception type +
target location at the top of the stack trace). No spec, no patch — reproduction only.

**Results (Table 2 and §4.2).**

| approach | success rate |
|---|---|
| Claude Code + GPT-5 | **89.5%** (325.8 s, $1.09 per bug) |
| OpenHands + GPT-5 | 87.6% |
| OpenCode + DeepSeek-V3.2 | 65.2% ($0.04, 774.1 s) |
| UnitCon (SOTA targeted tool) | 49.6% |
| EvoSuite | 39.4% |
| Randoop | 21.3% |

**What the paper supports.** LLM agents with code exploration, execution feedback and
dynamic API access are much better at **reproducing a known bug** than coverage-oriented
or heuristic tools. The advantage comes from direct code comprehension, iterative
refinement on execution output, and choosing public call paths or reflection to reach the
buggy location. Even the open-source configuration (65.2%) beats every traditional tool.

**What the paper does not show.** It does **not** measure TDD, does not compare
spec-derived tests with target tests, and does not report a 53% baseline. The closest
number is UnitCon's 49.6%. The "53%" and the claim that ordinary unit tests miss half the
bugs are the expert's broader argument (possibly from another source) — keep them as a
separate citation, not as this paper's result. The paper's baselines are test-generation
**tools**, not developer-written TDD suites.

**Quality caveats.** High reproduction is not high quality. In the manual sample of 90
successful cases: **5.6%** are degenerate paths (exceptions forced with artificial inputs
such as raw nulls into internal methods), **16.7%** bypass public entry workflows to
manipulate private APIs or internal singletons (structurally fragile), and **72.2%** have
low semantic clarity (`testBug`, `boom`, cryptic hardcoded JSON). Generated tests are
structurally more fragile than developer-written ones.

**Failure modes** (RQ3): Insufficient Exploration 41.5%, Inadequate Reasoning 25.5%,
Tool Misuse 14.0%, Incorrect Focus 11.5%. These are the checklist for an agentic
target-test loop.

**Boundaries.** Java runtime exceptions only; the authors argue the core capabilities are
language-agnostic, but logical/assertion bugs may need spec context, and concurrency bugs
need temporal control that is out of scope. The 15-minute budget matters: tightening to 10
minutes costs ~7 points for closed models and more for the open one; 20–25 minutes is the
plateau.

## Target-test quality bar

A target test is evidence only if all of these hold:

- **Real failure path.** The failure is reproduced through the product's real entry point;
  an artificial exception (raw null into an internal method, forced throw) is not a
  reproduction. If the bug is genuinely inside a private seam, say so and justify it.
- **Red → green.** The test fails on the base commit for the right reason, and passes
  after the fix. A test that passes before the fix proves nothing.
- **Stable and deterministic.** No flaky timing, network, ordering or environment
  dependence; the failure is the bug, not the harness.
- **Readable.** A descriptive name, a minimal fixture, parameters that a reader can
  explain. `testBug`/`boom` and cryptic blobs are a quality defect, not a shortcut.
- **Reviewed.** A second pair of eyes (human or an independent agent) checks that the
  test reproduces the reported failure, not a nearby or invented one.
- **Kept only while the failure class is live.** When the bug class is fixed for good or
  the feature is retired, delete the target test like any stale spec test.

## When to use which class

| situation | primary class | notes |
|---|---|---|
| New behaviour with a customer-visible contract | spec test | acceptance criteria; expected values from the spec |
| A defect report, crash, regression, incident | target test | reproduce first, then fix; quality bar above |
| A project invariant (security, format, compatibility, data integrity) | invariant guard | deterministic, cheap, broad |
| Logic with no independent oracle | none — first find the proof | a test that restates the code is tautological |
| UI/browser behaviour | target or spec at the E2E level | agent via MCP + screenshot; not a hand-written safe path |
| Performance/scale | invariant guard (budget) | index/lint/map budgets for the engine |

**Channels are instruments, not purposes:** unit/contract, E2E/smoke, expected output,
recorded replay, browser/snapshot, performance. A target test can live in any channel; a
spec test usually lives in unit/contract or E2E.

## The agentic target-test loop

The paper's successful loop is: read the code → infer the failure condition → draft a
test → execute → refine on feedback. For the skill:

1. **Reproduce** — get a tight, deterministic command that goes red on the reported
   failure (the `diagnose` discipline: a named command, already run, that can go red).
2. **Explore** — read the code and logs enough to name the precondition that triggers the
   failure. Insufficient exploration is the largest failure mode (41.5%).
3. **Reason** — state the failure mechanism and the expected observation before writing
   the test (25.5% failures are inadequate reasoning).
4. **Draft and run** — one test at a time, execute, refine; keep the test suite minimal.
5. **Quality gate** — check the bar above: real path, red→green, stable, readable,
   reviewed; reject degenerate or private-API shortcuts.
6. **Fix** — the fix follows the reproduced failure; the target test stays as the
   regression guard.
7. **Diagnose on failure** — if no reproduction after the budget, stop and report what was
   tried and what is missing (environment, artifact, instrumentation), rather than writing
   a shallow test.

Budget: the study used 15 minutes and $0.04–$1.09 per bug; the open model trades quality
for cost. Set a per-bug budget in the skill; do not let target generation eat a whole
session.

## Metrics

- **Spec coverage** — spec clauses with at least one failing-capable test.
- **Invariant coverage** — invariants with a guard.
- **Target coverage** — fixed defects with a red→green target test; escaped defects per
  period.
- **Stale tests removed** — a first-class count, not a cleanup chore.
- **Suite cost** — runtime and flakiness; a suite that the agent cannot run is not a
  suite.

Not metrics: number of tests, line coverage, "green suite" without a read log.

## Relationship to TDD

The study does not refute TDD; it shows that **targeted** generation against a known
failure is a much stronger signal than coverage-oriented generation. The practical
reading: keep spec tests for acceptance, invariant guards for the system's promises, and
generate target tests as the response to real failures. A test base grown only from specs
is a projection; a test base grown from failures does not encode the spec's distortions.
Both are needed; neither replaces the other.

The 53% figure and the Microsoft reward-hacking argument belong to the operator's
argument, not to this paper. If the 53% is used in the canon, cite its source separately.
