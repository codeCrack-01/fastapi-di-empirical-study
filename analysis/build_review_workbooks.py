"""analysis/build_review_workbooks.py — build the Arm 1 / 2a / 2b review workbooks.

Reproduces the draws fixed in `docs/audit_preregistration.md` (branch
`prereg/census-validation`, commit 670af3b). The frame and draw SHA-256 values
are asserted on every run: if a draw no longer matches the pre-registration,
this script fails rather than emitting a workbook for a different sample.

Frames (seed 20260928):
    Arm 1  zero-DI frame  804  fb466c1883a28fb7   draw n=80   3763e311dad256e2
    Arm 2a signal frame   23  e1f34ea893fb2cde   exhaustive
    Arm 2b has-DI frame 1375  fc7c5c6295899972   draw n=200  d497401503766ea6

Usage:
    .venv/bin/python analysis/build_review_workbooks.py
"""
from __future__ import annotations

import hashlib
import json
import random
from pathlib import Path

from openpyxl import Workbook
from openpyxl.styles import Alignment, Border, Font, PatternFill, Side
from openpyxl.utils import get_column_letter
from openpyxl.worksheet.datavalidation import DataValidation

ROOT = Path(__file__).resolve().parents[1]
CENSUS = ROOT / "analysis" / "out" / "census_input"
REPORTS = ROOT / "corpus" / "reports"
OUT = ROOT / "peer_review_kit"

SEED = 20260928
CORE_KEYS = ("depends_total", "security_total", "annotated_depends_total", "yield_dep_total")

# The wider list used only to *find candidates*; never to assign a verdict.
CANDIDATE_LIBS = {
    "dependency_injector", "injector", "punq", "lagom", "wired", "svcs", "antidote",
    "dishka", "aioinject", "kink", "fastapi_injector", "pyioc", "ioccontainer",
    "ioclib", "kani", "solitary", "wireup", "servicemanager", "thiriy", "morango",
    "asgi_container", "asyncdi", "python_dependency_injector", "fluid", "cervantes",
    "decopatch", "inject", "di", "svc",
}

# Imports worth a looker's attention, for the triage hint column.
INTERESTING = CANDIDATE_LIBS | {
    "starlette", "contextvars", "requests", "httpx", "aiohttp",
}

EXPECTED = {
    "arm1": {"frame": (804, "fb466c1883a28fb7"), "n": 80, "draw": "3763e311dad256e2"},
    "arm2a": {"frame": (23, "e1f34ea893fb2cde")},
    "arm2b": {"frame": (1375, "fc7c5c6295899972"), "n": 200, "draw": "d497401503766ea6"},
}

HDR_FILL = PatternFill("solid", fgColor="1F3864")
HDR_FONT = Font(color="FFFFFF", bold=True, size=10)
TRIAGE_FILL = PatternFill("solid", fgColor="FFF2CC")
LOCKED_FILL = PatternFill("solid", fgColor="EDEDED")
BORDER = Border(*(Side(style="thin", color="BFBFBF"),) * 4)


def digest(names: list[str]) -> str:
    return hashlib.sha256("\n".join(sorted(names)).encode()).hexdigest()[:16]


def load_corpus() -> dict[str, dict]:
    """Return full_name -> record for every labelled census pack."""
    out: dict[str, dict] = {}
    for f in sorted(CENSUS.glob("census_*.json")):
        d = json.loads(f.read_text())
        fn = d.get("full_name")
        if fn:
            out[fn] = d
    return out


def report_for(fn: str) -> dict | None:
    p = REPORTS / (fn.replace("/", "__") + ".json")
    return json.loads(p.read_text()) if p.exists() else None


def build_frames(corpus: dict[str, dict]) -> tuple[list[str], list[str], list[str]]:
    arm1: list[str] = []
    arm2b: list[str] = []
    arm2a: list[str] = []
    for fn, d in corpus.items():
        agg = d.get("aggregate") or {}
        core = sum(agg.get(k) or 0 for k in CORE_KEYS)
        rep = report_for(fn)
        files = (rep or {}).get("file_details") or []
        non_fastapi = sum(1 for e in files if e.get("non_fastapi_depends_sources"))
        callable_dep = sum(1 for e in files if e.get("callable_class_deps"))
        mods = {str(m).split(".")[0] for m in (d.get("census_payload") or {}).get("import_table") or {}}
        lib_hit = bool(d.get("di_lib_hits")) or bool(mods & CANDIDATE_LIBS)
        if non_fastapi or callable_dep or lib_hit:
            arm2a.append(fn)
        if core == 0 and not d.get("di_lib_hits"):
            arm1.append(fn)
        else:
            arm2b.append(fn)
    return arm1, arm2a, arm2b


