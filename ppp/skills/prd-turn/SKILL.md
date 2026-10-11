---
name: prd-turn
description: Take one seat's turn in a PPP ping-pong — respond to the other seat, revise the PRD in place, park what doesn't belong, file data requests, write the memo, and pass prd-check. Use for every builder or product turn.
---

# prd-turn

## Plan Mode

This skill does NOT invoke Plan Mode. A turn is written directly into the bundle and lands only when prd-check passes.

## Inputs

`--seat builder|product` and the bundle pointer. Read `medium.md`, then `state.json`; refuse if it isn't this seat's turn.

## Read first (everything; there are no private files)

`_shared/` · the PRD (`<slug>-prd.md`) · `parking-lot.md` · `evidence/` · every `rounds/*-summary.md` · the last two memos · `${CLAUDE_PLUGIN_ROOT}/seats/<seat>.md` · `${CLAUDE_PLUGIN_ROOT}/process.md`. Round 1 opening: draft from `_shared/inputs/`.

## Do

0. Locate the bundle (`process.md` §Finding a bundle) and read `medium.md`; do every read, write and hand-off below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue.
1. **Respond.** For each point in the other seat's last memo: accept (say why), or push back with evidence and exactly one alternative. Decisions inside your seat's authority (see seat brief) you make; outside it you ask.
2. **Revise the PRD in place.** Follow every rule in `${CLAUDE_PLUGIN_ROOT}/process.md` §"What goes in the PRD". Write the PRD as if it had always been right: no history, no names, no effort or schedule, sizes only in Increments, service values only in Service parameters.
3. **Trim before you add.** Before adding words, remove stale or duplicated text. Growth must be net-new information the final PRD needs. The memo's **Cut** line names the biggest thing you removed and what you would cut next to reach about 80% of the ceiling; its **Key decisions kept** line says, for each key decision, why a requirement can't carry it. Limits are ceilings, not targets.
4. **Park.** Anything that is scheduling, capacity, another PRD's concern, or a good idea for later goes to `parking-lot.md` with its kind, one line each. Parking costs nothing; never hesitate. If a thread keeps growing, park it as `split`.
5. **Ask for data** in `evidence/requests.md` (status `open`) when a position rests on a number nobody has.
6. **Questions.** Close what you can (`answered` / `deferred` with owner role and trigger / `dropped` with reason). New questions take the next free `Q-n` and the `?` marker.
7. **Memo** at `turns/<round>-<seat>.md` from `${CLAUDE_PLUGIN_ROOT}/templates/memo.md`, ≤ 500 words.
8. **Check.** Get the previous PRD version as `medium.md` §Versions says. Make a local copy if the medium isn't local (`process.md` §The check runs on local files). Run:
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/prd-check/check.py" <local bundle> --prev <previous> --memo <memo>
   ```
   Add `--closing` on the closing product turn. (`check.py` sits beside prd-check's SKILL.md.) Fix and re-run until PASS. A turn that fails does not land.
9. Update `state.json` (`next`; round complete → hand to `prd-retro`), write everything back, and hand off as `medium.md` says.

## Closing round

Builder: propose a resolution for every open question, as a yes/no list at the end of the memo.
Product: close every question. Each seat records sign-off (`yes` / `yes-with-conditions` / `no`) in the memo and in `state.json`; each condition must already exist in the PRD as a requirement or a deferred question.

## Evidence rule

Every decision cites a file in the bundle. A value with no evidence in the bundle and no authority in the inputs is written `[provisional]` or `[provisional: <reason>]` (a reason is encouraged). Never invent a person, a date, or a number presented as firm.

## Anti-patterns

Appending a diary to the PRD · re-arguing a closed question without new evidence · estimating effort in time · naming people · answering for the other seat · making the PRD longer to sound thorough.
