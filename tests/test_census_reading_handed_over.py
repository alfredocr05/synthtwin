"""Every column is read once, and split once for the person question.

THE DEFECT, counted rather than timed. Stage 3 put the population census
in front of the description (plan P4-D341): `cli._population_of` reads
the columns it needs under the finished reading
(`taxonomy._read_the_column`) before anything is described, and
`profile_column` then read the same column object again with the same
arguments. The person question (plan P4-D340) split every column with
`taxonomy.split_missing` straight after `asking.questions_for` had split
the same columns under the same settings. Measured by cProfile on the
KPI's own `labels2` table at 200,000 rows: 747.1 million calls against
541.7 million before stage 3, all of it those two repeats, and K-S1-05
went from 14.1 s to 19-20 s.

THE REPAIR HANDS THE ANSWERS OVER, EXPLICITLY. The census returns the
reading it kept (`taxonomy.HeldReading`, carrying every argument it was
read under), the command passes it to `profile.build_document`, and
`profile_column` takes it only where every argument is the same.
`asking.questions_and_splits_for` returns what it split, and
`asking.person_questions` takes it where the column object and the
settings are the same.

WHAT THIS FILE PINS -- call counts, which the machine does not decide:

1. On `synthtwin profile` of a small table, no column is read twice, and
   the person question splits nothing -- once with no declaration, where
   the census reads the first column, and once with a declared
   identifier that is not the first column, where the census asks after
   the identifier three times and reads the first column besides.
2. A reading handed over under ANY different argument is not taken, and
   neither is a split handed over from other settings or another column.
3. A reading taken over is, field for field, the reading
   `_read_the_column` returns under the description's own settings --
   including the settings its tally carries, which differ from the
   census's in `person_columns`.

THE RED CHECK, done by hand when this file was written: `profile_column`
with its `handed_over` argument ignored, and the command passing no
splits to `person_questions`, each turned item 1 red; `person_questions`
without its settings check, and without its column check, each turned
item 2's split test red; the kept reading taken as it was kept, with
the census's settings on its tally, turned item 3 red.
"""

from __future__ import annotations

import dataclasses
import pathlib

import pytest

from synthtwin import asking, profile, reading, taxonomy
from synthtwin.cli import main

import fixtures

# Over `parsing.POPULATION_FLOOR`, so the table is described rather than
# refused, and small, so the file costs well under a second.
_ROWS = 150


