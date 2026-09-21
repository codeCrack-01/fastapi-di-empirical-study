"""analysis/novelty/anchors.py — constructed ground-truth items for rater selection.

Ground truth is CONSTRUCTED, never human-annotated. Each anchor is a minimal
FastAPI-style snippet whose expected label is known BECAUSE we wrote the rule
violation it encodes. We additionally run the snippet through the *real*
extractor (scripts/extractor via import) so the ``report`` given to raters is
what the pipeline actually produces — anchors therefore test the raters on the
same representation they will see at annotation time.

Anchor template matrix (each rule C1-C4 + EX2/Z; plus one per out-of-catalog
label for discrimination):

    positive  : a canonical, rule-satisfying example
    near-miss : the same rule bent (alias import, dotted path, title-case
                class, scopes usage, nested Depends, generator NOT used as
                dependency, ...)
    negative-ish: what the extractor can misread -> raters must not over-tag
    unrelated : FastAPI import with zero DI (Z) or non-DI fastapi usage

Labels use the taxonomy in labels.py: catalog (C1..C4) for rule-satisfying
items; out_of_catalog for everything else (known/variant/false_pos/external_di).

No network, no model, no humans. Deterministic (seeded) so select_panel and
reverify run on byte-identical anchor sets.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Callable

ROOT = Path(__file__).resolve().parents[2]
EXTRACTOR_DIR = ROOT / "extractor"

sys.path.insert(0, str(EXTRACTOR_DIR))

from extract import analyze_file  # noqa: E402
from models import FileReport  # noqa: E402


# --------------------------------------------------------------------------
# Snippet templates laid out so each is minimally annotated and self-consistent.
# --------------------------------------------------------------------------

def _base_fastapi() -> str:
    return (
        "from fastapi import FastAPI, Depends, Security\n"
        "from fastapi.security import HTTPBearer\n"
        "from typing import Annotated\n"
        "\n"
    )


def snippet_c1_bare(use_dotted: bool) -> str:
    body = "from fastapi import FastAPI, Depends\n\n\ndef get_db():\n    return \"db\"\n\n"
    arg = "get_db"
    if use_dotted:
        body += "import core\ncore.get_db = get_db\n"
        arg = "core.get_db"
    return body + f"async def read_item(item: str = Depends({arg})):\n    return item\n"


def snippet_c1_class() -> str:
    return (
        "from fastapi import FastAPI, Depends\n\n\n"
        "class Settings:\n    def __init__(self):\n        self.app_name = \"x\"\n\n\n"
        "async def read_item(settings: Settings = Depends(Settings)):\n    return settings.app_name\n"
    )


def snippet_c1_empty() -> str:
    return "from fastapi import FastAPI, Depends\n\nasync def read_item(x: str = Depends()):\n    return x\n"


def snippet_c1_call_inline() -> str:
    return (
        "from fastapi import FastAPI, Depends\n\n\n"
        "def make_dep():\n    return \"d\"\n\n\n"
        "async def read_item(x: str = Depends(make_dep())):\n    return x\n"
    )


def snippet_c2_scopes() -> str:
    return (
        "from fastapi import FastAPI, Security\nfrom fastapi.security import HTTPBearer\n\n"
        "bearer = HTTPBearer()\n\n"
        "def require_admin(credentials = Security(bearer, scopes=[\"admin\"])):\n"
        "    return credentials\n\n"
        "async def admin(cheese = Security(require_admin)):\n"
        "    return cheese\n"
    )


def snippet_c3_annotated() -> str:
    return (
        "from fastapi import FastAPI, Depends\nfrom typing import Annotated\n\n\n"
        "def get_current_user():\n    return {\"id\": 1}\n\n\n"
        "# C3: Annotated metadata form\n"
        "async def me(current: Annotated[dict, Depends(get_current_user)]):\n"
        "    return current\n"
    )


def snippet_c4_generator_used() -> str:
    return (
        "from fastapi import FastAPI, Depends\n\n\n"
        "def get_session():\n    yield \"session\"\n\n\n"
        "async def read(db = Depends(get_session)):\n    return db\n"
    )


def snippet_c4_generator_defined_not_used() -> str:
    return (
        "from fastapi import FastAPI\n\n\n"
        "def get_session():\n    yield \"session\"\n\n\n"
        "async def read():\n    return \"nodb\"\n"
    )


def snippet_ex2_non_fastapi_depends() -> str:
    # A Depends imported from somewhere other than fastapi must NOT be counted.
    return (
        "from fastapi import FastAPI, Depends\n"
        "from redis import Depends as RedisDepends\n\n"
        "def get_redis():\n    return \"redis\"\n\n\n"
        "async def read(r = RedisDepends(get_redis)):\n    return r\n"
    )


def snippet_z_zero_di() -> str:
    return (
        "from fastapi import FastAPI\n\napp = FastAPI()\n\n"
        "@app.get(\"/\")\nasync def root():\n    return {\"hello\": \"world\"}\n"
    )


def snippet_external_di_fastapi_injector() -> str:
    return (
        "from fastapi import FastAPI\n"
        "from fastapi_injector import Injector, attach_injector, Injected\n\n"
        "app = FastAPI()\n"
        "injector = Injector()\n"
        "attach_injector(app, injector)\n\n"
        "async def read(db: Injector = Injected(DB)):\n    return db\n"
    )


ANCHOR_TEMPLATES: list[dict] = [
    {"label": "C1", "name": "c1_bare", "make": lambda: snippet_c1_bare(False), "category": "positive"},
    {"label": "C1", "name": "c1_dotted", "make": lambda: snippet_c1_bare(True), "category": "positive"},
    {"label": "C1", "name": "c1_class", "make": snippet_c1_class, "category": "near-miss"},
    {"label": "C1", "name": "c1_empty", "make": snippet_c1_empty, "category": "near-miss"},
    {"label": "C1", "name": "c1_call_inline", "make": snippet_c1_call_inline, "category": "near-miss"},
    {"label": "C2", "name": "c2_scopes", "make": snippet_c2_scopes, "category": "positive"},
    {"label": "C3", "name": "c3_annotated", "make": snippet_c3_annotated, "category": "positive"},
    {"label": "C4", "name": "c4_generator_used", "make": snippet_c4_generator_used, "category": "positive"},
    {"label": "C4", "name": "c4_generator_unused", "make": snippet_c4_generator_defined_not_used, "category": "negative-ish"},
    {"label": "EX2", "name": "ex2_non_fastapi_depends", "make": snippet_ex2_non_fastapi_depends, "category": "positive"},
    {"label": "Z", "name": "z_zero_di", "make": snippet_z_zero_di, "category": "positive"},
    {"label": "external_di", "name": "external_di_injector", "make": snippet_external_di_fastapi_injector, "category": "positive"},
]


def _run_extractor(source: str) -> FileReport:
    """Run the real extractor against an in-memory snippet."""
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".py", delete=False, encoding="utf-8") as fh:
        fh.write(source)
        tmp_path = fh.name
    try:
        report = analyze_file(Path(tmp_path))
    finally:
        Path(tmp_path).unlink(missing_ok=True)
    if report is None:
        raise RuntimeError("extractor returned None (syntax error in anchor?)")
    used_names = {d.argument for d in report.depends_calls}
    for yf in report.yield_functions:
        yf.used_as_dependency = yf.name in used_names
    return report


def _extractor_summary(report: FileReport) -> dict:
    return {
        "imports_fastapi": report.imports_fastapi,
        "depends_calls": len(report.depends_calls),
        "security_calls": len(report.security_calls),
        "annotated_depends": len(report.annotated_depends),
        "yield_functions": len(report.yield_functions),
        "non_fastapi_depends_sources": dict(report.non_fastapi_depends_sources),
        "fastapi_app_count": report.fastapi_app_count,
    }


def build_anchors(out_dir: Path | None = None) -> list[dict]:
    """Materialize all anchor templates and run them through the extractor.

    Returns deterministic, sorted list of anchors:
        {id, label, category, source, extractor_summary}
    """
    anchors: list[dict] = []
    for t in ANCHOR_TEMPLATES:
        source = t["make"]()
        report = _run_extractor(source)
        anchor_id = f"{t['label']}::{t['name']}"
        anchors.append({
            "id": anchor_id,
            "label": t["label"],
            "category": t["category"],
            "source": source,
            "extractor_summary": _extractor_summary(report),
            "extractor_top": _top_extractor_node(report, t["label"]),
        })
    anchors.sort(key=lambda a: a["id"])
    if out_dir is not None:
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / "novelty_anchors.json").write_text(json.dumps(anchors, indent=2))
    return anchors


def _top_extractor_node(report: FileReport, label: str) -> str | None:
    """The fingerprint string of the primary matching node, for prompt display.

    For Z there is no node; for EX2 the non-fastapi source is recorded. For the
    catalog rules we take the first node of the matching list.
    """
    mapping = {
        "C1": report.depends_calls,
        "C2": report.security_calls,
        "C3": report.annotated_depends,
        "C4": report.yield_functions,
    }
    if label in mapping and mapping[label]:
        node = mapping[label][0]
        from fingerprints import fingerprint_for
        return fingerprint_for(node.model_dump(), label)
    if label == "EX2":
        srcs = dict(report.non_fastapi_depends_sources)
        return f"EX2|{','.join(sorted(srcs.values()))}" if srcs else None
    return None


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser(description="Build constructed anchors")
    ap.add_argument("--out", default=str(Path(__file__).resolve().parent / "out"))
    args = ap.parse_args()
    anchors = build_anchors(Path(args.out))
    print(f"[anchors] {len(anchors)} anchors")
    for a in anchors:
        print(f"  {a['id']:<38} label={a['label']:<12} {a['category']}")
        print(f"      extractor: {json.dumps(a['extractor_summary'])}")