from contextlib import asynccontextmanager
from http.client import HTTPException

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from sqlalchemy import select, func
from sqlalchemy.dialects.postgresql import insert

from app.api import model
from app.db import orm
from app.db.database_engine import async_session
from app.db.unit_of_work import UnitOfWork


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start_mapping()
    yield


app = FastAPI(lifespan=lifespan)


@app.exception_handler(Exception)
@app.exception_handler(ConnectionRefusedError)
@app.exception_handler(HTTPException)
async def generic_exception_handler(request, exc):
    error_response = {"message": "Something went wrong. Please try again later."}
    return JSONResponse(status_code=500, content=str(exc))


uow = UnitOfWork(async_session)
PSQL_QUERY_ALLOWED_MAX_ARGS = 32767


@app.post("/user")
async def add_user(user: model.user.User) -> model.user.User:
    async with uow:
        await uow.user_repository.add(user)
        await uow.commit()

    return user


@app.post("/users")
async def add_user(start: int, end: int) -> str:
    users = [
        {
            "user_name": f"user_{i}",
            "password": f"password_{i}",
            "first_name": f"first name {i}",
            "last_name": f"last name {i}",
        }
        for i in range(start, end)
    ]

    async with async_session() as session:
        print("*" * 100)
        # connection_id = uow.async_session._connection._lock._holder.get_connection().connection_id
        session_id = id(session)
        # session_id = uow.async_session.hash_key
        # print(f"Connection ID: {connection_id}")
        print(f"Session ID: {session_id}")
        print("*" * 100)

        for value in get_chanks(users):
            stmt = insert(orm.User).values(value)
            stmt = stmt.on_conflict_do_nothing()

            await session.execute(stmt)
            await session.flush()
        await session.commit()

    return "succssfull"


# async with uow:
#     print("*" * 100)
#     # connection_id = uow.async_session._connection._lock._holder.get_connection().connection_id
#     session_id = id(uow.async_session)
#     # session_id = uow.async_session.hash_key
#     # print(f"Connection ID: {connection_id}")
#     print(f"Session ID: {session_id}")
#     print("*" * 100)
#     await uow.user_repository.bulk_add(users)
#     await uow.commit()
#


def get_chanks(values):
    batch_size = PSQL_QUERY_ALLOWED_MAX_ARGS // len(values[0])
    start = 0
    end = len(values)

    while start < end:
        yield values[start:start + batch_size]
        start += batch_size


@app.get("/users")
async def get_user() -> str:
    async with async_session() as session:
        print("*" * 100)
        session_id = id(session)
        print(f"Session ID: {session_id}")
        print("*" * 100)

        stmt = func.count(orm.User.user_name)
        result = await session.execute(stmt)
        users = result.scalar()

    return f"users: {users}"
