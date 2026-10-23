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

import dataclasses
import datetime
import gc
import hashlib
import json
import math
import pathlib
import random
import tracemalloc
import types
import weakref

import pytest

import fixtures
import kpi_shapes
import stage4_as_built
from synthtwin import asking, calendar_rules, cli, parsing, profile, reading, taxonomy

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
    built, names = stage4_as_built.compiled(taxonomy, stage4_as_built.TALLY, "_tally")
    # 66bca69's record of the tally, its fields as that commit named them
    # (`folded_counts`, `spellings_by_folded`; lane H3's repair renamed
    # them when it keyed the labels by their first spellings).
    names["_Cells"] = types.SimpleNamespace
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
        "one way otherwise": [f"V{k:06d}" for k in range(300)] + ["ABC"] * 3,
    }


def test_every_label_s_spellings_are_the_map_66bca69_held() -> None:
    """`_label_spellings` answers every label with 66bca69's map, key order included, and holds only mixed labels."""
    as_built = _tally_as_built()
    for name, cells in _tally_shapes().items():
        classified = taxonomy._classify_all(cells)
        now = taxonomy._tally(classified, len(cells), _SETTINGS)
        before = as_built(classified, len(cells), _SETTINGS)  # type: ignore[operator]
        # Keyed by each label's first spelling since lane H3's repair (plan
        # P4-D423): the maps keyed by label are `_label_maps`'s, the same
        # key for key and in order, and each first spelling's are its label's.
        counts, mixed_now = taxonomy._label_maps(now)
        assert list(counts) == list(before.folded_counts), name
        assert counts == before.folded_counts, name
        for label in before.folded_counts:
            answered = taxonomy._label_spellings(counts, mixed_now, label)
            assert list(answered.items()) == list(before.spellings_by_folded[label].items()), (name, label)
        mixed = {label for label in before.spellings_by_folded if list(before.spellings_by_folded[label]) != [label]}
        assert set(mixed_now) == mixed, name
        for first in now.label_counts:
            label = parsing.folded(first)
            assert list(taxonomy._rep_spellings(now, first).items()) == list(before.spellings_by_folded[label].items())
            assert list(before.spellings_by_folded[label])[0] == first, (name, first)
        assert len(now.label_spellings) == sum(1 for label in before.spellings_by_folded if len(before.spellings_by_folded[label]) > 1)


def test_a_column_of_plain_labels_holds_no_map_of_spellings() -> None:
    """66bca69 held one map per label: 100,000 maps on 100,000 different numbers."""
    cells = [f"{k}" for k in range(100_000)]
    tallied = taxonomy._tally(taxonomy._classify_all(cells), len(cells), _SETTINGS)
    assert tallied.label_spellings == {}
    assert len(tallied.label_counts) == 100_000


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


