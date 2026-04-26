from typing import Annotated

from fastapi import Cookie, HTTPException, Response, status
from sqlalchemy import select

from app.core.config import settings
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.db.db import DBSession
from app.models import User
from app.schemas.users import LoginRequest, UserCreate


async def get_by_email_service(db: DBSession, email: str):
    result = await db.scalar(select(User).filter_by(email=email))
    return result


async def create_user_service(*, db: DBSession, user_in: UserCreate):
    existing_user = await get_by_email_service(db=db, email=user_in.email)

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=user_in.email,
        name=user_in.name,
        password_hash=hash_password(user_in.password),
    )

    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def login_service(
    *,
    db: DBSession,
    credentials: LoginRequest,
    response: Response,
):
    user = await get_by_email_service(db=db, email=credentials.email)

    if not user or not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user_id=user.id)
    refresh_token = create_refresh_token(user_id=user.id)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )
    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )

    return {
        "message": "Login successful",
    }


async def get_current_user(
    *,
    db: DBSession,
    access_token: Annotated[str | None, Cookie(include_in_schema=False)] = None,
) -> User:
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    try:
        user_id = decode_access_token(access_token)
    except Exception as err:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        ) from err

    user = await db.get(User, user_id)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
        )

    return user
