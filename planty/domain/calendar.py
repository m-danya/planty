from datetime import date

from dateutil.relativedelta import relativedelta

from planty.application.schemas import TasksByDate, TasksByDates
from planty.domain.task import Task


def get_tasks_by_dates(
    tasks: list[Task],
    not_before: date,
    not_after: date,
) -> TasksByDates:
    delta = not_after - not_before
    tasks_by_dates = [
        TasksByDate(date=not_before + relativedelta(days=i), tasks=[])
        for i in range(delta.days + 1)
    ]
    for task in tasks:
        for date_tasks_item in tasks_by_dates:
            if date_tasks_item.date == task.due_to:
                date_tasks_item.tasks.append(task)
                break
    return tasks_by_dates
