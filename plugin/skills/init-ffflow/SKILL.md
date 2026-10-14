---
name: init-ffflow
description: Bootstrap a project for FFFlow — write .ffflow/config.yaml, stamp the beliefs block into the root CLAUDE.md, propose level/stack/capture. Idempotent.
---

# init-ffflow

## Purpose

Stand up the minimum FFFlow scaffolding: one config file, plus the beliefs block that tells every future session in this repo what FFFlow holds non-negotiable. Everything else (audit state, spec directory, justfile, hooks) gets created lazily by the skill that needs it.

## Plan Mode

This skill does NOT invoke Plan Mode. Configuration writes are direct.

## When to invoke

- New project starting fresh on FFFlow.
- Existing project adopting FFFlow (see also `adopt-ffflow` for the full onboarding wrapper).
- Re-run any time to upgrade config (idempotent).

## Inputs

- Current working directory (project root).
- Optional: explicit `--level`, `--stack`, `--capture` flags.

## Outputs

- `.ffflow/config.yaml` written or updated — including the `ffflow_version` stamp.
- A managed **beliefs block** written into the project's root `CLAUDE.md` (created if absent), delimited by `<!-- ffflow:beliefs ... -->` markers.

The beliefs block is the *one* deliberate exception to this skill's "don't write project files" rule, and §2.11 explains why it has to be: a downstream session reads its own project's CLAUDE.md, never the plugin's docs. A belief the plugin professes but the repo never states is not in effect. The exception is bounded — only the bytes between the markers are ever written.

Notably **not** outputs:
- No `.gitignore` edits. Plans live in `/tmp/ffflow-plans/<project-hash>/<slug>/`, not in the project tree.
- No `.ffflow/audit.yaml` init. The first auditor to run creates it.
- No starter spec directory. `plan-chat` and `characterize` create it on first use at the configured `spec_location`.

## Dependencies

- The `stack` skill (consulted to propose stack defaults; cartridges for python, typescript, java, polyglot).
- `stack-init` (optional follow-up if the user wants justfile/git-hooks/CI installed in the same session).

## Flow

### 1. Detect existing state

- Read `.ffflow/config.yaml` if present. Treat it as the source of truth to upgrade, not overwrite.
- Detect language by file signals:
  - `pyproject.toml` or `*.py` → propose `stack: python`.
  - `package.json` with TS deps or `tsconfig.json` → propose `stack: typescript`.
    - **UI signal present** → propose `stack: typescript-ui` instead (the view-layer-purity toolchain, §2.9). UI signals: `react` / `react-dom`, `lit`, `@awesome.me/webawesome` (or legacy `@shoelace-style/shoelace`), `vue`, `svelte`, `@storybook/*`, or a `.storybook/` directory. When proposing `typescript-ui`, also propose a lane (`ui_baseline`) — `react` if a React signal, `web-components` if a Lit/Web-Awesome signal; ask if ambiguous or both present.
  - `pom.xml` or `build.gradle` → propose `stack: java`.
  - `Cargo.toml` or `*.rs` → propose `stack: rust`.
  - Multiple language signals → propose `stack: polyglot`.
- Detect test/coverage tooling already in place (pytest, vitest, etc.) for the proposal.
- Probe `gh auth status` (silent — `gh auth status >/dev/null 2>&1`). On success, capture the result for the next step.

### 2. Confirm with user

Single confirmation step. Present the proposed config inline.

If `gh` is authenticated, **ask explicitly** rather than silently defaulting:

```
gh is authenticated for this repo. Capture backend?
  1. github-issues (recommended — gh detected)
  2. linear
  3. jira
  4. markdown (file-based, no tracker)
```

If `gh` is not authenticated, default to `markdown` with a note.

Then present the rest of the config:

```
Proposed .ffflow/config.yaml:

  version: 1
  ffflow_version: 0.4.0
  level: L1
  stack: typescript
  capture: github-issues
  spec_location: docs/specs
  test_location: tests
  audit_state_file: .ffflow/audit.yaml

  features:
    property_based_testing: false
    mutation_testing: false
    rid_traceability: false
    four_quality_gates: false

Accept (a), edit a field (e), or abort (x)?
```

Default level is **L1** (light hexagonal layering + defect-driven specs, no Gherkin or RIDs yet). L0 is a deliberate downgrade choice; L2/L3 are deliberate upgrades.

**When the stack is `typescript-ui`,** also write the chosen lane to `.ffflow/stack.yaml` (the UI cartridge reads `ui_baseline` from there, not from `config.yaml`):

```yaml
extends: typescript-ui
dimensions:
  ui_baseline: react          # or: web-components
```

Mention in the confirmation that view-layer purity (§2.9) is now in effect — the sibling of hexagonal for the frontend — and that `/stack-init` will scaffold Storybook + tokens + the sample component triple.

When the user picks L2 or L3, flip the corresponding entries in `features:` automatically:
- L2: `property_based_testing: true`
- L3: all four feature flags on

### 2a. Honor the cartridge's `max_level`