def assert_preregistered(name: str, names: list[str], key: str) -> None:
    exp = EXPECTED[name][key]
    exp_n, exp_h = exp if isinstance(exp, tuple) else (None, exp)
    got_h = digest(names)
    bad = (exp_n is not None and len(names) != exp_n) or got_h != exp_h
    if bad:
        raise SystemExit(
            f"PRE-REGISTRATION MISMATCH for {name}/{key}\n"
            f"  expected {exp_n if exp_n is not None else '?'} repos, "
            f"sha256[:16] = {exp_h}\n"
            f"  got      {len(names)} repos, sha256[:16] = {got_h}\n"
            f"Refusing to build a workbook for a sample that is not the one "
            f"registered in docs/audit_preregistration.md."
        )
    print(f"  {name}/{key}: {len(names)} repos, sha256[:16]={got_h}  OK")


def triage_hint(fn: str, d: dict, rep: dict | None) -> str:
    files = (rep or {}).get("file_details") or []
    parts: list[str] = []
    nfs = [e for e in files if e.get("non_fastapi_depends_sources")]
    if nfs:
        mods = sorted({str(m).split(".")[0] for e in nfs for m in e["non_fastapi_depends_sources"]})
        parts.append("non-FastAPI Depends from: " + ", ".join(mods[:5]))
    cd = [e for e in files if e.get("callable_class_deps")]
    if cd:
        parts.append(f"callable-class deps in {len(cd)} file(s)")
    mods = {str(m).split(".")[0] for m in (d.get("census_payload") or {}).get("import_table") or {}}
    hits = sorted(mods & INTERESTING)
    if hits:
        parts.append("imports: " + ", ".join(hits[:6]))
    if d.get("di_lib_hits"):
        parts.append("di_lib_hits: " + ", ".join(sorted(map(str, d["di_lib_hits"]))[:5]))
    return "; ".join(parts) if parts else "no DI signal detected"


def style_header(ws, ncols: int) -> None:
    for c in range(1, ncols + 1):
        cell = ws.cell(row=1, column=c)
        cell.fill, cell.font = HDR_FILL, HDR_FONT
        cell.alignment = Alignment(vertical="center", horizontal="center", wrap_text=True)
    ws.row_dimensions[1].height = 30
    ws.freeze_panes = "A2"


def add_dropdown(ws, col_letter: str, options: str, first: int, last: int) -> None:
    dv = DataValidation(
        type="list",
        formula1=f'"{options}"',
        allow_blank=True,
        showDropDown=False,
        error="Choose one of the listed values.",
        errorTitle="Invalid verdict",
    )
    ws.add_data_validation(dv)
    dv.add(f"{col_letter}{first}:{col_letter}{last}")


