"""remote/sync.py — anti-entropy sync between the remote executor and our machine.

Contract
    - The executor writes immutable chunk files  results/chunk_<NNNN>.jsonl  and
      one append-only  results/journal.jsonl  whose every entry carries the
      chunk's SHA-256. Chunk ids are position-derived, so chunk N is always the
      same fingerprints.
    - Our machine keeps  received.txt (chunk_id -> sha256 seen & verified).
    - Reconciliation is pure anti-entropy over a shared folder (Syncthing /
      OneDrive / USB), stridge of any one side being offline:

        pull_missing()          our side copies any journaled chunk we lack,
                                verifies its sha, appends to received.txt.
        final_crosscheck()      at run end: the executor diffs its journal vs
                                the last received.txt it can see, re-pushes
                                leftovers, then writes COMPLETE.txt.

    Everything is read-only on the journal; deletes never happen here. Files
    are immutable by construction (annotate.py only creates them once).
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""):
            h.update(block)
    return h.hexdigest()


def load_journal(results_dir: Path) -> dict[int, dict]:
    """journal.jsonl -> {chunk_id: entry}. Returns {} if missing/corrupt."""
    entries: dict[int, dict] = {}
    jpath = results_dir / "journal.jsonl"
    if not jpath.exists():
        return entries
    for line in jpath.read_text().splitlines():
        if not line.strip():
            continue
        try:
            e = json.loads(line)
            entries[int(e["chunk_id"])] = e
        except (KeyError, ValueError, json.JSONDecodeError):
            continue
    return entries


def verify_chunk(chunk_file: Path, entry: dict) -> bool:
    """True iff the file exists AND its sha256 matches the journal entry."""
    if not chunk_file.exists():
        return False
    want = entry.get("sha256")
    if not want:
        return False
    return sha256_file(chunk_file) == want


def load_received(received_path: Path) -> dict[int, str]:
    """received.txt -> {chunk_id: sha256}. Tolerates partial/corrupt lines."""
    got: dict[int, str] = {}
    if not received_path.exists():
        return got
    for line in received_path.read_text().splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            cid, sha = line.split(" ", 1)
            got[int(cid)] = sha
        except ValueError:
            continue
    return got


def save_received(received_path: Path, mapping: dict[int, str]) -> Path:
    received_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = received_path.with_suffix(".tmp")
    lines = "\n".join(f"{cid} {sha}" for cid, sha in sorted(mapping.items())) + "\n"
    tmp.write_text(lines)
    tmp.replace(received_path)
    return received_path


def list_missing(received: dict[int, str], journal: dict[int, dict]) -> list[tuple[int, dict]]:
    """Journal entries whose chunk we have not yet verified as received."""
    return [(cid, e) for cid, e in sorted(journal.items()) if received.get(cid) != e.get("sha256")]


def pull_missing(results_dir: Path, received_path: Path, local_dir: Path) -> dict:
    """Our side: copy+verify every journaled chunk we lack into local_dir.

    Returns {copied, verified, failed} where failed lists (chunk_id, file).
    Mutates received.txt only for chunks that verified.
    """
    journal = load_journal(results_dir)
    received = load_received(received_path)
    local_dir.mkdir(parents=True, exist_ok=True)

    copied = verified = 0
    failed: list[tuple[int, str]] = []
    for cid, entry in list_missing(received, journal):
        src = results_dir / entry["file"]
        dst = local_dir / entry["file"]
        if not src.exists():
            failed.append((cid, entry["file"]))
            continue
        dst.write_bytes(src.read_bytes())
        if verify_chunk(dst, entry):
            received[cid] = entry["sha256"]
            verified += 1
        else:
            failed.append((cid, entry["file"]))
            dst.unlink(missing_ok=True)
            continue
        copied += 1
    save_received(received_path, received)
    return {"copied": copied, "verified": verified, "failed": failed}


def final_crosscheck(results_dir: Path, received_path: Path, share_dir: Path) -> dict:
    """Executor side: after the run, diff journal vs latest received.txt.

    Re-pushes leftovers into share_dir/results (idempotent), returns the list
    re-pushed, and writes COMPLETE.txt when all journaled chunks are accounted
    for. Receives may be missing if our machine was off the whole run: in that
    case EVERY chunk is 'leftover' and gets re-pushed (that's the recovery).
    """
    journal = load_journal(results_dir)
    received = load_received(received_path)
    missing = list_missing(received, journal)

    out = results_dir if results_dir == share_dir or not share_dir else share_dir
    out.mkdir(parents=True, exist_ok=True)
    repushed: list[str] = []
    for cid, entry in missing:
        src = results_dir / entry["file"]
        if not src.exists():
            continue
        dst = out / entry["file"]
        dst.write_bytes(src.read_bytes())
        repushed.append(entry["file"])

    all_done = not list_missing(received, journal) if not missing else False
    # recompute: caller may have updated received between calls
    still_missing = list_missing(load_received(received_path), load_journal(results_dir))
    all_done = not still_missing
    if all_done:
        (out / "COMPLETE.txt").write_text(json.dumps({
            "n_chunks": len(journal),
            "verified": len(journal) - len(still_missing),
            "writer": "executor",
        }))
    return {"repushed": repushed, "all_done": all_done, "still_missing": len(still_missing)}