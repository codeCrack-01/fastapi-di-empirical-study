"""analysis/novelty/select_panel.py — objective, pre-registered rater selection.

This is the measurement-driven replacement for "pick three models you like".
Sequence:

    1. ELIGIBILITY (hard rules, no taste):
         open weights / license, fits the given executor, not a drifting alias.
       Implemented as a candidate list + optional size/VRAM filter.
    2. ANCHOR SCORING: each candidate runs the constructed anchor set (anchors.py)
       through the pinned prompt; per-anchor label vs expected label -> accuracy,
       per-construct recall, and a confusion matrix.
    3. COMPETENCE FLOOR: pre-registered minimum anchor accuracy (default .8);
       candidates below floor are dropped (Condorcet: p<=0.5 members are a
       liability).
    4. ERROR-DIVERSITY: pairwise disagreement rate (1 - Cohen's kappa) between
       surviving pairs; we want complementary error patterns — NOT merely
       different families.
    5. PANEL SELECTION: greedy forward selection maximizing ensemble anchor
       accuracy under a pairwise-agreement penalty, honoring the floor.
    6. PANEL SIZE k: leave-one-out stability (consensus.py) on the anchors —
       smallest k whose single-drop flip_rate <= eps. Hardware never decides k.

Outputs (analysis/novelty/out/):
    novelty_leaderboard.csv  every candidate: accuracy, per-label F1, tokens/s
    novelty_panel.json       selected panel: raters, k, tau, eps, profile
    novelty_selection.md     human-readable justification

Runners are injected as ``raters: dict[model -> Callable[[str,str], dict]]`` so
this is testable offline with fake raters and live with OllamaClient. No
network is required at import time.
"""
from __future__ import annotations

import argparse
import csv
import json
import statistics as st
from pathlib import Path
from typing import Callable

OUT_DIR = Path(__file__).resolve().parent / "out"

LABEL_ALIASES = {
    "C1": "C1", "C2": "C2", "C3": "C3", "C4": "C4",
    "EX2": "EX2", "Z": "Z",
    "external_di": "external_di", "external": "external_di",
    "false_pos": "false_pos", "false_positive": "false_pos",
}


def normalize_anchor_label(label: str) -> str:
    return LABEL_ALIASES.get(label.strip().lower(), label.strip())


def _confusion_matrix(expected: list[str], actual: list[str]) -> dict[str, dict[str, int]]:
    labels = sorted(set(expected) | set(actual))
    mat = {lbl: {o: 0 for o in labels} for lbl in labels}
    for e, a in zip(expected, actual):
        mat[e][a] = mat[e].get(a, 0) + 1
    return mat


def per_label_f1(mat: dict[str, dict[str, int]]) -> dict[str, float]:
    out: dict[str, float] = {}
    labels = list(mat.keys())
    for lbl in labels:
        tp = mat[lbl].get(lbl, 0)
        fp = sum(mat[o].get(lbl, 0) for o in labels if o != lbl)
        fn = sum(mat[lbl].get(o, 0) for o in labels if o != lbl)
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / (tp + fn) if (tp + fn) else 0.0
        out[lbl] = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return out


def score_rater(rater: Callable[[str, str], dict], anchors: list[dict]) -> dict:
    """Run one candidate on the full anchor set; return accuracy + confusions."""
    from prompt import parse_response, render_system, render_user
    expected: list[str] = []
    actual: list[str] = []
    for a in anchors:
        sys_txt = render_system()
        usr_txt = render_user(a.get("extractor_top") or a["id"], [{k: v for k, v in a.items() if k != "source"}])
        response = rater(sys_txt, usr_txt)
        predicted = normalize_anchor_label(parse_response(response.get("content", ""))["label"])
        expected.append(a["label"])
        actual.append(predicted)
    acc = sum(1 for e, a in zip(expected, actual) if e == a) / len(expected)
    mat = _confusion_matrix(expected, actual)
    return {
        "accuracy": round(acc, 4),
        "f1": per_label_f1(mat),
        "confusion": mat,
        "n_anchors": len(expected),
        "predicted": actual,
        "expected": expected,
    }


