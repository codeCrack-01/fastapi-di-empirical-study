"""scripts/compile_review.py — turn annotate + repo_check chunks into a human review.

SCOPE IS THE 327-REPO STRATIFIED SAMPLE (not the full corpus). Run locally
(NOT on the remote box): copy ``remote/results`` back together with the repo
first, then::

    .venv/bin/python scripts/compile_review.py

Inputs
------
  remote/results/chunk_*.jsonl                  annotated fingerprint records (finalized chunks)
  remote/results/chunk_1*.jsonl                 repo_check two-pass records (chunk ids >= 10000)
  analysis/out/sample.json                      the 327-repo stratified sample (scope + stratum/weight)
  analysis/novelty/out/novelty_occurrences.json per-(repo, fingerprint) counts + links
  analysis/out/covariates.csv                   sample star data (covers all 327 -> no GitHub API needed)

Outputs (analysis/out/review/)
  review.tsv                       canonical table, one row per sample repo
  review.xlsx                      same table (openpyxl; skipped if unavailable)
  Q1/../Q4/<owner__repo>/review.md per-repo evidence pages (pass-1 observations,
                                    pass-2 reconciliation, labeled fingerprints)
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
RESULTS_DIR = ROOT / "remote" / "results"
SAMPLE = ROOT / "analysis" / "out" / "sample.json"
OCCURRENCES = ROOT / "analysis" / "novelty" / "out" / "novelty_occurrences.json"
COVARIATES = ROOT / "analysis" / "out" / "covariates.csv"
OUT_DIR = ROOT / "analysis" / "out" / "review"
STARS_CACHE = OUT_DIR / "stars_cache.json"

LABEL_ORDER = ("novel", "variant", "known", "false_pos", "external_di", "unknown")


def norm(owner_repo: str | None) -> str:
    """owner__repo -> owner/repo (idempotent for owner/repo)."""
    v = (owner_repo or "").strip()
    return v.replace("__", "/", 1)


def load_samples() -> dict[str, dict]:
    """full_name -> {stratum, weight} for the 327 sampled repos (scope gate)."""
    data = json.loads(SAMPLE.read_text())
    sampled = data.get("sampled") if isinstance(data, dict) else data
    out: dict[str, dict] = {}
    for e in sampled or []:
        name = norm(e.get("full_name"))
        out[name] = {"stratum": e.get("stratum"), "weight": e.get("weight")}
    if not out:
        raise SystemExit(f"[compile] sample.json has no 'sampled' entries ({SAMPLE})")
    return out


def load_chunks(results_dir: Path, start_id: int = 0) -> list[dict]:
    """Finalized chunk records with chunk_id >= start_id (annotate: 0; repo_check: 10000)."""
    recs: list[dict] = []
    for f in sorted(results_dir.glob("chunk_*.jsonl")):
        sid = int(f.stem.split("_")[1])
        if sid < start_id:
            continue
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


def load_repo_check(results_dir: Path) -> dict[str, dict]:
    """repo -> repo_check record (indexed by owner/repo)."""
    out: dict[str, dict] = {}
    for rec in load_chunks(results_dir, start_id=10000):
        out[norm(rec.get("repo"))] = rec
    return out


def load_occurrences() -> dict[tuple[str, str], dict]:
    """{(repo_key, fingerprint): occurrence-meta} with per-repo counts + example links."""
    data = json.loads(OCCURRENCES.read_text())
    if isinstance(data, dict):
        occs = data.get("occurrences") or data.get("fingerprints") or []
    else:
        occs = data or []
    out: dict[tuple[str, str], dict] = {}
    for o in occs:
        key = (norm(o.get("repo")), o.get("fingerprint"))
        cur = out.setdefault(key, {"repo": key[0], "fingerprint": key[1],
                                   "construct": o.get("construct"),
                                   "file": o.get("file"), "github_url": o.get("github_url"),
                                   "argument": o.get("argument"), "line": o.get("line"),
                                   "n": 0})
        cur["n"] += 1
        if not cur["github_url"] and o.get("github_url"):
            cur["file"], cur["github_url"], cur["line"] = o.get("file"), o.get("github_url"), o.get("line")
        if not cur["argument"] and o.get("argument"):
            cur["argument"] = o.get("argument")
    return out


def load_covariate_stars() -> dict[str, tuple[int | None, int | None]]:
    if not COVARIATES.exists():
        return {}
    stars: dict[str, tuple[int | None, int | None]] = {}
    with COVARIATES.open(encoding="utf-8") as fh:
        for row in csv.DictReader(fh):
            repo = norm(row.get("repo"))
            s1 = row.get("stars_gh") or row.get("stars")
            s2 = row.get("stars_libio")
            stars[repo] = (int(s1) if str(s1).strip().isdigit() else None,
                           int(s2) if str(s2).strip().isdigit() else None)
    return stars


def load_token() -> str | None:
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text(encoding="utf-8").splitlines():
            if line.strip().startswith("GITHUB_TOKEN="):
                return line.split("=", 1)[1].strip().strip('"').strip("'")
    return os.environ.get("GITHUB_TOKEN")


def fetch_stars(repos: set[str], token: str | None, cache: dict) -> dict:
    """Backfill star counts from the GitHub API, rate-limit aware, cached on disk."""
    for r in repos:
        if r in cache or "/" not in r:
            continue
        url = f"https://api.github.com/repos/{r}"
        req = urllib.request.Request(url, headers={
            "Accept": "application/vnd.github+json",
            "User-Agent": "research_fastapi",
            **({"Authorization": f"Bearer {token}"} if token else {}),
        })
        try:
            with urllib.request.urlopen(req, timeout=15) as resp:
                body = json.loads(resp.read())
            cache[r] = body.get("stargazers_count")
        except Exception as exc:  # noqa: BLE001 — 4xx/5xx/network all treated the same
            cache[r] = None
            if isinstance(exc, urllib.error.HTTPError) and exc.code == 403:
                time.sleep(5)  # secondary rate limit / cooldown
        time.sleep(0.1)
    return cache


def quantile(sorted_vals: list[float], q: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return sorted_vals[0]
    pos = (len(sorted_vals) - 1) * q
    lo = int(pos)
    frac = pos - lo
    return sorted_vals[lo] * (1 - frac) + sorted_vals[min(lo + 1, len(sorted_vals) - 1)] * frac


def assign_quadrants(repos: dict[str, int | None]) -> dict[str, int | None]:
    """Q4=top-25% by stars .. Q1=bottom-25%; None when a repo's stars are unknown."""
    known = sorted(v for v in repos.values() if v is not None and v >= 0)
    q1 = quantile(known, 0.25)
    q2 = quantile(known, 0.50)
    q3 = quantile(known, 0.75)
    out: dict[str, int | None] = {}
    for repo, stars in repos.items():
        if stars is None:
            out[repo] = None
        elif stars <= q1:
            out[repo] = 1
        elif stars <= q2:
            out[repo] = 2
        elif stars <= q3:
            out[repo] = 3
        else:
            out[repo] = 4
    return out


