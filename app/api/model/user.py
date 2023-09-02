from pydantic import BaseModel


class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    is_active: bool


class UserSignup(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str


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
