# Audit cartridge: code-health (refactor signals)

## Purpose

Catch code-health problems before they compound. Runs the stack's complexity and duplication tools, plus the FFFlow-specific signals (test slowness, redundancy, hot spots).

Absorbs the former `test-optimization` skill — test health is a code-health signal at the same level as cyclomatic complexity.

Invoked by `/audit`. Findings can convert directly to a plan via `audit --plan`.

## Inputs

- `.ffflow/config.yaml` for thresholds (or defaults).
- Source + test trees.
- Stack skill for tool commands.

## Outputs

- Findings.
- Stage findings sorted by `impact / (complexity + 1)` for the plan-generation path.

## Thresholds

Defaults (overrideable in config):

```yaml
audit_refactor:
  complexity_limit: 10               # cyclomatic
  file_loc_warn: 250
  file_loc_block: 500
  duplication_threshold: 0.3         # 30% identical lines
  hot_spot_lookback_commits: 50
  test_unit_max_ms: 50
  test_spec_max_ms: 200
  test_suite_max_seconds: 30
```

## Flow

### 1. Complexity

Run the stack's complexity tool:

- Python: `ruff check --select C90 --config "lint.mccabe.max-complexity=10"`.
- TypeScript: `eslint . --rule 'complexity: [error, 10]'`.
- Java: SpotBugs cyclomatic complexity rule.

Each function above the limit is a finding (severity = low if just over, medium if 2× over, high if 3× over).

### 2. LoC

Per-file line counts. Files above `file_loc_warn`: low/medium severity (depends on layer — domain has tighter budget than infrastructure).

Files above `file_loc_block`: high.

### 3. Duplication

Run a duplication detector:

- Python: `pylint --disable=all --enable=R0801` or `jscpd --languages python`.
- TypeScript: `jscpd src/`.

Any duplicate cluster above `duplication_threshold` is a finding. Cite both/all instances.

### 4. Hot spots

Combine complexity with churn:

- For each file with complexity ≥ 8, count its commits in the last `hot_spot_lookback_commits`.
- "Hot spots" = complexity ≥ 8 AND churn in top 25%. Surface as high-priority findings.

The idea: a complex file nobody touches is fine; a complex file everyone keeps touching is where bugs accumulate.

### 5. Test health

From the former `test-optimization`:

**Speed analysis:**
- Per-test duration (`pytest --durations=0` / `vitest --reporter=verbose`).
- Unit tests over `test_unit_max_ms` → finding (low).
- Spec tests over `test_spec_max_ms` → finding (low).
- Total suite over `test_suite_max_seconds` → finding (medium).

Common causes annotated in the finding:
- DB call: mock with fixtures.
- External API: mock response.
- File I/O: in-memory.
- Sleep/wait: mock time.

**Redundancy:**
- Semantic overlap: tests with > 70% similar assertions → finding with both names, suggest deleting the weaker one.
- Cross-suite overlap: unit test and spec test asserting identical behavior at identical layer → finding, suggest consolidating to the appropriate suite.

**DRY opportunities:**
- Fixture candidates: repeated object creation across tests → finding.
- Parameterization: similar tests with different inputs → finding.

### 6. Prioritize

Sort findings by `impact / (complexity + 1)`:

- Speed fixes on slow tests: high impact, low complexity → top of list.
- Removing redundant tests: medium impact, low complexity.
- DRY refactoring: medium impact, medium complexity.
- Complexity reduction in a hot spot: high impact, high complexity → still high priority because of the impact.

## Plan-generation flow

When `/audit --plan` runs:

1. Filter to medium-or-higher severity findings.
2. Group by file when possible (one refactor task per file makes for cleaner PRs).
3. Generate a plan whose tasks read:

```markdown
# Task: Reduce complexity in src/auth/signup.py

## Problem
src/auth/signup.py contains 3 functions over complexity limit 10:
  - signup_user (complexity 17)
  - validate_signup_request (complexity 14)
  - persist_signup (complexity 12)

## Approach
1. Extract method for input validation phase.
2. Extract method for persistence phase.
3. Use a small DTO to pass data between phases.

## Out of scope
- Behavior change. This is a structural refactor only.
- Touching other files with similar issues.

## Acceptance
- [ ] All complexity warnings on signup.py cleared.
- [ ] Existing tests still pass with no modification.
- [ ] No new public API.
```

## Safeguards

- Never remove tests as part of a finding — only **suggest**. The user decides.
- Never apply complexity refactors automatically. The fix is structural; auto-application produces bad code.
- Re-run after any user-applied fix to confirm the finding is resolved.

## Anti-patterns

- Treating "high LoC" as inherently bad. Some files (configs, generated code, fixtures) legitimately are large — exclude via config.
- Counting every duplication as a finding. The rule of three: < 3 duplicates is acceptable.
- Recommending refactors that would break the architecture. Cross-check with `audit-architecture` before suggesting.

## Friction addressed

- Test suites drifting from <30s to >5 minutes over time, with no single PR being blamed.
- Complexity creeping into hot files where the cost of refactoring keeps rising.
- "We should refactor this someday" — `audit --plan` turns it into actual tasks.
- Test redundancy hiding behind growing coverage numbers.
