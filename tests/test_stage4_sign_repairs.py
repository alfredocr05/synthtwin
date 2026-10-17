"""Stage 4: G5.5's sign repairs without the square of the strata (plan P4-D387).

G5.5 repairs a stratum whose value has the wrong sign for its band, and on
a column written at one width (``grid``) it gives such a stratum, when it
is not pinned, the nearest point of the grid on its band's side of
nought that no OTHER stratum holds at that moment -- the repaired value
of each stratum before it, the drawn value of each after it -- and,
where every step within reach is held, the first such step, which
another stratum then shares (`generation._grid_step_of_sign`, G5.5a).
564c61a gathered those values again for every repair, and built the list
of every stratum's value again for each stratum it read there, so each
repair cost the square of the strata: 22 of the 26 s `generate` took
under a profiler at 8,000 rows of the Codex review's column of P4-D387,
and at 32,000 rows it ran past eleven CPU minutes. The values held are
now counted once, at the first repair, and kept as the strata are
repaired, and each band's walk begins where its last one stopped while
nothing a step on that side can read back as has been let go -- nought
included, which the first steps of a grid of 324 places or more read
back as (at 330 places every step of a walk over fewer than 2.4 million
strata), and which d36627f missed.

Nothing written moves, so 564c61a's two functions are kept here as this
file's ORACLE (`*_as_built`, their text with the docstrings left out),
asked the same questions and required to give the same answers, and a
growth measure that needs no clock -- the lines the interpreter runs
inside the call, in every frame -- is taken at N and at 2N strata. The
oracle is required to grow at least three times on the same arguments,
so the measure is known to see the defect rather than assumed to. A
builtin runs as one line however many values it reads, so the measure
is taken again on values that run a line of their own each time a
builtin hashes or compares one, by `==` or by order (`_Counted`): three
repairs that do the square of the strata inside builtins -- one
searching a list of the values held, one building their dict again and
one sorting them again at every repair -- are required to show it
there, where the lines alone do not. So a repair that hashes or
compares the values every stratum holds inside builtins at each repair
is seen too; one that only copies them is not, and that is the accepted
limit, bounded only by the seconds K-S4-05's evidence records.
"""

from __future__ import annotations

import csv
import io
import math
import pathlib
import random
import sys
import tempfile
import types

import pytest

import fixtures
from synthtwin import contract, generation, profile, reading, rendering, taxonomy

# What a pass whose work grows with the strata may grow by when they
# double, and what the replaced pass must reach on the same arguments.
LINEAR_AT_MOST = 2.5
SQUARE_AT_LEAST = 3.0


# -- the oracle: 564c61a's two functions as it shipped them ----------------


def _sign_repairs_as_built(column, facts, layout, rungs, values, grid=-1):
    total = len(values)
    notes = []
    repaired = []
    for place in range(total):
        band = layout.bands[place]
        value = values[place]
        fallback = generation._sign_fallback(band, rungs)
        wrong = False
        if band == generation._BAND_NEGATIVE and value >= 0.0:
            wrong = True
        if band == generation._BAND_POSITIVE and value <= 0.0:
            wrong = True
        pinned = place == 0 or (place == total - 1 and total >= 2)
        if wrong and grid > 0 and not pinned:
            held = {
                (repaired + values[place:])[other]: 1
                for other in range(total) if other != place
            }
            repaired += [
                _grid_step_of_sign_as_built(
                    band, rungs, grid, held, total, kept=facts.kept_stand_ins
                )
            ]
            continue
        if wrong:
            if band == generation._BAND_NEGATIVE and fallback >= 0.0:
                fallback = -1.0
            if band == generation._BAND_POSITIVE and fallback <= 0.0:
                fallback = 1.0
            if facts.integer_valued:
                fallback = generation._whole_valued(fallback)
            value = fallback
            if pinned:
                notes += [
                    generation._deviation(
                        column.name,
                        "percentiles",
                        f"{values[place]}",
                        f"{value}",
                        "The end of this column's ladder and its counts of "
                        "negative and zero values cannot both hold, so the "
                        "twin keeps the counts and that end moves.",
                    )
                ]
        repaired += [value]
    return repaired, notes


