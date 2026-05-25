---
name: work-epic
description: Sequential execution of every open issue under an epic onto one feature branch — one squashed commit per task, one PR per epic. Implement and review subagents kept independent; user approves the merge.
---

# work-epic

## Plan Mode

This skill does NOT invoke Plan Mode. It runs a sequence of implement/review subagents on one feature branch.

## Purpose

Drive an entire epic from open issues to a reviewed PR off `main`. One feature branch, one clean commit per task, one PR per epic. Stops before merging — the user approves merges.

Use this when:
- You have several issues under one epic that should ship as a single PR (logically inseparable, or small enough that splitting hurts review).
- You want sequential execution with per-task review, not parallel fanout.

For one PR per issue: `/work-issue`. For multiple parallel PRs: `/work-fanout`.

## Inputs

- An epic identifier (`/work-epic E0.1` or `/work-epic 100` for a GitHub umbrella issue number).
- `.ffflow/config.yaml` — read for level, stack, capture backend.

## Outputs

- One feature branch `epic/<epic-id>` off `origin/main`.
- One squashed commit per task.
- One PR per epic, off `main`.
- Per-task issues closed and umbrella issue closed (Step 7) after the user merges.

## Dependencies

- `work-issue` discipline applies inside each implement subagent (TDD loop, spec update, level-appropriate gates).
- `self-review` discipline applies inside each review subagent.
- Cartridge from `plan-capture` to resolve epic→issues (the active capture backend's "list child issues" semantics).

## Cross-cutting invariants

These are non-negotiable.

### Issue ordering

GitHub issue numbers are out of order (parallel agents created them). The **titles** are ground truth — they encode `<epic> T<N>` (e.g. `E0.1 T1`, `E0.1 T2`). Always sort by title, never by issue number. Use a natural sort on the `T<N>` prefix so `T10` comes after `T2`.

### Implement and review never share a subagent

Each task uses a fresh implement subagent and a fresh review subagent. Reviews must be independent of the implementation that produced them.

### No merge

This skill never merges. Even green PRs sit until the user approves. Step 7 (post-merge cleanup) runs only after the user confirms the merge happened.

## Flow

### Step 1 — Resolve tasks

For GitHub backend:
```bash
gh issue list --label "epic:<epic-id>" --state open --limit 100 --json number,title,labels
```

For other backends, equivalent query via the active capture cartridge.

Parse, extract the `T<N>` from each title, sort numerically. **Print the resolved task list** (issue # + title in execution order) to the user before doing anything destructive. If zero issues found, stop and ask.

### Step 2 — Branch

- Verify working tree is clean. If not, stop and ask.
- `git fetch origin main`
- `git checkout -b epic/<epic-id> origin/main`

If the branch already exists, stop and ask whether to resume on it or recreate.

### Step 3 — Per-task loop (sequential, in title order)

For each task `T<N>` (issue `#NN`):

#### 3a. Capture starting SHA

`git rev-parse HEAD` → remember as `START_SHA` for this task.

#### 3b. Implement (fresh subagent)

Spawn a subagent via the Agent tool. Briefing:

- Issue number and full title.
- "You are implementing on the **current branch `epic/<epic-id>`** and **must not** create a new branch, push, or open a PR."
- "Follow the `work-issue` discipline (TDD loop, spec update in-tree, level-appropriate gates) but skip the PR-creation phase — your output is local commits."
- "Commit locally as you go (intermediate commits are fine; they will be squashed)."
- "Run `just check-all` green before reporting success."
- "Return a short summary of what changed."

#### 3c. Review (fresh subagent — not the implementer)

Spawn a fresh subagent. Do not reuse the implementer:

- Review the diff `git diff $START_SHA..HEAD` against the issue's acceptance criteria.
- Pull AC with the capture backend's `view-issue` equivalent.
- Run `just check-all`.
- Apply the `self-review` checklist appropriate for the project's level.
- Return either `PASS` or a concrete list of issues to fix. Be specific — `file:line` where possible.

#### 3d. Cycle on feedback

If review returns issues, spawn a **new** implement subagent with the issue list, then re-review. Cap at 3 cycles. If still failing, stop and report to the user — don't push through.

#### 3e. Squash to one commit

Once review passes:

```bash
git reset --soft $START_SHA
git commit -m "<message>"
```

Match the project's commit style (run `git log --oneline -10` first to see the convention). Reference the issue (`#NN`).

### Step 4 — Open the PR

Push and open the PR:

```bash
git push -u origin epic/<epic-id>
gh pr create --base main --title "Epic <epic-id> — <epic title>" --body "$(cat <<'EOF'
## Summary
<one-paragraph epic summary>

## Tasks
- T1 — <title> (#NN)
- T2 — <title> (#NN)

## Test plan
- [ ] <item>
EOF
)"
```

Pull the epic's title and description from the umbrella issue. For GitHub:
```bash
gh issue list --search "Epic <epic-id>" --state all --json number,title,body --limit 5
```
Pick the one whose title starts with `Epic <epic-id> — …`. Use its title for the PR title and its body as the basis for the PR Summary.

### Step 5 — Holistic epic review (subagent)

Spawn one more fresh subagent:

- Review PR #<num> against the acceptance criteria for the epic **as a whole**.
- Pull the epic AC from the umbrella issue resolved in Step 4.
- Verify each task's AC is met **and** the tasks integrate cleanly.
- Return `PASS` or specific fixes.

If fixes needed, loop back to Step 3 for the affected task(s) — add follow-up commits, re-squash if needed, push.

### Step 6 — Hand off to user

Print the PR URL. Explicitly ask the user to approve the merge.

**Do not merge.** The user merges.

### Step 7 — Post-merge cleanup

Once the PR has merged (the user either merged themselves or asked you to merge after approving), do this cleanup pass:

1. Close each per-task issue with a back-link to the PR. `gh issue close` only takes one issue per invocation:
   ```bash
   gh issue close <NN> -c "Landed in PR #<PR> (epic <epic-id>)."
   ```

2. Close the umbrella issue:
   ```bash
   gh issue close <umbrella-num> -c "Epic <epic-id> landed in PR #<PR>."
   ```

3. Sync local `main` and delete the local epic branch if it still exists. (`gh pr merge --delete-branch` may have removed it already; tolerate that.)
   ```bash
   git checkout main && git pull origin main
   git branch -d epic/<epic-id> 2>/dev/null || true
   ```

## Guardrails

- **Never reuse a subagent across implement/review boundaries.** Reviews must be independent.
- **Any unexpected state** (dirty tree, branch exists, missing label, no AC on issue) → stop and ask; don't auto-recover destructively.
- **Never `--force` push or `reset --hard` to a SHA you don't fully control.**
- **Don't merge.** The user's role. Post-merge cleanup in Step 7 happens *after* the merge is confirmed.
- **Don't fan out within an epic.** This skill is sequential by design. Use `/work-fanout` if you want parallelism (different shape — one PR per issue, not one PR per epic).

## Idempotency / resume

- Re-running on an existing `epic/<epic-id>` branch with an open PR: resume by computing which tasks are already squash-committed (parse commit messages for issue refs), skip those, continue from the next.
- Mid-loop crash: the previous squashed commits stay; only the in-flight task needs to restart at Step 3a.

## Friction addressed

- Hand-typed "have an agent team work on these four under epic X, sequentially, one squashed commit each" prompts.
- Review accidentally being done by the same agent that wrote the code.
- Cleanup forgotten after merge (issues left open).
- Epic-level integration regressions that per-task review misses.

## Anti-patterns

- Sorting by issue number instead of title. Title order is ground truth.
- Skipping the holistic Step 5 review. Per-task reviews miss integration issues.
- Squashing before review passes. Lose the intermediate commits before they've been judged.
- Merging without user approval. Even if PR is green.
- Cleanup before merge. Issues stay open until the PR is actually in `main`.
