# Novelty panel selection

- Candidate pool: ['fake-qwen', 'fake-llama', 'fake-deepseek', 'fake-glm', 'fake-phi']
- Anchor set: 12 constructed items (no humans)
- Competence floor: accuracy >= 0.8
- Panel (greedy, max-k=5): ['fake-qwen', 'fake-deepseek', 'fake-glm', 'fake-llama']
- Leave-one-out stability eps=0.02: k_design=4, reported k=4

| model | accuracy | qualified |
|---|---|---|
| fake-qwen | 1.0 | yes |
| fake-deepseek | 1.0 | yes |
| fake-glm | 1.0 | yes |
| fake-llama | 0.9167 | yes |
| fake-phi | 0.5833 | no |
