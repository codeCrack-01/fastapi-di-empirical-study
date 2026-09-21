"""End-to-end test of the remote judge-job stage machine (offline --fake)."""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))


@pytest.fixture
def jobdir(tmp_path):
    out = tmp_path / "out"
    share = tmp_path / "share"
    results = out / "results"
    fprints = [
        {"fingerprint": f"FP::{i}", "count": 1, "repos": [f"r{i}"],
         "examples": [{"repo": f"r{i}", "line": 0, "argument": "db", "context_function": "f"}]}
        for i in range(8)
    ]
    (tmp_path / "fprints.json").write_text(json.dumps(fprints))
    job = {
        "version": 1,
        "chunk_size": 10,
        "skip_ollama_wait": True,
        "pool": ["fake-qwen", "fake-llama", "fake-glm"],
        "fingerprints": str(tmp_path / "fprints.json"),
        "out_dir": str(out),
        "results_dir": str(results),
        "share_dir": str(share),
        "received_path": str(share / "received.txt"),
        "job_state": str(out / "job_state.json"),
        "host": "",
    }
    (tmp_path / "job.json").write_text(json.dumps(job))
    return tmp_path


def test_full_job_stage_machine(jobdir, monkeypatch):
    from remote.run_judge_job import main as job_main

    monkeypatch.chdir(jobdir)
    monkeypatch.setattr(sys, "argv", ["run_judge_job.py", "--job", str(jobdir / "job.json"), "--fake"])
    job_main()

    out = jobdir / "out"
    results = out / "results"
    share = jobdir / "share"

    assert (out / "executor.json").exists()           # profile
    assert (out / "novelty_panel.json").exists()      # select
    assert (out / "novelty_reverify.json").exists()   # reverify
    journal = json.loads((results / "journal.jsonl").read_text().splitlines()[0])
    assert journal["status"] == "complete"            # annotate finalized a chunk
    assert (share / "results" / "chunk_0000.jsonl").exists()   # publish
    assert (share / "results" / "COMPLETE.txt").exists()  # complete
    assert (out / "job.complete").exists()

    state = json.loads((out / "job_state.json").read_text())
    assert state["stage_done"] == ["profile", "select", "reverify", "annotate", "publish", "complete"]


def test_job_resumes_stages(jobdir, monkeypatch):
    """A 'profile'-only state resumes from 'select', not from scratch."""
    from remote.run_judge_job import main as job_main

    out = jobdir / "out"
    out.mkdir(exist_ok=True)
    (out / "job_state.json").write_text(json.dumps({"stage_done": ["profile"], "stage": "profile"}))

    monkeypatch.chdir(jobdir)
    monkeypatch.setattr(sys, "argv", ["run_judge_job.py", "--job", str(jobdir / "job.json"), "--fake"])
    job_main()

    state = json.loads((out / "job_state.json").read_text())
    assert state["stage_done"] == ["profile", "select", "reverify", "annotate", "publish", "complete"]