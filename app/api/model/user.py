from typing import Optional

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    is_active: bool


class UserSignup(BaseModel):
    username: str
    password: str
    email: Optional[EmailStr]
    phone: Optional[str]
    first_name: Optional[str]
    last_name: Optional[str]


class UserLogin(BaseModel):
    username: str
    password: str


class LoginToken(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
