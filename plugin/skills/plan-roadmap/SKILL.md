---
name: plan-roadmap
description: Phase-level planning above plan-chat. Reads a vision doc (project.md, README, free-form prompt) or an in-progress codebase and produces an ordered, dependency-aware roadmap of independently shippable phases. Each phase becomes a /plan-chat (or /characterize, or /audit --plan, or recursively another /plan-roadmap for very large phases). Use when starting a green-field project from a vision, or when adding a multi-phase capability to an existing one.
---

# plan-roadmap

## Plan Mode

This skill does NOT invoke Plan Mode. It writes a roadmap artifact to disk and confirms with the user phase-by-phase.

## Purpose

`plan-chat` is sized for one slice. `plan-roadmap` is sized for everything above that — a vision, a multi-phase capability, a green-field build-out. It produces an ordered list of phases with dependencies and rationale. Each phase becomes a tier-2 planning session (`/plan-chat`, `/characterize`, `/audit --plan`, or recursively another `/plan-roadmap`).

You use this when:
- Starting a green-field project from `project.md` or a vision prompt.
- Adding a large feature to a brownfield codebase that needs phased delivery.
- Re-orienting an existing project around a new direction.

You don't use this for:
- Single-slice changes — go straight to `/plan-chat`.
- Bug fixes — go straight to `/plan-chat` (or `/debugging` first).
- Drift cleanup — go to `/audit --plan`.

## Inputs

- **A vision**: file path (`project.md`, `README.md`, `VISION.md`), free-form description, or "what we want next" prompt.
- Optional `--phase <N>` to recurse on a specific phase from an existing roadmap.
- Optional `--vision-doc <path>` to point at a specific file when there's ambiguity.
- `.ffflow/config.yaml` — read for level, stack, capture backend.

## Outputs

- `<plan-dir>/roadmap.md` — the roadmap itself: ordered phases with rationale, scope, dependencies, success criteria.
- `<plan-dir>/phases/phase-N.md` — one placeholder per phase that becomes the starting point for that phase's tier-2 session.
- `<plan-dir>/decisions.md` — phase-level decisions made + open ones marked with `?`.
- `<plan-dir>/metadata.json` — slug, phase, created date, level, source (`vision-doc` / `prompt` / `recursion`).

Plans live in `/tmp/ffflow-plans/<project-hash>/<slug>/` per the standard convention.

## Dependencies

- Stack and methodology context per level (loaded from the configured stack cartridge and the L0/L1/L2/L3 rulebooks).
- Surveys the project filesystem to detect what exists.
- Reads `.ffflow/audit.yaml` if present, to know what's already been characterized.

## Hard rule

**Does not seal with any open `?` markers in `decisions.md`.** Same discipline as `plan-chat`: every phase-level decision gets resolved inline before the roadmap is handed off.

## Flow

### 0. Setup

1. Read `.ffflow/config.yaml`. If absent, prompt the user to run `/init-ffflow` first and stop.
2. Resolve the vision input:
   - If `--vision-doc <path>` given, read that file.
   - Else, look for `project.md`, `VISION.md`, `ROADMAP.md`, then `README.md` in repo root. If found, ask: "use `<path>` as the vision?" If user confirms, read it.
   - Else, ask the user for free-form vision input. Paste, or describe in chat.
3. Ask for a slug (e.g. `mvp`, `oauth-rollout`, `multi-tenant`).
4. Create `<plan-dir>/`. If one already exists for this slug, offer to resume rather than overwrite.
5. Write a skeleton `roadmap.md` with the section headings and the status header recorded at the top. The status header is composed from `.ffflow/config.yaml`:
   - **Single-stack project**: `Level: <L>, Stack: <stack>`.
   - **Polyglot project**: `Level: <L> (<subproject>: <override>, ...)` for any subproject that has a `level_override` differing from the project-level `level`. Example: `Level: L3 (Rust subproject overridden to L2)`. Compose from config — don't ask the user to write it manually.
6. Write `metadata.json` with `phase: roadmap-incomplete`.

### 1. Survey

Internal-only. Determine the project's starting state:

- Is this **greenfield** (empty repo / `project.md` + maybe README + nothing else)?
- Or **brownfield** (existing code)?
  - If brownfield, what's already spec'd? Read `.ffflow/audit.yaml auditors.spec.files`.
  - What modules / bounded contexts exist? Recent commit history. Test density.
