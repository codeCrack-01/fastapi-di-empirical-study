CORPUS_SCHEMA_VERSION = "0.2"

# Discovery/acceptance targets (2026-09: discovery pool targeting a 5,000-
# candidate crawl; acceptance is whatever clears E1-E3).
TARGET_CANDIDATES = 5000
TARGET_MIN_ACCEPTED = 50
SAMPLE_SEED = 42

FASTAPI_PACKAGE = "fastapi"

# Eligibility rules (census v2):
#   E1  Imports FastAPI: files_importing_fastapi >= 1 in production code.
#   E2  Origin: not a fork and not archived.
#   E3  Window: pushed_at within the last E3_MAX_AGE_MONTHS months.
#   E4  Scale: at least E4_MIN_FASTAPI_FILES distinct files import FastAPI
#       (rejects single-file/demo projects).
# E2/E3 are metadata gates evaluated before cloning; E1 is evaluated from
# the extractor report after cloning. All rules are binary existence checks
# (no magnitude thresholds).
E3_MAX_AGE_MONTHS = 60
E4_MIN_FASTAPI_FILES = 2

CLONE_DEPTH = 1
CLONE_TIMEOUT_SECONDS = 900
MAX_RETRY_ROUNDS = 3

# Clone retention policy for filter.py: "accepted" keeps only clones of
# accepted repos (rejected clones are deleted right after extraction);
# "all" keeps every processed clone; "none" deletes every clone after
# extraction (reports + manifest are sufficient for all analyses).
CLONE_RETENTION = "accepted"

DEPENDENTS_PAGE_SIZE = 30
DEPENDENTS_MAX_PAGES = 2000  # absolute safety cap; the crawl normally stops at --target
DEPENDENTS_PAGE_DELAY_SEC = 1.0

TOPIC_QUERY = "topic:fastapi"
TOPIC_SEED_TOP = 1000