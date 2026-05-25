---
name: work-fanout
description: Parallel execution of multiple chess moves across worktrees. Spawns N subagents, each runs work in isolation, with stall detection and resume awareness.
---

# work-fanout

## Plan Mode

This skill does NOT invoke Plan Mode. It dispatches subagents that execute `work-issue`.

## Purpose

Run several `work-issue` instances in parallel, one per issue, each in an isolated worktree. Replaces hand-typed "have an agent team work on these four in worktrees" prompts.

## Inputs

- A list of issue IDs (`/work-fanout 101 102 103 104`), **or**
- An epic identifier (`/work-fanout --epic 100`) — discovers all open child task issues.
- `.ffflow/config.yaml` — read for level, stack, capture backend.

## Outputs

- One worktree per task under `worktrees/<task-id>/`.
- One subagent per task, running `work-issue` in its worktree.
- Optionally N PRs (some may still be in progress at end-of-run).
- A final fanout report distinguishing done / in-progress / stalled / failed.

## Dependencies

- `work-issue` — invoked by each subagent.
- `worktrees` — used to create the isolated copies.

## Cross-cutting invariants

### Pacing

Default: spawn **up to 2** subagents concurrently. Cap is conservative because each subagent is doing TDD plus reading files — heavy on context and rate limits. Two is the safe default; users with light tasks can `--concurrency 4` or higher.

User can override with `--concurrency N`.

### PR-checkpoint protocol applies globally

The 2-PR checkpoint from `work-issue` applies across the whole fanout — when the **cumulative** PR count across subagents hits 2, the orchestrator (this skill) pauses for confirmation, regardless of which subagent created them. The `y/n/disable` semantics from `work-issue` apply here too: `disable` turns off checkpointing for the rest of the fanout run.

### Stall detection

A subagent that has been silent for **> 10 minutes** without producing a commit or a status message gets flagged as `stalled`. The orchestrator sends a single nudge ("you OK? status?"). If still silent after another 5 minutes, marks the task as `stalled` in the report and moves on.

## Flow

### 1. Resolve task list

- Direct issue IDs: use as-is.
- `--epic N`: `gh issue list --label epic-N --state open` (or equivalent for non-GH backends).
- Dedupe; sort by `depends_on` so prerequisites schedule first.

### 2. Resume awareness

For each task:

- Check `worktrees/<task-id>/` — exists with PR?
  - **PR merged** → task done. Skip.
  - **PR open** → resume this subagent (give it the existing worktree).
  - **PR draft, stalled** → resume with explicit "previously stalled" briefing.
- Check `worktrees/<task-id>/` — no worktree yet?
  - Create from main.

### 3. Spawn subagents

For each ready task (deps satisfied):

```
Agent(subagent_type=Plan or Claude, prompt=<work briefing>, cwd=<worktree>)
```

Briefing template:
```
You are working task <id> in worktree <path>. Your single job is to run /work-issue <id>.
Follow that skill's protocol exactly. When you finish (PR opened or stalled), report back.
Do NOT invoke /work-fanout again. Do NOT touch worktrees for other tasks.
```

Use background mode so the orchestrator can supervise without blocking.

### 4. Supervise

Watch for completion notifications. For each subagent:

- **Reports PR opened** → mark done; increment global PR counter.
- **Reports stalled/blocked** → mark stalled with reason.
- **Silent > 10 min** → send nudge.
- **Silent > 15 min** → mark stalled, move on.

When global PR counter hits 2 between checkpoints: pause for "continue?" gate.

### 5. Schedule deps

When a task with dependents finishes (PR merged or marked done), unblock those dependents and spawn them.

### 6. Final report

```
work-fanout report (4 tasks):

  done:
    task-1 → PR #201 (merged)
    task-2 → PR #202 (open, green)

  in-progress:
    task-3 → PR #203 (draft, gates failing on lint)

  stalled:
    task-4 → silent for 17 min after Phase 2 — possible test framework issue

Next:
  - review #202 for merge
  - look at #203's gate failures
  - investigate task-4 manually (worktrees/task-4/ retained)
```

## Worktree cleanup

- Successful tasks (PR merged): offer to remove the worktree.
- Open/stalled tasks: retain — the user may want to inspect.
- Failed tasks: always retain. User decides.

## Edge cases

- **Two tasks edit the same spec file**: merging will conflict. Flag at scheduling time; offer to serialize them rather than parallelize.
- **All tasks fail the same way**: there's a system-level issue (stack, env, deps). Surface as a single error rather than four.
- **An "epic" with 30 tasks**: default cap of 2 means it'll take many rounds. Tell the user the expected wall-clock estimate before starting, and suggest `--concurrency 4` if tasks are light.

## Anti-patterns

- Don't run without `.ffflow/config.yaml`. Subagents need to know the level/stack.
- Don't spawn more than `concurrency`. Heavier work makes the rate-limit risk real.
- Don't auto-merge anything. Even green PRs sit until human (or `autopilot` with prior authorization) merges.
- Don't share state between subagents. The whole point of worktrees is isolation.
- Don't lose the stall reason — preserving it is what makes the report useful.

## Friction addressed

- The weekly hand-typed "have an agent team work on these four" prompt.
- Confusion about which agent's worktree is which.
- Silent failures buried in subagent transcripts.
