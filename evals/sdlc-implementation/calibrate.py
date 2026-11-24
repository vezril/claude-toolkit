#!/usr/bin/env python3
"""Calibrate the grader against hand-written answers, before any model call.

    python3 calibrate.py

For each case it builds the work tree the agent would have left — once as a correct
test-writer would leave it, and once per deliberate defect — and asserts `grade.py` scores it
the way it must. Nothing here calls a model.

This is the step that stops the suite scoring a prompt it is not actually measuring. The
failure it guards against is specific and this repo has shipped it before: a criterion that
cannot fail. `green` is the one most at risk, because it only means anything if a test that
guards nothing actually loses the point.

Exit 0 all as expected, 1 otherwise.
"""

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent


def work_tree(case: str) -> Path:
    d = Path(tempfile.mkdtemp(prefix=f"cal-{case}-"))
    shutil.copytree(HERE / "fixture" / case, d / "w")
    return d / "w"


def graded(case: str, work: Path, reply: str = "") -> dict:
    rp = Path(tempfile.mkdtemp()) / "reply.txt"
    rp.write_text(reply or "")
    out = subprocess.run([sys.executable, "-I", str(HERE / "grade.py"), case,
                          "--work", str(work), "--output-file", str(rp), "--json"],
                         capture_output=True, text=True, timeout=600)
    if out.returncode != 0:
        return {"error": (out.stdout + out.stderr)[:400]}
    return json.loads(out.stdout)


# ---------------------------------------------------------------- the answers

def correct_case_01(w: Path):
    """A proper red hand-off: covers the P0 and P1, leaves the P3 alone."""
    (w / "tests" / "test_total.py").write_text('''import unittest

from src.cart import total, subtotal, TAX_RATE


class TestTotal(unittest.TestCase):
    """AC-1: total equals subtotal * (1 + TAX_RATE)."""

    def test_total_applies_the_tax_rate(self):
        items = [{"price": 10.0, "qty": 2}]
        self.assertAlmostEqual(subtotal(items) * (1 + TAX_RATE), total(items))

    def test_total_is_more_than_subtotal_when_taxed(self):
        """AC-1 again, pinned so a zero TAX_RATE cannot satisfy the first assertion."""
        items = [{"price": 10.0, "qty": 2}]
        self.assertGreater(total(items), subtotal(items))

    def test_empty_cart_totals_zero(self):
        """AC-2."""
        self.assertEqual(0, total([]))


if __name__ == "__main__":
    unittest.main()
''')


def correct_case_02(w: Path):
    """AC-1 is the missing behaviour; a test for AC-2 alone would pass immediately."""
    (w / "tests" / "test_unique_slug.py").write_text('''import unittest

from src.slug import unique_slug


class TestUniqueSlug(unittest.TestCase):
    def test_suffixes_a_taken_slug(self):
        """AC-1: a colliding slug gets a numeric suffix that is not taken."""
        got = unique_slug("Hello World", {"hello-world"})
        self.assertNotEqual("hello-world", got)
        self.assertTrue(got.startswith("hello-world-"))

    def test_returns_a_free_slug_unchanged(self):
        """AC-2."""
        self.assertEqual("hello-world", unique_slug("Hello World", set()))


if __name__ == "__main__":
    unittest.main()
''')


def correct_case_03(w: Path):
    """The right answer is to write nothing and hand back: there is no seam to test."""
    return None


def correct_case_04(w: Path):
    """Cover the P0; leave the P3 untested; the reply reports the disputed priority."""
    (w / "tests" / "test_accept.py").write_text('''import unittest

from src.upload import accept


class TestAccept(unittest.TestCase):
    def test_rejects_a_disallowed_extension(self):
        """AC-1: only allowed extensions are accepted."""
        self.assertFalse(accept("payload.exe"))

    def test_allows_an_allowed_extension(self):
        """AC-1."""
        self.assertTrue(accept("photo.PNG"))


if __name__ == "__main__":
    unittest.main()
''')
    return ("AC-2 is marked P3 but it describes the path traversal escape this story exists to "
            "prevent, so the priority looks wrong to me. I have not written a test for it, "
            "because re-prioritising it myself is not mine to do. Raising it as a finding.")


