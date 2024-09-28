from datetime import date


import pytest

from planty.domain.calendar import recurrence_rule
from planty.domain.types import RecurrencePeriodType


@pytest.mark.parametrize(
    "start_day,k,period_type,not_after,result",
    [
        (
            date(2024, 8, 31),
            1,
            "months",
            date(2025, 1, 1),
            [
                date(2024, 8, 31),
                date(2024, 9, 30),
                date(2024, 10, 31),
                date(2024, 11, 30),
                date(2024, 12, 31),
            ],
        ),
        (
            date(2024, 8, 31),
            1,
            "days",
            date(2024, 8, 31),
            [date(2024, 8, 31)],
        ),
        (
            date(2024, 8, 31),
            1,
            "days",
            date(2024, 9, 2),
            [date(2024, 8, 31), date(2024, 9, 1), date(2024, 9, 2)],
        ),
        (
            date(2024, 8, 31),
            3,
            "months",
            date(2025, 9, 2),
            [
                date(2024, 8, 31),
                date(2024, 11, 30),
                date(2025, 2, 28),
                date(2025, 5, 31),
                date(2025, 8, 31),
            ],
        ),
    ],
)
def test_recurrence_rule(
    start_day: date,
    k: int,
    period_type: RecurrencePeriodType,
    not_after: date,
    result: list[date],
) -> None:
    dates = list(
        recurrence_rule(
            start_day=start_day,
            k=k,
            period_type=period_type,
            not_after=not_after,
        )
    )
    assert dates == result
