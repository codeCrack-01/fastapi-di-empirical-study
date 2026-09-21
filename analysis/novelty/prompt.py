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


if __name__ == "__main__":
    demo = [
        {"repo": "a/b", "line": 12, "argument": "get_db", "context_function": "read_item"},
        {"repo": "c/d", "line": 41, "argument": "core.get_db", "context_function": "read_item"},
    ]
    print(render_system())
    print("----")
    print(render_user("C1|BARE|SIG", demo))