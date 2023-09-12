from typing import Optional

from pydantic import BaseModel, EmailStr, Field


class User(BaseModel):
    username: str
    first_name: str
    last_name: str
    email: Optional[str]
    phone: Optional[str]


class UserSignup(BaseModel):
    username: str = Field(min_length=2, examples=['user1'])
    password: str = Field(min_length=5, examples=['12345'])
    email: EmailStr = Field(examples=['user1@example.com'])
    phone: str = Field(min_length=5, examples=["+8801711244334"])
    first_name: str = Field(min_length=2, examples=['ABC'])
    last_name: str = Field(min_length=2, examples=['XYZ'])


class UserLogin(BaseModel):
    username: str = Field(min_length=2, examples=['user1'])
    password: str = Field(min_length=5, examples=['12345'])


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