def build_arm1(corpus: dict[str, dict], draw: list[str]) -> Path:
    wb = Workbook()
    ws = wb.active
    ws.title = "audit"
    cols = [
        ("#", 5), ("REPO", 30), ("COMMIT", 9), ("LINK", 34), ("AST_VERDICT", 11),
        ("TRIAGE HINT (not a verdict)", 52), ("VERDICT_A", 12),
        ("VERDICT_B", 12), ("FINAL", 11), ("NOTE", 40),
    ]
    ws.append([c[0] for c in cols])
    for i, (name, width) in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width
    style_header(ws, len(cols))

    for i, fn in enumerate(draw, start=1):
        d = corpus[fn]
        sha = (d.get("commit_sha") or "")[:8]
        link = f"https://github.com/{fn}/tree/{sha}" if sha else f"https://github.com/{fn}"
        ws.append([i, fn, sha, link, "S1", triage_hint(fn, d, report_for(fn)), "", "", "", ""])
        r = ws.max_row
        for c in (1, 3, 5, 7, 8, 9):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=r, column=5).fill = LOCKED_FILL
        ws.cell(row=r, column=6).fill = TRIAGE_FILL
        ws.cell(row=r, column=4).hyperlink = link
        ws.cell(row=r, column=4).font = Font(color="0563C1", underline="single")
        ws.cell(row=r, column=10).alignment = Alignment(vertical="top", wrap_text=True)
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).border = BORDER

    last = ws.max_row
    ws.cell(row=last, column=9).value = None
    for r in range(2, last + 1):
        a, b = f"G{r}", f"H{r}"
        ws.cell(row=r, column=9).value = f'=IF(OR({a}="",{b}=""),"",IF({a}={b},{a},"DISAGREE"))'
    ws.cell(row=1, column=9).value = "FINAL"

    add_dropdown(ws, "G", "yes,no,unclear", 2, last)
    add_dropdown(ws, "H", "yes,no,unclear", 2, last)

    gate = wb.create_sheet("gate")
    gate.append(["ARM 1 GATE — fixed before any rating occurred"])
    gate["A1"].font = Font(bold=True, size=12)
    for row in [
        ("", ""),
        ("Frame", "804 detected-zero-DI repos (sha256[:16] fb466c1883a28fb7)"),
        ("Draw", "80, seed 20260928 (sha256[:16] 3763e311dad256e2)"),
        ("Raters", "2, working independently"),
        ("Question", "Does this repository contain any dependency-injection mechanism of any kind?"),
        ("Responses", "yes / no / unclear  (unclear is a permitted answer)"),
        ("", ""),
        ("misses k", "95% upper bound", "decision"),
        (0, 0.046, "proceed; bound reportable as-is"),
        (1, 0.067, "proceed; bound reportable as-is"),
        (2, 0.087, "proceed; report the zero-DI share as a RANGE"),
        (3, 0.105, "proceed; report the zero-DI share as a RANGE"),
        (4, 0.122, "STOP — do not write any headline number"),
        (">=4", ">=0.122", "STOP — extend the detector first"),
        ("", ""),
        ("Rationale", "The exposure is the zero-DI/non-zero-DI boundary, which is most of the corpus, not the rare S3/S4 buckets. At a 12.2% false-negative rate the zero-DI share moves by roughly 7 points."),
    ]:
        gate.append(row)
    gate.column_dimensions["A"].width = 12
    gate.column_dimensions["B"].width = 26
    gate.column_dimensions["C"].width = 70
    for r in (9, 10, 11, 12, 13, 14):
        gate.cell(row=r, column=3).font = Font(bold=r in (13, 14))

    inst = wb.create_sheet("how_to")
    for line in [
        ["ARM 1 — HOW TO FILL THIS IN"],
        [""],
        ["1", "Fill ONLY your own column: rater A uses VERDICT_A, rater B uses VERDICT_B."],
        ["2", "Do not look at the other rater's column until both of you have finished all 80 rows."],
        ["3", "Read the repository, then record your own answer. Only afterwards compare with AST_VERDICT."],
        ["4", "The TRIAGE HINT column lists signals the extractor already noticed. It is a starting point, NOT an answer."],
        ["5", "Answer the question below. It is deliberately broader than 'does it use FastAPI Depends'."],
        ["", ""],
        ["THE QUESTION", ""],
        ["Does this repository contain any dependency-injection mechanism of any kind?", ""],
        ["", "This may be a FastAPI Depends, a container from another library, a hand-rolled", ""],
        ["", "Depends equivalent, a service-locator, or a request-scoped context object that", ""],
        ["", "assembles and passes dependencies itself. If you are unsure, answer 'unclear'.", ""],
        ["", ""],
        ["ANSWERS", ""],
        ["yes", "Some DI mechanism is present."],
        ["no", "No DI mechanism is present."],
        ["unclear", "You cannot tell. This is a real answer, not a failure."],
        ["", ""],
        ["NOTE", "Use this if a decision needs explaining, or if the repo is archived/moved/unavailable."],
    ]:
        inst.append(line)
    inst.column_dimensions["A"].width = 14
    inst.column_dimensions["B"].width = 88
    inst["A1"].font = Font(bold=True, size=12)
    inst["A8"].font = Font(bold=True)
    inst["A16"].font = Font(bold=True)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "AUDIT_80.xlsx"
    wb.save(path)
    return path


