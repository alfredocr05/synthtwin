"""The stage-5 golden battery: its cases and the builders that lay their inputs.

Plan P4-D395 part 5 (lane M5) designed it and lane S5a builds it (plan
P4-D437). Each case is ONE command line, the inputs it needs, built at
run time by the seeded neutral builders below -- nothing here is
committed as data -- and, for `K-S5-01`, the class and the facts a
caller must be able to read off the result, written in this table when
the case was written and never read off a run.

`tools/goldens/record_stage5_goldens.py` runs the recorded cases through
`cli.main`, the command line as typed, and keeps three records of each:
every file in the case's folder, the screen as one transcript, and the
exit status (`K-S5-02`). `tests/test_stage5_gate.py` reproduces them and
checks every case's result (`K-S5-01`).

THE TABLES ARE AT THE TABLE FLOOR (plan P4-D425): the recorder runs the
battery in a fresh interpreter, where `synthtwin profile` refuses a
table under 20,000 rows that hold a value, so every table a case
describes holds 20,000 rows, and the page's 50- and 150-row tables are
now refusal cases. Step 0's table (a record number, a date, a weight
and a ward) keeps its four columns; its date and its weight are present
on about one row in ten, which keeps the battery fast (a validate run
of 20,000 full rows took 9 seconds, measured) and is a shape health
tables hold.

Determinism: every builder draws from `random.Random(TABLE_SEED)` and
uses its `random()` stream alone, the one method whose sequence Python
promises across versions. No builder reads a clock, the network or a
file outside the battery's own folders.
"""

from __future__ import annotations

import contextlib
import dataclasses
import io
import json
import os
import pathlib
import random
import shutil
import typing

import fixtures

TABLE_ROWS = 20_000
TABLE_SEED = 20261016
SMALL_ROWS = 150
TINY_ROWS = 50
# One row in this many holds a date and a weight.
PRESENCE = 10
WARDS = ("Cardiology", "Surgery", "Oncology", "Neurology")
HEADER = "record_no,admitted,weight,ward"


@dataclasses.dataclass(frozen=True)
class Expect:
    """What `K-S5-01` reads off a case's result, written with the case.

    ``verdict`` is the class; ``exit`` the status the case's row writes
    for a case the golden battery does not record (Q1, I1, I2, DR1 to
    DR3 and the internal cases); ``step`` and ``key`` a refusal's;
    ``breaks`` the (column, fact, subcheck, tier) a damage must break,
    each among the misses; ``first_tier`` the tier of the first miss;
    ``every_tier`` the tier each miss must hold, where one does;
    ``warnings`` the warning keys in order; ``floor`` and
    ``floor_lowered`` the result's floor; ``next_words`` and
    ``next_purpose`` the next command (the words as one tuple, with
    `<FOLDER>` for the case's folder as resolved); ``carried`` the
    (class, reason, verdict) of every carried entry, in order;
    ``tally`` the doctor's counts.
    """

    verdict: str
    exit: "int | None" = None
    step: str = ""
    key: str = ""
    breaks: "tuple[tuple[str, str, str, str], ...]" = ()
    first_tier: str = ""
    every_tier: str = ""
    warnings: "tuple[str, ...]" = ()
    floor: "int | None" = None
    floor_lowered: bool = False
    next_words: "tuple[str, ...]" = ()
    next_purpose: str = ""
    carried: "tuple[tuple[str, str, str], ...] | None" = None
    tally: "tuple[tuple[str, int], ...] | None" = None
    unjudged_count: "int | None" = None


@dataclasses.dataclass(frozen=True)
class Case:
    """One command line of the battery.

    ``on`` names the case whose folder this one runs in (a case that
    builds on another runs after it, in its folder); empty means a folder
    of its own. ``build`` names the builder that lays its inputs there
    before the run. ``posix_only`` marks the cases that leave a link at
    an output's name, which Windows refuses before anything is written.
    ``argparse_text`` marks a screen argparse lays out itself, pinned on
    the recorder's Python version. ``recorded`` is False for the cases
    `K-S5-01` alone runs. ``internal`` holds `cli.run`'s internal
    keywords for the cases that need one, and ``fault`` the fault or the
    reader the case injects; a recorded case has neither.
    """

    key: str
    argv: "tuple[str, ...]"
    on: str = ""
    build: str = ""
    posix_only: bool = False
    argparse_text: bool = False
    recorded: bool = True
    internal: "tuple[tuple[str, int], ...]" = ()
    fault: str = ""
    expect: "Expect | None" = None


def _pick(stream: random.Random, count: int) -> int:
    """A whole number from 0 to ``count`` - 1, from `random()` alone."""
    return int(stream.random() * count)