def _write(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> pathlib.Path:
    return fixtures.write(folder, "clinic.csv", fixtures.rows_to_csv(header, rows))


def _counted_run(
    monkeypatch: pytest.MonkeyPatch,
    folder: pathlib.Path,
    table: pathlib.Path,
    *options: str,
) -> "tuple[dict[int, int], int, int]":
    """Describe the table; count the readings per column and the splits.

    Returns how many times each column OBJECT was read by
    `_read_the_column` (keyed by its place in the order first read), how
    many `split_missing` calls ran inside `person_questions`, and how
    many times `person_questions` was asked at all.
    """
    readings: "list[tuple[list[str], int]]" = []
    inside = [False]
    splits = [0]
    asked = [0]
    reading_as_shipped = taxonomy._read_the_column
    split_as_shipped = taxonomy.split_missing
    person_as_shipped = asking.person_questions

    def counted_reading(values: "list[str]", *args: object, **named: object) -> object:
        nonlocal readings
        place = 0
        for seen, count in readings:
            if seen is values:
                readings[place] = (seen, count + 1)
                break
            place = place + 1
        else:
            readings += [(values, 1)]
        return reading_as_shipped(values, *args, **named)  # type: ignore[arg-type]

    def counted_split(*args: object, **named: object) -> object:
        if inside[0]:
            splits[0] = splits[0] + 1
        return split_as_shipped(*args, **named)  # type: ignore[arg-type]

    def counted_person(*args: object, **named: object) -> object:
        asked[0] = asked[0] + 1
        inside[0] = True
        try:
            return person_as_shipped(*args, **named)  # type: ignore[arg-type]
        finally:
            inside[0] = False

    monkeypatch.setattr(taxonomy, "_read_the_column", counted_reading)
    monkeypatch.setattr(taxonomy, "split_missing", counted_split)
    monkeypatch.setattr(asking, "person_questions", counted_person)
    folder.mkdir(parents=True, exist_ok=True)
    assert main(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace"] + list(options)
    ) == 0
    per_column = {place: count for place, (_values, count) in enumerate(readings)}
    return per_column, splits[0], asked[0]


def test_no_declaration_reads_each_column_once_and_splits_nothing_twice(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The census reads the first column; the description takes it over."""
    rows = [
        [fixtures.REGIONS[place % 4], fixtures.LABELS[place % 5], f"{place % 37}"]
        for place in range(_ROWS)
    ]
    table = _write(tmp_path, ["site", "grade", "score"], rows)
    per_column, splits, asked = _counted_run(monkeypatch, tmp_path / "out", table)
    assert per_column == {0: 1, 1: 1, 2: 1}, (
        "a column was read twice by `_read_the_column`: the census's "
        "reading was not handed over to the description"
    )
    # The person question is put twice per run -- before the files and
    # again from the finished description -- and splits nothing either time.
    assert asked == 2
    assert splits == 0, (
        "`person_questions` split a column `questions_for` had just split"
    )


def test_a_declared_identifier_is_read_once_although_the_census_asks_three_times(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Does it repeat, does each row hold something, who is each row.

    The identifier is the SECOND column and the first column has holes,
    so the census reads the identifier (does it repeat), then the first
    column and the identifier again (which rows hold something), then the
    identifier a third time (who is each row). The identifier's reading
    is the one the census keeps, so it answers all three and the
    description takes it over.
    """
    rows = [
        [
            "" if place % 9 == 0 else fixtures.REGIONS[place % 4],
            f"S{place % 120:04d}",
            f"{place % 41}",
        ]
        for place in range(_ROWS)
    ]
    table = _write(tmp_path, ["site", "subject_id", "score"], rows)
    per_column, splits, _asked = _counted_run(
        monkeypatch, tmp_path / "out", table, "--identifier", "subject_id"
    )
    # In the order first read: the identifier, once; the holey first
    # column, which the census reads and does not keep -- it keeps ONE
    # reading, the first it takes (`taxonomy._census_reading` says why)
    # -- so the description reads it again; and the last column, which
    # only the description reads.
    assert per_column == {0: 1, 1: 2, 2: 1}, per_column
    assert splits == 0


def _held(values: "list[str]", settings: taxonomy.Settings) -> taxonomy.HeldReading:
    return taxonomy.population_census(["only"], [values], [], settings)[2][0]


@pytest.mark.parametrize(
    "different",
    [
        {"forced_identifier": True},
        {"forced_code": True},
        {"forced_measurement": True},
        {"forced_decimal_comma": True},
        {"described_as_pair": True},
        {"kept_placeholder_days": ("1900-01-01",)},
        {"judged_candidates": ("-999",)},
        {"settings": "floor"},
        {"values": "copy"},
        {"n_rows": "other"},
    ],
)
def test_a_reading_under_any_other_argument_is_read_again(
    monkeypatch: pytest.MonkeyPatch, different: "dict[str, object]"
) -> None:
    """Every argument `_read_the_column` depends on is part of the match."""
    values = [f"{place % 23}" for place in range(_ROWS)]
    settings = taxonomy.Settings()
    held = _held(values, settings)
    calls = [0]
    # Counted from here: `_held` above is the census's own reading.
    reading_as_shipped = taxonomy._read_the_column

    def counted(*args: object, **named: object) -> object:
        calls[0] = calls[0] + 1
        return reading_as_shipped(*args, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "_read_the_column", counted)
    arguments: "dict[str, object]" = {
        "forced_identifier": False,
        "forced_code": False,
        "forced_measurement": False,
        "forced_decimal_comma": False,
        "described_as_pair": False,
        "kept_placeholder_days": (),
        "judged_candidates": (),
    }
    cells: "list[str]" = values
    rows = _ROWS
    here = settings
    for key in different:
        if key == "settings":
            here = dataclasses.replace(settings, small_cell_floor=settings.small_cell_floor + 1)
        elif key == "values":
            cells = list(values)
        elif key == "n_rows":
            cells = values + ["1"]
            rows = _ROWS + 1
        else:
            arguments[key] = different[key]
    taxonomy.profile_column("only", 1, cells, rows, here, handed_over=held, **arguments)  # type: ignore[arg-type]
    assert calls[0] == 1

    # ...and the same call with nothing different takes the reading over,
    # which is what makes the count above mean something.
    same = _held(values, settings)
    calls[0] = 0
    taxonomy.profile_column("only", 1, values, _ROWS, settings, handed_over=same)
    assert calls[0] == 0
    # The one field of the settings no reading consults does not matter.
    same = _held(values, settings)
    calls[0] = 0
    taxonomy.profile_column(
        "only",
        1,
        values,
        _ROWS,
        dataclasses.replace(settings, person_columns=("only",)),
        handed_over=same,
    )
    assert calls[0] == 0


def test_the_document_is_the_same_with_and_without_the_hand_over(
    tmp_path: pathlib.Path,
) -> None:
    """The hand-over saves work and changes nothing the description says.

    The whole command is compared byte for byte against the tree before
    the repair by the landing's own battery; this is the in-suite half,
    over a declared identifier that repeats and so is kept by the census.
    """
    rows = [
        [f"S{place % 60:03d}", fixtures.REGIONS[place % 4], f"{place % 37}"]
        for place in range(_ROWS)
    ]
    path = _write(tmp_path, ["subject_id", "site", "score"], rows)
    table = reading.read_table(f"{path}")
    settings = taxonomy.Settings()
    people, _count, held = taxonomy.population_census(
        table.column_names,
        table.columns,
        ["subject_id"],
        settings,
        taxonomy.Declarations(identifiers=("subject_id",)),
    )
    assert people == ("subject_id",)
    assert len(held) == 1 and held[0].values is table.columns[0]
    settings = dataclasses.replace(settings, person_columns=people)
    handed = profile.build_document(table, settings, ["subject_id"], readings=held)
    read_again = profile.build_document(table, settings, ["subject_id"])
    assert handed == read_again


def test_the_reading_described_is_the_reading_the_description_would_take(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Field for field, including the settings the reading carries.

    The census reads under settings whose `person_columns` is still
    empty; the description runs under the people the census found. The
    match sets that one field aside, so the kept reading's tally still
    carries the census's settings -- and the reading `profile_column`
    goes on to describe must be the one `_read_the_column` returns under
    the description's own settings, not a reading that differs from it
    in a field nothing consults TODAY.
    """
    rows = [
        [f"S{place % 60:03d}", fixtures.REGIONS[place % 4], f"{place % 37}"]
        for place in range(_ROWS)
    ]
    path = _write(tmp_path, ["subject_id", "site", "score"], rows)
    table = reading.read_table(f"{path}")
    census_settings = taxonomy.Settings()
    people, _count, held = taxonomy.population_census(
        table.column_names,
        table.columns,
        ["subject_id"],
        census_settings,
        taxonomy.Declarations(identifiers=("subject_id",)),
    )
    assert people == ("subject_id",) and len(held) == 1
    described_under = dataclasses.replace(census_settings, person_columns=people)
    assert held[0].settings != described_under
    fresh = taxonomy._read_the_column(
        table.columns[0], _ROWS, described_under, forced_identifier=True
    )

    # What `profile_column` describes reaches `_decide` as the reading's
    # tally; everything else of the reading is shared with the kept one.
    tallies: "list[object]" = []
    decide_as_shipped = taxonomy._decide

    def watched(cells: object, *args: object, **named: object) -> object:
        tallies.append(cells)
        return decide_as_shipped(cells, *args, **named)  # type: ignore[arg-type]

    reads = [0]
    reading_as_shipped = taxonomy._read_the_column

    def counted(*args: object, **named: object) -> object:
        reads[0] = reads[0] + 1
        return reading_as_shipped(*args, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "_decide", watched)
    monkeypatch.setattr(taxonomy, "_read_the_column", counted)
    taxonomy.profile_column(
        "subject_id",
        1,
        table.columns[0],
        _ROWS,
        described_under,
        forced_identifier=True,
        handed_over=held[0],
    )
    assert reads[0] == 0, "the kept reading was not taken over"
    assert len(tallies) == 1
    described = dataclasses.replace(held[0].reading, cells=tallies[0])
    assert described == fresh, (
        "the handed-over reading is not the reading `_read_the_column` "
        "returns under the description's settings"
    )


def _split_table(
    tmp_path: pathlib.Path,
) -> "tuple[reading.Table, dict[str, object]]":
    rows = [
        [
            fixtures.REGIONS[place % 4],
            fixtures.LABELS[place % 5],
            f"{place % 37}",
            f"S{place % 120:04d}",
        ]
        for place in range(_ROWS)
    ]
    path = _write(tmp_path, ["site", "grade", "score", "subject"], rows)
    table = reading.read_table(f"{path}")
    document = profile.build_document(table, taxonomy.Settings(), [])
    return table, document


def _splits_in_person_questions(
    monkeypatch: pytest.MonkeyPatch,
    document: "dict[str, object]",
    columns: "list[list[str]]",
    settings: taxonomy.Settings,
    asked: "list[asking.Question]",
    split: "asking.SplitColumns",
) -> int:
    splits = [0]
    split_as_shipped = taxonomy.split_missing

    def counted(*args: object, **named: object) -> object:
        splits[0] = splits[0] + 1
        return split_as_shipped(*args, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "split_missing", counted)
    try:
        asking.person_questions(document, columns, settings, [], asked, split)
    finally:
        monkeypatch.setattr(taxonomy, "split_missing", split_as_shipped)
    return splits[0]


def test_a_split_is_taken_only_from_the_same_column_under_the_same_settings(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The person question's side of the hand-over, pinned both ways."""
    table, document = _split_table(tmp_path)
    columns = table.columns
    settings = taxonomy.Settings()
    asked, split = asking.questions_and_splits_for(document, columns, settings, [])
    unanswered = len(columns) - len(asked)
    assert unanswered >= 2 and sorted(split.present) == list(range(len(columns)))

    # The same columns under the same settings: nothing is split again,
    # which is what makes the counts below mean something.
    assert _splits_in_person_questions(
        monkeypatch, document, columns, settings, asked, split
    ) == 0

    # Other settings: every column still to be asked about is split anew.
    other = dataclasses.replace(settings, declared_missing_values=("x",))
    assert _splits_in_person_questions(
        monkeypatch, document, columns, other, asked, split
    ) == unanswered

    # A column that is not the object the split was taken from -- the
    # same cells in another list -- is split anew, and only that column.
    spoken = [question.name for question in asked]
    place = next(
        spot
        for spot, name in enumerate(table.column_names)
        if name not in spoken
    )
    elsewhere = list(columns)
    elsewhere[place] = list(columns[place])
    assert _splits_in_person_questions(
        monkeypatch, document, elsewhere, settings, asked, split
    ) == 1
