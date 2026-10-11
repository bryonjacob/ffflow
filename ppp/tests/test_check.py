"""Tests for ppp/skills/prd-check/check.py. Run from the repo root:

    python3 -m unittest discover -s ppp/tests -v

stdlib only. Each directory in fixtures/ not starting with "_" is one case, described by its
case.json: {"target", "args", "exit", "fails", "warns", "fail_counts", "metrics"?}.
"""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
PPP = HERE.parent
CHECK = PPP / "skills" / "prd-check" / "check.py"
FIXTURES = HERE / "fixtures"
TEMPLATES = PPP / "templates"
DESIGN_BUNDLE = PPP / "docs" / "prds" / "ppp"

_spec = importlib.util.spec_from_file_location("prd_check", CHECK)
prd_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(prd_check)


def run_check(target, args=(), cwd=None):
    proc = subprocess.run(
        [sys.executable, str(CHECK), str(target), *args, "--json"],
        cwd=cwd, capture_output=True, text=True, encoding="utf-8",
    )
    report = None
    if proc.stdout.strip():
        report = json.loads(proc.stdout)
    return proc.returncode, report, proc


def minimal_prd(sections=None):
    """A PRD with the eleven headings; `sections` maps section number to body text."""
    sections = sections or {}
    out = ["# T", "", "Status: drafting", ""]
    for n, title in enumerate(prd_check.HEADINGS, 1):
        out.append(f"## {n}. {title}")
        if n in sections:
            out.append(sections[n])
        out.append("")
    out += ["| ID | ? | Question | Raised by | Owner (role) | Status | Resolution |",
            "|---|---|---|---|---|---|---|"]
    return "\n".join(out) + "\n"


class FixtureCases(unittest.TestCase):
    def test_fixtures(self):
        cases = sorted(p for p in FIXTURES.iterdir() if p.is_dir() and not p.name.startswith("_"))
        self.assertGreater(len(cases), 20)
        for case_dir in cases:
            with self.subTest(case=case_dir.name):
                spec = json.loads((case_dir / "case.json").read_text(encoding="utf-8"))
                code, report, proc = run_check(spec["target"], spec.get("args", []), cwd=case_dir)
                self.assertEqual(code, spec["exit"], proc.stdout + proc.stderr)
                if code == 2:
                    self.assertEqual(report["result"], "ERROR")
                    continue
                fails = Counter(f["code"] for f in report["fails"])
                warns = {w["code"] for w in report["warns"]}
                self.assertEqual(set(fails), set(spec.get("fails", [])), proc.stdout)
                self.assertEqual(warns, set(spec.get("warns", [])), proc.stdout)
                for code_name, count in spec.get("fail_counts", {}).items():
                    self.assertEqual(fails[code_name], count, proc.stdout)
                for key, value in spec.get("metrics", {}).items():
                    self.assertEqual(report[key], value, key)
                self.assertEqual(report["result"], "PASS" if spec["exit"] == 0 else "FAIL")


class JsonReport(unittest.TestCase):
    def test_schema(self):
        code, report, _ = run_check(".", ["--prev", "prev.md", "--memo", "memo.md"],
                                    cwd=FIXTURES / "pass-growth")
        self.assertEqual(code, 0)
        self.assertEqual(set(report), {"result", "prd", "words", "growth", "key_decisions", "questions",
                                       "provisional", "xl_increments", "fails", "warns"})
        self.assertEqual(set(report["questions"]), {"open", "answered", "deferred", "dropped"})
        self.assertLess(report["growth"]["before"], report["growth"]["after"])

    def test_text_output(self):
        proc = subprocess.run([sys.executable, str(CHECK), "."], cwd=FIXTURES / "fail-time",
                              capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(proc.returncode, 1)
        self.assertTrue(proc.stdout.startswith("FAIL"))
        self.assertIn("✗ TIME", proc.stdout)

    def test_unreadable_prev_is_input_error(self):
        code, report, _ = run_check(".", ["--prev", "missing.md"], cwd=FIXTURES / "pass-good")
        self.assertEqual(code, 2)


class Patterns(unittest.TestCase):
    TIME_STRINGS = ["2 sprints", "3 dev-days", "Q3", "2026-01-15", "March 3", "by end of quarter"]

    def _check(self, sections):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "b"
            bundle.mkdir()
            (Path(tmp) / "_shared").mkdir()
            (Path(tmp) / "_shared" / "roster.txt").write_text("# none\n", encoding="utf-8")
            prd = bundle / "b-prd.md"
            prd.write_text(minimal_prd(sections), encoding="utf-8")
            (bundle / "parking-lot.md").write_text(
                (TEMPLATES / "parking-lot.md").read_text(encoding="utf-8"), encoding="utf-8")
            return prd_check.check(prd, bundle / "parking-lot.md", Path(tmp) / "_shared")

    def test_time_patterns(self):
        for s in self.TIME_STRINGS:
            with self.subTest(s=s):
                in_increments = self._check({8: f"1. **Thing (S):** done {s}."})
                self.assertIn("TIME", {f.code for f in in_increments.fails}, s)
                in_service = self._check({6: f"Turnaround is {s}."})
                self.assertNotIn("TIME", {f.code for f in in_service.fails}, s)

    def test_provisional_forms(self):
        self.assertEqual(len(prd_check.PROVISIONAL_RE.findall(
            "a [provisional] b [Provisional: no data] c [provisional:x] d [provisionally]")), 3)


class Templates(unittest.TestCase):
    def test_template_skeleton_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = Path(tmp) / "new-thing"
            bundle.mkdir()
            prd = (TEMPLATES / "prd.md").read_text(encoding="utf-8")
            prd = prd.replace("# <Title>", "# New thing")
            (bundle / "new-thing-prd.md").write_text(prd, encoding="utf-8")
            lot = (TEMPLATES / "parking-lot.md").read_text(encoding="utf-8").replace("<slug>", "new-thing")
            (bundle / "parking-lot.md").write_text(lot, encoding="utf-8")
            code, report, proc = run_check(bundle)
            self.assertEqual(code, 0, proc.stdout)
            self.assertEqual(report["fails"], [])

    def test_state_template_is_json(self):
        state = json.loads((TEMPLATES / "state.json").read_text(encoding="utf-8"))
        self.assertEqual(state["status"], "drafting")


class Dogfood(unittest.TestCase):
    def test_dogfood_design_prd(self):
        code, report, proc = run_check(DESIGN_BUNDLE)
        self.assertEqual(code, 0, proc.stdout)
        self.assertEqual(report["fails"], [])
        self.assertTrue(report["prd"].endswith("ppp-prd.md"))

    def test_dogfood_bundle_parts(self):
        for part in ["ppp-prd.md", "parking-lot.md", "evidence/requests.md", "state.json", "medium.md"]:
            self.assertTrue((DESIGN_BUNDLE / part).is_file(), part)
        json.loads((DESIGN_BUNDLE / "state.json").read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
