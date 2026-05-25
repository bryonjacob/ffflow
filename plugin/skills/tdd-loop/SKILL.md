---
name: tdd-loop
description: The red/green/refactor discipline — same at every level, artifacts scale. Reference rulebook loaded by work and by characterize backfill tasks.
---

# tdd-loop

## Purpose

The execution discipline shared by every FFFlow workflow that writes code. Not a standalone skill — it's a reference rulebook loaded by `work-issue` and by characterize's test-backfill tasks.

Same loop at every level. The artifacts scale.

## The loop

1. **Read the spec / acceptance criteria.** What behavior is being added or changed?
2. **Write the test(s) that pin the new behavior.** One behavior per test where possible.
3. **Run the tests. Confirm they fail (RED).** If they pass, the test is wrong, or the behavior already exists, or both. Investigate before continuing.
4. **Write the minimum code to make them pass (GREEN).** Don't anticipate the next behavior. Don't refactor yet.
5. **Refactor under green.** Tests stay green throughout. If they go red during refactor, revert and try smaller steps.
6. **Repeat** for the next chunk of acceptance.

## Per-level artifact mapping

The discipline is the same; what counts as a "test" varies.

### L0

- Tests: unit tests in the project's existing framework (pytest, vitest, junit, etc.).
- Spec: prose. The test names should align with the prose's verbs.
- Refactor target: extract method, rename, deduplicate.

### L1

- Tests: as L0, plus integration tests at module boundaries.
- Spec: prose with hexagonal layer mapping.
- Refactor target: as L0, plus port/adapter separation when a test forces it.

### L2

- Tests are two-layered:
  - **Acceptance:** Gherkin Scenarios first. Bind step definitions. Run via the BDD runner (pytest-bdd, quickpickle, cucumber).
  - **Inner:** unit tests for each Rule's invariants. Property-based tests for `@property-based` Scenarios.
- Spec: `.feature` file. Scenarios written before the test runner can pass them.
- Refactor target: as L1, plus extracting domain primitives that show up across scenarios.

### L3

- Tests are three-layered:
  - **Acceptance:** Gherkin Scenarios with `@RID-*` tags.
  - **Inner:** unit tests covering each domain invariant.
  - **Mutation:** the test suite must kill mutants in scope above the threshold from `quality-gates` (which reads from the stack's `dimensions:`).
- Spec: `.feature` files with full RID traceability, plus property-based scenarios where `@property-based` is tagged.
- Refactor target: as L2, plus reducing complexity to meet `quality-gates` maintainability thresholds.

## Red discipline

If your test passes the first time:

1. **The test is trivial.** It asserts what's already true. Rewrite it to assert the new behavior, not the existing one.
2. **The behavior already exists.** Check. If it does, the task is wrong — stop and confirm with the user.
3. **The test isn't actually running.** Check the runner output. (Pytest-bdd silently skipping unbound steps is a common one.)

A passing first-run test is a smell, not a win. Investigate before declaring green.

## Green discipline

When making the test pass:

- Write the **minimum** code. Don't anticipate.
- Don't add error handling, validation, or fallbacks unless the test asserts them.
- Don't add comments explaining what the code does. The test does that.
- Resist refactoring until green. Refactor in step 5, not step 4.

## Refactor discipline

- **Under green.** Tests pass at every commit.
- **Small steps.** One refactor per commit when feasible. Easier to revert.
- **Sanity checks:** types still check, lint clean, format clean. Not just tests.
- **Refactor target lives, refactor noise dies:** keep meaningful renames; revert exploratory edits that didn't pan out.

## Commit cadence

- Commit at the end of each green step. Each commit message names the behavior added.
- L2+: include the Rule or RID in the commit message.

Example:
```
auth: reject passwords < 8 chars (@RID-PWD-001)
```

## When tests can't be written first

Exceptions exist. Note in the PR body when the loop is abridged and why.

## Anti-patterns

- Writing the code first, then writing tests that confirm it. Tests must be able to **fail** before they pass.
- Skipping the red step "because I'm confident." Red is the confirmation that the test actually tests something.
- Refactoring while tests are red. Always restore green first.
- Bundling multiple behaviors in one test. Hard to read, hard to fix when it fails.
- Letting test coverage drift without updating the spec. Every new test should map to a spec entry — if it doesn't, the spec is incomplete.

## How `work-issue` uses this skill

`work-issue` loads `tdd-loop` as reference context at Phase 2 and walks the loop per chunk of acceptance. It doesn't invoke `tdd-loop` as a tool call — there's nothing to invoke. The skill is the prose discipline; the implementation lives inside `work-issue`.

## How `characterize` uses this skill

Characterize-generated tasks for the test backfill are tagged "characterization." Their TDD loop runs in reverse: the behavior already exists; the test is written to pin it. Red is replaced by "confirms the existing behavior, then confirm what would break if the behavior changed." Same discipline, characterized variant.
