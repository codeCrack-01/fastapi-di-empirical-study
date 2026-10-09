"""Preseed for johnsonhk88 arms: mint a valid admin JWT for the bench route.

The S2/S1/S3/S4 arms for johnsonhk88 all exercise the DI graph through
`GET /api/auth/me` (get_current_user -> get_db), which requires a valid token.
The alembic migration seeds an admin user; we look the first user up in the
real Postgres the server will use and mint a token signed with the same
JWT_SECRET the serve command sets. Run with the repo venv from repo/api:

    POSTGRES_PASSWORD=bankai JWT_SECRET=<S> ADMIN_EMAIL=... \
        ADMIN_PASSWORD_HASH=... ../../../runner/preseed_jhk.py
"""

import asyncio
import logging
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path.cwd()))

logging.getLogger("sqlalchemy.engine").setLevel(logging.CRITICAL)

from app.core.security import create_access_token, hash_password  # noqa: E402
from app.db.session import AsyncSessionLocal  # noqa: E402
from app.models import User  # noqa: E402
from sqlalchemy import select  # noqa: E402


async def _uid() -> str:
    async with AsyncSessionLocal() as s:
        r = await s.execute(select(User.id).order_by(User.created_at).limit(1))
        uid = r.scalar_one_or_none()
        if uid is not None:
            return str(uid)  # UUID as canonical string (NOT int())
        # bench fixture: no user row (migration ships no seed) -> insert one
        from sqlalchemy.dialects.postgresql import insert as pg_insert

        stmt = (
            pg_insert(User)
            .values(email="admin@bench.dev", password_hash=hash_password("bench"), is_admin=True)
            .returning(User.id)
            .on_conflict_do_nothing(index_elements=[User.email])
        )
        res = (await s.execute(stmt)).first()
        new_uid = res[0] if res else None
        if new_uid is None:
            r = await s.execute(select(User.id).where(User.email == "admin@bench.dev"))
            new_uid = r.scalar_one()
        await s.commit()
        return str(new_uid)


def main() -> None:
    uid = asyncio.run(_uid())
    print(create_access_token({"sub": str(uid), "email": "bench"}))


if __name__ == "__main__":
    main()