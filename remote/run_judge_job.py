"""remote/run_judge_job.py — headless judge-job driver for the remote executor.

Stages (resumable after any power cut):
    profile   capture ExecutorProfile -> out/executor.json
    select    run_selection (anchor qualification + floor + diversity + LOO k)
    reverify  anchor gate on THIS executor; blocks annotate on breach
    annotate  chunked, journaled, immutable (analysis.novelty.annotate)
    publish   copy results/shared-folder artifacts + received.txt
    complete  final cross-check + COMPLETE.txt

State lives in out/job_state.json; a crash resumes the FIRST unfinished stage
(annotate itself resumes at chunk granularity via its journal + staging).

usage:
    python remote/run_judge_job.py --job job.json          # real Ollama
    python remote/run_judge_job.py --job job.json --fake   # plumbing smoke test
"""
from __future__ import annotations

import argparse
import hashlib
import json
import time
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parent.parent
import sys  # noqa: E402
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "analysis" / "novelty"))

STAGES = ["profile", "select", "reverify", "annotate", "publish", "complete"]

DEFAULT_JOB = {
    "version": 1,
    "chunk_size": 10,
    "tau": 0.65,
    "floor": 0.80,
    "eps": 0.02,
    "max_k": 5,
    "host": "",
    "pool": ["qwen3-coder:4b", "llama3.2:3b", "deepseek-coder:6.7b"],
    "fingerprints": "analysis/novelty/out/novelty_fingerprints.json",
    "out_dir": "analysis/novelty/out",
    "results_dir": "analysis/novelty/out/results",
    "share_dir": "share",
    "received_path": "share/received.txt",
    "job_state": "analysis/novelty/out/job_state.json",
    "ollama_path": "ollama",
}


def load_job(path: Path) -> dict:
    cfg = dict(DEFAULT_JOB)
    cfg.update(json.loads(Path(path).read_text()))
    return cfg


def load_state(path: Path) -> dict:
    if path.exists():
        try:
            return json.loads(path.read_text())
        except json.JSONDecodeError:
            pass
    return {"stage_done": [], "stage": None}


def save_state(path: Path, state: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(state, indent=2))


def wait_for_ollama(host: str, timeout_s: int = 600, interval: float = 5.0) -> bool:
    """Poll /api/tags until Ollama answers (covers boot race after power cut)."""
    import requests
    base = (host or "http://localhost:11434").rstrip("/")
    deadline = time.time() + timeout_s
    while time.time() < deadline:
        try:
            r = requests.get(f"{base}/api/tags", timeout=10)
            if r.status_code == 200:
                return True
        except requests.RequestException:
            pass
        time.sleep(interval)
    return False


def _refresh_mtime(path: Path) -> None:
    """Touch a heartbeat file so an external watchdog sees liveness."""
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        path.touch()
    else:
        path.write_text(str(time.time()))


def run_stage(stage: str, job: dict, state: dict, fake: bool,
              rater_factory: Callable[[list[str]], dict] | None) -> None:
    from analysis.novelty import annotate as ann_mod
    from analysis.novelty.executor import ExecutorProfile
    from analysis.novelty.prompt import parse_response  # noqa: F401
    from analysis.novelty.select_panel import run_selection

    out_dir = Path(job["out_dir"])
    results_dir = Path(job["results_dir"])
    host = job["host"]
    pool = job["pool"]
    out_dir.mkdir(parents=True, exist_ok=True)

    ref = out_dir / "job.heartbeat"
    if stage == "profile":
        profile = ExecutorProfile.capture(pool)
        (out_dir / "executor.json").write_text(json.dumps(profile.to_dict(), indent=2))
    elif stage == "select":
        run_selection(
            pool=pool, host=host, floor=job["floor"], eps=job["eps"],
            max_k=job["max_k"], out_dir=out_dir, apply=not fake,
            rater_factory=rater_factory,
        )
    elif stage == "reverify":
        from analysis.novelty.reverify import run_reverify
        run_reverify(
            panel_path=out_dir / "novelty_panel.json",
            selection_path=out_dir / "novelty_selection.json",
            host=host, out_path=out_dir / "novelty_reverify.json",
            rater_factory=rater_factory,
        )
    elif stage == "annotate":
        fprints = json.loads(Path(job["fingerprints"]).read_text())
        if isinstance(fprints, dict):
            fprints = fprints["fingerprints"]
        panel = json.loads((out_dir / "novelty_panel.json").read_text())
        summary = ann_mod.run_annotate(
            fprints, panel, results_dir,
            chunk_size=job["chunk_size"], host=host, rater_factory=rater_factory,
        )
        print(f"[job] annotate -> {summary}")
    elif stage == "publish":
        _publish(results_dir, job)
        _refresh_mtime(out_dir / "job.heartbeat")
    elif stage == "complete":
        _finalize(results_dir, job)
    else:
        raise SystemExit(f"[job] unknown stage {stage}")
    _refresh_mtime(ref)


