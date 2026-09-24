"""Both ends of a column of dates are exact, and stay exact in the text.

Review item P2-C2-F5. Closing the temporal round-trip item of code review
round 1, a repair widened the seconds field of the contract's canonical
form to 60 -- correctly, because the shipped date reader accepts the last
second of a leap minute and the producer can therefore publish one -- and
then, rather than write that instant back, it moved BOTH normative
documents: the contract's disposition matrix grew a second corner making
the end REPORT-ONLY, and the method's G7.5 named a leap second as a
permitted loss. The ratified plan makes both ends exact in owner decision
5's representation and names no such corner, and no owner decision took
that back. A defect was closed by lowering the bar it failed.

The bar is restored, and an exact representation was available the whole
time: an end is written from the published instant's OWN fields instead
of through the whole-second space the ranks between the ends travel in.

AND THEN IT WAS LOWERED AGAIN, IN THE PLACE NOBODY WAS LOOKING (review
item P2-C3-F2). The repair above put the disposition back in the matrix
row and in the method's G7.5 construction -- where the reviewer had
looked -- and wrote the exception into the paragraph AFTER it: a
description publishing an end no cell of its own recorded shape can show
would have that end met as far as it could be, recounted and named. The
method said the same and the generator did it, declining to write the
published seconds field whenever the column was on the shared clock. The
strict loader accepted such a description, so the matrix said "no corner,
no exception" about documents this repository itself let through with the
end changed. Both pairs are now REFUSED where they are decided, by the
contract's D10, and D11 ties the ladder's ends to the column's own two
ends -- which also closed a hole nothing had named, a ladder end below
`earliest` giving a twin holding instants before its own published end
with nothing said about it.

AND THEN A THIRD TIME, IN THE GUARD ITSELF (review item P2-C4-F1). The
repair above refused those two pairs and left a third standing: a
shared-clock end whose own endpoint offset carries its cell outside the
years 0001 to 9999. The method called that the calendar's own end rather
than an exception, the generator wrote the cell and named the end, an
affirmative test here REQUIRED that outcome, and the wording inventory
below listed the passage as a decided one -- so the guard was green about
the sentence it existed to catch. The loader holds the end, its offset
and the clock, so D10 now settles that pair too, in both directions, and
this file permits ZERO passages that speak of an end met with something
other than what was published. The general form of the check -- every
published fact, all three documents, an authorization that only the
ratified plan can grant -- is `test_p2c4f1_disposition_registry.py`,
which exists because this file's subject was lowered four times.

WHY THIS FILE CHECKS THE TEXT AND NOT ONLY THE BEHAVIOUR. A behaviour
test alone cannot fail when a future repair writes a softer sentence into
a specification and then makes the code match it -- which is exactly the
sequence that happened here, three times. So each rule below is checked
twice: as the shipped behaviour, and as the WORDING of the two normative
documents.

WHY THE WORDING CHECK READS EVERY PASSAGE. The guard this file carried
before read one matrix cell and counted one numbered corner, and it was
green on the day the exception was written four paragraphs further down.
The wording check is now an inventory: every passage of either document
that speaks of an end being met with something other than what was
published has to be a passage this file decides on, by name and with a
reason. One added anywhere, however phrased, belongs to nobody and turns
the file red -- and `test_an_exception_added_anywhere_is_caught` proves
that by adding several, in both documents, at three places each.

WHY THE BEHAVIOUR CHECK WALKS THE WHOLE SHAPE SPACE. Prose can be right
while the code is not, so the other half is
`test_every_description_the_loader_accepts_gives_both_ends_back`: every
shape of temporal column, every end a reader can publish, and exactly two
outcomes -- refused, or described again with the same two instants.
"""

import copy
import dataclasses
import json
import pathlib
import typing

import pytest

