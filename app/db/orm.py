from __future__ import annotations

import datetime
import uuid
from typing import List

from sqlalchemy import String, DateTime, func, UUID, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.database_engine import Base
from app.db.permission import Role, Permission
from app.db.permission import UserPermissionAssociation, RolePermissionAssociation, UserRoleAssociation, \
    ContentType  # dont remove this line
from app.db.permission_mixin import PermissionMixin, FullPermissionMixin


class User(Base, PermissionMixin):
    __tablename__ = 'users'
    mixins = [FullPermissionMixin]

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=True)
    phone: Mapped[str] = mapped_column(String(15), nullable=True)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    picture: Mapped[str] = mapped_column(String(512), nullable=True)
    email_verified: Mapped[bool]
    phone_verified: Mapped[bool] = mapped_column(nullable=True)
    is_active: Mapped[bool]
    is_super_user: Mapped[bool]
    is_staff: Mapped[bool]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)

    roles: Mapped[List[Role]] = relationship("Role", secondary='user_role_association',
                                             back_populates="users")
    permissions: Mapped[List[Permission]] = relationship("Permission", secondary='user_permission_association',
                                                         back_populates="users")
    auth_providers: Mapped[List[AuthProvider]] = relationship('AuthProvider', back_populates='user')


class AuthProvider(Base):
    __tablename__ = 'auth_providers'

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id", ondelete='CASCADE'), nullable=False)
    provider_name: Mapped[str] = mapped_column(String(64))
    provider_user_id: Mapped[str] = mapped_column(String(255), nullable=False)
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now(), nullable=True)

    user: Mapped[User] = relationship('User', back_populates='auth_providers')

    # Add a unique constraint for provider_user_id, ensuring it's unique or null per user_id
    __table_args__ = (
        UniqueConstraint('user_id', 'provider_user_id', name='unique_user_id_provider_user_id'),
    )
