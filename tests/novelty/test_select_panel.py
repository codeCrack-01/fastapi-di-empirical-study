"""Tests for select_panel greedy + normalize (pure logic, no network)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "analysis" / "novelty"))

from select_panel import greedy_panel, normalize_anchor_label  # noqa: E402


def test_normalize_aliases():
    assert normalize_anchor_label("external_di") == "external_di"
    assert normalize_anchor_label("External") == "external_di"


def test_greedy_prefers_diverse_errors():
    # Three candidates: same accuracy but candidate C errs on DIFFERENT anchors.
    expected = ["a", "b", "c", "d", "e", "f"]
    a_pred = ["a", "b", "ERR", "ERR", "e", "f"]   # errs on c,d
    b_pred = ["a", "b", "ERR", "ERR", "e", "f"]   # same errors as A
    c_pred = ["a", "b", "c", "d", "ERR", "ERR"]   # errs on e,f (different)
    cands = {
        "A": {"accuracy": 0.9, "predicted": a_pred, "expected": expected},
        "B": {"accuracy": 0.9, "predicted": b_pred, "expected": expected},
        "C": {"accuracy": 0.9, "predicted": c_pred, "expected": expected},
    }
    panel = greedy_panel(cands, k=2)
    assert panel[0] == "A"
    assert panel[1] == "C"


def test_greedy_skips_below_floor_competitor():
    expected = ["a", "b", "c"]
    cands = {
        "strong": {"accuracy": 0.95, "predicted": expected, "expected": expected},
        "weak": {"accuracy": 0.6, "predicted": ["b", "b", "b"], "expected": expected},
    }
    assert greedy_panel(cands, 2) == ["strong", "weak"]  # floor applied by caller


def test_greedy_empty():
    assert greedy_panel({}, 3) == []