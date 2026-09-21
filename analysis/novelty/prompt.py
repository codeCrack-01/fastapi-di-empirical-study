"""analysis/novelty/prompt.py — pinned, byte-stable annotation prompt.

The prompt is a frozen artifact: any change to the rubric, the CoT block, or a
few-shot changes measured rater behavior, so the file content below is the ONE
canonical prompt. We render per-fingerprint with:

    {examples}  JSON list of representative occurrences (repo, line, argument/
                dependencies, annotated_type) — the "code evidence"
    {catalog}   the C1..C4/EX2/Z rubric text (labels.as_prompt_catalog)
    {fingerprint} the canonical signature being judged

Raters answer in EXACT JSON: {"label": <one of known|variant|novel|false_pos|external_di>}
or the catalog construct id. Any extra prose is ignored by the parser
(annotate.py extracts the first JSON object). The 10-way forced choice keeps
the rating task "fully specified" in the sense of the indeterminacy literature:
each option is enumerated, and there is a committed rubric for the boundary
cases.
"""
from __future__ import annotations

import json

from labels import as_prompt_catalog

RUBRIC = as_prompt_catalog()

SYSTEM_BLOCK = (
    "You are a precise annotator for a peer-reviewed empirical study of how "
    "FastAPI dependency injection (DI) is used in the wild. You classify DI "
    "construct fingerprints drawn from a ~4000-repo corpus by a static "
    "extractor. Your job is to judge, for a given canonical FINGERPRINT and its "
    "real code EXAMPLES, which catalog construct it belongs to OR whether it is "
    "a variant of a known pattern, a genuinely novel pattern, a false positive "
    "of the extractor, or an external DI framework.\n\n"
    "Never invent certainty: if the evidence is insufficient, return "
    '"known" with the closest catalog id and do NOT guess "novel". "novel" '
    "is reserved for a structural pattern that no catalog rule expresses and "
    "that recurs with evidence."
)

RUBRIC_BLOCK = (
    "## Catalog\n"
    "Each rule below describes exactly one construct. An occurrence that one "
    "rule describes is labeled by that rule's id (C1..C4, or EX2/Z).\n"
    f"{RUBRIC}\n"
    "\n"
    "## Output labels (choose exactly one)\n"
    "- known            -> one catalog rule fully explains the fingerprint\n"
    "- variant          -> semantically one of C1..C4 but spelled structurally "
    "different (e.g. dotted vs bare import, class passed where a function is "
    "expected, margin case)\n"
    "- novel            -> a structural DI pattern expressed nowhere in the "
    "catalog and not expressible by any single rule\n"
    "- false_pos        -> the extractor captured something that is not DI at "
    "all (e.g. an object named like a dependency, a non-DI call)\n"
    "- external_di      -> DI performed by a non-FastAPI framework "
    "(dependency-injector, fastapi-injector, celery, flask, etc.); the "
    "extractor should not have counted it as FastAPI DI\n"
    "\n"
    "## Chain-of-thought (do this before outputting JSON)\n"
    "1. Read each example carefully; identify the construct slot it landed in "
    "(Depends call, Security, Annotated metadata, yield generator).\n"
    "2. Ask: is there exactly ONE catalog rule describing it? If yes -> known.\n"
    "3. If the structure is close to a rule but spelled differently (alias "
    "import, dotted path, class-vs-function, empty Depends, inline call) -> "
    "say variant and name the base rule.\n"
    "4. If the DI wiring pattern has NO catalog rule -> novel (only if evidence "
    "appears across at least two distinct examples).\n"
    "5. If the code is not dependency injection -> false_pos. If it IS DI but "
    "from another framework -> external_di.\n"
    "6. Output JSON ONLY: {\"label\": \"<label>\", \"rule\": \"<optional "
    "catalog id>\", \"evidence\": \"<1 line why>\"}"
)

USER_TEMPLATE = (
    "FINGERPRINT:\n"
    "{fingerprint}\n\n"
    "EXAMPLES (real code evidence):\n"
    "{examples}\n\n"
    "Classify this fingerprint."
)


def render_system() -> str:
    return f"{SYSTEM_BLOCK}\n\n{RUBRIC_BLOCK}\n"