def build_arm2b(corpus: dict[str, dict], draw: list[str]) -> Path:
    """200 repos from the detected-has-DI frame, classified S2/S3/S4."""
    wb = Workbook()
    ws = wb.active
    ws.title = "prevalence"
    cols = [
        ("#", 5), ("REPO", 30), ("COMMIT", 9), ("LINK", 34), ("AST_VERDICT", 11),
        ("TRIAGE HINT (not a verdict)", 46), ("VERDICT_A", 12),
        ("VERDICT_B", 12), ("FINAL", 11), ("NOTE", 40),
    ]
    ws.append([c[0] for c in cols])
    for i, (_, width) in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width
    style_header(ws, len(cols))

    for i, fn in enumerate(draw, start=1):
        d = corpus[fn]
        sha = (d.get("commit_sha") or "")[:8]
        link = f"https://github.com/{fn}/tree/{sha}" if sha else f"https://github.com/{fn}"
        ws.append([i, fn, sha, link, "S2", triage_hint(fn, d, report_for(fn)), "", "", "", ""])
        r = ws.max_row
        for c in (1, 3, 5, 7, 8, 9):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=r, column=5).fill = LOCKED_FILL
        ws.cell(row=r, column=6).fill = TRIAGE_FILL
        ws.cell(row=r, column=4).hyperlink = link
        ws.cell(row=r, column=4).font = Font(color="0563C1", underline="single")
        ws.cell(row=r, column=10).alignment = Alignment(vertical="top", wrap_text=True)
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).border = BORDER
        ws.cell(row=r, column=9).value = f'=IF(OR(G{r}="",H{r}=""),"",IF(G{r}=H{r},G{r},"DISAGREE"))'

    last = ws.max_row
    add_dropdown(ws, "G", "S2,S3,S4,unclear", 2, last)
    add_dropdown(ws, "H", "S2,S3,S4,unclear", 2, last)

    inst = wb.create_sheet("how_to")
    for line in [
        ["ARM 2b — HOW TO FILL THIS IN"],
        [""],
        ["1", "Fill ONLY your own column: rater A uses VERDICT_A, rater B uses VERDICT_B."],
        ["2", "Do not look at the other rater's column until both of you have finished all 200 rows."],
        ["3", "Every repo here already uses FastAPI DI. The question is whether it ALSO does"],
        ["", "something else — a container, or hand-rolled wiring. Most of these are plain S2."],
        ["4", "The TRIAGE HINT column is a starting point, not an answer. A repo can have DI"],
        ["", "without any of the signals listed, and a listed signal can be a false lead."],
        ["", ""],
        ["WHAT TO CHOOSE", ""],
        ["S2", "Framework-native only. Depends / Security / Annotated, and nothing else."],
        ["S3", "Also has manual Python DI. A hand-rolled Depends equivalent, a service"],
        ["", "locator, or a request-scoped context object assembled in app.state or"],
        ["", "request.state and passed to handlers. The handler receives it explicitly."],
        ["S4", "Also imports an external container library (dependency_injector,"],
        ["", "injector, punq, dishka, ...). An import alone is enough for S4."],
        ["unclear", "You cannot tell from the code. A real answer, not a failure."],
        ["", ""],
        ["NOTE", "Record the file and construct that decided it. If a repo does both S3 and"],
        ["", "S4, choose S4 and say so in NOTE."],
    ]:
        inst.append(line)
    inst.column_dimensions["A"].width = 14
    inst.column_dimensions["B"].width = 88
    inst["A1"].font = Font(bold=True, size=12)
    inst["A9"].font = Font(bold=True)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "S3S4_200.xlsx"
    wb.save(path)
    return path


