import asyncio
from app.core.config import settings
from app.db.session import engine
from sqlalchemy import text

async def test_db():
    print(f"Connecting to: {settings.database_url}")
    try:
        async with engine.connect() as conn:
            result = await conn.execute(text("SELECT 1"))
            print(f"Connection successful: {result.scalar()}")
    except Exception as e:
        print(f"Database connection failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_db())
