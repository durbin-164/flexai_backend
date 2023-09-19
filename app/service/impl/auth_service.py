from fastapi import HTTPException
from sqlalchemy import select, update
from starlette import status

from app.api.model.user import UserSignup, UserLogin, LoginToken, User, UserChangePaasword
from app.constant import application_constant
from app.constant.application_enum import UserRoleEnum
from app.core.config import settings
from app.core.email_server import validate_email_format, EmailSchema, email_send
from app.core.security import get_password_hash, verify_password, create_token
from app.db import orm
from app.db.database_engine import async_session
from app.service.iauth_service import IAuthService


class AuthService(IAuthService):
    async def signup(self, user_signup: UserSignup):
        await validate_email_format(user_signup.email)

        user = orm.User(
            username=user_signup.email,
            password=get_password_hash(user_signup.password),
            email=user_signup.email,
            phone=user_signup.phone,
            first_name=user_signup.first_name,
            last_name=user_signup.last_name,
            is_active=True,
            is_super_user=False,
            is_staff=False
        )

        token = create_token(data={"sub": user.email}, expires_delta=1440)
        link = f"{settings.app.url}/auth/confirm?token={token}"

        email_verification_schema = EmailSchema(
            emails=[user.email],
            subject=application_constant.REGISTRATION_EMAIL_SUBJECT,
            body=application_constant.REGISTRATION_EMAIL_BODY.format(link)
        )

        async with async_session() as session:
            stmt = select(orm.User).filter_by(username=user.username).limit(1)
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

            stmt = select(orm.Role).filter(orm.Role.name == UserRoleEnum.USER).limit(1)
            db_role = await session.execute(stmt)
            db_role = db_role.scalar_one_or_none()
            if not db_role:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Something went wrong.",
                )

            user_role_association = orm.UserRoleAssociation(
                user_id=user.id,
                role_id=db_role.id
            )
            session.add(user_role_association)

            await email_send(email=email_verification_schema)

            await session.commit()

        return f"user created successfully with user_id: {user.id}"

    async def login(self, user_login: UserLogin):
        async with async_session() as session:
            stmt = select(orm.User).filter_by(username=user_login.username).limit(1)
            user = await session.execute(stmt)
            user = user.scalar()
            if not user or not user.is_active:
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
                # access_token=create_token(data={"sub": user.username, "scopes": ["me"]}),
                access_token=create_token(data={"sub": user.username}),
                token_type="bearer",
                refresh_token=create_token(data={"sub": user.username},
                                           expires_delta=settings.jwt.refresh_token_expire_minutes)
            )
            return user_token

    async def change_password(self, user: User, password_change: UserChangePaasword):
        if not verify_password(password=password_change.previous_password, hashed_password=user.password):
            raise HTTPException(
                detail="Invalid previous password",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        new_hashed_password = get_password_hash(password_change.new_password)

        async with async_session() as session:
            stmt = update(orm.User).where(orm.User.username == user.username).values(password=new_hashed_password)
            await session.execute(stmt)
            await session.commit()

        return 'Successfully change password'
