from planty.application.schemas import StatsResponse
from planty.application.uow import IUnitOfWork


class StatsService:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def get_stats(self) -> StatsResponse:
        return await self.uow.user_repo.get_all_users()
