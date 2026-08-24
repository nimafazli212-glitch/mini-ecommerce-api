import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock
from app.api import orders
from app.main import app
from app.db.dependencies import get_db
from app.core.dependencies import get_current_user
from app.db.models.user import User
from datetime import datetime


@pytest.mark.asyncio
async def test_create_order_api_success():

    fake_user = User(
        id=1,
        email="test@test.com"
    )

    async def override_current_user():
        return fake_user

    async def override_get_db():
        yield AsyncMock()

    app.dependency_overrides[get_current_user] = override_current_user
    app.dependency_overrides[get_db] = override_get_db

    fake_order = {
        "id": 1,
        "user_id": 1,
        "status": "pending",
        "total_price": 200,
        "created_at": datetime.now(),
        "items": []
    }

    async def fake_create_order(
        db,
        data,
        current_user
    ):
        return fake_order

    original = orders.create_order_service
    orders.create_order_service = fake_create_order

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.post(
                "/orders/",
                json={
                    "items": [
                        {
                            "product_id": 1,
                            "quantity": 2
                        }
                    ]
                }
            )

        assert response.status_code == 201
        assert response.json()["id"] == 1

    finally:
        orders.create_order_service = original
        app.dependency_overrides.clear()
