import datetime
import uuid
from typing import List

from sqlalchemy import Integer, String, ForeignKey, DateTime, func, UUID
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.database_engine import Base
from app.db.permission_mixin import PermissionMixin


class ContentType(Base):
    __tablename__ = 'content_types'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)


class Permission(Base, PermissionMixin):
    __tablename__ = 'permissions'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    content_type_id: Mapped[int] = mapped_column(Integer, ForeignKey('content_types.id'), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)

    roles: Mapped[List["Role"]] = relationship("Role", secondary='role_permission_association', back_populates="permissions")

    users: Mapped[List["User"]] = relationship("User", secondary='user_permission_association', back_populates="permissions")


class Role(Base, PermissionMixin):
    __tablename__ = 'roles'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)

    permissions: Mapped[List[Permission]] = relationship("Permission", secondary='role_permission_association',
                                                        back_populates="roles")
    users: Mapped[List["User"]] = relationship('User', secondary='user_role_association',
                                               back_populates="roles")


class UserRoleAssociation(Base):
    __tablename__ = 'user_role_association'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'),
                                               primary_key=True)
    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)


class UserPermissionAssociation(Base):
    __tablename__ = 'user_permission_association'

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'),
                                               primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)


class RolePermissionAssociation(Base):
    __tablename__ = 'role_permission_association'

    role_id: Mapped[int] = mapped_column(Integer, ForeignKey('roles.id', ondelete='CASCADE'), primary_key=True)
    permission_id: Mapped[int] = mapped_column(Integer, ForeignKey('permissions.id'), primary_key=True)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)
