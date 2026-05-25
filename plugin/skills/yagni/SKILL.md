---
name: yagni
description: Review-time discipline — only build what you need. Provides the TODO-with-trigger format that bridges "fix now" (zero-tech-debt) and "we'll get to it" (the smell). Triggers must be concrete inflection points, not vague intentions. Tension partner with zero-tech-debt.
---

# yagni

## Purpose

A reference rulebook (all levels). Loaded alongside `zero-tech-debt` by the same touchpoints. Not invoked as a tool.

The core rule: **only build what you need.** When zero-tech-debt would have you fix something at review time, but the fix is premature — because the right design depends on a future condition you haven't hit yet — defer with a documented trigger instead. Never "we'll get to it."

`yagni` provides the format and discipline for the deferral. Together with `zero-tech-debt`, it collapses the review-time choice to **fix now or write the trigger**. There is no third option.

## When this loads

Same touchpoints as `zero-tech-debt`:

- `/fff:code-review`
- `/fff:self-review`
- `/fff:work-issue` Phase 5
- `/fff:refactor`
- `/fff:audit` (the `tech-debt` cartridge enforces the trigger requirement)

## The TODO-with-trigger format

Two forms, both valid. Pick based on the complexity of the deferral.

### Single-line (trivial deferrals)

```python
# TODO(re-evaluate when 5+ RIDs land): switch to dynamic marker registration
```

For when the trigger is self-explanatory and the action is obvious. Single line, concrete trigger, one-sentence action.

### Multi-line (non-trivial deferrals)

```python
# TODO(re-evaluate when read-load > 1k req/s): caching layer in front of this query
# Current shape: direct query, ~200ms p99 at expected load
# What changes: introduce Redis cache with 5-min TTL; cache invalidation on writes
```

For when the trigger needs explanation, the current shape's justification matters, or the proposed change deserves more than a sentence. Use this when a future reader would benefit from knowing *why* the deferred decision is correct now and *what* would change later.

## What counts as a concrete trigger

A trigger must be a **specific inflection point** that someone could observe and recognize. Good triggers:

- `re-evaluate when 5+ RIDs land`
- `re-evaluate when read-load > 1k req/s`
- `re-evaluate when we add a third workspace member`
- `re-evaluate after the v2 schema migration`
- `re-evaluate when the team is > 4 engineers`
- `re-evaluate when this file exceeds 300 LoC`

Bad triggers (forbidden):

- `eventually` — when?
- `when we have time` — never.
- `if it becomes a problem` — by then it's already a problem.
- `someday` — see above.
- `TODO: refactor this` — no trigger at all.

If you can't name a concrete inflection, the deferral isn't legitimate yagni — either zero-tech-debt says fix it now, or the right move is to file a captured issue (durable in the tracker), not a code TODO.

## What deferral is for

Deferral is right when:

- **The current shape is correct for today's scale.** A simple solution that works for the current load isn't tech debt — it's appropriately sized.
- **The right future shape is conditional on information you don't have yet.** Building generality before you know which axis varies is the premature-abstraction smell.
- **The fix would expand scope materially.** A 4-hour refactor in a 30-minute PR is the wrong proportion; defer with trigger.

Deferral is NOT right when:

- The fix is uncontroversial and under 15 minutes (that's zero-tech-debt territory).
- The "trigger" is vague (write a captured issue instead, or fix now).
- You're using yagni to avoid pedantry pushback (fix the nit; pedantry isn't a code-quality concept).

## What yagni protects against

The opposite failure mode from zero-tech-debt's pedantic perfectionism:

- **Over-engineering.** Building speculative abstractions, generic interfaces, configuration hooks, and parametrization for cases you haven't hit.
- **Premature optimization.** Caching layers, batching, sharding before measurement shows they're needed.
- **Generality before specifics.** Three users today, written as if it'll be three thousand tomorrow.
- **Architectural cathedrals on greenfield projects.** Hexagonal layering with seven ports on a two-week prototype.

Zero-tech-debt without yagni breeds over-engineering. Yagni without zero-tech-debt breeds drift. The pair holds the line.

## Anti-patterns

- **Bare `# TODO` / `# FIXME` / `# XXX` comments.** No trigger = no plan = won't happen. Forbidden.
- **Vague triggers** (`eventually`, `someday`, `when we have time`). These are deferral-without-deferral. The audit cartridge flags them.
- **"Future work" sections in PR bodies.** PR bodies disappear when the PR closes. Code TODOs persist; captured issues persist. Prose in PR bodies doesn't.
- **TODO-with-trigger as a substitute for fixing.** If zero-tech-debt's 15-minute test says fix it, fix it. Yagni isn't an escape from review-time discipline; it's the discipline for the cases where deferral is legitimate.
- **Using yagni to avoid uncomfortable conversations.** "This code has a real problem but I don't want to push back" → that's a blocker, not a yagni case.

## Auditing

The `/fff:audit --type tech-debt` cartridge scans for:

- Bare `TODO`/`FIXME`/`XXX`/`HACK` without a trigger condition.
- Comments with vague triggers (`eventually`, `someday`, `when we have time`).
- "We should..." / "Consider..." comments without an actionable next step.
- PR body "future work" sections (those should be issues or code TODOs).

Findings convert to refactor tasks via `/fff:audit --plan`.

## Related

- **`zero-tech-debt`** — tension partner. The "fix it now" side of the binary.
- **`defect-driven-specification`** — for behavioral invariants and bug-derived spec entries (L1+). Different category: that's spec-level annotations; this is code-level sizing decisions. No overlap.
- **`audit` cartridge `tech-debt`** — enforces the trigger requirement project-wide.

## Friction addressed

- "We'll get to it" comments that become permanent code archaeology.
- Speculative generality that costs maintenance for capabilities never used.
- Reviewers reaching for "follow-up issue" as a stalling move when they should either fix or trigger.
- TODOs that proliferate without dates, contexts, or owners.

## Quality checks

Every deferral you record:

- [ ] Has a concrete, observable trigger (someone could recognize when it fires).
- [ ] Names what would change at the trigger, not just that something would change.
- [ ] Uses single-line format only when the trigger and action fit; multi-line when explanation matters.
- [ ] Lives in the code (not in PR-body prose or in a slack message).

If a check fails, the deferral isn't legitimate. Re-classify: fix now (zero-tech-debt), file as a captured issue, or sharpen the trigger.
