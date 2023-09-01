from datetime import timedelta, datetime

from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from passlib.context import CryptContext
from pydantic import ValidationError
from sqlalchemy import select
from starlette import status

from app.api import model
from app.api.model.user import UserSignup, UserLogin, UserToken, TokenPayload
from app.db import orm
from app.db.database_engine import async_session
from app.service.iauth_service import IAuthService

SECRET_KEY = "012343b88e8d3e7"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
reuseable_oauth = OAuth2PasswordBearer(
    tokenUrl="/auth/token"
    # scheme_name="JWT"
)


class AuthService(IAuthService):
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)

    def verify_password(self, password, hashed_password) -> bool:
        return self.pwd_context.verify(password, hashed_password)

    async def signup_user(self, user_signup: UserSignup):
        user = orm.User(
            username=user_signup.username,
            password=self.get_password_hash(user_signup.password),
            first_name=user_signup.first_name,
            last_name=user_signup.last_name,
            is_active=True
        )

        async with async_session() as session:
            stmt = select(orm.User).filter_by(username=user_signup.username).limit(1)
            db_user = await session.execute(stmt)
            db_user = db_user.scalar_one_or_none()
            if db_user:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail=f"Use different user name.",
                )

            session.add(user)
            await session.flush()
            await session.refresh(user)
            await session.commit()

        return f"user created successfully with user_id: {user.id}"

    async def login_user(self, user_login: UserLogin):
        async with async_session() as session:
            stmt = select(orm.User).filter_by(username=user_login.username).limit(1)
            user = await session.execute(stmt)
            user = user.scalar()
            if user and self.verify_password(password=user_login.password, hashed_password=user.password):
                user_data = {
                    "username": user.username,
                    "first_name": user.first_name,
                    "last_name": user.last_name
                }
                user_token = UserToken(
                    access_token=self.create_token(data=user_data),
                    token_type="bearer",
                    refresh_token=self.create_token(data=user_data)
                )
                print(user_token)
                return user_token

        raise Exception(
            "Invalid username or password"
        )

    def create_token(self, data: dict, expires_delta: timedelta | None = None):
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    async def get_user_from_token(self, token: str = Depends(reuseable_oauth)):
        try:
            payload = jwt.decode(
                token, SECRET_KEY, algorithms=[ALGORITHM]
            )
            token_data = TokenPayload(**payload)

            if datetime.fromtimestamp(token_data.exp) < datetime.now():
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Token expired",
                    headers={"WWW-Authenticate": "Bearer"},
                )
        except(jwt.JWTError, ValidationError):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )

        async with async_session() as session:
            stmt = select(orm.User).filter_by(username=token_data.username).limit(1)
            user = await session.execute(stmt)
            user = user.scalar()

        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Could not find user",
            )

        return model.user.User.model_validate(user)
