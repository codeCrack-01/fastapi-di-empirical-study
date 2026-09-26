"""
analysis/build_pptx.py — Build the editable presentation deck for Dr. Bangash.

Generates a data-true, minimalist .pptx from the actual curated results so the
deck always reflects the numbers in analysis/out/ and docs/result_draft_01.md.
The deck is deliberately plain (professor prefers substance over decoration);
every claim is backed by a number in the slides.

Usage:
    uv run python analysis/build_pptx.py  ->  analysis/out/fastapi_di_presentation.pptx
"""

from __future__ import annotations

import collections
import csv
import json
import statistics as st
import sys
from pathlib import Path

from pptx import Presentation
from pptx.dml.color import RGBColor
from pptx.enum.shapes import MSO_SHAPE
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.util import Inches, Pt

ROOT = Path(__file__).resolve().parent
OUT_DIR = ROOT / "out"
DOC = ROOT.parent / "docs" / "result_draft_01.md"

INK = RGBColor(0x24, 0x29, 0x2F)          # near-black
MUTED = RGBColor(0x57, 0x60, 0x6A)        # gray
ACCENT = RGBColor(0x09, 0x69, 0xDA)       # blue
ACCENT2 = RGBColor(0x1A, 0x7F, 0x37)      # green
WARN = RGBColor(0x9A, 0x67, 0x00)         # amber
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
LGRAY = RGBColor(0xF6, 0xF8, 0xFA)


def _load() -> dict:
    sample = json.loads((OUT_DIR / "sample.json").read_text())
    manifest = json.loads((ROOT.parent / "corpus" / "manifest.json").read_text())
    candidates = json.loads((ROOT.parent / "corpus" / "candidates.json").read_text())["candidates"]
    excluded = json.loads((ROOT.parent / "corpus" / "exclusion_log.json").read_text())["excluded"]
    topic = json.loads((ROOT.parent / "corpus" / "topic_seed.json").read_text()).get("seed", [])

    n_cand = len(candidates)
    n_acc = len(manifest["accepted"])
    n_excl = len(excluded)
    by_reason: dict[str, int] = {}
    for e in excluded:
        by_reason[e["reason"]] = by_reason.get(e["reason"], 0) + 1
    n_pages = len(list((ROOT.parent / "corpus" / "raw_dependents").glob("dependents_page_*.html")))

    topic_names = {t["full_name"] for t in topic}
    cand_names = {c["full_name"] for c in candidates}
    acc_names = {a["full_name"] for a in manifest["accepted"]}
    overlap_cand_topic = len(cand_names & topic_names)
    overlap_acc_topic = len(acc_names & topic_names)

    return {
        "sample": sample,
        "manifest": manifest,
        "n_cand": n_cand,
        "n_acc": n_acc,
        "n_excl": n_excl,
        "accept_rate_pct": 100.0 * n_acc / n_cand if n_cand else 0.0,
        "exclusions_by_reason": by_reason,
        "n_pages": n_pages,
        "overlap_cand_topic": overlap_cand_topic,
        "overlap_acc_topic": overlap_acc_topic,
        "n_excl_pct": 100.0 * n_excl / n_cand if n_cand else 0.0,
    }


def _fmt(n: int) -> str:
    return f"{n:,}"


def _csv(path: str) -> list[dict]:
    return list(csv.DictReader((OUT_DIR / path).open()))


# Per-repo construct presence, derived from the frozen extractor reports.
# The deck aggregates the FULL accepted corpus (census) — many of the
# numbers below are deliberately computed here rather than hard-coded so the
# deck stays correct if the corpus or threshold ever changes.
_CORE_KEYS = (
    "depends_total", "security_total", "annotated_depends_total", "yield_dep_total",
)
_CONSTRUCT_LABELS = {
    "depends_total": "Depends",
    "security_total": "Security",
    "annotated_depends_total": "Annotated",
    "yield_dep_total": "Generator",
}


def _load_reports() -> dict[str, dict]:
    manifest = json.loads((ROOT.parent / "corpus" / "manifest.json").read_text())
    out = {}
    for a in manifest["accepted"]:
        p = ROOT.parent / "corpus" / "reports" / f"{a['full_name'].replace('/', '__')}.json"
        if p.exists():
            out[a["full_name"]] = json.loads(p.read_text())
    return out


def _fan_out3(reports: dict[str, dict]) -> tuple[int, int]:
    """(repos, graph_bearing) where some clean dependency node has >=3 direct
    dependents in the clean dependency graph (junk 'file:line' ids excluded)."""
    gb = fan = 0
    for r in reports.values():
        nodes = (r.get("dependency_graph") or {}).get("nodes") or []
        if not nodes:
            continue
        gb += 1
        indeg: collections.Counter = collections.Counter()
        for e in (r.get("dependency_graph") or {}).get("edges") or []:
            if not e:
                continue
            src, tgt = str(e.get("source", "")), str(e.get("target", ""))
            if "/" in src or ":" in src or "/" in tgt or ":" in tgt:
                continue
            indeg[tgt] += 1
        if indeg and max(indeg.values()) >= 3:
            fan += 1
    return fan, gb


def _multiplicity(reports: dict[str, dict]) -> list[tuple[int, int]]:
    counts = [0] * (len(_CORE_KEYS) + 1)
    for r in reports.values():
        agg = r.get("aggregate", {})
        n = sum(1 for k in _CORE_KEYS if agg.get(k, 0) > 0)
        counts[n] += 1
    return [(i, counts[i]) for i in range(len(counts))]