def _grid_step_of_sign_as_built(band, rungs, grid, held, total, kept=()):
    negative = band == generation._BAND_NEGATIVE
    unit = generation._ten_to(grid)
    first = 0.0
    for step in range(1, total + 2):
        text = f"{step // unit}.{step % unit:0{grid}d}"
        if negative:
            text = "-" + text
        candidate = float(text)
        if rungs is not None and negative and candidate < rungs[0]:
            break
        if rungs is not None and not negative and candidate > rungs[-1]:
            break
        if step == 1:
            first = candidate
        if candidate not in held and not generation._is_a_stand_in(candidate, kept):
            return candidate
    if first != 0.0:
        return first
    return -1.0 if negative else 1.0


# -- the measure -----------------------------------------------------------


def lines_run(function: "object", *arguments: object) -> int:
    """How many lines the interpreter runs answering ``function(*arguments)``, in every frame.

    Every frame is counted, so a comprehension is counted whether it runs
    in a frame of its own (Python 3.10 and 3.11) or inline (3.12 on).
    """
    counted = [0]

    def local(frame: object, event: str, argument: object) -> object:
        if event == "line":
            counted[0] += 1
        return local

    def calls(frame: object, event: str, argument: object) -> object:
        return local

    previous = sys.gettrace()
    sys.settrace(calls)  # type: ignore[arg-type]
    try:
        function(*arguments)  # type: ignore[operator]
    finally:
        sys.settrace(previous)
    return counted[0]


def _same(ours: "tuple[list[float], list[object]]", theirs: "tuple[list[float], list[object]]") -> bool:
    """The same values, nought's sign and NaN included, and the same notes."""
    return [repr(value) for value in ours[0]] == [repr(value) for value in theirs[0]] and ours[1] == theirs[1]


class _Counted(float):
    """A value that runs a line of its own each time it is hashed or compared, by ``==`` or by order.

    A builtin runs as one line however many values it reads -- a list
    searched for a value, a dict built from a list of them -- so `lines_run`
    alone lets a repair do the square of the strata inside one. Handed
    these, each value a builtin hashes, compares or sorts (``sorted``,
    ``min``, ``max``) is a line too; one it only copies is not. The
    number, its sign and its text are the float's own.
    """

    __slots__ = ()

    def __hash__(self) -> int:
        return float.__hash__(self)

    def __eq__(self, other: object) -> bool:
        return float.__eq__(self, other)

    def __ne__(self, other: object) -> bool:
        return float.__ne__(self, other)

    def __lt__(self, other: float) -> bool:
        return float.__lt__(self, other)

    def __le__(self, other: float) -> bool:
        return float.__le__(self, other)

    def __gt__(self, other: float) -> bool:
        return float.__gt__(self, other)

    def __ge__(self, other: float) -> bool:
        return float.__ge__(self, other)


def _handed(values: "list[float]", counted: bool) -> "list[float]":
    """A fresh list of ``values``, each one a `_Counted` where ``counted``."""
    if counted:
        return [_Counted(value) for value in values]
    return list(values)


# -- the Codex review's column, through the real producer -------------------


def codex_column(rows: int) -> "list[str]":
    """The Codex review's column of P4-D387, which the producer reads on a grid of two places.

    A hundredth of the rows hold `0.1` and a hundredth `0.10000000000000002`,
    each written one zero longer than the last; the rest count up in fives,
    three in ten of them with a quarter. Read on the grid, the strata just
    above the column's one nought fall on `0.00`, so a hundredth of the
    strata, less eleven, take G5.5's grid step of sign.
    """
    hundredth = rows // 100
    values = ["0.1" + "0" * place for place in range(hundredth)]
    values += ["0.10000000000000002" + "0" * place for place in range(hundredth)]
    values += [str(5 * place) if place % 10 < 7 else str(5 * place + 0.25) for place in range(rows - 2 * hundredth)]
    return values


def _table(values: "list[str]") -> str:
    """A one-column table of ``values``, every cell quoted."""
    out = io.StringIO()
    writer = csv.writer(out, quoting=csv.QUOTE_ALL, lineterminator="\n")
    writer.writerow(["value"])
    for value in values:
        writer.writerow([value])
    return out.getvalue()


