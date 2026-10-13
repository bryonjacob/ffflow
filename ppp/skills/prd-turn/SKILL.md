---
name: prd-turn
description: Take one seat's turn in a PPP ping-pong — respond to the other seat and the facilitator's findings, revise the PRD in place (or hand it back unchanged to agree), park what doesn't belong, file data requests, write the memo, and pass prd-check. Use for every builder or product turn.
---

# prd-turn

## Plan Mode

This skill does NOT invoke Plan Mode. A turn is written directly into the bundle and lands only when prd-check passes.

## Inputs

`--seat builder|product` and the bundle pointer. Read `medium.md`, then `state.json`; refuse if it isn't this seat's turn.

## Read first (everything; there are no private files)

`_shared/` (including `facts.md`) · the PRD (`<slug>-prd.md`) · `parking-lot.md` · `evidence/` · every `rounds/*-summary.md` · the last two memos · `${CLAUDE_PLUGIN_ROOT}/seats/<seat>.md` · `${CLAUDE_PLUGIN_ROOT}/process.md`. Round 1 opening: draft from `_shared/inputs/` and `_shared/facts.md`.

## Agree, or take a normal turn

Handing the PRD over means "I'd sign this exactly as it stands, if you will" (`process.md` §A turn). If you would sign it as you received it, take an **agreement turn**: leave the PRD untouched, answer your open findings, park or ask for data if you need to, and write a memo whose **Agreed** line says `agreed`. Otherwise take a normal turn. Wanting any change, however small, is a normal turn.

## Do

0. Locate the bundle (`process.md` §Finding a bundle) and read `medium.md`; do every read, write and hand-off below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue.
1. **Respond.** For each point in the other seat's last memo: accept (say why), or push back with evidence and exactly one alternative. Decisions inside your seat's authority (see seat brief) you make; outside it you ask.
2. **Answer findings.** In the latest round summary's Facilitator findings, every `F-n` whose owner is your seat gets a line in your memo's **Findings**: `F-n accepted` and where the PRD now covers it, or `F-n rejected` and why.
3. **Revise the PRD in place** (skip on an agreement turn). Follow every rule in `process.md` §"What goes in the PRD". Write the PRD as if it had always been right: no history, no names, no effort or schedule, sizes only in Increments, service values only in Service parameters. Cite `_shared/facts.md` or an evidence file for numbers.
4. **Trim before you add.** Before adding words, remove stale or duplicated text. Growth must be net-new information the final PRD needs, in every round. The memo's **Cut** line names the biggest thing you removed and what you would cut next to reach about 80% of the ceiling; its **Key decisions kept** line says, for each key decision, why a requirement can't carry it. Limits are ceilings, not targets.
5. **Park.** Anything that is scheduling, capacity, another PRD's concern, or a good idea for later goes to `parking-lot.md` with its kind, one line each. Parking costs nothing; never hesitate. If a thread keeps growing, propose a split: park it as `split` and write `Split P-n: accept` in the memo. Answer the other seat's split proposal with `Split P-n: accept` or `Split P-n: reject`.
6. **Ask for data** in `evidence/requests.md` (status `open`) when a position rests on a number nobody has. **Round 1: data before rulings.** Every round-1 memo lists the requests filed, or says `none needed` and why; don't rule on a contested number before its evidence is in.
7. **Questions.** Close what you can: `answered` with a Resolution that only points to where the answer lives (`→ R-15`, `→ §6 Turnaround`, ≤ 15 words); `deferred` with owner role and trigger; `dropped` with reason. Closed rows stay; never delete a row or reuse an ID. New questions take the next free `Q-n` and the `?` marker.
8. **Clearing a provisional value** needs a **Provisional cleared** line in the memo for each one: the value and the evidence file, or the role from `_shared/roles.md` whose authority settles it.
9. **Memo** at `turns/<round>-<seat>.md` from `${CLAUDE_PLUGIN_ROOT}/templates/memo.md`, ≤ 500 words.
10. **Check.** Get the PRD version you received as `medium.md` §Versions says. Make a local copy if the medium isn't local (`process.md` §The check runs on local files). Run:
    ```
    python3 "${CLAUDE_PLUGIN_ROOT}/skills/prd-check/check.py" <local bundle> \
      --prev <the PRD as you received it> \
      --memo turns/<round>-<seat>.md \
      --summary rounds/<latest round>-summary.md --seat <seat>
    ```
    `--memo` is the memo you just wrote, never the other seat's. `--summary` is the newest `rounds/*-summary.md`; leave out `--summary` and `--seat` only when no summary exists yet. On an agreement turn add `--agree`. (`check.py` sits beside prd-check's SKILL.md.) Fix and re-run until PASS. A turn that fails does not land.
11. Update `state.json`: `next` only (round complete → hand to `prd-retro`). Never change `status`; only `prd-retro` sets it. Write everything back and hand off as `medium.md` says.

## Evidence rule

Every decision cites a file in the bundle. A value with no evidence in the bundle and no authority in the inputs is written `[provisional]` or `[provisional: <reason>]` (a reason is encouraged). Never invent a person, a date, or a number presented as firm.

## Anti-patterns

Appending a diary to the PRD · re-arguing a closed question without new evidence · writing an answer into the Resolution cell instead of the PRD · estimating effort in time · naming people · answering for the other seat · making the PRD longer to sound thorough · "agreeing" with a change attached.