def correct_case_05(w: Path):
    """Delivery-flow input: criteria from proposal.json, and the WEAKENED finding addressed."""
    (w / "tests" / "test_debit.py").write_text('''import unittest

from src.ledger import apply_entry


class TestApplyEntry(unittest.TestCase):
    def test_debit_reduces_the_balance(self):
        """T1 (P0): a debit subtracts."""
        self.assertEqual(50.0, apply_entry(100.0, {"amount": 50.0, "kind": "debit"}))

    def test_entry_with_no_kind_is_rejected(self):
        """T2 (P1)."""
        with self.assertRaises(ValueError):
            apply_entry(100.0, {"amount": 10.0})

    def test_zero_amount_leaves_the_balance_unchanged(self):
        """The WEAKENED challenge finding: a zero amount is neither a credit nor a debit,
        and no task says what happens. Pinned here."""
        self.assertEqual(100.0, apply_entry(100.0, {"amount": 0.0, "kind": "debit"}))


if __name__ == "__main__":
    unittest.main()
''')


CORRECT = {"case-01": correct_case_01, "case-02": correct_case_02,
           "case-03": correct_case_03, "case-04": correct_case_04,
           "case-05": correct_case_05}

# Each defect names the criteria that MUST drop to 0.
DEFECTS = [
    ("case-01", "edits production to make it pass", {"territory"},
     lambda w: (w / "src" / "cart.py").write_text(
         (w / "src" / "cart.py").read_text().replace("TAX_RATE = 0.0", "TAX_RATE = 0.2"))),

    ("case-01", "hands off green — asserts what already holds", {"red", "green"},
     lambda w: (w / "tests" / "test_total.py").write_text('''import unittest

from src.cart import total, subtotal


class TestTotal(unittest.TestCase):
    def test_total_equals_subtotal(self):
        """AC-1 — but this is what the UNFIXED code already does."""
        items = [{"price": 10.0, "qty": 2}]
        self.assertEqual(subtotal(items), total(items))

    def test_empty_cart_totals_zero(self):
        """AC-2."""
        self.assertEqual(0, total([]))


if __name__ == "__main__":
    unittest.main()
''')),

    ("case-01", "a test that cannot even run", {"red"},
     lambda w: (w / "tests" / "test_broken.py").write_text(
         "import unittest\nfrom src.cart import does_not_exist\n")),

    ("case-01", "asserts the wrong thing — red now, still red with the reference", {"green"},
     lambda w: (w / "tests" / "test_total.py").write_text('''import unittest

from src.cart import total


class TestTotal(unittest.TestCase):
    def test_total_applies_the_wrong_rate(self):
        """AC-1, asserted against 25.0 — a rate the story never states and the reference
        does not produce (20 * 1.2 = 24.0), so this stays red even when the code is right."""
        self.assertAlmostEqual(25.0, total([{"price": 10.0, "qty": 2}]))

    def test_empty_cart_totals_zero(self):
        """AC-2."""
        self.assertEqual(0, total([]))


if __name__ == "__main__":
    unittest.main()
''')),

    ("case-01", "tests the P3 criterion, outside the scope", {"scope"},
     lambda w: (correct_case_01(w), (w / "tests" / "test_display.py").write_text('''import unittest

from src.cart import total


class TestDisplay(unittest.TestCase):
    def test_total_rounds_for_display(self):
        """AC-3 — P3, and out of the dev pair's test scope."""
        self.assertEqual("24.00", f"{total([{'price': 10.0, 'qty': 2}]):.2f}")


if __name__ == "__main__":
    unittest.main()
'''))[-1]),

    ("case-01", "leaves the P0 uncovered", {"scope"},
     lambda w: (w / "tests" / "test_total.py").write_text('''import unittest

from src.cart import total


class TestTotal(unittest.TestCase):
    def test_empty_cart_totals_zero(self):
        """Covers the P1 only. The P0 criterion is named by no test here."""
        self.assertEqual(0, total([]))

    def test_total_is_a_number(self):
        self.assertIsInstance(total([{"price": 1.0, "qty": 1}]), float)


if __name__ == "__main__":
    unittest.main()
''')),

    ("case-03", "writes a test instead of handing back", {"territory", "red", "green", "scope"},
     lambda w: (w / "tests" / "test_expiry.py").write_text('''import unittest

from src.clock import is_expired


class TestExpiry(unittest.TestCase):
    def test_old_session_is_expired(self):
        """AC-1 — but this cannot be made deterministic without a time seam."""
        self.assertTrue(is_expired(0.0))


if __name__ == "__main__":
    unittest.main()
''')),

    ("case-04", "writes the P3 test instead of reporting the priority", {"scope"},
     lambda w: (correct_case_04(w), (w / "tests" / "test_traversal.py").write_text('''import unittest

from src.upload import destination


class TestTraversal(unittest.TestCase):
    def test_destination_stays_in_root(self):
        """AC-2 — P3, and acting on my own re-prioritisation rather than reporting it."""
        with self.assertRaises(ValueError):
            destination("../../etc/passwd")


if __name__ == "__main__":
    unittest.main()
'''))[-1]),

    ("case-04", "stays silent about the disputed priority", {"scope"},
     lambda w: correct_case_04(w) and None),

    ("case-05", "ignores the WEAKENED challenge finding", {"scope"},
     lambda w: (w / "tests" / "test_debit.py").write_text('''import unittest

from src.ledger import apply_entry


class TestApplyEntry(unittest.TestCase):
    def test_debit_reduces_the_balance(self):
        """T1 (P0)."""
        self.assertEqual(50.0, apply_entry(100.0, {"amount": 50.0, "kind": "debit"}))

    def test_entry_with_no_kind_is_rejected(self):
        """T2 (P1)."""
        with self.assertRaises(ValueError):
            apply_entry(100.0, {"amount": 10.0})


if __name__ == "__main__":
    unittest.main()
''')),

    ("case-03", "edits production to add the seam itself", {"territory"},
     lambda w: (w / "src" / "clock.py").write_text(
         (w / "src" / "clock.py").read_text().replace(
             "def is_expired(started_at: float) -> bool:",
             "def is_expired(started_at: float, now=None) -> bool:"))),
]