def build_arm2a(corpus: dict[str, dict], frame: list[str]) -> Path:
    """The signal-bearing repos, exhaustively. One rater, open taxonomy."""
    wb = Workbook()
    ws = wb.active
    ws.title = "candidates"
    cols = [
        ("#", 5), ("REPO", 30), ("COMMIT", 9), ("LINK", 34), ("WHY FLAGGED", 40),
        ("MECHANISM", 22), ("IS THIS DI?", 13), ("LIBRARY / MECHANISM NAME", 24),
        ("EVIDENCE (file:line)", 26), ("NOTE", 40),
    ]
    ws.append([c[0] for c in cols])
    for i, (_, width) in enumerate(cols, start=1):
        ws.column_dimensions[get_column_letter(i)].width = width
    style_header(ws, len(cols))

    for i, fn in enumerate(sorted(frame), start=1):
        d = corpus[fn]
        sha = (d.get("commit_sha") or "")[:8]
        link = f"https://github.com/{fn}/tree/{sha}" if sha else f"https://github.com/{fn}"
        hint = triage_hint(fn, d, report_for(fn))
        ws.append([i, fn, sha, link, hint, "", "", "", "", ""])
        r = ws.max_row
        for c in (1, 3, 7):
            ws.cell(row=r, column=c).alignment = Alignment(horizontal="center", vertical="center")
        ws.cell(row=r, column=5).fill = TRIAGE_FILL
        ws.cell(row=r, column=4).hyperlink = link
        ws.cell(row=r, column=4).font = Font(color="0563C1", underline="single")
        for c in (6, 8, 9, 10):
            ws.cell(row=r, column=c).alignment = Alignment(vertical="top", wrap_text=True)
        for c in range(1, len(cols) + 1):
            ws.cell(row=r, column=c).border = BORDER

    last = ws.max_row
    add_dropdown(ws, "F", "external container,hand-rolled Depends,service locator,"
                         "request-scoped context,callable class,DI framework,not DI,unclear", 2, last)
    add_dropdown(ws, "G", "yes,no,unclear", 2, last)

    inst = wb.create_sheet("how_to")
    for line in [
        ["ARM 2a — CANDIDATE CHARACTERISATION (one rater, no second opinion)"],
        [""],
        ["This arm has a different job from the others. You are not confirming a count;"],
        ["you are building the vocabulary the other arms will use. Work through the rows"],
        ["and, for each one, say what the mechanism actually IS."],
        [""],
        ["The row is in this sheet because the extractor or the import table raised a"],
        ["signal. Signals are cheap and imprecise: most of these will be 'not DI'."],
        ["That is a useful result. Do not stretch to find DI."],
        ["", ""],
        ["FILL IN", ""],
        ["MECHANISM", "The single best description of what you found."],
        ["IS THIS DI?", "yes if it genuinely injects dependencies; no if the signal was a false lead."],
        ["LIBRARY / NAME", "The container package, or the hand-rolled class/function name."],
        ["EVIDENCE", "file path and line, so the claim can be checked later."],
        ["NOTE", "Anything surprising, or why a signal did not pan out."],
        ["", ""],
        ["There is no kappa here and no second rater. This arm produces a rubric and a"],
        ["lower bound on prevalence — not a prevalence estimate. The 200-repo random"],
        ["draw (Arm 2b) is what gives a number with a confidence interval."],
    ]:
        inst.append(line)
    inst.column_dimensions["A"].width = 22
    inst.column_dimensions["B"].width = 86
    inst["A1"].font = Font(bold=True, size=12)

    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "S3S4_CANDIDATES.xlsx"
    wb.save(path)
    return path


def main() -> None:
    print("Loading census packs...")
    corpus = load_corpus()
    print(f"  {len(corpus)} labelled repositories\n")
    arm1, arm2a, arm2b = build_frames(corpus)
    print("Verifying against the pre-registration:")
    assert_preregistered("arm1", arm1, "frame")
    assert_preregistered("arm2a", arm2a, "frame")
    assert_preregistered("arm2b", arm2b, "frame")

    # One RNG stream, drawn in the registered order: Arm 1 first, then Arm 2b.
    rnd = random.Random(SEED)
    d1 = sorted(rnd.sample(sorted(arm1), EXPECTED["arm1"]["n"]))
    d2 = sorted(rnd.sample(sorted(arm2b), EXPECTED["arm2b"]["n"]))
    print()
    assert_preregistered("arm1", d1, "draw")
    assert_preregistered("arm2b", d2, "draw")
    print()

    for label, path in [
        ("Arm 1  audit  (80)", build_arm1(corpus, d1)),
        ("Arm 2a candidates (23)", build_arm2a(corpus, arm2a)),
        ("Arm 2b prevalence (200)", build_arm2b(corpus, d2)),
    ]:
        print(f"  {label:<26} {path.relative_to(ROOT)}  ({path.stat().st_size:,} bytes)")


if __name__ == "__main__":
    main()
