from __future__ import annotations

import datetime
from typing import List

from sqlalchemy import String, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.orm import relationship

from app.db.database_engine import Base
from app.db.permission import Group, Role, Permission
from app.db.permission_mixin import PermissionMixin, FullPermissionMixin


class User(Base, PermissionMixin):
    __tablename__ = 'users'
    mixins = [FullPermissionMixin]

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    first_name: Mapped[str] = mapped_column(String(50))
    last_name: Mapped[str] = mapped_column(String(50))
    is_active: Mapped[bool]
    created_at: Mapped[datetime.datetime] = mapped_column(DateTime, default=func.now())

    groups: Mapped[List[Group]] = relationship("Group", secondary='user_group_association', back_populates="users")
    roles: Mapped[List[Role]] = relationship("Role", secondary='user_role_association', back_populates="users")
    permissions: Mapped[List[Permission]] = relationship("Permission", secondary='user_permission_association',
                                                         back_populates="users")
