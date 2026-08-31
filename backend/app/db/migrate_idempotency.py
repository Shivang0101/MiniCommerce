import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

from app.db.session import engine


async def migrate_schema():
    print("[INFO] Migrating Supabase database schema for users and orders tables...")
    async with engine.begin() as conn:
        await conn.execute(
            text(
                "ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN NOT NULL DEFAULT FALSE;"
            )
        )
        await conn.execute(
            text("ALTER TABLE orders ADD COLUMN IF NOT EXISTS idempotency_key VARCHAR(255);")
        )
        await conn.execute(
            text(
                "CREATE UNIQUE INDEX IF NOT EXISTS uq_user_idempotency_key ON orders (user_id, idempotency_key);"
            )
        )
    print(
        "[SUCCESS] Schema migration complete: is_admin added to users table, idempotency_key added to orders table."
    )


if __name__ == "__main__":
    asyncio.run(migrate_schema())
