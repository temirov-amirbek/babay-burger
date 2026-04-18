"""
handlers/admin/admin_products.py — Mahsulotlar boshqaruvi (CRUD)
"""
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from loguru import logger

from database.database import AsyncSession
from services.product_service import ProductService
from states import AdminProductStates
from keyboards.admin_kb import (
    admin_main_keyboard, admin_cancel_keyboard, admin_skip_keyboard,
    products_list_keyboard, product_edit_keyboard,
    categories_admin_keyboard, confirm_delete_keyboard,
)
from config import config

router = Router(name="admin_products")


def is_admin(user_id: int) -> bool:
    return user_id in config.bot.admin_ids


# ─── Mahsulotlar ro'yxati ─────────────────────────────────────────────────────

@router.message(F.text == "✏️ Mahsulotlar")
async def list_products(message: Message, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return

    product_service = ProductService(session)
    products = await product_service.get_all_products()

    if not products:
        await message.answer("📭 Mahsulotlar yo'q.", reply_markup=admin_main_keyboard())
        return

    await message.answer(
        f"📦 <b>Barcha mahsulotlar: {len(products)} ta</b>\n\nO'zgartirish uchun tanlang:",
        reply_markup=products_list_keyboard(products),
        parse_mode="HTML",
    )


@router.callback_query(F.data == "admin_products")
async def list_products_cb(call: CallbackQuery, session: AsyncSession):
    if not is_admin(call.from_user.id):
        return

    product_service = ProductService(session)
    products = await product_service.get_all_products()

    await call.message.edit_text(
        f"📦 Barcha mahsulotlar: {len(products)} ta",
        reply_markup=products_list_keyboard(products),
    )
    await call.answer()


@router.callback_query(F.data.startswith("admin_prod:"))
async def product_detail_admin(call: CallbackQuery, session: AsyncSession):
    prod_id = int(call.data.split(":")[1])
    product_service = ProductService(session)
    product = await product_service.get_product(prod_id)

    if not product:
        await call.answer("❌ Topilmadi.", show_alert=True)
        return

    status = "✅ Mavjud" if product.is_available else "❌ Mavjud emas"
    text = (
        f"📦 <b>{product.name_uz}</b>\n\n"
        f"🇷🇺 {product.name_ru}\n"
        f"🇬🇧 {product.name_en}\n\n"
        f"💰 Narxi: {product.price:,} so'm\n"
        f"🖼 Rasm: {'✅ Bor' if product.photo_id else '❌ Yo'q'}\n"
        f"📊 Holat: {status}"
    )

    await call.message.edit_text(
        text,
        reply_markup=product_edit_keyboard(prod_id),
        parse_mode="HTML",
    )
    await call.answer()


# ─── Mahsulot qo'shish ────────────────────────────────────────────────────────

@router.message(F.text == "➕ Mahsulot qo'shish")
async def add_product_start(message: Message, state: FSMContext, session: AsyncSession):
    if not is_admin(message.from_user.id):
        return

    product_service = ProductService(session)
    categories = await product_service.get_categories()

    await state.set_state(AdminProductStates.choosing_category)
    await message.answer(
        "📂 Kategoriyani tanlang:",
        reply_markup=categories_admin_keyboard(categories),
    )


@router.callback_query(F.data.startswith("admin_cat:"), AdminProductStates.choosing_category)
async def choose_category_for_product(call: CallbackQuery, state: FSMContext):
    cat_id = int(call.data.split(":")[1])
    await state.update_data(category_id=cat_id)
    await state.set_state(AdminProductStates.entering_name_uz)
    await call.message.edit_text("📝 Mahsulot nomini kiriting (O'zbek tilida):")
    await call.answer()


@router.message(AdminProductStates.entering_name_uz)
async def enter_name_uz(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
        return
    await state.update_data(name_uz=message.text)
    await state.set_state(AdminProductStates.entering_name_ru)
    await message.answer("📝 Mahsulot nomini kiriting (Rus tilida):", reply_markup=admin_cancel_keyboard())


@router.message(AdminProductStates.entering_name_ru)
async def enter_name_ru(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
        return
    await state.update_data(name_ru=message.text)
    await state.set_state(AdminProductStates.entering_name_en)
    await message.answer("📝 Mahsulot nomini kiriting (Ingliz tilida):")


@router.message(AdminProductStates.entering_name_en)
async def enter_name_en(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
        return
    await state.update_data(name_en=message.text)
    await state.set_state(AdminProductStates.entering_desc_uz)
    await message.answer("📝 Tavsif kiriting (UZ) yoki o'tkazib yuboring:", reply_markup=admin_skip_keyboard())


@router.message(AdminProductStates.entering_desc_uz)
async def enter_description(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
        return
    desc = None if message.text == "⏩ O'tkazish" else message.text
    await state.update_data(description_uz=desc, description_ru=desc, description_en=desc)
    await state.set_state(AdminProductStates.entering_price)
    await message.answer("💰 Narxni kiriting (so'm, faqat raqam):\nMasalan: 32000")


@router.message(AdminProductStates.entering_price)
async def enter_price(message: Message, state: FSMContext):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
        return
    try:
        price = int(message.text.replace(" ", "").replace(",", ""))
        if price <= 0:
            raise ValueError
    except ValueError:
        await message.answer("❌ Noto'g'ri narx. Faqat musbat raqam kiriting:")
        return

    await state.update_data(price=price)
    await state.set_state(AdminProductStates.uploading_photo)
    await message.answer("🖼 Mahsulot rasmini yuboring yoki o'tkazib yuboring:", reply_markup=admin_skip_keyboard())


@router.message(AdminProductStates.uploading_photo, F.photo)
async def receive_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo_id=photo_id)
    await save_new_product(message, state)


@router.message(AdminProductStates.uploading_photo, F.text == "⏩ O'tkazish")
async def skip_photo(message: Message, state: FSMContext):
    await state.update_data(photo_id=None)
    await save_new_product(message, state)


async def save_new_product(message: Message, state: FSMContext):
    from database.database import AsyncSessionFactory
    data = await state.get_data()

    async with AsyncSessionFactory() as session:
        product_service = ProductService(session)
        product = await product_service.create_product(
            category_id=data["category_id"],
            name_uz=data["name_uz"],
            name_ru=data["name_ru"],
            name_en=data["name_en"],
            price=data["price"],
            photo_id=data.get("photo_id"),
            description_uz=data.get("description_uz"),
            description_ru=data.get("description_ru"),
            description_en=data.get("description_en"),
        )
        await session.commit()
        logger.info(f"Yangi mahsulot qo'shildi: #{product.id} - {product.name_uz}")

    await state.clear()
    await message.answer(
        f"✅ <b>{data['name_uz']}</b> mahsuloti qo'shildi!\n\n"
        f"💰 Narxi: {data['price']:,} so'm",
        reply_markup=admin_main_keyboard(),
        parse_mode="HTML",
    )


# ─── Mahsulot tahrirlash ──────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("edit_prod:"))
async def edit_product_field(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    parts = call.data.split(":")
    field = parts[1]
    prod_id = int(parts[2])

    product_service = ProductService(session)

    if field == "toggle":
        new_status = await product_service.toggle_availability(prod_id)
        status_text = "✅ yoqildi" if new_status else "❌ o'chirildi"
        await call.answer(f"Holat {status_text}", show_alert=True)
        # Mahsulot ma'lumotlarini yangilash
        product = await product_service.get_product(prod_id)
        status = "✅ Mavjud" if product.is_available else "❌ Mavjud emas"
        await call.message.edit_text(
            f"📦 <b>{product.name_uz}</b>\n\n💰 Narxi: {product.price:,} so'm\n📊 Holat: {status}",
            reply_markup=product_edit_keyboard(prod_id),
            parse_mode="HTML",
        )
        return

    if field == "delete":
        await call.message.edit_text(
            "🗑 Bu mahsulotni o'chirishni tasdiqlaysizmi?",
            reply_markup=confirm_delete_keyboard(prod_id),
        )
        await call.answer()
        return

    field_prompts = {
        "name_uz": "📝 Yangi nom kiriting (UZ):",
        "name_ru": "📝 Yangi nom kiriting (RU):",
        "price":   "💰 Yangi narx kiriting (so'm):",
        "photo":   "🖼 Yangi rasm yuboring:",
    }

    await state.update_data(editing_product=prod_id, editing_field=field)
    await state.set_state(AdminProductStates.editing_field)
    await call.message.answer(
        field_prompts.get(field, "Yangi qiymat kiriting:"),
        reply_markup=admin_cancel_keyboard(),
    )
    await call.answer()


@router.message(AdminProductStates.editing_field)
async def save_edited_field(message: Message, state: FSMContext, session: AsyncSession):
    if message.text == "❌ Bekor qilish":
        await state.clear()
        await message.answer("❌ Bekor qilindi.", reply_markup=admin_main_keyboard())
        return

    data = await state.get_data()
    prod_id = data["editing_product"]
    field = data["editing_field"]

    product_service = ProductService(session)

    if field == "photo" and message.photo:
        await product_service.update_product(prod_id, photo_id=message.photo[-1].file_id)
        await message.answer("✅ Rasm yangilandi!", reply_markup=admin_main_keyboard())
    elif field == "price":
        try:
            price = int(message.text.replace(" ", ""))
            await product_service.update_product(prod_id, price=price)
            await message.answer(f"✅ Narx yangilandi: {price:,} so'm", reply_markup=admin_main_keyboard())
        except ValueError:
            await message.answer("❌ Noto'g'ri narx.")
            return
    else:
        await product_service.update_product(prod_id, **{field: message.text})
        await message.answer("✅ Yangilandi!", reply_markup=admin_main_keyboard())

    await state.clear()


@router.callback_query(F.data.startswith("confirm_delete:"))
async def confirm_delete_product(call: CallbackQuery, session: AsyncSession):
    prod_id = int(call.data.split(":")[1])
    product_service = ProductService(session)
    product = await product_service.get_product(prod_id)

    if product:
        name = product.name_uz
        await product_service.delete_product(prod_id)
        await call.message.edit_text(f"🗑 <b>{name}</b> o'chirildi.", parse_mode="HTML")
        logger.info(f"Mahsulot o'chirildi: #{prod_id} - {name}")
    else:
        await call.message.edit_text("❌ Mahsulot topilmadi.")

    await call.answer()
