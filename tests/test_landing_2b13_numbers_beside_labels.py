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
    """Codex item 7's own column: published numbers wearing `%.%@%`."""
    return ["alpha"] * 30 + ["1.1e6"] * 11 + ["1.2e6"] * 11 + ["1.3e6"] * 4


@pytest.mark.parametrize("seed", ["4", "13", "125"])
def test_a_column_publishing_exponent_numbers_wears_their_form(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """Codex item 7 of landing 2b.4, PARTLY at landing 2b.8's skeptic.

    Measured before this landing at two source seeds: the census named
    `%.%@%` twenty-six times, the twin wore it TWENTY-TWO, and the four
    held-back cells were written `1` -- so the twin's numbers had
    minimum 1 against the table's 1,100,000. `synthtwin validate`
    exited 3 on the twin and 0 on the table.
    """
    cells = _amounts_in_exponent_notation()
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"amounts-{seed}",
        cells,
        flags=("--smallest-group", "11"),
        seed=seed,
    )
    published = first["shape_forms"]
    worn = _worn(written)

    assert published["%.%@%"] == 26
    assert worn["%.%@%"] == published["%.%@%"]

    # The held-back cells are NUMBERS wearing that form, which is the
    # half that meets the class count and the census at the same time.
    # They were `1` before: whole numbers of one character.
    made = [cell for cell in written if cell not in _counted(cells)]
    for cell in made:
        assert parsing.classify_number(cell) == parsing.NUMBER, cell
        assert parsing.shape_form(cell) == "%.%@%", cell

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
