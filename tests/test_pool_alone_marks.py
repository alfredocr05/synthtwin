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

    Mutations, each run: the lone pool written bare turns all forty
    parameters red, and so do six marks in place of seven; each run given
    to the first mark with room rather than the one holding the fewest
    turns `point` and `uneven` red at every seed (the two run); a bare
    remainder of the floor or more joining the pool turns `beside-bare`
    red at every seed; the cap at seven marks' worth rather than six
    turns `whole-numbers` red at the three seeds that mark past sixty;
    the cells to mark taken packed, `chosen = cells[:wanted]`, rather
    than spread, turns `beside-bare` red at every seed (its nineteen bare
    cells all above every marked one) and `whole-numbers` at the same
    three seeds (its one bare cell the largest).
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
    # AND THE CELLS LEFT BARE ARE NOT THE LARGEST (plan P4-D149): a bare
    # cell lies under some marked one, and two or more bare cells reach
    # past the smallest marked one as well. One bare cell alone is the
    # smallest groupable value, which is where the spread leaves it.
    bare = [_value(cell, comma) for cell in grouped if not _mark(cell, comma)]
    worn = [_value(cell, comma) for cell in marked]
    if bare:
        assert min(bare) < max(worn)
    if len(bare) >= 2:
        assert max(bare) > min(worn)


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


def test_a_lone_pool_is_checked_and_not_listed(tmp_path):
    """One obligation is either checked or listed, never both (plan P4-D352).

    Mutation, run: the listing's skip withdrawn -- the pool is listed as
    well as checked.
    """
    profile, written = _written(tmp_path)
    path = tmp_path / "twin.csv"
    names, built = fixtures.rows_at_the_floor("value", written)
    path.write_text(fixtures.rows_to_csv(names, built), encoding="utf-8", newline="")
    outcome = validation.measure(contract.load_profile(str(profile)), str(path))
    assert [c.verdict for c in outcome.checks if c.subcheck == "spelling.thousands_marks"] == ["HELD"]
    assert [item for item in outcome.listings if item.fact == "numeric.thousands_marks"] == []


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
    # AND THE REPORT NAMES NOTHING THAT IS NOT SO: every grouped cell kept
    # its mark, and the cells under a thousand never carried one, so the
    # P4-D265 recount has nothing to report. Mutation, run: the recount
    # counting every cell offered the mark -- 200 published against 70.
    profile = contract.load_profile(str(tmp_path / "real-profile.json"))
    assert [d for d in generation.generate(profile, 0).deviations if d.fact == fact] == []


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


def _trailing_negatives(seed: int, trailing: int, brackets: int, minus: int, sign: int,
                        positives: int, whole_others: bool = True, points: bool = True,
                        whole_share: float = 0.5, padded: int = 0,
                        signed: int = 0) -> "list[str]":
    """Negatives under a thousand: ``trailing`` written `12.50-`, the others as asked.

    ``points`` False writes the trailing ones `12.00-`, so every value is
    whole; ``whole_share`` of the positives are written with no point;
    ``padded`` negatives under a hundred are written three figures wide,
    `-007`; ``signed`` more positives are written `+12.50`.
    """
    draw = random.Random(seed)

    def figures(point: bool) -> str:
        if not point:
            return f"{draw.randint(1, 999)}"
        return f"{draw.randint(1, 999)}.{draw.randint(0, 99) if points else 0:02d}"

    out = [figures(True) + "-" for _ in range(trailing)]
    out += ["(" + figures(not whole_others) + ")" for _ in range(brackets)]
    out += ["-" + figures(not whole_others) for _ in range(minus)]
    out += ["−" + figures(not whole_others) for _ in range(sign)]
    out += [f"-{draw.randint(1, 99):03d}" for _ in range(padded)]
    out += ["+" + figures(True) for _ in range(signed)]
    out += [figures(draw.random() >= whole_share) for _ in range(positives)]
    draw.shuffle(out)
    return out


