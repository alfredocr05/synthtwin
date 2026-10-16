"""Stage 4 lane S4d: describe at millions of rows (plan P4-D390).

Measured on 66bca69 (planning-notes/work-2026-10/wave5/S4d-build.md):
describing a register of 997,770 rows peaked at 901 MB, a dense numeric
tail of 1,000,000 at 1,025 MB and a table of free text, dates and
numbers of 1,000,000 rows at 1,333 MB. Each column was read into one
record per ROW (`taxonomy._classify_all`), with a folded copy of its
text and a map of its one spelling per label (`taxonomy._tally`); each
date was read into a pair, a key and a day number per row; the survey
held one text per row; and the census's reading of a column stayed held
until the whole table was described.

The lane shares one answer per SPELLING wherever a fixed function of a
cell's text is answered (bounded by `parsing.SPELLING_MEMO_TEXTS` where
values never repeat; past that bound a text met again is shared from its
second sighting, `parsing.SPELLING_MEMO_NOTED`, after Codex's review
found a unique prefix kept every later repeated row apart on d4b114d),
holds a folded label once where folding changes
nothing, keeps only the labels written otherwise than themselves in the
map of spellings (`taxonomy._label_spellings` answers the rest), and
lets each census reading go once its column is described. Every
description is the bytes 66bca69 wrote.

Pinned here by what can be counted without a clock: how many different
objects hold a column's records, texts, date pairs and day numbers; the
map of spellings against 66bca69's `_tally` (`stage4_as_built.TALLY`);
the census reading's release, by a weak reference; and the bytes
`tracemalloc` sees `synthtwin profile` hold per row it adds.
"""

from __future__ import annotations

import datetime
import gc
import json
import math
import pathlib
import random
import tracemalloc
import weakref

import pytest

import fixtures
import kpi_shapes
import stage4_as_built
from synthtwin import parsing, profile, reading, taxonomy

_SETTINGS = taxonomy.Settings()


def _objects(items: "list[object] | tuple[object, ...]") -> int:
    """How many different objects a list holds, by identity."""
    return len({id(item) for item in items})


def _register_cells(rows: int, codes: int, seed: int = 11) -> "list[str]":
    draw = random.Random(seed)
    return [f"{1000001 + draw.randrange(codes)}" for _ in range(rows)]


# -- one record per spelling ----------------------------------------------------


def test_a_million_rows_of_a_thousand_spellings_hold_a_thousand_records() -> None:
    """66bca69 held 1,000,000 records here, one per row; a record per spelling is 1,000."""
    cells = _register_cells(1_000_000, 1_000)
    classified = taxonomy._classify_all(cells)
    assert len(classified) == 1_000_000
    assert _objects(classified) == len(set(cells)) == 1_000
    assert [one.text for one in classified[:2_000]] == cells[:2_000]


def test_records_shared_or_not_answer_as_one_record_a_row() -> None:
    """Past the memo's bound and below it, every record is the one `_classify` makes of its row."""
    draw = random.Random(4)
    distinct = [f"{draw.random() * 1000:.6f}" for _ in range(parsing.SPELLING_MEMO_TEXTS + 3_000)]
    mixed = [draw.choice(["Yes", "yes", " YES", "no", "-999", "1,5", "12 mg", "", "2024-01-05"]) for _ in range(5_000)]
    for cells in (distinct, mixed, distinct[:500] * 3 + mixed):
        for comma in (False, True):
            classified = taxonomy._classify_all(cells, comma)
            assert classified == [taxonomy._classify(one, comma) for one in cells]
    # Past the bound a column whose values never repeat stops sharing:
    # the memo holds no more than the bound, and every row still has its record.
    assert _objects(taxonomy._classify_all(distinct)) == len(distinct)


def test_the_memo_takes_texts_to_its_bound_and_then_while_it_answers_as_many_rows() -> None:
    bound = parsing.SPELLING_MEMO_TEXTS
    assert bound == 65536
    assert parsing.memo_takes(0, 0)
    assert parsing.memo_takes(bound - 1, 0)
    assert not parsing.memo_takes(bound, 0)
    assert not parsing.memo_takes(bound, bound - 1)
    assert parsing.memo_takes(bound, bound)
    assert parsing.memo_takes(3 * bound, 10 * bound)


