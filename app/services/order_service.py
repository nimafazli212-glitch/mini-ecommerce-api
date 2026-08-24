from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

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
    pass