from fastapi import APIRouter
from loguru import logger


router = APIRouter(
    tags=["User tasks"],
)


@router.get("/tasks")
def get_tasks():
    return {"tasks": [1, 2, 3]}
