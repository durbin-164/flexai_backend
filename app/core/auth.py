from typing import Annotated

from fastapi import Depends, HTTPException, Security
from fastapi.security import SecurityScopes
from jose import jwt, JWTError
from pydantic import ValidationError
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from starlette import status

from app.authentication.constant.auth_enum import ScopeEnum
from app.authentication.model import user
from app.core.config import settings
from app.core.security import oauth2_scheme
from app.db import orm
from app.db.database_engine import async_session


async def get_valid_user(security_scopes: SecurityScopes, token: str) -> orm.User:
    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, settings.jwt.secret_key, algorithms=[settings.jwt.algorithm])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception

        # token_scopes = payload.get("scopes", [])
        # token_data = TokenData(scopes=token_scopes, username=username)
    except (JWTError, ValidationError):
        raise credentials_exception

    async with async_session() as session:
        stmt = select(orm.User).filter(orm.User.email == username).options(
            joinedload(orm.User.permissions),
            joinedload(orm.User.roles).options(joinedload(orm.Role.permissions)),
            # joinedload(orm.Role.permissions)
        ).limit(1)
        user = await session.execute(stmt)
        user: orm.User = user.scalar()

    if user is None:
        raise credentials_exception

    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    if user.is_super_user:
        return user

    user_permissions = set()
    permission_names = set(map(lambda permission: permission.name, user.permissions))
    user_permissions.update(permission_names)

    for role in user.roles:
        permission_names = set(map(lambda permission: permission.name, role.permissions))
        user_permissions.update(permission_names)

    for scope in security_scopes.scopes:
        if scope not in user_permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    return user


async def get_current_user(
        security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    return await get_valid_user(security_scopes=security_scopes,
                                token=token)


async def get_current_active_user(
        current_user: Annotated[user.User, Security(get_current_user, scopes=[ScopeEnum.USERS_GET])]
):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
