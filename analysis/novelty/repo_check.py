"""analysis/novelty/repo_check.py — two-pass per-repo DI check, chunked + resumable.

For each repo in the 327-sample novel-repo context, runs:

  pass 1 (blind)   the model reads the ACTUAL source excerpts and, WITHOUT any
                   fingerprint/label information, enumerates the DI patterns it
                   observes, each with a file:line citation.
  pass 2 (confront) the same code excerpts are shown again alongside the
                   repo's matched fingerprints and their panel labels; the
                   model must agree or overturn each (overturn requires a code
                   citation), and report anything pass-1 saw that the
                   fingerprint inventory missed.

Both passes + the model's `thinking` trace are persisted verbatim per repo.
The output uses the SAME immutable chunk/journal protocol as annotate.py, so
the driver's publish/complete cross-check and any manual retrieval all work.

usage:
    python analysis/novelty/repo_check.py --context out/novelty_repo_context.json \
        --labels out/results --out-dir out/results --host "" --limit N
"""
from __future__ import annotations

import argparse
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

OUT_DIR = Path(__file__).resolve().parent / "out"
DEFAULT_CHUNK_SIZE = 10
CHUNK_OFFSET = 10000          # chunk ids >= this: separates repo_check from annotate


def load_context(path: Path) -> list[dict]:
    data = json.loads(Path(path).read_text())
    if isinstance(data, dict):
        data = data.get("repos", [])
    if not isinstance(data, list):
        raise ValueError(f"context file {path} is neither an object with 'repos' nor a list")
    return data


def load_annotate_labels(results_dir: Path) -> dict[str, str]:
    """fingerprint_id -> consensus label, rebuilt from the annotate chunks."""
    labels: dict[str, str] = {}
    for f in sorted(results_dir.glob("chunk_*.jsonl")):
        if f.name.startswith("chunk_") and f.stem.split("_")[-1].isdigit():
            pass
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            c = rec.get("consensus")
            if isinstance(c, dict) and c.get("label"):
                labels[rec.get("fingerprint_id")] = str(c["label"]).lower()
    return labels


def _check_one(repo: dict, client: "object", labels: dict[str, str], profile: dict,
               system1: str, system2: str, render_pass1, render_pass2,
               parse_repo_response) -> dict:
    rec1 = client.generate(system1, render_pass1(repo))
    p1 = parse_repo_response(rec1.get("content", ""))
    rec2 = client.generate(system2, render_pass2(repo, labels, p1))
    p2 = parse_repo_response(rec2.get("content", ""))
    return {
        "repo": repo["full_name"],
        "stratum": repo.get("stratum"),
        "weight": repo.get("weight"),
        "commit_sha": repo.get("commit_sha"),
        "n_di_nodes": repo.get("n_di_nodes"),
        "pass1": {
            "content": rec1.get("content", ""),
            "thinking": rec1.get("thinking") or rec1.get("reasoning"),
            "parsed": p1,
            "latency_s": rec1.get("latency_s"),
        },
        "pass2": {
            "content": rec2.get("content", ""),
            "thinking": rec2.get("thinking") or rec2.get("reasoning"),
            "parsed": p2,
            "latency_s": rec2.get("latency_s"),
        },
        "executor": profile,
    }


