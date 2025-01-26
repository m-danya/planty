from datetime import date

from dateutil.relativedelta import relativedelta

from planty.application.schemas import TasksByDate, TasksByDates
from planty.domain.task import Task
from planty.utils import get_today


def get_tasks_by_dates(
    tasks: list[Task],
    not_before: date,
    not_after: date,
) -> TasksByDates:
    tasks_by_dates = []
    # Do not show tasks before today
    # TODO: show all overdue tasks separately
    current_date = max(not_before, get_today())
    while current_date <= not_after:
        tasks_by_dates.append(TasksByDate(date=current_date, tasks=[]))
        current_date += relativedelta(days=1)

    for task in tasks:
        for date_tasks_item in tasks_by_dates:
            if date_tasks_item.date == task.due_to:
                date_tasks_item.tasks.append(task)
                break
    return tasks_by_dates
