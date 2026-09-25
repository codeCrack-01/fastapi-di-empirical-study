# Rendered prompts — what was sent to qwen3:14b

- model: `qwen3:14b`, temperature 0, fixed seed, JSON-output schema
- reasoning traces (`thinking`) are **not** stored (Ollama `think` never enabled); the model was required to cite file:line in its JSON.

## 1. Annotate stage — system block

```
You are a precise annotator for a peer-reviewed empirical study of how FastAPI dependency injection (DI) is used in the wild. You classify DI construct fingerprints drawn from a ~4000-repo corpus by a static extractor. Your job is to judge, for a given canonical FINGERPRINT and its real code EXAMPLES, which catalog construct it belongs to OR whether it is a variant of a known pattern, a genuinely novel pattern, a false positive of the extractor, or an external DI framework.

Never invent certainty: if the evidence is insufficient, return "known" with the closest catalog id and do NOT guess "novel". "novel" is reserved for a structural pattern that no catalog rule expresses and that recurs with evidence.
```

## 2. Annotate stage — rubric block (label vocabulary + CoT instruction)

```
## Catalog
Each rule below describes exactly one construct. An occurrence that one rule describes is labeled by that rule's id (C1..C4, or EX2/Z).
- C1 (Depends): function/object passed to Depends(...)
- C2 (Security): Security(...) with optional scopes, in a signature or app/router dependencies
- C3 (Annotated dependency): Annotated[Type, Depends(...)] type metadata
- C4 (Generator/yield dependency): generator (yield) function used as a dependency
- EX2 (Non-FastAPI Depends sources): a Depends/Security identifier imported from a module other than fastapi
- Z (Zero core-DI repo): a repository that never uses Depends/Security/Annotated at all

## Output labels (choose exactly one)
- known            -> one catalog rule fully explains the fingerprint
- variant          -> semantically one of C1..C4 but spelled structurally different (e.g. dotted vs bare import, class passed where a function is expected, margin case)
- novel            -> a structural DI pattern expressed nowhere in the catalog and not expressible by any single rule
- false_pos        -> the extractor captured something that is not DI at all (e.g. an object named like a dependency, a non-DI call)
- external_di      -> DI performed by a non-FastAPI framework (dependency-injector, fastapi-injector, celery, flask, etc.); the extractor should not have counted it as FastAPI DI

## Chain-of-thought (do this before outputting JSON)
1. Read each example carefully; identify the construct slot it landed in (Depends call, 
```

## 3. Annotate stage — rendered user messages (27 fingerprints)

Reproduced verbatim via `render_user(fingerprint, examples)` with the stored per-fingerprint example payloads. First message shown in full, the rest truncated.

### 3.1 `C1|BARE|PARAM` — consensus `known`, tau=0.65

```
FINGERPRINT:
C1|BARE|PARAM

EXAMPLES (real code evidence):
{"repo": "0SansNom__holon", "line": 52, "context_function": null, "argument": "require_scim_token"}
{"repo": "0x3e4__hecate", "line": 37, "context_function": null, "argument": "require_admin_write"}
{"repo": "1semptify-arch__Semptify", "line": 39, "context_function": null, "argument": "require_capability"}
{"repo": "1semptify-arch__Semptify", "line": 138, "context_function": null, "argument": "require_capability"}
{"repo": "1semptify-arch__Semptify", "line": 31, "context_function": null, "argument": "require_admin"}

Classify this fingerprint.
```

### 3.2 `C1|BARE|SIG` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C1|BARE|SIG

