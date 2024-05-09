from datetime import date, datetime, timezone
import uuid


def get_datetime_now() -> datetime:
    # TODO: think about timezones
    return datetime.now(timezone.utc).replace(tzinfo=None)


def get_today() -> date:
    return datetime.now(timezone.utc).date()


def generate_uuid() -> uuid.UUID:
    return uuid.uuid4()
