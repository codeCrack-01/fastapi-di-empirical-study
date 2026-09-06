CORPUS_SCHEMA_VERSION = "0.1"

# Discovery/acceptance targets (2026-09: discovery pool targeting a 5,000-
# candidate crawl; acceptance is whatever clears E1-E6).
TARGET_CANDIDATES = 5000
TARGET_MIN_ACCEPTED = 50
SAMPLE_SEED = 42

FASTAPI_PACKAGE = "fastapi"

DEPENDENCY_FILES = [
    "pyproject.toml",
    "requirements.txt",
    "requirements/base.txt",
    "requirements/prod.txt",
    "requirements/main.txt",
    "Pipfile",
    "setup.cfg",
    "setup.py",
]

E1_RUNTIME_DEPS_REQUIRED = True

E2_MIN_PYTHON_RATIO = 0.5

E4_MAX_AGE_MONTHS = 60
E4_MIN_COMMITS = 10

E5_MIN_FASTAPI_FILES = 4
E5_MIN_FASTAPI_APPS = 1

E6_TUTORIAL_MARKERS = [
    "tutorial",
    "example",
    "demo",
    "sample",
    "boilerplate",
    "template",
    "playground",
    "starter",
    "course",
    "learn",
    "getting started",
    "walkthrough",
]

E6_README_CHECK_LIMIT = 2000

E5_SENSITIVITY_THRESHOLDS = [2, 3, 4, 5, 6, 8]

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
