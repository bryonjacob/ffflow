---
name: plan-chat
description: Interactive design of a behavior change — produces a plan describing the path from current spec to target spec, adapted to project level (L0–L3). Resolves every decision before sealing.
---

# plan-chat

## Plan Mode

This skill does NOT invoke Plan Mode. Claude Code's Plan Mode and FFFlow plans are different things — this skill creates an FFFlow plan on disk by writing files and confirming with the user, not by entering Plan Mode.

## Purpose

Stand up a working plan directory for one change. By the end of the session there is a sealed `<plan-dir>/plan.md` describing the path from current to target spec, plus a `decisions.md` capturing every choice made — with **zero open `?` markers**.

## When to invoke

- A new behavior change is about to start.
- Useful at every level. The artifact format changes with level; the workflow doesn't.

## Inputs

- A description of the change (free-form, from the user).
- `.ffflow/config.yaml` — read for level, stack, capture backend.

## Outputs

Where `<plan-dir>` = `/tmp/ffflow-plans/<project-hash>/<slug>/` (project-hash from `sha256(pwd) | head -c 16`, same convention as `notetoself`).

- `<plan-dir>/plan.md` — the plan itself.
- `<plan-dir>/decisions.md` — every decision made + rejected alternatives. Zero open `?` markers when sealed.
- `<plan-dir>/chat-log.md` — optional running transcript for archaeology.
- `<plan-dir>/metadata.json` — slug, phase, created date, level.
- Optionally a draft spec delta (`<plan-dir>/spec-delta.md`) showing the proposed spec change.

## Dependencies

- Level-appropriate methodology skills, loaded as reference context:
  - L1+: `hexagonal-architecture`, `defect-driven-specification`.
  - L2+: `writing-specs`, `spec-first-development`, `contract-enforcement`.
  - L3: `rid-traceability`, `total-specification`, `quality-gates`.

## Flow

### 0. Setup

1. Read `.ffflow/config.yaml`. If absent, prompt the user to run `/init-ffflow` first and stop.
2. Ask for a short kebab-case slug for the plan (e.g. `auth-token-refresh`).
3. Create `<plan-dir>/`. If one already exists for this slug, offer to resume rather than overwrite.
4. Write a skeleton `plan.md` with the three phase headings and the slug + level recorded at the top.
5. Write `metadata.json` with `phase: chat-incomplete`.

### 1. Understanding

Clarify scope. Ask sharp questions early.

- What problem does this solve? Who benefits?
- What does the current evergreen spec say about this area? Read it before asking the user.
- What exists in the code? Scan for related modules / ports / adapters / spec entries.
- What's out of scope? Mark explicitly.
- What constraints apply? Performance, security, compatibility, deadline.

Do not move on until the user confirms the problem statement. Write the confirmed problem statement into `plan.md` Phase 1.

### 2. Architecture / Approach

Design the path through the code.

- **L0**: prose. "We'll add X to module Y. The contract is: input A → output B." That's enough.
- **L1**: prose + hexagonal layer mapping. Which port? Which adapter? Where does the new code sit?
- **L2**: prose + draft Gherkin Rules + Scenarios. Tag `@property-based` candidates. Identify spec types per layer.
- **L3**: above, plus draft RIDs (`@RID-XXX` placeholders), mutation-testing scope, contract enforcement plan.

Surface decisions as you go. Open ones use `?` markers in `decisions.md`:

```
? Should token refresh happen on every request or only when expiring < 5 min?
```

Write decisions to `decisions.md` continuously as conversation proceeds. Don't batch them at the end.

### 3. Path

Describe the change as a sequence of steps that will become tasks. This is not the same as `plan-breakdown` (which decomposes into independent chess moves), but it does the rough cut.

- Which parts of the spec change, in what order?
- What depends on what?
- Where are the natural commit boundaries?

Write to Phase 3 of `plan.md`.

### 4. Resolve every open decision

**This skill does not seal until every `?` marker in `decisions.md` is resolved.** No exceptions.

For each open `?`:

1. **Restate the question** in plain language. Don't dump the `?` block back; rephrase.
2. **Present 2–3 alternatives**, each with:
   - A concrete name.
   - A one-line tradeoff (cost vs. benefit).
   - Implications for spec, implementation, or downstream work.
   Use evidence where available — file references, similar past decisions, prior plans in `/tmp/ffflow-plans/<project-hash>/`.
3. **Name a recommendation.** Don't be neutral. The user can override; abstaining wastes their time.
4. **Ask for confirmation.** Either "go with X" or "different — tell me which."
5. **Record the answer** in `decisions.md` with rejected alternatives:

   ```
   ✓ Token refresh strategy
      Chose: threshold-based (refresh when < 5min remaining)
      Rationale: balances network overhead against the auth-failure cliff for users on slow networks.
      Rejected alternatives:
        - every request: too much network traffic
        - on 401 retry: too much latency for unhappy paths
   ```

6. If the decision changes content in Phase 2 or Phase 3 of `plan.md`, update those sections — don't strand stale text.

If the user wants to **defer** a decision, write `? (deferred): <reason>` and continue. The skill will still refuse to seal — `plan-breakdown` requires zero opens.

### 5. Seal

Plan is sealed when:

- Zero open `?` markers in `decisions.md` (deferred markers count as open).
- User confirms "ready to break this down."

Update `metadata.json`:
```json
{
  "phase": "chat-complete",
  "ready_for_breakdown": true
}
```

Print:
```
✓ <plan-dir>/ sealed (chat-complete)
Next: /plan-breakdown
```

## Resume

Re-running `plan-chat` against an existing plan directory:
1. Read `metadata.json`. If `phase: chat-complete` and user is starting a new direction, refuse — they should start a new plan slug, or revert the metadata explicitly.
2. Otherwise, read `plan.md` and `decisions.md`. If any `?` markers exist, jump to step 4 (resolve every open decision). Otherwise, pick up at the latest unfinished phase.

## Friction addressed

- Plan Mode misfires (200+ turn chats inside Plan Mode that should have been writing to disk).
- Bloated chats that lose context after `/clear`. Plan files persist.
- Hand-pasted "walk me through alternatives" templates — now part of the chat's discipline.
- Plans that "seal" with open questions, then surprise everyone at breakdown time.
- Specs falling behind — plan optionally writes a spec-delta to commit alongside the work.

## Anti-patterns

- Don't write final RIDs here. Placeholders only — RIDs assigned at capture.
- Don't decompose into tasks here — that's `plan-breakdown`'s job.
- Don't try to do all three phases in one turn. Confirm each phase with the user.
- Don't write code. Plans describe intent.
- Don't seal with open `?`s. The discipline is what makes breakdown clean.
- Don't recommend "it depends" — pick something.
- Don't lose rejected alternatives. Future archaeology needs them.

## Quality checks before sealing

- [ ] Problem statement recorded in `plan.md` Phase 1, confirmed by user.
- [ ] Architecture/approach written in Phase 2, with level-appropriate detail.
- [ ] Path written in Phase 3.
- [ ] `decisions.md` has zero open `?` markers (including deferred).
- [ ] `metadata.json` shows `chat-complete`.
- [ ] At L2+, draft Gherkin parses if any was written.