def test_a_folded_label_that_folding_leaves_as_written_is_the_cell_s_own_text() -> None:
    for text in ("1000001", "yes", "kaloru mine", "2024-01-05", "12.5"):
        assert taxonomy._classify(text).folded is text, text
    for text, folded in (("Yes", "yes"), (" no", "no"), ("MG", "mg")):
        assert taxonomy._classify(text).folded == folded


# -- the map of spellings --------------------------------------------------------


def _tally_as_built() -> object:
    built, _names = stage4_as_built.compiled(taxonomy, stage4_as_built.TALLY, "_tally")
    return built


def _tally_shapes() -> "dict[str, list[str]]":
    draw = random.Random(9)
    return {
        "cases": [draw.choice(["Yes", "yes", "YES", " yes", "No", "no", "NO ", "maybe"]) for _ in range(3_000)],
        "plain words": [draw.choice(["pain", "fever", "cough"]) for _ in range(3_000)],
        "numbers": [f"{draw.gauss(80, 10):.1f}" for _ in range(3_000)],
        "first plain then not": ["abc"] * 5 + ["ABC"] + ["abc"] * 3 + [" abc"],
        "first not then plain": ["ABC", "abc", "abc", "Abc"],
        "codes": [draw.choice(["A1", "a1", "B12", "b12"]) for _ in range(2_000)],
        "one each": [f"Word{k}" for k in range(500)] + [f"word{k}" for k in range(500)],
    }


def test_every_label_s_spellings_are_the_map_66bca69_held() -> None:
    """`_label_spellings` answers every label with 66bca69's map, key order included, and holds only mixed labels."""
    as_built = _tally_as_built()
    for name, cells in _tally_shapes().items():
        classified = taxonomy._classify_all(cells)
        now = taxonomy._tally(classified, len(cells), _SETTINGS)
        before = as_built(classified, len(cells), _SETTINGS)  # type: ignore[operator]
        assert list(now.folded_counts) == list(before.folded_counts), name
        assert now.folded_counts == before.folded_counts, name
        for label in before.folded_counts:
            answered = taxonomy._label_spellings(now.folded_counts, now.spellings_by_folded, label)
            assert list(answered.items()) == list(before.spellings_by_folded[label].items()), (name, label)
        mixed = {label for label in before.spellings_by_folded if list(before.spellings_by_folded[label]) != [label]}
        assert set(now.spellings_by_folded) == mixed, name


def test_a_column_of_plain_labels_holds_no_map_of_spellings() -> None:
    """66bca69 held one map per label: 100,000 maps on 100,000 different numbers."""
    cells = [f"{k}" for k in range(100_000)]
    tallied = taxonomy._tally(taxonomy._classify_all(cells), len(cells), _SETTINGS)
    assert tallied.spellings_by_folded == {}
    assert len(tallied.folded_counts) == 100_000


def _mode_bytes_per_row(cells: "list[str]") -> "tuple[tuple[float | None, int], float]":
    tallied = taxonomy._tally(taxonomy._classify_all(cells), len(cells), _SETTINGS)
    taxonomy._mode_of(taxonomy._tally(taxonomy._classify_all(cells[:50]), 50, _SETTINGS))
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        mode = taxonomy._mode_of(tallied)
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    return mode, held / len(cells)


def test_the_mode_holds_one_map_beside_the_cells() -> None:
    """66bca69 held a map of values beside the counts: about 130 bytes a row on 200,000 different numbers."""
    cells = [f"{1000000 + k}" for k in range(200_000)] + ["1000007", "1000003", "1000007", "1000003"]
    mode, per_row = _mode_bytes_per_row(cells)
    assert mode == (1000003.0, 3)
    assert per_row < 100, per_row
    assert taxonomy._mode_of(taxonomy._tally(taxonomy._classify_all(["2", "2.0", "1", "1e0", "3"]), 5, _SETTINGS)) == (1.0, 2)


