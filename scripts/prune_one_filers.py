#!/usr/bin/env python3
"""scripts/prune_one_filers.py — retroactively apply E4 to the current corpus.

E4 rejects repos where only a single file imports FastAPI
(files_importing_fastapi == 1). This script re-classifies those already-accepted
entries: they are moved from corpus/manifest.json into corpus/exclusion_log.json
with reason="E4". Extractor reports in corpus/reports/ are kept untouched.

Usage:
    python scripts/prune_one_filers.py [--threshold N] [--manifest corpus/manifest.json]

A backup of the manifest is written to <manifest>.pre_prune.bak before changes.
"""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_MANIFEST = REPO_ROOT / "corpus" / "manifest.json"
DEFAULT_EXCLUSION = REPO_ROOT / "corpus" / "exclusion_log.json"
DEFAULT_SCHEMA = "0.2"


def load_json(path: Path) -> dict:
    with open(path) as f:
        return json.load(f)


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2))
    print(f"  wrote {path}")


def build_excluded_entry(entry: dict, threshold: int) -> dict:
    rules = list(entry.get("rules", []))
    if not any(r.get("rule") == "E4" for r in rules):
        rules = rules + [
            {"rule": "E4", "passed": False, "detail": "files_importing_fastapi=1"}
        ]
    return {
        "full_name": entry["full_name"],
        "decision": "excluded",
        "reason": "E4",
        "detail": f"files_importing_fastapi=1 (threshold {threshold})",
        "rules": rules,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Re-classify one-file FastAPI repos as E4 exclusions")
    parser.add_argument("--threshold", type=int, default=2,
                        help="minimum files_importing_fastapi to remain accepted (default 2)")
    parser.add_argument("--manifest", type=Path, default=DEFAULT_MANIFEST,
                        help="path to manifest.json")
    parser.add_argument("--exclusion", type=Path, default=DEFAULT_EXCLUSION,
                        help="path to exclusion_log.json")
    parser.add_argument("--no-backup", action="store_true",
                        help="skip writing a backup of the manifest")
    args = parser.parse_args()

    manifest_path = args.manifest
    exclusion_path = args.exclusion
    if not manifest_path.exists():
        print(f"error: {manifest_path} not found", file=sys.stderr)
        return 1
    if not exclusion_path.exists():
        print(f"error: {exclusion_path} not found", file=sys.stderr)
        return 1

    manifest = load_json(manifest_path)
    exclusion = load_json(exclusion_path)

    accepted = manifest.get("accepted", [])
    excluded = exclusion.get("excluded", [])

    kept: list[dict] = []
    pruned: list[dict] = []
    for entry in accepted:
        n = (entry.get("aggregate", {}).get("files_importing_fastapi") or 0)
        if n >= args.threshold:
            kept.append(entry)
        else:
            pruned.append(entry)

    if not pruned:
        print("no one-file repos found; nothing to do")
        return 0

    if not args.no_backup:
        backup = manifest_path.with_suffix(manifest_path.suffix + ".pre_prune.bak")
        shutil.copy2(manifest_path, backup)
        print(f"backup: {backup}")

    excluded += [build_excluded_entry(e, args.threshold) for e in pruned]
    kept_names = {e["full_name"] for e in kept}
    excluded = [e for e in excluded if e["full_name"] not in kept_names]

    now = datetime.now(timezone.utc).isoformat()
    new_manifest = {
        "schema_version": manifest.get("schema_version", DEFAULT_SCHEMA),
        "generated_at": now,
        "config": manifest.get("config", {}),
        "accepted": kept,
        "accepted_count": len(kept),
        "prune_e4_note": f"pruned {len(pruned)} one-file repos at threshold {args.threshold} "
                         f"on {now}",
    }
    new_exclusion = {
        "schema_version": exclusion.get("schema_version", DEFAULT_SCHEMA),
        "generated_at": now,
        "excluded": excluded,
        "excluded_count": len(excluded),
    }

    write_json(manifest_path, new_manifest)
    write_json(exclusion_path, new_exclusion)

    print(f"accepted: {len(accepted)} -> {len(kept)} (-{len(pruned)})")
    print(f"excluded: {len(excluded) - len(pruned)} existing + {len(pruned)} pruned = {len(excluded)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())