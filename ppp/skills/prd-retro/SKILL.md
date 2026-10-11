---
name: prd-retro
description: Close a PPP round — put the five retro questions to each seat on the record, tidy the parking lot, then write the round summary every seat reads next; on the closing round, mark converged, collect sign-offs and ratify. Use when both seats have taken their turn in a round.
---

# prd-retro

## Plan Mode

This skill does NOT invoke Plan Mode. It collects answers and writes the round summary directly.

## Steps

0. Locate the bundle (`${CLAUDE_PLUGIN_ROOT}/process.md` §Finding a bundle) and read `medium.md`; do every read, write and hand-off below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue.
1. Ask each seat holder, ≤ 150 words each: in the session if they are here; otherwise through the medium's hand-off, resuming when answers are in.
   1. What changed your mind this round, and on what evidence?
   2. What worries you most in the PRD as it stands?
   3. What would you give up to close faster?
   4. What are you assuming that isn't written down?
   5. Did anything you parked deserve to be its own PRD?
2. Run `prd-check` (`process.md` §The check runs on local files); read the metrics (words, growth, questions, provisional values, signals).
3. **Tidy the parking lot.** Merge duplicate entries. Mark each `other-prd` and `split` entry that has been routed with where it went (`routed to <PRD or bundle>` in its Why cell), so the lot reads as open thoughts only. Keep each entry to one line (about 30 words). Never delete a thought.
4. Write `rounds/<n>-summary.md` from `${CLAUDE_PLUGIN_ROOT}/templates/round-summary.md`, ≤ 300 words plus the answers verbatim. Neutral voice. It is the brief for the next round, so end with what the next round must do.
5. If an answer to Q4 names an unwritten assumption that matters, add it as a question for the owning seat. If Q5 says yes, propose `prd-split`.
6. If this was the closing round:
   - (a) Run the check with `--closing`. If it passes, set status `converged`, update the PRD status line, and do the medium's converged act.
   - (b) Collect each seat's sign-off as `medium.md` says, and record it in `state.json`.
   - (c) When every seat has signed `yes` or `yes-with-conditions` and the check passes with `--ratify`, set `ratified`, update the PRD status line, and do the medium's commit act, confirming with the user first.

   Re-running after sign-offs arrive completes (b) and (c).
7. Advance `state.json` to the next round or to the exit, write everything back, and hand off as `medium.md` says.
