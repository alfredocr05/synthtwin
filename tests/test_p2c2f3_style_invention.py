"""Review item P2-C2-F3: the invention family lives inside every style.

Owner decision 8 chose the leading-zero family for one reason stated in
the decision itself: it has no ceiling and it changes no type a reader
infers, so a published count of different spellings can always be
reached. Decision 10 then made the FORM of each cell a published fact.
Round 2 found the two decisions pulling apart in the code: the family
was reached for only where the assigned style was literally
`leading_zero`, so a column reproducing a `decimal` or an exponent form
had one spelling of a value and no way to make a second. A genuine
input holding twelve copies each of three different decimal spellings
of zero published thirty-six `decimal` cells with three raw and three
folded identities, and the twin held one.

WHAT THIS FILE HOLDS THE REPAIR TO:

1. zeros written after the sign leave the contract's ladder where it
   was for every style but `plain`, and leave the value alone;
2. the genuine decimal case round 2 built holds its three identities
   and its thirty-six decimal cells at the same time;
3. the same holds inside both exponent cases;
4. `plain` has no family and says so, and the shortfall that follows is
   named rather than hidden -- which is the case review item P2-C2-F4
   bounds;
5. no zero is spent that the published count did not ask for, so a
   column already holding its count is left byte-plain.
"""

import pathlib

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)

FAMILY = ("leading_zero", "leading_plus", "decimal", "exponent_lower",
          "exponent_upper")


# The publication floor these fixtures were counted against. A floor of
# one became the default under the owner ruling recorded as plan
# amendment A-P4-37 -- contract invariant C5-S13 says that at a floor of
# one nothing whatever is held back -- and pooling is a SUBJECT here:
# the counts below are the counts a description publishes when a form
# carried by fewer than eleven cells is pooled into `(withheld)`. So the
# floor is stated rather than inherited, and it is the eleven every
# docstring in this file counts against.
SMALL_CELL_FLOOR = 11


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, describe it, load the description."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("amount", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=SMALL_CELL_FLOOR), []
    )
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return document, contract.load_profile(str(target))


def _present(twin: generation.Twin) -> "list[str]":
    """Every cell of the one column that holds anything."""
    return [cell for cell in twin.columns[0] if cell != ""]


# -- 1. what a zero after the sign does, and does not, change ---------


def test_a_zero_after_the_sign_keeps_the_style_and_the_value() -> None:
    """Point 1, on the shipped spelling rule and the shipped ladder.

    For each of the five styles that carry the family, three orders in a
    row must read back as the same value and classify as the same style,
    and the three must be different pieces of text -- which is the whole
    of what "an unbounded supply of spellings inside the style" means.
    """
    for style in FAMILY:
        for value in (0.0, 5.0, -12.5, 1e15):
            if style == "leading_plus" and value < 0:
                continue
            if style in ("plain", "leading_zero") and not (
                generation._carries_plainly(value, False)
            ):
                continue
            start = 1 if style == "leading_zero" else 0
            written = [
                generation._styled_number(value, style, start + step, False)
                for step in range(3)
            ]
            assert len(set(written)) == 3, (style, value, written)
            for text in written:
                assert parsing.parse_number(text) == value, (style, text)
                assert parsing.numeric_style(text) == style, (style, text)


def test_plain_is_the_one_style_with_no_family() -> None:
    """Point 4's first half: a zero in front of a plain spelling moves it.

    That is not a defect of the rule, it is what the contract's ladder
    says, and it is why a column whose whole map is `plain` reaches only
    as many spellings as it has different values.
    """
    assert parsing.numeric_style("5") == "plain"
    assert parsing.numeric_style("05") == "leading_zero"
    assert generation._styled_number(5.0, "plain", 3, False) == "5"


# -- 2 and 3. the genuine cases -----------------------------------------


