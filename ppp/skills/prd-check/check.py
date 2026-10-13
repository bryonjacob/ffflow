"""prd-check: the mechanical rules of the PPP process.

usage: python3 check.py <bundle-dir | prd-file> [--shared DIR] [--prev FILE --memo FILE]
                        [--summary FILE --seat SEAT] [--agree] [--ratify] [--json]

exit 0 = pass (warnings allowed), 1 = fail, 2 = input error.
stdlib only, Python 3.9+.
"""
import argparse
import json
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

# Defaults; a portfolio overrides any of them in <shared>/limits.json.
CEILING = 2500
KEY_DECISIONS = 3
MEMO_WORDS = 500
XL_INCREMENTS = 2
NEAR_CEILING_PCT = 90
PARKING_ENTRY_WORDS = 30
MIN_GROWTH_WORDS = 6
RESOLUTION_WORDS = 15

DEFAULT_LIMITS = {
    "ceiling": CEILING,
    "key_decisions": KEY_DECISIONS,
    "memo_words": MEMO_WORDS,
    "xl_increments": XL_INCREMENTS,
    "near_ceiling_pct": NEAR_CEILING_PCT,
    "parking_entry_words": PARKING_ENTRY_WORDS,
}

HEADINGS = [
    "Problem",
    "Roles",
    "Outcomes and non-goals",
    "Journeys",
    "Requirements",
    "Service parameters",
    "Metrics",
    "Increments",
    "Risks",
    "Key decisions",
    "Open questions",
]
STATUSES = {"open", "answered", "deferred", "dropped"}
PARK_KINDS = {"idea", "planning", "other-prd", "split"}
TIME_OK_SECTIONS = {6, 7}  # service parameters, metrics
REQUIREMENTS_SECTION, INCREMENTS, KEY_DECISIONS_SECTION, QUESTIONS_SECTION = 5, 8, 10, 11

MONTHS = r"(January|February|March|April|May|June|July|August|September|October|November|December)"
TIME_PATTERNS = [
    (re.compile(r"\b\d+(\.\d+)?\s*[-–]?\s*(business\s+|working\s+|calendar\s+)?(hours?|days?|weeks?|months?|sprints?)\b", re.I), "duration"),
    (re.compile(r"\b(person|dev|engineer|lane)[- ](hours?|days?|weeks?|months?)\b", re.I), "effort unit"),
    (re.compile(r"\bQ[1-4]\b"), "quarter"),
    (re.compile(r"\b\d{4}-\d{2}-\d{2}\b", re.I), "calendar date"),
    (re.compile(rf"\b{MONTHS}\b(\s+\d{{1,2}})?"), "month"),
    (re.compile(r"\bby (the )?end of (the )?(week|month|quarter|year)\b", re.I), "deadline"),
]
HISTORY_PATTERNS = [
    (re.compile(r"\bround\s*\d\b|\b(last|previous|this|next) round\b", re.I), "fail"),
    (re.compile(r"\b(accepted|proposed|raised|suggested|conceded|agreed) by\b", re.I), "warn"),
    (re.compile(r"\b(previously|was changed|corrected from|originally|we now|no longer)\b", re.I), "warn"),
]
PROVISIONAL_RE = re.compile(r"\[provisional(?::[^\]]*)?\]", re.I)
XXL_RE = re.compile(r"\b(X{2,}L|\dXL)\b")
XL_RE = re.compile(r"\bXL\b")
SECTION_RE = re.compile(r"^##\s+(\d+)\.")
HEADING_RE = re.compile(r"^##\s")
NUMBERED_HEADING_RE = re.compile(r"^##\s+(\d+)\.\s+(.+?)\s*$")
LIST_ITEM_RE = re.compile(r"^\s*(\d+\.|[-*])\s+\S")
SEPARATOR_RE = re.compile(r"^\|[\s\-:|]+\|$")
EVIDENCE_LINK_RE = re.compile(r"\]\((?:\./)?(evidence/[^)#\s]+)(?:#[^)]*)?\)")
GROWTH_RE = re.compile(r"\*\*Growth:\*\*\s*(.+)")
Q_ID_RE = re.compile(r"^\**(Q-\d+)\**$")
R_ID_RE = re.compile(r"^\**(R-\d+)\**$")
R_REF_RE = re.compile(r"\bR-(\d+)\b")
SECTION_REF_RE = re.compile(r"§\s*(\d+)")
F_ID_RE = re.compile(r"^\**(F-\d+)\**$")
FINDINGS_HEADING_RE = re.compile(r"^#+\s*Facilitator findings\b|^\*\*Facilitator findings:?\*\*", re.I)
CLEARED_RE = re.compile(r"^\*\*Provisional cleared:?\*\*:?\s*(.*)$", re.I)


