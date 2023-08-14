from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

# from app.api import model


# map_registry = registry().map_imperatively


class Base(AsyncAttrs, DeclarativeBase):
    pass


class User(Base):
    __tablename__ = "users"
    user_name: Mapped[str] = mapped_column(primary_key=True)
    password: Mapped[str]
    first_name: Mapped[str]
    last_name: Mapped[str]


# map_registry = Base.registry.map_imperatively


# def start_mapping():
#     map_registry(model.user.User, User.__table__)
