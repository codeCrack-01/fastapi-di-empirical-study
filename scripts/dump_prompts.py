"""scripts/dump_prompts.py — render the ACTUAL prompts sent to qwen3:14b.

Reproduces the formatted system/user messages from the pinned templates
(analysis/novelty/prompt.py) exactly as the executor rendered them, using the
per-record data stored in the judge chunks. Writes:

    analysis/out/review/rendered_prompts.md

Fidelity notes
--------------
- Annotate stage: the system block, rubric, and USER_TEMPLATE are byte-stable in
  prompt.py; the per-fingerprint example payloads are stored verbatim in the
  annotate chunks, so render_user() reproduces the exact user message.
- repo_check stage: the pass-1/pass-2 user messages depend on the repo's live
  source excerpts (novelty_repo_context.json), its AST summary (corpus/reports),
  and the panel labels (annotate chunks). Two fully rendered examples are shown.
- Model reasoning traces (thinking) are NOT stored — the Ollama client never
  enabled `think`; structured evidence + file:line citations were required in
  the output schema instead.
"""
from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "pod_results" / "remote" / "results"
REPO_CTX = ROOT / "analysis" / "novelty" / "out" / "novelty_repo_context.json"
REPORTS_DIR = ROOT / "corpus" / "reports"
OUT = ROOT / "analysis" / "out" / "review" / "rendered_prompts.md"


def load_prompt_module() -> object:
    src = ROOT / "analysis" / "novelty" / "prompt.py"
    sys.path.insert(0, str(src.parent))
    spec = importlib.util.spec_from_file_location("prompt", src)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["prompt"] = mod
    spec.loader.exec_module(mod)
    return mod


def load_annotate() -> list[dict]:
    recs = []
    for f in sorted(RESULTS_DIR.glob("chunk_000*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            recs.append(json.loads(line))
    return recs


def load_label_map() -> dict[str, str]:
    return {d["fingerprint_id"]: d["consensus"]["label"] for d in load_annotate()}


def repo_excerpts(repo_full: str) -> list[dict]:
    ctx = json.loads(REPO_CTX.read_text())
    for r in ctx.get("repos", []):
        if r.get("full_name") == repo_full:
            return r.get("source_excerpts") or []
    return []


def repo_summary(repo_full: str) -> dict:
    rep = Path(f"{REPORTS_DIR}/{repo_full.replace('/', '__')}.json")
    if not rep.exists():
        return {}
    d = json.loads(rep.read_text())
    return d.get("aggregate") or {}


def main() -> int:
    prompt = load_prompt_module()
    ann = load_annotate()
    labels = load_label_map()
    L: list[str] = []
    L.append("# Rendered prompts — what was sent to qwen3:14b")
    L.append("")
    L.append("- model: `qwen3:14b`, temperature 0, fixed seed, JSON-output schema")
    L.append("- reasoning traces (`thinking`) are **not** stored (Ollama `think` "
             "never enabled); the model was required to cite file:line in its JSON.")
    L.append("")
    L.append("## 1. Annotate stage — system block")
    L.append("")
    L.append("```\n" + prompt.SYSTEM_BLOCK.strip() + "\n```")
    L.append("")
    L.append("## 2. Annotate stage — rubric block (label vocabulary + CoT instruction)")
    L.append("")
    L.append("```\n" + prompt.RUBRIC_BLOCK.strip()[:1500] + "\n```")
    L.append("")
    L.append("## 3. Annotate stage — rendered user messages (27 fingerprints)")
    L.append("")
    L.append("Reproduced verbatim via `render_user(fingerprint, examples)` with the "
             "stored per-fingerprint example payloads. First message shown in full, "
             "the rest truncated.")
    L.append("")
    for i, d in enumerate(sorted(ann, key=lambda x: x["fingerprint_id"])):
        fid = d["fingerprint_id"]
        rendered = prompt.render_user(fid, d.get("examples") or [])
        L.append(f"### 3.{i+1} `{fid}` — consensus `{d['consensus']['label']}`, "
                 f"tau={d.get('tau')}")
        L.append("")
        L.append("```")
        L.append(rendered if i == 0 else rendered[:400] + ("\n…(truncated)" if len(rendered) > 400 else ""))
        L.append("```")
        L.append("")
    L.append("## 4. repo_check stage — pass-1 system + template")
    L.append("")
    L.append("**system**")
    L.append("")
    L.append("```\n" + prompt.REPO_PASS1_SYSTEM.strip() + "\n```")
    L.append("")
    L.append("**user template**")
    L.append("")
    L.append("```\n" + prompt.REPO_PASS1_TEMPLATE.strip()[:900] + "\n```")
    L.append("")
    L.append("## 5. repo_check stage — pass-2 system + template")
    L.append("")
    L.append("**system**")
    L.append("")
    L.append("```\n" + prompt.REPO_PASS2_SYSTEM.strip() + "\n```")
    L.append("")
    L.append("**user template**")
    L.append("")
    L.append("```\n" + prompt.REPO_PASS2_TEMPLATE.strip()[:1000] + "\n```")
    L.append("")
    L.append("## 6. repo_check stage — two fully rendered examples")
    L.append("")
    for repo_full in ("0x0021/Linkora", "EndofTimeWorks/pluris-haven"):
        rc = None
        for f in sorted(RESULTS_DIR.glob("chunk_1*.jsonl")):
            for line in f.read_text(encoding="utf-8").splitlines():
                d = json.loads(line)
                if d.get("repo") == repo_full:
                    rc = d
                    break
            if rc:
                break
        if not rc:
            continue
        L.append(f"### `{repo_full}` (stratum {rc.get('stratum')}, weight {rc.get('weight')})")
        L.append("")
        repo = {"full_name": repo_full,
                "stratum": rc.get("stratum"), "weight": rc.get("weight"),
                "commit_sha": rc.get("commit_sha"),
                "summary": repo_summary(repo_full),
                "source_excerpts": repo_excerpts(repo_full),
                "matched_fingerprints": []}
        try:
            p1 = prompt.render_repo_pass1(repo)
            L.append("**pass-1 user message:**")
            L.append("")
            L.append("```\n" + p1[:1400] + ("\n…(truncated)" if len(p1) > 1400 else "") + "\n```")
            L.append("")
            p2 = prompt.render_repo_pass2(repo, labels, rc.get("pass1", {}).get("parsed", {}))
            L.append("**pass-2 user message:**")
            L.append("")
            L.append("```\n" + p2[:1400] + ("\n…(truncated)" if len(p2) > 1400 else "") + "\n```")
            L.append("")
        except Exception as exc:  # pragma: no cover
            L.append(f"_render skipped: {exc}_")
            L.append("")
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"[dump_prompts] wrote {OUT} ({len(L)} lines)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())