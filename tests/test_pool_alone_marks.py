"""A census of marks that is only a pool is written, named and checked (plan P4-D352).

THE DEFECT. Where every thousands-mark convention of a column stood below
the census floor, `thousands_marks` published only `{"(withheld)": N}`,
the twin wrote every groupable cell bare -- against contract C6-89, which
says a pooled remainder is written with a mark the census does not name --
and validation filed no check, so nothing was named: at 6a7a7d7, 0 of 230
twins over 46 pool-only shapes wrote a mark.

AND THE POOL ITSELF COULD SAY TOO MUCH. The two mixture censuses never
asked `parsing.census_pools`, which every other closed census asks (plan
P4-D222): seven marks of ten cells each at a floor of eleven published
`{"(withheld)": 70}`, a pool no six marks can hold below the floor, so it
said every mark was written and fixed each one's count at ten. A pool
over more cells than all but one convention can hold below the floor is
now counted under the commonest convention (ruling 6 of 2026-09-17), the
majority key follows it, and the loader refuses such a pool (TM1, NS2).

Each shape here is written by seeded neutral code, described, built at
five seeds, the twin described again, and the twin and the real table
validated. The rewrites then take a twin the method wrote and change
only its marks, which is how each verdict of C6-89 is pinned.
"""

import json
import pathlib
import random
import types

import pytest

from synthtwin import contract, errors, generation, parsing, validation
from tests import fixtures
from tests.test_stage2_round_trip import _round_trip

MARKS = parsing.GROUP_MARKS
LINE = 11
# SIXTY, the most seven marks can hold at a floor of eleven while all but
# one of them could still hold it below the floor (plan P4-D352).
AT_MOST = (9, 9, 9, 9, 8, 8, 8)


def _cells(seed: int, counts: "tuple[int, ...]", marks: "tuple[str, ...]",
           small: int, comma: bool = False, suffix: str = "", bare: int = 0,
           whole: bool = False) -> "list[str]":
    """Amounts: counts[k] cells past a thousand with marks[k], ``bare`` with none, ``small`` under it."""
    draw = random.Random(seed)
    point = "," if comma else "."
    out: "list[str]" = []

    def amount(mark: str, big: bool) -> str:
        figure = draw.randint(1000, 59999) if big else draw.randint(1, 999)
        text = f"{figure:,}".replace(",", "\0").replace("\0", mark)
        if whole:
            return text + suffix
        return f"{text}{point}{draw.randint(0, 99):02d}{suffix}"

    for mark, count in zip(marks, counts):
        out += [amount(mark, True) for _ in range(count)]
    out += [amount("", True) for _ in range(bare)]
    out += [amount("", False) for _ in range(small)]
    draw.shuffle(out)
    return out


COMMA_COLUMN = (".",) + MARKS[1:]
DECLARED = ("--decimal-comma", "value")
# (name, cells, flags, pool, distinct): distinct is True where every grouped
# value is its own run, so each mark must reach across the values.
SHAPES = (
    ("point", _cells(4, AT_MOST, MARKS, 130), (), 60, True),
    ("declared-comma", _cells(9, (10,) * 6, COMMA_COLUMN[1:], 90, comma=True), DECLARED, 60, True),
    ("affixed", _cells(12, (10,) * 6, MARKS[1:], 90, suffix=" kg"), (), 60, True),
    ("floor-31", _cells(2, (30,) * 6, MARKS[1:], 40), ("--smallest-group", "31"), 180, True),
    ("five-marks", _cells(3, (10,) * 5, MARKS[1:6], 100), (), 50, True),
    ("uneven", _cells(5, (10, 9, 8, 7, 6, 5, 4), MARKS, 120), (), 49, True),
    ("beside-bare", _cells(7, (9,) * 6, MARKS[:6], 100, bare=20), (), 54, True),
    ("whole-numbers", _cells(23, (10,) * 6, MARKS[1:], 90, whole=True), (), 60, True),
)
SEEDS = ("0", "1", "2", "3", "4")


