from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import (
    ProductNotFoundException,
    InsufficientStockException,
    EmptyOrderException,
)
from decimal import Decimal
from app.db.models.user import User
from app.db.models.order import Order, OrderStatus
from app.db.models.order_item import OrderItem
from app.db.models.product import Product

from app.schemas.order import OrderCreate


async def create_order(
    db: AsyncSession,
    data: OrderCreate,
    current_user: User,
):
    if not data.items:
        raise EmptyOrderException()

    order = Order(
        user_id=current_user.id,
        status=OrderStatus.PENDING,
        total_price=0
    )

    db.add(order)

    await db.flush()

    total_price = Decimal("0.00")

    for item_data in data.items:

        stmt = (
            select(Product)
            .where(
                Product.id == item_data.product_id,
                Product.is_active.is_(True)
            )
            .with_for_update()
        )

        result = await db.execute(stmt)

        product = result.scalar_one_or_none()

        if product is None:
            await db.rollback()
            raise ProductNotFoundException()

        if product.stock < item_data.quantity:
            await db.rollback()
            raise InsufficientStockException()

        item_total = product.price * item_data.quantity

        order_item = OrderItem(
            order=order,
            product_id=product.id,
            product_name=product.name,
            quantity=item_data.quantity,
            unit_price=product.price
        )

        db.add(order_item)

        product.stock -= item_data.quantity

        total_price += item_total

    order.total_price = total_price

    try:
        await db.commit()

    except Exception:
        await db.rollback()
        raise

    await db.refresh(order)

    await db.refresh(
        order,
        attribute_names=["items"]
    )

    return order