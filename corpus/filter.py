"""
corpus/filter.py — Eligibility filtering for the FastAPI DI corpus.

Stage 2 of the corpus methodology. Applies rules E1-E4 to the candidates
produced by finder.py, cloning repos that pass the cheap metadata rules.

Rules (census v2)
-----------------
E1  Imports FastAPI: files_importing_fastapi >= 1 in production code (extractor).
E2  Origin: not a fork and not archived (GitHub metadata).
E3  Window: pushed_at within the last 60 months (GitHub metadata; purely temporal).
E4  Scale: files_importing_fastapi >= E4_MIN_FASTAPI_FILES (rejects single-file/demo projects).

E2/E3 are metadata gates evaluated before cloning; E1/E4 are evaluated from the
extractor report after cloning. All rules are binary existence checks — no
magnitude thresholds.

Outputs
-------
corpus/manifest.json        accepted repos + metadata + extractor aggregate snapshot
corpus/exclusion_log.json   every candidate and the first rule that failed
corpus/reports/<name>.json  full extractor report per accepted repo

Usage:
    python corpus/filter.py --candidates corpus/candidates.json \
        --clone-dir study_repos/corpus \
        --output corpus/manifest.json
"""

from __future__ import annotations

import argparse
import calendar
import json
import os
import shutil
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional

ROOT = Path(__file__).resolve().parent
EXTRACTOR_DIR = ROOT.parent / "extractor"
sys.path.insert(0, str(EXTRACTOR_DIR))
sys.path.insert(0, str(ROOT))

from settings import (
    CLONE_DEPTH,
    CLONE_RETENTION,
    CLONE_TIMEOUT_SECONDS,
    CORPUS_SCHEMA_VERSION,
    E3_MAX_AGE_MONTHS,
    E4_MIN_FASTAPI_FILES,
    MAX_RETRY_ROUNDS,
    SAMPLE_SEED,
)

from extract import analyze_repo  # noqa: E402


class RuleResult:
    def __init__(self, rule: str, passed: bool, detail: str = ""):
        self.rule = rule
        self.passed = passed
        self.detail = detail

    def to_dict(self) -> dict:
        return {"rule": self.rule, "passed": self.passed, "detail": self.detail}


def clone_path(clone_dir: Path, full_name: str) -> Path:
    return clone_dir / full_name.replace("/", "__")


def _delete_clone(clone_dir: Path, full_name: str) -> None:
    dest = clone_path(clone_dir, full_name)
    if dest.is_dir():
        shutil.rmtree(dest, ignore_errors=True)


def _github_clone_env() -> dict:
    """Return extra env vars that let `git clone` authenticate via GITHUB_TOKEN.

    The token is injected through a live credential helper rather than the
    clone URL, so it is never persisted into the clone's .git/config.
    """
    token = os.environ.get("GITHUB_TOKEN")
    if not token:
        env_file = ROOT.parent / ".env"
        if env_file.exists():
            for line in env_file.read_text().splitlines():
                line = line.strip()
                if line.startswith("GITHUB_TOKEN="):
                    token = line.split("=", 1)[1].strip().strip("\"'")
                    break
    if not token:
        return {}
    helper = f"!f() {{ echo username=x-access-token; echo password={token}; }}; f"
    return {
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_CONFIG_COUNT": "1",
        "GIT_CONFIG_KEY_0": "credential.https://github.com.helper",
        "GIT_CONFIG_VALUE_0": helper,
    }


def clone_repo(candidate: dict, clone_dir: Path) -> Optional[Path]:
    full_name = candidate["full_name"]
    dest = clone_path(clone_dir, full_name)
    if (dest / ".git").exists():
        return dest
    dest.mkdir(parents=True, exist_ok=True)
    url = f"https://github.com/{full_name}.git"
    extra_env = _github_clone_env()
    try:
        result = subprocess.run(
            ["git", "clone", "--depth", str(CLONE_DEPTH), url, str(dest)],
            capture_output=True,
            text=True,
            timeout=CLONE_TIMEOUT_SECONDS,
            env={**os.environ, **extra_env},
        )
    except subprocess.TimeoutExpired:
        print(f"[filter] clone timed out {full_name}", flush=True)
        shutil.rmtree(dest, ignore_errors=True)
        return None
    if result.returncode != 0:
        print(f"[filter] clone failed {full_name}: {result.stderr[:200]}", flush=True)
        shutil.rmtree(dest, ignore_errors=True)
        return None
    return dest


