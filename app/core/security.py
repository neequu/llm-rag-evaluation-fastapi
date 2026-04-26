from datetime import datetime, timedelta, timezone
from uuid import UUID

import bcrypt
from jose import JWTError, jwt

from app.core.config import settings


def hash_password(password: str) -> str:
    """Hash a password using bcrypt directly."""
    password_bytes = password.encode("utf-8")

    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password_bytes, salt)

    return hashed_bytes.decode("utf-8")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    try:
        plain_bytes = plain_password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        return False


def create_access_token(*, user_id: UUID) -> str:
    expire = datetime.now(tz=timezone.utc) + timedelta(
        minutes=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "access",
    }

    print(settings)

    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_access_token(token: str) -> UUID:
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )
        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise ValueError("Missing subject")
        return UUID(user_id)
    except JWTError as exc:
        raise ValueError("Invalid token") from exc


def create_refresh_token(*, user_id: UUID) -> str:
    """Create a refresh token with longer expiry."""
    expire = datetime.now(tz=timezone.utc) + timedelta(
        days=settings.REFRESH_TOKEN_EXPIRE_DAYS
    )

    payload = {
        "sub": str(user_id),
        "exp": expire,
        "type": "refresh",
    }

    return jwt.encode(
        payload, settings.JWT_SECRET_KEY, algorithm=settings.JWT_ALGORITHM
    )


def decode_refresh_token(token: str) -> UUID:
    """Decode and validate refresh token."""
    try:
        payload = jwt.decode(
            token, settings.JWT_SECRET_KEY, algorithms=[settings.JWT_ALGORITHM]
        )

        if payload.get("type") != "refresh":
            raise ValueError("Invalid token type")

        user_id: str | None = payload.get("sub")
        if user_id is None:
            raise ValueError("Missing subject")
        return UUID(user_id)
    except JWTError as exc:
        raise ValueError("Invalid refresh token") from exc


def refresh_access_token(*, refresh_token: str) -> str:
    """Generate a new access token from a valid refresh token."""
    user_id = decode_refresh_token(refresh_token)
    return create_access_token(user_id=user_id)
