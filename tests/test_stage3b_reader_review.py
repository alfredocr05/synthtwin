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
  question and called a clock column text; and, at the merge of landing
  3b.5, `test_item_8_at_the_merge_of_landing_3b_5_a_clock_or_labels_column_is_offered_code`
  -- the clock-or-labels question fell to the block for measurements;
* item 9 `test_item_9_a_pooled_style_is_not_an_unused_declaration`
  -- a declared stamp whose written clock was pooled was told nothing was
  read on a 12-hour clock;
* item 10 `test_item_10_the_twelve_hour_question_says_what_it_read`
  -- the 12-hour question said every value wrote a time of day;
* item 11 `test_item_11_no_retained_clause_contradicts_the_forty_forms`
  -- the contract and the method still refused a one-figure hour.

And the fix stream's second round, each clause red at c13edd8, the head
of its first round, and each but the bound's red at 110cb46 too:

* items 1 and 2 `test_items_1_and_2_a_cell_counted_unread_is_in_no_recount`
  -- where both widths spell a declared absence the cells so written
  are counted unread, and validation's recount read them below a low
  tail measured without them: the unchanged source missed four checks;
* item 2 `test_item_2_a_stamp_on_another_face_is_in_no_recount` -- the
  census of date widths still counted stamps on another face;
* item 6 `test_item_6_a_census_the_first_walk_cannot_place_is_searched_most_ranks_first`
  and `test_item_6_the_search_stops_at_its_bound_product_and_oracle_alike`
  -- the search walked fewest ranks first and unbounded: 99 seconds on
  a census built so that no assignment exists, and 2.8 million states
  and 275 MB on one that a search most ranks first places in 99;
* item 7, the converse clause of its test -- a declared column published
  on the 24-hour face loaded, and the unchanged source missed 10 checks;
* item 9 `test_item_9_a_pooled_marked_stamp_is_a_declaration_that_reached_nothing`
  -- a declared stamp whose clocks write PM was told the declaration was
  used;
* item 10, the colon clause of its test -- a clock of the other
  precision was said not to be numbers joined by a colon.

And its third round, item 11 alone, each sentence it adds red at
9b60ab1 and every one but the first round's own "not another form's
cell" red at 110cb46 too: G7.5 still sent a 12-hour clock and Excel's
unpadded hour to free text, G7A.5 still stepped a stand-in past a clock
time "in EITHER form", the contract's `n_unparsed` row still counted
"the other form's cells", its fourth refusal said a cell of the other
hour width was "not another form's cell" and its pricing of the clock
facts still had `clock_form` name one of "two written clock forms", and
the comments and docstrings of the product and the oracle still spoke
of two clock forms -- one of them, the clock block's own, still saying
its ladder was ordered by text. The sentences are now matched whatever
their case and across a comment's lines, since `Two digits a field`
survived the first round's lower-case entry.
"""

import copy
import json
import pathlib

import pytest

from synthtwin import contract, errors
from tests import fixtures
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
    twin at seed 0 held 191 holes against the source's eleven. A stamp
    keeps the width that spells no declared absence instead. A column of
    clock times keeps the width most cells show since the merge of
    landing 3b.5's round 2 (method G7A.4): its 180 `1:00` stand on a heap
    at the place `01:00` names, and its twin writes them `1:00` there,
    as the table did, and every other cell padded, as the table did.
    """
    cells = [prefix + cell for cell in _padded_beside_one_figure()]
    block, profile, _questions = gate._described(
        tmp_path, cells, "--missing-value", f"{prefix}01:00"
    )
    assert block["n_present"] == 400 and block["n_missing"] == 11
    assert block["n_unparsed"] == 0
    twin, written = gate._twin(profile, 0)
    assert written.count(f"{prefix}01:00") == 11
    if not prefix:
        assert gate._style_of(block) == "hh"
        assert written.count("1:00") == 180
        for checked in (tmp_path / "real.csv", twin):
            code, report = gate._validated(profile, checked)
            assert code == 0, report[-3000:]
        for cell in written:
            if cell not in ("01:00", "1:00"):
                assert gate._wears(cell, "clock", "hh"), cell
        return
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


