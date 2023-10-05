from fastapi import HTTPException
from fastapi.security import SecurityScopes
from pydantic import EmailStr
from sqlalchemy import select, update
from sqlalchemy.orm import joinedload
from starlette import status

from app.authentication.model.user import UserSignup, UserLogin, LoginToken, User, UserChangePaasword, UserSignupExternal, \
    UserLoginExternal
from app.authentication.service.external_auth_service import ExternalAuthService
from app.authentication.constant.auth_enum import UserRoleEnum, AuthProviderEnum
from app.core.auth import get_valid_user
from app.core.config import settings
from app.core.email_server import validate_email_format, EmailSchema, email_send
from app.core.security import get_password_hash, verify_password, create_token
from app.db import orm
from app.db.database_engine import async_session


class AuthService:
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
            user.password = get_password_hash(user_signup.password) # if user already singup with external, then just change the password.
            auth_provider.user_id = user.id
            auth_provider.provider_user_id = str(user.id)
            await self.add_user_auth_provider(session=session, user=user, auth_provider=auth_provider)
            if not user.email_verified:
                await self.send_signup_conformation_mail(email=user.email)
            await session.commit()

        return f"user created successfully with user_id: {user.id}"

    async def external_signup(self, user_signup: UserSignupExternal):
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
        existing_provider = [p.provider_name for p in user.auth_providers]
        if auth_provider.provider_name in existing_provider:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
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
        user = await self.get_login_user(email=user_login.email, auth_provider=AuthProviderEnum.INTERNAL)
        if not verify_password(password=user_login.password, hashed_password=user.password):
            raise HTTPException(
                detail="Invalid password",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        return await self.get_login_token(email=user.email)

    async def get_login_token(self, email: EmailStr):
        return LoginToken(
            access_token=create_token(data={"sub": email}),
            token_type="bearer",
            refresh_token=create_token(data={"sub": email},
                                       expires_delta=settings.jwt.refresh_token_expire_minutes)
        )

    async def external_login(self, user_login_external: UserLoginExternal):
        if user_login_external.provider == AuthProviderEnum.GOOGLE:
            google_token_info = self.external_auth_service.get_google_token_info(token=user_login_external.token)
            user = await self.get_login_user(email=google_token_info.email,
                                             auth_provider=AuthProviderEnum.GOOGLE)
        else:
            raise HTTPException(
                detail="Invalid auth provider.",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return await self.get_login_token(email=user.email)

    async def get_login_user(self, email: EmailStr, auth_provider: AuthProviderEnum):
        async with async_session() as session:
            stmt = select(orm.User).join(orm.AuthProvider, orm.User.id == orm.AuthProvider.user_id).where(
                orm.User.email == email,
                orm.AuthProvider.provider_name == auth_provider).limit(1)
            user = await session.execute(stmt)
            user = user.scalar()
            if not user or not user.is_active:
                raise HTTPException(
                    detail="Email not found. Please signup.",
                    status_code=status.HTTP_401_UNAUTHORIZED
                )

        return user

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

    async def conform_token(self, token: str):
        security_scopes = SecurityScopes()
        user = await get_valid_user(security_scopes=security_scopes,
                                    token=token)

        if user.email_verified:
            return "Already user verified"

        async with async_session() as session:
            stmt = update(orm.User).where(orm.User.email == user.email).values(email_verified=True)
            await session.execute(stmt)
            await session.commit()

        return "Successfully user verified."
