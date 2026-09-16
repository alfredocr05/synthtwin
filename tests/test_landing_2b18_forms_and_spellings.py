"""Landing 2b.18, second part: the case of a form, a label's shape, a code's spellings.

Three silent defects, each measured on the base before anything was
built, and each with both files passing their own description at exit 0:

- **LTM-6 on the five roles that publish `shape_forms`** (plan P4-D121).
  The form marked every letter `@` and the twin wrote capitals, so a
  column of 800 lower-case codes came back upper case on every row.
- **Landing 2b.12's carried item** (plan P4-D122). A long tail of codes
  at a floor of twenty wrote `group-N` for every stand-in the census
  owed no form, and the twin's mean cell length was 9.907 against 7.204.
- **The audit's missed item on mixed padding** (plan P4-D123). A count
  column writing `7`, `07`, `007` and `0` came back with six to eight
  spellings for four, making up numbers and spellings the source never
  had.

Every shape here is a ROUND TRIP -- the table is described, a twin is
built, the twin is DESCRIBED AGAIN, the published facts are asserted to
come back, and BOTH the twin and the real table are validated at exit
0 -- and each carries a PATTERN-MATCHING CHECK written against the twin
(a regular expression, a length test and a case test) and run UNCHANGED
on the real table, asserting the same match count on both.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import random
import re
import tempfile

import pytest

from synthtwin import contract, errors, parsing, profile, reading, taxonomy
from tests import fixtures
from tests.test_landing_2b18_identifier_layout import _round_trip

SOURCE_SEEDS = (1, 2, 3)


def _checks(real: "list[str]", twin: "list[str]", pattern: str, length, case):
    """The same three checks, written for the twin, run on both files."""
    rule = re.compile(pattern)
    return {
        "regex": (
            sum(1 for cell in real if rule.fullmatch(cell)),
            sum(1 for cell in twin if rule.fullmatch(cell)),
        ),
        "length": (
            sum(1 for cell in real if length(cell)),
            sum(1 for cell in twin if length(cell)),
        ),
        "case": (
            sum(1 for cell in real if case(cell)),
            sum(1 for cell in twin if case(cell)),
        ),
    }


def _same_on_both(checks: dict) -> None:
    for name, (real, twin) in checks.items():
        assert real == twin, (name, real, twin)


def _document(values: "list[str]", floor: int) -> dict:
    """A description of one column, built in memory at a chosen floor."""
    folder = pathlib.Path(tempfile.mkdtemp())
    rows = [[value, f"row{index % 7}"] for index, value in enumerate(values)]
    table = fixtures.write(
        folder, "thing.csv", fixtures.rows_to_csv(["value", "other"], rows)
    )
    return profile.build_document(
        reading.read_table(f"{table}"),
        taxonomy.Settings(small_cell_floor=floor),
        [],
    )


# ------------------------------------------------ LTM-6: the case of a form


def lower_codes(seed: int, rows: int = 800) -> "list[str]":
    """LTM-6's own shape, `e9z-1i1`: lower case throughout."""
    draw = random.Random(seed)
    letters = "abcdefghijk"
    return [
        f"{draw.choice(letters)}{draw.randrange(0, 9)}{draw.choice(letters)}"
        f"-{draw.randrange(0, 9)}{draw.choice(letters)}{draw.randrange(0, 9)}"
        for _row in range(rows)
    ]


def lower_two_forms(seed: int, rows: int = 800) -> "list[str]":
    """Two forms, `ab12` beside `ab1`, lower case throughout."""
    draw = random.Random(seed)
    return [
        f"{draw.choice('abcdefgh')}{draw.choice('abcdefgh')}"
        f"{draw.randrange(0, 99)}"
        for _row in range(rows)
    ]


