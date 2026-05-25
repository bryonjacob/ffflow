---
name: self-review
description: Pre-PR self-review checklist — spec correctness, implementation quality, test coverage, audit pass. Level-aware.
---

# self-review

## Purpose

Review your own diff with fresh eyes before pushing the PR. Catch the obvious problems before another human (or a CI gate) does.

Loaded by `work-issue` at Phase 5.

## Inputs

- The current branch's diff against base (`git diff <base>...HEAD`).
- `.ffflow/config.yaml` — read for level.
- The task issue body (for spec back-link and acceptance criteria).

## Outputs

- Either:
  - A green report (PR is ready), with a verification summary that goes in the PR body.
  - A red report listing concrete issues to fix. Return to `work-issue`'s relevant phase.

## At a glance — what scales with level

| Phase | L0 | L1 | L2 | L3 |
|---|---|---|---|---|
| **Spec review** | Re-read prose section | + hexagonal layer notes | Re-read Rule + scenarios; check annotations | + RID coverage, property-test ranges |
| **Code review** | Clarity / correctness / maintainability / hygiene / tech-debt discipline | + port/adapter cleanliness | + step definitions bound | + complexity within budget, no 0% mutation funcs |
| **Verification** | lint + format + tests + coverage + `/audit --type tech-debt` clean | + `/audit --type claude-md` clean | + `/audit --type spec` + `/audit --type char-tests` | + full `quality-gates`, mutation score |

The phase ordering is the same at every level; the checklist scales.

## Three phases, in order

### Phase 1 — Spec review

The spec comes first. Wrong specs produce wrong code that passes wrong tests.

Open the spec sections this PR touches:

- **L0/L1**: prose spec. Re-read the affected section. Does it match what the code actually does?
- **L2**: `.feature` file Rule(s). Are scenarios complete? Missing edge cases? Readable to a non-developer?
- **L3**: above + RID tags present, traceable, unique. Property-based scenarios cover the right input space?

**Ask:** would a product owner accept this spec content as the definition of done?

### Phase 2 — Code review

Review as if someone else wrote it.

**Clarity**
- Names descriptive. Logic obvious.
- Comments only where the *why* is non-obvious. No comments restating *what* the code does.
- Would this make sense to someone unfamiliar?

**Correctness**
- Edge cases handled or explicitly out-of-scope.
- Error paths covered.
- Adapter boundaries clean — no domain logic leaking into adapters (L1+).

**Maintainability**
- Single responsibility per function.
- No duplication beyond the rule of three.
- Future changes easy.

**Hygiene**
- No leftover `console.log` / `print` / debug.
- No commented-out code.
- No magic numbers, no hardcoded values that should be config.

**Review-time discipline (`zero-tech-debt` + `yagni`)**

Every minor issue you noticed during review is in one of three states. There is no fourth.

- **Fixed in this PR.** If a fix was <15 min and uncontroversial (`zero-tech-debt`'s 15-minute rule), it's already in your diff.
- **TODO-with-trigger** in the code. If you deferred, the comment includes a concrete inflection (`# TODO(re-evaluate when <trigger>): <action>`). Vague triggers (`eventually`, `someday`, `when we have time`) are forbidden — see `yagni`.
- **Blocker.** If something has to change before merge, that's not deferral; it's the gating decision.

What's *not* allowed: "we should..." / "consider..." comments, bare `# TODO`s, "future work" sections in the PR body. Anything in those shapes is a self-review fail; fix or trigger before marking ready.

The `/fff:audit --type tech-debt` cartridge enforces this project-wide. Self-review is the per-PR enforcement.

### Phase 3 — Verification

Run gates per level.

- **L0**: lint + format + tests pass. Coverage threshold met (if configured). `/audit --type tech-debt` clean (no bare TODOs, no vague triggers).
- **L1**: above + `/audit --type claude-md` clean on touched docs.
- **L2**: above + `/audit --type spec` clean on touched specs + `/audit --type char-tests` clean if any characterization tests are pinned to this spec.
- **L3**: full `quality-gates` pass: structure / correctness / coverage / maintainability. Mutation testing for touched scope ≥ threshold.

If any gate fails, fix or explain. Don't mark ready with known failures.

## Output: verification summary

Goes in the PR body (`work-issue` Phase 6 picks this up). Shape:

```markdown
## Verification (self-review)

- Spec sections reviewed: <list>
- Tests added: <count> new, <count> modified
- Coverage: <line%> line, <branch%> branch
- Audits run:
  - claude-md: <pass | n/a>
  - spec: <pass | n/a>
  - <others per level>
- Mutation score (L3 only): <score%>
```

## Outcome

**Pass** → mark PR ready (or keep draft if other gates still pending). Verification summary included.

**Fail** → fix the issue. Do not mark ready with known problems. Return to `work-issue`'s relevant phase and iterate.

## Anti-patterns

- Reviewing only the diff — forgetting to consider the spec change.
- Reviewing only the spec — assuming the implementation matches.
- Marking ready with "I'll fix it in a follow-up" — that's a PR-author archaeology hazard.
- Skipping Phase 3 because "tests passed when I wrote them." Re-run.
