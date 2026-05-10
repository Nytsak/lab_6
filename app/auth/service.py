from app.auth.repository import UserRepository
from typing import Optional
from app.auth.models import User
from uuid import UUID

class AuthService:
    def __init__(self, repository: UserRepository):
        self.repository = repository

    async def get_user_by_id(self, user_id: UUID) -> Optional[User]:
        return await self.repository.get_by_id(user_id)

    async def get_user_by_username(self, username: str) -> Optional[User]:
        return await self.repository.get_by_username(username)
