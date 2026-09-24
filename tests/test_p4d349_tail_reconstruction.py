"""The fix pass of stage 3: a tail that would be read back says less.

STAGE 3 GOT ONE ADVERSARIAL ROUND AND IT RETURNED REJECT ON ALL FOUR
PASSES. Seven of the items it raised are this file's subject, and every
one of them is built here from the round's own reproduction -- the table
it names, at the floor it names, described, generated and checked.

1. **EXACT RECONSTRUCTION FROM A PUBLISHED TAIL** (numeric item 1, dates
   item 2). The integers `0` to `1100`, once each, published a low
   boundary of `11` and a high boundary of `1089`, eleven rows a side, a
   mean distance of `6` and a root-mean-square of root-46, with
   `percentiles.min` and `percentiles.max` null -- beside the column's own
   remark that every value in it is different. Eleven DIFFERENT whole
   distances summing to 66 can only be 1 to 11, because 66 is the least
   eleven different whole numbers can sum to, so all twenty-two withheld
   values came back exactly. 240 consecutive dates and 240 unique minutes
   did the same.
2. **THE SECOND LISTING ROAD PUBLISHED SINGLETONS** (numeric item 1's
   second half, dates item 3). `list(range(1089)) + [1089] * 11 + [1100]`
   published the high-tail values `[1089, 1100]`, and ONE row holds 1100;
   ten cells at `06:58` beside one at `06:59` published `06:59`.
3. **THE CHECKER LEAKED WHAT THE DESCRIPTION WITHHELD**, three ways: a
   quality report printed a measurement over ONE cell of the checked file
   (dates item 1); the root-mean-square distance certified a published
   minimum it cannot (numeric item 6); and an overflowing moment window
   skipped the exact listed-values check beside it (numeric item 7).
4. **THE SUMMARY CONTRADICTED ITSELF** (numeric item 11): "the 12
   smallest values are not published", three lines above two of them.

THE RED CHECKS, each measured by withdrawing the rule in place rather
than by asserting that a guard exists:

* `taxonomy._tail_pinned` forced False -- the whole fail-closed half,
  asked through the tail-leak driver's own back-solve;
* the tie the back-solve used to assume, asked directly of the eighteen
  consecutive distances it could not reach;
* `parsing.tail_may_list` forced open -- the listing rule, which is the
  only road to a named value now;
* `validation._finite_window` forced False -- the exact listed-values
  check, which must stand whether or not a window can be drawn;
* the old endpoint arithmetic, computed here beside the new verdict, so
  the test says what the repair changed rather than that it happened.

Nothing here is copied from any output: every expected number is worked
out from the rule in the assertion that uses it.
"""

from __future__ import annotations

import datetime
import importlib.util
import json
import math
import pathlib

import pytest

import fixtures
import kpi_rules
import kpi_shapes
from synthtwin import (
    contract,
    parsing,
    profile,
    reading,
    summary,
    taxonomy,
    validation,
)

FLOOR = 11

# The boundary percent of a 1,101-value column at a floor of eleven, and
# the rows it leaves beyond itself, both from the rule and not from the
# producer: the smallest whole percent whose type-7 reading leaves at
# least `max(floor, 3)` values outside it.
CONSECUTIVE = 1101


def _one_column(name: str, cells: "list[str]") -> str:
    return f"{name}\n" + "\n".join(cells) + "\n"


def _described(folder: pathlib.Path, name: str, cells: "list[str]", floor: int = FLOOR):
    """One column through the whole product path at ``floor``."""
    return kpi_shapes.describe(folder / name, name, _one_column("value", cells), floor)


