---
name: plan-capture
description: Capture a sealed plan as durable work. Two layers: roadmap rationale committed to docs/roadmap/<slug>/ in the repo (always, regardless of backend), and tasks pushed to the configured issue tracker (cartridges for github-issues, linear, jira, or markdown). Bidirectional traceability between repo and tracker.
---

# plan-capture

## Plan Mode

This skill does NOT invoke Plan Mode. Issue creation and repo commits happen directly.

## Purpose

Capture a sealed plan into durable form. The plan directory in `/tmp/` is transient; what comes out of this skill is permanent.

Two layers, two lifecycles:

| Layer | What it captures | Where it goes | Why |
|---|---|---|---|
| **Roadmap layer** | `roadmap.md`, `decisions.md`, `phases/*.md` | `docs/roadmap/<slug>/` in the repo | Rationale — the "why we built it this way" — outlives task completion. Belongs near `docs/specs/`. |
| **Task layer** | `tasks/task-N.md` | Issue tracker (or `docs/tasks/<slug>/` for markdown backend) | Chess moves — the transactional work-to-be-done. Belongs in the tracker. |

The roadmap layer always runs, regardless of which task backend is configured. Roadmap rationale is universal; only task representation varies by tracker.

## When to invoke

- After `plan-roadmap` has sealed a roadmap, or `plan-chat` + `plan-breakdown` have sealed a single-slice plan.
- Re-run to capture additional tasks added to the plan, or to re-sync after a roadmap update.

## Inputs

- Path to a plan directory. Either:
  - **Roadmap plan** in `roadmap-complete` state (contains `roadmap.md` + `phases/`).
  - **Single-slice plan** in `breakdown-complete` state (contains `plan.md` + `tasks/`).
- `.ffflow/config.yaml` — read for `capture` backend choice.

## Outputs

- **Roadmap-plan path:**
  - `docs/roadmap/<slug>/` committed to the repo: `roadmap.md`, `decisions.md`, `phases/phase-N.md` (each phase placeholder).
  - Per-phase tasks captured into the configured tracker; each phase's tasks share the phase as their epic-equivalent.
- **Single-slice path** (no roadmap, just `plan-chat` → `plan-breakdown` → here):
  - No `docs/roadmap/` write (no roadmap exists).
  - Tasks captured into the configured tracker under one epic.
- `<plan-dir>/captured.json` with the full identifier map (per-task, per-phase, per-roadmap).
- `phases/phase-N.md` (both in `<plan-dir>` and in `docs/roadmap/`) updated with a `## Captured tasks` section after task capture completes (see Artifact contract below).
- Per-issue back-link: each tracker task issue body cites `docs/roadmap/<slug>/phases/phase-N.md` (or `<plan-dir>/plan.md` for single-slice plans).

## Backends (cartridges)

The task-layer protocol is the same for all targets. API specifics live in cartridges under `cartridges/`:

| Config value | Cartridge | Task home |
|---|---|---|
| `github-issues` (default) | `cartridges/github-issues.md` | GitHub Issues |
| `linear` | `cartridges/linear.md` | Linear Projects + Issues |
| `jira` | `cartridges/jira.md` | Jira Epic + Stories |
| `markdown` | `cartridges/markdown.md` | `docs/tasks/<slug>/` in the repo |

Load only the cartridge matching `.ffflow/config.yaml capture:`. If the configured backend's cartridge is missing or unreadable, refuse and tell the user.

The roadmap layer is **not cartridge-specific** — it always commits to `docs/roadmap/<slug>/` regardless of which task backend is configured.

If `capture:` is unset, default to `github-issues` if `gh auth status` succeeds, otherwise `markdown`.

## Artifact contract (important — non-obvious)

Phase placeholder files (`phases/phase-N.md`) have a **two-write lifecycle**:

1. **Write at roadmap-seal time** — produced by `plan-roadmap`. Contains scope, success criteria, dependencies, kind, estimated tasks.
2. **Update once after task capture** — `plan-capture` rewrites the file to add a `## Captured tasks` section listing the created issues. After this update, the file freezes again.

