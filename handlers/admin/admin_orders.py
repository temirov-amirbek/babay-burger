"""
handlers/admin/admin_orders.py — Admin buyurtmalar boshqaruvi
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from loguru import logger

from database.database import AsyncSession
from database.models import OrderStatus
from services.order_service import OrderService
from keyboards.admin_kb import admin_main_keyboard, order_management_keyboard
from utils.helpers import build_order_card_for_admin, format_price
from config import config

router = Router(name="admin_orders")


def is_admin(user_id: int) -> bool:
    return user_id in config.bot.admin_ids


@router.message(F.text == "📥 Buyurtmalar")
async def view_orders(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return

    order_service = OrderService(session)
    orders = await order_service.get_pending_orders()

    if not orders:
        await message.answer(
            "📭 Hozircha yangi buyurtmalar yo'q.",
            reply_markup=admin_main_keyboard(),
        )
        return

    await message.answer(
        f"📥 <b>Kutilayotgan buyurtmalar: {len(orders)} ta</b>",
        parse_mode="HTML",
    )

    for order in orders:
        text = build_order_card_for_admin(order)
        kb = order_management_keyboard(order.id, order.status)
        await message.answer(text, reply_markup=kb, parse_mode="HTML")


# ─── Holat o'zgartirish ───────────────────────────────────────────────────────

STATUS_MAP = {
    "confirm":   OrderStatus.CONFIRMED,
    "delivering": OrderStatus.DELIVERING,
    "delivered": OrderStatus.DELIVERED,
    "cancel":    OrderStatus.CANCELLED,
}

STATUS_MESSAGES = {
    OrderStatus.CONFIRMED:  "✅ Buyurtma #{id} tasdiqlandi!",
    OrderStatus.DELIVERING: "🚚 Buyurtma #{id} yetkazilmoqda!",
    OrderStatus.DELIVERED:  "✔️ Buyurtma #{id} yetkazildi!",
    OrderStatus.CANCELLED:  "❌ Buyurtma #{id} bekor qilindi.",
}

USER_NOTIFICATIONS = {
    OrderStatus.CONFIRMED: {
        "uz": "✅ Buyurtma #{id} tasdiqlandi! Tez orada yetkaziladi.",
        "ru": "✅ Заказ #{id} подтверждён! Скоро будет доставлен.",
        "en": "✅ Order #{id} confirmed! Will be delivered soon.",
    },
    OrderStatus.DELIVERING: {
        "uz": "🚚 Buyurtma #{id} yetkazilmoqda! Kuryer yo'lda.",
        "ru": "🚚 Заказ #{id} доставляется! Курьер в пути.",
        "en": "🚚 Order #{id} is on its way! Courier is coming.",
    },
    OrderStatus.DELIVERED: {
        "uz": "✔️ Buyurtma #{id} yetkazildi! Rahmat, yana keling! 🍔",
        "ru": "✔️ Заказ #{id} доставлен! Спасибо, приходите ещё! 🍔",
        "en": "✔️ Order #{id} delivered! Thank you, come again! 🍔",
    },
    OrderStatus.CANCELLED: {
        "uz": "❌ Buyurtma #{id} bekor qilindi. Kechirasiz.",
        "ru": "❌ Заказ #{id} отменён. Извините.",
        "en": "❌ Order #{id} has been cancelled. We apologize.",
    },
}


@router.callback_query(F.data.startswith("admin_order:"))
async def update_order_status(
    call: CallbackQuery, session: AsyncSession
):
    if not is_admin(call.from_user.id):
        await call.answer("⛔️ Ruxsat yo'q.", show_alert=True)
        return

    parts = call.data.split(":")
    action = parts[1]
    order_id = int(parts[2])

    new_status = STATUS_MAP.get(action)
    if not new_status:
        await call.answer("❌ Noma'lum holat.", show_alert=True)
        return

    order_service = OrderService(session)
    order = await order_service.update_order_status(order_id, new_status)

    if not order:
        await call.answer("❌ Buyurtma topilmadi.", show_alert=True)
        return

    # Admin xabarni yangilash
    admin_msg = STATUS_MESSAGES.get(new_status, "Holat yangilandi").format(id=order_id)

    try:
        new_kb = order_management_keyboard(order.id, new_status)
        await call.message.edit_reply_markup(reply_markup=new_kb)
    except Exception:
        pass

    await call.answer(admin_msg, show_alert=True)

    # Foydalanuvchiga xabar
    user_lang = order.user.language if order.user else "uz"
    user_msgs = USER_NOTIFICATIONS.get(new_status, {})
    user_msg = user_msgs.get(user_lang, user_msgs.get("uz", "")).format(id=order_id)

    if user_msg:
        try:
            await call.bot.send_message(
                order.user_id,
                user_msg,
            )
        except Exception as e:
            logger.error(f"Foydalanuvchi {order.user_id} ga xabar yuborib bo'lmadi: {e}")

    logger.info(
        f"Admin {call.from_user.id} → Buyurtma #{order_id} holati: {new_status}"
    )
