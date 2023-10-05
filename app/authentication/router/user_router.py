from typing import Annotated

from fastapi import APIRouter, Security

from app.authentication.model.user import User, UserUpdate
from app.authentication.constant.auth_enum import ScopeEnum
from app.core.auth import get_current_active_user
from app.authentication.service.user_service import UserService

router = APIRouter(prefix="/user", tags=['user'])

user_service = UserService()


@router.get('/all', summary='Get details of all users', response_model=list[User], status_code=200)
async def get_all(user: Annotated[User, Security(get_current_active_user, scopes=[ScopeEnum.USERS_GET_ALL])]):
    return await user_service.get_all()


@router.patch('/', summary='Update user info', status_code=200)
async def patch(user_update: UserUpdate,
                user: Annotated[User, Security(get_current_active_user, scopes=[ScopeEnum.USERS_UPDATE])]):
    return await user_service.update(user=user, user_update=user_update)

