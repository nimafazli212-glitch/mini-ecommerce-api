from datetime import datetime

import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.db.dependencies import get_db
from app.db.models.product import Product


@pytest.mark.asyncio
async def test_get_products_api_success():

    product = Product(
        id=1,
        name="Test Product",
        description="Test Description",
        price=100,
        stock=10,
        is_active=True,
        created_at=datetime.utcnow()
    )

    async def override_get_db():
        db = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        products_result = MagicMock()
        products_result.scalars.return_value.all.return_value = [
            product
        ]

        async def execute_mock(statement):
            if "count" in str(statement).lower():
                return count_result

            return products_result

        db.execute.side_effect = execute_mock

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.get(
                "/products/"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 1
        assert data["page"] == 1
        assert data["items"][0]["name"] == "Test Product"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_products_search():

    product = Product(
        id=1,
        name="Test Product",
        description="Test Description",
        price=100,
        stock=10,
        is_active=True,
        created_at=datetime.utcnow()
    )

    async def override_get_db():
        db = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 1

        products_result = MagicMock()
        products_result.scalars.return_value.all.return_value = [
            product
        ]

        async def execute_mock(statement):
            return (
                count_result
                if "count" in str(statement).lower()
                else products_result
            )

        db.execute.side_effect = execute_mock

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.get(
                "/products/?search=Test"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["total"] == 1
        assert data["items"][0]["name"] == "Test Product"

    finally:
        app.dependency_overrides.clear()



@pytest.mark.asyncio
async def test_get_products_pagination():

    products = [
        Product(
            id=1,
            name="Product 1",
            description="Test",
            price=100,
            stock=5,
            is_active=True,
            created_at=datetime.utcnow()
        )
    ]

    async def override_get_db():
        db = AsyncMock()

        count_result = MagicMock()
        count_result.scalar_one.return_value = 11

        products_result = MagicMock()
        products_result.scalars.return_value.all.return_value = products

        async def execute_mock(statement):
            if "count" in str(statement).lower():
                return count_result

            return products_result

        db.execute.side_effect = execute_mock

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.get(
                "/products/?page=2&limit=10"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["page"] == 2
        assert data["limit"] == 10
        assert data["total"] == 11
        assert data["pages"] == 2

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_product_not_found():

    async def override_get_db():
        db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = None

        db.execute.return_value = result

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.get(
                "/products/999"
            )

        assert response.status_code == 404
        assert response.json()["detail"] == "Product not found"

    finally:
        app.dependency_overrides.clear()
