"""
services/order_service.py — Buyurtma va savat servisi
"""
from typing import Optional, List
from datetime import datetime, timedelta
from sqlalchemy import select, update, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from database.models import Order, OrderItem, CartItem, Product, OrderStatus
from config import config


class CartService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_cart(self, user_id: int) -> List[CartItem]:
        result = await self.session.execute(
            select(CartItem)
            .where(CartItem.user_id == user_id)
            .options(selectinload(CartItem.product))
        )
        return list(result.scalars().all())

    async def get_cart_item(self, item_id: int) -> Optional[CartItem]:
        result = await self.session.execute(
            select(CartItem)
            .where(CartItem.id == item_id)
            .options(selectinload(CartItem.product))
        )
        return result.scalar_one_or_none()

    async def add_to_cart(self, user_id: int, product_id: int, quantity: int = 1) -> CartItem:
        # Mavjud bo'lsa miqdorini oshir
        result = await self.session.execute(
            select(CartItem).where(
                CartItem.user_id == user_id,
                CartItem.product_id == product_id,
            )
        )
        item = result.scalar_one_or_none()
        if item:
            item.quantity += quantity
            await self.session.flush()
            return item

        item = CartItem(user_id=user_id, product_id=product_id, quantity=quantity)
        self.session.add(item)
        await self.session.flush()
        return item

    async def increase_quantity(self, item_id: int) -> Optional[CartItem]:
        item = await self.get_cart_item(item_id)
        if item:
            item.quantity += 1
            await self.session.flush()
        return item

    async def decrease_quantity(self, item_id: int) -> Optional[CartItem]:
        item = await self.get_cart_item(item_id)
        if item:
            if item.quantity <= 1:
                await self.session.delete(item)
                await self.session.flush()
                return None
            item.quantity -= 1
            await self.session.flush()
        return item

    async def clear_cart(self, user_id: int) -> None:
        items = await self.get_cart(user_id)
        for item in items:
            await self.session.delete(item)
        await self.session.flush()

    async def get_cart_total(self, user_id: int) -> int:
        items = await self.get_cart(user_id)
        return sum(item.product.price * item.quantity for item in items)

    async def get_cart_count(self, user_id: int) -> int:
        items = await self.get_cart(user_id)
        return sum(item.quantity for item in items)

    def calculate_delivery_fee(self, total: int) -> int:
        if total >= config.delivery.free_from:
            return 0
        return config.delivery.fee


class OrderService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_order(
        self,
        user_id: int,
        cart_items: List[CartItem],
        delivery_address: str,
        delivery_fee: int,
        discount: int = 0,
        promo_code: Optional[str] = None,
        delivery_lat: Optional[float] = None,
        delivery_lon: Optional[float] = None,
        comment: Optional[str] = None,
    ) -> Order:
        total = sum(item.product.price * item.quantity for item in cart_items)

        order = Order(
            user_id=user_id,
            status=OrderStatus.PENDING,
            total_amount=total,
            delivery_fee=delivery_fee,
            discount=discount,
            promo_code=promo_code,
            delivery_address=delivery_address,
            delivery_lat=delivery_lat,
            delivery_lon=delivery_lon,
            comment=comment,
        )
        self.session.add(order)
        await self.session.flush()

        # OrderItem larni yaratish
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                product_id=item.product_id,
                product_name=item.product.name_uz,
                product_price=item.product.price,
                quantity=item.quantity,
            )
            self.session.add(order_item)

        await self.session.flush()
        return order

    async def get_order(self, order_id: int) -> Optional[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.items),
                selectinload(Order.user),
            )
        )
        return result.scalar_one_or_none()

    async def get_user_orders(self, user_id: int, limit: int = 10) -> List[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.items))
            .order_by(Order.created_at.desc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def get_pending_orders(self) -> List[Order]:
        result = await self.session.execute(
            select(Order)
            .where(Order.status == OrderStatus.PENDING)
            .options(selectinload(Order.items), selectinload(Order.user))
            .order_by(Order.created_at.desc())
        )
        return list(result.scalars().all())

    async def update_order_status(
        self, order_id: int, status: str
    ) -> Optional[Order]:
        await self.session.execute(
            update(Order).where(Order.id == order_id).values(status=status)
        )
        await self.session.flush()
        return await self.get_order(order_id)

    async def set_admin_message_id(self, order_id: int, message_id: int) -> None:
        await self.session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(admin_message_id=message_id)
        )

    # ── Statistika ────────────────────────────────────────────────────────────

    async def get_daily_stats(self, date: Optional[datetime] = None) -> dict:
        if not date:
            date = datetime.now()
        start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end = start + timedelta(days=1)

        result = await self.session.execute(
            select(
                func.count(Order.id).label("count"),
                func.coalesce(func.sum(Order.total_amount + Order.delivery_fee - Order.discount), 0).label("revenue"),
            ).where(
                Order.created_at >= start,
                Order.created_at < end,
                Order.status != OrderStatus.CANCELLED,
            )
        )
        row = result.one()
        return {"count": row.count, "revenue": row.revenue}

    async def get_total_stats(self) -> dict:
        result = await self.session.execute(
            select(
                func.count(Order.id).label("total_orders"),
                func.coalesce(
                    func.sum(Order.total_amount + Order.delivery_fee - Order.discount), 0
                ).label("total_revenue"),
            ).where(Order.status != OrderStatus.CANCELLED)
        )
        row = result.one()
        return {
            "total_orders": row.total_orders,
            "total_revenue": row.total_revenue,
        }