def _driver() -> object:
    """The tail-leak driver, loaded as a module.

    THE BACK-SOLVE IS NOT WRITTEN TWICE. `tools/measurements/kpi_stage3_tail_leak.py`
    already holds the walk a reader would make with a tail's published
    rows and two distances, with its own budget and its own permissive
    default; this file asks that walk rather than growing a second one
    that could disagree with it.
    """
    spec = importlib.util.spec_from_file_location(
        "kpi_stage3_tail_leak_for_p4d349",
        kpi_rules.MEASUREMENTS / "kpi_stage3_tail_leak.py",
    )
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _consecutive_dates(count: int) -> "list[str]":
    first = datetime.date(2020, 1, 1)
    return [
        (first + datetime.timedelta(days=step)).isoformat()
        for step in range(count)
    ]


def _consecutive_minutes(count: int) -> "list[str]":
    return ["%02d:%02d" % divmod(7 * 60 + step, 60) for step in range(count)]


def _settles(block: "dict", driver: object, apart: bool) -> int:
    """How many of one block's tails the published facts settle to ONE answer."""
    settled = 0
    if isinstance(block.get("tails"), dict):
        pinned, _room, _unsearched = driver._numeric_pinned(block, FLOOR, apart)
        settled += pinned
    if block.get("low_tail") is not None:
        pinned, _room, _unsearched = driver._pinned_and_room(block, FLOOR)
        settled += pinned
    return settled


# -- 1. the exact reconstruction -----------------------------------------


def test_the_least_sum_of_eleven_different_whole_numbers_is_the_whole_attack() -> None:
    """The arithmetic the round ran, stated before any table is built.

    Eleven DIFFERENT whole distances of one or more sum to at least
    `1 + 2 + ... + 11 = 66`, so a tail of eleven rows whose published mean
    distance is exactly 6 has distances summing to exactly that least sum
    and can hold no other multiset. That is the whole of the attack, and
    the rest of this file is the product being held to it.
    """
    assert sum(range(1, 12)) == 66
    assert 11 * 6 == 66
    assert sum(value * value for value in range(1, 12)) == 506
    assert math.isclose(506 / 11, 46.0)


@pytest.mark.parametrize(
    "name,cells",
    [
        ("integers", [str(value) for value in range(CONSECUTIVE)]),
        ("tenths", [f"{value / 10.0:.1f}" for value in range(CONSECUTIVE)]),
        ("dates", _consecutive_dates(240)),
        ("minutes", _consecutive_minutes(240)),
    ],
)
def test_a_column_whose_pair_would_be_read_back_publishes_neither_distance(
    tmp_path: pathlib.Path, name: str, cells: "list[str]"
) -> None:
    """Every tail of the round's own four columns publishes neither distance.

    Each of these columns steps one grid unit at a time and publishes that
    every value in it is different, so each tail's distances are the least
    multiset of different whole numbers its row count allows -- one answer
    and no other. The tail's boundary and its row count stand; both
    distances and any list of values are null.
    """
    described = _described(tmp_path, name, cells)
    block = described.document["columns"][0]
    sides = 0
    for key, tails in (("tails", block.get("tails")), ("", None)):
        if isinstance(tails, dict):
            for side in ("low", "high"):
                one = tails[side]
                assert isinstance(one, dict)
                assert one["mean_distance"] is None, f"{name} {side}"
                assert one["rms_distance"] is None, f"{name} {side}"
                assert not one["values"], f"{name} {side}"
                assert one["rows"] >= parsing.tail_units(FLOOR)
                sides += 1
    for key in ("low_tail", "high_tail"):
        one = block[key] if key in block else None
        if isinstance(one, dict):
            assert one["mean_distance"] is None, f"{name} {key}"
            assert one["rms_distance"] is None, f"{name} {key}"
            assert one["values"] is None, f"{name} {key}"
            assert one["rows"] >= FLOOR
            sides += 1
    assert sides == 2, f"{name}: both sides of the column must be asked"


@pytest.mark.parametrize(
    "name,cells",
    [
        ("integers", [str(value) for value in range(CONSECUTIVE)]),
        ("dates", _consecutive_dates(240)),
        ("minutes", _consecutive_minutes(240)),
    ],
)
def test_no_tail_of_those_columns_is_settled_by_the_whole_description(
    tmp_path: pathlib.Path, name: str, cells: "list[str]"
) -> None:
    """The reader's own walk, with every fact the description publishes."""
    driver = _driver()
    described = _described(tmp_path, name, cells)
    block = described.document["columns"][0]
    assert _settles(block, driver, True) == 0


