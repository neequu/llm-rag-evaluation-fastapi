from typing import Annotated

from fastapi import Cookie, HTTPException, Response, status
from sqlalchemy import select

from app.core.config import settings
from app.core.security import (
    create_access_token,
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
        email=user_in.email, name=user_in.name, password=hash_password(user_in.password)
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
    # redis_client: RedisClient,
):
    user = await get_by_email_service(db=db, email=credentials.email)

    if not user or not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    access_token = create_access_token(user_id=user.id)
    # refresh_token = create_refresh_token()

    # redis_key = f"refresh:{refresh_token}"

    # await redis_client.set(
    #     redis_key,
    #     user.id,
    #     ex=settings.refresh_token_expire_days * 86400,
    # )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.jwt_expire_minutes * 60,
    )
    response.set_cookie(
        key="refresh_token",
        # value=refresh_token,
        httponly=True,
        secure=True,
        samesite="lax",
        max_age=settings.refresh_token_expire_days * 86400,
    )


async def logout_service(
    *,
    response: Response,
    refresh_token: Annotated[str | None, Cookie(include_in_schema=False)] = None,
    # redis_client: RedisClient,
):
    # if refresh_token:
    #     await redis_client.delete(f"refresh:{refresh_token}")

    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out"}


async def refresh_access_token_service(
    *,
    refresh_token: Annotated[str | None, Cookie(include_in_schema=False)] = None,
    response: Response,
    # redis_client: RedisClient,
):
    if refresh_token is None:
        raise HTTPException(401, "Missing refresh token")

    redis_key = f"refresh:{refresh_token}"
    # user_id = await redis_client.get(redis_key)

    # if user_id is None:
    #     raise HTTPException(
    #         status_code=status.HTTP_401_UNAUTHORIZED,
    #         detail="Invalid refresh token",
    #     )

    # new_access_token = create_access_token(user_id=int(user_id))

    # response.set_cookie("access_token", new_access_token, httponly=True, secure=True)

    return {"message": "refreshed"}


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
