# Codebook: sync dependency blocking classification (Phase 2.4)

## Classes

1. **Cheap (non-blocking):** The sync dependency does only in-memory work — settings lookup, header parsing, object instantiation, pure computation, cached singleton return. No I/O, no sleep, no locks. These are candidates where converting to `async def` would help (no threadpool hop needed).

2. **Blocking I/O:** The sync dependency performs blocking I/O — database queries (sqlite3, psycopg2, pymongo), HTTP requests (requests, urllib), file I/O (open, read, write), time.sleep, or acquires locks/semaphores. These should stay sync (FastAPI runs them in a threadpool); converting to async would stall the event loop.

3. **CPU-heavy or unclear:** The sync dependency does CPU-bound work (hashing, parsing, computation) or its blocking status cannot be determined from the snippet. CPU-bound work in a thread still contends for the GIL, so it's a distinct case from blocking I/O.

## Labeling rules

- Two raters (Zain, Yahya) label independently.
- Record Cohen's kappa.
- Tie-breaker: third person (Hassan).
- Label based on the function body AND one level of callees (as visible in the snippet).
- If the snippet is insufficient to determine, label as class 3 (unclear).

## Sample

- File: `analysis/out/phase2_sync_sample_100.csv`
- Draw: 100 repos sampled from the 913 route-reachable-sync repos (seed 20261117), one sync target per repo.
- Columns: repo, target, file, snippet, manual_blocking, notes.
- Label in `manual_blocking` column: "cheap", "blocking", or "unclear".
PY
echo "done"