def test_the_pair_put_back_is_settled_and_the_walk_says_so(
    tmp_path: pathlib.Path,
) -> None:
    """RED CHECK: `_tail_pinned` forced False, and the leak comes back.

    With the producer's own back-solve withdrawn, the integer column
    publishes its two distances again -- and the driver's walk, holding
    the column's own "every value different" remark, settles BOTH sides
    to exactly one multiset. Without the remark it settles neither, which
    is the measurement that says the remark is what does it.
    """
    driver = _driver()
    cells = [str(value) for value in range(CONSECUTIVE)]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            taxonomy,
            "_tail_pinned",
            lambda distances, floor, edge, distinct, least=1: False,
        )
        described = _described(tmp_path, "unguarded", cells)
    block = described.document["columns"][0]
    tails = block["tails"]
    assert isinstance(tails, dict)
    for side in ("low", "high"):
        assert tails[side]["mean_distance"] == 6.0, (
            "the guard was withdrawn and the pair did not come back, so "
            "this red check proves nothing"
        )
    assert _settles(block, driver, True) == 2
    assert _settles(block, driver, False) == 0


def test_the_back_solve_reaches_a_widened_tail_of_different_distances() -> None:
    """RED CHECK: the tie the back-solve used to assume, asked directly.

    It assumed that a tail wider than the floor is wider BECAUSE its
    innermost `rows - floor + 1` cells are tied, which held while a
    boundary stood where `tail_ranks` put it and stopped holding when a
    boundary learned to move inward. The cost was not looseness but
    BLINDNESS: eighteen consecutive distances break the assumed tie, so
    the search could not reach the real multiset, found its witness at
    another largest distance and answered NOT PINNED.

    Eighteen different whole distances of one or more sum to at least
    `18 * 19 / 2 = 171`, and these do, so the answer is PINNED at every
    width.
    """
    assert sum(range(1, 19)) == 171
    for size in (11, 18, 19):
        distances = list(range(1, size + 1))
        assert sum(distances) == size * (size + 1) // 2
        assert taxonomy._tail_pinned(distances, FLOOR, 100000, True), (
            f"{size} consecutive distances are one multiset and the "
            f"back-solve did not see it"
        )


# -- 2. the withdrawn second listing road --------------------------------


def test_a_tail_the_rule_refuses_names_nothing_however_settled_it_is(
    tmp_path: pathlib.Path,
) -> None:
    """The round's own second-road reproductions, both roles.

    `list(range(1089)) + [1089] * 11 + [1100]` has a high tail of two
    values, 1089 held by eleven rows and 1100 by ONE, so the listing rule
    refuses it -- and P4-D346's second road listed it anyway because its
    published pair settled both. Ten cells at `06:58` beside one at
    `06:59` are the same shape on the clock.
    """
    numbers = [str(value) for value in range(1089)] + ["1089"] * 11 + ["1100"]
    described = _described(tmp_path, "heaped", numbers)
    block = described.document["columns"][0]
    tails = block["tails"]
    assert isinstance(tails, dict)
    assert not tails["high"]["values"], (
        "the high tail named 1100, which one row of this column holds"
    )
    clock = ["06:58"] * 10 + ["06:59"] + _consecutive_minutes(239)
    described = _described(tmp_path, "singleton", clock)
    block = described.document["columns"][0]
    for key in ("low_tail", "high_tail"):
        one = block[key]
        assert isinstance(one, dict)
        if one["values"] is not None:
            assert "06:59" not in one["values"], (
                "the tail named a clock time ONE cell of the column holds"
            )


