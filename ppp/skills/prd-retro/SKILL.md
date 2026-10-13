---
name: prd-retro
description: Close a PPP round — put the five retro questions to each seat on the record, tidy the parking lot, write the round summary with facilitator findings, and set status; when a round ends in an agreement turn, mark converged, collect yes/no sign-offs and ratify. Use when both seats have taken their turn in a round.
---

# prd-retro

## Plan Mode

This skill does NOT invoke Plan Mode. It collects answers and writes the round summary directly.

## Rule

The facilitator never edits the PRD. What it notices goes in the round summary as findings. It is the only skill that sets `status` in `state.json`.

## Steps

0. Locate the bundle (`${CLAUDE_PLUGIN_ROOT}/process.md` §Finding a bundle) and read `medium.md`; do every read, write and hand-off below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue. Open data requests can be answered with `/ppp:prd-data` while this runs.
1. Ask each seat holder, ≤ 150 words per answer: in the session if they are here; otherwise through the medium's hand-off, resuming when answers are in. Count only the words of each answer; headings and the question labels don't count. Over the limit: trim it in the summary and say so.
   1. What changed your mind this round, and on what evidence?
   2. What worries you most in the PRD as it stands?
   3. What would you give up to close faster?
   4. What are you assuming that isn't written down?
   5. Did anything you parked deserve to be its own PRD?
2. Run `prd-check` (`process.md` §The check runs on local files); read the metrics (words, growth, questions, provisional values, signals).
3. **Tidy the parking lot.** Merge duplicate entries. Mark each `other-prd` and `split` entry that has been routed with where it went (`routed to <PRD or bundle>` in its Why cell), so the lot reads as open thoughts only. Keep each entry to one line (about 30 words). Never delete a thought.
4. **Findings.** Every unwritten assumption (Q4), unanswered question or gap that matters becomes a finding in the summary: the next free `F-n` across the whole bundle (never reuse one), the owning seat, one line. Never write it into the PRD. If Q5 says yes, write a finding to that seat suggesting it propose the split in its next turn.
5. Write `rounds/<n>-summary.md` from `${CLAUDE_PLUGIN_ROOT}/templates/round-summary.md`, ≤ 300 words plus the answers verbatim. Neutral voice. It is the brief for the next round, so end with what the next round must do.
6. **Convergence** (`process.md` §Rounds and convergence). If the round's last turn was an agreement turn:
   - (a) Check every condition: the agreement memo's check passed with `--agree`; zero open questions; every earlier finding answered by ID in its owner's memo. New findings from step 4: one that matters is a named blocker, so ask the portfolio lead whether to allow another round; park the rest (`idea` or `planning`) and say so in the summary.
   - (b) All hold: set `status` to `converged` and do the medium's sign-off act.
   - (c) Record each seat's sign-off (`yes` or `no`) in `state.json` as it arrives. A `no` is a change: set `status` back to `drafting`, clear both sign-offs, and hand that seat a normal turn.
   - (d) Every seat `yes` and the check passes with `--ratify`: set `ratified` and do the medium's commit act, confirming with the user first unless they already said to do it.

   Re-running after sign-offs arrive completes (c) and (d).
7. **Round cap.** If this round reaches `round_cap` without converging, ask the portfolio lead to decide: split (`/ppp:prd-split`), park the PRD, or allow another round (raise `round_cap` by one). Record the decision in the summary.
8. Advance `state.json` (round, `next`, `status`), write everything back, and hand off as `medium.md` says.
