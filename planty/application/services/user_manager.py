import uuid
from typing import Optional
from loguru import logger
from fastapi import Request
from planty.config import settings
from fastapi_users import BaseUserManager, UUIDIDMixin

from planty.infrastructure.models import UserModel


class UserManager(UUIDIDMixin, BaseUserManager[UserModel, uuid.UUID]):
    reset_password_token_secret = settings.auth_secret
    verification_token_secret = settings.auth_secret

    async def on_after_register(
        self, user: UserModel, request: Optional[Request] = None
    ) -> None:
        logger.info(f"User {user.id} has registered.")

    async def on_after_forgot_password(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ) -> None:
        logger.info(f"User {user.id} has forgot their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: UserModel, token: str, request: Optional[Request] = None
    ) -> None:
        logger.info(
            f"Verification requested for user {user.id}. Verification token: {token}"
        )