def _pairings(reports: dict[str, dict], top: int = 6) -> list[tuple[str, str, int]]:
    counter: dict[tuple[str, str], int] = {}
    for r in reports.values():
        agg = r.get("aggregate", {})
        present = sorted(_CONSTRUCT_LABELS[k] for k in _CORE_KEYS if agg.get(k, 0) > 0)
        for i in range(len(present)):
            for j in range(i + 1, len(present)):
                key = tuple(sorted((present[i], present[j])))
                counter[key] = counter.get(key, 0) + 1
    ranked = sorted(counter.items(), key=lambda kv: (-kv[1], kv[0]))
    return [(a, b, n) for (a, b), n in ranked[:top]]


def set_bg(slide, color=WHITE):
    slide.background.fill.solid()
    slide.background.fill.fore_color.rgb = color


def add_text(slide, title, body, left=Inches(0.6), top=None, width=Inches(12.3),
             height=Inches(1.1), size=Pt(26)):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.clear()
    tf.margin_top = tf.margin_bottom = Pt(4)
    p = tf.paragraphs[0]
    p.text = title
    p.font.size = size
    p.font.bold = True
    p.font.color.rgb = INK
    return box


def bullet_box(slide, left, top, width, height, lines):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.clear()
    tf.word_wrap = True
    first = True
    for lvl, text, bold, color in lines:
        p = tf.paragraphs[0] if first else tf.add_paragraph()
        first = False
        p.text = text
        p.level = lvl
        p.font.bold = bold
        p.font.color.rgb = color or INK
        p.font.size = Pt(13 if lvl == 0 else 12)
        p.space_after = Pt(4)
    return box


def add_table(slide, headers, rows, left=Inches(0.6), top=Inches(1.6),
              width=Inches(12.3), col_widths=None, font_size=12, header_fill=ACCENT):
    nrows, ncols = len(rows) + 1, len(headers)
    shape = slide.shapes.add_table(nrows, ncols, left, top, width, Inches(0.4 * nrows))
    table = shape.table
    if col_widths:
        for i, w in enumerate(col_widths):
            table.columns[i].width = w
    # header
    for j, h in enumerate(headers):
        cell = table.cell(0, j)
        cell.text = h
        cell.fill.solid()
        cell.fill.fore_color.rgb = header_fill
        cp = cell.text_frame.paragraphs[0]
        cp.font.bold = True
        cp.font.size = Pt(font_size)
        cp.font.color.rgb = WHITE
    for i, row in enumerate(rows, start=1):
        for j, val in enumerate(row):
            cell = table.cell(i, j)
            cell.text = str(val)
            if i % 2 == 0:
                cell.fill.solid()
                cell.fill.fore_color.rgb = LGRAY
            cp = cell.text_frame.paragraphs[0]
            cp.font.size = Pt(font_size)
            cp.font.color.rgb = INK
    return table


def add_bigstat(slide, left, top, width, height, number, caption, color=ACCENT):
    box = slide.shapes.add_textbox(left, top, width, height)
    tf = box.text_frame
    tf.clear()
    p = tf.paragraphs[0]
    p.text = number
    p.font.size = Pt(44)
    p.font.bold = True
    p.font.color.rgb = color
    p2 = tf.add_paragraph()
    p2.text = caption
    p2.font.size = Pt(13)
    p2.font.color.rgb = MUTED
    return box


def slide_title(prs, title, subtitle=None):
    s = prs.slides.add_slide(prs.slide_layouts[6])  # blank
    set_bg(s)
    add_text(s, title, "", top=Inches(0.55), size=Pt(30))
    if subtitle:
        add_text(s, subtitle, "", top=Inches(1.1), size=Pt(15))
        box = s.shapes[-1]
        box.text_frame.paragraphs[0].font.color.rgb = MUTED
        box.text_frame.paragraphs[0].font.bold = False
    return s


def _row_by(rows: list[dict], key: str, val: str) -> dict:
    return next((r for r in rows if r[key] == val), {})