def months_before(now: datetime, months: int) -> datetime:
    total = now.year * 12 + now.month - months
    y, m = divmod(total - 1, 12)
    m += 1
    day = min(now.day, calendar.monthrange(y, m)[1])
    return now.replace(year=y, month=m, day=day)


def evaluate(candidate: dict, repo_path: Optional[Path]) -> tuple[list[RuleResult], Optional[dict]]:
    """Evaluate eligibility rules E1-E4.

    E2/E3 are pure metadata rules and are always evaluated. When
    ``repo_path`` is None, evaluation stops there (metadata gate) so the
    caller can skip cloning for candidates that already fail a metadata rule;
    when ``repo_path`` is given, the clone-dependent rule E1 (production
    import of fastapi) is added at the front of the results, keeping
    canonical E1..E3 order.
    """
    results: list[RuleResult] = []

    fork = candidate.get("fork", False)
    archived = candidate.get("archived", False)
    results.append(
        RuleResult("E2", not fork and not archived, f"fork={fork} archived={archived}")
    )

    pushed_at = candidate.get("pushed_at")
    cutoff = months_before(datetime.now(timezone.utc), E3_MAX_AGE_MONTHS)
    try:
        pushed_dt = datetime.fromisoformat(pushed_at.replace("Z", "+00:00"))
        fresh = pushed_dt >= cutoff
    except (ValueError, AttributeError):
        fresh = False
    results.append(
        RuleResult(
            "E3",
            fresh,
            f"pushed_at={pushed_at} cutoff={cutoff.isoformat()}",
        )
    )

    if repo_path is None:
        return results, None

    try:
        report = analyze_repo(repo_path)
    except Exception as exc:
        results.insert(0, RuleResult("E1", False, f"extractor error: {exc}"))
        return results, None
    fastapi_files = report.aggregate.files_importing_fastapi
    results.insert(
        0,
        RuleResult("E1", fastapi_files >= 1, f"files_importing_fastapi={fastapi_files}"),
    )
    results.append(
        RuleResult(
            "E4",
            fastapi_files >= E4_MIN_FASTAPI_FILES,
            f"files_importing_fastapi={fastapi_files}",
        )
    )

    snapshot = report.model_dump(mode="json")
    return results, snapshot


def first_failure(results: list[RuleResult]) -> Optional[RuleResult]:
    for r in results:
        if not r.passed:
            return r
    return None


def process_candidate(
    candidate: dict,
    clone_dir: Path,
    reports_dir: Path,
    retention: str = CLONE_RETENTION,
) -> tuple[Optional[dict], Optional[dict]]:
    """Run the full E1-E4 pipeline for one candidate.

    Returns (accepted_entry, excluded_entry); exactly one is non-None.

    ``retention`` controls what happens to the clone afterwards: "all" keeps
    every processed clone, "accepted" keeps clones of accepted repos and
    deletes rejected ones, "none" deletes every clone after extraction
    (reports + manifest are sufficient for all analyses).
    """
    full_name = candidate["full_name"]
    results, snapshot = evaluate(candidate, None)
    failure = first_failure(results)
    if failure is not None:
        return None, {
            "full_name": full_name,
            "decision": "excluded",
            "reason": failure.rule,
            "detail": failure.detail,
            "rules": [r.to_dict() for r in results],
        }

    repo_path = clone_repo(candidate, clone_dir)
    if repo_path is None:
        return None, {
            "full_name": full_name,
            "decision": "excluded",
            "reason": "clone_failed",
            "rules": [],
        }
    results, snapshot = evaluate(candidate, repo_path)
    failure = first_failure(results)
    if failure is not None:
        if retention != "all":
            _delete_clone(clone_dir, full_name)
        return None, {
            "full_name": full_name,
            "decision": "excluded",
            "reason": failure.rule,
            "detail": failure.detail,
            "rules": [r.to_dict() for r in results],
        }

    entry = {
        "full_name": full_name,
        "repository_url": candidate.get("repository_url"),
        "stars_gh": candidate.get("stars_gh"),
        "stars_libio": candidate.get("stars_libio"),
        "forks_gh": candidate.get("forks_gh"),
        "created_at": candidate.get("created_at"),
        "pushed_at": candidate.get("pushed_at"),
        "commit_count": candidate.get("commit_count"),
        "py_ratio": candidate.get("py_ratio"),
        "license": candidate.get("license"),
        "topics": candidate.get("topics"),
        "description": candidate.get("description_gh") or candidate.get("description_libio"),
        "rules_passed": [r.rule for r in results],
        "rules": [r.to_dict() for r in results],
        "aggregate": snapshot["aggregate"],
        "coverage": snapshot["coverage"],
        "extractor_schema_version": snapshot["schema_version"],
        "extractor_version": snapshot["extractor_version"],
        "commit_sha": snapshot["repo"]["commit_sha"],
    }
    report_file = reports_dir / f"{full_name.replace('/', '__')}.json"
    report_file.write_text(json.dumps(snapshot, indent=2))
    if retention == "none":
        _delete_clone(clone_dir, full_name)
    return entry, None


