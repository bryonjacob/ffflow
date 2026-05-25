# Capture cartridge: Linear

## Purpose

Linear backend for the capture protocol. Implements the protocol defined in `plan-capture` — creates/updates one Project + N Issues.

## When to invoke

Called by `plan-capture` when `.ffflow/config.yaml` has `capture: linear`.

## Prerequisites

- `LINEAR_API_KEY` in env, or Linear CLI auth (`linear auth status`).
- Team identifier configured:
  ```yaml
  capture: linear
  linear:
    team_id: ENG
    project_template: ffflow-epic        # optional
  ```

## Concept mapping

| Protocol | Linear |
|---|---|
| Roadmap | Project (top-level) |
| Phase epic | Sub-project (or labeled group within the project) |
| Task | Issue |
| Dependency | Issue relation (`relation:blocks`) — first-class in Linear |
| Spec back-link | "Spec" section in issue description + label |
| Roadmap back-link | `Roadmap: docs/roadmap/<slug>/phases/phase-N.md` line in issue description |
| RID range (L3) | Label `rid/AUTH-001..003` (slashes OK in Linear labels) |

Linear's hierarchy (Project → sub-project → Issue) maps naturally to (Roadmap → Phase → Task). For single-slice plans (no roadmap), use a single Project for the plan with Issues directly under it.

## API specifics

### Create project (epic)

```bash
linear project create \
  --team <team-id> \
  --name "Epic: <plan title>" \
  --description "<epic body per protocol>"
```

Or via GraphQL `projectCreate`.

### Create each task issue

```bash
linear issue create \
  --team <team-id> \
  --project <project-id> \
  --title "<task title>" \
  --description "<task body per protocol>" \
  --label ffflow-task
```

### Update project body with real Linear IDs

After all issues exist, edit project description and replace task placeholders with real Linear IDs (`ENG-101`, etc.).

### Set dependencies

Linear has first-class dependency relations:
```bash
linear issue relation --type blocks --from <this-issue> --to <other-issue>
```

### Write captured.json

```json
{
  "backend": "linear",
  "epic": "https://linear.app/<workspace>/project/<slug>-<short-id>",
  "tasks": {
    "task-1": "https://linear.app/<workspace>/issue/ENG-101"
  },
  "captured_at": "<UTC ISO>"
}
```

## Anti-patterns

- Don't map FFFlow's spec back-link to Linear's `parent` field. Use the description — `parent` is for organizational hierarchy.
- Don't touch cycles or milestones. Out of scope.
- Don't restate the protocol — it lives in `plan-capture`.
