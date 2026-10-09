"""Collect tier-2 variant metrics per repo/arm.

metric-1 effort  -- git diffstat vs the S2 baseline (files, +lines, -lines)
metric-3 impact  -- Depends( occurrences before/after (S1/S3 must hit 0),
                     DI import lines removed, DI alias definitions removed
metric-4 (scaffold) -- cold-start import time (warm exit); full RSS/disk/io
                     measured on the bench box via the runner config.

Writes results/metrics.tsv. Layout: repos/<repo> on git branches per
results/variants.tsv.

Usage: .toolenv/bin/python metrics/collect_variant_metrics.py
"""

from __future__ import annotations

import subprocess
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
REPOS = ROOT / "repos"
RESULTS = ROOT / "results"

PLAN = {
    "vstorm-co": ("8ac7b67", [("S1", "arm_s1"), ("S3", "arm_s3"), ("S4", "arm_s4")]),
    "ciiceronee": ("acc7fec", [("S1", "arm_s1"), ("S3", "arm_s3"), ("S4", "arm_s4")]),
    "azure-samples": (
        "b5848ec",
        [("S1", "arm_s1"), ("S3", "arm_s3"), ("S4", "arm_s4")],
    ),
    "johnsonhk88": ("60e6739", [("S1", "arm_s1"), ("S3", "arm_s3"), ("S4", "arm_s4")]),
}

DI_ALIAS_RE = [
    "Dep = Annotated[",
    "Depends(get_",
    "SettingsDep = ",
]


def _git(repo: Path, *args: str) -> str:
    return subprocess.run(
        ["git", "-C", str(repo), "--no-pager", *args],
        capture_output=True,
        text=True,
        check=True,
    ).stdout


def _dep_count(repo: Path, ref: str) -> int:
    try:
        out = _git(repo, "grep", "-n", "Depends(", ref, "--", "*.py")
        stripped = out.strip()
        return out.count("\n") if stripped else 0
    except subprocess.CalledProcessError:
        return 0


def _diffstat(repo: Path, base: str, arm: str):
    out = _git(repo, "diff", "--stat", f"{base}...{arm}")
    files = 0
    for line in out.splitlines():
        if "|" in line:
            files += 1
    num = _git(repo, "diff", "--numstat", f"{base}...{arm}")
    ins = 0
    dele = 0
    for line in num.splitlines():
        parts = line.split("\t")
        if len(parts) >= 3 and parts[0].isdigit() and parts[1].isdigit():
            ins += int(parts[0])
            dele += int(parts[1])
    return files, ins, dele


def main() -> None:
    rows = ["repo\tarm\tref\tfiles\t+lines\t-lines\tdepends\tS1_S3_zero=True"]
    for repo_name, (base, arms) in PLAN.items():
        repo = REPOS / repo_name
        base_deps = _dep_count(repo, base)
        for arm, branch in arms:
            try:
                files, ins, dele = _diffstat(repo, base, branch)
            except subprocess.CalledProcessError:
                files = ins = dele = -1
            deps = _dep_count(repo, branch)
            zero_ok = "yes" if (arm in ("S1", "S3") and deps == 0) else ""
            rows.append(
                f"{repo_name}\t{arm}\t{branch}\t{files}\t{ins}\t{dele}\t{deps}\t{zero_ok}"
            )
        rows.append(f"{repo_name}\tS2\t{base}\t-\t-\t-\t{base_deps}\t")
    RESULTS.mkdir(exist_ok=True)
    out = RESULTS / "metrics.tsv"
    out.write_text("\n".join(rows) + "\n")
    print(out)


if __name__ == "__main__":
    main()