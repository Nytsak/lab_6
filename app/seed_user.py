import asyncio
from app.core.database import AsyncSessionLocal, Base, engine
from app.auth.repository import UserRepository
from app.core.security import hash_password

async def seed_user():
    import app.auth.models
    import app.books.models
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        repo = UserRepository(db)
        existing = await repo.get_by_username("admin")
        if not existing:
            await repo.create("admin", hash_password("admin"))
            print("Admin user created (username: admin, password: admin)")
        else:
            print("Admin user already exists")

if __name__ == "__main__":
    asyncio.run(seed_user())