def run_repo_check(
    contexts: list[dict],
    out_dir: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    host: str = "",
    labels: dict[str, str] | None = None,
    limit: int = 0,
    model: str = "qwen3:14b",
    rater_factory: Callable[[list[str]], dict] | None = None,
) -> dict:
    """Run the two-pass check over contexts into journaled chunks."""
    from client import OllamaClient
    from executor import ExecutorProfile
    from prompt import (REPO_PASS1_SYSTEM, REPO_PASS2_SYSTEM, parse_repo_response,
                        render_repo_pass1, render_repo_pass2)

    out_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = out_dir / "rc_staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    clients = (rater_factory or (lambda ms: {m: OllamaClient(model=m, host=host) for m in ms}))([model])
    client = clients[model]
    profile = ExecutorProfile.capture(list(clients)).to_dict()
    labels = labels or {}
    journal = _read_journal(out_dir)

    processed = 0
    skipped = 0
    chunks_finalized = 0
    limit_hit = False

    for start in range(0, len(contexts), chunk_size):
        if limit > 0 and processed >= limit:
            limit_hit = True
            break
        chunk = contexts[start:start + chunk_size]
        chunk_id = CHUNK_OFFSET + start // chunk_size

        if chunk_id in journal:
            skipped += len(chunk)
            continue

        staging = staging_dir / f"chunk_{chunk_id:04d}.jsonl"
        done_repos = _staged_repos(staging)
        entries: list[dict] = []
        if staging.exists():
            for line in staging.read_text().splitlines():
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        for repo in chunk:
            rr = repo.get("full_name")
            if rr in done_repos or (limit > 0 and processed >= limit):
                if rr in done_repos:
                    skipped += 1
                if limit > 0 and processed >= limit:
                    limit_hit = True
                    break
                continue
            rec = _check_one(repo, client, labels, profile,
                             REPO_PASS1_SYSTEM, REPO_PASS2_SYSTEM,
                             render_repo_pass1, render_repo_pass2, parse_repo_response)
            entries.append(rec)
            with staging.open("a") as s:
                s.write(json.dumps(rec, ensure_ascii=False) + "\n")
                s.flush()
                os.fsync(s.fileno())
            processed += 1
        else:
            _finalize_chunk(out_dir, chunk_id, staging, entries)
            chunks_finalized += 1
            continue
        limit_hit = True
        break

    return {
        "processed": processed,
        "skipped": skipped,
        "chunks_finalized": chunks_finalized,
        "limit_hit": limit_hit,
        "executor_machine": profile.get("machine"),
        "out_dir": str(out_dir),
    }


def _read_journal(out_dir: Path) -> dict[int, dict]:
    from annotate import read_journal
    return read_journal(out_dir)


def _staged_repos(staging: Path) -> set[str]:
    repos: set[str] = set()
    if not staging.exists():
        return repos
    for line in staging.read_text().splitlines():
        if line.strip():
            try:
                repos.add(json.loads(line)["repo"])
            except (KeyError, json.JSONDecodeError):
                continue
    return repos


def _finalize_chunk(out_dir: Path, chunk_id: int, staging: Path, entries: list[dict]) -> None:
    """Finalize a repo-check chunk: immutable file + journal entry (CHUNK_OFFSET ids)."""
    import hashlib
    dst = out_dir / f"chunk_{chunk_id:04d}.jsonl"
    tmp = out_dir / f".chunk_{chunk_id:04d}.tmp"
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in entries))
    os.replace(tmp, dst)

    h = hashlib.sha256()
    with dst.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    with (out_dir / "journal.jsonl").open("a") as j:
        j.write(json.dumps({
            "chunk_id": chunk_id,
            "file": dst.name,
            "sha256": h.hexdigest(),
            "n": len(entries),
            "first_repo": entries[0]["repo"] if entries else None,
            "last_repo": entries[-1]["repo"] if entries else None,
            "status": "complete",
            "created_utc": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False) + "\n")
        j.flush()
        os.fsync(j.fileno())
    staging.unlink(missing_ok=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="Two-pass per-repo DI check")
    ap.add_argument("--context", default=str(OUT_DIR / "novelty_repo_context.json"))
    ap.add_argument("--out-dir", default=str(OUT_DIR / "results"))
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    ap.add_argument("--host", default="")
    ap.add_argument("--model", default="qwen3:14b")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    contexts = load_context(Path(args.context))
    labels = load_annotate_labels(Path(args.out_dir))
    summary = run_repo_check(contexts, Path(args.out_dir),
                             chunk_size=args.chunk_size, host=args.host,
                             labels=labels, limit=args.limit, model=args.model)
    print(f"[repo_check] {summary}")


if __name__ == "__main__":
    main()