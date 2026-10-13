---
name: prd-data
description: Fill the PPP analyst seat — answer the open data requests in a PRD bundle with evidence files, neutrally, and keep the portfolio's facts.md. Use between turns, or while a retro runs, whenever evidence/requests.md has open requests.
---

# prd-data

## Plan Mode

This skill does NOT invoke Plan Mode. It writes evidence files directly.

## Purpose

Turn "I think" into "the data says". Evidence is what moves positions; this seat exists so either side can get it, including a seat with no access to the code or systems.

## Steps

0. Locate the bundle (`${CLAUDE_PLUGIN_ROOT}/process.md` §Finding a bundle) and read `medium.md`; do every read, write and hand-off below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue.
1. Read `evidence/requests.md`. For each request with status `open`, in order:
2. Answer exactly the question asked. Use the sources the bundle points to (repo, issue tracker, analytics, documents in `_shared/inputs/`). Read-only: never change a system to get a number.
3. Write `evidence/<nn>-<topic>.md` from `${CLAUDE_PLUGIN_ROOT}/templates/evidence.md`: question · method · result · as-of · caveats. Method must be repeatable by someone else.
4. Update the request's Status: `answered` with a link to the evidence file in Answer, or `cannot-answer` with what it would take.
5. **Keep `_shared/facts.md`** (from `${CLAUDE_PLUGIN_ROOT}/templates/facts.md` if missing). A fact the answer settles goes in as one row: value, source, as-of. When sources disagree, record which wins and why (the newer read, the system of record, the narrower method), and link the evidence file. Each fact has one row; correct it in place rather than adding a second.
6. Write back and announce the answers as `medium.md` says. This can run while `prd-retro` does.

## Rules

No recommendation, no position, no adjectives that argue ("only", "just", "alarming"). Counts, not conclusions. If the question is loaded, answer it and note the framing in Caveats.