def _value(cell: str, comma: bool) -> float:
    """The number a cell writes, read by this test alone."""
    text = cell[: -len(" kg")] if cell.endswith(" kg") else cell
    point = "," if comma else "."
    head, _mark, tail = text.partition(point)
    figures = "".join(ch for ch in head if ch.isdigit())
    return float(figures + ("." + tail if tail else ""))


def _mark(cell: str, comma: bool) -> str:
    """The mark between thousands, as written before any exchange, or ""."""
    text = cell[: -len(" kg")] if cell.endswith(" kg") else cell
    if comma:
        text = text.replace(",", "\0").replace(".", ",").replace("\0", ".")
    return parsing.thousands_mark(text)


def _bare(cell: str, comma: bool) -> str:
    """The cell with every mark between its thousands taken out."""
    point = "," if comma else "."
    cut = cell.rfind(point)
    whole, rest = (cell, "") if cut < 0 else (cell[:cut], cell[cut:])
    own = "." if comma else ","
    return "".join(ch for ch in whole if ch not in MARKS[1:] and ch != own) + rest


def _verdict(profile: pathlib.Path, cells: "list[str]", folder: pathlib.Path) -> str:
    """The verdict of `spelling.thousands_marks` on a file of these cells."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "rewritten.csv"
    names, built = fixtures.rows_at_the_floor("value", cells)
    path.write_text(fixtures.rows_to_csv(names, built), encoding="utf-8", newline="")
    outcome = validation.measure(contract.load_profile(str(profile)), str(path))
    found = [c.verdict for c in outcome.checks if c.subcheck == "spelling.thousands_marks"]
    return found[0] if found else "none filed"


def _twin(folder: pathlib.Path, cells, flags, seed):
    """One round trip, with the library's own deviations for the same seed."""
    first, second, written, twin_exit, real_exit = _round_trip(folder, cells, flags, seed=seed)
    profile = contract.load_profile(str(folder / "real-profile.json"))
    named = [
        (d.published, d.achieved)
        for d in generation.generate(profile, int(seed)).deviations
        if d.fact == "thousands_marks"
    ]
    return first, second, written, twin_exit, real_exit, named


