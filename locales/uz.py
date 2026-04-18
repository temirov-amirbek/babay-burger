"""
locales/uz.py — O'zbek tili tarjimalari
"""

UZ = {
    # ── Umumiy ──────────────────────────────────────────────────────────────
    "welcome_new": (
        "👋 Xush kelibsiz, <b>{name}</b>!\n\n"
        "🍔 <b>Babay Burger</b> botiga xush kelibsiz!\n\n"
        "Davom etish uchun telefon raqamingizni yuboring 👇"
    ),
    "welcome_back": (
        "👋 Xush kelibsiz, <b>{name}</b>!\n\n"
        "Nima buyurtma qilasiz? 😋"
    ),
    "send_contact": "📱 Telefon raqamni yuborish",
    "contact_received": "✅ Telefon raqam qabul qilindi!\n\nIsmingizni kiriting:",
    "name_saved": "🎉 Ro'yxatdan o'tdingiz!\n\nAsosiy menyuga o'tamiz 👇",
    "enter_name": "✏️ Ismingizni kiriting:",
    "invalid_name": "❌ Ism noto'g'ri. Iltimos, haqiqiy ismingizni kiriting:",
    "choose_lang": "🌐 Tilni tanlang / Выберите язык / Choose language:",
    "lang_saved": "✅ Til saqlandi!",

    # ── Asosiy menyu ────────────────────────────────────────────────────────
    "main_menu": "🏠 <b>Asosiy menyu</b>\n\nQuyidagilardan birini tanlang:",
    "btn_order":   "🍔 Buyurtma berish",
    "btn_orders":  "📦 Buyurtmalarim",
    "btn_about":   "ℹ️ Biz haqimizda",
    "btn_contact": "📞 Aloqa",
    "btn_lang":    "🌐 Til",
    "btn_back":    "⬅️ Orqaga",
    "btn_cancel":  "❌ Bekor qilish",
    "btn_menu":    "🏠 Menyu",

    # ── Kategoriyalar ───────────────────────────────────────────────────────
    "choose_category": "📂 <b>Kategoriyani tanlang:</b>",
    "choose_product":  "🍽 <b>{category}</b> — mahsulotni tanlang:",
    "no_products":     "😔 Bu kategoriyada hozircha mahsulot yo'q.",

    # ── Mahsulot ─────────────────────────────────────────────────────────────
    "product_card": (
        "🍔 <b>{name}</b>\n\n"
        "{description}\n\n"
        "💰 Narxi: <b>{price}</b>"
    ),
    "btn_add_cart": "🛒 Savatga qo'shish",
    "added_to_cart": "✅ <b>{name}</b> savatga qo'shildi!",

    # ── Savat ────────────────────────────────────────────────────────────────
    "cart_title":   "🛒 <b>Savatingiz:</b>\n\n",
    "cart_item":    "• {name} x{qty} — {price}\n",
    "cart_total":   "\n💰 <b>Jami:</b> {total}\n",
    "cart_delivery":"\n🚚 Yetkazib berish: <b>{fee}</b>",
    "cart_free_del":"🚀 Bepul yetkazib berish!",
    "cart_empty":   "🛒 Savat bo'sh. Biror narsa qo'shing!",
    "btn_checkout": "✅ Buyurtma berish",
    "btn_clear_cart":"🗑 Tozalash",
    "cart_cleared": "🗑 Savat tozalandi.",
    "min_order_err": "⚠️ Minimal buyurtma miqdori: <b>{amount}</b>. Hozirgi jami: <b>{current}</b>",

    # ── Checkout ─────────────────────────────────────────────────────────────
    "enter_address": (
        "📍 Manzilingizni yuboring:\n\n"
        "• Matn ko'rinishida kiriting yoki\n"
        "• 📎 → Lokatsiya tugmasini bosing"
    ),
    "promo_question": "🎟 Promo kodingiz bormi? Kiriting yoki o'tkazib yuboring:",
    "btn_skip_promo": "⏩ O'tkazib yuborish",
    "promo_applied":  "🎉 Promo kod qo'llandi! Chegirma: <b>{discount}</b>",
    "promo_invalid":  "❌ Promo kod noto'g'ri yoki muddati o'tgan.",
    "confirm_order": (
        "📋 <b>Buyurtmani tasdiqlash</b>\n\n"
        "{items}\n"
        "📍 Manzil: {address}\n"
        "💰 Jami: {total}\n"
        "🚚 Yetkazib berish: {delivery}\n"
        "{promo}"
        "💳 <b>To'lov: {final}</b>"
    ),
    "promo_line":    "🎟 Chegirma: -{discount}\n",
    "btn_confirm":   "✅ Tasdiqlash",
    "btn_edit":      "✏️ O'zgartirish",
    "order_placed": (
        "🎉 <b>Buyurtma #{order_id} qabul qilindi!</b>\n\n"
        "⏳ Tez orada admin tasdiqlaydi.\n"
        "Buyurtma holatini «📦 Buyurtmalarim» bo'limida ko'rishingiz mumkin."
    ),
    "comment_question": "💬 Izoh qo'shmoqchimisiz? (ixtiyoriy):",
    "btn_no_comment": "➡️ Yo'q",

    # ── Buyurtmalar ──────────────────────────────────────────────────────────
    "my_orders_title": "📦 <b>Buyurtmalarim:</b>\n\n",
    "no_orders":       "😔 Hali buyurtmalaringiz yo'q.",
    "order_item": (
        "🧾 Buyurtma <b>#{id}</b>\n"
        "📅 {date}\n"
        "{status_emoji} Holat: <b>{status}</b>\n"
        "💰 Summa: <b>{amount}</b>\n"
        "────────────────\n"
    ),
    "order_status_pending":    "Kutilmoqda",
    "order_status_confirmed":  "Tasdiqlandi ✅",
    "order_status_delivering": "Yetkazilmoqda 🚚",
    "order_status_delivered":  "Yetkazildi ✔️",
    "order_status_cancelled":  "Bekor qilindi ❌",

    # ── Haqida ───────────────────────────────────────────────────────────────
    "about_text": (
        "🍔 <b>Babay Burger</b>\n\n"
        "🏆 Toshkentning eng mazali burgerlari!\n\n"
        "⏰ Ish vaqti: 10:00 — 23:00\n"
        "📍 Manzil: Toshkent sh., Chilonzor tumani\n"
        "🌐 Instagram: @babayburger\n\n"
        "Sifatli go'sht, tabiiy ingredientlar va muhabbat bilan tayyorlaymiz! ❤️"
    ),
    "contact_text": (
        "📞 <b>Aloqa</b>\n\n"
        "📱 Telefon: <a href='tel:+998901234567'>+998 90 123-45-67</a>\n"
        "💬 Telegram: @babayburger_support\n"
        "📧 Email: info@babayburger.uz\n\n"
        "Savol va takliflaringiz uchun murojaat qiling!"
    ),

    # ── Xatolar ──────────────────────────────────────────────────────────────
    "error_generic": "❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring.",
    "blocked_user":  "🚫 Siz bloklangansiz. Admin bilan bog'laning.",
}