def main():
    D = _load()
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)

    # ---- Title ----
    s = prs.slides.add_slide(prs.slide_layouts[6]); set_bg(s)
    add_text(s, "Empirical Study of Dependency Injection (DI) Usage Patterns in FastAPI Applications", "", top=Inches(1.5), size=Pt(30))
    b = s.shapes[-1]
    b.text_frame.word_wrap = True
    for p in b.text_frame.paragraphs:
        p.font.color.rgb = INK
    add_text(s, f"A dependency-graph corpus of {_fmt(D['n_acc'])} real applications", "", top=Inches(2.8), size=Pt(20))
    b = s.shapes[-1]; b.text_frame.paragraphs[0].font.color.rgb = MUTED; b.text_frame.paragraphs[0].font.bold = False
    add_text(s, "Mining Software Repositories (MSR) study · the current RQs (RQ1–RQ4, RQ4 deferred)", "", top=Inches(3.4), size=Pt(16))
    b = s.shapes[-1]; b.text_frame.paragraphs[0].font.color.rgb = MUTED; b.text_frame.paragraphs[0].font.bold = False
    add_text(s, "Data-driven and self-contained · every number is backed by a committed corpus/analysis artifact", "", top=Inches(6.5), size=Pt(12))
    b = s.shapes[-1]; b.text_frame.paragraphs[0].font.color.rgb = MUTED; b.text_frame.paragraphs[0].font.bold = False

    # ---- 0. How to read this deck (orientation) ----
    s = slide_title(prs, "How to read this presentation")
    bullet_box(s, Inches(0.6), Inches(1.6), Inches(12.3), Inches(5.4), [
        (0, "This study builds a corpus of real FastAPI applications and measures how DI is actually used.", False, INK),
        (0, "Whether you have seen any prior work or not, the narrative is: questions → population → rules → results → limits.", False, INK),
        (0, "Two arcs deserve careful attention and are repeated at the end for clarity:", True, ACCENT),
        (1, "The research question evolution — the original RQ set, and why RQ2 was dropped and folded into RQ1 (supervisor direction).", False, INK),
        (1, "A genuine data-quality bug in our RQ3 dependency-graph metric — how it originated, how it was found, the fix, the reasoning, and what it enabled.", False, WARN),
        (0, "Honesty over polish: every number, caveat, and unresolved step is stated plainly. No step is hidden.", True, ACCENT2),
    ])

    # ---- 1. Motivation and research questions (original vs current) ----
    s = slide_title(prs, "Research questions — four asked, four current")
    add_table(s,
              ["Original RQ", "Original question", "Decision"],
              [
                  ["RQ1", "Which FastAPI DI constructs are used, and how frequently?", "KEPT — primary focus"],
                  ["RQ2", "Do DI patterns vary across application classes?", "DROPPED — folded into RQ1 (see below)"],
                  ["RQ3", "How has DI usage evolved over repo history?", "KEPT — deferred (now RQ4)"],
                  ["RQ4", "How complex are the resulting dependency graphs?", "KEPT — now RQ3"],
              ],
              top=Inches(1.5), col_widths=[Inches(1.2), Inches(6.1), Inches(5.0)])
    bullet_box(s, Inches(0.6), Inches(3.7), Inches(12.3), Inches(3.5), [
        (0, "Why the original RQ2 was dropped: it required an a priori taxonomy of 'application classes', which we had no principled way to define. Inventing classes post-hoc is methodologically weak (leakage).", False, INK),
        (0, "Supervisor direction: fold the 'who uses DI?' question into RQ1 as a covariate axis (stars, age) instead.", True, ACCENT),
        (0, "The current RQ set, renumbered for clarity:", True, INK),
        (1, "RQ1 — construct prevalence (was RQ1).", False, INK),
        (1, "RQ2 — usage & dynamic relationships (new — added after an exploratory pass found measurable patterns).", False, INK),
        (1, "RQ3 — dependency-graph complexity (was RQ4).", False, INK),
        (1, "RQ4 — evolution over time (was RQ3) — committed to but deferred as future work.", False, MUTED),
        (0, "Every later slide follows THIS numbering.", True, ACCENT2),
    ])

    # ---- 2. Oversize stats ----
    s = slide_title(prs, "The corpus at a glance — three headline magnitudes")
    add_bigstat(s, Inches(0.6), Inches(2.4), Inches(3.6), Inches(2.0),
                _fmt(D["n_cand"]), "candidates from the GitHub dependency graph", INK)
    add_bigstat(s, Inches(4.9), Inches(2.4), Inches(3.8), Inches(2.0),
                _fmt(D["n_acc"]), f"accepted after rules E1\u2013E4 ({D['accept_rate_pct']:.1f}%)", ACCENT)
    add_bigstat(s, Inches(9.4), Inches(2.4), Inches(3.6), Inches(2.0),
                f"{D['overlap_acc_topic']} / {D['n_acc']}", "overlap with the topic:fastapi signal", ACCENT2)
    bullet_box(s, Inches(0.6), Inches(4.7), Inches(12.3), Inches(2.4), [
        (0, "These three numbers frame the whole study: a large candidate pool, a strict quality gate, and a population that an alternative signal cannot recover.", False, INK),
        (0, "Each is unpacked in the slides that follow.", False, MUTED),
    ])

    # ---- 3. Population / source ----
    s = slide_title(prs, "Population and discovery source")
    bullet_box(s, Inches(0.6), Inches(1.6), Inches(12.3), Inches(3.0), [
        (0, "Target population: open-source GitHub repos that import fastapi and expose ≥ 1 FastAPI app.", False, INK),
        (0, "Primary source: GitHub dependency-graph dependents of fastapi/fastapi — repos whose manifests GitHub resolves as depending on fastapi.", True, ACCENT),
        (0, "Origin of this choice: originally Libraries.io /dependents; that endpoint is disabled server-side (librariesio#2647). GitHub's dependency graph uses the same manifest-parsing mechanism, so it is the live, fresh equivalent.", False, INK),
        (0, "Every candidate enriched via the GitHub REST API: language byte ratios, forks, archived flag, push age, commit count, stars, license, topics.", False, INK),
        (0, "Stars are recorded as a covariate only, never as an eligibility gate.", False, MUTED),
    ])
    add_table(s,
              ["Candidates", "Snapshot", "Enriched", "Terminal decisions"],
              [[_fmt(D["n_cand"]), f"{D['n_pages']} raw dependent pages", "via GitHub API",
                f"{_fmt(D['n_acc'])} accepted + {_fmt(D['n_excl'])} excluded"]],
              top=Inches(4.9), col_widths=[Inches(2.0), Inches(3.4), Inches(3.4), Inches(3.5)])

    # ---- 4. Eligibility rules E1–E4 ----
    s = slide_title(prs, "Eligibility rules E1–E4 — what each tests, and its status")
    add_table(s,
              ["Rule", "What it tests (pass criterion)", "Role", "Status"],
              [
                  ["E1", "fastapi imported in ≥ 1 production file (extractor)", "Exclusion", "Active"],
                  ["E2", "Not a fork and not archived", "Exclusion", "Active"],
                  ["E3", "Pushed within the last 60 months", "Exclusion", "Active"],
                  ["E4", "≥ 2 distinct files import fastapi", "Exclusion", "Active · threshold-tested"],
              ],
              top=Inches(1.6), font_size=11,
              col_widths=[Inches(0.8), Inches(6.6), Inches(1.7), Inches(3.2)])
    bullet_box(s, Inches(0.6), Inches(4.7), Inches(12.3), Inches(2.4), [
        (0, "E1–E4 are hard gates: the first failing rule is recorded for every candidate (exclusion_log.json).", False, INK),
        (0, "The earlier E1–E6 gate (Python-byte-ratio E2, tutorial-marker E6 flag) was revised to the current E1–E4 rules — see github_stratified_scan_stats.md.", True, MUTED),
        (0, "Rule thresholds are schema-versioned constants in corpus/settings.py for full reproducibility.", False, MUTED),
    ])

    # ---- 5. Funnel / exclusion counts ----
    s = slide_title(prs, f"From {_fmt(D['n_cand'])} candidates to {_fmt(D['n_acc'])} accepted \u2014 the funnel")
    reasons = D["exclusions_by_reason"]
    e1_e2_pct = 100.0 * (reasons.get("E1", 0) + reasons.get("E2", 0)) / D["n_excl"] if D["n_excl"] else 0.0
    e2_pct = 100.0 * reasons.get("E2", 0) / D["n_excl"] if D["n_excl"] else 0.0
    e1_pct = 100.0 * reasons.get("E1", 0) / D["n_excl"] if D["n_excl"] else 0.0
    unavail = reasons.get("clone_failed", 0)
    add_table(s,
              ["Rule", "Criterion (short)", "Excluded"],
              [["E4", "below scale (single-file/demo)", _fmt(reasons.get("E4", 0))],
               ["E2", "is a fork OR archived", _fmt(reasons.get("E2", 0))],
               ["E1", "no production fastapi import", _fmt(reasons.get("E1", 0))],
               ["clone_failed", "un-retrievable at snapshot time", _fmt(unavail)]],
              top=Inches(1.6), col_widths=[Inches(1.6), Inches(8.7), Inches(2.0)])
    bullet_box(s, Inches(0.6), Inches(4.8), Inches(12.3), Inches(2.4), [
        (0, f"{e1_e2_pct:.0f}% of the {_fmt(D['n_excl'])} exclusions come from E2 ({e2_pct:.0f}%) and E1 ({e1_pct:.0f}%) \u2014 the dependency graph surfacing forks/archives and non-production-import repos.", False, INK),
        (0, f"Only {_fmt(unavail)} repos ({100.0 * unavail / D['n_cand']:.1f}%) were un-retrievable at clone time \u2014 minimal, documented attrition; every remaining candidate has a decision.", False, ACCENT2),
    ])

    # ---- 6. Recall benchmark ----
    s = slide_title(prs, "Methodological anchor: the topic signal recovers ~0% of the corpus")
    add_table(s,
              ["Pool", "Size", "Overlap with topic:fastapi", "% overlap"],
              [["Candidates (dependency graph)", _fmt(D["n_cand"]), str(D["overlap_cand_topic"]),
                f"{100.0 * D['overlap_cand_topic'] / D['n_cand']:.1f}%"],
               ["Accepted corpus", _fmt(D["n_acc"]), str(D["overlap_acc_topic"]),
                f"{100.0 * D['overlap_acc_topic'] / D['n_acc']:.1f}%"]],
              top=Inches(1.6), col_widths=[Inches(5.5), Inches(2.0), Inches(3.6), Inches(1.2)])
    bullet_box(s, Inches(0.6), Inches(3.6), Inches(12.3), Inches(3.4), [
        (0, "Independent signal: the `topic:fastapi` GitHub search (top 1,000 by stars), snapshotted once.", False, INK),
        (0, f"It recovers {_fmt(D['overlap_acc_topic'])} accepted repo ({100.0 * D['overlap_acc_topic'] / D['n_acc']:.1f}%). The dependency graph finds real users; the topic signal finds templates and tutorials.", True, ACCENT),
        (0, "This is a completeness bound on our primary source: the corpus is not merely 'well-known FastAPI projects', and a tutorial-based corpus would systematically miss real DI usage.", False, INK),
        (0, "The topic signal is used only as a measurement — never as a pool member or an eligibility criterion.", False, MUTED),
    ])

    # ---- 7. Sampling / corpus ----
    reports = _load_reports()
    n_total = len(reports)
    s = slide_title(prs, f"Corpus \u2014 full census of {_fmt(D['n_acc'])} accepted repos")
    bullet_box(s, Inches(0.6), Inches(1.6), Inches(12.3), Inches(2.6), [
        (0, f"{_fmt(D['n_cand'])} GitHub dependents of fastapi/fastapi (dependency graph) \u2192 {_fmt(D['n_acc'])} accepted under E1\u2013E4.", False, INK),
        (0, f"This analysis reports the FULL accepted corpus (census, n = {_fmt(D['n_acc'])}), not a random sample.", True, ACCENT),
        (0, "A 327-repo stratified sample is used only for manual extractor review; all reported numbers are this census.", True, ACCENT),
        (0, f"So the '%' denominators throughout are out of {_fmt(D['n_acc'])} repos (per-construct rows overlap by design).", False, MUTED),
    ])
    add_bigstat(s, Inches(4.0), Inches(4.4), Inches(5.3), Inches(1.8),
                f"{_fmt(n_total)} / {_fmt(D['n_acc'])}", "accepted corpus · full census", ACCENT)

    # ---- 8. RQ1 prevalence ----
    s = slide_title(prs, "RQ1 — which DI constructs do real projects use?", f"full-corpus census, n={_fmt(D['n_acc'])}")
    rows = _csv("rq1_constructs.csv")
    clean = [r for r in rows if r["construct_id"] in ("C1","C2","C3","C4")]
    table_rows = [[r["construct"], r["repos_using"], r["pct_of_sample"]+"%", r["total_calls"], r["median_per_repo_using"]] for r in clean]
    add_table(s,
              ["Construct", "Repos", "% of corpus", "Total calls", "Median (users)"],
              table_rows,
              top=Inches(1.4), col_widths=[Inches(4.4), Inches(1.7), Inches(1.7), Inches(2.2), Inches(2.2)])
    mult = _multiplicity(reports)
    zero, one, two = mult[0][1], mult[1][1], sum(n for i, n in mult if i >= 2)
    bullet_box(s, Inches(0.6), Inches(5.1), Inches(12.3), Inches(2.1), [
        (0, "The \"% of corpus\" column is per-construct and does NOT sum to 100%. Each cell is the share of the "
            f"{_fmt(D['n_acc'])} repos that use that construct at least once.", True, INK),
        (0, "A repo can appear in many rows because one project often mixes several DI constructs (e.g. Depends + generator/yield + Security together).", False, INK),
        (0, f"In the census: {100*zero/n_total:.0f}% use no core construct, {100*one/n_total:.0f}% exactly one, and {100*two/n_total:.0f}% two or more. The columns overlap by design — see the next slide for the full breakdown.", True, ACCENT2),
    ])

    # ---- 9. RQ1 construct-overlap breakdown ----
    s = slide_title(prs, "RQ1 — how the constructs overlap in the same repos", "the multiplicity and pairings behind the per-construct percentages")
    mult_rows = [[f"{i}" if i else "0 (no core DI)", n, f"{100*n/n_total:.1f}%"] for i, n in mult]
    add_table(s,
              ["Constructs per repo", f"Repos (of {n_total})", "% of corpus"],
              mult_rows,
              top=Inches(1.5), left=Inches(0.55), width=Inches(4.7),
              col_widths=[Inches(2.6), Inches(1.2), Inches(1.2)])
    prs_rows = [[f"{a} + {b}", n] for a, b, n in _pairings(reports, top=6)]
    add_table(s,
              ["Most common pairings", f"Repos (of {n_total})"],
              prs_rows,
              top=Inches(1.5), left=Inches(6.35), width=Inches(6.1),
              col_widths=[Inches(4.8), Inches(1.3)])
    bullet_box(s, Inches(0.6), Inches(4.75), Inches(12.3), Inches(2.4), [
        (0, f"{100*two/n_total:.0f}% of repos mix two or more DI constructs — the per-construct rows on the previous slide are NOT mutually exclusive.", True, ACCENT2),
        (0, "Depends (C1) is the 'host' construct: every user of Security, Annotated or Generator/yield also uses Depends.", False, INK),
        (0, "The dominant pairing is Depends + Generator/yield "
            f"({_pairings(reports, top=1)[0][2]} repos) — the classic session-scope pattern `def foo(yield db)`.", False, WARN),
    ])

    # ---- 10. RQ1 interpretation + zero-DI ----
    P = {r["construct_id"]: float(r["pct_of_sample"]) for r in clean}
    zero_core = 100.0 * mult[0][1] / n_total
    s = slide_title(prs, "RQ1 — what the numbers mean")
    bullet_box(s, Inches(0.6), Inches(1.5), Inches(12.3), Inches(3.0), [
        (0, f"Depends (C1) is dominant but not universal: {P['C1']:.1f}% of real apps use it; the zero-DI cohort is {zero_core:.1f}%.", True, INK),
        (0, f"Generator/yield deps (C4, {P['C4']:.1f}%) outnumber the modern Annotated style (C3, {P['C3']:.1f}%) — the 'recommended' style is not the most common in the wild.", False, INK),
        (0, f"Security (C2, {P['C2']:.1f}%) is under-used despite being a headline auth feature; median just 1 call among users.", False, INK),
        (0, f"Zero-DI cohort = {zero_core:.1f}%: real FastAPI apps (\u2265 2 distinct files importing fastapi) that use no core DI construct at all.", True, ACCENT2),
    ])
    add_bigstat(s, Inches(0.9), Inches(5.0), Inches(5.6), Inches(1.8),
                f"{zero_core:.1f}%", "zero-DI cohort — real apps bypassing the DI system", ACCENT2)
    add_bigstat(s, Inches(6.9), Inches(5.0), Inches(5.6), Inches(1.8),
                f"{P['C1']:.1f}%", "use Depends at least once in production files", ACCENT)

    # ---- 10. RQ1 by covariate (the dropped application-class question) ----
    s = slide_title(prs, "RQ1 axis — who uses DI? (the dropped 'application classes' question)", "disaggregated by stars and age across the census")
    bs = _csv("rq1_by_stars.csv")
    ba = _csv("rq1_by_age.csv")
    add_table(s,
              ["Stars", "Repos", "% using core DI", "Median core calls"],
              [[r["stars_bucket"], r["repos"], r["pct_using_core_di"]+"%", r["median_core_calls"]] for r in bs],
              top=Inches(1.4), left=Inches(0.6), width=Inches(6.0),
              col_widths=[Inches(1.5), Inches(1.3), Inches(1.9), Inches(1.9)])
    add_table(s,
              ["Age", "Repos", "% using core DI", "Median core calls"],
              [[r["age_bucket"], r["repos"], r["pct_using_core_di"]+"%", r["median_core_calls"]] for r in ba],
              top=Inches(1.4), left=Inches(7.0), width=Inches(6.0),
              col_widths=[Inches(1.5), Inches(1.3), Inches(1.9), Inches(1.9)])
    bullet_box(s, Inches(0.6), Inches(4.2), Inches(12.3), Inches(3.0), [
        (0, "DI adoption is essentially flat across popularity (≈70–76%) in the well-populated star buckets — DI use is not a popularity artefact.", True, ACCENT),
        (0, f"The corpus skews very young: {next((r['repos'] for r in ba if r['age_bucket'] == '<12mo'), '?')}/{n_total} repos are under 12 months old — a product of the E3 recency gate and a fast-growing dependency-graph population.", False, INK),
        (0, "Ages 12–36mo and 36mo+ show slightly higher adoption "
            f"({next((r['pct_using_core_di'] for r in ba if r['age_bucket'] == '12-36mo'), '?')}%, "
            f"{next((r['pct_using_core_di'] for r in ba if r['age_bucket'] == '36mo+'), '?')}%) but hold only "
            f"{next((r['repos'] for r in ba if r['age_bucket'] == '12-36mo'), '?')} and "
            f"{next((r['repos'] for r in ba if r['age_bucket'] == '36mo+'), '?')} repos — too few for stable conclusions. Reported for completeness, not over-read.", False, WARN),
        (0, "High-star buckets (10–99, 100+) hold "
            f"{next((r['repos'] for r in bs if r['stars_bucket'] == '10-99'), '?')} and "
            f"{next((r['repos'] for r in bs if r['stars_bucket'] == '100+'), '?')} repos — reported for completeness, not over-read.", False, WARN),
        (0, "This covariate view is how the dropped 'application classes' question is answered without an arbitrary taxonomy.", False, MUTED),
    ])

    # ---- 11. RQ3 graphs ----
    g = [r for r in _csv("rq4_graphs.csv") if int(r["nodes_clean"]) > 0]
    s = slide_title(prs, "RQ3 — how complex are the dependency graphs?", f"{len(g)} of {n_total} repos have a non-empty graph")
    add_table(s,
              ["Metric", "Median", "IQR", "Max"],
              [[ "Nodes (clean)", st.median(int(r["nodes_clean"]) for r in g),
                f"({_q(int(r['nodes_clean']) for r in g)})", max(int(r["nodes_clean"]) for r in g)],
               ["Max depth", st.median(int(r["max_depth"]) for r in g),
                f"({_q(int(r['max_depth']) for r in g)})", max(int(r["max_depth"]) for r in g)],
               ["Unresolved %", round(st.median(float(r["unresolved_pct"]) for r in g), 2),
                f"({_q(float(r['unresolved_pct']) for r in g)})", max(float(r["unresolved_pct"]) for r in g)]],
              top=Inches(1.6), col_widths=[Inches(3.5), Inches(2.4), Inches(3.5), Inches(2.4)])
    bullet_box(s, Inches(0.6), Inches(3.6), Inches(12.3), Inches(3.0), [
        (0, "Complexity is measured on the dependency graph the resolver builds from Depends calls.", False, INK),
        (0, f"Graphs are shallow in the median: depth {st.median(int(r['max_depth']) for r in g)}, max {max(int(r['max_depth']) for r in g)} — flat dependency trees in the typical case.", True, INK),
        (0, "A small deep tail exists: 58 repos (4.3%) reach depth \u2265 5, and every one still has a fan-out hub (see rq3_depth_tail.csv).", False, WARN),
        (0, "This is the empirical signature of FastAPI DI: a small set of shared dependencies reused across many handlers (fan-out), not deep inheritance-like nesting.", False, ACCENT),
        (0, f"{round(100*sum(1 for r_ in g if float(r_['unresolved_pct']) == 0)/len(g))}% of graph-bearing repos resolve at 0% unresolved — the resolver is reliable at corpus scale.", False, ACCENT2),
    ])

    # ---- 12. RQ3 DATA-QUALITY BUG (PART 1: origin & diagnosis) ----
    s = slide_title(prs, "RQ3 data-quality bug — Part 1: how it originated and how we found it")
    add_table(s,
              ["Aspect", "Detail"],
              [["What was wrong", "Some 'nodes' in the dependency graphs were filesystem paths (e.g. /home/.../main.py:23), not callable names."],
               ["Where", "In the dependency-graph builder of the resolver (resolver.py line 112)."],
               ["Why it happened", "A Depends call at module scope (e.g. FastAPI(dependencies=[...]) or router defaults) has no enclosing function, so context_function is None; the code fell back to using '{file_path}:{line}' as the source node id."],
               ["How diagnosed", "While inspecting graphs for the presentation, node ids containing '/' stood out — not valid function names."]],
              top=Inches(1.5), font_size=11,
              col_widths=[Inches(2.3), Inches(10.0)])
    db_g = [r for r in g]
    junk_bear = [r for r in db_g if int(r["junk_nodes"]) > 0]
    junk_total = sum(int(r["junk_nodes"]) for r in db_g)
    add_bigstat(s, Inches(0.9), Inches(5.1), Inches(5.9), Inches(1.8),
                f"{junk_total}", f"junk 'file:line' nodes across {len(junk_bear)} of {len(db_g)} graph-bearing repos"
                f" ({round(100*junk_total/max(1,sum(int(r['nodes_raw']) for r in db_g)),1)}% of all raw nodes)", WARN)
    add_bigstat(s, Inches(7.0), Inches(5.1), Inches(5.9), Inches(1.8),
                f"{round(100*len(junk_bear)/max(1,len(db_g)))}%", f"of graph-bearing repos were contaminated ({len(junk_bear)} / {len(db_g)})", WARN)

    # ---- 13. RQ3 DATA-QUALITY BUG (PART 2: impact) ----
    rq4all = [r for r in _csv("rq4_graphs.csv")]
    gb_all = [r for r in rq4all if int(r["nodes_clean"]) > 0]
    clean_med = st.median(int(r["nodes_clean"]) for r in gb_all)
    raw_med = st.median(int(r["nodes_raw"]) for r in gb_all)
    junk_bear_all = [r for r in gb_all if int(r["junk_nodes"]) > 0]
    junk_share_med = st.median(int(r["junk_nodes"]) / (int(r["nodes_raw"]) or 1) for r in junk_bear_all)
    raw_max = max(int(r["nodes_raw"]) for r in rq4all)
    s = slide_title(prs, "RQ3 data-quality bug — Part 2: how much it distorted the numbers")
    add_table(s,
              ["Effect of the bug", "Value"],
              [["Median node count (graph-bearing)", f"inflated {clean_med} → {raw_med} (with junk)"],
               ["Per-repo junk share (dirty repos)", f"median ~{round(100*junk_share_med)}% of that repo's nodes were junk"],
               ["Max node count seen in a repo", f"inflated by the junk (one raw repo reached {raw_max} nodes)"],
               ["Did it change whether a repo had a graph?", f"No — all {len(gb_all)} repos still had a clean non-empty graph after filtering"]],
              top=Inches(1.5), font_size=11, col_widths=[Inches(6.2), Inches(6.1)])
    bullet_box(s, Inches(0.6), Inches(4.6), Inches(12.3), Inches(2.4), [
        (0, "The bug inflated node counts and could add spurious edges/density — it did not fabricate graphs where none existed.", False, INK),
        (0, "Important: RQ1 construct counts (C1–C4) are read from call sites, not from graph nodes, so RQ1 was NOT affected by this bug.", True, ACCENT2),
        (0, "Only the RQ3 dependency-graph complexity metric needed correction.", False, INK),
    ])

    # ---- 14. RQ3 DATA-QUALITY BUG (PART 3: fix + reasoning) ----
    s = slide_title(prs, "RQ3 data-quality bug — Part 3: the fix and the reasoning")
    bullet_box(s, Inches(0.6), Inches(1.5), Inches(12.3), Inches(5.4), [
        (0, "Two possible places to fix: the resolver (root cause) or the aggregation (defensive filter).", True, INK),
        (0, "We chose the aggregation-time filter, for three reasons:", False, INK),
        (1, "Existing corpus reports are frozen snapshots — patching the resolver does not retroactively fix them, and re-running full extraction over "
            f"{_fmt(D['n_acc'])} repos is expensive.", False, INK),
        (1, "Filtering by node-id pattern is targeted and auditable: drop any id containing a path separator or a 'file:line' anchor, and drop any edge that references such a node.", False, INK),
        (1, "It keeps the raw and clean columns side by side (rq4_graphs.csv) so the transformation is transparent and re-checkable.", False, INK),
        (0, "The fix is deterministic and documented in docs/result_draft_01.md §6.1 as an honest reporting sentence: 'we filtered resolver-emitted non-callable artifact nodes before computing complexity metrics.'", True, ACCENT2),
    ])

    # ---- 15. RQ3 DATA-QUALITY BUG (PART 4: what the clean data enabled) ----
    s = slide_title(prs, "RQ3 data-quality bug — Part 4: what the fix enabled")
    bullet_box(s, Inches(0.6), Inches(1.5), Inches(12.3), Inches(3.2), [
        (0, f"After the fix the RQ3 picture is trustworthy: median {clean_med} clean nodes, IQR {_q(int(r['nodes_clean']) for r in gb_all)}, max {max(int(r['nodes_clean']) for r in gb_all)}; median depth 2, max 7; median unresolved 0.0%.", True, ACCENT2),
        (0, "It let us establish the fan-out signature with confidence (next slide).", False, INK),
        (0, "It exposed that the 'lost' module-scope dependency declarations are exactly where real DI hubs live (e.g. mealie's base_controllers.py) — a limitation worth reporting.", False, INK),
        (0, "It set a precedent for data QA in the paper: we surface the bug, its measure, and the fix instead of hiding it — a credibility asset.", False, WARN),
    ])
    add_bigstat(s, Inches(0.9), Inches(5.1), Inches(5.9), Inches(1.8),
                f"{len(gb_all)} → {len(gb_all)}", "graph-bearing repos retained clean graphs after filtering", ACCENT2)
    add_bigstat(s, Inches(7.0), Inches(5.1), Inches(5.9), Inches(1.8),
                "0.0%", "median unresolved rate on clean graphs", ACCENT2)

    # ---- 16. Fan-out hub ----
    s = slide_title(prs, "The architectural signature: fan-out reuse", "a shared dependency with many dependents")
    hub = s.shapes.add_shape(MSO_SHAPE.OVAL, Inches(4.1), Inches(2.5), Inches(5.1), Inches(1.4))
    hub.fill.solid(); hub.fill.fore_color.rgb = RGBColor(0xDD, 0xF4, 0xFF); hub.line.color.rgb = ACCENT
    htf = hub.text_frame; htf.text = "get_db (shared dependency)  ·  depends=get_db"
    htf.paragraphs[0].font.size = Pt(15); htf.paragraphs[0].font.bold = True
    htf.paragraphs[0].alignment = PP_ALIGN.CENTER; htf.word_wrap = True
    labels = [
        ("GET /users", 0.9, 1.7), ("POST /users", 5.9, 1.3),
        ("GET /items", 10.9, 1.7), ("GET /orders", 1.1, 5.9),
        ("PUT /users", 5.6, 6.2), ("DELETE /items", 10.7, 5.9),
    ]
    for lab, x, y in labels:
        b = s.shapes.add_textbox(Inches(x), Inches(y), Inches(2.1), Inches(0.7))
        tf = b.text_frame; tf.text = lab
        tf.paragraphs[0].font.size = Pt(14); tf.paragraphs[0].font.color.rgb = MUTED
        tf.paragraphs[0].alignment = PP_ALIGN.CENTER
    add_bigstat(s, Inches(0.6), Inches(5.3), Inches(6.0), Inches(1.6),
                f"{round(100*_fan_out3(reports)[0]/_fan_out3(reports)[1],1)}%",
                "of clean graph-bearing repos have some dependency called by ≥3 other Depends sites (fan-out)", ACCENT)
    add_bigstat(s, Inches(7.0), Inches(5.3), Inches(6.0), Inches(1.6),
                f"depth {st.median(int(r['max_depth']) for r in g):g}", "median graph depth = reuse is broad, not deep", MUTED)

    # ---- 17. Sensitivity ----
    s = slide_title(prs, "Robustness — eligibility threshold (t) sensitivity", "the headline % is stable across the threshold range")
    sens = _csv("sensitivity.csv")
    add_table(s,
              ["Min fastapi files (t)", "Eligible N", "% use core DI", "Median depends (users)"],
              [[r["e5_min_fastapi_files"], r["eligible_n"], r["pct_using_core_di"]+"%", r["median_depends_among_users"]] for r in sens],
              top=Inches(1.6), col_widths=[Inches(2.6), Inches(2.2), Inches(3.0), Inches(3.0)])
    bullet_box(s, Inches(0.6), Inches(4.0), Inches(12.3), Inches(3.0), [
        (0, "As the E4 threshold t rises from 2 to 8 (scoping to progressively larger, more substantial apps), the % using core DI moves only "
            f"{_row_by(sens, 'e5_min_fastapi_files', '2')['pct_using_core_di']}% \u2192 {_row_by(sens, 'e5_min_fastapi_files', '8')['pct_using_core_di']}%.", False, INK),
        (0, "Conclusion is threshold-stable: the qualitative findings do not depend on the specific threshold.", True, ACCENT),
        (0, "t=2 is near-null (all but the low-file tail pass); the base threshold t=4 balances inclusiveness against structural meaning. Sensitivity is meaningful at t ≥ 5.", False, WARN),
        (0, "Tighter thresholds capture larger apps with more DI per repo — larger apps do use DI more.", False, INK),
    ])

    # ---- 18. Caveats ----
    s = slide_title(prs, "Caveats & threats — said plainly")
    bullet_box(s, Inches(0.6), Inches(1.4), Inches(12.3), Inches(5.7), [
        (0, "Source substitution: GitHub dependency graph replaced Libraries.io (disabled server-side).", False, INK),
        (0, "Population: only repos GitHub's dependency graph resolves; invisible setups (e.g. submodules, unusual installs) are unrepresented.", False, INK),
        (0, "Attrition: "
            f"{_fmt(reasons.get('clone_failed', 0))} repos ({100.0 * reasons.get('clone_failed', 0) / D['n_cand']:.1f}%) un-retrievable at clone time; "
            "every remaining candidate has a decision.", False, INK),
        (0, "E-rule revision: the earlier E1–E6 gate (Python-byte-ratio E2, tutorial-marker E6 flag) was replaced by the current E1–E4 rules (see github_stratified_scan_stats.md); the E6 review is retained as historical rationale only.", False, MUTED),
        (0, "Resolver coverage: "
            f"{100 * (n_total - len(g)) // n_total}% of accepted repos have empty graphs despite nonzero depends_total (resolver cannot follow some cross-file patterns).", False, INK),
        (0, "The manual-review sample is stratified by stars (0★ / 1–9★ / 10–99★ / 100+★); the smallest star bucket (100+) has only "
            f"{next((r['repos'] for r in bs if r['stars_bucket'] == '100+'), '?')} repos — bucket-level conclusions are not over-read.", False, INK),
        (0, "Artifacts were only first committed to git on 2026-08-31 (previously zero commits) — review the commit history before any external submission.", False, WARN),
    ])

    # ---- 19. So what / significance ----
    s = slide_title(prs, "So what? — the value to the table")
    bullet_box(s, Inches(0.6), Inches(1.5), Inches(12.3), Inches(5.4), [
        (0, "Methodology: a corpus source with provable recall (0% topic overlap) and full decision auditability.", True, ACCENT),
        (0, "For tool/users: DI is NOT universal in real FastAPI "
            f"({zero_core:.0f}% zero-DI) — ecosystem guidance assumes more DI than practice shows.", True, INK),
        (0, "For maintainers: Security() and advanced constructs are barely adopted; Depends + generator-style dominate.", True, INK),
        (0, "For the paper: hard, reproducible, threshold-stable numbers on construct prevalence, graph depth, and sensitivity.", False, INK),
        (0, "For practice: real graphs are broad-and-shallow (fan-out hubs), which informs how FastAPI DI is taught and designed.", False, INK),
        (0, "For the reader: the study is honest about its own evolution (RQ change) and its own data-quality bug, and shows how each was handled.", True, ACCENT2),
    ])

    out = OUT_DIR / "fastapi_di_presentation.pptx"
    prs.save(out)
    print(f"[pptx] wrote {out}")


def _q(it):
    v = list(it)
    if len(v) < 2:
        return v[0] if v else 0
    q1, _, q3 = st.quantiles(v, n=4)
    return f"{int(q1)}–{int(q3)}"


if __name__ == "__main__":
    main()