def battery(folder: pathlib.Path) -> "tuple[int, int, int, int]":
    """The KPI's four numbers: unnamed, bare copies not missed, real missed, twins.

    UNNAMED counts twins whose own description does not publish the pool
    and whose report names no difference in `thousands_marks`; BARE COPIES
    NOT MISSED counts twins holding as many groupable cells as the pool
    whose copy with every mark taken out is not MISSED.
    """
    unnamed = bare_not_missed = real_missed = twins = 0
    for name, cells, flags, pool, _distinct in SHAPES:
        comma = flags[:1] == ("--decimal-comma",)
        for seed in SEEDS:
            place = folder / f"{name}-{seed}"
            first, second, written, _t, real_exit, named = _twin(place, cells, flags, seed)
            twins += 1
            if second["thousands_marks"] != first["thousands_marks"] and not named:
                unnamed += 1
            if real_exit != 0:
                real_missed += 1
            grouped = [c for c in written if _value(c, comma) >= 1000]
            if len(grouped) == pool:
                bare = [_bare(cell, comma) for cell in written]
                if _verdict(place / "real-profile.json", bare, place / "bare") != "MISSED":
                    bare_not_missed += 1
    return unnamed, bare_not_missed, real_missed, twins


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize(
    "name,cells,flags,pool,distinct", SHAPES, ids=[shape[0] for shape in SHAPES]
)
def test_the_twin_pools_its_marks_again_or_names_why(
    name, cells, flags, pool, distinct, seed, tmp_path
):
    """The twin's own description publishes the pool, or its report names why.

    Mutations, each run: `_pool_alone_places` writing every cell bare
    turns every parameter red; six marks in place of seven turns every
    parameter red; each mark's cells taken from the first free cell up
    turns the spread assertion red; a bare remainder of the floor or more
    joining the pool turns `beside-bare` red; the cap at seven marks'
    worth rather than six turns the twin's own census into a named mark
    wherever it marks more than sixty.
    """
    comma = flags[:1] == ("--decimal-comma",)
    line = int(flags[1]) if flags[:1] == ("--smallest-group",) else LINE
    first, second, written, twin_exit, real_exit, named = _twin(tmp_path, cells, flags, seed)
    assert first["thousands_marks"] == {"(withheld)": pool}
    assert first["group_separator"] == second["group_separator"] == ""
    assert twin_exit == 0 and real_exit == 0
    grouped = [c for c in written if _value(c, comma) >= 1000]
    marked = [c for c in grouped if _mark(c, comma)]
    by_mark: "dict[str, list[float]]" = {}
    for cell in marked:
        key = _mark(cell, comma)
        by_mark.setdefault(key, [])
        by_mark[key] += [_value(cell, comma)]
    # NO MARK REACHES THE FLOOR, AND ALL SEVEN ARE SHOWN.
    assert max(len(values) for values in by_mark.values()) <= line - 1
    assert len(by_mark) == 7
    groupable = len(grouped)
    if groupable == pool or groupable >= pool + line:
        # POOLED AGAIN: the same count, and a bare remainder only of the floor or more.
        assert second["thousands_marks"] == first["thousands_marks"]
        assert len(marked) == pool
        assert named == []
    else:
        # NAMED: the pool against the groupable cells, and the check withheld.
        assert named == [(str(pool), str(groupable))]
        assert _verdict(tmp_path / "real-profile.json", written, tmp_path / "again") == "WITHHELD"
        assert len(marked) == min(groupable, 6 * (line - 1))
    if distinct:
        # SPREAD, NOT PACKED (plan P4-D149): every mark reaches both halves.
        middle = sorted(v for values in by_mark.values() for v in values)[len(marked) // 2]
        for values in by_mark.values():
            assert min(values) < middle <= max(values)


def test_the_whole_number_shape_reaches_the_capped_leftover(tmp_path):
    """The shape above that pins the naming reaches more groupable cells than sixty.

    Sixty pooled at a floor of eleven carry at most sixty marks, so a
    sixty-first groupable cell is written bare and the twin's own
    description can publish no census; the report names 60 against 61.
    Mutation, run: naming only where the cells marked are not the pool --
    nothing is named at the seeds that reach it.
    """
    name, cells, flags, pool, _distinct = SHAPES[-1]
    reached = []
    for seed in SEEDS:
        _f, _s, _written, _t, _r, named = _twin(tmp_path / seed, cells, flags, seed)
        reached += named
    assert ("60", "61") in reached


def _written(tmp_path: pathlib.Path) -> "tuple[pathlib.Path, list[str]]":
    name, cells, flags, pool, _distinct = SHAPES[0]
    _f, _s, written, twin_exit, _r = _round_trip(tmp_path, cells, flags, seed="0")
    assert twin_exit == 0
    assert sum(1 for cell in written if parsing.thousands_mark(cell)) == pool
    return tmp_path / "real-profile.json", written


def _remarked(cell: str, mark: str) -> str:
    found = parsing.thousands_mark(cell)
    return cell.replace(found, mark) if found else cell


def test_a_bare_twin_is_missed(tmp_path):
    """C6-89: a pool written with no mark could have been named, so MISSED.

    Mutation, run: the pool-alone check withdrawn -- the verdict reads
    `none filed`.
    """
    profile, written = _written(tmp_path)
    assert _verdict(profile, [_remarked(c, "") for c in written], tmp_path / "v") == "MISSED"


def test_a_twin_naming_a_mark_the_census_pooled_is_missed(tmp_path):
    """C6-89: sixty cells with one space name a convention the census pooled."""
    profile, written = _written(tmp_path)
    assert _verdict(profile, [_remarked(c, " ") for c in written], tmp_path / "v") == "MISSED"


def test_a_short_twin_naming_marks_is_missed_before_any_gate(tmp_path):
    """A named mark is MISSED whatever the population (plan P4-D352).

    Fifty-nine grouped cells, thirty with a comma and twenty-nine with a
    space: the population is short of the pool of sixty, so the gate
    would withhold, but no twin the method writes names a mark at all.
    Mutation, run: the named branch asked after the gate -- WITHHELD.
    """
    profile, written = _written(tmp_path)
    out: "list[str]" = []
    grouped = 0
    for cell in written:
        if not parsing.thousands_mark(cell):
            out += [cell]
            continue
        grouped += 1
        if grouped == 60:
            out += ["999.50"]
            continue
        out += [_remarked(cell, "," if grouped <= 30 else " ")]
    assert _verdict(profile, out, tmp_path / "v") == "MISSED"


def test_a_twin_pooling_a_different_count_is_missed(tmp_path):
    """Eleven marks stripped: the file pools 49 beside 11 bare, not 60."""
    profile, written = _written(tmp_path)
    stripped = 0
    cells = []
    for cell in written:
        if stripped < 11 and parsing.thousands_mark(cell):
            cells += [_remarked(cell, "")]
            stripped += 1
        else:
            cells += [cell]
    assert _verdict(profile, cells, tmp_path / "v") == "MISSED"


def test_a_twin_splitting_differently_under_the_floor_is_held(tmp_path):
    """Which marks the pool held is not published, so a different split is HELD."""
    name, cells, flags, pool, _distinct = SHAPES[4]
    _f, _s, written, twin_exit, real_exit = _round_trip(tmp_path, cells, flags, seed="0")
    assert twin_exit == 0 and real_exit == 0
    moved = 0
    out = []
    for cell in written:
        if moved < 3 and parsing.thousands_mark(cell) == ",":
            out += [_remarked(cell, " ")]
            moved += 1
        else:
            out += [cell]
    assert moved == 3
    assert _verdict(tmp_path / "real-profile.json", out, tmp_path / "v") == "HELD"


def _negatives(seed: int, counts: "tuple[int, ...]", positives: int) -> "list[str]":
    """Amounts under a thousand: counts[k] negatives in the k-th notation."""
    draw = random.Random(seed)
    written = (
        lambda text: "-" + text,
        lambda text: "(" + text + ")",
        lambda text: "−" + text,
        lambda text: text + "-",
    )
    out: "list[str]" = []
    for notation, count in zip(written, counts):
        out += [notation(f"{draw.randint(1, 999)}.{draw.randint(0, 99):02d}") for _ in range(count)]
    out += [f"{draw.randint(1, 999)}.{draw.randint(0, 99):02d}" for _ in range(positives)]
    draw.shuffle(out)
    return out


# A POOL NO CLOSED CENSUS MAY PUBLISH (plan P4-D352): over more cells than
# all but one convention hold below the floor, counted under the commonest.
BAND = (
    ("marks-seventy", _cells(4, (10,) * 7, MARKS, 130), (), "thousands_marks",
     {",": 70}, "group_separator", ","),
    ("marks-apostrophe-first", _cells(8, (9, 9, 10, 9, 9, 9, 9), MARKS, 130), (),
     "thousands_marks", {"'": 64}, "group_separator", "'"),
    ("marks-declared", _cells(9, (10,) * 7, COMMA_COLUMN, 90, comma=True), DECLARED,
     "thousands_marks", {".": 70}, "group_separator", "."),
    ("notations-forty", _negatives(21, (10, 10, 10, 10), 120), (), "negative_notations",
     {"minus": 40}, "negative_form", "minus"),
    ("notations-brackets-first", _negatives(22, (9, 10, 9, 9), 120), (),
     "negative_notations", {"brackets": 37}, "negative_form", "brackets"),
)


@pytest.mark.parametrize(
    "name,cells,flags,fact,census,majority,word", BAND, ids=[shape[0] for shape in BAND]
)
def test_a_pool_that_would_name_every_convention_counts_under_the_commonest(
    name, cells, flags, fact, census, majority, word, tmp_path
):
    """Ruling 6 asked of the two mixture censuses (plan P4-D352).

    Seventy grouped cells, ten on each of seven marks at a floor of
    eleven, pooled `{"(withheld)": 70}`, which fixed each mark's count at
    ten. The census now names the commonest mark with all seventy -- the
    first in the contract's order on a tie -- the majority key follows it,
    and the twin and the real table both meet the description.
    Mutation, run: `_band_commonest` answering "" -- the pool comes back.
    """
    first, second, _written, twin_exit, real_exit = _round_trip(tmp_path, cells, flags, seed="0")
    assert first[fact] == census and first[majority] == word
    assert second[fact] == census and second[majority] == word
    assert twin_exit == 0 and real_exit == 0


def test_a_pool_six_marks_cannot_hold_below_the_floor_is_refused(tmp_path):
    """TM1: seventy pooled at a floor of eleven says every mark was written.

    Mutation, run: the band refusal withdrawn -- the description loads.
    """
    first, _s, _w, _t, _r = _round_trip(tmp_path, BAND[0][1], (), seed="0")
    assert first["thousands_marks"] == {",": 70}
    document = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))
    for column in document["columns"]:
        if column["name"] == "value":
            column["thousands_marks"] = {"(withheld)": 70}
            column["group_separator"] = ""
    edited = fixtures.write_profile(tmp_path, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    assert "TM1" in str(refused.value) and "70 grouped numbers are held back" in str(refused.value)


def test_a_pool_three_notations_cannot_hold_below_the_floor_is_refused(tmp_path):
    """NS2: forty negatives pooled at a floor of eleven says every notation was written.

    Mutation, run: the band refusal withdrawn -- the description loads.
    """
    first, _s, _w, _t, _r = _round_trip(tmp_path, BAND[3][1], (), seed="0")
    assert first["negative_notations"] == {"minus": 40}
    document = json.loads((tmp_path / "real-profile.json").read_text(encoding="utf-8"))
    for column in document["columns"]:
        if column["name"] == "value":
            column["negative_notations"] = {"(withheld)": 40}
    edited = fixtures.write_profile(tmp_path, "edited.json", document)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(edited))
    assert "NS2" in str(refused.value) and "40 negative numbers are held back" in str(refused.value)


