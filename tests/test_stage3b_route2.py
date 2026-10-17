"""THE ROUTE-2 CORRECTION (plans P4-D390 and P4-D373, 2026-10-08): times beside notes or another face are labels, and their twins meet the census of forms.

Landing 3b.5's second repair round counted out, beside a column of clock
times, the levels below the floor no clock form reads -- one-off notes,
times on another face or at another precision -- and read what was left
as clock times (route 2). Lane G4 deleted the level pass the route lived
in; the merge kept it asked of every level below the floor, because
without it 13 of lane C1's 112 such columns wrote twins that missed the
census count of the `HH:MM` form. The orchestrator's corrected ruling, under
the owner's principle of 2026-10-01 (HIPAA exposure is the only privacy
concern; code written on the twin must run, and fail, as it does on the real
file): the route wrote 37,632 cells blank that the source never left blank,
so it is dropped, and the 13 misses are repaired where they came from.

They came from method G8.3's one-pass arrangement, which a column holding
more than 256 held-back labels takes directly: it gave each size, largest
first, to the form owing the most cells and cut the debt at nought, so a
form owing one cell took a label of two rows. On the integrator's two traced
tables the `HH:MM` form was paid one cell over -- 29,143 for 29,142 and 2,719
for 2,718 -- while the labels of one row that would have finished it exactly
stood at the end of the walk. The pass now leaves a size neutral where the
form owing the most owes less, and takes the walk as it stood only where
that leaves a debt unpaid.

* `test_a_debt_its_own_labels_can_make_is_paid_exactly` -- the face table's
  326 held-back sizes pay its debt of 662 cells exactly (mutant: the pass as
  it stood, 663);
* `test_where_no_pass_settles_exactly_the_walk_still_covers_the_debt` -- 300
  labels of two rows against a debt of 301 cells are paid 302, as before, and
  never 300: the census window takes a form's count above the published one,
  up to its pool, and never below it;
* `test_the_traced_tables_are_labels_and_miss_nothing` -- times beside 3 %
  one-off notes at 30,000 rows (floor 11) and beside 10 % on the 12-hour face
  at 3,000 rows (floor 36) are labels with no cell counted missing, the real
  table and the twin miss no check, and the twin writes no blank (mutant: the
  pass as it stood, handed the sizes as they stood before the repair round
  below, and each twin misses `forms.published.%%:%%`).

ITS REPAIR ROUND (skeptic 1 of the correction, 2026-10-09). Where the route
had written blanks, the label twins wrote clock times no clock reads where the
table holds none -- `44:89`, `9:75` -- so code keeping a real column's cells
shaped like a time and parsing them stopped on the twin: 63 cells in 4 of the
112 columns and 200,134 in 47 of the skeptic's own tables, where the route had
written 402 and 324,134 blanks. The held-back labels' walk of a clock's form
ran on past the times it can write into its other spellings; a clock's form
took up to a label per cell, more labels than it has times; the form owing the
most took the largest labels first and left a form short of times the small
ones; and past G8.3's clock line a stand-in owed no named form, wearing the
published labels' shape, was filled figure by figure, or spent the room the
owed stand-ins after it needed.

* `test_label_twins_write_no_time_no_clock_reads` -- times written `HH:MM`
  beside 3 % one-off notes at 100,000 rows (floor 36) and `H:MM` beside 10 %
  at 10,000 rows (floor 11) are labels, the real table and the twin miss no
  check, and the twin writes no blank and no cell shaped like a time that no
  clock reads (mutant: the walk run past a clock's times, 4,822 and 169 such
  cells, as on 07e9e0b);
* `test_red_when_a_clocks_labels_are_unbounded` -- the `HH:MM` form of the
  first, handed up to a label per cell, writes 1,091 of its cells `group-N`
  and misses its count;
* `test_a_form_short_of_times_is_paid_first` -- `HH:MM` beside 15 %
  `HH:MM:SS` at 30,000 rows (floor 11) meets both forms' counts and misses
  nothing (mutant: the form owing the most paid first, `HH:MM` 37 short);
* `test_the_owed_stand_ins_keep_their_room` -- `H:MM` beside 3 % notes at
  30,000 rows (floor 11) writes no such cell and misses nothing (mutant: the
  published labels' shape spends the room first, 610 such cells).

ITS LEFTOVER (skeptic 2 of the correction, 2026-10-09). A duration written
in a clock's form -- minutes and seconds over the hour, an emergency stay past
a day -- holds that form's spellings no clock reads, `26:07` and `45:12`, and
they are the column's own values. The repair round stopped every clock's form
at its times, so where such a column's held-back labels outnumbered the times
its form could still write the rest were written `group-N`: on 18 of the
skeptic's 50 duration tables the twin missed the count of `%%:%%`, which it
met before the round, and code reading every cell as a duration -- split on
the colon, each field a whole number -- stopped on the twin where it runs on
the real table. A clock's form handed more labels than it has times is now
past its times: its supply is counted over its whole room, its largest places
take its times and the others a duration's spellings, hours 24 to 59 first.

* `test_duration_twins_miss_nothing` -- minutes and seconds of 2 to 40
  minutes at 10,000 rows (floor 11) and a stay of up to 72 hours at 30,000
  rows (floor 36) are labels, the real table and the twin miss no check;
* `test_duration_twins_write_no_neutral_spelling` -- and the twin writes no
  blank and no `group-N` (mutant: every clock's form stopped at its times,
  755 and 705 such cells and the count missed, as on 224c320);
* `test_duration_code_runs_on_the_twin_as_on_the_table` -- every cell of the
  table and of its twin is read as a duration and written back as it stands,
  every field after the first below 60 (mutant: past its times the form
  filled figure by figure, 349 and 324 fields of 60 or more, `29:93`).
"""

