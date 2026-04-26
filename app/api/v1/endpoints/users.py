from fastapi import APIRouter, HTTPException, Request, Response, status

from app.core.config import settings
from app.core.security import refresh_access_token
from app.crud.users import create_user_service, login_service
from app.db.db import DBSession
from app.schemas.users import LoginRequest, UserCreate, UserResponse

router = APIRouter(tags=["Users"])


@router.post("/sign-up", response_model=UserResponse)
async def create_user(db: DBSession, user_in: UserCreate):
    user = await create_user_service(db=db, user_in=user_in)

    return user


@router.post("/login")
async def login(
    db: DBSession,
    credentials: LoginRequest,
    response: Response,
):
    await login_service(
        db=db,
        response=response,
        credentials=credentials,
    )

    return {"message": "Logged in"}


@router.post("/refresh")
async def refresh_token(request: Request, response: Response, db: DBSession):
    """Get a new access token using refresh token from cookies"""
    refresh_token = request.cookies.get("refresh_token")

    if not refresh_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token missing"
        )

    try:
        new_access_token = refresh_access_token(refresh_token=refresh_token)

        response.set_cookie(
            key="access_token",
            value=new_access_token,
            httponly=True,
            secure=True,
            samesite="lax",
            max_age=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )

        return {"message": "Token refreshed successfully"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e)
        ) from e


@router.post("/logout")
async def logout(response: Response):
    """Clear authentication cookies"""
    response.delete_cookie("access_token")
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}
