# PPP — plugin design notes

PPP (product ping-pong) turns a product ask into a PRD both sides can stand behind. A builder seat and a product seat take turns revising one PRD under mechanical checks; an analyst seat answers data requests neutrally; whatever doesn't belong is parked; every round ends with a retro on the record; the PRD converges when no question is open and is ratified when every seat signs off with nothing provisional left. The process is defined over text documents and is indifferent to where they live: each PRD's medium is agreed when it starts and recorded in its bundle.

## Layout

```
ppp/
├── .claude-plugin/plugin.json   the plugin manifest; the only place ppp's version lives
├── process.md                   the process contract every skill implements
├── media.md                     what a medium must do; the repo + draft-PR worked example
├── seats/                       builder, product, analyst briefs
├── templates/                   prd, parking-lot, memo, evidence, round-summary, requests, state.json, medium
├── skills/                      prd-start, prd-turn, prd-check (+ check.py), prd-retro, prd-data, prd-split, prd-status
├── tests/                       test_check.py + fixtures/
├── docs/prds/ppp/               PPP's own design bundle (dogfood)
├── CHANGELOG.md
└── CLAUDE.md                    this file
```

## Invariants

- **Seats, not people.** The process defines what a seat owns, never who holds it. No branching anywhere on what kind of participant holds a seat.
- **Rules are enforced by `check.py`, not by prose.** If a rule matters, it has a check code.
- **The medium is an agreement recorded in `medium.md`.** No product names in skill logic; medium examples live only in `media.md` prose. A medium decides where and how, never the process.
- **No dependency on fff.** fff may be mentioned only as one possible next step after convergence.
- **Bundled files are referenced via `${CLAUDE_PLUGIN_ROOT}`** (`${CLAUDE_PLUGIN_ROOT}/process.md`, `.../templates/…`, `.../skills/prd-check/check.py`).
- **Each skill has a `## Plan Mode` section** stating that it does not invoke Plan Mode, and why.
- **Skills only.** No agents, hooks or MCP servers.
- **Idempotent and resumable from state.** Every skill can be re-run; `state.json` says where things stand.

## Tests

```
python3 -m unittest discover -s ppp/tests -v
```

Run from the repo root; stdlib only. Every new check rule ships with at least one fixture that trips it and keeps `pass-good` clean. Each fixture asserts the exact set of fail and warn codes, so a fixture trips only the rule it targets.

## Design PRD

`docs/prds/ppp/` is the design document, laid out as a real bundle. It must pass its own check (`python3 skills/prd-check/check.py docs/prds/ppp` exits 0); `tests/test_check.py` enforces this.
