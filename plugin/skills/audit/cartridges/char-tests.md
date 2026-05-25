# Audit cartridge: characterization tests

## Purpose

Characterization tests pin existing behavior. They were added by `/characterize` (or by `/work` on a characterize plan's task) and exist to catch unintentional changes.

This auditor runs them. When they pass, the safety net holds. When they fail, **the failure is itself the finding** — and the auditor's job is to ask: was the test wrong, or did the behavior change?

Invoked by `/audit`.

## State

`.ffflow/audit.yaml`:

```yaml
auditors:
  char-tests:
    files:
      tests/characterization/test_auth.py:
        pins_spec: docs/specs/auth.md       # which spec entry this test pins
        last_passed: 2026-05-15T11:00:00Z
        commit_at_last_pass: abc123
```

`pins_spec` is the link. When a characterization test fails, the question becomes "which spec entry was supposed to be invariant here?"

## Inputs

- `.ffflow/audit.yaml`.
- The actual characterization test suite (`tests/characterization/` by stack convention).
- `.ffflow/config.yaml`.

## Outputs

- Findings per the `audit` contract.
- Updated `last_passed` and `commit_at_last_pass` for passing tests.

## Flow

### 1. Discover

Find characterization tests:
- Conventional: `tests/characterization/**/*` (or `specs/characterization/` at L2+).
- Explicit: tests registered in `.ffflow/audit.yaml` under `char-tests:`.

If both miss a test, opportunistically add it to the state file on first pass.

### 2. Run

Invoke the stack's test runner targeted at the characterization tests only:

- Python: `uv run pytest tests/characterization -v`
- TypeScript: `pnpm vitest run tests/characterization`
- Java: `mvn test -Dtest=Characterization\*`

Capture per-test pass/fail.

### 3. Triage failures

For each failing test, the auditor surfaces it as a finding but explicitly **does not classify** the failure as regression or intentional change. Both possibilities are presented:

```json
{
  "severity": "high",
  "file": "tests/characterization/test_auth.py::test_password_complexity",
  "summary": "Characterization test failed. Possibilities:\n  1. Regression: code broke; the test was right.\n  2. Intentional behavior change: behavior was updated and the spec entry it pins (docs/specs/auth.md 'Password complexity') needs updating.\n\nHuman judgment required.",
  "auto_fixable": false,
  "pins_spec": "docs/specs/auth.md",
  "test_output": "AssertionError: expected 'invalid' but got 'valid'"
}
```

This auditor never decides. It reports the divergence and the two possible interpretations.

### 4. Pass advance

For each passing test, advance `last_passed` and `commit_at_last_pass`. This is the keep-honest record.

## Integration with `--plan`

When `/audit --plan` runs and a characterization test failed, the resulting plan template includes:

- A `## Triage` section in `plan.md` flagging the test failure with both possibilities.
- A first task: "Decide: regression or intentional? If regression → fix the code in same PR. If intentional → update the spec entry and the characterization test in same PR."

`work-issue` is good at executing either branch once the decision is made; the triage is the human gate.

## Severity

- All characterization test failures are **high** severity by default. They mean the safety net the user paid to install is firing.
- Exception: if the characterization test pins a `@known-defect`'d behavior, failure may be expected — but only if the test was tagged accordingly. The user marks expected-failure tests explicitly:

### Strict blocking is intentional

A failing characterization test always blocks the PR. There is no auto-classification path; no "let it through and we'll fix it later" mode. The user must update the test **and** the spec in the same PR (regression case → fix code; intentional change → update spec).

This will feel painful in practice. **That is the point.** Characterization tests are the safety net. Softening them is the same as not having them. Future maintainers reading this skill: do not add a `--ignore-failures` flag, a `nightly-only` mode, or a "demote to warning" path. If the friction is too high, the project's discipline-vs-velocity tradeoff has shifted — that's a separate decision, not an auditor tweak.



```python
@pytest.mark.characterization_known_defect
def test_known_buggy_behavior():
    ...
```

Such tests are inverted: failure is the pass condition.

## Anti-patterns

- Deciding for the user whether the failure is a regression. The auditor stays neutral.
- Auto-updating the characterization test to make it pass. That defeats the entire point.
- Running on every commit. Characterization tests can be slow; gate them per PR via CI (`audit-char-tests` runs in the maintainability gate).
- Skipping characterized tests in CI to save time. The cost of a silent regression is much higher than the test runtime.

## Friction addressed

- Characterization tests turning into "delete-and-forget" tech debt because their failures are hard to triage.
- Regressions shipping because nobody knew which test pinned which behavior.
- Spec updates without the corresponding characterization test update.
