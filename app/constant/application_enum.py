from enum import Enum


class UserRoleEnum(str, Enum):
    USER = 'USER'
    ADMIN = 'ADMIN'


class ScopeEnum(str, Enum):
    USERS_GET = 'users_get'
    USERS_GET_ALL = 'users_get_all'
    USERS_UPDATE = 'users_update'
    USERS_DELETE = 'users_delete'
    USERS_CREATE = 'users_create'
    ROLES_CREATE = 'roles_create'
    ROLES_GET = 'roles_get'
    ROLES_GET_ALL = 'roles_get_all'
    ROLES_UPDATE = 'roles_update'
    ROLES_DELETE = 'roles_delete'
    PERMISSIONS_CREATE = 'permissions_create'
    PERMISSIONS_GET = 'permissions_get'
    PERMISSIONS_GET_ALL = 'permissions_get_all'
    PERMISSIONS_UPDATE = 'permissions_update'
    PERMISSIONS_DELETE = 'permissions_delete'
