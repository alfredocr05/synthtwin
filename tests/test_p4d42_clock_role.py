"""The time-of-day role, end to end and at every edge it names.

Phase 4's second new column type (plan P4-D4.2, with amendment A-P4-20
for its distinctness). A column of `09:30` or `14:05:00` used to match
no rule and become free text, which publishes nothing at all.

WHAT IS PINNED HERE, and each of it is a rule the decision states
rather than a property somebody noticed:

- the reader accepts exactly two shapes and REFUSES four, each refusal
  for its own reason;
- one form must clear the parse line, applied as a COUNT; where both
  clear it the finer wins; below the line the column declines;
- every cell no clock reading accepted is counted and nothing of it is
  published;
- the ladder is SELECTION, so every rung is a time some row wore, and
  its two ends ARE the endpoints;
- the twin pins those two ends and interpolates between them in the
  form's own unit, so no generated cell is truncated or widened;
- and the report says a rung's distance in minutes or seconds, never a
  clock time read out of the file it is checking.
"""

import pathlib
import tempfile

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    generation,
    parsing,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)


def _described(
    values: "list[str]",
    name: str = "seen_at",
    settings: "taxonomy.Settings | None" = None,
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One single-column table, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, f"{name}.csv", fixtures.single_column_table(name, values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), settings or taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, f"{name}.json", document)
    return document, contract.load_profile(f"{written}"), table


def _minutes(count: int, start: int = 7 * 60) -> "list[str]":
    """A column of clock times at one-minute steps, in `hh-mm`."""
    return [
        parsing.clock_spelling(start + index, parsing.CLOCK_HH_MM)
        for index in range(count)
    ]


# -- the reader: two shapes accepted, four refused --------------------


def test_the_reader_accepts_exactly_two_shapes() -> None:
    """And every value of both spaces round-trips through it.

    Not a sample: all 1,440 minutes of the day and all 86,400 seconds.
    The whole ordinal argument -- that every interpolated value has
    exactly one spelling in the column's form, so no generated cell is
    ever truncated or widened -- rests on this being total.
    """
    for form in parsing.CLOCK_FORMS:
        for ordinal in range(parsing.CLOCK_CAPACITY[form]):
            text = parsing.clock_spelling(ordinal, form)
            assert parsing.clock_form(text) == form, (form, ordinal)
            assert parsing.clock_ordinal(text, form) == ordinal, text


@pytest.mark.parametrize(
    "cell, why",
    [
        ("12:34:56.7", "a fractional part: the role publishes no key for it"),
        ("23:59:60", "a leap second: the ordinal space has no point for it"),
        ("9:30", "a single-digit hour: both forms are fixed width"),
        ("24:00", "an hour past the day"),
        ("12:60", "a minute past the hour"),
        ("12:34:5", "a short seconds field"),
        ("2024-03-17 09:30", "a date in front of it"),
        ("09:30+02:00", "an offset behind it"),
        ("", "nothing at all"),
    ],
)
def test_the_reader_refuses_what_the_decision_names(cell: str, why: str) -> None:
    """Each refusal is a rule, and the reason is written beside it."""
    assert parsing.clock_form(cell) is None, why


def test_a_refused_cell_is_counted_rather_than_re_read() -> None:
    """Inside the line's slack, an unreadable cell is an unparsed one.

    All four named refusals land here, and so does a cell of the OTHER
    form: none of them is merged into the winning reading, and the
    column still holds the role.
    """
    for tail in ("09:30:00", "09:30:00.5", "23:59:60", "9:30"):
        document, _loaded, _table = _described(_minutes(99) + [tail])
        column = document["columns"][0]
        assert column["role"] == "time_of_day", tail
        assert column["clock_form"] == parsing.CLOCK_HH_MM, tail
        assert column["n_unparsed"] == 1, tail


# -- the rule: the line, the tie, and the decline ---------------------


