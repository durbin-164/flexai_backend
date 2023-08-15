"""insert_initial_permission_data

Revision ID: b544f4196914
Revises: edacaaaf1c7e
Create Date: 2023-08-16 01:42:47.715510

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session

from app.db.orm import User
from app.db.permission import Group, Role, Permission

# revision identifiers, used by Alembic.
revision: str = 'b544f4196914'
down_revision: Union[str, None] = 'edacaaaf1c7e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    session = Session(bind=op.get_bind())

    User.create_permissions(session)
    Group.create_permissions(session)
    Role.create_permissions(session)
    Permission.create_permissions(session)


def downgrade() -> None:
    session = Session(bind=op.get_bind())

    User.delete_permissions(session)
    Group.delete_permissions(session)
    Role.delete_permissions(session)
    Permission.delete_permissions(session)
