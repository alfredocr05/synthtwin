"""The four advisory remarks (residual R-P4-24, plan L1).

Amendment A-P4-30 cut four remarks out of this phase to finish it, and
priced the cut in as many words: every one of them ROUTES NOTHING, so
nobody is misled -- but "they are not helped either, and a reader who
would have acted on the advice now has to notice the shape themselves".
Residual R-P4-24 held them. They are built here.

WHAT EACH ONE IS, and what "routes nothing" means for it:

* **NF51, the time-band remark** (residual R-P4-9), RETIRED FROM THE
  PRODUCER by landing R4 (plan P4-D384). A column of numbers lying
  where a counting system writes dates is now told so in question Q3's
  own words (NF113, NF114) and asked, and `--date-count` reads it as
  the dates it counts; the tests below hold those words to the same
  two claims NF51 was held to -- the years are the published edges,
  and the sentences move nothing.
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
import tail_rule
from synthtwin import date_counts, parsing, profile, reading, taxonomy

# Each sentence's own fixed opening. Every test finds its remark by one
# of these rather than by a position in the list: the order remarks are
# raised in is not what this file is about, and an assertion on the
# order would go red for a reason nobody meant.
BOTH_COUNTS_OPENING = "the values in this column read both as dates"
STAND_IN_OPENING = "one of the values this column publishes is"
ADVICE_CLAUSE = "run the command again with --missing-value and this"
CLOCK_CLAUSE = "read as a clock time, in a shape synthtwin does not describe"

_DAY = 24 * 60 * 60


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


# -- NF113 and NF114: question Q3's own words, in NF51's place ----------
#
# NF51 told a column of whole numbers in two bands from 1970 that it
# looked like moments, and that nothing about its twin changed. Landing
# R4 (plan P4-D384) retired it from the producer: it read every band
# from 1970, so SAS seconds of 2016 to 2025 were said to run from 2026
# to 2035, and the twin DOES lose the calendar -- the weekday and the
# time of day -- a column of numbers keeps. What stands in its place is
# the question's own words, NF113, and one NF114 per counting system
# offered with the years the block's own published edges name in it.


def _epoch_seconds(count: int = 200, seed: int = 5) -> "list[str]":
    """Whole seconds from 1970, spread over about three years of one decade."""
    rng = random.Random(seed)
    low = parsing.days_from_civil(2020, 1, 1) * _DAY
    high = parsing.days_from_civil(2023, 1, 1) * _DAY
    return [str(rng.randint(low, high)) for _each in range(count)]


def _of_form(block: dict, form: str) -> list:
    return [remark for remark in block["remarks"] if remark.form == form]


def _members(block: dict) -> "list[str]":
    return [
        remark.arguments[0]
        for remark in _of_form(block, taxonomy.REMARK_READ_AS_COUNTED_DATES)
    ]


def test_a_column_of_epoch_seconds_is_told_what_it_may_be() -> None:
    """THE WHOLE OF WHAT R-P4-9 BOUGHT, said as the question Q3 asks it.

    Both systems counting seconds read this column inside the band, so
    both are offered: from 1970 it runs over 2020 to 2022, and from 1960
    -- SAS's and Stata's day -- over 2030 to 2032. Telling them apart is
    the person's to do; NF51 named one and was wrong about the other.
    """
    block = _described(_epoch_seconds(), name="event_at")["columns"][0]
    assert block["role"] == taxonomy.ROLE_COUNT
    forms = [remark.form for remark in block["remarks"]]
    assert taxonomy.REMARK_EPOCH_BAND not in forms
    asked = _of_form(block, taxonomy.REMARK_NUMBERS_COULD_BE_DATES)
    assert len(asked) == 1, block["remarks"]
    assert asked[0].arguments[0] == date_counts.RULE_BAND
    assert _members(block) == ["seconds-since-1960", "seconds-since-1970"]
    assert "--date-count NAME SYSTEM" in asked[0]


def test_each_reading_says_the_years_of_the_published_edges() -> None:
    """The two years are the two edges the BLOCK publishes, read in each system.

    Plan P4-D345's rule, carried over from NF51: an advisory remark may
    not outlive the facts it quotes, and the tail rule withholds the
    column's own smallest and largest number (contract 6.7a), so each
    end is the boundary rung that stands in its place. The rungs are
    read here through `tests/tail_rule.py` and the years worked out from
    each system's own first day with `parsing`, so this holds by working
    the rule out and not by agreeing with the producer.
    """
    values = _epoch_seconds()
    block = _described(values, name="event_at")["columns"][0]
    assert block["percentiles"]["min"] is None
    assert block["percentiles"]["max"] is None
    percent = tail_rule.percent_of(len(values), 11)
    assert percent is not None
    edges = (
        tail_rule.rung_of(block, percent),
        tail_rule.rung_of(block, 100 - percent),
    )
    first_days = {
        "seconds-since-1960": parsing.days_from_civil(1960, 1, 1),
        "seconds-since-1970": parsing.days_from_civil(1970, 1, 1),
    }
    readings = _of_form(block, taxonomy.REMARK_READ_AS_COUNTED_DATES)
    assert len(readings) == 2
    for remark in readings:
        member, first, last = remark.arguments
        owed = tuple(
            parsing.civil_from_days(first_days[member] + int(edge) // _DAY)[0]
            for edge in edges
        )
        assert (first, last) == owed, (member, first, last, owed)
        assert f"this column runs from {first} to {last}" in remark


def test_a_column_of_epoch_milliseconds_is_offered_milliseconds() -> None:
    """The unit, named: converting with the wrong one is off a thousandfold."""
    values = [f"{int(value) * 1000}" for value in _epoch_seconds()]
    block = _described(values, name="event_at")["columns"][0]
    assert _members(block) == [
        "milliseconds-since-1960",
        "milliseconds-since-1970",
    ]
    said = " ".join(_of_form(block, taxonomy.REMARK_READ_AS_COUNTED_DATES))
    assert "milliseconds from the start of 1 January 1970" in said
    assert "read as seconds from" not in said


def test_the_sentence_says_what_the_twin_loses_and_how_to_keep_it() -> None:
    """NF51's "it changes nothing about your twin" was false, and is gone.

    A column of numbers keeps the numbers' spread; the day of the week
    and the time of day each value falls on come back only when the
    column is read as dates, which the sentence says, with the two ways
    to ask for it.
    """
    block = _described(_epoch_seconds())["columns"][0]
    said = " ".join(block["remarks"])
    assert "changes nothing about your twin" not in said
    assert "THIS SENTENCE DECIDES NOTHING" not in said
    (asked,) = _of_form(block, taxonomy.REMARK_NUMBERS_COULD_BE_DATES)
    assert "which day of the week and which time of day" in asked
    assert "answer the question about this column in the questions file" in asked
    assert "--date-count NAME SYSTEM" in asked


def test_the_question_moves_no_role_and_no_fact(monkeypatch) -> None:
    """WITH THE SENTENCES AND WITHOUT THEM, ONE BLOCK.

    `_date_count_remarks` is consulted for exactly one purpose, so
    answering it with nothing rebuilds the description without question
    Q3's words. Everything but `remarks` must be identical, and `remarks`
    must differ by those sentences and nothing else: asking is not
    reading, and the column stays numbers until the person answers.
    """
    values = _epoch_seconds()
    with_it = _described(values, name="event_at")["columns"][0]
    monkeypatch.setattr(
        taxonomy, "_date_count_remarks", lambda _cells, _details: []
    )
    without = _described(values, name="event_at")["columns"][0]

    q3_forms = (
        taxonomy.REMARK_NUMBERS_COULD_BE_DATES,
        taxonomy.REMARK_READ_AS_COUNTED_DATES,
    )
    assert _of_form(with_it, q3_forms[0])
    assert not _of_form(without, q3_forms[0])
    assert not _of_form(without, q3_forms[1])
    assert with_it["role"] == without["role"]
    for key in sorted(set(with_it) | set(without)):
        if key == "remarks":
            continue
        assert with_it[key] == without[key], key
    kept = [line for line in with_it["remarks"] if line.form not in q3_forms]
    assert kept == list(without["remarks"])


def test_the_sentences_are_exactly_their_forms_and_carry_no_cell() -> None:
    """Six words of this package's own, then a system and two years.

    NF113's arguments are the rule's word and five set-aside slots, each
    a word of a closed list; NF114's are a system's word and two years.
    No spelling of the column reaches either.
    """
    values = _epoch_seconds()
    block = _described(values)["columns"][0]
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_NUMBERS_COULD_BE_DATES] == 6
    assert taxonomy.NOTE_ARITY[taxonomy.REMARK_READ_AS_COUNTED_DATES] == 3
    said = _of_form(block, taxonomy.REMARK_NUMBERS_COULD_BE_DATES)
    said += _of_form(block, taxonomy.REMARK_READ_AS_COUNTED_DATES)
    assert len(said) == 3
    for remark in said:
        assert remark == taxonomy.rendered(remark.form, remark.arguments)
        for word in remark.arguments:
            if isinstance(word, str):
                assert word in taxonomy.NOTE_ARGUMENT_WORDS, word
        for value in set(values):
            assert value not in remark, value
    assert said[0].arguments[1:] == (date_counts.ASIDE_NONE,) * 5


def test_an_ordinary_count_column_hears_nothing() -> None:
    """Ages, tallies and row counts must stay quiet.

    This is the test the band's lower end exists for. Nought is the 1st
    of January 1970, so a band starting there would put this question on
    nearly every column of whole numbers a table holds.
    """
    ages = fixtures.numbers(seed=3, count=200, low=18, high=95)
    block = _described(ages, name="age")["columns"][0]
    assert block["role"] == taxonomy.ROLE_COUNT
    assert not _of_form(block, taxonomy.REMARK_NUMBERS_COULD_BE_DATES)
    assert not _of_form(block, taxonomy.REMARK_READ_AS_COUNTED_DATES)


def test_a_column_holding_A_FEW_epoch_shaped_values_hears_nothing() -> None:
    """Two epoch-shaped values among ordinary counts ask nothing.

    The rest beside the set-aside numbers must lie in the band but for
    one cell in a thousand (one at least), so two strays among two
    hundred ordinary counts are far from enough -- and the published
    median, asked before anything is sorted, already says so.
    """
    values = _epoch_seconds(count=2) + fixtures.numbers(
        seed=4, count=198, low=1, high=500
    )
    block = _described(values, name="event_at")["columns"][0]
    assert block["role"] == taxonomy.ROLE_COUNT
    assert not _of_form(block, taxonomy.REMARK_NUMBERS_COULD_BE_DATES)


def test_a_column_of_fractions_in_one_decade_of_the_band_is_asked() -> None:
    """A count with a fraction is a moment too, so NF51's exclusion is gone.

    `45386.5` is noon in Excel's count of days and `1600000000.25` a
    quarter of a second in Unix's; a column of such numbers read as
    measurements keeps them as measurements, which is the answer Enter
    gives. Whole figures of one width, inside the band, ask.
    """
    rng = random.Random(6)
    low = parsing.days_from_civil(2016, 1, 1) * _DAY
    high = parsing.days_from_civil(2025, 1, 1) * _DAY
    values = [f"{rng.randint(low, high - 1)}.5" for _each in range(200)]
    block = _described(values, name="reading")["columns"][0]
    assert block["role"] == taxonomy.ROLE_CONTINUOUS
    (asked,) = _of_form(block, taxonomy.REMARK_NUMBERS_COULD_BE_DATES)
    assert asked.arguments[0] == date_counts.RULE_BAND
    assert _members(block) == ["seconds-since-1960", "seconds-since-1970"]


def test_one_value_outside_the_band_is_let_stand_and_two_are_not() -> None:
    """The band's own edge, walked from the outside.

    One cell in a thousand -- one at least -- may stray outside the band
    (the R4 design review, item 1: one keying slip silences no
    question), so on two hundred cells one value just below the band's
    first second is let stand and two are not. The band's first second
    is inside it: swapping one of the two strays for that very number
    asks again. Asserted at the edge rather than far from it, because an
    off-by-one in the comparison is what a test far from it would miss.
    """
    low, _high = date_counts.band("seconds-since-1970", date_counts.NARROW_FROM)
    first = int(low)
    assert first == parsing.days_from_civil(1990, 1, 1) * _DAY
    inside = [str(first + index * 7919) for index in range(199)]

    def asked(values: "list[str]") -> bool:
        block = _described(values, name="event_at")["columns"][0]
        return bool(_of_form(block, taxonomy.REMARK_NUMBERS_COULD_BE_DATES))

    assert asked(inside + [str(first - 1)])
    assert not asked(inside[1:] + [str(first - 1), str(first - 2)])
    assert asked(inside[1:] + [str(first), str(first - 1)])


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

    THE REPLACEMENT IS A GROUP, and since stage 3 landing 3.5 it has to
    be. This clause is one of the thirteen sentence positions no key of
    the block covers, so the floor is asked of it here (plan P4-D334):
    a reach below `parsing.census_floor` is written as the fragment
    "fewer than 11" and the digits never appear. Thirty-seven is above
    the line and is not the reach the column really has, which is what
    this test needs it to be -- the point is that the sentence reads
    `clock_reach` and not that it reads a small number.
    """
    values = _declined_with_clocks()
    monkeypatch.setattr(taxonomy, "clock_reach", lambda _cells: 37)
    block = _described(values, name="taken_at")["columns"][0]
    said = _said(block, CLOCK_CLAUSE)
    assert said is not None
    assert "37 of these values read as a clock time" in said


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


