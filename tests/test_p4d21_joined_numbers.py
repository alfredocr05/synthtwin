"""`joined_numbers`: two numbers in one cell, and why it is declared.

WHAT THIS FILE IS FOR (plan P4-D21). A blood pressure column holds
`120/80`. Every shape fact about it was already exact -- residual
R-P4-38 closed the last one -- and its twin still held `632/20`,
because the cell was written from the free-text alphabet and its digits
carried no distribution at all. This role reads each number in the cell
separately and publishes a range and an average for each.

THE ROLE IS REACHED ONLY BY DECLARATION, and the reason is measured
rather than cautious. `test_no_column_of_the_other_roles_is_claimed`
below is the whole argument: a rule that read the VALUES would claim
this project's own date column, its clock column, and -- past any rule
order that could save those two -- its laboratory-code and drug-code
columns, publishing fragments of real codes as numeric ranges.
"""

import pathlib
import random
import statistics
import tempfile

import fixtures
import pytest

from synthtwin import (
    contract,
    errors,
    generation,
    profile,
    reading,
    taxonomy,
)


def _readings(count: int = 400, seed: int = 5) -> "list[str]":
    """A blood-pressure column of believable readings."""
    rng = random.Random(seed)
    out: "list[str]" = []
    for _each in range(count):
        top = rng.randrange(95, 176)
        bottom = rng.randrange(55, 106)
        out = out + [f"{top}/{bottom}"]
    return out


def _described(
    values: "list[str]", name: str = "bp", declared: bool = True
) -> "tuple[dict, pathlib.Path]":
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "t.csv", fixtures.single_column_table(name, values)
    )
    read = reading.read_table(f"{table}")
    document = profile.build_document(
        read, taxonomy.Settings(), [], [], [name] if declared else []
    )
    return document, folder


def _loaded(document: dict, folder: pathlib.Path) -> "contract.Profile":
    written = fixtures.write_profile(folder, "t.json", document)
    return contract.load_profile(f"{written}")


def _part(cell: str, place: int) -> int:
    return int(cell.split("/")[place])


# -- what the declaration does -----------------------------------------


def test_undeclared_it_is_not_this_role() -> None:
    """The values decide nothing, so an undeclared column is untouched."""
    document, _folder = _described(_readings(), declared=False)
    assert document["columns"][0]["role"] != taxonomy.ROLE_JOINED


def test_declared_it_reads_each_number_separately() -> None:
    """With the word, the column publishes a block per position."""
    document, _folder = _described(_readings())
    block = document["columns"][0]
    assert block["role"] == taxonomy.ROLE_JOINED
    assert block["separator"] == "/"
    assert block["n_parts"] == 2
    assert len(block["parts"]) == 2


def test_each_position_publishes_its_own_range() -> None:
    """The first number's ladder is a ladder of first numbers."""
    values = _readings()
    document, _folder = _described(values)
    block = document["columns"][0]
    for place in range(2):
        real = [_part(cell, place) for cell in values]
        rungs = block["parts"][place]["percentiles"]
        assert rungs["min"] == min(real)
        assert rungs["max"] == max(real)
        assert abs(block["parts"][place]["mean"] - statistics.fmean(real)) < 0.5


def test_no_whole_cell_of_the_table_is_published() -> None:
    """A ranges role publishes no spelling but the separator."""
    values = _readings()
    document, _folder = _described(values)
    written = f"{document['columns'][0]}"
    for cell in set(values):
        assert f"'{cell}'" not in written


def test_the_declaration_is_recorded_in_the_profile() -> None:
    document, _folder = _described(_readings())
    assert document["settings"]["forced_measurements"] == ["bp"]


# -- the twin ----------------------------------------------------------


def test_the_twin_holds_believable_readings() -> None:
    """The defect this landing closes, stated as a test.

    Before it, a blood-pressure twin held cells like `632/20`: the
    right shape and an impossible reading.
    """
    values = _readings()
    document, folder = _described(values)
    twin = generation.generate(_loaded(document, folder), 7)
    for cell in twin.columns[0]:
        assert "/" in cell
        top = _part(cell, 0)
        bottom = _part(cell, 1)
        assert 95 <= top <= 175, f"{cell} is not a systolic reading"
        assert 55 <= bottom <= 105, f"{cell} is not a diastolic reading"


def test_each_position_keeps_its_own_distribution() -> None:
    """Both numbers land on the real column's spread, not just its shape."""
    values = _readings()
    document, folder = _described(values)
    twin = generation.generate(_loaded(document, folder), 7)
    for place in range(2):
        real = [_part(cell, place) for cell in values]
        made = [_part(cell, place) for cell in twin.columns[0]]
        assert min(made) == min(real)
        assert max(made) == max(real)
        assert abs(statistics.fmean(made) - statistics.fmean(real)) < 1.0
        assert abs(statistics.median(made) - statistics.median(real)) < 2.0