def greedy_panel(candidates: dict[str, dict], k: int, penalty: float = 0.5) -> list[str]:
    """Greedy forward selection of up to ``k`` members.

    ``candidates`` maps model -> scored result. Selection criterion per
    candidate at each step:

        score = accuracy - penalty * max_{picked}(E-overlap with picked)

    where E-overlap = |E_candidate ∩ E_picked| / max(|E_picked|, 1) is the
    share of the already-picked panel's anchor ERRORS (pred != expected) that
    this candidate also gets wrong. This rewards members that err on DIFFERENT
    items (complementary error patterns), not mere family diversity.
    """
    if not candidates:
        return []
    pool = list(candidates)

    def _errors(m: str) -> set[int]:
        preds = candidates[m]["predicted"]
        return {i for i, p in enumerate(preds) if p != candidates[m]["expected"][i]}

    picked: list[str] = []
    while len(picked) < k and pool:
        best, best_score = None, -1.0
        for cand in pool:
            acc = candidates[cand]["accuracy"]
            if not picked:
                score = acc
            else:
                err_c = _errors(cand)
                overlap = max((len(err_c & _errors(p)) / max(len(_errors(p)), 1)) for p in picked)
                score = acc - penalty * overlap
            if score > best_score:
                best, best_score = cand, score
        picked.append(best)
        pool.remove(best)
    return picked


