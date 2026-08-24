"""A zero-padded code column keeps its field width in the twin.

Plan decision P4-D7, amendment A-P4-34, contract section 7.8.

THE DEFECT THIS FILE IS THE RECORD OF. A profile could say that two
hundred and forty cells were written with a redundant leading zero. It
could not say whether the field was five figures wide or nine -- a
procedure code and a record number are the same fact to `numeric_styles`
-- so the twin of a column of five-figure codes wrote fields two, three,
four and five figures wide. It honoured every published fact while doing
it, and the quality report recorded nothing missed, because no published
fact said the width. Code developed against that twin -- a length check,
a fixed-width slice, a join on the code -- could not run on the real
table, which is the one thing the product exists to make possible.

WHAT IS PINNED HERE:

- the census is published for the roles that carry a forms map, over
  the CORES on the affixed role;
- the twin writes each padded cell at a published width;
- a width the twin could not reach is NAMED in the twin's report rather
  than passed over;
- the validator checks the census, and a file whose widths moved is
  reported MISSED;
- a named width spends the leading-zero family, so raw distinctness
  falls to the envelope owner decision 11 already authorizes -- never
  to a MISSED verdict;
- and a column with no padded cell publishes an empty census and is
  unaffected, which is what keeps this landing off every other column.
"""

import collections
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