def described(values: "list[str]") -> contract.Profile:
    """A one-column table of ``values`` described by the real producer and loaded."""
    with tempfile.TemporaryDirectory() as home:
        folder = pathlib.Path(home)
        path = fixtures.write(folder, "table.csv", _table(values))
        document = profile.build_document(reading.read_table(str(path)), taxonomy.Settings(), [])
        target = fixtures.write_profile(folder, "table-profile.json", document)
        return contract.load_profile(str(target))


_HANDED: "dict[int, tuple[contract.Profile, tuple[object, ...]]]" = {}


def repairs_handed(rows: int) -> "tuple[contract.Profile, tuple[object, ...]]":
    """The description of the Codex column of ``rows`` rows, and what its twin's build hands G5.5.

    Kept for the module, so a measure taken twice describes the column once.
    """
    if rows in _HANDED:
        return _HANDED[rows]
    loaded = described(codex_column(rows))
    handed: "list[tuple[object, ...]]" = []
    shipped = generation._sign_repairs

    def captured(*arguments: object) -> object:
        nonlocal handed
        handed += [arguments[:4] + (list(arguments[4]),) + arguments[5:]]  # type: ignore[operator]
        return shipped(*arguments)  # type: ignore[arg-type]

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_sign_repairs", captured)
        generation.generate(loaded, 0)
    assert len(handed) == 1, len(handed)
    _HANDED[rows] = (loaded, handed[0])
    return _HANDED[rows]


def grid_steps_asked(handed: "tuple[object, ...]") -> int:
    """How many strata of ``handed`` take G5.5's grid step: wrong-signed, not pinned, on a grid."""
    _column, _facts, layout, _rungs, values, grid = handed
    total = len(values)  # type: ignore[arg-type]
    asked = 0
    for place in range(1, total - 1):
        band = layout.bands[place]  # type: ignore[attr-defined]
        value = values[place]  # type: ignore[index]
        if grid > 0 and (  # type: ignore[operator]
            (band == generation._BAND_NEGATIVE and value >= 0.0)
            or (band == generation._BAND_POSITIVE and value <= 0.0)
        ):
            asked += 1
    return asked


def codex_repair_lines(rows: int, as_built: bool = False, counted: bool = False) -> int:
    """The lines G5.5's sign repairs run on the Codex column of ``rows`` rows (564c61a's with ``as_built``).

    With ``counted`` each value is handed as a `_Counted`, so a value a
    builtin hashes or compares there is a line too.
    """
    handed = repairs_handed(rows)[1]
    function = _sign_repairs_as_built if as_built else generation._sign_repairs
    return lines_run(function, *handed[:4], _handed(handed[4], counted), handed[5])  # type: ignore[arg-type]


# -- a column most of whose strata walk far ---------------------------------


def crowded_repairs(strata: int) -> "tuple[object, ...]":
    """What G5.5 is handed for ``strata`` one-cell strata, a quarter of them wrong-signed, on a grid of two places.

    Half the strata are negative and half positive. Three quarters of each
    band hold the grid's first points on their side, `-0.01` down and
    `0.01` up, and the quarter beside nought were drawn onto `0.0`, so each
    of them walks past every point its band holds: a walk from the first
    step costs the strata for each repair, and with a quarter of the strata
    repaired, their square.
    """
    half = strata // 2
    walked = half // 4
    values = [-(half - walked - place) / 100 for place in range(half - walked)] + [0.0] * walked
    values += [0.0] * walked + [(place + 1) / 100 for place in range(half - walked)]
    bands = ("negative",) * half + ("positive",) * half
    layout = generation._NumericLayout(
        sizes=(1,) * strata, starts=tuple(range(strata)), bands=bands, raw_budgets=(), folded_budgets=()
    )
    column = types.SimpleNamespace(name="value")
    facts = types.SimpleNamespace(kept_stand_ins=(), integer_valued=False)
    rungs = (-strata / 50, strata / 50)
    return (column, facts, layout, rungs, values, 2)