These are the *only* two writes. The phase placeholder is not generally editable — it's a versioned record of "what we decided this phase was" + "what we captured for it." If the user wants to change the phase's scope after capture, they re-run `plan-roadmap` (which produces a new phase or updates the existing one, then `plan-capture` re-syncs).

This contract matters because `phases/phase-N.md` is committed to the repo at `docs/roadmap/<slug>/phases/phase-N.md`. Treating it as freely-editable creates merge surprises and breaks the traceability story.

## Flow

### 1. Validate state

- Read `.ffflow/config.yaml`. If missing, prompt user to run `/init-ffflow`.
- Read `<plan-dir>/metadata.json`. Acceptable phases:
  - `roadmap-complete` — has roadmap, will do both layers.
  - `breakdown-complete` — single-slice plan, will do task layer only.
  - Anything else → refuse.
- For roadmap plans: read `roadmap.md`, `decisions.md`, and every `phases/phase-N.md`.
- For all plans: read `<plan-dir>/tasks/task-*.md` (if any are present at this point — sub-roadmap phases may have tasks under `phases/phase-N/tasks/`).

### 2. Load the cartridge

Read `cartridges/<capture-value>.md`. If missing, stop. Do not silently fall back — the user chose their backend for a reason.

### 3. Idempotency check

If `<plan-dir>/captured.json` exists from a previous run:
- For each task already captured, update the existing issue (body may have changed since spec updates).
- For new tasks, create per the cartridge.
- For the roadmap layer: re-write `docs/roadmap/<slug>/` files only if their content has changed. Don't churn commits on no-ops.

### 4. Roadmap-layer capture (roadmap plans only)

Before touching the task layer:

1. Create `docs/roadmap/<slug>/` if it doesn't exist.
2. Copy `roadmap.md`, `decisions.md`, and every `phases/phase-N.md` into it.
3. Stage the changes (`git add docs/roadmap/<slug>/`). **Do not commit** — the user owns the commit. Print a one-line summary at the end so they know to commit.

Why no auto-commit: this skill might be invoked mid-PR for a related change; auto-committing surprises the user with a non-related diff. The repo write happens; the commit decision is theirs.

### 5. Task-layer capture per cartridge

Walk each phase (for roadmap plans) or the plan as a whole (for single-slice plans), invoke the cartridge for each task:

- The cartridge supplies API specifics (CLI commands, body shape variations, label conventions).
- The structural protocol below — what those API calls accomplish — is the same for every backend.

### 6. Bidirectional traceability (after task capture completes)

For each phase that had tasks captured:

1. **Update `phases/phase-N.md` in `<plan-dir>`** with a `## Captured tasks` section:
   ```markdown
   ## Captured tasks
   - #101 — Add password complexity validator
   - #102 — Wire password validator into signup adapter
   - #103 — Update CLI auth flow
   ```
2. **Copy the updated file to `docs/roadmap/<slug>/phases/phase-N.md`** and re-stage.
3. **Verify each captured task issue body cites the phase**: `Roadmap: docs/roadmap/<slug>/phases/phase-N.md`. This is the cartridge's job — confirm it's present, fix if missing.

For single-slice plans (no roadmap), back-link points at `<plan-dir>/plan.md` instead, but since `<plan-dir>` is transient, single-slice plans don't get repo-side back-links. This is the right asymmetry: the rationale isn't durable for one-off slices anyway.

### 7. Record + report

Write `<plan-dir>/captured.json`:
```json
{
  "backend": "github-issues",
  "roadmap": "docs/roadmap/<slug>/",
  "phases": {
    "phase-1": { "tasks": { "task-1": "https://github.com/org/repo/issues/101" } },
    "phase-2": { "tasks": { "task-1": "https://github.com/org/repo/issues/102" } }
  },
  "captured_at": "2026-05-23T00:00:00Z"
}
```

(For single-slice plans, no `roadmap` key; `phases` collapses to a single implicit phase.)

Update `metadata.json` `phase: captured`.