# A TRAILING MINUS IS WRITTEN ONLY ON FIGURES WITH A POINT, so the twin must
# keep a point on as many negatives as the census counts under it (the
# second skeptic of plan P4-D352). (name, cells, census).
TRAILING = (
    # the band counted under its commonest, a trailing minus, beside
    # twenty-seven whole-number negatives
    ("band-beside-whole", _trailing_negatives(601, 10, 9, 9, 9, 130), {"trailing_minus": 37}),
    ("band-all-points", _trailing_negatives(602, 10, 9, 9, 9, 130, whole_others=False),
     {"trailing_minus": 37}),
    # the named controls
    ("named", _trailing_negatives(701, 37, 0, 0, 0, 130), {"trailing_minus": 37}),
    ("named-beside-brackets", _trailing_negatives(802, 20, 20, 0, 0, 130),
     {"brackets": 20, "trailing_minus": 20}),
    ("named-whole-values", _trailing_negatives(901, 37, 0, 0, 0, 130, points=False, whole_share=1.0),
     {"trailing_minus": 37}),
    # beside padded whole negatives, which need the values nearest zero
    # (the skeptic of plan P4-D352 (5))
    ("named-beside-padded", _trailing_negatives(2401, 25, 0, 0, 0, 90, whole_share=1.0, padded=20),
     {"minus": 20, "trailing_minus": 25}),
    # a signed decimal beside them asks the walk over the negatives for
    # whole ones, which the padded fields need nearest zero too (the
    # skeptic of plan P4-D352 (6), round 3)
    ("signed-beside-padded",
     _trailing_negatives(2501, 25, 0, 0, 0, 60, whole_share=1.0, padded=20, signed=25),
     {"minus": 20, "trailing_minus": 25}),
    ("signed-beside-padded-wide",
     _trailing_negatives(2504, 40, 0, 0, 0, 70, whole_share=1.0, padded=30, signed=30),
     {"minus": 30, "trailing_minus": 40}),
)


@pytest.mark.parametrize("seed", SEEDS)
@pytest.mark.parametrize("name,cells,census", TRAILING, ids=[shape[0] for shape in TRAILING])
def test_the_twin_writes_as_many_trailing_minuses_as_the_census_counts(
    name, cells, census, seed, tmp_path
):
    """Every negative the census counts under a trailing minus is written with one.

    At e294a82 the two band shapes and the two named ones beside no
    whole value wrote 0 or 1 trailing minus, missing both notation checks
    at every seed, and the whole-valued one 34 of 37. Mutations, each
    run: `_trailing_owed` answering nought turns all forty red; the
    values step's walk for a trailing minus withdrawn turns every shape
    but the whole-valued one red at every seed; the exchange withdrawn
    turns `band-beside-whole` and `named-whole-values` red at every seed;
    the trailing minus taken in the contract's order turns
    `named-beside-brackets` red at every seed. At 8448e5f
    `named-beside-padded` wrote every trailing minus and missed its
    padded cells at every seed; the last walk of the values step taken in
    stratum order turns it red at every seed. At 331ad47 both
    `signed-beside-padded` shapes missed their padded cells and four
    style checks at every seed; the walk over the negative strata taken
    in stratum order turns both red at every seed, and its count after a
    chain taken over every stratum turns `signed-beside-padded-wide` red
    at every seed (its `decimal_plus`).
    """
    first, second, written, twin_exit, real_exit = _round_trip(tmp_path, cells, (), seed=seed)
    assert first["negative_notations"] == census
    assert second["negative_notations"] == census
    assert second["negative_form"] == first["negative_form"]
    assert twin_exit == 0 and real_exit == 0
    assert sum(1 for cell in written if cell.endswith("-")) == census["trailing_minus"]
    profile = contract.load_profile(str(tmp_path / "real-profile.json"))
    named = [d for d in generation.generate(profile, int(seed)).deviations if d.fact == "negative_notations"]
    assert named == []


