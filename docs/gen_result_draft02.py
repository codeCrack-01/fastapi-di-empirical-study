#!/usr/bin/env python3
"""Generate docs/result_draft_02.docx"""
import os
from docx import Document
from docx.shared import Pt, Inches, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_TAB_ALIGNMENT, WD_TAB_LEADER
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.section import WD_SECTION
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

OUT = "docs/result_draft_02.docx"
MONO = "Consolas"

doc = Document()

# ---------- base styles ----------
st = doc.styles["Normal"]
st.font.name = "Calibri"
st.font.size = Pt(10.5)
st.paragraph_format.space_after = Pt(6)
st.paragraph_format.line_spacing = 1.12

for nm, sz, col in (("Heading 1", 16, 0x1F3864), ("Heading 2", 13, 0x2E5496),
                    ("Heading 3", 11.5, 0x2E5496), ("Heading 4", 10.5, 0x44546A)):
    s = doc.styles[nm]
    s.font.name = "Calibri"
    s.font.size = Pt(sz)
    s.font.bold = True
    s.font.color.rgb = RGBColor((col >> 16) & 255, (col >> 8) & 255, col & 255)
    s.paragraph_format.space_before = Pt(14 if nm == "Heading 1" else 10)
    s.paragraph_format.space_after = Pt(4)
    s.paragraph_format.keep_with_next = True

for s in doc.sections:
    s.left_margin = s.right_margin = Inches(0.9)
    s.top_margin = s.bottom_margin = Inches(0.85)


# ---------- helpers ----------
HEADINGS = []


def shade(cell, hexcolor):
    el = OxmlElement("w:shd")
    el.set(qn("w:val"), "clear")
    el.set(qn("w:fill"), hexcolor)
    cell._tc.get_or_add_tcPr().append(el)


def h(text, level=1):
    HEADINGS.append((level, text))
    return doc.add_heading(text, level=level)


def p(text="", bold=False, italic=False, size=None, align=None, space_after=None):
    par = doc.add_paragraph()
    if align:
        par.alignment = align
    if space_after is not None:
        par.paragraph_format.space_after = Pt(space_after)
    r = par.add_run(text)
    r.bold, r.italic = bold, italic
    if size:
        r.font.size = Pt(size)
    return par


def rich(parts, align=None, style=None):
    """parts: list of (text, fmt) where fmt in {'', 'b', 'i', 'c', 'bi'}"""
    par = doc.add_paragraph(style=style)
    if align:
        par.alignment = align
    for text, fmt in parts:
        r = par.add_run(text)
        if "b" in fmt:
            r.bold = True
        if "i" in fmt:
            r.italic = True
        if "c" in fmt:
            r.font.name = MONO
            r.font.size = Pt(9)
    return par


def bullet(text, level=0):
    par = doc.add_paragraph(text, style="List Bullet")
    par.paragraph_format.left_indent = Inches(0.25 + 0.25 * level)
    par.paragraph_format.space_after = Pt(2)
    return par


def kv_bullet(key, val):
    par = doc.add_paragraph(style="List Bullet")
    par.paragraph_format.left_indent = Inches(0.25)
    par.paragraph_format.space_after = Pt(2)
    par.add_run(key).bold = True
    par.add_run(val)
    return par


def code(text):
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Inches(0.25)
    par.paragraph_format.space_before = Pt(3)
    par.paragraph_format.space_after = Pt(6)
    r = par.add_run(text)
    r.font.name = MONO
    r.font.size = Pt(8.5)
    return par


def caption(text):
    par = doc.add_paragraph()
    par.paragraph_format.space_before = Pt(8)
    par.paragraph_format.space_after = Pt(3)
    r = par.add_run(text)
    r.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)
    return par


def note(text, label="Note"):
    par = doc.add_paragraph()
    par.paragraph_format.left_indent = Inches(0.2)
    par.paragraph_format.space_before = Pt(4)
    par.paragraph_format.space_after = Pt(8)
    r = par.add_run(f"{label}: ")
    r.bold = True
    r.font.size = Pt(9.5)
    r.font.color.rgb = RGBColor(0x7F, 0x30, 0x00)
    r2 = par.add_run(text)
    r2.font.size = Pt(9.5)
    return par


