"""Review item P2-C2-F4: the numeric fallback names both cardinalities.

The contract gives numeric `n_distinct` and `n_distinct_folded` one
disposition with a named fallback: exact where the permitted spellings
supply the count, and inside a two-sided envelope where they cannot.
The method's own complete list of approximated facts names them, and
G12.8 fixes their envelope. Round 2 found neither measured: a genuine
column holding nought through four published five of each, the twin
wrote four of each and named both as deviations, and `Twin.approximations`
carried neither fact, neither bound, nor any report entry -- while the
report's closing sentence said every approximation had been measured.

WHAT THIS FILE HOLDS THE REPAIR TO:

1. both facts are measured on every column of numbers, with both ends
   of the envelope and the answer;
2. the ends are the ones G12.8 fixes -- the column's own SUPPLY of
   different spellings against the published count -- and they are
   finite and in order;
3. both reach the rendered report, with the published value, the
   achieved value and the range;
4. the bound is ABLE TO FAIL: a twin that wrote one spelling where its
   own cells could have carried two lands outside it;
5. the inventory that says which facts are approximated is read out of
   the contract's matrix rather than transcribed, so a conditional row
   cannot be left out of it again -- asserted in
   `tests/test_p2c1f4_approximation_bounds.py`, whose derivation this
   file's fixtures then exercise.
"""

import pathlib

import fixtures
from synthtwin import (
    canonical,
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
)


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> contract.Profile:
    """Write a one-column table, describe it, load the description."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("count", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    target = folder / "table-profile.json"
    target.write_text(
        canonical.serialize(document), encoding="utf-8", newline="\n"
    )
    return contract.load_profile(str(target))


def _found(
    twin: generation.Twin, fact: str
) -> generation.Approximation:
    """The one record for a named fact, or a failure saying it is absent."""
    for record in twin.approximations:
        if record.fact == fact:
            return record
    raise AssertionError(
        f"{fact} was not measured; measured: "
        f"{[record.fact for record in twin.approximations]}"
    )


# -- 1, 2 and 3. the column round 2 built -----------------------------


def test_both_cardinalities_are_measured_and_bounded_on_the_named_column(
    tmp_path: pathlib.Path,
) -> None:
    """Points 1 and 2, on the genuine input the item names.

    Nought through four, every cell plain. The published counts are five
    and five; the whole-number rule rounds two strata onto one value and
    `plain` has no second spelling of it, so the twin holds four. Both
    facts now carry the achieved value and both ends of the envelope,
    and the achieved value sits inside them.
    """
    loaded = _described(tmp_path, [str(n) for n in range(5)])
    block = loaded.columns[0]
    assert block.n_distinct == 5
    assert block.n_distinct_folded == 5

    twin = generation.generate(loaded, 0)
    for fact in ("n_distinct", "n_distinct_folded"):
        record = _found(twin, fact)
        assert record.published == "5"
        assert record.achieved == "4"
        assert record.lowest == "4"
        assert record.highest == "5"
        assert record.inside is True


def test_both_ends_are_finite_and_in_order_on_every_column_of_numbers(
    tmp_path: pathlib.Path,
) -> None:
    """Point 2's floor: a bound with one end is a bound in name only."""
    for step, values in enumerate((
        [str(n) for n in range(5)],
        [f"{n}.5" for n in range(1, 30)],
        ["0.0"] * 12 + ["00.0"] * 12 + [f"{n}.5" for n in range(1, 20)],
        fixtures.numbers(4242, 120, -50, 50),
    )):
        folder = tmp_path / f"case-{step}"
        folder.mkdir()
        loaded = _described(folder, values)
        assert isinstance(
            loaded.columns[0].facts, contract.NumericFacts
        ), f"case {step} is not a column of numbers"
        twin = generation.generate(loaded, 0)
        for fact in ("n_distinct", "n_distinct_folded"):
            record = _found(twin, fact)
            assert int(record.lowest) <= int(record.highest)
            assert int(record.lowest) >= 0
            assert record.inside is True


def test_both_reach_the_rendered_report(tmp_path: pathlib.Path) -> None:
    """Point 3: what a person opens, not what a record holds.

    A reader who wants to know how far a fact was permitted to move
    reads the approximation section of the report. Neither of the two
    counts appeared there before this repair.
    """
    loaded = _described(tmp_path, [str(n) for n in range(5)])
    twin = generation.generate(loaded, 0)
    text = rendering.report(loaded, twin)
    assert "how many different spellings this column holds" in text
    assert "allowed anywhere from 4 to 5" in text


# -- 4. the bound can fail --------------------------------------------


def test_the_bound_refuses_a_twin_that_wasted_its_own_supply(
    tmp_path: pathlib.Path,
) -> None:
    """Point 4, through the SHIPPED measurement rather than a copy of it.

    The mutant is the column a differently broken generator would have
    written: thirty-six decimal cells of zero all spelled the same way,
    where the cells' own style carries the leading-zero family and could
    have supplied thirty-six identities. The supply is what the envelope
    is drawn from, so the mutant lands outside it and the same run that
    measures it turns that into a named deviation.
    """
    values = ["0.0"] * 12 + ["00.0"] * 12 + ["000.0"] * 12
    loaded = _described(tmp_path, values)
    plan = generation.plan_generation(loaded)

    honest = generation.generate(loaded, 0)
    assert _found(honest, "n_distinct").inside is True

    measured = generation._approximations(
        loaded.columns[0], plan.columns[0], ["0.0"] * 36
    )
    broken = [
        record for record in measured if record.fact == "n_distinct"
    ]
    assert broken and broken[0].achieved == "1"
    assert broken[0].inside is False
    assert generation._bound_notes(measured), (
        "a measurement outside its own bound must join the deviations"
    )


def test_the_supply_counts_cells_a_style_could_have_told_apart() -> None:
    """The rule the envelope's lower end is drawn from, on its own.

    A `plain` group of one value supplies exactly one spelling however
    many cells it holds; every other style carries the leading-zero
    family, so its group supplies as many as it has cells. That is a
    statement about the construction, not a reading of the output, which
    is what makes it able to catch a twin that wasted its own supply.
    """
    layout = generation._NumericLayout(
        sizes=(3,), starts=(0,), bands=("zero",),
        raw_budgets=(3, 0, 0, 0), folded_budgets=(3, 0, 0, 0),
    )
    assert generation._numeric_supply(layout, ["0", "0", "0"]) == (1, 1)
    assert generation._numeric_supply(layout, ["0.0", "0.0", "0.0"]) == (3, 3)
