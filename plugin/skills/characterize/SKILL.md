---
name: characterize
description: For an unspec'd codebase, walk it module-by-module to extract an evergreen spec (committed immediately) and produce a plan for characterization-test backfill.
---

# characterize

## Plan Mode

This skill does NOT invoke Plan Mode. It writes spec files directly and creates a plan directory like any other planning flow.

## Purpose

Most existing projects don't have specs. `characterize` extracts the behavioral contract from what's already there. Two outputs:

1. **Evergreen spec, committed directly.** Describes what the code does in present tense. Single mechanical chess move; no autonomy needed.
2. **Plan** in `<plan-dir>` whose tasks add characterization tests. Tests are queued for `/work-issue` like any other plan.

The spec layer is **additive** — existing tests stay. Specs document behavioral contract in domain language; tests verify implementation correctness.

## Inputs

- Optional target module/directory (`/characterize src/auth`). Default: full project.
- `.ffflow/config.yaml` — read for level (determines annotation style and spec format).

## Outputs

- Spec entries written to the project's spec location and committed (one commit per module).
- `<plan-dir>` with `plan.md` and `tasks/` for test backfill (slug = `characterize-<target>`).
- `.ffflow/audit.yaml` updated: each new spec entry registered with `characterized: true`.

## Dependencies

- `defect-driven-specification` — loaded for annotation conventions at L1+. This skill does not restate them.
- `writing-specs` (L2+) for Gherkin conventions.
- `hexagonal-architecture` (L1+) for layer mapping.
- `tdd-loop` — referenced in test-backfill task content.

## Resumability

State persists in `<plan-dir>/state.json` between phases. On resume, read state and jump to the current phase.

## The five phases

### Phase 1 — Survey

Internal-only. Read project structure, existing CLAUDE.md, existing tests at-a-glance for coverage estimate, recent git history (last 50–100 commits) for hot spots, existing docs.

Identify: architectural shape (hex/layered/flat), bounded contexts (vocabulary + module boundaries), test density per module.

Report once:

```
Survey complete:
  - 14k LoC across 28 modules.
  - Hexagonal-ish: src/{domain,application,infrastructure}.
  - Bounded contexts (estimate): auth, billing, search, notifications.
  - Test density: auth 70%, billing 85%, search 30%, notifications 0%.
  - Stable candidates (unchanged 18+ months): 3 modules.

Suggested order: billing → auth → search → notifications.
```

**Default attack order: safest first** (most stable + best-tested modules). Builds confidence, low rework risk. The user can override toward "most critical first" if appetite warrants.

### Phase 2 — Propose shape

Based on level and survey:
- **Spec layout**: L0/L1 prose under `docs/specs/<context>.md`; L2+ Gherkin under `specs/<context>.feature` with `specs/{acceptance,application,domain}/`.
- **Module-to-spec mapping**: which module's behavior lands in which spec file.
- **Order of attack**: per safest-first default above; user confirms or overrides.

Write proposal into `state.json`, commit empty scaffolding files (placeholder + heading per context).

### Phase 3 — Walk module-by-module

For each module in the agreed order:

1. **Read the code.** Identify behavioral rules: validation, state transitions, calculations, invariants, error handling.

2. **Propose rules in present tense.** "The system rejects emails without `@`." Not imperative ("Reject emails…"), not vague ("Validates emails"). Present-tense is the FFFlow voice.

3. **Identify judgment-call points** and disposition with the user per `defect-driven-specification` annotation rules (`@known-defect`, `@unverified-intent`, `@accepted-risk`, or no annotation — that skill defines tags, comment conventions, and per-level form). This skill does not restate them; load the rulebook.

4. **Write the spec, commit, register.** One commit per module — message names the module. Then update `.ffflow/audit.yaml` under `auditors.spec.files` with `characterized: true` and `characterized_by_session: <ts>` so `/audit --type spec` knows these are characterization-style.

Why per-module commits: the spec is the chess move; resumability matters; the audit surface comes online incrementally.

### Phase 4 — Test gap analysis

Compare spec to current test coverage:

| Category | Action |
|---|---|
| Well-tested (spec'd behavior pinned by tests) | None |
| Weakly tested (key paths or annotations unproven) | Backfill task: strengthen |
| Untested | Backfill task: write |

Use the stack's coverage tool where available. Output a structured gap list ready to become tasks.

### Phase 5 — Build the plan, decide on breakdown

1. Create `<plan-dir>` (slug = `characterize-<target>`), write `plan.md`:
   - **Problem**: "<module> behaviors are spec'd but not pinned by tests; regressions ship silently."
   - **Approach**: characterization-style TDD (red is replaced by "confirms the existing behavior").
   - **Path**: per-module task list.

2. Write `decisions.md` (any deferred `?` markers stay open — `plan-breakdown` will refuse if so; user resumes `plan-chat` to resolve them, or characterize asks here).

3. Write `tasks/task-N.md` files: one per gap from Phase 4, with backfill scope, acceptance, and dependencies.

4. **Decide on breakdown.** If the tasks emerged cleanly from Phase 4 (one task per gap, freestanding, bounded), mark `phase: breakdown-complete` directly — skip `plan-breakdown`. If they need further slicing or grouping, mark `phase: chat-complete` and direct the user to `/plan-breakdown`. Default: skip when gap-list-to-tasks is 1:1.

5. Optionally include "stakeholder-review" tasks for behaviors dispositioned as `@unverified-intent`.

6. Print:
   ```
   Spec committed: <N> entries across <M> modules.
   Plan: <plan-dir>  (<K> backfill tasks, phase: breakdown-complete)
   Next: /plan-capture
   ```

   Or, when breakdown was skipped to chat-complete:
   ```
   Plan: <plan-dir>  (phase: chat-complete — needs further slicing)
   Next: /plan-breakdown
   ```

## Principles

- **Specs are additive.** Existing tests stay.
- **Present tense.** "The system rejects X" — not imperative, not vague.
- **AI proposes, human dispositions.** Don't assume intent.
- **Commit per module.** Small commits; resumable; auditable.
- **Safest first.** Build confidence before tackling scary modules.

## Anti-patterns

- Writing spec for code you didn't read carefully.
- Skipping disposition ("looks fine, moving on") — that's how `@known-defect` ships unannotated.
- Bundling modules into one commit. Resumability dies.
- Generating tests in this skill. Tests belong in the plan; `/work-issue` executes them.

## Friction addressed

- Brownfield adoption stalling because "no specs yet" feels too big.
- Conflating spec extraction with test backfill (different chess moves).
- Spec drift on day 1 because nothing registered the new spec in audit state.
- Forced `plan-breakdown` step even when gaps already mapped 1:1 to tasks.

## Quality checks before handoff

- [ ] Every spec'd module is in `.ffflow/audit.yaml` under `auditors.spec.files`.
- [ ] Every annotated scenario has an explanatory comment (per `defect-driven-specification`).
- [ ] Spec commits are present, one per module.
- [ ] `<plan-dir>` has `plan.md`, `decisions.md`, `tasks/*.md`.
- [ ] `metadata.json` reflects the actual phase (`chat-complete` or `breakdown-complete`).
