from fastapi import APIRouter

from app.admin.router import auth_router

admin_router = APIRouter(prefix="/admin")
admin_router.include_router(auth_router.router)