"""Tests for analysis/novelty/consensus.py — voting, kappa, LOO stability."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "analysis" / "novelty"))

from consensus import (  # noqa: E402
    leave_one_out_stability,
    majority_vote,
    fleiss_kappa,
    consensus_decision,
    TAU_DEFAULT,
)


def test_majority_clean():
    assert majority_vote(["C1", "C1", "C2"]) == ("C1", 2, 3)


def test_majority_tie_is_none():
    assert majority_vote(["C1", "C2"]) == (None, 1, 2)


def test_majority_empty():
    assert majority_vote([]) == (None, 0, 0)


def test_consensus_meets_tau():
    d = consensus_decision(["known", "known", "novel"], 0.65)
    assert d["label"] == "known" and d["met_tau"]
    assert d["share"] == pytest.approx(2 / 3, abs=1e-3)


def test_consensus_plurality_fails_tau():
    # true plurality: 3-2 split (majority of the full panel, but below tau)
    d = consensus_decision(["known", "known", "known", "novel", "variant"], 0.65)
    assert d["label"] == "known" and not d["met_tau"]
    assert d["share"] == pytest.approx(0.6, abs=1e-3)


def test_consensus_three_way_deadlock_is_none():
    # genuine 3-way tie has no winner and cannot meet tau
    d = consensus_decision(["known", "novel", "variant"])
    assert d["label"] is None and not d["met_tau"]


def test_fleiss_perfect():
    assert fleiss_kappa([["a"] * 3, ["a"] * 3]) == float("inf")


def test_fleiss_symmetric():
    m = [["a"] * 3, ["b"] * 3, ["a"] * 3]
    assert fleiss_kappa(m) == pytest.approx(1.0)


def test_fleiss_disagreement_is_low():
    m = [["a", "b", "c"], ["a", "b", "c"], ["a", "b", "c"]]
    assert fleiss_kappa(m) < 0.5


def test_loo_stability_identical_raters_designs_3():
    items = [["novel" if i % 3 == 0 else "known" for i in range(3)] for _ in range(5)]
    # transpose into item-major (5 items x 3 raters, all identical)
    trans = list(zip(*items))
    res = leave_one_out_stability(trans)
    assert res["k_design"] == 3
    assert res["by_k"][0]["k_stable"]


def test_loo_flips_when_rater_diverges():
    items = [
        ["novel", "novel", "novel"],
        ["known", "known", "novel"],  # rater 2 disagrees
    ]
    trans = list(zip(*items))
    res = leave_one_out_stability(trans)
    # k=2 treated as degenerate; should NOT design below 3
    assert res["k_design"] != 2