def write_outputs(out_path: Path, config: dict, accepted: list[dict], excluded: list[dict]):
    manifest = {
        "schema_version": CORPUS_SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "config": config,
        "accepted": accepted,
        "accepted_count": len(accepted),
    }
    out_path.write_text(json.dumps(manifest, indent=2))
    exclusion_path = out_path.parent / "exclusion_log.json"
    exclusion_path.write_text(
        json.dumps(
            {
                "schema_version": CORPUS_SCHEMA_VERSION,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "excluded": excluded,
                "excluded_count": len(excluded),
            },
            indent=2,
        )
    )


def retry_clone_failures(
    excluded: list[dict],
    by_name: dict[str, dict],
    clone_dir: Path,
    reports_dir: Path,
    max_rounds: int = MAX_RETRY_ROUNDS,
    checkpoint=None,
    retention: str = CLONE_RETENTION,
) -> tuple[list[dict], list[dict]]:
    """Reprocess clone_failed entries for up to ``max_rounds``.

    Transient network failures are common; a repo that could not be cloned in
    one pass is retried in later rounds once the connection recovers. Entries
    that still fail after all rounds stay marked clone_failed in the output.
    Returns (newly_accepted, final_excluded).

    ``checkpoint(new_accepted, kept_excluded, still_failed)`` is called after
    each round so callers can persist partial progress (crash-resilience).
    """
    pending = [e for e in excluded if e["reason"] == "clone_failed"]
    kept = [e for e in excluded if e["reason"] != "clone_failed"]
    new_accepted: list[dict] = []
    round_num = 0
    while pending and round_num < max_rounds:
        round_num += 1
        print(
            f"[filter] retry round {round_num}/{max_rounds}: {len(pending)} clone_failed repos",
            flush=True,
        )
        still_failed: list[dict] = []
        start_time = time.monotonic()
        for i, entry in enumerate(pending):
            name = entry["full_name"]
            elapsed = int(time.monotonic() - start_time)
            print(
                f"[retry] round {round_num} ({i + 1}/{len(pending)}) {name} "
                f"[elapsed {elapsed // 60:02d}:{elapsed % 60:02d}]",
                flush=True,
            )
            accepted_entry, excluded_entry = process_candidate(
                by_name[name], clone_dir, reports_dir, retention
            )
            if accepted_entry is not None:
                new_accepted.append(accepted_entry)
                print(
                    f"  ACCEPTED (E1: {accepted_entry['aggregate']['files_importing_fastapi']} files)",
                    flush=True,
                )
            else:
                print(
                    f"  EXCLUDED ({excluded_entry['reason']}: {excluded_entry.get('detail', '')})",
                    flush=True,
                )
                if excluded_entry["reason"] == "clone_failed":
                    still_failed.append(excluded_entry)
                else:
                    kept.append(excluded_entry)
            time.sleep(0.2)
        pending = still_failed
        if checkpoint is not None:
            checkpoint(new_accepted, kept, pending)
    return new_accepted, kept + pending


