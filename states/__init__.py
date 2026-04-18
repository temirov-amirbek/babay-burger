"""
states/__init__.py — FSM holatlari (State Management)
"""
from aiogram.fsm.state import State, StatesGroup


# ─── Foydalanuvchi holatlari ──────────────────────────────────────────────────

class RegistrationStates(StatesGroup):
    waiting_contact = State()   # Telefon raqam kutish
    waiting_name    = State()   # Ism kutish


class OrderStates(StatesGroup):
    choosing_category = State()  # Kategoriya tanlash
    choosing_product  = State()  # Mahsulot tanlash
    viewing_cart      = State()  # Savat ko'rish
    entering_address  = State()  # Manzil kiritish
    entering_promo    = State()  # Promo kod kiritish
    entering_comment  = State()  # Izoh kiritish
    confirming_order  = State()  # Buyurtmani tasdiqlash


class LanguageStates(StatesGroup):
    choosing_language = State()


# ─── Admin holatlari ──────────────────────────────────────────────────────────

class AdminOrderStates(StatesGroup):
    viewing_orders = State()


class AdminProductStates(StatesGroup):
    choosing_category  = State()   # Kategoriya tanlash
    entering_name_uz   = State()   # Nomi (UZ)
    entering_name_ru   = State()   # Nomi (RU)
    entering_name_en   = State()   # Nomi (EN)
    entering_desc_uz   = State()   # Tavsif (UZ)
    entering_price     = State()   # Narxi
    uploading_photo    = State()   # Rasm yuklash
    confirming         = State()   # Tasdiqlash

    # Tahrirlash
    editing_product    = State()   # Qaysi mahsulotni tahrirlash
    editing_field      = State()   # Qaysi maydon


class AdminBroadcastStates(StatesGroup):
    choosing_lang    = State()   # Qaysi til foydalanuvchilari
    entering_message = State()   # Xabar matni
    confirming       = State()   # Tasdiqlash


class AdminPromoStates(StatesGroup):
    entering_code     = State()
    entering_discount = State()
    entering_max_uses = State()
    entering_expires  = State()
