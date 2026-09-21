"""analysis/novelty/labels.py — catalog + out-of-catalog class taxonomy.

The catalog (C1-C4) is the deterministic part of the classifier: an item is
``known`` if the extractor's own node-for-construct assignment says so. The
LLM panel assigns out-of-catalog labels to *fingerprints* (grouped occurrences),
never to raw repo identifiers.

The label space mirrors the paper taxonomy:
    known      : expressible by exactly one catalog rule (C1-C4)
    variant    : semantically one of C1-C4, structurally different spelling
                 (differs only by argument shape nuance the rule does not pin)
    novel      : genuinely new DI pattern outside C1-C4/EX2/Z
    false_pos  : not DI (extractor over-captured; e.g. non-FastAPI Depends)
    external_di: DI from a non-FastAPI framework (celery, dependency-injector,
                 fastapi-injector, flask, litestar...)

Router- and app-level ``dependencies=[...]`` wiring, dependency overrides and
callable-class dependencies are **compositions of C1/C2** within the corpus
(no repository uses them without C1-C4); they are not counted as constructs.
"""

CATALOG = [
    ("C1", "Depends", "depends_total"),
    ("C2", "Security", "security_total"),
    ("C3", "Annotated dependency", "annotated_depends_total"),
    ("C4", "Generator/yield dependency", "yield_dep_total"),
]

CATALOG_IDS = tuple(cid for cid, _, _ in CATALOG)

EXTRA = [
    ("EX2", "Non-FastAPI Depends sources"),
    ("Z", "Zero core-DI repo"),
]
EXTRA_IDS = tuple(cid for cid, _ in EXTRA)

OUT_OF_CATALOG = ("known", "variant", "novel", "false_pos", "external_di")

CATALOG_RULE_SUMMARY = {
    "C1": "function/object passed to Depends(...)",
    "C2": "Security(...) with optional scopes, in a signature or app/router dependencies",
    "C3": "Annotated[Type, Depends(...)] type metadata",
    "C4": "generator (yield) function used as a dependency",
}


def out_of_catalog_label(label: str) -> bool:
    return label in OUT_OF_CATALOG


def as_prompt_catalog() -> str:
    lines = []
    for cid, name, key in CATALOG:
        lines.append(f"- {cid} ({name}): {CATALOG_RULE_SUMMARY[cid]}")
    lines.append("- EX2 (Non-FastAPI Depends sources): a Depends/Security identifier imported from a module other than fastapi")
    lines.append("- Z (Zero core-DI repo): a repository that never uses Depends/Security/Annotated at all")
    return "\n".join(lines)