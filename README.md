# FFFlow Plugin for Claude Code

**Plan, work, audit — at the level of rigor your project actually needs.**

FFFlow is a complete development lifecycle in a single Claude Code plugin. It scales from informal prose specs (L0) to full spec-driven development with mutation testing and RID traceability (L3). Same workflow at every level; what changes is the formality of the artifacts and strictness of the gates.

The plugin's invocation prefix is `/fff:` — short, distinctive, won't collide.

## Install

```bash
/plugin marketplace add /path/to/ffflow-plugin
/plugin install fff@ffflow
```

After install, every command is namespaced under `/fff:` (e.g., `/fff:plan-chat`, `/fff:work-issue`).

## The shape

Three artifacts. Three roles. Three locations.

- **Spec** (present tense, evergreen) — your codebase's behavioral contract. Lives in `docs/specs/`, `specs/`, or per-module CLAUDE.md.
- **Plan** (future tense, transient) — the path from current spec to next spec. Lives in `/tmp/ffflow-plans/<project-hash>/<slug>/`, never in the project tree.
- **Issues** (imperative, transactional) — the chess moves. Lives in your issue tracker.

## Workflows

**Bootstrap a new project (from `project.md`, README, or just an idea):**
```
/fff:adopt-ffflow   Detects greenfield vs. brownfield. Runs init + stack setup,
                    then hands off to /fff:plan-roadmap.
/fff:plan-roadmap   Reads your vision; produces ordered phases with dependencies.
                    Per phase: design-slice (→ plan-chat), characterize, cleanup,
                    or recursive sub-roadmap.
```

**Steady-state feature work (after bootstrap):**
```
/fff:plan-chat        Design one slice. Open decisions resolved inline before sealing.
/fff:plan-breakdown   Cut the plan into 3–8 independently shippable chess moves.
/fff:plan-capture     Write the chess moves to your issue tracker.
/fff:work-issue       Execute one chess move end-to-end: red → green → spec → PR.
/fff:work-fanout      Or run several in parallel across worktrees (one PR per issue).
/fff:work-epic        Or run an epic's issues sequentially into one PR.
/fff:audit            Periodically: check that specs, CLAUDE.md, tests still match reality.
```

**Maintenance loop:**
```
/fff:audit            Find drift. Find gaps.
/fff:audit --plan     Convert findings into a plan. Then breakdown → capture → work.
```

## Two-tier planning

- **Tier 1** — `/fff:plan-roadmap` (phase-level). Used for new projects, big features, or new directions.
- **Tier 2** — three entries, each handling one phase:
  - `/fff:plan-chat` — design a slice.
  - `/fff:characterize` — extract specs from existing code.
  - `/fff:audit --plan` — convert drift into a plan.

All four converge on `plan-breakdown → plan-capture → work-*`.

Single-slice changes skip tier 1; bug fixes go through `plan-chat` directly.

## The L0–L3 dial

Pick the level your project needs. You can change levels later.

| Level | Spec format | Tests | Gates |
|---|---|---|---|
| **L0** | Informal prose | Standard unit/integration | Lint + tests pass |
| **L1** | Structured prose, hexagonal layering | + defect-driven spec entries | + CLAUDE.md audit |
| **L2** | Gherkin 6 scenarios | + spec-first TDD | + spec audit, contract enforcement |
| **L3** | Gherkin + RIDs + property-based | + mutation testing | + four quality gates, RID audit |

No config = L0. Declare your level in `.ffflow/config.yaml` to enable more.

## Cartridge architecture

Several skills carry their family of variants as on-demand cartridges, keeping the LLM's skill index uncluttered:

- `/fff:plan-capture` — cartridges for `github-issues` (default), `linear`, `jira`, `markdown`.
- `/fff:stack` — cartridges for `python`, `typescript`, `java`, `rust`, `polyglot`.
- `/fff:justfile` — Tier 1–4 pattern cartridges (quality, security, advanced, polyglot).
- `/fff:audit` — cartridges for `claude-md`, `spec`, `char-tests`, `architecture`, `refactor`, `tech-debt`, `rid`.

Configure once in `.ffflow/config.yaml`; the right cartridge loads when needed.

## What FFFlow doesn't do

- It doesn't lock you to one stack. Pluggable via cartridges; override any tool via `.ffflow/stack.yaml`.
- It doesn't lock you to GitHub. Capture backends are pluggable (Linear, Jira, markdown).
- It doesn't replace your tests. Spec tests are additive — both unit and spec tests have independent coverage thresholds.
- It doesn't force L3 on you. L0 is a valid forever-state for projects that want lightweight discipline.

## Documentation

- [Build spec & architecture](plugin/docs/architecture.md) — what the plugin is and why
- [Levels explained](plugin/docs/levels.md) — the L0–L3 dial in detail
- [Workflows](plugin/docs/workflows.md) — the lifecycle flows
- [Audit subsystem](plugin/docs/audit.md) — the keep-honest layer

## Status

Active development. See [`plugin/CLAUDE.md`](plugin/CLAUDE.md) for the build phase status.

## License

Apache License 2.0 — see [LICENSE](LICENSE). Copyright 2026 Bryon Jacob.

Contributions welcome. New stack cartridges (Go, Elixir, …), capture backends, and audit cartridges are the easiest ways to extend FFFlow without touching the core.
