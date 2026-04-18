"""
handlers/admin/admin_main.py — Admin panel asosiy handler
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from loguru import logger

from database.database import AsyncSession
from services.user_service import UserService
from services.order_service import OrderService
from services.product_service import ProductService
from keyboards.admin_kb import admin_main_keyboard
from config import config

router = Router(name="admin_main")


def is_admin(user_id: int) -> bool:
    return user_id in config.bot.admin_ids


@router.message(Command("admin"))
async def admin_panel(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("⛔️ Ruxsat yo'q.")
        return

    await state.clear()
    await message.answer(
        "🔐 <b>Admin Panel</b>\n\nXush kelibsiz!",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


@router.message(F.text == "📊 Statistika")
async def admin_stats(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return

    order_service = OrderService(session)
    user_service = UserService(session)
    product_service = ProductService(session)

    daily = await order_service.get_daily_stats()
    total = await order_service.get_total_stats()
    user_count = await user_service.get_user_count()
    top_products = await product_service.get_top_products(limit=5)

    top_text = "\n".join(
        f"  {i+1}. {p['name']} — {p['qty']} ta ({p['revenue']:,} so'm)"
        for i, p in enumerate(top_products)
    ) or "  Ma'lumot yo'q"

    text = (
        "📊 <b>Statistika</b>\n\n"
        f"<b>Bugun:</b>\n"
        f"  📦 Buyurtmalar: {daily['count']} ta\n"
        f"  💰 Daromad: {daily['revenue']:,} so'm\n\n"
        f"<b>Jami (barchasi):</b>\n"
        f"  📦 Buyurtmalar: {total['total_orders']} ta\n"
        f"  💰 Daromad: {total['total_revenue']:,} so'm\n\n"
        f"<b>Foydalanuvchilar:</b> {user_count} ta\n\n"
        f"<b>🏆 Eng ko'p sotilgan:</b>\n{top_text}"
    )

    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "👥 Foydalanuvchilar")
async def admin_users(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return

    user_service = UserService(session)
    users = await user_service.get_all_users()

    lang_counts = {}
    for u in users:
        lang_counts[u.language] = lang_counts.get(u.language, 0) + 1

    text = (
        f"👥 <b>Foydalanuvchilar</b>\n\n"
        f"Jami: <b>{len(users)}</b> ta\n\n"
        f"🇺🇿 O'zbek: {lang_counts.get('uz', 0)}\n"
        f"🇷🇺 Rus: {lang_counts.get('ru', 0)}\n"
        f"🇬🇧 Ingliz: {lang_counts.get('en', 0)}\n"
    )
    await message.answer(text, parse_mode="HTML")


@router.message(F.text == "🏠 Bot menyusi")
async def go_to_user_menu(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    from keyboards.user_kb import main_menu_keyboard
    await state.clear()
    await message.answer("🏠 Bot menyusiga o'tdingiz.", reply_markup=main_menu_keyboard("uz"))


@router.callback_query(F.data == "admin_cancel")
async def admin_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
    await call.answer()


@router.callback_query(F.data == "admin_back")
async def admin_back(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.message.answer("⬅️ Admin menyusi:", reply_markup=admin_main_keyboard())
    await call.answer()
