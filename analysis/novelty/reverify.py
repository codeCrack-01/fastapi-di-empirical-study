"""analysis/novelty/reverify.py — anchor-reverification gate before the definitive run.

Purpose: the panel was calibrated on anchors under one executor (machine/gguf/
quant/offload). If the definitive run happens on a DIFFERENT executor, or the
serving stack drifted, rater outputs can differ (DriftBench-style flips). So:

    1. re-run every anchor through the CURRENT executor exactly as selection did;
    2. compute per-rater agreement with the SELECTION-TIME anchor answers
       (novelty_selection records) — NOT with the gold label (we probe stability);
    3. if per-rater agreement < AGREEMENT_FLOOR (0.98) on ANY rater
       => the anchoring assumption breaks => report and mark re-selection needed.
       (0.98 chosen from anchor-reverification literature; overrides not allowed)

Also emits a cross-executor agreement table (selection vs current) for the paper.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Callable

OUT_DIR = Path(__file__).resolve().parent / "out"
AGREEMENT_FLOOR = 0.98


def run_reverify(
    *,
    panel_path: Path | str,
    selection_path: Path | str,
    host: str = "",
    out_path: Path | str | None = None,
    rater_factory: Callable[[list[str]], dict] | None = None,
) -> dict:
    """Run the gate. Returns result dict; raises RuntimeError on any breach."""
    from anchors import build_anchors
    from client import OllamaClient
    from executor import ExecutorProfile
    from prompt import parse_response, render_system, render_user

    panel = json.loads(Path(panel_path).read_text())
    sel = json.loads(Path(selection_path).read_text())
    anchors = build_anchors()

    if rater_factory:
        clients = rater_factory(panel["panel"])
    else:
        clients = {m: OllamaClient(model=m, host=host) for m in panel["panel"]}
    profile = ExecutorProfile.capture(list(clients)).to_dict()

    agreed: dict[str, dict] = {}
    for m, cli in clients.items():
        sel_pred = sel["rater_predictions"].get(m) or []
        cur_pred = [
            parse_response(cli.generate(render_system(), render_user(a.get("extractor_top") or a["id"], [a]))
                           .get("content", ""))["label"]
            for a in anchors
        ]
        baseline = sel_pred[:len(cur_pred)]
        agree = sum(1 for s, c in zip(baseline, cur_pred) if s == c)
        rate = agree / max(len(cur_pred), 1)
        agreed[m] = {"selection_agreement": round(rate, 4), "n": len(cur_pred)}

    breaches = {m: d for m, d in agreed.items() if d["selection_agreement"] < AGREEMENT_FLOOR}
    result = {
        "executor_now": profile,
        "agreement": agreed,
        "floor": AGREEMENT_FLOOR,
        "re_selection_needed": bool(breaches),
        "breaches": list(breaches),
    }
    out_path = Path(out_path or Path(panel_path).parent / "novelty_reverify.json")
    out_path.write_text(json.dumps(result, indent=2))

    print(f"[reverify] executor={profile.get('machine')} floor={AGREEMENT_FLOOR}")
    for m, d in agreed.items():
        flag = "" if d["selection_agreement"] >= AGREEMENT_FLOOR else "  <-- RE-SELECT"
        print(f"  {m}: {d['selection_agreement']:.2%}{flag}")
    if breaches:
        raise RuntimeError(f"anchor-reverification FAILED: {result['breaches']}")
    return result


def main():
    ap = argparse.ArgumentParser(description="Anchor-reverification gate")
    ap.add_argument("--panel", default=str(OUT_DIR / "novelty_panel.json"))
    ap.add_argument("--selection", default=str(OUT_DIR / "novelty_selection.json"))
    ap.add_argument("--host", default="")
    args = ap.parse_args()

    run_reverify(panel_path=args.panel, selection_path=args.selection, host=args.host)


if __name__ == "__main__":
    main()