def run_selection(
    *,
    anchors: list[dict] | None = None,
    pool: list[str] | None = None,
    kv_file: str | None = None,
    host: str = "",
    floor: float = 0.80,
    eps: float = 0.02,
    max_k: int = 5,
    out_dir: Path | str | None = None,
    apply: bool = True,
    rater_factory: Callable[[list[str]], dict] | None = None,
) -> dict:
    """Run the full objective selection and write artifacts. Returns panel dict."""
    from anchors import build_anchors
    from consensus import _loo_stability_with_threshold

    anchors = anchors or build_anchors()
    out_dir = Path(out_dir or OUT_DIR)
    out_dir.mkdir(parents=True, exist_ok=True)

    if kv_file:
        kv = json.loads(Path(kv_file).read_text())
        leaderboard: dict[str, dict] = {}
        for m, d in kv.items():
            expected = [a["label"] for a in anchors]
            if len(d.get("predicted", [])) != len(expected):
                print(f"[select_panel] WARNING: {m} predicted len mismatch; skipping")
                continue
            leaderboard[m] = dict(d)
            leaderboard[m]["expected"] = expected
            leaderboard[m]["predicted"] = list(d["predicted"])
            leaderboard[m]["accuracy"] = d.get("accuracy") or round(
                sum(1 for e, p in zip(expected, leaderboard[m]["predicted"]) if e == p) / len(expected), 4)
        records: list[dict] = []
    else:
        records: list[dict] = []
        pool = pool or []
        if rater_factory:
            clients = rater_factory(pool)
            raters = {m: (lambda sys_txt, usr_txt, c=clients[m]: c.generate(sys_txt, usr_txt)) for m in pool}
            leaderboard = {m: score_rater(r, anchors) for m, r in raters.items()}
        elif apply:
            from client import OllamaClient
            def make_call(model: str) -> Callable[[str, str], dict]:
                client = OllamaClient(model=model, host=host)

                def call(system: str, user: str) -> dict:
                    rec = client.generate(system, user)
                    records.append(rec)
                    return rec
                return call

            raters = {m: make_call(m) for m in pool}
            if not raters:
                raise SystemExit("[select_panel] --apply requires --pool")
            leaderboard = {m: score_rater(r, anchors) for m, r in raters.items()}
        else:
            # Offline rehearsal with deterministic fake raters (no network).
            import random
            rnd = random.Random(7)
            leaderboard = {}
            expected = [a["label"] for a in anchors]
            for m in pool or ["fake-qwen", "fake-llama", "fake-deepseek", "fake-glm", "fake-phi"]:
                skill = rnd.uniform(0.72, 0.96)
                predicted = [
                    e if rnd.random() < skill else rnd.choice(["C1", "C2", "C3", "EX2", "novel", "variant"])
                    for e in expected
                ]
                leaderboard[m] = {
                    "accuracy": round(sum(1 for e, p in zip(expected, predicted) if e == p) / len(expected), 4),
                    "n_anchors": len(expected),
                    "predicted": predicted,
                    "expected": expected,
                    "f1": {}, "confusion": {},
                }
            print("[select_panel] offline rehearsal (no model called); use --apply for live.")

    # competence floor
    qualified = {m: s for m, s in leaderboard.items() if s["accuracy"] >= floor}
    # select up to max_k members, then trim by leave-one-out stability
    panel = greedy_panel(qualified, max_k)

    if panel:
        # transpose: consensus expects item-major (N items x K raters),
        # we have rater-major lists.
        preds_t = list(zip(*(leaderboard[m]["predicted"] for m in panel)))
        loo = _loo_stability_with_threshold(preds_t, eps)
        # smallest stable k >= 3 (odd panels give clean majority tie-breaking)
        stable = [row["k"] for row in sorted(loo["by_k"], key=lambda r: r["k"]) if row["k"] >= 3 and row["k_stable"]]
        k_design = stable[0] if stable else len(panel)
    else:
        loo = {"k_design": None, "by_k": []}
        k_design = 0

    k_final = max(min(k_design, len(panel)), 0)
    panel_final = panel[:k_final]

    with (out_dir / "novelty_leaderboard.csv").open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["model", "accuracy", "qualified", "n", "f1_macro"])
        w.writeheader()
        for m, s in leaderboard.items():
            f1 = s.get("f1") or {}
            macro = round(st.mean(f1.values()), 4) if f1 else ""
            w.writerow({"model": m, "accuracy": s["accuracy"],
                        "qualified": m in qualified, "n": s.get("n_anchors", ""), "f1_macro": macro})

    panel_out = {
        "floor": floor,
        "eps": eps,
        "candidates": list(leaderboard.keys()),
        "qualified": list(qualified.keys()),
        "panel": panel_final,
        "k_reported": len(panel_final),
        "k_design": k_design,
        "loo": loo["by_k"],
        "records": records,
    }
    (out_dir / "novelty_panel.json").write_text(json.dumps(panel_out, indent=2))

    # selection-time rater predictions (anchor answers) — consumed by reverify.py
    (out_dir / "novelty_selection.json").write_text(json.dumps({
        "executor": host or "default",
        "anchors": [a["id"] for a in anchors],
        "rater_predictions": {m: s.get("predicted", []) for m, s in leaderboard.items()},
    }, indent=2))

    lines = [
        "# Novelty panel selection",
        "",
        f"- Candidate pool: {list(leaderboard)}",
        f"- Anchor set: {len(anchors)} constructed items (no humans)",
        f"- Competence floor: accuracy >= {floor}",
        f"- Panel (greedy, max-k={max_k}): {panel_final}",
        f"- Leave-one-out stability eps={eps}: k_design={k_design}, reported k={len(panel_final)}",
        "",
        "| model | accuracy | qualified |",
        "|---|---|---|",
    ]
    for m, s in sorted(leaderboard.items(), key=lambda kv: -kv[1]["accuracy"]):
        lines.append(f"| {m} | {s['accuracy']} | {'yes' if m in qualified else 'no'} |")
    (out_dir / "novelty_selection.md").write_text("\n".join(lines) + "\n")
    print("\n".join(lines[4:11]))
    print(f"[select_panel] artifacts -> {out_dir}/")
    return panel_out


def main():
    ap = argparse.ArgumentParser(description="Select LLM rater panel objectively")
    ap.add_argument("--pool", nargs="+", default=[],
                    help="candidate OLLAMA model names (hard-eligible pool)")
    ap.add_argument("--kv-file", default=None,
                    help="JSON file mapping model -> score (predicted/expected/accuracy)")
    ap.add_argument("--k", type=int, default=3, help="starting k (was 3; actual k via leave-one-out)")
    ap.add_argument("--max-k", type=int, default=5)
    ap.add_argument("--eps", type=float, default=0.02, help="flip-rate eps")
    ap.add_argument("--floor", type=float, default=0.80, help="anchor-accuracy floor")
    ap.add_argument("--apply", action="store_true",
                    help="actually call Ollama for each pool model (live)")
    ap.add_argument("--host", default="", help="Ollama host override for live runs")
    ap.add_argument("--out", default=str(OUT_DIR))
    args = ap.parse_args()

    run_selection(
        pool=args.pool,
        kv_file=args.kv_file,
        host=args.host,
        floor=args.floor,
        eps=args.eps,
        max_k=args.max_k,
        out_dir=args.out,
        apply=args.apply,
    )


if __name__ == "__main__":
    main()