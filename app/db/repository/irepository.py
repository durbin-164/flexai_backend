from abc import ABC, abstractmethod
from inspect import Attribute
from typing import TypeVar, Generic, Any, List

from pydantic import BaseModel
from sqlalchemy import ClauseElement, Select

from app.db import orm

T = TypeVar("T", bound=orm.Base)
P = TypeVar("P", bound=BaseModel)


class IRepository(ABC, Generic[T, P]):
    @abstractmethod
    async def add(self, data_model: P) -> P:
        raise NotImplementedError()

    @abstractmethod
    async def bulk_add(self, values: list[P]):
        raise NotImplementedError()

    @abstractmethod
    async def get(self, id: int) -> P:
        raise NotImplementedError()

    @abstractmethod
    async def get_by_expression(self, **kwargs: Any) -> P:
        raise NotImplementedError()

    @abstractmethod
    async def get_all(self) -> List[P]:
        raise NotImplementedError()

    @abstractmethod
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
        raise NotImplementedError()

    @abstractmethod
    async def update(self, id: int, data_model: P) -> P:
        raise NotImplementedError()

    @abstractmethod
    async def delete(self, id: int) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def delete_by_expression(self, **kwargs: Any) -> None:
        raise NotImplementedError()

    @abstractmethod
    async def delete_all(self) -> None:
        raise NotImplementedError()