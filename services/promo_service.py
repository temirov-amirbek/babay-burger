"""
services/promo_service.py — Promo kod servisi
"""
from typing import Optional
from datetime import datetime
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import PromoCode


class PromoService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_promo(self, code: str) -> Optional[PromoCode]:
        result = await self.session.execute(
            select(PromoCode).where(PromoCode.code == code.upper())
        )
        return result.scalar_one_or_none()

    async def validate_promo(self, code: str) -> tuple[bool, Optional[PromoCode]]:
        promo = await self.get_promo(code)
        if not promo or not promo.is_valid:
            return False, None
        return True, promo

    async def apply_promo(self, code: str, order_total: int) -> int:
        """Chegirmani hisoblash (UZS da qaytaradi)."""
        is_valid, promo = await self.validate_promo(code)
        if not is_valid or not promo:
            return 0

        if promo.discount_percent > 0:
            discount = int(order_total * promo.discount_percent / 100)
        else:
            discount = min(promo.discount_amount, order_total)

        # Ishlatilganlar sonini oshirish
        await self.session.execute(
            update(PromoCode)
            .where(PromoCode.code == code.upper())
            .values(used_count=PromoCode.used_count + 1)
        )
        return discount

    async def create_promo(
        self,
        code: str,
        discount_percent: int = 0,
        discount_amount: int = 0,
        max_uses: int = 1,
        expires_at: Optional[datetime] = None,
    ) -> PromoCode:
        promo = PromoCode(
            code=code.upper(),
            discount_percent=discount_percent,
            discount_amount=discount_amount,
            max_uses=max_uses,
            expires_at=expires_at,
        )
        self.session.add(promo)
        await self.session.flush()
        return promo

    async def get_all_promos(self) -> list[PromoCode]:
        result = await self.session.execute(select(PromoCode).order_by(PromoCode.id.desc()))
        return list(result.scalars().all())

    async def deactivate_promo(self, promo_id: int) -> None:
        await self.session.execute(
            update(PromoCode).where(PromoCode.id == promo_id).values(is_active=False)
        )