- What does the vision actually ask for? Read the vision doc carefully; identify the major capabilities described.

Report once to the user: "Greenfield project; vision asks for X, Y, Z. Surveying gave me <summary>. Ready to propose phases?"

### 2. Propose shape

Based on greenfield vs. brownfield, draft an initial phase list.

#### Greenfield default phasing

1. **Phase 1 — Foundation.** Project scaffolding (covered by `stack-init`), initial CLAUDE.md, module skeletons matching the architecture you'll need. No user-facing behavior. Success: `just check-all` passes against an empty domain.
2. **Phase 2 — Smallest end-to-end slice.** One bounded context, one happy-path scenario, real user value (however tiny). Proves the architecture and the loop.
3. **Phase 3+ — Expansion in dependency order.** Each phase adds capability that builds on prior phases. Independent shippability: any phase, once merged, leaves the system in a usable state.

Each phase is one of these kinds (record per-phase in the roadmap):

| Kind | Handed off to | When |
|---|---|---|
| `design-slice` | `/plan-chat` | Single chess move or small cluster |
| `characterize` | `/characterize` | Phase needs spec extraction from existing code (brownfield) |
| `cleanup` | `/audit --plan` | Phase is drift remediation |
| `roadmap` | `/plan-roadmap --phase <N>` | Phase itself is too large; recurse |

#### Brownfield default phasing

1. **Survey the touched surface.** Whatever modules / contexts the vision will reach — list them.
2. **Phase 1 — Characterize the touched surface** (if any of it lacks specs). Kind: `characterize`. Per-module within that surface.
3. **Phase 2+ — Build phases** on the characterized base. Kind: `design-slice` each.
4. **Final phase (optional) — Deprecation / cleanup** of any pre-existing behavior the vision replaces. Kind: `cleanup` or `design-slice`.

Per-phase content:

```markdown
### Phase 2 — Core domain (the smallest end-to-end slice)
**Kind:** design-slice
**Scope:** the `pricing` bounded context, one happy-path scenario (calculate base price).
**Out of scope:** discount logic (Phase 4), tax (Phase 5), persistence (Phase 3).
**Success:** a user can request a base price for a configured product via the CLI; spec entry in `docs/specs/pricing.md` covers the happy path.
**Depends on:** Phase 1.
**Estimated tasks:** ~4 (one per spec scenario + one for the CLI wiring).
```

Present the draft phase list. Iterate with the user. Resolve `?`-marked decisions inline (same discipline as `plan-chat`).

### 3. Walk decisions

For each phase-level decision marker in `decisions.md`:

1. Restate the question.
2. Present 2–3 alternatives with concrete tradeoffs.
3. Name a recommendation.
4. Confirm with user; record rejected alternatives.

Examples of phase-level decisions:
- Order: does auth ship before or after the data-import phase?
- Scope: does Phase 2's end-to-end slice include the UI, or is the UI a separate Phase 3?
- Architecture: are we picking hexagonal at L1 (engages `audit-architecture`), or staying L0?
- Capture backend: stay on the configured one, or does this roadmap warrant a switch (rare)?

Don't seal with any open `?`.

### 4. Confirm shippability and dependencies

For each phase, double-check:

- **Independent shippability:** could this phase merge alone and leave the system usable? If no, it's not a phase boundary — merge it into the next phase or rethink.
- **Dependency declared:** which prior phases must complete first? Explicit field.
- **Success criterion concrete:** "a user can <X>" or "the test suite covers <Y> behaviors" — not "we have made progress on Z."

Iterate until each phase passes the check.

### 5. Write phase placeholders

For each phase, write `<plan-dir>/phases/phase-N.md`:

```markdown
# Phase N: <title>

**Kind:** <design-slice | characterize | cleanup | roadmap>
**Status:** not-started
**Roadmap:** <plan-dir>/roadmap.md

<copied from the roadmap entry — scope, out-of-scope, success, dependencies, estimated tasks>

## Handoff
When ready to execute this phase:
  /plan-chat            # for design-slice
  /characterize <target>  # for characterize
  /audit --plan         # for cleanup
  /plan-roadmap --phase N  # for roadmap (recursive)

The handoff skill will read this file as its starting point.
```

