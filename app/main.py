from contextlib import asynccontextmanager

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse

from app.admin.router import admin_router
from app.api import api_router


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(api_router)
app.include_router(admin_router)


@app.exception_handler(Exception)
async def generic_exception_handler(request, exc):
    error_response = {"message": "Something went wrong. Please try again later."}
    return JSONResponse(status_code=500, content=error_response)
