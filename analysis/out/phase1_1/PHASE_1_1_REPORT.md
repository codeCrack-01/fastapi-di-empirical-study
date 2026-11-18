# Phase 1.1 report — explaining the S1/S3 count change

Commit tag: `eval-freeze-1` (overleaf 9b065d3; research repo state at freeze).
Data sources: `analysis/out/compare_v0.4_v0.5.json`, `analysis/out/s1s3_boundary_seen.csv` (old labels, 758/45), `analysis/out/peer_review_327.json` (validation, v0.5).

## 1. Transition matrix (old label x new label)

| old \ new | S1 | S2 | S3 | S4 | row total |
|---|---:|---:|---:|---:|---:|
| S1 (758) | 517 | 0 | 241 | 0 | 758 |
| S2 (1369) | 1 | 1368 | 0 | 0 | 1369 |
| S3 (45) | 0 | 0 | 45 | 0 | 45 |
| S4 (7) | 0 | 0 | 0 | 7 | 7 |
| **col total** | **518** | **1368** | **286** | **7** | **2179** |

- 241 of 758 old-S1 repositories (31.8%) moved to S3; all other old-S1 (517) stayed S1 plus one S2->S1.
- No repository moved out of S3 or S4; S3 grew entirely from S1.
- Combined S1+S3 is stable: 803 (old) vs 804 (new). S2 stable (1369 vs 1368).

## 2. Rule change in one paragraph

The v0.5 classifier broadened the manual-DI (S3) vocabulary: constructor injection, setter injection, attribute injection, interface injection and service-locator patterns that v0.4 did not recognise are now detected. Concretely, 241 repositories that v0.4 labelled "no DI detected" (S1) because their dependency wiring was not a FastAPI `Depends()`/`Security()`/`Annotated` call are now labelled S3, since they hand-wire dependencies (e.g. `Service(dep)` in a constructor, or registry lookups). S2, S3's existing 45 and S4 are unchanged. The change is a recall gain on hand-written DI, not a change in the FastAPI-native boundary.

## 3. Audit of 25 randomly moved repositories (seed 20261103)

All 25 are cloned locally. Evidence type from `analysis/out/s3_evidence_v0.5.csv` (all sites direct, not heuristic). Provisional S3-correctness judgment pending rubric 1.2 (Fowler 2004 S3a composition-root vs S3b service-locator).

| repo | evidence | sites | provisional judgment |
|---|---|---:|---|
| Iron-Triangle-Tech/Locus | constructor_injection | 6 | S3 (constructor params wired) |
| hapax-systems/reins | constructor_injection | 80 | S3 (large constructor-injection surface) |
| hoshisora1/ai-resume-match | constructor_injection | 1 | S3 (single constructor injection) |
| roshni2020/CivicTrace_SF | setter_injection | 1 | S3 (setter injection) |
| zeroday0619/KotonohaInterpreter | constructor_injection | 1 | S3 |
| iVGeek/bta | constructor_injection | 2 | S3 |
| bossayan9999/aios-one-command-center | constructor_injection | 3 | S3 |
| KyleHafner/helios-horizon | constructor_injection | 18 | S3 |
| ClearGlassInc/Opal-Koboi | constructor_injection | 2 | S3 |
| a-simeshin/librarian-lightrag | constructor_injection | 3 | S3 |
| auraecosystem/Smart-Farming-app | constructor_injection | 2 | S3 |
| F4TB0Yz/kirospan | constructor_injection | 12 | S3 |
| manuelbomi/crew-ai-fraud | constructor_injection | 1 | S3 |
| BigProject09/cultural-heritage-be | constructor_injection | 3 | S3 |
| asadbutt64/OGS | constructor_injection | 3 | S3 |
| localzet/caine-companion | constructor_injection | 7 | S3 |
| pilotmain/AethOS | constructor_injection | 1 | S3 |
| bupt20220407/compute-optical-orchestrator | constructor_injection | 16 | S3 |
| sueun-dev/open-seed | constructor_injection | 1 | S3 |
| DansiDanutz/SemeClaw | constructor_injection+setter | 5 | S3 |
| clausgf/nicepaper | constructor_injection | 1 | S3 |
| MuhammadHassanminhas/DATA-CLEANING-DISTRIBUTED-SYSTEM | setter_injection | 1 | S3 |
| DEVTKITS/devkitz-workspace | constructor_injection | 2 | S3 |
| paperworkmg-arch/VOLT | constructor_injection | 2 | S3 |
| almondsun/nutshellm | constructor_injection | 2 | S3 |

Provisional: 25/25 show direct constructor or setter injection evidence, consistent with S3 under the broadened vocabulary. Whether each qualifies as S3a (external composition root) vs S3b (service locator) requires the rubric in 1.2 and a human read of the call sites; this sheet is the input for that.

## 4. Validation reconciliation (already v0.5)

- `peer_review_327.json`: predicted S3 = 38, gold S3 = 19, precision 0.368, recall 0.737.
- 23 of 77 gold-S1 repositories predicted S3 (29.9%), matching the corpus move scale (241/758 = 31.8%).
- 28 of 29 errors are S1/S3 swaps; combined S1+S3 differs by 1 (96 gold vs 97 predicted).
- Conclusion: the validation matrix already describes the v0.5 labels; the paper's missing piece was the reconciliation paragraph (added in commit b3b7b0e).

## Stop point
Per work order 1.1: stop and report before continuing. Next: 1.2 rubric fix (human), 1.3 relabel 95 imputed repos (human raters), 1.4 freeze, 1.5 audit sample, 1.6 weighted estimates, 1.7 headline rule, 1.8 reconciliation.