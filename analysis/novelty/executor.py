"""analysis/novelty/executor.py — executor fingerprint / pinning records.

A rater runs on an EXECUTOR (a machine + serving stack). Reproducibility
requires the executor to be pinned alongside the model digest and sampling
config; this module records the tuple and detects drift between entries so the
definitive annotation and its selection-time calibration can be compared
(anchor-reverification gate).
"""
from __future__ import annotations

import json
import os
import platform
import subprocess
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Optional

OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://localhost:11434")


@dataclass
class ExecutorProfile:
    host: str = OLLAMA_HOST
    machine: str = ""
    python: str = ""
    ollama_version: str = ""
    nproc: int = 0
    model_specs: dict[str, Optional[str]] = field(default_factory=dict)
    backend: str = "ollama"

    @classmethod
    def capture(cls, models: list[str] | None = None) -> "ExecutorProfile":
        profile = cls()
        profile.host = OLLAMA_HOST
        profile.machine = platform.machine()
        profile.python = platform.python_version()
        try:
            _n = os.cpu_count()
            profile.nproc = _n or 0
        except Exception:
            profile.nproc = 0
        # ollama version (may be unavailable on a remote-only host)
        try:
            out = subprocess.run(
                ["ollama", "--version"], capture_output=True, text=True, timeout=5
            ).stdout.strip()
            profile.ollama_version = out
        except Exception:
            profile.ollama_version = ""
        for m in models or []:
            profile.model_specs[m] = _ollama_digest(m)
        return profile

    def to_dict(self) -> dict:
        return asdict(self)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_dict(), indent=2))


def _ollama_digest(model: str) -> Optional[str]:
    """Best-effort model digest from `ollama list` JSON output."""
    try:
        out = subprocess.run(
            ["ollama", "list", "--format", "json"], capture_output=True, text=True, timeout=10
        )
        if out.returncode != 0:
            return None
        items = json.loads(out.stdout)
        for it in items:
            if it.get("name") == model:
                return it.get("digest") or it.get("model")
    except Exception:
        return None
    return None