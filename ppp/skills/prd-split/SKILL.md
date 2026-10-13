---
name: prd-split
description: Carve a growing thread out of a PPP PRD into its own PRD — turn a parking-lot `split` entry both seats accepted into a one-paragraph charter, move the thread from the parent, and open the child with prd-start. Use once both seats' memos say "Split P-n: accept".
---

# prd-split

## Plan Mode

This skill does NOT invoke Plan Mode. It moves content between bundles directly, confirming the charter with the user first.

## Steps

0. Locate the bundle (`${CLAUDE_PLUGIN_ROOT}/process.md` §Finding a bundle) and read `medium.md`; do every read, write and hand-off below as it says. If `medium.md` is missing, ask the user how the bundle is being managed (offer the worked example), write it from `${CLAUDE_PLUGIN_ROOT}/templates/medium.md`, then continue.
1. **Confirm acceptance.** A split is proposed in an ordinary turn (`process.md` §Split signals). Find `Split P-n: accept` in a builder memo and in a product memo, both naming this entry. Missing either: report which seat hasn't accepted and stop. There is no special split mode and nothing to add to `state.json`.
2. Take the `split` entry. Write a charter (≤ 120 words): the problem, the roles, what's in, what stays in the parent, and the one interface between them. Confirm it with the user.
3. Move every requirement, journey step, question and parking-lot entry that belongs to the child into the child's seed. If the parent is still an empty skeleton, there is nothing to move: the child starts from the charter alone. Either way, leave in the parent a single line in Non-goals pointing at the child.
4. Run `/ppp:prd-start` for the child with the parent's medium reference (the same protocol unless the user agrees another), the slug, the charter, the parent's seat holders and the seed. Record `links.parent` / `links.children` in both `state.json` files. Mark the parent's `split` entry routed to the child.
5. Re-run the check on the parent (on a local copy if the medium isn't local):
   ```
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/prd-check/check.py" <parent bundle>
   ```
   (`check.py` sits beside prd-check's SKILL.md.) The split should clear the signal that triggered it.
6. Write back and hand off as `medium.md` says.

## Rule

A split never loses content and never duplicates it. Each requirement lives in exactly one PRD.
