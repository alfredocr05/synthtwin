"""Seeded neutral table builders for the Phase 1 tests (plan P1-D8).

No data file is ever committed (plan D13). Every table a test needs is
built here, from code, with a fixed seed, so the same test run produces
the same bytes on every machine and the repository holds no data-format
file at all.

The vocabulary is deliberately neutral and made up on the spot: labels
like "north" and "batch", column names like "reading" and "recorded_on".
Nothing here is derived from any real table.
"""

import pathlib
import random

# Neutral label pools. Small, plain words with no meaning outside these
# tests.
REGIONS = ("north", "south", "east", "west")
LABELS = ("alpha", "beta", "gamma", "delta", "epsilon")


def write(folder: pathlib.Path, name: str, text: str) -> pathlib.Path:
    """Write ``text`` as a UTF-8 file with newline endings; return its path."""
    target = folder / name
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def rows_to_csv(header: list[str], rows: list[list[str]]) -> str:
    """Turn a header and rows into CSV text, quoting only when needed."""
    lines = [",".join(header)]
    for row in rows:
        cells = []
        for cell in row:
            if "," in cell or '"' in cell or "\n" in cell:
                escaped = cell.replace('"', '""')
                cells.append(f'"{escaped}"')
            else:
                cells.append(cell)
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def every_role_table(seed: int = 20260807, n_rows: int = 240) -> str:
    """A table with one column for (almost) every role in the taxonomy.

    Columns, in order: a record number; a category with one rare label
    that the small-cell floor must withhold; whole numbers with blank
    cells; whole numbers using -999 as a stand-in for "no value"; a
    measured number; an ISO date; a two-value column; free text; a
    column that is entirely blank; and a column with one repeated value.
    """
    rng = random.Random(seed)
    header = [
        "record_code",
        "region",
        "visits",
        "reading",
        "amount",
        "recorded_on",
        "answer",
        "comment",
        "unused",
        "batch",
    ]
    rows = []
    for index in range(n_rows):
        record = f"R{index:05d}"
        region = "outlying" if index % 37 == 0 else REGIONS[index % 4]
        visits = "" if index % 23 == 0 else str(rng.randint(0, 9))
        reading = "-999" if index % 19 == 0 else str(rng.randint(1, 400))
        amount = f"{rng.uniform(0.5, 99.5):.2f}"
        recorded = f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}"
        answer = "yes" if rng.random() < 0.3 else "no"
        comment = (
            ""
            if index % 3
            else f"observation {index} written out in several plain words"
        )
        rows.append(
            [
                record,
                region,
                visits,
                reading,
                amount,
                recorded,
                answer,
                comment,
                "",
                "one",
            ]
        )
    return rows_to_csv(header, rows)


def single_column_table(name: str, values: list[str]) -> str:
    """A one-column table holding exactly ``values``."""
    return rows_to_csv([name], [[value] for value in values])


def numbers(seed: int, count: int, low: int, high: int) -> list[str]:
    """``count`` whole numbers written as text, drawn with ``seed``."""
    rng = random.Random(seed)
    return [str(rng.randint(low, high)) for _index in range(count)]


def labels(seed: int, count: int, pool: tuple[str, ...] = LABELS) -> list[str]:
    """``count`` labels drawn from ``pool`` with ``seed``."""
    rng = random.Random(seed)
    return [pool[rng.randrange(len(pool))] for _index in range(count)]
