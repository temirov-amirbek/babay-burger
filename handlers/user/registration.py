"""
handlers/user/registration.py — Ro'yxatdan o'tish handlerlari
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from database.database import AsyncSession
from database.models import User
from services.user_service import UserService
from states import RegistrationStates
from keyboards.user_kb import (
    contact_keyboard, main_menu_keyboard, language_keyboard
)
from locales import _
from utils.helpers import validate_name

router = Router(name="registration")


# ─── /start ───────────────────────────────────────────────────────────────────

@router.message(F.text == "/start")
async def cmd_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    db_user: User | None,
    lang: str,
):
    await state.clear()

    if db_user and db_user.phone:
        # Ro'yxatdan o'tgan foydalanuvchi
        await message.answer(
            _("welcome_back", lang, name=db_user.full_name),
            reply_markup=main_menu_keyboard(lang),
        )
        return

    # Yangi foydalanuvchi — til tanlash
    await message.answer(
        _("choose_lang", lang),
        reply_markup=language_keyboard(),
    )
    await state.set_state(RegistrationStates.waiting_contact)
    await state.update_data(tg_name=message.from_user.full_name)


# ─── Til tanlash (start paytida) ─────────────────────────────────────────────

@router.callback_query(F.data.startswith("set_lang:"), RegistrationStates.waiting_contact)
async def choose_lang_on_register(
    call: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
):
    lang_code = call.data.split(":")[1]
    await state.update_data(lang=lang_code)

    await call.message.edit_text(
        _("welcome_new", lang_code, name=call.from_user.first_name)
    )
    await call.message.answer(
        _("send_contact", lang_code),
        reply_markup=contact_keyboard(lang_code),
    )
    await call.answer()


# ─── Kontakt qabul qilish ─────────────────────────────────────────────────────

@router.message(F.contact, RegistrationStates.waiting_contact)
async def receive_contact(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    lang = data.get("lang", "uz")

    contact = message.contact
    phone = contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone

    await state.update_data(phone=phone)

    await message.answer(
        _("contact_received", lang),
        reply_markup=None,
    )
    await state.set_state(RegistrationStates.waiting_name)


# ─── Ism qabul qilish ────────────────────────────────────────────────────────

@router.message(RegistrationStates.waiting_name)
async def receive_name(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
):
    data = await state.get_data()
    lang = data.get("lang", "uz")
    name = message.text.strip() if message.text else ""

    if not validate_name(name):
        await message.answer(_("invalid_name", lang))
        return

    phone = data.get("phone", "")

    user_service = UserService(session)
    user = await user_service.get_user(message.from_user.id)

    if user:
        await user_service.update_name(message.from_user.id, name)
        await user_service.update_phone(message.from_user.id, phone)
        await user_service.update_language(message.from_user.id, lang)
    else:
        await user_service.create_user(
            user_id=message.from_user.id,
            full_name=name,
            username=message.from_user.username,
            lang=lang,
        )
        # Telefon va tilni ham saqlash
        await user_service.update_phone(message.from_user.id, phone)
        await user_service.update_language(message.from_user.id, lang)

    await state.clear()
    logger.info(f"Yangi foydalanuvchi: {message.from_user.id} | {name} | {phone}")

    await message.answer(
        _("name_saved", lang),
        reply_markup=main_menu_keyboard(lang),
    )


# ─── Til o'zgartirish (asosiy menyudan) ──────────────────────────────────────

@router.message(F.text.in_(["🌐 Til", "🌐 Язык", "🌐 Language"]))
async def change_language(message: Message, lang: str):
    await message.answer(
        _("choose_lang", lang),
        reply_markup=language_keyboard(),
    )


@router.callback_query(F.data.startswith("set_lang:"))
async def set_language(
    call: CallbackQuery,
    session: AsyncSession,
    db_user: User | None,
):
    lang_code = call.data.split(":")[1]

    if db_user:
        user_service = UserService(session)
        await user_service.update_language(db_user.id, lang_code)

    await call.message.edit_text(
        _("lang_saved", lang_code)
    )
    await call.message.answer(
        _("main_menu", lang_code),
        reply_markup=main_menu_keyboard(lang_code),
    )
    await call.answer()
