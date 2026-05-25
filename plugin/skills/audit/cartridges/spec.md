# Audit cartridge: spec drift

## Purpose

Specs drift. Code moves; specs don't. This auditor catches that — every spec entry declares which code it describes, and the auditor verifies the spec still reads true against that code.

Invoked by `/audit`. Can also run standalone or in `--fix` mode for narrow auto-fixes.

## State

`.ffflow/audit.yaml`:

```yaml
auditors:
  spec:
    files:
      docs/specs/auth.md:
        commit: abc123                    # HEAD when last validated
        date: 2026-05-15T11:00:00Z
        scope: ["src/auth/**/*"]          # which code this spec describes
        characterized: true               # was the entry written by /characterize?
        characterized_by_session: <opt>
      docs/specs/payment.md:
        commit: def456
        date: 2026-05-10T08:00:00Z
        scope: ["src/payment/**/*"]
```

`scope` is the contract. Drift detection is: "does anything in `scope` have a commit later than `commit`?"

## Inputs

- `.ffflow/audit.yaml` state.
- `.ffflow/config.yaml` for level.
- Optional `--type <prose|feature|all>` to limit scope.

## Outputs

- Findings per the `audit` contract.
- Updated state with `validated_at` advanced for re-validated entries.

## Per-level mechanism

The drift trigger is the same at every level; the verification mechanism differs.

### L0 / L1 — prose specs

1. Detect drift: any file in `scope` has a commit newer than the entry's `commit`?
2. If drift detected, **LLM re-read**: load the spec section + all files in scope, then read each. Does the prose still read true?
3. Outcomes:
   - **No semantic mismatch** → re-validate (advance `commit` to current HEAD), report `pass`.
   - **Small semantic mismatch** (e.g., a renamed function still does the same thing) → `auto_fixable: true` with a one-line edit. Surface as `low` severity.
   - **Substantive drift** (behavior actually changed) → `auto_fixable: false`, surface as plan task. `medium` or `high` severity depending on the spec's importance.

### L2 — `.feature` files

1. Detect drift the same way.
2. **Run the scenarios.** If they all pass, behavior still matches spec; advance `commit`.
3. Failing scenarios are the drift signal:
   - Failure on a `@known-defect` scenario → expected, no finding.
   - Failure on a normal scenario → drift. Surface as finding with the scenario name and which step failed. `auto_fixable: false` — humans triage behavior changes.

### L3 — RID-traced specs

1. Drift trigger same.
2. **Wrap `audit-rid`** — that auditor uses `specdrive audit` for full RID validation (coverage, unbound scenarios, orphaned step definitions, mutation scores).
3. Translate `audit-rid`'s output into the unified report format.

## Substantive vs. cosmetic drift

A semantic mismatch where the spec still says correct things about new code is cosmetic — auto-fixable via a rewrite.

A drift where the spec says "X" and the code does "Y" is substantive — needs human eyes. Surface as a plan task via `audit --plan`.

The auditor doesn't decide whether the new behavior is right or wrong. It surfaces the divergence. Humans (or `defect-driven-specification` flow) decide if the code changed correctly.

## Characterized vs. authored

If `characterized: true`, the spec was extracted by `/characterize` and reflects observed behavior, not authored contract. Drift on a characterized entry means observed behavior changed — same finding flow, but worth labeling as "characterization-style drift" so the user knows the original intent wasn't ever pinned by hand.

## Annotations interaction

When running against L2+ specs, account for annotation tags:

- `@known-defect` scenarios: a failing one is expected (it documents broken behavior). A passing one is a finding (`@known-defect` should fail until removed).
- `@accepted-risk`: pass expected.
- `@unverified-intent` + age > configured days → finding (`unverified-intent expired`).

This wiring lives in `defect-driven-specification`; this skill just enforces it.

## Findings format

```json
{
  "severity": "low | medium | high",
  "file": "docs/specs/auth.md",
  "summary": "Drift on Rule 'Password complexity': src/auth/validator.py changed at commit abc123; spec re-read shows function signature changed.",
  "auto_fixable": false,
  "category": "freshness",
  "evidence": {
    "scope_changes": ["src/auth/validator.py"],
    "scenarios_failed": []
  }
}
```

## Fix mode

For `auto_fixable: true` findings (cosmetic drift):
1. Apply the proposed edit.
2. Re-run the auditor on that file.
3. Confirm passes.
4. Stage the change (don't commit — user reviews).

For substantive drift: never auto-fix. Always route to `audit --plan`.

## Idempotency

- Re-running with no code or spec changes since last validation: short-circuits to `pass` for each entry.
- The `commit` field on each entry is the cache key. If HEAD matches, no work.

## Anti-patterns

- Auto-fixing substantive drift. The auditor can't tell whether the behavior change was correct.
- Treating any spec edit as drift "resolution." Drift is resolved by **re-validating** the spec against current code, not by accepting it.
- Running at L0 with the L2 mechanism (running scenarios). At L0 there are no scenarios.
- Skipping the `@known-defect` inversion. A passing `@known-defect` scenario is a finding, not a pass.

## Friction addressed

- Specs going stale silently for a quarter.
- "Drift" not being a first-class concept — engineers re-discover it ad hoc.
- Conflation between drift (technical signal) and incorrect behavior (judgment call).
