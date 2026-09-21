"""
analysis/llm_discovery.py — Phase 2: repo-level LLM pattern discovery driver.

Drives the single LLM (default qwen3:14b, per the pre-registered design) over
the 327-repo stratified sample to (a) confirm the deterministic C1-C4 / zero-DI
baseline and (b) flag rep-level DI patterns that LOOK novel / non-standard, with
concrete evidence lines. Output is the candidate list that the human peer-review
phase (Phase 3) inspects one by one.

Resumable: per-repo checkpoints appended to out/llm_discovery.jsonl; re-running
skips repos already annotated. Seeded, temperature=0, executor profile recorded
per the novelty protocol (reverify gate before a changed executor).

Usage (against an Ollama host, e.g. the collaborator PC):
    OLLAMA_HOST=http://<friend-ip>:11434 uv run python analysis/llm_discovery.py \
        --model qwen3:14b --out analysis/out/llm_discovery.jsonl
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "novelty"))
from client import OllamaClient  # noqa: E402
from executor import ExecutorProfile  # noqa: E402

ROOT = Path(__file__).resolve().parent
SAMPLE = ROOT / "out" / "sample.json"
INPUT_DIR = ROOT / "out" / "llm_input"
DEFAULT_OUT = ROOT / "out" / "llm_discovery.jsonl"
PROMPT_VERSION = "0.2"

SYSTEM_BLOCK = (
    "You are a precise annotator for a peer-reviewed empirical study of how "
    "FastAPI dependency injection (DI) is used in the wild. You inspect a "
    "summary of a SINGLE real FastAPI repository and you judge its DI usage.\n\n"
    "Rules:\n"
    "- The 'known' baseline (C1-C4 constructs and zero-DI) was already computed "
    "deterministically from a static extractor. Your job is NOT to re-derive it. "
    "Declare whether the repo shows any DI pattern that is NOT that baseline, "
    "especially anything new, unusual, or non-idiomatic.\n"
    "- Only flag something 'potentially_novel' if you see REAL structural "
    "evidence in the provided excerpt (an argument, a yield generator, a "
    "Security scope, a dependency-argument name, or a non-FastAPI source like "
    "dependency-injector). Name the exact identifier.\n"
    "- 'zero_di' means the repo genuinely does no framework DI.\n"
    "- Never invent identifiers that are not in the evidence. If evidence is "
    "insufficient, say so explicitly.\n"
    "- Be concise."
)

USER_TEMPLATE = (
    "REPO: {full_name}\n"
    "STRATUM: {stratum}\n"
    "KNOWN BASELINE: {baseline}\n"
    "DEPENDS: {depends_total} total, argument shapes {arg_shapes}\n"
    "SECURITY: {security_total} calls, scopes present: {scopes}\n"
    "ANNOTATED DEPS: {annotated_dep_total}\n"
    "YIELD/GENERATOR DEPS: {yield_dep_total} ({n_yield} distinct functions)\n"
    "NON-FASTAPI DEPENDS SOURCES (EX2): {ex2_sources}\n"
    "DEPENDENCY GRAPH: {nodes} nodes, {edges} edges, max_depth={max_depth}, "
    "unresolved={unresolved}\n"
    "\n"
    "Answer EXACTLY this JSON:\n"
    "{{\n"
    "  \"baseline_confirmed\": <true|false>,\n"
    "  \"candidate_patterns\": [{{\"pattern\": \"<short name>\", "
    "\"evidence\": \"<exact identifier or construct from the evidence>\", "
    "\"reason\": \"<why this looks like a real DI pattern, 1-2 sentences>\", "
    "\"possibly_novel\": <true|false>}}],\n"
    "  \"notes\": \"<anything else, incl. obviously non-fastapi DI>\",\n"
    "  \"confident\": <true|false>\n"
    "}}\n"
    "Output ONLY the JSON object."
)


def render_user(evidence: dict) -> str:
    agg = evidence["aggregate"]
    return USER_TEMPLATE.format(
        full_name=evidence["full_name"],
        stratum=evidence["stratum"],
        baseline=evidence["catalog_baseline"],
        depends_total=agg.get("depends_total", 0),
        arg_shapes=json.dumps(evidence.get("arg_shapes", {})),
        security_total=agg.get("security_total", 0),
        scopes=json.dumps(evidence.get("security_scopes", [])),
        annotated_dep_total=agg.get("annotated_depends_total", 0),
        yield_dep_total=agg.get("yield_dep_total", 0),
        n_yield=evidence.get("n_yield_functions", 0),
        ex2_sources=json.dumps(evidence.get("ex2_sources", [])),
        nodes=evidence.get("dependency_graph", {}).get("nodes", 0),
        edges=evidence.get("dependency_graph", {}).get("edges", 0),
        max_depth=evidence.get("dependency_graph", {}).get("max_depth"),
        unresolved=evidence.get("dependency_graph", {}).get("unresolved_depends", 0),
    )


def parse_response(text: str) -> dict:
    import re
    m = re.search(r"\{[^{}]*\"candidate_patterns\"[^{}]*\}", text, re.DOTALL)
    chunk = m.group(0) if m else text
    try:
        data = json.loads(chunk)
    except json.JSONDecodeError:
        return {"parse_error": True, "raw": text[:500]}
    return data


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="qwen3:14b")
    ap.add_argument("--host", default="")
    ap.add_argument("--out", default=str(DEFAULT_OUT))
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--limit", type=int, default=0, help="0 = all")
    ap.add_argument("--num-ctx", type=int, default=8192)
    ap.add_argument("--reverify", default="",
                    help="path to a reverify gate json; refuse to run without it being OK")
    args = ap.parse_args()

    sample = json.loads(SAMPLE.read_text())
    entries = sample["sampled"]
    out = Path(args.out)

    if args.reverify:
        gate = json.loads(Path(args.reverify).read_text())
        ok = gate.get("ok") or gate.get("passed")
        if not ok:
            sys.exit(f"reverify gate not OK: {gate.get('summary', '<none>')}")
        print(f"[gate] reverify OK on {gate.get('executor', {}).get('machine')}")

    done = {json.loads(l)["full_name"] for l in out.read_text().splitlines()} if out.exists() else set()
    client = OllamaClient(model=args.model, host=args.host, num_ctx=args.num_ctx)
    profile = ExecutorProfile.capture(models=[args.model]).to_dict()
    run_id = datetime.now(timezone.utc).isoformat(timespec="seconds")

    def record(rec: dict) -> None:
        with out.open("a") as fh:
            fh.write(json.dumps(rec, ensure_ascii=False) + "\n")

    processed = 0
    for i, e in enumerate(entries):
        if i < args.start:
            continue
        if args.limit and processed >= args.limit:
            break
        if e["full_name"] in done:
            continue
        evidence = json.loads((INPUT_DIR / f"sample_{e['full_name'].replace('/', '__')}.json").read_text())
        system = SYSTEM_BLOCK
        user = render_user(evidence)
        resp = client.generate(system, user)
        parsed = parse_response(resp["content"])
        rec = {
            "run_id": run_id,
            "prompt_version": PROMPT_VERSION,
            "model": args.model,
            "full_name": e["full_name"],
            "stratum": e["stratum"],
            "weight": e["weight"],
            "baseline": evidence["catalog_baseline"],
            "parsed": {k: parsed.get(k) for k in
                       ("baseline_confirmed", "candidate_patterns", "notes", "confident")},
            "parse_error": parsed.get("parse_error", False),
            "raw": resp["content"],
            "latency_s": resp["latency_s"],
            "executor": profile,
            "generated_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        }
        record(rec)
        processed += 1
        if processed % 10 == 0 or processed == 1:
            print(f"[llm] {processed}/{args.limit or 'all'} {e['full_name']} "
                  f"candidates={len(parsed.get('candidate_patterns', []))}")

    print(f"[llm] done. fresh records appended to {out}")


if __name__ == "__main__":
    main()