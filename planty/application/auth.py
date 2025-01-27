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

# Cookie/token lifetime is 10 years. This is intentional to avoid relogin
# torture when the token expires. Token can be invalidated in case of
# passord/cookie leakage, cause it's stored in the db.
#
# (TODO: consider using refresh tokens when they will be supported by
# fastapi-users: https://github.com/fastapi-users/fastapi-users/discussions/350
# and set lifetime to a shorter period without requiring user to relogin)
TOKEN_LIFETIME = 60 * 60 * 24 * 365 * 10


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
    return DatabaseStrategy(access_token_db, lifetime_seconds=TOKEN_LIFETIME)


cookie_transport = CookieTransport(cookie_max_age=TOKEN_LIFETIME)


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
admin_user_dependency = fastapi_users_obj.current_user(superuser=True)


def current_user(
    user: UserModel = Depends(current_user_dependency),
) -> User:
    return user.to_entity()


def admin_user(
    user: UserModel = Depends(admin_user_dependency),
) -> User:
    return user.to_entity()
