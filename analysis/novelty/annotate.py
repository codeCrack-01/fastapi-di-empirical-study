"""analysis/novelty/annotate.py — chunked, journaled, power-loss-safe annotation.

Input
    analysis/novelty/out/novelty_fingerprints.json (grouped fingerprints)
    analysis/novelty/out/novelty_panel.json        (selected raters + k + tau + eps)

Model
    each fingerprint gets the pinned prompt (prompt.py) from each panel rater;
    consensus.consensus_decision turns the k labels into the item label at tau.

Chunks (the sync-protocol contract)
    Fingerprints are processed in --chunk-size (default 10) groups. Each chunk
    becomes ONE immutable file results/chunk_<NNNN>.jsonl, finalised atomically
    (temp + rename) with a recorded SHA-256 in results/journal.jsonl. Chunk ids
    are derived from fingerprint position (index // chunk_size), so chunk N is
    always the same set of fingerprints regardless of when it was run.

Resume
    - journal entry present  => chunk complete, skipped wholesale.
    - staging/chunk_<NNNN>.jsonl exists => crash mid-chunk; its rows are
      re-loaded and only the missing fingerprints are re-queried, then the chunk
      is finalised. No duplicate rows, no reprocessing of finished chunks.

Pass  --limit N  to cap fingerprints processed in this invocation (test runs).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Callable

OUT_DIR = Path(__file__).resolve().parent / "out"
DEFAULT_CHUNK_SIZE = 10


def load_panel(path: Path) -> dict:
    return json.loads(Path(path).read_text())


def load_fingerprints(path: Path) -> list[dict]:
    return json.loads(Path(path).read_text())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def read_journal(out_dir: Path) -> dict[int, dict]:
    entries: dict[int, dict] = {}
    jpath = out_dir / "journal.jsonl"
    if jpath.exists():
        for line in jpath.read_text().splitlines():
            if not line.strip():
                continue
            try:
                e = json.loads(line)
                entries[int(e["chunk_id"])] = e
            except (KeyError, ValueError, json.JSONDecodeError):
                continue
    return entries


def _staged_ids(staging: Path) -> set[str]:
    ids: set[str] = set()
    if not staging.exists():
        return ids
    for line in staging.read_text().splitlines():
        if line.strip():
            try:
                ids.add(json.loads(line)["fingerprint_id"])
            except (KeyError, json.JSONDecodeError):
                continue
    return ids


def _atomically_finalize(staging: Path, out_dir: Path, chunk_id: int, entries: list[dict]) -> Path:
    dst = out_dir / f"chunk_{chunk_id:04d}.jsonl"
    tmp = out_dir / f".chunk_{chunk_id:04d}.tmp"
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in entries))
    os.replace(tmp, dst)
    return dst


def _finalize_chunk(out_dir: Path, chunk_id: int, staging: Path, entries: list[dict]) -> None:
    dst = _atomically_finalize(staging, out_dir, chunk_id, entries)
    digest = sha256_file(dst)
    with (out_dir / "journal.jsonl").open("a") as j:
        j.write(json.dumps({
            "chunk_id": chunk_id,
            "file": dst.name,
            "sha256": digest,
            "n": len(entries),
            "first_fp": entries[0]["fingerprint_id"] if entries else None,
            "last_fp": entries[-1]["fingerprint_id"] if entries else None,
            "status": "complete",
            "created_utc": datetime.now(timezone.utc).isoformat(),
        }, ensure_ascii=False) + "\n")
        j.flush()
        os.fsync(j.fileno())
    staging.unlink(missing_ok=True)


def _annotate_one(
    fp: dict, clients: dict[str, "object"], tau: float, profile: dict,
    render_system: Callable[[], str], render_user: Callable[[str, list[dict]], str],
    parse_response: Callable[[str], dict],
) -> dict:
    fid = fp.get("fingerprint") or fp.get("id")
    examples = fp.get("examples") or []
    rater_labels: dict[str, str] = {}
    responses = []
    for m, cli in clients.items():
        rec = cli.generate(render_system(), render_user(fid, examples[:5]))
        parsed = parse_response(rec.get("content", ""))
        rater_labels[m] = parsed["label"]
        responses.append({
            "model": m, "latency_s": rec.get("latency_s"),
            "content": rec.get("content", ""),
            "thinking": rec.get("thinking") or rec.get("reasoning"),
            "parsed": parsed,
        })
    decision = None
    from consensus import consensus_decision
    decision = consensus_decision(list(rater_labels.values()), tau)
    return {
        "fingerprint_id": fid,
        "count": fp.get("count") or fp.get("total_occurrences"),
        "repos": fp.get("repos"),
        "examples": examples[:5],
        "rater_labels": rater_labels,
        "consensus": decision,
        "tau": tau,
        "executor": profile,
        "responses": responses,
    }


def run_annotate(
    fingerprints: list[dict],
    panel: dict,
    out_dir: Path,
    chunk_size: int = DEFAULT_CHUNK_SIZE,
    host: str = "",
    limit: int = 0,
    rater_factory: Callable[[list[str]], dict] | None = None,
) -> dict:
    """Annotate fingerprints into journaled chunks. Returns a run summary."""
    from client import OllamaClient
    from executor import ExecutorProfile
    from prompt import parse_response, render_system, render_user

    out_dir.mkdir(parents=True, exist_ok=True)
    staging_dir = out_dir / "staging"
    staging_dir.mkdir(parents=True, exist_ok=True)

    clients = (rater_factory or (lambda ms: {m: OllamaClient(model=m, host=host) for m in ms}))(panel["panel"])
    profile = ExecutorProfile.capture(list(clients)).to_dict()
    tau = panel.get("tau", 0.65)
    journal = read_journal(out_dir)

    processed = 0
    skipped = 0
    chunks_finalized = 0
    limit_hit = False

    for start in range(0, len(fingerprints), chunk_size):
        if limit > 0 and processed >= limit:
            limit_hit = True
            break
        chunk = fingerprints[start:start + chunk_size]
        chunk_id = start // chunk_size

        if chunk_id in journal:
            skipped += len(chunk)
            continue

        staging = staging_dir / f"chunk_{chunk_id:04d}.jsonl"
        done_ids = _staged_ids(staging)
        entries: list[dict] = []
        if staging.exists():
            for line in staging.read_text().splitlines():
                if line.strip():
                    try:
                        entries.append(json.loads(line))
                    except json.JSONDecodeError:
                        pass

        for fp in chunk:
            fid = fp.get("fingerprint") or fp.get("id")
            if fid in done_ids or (limit > 0 and processed >= limit):
                if fid in done_ids:
                    skipped += 1
                if limit > 0 and processed >= limit:
                    limit_hit = True
                    break
                continue
            rec = _annotate_one(
                fp, clients, tau, profile, render_system, render_user, parse_response
            )
            entries.append(rec)
            with staging.open("a") as s:
                s.write(json.dumps(rec, ensure_ascii=False) + "\n")
                s.flush()
                os.fsync(s.fileno())
            processed += 1
        else:
            # chunk complete only when EVERY fingerprint in it was annotated
            _finalize_chunk(out_dir, chunk_id, staging, entries)
            chunks_finalized += 1
            continue
        # limit cut this chunk short: leave staging in place, stop entirely
        limit_hit = True
        break

    return {
        "processed": processed,
        "skipped": skipped,
        "chunks_finalized": chunks_finalized,
        "limit_hit": limit_hit,
        "panel": panel["panel"],
        "tau": tau,
        "executor_machine": profile.get("machine"),
        "out_dir": str(out_dir),
    }


def main():
    ap = argparse.ArgumentParser(description="Annotate corpus fingerprints into immutable chunks")
    ap.add_argument("--fingerprints", default=str(OUT_DIR / "novelty_fingerprints.json"))
    ap.add_argument("--panel", default=str(OUT_DIR / "novelty_panel.json"))
    ap.add_argument("--out-dir", default=str(OUT_DIR / "results"))
    ap.add_argument("--chunk-size", type=int, default=DEFAULT_CHUNK_SIZE)
    ap.add_argument("--host", default="")
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    panel = load_panel(Path(args.panel))
    fprints = load_fingerprints(Path(args.fingerprints))
    summary = run_annotate(
        fprints, panel, Path(args.out_dir),
        chunk_size=args.chunk_size, host=args.host, limit=args.limit,
    )
    print(f"[annotate] {summary}")


if __name__ == "__main__":
    main()