def _both_widths_spell_an_absence() -> "list[str]":
    """Padded minutes from `06:40`, three `1:00`, twenty `02:00`, and eleven each of `01:00` and `2:00`."""
    return (
        [f"{minute // 60:02d}:{minute % 60:02d}" for minute in range(400, 1400)]
        + ["1:00"] * 3
        + ["02:00"] * 20
        + ["01:00"] * 11
        + ["2:00"] * 11
    )


@pytest.mark.parametrize("prefix", ["", "3/17/2023 "])
def test_items_1_and_2_a_cell_counted_unread_is_in_no_recount(
    tmp_path: pathlib.Path, prefix: str
) -> None:
    """`01:00` and `2:00` declared missing: both widths spell one, so the three `1:00` are unread everywhere.

    At 110cb46 the three were written `01:00`, the declared word, and
    counted present. Since item 1 they are counted unread, as C6-10a
    says -- and at c13edd8 validation's recount still read them, below
    the low tail the description measured without them, so the unchanged
    source missed four checks on clocks and five on stamps, the census of
    date widths among them. Every recount now reads what the producer read.
    """
    cells = [prefix + cell for cell in _both_widths_spell_an_absence()]
    block, profile, _questions = gate._described(
        tmp_path, cells,
        "--missing-value", f"{prefix}01:00", "--missing-value", f"{prefix}2:00",
    )
    assert block["n_present"] == 1023 and block["n_missing"] == 22
    # A column of clock times reads the three at the place `01:00` names
    # since the merge of landing 3b.5's round 2 (method G7A.4); a stamp
    # still counts them unread.
    assert block["n_unparsed"] == (3 if prefix else 0)
    code, report = gate._validated(profile, tmp_path / "real.csv")
    assert code == 0, report[-3000:]
    twin, _written = gate._twin(profile, 0)
    code, report = gate._validated(profile, twin)
    assert code == 0, report[-3000:]


def test_item_2_a_stamp_on_another_face_is_in_no_recount(tmp_path: pathlib.Path) -> None:
    """Three `3/18/2023 23:59` beside 600 marked stamps: no recount reads the three.

    The producer counts them unread (NF108) and publishes its census of
    date widths and its tails without them. At 110cb46 every recount
    read them, and the unchanged source missed five checks; at c13edd8
    the tail recount read the face and the census of widths did not, and
    it still missed one.
    """
    cells = [
        f"3/{1 + minute // 60}/2023 {1 + minute % 12}:{minute % 60:02d} AM"
        for minute in range(600)
    ] + ["3/18/2023 23:59"] * 3
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


# -- item 6: the unnamed widths are placed wherever days can hold them ---

_SIX_AND_SEVEN = (
    ["03/01/2023"] * 83 + ["03/02/2023"] * 4 + ["3/03/2023"] * 5 + ["03/4/2023"] * 8
)


