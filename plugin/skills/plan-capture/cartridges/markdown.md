# Capture cartridge: Markdown (file-based)

## Purpose

Local backend for the capture protocol. No external dependencies — task work items are markdown files in the repo. Good for solo projects, offline work, or repos where GitHub/Linear/Jira isn't appropriate.

Implements the protocol defined in `plan-capture`. The "API" here is filesystem writes.

This cartridge owns the **task layer** only. The **roadmap layer** is plan-capture's own concern and always lands in `docs/roadmap/<slug>/` regardless of cartridge.

## When to invoke

Called by `plan-capture` when `.ffflow/config.yaml` has `capture: markdown`.

## Concept mapping

| Protocol | Markdown |
|---|---|
| Epic-equivalent (per phase, or per plan for single-slice) | `docs/tasks/<slug>/EPIC-<phase>.md` |
| Task | `docs/tasks/<slug>/task-N.md` |
| Dependency | `**Depends on:** task-X` line in the task file |
| Spec back-link | Inline in task body |
| Roadmap back-link | `Roadmap: docs/roadmap/<slug>/phases/phase-N.md` line in working notes |
| Index | `docs/tasks/<slug>/TASKS.md` |

## Output layout

```
docs/
├── roadmap/<slug>/           # roadmap layer — owned by plan-capture, not this cartridge
│   ├── roadmap.md
│   ├── decisions.md
│   └── phases/
│       ├── phase-1.md
│       └── phase-2.md
└── tasks/<slug>/             # task layer — this cartridge writes here
    ├── EPIC-phase-1.md       # one per phase (or one EPIC-<slug>.md for single-slice plans)
    ├── EPIC-phase-2.md
    ├── task-1.md
    ├── task-2.md
    └── TASKS.md              # local index for this slug
```

Two sibling subtrees under `docs/`:
- `docs/roadmap/<slug>/` — rationale, never deleted.
- `docs/tasks/<slug>/` — work items, can be deleted after roadmap completion.

For single-slice plans (no roadmap), the cartridge skips per-phase EPIC files and produces a single `docs/tasks/<slug>/EPIC.md`.

## "API" specifics

### Create epic file (`docs/tasks/<slug>/EPIC-phase-N.md`, or `EPIC.md` for single-slice)

Body per the protocol's epic shape, plus `**Status:** open` at top. For roadmap plans, body includes a `Roadmap: docs/roadmap/<slug>/phases/phase-N.md` line.

### Create each task file (`docs/tasks/<slug>/task-N.md`)

```markdown
# Task <N>: <title>

**Status:** open
**Epic:** [EPIC-phase-N](EPIC-phase-N.md)
**Depends on:** task-X (or "None")

<body of <plan-dir>/tasks/task-N.md verbatim>

---
## Working notes
- Branch: `task/<plan-slug>/task-N-<short-title>`
- Spec back-link: <link>
- Roadmap: docs/roadmap/<slug>/phases/phase-N.md   (for roadmap plans only)

To start work: /work-issue docs/tasks/<slug>/task-N.md
```

### Index file (`docs/tasks/<slug>/TASKS.md`)

```markdown
# Tasks index — <slug>

| ID | Phase | Title | Status | Depends |
|---|---|---|---|---|
| EPIC-phase-1 | 1 | <phase title> | open | — |
| task-1 | 1 | <title> | open | — |
| task-2 | 1 | <title> | open | task-1 |
| EPIC-phase-2 | 2 | <phase title> | open | phase-1 |
| task-3 | 2 | <title> | open | task-2 |
```

For single-slice plans, omit the Phase column.

Re-runs update the table rows but preserve any user-edited Status column.

### Write captured.json (in `<plan-dir>`)

```json
{
  "backend": "markdown",
  "roadmap": "docs/roadmap/<slug>/",
  "phases": {
    "phase-1": {
      "epic": "docs/tasks/<slug>/EPIC-phase-1.md",
      "tasks": { "task-1": "docs/tasks/<slug>/task-1.md" }
    }
  },
  "captured_at": "<UTC ISO>"
}
```

For single-slice plans, no `roadmap` key; `phases` is one implicit phase.

## Status tracking

Markdown is the tracker. Status lives at the top of each task file (`**Status:** open | in-progress | done | blocked`) and is mirrored in the per-slug `TASKS.md`.

`/work-issue` updates the task file's status on entry (`in-progress`) and on PR creation (`done` once merged, after manual confirmation).

## Conventions

- Task files live in `docs/tasks/<slug>/` (sibling to `docs/roadmap/<slug>/`).
- One file per task. No multi-task files.
- Per-slug `TASKS.md` index lives inside the slug dir.
- Markdown links between files use repo-relative paths.
- Stage the writes but don't commit — same rule as plan-capture's roadmap layer. User owns the commit.

## Lifecycle and cleanup

Task files in `docs/tasks/<slug>/` are durable but **not permanent** — when a slug's work is fully shipped, the `docs/tasks/<slug>/` tree can be removed. The rationale lives in `docs/roadmap/<slug>/` and stays.

A reasonable archive pattern: move `docs/tasks/<slug>/` to `docs/tasks/_archive/<slug>/` once done. Don't auto-archive; the user decides.

## Overriding the location

If a project wants task files alongside the roadmap (single durable tree per slug), override via `.ffflow/stack.yaml`:

```yaml
markdown:
  task_layout: colocated   # docs/roadmap/<slug>/tasks/ instead of docs/tasks/<slug>/
```

Default is `siblings` (separate `docs/roadmap/` and `docs/tasks/`). Colocated is a single-tree option.

## Anti-patterns

- Embedding the full plan content in the EPIC file. The roadmap rationale lives in `docs/roadmap/<slug>/`; the EPIC file is a summary.
- Writing tasks to `docs/roadmap/<slug>/` instead of `docs/tasks/<slug>/` without the colocated override. Mixes layers.
- Auto-deleting completed task files. They're cheap and they're archaeology — archive instead.
- Hand-editing status in TASKS.md without updating the task file. They drift.
- Restating the protocol — it lives in `plan-capture`.

## Friction addressed

- Solo / offline projects that want FFFlow's discipline without setting up a tracker.
- Self-hosted repos where GitHub Issues isn't the canonical truth.
- Demo / tutorial projects where issue trackers add friction.
- Sealed roadmaps that need a durable home regardless of which tracker is configured (this cartridge handles the task layer; plan-capture handles the roadmap layer).
