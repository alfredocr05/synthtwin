"""The quality report's mirror of the clock's knots (method G12.15; lane BT2, plan P4-D448).

On a description carrying a chain, the generator lays an eligible clock
column at G7A.4d's knots, or cuts its census groups at the `L0` edges, and
its own report draws G12.10's windows so. The quality report draws them
from the same cuts now (`validation.clock_cuts_mirrored`, then
`_clock_rank_windows` and `_clock_census_windows`), written out from the
method's clauses rather than imported from the generator; this file holds
the two writings to agreeing, each beside its mutant: the mirror
withdrawn, and the knots read as an uncut column's. It is built before the
landing that lets `validate` read a chain (lane CHON), as the
orchestrator's ruling (b) of 2026-10-25 asks.

Every table is invented here, below the owner's table floor, through the
library (the floor is the command's rule); the key is a fixed test key.
"""

import dataclasses
import json
import pathlib
import sys

import pytest

from synthtwin import calendar_clock, contract, generation, parsing, validation

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "tools" / "measurements"))
import kpi_band_totals as kpi  # noqa: E402

FLOOR = 11


def _switched(folder: pathlib.Path, name: str) -> "kpi._Described":
    header, body = kpi._ward(2000) if name == "ward" else kpi._hunt(2000)
    path = folder / f"{name}.csv"
    path.write_text(kpi.fixtures.rows_to_csv(header, body), encoding="utf-8", newline="\n")
    described = kpi._described(folder, name, path)
    assert described.loaded is not None
    return described


def _clocks(profile: contract.Profile) -> "list[contract.ColumnBlock]":
    return [column for column in profile.columns if isinstance(column.facts, contract.ClockFacts)]


@pytest.mark.parametrize("name", ["ward", "hunt"])
def test_the_mirror_cuts_every_clock_column_the_generator_cuts(tmp_path: pathlib.Path, name: str) -> None:
    """Each clock column the ladder names carries, in the quality report, the cuts the generator lays it at."""
    described = _switched(tmp_path, name)
    assert described.loaded is not None
    laid = generation._l0_columns(described.loaded)
    mirrored = validation.clock_cuts_mirrored(described.loaded)
    clocks = _clocks(mirrored)
    assert clocks
    for column in clocks:
        assert isinstance(column.facts, contract.ClockFacts)
        assert column.name in laid and laid[column.name][0] is not None
        assert column.facts.l0 == laid[column.name][0]


def test_a_description_with_no_chain_is_handed_back_as_it_is(tmp_path: pathlib.Path) -> None:
    """Every shipped run keeps its bytes: no ladder, no change."""
    described = _switched(tmp_path, "ward")
    assert validation.clock_cuts_mirrored(described.plain) is described.plain


def _census_windows(facts: contract.ClockFacts, parsed: int) -> "tuple[list[int], list[int]]":
    found = validation._clock_census_windows(facts, parsed)
    assert found is not None
    return found