def test_three_decimal_spellings_of_zero_survive_inside_the_decimal_form(
    tmp_path: pathlib.Path,
) -> None:
    """Point 2: the input round 2 built, end to end.

    Twelve copies each of `0.0`, `00.0` and `000.0`. The profile
    publishes thirty-six `decimal` cells, three raw identities and three
    folded ones. The twin used to keep the form and hold one identity;
    it now holds all three, so code that tests whether differently
    written zeros were normalized sees three groups here as it does on
    the real table.
    """
    values = ["0.0"] * 12 + ["00.0"] * 12 + ["000.0"] * 12
    document, loaded = _described(tmp_path, values)
    assert document["columns"][0]["numeric_styles"] == {"decimal": 36}
    assert document["columns"][0]["n_distinct"] == 3
    assert document["columns"][0]["n_distinct_folded"] == 3

    twin = generation.generate(loaded, 0)
    written = _present(twin)
    assert len(written) == 36
    assert all(
        parsing.numeric_style(cell) == "decimal" for cell in written
    )
    assert all(parsing.parse_number(cell) == 0.0 for cell in written)
    assert len(set(written)) == 3
    assert len({parsing.folded(cell) for cell in written}) == 3
    assert [
        note for note in twin.deviations
        if note.fact in ("n_distinct", "n_distinct_folded", "numeric_styles")
    ] == []


def test_three_exponent_spellings_of_one_value_survive_the_same_way(
    tmp_path: pathlib.Path,
) -> None:
    """Point 3: the same, inside the exponent form.

    The exponent styles are the ones that change the type a reader
    infers, so a column that published them had them in the real table
    and the twin owes them back with as many identities as the profile
    records.
    """
    values = ["1e2"] * 12 + ["01e2"] * 12 + ["001e2"] * 12
    document, loaded = _described(tmp_path, values)
    assert set(document["columns"][0]["numeric_styles"]) == {
        "exponent_lower"
    }
    assert document["columns"][0]["n_distinct"] == 3

    twin = generation.generate(loaded, 0)
    written = _present(twin)
    assert all(
        parsing.numeric_style(cell) == "exponent_lower" for cell in written
    )
    assert len({parsing.folded(cell) for cell in written}) == 3
    assert [
        note for note in twin.deviations
        if note.fact in ("n_distinct", "n_distinct_folded", "numeric_styles")
    ] == []


# -- 4 and 5. the two floors ------------------------------------------


def test_a_plain_column_that_cannot_reach_its_count_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """Point 4's second half: the shortfall speaks.

    Nought through four, every cell written plainly. The whole-number
    rule can round two neighbouring strata onto one value and `plain`
    has no second spelling of it, so the count of different values falls
    short -- and the report names it, with the range of review item
    P2-C2-F4 beside it.
    """
    document, loaded = _described(tmp_path, [str(n) for n in range(5)])
    assert set(document["columns"][0]["numeric_styles"]) == {"(withheld)"}

    twin = generation.generate(loaded, 0)
    written = _present(twin)
    assert all(parsing.numeric_style(cell) == "plain" for cell in written)
    named = [
        note.fact for note in twin.deviations
        if note.fact in ("n_distinct", "n_distinct_folded")
    ]
    assert named == ["n_distinct", "n_distinct_folded"]


def test_no_zero_is_spent_that_the_published_count_did_not_ask_for(
    tmp_path: pathlib.Path,
) -> None:
    """Point 5: a column already holding its count is left byte-plain.

    Spending a zero that was not needed carries the count PAST the
    published one, which is a miss in the other direction and just as
    visible to somebody grouping rows by the column. Forty different
    decimal values ask for forty identities and their own spellings
    supply them, so not one zero is written.
    """
    values = [f"{n}.25" for n in range(1, 41)]
    document, loaded = _described(tmp_path, values)
    assert document["columns"][0]["n_distinct"] == 40

    twin = generation.generate(loaded, 0)
    written = _present(twin)
    assert len(set(written)) == 40
    assert [
        note for note in twin.deviations
        if note.fact in ("n_distinct", "n_distinct_folded")
    ] == []
    for cell in written:
        assert not cell.startswith("0") or cell.startswith("0.")
