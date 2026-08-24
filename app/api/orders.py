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
from app.services.order_service import create_order as create_order_service


router = APIRouter(
    prefix="/orders",
    tags=["Orders"]
)


@router.post(
    "/",
    response_model=OrderDetailResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create order",
    description="Create a new order for the authenticated user."
)
async def create_order(
    data: OrderCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    order = await create_order_service(
        db=db,
        data=data,
        current_user=current_user
    )

    return order

@router.get(
    "/",
    response_model=list[OrderResponse],
    summary="Get my orders",
    description="Retrieve all orders of the authenticated user."
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
    response_model=OrderDetailResponse,
    summary="Get order details",
    description="Retrieve a user's order with order items.",
    responses={
        404: {
            "description": "Order not found"
        }
    }
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
    response_model=OrderResponse,
    summary="Cancel order",
    description="Cancel a pending order and restore product stock.",
    responses={
        400: {
            "description": "Order cannot be cancelled"
        },
        404: {
            "description": "Order or product not found"
        }
    }
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
    response_model=OrderResponse,
    summary="Update order status",
    description="Update order status. Admin access required.",
    responses={
        400: {
            "description": "Invalid status transition"
        },
        404: {
            "description": "Order not found"
        }
    }
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
    response_model=list[OrderResponse],
    summary="Get all orders",
    description="Admin endpoint to retrieve all orders."
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
    response_model=OrderDetailResponse,
    summary="Get order by ID for admin",
    description="Admin endpoint to retrieve any order.",
    responses={
        404: {
            "description": "Order not found"
        }
    }
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