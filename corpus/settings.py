CORPUS_SCHEMA_VERSION = "0.1"

TARGET_MIN_REPOS = 50
TARGET_MAX_REPOS = 150
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

DEPENDENTS_MAX_PAGES = 150
DEPENDENTS_PAGE_DELAY_SEC = 1.0

TOPIC_QUERY = "topic:fastapi"
TOPIC_SEED_TOP = 1000
