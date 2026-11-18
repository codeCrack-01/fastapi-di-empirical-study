import pathlib

SCHEMA_VERSION = "0.2"
EXTRACTOR_VERSION = "0.2.1"

FILE_PATTERNS = ["*.py"]

IGNORED_DIRS = {
    ".git",
    ".venv",
    "venv",
    "env",
    ".env",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    "node_modules",
    ".tox",
    "dist",
    "build",
    ".eggs",
    "egg-info",
    ".github",
    ".vscode",
    ".idea",
    ".devcontainer",
    "frontend",
    "docs",
    "docker",
    "assets",
}

IGNORED_FILES = {
    "setup.py",
    "setup.cfg",
    "pyproject.toml",
}

TEST_INDICATORS = [
    "tests/",
    "test/",
    "test_",
    "_test.py",
    "conftest.py",
]

FASTAPI_MODULES_PREFIX = "fastapi."


def is_fastapi_module(module_name: str) -> bool:
    return module_name == "fastapi" or module_name.startswith("fastapi.")


def is_local_module(module_name: str, local_modules=None) -> bool:
    if not module_name:
        return False
    local_modules = local_modules or set()
    top = module_name.split(".")[0]
    if top in local_modules:
        return True
    return module_name in local_modules

FASTAPI_DI_NAMES = {"Depends", "Security"}

FASTAPI_APP_NAMES = {"FastAPI"}
FASTAPI_ROUTER_NAMES = {"APIRouter", "APIRouter"}


def is_test_file(path: pathlib.Path) -> bool:
    relative = path.as_posix()
    name = path.name
    for indicator in TEST_INDICATORS:
        if indicator.startswith("/") and indicator.endswith("/"):
            if indicator.strip("/") in relative.split("/"):
                return True
        elif indicator.endswith(".py"):
            if name == indicator:
                return True
        elif indicator.endswith("/"):
            if relative.startswith(indicator) or f"/{indicator}" in relative:
                return True
        elif relative.startswith(indicator) or name.startswith(indicator):
            return True
    return False
