import datetime
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.database_engine import Base
from app.db.permission_mixin import PermissionMixin

class ContentType(Base):
    __tablename__ = 'content_types'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class Permission(Base, PermissionMixin):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    content_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('content_types.id'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class Role(Base, PermissionMixin):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    permissions: Mapped[List[Permission]] = relationship("Permission", secondary='role_permission_association')


class UserRoleAssociation(Base):
    __tablename__ = 'user_role_association'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class UserPermissionAssociation(Base):
    __tablename__ = 'user_permission_association'

    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())


class RolePermissionAssociation(Base):
    __tablename__ = 'role_permission_association'

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())