def run_retry(
    candidates: list[dict],
    clone_dir: Path,
    reports_dir: Path,
    out_path: Path,
    limit: int = 0,
    max_rounds: int = MAX_RETRY_ROUNDS,
    retention: str = CLONE_RETENTION,
):
    """Reprocess only repos previously marked clone_failed, then merge into
    the existing manifest.json / exclusion_log.json.

    A prior run can record clone_failed when the network dropped mid-run even
    though the repo itself is clonable; those candidates passed the metadata
    gate but never had E1 evaluated. This mode evaluates them and merges
    the results, preserving everything that was already decided.
    """
    exclusion_path = out_path.parent / "exclusion_log.json"
    if not out_path.exists() or not exclusion_path.exists():
        sys.exit("--retry requires an existing manifest.json and exclusion_log.json")
    old_excluded = json.loads(exclusion_path.read_text())["excluded"]
    retry_names = sorted(
        {e["full_name"] for e in old_excluded if e["reason"] == "clone_failed"}
    )
    if limit:
        retry_names = retry_names[:limit]
    by_name = {c["full_name"]: c for c in candidates}
    retry_names = [n for n in retry_names if n in by_name]
    if not retry_names:
        print("[filter] no clone_failed entries to retry")
        return
    print(f"[filter] retrying {len(retry_names)} clone_failed candidates", flush=True)
    retry_set = set(retry_names)
    initial = [
        {"full_name": n, "decision": "excluded", "reason": "clone_failed", "rules": []}
        for n in retry_names
    ]
    old_manifest = json.loads(out_path.read_text())
    old_accepted = list(old_manifest["accepted"])
    old_accepted_names = {e["full_name"] for e in old_accepted}
    config = old_manifest.get("config", {})
    preserved = [e for e in old_excluded if e["full_name"] not in retry_set]

    def checkpoint(new_accepted, kept_excluded, still_failed):
        merged_accepted = old_accepted + [
            e for e in new_accepted if e["full_name"] not in old_accepted_names
        ]
        merged_excluded = preserved + kept_excluded + still_failed
        write_outputs(out_path, config, merged_accepted, merged_excluded)
        print(
            f"[filter] checkpoint persisted: {len(merged_accepted)} accepted, "
            f"{len(merged_excluded)} excluded",
            flush=True,
        )

    new_accepted, final_excluded = retry_clone_failures(
        initial, by_name, clone_dir, reports_dir, max_rounds,
        checkpoint=checkpoint, retention=retention,
    )
    merged_accepted = old_accepted + [
        e for e in new_accepted if e["full_name"] not in old_accepted_names
    ]
    merged_excluded = preserved + final_excluded
    write_outputs(out_path, config, merged_accepted, merged_excluded)
    print(
        f"[filter] retry done: +{len(new_accepted)} accepted; "
        f"total accepted {len(merged_accepted)}, excluded {len(merged_excluded)}"
    )


