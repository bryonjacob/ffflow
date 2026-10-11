---
name: prd-split
description: Carve a growing thread out of a PPP PRD into its own PRD — turn a parking-lot `split` entry into a one-paragraph charter, remove the thread from the parent, and open the child with prd-start. Use when prd-check or a retro signals a split and the seats accept it.
---

# prd-split

## Plan Mode

This skill does NOT invoke Plan Mode. It moves content between bundles directly, confirming the charter with the user first.

## Steps

0. Locate the bundle (`${CLAUDE_PLUGIN_ROOT}/process.md` §Finding a bundle) and read `medium.md`; do every read, write and hand-off below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue.
1. Take the `split` entry. Write a charter (≤ 120 words): the problem, the roles, what's in, what stays in the parent, and the one interface between them. Confirm it with the user.
2. Move every requirement, journey step, question and parking-lot entry that belongs to the child into the child's seed; leave in the parent a single line in Non-goals pointing at the child.
3. Run `/ppp:prd-start` for the child with the parent's medium reference (the same protocol unless the user agrees another), the slug, the charter and the seed. Record `links.parent` / `links.children` in both `state.json` files. Mark the parent's `split` entry routed to the child.
4. Re-run the check on the parent (on a local copy if the medium isn't local):
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/prd-check/check.py" <parent bundle>
   ```
   (`check.py` sits beside prd-check's SKILL.md.) The split should clear the signal that triggered it.
5. Write back and hand off as `medium.md` says.

## Rule

A split never loses content and never duplicates it. Each requirement lives in exactly one PRD.
