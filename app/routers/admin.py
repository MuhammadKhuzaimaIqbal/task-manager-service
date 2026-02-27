from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.routers.auth import CurrentUser
from app.schemas.user import UserResponse


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[UserResponse])
async def list_users(
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    result = await db.execute(select(User))
    return result.scalars().all()


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    current_user: CurrentUser,
    db: AsyncSession = Depends(get_db),
):
    if current_user.role != UserRole.admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )

    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    await db.delete(user)
    await db.commit()

