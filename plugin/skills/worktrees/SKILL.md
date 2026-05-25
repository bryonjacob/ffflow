---
name: worktrees
description: Isolated worktree management for parallel work — naming convention, creation, cleanup, troubleshooting.
---

# worktrees

## Purpose

Isolated working directories on separate branches. Used by `work-fanout` to run multiple `work` instances in parallel without conflicts.

This skill is both:
- A reference for the conventions (path layout, naming).
- The mechanics for create/remove/list operations.

## Conventions

### Where worktrees live

By default, all FFFlow worktrees live under `worktrees/` at the project root.

**Why not `/tmp` (like plans and autopilot logs)?** Worktrees can hold uncommitted work. Plans are design docs that get captured into issues; autopilot logs are spot-check material — both can survive `/tmp` cleanup with no real loss. A worktree with mid-flight changes is unrecoverable if `/tmp` clears it. So worktrees stay in the project tree (gitignored), while transient artifacts go to `/tmp`.

This also keeps them out of `.git/` (where they confuse tooling).

```
<project>/
├── .git/
├── src/
├── worktrees/             # all FFFlow worktrees here
│   ├── task-101/
│   ├── task-102/
│   └── task-103/
└── ...
```

Add `worktrees/` to `.gitignore` if it isn't already.

### Branch naming

Branches inside FFFlow worktrees follow:

```
task/<plan-slug>/task-<N>-<short-title>
```

Examples:
- `task/auth-token-refresh/task-1-validator-port`
- `task/password-rules/task-2-signup-integration`

This makes it obvious which plan a branch came from, and `gh pr list --search "head:task/auth-token-refresh"` filters cleanly.

## Operations

### Check whether you're in a worktree

```bash
git rev-parse --git-dir
# .git              → main repo
# ../.git/worktrees/<name>  → worktree
```

Or:

```bash
git worktree list
```

### Create

```bash
git worktree add worktrees/<name> -b <branch-name>
```

Or with an existing branch:

```bash
git worktree add worktrees/<name> <branch-name>
```

### Remove

```bash
git worktree remove worktrees/<name>
```

If a worktree is dirty or has uncommitted changes, `remove` refuses by default. Either commit/stash the work or pass `--force` (only with explicit user authorization).

### List

```bash
git worktree list
```

### Prune stale entries

When a worktree directory has been deleted without `git worktree remove`:

```bash
git worktree prune
```

## Working inside a worktree

Everything works as usual:
- Commit, push, pull.
- Run tests in isolation — they see only your worktree's changes.
- Create PRs.

What's different:
- Separate working directory.
- Changes don't affect parallel worktrees.

## Cleanup discipline

When a task's PR is **merged**:
1. The orchestrator (`work-fanout`) offers to remove the worktree.
2. User confirms; worktree is removed.

When a task is **stalled or failed**:
1. The worktree is retained for inspection.
2. The user decides when to remove.

Don't auto-remove. Lost worktrees with uncommitted changes are unrecoverable.

## Troubleshooting

- **"Branch already checked out"** — switch branch in the other worktree, or remove that worktree, then retry.
- **Changes not showing** — check `pwd` and `git branch`. Worktrees are easy to lose track of.
- **`git worktree remove` fails with "contains modified files"** — review the changes in that worktree. If they should be saved, commit them first. Only use `--force` if you're sure.
- **A worktree directory exists but `git worktree list` doesn't show it** — `git worktree prune`, then recreate.

## Anti-patterns

- Worktrees outside `worktrees/` — breaks orchestrator assumptions.
- Naming worktrees with the date or session ID — they're per-task, not per-session.
- Sharing state between worktrees via symlinks or shared dirs. The whole point is isolation.
- Force-removing without checking for uncommitted changes.
