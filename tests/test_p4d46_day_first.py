"""The day-first declaration, which is not an order swap.

Plan P4-D4.6. `--day-first` tells the profiler that slashed dates in
this table are written day first. Its mechanics are evidence-first, and
the decision says why in one sentence: a swap can silently reverse a
column against its own evidence.

WHAT IS PINNED HERE, and each of it is a rule the decision states:

- with the option given, BOTH slashed readings are counted for every
  column whose slashed cells are in play;
- the reading that parses strictly MORE cells wins whatever the
  declaration said, so ninety-nine ambiguous cells and one cell only
  the month-first reading can parse is read month first and counts
  nothing as unparsed;
- the declaration decides a count TIE and nothing else;
- every column read under the option carries EXACTLY ONE remark, and it
  is the evidence remark rather than the standing month-first warning,
  because the standing one warns about a guess and nothing here was
  guessed;
- that remark has TWO INDEPENDENT clauses: which reading was used and
  why, and -- whenever both only-one-reading counts are nonzero, at any
  counts, tie or no tie -- that the column carries evidence in both
  directions with both counts named;
- the declaration is recorded in the settings block, so the file says
  what it was written under;
- and the version-refusal message names the option and what leaving it
  out costs, which the suite derives from the shipped parser so that
  forgetting is red.
"""

import pathlib
import tempfile

import fixtures
from synthtwin import (
    contract,
    errors,
    parsing,
    profile,
    reading,
    taxonomy,
)


