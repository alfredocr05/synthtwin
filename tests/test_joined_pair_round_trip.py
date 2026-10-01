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
import json
import pathlib
import random
import statistics

import pytest

import tail_rule
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
        # THE ENDS ARE WITHHELD AT EACH POSITION (stage 3, contract
        # 6.7a): a position's smallest and largest readings are held by
        # too few rows for the floor, so what the description states
        # about them is the GROUP beyond each boundary -- and the twin
        # described again states the same group and the same count of
        # different numbers at this position.
        assert described["percentiles"]["min"] is None
        assert described["percentiles"]["max"] is None
        assert tail_rule.stated(described["tails"]["low"]) == (
            tail_rule.expected(described, [float(one) for one in real])
        )
        assert tail_rule.stated(described["tails"]["high"]) == (
            tail_rule.expected(
                described, [float(one) for one in real], low=False
            )
        )
        assert described["n_distinct_values"] == len(set(real))
        assert again["tails"]["low"]["rows"] == (
            described["tails"]["low"]["rows"]
        )
        assert again["tails"]["high"]["rows"] == (
            described["tails"]["high"]["rows"]
        )
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
        # THE AVERAGE MOVES A LITTLE FURTHER SINCE STAGE 3 (landing
        # 3.3): the rows beyond each boundary are described by their
        # mean distance rather than named one by one, so the twin puts
        # them where those two moments say and not where the source's
        # own values were. Measured over these cases, the furthest a
        # position's average moves is 1.05 of a reading.
        assert abs(statistics.fmean(twin) - statistics.fmean(real)) < 1.5
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
# AND ONE WAS RE-CHOSEN AGAIN AT STAGE 3 (landing 3.3): the tail rule
# describes the rows beyond each position's two boundary rungs as a
# group, so a twin's repeats fall where those two moments put them and
# `even-pressure-1200-seed-5` (twin top repeat 9) no longer crosses.
# THE SEARCH WAS RUN TWICE, and the second time is the one that stands:
# the landing's own repairs -- a run cut at a listed tail's edge and the
# separation walking the stratum the tail does not name (method G5.3e)
# -- moved the first replacement's twin back to 10, one short of the
# line, so it was no witness either. Searched again over 1200 to 1600
# even-rounded rows at every data seed from 3 to 25, eighteen tables
# cross; `even-pressure-1500-seed-7` (real top 9, twin 11) is the one at
# the row count the replaced case used, and it validates at exit 0 on
# both files.
# AND ONE WAS RE-CHOSEN A THIRD TIME AT PLAN P4-D346: one listing rule
# now decides which tail of which role may name its values, and a
# position of this column whose tail named a value one row of it holds
# says its shape instead -- so a twin's repeats fall where the shape
# puts them and `even-pressure-1500-seed-7` (twin top repeat 9) no
# longer crosses. Searched the same way over 1,200 to 1,600
# even-rounded rows at every data seed from 3 to 25:
# `even-pressure-1500-seed-10` (real top 10, twin 11) is the one at the
# row count the replaced case used, and it validates at exit 0 on both
# files. `even-pressure-1400-seed-9` still crosses and is untouched.
NEAR_THE_LINE = [
    ("pressure-5000-seed-3", "plain", 5000, 3, "3"),
    ("pressure-4500-seed-8", "plain", 4500, 8, "3"),
    ("even-pressure-1500-seed-10", "even", 1500, 10, "3"),
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
        # The ends are withheld at each position (stage 3, contract
        # 6.7a) and the group beyond each boundary is what the
        # description states about those rows; the twin described again
        # states a group of the same size.
        assert described["percentiles"]["min"] is None
        assert described["percentiles"]["max"] is None
        assert tail_rule.stated(described["tails"]["low"]) == (
            tail_rule.expected(described, [float(one) for one in real])
        )
        assert again["tails"]["low"]["rows"] == (
            described["tails"]["low"]["rows"]
        )
        assert again["n_distinct_values"] <= described["n_distinct_values"]
        twin = _position(written, "/", place)
        assert len(twin) == rows
        assert abs(statistics.fmean(twin) - statistics.fmean(real)) < 1.0
    assert twin_exit == 0
    assert real_exit == 0


@pytest.mark.parametrize(
    "remainder", ("0120/080", "120/80.5"), ids=["a padded pair", "a pointed part"]
)
def test_a_real_table_with_one_pair_rule_9c_leaves_unparsed_meets_its_description(
    tmp_path: pathlib.Path, remainder: str
) -> None:
    """The integration verdict: the real table failed its own description.

    Rule 9c reads only plain whole pairs, so `0120/080` and `120/80.5` are
    left unparsed; the validator counted them into the positions anyway,
    and the real table exited 3 on `leading_zero` and on `remainder`.
    """
    cells = [f"{100 + i}/{50 + i % 61}" for i in range(299)] + [remainder]
    first, _second, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "trip", cells, seed="4", header="bp"
    )
    assert first["role"] == "joined_numbers"
    assert (first["n_joined"], first["n_unparsed"]) == (299, 1)
    assert real_exit == 0
    assert twin_exit == 0