def truncate(text: Any, n: int = 400) -> str:
    s = str(text if text is not None else "").replace("\r", "")
    return s if len(s) <= n else s[: n - 3] + "..."


COLS = ["repo", "stratum", "weight", "quadrant", "stars", "star_source", "github_url",
        "n_di_nodes", "commit_sha",
        "n_novel", "n_variant", "n_known", "n_false_pos", "n_external_di",
        "n_unknown", "n_fingerprints", "n_occurrences",
        "pass1_n_obs", "pass2_n_recon", "pass2_n_overturn", "pass2_n_missed",
        "fingerprints"]


def build_tsv(rows: list[dict]) -> str:
    lines = ["\t".join(COLS)]
    for r in rows:
        lines.append("\t".join("" if (v := r.get(c)) is None else str(v) for c in COLS))
    return "\n".join(lines) + "\n"


def write_xlsx(path: Path, rows: list[dict]) -> bool:
    try:
        from openpyxl import Workbook
    except ImportError:
        return False
    from openpyxl.styles import Font, PatternFill
    from openpyxl.utils import get_column_letter

    wb = Workbook()
    ws = wb.active
    ws.title = "repos"
    cols = COLS
    header_fill = PatternFill("solid", fgColor="1F4E79")
    for c, name in enumerate(cols, 1):
        cell = ws.cell(row=1, column=c, value=name)
        cell.font = Font(bold=True, color="FFFFFF")
        cell.fill = header_fill
    for i, r in enumerate(rows, 2):
        for c, name in enumerate(cols, 1):
            v = r.get(name)
            ws.cell(row=i, column=c, value=("" if v is None else v))
        url = r.get("github_url")
        if url:
            cell = ws.cell(row=i, column=cols.index("github_url") + 1)
            cell.hyperlink = url
            cell.font = Font(color="0563C1", underline="single")
    for c in range(1, len(cols) + 1):
        ws.column_dimensions[get_column_letter(c)].width = max(12, len(cols[c - 1]) + 3)
    ws.freeze_panes = "A2"
    wb.save(path)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS_DIR))
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--net", action="store_true",
                    help="ATTENTION: not needed for the 327 sample (covariates covers 100%); "
                         "only force a GitHub API star fetch for repos missing from covariates")
    args = ap.parse_args()

    results_dir = Path(args.results)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    samples = load_samples()
    records = load_chunks(results_dir, start_id=0)
    annotate_only = [r for r in records if r.get("consensus")]
    if not annotate_only:
        raise SystemExit(f"[compile] no annotate chunk_*.jsonl under {results_dir} — nothing to compile")
    print(f"[compile] {len(annotate_only)} annotated fingerprints; {len(records)} total chunk records")

    rcs = load_repo_check(results_dir)
    print(f"[compile] {len(rcs)} repo_check records ({len(rcs)}/327 sample repos covered)")

    occ_by = load_occurrences()
    cov_stars = load_covariate_stars()

    # ---- label tallies + per-repo stats (sample scope) ----
    label_of: dict[str, dict] = {}          # fp -> {consensus, evidence, thinking, rule, executor}
    repo_stats: dict[str, dict] = {}
    for repo in samples:   # pre-seed EVERY sample repo (incl. zero-DI) with zeroed stats
        repo_stats[repo] = {"label_counts": {l: 0 for l in LABEL_ORDER},
                            "fps": {}, "occ_example": {}, "q": None, "stars": None}
    for rec in annotate_only:
        fid = rec.get("fingerprint_id")
        dec = rec.get("consensus")
        label = (dec or {}).get("label") if isinstance(dec, dict) else None
        label = str(label or "unknown").lower()
        if label not in LABEL_ORDER:
            label = "unknown"
        resp = (rec.get("responses") or [{}])[0]
        label_of[fid] = {
            "label": label,
            "evidence": resp.get("parsed", {}).get("evidence"),
            "rule": resp.get("parsed", {}).get("rule"),
            "thinking": resp.get("thinking"),
            "count": rec.get("count"),
            "executor": (rec.get("executor") or {}).get("machine"),
        }
        for r in rec.get("repos") or []:
            key = norm(r)
            if key not in repo_stats:   # out-of-sample repo from a fingerprint — ignore
                continue
            st = repo_stats[key]
            st["label_counts"][label] += 1
            st["fps"][fid] = st["fps"].get(fid, 0)

    # attach per-repo occurrence counts + example links (from occurrences file)
    for (repo, fid), om in occ_by.items():
        if repo in repo_stats:
            repo_stats[repo]["fps"][fid] = om["n"]
            repo_stats[repo]["occ_example"][fid] = om

    # ---- stars: covariates covers all 327; API only on explicit --net ----
    cache: dict = {}
    for repo in repo_stats:
        gh, libio = cov_stars.get(repo, (None, None))
        if gh is not None:
            repo_stats[repo]["stars"], repo_stats[repo]["star_source"] = gh, "covariates"
        elif libio is not None:
            repo_stats[repo]["stars"], repo_stats[repo]["star_source"] = libio, "covariates:libio"
    if args.net:
        if STARS_CACHE.exists():
            cache = json.loads(STARS_CACHE.read_text())
        missing = {r for r, s in repo_stats.items()
                   if s["stars"] is None and "/" in r and r not in cache}
        if missing:
            print(f"[compile] fetching stars for {len(missing)} repos from GitHub API ...")
            cache = fetch_stars(missing, load_token(), cache)
            for r in missing:
                if cache.get(r) is not None:
                    repo_stats[r]["stars"], repo_stats[r]["star_source"] = cache[r], "github"
            STARS_CACHE.write_text(json.dumps(cache, indent=2, sort_keys=True))
    for r, s in repo_stats.items():
        if s["stars"] is None:
            s["star_source"] = s.get("star_source") or "unset"

    starmap = {r: s["stars"] for r, s in repo_stats.items()}
    quad = assign_quadrants(starmap)

    rows: list[dict] = []
    for repo in sorted(repo_stats, key=lambda r: (repo_stats[r]["stars"] is None,
                                                  -(repo_stats[r]["stars"] or -1), r)):
        s = repo_stats[repo]
        info = samples[repo]
        q = quad[repo]
        s["q"] = q
        counts = s["label_counts"]
        nfps = len(s["fps"])
        fp_ids = sorted(s["fps"], key=lambda f: (-s["fps"][f], f))
        rc = rcs.get(repo) or {}
        p1 = (rc.get("pass1") or {}).get("parsed") or {}
        p2 = (rc.get("pass2") or {}).get("parsed") or {}
        recons = p2.get("reconciliations") or []
        rows.append({
            "repo": repo,
            "stratum": info.get("stratum"),
            "weight": info.get("weight"),
            "quadrant": f"Q{q}" if q else "Q?",
            "stars": s["stars"] if s["stars"] is not None else "",
            "star_source": s["star_source"],
            "github_url": f"https://github.com/{repo}",
            "n_di_nodes": rc.get("n_di_nodes"),
            "commit_sha": (rc.get("commit_sha") or "")[:12],
            "n_novel": counts["novel"], "n_variant": counts["variant"], "n_known": counts["known"],
            "n_false_pos": counts["false_pos"], "n_external_di": counts["external_di"],
            "n_unknown": counts["unknown"],
            "n_fingerprints": nfps,
            "n_occurrences": sum(s["fps"].values()),
            "pass1_n_obs": len(p1.get("observations") or []),
            "pass2_n_recon": len(recons),
            "pass2_n_overturn": sum(1 for x in recons if not x.get("agree")),
            "pass2_n_missed": len(p2.get("missed_by_inventory") or []),
            "fingerprints": ", ".join(fp_ids),
        })

    # ---- write ----
    tsv = out_dir / "review.tsv"
    tsv.write_text(build_tsv(rows), encoding="utf-8")
    print(f"[compile] wrote {tsv} ({len(rows)} repos)")

    xlsx = out_dir / "review.xlsx"
    if write_xlsx(xlsx, rows):
        print(f"[compile] wrote {xlsx}")
    else:
        print("[compile] openpyxl not installed — skipping xlsx (TSV is canonical)")

    # per-repo review pages
    for repo, s in repo_stats.items():
        q = s["q"]
        d = out_dir / (f"Q{q}" if q else "Q?")
        d.mkdir(parents=True, exist_ok=True)
        review_md(d / f"{repo.replace('/', '__')}" / "review.md", repo, s, label_of,
                  occ_by, s.get("star_source"), rcs.get(repo))

    n_novel_repos = sum(1 for r in rows if r["n_novel"])
    n_p2 = sum(1 for r in rows if r["pass2_n_recon"])
    print(f"[compile] done — {n_novel_repos} repos with >=1 novel fingerprint, "
          f"{n_p2} with pass-2 reconciliation evidence, {len(rows)} sample repos total")
    return 0


