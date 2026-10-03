"""The reader's one review (stage 3b landing T1, plan P4-D370): each item it raised, pinned.

Codex read landing T1 at 110cb46 and raised eleven items. Items 4 and 5
-- the date-code question on the clock forms T1 added, and the reading
that question promises -- are the R1 landing's (plan P4-D381) and are
fixed in its own stream. Every other item has a clause here that failed
at 110cb46 and passes with its fix:

* item 1 `test_item_1_a_rewritten_hour_never_spells_a_declared_absence`
  -- a cell of the other hour width, rewritten in the column's, spelled
  a declared missing value, so the twin wrote it as a hole (191 holes
  where the source has 11);
* item 2 `test_item_2_the_tail_recount_reads_the_column_s_face_alone`
  -- validation's tail recount read stamps on another face, which the
  producer had counted unread, and the source missed four checks;
* item 3 `test_item_3_the_day_and_month_readings_are_compared_on_the_face`
  -- day first won on cells the face then dropped, and the month-first
  reading that cleared the line was never asked again;
* item 6 `test_item_6_the_unnamed_widths_are_placed_wherever_days_can_hold_them`
  -- G7.5 step 5 walked the days greedily, missed six and seven where
  four and six overshot, and said no set of days could hold them;
* item 7 `test_item_7_a_twelve_hour_style_needs_its_declaration`
  -- the loader took a 12-hour style no declaration stood behind;
* item 8 `test_item_8_a_scripted_run_names_the_clock_question_s_own_answer`
  -- the notice for a scripted run offered `--code` to the 12-hour
  question and called a clock column text;
* item 9 `test_item_9_a_pooled_style_is_not_an_unused_declaration`
  -- a declared stamp whose written clock was pooled was told nothing was
  read on a 12-hour clock;
* item 10 `test_item_10_the_twelve_hour_question_says_what_it_read`
  -- the 12-hour question said every value wrote a time of day;
* item 11 `test_item_11_no_retained_clause_contradicts_the_forty_forms`
  -- the contract and the method still refused a one-figure hour.
"""

import pathlib

import pytest

from tests import test_stage3b_reader as gate


# -- item 1: a rewritten hour never spells a declared absence -----------


def _padded_beside_one_figure() -> "list[str]":
    """Codex's shape: 180 `1:00`, the padded minutes `01:01` to `04:40` once, eleven `01:00`."""
    return (
        ["1:00"] * 180
        + [f"{minute // 60:02d}:{minute % 60:02d}" for minute in range(61, 281)]
        + ["01:00"] * 11
    )


@pytest.mark.parametrize("prefix", ["", "3/17/2023 "])
def test_item_1_a_rewritten_hour_never_spells_a_declared_absence(
    tmp_path: pathlib.Path, prefix: str
) -> None:
    """`01:00` declared missing: the 180 present `1:00` stay present in the twin.

    At 110cb46 the column kept the padded width most cells show, rewrote
    every `1:00` as `01:00` -- the declared missing spelling -- and the
    twin at seed 0 held 191 holes against the source's eleven. The width
    that spells no declared absence is kept instead.
    """
    cells = [prefix + cell for cell in _padded_beside_one_figure()]
    block, profile, _questions = gate._described(
        tmp_path, cells, "--missing-value", f"{prefix}01:00"
    )
    assert block["n_present"] == 400 and block["n_missing"] == 11
    assert block["n_unparsed"] == 0
    twin, written = gate._twin(profile, 0)
    assert written.count(f"{prefix}01:00") == 11
    assert gate._style_of(block) == "h"
    # ...and the source and its twin both validate with nothing missed.
    for checked in (tmp_path / "real.csv", twin):
        code, report = gate._validated(profile, checked)
        assert code == 0, report[-3000:]
    for cell in written:
        if cell != f"{prefix}01:00":
            kind = "stamp" if prefix else "clock"
            assert gate._wears(cell, kind, "h"), cell


# -- item 2: the tail recount reads the column's face alone -------------


def test_item_2_the_tail_recount_reads_the_column_s_face_alone(tmp_path: pathlib.Path) -> None:
    """Three 24-hour stamps beside 300 marked ones: the source validates clean.

    The producer counts the three unread, on another face (NF108). At
    110cb46 validation's tail recount read all 303, and the unchanged
    source missed the high tail's boundary, count, mean and RMS distance.
    """
    cells = [
        f"3/17/2023 {1 + minute // 60}:{minute % 60:02d} AM" for minute in range(300)
    ] + ["12/31/2030 23:59"] * 3
    block, profile, _questions = gate._described(tmp_path, cells)
    assert block["role"] == "datetime" and block["n_unparsed"] == 3
    code, report = gate._validated(profile, tmp_path / "real.csv")
    assert code == 0, report[-3000:]


# -- item 3: the day and month readings are compared on the face --------


def test_item_3_the_day_and_month_readings_are_compared_on_the_face(
    tmp_path: pathlib.Path,
) -> None:
    """Month first reads 990 of 1,000 stamps on their face; day first, 989.

    At 110cb46 day first parsed 999 -- ten of them 24-hour clocks beside
    989 marked ones -- and won the comparison, then dropped those ten as
    another face and fell under the line; the month-first reading, which
    cleared it, was never asked again, and the column was free text.
    """
    cells = [
        f"{3 + i // 720}/{1 + (i // 60) % 12}/2023 6:{i % 60:02d} AM" for i in range(989)
    ]
    cells += [f"17/4/2023 06:{minute:02d}" for minute in range(10)]
    cells += ["4/17/2023 6:42 AM"]
    block, _profile, _questions = gate._described(tmp_path, cells)
    assert block["role"] == "datetime", block["role"]
    assert block["format"] == "month-first-datetime"
    assert block["n_unparsed"] == 10