from __future__ import annotations

import csv
import functools
import io
import pathlib
import random
import re
import sys
import tempfile
import typing

import pytest

import fixtures

from synthtwin import contract
from synthtwin import generation
from synthtwin import parsing
from synthtwin import profile
from synthtwin import reading
from synthtwin import rendering
from synthtwin import taxonomy
from synthtwin import validation

# The one folder this module's tables and twins are written under, pytest's
# own, set for the module.
_HOME: "list[pathlib.Path]" = []


@pytest.fixture(scope="module", autouse=True)
def _home(tmp_path_factory: pytest.TempPathFactory) -> "typing.Iterator[None]":
    _HOME[:] = [tmp_path_factory.mktemp("route2")]
    yield
    _described.cache_clear()


# THE TWO TABLES THE MERGE'S INTEGRATOR TRACED, cell for cell: lane C1's
# second skeptic's appointment times (80 % on the quarter hour from 07:00 to
# 16:45, 12 % any minute from 06:30 to 18:59, 8 % on the half hour from 17:00
# to 19:30), beside one-off notes (`capsweep`) or beside a minority written on
# the 12-hour face (`face`).
_TRACED = {
    "notes": ("capsweep", 0.03, 30000, 11),
    "face": ("face", 0.1, 3000, 36),
}

# What each table publishes for the `HH:MM` form, which its twin paid one cell
# over before this correction.
_PUBLISHED = {"notes": 29142, "face": 2718}

# Each table's whole census of forms. Since lane L2 (plan P4-D392) the
# minority written `9:15 AM` has the form `%:%% @@` (or `%%:%% @@`), which
# the census names beside `%%:%%`; before, those cells had no form.
_CENSUS = {
    "notes": {"%%:%%": 29142},
    "face": {"%%:%%": 2718, "%%:%% @@": 78, "%:%% @@": 204},
}

# THE REPAIR ROUND'S FOUR TABLES, cell for cell its skeptic's own (the `mine`
# and `mine2` batteries, at their seeds): the same appointment times, written
# `HH:MM` or, as Excel's `h:mm` writes an hour below ten, `H:MM`, beside
# one-off notes (`notes`, `hours`) or beside a minority written to the second
# (`seconds`), as kind, share, rows, floor and seed.
_CLOCKS = {
    "notes_100000": ("notes", 0.03, 100000, 36, 7031),
    "hours_10000": ("hours", 0.10, 10000, 11, 9034),
    "seconds_30000": ("seconds", 0.15, 30000, 11, 7412),
    "hours_30000": ("hours", 0.03, 30000, 11, 9016),
}