class InputError(Exception):
    """Bad input: exit 2."""


@dataclass
class Finding:
    level: str  # "fail" | "warn"
    code: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None

    def render(self):
        where = ""
        if self.file and self.line:
            where = f"{self.file}:{self.line} "
        elif self.file:
            where = f"{self.file} "
        return f"{self.code} {where}{self.message}"

    def as_dict(self):
        return {"code": self.code, "file": self.file, "line": self.line, "message": self.message}


@dataclass
class Result:
    prd: str
    notes: List[str] = field(default_factory=list)
    findings: List[Finding] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)

    @property
    def fails(self):
        return [f for f in self.findings if f.level == "fail"]

    @property
    def warns(self):
        return [f for f in self.findings if f.level == "warn"]

    @property
    def passed(self):
        return not self.fails

    def fail(self, code, message, file=None, line=None):
        self.findings.append(Finding("fail", code, message, file, line))

    def warn(self, code, message, file=None, line=None):
        self.findings.append(Finding("warn", code, message, file, line))


# ---------- helpers ----------

def read(path, what):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as e:
        raise InputError(f"cannot read {what} '{path}': {e}")


def words(text):
    return len(re.findall(r"\w+", text))


def unfenced(text):
    """(line number, line) for every line outside ``` fences."""
    out, fenced = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if not fenced:
            out.append((i, line))
    return out


def sections(text):
    out, cur = {}, 0
    for i, line in enumerate(text.splitlines(), 1):
        m = SECTION_RE.match(line)
        if m:
            cur = int(m.group(1))
        out.setdefault(cur, []).append((i, line))
    return out


def table_rows(lines):
    for i, line in lines:
        s = line.strip()
        if s.startswith("|") and not SEPARATOR_RE.match(s):
            yield i, [c.strip() for c in s.strip("|").split("|")]


def same_text(a, b):
    """Equal ignoring line endings and trailing whitespace only."""
    def norm(t):
        return "\n".join(l.rstrip() for l in t.replace("\r\n", "\n").replace("\r", "\n").split("\n")).rstrip()
    return norm(a) == norm(b)


def question_ids(text):
    return {m.group(1) for _, cells in table_rows(sections(text).get(QUESTIONS_SECTION, []))
            if (m := Q_ID_RE.match(cells[0]))}


def summary_findings(text):
    """(F-id, owner seat) for every row of the summary's Facilitator findings section."""
    out, inside = [], False
    for i, line in enumerate(text.splitlines(), 1):
        if FINDINGS_HEADING_RE.match(line.strip()):
            inside = True
            continue
        if inside and line.startswith("#"):
            break
        if inside:
            for _, cells in table_rows([(i, line)]):
                m = F_ID_RE.match(cells[0])
                if m:
                    out.append((m.group(1), cells[1].lower().strip("* ") if len(cells) > 1 else ""))
    return out


def cleared_entries(memo_text):
    """Entries under the memo's **Provisional cleared:** line (list items, or inline text)."""
    out, inside = [], False
    for line in memo_text.splitlines():
        m = CLEARED_RE.match(line.strip())
        if m:
            inside = True
            inline = m.group(1).strip()
            if inline and inline.lower().rstrip(".") not in {"none", "<none>"} and not inline.startswith("<"):
                out.append(inline)
            continue
        if inside:
            s = line.strip()
            if LIST_ITEM_RE.match(s):
                out.append(re.sub(r"^(\d+\.|[-*])\s+", "", s))
            elif s:
                break
    return out


