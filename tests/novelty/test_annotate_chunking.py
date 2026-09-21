"""Tests for analysis/novelty/annotate.py chunked/journaled model (offline fakes)."""
import hashlib
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "analysis" / "novelty"))

from annotate import (  # noqa: E402
    DEFAULT_CHUNK_SIZE,
    read_journal,
    run_annotate,
    sha256_file,
)

POOL = ["fake-a", "fake-b", "fake-c"]


class FakeClient:
    def __init__(self, model: str):
        self.model = model

    def generate(self, system: str, user: str) -> dict:
        seed = int(hashlib.sha256((self.model + user).encode()).hexdigest()[:8], 16)
        label = ["C1", "C2", "C3", "C4", "EX2", "Z",
                 "known", "variant", "novel", "false_pos", "external_di"][seed % 11]
        return {
            "content": json.dumps({"label": label}),
            "latency_s": 0.001, "model": self.model,
        }


def fake_factory(models):
    return {m: FakeClient(m) for m in models}


def make_fprint(n: int) -> list[dict]:
    return [
        {"fingerprint": f"FP::{i}", "count": 1, "repos": [f"r{i % 3}"],
         "examples": [{"repo": f"r{i % 3}", "line": i, "argument": "db", "context_function": "f"}]}
        for i in range(n)
    ]


def all_ids(tmp: Path) -> tuple[list[str], dict]:
    journal = read_journal(tmp)
    ids: list[str] = []
    for cid, entry in sorted(journal.items()):
        rows = [json.loads(l) for l in (tmp / entry["file"]).read_text().splitlines() if l.strip()]
        ids += [r["fingerprint_id"] for r in rows]
    return ids, journal


def test_chunk_files_are_immutable_and_journaled(tmp_path):
    out = tmp_path / "results"
    run_annotate(make_fprint(25), {"panel": POOL}, out, chunk_size=10,
                 rater_factory=fake_factory)
    ids, journal = all_ids(out)
    assert len(journal) == 3
    assert sorted(ids) == sorted(f"FP::{i}" for i in range(25))
    assert len(set(ids)) == 25  # no duplicates across chunks
    for cid, entry in journal.items():
        assert entry["status"] == "complete"
        assert sha256_file(out / entry["file"]) == entry["sha256"]
    # staging cleaned up
    assert not (out / "staging").exists() or not list((out / "staging").iterdir())


def test_resume_after_crash_mid_chunk(tmp_path):
    out = tmp_path / "results"
    fprints = make_fprint(25)
    run_annotate(fprints, {"panel": POOL}, out, chunk_size=10, limit=12,
                 rater_factory=fake_factory)
    journal_after_limit = read_journal(out)
    # chunk0 done (10), chunk1 partially staged (2)
    assert 0 in journal_after_limit and 1 not in journal_after_limit
    staged = out / "staging" / "chunk_0001.jsonl"
    assert staged.exists()
    staged_count = len([l for l in staged.read_text().splitlines() if l.strip()])

    # full resume: chunk1 + chunk2 complete, nothing duplicated, nothing re-queryed
    run_annotate(fprints, {"panel": POOL}, out, chunk_size=10, rater_factory=fake_factory)
    ids, journal = all_ids(out)
    assert len(journal) == 3
    assert sorted(ids) == sorted(f"FP::{i}" for i in range(25))
    assert len(set(ids)) == 25


def test_rerun_skips_completed_chunks(tmp_path):
    out = tmp_path / "results"
    fprints = make_fprint(10)
    run_annotate(fprints, {"panel": POOL}, out, chunk_size=10, rater_factory=fake_factory)
    before = (out / "chunk_0000.jsonl").read_bytes()
    run_annotate(fprints, {"panel": POOL}, out, chunk_size=10, rater_factory=fake_factory)
    assert (out / "chunk_0000.jsonl").read_bytes() == before
    assert len(read_journal(out)) == 1