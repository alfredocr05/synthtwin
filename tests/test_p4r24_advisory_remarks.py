"""The four advisory remarks (residual R-P4-24, plan L1).

Amendment A-P4-30 cut four remarks out of this phase to finish it, and
priced the cut in as many words: every one of them ROUTES NOTHING, so
nobody is misled -- but "they are not helped either, and a reader who
would have acted on the advice now has to notice the shape themselves".
Residual R-P4-24 held them. They are built here.

WHAT EACH ONE IS, and what "routes nothing" means for it:

* **NF51, the time-band remark** (residual R-P4-9). A `count` column
  whose every value falls in the band a moment in time is counted into
  is told so, with its two ends said as calendar dates. There is no
  declaration to name -- no rule of this package reads a number as a
  time and none can be made to -- so the sentence says the shape, says
  the twin is unaffected, and stops.
* **NF29 argument 9, the recoverable-distribution advice** (amendment
  A-P4-1 item 4) under the TIGHTENED trigger of residual R-P4-16. The
  plan's arithmetic promised a distribution on three column shapes that
  do not publish one, so the producer RE-READS the column over the
  survivors and writes the sentence only where that reading lands on a
  role with a distribution. Both shapes R-P4-16 names have a test here.
* **NF29 argument 8, the clock clause**, which travels with it: the
  competing-readings remark named three readings and stayed silent
  about the fourth.
* **NF25 at arity 2**: the compact-date remark states BOTH counts,
  because eight digits are a date and a number at once and a sentence
  saying only which reading won leaves no way to see how close the
  other came.
* **NF37**: a label column publishing one of the three built-in
  stand-in numbers as a level is told `--missing-value` exists for it.

EVERY ONE OF THEM IS MEASURED AGAINST THE OTHER HALF OF ITS OWN CLAIM.
A remark that names a route is held to that route producing what it
says (`test_the_advice_keeps_its_promise`), and a remark that claims to
move nothing is compared block for block with the same column read
without it. This file is the second kind of test this repository asks
for: not that a sentence appears, but that what it says is true.
"""

import pathlib
import random
import tempfile

import fixtures
from synthtwin import parsing, profile, reading, taxonomy

# Each sentence's own fixed opening. Every test finds its remark by one
# of these rather than by a position in the list: the order remarks are
# raised in is not what this file is about, and an assertion on the
# order would go red for a reason nobody meant.
BAND_OPENING = "every value in this column is a whole number, and every one"
BOTH_COUNTS_OPENING = "the values in this column read both as dates"
STAND_IN_OPENING = "one of the values this column publishes is"
ADVICE_CLAUSE = "run the command again with --missing-value and this"
CLOCK_CLAUSE = "read as a clock time, in a shape synthtwin does not describe"

# The two bands, in the units the column is written in. Worked out the
# way the producer works them out, from the two calendar years, so a
# test that disagreed with the rule would disagree about the years and
# not about a large number somebody typed twice.
_DAY = 24 * 60 * 60
FIRST_SECOND = parsing.days_from_civil(taxonomy.EPOCH_BAND_FROM, 1, 1) * _DAY
LAST_SECOND = parsing.days_from_civil(taxonomy.EPOCH_BAND_UNTIL, 1, 1) * _DAY


