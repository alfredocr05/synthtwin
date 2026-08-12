"""Owner decision 8's leading-zero family has no ceiling.

Review item P2-C1-F5. The owner chose the leading-zero family over the
decimal-point pair for one stated reason: `0`, `00`, `000` and so on
supply as many different spellings of one value as a description can ask
for, so a numeric column's count of different spellings can always be
met. The implementation stopped looking for a new leading-zero order at
four thousand and ninety-six and then wrote a spelling it had already
used, which put the ceiling back and lost a published count -- and owner
decision 8 says that capacity failure cannot arise, so it is not one of
the corners the report is allowed to merely name.

The second half of the item is a diagnostic one. A column of nothing but
zeros built one value stratum per different spelling the description
allowed, so a column of four thousand zeros built four thousand strata
holding no cell at all. Those empty strata still took an end of the
ladder and still had their sign repaired, so the run named an endpoint
deviation about a value the twin never wrote -- a report entry with no
cell behind it, which makes every other entry harder to trust.
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

# One more than the ceiling the implementation used to impose, so the
# ladder of spellings has to pass through it rather than stop at it.
BEYOND_THE_OLD_CEILING = 4098


def _described(folder: pathlib.Path, values: "list[str]") -> contract.Profile:
    """Write a one-column table, describe it, and load the description."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("count", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return contract.load_profile(str(target))


def test_the_leading_zero_family_passes_the_old_ceiling(
    tmp_path: pathlib.Path,
) -> None:
    """A column asking for more spellings than the old ceiling gets them.

    The table holds `0`, `00`, `000` and so on, four thousand and
    ninety-eight of them, so the description publishes that many
    different spellings and that many different folded identities. Every
    one of those cells is the value zero: the count can only be met by
    the leading-zero family, which is exactly the capacity owner
    decision 8 says has no end.
    """
    folder = tmp_path / "ladder"
    folder.mkdir(parents=True, exist_ok=True)
    described = _described(
        folder, ["0" * (index + 1) for index in range(BEYOND_THE_OLD_CEILING)]
    )
    column = described.columns[0]
    assert column.n_distinct == BEYOND_THE_OLD_CEILING
    assert column.n_distinct_folded == BEYOND_THE_OLD_CEILING
    built = generation.generate(described, 0)
    present = [cell for cell in built.columns[0] if cell != ""]
    assert len(set(present)) == BEYOND_THE_OLD_CEILING
    assert len({parsing.folded(cell) for cell in present}) == (
        BEYOND_THE_OLD_CEILING
    )
    for cell in present:
        assert parsing.parse_number(cell) == 0.0, cell
    named = {deviation.fact for deviation in built.deviations}
    assert "n_distinct" not in named
    assert "n_distinct_folded" not in named


def test_a_column_of_zeros_names_no_endpoint_it_never_wrote(
    tmp_path: pathlib.Path,
) -> None:
    """No stratum with no cell in it, so no deviation about one.

    A published count of different spellings is not a count of different
    VALUES: the leading-zero family writes one value many ways. Only the
    negative and the positive cells are divided into strata, so a column
    holding nothing but zeros has exactly one stratum, and the ends of
    its ladder are the zero it actually wrote.
    """
    folder = tmp_path / "zeros"
    folder.mkdir(parents=True, exist_ok=True)
    described = _described(folder, ["0" * (index + 1) for index in range(40)])
    planned = generation.plan_generation(described)
    assert planned.columns[0].layout is not None
    layout = planned.columns[0].layout
    assert layout is not None
    for size in layout.sizes:
        assert size > 0, "a stratum was built with no cell in it"
    built = generation.generate(described, 0)
    named = [
        deviation
        for deviation in built.deviations
        if deviation.fact == "percentiles"
    ]
    assert named == [], [
        (deviation.published, deviation.achieved) for deviation in named
    ]
    present = [cell for cell in built.columns[0] if cell != ""]
    assert len(set(present)) == 40
    for cell in present:
        assert parsing.parse_number(cell) == 0.0, cell