def test_the_listing_rule_is_the_only_road_to_a_named_value(
    tmp_path: pathlib.Path,
) -> None:
    """RED CHECK: `tail_may_list` forced open, and the singletons return.

    The rule is now the whole of what lets a tail name a value, so
    forcing it open must be enough to make the refused tail name 1100.
    If some other road were still open, the shipped tree would already
    name it and the test above would be red instead.
    """
    numbers = [str(value) for value in range(1089)] + ["1089"] * 11 + ["1100"]
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(
            parsing, "tail_may_list", lambda held, floor, distinct, cells: True
        )
        patch.setattr(
            taxonomy, "tail_may_list", lambda held, floor, distinct, cells: True
        )
        described = _described(tmp_path, "opened", numbers)
    block = described.document["columns"][0]
    tails = block["tails"]
    assert isinstance(tails, dict)
    assert 1100.0 in list(tails["high"]["values"]), (
        "with the listing rule forced open the tail still named nothing, so "
        "the rule is not what decides it"
    )


# -- 3a. the subfloor measurement of a checked file ----------------------


def test_a_group_smaller_than_the_floor_keeps_its_verdict_and_drops_its_numbers(
    tmp_path: pathlib.Path,
) -> None:
    """Dates item 1: one cell below the boundary named January 1 exactly.

    The cells this walk counts are the file's own cells beyond the
    DESCRIPTION's boundary, which is not where the file's own boundary
    stands, so it can measure a group no description of that file would
    publish a number for. Here the description's low boundary is the
    twelfth consecutive day and the file keeps the first day and then the
    twelfth onward: ONE cell below the boundary, eleven days away. The
    verdict stands and the numbers are gone.
    """
    cells = _consecutive_dates(200)
    described = _described(tmp_path, "twohundred", cells)
    kept = [cells[0]] + [cells[11]] * 11 + cells[11:]
    outcome = kpi_shapes.measure(
        described, _one_column("value", kept), "subfloor.csv"
    )
    found = [
        check for check in outcome.checks
        if check.subcheck.startswith("tails.low.")
    ]
    assert found, "the low tail set no obligation at all"
    for check in found:
        if check.verdict in (validation.HELD, validation.MISSED):
            assert check.achieved == "", (
                f"{check.subcheck} printed {check.achieved!r}, which is a "
                f"measurement over fewer cells than the floor"
            )
        if check.verdict == validation.MISSED:
            assert check.note, (
                f"{check.subcheck} MISSED and said neither the value nor "
                f"why it is kept back"
            )


def test_the_same_walk_shows_its_numbers_above_the_floor(
    tmp_path: pathlib.Path,
) -> None:
    """NON-VACUITY: the gate is the floor and not a constant.

    A file whose count beyond the description's boundary REACHES the
    floor has the same three obligations measured and printed, so the
    withholding above is the group's size doing it and not this code
    going quiet on every file.
    """
    cells = [f"{100 + index * index}" for index in range(400)]
    described = _described(tmp_path, "squares", cells)
    outcome = kpi_shapes.measure(
        described, _one_column("value", cells), "itself.csv"
    )
    shown = [
        check for check in outcome.checks
        if check.subcheck.startswith("tails.low.") and check.achieved
    ]
    assert shown, (
        "no tail measurement of a conforming file was printed at all, so "
        "the subfloor rule above cannot be told from silence"
    )


# -- 3b. the endpoint the root-mean-square cannot certify ----------------


