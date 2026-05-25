---
name: work-issue
description: Execute one captured issue from cold-start to merged PR. Spec updates ship in the same PR. Level-aware: lint+test gates at L0, full quality gates at L3. For parallel multi-issue runs use work-fanout; for one PR per epic use work-epic.
---

# work-issue

## Plan Mode

This skill does NOT invoke Plan Mode. It executes a single chess move; planning is already done.

## Purpose

Take one captured issue (or task file) from cold-start to a PR. The spec change ships in the same PR as the implementation. At every level, the discipline is the same — only the artifacts scale.

## Inputs

- An issue ID (`/work 42`) or path to a task file (markdown backend).
- `.ffflow/config.yaml` — read for level, stack, capture backend.

## Outputs

- A branch named per the task's `Branch:` field (typically `task/<plan-slug>/task-N-<short-title>`).
- A PR (draft or ready, depending on local-validation results).
- Spec updates committed in the same PR.
- Updated `.ffflow/audit.yaml` if any audited file is touched.

## Dependencies

- `tdd-loop` — the red/green/refactor discipline.
- `self-review` — pre-PR checklist.
- Level-appropriate stack and methodology skills.

## Cross-cutting invariants

These are non-negotiable.

### PR-checkpoint protocol

When ≥ 2 PRs have been created in the current session, pause with a summary:

```
PRs created this session:
  #101 — task-1: ...  (status: open, draft=false, checks=pending)
  #102 — task-2: ...  (status: open, draft=false, checks=pending)

continue? (y/n/disable)
```

- `y` continues; counter resets.
- `n` stops the session.
- `disable` turns off PR-checkpointing for the rest of the session. One decision; no further nags.

The default is the every-2-PRs cadence. `disable` is for users who want to let a long fanout run uninterrupted after they've confirmed it's healthy. Counter and disable-state are session-local — they reset on next invocation.

### Local-validation gate

Before pushing a PR that contains anything other than spec-only changes:

- Either run the project's local repro/smoke (`just test`, `pytest`, `npm test`, level-appropriate) and confirm green, **or**
- State explicitly in the PR body why local validation wasn't possible (e.g., "requires external API access").

A non-spec-only PR with neither is a protocol violation.

## Flow

### Phase 0 — Load and detect state

1. Read `.ffflow/config.yaml` for level/stack.
2. Load the task:
   - Issue ID → `gh issue view <id>` for body and metadata.
   - Task file → read directly.
3. Detect resume state by branch + PR:
   - **Branch exists, PR merged** → done. Exit.
   - **Branch exists, PR open** → resume at Phase 5.
   - **Branch exists, no PR** → resume from where commits left off.
   - **No branch** → create from main: `git checkout -b <branch>`.
4. Verify dependencies are complete (closed PRs / merged branches). If a dep is open, ask the user how to proceed.

### Phase 1 — Read the spec

The task body cites a spec back-link. Open it:

- **L0/L1**: prose spec section. Read the surrounding context.
- **L2**: `.feature` Rule. Read the scenarios in scope.
- **L3**: RID list. Read those scenarios and their bound step definitions.

Re-read the task body once more after reading the spec. Confirm the chess move is still well-defined; if you have new questions, stop and ask the user.

### Phase 2 — TDD loop (delegated to `tdd-loop`)

Load `tdd-loop` as reference context. Walk the loop:

1. Write the test(s) that pin the new behavior. At L2+, this includes any new `.feature` content or scenarios.
2. Run them. They must fail (red). If they pass, the test is wrong or the behavior already exists.
3. Write the minimum code to make them pass.
4. Refactor under green.
5. Repeat per chunk.

Stack-specific commands come from the `stack` skill's cartridge matching `.ffflow/config.yaml stack:`.

### Phase 3 — Spec update

Update the evergreen spec to reflect the new behavior. This commit goes in the same PR as the implementation.

- L0/L1: edit prose. Cross-reference the task issue in the spec section's footer.
- L2: update or add Rule / Scenarios in the `.feature` file.
- L3: write RID-tagged scenarios; ensure RID uniqueness via `/audit --type rid` (deferred until Phase 4).

### Phase 4 — Gates

Run level-appropriate gates:

- **L0**: lint, format, tests.
- **L1**: above + `/audit --type claude-md` (if any docs changed).
- **L2**: above + `/audit --type spec` for files in scope + `/audit --type char-tests` if any characterization tests are pinned to this spec.
- **L3**: full quality gates per `quality-gates`: structure / correctness / coverage / maintainability, including mutation testing for the touched scope.

If any gate fails after honest attempts, mark the PR as draft and surface the failures in the PR body.

### Phase 5 — Self-review

Invoke `self-review` skill. Walk its checklist against this PR's diff. In particular: every minor issue you noticed during implementation should be either **fixed in this PR** (`zero-tech-debt`'s 15-minute rule) or **deferred with a concrete TODO-with-trigger** (`yagni`). No bare TODOs, no vague triggers, no "future work" sections in the PR body.

### Phase 6 — PR

Honor the local-validation gate (above). Then:

```bash
gh pr create \
  --title "<short title>" \
  --body "<body>"
```

PR body shape:

```markdown
Closes #<issue-id>

## Spec changes
- <file>: <one-line description>

## Implementation
- <file>: <one-line description>

## Tests
- <file>: <added / modified>
- Local result: <pass | fail | not-run + reason>

## Audit
- <auditor>: <pass | fail | n/a>
```

If draft (gates failing): prefix title with `[WIP]` and add `## Outstanding` section listing the open work.

After creating the PR, **post a one-line summary in the session** per the PR-checkpoint protocol:

```
created PR #<n> — task-<id>: <title> (draft=<bool>)
```

## Idempotency

- Re-running on a branch with an open PR resumes at the PR step — checks state, refreshes body if spec/test summary changed, no-ops if already current.
- Commits are atomic per chunk. Mid-loop interruptions resume cleanly because the previous chunk is already on the branch.

## Friction addressed

- PR-author archaeology after long autonomous runs (PR body cites issue, spec, tests).
- Specs falling behind code (single-PR spec+code).
- PRs shipped without local repro (local-validation gate).
- Plan Mode misfires inside execution flows.
- Runaway autonomous loops (PR-checkpoint protocol).

## Anti-patterns

- Don't push a PR without spec changes if the task said the spec should change.
- Don't move past Phase 2 if tests aren't actually red first — that means the test is wrong.
- Don't merge yourself. The human merges (or `autopilot` does, with explicit authorization).
- Don't refactor outside the scope of the task. Refactor opportunities → file a `refactor`-driven plan, not in this PR.
- Don't change spec sections outside the task's scope. If you notice drift, file an audit finding.

## Edge cases

- **Spec back-link missing from task body**: capture wasn't clean. Stop and ask the user — fix the issue, don't proceed.
- **Tests already pass at Phase 2 red step**: behavior already exists somewhere. Investigate. Either the task is a no-op (delete the issue), or there's a duplication problem.
- **Gates fail repeatedly with the same error**: stop, surface to user. Do not self-loop indefinitely.

## Quality checks before PR

- [ ] Task issue read; spec back-link followed.
- [ ] Tests written, ran red, then green.
- [ ] Spec updated in the same branch.
- [ ] Local-validation gate honored (either passed or explained).
- [ ] Level-appropriate audits ran.
- [ ] `self-review` clean.
- [ ] PR body cites issue, spec changes, tests.
