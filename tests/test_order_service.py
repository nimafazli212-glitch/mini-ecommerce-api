import pytest
from decimal import Decimal
from unittest.mock import AsyncMock, MagicMock

from app.services.order_service import create_order
from app.core.exceptions import (
    ProductNotFoundException,
    InsufficientStockException,
)
from app.db.models.user import User
from app.db.models.product import Product
from app.schemas.order import OrderCreate, OrderItemCreate


@pytest.mark.asyncio
async def test_create_order_success():

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()

    user = User(
        id=1,
        email="test@test.com"
    )

    product = Product(
        id=1,
        name="Test Product",
        price=Decimal("100"),
        stock=10,
        is_active=True
    )

    async def execute_mock(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = product
        return result

    db.execute.side_effect = execute_mock

    data = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=1,
                quantity=2
            )
        ]
    )

    order = await create_order(
        db=db,
        data=data,
        current_user=user
    )

    assert order.total_price == Decimal("200")
    assert product.stock == 8
    db.commit.assert_awaited_once()


@pytest.mark.asyncio
async def test_create_order_product_not_found():

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()

    user = User(
        id=1,
        email="test@test.com"
    )

    async def execute_mock(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = None
        return result

    db.execute.side_effect = execute_mock

    data = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=99,
                quantity=1
            )
        ]
    )

    with pytest.raises(ProductNotFoundException):
        await create_order(
            db=db,
            data=data,
            current_user=user
        )


@pytest.mark.asyncio
async def test_create_order_insufficient_stock():

    db = MagicMock()
    db.execute = AsyncMock()
    db.flush = AsyncMock()
    db.commit = AsyncMock()
    db.refresh = AsyncMock()
    db.rollback = AsyncMock()

    user = User(
        id=1,
        email="test@test.com"
    )

    product = Product(
        id=1,
        name="Test Product",
        price=Decimal("100"),
        stock=0,
        is_active=True
    )

    async def execute_mock(*args, **kwargs):
        result = MagicMock()
        result.scalar_one_or_none.return_value = product
        return result

    db.execute.side_effect = execute_mock

    data = OrderCreate(
        items=[
            OrderItemCreate(
                product_id=1,
                quantity=1
            )
        ]
    )

    with pytest.raises(InsufficientStockException):
        await create_order(
            db=db,
            data=data,
            current_user=user
        )
