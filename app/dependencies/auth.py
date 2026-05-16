from typing import Annotated

from fastapi import Cookie, Depends, HTTPException, status

from app.core.security import (
    decode_access_token,
)
from app.db.db import AsyncSession
from app.models.user import User


async def get_current_user(
    *,
    db: AsyncSession,
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


CurrentUser = Annotated[User, Depends(get_current_user)]
