"""analysis/novelty/client.py — backend-agnostic model client with pinning.

Supports local and remote Ollama endpoints (``OLLAMA_HOST``), the only two
backends needed for the solo/GPU-shared futures. Every request carries the
executor profile + frozen sampling config so annotation is reproducible per
(executor, model, prompt, seed).

Determinism: Ollama supports a fixed ``seed``; we send temperature=0 and a
fixed seed at every call. For hosted/API backends without seed control the
client records the response id and temperatures so disagreement is measurable
rather than silently averaged.

Robustness: retry with exponential backoff (shared GPU boxes are timeshared and
may briefly reject); a max-tokens guard; and a pluggable ``record_callback`` so
callers can persist each (request, response, latency, profile) for the audit
trail and for the model-model agreement stats.
"""
from __future__ import annotations

import json
import os
import time
from dataclasses import dataclass, field
from typing import Any, Callable, Optional

import requests


@dataclass
class OllamaClient:
    model: str
    host: str = ""
    temperature: float = 0.0
    seed: int = 42
    num_ctx: int = 16384
    max_tokens: int = 2048
    timeout: float = 600.0
    retries: int = 4
    backoff_base: float = 2.0
    record_callback: Optional[Callable[[dict], None]] = None

    def __post_init__(self):
        self.host = self.host or os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        self.host = self.host.rstrip("/")
        session = requests.Session()
        session.headers.update({"Content-Type": "application/json"})
        self._session = session

    # ------------------------------------------------------------------ I/O
    def generate(self, system: str, user: str) -> dict:
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "options": {
                "temperature": self.temperature,
                "seed": self.seed,
                "num_ctx": self.num_ctx,
                "num_predict": self.max_tokens,
            },
        }
        return self._post(payload)

    def _post(self, payload: dict) -> dict:
        last: Optional[Exception] = None
        for attempt in range(self.retries):
            started = time.time()
            try:
                resp = self._session.post(f"{self.host}/api/chat", json=payload, timeout=self.timeout)
                resp.raise_for_status()
                data = resp.json()
                record = {
                    "model": self.model,
                    "host": self.host,
                    "attempt": attempt,
                    "latency_s": round(time.time() - started, 3),
                    "response_id": data.get("id"),
                    "created_at": data.get("created_at"),
                    "done_reason": data.get("done_reason"),
                    "prompt_eval_count": data.get("prompt_eval_count"),
                    "eval_count": data.get("eval_count"),
                    "content": data.get("message", {}).get("content", ""),
                }
                if self.record_callback:
                    self.record_callback(record)
                return record
            except (requests.RequestException, ValueError) as exc:
                last = exc
                time.sleep(self.backoff_base ** attempt)
        raise RuntimeError(f"Ollama request failed after retries for {self.model}: {last}")