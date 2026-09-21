"""Tests for labels.py + prompt.py rendering."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "analysis" / "novelty"))

from labels import as_prompt_catalog  # noqa: E402
from prompt import render_system, render_user, RUBRIC_BLOCK, parse_response  # noqa: E402


def test_catalog_contains_all_categories():
    txt = as_prompt_catalog()
    for c in ["C1", "C2", "C3", "C4", "EX2", "Z"]:
        assert c in txt


def test_prompt_is_byte_stable():
    a = render_system()
    b = render_system()
    assert a == b
    assert "C1" in a and "C4" in a  # rubric actually rendered in


def test_rubric_block_has_output_labels():
    assert "external_di" in RUBRIC_BLOCK
    assert "false_pos" in RUBRIC_BLOCK
    assert "novel" in RUBRIC_BLOCK


def test_render_user_includes_fingerprint_and_examples():
    u = render_user("C1|BARE|SIG", [{"repo": "x", "line": 1, "argument": "db", "context_function": "f"}])
    assert "C1|BARE|SIG" in u
    assert "x" in u


def test_parse_response_json():
    r = parse_response('{"tool_calls": [], "label": "novel", "rule": "C1", "evidence": "genuine weave"}')
    assert r["label"] == "novel"


def test_parse_response_chatty():
    r = parse_response('Let me analyze.\n{"label": "known", "rule": "C1"}\nDone.')
    assert r["label"] == "known"
    assert r["rule"] == "C1"


def test_parse_response_bare_label():
    assert parse_response("unknown but novel")["label"] == "novel"