def run_delta(
    candidates: list[dict],
    clone_dir: Path,
    reports_dir: Path,
    out_path: Path,
    max_rounds: int = MAX_RETRY_ROUNDS,
    retention: str = CLONE_RETENTION,
    prune_rejected: bool = False,
):
    """Process only candidates not yet decided, merging into existing outputs.

    A previous run already decided 4,500 candidates; this mode accepts the
    newly-discovered tail without re-cloning anything already judged. Existing
    accepts/excludes are preserved verbatim; new decisions are appended and the
    manifest / exclusion_log are rewritten. Clone retention and an optional
    prune of rejected clones both follow the configured policy.
    """
    exclusion_path = out_path.parent / "exclusion_log.json"
    if not out_path.exists() or not exclusion_path.exists():
        sys.exit("--delta requires an existing manifest.json and exclusion_log.json")
    old_manifest = json.loads(out_path.read_text())
    old_config = old_manifest.get("config", {})
    old_accepted = list(old_manifest["accepted"])
    old_excluded = json.loads(exclusion_path.read_text())["excluded"]
    decided = {e["full_name"] for e in old_accepted} | {
        e["full_name"] for e in old_excluded
    }
    new_candidates = [c for c in candidates if c["full_name"] not in decided]
    print(
        f"[filter] delta mode: {len(new_candidates)} new candidates "
        f"({len(decided)} already decided, {len(new_candidates) + len(decided)} total)"
    )
    if not new_candidates:
        print("[filter] nothing new to process")
        return

    by_name = {c["full_name"]: c for c in candidates}
    new_accepted: list[dict] = []
    new_excluded: list[dict] = []
    start_time = time.monotonic()

    for i, candidate in enumerate(new_candidates):
        full_name = candidate["full_name"]
        elapsed = int(time.monotonic() - start_time)
        print(
            f"[filter] ({i + 1}/{len(new_candidates)}) {full_name} "
            f"[elapsed {elapsed // 60:02d}:{elapsed % 60:02d}, "
            f"new accepted {len(new_accepted)}, new excluded {len(new_excluded)}]",
            flush=True,
        )
        accepted_entry, excluded_entry = process_candidate(
            candidate, clone_dir, reports_dir, retention
        )
        if accepted_entry is not None:
            new_accepted.append(accepted_entry)
            print(
                f"  ACCEPTED (E1: {accepted_entry['aggregate']['files_importing_fastapi']} files)",
                flush=True,
            )
        else:
            new_excluded.append(excluded_entry)
            print(
                f"  EXCLUDED ({excluded_entry['reason']}: {excluded_entry.get('detail', '')})",
                flush=True,
            )
        time.sleep(0.2)

    preserved = [e for e in new_excluded if e["reason"] != "clone_failed"]
    pending = [e for e in new_excluded if e["reason"] == "clone_failed"]

    def checkpoint(new_acc, kept_excl, still_failed):
        merged_accepted = old_accepted + list(new_accepted) + list(new_acc)
        merged_excluded = old_excluded + preserved + list(kept_excl) + list(still_failed)
        write_outputs(out_path, old_config, merged_accepted, merged_excluded)
        print(
            f"[filter] delta checkpoint: {len(merged_accepted)} accepted, "
            f"{len(merged_excluded)} excluded",
            flush=True,
        )

    retried_accepted, final_all = retry_clone_failures(
        pending, by_name, clone_dir, reports_dir, max_rounds,
        checkpoint=checkpoint, retention=retention,
    )

    merged_accepted = old_accepted + new_accepted + retried_accepted
    merged_excluded = old_excluded + preserved + final_all
    write_outputs(out_path, old_config, merged_accepted, merged_excluded)
    if prune_rejected:
        pruned = 0
        for e in merged_excluded:
            if clone_path(clone_dir, e["full_name"]).is_dir():
                _delete_clone(clone_dir, e["full_name"])
                pruned += 1
        print(f"[filter] pruned {pruned} rejected clone dirs (retention={retention})")
    print(
        f"[filter] delta done: +{len(new_accepted) + len(retried_accepted)} accepted "
        f"(total {len(merged_accepted)}); excluded total {len(merged_excluded)}"
    )


