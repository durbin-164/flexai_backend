import random

from google.auth.transport import requests
from google.oauth2 import id_token
from pydantic import BaseModel

from app.constant.application_enum import AuthProviderEnum
from app.core.config import settings
from app.core.security import get_password_hash, generate_random_password
from app.db import orm


class GoogleTokenInfo(BaseModel):
    sub: str
    email: str
    email_verified: bool
    picture: str
    given_name: str
    family_name: str


class ExternalAuthService:
    def get_user_from_google_token(self, token: str):
        token_info = id_token.verify_oauth2_token(token, requests.Request(), settings.AUTH_PROVIDER.GOOGLE_CLIENT_ID)
        google_token_info = GoogleTokenInfo(**token_info)

        user = orm.User(
            email=google_token_info.email,
            password=get_password_hash(generate_random_password(random.randint(10, 20))),
            first_name=google_token_info.given_name,
            last_name=google_token_info.family_name,
            email_verified=google_token_info.email_verified,
            is_active=True,
            is_super_user=False,
            is_staff=False
        )

        auth_provider = orm.AuthProvider(
            provider_name=AuthProviderEnum.GOOGLE,
            provider_user_id=google_token_info.sub
        )

        return user, auth_provider
