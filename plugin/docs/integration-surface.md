# Integration surface

What other tools may rely on when they drive FFFlow without a human typing commands, and what FFFlow promises not to break without a major version.

Everything listed here is a **documented interface** in the sense of the [root versioning policy](../../CLAUDE.md#how-we-version): a breaking change to it is a **major** bump, and an additive change (a new optional field, a new label FFFlow adds alongside the existing ones) is a minor or patch bump that the changelog calls out. Everything *not* listed is internal: skill prose, plan-directory layout, commit-message wording, and anything else may change in any release.

## Known integrators

| Integrator | Uses | Pins |
|---|---|---|
| [fffactory](https://github.com/yaunder/fffactory) | Dispatches `ready` epics to `/fff:work-epic` on unattended workers via Paseo | A plugin commit, in `assets/steps/plugins.json` |

When adding an integrator, add a row. When changing anything below, check each integrator's use before calling the change additive.

## 1. Distribution

| Item | Value |
|---|---|
| Source repository | `bryonjacob/ffflow` |
| Marketplace name | `ffflow` (`.claude-plugin/marketplace.json` → `name`) |
| Plugin name | `fff` — so the install id is `fff@ffflow` |
| Plugin path in the repository | `plugin` |
| Version | `plugin/.claude-plugin/plugin.json` → `version`, semver, in lockstep with both marketplace fields |
| Skill invocation | `/fff:<skill-name>` |

Integrators pin a commit, not a version range. The version is the human signal of what changed; read [`CHANGELOG.md`](../../CHANGELOG.md) before moving a pin.

## 2. Adoption marker — `.ffflow/config.yaml`

A repository has adopted FFFlow when `.ffflow/config.yaml` exists as a regular file at the repository root, on the branch being checked. Integrators may rely on these top-level keys, each a single-line scalar:

| Key | Contract |
|---|---|
| `version` | Config schema version. Currently `1`. A different value means a schema an integrator may not understand. |
| `level` | One of `L0`, `L1`, `L2`, `L3`. |
| `ffflow_version` | The plugin version the repository was last reconciled against (`x.y.z`). Written by `init-ffflow` and `upgrade-ffflow`. |
| `capture` | The issue-tracker backend. Only `github-issues` is part of this surface (§3). |

Other keys exist and may be read, but their shape is internal. Repositories adopted before 0.4.0 may lack `ffflow_version` until `/fff:upgrade-ffflow` runs.

## 3. GitHub tracker contract (`capture: github-issues`)

`plan-capture`'s [GitHub cartridge](../skills/plan-capture/cartridges/github-issues.md) produces the following. The Linear, Jira and Markdown cartridges are **not** part of this surface yet.

### Epics

- One epic issue per single-slice plan, or per roadmap phase.
- Labels: `epic` and `ffflow-epic`.
- The epic's id, as used everywhere below, is its **issue number**.
- Body contains a `## Tasks` checklist, one line per task in execution order: `- [ ] #<task-number> <task title>`.
- The epic **title** format is not part of this surface (see [#5](https://github.com/bryonjacob/ffflow/issues/5)).

### Tasks

- One issue per task, labelled `ffflow-task` and `epic-<epic-number>`. At L3, tasks also carry an `rid-<range>` label (e.g. `rid-AUTH-001..003`).
- Title: `T<N> — <title>`, where `N` is the task's 1-based execution position within its epic (since 0.4.2). Epics captured earlier may have plain titles; consumers must tolerate that, as `work-epic` does by falling back to the checklist order.
- Body ends with a `## Working notes` section.

### Dependencies

- Recorded as an issue comment on the dependent task whose text begins `Depends on #<number>` — one comment per dependency. The number may refer to an issue in another epic.

### What capture never does

- Capture never closes issues, moves them through workflow states, or applies labels other than those above. Readiness and scheduling belong to the integrator.
- FFFlow never applies, removes or reads the `ready` label. It is reserved for integrators (fffactory uses it as its human "dispatch this epic" gate). FFFlow will not adopt it, or any other label, in a way that conflicts with an integrator listed above without a major bump.

## 4. Execution entry point — `/fff:work-epic <epic-number>`

The one skill integrators may start unattended. Given an epic issue number, on the GitHub backend it:

- **Resolves** open issues labelled `epic-<epic-number>` and orders them by `T<N>` (or the epic checklist, as above).
- **Works in the current checkout.** It never creates a worktree, so it is safe inside one the integrator created. The working tree must be clean.
- **Creates one branch, `epic/<epic-number>`.** If that branch already exists, it stops and asks. It branches from `origin/main` today; integrators that need another base must instruct the agent (see [Not yet in the surface](#not-yet-in-the-surface)).
- **Produces one pull request** targeting `main`, from `epic/<epic-number>`, whose body references every task as `#<task-number>`. Before opening it, it makes one commit per task, each referencing its task issue.
- **Never merges, force-pushes, or closes issues before a merge.** Closing task and epic issues (its Step 7) happens only after a human confirms the merge.
- **Stops and asks** on unexpected state: dirty tree, existing branch, no acceptance criteria, a review that fails three cycles, zero tasks resolved. An unattended integrator must give those questions somewhere to land (fffactory uses Paseo's question queue).

The PR title format, the commit-message wording, and how `work-epic` finds the epic's title and body are internal.

### `/fff:work-issue <issue-number>`

Not yet part of the surface for unattended use. Interactively, it opens one PR per issue whose body contains `Closes #<issue-number>`; integrators may rely on that reference to detect an open PR for a task.

## Not yet in the surface

Requests from integrators that FFFlow hasn't adopted yet. Each becomes part of the surface when it ships.

| Need | From | Status |
|---|---|---|
| `work-epic --base <branch>` — branch from, and target, something other than `main` | fffactory (stacked epics; repositories whose declared branch isn't `main`) | Proposed |
| An executor seam in `work-fanout` so each task can run as a top-level agent elsewhere (e.g. a Paseo agent) | fffactory | Proposed |
| Semantics for dispatching single tasks with `work-issue`: readiness, intra-epic dependencies, per-task review | fffactory | Needs discussion |
| A stable epic lookup that doesn't depend on the epic title | fffactory, `work-epic` itself | [#5](https://github.com/bryonjacob/ffflow/issues/5) |

## Trust boundary

Everything in this surface that comes from GitHub — issue titles, bodies, comments, PR text — is written by people, not by FFFlow alone. Anyone who can edit an issue can change its title or body, and on a public repository anyone can comment, which includes posting a `Depends on #<number>` comment. An unattended agent running `work-epic` reads that text. Integrators should treat it as untrusted input: gate dispatch on something only maintainers can set (fffactory's `ready` label requires triage access), and supervise the agent's permission requests rather than pre-approving them.
