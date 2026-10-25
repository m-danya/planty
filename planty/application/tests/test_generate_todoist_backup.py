"""Sanity checks for the synthetic Todoist backup fixture."""

from __future__ import annotations

import csv
import io
import json
import zipfile
from pathlib import Path

from planty.application.tests.fixtures.generate_todoist_backup import (
    HEADER,
    NUM_COLUMNS,
    build_todoist_backup_zip,
)


def _parse_csv(raw: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(raw)))


def test_zip_structure(tmp_path: Path) -> None:
    dest = build_todoist_backup_zip(tmp_path / "todoist_backup.zip")
    names = zipfile.ZipFile(dest).namelist()

    project_csvs = [n for n in names if n.endswith(".csv")]
    attachments = [n for n in names if n.startswith("attachments/")]
    assert len(project_csvs) == 4
    assert all("[xTst" in n for n in project_csvs)
    assert {"attachments/image.png", "attachments/Тестовый отчёт.pdf"} <= set(
        attachments
    )


def test_csv_shape_and_row_types(tmp_path: Path) -> None:
    dest = build_todoist_backup_zip(tmp_path / "todoist_backup.zip")
    with zipfile.ZipFile(dest) as zf:
        for name in (n for n in zf.namelist() if n.endswith(".csv")):
            raw = zf.read(name).decode("utf-8-sig")
            assert raw.endswith("\r\n")
            rows = _parse_csv(raw)
            assert all(len(row) == NUM_COLUMNS for row in rows)
            types = {row[0] for row in rows[1:]}
            assert types <= {"task", "section", "note", "reminder", "meta"}
            assert rows[1][0] == "meta"
            assert rows[1][1].startswith("view_style=")


def test_case_coverage(tmp_path: Path) -> None:
    dest = build_todoist_backup_zip(tmp_path / "todoist_backup.zip")
    with zipfile.ZipFile(dest) as zf:
        all_rows: list[list[str]] = []
        sizes: dict[str, int] = {}
        for name in (n for n in zf.namelist() if n.endswith(".csv")):
            rows = _parse_csv(zf.read(name).decode("utf-8-sig"))
            all_rows.extend(rows[1:])
        for name in (n for n in zf.namelist() if n.startswith("attachments/")):
            sizes[name.split("/")[-1]] = len(zf.read(name))

    by_type: dict[str, list[list[str]]] = {}
    for row in all_rows:
        by_type.setdefault(row[0], []).append(row)

    idx = {c: i for i, c in enumerate(HEADER)}
    tasks = by_type["task"]
    assert {r[idx["PRIORITY"]] for r in tasks} == {"1", "2", "3", "4"}
    assert {r[idx["INDENT"]] for r in tasks} == {"1", "2"}
    dates = {r[idx["DATE"]] for r in tasks if r[idx["DATE"]]}
    assert "26 окт 17:45" in dates
    assert "2026-11-15" in dates
    assert "2026-11-15T09:30:00.123456Z" in dates
    assert "каждый! день" in dates
    assert "каждую вс" in dates
    assert "28 ноября 2027" in dates
    assert {r[idx["TIMEZONE"]] for r in tasks} == {"Europe/Moscow", "Europe/Berlin"}

    assert {r[idx["CONTENT"]] for r in by_type["section"]}
    assert {"True", "False"} <= {r[4] for r in by_type["section"]}

    assert len(by_type["reminder"]) >= 2
    notes = by_type["note"]
    embeds = [
        json.loads(r[1].split("[[file ")[1].rsplit("]]", 1)[0])
        for r in notes
        if "[[file " in r[1]
    ]
    assert len(embeds) == 3
    for embed in embeds:
        assert embed["file_size"] == sizes[embed["file_name"]]
        assert embed["upload_state"] == "completed"


def test_output_is_deterministic(tmp_path: Path) -> None:
    a = build_todoist_backup_zip(tmp_path / "a.zip").read_bytes()
    b = build_todoist_backup_zip(tmp_path / "b.zip").read_bytes()
    assert a == b