These files are what tier-2 sessions consume. They keep the roadmap context attached without forcing the user to recite it.

### 6. Seal

Roadmap is sealed when:

- Every `?` in `decisions.md` is resolved.
- Every phase passes the shippability + dependency check.
- User confirms "ready to start phase 1."

**Before writing `roadmap-complete` to `metadata.json`, perform a self-check.** Don't rely on the user (or the agent) to have manually tracked this:

1. **Scan `decisions.md` for any line starting with `?`** (including `? (deferred):`). If any found, refuse to seal. Print the unresolved questions verbatim:
   ```
   Cannot seal: 2 open decisions remain in decisions.md:
     ? Should auth ship before or after data-import?
     ? (deferred): Stack choice for the worker subproject

   Resolve each (step 3 of this skill) before sealing.
   ```
   Return to step 3.

2. **Scan each `phases/phase-N.md` for required fields** (`Kind:`, `Scope:`, `Success:`, `Depends on:`). If any phase is missing a field, refuse to seal and list which.

3. **Confirm with the user** one last time: "Ready to seal?" — only after both scans pass.

Only after all three checks pass, update `metadata.json`:
```json
{
  "phase": "roadmap-complete",
  "phases_total": 5,
  "phases_complete": 0,
  "next_phase": 1
}
```

The self-check makes the discipline stick across sessions. A user re-running mid-flow can't accidentally short-circuit to `roadmap-complete`.

Print:
```
✓ Roadmap sealed: <N> phases, slug=<slug>.
  Phase 1: <title> (<kind>)
    → /plan-chat   (or /characterize, or /audit --plan, or /plan-roadmap --phase 1)
  Phase 2: <title> (<kind>)  — blocked by Phase 1
  ...

Roadmap: <plan-dir>/roadmap.md
Next: invoke the handoff skill for Phase 1.
```

## Recursion

`/plan-roadmap --phase <N>` opens an existing roadmap, reads `phases/phase-N.md`, and produces a sub-roadmap *for that phase*. The sub-roadmap is its own `<plan-dir>` (slug-suffixed: `<parent-slug>-phase-N`) but its `metadata.json` records the parent.

When a recursive sub-roadmap is captured via `plan-capture`, its artifacts land under `docs/roadmap/<parent-slug>/phases/phase-N/sub-roadmap/` in the repo — nested directory under the parent's phase placeholder. Bidirectional traceability preserved.

Use recursion only when a phase is genuinely too large for a single `/plan-chat` — usually meaning `plan-chat` would produce > 8 tasks.

**Two-level ceiling (soft refuse).** Recursing past two levels deep — i.e., a sub-roadmap that itself contains a phase that wants to be a sub-roadmap — is refused by default. The error names the structural problem:

```
Refusing third-level recursion.

You're recursing into <slug>/phase-3/sub-roadmap/phase-2, which would produce
a third-level sub-roadmap at docs/roadmap/<parent>/phases/phase-3/sub-roadmap/phases/phase-2/sub-roadmap/.

This usually signals the top-level roadmap was too ambitious. Options:
  1. Re-scope the top-level — split into two top-level roadmaps.
  2. Flatten — turn the third-level work into peer phases of the second-level roadmap.
  3. Use --force if you genuinely want to proceed anyway.
```

`--force` overrides. The escape hatch exists; the default discourages.

## Artifact contract for phase placeholders

`phases/phase-N.md` has a **two-write lifecycle**:

1. **Written at roadmap-seal time** by this skill. Contains scope, success criteria, dependencies, kind, estimated tasks.
2. **Updated once after capture** by `plan-capture`, which appends a `## Captured tasks` section listing the created issues.

These are the only two writes. The phase placeholder is not freely editable. If a user wants to change a phase's scope after capture, they re-run `/plan-roadmap` (which produces an updated phase entry) and then re-run `/plan-capture` to re-sync.

This contract matters because the file is committed to `docs/roadmap/<slug>/phases/phase-N.md` in the repo. Treating it as freely-editable creates merge surprises and breaks traceability.

## Resume

Re-running `/plan-roadmap` against an existing slug:
1. Read `metadata.json`.
2. If `roadmap-complete`: ask "this roadmap is sealed; do you want to (a) view status, (b) extend with new phases, (c) start a new roadmap?"
3. If `roadmap-incomplete`: read `roadmap.md` and `decisions.md`; pick up at the latest unresolved decision or unfinished phase block.

