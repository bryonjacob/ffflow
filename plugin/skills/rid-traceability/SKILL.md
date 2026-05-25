---
name: rid-traceability
description: Requirement ID format, assignment, uniqueness, and audit enforcement — the traceability backbone of FFFlow. L3 reference rulebook.
---

# rid-traceability

## Purpose

Reference rulebook (L3). Loaded as context by `work-issue`, `/audit --type rid`, `/audit --type spec`, and `writing-specs` when the project is at L3. Not invoked as a tool.

A Requirement ID is a tag on a scenario. It is the anchor point for all traceability in FFFlow. At L3, every scenario gets one. No exceptions.

A Requirement ID is a tag on a scenario. It is the anchor point for all traceability in FFFlow. Every scenario gets one. No exceptions.

## Format

```
@RID-{CONTEXT}-{NAME}-{NNN}
```

- **RID** — Fixed prefix. Always present.
- **CONTEXT** — Bounded context. Upper-case letters and hyphens. Matches the first directory segment under `specs/`.
- **NAME** — Descriptive label. Upper-case letters and hyphens.
- **NNN** — Three-digit zero-padded sequence number.

Examples:

```
@RID-AUTH-LOGIN-001
@RID-AUTH-PASSWORD-003
@RID-ORDER-CHECKOUT-001
```

## Rules

RIDs follow four rules. Break one and the audit fails.

1. **Every scenario has an RID.** No untagged scenarios pass audit.
2. **RIDs are unique.** No two scenarios share the same RID across the entire project.
3. **RIDs are immutable.** Once assigned, an RID never changes meaning. If the requirement changes, create a new RID.
4. **RIDs are never reused.** Delete `@RID-AUTH-LOGIN-002` and 002 is retired permanently.

## Context Matches Directory

The CONTEXT segment must match the first directory under `specs/`. A scenario in `specs/auth/login.feature` must carry an RID starting with `@RID-AUTH-`. This is not a suggestion. `specdrive audit` enforces it.

## Placement

RIDs go on scenarios. Not on features. Not on rules.

```gherkin
Feature: Password validation         # No RID here
  Rule: Minimum complexity            # No RID here
    @RID-AUTH-PASSWORD-001            # RID here
    Scenario: Valid password accepted
```

Features and rules are organizational. Scenarios are the testable units. RIDs tag testable units.

## Assignment

RIDs are assigned when a scenario is written. Pick the next available number for a given CONTEXT-NAME pair by scanning existing `@RID-*` tags. (If your `specdrive` distribution provides a helper for this, use it; otherwise scan manually — the audit catches collisions either way.)

## Deprecation

Requirements retire. They do not vanish. Mark the scenario with `@deprecated` alongside its RID:

```gherkin
@RID-AUTH-LOGIN-002 @deprecated
Scenario: Login with username (deprecated — use email login)
```

The scenario stays in the spec. The audit logs a warning instead of an error. The RID remains reserved.

## The Traceability Chain

RIDs connect three things:

1. **Spec** — The Gherkin scenario carries the RID as a tag.
2. **Test** — The test runner picks up the tag. Property-based or deterministic, the RID propagates into JUnit XML via `specdrive init` bridging hooks.
3. **Code** — Coverage maps trace executed lines back through tests to their RIDs.

The chain is: spec tags a scenario with an RID, test inherits the tag, coverage links the tag to source lines. `specdrive audit` walks the chain and reports gaps.

No RID, no traceability. No traceability, no proof the code does what the spec says.

## Audit Enforcement

`specdrive audit` checks five things:

- Every scenario has an RID tag.
- Every RID matches the `@RID-{CONTEXT}-{NAME}-{NNN}` format.
- Every CONTEXT matches its directory under `specs/`.
- No RID appears more than once.
- Deprecated RIDs warn but do not fail.

Run it in CI. A single violation fails the build.
