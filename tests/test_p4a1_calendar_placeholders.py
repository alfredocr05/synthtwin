"""The calendar placeholders, judged like the stand-in numbers.

Plan amendment A-P4-1 item 3. A column whose open-ended rows are filled
with `9999-12-31` published that day as its exact last value, dragged
its whole ladder toward it, and seeded the twin with decades the source
never held -- the one audited shape where the ratified plan published
wrong numbers with no warning at all. It is the calendar's `-999`, one
space over.

WHAT IS PINNED HERE, and each of it is a rule the amendment states:

- exactly two candidates, and their identity is the WRITTEN calendar
  day: a cell matches when its own written fields, under the column's
  own format, denote that day -- no shared-clock normalization and no
  offset arithmetic;
- the standing outlier-and-share rule transposed to day ordinals,
  reusing the two recorded sentinel settings and adding none;
- TWO gates on the pass, and both must hold: rules 0 through 4 declined
  the un-removed column, AND the non-candidate remainder clears the
  datetime rule's line by itself -- otherwise no cell is judged, no
  cell is removed, and the column lands exactly where today's rules put
  it;
- so a constant column of one placeholder stays constant, a two-valued
  column whose one value is a placeholder stays binary, and a column
  that was never a column of dates cannot be turned into one;
- the absence-class map gains `(date-sentinel)`, present on every
  column block like the other five;
- verdicts carry the candidate as its canonical ISO day, ordered after
  every numeric candidate and among themselves as text;
- and `--keep-value` wins exactly as it does for a number.
"""

import pathlib
import tempfile

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

FAR = "9999-12-31"
NEAR = "1900-01-01"


def _described(
    values: "list[str]", settings: "taxonomy.Settings | None" = None
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One single-column table, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "when.csv", fixtures.single_column_table("when", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), settings or taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "when.json", document)
    return document, contract.load_profile(f"{written}"), folder


def _dates(count: int) -> "list[str]":
    """Ordinary ISO dates over one year."""
    return [
        f"2024-{1 + place % 12:02d}-{1 + place % 28:02d}"
        for place in range(count)
    ]


# -- what the pass buys -----------------------------------------------


def test_a_placeholder_stops_being_the_column_s_last_value() -> None:
    """THE DEFECT THE AMENDMENT IS FOR, and it is a silent one.

    Two hundred and twenty-eight dates in 2024 and twelve rows filled
    with the far placeholder. Before this pass the column published
    `latest: 9999-12-31`, dragged every rung of its ladder toward it,
    and the twin held dates spread over eight thousand years -- so code
    computing a span, a maximum date or a days-to-event ran one way on
    the real table and another on the twin, in the same direction, with
    nothing saying so.
    """
    document, described, _folder = _described(_dates(228) + [FAR] * 12)
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["n_present"] == 228
    assert block["n_missing"] == 12
    assert block["latest"] == "2024-12-28"
    assert FAR not in f"{block['date_percentiles']}"
    assert block["missing_by_class"]["(date-sentinel)"] == 12
    assert described.columns[0].missing_by_class.date_sentinel == 12


def test_the_verdict_says_what_was_decided_and_why() -> None:
    """Either way, and in the candidate's own canonical spelling."""
    document, _loaded, _folder = _described(_dates(228) + [FAR] * 12)
    verdicts = document["columns"][0]["sentinel_verdicts"]
    assert len(verdicts) == 1
    assert verdicts[0]["candidate"] == FAR
    assert verdicts[0]["verdict"] == "read_as_missing"
    assert verdicts[0]["reason"] == "outlier_and_frequent"
    assert verdicts[0]["n_occurrences"] == 12


def test_a_twin_of_such_a_column_holds_no_placeholder() -> None:
    """The whole way through."""
    _document, described, folder = _described(_dates(228) + [FAR] * 12)
    twin = generation.generate(described, 5)
    cells = [cell for cell in twin.columns[0] if cell]
    for cell in cells:
        assert not cell.startswith("9999"), cell
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == []


# -- the identity: the WRITTEN day ------------------------------------


def test_the_candidate_is_the_written_day() -> None:
    """No shared-clock normalization and no offset arithmetic.

    The placeholder is a writing convention and the person typed that
    day, so a cell whose own fields denote it matches whatever time or
    offset it carries beside them.
    """
    assert parsing.placeholder_day_of(FAR, "iso-date") == FAR
    assert parsing.placeholder_day_of(f"{FAR} 23:59:59", "iso-datetime") == FAR
    assert parsing.placeholder_day_of("12/31/9999", "month-first-date") == FAR
    assert parsing.placeholder_day_of("31/12/9999", "day-first-date") == FAR
    assert parsing.placeholder_day_of(NEAR, "iso-date") == NEAR
    assert parsing.placeholder_day_of("9999-12-30", "iso-date") is None
    assert parsing.placeholder_day_of("2024-01-01", "iso-date") is None