def test_the_root_mean_square_no_longer_certifies_a_published_end(
    tmp_path: pathlib.Path,
) -> None:
    """Numeric item 6: a file whose minimum is 9 was reported HELD at 10.

    The root-mean-square distance is a LOWER bound on a tail's largest
    distance, so `boundary - rms` is an UPPER bound on a low file's own
    minimum; read as a lower one it certified an end the file breaks. The
    old arithmetic is computed here beside the new verdict, so this test
    says what the repair changed.
    """
    cells = ["10"] * 11 + [str(value) for value in range(20, 1509)]
    described = _described(tmp_path, "heapedmin", cells)
    block = described.document["columns"][0]
    assert block["percentiles"]["min"] == 10.0, (
        "this shape is chosen because its own minimum is published: eleven "
        "rows hold it, so it is a value of a group"
    )
    bad = ["9"] + ["10"] * 10 + [str(value) for value in range(20, 1508)]
    bad = bad + ["1507"]
    outcome = kpi_shapes.measure(described, _one_column("value", bad), "nine.csv")
    found = [
        check for check in outcome.checks
        if check.subcheck.startswith("ladder.min")
    ]
    assert len(found) == 1
    assert found[0].verdict != validation.HELD, (
        "the file's own minimum is 9 against a published 10 and the check "
        "certified it"
    )
    assert found[0].achieved == "", "the file's own extreme was printed"
    # AND THE OLD ARITHMETIC WOULD HAVE SAID OTHERWISE, which is what
    # makes this a red check rather than a restatement.
    rebuilt = profile.build_document(
        reading.read_table(
            str(fixtures.write(tmp_path, "nine-again.csv", _one_column("value", bad))),
            small_cell_floor=FLOOR,
        ),
        taxonomy.Settings(small_cell_floor=FLOOR),
        [],
        [],
        [],
    )
    side = rebuilt["columns"][0]["tails"]["low"]
    boundary = rebuilt["columns"][0]["percentiles"]["p01"]
    assert side["percent"] == 1, "the boundary rung this reads is the p01 one"
    assert boundary - side["rms_distance"] >= 10.0, (
        "this file no longer reproduces the defect: the old reading has to "
        "be the one that passes it"
    )


def test_a_file_the_bounds_convict_still_misses(tmp_path: pathlib.Path) -> None:
    """NON-VACUITY: the two bounds still reach a verdict where they can.

    A file whose own tail reaches far past the published end is convicted
    by the sharper of the two lower bounds on its largest distance --
    `rms**2 / mean`, which no distance can be below -- so the repair is
    not "never decide".

    ITS LOW CELLS ARE SPREAD AND NOT PILED ON ONE, because a file with a
    single far cell has a tail whose sum of squares is the square of its
    sum, which one part alone can make: that tail is settled by its own
    pair and so publishes neither distance, and then there is nothing for
    a bound to be drawn from. Eleven cells stepping ten apart publish
    theirs.
    """
    cells = ["10"] * 11 + [str(value) for value in range(20, 1509)]
    described = _described(tmp_path, "heapedmin2", cells)
    bad = [str(-100 + 10 * step) for step in range(11)]
    bad = bad + [str(value) for value in range(20, 1509)]
    outcome = kpi_shapes.measure(described, _one_column("value", bad), "far.csv")
    found = [
        check for check in outcome.checks
        if check.subcheck.startswith("ladder.min")
    ]
    assert len(found) == 1
    assert found[0].verdict == validation.MISSED, found[0]
    assert found[0].achieved == "", "the file's own extreme was printed"


# -- 3c. the exact check that a window cannot reach ----------------------


_HUGE = (
    ["-1.7e308"] * 60 + [str(value) for value in range(28)] + ["1.7e308"] * 12
)


def test_an_unreachable_moment_window_leaves_the_exact_check_standing(
    tmp_path: pathlib.Path,
) -> None:
    """Numeric item 7: the whole side was skipped, values check and all.

    This column's high tail lists `1.7e308` -- twelve rows hold it, so
    the listing rule admits it -- and its G12.13 window has no end this
    format can write. A file holding `1.6e308` twelve times instead
    reported no miss anywhere and appeared in no not-checkable listing
    either, so the obligation simply vanished.
    """
    described = _described(tmp_path, "huge", _HUGE)
    block = described.document["columns"][0]
    listed = block["tails"]["high"]["values"]
    assert listed, "this shape is chosen because its high tail lists a value"
    smaller = (
        ["-1.7e308"] * 60
        + [str(value) for value in range(28)]
        + ["1.6e308"] * 12
    )
    outcome = kpi_shapes.measure(
        described, _one_column("value", smaller), "smaller.csv"
    )
    missed = [
        check for check in outcome.checks
        if check.subcheck == "tails.high.values"
    ]
    assert len(missed) == 1 and missed[0].verdict == validation.MISSED, missed
    assert missed[0].achieved == "", "the file's own tail values were printed"
    # ...and the two obligations no window reaches are ACCOUNTED FOR.
    named = {
        listing.subcheck for listing in outcome.listings
        if listing.subcheck.startswith("tails.high.")
    }
    assert "tails.high.mean_distance" in named
    assert "tails.high.rms_distance" in named


