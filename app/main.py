from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.responses import JSONResponse

from app.api import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # start_mapping()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(api_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    error_response = {"message": "Something went wrong. Please try again later."}
    return JSONResponse(status_code=500, content=str(exc))