def test_a_zero_mode_carries_the_sign_its_last_cell_wrote(tmp_path: pathlib.Path) -> None:
    """"0" and "-0" are one exact number read as 0.0 and -0.0: 66bca69's map kept the last cell's, and so does the walk."""
    counted = [f"{1 + k % 40}" for k in range(200)]
    plus_last = ["-0"] * 30 + counted + ["0"] * 15
    minus_last = ["0"] * 30 + counted + ["-0"] * 15
    for cells, sign in ((plus_last, 1.0), (minus_last, -1.0)):
        mode, count = taxonomy._mode_of(taxonomy._tally(taxonomy._classify_all(cells), len(cells), _SETTINGS))
        assert mode is not None
        assert (mode, count, math.copysign(1.0, mode)) == (0.0, 45, sign)
    text = "minus_last,plus_last\n" + "".join(f"{minus},{plus}\n" for minus, plus in zip(minus_last, plus_last))
    path = fixtures.write(tmp_path, "zeros.csv", text)
    for floor in (11, 36):
        table = reading.read_table(str(path), small_cell_floor=floor)
        document = profile.build_document(table, taxonomy.Settings(small_cell_floor=floor), [], [])
        written = json.dumps(document, sort_keys=True)
        assert written.count('"mode": -0.0, ') == 1, written
        assert written.count('"mode": 0.0, ') == 1, written


# -- the dates -------------------------------------------------------------------


def _date_cells(rows: int, offsets: bool = False) -> "list[str]":
    draw = random.Random(21)
    made: "list[str]" = []
    for _ in range(rows):
        cell = f"20{draw.randint(15, 24)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"
        if offsets:
            cell = cell + f"T{draw.randint(0, 2):02d}:00:00" + draw.choice(["Z", "+01:00", "-05:00"])
        made += [cell]
    return made


def test_the_rows_of_one_date_share_its_pair_up_to_a_million_rows() -> None:
    cells = _date_cells(1_000_000)
    found = taxonomy._matching_date_format(cells, _SETTINGS)
    assert found is not None
    good, sources = found[1], found[2]
    assert len(good) == len(sources) == 1_000_000
    assert _objects(good) == len(set(cells)) <= 3_360


def test_the_rows_of_one_date_share_its_day_number() -> None:
    cells = _date_cells(200_000)
    pairs = [(cell, "") for cell in cells]
    details = {"resolution": taxonomy.RESOLUTION_DATE, "datetimes_read_at": taxonomy.READ_AT_LOCAL, "format": "iso-date", "all_at_midnight": False}
    days = taxonomy._census_days(details, pairs)
    assert len(days) == 200_000
    assert _objects(days) <= len(set(cells))


def test_a_pair_that_keeps_its_offset_is_the_pair_itself() -> None:
    pairs = [(cell[:19], cell[19:]) for cell in _date_cells(20_000, offsets=True)]
    offsets: "dict[str, int]" = {}
    for _canonical, offset in pairs:
        offsets[offset] = (offsets[offset] if offset in offsets else 0) + 1
    kept = taxonomy._offsets_as_published(pairs, offsets)
    assert kept == pairs
    assert all(kept[place] is pairs[place] for place in range(len(pairs)))


def test_ordering_moments_holds_one_key_per_written_moment() -> None:
    """66bca69 built a key per row: about 120 bytes a row over 200,000 rows of 3,360 dates."""
    pairs = [(cell, "") for cell in _date_cells(200_000)]
    expected = sorted(cell for cell, _offset in pairs)
    taxonomy.ordered_moments(pairs[:100], taxonomy.READ_AT_LOCAL)
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        ordered = taxonomy.ordered_moments(pairs, taxonomy.READ_AT_LOCAL)
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    assert ordered[0] == expected and ordered[1] == expected[0] and ordered[2] == expected[-1]
    assert held / len(pairs) < 60, held / len(pairs)


# -- the survey ------------------------------------------------------------------


