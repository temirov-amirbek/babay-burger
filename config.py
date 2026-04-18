"""
config.py — Babay Burger Bot konfiguratsiyasi
"""
from dataclasses import dataclass, field
from typing import List
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class BotConfig:
    token: str = field(default_factory=lambda: os.getenv("BOT_TOKEN", ""))
    admin_ids: List[int] = field(
        default_factory=lambda: [
            int(x.strip()) for x in os.getenv("ADMIN_IDS", "").split(",") if x.strip()
        ]
    )
    orders_channel_id: int = field(
        default_factory=lambda: int(os.getenv("ORDERS_CHANNEL_ID", "0") or 0)
    )


@dataclass
class DatabaseConfig:
    host: str = field(default_factory=lambda: os.getenv("DB_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("DB_PORT", "5432")))
    name: str = field(default_factory=lambda: os.getenv("DB_NAME", "babay_burger"))
    user: str = field(default_factory=lambda: os.getenv("DB_USER", "postgres"))
    password: str = field(default_factory=lambda: os.getenv("DB_PASS", ""))
    url: str = field(
        default_factory=lambda: os.getenv(
            "DATABASE_URL",
            "postgresql+asyncpg://postgres:password@localhost:5432/babay_burger",
        )
    )


@dataclass
class RedisConfig:
    host: str = field(default_factory=lambda: os.getenv("REDIS_HOST", "localhost"))
    port: int = field(default_factory=lambda: int(os.getenv("REDIS_PORT", "6379")))
    db: int = field(default_factory=lambda: int(os.getenv("REDIS_DB", "0")))

    @property
    def url(self) -> str:
        return f"redis://{self.host}:{self.port}/{self.db}"


@dataclass
class DeliveryConfig:
    fee: int = field(default_factory=lambda: int(os.getenv("DELIVERY_FEE", "5000")))
    min_order: int = field(
        default_factory=lambda: int(os.getenv("MIN_ORDER_AMOUNT", "15000"))
    )
    free_from: int = field(
        default_factory=lambda: int(os.getenv("FREE_DELIVERY_FROM", "80000"))
    )


@dataclass
class AppConfig:
    bot: BotConfig = field(default_factory=BotConfig)
    db: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    delivery: DeliveryConfig = field(default_factory=DeliveryConfig)
    default_lang: str = field(
        default_factory=lambda: os.getenv("DEFAULT_LANG", "uz")
    )
    timezone: str = field(
        default_factory=lambda: os.getenv("TIMEZONE", "Asia/Tashkent")
    )


# Global config instance
config = AppConfig()
