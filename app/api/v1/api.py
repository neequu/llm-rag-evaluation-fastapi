from fastapi import APIRouter

from app.api.v1.endpoints import users, workspace

api_router = APIRouter()

api_router.include_router(users.router)
api_router.include_router(workspace.router)
