"""
locales/en.py — English translations
"""

EN = {
    # ── General ──────────────────────────────────────────────────────────────
    "welcome_new": (
        "👋 Welcome, <b>{name}</b>!\n\n"
        "🍔 Welcome to <b>Babay Burger</b> bot!\n\n"
        "Please send your phone number to register 👇"
    ),
    "welcome_back": (
        "👋 Welcome back, <b>{name}</b>!\n\n"
        "What would you like to order? 😋"
    ),
    "send_contact": "📱 Share Phone Number",
    "contact_received": "✅ Phone number received!\n\nPlease enter your name:",
    "name_saved": "🎉 Registration complete!\n\nHeading to the main menu 👇",
    "enter_name": "✏️ Enter your name:",
    "invalid_name": "❌ Invalid name. Please enter your real name:",
    "choose_lang": "🌐 Choose language / Tilni tanlang / Выберите язык:",
    "lang_saved": "✅ Language saved!",

    # ── Main menu ────────────────────────────────────────────────────────────
    "main_menu": "🏠 <b>Main Menu</b>\n\nChoose an option:",
    "btn_order":   "🍔 Place an Order",
    "btn_orders":  "📦 My Orders",
    "btn_about":   "ℹ️ About Us",
    "btn_contact": "📞 Contact",
    "btn_lang":    "🌐 Language",
    "btn_back":    "⬅️ Back",
    "btn_cancel":  "❌ Cancel",
    "btn_menu":    "🏠 Menu",

    # ── Categories ───────────────────────────────────────────────────────────
    "choose_category": "📂 <b>Choose a category:</b>",
    "choose_product":  "🍽 <b>{category}</b> — choose a product:",
    "no_products":     "😔 No products in this category yet.",

    # ── Product ──────────────────────────────────────────────────────────────
    "product_card": (
        "🍔 <b>{name}</b>\n\n"
        "{description}\n\n"
        "💰 Price: <b>{price}</b>"
    ),
    "btn_add_cart": "🛒 Add to Cart",
    "added_to_cart": "✅ <b>{name}</b> added to cart!",

    # ── Cart ─────────────────────────────────────────────────────────────────
    "cart_title":    "🛒 <b>Your Cart:</b>\n\n",
    "cart_item":     "• {name} x{qty} — {price}\n",
    "cart_total":    "\n💰 <b>Total:</b> {total}\n",
    "cart_delivery": "\n🚚 Delivery fee: <b>{fee}</b>",
    "cart_free_del": "🚀 Free delivery!",
    "cart_empty":    "🛒 Your cart is empty. Add something!",
    "btn_checkout":  "✅ Checkout",
    "btn_clear_cart":"🗑 Clear Cart",
    "cart_cleared":  "🗑 Cart cleared.",
    "min_order_err": "⚠️ Minimum order amount: <b>{amount}</b>. Current total: <b>{current}</b>",

    # ── Checkout ─────────────────────────────────────────────────────────────
    "enter_address": (
        "📍 Enter your delivery address:\n\n"
        "• Type the address or\n"
        "• 📎 → tap 'Location'"
    ),
    "promo_question": "🎟 Do you have a promo code? Enter it or skip:",
    "btn_skip_promo": "⏩ Skip",
    "promo_applied":  "🎉 Promo code applied! Discount: <b>{discount}</b>",
    "promo_invalid":  "❌ Invalid or expired promo code.",
    "confirm_order": (
        "📋 <b>Order Confirmation</b>\n\n"
        "{items}\n"
        "📍 Address: {address}\n"
        "💰 Subtotal: {total}\n"
        "🚚 Delivery: {delivery}\n"
        "{promo}"
        "💳 <b>Total to pay: {final}</b>"
    ),
    "promo_line":    "🎟 Discount: -{discount}\n",
    "btn_confirm":   "✅ Confirm Order",
    "btn_edit":      "✏️ Edit",
    "order_placed": (
        "🎉 <b>Order #{order_id} placed!</b>\n\n"
        "⏳ An admin will confirm it shortly.\n"
        "Track your order status in «📦 My Orders»."
    ),
    "comment_question": "💬 Add a comment? (optional):",
    "btn_no_comment": "➡️ No",

    # ── Orders ───────────────────────────────────────────────────────────────
    "my_orders_title": "📦 <b>My Orders:</b>\n\n",
    "no_orders":       "😔 You haven't placed any orders yet.",
    "order_item": (
        "🧾 Order <b>#{id}</b>\n"
        "📅 {date}\n"
        "{status_emoji} Status: <b>{status}</b>\n"
        "💰 Amount: <b>{amount}</b>\n"
        "────────────────\n"
    ),
    "order_status_pending":    "Pending",
    "order_status_confirmed":  "Confirmed ✅",
    "order_status_delivering": "Out for delivery 🚚",
    "order_status_delivered":  "Delivered ✔️",
    "order_status_cancelled":  "Cancelled ❌",

    # ── About ────────────────────────────────────────────────────────────────
    "about_text": (
        "🍔 <b>Babay Burger</b>\n\n"
        "🏆 The tastiest burgers in Tashkent!\n\n"
        "⏰ Working hours: 10:00 AM — 11:00 PM\n"
        "📍 Address: Tashkent, Chilanzar district\n"
        "🌐 Instagram: @babayburger\n\n"
        "Made with quality meat, natural ingredients, and love! ❤️"
    ),
    "contact_text": (
        "📞 <b>Contact Us</b>\n\n"
        "📱 Phone: <a href='tel:+998901234567'>+998 90 123-45-67</a>\n"
        "💬 Telegram: @babayburger_support\n"
        "📧 Email: info@babayburger.uz\n\n"
        "Reach out for any questions or feedback!"
    ),

    # ── Errors ───────────────────────────────────────────────────────────────
    "error_generic": "❌ An error occurred. Please try again.",
    "blocked_user":  "🚫 You are blocked. Contact the admin.",
}
