---
name: init-ffflow
description: Bootstrap a project for FFFlow — write .ffflow/config.yaml, propose level/stack/capture. Idempotent.
---

# init-ffflow

## Purpose

Stand up the minimum FFFlow scaffolding: one config file. Everything else (audit state, spec directory, justfile, hooks) gets created lazily by the skill that needs it.

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

- `.ffflow/config.yaml` written or updated.

That's it. Notably **not** outputs:
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

When the user picks L2 or L3, flip the corresponding entries in `features:` automatically:
- L2: `property_based_testing: true`
- L3: all four feature flags on

### 2a. Honor the cartridge's `max_level`

Before writing the config, check the chosen stack cartridge for a `max_level:` declaration. Today, `python`, `java`, and `rust` cartridges all declare `max_level: L2` because [`specdrive`](https://github.com/specdrive/specdrive) is npm-only — there's no PyPI / Maven Central / crates.io publication.

If the user picked a level above the cartridge's max:

```
Heads up: the `<stack>` cartridge declares max_level: L2.

L3 requires specdrive (RID traceability tool), which only ships on npm today.
Your options:
  1. Drop to L2 — full mutation testing + spec audit; no RID gate.
  2. Use polyglot with a TypeScript subproject and put the L3 surface there.
  3. Proceed with L3 anyway — spec-audit will skip silently. Mutation works.

Pick 1, 2, or 3?
```

For **polyglot** stacks: each subproject inherits its own cartridge's max_level. If the project-level config says L3 but one subproject's cartridge tops out at L2, surface the subprojects that will need a `level_override` and ask the user to confirm the per-subproject levels.

### 3. Write the config

Write `.ffflow/config.yaml`. That's the entire write step.

### 4. Report

```
✓ wrote .ffflow/config.yaml (level=L1, stack=typescript, capture=github-issues)

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

## Friction addressed

- "Where do I even start?" — single command bootstrap.
- Capture-backend ambiguity — probe `gh` and ask explicitly rather than silently default.
- Plan artifact accidental commits — moot; plans live in `/tmp/`, never in the project tree.

## Anti-patterns

- Don't write project-level files outside `.ffflow/config.yaml`. Lazy-init everything else.
- Don't run `stack-init` automatically — that's a follow-up, not the bootstrap.
- Don't try to detect L0/L1/L2/L3 from existing files. Always ask. Level is a methodology choice, not a tooling detection.
- Don't gitignore `plan/`. It doesn't exist in the project tree anymore.