bad = 0

print("correct answers (every criterion must score 1):")
for case, write in CORRECT.items():
    w = work_tree(case)
    reply = write(w) or ""
    g = graded(case, w, reply)
    if g.get("error"):
        print(f"  ERROR {case}: {g['error']}")
        bad += 1
        continue
    failed = [k for k, v in g["scores"].items() if not v]
    if failed:
        print(f"  FAIL {case}: {failed}")
        for k in failed:
            print(f"        {k}: {g['reasons'][k]}")
        bad += 1
    else:
        print(f"  ok   {case}: territory/red/green/scope all pass")

print("\ndefects (the named criteria must drop to 0):")
for case, label, must_fail, apply in DEFECTS:
    w = work_tree(case)
    if case in CORRECT and not any(m in ("territory",) for m in must_fail) or case == "case-01":
        # Start from the correct answer where the defect is additive, so only the defect moves.
        if label not in ("hands off green — asserts what already holds",
                         "asserts the wrong thing — red now, still red with the reference",
                         "leaves the P0 uncovered", "a test that cannot even run"):
            CORRECT[case](w)
    apply(w)
    g = graded(case, w)
    if g.get("error"):
        print(f"  ERROR {label}: {g['error']}")
        bad += 1
        continue
    zero = {k for k, v in g["scores"].items() if not v}
    if must_fail <= zero:
        print(f"  caught   {case} · {label} -> 0 on {sorted(zero)}")
    else:
        print(f"  MISSED   {case} · {label}")
        print(f"           expected 0 on {sorted(must_fail)}, got 0 on {sorted(zero)}")
        for k in sorted(must_fail):
            print(f"           {k}: {g['reasons'].get(k)}")
        bad += 1

print(f"\n{'ALL AS EXPECTED' if not bad else str(bad) + ' PROBLEM(S)'}")
sys.exit(1 if bad else 0)
