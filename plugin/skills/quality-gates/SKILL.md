---
name: quality-gates
description: The four-gate model (Structure, Correctness, Coverage, Maintainability) with spec liveness, mutation testing, complexity budgets. L3 reference rulebook.
---

# quality-gates

## Purpose

Reference rulebook (L3). Loaded as context by `work-issue`, `ci-gates`, and L3 auditors. Not invoked as a tool.

Four gates. Ordered by speed. Fast feedback first. All must pass for a PR to merge. Implemented in CI by `ci-gates` invoking `/audit --ci`; this skill describes the *model*.

## Gate 1: Structure

Runs in under a second. No test execution.

- **Spec audit passes.** `specdrive audit` verifies the full traceability chain.
  - S1: Every scenario has an RID.
  - S2: All RIDs are unique.
  - S3: RID format is valid.
  - S4: RID context matches directory.
  - S5: Every step has a step definition.
  - S6: No orphaned step definitions.
- **RID checks.** Format, uniqueness, context-directory alignment.
- **Annotation health.** `@known-defect` count within configured maximum. `@unverified-intent` resolved within configured timeframe.

```yaml
audit:
  rules:
    known-defect-count:
      severity: warning
      max: 5
    unverified-intent-max-age-days: 30
```

Structure gates catch problems before any test runs. Suitable for pre-commit hooks via `/audit --type structure` (selecting the structural auditors only).

## Gate 2: Correctness

All tests pass. No exceptions.

- **All unit tests pass.** Implementation-level correctness verified.
- **All spec tests pass.** Every Gherkin scenario with step definitions passes against real code.
- **All property-based tests pass.** `@property-based` tagged scenarios generate hundreds of random inputs. Invariants hold across all of them.
- **Contract checks pass.** Schema generation and type compilation succeed.

A single failing test blocks the PR. No "known failures" in the test suite. Known failures live in the spec as `@known-defect` annotations, not as skipped tests.

## Gate 3: Coverage

Two independent coverage dimensions plus mutation testing.

**Unit test coverage**, **spec test coverage**, and **mutation score** all read their thresholds from the stack skill's `dimensions:` block (e.g., `coverage_threshold_line`, `mutation_threshold`). Numbers are not duplicated here — the stack is the single source of truth, and `.ffflow/stack.yaml` can override per project.

- Unit coverage and spec coverage are measured independently (different suites).
- Mutation score combines both suites against mutated code. Focus on the hexagonal core (domain + application). Don't waste cycles mutating infrastructure adapters.
- Tools: Stryker (TypeScript), mutmut (Python), PIT (Java).

Mutation testing is slow. Run it in CI on PRs scoped to changed files (e.g., Stryker's incremental mode). Run it nightly across the full domain layer.

## Gate 4: Maintainability

- **Cyclomatic complexity per function** capped at the stack's `complexity_limit` (default 10). Higher complexity means more branches; more branches mean more spec scenarios needed. If a function exceeds the budget, refactor until it's specifiable.
- **No functions with 0% mutation score.** A function where every mutant survives has assertions that verify nothing. Dead assertions are worse than no assertions. They create false confidence.
- **Contract types regenerated and committed.** If a port interface changes, the generated types must be updated in the same PR.

Complexity budgets connect architecture to specification. You refactor not for aesthetics but because the code must be specifiable.

## Spec Liveness

Liveness means no decay and no orphans.

**Unbound specs.** Scenarios with no step definitions. The audit catches these via S5. Every scenario must be bound.

**Orphaned step definitions.** Step definitions with no corresponding scenario. Dead code. The audit catches these via S6.

**Stale specs.** Behavior changed but spec didn't. Mutation testing and integration tests catch some of this. The audit's structural checks catch the rest.

## Gate Order

```
Gate 1: Structure     ~1 second     (pre-commit viable)
Gate 2: Correctness   ~30 seconds   (fast test suite required)
Gate 3: Coverage      ~2 minutes    (coverage collection overhead)
Gate 4: Maintainability  ~5 minutes (mutation testing on changed files)
```

A structural failure means don't bother running tests. A correctness failure means don't bother measuring coverage. A coverage failure means don't bother with mutation analysis. Each gate's success is a precondition for the next.
