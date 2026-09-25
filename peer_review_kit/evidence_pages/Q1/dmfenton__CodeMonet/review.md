# dmfenton/CodeMonet

- GitHub: https://github.com/dmfenton/CodeMonet
- Stars: 0 (covariates)
- Quadrant: Q1
- Stratum: S1 · DI nodes: 31 · commit: `ea3ec2b369a0`
- Fingerprints touching this repo: 4
- Label mix: novel=0 variant=1 known=1 false_pos=2 external_di=0 unknown=0

## Pass 1 — blind observations
| # | pattern | location | why |
|---|---|---|---|
| 1 | `FastAPI Depends with Annotated type aliases` | server/code_monet/auth/dependencies.py#L75 | Defines type aliases for dependency injection: CurrentUser = Annotated[User, Depends(get_current_user)] and OptionalUser = Annotated[User | None, Depends(get_optional_user)] |
| 2 | `Route-level dependency injection` | server/code_monet/auth/routes.py#L53 | Uses Depends in route dependencies: dependencies=[Depends(require_legacy_auth)] for the /signup endpoint |
| 3 | `Nested dependency resolution` | server/code_monet/auth/dependencies.py#L19 | get_current_user depends on security (HTTPBearer) and calls _authenticated_user which uses get_session and repository |

## Pass 2 — reconcile with inventory of dmfenton/CodeMonet

_Presented fingerprints:_ `C4|DEF`, `C1|BARE|PARAM`, `C3|CLASS|BARE`, `C3|ELLIPSIS|BARE`

| fingerprint | model label | agree? | reason | citation |
|---|---|---|---|---|
| `C4|DEF` | true_pos | **no (overturn)** | The code correctly uses Annotated[...] with Depends(...) in type aliases for dependency injection (e.g., CurrentUser = Annotated[User, Depends(get_current_user)]). These are valid FastAPI dependenc... | server/code_monet/auth/dependencies.py#L75 |
| `C3|CLASS|BARE` | true_pos | **no (overturn)** | The code correctly uses FastAPI's HTTPBearer class in security schemes (e.g., security = HTTPBearer()). These are valid class-based dependency patterns, not false positives. | server/code_monet/auth/dependencies.py#L19 |
| `C3|ELLIPSIS|BARE` | variant | yes | The code uses union types with | (e.g., HTTPAuthorizationCredentials | None) in dependency parameters, which matches the 'variant' label for this fingerprint. | server/code_monet/auth/dependencies.py#L46 |
| `C1|BARE|PARAM` | known | yes | The code correctly uses bare parameters with Depends(...) in route dependencies (e.g., dependencies=[Depends(require_legacy_auth)]), matching the 'known' label. | server/code_monet/auth/routes.py#L53 |

### Missed by inventory (1)
- `Nested dependency resolution via async functions` @ server/code_monet/auth/dependencies.py#L19 — The code uses _authenticated_user (called by get_current_user) which itself uses get_session and repository, demonstrating nested dependency resolution patterns not explicitly labeled in the invent...

## Fingerprint labels
| fingerprint | construct | #occs here | label | example |
|---|---|---|---|---|
| `C4|DEF` | C4 | 14 | **false_pos** | [server/code_monet/agent/__init__.py#L435](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/agent/__init__.py#L435) |
| `C1|BARE|PARAM` | C1 | 11 | **known** | [server/code_monet/auth/dependencies.py#L19](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/auth/dependencies.py#L19) |
| `C3|CLASS|BARE` | C3 | 3 | **false_pos** | [server/code_monet/auth/dependencies.py#L19](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/auth/dependencies.py#L19) |
| `C3|ELLIPSIS|BARE` | C3 | 3 | **variant** | [server/code_monet/auth/dependencies.py#L46](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/auth/dependencies.py#L46) |

## `C4|DEF` — **false_pos**
> occurrences here: 14 · corpus total: 56644 · executor: x86_64
> example: [server/code_monet/agent/__init__.py#L435](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/agent/__init__.py#L435)

> **evidence (model):** The examples only show argument names (e.g., 'lifespan', '__aiter__') without visible generator functions or yield-based dependency usage, suggesting the extractor misidentified non-DI code as C4.

## `C1|BARE|PARAM` — **known**
> occurrences here: 11 · corpus total: 18195 · executor: x86_64
> example: [server/code_monet/auth/dependencies.py#L19](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/auth/dependencies.py#L19)
> **rule:** C1

> **evidence (model):** The examples show function names (e.g., require_scim_token) passed directly to Depends(), matching C1's definition of a function/object passed to Depends(...).

## `C3|CLASS|BARE` — **false_pos**
> occurrences here: 3 · corpus total: 20139 · executor: x86_64
> example: [server/code_monet/auth/dependencies.py#L19](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/auth/dependencies.py#L19)
> **rule:** C3

> **evidence (model):** Annotated types (Settings, Any) are present but without Depends(...) as required by C3; this is not a valid FastAPI DI pattern

## `C3|ELLIPSIS|BARE` — **variant**
> occurrences here: 3 · corpus total: 1113 · executor: x86_64
> example: [server/code_monet/auth/dependencies.py#L46](https://github.com/dmfenton/CodeMonet/blob/ea3ec2b369a0f9d567e1021a769893fdca1733b4/server/code_monet/auth/dependencies.py#L46)
> **rule:** C3

> **evidence (model):** Annotated type uses ellipsis (...) instead of a concrete type, but still follows C3's structure of Annotated[Type, Depends(...)]

