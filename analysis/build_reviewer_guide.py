"""analysis/build_reviewer_guide.py — build the Windows-friendly reviewer guide.

Emits peer_review_kit/REVIEWER_GUIDE.docx. The reviewer has no Markdown
viewer, so everything they need lives in this one file.

Usage:
    .venv/bin/python analysis/build_reviewer_guide.py
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Inches

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "peer_review_kit" / "REVIEWER_GUIDE.docx"

NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x55, 0x55, 0x55)


def setup(doc: Document) -> None:
    st = doc.styles["Normal"]
    st.font.name = "Calibri"
    st.font.size = Pt(11)
    st.paragraph_format.space_after = Pt(6)
    for name, size in (("Heading 1", 18), ("Heading 2", 14), ("Heading 3", 12)):
        h = doc.styles[name]
        h.font.name = "Calibri"
        h.font.size = Pt(size)
        h.font.color.rgb = NAVY
        h.font.bold = True


def para(doc, text="", *, italic=False, bold=False, size=None, color=None, space_after=None):
    p = doc.add_paragraph()
    r = p.add_run(text)
    r.italic, r.bold = italic, bold
    if size:
        r.font.size = Pt(size)
    if color:
        r.font.color.rgb = color
    if space_after is not None:
        p.paragraph_format.space_after = Pt(space_after)
    return p


def bullets(doc, items, style="List Bullet"):
    for it in items:
        p = doc.add_paragraph(style=style)
        p.paragraph_format.space_after = Pt(3)
        if isinstance(it, tuple):
            r = p.add_run(it[0])
            r.bold = True
            p.add_run(it[1])
        else:
            p.add_run(it)


def table(doc, headers, rows, widths=None):
    t = doc.add_table(rows=1, cols=len(headers))
    t.style = "Table Grid"
    t.alignment = WD_TABLE_ALIGNMENT.LEFT
    for i, h in enumerate(headers):
        c = t.rows[0].cells[i]
        c.text = ""
        r = c.paragraphs[0].add_run(h)
        r.bold = True
        r.font.size = Pt(10)
    for row in rows:
        cells = t.add_row().cells
        for i, v in enumerate(row):
            cells[i].text = ""
            r = cells[i].paragraphs[0].add_run(str(v))
            r.font.size = Pt(10)
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    return t


def build() -> Path:
    doc = Document()
    setup(doc)

    # ---------------------------------------------------------------- cover
    h = doc.add_heading("DI Review Guide", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    para(doc, "Reviewing a FastAPI dependency-injection corpus", italic=True, color=GREY, size=12)
    para(doc, "Three workbooks · 303 repositories · about 16 hours", color=GREY, size=10)

    doc.add_heading("What you are doing", level=1)
    para(
        doc,
        "A program analysed 2,179 FastAPI GitHub repositories with a static analyser "
        "and sorted each one into a category: does it use dependency injection (DI), "
        "and if so, what kind?",
    )
    para(
        doc,
        "That sorting decides what the research can claim. An earlier version of it was "
        "done by an AI model, and it turned out to be unreliable. We threw that out. The "
        "categories in your workbooks now come from the static analyser, and your job is "
        "to check it — by reading the actual code and deciding for yourself.",
    )
    para(
        doc,
        "You are not being asked to be fast, and you are not being asked to find DI. "
        "You are being asked to say what you see. An honest \"unclear\" is worth more "
        "than a confident guess, because a wrong answer here quietly corrupts a number "
        "in the final paper.",
    )

    doc.add_heading("Ground rules", level=2)
    bullets(doc, [
        ("Decide before you compare. ", "Read the repository and form your own answer "
         "before you look at what the analyser said. If you look first, you will tend to "
         "agree with it — and agreement we can already measure without you."),
        ("Fill in only your own column. ", "The workbooks have a column for you and a "
         "column for the other person. Fill yours. Do not look at theirs until both of "
         "you have finished every row."),
        ("\"unclear\" is a real answer. ", "Use it whenever you cannot tell. Do not guess "
         "to fill the cell, and do not default to \"no\" because you did not find anything."),
        ("Record the evidence. ", "If you mark a repository as having manual or external "
         "DI, write down the file and roughly where in it you saw the mechanism."),
        ("Do not edit the analyser column. ", "The columns marked S1, S2, and TRIAGE are "
         "the machine's output. They are locked on purpose — they are what we are testing."),
    ])

    doc.add_page_break()

    # ------------------------------------------------------------ categories
    doc.add_heading("The four categories", level=1)
    para(
        doc,
        "Every repository gets one label. These are the definitions the whole project "
        "uses — there are no others.",
    )
    table(
        doc,
        ["Label", "Name", "What it means"],
        [
            ["S1", "Direct construction",
             "The code does not use DI at all. The handler opens the database connection "
             "itself, calls get_current_user() itself, and so on. No framework, no container."],
            ["S2", "Framework-native DI",
             "Uses FastAPI's own resolver: Depends(...), Security(...), or "
             "Annotated[..., Depends(...)]. This is the common case."],
            ["S3", "Manual Python DI",
             "Somebody rolled their own. A hand-written Depends equivalent, a service "
             "locator, or a context object assembled in app.state / request.state and "
             "passed to the handler explicitly."],
            ["S4", "External container",
             "Imports a third-party DI container such as dependency_injector, injector, "
             "punq, or dishka. The import alone is enough to make it S4."],
        ],
        widths=[0.6, 1.7, 4.2],
    )
    para(doc, "")
    para(
        doc,
        "S1 and S2 are mutually exclusive. S3 and S4 are not: a repository can use "
        "FastAPI's Depends and a container at the same time. When that happens, label it "
        "S4 and mention the S3 mechanism in the NOTE column.",
        italic=True,
    )
    para(
        doc,
        "The analyser can detect S1, S2, and S4 (that last one only by import name). "
        "It cannot detect S3 at all — there is no field for it, because hand-rolled DI "
        "has no fixed shape. That gap is exactly what Parts 1 and 2 below exist to measure.",
        italic=True,
    )

    doc.add_page_break()

    # ---------------------------------------------------------------- arm 1
    doc.add_heading("Part 1 — AUDIT_80.xlsx (80 repositories)", level=1)
    para(doc, "Two people, both doing all 80 rows. This is the most important workbook.",
         bold=True)
    para(
        doc,
        "These 80 were drawn at random from the 804 repositories the analyser called S1 — "
        "the ones it found no DI constructs in. Your job is to find out whether that was right.",
    )
    doc.add_heading("The question", level=3)
    p = doc.add_paragraph()
    r = p.add_run("Does this repository contain any dependency-injection mechanism of any kind?")
    r.bold = True
    r.font.size = Pt(12)
    para(
        doc,
        "Notice how broad that is. It is not \"does it use FastAPI Depends\" — a "
        "repository can score zero on that and still contain a DI container, a "
        "hand-rolled resolver, or a service locator. Those are the cases we are hunting "
        "for. If you find a real DI mechanism the analyser missed, that is exactly the "
        "kind of row that matters most.",
    )
    doc.add_heading("How to fill it in", level=3)
    bullets(doc, [
        ("VERDICT_A ", "is yours if you are rater A. VERDICT_B if you are rater B."),
        ("yes ", "— some DI mechanism is present, even if the analyser found nothing."),
        ("no ", "— no DI mechanism is present."),
        ("unclear ", "— you cannot tell."),
        ("TRIAGE HINT ", "lists things the analyser already noticed (a non-FastAPI Depends, "
         "a callable class used as a dependency, an interesting import). It is a place to "
         "start looking, not an answer. Most repos have no signal and most are genuinely clean."),
        ("NOTE ", "— use it to record the file and line where you found a mechanism, or to "
         "explain an unclear."),
    ])
    doc.add_heading("The FINAL column fills itself in", level=3)
    para(
        doc,
        "Once both columns are filled, FINAL shows either the agreed answer or the word "
        "DISAGREE. You do not need to type in it, and you should not.",
    )
    doc.add_heading("Why this stops the project if it goes badly", level=3)
    para(
        doc,
        "Before any of this work began, we fixed in advance how many misses would force "
        "us to change course. The zero-DI group is the largest group in the corpus, so an "
        "error rate that looks small can move the headline number a long way.",
    )
    table(
        doc,
        ["Repositories with DI missed, out of 80", "Worst-case true rate", "What happens"],
        [
            ["0–1", "up to 6.7%", "Proceed. The bound is reportable as it stands."],
            ["2–3", "up to 10.5%", "Proceed, but the zero-DI share gets reported as a range."],
            ["4 or more", "12.2% or worse",
             "Stop. No headline number gets written until we extend the analyser."],
        ],
        widths=[2.2, 1.6, 2.8],
    )
    para(doc, "")
    para(
        doc,
        "These thresholds are printed in the workbook's own gate sheet and were committed "
        "to the repository before a single row was rated. They are not going to move once "
        "we see the answers.",
        italic=True,
    )

    doc.add_page_break()

    # --------------------------------------------------------------- arm 2b
    doc.add_heading("Part 2 — S3S4_200.xlsx (200 repositories)", level=1)
    para(doc, "Two people, both doing all 200 rows.", bold=True)
    para(
        doc,
        "These 200 were drawn at random from the 1,375 repositories the analyser found "
        "FastAPI DI in. All of them already use Depends. The question is whether any of "
        "them do something else as well — a container, or hand-rolled wiring.",
    )
    bullets(doc, [
        ("S2 ", "— FastAPI DI and nothing else. Expect this to be the large majority."),
        ("S3 ", "— also has manual DI: a hand-rolled Depends equivalent, a service "
         "locator, or a request-scoped context object passed to handlers explicitly."),
        ("S4 ", "— also imports an external container library. An import on its own is enough."),
        ("unclear ", "— you cannot tell from the code."),
    ])
    para(
        doc,
        "Same column rules as Part 1: fill only your own column, decide before comparing, "
        "and use the NOTE column to point at the code that settled it.",
    )
    para(
        doc,
        "Why 200 rows: this is the part that produces an actual percentage with a "
        "confidence range attached, rather than a bare list of examples. If manual DI is "
        "genuinely 5% of these repositories, 200 rows pins it down to somewhere between "
        "2.7% and 9.0%. That is the difference between a claim and a guess.",
        italic=True,
    )

    doc.add_page_break()

    # --------------------------------------------------------------- arm 2a
    doc.add_heading("Part 3 — S3S4_CANDIDATES.xlsx (23 repositories)", level=1)
    para(doc, "One person only. No second opinion needed here.", bold=True)
    para(
        doc,
        "These 23 repositories raised some signal — an unusual import, a non-FastAPI "
        "Depends, a class used as a dependency. Work through them and describe what you "
        "actually find.",
    )
    para(
        doc,
        "Expect most of them to turn out to be nothing. These signals are cheap to fire "
        "and easy to trigger by accident — a library called \"injector\" that has nothing "
        "to do with dependency injection, a settings module, a test helper. Marking those "
        "\"not DI\" is a useful result, not a wasted row. Please do not stretch to find "
        "DI that is not there.",
    )
    para(
        doc,
        "This part has no agreement check on purpose: its job is to build the vocabulary "
        "and the worked examples that Parts 1 and 2 then apply consistently. It cannot "
        "tell you how common anything is — it has no denominator, and it is not a random "
        "sample. Part 2 is what gives a number.",
        italic=True,
    )

    doc.add_page_break()

    # -------------------------------------------------------------- closing
    doc.add_heading("What happens after", level=1)
    bullets(doc, [
        "We compare the two columns in each workbook and report how often the raters "
        "agreed with each other.",
        "We count the Arm 1 misses and read the answer off the fixed gate table. Four or "
        "more means we stop and fix the analyser before writing anything.",
        "Part 2 gives the manual and external DI percentages with confidence intervals.",
        "Part 3 gives a worked definition of what manual DI actually looks like, plus a "
        "floor on how much of it exists.",
    ])
    para(
        doc,
        "The earlier AI-based analysis is not being used anywhere. Its numbers were "
        "withdrawn. This work replaces them.",
        italic=True,
    )

    doc.add_heading("One last thing", level=1)
    para(
        doc,
        "The analyser has a known blind spot, and it is a specific one: it only "
        "recognises DI that FastAPI itself provides. Manual DI has no fixed syntax, so "
        "the analyser cannot see it. That means the machine's answer is reliable about "
        "S1 and S2 and largely guessing about S3 and S4 — which is why Parts 2 and 3 "
        "exist, and why your judgement matters more here than a spot check would.",
    )
    para(
        doc,
        "If a row is ambiguous, or a repository has been deleted, or you cannot get the "
        "code to load — write that down and move on. A recorded \"unclear\" is a data "
        "point. A quiet blank is not.",
    )

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"Wrote {p.relative_to(ROOT)}  ({p.stat().st_size:,} bytes)")