# THE LEFTOVER'S TWO DURATION TABLES, cell for cell its skeptic's own (the
# duration battery, at its seeds): a timed task in minutes and seconds, `MM:SS`,
# from 2 to 40 minutes (`task`), and an emergency department's length of
# stay, `HH:MM`, about five hours at the median with a tail of boarders to 72
# hours (`stay`), as kind, rows, floor and seed.
_DURATIONS = {
    "task_10000": ("task", 10000, 11, 31014),
    "stay_30000": ("stay", 30000, 36, 31007),
}

# A cell shaped like a clock time: an hour of one or two figures, a colon and
# two figures, and optionally a colon and two more.
_TIME_SHAPED = re.compile(r"\d{1,2}:\d\d(?::\d\d)?")

# The neutral spelling of a made-up label.
_NEUTRAL = re.compile(r"group-\d+")


def _slot(draw: random.Random) -> int:
    pick = draw.random()
    if pick < 0.80:
        hour = draw.choices(range(7, 17), weights=(3, 9, 10, 10, 8, 4, 8, 9, 8, 5))[0]
        return hour * 60 + 15 * draw.randrange(4)
    if pick < 0.92:
        return 390 + draw.randrange(750)
    return 17 * 60 + 30 * draw.randrange(6)


def _hh_mm(minutes: int) -> str:
    return f"{minutes // 60:02d}:{minutes % 60:02d}"


def _twelve_hour(minutes: int) -> str:
    hour = minutes // 60
    return f"{hour % 12 or 12}:{minutes % 60:02d} {'AM' if hour < 12 else 'PM'}"


def _h_mm(minutes: int) -> str:
    return f"{minutes // 60}:{minutes % 60:02d}"


def _clock_cells(name: str) -> "list[str]":
    """One of the repair round's tables, as its skeptic's batteries drew it."""
    kind, share, rows, _floor, seed = _CLOCKS[name]
    draw = random.Random(seed)
    cells: "list[str]" = []
    notes = 0
    for _row in range(rows):
        minutes = _slot(draw)
        if draw.random() >= share:
            cells += [_h_mm(minutes) if kind == "hours" else _hh_mm(minutes)]
            continue
        if kind == "seconds":
            cells += [f"{_hh_mm(minutes)}:{draw.randrange(60):02d}"]
            continue
        notes = notes + 1
        cells += [f"see note {notes}"]
    return cells


def _duration_cells(name: str) -> "list[str]":
    """One of the leftover's duration tables, as its skeptic's battery drew it."""
    kind, rows, _floor, seed = _DURATIONS[name]
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(rows):
        if kind == "task":
            seconds = int(draw.triangular(120, 2400, 600))
            cells += [f"{seconds // 60:02d}:{seconds % 60:02d}"]
            continue
        stay = draw.lognormvariate(0.0, 0.8) * 5.0 * 60
        while stay >= 72 * 60:
            stay = draw.lognormvariate(0.0, 0.8) * 5.0 * 60
        minutes = int(stay)
        cells += [f"{minutes // 60:02d}:{minutes % 60:02d}"]
    return cells


def _cells(name: str) -> "list[str]":
    if name in _CLOCKS:
        return _clock_cells(name)
    if name in _DURATIONS:
        return _duration_cells(name)
    kind, share, rows, floor = _TRACED[name]
    cells: "list[str]" = []
    if kind == "capsweep":
        draw = random.Random(int(share * 10000) + rows + floor)
        notes = 0
        for _row in range(rows):
            minutes = _slot(draw)
            if draw.random() < share:
                notes = notes + 1
                cells += [f"see note {notes}"]
            else:
                cells += [_hh_mm(minutes)]
        return cells
    draw = random.Random(int(share * 1000) + rows + floor)
    for _row in range(rows):
        minutes = _slot(draw)
        if draw.random() < share:
            cells += [_twelve_hour(minutes)]
        else:
            cells += [_hh_mm(minutes)]
    return cells


