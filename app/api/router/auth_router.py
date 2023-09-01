from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.model.user import UserSignup, UserLogin, UserToken, User
from app.service.impl.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=['auth'])

auth_service = AuthService()


@router.post("/signup", status_code=201)
async def signup(user_signup: UserSignup):
    return await auth_service.signup_user(user_signup=user_signup)


@router.post("/token", response_model=UserToken, status_code=200)
async def login(form_data: Annotated[OAuth2PasswordRequestForm, Depends()]):
    user_login = UserLogin(
        username=form_data.username,
        password=form_data.password
    )
    return await auth_service.login_user(user_login=user_login)


@router.get('/me', summary='Get details of currently logged in user', response_model=User, status_code=200)
async def get_me(user: User = Depends(auth_service.get_user_from_token)):
    return user
