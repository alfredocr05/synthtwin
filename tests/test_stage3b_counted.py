"""THE GATE OF LANDING R4 (plan P4-D384): numbers that are dates.

A column whose dates an export wrote as counts -- Excel serials, SAS and
Stata days and seconds, Unix seconds and milliseconds, Epic day numbers --
is asked about (question Q3), and once declared (`--date-count`, or an
answer) is read exactly as the dates its counts name, described as dates
with its `count_form`, and twinned as the same counts. Each clause below
turns red on the mutant it names.

* C1 -- the twenty-sixth vectors file's readings and spellings are the
  product's, and each mutant -- float arithmetic, the 1970 epoch read for
  1960, halves rounded up, figures not trimmed, Excel's leap day ignored,
  exact rounding where an exporter writes the binary64 -- turns a case red;
* C2 -- Q3 asks thirteen of the battery's fourteen shapes with the member
  that wrote them among its answers, clean and under every stray-value
  scenario but one, and raises no question the fixed-width question did
  not raise already on the chance battery (mutant: a band from 1970);
* C3 -- an answered questions file and the typed option give one
  description, byte for byte, with its `count_form` (mutant: the answer
  dropped);
* C4 -- every twin cell keeps the column's spelling and names a date, the
  weekday census and the contact census are met (mutant: the twin written
  with the 1970 epoch);
* C5 -- `validate` holds the faithful twin and the source, and MISSES a
  twin written as ISO dates, in another member or with other figures
  (mutant: a check of the form that asks nothing);
* C6 -- a column NF51 told about now carries question Q3's own words and
  no NF51;
* C7 -- a workbook's column of serials stored as numbers round-trips as
  number cells.

Every table is built here, seeded and made up (plan D13).
"""

from __future__ import annotations

import contextlib
import csv
import dataclasses
import datetime
import io
import json
import pathlib
import random

import pytest

import counted_dates as battery
from synthtwin import (
    asking,
    contract,
    date_counts,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
VECTORS = REPOSITORY / "tests" / "reference" / "generation-branch-vectors-26.json"
_FILE = json.loads(VECTORS.read_text(encoding="utf-8"))
_UNITS = {
    "day": date_counts.DAY,
    "minute": date_counts.MINUTE,
    "second": date_counts.SECOND,
    "millisecond": date_counts.MILLISECOND,
    "microsecond": date_counts.MICROSECOND,
    "nanosecond": date_counts.NANOSECOND,
}
_TAIL_SECONDS = {"day": 86400, "minute": 60, "second": 1}


def _exit_of(argv: "list[str]") -> "tuple[int, str]":
    from synthtwin import cli

    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv)
    return code, said.getvalue()


def _table(folder: pathlib.Path, cells: "list[str]", name: str = "seen") -> pathlib.Path:
    """One column in a CSV file, each cell quoted where it holds a comma."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "table.csv"
    written = [f'"{cell}"' if "," in cell else cell for cell in cells]
    path.write_text(name + "\n" + "\n".join(written) + "\n", encoding="utf-8", newline="")
    return path


def _block_of(tmp: pathlib.Path, cells: "list[str]", counted: str = "") -> "dict[str, object]":
    """One column `seen` described in process, with the declaration where given."""
    path = _table(tmp, cells)
    table = reading.read_table(str(path))
    declared = (("seen", counted),) if counted else ()
    document = profile.build_document(
        table, taxonomy.Settings(forced_date_counts=declared), []
    )
    return document["columns"][0]


def _q3(block: "dict[str, object]") -> "asking.DateCountsSaid | None":
    return asking._date_counts_said(block)


# -- C1: the twenty-sixth file ------------------------------------------


def _read(case: "dict[str, object]") -> "str | None":
    written = date_counts.written_count(f"{case['text']}", f"{case['mark']}")
    if written is None:
        return None
    numerator, denominator = date_counts.exact_value(written)
    unit = _UNITS[f"{case['unit']}"]
    moment = date_counts.moment_of(f"{case['member']}", numerator, denominator, unit)
    return None if moment is None else date_counts.iso_text(moment, unit, unit)


def _spelled(case: "dict[str, object]") -> "str | None":
    iso = f"{case['iso']}"
    unit = {10: date_counts.DAY, 16: date_counts.MINUTE, 19: date_counts.SECOND,
            23: date_counts.MILLISECOND, 26: date_counts.MICROSECOND,
            29: date_counts.NANOSECOND}[len(iso)]
    form = case["form"]
    assert isinstance(form, dict)
    shaped = date_counts.CountForm(
        form["places"], form["trimmed"], form["significant"], form["exponent"],
        form["mark"], form["contacts"],
    )
    moment = date_counts.moment_of_iso(iso, unit)
    assert moment is not None
    return date_counts.written_for(f"{case['member']}", moment, unit, shaped, f"{case['contact']}")


def _wrong() -> "list[str]":
    """Every case of the file the product answers otherwise."""
    wrong: "list[str]" = []
    for name, case in sorted(_FILE["readings"].items()):
        if _read(case) != case["answer"]:
            wrong += [f"reading {name}"]
    for name, case in sorted(_FILE["spellings"].items()):
        if _spelled(case) != case["answer"]:
            wrong += [f"spelling {name}"]
    for name, case in sorted(_FILE["dealings"].items()):
        if generation._contacts_dealt(case["census"], case["dated"]) != case["answer"]:
            wrong += [f"dealing {name}"]
    for member, words in sorted(_FILE["holes"].items()):
        if list(date_counts.hole_words(member)) != words:
            wrong += [f"holes {member}"]
    for member, words in sorted(_FILE["moment_holes"].items()):
        if list(date_counts.hole_words(member, True)) != words:
            wrong += [f"moment holes {member}"]
    for name, case in sorted(_FILE["reaches"].items()):
        tail = f"{case['tail']}"
        at = taxonomy.tail_ordinal(f"{case['boundary']}", tail, taxonomy.READ_AT_LOCAL)
        reach = date_counts.tail_reach(
            f"{case['member']}", _UNITS[f"{case['written']}"], _TAIL_SECONDS[tail], at,
            bool(case["low_side"]), int(case["edge"]),
        )
        if reach != case["answer"]:
            wrong += [f"reach {name}"]
    for name, case in sorted(_FILE["islands"].items()):
        tail = f"{case['tail']}"
        at = taxonomy.tail_ordinal(f"{case['boundary']}", tail, taxonomy.READ_AT_LOCAL)
        written = _UNITS[f"{case['written']}"]
        reach = date_counts.tail_reach(
            f"{case['member']}", written, _TAIL_SECONDS[tail], at, bool(case["low_side"]), int(case["edge"])
        )
        found = date_counts.tail_islands(
            f"{case['member']}", written, _TAIL_SECONDS[tail], at, bool(case["low_side"]), reach
        )
        if {"reach": reach, "islands": [list(pair) for pair in found]} != case["answer"]:
            wrong += [f"islands {name}"]
    for name, case in sorted(_FILE["steps"].items()):
        pairs = tuple((pair[0], pair[1]) for pair in case["islands"])
        if date_counts.off_the_islands(case["distance"], pairs, case["reach"]) != case["answer"]:
            wrong += [f"step {name}"]
    for name, case in sorted(_FILE["strata"].items()):
        pairs = tuple((pair[0], pair[1]) for pair in case["islands"])
        near, far = date_counts.stratum_off_the_islands(case["near"], case["far"], pairs, case["reach"])
        if {"near": near, "far": far} != case["answer"]:
            wrong += [f"strata {name}"]
    for name, case in sorted(_FILE["keepings"].items()):
        kept = generation._kept_off_placeholder_days(
            case["ordinals"], case["lows"], case["highs"], case["day"], frozenset(case["holes"]), case["grid"]
        )
        if kept != case["answer"]:
            wrong += [f"keeping {name}"]
    return wrong


def test_c1_every_case_of_the_twenty_sixth_file_is_the_products() -> None:
    assert len(_FILE["readings"]) >= 14 and len(_FILE["spellings"]) >= 17
    assert len(_FILE["dealings"]) >= 4
    assert sorted(_FILE["holes"]) == sorted(date_counts.MEMBERS) and len(_FILE["keepings"]) >= 7
    assert sorted(_FILE["moment_holes"]) == sorted(date_counts.MEMBERS) and len(_FILE["reaches"]) >= 9
    assert len(_FILE["islands"]) >= 7 and len(_FILE["steps"]) >= 4 and len(_FILE["strata"]) >= 4
    assert len([case for case in _FILE["keepings"].values() if case["grid"]]) >= 5
    assert _wrong() == []


def _float_arithmetic(monkeypatch: pytest.MonkeyPatch) -> None:
    original = date_counts.exact_value

    def through_a_float(written: "date_counts.Written") -> "tuple[int, int]":
        numerator, denominator = original(written)
        return float(numerator / denominator).as_integer_ratio()

    monkeypatch.setattr(date_counts, "exact_value", through_a_float)


def _epoch_1970_for_1960(monkeypatch: pytest.MonkeyPatch) -> None:
    table = dict(date_counts.TABLE)
    for word in ("days-since-1960", "seconds-since-1960", "milliseconds-since-1960"):
        table[word] = dataclasses.replace(table[word], epoch=parsing.days_from_civil(1970, 1, 1))
    monkeypatch.setattr(date_counts, "TABLE", table)


def _halves_up(monkeypatch: pytest.MonkeyPatch) -> None:
    def up(numerator: int, denominator: int) -> int:
        quotient, rest = divmod(numerator, denominator)
        return quotient + (1 if 2 * rest >= denominator else 0)

    monkeypatch.setattr(date_counts, "_rounded", up)


def _not_trimmed(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "_trimmed_number", lambda text: text)
    monkeypatch.setattr(date_counts, "_trimmed_fraction", lambda text: text)


def _no_leap_day(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "_EXCEL_LEAP_SERIAL", -5)
    monkeypatch.setattr(date_counts, "_EXCEL_EARLY_EPOCH", parsing.days_from_civil(1899, 12, 30))


def _exact_where_binary64(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(date_counts, "_spelled_inexact", date_counts._spelled_exact)


def _dealt_down_the_rows(monkeypatch: pytest.MonkeyPatch) -> None:
    """The first build's dealing: the census's words in rank order, down the rows."""

    def in_rank_order(census: "dict[str, int]", dated: int) -> "list[str]":
        words: "list[str]" = []
        for _rank, word in sorted((-census[each], each) for each in census):
            words += [word] * census[word]
        return (words + [date_counts.NO_CONTACT] * dated)[:dated]

    monkeypatch.setattr(generation, "_contacts_dealt", in_rank_order)


def _held_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.10's last pass taking the nearest day off the holes whether or not a rank holds it."""
    original = generation._nearest_day_off

    def any_day(
        value: int, low: int, high: int, day: int, holes: "frozenset[int]", held: "dict[int, int]", free: bool
    ) -> "int | None":
        return original(value, low, high, day, holes, held, False)

    monkeypatch.setattr(generation, "_nearest_day_off", any_day)


def _excel_two_ignored(monkeypatch: pytest.MonkeyPatch) -> None:
    """The holes of a column of counted dates the two placeholder days alone, as on every system but Excel's."""
    monkeypatch.setattr(date_counts, "hole_words", lambda member, moments=False: ("1900-01-01", "9999-12-31"))


def _excel_two_a_day_of_moments(monkeypatch: pytest.MonkeyPatch) -> None:
    """Excel's serial 2 the whole of 2 January on a column of moments too, as the first repair held it."""
    original = date_counts.hole_days
    monkeypatch.setattr(date_counts, "hole_days", lambda member, moments=False: original(member, False))


def _reach_the_members_own(monkeypatch: pytest.MonkeyPatch) -> None:
    """A tail of counted dates reaching as far as the member's spelling allows, as before the verification."""
    monkeypatch.setattr(
        date_counts, "tail_reach", lambda member, written, tail_seconds, at, low_side, edge: edge
    )


def _reach_past_the_instant(monkeypatch: pytest.MonkeyPatch) -> None:
    """The stretches a twin cell may not stand on, Excel's serial 2 left out of them."""
    original = date_counts.blocked_spans

    def without_two(member: str, written: int) -> "tuple[tuple[int, int], ...]":
        two = parsing.days_from_civil(1900, 1, 2) * 86400
        return tuple(span for span in original(member, written) if span[0] != two)

    monkeypatch.setattr(date_counts, "blocked_spans", without_two)


def _islands_cut_the_reach(monkeypatch: pytest.MonkeyPatch) -> None:
    """The reach cut at every stretch beyond the boundary, as the first repair of the verification cut it."""

    def nearest_stretch(member: str, written: int, tail_seconds: int, at: int, low_side: bool, edge: int) -> int:
        nearest: "int | None" = None
        for start, stop in date_counts.blocked_units(member, written, tail_seconds):
            if low_side and stop < at and (nearest is None or stop > nearest):
                nearest = stop
            if not low_side and start > at and (nearest is None or start < nearest):
                nearest = start
        if nearest is None:
            return edge
        reach = at - nearest - 1 if low_side else nearest - at - 1
        return edge if reach < 1 else min(edge, reach)

    monkeypatch.setattr(date_counts, "tail_reach", nearest_stretch)


def _no_islands(monkeypatch: pytest.MonkeyPatch) -> None:
    """No island inside a tail's reach, as 568b597 read the holes as one unit of their midnight."""
    monkeypatch.setattr(
        date_counts, "tail_islands", lambda member, written, tail_seconds, at, low_side, reach: ()
    )


def _stepped_inward_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """An end or group on an island beside the boundary left on it, stepping inward alone."""

    def inward(distance: int, islands: "tuple[tuple[int, int], ...]", reach: int) -> int:
        for nearest, furthest in islands:
            if nearest <= distance <= furthest:
                return nearest - 1 if nearest > 1 else distance
        return distance

    monkeypatch.setattr(date_counts, "off_the_islands", inward)