def test_there_are_exactly_two_candidates() -> None:
    """A closed list, like the three stand-in numbers."""
    assert parsing.calendar_placeholders() == (NEAR, FAR)


# -- the two gates ----------------------------------------------------


def test_a_constant_column_of_the_placeholder_keeps_its_claim() -> None:
    """Rules 0 through 4 declined the UN-REMOVED column, and they did not."""
    document, _loaded, _folder = _described([FAR] * 240)
    assert document["columns"][0]["role"] == "constant"
    assert document["columns"][0]["n_missing"] == 0
    assert document["columns"][0]["sentinel_verdicts"] == []


def test_a_two_valued_column_stays_binary() -> None:
    """The second fixture the amendment names by hand."""
    document, _loaded, _folder = _described(["2024-01-01"] * 120 + [FAR] * 120)
    assert document["columns"][0]["role"] == "binary"
    assert document["columns"][0]["n_missing"] == 0


def test_a_remainder_that_misses_the_line_is_left_alone() -> None:
    """The third: no cell is judged and no cell is removed.

    A column of free text with a few placeholder cells is not a column
    of dates without them, so this pass has no business in it -- and a
    pass that removed cells anyway could turn a column into a column of
    dates by taking things out of it.
    """
    values = [f"note {place}" for place in range(228)] + [FAR] * 12
    document, _loaded, _folder = _described(values)
    assert document["columns"][0]["role"] != "datetime"
    assert document["columns"][0]["n_missing"] == 0
    assert document["columns"][0]["sentinel_verdicts"] == []


def test_a_column_of_dates_with_no_placeholder_is_untouched() -> None:
    """Nothing about an ordinary column of dates moves."""
    document, _loaded, _folder = _described(_dates(240))
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["n_missing"] == 0
    assert block["sentinel_verdicts"] == []
    assert block["missing_by_class"]["(date-sentinel)"] == 0


# -- the judgement itself ---------------------------------------------


def test_a_rare_placeholder_is_kept_and_says_so() -> None:
    """An outlier that too few rows share is data, with the reason."""
    document, _loaded, _folder = _described(_dates(228) + [FAR] * 12, taxonomy.Settings(
        sentinel_minimum_share=0.2
    ))
    block = document["columns"][0]
    assert block["n_missing"] == 0
    verdicts = block["sentinel_verdicts"]
    assert len(verdicts) == 1
    assert verdicts[0]["verdict"] == "kept_as_a_number"
    assert verdicts[0]["reason"] == "too_rare"


def test_a_declared_placeholder_is_data_and_says_so() -> None:
    """`--keep-value` wins exactly as it does for a number."""
    document, _loaded, _folder = _described(
        _dates(228) + [FAR] * 12, taxonomy.Settings(kept_values=(FAR,))
    )
    block = document["columns"][0]
    assert block["n_missing"] == 0
    assert block["latest"] == FAR
    verdicts = block["sentinel_verdicts"]
    assert len(verdicts) == 1
    assert verdicts[0]["reason"] == "kept_by_you"


def test_a_placeholder_below_the_floor_is_counted_and_not_named() -> None:
    """The publication rule the numeric half carries, over a day."""
    document, _loaded, _folder = _described(_dates(235) + [FAR] * 5)
    block = document["columns"][0]
    assert block["sentinel_verdicts"] == []
    assert block["n_sentinel_candidates_unpublished"] == 1


def test_both_placeholders_are_judged_against_the_same_others() -> None:
    """The reference population excludes EVERY candidate.

    A column holding both placeholders must not have either made to
    look ordinary by the other's presence -- the defect the numeric
    rule's first property closes.
    """
    document, _loaded, _folder = _described(
        _dates(216) + [NEAR] * 12 + [FAR] * 12
    )
    block = document["columns"][0]
    assert block["n_missing"] == 24
    named = [entry["candidate"] for entry in block["sentinel_verdicts"]]
    assert named == [NEAR, FAR]
    assert block["earliest"] == "2024-01-01"
    assert block["latest"] == "2024-12-28"


# -- the sixth class, on every block ----------------------------------


def test_every_column_block_carries_the_sixth_class() -> None:
    """Present on every column, like the other five."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "table.csv", fixtures.every_role_table()
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), taxonomy.Settings(), ["record_code"]
    )
    for block in document["columns"]:
        assert "(date-sentinel)" in block["missing_by_class"], block["name"]
    assert parsing.MISSING_CLASSES == (
        "(blank)",
        "(date-sentinel)",
        "(declared-missing)",
        "(numeric-sentinel)",
        "(text-code)",
        "(withheld)",
    )