EXAMPLES (real code evidence):
{"repo": "0SansNom__holon", "line": 171, "context_function": "list_automation_audit_events", "argument": "current_principal"}
{"repo": "0SansNom__holon", "line": 194, "context_function": "get_workflow_execution", "argument": "current_principal"}
{"repo": "0SansNom__holon", "line": 22, "context_function": "list_connectivity_audit_events", "ar
…(truncated)
```

### 3.3 `C1|CLASS|PARAM` — consensus `known`, tau=0.65

```
FINGERPRINT:
C1|CLASS|PARAM

EXAMPLES (real code evidence):
{"repo": "COS301-SE-2026__Veritas-Lab", "line": 242, "context_function": "create_case", "argument": "COOKIE_SCHEME"}
{"repo": "COS301-SE-2026__Veritas-Lab", "line": 328, "context_function": "get_cases", "argument": "COOKIE_SCHEME"}
{"repo": "COS301-SE-2026__Veritas-Lab", "line": 445, "context_function": "get_single_case", "argument": "COO
…(truncated)
```

### 3.4 `C1|CLASS|SIG` — consensus `known`, tau=0.65

```
FINGERPRINT:
C1|CLASS|SIG

EXAMPLES (real code evidence):
{"repo": "Coding-Temple-Tech-Residency__MedBridge-B", "line": 45, "context_function": "get_current_user_sse", "argument": "HTTPBearer"}
{"repo": "EOPF-Explorer__titiler-eopf", "line": 104, "context_function": "info_geojson", "argument": "CRSParams"}
{"repo": "EOPF-Explorer__titiler-eopf", "line": 160, "context_function": "tileset_list", "ar
…(truncated)
```

### 3.5 `C1|DOTTED|PARAM` — consensus `variant`, tau=0.65

```
FINGERPRINT:
C1|DOTTED|PARAM

EXAMPLES (real code evidence):
{"repo": "Braydenh563__MemoryMap-AI", "line": 218, "context_function": "create_app", "argument": "routes_auth.require_unlock_media"}
{"repo": "Codeit-AI10-Part4-3Team__AI10-Part4-3Team-Advanced-Project", "line": 86, "context_function": "login", "argument": "deps.db"}
{"repo": "Codeit-AI10-Part4-3Team__AI10-Part4-3Team-Advanced-Project", 
…(truncated)
```

### 3.6 `C1|DOTTED|SIG` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C1|DOTTED|SIG

EXAMPLES (real code evidence):
{"repo": "0SansNom__holon", "line": 22, "context_function": "list_ontologies", "argument": "core.current_principal"}
{"repo": "0SansNom__holon", "line": 38, "context_function": "get_ontology", "argument": "core.current_principal"}
{"repo": "0SansNom__holon", "line": 121, "context_function": "preview_action", "argument": "core.current_princ
…(truncated)
```

### 3.7 `C1|ELLIPSIS|PARAM` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C1|ELLIPSIS|PARAM

EXAMPLES (real code evidence):
{"repo": "brcampidelli__chimera-agent", "line": 63, "context_function": "cliente", "argument": "..."}
{"repo": "brcampidelli__chimera-agent", "line": 43, "context_function": "app_and_backend", "argument": "..."}
{"repo": "darkspock__CareerPython", "line": 80, "context_function": "get_current_admin_user", "argument": "..."}
{"repo": "da
…(truncated)
```

### 3.8 `C1|ELLIPSIS|SIG` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C1|ELLIPSIS|SIG

EXAMPLES (real code evidence):
{"repo": "Bederf__sentinel-ai", "line": 245, "context_function": "recommend_control", "argument": "..."}
{"repo": "Bederf__sentinel-ai", "line": 333, "context_function": "execute_control", "argument": "..."}
{"repo": "Bederf__sentinel-ai", "line": 418, "context_function": "get_control_history", "argument": "..."}
{"repo": "Murugavl__AI-p
…(truncated)
```

### 3.9 `C1|EMPTY|PARAM` — consensus `variant`, tau=0.65

```
FINGERPRINT:
C1|EMPTY|PARAM

EXAMPLES (real code evidence):
{"repo": "4ch1m__pixoo-rest", "line": 27, "context_function": "image", "argument": "<empty>"}
{"repo": "4ch1m__pixoo-rest", "line": 36, "context_function": "send_gif", "argument": "<empty>"}
{"repo": "ALK-IT__hackathon-manager", "line": 146, "context_function": "login", "argument": "<empty>"}
{"repo": "AlbanAndrieu__fastapi-sample", "line
…(truncated)
```

### 3.10 `C1|EMPTY|SIG` — consensus `variant`, tau=0.65

```
FINGERPRINT:
C1|EMPTY|SIG

EXAMPLES (real code evidence):
{"repo": "514-labs__moosestack", "line": 57, "context_function": "get_bar_data", "argument": "<empty>"}
{"repo": "7-Blocks__Kepler", "line": 109, "context_function": "login_for_access_token", "argument": "<empty>"}
{"repo": "88866888__MoviePilot", "line": 26, "context_function": "login_access_token", "argument": "<empty>"}
{"repo": "Adejare
…(truncated)
```

### 3.11 `C2|BARE|ascopes` — consensus `known`, tau=0.65

```
FINGERPRINT:
C2|BARE|ascopes

EXAMPLES (real code evidence):
{"repo": "AbheyTiwari__OCR", "line": 28, "context_function": "validate_api_key", "argument": "api_key_header"}
{"repo": "Alajmah__NodeChain", "line": 30, "context_function": "verify_token", "argument": "_security"}
{"repo": "AlphaHorizon-AI__Shogun", "line": 18, "context_function": "get_authenticated_agent", "argument": "security"}
{"rep
…(truncated)
```

### 3.12 `C2|CLASS|ascopes` — consensus `known`, tau=0.65

```
FINGERPRINT:
C2|CLASS|ascopes

EXAMPLES (real code evidence):
{"repo": "ATphobia22__PTDT-v33", "line": 37, "context_function": "inbound_seal_webhook_trigger", "argument": "X_HUB_SIGNATURE"}
{"repo": "Danush-Aries__sovereign-ai-core", "line": 174, "context_function": "_require_api_key", "argument": "API_KEY_HEADER"}
{"repo": "PTejasKr__Capsule", "line": 13, "context_function": "verify_api_key", "ar
…(truncated)
```

### 3.13 `C2|ELLIPSIS|ascopes` — consensus `variant`, tau=0.65

```
FINGERPRINT:
C2|ELLIPSIS|ascopes

EXAMPLES (real code evidence):
{"repo": "Abishek-kk__RailMind-AI", "line": 57, "context_function": "verify_api_key_http", "argument": "..."}
{"repo": "NASA-IMPACT__veda-backend", "line": 36, "context_function": "validated_token", "argument": "..."}
{"repo": "NASA-IMPACT__veda-backend", "line": 61, "context_function": "enqueue_ingestion", "argument": "..."}
{"repo"
…(truncated)
```

### 3.14 `C3|BARE|BARE` — consensus `variant`, tau=0.65

```
FINGERPRINT:
C3|BARE|BARE

EXAMPLES (real code evidence):
{"repo": "4alvit__fastapi-mqtt-gateway", "line": 89, "context_function": null, "annotated_type": "str"}
{"repo": "AI-Almanac__ai-almanac", "line": 148, "context_function": null, "annotated_type": "dict"}
{"repo": "AI-Almanac__ai-almanac", "line": 149, "context_function": null, "annotated_type": "dict"}
{"repo": "ALK-IT__hackathon-manager", 
…(truncated)
```

### 3.15 `C3|BARE|CLASS` — consensus `known`, tau=0.65

```
FINGERPRINT:
C3|BARE|CLASS

EXAMPLES (real code evidence):
{"repo": "OpenG2P__pbms", "line": 83, "context_function": "api_key_based_authenticated_partner_impl", "annotated_type": "str"}
{"repo": "OpenG2P__pbms", "line": 83, "context_function": "api_key_based_authenticated_partner_impl", "annotated_type": "str"}

Classify this fingerprint.
```

### 3.16 `C3|BARE|DOTTED` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C3|BARE|DOTTED

EXAMPLES (real code evidence):
{"repo": "Ostorlab__benchmarks", "line": 73, "context_function": "logout", "annotated_type": "str"}
{"repo": "Ostorlab__benchmarks", "line": 73, "context_function": "logout", "annotated_type": "str"}

Classify this fingerprint.
```

### 3.17 `C3|CLASS|BARE` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C3|CLASS|BARE

EXAMPLES (real code evidence):
{"repo": "1wgrumph__citypulse-austin", "line": 39, "context_function": "get_bran_gateway", "annotated_type": "Settings"}
{"repo": "1wgrumph__citypulse-austin", "line": 40, "context_function": "get_bran_gateway", "annotated_type": "Any"}
{"repo": "1wgrumph__citypulse-austin", "line": 39, "context_function": "get_bran_gateway", "annotated_ty
…(truncated)
```

### 3.18 `C3|CLASS|CLASS` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C3|CLASS|CLASS

EXAMPLES (real code evidence):
{"repo": "LinzeColin__MetaDatabase", "line": 216, "context_function": null, "annotated_type": "CatalogRepository"}
{"repo": "OpenG2P__pbms", "line": 52, "context_function": "get_my_programs", "annotated_type": "AuthCredentials"}
{"repo": "OpenG2P__pbms", "line": 52, "context_function": "get_my_programs", "annotated_type": "AuthCredentials
…(truncated)
```

### 3.19 `C3|CLASS|DOTTED` — consensus `known`, tau=0.65

```
FINGERPRINT:
C3|CLASS|DOTTED

EXAMPLES (real code evidence):
{"repo": "Codeit-AI10-Part4-3Team__AI10-Part4-3Team-Advanced-Project", "line": 87, "context_function": "login", "annotated_type": "Settings"}
{"repo": "Codeit-AI10-Part4-3Team__AI10-Part4-3Team-Advanced-Project", "line": 87, "context_function": "login", "annotated_type": "Settings"}
{"repo": "Codeit-AI10-Part4-3Team__AI10-Part4-3Team-Adv
…(truncated)
```

### 3.20 `C3|CLASS|ELLIPSIS` — consensus `known`, tau=0.65

```
FINGERPRINT:
C3|CLASS|ELLIPSIS

EXAMPLES (real code evidence):
{"repo": "darkspock__CareerPython", "line": 80, "context_function": "get_current_admin_user", "annotated_type": "QueryBus"}
{"repo": "darkspock__CareerPython", "line": 80, "context_function": "get_current_admin_user", "annotated_type": "QueryBus"}
{"repo": "darkspock__CareerPython", "line": 110, "context_function": "list_interview_temp
…(truncated)
```

### 3.21 `C3|CLASS|EMPTY` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C3|CLASS|EMPTY

EXAMPLES (real code evidence):
{"repo": "4ch1m__pixoo-rest", "line": 27, "context_function": "image", "annotated_type": "ImageModel"}
{"repo": "4ch1m__pixoo-rest", "line": 27, "context_function": "image", "annotated_type": "ImageModel"}
{"repo": "4ch1m__pixoo-rest", "line": 36, "context_function": "send_gif", "annotated_type": "GIFModel"}
{"repo": "4ch1m__pixoo-rest", 
…(truncated)
```

### 3.22 `C3|DOTTED|BARE` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C3|DOTTED|BARE

EXAMPLES (real code evidence):
{"repo": "COS301-SE-2026__Veritas-Lab", "line": 307, "context_function": "create_case", "annotated_type": "asyncpg.Connection"}
{"repo": "COS301-SE-2026__Veritas-Lab", "line": 307, "context_function": "create_case", "annotated_type": "asyncpg.Connection"}
{"repo": "COS301-SE-2026__Veritas-Lab", "line": 410, "context_function": "get_cases"
…(truncated)
```

### 3.23 `C3|DOTTED|DOTTED` — consensus `variant`, tau=0.65

```
FINGERPRINT:
C3|DOTTED|DOTTED

EXAMPLES (real code evidence):
{"repo": "Codeit-AI10-Part4-3Team__AI10-Part4-3Team-Advanced-Project", "line": 86, "context_function": "login", "annotated_type": "sqlite3.Connection"}
{"repo": "Codeit-AI10-Part4-3Team__AI10-Part4-3Team-Advanced-Project", "line": 86, "context_function": "login", "annotated_type": "sqlite3.Connection"}
{"repo": "Codeit-AI10-Part4-3Team_
…(truncated)
```

### 3.24 `C3|ELLIPSIS|BARE` — consensus `variant`, tau=0.65

```
FINGERPRINT:
C3|ELLIPSIS|BARE

EXAMPLES (real code evidence):
{"repo": "1wgrumph__citypulse-austin", "line": 41, "context_function": "get_bran_gateway", "annotated_type": "..."}
{"repo": "1wgrumph__citypulse-austin", "line": 41, "context_function": "get_bran_gateway", "annotated_type": "..."}
{"repo": "1wgrumph__citypulse-austin", "line": 63, "context_function": "receive_apify_webhook", "annotated
…(truncated)
```

### 3.25 `C3|ELLIPSIS|DOTTED` — consensus `known`, tau=0.65

```
FINGERPRINT:
C3|ELLIPSIS|DOTTED

EXAMPLES (real code evidence):
{"repo": "NASA-IMPACT__veda-backend", "line": 70, "context_function": "get_username", "annotated_type": "..."}
{"repo": "NASA-IMPACT__veda-backend", "line": 70, "context_function": "get_username", "annotated_type": "..."}
{"repo": "NASA-IMPACT__veda-backend", "line": 16, "context_function": "get_username", "annotated_type": "..."}
{"r
…(truncated)
```

### 3.26 `C4|DEF` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C4|DEF

EXAMPLES (real code evidence):
{"repo": "0SansNom__holon", "line": 185, "context_function": null, "argument": "__aiter__"}
{"repo": "0SansNom__holon", "line": 67, "context_function": null, "argument": "lifespan"}
{"repo": "0SansNom__holon", "line": 95, "context_function": null, "argument": "lifespan"}
{"repo": "0SansNom__holon", "line": 23, "context_function": null, "argument"
…(truncated)
```

### 3.27 `C4|USED` — consensus `false_pos`, tau=0.65

```
FINGERPRINT:
C4|USED

EXAMPLES (real code evidence):
{"repo": "0x3e4__pflanzn", "line": 185, "context_function": null, "argument": "get_db"}
{"repo": "1semptify-arch__Semptify", "line": 315, "context_function": null, "argument": "_get_db"}
{"repo": "1semptify-arch__Semptify", "line": 104, "context_function": null, "argument": "get_db"}
{"repo": "1semptify-arch__Semptify", "line": 28, "context_func
…(truncated)
```

## 4. repo_check stage — pass-1 system + template

**system**

```
You are an independent code reviewer for an empirical study of FastAPI dependency injection. You are looking at ONE repository from the study's stratified sample. You have NOT been told what patterns to expect — your job is to read the ACTUAL source code excerpts that follow and describe, on your own terms, how dependency injection is used here. Cite exact file:line for everything you claim. Do not invent certainty: if you see no DI, say so explicitly.
```

**user template**

```
REPOSITORY: {full_name} (stratum {stratum}, weight {weight})

STATIC SUMMARY (from a deterministic AST extractor — counts only, no pattern labels):
{summary}

REAL SOURCE EXCERPTS (code around every DI-adjacent AST node in this repo, all pinned to commit {commit_sha}):
{excerpts}

{mark}
Read the code. In JSON ONLY, answer:
{{"observations": [{{"pattern": "<your name for the DI pattern>", "file": "<path>", "line": <int>, "why": "<reasoning with references>"}}], "comment": "<anything you want flag stage 2 to reconsider>"}}
```

## 5. repo_check stage — pass-2 system + template

**system**

```
You are a second-pass DI reviewer. Another (static) instrument grouped this repository's DI occurrences into canonical structural fingerprints and a panel already labeled each fingerprint. You must now CONFRONT those labels with the REAL code in THIS repo: for each fingerprint say whether you AGREE. To OVERTURN a label you MUST cite the exact file:line in this repo that contradicts it. Also report anything you noticed in your first pass that the fingerprint inventory missed entirely.
```

**user template**

```
REPOSITORY: {full_name} (stratum {stratum}, weight {weight}), commit {commit_sha}.

PANEL LABELS PER FINGERPRINT (from an independent annotator pass):
{matches}

REAL SOURCE EXCERPTS (as in pass 1):
{excerpts}

YOUR PASS-1 OBSERVATIONS (from reading the code fresh):
{pass1}

{mark}
In JSON ONLY, answer:
{{"reconciliations": [{{"fingerprint": "<id>", "agree": true|false, "label": "<your final label>", "reason": "<why>", "citation": {{"file": "<path>", "line": <int>}}}}], "missed_by_inventory": [{{"pattern": "...", "file": "...", "line": <int>, "why": "..."}}], "comment": "..."}}
Rules: leave a fingerprint's label unchanged unless code in THIS repo contradicts it; every "agree": false must carry a citation.
```

## 6. repo_check stage — two fully rendered examples

### `0x0021/Linkora` (stratum S2, weight 6.370787)

**pass-1 user message:**

```
REPOSITORY: 0x0021/Linkora (stratum S2, weight 6.370787)

STATIC SUMMARY (from a deterministic AST extractor — counts only, no pattern labels):
files_importing_fastapi=31, fastapi_app_count=1, depends_total=0, security_total=0, annotated_depends_total=0, yield_dep_total=0, router_dep_total=0, app_dep_total=0, override_total=0, callable_class_dep_total=0

REAL SOURCE EXCERPTS (code around every DI-adjacent AST node in this repo, all pinned to commit ba6d54387788):
--- src/llm/agent_steps/stream.py:27 (handle_stream_response)  https://github.com/0x0021/Linkora/blob/ba6d5438778808d5c675f58480c099ad7bbf1f87/src/llm/agent_steps/stream.py#L27 ---

        
        def detect_stream_support(agent, enable_stream: bool) -> bool:
            """判定本轮能否走流式：需启用流式且 IM 适配器支持增量更新。"""
            stream_supported = enable_stream and agent.im_adapter is not None
            if stream_supported:
                try:
                    stream_supported = hasattr(agent.im_adapter, "chat_message_update")
                except Exception as _exc:
                    logger.debug(f"_detect_stream_support: swallowed exception: {_exc}")
                    stream_supported = False
            return stream_supported
        
        
        def handle_stream_response(
            stream,
            message,
            agent,
        ) -> Iterator[str]:
            """处理流式 LLM 响应，发送占位消息并逐步更新。
       
…(truncated)
```

**pass-2 user message:**

```
REPOSITORY: 0x0021/Linkora (stratum S2, weight 6.370787), commit ba6d54387788.

PANEL LABELS PER FINGERPRINT (from an independent annotator pass):
(none — extractor found no fingerprints here)

REAL SOURCE EXCERPTS (as in pass 1):
--- src/llm/agent_steps/stream.py:27 (handle_stream_response)  https://github.com/0x0021/Linkora/blob/ba6d5438778808d5c675f58480c099ad7bbf1f87/src/llm/agent_steps/stream.py#L27 ---

        
        def detect_stream_support(agent, enable_stream: bool) -> bool:
            """判定本轮能否走流式：需启用流式且 IM 适配器支持增量更新。"""
            stream_supported = enable_stream and agent.im_adapter is not None
            if stream_supported:
                try:
                    stream_supported = hasattr(agent.im_adapter, "chat_message_update")
                except Exception as _exc:
                    logger.debug(f"_detect_stream_support: swallowed exception: {_exc}")
                    stream_supported = False
            return stream_supported
        
        
        def handle_stream_response(
            stream,
            message,
            agent,
        ) -> Iterator[str]:
            """处理流式 LLM 响应，发送占位消息并逐步更新。
        
            委托给 src.llm.stream_helper.handle_stream_response，
            传入 agent 上的方法引用以维持与 agent._handle_stream_response 的接口一致。
            """
            from src.llm.stream_helper import handle_stream_response as _helper
        
…(truncated)
```

### `EndofTimeWorks/pluris-haven` (stratum S1, weight 12.74359)

**pass-1 user message:**

```
REPOSITORY: EndofTimeWorks/pluris-haven (stratum S1, weight 12.74359)

STATIC SUMMARY (from a deterministic AST extractor — counts only, no pattern labels):
files_importing_fastapi=8, fastapi_app_count=1, depends_total=8, security_total=0, annotated_depends_total=11, yield_dep_total=1, router_dep_total=1, app_dep_total=0, override_total=0, callable_class_dep_total=0

REAL SOURCE EXCERPTS (code around every DI-adjacent AST node in this repo, all pinned to commit e6fe1d7dd34b):
--- server/pluris_server/dependencies.py:30 (get_auth_context)  https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L30 ---
bearer = HTTPBearer(auto_error=False)
        
        
        @dataclass(frozen=True)
        class AuthContext:
            user: User
            session: DeviceSession
        
        
        def settings_from_request(request: Request) -> Settings:
            return request.app.state.settings
        
        
        async def get_auth_context(
            credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
            db: Annotated[AsyncSession, Depends(get_db)],
            settings: Annotated[Settings, Depends(settings_from_request)],
        ) -> AuthContext:
            unauthorized = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
            
…(truncated)
```

**pass-2 user message:**

```
REPOSITORY: EndofTimeWorks/pluris-haven (stratum S1, weight 12.74359), commit e6fe1d7dd34b.

PANEL LABELS PER FINGERPRINT (from an independent annotator pass):
(none — extractor found no fingerprints here)

REAL SOURCE EXCERPTS (as in pass 1):
--- server/pluris_server/dependencies.py:30 (get_auth_context)  https://github.com/EndofTimeWorks/pluris-haven/blob/e6fe1d7dd34bf3eeaa7acf63f077e1820c3fc0c2/server/pluris_server/dependencies.py#L30 ---
bearer = HTTPBearer(auto_error=False)
        
        
        @dataclass(frozen=True)
        class AuthContext:
            user: User
            session: DeviceSession
        
        
        def settings_from_request(request: Request) -> Settings:
            return request.app.state.settings
        
        
        async def get_auth_context(
            credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(bearer)],
            db: Annotated[AsyncSession, Depends(get_db)],
            settings: Annotated[Settings, Depends(settings_from_request)],
        ) -> AuthContext:
            unauthorized = HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or expired credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
            if credentials is None:
                raise unauthorized
            try:
                payload = decode_a
…(truncated)
```