def _generator_windows(facts: contract.ClockFacts, parsed: int) -> "tuple[list[int], list[int]]":
    """G12.10's census windows as the generator draws them for its own report: its cut pairs handed to the shared reading."""
    form = facts.clock_form
    unit = parsing.clock_step(form)
    assert facts.clock_step is not None and facts.low_tail is not None and facts.high_tail is not None
    body = (validation._clock_ordinal_or_zero(facts.low_tail.boundary, form), validation._clock_ordinal_or_zero(facts.high_tail.boundary, form))
    heaps = tuple((validation._clock_ordinal_or_zero(value, form), count) for value, count in facts.clock_heaps)
    windows = calendar_clock.clock_rank_windows(
        parsed, (facts.low_tail.rows, facts.high_tail.rows), body, facts.clock_census, heaps, form,
        max(1, facts.clock_step // unit), (), bool(facts.minute_census), generation._clock_cut_pairs(facts),
    )
    assert windows is not None
    return [unit * value for value in windows[0]], [unit * value for value in windows[1]]


def test_a_census_laid_clock_is_judged_by_its_halves(tmp_path: pathlib.Path) -> None:
    """The ward's `arrival`, laid on its census and step: the quality report's windows are the generator's cut ones, and differ from an uncut column's."""
    described = _switched(tmp_path, "ward")
    assert described.loaded is not None
    column = [column for column in _clocks(validation.clock_cuts_mirrored(described.loaded)) if column.name == "arrival"][0]
    facts = column.facts
    assert isinstance(facts, contract.ClockFacts) and facts.l0 is not None
    parsed = column.n_present - facts.n_unparsed
    assert _census_windows(facts, parsed) == _generator_windows(facts, parsed)
    assert _census_windows(dataclasses.replace(facts, l0=None), parsed) != _generator_windows(facts, parsed)


def _older(column: contract.ColumnBlock) -> "tuple[contract.ColumnBlock, contract.ClockFacts]":
    """The same column as an older description writes it: no step, census or heaps, so G7A.4 lays it on its knots."""
    facts = column.facts
    assert isinstance(facts, contract.ClockFacts)
    older = dataclasses.replace(facts, clock_step=None, clock_census=(), clock_heaps=(), minute_census=())
    return dataclasses.replace(column, facts=older), older


def _knots_both(tmp_path: pathlib.Path) -> "tuple[list[tuple[int, int]], list[tuple[int, int]]]":
    described = _switched(tmp_path, "ward")
    assert described.loaded is not None
    column = [column for column in _clocks(validation.clock_cuts_mirrored(described.loaded)) if column.name == "arrival"][0]
    column, facts = _older(column)
    assert facts.l0 is not None and facts.low_tail is not None and facts.high_tail is not None
    parsed = column.n_present - facts.n_unparsed
    laid = generation._clock_knots_laid(column, facts, FLOOR)
    form = facts.clock_form
    mirrored = validation._clock_cut_knots(
        facts, parsed, facts.low_tail.rows, parsed - 1 - facts.high_tail.rows,
        validation._clock_ordinal_or_zero(facts.low_tail.boundary, form),
        validation._clock_ordinal_or_zero(facts.high_tail.boundary, form),
    )
    return list(laid.knots), mirrored


def test_a_knots_laid_clock_is_read_between_the_generators_knots(tmp_path: pathlib.Path) -> None:
    """An older description's clock, laid by G7A.4: the quality report's knots are G7A.4d's, the generator's own."""
    generated, mirrored = _knots_both(tmp_path)
    assert mirrored == generated


def test_red_with_the_knots_read_as_an_uncut_columns(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the mirror's knots read off the uncut ladder (the quality report before this landing): they are not the generator's."""
    built = generation._clock_l0_knots
    monkeypatch.setattr(validation, "_clock_cut_knots", lambda facts, parsed, low_rank, high_rank, low_at, high_at: [])
    generated, mirrored = _knots_both(tmp_path)
    assert generated == sorted(generated) and built is generation._clock_l0_knots
    assert mirrored != generated


def test_red_with_the_mirror_withdrawn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: no cuts handed to the quality report: the census windows are an uncut column's, not the generator's."""
    monkeypatch.setattr(validation, "clock_cuts_mirrored", lambda description: description)
    described = _switched(tmp_path, "ward")
    assert described.loaded is not None
    column = [column for column in _clocks(validation.clock_cuts_mirrored(described.loaded)) if column.name == "arrival"][0]
    facts = column.facts
    assert isinstance(facts, contract.ClockFacts) and facts.l0 is None
    cut = generation._l0_columns(described.loaded)["arrival"][0]
    parsed = column.n_present - facts.n_unparsed
    assert _census_windows(facts, parsed) != _generator_windows(dataclasses.replace(facts, l0=cut), parsed)


# -- THE QUALITY REPORT ITSELF: `validation.measure` handed the chain's document ---------------


def _clock_windows(outcome: "validation.Outcome", names: "list[str]") -> "dict[tuple[str, str, str], str]":
    """Every check the quality report draws on the clock columns ``names``: its window as published."""
    return {
        (f"{check.column}", f"{check.fact}", f"{check.subcheck}"): f"{check.published}"
        for check in outcome.checks
        if check.column in names
    }


def _measured_three_ways(
    folder: pathlib.Path, monkeypatch: pytest.MonkeyPatch, older: bool
) -> "tuple[dict[tuple[str, str, str], str], dict[tuple[str, str, str], str], dict[tuple[str, str, str], str], list[str]]":
    """The ward's switched twin measured by the quality report: as a chained run is (the chain's document handed over), on the mirrored description, and with the mirror withdrawn.

    ``older`` makes `arrival` an older description's clock (no step,
    census or heaps), which G7A.4 lays on its knots, so its windows are
    read between G7A.4d's knots (`_clock_cut_knots`); otherwise both
    clocks are laid on their census and step and cut at their halves.
    """
    described = _switched(folder, "ward")
    assert described.loaded is not None
    loaded = described.loaded
    if older:
        loaded = dataclasses.replace(
            loaded, columns=tuple(_older(column)[0] if column.name == "arrival" else column for column in loaded.columns)
        )
    document = json.loads((folder / "ward-switched.json").read_text(encoding="utf-8"))
    twin = generation.generate_held(loaded, 0)
    path = kpi._twin_file(folder, described, loaded, twin, "older" if older else "census")
    names = ["arrival"] if older else [column.name for column in _clocks(loaded)]
    chained = _clock_windows(validation.measure(loaded, str(path), chain_document=document), names)
    mirrored = _clock_windows(validation.measure(validation.clock_cuts_mirrored(loaded), str(path), chain_document=document), names)
    monkeypatch.setattr(validation, "clock_cuts_mirrored", lambda description: description)
    withdrawn = _clock_windows(validation.measure(loaded, str(path), chain_document=document), names)
    return chained, mirrored, withdrawn, names


def _differs_on_every_clock(chained: "dict[tuple[str, str, str], str]", withdrawn: "dict[tuple[str, str, str], str]", names: "list[str]") -> bool:
    return all(any(key[0] == name and chained[key] != withdrawn.get(key) for key in chained) for name in names)


def test_a_chained_run_reads_a_census_clock_through_the_mirror(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane BT2's skeptic 1, item 1, and Codex's review, item 5: `validation.measure`, handed a chain's document, draws each census-laid clock's windows on the mirrored facts (`arrival` and `given_at`), and they are not an uncut column's. MUTANTS: the mirror's call in `measure` removed (V1), and the knots read as an uncut column's in `_clock_rank_windows` (V2)."""
    chained, mirrored, withdrawn, names = _measured_three_ways(tmp_path, monkeypatch, False)
    assert sorted(names) == ["arrival", "given_at"]
    assert chained == mirrored
    assert _differs_on_every_clock(chained, withdrawn, names)


def test_a_chained_run_reads_a_knots_clock_through_the_mirror(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The same for an older description's clock, laid by G7A.4 on its knots: the quality report reads its windows between G7A.4d's knots. MUTANTS V1 and V2."""
    chained, mirrored, withdrawn, names = _measured_three_ways(tmp_path, monkeypatch, True)
    assert chained == mirrored
    assert _differs_on_every_clock(chained, withdrawn, names)