def step0_table(n_rows: int) -> str:
    """Step 0's table at ``n_rows`` rows: a record number, a date, a weight, a ward.

    The record number fills every row and the ward every row; the date
    (month and day padded, the year 2024) and the weight (one decimal,
    the sum of three uniform draws, about 50 to 104) each fill about one
    row in `PRESENCE`.
    """
    stream = random.Random(TABLE_SEED)
    rows = [HEADER]
    for index in range(n_rows):
        month = 1 + _pick(stream, 12)
        day = 1 + _pick(stream, 28)
        admitted = f"{month:02d}/{day:02d}/2024"
        weight = 50.0 + 18.0 * (stream.random() + stream.random() + stream.random())
        written = f"{weight:.1f}"
        ward = WARDS[_pick(stream, len(WARDS))]
        if _pick(stream, PRESENCE) != 0:
            admitted = ""
        if _pick(stream, PRESENCE) != 0:
            written = ""
        rows += [f"REC{100000 + index},{admitted},{written},{ward}"]
    return "\n".join(rows) + "\n"


def _write(folder: pathlib.Path, name: str, text: str) -> None:
    (folder / name).write_text(text, encoding="utf-8", newline="\n")


def _copy(source: pathlib.Path, target: pathlib.Path) -> None:
    target.write_bytes(source.read_bytes())


def _description(root: pathlib.Path) -> "dict[str, typing.Any]":
    """G1's description, as G1 wrote it."""
    loaded = json.loads((root / "G1" / "t-profile.json").read_text(encoding="utf-8"))
    return typing.cast("dict[str, typing.Any]", loaded)


def _column(document: "dict[str, typing.Any]", name: str) -> "dict[str, typing.Any]":
    for block in document["columns"]:
        if block["name"] == name:
            return typing.cast("dict[str, typing.Any]", block)
    raise AssertionError(f"G1's description has no column named {name}")


def _twin_rows(root: pathlib.Path) -> "list[list[str]]":
    """G2's twin, split into its rows and cells (no cell holds a comma)."""
    text = (root / "G1" / "t-twin.csv").read_text(encoding="utf-8")
    lines = text.split("\n")
    if lines and lines[-1] == "":
        lines = lines[:-1]
    return [line.split(",") for line in lines]


def _joined(rows: "list[list[str]]") -> str:
    return "\n".join([",".join(row) for row in rows]) + "\n"


def _with_twin(folder: pathlib.Path, root: pathlib.Path, rows: "list[list[str]]") -> None:
    _copy(root / "G1" / "t-profile.json", folder / "t-profile.json")
    _write(folder, "t-twin.csv", _joined(rows))


def _where(rows: "list[list[str]]", name: str) -> int:
    return rows[0].index(name)


def _blank_one_weight(rows: "list[list[str]]") -> "list[list[str]]":
    at = _where(rows, "weight")
    for row in rows[1:]:
        if row[at]:
            row[at] = ""
            break
    return rows


def _recase_thirty(rows: "list[list[str]]") -> "list[list[str]]":
    at = _where(rows, "ward")
    left = 30
    for row in rows[1:]:
        if left and row[at] == "Cardiology":
            row[at] = "CARDIOLOGY"
            left = left - 1
    return rows


def _recase_header(rows: "list[list[str]]") -> "list[list[str]]":
    rows[0][_where(rows, "ward")] = "Ward"
    return rows


def _scale_weights(rows: "list[list[str]]") -> "list[list[str]]":
    at = _where(rows, "weight")
    for row in rows[1:]:
        if row[at]:
            row[at] = f"{float(row[at]) * 1.1:.1f}"
    return rows


def _weights_as_words(rows: "list[list[str]]") -> "list[list[str]]":
    at = _where(rows, "weight")
    for row in rows[1:]:
        if row[at]:
            row[at] = "seventy"
    return rows


def _dates_unpadded(rows: "list[list[str]]") -> "list[list[str]]":
    at = _where(rows, "admitted")
    for row in rows[1:]:
        if row[at]:
            month, day, year = row[at].split("/")
            row[at] = f"{int(month)}/{int(day)}/{year}"
    return rows


