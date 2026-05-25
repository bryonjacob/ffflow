---
name: defect-driven-specification
description: Every bug becomes a spec before it becomes a fix — the defect-driven loop with @known-defect, @accepted-risk, @unverified-intent annotations. L1+ reference rulebook.
---

# defect-driven-specification

## Purpose

A reference rulebook (L1+). Loaded as context by `plan-chat`, `characterize`, and `work-issue` when a bug-driven change is in scope. Not invoked as a tool.

The core idea: **every bug becomes a spec before it becomes a fix.** The bug isn't just fixed; it's specified forever. The invariant that was implicit becomes explicit, named, tested, and traceable.

## The loop

```
1. Bug reported.
2. Name the invariant that was violated — write a spec entry (Rule at L2+, prose section at L0/L1).
3. Write a Scenario or test case documenting the broken behavior, tagged @known-defect.
4. Verify the scenario passes — it documents current behavior.
5. Change the scenario to describe correct behavior, remove @known-defect.
6. Watch it fail.
7. Fix the code.
8. Audit passes — the invariant is specified and enforced forever.
```

Step 2 is the critical one. The bug report says "login breaks after 3 failures at the window boundary." Step 2 names the invariant: "Failure window boundary determines accumulation." That invariant was implicit. Now it's explicit.

The spec diff from step 5 is the change request. The fix in step 7 ships in the same PR as the spec change (per `work-issue`).

## Annotation tags

### `@known-defect`

The scenario documents behavior the analyst believes is a bug.

Comment convention:
- `BUG:` — What's wrong.
- `LIKELY INTENT:` — What the original developer probably meant.
- `ACTUAL:` — What the code actually does.

### `@accepted-risk`

The behavior looks wrong but is intentional.

Comment convention:
- `RATIONALE:` — The business reason this surprising behavior is correct.

### `@unverified-intent`

The analyst cannot determine whether the behavior is correct or incorrect.

Comment convention:
- `OBSERVATION:` — What the code does and why it's ambiguous.
- `NEEDS:` — What review or input would resolve the ambiguity.

## Per-level annotation form

| Level | Form |
|---|---|
| L0 | Inline HTML comments in prose: `<!-- INTENT?: <text> -->` |
| L1 | Prose annotations: `> @known-defect: <comment block>` |
| L2 | Gherkin tags on `Scenario:` blocks |
| L3 | Above + RID-tagged scenarios + audit enforcement |

## Annotation hygiene

Annotations are not permanent markers. They are work items.

- `@known-defect` counts should trend toward zero. Every one is a bug you know about but haven't fixed. CI can gate on a maximum count.
- `@unverified-intent` should be resolved within a bounded timeframe (default 30 days). These need stakeholder review, not code changes.
- `@accepted-risk` is stable. It documents a deliberate decision. It stays unless the business rule changes.

Configuration example (`.ffflow/audit.yaml`):

```yaml
auditors:
  spec:
    rules:
      known-defect-count:
        severity: warning
        max: 5
      unverified-intent-max-age-days: 30
```

Track annotation counts over time. They are the clearest measure of specification confidence. A project with 30 `@unverified-intent` tags has a different risk profile than one with 30 confirmed-correct scenarios.

## Why this matters

A regression test says "this input should produce this output." A defect-driven spec says "this business rule exists, it was violated, and here is the invariant expressed in domain language."

The regression test lives in a test file. The spec lives in the behavioral contract — traceable by RID at L3, readable by stakeholders, enforced by audit.

The invariant that was previously implicit is now explicit. It cannot be silently broken. It cannot be accidentally removed.

## Anti-patterns

- Fixing the bug without writing the invariant. The next person re-implements the bug.
- Using `@accepted-risk` for things you didn't bother to fix. That's `@known-defect`.
- Leaving `@unverified-intent` un-resolved past the configured age. Either fix it or accept it.
- Removing `@known-defect` when you didn't actually fix the code. Audit will catch the lie.

## Friction addressed

- Bug fixes that ship without anything stopping the same bug from re-emerging.
- Invariants buried in code comments instead of the spec.
- Recurring "is this intentional?" arguments because the original intent isn't recorded.
