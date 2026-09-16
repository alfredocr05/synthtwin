"""Landing 2b.13: a held-back level's class and its written form together.

Both shapes here are ones the Codex review of landing 2b.4 measured and
landing 2b.8's skeptic reproduced on two trees and recorded as open.
Each is a ROUND TRIP: the table is described, a twin is built, the twin
is described AGAIN, and both the twin AND the real table are validated.
The census is recounted off the written twin form by form, rather than
read out of a report, because a report that names no miss is exactly
what both of these defects produced on the table while the twin failed.

The reviewer's own numbers are in each docstring, so a regression says
what it broke.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib

import pytest

from synthtwin import generation, parsing

from tests.test_landing_2b12_identifiers_codes_text import _counted, _round_trip


def _worn(written: "list[str]") -> "dict[str, int]":
    """The census the twin actually wears, recounted off its own cells."""
    seen: "dict[str, int]" = {}
    for cell in written:
        if not cell:
            continue
        form = parsing.shape_form(cell)
        seen[form] = (seen[form] if form in seen else 0) + 1
    return seen


# -- P4-D90: a class arrangement may not strand a feasible form debt --


def _readings_beside_words() -> "list[str]":
    """Codex item 5's own column, cell for cell.

    Five cells must read as numbers and four of them must wear `%.%`.
    The held-back sizes are 4, 1, 3 and 2: the split took 3+2, which
    makes five exactly and four not at all.
    """
    return (
        ["ab-cd"] * 20
        + ["5.1"] * 11
        + ["5.3"] * 11
        + ["7"] * 11
        + ["5.2"] * 4
        + ["8"]
        + ["retest"] * 3
        + ["hold"] * 2
    )


@pytest.mark.parametrize("seed", ["125", "4", "13"])
def test_readings_beside_words_settle_their_whole_form_debt(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Codex item 5 of landing 2b.4, NOT_FIXED at landing 2b.8's skeptic.

    Measured before this landing at two source seeds: the census
    published `%.%` twenty-six times and the twin wore it TWENTY-SEVEN,
    writing `6.9` twice where the table held `5.2` four times.
    `synthtwin validate` exited 3 on the twin and 0 on the table.
    """
    cells = _readings_beside_words()
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"readings-{seed}",
        cells,
        flags=("--smallest-group", "11"),
        seed=seed,
    )
    published = first["shape_forms"]
    worn = _worn(written)

    # The form the split used to strand is met EXACTLY -- not merely
    # approached, and not overpaid, which is how it failed before.
    assert published["%.%"] == 26
    assert worn["%.%"] == published["%.%"]

    # Every other published form is met too, so the repair did not buy
    # this one count with another.
    for form in published:
        if form == "__withheld__":
            continue
        assert worn.get(form, 0) == published[form], form

    # The twin still reads back as the same role with the same census,
    # which is what makes the count EXACT-OBSERVABLE and not just written.
    assert second["role"] == first["role"]

    # And both files meet the description: the twin, and the table the
    # description was written from.
    assert (twin_exit, real_exit) == (0, 0)


def test_an_arrangement_is_refused_only_when_another_settles_the_forms() -> None:
    """The rule is a PREFERENCE, so a column with no better split is unmoved.

    Asked of the product's own function at the reviewer's sizes. The
    split that meets the class exactly but strands the form debt is
    refused; the one the source itself exhibits is taken.
    """
    sizes = (4, 1, 3, 2)
    debts = {
        generation._OWED_NUMBER: 5,
        generation._OWED_OUT_OF_RANGE: 0,
        generation._OWED_CONTRADICTORY: 0,
    }
    supply = {name: 4 for name in generation._OWED_CLASSES}

    # Asked WITHOUT the form debt, the answer is the one it always gave.
    blind = generation._class_split(sizes, debts, supply)
    assert sorted(sizes[place] for place in blind) == [2, 3]

    # Asked WITH it, the arrangement that can pay `%.%` four cells wins.
    owing = {"%.%": 4, "@@-@@": 0}
    settled = generation._class_split(sizes, debts, supply, owing, False)
    assert sorted(sizes[place] for place in settled) == [1, 4]

    # And a form debt no arrangement can make leaves the first standing,
    # so this can never be worse than the walk it replaces.
    stranded = generation._class_split(
        sizes, debts, supply, {"%.%": 5, "@@-@@": 0}, False
    )
    assert stranded == blind