def test_the_twin_never_holds_more_readings_than_the_table() -> None:
    """`n_distinct` bounds the twin, and a shortfall is REPORTED.

    IT WAS EXACT UNTIL THE PAIRING CARRIED FACTS OF ITS OWN (plan
    P4-D23). With the pairing free, the walk could always reach the
    published count. It is no longer free: it also has to make the two
    numbers move together as strongly as the real ones did, and hold
    the earlier one above the later one as often. For the values a
    position DRAWS -- which follow the published ladder and so repeat
    more evenly than the real ones did -- the three cannot always be
    met at once. Residual R-P4-40 records the cause and its fix.

    What must never happen is a silent shortfall, so this asserts the
    bound and `test_a_shortfall_in_different_readings_is_reported`
    asserts that the twin's own report says it.
    """
    values = _readings()
    document, folder = _described(values)
    twin = generation.generate(_loaded(document, folder), 7)
    assert len(set(twin.columns[0])) <= document["columns"][0]["n_distinct"]


def test_a_shortfall_in_different_readings_is_reported() -> None:
    """A twin holding fewer different readings says so on its own page."""
    values = _readings()
    document, folder = _described(values)
    twin = generation.generate(_loaded(document, folder), 7)
    made = len(set(twin.columns[0]))
    published = document["columns"][0]["n_distinct"]
    said = [
        note for note in twin.deviations if note.fact == "n_distinct"
    ]
    if made == published:
        assert not said, "nothing was given up, so nothing should be said"
        return
    assert said, (
        "the twin holds fewer different readings than the description "
        "records and its report does not say so"
    )


def test_the_two_numbers_move_together_as_they_did() -> None:
    """The point of P4-D23, and the reason the pairing is not free.

    Drawn independently the two numbers agreed at about zero where the
    real column agreed at 0.83, and a twin cell could hold a diastolic
    above its systolic. Both are facts the description now carries.
    """
    rng = random.Random(11)
    values: "list[str]" = []
    for _each in range(400):
        together = rng.gauss(0, 1)
        top = max(95, min(175, round(133 + 24 * together + rng.gauss(0, 12))))
        bottom = max(55, min(105, round(80 + 14 * together + rng.gauss(0, 7))))
        values = values + [f"{top}/{bottom}"]
    document, folder = _described(values)
    block = document["columns"][0]
    assert block["part_agreements"][0] > 0.5, "the fixture is not correlated"
    twin = generation.generate(_loaded(document, folder), 7)
    from synthtwin import parsing

    first = [float(_part(cell, 0)) for cell in twin.columns[0]]
    second = [float(_part(cell, 1)) for cell in twin.columns[0]]
    made = parsing.rank_agreement(first, second)
    assert abs(made - block["part_agreements"][0]) < 0.01, (
        f"the twin's two numbers agree at {made}, not at "
        f"{block['part_agreements'][0]}"
    )
    above = len([1 for a, b in zip(first, second) if a > b])
    assert above == block["part_above"][0]
    assert above == 400, "every reading should have its systolic on top"


def test_a_padded_position_stays_padded() -> None:
    """A position written `007` comes back three characters wide."""
    values = [f"{top:03d}/{bottom:03d}" for top in range(10, 90)
              for bottom in range(5, 10)]
    document, folder = _described(values)
    assert document["columns"][0]["part_min_widths"] == [3, 3]
    twin = generation.generate(_loaded(document, folder), 3)
    for cell in twin.columns[0]:
        top, bottom = cell.split("/")
        assert len(top) == 3 and len(bottom) == 3, cell


def test_three_numbers_in_a_cell_are_read_as_three() -> None:
    values = [f"{a}-{a + 1}-{a + 2}" for a in range(100, 340)]
    document, _folder = _described(values, name="score")
    block = document["columns"][0]
    assert block["role"] == taxonomy.ROLE_JOINED
    assert block["n_parts"] == 3
    assert block["separator"] == "-"


# -- the reason it is declared and not detected ------------------------