def crowded_repair_lines(strata: int, as_built: bool = False, counted: bool = False) -> int:
    """The lines G5.5's sign repairs run on `crowded_repairs` (564c61a's with ``as_built``).

    With ``counted`` each value is handed as a `_Counted`, so a value a
    builtin hashes or compares there is a line too.
    """
    handed = crowded_repairs(strata)
    function = _sign_repairs_as_built if as_built else generation._sign_repairs
    return lines_run(function, *handed[:4], _handed(handed[4], counted), handed[5])  # type: ignore[arg-type, index]


# -- answers ---------------------------------------------------------------


def test_the_codex_column_is_repaired_as_the_repairs_as_built_repaired_it() -> None:
    """At 2,000 and 4,000 rows: the same values and notes, on the strata the producer's description gives.

    PREMISE: a hundredth of the strata, less eleven, take the grid step
    (9 and 29 of them), so the walk is asked at each size.
    """
    for rows, asked in ((2000, 9), (4000, 29)):
        handed = repairs_handed(rows)[1]
        assert grid_steps_asked(handed) == asked, (rows, grid_steps_asked(handed))
        ours = generation._sign_repairs(*handed[:4], list(handed[4]), handed[5])  # type: ignore[arg-type]
        theirs = _sign_repairs_as_built(*handed[:4], list(handed[4]), handed[5])
        assert _same(ours, theirs), rows


def test_the_twins_of_the_codex_column_are_the_twins_the_repairs_as_built_wrote() -> None:
    """2,000 rows at seeds 0, 1 and 2: the twin and its report are the same bytes with 564c61a's repairs."""
    loaded = repairs_handed(2000)[0]
    written = []
    for seed in (0, 1, 2):
        twin = generation.generate(loaded, seed)
        written += [(rendering.twin_csv(twin), rendering.report(loaded, twin))]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_sign_repairs", _sign_repairs_as_built)
        for seed in (0, 1, 2):
            twin = generation.generate(loaded, seed)
            assert (rendering.twin_csv(twin), rendering.report(loaded, twin)) == written[seed], seed


def _made_up(draw: random.Random, ordered: bool) -> "tuple[object, ...]":
    """What G5.5 may be handed: strata in band order or, with ``ordered`` false, in any order.

    The values are mostly points of the grid either side of nought, among
    them a band's own first points and nought written both ways, so the
    strata hold one another's answers, and many are wrong-signed; a few are
    any number, infinity or NaN. The ladder ends short of some walks, so
    some find every point within reach held or none within reach at all.
    """
    total = draw.randrange(1, 60)
    grid = draw.choice((-1, 1, 1, 2, 2, 3))
    unit = 10 ** max(grid, 1)
    if ordered:
        negatives = draw.randrange(0, total + 1)
        zero = 1 if negatives < total and draw.random() < 0.4 else 0
        bands = tuple(
            "negative" if place < negatives else "zero" if place < negatives + zero else "positive"
            for place in range(total)
        )
    else:
        bands = tuple(draw.choice(("negative", "positive", "positive", "zero")) for _place in range(total))
    values: "list[float]" = []
    for band in bands:
        roll = draw.random()
        if band == "zero":
            values += [0.0]
        elif roll < 0.35:
            values += [draw.choice((0.0, -0.0, 0.0))]
        elif roll < 0.85:
            values += [draw.choice((-1, 1)) * draw.randrange(1, 12) / unit]
        elif roll < 0.95:
            values += [draw.uniform(-3.0, 3.0)]
        else:
            values += [draw.choice((math.inf, -math.inf, math.nan, -1.0, 1.0))]
    reach = draw.randrange(1, 15) / unit
    rungs = None if draw.random() < 0.1 else (-reach * draw.choice((1, 2)), reach * draw.choice((1, 2)))
    layout = generation._NumericLayout(
        sizes=(1,) * total, starts=tuple(range(total)), bands=bands, raw_budgets=(), folded_budgets=()
    )
    column = types.SimpleNamespace(name="value")
    facts = types.SimpleNamespace(
        kept_stand_ins=draw.choice(((), (-999.0,))), integer_valued=draw.random() < 0.2
    )
    return (column, facts, layout, rungs, values, grid)