def test_the_exact_check_does_not_depend_on_a_window_at_all(
    tmp_path: pathlib.Path,
) -> None:
    """RED CHECK: every window unreachable, and the exact check must stand.

    With `_finite_window` forced False the two moment obligations of every
    tail go to the not-checkable census, and the listed-values check must
    still be built and still be able to MISS. Before the repair the same
    condition removed it.
    """
    described = _described(tmp_path, "huge2", _HUGE)
    smaller = (
        ["-1.7e308"] * 60
        + [str(value) for value in range(28)]
        + ["1.6e308"] * 12
    )
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(validation, "_finite_window", lambda window: False)
        outcome = kpi_shapes.measure(
            described, _one_column("value", smaller), "smaller2.csv"
        )
    kinds = {
        check.subcheck: check.verdict for check in outcome.checks
        if check.subcheck.startswith("tails.")
    }
    assert kinds.get("tails.high.values") == validation.MISSED, kinds
    assert "tails.high.mean_distance" not in kinds
    named = {
        listing.subcheck for listing in outcome.listings
        if listing.subcheck.startswith("tails.")
    }
    assert "tails.high.mean_distance" in named
    assert "tails.low.mean_distance" in named


# -- 4. the summary's own sentence ---------------------------------------


def _summary_of(described) -> str:
    return summary.render(described.document, "")


def test_the_summary_never_says_unpublished_over_values_it_prints(
    tmp_path: pathlib.Path,
) -> None:
    """Numeric item 11: one page said both things about the same tail.

    Each integer 0 to 10, ten times, publishes low-tail values `[0, 1]`
    and high-tail values `[9, 10]` -- a bounded scale every step of which
    many rows hold, which the owner's ruling reaches. The page said "the
    12 smallest values are not published" and then printed two of them.

    BOTH HALVES ARE ABOUT WHAT THE PAGE SAYS, NOT ABOUT ITS WORDING. The
    second half quoted "names which values they are" and the repair of
    the six untrue sentences (2026-09-23, finding 7) rewrote that
    heading, which left this asserting a phrase no page writes. What it
    is FOR is that the page tells the reader a listed tail's values are
    named and says which column they belong to, so it is asked that way:
    the heading's own stem, and the column named under it.
    """
    cells = [str(value % 11) for value in range(110)]
    described = _described(tmp_path, "likert", cells)
    block = described.document["columns"][0]
    assert block["tails"]["low"]["values"], "this shape lists its values"
    page = _summary_of(described)
    for line in page.splitlines():
        if "values are not published" in line:
            raise AssertionError(
                "the page says a listed tail's values are not published: "
                + line.strip()
            )
    heading = "the description names which values"
    assert heading in page, (
        "the page does not tell the reader that a listed tail's values "
        "are named at all"
    )
    named = page[page.index(heading):].split("\n\n")[0]
    assert block["name"] in named, (
        "the page says a bounded scale's tail names its values and does "
        f"not say it of {block['name']}: {named!r}"
    )


def test_the_summary_says_a_withheld_pair_is_withheld(
    tmp_path: pathlib.Path,
) -> None:
    """And the third shape a tail can take has a sentence of its own.

    A tail that publishes neither distance is neither "not published,
    they lie on average N below" nor "the values named below". The page
    has to say what is true of it, and printing `None` as an average
    would not be a sentence at all.
    """
    described = _described(
        tmp_path, "consec", [str(value) for value in range(CONSECUTIVE)]
    )
    page = _summary_of(described)
    assert "give those values back one by one" in page
    assert "None" not in page, page


