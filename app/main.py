from contextlib import asynccontextmanager
from http.client import HTTPException

from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.api import model
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


@app.post("/user")
async def add_user(user: model.user.User) -> model.user.User:
    async with uow:
        await uow.user_repository.add(user)
        await uow.commit()

    return user


@app.post("/users")
async def add_user(start: int, end: int) -> str:
    users = [
        model.user.User(
            user_name=f"user_{i}",
            password=f"password_{i}",
            first_name=f"first name {i}",
            last_name=f"last name {i}"
        )
        for i in range(start, end)
    ]

    async with uow:
        print("*"*100)
        # connection_id = uow.async_session._connection._lock._holder.get_connection().connection_id
        session_id = id(uow.async_session)
        # session_id = uow.async_session.hash_key
        # print(f"Connection ID: {connection_id}")
        print(f"Session ID: {session_id}")
        print("*"*100)
        await uow.user_repository.bulk_add(users)
        await uow.commit()

    return "succssfull"
