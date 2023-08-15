from __future__ import annotations

from typing import List

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.api.model.user import User
from app.db.database_engine import Base
from app.db.permission_mixin import PermissionMixin


class Group(Base, PermissionMixin):
    __tablename__ = 'groups'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List[User]] = relationship("User", secondary='user_group_association', back_populates="groups")
    roles: Mapped[List[Role]] = relationship("Role", secondary='group_role_association', back_populates="groups")
    permissions: Mapped[List[Permission]] = relationship("Permission", secondary='group_permission_association',
                                                         back_populates="groups")


class Role(Base, PermissionMixin):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List[User]] = relationship("User", secondary='user_role_association', back_populates="roles")
    groups: Mapped[List[Group]] = relationship("Group", secondary='group_role_association', back_populates="roles")
    permissions: Mapped[List[Permission]] = relationship("Permission", secondary='role_permission_association',
                                                         back_populates="roles")


class Permission(Base, PermissionMixin):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    users: Mapped[List[User]] = relationship("User", secondary='user_permission_association',
                                             back_populates="permissions")
    groups: Mapped[List[Group]] = relationship("Group", secondary='group_permission_association',
                                               back_populates="permissions")
    roles: Mapped[List[Role]] = relationship("Role", secondary='role_permission_association',
                                             back_populates="permissions")


class UserGroupAssociation(Base):
    __tablename__ = 'user_group_association'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id'), primary_key=True)


class GroupRoleAssociation(Base):
    __tablename__ = 'group_role_association'

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id'), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)


class UserRoleAssociation(Base):
    __tablename__ = 'user_role_association'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)


class UserPermissionAssociation(Base):
    __tablename__ = 'user_permission_association'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)


class GroupPermissionAssociation(Base):
    __tablename__ = 'group_permission_association'

    group_id: Mapped[int] = mapped_column(Integer, ForeignKey('groups.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)


class RolePermissionAssociation(Base):
    __tablename__ = 'role_permission_association'

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)