def render_user(fingerprint: str, examples: list[dict]) -> str:
    lines = []
    for ex in examples:
        item = {
            "repo": ex.get("repo"),
            "line": ex.get("line"),
            "context_function": ex.get("context_function"),
        }
        if ex.get("argument"):
            item["argument"] = ex["argument"]
        if ex.get("dependencies"):
            item["dependencies"] = ex["dependencies"]
        if ex.get("annotated_type"):
            item["annotated_type"] = ex["annotated_type"]
        if ex.get("scopes"):
            item["scopes"] = ex["scopes"]
        lines.append(json.dumps(item, ensure_ascii=False))
    return USER_TEMPLATE.format(
        fingerprint=fingerprint,
        examples="\n".join(lines) if lines else "(no examples)",
    ).strip()


def parse_response(text: str) -> dict:
    """Extract the final JSON object from a rater's (possibly chatty) reply.

    Returns normalized {label, rule, evidence} with label lowercased and
    validated against known labels.

    Hardened for thinking-mode models (qwen3): reasoning can contain draft
    ``{"label": ...}`` objects, so we collect ALL candidate JSON objects and
    take the LAST one (the final answer), never the first.
    """
    import re
    clean = text.strip()
    # strip markdown code fences if the model wrapped its answer in them
    clean = re.sub(r"```[a-zA-Z0-9]*\n?|\n?```", "", clean)

    blocks = list(re.finditer(r"\{[^{}]*?\"label\"[^{}]*\}", clean, re.DOTALL))
    if blocks:
        chunk = blocks[-1].group(0)
    else:
        chunk = None

    if chunk is None:
        m = re.search(r'\b(known|variant|novel|false_pos|external_di|C[1-8]|EX2|Z)\b', clean)
        if not m:
            return {"label": "unknown", "rule": None, "evidence": clean[:200]}
        data = {"label": m.group(1)}
    else:
        try:
            data = json.loads(chunk)
        except json.JSONDecodeError:
            return {"label": "unknown", "rule": None, "evidence": clean[:200]}

    label = str(data.get("label", "unknown")).strip().lower()
    label = label if re.fullmatch(r"known|variant|novel|false_pos|external_di|C[1-8]|ex2|z", label) else "unknown"
    return {
        "label": label,
        "rule": data.get("rule"),
        "evidence": str(data.get("evidence", ""))[:2000],
    }


def parse_repo_response(text: str) -> dict:
    """Extract the top-level JSON object from a repo-check reply.

    Handles nested ``{...}`` output (observations/reconciliations arrays with
    inner objects) by raw-decoding every object start and keeping the one that
    consumes the MOST text (the outermost object). Returns {} when the model
    produced no parseable object (caller stores it verbatim anyway).
    """
    import re
    clean = text.strip()
    clean = re.sub(r"```[a-zA-Z0-9]*\n?|\n?```", "", clean)
    decoder = json.JSONDecoder()
    best: dict | None = None
    best_end = -1
    i = 0
    while True:
        i = clean.find("{", i)
        if i == -1:
            break
        try:
            obj, n = decoder.raw_decode(clean[i:])
        except json.JSONDecodeError:
            i += 1
            continue
        if isinstance(obj, dict) and i + n > best_end:
            best = obj
            best_end = i + n
        i += 1
    return best or {}


REPO_PASS1_MARK = "__REPO_PASS1__"
REPO_PASS2_MARK = "__REPO_PASS2__"

REPO_PASS1_SYSTEM = (
    "You are an independent code reviewer for an empirical study of FastAPI "
    "dependency injection. You are looking at ONE repository from the study's "
    "stratified sample. You have NOT been told what patterns to expect — your "
    "job is to read the ACTUAL source code excerpts that follow and describe, "
    "on your own terms, how dependency injection is used here. Cite exact "
    "file:line for everything you claim. Do not invent certainty: if you see "
    "no DI, say so explicitly."
)

REPO_PASS1_TEMPLATE = (
    "REPOSITORY: {full_name} (stratum {stratum}, weight {weight})\n\n"
    "STATIC SUMMARY (from a deterministic AST extractor — counts only, no "
    "pattern labels):\n{summary}\n\n"
    "REAL SOURCE EXCERPTS (code around every DI-adjacent AST node in this repo, "
    "all pinned to commit {commit_sha}):\n{excerpts}\n\n"
    "{mark}\n"
    "Read the code. In JSON ONLY, answer:\n"
    '{{"observations": [{{"pattern": "<your name for the DI pattern>", '
    '"file": "<path>", "line": <int>, "why": "<reasoning with references>"}}], '
    '"comment": "<anything you want flag stage 2 to reconsider>"}}'
)

