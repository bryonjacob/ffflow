# Changelog: ppp

All notable changes to the `ppp` plugin. Versions track `ppp/.claude-plugin/plugin.json`; rules in the root [CLAUDE.md](../CLAUDE.md#how-we-version).

---

## [0.2.0] — 2026-10-11

**Breaking.** The convergence rule, sign-off values and question resolutions change. A bundle already in flight must replace any conditional sign-off (the removed third value, in `state.json` and memos) with `yes` or `no`, turning each condition into a change made in a turn, and rewrite every answered question's Resolution as a pointer (`→ R-n` or `→ §n`, ≤ 15 words) with the answer moved into the PRD. Calls to `check.py --closing` become `--agree` (agreement turn) or `--ratify`.

### Changed
- **Convergence is a no-edit agreement turn (breaking).** Handing the PRD over means "I'd sign this exactly as it stands, if you will"; a seat agrees by handing it back unchanged (trailing whitespace and line endings aside), with `agreed` in its memo. Converged = an agreement turn, zero open questions, a passing check and no unanswered facilitator findings. Ratified = converged, nothing provisional, and the medium's commit act (worked example: PR marked ready for review, every seat approves the unchanged PRD, then merge).
- **Sign-off is `yes` or `no` (breaking).** The conditional third value is gone everywhere: a condition is a change, made in another turn.
- **No closing round (breaking).** The builder-proposes / product-closes closing round and its special growth rule are removed; the normal growth rule holds in every round. The round cap (`round_cap`, default 3) is now an escalation trigger: the portfolio lead decides split, park, or another round.
- **Resolutions are pointers (breaking).** An answered question's Resolution only names where the answer lives (`→ R-15`, `→ §6 Turnaround`), ≤ 15 words.
- **`check.py --closing` is replaced by `--agree`** (fails `AGREE` if the PRD differs from `--prev`; implies the no-open-questions check). The open-questions failure is now `OPEN-QUESTIONS` (was `CLOSING`), raised by `--agree` and `--ratify`.
- **Status lives only in `state.json`, set only by `prd-retro`.** The PRD template has no Status line; `prd-turn` never changes status.
- **Splits are proposed in an ordinary turn:** a `split` parking entry plus `Split P-n: accept` in the memo; both seats' acceptances are `prd-split`'s confirmation. No special split mode.
- **Round 1: data before rulings.** Each round-1 memo lists data requests filed or says `none needed` and why.
- **`prd-start` never re-asks** for a medium, slug, charter or seat holders given in its arguments; outward-facing acts are still confirmed unless the user already said to do them.

### Added
- **Facilitator findings.** The round summary has a Facilitator findings section (`F-n`, numbered across the bundle, never reused, with an owner seat); retro-surfaced assumptions become findings instead of PRD edits. The memo has a **Findings** line answering each by ID (`accepted` / `rejected`); `check.py --summary <file> --seat <seat>` fails `FINDINGS` when one is unanswered.
- **Provisional cleared.** Memo lines justifying each cleared `[provisional]` value with an evidence link or a role from `_shared/roles.md`; `check.py` fails `PROVISIONAL-CLEARED` when the provisional count drops without them (warns if `roles.md` is missing).
- **`_shared/facts.md`** (`templates/facts.md`), the portfolio's one fact sheet, created by `prd-start` and kept by the analyst through `prd-data`, including which source wins when sources disagree.
- **New check codes:** `QUESTIONS-REMOVED` (a `Q-n` in `--prev` is gone), `QUESTIONS` pointer failures (no reference, dangling R-id or section, over 15 words), and the `XL-AT-LIMIT` warning. Fixtures for each.

### Fixed
- `--prev` without `--memo` is an input error (exit 2) instead of a misleading GROWTH failure; skills name exactly which memo and summary to pass.
- Closed question rows stay and IDs are never reused (process rule plus `QUESTIONS-REMOVED`).
- Retro answer length (≤ 150 words per answer) counts only the answer, not headings or question labels.
- Analyst data requests may run in parallel with the retro.
- `prd-split` handles a parent that is still an empty skeleton: the child starts from the charter alone, and the parent still gets its Non-goals pointer.

## [0.1.0] — 2026-10-11

### Added
- **The process kit.** `process.md` (seats, the bundle, finding a bundle, the PRD rules, parking lot, turns, data requests, rounds and convergence, retro, split signals, the evidence rule, exit); `media.md` (what a medium must do, bringing your own medium document, and the repo + draft-PR worked example); templates for the PRD, parking lot, memo (with **Cut** and **Key decisions kept** lines), evidence, round summary, `requests.md`, `state.json` and `medium.md`; seat briefs for builder, product and analyst.
- **Seven skills:** `/ppp:prd-start`, `/ppp:prd-turn`, `/ppp:prd-check`, `/ppp:prd-retro`, `/ppp:prd-data`, `/ppp:prd-split`, `/ppp:prd-status`. Every skill after `prd-start` locates the bundle and follows its `medium.md`; a bundle without one gets one written, never a failure.
- **`check.py`** as bundled tooling (stdlib only, Python 3.9+): HEADINGS, PROVISIONAL / `--ratify` (both `[provisional]` and `[provisional: <reason>]`), the CEILING, CEILING-NEAR, DECISIONS-AT-LIMIT, MEMO and PARKING-LONG warnings, `--json`, per-portfolio `limits.json`, and exit code 2 for input errors. Ships with fixtures and a `unittest` suite (`python3 -m unittest discover -s ppp/tests`).
- **The design PRD bundle** at `docs/prds/ppp/`, which passes its own check.
