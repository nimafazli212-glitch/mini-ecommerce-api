from fastapi import Request
from fastapi.responses import JSONResponse

from app.core.exceptions import (
    OrderException,
    ProductNotFoundException,
    OrderNotFoundException,
    InsufficientStockException,
    EmptyOrderException,
    InvalidOrderStatusException,
)


async def order_exception_handler(
    request: Request,
    exc: OrderException,
):
    status_code = 400
    error_code = "ORDER_ERROR"
    message = str(exc) or "Order error"

    if isinstance(exc, ProductNotFoundException):
        status_code = 404
        error_code = "PRODUCT_NOT_FOUND"
        message = "Product not found"

    elif isinstance(exc, OrderNotFoundException):
        status_code = 404
        error_code = "ORDER_NOT_FOUND"
        message = "Order not found"

    elif isinstance(exc, InsufficientStockException):
        status_code = 400
        error_code = "INSUFFICIENT_STOCK"
        message = "Insufficient stock"

    elif isinstance(exc, EmptyOrderException):
        status_code = 400
        error_code = "EMPTY_ORDER"
        message = "Order must contain at least one item"

    elif isinstance(exc, InvalidOrderStatusException):
        status_code = 400
        error_code = "INVALID_ORDER_STATUS"
        message = "Invalid order status"

    return JSONResponse(
        status_code=status_code,
        content={
            "success": False,
            "error": {
                "code": error_code,
                "message": message,
            },
        },
    )
