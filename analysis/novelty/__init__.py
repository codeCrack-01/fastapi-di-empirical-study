"""analysis/novelty — canonical fingerprinting + LLM-ensemble novelty discovery.

Fully backend-agnostic. Ground-truth is CONSTRUCTED from the executable catalog
rules (C1-C4 + EX2/Z), not annotated by humans. Rater selection and panel size
are measurement-driven (anchors + error-diversity + leave-one-out stability).

Modules:
    fingerprints : canonical fingerprint extraction from extractor reports
    anchors      : constructed test items (rule-derived positives, near-miss
                   negatives, real known-side matcher)
    prompt       : pinned annotation prompt (rubric + CoT + few-shots)
    clients      : OllamaClient (local or remote; retry/backoff; checkpoint)
    consensus    : majority vote + Fleiss' kappa + tau threshold
    select_panel : objective rater selection -> leaderboard + panel + k
    annotate     : full-corpus annotation driver (resumable)
    reverify     : anchor-reverification gate before the definitive run
    executor     : executor fingerprint / pinning records
"""