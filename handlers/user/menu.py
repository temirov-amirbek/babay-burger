"""
handlers/user/menu.py — Asosiy menyu va statik sahifalar
"""
from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from database.models import User
from keyboards.user_kb import main_menu_keyboard
from locales import _

router = Router(name="menu")

# Barcha tillardagi tugma matnlari
ORDER_BUTTONS   = ["🍔 Buyurtma berish", "🍔 Сделать заказ",   "🍔 Place an Order"]
ORDERS_BUTTONS  = ["📦 Buyurtmalarim",   "📦 Мои заказы",      "📦 My Orders"]
ABOUT_BUTTONS   = ["ℹ️ Biz haqimizda",  "ℹ️ О нас",           "ℹ️ About Us"]
CONTACT_BUTTONS = ["📞 Aloqa",           "📞 Контакты",         "📞 Contact"]
MENU_BUTTONS    = ["🏠 Menyu",           "🏠 Меню",             "🏠 Menu"]


@router.message(F.text.in_(MENU_BUTTONS))
async def main_menu(message: Message, state: FSMContext, lang: str, db_user: User | None):
    await state.clear()
    await message.answer(
        _("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )


@router.message(F.text.in_(ABOUT_BUTTONS))
async def about_page(message: Message, lang: str):
    await message.answer(
        _("about_text", lang),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )


@router.message(F.text.in_(CONTACT_BUTTONS))
async def contact_page(message: Message, lang: str):
    await message.answer(
        _("contact_text", lang),
        parse_mode="HTML",
        disable_web_page_preview=True,
    )
