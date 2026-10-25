"""Generate a synthetic Todoist backup archive.

Builds a zip that mirrors the structure of a real Todoist "Backup as CSV"
export, using only clearly fictional data (no personal information):

- one CSV per project, named ``Project name [<16-char id>].csv``
- ``utf-8-sig`` BOM, CRLF line endings, 20 columns
- ``meta`` rows (``view_style=list`` / ``view_style=board``)
- ``task`` rows: priorities 1-4, indent levels, Russian natural-language
  dates, date-only and full-timestamp dates, multiple timezones,
  multiline / markdown / quote / link content
- ``section`` rows with collapsed / expanded state
- ``note`` rows, including ``[[file {...}]]`` attachment embeds (ASCII and
  Cyrillic file names)
- ``reminder`` rows
- an ``attachments/`` folder with tiny generated PNG and PDF files

Usage::

    python -m planty.application.tests.fixtures.generate_todoist_backup \
        path/to/todoist_backup.zip

or from a test::

    from planty.application.tests.fixtures.generate_todoist_backup import (
        build_todoist_backup_zip,
    )

    build_todoist_backup_zip(tmp_path / "todoist_backup.zip")

The output is fully deterministic: repeated runs produce identical bytes.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import struct
import zipfile
import zlib
from pathlib import Path

HEADER = [
    "TYPE",
    "CONTENT",
    "DESCRIPTION",
    "ICON",
    "IS_COLLAPSED",
    "PRIORITY",
    "INDENT",
    "AUTHOR",
    "RESPONSIBLE",
    "DATE",
    "DATE_LANG",
    "TIMEZONE",
    "DURATION",
    "DURATION_UNIT",
    "DEADLINE",
    "DEADLINE_LANG",
    "REMINDER_TYPE",
    "REMINDER_OFFSET",
    "REMINDER_DATE",
    "REMINDER_DATE_LANG",
]
NUM_COLUMNS = len(HEADER)
assert NUM_COLUMNS == 20

AUTHOR = "planty_test (9900001)"
TZ = "Europe/Moscow"

# Fixed timestamps reused from public date ranges only (not personal data).
NOTE_DATES = [
    "2026-10-20T11:23:37.634770Z",
    "2026-10-21T09:15:02.481200Z",
    "2026-10-22T18:03:08.151000Z",
    "2026-10-23T13:10:26.768000Z",
]


def _task(
    content: str,
    *,
    description: str = "",
    priority: int = 4,
    indent: int = 1,
    date: str = "",
    timezone: str = TZ,
) -> list[str]:
    row = [""] * NUM_COLUMNS
    row[0] = "task"
    row[1] = content
    row[2] = description
    row[5] = str(priority)
    row[6] = str(indent)
    row[7] = AUTHOR
    if date:
        row[9] = date
        row[10] = "ru"
    row[11] = timezone
    return row


def _section(name: str, *, collapsed: bool = False) -> list[str]:
    row = [""] * NUM_COLUMNS
    row[0] = "section"
    row[1] = name
    row[4] = str(collapsed)
    return row


def _note(content: str, date: str) -> list[str]:
    row = [""] * NUM_COLUMNS
    row[0] = "note"
    row[1] = content
    row[7] = AUTHOR
    row[9] = date
    return row


def _reminder() -> list[str]:
    row = [""] * NUM_COLUMNS
    row[0] = "reminder"
    row[1] = "Reminder"
    row[8] = AUTHOR
    row[16] = "relative"
    row[17] = "0"
    return row


def _meta(view_style: str) -> list[str]:
    row = [""] * NUM_COLUMNS
    row[0] = "meta"
    row[1] = f"view_style={view_style}"
    return row


def _file_embed(
    file_name: str,
    file_size: int,
    *,
    file_type: str,
    resource_type: str,
    fake_hash: str,
    image_width: int | None = None,
    image_height: int | None = None,
) -> str:
    embed: dict[str, object] = {
        "file_name": file_name,
        "file_size": file_size,
        "file_type": file_type,
        "file_url": f"https://files.todoist.com/{fake_hash}/by/9900001/as/file.png",
        "resource_type": resource_type,
        "upload_state": "completed",
    }
    if image_width is not None and image_height is not None:
        embed["image"] = f"https://files.todoist.com/{fake_hash}/by/9900001/as/file.png"
        embed["image_height"] = image_height
        embed["image_width"] = image_width
    return f" [[file {json.dumps(embed, ensure_ascii=True, separators=(',', ':'))}]]"


def _png_bytes(width: int, height: int, rgb: tuple[int, int, int]) -> bytes:
    """Build a minimal solid-color PNG in pure Python."""

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", width, height, 8, 2, 0, 0, 0)
    raw = b"".join(b"\x00" + bytes(rgb) * width for _ in range(height))
    return (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )


def _minimal_pdf_bytes(title: str) -> bytes:
    """Build a tiny one-page PDF containing a title string."""
    content = f"BT /F1 24 Tf 72 720 Td ({title}) Tj ET".encode("latin-1")
    parts = [b"%PDF-1.4\n"]
    objs: list[bytes] = [
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n",
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n",
        (
            b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 595 842] "
            b"/Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        ),
        (
            b"4 0 obj\n<< /Length "
            + str(len(content)).encode("ascii")
            + b" >>\nstream\n"
            + content
            + b"\nendstream\nendobj\n"
        ),
        (
            b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\n"
            b"endobj\n"
        ),
    ]
    offsets = [0]
    data = parts[0]
    for obj in objs:
        offsets.append(len(data))
        data += obj
    xref = f"xref\n0 {len(objs) + 1}\n0000000000 65535 f \n".encode("latin-1")
    for off in offsets[1:]:
        xref += f"{off:010d} 00000 n \n".encode("latin-1")
    trailer = (
        f"trailer\n<< /Size {len(objs) + 1} /Root 1 0 R >>\n"
        f"startxref\n{len(data)}\n%%EOF\n"
    ).encode("latin-1")
    return data + xref + trailer


def _projects(attachments: dict[str, bytes]) -> list[tuple[str, list[list[str]]]]:
    image_png = attachments["image.png"]
    image_2_png = attachments["image_2.png"]
    report_pdf = attachments["Тестовый отчёт.pdf"]

    inbox: list[list[str]] = [_meta("list")]
    inbox += [
        _task("Купить тестовые батарейки"),
        _task(
            "Проверить [тестовую ссылку](https://example.com/test)",
            date="26 окт 17:45",
        ),
        _task(
            "Сделать тестовую уборку\n- протереть стол\n- полить растение",
        ),
        _task('Обсудить "тестовый план", детали в вики', priority=3),
        _task(
            "Написать ~~черновик~~ финальный `тестовый` **отчёт**",
            date="31 окт. 13:00",
        ),
        _task(
            "Спланировать тестовую поездку",
            description="Маршрут:\n- день 1: заселиться\n- день 2: экскурсия",
            priority=2,
        ),
        _task("Тестовая задача с датой", date="2026-11-15"),
        _task(
            "Тестовая задача с полным временем",
            date="2026-11-15T09:30:00.123456Z",
        ),
        _task("Тестовая задача с низким приоритетом", priority=1),
        _task("Подзадача тестового плана", indent=2),
        _task(
            "Тестовая задача в другом таймзоне",
            timezone="Europe/Berlin",
        ),
        _reminder(),
        _reminder(),
    ]

    chill: list[list[str]] = [
        _meta("list"),
        _section("Тестовый раздел один"),
        _task("📝 Написать тестовую заметку"),
        _task("[Тестовая статья](https://example.org/articles/test)"),
        _task("Тестовая подзаметка", indent=2, priority=3),
        _section("Тестовый раздел два", collapsed=True),
        _task("Старая тестовая задача", priority=2),
        _note("Обычная тестовая заметка", NOTE_DATES[0]),
        _note(
            "Заметка со ссылкой https://example.com/test-page",
            NOTE_DATES[1],
        ),
        _note(
            "Тестовое фото"
            + _file_embed(
                "image.png",
                len(image_png),
                file_type="image/png",
                resource_type="image",
                fake_hash="xTestInboxA00000001",
                image_width=8,
                image_height=8,
            ),
            NOTE_DATES[2],
        ),
        _note(
            "Вторая тестовая картинка"
            + _file_embed(
                "image_2.png",
                len(image_2_png),
                file_type="image/png",
                resource_type="image",
                fake_hash="xTestInboxA00000003",
                image_width=4,
                image_height=4,
            ),
            NOTE_DATES[0],
        ),
        _note(
            "Тестовый файл"
            + _file_embed(
                "Тестовый отчёт.pdf",
                len(report_pdf),
                file_type="application/pdf",
                resource_type="file",
                fake_hash="xTestInboxA00000002",
            ),
            NOTE_DATES[3],
        ),
        _reminder(),
    ]

    calendar: list[list[str]] = [
        _meta("list"),
        _task("Каждый день: тестовая привычка", date="каждый! день"),
        _task("Каждые два дня: тестовая тренировка", date="каждые! 2 дня"),
        _task("По воскресеньям: тестовая прогулка", date="каждую вс"),
        _task("Тестовый день рождения", date="каждый 25 апр"),
        _task("Тестовое ежемесячное событие", date="каждое 5-е"),
        _task("Тестовое ежегодное событие", date="каждый 1 января"),
        _task("Тестовое событие в будущем", date="28 ноября 2027"),
        _task("Тестовая дата без года", date="29 ноября"),
    ]

    empty = [_meta("board")]

    return [
        ("Inbox [xTstInbox0000001].csv", inbox),
        ("🌴 Тестовый проект [xTstChill0000002].csv", chill),
        ("Календарь [xTstCalend0000003].csv", calendar),
        ("Пустой проект [xTstEmpty0000004].csv", empty),
    ]


def build_todoist_backup_zip(dest: Path | str) -> Path:
    """Write the synthetic Todoist backup archive to ``dest``."""
    dest_path = Path(dest)
    dest_path.parent.mkdir(parents=True, exist_ok=True)

    image_png = _png_bytes(8, 8, (220, 38, 38))
    image_2_png = _png_bytes(4, 4, (37, 99, 235))
    receipt_pdf = _minimal_pdf_bytes("Test receipt")
    report_pdf = _minimal_pdf_bytes("Test report")
    attachments = {
        "image.png": image_png,
        "image_2.png": image_2_png,
        "test receipt.pdf": receipt_pdf,
        "Тестовый отчёт.pdf": report_pdf,
    }
    projects = _projects(attachments)

    timestamp = (2026, 10, 25, 10, 10, 44)
    with zipfile.ZipFile(dest_path, "w", zipfile.ZIP_DEFLATED) as zf:
        for name, rows in projects:
            info = zipfile.ZipInfo(name, date_time=timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            text = _render_csv(rows)
            zf.writestr(info, text)
        for name, data in attachments.items():
            info = zipfile.ZipInfo(f"attachments/{name}", date_time=timestamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            zf.writestr(info, data)
    return dest_path


def _render_csv(rows: list[list[str]]) -> str:
    buf = io.StringIO()
    writer = csv.writer(buf, lineterminator="\r\n")
    writer.writerow(HEADER)
    writer.writerows(rows)
    return buf.getvalue()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("dest", type=Path, help="path of the zip file to write")
    args = parser.parse_args()
    dest = build_todoist_backup_zip(args.dest)
    print(f"wrote {dest}")


if __name__ == "__main__":
    main()
