from httpx import AsyncClient, ASGITransport
from unittest.mock import AsyncMock, MagicMock
from app.core.dependencies import get_current_user, get_db
from app.db.models.user import User
import pytest
from app.main import app



@pytest.mark.asyncio
async def test_create_user_success():

    async def override_get_db():

        db = MagicMock()

        db.commit = AsyncMock()
        db.refresh = AsyncMock()

        user = MagicMock()
        user.id = 1
        user.name = "Test User"
        user.email = "test@test.com"

        async def refresh_mock(obj):
            obj.id = user.id
            obj.name = user.name
            obj.email = user.email

        db.refresh.side_effect = refresh_mock

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.post(
                "/users/",
                json={
                    "name": "Test User",
                    "email": "test@test.com",
                    "password": "123456"
                }
            )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["email"] == "test@test.com"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_create_user_duplicate_email():

    async def override_get_db():

        db = MagicMock()

        db.commit = AsyncMock()
        db.rollback = AsyncMock()

        from sqlalchemy.exc import IntegrityError

        async def commit_mock():
            raise IntegrityError(
                "duplicate",
                {},
                Exception("duplicate email")
            )

        db.commit.side_effect = commit_mock

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.post(
                "/users/",
                json={
                    "name": "Test User",
                    "email": "test@test.com",
                    "password": "123456"
                }
            )

        assert response.status_code == 409
        assert response.json()["error"]["message"] == "Email already exists"
    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_get_me():

    user = User(
        id=1,
        name="Test User",
        email="test@test.com",
        password_hash="hashed-password",
        role="customer"
    )

    async def override_current_user():
        return user

    app.dependency_overrides[get_current_user] = override_current_user

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.get(
                "/users/me"
            )

        assert response.status_code == 200

        data = response.json()

        assert data["id"] == 1
        assert data["email"] == "test@test.com"

    finally:
        app.dependency_overrides.clear()



@pytest.mark.asyncio
async def test_update_other_user_forbidden():

    current_user = User(
        id=1,
        name="Current User",
        email="current@test.com",
        password_hash="hash",
        role="customer"
    )

    async def override_current_user():
        return current_user

    app.dependency_overrides[get_current_user] = override_current_user

    async def override_get_db():
        db = MagicMock()
        db.execute = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = User(
            id=2,
            name="Other User",
            email="other@test.com",
            password_hash="hash",
            role="customer"
        )

        db.execute.return_value = result

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.patch(
                "/users/2",
                json={
                    "name": "Hacker"
                }
            )

        assert response.status_code == 403
        assert response.json()["error"]["message"] == "You can only update your own account"

    finally:
        app.dependency_overrides.clear()


@pytest.mark.asyncio
async def test_delete_other_user_forbidden():

    current_user = User(
        id=1,
        name="Current User",
        email="current@test.com",
        password_hash="hash",
        role="customer"
    )

    async def override_current_user():
        return current_user

    app.dependency_overrides[get_current_user] = override_current_user

    async def override_get_db():

        db = MagicMock()
        db.execute = AsyncMock()

        result = MagicMock()
        result.scalar_one_or_none.return_value = User(
            id=2,
            name="Other User",
            email="other@test.com",
            password_hash="hash",
            role="customer"
        )

        db.execute.return_value = result

        yield db

    app.dependency_overrides[get_db] = override_get_db

    try:
        transport = ASGITransport(app=app)

        async with AsyncClient(
            transport=transport,
            base_url="http://test"
        ) as client:

            response = await client.delete(
                "/users/2"
            )

        assert response.status_code == 403
        assert response.json()["error"]["message"] == "You can only delete your own account"

    finally:
        app.dependency_overrides.clear()
