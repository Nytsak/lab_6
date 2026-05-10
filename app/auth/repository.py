from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import RefreshToken, User

class UserRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_username(self, username: str) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.username == username))
        return result.scalars().first()

    async def get_by_id(self, user_id: UUID) -> Optional[User]:
        result = await self.db.execute(select(User).where(User.id == user_id))
        return result.scalars().first()

    async def create(self, username: str, hashed_password: str) -> User:
        user = User(username=username, hashed_password=hashed_password)
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        return user

    async def save_refresh_token(
        self, user_id: UUID, token: str, expires_at: datetime
    ) -> RefreshToken:
        rt = RefreshToken(user_id=user_id, token=token, expires_at=expires_at)
        self.db.add(rt)
        await self.db.commit()
        return rt

    async def get_refresh_token(self, token: str) -> Optional[RefreshToken]:
        result = await self.db.execute(
            select(RefreshToken).where(RefreshToken.token == token)
        )
        return result.scalars().first()

    async def delete_refresh_token(self, token: str) -> None:
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.token == token)
        )
        await self.db.commit()

    async def rotate_refresh_token(
        self, old_token: str, new_token: str, user_id: UUID, expires_at: datetime
    ) -> RefreshToken:
        """Atomically deletes the old refresh token and saves a new one (token rotation)."""
        await self.db.execute(
            delete(RefreshToken).where(RefreshToken.token == old_token)
        )
        rt = RefreshToken(user_id=user_id, token=new_token, expires_at=expires_at)
        self.db.add(rt)
        await self.db.commit()
        return rt
