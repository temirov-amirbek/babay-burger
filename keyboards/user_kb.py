"""
keyboards/user_kb.py — Foydalanuvchi klaviaturalari
"""
from typing import List, Optional
from aiogram.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton,
    KeyboardButtonRequestContact,
)
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder

from database.models import Category, Product, Order, OrderStatus
from locales import _, LANG_NAMES


# ─── Reply Keyboards ──────────────────────────────────────────────────────────

def contact_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Telefon raqam yuborish klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(
            text=_(  "send_contact", lang),
            request_contact=True,
        )
    )
    return builder.as_markup(resize_keyboard=True, one_time_keyboard=True)


def main_menu_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Asosiy menyu klaviaturasi."""
    builder = ReplyKeyboardBuilder()
    builder.row(
        KeyboardButton(text=_("btn_order", lang)),
        KeyboardButton(text=_("btn_orders", lang)),
    )
    builder.row(
        KeyboardButton(text=_("btn_about", lang)),
        KeyboardButton(text=_("btn_contact", lang)),
    )
    builder.row(
        KeyboardButton(text=_("btn_lang", lang)),
    )
    return builder.as_markup(resize_keyboard=True)


def back_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Orqaga tugmasi."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=_("btn_back", lang)))
    return builder.as_markup(resize_keyboard=True)


def cancel_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Bekor qilish tugmasi."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=_("btn_cancel", lang)))
    return builder.as_markup(resize_keyboard=True)


def address_keyboard(lang: str = "uz") -> ReplyKeyboardMarkup:
    """Manzil yuborish klaviaturasi (location + back)."""
    builder = ReplyKeyboardBuilder()
    builder.add(
        KeyboardButton(text="📍 Lokatsiya yuborish", request_location=True)
    )
    builder.add(KeyboardButton(text=_("btn_back", lang)))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


def skip_keyboard(skip_text: str, cancel_text: str) -> ReplyKeyboardMarkup:
    """O'tkazib yuborish + bekor qilish."""
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text=skip_text))
    builder.add(KeyboardButton(text=cancel_text))
    builder.adjust(2)
    return builder.as_markup(resize_keyboard=True)


# ─── Inline Keyboards ─────────────────────────────────────────────────────────

def language_keyboard() -> InlineKeyboardMarkup:
    """Til tanlash inline klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for code, name in LANG_NAMES.items():
        builder.add(
            InlineKeyboardButton(text=name, callback_data=f"set_lang:{code}")
        )
    builder.adjust(1)
    return builder.as_markup()


def categories_keyboard(
    categories: List[Category], lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Kategoriyalar inline klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for cat in categories:
        builder.add(
            InlineKeyboardButton(
                text=f"{cat.emoji} {cat.get_name(lang)}",
                callback_data=f"cat:{cat.id}",
            )
        )
    builder.add(
        InlineKeyboardButton(
            text=_("btn_back", lang), callback_data="back_to_menu"
        )
    )
    builder.adjust(2)
    return builder.as_markup()


def products_keyboard(
    products: List[Product], category_id: int, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Mahsulotlar inline klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for product in products:
        builder.add(
            InlineKeyboardButton(
                text=f"{product.get_name(lang)} — {product.formatted_price()}",
                callback_data=f"prod:{product.id}",
            )
        )
    builder.add(
        InlineKeyboardButton(
            text=_("btn_back", lang),
            callback_data="back_to_categories",
        )
    )
    builder.adjust(1)
    return builder.as_markup()


def product_detail_keyboard(
    product_id: int, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Mahsulot detail inline klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("btn_add_cart", lang),
            callback_data=f"add_cart:{product_id}",
        )
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_back", lang),
            callback_data="back_to_products",
        )
    )
    return builder.as_markup()


def cart_keyboard(
    cart_items: list, lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Savat inline klaviaturasi."""
    builder = InlineKeyboardBuilder()

    # Har bir mahsulot uchun ±/o'chirish
    for item in cart_items:
        prod_name = item.product.get_name(lang)[:20]
        builder.row(
            InlineKeyboardButton(
                text="➖", callback_data=f"cart_minus:{item.id}"
            ),
            InlineKeyboardButton(
                text=f"{prod_name} ({item.quantity})",
                callback_data=f"cart_item:{item.id}",
            ),
            InlineKeyboardButton(
                text="➕", callback_data=f"cart_plus:{item.id}"
            ),
        )

    builder.row(
        InlineKeyboardButton(
            text=_("btn_checkout", lang),
            callback_data="checkout",
        ),
        InlineKeyboardButton(
            text=_("btn_clear_cart", lang),
            callback_data="clear_cart",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_back", lang),
            callback_data="back_to_categories",
        )
    )
    return builder.as_markup()


def confirm_order_keyboard(lang: str = "uz") -> InlineKeyboardMarkup:
    """Buyurtmani tasdiqlash inline klaviaturasi."""
    builder = InlineKeyboardBuilder()
    builder.row(
        InlineKeyboardButton(
            text=_("btn_confirm", lang),
            callback_data="confirm_order",
        ),
        InlineKeyboardButton(
            text=_("btn_edit", lang),
            callback_data="edit_order",
        ),
    )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_cancel", lang),
            callback_data="cancel_order",
        )
    )
    return builder.as_markup()


def orders_list_keyboard(
    orders: List[Order], lang: str = "uz"
) -> InlineKeyboardMarkup:
    """Buyurtmalar ro'yxati klaviaturasi."""
    builder = InlineKeyboardBuilder()
    for order in orders[:10]:
        builder.row(
            InlineKeyboardButton(
                text=f"#{order.id} | {order.status_emoji()} | {order.final_amount:,} so'm",
                callback_data=f"order_detail:{order.id}",
            )
        )
    builder.row(
        InlineKeyboardButton(
            text=_("btn_menu", lang),
            callback_data="back_to_menu",
        )
    )
    return builder.as_markup()
