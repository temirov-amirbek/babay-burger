"""
keyboards/admin_kb.py — Admin klaviaturalari
"""
from typing import List
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.models import Order, Product, Category, OrderStatus


# ─── Reply Keyboards ──────────────────────────────────────────────────────────

def admin_main_keyboard() -> ReplyKeyboardMarkup:
    """Admin asosiy menyu klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="📥 Buyurtmalar"),
        KeyboardButton(text="📊 Statistika"),
    )
    builder.row(
        KeyboardButton(text="➕ Mahsulot qo'shish"),
        KeyboardButton(text="✏️ Mahsulotlar"),
    )
    builder.row(
        KeyboardButton(text="🎟 Promo kodlar"),
        KeyboardButton(text="📢 Broadcast"),
    )
    builder.row(
        KeyboardButton(text="👥 Foydalanuvchilar"),
        KeyboardButton(text="🏠 Bot menyusi"),
    )
    return builder.as_markup(resize_keyboard=True)


def admin_cancel_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="❌ Bekor qilish"))
    return builder.as_markup(resize_keyboard=True)


def admin_skip_keyboard() -> ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text="⏩ O'tkazish"),
        KeyboardButton(text="❌ Bekor qilish"),
    )
    return builder.as_markup(resize_keyboard=True)


# ─── Inline Keyboards ─────────────────────────────────────────────────────────

def order_management_keyboard(order_id: int, status: str) -> InlineKeyboardMarkup:
    """Buyurtma boshqaruv klaviaturasi (admin uchun)."""
    builder = InlineKeyboardBuilder()

    if status == OrderStatus.PENDING:
        builder.row(
            InlineKeyboardButton(
                text="✅ Tasdiqlash",
                callback_data=f"admin_order:confirm:{order_id}",
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data=f"admin_order:cancel:{order_id}",
            ),
        )
    elif status == OrderStatus.CONFIRMED:
        builder.row(
            InlineKeyboardButton(
                text="🚚 Yetkazilmoqda",
                callback_data=f"admin_order:delivering:{order_id}",
            ),
            InlineKeyboardButton(
                text="❌ Bekor qilish",
                callback_data=f"admin_order:cancel:{order_id}",
            ),
        )
    elif status == OrderStatus.DELIVERING:
        builder.row(
            InlineKeyboardButton(
                text="✔️ Yetkazildi",
                callback_data=f"admin_order:delivered:{order_id}",
            )
        )

    return builder.as_markup()


def products_list_keyboard(products: List[Product]) -> InlineKeyboardMarkup:
    """Mahsulotlar ro'yxati (admin uchun)."""
    builder = InlineKeyboardBuilder()
    for p in products:
        status = "✅" if p.is_available else "❌"
        builder.row(
            InlineKeyboardButton(
                text=f"{status} {p.name_uz} — {p.price:,} so'm",
                callback_data=f"admin_prod:{p.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_back")
    )
    return builder.as_markup()


def product_edit_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """Mahsulotni tahrirlash klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="📝 Nomi (UZ)",
            callback_data=f"edit_prod:name_uz:{product_id}",
        ),
        InlineKeyboardButton(
            text="📝 Nomi (RU)",
            callback_data=f"edit_prod:name_ru:{product_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="💰 Narxi",
            callback_data=f"edit_prod:price:{product_id}",
        ),
        InlineKeyboardButton(
            text="🖼 Rasm",
            callback_data=f"edit_prod:photo:{product_id}",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text="🔄 Holat (on/off)",
            callback_data=f"edit_prod:toggle:{product_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🗑 O'chirish",
            callback_data=f"edit_prod:delete:{product_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(text="⬅️ Orqaga", callback_data="admin_products")
    )
    return builder.as_markup()


def categories_admin_keyboard(categories: List[Category]) -> InlineKeyboardMarkup:
    """Kategoriyalar tanlash (admin - mahsulot qo'shish uchun)."""
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.add(
            InlineKeyboardButton(
                text=f"{cat.emoji} {cat.name_uz}",
                callback_data=f"admin_cat:{cat.id}",
            )
        )
    builder.add(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")
    )
    builder.adjust(2)
    return builder.as_markup()


def confirm_delete_keyboard(product_id: int) -> InlineKeyboardMarkup:
    """O'chirishni tasdiqlash."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Ha, o'chirish",
            callback_data=f"confirm_delete:{product_id}",
        ),
        InlineKeyboardButton(
            text="❌ Yo'q",
            callback_data=f"admin_prod:{product_id}",
        ),
    )
    return builder.as_markup()


def broadcast_target_keyboard() -> InlineKeyboardMarkup:
    """Broadcast maqsadi tanlash."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="🌍 Barcha foydalanuvchilar",
            callback_data="broadcast_target:all",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text="🇺🇿 O'zbek tilli",
            callback_data="broadcast_target:uz",
        ),
        InlineKeyboardButton(
            text="🇷🇺 Rus tilli",
            callback_data="broadcast_target:ru",
        ),
        InlineKeyboardButton(
            text="🇬🇧 Ingliz tilli",
            callback_data="broadcast_target:en",
        ),
    )
    builder.row(
        InlineKeyboardButton(text="❌ Bekor qilish", callback_data="admin_cancel")
    )
    return builder.as_markup()


def confirm_broadcast_keyboard() -> InlineKeyboardMarkup:
    """Broadcastni tasdiqlash."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text="✅ Yuborish", callback_data="confirm_broadcast"
        ),
        InlineKeyboardButton(
            text="❌ Bekor qilish", callback_data="admin_cancel"
        ),
    )
    return builder.as_markup()
