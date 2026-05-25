---
name: zero-tech-debt
description: Review-time discipline — when you notice a minor issue, fix it now if it's <15 min and uncontroversial. Never "we'll get to it" without a code-level marker. Pair with yagni for the deferral cases. Loaded by code-review, self-review, work-issue, refactor, and audit.
---

# zero-tech-debt

## Purpose

A reference rulebook (all levels). Loaded as context by skills that decide what to do with noticed-but-not-blocking issues at review time. Not invoked as a tool.

The core rule: **default to fixing.** When you spot a minor issue during review — a name that doesn't read right, a redundant import, a function returning a value nobody uses, a comment that contradicts the code — and the fix is small and uncontroversial, fix it in the same PR rather than deferring.

The pair-skill `yagni` handles the cases where deferring is the right call. Together they collapse the binary choice: **fix it, or write a TODO-with-trigger**. There is no third option.

## When this loads

- `/fff:code-review` — the report template forbids a "Suggestions" section. Findings are blockers, fixed-in-flight, or TODO-with-trigger.
- `/fff:self-review` — pre-PR checklist asks "every minor issue you noticed: fixed or TODO-with-trigger?"
- `/fff:work-issue` Phase 5 — same self-review gate.
- `/fff:refactor` — when scanning for refactor targets, treat noticed nits as inline fixes rather than queueing them.
- `/fff:audit` — the `tech-debt` cartridge enforces this with a scan for unmarked deferrals.

## The 15-minute rule

If a fix would take **under 15 minutes** and is **uncontroversial** (no risk of regression, no API change, no scope creep), fix it now.

"Uncontroversial" means:
- No behavior change (or a behavior change you're already authorized for via the current task).
- No new dependency or pattern.
- No scope expansion beyond the file(s) you're already touching.
- Reviewable in the diff without additional context.

If a fix is bigger than 15 min, or touches something controversial, that's where `yagni` takes over: write the trigger and move on.

## What this looks like in practice

Real example, paraphrased from a session:

> Reviewing a Python hello-world PR, the reviewer notices:
> 1. A `from __future__ import annotations` that isn't load-bearing.
> 2. A test helper returning a value the When step never consumes.
> 3. A hand-maintained `markers = [...]` list that'll need extension as tests grow.
>
> Pre-rule: framed as "three polish items, not blockers."
> Post-rule:
> - Items 1 and 2 are uncontroversial 30-second fixes → fixed in a follow-up commit on the same PR.
> - Item 3 is a real sizing question (dynamic registration is the right call at scale but premature for two scenarios) → TODO-with-trigger in the code, not a separate ticket.
>
> No ghosts. No "follow-up" issues that never get picked up. PR ships cleaner.

## What this is not

- **Not "every refactor opportunity must be taken."** That's the `refactor` skill's job, with its own discipline (audit-driven, plan-tasked). Zero-tech-debt is about *noticed* issues at review time, not exhaustive scanning.
- **Not "block on perfectionism."** If a fix is bigger than 15 min or controversial, defer it — but defer with a trigger, not a shrug.
- **Not "no TODOs allowed."** TODOs are fine when they carry a trigger condition (`yagni` skill defines the format). Bare TODOs are the smell.

## Anti-patterns

- **"Follow-up issue" tickets that nobody picks up.** If it's worth doing, do it now. If it's not worth doing now, write the trigger.
- **PR-review "nits" left unaddressed because the reviewer didn't want to seem pedantic.** Pedantry is a moral panic, not a code-quality concept. Fix the nit.
- **"We should refactor this someday."** Either do it (zero-tech-debt) or write the trigger (yagni). "Someday" is the smell.
- **Bare `# TODO` / `# FIXME` / `# XXX` comments.** No trigger = no plan = won't happen. The `tech-debt` audit cartridge flags these.
- **"Future work" sections in PR bodies.** Captured issues (in the tracker) or code TODOs (with trigger). Not PR-body prose, which disappears as soon as the PR closes.

## Related

- **`yagni`** — tension partner. Provides the TODO-with-trigger format for cases where deferring is right.
- **`defect-driven-specification`** — for *behavioral* invariants and bug-derived spec entries (L1+). Different category from this skill: that's about spec-level annotations (`@known-defect`, `@unverified-intent`, `@accepted-risk`); this is about code-level sizing decisions at review time. No overlap.
- **`refactor`** — exhaustive scanning + planned refactor work. Zero-tech-debt is *noticed* issues at review; refactor is *sought* issues via tooling.

## Friction addressed

- Codebases that accumulate "minor" papercuts because every reviewer defers them.
- Follow-up tickets nobody picks up, leaving the original PR's author with the unspoken expectation that they'll come back.
- Reviewers who can't tell the difference between "ship it as-is" and "fix before merge" because the language has too many gradations.
- The implicit "third option" of shrugging at a noticed issue.

## Quality checks

Before signing off on a review (yours or someone else's):

- [ ] Every issue I noticed is one of: blocker (PR doesn't merge), fixed in this PR, or has a TODO-with-trigger in the code.
- [ ] No "consider..." / "we should..." / "future work" without a trigger.
- [ ] No bare `# TODO` without a re-evaluation condition.

If a check fails, you have the wrong framing. Re-classify or fix.
