# Integration surface

What other tools may rely on when they drive FFFlow without a human typing commands, and what FFFlow promises not to break without a major version.

Everything under **The surface** is a **documented interface** in the sense of the [root versioning policy](../../CLAUDE.md#how-we-version): a breaking change to it is a **major** bump of `fff`. Additive changes, such as an extra label on an issue or a new optional config key, are not breaking. Everything else is internal and may change in any release, including the conventions listed under [Internal conventions](#internal-conventions).

The surface is deliberately narrow. It covers what integrators need to find work, start it, and recognize its result, not the formats FFFlow uses to organize that work.

## Known integrators

| Integrator | Uses | Pins |
|---|---|---|
| [fffactory](https://github.com/yaunder/fffactory) | Dispatches `ready` epics to `/fff:work-epic` on hosted workers via Paseo, so a team runs the same FFFlow flow off their laptops | A plugin commit, in `assets/steps/plugins.json` |

When adding an integrator, add a row. When changing anything below, check each integrator's use before calling the change additive.

## The surface

### 1. Distribution

| Item | Value |
|---|---|
| Source repository | `zerotechdebt/ffflow` |
| Marketplace name | `ffflow` (`.claude-plugin/marketplace.json` → `name`) |
| Plugin name | `fff`, so the install id is `fff@ffflow` |
| Plugin path in the repository | `plugin` |
| Version | `plugin/.claude-plugin/plugin.json` → `version`, semver |
| Skill invocation | `/fff:<skill-name>` |

Integrators pin a commit, not a version range. Read [`CHANGELOG.md`](../../CHANGELOG.md) before moving a pin.

### 2. Adoption marker: `.ffflow/config.yaml`

A repository has adopted FFFlow when `.ffflow/config.yaml` exists as a regular file at the repository root, on the branch being checked, with these top-level keys:

| Key | Contract |
|---|---|
| `version` | Config schema version. Currently `1`. A different value means a schema an integrator may not understand. |
| `level` | One of `L0`, `L1`, `L2`, `L3`. |
| `ffflow_version` | The `fff` version the repository was last reconciled against (`x.y.z`). Written by `init-ffflow` and `upgrade-ffflow`. |
| `capture` | The issue-tracker backend. Only `github-issues` is covered by this surface (§3). |

The promise is about keys and values, not YAML spelling. FFFlow's own skills write each as a plain, unquoted `key: value` line, but a hand-edited file may use any valid YAML form; an integrator that parses more narrowly than YAML should say so. Other keys exist and may be read, but their shape is internal. Repositories adopted before 0.4.0 may lack `ffflow_version` until `/fff:upgrade-ffflow` runs.

### 3. Finding work on GitHub (`capture: github-issues`)

What `plan-capture`'s [GitHub cartridge](../skills/plan-capture/cartridges/github-issues.md) guarantees. The Linear, Jira and Markdown cartridges are not covered yet (see [Not yet in the surface](#not-yet-in-the-surface)).

- **Epics** are issues labelled `ffflow-epic`. An epic's id, everywhere below, is its **issue number**.
- **Tasks** are issues labelled `ffflow-task` and `epic-<epic-number>`.
- **Dependencies** are recorded on the dependent task as a comment containing a line that begins `Depends on #<number>`. The number is an issue **in the same repository**, possibly under another epic. Integrators may read such lines from task bodies as well as comments.
- **Captured issues are self-sufficient.** Each task issue carries what `work-epic` needs to execute it, together with the repository checkout. Execution never depends on planning files that live only on the machine that captured them (`/tmp/ffflow-plans/…`).
- **Capture never changes issue state.** It does not close, reopen, or otherwise transition issues, and it never applies or removes the `ready` label. It may add other labels.

**The `ready` label is reserved for integrators.** fffactory uses it as its human "dispatch this epic" gate. FFFlow will not apply, remove or interpret `ready` without a major bump. fffactory plans to make its readiness label configurable (defaulting to `fff-ready`); once that ships, this reservation can be revisited.

### 4. Executing work: `/fff:work-epic <epic-number>`

The one skill integrators may start unattended. Given an epic issue number, on the GitHub backend it:

- **Resolves** the epic's open tasks (§3) and executes them in FFFlow's task order.
- **Works in the current checkout.** It never creates a worktree, so it is safe inside one the integrator created. The working tree must be clean.
- **Uses one branch, `epic/<epic-number>`.** Integrators may treat a remote `epic/<epic-number>` branch as a sign that the epic is underway or done. If the branch already exists, the skill stops and asks. It branches from `origin/main` today; integrators that need another base must instruct the agent (see `--base` below).
- **Produces one pull request** from `epic/<epic-number>` that references every task as `#<task-number>` in its title or body. No particular PR title or closing keyword is promised.
- **Keeps the human merge boundary.** It never merges and never force-pushes. Closing task and epic issues happens only after a human confirms the merge.
- **Stops and asks** on unexpected state: a dirty tree, an existing branch, a task without acceptance criteria, a review that fails three cycles, or zero tasks resolved. An unattended integrator must give those questions somewhere to land (fffactory uses Paseo's question queue).

### `/fff:work-issue <issue-number>`

Not yet covered for unattended use. Interactively, it opens one PR per issue whose body references `#<issue-number>`.

## Internal conventions

These support FFFlow's own execution workflow and stay free to evolve together, as long as task resolution and execution keep working. Integrators should not parse them:

- The `epic` label on epics, and `rid-<range>` labels on L3 tasks.
- Task-title ordinals (`T<N> — <title>`) and how `work-epic` orders tasks.
- The epic body's `## Tasks` checklist, and the `## Working notes` section on tasks.
- One commit per task, commit-message wording, and the PR title.
- How `work-epic` finds the epic's title and body ([#5](https://github.com/zerotechdebt/ffflow/issues/5)).

## Not yet in the surface

Integrator needs FFFlow hasn't adopted. Each becomes part of the surface when it ships.

| Need | From | Status |
|---|---|---|
| **`work-epic --base <branch>`.** Branch from, and target, a base other than `main`, for stacked epics and for repositories whose declared branch isn't `main`. Includes the stacked-PR lifecycle: record the base, then rebase, retarget and rerun the gates once the base merges. | fffactory ([factory#66](https://github.com/yaunder/factory/issues/66)) | Proposed |
| **An executor seam in `work-fanout`.** Keep today's in-session default and fanout reporting, while allowing tasks to run as separately supervised agents in workspaces owned by someone else. Paseo is fffactory's implementation; the seam stays general. | fffactory ([factory#65](https://github.com/yaunder/factory/issues/65)) | Proposed |
| **Single-task dispatch with `work-issue`.** Readiness, dependencies between tasks in one epic, per-task review. | fffactory | Needs discussion |
| **Tracker-independent issue access.** Operations such as `find-epic` and `find-epic-issues` exposed through one skill backed by the active capture cartridge, so integrators call FFFlow rather than reading GitHub labels directly. That would shrink §3 to a few skill calls. | fffactory | Needs discussion |
| **Shared work claims and progress.** Execution recording claims and status in the tracker itself, so several factories, or a factory and a person, can work the same repository without duplicating an epic and anyone can report on progress. Today the only cross-machine signal is the `epic/<n>` branch, which `work-epic` pushes only when the PR opens. | fffactory | Needs discussion |
| **Audit invocation and results.** How an integrator runs FFFlow's audits and gets a report on spec adherence. | fffactory | Needs discussion |

## Trust boundary

Everything in this surface that comes from GitHub (issue titles, bodies, comments, PR text) is written by people, not by FFFlow alone. Anyone who can edit an issue can change its title or body, and on a public repository anyone can comment, which includes posting a `Depends on #<number>` line. An unattended agent running `work-epic` reads that text. Integrators should treat it as untrusted input: gate dispatch on something only maintainers can set (fffactory's `ready` label requires triage access), and supervise the agent's permission requests rather than pre-approving them.