@pytest.mark.parametrize(
    "spacing,unclear", ((" / ", False), ("/", True)), ids=["spaced", "one unclear cell"]
)
def test_a_column_read_as_pairs_from_its_values_is_always_asked(
    tmp_path: pathlib.Path, spacing: str, unclear: bool
) -> None:
    """The integration verdict: only a bare column whose every cell parsed was asked.

    A pair written `1234 / 5`, or a column with one cell that is not a
    pair, was read as joined numbers and published each position's
    average with no question put, while the bare column was asked.
    """
    draw = random.Random(9)
    cells = [f"{draw.randrange(1000, 9999)}{spacing}{draw.randrange(1, 9)}" for _ in range(240)]
    if unclear:
        cells[-1] = "unclear"
    folder = tmp_path / "asked"
    folder.mkdir()
    table = folder / "real.csv"
    table.write_text("ref\n" + "".join(cell + "\n" for cell in cells), encoding="utf-8", newline="")
    assert _exit_of(["profile", str(table), "--out-dir", str(folder), "--replace"]) == 0
    asked = json.loads((folder / "real-questions.json").read_text(encoding="utf-8"))["asked"]
    assert [entry["column"] for entry in asked] == ["ref"]
    saw = asked[0]["what_synthtwin_saw"]
    assert f"'{spacing}'" in saw
    assert ("are not" in saw) == unclear
    answers = [choice["answer"] for choice in asked[0]["answers_you_can_give"]]
    assert answers == ["keep", "code", "identifier"]


def test_a_pair_too_large_for_this_format_is_not_admitted_as_a_pair(
    tmp_path: pathlib.Path,
) -> None:
    """300 pairs opening `10 ** 310`: every part is past what binary64 holds.

    RULE 9c ADMITS A PART ON ITS SPELLING AND ON ITS REPRESENTABILITY,
    and the second half is what the Codex review of landing 2b.5 (item 4)
    added. `10 ** 310` is figures alone with no sign, no point and no
    padding, so the spelling test admitted it -- and then every statistic
    over that position was taken on a value binary64 cannot carry.

    Two shapes, and this pins both. Where EVERY cell is such a pair the
    column is not read as pairs at all: it falls to the rules below rule
    9c, exactly as a cell nothing can read always has. Where 299 ordinary
    pairs stand beside ONE too-large cell, the one is counted unparsed
    and the parse line decides the column, so `n_joined` counts the cells
    whose statistics were actually taken.

    WHAT THE OLD READING COST, which is why this expectation moved. Admitted
    on spelling, the all-too-large column was published as `joined_numbers`
    with a wholly null ladder, and the 299-plus-one column published
    `n_joined` 300 while the first position's statistics had used 299
    values -- a description its own loader then refused under invariant
    Q2, so `synthtwin profile` wrote a file `synthtwin generate` would not
    read (exit 1). Both now generate.
    """
    folder = tmp_path / "huge"
    folder.mkdir()
    table = folder / "real.csv"
    cells = [f"{10 ** 310 + place}/{place + 1}" for place in range(300)]
    table.write_text(
        "bp\n" + "".join(cell + "\n" for cell in cells), encoding="utf-8", newline=""
    )
    assert _exit_of(
        ["profile", str(table), "--out-dir", str(folder), "--replace"]
    ) == 0
    described = json.loads(
        (folder / "real-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    assert described["role"] != "joined_numbers", described["role"]
    # THE DESCRIPTION IS ONE THE LOADER READS, which the old reading's
    # was not: generation opens it and writes a twin.
    assert _exit_of(
        [
            "generate", str(folder / "real-profile.json"),
            "--out-dir", str(folder), "--seed", "4", "--replace",
        ]
    ) == 0

    # ...AND ONE TOO-LARGE CELL AMONG ORDINARY PAIRS IS UNPARSED.
    draw = random.Random(77)
    mixed = [
        f"{draw.randrange(100, 200)}/{draw.randrange(50, 99)}"
        for _each in range(299)
    ] + [f"{10 ** 310}/79"]
    other = tmp_path / "mixed"
    other.mkdir()
    beside = other / "real.csv"
    beside.write_text(
        "bp\n" + "".join(cell + "\n" for cell in mixed),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of(
        ["profile", str(beside), "--out-dir", str(other), "--replace"]
    ) == 0
    block = json.loads(
        (other / "real-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    assert block["role"] == "joined_numbers"
    assert block["n_joined"] == 299, block["n_joined"]
    assert block["n_unparsed"] == 1, block["n_unparsed"]
    assert _exit_of(
        [
            "generate", str(other / "real-profile.json"),
            "--out-dir", str(other), "--seed", "4", "--replace",
        ]
    ) == 0


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
