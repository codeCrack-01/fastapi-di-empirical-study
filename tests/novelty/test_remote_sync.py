"""Tests for remote/sync.py anti-entropy protocol (pure file logic)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from remote.sync import (  # noqa: E402
    final_crosscheck,
    list_missing,
    load_journal,
    load_received,
    pull_missing,
    save_received,
    sha256_file,
    verify_chunk,
)


def make_results(tmp: Path, n_chunks: int = 3) -> Path:
    results = tmp / "results"
    results.mkdir()
    for i in range(n_chunks):
        (results / f"chunk_{i:04d}.jsonl").write_text(json.dumps({"chunk": i}) + "\n")
    journal = []
    for i in range(n_chunks):
        f = results / f"chunk_{i:04d}.jsonl"
        journal.append({
            "chunk_id": i, "file": f.name, "sha256": sha256_file(f),
            "n": 1, "status": "complete",
        })
    (results / "journal.jsonl").write_text("".join(json.dumps(e) + "\n" for e in journal))
    return results


def test_load_journal_and_verify(tmp_path):
    results = make_results(tmp_path)
    j = load_journal(results)
    assert len(j) == 3
    assert verify_chunk(results / "chunk_0000.jsonl", j[0])

    bad = dict(j[0]); bad["sha256"] = "0" * 64
    assert not verify_chunk(results / "chunk_0000.jsonl", bad)
    assert not verify_chunk(results / "missing.jsonl", j[0])


def test_pull_missing_and_received(tmp_path):
    results = make_results(tmp_path)
    received = tmp_path / "received.txt"
    local = tmp_path / "local"
    report = pull_missing(results, received, local)
    assert report["copied"] == 3 and report["verified"] == 3 and report["failed"] == []
    got = load_received(received)
    assert len(got) == 3
    assert list_missing(got, load_journal(results)) == []
    # every copied file verifies against the journal
    for cid, e in load_journal(results).items():
        assert verify_chunk(local / e["file"], e)


def test_pull_missing_detects_corruption(tmp_path):
    results = make_results(tmp_path)
    # corrupt chunk 1 before pulling
    (results / "chunk_0001.jsonl").write_text("CORRUPTED")
    received = tmp_path / "received.txt"
    local = tmp_path / "local"
    report = pull_missing(results, received, local)
    assert report["failed"] and any(cid == 1 for cid, _ in report["failed"])
    got = load_received(received)
    assert 1 not in got  # never recorded as received
    assert not (local / "chunk_0001.jsonl").exists()  # torn copy removed


def test_save_received_roundtrip(tmp_path):
    received = tmp_path / "received.txt"
    save_received(received, {2: "aa", 10: "bb"})
    assert load_received(received) == {2: "aa", 10: "bb"}


def test_final_crosscheck_repushes_leftovers(tmp_path):
    results = make_results(tmp_path, n_chunks=4)
    share = tmp_path / "share"
    received = tmp_path / "received.txt"
    # pretend our machine only got two chunks before going offline
    save_received(received, load_received(tmp_path / "nonexistent"))  # empty
    # simulate partial: our side recorded only 0 and 1
    j = load_journal(results)
    save_received(received, {0: j[0]["sha256"], 1: j[1]["sha256"]})

    report = final_crosscheck(results, received, share)
    # chunks 2,3 re-pushed into share/results
    assert report["repushed"] == ["chunk_0002.jsonl", "chunk_0003.jsonl"]
    for f in ("chunk_0002.jsonl", "chunk_0003.jsonl"):
        assert (share / f).exists()

    # once our received.txt is complete, COMPLETE.txt is emitted
    save_received(received, {cid: e["sha256"] for cid, e in j.items()})
    share.mkdir(exist_ok=True)
    report2 = final_crosscheck(results, received, share)
    assert report2["all_done"] and (share / "COMPLETE.txt").exists()