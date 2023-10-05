from typing import Optional

from pydantic import BaseModel, EmailStr, Field

from app.constant.application_enum import AuthProviderEnum


class User(BaseModel):
    email: EmailStr
    first_name: str
    last_name: str
    phone: Optional[str]


class UserSignup(BaseModel):
    email: EmailStr = Field(examples=['user1@example.com'])
    password: str = Field(min_length=5, examples=['12345'])
    phone: Optional[str] = Field(min_length=5, examples=["+8801711244334"], default=None)
    first_name: str = Field(min_length=2, examples=['ABC'])
    last_name: str = Field(min_length=2, examples=['XYZ'])


class UserSignupExternal(BaseModel):
    provider: AuthProviderEnum = Field(examples=[AuthProviderEnum.GOOGLE])
    token: str


class UserLogin(BaseModel):
    email: EmailStr = Field(examples=['user1@example.com'])
    password: str = Field(min_length=5, examples=['12345'])


class UserLoginExternal(BaseModel):
    provider: AuthProviderEnum = Field(examples=[AuthProviderEnum.GOOGLE])
    token: str


class LoginToken(BaseModel):
    access_token: str
    token_type: str
    refresh_token: str


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = Field(examples=['user1@example.com'], default=None)
    phone: Optional[str] = Field(min_length=5, examples=["+8801711244334"], default=None)
    first_name: Optional[str] = Field(min_length=2, examples=['ABC'], default=None)
    last_name: Optional[str] = Field(min_length=2, examples=['XYZ'], default=None)


class UserChangePaasword(BaseModel):
    previous_password: str = Field(min_length=5, examples=['12345'])
    new_password: str = Field(min_length=5, examples=['12345'])
