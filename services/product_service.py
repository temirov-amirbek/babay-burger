"""
services/product_service.py — Mahsulot va kategoriya servisi
"""
from typing import Optional, List
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Product, Category


class ProductService:

    def __init__(self, session: AsyncSession):
        self.session = session

    # ── Kategoriyalar ─────────────────────────────────────────────────────────

    async def get_categories(self, active_only: bool = True) -> List[Category]:
        q = select(Category).order_by(Category.order)
        if active_only:
            q = q.where(Category.is_active == True)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_category(self, cat_id: int) -> Optional[Category]:
        result = await self.session.execute(
            select(Category).where(Category.id == cat_id)
        )
        return result.scalar_one_or_none()

    # ── Mahsulotlar ───────────────────────────────────────────────────────────

    async def get_products_by_category(
        self, category_id: int, available_only: bool = True
    ) -> List[Product]:
        q = (
            select(Product)
            .where(Product.category_id == category_id)
            .order_by(Product.order)
        )
        if available_only:
            q = q.where(Product.is_available == True)
        result = await self.session.execute(q)
        return list(result.scalars().all())

    async def get_product(self, product_id: int) -> Optional[Product]:
        result = await self.session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_all_products(self) -> List[Product]:
        result = await self.session.execute(
            select(Product)
            .options(selectinload(Product.category))
            .order_by(Product.category_id, Product.order)
        )
        return list(result.scalars().all())

    async def create_product(
        self,
        category_id: int,
        name_uz: str,
        name_ru: str,
        name_en: str,
        price: int,
        photo_id: Optional[str] = None,
        description_uz: Optional[str] = None,
        description_ru: Optional[str] = None,
        description_en: Optional[str] = None,
    ) -> Product:
        product = Product(
            category_id=category_id,
            name_uz=name_uz,
            name_ru=name_ru,
            name_en=name_en,
            price=price,
            photo_id=photo_id,
            description_uz=description_uz,
            description_ru=description_ru,
            description_en=description_en,
        )
        self.session.add(product)
        await self.session.flush()
        return product

    async def update_product(self, product_id: int, **kwargs) -> None:
        await self.session.execute(
            update(Product).where(Product.id == product_id).values(**kwargs)
        )

    async def toggle_availability(self, product_id: int) -> bool:
        product = await self.get_product(product_id)
        if product:
            new_status = not product.is_available
            await self.update_product(product_id, is_available=new_status)
            return new_status
        return False

    async def delete_product(self, product_id: int) -> None:
        await self.session.execute(
            delete(Product).where(Product.id == product_id)
        )

    async def get_top_products(self, limit: int = 5) -> List[dict]:
        """Eng ko'p sotilgan mahsulotlar."""
        from sqlalchemy import func
        from database.models import OrderItem
        result = await self.session.execute(
            select(
                Product.name_uz,
                func.sum(OrderItem.quantity).label("total_qty"),
                func.sum(OrderItem.quantity * OrderItem.product_price).label("revenue"),
            )
            .join(OrderItem, Product.id == OrderItem.product_id)
            .group_by(Product.id, Product.name_uz)
            .order_by(func.sum(OrderItem.quantity).desc())
            .limit(limit)
        )
        return [
            {"name": row.name_uz, "qty": row.total_qty, "revenue": row.revenue}
            for row in result.all()
        ]