@pytest.mark.parametrize(
    "name,values,role",
    [
        (
            "visit_date",
            [f"2023-{month:02d}-{day:02d}" for month in range(1, 13)
             for day in range(1, 21)],
            taxonomy.ROLE_DATETIME,
        ),
        (
            "seen_at",
            [f"{hour:02d}:{minute:02d}" for hour in range(8, 20)
             for minute in range(0, 60, 3)],
            taxonomy.ROLE_CLOCK,
        ),
    ],
)
def test_no_column_of_the_other_roles_is_claimed(
    name: str, values: "list[str]", role: str
) -> None:
    """A date and a clock split into whole numbers and are NOT this role.

    `2023-02-12` is three whole numbers joined by `-` and `09:30` is two
    joined by `:`. Both would be claimed by any rule that read the
    values, and both keep the role they had -- because no rule reads the
    values, and the declaration was not given.
    """
    document, _folder = _described(values, name=name, declared=False)
    assert document["columns"][0]["role"] == role


def test_a_code_column_is_not_claimed_either() -> None:
    """The case rule order could NOT have saved, and the reason for P4-D21.

    A laboratory code `1923-1` is two whole numbers joined by `-`, and
    it is free text today -- the last rule of all. A value-based
    joined-number rule would have to be tested before free text, so it
    WOULD claim this column and publish the smallest and largest of its
    parts, which are fragments of real codes.
    """
    rng = random.Random(9)
    values = [
        f"{rng.randrange(1000, 9999)}-{rng.randrange(1, 9)}"
        for _each in range(240)
    ]
    document, _folder = _described(values, name="lab_code", declared=False)
    block = document["columns"][0]
    assert block["role"] != taxonomy.ROLE_JOINED
    assert "parts" not in block


def test_declaring_a_column_of_codes_is_the_owner_s_mistake_to_make() -> None:
    """Named as measurements, a code column IS read as measurements.

    Stated as a test because it is the cost of the declaration and not
    a defect: synthtwin cannot tell, so it does what it is told. What
    protects the column is that nothing declares it by itself.
    """
    rng = random.Random(9)
    values = [
        f"{rng.randrange(1000, 9999)}-{rng.randrange(1, 9)}"
        for _each in range(240)
    ]
    document, _folder = _described(values, name="lab_code")
    assert document["columns"][0]["role"] == taxonomy.ROLE_JOINED


# -- what the contract refuses ------------------------------------------


def test_a_separator_this_format_does_not_split_on_is_refused() -> None:
    document, folder = _described(_readings())
    document["columns"][0]["separator"] = "."
    with pytest.raises(errors.ProfileError):
        _loaded(document, folder)


def test_a_block_claiming_one_part_is_refused() -> None:
    """One number in a cell is a bare number, which is another role."""
    document, folder = _described(_readings())
    document["columns"][0]["n_parts"] = 1
    with pytest.raises(errors.ProfileError):
        _loaded(document, folder)


def test_the_split_and_the_unsplit_close_on_the_present_cells() -> None:
    document, folder = _described(_readings())
    document["columns"][0]["n_joined"] = 3
    with pytest.raises(errors.ProfileError):
        _loaded(document, folder)


def test_a_declared_name_the_table_lacks_is_refused() -> None:
    document, folder = _described(_readings())
    document["settings"]["forced_measurements"] = ["not_a_column"]
    with pytest.raises(errors.ProfileError):
        _loaded(document, folder)


def test_the_twin_reads_back_as_the_role_it_was_built_for() -> None:
    """The whole workflow, end to end, on the column this landing is for."""
    values = _readings()
    document, folder = _described(values)
    described = _loaded(document, folder)
    twin = generation.generate(described, 7)
    # WRITTEN BY THE PRODUCT'S OWN WRITER, not by `csv`. The line
    # ending is a published fact and `csv.writer` ends a row with a
    # carriage return, so a hand-written twin misses an obligation the
    # generator never would -- which is the defect this file found in
    # its own first draft.
    from synthtwin import rendering, validation

    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    # EVERY OBLIGATION BUT THE COUNT OF DIFFERENT READINGS, which the
    # pairing cannot always meet beside the facts it now also carries
    # (residual R-P4-40). A shortfall there is reported by the twin and
    # is asserted by
    # `test_a_shortfall_in_different_readings_is_reported`; anything
    # else missing is a defect.
    missed = [
        check
        for check in outcome.checks
        if check.verdict == "MISSED" and "n_distinct" not in check.subcheck
    ]
    assert missed == [], f"the twin missed {missed}"


# -- P4-D24: the two shapes the first build could not read -------------


def test_a_reading_written_with_spaces_round_its_mark_is_read() -> None:
    """`120 / 80` is the same reading as `120/80`.

    It was read as free text, which publishes nothing: the mark alone
    did not match and no rule looked further.
    """
    rng = random.Random(3)
    values = [
        f"{rng.randrange(95, 176)} / {rng.randrange(55, 106)}"
        for _each in range(240)
    ]
    document, _folder = _described(values)
    block = document["columns"][0]
    assert block["role"] == taxonomy.ROLE_JOINED
    assert block["separator"] == " / "
    assert block["n_parts"] == 2


