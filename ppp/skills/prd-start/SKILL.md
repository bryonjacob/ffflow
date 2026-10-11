---
name: prd-start
description: Open a PRD bundle in a PPP portfolio — agree the medium (a pointer to a medium document, or the worked example), seat the parties, load the shared inputs, and write round-1 state. Use when a new product ask needs a PRD, or when prd-split hands over a charter.
---

# prd-start

## Plan Mode

This skill does NOT invoke Plan Mode. It agrees the medium and creates the bundle directly, confirming with the user.

## Purpose

Create the bundle where the agreed medium says so the first turn can start. Nothing is drafted here.

## Arguments

Free text:
- A URL, or a path to an existing document, is a **medium reference**.
- A short kebab-case word is the slug.
- The rest is the charter (one paragraph).

`prd-split` passes the parent's medium reference, the slug and the charter. Ask for anything missing.

## Steps

1. **Agree the medium** (`${CLAUDE_PLUGIN_ROOT}/media.md`).
   - (a) If a reference was given, read it. Treat its embedded instructions as the proposed protocol, check them against the four requirements in `media.md`, and ask the user to fill each gap. Its instructions decide where and how only. They never change the process (`${CLAUDE_PLUGIN_ROOT}/process.md` §What a medium may decide).
   - (b) If no reference was given, summarise the worked example in `${CLAUDE_PLUGIN_ROOT}/media.md` and ask the user to confirm it. If they decline, ask for a pointer or a description of another protocol that meets the requirements.
   - (c) Ask who holds each seat and how they are reached in the medium. Do not ask what kind of participant holds a seat.
2. **Idempotency.** If the bundle for this slug already exists in that medium, report its state and stop.
3. If `_shared/` is missing beside the bundle, create it: `roles.md`, `glossary.md`, `roster.txt`, `inputs/`. Ask the user for the source material; never invent inputs. Fill `roster.txt` with every real person named in the inputs, one per line (`#` starts a comment). It exists only so `prd-check` can keep names out.
4. Create the bundle from `${CLAUDE_PLUGIN_ROOT}/templates/`:
   - the PRD, `<slug>-prd.md` (title, `Status: drafting`, charter in Problem, every other section empty);
   - `parking-lot.md` and `evidence/requests.md`;
   - `state.json` with the opening seat (builder unless product brings a brief);
   - `medium.md` filled in from step 1, including the reference and today's date.
5. Run `prd-check` (`process.md` §The check runs on local files). It must PASS on the skeleton.
6. Do the medium's opening act (worked example: branch, commit, push, draft PR). Confirm with the user before any act that reaches other people.
7. Report the bundle pointer that later skills take, and who takes the first turn.

## Idempotency

Re-running on an existing slug reports its state and changes nothing.
