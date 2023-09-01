from pydantic import BaseModel, ConfigDict


class User(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    username: str
    # password: str
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


class UserToken(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class TokenPayload(BaseModel):
    exp: int = None
    username: str
    first_name: str
    last_name: str