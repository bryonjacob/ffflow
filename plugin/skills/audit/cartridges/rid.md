# Audit cartridge: RID traceability (L3)

## Purpose

At L3, requirement traceability is enforced. This auditor wraps `specdrive audit` and translates its findings into the unified report format the `audit` coordinator expects.

Only runs at L3. At lower levels, this skill no-ops (returns `not_applicable`).

## Prerequisites

- `.ffflow/config.yaml` shows `level: L3` and `features.rid_traceability: true`.
- `specdrive` reachable (it's a language-agnostic CLI run via `npx specdrive`; needs Node/npm on PATH regardless of the project's stack). Provisioned by the stack skill at L3.
- A `.feature` corpus with RID tags per `rid-traceability` skill.

## Inputs

- `.ffflow/audit.yaml` for state.
- Project root.
- `--ci` flag (passed through from `audit`).
- `--changed-only` for incremental audits on a PR.

## Outputs

- Findings in the unified format.
- Updated `.ffflow/audit.yaml` under `auditors.rid:`.

## What specdrive audit checks

Per `rid-traceability`:

- **S1**: Every scenario has an `@RID-*` tag.
- **S2**: All RIDs are unique across the project.
- **S3**: Every RID matches `@RID-{CONTEXT}-{NAME}-{NNN}` format.
- **S4**: Every CONTEXT matches the scenario's directory under `specs/`.
- **S5**: Every step has a step definition (no unbound scenarios).
- **S6**: No orphaned step definitions.
- **S7**: `@known-defect` count within configured maximum.
- **S8**: `@unverified-intent` resolved within configured timeframe.

If `features.mutation_testing: true` is set, also:
- **M1**: Mutation score for domain ≥ threshold.
- **M2**: Mutation score for application ≥ threshold.
- **M3**: No function has 0% mutation score.

## Flow

### 1. Verify L3

If level ≠ L3, return:
```json
{ "auditor": "audit-rid", "status": "not_applicable" }
```

### 2. Run

```bash
npx specdrive audit --json
```

(Or `npx specdrive audit --json --changed-only` if `--changed-only` was passed.)

Run via `npx` so the same invocation works on every stack — specdrive audits the Gherkin specs + JUnit XML, not the project's source language. If the justfile defines a `spec-audit` recipe, prefer `just spec-audit` to honor any project-pinned version.

If `specdrive` can't run (Node/npm missing, or specdrive not resolvable), return:
```json
{
  "auditor": "audit-rid",
  "status": "fail",
  "findings": [{
    "severity": "high",
    "summary": "specdrive CLI not available. Ensure Node/npm is installed (specdrive runs via npx); the stack skill provisions it at L3.",
    "auto_fixable": false
  }]
}
```

### 3. Translate

`specdrive`'s JSON output uses its own schema. Translate each finding into the unified format:

| specdrive code | Severity | Description template |
|---|---|---|
| S1 (missing RID) | high | "Scenario '<name>' in <file> has no @RID tag." |
| S2 (duplicate RID) | high | "@RID-X appears in both <file1> and <file2>." |
| S3 (bad format) | medium | "RID '<value>' does not match @RID-{CONTEXT}-{NAME}-{NNN}." |
| S4 (context mismatch) | medium | "RID '<value>' context does not match directory <dir>." |
| S5 (unbound scenario) | high | "Scenario '<name>' has no step definition for step '<step>'." |
| S6 (orphaned stepdef) | low | "Step definition '<pattern>' in <file> matches no scenario." |
| S7 (defect count) | medium | "@known-defect count <N> exceeds max <M>." |
| S8 (unverified expired) | medium | "@unverified-intent on '<scenario>' is <days> days old (max <max>)." |
| M1/M2 (mutation low) | medium | "Mutation score for <layer> is <X%>, below threshold <Y%>." |
| M3 (zero-mutation function) | high | "Function <name> has 0% mutation score — tests don't catch any change to it." |

### 4. State updates

Update `.ffflow/audit.yaml`:

```yaml
auditors:
  rid:
    last_run_commit: <HEAD>
    last_run_at: <UTC ISO>
    scenario_count: <N>
    rid_count: <N>
    annotations:
      known_defect: <count>
      unverified_intent: <count>
      accepted_risk: <count>
    mutation_score:
      domain: <pct>
      application: <pct>
```

These don't drive the audit (specdrive's own state does that), but the unified `audit.yaml` is the single-pane view.

### 5. Report

Return findings to the `audit` coordinator. The coordinator emits the unified report.

## CI integration

`ci-gates` workflow includes (at L3):

```yaml
- name: RID audit
  run: pnpm dlx claude-code --ci /audit --type rid --ci > audit-rid.json
```

Non-zero specdrive exit → non-zero `audit` exit → PR check fails.

## Incremental mode

`--changed-only` flag instructs specdrive to scan only files touched in the current PR. Used in the per-PR gate to keep CI fast. The full audit runs nightly or on `main` push.

## Edge cases

- **No `.feature` files**: status `pass`, scenario_count 0. Don't fail just because there's no spec corpus yet.
- **specdrive version mismatch**: surface as `high` severity finding asking the user to update the stack-installed version.
- **Mutation step takes too long**: respect `audit-rid --max-runtime-min` config (default 30 min). Above that, surface as a `warn` finding and skip the mutation checks for that run.

## Anti-patterns

- Running at L0/L1/L2. The auditor is a no-op there; the coordinator skips it.
- Translating specdrive findings as warnings when specdrive marks them as errors. Severity respects specdrive's classification.
- Forking specdrive's logic into this skill. This skill is a thin wrapper.

## Friction addressed

- `specdrive` output not integrated with the rest of FFFlow's audit story.
- L3 projects discovering RID drift via "I ran specdrive manually."
- Mutation scores invisible to PR reviewers (they live in Stryker / mutmut reports).
