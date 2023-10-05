from fastapi import APIRouter

from app.authentication.router import auth_router, user_router

api_router = APIRouter()
api_router.include_router(auth_router.router)
api_router.include_router(user_router.router)
