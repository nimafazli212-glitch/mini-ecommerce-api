import pytest
from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock

from app.main import app
from app.db.dependencies import get_db
from app.db.models.user import User
from app.core.security import hash_password


@pytest.mark.asyncio
async def test_login_success():

    user = User(
        id=1,
        name="Test User",
        email="test@test.com",
        password_hash=hash_password("123456"),
        role="customer"
    )

    async def override_get_db():

        db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = user

        db.execute.return_value = result

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.post(
                "/auth/login",
                json={
                    "email": "test@test.com",
                    "password": "123456"
                }
            )

        assert response.status_code == 200

        data = response.json()

        assert "access_token" in data
        assert data["token_type"] == "bearer"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_wrong_password():

    user = User(
        id=1,
        name="Test User",
        email="test@test.com",
        password_hash=hash_password("123456"),
        role="customer"
    )

    async def override_get_db():

        db = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = user

        db.execute.return_value = result

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.post(
                "/auth/login",
                json={
                    "email": "test@test.com",
                    "password": "wrong-password"
                }
            )

        assert response.status_code == 401
        assert response.json()["error"]["message"] == "Invalid email or password"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_login_user_not_found():

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

            response = await client.post(
                "/auth/login",
                json={
                    "email": "none@test.com",
                    "password": "123456"
                }
            )

        assert response.status_code == 401
        assert response.json()["error"]["message"] == "Invalid email or password"

    finally:
        app.dependency_overrides.clear()