def test_the_walk_nearest_zero_leaves_a_more_negative_stratum_its_number(tmp_path, monkeypatch):
    """A negative made whole never takes a number a stratum walked after it holds.

    Review item P2-C5-F3 refuses a candidate outside a stratum's own
    share where the share of a stratum the walk reaches LATER holds it.
    Beside a trailing minus the last walk of G6.4's values step takes the
    negative strata nearest zero first (the skeptic of plan P4-D352 (5)),
    so the strata it reaches later are the MORE negative ones, and a
    nearest whole number rounded away from zero is exactly the number
    such a stratum may be waiting for. Mutation, run: the guard read in
    stratum order rather than the walk's turns this red.
    """
    shape = [entry for entry in TRAILING if entry[0] == "named-beside-padded"][0]
    _round_trip(tmp_path, shape[1], (), seed="0")
    profile = contract.load_profile(str(tmp_path / "real-profile.json"))
    seen: "list[tuple[object, object, object, list[float], list[float]]]" = []
    walked = generation._whole_enough

    def watched(column, facts, layout, rungs, values):
        nonlocal seen
        after = walked(column, facts, layout, rungs, values)
        seen += [(column, layout, rungs, list(values), list(after))]
        return after

    monkeypatch.setattr(generation, "_whole_enough", watched)
    for seed in SEEDS:
        generation.generate(profile, int(seed))
    refused = 0
    for column, layout, rungs, before, after in seen:
        for place in range(1, len(after)):
            if layout.bands[place] != "negative" or after[place] == before[place]:
                continue
            nearest = generation._whole_valued(before[place])
            own = generation._share_of(place, layout, rungs, column.n_numeric)
            for other in range(1, place):
                theirs = generation._share_of(other, layout, rungs, column.n_numeric)
                if not theirs[0] <= nearest <= theirs[1] or own[0] <= nearest <= own[1]:
                    continue
                refused = refused + 1
                assert after[place] != nearest, (place, before[place], after[place], theirs)
    assert refused > 0, "no nearest whole number was ever a more negative stratum's"


# One column of 100 cells on a 101-rung ladder whose rungs stand at each
# stratum's start, so stratum k's share is (rung[start], rung[start + size]):
# (-6, -5.2), (-5.2, -1.7), (-1.7, -1.5), (-1.5, 0.1) and (0.1, 10). Sixty
# cells asked point-free, the pinned ends holding thirty-five of them.
CHAIN_STARTS = (0, 10, 50, 55, 75)
CHAIN_SIZES = (10, 40, 5, 20, 25)
CHAIN_LOWS = (-6.0, -5.2, -1.7, -1.5, 0.1)
CHAIN_VALUES = (-6.0, -2.8, -1.6, -0.9, 10.0)
# (census, the values G6.4's values step gives), worked by hand.
CHAIN_ANSWERS = (
    # The walk takes -0.9 first, to -1 (55 cells). -1.6's nearest, -2, is
    # outside its share and inside the share of -2.8, which the walk reaches
    # later; -1 is held and -3 too far, so -1.6 asks the holder of -1. That
    # holder's one other number is -2, refused the same way, and it covers
    # more cells, so it keeps -1: -1.6 keeps its point and -2.8 takes -3
    # (95 cells).
    ({"minus": 65, "trailing_minus": 10}, (-6.0, -3.0, -1.6, -1.0, 10.0)),
    # No trailing minus: stratum order, so -2.8 takes -3 first (75 cells).
    ({"minus": 75}, (-6.0, -3.0, -1.6, -0.9, 10.0)),
)


