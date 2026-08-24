from datetime import datetime
from decimal import Decimal
from pydantic import BaseModel, Field


class ProductCreate(BaseModel):

    name: str = Field(
        min_length=2,
        max_length=150
    )

    description: str | None = None

    price: Decimal = Field(
        gt=0
    )

    stock: int = Field(
        ge=0
    )


class ProductResponse(BaseModel):
    id: int
    name: str
    description: str | None
    price: Decimal
    stock: int
    is_active: bool
    created_at: datetime
    
    
class ProductUpdate(BaseModel):

    name: str | None = Field(
        default=None,
        min_length=2,
        max_length=150
    )

    description: str | None = None

    price: Decimal | None = Field(
        default=None,
        gt=0
    )

    stock: int | None = Field(
        default=None,
        ge=0
    )
    
    
class ProductListResponse(BaseModel):
    items: list[ProductResponse]
    page: int
    limit: int
    total: int
    pages: int