def test_the_column_this_advice_was_written_for_now_needs_no_advice(
) -> None:
    """A-P4-1 item 4, SUPERSEDED by landing L8 (residual R-P4-147).

    This test held the advice itself: a declined column of numbers
    beside a few repeated gap words was told that running again with
    `--missing-value` would get its distribution described. What it
    holds now is that the column no longer needs telling, because it
    gets the distribution WITHOUT the declaration.

    THE SENTENCE IS NOT REACHABLE ANY MORE, measured rather than
    assumed. It needs two things at once: the non-numeric spellings
    must REPEAT, because only spellings the floor would let it name are
    counted, and removing them must leave a column with a distribution
    -- which means what is left is numbers. A column of numbers beside
    REPEATED non-numeric spellings is exactly what rule 7b claims, so
    every column satisfying both is compound before the advice is
    considered, and the advice is written on the free-text path. Gap
    words appearing once apiece are not named by the floor at all, so
    the reach is nought there.

    Retiring the sentence is a decision the owner has not been asked
    for, so the code still carries it and R-P4-147 records what is
    owed. Two sibling tests that exercised the sentence were removed
    with this one rewritten, and the register says so rather than
    leaving them renamed out of the way.
    """
    block = _described(_recoverable(_spread_numbers()), name="dose")["columns"][0]
    assert block["role"] == taxonomy.ROLE_COMPOUND, block["role"]
    # THE PROMISE, KEPT WITHOUT THE COMMAND: the sentence offered "this
    # column's distribution described", and the column publishes one.
    assert "percentiles" in block["numbers"]
    assert block["n_numeric_cells"] + block["n_label_cells"] == block["n_present"]
    assert not _said(block, ADVICE_CLAUSE)


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
