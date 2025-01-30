import asyncio
import contextlib

import typer

from planty.application.auth import get_user_db, get_user_manager
from planty.application.schemas import UserCreate
from planty.infrastructure.database import raw_async_session_maker

app = typer.Typer()


get_user_db_context = contextlib.asynccontextmanager(get_user_db)
get_user_manager_context = contextlib.asynccontextmanager(get_user_manager)


async def create_admin_user(email: str, password: str) -> None:
    async with raw_async_session_maker() as session:
        async with get_user_db_context(session) as user_db:
            async with get_user_manager_context(user_db) as user_manager:
                user = await user_manager.create(
                    UserCreate(
                        email=email,
                        password=password,
                        is_superuser=True,
                        is_active=True,
                        is_verified=True,
                    )
                )
            print(f"User {user} successfully created")


@app.command()
def create_admin(
    email: str = typer.Option(..., prompt=True),
    password: str = typer.Option(
        ...,
        prompt=True,
        hide_input=True,
        confirmation_prompt=True,
    ),
) -> None:
    asyncio.run(create_admin_user(email, password))


if __name__ == "__main__":
    app()