def test_the_repairs_give_what_the_repairs_as_built_gave() -> None:
    """Over 6,000 made-up strata sets, in band order and in any order: the same values and notes.

    A real layout puts its negative strata before its positive ones, so the
    points a band holds only grow while its strata are repaired, and a
    band's walk begins again from its first step only where the last
    stratum holding nought lets it go -- both sides begin again then
    (`_let_go`), and on these grids nought is not held again; strata in
    any order let a repair on one side give back a point the other side
    walked past, and there the walk must begin again. Both are required:
    in band order no walk begun again before nought was let go, and many
    walks begun again in any order.
    """
    draw = random.Random(3871)
    asked = {True: 0, False: 0}
    begun_again = {True: 0, False: 0}
    begun_before_nought = [0]
    shipped = generation._grid_step_of_sign
    shipped_let_go = generation._let_go
    stopped: "dict[int, int]" = {}
    nought_let_go = [False]

    def spied(band, rungs, grid, held, total, kept=(), walked=None):  # type: ignore[no-untyped-def]
        if walked is not None and id(walked) in stopped and walked[0] < stopped[id(walked)]:
            begun_again[ordered] += 1
            begun_before_nought[0] += 1 if ordered and not nought_let_go[0] else 0
        answer = shipped(band, rungs, grid, held, total, kept=kept, walked=walked)
        if walked is not None:
            stopped[id(walked)] = walked[0]
        return answer

    def let_go_spied(held, value, walked):  # type: ignore[no-untyped-def]
        shipped_let_go(held, value, walked)
        if value == 0.0 and value not in held:
            nought_let_go[0] = True

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_grid_step_of_sign", spied)
        patch.setattr(generation, "_let_go", let_go_spied)
        for case in range(6000):
            ordered = case % 2 == 0
            handed = _made_up(draw, ordered)
            stopped.clear()
            nought_let_go[0] = False
            ours = generation._sign_repairs(*handed[:4], list(handed[4]), handed[5])  # type: ignore[arg-type]
            theirs = _sign_repairs_as_built(*handed[:4], list(handed[4]), handed[5])
            assert _same(ours, theirs), (case, handed[2].bands, handed[3], handed[4], handed[5])  # type: ignore[attr-defined]
            asked[ordered] += grid_steps_asked(handed)
    assert asked[True] > 3000 and asked[False] > 3000, asked
    assert begun_before_nought[0] == 0, (begun_again, begun_before_nought)
    assert begun_again[True] > 100 and begun_again[False] > 1000, begun_again


def test_a_walk_begun_where_the_last_one_stopped_answers_as_the_walk_from_the_first_step() -> None:
    """`_grid_step_of_sign` handed its last step answers as from step 1, while the points held only grow.

    Sequences of questions on one side of nought, each answer then held,
    over grids of one to three places: walks that end short of the ladder's
    end, walks that find every point within reach held, a ladder whose end
    stands before the first step, and a stand-in number in reach -- `-999.0`,
    past 9,989 held tenths -- kept or not. A walk handed nothing is held to
    564c61a's text. Each kind is required to have happened.
    """
    draw = random.Random(3872)
    kinds = {"begun later": 0, "every point held": 0, "none in reach": 0, "past -999.0": 0, "at -999.0 kept": 0}
    for case in range(400):
        negative = draw.random() < 0.5
        band = "negative" if negative else "positive"
        sign = -1 if negative else 1
        kept = draw.choice(((), (sign * 999.0, sign * 9999.0)))
        far = case % 40 == 0
        if far:
            grid, total, rungs = 1, 10000, (-2000.0, 2000.0)
            held = {sign * step / 10: 1 for step in range(1, 9990)}
        else:
            grid = draw.choice((1, 2, 3))
            total = draw.randrange(3, 120)
            held = {sign * step / 10**grid: 1 for step in range(1, draw.randrange(1, total + 1)) if draw.random() < 0.8}
            reach = draw.randrange(0, total + 3) / 10**grid
            rungs = None if draw.random() < 0.3 else ((-reach, 1.0) if negative else (-1.0, reach))
        walked = [1]
        for question in range(3 if far else draw.randrange(1, 40)):
            theirs = _grid_step_of_sign_as_built(band, rungs, grid, held, total, kept=kept)
            assert repr(generation._grid_step_of_sign(band, rungs, grid, held, total, kept=kept)) == repr(theirs)
            before = walked[0]
            ours = generation._grid_step_of_sign(band, rungs, grid, held, total, kept=kept, walked=walked)
            assert repr(ours) == repr(theirs), (case, before, ours, theirs)
            kinds["begun later"] += 1 if before > 1 else 0
            kinds["every point held"] += 1 if ours in held else 0
            kinds["none in reach"] += 1 if rungs is not None and ours == sign * 1.0 and abs(rungs[0 if negative else 1]) < 10**-grid else 0
            if far and negative and question == 0:
                kinds["past -999.0" if kept == () else "at -999.0 kept"] += 1
                assert ours == (-999.1 if kept == () else -999.0), (kept, ours)
            held[ours] = 1
    assert kinds["begun later"] > 5000 and kinds["every point held"] > 1000 and kinds["none in reach"] > 50, kinds
    assert kinds["past -999.0"] >= 1 and kinds["at -999.0 kept"] >= 1, kinds


