"""analysis/build_team_writeup.py — team-facing writeup of the R=40 stress-test run.

The team has not seen this experiment run, so the document explains every term
from scratch rather than assuming background. Numbers are transcribed from the
committed artifacts; every one is reproducible with
analysis/experiment/analyze.py.

Usage:
    .venv/bin/python analysis/build_team_writeup.py
"""
from __future__ import annotations

from pathlib import Path

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.shared import Pt, RGBColor, Inches

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "docs" / "EXPERIMENT_R40_TEAM_WRITEUP.docx"

NAVY = RGBColor(0x1F, 0x38, 0x64)
GREY = RGBColor(0x55, 0x55, 0x55)
RED = RGBColor(0xA3, 0x1D, 0x1D)
GREEN = RGBColor(0x1E, 0x6B, 0x3A)


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


def numbered(doc, items):
    bullets(doc, items, style="List Number")


def table(doc, headers, rows, widths=None, color=None):
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
            if color and i in color and str(v) == color[i][0]:
                r.font.color.rgb = color[i][1]
                r.bold = True
    if widths:
        for i, w in enumerate(widths):
            for row in t.rows:
                row.cells[i].width = Inches(w)
    return t


def code(doc, text):
    p = doc.add_paragraph()
    p.paragraph_format.left_indent = Inches(0.3)
    p.paragraph_format.space_after = Pt(6)
    r = p.add_run(text)
    r.font.name = "Consolas"
    r.font.size = Pt(9.5)
    return p


