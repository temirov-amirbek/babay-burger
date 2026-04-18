"""
services/user_service.py — Foydalanuvchi bilan ishlash servisi
"""
from typing import Optional
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import User
from config import config


class UserService:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_user(self, user_id: int) -> Optional[User]:
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def create_user(
        self,
        user_id: int,
        full_name: str,
        username: Optional[str] = None,
        lang: str = "uz",
    ) -> User:
        user = User(
            id=user_id,
            full_name=full_name,
            username=username,
            language=lang,
            is_admin=(user_id in config.bot.admin_ids),
        )
        self.session.add(user)
        await self.session.flush()
        return user

    async def get_or_create(
        self,
        user_id: int,
        full_name: str,
        username: Optional[str] = None,
    ) -> tuple[User, bool]:
        """(user, created) qaytaradi."""
        user = await self.get_user(user_id)
        if user:
            return user, False
        user = await self.create_user(user_id, full_name, username)
        return user, True

    async def update_phone(self, user_id: int, phone: str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(phone=phone)
        )

    async def update_name(self, user_id: int, name: str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(full_name=name)
        )

    async def update_language(self, user_id: int, lang: str) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(language=lang)
        )

    async def get_all_users(
        self, lang: Optional[str] = None, active_only: bool = True
    ) -> list[User]:
        q = select(User)
        if lang:
            q = q.where(User.language == lang)
        if active_only:
            q = q.where(User.is_blocked == False)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_user_count(self) -> int:
        from sqlalchemy import func
        result = await self.session.execute(
            select(func.count(User.id)).where(User.is_blocked == False)
        )
        return result.scalar_one()

    async def block_user(self, user_id: int) -> None:
        await self.session.execute(
            update(User).where(User.id == user_id).values(is_blocked=True)
        )

    async def is_admin(self, user_id: int) -> bool:
        return user_id in config.bot.admin_ids

    async def get_user_lang(self, user_id: int) -> str:
        user = await self.get_user(user_id)
        return user.language if user else config.default_lang