Print:
```
✓ Captured 8 tasks across 4 phases → github-issues

Roadmap layer (staged in repo, not yet committed):
  + docs/roadmap/mvp/roadmap.md
  + docs/roadmap/mvp/decisions.md
  + docs/roadmap/mvp/phases/phase-1.md  (+ Captured tasks section)
  + docs/roadmap/mvp/phases/phase-2.md  (+ Captured tasks section)
  ...

Task layer (created in tracker):
  Phase 1: #101 #102
  Phase 2: #103 #104 #105
  ...

Next:
  git commit docs/roadmap/   # land the durable roadmap record
  /work-issue 101            # start phase 1's first chess move
```

### 8. Cleanup (optional)

By default, **keep** the plan directory in `/tmp/`. Users sometimes refer back during the same session. The durable record is in the repo regardless.

- `--cleanup` deletes `<plan-dir>` after writing `captured.json`. Safe because everything important is now in the repo.

## Backend protocol (task layer)

Every cartridge implements the same contract. The protocol is defined here; each cartridge is just "the protocol, applied to its target system."

### Inputs (passed from plan-capture's flow)

- Path to `<plan-dir>`.
- Ordered list of task file paths (per-phase for roadmap plans).
- Phase context (for roadmap plans): the phase's title, scope, success criteria.
- Epic-level context from `plan.md` or the relevant phase placeholder.
- `captured.json` if it exists (for resume/update).
- The committed roadmap path (`docs/roadmap/<slug>/phases/phase-N.md`) for back-link inclusion.

### Required steps

1. **Idempotency check.** Read `captured.json`. For each task:
   - Already captured + body unchanged → skip.
   - Already captured + body changed → update existing work item.
   - Not yet captured → create.

2. **Create or update the epic-equivalent.** For roadmap plans, this is **per-phase** — each phase gets an epic representing it, holding its tasks. For single-slice plans, one epic for the whole plan. Body shape:
   - Phase title (or plan title).
   - Phase scope / success criteria (or plan problem statement).
   - **Roadmap back-link**: `Roadmap: docs/roadmap/<slug>/phases/phase-N.md` (for roadmap plans only; omit for single-slice).
   - Task list with placeholders (filled in step 5).

3. **Create or update each task work item.** Body = the task file's contents verbatim, plus a `## Working notes` section with:
   - Branch name (`task/<plan-slug>/task-N-<short-title>`).
   - Epic/phase link.
   - Spec back-link.
   - **Roadmap back-link** (for roadmap plans): `Roadmap: docs/roadmap/<slug>/phases/phase-N.md`.
   - Dependency references.
   - `/work-issue` invocation hint.

4. **Set dependencies.** For each task with `depends_on: [task-X]`, create the appropriate link in the backend's native dependency mechanism.

5. **Patch the epic body** with real work-item identifiers (replacing the placeholders from step 2).

6. **Return the map** of `phase → task-id → issue-id` to `plan-capture`.

### Hard rules

- **Spec back-link is required.** If any task file lacks a spec back-link, refuse to capture and tell `plan-capture` which task is broken. The breakdown didn't slice cleanly.
- **Roadmap back-link is required when a roadmap exists.** Same shape: refuse if missing.
- **No status transitions.** Backends don't move work items through workflow states. That's `/work-issue`-time or manual.
- **No auto-assign.** Users assign at `/work-issue` time.
- **Partial failure leaves recoverable state.** If 2 of 5 task creations failed, `captured.json` reflects the 3 that succeeded; resume picks up from there.

Each cartridge describes only what's specific to its target: the API calls, the customfield handling, the label convention. The structural protocol is here.

## Friction addressed

- Sealed roadmaps stranded in `/tmp/`, evaporating when the container clears.
- Rationale ("why this order, what alternatives did we reject") buried in chat history with no repo record.
- Task issues with no link back to the phase that produced them, leaving PR reviewers with no context.
- Translating planning prose into well-structured issues by hand.
- Re-running captures that duplicate work items.

## Anti-patterns

- Don't auto-commit. Stage; let the user commit.
- Don't compose issue bodies in this skill. Cartridges own the wire format.
- Don't auto-delete plan dirs on first run.
- Don't fall back silently to a different backend.
- Don't claim partial success on errors — if some issues failed, report which and leave the plan in capturable state for resume.
- Don't treat `phases/phase-N.md` as freely-editable. Two writes total: roadmap-seal and post-capture. Surprising mid-file edits break the artifact contract.