def _places(pool: int, groupable: int, values: "list[float] | None" = None, floor: int = LINE):
    flags = [True] * groupable + [False] * 30
    worn, notes = generation._pool_alone_places(
        types.SimpleNamespace(name="value"), flags, floor,
        values if values is not None else [float(index) for index in range(len(flags))],
        pool,
    )
    marked = [mark for mark in worn if mark]
    return worn, marked, [(n.fact, n.published, n.achieved) for n in notes]


def test_a_leftover_under_the_floor_joins_the_pool_and_is_named():
    """Fifty pooled, fifty-five groupable: five cannot be the column's bare cells.

    Mutation, run: the pool split over the published fifty alone -- five
    bare and nothing marked past fifty.
    """
    _worn, marked, named = _places(50, 55)
    assert len(marked) == 55
    assert max(marked.count(mark) for mark in set(marked)) <= 10
    assert named == [("thousands_marks", "50", "55")]


def test_a_leftover_six_marks_cannot_carry_is_named():
    """Sixty pooled, sixty-five groupable: sixty marked, five bare, named.

    Mutation, run: the cap at seven marks' worth -- sixty-five marked,
    which the twin's own description counts under one mark.
    """
    _worn, marked, named = _places(60, 65)
    assert len(marked) == 60
    assert max(marked.count(mark) for mark in set(marked)) <= 10
    assert named == [("thousands_marks", "60", "65")]


def test_a_bare_remainder_at_the_floor_stays_bare():
    """Fifty-four pooled, sixty-five groupable: eleven are the column's own bare cells.

    Mutation, run: every leftover joining the pool -- sixty marked.
    """
    _worn, marked, named = _places(54, 65)
    assert len(marked) == 54
    assert named == []


def test_a_short_twin_is_named():
    """Sixty pooled, fifty-nine groupable: every one marked, the shortfall named."""
    _worn, marked, named = _places(60, 59)
    assert len(marked) == 59
    assert named == [("thousands_marks", "60", "59")]


def test_a_run_of_one_value_keeps_one_mark():
    """Fourteen values in runs of three, pooled 42: each value written one way.

    Mutation, run: the runs ignored, every cell dealt alone -- values
    written two or three ways.
    """
    values = [float(1000 + index // 3) for index in range(42)] + [0.0] * 30
    worn, marked, named = _places(42, 42, values)
    ways: "dict[float, set]" = {}
    for index in range(42):
        ways.setdefault(values[index], set()).add(worn[index])
    assert len(marked) == 42 and named == []
    assert all(len(marks) == 1 for marks in ways.values())
    assert len(set(marked)) == 7
