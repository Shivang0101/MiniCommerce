import asyncio
import sys
from pathlib import Path

from sqlalchemy import text

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent))
from app.db.session import engine


async def promote():
    async with engine.begin() as conn:
        await conn.execute(
            text("UPDATE users SET is_admin = TRUE WHERE email = 'admin@minicommerce.com';")
        )
        print("[SUCCESS] admin@minicommerce.com is now confirmed as Admin in database!")


if __name__ == "__main__":
    asyncio.run(promote())