def lower_long_tail(seed: int, rows: int = 800) -> "list[str]":
    """Four common lower-case codes and a tail of rare ones."""
    draw = random.Random(seed)
    common = ["ab1", "cd2", "ef3", "gh4"]
    built = []
    for _row in range(rows):
        if draw.random() < 0.8:
            built += [draw.choice(common)]
        else:
            built += [
                f"{draw.choice('xyzw')}{draw.choice('pqrs')}"
                f"{draw.randrange(0, 9)}"
            ]
    return built


def mixed_case_codes(seed: int, rows: int = 800) -> "list[str]":
    """Half `abc-123`, three tenths `ABC-123`, a fifth `Abc-123`."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        pick = draw.random()
        word = "".join(draw.choice("abcdefghjk") for _c in range(3))
        number = draw.randrange(100, 999)
        if pick < 0.5:
            built += [f"{word}-{number}"]
        elif pick < 0.8:
            built += [f"{word.upper()}-{number}"]
        else:
            built += [f"{word.capitalize()}-{number}"]
    return built


@pytest.mark.parametrize("seed", SOURCE_SEEDS)
def test_a_lower_case_code_column_comes_back_in_lower_case(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """Base: 800 real cells lower case and 0 twin cells, both at exit 0."""
    cells = lower_codes(seed)
    got = _round_trip(tmp_path, cells, seed="4", declared=False)
    assert got["source"]["role"] == "free_text"
    assert got["source"]["shape_forms"] == {"&%&-%&%": 800}
    assert got["twin_profile"]["shape_forms"] == got["source"]["shape_forms"]
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    _same_on_both(
        _checks(
            cells, got["cells"], r"[a-z][0-9][a-z]-[0-9][a-z][0-9]",
            lambda cell: len(cell) == 7, str.islower,
        )
    )


@pytest.mark.parametrize("seed", SOURCE_SEEDS)
def test_two_lower_case_forms_come_back_at_their_counts(
    tmp_path: pathlib.Path, seed: int
) -> None:
    cells = lower_two_forms(seed)
    got = _round_trip(tmp_path, cells, seed="7", declared=False)
    published = got["source"]["shape_forms"]
    assert set(published) == {"&&%", "&&%%"}, published
    assert got["twin_profile"]["shape_forms"] == published
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    _same_on_both(
        _checks(
            cells, got["cells"], r"[a-z]{2}[0-9]{2}",
            lambda cell: len(cell) == 3, str.islower,
        )
    )


@pytest.mark.parametrize("seed", SOURCE_SEEDS)
def test_a_lower_case_long_tail_writes_its_stand_ins_in_lower_case(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """Base: every stand-in -- 156 to 176 of 800 cells -- in capitals."""
    cells = lower_long_tail(seed)
    got = _round_trip(tmp_path, cells, seed="13", floor=20, declared=False)
    assert got["source"]["role"] == "long_tail_labels"
    assert got["source"]["shape_forms"] == {"&&%": 800}
    assert got["twin_profile"]["shape_forms"] == {"&&%": 800}
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    _same_on_both(
        _checks(
            cells, got["cells"], r"[a-z]{2}[0-9]",
            lambda cell: len(cell) == 3, str.islower,
        )
    )


@pytest.mark.parametrize("seed", SOURCE_SEEDS)
def test_a_mixed_case_column_names_its_lower_case_cells_and_says_its_limit(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """Both keys, the lower-case count exact -- and the capitalised cells not.

    THE LIMIT IS PINNED AS A LIMIT. A cell mixing the two cases is
    counted under the form's own key, which the twin writes in capitals,
    so a test for upper case alone counts MORE twin cells than real ones.
    A mark per position would carry it, and the floor would pool it.
    """
    cells = mixed_case_codes(seed)
    got = _round_trip(tmp_path, cells, seed="4", declared=False)
    published = got["source"]["shape_forms"]
    assert set(published) == {"&&&-%%%", "@@@-%%%"}, published
    assert got["twin_profile"]["shape_forms"] == published
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    _same_on_both(
        _checks(
            cells, got["cells"], r"[a-z]{3}-[0-9]{3}",
            lambda cell: len(cell) == 7, str.islower,
        )
    )
    upper_real = sum(1 for cell in cells if cell.isupper())
    upper_twin = sum(1 for cell in got["cells"] if cell.isupper())
    assert upper_twin == published["@@@-%%%"] > upper_real


def test_the_lower_case_key_is_named_only_under_the_disclosure_rule() -> None:
    """Each branch of C6-31a's rule, on a column small enough to read.

    `ab1` and its kin wear `@@%`. A lower-case count of ONE is never
    named, and neither is a remainder of one beside it at a floor of
    one; a remainder under the floor goes to the pool; a column whose
    values fold together names no lower-case key at all.
    """
    lower = [f"{a}{b}{n}" for a in "abcdefg" for b in "hijklmn" for n in range(3)]
    upper = [cell.upper() for cell in lower]

    def forms(values: "list[str]", floor: int) -> dict:
        return _document(values, floor)["columns"][0]["shape_forms"]

    # ONE lower-case cell at a floor of one: blind to case, as before.
    # (Every pair below is drawn from DIFFERENT codes, so no value folds
    # onto another and the fold rule at the end is not what decides it.)
    assert forms(upper[:40] + lower[40:41], 1) == {"@@%": 41}
    # Lower-case cells at the line and ONE cell beside them: blind to case.
    assert forms(lower[:40] + upper[40:41], 1) == {"@@%": 41}
    # Both at the line: both keys.
    assert forms(lower[:40] + upper[40:42], 1) == {"&&%": 40, "@@%": 2}
    # The rest under a floor of eleven: pooled.
    assert forms(lower[:40] + upper[40:45], 11) == {
        "&&%": 40, "(withheld)": 5,
    }
    # Every cell lower case: the lower-case key alone.
    assert forms(lower[:40], 11) == {"&&%": 40}
    # A column whose values fold together: blind to case, whatever else.
    assert forms(lower[:40] + upper[:5], 1) == {"@@%": 45}


def test_a_lower_case_key_counting_one_cell_is_refused_at_a_floor_of_one(
    tmp_path: pathlib.Path,
) -> None:
    """SF1's second line, which the loader battery cannot reach at eleven.

    At a floor of two or more SF1's floor already refuses a key under
    it, so the two-cell line matters only at a floor of one -- and the
    battery's base description is written at eleven. It is exercised
    here on a description made at one.
    """
    lower = [f"{a}{b}{n}" for a in "abcdefg" for b in "hijklmn" for n in range(3)]
    document = _document(lower[:40] + [c.upper() for c in lower[40:42]], 1)
    block = document["columns"][0]
    assert block["shape_forms"] == {"&&%": 40, "@@%": 2}
    for place, census in enumerate(
        ({"&&%": 41, "@@%": 1}, {"&&%": 1, "@@%": 41})
    ):
        block["shape_forms"] = census
        written = fixtures.write_profile(tmp_path, f"one-{place}.json", document)
        with pytest.raises(errors.ProfileError) as refusal:
            contract.load_profile(f"{written}")
        assert contract.INVARIANTS["SF1"] in str(refusal.value), census


def test_the_filling_writes_the_case_the_key_names() -> None:
    from synthtwin import generation

    assert generation._filled_form("&&-%", 0) == "aa-0"
    assert generation._filled_form("@@-%", 0) == "AA-0"
    assert generation._exponent_filling("%.%&%") == "0.0e0"
    assert generation._form_reading("%.%&%", False) == parsing.NUMBER
    assert parsing.census_form("ab1", {"&&%": 3}) == "&&%"
    assert parsing.census_form("ab1", {"@@%": 3}) == "@@%"
    assert parsing.census_form("Ab1", {"&&%": 3, "@@%": 3}) == "@@%"
    assert parsing.is_a_written_form("&&%")
    assert not parsing.is_a_written_form("&@%")


# ------------------------------------ P4-D122: the shape of a published label


def wide_codes(seed: int, rows: int = 2000) -> "list[str]":
    """Landing 2b.12's carried column: figures, a hyphen, capitals."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        size = draw.choice((1, 1, 1, 2, 4, 9))
        left = "".join(draw.choice("0123456789") for _c in range(size))
        right = "".join(draw.choice("ABCDEFGH") for _c in range(size))
        built += [f"{left}-{right}"]
    return built