def test_below_the_line_the_column_declines() -> None:
    """Ninety of a hundred is not enough, and the column falls through."""
    values = _minutes(90) + [f"note {index}" for index in range(10)]
    document, _loaded, _table = _described(values, name="note")
    assert document["columns"][0]["role"] != "time_of_day"


def test_where_both_forms_clear_the_line_the_finer_one_wins() -> None:
    """Possible only at a lowered rate, because no cell wears both.

    The two shapes have different lengths, so both clearing the line
    needs twice the line to fit inside the column.
    """
    fine = [
        parsing.clock_spelling(8 * 3600 + index, parsing.CLOCK_HH_MM_SS)
        for index in range(50)
    ]
    values = fine + _minutes(50, start=10 * 60)
    document, _loaded, _table = _described(
        values, settings=taxonomy.Settings(minimum_parse_rate=0.5)
    )
    column = document["columns"][0]
    assert column["role"] == "time_of_day"
    assert column["clock_form"] == parsing.CLOCK_HH_MM_SS
    assert column["n_unparsed"] == 50


def test_the_rule_reads_no_floor_at_detection() -> None:
    """A short column of clock times is still a column of clock times.

    Two rules of this phase consult `small_cell_floor` at detection,
    because publishing a floor-clearing SPELLING is what makes them the
    role they are. This role publishes no spelling of the column's own
    text, so a floor copied from them would withhold the role on short
    columns for no stated reason.
    """
    document, _loaded, _table = _described(_minutes(4))
    assert document["columns"][0]["role"] == "time_of_day"


# -- what it publishes ------------------------------------------------


def test_the_block_carries_five_keys_and_no_sixth() -> None:
    """The five the contract names, and the ladder is selection."""
    document, loaded, _table = _described(_minutes(60))
    column = document["columns"][0]
    for key in contract.CLOCK_KEYS:
        assert key in column, key
    for absent in ("format", "resolution", "utc_offsets", "percentiles"):
        assert absent not in column, absent
    ladder = column["clock_percentiles"]
    assert sorted(ladder) == sorted(taxonomy.LADDER_NAMES)
    # SELECTION: every rung is a time some row wore.
    for rung in ladder.values():
        assert rung in _minutes(60), rung
    assert ladder["min"] == column["earliest"]
    assert ladder["max"] == column["latest"]
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.ClockFacts)


# -- the five invariants, each with its red case ----------------------


def _forged(edit) -> "tuple[dict, pathlib.Path]":
    """One conforming clock document with one thing changed."""
    import copy

    document, _loaded, _table = _described(_minutes(99) + ["not a time"])
    forged = copy.deepcopy(document)
    edit(forged["columns"][0])
    folder = pathlib.Path(tempfile.mkdtemp())
    return forged, fixtures.write_profile(folder, "forged.json", forged)


@pytest.mark.parametrize(
    "rule, edit",
    [
        (
            "T1",
            lambda column: column["clock_percentiles"].__setitem__(
                "p50", "07:49:00"
            ),
        ),
        ("T2", lambda column: column.__setitem__("latest", "09:15")),
        (
            "T2",
            lambda column: column["clock_percentiles"].__setitem__(
                "max", "09:15"
            ),
        ),
        (
            "T3",
            lambda column: column["clock_percentiles"].__setitem__(
                "p50", "07:01"
            ),
        ),
        ("T4", lambda column: column.__setitem__("n_unparsed", 100)),
        ("T5", lambda column: column.__setitem__("n_unparsed", 40)),
    ],
)
def test_each_clock_invariant_refuses_a_document_that_breaks_it(
    rule: str, edit
) -> None:
    """Five rules, each raised in its own words for a person to read."""
    _forged_document, written = _forged(edit)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(f"{written}")
    assert contract.INVARIANTS[rule] in f"{raised.value}", rule


# -- the twin ---------------------------------------------------------


