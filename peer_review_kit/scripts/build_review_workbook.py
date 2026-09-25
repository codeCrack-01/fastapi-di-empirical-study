"""scripts/build_review_workbook.py — build the peer-review Excel workbook.

Reads the compiled review table (analysis/out/review/review.tsv) plus the raw
judge chunks (pod_results/remote/results/chunk_1*.jsonl) and produces:

    analysis/out/review/peer_review.xlsx

One row per 327 sample repo with: metadata, LLM verdict summary, example &
evidence links, the LLM no-DI reason (for zero-DI repos), two reviewer-verdict
columns (MY / PEER) with data-validation dropdowns, a FINAL column (formula:
equal verdicts -> shown, differing -> "CONFLICTED", else pending), and notes.
"""
from __future__ import annotations

import csv
import json
import random as _random
from pathlib import Path

try:
    from openpyxl import Workbook
    from openpyxl.formatting.rule import CellIsRule
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.utils import get_column_letter
    from openpyxl.worksheet.datavalidation import DataValidation
except ImportError:  # pragma: no cover
    raise SystemExit("openpyxl required: .venv/bin/pip install openpyxl")

ROOT = Path(__file__).resolve().parents[1]
REVIEW_TSV = ROOT / "analysis" / "out" / "review" / "review.tsv"
RESULTS_DIR = ROOT / "pod_results" / "remote" / "results"
REPORTS_DIR = ROOT / "corpus" / "reports"
OUT = ROOT / "analysis" / "out" / "review" / "peer_review.xlsx"

VERDICTS = ["Agree with LLM", "Override"]
SEED = 42

PRE = ["repo", "stratum", "weight", "quadrant", "stars", "github_url", "commit_sha"]
LLM = ["llm_n_di", "llm_fingerprints", "llm_pass1_obs", "llm_pass2_recon",
       "llm_pass2_overturn", "llm_pass2_missed", "example_url", "evidence"]
REV = ["MY_VERDICT", "PEER_VERDICT", "FINAL_VERDICT", "NOTES"]
COLS = PRE + ["star_source", "labels_summary"] + LLM + ["llm_no_di_reason"] + REV


def norm(v: str) -> str:
    return (v or "").replace("__", "/", 1)


def load_rows() -> list[dict]:
    with REVIEW_TSV.open(encoding="utf-8") as fh:
        rows = list(csv.DictReader(fh, delimiter="\t"))
    out = []
    for r in rows:
        s = {"repo": r["repo"], "stratum": r["stratum"], "weight": r.get("weight"),
             "quadrant": r["quadrant"], "stars": r.get("stars", ""),
             "github_url": f"https://github.com/{r['repo']}",
             "commit_sha": (r.get("commit_sha") or ""),
             "star_source": r.get("star_source", ""),
             "labels_summary": (f"known={r.get('n_known', 0)} variant={r.get('n_variant', 0)} "
                                f"false_pos={r.get('n_false_pos', 0)} novel={r.get('n_novel', 0)}"),
             "llm_n_di": r.get("n_di_nodes", 0),
             "llm_fingerprints": r.get("fingerprints", ""),
             "llm_pass1_obs": r.get("pass1_n_obs", 0),
             "llm_pass2_recon": r.get("pass2_n_recon", 0),
             "llm_pass2_overturn": r.get("pass2_n_overturn", 0),
             "llm_pass2_missed": r.get("pass2_n_missed", 0),
             "example_url": "", "evidence": "", "llm_no_di_reason": "",
             "MY_VERDICT": "", "PEER_VERDICT": "", "FINAL_VERDICT": "", "NOTES": ""}
        out.append(s)
    return out


