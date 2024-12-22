from collections import defaultdict
from datetime import date

from typing import Generator
import itertools
from dateutil.relativedelta import relativedelta

from planty.domain.task import Task
from planty.domain.types import RecurrencePeriodType


def recurrence_rule(
    start_day: date,
    period: int,
    period_type: RecurrencePeriodType,
    not_before: date,
    not_after: date,
) -> Generator[date, None, None]:
    for i in itertools.count():
        d = start_day + relativedelta(**{period_type: period * i})  # type: ignore
        if d < not_before:
            continue
        if d > not_after:
            return
        yield d


def get_task_recurrences(task: Task, not_before: date, not_after: date) -> list[date]:
    if task.due_to is None or task.due_to > not_after:
        return []
    if task.recurrence is None:
        if task.due_to >= not_before:
            return [task.due_to]
        else:
            return []
    return list(
        recurrence_rule(
            start_day=task.due_to,
            period=task.recurrence.period,
            period_type=task.recurrence.type,
            not_before=not_before,
            not_after=not_after,
        )
    )


def multiply_tasks_with_recurrences(
    prefiltered_tasks: list[Task],
    not_before: date,
    not_after: date,
):
    delta = not_after - not_before
    # TODO: rewrite with pydantic model, add typings, add tests
    tasks_by_date = [
        {"date": not_before + relativedelta(days=i), "tasks": []}
        for i in range(delta.days + 1)
    ]
    for task in prefiltered_tasks:
        for date_ in get_task_recurrences(task, not_before, not_after):
            for date_tasks_item in tasks_by_date:
                if date_tasks_item["date"] == date_:
                    date_tasks_item["tasks"].append(task)
                    break
    return tasks_by_date