def _described(
    values: "list[str]", day_first: bool
) -> "tuple[dict, contract.Profile]":
    """One single-column table, described under the declaration or not."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "when.csv", fixtures.single_column_table("when", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(day_first=day_first),
        [],
    )
    written = fixtures.write_profile(folder, "when.json", document)
    return document, contract.load_profile(f"{written}")


def _ambiguous(count: int) -> "list[str]":
    """Slashed cells both readings parse: the day is never above nine."""
    return [
        f"0{1 + place % 9}/0{1 + place % 9}/2024" for place in range(count)
    ]


# -- the evidence decides, and the declaration only breaks a tie ------


def test_without_the_option_nothing_moves() -> None:
    """The reading and the standing remark are what they were."""
    document, _loaded = _described(_ambiguous(99) + ["12/25/2024"], False)
    block = document["columns"][0]
    assert block["format"] == "month-first-date"
    assert block["n_unparsed"] == 0
    assert block["remarks"] == [
        taxonomy.note(taxonomy.REMARK_MONTH_FIRST)
    ]
    assert document["settings"]["day_first"] is False


def test_one_contrary_cell_overrules_the_declaration() -> None:
    """The case the decision names, and the reason it is not a swap.

    Ninety-nine ambiguous slashed cells and one cell only the
    month-first reading can parse. A bare swap would read the whole
    column backwards and count that one cell -- the column's ONLY
    evidence -- as unparsed. Counting both readings first gives the
    column back its own answer.
    """
    document, described = _described(_ambiguous(99) + ["12/25/2024"], True)
    block = document["columns"][0]
    assert block["format"] == "month-first-date"
    assert block["n_unparsed"] == 0
    assert described.columns[0].facts.n_unparsed == 0
    # THE WHOLE SENTENCE, not a fragment of it: contract NF36 fixes
    # every word, and a control that matched fragments would pass on a
    # sentence outside the ratified grammar (review item P4-DATE5-F3).
    assert f"{block['remarks'][0]}" == (
        "read month first, though you asked for day first, because it "
        "parses 100 against 99."
    )


def test_one_contrary_cell_the_other_way_obeys_the_declaration() -> None:
    """...and the same arithmetic, when the evidence agrees."""
    document, _loaded = _described(_ambiguous(99) + ["25/12/2024"], True)
    block = document["columns"][0]
    assert block["format"] == "day-first-date"
    assert block["n_unparsed"] == 0
    assert f"{block['remarks'][0]}" == (
        "read day first, which parses 100 of these values against the "
        "month-first reading's 99."
    )


def test_a_count_tie_is_where_the_declaration_decides() -> None:
    """Nothing in a fully ambiguous column chooses, so the person does."""
    document, _loaded = _described(_ambiguous(120), True)
    block = document["columns"][0]
    assert block["format"] == "day-first-date"
    assert f"{block['remarks'][0]}" == (
        "read day first because you asked for it: both readings parse "
        "120 of these values and the values themselves do not settle "
        "which is right."
    )


def test_a_tie_is_not_the_same_thing_as_full_ambiguity() -> None:
    """Evidence in BOTH directions, at equal counts.

    A column can hold one cell only the day-first reading parses AND
    one cell only the month-first reading parses. The counts tie, so
    the declaration decides the reading -- and the column still
    contradicts itself, which is a different question and gets its own
    clause.
    """
    document, _loaded = _described(
        _ambiguous(98) + ["12/25/2024", "25/12/2024"], True
    )
    block = document["columns"][0]
    assert block["format"] == "day-first-date"
    assert block["n_unparsed"] == 1
    assert f"{block['remarks'][0]}" == (
        "read day first because you asked for it: both readings parse "
        "99 of these values and the values themselves do not settle "
        "which is right. This column contradicts itself: 1 values only "
        "a day-first reading accepts, and 1 only a month-first one."
    )


def test_a_column_decided_by_evidence_can_also_contradict_itself() -> None:
    """The two clauses combine freely, which is why they are two.

    Two cells only the month-first reading parses and one only the
    day-first reading parses: the counts do NOT tie, so the evidence
    decides -- and the second clause still appears, because the column
    points both ways.
    """
    document, _loaded = _described(
        _ambiguous(97) + ["12/25/2024", "12/26/2024", "25/12/2024"], True
    )
    block = document["columns"][0]
    assert block["format"] == "month-first-date"
    assert f"{block['remarks'][0]}" == (
        "read month first, though you asked for day first, because it "
        "parses 99 against 98. This column contradicts itself: 1 values "
        "only a day-first reading accepts, and 2 only a month-first one."
    )


def test_exactly_one_remark_and_it_is_the_evidence_one() -> None:
    """The standing warning is about a guess; nothing here was guessed."""
    for values in (
        _ambiguous(120),
        _ambiguous(99) + ["12/25/2024"],
        _ambiguous(99) + ["25/12/2024"],
    ):
        document, _loaded = _described(values, True)
        remarks = document["columns"][0]["remarks"]
        assert len(remarks) == 1
        assert f"{remarks[0]}".startswith("read ")
        assert "the profile has the month and day the wrong way round" not in (
            f"{remarks[0]}"
        )


def test_the_stamp_members_are_one_pair_too() -> None:
    """The declaration is about a grammar, not about a member."""
    values = [
        f"0{1 + place % 9}/0{1 + place % 9}/2024 08:0{place % 9}"
        for place in range(99)
    ] + ["25/12/2024 08:00"]
    document, _loaded = _described(values, True)
    block = document["columns"][0]
    assert block["format"] == "day-first-datetime"
    assert block["n_unparsed"] == 0
    assert f"{block['remarks'][0]}" == (
        "read day first, which parses 100 of these values against the "
        "month-first reading's 99."
    )


def test_a_column_with_no_slashes_is_untouched_by_the_option() -> None:
    """The declaration reaches the slashed pairs and nothing else."""
    values = [f"2024-{1 + place % 12:02d}-{1 + place % 28:02d}" for place in range(120)]
    document, _loaded = _described(values, True)
    block = document["columns"][0]
    assert block["format"] == "iso-date"
    assert block["remarks"] == []


# -- what the file says it was written under --------------------------


def test_the_declaration_is_recorded_in_the_settings_block() -> None:
    """A description that does not say this cannot be read back."""
    document, described = _described(_ambiguous(120), True)
    assert document["settings"]["day_first"] is True
    assert described.settings.day_first is True


def test_the_version_refusal_names_the_option_and_its_cost() -> None:
    """The suite derives the list from the parser, so forgetting is red."""
    said = errors.profile_version_is_older(4, 5)
    assert "--day-first" in said
    assert "without the --day-first you gave" in said


def test_the_evidence_is_computed_from_the_readings_themselves() -> None:
    """Four counts, and the two `only` ones are the whole point."""
    values = _ambiguous(3) + ["12/25/2024", "25/12/2024"]
    found = taxonomy._slashed_evidence(
        values, ("month-first-date", "day-first-date"), True
    )
    assert found.month_parsed == 4
    assert found.day_parsed == 4
    assert found.month_only == 1
    assert found.day_only == 1
    assert found.used == "day-first-date"
    assert found.reading == taxonomy.READING_DAY_FIRST
    without = taxonomy._slashed_evidence(
        values, ("month-first-date", "day-first-date"), False
    )
    assert without.used == "month-first-date"
    assert without.reading == taxonomy.READING_MONTH_FIRST
    # NG2, the both-readings identity the contract will not let go of:
    # the cells BOTH readings parse are countable two ways and the two
    # answers have to agree.
    assert found.day_parsed - found.day_only == (
        found.month_parsed - found.month_only
    )


def test_the_reading_names_are_words_and_not_format_members() -> None:
    """Contract NF36's fifth argument is a READING, not a member.

    One reading covers two format members, so naming the member would
    make the sentence narrower than it means and would render a date
    column and a stamp column differently where they were decided
    identically.
    """
    assert taxonomy.NOTE_READING_WORDS == ("day-first", "month-first")
    for word in taxonomy.NOTE_READING_WORDS:
        assert word in taxonomy.NOTE_ARGUMENT_WORDS
        assert word not in parsing.DATE_FORMATS


def test_the_pairs_are_the_two_slashed_grammars_and_no_others() -> None:
    """A pair added without a reading is a declaration that lies."""
    assert taxonomy.SLASHED_PAIRS == (
        ("month-first-date", "day-first-date"),
        ("month-first-datetime", "day-first-datetime"),
    )
    for pair in taxonomy.SLASHED_PAIRS:
        for member in pair:
            assert member in parsing.DATE_FORMATS
