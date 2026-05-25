---
name: debugging
description: Hypothesis-driven debugging — reproduce, gather evidence, test hypotheses, find root cause, fix minimally, then close the spec gap.
---

# debugging

## Purpose

A workflow for tracking down a bug without chasing symptoms. Loaded by `work-issue` when a chess move is a bug fix, or invoked directly when investigating a failure.

At L1+, this skill loads `defect-driven-specification` as context — every bug becomes a spec before it becomes a fix.

## Process

### 1. Reproduce

- Isolate the minimum steps to trigger the bug.
- Verify it reproduces consistently.
- Note environment factors (versions, configuration, data state).

If you can't reproduce, the bug isn't a bug yet — it's a report. Don't fix the report; reproduce or move on.

### 2. Gather evidence

```
Error: <exact message>
Stack: <key frames, not the full trace>
When: <conditions: load, time, data shape>
Changed: <recent commits, deps, config>
```

Then list hypotheses:

1. <most likely cause>
2. <second possibility>
3. <edge case>

### 3. Test hypotheses

For each:

- **Test:** how will you verify? (Add a log? Run a specific input?)
- **Expected:** what should happen if the hypothesis is right?
- **Actual:** what happened?
- **Result:** confirmed / rejected.

Don't skip the result step. "Confirmed" before evidence isn't confirmation.

### 4. Identify root cause

```
Cause: <actual problem>
Not: <what seemed wrong but wasn't>
Why missed: <testing gap, spec gap, both>
```

The "why missed" is the most important line. It tells you what to add — a test, a spec entry, or both.

### 5. Defect-driven spec (L1+)

Before fixing, write the spec for the invariant the bug violated. Load `defect-driven-specification` as the rulebook for this step.

- Name the invariant. Write a `Rule:` (L2+) or prose section (L0/L1).
- Write a scenario / test documenting the broken behavior, tagged `@known-defect`.
- Verify the test passes (documents current broken behavior).
- Change the test to describe correct behavior; remove `@known-defect`.
- Verify the test fails.

Now you're red. Step 6 makes it green.

### 6. Fix

- Minimal change. One root cause; one fix.
- Don't refactor while fixing — refactor in a separate PR.
- Don't add error handling unrelated to this bug.

Confirm green:
```bash
just check-all
```

### 7. Verify

Run the full check pipeline:
- `just test` — unit tests pass.
- `just spec-test` (L2+) — spec tests pass.
- `just check-all` — no side effects elsewhere.

### 8. PR

Per `work-issue`, the spec change and the fix ship in the same PR. PR body cites the originating bug report, the invariant added, and the fix.

## Investigation patterns

**Binary search through code paths.** When you don't know where the bug lives, halve the suspect surface area at each step. Add a log, observe, halve again.

**Diff against last-known-good.** If the bug appeared recently, `git bisect` to the commit that introduced it.

**Reproducer in a test.** If the bug is in production but doesn't reproduce locally, write the test first — even a flaky one. Use it to drive the investigation.

## Anti-patterns

- Skipping reproduction. Fixes for unreproduced bugs are gambling.
- Fixing symptoms (e.g., catching an exception that shouldn't have been thrown) instead of the cause.
- Refactoring "while you're in there." Separate PRs.
- Skipping the spec step at L1+. The bug returns next quarter.
- Writing the fix before the failing test. Then it's not TDD; it's hope.

## Friction addressed

- Bug fixes that don't pin the invariant — same bug recurs.
- Hours of debugging without a written hypothesis trail.
- Fixes that mutate scope and add unrelated changes.
