from __future__ import annotations

import csv
import io
import re
import zipfile
from dataclasses import dataclass
from datetime import date, datetime, timedelta
from pathlib import PurePath
from uuid import UUID

from dateutil.relativedelta import relativedelta

from planty.application.exceptions import InvalidTodoistBackupException
from planty.application.uow import IUnitOfWork
from planty.domain.task import RecurrenceInfo, Section, Task
from planty.utils import get_today

TODOIST_COLUMNS = {"TYPE", "CONTENT", "DESCRIPTION", "INDENT", "DATE"}
MAX_ARCHIVE_SIZE = 25 * 1024 * 1024
MAX_UNCOMPRESSED_SIZE = 100 * 1024 * 1024
MAX_CSV_FILES = 1_000

MONTHS = {
    "янв": 1,
    "января": 1,
    "фев": 2,
    "февр": 2,
    "февраля": 2,
    "мар": 3,
    "марта": 3,
    "апр": 4,
    "апреля": 4,
    "мая": 5,
    "май": 5,
    "июн": 6,
    "июня": 6,
    "июл": 7,
    "июля": 7,
    "авг": 8,
    "августа": 8,
    "сен": 9,
    "сентября": 9,
    "окт": 10,
    "октября": 10,
    "ноя": 11,
    "нояб": 11,
    "ноября": 11,
    "дек": 12,
    "декабря": 12,
}
WEEKDAYS = {"пн": 0, "вт": 1, "ср": 2, "чт": 3, "пт": 4, "сб": 5, "вс": 6}


@dataclass
class ImportedProject:
    title: str
    rows: list[dict[str, str]]


@dataclass
class ImportedData:
    sections: list[tuple[Section, int]]
    tasks: list[tuple[Task, int]]


@dataclass
class ImportResult:
    projects: int
    sections: int
    tasks: int


class TodoistImportService:
    def __init__(self, uow: IUnitOfWork):
        self._section_repo = uow.section_repo
        self._task_repo = uow.task_repo

    async def import_backup(
        self, user_id: UUID, archive: bytes, *, erase_existing: bool
    ) -> ImportResult:
        projects = parse_todoist_backup(archive)
        if erase_existing:
            await self._section_repo.remove_all_for_user(user_id)
            root = Section.create_root_section(user_id)
            await self._section_repo.add(root, index=0)
            top_level_offset = 0
        else:
            root = await self._section_repo.get_root(user_id)
            top_level_offset = await self._section_repo.count_subsections(root.id)

        imported = build_imported_data(
            user_id, root.id, projects, top_level_offset=top_level_offset
        )
        for section, index in imported.sections:
            await self._section_repo.add(section, index=index)
        for task, index in imported.tasks:
            await self._task_repo.add(task, index=index)

        if imported.sections and not root.has_subsections:
            root.has_subsections = True
            await self._section_repo.update(root)

        return ImportResult(
            projects=len(projects),
            sections=len(imported.sections),
            tasks=len(imported.tasks),
        )


def parse_todoist_backup(archive: bytes) -> list[ImportedProject]:
    if not archive or len(archive) > MAX_ARCHIVE_SIZE:
        raise InvalidTodoistBackupException()
    try:
        with zipfile.ZipFile(io.BytesIO(archive)) as zipped:
            csv_infos = [
                info
                for info in zipped.infolist()
                if not info.is_dir() and info.filename.lower().endswith(".csv")
            ]
            if not csv_infos or len(csv_infos) > MAX_CSV_FILES:
                raise InvalidTodoistBackupException()
            if (
                sum(info.file_size for info in zipped.infolist())
                > MAX_UNCOMPRESSED_SIZE
            ):
                raise InvalidTodoistBackupException()

            projects = []
            for info in csv_infos:
                title = _project_title(info.filename)
                text = zipped.read(info).decode("utf-8-sig")
                reader = csv.DictReader(io.StringIO(text))
                if reader.fieldnames is None or not TODOIST_COLUMNS.issubset(
                    reader.fieldnames
                ):
                    raise InvalidTodoistBackupException()
                projects.append(ImportedProject(title=title, rows=list(reader)))
            return projects
    except (zipfile.BadZipFile, KeyError, UnicodeDecodeError, csv.Error):
        raise InvalidTodoistBackupException() from None


def _project_title(filename: str) -> str:
    stem = PurePath(filename).stem
    title = re.sub(r"\s+\[[^\]]+\]$", "", stem).strip()
    if not title:
        raise InvalidTodoistBackupException()
    return title


def build_imported_data(
    user_id: UUID,
    root_id: UUID,
    projects: list[ImportedProject],
    *,
    top_level_offset: int = 0,
) -> ImportedData:
    sections: list[tuple[Section, int]] = []
    tasks: list[tuple[Task, int]] = []
    for project_index, project in enumerate(projects, start=top_level_offset):
        named_sections = [
            row for row in project.rows if row.get("TYPE", "").lower() == "section"
        ]
        unsectioned_tasks = _tasks_before_first_section(project.rows)
        needs_children = bool(named_sections)
        project_section = Section(
            user_id=user_id,
            title=project.title,
            parent_id=root_id,
            tasks=[],
            subsections=[],
            has_tasks=not needs_children and bool(unsectioned_tasks),
            has_subsections=needs_children,
        )
        sections.append((project_section, project_index))

        if not needs_children:
            tasks.extend(_build_tasks(user_id, project_section.id, unsectioned_tasks))
            continue

        child_index = 0
        if unsectioned_tasks:
            default_section = _leaf_section(
                user_id, project_section.id, "Без раздела", bool(unsectioned_tasks)
            )
            sections.append((default_section, child_index))
            tasks.extend(_build_tasks(user_id, default_section.id, unsectioned_tasks))
            child_index += 1

        current_rows: list[dict[str, str]] = []
        current_title: str | None = None
        for row in project.rows:
            row_type = row.get("TYPE", "").lower()
            if row_type == "section":
                if current_title is not None:
                    child = _leaf_section(
                        user_id, project_section.id, current_title, bool(current_rows)
                    )
                    sections.append((child, child_index))
                    tasks.extend(_build_tasks(user_id, child.id, current_rows))
                    child_index += 1
                current_title = row.get("CONTENT", "").strip() or "Без названия"
                current_rows = []
            elif row_type == "task" and current_title is not None:
                current_rows.append(row)
        if current_title is not None:
            child = _leaf_section(
                user_id, project_section.id, current_title, bool(current_rows)
            )
            sections.append((child, child_index))
            tasks.extend(_build_tasks(user_id, child.id, current_rows))

    return ImportedData(sections=sections, tasks=tasks)


