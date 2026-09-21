"""analysis/novelty/consensus.py — voting, agreement, and panel-size criteria.

Pure functions (no I/O) so they are trivially unit-testable:

    majority_vote(labels)      -> (winner, votes_for_winner, n) with tie = None
    fleiss_kappa(responses)    -> Fleiss' kappa over an N-item x K-rater matrix
    consensus_decision(...)    -> item-level label at pre-registered tau (majority share)
    leave_one_out_stability(rater_dfs) -> per-k majority stability when dropping
                                          any one rater (panel-size criterion)

Tie handling: an odd panel (3/5) yields a clean majority on binary/ternary
splits; with 10-way labels a 3-2 split (k=5) is still a plurality, so we expose
both the winner AND whether the shared Tau_T consensus threshold was met.

Tau, the consensus threshold, is a PRE-REGISTERED instrument parameter (the
paper fixes it before the definitive run). The leave-one-out stability sweep is
what DECIDES panel size k, decoupled from hardware.
"""
from __future__ import annotations

import itertools
import statistics as st
from collections import Counter
from typing import Iterable, Sequence

TAU_DEFAULT = 0.65


def majority_vote(labels: Sequence[str]) -> tuple[str | None, int, int]:
    """Return (winner or None on tie, votes_for_winner, n).

    Ties are only returned when the top two counts are equal and strict
    majority (> n/2) is impossible.
    """
    if not labels:
        return None, 0, 0
    counts = Counter(labels)
    (winner, top), = counts.most_common(1)
    second = counts.most_common(2)[1][1] if len(counts) > 1 else 0
    n = len(labels)
    if top > n / 2:
        return winner, top, n
    if top == second:
        return None, top, n
    return winner, top, n


def consensus_decision(labels: Sequence[str], tau: float = TAU_DEFAULT) -> dict:
    """Item label at the pre-registered tau (majority share) threshold.

    Returns:
        label   : winning label or None
        share   : winner share of votes (0 if no votes)
        n       : number of raters
        met_tau : True when n>0 and share >= tau
    """
    label, votes, n = majority_vote(labels)
    share = votes / n if n else 0.0
    return {
        "label": label,
        "share": round(share, 4),
        "n": n,
        "met_tau": n > 0 and share >= tau,
    }


def fleiss_kappa(responses: Sequence[Sequence[str]]) -> float:
    """Fleiss' kappa over an N-item x K-rater matrix (list of per-item label lists).

    Returns -inf if degenerate (no variance: all same label, or single item).
    Null-category handling: raters may return None -> treated as its own category
    so disagreement is four-point-unbiased in spirit; kappa stays well-defined.
    """
    items = [list(r) for r in responses]
    n_items = len(items)
    if n_items == 0:
        return float("-inf")
    n_raters = len(items[0])
    if n_raters == 0:
        return float("-inf")
    # category universe = union of returned labels (incl. None)
    categories: list[str | None] = []
    for item in items:
        for lab in item:
            if lab not in categories:
                categories.append(lab)
    n_cat = len(categories)
    if n_cat <= 1:
        return float("inf")  # perfect agreement

    P_i: list[float] = []
    for item in items:
        counts = Counter(item)
        p = sum((counts[c] / n_raters) ** 2 for c in categories)
        P_i.append((p - 1 / n_raters) / (1 - 1 / n_raters)) if n_raters > 1 else P_i.append(1.0)

    P_bar = st.mean(P_i) if P_i else 0.0
    p_c = sum((sum(1 for item in items if c in item) / (n_items * n_raters)) ** 2 for c in categories)
    if p_c == 1.0:
        return float("inf")
    denom = 1 - p_c
    if denom == 0:
        return float("-inf")
    return (P_bar - p_c) / denom


def leave_one_out_stability(item_labels: Sequence[Sequence[str]]) -> dict:
    """Panel-size criterion: per-k majority stability under leave-one-out.

    ``item_labels`` is N x K (K = full panel). For every k in 2..K we consider
    all subsets of size k of the panel, recompute the majority label per item,
    and drop one member -> flip fraction. The metric that DESIGNS k: the largest
    single-rater flip rate among size-(k-1) subsets descending from that k.

    Returns per-k: flip_rate (share of item decisions changed by dropping one
    rater) and k_stable (flip_rate <= eps). ``k_design`` = smallest k whose
    flip_rate <= eps.
    """
    eps_default = 0.02
    return _loo_stability_with_threshold(item_labels, eps_default)


def _loo_stability_with_threshold(item_labels: Sequence[Sequence[str]], eps: float) -> dict:
    n_raters = len(item_labels[0]) if item_labels else 0
    rows: list[dict] = []
    by_k: dict[int, float] = {}
    for k in range(2, n_raters + 1):
        flip_counts: list[int] = []
        for subset in itertools.combinations(range(n_raters), k):
            majority = [majority_vote([item[i] for i in subset])[0] for item in item_labels]
            for drop in subset:
                rest = [i for i in subset if i != drop]
                loo_majority = [majority_vote([item[i] for i in rest])[0] for item in item_labels]
                flips = sum(1 for m, loo in zip(majority, loo_majority) if m != loo)
                flip_counts.append(flips / max(len(item_labels), 1))
        flip_rate = max(flip_counts) if flip_counts else 0.0
        by_k[k] = round(flip_rate, 4)
        rows.append({"k": k, "flip_rate": flip_rate, "k_stable": flip_rate <= eps})
    # smallest k >= 3 where flip_rate <= eps (odd k preferred; k=2 is degenerate)
    stable = [k for k in sorted(by_k) if k >= 3 and by_k[k] <= eps]
    k_design = stable[0] if stable else None
    return {"eps": eps, "by_k": rows, "k_design": k_design}


if __name__ == "__main__":
    # Quick self-check demonstrating the decision logic.
    sample = [["C1", "C1", "C1"], ["C1", "C2", "C1"], ["novel", "novel", "C1"]]
    print("majority         :", [majority_vote(r) for r in sample])
    print("consensus        :", [consensus_decision(r) for r in sample])
    print("fleiss kappa     :", round(fleiss_kappa(sample), 4))
    print("loop stability   :", leave_one_out_stability(sample))