# Source seed 1 is left out ON MEASUREMENT: its twin misses two form counts
# at exit 3 on the base as well, a settlement defect this landing did not
# cause and does not touch (plan P4-D122).
@pytest.mark.parametrize("seed", (401, 2))
def test_a_long_tail_at_a_floor_of_twenty_keeps_its_length_mix(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """Base: mean length 9.907 against 7.204, `group-N` everywhere."""
    cells = wide_codes(seed)
    got = _round_trip(tmp_path, cells, seed="7", floor=20, declared=False)
    assert got["source"]["role"] == "long_tail_labels"
    assert got["twin_profile"]["shape_forms"] == got["source"]["shape_forms"]
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    twin = got["cells"]

    def lengths(values: "list[str]") -> dict:
        counted: dict = {}
        for value in values:
            counted[len(value)] = counted.get(len(value), 0) + 1
        return counted

    assert lengths(twin) == lengths(cells)
    assert not [cell for cell in twin if cell.startswith("group-")]
    _same_on_both(
        _checks(
            cells, twin, r"[0-9]-[A-Z]",
            lambda cell: len(cell) <= 3, str.isupper,
        )
    )


# --------------------------------------- P4-D123: the spellings of a count


def zero_filled_answers(seed: int, rows: int = 500) -> "list[str]":
    """The audit's own column: `7`, `07`, `007` and `0`."""
    draw = random.Random(seed)
    return [draw.choice(("7", "07", "007", "0")) for _row in range(rows)]


def twelve_numbers_three_ways(seed: int, rows: int = 800) -> "list[str]":
    """Twelve numbers, each written with one, two or three figures."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        number = draw.randrange(0, 12)
        built += [draw.choice((str(number), f"{number:02d}", f"{number:03d}"))]
    return built


def _counts(values: "list[str]") -> dict:
    counted: dict = {}
    for value in values:
        counted[value] = counted.get(value, 0) + 1
    return counted


@pytest.mark.parametrize("seed", SOURCE_SEEDS)
@pytest.mark.parametrize(
    "make, pattern",
    [
        (zero_filled_answers, r"0[0-9]+"),
        (twelve_numbers_three_ways, r"0[0-9]+"),
    ],
)
def test_both_spellings_of_one_number_come_back_at_their_counts(
    tmp_path: pathlib.Path, seed: int, make, pattern: str
) -> None:
    """Base: six to eight spellings for four, `00` and `05` invented."""
    cells = make(seed)
    got = _round_trip(tmp_path, cells, seed="4", declared=False)
    assert got["source"]["role"] == "count"
    published = got["source"]["number_spellings"]
    assert published == _counts(cells)
    assert got["twin_profile"]["number_spellings"] == published
    assert _counts(got["cells"]) == _counts(cells)
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    _same_on_both(
        _checks(
            cells, got["cells"], pattern,
            lambda cell: len(cell) == 3, str.islower,
        )
    )


def test_the_spelling_census_is_all_or_nothing() -> None:
    """Each condition of contract 7.13, on its own."""

    def census(values: "list[str]", floor: int) -> dict:
        block = _document(values, floor)["columns"][0]
        assert block["role"] == "count"
        return block["number_spellings"]

    both = ["7"] * 20 + ["07"] * 20 + ["0"] * 20
    assert census(both, 1) == {"0": 20, "07": 20, "7": 20}
    # One spelling written by ONE cell: nothing, at a floor of one too.
    assert census(both + ["007"], 1) == {}
    # One spelling under the floor: nothing.
    assert census(both + ["007"] * 5, 11) == {}
    # Every number written one way: nothing, the field widths suffice.
    assert census(["7"] * 20 + ["12"] * 20 + ["3"] * 20, 1) == {}
    # The role does not move for any of them.
    assert _document(both + ["007"], 1)["columns"][0]["role"] == "count"


def test_a_census_whose_counts_do_not_add_up_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    both = ["7"] * 20 + ["07"] * 20 + ["0"] * 20
    document = _document(both, 11)
    block = document["columns"][0]
    for place, (census, rule) in enumerate(
        (
            ({"0": 20, "07": 20, "7": 5}, "SC1"),
            ({"0": 20, "07": 20, "7": 21}, "SC2"),
            ({"0": 20, "08": 20, "7": 20}, "SC2"),
            ({"07": 20, "7": 20, "8": 20}, "SC3"),
        )
    ):
        block["number_spellings"] = census
        written = fixtures.write_profile(
            tmp_path, f"{rule}-{place}.json", document
        )
        with pytest.raises(errors.ProfileError) as refusal:
            contract.load_profile(f"{written}")
        assert contract.INVARIANTS[rule] in str(refusal.value), (rule, census)


def test_a_lower_case_key_with_too_small_a_supply_is_not_named() -> None:
    """The small-supply rule asks the lower-case key for its OWN room.

    `a-` beside `z-` wears `@-`, which has fifty-two spellings to the
    census and clears a column of twenty-six values; its lower-case key
    `&-` has twenty-six, which a column of twenty-six different values
    would name in full. So the form is named blind to case.
    """
    letters = "abcdefghijklmnopqrstuvwxyz"
    values = [f"{letter}-" for letter in letters for _twice in range(2)]
    block = _document(values, 1)["columns"][0]
    assert block["shape_forms"] == {"@-": 52}, block["shape_forms"]


def test_a_census_of_more_spellings_than_a_set_of_categories_is_not_published() -> None:
    """SC2's ceiling, from the producer's side: a column of counts is never
    turned into a list of every value it holds."""
    values = []
    for number in range(40):
        values += [str(number)] * 3 + [f"0{number}"] * 3
    block = _document(values, 1)["columns"][0]
    assert block["role"] == "count"
    assert block["number_spellings"] == {}


def _validate_file(
    folder: pathlib.Path, cells: "list[str]", written: "list[str]",
    floor: "int | None" = None,
) -> "tuple[int, str]":
    """Describe ``cells``; validate a file holding ``written`` against it."""
    from tests.test_stage2_round_trip import _exit_of

    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(
            ["value", "other"],
            [[cell, f"row{index % 7}"] for index, cell in enumerate(cells)],
        ),
        encoding="utf-8",
        newline="",
    )
    described = ["profile", str(table), "--out-dir", str(folder), "--replace"]
    if floor is not None:
        described += ["--smallest-group", str(floor)]
    assert _exit_of(described) == 0
    other = folder / "other.csv"
    other.write_text(
        fixtures.rows_to_csv(
            ["value", "other"],
            [[cell, f"row{index % 7}"] for index, cell in enumerate(written)],
        ),
        encoding="utf-8",
        newline="",
    )
    checked = folder / "check"
    checked.mkdir()
    code = _exit_of(
        ["validate", str(folder / "real-profile.json"), "--twin", str(other),
         "--out-dir", str(checked), "--replace"]
    )
    report = (checked / "other-quality.txt").read_text(encoding="utf-8")
    return code, report


def test_a_file_writing_the_same_numbers_in_other_spellings_is_missed(
    tmp_path: pathlib.Path,
) -> None:
    """The validator's recount, where nothing ELSE a count publishes moves.

    Ten `07` become `08` and ten `8` become `7`: the same multiset of
    numbers, the same field widths, the same noughts and the same count
    of different spellings -- and a census of spellings that no longer
    holds. Only that census can miss it.
    """
    cells = ["7"] * 30 + ["07"] * 30 + ["8"] * 30 + ["08"] * 30 + ["0"] * 30
    moved = (
        ["7"] * 40 + ["07"] * 20 + ["8"] * 20 + ["08"] * 40 + ["0"] * 30
    )
    code, report = _validate_file(tmp_path, cells, moved)
    assert code == 3
    assert "spellings.published.07 [numeric.number_spellings]: MISSED" in report
    missed = [line for line in report.splitlines() if ": MISSED" in line]
    assert missed and all("number_spellings" in line for line in missed), missed


def test_a_file_writing_a_lower_case_column_in_capitals_is_missed(
    tmp_path: pathlib.Path,
) -> None:
    cells = lower_codes(1)
    code, report = _validate_file(
        tmp_path, cells, [cell.upper() for cell in cells]
    )
    assert code == 3
    assert "forms.published.&%&-%&% [free_text.shape_forms]: MISSED" in report


def lower_codes_beside_rare_capitals(seed: int, rows: int = 800) -> "list[str]":
    """Common lower-case codes, published; rare four-character capitals, held back."""
    draw = random.Random(seed)
    common = ["ab1", "cd2", "ef3", "gh4"]
    built = []
    for _row in range(rows):
        if draw.random() < 0.8:
            built += [draw.choice(common)]
        else:
            built += [
                f"{draw.choice('WXYZ')}{draw.choice('PQRS')}"
                f"{draw.randrange(10, 99)}"
            ]
    return built


@pytest.mark.parametrize("seed", SOURCE_SEEDS)
def test_published_lower_case_labels_pay_their_own_key(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """The cells already written pay the census under the key it files them.

    Every published level is lower case and settles `&&%` in full, and the
    held-back capitals owe `@@%%` alone. A walk reading the published
    cells blind to case would count them under `@@%`, find `&&%` unpaid
    and hand it stand-ins -- overpaying a key the table already met.
    """
    cells = lower_codes_beside_rare_capitals(seed)
    got = _round_trip(tmp_path, cells, seed="4", floor=20, declared=False)
    published = got["source"]["shape_forms"]
    assert "&&%" in published and "@@%%" in published, published
    assert got["twin_profile"]["shape_forms"] == published
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    _same_on_both(
        _checks(
            cells, got["cells"], r"[A-Z]{2}[0-9]{2}",
            lambda cell: len(cell) == 4, str.islower,
        )
    )


def short_lower_codes_beside_rare_longer_ones() -> "list[str]":
    """`a-` published; `b-` to `z-` held back at three rows; fifteen `ab-` once."""
    letters = "abcdefghijklmnopqrstuvwxyz"
    built = ["a-"] * 25
    for letter in letters[1:]:
        built += [f"{letter}-"] * 3
    for place in range(15):
        built += [f"{letters[place]}{letters[place + 1]}-"]
    random.Random(5).shuffle(built)
    return built


def test_the_published_shape_covers_the_largest_places_first(
    tmp_path: pathlib.Path,
) -> None:
    """G8.3b step 3: the shape's supply goes to the places writing most rows.

    `&-` has twenty-five spellings left and forty places are owed no form:
    twenty-five groups of three rows and fifteen of one. Spent in the
    order the walk meets them, singles first, ten groups of three would
    be `group-N`; spent largest first, every row of `b-` to `z-` wears
    the shape and only the fifteen single rows do not.
    """
    cells = short_lower_codes_beside_rare_longer_ones()
    got = _round_trip(tmp_path, cells, seed="4", floor=20, declared=False)
    assert got["source"]["shape_forms"] == {"(withheld)": 15}
    assert (got["twin_exit"], got["real_exit"]) == (0, 0)
    _same_on_both(
        _checks(
            cells, got["cells"], r"[a-z]-",
            lambda cell: len(cell) == 2, str.islower,
        )
    )
