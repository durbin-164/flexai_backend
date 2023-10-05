import random
import string
from datetime import datetime, timedelta

from jose import jwt
from passlib.context import CryptContext

from app.core.auth_method import OAuth2PasswordBearerWithCookie
from app.core.config import settings

oauth2_scheme = OAuth2PasswordBearerWithCookie(
    tokenUrl=settings.app.token_url
)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password, hashed_password) -> bool:
    return pwd_context.verify(password, hashed_password)


def create_token(data: dict, expires_delta: int | None = None):
    to_encode = data.copy()
    if expires_delta:
        expires_delta = timedelta(minutes=expires_delta)
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.jwt.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt.secret_key, algorithm=settings.jwt.algorithm)
    return encoded_jwt


def generate_random_password(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters +
                                  string.digits, k=length))
