"""Generate per-repo predicted labels from reports_v0.5 using the frozen classifier."""
from __future__ import annotations
import json, glob, csv
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "extractor"))
from models import RepoReport
from verdict import classify_report

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "corpus" / "reports_v0.5"
OUT = ROOT / "analysis" / "out" / "corpus_labels_v0.5.csv"

rows = []
for p in sorted(REPORTS.glob("*.json")):
    d = json.loads(p.read_text())
    rep = RepoReport.model_validate(d)
    v = classify_report(rep)
    rows.append({"repo": rep.repo.name, "commit": rep.repo.commit_sha, "label": v.label})

with open(OUT, "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["repo", "commit", "label"])
    w.writeheader()
    w.writerows(rows)

from collections import Counter
print(Counter(r["label"] for r in rows))
print("total", len(rows))
print("wrote", OUT)