def test_the_survey_holds_one_text_per_spelling_in_each_column(tmp_path: pathlib.Path) -> None:
    """200,000 rows of 500 codes and 3 words: 66bca69 held 200,000 texts in each column."""
    draw = random.Random(2)
    lines = ["code,arm,note"]
    for row in range(200_000):
        lines += [f"{1000001 + draw.randrange(500)},{draw.choice(['north', 'south', 'east'])},note {row}"]
    path = fixtures.write(tmp_path, "register.csv", "\n".join(lines) + "\n")
    table = reading.read_table(str(path))
    assert table.n_rows == 200_000
    assert _objects(table.columns[0]) == 500
    assert _objects(table.columns[1]) == 3
    assert _objects(table.columns[2]) == 200_000
    assert table.columns[2][:3] == ["note 0", "note 1", "note 2"]


# -- the census reading is let go ------------------------------------------------


def test_the_census_reading_is_let_go_once_its_column_is_described(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """66bca69 kept the census's reading of `code` held while every later column was described."""
    draw = random.Random(8)
    lines = ["code,arm,score"]
    for _ in range(3_000):
        lines += [f"{1000001 + draw.randrange(200)},{draw.choice(['a', 'b'])},{draw.gauss(50, 9):.1f}"]
    path = fixtures.write(tmp_path, "register.csv", "\n".join(lines) + "\n")
    described = taxonomy.profile_column
    handed: "list[weakref.ref[taxonomy.HeldReading]]" = []
    alive_later: "list[bool]" = []

    def watched(*args: object, **kwargs: object) -> taxonomy.ColumnProfile:
        nonlocal handed, alive_later
        if handed:
            gc.collect()
            alive_later += [handed[0]() is not None]
        given = args[12] if len(args) > 12 else kwargs.get("handed_over")
        if isinstance(given, taxonomy.HeldReading):
            handed += [weakref.ref(given)]
        del given
        return described(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "profile_column", watched)
    assert kpi_shapes.quiet_cli(["profile", str(path), "--out-dir", str(tmp_path), "--code", "code"]) == 0
    assert len(handed) == 1, "premise: the census read `code` and handed it over"
    assert alive_later == [False, False]


def test_the_census_reading_is_let_go_while_the_caller_holds_every_argument(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """CPython 3.10's caller kept the readings handed to `build_document` until it returned (plan P4-D390).

    On 3.10 the caller's evaluation stack holds every argument of a call
    until the call returns; from 3.11 a call from Python to Python moves
    them into the callee's frame. 68dae22f handed the readings over as
    `readings=_handed_once(census_box)`, so the description's own
    `readings = ()` let them go on 3.11 and later and on 3.10 they lived
    until the whole table was described: CI's 3.10 jobs read
    `[True, True]` where the test above asks `[False, False]`. Here
    `build_document` is wrapped by a function whose own ``args`` and
    ``kwargs`` hold every argument until the call returns, as 3.10's
    caller does, on any Python: the readings are let go only if what the
    command hands over is the box, which the description empties in its
    own frame. Red on 68dae22f on every Python.
    """
    draw = random.Random(8)
    lines = ["code,arm,score"]
    for _ in range(3_000):
        lines += [f"{1000001 + draw.randrange(200)},{draw.choice(['a', 'b'])},{draw.gauss(50, 9):.1f}"]
    path = fixtures.write(tmp_path, "register.csv", "\n".join(lines) + "\n")
    described = taxonomy.profile_column
    built = profile.build_document
    handed: "list[weakref.ref[taxonomy.HeldReading]]" = []
    alive_later: "list[bool]" = []
    calls: "list[int]" = []

    def watched(*args: object, **kwargs: object) -> taxonomy.ColumnProfile:
        nonlocal handed, alive_later
        if handed:
            gc.collect()
            alive_later += [handed[0]() is not None]
        given = args[12] if len(args) > 12 else kwargs.get("handed_over")
        if isinstance(given, taxonomy.HeldReading):
            handed += [weakref.ref(given)]
        del given
        return described(*args, **kwargs)  # type: ignore[arg-type]

    def holding(*args: object, **kwargs: object) -> "dict[str, object]":
        # ``args`` and ``kwargs`` are this frame's until the call
        # returns: what CPython 3.10's caller stack holds.
        nonlocal calls
        calls += [len(args) + len(kwargs)]
        return built(*args, **kwargs)  # type: ignore[arg-type]

    monkeypatch.setattr(taxonomy, "profile_column", watched)
    monkeypatch.setattr(profile, "build_document", holding)
    assert kpi_shapes.quiet_cli(["profile", str(path), "--out-dir", str(tmp_path), "--code", "code"]) == 0
    assert len(calls) == 1, "premise: the command described the table once, through the wrapper"
    assert len(handed) == 1, "premise: the census read `code` and handed it over"
    assert alive_later == [False, False]


# -- bytes per row ---------------------------------------------------------------


def _profile_peak(folder: pathlib.Path, rows: int) -> int:
    draw = random.Random(3)
    lines = ["code,arm,visit"]
    for _ in range(rows):
        lines += [
            f"{1000001 + draw.randrange(2000)},{'a' if draw.random() < 0.5 else 'b'},"
            f"20{draw.randint(15, 24)}-{draw.randint(1, 12):02d}-{draw.randint(1, 28):02d}"
        ]
    path = fixtures.write(folder, f"t{rows}.csv", "\n".join(lines) + "\n")
    out = folder / f"o{rows}"
    out.mkdir()
    tracemalloc.start()
    try:
        assert kpi_shapes.quiet_cli(["profile", str(path), "--out-dir", str(out), "--code", "code"]) == 0
        return tracemalloc.get_traced_memory()[1]
    finally:
        tracemalloc.stop()


def test_describe_holds_under_three_hundred_bytes_a_row_it_adds(tmp_path: pathlib.Path) -> None:
    """A register of 2,000 codes, two arms and dates: 66bca69 held 1,079 bytes per added row, the lane 124 (`K-S4-08`)."""
    _profile_peak(tmp_path, 2_000)
    smaller = _profile_peak(tmp_path, 40_000)
    larger = _profile_peak(tmp_path, 80_000)
    per_row = (larger - smaller) / 40_000
    assert per_row < 300, per_row


# -- the answers do not move -----------------------------------------------------


def _documents(folder: pathlib.Path) -> "list[dict[str, object]]":
    draw = random.Random(31)
    columns = {
        "code": [f"{1000001 + draw.randrange(300)}" for _ in range(6_000)],
        "label": [draw.choice(["Yes", "yes", "YES", " no", "No", "maybe"]) for _ in range(6_000)],
        "visit": _date_cells(6_000, offsets=True),
        "day": _date_cells(6_000),
        "score": [draw.choice(["-999", f"{draw.gauss(70, 9):.1f}"]) for _ in range(6_000)],
    }
    names = sorted(columns)
    text = ",".join(names) + "\n" + "".join(",".join(columns[name][row] for name in names) + "\n" for row in range(6_000))
    path = fixtures.write(folder, "mixed.csv", text)
    documents: "list[dict[str, object]]" = []
    for floor in (11, 1):
        settings = taxonomy.Settings(small_cell_floor=floor)
        table = reading.read_table(str(path), small_cell_floor=floor)
        documents += [profile.build_document(table, settings, [], ["code"])]
    return documents


def test_no_answer_moves_when_nothing_is_shared(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The memos change which objects hold the answers, never the answers: compared as written text, where -0.0 is not 0.0."""
    shared = json.dumps(_documents(tmp_path), sort_keys=True)
    monkeypatch.setattr(parsing, "memo_takes", lambda held, answered: False)
    monkeypatch.setattr(parsing, "memo_notes", lambda noted: False)
    assert json.dumps(_documents(tmp_path), sort_keys=True) == shared


# -- the measures `K-S4-08` reads (tests/test_kpi_ledger.py) ---------------------


def describe_memory_measures(folder: pathlib.Path) -> "dict[str, float]":
    """Records, date pairs and survey texts per spelling at up to a million rows, and bytes held per row added.

    Past the bound (Codex's review): 65,536 different numbers and then
    "70000" on every later row, 200,000 rows, records per spelling.
    """
    folder.mkdir(parents=True, exist_ok=True)
    cells = _register_cells(1_000_000, 1_000)
    records = _objects(taxonomy._classify_all(cells)) / len(set(cells))
    dates = _date_cells(1_000_000)
    found = taxonomy._matching_date_format(dates, _SETTINGS)
    assert found is not None
    pairs = _objects(found[1]) / len(set(dates))
    draw = random.Random(2)
    lines = ["code"] + [f"{1000001 + draw.randrange(500)}" for _ in range(200_000)]
    path = fixtures.write(folder, "codes.csv", "\n".join(lines) + "\n")
    texts = _objects(reading.read_table(str(path)).columns[0]) / 500
    past = _past_the_bound("prefix", 200_000, parsing.SPELLING_MEMO_TEXTS, _numbers(200_000), _AGAIN)
    past_records = _objects(taxonomy._classify_all(past)) / len(set(past))
    _profile_peak(folder, 2_000)
    smaller = _profile_peak(folder, 40_000)
    larger = _profile_peak(folder, 80_000)
    return {
        "records_per_spelling_past_the_bound_200000_rows": round(past_records, 2),
        "records_per_spelling_1m_rows": round(records, 2),
        "date_pairs_per_spelling_1m_rows": round(pairs, 2),
        "survey_texts_per_spelling_200000_rows": round(texts, 2),
        "describe_held_bytes_per_added_row": round((larger - smaller) / 40_000, 1),
    }


# -- past the bound: a text met again is taken (Codex's review of the lane) ------

_AGAIN = "70000"


def _past_the_bound(case: str, rows: int, bound: int, made: "list[str]", again: str) -> "list[str]":
    """`bound` different texts, then rows of the text `again` that a memo full at the bound met only there.

    "prefix": the rest of the rows all write `again` (Codex's case);
    "interleaved": a new text and `again` by turns; "late": 500 more new
    texts, then two new texts and `again` by turns, so `again` is first
    met after the memo has refused others. `made` gives the new texts in
    order, none of them `again`.
    """
    cells = made[:bound]
    taken = bound
    if case == "late":
        cells = cells + made[taken : taken + 500]
        taken = taken + 500
    turn = 0
    while len(cells) < rows:
        if case == "prefix" or (case == "interleaved" and turn % 2 == 1) or (case == "late" and turn % 3 == 2):
            cells += [again]
        else:
            cells += [made[taken]]
            taken = taken + 1
        turn = turn + 1
    return cells


def _numbers(count: int) -> "list[str]":
    return [f"{100000 + k}" for k in range(count)]


def _days(count: int) -> "list[str]":
    first = datetime.date(1800, 1, 1).toordinal()
    return [datetime.date.fromordinal(first + k).isoformat() for k in range(count)]


_CASES = ("prefix", "interleaved", "late")


@pytest.mark.parametrize("case", _CASES)
def test_past_the_bound_a_text_met_again_shares_one_record(case: str) -> None:
    """Codex's review: 65,536 different numbers and then "70000" made a record a row on d4b114d (200,000 for 65,537)."""
    bound = parsing.SPELLING_MEMO_TEXTS
    cells = _past_the_bound(case, bound + 20_000, bound, _numbers(bound + 20_000), _AGAIN)
    classified = taxonomy._classify_all(cells)
    assert _objects(classified) == len(set(cells)), case
    assert [one.text for one in classified[bound - 3 : bound + 40]] == cells[bound - 3 : bound + 40]
    tallied = taxonomy._tally(classified, len(cells), _SETTINGS)
    assert tallied.spellings_by_folded == {}
    assert tallied.folded_counts[_AGAIN] == cells.count(_AGAIN)


@pytest.mark.parametrize("case", _CASES)
def test_past_the_bound_a_date_met_again_shares_its_pair_and_day(case: str) -> None:
    """d4b114d made a date pair and a day number a row of the date met only past the bound."""
    bound = parsing.SPELLING_MEMO_TEXTS
    cells = _past_the_bound(case, bound + 20_000, bound, _days(bound + 20_000), "2024-01-05")
    found = taxonomy._matching_date_format(cells, _SETTINGS)
    assert found is not None
    good = found[1]
    assert len(good) == len(cells)
    assert _objects(good) == len(set(cells)), case
    details = {"resolution": taxonomy.RESOLUTION_DATE, "datetimes_read_at": taxonomy.READ_AT_LOCAL, "format": "iso-date", "all_at_midnight": False}
    days = taxonomy._census_days(details, good)
    assert _objects(days) == len(set(cells)), case


@pytest.mark.parametrize("case", _CASES)
def test_past_the_bound_a_stamp_met_again_keeps_its_pair_and_one_key(
    case: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The offsets keep the shared pair, and the ordered moments make one key per moment past the bound.

    d4b114d made a pair and a key a row of the moment met only past the
    bound: about 100 bytes a row it adds where that is every added row.
    """
    bound = parsing.SPELLING_MEMO_TEXTS
    start = datetime.datetime(2020, 1, 1)
    made = [(start + datetime.timedelta(seconds=k)).isoformat() + "+01:00" for k in range(bound + 40_000)]
    keys = parsing.instant_key
    asked: "list[int]" = [0]

    def counted(canonical: str, offset: str) -> "int | None":
        asked[0] = asked[0] + 1
        return keys(canonical, offset)

    held: "list[float]" = []
    for rows in (bound + 10_000, bound + 40_000):
        cells = _past_the_bound(case, rows, bound, made, "2024-01-05T09:15:00-05:00")
        found = taxonomy._matching_date_format(cells, _SETTINGS)
        assert found is not None
        good = found[1]
        assert _objects(good) == len(set(cells)), case
        offsets: "dict[str, int]" = {}
        for _canonical, offset in good:
            offsets[offset] = (offsets[offset] if offset in offsets else 0) + 1
        kept = taxonomy._offsets_as_published(good, offsets)
        assert all(kept[place] is good[place] for place in range(len(good)))
        monkeypatch.setattr(parsing, "instant_key", counted)
        asked[0] = 0
        taxonomy.ordered_moments(good, taxonomy.READ_AT_LOCAL)
        assert asked[0] == len(set(cells)), case
        monkeypatch.setattr(parsing, "instant_key", keys)
        taxonomy.ordered_moments(good[:100], taxonomy.READ_AT_LOCAL)
        tracemalloc.start()
        try:
            before = tracemalloc.get_traced_memory()[0]
            tracemalloc.reset_peak()
            ordered = taxonomy.ordered_moments(good, taxonomy.READ_AT_LOCAL)
            held += [tracemalloc.get_traced_memory()[1] - before]
        finally:
            tracemalloc.stop()
        assert len(ordered[0]) == len(cells)
    if case == "prefix":
        per_row = (held[1] - held[0]) / 30_000
        assert per_row < 60, (case, per_row)


def test_past_the_bound_the_survey_holds_one_text_per_spelling(tmp_path: pathlib.Path) -> None:
    bound = parsing.SPELLING_MEMO_TEXTS
    made = _numbers(bound + 20_000)
    columns = [_past_the_bound(case, bound + 20_000, bound, made, _AGAIN) for case in _CASES]
    text = "prefix,interleaved,late\n" + "".join(f"{a},{b},{c}\n" for a, b, c in zip(*columns))
    table = reading.read_table(str(fixtures.write(tmp_path, "past.csv", text)))
    for place, cells in enumerate(columns):
        assert table.columns[place] == cells
        assert _objects(table.columns[place]) == len(set(cells)), _CASES[place]


def test_the_note_of_texts_met_once_turns_over_at_its_bound() -> None:
    noted = parsing.SPELLING_MEMO_NOTED
    assert noted == 8192
    assert parsing.memo_notes(0)
    assert parsing.memo_notes(noted - 1)
    assert not parsing.memo_notes(noted)


def test_a_text_met_again_within_the_note_s_bound_is_shared_and_one_further_apart_is_not(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Past the bound a text is taken where it is met again before `SPELLING_MEMO_NOTED` other new texts."""
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 64)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", 16)
    made = _numbers(2_000)
    for gap, shared in ((15, True), (16, True), (40, False)):
        cells = made[:64]
        taken = 64
        while len(cells) < 1_000:
            cells = cells + [_AGAIN] + made[taken : taken + gap]
            taken = taken + gap
        classified = taxonomy._classify_all(cells)
        assert classified == [taxonomy._classify(one) for one in cells]
        records = {id(classified[place]) for place in range(len(cells)) if cells[place] == _AGAIN}
        assert (len(records) == 1) == shared, (gap, len(records))


def _profile_files(folder: pathlib.Path, table: pathlib.Path, floor: int) -> "dict[str, bytes]":
    out = folder / f"out-{floor}"
    out.mkdir()
    assert kpi_shapes.quiet_cli(["profile", str(table), "--out-dir", str(out), "--smallest-group", str(floor)]) == 0
    return {path.name: path.read_bytes() for path in sorted(out.iterdir())}


def test_past_the_bound_every_file_is_the_bytes_written_with_nothing_shared(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The three cases of numbers, days and stamps with offsets, at floors 1, 11 and 36, with a bound of 2,048 and a note of 64."""
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 2_048)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", 64)
    rows = 6_000
    start = datetime.datetime(2020, 1, 1)
    stamps = [(start + datetime.timedelta(minutes=k)).isoformat() + "+01:00" for k in range(rows)]
    columns: "dict[str, list[str]]" = {}
    for case in _CASES:
        columns[f"n_{case}"] = _past_the_bound(case, rows, 2_048, _numbers(rows), _AGAIN)
        columns[f"d_{case}"] = _past_the_bound(case, rows, 2_048, _days(rows), "2024-01-05")
        columns[f"s_{case}"] = _past_the_bound(case, rows, 2_048, stamps, "2024-01-05T09:15:00-05:00")
    names = sorted(columns)
    text = ",".join(names) + "\n" + "".join(",".join(columns[name][row] for name in names) + "\n" for row in range(rows))
    table = fixtures.write(tmp_path, "past.csv", text)
    shared: "dict[int, dict[str, bytes]]" = {}
    (tmp_path / "shared").mkdir()
    for floor in (1, 11, 36):
        shared[floor] = _profile_files(tmp_path / "shared", table, floor)
    monkeypatch.setattr(parsing, "memo_takes", lambda held, answered: False)
    monkeypatch.setattr(parsing, "memo_notes", lambda noted: False)
    (tmp_path / "alone").mkdir()
    for floor in (1, 11, 36):
        alone = _profile_files(tmp_path / "alone", table, floor)
        assert len(alone) >= 3, sorted(alone)
        assert alone == shared[floor], floor


def test_the_survey_shares_its_texts_on_lines_closed_by_a_trailing_delimiter(tmp_path: pathlib.Path) -> None:
    """Batch 4b's seam of lane S4d with lane R6 (`dialect.survey`).

    Lane R6 named the closing a line wrote `spelled`; lane S4d named each
    column's memo of texts `spelled` in the same function. Merged as
    written, the first closed line turned the memos into a word and the
    next cell's lookup raised; the closing is now `closing_now`.
    """
    lines = ["code;arm;"]
    for row in range(2_000):
        lines += [f"{1000001 + row % 50};{'north' if row % 3 else 'south'};"]
    path = fixtures.write(tmp_path, "closed.csv", "\n".join(lines) + "\n")
    table = reading.read_table(str(path))
    assert table.n_rows == 2_000
    assert table.columns[0][:3] == ["1000001", "1000002", "1000003"]
    assert table.columns[1][:3] == ["south", "north", "north"]
    assert _objects(table.columns[0]) == 50
    assert _objects(table.columns[1]) == 2
