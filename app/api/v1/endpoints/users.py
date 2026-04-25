from fastapi import APIRouter

from app.crud.users import create_user_service
from app.db.db import DBSession
from app.schemas.users import UserCreate, UserResponse

router = APIRouter()


@router.post("/sign-up", response_model=UserResponse)
async def create_user(db: DBSession, user_in: UserCreate):
    user = await create_user_service(db=db, user_in=user_in)

    return user


# @router.post("/login")
# async def login(
#     db: DBSession,
#     credentials: LoginRequest,
#     response: Response,
#     redis_client: RedisClient,
# ):
#     await login_service(
#         db=db, response=response, credentials=credentials, redis_client=redis_client
#     )

#     return {"message": "Logged in"}


# @router.post("/logout")
# async def logout(
#     response: Response,
#     redis_client: RedisClient,
#     refresh_token: Annotated[str | None, Cookie(include_in_schema=False)] = None,
# ):
#     await logout_service(
#         refresh_token=refresh_token, response=response, redis_client=redis_client
#     )

#     return {"message": "Logged out"}


# @router.post("/refresh")
# async def refresh_access_token(
#     response: Response,
#     redis_client: RedisClient,
#     refresh_token: Annotated[str | None, Cookie(include_in_schema=False)] = None,
# ):
#     await refresh_access_token_service(
#         response=response, refresh_token=refresh_token, redis_client=redis_client
#     )

#     return {"message": "refreshed"}
