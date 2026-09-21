# Novelty Detection & Gold-Standard Protocol

- Status: **adopted 2026-09-13** (rev.2 — consensus-only, no human labels). Implemented on the `experimental` branch as `analysis/novelty/`.
- Scope: add-on to the census v2 methodology (`methodology_notes.md`) — answers *"how do we know the C1–C4 catalog is complete, and what did it miss?"*
- Branch rule: work lands on `experimental`; the running reconstitution on `main` is untouched.

---

## 1. Design principles (rev.2)

> No human gold standard. No "three models we like". No debate escalation. Every
> instrumentation decision is pre-registered, and every panel decision is made
> from measured numbers (constructed-anchor accuracy, error diversity, and
> leave-one-out stability), never from taste or hardware budgets.

1. **Exhaustive discovery.** Every DI occurrence in the accepted corpus is reduced to a canonical fingerprint by `fingerprints.py` (pure function of stored extractor report fields — the extractor itself is *not* patched mid-run). Distinct fingerprints are deduped and **all** of them are classified; sampling appears nowhere in discovery.
2. **Ground truth by construction.** `anchors.py` builds a gold set from the *executable* catalog rules themselves and runs it through the **real extractor**: rule-derived positives, near-miss negatives (flask_depends, `Annotated[str, Field]`, plain `__call__` class, yield-not-in-DI), a real known-side matcher, and an external-DI fake. This gold set is invariant; raters are swappable instruments.
3. **Objective rater selection.** `select_panel.py` runs a hard eligibility screen (open weights, permissive license, fits the executor) over ALL eligible families (Qwen, DeepSeek, GLM, Llama, Gemma, Phi, Mistral…), then anchor qualification (accuracy + Fleiss κ), a competence floor (~0.8), and error-diversity (greedy forward selection penalizing overlapping anchor errors). Emits `novelty_leaderboard.csv`, `novelty_panel.json`.
4. **Panel size k is measured, not chosen.** `consensus.py` computes leave-one-out stability — the smallest k ≥ 3 whose single-rater-drop flip rate ≤ ε (ε ≈ 1–2%). k is never fixed by fiat and never bounded by hardware.
5. **Fully automated claims.** Final novelty labels are **consensus-only**: per-fingerprint majority at pre-registered τ = 0.65, with Fleiss κ and the full disagreement statistics published as a caveat. No human reads the rare tail.
6. **Executor pinning.** Raters are only comparable if the executor is the same. Each call records `executor.py` profile (machine, Ollama version, GGUF digest, quant, num_gpu, context, flash-attention, precision). The rater→executor mapping is frozen between selection and the definitive run, and `reverify.py` re-runs all anchors on the definitive executor: < 98% agreement on any rater ⇒ re-selection.

---

## 2. Files (`analysis/novelty/`)

| Module | Role | Testable offline? |
|---|---|---|
| `labels.py` | C1–C4 + EX2/Z + out-of-catalog taxonomy; prompt catalog text | yes |
| `fingerprints.py` | canonical fingerprints, `arg_shape()` (BARE/DOTTED/CLASS/CALL/EMPTY/ELLIPSIS/OTHER), grouping, frequency | yes |
| `anchors.py` | 16 constructed anchors run through the real extractor (`novelty_anchors.json`) | yes (needs extractor) |
| `prompt.py` | pinned rubric + CoT + few-shots; byte-stable; `parse_response` JSON extraction | yes |
| `client.py` | `OllamaClient`, local/remote, retry/backoff, per-call record callback | mock via callback |
| `consensus.py` | majority vote, τ decision, Fleiss κ, leave-one-out stability | yes (pure) |
| `executor.py` | `ExecutorProfile.capture()` — machine, ollama ver, GGUF digest | partial (shell call) |
| `select_panel.py` | hard screen → anchor scoring → floor → error-diversity → k by LOO → leaderboard/panel artifacts | yes (fake raters) |
| `annotate.py` | resumable full-corpus driver (per-fingerprint checkpoint in `novelty_annotations.jsonl`) | no (needs Ollama) |
| `reverify.py` | anchor-reverification gate on the definitive executor (floor 0.98) | no (needs Ollama) |

CLI flow:
1. `build_fingerprints.py --reports corpus/reports/ --out analysis/novelty/out/`
2. `python -m select_panel --apply --pool qwen3-coder:14b llama3.1:8b deepseek-coder:6.7b glm4:9b phi-3.5:8b --host <executor>`
3. `python -m annotate --fingerprints out/novelty_fingerprints.json --panel out/novelty_panel.json`
4. `python -m reverify ...` before the definitive run on a changed executor (or as a routine pre-flight).

---

## 3. Hardening & mitigations

| Risk | Mitigation |
|---|---|
| Extractor schema drift (reconstitution mid-run) | fingerprints computed **inside** the novelty module from stored fields; `extractor/` is read-only until reconstitution completes and corpus is renumbered |
| Executor drift (same GGUF decodes differently across machines) | per-call executor profile; frozen rater→executor mapping; anchor reverification gate (<98% ⇒ re-select); optional cross-executor probe as a published sensitivity table |
| Consensus popularity trap | only closed-set *classification* with explicit rubric + gold calibration (cite arXiv:2510.21513); never consensus over generated artifacts |
| Determinism | temperature = 0 + fixed seed per call; GGUF digests pinned (hosted/API fallbacks record response ids; drift is measured, not assumed) |
| Panel overfits the 16 anchors | k and panel both selected from cross-model LOO on anchors; re-run selection if any rater's anchor replies degrade |
| Model version drift | pin checkpoint revision + weight digest at pull time; re-run reverify before using a re-pulled model |

