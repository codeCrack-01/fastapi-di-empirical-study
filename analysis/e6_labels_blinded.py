# Label mapping from the blinded review (order in e6_review_evidence.txt).
#
# Labels: G = genuine application, D = demo/tutorial/scaffold/challenge artifact,
#         U = uncertain (functional but research/portfolio/challenge-status, or
#             thin docs relative to ambition).
#
# Assignment was made BEFORE unmasking the flag/control and stars, using only
# README language + project tree structure + dependency profile.
case_labels = {
    0: "G",   # HERMES: DICOM/Orthanc clinical data platform, FastAPI+Postgres, submodules
    1: "G",   # housepy: released genealogy service, PyPI, live API, sqlalchemy, tests
    2: "G",   # Sealium: production licensing toolkit, RSA/AES, src layout, tests
    3: "G",   # Wind-turbine PM platform: CI, 432 tests, Docker, notebooks
    4: "G",   # energy-data-rag-pipeline: docker-compose, langchain, pgvector, tests
    5: "G",   # api.evd: university evaluation API, alembic, Makefile, tests, docker
    6: "G",   # myblog_backend: blog+music-reviews core API, Cognito auth, tests
    7: "G",   # agent-failure: instrumented AI security lab, alembic/docker/tests (real product)
    8: "G",   # capitalview-api: wealth mgmt API, alembic, tests, Docker
    9: "U",   # OWNEX: doc-heavy ambitious personal platform, deps very thin vs 1400+ tests claim
    10: "G",  # bucketing: expense tracker PWA, alembic, tests, Docker
    11: "G",  # trackinizer: epistemological DB, PyPI+CI
    12: "G",  # open-grimoire: self-hosted RPG PDF app, 5-stage pipeline, Docker, tests
    13: "G",  # VillageGameBot: production-flag Discord bot, cog architecture
    14: "G",  # video-preview-app: video catalog/token API, Docker, admin accounts
    15: "G",  # M365 Copilot reporter: containerised Graph->Postgres->dashboard, alembic, tests, Azure
    16: "G",  # waygate: OpenStack WireGuard gateway, sdk, tests, Docker (no README but real infra)
    17: "U",  # CEREBRO-X: research pipeline, Docker/tests/CI; self-declared research prototype NOT production
    18: "G",  # Forge-OH: AI coding assistant, Next.js+FastAPI, full test/playwright tooling
    19: "G",  # order-intelligence-layer: corp project, docker, tests, pipelines, dashboards
    20: "G",  # msb-v3: sovereign AI runtime, many endpoints, Prometheus, Docker, tests
    21: "G",  # FlowDesk-Backend: multi-tenant SaaS, alembic, Supabase JWKS auth, tests
    22: "G",  # MarketPulse: hosted on Render, 31 tests, CI/CD, Docker, LangGraph
    23: "G",  # celuma-backend: multi-tenant lab mgmt, alembic, tests, Docker
    24: "D",  # Nile-Connect: self-declared 'portfolio demonstration from a notebook', demo content
    25: "G",  # grok-build-gateway: reusable microservice, SDK, tests, Docker
    26: "U",  # cadence-clinical: self-declared 'Pre-Demo sandbox, WIP', big monorepo concept
    27: "G",  # trussium: cloud-native AI runtime, hatchling, tests, Docker, deploy/
    28: "G",  # Devops_CD: CD service from real ops experience, Docker, smoke tests
    29: "U",  # mapi: explicit 'public engineering portfolio artifact, not production', synthetic examples
    30: "G",  # havachat: language-learning content pipeline, heavy real deps, tests
    31: "G",  # tidings: private finance journal, CI, Docker, docs-site
    32: "G",  # amosclaude: scoped inspection tool, Docker, CircleCI, many release/self-host docs
    33: "U",  # Earth-obs verification lab: explicit 'fictional civilian platform, synthetic', exercise in verification
    34: "G",  # lux: visual surface for AI agents, PyPI, tests, alpha
    35: "G",  # cyxcbot: QQ bot w/ web admin, Docker, tests, real user base
    36: "G",  # MoneyPrinterTurbo: well-known AI short-video generator, Docker, tests
    37: "D",  # KB-NEST: '2026 KB AI Challenge' entry, minimal requirements.txt only
    38: "D",  # msit-capstone-project: university capstone, committed .db files + venv, 'demonstrates'
    39: "U",  # dharma_swarm: aspirational swarm runtime, extremely docs-heavy, thin runtime deps
    40: "G",  # data_pipeline: full-stack dash, Celery/RabbitMQ microservices, Docker compose
    41: "G",  # HospitalityAIPlatform: multi-tenant SaaS, alembic, tests, Makefile, ADR docs
    42: "G",  # vires: strength-tracker PWA, alembic, tests, CI, semantic search
    43: "U",  # prima-tech-challenge: 'Tech Challenge' but production-shaped AWS API, Docker/Helm/Terraform/tests
    44: "G",  # gitopsapi: GitOps-as-store backend, Docker, tests, Helm charts
    45: "G",  # Personal_Execution_OS: self-hosted PWA app, alembic, tests, Docker, sentry
    46: "U",  # Fathom (aquarium-tracker): hobby-level smart aquarium app, SQLite, plain templates, Anthropic
    47: "G",  # OpenHubble: cloud API, alembic, models, firebase auth, migrations
}