from enum import Enum


class UserRoleEnum(str, Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'


class ScopeEnum(str, Enum):
    USERS_GET = 'users_get'