import dispositions
import fixtures
from synthtwin import (
    parsing,
    contract,
    errors,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
CONTRACT = REPO_ROOT / "docs" / "spec" / "profile-contract-v4.md"
METHOD = REPO_ROOT / "docs" / "spec" / "generation-method-v1.md"
PLAN = REPO_ROOT / "docs" / "plans" / "phase-2-generator.md"

# The obligation, in the ratified plan's own words (P2-D6, the datetime
# paragraph). Both specifications carry it character for character, so
# one document cannot drift from the other or from the plan.
#
# THE FACT IT IS ABOUT MOVED IN STAGE 3 AND THE OBLIGATION MOVED WITH IT
# (plan P4-D328). `earliest` and `latest` are published nowhere now: the
# published moments of a column of dates are its two tail boundaries, so
# the plan states the same disposition over them and both specifications
# carry the same words. What this file exists to refuse -- a published
# moment met by something other than what was published -- is refused of
# whatever fact carries the moment, so the phrase is re-derived from the
# rule rather than deleted with the fact it used to name.
PLAN_WORDS = (
    "both tail boundaries exact-observable in the representation owner "
    "decision 5 fixes"
)
SHARED_WORDS = "exact-observable in the representation owner decision 5 fixes"

# One column of dates and times at the second, with no offset, which is
# the shape the review item's scenario uses and the shape a real table
# most often has.
AT_THE_SECOND = [
    "2024-01-05 09:15:07",
    "2024-02-19 13:40:44",
    "2024-07-30 21:05:19",
    "2024-11-02 04:55:02",
]

# The same column written in two offsets, so the description publishes
# its instants on the shared clock instead of the wall clock.
IN_TWO_OFFSETS = [
    "2024-01-05 09:15:07+02:00",
    "2024-02-19 13:40:44+02:00",
    "2024-07-30 21:05:19-05:00",
    "2024-11-02 04:55:02-05:00",
]

Document = dict[str, typing.Any]


def _text(path: pathlib.Path) -> str:
    """One document as lower-case text with its line wrapping removed."""
    return " ".join(path.read_text(encoding="utf-8").lower().split())


def _row(path: pathlib.Path, opening: str) -> str:
    """The disposition cell of the one row whose field cell is ``opening``.

    A matrix row is one line, so this reads the line rather than the
    unwrapped text: what is checked is the cell that carries the
    disposition, not a phrase that happens to sit somewhere near it.
    """
    rows = [
        line.lower()
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.startswith(f"| {opening}")
    ]
    assert len(rows) == 1, f"{opening}: {len(rows)} rows"
    cells = rows[0].split("|")
    assert len(cells) >= 4, rows[0]
    return " ".join(cells[2].split())


def _document(folder: pathlib.Path, values: "list[str]") -> Document:
    """The producer's own description of a one-column table of dates."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("when", values)
    )
    built = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), []
    )
    return typing.cast(Document, json.loads(json.dumps(built)))


def _loaded(
    folder: pathlib.Path, document: Document, name: str
) -> contract.Profile:
    """Load a description from a file of its own canonical bytes."""
    target = fixtures.write_profile(folder, name, document)
    return contract.load_profile(str(target))


def _rows(values: "list[str]", copies: int) -> "list[str]":
    """Enough DIFFERENT values of one shape for both tails to exist.

    STAGE 3 (plan P4-D328). These shapes were four values repeated ten
    times each, which publishes no tail at all at a floor of eleven: ties
    at both ends leave no value between the two boundaries (contract
    DT2), so the boundary this file is about would not exist. Each row
    keeps its shape's own resolution, precision and clock and takes a day
    of its own, which is what a tail needs.
    """
    made: "list[str]" = []
    for index in range(copies):
        value = values[index % len(values)]
        if value[4:5] == "-" and value[5:6] == "Q":
            made += [f"{1990 + index // 4:04d}-Q{1 + index % 4}"]
            continue
        month = f"{1 + index // 28:02d}"
        day = f"{1 + index % 28:02d}"
        made += [f"{value[0:5]}{month}-{day}{value[10:]}"]
    return made


def _named(twin: generation.Twin) -> "dict[str, generation.Deviation]":
    """Every fact of the one column the run could not meet, by name."""
    return {
        deviation.fact: deviation
        for deviation in twin.deviations
        if deviation.column == "when"
    }


# -- the behaviour: the end a real reader can hand us ------------------


def test_a_published_leap_second_boundary_is_written_back_unchanged(
    tmp_path: pathlib.Path,
) -> None:
    """The review item's own scenario, on the value stage 3 publishes.

    Forty rows, a genuine description, a TAIL BOUNDARY whose seconds
    field is 60, seed 3. The item's twin wrote the following minute and
    named the miss; a boundary filter written against that twin admitted
    a row the real table's own boundary excludes. No end is published
    since plan P4-D328, and what carries the same obligation is the
    boundary: an exact value of a real cell, written from its own
    published fields (G7.5) rather than through the whole-second space
    the ranks around it travel in.
    """
    folder = tmp_path / "held"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(AT_THE_SECOND, 40))
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["datetimes_read_at"] == "local"
    assert block["time_precision"] == "second"

    boundary = block["high_tail"]["boundary"]
    leap = f"{boundary[0:17]}60"
    block["high_tail"]["boundary"] = leap
    for name in taxonomy.LADDER_NAMES:
        if block["date_percentiles"][name] == boundary:
            block["date_percentiles"][name] = leap
    twin = generation.generate(_loaded(folder, document, "held.json"), 3)

    assert "high_tail.rows" not in _named(twin)
    written = [cell for cell in twin.columns[0] if cell != ""]
    # The source wrote its stamps with a space, and since plan P4-D39 a
    # pinned rank keeps the source's own mark.
    assert leap in written


def test_every_other_end_keeps_the_bytes_it_already_had(
    tmp_path: pathlib.Path,
) -> None:
    """Writing an end from its own fields moved no ordinary cell.

    The two routes agree on every instant the whole-second space has a
    place for, which is what makes the repair safe for the frozen
    vectors and for every description a producer has ever written.
    """
    for name, values in [
        ("plain", AT_THE_SECOND),
        ("offsets", IN_TWO_OFFSETS),
    ]:
        folder = tmp_path / name
        folder.mkdir(parents=True, exist_ok=True)
        document = _document(folder, _rows(values, 40))
        facts = _loaded(folder, document, f"{name}.json").columns[0].facts
        assert isinstance(facts, contract.DatetimeFacts)
        carried = [
            key
            for key in sorted(facts.utc_offsets)
            if generation._is_real_offset(key)
        ]
        boundaries = [
            tail.boundary
            for tail in (facts.low_tail, facts.high_tail)
            if tail is not None
        ]
        assert boundaries
        for published in boundaries:
            for offset in carried or [""]:
                moved = generation._ordinal_of(published, "datetime")
                if facts.datetimes_read_at == "utc":
                    moved = moved + generation._offset_seconds(offset)
                for mark in ("T", " ", "t"):
                    assert generation._endpoint_cell(
                        facts, published, offset, mark
                    ) == generation._cell_of_ordinal(
                        moved,
                        facts.resolution,
                        facts.time_precision,
                        facts.subsecond_digits,
                        mark,
                    ), (name, published, offset, mark)


def test_the_end_no_cell_of_this_shape_can_show_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The description that made the exception arguable is not loadable.

    A sixtieth second published while the description says its instants
    are written on the shared clock reads back as the following minute
    whatever cell carries it. The previous repair accepted that
    description, wrote the following minute, and named the end in the
    report -- an exception standing beside a matrix row that says there
    is none, on a document this repository's own loader let through
    (review item P2-C3-F2). D10 refuses the pair where it is decided,
    and the generator has no case that declines.
    """
    folder = tmp_path / "cannot"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(IN_TWO_OFFSETS, 40))
    assert document["columns"][0]["datetimes_read_at"] == "utc"
    edited = copy.deepcopy(document)
    boundary = edited["columns"][0]["high_tail"]["boundary"]
    leap = f"{boundary[0:17]}60"
    edited["columns"][0]["high_tail"]["boundary"] = leap
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, edited, "cannot.json")
    message = f"{raised.value}"
    assert "D10" in message
    assert leap in message
    assert "when" in message

    # The same description without that one edit loads and reports no
    # tail at all, so the refusal above is the pair's and not the base's.
    ordinary = generation.generate(_loaded(folder, document, "ok.json"), 3)
    assert "high_tail.rows" not in _named(ordinary)
    assert "low_tail.rows" not in _named(ordinary)