def load_roles(shared_dir):
    """Role names from <shared>/roles.md (list items or table rows), lowercased; None if missing."""
    path = Path(shared_dir) / "roles.md"
    if not path.is_file():
        return None
    roles = set()
    lines = list(enumerate(read(path, "roles").splitlines(), 1))
    for _, line in lines:
        s = line.strip()
        if LIST_ITEM_RE.match(s):
            s = re.sub(r"^(\d+\.|[-*])\s+", "", s)
            name = re.split(r"\*\*:|:\*\*|:| — | - | – ", s, maxsplit=1)[0]
            roles.add(name.strip("* ").lower())
    rows = list(table_rows(lines))
    for _, cells in rows[1:]:
        roles.add(cells[0].strip("* ").lower())
    return {r for r in roles if r}


def resolve_prd(target):
    p = Path(target)
    if p.is_file():
        return p
    if not p.is_dir():
        raise InputError(f"no such file or directory: '{target}'")
    named = sorted(p.glob("*-prd.md"))
    if len(named) > 1:
        raise InputError(f"more than one *-prd.md in '{target}': " + ", ".join(n.name for n in named))
    if named:
        return named[0]
    if (p / "prd.md").is_file():
        return p / "prd.md"
    raise InputError(f"no PRD in '{target}' (expected <slug>-prd.md or prd.md)")


def load_limits(shared_dir):
    limits = dict(DEFAULT_LIMITS)
    path = Path(shared_dir) / "limits.json"
    if not path.exists():
        return limits
    try:
        data = json.loads(read(path, "limits"))
    except json.JSONDecodeError as e:
        raise InputError(f"{path} is not valid JSON: {e}")
    if not isinstance(data, dict):
        raise InputError(f"{path} must be a JSON object")
    for key, value in data.items():
        if key not in DEFAULT_LIMITS:
            raise InputError(f"{path}: unknown limit '{key}' (known: {', '.join(sorted(DEFAULT_LIMITS))})")
        if isinstance(value, bool) or not isinstance(value, int) or value < 0:
            raise InputError(f"{path}: '{key}' must be a non-negative integer")
        limits[key] = value
    return limits


# ---------- the check ----------