def _described(
    values: "list[str]",
    name: str = "thing",
    settings: "taxonomy.Settings | None" = None,
    identifiers: "list[str] | None" = None,
    codes: "list[str] | None" = None,
    measurements: "list[str] | None" = None,
) -> dict:
    """One column, described the way `synthtwin profile` describes it."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table(name, values)
    )
    return profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings() if settings is None else settings,
        [] if identifiers is None else identifiers,
        forced_codes=codes,
        forced_measurements=measurements,
    )


def _said(block: dict, opening: str) -> "str | None":
    for remark in block["remarks"]:
        if opening in remark:
            return remark
    return None


def _every(block: dict, opening: str) -> "list[str]":
    return [remark for remark in block["remarks"] if opening in remark]


# -- NF51: the time band ----------------------------------------------


def _epoch_seconds(count: int = 200, seed: int = 5) -> "list[str]":
    """Whole seconds inside the band, spread over about three years."""
    rng = random.Random(seed)
    low = parsing.days_from_civil(2020, 1, 1) * _DAY
    high = parsing.days_from_civil(2023, 1, 1) * _DAY
    return [str(rng.randint(low, high)) for _each in range(count)]


def test_a_column_of_epoch_seconds_is_told_what_it_looks_like() -> None:
    """THE WHOLE OF WHAT R-P4-9 BUYS, on the column it was opened for."""
    block = _described(_epoch_seconds(), name="event_at")["columns"][0]
    assert block["role"] == taxonomy.ROLE_COUNT
    said = _said(block, BAND_OPENING)
    assert said is not None, block["remarks"]
    assert "seconds from the 1st of January 1970" in said
    assert "read them as plain numbers" in said


def test_the_sentence_says_the_range_as_dates() -> None:
    """The two ends, converted, are what makes the column recognizable.

    A reader holding `1600000000` cannot tell what it is; a reader told
    the column runs from one calendar day to another can. The two days
    are the block's own `min` and `max` said a second way, so the
    assertion is against those rather than against written dates.
    """
    values = _epoch_seconds()
    block = _described(values, name="event_at")["columns"][0]
    said = _said(block, BAND_OPENING)
    assert said is not None
    for end in ("min", "max"):
        number = int(block["percentiles"][end])
        year, month, day = parsing.civil_from_days(number // _DAY)
        assert f"{year:04d}-{month:02d}-{day:02d}" in said, end


def test_a_column_of_epoch_milliseconds_says_milliseconds() -> None:
    """The second band, and the word that tells the two apart.

    The whole use of the sentence is that somebody can convert the
    column, and converting it with the wrong unit is off by a factor of
    a thousand -- so the band the column is in has to be named, not
    implied.
    """
    values = [f"{int(value) * 1000}" for value in _epoch_seconds()]
    block = _described(values, name="event_at")["columns"][0]
    said = _said(block, BAND_OPENING)
    assert said is not None, block["remarks"]
    assert "milliseconds from the 1st of January 1970" in said
    assert "counts seconds from" not in said


def test_the_sentence_says_the_twin_is_unaffected() -> None:
    """The question a reader of a fidelity report asks next.

    Being told the column may be times invites the reader to think the
    twin lost something. It did not: the numeric reading keeps the
    range and the spacing, so the same conversion gives the same span.
    The sentence has to say so or it creates the doubt it exists to
    remove.
    """
    said = _said(_described(_epoch_seconds())["columns"][0], BAND_OPENING)
    assert said is not None
    assert "THIS SENTENCE DECIDES NOTHING" in said
    assert "It changes nothing about your twin either" in said
    assert "over the same span" in said


def test_the_time_band_sentence_moves_no_role_and_no_fact(monkeypatch) -> None:
    """WITH THE SENTENCE AND WITHOUT IT, ONE BLOCK.

    `_epoch_band_reading` is consulted for exactly one purpose, so
    answering it None rebuilds the description as it was before this
    landing. Everything but `remarks` must be identical, and `remarks`
    must differ by this one sentence and nothing else.
    """
    values = _epoch_seconds()
    with_it = _described(values, name="event_at")["columns"][0]
    monkeypatch.setattr(
        taxonomy, "_epoch_band_reading", lambda _cells: None
    )
    without = _described(values, name="event_at")["columns"][0]

    said = _said(with_it, BAND_OPENING)
    assert said is not None
    assert _said(without, BAND_OPENING) is None
    assert with_it["role"] == without["role"]
    for key in sorted(set(with_it) | set(without)):
        if key == "remarks":
            continue
        assert with_it[key] == without[key], key
    kept = [line for line in with_it["remarks"] if line != said]
    assert kept == list(without["remarks"])


def test_the_sentence_is_exactly_the_form_and_carries_no_cell() -> None:
    """Seven whole numbers, and not one spelling of the column."""
    values = _epoch_seconds()
    block = _described(values)["columns"][0]
    said = _said(block, BAND_OPENING)
    assert said is not None
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_EPOCH_BAND] == 7
    first = parsing.civil_from_days(int(block["percentiles"]["min"]) // _DAY)
    last = parsing.civil_from_days(int(block["percentiles"]["max"]) // _DAY)
    assert said == taxonomy.rendered(
        taxonomy.REMARK_EPOCH_BAND,
        (taxonomy.EPOCH_BAND_SECONDS,) + first + last,
    )
    for value in set(values):
        assert value not in said, value


def test_an_ordinary_count_column_hears_nothing() -> None:
    """Ages, tallies and row counts must stay quiet.

    This is the test the band's lower end exists for. Zero is the 1st
    of January 1970, so a band starting there would put this sentence
    on nearly every column of whole numbers a table holds.
    """
    ages = fixtures.numbers(seed=3, count=200, low=18, high=95)
    block = _described(ages, name="age")["columns"][0]
    assert block["role"] == taxonomy.ROLE_COUNT
    assert _said(block, BAND_OPENING) is None


def test_a_column_holding_A_FEW_epoch_shaped_values_hears_nothing() -> None:
    """Two epoch-shaped values among ordinary counts say nothing.

    THIS TEST DOES NOT PIN THE WALK OVER EVERY VALUE, AND SAYING SO IS
    the point. It was written to, under the name "a column whose ENDS
    are in the band", and the mutation that reads `min` and `max`
    instead of walking survived it -- because a band is one interval,
    so on an all-whole role the two ends answer the same question. The
    shape the old name described cannot be built. What this really
    pins is the band's LOWER end doing its job: the smallest value here
    is an ordinary count, so the column is out of the band and quiet.
    """
    values = _epoch_seconds(count=2) + fixtures.numbers(
        seed=4, count=198, low=1, high=500
    )
    block = _described(values, name="event_at")["columns"][0]
    assert block["role"] == taxonomy.ROLE_COUNT
    assert _said(block, BAND_OPENING) is None


def test_a_column_of_fractions_in_the_band_hears_nothing() -> None:
    """`continuous` is not this remark's role, and the reason is real.

    A moment in time counted into a whole number is a whole number. A
    column of fractions that happen to sit in the band is a column of
    measurements, and telling its owner it might be times would be the
    guess this package refuses to make from values.
    """
    rng = random.Random(6)
    values = [
        f"{rng.randint(FIRST_SECOND, LAST_SECOND - 1)}.5" for _each in range(200)
    ]
    block = _described(values, name="reading")["columns"][0]
    assert block["role"] == taxonomy.ROLE_CONTINUOUS
    assert _said(block, BAND_OPENING) is None


def test_a_column_just_below_the_band_hears_nothing() -> None:
    """The band's own edge, walked from the outside.

    One value one below the band's first number is enough, which is
    what "every value" means. Asserted at the edge rather than far from
    it, because an off-by-one in the comparison is exactly what a test
    far from the edge would miss.
    """
    inside = [str(FIRST_SECOND + index) for index in range(200)]
    assert _said(_described(inside)["columns"][0], BAND_OPENING) is not None
    outside = [str(FIRST_SECOND - 1)] + inside[1:]
    assert _said(_described(outside)["columns"][0], BAND_OPENING) is None


# -- NF25: both counts ------------------------------------------------


def _compact_days(count: int = 300) -> "list[str]":
    """`YYYYMMDD` cells: a date and a whole number at the same time."""
    built: "list[str]" = []
    for month in range(1, 13):
        for day in range(1, 26):
            built += [f"2024{month:02d}{day:02d}"]
    return built[:count]


def test_the_compact_date_column_states_both_counts() -> None:
    """A-P4-30 item 1's second widening, built.

    The compact family is where the two readings compete most often,
    and the sentence used to say only which one won.
    """
    values = _compact_days()
    block = _described(values, name="visit")["columns"][0]
    assert block["role"] == taxonomy.ROLE_DATETIME
    said = _said(block, BOTH_COUNTS_OPENING)
    assert said is not None, block["remarks"]
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_DATES_ALSO_NUMBERS] == 2
    assert said == taxonomy.rendered(
        taxonomy.REMARK_DATES_ALSO_NUMBERS, (len(values), len(values))
    )


def test_the_two_counts_are_this_column_s_own_and_can_differ() -> None:
    """They are two readings' counts, not one count written twice.

    A cell that reads as a date and not as a number moves one of them
    and not the other, so a rendering that had passed the same number
    twice would be wrong here. `2024-03-17` is a date under the ISO
    member and no number at all.
    """
    values = [f"2024-03-{day:02d}" for day in range(1, 29)] * 8
    block = _described(values, name="visit")["columns"][0]
    said = _said(block, BOTH_COUNTS_OPENING)
    assert said is None, "an ISO column reads as no number and must stay quiet"


def test_the_two_counts_are_measured_apart() -> None:
    """THE TEST THAT SEPARATES TWO ARGUMENTS FROM ONE WRITTEN TWICE.

    On an ordinary compact-date column both readings reach every cell,
    so a producer passing the same number twice would render the same
    sentence and no assertion could tell. `99999999` is eight digits
    and a whole number and no calendar day at all, so it moves the
    numeric count and not the date count -- and the two arguments come
    out different.
    """
    values = _compact_days() + ["99999999", "88888888"]
    block = _described(values, name="visit")["columns"][0]
    assert block["role"] == taxonomy.ROLE_DATETIME
    said = _said(block, BOTH_COUNTS_OPENING)
    assert said is not None, block["remarks"]
    assert said == taxonomy.rendered(
        taxonomy.REMARK_DATES_ALSO_NUMBERS, (300, 302)
    ), said
    assert "300 of them read as dates and 302 of them are written" in said


def test_a_date_column_that_reads_as_no_number_stays_quiet() -> None:
    """The trigger is unchanged: dates AND numbers, or nothing."""
    values = [f"17/03/{1990 + index % 30}" for index in range(200)]
    block = _described(values, name="visit")["columns"][0]
    assert block["role"] == taxonomy.ROLE_DATETIME
    assert _said(block, BOTH_COUNTS_OPENING) is None


# -- NF29 argument 8: the clock clause --------------------------------


def _declined_with_clocks(clocks: int = 80, others: int = 120) -> "list[str]":
    """A column no rule claims, part of it written as clock times."""
    rng = random.Random(9)
    times = [
        f"{rng.randint(0, 23):02d}:{rng.randint(0, 59):02d}"
        for _each in range(clocks)
    ]
    return times + [f"note-{index}" for index in range(others)]


def test_a_declined_column_says_how_far_the_clock_reading_got() -> None:
    """The fourth reading, which this remark used to be silent about.

    The competing-readings remark named the numeric reading, the date
    reading and the affix reading. A column of clock times in a shape
    this version does not describe was told nothing fitted it and never
    told which reading came closest.
    """
    values = _declined_with_clocks()
    block = _described(values, name="taken_at")["columns"][0]
    assert block["role"] == taxonomy.ROLE_TEXT
    said = _said(block, CLOCK_CLAUSE)
    assert said is not None, block["remarks"]
    assert "80 of these values read as a clock time" in said


def test_a_declined_column_with_no_clock_cells_says_nothing_about_one() -> None:
    """A clause naming a reading that reached nothing says something happened.

    The words are drawn letter by letter so that no two of them share a
    prefix or a suffix. `note-1` through `note-200` would take the
    affixed role instead and never reach the remark at all.
    """
    rng = random.Random(11)
    letters = "abcdefghijklmnopqrstuvwxyz"
    values = [
        "".join(rng.choice(letters) for _each in range(rng.randint(4, 9)))
        for _each in range(200)
    ]
    block = _described(values, name="comment")["columns"][0]
    assert block["role"] == taxonomy.ROLE_TEXT
    assert _said(block, CLOCK_CLAUSE) is None


def test_the_clock_count_is_the_readings_own_count(monkeypatch) -> None:
    """The clause states `clock_reach`, not a second measurement of it.

    Two places computing one quantity is the shape four of six items
    in review round P4-G3-R1 took. Replacing the one function moves the
    sentence, which is what says the sentence reads it.
    """
    values = _declined_with_clocks()
    monkeypatch.setattr(taxonomy, "clock_reach", lambda _cells: 7)
    block = _described(values, name="taken_at")["columns"][0]
    said = _said(block, CLOCK_CLAUSE)
    assert said is not None
    assert "7 of these values read as a clock time" in said


# -- NF29 argument 9: the recoverable-distribution advice --------------

GAP_WORDS = (
    "not recorded",
    "refused",
    "pending",
    "unknown at intake",
    "not applicable",
)


def _recoverable(numbers: "list[str]") -> "list[str]":
    """Numbers beside a few repeated words that are not numbers."""
    return numbers + [word for word in GAP_WORDS for _each in range(2)]


def _spread_numbers(count: int = 190, seed: int = 9) -> "list[str]":
    rng = random.Random(seed)
    found = sorted({f"{rng.uniform(1, 100):.2f}" for _each in range(count * 2)})
    return found[:count]


def test_the_declined_column_is_told_one_declaration_would_recover_it() -> None:
    """A-P4-1 item 4, built. The count is the rows those words cover."""
    block = _described(_recoverable(_spread_numbers()), name="dose")["columns"][0]
    assert block["role"] == taxonomy.ROLE_TEXT
    said = _said(block, ADVICE_CLAUSE)
    assert said is not None, block["remarks"]
    assert "10 more are written one of a few ways" in said
    assert "If those 10 mean 'no value'" in said


def test_the_advice_keeps_its_promise() -> None:
    """THE OTHER HALF OF THE CLAIM, AND THE POINT OF R-P4-16.

    The sentence tells its reader that `--missing-value` will get "this
    column's distribution described". That is a promise, so it is run:
    the same column, described again with exactly those words declared,
    has to come out in a role that publishes a distribution.

    A remark whose route was never run is a remark nobody checked, and
    the plan's original trigger promised this on three column shapes
    that do not publish one.
    """
    values = _recoverable(_spread_numbers())
    assert _said(_described(values, name="dose")["columns"][0], ADVICE_CLAUSE)
    declared = _described(
        values,
        name="dose",
        settings=taxonomy.Settings(declared_missing_values=GAP_WORDS),
    )["columns"][0]
    assert declared["role"] in (
        taxonomy.ROLE_COUNT,
        taxonomy.ROLE_CONTINUOUS,
        taxonomy.ROLE_AFFIXED,
    )
    assert "mean" in declared and "percentiles" in declared


def test_no_advice_where_the_survivors_hold_no_number_R_P4_16() -> None:
    """R-P4-16's FIRST shape, and the plan's own trigger fires on it.

    Survivors that clear the parse line on cells that merely LOOK
    numeric, without one of them being a number this format can hold,
    take `numeric_unrepresentable` and publish no statistic at all --
    so the advice would promise a distribution the re-run does not
    describe. The arithmetic trigger cannot tell; the re-run can.
    """
    values = _recoverable([f"1e{400 + index}" for index in range(190)])
    block = _described(values, name="dose")["columns"][0]
    assert block["role"] == taxonomy.ROLE_TEXT
    assert _said(block, ADVICE_CLAUSE) is None, block["remarks"]
    declared = _described(
        values,
        name="dose",
        settings=taxonomy.Settings(declared_missing_values=GAP_WORDS),
    )["columns"][0]
    assert declared["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert "mean" not in declared


def test_no_advice_where_the_survivors_collapse_to_two_values_R_P4_16() -> None:
    """R-P4-16's SECOND shape: `constant` and `binary` claim them first.

    Two numbers repeated are a set of two labels, whatever else they
    are, and that role publishes levels and counts rather than a
    distribution. The advice must not promise one.
    """
    values = _recoverable(["12.5"] * 95 + ["13.5"] * 95)
    block = _described(values, name="dose")["columns"][0]
    assert block["role"] != taxonomy.ROLE_TEXT or _said(
        block, ADVICE_CLAUSE
    ) is None
    declared = _described(
        values,
        name="dose",
        settings=taxonomy.Settings(declared_missing_values=GAP_WORDS),
    )["columns"][0]
    assert declared["role"] == taxonomy.ROLE_BINARY
    assert "mean" not in declared


def test_no_advice_under_a_declared_code_column() -> None:
    """`--code` silences every rule that reads a cell as a number.

    So no `--missing-value` can give such a column a distribution, and
    a sentence promising one would send its reader to a command that
    cannot help. The declaration is asked for exactly this reason.
    """
    values = _recoverable(_spread_numbers())
    block = _described(values, name="dose", codes=["dose"])["columns"][0]
    assert _said(block, ADVICE_CLAUSE) is None, block["remarks"]


def test_no_advice_where_the_gap_words_never_repeat() -> None:
    """"A few ways that repeat" has to be true of the column.

    At the default floor of one an all-different word would clear the
    floor, so a hundred one-off spellings would be called a few
    repeated ones. The rule asks for a spelling shared by at least two
    rows, and this is the column that separates the two readings.
    """
    once = [f"note-{index}" for index in range(10)]
    block = _described(_spread_numbers() + once, name="dose")["columns"][0]
    assert block["role"] == taxonomy.ROLE_TEXT
    assert _said(block, ADVICE_CLAUSE) is None, block["remarks"]


def test_no_advice_where_the_gaps_wear_more_ways_than_a_few() -> None:
    """The other half of the same sentence: "a few WAYS".

    A column whose gaps are written fifty different ways is not written
    "one of a few ways", and the categorical ceiling is this document's
    own line for a small set of values in a column. Above it the advice
    stays quiet.
    """
    many = [word for index in range(50) for word in (f"gap-{index}",) * 2]
    block = _described(_spread_numbers(count=100) + many, name="dose")["columns"][0]
    assert block["role"] == taxonomy.ROLE_TEXT
    assert _said(block, ADVICE_CLAUSE) is None, block["remarks"]


def test_the_advice_asks_the_reading_and_not_the_arithmetic(monkeypatch) -> None:
    """The trigger is the RE-RUN, and this is what says so.

    R-P4-16's whole point is that counting is not enough. Making the
    re-read answer with a role that publishes nothing must silence the
    advice on a column whose counts are unchanged -- so a producer that
    had kept the arithmetic trigger fails here.
    """
    values = _recoverable(_spread_numbers())
    assert _said(_described(values, name="dose")["columns"][0], ADVICE_CLAUSE)

    real = taxonomy._decide

    def declined(cells, forced_identifier, *rest, **named):
        verdict = real(cells, forced_identifier, *rest, **named)
        if named.get("probing"):
            return taxonomy.dataclasses.replace(
                verdict, role=taxonomy.ROLE_TEXT
            )
        return verdict

    monkeypatch.setattr(taxonomy, "_decide", declined)
    block = _described(values, name="dose")["columns"][0]
    assert _said(block, ADVICE_CLAUSE) is None, block["remarks"]


def test_the_two_new_clauses_compose_the_way_the_contract_says() -> None:
    """4.5.1's composition rule, over all four combinations.

    A CLAUSE IS WRITTEN IF AND ONLY IF ITS OWN ARGUMENT IS NONZERO, in
    argument order, each ending in a full stop and separated from the
    next by ONE space, with a full stop and one space after what came
    before. The first build of this wrote `describe.. 9 more`, because
    two functions each prefixed their own full stop -- so the join is
    asserted here rather than trusted.
    """
    numbers = (taxonomy.SAID_WRITTEN_AS_NUMBERS, (3, 9))
    dates = (taxonomy.SAID_READ_AS_DATES, (2, taxonomy.NOTE_ARGUMENT_WORDS[0]))

    def written(clock: int, advice: int) -> str:
        return taxonomy.rendered(
            taxonomy.REMARK_NO_READING_FITS,
            (numbers, dates, 9, 4, 5, 6, 7, clock, advice),
        )

    base = written(0, 0)
    assert ".." not in written(8, 9)
    assert "  " not in written(8, 9)
    assert not base.endswith("."), "the base sentence carries no terminal stop"
    assert written(8, 0) == base + ". 8 of these values read as a clock " \
        "time, in a shape synthtwin does not describe."
    assert written(0, 9).startswith(base + ". 9 more are written")
    assert written(8, 9) == (
        written(8, 0) + " " + written(0, 9)[len(base) + 2:]
    )


# -- NF37: a stand-in number published as a label ----------------------


def test_a_label_column_publishing_a_stand_in_is_told() -> None:
    """A-P4-30 item 1's third widening, built.

    Stand-in judging runs only above the numeric parse line, so a
    column of labels publishes `-999` as an ordinary level with an
    ordinary count, and nothing said that the same number one column
    over would have been read as a gap.
    """
    values = ["A"] * 80 + ["B"] * 60 + ["-999"] * 60
    block = _described(values, name="grade")["columns"][0]
    assert block["role"] == taxonomy.ROLE_CATEGORICAL
    said = _said(block, STAND_IN_OPENING)
    assert said is not None, block["remarks"]
    assert "--missing-value -999" in said
    assert said == taxonomy.rendered(taxonomy.REMARK_LABEL_IS_A_STAND_IN, (2,))
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_LABEL_IS_A_STAND_IN] == 1


def test_every_label_role_carries_it() -> None:
    """All four roles that publish levels, asserted together.

    "Every label role suppresses levels; whether it does is a fact
    about the FLOOR and not about the role" is the correction the shape
    census took when it stood on one role. The same argument reaches
    here: whether a column publishes `-999` as a label is a fact about
    its values, and a rule wired into three of the four would be silent
    on the fourth for no reason a reader could find.
    """
    constant = _described(["-999"] * 200, name="grade")["columns"][0]
    binary = _described(["A"] * 100 + ["-999"] * 100, name="grade")["columns"][0]
    categorical = _described(
        ["A"] * 80 + ["B"] * 60 + ["-999"] * 60, name="grade"
    )["columns"][0]
    long_tail = _described(
        [f"code-{index}" for index in range(120)]
        + ["-999"] * 40
        + ["x"] * 40,
        name="code",
    )["columns"][0]
    assert constant["role"] == taxonomy.ROLE_CONSTANT
    assert binary["role"] == taxonomy.ROLE_BINARY
    assert categorical["role"] == taxonomy.ROLE_CATEGORICAL
    assert long_tail["role"] == taxonomy.ROLE_LONG_TAIL
    for block in (constant, binary, categorical, long_tail):
        assert _said(block, STAND_IN_OPENING) is not None, block["role"]


def test_all_three_built_in_numbers_are_reached() -> None:
    """The list is three long and the remark names the one it found."""
    for place, candidate in enumerate(parsing.NUMERIC_SENTINELS, start=1):
        spelling = f"{int(candidate)}"
        values = ["A"] * 120 + [spelling] * 80
        block = _described(values, name="grade")["columns"][0]
        said = _said(block, STAND_IN_OPENING)
        assert said is not None, spelling
        assert said == taxonomy.rendered(
            taxonomy.REMARK_LABEL_IS_A_STAND_IN, (place,)
        )
        assert f"is {spelling}," in said


def test_a_column_publishing_two_of_them_is_told_about_both() -> None:
    """Two levels, two sentences, in this package's own order.

    A rule that stopped at the first would leave a column publishing
    both `-999` and `9999` half explained, and the half it left out is
    the one the reader has not thought of.
    """
    values = ["A"] * 80 + ["-999"] * 60 + ["9999"] * 60
    block = _described(values, name="grade")["columns"][0]
    said = _every(block, STAND_IN_OPENING)
    assert len(said) == 2, said
    assert said[0] == taxonomy.rendered(taxonomy.REMARK_LABEL_IS_A_STAND_IN, (2,))
    assert said[1] == taxonomy.rendered(taxonomy.REMARK_LABEL_IS_A_STAND_IN, (3,))


def test_the_match_is_by_number_and_not_by_spelling() -> None:
    """`-999.0` is the same number as `-999`, and the same hazard.

    Every declaration in this package is matched by NUMBER where it
    reads as one, and a remark matched on the text instead would be
    silent on the column that spells it with a fraction -- which is
    exactly the column whose owner has not noticed.
    """
    values = ["A"] * 120 + ["-999.00"] * 80
    block = _described(values, name="grade")["columns"][0]
    said = _said(block, STAND_IN_OPENING)
    assert said is not None, block["remarks"]
    assert "is -999," in said, "the sentence names this package's own spelling"


def test_a_level_the_floor_held_back_is_not_described() -> None:
    """The sentence says "one of the values this column PUBLISHES".

    A level below the floor is not published, so a remark describing it
    would name a value the same document promises to withhold -- the
    contradiction review item P1-R1-F10 found one field over.
    """
    values = ["A"] * 130 + ["B"] * 65 + ["-999"] * 5
    block = _described(
        values, name="grade", settings=taxonomy.Settings(small_cell_floor=11)
    )["columns"][0]
    assert block["role"] == taxonomy.ROLE_CATEGORICAL
    assert block["suppressed_levels"] == 1
    assert _said(block, STAND_IN_OPENING) is None, block["remarks"]


def test_a_numeric_column_holding_the_same_number_hears_nothing() -> None:
    """There the stand-in rule already ran and published its verdict.

    The remark exists for the column the judgement never reached. On a
    numeric column it would be a second account of a decision the
    document already carries in `sentinel_verdicts`.
    """
    values = fixtures.numbers(seed=8, count=180, low=50, high=70) + ["-999"] * 20
    block = _described(values, name="dose")["columns"][0]
    assert block["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS)
    assert _said(block, STAND_IN_OPENING) is None


def test_the_stand_in_sentence_moves_no_role_and_no_fact(monkeypatch) -> None:
    """WITH THE SENTENCE AND WITHOUT IT, ONE BLOCK."""
    values = ["A"] * 80 + ["B"] * 60 + ["-999"] * 60
    with_it = _described(values, name="grade")["columns"][0]
    monkeypatch.setattr(
        taxonomy, "_stand_in_level_remarks", lambda _levels: []
    )
    without = _described(values, name="grade")["columns"][0]

    said = _said(with_it, STAND_IN_OPENING)
    assert said is not None
    assert _said(without, STAND_IN_OPENING) is None
    assert with_it["role"] == without["role"]
    for key in sorted(set(with_it) | set(without)):
        if key == "remarks":
            continue
        assert with_it[key] == without[key], key
    kept = [line for line in with_it["remarks"] if line != said]
    assert kept == list(without["remarks"])


def test_the_two_lookup_tables_refuse_a_position_they_do_not_hold() -> None:
    """Contract 4.5.2's NG13, and NF51's band table beside it.

    Both forms take a POSITION in a closed list rather than a value, so
    a position the list does not hold has no rendering -- and the right
    answer is a refusal, not a borrowed one. The publication guard
    rebuilds every sentence through `rendered`, so this is where such
    an argument is stopped.
    """
    for form, held in (
        (taxonomy.REMARK_LABEL_IS_A_STAND_IN, len(parsing.NUMERIC_SENTINELS)),
        (taxonomy.REMARK_EPOCH_BAND, 2),
    ):
        rest = (2020, 1, 1, 2021, 1, 1)[: taxonomy.NOTE_ARITY[form] - 1]
        for place in (0, held + 1):
            try:
                taxonomy.rendered(form, (place,) + rest)
            except ValueError:
                continue
            raise AssertionError(f"{form} rendered position {place}")
        for place in range(1, held + 1):
            assert len(taxonomy.rendered(form, (place,) + rest)) > 20


def test_no_sentence_of_these_four_carries_a_value_of_the_column() -> None:
    """The one rule none of them may break, asserted over all four.

    Every argument of every one of these forms is a whole number, so no
    spelling of anybody's table can reach a published sentence through
    them. The `-999` in NF37 is this package's own number, written from
    a POSITION, and the test above pins that it is matched by number
    rather than carried as text.
    """
    for form in (
        taxonomy.REMARK_EPOCH_BAND,
        taxonomy.REMARK_LABEL_IS_A_STAND_IN,
        taxonomy.REMARK_DATES_ALSO_NUMBERS,
        taxonomy.REMARK_NO_READING_FITS,
    ):
        for place in range(taxonomy.NOTE_ARITY[form]):
            assert not taxonomy.takes_a_bound_affix(form, place), (form, place)