@pytest.mark.parametrize("census,answer", CHAIN_ANSWERS, ids=("trailing", "no-trailing"))
def test_the_chain_asks_in_the_walk_s_order_which_a_trailing_minus_sets(census, answer):
    """A number the chain asks for is refused where the walk reaches its share later.

    Review item P2-C5-F3's refusal holds inside R-P4-69's chain too, and
    beside a trailing minus "later" is later in the walk's order (method
    G6.4); with no trailing minus the walk is in stratum order. No test
    held either (the second skeptic of plan P4-D352 (6): withdrawn, the
    whole suite stood). Mutations, each run: the chain's own question
    read in stratum order gives -1.6 the -2 outright; the holder's
    question read so moves -0.9 to -2 and hands -1 on, and -2.8 keeps its
    point; the walk's order taken with no trailing minus gives -0.9 its
    -1 before -2.8 -- each turns its row red.
    """
    rungs = tuple(
        CHAIN_LOWS[max(k for k in range(5) if CHAIN_STARTS[k] <= place)]
        for place in range(100)
    ) + (10.0,)
    layout = types.SimpleNamespace(
        sizes=CHAIN_SIZES, starts=CHAIN_STARTS, bands=("negative",) * 4 + ("positive",)
    )
    column = types.SimpleNamespace(n_numeric=100)
    shares = [generation._share_of(k, layout, rungs, 100) for k in range(5)]
    assert shares == [(-6.0, -5.2), (-5.2, -1.7), (-1.7, -1.5), (-1.5, 0.1), (0.1, 10.0)]
    facts = types.SimpleNamespace(
        integer_valued=False,
        numeric_styles={"plain": 60, "decimal": 40},
        decimal_plus={},
        negative_notations=census,
    )
    assert tuple(generation._whole_enough(column, facts, layout, rungs, list(CHAIN_VALUES))) == answer


def test_the_walks_over_the_side_that_is_not_negative_keep_stratum_order():
    """Beside a trailing minus, only the walks reaching a negative take its order.

    Four strata of 10, 40, 20 and 30 cells on a 101-rung ladder, shares
    (-6, -5), (-5, 1.3), (1.3, 1.9) and (1.9, 10), values -6, -0.4, 1.4
    and 10; 80 cells asked point-free and 10 of the 50 negatives under a
    trailing minus. The walk beside is asked for 80 - (50 - 10) = 40 and
    the end 10 carries 30, so it asks 1.4, whose nearest whole number, 1,
    is outside its own share and inside -0.4's. In stratum order -0.4 is
    not after 1.4, so 1.4 takes 1; the last walk then gives -0.4 its -1,
    since 0 would carry it across zero. The two walks over the side that
    is not negative reach no negative, so a negative's share is nothing
    they wait for (the skeptic of plan P4-D352 (6), round 3: that order
    taken on every walk moves 22 of 277 fuzzed twins, changes no verdict,
    and no other test holds it). Mutation, run: the order taken on every
    walk gives 1.4 the 2 instead.
    """
    starts = (0, 10, 50, 70)
    lows = (-6.0, -5.0, 1.3, 1.9)
    rungs = tuple(
        lows[max(k for k in range(4) if starts[k] <= place)] for place in range(100)
    ) + (10.0,)
    layout = types.SimpleNamespace(
        sizes=(10, 40, 20, 30), starts=starts, bands=("negative",) * 2 + ("positive",) * 2
    )
    column = types.SimpleNamespace(n_numeric=100)
    shares = [generation._share_of(k, layout, rungs, 100) for k in range(4)]
    assert shares == [(-6.0, -5.0), (-5.0, 1.3), (1.3, 1.9), (1.9, 10.0)]
    facts = types.SimpleNamespace(
        integer_valued=False,
        numeric_styles={"plain": 80, "decimal": 20},
        decimal_plus={},
        negative_notations={"minus": 40, "trailing_minus": 10},
    )
    values = [-6.0, -0.4, 1.4, 10.0]
    assert tuple(generation._whole_enough(column, facts, layout, rungs, values)) == (
        -6.0, -1.0, 1.0, 10.0,
    )
