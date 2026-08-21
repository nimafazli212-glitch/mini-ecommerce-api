from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload
from app.core.permissions import get_current_admin
from app.db.dependencies import get_db
from app.db.models.order import Order, OrderStatus
from app.db.models.order_item import OrderItem
from app.db.models.product import Product
from app.db.models.user import User
from app.schemas.order import (
    OrderCreate,
    OrderResponse,
    OrderDetailResponse,
    OrderStatusUpdate,
)
from app.core.dependencies import get_current_user


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "/",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_201_CREATED
)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Order must contain at least one item"
        )

    order = Order(
        user_id=current_user.id,
        status=OrderStatus.PENDING,
        total_price=0
    )

    db.add(order)

    await db.flush()

    total_price = 0

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

            raise HTTPException(
                status_code=404,
                detail=f"Product {item_data.product_id} not found"
            )

        if product.stock < item_data.quantity:
            await db.rollback()

            raise HTTPException(
                status_code=400,
                detail=f"Not enough stock for product {product.id}"
            )

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

    await db.commit()

    await db.refresh(order)
    await db.refresh(order, ["items"])

    return order

@router.get(
    "/",
    response_model=list[OrderResponse]
)
async def get_my_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Order)
        .where(Order.user_id == current_user.id)
        .order_by(Order.created_at.desc())
    )

    result = await db.execute(stmt)

    orders = result.scalars().all()

    return orders



@router.get(
    "/{order_id}",
    response_model=OrderDetailResponse
)
async def get_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )

    result = await db.execute(stmt)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order


@router.patch(
    "/{order_id}/cancel",
    response_model=OrderResponse
)
async def cancel_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(
            Order.id == order_id,
            Order.user_id == current_user.id
        )
    )

    result = await db.execute(stmt)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=400,
            detail="Only pending orders can be cancelled"
        )

    for item in order.items:

        product_stmt = (
            select(Product)
            .where(Product.id == item.product_id)
            .with_for_update()
        )

        product_result = await db.execute(product_stmt)

        product = product_result.scalar_one_or_none()

        if product is None:
            await db.rollback()

            raise HTTPException(
                status_code=404,
                detail="Product not found"
            )

        product.stock += item.quantity

    order.status = OrderStatus.CANCELLED

    await db.commit()
    await db.refresh(order)

    return order


@router.patch(
    "/{order_id}/status",
    response_model=OrderResponse
)
async def update_order_status(
    order_id: int,
    data: OrderStatusUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    stmt = (
        select(Order)
        .where(
            Order.id == order_id
        )
    )

    result = await db.execute(stmt)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    allowed_transitions = {
        OrderStatus.PENDING: [OrderStatus.CONFIRMED],
        OrderStatus.CONFIRMED: [OrderStatus.SHIPPED],
        OrderStatus.SHIPPED: [OrderStatus.DELIVERED],
        OrderStatus.DELIVERED: [],
        OrderStatus.CANCELLED: []
    }

    if data.status not in allowed_transitions[order.status]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot change order status from "
                   f"{order.status} to {data.status}"
    )

    order.status = data.status

    await db.commit()
    await db.refresh(order)

    return order


@router.get(
    "/admin/all",
    response_model=list[OrderResponse]
)
async def get_all_orders(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    stmt = (
        select(Order)
        .order_by(Order.created_at.desc())
    )

    result = await db.execute(stmt)

    orders = result.scalars().all()

    return orders


@router.get(
    "/admin/{order_id}",
    response_model=OrderDetailResponse
)
async def get_admin_order(
    order_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    stmt = (
        select(Order)
        .options(selectinload(Order.items))
        .where(Order.id == order_id)
    )

    result = await db.execute(stmt)

    order = result.scalar_one_or_none()

    if order is None:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    return order