def _strata_left_on_the_island(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every stratum as the shape drew it, one wholly on an island too."""
    monkeypatch.setattr(
        date_counts,
        "stratum_off_the_islands",
        lambda near, far, islands, reach: ([value for value in near], [value for value in far]),
    )


def _whole_days_alone(monkeypatch: pytest.MonkeyPatch) -> None:
    """G7.10's last pass moving by whole days alone, as before the repair of the verification."""
    original = generation._kept_off_placeholder_days

    def by_days(
        ordinals: "list[int]", lows: "list[int]", highs: "list[int]", day: int,
        holes: "frozenset[int]", grid: int = 0,
    ) -> "list[int]":
        return original(ordinals, lows, highs, day, holes, 0)

    monkeypatch.setattr(generation, "_kept_off_placeholder_days", by_days)


def _repr_never(monkeypatch: pytest.MonkeyPatch) -> None:
    """Seventeen figures written by `%.17g` and a whole count with no `.0`, as `repr` never writes them."""
    monkeypatch.setattr(date_counts, "_REPR_WHOLE_BELOW", 0)
    original = date_counts._spelled_inexact

    def seventeen(numerator: int, denominator: int, form: "date_counts.CountForm") -> str:
        if form.significant == 17 and not form.exponent:
            return f"{numerator / denominator:.17g}"
        return original(numerator, denominator, form)

    monkeypatch.setattr(date_counts, "_spelled_inexact", seventeen)


@pytest.mark.parametrize(
    "mutant",
    (
        _float_arithmetic, _epoch_1970_for_1960, _halves_up, _not_trimmed,
        _no_leap_day, _exact_where_binary64, _dealt_down_the_rows, _repr_never,
        _held_ignored, _excel_two_ignored, _excel_two_a_day_of_moments,
        _reach_the_members_own, _reach_past_the_instant, _islands_cut_the_reach,
        _no_islands, _stepped_inward_only, _strata_left_on_the_island, _whole_days_alone,
    ),
    ids=lambda mutant: mutant.__name__.strip("_"),
)
def test_c1_each_mutant_turns_a_case_red(
    monkeypatch: pytest.MonkeyPatch, mutant: object
) -> None:
    assert _wrong() == []
    mutant(monkeypatch)  # type: ignore[operator]
    assert _wrong(), "the mutant changed no answer of the file"


def test_c1_the_binary64_an_exporter_writes_is_held() -> None:
    """`%.15g` of 00:03:07 on 4 April 2024 ends in 8, where rounding the exact count gives 9."""
    case = _FILE["spellings"]["excel_15g_binary64"]
    assert _spelled(case) == case["answer"] == "45386.0021643518"
    form = date_counts.CountForm(10, True, 15, False, ".", None)
    moment = date_counts.moment_of_iso(f"{case['iso']}", date_counts.SECOND)
    assert moment is not None
    found = date_counts.count_of("excel-1900", moment, date_counts.SECOND)
    assert found is not None
    sign, digits, exponent = date_counts._significant_figures(found[0], found[1], 15)
    assert (sign, digits, exponent) == (False, "453860021643519", 4)
    assert date_counts.spelled_count(found[0], found[1], form) == "45386.0021643518"


def test_c1_the_spreadsheet_reading_is_the_workbook_readers_on_every_whole_serial() -> None:
    """One leap rule: `dialect.sheet_serial_moment` and the counted reading agree on 1 to 70,000."""
    from synthtwin import dialect

    for serial in range(1, 70000):
        moment = date_counts.moment_of("excel-1900", serial, 1, date_counts.DAY)
        mine = f"{serial}" if moment is None else date_counts.iso_text(moment, date_counts.DAY, date_counts.DAY)
        assert dialect.sheet_serial_moment(f"{serial}", "date", False) == mine, serial


# -- C2: question Q3 ------------------------------------------------------


def test_c2_q3_asks_thirteen_of_fourteen_shapes_with_their_member(tmp_path: pathlib.Path) -> None:
    asked: "dict[str, bool]" = {}
    for shape in battery.SHAPES:
        cells, _truth = battery.cells(shape, battery.ROWS, 0)
        said = _q3(_block_of(tmp_path / shape.name, cells))
        asked[shape.name] = said is not None
        if said is not None:
            members = [member for member, _first, _last in said.readings]
            assert shape.system in members, (shape.name, members)
    assert sorted(name for name in asked if not asked[name]) == list(battery.NOT_ASKED)


@pytest.mark.parametrize("scenario", battery.SCENARIOS[1:])
def test_c2_one_stray_value_does_not_silence_q3(tmp_path: pathlib.Path, scenario: str) -> None:
    """The R4 design review's BLOCKER: a typo or a placeholder in one cell in a hundred."""
    asked = 0
    for shape in battery.SHAPES:
        cells, truth = battery.cells(shape, battery.ROWS, 0)
        said = _q3(_block_of(tmp_path / shape.name, battery.dirty(shape, cells, truth, scenario, 0)))
        if said is not None:
            members = [member for member, _first, _last in said.readings]
            assert shape.system in members, (shape.name, scenario)
            asked += 1
    # A KEYING SLIP A CENTURY EARLY CAN LAND INSIDE THE BAND AT ANOTHER WIDTH,
    # which no rule lets stand (`date_counts._text_holds`): Excel birth dates
    # from 1930 keyed in the 1830s read as four figures.
    assert asked >= (12 if scenario in ("typo_past_1", "typos_2", "typos_5") else 13), scenario


@pytest.mark.parametrize("name,least", (("events_1985", 6), ("births_1920", 3)))
def test_c2_the_two_ranges_offer_the_member_that_wrote_them(
    tmp_path: pathlib.Path, name: str, least: int
) -> None:
    """Item 2 of the review: every member of the unit whose wide band holds the column is offered."""
    asked = 0
    for shape in battery.SHAPES:
        said = _q3(_block_of(tmp_path / shape.name, battery.ranged(shape, name, battery.ROWS, 0)))
        if said is None:
            continue
        asked += 1
        assert shape.system in [member for member, _first, _last in said.readings], shape.name
    assert asked >= least


def _median(ordered: "list[float]") -> float:
    middle = (len(ordered) - 1) * 0.5
    low = int(middle)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (middle - low) * (ordered[high] - ordered[low])


def _new_questions(draws: int) -> "tuple[int, int, list[str]]":
    """Columns of the chance battery Q3 asks, and those the fixed-width question did not ask already."""
    asked = 0
    new: "list[str]" = []
    for name in sorted(battery.ORDINARY):
        for draw in range(draws):
            texts = battery.ordinary(name, 1000, draw)
            numbers = [float(text) for text in texts]
            whole = all(value == int(value) for value in numbers)
            found = date_counts.asked_of(
                texts, numbers, taxonomy._needed(0.99, len(texts)),
                _median(sorted(numbers)), whole, floor=11,
            )
            if found is None:
                continue
            asked += 1
            if asking.why_worth_asking(texts) is None:
                new += [f"{name}:{draw}"]
    return asked, len(battery.ORDINARY) * draws, new


def test_c2_no_ordinary_column_gets_a_new_question() -> None:
    """Items 1 and 5: 0 new questions over the chance battery and the review's identifiers.

    Seventy-seven generators at ten draws. The two the second review of
    landing R4 added (its item 4), five-figure record numbers with a few
    six- or seven-figure ones, were asked newly on 10 and 2 of the ten
    draws on e9aa5fb, where rule C let the one-in-a-hundred strays stand
    at another width.
    """
    asked, draws, new = _new_questions(10)
    assert draws == 770 and asked > 0
    assert new == []


def test_c2_rule_c_holds_every_count_beside_the_set_aside_ones_to_one_width(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The second review of landing R4, item 4: rule C asks only what the fixed-width question asks already.

    Five-figure record numbers with half a percent six-figure, or nearly
    one percent seven-figure, are no column of one width, and are not
    asked. Under a rule C that lets the column's commonest width stand
    for one width -- the strays of another width let stand, as the
    one-in-a-hundred allowance did -- they are.
    """

    def asked(name: str) -> int:
        found = 0
        for draw in range(10):
            texts = battery.ordinary(name, 1000, draw)
            numbers = [float(text) for text in texts]
            if date_counts.asked_of(
                texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True,
                floor=11,
            ) is not None:
                found += 1
        return found

    for name in ("record_no_5_some_6", "record_no_5_some_7"):
        assert asked(name) == 0, name

    def commonest_width(present: "list[str]") -> int:
        widths: "dict[int, int]" = {}
        for text in present:
            if not text.isdigit():
                return 0
            widths[len(text)] = widths.get(len(text), 0) + 1
        return max(widths, key=lambda width: widths[width]) if widths else 0

    monkeypatch.setattr(date_counts, "fixed_width", commonest_width)
    assert asked("record_no_5_some_6") > 0


# THE STATED LIMITS, PINNED (the second review of landing R4, item 4): the
# draws of ten on which each `STATED` column is asked where the
# fixed-width question did not ask. Each is a price plan P4-D384 states;
# a count that moves is a change of question Q3.
_STATED_ASKED = {
    "ids_10fig_some_9fig": 10,
    "ids_13fig_some_12fig": 10,
    "salary_mostly_whole_65k": 10,
    "codes_5fig_zero": 10,
    "codes_5fig_minus1": 10,
    "followup_seconds_years": 10,
    "survival_milliseconds_years": 10,
    "age_seconds_whole_days": 10,
}


def test_c2_the_stated_limits_are_asked_as_measured() -> None:
    """Eight ordinary columns Q3 still asks newly, each on the pinned number of ten draws."""
    assert sorted(_STATED_ASKED) == sorted(battery.STATED)
    for name in sorted(battery.STATED):
        new = 0
        for draw in range(10):
            texts = battery.stated(name, 1000, draw)
            numbers = [float(text) for text in texts]
            whole = all(value == int(value) for value in numbers)
            found = date_counts.asked_of(
                texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), whole,
                floor=11,
            )
            if found is not None and asking.why_worth_asking(texts) is None:
                new += 1
        assert new == _STATED_ASKED[name], (name, new)


def test_c2_a_band_from_1970_would_ask_ordinary_columns(monkeypatch: pytest.MonkeyPatch) -> None:
    """Mutant: a band from 1970, which reads a potassium of `4.2` as an instant of 1 January 1970.

    Measurements written to one or two figures -- a potassium, an INR,
    cents -- stand in the band from 1970 as seconds and are asked by it,
    where the band from 1990 asks none. Since the review of landing R4
    the figures check refuses them too (`date_counts.figures_kept`:
    tenths of a second keep no unit), so each guard alone keeps them
    unasked, and the mutant is shown with the check lifted as well.
    """
    monkeypatch.setattr(date_counts, "NARROW_FROM", 1970)
    _asked, _draws, new = _new_questions(4)
    assert new == [], "the figures check alone"
    monkeypatch.setattr(date_counts, "figures_kept", lambda members, present, mark=".": members)
    _asked, _draws, new = _new_questions(4)
    assert new, "a band from 1970 asked nothing new"
    monkeypatch.setattr(date_counts, "NARROW_FROM", 1990)
    _asked, _draws, new = _new_questions(4)
    assert new == [], "the band from 1990 alone"


def test_c2_variable_width_identifiers_are_not_asked() -> None:
    """Item 5: nine- and ten-figure order numbers lie in Unix seconds' band and are not asked."""
    for name in ("csn_9to10", "order_id_9to10"):
        for draw in range(8):
            texts = battery.ordinary(name, 1000, draw)
            numbers = [float(text) for text in texts]
            assert date_counts.asked_of(
                texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True,
                floor=11,
            ) is None, (name, draw)


def test_c2_dates_kept_at_local_midnight_are_not_asked_as_dates_at_utc_midnight(tmp_path: pathlib.Path) -> None:
    """Item 3: rule B reads ONE residue, midnight UTC; New York's two are a stated limit."""
    draw = random.Random(384)
    cells: "list[str]" = []
    for _row in range(1000):
        day = datetime.date(1930, 1, 1) + datetime.timedelta(days=draw.randrange(27394))
        shift = 4 if 4 <= day.month <= 10 else 5
        moment = datetime.datetime(day.year, day.month, day.day, shift)
        cells += [f"{int((moment - datetime.datetime(1970, 1, 1)).total_seconds())}"]
    assert _q3(_block_of(tmp_path, cells)) is None
    at_utc = [f"{int(cell) - int(cell) % 86400}" for cell in cells]
    said = _q3(_block_of(tmp_path / "utc", at_utc))
    assert said is not None and said.rule == date_counts.RULE_MIDNIGHT


def test_c2_the_question_names_no_value_and_says_the_set_aside_numbers(tmp_path: pathlib.Path) -> None:
    """Twenty `0` cells in a thousand: a heap the ladder publishes as the low end.

    The question still offers the 1900 system, its years read past the
    heap (the review of landing R4, item 1: the first build read them off
    the heaped `0`, which names no Excel date, and dropped the system),
    and names `0` among the numbers set aside, which twenty cells hold.
    """
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    cells = battery.heaped(shape, cells, "zero", 0.02)
    path = _table(tmp_path, cells)
    code, said = _exit_of(["profile", str(path), "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-500:]
    questions = json.loads((tmp_path / "table-questions.json").read_text(encoding="utf-8"))
    entries = [entry for entry in questions["asked"] if entry["column"] == "seen"]
    assert len(entries) == 1
    entry = entries[0]
    offered = [choice["answer"] for choice in entry["answers_you_can_give"]]
    assert offered[0] == asking.ANSWER_MEASUREMENT and entry["read_as_now"] == asking.ANSWER_MEASUREMENT
    assert "excel-1900" in offered and "excel-1904" in offered
    shown = entry["what_synthtwin_saw"]
    assert "some cells hold 0" in shown and "they run from 2016 to 2025" in shown
    for cell in set(cells):
        if cell != "0":
            assert cell not in shown


def _offered_of(folder: pathlib.Path) -> "list[str]":
    """The answers the questions file offers about `seen`, or none where it is not asked."""
    questions = json.loads((folder / "table-questions.json").read_text(encoding="utf-8"))
    offered: "list[str]" = []
    for entry in questions["asked"]:
        if entry["column"] == "seen":
            offered += [choice["answer"] for choice in entry["answers_you_can_give"]]
    return offered


def test_c2_a_declared_decimal_comma_is_read_with_the_comma(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Item 8: clinic date-times exported with a comma for the point.

    Under `--decimal-comma` the column is numbers, and Q3 reads its counts
    with the comma, so it is asked with the 1900 system among its answers.
    Undeclared, the cells are text and nothing asks about dates (a stated
    limit). THE MUTANT: Q3 reading the declared column with the point.
    """
    shape = battery.BY_NAME["xl_dt15g"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    commas = [cell.replace(".", ",") for cell in cells]
    assert sum("," in cell for cell in commas) > 900
    path = _table(tmp_path, commas)
    runs = {}
    for name, extra in (("declared", ["--decimal-comma", "seen"]), ("plain", [])):
        folder = tmp_path / name
        folder.mkdir()
        code, said = _exit_of(["profile", str(path), *extra, "--out-dir", str(folder), "--replace"])
        assert code == 0, said[-500:]
        runs[name] = _offered_of(folder)
    assert "excel-1900" in runs["declared"]
    assert not [word for word in runs["plain"] if word in date_counts.MEMBERS]
    original = date_counts.asked_of

    def pointed(*arguments: object, **named: object) -> "date_counts.Asked | None":
        return original(*arguments[:5], **named)  # type: ignore[arg-type]

    monkeypatch.setattr(date_counts, "asked_of", pointed)
    mutated = tmp_path / "mutated"
    mutated.mkdir()
    code, said = _exit_of(["profile", str(path), "--decimal-comma", "seen", "--out-dir", str(mutated), "--replace"])
    assert code == 0, said[-500:]
    assert "excel-1900" not in _offered_of(mutated)


def _table_of(folder: pathlib.Path, columns: "dict[str, list[str]]") -> pathlib.Path:
    """Several columns of one length in a CSV file, none holding a comma."""
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "table.csv"
    names = list(columns)
    rows = [",".join(names)]
    for place in range(len(columns[names[0]])):
        rows += [",".join(columns[name][place] for name in names)]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8", newline="")
    return path


def _rung_of(ordered: "list[float]", percent: int) -> float:
    """A percentile of rising numbers, read between two cells as the ladder reads it."""
    place = (len(ordered) - 1) * percent / 100
    low = int(place)
    high = min(low + 1, len(ordered) - 1)
    return ordered[low] + (place - low) * (ordered[high] - ordered[low])


def _heaps_read_right(folder: pathlib.Path, heap: "object", label: str) -> None:
    """Every asked shape, its heaps laid by ``heap``, offered its writer's system, every system's years its own reading of the dates.

    The writer's system is held to the true span, within one year. EVERY
    SYSTEM OFFERED, the writer's among them, is held to the years it reads
    of the column's own dates at each edge: from the clean column's
    outermost count to its third percentile from that edge -- the deepest
    rung the walk reads past two heaps of one percent -- within one year
    (`date_counts.years_of`). A system that read a placeholder as a date
    of its own printed a year of 9941 or 1889 there (the second review of
    landing R4, item 3).
    """
    shapes = [shape for shape in battery.SHAPES if shape.name not in battery.NOT_ASKED]
    columns: "dict[str, list[str]]" = {}
    clean: "dict[str, tuple[float, float, float, float]]" = {}
    spans: "dict[str, tuple[int, int]]" = {}
    for shape in shapes:
        cells, truth = battery.cells(shape, 10000, 0)
        columns[shape.name] = heap(shape, cells)  # type: ignore[operator]
        ordered = sorted(float(cell) for cell in cells)
        clean[shape.name] = (ordered[0], _rung_of(ordered, 3), _rung_of(ordered, 97), ordered[-1])
        spans[shape.name] = (min(t.year for t in truth), max(t.year for t in truth))
    path = _table_of(folder, columns)
    document = profile.build_document(reading.read_table(str(path)), taxonomy.Settings(), [])
    for shape, block in zip(shapes, document["columns"]):
        said = _q3(block)
        assert said is not None, (label, shape.name)
        years = {member: (first, last) for member, first, last in said.readings}
        assert shape.system in years, (label, shape.name, sorted(years))
        first, last = years[shape.system]
        low, high = spans[shape.name]
        assert abs(first - low) <= 1 and abs(last - high) <= 1, (label, shape.name, years[shape.system], spans[shape.name])
        for member, (first, last) in years.items():
            edges = [date_counts.years_of(member, value) for value in clean[shape.name]]
            assert None not in edges, (label, shape.name, member)
            outer_low, inner_low, inner_high, outer_high = edges
            assert outer_low - 1 <= first <= inner_low + 1, (label, shape.name, member, years[member], edges)  # type: ignore[operator]
            assert inner_high - 1 <= last <= outer_high + 1, (label, shape.name, member, years[member], edges)  # type: ignore[operator]


@pytest.mark.parametrize("kind", battery.PLACEHOLDERS)
def test_c2_a_heap_of_placeholders_keeps_each_shapes_system_and_years(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """The review of landing R4, item 1: a placeholder common enough to be the column's published end.

    At 10,000 rows, two and ten cells in a thousand holding `0`, `-1` or
    the system's own count for 9999-12-31 or 1900-01-01: every shape Q3
    asks is offered the system that wrote it, with years within one of
    the true span -- AND EVERY SYSTEM OFFERED WITH ITS OWN READING OF THE
    COLUMN'S DATES (its second review, item 3: Excel's 31 December 9999
    read as Epic days gave "1957 to 9941", and a Unix 1900 count read from
    1960 "1889 to 2015"; on e9aa5fb, 40 readings over the eight tables).
    The first build read the years off the
    heaped end itself -- `0` names no Excel date, so the 1900 system was
    dropped from the four Excel shapes, and the 9999 count gave "2016 to
    9999".
    """
    for share in (0.002, 0.01):
        _heaps_read_right(
            tmp_path / f"{kind}-{share}",
            lambda shape, cells: battery.heaped(shape, cells, kind, share),
            f"{kind} {share}",
        )


@pytest.mark.parametrize("kinds", battery.PLACEHOLDER_PAIRS, ids=lambda kinds: "+".join(kinds))
def test_c2_two_heaps_at_one_end_keep_each_systems_years(
    tmp_path: pathlib.Path, kinds: "tuple[str, str]"
) -> None:
    """The second review of landing R4, item 3: one percent each of two placeholders at one end.

    `0` and the system's 1900 count, `-1` and it, or `0` and `-1`: the
    second heap need publish no rung of its own, so the rungs before the
    first date are the first heap, one read between the two heaps and one
    read between the second heap and the first date. The walk passed one
    rung beside the first heap and read the next, the writer's first year
    two to four years early on 5 to 8 of the 13 shapes (Excel "2013 to
    2025" for 2016). It now passes every rung with a heap count between it
    and the rung before it, and every system's years are its own reading
    of the column's dates.
    """
    _heaps_read_right(
        tmp_path, lambda shape, cells: battery.heaped_pair(shape, cells, kinds, 0.01), "+".join(kinds)
    )


def test_c2_one_placeholder_cell_is_set_aside_and_not_named(tmp_path: pathlib.Path) -> None:
    """The review of landing R4, item 4: a set-aside number one row holds is no word of NF113.

    One `0` among Unix-second birth dates is a birth on 1 January 1970,
    and one `-1` among SAS days is 31 December 1959: each is still set
    aside for the question, and named only where the census line of
    cells -- eleven -- holds it.
    """
    for name, word in (("unix_s_birth", "0"), ("sas_days", "-1"), ("xl_date", "2")):
        cells, _truth = battery.cells(battery.BY_NAME[name], battery.ROWS, 0)
        for many in (1, 9, 11):
            changed = list(cells)
            for place in range(many):
                changed[100 + 7 * place] = word
            held = changed.count(word)
            said = _q3(_block_of(tmp_path / f"{name}-{many}", changed))
            assert said is not None, (name, many)
            shown = "the count for 1 January 1900" if word == "2" else word
            named = date_counts.aside_listed(said.aside).split(", ")
            assert (shown in named) == (held >= 11), (name, held, said.aside)
            if many == 1:
                assert held < 11 and shown not in named


def test_c2_nf113s_line_follows_the_floor(tmp_path: pathlib.Path) -> None:
    """The second review of landing R4, item 6 (mutant K4b): the census line, not eleven.

    At a floor of 36 the line is 36: a `0` that 11 or 35 of ten thousand
    Unix-second birth dates hold -- births on 1 January 1970 among them --
    is set aside and not named, and one 36 hold is named. A line fixed at
    eleven named the first two.
    """
    cells, _truth = battery.cells(battery.BY_NAME["unix_s_birth"], 10000, 0)
    free = [place for place in range(len(cells)) if cells[place] != "0"]
    for held, named in ((11, False), (35, False), (36, True)):
        changed = list(cells)
        for place in free[: held - cells.count("0")]:
            changed[place] = "0"
        assert changed.count("0") == held
        path = _table(tmp_path / f"zeros-{held}", changed)
        document = profile.build_document(
            reading.read_table(str(path)), taxonomy.Settings(small_cell_floor=36), []
        )
        said = _q3(document["columns"][0])
        assert said is not None, held
        assert ("0" in said.aside) == named, (held, said.aside)


def test_c2_nine_tenths_of_the_present_cells_stand_beside_the_set_aside_ones(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The 90 % share (mutant M04): twelve cells in a hundred holding `0` leave no question."""
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    cells = battery.heaped(shape, cells, "zero", 0.12)
    assert _q3(_block_of(tmp_path / "head", cells)) is None
    monkeypatch.setattr(date_counts, "_rest_is_enough", lambda rest, present: rest >= date_counts.REST_LEAST)
    assert _q3(_block_of(tmp_path / "mutant", cells)) is not None


def test_c2_every_system_of_the_unit_whose_years_fit_is_offered(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The R4 design review's item 2 (mutant M07): SAS days of June 1987 to 1989.

    Read in the 1960 system they lie before the band from 1990, and read
    in the 1970 one inside it, so the rule holds for the 1970 system
    alone; the 1960 system that wrote them is offered beside it because
    its years fit 1900 to 2050.
    """
    draw = random.Random(1987)
    first = datetime.date(1987, 6, 1)
    cells = [
        f"{(first + datetime.timedelta(days=draw.randrange(944)) - datetime.date(1960, 1, 1)).days}"
        for _row in range(battery.ROWS)
    ]
    said = _q3(_block_of(tmp_path / "head", cells))
    assert said is not None
    offered = [member for member, _first, _last in said.readings]
    assert "days-since-1960" in offered and "days-since-1970" in offered

    def hits_alone(
        ordered: "list[float]", hits: "list[str]", total: int, *rest: object
    ) -> "tuple[str, ...]":
        return tuple(hits)

    monkeypatch.setattr(date_counts, "_offered", hits_alone)
    said = _q3(_block_of(tmp_path / "mutant", cells))
    assert said is not None
    assert "days-since-1960" not in [member for member, _first, _last in said.readings]


def _days_at_midnight(days: "list[int]") -> "tuple[list[str], list[float]]":
    texts = [f"{day * 86400}" for day in days]
    return texts, [float(text) for text in texts]


def test_c2_rule_b_reads_eleven_different_days_at_midnight(monkeypatch: pytest.MonkeyPatch) -> None:
    """Rule B (mutant M35): Unix seconds at midnight UTC of births before 1990, eleven different days or more.

    Ten different days repeated over a thousand rows are no column of
    dates rule B may ask about; eleven are.
    """
    first = parsing.days_from_civil(1935, 3, 1)
    for different, asked in ((10, False), (11, True)):
        days = [first + 997 * (row % different) for row in range(battery.ROWS)]
        texts, numbers = _days_at_midnight(days)
        found = date_counts.asked_of(
            texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True,
            floor=11,
        )
        assert (found is not None) == asked, different
        if found is not None:
            assert found.rule == date_counts.RULE_MIDNIGHT
    days = [first + 997 * (row % 10) for row in range(battery.ROWS)]
    texts, numbers = _days_at_midnight(days)
    monkeypatch.setattr(date_counts, "REST_LEAST", 1)
    assert date_counts.asked_of(
        texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), True,
        floor=11,
    ) is not None


def test_c2_money_amounts_and_lengths_of_time_are_not_asked(monkeypatch: pytest.MonkeyPatch) -> None:
    """The review of landing R4, item 7: four ordinary shapes the first build asked about, newly.

    Salaries and payments in cents and amounts to one decimal in Excel's
    five-figure band, a room charge in cents read as Epic days, and
    lengths of time kept as whole days of seconds or of milliseconds.
    Each is asked once its rule is put back as it was: rule A without its
    four figures of a day or its Epic days mostly whole, rule B without
    its year from the epoch or its thousand-day step. One or two figures
    of a day keep no unit (`date_counts.figures_kept`), so the four
    figures are the cheap half of a refusal the figures check would reach
    after a second walk of the cells: the money and the amounts to one
    figure are asked only with both lifted.
    """
    names = (
        "salary_cents_45k", "payment_cents_20k", "room_charge_cents_62k", "glucose_area_1dp",
        "dose_total_1dp", "stay_seconds_whole_days", "gap_milliseconds_whole_days",
        "followup_seconds_whole_days",
    )

    def asked(name: str, draw: int) -> bool:
        texts = battery.ordinary(name, 1000, draw)
        numbers = [float(text) for text in texts]
        whole = all(value == int(value) for value in numbers)
        return date_counts.asked_of(
            texts, numbers, taxonomy._needed(0.99, len(texts)), _median(sorted(numbers)), whole,
            floor=11,
        ) is not None

    for name in names:
        assert not any(asked(name, draw) for draw in range(4)), name

    def second_walk(members: "tuple[str, ...]", present: "list[str]", mark: str = ".") -> "tuple[str, ...]":
        raise AssertionError(f"the four figures let a column of cents reach the figures check {members}")

    # THE CHEAP HALF REFUSES FIRST: money in cents is never walked again.
    monkeypatch.setattr(date_counts, "figures_kept", second_walk)
    assert not asked("salary_cents_45k", 0) and not asked("dose_total_1dp", 0)
    monkeypatch.undo()
    monkeypatch.setattr(date_counts, "DAY_TIME_PLACES", 0)
    assert not asked("salary_cents_45k", 0) and not asked("dose_total_1dp", 0)
    monkeypatch.setattr(date_counts, "figures_kept", lambda members, present, mark=".": members)
    assert asked("salary_cents_45k", 0) and asked("dose_total_1dp", 0)
    monkeypatch.undo()
    monkeypatch.setattr(date_counts, "figures_kept", lambda members, present, mark=".": members)
    assert not asked("salary_cents_45k", 0) and not asked("dose_total_1dp", 0)
    monkeypatch.undo()
    original = date_counts._text_holds

    def any_contacts(present: "list[str]", member: str, rule: str, needed: int, mark: str = ".") -> bool:
        if date_counts.TABLE[member].contacts:
            return sum(date_counts.counted(member, text, mark) is not None for text in present) >= needed
        return original(present, member, rule, needed, mark)

    monkeypatch.setattr(date_counts, "_text_holds", any_contacts)
    assert asked("room_charge_cents_62k", 0)
    monkeypatch.undo()
    monkeypatch.setattr(date_counts, "EPOCH_YEAR_DAYS", 0)
    assert asked("stay_seconds_whole_days", 0)
    monkeypatch.undo()
    # Whole days of milliseconds read as seconds stand every thousand days.
    monkeypatch.setattr(date_counts, "UNIT_STEP_DAYS", 10**18)
    assert asked("gap_milliseconds_whole_days", 0)


def test_c2_a_system_whose_answer_is_refused_is_not_offered(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The review of landing R4, item 2, as question Q3 sees it: figures no unit keeps are asked nothing.

    Unix seconds written with tenths or hundredths, and four figures of a
    day of moments off the minute, are no counted dates a twin could be
    drawn at, and their declaration is refused (NF115). Q3 asks the
    profiler's own decision first (`date_counts.figures_kept`, over
    `date_counts.settled_reading`): such a column is asked nothing, and
    the two `COARSE` columns a unit keeps are asked with the system that
    wrote them and read as dates once answered. Without the check Q3
    asked about the tenths, and every system it offered was refused.
    """
    for name in sorted(battery.COARSE):
        system, _write, kept = battery.COARSE[name]
        cells = battery.coarse(name, battery.ROWS, 0)
        said = _q3(_block_of(tmp_path / name, cells))
        offered = [] if said is None else [member for member, _first, _last in said.readings]
        assert (system in offered) == kept and (kept or not offered), (name, offered)
        for member in offered:
            assert _block_of(tmp_path / f"{name}-{member}", cells, member)["role"] == "datetime", (name, member)
    monkeypatch.setattr(date_counts, "figures_kept", lambda members, present, mark=".": members)
    cells = battery.coarse("unix_s_1dp", battery.ROWS, 0)
    said = _q3(_block_of(tmp_path / "mutant", cells))
    assert said is not None and said.readings
    for member, _first, _last in said.readings:
        assert _block_of(tmp_path / f"mutant-{member}", cells, member)["role"] != "datetime", member


# -- C3: the answer and the option ---------------------------------------


def test_c3_an_answered_file_and_the_typed_option_give_one_description(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shape = battery.BY_NAME["sas_days"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    path = _table(tmp_path, cells)
    plain = tmp_path / "plain"
    plain.mkdir()
    assert _exit_of(["profile", str(path), "--out-dir", str(plain), "--replace"])[0] == 0
    questions = json.loads((plain / "table-questions.json").read_text(encoding="utf-8"))
    for entry in questions["asked"]:
        if entry["column"] == "seen":
            entry["your_answer"] = "days-since-1960"
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    answered = tmp_path / "answered"
    typed = tmp_path / "typed"
    answered.mkdir()
    typed.mkdir()
    code, said = _exit_of(["profile", str(path), "--answers", str(answers), "--out-dir", str(answered), "--replace"])
    assert code == 0, said[-600:]
    # THE LINE THAT REPEATS THE RUN NAMES THE ANSWER AS ITS OPTION (mutant
    # M51: the repeat command dropping `--date-count`).
    assert "TO REPEAT THIS RUN WITHOUT THE QUESTIONS" in said
    assert "--date-count seen days-since-1960" in said
    assert _exit_of(["profile", str(path), "--date-count", "seen", "days-since-1960", "--out-dir", str(typed), "--replace"])[0] == 0
    one = (answered / "table-profile.json").read_bytes()
    assert one == (typed / "table-profile.json").read_bytes()
    document = json.loads(one)
    assert document["settings"]["forced_date_counts"] == [["seen", "days-since-1960"]]
    block = document["columns"][0]
    assert block["role"] == "datetime" and block["format"] == "iso-date"
    assert block["count_form"] == {
        "contacts": None, "exponent": False, "mark": ".", "places": 0,
        "significant": None, "trimmed": False,
    }
    # THE MUTANT: the answer dropped.
    original = asking.answers_in

    def dropped(document: object, shown: str) -> asking.Answers:
        return dataclasses.replace(original(document, shown), date_counts=())

    monkeypatch.setattr(asking, "answers_in", dropped)
    mutated = tmp_path / "mutated"
    mutated.mkdir()
    assert _exit_of(["profile", str(path), "--answers", str(answers), "--out-dir", str(mutated), "--replace"])[0] == 0
    assert (mutated / "table-profile.json").read_bytes() != one


def test_c3_a_system_outside_the_twelve_is_refused_before_the_table_is_read(tmp_path: pathlib.Path) -> None:
    path = _table(tmp_path, ["45000"] * 200)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", "excel-2000", "--out-dir", str(tmp_path)])
    assert code == 2 and "is not one of the systems synthtwin reads" in said
    assert not (tmp_path / "table-profile.json").exists()


def test_c3_a_counted_column_also_named_a_code_is_refused(tmp_path: pathlib.Path) -> None:
    path = _table(tmp_path, ["45000"] * 200)
    code, said = _exit_of([
        "profile", str(path), "--date-count", "seen", "excel-1900", "--code", "seen",
        "--out-dir", str(tmp_path),
    ])
    assert code == 2
    assert not (tmp_path / "table-profile.json").exists()


# -- C4 and C5: the twin, and its check ----------------------------------


def _trip(folder: pathlib.Path, cells: "list[str]", member: str, *extra: str) -> "dict[str, object]":
    path = _table(folder, cells)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", member, "--out-dir", str(folder), "--replace", *extra])
    assert code == 0, said[-800:]
    described = folder / "table-profile.json"
    code, said = _exit_of(["generate", str(described), "--seed", "0", "--out-dir", str(folder), "--replace"])
    assert code == 0, said[-800:]
    twin = [row[0] for row in list(csv.reader(io.StringIO((folder / "table-twin.csv").read_text(encoding="utf-8"))))[1:] if row]
    exits = []
    for checked in (folder / "table-twin.csv", path):
        out = folder / f"check-{checked.stem}"
        out.mkdir(exist_ok=True)
        exits += [_exit_of(["validate", str(described), "--twin", str(checked), "--out-dir", str(out), "--replace"])[0]]
    return {
        "described": described,
        "block": json.loads(described.read_text(encoding="utf-8"))["columns"][0],
        "twin": twin,
        "twin_exit": exits[0],
        "real_exit": exits[1],
        "path": path,
    }


@pytest.mark.parametrize("name", ("xl_date", "xl_dt15g", "sas_secs", "unix_ms", "epic_real", "unix_s_birth"))
def test_c4_every_twin_cell_keeps_the_columns_spelling_and_names_a_date(
    tmp_path: pathlib.Path, name: str
) -> None:
    shape = battery.BY_NAME[name]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, shape.system)
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in trip["twin"]:
        written = date_counts.written_count(cell, facts.count_form.mark)
        assert written is not None and date_counts.form_holds(shape.system, facts.count_form, written), cell
        numerator, denominator = date_counts.exact_value(written)
        assert date_counts.moment_of(shape.system, numerator, denominator, unit) is not None, cell
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    if shape.kind == "date":
        real = [battery.decode(shape.system, cell) for cell in cells]
        fake = [battery.decode(shape.system, cell) for cell in trip["twin"]]
        assert battery.tvd(
            battery.weekday_shares([m for m in real if m is not None]),
            battery.weekday_shares([m for m in fake if m is not None]),
        ) <= 0.03
    if name == "epic_real":
        assert facts.count_form.contacts is not None
        words = [date_counts.contact_word(date_counts.written_count(cell)) for cell in trip["twin"]]  # type: ignore[arg-type]
        for word, count in facts.count_form.contacts.items():
            assert words.count(word) == count


def test_c4_the_counted_route_never_calls_the_whole_share_pass(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The R4 design review, item 4: `_whole_enough` is stage 4 lane S2's, and quadratic.

    An Epic `*_DATE_REAL` column read as numbers takes that pass, which
    grows as the square of its rows; declared, it is drawn as dates and
    never reaches it. The undeclared run calling it is what keeps the
    count from being nought by accident.
    """
    shape = battery.BY_NAME["epic_real"]
    cells, _truth = battery.cells(shape, 300, 0)
    calls = [0]
    original = generation._whole_enough

    def counted(*arguments: object, **named: object) -> object:
        calls[0] += 1
        return original(*arguments, **named)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_whole_enough", counted)
    _trip(tmp_path / "declared", cells, shape.system)
    assert calls[0] == 0
    path = _table(tmp_path / "plain", cells)
    folder = tmp_path / "plain"
    assert _exit_of(["profile", str(path), "--out-dir", str(folder), "--replace"])[0] == 0
    described = folder / "table-profile.json"
    assert json.loads(described.read_text(encoding="utf-8"))["columns"][0]["role"] == "continuous"
    assert _exit_of(["generate", str(described), "--seed", "0", "--out-dir", str(folder), "--replace"])[0] == 0
    assert calls[0] > 0


def test_c4_the_twin_written_with_the_1970_epoch_is_missed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shape = battery.BY_NAME["sas_days"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    original = date_counts.written_for

    def shifted(member: str, moment: int, unit: int, form: "date_counts.CountForm", contact: str = date_counts.NO_CONTACT) -> "str | None":
        return original("days-since-1970" if member == "days-since-1960" else member, moment, unit, form, contact)

    monkeypatch.setattr(generation.date_counts, "written_for", shifted)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 3


def _rewritten(trip: "dict[str, object]", folder: pathlib.Path, change: "object") -> int:
    twin = [change(cell) for cell in trip["twin"]]  # type: ignore[operator]
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "changed.csv"
    path.write_text("seen\n" + "\n".join(twin) + "\n", encoding="utf-8", newline="")
    out = folder / "check-changed"
    out.mkdir(exist_ok=True)
    return _exit_of(["validate", str(trip["described"]), "--twin", str(path), "--out-dir", str(out), "--replace"])[0]


def test_c5_validate_misses_a_twin_written_another_way(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 0

    def as_iso(cell: str) -> str:
        return (datetime.date(1899, 12, 30) + datetime.timedelta(days=int(cell))).isoformat()

    assert _rewritten(trip, tmp_path / "iso", as_iso) == 3
    assert _rewritten(trip, tmp_path / "member", lambda cell: f"{int(cell) - 1462}") == 3
    assert _rewritten(trip, tmp_path / "places", lambda cell: f"{cell}.000") == 3
    # THE MUTANT: a check of the form that asks nothing passes the ISO twin.
    monkeypatch.setattr(validation, "_count_form_checks", lambda *arguments: [])
    assert _rewritten(trip, tmp_path / "vacuous", as_iso) == 0


def test_c5_a_count_that_names_no_date_is_no_value_and_written_back(tmp_path: pathlib.Path) -> None:
    """Item 1 under a declaration: Excel's 0 and 60 are counted as no value, never voiding it."""
    shape = battery.BY_NAME["xl_date"]
    cells, truth = battery.cells(shape, battery.ROWS, 0)
    cells = battery.dirty(shape, cells, truth, "zero_1pct", 0)
    for place in range(20, 40):
        cells[place] = "60"
    trip = _trip(tmp_path, cells, shape.system)
    block = trip["block"]
    assert block["role"] == "datetime"
    assert block["missing_by_source"] == {"0": 10, "60": 20} or block["missing_by_source"] == {"60": 20}
    assert block["missing_by_class"]["(declared-missing)"] >= 20
    assert trip["twin"].count("60") == 20
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0


def test_c5_a_declaration_whose_cells_are_no_dates_decides_nothing(tmp_path: pathlib.Path) -> None:
    """CD1 and NF115: the column is described as it reads, and the run says so."""
    draw = random.Random(115)
    cells = [f"A{draw.randrange(100, 999)}" for _row in range(300)]
    path = _table(tmp_path, cells)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", "excel-1900", "--out-dir", str(tmp_path), "--replace"])
    assert code == 0 and "did not read as such" in said
    block = json.loads((tmp_path / "table-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["role"] != "datetime"
    assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in block["remarks"])
    rendered = taxonomy.rendered(taxonomy.REMARK_COUNTED_DATES_NOT_READ, ("excel-1900",))
    assert contract.COUNTED_NOT_READ_MARK in rendered


def test_c5_a_contact_number_rarer_than_the_line_leaves_the_source_whole(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Five `.03` cells are counted into the commonest contact number, and the source still meets its form.

    THE MUTANT: the form holding each cell to a contact number the census
    names, which the source's five cells are not, so the real table
    missed its own description.
    """
    draw = random.Random(3)
    cells: "list[str]" = []
    for row in range(1000):
        contact = "" if row < 850 else ".01" if row < 970 else ".02" if row < 995 else ".03"
        cells += [f"{65000 + draw.randrange(3000)}{contact}"]
    draw.shuffle(cells)
    trip = _trip(tmp_path, cells, "days-since-1840")
    assert trip["block"]["count_form"]["contacts"] == {"(none)": 855, "01": 120, "02": 25}
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0

    def named_only(member: str, form: "date_counts.CountForm", written: "date_counts.Written") -> bool:
        return date_counts.contact_word(written) in (form.contacts or {})

    monkeypatch.setattr(date_counts, "form_holds", named_only)
    out = tmp_path / "mutated"
    out.mkdir()
    assert _exit_of(["validate", str(trip["described"]), "--twin", str(trip["path"]), "--out-dir", str(out), "--replace"])[0] == 3


def _trip_of(
    folder: pathlib.Path, columns: "dict[str, list[str]]", declared: "dict[str, str]", *extra: str
) -> "dict[str, object]":
    """Several columns, each of ``declared`` named with `--date-count`, described, twinned and checked."""
    path = _table_of(folder, columns)
    argv = ["profile", str(path), "--out-dir", str(folder), "--replace", *extra]
    for name in sorted(declared):
        argv += ["--date-count", name, declared[name]]
    code, said = _exit_of(argv)
    came: "dict[str, object]" = {"profile": code, "said": said[-600:]}
    if code != 0:
        return came
    described = folder / "table-profile.json"
    blocks = json.loads(described.read_text(encoding="utf-8"))["columns"]
    came["blocks"] = {block["name"]: block for block in blocks}
    came["generate"] = _exit_of(["generate", str(described), "--seed", "0", "--out-dir", str(folder), "--replace"])[0]
    for label, checked in (("twin", folder / "table-twin.csv"), ("source", path)):
        out = folder / f"check-{label}"
        out.mkdir(exist_ok=True)
        came[label] = _exit_of(["validate", str(described), "--twin", str(checked), "--out-dir", str(out), "--replace"])[0]
    return came


def _epic_days(rows: int, ones: int, twos: int = 0, dated: int = -1) -> "list[str]":
    """An Epic `*_DATE_REAL` column: ``ones`` dates written `.01`, ``twos`` `.02`, the rest whole; ``dated`` dates in all, the rest empty."""
    draw = random.Random(f"rare-contacts:{rows}:{ones}:{twos}:{dated}")
    dates = rows if dated < 0 else dated
    cells: "list[str]" = []
    for row in range(dates):
        contact = ".01" if row < ones else ".02" if row < ones + twos else ""
        cells += [f"{64000 + draw.randrange(3650)}{contact}"]
    cells += [""] * (rows - dates)
    draw.shuffle(cells)
    return cells


def test_c5_contact_numbers_none_of_which_reaches_the_line_publish_no_census(tmp_path: pathlib.Path) -> None:
    """The second review of landing R4, item 1: a census of `(none)` alone is not published.

    Eight or ten `.01` among a thousand Epic days, six among ten thousand,
    four `.01` and two `.02` among ten thousand, the battery's own
    `epic_real` at 250 rows and a floor of 36, five dates of a thousand
    rows one of them `.01`, and nine of two hundred five of them `.01`:
    no contact number reaches the census line. The build pooled each into
    `{"(none)": N}`, whose twin wrote no contact number, published no
    census of its own and missed `form.contacts` -- and where the dates
    were fewer than the line the pool itself was under it, and `profile`
    stopped with an internal fault. No census is published now, the twin
    writes day counts alone, and every file is at exit 0; the source's
    rare contact numbers still stand in its own form, which reads an Epic
    column by its contact rule (`date_counts.form_holds`). With 27 `.01`
    among a thousand the census is published as before.
    """
    tables = (
        (1000, {"eight": _epic_days(1000, 8), "ten": _epic_days(1000, 10), "sparse": _epic_days(1000, 1, 0, 5)}, ()),
        (10000, {"six": _epic_days(10000, 6), "four_two": _epic_days(10000, 4, 2)}, ()),
        (200, {"nine": _epic_days(200, 5, 0, 9)}, ()),
        (250, {"battery": battery.cells(battery.BY_NAME["epic_real"], 250, 0)[0]}, ("--smallest-group", "36")),
        (1000, {"common": _epic_days(1000, 27)}, ()),
    )
    for rows, columns, extra in tables:
        named = sorted(columns)
        columns = dict(columns)
        columns["k"] = ["a" if row % 3 else "b" for row in range(rows)]
        came = _trip_of(tmp_path / "-".join(named), columns, {name: "days-since-1840" for name in named}, *extra)
        assert came["profile"] == 0, came["said"]
        assert (came["generate"], came["twin"], came["source"]) == (0, 0, 0), (named, came)
        blocks = came["blocks"]
        assert isinstance(blocks, dict)
        for name in named:
            form = blocks[name]["count_form"]
            assert form is not None and form["places"] == 2, (name, form)
            if name == "common":
                assert form["contacts"] == {"(none)": 973, "01": 27}
            else:
                assert form["contacts"] is None, (name, form)


# How each system the next clause writes counts days, read with `datetime`.
_SPANS = {
    "days-since-1960": (datetime.date(1960, 1, 1), 1),
    "seconds-since-1970": (datetime.date(1970, 1, 1), 86400),
    "seconds-since-1960": (datetime.date(1960, 1, 1), 86400),
}


def _day_written(system: str, cell: str) -> datetime.date:
    """The day a cell of the next clause names, read the way its owner reads it."""
    if system == "excel-1900":
        serial = int(cell)
        first = datetime.date(1899, 12, 31) if serial < 61 else datetime.date(1899, 12, 30)
        return first + datetime.timedelta(days=serial)
    first, per_day = _SPANS[system]
    return first + datetime.timedelta(days=int(cell) // per_day)


def _counted_from(system: str, moment: datetime.datetime) -> str:
    """A moment written as ``system`` writes it, a whole count."""
    if system == "excel-1900":
        first = datetime.datetime(1899, 12, 31) if moment < datetime.datetime(1900, 3, 1) else datetime.datetime(1899, 12, 30)
        return f"{(moment - first).days}"
    epoch, per_day = _SPANS[system]
    seconds = (moment - datetime.datetime.combine(epoch, datetime.time())).total_seconds()
    return f"{int(seconds) // (86400 // per_day)}"


def test_c5_a_counted_column_crossing_1_january_1900_twins_no_date_on_it(tmp_path: pathlib.Path) -> None:
    """The second review of landing R4, item 2: the days a counted column reads as no value are holes.

    Every count naming 1 January 1900 or 31 December 9999 is no value, and
    so is Excel's serial 2, the count pandas writes for 1 January 1900 --
    which the 1900 system reads as 2 January. The build published no hole
    there, so the twin drew those days and read them back as no value:
    births of 1890 to 1935 as SAS days or Unix seconds at midnight, and of
    1900 to 1935 as Excel serials, at 10,000 rows, missed `n_present` on
    1, 2 and 3 seeds of 3; and every twin of dates or moments packed
    around the day, at 1,000 rows, drew it. Each such day is now a hole of
    the column (`date_counts.hole_words`): the source's real dates there
    are no value, the twin writes none, and both files are at exit 0 on
    seeds 0 to 2.
    """
    draw = random.Random(1900)
    births = {
        "sas_days": ("days-since-1960", datetime.date(1890, 1, 1), 16437),
        "unix_s": ("seconds-since-1970", datetime.date(1890, 1, 1), 16437),
        "xl": ("excel-1900", datetime.date(1900, 1, 1), 12784),
    }
    packed = {
        "sas_days_packed": ("days-since-1960", datetime.date(1899, 7, 1), 366),
        "sas_secs_packed": ("seconds-since-1960", datetime.date(1899, 7, 1), 366),
        "xl_packed": ("excel-1900", datetime.date(1900, 1, 1), 365),
    }
    for rows, spans in ((10000, births), (1000, packed)):
        columns: "dict[str, list[str]]" = {}
        members: "dict[str, str]" = {}
        for name, (system, first, days) in spans.items():
            cells: "list[str]" = []
            for _row in range(rows):
                moment = datetime.datetime.combine(first, datetime.time()) + datetime.timedelta(days=draw.randrange(days))
                if name == "sas_secs_packed":
                    moment = moment + datetime.timedelta(seconds=draw.randrange(86400))
                cells += [_counted_from(system, moment)]
            columns[name] = cells
            members[name] = system
        folder = tmp_path / f"rows-{rows}"
        path = _table_of(folder, columns)
        argv = ["profile", str(path), "--out-dir", str(folder), "--replace"]
        for name in sorted(members):
            argv += ["--date-count", name, members[name]]
        code, said = _exit_of(argv)
        assert code == 0, said[-600:]
        described = folder / "table-profile.json"
        blocks = {block["name"]: block for block in json.loads(described.read_text(encoding="utf-8"))["columns"]}
        holes: "dict[str, set[datetime.date]]" = {}
        for name, system in members.items():
            # Both placeholder days, and on Excel's 1900 system 2 January,
            # its serial 2 being the count pandas writes for 1 January.
            holes[name] = {datetime.date(1900, 1, 1), datetime.date(9999, 12, 31)}
            if system == "excel-1900":
                holes[name] = holes[name] | {datetime.date(1900, 1, 2)}
            on_holes = sum(_day_written(system, cell) in holes[name] for cell in columns[name])
            assert blocks[name]["role"] == "datetime" and blocks[name]["n_present"] == rows - on_holes, name
        for seed in (0, 1, 2):
            code, said = _exit_of(["generate", str(described), "--seed", f"{seed}", "--out-dir", str(folder), "--replace"])
            assert code == 0, said[-600:]
            twin = list(csv.reader(io.StringIO((folder / "table-twin.csv").read_text(encoding="utf-8"))))
            header = twin[0]
            for name, system in members.items():
                at = header.index(name)
                on = [row[at] for row in twin[1:] if row and row[at] and _day_written(system, row[at]) in holes[name]]
                assert on == [], (rows, seed, name, on[:3])
            out = folder / f"check-twin-{seed}"
            out.mkdir()
            assert _exit_of([
                "validate", str(described), "--twin", str(folder / "table-twin.csv"), "--out-dir", str(out), "--replace",
            ])[0] == 0, (rows, seed)
        out = folder / "check-source"
        out.mkdir()
        assert _exit_of(["validate", str(described), "--twin", str(path), "--out-dir", str(out), "--replace"])[0] == 0
    for system in ("excel-1900", "days-since-1960", "seconds-since-1970", "days-since-1840"):
        wanted = ["1900-01-01", "1900-01-02", "9999-12-31"] if system == "excel-1900" else ["1900-01-01", "9999-12-31"]
        assert list(date_counts.hole_words(system)) == wanted, system


def _excel_births_from_1900(drawn_by: str) -> "list[str]":
    """Ten thousand Excel date-times `%.15g` at whole minutes, births from 1 January 1900 to 1935."""
    draw = random.Random(drawn_by)
    cells: "list[str]" = []
    for _row in range(10000):
        moment = datetime.datetime(1900, 1, 1) + datetime.timedelta(
            days=draw.randrange(12784), seconds=60 * draw.randrange(1440)
        )
        first = datetime.datetime(1899, 12, 31) if moment < datetime.datetime(1900, 3, 1) else datetime.datetime(1899, 12, 30)
        delta = moment - first
        cells += ["%.15g" % (delta.days + delta.seconds / 86400)]
    return cells


def test_c5_excel_date_times_from_1900_twin_no_cell_on_1_january_and_no_text(tmp_path: pathlib.Path) -> None:
    """The verification of the second review's item 2: a tail of moments stops short of the days no count holds.

    Excel date-times of births from 1 January 1900 to 1935 at whole
    minutes, written `%.15g`, in the two draws the verification measured,
    at 10,000 rows. The source's few cells on 1 January are no value, so
    its lowest present date stands on 2 January, and the low tail drawn
    from its two published distances reached past it: 568b597 stepped the
    end off 00:00 of 1 January alone, left a rank on that day inside a
    stratum less than a day wide, which no whole day's move fits, and held
    all of 2 January a hole on a column of moments; the twin wrote
    `1.83263888888889` (19:59 on 1 January), read back as no value, and
    its end `1899-12-31 06:20` before Excel's first day, as ISO text -- 6
    seeds of 6 on the first draw and 3 of 6 on the second at exit 3. Each
    tail now stops one unit short of the nearest stretch its counts cannot
    hold (`date_counts.tail_reach`: 00:01 on 2 January here, past the
    instant serial 2 names), and on a column of moments only the
    placeholder days are holes. On seeds 0 to 5 every twin cell is a count
    naming a date -- none on 1 January 1900, none set aside, none text --
    and twin and source are both at exit 0. Red on 568b597.
    """
    columns = {
        "births": _excel_births_from_1900("tail1900:excel_dt_from_1900:10000"),
        "born": _excel_births_from_1900("p1900dt:excel_dt_1900_1935:10000"),
    }
    path = _table_of(tmp_path, columns)
    argv = ["profile", str(path), "--out-dir", str(tmp_path), "--replace"]
    for name in sorted(columns):
        argv += ["--date-count", name, "excel-1900"]
    code, said = _exit_of(argv)
    assert code == 0, said[-600:]
    described = tmp_path / "table-profile.json"
    blocks = {block["name"]: block for block in json.loads(described.read_text(encoding="utf-8"))["columns"]}
    aside: "dict[int, int]" = {}
    for number in date_counts.declared_aside("excel-1900"):
        aside[number] = 1
    first_day = parsing.days_from_civil(1900, 1, 1)
    for seed in range(6):
        code, said = _exit_of(["generate", str(described), "--seed", f"{seed}", "--out-dir", str(tmp_path), "--replace"])
        assert code == 0, said[-600:]
        rows = list(csv.reader(io.StringIO((tmp_path / "table-twin.csv").read_text(encoding="utf-8"))))
        header = rows[0]
        for name in sorted(columns):
            assert blocks[name]["role"] == "datetime" and blocks[name]["time_precision"] == "minute", name
            absent = blocks[name].get("missing_by_source") or {}
            at = header.index(name)
            for row in rows[1:]:
                cell = row[at]
                if not cell or cell in absent:
                    continue
                written = date_counts.written_count(cell)
                assert written is not None, (seed, name, cell)
                numerator, denominator = date_counts.exact_value(written)
                moment = date_counts.moment_of("excel-1900", numerator, denominator, date_counts.MINUTE)
                assert moment is not None and (moment * 60) // 86400 != first_day, (seed, name, cell)
                assert not date_counts.stands_aside(numerator, denominator, False, aside), (seed, name, cell)
        out = tmp_path / f"check-twin-{seed}"
        out.mkdir()
        assert _exit_of([
            "validate", str(described), "--twin", str(tmp_path / "table-twin.csv"), "--out-dir", str(out), "--replace",
        ])[0] == 0, seed
    out = tmp_path / "check-source"
    out.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(path), "--out-dir", str(out), "--replace"])[0] == 0
    assert list(date_counts.hole_words("excel-1900", True)) == ["1900-01-01", "9999-12-31"]


def _counted_near_the_holes(shape: str) -> "tuple[str, list[str]]":
    """Counts whose tails meet the days the system holds no date on, and the system.

    Ten thousand, the last century before 10000 a thousand: as many as
    put the tail drawn by 568b597 across one of those days.
    """
    draw = random.Random(f"near-the-holes:{shape}")
    cells: "list[str]" = []
    for _row in range(1000 if shape == "unix_days_to_9999" else 10000):
        if shape in ("excel_moments", "excel_moments_packed"):
            days = 12784 if shape == "excel_moments" else 90
            moment = datetime.datetime(1900, 1, 1) + datetime.timedelta(days=draw.randrange(days), seconds=60 * draw.randrange(1440))
            first = datetime.datetime(1899, 12, 31) if moment < datetime.datetime(1900, 3, 1) else datetime.datetime(1899, 12, 30)
            delta = moment - first
            cells += ["%.15g" % (delta.days + delta.seconds / 86400)]
        elif shape == "excel_dates":
            day = datetime.date(1900, 1, 1) + datetime.timedelta(days=draw.randrange(12784))
            first = datetime.date(1899, 12, 31) if day < datetime.date(1900, 3, 1) else datetime.date(1899, 12, 30)
            cells += [f"{(day - first).days}"]
        elif shape == "excel_1904_seconds":
            seconds = draw.randrange(4000) * 86400 + draw.randrange(86400)
            cells += ["%.15g" % (seconds / 86400)]
        elif shape == "sas_moments":
            moment = datetime.datetime(1900, 1, 1) + datetime.timedelta(days=draw.randrange(12784), seconds=draw.randrange(86400))
            cells += [f"{int((moment - datetime.datetime(1960, 1, 1)).total_seconds())}"]
        elif shape in ("sas_days_across", "sas_seconds_across"):
            break
        else:
            day = datetime.date(9900, 1, 1) + datetime.timedelta(days=draw.randrange(36523))
            cells += [f"{(day - datetime.date(1970, 1, 1)).days}"]
    if shape == "sas_days_across":
        return "days-since-1960", _across_1900("sas_days")
    if shape == "sas_seconds_across":
        return "seconds-since-1960", _across_1900("sas_seconds")
    member = {
        "excel_moments": "excel-1900", "excel_moments_packed": "excel-1900", "excel_dates": "excel-1900",
        "excel_1904_seconds": "excel-1904", "sas_moments": "seconds-since-1960", "unix_days_to_9999": "days-since-1970",
    }[shape]
    return member, cells


def _across_1900(shape: str) -> "list[str]":
    """Ten thousand counts whose low tail runs across 1 January 1900, in a system writing the days either side.

    `sas_days`: eight SAS days in December 1899, none on 1 January, the
    rest from 3 January 1900 to 1935 -- a low boundary on 7 January.
    `sas_seconds` and `unix_minutes`: five moments on the evening of 31
    December 1899, a crowd of three hundred on 2 January and the rest to
    1935, SAS seconds at the second or Unix milliseconds at the minute --
    a low tail of eleven within the first hour of 2 January and the
    evening before, its strata hours wide.
    """
    draw = random.Random(f"across-1900:{shape}")
    step = 86400 if shape == "sas_days" else 60 if shape == "unix_minutes" else 1
    moments: "list[datetime.datetime]" = []
    if shape == "sas_days":
        for _row in range(8):
            moments += [datetime.datetime(1899, 12, 1) + datetime.timedelta(days=draw.randrange(31))]
    else:
        for _row in range(5):
            moments += [datetime.datetime(1899, 12, 31, 18) + datetime.timedelta(seconds=step * draw.randrange(21600 // step))]
        for _row in range(300):
            moments += [datetime.datetime(1900, 1, 2) + datetime.timedelta(seconds=step * draw.randrange(86400 // step))]
    while len(moments) < 10000:
        moments += [
            datetime.datetime(1900, 1, 3)
            + datetime.timedelta(days=draw.randrange(12780), seconds=step * draw.randrange(86400 // step))
        ]
    draw.shuffle(moments)
    if shape == "sas_days":
        return [f"{(moment.date() - datetime.date(1960, 1, 1)).days}" for moment in moments]
    if shape == "unix_minutes":
        return [f"{int((moment - datetime.datetime(1970, 1, 1)).total_seconds()) * 1000}" for moment in moments]
    return [f"{int((moment - datetime.datetime(1960, 1, 1)).total_seconds())}" for moment in moments]


@pytest.mark.parametrize(
    "shape",
    (
        "excel_moments", "excel_moments_packed", "excel_dates", "excel_1904_seconds", "sas_moments",
        "unix_days_to_9999", "sas_days_across", "sas_seconds_across",
    ),
)
def test_c5_both_writings_of_a_counted_tail_stop_short_of_the_days_its_counts_cannot_hold(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """The verification of the second review's item 2: the generator's strata and the validator's, one reach.

    Ten thousand Excel date-times and Excel dates from 1900 -- the
    date-times also packed into its first quarter, whose low boundary
    stands on 2 January, so the tail has room only because serial 2 is
    one instant of that day -- Excel 1904 seconds from 1904 and SAS
    seconds from 1900, a thousand Unix days of the last century before
    10000, and SAS days and SAS seconds whose low tail runs across 1
    January 1900 (`_across_1900`). Each tail's strata are drawn by the
    generator (`generation._date_layout`) and again by the validator
    (`validation._date_tail_windows`), both to the reach the counting
    system leaves (`date_counts.tail_reach`), and agree rank by rank;
    every place a tail rank can stand, nearest and furthest, is a count of
    the system naming a date -- no moment before Excel's first count, none
    on the instant serial 2 names, none on a wall's 1 January 1900 or 31
    December 9999 -- and where 1 January 1900 is an island, a system
    writing the days either side of it, the tail reaches past it, no
    stratum lies wholly on it and each place off it is no set-aside
    count. Red on 568b597 on the first six: its low tails stood before
    Excel's two first counts and on 1 January 1900, and its high tail on
    31 December 9999; red on 22e52f0 on the last two, whose reach stopped
    short of the island.
    """
    member, cells = _counted_near_the_holes(shape)
    path = _table(tmp_path, cells)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", member, "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-600:]
    described = contract.load_profile(str(tmp_path / "table-profile.json"))
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    floor = described.settings.small_cell_floor
    parsed = column.n_present - facts.n_unparsed
    layout = generation._date_layout(column, facts, parsed, floor, member)
    windows = validation._date_tail_windows(column, facts, floor, member)
    space = generation._ordinal_space(facts)
    unit = date_counts.DAY if space == "date" else date_counts.SECOND
    aside: "dict[int, int]" = {}
    for number in date_counts.declared_aside(member):
        aside[number] = 1
    # 1 January 1900 is an island of a low tail where the system writes the
    # days before it; every other stretch a count cannot hold is a wall.
    island = date_counts.TABLE[member].signed
    drawn = 0
    for side, plan in (("low", layout.low), ("high", layout.high)):
        assert plan is not None, side
        if plan.shape is None:
            # A tail publishing its values stands on them: present values
            # of the source, never on a day its counts cannot hold.
            assert side not in windows, side
            continue
        drawn = drawn + 1
        near, far = windows[side]
        assert list(near) == list(plan.near) and list(far) == list(plan.far), side
        for index in range(plan.rows):
            named: "list[str]" = []
            for distance in (plan.near[index], plan.far[index]):
                place = generation._tail_place(plan, distance)
                found = date_counts.count_of(member, place, unit)
                assert found is not None, (side, index, place)
                numerator, denominator = found
                moment = date_counts.moment_of(member, numerator, denominator, unit)
                assert moment == place, (side, index, place)
                day = date_counts.placeholder_day_named(moment, unit)
                named += [day]
                if day:
                    assert island and side == "low" and day == "1900-01-01", (side, index, place)
                else:
                    assert not date_counts.stands_aside(numerator, denominator, False, aside), (side, index, place)
            assert not (named[0] and named[0] == named[1]), (side, index, named)
        if shape.endswith("_across") and side == "low":
            # The tail reaches past the island, as the source's own does.
            first = generation._tail_place(plan, plan.near[0])
            assert first < parsing.days_from_civil(1900, 1, 1) * (86400 * date_counts.SECOND // unit), first
    assert drawn == 2


@pytest.mark.parametrize("which", ("end", "group"))
def test_c5_an_end_or_a_group_on_1_january_1900_steps_off_it_in_both_writings(
    tmp_path: pathlib.Path, which: str
) -> None:
    """The repair of the verification of the second review's item 2: a word-less rank on an island steps off it.

    A tail's end and its tie group each stand at one distance, so a
    stratum of one point: on 1 January 1900 -- an island of SAS days,
    which write the days either side of it -- no move inside it would
    leave the day, and a group spread over the units beside it would no
    longer be one group. So each steps off the island in the plan, inward
    to the day after it (`date_counts.off_the_islands`), and the
    validator's windows step it alike. A column of SAS days across the
    day (`_across_1900`) is described; its low tail is given fourteen
    ranks, a group of four, and a boundary as many days after 1 January
    as the shape puts its end, or its group, from the boundary. The
    generator's plan stands that rank off the island, a day nearer, and
    the validator's windows are its strata rank by rank. Red where the
    end and the group do not step (the group on the day, the end on it).
    """
    path = _table(tmp_path, _across_1900("sas_days"))
    member = "days-since-1960"
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", member, "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-600:]
    described = contract.load_profile(str(tmp_path / "table-profile.json"))
    column = described.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.low_tail is not None
    low = facts.low_tail
    assert low.values is None and low.mean_distance is not None and low.rms_distance is not None
    floor = described.settings.small_cell_floor
    shape = generation._tail_shape(14, low.mean_distance, low.rms_distance, floor, 10**9, False, True)
    assert shape.grouped < 14
    distance = shape.end if which == "end" else shape.group
    boundary = (datetime.date(1900, 1, 1) + datetime.timedelta(days=distance)).isoformat()
    moved = dataclasses.replace(facts, low_tail=dataclasses.replace(low, rows=14, boundary=boundary))
    moved_column = dataclasses.replace(column, facts=moved)
    parsed = column.n_present - facts.n_unparsed
    layout = generation._date_layout(moved_column, moved, parsed, floor, member)
    windows = validation._date_tail_windows(moved_column, moved, floor, member)
    plan = layout.low
    assert plan is not None and plan.shape is not None
    assert plan.islands == ((distance, distance),), plan.islands
    stood = plan.shape.end if which == "end" else plan.shape.group
    assert stood == distance - 1, (which, distance, stood)
    assert list(windows["low"][0]) == list(plan.near) and list(windows["low"][1]) == list(plan.far)


def test_c5_a_tail_across_1_january_1900_keeps_its_spread_and_no_cell_on_the_day(tmp_path: pathlib.Path) -> None:
    """The repair of the verification of the second review's item 2: a tail reaches past the day, its ranks off it.

    Three columns of ten thousand whose low tail runs across 1 January
    1900 in a system writing the days either side of it (`_across_1900`):
    SAS days with eight values in December 1899 and a boundary on 7
    January; SAS seconds and Unix milliseconds at the minute with five
    moments on the evening of 31 December and a crowd on 2 January. On
    seeds 0 to 2 every twin cell is a count naming a date -- none on 1
    January 1900, none set aside -- each column's twin holds cells before
    1900 as its source does, and twin and source are both at exit 0. Red
    on 22e52f0, whose reach stopped short of the day: no twin cell before
    1900, and the dense tail of SAS seconds piled onto one second and
    missing both counts of different values. Red on 568b597: cells on 1
    January 1900 in both dense columns.
    """
    columns = {
        "days": _across_1900("sas_days"),
        "seconds": _across_1900("sas_seconds"),
        "minutes": _across_1900("unix_minutes"),
    }
    members = {"days": "days-since-1960", "seconds": "seconds-since-1960", "minutes": "milliseconds-since-1970"}
    path = _table_of(tmp_path, columns)
    argv = ["profile", str(path), "--out-dir", str(tmp_path), "--replace"]
    for name in sorted(columns):
        argv += ["--date-count", name, members[name]]
    code, said = _exit_of(argv)
    assert code == 0, said[-600:]
    described = tmp_path / "table-profile.json"
    blocks = {block["name"]: block for block in json.loads(described.read_text(encoding="utf-8"))["columns"]}
    first_day = parsing.days_from_civil(1900, 1, 1)
    for seed in range(3):
        code, said = _exit_of(["generate", str(described), "--seed", f"{seed}", "--out-dir", str(tmp_path), "--replace"])
        assert code == 0, said[-600:]
        rows = list(csv.reader(io.StringIO((tmp_path / "table-twin.csv").read_text(encoding="utf-8"))))
        header = rows[0]
        for name in sorted(columns):
            member = members[name]
            assert blocks[name]["role"] == "datetime", name
            absent = blocks[name].get("missing_by_source") or {}
            aside: "dict[int, int]" = {}
            for number in date_counts.declared_aside(member):
                aside[number] = 1
            at = header.index(name)
            before = 0
            for row in rows[1:]:
                cell = row[at]
                if not cell or cell in absent:
                    continue
                written = date_counts.written_count(cell)
                assert written is not None, (seed, name, cell)
                numerator, denominator = date_counts.exact_value(written)
                moment = date_counts.moment_of(member, numerator, denominator, date_counts.SECOND)
                assert moment is not None and moment // 86400 != first_day, (seed, name, cell)
                assert not date_counts.stands_aside(numerator, denominator, False, aside), (seed, name, cell)
                before = before + (1 if moment // 86400 < first_day else 0)
            assert before >= 2, (seed, name, before)
        out = tmp_path / f"check-twin-{seed}"
        out.mkdir()
        assert _exit_of([
            "validate", str(described), "--twin", str(tmp_path / "table-twin.csv"), "--out-dir", str(out), "--replace",
        ])[0] == 0, seed
    out = tmp_path / "check-source"
    out.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(path), "--out-dir", str(out), "--replace"])[0] == 0


def test_c5_a_count_written_as_a_numeric_stand_in_is_the_date_it_names_on_both_sides(tmp_path: pathlib.Path) -> None:
    """A real date whose count is `-999`, `9999` or `-9999` stays a date when the source is checked.

    Found repairing the second review of landing R4, item 2. Under a
    declaration a count is read as the date it names before any
    judgement, so SAS day -999 (7 April 1957) and Excel serial 9999 (17
    May 1927) are dates, never stand-ins for "no value". The checker's
    recount asked them as stand-ins nothing publishes a verdict on, and
    where the counted reading had set any cell aside -- a count naming
    1 January 1900, which no published verdict accounts for either --
    it dropped them, and the source missed its own weekday census.
    """
    draw = random.Random(999)
    columns: "dict[str, list[str]]" = {"sas": [], "xl": []}
    for row in range(1000):
        sas = (datetime.date(1925, 1, 1) + datetime.timedelta(days=draw.randrange(25000)) - datetime.date(1960, 1, 1)).days
        xl = (datetime.date(1905, 1, 1) + datetime.timedelta(days=draw.randrange(25000)) - datetime.date(1899, 12, 30)).days
        columns["sas"] += [f"{(-999, 9999, -9999)[row % 3] if row < 9 else sas}"]
        columns["xl"] += [f"{9999 if row < 3 else xl}"]
    # ...and one count each column sets aside: 1 January 1900.
    columns["sas"][500] = "-21914"
    columns["xl"][500] = "1"
    came = _trip_of(tmp_path, columns, {"sas": "days-since-1960", "xl": "excel-1900"})
    assert came["profile"] == 0, came["said"]
    blocks = came["blocks"]
    assert isinstance(blocks, dict)
    for name in ("sas", "xl"):
        assert blocks[name]["role"] == "datetime" and blocks[name]["n_present"] == 999, name
    assert (came["generate"], came["twin"], came["source"]) == (0, 0, 0), came


def test_c5_a_table_of_one_counted_column_is_counted_in_rows(tmp_path: pathlib.Path) -> None:
    """The population census reads each count's date: one counted column is a table of rows."""
    shape = battery.BY_NAME["unix_s"]
    cells, _truth = battery.cells(shape, 150, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["block"]["n_present"] == 150


def test_c5_r_exponent_form_and_a_decimal_comma_round_trip(tmp_path: pathlib.Path) -> None:
    """Items 6 and 8: R's shorter form asked about undeclared, and both it and a comma for the point read and written back.

    Item 6 said Q3 never asked a column of milliseconds R wrote with an
    exponent on some cells (here about one in six). It is asked, offering
    the system that wrote it; with the exponent cells read as no count by
    the question's walk, it is not, and the round trip still holds.
    """
    draw = random.Random(6)
    cells: "list[str]" = []
    for _row in range(400):
        day = datetime.date(2016, 1, 1) + datetime.timedelta(days=draw.randrange(3653))
        milliseconds = (day - datetime.date(1970, 1, 1)).days * 86400000 + draw.choice((0, 0, 0, draw.randrange(86400) * 1000))
        form = date_counts.CountForm(0, True, 15, True, ".", None)
        cells += [date_counts.spelled_count(milliseconds, 1, form)]
    assert any("e+" in cell for cell in cells) and not all("e+" in cell for cell in cells)
    said = _q3(_block_of(tmp_path / "asked", cells))
    assert said is not None
    assert "milliseconds-since-1970" in [member for member, _first, _last in said.readings]
    trip = _trip(tmp_path / "r", cells, "milliseconds-since-1970")
    assert trip["block"]["count_form"]["exponent"] is True
    assert any("e+" in cell for cell in trip["twin"])
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    commas = [
        f"{45000 + draw.randrange(3000) + draw.randrange(86400) / 86400:.6f}".rstrip("0").rstrip(".").replace(".", ",")
        for _row in range(400)
    ]
    trip = _trip(tmp_path / "comma", commas, "excel-1900", "--decimal-comma", "seen")
    assert trip["block"]["count_form"]["mark"] == ","
    assert all("," in cell or cell.isdigit() for cell in trip["twin"])
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0


def test_c5_fifteen_figures_crossing_serial_ten_thousand_round_trip(tmp_path: pathlib.Path) -> None:
    """Item 7: `%.15g` writes one figure fewer after the point past serial 10,000."""
    shape = battery.BY_NAME["xl_dt15g"]
    cells = battery.ranged(shape, "births_1920", battery.ROWS, 0)
    assert any(len(cell.split(".")[0]) == 4 for cell in cells) and any(len(cell.split(".")[0]) == 5 for cell in cells)
    trip = _trip(tmp_path, cells, "excel-1900")
    form = trip["block"]["count_form"]
    assert form["significant"] == 15 and trip["block"]["time_precision"] == "second"
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in cells:
        written = date_counts.written_count(cell)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of("excel-1900", numerator, denominator, unit)
        assert moment is not None
        assert date_counts.written_for("excel-1900", moment, unit, facts.count_form) == cell


@pytest.mark.parametrize("name", sorted(battery.COARSE))
def test_c4_figures_no_unit_keeps_are_refused_and_the_rest_written_back(
    tmp_path: pathlib.Path, name: str
) -> None:
    """The review of landing R4, item 2: the reading unit keeps every figure the column wrote, or reads none.

    One and two figures of a day step by 2.4 hours and 14.4 minutes,
    tenths and hundredths of a second by a tenth and a hundredth, and four
    figures of a day of moments off the minute by 8.64 seconds: settled to
    a unit at least the step, a count loses its figures, and settled
    finer the twin's own cells are rounded onto the column's coarser grid
    as they are written -- the first build's twin of one figure missed its
    own description, and its Unix tenths came back as whole seconds. Such a
    column is not read as counted dates (NF115) and is twinned as the
    numbers it reads, both files at exit 0. Four figures of a day at
    whole minutes and five at whole seconds are kept: read as dates, every
    source cell written back as itself.
    """
    system, _write, kept = battery.COARSE[name]
    cells = battery.coarse(name, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, system)
    block = trip["block"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    if not kept:
        assert block["role"] != "datetime", name
        assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in block["remarks"])
        return
    assert block["role"] == "datetime" and block["count_form"] is not None
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in cells:
        written = date_counts.written_count(cell)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of(system, numerator, denominator, unit)
        assert moment is not None
        assert date_counts.written_for(system, moment, unit, facts.count_form) == cell


def test_c4_a_truncating_exporter_is_refused(tmp_path: pathlib.Path) -> None:
    """The second review of landing R4, item 6 (mutant K2b): a count is held within HALF its last figure.

    A thousand Excel date-times at whole seconds whose exporter CUT them
    to six figures instead of rounding: each count stands up to a whole
    last figure, 86 milliseconds, below its moment, so no unit keeps the
    column's figures -- Q3 offers no system and the declaration is refused
    (NF115), both files at exit 0. Held within a whole last figure, the
    column was read as dates and only 514 of its 1,000 cells were written
    back as themselves.
    """
    draw = random.Random(12)
    cells: "list[str]" = []
    for _row in range(1000):
        value = 45000 + draw.randrange(3000) + draw.randrange(86400) / 86400
        cells += [f"{int(value * 10**6) / 10**6:.6f}"]
    said = _q3(_block_of(tmp_path / "asked", cells))
    assert said is None or "excel-1900" not in [member for member, _first, _last in said.readings]
    trip = _trip(tmp_path / "declared", cells, "excel-1900")
    block = trip["block"]
    assert isinstance(block, dict) and block["role"] != "datetime"
    assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in block["remarks"])
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0


def test_c4_the_settled_unit_is_at_least_the_step(monkeypatch: pytest.MonkeyPatch, tmp_path: pathlib.Path) -> None:
    """The first build's minute floor (mutant M52), and a figures check that holds everything.

    Settled to the minute, one figure of a day reads exactly -- 0.1 of a
    day is 144 minutes -- and its twin, drawn at the minute and rounded to
    2.4 hours as it is written, missed its own description. Put back, the
    column is read as dates again; so is a column of Unix tenths where the
    figures check holds every count.
    """
    assert date_counts.settled_unit("excel-1900", 1) == date_counts.DAY
    assert date_counts.settled_unit("excel-1900", 4) == date_counts.MINUTE
    assert date_counts.settled_unit("excel-1900", 6) == date_counts.SECOND
    assert date_counts.settled_unit("excel-1900", 10) == date_counts.MILLISECOND
    assert date_counts.settled_unit("seconds-since-1970", 1) == date_counts.SECOND
    original = date_counts.settled_unit

    def minute_floor(member: str, places: int) -> int:
        found = date_counts.TABLE[member]
        if places > 0 and found.unit >= date_counts.DAY and not found.contacts and places < 4:
            return date_counts.MINUTE
        return original(member, places)

    monkeypatch.setattr(date_counts, "settled_unit", minute_floor)
    block = _block_of(tmp_path / "floor", battery.coarse("excel_1dp", battery.ROWS, 0), "excel-1900")
    assert block["role"] == "datetime"
    monkeypatch.undo()
    monkeypatch.setattr(date_counts, "held_by_its_moment", lambda *arguments: True)
    block = _block_of(tmp_path / "held", battery.coarse("unix_s_1dp", battery.ROWS, 0), "seconds-since-1970")
    assert block["role"] == "datetime"


def test_c4_the_contact_numbers_are_spread_over_the_rows(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The review of landing R4, item 8: each half of the twin holds the census's share of each contact number.

    Dealt in rank order down the rows, the first build's twin of 100,000
    rows held no contact number in its first half at all. At 10,000 rows
    each half of the twin's dated cells is within one point of the
    census's share, and with the first build's dealing it is not.
    """
    shape = battery.BY_NAME["epic_real"]
    cells, _truth = battery.cells(shape, 10000, 0)

    def halves_off(twin: "list[str]", census: "dict[str, int]") -> float:
        words = [date_counts.contact_word(date_counts.written_count(cell)) for cell in twin if cell]  # type: ignore[arg-type]
        total = sum(census.values())
        worst = 0.0
        for half in (words[: len(words) // 2], words[len(words) // 2 :]):
            for word, count in census.items():
                worst = max(worst, abs(half.count(word) / len(half) - count / total) * 100)
        return worst

    trip = _trip(tmp_path / "head", cells, shape.system)
    census = trip["block"]["count_form"]["contacts"]
    assert census is not None and len(census) >= 2
    assert halves_off(trip["twin"], census) <= 1.0
    _dealt_down_the_rows(monkeypatch)
    trip = _trip(tmp_path / "mutant", cells, shape.system)
    assert halves_off(trip["twin"], census) > 1.0


@pytest.mark.parametrize(
    ("writer", "name"),
    (
        ("repr", "xl_dt15g"), ("repr", "xl_dt6"), ("pandas_point_zero", "xl_date"),
        ("repr_microseconds", "unix_s"),
    ),
)
def test_c4_pandas_and_repr_spellings_round_trip(
    tmp_path: pathlib.Path, writer: str, name: str
) -> None:
    """`repr`'s shortest figures (mutant M47) and pandas' `45000.0` (mutant M49) written as their writer writes them.

    A column of Excel serials pandas wrote with `repr` is settled at the
    second or the minute its moments stand on, every source cell is
    written back as itself, and every twin cell is `repr`'s own spelling
    of its double -- not `%.17g`'s seventeen figures. A column of whole
    serials pandas wrote as `45000.0` keeps its one nought after the point
    in the twin, and the source meets its own form. Unix seconds Python
    wrote to the microsecond hold no figure at the unit fifteen figures
    carry and are settled at the next finer one, the microsecond (mutant
    M72: the first unit alone refused them). Undeclared, question Q3
    offers each column the system that wrote it: the figures check tries
    a system's units finest first and finds the one its reading holds at
    (mutant M76: the coarsest alone left the microseconds unasked).
    """
    shape = battery.BY_NAME[name]
    cells = battery.written_by(writer, shape, battery.ROWS, 0)
    said = _q3(_block_of(tmp_path / "asked", cells))
    assert said is not None and shape.system in [member for member, _first, _last in said.readings]
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    form = trip["block"]["count_form"]
    if writer.startswith("repr"):
        assert form["significant"] == 17
        wanted = ("subsecond",) if writer == "repr_microseconds" else ("second", "minute")
        assert trip["block"]["time_precision"] in wanted
        assert all(cell == repr(float(cell)) for cell in trip["twin"] if cell)
    else:
        assert form["places"] == 1 and form["trimmed"] is False
        assert all(cell.endswith(".0") for cell in trip["twin"] if cell)
    loaded = contract.load_profile(str(trip["described"]))
    facts = loaded.columns[0].facts
    assert isinstance(facts, contract.DatetimeFacts) and facts.count_form is not None
    unit = contract.counted_unit(facts)
    for cell in cells:
        written = date_counts.written_count(cell)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of(shape.system, numerator, denominator, unit)
        assert moment is not None
        assert date_counts.written_for(shape.system, moment, unit, facts.count_form) == cell


@pytest.mark.parametrize("figures,many", ((7, 1), (10, 1), (7, 10), (7, 11)))
def test_c4_a_cell_written_with_more_figures_is_a_stray(tmp_path: pathlib.Path, figures: int, many: int) -> None:
    """The second review of landing R4, item 5: cells exported with more figures than the rest.

    A thousand Excel date-times at whole seconds written `%.6f`, one or
    ten of them to seven or ten figures. The column's form, unit and
    figures check are its usual counts', and each stray is held to its
    own last figure: Q3 asks with the 1900 system, and declared, the
    column is read as dates at the second in six fixed figures, its twin
    and source each at exit 0. The twin writes each stray's moment in six
    figures, so the strays alone are not written back as themselves. On
    e9aa5fb one stray silenced Q3 and refused the declaration (NF115):
    the six-figure cells were held to the seven-figure form's tolerance.
    ELEVEN in a thousand are more than one in a hundred, no stray: the
    form is then one of seven figures, which the six-figure cells do not
    meet, and the declaration is refused as before.
    """
    draw = random.Random(11)
    moments = [45000 + draw.randrange(3000) + draw.randrange(86400) / 86400 for _row in range(1000)]
    cells = [f"{value:.6f}" for value in moments]
    strays = [500 + 37 * place for place in range(many)]
    for place in strays:
        cells[place] = f"{moments[place]:.{figures}f}"
    said = _q3(_block_of(tmp_path / "asked", cells))
    offered = [] if said is None else [member for member, _first, _last in said.readings]
    block = _block_of(tmp_path / "declared-alone", cells, "excel-1900")
    if many > 10:
        assert "excel-1900" not in offered and block["role"] != "datetime", (offered, block["role"])
        return
    assert "excel-1900" in offered, offered
    trip = _trip(tmp_path / "declared", cells, "excel-1900")
    described = trip["block"]
    assert isinstance(described, dict) and described["role"] == "datetime"
    assert described["time_precision"] == "second"
    assert described["count_form"]["places"] == 6 and not described["count_form"]["trimmed"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    form = date_counts.CountForm(6, False, None, False, ".", None)
    moved: "list[int]" = []
    for place in range(len(cells)):
        written = date_counts.written_count(cells[place])
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        moment = date_counts.moment_of("excel-1900", numerator, denominator, date_counts.SECOND)
        assert moment is not None
        if date_counts.written_for("excel-1900", moment, date_counts.SECOND, form) != cells[place]:
            moved += [place]
    assert moved == strays
    twin = trip["twin"]
    assert isinstance(twin, list) and all(len(f"{cell}".split(".")[1]) == 6 for cell in twin if cell)
    # THE CHECKER LETS AS MANY STAND, AND NO MORE: the twin with ten of its
    # cells written to seven figures passes, with eleven it misses.
    for finer, code in ((10, 0), (11, 3)):
        changed = list(twin)
        for place in range(finer):
            changed[100 + 13 * place] = f"{changed[100 + 13 * place]}0"
        folder = tmp_path / f"finer-{finer}"
        folder.mkdir()
        path = folder / "changed.csv"
        path.write_text("seen\n" + "\n".join(changed) + "\n", encoding="utf-8", newline="")
        out = folder / "check"
        out.mkdir()
        assert _exit_of(["validate", str(trip["described"]), "--twin", str(path), "--out-dir", str(out), "--replace"])[0] == code, finer


def test_c4_a_stray_is_held_to_its_own_last_figure(tmp_path: pathlib.Path) -> None:
    """The second review of landing R4, item 5: a stray's figures are kept, or the column is not read.

    One cell of a thousand `%.6f` date-times at whole seconds written to
    seven figures for a moment 0.02 seconds past its second: its own last
    figure, 8.6 milliseconds, says the moment is not at the second the
    column is read at, so no unit keeps every figure the column wrote --
    Q3 offers no system, and the declaration is refused (NF115). Held to
    the six-figure form instead, 86 milliseconds, the cell would be read
    as its second and written back without its seventh figure.
    """
    draw = random.Random(11)
    moments = [45000 + draw.randrange(3000) + draw.randrange(86400) / 86400 for _row in range(1000)]
    cells = [f"{value:.6f}" for value in moments]
    cells[500] = f"{moments[500] + 0.02 / 86400:.7f}"
    said = _q3(_block_of(tmp_path / "asked", cells))
    assert said is None or "excel-1900" not in [member for member, _first, _last in said.readings]
    assert _block_of(tmp_path / "declared", cells, "excel-1900")["role"] != "datetime"
    cells[500] = f"{moments[500]:.7f}"
    assert _block_of(tmp_path / "whole-second", cells, "excel-1900")["role"] == "datetime"


def _time_carried_by_the_few(maker: str, writer: str, share: float) -> "list[str]":
    """A thousand Excel date-times whose few longer counts are the ones carrying the time of day.

    `quarter`: most at 00, 06, 12 or 18 o'clock (`45123.25`), ``share`` of
    them at other whole hours; `midnight`: most at midnight, as date-only
    entries, ``share`` at whole minutes. Written `%.15g`, as Excel's
    General format and R write them, or `repr`, as pandas does -- so the
    usual counts write two figures after the point, one or none, and the
    few others ten or twelve.
    """
    draw = random.Random(f"carried:{maker}:{writer}:{share}")
    many = round(1000 * share)
    cells: "list[str]" = []
    for row in range(1000):
        day = 45000 + draw.randrange(1500)
        if maker == "quarter":
            hours = (1, 2, 3, 4, 5, 7, 8, 9, 10, 11, 13, 14) if row < many else (0, 6, 12, 18)
            value = day + draw.choice(hours) / 24
        else:
            value = day + (draw.randrange(1, 1440) if row < many else 0) / 1440
        cells += ["%.15g" % value if writer == "g15" else repr(value)]
    draw.shuffle(cells)
    return cells


def test_c4_longer_counts_carrying_the_time_of_day_are_read_with_the_rest(tmp_path: pathlib.Path) -> None:
    """The verification of the second review's item 5: every count is read first, strays only where that fails.

    Eight columns of a thousand Excel date-times, written `%.15g` or
    `repr`, mostly at six-hour steps or at midnight with half or one
    percent at other hours or minutes. The longer counts are the ones
    carrying the time: reading by every count, the column settles at the
    millisecond and is written at the minute, as e9aa5fb read all eight.
    The first repair set the longer counts aside as strays FIRST, so the
    usual two figures or none settled at the day, the strays named times
    a day cannot hold, Q3 asked none of the eight and each declaration
    was refused (NF115) -- red on 568b597. Each is asked with Excel's
    1900 system, read at the minute in its own form, every source cell
    that form's writing of its moment, and its twin and source both pass.
    """
    columns: "dict[str, list[str]]" = {}
    for maker in ("quarter", "midnight"):
        for writer in ("g15", "repr"):
            for share in (0.005, 0.01):
                columns[f"{maker}_{writer}_{round(share * 1000)}"] = _time_carried_by_the_few(maker, writer, share)
    for name in sorted(columns):
        said = _q3(_block_of(tmp_path / f"asked-{name}", columns[name]))
        offered = [] if said is None else [member for member, _first, _last in said.readings]
        assert "excel-1900" in offered, (name, offered)
    came = _trip_of(tmp_path / "declared", columns, {name: "excel-1900" for name in columns})
    assert came["profile"] == 0, came["said"]
    blocks = came["blocks"]
    assert isinstance(blocks, dict)
    for name in sorted(columns):
        block = blocks[name]
        assert block["role"] == "datetime" and block["time_precision"] == "minute", (name, block["role"])
        form = block["count_form"]
        longest = max(len(cell.split(".")[1]) if "." in cell else 0 for cell in columns[name])
        assert form["places"] == longest and form["trimmed"], (name, form)
        shaped = date_counts.CountForm(
            form["places"], form["trimmed"], form["significant"], form["exponent"], form["mark"], None
        )
        for cell in columns[name]:
            written = date_counts.written_count(cell)
            assert written is not None
            numerator, denominator = date_counts.exact_value(written)
            moment = date_counts.moment_of("excel-1900", numerator, denominator, date_counts.MINUTE)
            assert moment is not None
            assert date_counts.written_for("excel-1900", moment, date_counts.MINUTE, shaped) == cell, (name, cell)
    assert (came["generate"], came["twin"], came["source"]) == (0, 0, 0), came


def test_c5_a_placeholder_count_is_set_aside_whole_or_not(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant M12: Excel's count for 31 December 9999, and pandas' `2` for 1 January 1900.

    Each is counted as no value and written back as written: the twin
    holds as many of each spelling as the source, no ISO date stands in a
    column of numbers, and both files meet the description. With no
    placeholder day set aside the date role's own judgement withholds
    them under the ISO text it read, and the twin writes that text into
    the column.
    """
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    for place in range(0, 1000, 50):
        cells[place] = "2958465"
    for place in range(25, 1000, 50):
        cells[place] = "2"
    trip = _trip(tmp_path / "head", cells, shape.system)
    assert trip["block"]["missing_by_source"] == {"2": 20, "2958465": 20}
    assert trip["twin"].count("2958465") == 20 and trip["twin"].count("2") == 20
    assert not [cell for cell in trip["twin"] if "-" in cell]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    # ...AND NOT WHOLE: six in the morning of either day, among date-times
    # written to four figures, is set aside by the one reading the profiler
    # and question Q3 share (`date_counts.settled_reading`; mutant M73 kept
    # its moment, and the twin wrote `9999-12-31 06:00` into the column).
    timed = battery.coarse("excel_4dp_minutes", battery.ROWS, 0)
    for place in range(0, 1000, 50):
        timed[place] = "2958465.2500"
    for place in range(25, 1000, 50):
        timed[place] = "1.2500"
    trip = _trip(tmp_path / "timed", timed, "excel-1900")
    assert trip["block"]["missing_by_source"] == {"1.2500": 20, "2958465.2500": 20}
    assert trip["twin"].count("2958465.2500") == 20 and trip["twin"].count("1.2500") == 20
    assert not [cell for cell in trip["twin"] if "-" in cell]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    monkeypatch.setattr(date_counts, "declared_aside", lambda member: ())
    monkeypatch.setattr(date_counts, "placeholder_day_named", lambda moment, unit: "")
    path = _table(tmp_path / "mutant", cells)
    code, said = _exit_of(["profile", str(path), "--date-count", "seen", "excel-1900", "--out-dir", str(tmp_path / "mutant"), "--replace"])
    assert code == 0, said[-500:]
    block = json.loads((tmp_path / "mutant" / "table-profile.json").read_text(encoding="utf-8"))["columns"][0]
    assert block["missing_by_source"] != {"2": 20, "2958465": 20}


@pytest.mark.parametrize(
    "case",
    ("minutes_ten_9999_quarter", "minutes_ten_1900_quarter", "dates_ten_serial_2", "dates_ten_serial_1", "dates_ten_9999"),
)
def test_c5_ten_pooled_placeholder_counts_leave_both_files_whole(tmp_path: pathlib.Path, case: str) -> None:
    """The second review of landing R4, item 6 (mutants K2j and K2k): placeholders fewer than the line.

    Ten cells of a thousand naming a placeholder day -- `2958465.2500` or
    `1.2500` among Excel moments at whole minutes written to four figures,
    or `2`, `1` or `2958465` among whole Excel dates -- are set aside, and
    ten are fewer than the line, so they are pooled as withheld and the
    twin writes them empty. Both files are at exit 0: the reading the
    generator and the checker share sets each aside as the profiler did.
    A read-back keeping a placeholder day's moment (K2j) read the quarter
    days as dates of 9999 and 1900, and one reading a declared-aside whole
    count (K2k) read `2` as 2 January 1900, each in the source's tails,
    which then missed its own description.
    """
    draw = random.Random(13)
    minutes = [f"{45000 + draw.randrange(3000) + draw.randrange(1440) / 1440:.4f}" for _row in range(1000)]
    dates = [f"{42500 + draw.randrange(3000)}" for _row in range(1000)]
    base, word = {
        "minutes_ten_9999_quarter": (minutes, "2958465.2500"),
        "minutes_ten_1900_quarter": (minutes, "1.2500"),
        "dates_ten_serial_2": (dates, "2"),
        "dates_ten_serial_1": (dates, "1"),
        "dates_ten_9999": (dates, "2958465"),
    }[case]
    cells = list(base)
    for place in range(10):
        cells[13 + 37 * place] = word
    trip = _trip(tmp_path, cells, "excel-1900")
    block = trip["block"]
    assert isinstance(block, dict) and block["role"] == "datetime"
    assert block["missing_by_class"].get(parsing.MISSING_WITHHELD) == 10, block["missing_by_class"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    assert trip["twin"].count(word) == 0  # type: ignore[union-attr]


def test_c5_keep_value_does_not_reach_a_declared_columns_placeholder(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant M40: `--keep-value 2958465` beside `--date-count` leaves the count set aside.

    The first build rescued it, read it as 31 December 9999, and the date
    role withheld that day under its ISO text: the twin wrote
    `9999-12-31` twenty times into a column of numbers and the source
    missed its own description. A number kept that way is no word of the
    vocabulary the settings record, so the checker could not keep it too.
    """
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    for place in range(0, 1000, 50):
        cells[place] = "2958465"
    trip = _trip(tmp_path / "head", cells, shape.system, "--keep-value", "2958465")
    assert trip["block"]["missing_by_source"] == {"2958465": 20}
    assert trip["twin"].count("2958465") == 20 and "9999-12-31" not in trip["twin"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0
    original = date_counts.declared_aside
    monkeypatch.setattr(
        date_counts, "declared_aside", lambda member: tuple(n for n in original(member) if n != 2958465)
    )
    monkeypatch.setattr(date_counts, "placeholder_day_named", lambda moment, unit: "")
    trip = _trip(tmp_path / "mutant", cells, shape.system, "--keep-value", "2958465")
    assert trip["real_exit"] == 3


def test_c5_a_declaration_reading_two_dates_decides_nothing(tmp_path: pathlib.Path) -> None:
    """Mutant M19: two different serials are read as dates, and the date rule does not take two values.

    The column is then read as if nothing had been declared and says so
    (NF115); without that the first build left a column of two dates on
    another role, and `generate` and `validate` stopped.
    """
    cells = ["45000" if row % 2 else "45001" for row in range(battery.ROWS)]
    trip = _trip(tmp_path, cells, "excel-1900")
    assert trip["block"]["role"] != "datetime"
    assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in trip["block"]["remarks"])
    assert sorted(set(trip["twin"])) == ["45000", "45001"]
    assert trip["twin_exit"] == 0 and trip["real_exit"] == 0


def test_c5_the_census_of_contact_numbers_is_held_exactly(tmp_path: pathlib.Path) -> None:
    """Mutant M33: a twin of Epic days whose census of contact numbers is another misses `form.contacts`.

    Each `02` written as `01`: every cell is still in the published form
    and names the same day, and the census the twin's own description
    counts -- `01` and `(none)` -- is not the one published, so only the
    census check can see it. Written with no contact number at all the
    twin publishes no census, which a vacuous check of the census would
    miss as well; the clause asks the census beside one.
    """
    shape = battery.BY_NAME["epic_real"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    trip = _trip(tmp_path, cells, shape.system)
    assert trip["twin_exit"] == 0
    census = trip["block"]["count_form"]["contacts"]
    assert census is not None and "02" in census
    merged = tmp_path / "merged"
    assert _rewritten(trip, merged, lambda cell: cell[:-3] + ".01" if cell.endswith(".02") else cell) == 3
    report = "\n".join(
        path.read_text(encoding="utf-8") for path in sorted((merged / "check-changed").glob("*.txt"))
    )
    assert "form.contacts" in report and "MISSED" in report


@pytest.mark.parametrize("noisy", (137, 5))
def test_c5_an_epic_day_with_a_binary64_tail_is_no_count(tmp_path: pathlib.Path, noisy: int) -> None:
    """The review of landing R4, item 3: `65053.010000000002` is a day and a binary64's tail.

    An Epic `*_DATE_REAL` exported with seventeen significant figures
    stopped `profile` with an internal fault once declared. Such a cell is
    no count: it stands to the date role's own line, so a column of them
    is read as it reads without the declaration and says so (NF115), and
    a column of five among a thousand is read as dates with five cells it
    could not read. Question Q3 does not offer the 1840 system for it.
    """
    shape = battery.BY_NAME["epic_real"]
    cells, truth = battery.cells(shape, battery.ROWS, 0)
    for place in range(noisy):
        day = int(battery.count_of(shape.system, truth[place * 7]))
        cells[place * 7] = f"{day + 0.01:.17g}"
    assert sum(len(cell.split(".")[1]) > 9 for cell in cells if "." in cell) == noisy
    trip = _trip(tmp_path, cells, shape.system)
    if noisy > 10:
        assert trip["block"]["role"] != "datetime"
        assert any(contract.COUNTED_NOT_READ_MARK in remark for remark in trip["block"]["remarks"])
        assert trip["twin_exit"] == 0
        said = _q3(_block_of(tmp_path / "asked", cells))
        assert said is None or "days-since-1840" not in [m for m, _f, _l in said.readings]
    else:
        # Read as dates beside five cells the date role could not read, which
        # the source meets. (Its twin writes those five as text stand-ins, as
        # every column of dates does with cells that are numbers, and so
        # misses `n_numeric` -- method G10.4's, not this landing's.)
        assert trip["block"]["role"] == "datetime" and trip["block"]["n_unparsed"] == noisy
        assert trip["real_exit"] == 0


# -- C6: NF51's place -----------------------------------------------------


def test_c6_a_column_of_unix_seconds_carries_q3s_words_and_no_nf51(tmp_path: pathlib.Path) -> None:
    shape = battery.BY_NAME["unix_s"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    path = _table(tmp_path, cells)
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    forms = [remark.form for remark in document["columns"][0]["remarks"]]
    assert taxonomy.REMARK_EPOCH_BAND not in forms
    assert taxonomy.REMARK_NUMBERS_COULD_BE_DATES in forms
    assert forms.count(taxonomy.REMARK_READ_AS_COUNTED_DATES) == 2
    said = " ".join(document["columns"][0]["remarks"])
    assert "changes nothing about your twin" not in said
    assert "run from" not in said or "runs from 2016 to 2025" in said


def test_c6_the_years_are_the_published_rungs_said_another_way(tmp_path: pathlib.Path) -> None:
    """NF114 quotes the block's own rungs; the loader refuses other years.

    Twenty `0` cells among a thousand SAS days are the published low end.
    Each system's years are those of the outermost published rung that is
    a date of the column (`taxonomy.counted_edge_years`), and a description
    naming other years -- a year off, or the first build's, read off the
    heaped `0` as 1960 -- is refused (the review of landing R4, item 1).
    """
    shape = battery.BY_NAME["sas_days"]
    cells, _truth = battery.cells(shape, battery.ROWS, 0)
    block = _block_of(tmp_path, battery.heaped(shape, cells, "zero", 0.02))
    edges = taxonomy.published_ends(block)
    assert edges is not None and edges[0] == 0.0
    seen = 0
    for remark in block["remarks"]:
        if remark.form != taxonomy.REMARK_READ_AS_COUNTED_DATES:
            continue
        member = remark.arguments[0]
        years = taxonomy.counted_edge_years(block, member)
        assert years is not None and remark.arguments[1:] == years
        profile._counted_years_quote_the_published_edges(remark.arguments, block)
        first_build = (date_counts.years_of(member, edges[0]), date_counts.years_of(member, edges[1]))
        assert first_build != years
        for wrong in ((member,) + first_build, (member, years[0] - 1, years[1])):
            with pytest.raises(Exception):
                profile._counted_years_quote_the_published_edges(wrong, block)
        seen += 1
    assert seen >= 2


def test_c6_the_loader_walks_past_every_heap_the_remarks_name(tmp_path: pathlib.Path) -> None:
    """The second review of landing R4, item 3, as the loader asks it.

    Twenty cells of Excel's 31 December 9999 among ten thousand serials:
    NF113 names `9999-12-31`, and the heaps the walk passes are that word's
    count in every system an NF114 names (`date_counts.heap_counts`). Read
    as Epic days, the heap is no date of the column: the walk passes it,
    and the loader, reading the words and the systems from the remarks,
    finds the same years. The walk that knew only the system's own
    set-aside numbers read it as 9941, and that sentence is refused.
    """
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, 10000, 0)
    block = _block_of(tmp_path, battery.heaped(shape, cells, "hi_sentinel", 0.002))
    said = _q3(block)
    assert said is not None and "9999-12-31" in said.aside
    members = tuple(member for member, _first, _last in said.readings)
    assert "days-since-1840" in members
    heaps = date_counts.heap_counts(("9999-12-31",), members)
    assert 2958465.0 in heaps
    for remark in block["remarks"]:
        if remark.form != taxonomy.REMARK_READ_AS_COUNTED_DATES:
            continue
        member = remark.arguments[0]
        assert remark.arguments[1:] == taxonomy.counted_edge_years(block, member, heaps)
        profile._counted_years_quote_the_published_edges(remark.arguments, block)
        if member != "days-since-1840":
            continue
        own_alone = taxonomy.counted_edge_years(block, member)
        assert own_alone is not None and own_alone[1] == 9941 and remark.arguments[2] < 2000
        with pytest.raises(Exception):
            profile._counted_years_quote_the_published_edges((member,) + own_alone, block)


# -- C7: a workbook --------------------------------------------------------


def test_c7_a_workbooks_serials_stored_as_numbers_come_back_as_number_cells(tmp_path: pathlib.Path) -> None:
    from tests import crosscheck

    openpyxl = crosscheck.fixture_writer()
    shape = battery.BY_NAME["xl_date"]
    cells, _truth = battery.cells(shape, 300, 0)
    book = openpyxl.Workbook()
    sheet = book.active
    sheet.title = "Data"
    sheet.cell(row=1, column=1, value="seen")
    for row, cell in enumerate(cells, start=2):
        sheet.cell(row=row, column=1, value=int(cell))
    table = tmp_path / "table.xlsx"
    held = io.BytesIO()
    book.save(held)
    table.write_bytes(held.getvalue())
    code, said = _exit_of(["profile", str(table), "--date-count", "seen", "excel-1900", "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-600:]
    described = tmp_path / "table-profile.json"
    assert json.loads(described.read_text(encoding="utf-8"))["columns"][0]["role"] == "datetime"
    code, said = _exit_of(["generate", str(described), "--seed", "0", "--out-dir", str(tmp_path), "--replace"])
    assert code == 0, said[-600:]
    twin = tmp_path / "table-twin.xlsx"
    read = crosscheck.reader().load_workbook(twin).worksheets[0]
    values = [row[0].value for row in read.iter_rows(min_row=2, max_col=1)]
    assert values and all(isinstance(value, (int, float)) and not isinstance(value, bool) for value in values)
    out = tmp_path / "check"
    out.mkdir()
    assert _exit_of(["validate", str(described), "--twin", str(twin), "--out-dir", str(out), "--replace"])[0] == 0


# -- the loader's own words ------------------------------------------------


def test_the_loaders_mark_is_the_rendered_sentences() -> None:
    """CD1 reads NF115 by one phrase, a second spelling of it; held to the rendered form."""
    for member in date_counts.MEMBERS:
        assert contract.COUNTED_NOT_READ_MARK in taxonomy.rendered(
            taxonomy.REMARK_COUNTED_DATES_NOT_READ, (member,)
        )


def test_every_member_has_a_terminal_key() -> None:
    from synthtwin import cli

    keys = {cli._KEY_OF[member] for member in date_counts.MEMBERS}
    assert len(keys) == 12
    for member in date_counts.MEMBERS:
        assert cli._ANSWER_KEYS[cli._KEY_OF[member]] == member


@pytest.mark.parametrize("member", date_counts.MEMBERS)
def test_every_member_reads_and_writes_its_own_counts(member: str) -> None:
    """Every member, at its own unit: a moment written as its count reads back as itself."""
    found = date_counts.TABLE[member]
    unit = found.unit if found.unit < date_counts.DAY else date_counts.DAY
    form = date_counts.CountForm(0, False, None, False, ".", None)
    for day in (parsing.days_from_civil(1950, 6, 1), parsing.days_from_civil(2024, 2, 29)):
        moment = day * (date_counts.DAY // unit) + (7 if unit < date_counts.DAY else 0)
        text = date_counts.written_for(member, moment, unit, form)
        assert text is not None
        written = date_counts.written_count(text)
        assert written is not None
        numerator, denominator = date_counts.exact_value(written)
        assert date_counts.moment_of(member, numerator, denominator, unit) == moment, (member, text)