# -- P4-D91: a form reads as a number where its exponent filling does --


def _amounts_in_exponent_notation() -> "list[str]":
    """Codex item 7's own column: published numbers wearing `%.%@%`.

    EVERY published number here is an exponent spelling, and `%.%@%` is
    no plain decimal, so the ladder of step 3 has nothing to stand on:
    the description places no number at all and `ladder.anchored` is
    False. That is what makes this the column P4-D92 governs.
    """
    return ["alpha"] * 30 + ["1.1e6"] * 11 + ["1.2e6"] * 11 + ["1.3e6"] * 4


def _amounts_in_both_notations() -> "list[str]":
    """The same census on a column that also publishes PLAIN numbers.

    A spreadsheet writing large amounts turns to scientific notation
    partway down a column, which is where this shape comes from. The
    plain spellings anchor the ladder, so the published ends exist and
    the form's own walk has somewhere to stand.
    """
    return (
        ["alpha"] * 20
        + ["1000000"] * 11
        + ["9000000"] * 11
        + ["1.1e6"] * 11
        + ["1.2e6"] * 11
        + ["5.5e6"] * 4
    )


def _source_numbers(cells: "list[str]") -> "list[float]":
    """Every number the table itself holds, as the shipped reader reads."""
    found: "list[float]" = []
    for cell in cells:
        value = parsing.parse_number(cell)
        if value is not None:
            found += [value]
    return found


@pytest.mark.parametrize("seed", ["4", "13", "125"])
def test_an_unplaced_exponent_form_is_left_unpaid_and_says_so(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """P4-D92: a census count is never bought with a stray magnitude.

    Landing 2b.13 settled this column's form debt from the form's OWN
    walk, which wrote `9.6E6` for all four held-back cells at every one
    of seven generate seeds. The census then came out twenty-six of
    twenty-six -- and the twin's numbers had mean 2,450,000 and maximum
    9,600,000 against the table's 1,173,077 and 1,300,000, a spread
    42.9 times the table's against the 5.9 times it replaced, while
    `synthtwin validate` fell from 3 to 0 and took with it the only
    warning a reader had.

    Every published number here is an exponent spelling, so no plain
    decimal anchors the ladder and NOTHING places a made-up number.
    The debt therefore stands, and it stands where a reader can see it.
    """
    cells = _amounts_in_exponent_notation()
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"amounts-{seed}",
        cells,
        flags=("--smallest-group", "11"),
        seed=seed,
    )

    # NOT ONE made-up cell reaches past the numbers the table holds.
    # `9.6E6` was 7.4 times the largest of them.
    largest = max(_source_numbers(cells))
    made = [cell for cell in written if cell not in _counted(cells)]
    for cell in made:
        value = parsing.parse_number(cell)
        if value is not None:
            assert value <= largest, cell

    # The shortfall is ANNOUNCED rather than settled: the table meets
    # its own description and the twin does not. That asymmetry is the
    # signal, and this landing's repair is that it survives.
    assert real_exit == 0
    assert twin_exit == 3
    assert second["role"] == first["role"]


@pytest.mark.parametrize("seed", ["4", "13", "125"])
def test_an_anchored_exponent_form_is_settled_inside_the_published_ends(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """P4-D92 BOUNDS P4-D91 without withdrawing it.

    The same census, on a column whose plain spellings give the ladder
    its ends. The form debt is met in full AND every made-up number
    lies inside them -- `5.0E6` on a column spanning 1,000,000 to
    9,000,000 -- so the census count and the twin's statistics are had
    together rather than one at the other's cost. Measured: the twin's
    numbers have mean 3,235,417 and standard deviation 3,318,790
    against the table's 3,277,083 and 3,343,728, with the same least
    and greatest.
    """
    cells = _amounts_in_both_notations()
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"both-{seed}",
        cells,
        flags=("--smallest-group", "11"),
        seed=seed,
    )
    published = first["shape_forms"]
    worn = _worn(written)

    assert published["%.%@%"] == 26
    assert worn["%.%@%"] == published["%.%@%"]

    # Each made-up cell meets all three obligations at once: it wears
    # the published form, it reads as a number, and it is a number the
    # column is known to hold.
    numbers = _source_numbers(cells)
    made = [cell for cell in written if cell not in _counted(cells)]
    for cell in made:
        assert parsing.classify_number(cell) == parsing.NUMBER, cell
        assert parsing.shape_form(cell) == "%.%@%", cell
        value = parsing.parse_number(cell)
        assert value is not None
        assert min(numbers) <= value <= max(numbers), cell

    assert second["role"] == first["role"]
    assert (twin_exit, real_exit) == (0, 0)