@pytest.mark.parametrize("seed", (0, 1, 2))
def test_item_6_the_unnamed_widths_are_placed_wherever_days_can_hold_them(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """`{"padded": 87}` over 100 dates: the remainder of 13 goes on two whole days.

    The twin's days hold 83, 4, 6 and 7 ranks at seeds 0 to 2. At 110cb46
    step 5 took 4 and 6, could not take 7, stopped short of 13 and said
    no set of whole dates held that many, though 6 and 7 do; every cell
    was written padded and the twin's own description named 100.
    """
    block, profile, _questions = gate._described(tmp_path, _SIX_AND_SEVEN)
    assert block["date_field_widths"] == {"padded": 87}
    twin, written = gate._twin(profile, seed)
    # Thirteen cells in a width the census does not name: a field of one figure.
    unnamed = [cell for cell in written if min(len(field) for field in cell.split("/")[:2]) == 1]
    assert len(unnamed) == 13, sorted(set(unnamed))
    report = (twin.parent / "real-twin-report.txt").read_text(encoding="utf-8")
    assert "no set of whole dates" not in report
    code, quality = gate._validated(profile, twin)
    assert code == 0, quality[-3000:]


def test_item_6_the_oracle_places_the_same_days() -> None:
    """G7.5 step 5's oracle makes the product's choice, on the walk that needed a step back."""
    from synthtwin import generation
    from tools.reference import make_generation_reference_vectors as oracle

    census = {"padded": 87}
    weights = {"padded": 87}
    days = [0] * 83 + [1] * 4 + [2] * 6 + [3] * 7
    both = list(range(100))
    product = generation._unnamed_remainder(census, weights, both, days, 100, 11)
    reference = oracle.width_remainder(census, weights, both, days, 100, 11)
    assert product is not None and product == reference
    assert sorted({days[rank] for rank in product}) == [2, 3]


def _every_size_up_to(cap: int) -> "tuple[dict[str, int], list[int], int]":
    """A named day of 5,000 ranks, then one day each of 1 to ``cap`` ranks; three words' worth left over."""
    days = [0] * 5000
    for day in range(1, cap + 1):
        days += [day] * day
    return {"padded": len(days) - 3 * cap}, days, len(days)


def test_item_6_a_census_the_first_walk_cannot_place_is_searched_most_ranks_first() -> None:
    """Days of every size from 1 to 99 under a remainder of 297: three words of 99, placed in 99 states.

    The walk that never steps back falls short here. At c13edd8 the
    search walked the days fewest ranks first, with no bound, and looked
    at 2.8 million states -- 2.3 seconds and 275 MB -- before its answer;
    most ranks first it fills the words with the days that fit them
    least, and finds one on its first path, 99 states.
    """
    from synthtwin import generation
    from tools.reference import make_generation_reference_vectors as oracle

    chosen, entered = generation._days_searched(list(range(99, 0, -1)), 297, 3, 99)
    assert chosen is not None and entered == 99
    census, days, parsed = _every_size_up_to(99)
    both = list(range(parsed))
    product = generation._unnamed_remainder(census, dict(census), both, days, parsed, 100)
    reference = oracle.width_remainder(census, dict(census), both, days, parsed, 100)
    assert product is not None and product == reference
    held: "dict[str, int]" = {}
    for word in product.values():
        held[word] = (held[word] if word in held else 0) + 1
    assert held == {"unpadded": 99, "first-padded": 99, "second-padded": 99}
    # ...whole days: every rank of a day wears one word.
    for day in range(1, 100):
        assert len({product[rank] for rank in both if days[rank] == day and rank in product}) <= 1


def test_item_6_the_search_stops_at_its_bound_product_and_oracle_alike(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A census built so that no assignment exists stops at the bound; product and oracle share it.

    At c13edd8 the search had no bound and no reach: days of even sizes
    under an odd remainder at a floor of 100 walked every state there is,
    99 seconds. Now no state is entered there at all, a census of twos
    and one three that no assignment fills is walked to its end inside
    the bound, and the bound -- 98 states, then 99 -- moves the product
    and the oracle together.
    """
    from synthtwin import generation
    from tools.reference import make_generation_reference_vectors as oracle

    evens = sorted([2, 4, 6, 8, 10, 12] * 20, reverse=True)
    assert generation._days_searched(evens, 297, 3, 99) == (None, 0)
    twos_and_a_three = [3] + [2] * 73
    assert generation._days_searched(twos_and_a_three, 147, 3, 49) == (None, 15601)
    assert generation._days_searched(twos_and_a_three, 147, 3, 49, 1000) == (None, 1001)
    census, days, parsed = _every_size_up_to(99)
    both = list(range(parsed))
    for bound, placed in ((98, False), (99, True)):
        monkeypatch.setattr(generation, "_WIDTH_WALK_STATES", bound)
        monkeypatch.setattr(oracle, "WIDTH_WALK_STATES", bound)
        product = generation._unnamed_remainder(census, dict(census), both, days, parsed, 100)
        reference = oracle.width_remainder(census, dict(census), both, days, parsed, 100)
        assert product == reference
        assert (product is not None) == placed


# -- item 7: a 12-hour style needs its declaration -----------------------


def _twelve_hour_dial() -> "list[str]":
    """Codex's declared clock: the hour after midnight `12:00` to `12:59`, then `1:00` to `4:59`."""
    return [f"12:{minute:02d}" for minute in range(60)] + [
        f"{hour}:{minute:02d}" for hour in range(1, 5) for minute in range(60)
    ]


def _described_here(
    folder: pathlib.Path, cells: "list[str]", *flags: str
) -> "tuple[dict[str, object], pathlib.Path]":
    """`synthtwin profile` over one column, the command built in this module.

    The description item 7 hands the loader is the product's own file,
    and `tests/test_description_line_endings.py` asks a module that
    loads a description to show where its bytes came from: the fixture
    that decides them, or the product run by the module itself. The
    table and the options are `gate._described`'s.
    """
    folder.mkdir(parents=True, exist_ok=True)
    names, rows = fixtures.rows_at_the_floor("seen_at", cells)
    table = folder / "real.csv"
    table.write_text(fixtures.rows_to_csv(names, rows), encoding="utf-8", newline="")
    command = ["profile", str(table), "--out-dir", str(folder), "--replace", "--smallest-group", "11"]
    assert gate._exit_of(command + list(flags)) == 0
    profile = folder / "real-profile.json"
    return json.loads(profile.read_text(encoding="utf-8"))["columns"][0], profile


@pytest.mark.parametrize("prefix", ["", "3/17/2023 "])
def test_item_7_a_twelve_hour_style_needs_its_declaration(
    tmp_path: pathlib.Path, prefix: str
) -> None:
    """C6-10a: the ` twelve-hour` face is the face of a DECLARED column, and only that.

    At 110cb46 the loader took the style with the declaration cleared,
    and validation, reading `12:xx` as noon, missed 16 checks on the
    unchanged source.
    """
    cells = [prefix + cell for cell in _twelve_hour_dial()]
    block, profile = _described_here(tmp_path, cells, "--twelve-hour", "seen_at")
    assert gate._style_of(block) == "h twelve-hour"
    contract.load_profile(str(profile))
    document = json.loads(profile.read_text(encoding="utf-8"))
    changed = copy.deepcopy(document)
    changed["settings"]["forced_twelve_hour_clocks"] = []
    said = gate._refusal(tmp_path, changed)
    assert contract.INVARIANTS["S8c"] in said, said
    assert "seen_at" in said


@pytest.mark.parametrize("prefix", ["", "3/17/2023 "])
def test_item_7_a_declaration_needs_its_twelve_hour_face(
    tmp_path: pathlib.Path, prefix: str
) -> None:
    """S8c's other half: a declared column with no AM or PM is published on the 12-hour face.

    A declared column reads its unmarked hours on that face and on no
    other (C6-10a). At c13edd8, as at 110cb46, such a document loaded:
    Codex's declared stamp of `12:00` to `4:59`, its word moved to the
    24-hour face, was read by the validator at the declaration -- `12:xx`
    the first hour -- against facts taken at noon, and the unchanged
    source missed 10 checks. Here the dial is `1:00` to `5:59`, which
    both faces spell alike, so the face is the one thing wrong.
    """
    cells = [prefix + f"{hour}:{minute:02d}" for hour in range(1, 6) for minute in range(60)]
    block, profile, _questions = gate._described(tmp_path, cells, "--twelve-hour", "seen_at")
    assert gate._style_of(block) == "h twelve-hour"
    document = json.loads(profile.read_text(encoding="utf-8"))
    changed = copy.deepcopy(document)
    column = changed["columns"][0]
    if prefix:
        column["datetime_separators"] = {
            word.replace(" twelve-hour", ""): count
            for word, count in column["datetime_separators"].items()
        }
    else:
        column["clock_form"] = f"{column['clock_form']}".replace(" twelve-hour", "")
        # ...and since landing 3b.5 (plan P4-D373) its census of ten-minute
        # bins with it, from the 12-hour dial's 72 to the 24-hour dial's 144
        # (CC1), so the face is still the one thing wrong (the merge of
        # landing 3b.5 beside this landing).
        census = column["clock_census"]
        if census:
            last = census[len(census) - 1]
            assert last["count"] == 0 and last["last"] == 71, last
            last["last"] = 143
    said = gate._refusal(tmp_path, changed)
    assert contract.INVARIANTS["S8c"] in said, said
    assert "24-hour face" in said


# -- item 8: a scripted run names the clock question's own answer --------


def _notice(output: str) -> str:
    """The notice a scripted run prints for the columns it would have asked about."""
    start = output.find("THESE COLUMNS")
    assert start >= 0, output[-2000:]
    return output[start : output.find("Nothing is wrong with this profile", start)]


def test_item_8_a_scripted_run_names_the_clock_question_s_own_answer(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The 12-hour question is offered `--twelve-hour`; a clock column is not called text.

    At 110cb46 the minutes `1:00` to `5:59` were put under "read as
    measurements, and might be codes" with `--code seen_at`, and `0:00`
    to `4:59` were "described as text rather than as numbers", though
    both columns are read as times of day.
    """
    twelve = [f"{1 + minute // 60}:{minute % 60:02d}" for minute in range(300)]
    gate._described(tmp_path / "twelve", twelve)
    said = _notice(capsys.readouterr().out)
    assert "--twelve-hour seen_at" in said and "--code seen_at" not in said
    assert "times of day" in said and "as text" not in said
    # ...and its hours in one figure are two numbers to a colon too.
    assert "--measurement seen_at" in said
    joined = [f"{minute // 60}:{minute % 60:02d}" for minute in range(300)]
    gate._described(tmp_path / "joined", joined)
    said = _notice(capsys.readouterr().out)
    assert "--measurement seen_at" in said and "--twelve-hour" not in said
    assert "times of day" in said and "as text" not in said
    # ...and a two-figure 12-hour question is offered nothing else.
    padded = [f"{1 + minute // 60:02d}:{minute % 60:02d}" for minute in range(300)]
    gate._described(tmp_path / "padded", padded)
    said = _notice(capsys.readouterr().out)
    assert "--twelve-hour seen_at" in said and "--measurement" not in said


def test_item_8_at_the_merge_of_landing_3b_5_a_clock_or_labels_column_is_offered_code(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Few shared times are offered `--code` beside the clock's own answers, never called measurements.

    Landing 3b.5 (plan P4-D373) asks whether a column of few times, each
    written by many rows, holds labels written as times, and its review
    adds `code` to the 12-hour question where both fit. Merged into this
    landing's tree, `asking.asks_about_a_clock` knew neither: three
    afternoon shift starts fell to the block saying a column was "read
    as measurements" and described "with an average, a spread", and
    three morning ones were offered `--twelve-hour` alone.
    """
    shifts = ["13:00"] * 100 + ["14:00"] * 100 + ["15:00"] * 100
    gate._described(tmp_path / "shifts", shifts)
    said = _notice(capsys.readouterr().out)
    assert "times of day" in said and "MEASUREMENTS" not in said
    assert "--code seen_at" in said and "--twelve-hour" not in said
    # ...and on a face the 12-hour question also fits, both answers.
    morning = ["07:00"] * 100 + ["08:00"] * 100 + ["09:00"] * 100
    gate._described(tmp_path / "morning", morning)
    said = _notice(capsys.readouterr().out)
    assert "--twelve-hour seen_at" in said and "--code seen_at" in said
    assert "MEASUREMENTS" not in said


# -- item 9: a pooled style is not an unused declaration -----------------


def test_item_9_a_pooled_style_is_not_an_unused_declaration(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ten declared stamps beside ninety `NA`: read on the face, the word pooled.

    At 110cb46 the run said nothing about the column was read on a
    12-hour clock and told the person to drop `--twelve-hour`, which had
    been honoured: only the census naming the written clock was too
    small to print. The stated limit -- that twin writes the 24-hour clock
    -- stands, and is what the run now says.
    """
    cells = [f"3/{17 + day}/2023 12:{day:02d}" for day in range(10)] + ["NA"] * 90
    block, _profile, _questions = gate._described(tmp_path, cells, "--twelve-hour", "seen_at")
    assert block["role"] == "datetime" and block["datetime_separators"] == {"(withheld)": 10}
    said = capsys.readouterr()
    shown = said.out + said.err
    assert "Nothing about this column was read on a 12-hour clock" not in shown
    assert "without --twelve-hour" not in shown
    assert errors.the_twelve_hour_style_was_held_back("seen_at") in shown


def test_item_9_a_pooled_marked_stamp_is_a_declaration_that_reached_nothing(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Ten declared stamps written `1:00 PM` beside ninety `NA`: told the declaration changed nothing.

    A marked clock is one the declaration does not change, so the run
    says so, as it does of a marked column whose word is named. At
    c13edd8 every pooled stamp was told `--twelve-hour` was used and to
    keep it, these too.
    """
    cells = [f"3/{17 + day}/2023 1:{day:02d} PM" for day in range(10)] + ["NA"] * 90
    block, _profile, _questions = gate._described(tmp_path, cells, "--twelve-hour", "seen_at")
    assert block["role"] == "datetime" and block["datetime_separators"] == {"(withheld)": 10}
    said = capsys.readouterr()
    shown = said.out + said.err
    assert errors.the_twelve_hour_style_was_held_back("seen_at") not in shown
    assert errors.the_twelve_hour_declaration_did_not_reach("seen_at", "datetime") in shown


# -- item 10: the 12-hour question says what it read ---------------------


def _seen(questions: "dict[str, object]") -> str:
    """What the questions file says synthtwin saw in `seen_at`."""
    asked = questions["asked"]
    assert isinstance(asked, list)
    found = [entry["what_synthtwin_saw"] for entry in asked if entry["column"] == "seen_at"]
    assert len(found) == 1, questions
    return f"{found[0]}"


def test_item_10_the_twelve_hour_question_says_what_it_read(tmp_path: pathlib.Path) -> None:
    """One `not-a-time` beside the minutes `1:00` to `5:59`: not "every value".

    At 110cb46 the profile counted the cell unread and the question said
    "every value writes a time of day". The colon question a clock in
    one figure keeps said "every value is two or more numbers" the same
    way, and is held to the same rule.
    """
    cells = [f"{1 + minute // 60}:{minute % 60:02d}" for minute in range(300)] + ["not-a-time"]
    block, _profile, questions = gate._described(tmp_path / "twelve", cells)
    assert block["role"] == "time_of_day" and block["n_unparsed"] == 1
    seen = _seen(questions)
    assert "every value" not in seen and "1 to 12" in seen, seen
    cells = [f"{minute // 60}:{minute % 60:02d}" for minute in range(300)] + ["not-a-time"]
    block, _profile, questions = gate._described(tmp_path / "joined", cells)
    assert block["role"] == "time_of_day" and block["n_unparsed"] == 1
    seen = _seen(questions)
    assert "every value" not in seen and "':'" in seen, seen
    # ...and a column every cell of which reads still says so.
    cells = [f"{1 + minute // 60}:{minute % 60:02d}" for minute in range(300)]
    _block, _profile, questions = gate._described(tmp_path / "whole", cells)
    assert "every value" in _seen(questions)
    # ...and the colon question counts the cells that are not numbers
    # joined by a colon, not the cells left unread: `1:00:00` among
    # minutes is unread and is such numbers all the same (at c13edd8 the
    # question said some of them were not).
    cells = [f"{minute // 60}:{minute % 60:02d}" for minute in range(300)] + ["1:00:00"]
    block, _profile, questions = gate._described(tmp_path / "precision", cells)
    assert block["role"] == "time_of_day" and block["n_unparsed"] == 1
    assert "every value is two or more numbers with ':'" in _seen(questions)


# -- item 11: no retained clause contradicts the forty forms -------------

ROOT = pathlib.Path(__file__).resolve().parent.parent

# Each sentence a consumer could follow to refuse `9:30`, or to order
# `9:30 AM` after `1:00 PM` by its text, as 110cb46 still stated it.
_RETIRED = {
    "docs/spec/profile-contract-v6.md": (
        "A single-digit hour does not parse",
        "match ONE of the exactly two clock forms below",
        "because both forms are fixed-width",
        "every field in two digits and in the ranges",
        "in one of the two forms the `time_of_day` role fixes",
        "the `time_of_day` role's two forms",
        "| `clock_form` | string | `hh-mm`, `hh-mm-ss` |",
        "Two clock forms in one column are not read as one clock",
        # ...and the fix stream's second round: T3 still said every
        # ladder agrees with text comparison, the line and its tie-break
        # still spoke of two forms, and a tail window of `hh-mm` alone.
        "and both agree with plain text comparison of the written rungs",
        "Cells of the other clock form, and every other present cell",
        "the finer wins: the column takes `hh-mm-ss`",
        "in minutes (`hh-mm`) or seconds (`hh-mm-ss`)",
        # ...and the third round: `n_unparsed` counted "the other form's
        # cells", the fourth refusal said a cell of the other hour width
        # is not another form's, where under C6-10a it is one -- and is
        # read all the same -- and the pricing of 12.3 still named two.
        "present cells no clock reading of C6-10 accepted, the other form's cells among them",
        "is not another form's cell",
        "says which of the two written clock forms the column's cells wore",
    ),
    "docs/spec/generation-method-v1.md": (
        "What the reader accepts is EXACTLY these two shapes",
        "zero-padded to two digits per",
        "an hour written with one digit such as `9:30`\n(the published spellings are fixed width)",
        # ...and the second round: a cell of the other width is read, and
        # a published value is no longer always the row's own text.
        "values some row wore, character for character",
        "A cell wearing the form the column did NOT publish is counted unparsed",
        "minutes of the day for `hh-mm`, seconds for `hh-mm-ss`",
        # ...and the third round: G7.5 sent a 12-hour clock and Excel's
        # unpadded hour to free text, which the stamp members read since
        # landing T1, and G7A.5 spoke of a clock time in "EITHER form".
        "a 12-hour clock, `08APR2024`, Excel's unpadded hour — still fall to free text",
        "a spelling that would read as a clock time in EITHER form",
        "reads as a clock time under the form the column did NOT publish",
    ),
    # ...and the comments and docstrings that say what the code does (the
    # third round): each still spoke of the clock's two forms.
    "src/synthtwin/contract.py": (
        "two digits a field",
        "the two forms its cells can wear",
        "the time-of-day role's own two forms",
        "which of the two forms the cells wore",
        "hours to 23 and minutes and seconds to 59 -- invariant T1",
    ),
    "src/synthtwin/generation.py": (
        "as a clock time in EITHER form",
        "under the form the column did NOT publish",
    ),
    "src/synthtwin/parsing.py": (
        "its clock is the time-of-day role's two forms",
        "is the time-of-day role's own two forms",
        "then a clock in the time-of-day role's two forms",
    ),
    "src/synthtwin/taxonomy.py": (
        "THE ORDER IS TEXT ORDER",
        "both forms are fixed-width and zero-padded",
        "the two forms are tried in a fixed order",
        "clock times, in one of two forms",
        "Zero where no cell wore either form",
        "every rung is a clock value some row wore",
        "values some row wore, and the reader accepts nothing that needed tidying",
    ),
    "src/synthtwin/validation.py": (
        "the one unit the two forms share",
        "a file that wore the other form",
    ),
    "src/synthtwin/dialect.py": ("the two forms of contract C6-10",),
    "src/synthtwin/profile.py": ("the one place the two forms are named",),
    "tools/reference/make_generation_reference_vectors.py": (
        "as a clock time in NEITHER form",
    ),
}


def _words_of(name: str) -> str:
    """One file's words: each line's comment mark off, whitespace collapsed, case folded."""
    lines = (ROOT / name).read_text(encoding="utf-8").splitlines()
    joined = " ".join(line.strip().lstrip("#") for line in lines)
    return " ".join(joined.split()).casefold()


def test_item_11_no_retained_clause_contradicts_the_forty_forms() -> None:
    """The contract and the method state the forty forms, and no clause of the two forms survives.

    Matched with whitespace collapsed, a comment's marks taken off each
    line and whatever the case, so a retired sentence re-wrapped, run
    across two comment lines or opening a docstring is still found.
    """
    for name, sentences in _RETIRED.items():
        text = _words_of(name)
        for sentence in sentences:
            assert " ".join(sentence.split()).casefold() not in text, (name, sentence)
    contract_text = (ROOT / "docs/spec/profile-contract-v6.md").read_text(encoding="utf-8")
    assert "the thirty-eight more of C6-10a (forty in all" in contract_text
    method = (ROOT / "docs/spec/generation-method-v1.md").read_text(encoding="utf-8")
    assert "**What the reader accepts is EXACTLY the forty forms**" in method
    # ...and the third round's restatements stand where the retired
    # sentences stood.
    method_text = " ".join(method.split())
    assert "`08APR2024` among them" in method_text
    assert "in any of the forty forms (contract C6-10a, `parsing.clock_form`)" in method_text
    assert "**Read the table through the member.** Its texts are the ISO spellings" in method_text
    contract_said = " ".join(contract_text.split())
    assert "every other cell of the other hour width is read (NF109)" in contract_said
    assert "says which of the forty written clock forms of C6-10a" in contract_said
    # ...and the phase 2 plan's retired R-P2-7, which still says what
    # fell to free text the day it retired, says what T1 narrowed.
    plan_said = " ".join((ROOT / "docs/plans/phase-2-generator.md").read_text(encoding="utf-8").split())
    assert "*Narrowed by landing T1 (plan P4-D370; the T1 review's item 11)" in plan_said
