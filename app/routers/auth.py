from typing import Annotated
from datetime import datetime, timedelta
import bcrypt
from jose import JWTError, jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.config import settings
from app.database import get_db
from app.models.user import User, UserRole
from app.schemas.user import (
    UserCreate,
    UserLogin,
    UserResponse,
    Token,
    TokenRefreshRequest,
)


router = APIRouter(prefix="/auth", tags=["Auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(password: str) -> str:
    """Hash a plain-text password using bcrypt."""
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plain-text password against a bcrypt hash."""
    return bcrypt.checkpw(
        plain_password.encode("utf-8"), hashed_password.encode("utf-8")
    )


def _create_token(
    data: dict, expires_delta: timedelta, token_type: str
) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expire, "type": token_type})
    encoded_jwt = jwt.encode(
        to_encode, settings.jwt_secret_key, algorithm=settings.jwt_algorithm
    )
    return encoded_jwt


def create_access_token(data: dict) -> str:
    """Create a signed JWT access token."""
    return _create_token(
        data, timedelta(minutes=settings.access_token_expire_minutes), "access"
    )


def create_refresh_token(data: dict) -> str:
    """Create a signed JWT refresh token."""
    return _create_token(
        data, timedelta(minutes=settings.refresh_token_expire_minutes), "refresh"
    )


DBSession = Annotated[AsyncSession, Depends(get_db)]


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(user_in: UserCreate, db: DBSession):
    # Check if email already exists
    result = await db.execute(select(User).where(User.email == user_in.email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already registered",
        )

    hashed_pw = hash_password(user_in.password)

    new_user = User(
        email=user_in.email,
        username=user_in.username,
        hashed_password=hashed_pw,
        role=UserRole.user,
        is_active=True,
    )

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)

    return new_user


@router.post("/login", response_model=Token)
async def login(user_in: UserLogin, db: DBSession):
    result = await db.execute(select(User).where(User.email == user_in.email))
    user = result.scalar_one_or_none()

    if not user or not verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive",
        )

    access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    refresh_token = create_refresh_token(data={"sub": str(user.id)})
    return Token(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/refresh", response_model=Token)
async def refresh_token(
    token_request: TokenRefreshRequest,
    db: DBSession,
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate refresh token",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token_request.refresh_token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        token_type = payload.get("type")
        sub = payload.get("sub")
        if token_type != "refresh" or sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, int(sub))
    if not user or not user.is_active:
        raise credentials_exception

    new_access_token = create_access_token(
        data={"sub": str(user.id), "role": user.role.value}
    )
    new_refresh_token = create_refresh_token(data={"sub": str(user.id)})

    return Token(
        access_token=new_access_token,
        refresh_token=new_refresh_token,
        token_type="bearer",
    )


async def get_current_user(
    db: DBSession,
    token: str = Depends(oauth2_scheme),
) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        token_type = payload.get("type")
        sub = payload.get("sub")
        if token_type != "access" or sub is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user = await db.get(User, int(sub))
    if user is None or not user.is_active:
        raise credentials_exception

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]

