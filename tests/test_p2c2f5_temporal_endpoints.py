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

import fixtures
from synthtwin import (
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
PLAN_WORDS = (
    "`earliest`, `latest` exact-observable in the representation owner "
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
    """Enough rows of a small set of values to clear the smallest group."""
    return [values[index % len(values)] for index in range(copies)]


def _named(twin: generation.Twin) -> "dict[str, generation.Deviation]":
    """Every fact of the one column the run could not meet, by name."""
    return {
        deviation.fact: deviation
        for deviation in twin.deviations
        if deviation.column == "when"
    }


# -- the behaviour: the end a real reader can hand us ------------------


def test_a_published_leap_second_end_is_written_back_unchanged(
    tmp_path: pathlib.Path,
) -> None:
    """The review item's own scenario, and it now holds the end exactly.

    Forty rows, a genuine description, an end whose seconds field is 60,
    seed 3. The item's twin wrote the following minute and named the
    miss; a boundary filter written against that twin admitted a row the
    real table's own end excludes.
    """
    folder = tmp_path / "held"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(AT_THE_SECOND, 40))
    block = document["columns"][0]
    assert block["role"] == "datetime"
    assert block["datetimes_read_at"] == "local"
    assert block["time_precision"] == "second"

    end = f"{block['latest'][0:17]}60"
    block["latest"] = end
    block["date_percentiles"]["max"] = end
    twin = generation.generate(_loaded(folder, document, "held.json"), 3)

    assert "latest" not in _named(twin)
    written = [cell for cell in twin.columns[0] if cell != ""]
    assert "2024-11-02T04:55:60" in written
    assert max(written) == "2024-11-02T04:55:60"


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
        for published in [facts.earliest, facts.latest]:
            for offset in carried or [""]:
                moved = generation._ordinal_of(published, "datetime")
                if facts.datetimes_read_at == "utc":
                    moved = moved + generation._offset_seconds(offset)
                assert generation._endpoint_cell(
                    facts, published, offset
                ) == generation._cell_of_ordinal(
                    moved,
                    facts.resolution,
                    facts.time_precision,
                    facts.subsecond_digits,
                ), (name, published, offset)


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
    end = f"{edited['columns'][0]['latest'][0:17]}60"
    edited["columns"][0]["latest"] = end
    edited["columns"][0]["date_percentiles"]["max"] = end
    with pytest.raises(errors.ProfileError) as raised:
        _loaded(folder, edited, "cannot.json")
    message = f"{raised.value}"
    assert "D10" in message
    assert end in message
    assert "when" in message

    # The same description without that one edit loads and reports no
    # end at all, so the refusal above is the pair's and not the base's.
    ordinary = generation.generate(_loaded(folder, document, "ok.json"), 3)
    assert "latest" not in _named(ordinary)
    assert "earliest" not in _named(ordinary)


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
    shared = dataclasses.replace(facts, latest=f"{facts.latest[0:17]}60")
    written = generation._endpoint_cell(shared, shared.latest, "-05:00")
    assert written is not None
    assert written[17:19] == "60"

    local = dataclasses.replace(shared, datetimes_read_at="local")
    on_the_wall = generation._endpoint_cell(local, local.latest, "-05:00")
    assert on_the_wall is not None
    assert on_the_wall[17:19] == "60"


def test_a_ladder_end_that_is_not_the_column_s_own_end_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """`date_percentiles` ends and the column's ends are one pair (D11).

    The matrix calls both pairs exact and says they are the same two
    instants; nothing enforced it. A ladder beginning before `earliest`
    loaded, and the twin then held instants before its own published
    earliest instant with nothing named -- an exact fact missed in
    silence, which is worse than the reported one this item is about.
    """
    folder = tmp_path / "tied"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(AT_THE_SECOND, 40))
    edited = copy.deepcopy(document)
    edited["columns"][0]["date_percentiles"]["min"] = "2020-01-01 00:00:00"
    edited["columns"][0]["date_percentiles"]["p01"] = "2020-01-01 00:00:00"
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


def _with_end(document: Document, seconds: str) -> Document:
    """The same description with its last value's seconds field changed."""
    edited = copy.deepcopy(document)
    block = edited["columns"][0]
    end = f"{block['latest'][0:17]}{seconds}"
    block["latest"] = end
    block["date_percentiles"]["max"] = end
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


