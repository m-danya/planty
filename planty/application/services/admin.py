from uuid import UUID

from planty.application.schemas import StatsResponse
from planty.application.uow import IUnitOfWork


class AdminService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_stats(self) -> StatsResponse:
        return await self.uow.user_repo.get_all_users()

    async def verify_user(self, user_id: UUID) -> None:
        await self.uow.user_repo.verify_user(user_id)
