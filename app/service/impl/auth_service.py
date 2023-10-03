from fastapi import HTTPException
from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from starlette import status

from app.api.model.user import UserSignup, UserLogin, LoginToken, User, UserChangePaasword, UserSignupExternal
from app.constant import application_constant
from app.constant.application_enum import UserRoleEnum, AuthProviderEnum
from app.core.config import settings
from app.core.email_server import validate_email_format, EmailSchema, email_send
from app.core.security import get_password_hash, verify_password, create_token
from app.db import orm
from app.db.database_engine import async_session
from app.service.iauth_service import IAuthService
from app.service.impl.external_auth_service import ExternalAuthService


class AuthService(IAuthService):
    def __init__(self):
        self.external_auth_service = ExternalAuthService()

    async def signup(self, user_signup: UserSignup):
        await validate_email_format(user_signup.email)

        user = orm.User(
            email=user_signup.email,
            password=get_password_hash(user_signup.password),
            phone=user_signup.phone,
            first_name=user_signup.first_name,
            last_name=user_signup.last_name,
            email_verified=False,
            is_active=True,
            is_super_user=False,
            is_staff=False
        )

        auth_provider = orm.AuthProvider(
            provider_name=AuthProviderEnum.INTERNAL
        )

        async with async_session() as session:
            user = await self.add_user_in_db(session=session, user=user)
            auth_provider.user_id = user.id
            auth_provider.provider_user_id = str(user.id)
            await self.add_user_auth_provider(session=session, user=user, auth_provider=auth_provider)
            if not user.email_verified:
                await self.send_signup_conformation_mail(email=user.email)
            await session.commit()

        return f"user created successfully with user_id: {user.id}"

    async def user_external_signup(self, user_signup: UserSignupExternal):
        if user_signup.provider == AuthProviderEnum.GOOGLE:
            user, auth_provider = self.external_auth_service.get_user_from_google_token(user_signup.token)
            async with async_session() as session:
                user = await self.add_user_in_db(session=session, user=user)
                auth_provider.user_id = user.id
                await self.add_user_auth_provider(session=session, user=user, auth_provider=auth_provider)

                await session.commit()

            return f"user created successfully with user_id: {user.id}"
        else:
            raise HTTPException(
                detail="Invalid auth provider.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

    async def add_user_in_db(self, session, user: orm.User, default_role: UserRoleEnum = UserRoleEnum.USER):
        stmt = select(orm.User).where(orm.User.email == user.email).options(joinedload(orm.User.auth_providers))
        db_user = await session.execute(stmt)
        db_user = db_user.scalars().first()
        if db_user:
            return db_user

        session.add(user)
        await session.flush()
        await session.refresh(user, attribute_names=['auth_providers'])

        stmt = select(orm.Role).filter(orm.Role.name == default_role).limit(1)
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
        return user

    async def add_user_auth_provider(self, session, user: orm.User, auth_provider: orm.AuthProvider):
        # auth_providers = await user.auth_providers.load()
        existing_provider = [p.provider_name for p in user.auth_providers]
        if auth_provider.provider_name in existing_provider:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Already have an account.",
            )

        session.add(auth_provider)

    async def send_signup_conformation_mail(self, email: EmailStr):
        token = create_token(data={"sub": email}, expires_delta=settings.jwt.verification_token_expire_minutes)
        link = settings.app.auth_conform_url.format(token)

        email_verification_schema = EmailSchema(
            emails=[email],
            subject=settings.EMAIL.SIGNUP_EMAIL_SUBJECT,
            body=settings.EMAIL.SIGNUP_EMAIL_BODY.format(link)
        )

        await email_send(email=email_verification_schema)

    async def login(self, user_login: UserLogin):
        async with async_session() as session:
            stmt = select(orm.User).filter(orm.User.email == user_login.email).limit(1)
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
                access_token=create_token(data={"sub": user.email}),
                token_type="bearer",
                refresh_token=create_token(data={"sub": user.email},
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
            stmt = update(orm.User).where(orm.User.email == user.username).values(password=new_hashed_password)
            await session.execute(stmt)
            await session.commit()

        return 'Successfully change password'
