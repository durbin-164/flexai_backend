from typing import Annotated

from fastapi import APIRouter, Depends, Security
from fastapi.security import OAuth2PasswordRequestForm

from app.api.model.user import UserSignup, UserLogin, LoginToken, User, UserChangePaasword, UserSignupExternal, \
    UserLoginExternal
from app.constant.application_enum import ScopeEnum
from app.core.auth import get_current_active_user
from app.service.impl.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=['auth'])

auth_service = AuthService()


@router.post("/signup", status_code=201)
async def signup(user_signup: UserSignup):
    return await auth_service.signup(user_signup=user_signup)


@router.post("/signup-external", status_code=201)
async def signup_external(user_signup: UserSignupExternal):
    return await auth_service.external_signup(user_signup=user_signup)


@router.post("/token", response_model=LoginToken, status_code=200)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_login = UserLogin(
        email=form_data.username,
        password=form_data.password
    )
    return await auth_service.login(user_login=user_login)


@router.post("/token-external", response_model=LoginToken, status_code=200)
async def login_external(user_login: UserLoginExternal):
    return await auth_service.external_login(user_login_external=user_login)


@router.get('/me', summary='Get details of currently logged in user', response_model=User, status_code=200)
async def get_me(user: Annotated[User, Security(get_current_active_user)]):
    return user


@router.patch('/change-password', summary='Password Change', status_code=200)
async def patch(password_change: UserChangePaasword,
                user: Annotated[User, Security(get_current_active_user, scopes=[ScopeEnum.USERS_UPDATE])]):
    return await auth_service.change_password(user=user, password_change=password_change)


@router.get("/confirm")
async def confirm(token: str):
    return await auth_service.conform_token(token=token)
