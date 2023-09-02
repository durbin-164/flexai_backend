from fastapi import APIRouter

from app.api.router import user_router

api_router = APIRouter()
api_router.include_router(user_router.router)