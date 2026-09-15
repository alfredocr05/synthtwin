"""The gate for a blood pressure nobody declared: a round trip per shape.

WHAT WAS BROKEN (plan P4-D40). A blood-pressure column written
`int(gauss(128, 17))/int(gauss(79, 11))` -- `128/79` -- was described as
free text at 300 rows and at 2,000. The joined reading was asked only
under `--measurement`, so without the declaration the column published
no value, its twin held stand-in text, and neither position's ladder was
ever described or checked.

WHAT THE GATE IS. Each shape is described, built, and the TWIN IS
DESCRIBED AGAIN; both descriptions must read the column as joined
numbers with the same separator, the same count of joined cells and the
same ends and different-number count at each position, every twin cell
must be a reading and not stand-in text, and `synthtwin validate` must
exit 0 on the twin and on the real table. No declaration is passed
anywhere. The helper is stage 2's (`tests/test_stage2_round_trip.py`).

NEAR THE LONG-TAIL LINE THE READING IS THE SAMPLE'S, NOT THE COLUMN'S
(plan P4-D40, validation method V2.2-A2). Rule 9c stands after the
long-tail rule, so a column of slashed pairs is read as two numbers only
while no whole reading repeats in eleven rows. From about 1,200 rows of
even-rounded pressures and 3,500 of plain ones, a faithful twin -- whose
two positions are paired at random -- crosses that line where the real
table did not, and a plain `synthtwin profile` of the twin reads a long
tail. Before the validator read a checked file the way its description
was read, that twin was reported MISSED on its role on 22 runs of 80.
The second half of this file pins both halves: the plain re-profile does
cross, and the validator's own re-description of the twin still returns
every fact.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import collections
import pathlib
import random
import statistics

import pytest

from synthtwin import contract, profile, reading, validation
from tests.test_stage2_round_trip import _exit_of, _round_trip


def _pressures(count: int, seed: int, spaced: bool = False) -> "list[str]":
    """Systolic and diastolic as a chart writes them, one reading a cell."""
    draw = random.Random(seed)
    mark = " / " if spaced else "/"
    return [
        f"{int(draw.gauss(128, 17))}{mark}{int(draw.gauss(79, 11))}"
        for _each in range(count)
    ]


def _even_pressures(count: int, seed: int) -> "list[str]":
    """The same readings charted to the nearest even number, as many are."""
    draw = random.Random(seed)
    return [
        f"{2 * int(draw.gauss(128, 17) / 2)}/{2 * int(draw.gauss(79, 11) / 2)}"
        for _each in range(count)
    ]


def _as_checked(described_at: pathlib.Path, table_at: pathlib.Path) -> "dict[str, object]":
    """The first column as `synthtwin validate` re-describes the checked file.

    The reading, settings and carried-over names are the validator's own
    (`validation.settings_for`, `validation._described_pairs_here`), so
    this is the description the verdicts are counted from.
    """
    described = contract.load_profile(f"{described_at}")
    table = reading.read_table(
        f"{table_at}",
        first_row=reading.FIRST_ROW_NAMES,
        refusals=reading.REFUSALS_NAME_POSITIONS,
    )
    document = profile.build_document(
        table,
        validation.settings_for(described),
        [],
        [],
        [],
        [],
        True,
        validation._described_pairs_here(described, table),
    )
    columns = document["columns"]
    assert isinstance(columns, list)
    first = columns[0]
    assert isinstance(first, dict)
    return first


def _position(cells: "list[str]", mark: str, place: int) -> "list[int]":
    out: "list[int]" = []
    for cell in cells:
        parts = cell.split(mark)
        if len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
            out += [int(parts[place])]
    return out


CASES = [
    ("pressure-300-seed-3", 300, 3, False, "3"),
    ("pressure-300-seed-11", 300, 11, False, "11"),
    ("pressure-300-seed-29", 300, 29, False, "29"),
    ("pressure-2000-seed-5", 2000, 5, False, "5"),
    ("pressure-2000-seed-17", 2000, 17, False, "17"),
    ("spaced-pressure-800", 800, 23, True, "8"),
]


@pytest.mark.parametrize(
    "rows, data_seed, spaced, seed",
    [case[1:] for case in CASES],
    ids=[case[0] for case in CASES],
)
def test_an_undeclared_pressure_comes_back_as_two_numbers(
    tmp_path: pathlib.Path, rows: int, data_seed: int, spaced: bool, seed: str
) -> None:
    cells = _pressures(rows, data_seed, spaced)
    mark = " / " if spaced else "/"
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "trip", cells, seed=seed, header="bp"
    )
    for block in (first, second):
        assert block["role"] == "joined_numbers", block["role"]
        assert block["separator"] == mark
        assert block["n_parts"] == 2
        assert (block["n_joined"], block["n_unparsed"]) == (rows, 0)
    for place in range(2):
        real = _position(cells, mark, place)
        described = first["parts"][place]
        again = second["parts"][place]
        # The published ends are the real column's own, and the twin
        # described again carries the same ends and different-number
        # count at this position.
        assert described["percentiles"]["min"] == min(real)
        assert described["percentiles"]["max"] == max(real)
        assert described["n_distinct_values"] == len(set(real))
        assert again["percentiles"]["min"] == described["percentiles"]["min"]
        assert again["percentiles"]["max"] == described["percentiles"]["max"]
        # NOT EXACT AT A POSITION, and the shortfall predates rule 9c:
        # at 300 rows the twin holds one or two numbers fewer at a
        # position than the description publishes (52 of 53, 74 of 76),
        # and the DECLARED column at commit 53bb012 wrote the same twin
        # byte for byte. The count never runs over the published one.
        assert again["n_distinct_values"] <= described["n_distinct_values"]
        # Readings, not stand-in text: every twin cell is two whole
        # numbers, and each position's average is the real one's.
        twin = _position(written, mark, place)
        assert len(twin) == rows
        assert abs(statistics.fmean(twin) - statistics.fmean(real)) < 1.0
    assert len(set(written)) == len(set(cells))
    assert twin_exit == 0
    assert real_exit == 0
    # THE READING FROM THE VALUES IS THE DECLARED READING: the same
    # column named with `--measurement` builds the same twin, cell for
    # cell, so nothing the declaration's own tests pin is lost here.
    _declared = _round_trip(
        tmp_path / "declared", cells, flags=("--measurement", "bp"), seed=seed, header="bp"
    )
    assert _declared[2] == written
    # A declared column is carried over as a declaration, and the
    # reading from the values is carried over only where nobody declared.
    table = reading.read_table(f"{tmp_path / 'trip' / 'real-twin.csv'}")
    assert validation._described_pairs_here(
        contract.load_profile(f"{tmp_path / 'trip' / 'real-profile.json'}"), table
    ) == ["bp"]
    assert validation._described_pairs_here(
        contract.load_profile(f"{tmp_path / 'declared' / 'real-profile.json'}"), table
    ) == []


# Each case was measured to cross the line: the real table is read as
# joined numbers, and a plain re-profile of its twin reads a long tail.
# All four as first chosen exited 3 on the twin before the validator
# carried the reading over (commit ccffc6b), and the declared column
# passed on the same cells.
# TWO WERE RE-CHOSEN when landing 2b.1 merged into the integration of
# landings 2b.1 to 2b.5, as this landing's merge notes said they might
# be: its stratum cap holds a twin's repeated pairs down, so the twins of
# `pressure-4500-seed-6` (top repeat 9) and `even-pressure-1600-seed-7`
# (10) no longer crossed, and the test failed loudly as it should.
# `pressure-4500-seed-8` (real top repeat 9, twin 12) and
# `even-pressure-1400-seed-9` (real 10, twin 13) cross on the merged tree;
# at 1,600 even-rounded rows no seed tried crosses any more. The two
# replacements were measured on the merged tree only, where the reading
# is already carried over, not against the validator before ccffc6b.
NEAR_THE_LINE = [
    ("pressure-5000-seed-3", "plain", 5000, 3, "3"),
    ("pressure-4500-seed-8", "plain", 4500, 8, "3"),
    ("even-pressure-1200-seed-5", "even", 1200, 5, "3"),
    ("even-pressure-1400-seed-9", "even", 1400, 9, "3"),
]


@pytest.mark.parametrize(
    "form, rows, data_seed, seed",
    [case[1:] for case in NEAR_THE_LINE],
    ids=[case[0] for case in NEAR_THE_LINE],
)
def test_a_twin_past_the_long_tail_line_is_checked_as_two_numbers(
    tmp_path: pathlib.Path, form: str, rows: int, data_seed: int, seed: str
) -> None:
    cells = (
        _pressures(rows, data_seed)
        if form == "plain"
        else _even_pressures(rows, data_seed)
    )
    home = tmp_path / "trip"
    first, second, written, twin_exit, real_exit = _round_trip(
        home, cells, seed=seed, header="bp"
    )
    # The case is the one the gate is for: the real table sits below
    # the line and its faithful twin sits on or above it.
    assert collections.Counter(cells).most_common(1)[0][1] < 11
    assert collections.Counter(written).most_common(1)[0][1] >= 11
    assert first["role"] == "joined_numbers"
    assert second["role"] == "long_tail_labels"
    checked = _as_checked(home / "real-profile.json", home / "real-twin.csv")
    real_checked = _as_checked(home / "real-profile.json", home / "real.csv")
    assert real_checked == first
    assert checked["role"] == "joined_numbers"
    for key in ("separator", "n_parts", "n_joined", "n_unparsed", "part_min_widths"):
        assert checked[key] == first[key], key
    assert (first["n_joined"], first["n_unparsed"]) == (rows, 0)
    for place in range(2):
        real = _position(cells, "/", place)
        described = first["parts"][place]
        again = checked["parts"][place]
        assert described["percentiles"]["min"] == min(real)
        assert described["percentiles"]["max"] == max(real)
        assert again["percentiles"]["min"] == described["percentiles"]["min"]
        assert again["percentiles"]["max"] == described["percentiles"]["max"]
        assert again["n_distinct_values"] <= described["n_distinct_values"]
        twin = _position(written, "/", place)
        assert len(twin) == rows
        assert abs(statistics.fmean(twin) - statistics.fmean(real)) < 1.0
    assert twin_exit == 0
    assert real_exit == 0


def test_the_carried_reading_still_misses_a_file_that_is_not_pairs(
    tmp_path: pathlib.Path,
) -> None:
    # The reading is carried over, not the verdict: a file whose cells
    # are joined by a hyphen is not read as slashed pairs, falls to the
    # ordinary rules, and its role is reported MISSED.
    cells = _pressures(300, 3)
    home = tmp_path / "trip"
    first, _second, _written, twin_exit, _real_exit = _round_trip(
        home, cells, seed="3", header="bp", check_real=False
    )
    assert first["role"] == "joined_numbers" and twin_exit == 0
    other = home / "hyphen.csv"
    other.write_text(
        "bp\n" + "".join(cell.replace("/", "-") + "\n" for cell in cells),
        encoding="utf-8",
        newline="",
    )
    out = home / "check-hyphen"
    out.mkdir()
    code = _exit_of(
        ["validate", str(home / "real-profile.json"), "--twin", str(other), "--out-dir", str(out), "--replace"]
    )
    assert code == 3
    report = "".join(
        found.read_text(encoding="utf-8") for found in sorted(out.glob("*.txt"))
    )
    assert "axes.role [universal.role]: MISSED" in report
    assert _as_checked(home / "real-profile.json", other)["role"] != "joined_numbers"