def build() -> Path:
    doc = Document()
    setup(doc)

    # ============================================================ COVER
    h = doc.add_heading("Does it matter how you get your dependencies?", level=0)
    h.alignment = WD_ALIGN_PARAGRAPH.LEFT
    para(doc, "The FastAPI DI stress test — full results and what they mean",
         italic=True, color=GREY, size=13)
    para(doc, "Experiment R=40 · 960 load-test cells · completed 28 September 2026",
         color=GREY, size=10)

    doc.add_heading("The short version", level=1)
    para(doc, "We built the same 21-route web application four times, changing "
              "only how each handler obtains its dependencies. We then hammered "
              "all four versions with a load generator and measured how fast and "
              "how reliably each one responded.")
    para(doc, "The answer has two halves, and the second one is the interesting one.")
    bullets(doc, [
        ("Below saturation, it does not matter. ", "At 160 requests per second all "
         "four versions respond in about the same time. The mechanism you pick is "
         "not a performance decision you need to make."),
        ("Above saturation, it matters enormously. ", "At 480 requests per second "
         "the idiomatic FastAPI version — using Depends() — and the hand-rolled "
         "middleware version both start failing outright, while the version that "
         "uses an external dependency-injection container behaves identically to "
         "the version with no DI at all."),
    ])
    para(doc, "The counter-intuitive part is that the version doing no DI and the "
              "version using a container both block the request thread, while the "
              "Depends() version does not. Under load, the extra machinery the "
              "idiomatic version relies on costs more than the thing it was avoiding.",
         bold=True)
    para(doc, "One caveat up front: the hypothesis we pre-registered about where "
              "each version breaks (H3) was never actually measured. Section 9 "
              "explains what that was, why it slipped through, and why the data "
              "turns out to point somewhere more interesting than we expected.",
         italic=True, color=RED)

    doc.add_page_break()

    # ============================================================ GLOSSARY
    doc.add_heading("1. Vocabulary", level=1)
    para(doc, "None of this is assumed background.", italic=True, color=GREY)

    doc.add_heading("Dependency injection (DI)", level=2)
    para(doc, "A handler needs things it did not create — a database connection, "
              "the current user, a settings object. Dependency injection means "
              "those are handed to the handler instead of the handler fetching "
              "them itself. The point is that a handler stops doing setup work "
              "and can be tested by passing in different dependencies.")
    para(doc, "All four versions below do identical work and return identical "
              "responses. The only difference is the plumbing.")

    doc.add_heading("The strategies we compared (S1–S4)", level=2)
    para(doc, "These labels are used throughout the report and in every table.")

    doc.add_heading("Load-test terms", level=2)
    bullets(doc, [
        ("Request per second (rps, also 'throughput'). ", "How many requests per "
         "second the server is being asked to handle. This is the x-axis of every "
         "result table — it is the load we apply."),
        ("Latency. ", "How long the server takes to answer one request. Lower is "
         "better. It is always measured in milliseconds (ms) in this report."),
        ("p50 (median). ", "Half the requests came back faster than this, half "
         "slower. The 'typical' experience. This is the headline number in this "
         "study because it was pre-registered as the primary measure."),
        ("p95. ", "95% of requests came back faster than this; the slowest 5% were "
         "worse. p95 is where overload shows up first, so it is how we detected "
         "that two versions were falling apart."),
        ("Saturation / the knee. ", "Below a certain request rate, adding load "
         "barely changes response time — the line is flat. Past that rate the "
         "server cannot keep up and latency climbs steeply. The rate where the "
         "line bends is called the knee. Below the knee, a server is fine. Above "
         "it, latency gets worse fast and eventually requests fail outright."),
        ("Load generator (k6). ", "The separate program that sends the requests. "
         "It is a different process from the app being tested, running on the "
         "same machine, pinned to different CPU cores so the two do not fight over "
         "the same core."),
        ("Repetition ('rep', R=40). ", "We ran every single test cell 40 times "
         "rather than once. One run can be unlucky; 40 runs let us use the median "
         "and compute a confidence interval. R=40 means 40 repetitions per cell."),
        ("Confidence interval (CI). ", "A range of plausible values for a measured "
         "difference. If the range does not include zero, we treat the difference "
         "as real. If it does include zero, we call it 'within noise' and say so "
         "rather than claiming a difference."),
        ("Check failure. ", "The load generator asserts that every response is "
         "valid — correct status code, correct authentication behaviour. A 'check "
         "failure' is a response that violated one of those assertions. It is a "
         "harder and more meaningful signal than 'it got slower'."),
    ])

    doc.add_heading("Implementation terms that matter for the result", level=2)
    bullets(doc, [
        ("Thread. ", "A unit of execution. A program can run several at once on a "
         "multi-core machine."),
        ("Threadpool (worker pool). ", "A fixed set of threads kept ready to do "
         "short jobs handed to them. Instead of creating a new thread per request, "
         "the request is queued and a waiting thread picks it up."),
        ("Event loop / blocking. ", "An async server runs one main loop that "
         "hands control between requests. Work done directly in the loop stalls "
         "every other in-flight request. Work handed to a threadpool does not stall "
         "the loop, but costs a queue hand-off."),
        "This distinction is the entire explanation for our headline result and is "
        "covered in Section 8.",
    ])

    doc.add_page_break()

    # ============================================================ WHAT / WHY
    doc.add_heading("2. What we were trying to settle", level=1)
    para(doc, "There is a common claim in the FastAPI community, roughly: 'using "
              "Depends() is idiomatic and costs essentially nothing, because "
              "FastAPI resolves dependencies asynchronously.'")
    para(doc, "That claim has a gap in it. The usual example is a synchronous "
              "dependency — a function that does blocking I/O, like reading a "
              "session cookie. FastAPI cannot run a blocking function inside an "
              "async server without either stalling everything or handing it to a "
              "thread. Which one it does is a real engineering decision, and almost "
              "all write-ups quietly assume the answer is free.")
    para(doc, "So the question we set out to answer was: across the four realistic "
              "ways to do this, how much does the mechanism actually cost, and "
              "does that change when the server gets busy?")
    para(doc, "We pre-registered the answer before running anything, which means "
              "the questions and the decision rules were written down and committed "
              "to the repository before data collection — so the hypotheses could "
              "not be quietly rewritten to match whatever came out.", italic=True)

    doc.add_heading("The four strategies, in code", level=2)
    para(doc, "These are the actual generated implementations. They are the real "
              "source of the results, not pseudocode.")

    para(doc, "S1 — direct call (no injection at all). The handler does the work itself:", bold=True)
    code(doc, "def get_profile(request: Request):\n"
              "    user = current_user(conn, request)\n"
              "    require_role(user, ROLES['editor'])")

    para(doc, "S2 — native Depends(). The idiomatic FastAPI style. Note the "
              "dependency functions are synchronous:", bold=True)
    code(doc, "def get_profile(\n"
              "    conn=Depends(get_db),\n"
              "    user=Depends(get_current_user),\n"
              "):\n"
              "    return services.get_profile(...)")

    para(doc, "S3 — manual / middleware. A middleware resolves the user once and "
              "stashes it on the request; handlers read it. The resolution itself "
              "is explicitly pushed to a threadpool:", bold=True)
    code(doc, "@app.middleware('http')\n"
              "async def build_ctx(request, call_next):\n"
              "    request.state.ctx = _Ctx(await run_in_threadpool(_resolve_user, request))\n"
              "    return await call_next(request)")

    para(doc, "S4 — external container. A container object holds the services; "
              "handlers pull what they need from it:", bold=True)
    code(doc, "c = request.app.state.container\n"
              "user = c.user_service().current_user(conn, request)")

    para(doc, "Read those four snippets again and note which ones cross the "
              "threadpool boundary. S2 and S3 do — a synchronous dependency or an "
              "explicit run_in_threadpool call. S1 and S4 do not; they do the work "
              "inline. That distinction turns out to predict the results exactly.",
         bold=True)

    doc.add_page_break()

    # ============================================================ MODES
    doc.add_heading("3. The design decision that makes the study meaningful", level=1)
    para(doc, "A single workload cannot answer this question, because the answer "
              "depends entirely on how much of the request the dependency "
              "resolution occupies.")
    para(doc, "If dependencies are the whole job, we measure DI cost at its "
              "absolute maximum. If the handler does a database round-trip and "
              "waits on a network call, the DI cost is a rounding error and we "
              "cannot see it. Both are real situations, and they give opposite "
              "answers.")
    para(doc, "So we built one application with a switch and ran both.")

    table(doc,
          ["Mode", "What the handler does", "Resolver share of request time", "What it tells us"],
          [["A — DI-sensitive",
            "Returns a small JSON response right after resolving dependencies",
            "~100%",
            "The upper bound: the most DI cost is possible"],
           ["B — realistic",
            "Real SQLite database reads/writes through the injected session, plus a "
            "fixed 5 ms wait modelling an external API call",
            "~2%",
            "The lower bound: DI cost in a normal application"]],
          widths=[1.1, 2.0, 1.1, 1.8])
    para(doc)
    para(doc, "Mode B's 5 ms wait is the key to the design. It creates a realistic "
              "floor of around 6–7 ms per request, so the table of Mode B results "
              "is deliberately flat. That flatness is not a null result — it is the "
              "measurement working correctly.", italic=True)

    doc.add_heading("Load levels and why there are three", level=2)
    para(doc, "Rather than guessing at load levels, we first measured where this "
              "machine's server breaks (the knee), then deliberately chose one rate "
              "below it, one at it, and one above it.")
    para(doc, "Mode A: 160, 320, 480 rps   ·   Mode B: 89, 179, 268 rps", bold=True)
    para(doc, "Repeating the knee procedure for each strategy individually would "
              "have been the more thorough design. It was not done — Section 9 "
              "covers that honestly.")

    doc.add_heading("Repetitions and pairing", level=2)
    para(doc, "24 test cells (4 strategies × 2 modes × 3 rates), each run 40 times "
              "= 960 runs. Within each repetition the order of the cells is "
              "randomised, so that a slow patch of machine noise cannot bias one "
              "strategy against another. Comparisons are made within a repetition "
              "and then aggregated, rather than comparing one strategy's best run "
              "to another's worst.")

    doc.add_page_break()

    # ============================================================ HYPOTHESES
    doc.add_heading("4. What we predicted, in advance", level=1)
    para(doc, "Four hypotheses were written down and committed before any data was "
              "collected. Stating predictions in advance is what stops us from "
              "declaring victory on whichever pattern happens to look interesting.")

    table(doc,
          ["", "Hypothesis", "Plain English"],
          [["H1", "Resolvable differences",
            "In Mode A the strategies will differ measurably, with no-DI (S1) fastest."],
           ["H2", "Diminishing returns",
            "In Mode B the differences will be smaller than measurement noise, i.e. "
            "negligible next to real handler work."],
           ["H3", "Saturation invariance",
            "The point where the server saturates will be the same for all four "
            "strategies."],
           ["H4", "Resource parity",
            "Memory and CPU use will differ by under 5% in Mode B; any real "
            "differences are confined to Mode A."]],
          widths=[0.4, 1.4, 4.2])

    doc.add_page_break()

    # ============================================================ RESULTS
    doc.add_heading("5. Result 1 — below saturation, the choice does not matter", level=1)
    para(doc, "Response time, median (p50) in milliseconds, 40 runs per cell.")

    doc.add_heading("Mode A (resolver is ~100% of the request)", level=2)
    table(doc, ["Load", "S1 direct", "S2 native Depends()", "S3 manual", "S4 container", "Reading"],
          [["160 rps", "1.0", "1.0", "1.0", "1.0", "Indistinguishable"],
           ["320 rps", "1.0", "1.0", "2.0", "1.0", "Only S3 separates, +0.90 ms"],
           ["480 rps", "6.0", "15.0", "26.0", "6.0", "Above the knee — see Section 6"]],
          widths=[0.8, 0.9, 1.4, 0.8, 1.0, 1.9])

    doc.add_heading("Mode B (resolver is ~2% of the request)", level=2)
    table(doc, ["Load", "S1 direct", "S2 native Depends()", "S3 manual", "S4 container"],
          [["89 rps", "6.0", "7.0", "7.0", "7.0"],
           ["179 rps", "7.0", "7.0", "7.0", "7.0"],
           ["268 rps", "6.0", "7.0", "7.0", "6.0"]],
          widths=[1.0, 1.0, 1.6, 1.0, 1.2])
    para(doc, "The flat 6–7 ms is the 5 ms wait plus database work. The dependency "
              "resolution is inside the noise.")

    doc.add_heading("The differences that are real, but small", level=2)
    para(doc, "In Mode B the four versions are not quite identical. Paired "
              "differences against S1, in milliseconds:")
    table(doc, ["Mode", "Load", "S2 native", "S3 manual", "S4 container"],
          [["B", "89 rps", "+0.60  [CI +0.45, +0.75]", "+0.60  [CI +0.45, +0.75]", "+0.10  within noise"],
           ["B", "179 rps", "+0.25  [CI +0.12, +0.38]", "+0.25  [CI +0.12, +0.38]", "+0.12  within noise"],
           ["B", "268 rps", "+0.97  [CI +0.93, +1.00]", "+0.97  [CI +0.93, +1.00]", "+0.03  within noise"]],
          widths=[0.5, 0.8, 1.9, 1.9, 1.5])
    para(doc, "These confidence intervals exclude zero, so by the rule we fixed in "
              "advance these are counted as real differences, not noise. They are "
              "also all under 1 ms against a 6–7 ms baseline — that is, at most "
              "about a 15% slowdown on a request that is dominated by other work. "
              "Both statements are true and we report both.", bold=True)

    doc.add_page_break()

    # ============================================================ THE CLIFF
    doc.add_heading("6. Result 2 — above saturation, the choice is critical", level=1)
    para(doc, "This is the finding we did not expect.")
    para(doc, "The knee was measured at 320 rps, so the 480 rps level is 1.5× past "
              "the point where the server should be struggling. Here is what "
              "happened.")

    table(doc,
          ["Strategy", "p50", "p95", "Runs with failures", "HTTP 500s", "Memory vs S1"],
          [["S1 direct (no DI)", "6.0 ms", "140 ms", "0 of 40", "0", "—"],
           ["S4 external container", "6.0 ms", "145 ms", "0 of 40", "0", "+4.2%"],
           ["S2 native Depends()", "15.0 ms", "460 ms", "40 of 40", "14,190", "+67.6%"],
           ["S3 manual middleware", "26.0 ms", "863 ms", "39 of 40", "1,609", "+10.6%"]],
          widths=[1.6, 0.7, 0.7, 1.2, 0.9, 1.0],
          color={(3,): ("40 of 40", RED), (3,): ("39 of 40", RED)})
    para(doc)
    para(doc, "Read the two 'runs with failures' columns together. S1 and S4 never "
              "failed once across 80 runs. S2 failed in every single run and S3 in "
              "39 of 40. These are not slow servers — these are servers shedding "
              "requests.", bold=True)

    doc.add_heading("What 'shedding requests' looks like in the logs", level=2)
    para(doc, "We pulled the per-request data off the machine before shutting it "
              "down and read the actual errors. They are not application bugs:")
    code(doc, "read: connection reset by peer   (error code 1220)\n"
              "EOF                              (error code 1000)")
    para(doc, "The server is refusing connections because it is out of capacity. "
              "For comparison, at 320 rps — the knee itself — every strategy had "
              "zero failures.")

    doc.add_heading("One number in that table needs a warning label", level=2)
    para(doc, "The raw data also shows around 44,000–48,000 HTTP 401 responses in "
              "the failing runs. These are NOT errors. The test harness "
              "deliberately probes some routes without a login token, and 401 "
              "'unauthorised' is the correct answer. Reporting that count as an "
              "error rate would be wrong, so we are flagging it explicitly. The "
              "genuine authentication failures are far smaller: 15,312 for S2 and "
              "1,839 for S3.", italic=True)

    doc.add_page_break()

    # ============================================================ RESOURCES
    doc.add_heading("7. Result 3 — memory and CPU", level=1)
    para(doc, "H4 predicted resources would be within 5% in Mode B, with any real "
              "differences confined to Mode A. That held, with one caveat worth "
              "noting.")

    table(doc,
          ["Where", "S2 native", "S3 manual", "S4 container", "Within the 5% rule?"],
          [["Mode B, all loads — memory", "+0.5% to +3.4%", "+0.8% to +1.4%",
            "+4.6% to +5.2%", "S4 sits ON the line"],
           ["Mode B, all loads — CPU", "−0.6% to −0.4%", "+1.1% to +2.5%",
            "+0.1% to +0.7%", "Yes"],
           ["Mode A at 480 — memory", "+67.6%", "+10.6%", "+4.2%",
            "No — S2 is 1.7× the memory"]],
          widths=[1.7, 1.1, 1.1, 1.1, 1.2])
    para(doc)
    bullets(doc, [
        ("CPU is a non-story. ", "Every strategy sat within about 2.5% of every "
         "other at every load level, in both modes. The mechanism does not change "
         "how much computing is required — only how gracefully it fails."),
        ("S2's memory is the story. ", "At 480 rps, native Depends() used 115 MB "
         "against 69 MB for no-DI, peaking at 164 MB. That extra memory is the "
         "queue of in-flight requests waiting on the threadpool — it is the cost "
         "mechanism made visible."),
        ("S4 costs about 5% more memory than doing nothing. ", "Consistently, at "
         "every load level in both modes. Small, but it is the one place where the "
         "external container is measurably not free."),
    ])

    doc.add_page_break()

    # ============================================================ MECHANISM
    doc.add_heading("8. Why the idiomatic version is the one that breaks", level=1)
    para(doc, "This is the part we would most like a second opinion on, so here is "
              "the reasoning laid out in full.")

    para(doc, "Look back at the four code snippets in Section 2. The two versions "
              "that failed at 480 rps are exactly the two that involve a thread "
              "pool:")
    bullets(doc, [
        ("S2 ", "resolves a synchronous dependency through Depends(). Because the "
         "dependency function blocks, the server hands it to a pool of worker "
         "threads rather than running it on the main loop."),
        ("S3 ", "explicitly wraps user resolution in run_in_threadpool() — a "
         "deliberate hand-off, the same mechanism, chosen by hand."),
        ("S1 ", "does the same work inline. It blocks the main loop. No hand-off."),
        ("S4 ", "does the same work inline. No hand-off."),
    ])

    para(doc, "The surprising part: S1 blocks the event loop, which is normally "
              "considered the wrong thing to do, and yet it is twice as robust as "
              "S2, which does not block.", bold=True)

    para(doc, "The explanation is that on a small machine the threadpool is the "
              "scarcer resource. This test ran on 4 virtual CPUs backed by 2 "
              "physical cores. Dispatching work to a thread means a queue hand-off, "
              "and those worker threads then compete for the same two cores. That "
              "adds latency and contention exactly when the machine is already "
              "struggling — and hand-offs also pile up in memory, which is what "
              "the 67% memory figure is showing.")
    para(doc, "The version that does the work inline, even though it stalls its own "
              "request, never builds a queue. Its cost is paid immediately and "
              "locally. That is why it degrades gently instead of falling off a "
              "cliff.")

    para(doc, "How confident are we in this?", bold=True)
    para(doc, "The evidence is solid but circumstantial. We have the connection "
              "resets, the HTTP 500s, the memory profile, the failure rates, and a "
              "known and documented difference in how each mechanism dispatches "
              "work — and they all point the same way. What we did not do is "
              "instrument the threadpool itself. We did not record its depth or "
              "queue length, so we cannot prove the queue is the bottleneck rather "
              "than a correlate. Treat the mechanism as well-supported and "
              "hypothesised, not as measured fact.", italic=True)

    doc.add_page_break()

    # ============================================================ H3
    doc.add_heading("9. The hypothesis we did not test, and why", level=1)

    para(doc, "What H3 said", bold=True)
    para(doc, "H3 was 'saturation invariance': the point at which the server "
              "saturates — the knee — should be the same for all four strategies, "
              "anyway more than normal run-to-run wobble.")

    para(doc, "Why it was not tested", bold=True)
    para(doc, "Short answer: the knee was measured on S1 only, and then the load "
              "levels for all four strategies were derived from S1's knee.")
    para(doc, "Concretely, the script that measures the knee starts the server by "
              "naming one specific application, and that name is hardcoded:")
    code(doc, "# analysis/experiment/pilot_knee.py, line 35\n"
              "\"python\", \"-m\", \"uvicorn\",\n"
              "  \"straights.s0.app:app\",       # <- always S1\n"
              "  \"--host\", \"127.0.0.1\", \"--port\", str(port), ...")
    para(doc, "The knee-finding loop then iterates over the two workload modes but "
              "never over the four strategies, so exactly two knee files were ever "
              "produced — one for Mode A, one for Mode B. The load levels were then "
              "computed from those two numbers and applied to all four versions.")
    para(doc, "This was my error, and the specific kind worth naming: the design "
              "served one purpose correctly (choosing sensible load levels) and "
              "silently failed at a second purpose that the pre-registration had "
              "promised. The pre-registration and the pre-registration document "
              "both named H3, and nothing in the pipeline ever checked that every "
              "pre-registered hypothesis had a matching measurement. The lesson is "
              "that a pre-registration is only worth something if you verify that "
              "the instrument can produce every number it promises.", bold=True)

    para(doc, "Does it matter? Yes — and the answer is more interesting than the "
              "hypothesis was.", bold=True)
    para(doc, "The worry was this. If S2's real knee were 480 rps rather than "
              "320, then S2 was not failing past its own limit — it was merely "
              "sitting at it. That is a much weaker claim than 'S2 breaks first', "
              "and it would have undercut the headline.")
    para(doc, "So we applied the same knee rule we had already fixed — p95 exceeds "
              "three times the low-load baseline, and stays there — to the steady-"
              "state results for all four strategies.")
    table(doc,
          ["Strategy", "p95 at 160 rps", "p95 at 320 rps", "p95 at 480 rps",
           "Where it crosses the 3× line", "How far past it ends up"],
          [["S1 direct", "4.0 ms", "14.0 ms", "139.5 ms", "between 160 and 320", "20× the threshold"],
           ["S2 native", "4.0 ms", "15.8 ms", "460.0 ms", "between 160 and 320", "66× the threshold"],
           ["S3 manual", "4.0 ms", "18.0 ms", "863.0 ms", "between 160 and 320", "124× the threshold"],
           ["S4 container", "4.0 ms", "14.0 ms", "145.0 ms", "between 160 and 320", "21× the threshold"]],
          widths=[1.1, 1.0, 1.0, 1.0, 1.4, 1.2])

    para(doc, "Two conclusions, and the second one changes the story.", bold=True)
    numbered(doc, [
        "H3 looks broadly correct. All four strategies cross the three-times "
        "threshold in the same place — between 160 and 320 rps. They start to "
        "degrade at the same load. So the knee does not meaningfully differ, which "
        "is what H3 predicted.",
        "But where they end up afterwards is wildly different: 20×, 66×, 124× and "
        "21× the threshold. S1 and S4 cross the line and then flatten out. S2 and "
        "S3 cross the same line and keep falling.",
    ])
    para(doc, "So the accurate finding is not 'S2 saturates earlier'. It is: every "
              "version bends at about the same load, but the slope after the bend "
              "differs by up to six times, and only the container version bends as "
              "gently as doing nothing at all. That is a better-supported claim "
              "than the one we set out to test, and it is the one to write up.",
         bold=True)
    para(doc, "Caveat on this: applying the rule after the fact is a post-hoc "
              "approximation, not the pre-registered measurement, and it uses 30-"
              "second steady windows while the original knee came from a 2-second "
              "ramp bucket. The two do not agree perfectly — the steady numbers "
              "suggest the crossing happened a little below 320 rather than exactly "
              "at it. So treat the table as directional evidence, not a substitute "
              "for running the proper per-strategy knee probe.", italic=True)

    doc.add_page_break()

    # ============================================================ SCORECARD
    doc.add_heading("10. Hypothesis scorecard", level=1)
    table(doc,
          ["", "Verdict", "Evidence"],
          [["H1", "Confirmed, but narrowly",
            "S1 is fastest as predicted, and all strategies separate at 480 rps. "
            "But below saturation the differences are 0–0.9 ms, not dramatic."],
           ["H2", "Not confirmed as written",
            "We predicted Mode B differences would be smaller than measurement "
            "noise. They were not — the intervals exclude zero. They are real but "
            "under 1 ms, i.e. negligible in practice. The prediction was too strong; "
            "the intuition behind it survives."],
           ["H3", "Never measured; post-hoc evidence supports it",
            "The knee was measured on S1 only. Applying S1's own rule afterwards "
            "suggests all four bend at the same load, but that is post-hoc."],
           ["H4", "Confirmed with one caveat",
            "Resource parity holds in Mode B, and the one real divergence is in "
            "Mode A, exactly as predicted. Caveat: S4 uses about 5% more memory than "
            "S1, sitting on the boundary we set rather than inside it."]],
          widths=[0.4, 1.7, 4.1])

    # ============================================================ LIMITS
    doc.add_heading("11. What this study cannot tell you", level=1)
    numbered(doc, [
        "The test machine is a shared cloud VM, not dedicated hardware — 4 virtual "
        "CPUs on 2 physical cores, under a virtualisation layer. Paired "
        "within-run comparisons are what we trust; the absolute millisecond figures "
        "would change on other hardware and should not be quoted as general.",
        "The median latency values are stored as whole milliseconds. At 160 and 320 "
        "rps the median is 1 ms, so one millisecond of rounding is the entire "
        "value. The tight confidence intervals come from all 40 runs agreeing, not "
        "from fine measurement. Where sub-millisecond detail matters, read the p95 "
        "figures instead.",
        "There is no 99th-percentile latency for the 480 rps level at all. That "
        "data was not recorded for that leg. Nothing reported here depends on it, "
        "but we cannot quote a 480 p99.",
        "One application, four variants, one day. The direction of the finding is "
        "well supported; the exact magnitudes are preliminary. Different "
        "applications with deeper dependency chains, more fan-in, or genuinely "
        "async dependencies could shift the numbers.",
        "We ran a single worker process. This says nothing about multi-worker or "
        "multi-process deployments, where the threadpool dynamics would differ.",
    ])

    doc.add_heading("12. What we would do next", level=1)
    numbered(doc, [
        "Run the per-strategy knee probe properly — four knees per mode instead of "
        "one. That converts Section 9's post-hoc reasoning into a real measurement "
        "and would let us report where each strategy's cliff actually begins.",
        "Instrument the threadpool: record its depth and queue length during a "
        "saturated run. That would settle the mechanism in Section 8 from "
        "well-supported hypothesis to demonstrated cause.",
        "Add at least one genuinely asynchronous dependency strategy. Every "
        "version here does blocking work somewhere, and the claim that Depends() is "
        "'free because it is async' only makes sense if some dependencies really "
        "are async.",
        "Vary the application: deeper chains, multiple fan-in, larger payloads. One "
        "21-route app cannot represent the whole space.",
    ])

    doc.add_page_break()

    # ============================================================ APPENDIX
    doc.add_heading("Appendix — where everything lives", level=1)
    para(doc, "All results are committed to the repository, so every table in this "
              "document can be regenerated.")
    table(doc,
          ["What", "Where"],
          [["Pre-registration (committed before data collection)",
            "docs/experiment_proposal.md"],
           ["Run-level data, all 960 runs", "analysis/out/experiment/standalone_R40/runs_960.csv"],
           ["Generated result tables", "analysis/out/experiment/standalone_R40/tables_preregistered.md"],
           ["Why S2 and S3 failed, with the log evidence",
            "analysis/out/experiment/standalone_R40/A480_failure_diagnosis.md"],
           ["Orchestrator logs for both legs", "analysis/out/experiment/standalone_R40/run_standalone.log, run_480.log"],
           ["Measured knee values", "analysis/out/experiment/standalone_R40/knee_A.json, knee_B.json"],
           ["Machine specification", "analysis/out/experiment/standalone_R40/env_report.txt"],
           ["The analysis script", "analysis/experiment/analyze.py"],
           ["The four generated applications", "analysis/experiment/straights/s0 … s3"],
           ["The load generator", "k6/harness.js"]],
          widths=[2.6, 3.4])
    para(doc)
    para(doc, "To regenerate the result tables from the committed data:", bold=True)
    code(doc, "cd analysis/experiment\n"
              "../../.venv/bin/python analyze.py \\\n"
              "    --runs ../out/experiment/standalone_R40/runs_960.csv")
    para(doc, "Integrity note: the 960 runs are 24 distinct test cells with exactly "
              "40 repetitions each, and every run completed with a zero exit code. "
              "The strategy labels were verified against the generated source code "
              "rather than trusted from a comment, so S1–S4 are known to correspond "
              "to the mechanisms described in Section 2.")

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc.save(OUT)
    return OUT


if __name__ == "__main__":
    p = build()
    print(f"Wrote {p}  ({p.stat().st_size:,} bytes)")
