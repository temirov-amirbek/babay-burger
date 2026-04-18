"""
utils/helpers.py — Yordamchi funksiyalar
"""
from datetime import datetime
from typing import Optional, List
from database.models import Order, OrderItem, CartItem, OrderStatus
from locales import _


def format_price(amount: int) -> str:
    """Narxni formatlash: 32000 → '32 000 so'm'"""
    return f"{amount:,} so'm".replace(",", " ")


def format_order_items(items: List[OrderItem], lang: str = "uz") -> str:
    """Buyurtma mahsulotlarini matn ko'rinishida formatlash."""
    lines = []
    for item in items:
        subtotal = item.product_price * item.quantity
        lines.append(
            f"  • {item.product_name} x{item.quantity} = {format_price(subtotal)}"
        )
    return "\n".join(lines)


def format_cart_items(items: List[CartItem], lang: str = "uz") -> str:
    """Savat mahsulotlarini matn ko'rinishida formatlash."""
    lines = []
    for item in items:
        name = item.product.get_name(lang)
        price = item.product.price * item.quantity
        lines.append(_("cart_item", lang, name=name, qty=item.quantity, price=format_price(price)))
    return "".join(lines)


def get_order_status_text(status: str, lang: str = "uz") -> str:
    """Buyurtma holatini tarjima qilish."""
    status_map = {
        OrderStatus.PENDING:    _("order_status_pending", lang),
        OrderStatus.CONFIRMED:  _("order_status_confirmed", lang),
        OrderStatus.DELIVERING: _("order_status_delivering", lang),
        OrderStatus.DELIVERED:  _("order_status_delivered", lang),
        OrderStatus.CANCELLED:  _("order_status_cancelled", lang),
    }
    return status_map.get(status, status)


def build_order_card_for_admin(order: Order) -> str:
    """Admin uchun buyurtma kartasi."""
    items_text = "\n".join(
        f"  {i+1}. {item.product_name} x{item.quantity} — {format_price(item.product_price * item.quantity)}"
        for i, item in enumerate(order.items)
    )

    address = order.delivery_address or "—"
    if order.delivery_lat and order.delivery_lon:
        address += f"\n  📌 https://maps.google.com/?q={order.delivery_lat},{order.delivery_lon}"

    promo_line = f"\n🎟 Promo: {order.promo_code} (−{format_price(order.discount)})" if order.promo_code else ""
    comment_line = f"\n💬 Izoh: {order.comment}" if order.comment else ""

    return (
        f"🆕 <b>YANGI BUYURTMA #{order.id}</b>\n"
        f"{'─'*30}\n"
        f"👤 Ism: <b>{order.user.full_name}</b>\n"
        f"📱 Tel: <b>{order.user.phone or '—'}</b>\n"
        f"📍 Manzil: {address}\n"
        f"{'─'*30}\n"
        f"🛒 <b>Mahsulotlar:</b>\n{items_text}\n"
        f"{'─'*30}\n"
        f"💰 Jami: {format_price(order.total_amount)}\n"
        f"🚚 Yetkazib berish: {format_price(order.delivery_fee)}\n"
        f"{promo_line}"
        f"\n💳 <b>To'lov: {format_price(order.final_amount)}</b>"
        f"{comment_line}\n"
        f"{'─'*30}\n"
        f"⏰ {order.created_at.strftime('%d.%m.%Y %H:%M')}"
    )


def build_order_confirmation_text(
    order: Order,
    cart_items: List[CartItem],
    delivery_address: str,
    delivery_fee: int,
    discount: int,
    lang: str = "uz",
) -> str:
    """Foydalanuvchi uchun buyurtma tasdiq matni."""
    items_text = ""
    total = 0
    for item in cart_items:
        name = item.product.get_name(lang)
        price = item.product.price * item.quantity
        total += price
        items_text += f"  • {name} x{item.quantity} = {format_price(price)}\n"

    promo_line = ""
    if discount > 0:
        promo_line = _("promo_line", lang, discount=format_price(discount))

    final = total + delivery_fee - discount

    delivery_text = format_price(delivery_fee) if delivery_fee > 0 else _("cart_free_del", lang)

    return _(
        "confirm_order", lang,
        items=items_text,
        address=delivery_address,
        total=format_price(total),
        delivery=delivery_text,
        promo=promo_line,
        final=format_price(final),
    )


def validate_name(name: str) -> bool:
    """Ismni tekshirish."""
    name = name.strip()
    return 2 <= len(name) <= 64 and not name.isdigit()


def format_datetime(dt: datetime) -> str:
    return dt.strftime("%d.%m.%Y %H:%M")


def truncate(text: str, max_len: int = 30) -> str:
    if len(text) <= max_len:
        return text
    return text[:max_len - 1] + "…"
