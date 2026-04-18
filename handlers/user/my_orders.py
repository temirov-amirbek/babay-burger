"""
handlers/user/my_orders.py — Foydalanuvchining buyurtmalari
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery

from database.database import AsyncSession
from database.models import User
from services.order_service import OrderService
from keyboards.user_kb import orders_list_keyboard, main_menu_keyboard
from locales import _
from utils.helpers import format_price, get_order_status_text, format_datetime

router = Router(name="my_orders")

ORDERS_BUTTONS = ["📦 Buyurtmalarim", "📦 Мои заказы", "📦 My Orders"]


@router.message(F.text.in_(ORDERS_BUTTONS))
async def my_orders(message: Message, session: AsyncSession, lang: str, db_user: User):
    if not db_user:
        return

    order_service = OrderService(session)
    orders = await order_service.get_user_orders(db_user.id, limit=10)

    if not orders:
        await message.answer(_("no_orders", lang))
        return

    text = _("my_orders_title", lang)
    for order in orders:
        status_text = get_order_status_text(order.status, lang)
        text += _(
            "order_item", lang,
            id=order.id,
            date=format_datetime(order.created_at),
            status_emoji=order.status_emoji(),
            status=status_text,
            amount=format_price(order.final_amount),
        )

    await message.answer(
        text,
        reply_markup=orders_list_keyboard(orders, lang),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("order_detail:"))
async def order_detail(call: CallbackQuery, session: AsyncSession, lang: str):
    order_id = int(call.data.split(":")[1])
    order_service = OrderService(session)
    order = await order_service.get_order(order_id)

    if not order:
        await call.answer("❌ Buyurtma topilmadi.", show_alert=True)
        return

    from utils.helpers import format_order_items, get_order_status_text, format_price
    items_text = format_order_items(order.items, lang)
    status_text = get_order_status_text(order.status, lang)

    text = (
        f"🧾 <b>Buyurtma #{order.id}</b>\n"
        f"📅 {format_datetime(order.created_at)}\n"
        f"{order.status_emoji()} Holat: <b>{status_text}</b>\n\n"
        f"🛒 Mahsulotlar:\n{items_text}\n\n"
        f"📍 Manzil: {order.delivery_address or '—'}\n"
        f"💰 Jami: {format_price(order.total_amount)}\n"
        f"🚚 Yetkazib berish: {format_price(order.delivery_fee)}\n"
        f"💳 To'lov: {format_price(order.final_amount)}"
    )

    await call.message.answer(text, parse_mode="HTML")
    await call.answer()
