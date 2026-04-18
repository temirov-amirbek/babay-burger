"""
handlers/admin/admin_broadcast.py — Broadcast va Promo kod boshqaruvi
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from database.database import AsyncSession
from services.user_service import UserService
from services.promo_service import PromoService
from states import AdminBroadcastStates, AdminPromoStates
from keyboards.admin_kb import (
    admin_main_keyboard, admin_cancel_keyboard,
    broadcast_target_keyboard, confirm_broadcast_keyboard,
)
from config import config

router = Router(name="admin_broadcast")


def is_admin(user_id: int) -> bool:
    return user_id in config.bot.admin_ids


# ─── Broadcast ────────────────────────────────────────────────────────────────

@router.message(F.text == "📢 Broadcast")
async def broadcast_start(message: Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return

    await state.set_state(AdminBroadcastStates.choosing_lang)
    await message.answer(
        "📢 <b>Broadcast</b>\n\nKimga xabar yuborasiz?",
        reply_markup=broadcast_target_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("broadcast_target:"), AdminBroadcastStates.choosing_lang)
async def choose_broadcast_target(call: CallbackQuery, state: FSMContext):
    target = call.data.split(":")[1]
    await state.update_data(target=target)
    await state.set_state(AdminBroadcastStates.entering_message)

    targets = {"all": "Barcha", "uz": "O'zbek tilli", "ru": "Rus tilli", "en": "Ingliz tilli"}
    await call.message.edit_text(
        f"✅ Maqsad: <b>{targets.get(target)}</b>\n\n"
        f"📝 Xabar matnini yuboring (HTML qo'llab-quvvatlanadi):",
        parse_mode="HTML",
    )
    await call.answer()


@router.message(AdminBroadcastStates.entering_message)
async def receive_broadcast_message(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
        return

    await state.update_data(
        text=message.text,
        photo=message.photo[-1].file_id if message.photo else None,
    )
    await state.set_state(AdminBroadcastStates.confirming)

    preview = f"📋 Preview:\n\n{message.text}\n\nYuboriladimi?"
    await message.answer(preview, reply_markup=confirm_broadcast_keyboard(), parse_mode="HTML")


@router.callback_query(F.data == "confirm_broadcast", AdminBroadcastStates.confirming)
async def send_broadcast(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    target = data.get("target", "all")
    text = data.get("text", "")
    photo = data.get("photo")

    user_service = UserService(session)
    lang_filter = None if target == "all" else target
    users = await user_service.get_all_users(lang=lang_filter)

    await call.message.edit_text(f"📤 Yuborilmoqda... ({len(users)} ta foydalanuvchi)")
    await call.answer()

    success = 0
    failed = 0

    for user in users:
        try:
            if photo:
                await call.bot.send_photo(user.id, photo=photo, caption=text, parse_mode="HTML")
            else:
                await call.bot.send_message(user.id, text, parse_mode="HTML")
            success += 1
        except Exception:
            failed += 1

    await state.clear()
    await call.message.answer(
        f"✅ Broadcast yakunlandi!\n\n"
        f"✔️ Muvaffaqiyatli: {success}\n"
        f"❌ Xato: {failed}",
        reply_markup=admin_main_keyboard(),
    )
    logger.info(f"Broadcast: {success} muvaffaqiyatli, {failed} xato")


# ─── Promo Kodlar ─────────────────────────────────────────────────────────────

@router.message(F.text == "🎟 Promo kodlar")
async def list_promos(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return

    from aiogram.utils.keyboard import InlineKeyboardBuilder
    from aiogram.types import InlineKeyboardButton
    from datetime import datetime

    promo_service = PromoService(session)
    promos = await promo_service.get_all_promos()

    if not promos:
        await message.answer("📭 Promo kodlar yo'q.")
        return

    lines = []
    for p in promos:
        status = "✅" if p.is_active else "❌"
        discount_text = f"{p.discount_percent}%" if p.discount_percent else f"{p.discount_amount:,} so'm"
        lines.append(
            f"{status} <code>{p.code}</code> — {discount_text} | "
            f"{p.used_count}/{p.max_uses} marta ishlatilgan"
        )

    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="➕ Yangi kod qo'shish", callback_data="add_promo"))
    for p in promos:
        if p.is_active:
            builder.add(InlineKeyboardButton(
                text=f"❌ {p.code} bekor qilish",
                callback_data=f"deactivate_promo:{p.id}"
            ))
    builder.adjust(1)

    await message.answer(
        "🎟 <b>Promo kodlar:</b>\n\n" + "\n".join(lines),
        reply_markup=builder.as_markup(),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "add_promo")
async def add_promo_start(call: CallbackQuery, state: FSMContext):
    if not is_admin(call.from_user.id):
        return

    await state.set_state(AdminPromoStates.entering_code)
    await call.message.answer(
        "🎟 Yangi promo kod nomini kiriting (lotin, katta harf):\nMasalan: SUMMER25",
        reply_markup=admin_cancel_keyboard(),
    )
    await call.answer()


@router.message(AdminPromoStates.entering_code)
async def promo_enter_code(message: Message, state: FSMContext):
    code = message.text.upper().strip()
    if len(code) < 3 or not code.isalnum():
        await message.answer("❌ Noto'g'ri kod. Faqat harf va raqamlar (3+ belgi):")
        return
    await state.update_data(code=code)
    await state.set_state(AdminPromoStates.entering_discount)
    await message.answer(
        "💰 Chegirma miqdorini kiriting:\n"
        "• Foiz uchun: masalan <b>10%</b>\n"
        "• So'm uchun: masalan <b>5000</b>",
        parse_mode="HTML",
    )


@router.message(AdminPromoStates.entering_discount)
async def promo_enter_discount(message: Message, state: FSMContext):
    text = message.text.strip()
    if text.endswith("%"):
        try:
            percent = int(text[:-1])
            await state.update_data(discount_percent=percent, discount_amount=0)
        except ValueError:
            await message.answer("❌ Noto'g'ri foiz.")
            return
    else:
        try:
            amount = int(text.replace(" ", "").replace(",", ""))
            await state.update_data(discount_amount=amount, discount_percent=0)
        except ValueError:
            await message.answer("❌ Noto'g'ri summa.")
            return

    await state.set_state(AdminPromoStates.entering_max_uses)
    await message.answer("🔢 Necha marta ishlatish mumkin?")


@router.message(AdminPromoStates.entering_max_uses)
async def promo_enter_max_uses(message: Message, state: FSMContext):
    try:
        max_uses = int(message.text)
    except ValueError:
        await message.answer("❌ Noto'g'ri son.")
        return

    data = await state.get_data()
    promo_service_data = {
        "code": data["code"],
        "discount_percent": data.get("discount_percent", 0),
        "discount_amount": data.get("discount_amount", 0),
        "max_uses": max_uses,
    }

    from database.database import AsyncSessionFactory
    async with AsyncSessionFactory() as session:
        promo_service = PromoService(session)
        await promo_service.create_promo(**promo_service_data)
        await session.commit()

    await state.clear()
    discount_text = (
        f"{promo_service_data['discount_percent']}%"
        if promo_service_data["discount_percent"]
        else f"{promo_service_data['discount_amount']:,} so'm"
    )
    await message.answer(
        f"✅ Promo kod <code>{data['code']}</code> yaratildi!\n"
        f"💰 Chegirma: {discount_text}\n"
        f"🔢 Max foydalanish: {max_uses}",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("deactivate_promo:"))
async def deactivate_promo(call: CallbackQuery, session: AsyncSession):
    if not is_admin(call.from_user.id):
        return

    promo_id = int(call.data.split(":")[1])
    promo_service = PromoService(session)
    await promo_service.deactivate_promo(promo_id)

    await call.answer("✅ Promo kod bekor qilindi.", show_alert=True)
    await call.message.edit_text("✅ Promo kod bekor qilindi.")