def test_every_description_the_loader_accepts_gives_both_ends_back(
    tmp_path: pathlib.Path,
) -> None:
    """The obligation itself, over the whole space, on the written bytes.

    The wording checks below read what the documents SAY. This reads what
    the run DOES, and it is the half that no prose can satisfy: for every
    shape of temporal column and every end a reader can publish, either
    the description is refused -- which is what D10 does with the two
    pairs no cell can show -- or the twin is described again and gives
    back the same `earliest`, the same `latest`, and the same two ladder
    ends. There is no third outcome, and an exception added to either
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
                document = _with_end(document, "60")
            elif edit == "seconds at the end":
                document = _with_end(document, "37")
            try:
                described = _loaded(folder, document, "described.json")
            except errors.ProfileError as raised:
                assert "D10" in f"{raised}", (shape, edit)
                refused = refused + 1
                continue
            accepted = accepted + 1
            facts = described.columns[0].facts
            assert isinstance(facts, contract.DatetimeFacts)
            twin = generation.generate(described, 3)
            named = _named(twin)
            for fact in [
                "earliest",
                "latest",
                "date_percentiles.min",
                "date_percentiles.max",
            ]:
                assert fact not in named, (shape, edit, fact)
            again = _redescribed(folder, twin)["columns"][0]
            assert again["earliest"] == facts.earliest, (shape, edit)
            assert again["latest"] == facts.latest, (shape, edit)
            assert again["date_percentiles"]["min"] == facts.earliest
            assert again["date_percentiles"]["max"] == facts.latest
            if facts.latest[17:19] == "60":
                carried_a_leap_second = carried_a_leap_second + 1

    # The floor under the count: the space is really walked, the refusals
    # are the two pairs and not the whole battery, and the last second of
    # a leap minute is carried by the shapes that can show one rather
    # than refused everywhere.
    assert accepted >= 14, accepted
    assert refused >= 3, refused
    assert carried_a_leap_second >= 3, carried_a_leap_second


def test_an_end_whose_offset_leaves_the_calendar_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The third pair, refused in BOTH directions (review item P2-C4-F1).

    This is the scenario round 4 ran. A shared-clock column whose first
    instant is inside the first day the canonical form can spell, with an
    endpoint offset behind that clock, asks for a cell outside the years
    `0001` to `9999`, which reads back as no date at all. The repair
    before this one wrote that cell, named the end in the report and
    called the calendar's own end something other than an exception --
    the fourth lowering of one obligation. The loader holds the end, its
    offset and the clock, so D10 settles the pair where it is decided,
    and the upper end is settled with it.
    """
    folder = tmp_path / "calendar"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(IN_TWO_OFFSETS, 40))
    assert document["columns"][0]["datetimes_read_at"] == "utc"

    for name, key, instant, offset, rung in [
        ("lower", "earliest", "0001-01-01 00:00:00", "-05:00", "min"),
        ("upper", "latest", "9999-12-31 23:59:59", "+02:00", "max"),
    ]:
        edited = copy.deepcopy(document)
        block = edited["columns"][0]
        block[key] = instant
        block[f"{key}_utc_offset"] = offset
        block["date_percentiles"][rung] = instant
        block["date_percentiles"]["p01" if rung == "min" else "p99"] = instant
        with pytest.raises(errors.ProfileError) as raised:
            _loaded(folder, edited, f"calendar-{name}.json")
        message = f"{raised.value}"
        assert "D10" in message, name
        assert instant in message, name
        assert offset in message, name
        assert "0001 to 9999" in message, name

    # The same description without that one edit loads and writes both
    # ends exactly, so the refusals above are the pair's and not the
    # shape's.
    ordinary = generation.generate(_loaded(folder, document, "ok.json"), 3)
    assert "earliest" not in _named(ordinary)
    assert "latest" not in _named(ordinary)


def test_an_end_this_tool_fails_to_write_is_still_printed(
    tmp_path: pathlib.Path,
) -> None:
    """The read-back check can fail, and says so when it does.

    Every description the loader accepts now has an end G7.5 writes
    exactly, so the check cannot be reached by a description any more.
    That is precisely when a check quietly becomes decoration, so this
    puts the defect back: the writing rule is reverted to the ordinal
    route -- the round-1 behaviour -- and the run has to catch its own
    end, name it under the contract's field name, and print both values.
    The report entry is a defect notice, not a disposition: no
    description asked for it.
    """
    folder = tmp_path / "detector"
    folder.mkdir(parents=True, exist_ok=True)
    document = _document(folder, _rows(AT_THE_SECOND, 40))
    block = document["columns"][0]
    end = f"{block['latest'][0:17]}60"
    block["latest"] = end
    block["date_percentiles"]["max"] = end
    described = _loaded(folder, document, "detector.json")

    kept = generation._endpoint_cell

    def reverted(
        facts: contract.DatetimeFacts, published: str, offset: str
    ) -> str:
        """The withdrawn rule: an end through the whole-second space."""
        moved = generation._ordinal_of(published, facts.resolution)
        if facts.datetimes_read_at == "utc":
            moved = moved + generation._offset_seconds(offset)
        return generation._cell_of_ordinal(
            moved,
            facts.resolution,
            facts.time_precision,
            facts.subsecond_digits,
        )

    generation._endpoint_cell = reverted  # type: ignore[assignment]
    try:
        twin = generation.generate(described, 3)
    finally:
        generation._endpoint_cell = kept  # type: ignore[assignment]

    named = _named(twin)
    assert "latest" in named, "the read-back check missed a changed end"
    assert named["latest"].published == end
    assert named["latest"].achieved == "2024-11-02 04:56:00"
    printed = rendering.report(described, twin)
    assert end in printed
    assert "2024-11-02 04:56:00" in printed


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


def test_the_method_states_how_an_end_is_written() -> None:
    """G7.5 fixes the exact representation, so an implementer can build it."""
    body = _text(METHOD)

    assert (
        "the two endpoint cells are built from the published endpoint's "
        "own fields, not from its ordinal" in body
    )
    assert "write the published `ss` back into the seconds field" in body
    assert (
        "both endpoints are therefore exact-observable, with no "
        "leap-second exception" in body
    )
    assert "these two cells are built by g7.5's endpoint rule" in body


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
    "| `earliest`, `latest` | exact-observable": (
        "the disposition matrix, which states the exact class"
    ),
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


def _passages(body: str) -> "list[str]":
    """One document's blank-line separated passages, lower-cased.

    A markdown table has no blank line inside it, so a table is one
    passage and a row cannot be read apart from the rule above it.
    """
    found: list[str] = []
    block: list[str] = []
    for line in body.splitlines():
        if line.strip():
            block = block + [line]
        elif block:
            found = found + [" ".join(" ".join(block).lower().split())]
            block = []
    if block:
        found = found + [" ".join(" ".join(block).lower().split())]
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