def table(headers, rows, widths=None, fontsize=9, mono_cols=(), bold_rows=()):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    hdr = t.rows[0].cells
    for i, htxt in enumerate(headers):
        hdr[i].text = ""
        par = hdr[i].paragraphs[0]
        par.paragraph_format.space_after = Pt(1)
        par.paragraph_format.space_before = Pt(1)
        r = par.add_run(str(htxt))
        r.bold = True
        r.font.size = Pt(fontsize)
        r.font.color.rgb = RGBColor(0xFF, 0xFF, 0xFF)
        shade(hdr[i], "2E5496")
    for ri, row in enumerate(rows):
        cells = t.add_row().cells
        for i, val in enumerate(row):
            cells[i].text = ""
            par = cells[i].paragraphs[0]
            par.paragraph_format.space_after = Pt(1)
            par.paragraph_format.space_before = Pt(1)
            r = par.add_run(str(val))
            r.font.size = Pt(fontsize)
            if i in mono_cols:
                r.font.name = MONO
                r.font.size = Pt(fontsize - 1)
            if ri in bold_rows:
                r.bold = True
        if ri % 2 == 1:
            for c in cells:
                shade(c, "F2F5FA")
        if ri in bold_rows:
            for c in cells:
                shade(c, "E4ECF7")
    if widths:
        # Word and LibreOffice both autofit by content unless the layout is
        # pinned to fixed, which makes a narrow first column swallow the page.
        t.autofit = False
        tblPr = t._tbl.tblPr
        layout = OxmlElement("w:tblLayout")
        layout.set(qn("w:type"), "fixed")
        tblPr.append(layout)
        for i, w in enumerate(widths):
            t.columns[i].width = Inches(w)
            for row in t.rows:
                row.cells[i].width = Inches(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(2)
    return t


def verdict_key():
    rich([("Verdict key. ", "b"),
          ("meaningful", "b"), (" = the exact interval lies entirely beyond the practical "
           "margin; ", ""), ("practically equivalent", "b"),
          (" = the interval lies entirely inside the margin; ", ""),
          ("inconclusive vs margin", "b"),
          (" = the interval straddles the margin, so the data neither establish nor "
           "exclude a difference of practical size. Direction is stated relative to the "
           "treatment arm (a).", "")])


# ================= COVER =================
tp = doc.add_paragraph()
tp.alignment = WD_ALIGN_PARAGRAPH.CENTER
tp.paragraph_format.space_before = Pt(70)
r = tp.add_run("FastAPI Dependency Injection")
r.bold = True
r.font.size = Pt(24)
r.font.color.rgb = RGBColor(0x1F, 0x38, 0x64)

sp = doc.add_paragraph()
sp.alignment = WD_ALIGN_PARAGRAPH.CENTER
sp.paragraph_format.space_before = Pt(4)
r1 = sp.add_run("A Mixed-Methods Study of Dependency Injection")
r1.font.size = Pt(13)
r1.font.color.rgb = RGBColor(0x40, 0x40, 0x40)
r2 = sp.add_run("\nin FastAPI: A Census and a Controlled Execution-Model Benchmark")
r2.font.size = Pt(13)
r2.font.color.rgb = RGBColor(0x40, 0x40, 0x40)

dp = doc.add_paragraph()
dp.alignment = WD_ALIGN_PARAGRAPH.CENTER
dp.paragraph_format.space_before = Pt(18)
r = dp.add_run("Result Draft 02")
r.bold = True
r.font.size = Pt(12)

mp = doc.add_paragraph()
mp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = mp.add_run("Supersedes Result Draft 01")
r.italic = True
r.font.size = Pt(10.5)

doc.add_paragraph()
for line in [
    "Corpus: 2,179 accepted open-source FastAPI repositories (full census)",
    "Benchmark: 485 measured cells, 10 arms, 12 repetitions per cell",
    "RQ1-RQ3 answered; RQ4 (real-repository validation) specified but not run",
    "All benchmark artifacts SHA256-verified and committed",
]:
    q = doc.add_paragraph()
    q.alignment = WD_ALIGN_PARAGRAPH.CENTER
    q.paragraph_format.space_after = Pt(3)
    r = q.add_run(line)
    r.font.size = Pt(10)

doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

# ================= TOC (built at end, relocated here) =================
TOC_ANCHOR = len(doc.element.body) - 1  # before the trailing sectPr

# ================= 1. OVERVIEW =================
h("1. Study overview", 1)
p("This study reports two parts, answering two different questions about the same subject, and specifies a third that has not been run. The three correspond to four research questions: the first part answers RQ1 and RQ2, the second answers RQ3, and the third would answer RQ4.")
rich([("Part I is a census.", "b"),
      (" It characterises how FastAPI's dependency injection (DI) constructs are used "
       "across the open-source ecosystem, using structured AST extraction over a "
       "reproducible corpus of real FastAPI applications. It is descriptive: it "
       "establishes what exists in the wild.", "")])
rich([("Part II is a controlled experiment.", "b"),
      (" It measures what those DI patterns ", ""), ("cost", "i"),
      (" at run time, by holding the application's work constant and varying only the "
       "mechanism by which dependencies are resolved, crossed with the execution model "
       "of the dependency callables. It is causal within its design bounds: it can "
       "support statements about mechanism and load, and nothing about maintainability "
       "or preference.", "")])
p("The two parts answer the question the census alone cannot. The census shows which "
  "patterns are common; it cannot say what any of them cost, because in real code the "
  "pattern, the workload, the database and the author's skill all vary together. Part II "
  "breaks that confound by construction.")

h("1.1 Research questions", 2)
caption("Table 1.1 — Research questions, the part that answers each, and its status")
table(
    ["RQ", "Question", "Answered by", "Status"],
    [
        ["RQ1", "What dependency-injection approaches are used in FastAPI applications?",
         "Part I", "Answered — framing"],
        ["RQ2", "How are FastAPI's dependency-injection constructs used in practice?",
         "Part I", "Answered"],
        ["RQ3", "What runtime performance differences arise among commonly observed DI "
                "approaches?", "Part II", "Answered"],
        ["RQ4", "Do the observed performance differences persist when applied to real-world "
                "FastAPI applications?", "Part III", "Not answered — design fixed in "
                "Section 9"],
    ],
    widths=[0.45, 3.55, 0.85, 1.85],
)
note("RQ3 and RQ4 are deliberately not merged. RQ3 has a result and RQ4 does not, and "
     "combining them would leave a reader unable to tell which half is evidenced. Once "
     "Part III reports, the two can be presented as a single question with a synthetic "
     "half and a real-repository half. RQ2 subsumes the separate construct-usage, "
     "relationship and graph-complexity questions the design originally carried as three, "
     "because all three ask the same thing at different resolutions: how these constructs "
     "are actually used.")

h("1.2 Mixed-methods design", 2)
p("This is a mixed-methods study, and the two strands are not two studies of one topic — "
  "they are two different kinds of evidence about the same code, and each is responsible "
  "for a different class of claim.")
rich([("The quantitative strand is a census.", "b"),
      (" Its unit is the repository, its instrument is deterministic AST extraction, and "
       "its sample is the whole eligible population rather than a draw from it, so its "
       "outputs are population values and sampling error does not apply. It supports "
       "claims of the form ", ""),
      ("how often", "i"),
      (" and ", ""), ("in what form", "i"),
      (". It cannot support any claim about cost, because in real code the pattern, the "
       "workload, the database and the author's judgement all vary together and cannot be "
       "separated observationally.", "")])
rich([("The experimental strand is a controlled benchmark.", "b"),
      (" Its unit is the measured cell, its instrument is a pinned application under "
       "synthetic load, and its design holds work constant while varying one factor at a "
       "time. It supports claims of the form ", ""),
      ("how much", "i"),
      (", within its stated bounds. It cannot support any claim about prevalence, because "
       "the mechanisms it measures were selected for architectural distinctness rather "
       "than sampled from the population.", "")])
p("The two integrate in one direction only. The census determines which mechanisms exist "
  "and therefore which arms the experiment must build, and the experiment returns a cost "
  "figure for arms the census has already shown to be in use. Neither strand validates the "
  "other: a cheap mechanism that nobody uses is not a finding, and a common mechanism "
  "measured only on a synthetic application is not yet a finding about practice. That gap "
  "is exactly what RQ4 is for, and it is open.")

h("1.3 RQ1 — The DI approaches observed in FastAPI applications", 2)
p("RQ1 is a landscape question, and it is answered by orientation rather than by a "
  "headline figure. The corpus resolves into five functionally distinct approaches to "
  "obtaining a collaborator at request time, plus a substantial population that resolves "
  "nothing through the framework at all.")
rich([("The five approaches are:", "b"),
      (" no framework mechanism, where the handler resolves its own collaborator by direct "
       "call inside a connection context (", ""), ("s1_direct", "m"),
      ("); function Depends, where a callable is handed to the framework per request "
       "(", ""), ("s2_depends", "m"),
      ("); ASGI middleware injection, where a resolved object is placed on the request "
       "once and read by the handler (", ""), ("s3_middleware", "m"),
      ("); a declarative container with cached singleton providers (", ""),
      ("s4_container", "m"), ("); and a full DI library with explicit scopes and markers "
       "(", ""), ("s4_dishka", "m"), (").", "")])
p("Prevalence, call-site form, the relationships these calls establish and the depth of "
  "the resulting graphs are all evidence about how the constructs are used, and are "
  "reported together under RQ2 in Section 3. What RQ1 fixes is the design of Part II: "
  "these five are the approaches that exist to be measured, and the benchmark's arms are "
  "one-to-one with them. Table 5.1 states the mechanism each arm implements and the "
  "corpus evidence for including it.")
note("RQ1 does not ask which approach is best, and nothing in this section should be read "
     "as a recommendation. The five are functionally distinct resolution paths, not "
     "competing products; two of them are attested at very low n and are in the experiment "
     "because they are architecturally distinct, not because they are common.")

h("1.4 Relationship between the parts", 2)
p("Part I supplies the input distribution for Part II, and it also fixes which arms are "
  "worth building. Plain function Depends is not a hypothetical arm: it is the idiom of "
  "62.9% of the corpus and 96.6% of all call sites. The shared-provider shape behind the "
  "container arm is likewise attested — 708 fan-in hub dependencies with ten or more "
  "dependents, led by get_db with 24,014 — so a provider resolved once and shared across "
  "callers is a well-evidenced shape in this ecosystem, and it is the shape the container "
  "arm instantiates. The two remaining arms are "
  "deliberately minority idioms: middleware injection is observed at low n, and a "
  "third-party container import is detected in 9 repositories. They are in the benchmark "
  "because they are architecturally distinct resolution paths, not because they are "
  "common, and Section 5.10 states what their results do and do not license.")
note("The census does not measure whether the population's dependency callables are "
     "synchronous or asynchronous, so it makes no claim about that, and Part II's "
     "execution-model factor is not a sample of the corpus. It is an experimental factor "
     "introduced by the design.", "Boundary")

# ================= 2. CORPUS =================
h("2. Corpus construction", 1)

h("2.1 Discovery", 2)
kv_bullet("Source: ", "GitHub dependency-graph dependents of fastapi/fastapi, paginated "
                      "HTML, snapshotted to corpus/raw_dependents/ (167 pages).")
kv_bullet("Enrichment: ", "GitHub REST API for language bytes, fork and archived flags, "
                          "push age, commit count, stars, license and topics.")
kv_bullet("Substitution: ", "the original source, the Libraries.io /dependents endpoint, "
                            "was disabled server-side (librariesio/libraries.io#2647). "
                            "GitHub's dependency graph uses equivalent manifest parsing "
                            "and is the live substitute. Carried as an open-access data "
                            "dependency in Section 7.")

h("2.2 Candidates", 2)
p("5,000 candidates were discovered and enriched: 4,500 from the original snapshot plus "
  "500 added in 2026-09 by extending the scrape to 17 further live dependents pages, "
  "without re-deciding any already-finalised candidate.")

h("2.3 Eligibility rules", 2)
caption("Table 2.1 — Eligibility rules (E1-E4)")
table(
    ["Rule", "Criterion", "Rationale"],
    [
        ["E1", "fastapi imported in >= 1 production file", "Dev-only dependencies do not "
                                                            "constitute real usage"],
        ["E2", "Not a fork, not archived", "Original codebase, not abandoned"],
        ["E3", "pushed_at within the last 60 months", "Active, not abandoned"],
        ["E4", ">= 2 distinct files importing fastapi", "Reject single-file / demo projects"],
    ],
    widths=[0.5, 2.85, 3.35],
)
note("An earlier gate added a Python-byte-ratio threshold (>= 0.5) and a tutorial-marker "
     "flag. Both were removed. The byte-ratio gate excluded real mixed-language FastAPI "
     "applications (PyTorch/notebook-backed services, microservice repositories); the "
     "tutorial flag did not separate genuine from non-genuine applications — in the "
     "earlier 402-repository census 188 repositories (47%) carried a tutorial flag, and "
     "genuine-ness was the majority class in both the flagged and unflagged groups, so "
     "the flag modestly over-selected non-genuine repositories without being usable as "
     "an exclusion rule. The current gate is E1-E4.")

h("2.4 Filtering results", 2)
caption("Table 2.2 — Filtering outcomes over 5,000 candidates")
table(
    ["Decision", "Count", "% of pool"],
    [
        ["E4 — below scale (single-file / demo)", "1,281", "25.6%"],
        ["E2 — fork or archived", "800", "16.0%"],
        ["E1 — no production fastapi import", "516", "10.3%"],
        ["Clone failed (metadata unavailable)", "224", "4.5%"],
        ["Accepted (E1-E4 pass)", "2,179", "43.5%"],
        ["Total", "5,000", "100%"],
    ],
    widths=[3.6, 1.0, 1.0],
    bold_rows=(4, 5),
)
p("Every candidate carries a decision; corpus/exclusion_log.json records 2,821 "
  "exclusions with the first failing rule. The 224 clone failures are repositories that "
  "could not be retrieved at clone time — deleted, private, or transient network failure "
  "— and are treated as population attrition (Section 7).")

h("2.5 Recall benchmark", 2)
p("As an independent check on the discovery signal, the topic:fastapi repository search "
  "(GitHub search API, sorted by stars, top 1,000) was snapshotted and compared with the "
  "dependency-graph pool.")
caption("Table 2.3 — Overlap with an independent topic-based discovery signal")
table(
    ["Pool", "Size", "Overlap with topic:fastapi", "% overlap"],
    [["Candidates (dependency graph)", "5,000", "2", "0.04%"],
     ["Accepted", "2,179", "1", "0.05%"]],
    widths=[2.3, 0.8, 2.2, 0.9],
)
p("One accepted repository overlaps. A corpus strategy built on the topic signal would "
  "recover essentially none of this population: the two signals select different things. "
  "The topic signal finds templates and tutorials; the dependency graph finds working "
  "applications that declare a real dependency. This is a substantive methodological "
  "finding for corpus construction, not merely a coverage statistic.")

h("2.6 Analysis scope and verification", 2)
p("Part I is a full-corpus census: all 2,179 accepted repositories enter every "
  "downstream table. There is no sampling inference to generalise from, so the RQ1-RQ2 "
  "figures are population values and standard errors do not apply.")
p("Extractor correctness is verified rather than asserted. A precision probe drew a "
  "seeded sample of 40 repositories claiming DI and re-read every recorded call site at "
  "source: 2,113 of 2,147 sites confirmed (98.42%, Wilson 95% CI 97.80-98.86), above the "
  "pre-registered 90% bar. A separate 327-repository star-stratified sample exists for "
  "manual review of the extractor's output. Neither sample is used for statistical "
  "inference about prevalence; they bound measurement error only.")
note("Recall is not established by these probes. The precision probe can show that a "
     "recorded call site is real, but not that an unrecorded one was found. The "
     "pre-registered audit in Section 7.7 is what addresses that question, and it has not "
     "yet reported.", "Boundary")

# ================= 3. RQ2 =================
h("3. RQ2 — How FastAPI's DI constructs are used in practice", 1)
p("RQ2 asks what these constructs do in practice, at three resolutions: which constructs "
  "appear and how often, what form each call site takes, and what structure the resulting "
  "dependency graph has. All three are answered from the same deterministic extraction "
  "over the full accepted population, so none of them involves sampling inference.")

h("3.1 Which constructs are used, and how often", 2)
p("The first resolution is construct presence: whether a discrete syntactic API token "
  "appears at a call site. It is answerable from the left-hand token alone, with no "
  "interpretation of the argument. Four constructs are operationalised.")
caption("Table 3.1 — Core construct prevalence (n = 2,179); C3 volume is corrected, "
        "see Section 3.4")
table(
    ["ID", "Construct", "Repos (of 2,179)", "% of corpus", "Total calls",
     "Median (users)", "IQR (users)", "Max"],
    [
        ["C1", "Depends", "1,371", "62.9%", "98,243", "22.0", "7.0-66.0", "1,940"],
        ["C2", "Security", "104", "4.8%", "620", "1", "1.0-2.8", "305"],
        ["C3", "Annotated[..., Depends]", "384", "17.6%", "12,478", "7.0", "3.0-25.0", "1,940"],
        ["C4", "Generator / yield dependency", "759", "34.8%", "1,003", "1.0", "1.0-1.0", "14"],
    ],
    widths=[0.3, 1.75, 0.85, 0.72, 0.75, 0.72, 0.78, 0.5],
    mono_cols=(1,),
)
p("These four are mutually swappable spellings of a single injection mechanism. A "
  "dependency re-expressed in another construct keeps its behaviour: C1 and C3 differ "
  "only in annotation-versus-default-value spelling, and C4 is consumed through a C1 or "
  "C3 call site. The in-the-wild swappable-pattern catalogue measures this directly: "
  "1,142 providers are written in two or more constructs within a single repository, 933 "
  "of them as pure C1|C3 pairs.")

h("3.2 The zero-DI cohort", 2)
rich([("805 repositories (36.9%)", "b"),
      (" pass E1-E4 but contain no core DI construct at all — no Depends, no Security, no "
       "Annotated form, no yield dependency. These are substantial real FastAPI "
       "applications (at least two importing files, at least one app object) that do not "
       "invoke the DI system, resolving collaborators by direct call.", "")])
note("Two different denominators appear in this study and should not be confused. The "
     "805 figure is construct presence over the four framework constructs and is what "
     "Table 3.1 reports. A pre-registered audit (Section 7.7) widens the definition to any "
     "detected DI mechanism, including a third-party container import, which moves the "
     "corresponding frame to 803 zero-DI and 1,376 has-DI repositories. The two-repo "
     "difference is entirely repositories that import a DI container without using a "
     "framework construct.", "Definitions")
note("This is a construct-presence measure. It says the extractor found no DI construct; "
     "it does not establish that the repository has no dependency-management strategy. "
     "A repository may hand-roll a service locator, module-level singletons or plain "
     "function calls — all invisible to construct counting. Section 3.10 records "
     "hand-rolled locators observed in the wild, and the benchmark's own baseline arm "
     "(s1_direct) is exactly this style.", "Interpretive limit")

h("3.3 Key trends", 2)
bullet("Depends dominates but is not universal: 62.9% of real applications use it, and "
       "the 36.9% zero-DI cohort does not. DI is clearly not the mandatory "
       "architectural pattern of the FastAPI ecosystem.")
bullet("Generator/yield dependencies are more common (34.8%) than the "
       "Annotated[..., Depends] form (17.6%), despite the latter being the style the "
       "documentation presents as modern.")
bullet("Security is markedly underused (4.8%) despite being a headline feature for "
       "authentication, and its median usage among adopting repositories is a single "
       "call site.")
bullet("The core DI surface is small: four constructs cover essentially all framework DI "
       "in production FastAPI code. Router-level wiring, app-level wiring, dependency "
       "overrides and callable-class dependencies are compositions of C1/C2 and are never "
       "observed without a core construct.")

h("3.4 Corrected data defect (C3 volume)", 2)
p("The C3 call volume was overstated in an earlier extraction. Annotated[..., Depends] "
  "used as a function-parameter annotation was recorded twice — once by the "
  "per-argument path and once by the generic Subscript visitor — so 10,763 of 23,241 "
  "recorded sites (46%) were duplicates. The type-alias form was never affected, because "
  "only the generic path fires for it. The extractor is fixed, pinned by seven regression "
  "tests verified to fail against the pre-fix code, and the table in Section 3.1 reports "
  "the corrected volume.")
note("Blast radius is bounded and verified: repository-level prevalence is unchanged "
     "(384, 17.6%), and 0 of 2,179 repositories cross a core-count boundary, so no "
     "downstream classification or sampling frame is affected. Only C3 volume statistics "
     "were wrong. The frozen per-repository reports are deliberately left unmodified so "
     "the substrate a human audit rates against does not shift mid-audit.", "Scope")

h("3.5 Who uses DI", 2)
p("Who uses DI? Disaggregated by repository stars and age, using observed covariates "
  "rather than an invented application-class taxonomy.")
caption("Table 3.2 — Core DI adoption by stars")
table(
    ["Stars", "Repos", "% using core DI", "Median core calls"],
    [["0", "1,491", "61.0%", "6"], ["1-9", "567", "67.9%", "10"],
     ["10-99", "87", "69.0%", "16"], ["100+", "34", "58.8%", "3"]],
    widths=[0.9, 0.9, 1.4, 1.4],
)
caption("Table 3.3 — Core DI adoption by age")
table(
    ["Age", "Repos", "% using core DI", "Median core calls"],
    [["< 12 months", "1,903", "63.1%", "8"], ["12-36 months", "206", "63.6%", "6"],
     ["36+ months", "70", "61.4%", "8"]],
    widths=[0.9, 0.9, 1.4, 1.4],
)
rich([("DI prevalence is essentially flat across both covariates", "b"),
      (" (roughly 59-69% in every bucket, with no monotonic trend). Popularity and age "
       "do not predict DI adoption. The corpus skews young — 1,903 of 2,179 repositories "
       "are under a year old — which reflects the discovered population rather than the "
       "gate, since E3 admits repositories up to 60 months old. The two thinnest buckets "
       "(100+ stars, n=34; 36+ months, n=70) are reported for completeness and are too "
       "small to carry weight.", "")])

# ================= forms, relationships, roles =================
h("3.6 In what form are dependencies passed?", 2)
p("Presence alone does not say how a construct is used, so the second resolution is the "
  "argument each call site carries. This is relationship analysis over the same "
  "extraction, not token counting.")
caption("Table 3.4 — Argument shape of every Depends() call site")
table(
    ["Depends() argument shape", "Calls", "% of calls", "Repos"],
    [["bare function — Depends(get_db)", "94,889", "96.6%", "1,354"],
     ["module alias — Depends(deps.get_session)", "2,433", "2.5%", "54"],
     ["placeholder — Depends(<empty>)", "720", "0.7%", "120"],
     ["title-case class — Depends(HTTPBearer)", "178", "0.2%", "28"],
     ["classmethod — Depends(X.as_form)", "23", "0.0%", "4"]],
    widths=[3.3, 1.0, 0.95, 0.8],
)
p("The overwhelming idiom is passing a plain callable: 96.6% of call sites. No naive "
  "Depends(foo()) calls and no lambdas appear anywhere in the accepted census.")

h("3.7 What relationships do call sites form?", 2)
rich([("1,338 of 2,179", "b"), (" repositories have a non-empty dependency graph, "
      "containing 62,200 function nodes and 2,682 class nodes (4.1% class; 432 "
      "repositories contain class nodes) across 90,863 directed edges.", "")])
p("Within those, 708 fan-in hub nodes have ten or more dependents. This is the "
  "relationship-level signature of FastAPI DI: a small set of shared dependencies — auth "
  "guards, database sessions, current-user providers — each consumed by a large number "
  "of handlers.")
caption("Table 3.5 — Most frequent fan-in hub dependencies")
table(
    ["Hub dependency", "Dependents"],
    [["get_db", "24,014"], ["get_current_user", "11,432"], ["get_session", "5,014"],
     ["require_admin", "3,030"], ["require_permission", "1,764"],
     ["get_db_session", "1,390"], ["require_role", "1,349"], ["require_user", "960"]],
    widths=[2.2, 1.0],
)
p("Chained and nested dependencies exist at the graph level even though they are not a "
  "syntactic construct: edges whose target is itself a dependency, such as "
  "require_api_admin -> require_api_token and get_current_user -> get_session. Median "
  "depth is 2, maximum 7. This is why nested dependency is treated as a "
  "graph-topological property reported under RQ2 rather than as a prevalence counter.")

h("3.8 Annotated type roles", 2)
p("The types named inside Annotated[...] encode dependency semantics, dominated by "
  "request-context and session roles: AsyncSession (2,435), User (2,133), ActorContext "
  "(1,630), KernelContainer (1,312), Session (1,107), followed by principal and "
  "identity objects and configuration/registry types. These are what practitioners "
  "actually name as injected dependencies.")

h("3.9 Security scopes: a total non-adoption", 2)
rich([("Of 620 Security() call sites across 104 repositories, 0 pass scopes=[...]",
       "b"),
      (" — not one call, and not one repository. The OAuth2 scopes mechanism that "
       "FastAPI advertises for fine-grained authorisation is entirely unadopted in this "
       "population. Security(scheme) is used purely as a boolean-style flag, which makes "
       "it behaviourally interchangeable with Depends() in every observed use. This is "
       "the strongest non-obvious corpus-scale finding in Part I.", "")])

h("3.10 Idioms observed in the wild (low n, explicitly non-statistical)", 2)
p("Practitioners extend the documented API in ways the documentation does not teach. "
  "Counts are small and are reported as evidence-with-n, never as rates.")
caption("Table 3.6 — Idioms observed in the wild, reported as counts and never as rates")
table(
    ["Idiom", "Repos", "Evidence"],
    [["current_* request-scope injection", "76", "current_*_repository, current_audit_sink, "
      "current_tenant_authorization — request-scoped context objects"],
     ["module-alias dependencies", "54", "deps.get_session, dependencies.get_prefect_client_version"],
     ["class-as-dependency", "28 (38 classes)", "APIKeyAuth, AdminOnly, ArrestService, "
      "AttachmentRepo — constructor-injected classes"],
     ["classmethod-as-dependency", "6", ".as_form, .from_query_parameters, .has_permission, "
      ".is_authed — Pydantic models doubling as form-parsing dependencies"],
     ["provide_* service-locator dialect", "3", "a provide_* namespace acting as a "
      "hand-rolled service locator over DI"],
     ["*Repository-typed injection", "1", "repository pattern observed as an injected type"]],
    widths=[1.9, 0.85, 3.55],
)
note("The provide_* dialect matters for interpretation of Section 3.2: at least some "
     "repositories in the zero-DI cohort are not doing without dependency management, "
     "they are doing it by hand. The cohort is best read as 'no framework DI construct' "
     "rather than 'no DI discipline'.", "Reading")

# ================= 3.11 GRAPH DEPTH =================
h("3.11 How deep do dependency graphs go?", 2)
p("Restricted to the 1,338 repositories with a non-empty clean dependency graph. The "
  "remaining 841 produce no clean graph nodes the resolver can follow; resolver coverage "
  "is reported as a coverage metric rather than treated as a failure.")
caption("Table 3.7 — Graph complexity over the 1,338 graph-bearing repositories")
table(
    ["Metric", "Median", "IQR", "Max"],
    [["Clean nodes", "19.0", "7-48.8", "1,444"],
     ["Maximum depth", "2", "2-3", "7"],
     ["Unresolved share", "0.0%", "0.0-3.3%", "100%"]],
    widths=[1.6, 0.9, 1.0, 0.9],
)
bullet("817 of 1,338 (61.1%) graph-bearing repositories resolve completely cleanly.")
bullet("21 repositories are 100% unresolved — a small outlier set relying on patterns "
       "the static resolver cannot follow.")
bullet("Graphs are shallow in the median but not flat everywhere. The typical FastAPI DI "
       "graph is a shallow tree, which is consistent with the API's design philosophy of "
       "explicit, inspectable dependencies.")

h("3.11.1 The deep tail", 3)
p("The median depth of 2 conceals a small tail of repositories where dependencies chain "
  "through five or more callables. Isolating every repository with maximum depth >= 5:")
caption("Table 3.8 — Distribution of the deep tail (maximum depth >= 5)")
table(
    ["Depth", ">= 5 (tail)", "5", "6", "7"],
    [["Repositories (of 1,338 graph-bearing)", "58 (4.3%)", "43", "11", "4"]],
    widths=[2.6, 1.0, 0.6, 0.6, 0.6],
)
bullet("Every tail repository still has a fan-out hub (58 of 58). Depth is an overlay on "
       "the shared-hub pattern, not a replacement for it.")
bullet("Tail repositories are larger: median 116.5 clean nodes and 207 clean edges, against "
       "corpus medians of 19 nodes and 20 edges.")
bullet("Chains resolve cleanly (median unresolved 0.55%); 17 of 58 are fully resolved and "
       "still reach the reported depth as genuine callable chains.")
bullet("The deepest chains are layered service constructions. Every depth-7 chain reads "
       "endpoint -> service -> service -> service -> repository -> db; one example runs "
       "handle_swipes -> get_swipe_service -> get_spotify_service -> get_spotify_cache "
       "-> get_redis_client -> get_redis -> get_state.")
bullet("Tail repositories skew young (54 of 58 under 12 months) and low-star (36 of 58 "
       "zero-star). Deep chains are an early-architecture pattern, not a marker of "
       "sophistication at scale.")
rich([("Interpretation. ", "b"),
      ("The broad-and-shallow headline holds for the corpus and, notably, even for the "
       "4.3% deep tail. FastAPI DI permits chains reaching five to seven hops, but in "
       "practice they arise in smaller, younger applications that stack service layers "
       "end-to-end instead of converging on shared hubs.", "")])

h("3.11.2 Filtered artefact nodes", 3)
p("Module-scope Depends declarations — FastAPI(dependencies=[...]), router defaults — "
  "produced file:line placeholder nodes rather than callable names. These are filtered "
  "before complexity metrics are computed, and both raw and clean columns are retained in "
  "the graph output for transparency. The contamination was 2,656 nodes of 64,882 (4.1%) "
  "across 425 of 2,179 repositories, purely additive: all 1,338 graph-bearing "
  "repositories retain a non-empty clean graph. Construct counts derive from call "
  "sites rather than graph nodes and are unaffected.")

# ================= 4. SENSITIVITY =================
h("4. Sensitivity analysis", 1)
p("The E4 file-count threshold is the only discretionary numeric gate in corpus "
  "construction, so headline statistics were recomputed at every threshold from 2 to 8 "
  "over the accepted pool.")
caption("Table 4.1 — E4 threshold sensitivity")
table(
    ["Threshold", "Eligible N", "% using core DI", "Median depends_total (all)",
     "Median depends_total (users)"],
    [["2", "2,150", "63.1%", "8", "26"],
     ["3", "1,720", "70.2%", "13", "30"],
     ["4 (base)", "1,451", "76.2%", "19", "35"],
     ["5", "1,284", "79.4%", "24", "40.5"],
     ["6", "1,167", "80.8%", "27", "45"],
     ["8", "937", "84.1%", "41", "55.5"]],
    widths=[0.85, 0.8, 1.05, 1.5, 1.6],
    bold_rows=(2,),
)
rich([("Qualitative conclusions are stable across every threshold.", "b"),
      (" Tightening the gate raises DI adoption (63.1% to 84.1%) and per-repository call "
       "counts monotonically: larger applications use DI more. Threshold 2 is near-null "
       "(2,150 of 2,179 pass), so sensitivity analysis is only meaningful above the base, "
       "where both quantities climb without reordering.", "")])

# ================= 5. RQ3 BENCHMARK =================
h("5. RQ3 — Runtime performance differences among the observed DI approaches", 1)
rich([("The census establishes which DI patterns exist. It cannot say what any of them "
       "cost, because in real code the pattern, the workload, the database and the "
       "author's skill all vary together. Part II breaks that confound by construction: "
       "one application, one workload, five DI mechanisms, two execution models, four "
       "load levels, twelve repetitions.", "")])

h("5.1 Patterns under test", 2)
p("Five resolution mechanisms, each implemented as a full 12-route read-only "
  "application over an identical service layer. All arms perform identical work, "
  "verified rather than asserted (Section 5.5).")
caption("Table 5.1 — The five dependency-resolution mechanisms")
table(
    ["Arm", "Pattern", "Mechanism", "Corpus evidence"],
    [["s1_direct", "Direct call (baseline)", "Handler calls the service function "
      "explicitly inside a connection context; no DI framework", "805 repos (36.9% of the "
      "cohort) show no framework DI construct"],
     ["s2_depends", "Function Depends", "Depends(get_db) with a chained provider graph: "
      "get_db -> get_current_user -> require_user / require_admin", "96.6% of all Depends "
      "sites pass a bare function"],
     ["s3_middleware", "ASGI middleware injection", "Middleware resolves the context once "
      "and places it on the request; handlers read it", "Hand-rolled and framework "
      "middleware attested in the corpus"],
     ["s4_container", "Declarative container", "dependency-injector DeclarativeContainer "
      "with Singleton providers, resolved from application state", "708 fan-in hubs; "
      "24,014 get_db dependents"],
     ["s4_dishka", "Full DI library", "dishka Provider/Scope with FromDishka[...] markers "
      "and DishkaSyncRoute / DishkaRoute", "Third-party container idiom"]],
    widths=[1.25, 1.05, 2.35, 2.05],
    mono_cols=(0,),
)

h("5.2 Design", 2)
caption("Table 5.2 — Factorial design")
table(
    ["Factor", "Levels", "Count"],
    [["DI pattern", "s1_direct, s2_depends, s3_middleware, s4_container, s4_dishka", "5"],
     ["Execution model", "sync, async (dependency callables)", "2"],
     ["Offered load", "600, 700, 800, 900 requests/second", "4"],
     ["Repetitions", "12 per cell", "12"],
     ["Study cells", "5 x 2 x 4 x 12", "480"],
     ["Host-drift reference cells", "after study cell 0, 96, 192, 288, 480", "5"],
     ["Total measured cells", "", "485"]],
    widths=[1.85, 3.55, 0.9],
    bold_rows=(4, 6),
)
p("Ten arms, each a complete 12-route application. The endpoint surface is identical "
  "across arms by construction and is verified by the smoke gate.")

h("5.3 Held constant", 2)
bullet("Service layer — all query and serialisation logic lives in one shared module "
       "imported unchanged by every arm.")
bullet("Database — a read-only SQLite database, sha256 ec432e82...; the hash is recorded "
       "before and after every cell, and was unchanged on all 480 study cells.")
bullet("Endpoint surface — exactly 12 read routes; documentation routes disabled so the "
       "exposed surface is identical.")
bullet("Connection pool — POOL = 8, with the anyio default thread limiter set to the same "
       "value during the run, not only at shutdown.")
bullet("Host and pinning — one server process per physical core, load generator and "
       "sampler isolated, sibling hyperthreads taken offline.")
bullet("Client — k6 2.2.0, one constant arrival-rate workload, identical thresholds and "
       "request mix for every arm.")
bullet("Runtime versions — Python 3.12.15, FastAPI 0.141.1, Starlette 1.6.0.")

h("5.4 Instrumentation and metrics", 2)
p("Each cell records 53 fields. The primary metric is client-observed p99 latency; "
  "server-side and host-side telemetry are recorded alongside so that a latency "
  "difference can be attributed rather than merely observed.")
caption("Table 5.3 — Recorded metrics")
table(
    ["Group", "Fields"],
    [["Latency", "cell and window p50 / p95 / p99 / max, HTTP p50 / p95 / p99 / max, "
      "startup time"],
     ["Throughput", "offered rate, achieved rate, request counts, dropped iterations, "
      "check failures"],
     ["Fidelity", "load fidelity (achieved / offered), window error rate"],
     ["Resource", "CPU seconds, CPU seconds per request, peak RSS (live per-process VmHWM)"],
     ["Host", "CPU steal jiffies, CPU model, physical and logical core counts, memory, "
      "kernel, offlined siblings, plan type"],
     ["Integrity", "database hash before and after, unchanged flag, return code, timeout "
      "flag, wall seconds"]],
    widths=[1.0, 5.7],
)

h("5.5 Validity controls", 2)
p("A latency measurement is only worth as much as the controls around it. Five controls "
  "were specified before measurement and are reported as outcomes, not intentions.")

h("5.5.1 Identical-work verification", 3)
p("Before any timing is trusted, every arm is shown to perform the same work. All ten "
  "arms return byte-identical response bodies on all 12 routes, and all ten produce the "
  "same work counters: 12 checkouts, 22 SQL statements, 93 result rows and 13 service "
  "calls. A DI pattern that did less work would be faster for the wrong reason.")
p("Two sets of counters do differ, and the difference is the point rather than a "
  "discrepancy. The middleware arm records one context object per request and non-zero "
  "current-user and bearer-token resolution on the six guarded routes, where the "
  "direct-call arm records zero. Those counters record that a DI mechanism ran; they are "
  "not work performed. The work counters above are identical across all ten arms.")

h("5.5.2 Concurrency gate", 3)
p("Each arm is driven concurrently through real sockets, not sequentially, because "
  "sequential exercise cannot detect a lock or admission defect that only manifests "
  "under contention. All ten arms complete 256 of 256 requests at concurrency 64 against "
  "a pool of 8, with zero timeouts, zero server errors and no arm failing to return. The "
  "gate's own recorded evidence is committed alongside the results.")

h("5.5.3 Load-fidelity floor", 3)
p("A cell that cannot sustain its offered load is evidence that the arm saturated, not "
  "evidence about its latency. Cells below 95% load fidelity are therefore excluded from "
  "the primary comparison and reported separately as saturation evidence. Sensitivity "
  "floors of 90% and 98% are specified in advance. No cell in the reported run fell "
  "below the floor at any of the three settings.")

h("5.5.4 Host-drift references", 3)
p("A fixed low-rate reference arm is measured five times across the run, at fixed "
  "positions after study cells 0, 96, 192, 288 and 480. This bounds host drift within "
  "the session and identifies which cells are confounded with time. CPU steal was zero at "
  "every reference, and the client-observed p95 of the reference varied by 8.1% "
  "peak-to-peak around a 0.89 ms median over the roughly seven-hour session. That is "
  "below the pre-registered 10% tolerance at p95, but it is not zero, and its direction "
  "is upward: the reference p99 rose 10.3% peak-to-peak, or 0.14 ms in absolute terms. "
  "The reference is discussed further in Section 6.7, because the drift is real and its "
  "consequences for the design are not uniform.")

h("5.5.5 Provenance hashing", 3)
p("The measurement code is hashed component by component — 14 components including the "
  "application generator, the k6 harness, the runner, the database builder, the analyser "
  "and the concurrency gate — and the combined hash is frozen before the run. Each cell "
  "additionally records the database hash before and after, so a cell that mutated shared "
  "state would be detectable rather than assumed absent. All 12 measurement-side "
  "components still hash to their pre-run values; the two interpretation-side components "
  "changed after the run, for the reasons given in Section 6.7, and are reported "
  "separately.")

h("5.6 Execution and data quality", 2)
caption("Table 5.4 — Data quality, reported run")
table(
    ["Check", "Result"],
[["Cells measured", "485 of 485 (480 study + 5 drift references), 0 failures"],
      ["Load fidelity", "minimum 0.9847, median 0.9999; 0 cells below the 0.95 floor"],
      ["Window error rate", "0 in all 480 study cells"],
      ["Database integrity", "hash unchanged on 480 of 480 cells"],
      ["Host drift", "reference p95 spread 8.1%, p99 spread 10.3% over the session "
       "(Section 6.7); 0 steal jiffies at every reference"],
      ["Steal across all cells", "maximum 4 jiffies"],
      ["Config hash", "frozen pre-run, 14 components; all 12 measurement-side components "
       "still match, 2 analysis-side components changed post-run (Section 6.7)"],
      ["Grid completeness", "40 of 40 conditions complete, 0 shortfalls, 0 absent"]],
    widths=[1.5, 5.2],
)

h("5.7 Results: cost of each DI pattern against a direct call", 2)
p("The primary comparison. Each pattern is compared against the s1_direct baseline — "
  "no DI framework — within the same execution model, so the contrast isolates the "
  "resolution mechanism. Values are median p99 latency differences in milliseconds; "
  "positive means the DI pattern is slower than the direct call. Twelve paired "
  "repetitions per cell, exact order-statistic intervals at nominal 95%.")
verdict_key()

caption("Table 5.5 — DI pattern versus direct call, sync execution (ms, p99)")
table(
    ["Pattern", "@600", "@700", "@800", "@900"],
    [["s2_depends", "+3.53 *", "+5.87 *", "+8.89 *", "+15.43 *"],
     ["s3_middleware", "+4.68 *", "+7.25 *", "+9.16 *", "+19.67 *"],
     ["s4_container", "+0.10", "-0.24 =", "-0.29", "-0.77"],
     ["s4_dishka", "+15.67 *", "+17.52 *", "+20.21 *", "+21.63 *"]],
    widths=[1.3, 1.2, 1.2, 1.2, 1.2],
    mono_cols=(0,),
)
note("* = meaningful beyond the practical margin;  = = practically equivalent. Full "
     "intervals in Section 6.6.", "Key")

caption("Table 5.6 — DI pattern versus direct call, async execution (ms, p99)")
table(
    ["Pattern", "@600", "@700", "@800", "@900"],
    [["s2_depends", "+0.55", "+0.10", "+1.66", "+1.27"],
     ["s3_middleware", "+3.47 *", "+5.97 *", "+8.06 *", "+17.22 *"],
     ["s4_container", "-0.58", "-1.27", "-0.73", "-1.38"],
     ["s4_dishka", "+15.52 *", "+21.09 *", "+25.70 *", "+27.91 *"]],
    widths=[1.3, 1.2, 1.2, 1.2, 1.2],
    mono_cols=(0,),
)

rich([("The central finding: the execution-model effect on DI cost is not uniform — it "
       "depends on which DI mechanism is in use.", "b"),
      (" Plain function Depends is the community's dominant idiom — 96.6% of all call "
       "sites — and it is expensive under synchronous execution, costing up to "
       "+15.4 ms of p99 latency over a direct call at 900 requests/second. Under "
       "asynchronous execution the same pattern shows no difference from the direct call "
       "that the interval can separate from the practical margin, at any load. "
       "The cached container (s4_container) is the only other pattern with no meaningful "
       "cost under sync, and it shows none under async either. Middleware injection "
       "and the full dishka container pay under both, and dishka pays the most "
       "everywhere, from +15.5 ms to +27.9 ms. Neither execution model nor DI pattern "
       "dominates the other; the interaction between them is the result.", "")])
p("This pattern is consistent with a specific, checkable difference in how the two "
  "execution models resolve a dependency. A synchronous dependency callable must be "
  "dispatched to a bounded worker thread, because blocking the event loop is not "
  "permitted; an async dependency callable resolves inline on the loop. The DI overhead "
  "that looks like a property of the framework is therefore partly the cost of crossing "
  "into a thread. s2_depends is the case where that crossing is close to pure overhead — "
  "a session factory call that returns a connection — which is why its penalty appears "
  "under sync and vanishes under async. s4_container shows no penalty in either model, "
  "which is what a resolve-once-and-cache provider should produce: per-request resolution "
  "becomes a dictionary lookup rather than a thread hop. dishka pays under both models, "
  "which is what per-resolution scope bookkeeping and marker resolution would produce. "
  "The design controls rule out the alternatives that would also fit these numbers — "
  "identical work, identical database, identical response bodies, host drift bounded at "
  "8.1% of a sub-millisecond reference with zero CPU steal, and a baseline that contains "
  "no DI mechanism at all — so the differences are attributable to the resolution path "
  "rather than to the amount of work performed.")

h("5.8 Results: sync versus async within each pattern", 2)
p("The complementary comparison, holding the pattern fixed and varying only the "
  "execution model of the dependency callables. Negative means async is faster.")
caption("Table 5.7 — Async minus sync within pattern (ms, p99)")
table(
    ["Pattern", "@600", "@700", "@800", "@900"],
    [["s1_direct", "+0.59", "+1.33", "+0.78", "+2.45"],
     ["s2_depends", "-2.07 *", "-2.67 *", "-6.08 *", "-10.76 *"],
     ["s3_middleware", "-0.48", "+0.90", "+0.08", "+1.12 (unstable)"],
     ["s4_container", "+0.71", "+0.53", "+1.00", "+2.50"],
     ["s4_dishka", "+0.63 =", "+3.52 *", "+4.78", "+10.10 *"]],
    widths=[1.3, 1.05, 1.05, 1.05, 1.45],
    mono_cols=(0,),
)
p("The two analyses agree from different directions. s2_depends is the only pattern that "
  "clearly prefers async, and it is the only pattern whose DI overhead disappears under "
  "async; dishka is the only pattern that clearly prefers sync under load. The baseline "
  "and the cached container show no execution-model effect worth reporting, which is the "
  "necessary control: if async were faster for reasons unrelated to DI, that difference "
  "would appear in the baseline too. It does not.")

h("5.9 Secondary metrics", 2)
p("Client-observed p95 reproduces the direction and rough magnitude of the p99 result "
  "without relying on it: s2_depends is faster under async at every load, with the gap "
  "reaching -8.18 ms at 900 requests/second, and no other pattern produces a comparably "
  "sized or consistent secondary effect. The conclusion does not depend on the choice of "
  "percentile.")

h("5.10 What the benchmark supports", 2)
bullet("Within this application, workload, host and load range: the cost of a DI "
       "mechanism is not fixed, and depends on the execution model it is combined with.")
bullet("Plain Depends is not 'slow'. Its measured cost under async is indistinguishable "
       "from zero at every load tested, while under sync it is the largest of the three "
       "framework-native costs. Advice to avoid Depends on performance grounds is, in this "
       "design, measuring the thread hop rather than the framework.")
bullet("Among DI mechanisms, a cached container is the cheapest tested under either "
       "execution model, which makes container scope and caching the variable that matters "
       "rather than 'containers versus functions'.")
bullet("Full container libraries are the most expensive option tested and do not benefit "
       "from async execution.")

h("5.11 What the benchmark does not support", 2)
bullet("No claim about maintainability, readability or developer productivity. These are "
       "runtime measurements; the design cannot speak to code quality.")
bullet("No claim that these effects generalise to other frameworks, other databases, or "
       "write-heavy workloads. The read path only was measured.")
bullet("No ranking of patterns for adoption. A mechanism that is fast here may be slower "
       "to write, and that trade is outside the design.")
bullet("No claim about host portability. The result is tied to a pinned 4-core AMD EPYC "
       "configuration; the direction of the thread-hop mechanism should hold broadly, "
       "but the magnitudes are host-specific.")

# ================= 6. ANALYSIS NOTES =================
h("6. Analysis notes", 1)

h("6.1 Estimator and interval method", 2)
p("The primary interval is an exact binomial sign / order-statistic interval for the "
  "median of paired differences, chosen because it makes no distributional assumption "
  "and reports attained coverage per cell. A percentile bootstrap with 10,000 resamples "
  "is computed as a sensitivity analysis and is never primary. Pairing is on repetition "
  "index: the two arms of a pair occupy adjacent slots in the same (rate, repetition) "
  "block, so host state at that slot is common to both and cancels from the difference. "
  "Attained coverage was 0.96 on all 20 execution-model comparisons.")

h("6.2 Practical margin", 2)
p("Statistical significance is not a useful threshold for a latency question, so each "
  "comparison is also judged against a practical margin of 10% of that pair's own "
  "baseline. The margin is relative rather than absolute so that it scales with the "
  "regime: a 1 ms difference is material at 5 ms and immaterial at 50 ms. The margin is "
  "calibrated on within-condition repeatability rather than between-condition "
  "differences, so it asks whether an observed gap is large relative to the noise the "
  "instrument produces on a single arm.")

h("6.3 Sensitivity to the fidelity floor", 2)
p("Recomputing the full analysis at fidelity floors of 0.90 and 0.98 retains all 480 "
  "study cells, because the lowest observed fidelity in the run is 0.9847. No headline "
  "verdict depends on the floor setting.")

h("6.4 Completeness and dispersion diagnostics", 2)
p("All 40 conditions are complete at 12 repetitions: no shortfalls, no absent cells, no "
  "failed cells. Had any arm starved, the analyser reports it as an explicit absence "
  "rather than silently narrowing, and distinguishes a condition that never ran from one "
  "whose every cell was excluded as sub-floor — a distinction that matters because the "
  "second is evidence about the arm while the first is a gap in the grid.")
p("Separately, a cell whose repetitions disperse by more than 2.5x their own median is "
  "flagged, because a wide interval caused by a bimodal arm is not the same evidence as a "
  "wide interval caused by sampling noise. On this run the diagnostic flags one cell of "
  "480 — s3_middleware@900, in both of its arms (Section 6.5). The next highest "
  "dispersion anywhere in the run is 1.82, so the flag separates a bimodal cell from the "
  "rest of the grid by an order of magnitude rather than by a hair. The threshold was "
  "checked against synthetic arms with known dispersion and does not fire on "
  "well-behaved data.")

h("6.5 One non-interpretable cell", 2)
rich([("s3_middleware at 900 requests/second", "b"),
      (" is genuinely bimodal in both arms and does not support a central-tendency "
       "claim. In the async arm, 3 of 12 repetitions reach 70-191 ms against a median of "
       "29 ms (6.6x dispersion) while p50 stays near 0.7 ms — tail inflation rather than "
       "a shifted distribution. In the sync arm, 4 of 12 repetitions reach 74-495 ms "
       "against a median of 29 ms (17.0x dispersion), and the worst repetition has a "
       "median of 166 ms with 326 dropped iterations, which is whole-distribution "
       "collapse rather than a tail.", "")])
p("This is not host instability. Steal was zero at every drift reference and the "
  "reference cell's own p95 varied only 8.1% across the whole session, far less than the "
  "17x spread inside this one arm, and the arm's other three load levels are unremarkable "
  "(maximum-to-median ratios of 1.06-1.35). It is a property of this arm at this load, "
  "and the honest reading "
  "is that middleware injection is intermittently unstable at 900 requests/second under "
  "both execution models. Its interval is reported but should not be read as a measured "
  "difference, and the row is not counted as evidence that async and sync are equivalent "
  "here. The dispersion diagnostic that catches this case is part of the analysis, not a "
  "post-hoc inspection.")

h("6.6 Full intervals", 2)
p("Complete exact intervals for all 20 execution-model comparisons and all 32 "
  "pattern-versus-baseline comparisons, across 13 metrics, are in the committed analysis "
  "output (Section 8).")

h("6.7 Post-run analysis changes, and what they do and do not touch", 2)
p("Two analysis-side components were changed after the run completed. Both changes are "
  "reported here rather than folded silently into the results, because the pre-run "
  "config hash covers them.")
bullet("drift_report.py. The report originally read the reference cell's p95 from a "
       "column stored as whole milliseconds. At a 200 requests/second reference every "
       "value rounds to 1.00 ms, so the spread computed as exactly 0.0% — a property of "
       "the field's storage precision rather than a measurement of the host. The report "
       "now reads the client-observed percentile, which has sub-millisecond resolution, "
       "and additionally reports the primary metric's percentile. The corrected figures "
       "are 8.1% peak-to-peak spread at p95 and 10.3% at p99, not 0.0%.")
bullet("analyze.py. Completeness reporting was corrected so that a condition whose cells "
       "were all excluded as sub-floor is not also described as never run, and a "
       "dispersion diagnostic was added that flags any cell whose repetitions spread by "
       "more than 2.5x their own median. On this run it flags exactly one cell, "
       "s3_middleware@900 (Section 6.5), and no verdict changes.")
p("Neither component emits a load, selects a rate, or reads a measured cell into an "
  "aggregate. All 12 measurement-side components — the shared service layer, the routes, "
  "the application generator, the runner and connection pool, the host pinning script, "
  "the orchestrator, the k6 harness, the database builder and seed, the smoke test, the "
  "bootstrap script and the concurrency gate — still hash to their pre-run values, and "
  "the 485 recorded cells are byte-identical to what the host wrote. The changes affect "
  "how the run is summarised, not what was measured.")
rich([("The drift is real, upward, and its consequences are not uniform.", "b"),
      (" A 0.14 ms rise in reference p99 across seven hours could in principle "
       "accumulate across the session and inflate absolute latencies at later rates. It "
       "does not bias the reported differences, for two structural reasons. The run is "
       "rate-major, so time is confounded with offered rate and not with arm: every rate "
       "gets the same exposure to drift. And the two arms of every pair occupy adjacent "
       "slots roughly 30 seconds apart, which is about 0.03% of the session's drift, so "
       "the drift is effectively common-mode within a pair and cancels from the "
       "difference. What remains true is that absolute p99 values at 800 and 900 "
       "requests/second may be marginally inflated relative to 600, and the study reports "
       "differences rather than absolute values for exactly this reason.", "")])

# ================= 7. LIMITATIONS =================
h("7. Limitations and elements we do not defend", 1)
p("This section collects the elements of the study that we consider genuinely "
  "non-defensible or insufficiently supported, stated plainly rather than softened.")

h("7.1 Star counts are not a usable selection criterion", 2)
rich([("Across the accepted population, stars have essentially no relationship to the "
       "quantity the study measures.", "b"),
      (" The Spearman rank correlation between stargazers and Depends call sites is "
       "+0.080; against FastAPI-importing files it is +0.088 and against FastAPI "
       "application count +0.087. Ranking repositories by stars therefore selects "
       "largely on an axis orthogonal to the object of study. Wiring density is not "
       "concentrated at the top of the ranking either: among the 1,688 accepted "
       "repositories with at least 20 production files, Depends call sites per "
       "production file have a median of 0.15 and a 90th percentile of 1.50, and the "
       "single most-starred repository in the corpus sits at 0.27 — above the median "
       "but at roughly half the 90th percentile.", "")])
rich([("Selecting a real-repository tier by star count would be indefensible on this "
       "evidence.", "b"),
      (" Any such tier should be selected on wiring structure, with stars reported as a "
       "descriptive covariate and the rejection of star-based selection stated "
       "explicitly.", "")])

h("7.2 One repository's star count is not credible", 2)
p("The highest-ranked repository in the corpus carries 84,888 stars against 349 forks — "
  "a ratio of 243:1 — accumulated in under four months since its recorded creation date. "
  "That profile is not consistent with organic adoption, and we treat the metadata "
  "as an artefact of capture rather than as traction. It is excluded by rule in the "
  "downstream selection (age at least one year at snapshot, and a stars-to-forks ratio "
  "at most 100) rather than by assertion.")

h("7.3 Two of the three most-starred repositories have no dependency injection at all", 2)
p("The second- and third-ranked repositories by stars have zero Depends call sites. One "
  "is TypeScript-primary (Python at 36.6% of files) with FastAPI as a thin serving layer "
  "over a computer-vision pipeline: 9,954 stars, 16 FastAPI-importing files, one FastAPI "
  "application, no Depends. The other is a Java project whose clone is 2.8 GB, with "
  "Python at 0.5% of files: 6,209 stars, three FastAPI-importing files, one FastAPI "
  "application, no Depends. Neither possesses the independent variable the study "
  "manipulates, so neither can be a subject of a before-and-after DI transform. This is "
  "the concrete reason star-based selection was rejected rather than merely disfavoured.")

h("7.4 One benchmark cell does not support a claim", 2)
p("s3_middleware at 900 requests/second, as set out in Section 6.5. We report it and "
  "decline to interpret it as a measured difference.")

h("7.5 Population attrition", 2)
p("224 of 5,000 candidates (4.5%) could not be cloned and are recorded as permanent "
  "attrition. If deletion is correlated with abandonment, and abandonment with "
  "architectural style, the accepted population is biased toward maintained code. The "
  "direction and size of that bias cannot be estimated from what is observed.")

h("7.6 Resolver coverage", 2)
p("841 of 2,179 accepted repositories (38.6%) yield an empty dependency graph despite "
  "passing all four eligibility rules. Graph statistics in Section 3.11 therefore describe "
  "1,338 repositories, not the corpus, and the 841 are not a random subset — the static "
  "resolver cannot follow certain cross-file and dynamic patterns. Graph findings "
  "generalise to the resolvable subpopulation only.")

h("7.7 The zero-DI cohort is a construct measure, and its recall is unaudited", 2)
p("805 repositories are recorded as using no DI construct. As Section 3.2 and the "
  "provide_* idiom in Section 3.10 show, at least some of these hand-roll dependency "
  "management. The cohort should be read as 'no framework DI construct observed', not as "
  "'no dependency management', and the census cannot quantify what these repositories do "
  "instead without a different analysis.")
p("The extractor is verified for precision but not for recall. A 40-repository probe "
  "confirms 98.42% of recorded call sites are real; nothing in the committed analysis "
  "bounds how many real call sites were missed. A pre-registered audit exists for exactly "
  "this purpose — an 80-repository draw from the zero-DI frame to bound the false-negative "
  "rate, with a gate of four or more misses in 80 halting all headline reporting, plus a "
  "200-repository draw from the has-DI frame for prevalence with a Wilson interval. That "
  "audit has not reported. Until it does, the 36.9% figure is a floor on undetected DI, "
  "not a measurement of it, and the corpus-wide prevalence claims in Section 3.1 inherit "
  "that uncertainty. The instrument was revised once during fielding, and that revision "
  "is documented as a dated deviation in the pre-registration rather than corrected "
  "silently.")

h("7.8 Withdrawn: the LLM strategy-attribution census", 2)
p("An earlier attempt to assign each repository a dominant wiring strategy using a local "
  "model produced a four-way split of 1,188 / 712 / 268 / 11 repositories. It is "
  "withdrawn from this study. It agreed with the deterministic extractor on 56.4% of "
  "repositories against a 55% majority-class baseline, and inspection of its inputs showed "
  "the defect that mattered: the token settings matched benign configuration identifiers "
  "and consumed roughly two thirds of the excerpt budget, so only 8% of evidence packs "
  "contained a single real Depends call. Repositories with hundreds of call sites were "
  "presented to the model as configuration plumbing.")
p("The per-repository labels remain on disk as provenance so the reasoning stays "
  "auditable, but they are quarantined from the analysis: no figure in this draft derives "
  "from them, and the deterministic 805-repository zero-DI cohort — not the model's 1,188 — "
  "is the number reported. The 327-repository peer review built to adjudicate the model's "
  "disagreements is retired with it. Manual and external strategy prevalence remains "
  "unquantified pending the audit in Section 7.7.")

h("7.9 The exploratory pattern comparison is not comparable", 2)
p("The maintainability-proxy comparison (styles against hygiene, sophistication, "
  "open issues, contributor counts) and its runtime micro-benchmark derive from an "
  "earlier 402-repository run and were never refreshed to the 2,179 census. Their "
  "effect sizes are not comparable with the RQ1-RQ2 figures and are superseded in "
  "substance by Part II. They are not reproduced here. The census figures stand; those "
  "do not.")

h("7.10 Design scope of the benchmark", 2)
bullet("Read paths only. Write-heavy workloads, cold caches and multi-process deployments "
       "are outside the design.")
bullet("One application and one workload shape. The magnitude of each effect is a "
       "property of this application; the direction of the execution-model interaction is "
       "the transferable claim.")
bullet("Measured drift bounds drift for this session only and is not a claim that the "
       "host is stable in general or across sessions. The drift that was measured is "
       "small and upward; Section 6.7 gives its magnitude and explains why it does not "
       "bias the reported differences, while conceding that absolute latencies at higher "
       "rates may be marginally inflated.")
bullet("The 10% practical margin is a stated convention, not a distribution-derived "
       "threshold, chosen so that 'significant' means 'large enough to care about'.")
bullet("Sparse covariate buckets in Section 3.5 (100+ stars, n=34; 36+ months, n=70) are "
       "reported for completeness and are too thin to support conclusions.")

# ================= 8. ARTIFACTS =================
h("8. Artifacts", 1)
p("All paths are relative to the repository root. Corpus and census artifacts are "
  "schema-versioned and derived from committed source. "
  "The benchmark artifacts are not regenerable claims — they are measurements — so they "
  "are preserved verbatim: the benchmark host was ephemeral, and its complete state was "
  "retrieved and SHA256-verified before the machine was destroyed. The verified copy is "
  "committed, and the primary dataset hash is recorded so any later edit to it is "
  "detectable.")

caption("Table 8.1 — Corpus and census artifacts")
table(
    ["Artifact", "Description"],
    [["corpus/candidates.json", "5,000 enriched candidates"],
     ["corpus/manifest.json", "2,179 accepted repositories with metadata and extractor snapshots"],
     ["corpus/exclusion_log.json", "2,821 exclusions with first failing rule"],
     ["corpus/reports/*.json", "Per-repository extractor report"],
     ["corpus/raw_dependents/", "167 snapshotted dependents pages"],
     ["analysis/out/rq1_constructs.csv", "Construct prevalence (C1-C4)"],
     ["analysis/out/usage_patterns.csv", "Argument shapes, scopes, graph topology, annotated roles"],
     ["analysis/out/rq4_graphs.csv", "Per-repository graph statistics"],
     ["analysis/out/covariates.csv", "Stars, age, coverage, language share"],
     ["analysis/out/sensitivity.csv", "File-threshold sensitivity"]],
    widths=[2.3, 4.4],
    mono_cols=(0,),
)

caption("Table 8.2 — Benchmark artifacts")
table(
    ["Artifact", "Description"],
    [["analysis/syncasync/box6_snapshot/results/main/cells.csv",
      "All 485 measured cells, 53 fields each"],
      ["analysis/syncasync/box6_snapshot/results/main/plan.json",
      "Frozen run plan and design"],
      ["analysis/syncasync/box6_snapshot/run_main.log", "Complete run log"],
      ["analysis/syncasync/box6_snapshot/results/config_hash.json",
      "Frozen 14-component measurement hash"],
      ["analysis/syncasync/box6_snapshot/results/topology.json",
      "Host pinning layout as captured on the host"],
      ["analysis/syncasync/box6_snapshot/results/work_equiv/",
      "Identical-work evidence, all 10 arms"],
      ["analysis/syncasync/box6_snapshot/results/concurrency_gate.json",
      "Concurrency gate result"],
      ["analysis/syncasync/box6_snapshot/results/smoke_equivalence.json",
      "Endpoint-surface equivalence"],
      ["analysis/syncasync/box6_snapshot/results/reviewgate_ro.db",
      "Read-only benchmark database"],
      ["analysis/syncasync/results/final_r2.json",
      "All comparisons: 20 execution-model, 32 pattern-vs-baseline, 13 metrics"],
      ["analysis/syncasync/results/analysis_http_p99.txt", "Primary analysis report"],
      ["analysis/syncasync/results/drift_report.txt", "Host-drift report"]],
    widths=[3.05, 3.6],
    mono_cols=(0,),
)
note("The seed database is rebuilt byte-identically by its builder and its hash is "
     "recorded in the pre-registration, so the binary itself need not be tracked; it is "
     "retained here anyway because the ephemeral host that produced the measurements no "
     "longer exists.", "Note")

# ================= 9. PLANNED =================
h("9. Planned work — RQ4", 1)
rich([("RQ4 — real-repository validation.", "b"),
      (" The benchmark establishes mechanism cost on a synthetic application. The "
       "outstanding question is whether real repositories' wiring choices reproduce that "
       "ordering. The selection rule below is the design adopted for RQ4 and follows "
       "directly from Section 7.1: candidates are drawn on dependency-injection structure "
       "rather than popularity, requiring sufficient wiring to make a before-and-after "
       "transform measurable, a size band small enough to run and attribute, at least one "
       "guarded dependency so that injection is load-bearing rather than decorative, a "
       "permissive licence, and the maturity and plausibility screen of Section 7.2. "
       "Repositories are chosen for wiring diversity rather than rank. Star counts are "
       "reported as a covariate of the selected set, together with the reason star-based "
       "selection was rejected. The specific repositories, the number of arms per "
       "repository, and the repetition count are fixed at preregistration before any "
       "measurement is run.", "")])
rich([("Every candidate must clear the full pre-flight gate before any measurement run "
       "begins", "b"),
      (" — application boot at a pinned commit, per-repository per-arm semantic "
       "equivalence, the concurrency gate, fixture-seed determinism across repeats, and a "
       "frozen configuration hash. A repository failing any gate is replaced before the "
       "run rather than during it.", "")])
bullet("Temporal analysis of DI usage evolution, requiring per-repository git history.")
bullet("A change-cost experiment, which is the only design able to support a causal "
       "claim about which pattern is better to maintain.")
bullet("Refresh of the exploratory maintainability comparison to the full census, or "
       "formal withdrawal of it.")

# ================= FOOTER NOTE =================
doc.add_paragraph()
fp = doc.add_paragraph()
fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
r = fp.add_run("End of Result Draft 02")
r.italic = True
r.font.size = Pt(9)
r.font.color.rgb = RGBColor(0x80, 0x80, 0x80)

# ================= TOC (assembled here, then relocated to the anchor) =================
import json

TOC_PAGES = {}
_tp_path = os.environ.get("TOC_PAGES")
if _tp_path and os.path.exists(_tp_path):
    with open(_tp_path) as fh:
        TOC_PAGES = json.load(fh)
TOC_LEVELS = (1, 2)
_toc_first = len(doc.element.body) - 1

_chead = doc.add_paragraph("Contents", style="Heading 1")

_p = doc.add_paragraph()
_p.paragraph_format.space_after = Pt(0)
for _kind, _txt in (("begin", None), ("instr", r' TOC \o "1-2" \h \z \u '),
                    ("separate", None)):
    _r = _p.add_run()
    if _kind == "instr":
        _el = OxmlElement("w:instrText")
        _el.set(qn("xml:space"), "preserve")
        _el.text = _txt
    else:
        _el = OxmlElement("w:fldChar")
        _el.set(qn("w:fldCharType"), _kind)
    _r._r.append(_el)

_entries = [(lvl, txt) for lvl, txt in HEADINGS if lvl in TOC_LEVELS]
for _lvl, _txt in _entries:
    _e = doc.add_paragraph()
    _pf = _e.paragraph_format
    _pf.space_after = Pt(1)
    _pf.space_before = Pt(2 if _lvl == 1 else 0)
    _pf.left_indent = Inches(0.0 if _lvl == 1 else 0.28)
    _pf.tab_stops.add_tab_stop(Inches(6.7), WD_TAB_ALIGNMENT.RIGHT,
                               WD_TAB_LEADER.DOTS)
    _r = _e.add_run(_txt + "\t")
    _n = _e.add_run(str(TOC_PAGES.get(_txt, "")))
    _n.font.size = Pt(10.5 if _lvl == 1 else 10)
    _n.bold = _lvl == 1

_pe = doc.add_paragraph()
_pe.paragraph_format.space_after = Pt(0)
_re = _pe.add_run()
_fc = OxmlElement("w:fldChar")
_fc.set(qn("w:fldCharType"), "end")
_re._r.append(_fc)

_pb = doc.add_paragraph()
_pb.add_run().add_break(WD_BREAK.PAGE)

# relocate the assembled block from the end of the body to the anchor point
_body = doc.element.body
_moved = list(_body)[_toc_first:-1]
for _el in _moved:
    _body.remove(_el)
for _off, _el in enumerate(_moved):
    _body.insert(TOC_ANCHOR + _off, _el)

_settings = doc.settings.element
_uf = _settings.find(qn("w:updateFields"))
if _uf is None:
    _uf = OxmlElement("w:updateFields")
    _settings.append(_uf)
_uf.set(qn("w:val"), "true")

if os.environ.get("DUMP_HEADINGS"):
    with open(os.environ["DUMP_HEADINGS"], "w") as fh:
        json.dump([{"level": l, "text": t} for l, t in HEADINGS], fh, indent=1)

doc.save(OUT)
print("wrote", OUT, os.path.getsize(OUT), "bytes")