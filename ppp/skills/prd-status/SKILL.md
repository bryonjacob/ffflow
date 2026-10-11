---
name: prd-status
description: Report where a PPP PRD, or the whole portfolio, stands — medium, round, next seat, open questions, provisional values, parking lot, splits and sign-offs. Use to orient, or before a planning hand-off.
---

# prd-status

## Plan Mode

This skill does NOT invoke Plan Mode. It only reads and reports.

## Steps

0. Locate the bundle (`${CLAUDE_PLUGIN_ROOT}/process.md` §Finding a bundle) and read `medium.md`; do every read below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue.
1. Report one PRD, or the portfolio, as below.

## One PRD

Medium (Reference from `medium.md`) · round, round cap and next seat · status (drafting / converged / ratified) · words and growth per turn · open / answered / deferred / dropped · `[provisional]` count · facilitator findings not yet answered, by owner seat · parking lot by kind · split proposals and who has accepted · data requests open · sign-off per seat (`yes` / `no` / not yet) · the last round summary's "next round must".

Get the metrics from `python3 "${CLAUDE_PLUGIN_ROOT}/skills/prd-check/check.py" <local bundle> --json` (`check.py` sits beside prd-check's SKILL.md), and growth per turn from the versions `medium.md` says.

## Portfolio (every bundle sharing one `_shared/`)

One row per PRD with the above, plus: every `split` link (parent → child), every `other-prd` entry routed to a PRD that doesn't exist yet (a gap), and every `planning` entry across all PRDs — that list is the input to the planning step.

## Exit check

A PRD is ready for planning when converged. Say whether it is only converged (provisional values remain, or a seat hasn't signed off) or ratified and committed. Planning is outside PPP; if the user works with fff, `/fff:plan-roadmap` or `/fff:plan-chat` takes it from here.
