from __future__ import annotations

from sqlalchemy import event, select, delete


class CreatePermissionMixin:
    permissions = ["create"]


class UpdatePermissionMixin:
    permissions = ["update"]


class GetPermissionMixin:
    permissions = ["get", "get_all"]


class DeletePermissionMixin:
    permissions = ["delete"]


class FullPermissionMixin:
    permissions = sum(
        [CreatePermissionMixin.permissions,
         UpdatePermissionMixin.permissions,
         GetPermissionMixin.permissions,
         DeletePermissionMixin.permissions],

        []
    )


# Generic mixin for permission-based models
class PermissionMixin:
    mixins = [FullPermissionMixin]

    @classmethod
    def create_permissions(cls, session):
        from app.db.permission import Permission
        if hasattr(cls, "mixins"):
            permissions = []
            for mixin in cls.mixins:
                permissions.extend(mixin.permissions)
            permissions = list(set(permissions))
            for permission in permissions:
                permission_name = f"{cls.__tablename__}_{permission}"
                stmt = select(Permission).filter_by(name=permission_name).limit(1)
                permission_obj = session.execute(stmt)
                permission_obj = permission_obj.first()

                if not permission_obj:
                    permission_obj = Permission(name=permission_name)
                    session.add(permission_obj)
            session.commit()

    @classmethod
    def delete_permissions(cls, session):
        from app.db.permission import Permission
        if issubclass(cls, PermissionMixin):
            for mixin in cls.mixins:
                permissions = mixin.permissions
                for permission in permissions:
                    permission_name = f"{cls.__tablename__}_{permission}"
                    stmt = delete(Permission).where(Permission.name == permission_name)
                    session.execute(stmt)

                session.commit()

    @classmethod
    def add_events(cls):
        event.listen(cls.__table__, 'after_create', cls.create_permissions)
        event.listen(cls.__table__, 'after_drop', cls.delete_permissions)
