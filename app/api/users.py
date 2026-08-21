from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.dependencies import get_db
from app.db.models.user import User
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.core.security import hash_password
from app.core.dependencies import get_current_user
from app.core.permissions import get_current_admin
from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)


@router.post("/")
async def create_user(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):
    password_hash = hash_password(user.password)

    new_user = User(
        name=user.name,
        email=user.email,
        password_hash=password_hash,
    )

    db.add(new_user)

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    await db.refresh(new_user)

    return {
        "id": new_user.id,
        "name": new_user.name,
        "email": new_user.email,
    }

@router.get("/", response_model=list[UserResponse])
async def get_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    stmt = select(User)

    result = await db.execute(stmt)

    users = result.scalars().all()

    return users


@router.get("/me", response_model=UserResponse)
async def get_me(
    current_user: User = Depends(get_current_user)
):
    return current_user


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_admin)
):
    stmt = select(User).where(User.id == user_id)

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

@router.patch("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(User).where(User.id == user_id)

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    if (
        current_user.role != "admin"
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only update your own account"
        )

    if user_data.name is not None:
        user.name = user_data.name

    if user_data.email is not None:
        user.email = user_data.email

    try:
        await db.commit()

    except IntegrityError:
        await db.rollback()

        raise HTTPException(
            status_code=409,
            detail="Email already exists"
        )

    await db.refresh(user)

    return user

@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    stmt = select(User).where(User.id == user_id)

    result = await db.execute(stmt)

    user = result.scalar_one_or_none()

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )
        
    if (
        current_user.role != "admin"
        and current_user.id != user_id
    ):
        raise HTTPException(
            status_code=403,
            detail="You can only delete your own account"
        )

    await db.delete(user)

    await db.commit()

    return {
        "message": "User deleted successfully"
    }
    
    
    
