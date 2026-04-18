"""
bot.py — Babay Burger Bot asosiy kirish nuqtasi
"""
import asyncio
import os
from loguru import logger

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.fsm.storage.memory import MemoryStorage

from config import config
from utils.logger import setup_logger
from database.database import create_tables
from middlewares import DatabaseMiddleware, UserMiddleware, LoggingMiddleware

# ── Handlerlarni import qilish ─────────────────────────────────────────────────
from handlers.user.registration import router as reg_router
from handlers.user.menu import router as menu_router
from handlers.user.ordering import router as order_router
from handlers.user.my_orders import router as my_orders_router
from handlers.admin.admin_main import router as admin_main_router
from handlers.admin.admin_orders import router as admin_orders_router
from handlers.admin.admin_products import router as admin_products_router
from handlers.admin.admin_broadcast import router as admin_broadcast_router


async def on_startup(bot: Bot) -> None:
    """Bot ishga tushganda bajariladigan amallar."""
    # Database jadvallarini yaratish
    await create_tables()

    # Adminlarga xabar yuborish
    for admin_id in config.bot.admin_ids:
        try:
            await bot.send_message(
                admin_id,
                "✅ <b>Babay Burger Bot</b> ishga tushdi!\n\n"
                f"🕐 Vaqt: {__import__('datetime').datetime.now().strftime('%d.%m.%Y %H:%M')}",
                parse_mode="HTML",
            )
        except Exception as e:
            logger.warning(f"Admin {admin_id} ga xabar yuborib bo'lmadi: {e}")

    logger.success("🚀 Bot ishga tushdi!")


async def on_shutdown(bot: Bot) -> None:
    """Bot to'xtaganda bajariladigan amallar."""
    logger.info("🛑 Bot to'xtatilmoqda...")
    for admin_id in config.bot.admin_ids:
        try:
            await bot.send_message(admin_id, "🛑 Bot to'xtatildi.")
        except Exception:
            pass


async def main() -> None:
    # Logger sozlash
    setup_logger()

    os.makedirs("logs", exist_ok=True)

    # Bot yaratish
    bot = Bot(
        token=config.bot.token,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    # FSM Storage (Redis ishlamaganida MemoryStorage ishlatiladi)
    try:
        storage = RedisStorage.from_url(config.redis.url)
        logger.info("✅ Redis storage ishga tushdi")
    except Exception:
        logger.warning("⚠️ Redis ulana olmadi, MemoryStorage ishlatiladi")
        storage = MemoryStorage()

    # Dispatcher
    dp = Dispatcher(storage=storage)

    # ── Middleware'larni ro'yxatga olish ──────────────────────────────────────
    dp.message.middleware(LoggingMiddleware())
    dp.callback_query.middleware(LoggingMiddleware())

    dp.message.middleware(DatabaseMiddleware())
    dp.callback_query.middleware(DatabaseMiddleware())

    dp.message.middleware(UserMiddleware())
    dp.callback_query.middleware(UserMiddleware())

    # ── Routerlarni ro'yxatga olish (tartib muhim!) ───────────────────────────
    dp.include_router(reg_router)      # /start va ro'yxatdan o'tish

    # Admin routerlari (avval, chunki F.text filtrlari bor)
    dp.include_router(admin_main_router)
    dp.include_router(admin_orders_router)
    dp.include_router(admin_products_router)
    dp.include_router(admin_broadcast_router)

    # User routerlari
    dp.include_router(menu_router)
    dp.include_router(order_router)
    dp.include_router(my_orders_router)

    # ── Lifecycle hook'lar ────────────────────────────────────────────────────
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    # ── Botni ishga tushirish (polling) ───────────────────────────────────────
    logger.info(f"Bot @{(await bot.get_me()).username} polling boshlandi...")

    await dp.start_polling(
        bot,
        allowed_updates=dp.resolve_used_update_types(),
        drop_pending_updates=True,
    )


if __name__ == "__main__":
    asyncio.run(main())