def test_the_twin_writes_the_spacing_back() -> None:
    """The separator published is the separator written."""
    rng = random.Random(3)
    values = [
        f"{rng.randrange(95, 176)} / {rng.randrange(55, 106)}"
        for _each in range(240)
    ]
    document, folder = _described(values)
    twin = generation.generate(_loaded(document, folder), 5)
    for cell in twin.columns[0]:
        assert " / " in cell, cell


def test_a_position_carrying_a_decimal_point_is_read() -> None:
    """An I:E ratio of `1:1.5` has a decimal in its second number."""
    rng = random.Random(4)
    values = [
        f"1:{rng.choice(['1.0', '1.5', '2.0', '2.5', '3.0'])}"
        for _each in range(240)
    ]
    document, _folder = _described(values)
    block = document["columns"][0]
    assert block["role"] == taxonomy.ROLE_JOINED
    assert block["n_parts"] == 2
    assert block["parts"][1]["integer_valued"] is False


def test_the_twin_keeps_the_decimal() -> None:
    rng = random.Random(4)
    values = [
        f"1:{rng.choice(['1.0', '1.5', '2.0', '2.5', '3.0'])}"
        for _each in range(240)
    ]
    document, folder = _described(values)
    twin = generation.generate(_loaded(document, folder), 5)
    for cell in twin.columns[0]:
        assert "." in cell.split(":")[1], cell


@pytest.mark.parametrize(
    "text,separator,expected",
    [
        ("120/80", "/", ["120", "80"]),
        ("120 / 80", " / ", ["120", "80"]),
        ("1:1.5", ":", ["1", "1.5"]),
        ("1: 2", ": ", ["1", "2"]),
        ("1.5.2/3", "/", None),
        ("a/b", "/", None),
        ("120/", "/", None),
        (".5/2", "/", None),
        ("5./2", "/", None),
    ],
)
def test_what_counts_as_a_number_in_a_position(
    text: str, separator: str, expected: "list[str] | None"
) -> None:
    """Figures, and at most one point with figures on both sides.

    No sign, because a leading minus cannot be told from the mark a
    cell might be split on.
    """
    assert taxonomy.splits_into_numbers(text, separator) == expected


def test_a_column_of_negative_numbers_is_not_claimed() -> None:
    """`-3/-4` would split on its own minus signs, so it is refused."""
    values = [f"-{place}/-{place + 1}" for place in range(1, 200)]
    document, _folder = _described(values)
    block = document["columns"][0]
    assert block["role"] != taxonomy.ROLE_JOINED


# -- P4-D25: the role's own facts are checked --------------------------


def _measured(values: "list[str]") -> "object":
    from synthtwin import rendering, validation

    document, folder = _described(values)
    described = _loaded(document, folder)
    twin = generation.generate(described, 7)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    return validation.measure(described, f"{written}")


def test_every_fact_this_role_publishes_is_checked() -> None:
    """The hole R-P4-41 named, closed and held closed.

    `validation._role_checks` dispatches on the facts type and fell
    through to an EMPTY LIST for this role, so a joined column's
    separator, part count, widths, per-position numbers and pairing
    facts were published and verified by nothing. A twin was measured
    on the universal obligations alone.

    Every key the role adds is named here, so a key added later without
    a check turns this red.
    """
    outcome = _measured(_readings())
    checked = {check.fact for check in outcome.checks}
    owed = {
        "joined.separator",
        "joined.n_parts",
        "joined.n_joined",
        "joined.n_unparsed",
        "joined.part_min_widths[0]",
        "joined.part_min_widths[1]",
        "joined.part_above[0]",
        "joined.part_agreements[0]",
        "joined.parts[0].min",
        "joined.parts[0].max",
        "joined.parts[0].integer_valued",
        "joined.parts[1].min",
        "joined.parts[1].max",
        "joined.parts[1].integer_valued",
    }
    missing = sorted(owed - checked)
    assert missing == [], f"these facts are published and unchecked: {missing}"


def test_the_checks_are_met_by_the_twin_the_generator_builds() -> None:
    """A check nobody can pass is as useless as no check at all."""
    outcome = _measured(_readings())
    failed = [
        check.fact
        for check in outcome.checks
        if check.verdict == "MISSED" and check.fact.startswith("joined.")
    ]
    assert failed == [], f"the twin misses its own role's facts: {failed}"


