"""
handlers/user/ordering.py — Buyurtma berish to'liq oqimi
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from database.database import AsyncSession
from database.models import User, OrderStatus
from services.product_service import ProductService
from services.order_service import CartService, OrderService
from services.promo_service import PromoService
from services.user_service import UserService
from states import OrderStates
from keyboards.user_kb import (
    categories_keyboard, products_keyboard, product_detail_keyboard,
    cart_keyboard, confirm_order_keyboard, main_menu_keyboard,
    address_keyboard, skip_keyboard, cancel_keyboard,
)
from locales import _
from utils.helpers import (
    format_price, format_cart_items, get_order_status_text,
    build_order_confirmation_text,
)
from config import config

router = Router(name="ordering")

ORDER_BUTTONS = ["🍔 Buyurtma berish", "🍔 Сделать заказ", "🍔 Place an Order"]
BACK_BUTTONS  = ["⬅️ Orqaga", "⬅️ Назад", "⬅️ Back"]
CANCEL_BUTTONS = ["❌ Bekor qilish", "❌ Отмена", "❌ Cancel"]


# ─── Buyurtma boshlash ────────────────────────────────────────────────────────

@router.message(F.text.in_(ORDER_BUTTONS))
async def start_order(message: Message, state: FSMContext, session: AsyncSession, lang: str, db_user: User | None):
    if not db_user or not db_user.phone:
        await message.answer("❗ Avval ro'yxatdan o'ting. /start")
        return

    product_service = ProductService(session)
    categories = await product_service.get_categories()

    await state.set_state(OrderStates.choosing_category)
    await message.answer(
        _("choose_category", lang),
        reply_markup=categories_keyboard(categories, lang),
    )


# ─── Kategoriya tanlash ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("cat:"), OrderStates.choosing_category)
async def choose_category(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str
):
    cat_id = int(call.data.split(":")[1])

    product_service = ProductService(session)
    category = await product_service.get_category(cat_id)
    products = await product_service.get_products_by_category(cat_id)

    await state.update_data(current_category=cat_id)
    await state.set_state(OrderStates.choosing_product)

    if not products:
        await call.answer(_("no_products", lang), show_alert=True)
        return

    await call.message.edit_text(
        _("choose_product", lang, category=category.get_name(lang)),
        reply_markup=products_keyboard(products, cat_id, lang),
    )
    await call.answer()


# ─── Mahsulot tanlash ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("prod:"))
async def choose_product(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str
):
    prod_id = int(call.data.split(":")[1])
    product_service = ProductService(session)
    product = await product_service.get_product(prod_id)

    if not product:
        await call.answer("❌ Mahsulot topilmadi.", show_alert=True)
        return

    await state.update_data(current_product=prod_id)

    desc = product.get_description(lang) or ""
    text = _("product_card", lang,
        name=product.get_name(lang),
        description=desc,
        price=product.formatted_price(),
    )

    if product.photo_id:
        await call.message.answer_photo(
            photo=product.photo_id,
            caption=text,
            reply_markup=product_detail_keyboard(prod_id, lang),
        )
    else:
        await call.message.answer(
            text,
            reply_markup=product_detail_keyboard(prod_id, lang),
        )
    await call.answer()


# ─── Savatga qo'shish ─────────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("add_cart:"))
async def add_to_cart(
    call: CallbackQuery, state: FSMContext, session: AsyncSession,
    lang: str, db_user: User
):
    prod_id = int(call.data.split(":")[1])
    product_service = ProductService(session)
    cart_service = CartService(session)

    product = await product_service.get_product(prod_id)
    if not product:
        await call.answer("❌ Mahsulot topilmadi.", show_alert=True)
        return

    await cart_service.add_to_cart(db_user.id, prod_id)

    await call.answer(
        _("added_to_cart", lang, name=product.get_name(lang)),
        show_alert=True,
    )


# ─── Savat ko'rish ────────────────────────────────────────────────────────────

async def show_cart(message_or_call, session: AsyncSession, lang: str, user_id: int, edit: bool = False):
    cart_service = CartService(session)
    cart_items = await cart_service.get_cart(user_id)

    if not cart_items:
        text = _("cart_empty", lang)
        kb = None
    else:
        items_text = format_cart_items(cart_items, lang)
        total = sum(i.product.price * i.quantity for i in cart_items)
        delivery_fee = cart_service.calculate_delivery_fee(total)

        text = _("cart_title", lang) + items_text
        text += _("cart_total", lang, total=format_price(total))

        if delivery_fee == 0:
            text += "\n" + _("cart_free_del", lang)
        else:
            text += _("cart_delivery", lang, fee=format_price(delivery_fee))

        kb = cart_keyboard(cart_items, lang)

    if edit and hasattr(message_or_call, "message"):
        try:
            await message_or_call.message.edit_text(text, reply_markup=kb)
        except Exception:
            await message_or_call.message.answer(text, reply_markup=kb)
    else:
        target = message_or_call if isinstance(message_or_call, Message) else message_or_call.message
        await target.answer(text, reply_markup=kb)


# ─── Savat tugmasi (asosiy menyudan) ─────────────────────────────────────────

@router.callback_query(F.data == "back_to_categories")
async def back_to_categories(
    call: CallbackQuery, state: FSMContext, session: AsyncSession, lang: str
):
    product_service = ProductService(session)
    categories = await product_service.get_categories()
    await state.set_state(OrderStates.choosing_category)
    await call.message.edit_text(
        _("choose_category", lang),
        reply_markup=categories_keyboard(categories, lang),
    )
    await call.answer()


@router.callback_query(F.data == "back_to_menu")
async def back_to_main_menu(call: CallbackQuery, state: FSMContext, lang: str):
    await state.clear()
    await call.message.answer(
        _("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await call.answer()


# ─── Savat ±  tugmalari ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("cart_plus:"))
async def cart_increase(
    call: CallbackQuery, session: AsyncSession, lang: str, db_user: User
):
    item_id = int(call.data.split(":")[1])
    cart_service = CartService(session)
    await cart_service.increase_quantity(item_id)
    await show_cart(call, session, lang, db_user.id, edit=True)
    await call.answer()


@router.callback_query(F.data.startswith("cart_minus:"))
async def cart_decrease(
    call: CallbackQuery, session: AsyncSession, lang: str, db_user: User
):
    item_id = int(call.data.split(":")[1])
    cart_service = CartService(session)
    await cart_service.decrease_quantity(item_id)
    await show_cart(call, session, lang, db_user.id, edit=True)
    await call.answer()


@router.callback_query(F.data == "clear_cart")
async def clear_cart_handler(
    call: CallbackQuery, session: AsyncSession, lang: str, db_user: User
):
    cart_service = CartService(session)
    await cart_service.clear_cart(db_user.id)
    await call.message.edit_text(_("cart_cleared", lang))
    await call.answer()


# ─── Checkout ─────────────────────────────────────────────────────────────────

@router.callback_query(F.data == "checkout")
async def start_checkout(
    call: CallbackQuery, state: FSMContext, session: AsyncSession,
    lang: str, db_user: User
):
    cart_service = CartService(session)
    cart_items = await cart_service.get_cart(db_user.id)

    if not cart_items:
        await call.answer(_("cart_empty", lang), show_alert=True)
        return

    total = sum(i.product.price * i.quantity for i in cart_items)
    if total < config.delivery.min_order:
        await call.answer(
            _("min_order_err", lang,
              amount=format_price(config.delivery.min_order),
              current=format_price(total)),
            show_alert=True,
        )
        return

    await state.set_state(OrderStates.entering_address)
    await call.message.answer(
        _("enter_address", lang),
        reply_markup=address_keyboard(lang),
    )
    await call.answer()


# ─── Manzil qabul qilish ─────────────────────────────────────────────────────

@router.message(OrderStates.entering_address, F.location)
async def receive_location(message: Message, state: FSMContext, lang: str):
    lat = message.location.latitude
    lon = message.location.longitude
    address = f"📍 {lat:.5f}, {lon:.5f}"
    await state.update_data(address=address, lat=lat, lon=lon)
    await ask_promo(message, state, lang)


@router.message(OrderStates.entering_address, F.text)
async def receive_address_text(message: Message, state: FSMContext, lang: str):
    if message.text in BACK_BUTTONS or message.text in CANCEL_BUTTONS:
        await state.clear()
        await message.answer(_("main_menu", lang), reply_markup=main_menu_keyboard(lang))
        return

    await state.update_data(address=message.text, lat=None, lon=None)
    await ask_promo(message, state, lang)


async def ask_promo(message: Message, state: FSMContext, lang: str):
    await state.set_state(OrderStates.entering_promo)
    await message.answer(
        _("promo_question", lang),
        reply_markup=skip_keyboard(_("btn_skip_promo", lang), _("btn_cancel", lang)),
    )


# ─── Promo kod ────────────────────────────────────────────────────────────────

@router.message(OrderStates.entering_promo)
async def receive_promo(
    message: Message, state: FSMContext, session: AsyncSession,
    lang: str, db_user: User
):
    skip_texts = ["⏩ O'tkazib yuborish", "⏩ Пропустить", "⏩ Skip"]

    if message.text in CANCEL_BUTTONS:
        await state.clear()
        await message.answer(_("main_menu", lang), reply_markup=main_menu_keyboard(lang))
        return

    promo_service = PromoService(session)
    cart_service = CartService(session)

    discount = 0
    promo_code = None

    if message.text not in skip_texts:
        cart_items = await cart_service.get_cart(db_user.id)
        total = sum(i.product.price * i.quantity for i in cart_items)

        is_valid, promo = await promo_service.validate_promo(message.text)
        if is_valid and promo:
            discount = await promo_service.apply_promo(message.text, total)
            promo_code = message.text.upper()
            await message.answer(
                _("promo_applied", lang, discount=format_price(discount))
            )
        else:
            await message.answer(_("promo_invalid", lang))
            return

    await state.update_data(discount=discount, promo_code=promo_code)
    await state.set_state(OrderStates.entering_comment)
    await message.answer(
        _("comment_question", lang),
        reply_markup=skip_keyboard(_("btn_no_comment", lang), _("btn_cancel", lang)),
    )


# ─── Izoh ────────────────────────────────────────────────────────────────────

@router.message(OrderStates.entering_comment)
async def receive_comment(
    message: Message, state: FSMContext, session: AsyncSession,
    lang: str, db_user: User
):
    no_comment_texts = ["➡️ Yo'q", "➡️ Нет", "➡️ No"]

    if message.text in CANCEL_BUTTONS:
        await state.clear()
        await message.answer(_("main_menu", lang), reply_markup=main_menu_keyboard(lang))
        return

    comment = None if message.text in no_comment_texts else message.text
    await state.update_data(comment=comment)

    # Tasdiqlash
    await show_order_confirmation(message, state, session, lang, db_user)


async def show_order_confirmation(
    message: Message, state: FSMContext, session: AsyncSession,
    lang: str, db_user: User
):
    data = await state.get_data()
    cart_service = CartService(session)
    cart_items = await cart_service.get_cart(db_user.id)

    total = sum(i.product.price * i.quantity for i in cart_items)
    delivery_fee = cart_service.calculate_delivery_fee(total)
    discount = data.get("discount", 0)
    address = data.get("address", "—")

    text = build_order_confirmation_text(
        order=None,
        cart_items=cart_items,
        delivery_address=address,
        delivery_fee=delivery_fee,
        discount=discount,
        lang=lang,
    )

    await state.set_state(OrderStates.confirming_order)
    await message.answer(
        text,
        reply_markup=confirm_order_keyboard(lang),
        parse_mode="HTML",
    )


# ─── Tasdiqlash / Bekor qilish ────────────────────────────────────────────────

@router.callback_query(F.data == "confirm_order", OrderStates.confirming_order)
async def confirm_order(
    call: CallbackQuery, state: FSMContext, session: AsyncSession,
    lang: str, db_user: User
):
    from aiogram import Bot
    data = await state.get_data()

    cart_service = CartService(session)
    order_service = OrderService(session)
    cart_items = await cart_service.get_cart(db_user.id)

    if not cart_items:
        await call.answer(_("cart_empty", lang), show_alert=True)
        return

    total = sum(i.product.price * i.quantity for i in cart_items)
    delivery_fee = cart_service.calculate_delivery_fee(total)

    order = await order_service.create_order(
        user_id=db_user.id,
        cart_items=cart_items,
        delivery_address=data.get("address", "—"),
        delivery_fee=delivery_fee,
        discount=data.get("discount", 0),
        promo_code=data.get("promo_code"),
        delivery_lat=data.get("lat"),
        delivery_lon=data.get("lon"),
        comment=data.get("comment"),
    )

    await cart_service.clear_cart(db_user.id)
    await state.clear()

    # Foydalanuvchiga xabar
    await call.message.edit_text(
        _("order_placed", lang, order_id=order.id),
        reply_markup=None,
    )
    await call.message.answer(
        _("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )

    # Adminga xabar yuborish
    bot = call.bot
    await notify_admins_new_order(bot, order, session)
    await call.answer()


async def notify_admins_new_order(bot, order, session: AsyncSession):
    """Adminga yangi buyurtma haqida xabar yuborish."""
    from utils.helpers import build_order_card_for_admin
    from keyboards.admin_kb import order_management_keyboard

    order_service = OrderService(session)
    full_order = await order_service.get_order(order.id)

    text = build_order_card_for_admin(full_order)
    kb = order_management_keyboard(full_order.id, full_order.status)

    for admin_id in config.bot.admin_ids:
        try:
            msg = await bot.send_message(
                admin_id,
                text,
                reply_markup=kb,
                parse_mode="HTML",
            )
            await order_service.set_admin_message_id(order.id, msg.message_id)
        except Exception as e:
            logger.error(f"Admin {admin_id} ga xabar yuborib bo'lmadi: {e}")

    # Kanal bor bo'lsa, u yerga ham yuborish
    if config.bot.orders_channel_id:
        try:
            await bot.send_message(
                config.bot.orders_channel_id,
                text,
                reply_markup=kb,
                parse_mode="HTML",
            )
        except Exception as e:
            logger.error(f"Kanalga xabar yuborib bo'lmadi: {e}")


@router.callback_query(F.data == "cancel_order")
async def cancel_order_handler(
    call: CallbackQuery, state: FSMContext, lang: str
):
    await state.clear()
    await call.message.edit_text(_("cart_cleared", lang))
    await call.message.answer(
        _("main_menu", lang),
        reply_markup=main_menu_keyboard(lang),
    )
    await call.answer()


@router.callback_query(F.data == "edit_order")
async def edit_order_handler(
    call: CallbackQuery, state: FSMContext, session: AsyncSession,
    lang: str, db_user: User
):
    await state.set_state(OrderStates.choosing_category)
    await show_cart(call, session, lang, db_user.id, edit=True)
    await call.answer()
