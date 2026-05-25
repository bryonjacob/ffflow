---
name: total-specification
description: The FFFlow methodology — 10 pillars of spec-driven development with dual coverage, property-based testing, mutation testing, and full RID traceability. L3 reference rulebook.
---

# total-specification

## Purpose

Reference rulebook (L3). Loaded as context by every L3 workflow skill. Not invoked as a tool.

Spec-driven development where the specification corpus is the primary artifact and code is the implementation detail. Built on FFFlow's structural conventions.

## The Ten Pillars

Each pillar is a one-line summary pointing at the rulebook that owns the discipline. Load those for depth.

1. **Everything is behavior.** Specs in domain language; unit tests for implementation. → [`writing-specs`](../writing-specs/SKILL.md)
2. **Spec-first, red/green TDD.** Spec change drives the loop. → [`spec-first-development`](../spec-first-development/SKILL.md), [`tdd-loop`](../tdd-loop/SKILL.md)
3. **Characterize before changing.** Legacy code = code without specs. Spec it before you change it. → [`characterize`](../characterize/SKILL.md)
4. **Dual coverage.** Unit and spec suites measured independently. Thresholds from the stack's `dimensions:`. → [`quality-gates`](../quality-gates/SKILL.md), stack skills.
5. **Property-based testing.** Universal invariants get `@property-based` scenarios over random inputs. → [`writing-specs`](../writing-specs/SKILL.md).
6. **Mutation testing.** Line coverage with weak assertions is false confidence. Threshold from the stack. → [`quality-gates`](../quality-gates/SKILL.md).
7. **Contract enforcement.** Mocks anchored to verifiable contracts; ports are the contract. → [`contract-enforcement`](../contract-enforcement/SKILL.md).
8. **Spec liveness.** No unbound scenarios, no orphaned step defs, annotation health gated. → [`/audit --type rid`](../audit/cartridges/rid.md), [`defect-driven-specification`](../defect-driven-specification/SKILL.md).
9. **Feedback loop speed.** If spec-test-code exceeds 30s, discipline collapses. Domain tests pure computation. → [`/audit --type refactor`](../audit/cartridges/refactor.md) catches slowness.
10. **Defect-driven specification.** Every bug becomes a spec before a fix. → [`defect-driven-specification`](../defect-driven-specification/SKILL.md).

## Quality gates

Four gates, ordered by speed: Structure → Correctness → Coverage → Maintainability. Thresholds from the stack. Detail in [`quality-gates`](../quality-gates/SKILL.md).

## The Steady-State Loop

```
Spec Change ──> Bind Tests ──> Red ──> Green ──> Refactor ──> Audit ──┐
    ^                                                                  |
    └──────────────── Discovery During Implementation ─────────────────┘

Defect Report ──> Spec the Invariant ──> (same loop)
Exploratory Finding ──> Formalize ──> (same loop)
```

Everything enters through the spec. Everything exits through the audit. The spec corpus grows monotonically.

## When to Use This Skill

- Starting a new project with FFFlow conventions
- Adding spec coverage to an existing codebase (brownfield extraction)
- Reviewing whether a PR meets Total Specification quality gates
- Diagnosing gaps: missing specs, weak mutation scores, drifting mocks
- Guiding the spec-first TDD cycle for a new feature or bugfix

For the full methodology, tooling details, and worked examples, see the FFFlow project's `docs/` repo and `docs/architecture.md` in this plugin.

## How other skills relate

- `writing-specs` — the prose conventions.
- `spec-first-development` — the steady-state loop.
- `defect-driven-specification` — the bug-fix branch of the loop.
- `contract-enforcement` — the mocking discipline.
- `rid-traceability` — the RID format and rules.
- `quality-gates` — the four-gate CI shape.
- `hexagonal-architecture` — the layering this methodology assumes.

This skill summarizes; the others go deep.