def _chunk_files(results_dir: Path) -> list[Path]:
    return sorted(results_dir.glob("chunk_*.jsonl"))


def _publish(results_dir: Path, job: dict) -> None:
    """Idempotently mirror results + journal into the shared folder."""
    share = Path(job["share_dir"])
    share_results = share / "results"
    share_results.mkdir(parents=True, exist_ok=True)
    for f in list(results_dir.glob("chunk_*.jsonl")) + [results_dir / "journal.jsonl"]:
        if not f.exists():
            continue
        dst = share_results / f.name
        if dst.exists() and f.read_bytes() == dst.read_bytes():
            continue
        dst.write_bytes(f.read_bytes())
    # executor-side received tracker (its own view of chunks in results_dir)
    from remote.sync import load_journal, load_received, save_received
    journal = load_journal(results_dir)
    recv_path = Path(job["received_path"])
    mapping = load_received(recv_path)
    for cid, e in journal.items():
        mapping[cid] = e["sha256"]
    save_received(recv_path, mapping)
    exe = Path(job["out_dir"]) / "executor.json"
    if exe.exists():  # absent only if 'profile' was pre-marked done without it
        (share / "executor.json").write_text(exe.read_text())


def _finalize(results_dir: Path, job: dict) -> None:
    from remote.sync import final_crosscheck, load_journal, load_received
    share_results = Path(job["share_dir"]) / "results"
    journal = load_journal(results_dir)
    recv = load_received(Path(job["received_path"]))
    report = final_crosscheck(results_dir, Path(job["received_path"]), share_results)
    all_have = all(recv.get(cid) == e.get("sha256") for cid, e in journal.items())
    print(f"[job] final cross-check: all_done={report['all_done']} "
          f"repushed={len(report['repushed'])} all_have_local={all_have}")
    if report["all_done"] and all_have:
        (Path(job["out_dir"]) / "job.complete").write_text(json.dumps({
            "stages": STAGES,
            "n_chunks": len(journal),
            "completed_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }, indent=2))


def _fake_factory(pool: list[str]) -> dict:
    """Deterministic hash-based fake raters; plumbing smoke test only."""
    class FakeClient:
        def __init__(self, model: str):
            self.model = model

        def generate(self, system: str, user: str) -> dict:
            seed = int(hashlib.sha256((self.model + user).encode()).hexdigest()[:8], 16)
            labels = ["C1", "C2", "C3", "C4", "C5", "C6", "C7", "C8", "EX2", "Z",
                      "known", "variant", "novel", "false_pos", "external_di"]
            label = labels[seed % len(labels)]
            return {
                "content": json.dumps({"label": label, "rule": None, "evidence": "fake"}),
                "latency_s": 0.0, "model": self.model,
            }
    return {m: FakeClient(m) for m in pool}


def main():
    ap = argparse.ArgumentParser(description="Headless judge-job driver")
    ap.add_argument("--job", default="job.json")
    ap.add_argument("--fake", action="store_true", help="plumbing smoke test (no Ollama)")
    args = ap.parse_args()

    job = load_job(Path(args.job))
    state_path = Path(job["job_state"])
    state = load_state(state_path)
    done = list(state.get("stage_done", []))

    if not (args.fake or job.get("skip_ollama_wait")):
        if not wait_for_ollama(job["host"]):
            raise SystemExit("[job] Ollama did not become reachable; bailing.")
    rater_factory = _fake_factory if args.fake else None

    for stage in STAGES:
        if stage in done:
            print(f"[job] stage {stage}: already done, skipping")
            continue
        print(f"[job] stage {stage}: start")
        try:
            run_stage(stage, job, state, args.fake, rater_factory)
        except RuntimeError as exc:
            # reverify breach: must NOT annotate on a drifted executor
            state["stage"] = stage
            state["error"] = str(exc)
            state["blocked"] = True
            save_state(state_path, state)
            raise SystemExit(f"[job] stage {stage} blocked: {exc}")
        done.append(stage)
        state["stage_done"] = done
        state["stage"] = stage
        state["completed_utc"] = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        save_state(state_path, state)
    print("[job] ALL STAGES COMPLETE")


if __name__ == "__main__":
    main()