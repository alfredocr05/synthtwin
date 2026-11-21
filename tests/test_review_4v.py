"""Batch 4v's outside review: the items fixed in the one code round, each case red on its mutant.

Item 1 (HIGH): a supported age band written with its own years unit (`18-44 años`, `65-89 jahre`) is an age
whatever the column's name says; the measurement-name exemption no longer overrides the band reader, so the bands
from 90 are pooled.

Item 2 (HIGH): the trajectory floor is applied to the support of each released coefficient: a patient whose readings
are all at one time fixes no slope, so a grouping band whose trend rests on fewer than twice the floor of patients with
two times is never published, and a curve rests on patients with three.

Item 3: the loader's number roles are the roles the producer writes (`affixed_number`, `joined_numbers`,
`numbers_with_labels`).

Item 4: every trajectory entry has a line of its own in the patient lines, `not checkable` in words.

Item 5: a column whose recount is rejected is let go from the rule search, so no derived rule of it is published.

The tables are invented.
"""

import copy
import pathlib
import random

import pytest

import test_patient_own_trajectory as own
import test_review_4u_patient as four_u
from synthtwin import chain_validation, cli, patient_trajectory, results, taxonomy, validation

FLOOR = own.FLOOR


# -- ITEM 1 -----------------------------------------------------------------------------------------------------------

_BAND_UNITS = ("años", "jahre", "ans", "anni", "anos")


@pytest.mark.parametrize("unit", _BAND_UNITS)
def test_item_1_the_year_bands_of_a_measured_name_are_still_ages_and_the_old_ones_are_pooled(unit: str) -> None:
    """`risk_score` holding `18-44`, `45-64`, `65-89`, `90-94` and `95-99` in a foreign years unit, 200 people each:
    the measurement name no longer frees the column, so the reach holds it as ages; the same bands under a name no
    measurement reads are ages as before. MUTANT: `ages_named_in_cells` reading no band's unit (the column is then
    freed and the five bands are published)."""
    bands = [f"18-44 {unit}", f"45-64 {unit}", f"65-89 {unit}", f"90-94 {unit}", f"95-99 {unit}"]
    cells = [bands[row % 5] for row in range(20_000)]
    assert taxonomy.ages_named_in_cells(cells, False, frozenset())
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, measured=True) == taxonomy.SAFE_HARBOR_AGES
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR) == taxonomy.SAFE_HARBOR_AGES


def test_item_1_measurement_bands_with_no_age_unit_stay_free() -> None:
    """The measurement exemption stands for what is no age: bands of a score written without a years unit, and a
    saturation's qualifiers, are not ages. MUTANT: every band read as an age."""
    cells = [["0-10", "11-20", "21-30", "91-95", "96-100"][row % 5] for row in range(20_000)]
    assert not taxonomy.ages_named_in_cells(cells, False, frozenset())
    assert taxonomy.safe_harbor_reach(cells, False, frozenset(), FLOOR, measured=True) == ""


# -- ITEM 2 -----------------------------------------------------------------------------------------------------------


def _one_date_group(constant: int, moving: int) -> "tuple[list[float | None], list[list[int]], list[int], list[float | None]]":
    """1,000 patients of eight readings at distinct years in arm 0, and arm 1 of `constant` patients whose readings
    are all at one date and `moving` of readings at distinct dates (the review's table, scaled to the test floor)."""
    r = random.Random(41)
    values: "list[float | None]" = []
    rows: "list[list[int]]" = []
    arm: "list[int]" = []
    times: "list[float | None]" = []
    for patient in range(1000 + constant + moving):
        group = 0 if patient < 1000 else 1
        still = group == 1 and patient < 1000 + constant
        held: "list[int]" = []
        for j in range(8):
            held += [len(values)]
            times += [0.0 if still else float(j) * 0.5]
            values += [r.gauss(0.0, 1.0) + (1.7 * j * 0.5 if group == 1 and not still else 0.0)]
        rows += [held]
        arm += [group]
    return values, rows, arm, times


def test_item_2_a_band_resting_on_one_person_s_slope_is_never_published() -> None:
    """Arm 1 holds twice the floor of patients, all but one with every reading at one date: its trend is that one
    patient's slope. The grouping is not kept (nothing of it is published); with twice the floor of patients that
    span two times it is. MUTANT: the band counted by patients with two readings alone."""
    least = patient_trajectory.FLOOR_TIMES * FLOOR
    values, rows, arm, times = _one_date_group(least - 1, 1)
    entry = patient_trajectory.from_scores("y", values, rows, own._arm(arm), FLOOR, times)
    assert entry is not None and entry["by"] == []
    values, rows, arm, times = _one_date_group(0, least)
    entry = patient_trajectory.from_scores("y", values, rows, own._arm(arm), FLOOR, times)
    assert entry is not None and [group["column"] for group in entry["by"]] == ["arm"]  # type: ignore[union-attr]