## Progress tracking

`plan-status` (which scans `/tmp/ffflow-plans/<project-hash>/*/`) shows roadmap progress alongside in-flight plans:

```
<plan-dir>/mvp/
  Phase: roadmap-complete
  Roadmap: 5 phases (1 complete, 1 in-progress, 3 pending)
  Next: /plan-chat (Phase 2 handoff)
```

When a phase's handoff plan reaches `phase: captured`, the roadmap entry for that phase advances to `complete`. When all phases complete, the roadmap moves to `roadmap-shipped` and can be archived.

## Greenfield project.md flow (worked example)

```
cd ~/new-project && git init
# project.md exists

/adopt-ffflow
# → init-ffflow writes config; stack-init scaffolds. Hands off to /plan-roadmap.

/plan-roadmap
# "Use project.md as vision? (y/n)" → y
# Reads project.md, surveys empty repo, proposes:
#   Phase 1 — Foundation (kind: design-slice; mostly verifying stack-init output)
#   Phase 2 — Core domain: <smallest slice from the vision> (kind: design-slice)
#   Phase 3 — <second capability> (depends on 2)
#   Phase 4 — <third capability> (depends on 2)
#   Phase 5 — <UI layer> (depends on 2, 3, 4)
# Walks decisions: "Are 3 and 4 actually independent, or does 4 need 3?"
# User answers; rejected alternatives recorded.
# Seals.

/plan-chat
# Phase 1 handoff. Reads <plan-dir>/phases/phase-1.md.
# Designs the foundation slice. Seals.

/plan-breakdown → /plan-capture → /work-issue <first issue>
```

## Brownfield "add OAuth to this app" flow (worked example)

```
cd ~/existing-app
# .ffflow/config.yaml exists from earlier adoption

/plan-roadmap
# "What's the vision?" → "Add OAuth login alongside existing password auth.
#                       Eventually deprecate passwords."
# Surveys: scans .ffflow/audit.yaml — auth surface is unspec'd.
# Proposes:
#   Phase 1 — Characterize auth surface (kind: characterize, target: src/auth/)
#   Phase 2 — Refactor session storage (kind: design-slice, depends on 1)
#   Phase 3 — Add OAuth provider integration (kind: design-slice, depends on 2)
#   Phase 4 — Add OAuth flow to UI (kind: design-slice, depends on 3)
#   Phase 5 — Deprecate password auth (kind: design-slice, depends on 4; flag for stakeholder review)
# Seals.

/characterize src/auth/
# Phase 1 handoff. Extracts specs, queues backfill tasks.
```

## Friction addressed

- Vision docs that never become a plan because "what's the first slice?" is paralyzing.
- Brownfield features that fail because the team didn't characterize first.
- Roadmaps that live in slide decks instead of versioned artifacts.
- Repeated "what's the order, what blocks what?" conversations that go unrecorded.
- The current handoff cliff where `adopt-ffflow` ends at "next: /plan-chat" but the user doesn't know what to ask `/plan-chat` to do.

## Anti-patterns

- Phases that aren't independently shippable. "Phase 4 makes Phase 3 actually useful" means 3 and 4 are one phase.
- Recursion more than two levels deep. The original roadmap was too big — re-scope.
- Roadmap as wish list. Every phase has a `Success:` line that names a verifiable outcome.
- Skipping the recursive check. A phase that produces > 8 tasks at `plan-chat` time was a sub-roadmap in disguise.
- Letting roadmap drift. When reality diverges from the roadmap, update `roadmap.md` — don't keep executing against a stale plan. The roadmap is a versioned artifact, not a contract.
- Detailed task design. That's `plan-chat`'s job. Roadmap operates one level up.

## Quality checks before sealing

- [ ] Vision summary recorded in `roadmap.md`, confirmed by user.
- [ ] Each phase has `Kind:`, `Scope:`, `Out of scope:`, `Success:`, `Depends on:`, `Estimated tasks:`.
- [ ] `decisions.md` has zero open `?` markers (including deferred).
- [ ] Each phase passes the independent-shippability check.
- [ ] Phase placeholders written to `<plan-dir>/phases/phase-N.md`.
- [ ] `metadata.json` shows `roadmap-complete`.