def main():
    parser = argparse.ArgumentParser(description="Apply eligibility rules E1-E4")
    parser.add_argument("--candidates", default=str(ROOT / "candidates.json"))
    parser.add_argument("--clone-dir", default=str(ROOT.parent / "study_repos" / "corpus"))
    parser.add_argument("--output", default=str(ROOT / "manifest.json"))
    parser.add_argument("--limit", type=int, default=0, help="Only process first N candidates")
    parser.add_argument(
        "--keep-clones",
        choices=("all", "accepted", "none"),
        default=CLONE_RETENTION,
        help="Clone retention policy (default: %(default)s)",
    )
    parser.add_argument(
        "--delta",
        action="store_true",
        help="Process only candidates not yet decided; merge into existing manifest/exclusion_log",
    )
    parser.add_argument(
        "--prune-rejected",
        action="store_true",
        help="Delete clone dirs for every rejected repo after writing outputs (retention=accepted)",
    )
    parser.add_argument(
        "--retry", action="store_true", help="Reprocess clone_failed repos and merge results"
    )
    parser.add_argument(
        "--max-retry-rounds",
        type=int,
        default=MAX_RETRY_ROUNDS,
        help="Rounds of clone_failed retries after the main pass (0 disables)",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Skip candidates already decided in existing 0.2 manifest/exclusion_log "
        "(checkpointed runs only; older schema outputs are ignored)",
    )
    parser.add_argument(
        "--checkpoint-every",
        type=int,
        default=50,
        help="Write checkpoint outputs every N candidates (default: %(default)s)",
    )
    args = parser.parse_args()

    cand_path = Path(args.candidates)
    if not cand_path.exists():
        sys.exit(f"candidates file not found: {cand_path}")
    payload = json.loads(cand_path.read_text())
    candidates = payload["candidates"]
    print(f"[filter] {len(candidates)} candidates loaded from {cand_path}", flush=True)

    clone_dir = Path(args.clone_dir)
    clone_dir.mkdir(parents=True, exist_ok=True)
    reports_dir = Path(args.output).parent / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    config = {
        "sample_seed": SAMPLE_SEED,
        "E3_max_age_months": E3_MAX_AGE_MONTHS,
    }

    if args.delta:
        run_delta(
            candidates,
            clone_dir,
            reports_dir,
            Path(args.output),
            args.max_retry_rounds,
            retention=args.keep_clones,
            prune_rejected=args.prune_rejected,
        )
        return

    if args.retry:
        run_retry(
            candidates,
            clone_dir,
            reports_dir,
            Path(args.output),
            args.limit,
            args.max_retry_rounds,
            retention=args.keep_clones,
        )
        return

    if args.limit:
        candidates = candidates[: args.limit]

    accepted: list[dict] = []
    excluded: list[dict] = []
    decided: set[str] = set()
    out_path = Path(args.output)
    if args.resume:
        try:
            prev = json.loads(out_path.read_text())
            if prev.get("schema_version") == CORPUS_SCHEMA_VERSION:
                accepted = list(prev.get("accepted", []))
                decided.update(e["full_name"] for e in accepted)
            else:
                print(
                    f"[filter] resume: existing manifest is schema {prev.get('schema_version')} "
                    f"(!= {CORPUS_SCHEMA_VERSION}), ignoring; will do a clean unchanged pass",
                    flush=True,
                )
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(f"[filter] WARNING: could not load previous manifest for resume: {e}", flush=True)
        exclusion_path = out_path.parent / "exclusion_log.json"
        try:
            prev = json.loads(exclusion_path.read_text())
            if prev.get("schema_version") == CORPUS_SCHEMA_VERSION:
                excluded = list(prev.get("excluded", []))
                decided.update(e["full_name"] for e in excluded)
        except FileNotFoundError:
            pass
        except (json.JSONDecodeError, KeyError, OSError) as e:
            print(
                f"[filter] WARNING: could not load previous exclusion_log for resume: {e}",
                flush=True,
            )
        if decided:
            print(
                f"[filter] resume: {len(decided)} candidates already decided, "
                f"{len([c for c in candidates if c['full_name'] not in decided])} remaining",
                flush=True,
            )

    start_time = time.monotonic()
    skipped = 0
    for i, candidate in enumerate(candidates):
        full_name = candidate["full_name"]
        if args.resume and full_name in decided:
            skipped += 1
            continue
        dest = clone_path(clone_dir, full_name)
        if (dest / ".git").exists():
            verify = subprocess.run(
                ["git", "-C", str(dest), "rev-parse", "--verify", "HEAD"],
                capture_output=True,
                text=True,
            )
            if verify.returncode != 0:
                print(f"[filter] removing stale partial clone {full_name}", flush=True)
                shutil.rmtree(dest, ignore_errors=True)
        elapsed = int(time.monotonic() - start_time)
        print(
            f"[filter] ({i + 1}/{len(candidates)}) {full_name} "
            f"[elapsed {elapsed // 60:02d}:{elapsed % 60:02d}, "
            f"accepted {len(accepted)}, excluded {len(excluded)}]",
            flush=True,
        )
        accepted_entry, excluded_entry = process_candidate(
            candidate, clone_dir, reports_dir, retention=args.keep_clones
        )
        if accepted_entry is not None:
            accepted.append(accepted_entry)
            print(
                f"  ACCEPTED (E1: {accepted_entry['aggregate']['files_importing_fastapi']} files)",
                flush=True,
            )
        else:
            excluded.append(excluded_entry)
            print(
                f"  EXCLUDED ({excluded_entry['reason']}: {excluded_entry.get('detail', '')})",
                flush=True,
            )
        time.sleep(0.2)
        if args.checkpoint_every > 0 and (i + 1) % args.checkpoint_every == 0:
            write_outputs(out_path, config, accepted, excluded)
            print(
                f"[filter] checkpoint @ {i + 1}: accepted {len(accepted)}, "
                f"excluded {len(excluded)}",
                flush=True,
            )

    if skipped:
        print(f"[filter] skipped {skipped} already-decided candidates", flush=True)

    if args.max_retry_rounds:
        by_name = {c["full_name"]: c for c in candidates}
        new_accepted, final_excluded = retry_clone_failures(
            excluded,
            by_name,
            clone_dir,
            reports_dir,
            args.max_retry_rounds,
            retention=args.keep_clones,
        )
        accepted.extend(new_accepted)
        excluded = final_excluded

    write_outputs(out_path, config, accepted, excluded)
    print(f"[filter] done: {len(accepted)} accepted, {len(excluded)} excluded")


if __name__ == "__main__":
    main()
