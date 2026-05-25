---
name: writing-specs
description: Gherkin 6 conventions for FFFlow — Feature structure, Rule blocks, Scenario Outlines, spec types by layer, property-based specs. L2+ reference rulebook.
---

# writing-specs

## Purpose

Reference rulebook (L2+). Loaded as context by `plan-chat`, `characterize`, and `work-issue` when a project is at L2 or higher. Not invoked as a tool.

Standard Gherkin 6. Domain language. Behavioral, not implementation-bound.

## Standard Gherkin 6

FFFlow uses standard Gherkin 6. No custom dialects. No extensions. No magic tags that alter parsing. The full keyword set: `Feature`, `Rule`, `Background`, `Scenario`, `Scenario Outline`, `Examples`, `Given`, `When`, `Then`, `And`, `But`.

If your tooling requires something beyond standard Gherkin, you are doing it wrong.

## Feature Structure

Every Feature file starts the same way. A title. A user story. No exceptions.

```gherkin
Feature: User account lockout
  As a security engineer
  I want failed login attempts to trigger account lockout
  So that brute force attacks are mitigated
```

The user story (`As a / I want / So that`) is mandatory. It answers who cares and why. Without it, the spec is an orphan — no one knows whose problem it solves.

Free-form prose can follow the user story to provide context, rationale, or cross-references. Not every feature needs it. Simple features can stand on the user story and well-named Rules alone.

## Rule Blocks

`Rule:` is the unit of specification. Each Rule names a single business rule, invariant, or behavioral boundary.

```gherkin
Rule: Account locks when failure threshold is reached
Rule: Successful authentication resets failure tracking
Rule: Lockout is irreversible through authentication attempts
```

Write Rule names as declarative statements. State what the system does, not how. Use domain language, not technical language. When a scenario fails, the Rule name tells a stakeholder which business rule broke.

A Rule with one Scenario is fine. Not every rule needs multiple examples.

## Scenario Guidelines

Scenarios are declarative. They describe WHAT happens, not HOW.

Good:

```gherkin
Scenario: Successful login with valid credentials
  Given a registered user with email "alice@example.com" and password "Str0ng!Pass"
  When the user logs in with email "alice@example.com" and password "Str0ng!Pass"
  Then the login succeeds
```

Bad:

```gherkin
Scenario: Login
  Given I open the browser
  And I navigate to "/login"
  And I type "alice@example.com" in the email field
  And I click the submit button
  Then I see the dashboard
```

No CSS selectors. No SQL queries. No API endpoints. No file paths. No implementation details of any kind. The moment you mention a class name or a URL path, the spec is coupled to an implementation that will change.

## Scenario Outline and Examples

When a rule applies across multiple input variations, use `Scenario Outline` with `Examples`. Each row is a distinct permutation. Hidden behavior becomes explicit.

```gherkin
Rule: Non-active accounts cannot authenticate

  Scenario Outline: Login rejected for non-active account states
    Given a registered user in "<status>" status
    When the user attempts to log in with valid credentials
    Then the login is rejected with reason "<reason>"

    Examples:
      | status    | reason            |
      | locked    | account_locked    |
      | suspended | account_suspended |
      | expired   | account_expired   |
```

## Spec Types by Layer

Spec type is determined by file location. No tags. No keywords. Convention only.

| File Location | Spec Type | What It Tests |
|---|---|---|
| `specs/{ctx}/domain/{name}.feature` | Entity or Value Object | Pure domain logic |
| `specs/{ctx}/domain/{name}-properties.feature` | Property | Universal invariants |
| `specs/{ctx}/application/{name}.feature` | Use Case | Application orchestration |
| `specs/{ctx}/{name}.feature` | Acceptance | Stakeholder-visible behavior |

### Entity Specs

Domain entities with state, lifecycle, and invariants. Rules describe state transitions and business policies. Scenarios involve temporal or stateful behavior. Lives in `specs/{ctx}/domain/`.

### Value Object Specs

Immutable domain objects defined by validation rules. Rules describe what is accepted and what is rejected. `Scenario Outline` with `Examples` is the workhorse here — enumerate the constraint permutations. Also lives in `specs/{ctx}/domain/`.

### Use Case Specs

Application-layer orchestration. How use cases coordinate domain objects and ports. Rules describe the use case contract: success paths, failure handling, side effects. These are the specs most accessible to non-technical stakeholders. Lives in `specs/{ctx}/application/`.

### Acceptance Specs

Stakeholder-visible behavior tested through the full application layer with infrastructure ports mocked. Lives at `specs/{ctx}/` — the context root. Traditional BDD territory.

## Property-Based Specs

Property specs describe universal truths. They use the `@property-based` tag and live in files with the `-properties.feature` suffix.

The natural language uses universal quantifiers: "any", "always", "never", "regardless of". Rules describe properties, not workflows. Scenarios read as universal claims.

```gherkin
Rule: Verification never produces false positives

  @property-based
  Scenario: Different passwords never verify as equal
    Given any two distinct valid passwords
    When one is created and verified against the other
    Then verification always fails
```

The spec says "any." The step definition uses Hypothesis or fast-check to generate hundreds of random inputs and verify the property holds for all of them. The spec is readable by anyone. The implementation is exhaustive.

## Specs Are Not Unit Tests

This is the critical distinction. Get it right.

A spec describes a behavioral rule at a higher level of abstraction. A unit test verifies a specific code path in a specific implementation.

**Spec scenario:** "Passwords must be at least 8 characters."

**Unit test:** "Password.validate() throws ValidationError with message matching /at least 8/."

The spec says what the system must do. The unit test says what a particular class does when you call a particular method. The spec survives a rewrite. The unit test does not.

Specs and unit tests are different tools for different jobs. Writing unit tests in Gherkin clothing — mentioning class names, method signatures, error types, return values — produces something that has the ceremony of BDD with none of the benefits. It is harder to read than a unit test and harder to maintain than a spec.

Write specs that a stakeholder could read. Write unit tests that a developer could debug. Do not confuse the two.

## Background

`Background:` establishes shared preconditions for all scenarios within its scope.

```gherkin
Background:
  Given the authentication system is available
```

Use it sparingly. If different Rules need different preconditions, place Background inside the Rule, not at the Feature level.

## What Does Not Belong in Feature Files

Feature files are implementation-independent behavioral specifications. Keep out:

- Library or framework choices
- Architecture decisions
- Code structure references
- Performance characteristics
- Deployment requirements

These belong in implementation documentation, not in specs that should be valid against any implementation of the same behavior.