def test_the_twin_pins_both_ends_and_stays_inside_them() -> None:
    """The construction's own promise, checked on the written cells."""
    document, loaded, _table = _described(
        _minutes(238) + ["not recorded", "missing entry"]
    )
    column = document["columns"][0]
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.ClockFacts)
    for seed in range(5):
        twin = generation.generate(loaded, seed)
        cells = [cell for cell in twin.columns[0] if cell]
        assert len(cells) == column["n_present"], seed
        times = [
            cell for cell in cells
            if parsing.clock_form(cell) == facts.clock_form
        ]
        assert len(times) == column["n_present"] - facts.n_unparsed, seed
        assert min(times) == facts.earliest, seed
        assert max(times) == facts.latest, seed


def test_a_stand_in_never_reads_as_a_clock_time_in_either_form() -> None:
    """Otherwise it would quietly move the count of what parsed."""
    _document, loaded, _table = _described(
        _minutes(238) + ["not recorded", "missing entry"]
    )
    twin = generation.generate(loaded, 3)
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.ClockFacts)
    stand_ins = [
        cell
        for cell in twin.columns[0]
        if cell and parsing.clock_form(cell) != facts.clock_form
    ]
    assert len(stand_ins) == facts.n_unparsed
    for cell in stand_ins:
        assert parsing.clock_form(cell) is None, cell


def test_a_twin_of_a_clock_column_misses_nothing() -> None:
    """Profile, generate, validate -- on both forms and several seeds."""
    folder = pathlib.Path(tempfile.mkdtemp())
    coarse = [
        parsing.clock_spelling(
            7 * 60 + (index % 120), parsing.CLOCK_HH_MM
        )
        for index in range(238)
    ] + ["not recorded", "missing entry"]
    fine = [
        parsing.clock_spelling(
            8 * 3600 + (index % 900) * 4, parsing.CLOCK_HH_MM_SS
        )
        for index in range(240)
    ]
    for label, values in (("coarse", coarse), ("fine", fine)):
        _document, loaded, _table = _described(values)
        for seed in range(4):
            twin = generation.generate(loaded, seed)
            target = fixtures.write(
                folder, f"{label}-{seed}.csv", rendering.twin_csv(twin)
            )
            outcome = validation.measure(loaded, f"{target}")
            missed = [
                check.subcheck
                for check in outcome.checks
                if check.verdict == validation.MISSED
            ]
            assert missed == [], (label, seed, missed)


# -- what the report may say ------------------------------------------


def test_no_clock_time_of_the_measured_file_reaches_the_report() -> None:
    """V5.4: the endpoints and the rungs are text read out of the file.

    A description of a morning column checked against an afternoon one
    must print no time the afternoon column holds -- the comparison is
    made in full and only the verdict and a DISTANCE are shown.
    """
    _document, loaded, _table = _described(_minutes(120))
    folder = pathlib.Path(tempfile.mkdtemp())
    other = fixtures.write(
        folder,
        "other.csv",
        fixtures.single_column_table(
            "seen_at", _minutes(120, start=15 * 60 + 7)
        ),
    )
    outcome = validation.measure(loaded, f"{other}")
    report = parsing.visible_lines(quality.quality_report(loaded, outcome))
    for ordinal in range(15 * 60 + 7, 15 * 60 + 127):
        assert (
            parsing.clock_spelling(ordinal, parsing.CLOCK_HH_MM)
            not in report
        ), ordinal


def test_a_rung_is_said_as_a_distance_a_person_can_read() -> None:
    """Minutes or seconds, never a raw ordinal and never the file's text."""
    _document, loaded, _table = _described(
        [
            parsing.clock_spelling(
                7 * 60 + (index % 120), parsing.CLOCK_HH_MM
            )
            for index in range(240)
        ]
    )
    twin = generation.generate(loaded, 1)
    folder = pathlib.Path(tempfile.mkdtemp())
    target = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(loaded, f"{target}")
    rungs = [
        check
        for check in outcome.checks
        if check.subcheck.startswith("clock-ladder.p")
    ]
    assert len(rungs) == 9
    for check in rungs:
        assert check.achieved == "that same time" or (
            "minute(s)" in check.achieved
        ), check.achieved
        assert ".0" not in check.achieved, check.achieved