def test_a_form_reads_as_a_number_only_where_a_filling_makes_one() -> None:
    """The rule's two edges, asked of the product's own function.

    Widened where an exponent filling reads as a number, and NOT
    widened anywhere else -- a form of letters alone is still text, and
    no form is ever talked into the out-of-range or contradictory
    classes, whose spellings G10.3 constructs outright.
    """
    # The form the first filling called text and the exponent makes a
    # number. `_filled_form` at step zero is `0.0A0`.
    assert generation._filled_form("%.%@%", 0) == "0.0A0"
    assert parsing.classify_number("0.0A0") == parsing.NOT_A_NUMBER
    assert generation._exponent_filling("%.%@%") == "0.0E0"
    assert generation._form_reading("%.%@%", False) == parsing.NUMBER

    # A form with no letter place is untouched: no probe is even built.
    assert generation._exponent_filling("%%.%") == ""
    assert generation._form_reading("%%.%", False) == parsing.NUMBER
    assert generation._form_reading("%%/%%", False) == parsing.NOT_A_NUMBER

    # A form of letters is still text however it is filled.
    assert generation._exponent_filling("@@-@@") == "EE-EE"
    assert generation._form_reading("@@-@@", False) == parsing.NOT_A_NUMBER

    # And the form's own walk really can write the class this claims,
    # which is what makes the answer a promise the generator can keep.
    spelling = generation._class_form_stand_in(
        "%.%@%", parsing.NUMBER, {}, {}, {}, (), False
    )
    assert parsing.classify_number(spelling) == parsing.NUMBER
    assert parsing.shape_form(spelling) == "%.%@%"


def test_a_leading_plus_or_a_grouping_mark_is_still_carried() -> None:
    """The two thirds of Codex item 7 this landing does NOT fix.

    Their cause is not P4-D91's: `+00` and `0,000` already read as
    numbers at the first filling, so those forms reach the number debt.
    What refuses them is the stand-in neutrality rule -- no made-up cell
    opens with a character a spreadsheet reads as a formula, and none
    carries a comma on a column not read with one. Widening either is an
    owner ruling nobody has given, so this pins the rule that stands
    rather than the defect that follows from it.
    """
    assert generation._form_reading("+%%", False) == parsing.NUMBER
    assert generation._form_reading("%,%%%", False) == parsing.NUMBER

    # Neither spelling may be CHOSEN as a stand-in, and that is the rule.
    assert not generation._is_a_usable_stand_in(
        "+11", (), parsing.NUMBER, False
    )
    assert not generation._is_a_usable_stand_in(
        "1,100", (), parsing.NUMBER, False
    )
    # ...while the same number written plainly is perfectly usable, so
    # the refusal is about the MARK and not about the value.
    assert generation._is_a_usable_stand_in("11", (), parsing.NUMBER, False)