@functools.lru_cache(maxsize=None)
def _described(name: str):
    """The table's description, loaded, and where the table lies."""
    if name in _DURATIONS:
        floor = _DURATIONS[name][2]
    else:
        floor = _CLOCKS[name][3] if name in _CLOCKS else _TRACED[name][3]
    folder = pathlib.Path(tempfile.mkdtemp(dir=_HOME[0]))
    table = fixtures.write(folder, "times.csv", "c\n" + "\n".join(_cells(name)) + "\n")
    document = profile.build_document(
        reading.read_table(str(table), small_cell_floor=floor),
        taxonomy.Settings(small_cell_floor=floor),
        [],
    )
    written = fixtures.write_profile(folder, "times.json", document)
    return folder, document, contract.load_profile(str(written)), table


def _missed(loaded: contract.Profile, path: pathlib.Path) -> "list[str]":
    outcome = validation.measure(loaded, str(path))
    return sorted(check.subcheck for check in outcome.checks if check.verdict == validation.MISSED)


def _twin(name: str) -> "tuple[list[str], list[str]]":
    """The seed-0 twin's cells, and what validation MISSED on it."""
    folder, _document, loaded, _table = _described(name)
    text = rendering.twin_csv(generation.generate(loaded, 0))
    target = fixtures.write(folder, "twin.csv", text)
    body = list(csv.reader(io.StringIO(text)))
    return [row[0] if row else "" for row in body[1:]], _missed(loaded, target)


def _twin_cells(name: str) -> "list[str]":
    """The seed-0 twin's cells alone, for a mutant whose witness needs no validation."""
    _folder, _document, loaded, _table = _described(name)
    body = list(csv.reader(io.StringIO(rendering.twin_csv(generation.generate(loaded, 0)))))
    return [row[0] if row else "" for row in body[1:]]


def _unread(cells: "list[str]") -> "list[str]":
    """The cells shaped like a clock time that no clock reads, such as `44:89` or `9:75`."""
    return [cell for cell in cells if _TIME_SHAPED.fullmatch(cell) and parsing.clock_parts(cell) is None]


def _forms(cells: "list[str]") -> "dict[str, int]":
    """How many cells wear each written form, a cell of none left out."""
    counted: "dict[str, int]" = {}
    for cell in cells:
        form = parsing.shape_form(cell)
        if form:
            counted[form] = counted.get(form, 0) + 1
    return counted


def _paid(sizes: "tuple[int, ...]", taken: "list[str]") -> "dict[str, int]":
    paid: "dict[str, int]" = {}
    for place in range(len(sizes)):
        if taken[place]:
            paid[taken[place]] = paid.get(taken[place], 0) + sizes[place]
    return paid


# THE FACE TABLE'S HELD-BACK SIZES, as `held_back_sizes` gives them for its
# pool of 326 labels over 944 rows at a floor of 36: 317 labels rising from one
# row pay the `HH:MM` form's 662 cells, and nine -- eight of 35 rows and one of
# two -- the 282 cells on the 12-hour face, which wear no form.
_FACE_SIZES = tuple(sorted([1] * 119 + [2] * 94 + [3] * 63 + [4] * 42 + [35] * 8))


def test_a_debt_its_own_labels_can_make_is_paid_exactly() -> None:
    assert len(_FACE_SIZES) > generation._SHARE_OUT_PLACES
    taken = generation._shared_out(_FACE_SIZES, {"%%:%%": 662}, {}, {}, ())
    assert _paid(_FACE_SIZES, taken) == {"%%:%%": 662}


def test_red_when_a_debt_is_paid_past_what_it_owes(monkeypatch: pytest.MonkeyPatch) -> None:
    _as_it_stood(monkeypatch)
    taken = generation._shared_out(_FACE_SIZES, {"%%:%%": 662}, {}, {}, ())
    assert _paid(_FACE_SIZES, taken) == {"%%:%%": 663}


def test_where_no_pass_settles_exactly_the_walk_still_covers_the_debt() -> None:
    sizes = tuple([2] * 300)
    taken = generation._shared_out(sizes, {"@-%": 301}, {}, {}, ())
    assert _paid(sizes, taken) == {"@-%": 302}