def test_the_generator_writes_the_published_seconds_on_both_clocks(
    tmp_path: pathlib.Path,
) -> None:
    """No clock has a case in which the end is not written from its fields.

    The refusal above is the loader's. This is the other half: the
    writing rule itself no longer asks which clock it is on before
    deciding whether to write the published seconds field. Handed the
    shared-clock facts directly -- the route a loaded description can no
    longer take -- the cell still carries the published seconds, so a
    future loader change cannot silently restore the old behaviour.
    """
    folder = tmp_path / "clocks"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(IN_TWO_OFFSETS, 40))
    facts = _loaded(folder, document, "clocks.json").columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts)
    assert facts.datetimes_read_at == "utc"
    high = facts.high_tail
    assert high is not None
    leap = f"{high.boundary[0:17]}60"
    shared = dataclasses.replace(
        facts, high_tail=dataclasses.replace(high, boundary=leap)
    )
    written = generation._endpoint_cell(shared, leap, "-05:00", "T")
    assert written is not None
    assert written[17:19] == "60"

    local = dataclasses.replace(shared, datetimes_read_at="local")
    on_the_wall = generation._endpoint_cell(local, leap, "-05:00", "T")
    assert on_the_wall is not None
    assert on_the_wall[17:19] == "60"


def test_a_ladder_rung_the_tail_rule_withholds_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The ladder is published between the two boundaries (D11).

    The matrix calls the boundary exact and the ladder around it a rule;
    nothing enforced the OLD pair either, and a ladder beginning before
    `earliest` loaded, so the twin held instants before its own published
    earliest instant with nothing named -- an exact fact missed in
    silence. Stage 3's D11 is the same protection one step further in:
    the ranks the ladder may speak at are exactly the ranks between the
    two boundaries.
    """
    folder = tmp_path / "tied"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(AT_THE_SECOND, 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["date_percentiles"]["min"] = (
        edited["columns"][0]["low_tail"]["boundary"]
    )
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, edited, "tied.json")
    assert "D11" in f"{raised.value}"


# -- the whole shape space, on the twin's own bytes --------------------

# Every shape of temporal column the contract admits, so that no rule
# about an end can be added for a shape nothing exercises. The names are
# the reader's, not the contract's.
SHAPES = {
    "quarters": ["2024-Q1", "2024-Q2", "2024-Q3", "2024-Q4"],
    "whole dates": [
        "2024-01-05", "2024-02-19", "2024-07-30", "2024-11-02",
    ],
    "whole minutes": [
        "2024-01-05 09:15", "2024-02-19 13:40",
        "2024-07-30 21:05", "2024-11-02 04:55",
    ],
    "seconds": AT_THE_SECOND,
    "fractions of a second": [
        "2024-01-05 09:15:07.250", "2024-02-19 13:40:44.500",
        "2024-07-30 21:05:19.125", "2024-11-02 04:55:02.875",
    ],
    "one offset": [f"{value}+02:00" for value in AT_THE_SECOND],
    "two offsets": IN_TWO_OFFSETS,
    "offsets too rare to name": [
        "2024-01-05 09:15:07+02:00", "2024-02-19 13:40:44+03:00",
        "2024-07-30 21:05:19-05:00", "2024-11-02 04:55:02-06:00",
    ],
}

# The three descriptions each shape is asked for: the producer's own, and
# two ends a real reader can hand a description that carry a seconds
# field the shape may or may not be able to show.
END_EDITS = ["as published", "a leap second at the end", "seconds at the end"]


def _with_boundary(document: Document, seconds: str) -> Document:
    """The same description with its high boundary's seconds field changed."""
    edited = copy.deepcopy(document)
    block = edited["columns"][0]
    tail = block["high_tail"]
    if not isinstance(tail, dict):
        return edited
    boundary = tail["boundary"]
    moved = f"{boundary[0:17]}{seconds}"
    tail["boundary"] = moved
    for name in taxonomy.LADDER_NAMES:
        if block["date_percentiles"][name] == boundary:
            block["date_percentiles"][name] = moved
    return edited


def _redescribed(folder: pathlib.Path, twin: generation.Twin) -> Document:
    """Write the twin as a table, read THAT, and describe it again."""
    lines = [",".join(twin.names)]
    for row in twin.rows:
        lines = lines + [",".join(row)]
    path = fixtures.write(folder, "twin.csv", "\n".join(lines) + "\n")
    again = profile.build_document(
        reading.read_table(str(path)), taxonomy.Settings(), []
    )
    return typing.cast(Document, json.loads(json.dumps(again)))