def test_a_forms_own_walk_is_held_to_the_published_ends() -> None:
    """P4-D92's rule, asked of the product's own functions.

    The form's own walk fills figure places by COUNTING, so left alone
    it lands wherever the counting lands -- which is how a column of
    amounts near 1.2 million came to hold `9.6E6`. Held to the ends the
    published numbers themselves cover, it reaches one inside them.
    """
    published = ["1000000", "9000000"]
    ladder = generation._number_ladder(published, False, ["%.%@%"])
    assert ladder.anchored
    used = {cell: 1 for cell in published}
    owners = {parsing.folded(cell): cell for cell in published}

    # UNBOUNDED, the walk landing 2b.13 shipped reaches a spelling
    # past the largest number the column has.
    free = generation._class_form_stand_in(
        "%.%@%", parsing.NUMBER, {}, dict(used), dict(owners), (), False
    )
    loose = parsing.parse_number(free)
    assert loose is not None and loose > 9000000.0

    # BOUNDED, it reaches one the column could have held, and the form
    # is still worn -- the census count is not given up to get there.
    held = generation._class_form_stand_in(
        "%.%@%", parsing.NUMBER, {}, dict(used), dict(owners), (), False,
        ladder,
    )
    inside = parsing.parse_number(held)
    assert parsing.shape_form(held) == "%.%@%"
    assert inside is not None and 1000000.0 <= inside <= 9000000.0

    # THE SUPPLY IS COUNTED UNDER THE SAME BOUND IT IS SPENT UNDER, and
    # this is asked STRICTLY, because a supply counted loosely settles
    # the form over a level the walk then cannot cover -- which reports
    # a missing spelling rather than the bound really refusing it. Asked
    # for twenty-six, this form holds twenty-six spellings unbounded and
    # FIFTEEN inside a span of 1,000,000 to 9,000,000.
    loose_room = generation._usable_room(
        "%.%@%", 26, dict(used), dict(owners), (), parsing.NUMBER, False
    )
    held_room = generation._usable_room(
        "%.%@%", 26, dict(used), dict(owners), (), parsing.NUMBER, False,
        ladder,
    )
    assert loose_room == 26
    assert held_room == 15
    assert held_room < loose_room

    # And where the column published ONE plain number the ends are a
    # single point: the form has spellings, and not one of them is a
    # number that column is known to hold, so the counted supply is
    # nought where the loose count was four.
    point = generation._number_ladder(["1100000"], False, ["%.%@%"])
    assert point.anchored
    assert generation._usable_room(
        "%.%@%", 4, {}, {}, (), parsing.NUMBER, False
    ) == 4
    assert generation._usable_room(
        "%.%@%", 4, {}, {}, (), parsing.NUMBER, False, point
    ) == 0

    # AND WHERE THE COLUMN PUBLISHED NO PLAIN NUMBER there are no ends
    # at all: nothing places a made-up number, so none is written and
    # the debt stands. This is Codex's own column.
    nowhere = generation._number_ladder(["1.1e6", "1.2e6"], False, ["%.%@%"])
    assert not nowhere.anchored
    assert generation._class_form_stand_in(
        "%.%@%", parsing.NUMBER, {}, {}, {}, (), False, nowhere
    ) == ""

    assert generation._within_the_published_ends("5.0E6", ladder, False)
    assert not generation._within_the_published_ends("9.6E6", ladder, False)
    assert not generation._within_the_published_ends("9.6E6", nowhere, False)


def test_a_held_back_levels_own_spelling_is_nowhere_in_the_description(
    tmp_path: pathlib.Path,
) -> None:
    """What the floor withholds, asserted of the document itself.

    A review of this landing asked that the held-back levels' own
    SPELLINGS be added to the stand-in refusal set, so that no twin
    cell could ever be spelled as one. They cannot be: the description
    does not carry them, which is what the floor is for. What it does
    carry is `suppressed_level_counts` -- the COUNTS, `5.2`'s four
    among them -- so a twin group is the size of a real one by
    construction while its spelling is invented by arithmetic on the
    published anchors.

    Pinned here because the asymmetry is the whole disclosure argument:
    a later change that began publishing a withheld spelling would
    break this test rather than leak quietly.
    """
    import json

    cells = _readings_beside_words()
    first, _second, _written, _twin_exit, _real_exit = _round_trip(
        tmp_path / "withheld",
        cells,
        flags=("--smallest-group", "11"),
        seed="4",
    )
    document = json.dumps(first)
    for spelling in ("5.2", "retest", "hold"):
        assert f'"{spelling}"' not in document, spelling

    # The counts, and only the counts.
    assert sorted(first["suppressed_level_counts"]) == [1, 2, 3, 4]