def _as_it_stood(monkeypatch: pytest.MonkeyPatch) -> None:
    """The one-pass arrangement as it stood: every size to the neediest form, however little it owes.

    And the sizes it was handed as they stood. Since the repair round a
    form short of spellings is paid first (`generation._tight_first`), and
    a clock's form takes no more labels than it has times left to write
    (`generation._word_form_bounds`); the traced table beside notes has
    such a form, and its sizes so bounded are settled exactly by either
    pass, so both are withdrawn too. The face table's form is short of
    neither, and its sizes are the ones it had.
    """
    _unbounded(monkeypatch)
    one_pass = generation._one_pass

    def overpaying(
        sizes: "tuple[int, ...]",
        places: "list[int]",
        owing: "dict[str, int]",
        every: "list[str]",
        spare: "dict[str, int]",
        whole: bool,
    ) -> "tuple[list[str], bool]":
        return one_pass(sizes, places, owing, every, spare, False)

    monkeypatch.setattr(generation, "_one_pass", overpaying)
    _short_form_waits(monkeypatch)


def _short_form_waits(monkeypatch: pytest.MonkeyPatch) -> None:
    """A form short of spellings paid in its turn like any other: the pass that serves it first never settles."""

    def never_settles(
        sizes: "tuple[int, ...]",
        places: "list[int]",
        owing: "dict[str, int]",
        every: "list[str]",
        spare: "dict[str, int]",
        tight: "list[str]",
    ) -> "tuple[list[str], bool]":
        return ["" for _each in sizes], False

    monkeypatch.setattr(generation, "_tight_first", never_settles)