def test_every_description_the_loader_accepts_gives_both_boundaries_back(
    tmp_path: pathlib.Path,
) -> None:
    """The obligation itself, over the whole space, on the written bytes.

    The wording checks below read what the documents SAY. This reads what
    the run DOES, and it is the half that no prose can satisfy: for every
    shape of temporal column and every boundary a reader can publish,
    either the description is refused -- which is what D10 does with the
    two pairs no cell can show -- or the twin is described again and
    gives back the same two boundaries and the same counts beyond them.
    There is no third outcome, and an exception added to either
    specification would have to make one.
    """
    accepted = 0
    refused = 0
    carried_a_leap_second = 0
    for shape, values in sorted(SHAPES.items()):
        for edit in END_EDITS:
            folder = tmp_path / f"{shape}-{edit}".replace(" ", "-")
            folder.mkdir(parents=True, exist_ok=True)
            document = _document(folder, _rows(values, 40))
            block = document["columns"][0]
            if edit != "as published" and block["resolution"] != "datetime":
                continue
            if edit == "a leap second at the end":
                document = _with_boundary(document, "60")
            elif edit == "seconds at the end":
                document = _with_boundary(document, "37")
            try:
                described = _loaded(folder, document, "described.json")
            except errors.ProfileError as raised:
                assert "D10" in f"{raised}", (shape, edit)
                refused = refused + 1
                continue
            accepted = accepted + 1
            facts = described.columns[0].facts
            assert isinstance(facts, contract.DatetimeFacts)
            assert facts.low_tail is not None and facts.high_tail is not None
            twin = generation.generate(described, 3)
            named = _named(twin)
            for fact in ["low_tail.rows", "high_tail.rows"]:
                assert fact not in named, (shape, edit, fact)
            again = _redescribed(folder, twin)["columns"][0]
            for side, tail in (
                ("low_tail", facts.low_tail),
                ("high_tail", facts.high_tail),
            ):
                assert again[side]["boundary"] == tail.boundary, (shape, edit)
                assert again[side]["rows"] == tail.rows, (shape, edit, side)
            if facts.high_tail.boundary[17:19] == "60":
                carried_a_leap_second = carried_a_leap_second + 1

    # The floor under the count: the space is really walked, the refusals
    # are the two pairs and not the whole battery, and the last second of
    # a leap minute is carried by the shapes that can show one rather
    # than refused everywhere.
    assert accepted >= 14, accepted
    assert refused >= 3, refused
    assert carried_a_leap_second >= 3, carried_a_leap_second


def test_no_twin_cell_leaves_what_its_own_column_can_write(
    tmp_path: pathlib.Path,
) -> None:
    """The calendar's edge, kept by the GENERATOR (stage 3, plan P4-D331).

    This was the third pair D10 refused: a shared-clock end whose own
    endpoint offset carried its cell outside the years `0001` to `9999`.
    Neither field is published any more, so there is nothing for a loader
    to refuse -- and the obligation did not disappear with them, it moved
    to where the cell is now derived. Method G7.3e keeps every rank of a
    tail inside the days the column's own member and clock can write and
    read back, so a column sitting against the calendar's first day, on
    the shared clock, with an offset behind it, has a twin every cell of
    which reads back as a date.

    The same clause covers the two-figure year, whose reader settles the
    century at 1969..2068: a twin that wrote 1968 as `68` would be read
    back as 2068 (the skeptic of the tail design, B2).
    """
    folder = tmp_path / "calendar"
    folder.mkdir(parents=True, exist_ok=True)
    edge = [
        f"0001-01-{1 + index:02d} 00:30:00{offset}"
        for index in range(20)
        for offset in ("+02:00", "-05:00")
    ]
    document = _document(folder, edge)
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["datetimes_read_at"] == "utc"
    described = _loaded(folder, document, "calendar.json")
    twin = generation.generate(described, 3)
    written = [cell for cell in twin.columns[0] if cell != ""]
    assert written
    for cell in written:
        assert parsing.parse_datetime(cell, block["format"]) is not None, cell
    again = _redescribed(folder, twin)["columns"][0]
    assert again["low_tail"]["boundary"] == block["low_tail"]["boundary"]
    assert again["low_tail"]["rows"] == block["low_tail"]["rows"]

    # And the same at the other edge of a two-figure year's window.
    second = tmp_path / "pivot"
    second.mkdir(parents=True, exist_ok=True)
    early = [
        f"{1 + index % 28:02d}/{1 + index // 28:02d}/69" for index in range(40)
    ]
    pivoted = _document(second, early)
    assert pivoted["columns"][0]["format"] in parsing.TWO_FIGURE_MEMBERS
    built = generation.generate(_loaded(second, pivoted, "pivot.json"), 3)
    for cell in [cell for cell in built.columns[0] if cell != ""]:
        year = parsing.parse_datetime(cell, pivoted["columns"][0]["format"])
        assert year is not None, cell
        assert 1969 <= int(year[0][0:4]) <= 2068, cell


def test_a_tail_this_tool_fails_to_write_is_still_printed(
    tmp_path: pathlib.Path,
) -> None:
    """The read-back check can fail, and says so when it does.

    Every description the loader accepts has tails G7.3b writes exactly,
    so the check cannot be reached by a description any more. That is
    precisely when a check quietly becomes decoration, so this puts a
    defect back: the tail's distances are reverted to nought -- every
    outer rank on the boundary itself -- and the run has to catch its own
    tail, name it under the contract's field name, and print both counts.
    The report entry is a defect notice, not a disposition: no
    description asked for it.
    """
    folder = tmp_path / "detector"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(AT_THE_SECOND, 40))
    described = _loaded(folder, document, "detector.json")

    kept = generation._tail_distances

    def collapsed(
        shape: "generation._TailShape", words: "dict[int, int]"
    ) -> "list[int]":
        """The withdrawn behaviour: every outer rank on the boundary."""
        return [0 for _index in range(shape.rows)]

    generation._tail_distances = collapsed  # type: ignore[assignment]
    try:
        twin = generation.generate(described, 3)
    finally:
        generation._tail_distances = kept  # type: ignore[assignment]

    named = _named(twin)
    assert "low_tail.rows" in named, "the read-back check missed a lost tail"
    assert named["low_tail.rows"].published == f"{described.columns[0].facts.low_tail.rows}"
    assert named["low_tail.rows"].achieved == "0"
    printed = rendering.report(described, twin)
    assert "low_tail.rows" in printed