def review_md(path: Path, repo: str, s: dict, label_of: dict, occ_by: dict,
              star_source: str, rc: dict | None) -> None:
    """Write one repo's evidence page: fingerprint labels, then pass-1/pass-2 quotes."""
    counts = s["label_counts"]
    fp_ids = sorted(s["fps"], key=lambda f: (-s["fps"][f], f))
    lines = [f"# {repo}", ""]
    lines.append(f"- GitHub: https://github.com/{repo}")
    lines.append(f"- Stars: {s['stars'] if s['stars'] is not None else 'n/a'} ({star_source})")
    lines.append(f"- Quadrant: {('Q' + str(s['q'])) if s['q'] else 'Q?'}")
    if rc:
        lines.append(f"- Stratum: {rc.get('stratum', s.get('stratum', '—'))} · "
                     f"DI nodes: {rc.get('n_di_nodes', '—')} · "
                     f"commit: `{(rc.get('commit_sha') or '—')[:12]}`")
    lines.append(f"- Fingerprints touching this repo: {len(fp_ids)}")
    lines.append(f"- Label mix: novel={counts['novel']} variant={counts['variant']} "
                 f"known={counts['known']} false_pos={counts['false_pos']} "
                 f"external_di={counts['external_di']} unknown={counts['unknown']}")
    lines.append("")
    if rc:
        lines.append("## Pass 1 — blind observations")
        obs = (rc.get("pass1") or {}).get("parsed", {}).get("observations") or []
        if obs:
            lines.append("| # | pattern | location | why |")
            lines.append("|---|---|---|---|")
            for i, o in enumerate(obs, 1):
                loc = f"{o.get('file')}#L{o.get('line', '')}"
                lines.append(f"| {i} | `{o.get('pattern')}` | {loc} | {truncate(o.get('why'), 200)} |")
            lines.append("")
        # fingerprints shown in pass 2 (from the repo) — so reviewer can reconcile
        lines.append(f"## Pass 2 — reconcile with inventory of {repo}")
        lines.append("")
        if fp_ids:
            lines.append("_Presented fingerprints:_ `" + "`, `".join(fp_ids) + "`")
            lines.append("")
        p2 = (rc.get("pass2") or {}).get("parsed") or {}
        recons = p2.get("reconciliations") or []
        if recons:
            lines.append("| fingerprint | model label | agree? | reason | citation |")
            lines.append("|---|---|---|---|---|")
            for x in recons:
                cit = x.get("citation") or {}
                cloc = f"{cit.get('file')}#L{cit.get('line', '')}" if cit else "—"
                agree = "yes" if x.get("agree") else "**no (overturn)**"
                lines.append(f"| `{x.get('fingerprint')}` | {x.get('label')} | {agree} "
                             f"| {truncate(x.get('reason'), 200)} | {cloc} |")
            lines.append("")
        missed = p2.get("missed_by_inventory") or []
        if missed:
            lines.append(f"### Missed by inventory ({len(missed)})")
            for m in missed:
                loc = f"{m.get('file')}#L{m.get('line', '')}"
                lines.append(f"- `{m.get('pattern')}` @ {loc} — {truncate(m.get('why'), 200)}")
            lines.append("")
        t1 = (rc.get("pass1") or {}).get("thinking")
        if t1:
            lines.append(f"**pass-1 thinking:** `{truncate(t1, 700)}`")
            lines.append("")
        t2 = (rc.get("pass2") or {}).get("thinking")
        if t2:
            lines.append(f"**pass-2 thinking:** `{truncate(t2, 700)}`")
            lines.append("")
    lines.append("## Fingerprint labels")
    if fp_ids:
        lines.append("| fingerprint | construct | #occs here | label | example |")
        lines.append("|---|---|---|---|---|")
        for fid in fp_ids:
            info = label_of.get(fid, {})
            ex = s.get("occ_example", {}).get(fid)
            link = f"[{ex['file']}#L{ex.get('line', '')}]({ex['github_url']})" if ex and ex.get("github_url") else "—"
            lines.append(f"| `{fid}` | {ex.get('construct', '') if ex else ''} "
                         f"| {s['fps'][fid]} | **{info.get('label', '')}** | {link} |")
        lines.append("")
        for fid in fp_ids:
            info = label_of.get(fid, {})
            ex = s.get("occ_example", {}).get(fid)
            lines.append(f"## `{fid}` — **{info.get('label', 'unknown')}**")
            lines.append(f"> occurrences here: {s['fps'][fid]} · corpus total: {info.get('count', '—')} "
                         f"· executor: {info.get('executor', '—')}")
            if ex:
                lines.append(f"> example: [{ex.get('file')}#L{ex.get('line', '')}]({ex['github_url']})")
            if info.get("rule"):
                lines.append(f"> **rule:** {truncate(info['rule'], 300)}")
            if info.get("evidence"):
                lines.append("")
                lines.append(f"> **evidence (model):** {truncate(info['evidence'], 900)}")
            if info.get("thinking"):
                lines.append("")
                lines.append(f"**model grounds** (first 700 chars): `{truncate(info['thinking'], 700)}`")
            lines.append("")
    else:
        lines.append("_No matched fingerprints in this repo — pass-1 observations and "
                     "pass-2 confirmation carry the evidence._")
        lines.append("")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())