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
  pass as it stood, and each twin misses `forms.published.%%:%%`).
"""

from __future__ import annotations

import csv
import functools
import io
import pathlib
import random
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


def _cells(name: str) -> "list[str]":
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
    """The traced table's description, loaded, and where the table lies."""
    floor = _TRACED[name][3]
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
    """The one-pass arrangement as it stood: every size to the neediest form, however little it owes."""
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


@pytest.mark.parametrize("name", sorted(_TRACED))
def test_the_traced_tables_are_labels_and_miss_nothing(name: str) -> None:
    _folder, document, loaded, table = _described(name)
    block = document["columns"][0]  # type: ignore[index]
    assert block["role"] in (taxonomy.ROLE_CATEGORICAL, taxonomy.ROLE_LONG_TAIL), block["role"]
    assert int(block["n_missing"] or 0) == 0
    assert block["shape_forms"] == {"%%:%%": _PUBLISHED[name]}, block["shape_forms"]
    assert _missed(loaded, table) == []
    cells, missed = _twin(name)
    assert missed == [], (name, missed)
    assert sum(1 for cell in cells if cell == "") == 0
    assert sum(1 for cell in cells if parsing.shape_form(cell) == "%%:%%") == _PUBLISHED[name]


@pytest.mark.parametrize("name", sorted(_TRACED))
def test_red_when_the_traced_twins_are_paid_past_their_debt(name: str, monkeypatch: pytest.MonkeyPatch) -> None:
    _as_it_stood(monkeypatch)
    _cells_now, missed = _twin(name)
    assert "forms.published.%%:%%" in missed, (name, missed)