Before writing the config, check the chosen stack cartridge for a `max_level:` declaration. All current cartridges — `typescript`, `typescript-ui`, `python`, `java`, `rust` — reach `max_level: L3` (`typescript-ui` inherits its base's). Every supported stack reaches every level.

specdrive (the L3 RID-traceability tool) is a **language-agnostic CLI**: it audits Gherkin `.feature` files and JUnit XML, not your source, and is distributed on npm. So L3 on a Python/Java/Rust project just needs Node/npm available to run `npx specdrive` — there is no PyPI / Maven Central / crates.io requirement, and no reason to cap these stacks at L2. (`stack-init` checks for `npx` at L3 and prompts to install Node if it's missing.)

If a cartridge ever *does* declare a `max_level` below the user's chosen level, and the user picked a level above that max, surface it:

```
Heads up: the `<stack>` cartridge declares max_level: <max>.
Drop to <max>, or pick a stack that supports the level you want?
```

But do not invent such a cap for `python`, `java`, or `rust` — they are L3-capable.

For **polyglot** stacks: each subproject inherits its own cartridge's max_level. Since all current cartridges are L3-capable, a polyglot L3 project needs no per-subproject downgrade on this account; only surface `level_override` prompts if a cartridge actually declares a lower max.

### 3. Write the config

Write `.ffflow/config.yaml`, including `ffflow_version` (the current plugin version, read from the manifest) and `ffflow_upgraded` (today).

### 3a. Stamp the beliefs block

Write the managed block into the project's root `CLAUDE.md`. If no root CLAUDE.md exists, create one with a minimal purpose line above the block — an FFFlow project without a root CLAUDE.md is a contradiction (§2.10).

**Placement:** after the file's opening purpose/overview section, before the first deep-detail section. High enough to be read; not so high it displaces the file's own introduction.

**Idempotency:** if the markers already exist, replace only what's between them. Never touch a byte outside. If the markers are missing or malformed, rewrite the block whole.

This is the canonical text. `upgrade-ffflow` refreshes it from here, so this block is the single source of truth — update it here and the upgrade path follows automatically:

```markdown
<!-- ffflow:beliefs v0.4.3 — managed by /fff:upgrade-ffflow. Edits inside this block are overwritten. -->
## FFFlow beliefs

This project runs [FFFlow](https://github.com/zerotechdebt/ffflow). These are the non-negotiables — the rules you should not have to discover.

- **Hierarchical CLAUDE.md.** Every significant module carries its own CLAUDE.md — a tree mirroring the module tree, not this root file alone. Adding one to a module that lacks it is *never* a new precedent; it is catching up to the norm. The root file stays a map; module-specific rules live with the module. A 2-line CLAUDE.md beats none. → `/fff:audit --type claude-md`
- **Specs and tests move together.** A spec entry without a test is documentation; a test without a spec entry is opaque. Spec updates ship in the same PR as the implementation. → `/fff:work-issue`, `/fff:audit --type spec`
- **Tech debt is marked or fixed, never deferred silently.** Fix nits in flight, or write `# TODO(re-evaluate when <trigger>): <action>`. "We'll get to it" without a code-level marker is not a plan. → `/fff:audit --type tech-debt`
- **Red, then green — wherever it's practical.** Write the failing test first and drive it to green. The artifacts scale with the level; the loop doesn't. Some edges genuinely resist it (exploratory spikes, config/scaffolding, hard-to-harness I/O, a bug you can't reproduce yet). At those edges, say so out loud and note what you did instead — an acknowledged exception is fine, a silent one is how the discipline erodes. → `/fff:tdd-loop`
- **Plans are transient, specs are evergreen, issues are transactional.** Three artifacts, three lifespans, three locations. Don't mix them.

Level and stack are declared in `.ffflow/config.yaml`. Run `/fff:upgrade-ffflow` after updating the plugin.
<!-- ffflow:beliefs end -->
```

**When the project's stack is a UI stack** (`typescript-ui`), add one more belief before the closing marker:

```markdown
- **View-layer purity.** Components are pure and presentational — no model, logic, or backend imports. Dependencies point view ← app, never the reverse. Decompose → story → test → *then* integrate. → `/fff:audit --type ui`
```

Keep the block short. A beliefs block that grows into a second architecture document stops being read, which defeats its entire purpose.

### 4. Report

```
✓ wrote .ffflow/config.yaml (level=L1, stack=typescript, capture=github-issues, ffflow_version=0.4.0)
✓ stamped FFFlow beliefs into CLAUDE.md

Plans live in /tmp/ffflow-plans/<project-hash>/<slug>/ — not in this repo.
Spec lives under docs/specs/ — created on first use.

Next steps:
  /stack-init           # install justfile, git hooks, CI workflow
  /plan-chat            # start designing your first change
  /characterize         # (brownfield) spec-extract existing behavior
```

## Idempotency rules

- Re-running with an existing config: read it, propose **only the changed fields** in the diff, confirm, write.
- Never silently downgrade a level or strip a feature flag.
- Don't touch `.ffflow/audit.yaml` even if it exists.
- Beliefs block: rewrite only between the markers, always. Content outside them is human-owned.
- Never downgrade `ffflow_version`.

## Friction addressed

- "Where do I even start?" — single command bootstrap.
- Capture-backend ambiguity — probe `gh` and ask explicitly rather than silently default.
- Plan artifact accidental commits — moot; plans live in `/tmp/`, never in the project tree.

## Anti-patterns

- Don't write project-level files outside `.ffflow/config.yaml` and the beliefs block in root `CLAUDE.md`. Lazy-init everything else. (The beliefs block is a bounded, marker-delimited exception — see Outputs. Do not let it become a precedent for writing other project files here.)
- Don't write the beliefs block *outside* its markers, or rewrite the user's root CLAUDE.md around it. The block is a guest in that file.
- Don't run `stack-init` automatically — that's a follow-up, not the bootstrap.
- Don't try to detect L0/L1/L2/L3 from existing files. Always ask. Level is a methodology choice, not a tooling detection.
- Don't gitignore `plan/`. It doesn't exist in the project tree anymore.