REPO_PASS2_SYSTEM = (
    "You are a second-pass DI reviewer. Another (static) instrument grouped "
    "this repository's DI occurrences into canonical structural fingerprints "
    "and a panel already labeled each fingerprint. You must now CONFRONT those "
    "labels with the REAL code in THIS repo: for each fingerprint say whether "
    "you AGREE. To OVERTURN a label you MUST cite the exact file:line in this "
    "repo that contradicts it. Also report anything you noticed in your first "
    "pass that the fingerprint inventory missed entirely."
)

REPO_PASS2_TEMPLATE = (
    "REPOSITORY: {full_name} (stratum {stratum}, weight {weight}), commit "
    "{commit_sha}.\n\n"
    "PANEL LABELS PER FINGERPRINT (from an independent annotator pass):\n"
    "{matches}\n\n"
    "REAL SOURCE EXCERPTS (as in pass 1):\n{excerpts}\n\n"
    "YOUR PASS-1 OBSERVATIONS (from reading the code fresh):\n{pass1}\n\n"
    "{mark}\n"
    "In JSON ONLY, answer:\n"
    '{{"reconciliations": [{{"fingerprint": "<id>", "agree": true|false, '
    '"label": "<your final label>", "reason": "<why>", '
    '"citation": {{"file": "<path>", "line": <int>}}}}], '
    '"missed_by_inventory": [{{"pattern": "...", "file": "...", "line": <int>, '
    '"why": "..."}}], '
    '"comment": "..."}}\n'
    "Rules: leave a fingerprint's label unchanged unless code in THIS repo "
    "contradicts it; every \"agree\": false must carry a citation."
)


def _format_summary(summary: dict) -> str:
    return ", ".join(f"{k}={v}" for k, v in (summary or {}).items()) or "(none)"


def _format_excerpts(excerpts: list[dict], cap: int = 60) -> str:
    lines = []
    for e in (excerpts or [])[:cap]:
        where = f"{e['file']}:{e['line']} ({e['context_function'] or 'toplevel'})"
        if e.get("github_url"):
            where += f"  {e['github_url']}"
        if not e.get("excerpt"):
            lines.append(f"--- {where}  [source unavailable on this box] ---")
            continue
        lines.append(f"--- {where} ---")
        lines.append(e["excerpt"].replace("\n", "\n        "))
    return "\n".join(lines) if lines else "(this repo has no DI-adjacent AST nodes)"


def _format_matches(repo: dict, labels: dict[str, str]) -> str:
    lines = []
    for m in (repo.get("matched_fingerprints") or []):
        fid = m["fingerprint"]
        label = labels.get(fid, "unlabeled")
        lines.append(f"- {fid}  -> {label}   (n={m['n']} in this repo, "
                     f"links: {', '.join(m.get('urls') or [])})")
    return "\n".join(lines) if lines else "(none — extractor found no fingerprints here)"


def render_repo_pass1(repo: dict) -> str:
    return REPO_PASS1_TEMPLATE.format(
        full_name=repo["full_name"],
        stratum=repo.get("stratum"),
        weight=repo.get("weight"),
        summary=_format_summary(repo.get("summary")),
        excerpts=_format_excerpts(repo.get("source_excerpts")),
        commit_sha=(repo.get("commit_sha") or "HEAD")[:12],
        mark=REPO_PASS1_MARK,
    ).strip()


def render_repo_pass2(repo: dict, labels: dict[str, str], pass1: dict) -> str:
    observations = pass1.get("observations") or []
    obs_lines = "\n".join(
        f"- {o.get('pattern')} @ {o.get('file')}:{o.get('line')} — {o.get('why')}"
        for o in observations
    ) or "(none recorded)"
    return REPO_PASS2_TEMPLATE.format(
        full_name=repo["full_name"],
        stratum=repo.get("stratum"),
        weight=repo.get("weight"),
        commit_sha=(repo.get("commit_sha") or "HEAD")[:12],
        matches=_format_matches(repo, labels),
        excerpts=_format_excerpts(repo.get("source_excerpts")),
        pass1=obs_lines,
        mark=REPO_PASS2_MARK,
    ).strip()


if __name__ == "__main__":
    demo = [
        {"repo": "a/b", "line": 12, "argument": "get_db", "context_function": "read_item"},
        {"repo": "c/d", "line": 41, "argument": "core.get_db", "context_function": "read_item"},
    ]
    print(render_system())
    print("----")
    print(render_user("C1|BARE|SIG", demo))