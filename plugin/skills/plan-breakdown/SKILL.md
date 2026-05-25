---
name: plan-breakdown
description: Cut a sealed plan into independently shippable chess moves — each task is a spec slice with explicit scope, dependencies, and acceptance criteria.
---

# plan-breakdown

## Plan Mode

This skill does NOT invoke Plan Mode. Task files are written directly.

## Purpose

Take a sealed plan and slice it into 3–8 independently-shippable tasks ("chess moves"). Each task becomes one PR, one branch, one issue.

## When to invoke

- After `plan-chat` has sealed the plan (zero open `?` markers).
- Re-run to refine task boundaries before capture.

## Inputs

- Path to a plan directory (`<plan-dir>/`). If only one in-flight plan exists, default to it.
- `.ffflow/config.yaml` — read for level (changes the task body schema).

## Outputs

- `<plan-dir>/tasks/task-1.md`, `task-2.md`, … one file per chess move.
- `<plan-dir>/metadata.json` updated to `phase: breakdown-complete` with a tasks array.

## Dependencies

None directly. Level-aware reference to methodology skills only.

## Hard gates

**Refuses to run if:**

1. `<plan-dir>/decisions.md` has any open `?` markers — tells the user to resume `plan-chat` to resolve them (`plan-chat` doesn't seal until they're all answered).
2. `<plan-dir>/metadata.json` shows `phase: chat-incomplete` — tells the user to finish `plan-chat` first.

These are non-negotiable. Plans get decomposed only after they're sealed.

## Flow

### 1. Load context

- Read `plan.md`, `decisions.md`, `metadata.json`.
- Read any draft spec delta or Gherkin files in the plan dir.
- If the plan references existing spec entries (e.g., "extends `docs/specs/auth.md` Rule 3"), open those too.

### 2. Propose task boundaries

A good chess move is:

- **Freestanding.** Mergeable on its own without breaking main.
- **Bounded.** Explicit out-of-scope list. The next agent doesn't have to guess.
- **Red/green-able.** A test can be written that fails before the code is written, and passes after.
- **One behavior.** Adds or modifies one Rule (L2+) or one prose spec section (L0/L1).

Propose 3–8 tasks. Present them to the user as a short list:

```
Proposed tasks:
  1. Add password complexity Rule + validator port (no UI changes)
  2. Wire password validator into signup adapter
  3. Add token-refresh threshold logic (depends on 1)
  4. Update CLI auth flow to use new validator (depends on 2)

Looks right? Anything to split, merge, or reorder?
```

Iterate with the user until they confirm.

### 3. Write task files

One file per chess move. Body shape varies by level:

#### L0 (prose)

```markdown
# Task 1: Add password complexity validator

## Behavioral scope
Spec: `docs/specs/auth.md` §"Password complexity" (new section to be written).

The system rejects passwords that are < 8 chars or contain no digit.

## Implementation scope
- New module: `src/auth/password_validator.py`
- Modified: `src/auth/signup.py` — call validator before persisting.
- Test: `tests/auth/test_password_validator.py`.

## Out of scope
- UI error messaging changes (see task 4)
- Existing password migration

## Acceptance
- [ ] Validator rejects passwords matching the rules above.
- [ ] Signup integration uses the validator.
- [ ] All existing auth tests still pass.
- [ ] Spec section written and committed in the same PR.

## Depends on
None.
```

#### L1 (prose + layer mapping)

Adds:
```markdown
## Hexagonal layer
- Domain: `PasswordPolicy` value object (pure)
- Application: `PasswordValidatorPort` interface
- Infrastructure: `RegexPasswordValidator` adapter
```

#### L2 (Gherkin scope)

```markdown
## Behavioral scope
Spec: `docs/specs/auth.feature` Rule "Password complexity".
Scenarios: 3 new (covering happy path, too-short, no-digit).

## Step definitions
New: `Given a user submitting password <pw>`, `Then signup is <result>`.
```

#### L3 (full Gherkin + RIDs + property tests)

```markdown
## Behavioral scope
Spec: `docs/specs/auth.feature` Rule "Password complexity".
RIDs: @RID-PWD-001 through @RID-PWD-003.
Property tests: @property-based scenario covering random strings against the policy.

## Mutation testing
This module must reach 80% mutation score before merge.
```

Each task ends with:
- `## Out of scope` — explicit boundary.
- `## Acceptance` — checklist.
- `## Depends on` — other tasks by id, or "None."

### 4. Interactive review

For each task, ask:
- Is this freestanding? (Could it merge alone?)
- Is the out-of-scope list honest? (No scope creep?)
- Is the test writable before the code? (If no, rewrite the task.)

Iterate. Don't move on until the user signs off.

### 5. Update metadata and report

`metadata.json`:
```json
{
  "phase": "breakdown-complete",
  "tasks": [
    {"id": "task-1", "title": "...", "depends_on": []},
    {"id": "task-2", "title": "...", "depends_on": ["task-1"]}
  ]
}
```

Report:
```
✓ <plan-dir>/ → 4 tasks
Next: /plan-capture
```

## Resume

Re-running:
- If `phase: breakdown-complete` and user wants to refine, allow edits to existing task files in place. Don't duplicate.
- If new tasks appear, append them with the next index.

## Friction addressed

- Plan-then-breakdown loops where breakdown reveals new design questions (caught by the `?` hard gate).
- Tasks that look done but leave PR authors archaeologizing the original plan (each task is self-contained).
- Scope creep mid-PR (explicit out-of-scope list).

## Anti-patterns

- Don't write infrastructure-only tasks ("set up CI") — those go in `stack-init`.
- Don't write test-only tasks at L2+ — tests travel with the implementation. Exception: characterize backfill tasks, which are intentionally tests-only.
- Don't propose 12 tiny tasks. Anything more than 8 means the plan was too big.
- Don't strand the spec change. Each task's PR carries its spec delta.

## Quality checks before sealing

- [ ] 3–8 tasks.
- [ ] Each task maps to specific spec content (sections, Rules, or RIDs).
- [ ] No spec content left unassigned.
- [ ] Each task is freestanding or has explicit `depends_on`.
- [ ] `out_of_scope` field non-empty for every task.
- [ ] `metadata.json` shows `breakdown-complete`.
