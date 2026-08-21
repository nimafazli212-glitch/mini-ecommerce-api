from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.db.dependencies import get_db
from app.db.models.product import Product
from app.schemas.product import (
    ProductCreate,
    ProductResponse,
    ProductUpdate,
    ProductListResponse,
)
from app.core.dependencies import get_current_user
from app.db.models.user import User
from app.core.permissions import get_current_admin
import math
router = APIRouter(
    prefix="/products",
    tags=["Products"]
)


@router.post("/", response_model=ProductResponse)
async def create_product(
    product_data: ProductCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        stock=product_data.stock,
    )

    db.add(new_product)

    await db.commit()

    await db.refresh(new_product)

    return new_product


@router.get("/", response_model=ProductListResponse)
async def get_products(
    page: int = Query(1, ge=1),
    limit: int = Query(10, ge=1, le=100),
    search: str | None = Query(None, min_length=1),
    min_price: float | None = Query(None, gt=0),
    max_price: float | None = Query(None, gt=0),
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Product)
        .where(Product.is_active.is_(True))
    )

    count_stmt = (
        select(func.count(Product.id))
        .where(Product.is_active.is_(True))
    )

    if search:
        condition = Product.name.ilike(f"%{search}%")

        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if min_price is not None:
        condition = Product.price >= min_price

        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    if max_price is not None:
        condition = Product.price <= max_price

        stmt = stmt.where(condition)
        count_stmt = count_stmt.where(condition)

    count_result = await db.execute(count_stmt)

    total = count_result.scalar_one()

    stmt = (
        stmt
        .order_by(Product.created_at.desc())
        .offset((page - 1) * limit)
        .limit(limit)
    )

    result = await db.execute(stmt)

    products = result.scalars().all()

    pages = math.ceil(total / limit)

    return {
        "items": products,
        "page": page,
        "limit": limit,
        "total": total,
        "pages": pages,
    }
@router.get("/{product_id}", response_model=ProductResponse)
async def get_product(
    product_id: int,
    db: AsyncSession = Depends(get_db)
):
    stmt = (
        select(Product)
        .where(
            Product.id == product_id,
            Product.is_active.is_(True)
        )
    )
    result = await db.execute(stmt)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    return product


@router.patch("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_data: ProductUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    stmt = select(Product).where(Product.id == product_id)

    result = await db.execute(stmt)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    if product_data.name is not None:
        product.name = product_data.name

    if product_data.description is not None:
        product.description = product_data.description

    if product_data.price is not None:
        product.price = product_data.price

    if product_data.stock is not None:
        product.stock = product_data.stock

    await db.commit()

    await db.refresh(product)

    return product


@router.delete("/{product_id}")
async def delete_product(
    product_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    stmt = select(Product).where(Product.id == product_id)

    result = await db.execute(stmt)

    product = result.scalar_one_or_none()

    if product is None:
        raise HTTPException(
            status_code=404,
            detail="Product not found"
        )

    product.is_active = False

    await db.commit()
    await db.refresh(product)

    return {
        "message": "Product deactivated successfully"
    }