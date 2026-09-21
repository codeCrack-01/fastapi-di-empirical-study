"""remote/__init__.py — self-contained remote judge-job bundle.

Ships to the remote Windows executor (professor's box) as-is. The executor
installs Ollama, pulls pinned GGUF digests, runs ``run_judge_job`` (stages:
profile -> select -> reverify -> annotate -> sync), ships immutable result
chunks through a shared folder, and tears down.

Modules are importable directly because the job script adds this repo root to
sys.path before importing ``analysis.novelty``.
"""