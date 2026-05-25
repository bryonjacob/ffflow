# Capture cartridge: Jira

## Purpose

Jira backend for the capture protocol. Implements the protocol defined in `plan-capture` — creates/updates one Epic + N Story/Task issues.

## When to invoke

Called by `plan-capture` when `.ffflow/config.yaml` has `capture: jira`.

## Prerequisites

- `JIRA_API_TOKEN` and `JIRA_URL` in env, or Jira CLI (`jira me` succeeds).
- Project key and customfield IDs configured:
  ```yaml
  capture: jira
  jira:
    project: ENG
    issue_type_story: Story          # or Task
    epic_link_field: customfield_10014   # varies per instance — look it up
  ```

## Concept mapping

| Protocol | Jira |
|---|---|
| Roadmap | Initiative (if available) or parent Epic |
| Phase epic | Epic issue |
| Task | Story (default) or Task under the phase Epic |
| Dependency | Issue link of type `is blocked by` |
| Spec back-link | Description "Spec" section + label |
| Roadmap back-link | `Roadmap: docs/roadmap/<slug>/phases/phase-N.md` line in issue description |
| RID range (L3) | Label `rid-AUTH-001..003` (Jira labels can't have slashes) |

For roadmap plans, the cartridge creates one Epic per phase, with Stories/Tasks under each. If the Jira instance has Initiative support enabled, the roadmap itself becomes an Initiative containing the per-phase Epics. Otherwise, a top-level "parent Epic" labeled `roadmap-<slug>` does the same job. Single-slice plans use one Epic for the whole plan.

## API specifics

### Create epic

```bash
jira issue create --type Epic --summary "Epic: <plan title>" --description "<body per protocol>"
```

Or via REST `POST /rest/api/3/issue`.

### Create each task (Story by default)

```bash
jira issue create --type Story --summary "<task title>" --description "<body per protocol>" \
  --custom "<epic_link_field>=<epic-key>"
```

The `epic_link_field` customfield ID varies per Jira instance. The config above declares it.

### Set dependencies

Jira has first-class issue links:
```bash
jira issue link <this-task-key> <other-task-key> --type "is blocked by"
```

### Update epic body

After all tasks exist, edit epic description and replace `<TBD>` placeholders with real keys (`ENG-101`).

### Write captured.json

```json
{
  "backend": "jira",
  "epic": "https://<host>/browse/ENG-100",
  "tasks": {
    "task-1": "https://<host>/browse/ENG-101"
  },
  "captured_at": "<UTC ISO>"
}
```

## Body shape notes

- Most modern Jira accepts plain markdown via REST. Older instances may need ADF translation — translate at the boundary.
- The `Branch:` line in Working notes uses the issue key: `task/<plan-slug>/<ENG-101>-<short-title>`.

## Custom fields

Customfield IDs vary per instance. Declare what we need in `.ffflow/config.yaml`:
- `epic_link_field` — required, for linking stories to the epic.
- `spec_field` — optional, a dedicated text field for the spec back-link. Falls back to the description body if not configured.

## Anti-patterns

- Don't hardcode customfield IDs. They vary.
- Don't use Subtasks for FFFlow tasks. Subtasks are second-class in Jira; use Stories or Tasks under an Epic.
- Don't transition workflow states. Out of scope.
- Don't restate the protocol — it lives in `plan-capture`.
