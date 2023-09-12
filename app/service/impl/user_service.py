from sqlalchemy import select, update

from app.api.model.user import UserUpdate, User, UserChangePaasword
from app.db import orm
from app.db.database_engine import async_session
from app.service.iuser_service import IUserService


class UserService(IUserService):
    async def get_all(self):
        async with async_session() as session:
            stmt = select(orm.User)
            users = await session.execute(stmt)
            users = users.scalars()

        return users

    async def update(self, user: User, user_update: UserUpdate):
        user_update_dict = user_update.model_dump(exclude_none=True)
        if not user_update_dict:
            return "Nothing need to change."

        async with async_session() as session:
            stmt = update(orm.User).where(orm.User.username == user.username).values(user_update_dict)
            await session.execute(stmt)
            await session.commit()

        return "Successfully updated."
