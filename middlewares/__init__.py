"""
middlewares/__init__.py — Bot middleware'lari
"""
from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Message, CallbackQuery
from loguru import logger

from database.database import AsyncSessionFactory
from services.user_service import UserService
from config import config


class DatabaseMiddleware(BaseMiddleware):
    """Har bir so'rovga DB sessiyasini inject qiladi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        async with AsyncSessionFactory() as session:
            data["session"] = session
            try:
                result = await handler(event, data)
                await session.commit()
                return result
            except Exception as e:
                await session.rollback()
                logger.error(f"DB xatosi: {e}")
                raise


class UserMiddleware(BaseMiddleware):
    """Foydalanuvchi ma'lumotlarini oladi va inject qiladi."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        user = None
        if isinstance(event, Message):
            user = event.from_user
        elif isinstance(event, CallbackQuery):
            user = event.from_user

        if user and "session" in data:
            session = data["session"]
            user_service = UserService(session)
            db_user = await user_service.get_user(user.id)

            data["db_user"] = db_user
            data["lang"] = db_user.language if db_user else config.default_lang
            data["is_admin"] = user.id in config.bot.admin_ids

            # Bloklangan foydalanuvchilarni filtrlash
            if db_user and db_user.is_blocked:
                if isinstance(event, Message):
                    await event.answer("🚫 Siz bloklangansiz.")
                return

        return await handler(event, data)


class LoggingMiddleware(BaseMiddleware):
    """Xabarlarni loglash."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any],
    ) -> Any:
        if isinstance(event, Message):
            user = event.from_user
            text = event.text or event.content_type
            logger.debug(
                f"MSG | user={user.id} | @{user.username} | text={text!r}"
            )
        elif isinstance(event, CallbackQuery):
            user = event.from_user
            logger.debug(
                f"CBQ | user={user.id} | @{user.username} | data={event.data!r}"
            )

        return await handler(event, data)
