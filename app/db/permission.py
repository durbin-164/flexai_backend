from typing import List

from sqlalchemy import Integer, String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.database_engine import Base
from app.db.permission_mixin import PermissionMixin


class Permission(Base, PermissionMixin):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)


class Role(Base, PermissionMixin):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)

    permissions: Mapped[List[Permission]] = relationship("Permission", secondary='role_permission_association')


class UserRoleAssociation(Base):
    __tablename__ = 'user_role_association'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)


class UserPermissionAssociation(Base):
    __tablename__ = 'user_permission_association'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)


class RolePermissionAssociation(Base):
    __tablename__ = 'role_permission_association'

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)
