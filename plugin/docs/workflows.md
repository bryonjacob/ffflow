# Workflows

Authoritative source for workflow definitions is [`architecture.md`](architecture.md) §6. This doc is the friendly summary with worked examples.

## The lifecycle flows

### 1. Greenfield bootstrap (from a vision)

You have a vision (probably `project.md`) and an empty git repo.

```
/adopt-ffflow            Detects greenfield. Runs init-ffflow + stack-init,
                         then /plan-roadmap.
/plan-roadmap            Reads project.md, surveys the empty repo, proposes
                         ordered phases (Foundation → smallest slice → expansion).
                         Per phase: design-slice (→ plan-chat), characterize,
                         cleanup (→ audit --plan), or recursive roadmap.
                         Seals with zero open ?-markers.

# Then per phase, the roadmap's handoff invokes the tier-2 skill:
/plan-chat               Design the slice (for design-slice phases).
/plan-breakdown          Cut into 3–8 chess moves.
/plan-capture            Commit roadmap rationale to docs/roadmap/<slug>/ + write tasks to tracker.
/work-issue <issue>      Execute one chess move.
# (or /work-fanout for parallel; /work-epic for one PR per epic.)
```

The roadmap is the orientation; tier-2 sessions execute one phase at a time.

### 2. Brownfield bootstrap

You have an existing codebase and want to add FFFlow.

```
/adopt-ffflow            Detects brownfield. Runs init-ffflow + stack-init
                         (incremental, non-destructive), then /plan-roadmap.
/plan-roadmap            Surveys the codebase. For touched surfaces lacking
                         specs, phase 1 = characterize; subsequent phases are
                         design-slice on top.
/characterize <target>   Phase 1 handoff. Extract spec; queue backfill tasks.
/plan-breakdown          Cut backfill plan into tasks.
/plan-capture            Commit roadmap to docs/roadmap/ + write tasks to tracker.
/work-issue (or fanout)  Fill the safety net.
/audit                   Verify the net is intact; baseline locked.
```

Resumable. Modules can be characterized one at a time across sessions.

### 3. Adding a new capability to an existing project

You're not bootstrapping — the project is already on FFFlow — but the new thing is bigger than one slice.

```
/plan-roadmap            Tier-1 planning for the new capability. Surveys
                         touched surface; queues characterize phases if needed;
                         orders build phases by dependency.
# Then per phase:
/plan-chat → /plan-breakdown → /plan-capture → /work-* → /audit
```

### 4. Steady-state slice work (no roadmap needed)

You're adding or changing one behavior. Small scope.

```
/plan-chat               Design the change directly.
/plan-breakdown          Cut into chess moves.
/plan-capture            Write to tracker (and commit roadmap rationale if a roadmap exists).
/work-issue (or fanout)  Execute.
/audit                   Periodically.
```

This is the normal cadence once a project is well-established. Skip `/plan-roadmap` for single slices.

### 5. Maintenance loop

You want to find what's drifted and fix it.

```
/audit                   Finds drift / gaps / sanity issues.
/audit --plan            Convert above-threshold findings into a plan.
/plan-breakdown          Cut maintenance plan into chess moves.
/plan-capture            Write to tracker (and commit roadmap rationale if a roadmap exists).
/work-issue (or fanout)  Execute.
```

### 6. Single chess move

You have one specific thing to do, already scoped.

```
/work-issue <issue-id>   Autonomous execution of one task end-to-end.
```

## Two-tier planning, one downstream

**Tier 1** (`plan-roadmap`) is phase-level. Used for greenfield bootstraps, new capabilities, and re-orientations. Optional for single-slice work.

**Tier 2** is slice-level. Three entries, each handling one phase of a roadmap (or operating standalone):

- `characterize` — extract specs from existing code.
- `plan-chat` — design a slice.
- `audit --plan` — convert drift findings into a plan.

All four converge on the same downstream pipeline: `plan-breakdown → plan-capture → work-*`.

## The execution discipline

Every chess move executed by `work-issue` follows the same loop. (See [`architecture.md`](architecture.md) §2.6.)

1. Read the current spec and the chess move's acceptance criteria.
2. Write or update the test(s) that pin the new behavior.
3. Run them. They must fail. **(Red.)**
4. Write the minimum code to make them pass. **(Green.)**
5. Refactor under green if needed.
6. Update the spec to reflect the new behavior, in the same PR.
7. Run all gates appropriate for the project's level.
8. Open the PR.

At L0/L1 this is standard TDD. At L2 the test is a Gherkin scenario. At L3 the audit verifies the loop's completeness. The loop is the same; the artifacts scale.

## See also

- [`architecture.md`](architecture.md) §6 — full workflow definitions including the `characterize` phase detail
- [`audit.md`](audit.md) — the audit subsystem and how findings become plans
- [`levels.md`](levels.md) — what changes per level