# -- the wording: what the two documents are allowed to say ------------


def test_the_contract_row_for_the_two_ends_states_the_exact_class() -> None:
    """The disposition cell says EXACT-OBSERVABLE and names no exception.

    This is the sentence a previous repair rewrote. It read
    "outside the two named corners below"; the second of those corners
    made the end REPORT-ONLY.
    """
    cell = _row(CONTRACT, "`earliest`, `latest`")

    assert cell.startswith("exact-observable")
    assert "in the representation owner decision 5 fixes" in cell
    assert "no corner, no exception" in cell

    assert "report-only" not in cell
    assert "approximated" not in cell
    assert "outside" not in cell


def test_the_contract_row_for_the_two_ladder_ends_matches_it() -> None:
    """The first and last rungs are the same two instants, so one rule."""
    cell = _row(CONTRACT, "`date_percentiles.min`")

    assert cell.startswith("exact-observable")
    assert "report-only" not in cell
    assert "outside" not in cell


def test_the_contract_names_exactly_one_datetime_corner() -> None:
    """One corner, and it is the withheld-offset one.

    The count is the check. A second numbered corner is how the end was
    lowered last time, and any future one has to be argued for in the
    plan before it can appear here.
    """
    body = _text(CONTRACT)
    opening = "the one corner this matrix names"
    closing = "outside that one corner"
    assert opening in body
    assert closing in body
    between = body[body.index(opening) : body.index(closing)]

    assert "1. **withheld offsets.**" in between
    assert "2. **" not in between
    assert "report-only for that column" in between
    assert "`earliest` and `latest` are the instants themselves" in between


def test_both_documents_state_the_plan_s_own_obligation() -> None:
    """The plan's words, in the plan and in both specifications.

    One phrase, carried unchanged, so no document can drift from the
    other two while each still reads well on its own.
    """
    assert PLAN_WORDS in _text(PLAN)
    for path in [PLAN, CONTRACT, METHOD]:
        assert SHARED_WORDS in _text(path), path.name


def test_the_method_states_how_a_published_moment_is_written() -> None:
    """G7.5 fixes the exact representation, so an implementer can build it.

    STAGE 3: the published moments of a column of dates are the two tail
    boundaries and the values a few-valued tail lists, so the sentences
    this reads are the ones stated over them. The obligation is the same
    one, moved with the fact it is about (plan P4-D328).
    """
    body = _text(METHOD)

    assert (
        "built from the published moment's own fields, not from its "
        "ordinal" in body
    )
    assert "write the published `ss` back into the seconds field" in body
    assert (
        "both tail boundaries are therefore exact-observable, with no "
        "leap-second exception" in body
    )
    assert (
        "each used exactly as published" in body
    )


def test_both_documents_state_the_refusal_that_makes_it_true() -> None:
    """The two pairs no cell can show are refused, in both documents.

    The sentence "no corner, no exception" is only true of a repository
    whose loader refuses the descriptions on which it would otherwise be
    false. Deleting D10 or D11 from either document while leaving the
    exact wording in place is the same drift in the other direction, so
    both are asserted here beside the wording itself.
    """
    contract_body = _text(CONTRACT)
    assert "invariant d10 (an endpoint the column's own recorded shape" in (
        contract_body
    )
    assert "invariant d11 (the ladder ends are the two endpoints)" in (
        contract_body
    )
    assert "| d10 |" in contract_body
    assert "| d11 |" in contract_body

    method_body = _text(METHOD)
    assert "refused by the profile contract's **d10**" in method_body
    assert "its **d11** ties `date_percentiles.min`" in method_body


def test_the_restoration_is_recorded_where_a_reader_will_find_it() -> None:
    """The audit trail is part of the repair, not a commit message.

    A reader who sees only the current text cannot tell a decision from a
    drift, so the contract records which bar was lowered, by which repair
    and what was put back -- twice now, because the second lowering was
    made by the repair that recorded the first.
    """
    body = _text(CONTRACT)

    assert (
        "13.14 the last second of a leap minute is carried, not excused"
        in body
    )
    assert "no owner decision authorized it" in body
    assert "review item p2-c2-f5" in body

    assert "13.15 the same bar, lowered a second time in a second place" in (
        body
    )
    assert "review item p2-c3-f2" in body

    assert "13.16 the same bar, a third and fourth time" in body
    assert "review item p2-c4-f1" in body
    # ...and the record says what replaced the instruction that failed
    # four times, so a reader can find the guard from the history.
    assert "registry" in body


# -- the wording, checked in EVERY place it appears --------------------
#
# The guard this replaces read one matrix cell and counted one numbered
# corner. It passed while the same document, four paragraphs further on,
# said that an end could be met with something else and named in the
# report -- and while the method said it too and the generator did it
# (review item P2-C3-F2). A guard that looks in one place cannot see
# that, so this one looks in every place.
#
# The rule: take every PASSAGE of either specification that speaks about
# the two ends of a column of dates, and keep those that also speak of an
# end being met with something other than the instant that was published.
# Each one that remains has to be a passage this repository has decided
# about. The decisions are listed below with the reason each is
# legitimate, and each is found by a short phrase of its own, so ordinary
# rewording is free while an ADDED passage of that kind -- anywhere, in
# either document, however it is phrased -- belongs to nobody and turns
# this file red. `test_an_exception_added_anywhere_is_caught` is the
# proof that it does.

