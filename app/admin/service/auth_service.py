from typing import Annotated

from fastapi import HTTPException, Depends, Security
from fastapi.security import SecurityScopes

from app.authentication.constant.auth_enum import ScopeEnum
from app.core.security import oauth2_scheme
from app.db import orm

# COOKIE_NAME = 'Authorization'
#
#
# class OAuth2PasswordBearerWithCookie(OAuth2):
#     def __init__(
#             self,
#             tokenUrl: str,
#             scheme_name: Optional[str] = None,
#             scopes: Optional[Dict[str, str]] = None,
#             description: Optional[str] = None,
#             auto_error: bool = True,
#     ):
#         if not scopes:
#             scopes = {}
#         flows = OAuthFlowsModel(
#             password=cast(Any, {"tokenUrl": tokenUrl, "scopes": scopes})
#         )
#         super().__init__(
#             flows=flows,
#             scheme_name=scheme_name,
#             description=description,
#             auto_error=auto_error,
#         )
#
#     async def __call__(self, request: Request) -> Optional[str]:
#         # authorization = request.headers.get("Authorization")
#         authorization: str = request.cookies.get(COOKIE_NAME)
#         scheme, param = get_authorization_scheme_param(authorization)
#         if not authorization or scheme.lower() != "bearer":
#             if self.auto_error:
#                 raise HTTPException(
#                     status_code=HTTP_401_UNAUTHORIZED,
#                     detail="Not authenticated",
#                     headers={"WWW-Authenticate": "Bearer"},
#                 )
#             else:
#                 return None
#         return param
#
#
# oauth2_cookie_scheme = OAuth2PasswordBearerWithCookie(tokenUrl="/admin")


async def get_current_cookie_user(
        security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    from app.core.auth import get_valid_user
    return await get_valid_user(security_scopes=security_scopes,
                                token=token)


async def get_active_stuff_user(
        current_user: Annotated[orm.User, Security(get_current_cookie_user, scopes=[ScopeEnum.USERS_GET])]
):
    if current_user.is_staff or current_user.is_super_user:
        return current_user
    raise HTTPException(status_code=400, detail="Invalid user")