# -- the contract shapes the two roles now admit ------------------------


def test_a_tail_publishes_both_distances_or_neither() -> None:
    """DT1 and TL5: a mean standing alone is half the back-solve.

    Asked of the loader's own two readers, because the shape a
    description may carry is the loader's statement and not the
    producer's: a tail with one distance is refused on both roles, and a
    tail with neither is accepted.
    """
    neither = {
        "boundary": "2020-01-12",
        "rows": 11,
        "mean_distance": None,
        "rms_distance": None,
        "values": None,
    }
    assert contract._tail_object(
        dict(neither), "low_tail", "the column", "date", ""
    ) is not None
    for half in (
        {"mean_distance": 6.0, "rms_distance": None},
        {"mean_distance": None, "rms_distance": 6.8},
    ):
        broken = dict(neither)
        broken.update(half)
        with pytest.raises(Exception) as raised:
            contract._tail_object(broken, "low_tail", "the column", "date", "")
        assert "DT1" in str(raised.value) or "distances" in str(raised.value)


def test_the_withheld_tail_is_read_as_the_narrowest_it_can_be(
    tmp_path: pathlib.Path,
) -> None:
    """A tail with no pair is read as `rows` grid steps out (method G5.3b).

    THE NARROWEST TAIL THE DESCRIPTION STILL ASKS FOR, and the least it
    can say: the rows lie strictly beyond the boundary and the column's
    own count of different values asks them to differ, so `rows` steps of
    the published grid is the least room they can have. On the integers 0
    to 1100 the boundary rungs are 11 and 1089, so the two ends come out
    at 11 - 11 = 0 and 1089 + 11 = 1100 -- which are this column's OWN
    smallest and largest values, reached without either of them being
    published, and the twin holds its mean, its spread, its count of
    different values and every published rung.

    Two wider readings were measured and rejected; plan P4-D349 carries
    what each costs and on which shape.
    """
    cells = [str(value) for value in range(CONSECUTIVE)]
    described = _described(tmp_path, "read", cells)
    facts = described.loaded.columns[0].facts
    ladder = contract.tail_ladder(facts)
    assert ladder is not None
    tails = facts.tails
    assert tails is not None and tails.low is not None
    assert tails.high is not None
    low_rung = described.document["columns"][0]["percentiles"]["p01"]
    high_rung = described.document["columns"][0]["percentiles"]["p99"]
    assert ladder[0] == low_rung - tails.low.rows, (
        "the low end is not the narrowest reading the method states"
    )
    assert ladder[100] == high_rung + tails.high.rows, (
        "the high end is not the narrowest reading the method states"
    )
    assert (ladder[0], ladder[100]) == (0.0, 1100.0)
    for seed in (0, 4, 9):
        twin = kpi_shapes.twin_text(described, seed)
        outcome = kpi_shapes.measure(described, twin, f"twin-{seed}.csv")
        assert kpi_shapes.missed(outcome) == [], (
            f"seed {seed}: the twin of a column whose two tails both "
            f"withhold their pair missed an obligation"
        )


def test_the_document_round_trips_through_its_own_loader(
    tmp_path: pathlib.Path,
) -> None:
    """Every shape this file builds is one the strict loader accepts.

    `kpi_shapes.describe` writes the description and loads it back, so a
    shape the loader refuses raises here rather than passing quietly; this
    asserts the round trip is what happened rather than leaving it to be
    inferred.
    """
    for name, cells in (
        ("integers", [str(value) for value in range(CONSECUTIVE)]),
        ("dates", _consecutive_dates(240)),
        ("minutes", _consecutive_minutes(240)),
        ("huge", _HUGE),
    ):
        described = _described(tmp_path, f"trip-{name}", cells)
        assert isinstance(described.loaded, contract.Profile)
        again = json.loads(
            (described.folder / f"trip-{name}-profile.json").read_text(
                encoding="utf-8"
            )
        )
        assert again["columns"][0]["name"] == "value"