def test_a_twin_with_the_wrong_pairing_is_caught() -> None:
    """The checks bite: a file whose numbers do not move together fails.

    Removal sensitivity, asked the way this project asks it. The cells
    are rebuilt with the second number shuffled against the first, so
    every number is still present exactly and only the PAIRING is
    wrong -- which is precisely what these checks exist to catch and
    what nothing caught before.
    """
    from synthtwin import validation

    rng = random.Random(11)
    values: "list[str]" = []
    for _each in range(400):
        together = rng.gauss(0, 1)
        top = max(95, min(175, round(133 + 24 * together + rng.gauss(0, 12))))
        bottom = max(55, min(105, round(80 + 14 * together + rng.gauss(0, 7))))
        values = values + [f"{top}/{bottom}"]
    document, folder = _described(values)
    described = _loaded(document, folder)
    twin = generation.generate(described, 7)
    firsts = [cell.split("/")[0] for cell in twin.columns[0]]
    seconds = [cell.split("/")[1] for cell in twin.columns[0]]
    rng.shuffle(seconds)
    spoiled = [f"{firsts[row]}/{seconds[row]}" for row in range(len(firsts))]
    text = "bp\n" + "\n".join(spoiled) + "\n"
    written = fixtures.write(folder, "spoiled.csv", text)
    outcome = validation.measure(described, f"{written}")
    caught = [
        check.fact
        for check in outcome.checks
        if check.verdict == "MISSED" and "part_agreements" in check.fact
    ]
    assert caught, (
        "a file whose two numbers do not move together as the "
        "description says passed every check"
    )


# -- the round trip, and the count the pairing is asked for -----------


def _one_cell_that_does_not_split(count: int = 200) -> "list[str]":
    """A believable joined column with a single cell that is not one."""
    return _readings(count - 1, seed=5) + ["no reading"]


def test_a_column_with_an_unparsed_cell_is_readable_by_its_own_loader() -> (
    None
):
    """`synthtwin profile` must never write a file it cannot read.

    Each POSITION of a joined column describes only the cells that
    split, so the profiler writes `n_joined` as that block's row count.
    Q1 compared it against the TABLE's row count instead, and the two
    differ by exactly the cells that did not split -- so every joined
    column carrying even one unparsed cell was refused by the loader
    that had just been handed the profiler's own output. The message it
    raised told the user the file had been changed since it was written
    and to make it again, which produces the same file.

    With no unparsed cell the two counts coincide, which is why nothing
    showed this until a column carried one.
    """
    document, folder = _described(_one_cell_that_does_not_split())
    column = document["columns"][0]
    assert column["role"] == "joined_numbers"
    assert column["n_unparsed"] >= 1, "this fixture must carry a straggler"
    assert column["parts"][0]["n_rows"] == column["n_joined"], (
        "a position describes the cells that split, so it echoes n_joined"
    )
    assert column["parts"][0]["n_rows"] != document["n_rows"], (
        "if these agreed the fixture would not reach the rule under test"
    )

    described = _loaded(document, folder)
    twin = generation.generate(described, 6)
    written = [cell for cell in twin.columns[0] if cell]
    assert len(written) == column["n_present"]


def test_the_pairing_is_asked_for_the_count_the_pairs_can_carry() -> None:
    """A column that MEETS its published count is not told it missed.

    The cells that did not split are replaced afterwards by stand-ins
    that are all ONE spelling, which no joined cell wears, so they add
    exactly one to the count of different cells however many there are.
    The pairing is therefore asked for `n_distinct - 1` where any such
    cell exists, and comparing its result against the whole column's
    `n_distinct` compares unlike quantities: a column of 120 cells that
    held 120 different ones was told by its own report that it held 119.
    """
    seen: "dict[str, int]" = {}
    values: "list[str]" = []
    rng = random.Random(3)
    while len(values) < 119:
        cell = f"{rng.randrange(95, 176)}/{rng.randrange(55, 106)}"
        if cell in seen:
            continue
        seen[cell] = 1
        values = values + [cell]
    document, folder = _described(values + ["no reading"])
    assert document["columns"][0]["role"] == "joined_numbers"
    described = _loaded(document, folder)
    published = described.columns[0].n_distinct
    twin = generation.generate(described, 4)
    written = [cell for cell in twin.columns[0] if cell]
    assert len(set(written)) == published, (
        "this fixture must reach a twin that MEETS the published count, "
        "or it cannot show a report claiming otherwise"
    )
    missed = [
        note
        for note in twin.deviations
        if note.fact == "n_distinct"
    ]
    assert not missed, (
        "the column holds every different value the description "
        f"publishes, and its own report says it missed: {missed}"
    )