def _unbounded(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every word form's labels bounded by its debt alone, a label per cell, as before the repair round."""

    def debts_alone(
        owing: "dict[str, int]",
        decimal_comma: bool,
        used: "dict[str, int]",
        owners: "dict[str, str]",
        holes: "tuple[str, ...]",
    ) -> "tuple[int, ...]":
        return tuple(
            owing[form] for form in sorted(owing)
            if owing[form] > 0 and generation._form_reading(form, decimal_comma) == parsing.NOT_A_NUMBER
        )

    monkeypatch.setattr(generation, "_word_form_bounds", debts_alone)


@pytest.mark.parametrize("name", sorted(_TRACED))
def test_the_traced_tables_are_labels_and_miss_nothing(name: str) -> None:
    _folder, document, loaded, table = _described(name)
    block = document["columns"][0]  # type: ignore[index]
    assert block["role"] in (taxonomy.ROLE_CATEGORICAL, taxonomy.ROLE_LONG_TAIL), block["role"]
    assert int(block["n_missing"] or 0) == 0
    assert block["shape_forms"] == _CENSUS[name], block["shape_forms"]
    assert _missed(loaded, table) == []
    cells, missed = _twin(name)
    assert missed == [], (name, missed)
    assert sum(1 for cell in cells if cell == "") == 0
    assert sum(1 for cell in cells if parsing.shape_form(cell) == "%%:%%") == _PUBLISHED[name]


@pytest.mark.parametrize("name", sorted(_TRACED))
def test_red_when_the_traced_twins_are_paid_past_their_debt(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the one-pass arrangement as it stood overpays `%%:%%` by a cell.

    On `face` the minority is written with a no-break space U+00A0 before
    its marker, which holds no form: since lane L2 (plan P4-D392) `9:15 AM`
    with a plain space has a form of its own, the census names it, and
    this mutant leaves that table nothing to overpay (measured: nothing
    missed); with U+00A0 the minority is formless, as it was when this
    clause was measured.
    """
    if name == "face":
        plain = _twelve_hour
        monkeypatch.setattr(
            sys.modules[__name__], "_twelve_hour", lambda minutes: plain(minutes).replace(" ", "\u00a0")
        )
        _described.cache_clear()
    _as_it_stood(monkeypatch)
    try:
        _cells_now, missed = _twin(name)
        assert "forms.published.%%:%%" in missed, (name, missed)
    finally:
        _described.cache_clear()


# -- the repair round: no time no clock reads -------------------------------


def _labels_described(name: str) -> "tuple[dict[str, typing.Any], contract.Profile, pathlib.Path]":
    """A repair-round table's column block, read as labels with no cell counted missing."""
    _folder, document, loaded, table = _described(name)
    block = document["columns"][0]  # type: ignore[index]
    assert block["role"] in (taxonomy.ROLE_CATEGORICAL, taxonomy.ROLE_LONG_TAIL), block["role"]
    assert int(block["n_missing"] or 0) == 0
    return block, loaded, table


@pytest.mark.parametrize("name", ("notes_100000", "hours_10000"))
def test_label_twins_write_no_time_no_clock_reads(name: str) -> None:
    """The skeptic's two tables: labels, nothing missed, and every cell shaped like a time a time.

    On 07e9e0b the twin of the first wrote 4,822 cells such as `44:89`,
    and of the second 169 such as `9:75`, where the table holds none;
    keeping the cells shaped like a time and parsing them, code that
    runs on the real column stopped on either twin.
    """
    _block, loaded, table = _labels_described(name)
    assert _unread(_cells(name)) == []
    assert _missed(loaded, table) == []
    cells, missed = _twin(name)
    assert missed == [], (name, missed)
    assert "" not in cells
    assert _unread(cells) == [], (name, _unread(cells)[:5])


@pytest.mark.parametrize(("name", "unread"), (("notes_100000", 4822), ("hours_10000", 169)))
def test_red_when_the_walk_runs_past_a_clocks_times(
    name: str, unread: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: a clock's form walked past its times as at 07e9e0b, where only a fraction's form stopped there."""
    monkeypatch.setattr(generation, "_clock_supply", generation._fraction_clock_supply)
    assert len(_unread(_twin_cells(name))) == unread


def test_red_when_a_clocks_labels_are_unbounded(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the `HH:MM` form handed up to a label per cell, past the 1,394 times it can still write.

    Each of its labels past them is the neutral spelling, so 1,091 of the
    cells it owes are written `group-N` and the twin misses its count.
    """
    block, _loaded, _table = _labels_described("notes_100000")
    _unbounded(monkeypatch)
    cells = _twin_cells("notes_100000")
    assert _unread(cells) == []
    assert _forms(cells)["%%:%%"] == block["shape_forms"]["%%:%%"] - 1091


def test_a_form_short_of_times_is_paid_first() -> None:
    """`HH:MM` beside 15 % `HH:MM:SS`: both forms' counts met exactly, nothing missed, every time a time."""
    block, _loaded, _table = _labels_described("seconds_30000")
    assert block["shape_forms"] == {"%%:%%": 25472, "%%:%%:%%": 4528}, block["shape_forms"]
    cells, missed = _twin("seconds_30000")
    assert missed == []
    assert _unread(cells) == []
    assert _forms(cells) == block["shape_forms"]


def test_red_when_the_form_short_of_times_waits(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: the form owing the most paid first, and `HH:MM` runs out of times on the small labels, 37 short."""
    block, _loaded, _table = _labels_described("seconds_30000")
    _short_form_waits(monkeypatch)
    cells = _twin_cells("seconds_30000")
    assert _forms(cells)["%%:%%"] == block["shape_forms"]["%%:%%"] - 37


def test_the_owed_stand_ins_keep_their_room() -> None:
    """`H:MM` beside 3 % notes: past G8.3's clock line no cell shaped like a time that no clock reads, nothing missed.

    The census names `%%:%%` alone, the stand-ins it owes nothing wear the
    published labels' shape `%:%%`, and both are held by one clock line.
    """
    block, _loaded, _table = _labels_described("hours_30000")
    assert sorted(block["shape_forms"]) == ["%%:%%"], block["shape_forms"]
    cells, missed = _twin("hours_30000")
    assert missed == []
    assert "" not in cells
    assert _unread(cells) == []


def test_red_when_the_shape_spends_the_owed_room(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTATION: no room kept for the owed stand-ins, and 610 of their cells are filled figure by figure."""
    _labels_described("hours_30000")
    monkeypatch.setattr(generation, "_owed_clock_cells", lambda keys_of, held, shared, sizes: 0)
    assert len(_unread(_twin_cells("hours_30000"))) == 610


# -- the leftover: durations written in a clock's form -------------------------


def _durations(cells: "list[str]") -> "list[list[int]]":
    """Every cell read as a duration, as code written on the real column reads it.

    Split on the colon, each field a whole number, two fields at least;
    a cell this code cannot read raises ValueError, as the code would.
    """
    read: "list[list[int]]" = []
    for cell in cells:
        fields = [int(part) for part in cell.split(":")]
        if len(fields) < 2:
            raise ValueError(cell)
        read += [fields]
    return read


def _written_back(fields: "list[int]") -> str:
    """A duration's fields written as the table writes them, two figures each."""
    return ":".join([f"{field:02d}" for field in fields])


@functools.lru_cache(maxsize=None)
def _duration_twin(name: str) -> "tuple[tuple[str, ...], tuple[str, ...]]":
    """The seed-0 twin of a duration table and what validation MISSED, generated once."""
    cells, missed = _twin(name)
    return tuple(cells), tuple(missed)


def _past_fifty_nine(cells: "list[str]") -> int:
    """How many fields after a cell's first are 60 or more, over every cell read as a duration."""
    return sum(
        1 for fields in _durations(cells) for field in fields[1:] if field >= 60
    )


@pytest.mark.parametrize("name", sorted(_DURATIONS))
def test_duration_twins_miss_nothing(name: str) -> None:
    """The leftover's two duration tables: labels in one clock's form, nothing missed on the table or its twin."""
    block, loaded, table = _labels_described(name)
    assert sorted(block["shape_forms"]) == ["%%:%%"], block["shape_forms"]
    assert _missed(loaded, table) == []
    _cells_now, missed = _duration_twin(name)
    assert list(missed) == [], (name, missed)


@pytest.mark.parametrize("name", sorted(_DURATIONS))
def test_duration_twins_write_no_neutral_spelling(name: str) -> None:
    """No blank and no `group-N` in the twin: every held-back label is written in the column's form."""
    _labels_described(name)
    cells, _missed_now = _duration_twin(name)
    assert "" not in cells
    neutral = [cell for cell in cells if _NEUTRAL.fullmatch(cell)]
    assert neutral == [], (name, len(neutral), neutral[:3])


@pytest.mark.parametrize("name", sorted(_DURATIONS))
def test_duration_code_runs_on_the_twin_as_on_the_table(name: str) -> None:
    """Code reading the real column's cells as durations reads every cell of the twin, and writes each back as it stands.

    On 224c320 it stopped on the twin at the first `group-N`.
    """
    _labels_described(name)
    real = _cells(name)
    assert [_written_back(fields) for fields in _durations(real)] == real
    assert _past_fifty_nine(real) == 0
    cells = list(_duration_twin(name)[0])
    assert [_written_back(fields) for fields in _durations(cells)] == cells
    assert _past_fifty_nine(cells) == 0


@pytest.mark.parametrize(("name", "neutral"), (("stay_30000", 705), ("task_10000", 755)))
def test_red_when_every_clocks_form_stops_at_its_times(
    name: str, neutral: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: no clock's form is past its times, as at 224c320, and the labels past them are `group-N`.

    The twin misses the count of `%%:%%` and code reading durations stops on it.
    """
    _labels_described(name)
    monkeypatch.setattr(
        generation,
        "_clock_forms_past_their_times",
        lambda owing, decimal_comma, counts, most: {},
    )
    cells, missed = _twin(name)
    assert "forms.published.%%:%%" in missed, (name, missed)
    assert len([cell for cell in cells if _NEUTRAL.fullmatch(cell)]) == neutral
    with pytest.raises(ValueError):
        _durations(cells)


@pytest.mark.parametrize(("name", "fields"), (("stay_30000", 324), ("task_10000", 349)))
def test_red_when_past_its_times_the_form_is_filled_figure_by_figure(
    name: str, fields: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    """MUTATION: past its times a clock's form filled figure by figure from the first, and minutes of 60 or more are written."""
    _labels_described(name)
    monkeypatch.setattr(
        generation,
        "_past_the_clock",
        lambda form, step: generation._filled_form(form, step, False),
    )
    assert _past_fifty_nine(_twin_cells(name)) == fields
