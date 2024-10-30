from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from planty.application.router import router as tasks_router
from planty.application.auth import (
    fastapi_users_obj,
    cookie_auth_backend,
)
from planty.application.schemas import UserCreate, UserRead

app = FastAPI(
    title="Planty",
    swagger_ui_parameters={"persistAuthorization": True},
)

app.include_router(tasks_router)

app.include_router(
    fastapi_users_obj.get_auth_router(cookie_auth_backend),
    prefix="/auth/db",
    tags=["auth"],
)

app.include_router(
    fastapi_users_obj.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
