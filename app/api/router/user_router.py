from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm

from app.api.model.user import UserSignup, UserLogin, LoginToken, User
from app.core.auth import get_current_active_user
from app.service.impl.user_service import UserService

router = APIRouter(prefix="/user", tags=['user'])

user_service = UserService()


@router.post("/signup", status_code=201)
async def signup(user_signup: UserSignup):
    return await user_service.signup(user_signup=user_signup)


@router.post("/token", response_model=LoginToken, status_code=200)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_login = UserLogin(
        username=form_data.username,
        password=form_data.password
    )
    return await user_service.login(user_login=user_login)


@router.get('/me', summary='Get details of currently logged in user', response_model=User, status_code=200)
async def get_me(user: Annotated[User, Security(get_current_active_user)]):
    return user