def check(prd_path, parking_path, shared_dir, prev=None, memo=None, agree=False, ratify=False,
          summary=None, seat=None):
    if prev and not memo:
        raise InputError("--prev needs --memo: pass this turn's memo (turns/<round>-<seat>.md)")
    if agree and not prev:
        raise InputError("--agree needs --prev and --memo: the PRD version this seat received, and its memo")
    if summary and not (memo and seat):
        raise InputError("--summary needs --memo and --seat: whose findings to check, in which memo")
    no_open = agree or ratify
    prd_path = Path(prd_path)
    shared_dir = Path(shared_dir)
    prd_name = prd_path.name
    prd = read(prd_path, "PRD")
    limits = load_limits(shared_dir)
    prev_text = read(prev, "--prev") if prev else None
    memo_text = read(memo, "--memo") if memo else None
    summary_text = read(summary, "--summary") if summary else None
    parking = read(parking_path, "parking lot") if Path(parking_path).is_file() else None

    r = Result(prd=str(prd_path))
    sec = sections(prd)
    lines = prd.splitlines()
    ceiling = limits["ceiling"]

    # headings: exactly the template's eleven, numbered and in order
    found = [(i, l) for i, l in unfenced(prd) if HEADING_RE.match(l)]
    for idx, (i, line) in enumerate(found):
        want = f"## {idx + 1}. {HEADINGS[idx]}" if idx < len(HEADINGS) else None
        m = NUMBERED_HEADING_RE.match(line)
        ok = (want is not None and m is not None and int(m.group(1)) == idx + 1
              and m.group(2).lower() == HEADINGS[idx].lower())
        if not ok:
            expect = f"expected '{want}'" if want else "no headings beyond the eleven"
            r.fail("HEADINGS", f"'{line.strip()}': {expect}", prd_name, i)
    for idx in range(len(found), len(HEADINGS)):
        r.fail("HEADINGS", f"missing '## {idx + 1}. {HEADINGS[idx]}'", prd_name)

    # size and growth
    n = words(prd)
    r.notes.append(f"words: {n} (soft ceiling {ceiling})")
    if n > ceiling:
        r.warn("CEILING", f"over the soft ceiling: {n} words > {ceiling}", prd_name)
    elif n >= ceiling * limits["near_ceiling_pct"] / 100:
        r.warn("CEILING-NEAR", f"{n} words is at least {limits['near_ceiling_pct']}% of the {ceiling}-word "
               "ceiling; trim before adding", prd_name)
    growth = None
    if prev_text is not None:
        before = words(prev_text)
        growth = {"before": before, "after": n}
        r.notes.append(f"growth: {before} -> {n} ({n - before:+d})")
        if n > before:
            g = GROWTH_RE.search(memo_text or "")
            if not g or len(g.group(1).split()) < MIN_GROWTH_WORDS:
                r.fail("GROWTH", "the PRD grew but the memo has no growth justification", prd_name)
    if agree and not same_text(prd, prev_text):
        r.fail("AGREE", "an agreement turn leaves the PRD exactly as received; any change is a normal turn",
               prd_name)
    if memo_text is not None:
        mw = words(memo_text)
        if mw > limits["memo_words"]:
            r.warn("MEMO", f"memo is {mw} words; the limit is {limits['memo_words']}", Path(memo).name)

    # names
    roster = shared_dir / "roster.txt"
    targets = {prd_name: prd}
    if parking is not None:
        targets[Path(parking_path).name] = parking
    if roster.is_file():
        names = [l.strip() for l in read(roster, "roster").splitlines()
                 if l.strip() and not l.strip().startswith("#")]
        for name in names:
            pat = re.compile(rf"\b{re.escape(name)}\b", re.I)
            for fname, text in targets.items():
                for i, line in enumerate(text.splitlines(), 1):
                    if pat.search(line):
                        r.fail("NAME", f"names a person ({name}); use a role", fname, i)
    else:
        r.warn("NAME", "no roster.txt found; person-name check skipped")

    # time units outside service parameters / metrics
    for s, sec_lines in sec.items():
        if s in TIME_OK_SECTIONS:
            continue
        for i, line in sec_lines:
            for pat, label in TIME_PATTERNS:
                m = pat.search(line)
                if m:
                    r.fail("TIME", f"{label} '{m.group(0)}' outside service parameters/metrics", prd_name, i)
                    break

    # sizes
    inc_lines = {j for j, _ in sec.get(INCREMENTS, [])}
    for i, line in enumerate(lines, 1):
        if XXL_RE.search(line):
            r.fail("SIZE", "XXL is not a size; list its parts, each XL or smaller", prd_name, i)
        if XL_RE.search(line) and i not in inc_lines:
            r.warn("SIZE", "size used outside Increments", prd_name, i)
    xl = sum(1 for _, l in sec.get(INCREMENTS, []) if XL_RE.search(l))

    # history
    q_lines = {j for j, _ in sec.get(QUESTIONS_SECTION, [])}
    for i, line in enumerate(lines, 1):
        if i in q_lines:
            continue  # the question table records who raised what by design
        for pat, level in HISTORY_PATTERNS:
            m = pat.search(line)
            if m:
                msg = f"'{m.group(0)}': the PRD states the shape, not how it got there"
                (r.fail if level == "fail" else r.warn)("HISTORY", msg, prd_name, i)

    # key decisions
    kd_lines = sec.get(KEY_DECISIONS_SECTION, [])[1:]
    kd = [l for _, l in kd_lines if LIST_ITEM_RE.match(l)]
    if any(l.strip().startswith("|") for _, l in kd_lines):
        kd += [cells for _, cells in table_rows(kd_lines)][1:]
    kd_limit = limits["key_decisions"]
    r.notes.append(f"key decisions: {len(kd)} (limit {kd_limit})")
    if len(kd) > kd_limit:
        r.fail("DECISIONS", f"{len(kd)} key decisions; the limit is {kd_limit} (more suggests a split)", prd_name)
    elif kd_limit and len(kd) == kd_limit:
        r.warn("DECISIONS-AT-LIMIT", f"{len(kd)} key decisions is the limit; could a requirement carry one?",
               prd_name)

    # open questions
    counts = {s: 0 for s in ("open", "answered", "deferred", "dropped")}
    r_ids = {m.group(1) for _, cells in table_rows(sec.get(REQUIREMENTS_SECTION, [])) if (m := R_ID_RE.match(cells[0]))}
    section_nums = set(range(1, len(HEADINGS) + 1)) & set(sec)
    rows = list(table_rows(sec.get(QUESTIONS_SECTION, [])))
    for i, cells in rows[1:]:
        if not re.match(r"^\**Q-\d+\**$", cells[0]):
            continue
        if len(cells) < 7:
            r.fail("QUESTIONS", "needs 7 columns", prd_name, i)
            continue
        status = cells[5].lower().strip("* ")
        if status not in STATUSES:
            r.fail("QUESTIONS", f"status '{cells[5]}' not one of {sorted(STATUSES)}", prd_name, i)
        else:
            counts[status] += 1
        if (cells[1] == "?") != (status == "open"):
            r.fail("QUESTIONS", "'?' marker must be present exactly when status is open", prd_name, i)
        if not cells[2]:
            r.fail("QUESTIONS", "question text is empty", prd_name, i)
        if status == "deferred" and (not cells[4] or not cells[6]):
            r.fail("QUESTIONS", "deferred needs an owner role and a trigger", prd_name, i)
        if status in {"answered", "dropped"} and not cells[6]:
            r.fail("QUESTIONS", f"{status} needs a resolution", prd_name, i)
        elif status == "answered":
            refs = R_REF_RE.findall(cells[6])
            secs = SECTION_REF_RE.findall(cells[6])
            dangling = [f"R-{x}" for x in refs if f"R-{x}" not in r_ids]
            dangling += [f"§{x}" for x in secs if int(x) not in section_nums]
            if not refs and not secs:
                r.fail("QUESTIONS", "an answered resolution points to where the answer lives (→ R-n or → §n)",
                       prd_name, i)
            elif dangling:
                r.fail("QUESTIONS", f"resolution points to {', '.join(dangling)}, which is not in the PRD",
                       prd_name, i)
            if words(cells[6]) > RESOLUTION_WORDS:
                r.fail("QUESTIONS", f"resolution is {words(cells[6])} words; a pointer is at most "
                       f"{RESOLUTION_WORDS}", prd_name, i)
    provisional = len(PROVISIONAL_RE.findall(prd))
    r.notes.append("questions: " + " · ".join(f"{k} {v}" for k, v in counts.items())
                   + f" · provisional values: {provisional}")
    if no_open and counts["open"]:
        r.fail("OPEN-QUESTIONS", f"{counts['open']} questions still open; converging needs none", prd_name)
    if prev_text is not None:
        gone = sorted(question_ids(prev_text) - question_ids(prd), key=lambda q: int(q[2:]))
        if gone:
            r.fail("QUESTIONS-REMOVED", f"{', '.join(gone)} removed; closed questions stay and IDs are never "
                   "reused", prd_name)
        cleared = len(PROVISIONAL_RE.findall(prev_text)) - provisional
        if cleared > 0:
            entries = cleared_entries(memo_text or "")
            roles = load_roles(shared_dir)
            if roles is None:
                ok = [e for e in entries if e.strip()]
                r.warn("PROVISIONAL-CLEARED", "no roles.md found; cleared-value justifications not checked "
                       "against roles")
            else:
                ok = [e for e in entries if "evidence/" in e
                      or any(re.search(rf"\b{re.escape(role)}\b", e, re.I) for role in roles)]
            if len(ok) < cleared:
                r.fail("PROVISIONAL-CLEARED", f"{cleared} provisional values cleared but the memo justifies "
                       f"{len(ok)}; each needs an evidence link or the role whose authority settles it",
                       Path(memo).name if memo else prd_name)
    if ratify and provisional:
        r.fail("PROVISIONAL", f"{provisional} [provisional] values remain; a ratified PRD has none", prd_name)

    # evidence links
    base = prd_path.parent
    for i, line in enumerate(lines, 1):
        for m in EVIDENCE_LINK_RE.finditer(line):
            if not (base / m.group(1)).is_file():
                r.fail("EVIDENCE", f"link {m.group(1)} does not resolve", prd_name, i)

    # parking lot
    if parking is None:
        r.fail("PARKING", f"no parking lot at {parking_path}")
    else:
        pname = Path(parking_path).name
        pl_rows = list(table_rows(list(enumerate(parking.splitlines(), 1))))
        for i, cells in pl_rows[1:]:
            if not re.match(r"^P-\d+$", cells[0]):
                continue
            kind = cells[1].lower() if len(cells) > 1 else ""
            if kind not in PARK_KINDS:
                r.fail("PARKING", f"kind '{kind}' not one of {sorted(PARK_KINDS)}", pname, i)
            entry = " ".join(cells[2:4])
            ew = words(entry)
            if ew > limits["parking_entry_words"]:
                r.warn("PARKING-LONG", f"entry is {ew} words (item + why); keep it to one line of about "
                       f"{limits['parking_entry_words']}", pname, i)

    # facilitator findings owned by this seat must be answered by ID in its memo
    if summary_text is not None:
        mine = [f for f, owner in summary_findings(summary_text) if owner == seat.lower()]
        missing = [f for f in mine if not re.search(rf"\b{re.escape(f)}\b", memo_text)]
        if missing:
            r.fail("FINDINGS", f"{', '.join(missing)} not answered (accepted or rejected, by ID)",
                   Path(memo).name)

    if limits["xl_increments"] and xl == limits["xl_increments"]:
        r.warn("XL-AT-LIMIT", f"{xl} XL increments is the limit; could one be smaller or split?", prd_name)

    # split signals
    signals = []
    if n > ceiling:
        signals.append("over the ceiling")
    if len(kd) > kd_limit:
        signals.append(f"more than {kd_limit} key decisions")
    if xl > limits["xl_increments"]:
        signals.append(f"{xl} XL increments")
    if signals:
        r.warn("SPLIT", "consider prd-split: " + ", ".join(signals))

    r.metrics = {
        "words": n,
        "growth": growth,
        "key_decisions": len(kd),
        "questions": counts,
        "provisional": provisional,
        "xl_increments": xl,
    }
    return r


