"""scripts/compile_review.py — turn annotate chunks into a human-reviewable summary.

Run locally (NOT on the remote box): copy ``remote/results`` back together with
the repo first, then::

    .venv/bin/python scripts/compile_review.py

Inputs
------
  remote/results/chunk_*.jsonl      annotated fingerprint records (only finalized chunks)
  analysis/novelty/out/novelty_occurrences.json   per-(repo, fingerprint) counts + links
  analysis/out/covariates.csv       sample star data (owner/repo, stars_gh, stars_libio)
  .env                              GITHUB_TOKEN for star backfill (optional)
  analysis/novelty/out/novelty_leaderboard.csv    anchor sanity score (optional)

Outputs (analysis/out/review/)
  review.tsv                       canonical table, one row per repo
  review.xlsx                      same table (openpyxl; skipped if unavailable)
  Q1/../Q4/<owner__repo>/review.md per-repo evidence pages (Q?, if stars unknown)
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
OCCURRENCES = ROOT / "analysis" / "novelty" / "out" / "novelty_occurrences.json"
COVARIATES = ROOT / "analysis" / "out" / "covariates.csv"
OUT_DIR = ROOT / "analysis" / "out" / "review"
STARS_CACHE = OUT_DIR / "stars_cache.json"

LABEL_ORDER = ("novel", "variant", "known", "false_pos", "external_di", "unknown")


def norm(owner_repo: str | None) -> str:
    """owner__repo -> owner/repo (idempotent for owner/repo)."""
    v = (owner_repo or "").strip()
    return v.replace("__", "/", 1)


def load_chunks(results_dir: Path) -> list[dict]:
    recs: list[dict] = []
    for f in sorted(results_dir.glob("chunk_*.jsonl")):
        for line in f.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line:
                recs.append(json.loads(line))
    return recs


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
        elif stars >= q3:
            out[repo] = 4
        elif stars >= q2:
            out[repo] = 3
        elif stars >= q1:
            out[repo] = 2
        else:
            out[repo] = 1
    return out


def truncate(text: Any, n: int = 400) -> str:
    s = str(text if text is not None else "").replace("\r", "")
    return s if len(s) <= n else s[: n - 3] + "..."


def build_tsv(rows: list[dict]) -> str:
    cols = ["repo", "quadrant", "stars", "star_source", "github_url",
            "n_novel", "n_variant", "n_known", "n_false_pos", "n_external_di",
            "n_unknown", "n_fingerprints", "n_occurrences", "fingerprints"]
    lines = ["\t".join(cols)]
    for r in rows:
        lines.append("\t".join("" if (v := r.get(c)) is None else str(v) for c in cols))
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
    cols = ["repo", "quadrant", "stars", "star_source", "github_url",
            "n_novel", "n_variant", "n_known", "n_false_pos", "n_external_di",
            "n_unknown", "n_fingerprints", "n_occurrences", "fingerprints"]
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
        ws.column_dimensions[get_column_letter(c)].width = max(14, len(cols[c - 1]) + 4)
    ws.freeze_panes = "A2"
    wb.save(path)
    return True


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--results", default=str(RESULTS_DIR))
    ap.add_argument("--out", default=str(OUT_DIR))
    ap.add_argument("--no-net", action="store_true", help="never hit the GitHub API (stars: covariates only)")
    args = ap.parse_args()

    results_dir = Path(args.results)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    records = load_chunks(results_dir)
    if not records:
        raise SystemExit(f"[compile] no chunk_*.jsonl under {results_dir} — nothing to compile")
    print(f"[compile] {len(records)} annotated fingerprints")

    occ_by = load_occurrences()
    cov_stars = load_covariate_stars()

    # ---- label tallies + per-repo stats ----
    label_of: dict[str, dict] = {}          # fp -> {consensus, evidence, thinking, rule, executor}
    repo_stats: dict[str, dict] = {}
    for rec in records:
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
            st = repo_stats.setdefault(key, {"label_counts": {l: 0 for l in LABEL_ORDER},
                                             "fps": {}, "occ_example": {}, "q": None, "stars": None})
            st["label_counts"][label] += 1
            st["fps"][fid] = st["fps"].get(fid, 0)

    # attach per-repo occurrence counts + example links (from occurrences file)
    for (repo, fid), om in occ_by.items():
        if repo in repo_stats:
            repo_stats[repo]["fps"][fid] = om["n"]
            repo_stats[repo]["occ_example"][fid] = om

    # ---- stars ----
    cache: dict = {}
    if STARS_CACHE.exists():
        cache = json.loads(STARS_CACHE.read_text())
    for repo in repo_stats:
        gh, libio = cov_stars.get(repo, (None, None))
        if gh is not None:
            repo_stats[repo]["stars"], repo_stats[repo]["star_source"] = gh, "covariates"
        elif libio is not None:
            repo_stats[repo]["stars"], repo_stats[repo]["star_source"] = libio, "covariates:libio"
    if not args.no_net:
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
        q = quad[repo]
        s["q"] = q
        counts = s["label_counts"]
        nfps = len(s["fps"])
        fp_ids = sorted(s["fps"], key=lambda f: (-s["fps"][f], f))
        rows.append({
            "repo": repo,
            "quadrant": f"Q{q}" if q else "Q?",
            "stars": s["stars"] if s["stars"] is not None else "",
            "star_source": s["star_source"],
            "github_url": f"https://github.com/{repo}",
            "n_novel": counts["novel"], "n_variant": counts["variant"], "n_known": counts["known"],
            "n_false_pos": counts["false_pos"], "n_external_di": counts["external_di"],
            "n_unknown": counts["unknown"],
            "n_fingerprints": nfps,
            "n_occurrences": sum(s["fps"].values()),
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
                  occ_by, s.get("star_source"))

    n_novel_repos = sum(1 for r in rows if r["n_novel"])
    print(f"[compile] done — {n_novel_repos} repos with >=1 novel fingerprint, {len(rows)} total")
    return 0


def review_md(path: Path, repo: str, s: dict, label_of: dict, occ_by: dict, star_source: str) -> None:
    """Write one repo's evidence page: every labeled fingerprint touching it, with links + thinking."""
    counts = s["label_counts"]
    fp_ids = sorted(s["fps"], key=lambda f: (-s["fps"][f], f))
    lines = [f"# {repo}", ""]
    lines.append(f"- GitHub: https://github.com/{repo}")
    lines.append(f"- Stars: {s['stars'] if s['stars'] is not None else 'n/a'} ({star_source})")
    lines.append(f"- Quadrant: {('Q' + str(s['q'])) if s['q'] else 'Q?'}")
    lines.append(f"- Fingerprints touching this repo: {len(fp_ids)}")
    lines.append(f"- Label mix: novel={counts['novel']} variant={counts['variant']} "
                 f"known={counts['known']} false_pos={counts['false_pos']} "
                 f"external_di={counts['external_di']} unknown={counts['unknown']}")
    lines.append("")
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
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())