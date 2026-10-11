# Changelog: ppp

All notable changes to the `ppp` plugin. Versions track `ppp/.claude-plugin/plugin.json`; rules in the root [CLAUDE.md](../CLAUDE.md#how-we-version).

---

## [0.1.0] — 2026-10-11

### Added
- **The process kit.** `process.md` (seats, the bundle, finding a bundle, the PRD rules, parking lot, turns, data requests, rounds and convergence, retro, split signals, the evidence rule, exit); `media.md` (what a medium must do, bringing your own medium document, and the repo + draft-PR worked example); templates for the PRD, parking lot, memo (with **Cut** and **Key decisions kept** lines), evidence, round summary, `requests.md`, `state.json` and `medium.md`; seat briefs for builder, product and analyst.
- **Seven skills:** `/ppp:prd-start`, `/ppp:prd-turn`, `/ppp:prd-check`, `/ppp:prd-retro`, `/ppp:prd-data`, `/ppp:prd-split`, `/ppp:prd-status`. Every skill after `prd-start` locates the bundle and follows its `medium.md`; a bundle without one gets one written, never a failure.
- **`check.py`** as bundled tooling (stdlib only, Python 3.9+): HEADINGS, PROVISIONAL / `--ratify` (both `[provisional]` and `[provisional: <reason>]`), the CEILING, CEILING-NEAR, DECISIONS-AT-LIMIT, MEMO and PARKING-LONG warnings, `--json`, per-portfolio `limits.json`, and exit code 2 for input errors. Ships with fixtures and a `unittest` suite (`python3 -m unittest discover -s ppp/tests`).
- **The design PRD bundle** at `docs/prds/ppp/`, which passes its own check.
