# Anubhav9/Yellow-Olive

- GitHub: https://github.com/Anubhav9/Yellow-Olive
- Stars: 83 (covariates)
- Quadrant: Q4
- Stratum: S3 · DI nodes: 10 · commit: `1472c88be42e`
- Fingerprints touching this repo: 1
- Label mix: novel=0 variant=0 known=0 false_pos=1 external_di=0 unknown=0

## Pass 1 — blind observations
## Pass 2 — reconcile with inventory of Anubhav9/Yellow-Olive

_Presented fingerprints:_ `C4|DEF`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The compose() methods in the provided files are valid and correctly implemented, contradicting the 'false_pos' label. | app.py#L38 |
| `C4|DEF` | true_pos | **no (overturn)** | The compose() method in NameInputScreen is properly structured with valid widget yields. | scenarios/oakwood_meadows/prologue/screens/name_input_screen.py#L16 |
| `C4|DEF` | true_pos | **no (overturn)** | The compose() method in BaseChallengeScreen correctly yields widgets and handles game logic. | screens/common/base_challenge_screen.py#L32 |

### Missed by inventory (3)
- `compose() methods in other screens` @ screens/common/challenge_music_preference_screen.py#L19 — The inventory did not include this file's compose() method as part of C4|DEF, but it follows the same pattern as the labeled instances.
- `compose() methods in other screens` @ screens/common/diagnostics_consent_screen.py#L90 — This file's compose() method matches the structural pattern of C4|DEF but was not included in the initial inventory.
- `compose() methods in other screens` @ screens/common/game_initialisation_and_reference_screen.py#L21 — This file's compose() method aligns with C4|DEF but was omitted from the inventory.

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 10 | **false_pos** | [app.py#L38](https://github.com/Anubhav9/Yellow-Olive/blob/1472c88be42e1f2395d705a9d341ca39ef32e645/app.py#L38) |

## `C4|DEF` — **false_pos**
> occurrences here: 10 · corpus total: 56644 · executor: x86_64
> example: [app.py#L38](https://github.com/Anubhav9/Yellow-Olive/blob/1472c88be42e1f2395d705a9d341ca39ef32e645/app.py#L38)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