# -- what codex round 1 found ------------------------------------------


def test_an_all_different_column_keeps_every_value_apart() -> None:
    """A-P4-20 as narrowed: the exact bar stands where the values did.

    A hundred different minutes published as a hundred different values
    must come back as a hundred. The interpolation collides where the
    ladder is tighter than the ranks are numerous, and the repair is
    the one the source column itself used: take the next minute. A
    closed finite space has a place for each of them, which the
    capacity refusal below is what guarantees.
    """
    values = _minutes(100)
    _document, loaded, _table = _described(values)
    for seed in range(12):
        cells = [cell for cell in generation.generate(loaded, seed).columns[0] if cell]
        assert len(set(cells)) == 100, seed


def test_a_column_asking_for_more_times_than_a_day_holds_is_refused() -> None:
    """The one refusal this role adds, decided before any cell exists.

    A day holds 1,440 minutes. A description saying a column holds
    1,441 different ones describes no table, and every arrangement of
    cells fails -- so the honest answer is to say so before writing
    anything, and to say the description itself is not damaged.
    """
    import copy

    document, _loaded, _table = _described(
        [
            parsing.clock_spelling(index, parsing.CLOCK_HH_MM)
            for index in range(1440)
        ]
    )
    forged = copy.deepcopy(document)
    forged["n_rows"] = 1441
    column = forged["columns"][0]
    column["n_present"] = 1441
    column["n_distinct"] = 1441
    column["n_distinct_folded"] = 1441
    column["n_not_numeric"] = 1441
    folder = pathlib.Path(tempfile.mkdtemp())
    written = fixtures.write_profile(folder, "over.json", forged)
    loaded = contract.load_profile(f"{written}")
    with pytest.raises(errors.ProfileError) as raised:
        generation.generate(loaded, 0)
    said = f"{raised.value}"
    assert "1441 different times of day" in said
    assert "only 1440 of them in a day" in said
    assert "description is not damaged" in said


def test_a_cell_needing_a_tidy_is_not_a_clock_time() -> None:
    """The fifth refusal: this reader takes the cell as the file wrote it.

    What this role publishes ARE the cells -- the two endpoints and
    eleven rungs are values some row wore, character for character. A
    reader that trimmed would let a column of ` 09:30 ` publish
    `09:30`, a string no row of that table holds, and the ladder would
    stop being a selection of real cells.
    """
    for cell in (" 09:30 ", "09:30 ", " 09:30", "\t09:30", "09:30\u00a0"):
        assert parsing.clock_form(cell) is None, repr(cell)


def test_a_file_in_the_other_form_is_read_rather_than_silenced() -> None:
    """V5.3: only the disclosure gate may withhold, and this is not it.

    A file whose cells wear the other shape publishes a ladder in that
    shape. Reading it under the DESCRIPTION's form found nothing and
    every rung went silent -- on a file whose own description publishes
    exactly the measurement being asked for. Both sides are read in
    their own form now and compared in seconds of day, so the same
    moments HOLD and the form itself is what misses.
    """
    coarse = _minutes(100, start=9 * 60)
    fine = [
        parsing.clock_spelling(9 * 3600 + index * 60, parsing.CLOCK_HH_MM_SS)
        for index in range(100)
    ]
    _document, loaded, _table = _described(coarse)
    folder = pathlib.Path(tempfile.mkdtemp())
    other = fixtures.write(
        folder, "other.csv", fixtures.single_column_table("seen_at", fine)
    )
    outcome = validation.measure(loaded, f"{other}")
    spoken = {check.subcheck: check.verdict for check in outcome.checks}
    assert spoken["form.clock_form"] == validation.MISSED
    for name in ("p01", "p25", "p50", "p75", "p99"):
        assert spoken[f"clock-ladder.{name}"] == validation.HELD, name
