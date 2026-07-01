---
name: refactor
description: Coverage/complexity-driven refactoring. Identify targets, refactor under green tests. Generates plan tasks rather than ad-hoc edits.
---

# refactor

## Purpose

Improve maintainability by finding the right targets first, then refactoring under green tests. Uses the stack's coverage and complexity tools to pick what to touch.

Produces a refactor plan via `audit --plan` (when invoked through the refactor cartridge) or directly via this skill (when invoked standalone).

## When to invoke

- Standalone: "I want to clean up this module."
- Indirectly: `/audit --type refactor` surfaces findings; `audit --plan` generates a refactor plan.

## Inputs

- Optional target directory or module (`/refactor src/auth/`). Default: scan the whole project.
- `.ffflow/config.yaml` for stack and thresholds.

## Outputs

- A refactor plan in the canonical transient plan dir — `/tmp/ffflow-plans/<project-hash>/refactor-<slug>/` (project-hash from `sha256(pwd) | head -c 16`, same convention as `plan-chat`/`plan-status`). **Never write plan artifacts into the repo** (no `./plan/`); the plan dir is transient and `plan-status`/`plan-breakdown` locate it by the pwd-hash. Ready for breakdown and capture.
- Or, when used inline during `work-issue`, a list of small in-PR refactors with their justifications.

## Principles

- **Tests stay green throughout.** Tests must pass before, during (between commits), and after.
- **Small steps.** One refactor per commit. Easier to revert; easier to review.
- **Refactor with evidence.** Coverage and complexity tools pick the target, not gut feel.
- **Refactor until specifiable.** If a function is too complex to spec, it has too many responsibilities. Extract until each piece maps to one rule.

## Flow

### 1. Identify targets

**Invoke `/audit --type refactor`** to get the list of refactor candidates. It runs the stack's complexity/coverage/duplication tools and emits findings with severity and `impact / (complexity + 1)` ordering already applied.

```
/audit --type refactor
```

This skill does not reimplement the scanning logic. `/audit --type refactor` is the single source of truth for "what's worth refactoring." When invoked via `audit --plan`, the findings are already computed and ready to consume.

If you want to refactor a specific target the auditor didn't surface (e.g., a hunch you have), name it explicitly when invoking refactor and skip the audit step.

### 2. Confirm green

Before any refactor, confirm tests are green:

```bash
just check-all
```

If the suite isn't green, refactoring is forbidden until it is. The user's first task becomes "fix the failing tests."

### 3. Generate plan tasks

For each target, draft a task. One target ≈ one task ≈ one PR:

```markdown
# Task: Reduce complexity in src/auth/signup.py

## Behavioral scope
None. Pure refactor; no spec change.

## Implementation scope
- Functions: `signup_user`, `validate_signup_request`, `persist_signup`.
- Pattern: extract methods for validation and persistence phases.

## Out of scope
- Behavior change.
- Touching other modules with similar issues — separate tasks per file.

## Acceptance
- [ ] Complexity warnings on this file cleared.
- [ ] Existing tests pass with no modification.
- [ ] No new public API.
```

Refactor tasks always include the **no spec change** flag — they don't trigger spec audits. If a refactor would change observable behavior, it's not a refactor; it's a feature, and goes through `plan-chat`.

**Refactor tasks at L2/L3 have no spec/RID delta — this is expected, not a gap.** A pure refactor adds no new `.feature` Rule, scenario, or RID because behavior doesn't change. The **existing** RID scenarios are the guardrail: they must pass **unmodified** through the refactor. So when `plan-capture`/`work-*` see a refactor task with an empty "Behavioral scope," that is correct — do not treat the absent spec delta as missing coverage, and do not invent a RID to fill it. The task's acceptance is "existing RIDs still green, complexity/LoC target met," not "new RID added." (See `quality-gates` on spec liveness — a refactor keeps specs live without adding to them.)

### 4. Hand off to `plan-breakdown`

The generated `/tmp/ffflow-plans/<project-hash>/refactor-<slug>/` flows through the normal pipeline:

```
/plan-breakdown → /plan-capture → work
```

**Choosing the execution step:**

- **Multi-task epic** (the usual refactor case — several targets, one per file) → **`/work-epic`**: one feature branch, one squashed commit per task, one PR for the whole epic, you approve the merge. This is the right default for a refactor plan with more than one task.
- **Single task** → `/work-issue <issue>`.
- **Independent tasks you want in parallel worktrees** → `/work-fanout`.

Do not default to one-branch-per-task; a refactor epic ships as a unit.

## Common refactor patterns

- **Extract function** — break large functions into single-purpose units.
- **Guard clauses** — replace nested conditionals with early returns.
- **Extract constants** — replace magic numbers with named constants.
- **Extract port** — separate I/O from domain logic (hexagonal boundary). At L1+, this often resolves `/audit --type architecture` findings simultaneously.
- **Parameterize tests** — collapse repeated tests with different inputs (also resolves test-redundancy findings from `/audit --type refactor`).
- **Extract fixture** — repeated object setup → shared fixture (test refactor pattern).

## When NOT to refactor

- **Tests not green.** Fix them first.
- **Unclear behavior.** Read the code first; consider running `/characterize` if it's a black-box module.
- **Behavior must change.** That's a feature. Use `plan-chat`.
- **No coverage.** Write tests first. A refactor on uncovered code is gambling.

## Inline vs. plan

| When | Mode | Why |
|---|---|---|
| During `work-issue` on an unrelated task | Inline, in-PR, only if small and obvious | Stay scoped. Big refactors are separate tasks. |
| Triggered by `/audit --type refactor` findings | Plan via `audit --plan` | Findings deserve dedicated PRs. |
| Standalone "let's clean this up" | Plan via this skill | Same. |

## Anti-patterns

- Refactoring while making behavior changes in the same PR. Reviewers can't tell what's a behavior change vs. cleanup.
- "Refactoring" that adds new patterns/abstractions for hypothetical future needs. YAGNI.
- Refactoring a hot file as part of a feature PR. Hot files deserve their own PR.
- Skipping the green check at step 2 "because the failures are unrelated." They aren't, until proven otherwise.

## Friction addressed

- "We should refactor this someday" never becoming a task.
- Refactor PRs that quietly change behavior.
- Refactors that touch six unrelated files because the agent got curious.