def _tasks_before_first_section(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    tasks = []
    for row in rows:
        row_type = row.get("TYPE", "").lower()
        if row_type == "section":
            break
        if row_type == "task":
            tasks.append(row)
    return tasks


def _leaf_section(
    user_id: UUID, parent_id: UUID, title: str, has_tasks: bool
) -> Section:
    return Section(
        user_id=user_id,
        title=title,
        parent_id=parent_id,
        tasks=[],
        subsections=[],
        has_tasks=has_tasks,
        has_subsections=False,
    )


def _build_tasks(
    user_id: UUID, section_id: UUID, rows: list[dict[str, str]]
) -> list[tuple[Task, int]]:
    tasks: list[tuple[Task, int]] = []
    parents: dict[int, UUID] = {}
    for index, row in enumerate(rows):
        try:
            indent = max(1, int(row.get("INDENT", "1") or "1"))
        except ValueError:
            indent = 1
        parent_id = parents.get(indent - 1) if indent > 1 else None
        due_to, recurrence = _parse_todoist_date(row.get("DATE", ""), get_today())
        task = Task(
            user_id=user_id,
            section_id=section_id,
            parent_task_id=parent_id,
            title=row.get("CONTENT", "").strip() or "Без названия",
            description=row.get("DESCRIPTION", "").strip() or None,
            due_to=due_to,
            recurrence=recurrence,
        )
        tasks.append((task, index))
        parents[indent] = task.id
        parents = {
            level: parent for level, parent in parents.items() if level <= indent
        }
    return tasks


def _parse_todoist_date(
    raw_value: str, today: date
) -> tuple[date | None, RecurrenceInfo | None]:
    value = raw_value.strip().lower().replace("ё", "е")
    if not value:
        return None, None
    try:
        return datetime.fromisoformat(value.replace("z", "+00:00")).date(), None
    except ValueError:
        pass

    day_match = re.fullmatch(
        r"(\d{1,2})\s+([а-я]+)\.?(?:\s+(\d{4}))?(?:\s+\d{1,2}:\d{2})?",
        value,
    )
    if day_match:
        due = _calendar_date(
            int(day_match.group(1)), day_match.group(2), day_match.group(3), today
        )
        return due, None

    every_days = re.fullmatch(
        r"кажд(?:ый|ые)(!)?\s*(?:(\d+)\s*)?д(?:ень|ня|ней)", value
    )
    if every_days:
        recurrence = RecurrenceInfo(
            period=int(every_days.group(2) or 1),
            type="days",
            flexible_mode=bool(every_days.group(1)),
        )
        return today, recurrence

    every_weeks = re.fullmatch(
        r"кажд(?:ую|ые)(!)?\s*(?:(\d+)\s*)?недел(?:ю|и|ь)", value
    )
    if every_weeks:
        recurrence = RecurrenceInfo(
            period=int(every_weeks.group(2) or 1),
            type="weeks",
            flexible_mode=bool(every_weeks.group(1)),
        )
        return today, recurrence

    weekday = re.fullmatch(r"кажд(?:ый|ую)\s+([а-я]{2})", value)
    if weekday and weekday.group(1) in WEEKDAYS:
        offset = (WEEKDAYS[weekday.group(1)] - today.weekday()) % 7
        return today + timedelta(days=offset), RecurrenceInfo(
            period=1, type="weeks", flexible_mode=False
        )

    monthly = re.fullmatch(r"кажд(?:ое|ый)\s+(\d{1,2})(?:-?[ео]?)", value)
    if monthly:
        day = int(monthly.group(1))
        try:
            due = today.replace(day=day)
        except ValueError:
            return None, None
        if due < today:
            due = (today + relativedelta(months=1)).replace(day=day)
        return due, RecurrenceInfo(period=1, type="months", flexible_mode=False)

    annual = re.fullmatch(r"кажд(?:ый|ое)\s+(\d{1,2})\s+([а-я]+)", value)
    if annual:
        due = _calendar_date(int(annual.group(1)), annual.group(2), None, today)
        return due, RecurrenceInfo(period=1, type="years", flexible_mode=False)
    return None, None


def _calendar_date(day: int, month_name: str, year: str | None, today: date) -> date:
    month = MONTHS.get(month_name.rstrip("."))
    if month is None:
        raise InvalidTodoistBackupException()
    candidate_year = int(year) if year else today.year
    try:
        candidate = date(candidate_year, month, day)
    except ValueError:
        raise InvalidTodoistBackupException() from None
    if year is None and candidate < today:
        candidate = date(candidate_year + 1, month, day)
    return candidate
