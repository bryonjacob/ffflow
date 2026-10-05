# Capture cartridge: GitHub Issues

## Purpose

GitHub backend for the capture protocol. Implements the protocol defined in `plan-capture` — creates/updates one epic issue + N task issues via `gh`.

## When to invoke

Called by `plan-capture` when `.ffflow/config.yaml` has `capture: github-issues` (the default). Not normally invoked directly.

## Prerequisites

- `gh auth status` reports OK.
- Repository has a remote on GitHub.
- Plan directory in `breakdown-complete` state.

## Concept mapping

| Protocol | GitHub |
|---|---|
| Epic | Issue with label `epic` + `ffflow-epic` |
| Task | Issue with labels `ffflow-task` + `epic-<epic-id>` |
| Dependency | Comment on the depending issue (GH has no first-class dep field) |
| Spec back-link | Inline in issue body, "Spec back-link" line in Working notes |
| RID range (L3) | Label `rid-AUTH-001..003` (dashes; no slashes — GH label limitation) |

## API specifics

### Create epic

```bash
gh issue create \
  --title "Epic: <plan title from plan.md>" \
  --label "epic,ffflow-epic" \
  --body "<epic body per protocol>"
```

### Create each task

```bash
gh issue create \
  --title "<ordinal-prefix><task title>" \
  --label "ffflow-task,epic-<epic-id>" \
  --body "<task body per protocol>"
```

**Title ordinal prefix (required).** The execution order is burned into the title so `work-epic` sorts on it (its "Issue ordering" invariant) rather than on unreliable issue numbers. `<N>` is the task's 1-based position in the phase's dependency-ordered task list (`task-1` → `T1`):

- **Roadmap plans** (one epic per phase): `E<phase-number> T<N> — `, e.g. `E3 T1 — Repository placement and synchronization`. The `E<phase-number>` matches the epic's own short code.
- **Single-slice plans** (one epic, no phase): `T<N> — `, e.g. `T1 — Add password validator`.

Use a plain ` — ` (space–em-dash–space) between the ordinal and the task title. Never create a task issue without the prefix.

Task body ends with the standard `## Working notes` block from the protocol:
```markdown
- Branch: `task/<plan-slug>/task-N-<short-title>`
- Epic: #<epic-id>
- Spec back-link: <spec section this advances>
- Roadmap: docs/roadmap/<slug>/phases/phase-N.md   (for roadmap plans only)
- Depends on: #<other-issue-id> (or "None")

To start work: `/work-issue <this-issue-id>`
```

The roadmap back-link is mandatory when the plan came from `plan-roadmap` (i.e., when `captured.json` will have a `roadmap` key). Single-slice plans omit it.

Per phase, the cartridge creates a phase-epic issue holding the phase's tasks. Phase-epic body includes:
- Phase title, scope, success criteria (from `phases/phase-N.md`).
- `Roadmap: docs/roadmap/<slug>/phases/phase-N.md` as the first line of the body.
- Task list with placeholders, filled in after task creation.

### Update epic with real issue numbers

After all task issues exist, patch the epic body's checklist with real issue numbers, **in ordinal order** — the title already carries the ordinal, so the line reads `- [ ] #<n> <full task title>`:

```markdown
## Tasks
- [ ] #103 E3 T1 — Repository placement and synchronization
- [ ] #104 E3 T2 — Paseo installation and change classification
```

```bash
gh issue edit <epic-id> --body "<patched body with real #s>"
```

### Verify the ordinal prefix (guardrail)

Before returning the map to `plan-capture`, re-read the titles of the issues just created/patched and confirm every task title matches `^(E\d+ )?T\d+ — `:

```bash
gh issue list --label "epic-<epic-id>" --state all --json number,title \
  --jq '.[] | select(.title | test("^(E[0-9]+ )?T[0-9]+ — ") | not) | "MISSING ORDINAL: #\(.number) \(.title)"'
```

Any output means generation regressed — report the offending issues to `plan-capture` and stop; do not leave an epic with unordered titles.

### Set dependencies

GitHub has no first-class dependency field. Use a comment:
```bash
gh issue comment <this-task-issue> --body "Depends on #<other> — block until that ships."
```

### Write captured.json

```json
{
  "backend": "github-issues",
  "epic": "https://github.com/<org>/<repo>/issues/100",
  "tasks": {
    "task-1": "https://github.com/<org>/<repo>/issues/101"
  },
  "captured_at": "<UTC ISO>"
}
```

## Error handling

- `gh` not authenticated → return error to `plan-capture` so it can stop cleanly.
- API rate limit → back off and retry once; otherwise report and leave state in `captured.json` for resume.
- Partial failure (some succeeded) → `captured.json` records what succeeded; resume continues from there.

## Anti-patterns

- Don't auto-close anything. Capture is one-way.
- Don't `gh issue close` the epic when all tasks close — let the user do that.
- Don't restate the protocol — it lives in `plan-capture`. Refer to it.
