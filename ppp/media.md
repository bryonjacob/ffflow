# Media: where a PPP bundle lives

PPP is defined over a set of text documents. It is not prescriptive about where they live. A repo,
a shared online drive, a wiki (Confluence, Notion), a Linear-style tracker: any of them works if it
meets the requirements below and the seats agree on how to use it.

## What a medium must do
1. **Hold several documents.** A bundle is a PRD plus its parking lot, evidence, round summaries,
   turn memos, state and medium record (`process.md` §The bundle). It is never one document.
2. **Let every seat and every PPP skill read and write them.** If a seat or a skill can't reach a
   document, the medium doesn't work for this PRD.
3. **Keep versions until it converges.** The documents change every turn and converge on a final
   version. The medium keeps a version of the PRD per turn, so each turn can be checked against the
   last, and ends with the final version committed.
4. **Be agreed.** Before the first turn, every seat agrees on what the documents are, where each one
   lives, how a seat gets the current version and writes back, how the next seat learns it is their
   turn (the hand-off), how each seat signs off, and what act commits the final version.

That agreement is written into the bundle as `medium.md` (template: `templates/medium.md`). Every
PPP skill reads it first and does what it says. PPP knows nothing else about any medium.

## The check runs on local files
`prd-check` reads files on disk. When the medium isn't a local folder, the skill taking the turn
copies what the check needs (the PRD, the parking lot, the evidence files, the previous PRD version,
`_shared/roster.txt` and `_shared/limits.json`) into a scratch folder under the bundle's default
names, runs the check there, and writes back to the medium only after it passes.

## Bringing your own medium
Anyone can publish a medium document: a page, doc or file that lays out where a bundle goes,
usually with a presentation template for the PRD, and embeds the instructions for using it. Start
a PRD with a pointer to it:

    /ppp:prd-start <url or path to the medium document>

`prd-start` reads the instructions, checks them against the four requirements above, asks about
any gap, and records the result as the bundle's `medium.md`. A medium document decides where and
how; it never changes the process: seats, turns, rules, rounds and the check stay as `process.md`
says. Anything it asks for that reaches other people or can't be undone is confirmed first.

## A worked example: the repo and a draft pull request
If you like this example, use it. If not, agree on another protocol that meets the requirements.
`prd-start` offers it when no medium is given.

**Where.** The product's repo gets `docs/prds/`. Portfolio material lives in `docs/prds/_shared/`.

**A new PRD.** Branch `prd/<slug>` from the default branch, and folder `docs/prds/<slug>/`:

    docs/prds/<slug>/
      <slug>-prd.md               the PRD
      parking-lot.md              ideas, planning items, other-PRD and split entries
      evidence/requests.md        the data-request queue
      evidence/<nn>-<topic>.md    one answer per request
      rounds/<n>-summary.md       the retro for round n
      turns/<n>-<seat>.md         turn memos
      state.json                  round, next seat, status, sign-offs
      medium.md                   this protocol, filled in: repo, branch, PR, who holds each seat

Commit the skeleton, push the branch, and open a **draft pull request** on GitHub against the
default branch. The draft PR is the table the ping-pong is played on.

**A turn.** Pull the branch, take the turn, commit it as one commit
(`ppp(<slug>): round <n> <seat>`), push. That commit is the turn's version; the previous PRD
version for `prd-check --prev` is the same file at the previous turn's commit. Hand off with a PR
comment that names the next seat and mentions its holder. Evidence answers and round summaries are
commits on the same branch, announced the same way.

**Converged.** When `prd-retro` marks the PRD converged, mark the PR ready for review and request a
review from the holder of every seat. A seat signs off by reviewing: approve for `yes` or
`yes-with-conditions` (conditions in the review text, each already in the PRD as a requirement or a
deferred question), request changes for `no`.

**Ratified.** When every seat has approved and no `[provisional]` is left, merge. The merge is the
commit: the PRD on the default branch is the ratified version, next to the code that will be
planned from it.

**Needs:** every seat holder can use git and GitHub pull requests, or works through a session that
can.