# A passage speaks about an end when it names one of these. `endpoint`
# is in the list without a qualifier on purpose: the paragraph that
# survived the last repair called it "the endpoint" and named neither
# field, so a list of field names alone would have missed it. The price
# is that the numeric ladder's ends are read too, and they are decided
# on below like everything else.
END_WORDS = (
    "earliest",
    "latest",
    "endpoint",
    "leap minute",
    "sixtieth second",
    "seconds field",
    "`ss` of `60`",
)

# ...and it speaks of an end being met with something else when it uses
# one of these. They are the vocabulary this repository writes deviations
# in: a lesser disposition, a recount, a value named beside the published
# one, or the following minute this item's own defect wrote.
EXCUSE_WORDS = (
    "report-only",
    "approximated",
    "recount",
    "meets what it can",
    "met as far as",
    "named in the report",
    "names it in the report",
    "name it in the report",
    "the following minute",
    "cannot all hold",
    "beside the published",
    "the report names",
    "the report says",
    "stops being exact",
    "not reproduced",
    "cannot be met",
    "missed",
)

# Every passage of the contract that is allowed to carry that vocabulary,
# with the reason. Anything else is an exception nobody decided on.
CONTRACT_PASSAGES = {
    "invariant l2 (endpoints)": (
        "the numeric ladder's own two ends, stated exact beside the "
        "approximated interior rungs"
    ),
    "no seconds field to carry anything else": (
        "D10 itself: the two pairs are refused, not reported"
    ),
    # The disposition matrix's `earliest`, `latest` row was decided here
    # while a table was ONE passage. It is read row by row now, and no row
    # of the matrix speaks of an end and a deviation in one breath, so the
    # key is withdrawn: kept, it would have exempted the one row of the
    # contract an excuse for an end would most likely be written into (the
    # merge skeptic of the carried date items of 2026-09-18).
    "**withheld offsets.**": (
        "the owner-authorized corner, which touches the two OFFSET "
        "fields and says the ends themselves come back exactly"
    ),
    "may not be made one": (
        "the record of the first lowering and its restoration (P2-C2-F5)"
    ),
    "left standing beside it is refused": (
        "the record of the second lowering and its refusal (P2-C3-F2)"
    ),
    "13.14 the last second of a leap minute": "the history entry",
    "13.15 the same bar, lowered a second time": "the history entry",
    "13.16 the same bar, a third and fourth time": "the history entry",
}

METHOD_PASSAGES = {
    "**the filled ladder.**": (
        "the numeric ladder's null rungs, which are filled before "
        "anything reads them"
    ),
    "the precedence is stated, not implied": (
        "G5.5's sign repair, where a NUMERIC endpoint moves on a "
        "description whose ladder contradicts its own sign counts. It is "
        "a named deviation of the kind G11 lists, and the contract's 9.4 "
        "row claims no exception-free class for it, unlike 9.6"
    ),
    "one generator, created once from the seed": (
        "the determinism summary, which lists the recount among the "
        "things a run does"
    ),
    "with no leap-second exception": (
        "G7.5's own statement of the exact class"
    ),
    "has no case that declines": (
        "the record of the three withdrawn exceptions (P2-C3-F2, "
        "P2-C4-F1)"
    ),
    "every deviation this document permits": (
        "G11's inventory of every deviation, which a reader checks the "
        "report against"
    ),
    "with one exception, and it keeps an exact fact": (
        "G7.5's separator rule, where a cell whose fixed spelling is "
        "one the column publishes among its ABSENT cells is written "
        "with the other separator instead. It is the only passage of "
        "either document that speaks of an end and an exception in one "
        "breath while RAISING what the twin holds: the two spellings "
        "are the same instant at the same precision on the same clock, "
        "and without it an exact end walks out of the twin over a "
        "separator nobody chose (review item P4-DATE-F2). Where both "
        "spellings are declared absent it declines to invent a third "
        "and G12 names the loss, which is the behaviour every other "
        "passage here describes"
    ),
    # THE PASSAGE STAGE 3 WROTE, when the two ends left the role.
    "**and two left the index in stage 3**": (
        "the deviation key index's record of `earliest` and `latest` "
        "LEAVING it (plan P4-D328). It reaches this guard's vocabulary "
        "because it names both ends beside the word 'fail', and what it "
        "says is the opposite of an excuse: neither instant is published "
        "any more, so no run can name one in a report at all, and the "
        "fact that stands where they stood -- a tail's BOUNDARY -- is "
        "exact, written from the published moment's own fields, with "
        "only the two distances left to the construction window"
    ),
    # THREE PASSAGES THE STAGE-2b LANDINGS WROTE, each reaching this
    # guard's vocabulary in a sense that is not a temporal end (measured
    # at their integration: the flagged words are quoted in each reason).
    "**and the exchange runs in both directions**": (
        "G6.1's padded-style exchange (landings 2b.7 and 2b.16). Its "
        "'endpoint' is a NUMERIC ladder end no padding may spend, and its "
        "'missed' and 'cannot be met' are the pad census, not a date end"
    ),
    "**the four class counts are packed with the two alphabet counts, in one allocation": (
        "G9.6's identifier packing. Its 'earliest' is the first name in "
        "sorted order on a tie (landing 2b.18), its 'recount' and "
        "'missed' are class and layout counts, and its 'cannot all hold' "
        "is the whole-number corner G12 refuses; no end of a date column "
        "is in it"
    ),
    # G14.3's table of frozen cases was decided here in two halves, one
    # key each, while a table was ONE passage: its END words ('endpoint',
    # 'earliest', 'latest') and its EXCUSE words ('recount') stood in
    # different rows, and a key exempting the whole table exempted any row
    # written into it. Read row by row, no row of either half speaks of an
    # end and a deviation together -- measured on the repair pass of the
    # carried date items of 2026-09-18 -- so both keys are withdrawn.
}

