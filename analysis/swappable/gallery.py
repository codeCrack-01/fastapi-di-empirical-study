"""analysis/swappable/gallery.py — build pattern_gallery.md for peer reviewers.

Shows REAL DI-bearing source lines (from analysis/novelty/out/novelty_repo_context.json,
the 327 in-sample repos) so reviewers know exactly what each DI type and each catalog
type (swappable / context-bound / over-capture) looks like in code.
"""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
REPO_CTX = ROOT / "analysis" / "novelty" / "out" / "novelty_repo_context.json"
CATALOG = ROOT / "analysis" / "swappable" / "out" / "catalog.json"
OUT = ROOT / "analysis" / "swappable" / "out" / "pattern_gallery.md"

C_LABEL = {
    "C1": "**C1 — `Depends(...)`** classic positional dependency",
    "C2": "**C2 — `Security(...)`** scoped security dependency",
    "C3": "**C3 — `Annotated[T, Depends(...)]`** modern typed dependency",
    "C4": "**C4 — generator/yield dependency** (`def get_db(): ...; yield db`)",
}


def clean(text: str, cap: int = 420) -> str:
    t = (text or "").replace("\r", "")
    lines = [l.rstrip() for l in t.splitlines()]
    # window around the DI-bearing line when present
    di = [i for i, l in enumerate(lines) if "Depends(" in l or "Annotated["
          in l or "Security(" in l or "yield" in l.lower()]
    lo = max(0, (di[len(di) // 2] if di else 0) - 8)
    hi = min(len(lines), (di[len(di) // 2] if di else len(lines) - 1) + 4)
    body = "\n".join(l for l in lines[lo:hi] if l.strip())
    return body.strip()[:cap]


def find_excerpt(repo: dict, file: str, line: int) -> dict | None:
    best = None
    for s in repo.get("source_excerpts", []):
        if s.get("file") != file:
            continue
        sl = s.get("line")
        if sl is None:
            continue
        if abs(sl - line) <= 3:
            if best is None or abs(sl - line) < abs(best["line"] - line):
                best = s
    return best


def header_lines() -> list[str]:
    """Reference sections: what C1-C4 are, and what fingerprints are."""
    L = []
    L.append("# What FastAPI DI looks like — reviewer reference")
    L.append("")
    L.append("This gallery shows **real source code** from the 327 in-sample repos. "
             "It is the shared \"what am I confirming?\" reference for the peer review.")
    L.append("")
    L.append("## Part A — The four DI constructs (C1–C4)")
    L.append("")
    L.append("C1–C4 are the **four syntactic forms** FastAPI provides for declaring a "
             "dependency. They are one feature (FastAPI's dependency-injection "
             "mechanism) spelled four ways — **not** four frameworks, and not a Python "
             "standard-library feature.")
    L.append("")
    L.append("| ID | Name | Code form | FastAPI or Python? | Reference (online) |")
    L.append("|---|---|---|---|---|")
    L.append("| **C1** | `Depends` — parameter dependency | `def read_x(db: Session = Depends(get_db))` | **FastAPI** — `from fastapi import Depends`. Not in the Python stdlib. | https://fastapi.tiangolo.com/tutorial/dependencies/ |")
    L.append("| **C2** | `Security` — scoped security dependency | `def read_x(token: str = Security(oauth2_scheme, scopes=[\"me\"]))` | **FastAPI** — `from fastapi import Security`. A `Depends` that additionally extracts OAuth2 security scopes. | https://fastapi.tiangolo.com/tutorial/security/ |")
    L.append("| **C3** | `Annotated` dependency (modern typed form) | `DbDep = Annotated[AsyncSession, Depends(get_db)]` | **Both.** `Annotated` is Python stdlib (`typing.Annotated`); the DI resolution is FastAPI's `Depends`. | https://docs.python.org/3/library/typing.html#typing.Annotated · https://fastapi.tiangolo.com/tutorial/dependencies/ |")
    L.append("| **C4** | Dependency with `yield` (generator dependency) | `def get_db() -> Iterator[Session]: try: yield session finally: close()` | **Both.** The `yield` mechanics are Python generators; treating the generator as a set-up/tear-down dependency is FastAPI. | https://fastapi.tiangolo.com/tutorial/dependencies/dependencies-with-yield/ |")
    L.append("")
    L.append("These four are read from the **call site** (and, for C4, from the "
             "**definition**): the extractor counts `depends_calls`, `security_calls`, "
             "`annotated_depends`, and `yield_functions` in `corpus/reports/*.json`. "
             "`EX2` = `Depends`/`Security` imported from a non-FastAPI module; `Z` = repo "
             "with no C1–C4 at all.")
    L.append("")
    L.append("### Are C1–C4 themselves \"swappable\"?")
    L.append("")
    L.append("**Yes — as a set.** C1–C4 are four mutually swappable spellings of a single "
             "FastAPI injection mechanism. Re-expressing a dependency in another "
             "construct does not change its behavior, so the constructs form an "
             "interchangeable set:")
    L.append("")
    L.append("| Pair | Swap type | Why |")
    L.append("|---|---|---|")
    L.append("| **C1 ⇄ C3** | full swap | same resolution; only annotation-vs-default-value spelling differs — the 933 pure `C1|C3` pairs observed |")
    L.append("| **C1 ⇄ C2** | full swap in practice | `Security()` without scopes resolves identically to `Depends()`; the census shows **0/163** calls pass `scopes`, so in the wild C2 is a labeled C1 |")
    L.append("| **C1/C3 ⇄ C4** | call-site swap | a yield-dependency is still consumed via `Depends(...)` / `Annotated[...]`; only the provider's definition form differs (adds setup/teardown) |")
    L.append("")
    L.append("\"Swappable\" in the catalog is the **measured** side of this: a provider "
             "(e.g. `get_db`) written in two or more constructs within one repo is an "
             "*observed swap instance* (1,142 across the corpus; 933 of them pure "
             "`C1|C3`). That interference-free re-writing across constructs is exactly "
             "what lets the S2 benchmark renders in `experiment_proposal.md` §3.1 stay "
             "behavior-preserving.")
    L.append("")
    L.append("## Part B — Fingerprints: every spelling of C1–C4, nothing more")
    L.append("")
    L.append("A **fingerprint** (the `C1|BARE|SIG` strings in this gallery) is one exact "
             "spelling of one of the four constructs. It answers \"*precisely how is this "
             "occurrence written?*\" and is the enumerator that makes **all the variants** "
             "of the original C1–C4 patterns visible.")
    L.append("")
    L.append("- **Every fingerprint starts with C1/C2/C3/C4.** Fingerprints are a finer "
             "partition *of* the four constructs, not extra categories: `C3|CLASS|BARE` "
             "is still a C3, `C1|EMPTY|PARAM` is still a C1. They never add a fifth "
             "construct.")
    L.append("- **Names are replaced by SHAPE classes**, so a fingerprint is "
             "repo-independent: identical patterns collapse and distinct spellings stay "
             "separate (per `analysis/novelty/fingerprints.py`).")
    L.append("")
    L.append("Shape classes (used in the argument / type / annotated slots):")
    L.append("")
    L.append("| Class | Meaning | Example |")
    L.append("|---|---|---|")
    L.append("| `BARE` | plain identifier | `Depends(get_db)` |")
    L.append("| `DOTTED` | dotted path | `Depends(core.current_principal)` |")
    L.append("| `CLASS` | Capitalized identifier (a type/class) | `Depends(AsyncSession)` · `Annotated[Session, …]` → `C3|CLASS|BARE` |")
    L.append("| `CALL` | call expression | `Depends(make_db())` |")
    L.append("| `EMPTY` | no argument | `Depends()` |")
    L.append("| `ELLIPSIS` | `...` | `Depends(...)` |")
    L.append("| `OTHER` | anything else | `Depends(<empty>)` forms |")
    L.append("| `SIG` / `PARAM` | C1 slot: in-function-signature vs plain default parameter | `C1|BARE|SIG` vs `C1|BARE|PARAM` |")
    L.append("| `USED` / `DEF` | C4 slot: used as a dependency vs defined but unwired | `C4|USED` vs `C4|DEF` |")
    L.append("")
    L.append("Fingerprint grammar (per construct):")
    L.append("")
    L.append("| Construct | Fingerprint | Slots |")
    L.append("|---|---|---|")
    L.append("| C1 | `C1|{shape}|{SIG,PARAM}` | shape of the `Depends(...)` argument; in-signature or not |")
    L.append("| C2 | `C2|{shape}|{scopes}` | argument shape; comma-joined OAuth2 scopes, or `ascopes` when none |")
    L.append("| C3 | `C3|{ann}|{dep}` | shape of the annotated type; shape of the inner `Depends(...)` argument |")
    L.append("| C4 | `C4|USED` / `C4|DEF` | whether the generator is wired as a dependency |")
    L.append("")
    L.append("The LLM panel then labels each *distinct spelling* (never per repo):")
    L.append("")
    L.append("| Label | Meaning (per `analysis/novelty/labels.py`) |")
    L.append("|---|---|")
    L.append("| `known` | expressible by exactly one catalog rule (C1–C4) |")
    L.append("| `variant` | semantically one of C1–C4, but a structurally different spelling |")
    L.append("| `novel` | genuinely new DI pattern outside C1–C4/EX2/Z |")
    L.append("| `false_pos` | not DI — the static extractor over-captured (e.g. non-FastAPI `Depends`) |")
    L.append("| `external_di` | DI from a non-FastAPI framework (flask, celery, dependency-injector, …) |")
    L.append("")
    L.append("So when the gallery says *Over-capture (e.g. `C3|CLASS|BARE`)* it means: the "
             "panel labelled that *spelling* `false_pos`, but the spelling is often real "
             "DI — adjudicate the code, don't auto-dismiss.")
    L.append("")
    L.append("A **swappable pattern** = the recurrence of this interchangeability in "
             "the wild: the same provider written in more than one of these ways (across "
             "constructs) within one repo.")
    L.append("")
    return L


def main() -> None:
    ctx = json.loads(REPO_CTX.read_text())
    cat = json.loads(CATALOG.read_text())
    repos = {r["full_name"]: r for r in ctx["repos"]}
    by = {
        "swappable": defaultdict(list),
        "context_bound": defaultdict(list),
        "over_capture": defaultdict(list),
    }
    for kind in ("swappable", "context_bound", "over_capture"):
        for e in cat.get(kind, []):
            rr = repos.get(e["repo"])
            if not rr:
                continue
            ex = next((x for x in e.get("examples", []) if x.get("file")), None)
            if not ex:
                continue
            hit = find_excerpt(rr, ex["file"], ex["line"])
            if hit and ("Depends(" in (hit.get("excerpt") or "")):
                prov = e["provider"] or "[mechanism]"
                by[kind][prov].append((e, rr, hit, ex))

    L: list[str] = header_lines()

    for kind, title, head in (
        ("swappable", "Swappable patterns (interchangeable DI — the benchmark arm set)",
         "Same provider expressed through two-or-more constructs. Confirm these are "
         "genuinely interchangeable DI."),
        ("context_bound", "Context-bound patterns (reported, not generic)",
         "Single-repo providers, non-plain argument shapes, closures/parameterized "
         "dependencies, or pass-2 non-native mechanisms."),
        ("over_capture", "Over-capture (flagged for adjudication, not auto-dismissed)",
         "Fingerprints the single-rater panel labelled false_pos but which often ARE "
         "real DI (e.g. `C3|CLASS|BARE`, `C4|USED`). Reviewers should adjudicate, "
         "not blanket-accept the label."),
    ):
        L.append(f"## {title}")
        L.append("")
        L.append(head)
        L.append("")
        providers = sorted(by[kind], key=lambda p: -len(by[kind][p]))[:14]
        for prov in providers:
            rows = by[kind][prov]
            L.append(f"### `{prov}` — {len(rows)} in-sample repo(s)")
            L.append("")
            for e, rr, hit, ex in rows[:2]:
                loc = f"{hit['file']}:{hit['line']}"
                url = hit.get("github_url") or ex.get("github_url") or f"https://github.com/{e['repo']}"
                L.append(f"**{e['repo']}** · `{loc}` · construct {hit.get('construct')} ...")
                L.append("")
                L.append("```python")
                L.append(clean(hit.get("excerpt", ""), 420))
                L.append("```")
                L.append(f"- fingerprint: `{hit.get('fingerprint')}` — [open on GitHub]({url})")
                L.append("")
            if len(rows) > 2:
                more = rows[2:]
                L.append(f"- +{len(more)} more in-sample repo(s): "
                         + "; ".join(f"`{a[1]['full_name']}`" for a in more[:6]) + ("..." if len(more) > 6 else ""))
                L.append("")
        if not providers:
            L.append("_No in-sample example with DI-bearing excerpt._")
            L.append("")

    L.append("## Notes")
    L.append("")
    L.append("- Excerpts are pinned to study commits; `[open on GitHub]` links jump to "
             "the exact line.")
    L.append("- Snippets are truncated for the digestible view; full code is on GitHub "
             "and in the per-repo evidence pages.")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n")
    print(f"[gallery] wrote {OUT} ({len(L)} lines)")


if __name__ == "__main__":
    main()