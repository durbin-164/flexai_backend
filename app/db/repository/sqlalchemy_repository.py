from inspect import Attribute
from typing import Generic, Type, Any, List

from sqlalchemy import select, ClauseElement, Select, and_, delete
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

# from app.api import model
# from app.db import orm
from app.db.repository.irepository import IRepository, T, P

PSQL_QUERY_ALLOWED_MAX_ARGS = 32767


class SQLAlchemyRepository(IRepository[T, P], Generic[T, P]):
    def __init__(self, async_session: AsyncSession, entity_class: Type[T], data_model: Type[P]) -> None:
        self.async_session = async_session
        self.entity_class = entity_class
        self.data_model = data_model

    async def add(self, data_model: P) -> P:
        entity = self.entity_class(**data_model.model_dump())
        self.async_session.add(entity)
        await self.async_session.flush()
        await self.async_session.refresh(entity)
        return self.data_model.model_validate(entity)

    async def bulk_add(self, values: list[P]):
        entities = [v.model_dump() for v in values]
        if not entities:
            return
        for value in self.get_chanks(entities):
            stmt = insert(self.entity_class).values(value)
            stmt = stmt.on_conflict_do_nothing()

            await self.async_session.execute(stmt)
            await self.async_session.flush()

    def get_chanks(self, values):
        batch_size = PSQL_QUERY_ALLOWED_MAX_ARGS // len(values[0])
        start = 0
        end = len(values)

        while start < end:
            yield values[start:start + batch_size]
            start += batch_size

    async def get(self, id: int) -> P:
        data = await self.async_session.get(self.entity_class, id)
        return self.data_model.model_validate(data)

    async def get_by_expression(self, **kwargs: Any) -> P:
        stmt = select(self.entity_class).filter_by(**kwargs)
        data = await self.async_session.execute(stmt)
        data = data.scalar_one()
        return self.data_model.model_validate(data)

    async def get_all_by_expression(
            self,
            distinct: bool = False,
            selected_columns: List[Attribute] = None,
            filters: List[ClauseElement] = None,
            order_by: List[ClauseElement] = None,
            limit: int = None,
            offset: int = None,
            relationship_loads: List[str] = None,
            custom_query: Select = None,
            **kwargs: Any
    ) -> List[P]:
        query = custom_query if custom_query else select(self.entity_class)

        if selected_columns:
            selected_columns_mapped = self.map_selected_columns(
                selected_columns, self.entity_class, self.data_model
            )
            query = query.with_only_columns(selected_columns_mapped)

        if filters:
            query = query.where(and_(*filters))

        if distinct:
            query = query.distinct()

        if order_by:
            query = query.order_by(*order_by)

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        if relationship_loads:
            for load in relationship_loads:
                query = query.options(joinedload(load))

        data = await self.async_session.execute(query)
        data = data.scalars().all()
        return [self.data_model.model_validate(item) for item in data]

    def map_selected_columns(self, selected_columns, entity_class, data_model):
        attribute_mapping = {
            attr: getattr(entity_class, attr_name)
            for attr, attr_name in data_model.__annotations__.items()
            if hasattr(entity_class, attr_name)
        }

        return [attribute_mapping[column] for column in selected_columns]

    async def update(self, id: int, data_model: P) -> P:
        entity = await self.async_session.get(self.entity_class, id)
        for field, value in data_model.model_dump().items():
            setattr(entity, field, value)
        await self.async_session.flush()
        await self.async_session.refresh(entity)
        return self.data_model(**entity.dict())

    async def delete(self, id: int) -> None:
        entity = await self.async_session.get(self.entity_class, id)
        await self.async_session.delete(entity)
        await self.async_session.flush()

    async def delete_by_expression(self, **kwargs: Any) -> None:
        stmt = delete(self.entity_class).where_by(**kwargs)
        await self.async_session.execute(stmt)
        await self.async_session.flush()

    async def get_all(self) -> List[P]:
        query = select(self.entity_class)
        data = await self.async_session.execute(query)
        return [self.data_model(**item.dict()) for item in data.scalars()]

    async def delete_all(self) -> None:
        query = delete(self.entity_class)
        await self.async_session.execute(query)
        await self.async_session.flush()

# class UserRepository(SQLAlchemyRepository[orm.User, model.user.User]):
#     pass
