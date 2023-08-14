from __future__ import annotations

from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.api import model
from app.db import orm
from app.db.repository.irepository import IRepository
from app.db.repository.sqlalchemy_repository import SQLAlchemyRepository


class IUnitOfWork(ABC):
    user_repository: IRepository[orm.User, model.user.User]

    async def __aenter__(self) -> IUnitOfWork:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_type is not None:  # An exception occurred within the 'with' block
            await self.rollback()

    @abstractmethod
    async def commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError


class UnitOfWork(IUnitOfWork):
    def __init__(self, session_factory: AsyncSession):
        self.session_factory = session_factory

    async def __aenter__(self):
        self.async_session = self.session_factory()  # type: AsyncSession
        self.user_repository = SQLAlchemyRepository[orm.User, model.user.User](self.async_session, orm.User,
                                                                               model.user.User)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.async_session.close()

    async def commit(self):
        await self.async_session.commit()

    async def rollback(self):
        await self.async_session.rollback()
