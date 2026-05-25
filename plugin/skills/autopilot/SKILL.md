---
name: autopilot
description: Meta-skill that wraps any interactive skill for unattended execution. Reads project context to stand in for the user on routine decisions, with a decision log.
---

# autopilot

## Purpose

Wrap an interactive skill and run it without stopping to ask. Different from `--dangerously-skip-permissions`: provides **contextual judgment**, not just auto-approval.

"Take over and do what I would do, and tell me what you did."

## When to invoke

- Routine chains: `/autopilot plan-breakdown → plan-capture`.
- Overnight runs: `/autopilot work-fanout 101 102 103 104`.
- Maintenance loops where the answers are determinable from project state.

## When NOT to invoke

- First-time setup requiring human judgment about project direction.
- Strategic or creative decisions (naming a product, choosing architecture from scratch).
- Domain knowledge the codebase can't provide.
- Anything you'd want to review before it ships. Use the interactive skill directly.

## Inputs

```
/autopilot <skill-name> [skill-args...]
```

Optional flags:
- `--ask-on <list>` — force interruption on specific decision types (e.g., `--ask-on destructive,architecture`).
- `--decision-log <path>` — write decisions somewhere other than the default.

## Outputs

- Whatever the wrapped skill produces.
- A decision log: `/tmp/ffflow-autopilot/<project-hash>/<timestamp>-<skill>.md` listing every choice the autopilot made and the evidence behind it.

  Logs are transient (same `/tmp` + project-hash convention as `notetoself` and plan dirs). The durable record of unattended decisions is whatever the wrapped skill committed — code, spec changes, issues. The log is for spot-checking the autopilot's reasoning when something looks off.

  If you want a log to survive `/tmp` cleanup (rare), pass `--decision-log <repo-relative-path>`.

## Dependencies

Any skill, dynamically.

## How it decides

Autopilot reads the room before it acts. Inputs to every decision:

- `.ffflow/config.yaml` — level, stack, capture backend.
- Root `CLAUDE.md` and module-level CLAUDE.md files.
- Codebase patterns: imports, test style, directory layout, naming.
- Recent git history (last 10–20 commits).
- Existing plans in `plan/` (prior decisions are guidance).
- Justfile / package scripts (the project's declared commands are the answer to "how do I run X?").

Every decision must cite at least one piece of evidence. **Bad autopilot decisions cite convention; good ones cite the codebase.**

## Decision principles

1. **Consistency over novelty.** Match what exists. Don't introduce new patterns mid-run.
2. **Simplicity when ambiguous.** Two valid paths, no clear signal — take the simpler one.
3. **Ask on high stakes.** Even in autopilot, some things warrant interruption:
   - Destructive operations (delete branches, force-push, rm files outside the worktree)
   - Architectural choices (new layer, new pattern, new dependency)
   - Ambiguous domain questions (what does "premium user" mean here?)
4. **Never force-push or delete** without **explicit prior authorization** from the user. Not implicit. Explicit.
5. **Context over preference.** The codebase is the authority. Not general knowledge. Not opinion.

## Decision-log format

Every autopilot decision logged as:

```markdown
## <Decision title>

**Question:** <what the wrapped skill asked or implied>
**Chose:** <option>
**Evidence:**
  - <file:line> — <relevance>
  - <commit hash> — <relevance>
**Alternatives considered:** <option B>, <option C>
**Confidence:** <high | medium | low>
```

Low-confidence decisions are flagged for the user to spot-check.

## Interruption discipline

Even in autopilot, hard interrupts apply:

- The wrapped skill's `Plan Mode discipline` clause is respected — autopilot doesn't bypass it.
- Skill hard gates (e.g., `plan-breakdown` refusing if `?` markers exist) are honored — autopilot resumes `plan-chat` to resolve decisions first.
- PR-checkpoint protocol in `work-issue` / `work-fanout` is honored — autopilot pauses, but auto-confirms unless `--ask-on pr-checkpoint` is set.

## End-of-run report

```
autopilot complete: <skill>
  Decisions made: 7 (5 high-confidence, 2 medium)
  Decision log: /tmp/ffflow-autopilot/<project-hash>/<ts>-<skill>.md

  Low-confidence flags:
    - "Should this go in domain or application layer?" → domain (cited src/auth/*)
      Spot-check recommended.

  Wrapped skill output: <whatever the skill returned>
```

## Anti-patterns

- Guessing based on popularity ("Jest is standard") instead of checking what's installed.
- Introducing tools or patterns the project doesn't use.
- Making architectural decisions that belong to the user.
- Skipping context gathering because the answer seems obvious.
- Logging decisions without evidence citations. The log is worthless if it just says "chose X."

## Success criteria

Good autopilot decisions cite evidence. Bad ones cite convention. If you can't point to a file, a config, or a commit — stop and ask.

## Friction addressed

- Routine chains where every answer is determinable but the user still has to type "y" to each.
- Overnight runs where the user wants to wake up to a result, not 14 unanswered prompts.
- `aug-core:automate` replaced by something that knows the project's conventions, not just a yes-key.