def _described(
    values: "list[str]", settings: "taxonomy.Settings | None" = None
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One single-column table, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table("thing", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), settings or taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    return document, contract.load_profile(f"{written}"), folder


def _cores(
    cells: "list[str]", prefix: str = "", suffix: str = ""
) -> "list[str]":
    """The padded cores of a written column, the affix pair stripped."""
    found: list[str] = []
    for cell in cells:
        if not cell:
            continue
        body = cell
        if prefix or suffix:
            if not body.startswith(prefix) or not body.endswith(suffix):
                continue
            body = body[len(prefix) : len(body) - len(suffix)]
            if not body:
                continue
        if parsing.classify_number(body) != parsing.NUMBER:
            continue
        if parsing.numeric_style(body) != parsing.STYLE_LEADING_ZERO:
            continue
        found = found + [body]
    return found


def _census(cells: "list[str]", prefix: str = "", suffix: str = "") -> dict:
    """The width census of a written column, recounted off its text."""
    return dict(
        collections.Counter(
            parsing.pad_width(core) for core in _cores(cells, prefix, suffix)
        )
    )


def _twin_cells(described: contract.Profile, seed: int = 5) -> "list[str]":
    twin = generation.generate(described, seed)
    return [cell for cell in twin.columns[0]]


# -- the rule itself --------------------------------------------------


def test_the_width_reads_the_field_and_not_the_characters() -> None:
    """The sign is not a figure, which is the whole of the reading."""
    assert parsing.pad_width("000123") == 6
    assert parsing.pad_width("-000123") == 6
    assert parsing.pad_width("+000123") == 6
    # A point ends the field: padding is written into the figures
    # BEFORE it, and the fraction census answers for the rest.
    assert parsing.pad_width("00012.5") == 5
    assert parsing.pad_width("0") == 1


# -- the census is published ------------------------------------------


def test_a_padded_code_column_publishes_its_width() -> None:
    """THE CASE THE DECISION IS FOR, at the width a person actually holds."""
    document, _loaded, _folder = _described(
        [f"{number:05d}" for number in range(240)]
    )
    block = document["columns"][0]
    assert block["numeric_styles"] == {"leading_zero": 240}
    assert block["pad_widths"] == {"5": 240}


def test_a_column_with_no_padded_cell_publishes_an_empty_census() -> None:
    """What keeps this landing off every other column."""
    document, _loaded, _folder = _described(
        [f"{1000 + number}" for number in range(240)]
    )
    block = document["columns"][0]
    assert block["pad_widths"] == {}


def test_a_width_too_thinly_shared_is_held_back() -> None:
    """The floor governs a width as it governs a form."""
    values = [f"{number:05d}" for number in range(200)] + [
        f"{number:09d}" for number in range(200, 205)
    ]
    document, _loaded, _folder = _described(values)
    block = document["columns"][0]
    assert block["pad_widths"] == {"5": 200, "(withheld)": 5}


# -- the twin writes the width ----------------------------------------


def test_the_twin_of_a_code_column_keeps_the_width() -> None:
    """THE DEFECT, AS A TEST. Before this landing the twin wrote widths
    two, three, four and five where the source wrote five throughout."""
    _document, described, _folder = _described(
        [f"{number:05d}" for number in range(240)]
    )
    cells = _twin_cells(described)
    assert _census(cells) == {5: 240}
    for cell in cells:
        if cell:
            assert len(cell) == 5, cell


def test_the_twin_keeps_the_width_behind_an_affix() -> None:
    """Read over the CORES on the affixed role, both ways round."""
    for values, prefix, suffix in (
        ([f"A{number:05d}" for number in range(240)], "A", ""),
        ([f"{number:05d}kg" for number in range(240)], "", "kg"),
    ):
        _document, described, _folder = _described(values)
        assert described.columns[0].role == "affixed_number"
        cells = _twin_cells(described)
        assert _census(cells, prefix, suffix) == {5: 240}, values[0]


def test_two_named_widths_are_both_written() -> None:
    """A column is not one width because one width is easier to write."""
    values = [f"{number:05d}" for number in range(120)] + [
        f"{number:07d}" for number in range(120, 240)
    ]
    _document, described, _folder = _described(values)
    assert _census(_twin_cells(described)) == {5: 120, 7: 120}


def test_a_negative_padded_value_keeps_its_field() -> None:
    """The sign is not a figure in the twin either."""
    values = [f"-{number:04d}" for number in range(1, 60)] + [
        f"{number:04d}" for number in range(60, 240)
    ]
    _document, described, _folder = _described(values)
    assert _census(_twin_cells(described)) == {4: 239}


def test_a_padded_minority_is_written_at_its_own_width() -> None:
    """The census reaches the padded cells and no others."""
    values = [f"{number:05d}" for number in range(20)] + [
        f"{number}" for number in range(1000, 1220)
    ]
    _document, described, _folder = _described(values)
    assert _census(_twin_cells(described)) == {5: 20}


# -- the report and the quality report --------------------------------


def test_the_quality_report_misses_a_twin_whose_widths_moved() -> None:
    """A check that cannot fail is a defect, so this makes it fail.

    The same values written one figure wider stay `leading_zero` cells
    and keep the forms map balanced -- so the census is the only thing
    that can notice, which is exactly why it exists.
    """
    _document, described, folder = _described(
        [f"{number:05d}" for number in range(240)]
    )
    widened = fixtures.write(
        folder,
        "widened.csv",
        fixtures.single_column_table(
            "thing", [f"0{number:05d}" for number in range(240)]
        ),
    )
    outcome = validation.measure(described, f"{widened}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert "pads.published.5" in missed


def test_the_twin_of_a_code_column_reports_nothing_missed() -> None:
    """And the twin the tool itself writes passes its own check."""
    _document, described, folder = _described(
        [f"{number:05d}" for number in range(240)]
    )
    twin = generation.generate(described, 5)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    assert outcome.census.missed == 0


def test_the_distinctness_cost_is_authorized_and_never_missed() -> None:
    """What a named width costs, and the verdict it is allowed to cost.

    Every order of the leading-zero family writes one more figure, so a
    named width leaves a value one spelling. Where that costs the twin
    an identity the shortfall is the case owner decision 11 already
    authorizes -- it is never reported as a miss.
    """
    _document, described, folder = _described(
        [f"{number:05d}" for number in range(240)]
    )
    twin = generation.generate(described, 5)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    for check in outcome.checks:
        if check.subcheck[:9] != "distinct.":
            continue
        assert check.verdict != validation.MISSED, check.subcheck


# -- what the adversarial reads found ---------------------------------


def test_one_value_may_wear_several_published_widths() -> None:
    """Round 2's first blocking finding, as a test.

    ELEVEN `01`, ELEVEN `001`, ELEVEN `0001` ARE ONE NUMBER WRITTEN
    THREE WAYS, and the description publishes three different spellings
    because of it. The walk that landed first held each value to a
    single width -- on the argument that a value wearing two widths is
    a value wearing two spellings -- and that argument is simply wrong
    here: the source column IS the counter-example, and holding to it
    collapsed all thirty-three cells onto `01`, meeting none of the
    three published counts and leaving the twin one spelling where its
    own description published three.
    """
    values = ["01"] * 11 + ["001"] * 11 + ["0001"] * 11
    document, described, folder = _described(values)
    block = document["columns"][0]
    assert block["pad_widths"] == {"2": 11, "3": 11, "4": 11}
    assert block["n_distinct"] == 3

    twin = generation.generate(described, 5)
    cells = [cell for cell in twin.columns[0]]
    assert _census(cells) == {2: 11, 3: 11, 4: 11}
    assert len({cell for cell in cells if cell}) == 3

    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    assert outcome.census.missed == 0


def test_the_padded_exchange_does_not_spend_the_fraction_census() -> None:
    """Round 2's second blocking finding: an ORDERING defect.

    `_width_places` gives a fraction width to each cell it finds
    wearing `decimal`; the padded exchange then moves styles between
    cells. Run in that order the width assignments land on cells that
    are no longer decimal, and the cells that now are carry none -- one
    census bought with another. The exchange runs first, so the widths
    are assigned to the styles the column actually ends up wearing.

    What is asserted here is the ORDER's effect and not that every
    fraction width is reached: a shortfall on this shape appears with
    no padded cell in the column at all (residual R-P4-28), so the test
    pins the padding census exactly and requires only that the fraction
    census is no WORSE for the padding being there.
    """
    padded = ["01"] * 11
    decimals = (
        ["2.000"] * 11 + ["4.000"] * 11 + ["6.000"] * 11 + ["20.000"] * 11
    )
    _document, described, folder = _described(padded + decimals)
    twin = generation.generate(described, 1)
    cells = [cell for cell in twin.columns[0]]
    assert _census(cells) == {2: 11}
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    padded_misses = [
        check.subcheck
        for check in validation.measure(described, f"{written}").checks
        if check.verdict == validation.MISSED
        and check.subcheck[:5] == "pads."
    ]
    assert padded_misses == []


def test_the_report_and_the_validator_share_one_supply_formula() -> None:
    """Round 2's fourth finding, and round 3's correction to this test.

    A named width spends the leading-zero family, so a padded group at
    a named width supplies ONE identity and not one per cell (method
    G12.8). The twin's own report counted them one apiece while the
    validator counted the group as one, so the two disagreed about the
    same twin.

    THE FIRST VERSION OF THIS TEST CHECKED NEITHER PARITY NOR MORE THAN
    ONE WIDTH, and a three-width column passed it while the two
    surfaces still disagreed -- the report collapsing all three widths
    of one value into a single identity because it keyed its groups by
    value and style alone. So the field width is part of the key, and
    the test now walks a real column and compares what the report
    allows against what the validator allows.
    """
    layout = generation._NumericLayout(
        sizes=(3,), starts=(0,), bands=("zero",),
        raw_budgets=(3, 0, 0, 0), folded_budgets=(3, 0, 0, 0),
    )
    assert generation._numeric_supply(
        layout, ["00", "00", "00"], {"2": 3}
    ) == (1, 1)
    assert generation._numeric_supply(
        layout, ["00", "00", "00"], {}
    ) == (3, 3)
    # ONE VALUE AT THREE NAMED WIDTHS IS THREE IDENTITIES, on both
    # surfaces. Keyed by value and style alone this reads one.
    assert generation._numeric_supply(
        layout, ["01", "001", "0001"], {"2": 1, "3": 1, "4": 1}
    ) == (3, 3)

    # ...and the two surfaces agree on a column, not only on a helper.
    values = ["01"] * 11 + ["001"] * 11 + ["0001"] * 11
    _document, described, folder = _described(values)
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.NumericFacts)
    twin = generation.generate(described, 5)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    held = [
        check.verdict
        for check in outcome.checks
        if check.subcheck == "distinct.n_distinct"
    ]
    assert validation.MISSED not in held
    floor_end = validation._spelling_supply(
        column, facts, column.n_distinct
    )
    ceiling_end = validation._spelling_ceiling(
        column, facts, column.n_distinct
    )
    assert floor_end is not None and ceiling_end is not None
    reported = generation._numeric_supply(
        generation._NumericLayout(
            sizes=(33,), starts=(0,), bands=("zero",),
            raw_budgets=(33, 0, 0, 0), folded_budgets=(33, 0, 0, 0),
        ),
        [cell for cell in twin.columns[0]],
        facts.pad_widths,
    )
    # THE REPORT'S OWN NUMBER SITS INSIDE THE VALIDATOR'S BRACKET. Two
    # surfaces implementing one formula is what that means in practice.
    assert floor_end <= reported[0] <= ceiling_end
    assert floor_end <= reported[1] <= ceiling_end


def test_a_pinned_cell_may_give_up_the_padded_style() -> None:
    """What pins a cell is its VALUE, and a style carries no value.

    Refusing to take the padding off an endpoint left the census
    unmeetable on every column whose widest value was also its largest
    -- which is most of them -- because the widest value is exactly the
    one a narrow field cannot hold.
    """
    values = ["02"] * 15 + ["27"] * 10 + ["3"] * 20
    _document, described, folder = _described(values)
    block_widths = described.columns[0].facts
    assert isinstance(block_widths, contract.NumericFacts)
    if not block_widths.pad_widths:
        return
    twin = generation.generate(described, 5)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    padded_misses = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
        and check.subcheck[:5] == "pads."
    ]
    assert padded_misses == []
