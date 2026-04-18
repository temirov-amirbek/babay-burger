"""
locales/__init__.py — I18n yordamchi funksiyalar
"""
from locales.uz import UZ
from locales.ru import RU
from locales.en import EN

LANGUAGES = {
    "uz": UZ,
    "ru": RU,
    "en": EN,
}

LANG_NAMES = {
    "uz": "🇺🇿 O'zbekcha",
    "ru": "🇷🇺 Русский",
    "en": "🇬🇧 English",
}


def _(key: str, lang: str = "uz", **kwargs) -> str:
    """Tarjima olish funksiyasi."""
    translations = LANGUAGES.get(lang, UZ)
    text = translations.get(key, UZ.get(key, f"[{key}]"))
    if kwargs:
        try:
            text = text.format(**kwargs)
        except KeyError:
            pass
    return text
