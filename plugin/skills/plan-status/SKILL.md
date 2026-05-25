---
name: plan-status
description: Show in-flight plans for this project — phase, what's done, what's next. Reads from /tmp/ffflow-plans/<project-hash>/.
---

# plan-status

## Purpose

A one-glance snapshot of every plan for this project. Useful after a `/clear` or when returning to a project after a few days.

Plans live in `/tmp/ffflow-plans/<project-hash>/<slug>/` (transient, addressed by `sha256(pwd) | head -c 16`). This skill scans that directory.

## Inputs

- Current working directory (used to compute the project-hash).
- Optional flag `--cleanup` to remove `captured` plans after confirmation.
- Optional flag `--archive <slug>` to copy a plan dir into `.ffflow/plan-archive/<slug>/` for long-term retention.

## Outputs

Console report. Optionally side-effects on `/tmp/ffflow-plans/<hash>/` (with `--cleanup`) or `.ffflow/plan-archive/` (with `--archive`).

## Flow

### 1. Compute path and scan

```bash
PROJECT_HASH=$(pwd | sha256sum | cut -d' ' -f1 | head -c 16)
PLAN_ROOT="/tmp/ffflow-plans/$PROJECT_HASH"
```

- Glob `$PLAN_ROOT/*/metadata.json` for active session plans.
- Also scan `docs/roadmap/*/` for committed (captured) roadmaps. These don't have `metadata.json` in `/tmp/` if the cache was cleared — they're the durable record.

If both sets are empty:
```
No in-flight plans for this project.
Next: /plan-chat to start one (or /plan-roadmap for phase-level planning).
```

### 1a. Re-hydration check

For each `docs/roadmap/<slug>/` found in the repo:

- If `$PLAN_ROOT/<slug>/` exists too: session cache is present; report normally.
- If `$PLAN_ROOT/<slug>/` is **missing** (e.g., `/tmp/` got cleared, fresh machine, fresh container): the durable record is in the repo but the session cache is gone. Offer to re-hydrate:

  ```
  Found committed roadmap docs/roadmap/<slug>/ but no /tmp/ cache.
  Re-hydrate session cache from repo? (y/n)

  This copies docs/roadmap/<slug>/{roadmap.md,decisions.md,phases/}
  back into /tmp/ffflow-plans/<hash>/<slug>/ so /plan-roadmap --phase N
  and other resumable flows work.
  ```

  On `y`: copy the files, reconstruct `metadata.json` with `phase: captured` (the durable state implies prior capture), and report the re-hydrated plan in the main status listing.

  On `n`: continue with status report; user can re-hydrate later.

Re-hydration is the completion of the durability story: roadmap rationale survives `/tmp/` clears because it's in the repo, and `plan-status` knows how to bring it back into the session cache when the user needs to extend or recurse into a phase.

### 2. For each plan

Read `metadata.json` plus sanity check files on disk:
- `plan.md` present?
- `decisions.md` present? Any open `?` markers?
- `tasks/` populated? How many?
- `captured.json` present?

### 3. Report

```
<plan-dir>/auth-token-refresh/
  Phase: chat-complete
  Level: L1
  Created: 2026-05-19
  Open decisions: 2 (?-marked in decisions.md)
  Next: /plan-chat   # resume to resolve open decisions

<plan-dir>/password-rules/
  Phase: breakdown-complete
  Level: L1
  Created: 2026-05-18
  Tasks: 4 (no captured.json)
  Next: /plan-capture

<plan-dir>/email-receipts/
  Phase: captured
  Level: L0
  Created: 2026-05-15
  Captured: 3 issues → github-issues (#42 #43 #44)
  Next: /work-issue 42  (or /plan-status --cleanup email-receipts)
```

### 4. Cleanup mode

`/plan-status --cleanup` removes captured plans:
- For each plan in `phase: captured`, ask the user to confirm deletion.
- Delete outright. The durable record is in the tracker; the plan dir is the workshop floor.
- Don't touch plans not yet captured.

### 5. Archive mode

`/plan-status --archive <slug>` copies a plan dir into `.ffflow/plan-archive/<slug>/`:
- Use when you want a plan to survive `/tmp` cleanup before it's captured (rare — almost always means "capture it instead").
- Doesn't move; copies. The `/tmp` dir is still authoritative until captured.
- Adds `.ffflow/plan-archive/` to `.gitignore` if not already there.

## Phase → next-command map

| Phase | Next command |
|---|---|
| `chat-incomplete` | `/plan-chat` (resumes the slug) |
| `chat-complete` (with open `?`) | `/plan-chat` (chat doesn't close until `?`s resolved) |
| `chat-complete` (clean) | `/plan-breakdown` |
| `breakdown-complete` | `/plan-capture` |
| `captured` | `/work-issue <issue>` or `/plan-status --cleanup <slug>` |

## Error handling

- Missing `metadata.json`: list the dir, surface as `metadata-missing`, suggest manual inspection.
- Corrupted JSON: surface as `corrupted`, suggest manual fix.
- `/tmp/ffflow-plans/<hash>/` doesn't exist: report no plans found (not an error — first run).

## Anti-patterns

- Don't auto-clean — `--cleanup` is opt-in and asks per plan.
- Don't suggest `/plan-chat` for a fresh start when an existing plan is `chat-incomplete`; `/plan-chat` resumes the slug.
- Don't read the full `plan.md` contents — summary only. The user can `cat` the path if needed.
- Don't promote archives into the durable record. The tracker is durable; `.ffflow/plan-archive/` is just a longer-lived workshop floor.