# -- a grid finer than binary64 --------------------------------------------


def _let_go_by_sign_alone(held: "dict[float, int]", value: float, walked: "dict[str, list[int]]") -> None:
    """d36627f's `_let_go`: a side's walk began again only for a value strictly on that side of nought."""
    held[value] = held[value] - 1
    if held[value] > 0:
        return
    del held[value]
    if value < 0.0:
        walked[generation._BAND_NEGATIVE][0] = 1
    if value > 0.0:
        walked[generation._BAND_POSITIVE][0] = 1


def _strata(bands: "tuple[str, ...]", values: "list[float]", rungs: object, grid: int) -> "tuple[object, ...]":
    """What G5.5 is handed for one-cell strata of ``bands`` holding ``values``, nothing kept, not whole."""
    layout = generation._NumericLayout(
        sizes=(1,) * len(bands), starts=tuple(range(len(bands))), bands=bands, raw_budgets=(), folded_budgets=()
    )
    column = types.SimpleNamespace(name="value")
    facts = types.SimpleNamespace(kept_stand_ins=(), integer_valued=False)
    return (column, facts, layout, rungs, values, grid)


def _made_up_fine(draw: random.Random, ordered: bool) -> "tuple[object, ...]":
    """Strata on a grid of 322 to 330 places, in band order or, with ``ordered`` false, in any order.

    Binary64's least positive number is about 4.9e-324, so a step of 324
    places or more reads back as nought until it reaches half of it, and
    then as one of the few numbers that small: at 324 places the first
    two steps read back as nought and the next five as 5e-324; at 330
    every step of a walk over fewer than 2.4 million strata reads back
    as nought. The values are mostly nought, written both ways, and
    those numbers, so the strata hold the points their walks read.
    """
    total = draw.randrange(1, 40)
    grid = draw.choice((322, 323, 324, 324, 325, 330, 330))
    least = 5e-324
    if ordered:
        negatives = draw.randrange(0, total + 1)
        zero = 1 if negatives < total and draw.random() < 0.3 else 0
        bands = tuple(
            "negative" if place < negatives else "zero" if place < negatives + zero else "positive"
            for place in range(total)
        )
    else:
        bands = tuple(draw.choice(("negative", "positive", "positive", "zero")) for _place in range(total))
    values: "list[float]" = []
    for band in bands:
        roll = draw.random()
        if band == "zero":
            values += [0.0]
        elif roll < 0.5:
            values += [draw.choice((0.0, -0.0, 0.0))]
        elif roll < 0.9:
            values += [draw.choice((-1, 1)) * draw.randrange(1, 6) * least]
        else:
            values += [draw.choice((-1.0, 1.0, -0.5, 0.5))]
    rungs = draw.choice((None, (-1.0, 1.0), (-2 * least, 2 * least), (-least, least), (-0.0, 0.0)))
    return _strata(bands, values, rungs, grid)


