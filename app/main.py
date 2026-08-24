from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.users import router as users_router
from app.api.products import router as products_router
from app.api.auth import router as auth_router
from app.api.orders import router as orders_router
from app.core.exceptions import OrderException
from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError

from app.core.exception_handlers import (
    order_exception_handler,
    http_exception_handler,
    validation_exception_handler,
)


app = FastAPI()
app.add_exception_handler(
    OrderException,
    order_exception_handler
)
app.add_exception_handler(
    HTTPException,
    http_exception_handler
)

app.add_exception_handler(
    RequestValidationError,
    validation_exception_handler
)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users_router)
app.include_router(products_router)
app.include_router(auth_router)
app.include_router(orders_router)

@app.get("/")
async def root():
    return {
        "message": "Mini E-Commerce API - Discount Feature",
        "version": "2.0.0"
    }