def build(name: str, folder: pathlib.Path, root: pathlib.Path) -> None:
    """Lay the inputs builder ``name`` names in ``folder``.

    ``root`` holds every case's folder, so a builder can start from an
    earlier case's output (G1's description, G2's twin). Raises
    AssertionError for a name no builder answers to.
    """
    if name == "table":
        _write(folder, "t.csv", step0_table(TABLE_ROWS))
    elif name == "small":
        _write(folder, "small.csv", step0_table(SMALL_ROWS))
    elif name == "tiny":
        _write(folder, "tiny.csv", step0_table(TINY_ROWS))
    elif name == "every":
        _write(folder, "every.csv", fixtures.every_role_and_joined_table(n_rows=TABLE_ROWS))
    elif name == "broken":
        _write(folder, "broken.json", "{not json\n")
    elif name == "answers":
        _answer_record_number(folder)
    elif name == "lowered":
        _lowered_description(folder)
    elif name == "older":
        document = _description(root)
        document["relationships"]["statistical"] = None
        fixtures.write_profile(folder, "t-profile.json", document)
    elif name == "zeros":
        document = _description(root)
        _column(document, "weight")["n_zero"] = 12
        fixtures.write_profile(folder, "t-profile.json", document)
    elif name == "refusal":
        document = _description(root)
        weight = _column(document, "weight")
        weight["n_zero"] = weight["n_numeric"]
        weight["n_negative"] = 1
        fixtures.write_profile(folder, "t-profile.json", document)
    elif name == "refusal-twin":
        _copy(root / "G1" / "t-twin.csv", folder / "t-twin.csv")
    elif name == "questions-link":
        _write(folder, "t.csv", step0_table(TABLE_ROWS))
        os.symlink("t.csv", folder / "t-questions.json")
    elif name == "profile-link":
        _write(folder, "t.csv", step0_table(TABLE_ROWS))
        os.symlink("t.csv", folder / "t-profile.json")
    elif name == "twin-link":
        _copy(root / "G1" / "t-profile.json", folder / "t-profile.json")
        os.symlink("t-profile.json", folder / "t-twin.csv")
    elif name == "quality-link":
        _copy(root / "G1" / "t-profile.json", folder / "t-profile.json")
        _copy(root / "G1" / "t-twin.csv", folder / "t-twin.csv")
        os.symlink("t-profile.json", folder / "t-twin-quality.txt")
    elif name in _DAMAGES:
        _with_twin(folder, root, _DAMAGES[name](_twin_rows(root)))
    else:
        raise AssertionError(f"no builder is named {name}")


def _lowered_description(folder: pathlib.Path) -> None:
    """G11's input: Step 0's table described at a smallest group of 5.

    No command line reaches a floor under 11 since plan P4-D426, so the
    description is written by the profiler through the command's
    internal setting (`internal_smallest_group`, which no option,
    environment variable or file sets), as the suite's own helpers write
    one; its screen is let go. The table is at the floor, so the table
    floor's keyword (off here, as in the suite's helpers) changes nothing. The case then shows what `generate` and
    `validate` do with a description recorded under 11.
    """
    from synthtwin import cli

    _write(folder, "t.csv", step0_table(TABLE_ROWS))
    here = os.getcwd()
    try:
        os.chdir(folder)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(
            io.StringIO()
        ):
            code = cli.main(
                ["profile", "t.csv", "--identifier", "record_no"],
                small_tables_refused=False,
                internal_smallest_group=5,
            )
    finally:
        os.chdir(here)
    if code != 0:
        raise AssertionError(f"G11's description was not written (exit {code})")


def _answer_record_number(folder: pathlib.Path) -> None:
    """G7's answers: G6's questions file with `record_no` answered `identifier`.

    Every entry naming `record_no` that offers `identifier` is answered
    so, wherever the file puts it (asked, or the checklist); every other
    entry is left blank, which keeps its reading.
    """
    document = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))

    def answer(node: object) -> None:
        if isinstance(node, dict):
            offered = node.get("answers_you_can_give")
            if node.get("column") == "record_no" and isinstance(offered, list):
                if any(
                    isinstance(entry, dict) and entry.get("answer") == "identifier"
                    for entry in offered
                ):
                    node["your_answer"] = "identifier"
            for value in node.values():
                answer(value)
        elif isinstance(node, list):
            for value in node:
                answer(value)

    answer(document)
    _write(folder, "a.json", json.dumps(document, indent=2, sort_keys=True) + "\n")


_DAMAGES: "dict[str, typing.Callable[[list[list[str]]], list[list[str]]]]" = {
    "damage-M1": _blank_one_weight,
    "damage-M2": _recase_thirty,
    "damage-M3": _recase_header,
    "damage-M4": lambda rows: rows[:-12],
    "damage-M5": lambda rows: [[row[1], row[0]] + row[2:] for row in rows],
    "damage-M6": lambda rows: [["﻿" + rows[0][0]] + rows[0][1:]] + rows[1:],
    "damage-M7": _scale_weights,
    "damage-M8": lambda rows: _recase_header(_recase_thirty(rows)),
    "damage-M9": _weights_as_words,
    "damage-M10": _dates_unpadded,
}


def _case(key: str, *argv: str, **fields: typing.Any) -> Case:
    return Case(key, tuple(argv), **fields)


_PROFILE_T = ("profile", "t.csv", "--identifier", "record_no")
_GENERATE_T = ("generate", "t-profile.json", "--seed", "7")
_VALIDATE_T = ("validate", "t-profile.json")

