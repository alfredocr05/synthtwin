"""Seeded neutral table builders for the Phase 1 tests (plan P1-D8).

No data file is ever committed (plan D13). Every table a test needs is
built here, from code, with a fixed seed, so the same test run produces
the same bytes on every machine and the repository holds no data-format
file at all.

The vocabulary is deliberately neutral and made up on the spot: labels
like "north" and "batch", column names like "reading" and "recorded_on".
Nothing here is derived from any real table.

`write_profile` lives here for the same reason the tables do: it is the
one place that decides the bytes of a description a test hands to the
loader, so no test has to decide them and no test can decide them
wrongly. Its docstring says what goes wrong when they are decided
anywhere else.
"""

import pathlib
import random

from synthtwin import canonical

# Neutral label pools. Small, plain words with no meaning outside these
# tests.
REGIONS = ("north", "south", "east", "west")
LABELS = ("alpha", "beta", "gamma", "delta", "epsilon")


def write(folder: pathlib.Path, name: str, text: str) -> pathlib.Path:
    """Write ``text`` as a UTF-8 file with newline endings; return its path."""
    target = folder / name
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def write_profile(
    folder: pathlib.Path, name: str, document: dict
) -> pathlib.Path:
    """Write ``document`` as a description file; return its path.

    THE GUARANTEE. The file left on disk is byte for byte the file
    `synthtwin profile` writes for that same document, on every
    platform. Two things carry it, and both are the product's own: the
    text is `canonical.serialize`, the serializer the loader re-writes
    with and compares against, and the write fixes the line ending
    rather than leaving it to the platform, exactly as
    `writing.write_text_file` does (plan D12).

    WHY IT EXISTS. A text-mode write with no ``newline`` argument
    translates every line ending to the platform's own, so the same two
    lines of Python leave newline bytes on Linux and macOS and
    carriage-return-newline bytes on Windows. The loader reads the file,
    writes the parsed document out again under the canonical rules, and
    refuses the file if the bytes differ -- so a description carrying
    the platform's line ending is a description it must refuse, and is
    right to refuse, because synthtwin did not write it. That is not a
    hypothetical: every Windows job of the test suite failed on it while
    every macOS and Linux job passed, with the loader and the writer
    both behaving exactly as specified. So the bytes are decided here,
    once, and a test that wants a description asks for one rather than
    building the file itself.

    Inputs: the folder to write into, the name of the file to write, and
    the profile document. Determinism: the same document gives the same
    bytes every time, on every platform.

    A test that deliberately needs bytes synthtwin would NOT write --
    proving the loader refuses them -- must not come through here. It
    writes its own exact bytes, with an explicit ``newline`` argument so
    that what it writes is what it meant on every platform too.
    """
    return write(folder, name, canonical.serialize(document))


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


def every_withholding_table(seed: int = 20260814, n_rows: int = 240) -> str:
    """A table that makes the floor hold something back in every way.

    THIS IS THE FIXTURE A DERIVATION STANDS ON. Described twice -- once
    at the default floor and once at a floor of one -- the two documents
    differ at exactly the positions the small-cell floor governs, and
    `tests/test_p3v5f1_floor_one.py` reads that difference off rather
    than trusting a list of field names somebody wrote down. A field the
    floor governs that this table does not exercise is a field that
    derivation cannot see, so every way the format has of holding
    something back is given a column here:

    * `region` -- one label that about seven rows share, so the floor
      suppresses a LEVEL and fills `suppressed_levels`,
      `suppressed_rows` and `suppressed_level_counts`;
    * `visits` -- blank cells plus three rare spellings of "no value",
      so `missing_by_source` pools a REMAINDER and `missing_by_class`
      pools the class those spellings fell into;
    * `reading` -- a common stand-in number and a rare one, so
      `n_sentinel_candidates_unpublished` counts a candidate too rare to
      name;
    * `amount` -- mostly plain decimals with one exponent and one signed
      value, so `numeric_styles` pools a FORM;
    * `stamped_at` -- times stamped in UTC with two rare offsets, so
      `utc_offsets` pools an OFFSET;
    * `answer` -- a two-value column where one row shouts its label, so
      one level's `variants_withheld` holds a SPELLING back;
    * `comment`, `unused`, `batch`, `record_code` -- free text, an empty
      column, a constant and an all-distinct column, so the roles that
      publish nothing are in the walk too.

    Every value is made up here with a fixed seed, exactly as the other
    builders in this file are (plan D13).
    """
    rng = random.Random(seed)
    header = [
        "record_code",
        "region",
        "visits",
        "reading",
        "amount",
        "stamped_at",
        "answer",
        "comment",
        "unused",
        "batch",
    ]
    rows = []
    for index in range(n_rows):
        if index % 23 == 0:
            visits = ""
        elif index == 5:
            visits = "n/a"
        elif index == 9:
            visits = "N/A"
        elif index == 11:
            visits = "unknown"
        else:
            visits = str(rng.randint(0, 9))
        if index % 19 == 0:
            reading = "-999"
        elif index in (3, 7):
            reading = "9999"
        else:
            reading = str(rng.randint(1, 400))
        if index == 13:
            amount = "1.5e3"
        elif index == 17:
            amount = "+12.25"
        else:
            amount = f"{rng.uniform(0.5, 99.5):.2f}"
        if index == 21:
            offset = "+02:00"
        elif index == 29:
            offset = "-05:00"
        else:
            offset = "Z"
        answer = "yes" if rng.random() < 0.3 else "no"
        if answer == "yes" and index % 31 == 0:
            answer = "YES"
        rows.append(
            [
                f"R{index:05d}",
                "outlying" if index % 37 == 0 else REGIONS[index % 4],
                visits,
                reading,
                amount,
                (
                    f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}"
                    f"T{index % 10:02d}:15:00{offset}"
                ),
                answer,
                (
                    ""
                    if index % 3
                    else f"observation {index} written out in plain words"
                ),
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