def test_a_grid_whose_steps_read_back_as_nought_is_repaired_as_the_repairs_as_built_repaired_it() -> None:
    """At 330 places nought let go frees every step of both sides, and the walks begin again from the first.

    Two negative strata drawn onto `0.0`: the first walks past every step,
    each read back as `-0.0` while the second holds nought, and takes
    `-1.0`; the second lets nought go, its first step is free, and
    564c61a gave it `-0.0`. d36627f began that walk again only for a value
    strictly on its side, so it began past every step and gave `-1.0`: the
    twin wrote another number. The same on the positive side; and on 4,000
    made-up strata sets of 322 to 330 places the answers are 564c61a's,
    where d36627f's rule is required to answer otherwise in many of them,
    so the battery is known to see the defect.
    """
    negative = _strata(("negative",) * 3 + ("positive",) * 2, [-5.0, 0.0, 0.0, 3.0, 5.0], (-5.0, 5.0), 330)
    positive = _strata(("negative",) + ("positive",) * 4, [-5.0, 0.0, 0.0, 3.0, 5.0], (-5.0, 5.0), 330)
    for handed, answer in ((negative, ["-5.0", "-1.0", "-0.0", "3.0", "5.0"]), (positive, ["-5.0", "1.0", "0.0", "3.0", "5.0"])):
        theirs = _sign_repairs_as_built(*handed[:4], list(handed[4]), handed[5])  # type: ignore[index]
        assert [repr(value) for value in theirs[0]] == answer, theirs
        assert _same(generation._sign_repairs(*handed[:4], list(handed[4]), handed[5]), theirs), answer  # type: ignore[arg-type, index]
    draw = random.Random(3873)
    missed = 0
    asked = 0
    for case in range(4000):
        handed = _made_up_fine(draw, case % 2 == 0)
        theirs = _sign_repairs_as_built(*handed[:4], list(handed[4]), handed[5])  # type: ignore[index]
        ours = generation._sign_repairs(*handed[:4], list(handed[4]), handed[5])  # type: ignore[arg-type, index]
        assert _same(ours, theirs), (case, handed[2].bands, handed[3], handed[4], handed[5])  # type: ignore[attr-defined]
        with pytest.MonkeyPatch.context() as patch:
            patch.setattr(generation, "_let_go", _let_go_by_sign_alone)
            missed += 0 if _same(generation._sign_repairs(*handed[:4], list(handed[4]), handed[5]), theirs) else 1  # type: ignore[arg-type, index]
        asked += grid_steps_asked(handed)
    assert asked > 10000 and missed > 100, (asked, missed)


# -- growth ----------------------------------------------------------------


def test_the_sign_repairs_of_the_codex_column_grow_with_the_rows() -> None:
    """2,000 and 4,000 rows: the lines run grow under 2.5 times; 564c61a's at least three times.

    564c61a ran 2,000 rows of the column in about a tenth of a second and
    32,000 in more than eleven CPU minutes, building the list of every
    stratum's value once for each stratum it read at each of its 9 to 309
    repairs. The lines it runs see the strata read, one a line; the
    copying it did inside each line is not counted, so the measure is the
    lower bound of its cost.
    """
    small, large = codex_repair_lines(2000), codex_repair_lines(4000)
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small, old_large = codex_repair_lines(2000, True), codex_repair_lines(4000, True)
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


def test_a_column_whose_strata_walk_far_is_repaired_in_lines_that_grow_with_the_strata() -> None:
    """400 and 800 strata, a quarter wrong-signed beside every point their band holds: under 2.5 times.

    Each repair's walk passes every point its band holds, so a walk from
    the first step costs a repair the strata even where what is held is
    kept as the strata move; each band's walk begins where its last one
    stopped, and 564c61a's lines are required to grow at least three times.
    """
    for strata in (400, 800):
        handed = crowded_repairs(strata)
        assert grid_steps_asked(handed) == strata // 8 * 2, strata
        ours = generation._sign_repairs(*handed[:4], list(handed[4]), handed[5])  # type: ignore[arg-type, index]
        theirs = _sign_repairs_as_built(*handed[:4], list(handed[4]), handed[5])  # type: ignore[index]
        assert _same(ours, theirs), strata
    small, large = crowded_repair_lines(400), crowded_repair_lines(800)
    assert large / small < LINEAR_AT_MOST, (small, large)
    old_small, old_large = crowded_repair_lines(400, True), crowded_repair_lines(800, True)
    assert old_large / old_small >= SQUARE_AT_LEAST, (old_small, old_large)


