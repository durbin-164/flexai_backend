from fastapi import HTTPException
from sqlalchemy import select
from starlette import status

from app.api.model.user import UserSignup, UserLogin, LoginToken
from app.core.security import get_password_hash, verify_password, create_token
from app.db import orm
from app.db.database_engine import async_session
from app.service.iuser_service import IUserService


class UserService(IUserService):
    async def signup(self, user_signup: UserSignup):
        user = orm.User(
            username=user_signup.username,
            password=get_password_hash(user_signup.password),
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

    async def login(self, user_login: UserLogin):
        async with async_session() as session:
            stmt = select(orm.User).filter_by(username=user_login.username).limit(1)
            user = await session.execute(stmt)
            user = user.scalar()
            if not user:
                raise HTTPException(
                    detail="Invalid username.",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )
            if not verify_password(password=user_login.password, hashed_password=user.password):
                raise HTTPException(
                    detail="Invalid password",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

            user_token = LoginToken(
                access_token=create_token(data={"sub": user.username, "scopes": ["me"]}),
                token_type="bearer",
                refresh_token=create_token(data={"sub": user.username})
            )
            return user_token