# Exceptions of the kind that have twice been written into these
# documents, plus phrasings nobody has used yet. Every one of them must
# be caught wherever it is put.
ADDED_EXCEPTIONS = (
    # The paragraph the round-2 repair wrote, in substance.
    (
        "**What remains.** A hand-made description can still publish an "
        "end no cell of its own recorded shape can show, and there the "
        "generator meets what it can, RECOUNTS the endpoint from the "
        "written cell, and names it in the report with the achieved "
        "instant beside the published one."
    ),
    # The disposition the round-1 repair wrote.
    (
        "| `earliest`, `latest` | REPORT-ONLY where the ordinal space has "
        "no room for the value |"
    ),
    # Phrasings neither repair used.
    (
        "On such a column the twin writes the following minute instead, "
        "and the report says so beside the published `latest`."
    ),
    (
        "For that description the seconds field is APPROXIMATED rather "
        "than exact, and both ends are measured instead."
    ),
    (
        "Where `datetimes_read_at` is `utc`, a published `SS` of `60` is "
        "not reproduced; the end is recounted from the written cell."
    ),
)


def _normal(lines: "list[str]") -> str:
    """Lines joined, lower-cased, with every run of whitespace one space."""
    return " ".join(" ".join(lines).lower().split())


def _is_separator(line: str) -> bool:
    """A markdown table's rule line, `|---|:---:|`."""
    body = line.strip()
    return (
        body.startswith("|")
        and "---" in body
        and not body.replace("|", "").replace("-", "").replace(":", "").strip()
    )


def _segments(block: "list[str]") -> "list[str]":
    """One blank-line separated block, as the statements it makes.

    A paragraph is ONE statement. A markdown table is one statement PER
    ROW, each read with the rule above it -- the lines before the table
    in the same block and its header row -- so a row is never read apart
    from what introduces it, and a decided row exempts itself and no row
    beside it (the merge skeptic of the carried date items of 2026-09-18,
    its second MINOR). Until then a table was one passage, and the key
    that decided one row of G14.3's case table exempted every row of it:
    an excuse written into that table as a row of its own was caught by
    nothing.
    """
    table = [index for index in range(len(block)) if block[index].lstrip().startswith("|")]
    if not table:
        return [_normal(block)]
    first = table[0]
    rule = block[:first]
    rows = block[first:]
    separators = [index for index in range(len(rows)) if _is_separator(rows[index])]
    if separators:
        rule = rule + rows[: separators[0]]
        rows = rows[separators[0] + 1 :]
    found: "list[str]" = []
    for row in rows:
        found = found + [_normal(rule + [row])]
    return found


def _passages(body: str) -> "list[str]":
    """One document's statements: every paragraph, and every table row.

    Blocks are separated by blank lines; `_segments` cuts each into what
    it states.
    """
    found: list[str] = []
    block: list[str] = []
    for line in body.splitlines():
        if line.strip():
            block = block + [line]
        elif block:
            found = found + _segments(block)
            block = []
    if block:
        found = found + _segments(block)
    return found


def _about_an_end(passage: str) -> bool:
    """True when this passage speaks about the two ends."""
    return any(word in passage for word in END_WORDS)


def _excuses(passage: str) -> "list[str]":
    """The words by which this passage speaks of an end met otherwise."""
    return [word for word in EXCUSE_WORDS if word in passage]


def _undecided(body: str, decided: "dict[str, str]") -> "list[str]":
    """Passages that excuse an end and are nobody's decision."""
    return [
        passage
        for passage in _passages(body)
        if _about_an_end(passage)
        and _excuses(passage)
        and not any(key in passage for key in decided)
    ]


def test_no_passage_of_either_specification_excuses_an_end() -> None:
    """Every such passage in either document is one that was decided on.

    This is the check the last guard could not make. It reads the whole
    of both documents rather than one cell of one table, so the
    paragraph that survived the last repair -- four paragraphs below the
    cell that guard read -- would have failed here on the day it was
    written.
    """
    for path, decided in [
        (CONTRACT, CONTRACT_PASSAGES),
        (METHOD, METHOD_PASSAGES),
    ]:
        body = path.read_text(encoding="utf-8")
        left = _undecided(body, decided)
        assert not left, f"{path.name}: {[one[:160] for one in left]}"


def test_every_decided_passage_is_still_where_it_was_decided() -> None:
    """The list above does not go stale, in either direction.

    A key that no longer finds its passage means the passage was
    rewritten or removed -- including the two history records, which are
    the audit trail -- and a key that finds two means the phrase stopped
    identifying one passage.
    """
    for path, decided in [
        (CONTRACT, CONTRACT_PASSAGES),
        (METHOD, METHOD_PASSAGES),
    ]:
        found = _passages(path.read_text(encoding="utf-8"))
        for key, why in decided.items():
            holders = [one for one in found if key in one]
            assert len(holders) == 1, f"{path.name}: {key} ({why})"