def enrich(rows: list[dict]) -> None:
    rcs: dict[str, dict] = {}
    for f in sorted(RESULTS_DIR.glob("chunk_1*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            d = json.loads(line)
            rcs[norm(d.get("repo"))] = d
    by = {r["repo"]: r for r in rows}
    for repo, rc in rcs.items():
        r = by.get(repo)
        if not r:
            continue
        n = r.get("llm_n_di")
        if not (n and str(n).strip().isdigit() and int(n) > 0):
            p1c = (rc.get("pass1") or {}).get("parsed", {}).get("comment") or ""
            p2c = (rc.get("pass2") or {}).get("parsed", {}).get("comment") or ""
            r["llm_no_di_reason"] = (p1c or p2c or "").strip()
        p2 = (rc.get("pass2") or {}).get("parsed", {})
        rec = (p2.get("reconciliations") or [])
        if rec:
            for x in rec:
                cit = x.get("citation") or {}
                if cit.get("file"):
                    r["example_url"] = f"https://github.com/{repo}/blob/{r['commit_sha'] or ''}/{(cit.get('file') or '').lstrip('/')}#L{cit.get('line', '')}"
                    break
    # evidence page path
    for r in rows:
        q = r.get("quadrant") or "Q?"
        r["evidence"] = f"{q}/{r['repo'].replace('/', '__')}/review.md"


def write_xlsx(rows: list[dict]) -> None:
    wb = Workbook()
    ws = wb.active
    ws.title = "repos"
    header_fill = PatternFill("solid", fgColor="1F4E79")
    header_font = Font(bold=True, color="FFFFFF")
    llm_fill = PatternFill("solid", fgColor="EAF1F8")
    rev_fill = PatternFill("solid", fgColor="FFF7E6")
    final_fill = PatternFill("solid", fgColor="FDF2F2")
    for c, name in enumerate(COLS, 1):
        cell = ws.cell(row=1, column=c, value=name)
        cell.font = header_font
        cell.fill = header_fill
    for i, r in enumerate(rows, 2):
        for c, name in enumerate(COLS, 1):
            v = r.get(name, "")
            cell = ws.cell(row=i, column=c, value=("" if v is None else v))
            if name.startswith("llm_") or name == "labels_summary":
                cell.fill = llm_fill
            if name in ("MY_VERDICT", "PEER_VERDICT", "NOTES"):
                cell.fill = rev_fill
            if name == "FINAL_VERDICT":
                cell.fill = final_fill
        ws.cell(row=i, column=COLS.index("github_url") + 1).hyperlink = r["github_url"]
        url = r.get("example_url")
        if url:
            cell = ws.cell(row=i, column=COLS.index("example_url") + 1)
            cell.hyperlink = url
            cell.font = Font(color="0563C1", underline="single")
    # FINAL formula
    myc = get_column_letter(COLS.index("MY_VERDICT") + 1)
    peerc = get_column_letter(COLS.index("PEER_VERDICT") + 1)
    finc = get_column_letter(COLS.index("FINAL_VERDICT") + 1)
    for i in range(2, len(rows) + 2):
        ws.cell(row=i, column=COLS.index("FINAL_VERDICT") + 1).value = (
            f'=IF(OR({myc}{i}="",{peerc}{i}=""),"",IF({myc}{i}={peerc}{i},{myc}{i},"CONFLICTED"))')
    # data validation dropdowns
    dv = DataValidation(type="list", formula1='"' + ",".join(VERDICTS) + '"', allow_blank=True)
    dv.error = "Choose Agree with LLM or Override"
    dv.errorTitle = "Invalid verdict"
    ws.add_data_validation(dv)
    dv.add(f"{myc}2:{myc}{len(rows) + 1}")
    dv.add(f"{peerc}2:{peerc}{len(rows) + 1}")
    # conditions: highlight CONFLICTED + any Override row in MY/PEER
    ws.conditional_formatting.add(
        f"{finc}2:{finc}{len(rows) + 1}",
        CellIsRule(operator="equal", formula=['"CONFLICTED"'],
                   fill=PatternFill("solid", fgColor="FFC7CE"),
                   font=Font(color="9C0006", bold=True)))
    for cname in ("MY_VERDICT", "PEER_VERDICT"):
        c = get_column_letter(COLS.index(cname) + 1)
        ws.conditional_formatting.add(
            f"{c}2:{c}{len(rows) + 1}",
            CellIsRule(operator="equal", formula=['"Override"'],
                       fill=PatternFill("solid", fgColor="FFEB9C")))
    for c, name in enumerate(COLS, 1):
        width = 52 if name in ("labels_summary", "llm_no_di_reason") else (
            34 if name in ("example_url", "evidence") else 16)
        ws.column_dimensions[get_column_letter(c)].width = width
    ws.freeze_panes = "A2"
    ws.auto_filter.ref = f"A1:{get_column_letter(len(COLS))}{len(rows) + 1}"
    # wrap long cells
    for c in (name for name in ("llm_no_di_reason", "NOTES")):
        col = get_column_letter(COLS.index(c) + 1)
        for i in range(2, len(rows) + 2):
            ws.cell(row=i, column=COLS.index(c) + 1).alignment = Alignment(wrap_text=True, vertical="top")
    # assignments reference sheet
    asheet = wb.create_sheet("reviewer split (reference)")
    asheet.cell(row=1, column=1, value="This sheet is informational only. The recommended design: both reviewers")
    asheet.cell(row=2, column=1, value="review ALL 327 rows; FINAL resolves agreement. Cohen's kappa is computed")
    asheet.cell(row=3, column=1, value="over all 327 paired verdicts afterwards (scripts/cohens_kappa.py).")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    wb.save(OUT)
    print(f"[workbook] wrote {OUT} ({len(rows)} rows)")


def main() -> int:
    rows = load_rows()
    enrich(rows)
    write_xlsx(rows)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())