# ---------- CLI ----------

def report_json(r):
    return {
        "result": "PASS" if r.passed else "FAIL",
        "prd": r.prd,
        **r.metrics,
        "fails": [f.as_dict() for f in r.fails],
        "warns": [f.as_dict() for f in r.warns],
    }


def main(argv=None):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except (AttributeError, ValueError):
        pass
    ap = argparse.ArgumentParser(prog="check.py", description="prd-check: the mechanical rules of PPP.")
    ap.add_argument("target", help="bundle directory or PRD file")
    ap.add_argument("--shared", help="the portfolio's _shared directory (default: <bundle>/../_shared)")
    ap.add_argument("--prev", help="the previous PRD version")
    ap.add_argument("--memo", help="this turn's memo (required with --prev)")
    ap.add_argument("--summary", help="the latest round summary, for facilitator findings (needs --seat)")
    ap.add_argument("--seat", help="the seat taking this turn, whose findings the memo must answer")
    ap.add_argument("--agree", action="store_true",
                    help="agreement turn: PRD unchanged from --prev, no open questions")
    ap.add_argument("--ratify", action="store_true", help="ratification: no open questions, no [provisional]")
    ap.add_argument("--json", action="store_true", help="machine-readable report")
    a = ap.parse_args(argv)

    try:
        prd_path = resolve_prd(a.target)
        bundle = prd_path.resolve().parent
        shared = Path(a.shared) if a.shared else bundle.parent / "_shared"
        r = check(prd_path, bundle / "parking-lot.md", shared, a.prev, a.memo, a.agree, a.ratify,
                  a.summary, a.seat)
    except InputError as e:
        if a.json:
            print(json.dumps({"result": "ERROR", "message": str(e)}))
        print(f"ERROR {e}", file=sys.stderr)
        return 2

    if a.json:
        print(json.dumps(report_json(r), indent=2, ensure_ascii=False))
    else:
        print("PASS" if r.passed else "FAIL")
        for x in r.notes:
            print("  ·", x)
        for f in r.fails:
            print("  ✗", f.render())
        for f in r.warns:
            print("  !", f.render())
    return 0 if r.passed else 1


if __name__ == "__main__":
    sys.exit(main())
