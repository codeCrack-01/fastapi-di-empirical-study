"""analysis/swappable/catalog.py — offline discovery + 3-tier screening of swappable DI patterns.

Discovery (no GPU): for each accepted repo, each DI *provider* (the callable given
to Depends/Security/Annotated, or a yield-function) is collected from the stored
extractor reports with a first-class ``provider`` field (the flattened
``novelty_occurrences.json`` loses it for C3 because ``argument`` is null there).
A **swap candidate** is a provider expressed via >= 2 distinct constructs
(C1 Depends / C2 Security / C3 Annotated / C4 yield-definition) in the same repo.

Screening (no blind capture): every candidate is put in exactly one *type*
by deterministic rules over the annotate consensus labels and structural reuse:

    Swappable       provider is a plain callable reused in >= 2 accepted repos and
                    >= 1 involved fingerprint labels the construct known/variant
                    with a plain argument shape -> the interchangeable arm set
    Context-bound   any involved fingerprint means a single-repo provider, or a
                    non-plain argument shape, or a variant spelling, or a pass-2
                    non-native mechanism -> reported, not generic
    Over-capture    every involved fingerprint labeled false_pos/unknown, i.e. the
                    extractor/panel captured something not reliably DI -> flagged
                    for reviewer adjudication, not auto-dismissed

Non-native/candidate mechanisms found by pass-2 (container @inject, thread-local,
lifespan DI, app.state, dependency factories) are folded in as Context-bound entries.

Outputs (under analysis/swappable/out/):
    catalog.json                full candidate list with per-entry screen_notes
    patterns_swappable.tsv      arm set (repo | provider | constructs
                               | fingerprints | labels | type_notes | stratum | weight)
    patterns_context_bound.tsv  context-bound set
    patterns_over_capture.tsv   over-capture set
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

REPORTS_DIR = Path(__file__).resolve().parents[2] / "corpus" / "reports"
MANIFEST = Path(__file__).resolve().parents[2] / "corpus" / "manifest.json"
SAMPLE = Path(__file__).resolve().parents[1] / "out" / "sample.json"
ANNOTATE_CHUNKS = Path(__file__).resolve().parents[2] / "pod_results" / "remote" / "results"
REPO_CHECK = Path(__file__).resolve().parents[2] / "pod_results" / "remote" / "results"
OUT_DIR = Path(__file__).resolve().parent / "out"

C = {
    "C1": "Depends",
    "C2": "Security",
    "C3": "Annotated",
    "C4": "yield-def",
}

IDENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*$")
TITLE = re.compile(r"^[A-Z][A-Za-z0-9_]*$")


def arg_shape(argument: str) -> str:
    a = (argument or "").strip()
    if a in ("<empty>", ""):
        return "EMPTY"
    if a == "...":
        return "ELLIPSIS"
    if "(" in a:
        return "CALL"
    if "." in a:
        return "DOTTED"
    if IDENT.match(a):
        return "CLASS" if TITLE.match(a) else "BARE"
    return "OTHER"


def _shapes_c4(node: dict) -> str:
    return "C4|USED" if node.get("used_as_dependency") else "C4|DEF"


def provider_and_fingerprint(node: dict, construct: str) -> tuple[str, str]:
    if construct == "C1":
        arg = node.get("argument")
        provider = arg or node.get("name") or ""
        shape = arg_shape(arg)
        sig = "SIG" if node.get("in_signature") else "PARAM"
        return provider, f"C1|{shape}|{sig}"
    if construct == "C2":
        arg = node.get("argument")
        provider = arg or node.get("name") or ""
        shape = arg_shape(arg)
        scopes = ",".join(sorted(s for s in (node.get("scopes") or []) if s))
        return provider, f"C2|{shape}|{scopes or 'ascopes'}"
    if construct == "C3":
        provider = node.get("depends_argument") or node.get("argument") or ""
        ann = arg_shape(node.get("annotated_type"))
        dep = arg_shape(node.get("depends_argument"))
        return provider, f"C3|{ann}|{dep}"
    if construct == "C4":
        provider = node.get("name") or ""
        return provider, _shapes_c4(node)
    return "", ""


def collect_provider_occurrences(reports_dir: Path, accepted: set[str]) -> list[dict]:
    out: list[dict] = []
    for path in sorted(reports_dir.glob("*.json")):
        stem = path.stem.replace("__", "/")
        if stem not in accepted:
            continue
        try:
            report = json.loads(path.read_text())
        except (OSError, json.JSONDecodeError):
            continue
        repo = report.get("repo") if isinstance(report.get("repo"), dict) else {}
        commit_sha = repo.get("commit_sha")
        for fd in report.get("file_details", []):
            rel = (fd.get("path") or "").replace("\\", "/")
            marker = f"corpus/{report.get('repo', {}).get('name') or stem}/"
            idx = rel.find(marker)
            rel = rel[idx + len(marker):] if idx >= 0 else rel
            for cid, key in (("C1", "depends_calls"), ("C2", "security_calls"),
                             ("C3", "annotated_depends"), ("C4", "yield_functions")):
                for n in fd.get(key, []):
                    provider, fp = provider_and_fingerprint(n, cid)
                    if not provider:
                        continue
                    url = None
                    if commit_sha and rel:
                        base = f"https://github.com/{stem}/blob/{commit_sha}/{rel}"
                        url = f"{base}#L{n.get('line')}" if n.get("line") else base
                    out.append({
                        "repo": stem,
                        "construct": cid,
                        "fingerprint": fp,
                        "provider": provider,
                        "file": rel,
                        "line": n.get("line"),
                        "context_function": n.get("context_function") or n.get("name"),
                        "github_url": url,
                    })
    return out


def load_label_map(results_dir: Path) -> dict[str, str]:
    m: dict[str, str] = {}
    if not results_dir.exists():
        return m
    for f in sorted(results_dir.glob("chunk_000*.jsonl")):
        for line in f.read_text().splitlines():
            d = json.loads(line)
            m[d["fingerprint_id"]] = d["consensus"]["label"]
    return m


def load_sample_weights(path: Path) -> dict[str, dict]:
    if not path.exists():
        return {}
    d = json.loads(path.read_text())
    w: dict[str, dict] = {}
    for r in d.get("sampled") or d.get("repos") or d.get("sample", []):
        name = r.get("full_name") or r.get("repo") or r.get("name")
        if name:
            w[str(name)] = {"stratum": r.get("stratum"), "weight": r.get("weight")}
    return w


def load_missed_mechanisms(results_dir: Path) -> list[dict]:
    """Load pass-2 missed_by_inventory items describing NON-catalog mechanisms only.

    The pattern strings are free text; the mechanism keywords below select the
    genuinely non-native candidates (container DI, thread-local, lifespan,
    app.state, dependency factories, manual construction) while excluding the
    ~203/+ items that merely restate a C1-C4 occurrence the inventory missed.
    """
    kw = ("dishka", "@provide", "@inject", "container", "provide[", "thread-local",
          "app.state", "closure", "factory", "lifespan", "router-level",
          "dependencies=[", "middleware", "app.dependency_overrides", "override",
          "fixture", "mock", "manual", "state injection", "state-based",
          "state via", "state sharing", "monkeypatch", "constructor",
          "custom dependency callable", "higher-order")
    out: list[dict] = []
    for f in sorted(results_dir.glob("chunk_1*.jsonl")):
        for line in f.read_text().splitlines():
            d = json.loads(line)
            for m in (d.get("pass2", {}).get("parsed", {}).get("missed_by_inventory") or []):
                pat = (m.get("pattern") or "")
                if not any(k in pat.lower() for k in kw):
                    continue
                out.append({
                    "repo": d["repo"],
                    "pattern": pat,
                    "file": m.get("file"),
                    "line": m.get("line"),
                })
    return out


def main() -> None:
    accepted = {str(a["full_name"]) for a in json.loads(MANIFEST.read_text())["accepted"]}
    labels = load_label_map(ANNOTATE_CHUNKS)
    weights = load_sample_weights(SAMPLE)
    missed = load_missed_mechanisms(REPO_CHECK)

    occ = collect_provider_occurrences(REPORTS_DIR, accepted)

    provider_reuse: dict[str, set[str]] = defaultdict(set)
    for o in occ:
        provider_reuse[o["provider"]].add(o["repo"])

    by_key: dict[tuple, dict] = {}
    for o in occ:
        key = (o["repo"], o["provider"])
        e = by_key.setdefault(key, {
            "repo": o["repo"], "provider": o["provider"],
            "constructs": set(), "fingerprints": set(),
            "shapes": set(), "occurrences": 0, "examples": [],
        })
        e["constructs"].add(o["construct"])
        e["fingerprints"].add(o["fingerprint"])
        e["shapes"].add(o["fingerprint"])
        e["occurrences"] += 1
        if len(e["examples"]) < 3:
            e["examples"].append({k: o[k] for k in ("file", "line", "context_function", "github_url")})

    candidates = [e for e in by_key.values() if len(e["constructs"]) >= 2]
    print(f"[catalog] accepted={len(accepted)} occurrences={len(occ)} "
          f"providers={len(by_key)} swap_candidates={len(candidates)}")

    def screen(e: dict) -> tuple[str, list[str]]:
        notes: list[str] = []
        fps = sorted(e["fingerprints"])
        lbls = [labels.get(f, "unknown") for f in fps]
        has_valid = any(l in ("known", "variant") for l in lbls)
        if not has_valid:
            return "OVER_CAPTURE", ["no valid construct; all false_pos/unknown: " + ",".join(fps)]
        n_repos = len(provider_reuse.get(e["provider"], {e["repo"]}))
        shapes = e["shapes"]
        over = [f for f, l in zip(fps, lbls) if l == "false_pos"]
        if over:
            notes.append("has false_pos over-capture shapes: " + ",".join(over))
        bad = []
        for s in shapes:
            if s.startswith("C3"):
                if len(s.split("|")) >= 3 and s.split("|")[2] not in ("BARE", "DOTTED", "CLASS"):
                    bad.append(s)
            elif s.startswith("C4"):
                continue
            elif s.split("|")[1] not in ("BARE", "DOTTED", "CLASS"):
                bad.append(s)
        if n_repos < 2:
            notes.append("single-repo provider")
        if bad:
            notes.append("non-plain argument shape: " + ",".join(sorted(bad)))
        if "single-repo provider" in notes or any(b.startswith("non-plain") for b in notes):
            return "CONTEXT_BOUND", notes if notes else ["context-bound"]
        return "SWAPPABLE", notes if notes else ["generic"]

    swappable: list[dict] = []
    context_bound: list[dict] = []
    over_capture: list[dict] = []
    for e in sorted(candidates, key=lambda x: (-len(x["constructs"]), x["repo"])):
        e["constructs"] = sorted(e["constructs"])
        e["fingerprints"] = sorted(e["fingerprints"])
        e["shapes"] = sorted(e["shapes"])
        e["n_repos_provider"] = len(provider_reuse[e["provider"]])
        e["labels"] = sorted({labels.get(f, "unknown") for f in e["fingerprints"]})
        sw = weights.get(e["repo"], {})
        e["stratum"] = sw.get("stratum")
        e["weight"] = sw.get("weight")
        tier, notes = screen(e)
        lbl_map = {f: labels.get(f, "unknown") for f in e["fingerprints"]}
        e["screen_notes"] = notes
        e["fp_labels"] = lbl_map
        e["valid_constructs"] = sorted({
            f.split("|")[0] for f, l in lbl_map.items() if l in ("known", "variant")
        })
        e.pop("shapes", None)
        {"SWAPPABLE": swappable, "CONTEXT_BOUND": context_bound,
         "OVER_CAPTURE": over_capture}[tier].append(e)

    for e in missed:
        context_bound.append({
            "repo": e["repo"], "provider": None, "constructs": ["mechanism"],
            "fingerprints": [], "labels": ["missed_by_inventory"],
            "occurrences": 1,
            "examples": [{"file": e["file"], "line": e["line"], "pattern": e["pattern"]}],
            "n_repos_provider": 1, "stratum": weights.get(e["repo"], {}).get("stratum"),
            "weight": weights.get(e["repo"], {}).get("weight"),
            "fp_labels": {}, "valid_constructs": [],
            "screen_notes": ["pass-2 candidate non-native mechanism (unverified)"],
        })

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    record = {
        "schema_version": "1.0",
        "generated_utc": __import__("datetime").datetime.now(timezone_utc()).isoformat(),
        "scope": {"accepted_repos": len(accepted), "occurrences": len(occ),
                  "swap_candidates_before_screen": len(candidates),
                  "pass2_mechanisms_added": len(missed)},
        "tiers": {"swappable": len(swappable), "context_bound": len(context_bound),
                  "over_capture": len(over_capture)},
        "reconcile": {"candidates": len(candidates), "mechanisms": len(missed),
                      "sum_swappable_context_overcapture": len(swappable) + len(context_bound) + len(over_capture)},
        "label_map": labels,
        "swappable": swappable, "context_bound": context_bound, "over_capture": over_capture,
    }
    (OUT_DIR / "catalog.json").write_text(json.dumps(record, indent=2))

    def dump_tsv(name: str, rows: list[dict]) -> None:
        with (OUT_DIR / name).open("w") as fh:
            fh.write("repo\tprovider\tconstructs\tvalid_constructs\tfingerprints\tfp_labels\ttype_notes\tn_repos_provider\tstratum\tweight\texample_url\n")
            for r in rows:
                ex = r["examples"][0] if r["examples"] else {}
                url = ex.get("github_url") or (ex.get("file") and f"{ex.get('file')}:{ex.get('line')}") or ""
                lbl = ";".join(f"{k}={v}" for k, v in sorted(r["fp_labels"].items()))
                fh.write("\t".join([
                    r["repo"], r["provider"] or "", ",".join(r["constructs"]),
                    ",".join(r.get("valid_constructs", [])),
                    ",".join(r["fingerprints"]), lbl,
                    "; ".join(r["screen_notes"]), str(r["n_repos_provider"]),
                    r["stratum"] or "", str(r["weight"] or ""), url,
                ]) + "\n")

    dump_tsv("patterns_swappable.tsv", swappable)
    dump_tsv("patterns_context_bound.tsv", context_bound)
    dump_tsv("patterns_over_capture.tsv", over_capture)

    print(f"[catalog] SWAPPABLE={len(swappable)} CONTEXT_BOUND={len(context_bound)} "
          f"OVER_CAPTURE={len(over_capture)}")
    for row in swappable[:15]:
        print(f"  SW  {row['repo']:45} {row['provider']:24} {','.join(row['constructs'])}  notes={row['screen_notes']}")


def timezone_utc():
    from datetime import timezone
    return timezone.utc


if __name__ == "__main__":
    main()