# THE RECORDED CASES, in the order they run. Part 5's table names them;
# a case holding several command lines is one case a line (G5.1 to G5.3,
# G10.1 to G10.3, G11.1 and G11.2, O1.1 and O1.2, R6.1 and R6.2).
RECORDED: "tuple[Case, ...]" = (
    _case("G1", *_PROFILE_T, build="table"),
    _case("G2", *_GENERATE_T, on="G1"),
    _case("G3", *_VALIDATE_T, on="G1"),
    _case("G4", *_VALIDATE_T, "--twin", "t.csv", on="G1"),
    _case("R3", *_GENERATE_T, on="G1"),
    _case("R4", *_VALIDATE_T, on="G1"),
    _case("R7", *_VALIDATE_T, "--twin", "missing.csv", on="G1"),
    _case(
        "G5.1",
        "profile",
        "every.csv",
        "--identifier",
        "record_code",
        "--measurement",
        "pressure",
        "--smallest-group",
        "11",
        build="every",
    ),
    _case("G5.2", "generate", "every-profile.json", "--seed", "20260811", on="G5.1"),
    _case("G5.3", "validate", "every-profile.json", on="G5.1"),
    _case("G6", "profile", "t.csv", build="table"),
    _case("G7", "profile", "t.csv", "--answers", "a.json", on="G6", build="answers"),
    _case("G8", "profile", "small.csv", build="small"),
    _case("G9", "profile", "t.csv", "--smallest-group", "5", build="table"),
    _case("G10.1"),
    _case("G10.2", "--help", argparse_text=True),
    _case("G10.3", "--version"),
    _case("G11.1", *_GENERATE_T, build="lowered"),
    _case("G11.2", *_VALIDATE_T, on="G11.1"),
    _case("O1.1", *_GENERATE_T, build="older"),
    _case("O1.2", *_VALIDATE_T, on="O1.1"),
    _case("L1", *_PROFILE_T, build="questions-link", posix_only=True),
    _case("R1", "profile", "missing.csv"),
    _case("R2", "profile", "tiny.csv", build="tiny"),
    _case("R5", "generate", "broken.json", build="broken"),
    _case("R6.1", *_GENERATE_T, build="refusal"),
    _case("R6.2", *_VALIDATE_T, on="R6.1", build="refusal-twin"),
    _case("L2", *_PROFILE_T, build="profile-link", posix_only=True),
    _case("L3", *_GENERATE_T, build="twin-link", posix_only=True),
    _case("L4", *_VALIDATE_T, build="quality-link", posix_only=True),
    _case("U1", "generate", "t-profile.json", "--seed", "-1"),
    _case("U2", "profile", "t.csv", "--smallest-group", "0", build="table"),
    _case("U3", "profile", "t.csv", "--no-such-option", build="table"),
    _case(
        "U4",
        "profile",
        "t.csv",
        "--keep-value",
        "-999",
        "--missing-value",
        "-999",
        build="table",
    ),
    _case("M1", *_VALIDATE_T, build="damage-M1"),
    _case("M2", *_VALIDATE_T, build="damage-M2"),
    _case("M3", *_VALIDATE_T, build="damage-M3"),
    _case("M4", *_VALIDATE_T, build="damage-M4"),
    _case("M5", *_VALIDATE_T, build="damage-M5"),
    _case("M6", *_VALIDATE_T, build="damage-M6"),
    _case("M7", *_VALIDATE_T, build="damage-M7"),
    _case("M8", *_VALIDATE_T, build="damage-M8"),
    _case("M9", *_VALIDATE_T, build="damage-M9"),
    _case("M10", *_VALIDATE_T, build="damage-M10"),
    _case("D1", *_GENERATE_T, build="zeros"),
)


def recorded_rows() -> "tuple[tuple[object, ...], ...]":
    """The recorded cases as the goldens' digest reads them.

    The fields that decide what a recorded run does -- its id, its
    command line, its folder, its builder and its two platform marks --
    and nothing `K-S5-01` adds, so writing a case's expectation never
    asks for the goldens to be recorded again.
    """
    return tuple(
        [
            (case.key, case.argv, case.on, case.build, case.posix_only, case.argparse_text)
            for case in RECORDED
        ]
    )


def lay(case: Case, root: pathlib.Path) -> pathlib.Path:
    """Make the case's folder (or find its base case's) and lay its inputs; return it."""
    folder = root / (case.on or case.key)
    folder.mkdir(parents=True, exist_ok=True)
    if case.build:
        build(case.build, folder, root)
    return folder


def clear(root: pathlib.Path) -> None:
    """Remove every case folder under ``root`` (links removed, never followed)."""
    if root.exists():
        shutil.rmtree(root)
