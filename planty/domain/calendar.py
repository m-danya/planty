from collections import defaultdict
from datetime import date

from typing import Generator
from pydantic import BaseModel
import itertools
from dateutil.relativedelta import relativedelta

from planty.domain.task import Task
from planty.domain.types import RecurrencePeriodType


class RecurrenceSpecification(BaseModel):
    pass


def recurrence_rule(
    start_day: date,
    k: int,
    period_type: RecurrencePeriodType,
    not_after: date,
) -> Generator[date, None, None]:
    for i in itertools.count():
        d = start_day + relativedelta(**{period_type: k * i})  # type: ignore
        if d > not_after:
            return
        yield d


# TODO: write tests
def get_task_recurrences(task: Task, not_after: date) -> list[date]:
    if task.due_to is None or task.due_to > not_after:
        return []
    if task.recurrence is None:
        return [task.due_to]
    return list(
        recurrence_rule(
            start_day=task.due_to,
            k=task.recurrence.period,
            period_type=task.recurrence.type,
            not_after=not_after,
        )
    )


def multiply_tasks_with_recurrences(
    prefiltered_tasks: list[Task], not_after: date
) -> dict[date, list[Task]]:
    dates = defaultdict(list)
    for task in prefiltered_tasks:
        for date_ in get_task_recurrences(task, not_after):
            dates[date_].append(task)
    return dates
