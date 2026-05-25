---
name: spec-first-development
description: The steady-state development loop — spec change drives implementation, producing both step definitions and unit tests. L2+ reference rulebook.
---

# spec-first-development

## Purpose

Reference rulebook (L2+). Loaded as context by `work-issue` and `plan-chat` when the project is at L2 or higher. Describes the spec → red → green → audit loop with explicit spec changes.

## The core loop

```
1. Spec change        — edit .feature files
2. Audit fails        — reality no longer matches specification
3. Implementation     — step definitions + unit tests + production code
4. Audit passes       — reality matches specification again
```

The spec diff IS the change request. A non-technical stakeholder reads the Gherkin diff and sees exactly what changes. No tickets required. No ambiguity.

Step 3 produces two kinds of tests. Step definitions bind Gherkin scenarios to code. Unit tests verify internal logic, edge cases, and implementation correctness. Both suites must pass. Both coverage thresholds must be met.

This inverts the traditional flow. Traditional: code changes, documentation catches up or doesn't. Spec-driven: documentation changes first, code catches up, audit enforces that it does.

## What triggers a spec change

**New feature.** Add scenarios describing desired behavior. No step definitions exist yet. Audit fails. Write step definitions and code. Audit passes.

**Bug fix.** The scenario already exists, tagged `@known-defect`. Change it to describe correct behavior. Remove the tag. Audit fails because code still does the wrong thing. Fix the code. Audit passes. (See `defect-driven-specification`.)

**Behavioral change.** Modify existing scenarios. The diff shows before and after in business language.

**Removing functionality.** Deprecate with `@deprecated` tag and comment, or delete outright. The RID is retired and never reused (L3).

**Resolving `@unverified-intent`.** After stakeholder review, reclassify to `@accepted-risk` or remove the annotation. No code changes needed.

## Implementation produces both test types

A spec change to add password length validation results in:

- **Step definitions** that bind the Gherkin scenario to domain code.
- **Unit tests** for boundary conditions, error messages, and edge cases the spec doesn't enumerate.

The spec says "passwords below 12 characters are rejected." The unit tests verify the exact boundary at 11 and 12, empty strings, maximum length, Unicode handling. Different concerns. Both essential.

## The spec diff as change request

A traditional change request is prose in a ticket. A spec diff is structured natural language, diffable in standard tools, more precise than prose.

The spec diff shows exact boundary values, exact error messages, and explicit edge cases. The prose ticket mentions acceptance criteria. The spec diff specifies them with examples.

## Discovery during implementation

Sometimes implementation reveals the spec was incomplete. This is normal.

```
Spec change → Implementation begins → New case discovered →
  → Spec amended → Implementation continues → Audit passes
```

Rules for mid-implementation spec changes:

1. Add new scenarios. Don't silently modify reviewed ones.
2. If an existing scenario was wrong, change it but note why in the PR body.
3. Property specs often grow during implementation (edge cases around Unicode, max length, null bytes). Expected.
4. The final PR includes all spec changes. The reviewer sees the full delta.

## PR shape

The FFFlow default (per `work-issue` and architecture §2.2): **spec and code ship in the same PR.**

The PR body cites:
- The originating issue.
- The spec sections changed (with diff hunks).
- The tests added.
- Audit status per applicable auditor.

This default beats the older two-PR pattern (spec PR then implementation PR) because:
- Reviewers see the whole change at once.
- Specs can't drift while waiting for the implementation PR.
- `work-issue`'s local-validation gate has both pieces available.

The older two-PR option remains for very large spec changes where the spec itself needs cross-stakeholder review before implementation. Use rarely.

## Git workflow

Commit prefixes tell the story:

```
spec: increase minimum password length to 12 characters
feat: implement 12-character minimum password length
spec: add edge case for passwords at exactly 12 characters
feat: handle 12-character boundary in password validation
```

`spec:` commits are behavioral decisions. `feat:` commits are implementation. The history reads as a narrative: decision, execution, discovery, more execution.

## Multi-context changes

Some features span multiple bounded contexts. Each context gets its own spec changes. The audit checks each context independently, so partial implementation is visible.

Don't write scenarios spanning multiple contexts. Each scenario is testable within its context. Integration between contexts is verified at the acceptance level or through contract testing (see `contract-enforcement`).

## The audit gates the PR

CI runs `/audit --ci` on every PR. Every spec change has step definitions and passing tests. Every code change maintains existing spec compliance. Coverage thresholds are met. No structural violations.

A PR that changes specs without implementing them fails. A PR that breaks existing specs fails. The audit is the automated enforcer.

## Anti-patterns

- Changing code without changing the spec it's specified by. The spec drifts.
- Squashing the spec commit and the implementation commit into a single mystery diff. Keep the narrative.
- Writing scenarios that cross contexts. They become harder to test and to read.
- Treating mid-implementation spec amendments as failures of the original plan. They're discoveries, expected, and the loop accommodates them.

## Friction addressed

- Tickets that describe behavior in vague prose while the code does something else.
- "Where did this rule come from?" — git log on the .feature file is the answer.
- Spec drift between sprints.