# -- what a builtin does with each value ------------------------------------


def _squared_in_builtins() -> "dict[str, object]":
    """Three grid steps that answer as the shipped one and cost every repair the strata inside a builtin.

    "a list searched" asks the shipped step of a list of the values held,
    so each point a walk asks about is looked for along that list inside
    `in`; "a dict built again" asks it of their dict built again from that
    list at every repair, each value hashed inside `dict.fromkeys`; "a
    list sorted again" sorts the values held at every repair, each value
    compared by order inside `sorted`, before asking the shipped step.
    """
    shipped = generation._grid_step_of_sign

    def searched(band, rungs, grid, held, total, kept=(), walked=None):  # type: ignore[no-untyped-def]
        return shipped(band, rungs, grid, list(held), total, kept=kept, walked=walked)

    def gathered(band, rungs, grid, held, total, kept=(), walked=None):  # type: ignore[no-untyped-def]
        return shipped(band, rungs, grid, dict.fromkeys(list(held), 1), total, kept=kept, walked=walked)

    def ordered(band, rungs, grid, held, total, kept=(), walked=None):  # type: ignore[no-untyped-def]
        points = sorted(held)
        return shipped(band, rungs, grid, held if points else {}, total, kept=kept, walked=walked)

    return {"a list searched": searched, "a dict built again": gathered, "a list sorted again": ordered}


def test_the_growth_measures_see_each_value_a_builtin_hashes_or_compares() -> None:
    """Both measures on `_Counted` values: under 2.5 times; 564c61a's at least three; a builtin's square seen.

    A builtin runs as one line however many values it reads, so the two
    growth tests above can pass a repair that does the square of the
    strata inside builtins: skeptic 1 of the lane kept the values held in
    a list, and gathered them again at every repair with `dict.fromkeys`,
    and on the Codex column both grew about twice by the lines alone. On
    values that run a line each time they are hashed or compared, the
    shipped repairs are required to grow under 2.5 times on the Codex
    column (2,000 to 4,000 rows) and on the strata walking far (400 to
    800), and 564c61a's at least three times. Three repairs of that kind
    -- one searching a list of the values held, one building their dict
    again and one sorting them again at every repair -- are built here
    from the shipped grid step (`_squared_in_builtins`):
    each is required to give 564c61a's answers, and to grow under 2.5
    times by the lines alone and at least 2.5 times on these values, so
    this test fails on them where the two above do not. Handed these
    values, the shipped repairs give 564c61a's answers too.
    """
    measures = (
        ("the Codex column", codex_repair_lines, (2000, 4000), lambda rows: repairs_handed(rows)[1]),
        ("strata walking far", crowded_repair_lines, (400, 800), crowded_repairs),
    )
    for name, measure, sizes, handed_at in measures:
        theirs = {}
        for size in sizes:
            handed = handed_at(size)
            theirs[size] = _sign_repairs_as_built(*handed[:4], list(handed[4]), handed[5])  # type: ignore[index]
            ours = generation._sign_repairs(*handed[:4], _handed(handed[4], True), handed[5])  # type: ignore[arg-type, index]
            assert _same(ours, theirs[size]), (name, size)
        small, large = (measure(size, counted=True) for size in sizes)
        assert large / small < LINEAR_AT_MOST, (name, small, large)
        old_small, old_large = (measure(size, as_built=True, counted=True) for size in sizes)
        assert old_large / old_small >= SQUARE_AT_LEAST, (name, old_small, old_large)
        for kind, step in _squared_in_builtins().items():
            with pytest.MonkeyPatch.context() as patch:
                patch.setattr(generation, "_grid_step_of_sign", step)
                for size in sizes:
                    handed = handed_at(size)
                    ours = generation._sign_repairs(*handed[:4], _handed(handed[4], True), handed[5])  # type: ignore[arg-type, index]
                    assert _same(ours, theirs[size]), (name, kind, size)
                plain = [measure(size) for size in sizes]
                counted = [measure(size, counted=True) for size in sizes]
            assert plain[1] / plain[0] < LINEAR_AT_MOST <= counted[1] / counted[0], (name, kind, plain, counted)
