"""Bench entry for azure-samples arms: run the real backend without an Azure session.

The postgres pool authenticates with an AAD token (AzureCliCredential); on a
credential-less machine that raises and lifespan refuses to boot. This wrapper
replaces only `AzureCliCredential.get_token` with one that returns the local
pgvector container password (AZURE_POSTGRES_LOCAL_PASSWORD, default "cwyd") --
the same substitution the repo's own lifespan tests make with MagicMock
credentials. Everything under test (S1/S2/S3/S4 DI wiring, health route, DB
client) is the real repo code. The health route is public (no auth).
"""

import os

from azure.identity.aio import AzureCliCredential


class _LocalToken:
    def __init__(self, token: str) -> None:
        self.token = token
        self.expires_on = 0


async def _get_token(self, *scopes, **kwargs):  # noqa: ANN002, ANN003
    return _LocalToken(os.environ.get("AZURE_POSTGRES_LOCAL_PASSWORD", "cwyd"))


AzureCliCredential.get_token = _get_token

from backend.app import app  # noqa: E402

__all__ = ["app"]