def test_the_census_reading_is_let_go_in_the_description_an_answer_rebuilds(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The description rebuilt after an answer on the screen lets each reading go too (plan P4-D390).

    `synthtwin profile` describes the table a second time once a person
    answers a question on the screen (cli.py's second `build_document`
    call). 68dae22f handed that call `readings=_handed_once(census_box)`
    as well, so on 3.10 both descriptions held their reading to the end.
    The same argument-holding wrapper as above stands in for 3.10's
    caller in BOTH descriptions. Red on 68dae22f (`[[True, True],
    [True, True]]`) and on a second site that keeps the readings bound
    in the caller during its call (`[[False, False], [True, True]]`).
    """
    draw = random.Random(8)
    lines = ["subject_id,arm,score"]
    for _ in range(3_000):
        lines += [f"{100000 + draw.randrange(300)},{draw.choice(['a', 'b'])},{draw.gauss(50, 9):.1f}"]
    path = fixtures.write(tmp_path, "register.csv", "\n".join(lines) + "\n")
    described = taxonomy.profile_column
    built = profile.build_document
    runs: "list[tuple[list[weakref.ref[taxonomy.HeldReading]], list[bool]]]" = []

    def watched(*args: object, **kwargs: object) -> taxonomy.ColumnProfile:
        handed, alive_later = runs[-1]
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
        nonlocal runs
        runs += [([], [])]
        return built(*args, **kwargs)  # type: ignore[arg-type]

    answers = iter([asking.ANSWER_IDENTIFIER])
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    monkeypatch.setattr(cli, "_read_one_answer", lambda standing: next(answers, ""))
    monkeypatch.setattr(taxonomy, "profile_column", watched)
    monkeypatch.setattr(profile, "build_document", holding)
    assert kpi_shapes.quiet_cli(["profile", str(path), "--out-dir", str(tmp_path)]) == 0
    assert len(runs) == 2, "premise: the answer on the screen rebuilt the description"
    assert [len(handed) for handed, _ in runs] == [1, 1], "premise: each census handed its reading over"
    assert [alive for _, alive in runs] == [[False, False], [False, False]]


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
    assert tallied.label_spellings == {}
    assert tallied.label_counts[_AGAIN] == cells.count(_AGAIN)


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


# -- lane H3: a column whose values all differ, and free text (plan P4-D423) -----
#
# Measured first on 4682d6ad, by line (`planning-notes/work-2026-10/wave6/H3/`):
# describing one column of 20,000 different record numbers written `V` and nine
# figures held 935 traced bytes a row above its cells, eight figures 502, stamps
# to the second 584 and 60-word notes 290: a record of ten fields a cell (112
# bytes) with its exact number (166), a second record a core, the set of every
# spelling the tally made (105), a triple a cell in the width censuses, a pair,
# a key and a day number a stamp, a map of every note. Each now holds what its
# description publishes and the next decision reads, in fewer objects; the
# answers are the oracles' (`stage4_as_built`), and every description of the
# lane's shapes is 4682d6ad's bytes.

_H3_WORDS = ["pain", "stable", "denies", "fever", "chest", "follow", "up", "noted",
             "history", "of", "mild", "acute", "no", "change", "plan", "continue"]


def _h3_values(shape: str, rows: int) -> "list[str]":
    """Made-up columns whose values all differ: record numbers, eight figures, stamps, 60-word notes."""
    draw = random.Random(11)
    base = datetime.datetime(2019, 1, 1)
    made: "list[str]" = []
    for row in range(rows):
        if shape == "rec":
            made += [f"V{(row * 2654435761) % 10 ** 9:09d}"]
        elif shape == "num":
            made += [f"{(row * 48271 + 12345) % 10 ** 8:08d}"]
        elif shape == "stamp":
            moment = base + datetime.timedelta(seconds=row * 97 + draw.randrange(97))
            made += [moment.strftime("%Y-%m-%dT%H:%M:%S")]
        else:
            made += [" ".join(draw.choice(_H3_WORDS) for _ in range(60))]
    return made


def _h3_traced_a_row(values: "list[str]", monkeypatch: pytest.MonkeyPatch) -> float:
    """The most `tracemalloc` sees held above the column's own cells while it is described, a row.

    THE MEMOS HELD TO 1,024 TEXTS: each holds at most 65,536 texts a column
    (`parsing.SPELLING_MEMO_TEXTS`, `taxonomy.LAYOUT_MEMO_TEXTS`), a fixed few
    megabytes at 2,000,000 rows, where at 20,000 rows they would hold every
    text and be counted a row. Held lower here, the bytes counted are the ones
    a row adds past them, which is what a column of 2,000,000 rows holds.
    """
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", 1_024)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", 128)
    monkeypatch.setattr(taxonomy, "LAYOUT_MEMO_TEXTS", 1_024)
    taxonomy.profile_column("warm", 1, values[:200], 200, _SETTINGS)
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        taxonomy.profile_column("column", 1, values, len(values), _SETTINGS)
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    return held / len(values)


# Each bound over the measured bytes a row (Python 3.11: 418 and 428, 170 and
# 177, 431 and 435 at 20,000 and 40,000 rows, notes 142 at 4,000; Python 3.13:
# 402 and 412, 169 and 176, 414 and 419, notes 149 and 141 at 2,000 and 4,000),
# against 824, 503 and 587 at 20,000 rows and 270 for notes at 4,000 rows on
# 4682d6ad (Python 3.11), its memos held as here. LOWERED BY THE LANE'S REPAIR
# (plan P4-D423) from 470 to 400 for record numbers and stamps: 339.4 and
# 344.7, 342.0 and 342.9 on Python 3.11, with no folded copy of a label written
# in capitals and no unit, set or pair a stamp counted.
@pytest.mark.parametrize("rows", [20_000, 40_000])
@pytest.mark.parametrize(("shape", "bound"), [("rec", 400), ("num", 200), ("stamp", 400)])
def test_a_column_whose_values_all_differ_holds_under_its_bound_a_row(
    shape: str, bound: int, rows: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    per_row = _h3_traced_a_row(_h3_values(shape, rows), monkeypatch)
    assert per_row < bound, (shape, rows, per_row)


# THE NOTES AT 2,000 AND 4,000 ROWS, not 20,000 and 40,000: `tracemalloc` makes
# describing free text about ten times slower (0.53 ms a 60-word note without
# it, about 5 with it), and 60,000 traced notes are five minutes of one test;
# the bytes a row are the same past the memos (148.7 at 2,000 rows, 140.6 at
# 4,000, 130.5 at 20,000, measured).
@pytest.mark.parametrize("rows", [2_000, 4_000])
def test_a_column_of_sixty_word_notes_holds_under_two_hundred_bytes_a_row(
    rows: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    per_row = _h3_traced_a_row(_h3_values("note", rows), monkeypatch)
    assert per_row < 200, (rows, per_row)


def _h3_texts() -> "list[str]":
    draw = random.Random(17)
    alphabet = list("0123456789.+-eE() ,'") + ["−", "’", " ", " ", " ", "\t", "x", "V", "T", "%", "$", "_"]
    made = ["42", "-42", "+42", "0", "-0", "0.0", "(0)", "3.5", "-3.5", "(1,234.50)", "1,234,567.89", "  7  ", "1e5", "0e5",
            "1e999", "-1e999", "(1e999)", "1e-999", "-1e-999", "(-5)", "(+5)", "(-a)", "abc", "12mg", "V000123", "Yes", " no",
            "2019-01-01T10:00:00", "1,5", "-1,5", "1.234,5", "−6.09", "1,483.65-", "0.10000000000000000001"]
    for _ in range(3_000):
        made += ["".join(draw.choice(alphabet) for _ in range(draw.randint(1, 10)))]
    return made


def test_a_record_answers_every_field_the_record_of_ten_fields_held() -> None:
    """Three slots and a shared entry of answers: every field reads what 4682d6ad's record held, on any text."""
    built, _names = stage4_as_built.compiled(taxonomy, stage4_as_built.RECORD_OF_TEN, "_classify")
    fields = ("text", "numeric_text", "kind", "value", "exact", "sign", "whole", "folded", "all_digits", "code_alphabet")
    for comma in (False, True):
        for text in _h3_texts():
            now = taxonomy._classify(text, comma)
            before = built(text, comma)  # type: ignore[operator]
            for field in fields:
                assert getattr(now, field) == getattr(before, field), (text, comma, field)
            if now.value is not None:
                assert math.copysign(1.0, now.value) == math.copysign(1.0, getattr(before, "value")), text
            assert now == taxonomy._classify(text, comma) and hash(now) == hash(taxonomy._classify(text, comma))
    assert taxonomy._classify("1000001").folded is taxonomy._classify("1000001").text
    assert len(taxonomy._CELL_FACTS) == 4 * 4 * 3 * 2 * 2 * 2


def _h3_number_columns() -> "dict[str, list[str]]":
    draw = random.Random(23)
    near = ["0.1", "0.10000000000000000001", "0.1000000000000000000000001", "0.3", "0.30000000000000000002"]
    return {
        "all different": [f"{(k * 48271 + 12345) % 10 ** 8:08d}" for k in range(5_000)],
        "near numbers": [draw.choice(near + [f"{draw.randint(1, 40)}"]) for _ in range(3_000)],
        "zeros plus last": ["-0"] * 30 + [f"{1 + k % 40}" for k in range(200)] + ["0"] * 15,
        "zeros minus last": ["0"] * 30 + [f"{1 + k % 40}" for k in range(200)] + ["-0"] * 15,
        "ties": [draw.choice(["7", "8", "7.0", "8.00", "9", "10"]) for _ in range(3_000)],
        "tied near": ["0.1"] * 20 + ["0.10000000000000000001"] * 20 + ["0.2"] * 20,
        "stand-ins": [draw.choice(["-999", "-999.0", "9999", "-999.00000000000001", f"{draw.gauss(80, 10):.2f}"]) for _ in range(3_000)],
        "words and numbers": [draw.choice(["n/a", "x", f"{draw.randint(1, 9)}", "1e999"]) for _ in range(2_000)],
        "no numbers": ["a", "b", "c"] * 50,
    }


def test_the_exact_numbers_are_counted_as_the_map_of_every_exact_number_counted() -> None:
    """`_distinct_numbers` and `_mode_of` count off the sorted values what 4682d6ad's map keyed by each exact number counted."""
    distinct, names = stage4_as_built.compiled(taxonomy, stage4_as_built.EXACT_MAPS, "_distinct_numbers")
    mode = names["_mode_of"]
    for name, cells in _h3_number_columns().items():
        for comma in (False, True):
            tallied = taxonomy._tally(taxonomy._classify_all(cells, comma), len(cells), _SETTINGS, comma)
            assert taxonomy._distinct_numbers(tallied) == distinct(tallied), (name, comma)  # type: ignore[operator]
            now, before = taxonomy._mode_of(tallied), mode(tallied)
            assert now == before, (name, comma)
            if now[0] is not None:
                assert math.copysign(1.0, now[0]) == math.copysign(1.0, before[0]), (name, comma)
            assert taxonomy._exact_count(tallied.classified) == distinct(tallied), (name, comma)  # type: ignore[operator]
            assert tallied.raw_distinct == len(set(tallied.present)), (name, comma)


def test_the_tally_s_counts_are_the_counts_of_every_spelling() -> None:
    """The different spellings and the shape of repetition are read off the tally's maps, as every spelling counted them."""
    shapes = dict(_tally_shapes())
    shapes["notes"] = _h3_values("note", 300) + _h3_values("note", 100)
    shapes["records"] = _h3_values("rec", 2_000)
    for name, cells in shapes.items():
        tallied = taxonomy._tally(taxonomy._classify_all(cells), len(cells), _SETTINGS)
        assert tallied.raw_distinct == len(set(cells)), name
        assert taxonomy._spellings_by_occurrences(tallied) == taxonomy._n_distinct_by_occurrences(cells), name


def test_the_moments_and_days_are_the_oracles() -> None:
    """Moments ordered by their sorted texts, and days held one number a day, are 4682d6ad's sequences."""
    keyed, _names = stage4_as_built.compiled(taxonomy, stage4_as_built.MOMENTS_KEYED, "ordered_moments")
    by_row, _names = stage4_as_built.compiled(taxonomy, stage4_as_built.DAYS_A_ROW, "_census_days")
    draw = random.Random(29)
    stamps = _h3_values("stamp", 3_000)
    mixed = [draw.choice(["2024-01-05", "2024-01-05 00:00:00", "2024-01-05 09:15:00", "2023-12-31 23:59:59"]) for _ in range(500)]
    offsets = [cell[:19].replace("T", " ") + cell[19:] for cell in _date_cells(2_000, offsets=True)]
    for name, pairs in (
        ("stamps", [(cell.replace("T", " "), "") for cell in stamps]),
        ("dates", [(cell, "") for cell in _date_cells(3_000)]),
        ("dates beside the day's first second", [(cell, "") for cell in mixed]),
        ("with offsets", [(cell[:19], cell[19:]) for cell in offsets]),
    ):
        for read_at in (taxonomy.READ_AT_LOCAL, taxonomy.READ_AT_UTC):
            assert taxonomy.ordered_moments(pairs, read_at) == keyed(pairs, read_at), (name, read_at)  # type: ignore[operator]
        details = {"resolution": taxonomy.RESOLUTION_DATETIME, "datetimes_read_at": taxonomy.READ_AT_LOCAL, "format": "iso-datetime", "all_at_midnight": False}
        days = taxonomy._census_days(details, pairs)
        assert days == by_row(details, pairs), name  # type: ignore[operator]
        assert _objects(days) <= len({day for day in days}), name
    ordinals = [3, 3, 5, 9, 9, 9, 12]
    assert taxonomy._different_ordinals(ordinals) == 4 and taxonomy._different_ordinals([5, 3, 3]) == 2
    assert taxonomy._sorted_runs([-0.0, 0.0, 1.0, 1.0, 2.5]) == len({-0.0, 0.0, 1.0, 2.5})
    assert taxonomy._end_run([1.0, 1.0, 2.0], 0) == 2 and taxonomy._end_run([1.0, 2.0, 2.0, 2.0], 3) == 3


def test_a_text_no_number_is_written_with_is_answered_as_its_reading_answered(monkeypatch: pytest.MonkeyPatch) -> None:
    """The alphabet's answer is the reading's: every text read with the shortcut and without it answers alike."""
    texts = _h3_texts() + _h3_values("note", 50)
    shortcut = [(parsing.classify_number(text), parsing.parse_number(text), parsing.number_out_of_range(text)) for text in texts]
    monkeypatch.setattr(parsing, "_outside_number_alphabet", lambda body: False)
    walked = [(parsing.classify_number(text), parsing.parse_number(text), parsing.number_out_of_range(text)) for text in texts]
    assert shortcut == walked
    split, _names = stage4_as_built.compiled(taxonomy, stage4_as_built.SPLIT_A_CHARACTER_AT_A_TIME, "splits_into_numbers")
    for text in texts + ["120/80", "1:1.5", "1::2", ":::", "3 / 4 / 5", "12-12-"]:
        for separator in ("/", ":", "::", " / ", "-", "e"):
            assert taxonomy.splits_into_numbers(text, separator) == split(text, separator), (text, separator)  # type: ignore[operator]


# Each digest is 4682d6ad's (`planning-notes/work-2026-10/wave6/H3/digests.py`).
_H3_DIGESTS = {
    "11": "47d047c1d0cee5d3d8316bcc1dc04fc428a5e3b25bbf9b549ebd20d400df4b44",
    "1": "c31157a791e551698c671cf7bd74a9e4877ee04b76816224726ea3d4485d7d48",
    "11-groups": "47d047c1d0cee5d3d8316bcc1dc04fc428a5e3b25bbf9b549ebd20d400df4b44",
}


def _h3_document_digest(folder: pathlib.Path, floor: int, grouped: bool, monkeypatch: pytest.MonkeyPatch) -> str:
    draw = random.Random(37)
    rows = 1_500
    columns = {
        "rec": _h3_values("rec", rows),
        "num": _h3_values("num", rows),
        "stamp": _h3_values("stamp", rows),
        "note": _h3_values("note", rows),
        "zeros": [draw.choice(["0", "-0", "0.0", "-0.0", "1", "2", "3"]) for _ in range(rows)],
        "near": [draw.choice(["0.1", "0.10000000000000000001", "0.3", "0.30000000000000000002", f"{draw.randint(1, 40)}"]) for _ in range(rows)],
        "stand_ins": [draw.choice(["-999", "-999.0", "9999", f"{draw.gauss(80, 10):.2f}", f"{draw.gauss(80, 10):.2f}"]) for _ in range(rows)],
        "padded": [draw.choice([f"{draw.randint(0, 999):04d}", f"+{draw.randint(0, 99):03d}", f"{draw.randint(1, 99999)}"]) for _ in range(rows)],
        "decimals": [f"{draw.randint(0, 99)}.{draw.randint(0, 10 ** draw.randint(1, 6) - 1)}" for _ in range(rows)],
        "affixed": [draw.choice(["-999 mg", f"{draw.randint(1, 900)} mg", f"{draw.randint(1, 900)}.5 mg"]) for _ in range(rows)],
        "label": [draw.choice(["Yes", "yes", "YES", " no", "No", "maybe"]) for _ in range(rows)],
    }
    names = sorted(columns)
    text = ",".join(names) + "\n" + "".join(",".join(columns[name][row] for name in names) + "\n" for row in range(rows))
    path = fixtures.write(folder, "lane-h3.csv", text)
    if grouped:
        monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    settings = taxonomy.Settings(small_cell_floor=floor)
    table = reading.read_table(str(path), small_cell_floor=floor, in_groups=grouped)
    document = profile.build_document(table, settings, [], ["num"])
    # The description names no path, so its text is the same on every machine.
    written = json.dumps(document, sort_keys=True)
    return hashlib.sha256(written.encode("utf-8")).hexdigest()


@pytest.mark.parametrize("case", sorted(_H3_DIGESTS))
def test_every_description_of_the_lane_s_shapes_is_the_bytes_4682d6ad_wrote(
    case: str, tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    floor = int(case.split("-")[0])
    assert _h3_document_digest(tmp_path, floor, case.endswith("groups"), monkeypatch) == _H3_DIGESTS[case]


# -- lane H3's repair (plan P4-D423): the skeptics' shapes and their oracles -----
#
# Measured on 34bb5902 by the lane's two skeptics (wave6/H3-sk1.md, H3-stat.md):
# the K-S4-09 table's own stamps -- `MM/DD/YYYY hh:mm AM` (`check_at`, its
# binding column) and `M/D/YYYY H:MM` (`order_at`) -- held 732 and 604 traced
# bytes a row, through the slashed stamps' one written clock (a tuple of halves,
# parts and pairs a stamp); stamps with offsets 620; notes that begin with a
# capital 565, and notes of a large vocabulary holding a dose and a date 1,343,
# through a folded copy of every label and a map of every affix pair. Each now
# counts what its description publishes; every answer is 4682d6ad's oracles'.


def _h3_repair_values(shape: str, rows: int) -> "list[str]":
    """The skeptics' shapes: the mixed table's two slashed stamp forms, stamps with offsets, and three kinds of note."""
    draw = random.Random(11)
    base = datetime.datetime(2019, 1, 1)
    made: "list[str]" = []
    vocabulary: "list[str]" = []
    weights: "list[float]" = []
    if shape in ("biglower", "bignote"):
        vocabulary = sorted(
            {"".join(draw.choice("abcdefghijklmnoprstuvwy") for _ in range(draw.randint(3, 11))) for _ in range(30_000)}
        )
        weights = [1.0 / (rank + 1) for rank in range(len(vocabulary))]
    for _row in range(rows):
        if shape in ("twelve", "mdy", "stampoff"):
            at = base + datetime.timedelta(seconds=_row * 97 + draw.randrange(97))
            if shape == "twelve":
                hour = at.hour % 12 or 12
                made += [f"{at.month:02d}/{at.day:02d}/{at.year} {hour:02d}:{at.minute:02d} {'AM' if at.hour < 12 else 'PM'}"]
            elif shape == "mdy":
                made += [f"{at.month}/{at.day}/{at.year} {at.hour}:{at.minute:02d}"]
            else:
                made += [at.strftime("%Y-%m-%dT%H:%M:%S") + draw.choice(["Z", "+01:00", "-05:00"])]
        elif shape == "notecap":
            made += [" ".join(draw.choice(_H3_WORDS) for _ in range(60)).capitalize()]
        else:
            words = draw.choices(vocabulary, weights, k=60)
            words[draw.randrange(60)] = f"{draw.randint(1, 400)}mg"
            words[draw.randrange(60)] = f"{draw.randint(1, 12)}/{draw.randint(1, 28)}/2024"
            note = " ".join(words)
            made += [note.capitalize() if shape == "bignote" else note]
    return made


def _h3_repair_traced_a_row(values: "list[str]", monkeypatch: pytest.MonkeyPatch, memo: int) -> float:
    """`_h3_traced_a_row` with the memos held to ``memo`` texts (and their note to an eighth of it)."""
    monkeypatch.setattr(parsing, "SPELLING_MEMO_TEXTS", memo)
    monkeypatch.setattr(parsing, "SPELLING_MEMO_NOTED", max(8, memo // 8))
    monkeypatch.setattr(taxonomy, "LAYOUT_MEMO_TEXTS", memo)
    taxonomy.profile_column("warm", 1, values[:200], 200, _SETTINGS)
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        taxonomy.profile_column("column", 1, values, len(values), _SETTINGS)
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    return held / len(values)


def _h3_stamp_columns() -> "dict[str, tuple[list[str], tuple[str, ...]]]":
    """Slashed stamps on every face and width the one written clock reads, each with the declared absences it is asked under."""
    draw = random.Random(31)
    base = datetime.datetime(2021, 6, 1)
    moments = [base + datetime.timedelta(minutes=row * 37 + draw.randrange(37)) for row in range(900)]

    def marked(moment: datetime.datetime, two: bool, marks: "tuple[str, str]" = ("AM", "PM"), space: str = " ") -> str:
        hour = moment.hour % 12 or 12
        shown = f"{hour:02d}" if two else f"{hour}"
        return f"{moment.month:02d}/{moment.day:02d}/{moment.year} {shown}:{moment.minute:02d}{space}{marks[0] if moment.hour < 12 else marks[1]}"

    def plain(moment: datetime.datetime, two: bool, seconds: bool = False) -> str:
        shown = f"{moment.hour:02d}" if two else f"{moment.hour}"
        tail = f":{moment.second:02d}" if seconds else ""
        return f"{moment.month}/{moment.day}/{moment.year} {shown}:{moment.minute:02d}{tail}"

    early = datetime.datetime(2021, 6, 1, 1, 5)
    later = datetime.datetime(2021, 6, 2, 2, 10)
    widths = [marked(early, False), marked(later, True)] + [marked(moment, draw.random() < 0.8) for moment in moments]
    unmarked = [plain(early, False)] + [plain(moment, draw.random() < 0.7) for moment in moments]
    return {
        "marked": ([marked(moment, True) for moment in moments], ()),
        "marked one figure": ([marked(moment, False) for moment in moments], ()),
        "marked widths": (widths, ()),
        "marked widths, the rewrite absent": (widths, (marked(early, True),)),
        "marked widths, both widths absent": (widths, (marked(early, True), marked(later, False))),
        "lower and dotted faces": ([marked(moment, True, draw.choice([("AM", "PM"), ("am", "pm"), ("a.m.", "p.m.")]), draw.choice([" ", ""])) for moment in moments], ()),
        "unmarked": ([plain(moment, False) for moment in moments], ()),
        "unmarked padded": ([plain(moment, True) for moment in moments], ()),
        "unmarked widths": (unmarked, ()),
        "unmarked widths, the rewrite absent": (unmarked, (plain(early, True),)),
        "unmarked seconds": ([plain(moment, draw.random() < 0.5, True) for moment in moments], ()),
        "faces mixed": ([draw.choice([marked(moment, True), plain(moment, True)]) for moment in moments], ()),
    }


def test_the_one_written_clock_of_slashed_stamps_is_4682d6ad_s() -> None:
    """Counted by hour, figures and face, the clock keeps and writes every stamp as 4682d6ad's halves and parts a stamp did."""
    _built, names = stage4_as_built.compiled(taxonomy, stage4_as_built.STAMP_CLOCK, "_stamp_clocks")
    twelve = taxonomy.Settings(forced_twelve_hour_clocks=(taxonomy.TWELVE_HOUR_HERE,))
    for name, (cells, absent) in _h3_stamp_columns().items():
        for settings in (_SETTINGS, twelve):
            settings = dataclasses.replace(settings, declared_missing_values=absent)
            for member in parsing.SLASHED_STAMPS:
                parsed = [parsing.parse_datetime(cell, member) is not None for cell in cells]
                now = taxonomy._on_the_written_clock(cells, list(parsed), settings)
                assert now == names["_on_the_written_clock"](cells, list(parsed), settings), (name, member)  # type: ignore[operator]
                good = [pair for pair in (parsing.parse_datetime(cell, member) for cell in cells) if pair is not None]
                sources = [cell for cell in cells if parsing.parse_datetime(cell, member) is not None]
                kept = taxonomy._stamp_clocks(good, sources, settings)
                assert kept == names["_stamp_clocks"](good, sources, settings), (name, member)  # type: ignore[operator]


def test_the_clock_style_of_a_census_is_the_style_of_every_clock() -> None:
    """`_clock_style_of_census` is `parsing.clock_style_of_cells` of the clocks the census counts."""
    draw = random.Random(43)
    faces = list(parsing.CLOCK_FACES) + ["?"]
    for _case in range(400):
        read = []
        for _cell in range(draw.randint(0, 40)):
            face = draw.choice(faces)
            hour = draw.randint(0, 23) if not face else draw.randint(1, 12)
            read += [(hour, draw.randint(0, 59), draw.randint(0, 59), draw.random() < 0.5, draw.choice([1, 2]), face, draw.random() < 0.5)]
        census: "dict[tuple[int, int, str], int]" = {}
        for parts in read:
            key = (parts[0], parts[4], parts[5])
            census[key] = census.get(key, 0) + 1
        for twelve_hour in (False, True):
            assert taxonomy._clock_style_of_census(census, twelve_hour) == parsing.clock_style_of_cells(read, twelve_hour)


def test_written_units_are_counted_along_the_instants_as_the_set_counts_them() -> None:
    """`_different_units`, `calendar_rules.few_units` counting run by run, and the units `_written_units` hands it, answer as the set of every unit did."""
    _built, names = stage4_as_built.compiled(calendar_rules, stage4_as_built.FEW_UNITS, "few_units")
    old = names["few_units"]
    draw = random.Random(47)
    for _case in range(120):
        instants = sorted(draw.randrange(0, 86_400 * 400) for _ in range(draw.randint(1, 400)))
        if draw.random() < 0.3:
            instants = [instant - instant % 86_400 for instant in instants]
        elif draw.random() < 0.3:
            instants = [instant - instant % 60 for instant in instants]
        body = [instant // 86_400 for instant in instants]
        if draw.random() < 0.2:
            draw.shuffle(instants)
        groups, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), 2)
        for step in (1, 60, 86_400):
            units = [instant // step for instant in instants]
            assert taxonomy._different_units(tuple(instants), step) == len(set(units))
            if groups:
                expected = old(groups, body, units)  # type: ignore[operator]
                assert calendar_rules.few_units(groups, body, units) == expected
                assert calendar_rules.few_units(groups, body, taxonomy._written_units(tuple(instants), body, step)) == expected
                assert calendar_rules.few_units(groups, body[: len(body) // 2], units) == old(groups, body[: len(body) // 2], units)  # type: ignore[operator]


def test_written_units_out_of_order_are_counted_as_the_set_counts_them_and_none_is_held() -> None:
    """Units met again after another are one unit (the run count alone counts them again); no list of them is made."""
    _built, names = stage4_as_built.compiled(calendar_rules, stage4_as_built.FEW_UNITS, "few_units")
    body = [day for day in range(14) for _row in range(20)]
    instants = [day * 86_400 + 3_600 * (place % 2) for place, day in enumerate(body)]
    groups, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(body), 2)
    assert groups
    assert calendar_rules.few_units(groups, body, instants) == names["few_units"](groups, body, instants) is True  # type: ignore[operator]
    ascending = tuple(sorted(range(0, 40_000 * 60, 60)))
    days = [instant // 86_400 for instant in ascending]
    assert taxonomy._written_units(ascending, days, 1) is ascending
    assert taxonomy._written_units(ascending, days, 60) is ascending
    midnights = tuple(day * 86_400 for day in days)
    assert taxonomy._written_units(midnights, days, 86_400) is days
    assert taxonomy._written_units(tuple(instant + 1 for instant in ascending), days, 60) == [(instant + 1) // 60 for instant in ascending]
    groups, _entry = calendar_rules.menu_groups(calendar_rules.body_bins(days), 2)
    gc.collect()
    tracemalloc.start()
    try:
        before = tracemalloc.get_traced_memory()[0]
        tracemalloc.reset_peak()
        calendar_rules.few_units(groups, days, taxonomy._written_units(ascending, days, 60))
        taxonomy._different_units(ascending, 60)
        held = tracemalloc.get_traced_memory()[1] - before
    finally:
        tracemalloc.stop()
    assert held < 2 * len(ascending), held


def _h3_affix_columns() -> "dict[str, list[str]]":
    draw = random.Random(53)
    notes = _h3_repair_values("bignote", 300)
    return {
        "notes with a dose and a date": notes,
        "notes in lower case": _h3_repair_values("biglower", 300),
        "units": [f"{draw.randint(1, 900)} {draw.choice(['mg', 'mg', 'mg', 'MG'])}" for _ in range(400)],
        "flagged": [draw.choice([f"{draw.randint(10, 99)}.{draw.randint(0, 9)}", f"{draw.randint(1, 9)}.{draw.randint(0, 9)} H", f"{draw.randint(1, 9)}.{draw.randint(0, 9)} L"]) for _ in range(400)],
        "feet and inches": [f"{draw.randint(4, 6)}'{draw.randint(0, 11)}\"" for _ in range(400)],
        "money": [draw.choice([f"${draw.randint(1, 99)}", f"EUR{draw.randint(1, 99)}"]) for _ in range(400)],
        "noun beside readings": [draw.choice([f"{draw.randint(1, 9)}.{draw.randint(0, 9)}", f"note {draw.randint(1, 9)}"]) for _ in range(400)],
        "prose": [f"free comment number {draw.randint(0, 99):02d} written out" if draw.random() < 0.5 else f"FREE COMMENT NUMBER {draw.randint(0, 99):02d} WRITTEN OUT" for _ in range(400)],
        "addresses": [f"user{draw.randint(1, 50)}@example.org" for _ in range(300)],
        "notes repeated": notes[:100] * 3,
        "a reading beside a few stragglers": [f"{draw.randint(1, 900)} mg" for _ in range(396)] + [f"odd {k} unit" for k in range(4)],
        "near the line": [f"{draw.randint(1, 900)} mg" for _ in range(394)] + [f"x{k} y" for k in range(6)],
    }


def _h3_affix_on_the_line() -> "list[str]":
    """1,000 cells proposing exactly as many pairs as a reading can stand on, and the reading standing, at a floor of 2.

    The categorical ceiling's 100 one-word units, each worn by 9 or 10
    cells, cover the parse line's 990 cells exactly, and the 10 cells left
    wear a pair each: 110 pairs, the most `_affixed_before_the_address_test`
    walks on with.
    """
    units = [f"u{chr(97 + k // 26)}{chr(97 + k % 26)}" for k in range(100)]
    cells: "list[str]" = []
    for place, unit in enumerate(units):
        for row in range(10 if place < 90 else 9):
            cells += [f"{row * 7 + place} {unit}"]
    for k in range(10):
        cells += [f"{k + 1} zq{chr(97 + k)}"]
    return cells


def test_the_affix_reading_stands_on_exactly_as_many_pairs_as_its_rules_allow() -> None:
    """At the bound's own line the reading stands, as 4682d6ad's map read it: the bound is no tighter than the rules."""
    _built, names = stage4_as_built.compiled(taxonomy, stage4_as_built.AFFIX_PAIRS, "affixed_reach")
    cells = _h3_affix_on_the_line()
    settings = taxonomy.Settings(small_cell_floor=2)
    tallied = taxonomy._tally(taxonomy._classify_all(cells), len(cells), settings)
    assert taxonomy._categorical_ceiling(tallied) == 100
    now = taxonomy._affixed_before_the_address_test(tallied)
    assert now is not None
    assert now == names["_affixed_before_the_address_test"](tallied)  # type: ignore[operator]
    one_more = taxonomy._tally(taxonomy._classify_all(cells + ["11 zqz"]), len(cells) + 1, settings)
    assert taxonomy._affixed_before_the_address_test(one_more) == names["_affixed_before_the_address_test"](one_more)  # type: ignore[operator]


@pytest.mark.parametrize("mask", [None, 3])
def test_the_affix_reading_and_its_reach_are_4682d6ad_s(mask: "int | None", monkeypatch: pytest.MonkeyPatch) -> None:
    """Bounded by the pairs a reading can stand on, and counted off one number a cell, the pair walk answers as its map did.

    ``mask`` 3 keeps two bits of each pair's hash, so most cells share a run
    with cells of other pairs, and every run is counted again exactly.
    """
    _built, names = stage4_as_built.compiled(taxonomy, stage4_as_built.AFFIX_PAIRS, "affixed_reach")
    if mask is not None:
        monkeypatch.setattr(taxonomy, "_HASH_MASK", mask)
    for name, cells in _h3_affix_columns().items():
        for floor in (1, 11):
            settings = taxonomy.Settings(small_cell_floor=floor)
            tallied = taxonomy._tally(taxonomy._classify_all(cells), len(cells), settings)
            for forced in (False, True):
                now = taxonomy._affixed_before_the_address_test(tallied, forced)
                assert now == names["_affixed_before_the_address_test"](tallied, forced), (name, floor, forced)  # type: ignore[operator]
            assert taxonomy.affixed_reach(tallied) == names["affixed_reach"](tallied), (name, floor)  # type: ignore[operator]


def _as_4682d6ad_tally(cells: "taxonomy._Cells") -> object:
    """The tally with 4682d6ad's two maps keyed by folded label, under their old names, beside every field it holds."""
    counts, mixed = taxonomy._label_maps(cells)
    fields = {field.name: getattr(cells, field.name) for field in dataclasses.fields(cells)}
    return types.SimpleNamespace(**fields, folded_counts=counts, spellings_by_folded=mixed)


def test_the_rules_reading_labels_answer_as_they_read_folded_labels() -> None:
    """Asked of the first spellings, four rules answer as 4682d6ad's asked of the folded labels."""
    _built, names = stage4_as_built.compiled(taxonomy, stage4_as_built.LABEL_READERS, "_published_distinct")
    draw = random.Random(59)
    shapes = dict(_tally_shapes())
    shapes["notes"] = _h3_values("note", 200) + _h3_values("note", 50)
    shapes["notes with capitals"] = _h3_repair_values("notecap", 300)
    shapes["record numbers"] = _h3_values("rec", 500)
    shapes["clocks beside rare words"] = [draw.choice(["07:00", "15:00", "19:00", "23:00"]) for _ in range(600)] + ["UNK", "Unk", "n/a", "N/A"] * 3
    shapes["levels and numbers"] = [draw.choice(["Yes", "yes", "NO", "12", "12.0", "7", "maybe", "MAYBE", "1E3", "1e3", " 12"]) for _ in range(800)]
    shapes["numbers written only in capitals"] = ["1E3"] * 40 + ["2E3"] * 40 + ["maybe"] * 40
    for name, cells in shapes.items():
        for floor in (1, 2, 11):
            settings = taxonomy.Settings(small_cell_floor=floor)
            classified = taxonomy._classify_all(cells)
            tallied = taxonomy._tally(classified, len(cells), settings)
            old = _as_4682d6ad_tally(tallied)
            for rule in ("_published_distinct", "_a_level_is_below_the_floor", "_floor_clearing_non_numeric"):
                assert getattr(taxonomy, rule)(tallied) == names[rule](old), (name, floor, rule)  # type: ignore[operator]
            now = taxonomy._rare_beside_clocks(tallied, classified, len(cells), settings, False)
            assert now == names["_rare_beside_clocks"](old, classified, len(cells), settings, False), (name, floor)  # type: ignore[operator]


def test_labels_whose_hashes_share_a_key_are_told_apart() -> None:
    """With two bits of each folded label's hash kept, the tally is 66bca69's, label for label."""
    as_built = _tally_as_built()
    shapes = dict(_tally_shapes())
    shapes["capitals"] = [f"Word{k % 700}" for k in range(1_400)] + [f"WORD{k}" for k in range(300)]
    with pytest.MonkeyPatch.context() as patched:
        patched.setattr(taxonomy, "_REFOLD_MASK", 3)
        for name, cells in shapes.items():
            classified = taxonomy._classify_all(cells)
            now = taxonomy._tally(classified, len(cells), _SETTINGS)
            before = as_built(classified, len(cells), _SETTINGS)  # type: ignore[operator]
            counts, mixed = taxonomy._label_maps(now)
            assert list(counts.items()) == list(before.folded_counts.items()), name
            for label in before.folded_counts:
                answered = taxonomy._label_spellings(counts, mixed, label)
                assert list(answered.items()) == list(before.spellings_by_folded[label].items()), (name, label)
            assert now.raw_distinct == before.raw_distinct, name


def test_folding_a_folded_label_leaves_it_as_it_is() -> None:
    """The tally finds a label's own first spelling by the label (`_tally`): a folded text folds to itself."""
    texts = [chr(point) for point in range(0x110000) if not 0xD800 <= point <= 0xDFFF]
    for text in texts + [" " + text + "x " for text in texts[::97]]:
        label = parsing.folded(text)
        assert parsing.folded(label) == label, repr(text)


def test_the_rewrites_no_battery_reaches_answer_as_their_oracles() -> None:
    """Skeptic 1's item 4: each guard of a rewrite asked where it decides, beside the oracle it stands for."""
    # Out of order, the ordinals are counted by the set, not by their runs.
    assert taxonomy._different_ordinals([3, 5, 3]) == 2 == len({3, 5, 3})
    # The tally's own count stands only for the very texts in their order.
    cells = ["a", "b", "c"]
    tallied = taxonomy._tally(taxonomy._classify_all(cells), 3, _SETTINGS)
    assert taxonomy._different_sources(tallied.present[:2], tallied) == 2
    assert taxonomy._different_sources(["x", "x", "x"], tallied) == 1
    assert taxonomy._different_sources(tallied.present, tallied) == 3
    # Texts whose instants fall along their order are ordered by instant.
    keyed, _names = stage4_as_built.compiled(taxonomy, stage4_as_built.MOMENTS_KEYED, "ordered_moments")
    falling = [("2024-01-05 10:59:99", ""), ("2024-01-05 10:60:00", ""), ("2024-01-05 10:59:99", "")]
    assert taxonomy._moments_by_text(falling) is None
    for read_at in (taxonomy.READ_AT_LOCAL, taxonomy.READ_AT_UTC):
        assert taxonomy.ordered_moments(falling, read_at) == keyed(falling, read_at)  # type: ignore[operator]
    assert taxonomy.ordered_moments(falling, taxonomy.READ_AT_LOCAL)[0][0] == "2024-01-05 10:60:00"
    # No value above nought is read off the largest, whatever the smallest is.
    for ordered in ([-3.0, -1.0, 2.0], [-3.0, 0.0], [-2.0, -1.0], [1.0], [-0.0, 0.0], [-5.0, 0.0, 0.0, 7.5]):
        assert taxonomy._none_above_nought(ordered) == (len([value for value in ordered if value > 0.0]) == 0), ordered
    # The texts handed to the tally stand only where they are the records' own.
    classified = taxonomy._classify_all(["1", "2", "3"])
    assert taxonomy._tally(classified[:2], 2, _SETTINGS, texts=["1", "2", "3"]).present == ["1", "2"]
    # One float a different length and word count, shared by its rows.
    notes = _h3_values("note", 500) + ["a b", "a b c", "abc"] * 50
    lengths, words = taxonomy._text_measures(notes)
    assert lengths == [float(len(note)) for note in notes]
    assert words == [float(parsing.token_count(note)) for note in notes]
    assert _objects(lengths) == len(set(lengths)) and _objects(words) == len(set(words))


def test_pairs_are_ranked_by_instant_text_and_offset_as_4682d6ad_ranked_them() -> None:
    """One whole number a pair ranks as the tuple of instant, published text, offset and place did, every tie included."""
    built, _names = stage4_as_built.compiled(taxonomy, stage4_as_built.CENSUS_RANKED, "_census_ranked")
    draw = random.Random(61)
    base = datetime.datetime(2019, 3, 30, 22, 0)
    offsets = ["", "Z", "+01:00", "-05:00", "+05:30", "+00:00"]
    pairs: "list[tuple[str, str]]" = []
    for _row in range(3_000):
        moment = base + datetime.timedelta(minutes=draw.randrange(0, 600, 30))
        canonical = moment.strftime("%Y-%m-%d %H:%M:%S") if draw.random() < 0.9 else moment.strftime("%Y-%m-%d")
        pairs += [(canonical, draw.choice(offsets))]
    pairs += [("0001-01-01 00:00:00", "+01:00"), ("9999-12-31 23:59:59", "-05:00"), ("1969-12-31 23:00:00", "")]
    for read_at in (taxonomy.READ_AT_UTC, taxonomy.READ_AT_LOCAL):
        for form in ("iso-datetime", taxonomy.FORMAT_ISO_MIXED):
            for resolution in (taxonomy.RESOLUTION_DATETIME, taxonomy.RESOLUTION_DATE):
                details = {"datetimes_read_at": read_at, "format": form, "resolution": resolution}
                now: "list[int]" = []
                before: "list[int]" = []
                assert taxonomy._census_ranked(details, pairs, now) == built(details, pairs, before), (read_at, form)  # type: ignore[operator]
                assert now == before, (read_at, form)
    assert taxonomy._census_ranked({"datetimes_read_at": taxonomy.READ_AT_UTC, "format": "x", "resolution": taxonomy.RESOLUTION_DATETIME}, [("2024-01-05 10:00:00", ""), ("not a moment", "")]) is None


# THE SKEPTICS' SHAPES, BOUNDED (lane H3's repair). Measured on the repair's
# head, Python 3.11, traced bytes a row above the column, memos at 1,024, at
# 20,000 / 40,000 / 80,000 rows: `MM/DD/YYYY hh:mm AM` 322.6 / 323.4 / 324.6
# (732 on 34bb5902), `M/D/YYYY H:MM` 322.7 / 323.4 (604), stamps with offsets
# 480.7 / 480.9 (620), stamps to the second 342.0 / 342.9 / 342.0 (431 / 435 /
# 462-465 on 34bb5902: they no longer rise past 40,000 rows).
@pytest.mark.parametrize("rows", [20_000, 40_000])
@pytest.mark.parametrize(("shape", "bound"), [("twelve", 380), ("mdy", 380), ("stampoff", 540)])
def test_the_mixed_table_s_stamp_forms_hold_under_their_bound_a_row(
    shape: str, bound: int, rows: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    per_row = _h3_repair_traced_a_row(_h3_repair_values(shape, rows), monkeypatch, 1_024)
    assert per_row < bound, (shape, rows, per_row)


# PAST 40,000 ROWS, where 34bb5902's stamps rose 7 % (the statistics
# skeptic's item 3): stamps to the second and the mixed table's 12-hour
# form at 80,000 rows, under the bounds of 20,000.
@pytest.mark.parametrize(("shape", "bound"), [("stamp", 400), ("twelve", 380)])
def test_stamps_at_eighty_thousand_rows_hold_under_the_bound_of_twenty_thousand(
    shape: str, bound: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    values = _h3_values(shape, 80_000) if shape == "stamp" else _h3_repair_values(shape, 80_000)
    per_row = _h3_repair_traced_a_row(values, monkeypatch, 1_024)
    assert per_row < bound, (shape, per_row)


# NOTES THAT BEGIN WITH A CAPITAL, AND NOTES OF A 30,000-WORD VOCABULARY
# EACH HOLDING A DOSE AND A DATE, in lower case and capitalised (the
# statistics skeptic's item 1, skeptic 1's item 3), under the 200 of
# P4-D400's limit (b). THE MEMOS HELD TO A THIRTY-SECOND OF THE ROWS (64 and
# 128 texts), the share 65,536 texts are of 2,000,000 rows: an affix split
# of a note is most of the note, and 1,024 of them at 2,000 rows would be
# counted as half a split a row. Measured, Python 3.11, at 2,000 / 4,000
# rows: 179.2 / 179.1 (557 to 565 on 34bb5902), the large vocabulary 210.2 at
# 2,000 rows with memos of 128 and 185.8 at 4,000 (769 and 1,343).
@pytest.mark.parametrize("rows", [2_000, 4_000])
@pytest.mark.parametrize("shape", ["notecap", "biglower", "bignote"])
def test_notes_with_capitals_and_figures_hold_under_two_hundred_bytes_a_row(
    shape: str, rows: int, monkeypatch: pytest.MonkeyPatch
) -> None:
    per_row = _h3_repair_traced_a_row(_h3_repair_values(shape, rows), monkeypatch, rows // 32)
    assert per_row < 200, (shape, rows, per_row)