---

## 4. Cost & hardware

~38,100 occurrences → ~2,100 distinct `(construct, argument)` pairs → ~3–6k canonical signatures. At consensus panel k (by LOO, typically 3–5) ≈ **~15–20k LLM calls**.

| Scenario | Cost | Notes |
|---|---|---|
| Local CPU Ollama (this machine) | US$0, ~10–14 h | several Q4 small families; `temperature=0, seed` pinned |
| Collaborator RTX 3050 4 GB | free | small quants (≤ ~3.9 GB); same Ollama layer |
| Professor's dedicated GPU box | free, always-on | may share inference; same design, new executor profile + reverify |
| Hosted open-weight (fallback) | US$5–20 | pin GGUF; purge before/after; still record executor profile |

Hardware never changes the selection logic — only the eligibility screen and the executor profile. If >1 executor is ever used for the same rater, publish the cross-executor agreement table.

---

## 5. Deliverables (artifacts in `analysis/novelty/out/`)

- `novelty_fingerprints.json` / `novelty_occurrences.json` — exhaustive signature inventory (deterministic).
- `novelty_anchors.json` — the 16 constructed anchors with extractor-verified nodes.
- `novelty_leaderboard.csv` + `novelty_panel.json` + `novelty_selection.md` — panel selection, pre-registered numbers.
- `novelty_annotations.jsonl` — per-fingerprint per-rater labels, consensus, τ, executor profile (resumable).
- `novelty_reverify.json` — gate result on the definitive executor.
- Extractor is **not patched** (rev.1 considered resolver-side argument-shape canonicalization; dropped to avoid mid-run schema drift).
- Docs folded into `methodology_notes.md` + `methodology_journal.md`; a "Novelty detection" subsection in `result_draft_01.md`.

---

## 6. Papers & citations

### LLM-as-annotator / ensemble (core evidence)
1. T. Ahmed, P. Devanbu, C. Treude, M. Pradel — "Can LLMs Replace Manual Annotation of Software Engineering Artifacts?", MSR 2025 (arXiv:2408.05534). — model–model agreement predicts human–model agreement (ρ≈0.65).
2. J. Niimi et al. — "A Simple Ensemble Strategy for LLM Inference", NLDB 2025 (arXiv:2504.18884). — majority voting beats a single larger model (−18.6% RMSE).
3. — "Majority Rules: LLM Ensemble ... Content Categorization" (eLLM), arXiv:2511.15714. — Condorcet-style ensembles of 5–10 LLMs; τ=0.65 (our default).
4. — "SILICON: Management research with LLM annotation", arXiv:2412.14461. — four error sources (guideline/baseline/prompt/model-induced); regression-based open-weight backup; route low-confidence items.
5. — JuStRank (ACL 2025) — benchmark/rank LLM judges for system ranking (objective judge selection).
6. — "How AI Coders Discuss, Disagree, and Reach Consensus", arXiv:2609.11109. — multi-agent coding/debate; unresolved debate relates to higher accuracy (recorded as caveat; we do not gate on it).

### LLM-assisted qualitative coding (reliability engineering)
7. — Muse, ACL 2026 Industry Track (2026.acl-industry.131). — LLM-assisted coding reaches Cohen's κ=0.7 for well-specified codes; codebook design matters as much as model choice; CoT + true-positive few-shots improve IRR.
8. — "SYNCode", Information 16(5):392, 2025. — transformer/LLM annotation + minimal human refinement (we use **none**).

### Deterministic pattern mining (Fix #1 anchors)
9. — UP-Miner (MSR 2013), 10. — LUPIN (arXiv:2109.13099), 11. — MAPO (ASE 2009). — pattern-mining anchors for coverage/novelty measurement.

### Ensembles / code (support + honest caveat)
12. — "Ensembling LLMs for Code Vulnerability Detection", arXiv:2509.12629.
13. — "Wisdom and Delusion of LLM Ensembles", arXiv:2510.21513. — **caveat to cite**: voting/consensus only on closed-set classification, never generation.

### Methodology / reliability instrument
14. Fleiss — "Measuring nominal scale agreement among many raters", Psych. Bulletin 76(5), 1971.
15. Krippendorff — *Content Analysis*, 4th ed., 2018.
16. Condorcet's Jury Theorem (via eLLM framing) — p > 0.5 floor; per-member competence must exceed chance for ensembles to help.

### Execution/drift instrument
17. — DriftBench / "LLMs are not code reviewers"? first-citation: "Generative LLM-Judge DriftBench" (MLSys 2026) — same-model same-prompt label flips across temperature/servers (≤24% instruct); APIs reproduce temp-0 outputs only ~22% vs 95.6% local. Grounds the executor-pinning + anchor-reverification design.