def test_item_2_a_curve_rests_on_patients_with_three_times() -> None:
    """Patients whose four readings are at two times fix a slope and no bend (five of 700 span more): the curve is published as nought.
    MUTANT: the curve published from a fit that rests on no three times."""
    r = random.Random(43)
    values: "list[float | None]" = []
    rows: "list[list[int]]" = []
    arm: "list[int]" = []
    times: "list[float | None]" = []
    for patient in range(700):
        held: "list[int]" = []
        b0 = r.gauss(0.0, 1.0)
        for j in range(4):
            held += [len(values)]
            at = float(j) if patient < 5 else float(j // 2)
            times += [at]
            values += [b0 + 0.3 * at + 0.5 * at * at + r.gauss(0.0, 0.5)]
        rows += [held]
        arm += [patient % 2]
    entry = patient_trajectory.from_scores("y", values, rows, own._arm(arm), FLOOR, times)
    assert entry is not None and entry["curve"] == "0"
    assert all(set(group["curve"]) == {"0"} for group in entry["by"])  # type: ignore[union-attr]


# -- ITEM 3 -----------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("role", ["affixed_number", "joined_numbers", "numbers_with_labels"])
def test_item_3_the_loader_reads_the_entry_of_each_number_role_the_producer_writes(role: str) -> None:
    """The producer writes entries for columns of the three affixed, joined and labelled number roles; S35 reads them.
    MUTANT: the loader's role names as before (`affixed`, `joined`, `compound`)."""
    grain, classes, roles, bands, counted = own._loader_case()
    roles = dict(roles, sbp=role)
    patient_trajectory.checked(copy.deepcopy(grain), classes, roles, bands, counted)
    assert role in patient_trajectory.NUMBER_ROLES


# -- ITEM 4 -----------------------------------------------------------------------------------------------------------


def test_item_4_every_trajectory_entry_has_a_not_checkable_line(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """A described table with trajectory entries, checked against its own description: the patient lines carry one
    `trajectory` line per entry, with no verdict and the fixed words, so no entry goes unverified in silence. MUTANT:
    `patient_lines` reading no entry."""
    monkeypatch.setattr(cli, "_PATIENT_LAYER_SHIPPED", True)
    counts = [5] * 1000 + [15] * 1000
    sites = ["A" if p % 2 == 0 else "B" for p in range(2000)]
    text = four_u._visits_text(counts, sites, [0], 7, newest_first=False)
    table, profile_path, described = four_u._described_with_grain(tmp_path / "t", text)
    grain = described["relationships"]["grain"]  # type: ignore[index]
    entries = grain.get("trajectory", [])  # type: ignore[union-attr]
    assert entries, "the table must publish at least one entry"
    outcomes: "list[validation.Outcome]" = []
    measure = validation.measure

    def kept(*given: object, **named: object) -> validation.Outcome:
        outcome = measure(*given, **named)  # type: ignore[arg-type]
        outcomes.extend([outcome])
        return outcome

    monkeypatch.setattr(validation, "measure", kept)
    done, said = four_u._ran(["validate", str(profile_path), "--twin", str(table)])
    assert done.verdict in (results.NO_MISS, results.MISSED), said[-2000:]
    chain = outcomes[0].chain
    assert chain is not None
    lines = [one for one in chain.patient if one.kind == "trajectory"]
    assert sorted(one.subject for one in lines) == sorted(f"{entry['column']}" for entry in entries)
    assert all(one.verdict == "" and one.reason == chain_validation.TRAJECTORY_NOT_CHECKABLE for one in lines)
    assert "trajectory" in said


# -- ITEM 5 -----------------------------------------------------------------------------------------------------------


def test_item_5_the_rejected_branch_lets_the_readings_go() -> None:
    """The source reads the rejected branch letting its readings go: the call stands in the branch that names
    `REASON_RECOUNT` and follows the note of the column carried alone. MUTANT: the call removed."""
    source = (pathlib.Path(__file__).resolve().parents[1] / "src" / "synthtwin" / "chain.py").read_text(encoding="utf-8")
    at = source.index('ineligible += [{"column": name, "reason": REASON_RECOUNT}]')
    window = source[at:at + 700]
    assert "chain_order.let_go(gathered, name)" in window
