from typing import Any, AsyncGenerator
from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
import uuid
from fastapi_users import FastAPIUsers
from planty.application.services.user_manager import UserManager
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi_users_db_sqlalchemy.access_token import (
    SQLAlchemyAccessTokenDatabase,
)
from fastapi_users.authentication.strategy.db import (
    AccessTokenDatabase,
    DatabaseStrategy,
)
from fastapi_users.authentication import (
    AuthenticationBackend,
)
from fastapi_users.authentication import CookieTransport


from planty.domain.task import User
from planty.infrastructure.database import get_async_session
from planty.infrastructure.models import AccessTokenModel, UserModel


async def get_user_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyUserDatabase[UserModel, uuid.UUID], None]:
    yield SQLAlchemyUserDatabase(session, UserModel)


async def get_access_token_db(
    session: AsyncSession = Depends(get_async_session),
) -> AsyncGenerator[SQLAlchemyAccessTokenDatabase[AccessTokenModel], None]:
    yield SQLAlchemyAccessTokenDatabase(session, AccessTokenModel)


def get_database_strategy(
    access_token_db: AccessTokenDatabase[AccessTokenModel] = Depends(
        get_access_token_db
    ),
) -> DatabaseStrategy[Any, Any, Any]:
    return DatabaseStrategy(access_token_db, lifetime_seconds=3600)


cookie_transport = CookieTransport(cookie_max_age=3600)


cookie_auth_backend = AuthenticationBackend(
    name="db_cookie",
    transport=cookie_transport,
    get_strategy=get_database_strategy,
)


async def get_user_manager(
    user_db: SQLAlchemyUserDatabase[UserModel, uuid.UUID] = Depends(get_user_db),
) -> AsyncGenerator[UserManager, None]:
    yield UserManager(user_db)


fastapi_users_obj = FastAPIUsers[UserModel, uuid.UUID](
    get_user_manager,
    [cookie_auth_backend],
)


current_user_dependency = fastapi_users_obj.current_user()


def current_user(
    user: UserModel = Depends(current_user_dependency),
) -> User:
    return user.to_entity()