# A row of the kind the round-1 repair wrote into the disposition matrix,
# put INTO each table this guard once exempted whole, among its rows.
TABLE_ROWS = (
    (CONTRACT, CONTRACT_PASSAGES, "| `date_percentiles` interior rungs |"),
    (METHOD, METHOD_PASSAGES, "| `quarter` | g7.5's quarter form"),
    (METHOD, METHOD_PASSAGES, "| `written_form_classes` |"),
)
ADDED_ROW = (
    "| `latest` | met as far as the ordinal space allows: the end is "
    "APPROXIMATED and the report names it |"
)


def test_an_exception_written_into_a_table_is_caught() -> None:
    """The row-level half of the mutation above (the merge skeptic, MINOR 2).

    A table used to be ONE passage, and the key that decided one row of
    G14.3's case table exempted every row of it, so an excuse written into
    that table as a row of its own came back as nobody's decision --
    nothing. Each table this guard once exempted whole now takes such a row
    among its own, and every one of them comes back undecided.
    """
    for path, decided, anchor in TABLE_ROWS:
        lines = path.read_text(encoding="utf-8").split("\n")
        places = [
            index for index in range(len(lines))
            if lines[index].lower().startswith(anchor)
        ]
        assert len(places) == 1, (path.name, anchor)
        mutated = "\n".join(
            lines[: places[0]] + [ADDED_ROW] + lines[places[0] :]
        )
        assert _undecided(mutated, decided), f"{path.name} before {anchor}"


def test_an_exception_added_anywhere_is_caught() -> None:
    """The mutation this guard exists for: an exception, anywhere.

    Each of the withdrawn paragraphs, and phrasings no repair has used
    yet, is put into each document at the front, in the middle and at the
    end. Every one of them has to come back as a passage nobody decided
    on. A guard that reads one place would catch none of these; this one
    catches all of them, which is what makes the check above mean
    something.
    """
    for path, decided in [
        (CONTRACT, CONTRACT_PASSAGES),
        (METHOD, METHOD_PASSAGES),
    ]:
        body = path.read_text(encoding="utf-8")
        assert not _undecided(body, decided), path.name
        blocks = body.split("\n\n")
        for added in ADDED_EXCEPTIONS:
            for place in [0, len(blocks) // 2, len(blocks)]:
                mutated = "\n\n".join(
                    blocks[:place] + [added] + blocks[place:]
                )
                assert _undecided(mutated, decided), (
                    f"{path.name} at block {place}: {added[:60]}"
                )


# -- the version 6 contract commands no removed endpoint behaviour -----
#
# THE GOVERNANCE PASS OF STAGE 3'S REVIEW, ITEM 10. Everything above
# reads `profile-contract-v4.md`, which is history and is sealed as
# history. The document that GOVERNS is version 6, and stage 3 removed
# `earliest` and `latest` from it (plan P4-D328) while section 9's prose
# went on commanding the behaviour they carried: "the two endpoint cells
# are written from the published endpoint's OWN fields", "D11 ties
# `date_percentiles.min` and `.max` to the same two texts". An
# independent implementer reading the disposition table and the
# paragraph under it received two incompatible instructions at once.
#
# The obligation did not go; it moved to the two tail BOUNDARIES, which
# are the outermost moments a description names now. So the guard is not
# "the words are gone" -- that would be satisfied by deleting the
# obligation -- it is BOTH: no passage of the governing contract still
# commands a published endpoint, AND the boundary obligations are stated
# where the endpoint ones were.

GOVERNING_CONTRACT = fixtures.GOVERNING_CONTRACT

# The words that mark a passage as a RECORD of what was removed rather
# than an instruction about what a description carries.
WITHDRAWN_MARKERS = (
    "are gone",
    "no longer exist",
    "left the matrix",
    "which no longer exist",
    "and both fields are gone",
)

# The two fields stage 3 removed, as a normative field name is written.
REMOVED_ENDPOINTS = ("`earliest`", "`latest`", "`earliest_utc_offset`", "`latest_utc_offset`")


def _governing_passages() -> "list[str]":
    """The version 6 contract's passages, its own decision record aside.

    Section 13 is "Decisions this contract took, and why": it exists to
    record what was lowered and restored, and reading it as an
    instruction would make the audit trail unwritable.
    """
    body = GOVERNING_CONTRACT.read_text(encoding="utf-8")
    body = body[: body.index("\n## 13. Decisions this contract took")]
    return [
        " ".join(passage.split())
        for passage in dispositions.passages(GOVERNING_CONTRACT)
        if " ".join(passage.split()) in " ".join(body.split())
    ]


def test_the_governing_contract_commands_no_removed_endpoint() -> None:
    """No normative passage of version 6 names an endpoint as a live fact."""
    left = [
        passage
        for passage in _governing_passages()
        if any(name in passage for name in REMOVED_ENDPOINTS)
        and not any(mark in passage for mark in WITHDRAWN_MARKERS)
    ]
    assert left == [], (
        "these passages of the contract that GOVERNS still name a field "
        "stage 3 removed, without saying it is removed:\n  "
        + "\n  ".join(one[:200] for one in left)
    )


def test_the_governing_contract_states_the_boundary_obligations() -> None:
    """...and the obligation is stated on what replaced them.

    Without this half the check above would be met by deleting the
    paragraph, which is the lowering this whole file exists to catch.
    """
    body = " ".join(GOVERNING_CONTRACT.read_text(encoding="utf-8").split())
    for sentence in (
        "every MOMENT A TAIL PUBLISHES — its `boundary` and each entry "
        "of its `values` — is exact in owner decision 5's representation "
        "with no exception at all",
        "a published moment is written from its OWN fields rather than "
        "through the whole-second ordinal arithmetic the interior ranks "
        "use",
        "**D11 makes `date_percentiles.min` and `.max` `null` in every "
        "description**",
    ):
        assert " ".join(sentence.split()) in body, sentence[:80]
