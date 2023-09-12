from enum import Enum


class UserRoleEnum(str, Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'


class ScopeEnum(str, Enum):
    USERS_GET = 'users_get'
    USERS_GET_ALL = 'users_get_all'
    USERS_UPDATE = 'users_update'
