"""Lane PL's gate: a rare level does not cost the whole column (plan P4-D453, K-HZ-19).

The form is invented (`tests/levels_few_people_hold.py`). Each case is red on the
mutant its comment names; the mutants' log is the lane's. One case runs at 20,000
rows, the rest at 600 rows or on a few cells; the sweep is K-HZ-19's driver.
"""

from __future__ import annotations

import copy
import json
import pathlib
import tempfile
import typing

import fixtures
import health_zoo
import levels_few_people_hold as form
import pytest

from synthtwin import contract, errors, parsing, profile, reading, taxonomy
from synthtwin import validation


def _run(tmp_path: pathlib.Path, rows: int = health_zoo.SMOKE_ROWS) -> "dict[str, object]":
    return form.measure(rows, form.SEED, tmp_path / "run")


BAR = (
    "levels_shown", "counts_named", "kept_filter_faults", "flag_blank_share_faults", "dtype_mismatches",
    "thin_words_read_as_numbers", "identifying_levels_published", "validate_misses", "leaks",
)
# The shares the pool keeps, real to twin, to the fourth place (the statistics
# skeptic's item 3): ten points of `SHARE_TOLERANCE` would let `N` at .80 pass.
GAPS = ("kept_share_gap_max", "isin_gap_max", "blank_share_gap_max", "pool_share_gap_max")


def _meets_the_bar(found: "dict[str, object]") -> None:
    for key in BAR:
        assert found[key] == 0, (key, found)
    for key in GAPS:
        assert float(found[key]) <= 0.001, (key, found)  # type: ignore[arg-type]
    assert found["columns_still_held"] == [], found
    assert set(found["steps"].values()) == {0}, found  # type: ignore[attr-defined]
    # A column of words too few people fill stays words: `.str` runs, and the
    # twin writes the floor's number of cells (RULINGS 1 (1)).
    assert found["thin_word_str_runs"] == 1 and found["thin_word_twin_cells"] == 11, found


def test_the_form_at_600_rows_meets_the_bar(tmp_path: pathlib.Path) -> None:
    # Mutant: the pool never built (the hold stands): kept filters and the
    # columns still held go red. Mutant: the census counted over every cell:
    # validate misses the census on the twin. Mutant: a thin column of words
    # written blank: its dtype and `.str` go red.
    _meets_the_bar(_run(tmp_path))


def test_a_table_at_the_floor_size_pools_and_blanks_through_the_command(tmp_path: pathlib.Path) -> None:
    # The one 20,000-row case, through the shipped command's table floor, on a
    # few columns: the whole form at this size is K-HZ-19's, under kpi_run --slow.
    # Mutant: the table floor's rule for rows, the pool, the blank column.
    # Held `6` and held `8` beside 1 to 5 write the same block but for its name
    # (the orchestrator's LANE PL RULINGS 3 (3)). Mutant: the start read off
    # the real cells writes `888` beside the held `8`.
    person = [f"{1_000_000 + (row * 7_919) % 5_000:07d}" for row in range(20_000)]
    few = {f"{1_000_000 + place}" for place in range(5)}
    table = tmp_path / "floor.csv"
    lines = ["record_key,patient_key,flag_col,code_col,code_eight,thin_col,ref_col"]
    for row, who in enumerate(person):
        rare = who in few
        lines += [
            f"{500_000 + row},{who},{'Y' if rare else 'N'},{'6' if rare else 1 + row % 5},{'8' if rare else 1 + row % 5},"
            f"{'1' if rare else ''},{f'R{400_000 + int(who) % 9973}' if rare else ''}"
        ]
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    from synthtwin import cli

    arguments = [
        "--identifier", "record_key", "--identifier", "patient_key", "--identifier", "ref_col", "--code", "code_col", "--code", "code_eight",
    ]
    assert cli.main(["profile", f"{table}", "--replace", *arguments], small_tables_refused=True) in (0, 3)
    described = tmp_path / "floor-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    questions = tmp_path / "floor-questions.json"
    if questions.exists():
        asked = json.loads(questions.read_text(encoding="utf-8"))
        for entry in asked.get("asked", []):
            if entry.get("column") == "patient_key":
                entry["your_answer"] = "identifier"
        questions.write_text(json.dumps(asked, indent=2), encoding="utf-8", newline="\n")
        assert cli.main(["profile", f"{table}", "--replace", "--answers", f"{questions}", *arguments], small_tables_refused=True) in (0, 3)
        document = json.loads(described.read_text(encoding="utf-8"))
    assert _block_of(document, "flag_col")["role"] == "binary"
    # A yes-no flag publishing its no takes its yes (RULINGS 2 (2)).
    assert _block_of(document, "flag_col")["pool_in_people"]["word_from"] == "Y"
    assert [entry["label"] for entry in _block_of(document, "flag_col")["levels"]] == ["n"]
    code = _block_of(document, "code_col")
    assert code["pool_in_people"]["number_from"] == "88"
    assert "6" not in {spelling for entry in code["levels"] for spelling in [entry["label"], *entry["variants"]]}
    eight = _block_of(document, "code_eight")
    assert _differences(code, eight) == [".name", ".position"], _differences(code, eight)
    assert _block_of(document, "thin_col")["n_present"] == 0
    # A declared record number five people fill is counted absent too (skeptic
    # 1's item 2). Mutant: declared identifiers left out of the thin rule.
    assert _block_of(document, "ref_col")["n_present"] == 0
    assert _block_of(document, "ref_col")["present_count_withheld"] is True
    assert cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=True) == 0
    twin = (tmp_path / "floor-twin.csv").read_text(encoding="utf-8").split("\n")[1:]
    rows = [line.split(",") for line in twin if line]
    assert {row[2] for row in rows} == {"N", "Y"} and "6" not in {row[3] for row in rows}
    assert {row[3] for row in rows} == {row[4] for row in rows} == {"1", "2", "3", "4", "5", "88"}
    assert {row[5] for row in rows} == {""}
    # ...its twin a column of words in the floor's number of cells, never a count.
    assert sum(1 for row in rows if row[6]) == 11
    outcome = validation.measure(contract.load_profile(f"{described}"), f"{table}")
    reached = ("flag_col", "code_col", "code_eight", "thin_col", "ref_col")
    assert [one for one in outcome.checks if one.verdict == validation.MISSED and one.column in reached] == []


def _quoted(cell: str) -> str:
    """A cell as a CSV writer quotes it: a comma inside it (`2,5`) needs quotes."""
    return f'"{cell}"' if "," in cell else cell


def _pool_table(columns: "dict[str, list[str]]") -> reading.Table:
    header = list(columns)
    lines = [",".join(header)]
    for row in range(len(columns[header[0]])):
        lines += [",".join(_quoted(columns[name][row]) for name in header)]
    with tempfile.TemporaryDirectory() as folder:
        path = pathlib.Path(folder) / "t.csv"
        path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        return reading.read_table(f"{path}")


def _people_and_cells(
    rare: str, kept: "tuple[str, ...]" = ("1", "2", "3", "4", "5"), holders: int = 5
) -> "dict[str, list[str]]":
    """Three hundred people on four rows each, `holders` of them holding `rare`, the rest the kept levels."""
    person: "list[str]" = []
    cells: "list[str]" = []
    for who in range(300):
        for _row in range(4):
            person += [f"{100000 + who}"]
            cells += [rare if who < holders else kept[who % len(kept)]]
    return {"patient_key": person, "code_col": cells}


def _block_of(document: "dict[str, object]", name: str) -> "dict[str, object]":
    for block in document["columns"]:  # type: ignore[attr-defined]
        if block["name"] == name:
            return block  # type: ignore[no-any-return]
    raise AssertionError(name)


def _described(columns: "dict[str, list[str]]", **more: object) -> "dict[str, object]":
    settings = taxonomy.Settings()
    return profile.build_document(
        _pool_table(columns), settings, ["patient_key"], subjects=["patient_key"], **more  # type: ignore[arg-type]
    )


def test_a_rare_level_is_pooled_and_the_others_keep_their_counts() -> None:
    block = _block_of(_described(_people_and_cells("7"), forced_codes=["code_col"]), "code_col")
    assert block["role"] == "categorical"
    assert sorted(entry["label"] for entry in block["levels"]) == ["1", "2", "3", "4", "5"]
    assert [entry["count"] for entry in block["levels"]] == [236, 236, 236, 236, 236]
    assert block["suppressed_levels"] == 1 and block["suppressed_rows"] == 20
    assert block["suppressed_numbers"] == {"mean": None, "n_cells": 0}
    assert "7" not in json.dumps(block["levels"])
    assert block["shape_forms"] == {} or "(withheld)" not in block["shape_forms"]


@pytest.mark.parametrize(
    ("rare", "kept", "start", "number"),
    [
        # ONE PLACE WIDER THAN THE WIDEST PUBLISHED SPELLING OF ITS CLASS,
        # whatever the held level (the orchestrator's LANE PL RULINGS 2 (1)).
        # Mutant: the start read off the real cells (the build's) writes `8`
        # beside a held `6` and `88` beside a held `8`.
        ("8", ("1", "2", "3", "4", "5"), "88", True),
        ("6", ("1", "2", "3", "4", "5"), "88", True),
        ("88", ("01", "02", "03", "04", "05"), "888", True),
        ("Z", ("N", "M"), "ZZ", False),
        ("z", ("N", "M"), "ZZ", False),
        ("Zz", ("No", "Ne"), "ZZz", False),
    ],
)
def test_a_start_reads_the_published_levels_alone(rare: str, kept: "tuple[str, ...]", start: str, number: bool) -> None:
    block = _block_of(_described(_people_and_cells(rare, kept), forced_codes=["code_col"]), "code_col")
    starts = block["pool_in_people"]
    assert starts[("number_from" if number else "word_from")] == start
    assert starts[("word_from" if number else "number_from")] == ""


def test_a_number_equal_to_a_published_number_is_refused_as_a_stand_in() -> None:
    # `88.0` published is the number 88 as pandas reads it: `88` would read as
    # that level. Mutant: the numbers not asked in `_start_fits`.
    settings = taxonomy.Settings()
    published = frozenset({"1", "88.0"})
    assert not taxonomy._start_fits("88", 1, parsing.NUMBER, published, {88.0: True}, settings, frozenset())
    assert taxonomy._start_fits("88", 1, parsing.NUMBER, published, {1.0: True}, settings, frozenset())


def test_one_numeric_reading_under_the_declared_grammar() -> None:
    # The orchestrator's LANE PL RULINGS 4 (1): class, value and whole-ness, read
    # as the column's declared grammar reads them. Mutants: the declaration
    # ignored; a sign before figures not read as whole.
    assert parsing.number_as_declared("+1") == (parsing.NUMBER, 1.0, True)
    assert parsing.number_as_declared("-05") == (parsing.NUMBER, -5.0, True)
    assert parsing.number_as_declared("2.5")[1:] == (2.5, False)
    assert parsing.number_as_declared("8,0", True) == (parsing.NUMBER, 8.0, False)
    assert parsing.number_as_declared("2,5", True)[1:] == (2.5, False)
    assert parsing.number_as_declared("8,0")[0] != parsing.NUMBER
    assert parsing.number_as_declared("Z") == (parsing.NOT_A_NUMBER, None, False)


def test_the_walk_keeps_its_width_and_steps_past_the_published() -> None:
    assert parsing.stand_in_start("J45.9") == "Z88.8"
    assert parsing.stand_in_start("No") == "Zz"
    assert parsing.stand_in_start("05") == "88"
    assert parsing.stand_in_start(" Yes ") == "Zzz"
    assert parsing.stand_in_start("caf\u00e9") == "zzzz"
    assert parsing.stand_in_start("--") == "Z--"
    # Words and units beside figures stand as written; only figures and code
    # letters walk (RULINGS 2 (3)). Mutant: every letter walking writes `8 zz`.
    assert parsing.stand_in_start("6 mo") == "8 mo"
    assert parsing.stand_in_start("12 yr") == "88 yr"
    assert parsing.stand_in_start("3 d") == "8 d"
    assert parsing.stand_in_start("AB12") == "AB88"
    for text in ("J45.9", " Yes ", "caf\u00e9", "--", "A B", "1,234", "6 mo", "3 d"):
        assert parsing.is_a_stand_in_start(parsing.stand_in_start(text))
    assert parsing.stand_in_wider("88") == "888"
    assert parsing.stand_in_wider("Z88") == "Z888"
    assert parsing.stand_in_wider("8 mo") == "88 mo"
    assert parsing.stand_in_wider("Zz") == "ZZz"
    assert parsing.stand_ins_from("8", 3, frozenset({"7"})) == ["8", "6", "5"]
    assert parsing.stand_ins_from("88 mo", 2, frozenset()) == ["88 mo", "87 mo"]
    # A first figure never reaches nought, so the number keeps its width.
    assert parsing.stand_ins_from("2", 5, frozenset()) == ["2", "1"]
    assert parsing.stand_ins_from("11", 3, frozenset()) == ["11", "10"]
    assert parsing.stand_ins_from("Z8", 2, frozenset()) == ["Z8", "Z7"]
    assert parsing.stand_in_next("A0") is None


def test_the_walks_that_keep_a_form_valid() -> None:
    # Clocks count down a minute at a time, `24:00` the day's end; dates a day
    # at a time across a leap day; a closed alphabet through its letters; a
    # pair's member stands alone (RULINGS 2 (2) and (3)).
    assert parsing.stand_ins_from("23:59", 3, frozenset({"23:58"})) == ["23:59", "23:57", "23:56"]
    assert parsing.stand_ins_from("00:01", 3, frozenset()) == ["00:01", "00:00"]
    assert parsing.stand_ins_from("9:59:59", 2, frozenset()) == ["9:59:59", "9:59:58"]
    assert parsing.stand_ins_from("2000-03-01", 2, frozenset()) == ["2000-03-01", "2000-02-29"]
    assert parsing.stand_ins_from("03/01/1999", 2, frozenset()) == ["03/01/1999", "02/28/1999"]
    assert parsing.stand_ins_from("T", 4, frozenset({"g"})) == ["T", "C", "A"]
    assert parsing.stand_ins_from("TT", 3, frozenset()) == ["TT", "TG", "TC"]
    assert parsing.stand_ins_from("Yes", 3, frozenset()) == ["Yes"]
    assert parsing.stand_ins_from("1", 3, frozenset()) == ["1"]
    for start in ("23:59", "24:00", "1999-12-31", "12/31/1999", "TGCA", "Yes", "N", "0", "8 mo"):
        assert parsing.is_a_stand_in_start(start), start
    for start in ("7", "8:7", "2024-13-01", "TGCX", "8 zz9"):
        assert not parsing.is_a_stand_in_start(start), start
    assert [parsing.pair_member(one) for one in ("N", "n", "No", "NO", "no", "F", "True", "0", "1", "X")] == [
        "Y", "y", "Yes", "YES", "yes", "T", "False", "1", "0", None
    ]


@pytest.mark.parametrize(
    ("rare", "kept", "start", "valid"),
    [
        # A 0/1 indicator publishing 0 takes 1, and a flag publishing its no
        # takes its yes, in its own case (RULINGS 2 (2)): a logistic model runs on the twin.
        # Mutant: the pair not read writes `88` and `Zz`.
        ("1", ("0",), "1", "number"),
        ("Yes", ("No",), "Yes", "word"),
        ("Y", ("N",), "Y", "word"),
        # Clocks and dates take valid ones, bases unpublished bases (RULINGS 2
        # (3)). Mutant: the countdown alone writes `88:88` and `Z`.
        ("09:15", ("08:30", "10:45", "24:00"), "23:59", "clock"),
        ("2024-02-03", ("2024-01-05", "2024-01-06"), "1999-12-31", "date"),
        ("T", ("A", "C", "G"), "T", "word"),
        ("9 mo", ("6 mo", "12 mo", "3 mo"), "888 mo", "word"),
    ],
)
def test_a_pool_keeps_its_published_form(rare: str, kept: "tuple[str, ...]", start: str, valid: str, tmp_path: pathlib.Path) -> None:
    document = _described(_people_and_cells(rare, kept), forced_codes=["code_col"])
    block = _block_of(document, "code_col")
    starts = block["pool_in_people"]
    assert start in (starts["number_from"], starts["word_from"]), starts
    written = set(generation_cells(document, tmp_path)) - {entry["label"] for entry in block["levels"]}
    written = {one for one in written if parsing.folded(one) not in {entry["label"] for entry in block["levels"]}}
    if valid == "clock":
        assert all(parsing.stand_in_clock(one) is not None for one in written), written
    if valid == "date":
        assert all(parsing.date_parts(one) is not None for one in written), written
    if valid == "number":
        assert written <= {"0", "1"}, written


def test_a_class_a_pool_holds_keeps_its_own_stand_ins() -> None:
    # Words beside numbers, the column's own mix: `n_numeric` is kept.
    settings = taxonomy.Settings()
    starts = taxonomy.pool_stand_in_starts(["1", "2"], ["1", "2"], (1, 1), settings, frozenset())
    assert starts == {"number_from": "88", "word_from": "Z"}
    # A pool holding a number out of range is the hold's.
    columns = _people_and_cells("1e999", ("1", "2", "3"))
    assert "levels" not in _block_of(_described(columns, forced_codes=["code_col"]), "code_col")


def test_a_fraction_among_whole_numbers_keeps_the_hold() -> None:
    # Skeptic 1's item 5, its first remedy: `2.5` held beside 1 to 5 would read
    # float64 on the real and int64 on the twin; the column is held, as P4-D406
    # holds it. Mutant: the check removed pools it with stand-in `88`.
    for held in ("2.5", "8.0"):
        block = _block_of(_described(_people_and_cells(held), forced_codes=["code_col"]), "code_col")
        assert "levels" not in block and "pool_in_people" not in block, held
    block = _block_of(_described(_people_and_cells("6"), forced_codes=["code_col"]), "code_col")
    assert "pool_in_people" in block


def _read_back(cells: "list[str]", decimal: str = ".") -> typing.Any:
    """One column as pandas reads it from a CSV, in the decimal mark its column declares."""
    import io

    import pandas

    text = "code_col\n" + "\n".join(_quoted(cell) for cell in cells) + "\n"
    return pandas.read_csv(io.StringIO(text), decimal=decimal)["code_col"]


@pytest.mark.parametrize(
    ("held", "kept", "comma", "answer", "pair"),
    [
        # The orchestrator's LANE PL RULINGS 3 (5): the held-whole twin's dtype
        # read against the real's (h6dec's shape). The held column's walk writes
        # made-up numbers with a point where the real holds `2.5`, so both read
        # float64; beside a held `8.0` it writes none, so the twin reads int64
        # (the verify's measurement, RULINGS 5 (1); e52dd949 reads the same pair:
        # the hold is older than this lane, and nothing is widened).
        ("2.5", ("1", "2", "3", "4", "5"), False, "code", ("float64", "float64")),
        ("8.0", ("1", "2", "3", "4", "5"), False, "code", ("float64", "int64")),
        # Codex's item 3 on repair 1 (RULINGS 4 (1)): a sign before whole figures
        # is a whole number, and under a declared decimal comma `2,5` is two and
        # a half. Each pooled on 0f5b9818 (`+88`, and `0` the pair member of `1`),
        # the twin int64 against the real's float64; held now. The held twin of
        # a declared decimal comma writes the twenty cells its hold reads as no
        # number as a word, as e52dd949 does (the held walk's, owner lane PL2).
        ("2.5", ("+1",), False, "no", ("float64", "float64")),
        ("2,5", ("1",), True, "no", ("float64", "str")),
    ],
)
def test_a_fraction_among_whole_numbers_keeps_the_hold_and_its_twin_dtype(
    held: str, kept: "tuple[str, ...]", comma: bool, answer: str, pair: "tuple[str, str]", tmp_path: pathlib.Path
) -> None:
    columns = _people_and_cells(held, kept)
    more: "dict[str, object]" = {"forced_codes": ["code_col"]} if answer == "code" else {"safe_harbor_no": ["code_col"]}
    if comma:
        more["forced_decimal_commas"] = ["code_col"]
    document = _described(columns, **more)
    block = _block_of(document, "code_col")
    assert "levels" not in block and "pool_in_people" not in block
    decimal = "," if comma else "."
    real = _read_back(columns["code_col"], decimal)
    twin = _read_back(_twin_column(document, tmp_path, "code_col"), decimal)
    assert (f"{real.dtype}", f"{twin.dtype}") == pair


def test_a_stand_in_past_eighteen_figures_keeps_the_hold(tmp_path: pathlib.Path) -> None:
    # Codex's item 2 on repair 1 (the orchestrator's LANE PL RULINGS 4 (2)):
    # codes of nineteen figures, five people holding a fourth. On 0f5b9818,
    # answered, the pool started one place wider, `88888888888888888888`, past
    # a reader's 64-bit integers: the twin read object where the real read
    # int64, and numeric selection dropped the column. Unanswered it is held and
    # asked; answered `no`, it is held whole. The held twin's made-up numbers
    # of nineteen figures read uint64 (as on e52dd949: the held walk's, owner
    # lane PL2), numbers still. Mutant: the width not asked of a stand-in.
    import numpy

    big = ("1000000000000000000", "2000000000000000000", "3000000000000000000")
    columns = _people_and_cells("7000000000000000000", big)
    held: "list[str]" = []
    reasons: "dict[str, str]" = {}
    block = _block_of(_described(columns, five_figures=held, harbor_reasons=reasons), "code_col")
    assert "levels" not in block and held == ["code_col"]
    document = _described(columns, safe_harbor_no=["code_col"])
    block = _block_of(document, "code_col")
    assert "levels" not in block and "pool_in_people" not in block
    real = _read_back(columns["code_col"])
    twin = _read_back(_twin_column(document, tmp_path, "code_col"))
    assert (f"{real.dtype}", f"{twin.dtype}") == ("int64", "uint64")
    for read in (real, twin):
        assert read.to_frame().select_dtypes("number").shape[1] == 1
        assert bool(numpy.isfinite(read).all())
    # Eighteen figures still fit: a stand-in of them is no reason to hold.
    settings = taxonomy.Settings()
    assert taxonomy._start_fits("8" * 18, 1, parsing.NUMBER, frozenset({"1"}), {1.0: True}, settings, frozenset())
    assert not taxonomy._start_fits("8" * 19, 1, parsing.NUMBER, frozenset({"1"}), {1.0: True}, settings, frozenset())


def test_a_decimal_comma_pool_keeps_the_published_filter(tmp_path: pathlib.Path) -> None:
    # Codex's item 1 on repair 1 (RULINGS 4 (1)): under a declared decimal comma,
    # five people's `2,5` beside everyone else's `8,0`, answered `no`. On
    # 0f5b9818 the start read `8,0` as no number and wrote `8`, so the twin's
    # `== 8` found every row. The start and its check read the declared grammar:
    # `88,8`, and since lane HB2's repair 2 (plan P4-D477, Codex's item 4: a
    # pool after `no` starts four figures wide before its point in every form
    # the code readers accept) `8888,8`. Mutant: the declaration not passed to
    # the start.
    columns = _people_and_cells("2,5", ("8,0",))
    document = _described(columns, forced_decimal_commas=["code_col"], safe_harbor_no=["code_col"])
    block = _block_of(document, "code_col")
    assert block["pool_in_people"] == {"number_from": "8888,8", "word_from": ""}
    real = _read_back(columns["code_col"], ",")
    twin = _read_back(_twin_column(document, tmp_path, "code_col"), ",")
    assert int((twin == 8).sum()) == int((real == 8).sum()) == 1180
    assert (f"{real.dtype}", f"{twin.dtype}") == ("float64", "float64")


def _counted(cells: "list[str]") -> "dict[str, int]":
    return {cell: cells.count(cell) for cell in set(cells)}


def test_numbers_kept_beside_one_held_word_load_and_generate(tmp_path: pathlib.Path) -> None:
    # Lane PL's verify 2, its MINOR (1) (i): the numbers `1` to `5` everyone
    # else holds beside a word five people hold. The loader's check of the
    # starts (B4e) counts each published level's rows in the class its
    # spelling reads as, so the pool owes a word alone, `Z`, and the profiler's
    # own description loads and writes its twin. Mutant: the published numbers'
    # rows not counted (the loader owes the pool numbers it does not hold and
    # refuses it).
    document = _described(_people_and_cells("Q"), forced_codes=["code_col"])
    assert _block_of(document, "code_col")["pool_in_people"] == {"number_from": "", "word_from": "Z"}
    _load(document, tmp_path)
    twin = _counted(_twin_column(document, tmp_path, "code_col"))
    assert twin == {"1": 236, "2": 236, "3": 236, "4": 236, "5": 236, "Z": 20}


def test_a_decimal_comma_pool_of_a_number_and_a_word_loads(tmp_path: pathlib.Path) -> None:
    # Lane PL's verify 2, its MINOR (1) (ii): under a declared decimal comma,
    # answered `no`, `8,0` and `x` kept beside `2,5` and `Q` that five people
    # each hold. The profiler reads each published level and each held one in
    # the declared grammar, so the pool owes one number and one word, starting
    # at `88,8` and `zz` (`8888,8` since lane HB2's repair 2, plan P4-D477: after
    # `no` four figures before the point), and the loader, reading the same
    # grammar, admits them.
    # Mutants: the profiler's split or its published levels read without the
    # declaration (the starts no longer what the loader asks).
    person: "list[str]" = []
    cells: "list[str]" = []
    for who in range(300):
        for _row in range(4):
            person += [f"{100000 + who}"]
            cells += ["2,5" if who < 5 else "Q" if who < 10 else ("8,0", "x")[who % 2]]
    document = _described(
        {"patient_key": person, "code_col": cells}, forced_decimal_commas=["code_col"], safe_harbor_no=["code_col"]
    )
    assert _block_of(document, "code_col")["pool_in_people"] == {"number_from": "8888,8", "word_from": "zz"}
    _load(document, tmp_path)
    twin = _counted(_twin_column(document, tmp_path, "code_col"))
    assert twin == {"8,0": 580, "x": 580, "8888,8": 20, "zz": 20}


@pytest.mark.parametrize(("holders", "pooled"), [(10, True), (11, False)])
def test_a_level_ten_people_hold_is_pooled_and_eleven_kept(holders: int, pooled: bool) -> None:
    # Skeptic 1's item 4. Mutant: `holders) < floor` read `< floor - 1`.
    block = _block_of(_described(_people_and_cells("7", holders=holders), forced_codes=["code_col"]), "code_col")
    labels = {entry["label"] for entry in block["levels"]}
    assert ("7" not in labels) is pooled and ("pool_in_people" in block) is pooled


def test_the_pool_waits_while_a_question_offering_identifier_is_open() -> None:
    # "none offering identifier is open" (the lane's spec). Mutant: the release
    # not asked goes red here, and K-S3-64's held shapes with it.
    words = ("A1", "B2", "C3")
    block = _block_of(_described(_people_and_cells("RARE", words)), "code_col")
    assert block["role"] == "categorical" and block["suppressed_rows"] == 20
    block = _block_of(_described(_people_and_cells("RARE", words), rare_values_released=False), "code_col")
    assert block["role"] == "identifier" and "levels" not in block


def test_the_columns_own_answer_pools_beside_an_open_question() -> None:
    block = _block_of(
        _described(_people_and_cells("7"), rare_values_released=False, forced_codes=["code_col"]), "code_col"
    )
    assert block["role"] == "categorical" and block["suppressed_rows"] == 20
    block = _block_of(
        _described(_people_and_cells("7"), rare_values_released=False, safe_harbor_no=["code_col"]), "code_col"
    )
    assert block["role"] == "categorical" and block["suppressed_rows"] == 20


@pytest.mark.parametrize(
    ("name", "kept"),
    [
        # A name that says it may identify. Mutant: the words not read.
        ("plan_code", ("A1", "B2", "C3")),
        ("member_id", ("A1", "B2", "C3")),
        ("given_name", ("ANN", "BOB", "CAL")),
        # A run of five figures, an at sign, a date, a long value.
        ("group_col", ("HPX123456789", "HPX223456789", "HPX323456789")),
        ("contact_col", ("a@b.org", "c@d.org", "e@f.org")),
        ("event_col", ("2024-01-05", "2024-01-06", "2024-01-07")),
        ("line_col", ("twelve oak street apartment nine", "thirty oak street apartment two", "one oak street unit four")),
        # NAMES THAT SAY NOTHING (skeptic 1's item 1): the values decide, never
        # the name. Mutant: the build's test, the name read and values up to 24
        # characters taken, publishes all four.
        ("first", ("Anna", "Ben", "Cara")),
        ("grp", ("GRP-1000", "GRP-1037", "GRP-1074")),
        ("line1", ("10 Elm Street", "11 Elm Street", "12 Elm Street")),
        ("col_d", ("AC2000", "AC2041", "AC2082")),
        # ...and a letter beside five figures (RULINGS 3 (1)'s attack set).
        ("col_e", ("A10234", "B20345", "C30456")),
    ],
)
def test_a_shape_that_cannot_tell_is_held_and_asked(name: str, kept: "tuple[str, ...]") -> None:
    columns = _people_and_cells("RAREVALUE", kept)
    columns = {"patient_key": columns["patient_key"], name: columns["code_col"]}
    held: "list[str]" = []
    reasons: "dict[str, str]" = {}
    block = _block_of(_described(columns, five_figures=held, harbor_reasons=reasons), name)
    assert "levels" not in block
    assert held == [name] and reasons[name] == taxonomy.HELD_LEVELS_OF_FEW_PEOPLE


def test_many_different_values_are_asked_not_pooled() -> None:
    # A register or a column of names: more than 64 different values (P4-D453
    # (1)), the cap read as a number, never off the constant (the verify's
    # finding 2, the orchestrator's LANE PL RULINGS 5 (2)). Mutant: the cap
    # raised to 1000. (Read on short whole numbers: one or two letters are no
    # code by their shape since the orchestrator's LANE I4m RULINGS 21 (2).)
    assert taxonomy.levels_read_as_codes("group_col", ["1", "2"], 64)
    assert not taxonomy.levels_read_as_codes("group_col", ["1", "2"], 65)


def test_a_long_register_of_two_letter_values_is_held_and_asked() -> None:
    # ...and through the profiler: initials, say, under a name that says
    # nothing. Sixty-five two-letter values each eleven people hold, one five
    # people hold on twenty rows, unanswered: held and asked, none of the
    # sixty-six spellings in the description. Two letters alone are no code
    # by their shape since the orchestrator's LANE I4m RULINGS 21 (2), so the
    # cap is pinned by the case above, and this one by that rule's mutant too.
    common = [f"{first}{second}" for first in "QXZ" for second in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"][:65]
    person: "list[str]" = []
    cells: "list[str]" = []
    for who in range(65 * 11 + 5):
        value = common[who // 11] if who < 65 * 11 else "JW"
        for _row in range(2 if who < 65 * 11 else 4):
            person += [f"{100000 + who}"]
            cells += [value]
    held: "list[str]" = []
    reasons: "dict[str, str]" = {}
    document = _described({"patient_key": person, "col_b": cells}, five_figures=held, harbor_reasons=reasons)
    block = _block_of(document, "col_b")
    assert "levels" not in block and "pool_in_people" not in block
    assert held == ["col_b"] and reasons["col_b"] == taxonomy.HELD_LEVELS_OF_FEW_PEOPLE
    said = json.dumps(document)
    assert [value for value in (*common, "JW") if f'"{value}"' in said] == []


def test_only_short_codes_are_read_as_codes_unasked() -> None:
    # A whole number of at most three figures, one or two characters, a yes or
    # a no; nothing else, whatever the name (skeptic 1's item 1).
    for labels in (["1", "05", "120"], ["n", "a1"], ["yes"], ["no", "true", "false"]):
        assert taxonomy.levels_read_as_codes("col_a", labels, len(labels)), labels
    for labels in (["1234"], ["ann"], ["grp-1000"], ["8.5"], ["10 elm street"], ["ac2000"]):
        assert not taxonomy.levels_read_as_codes("col_a", labels, len(labels)), labels


def test_identifiers_under_names_that_say_nothing_are_held_through_the_command(tmp_path: pathlib.Path) -> None:
    # Through the shipped command at 600 rows, unanswered: no real spelling in
    # any file or on the screen, and each column asked. The 20,000-row leg is
    # K-HZ-19's (`neutral_identifier_*_20000_rows`).
    found = form.neutral_identifiers(health_zoo.SMOKE_ROWS, tmp_path / "neutral")
    assert found == {"spellings_published": 0, "not_asked": 0}, found


def test_a_few_whole_numbers_read_as_a_count_need_the_answer() -> None:
    # A code or a measurement? The shape cannot tell: `no` reads it as codes.
    person: "list[str]" = []
    cells: "list[str]" = []
    for who in range(300):
        for _row in range(4):
            person += [f"{100000 + who}"]
            cells += ["101" if who < 5 else f"{1 + who % 20}"]
    columns = {"patient_key": person, "code_col": cells}
    held: "list[str]" = []
    reasons: "dict[str, str]" = {}
    block = _block_of(_described(columns, five_figures=held, harbor_reasons=reasons), "code_col")
    assert block["role"] == "identifier" and held == ["code_col"]
    document = _described(columns, safe_harbor_no=["code_col"])
    block = _block_of(document, "code_col")
    assert block["role"] == "categorical" and block["pool_in_people"]["number_from"]
    # Nothing is recorded as declared that nobody declared (mutant: the column
    # written into `forced_codes`, as this lane's build first did).
    assert "code_col" not in document["settings"]["forced_codes"]  # type: ignore[index]
    # A column answered or declared a measurement keeps the hold (lane PS3's).
    held_too: "list[str]" = []
    document = _described(columns, safe_harbor_no=["code_col"], forced_measurements=["code_col"], five_figures=held_too)
    assert _block_of(document, "code_col")["role"] == "identifier" and held_too == []


def test_no_level_to_keep_stays_held() -> None:
    # Every level few people hold: nothing kept, the hold stands as P4-D406's.
    person: "list[str]" = []
    cells: "list[str]" = []
    for who in range(300):
        for _row in range(4):
            person += [f"{100000 + who}"]
            cells += [f"V{who % 40}" if who < 120 else "RARE"]
    columns = {"patient_key": person, "code_col": ["X" + one for one in cells]}
    # `XV1` to `XV39` each held by three people; `XRARE` by many; so one kept.
    assert _block_of(_described(columns, forced_codes=["code_col"]), "code_col").get("levels")
    columns["code_col"] = [f"X{index // 4}" for index in range(1200)]
    assert "levels" not in _block_of(_described(columns, forced_codes=["code_col"]), "code_col")


# -- thin columns -----------------------------------------------------------


def _thin(rows_a_person: int = 4, cell: str = "1", holders: int = 5) -> "dict[str, list[str]]":
    person: "list[str]" = []
    cells: "list[str]" = []
    for who in range(300):
        for _row in range(rows_a_person):
            person += [f"{100000 + who}"]
            cells += [cell if who < holders else ""]
    return {"patient_key": person, "thin_col": cells, "full_col": ["A" if index % 2 else "B" for index in range(len(person))]}


@pytest.mark.parametrize(("holders", "absent"), [(10, True), (11, False)])
def test_a_column_ten_people_fill_is_counted_absent_and_eleven_described(holders: int, absent: bool) -> None:
    # Skeptic 1's item 4. Mutant: `_present_too_few`'s `holders) < floor` read
    # `< floor - 1`.
    block = _block_of(_described(_thin(holders=holders)), "thin_col")
    assert (block.get("present_count_withheld") is True) is absent
    assert block["n_present"] == (0 if absent else holders * 4)


def test_a_declared_record_number_few_people_fill_is_counted_absent() -> None:
    # Skeptic 1's item 2: declared or answered, its count is a group of five.
    # Mutant: declared identifiers left out of the thin rule prints 10.
    person: "list[str]" = []
    ref: "list[str]" = []
    for who in range(300):
        for row in range(4):
            person += [f"{100000 + who}"]
            ref += [f"R{400000 + who}" if who < 5 and row < 2 else ""]
    columns = {"patient_key": person, "ref_col": ref, "full_col": ["A" if index % 2 else "B" for index in range(1200)]}
    document = profile.build_document(
        _pool_table(columns), taxonomy.Settings(), ["patient_key", "ref_col"], subjects=["patient_key", "ref_col"]
    )
    block = _block_of(document, "ref_col")
    assert block["role"] == "empty" and block["n_present"] == 0 and block["present_count_withheld"] is True
    assert "R400000" not in json.dumps(document)


def test_a_declared_record_number_in_rows_is_counted_absent(monkeypatch: pytest.MonkeyPatch) -> None:
    # One row a person, counted in rows, which the library reaches at the table
    # floor (the 20,000-row leg is K-HZ-19's `rows_boundary_faults`): the floor
    # moved to this table's size. Mutant: declared identifiers left out.
    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 600)
    columns = {
        "key_col": [f"{300000 + index}" for index in range(600)],
        "ref_col": [f"R{400000 + index}" if index < 5 else "" for index in range(600)],
        "rows_ten": ["A" if index < 10 else "" for index in range(600)],
        "rows_eleven": ["B" if index < 11 else "" for index in range(600)],
    }
    document = profile.build_document(_pool_table(columns), taxonomy.Settings(), ["key_col", "ref_col"])
    assert _block_of(document, "ref_col")["n_present"] == 0
    assert _block_of(document, "rows_ten")["present_count_withheld"] is True
    assert _block_of(document, "rows_eleven")["n_present"] == 11


@pytest.mark.parametrize("holders", [1, 5, 10])
def test_a_column_of_words_few_people_fill_stays_words(holders: int, tmp_path: pathlib.Path) -> None:
    # The orchestrator's LANE PL RULINGS 1 (1): the twin writes its word in the
    # floor's number of cells, whatever the real holds, from a start that reads
    # nothing real. Mutant: the word not written leaves the twin blank (float64).
    import pandas

    document = _described(_thin(cell="word", holders=holders))
    block = _block_of(document, "thin_col")
    assert block["n_present"] == 0 and block["withheld_words_from"] == "Z"
    cells = _twin_column(document, tmp_path, "thin_col")
    assert sorted(set(cells)) == ["", "Z"] and sum(1 for one in cells if one) == 11
    twin = pandas.Series([one or None for one in cells], dtype=object)
    assert twin.dropna().str.len().eq(1).all()
    # A column of figures stays blank: blanks read float64 as its cells do.
    assert "withheld_words_from" not in _block_of(_described(_thin(holders=holders)), "thin_col")


def test_a_column_of_dates_written_as_text_few_people_fill_writes_its_word(tmp_path: pathlib.Path) -> None:
    # The orchestrator's LANE PL RULINGS 5 (3), ruled (a): every present cell a
    # date written as text, five people fill it. It is a column of words: its
    # twin writes `Z` in eleven cells, so pandas reads str on both and
    # `to_datetime` reads the real and refuses the twin. A start in the dates'
    # layout would publish the layout of cells under the floor, a change of
    # NF133's contract and lane CZ-B's; this case pins today's twin so that a
    # change is a visible decision. Mutant: the word not written.
    import pandas

    columns = _thin(cell="2023-05-14")
    columns["thin_col"] = [
        f"2023-0{1 + index % 9}-1{index % 10}" if cell else "" for index, cell in enumerate(columns["thin_col"])
    ]
    document = _described(columns)
    block = _block_of(document, "thin_col")
    assert block["n_present"] == 0 and block["withheld_words_from"] == "Z"
    cells = _twin_column(document, tmp_path, "thin_col")
    assert sorted(set(cells)) == ["", "Z"] and cells.count("Z") == 11
    real = _read_back(columns["thin_col"])
    twin = _read_back(cells)
    assert (f"{real.dtype}", f"{twin.dtype}") == ("str", "str")
    pandas.to_datetime(real.dropna(), format="%Y-%m-%d")
    with pytest.raises(ValueError):
        pandas.to_datetime(twin.dropna(), format="%Y-%m-%d")


def test_a_column_few_people_fill_is_counted_absent() -> None:
    document = _described(_thin())
    block = _block_of(document, "thin_col")
    assert block["role"] == "empty" and block["n_present"] == 0
    assert block["n_missing"] == 1200 and block["present_count_withheld"] is True
    assert "not published" in f"{block['detection_evidence']}"
    assert "the real table may hold values" in f"{block['detection_evidence']}"
    # No count of its twenty cells anywhere in its block, nor of its 1,180 blanks.
    said = json.dumps({key: block[key] for key in block if key not in ("position", "name")})
    assert ": 20," not in said and ": 20}" not in said and "1180" not in said
    assert block["missing_by_class"]["(blank)"] == 1200


def test_the_real_table_meets_a_column_counted_absent(tmp_path: pathlib.Path) -> None:
    # Mutant: the validator not handed the column misses `n_present` (P4-D406's
    # record of a description claiming blanks).
    found = _run(tmp_path)
    assert found["validate_misses"] == 0 and found["validate_exit"] == 0
    stem = "levels_few_people_hold"
    outcome = validation.measure(
        contract.load_profile(f"{tmp_path / 'run' / (stem + '-profile.json')}"), f"{tmp_path / 'run' / (stem + '.csv')}"
    )
    reached = (*form.CODES, *form.FLAGS, *form.THIN)
    assert [
        (one.column, one.subcheck) for one in outcome.checks if one.verdict == validation.MISSED and one.column in reached
    ] == []
    text = (tmp_path / "run" / "levels_few_people_hold-profile.txt").read_text(encoding="utf-8")
    section = text[text.index("  thin_digit\n"):]
    section = section[: section.index("  thin_word\n")]
    assert "values present: not published" in section
    assert "no values at all" not in section


def test_a_thin_column_of_rows_counts_rows_only_at_the_command_size() -> None:
    # No subject column repeats: rows, on a table the command describes; the
    # library keeps its bytes below the floor (P4-D433's rule).
    small = ["1" if index < 5 else "" for index in range(600)]
    wide = {"key_col": [f"{index}" for index in range(600)], "thin_col": small}
    settings = taxonomy.Settings()
    block = _block_of(profile.build_document(_pool_table(wide), settings, ["key_col"]), "thin_col")
    assert block["n_present"] == 5
    assert profile._present_too_few(small, frozenset(), [], [], 11, parsing.TABLE_ROW_FLOOR)
    assert not profile._present_too_few(small, frozenset(), [], [], 11, parsing.TABLE_ROW_FLOOR - 1)
    # Ten rows and eleven (skeptic 1's item 4). Mutant: `rows < floor - 1`.
    assert profile._present_too_few(["1"] * 10, frozenset(), [], [], 11, parsing.TABLE_ROW_FLOOR)
    assert not profile._present_too_few(["1"] * 11, frozenset(), [], [], 11, parsing.TABLE_ROW_FLOOR)


def test_a_column_held_by_an_open_identifier_question_stays_as_it_was() -> None:
    columns = _thin()
    document = profile.build_document(
        _pool_table(columns), taxonomy.Settings(), [], unanswered=["thin_col"], subjects=["patient_key"]
    )
    block = _block_of(document, "thin_col")
    assert block["role"] == "identifier" and "present_count_withheld" not in block
    # Mutant: the thin rule run first blanks the column under its hold.
    assert block["n_present"] == 20


# -- what the tool says of a pool and of a column counted absent --------------


def test_the_generation_report_claims_no_real_cell_for_a_stand_in(tmp_path: pathlib.Path) -> None:
    # Codex's item 7 on repair 1 (RULINGS 4 (6)): a yes-no column publishing
    # `N` writes `Y` into its pool beside a real `Y` few people hold (B4e), so
    # the report says where the stand-ins come from and claims no real cell
    # for them. Mutant: the sentence of repair 1.
    from synthtwin import generation

    document = _described(_people_and_cells("Y", ("N",)), forced_codes=["code_col"])
    assert _block_of(document, "code_col")["pool_in_people"]["word_from"] == "Y"
    plan = generation.plan_generation(contract.load_profile(f"{fixtures.write_profile(tmp_path, 't-profile.json', document)}"))
    for column in plan.columns:
        if column.column.name == "code_col":
            notes = generation._label_content(column)[1]
    said = [note.note for note in notes if note.fact == "suppressed_levels"]
    assert len(said) == 1 and "no real cell" not in said[0], said
    assert "made up from the description's published facts alone" in said[0]


def test_the_summary_says_a_column_of_words_counted_absent_is_written_as_its_word() -> None:
    # Codex's item 8 on repair 1 (RULINGS 4 (6)): its twin writes eleven `Z`
    # cells, so the summary no longer calls it blank; a column of figures so
    # counted is still written blank. Mutant: the word marker not read.
    from synthtwin import summary

    words = summary.render(_described(_thin(cell="word")), "")
    section = words[words.index("  thin_col\n") :]
    section = section[: section.index("  full_col\n")]
    assert "written blank" not in section
    assert "the made-up word 'Z' in 11 cells" in section and "values present: not published" in section
    figures = summary.render(_described(_thin()), "")
    section = figures[figures.index("  thin_col\n") :]
    assert "written blank in the twin" in section[: section.index("  full_col\n")]


def test_the_changelog_says_which_dates_stay_valid() -> None:
    # Codex's item 9 on repair 1 (RULINGS 4 (6)): "clocks and dates stay valid"
    # was too broad. Day-first labels, five of 300 people holding `03/02/2024`
    # beside `05/01/2024` and `06/01/2024`, declared codes: the pool writes
    # twenty `12/31/1999` cells, which `%d/%m/%Y` refuses while it reads every
    # real cell. The behaviour is pinned so a change to it is a visible
    # decision (owner lane PL2), and the CHANGELOG and P4-D453 say so. Mutant:
    # the changelog's sentence of repair 1.
    import datetime

    columns = _people_and_cells("03/02/2024", ("05/01/2024", "06/01/2024"))
    document = profile.build_document(
        _pool_table(columns), taxonomy.Settings(day_first=True), ["patient_key"],
        subjects=["patient_key"], forced_codes=["code_col"],
    )
    cells = generation_cells(document, pathlib.Path(tempfile.mkdtemp()))
    made_up = sorted(set(cells) - set(columns["code_col"]))
    assert made_up == ["12/31/1999"] and cells.count("12/31/1999") == 20
    for cell in set(columns["code_col"]):
        datetime.datetime.strptime(cell, "%d/%m/%Y")
    with pytest.raises(ValueError):
        datetime.datetime.strptime(made_up[0], "%d/%m/%Y")
    root = pathlib.Path(__file__).resolve().parents[1]
    changelog = (root / "CHANGELOG.md").read_text(encoding="utf-8")
    assert "clocks and dates stay valid" not in changelog
    assert "clocks on the 24-hour face and dates written year first or month first stay valid" in changelog
    plan = (root / "docs" / "plans" / "phase-4-columns.md").read_text(encoding="utf-8")
    decision = plan[plan.index("## Decision P4-D453") :]
    after = decision.find("\n## ", 10)
    assert "`12/31/1999`" in (decision if after < 0 else decision[:after])


# -- the loader -------------------------------------------------------------


def _load(document: "dict[str, object]", folder: pathlib.Path) -> None:
    contract.load_profile(f"{fixtures.write_profile(folder, 't-profile.json', document)}")


def _loaded_pool(tmp_path: pathlib.Path) -> "dict[str, object]":
    document = _described(_people_and_cells("7"), forced_codes=["code_col"])
    _load(document, tmp_path)
    return document


def _refused(document: "dict[str, object]", word: str, folder: pathlib.Path) -> None:
    with pytest.raises(errors.ProfileError) as raised:
        _load(document, folder)
    assert word in f"{raised.value}"


def test_b4_reads_people_only_on_a_block_that_says_so(tmp_path: pathlib.Path) -> None:
    document = _loaded_pool(tmp_path)
    without = copy.deepcopy(document)
    del _block_of(without, "code_col")["pool_in_people"]
    _refused(without, "B4", tmp_path)


def test_the_loader_reads_the_starts(tmp_path: pathlib.Path) -> None:
    document = _loaded_pool(tmp_path)
    for starts, word in (
        ({"number_from": "7", "word_from": ""}, "B4e"),
        ({"number_from": "", "word_from": ""}, "B4e"),
    ):
        broken = copy.deepcopy(document)
        _block_of(broken, "code_col")["pool_in_people"] = starts
        _refused(broken, word, tmp_path)


def test_the_loader_refuses_a_start_its_walk_cannot_serve(tmp_path: pathlib.Path) -> None:
    # Codex's item 6 on repair 1 (the orchestrator's LANE PL RULINGS 4 (5)): a
    # start the loader admitted could write nothing (`1` beside published `1`
    # to `5` walks only onto a published level, and generation divided by the
    # empty walk) or the wrong class (`Z` on a pool of numbers). Each is refused
    # with the column named. Mutants: the walk's room not asked; the class not
    # asked.
    document = _loaded_pool(tmp_path)
    assert _block_of(document, "code_col")["pool_in_people"] == {"number_from": "88", "word_from": ""}
    for starts, said in (
        ({"number_from": "1", "word_from": ""}, "walks to 0 spellings"),
        ({"number_from": "Z", "word_from": ""}, "'Z' reads as no number"),
        ({"number_from": "", "word_from": "Z"}, "walks to 0 spellings"),
    ):
        broken = copy.deepcopy(document)
        _block_of(broken, "code_col")["pool_in_people"] = starts
        with pytest.raises(errors.ProfileError) as raised:
            _load(broken, tmp_path)
        assert "B4e" in f"{raised.value}" and said in f"{raised.value}" and "code_col" in f"{raised.value}", starts
    # A start the walk serves loads, wider or not.
    for start in ("88", "888"):
        served = copy.deepcopy(document)
        _block_of(served, "code_col")["pool_in_people"] = {"number_from": start, "word_from": ""}
        _load(served, tmp_path)


def test_present_count_withheld_stands_on_an_empty_block_alone(tmp_path: pathlib.Path) -> None:
    document = _loaded_pool(tmp_path)
    broken = copy.deepcopy(document)
    _block_of(broken, "code_col")["present_count_withheld"] = True
    with pytest.raises(errors.ProfileError):
        _load(broken, tmp_path)
    thin = _described(_thin())
    _load(thin, tmp_path)
    _block_of(thin, "thin_col")["present_count_withheld"] = False
    with pytest.raises(errors.ProfileError):
        _load(thin, tmp_path)
    # ...and its word stands beside it alone, a start of the walks that reads
    # as no number (B4e). Mutant: the word's check dropped.
    words = _described(_thin(cell="word"))
    _load(words, tmp_path)
    for start in ("7", "8"):
        broken = copy.deepcopy(words)
        _block_of(broken, "thin_col")["withheld_words_from"] = start
        _refused(broken, "B4e", tmp_path)
    broken = copy.deepcopy(document)
    _block_of(broken, "code_col")["withheld_words_from"] = "Z"
    with pytest.raises(errors.ProfileError):
        _load(broken, tmp_path)


# -- the validator ----------------------------------------------------------


def test_a_column_counted_absent_is_not_observed(tmp_path: pathlib.Path) -> None:
    # Codex's item 4 on repair 1 (the orchestrator's LANE PL RULINGS 4 (3)):
    # twenty words five people fill are described; a file with words in every
    # cell is checked. The blank reading stays (V17.2), but what it decides is
    # not an observation of the file: the presence, content and type facts are
    # WITHHELD with the reason, none HELD, and the report says nothing was
    # found. On 0f5b9818 twelve were HELD and the report read the file as
    # holding no present cell. Mutant: the reading's checks left as they were.
    from synthtwin import quality

    columns = _thin(cell="word")
    document = _described(columns)
    folder = tmp_path / "words"
    folder.mkdir()
    description = contract.load_profile(f"{fixtures.write_profile(folder, 't-profile.json', document)}")
    path = folder / "every_cell.csv"
    lines = ["patient_key,thin_col,full_col"]
    for row in range(1200):
        lines += [f"{columns['patient_key'][row]},word,{columns['full_col'][row]}"]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    outcome = validation.measure(description, f"{path}")
    mine = [check for check in outcome.checks if check.column == "thin_col"]
    observed = {check.fact for check in mine if check.verdict != validation.WITHHELD}
    assert observed <= {"universal.position", "document.source.dialect"}, observed
    withheld = [check for check in mine if check.verdict == validation.WITHHELD]
    assert {check.fact for check in withheld} >= {"universal.n_present", "universal.n_missing", "universal.role", "empty.n_distinct"}
    for check in withheld:
        assert check.citation[: len("not available")] == "not available" and not check.achieved and not check.published
        assert validation.withheld_rule(check) == "count-not-published"
    report = quality.quality_report(description, outcome)
    section = report[report.index("\n'thin_col'\n") + 1 :]
    section = section[: section.index("\n'full_col'\n")]
    # Only the column's place and the bytes' quoting are found in the file.
    found = [line for line in section.split("\n") if "found to hold:" in line]
    assert len(found) == 2 and "quoted" in found[0] and "column number 2" in found[1], found
    assert section.count("why nothing is shown: not available") == len(withheld)


def test_a_file_that_loses_a_kept_level_is_missed(tmp_path: pathlib.Path) -> None:
    # Mutant: every label read as pooled: a file with no kept level passes.
    form.measure(health_zoo.SMOKE_ROWS, form.SEED, tmp_path / "run")
    run = tmp_path / "run"
    stem = "levels_few_people_hold"
    source = run / f"{stem}.csv"
    text = source.read_text(encoding="utf-8").split("\n")
    header = text[0].split(",")
    place = header.index("rare_code")
    rows = [line.split(",") for line in text[1:] if line]
    for row in rows:
        if row[place] == "1":
            row[place] = "2"
    source.write_text("\n".join([",".join(header)] + [",".join(row) for row in rows]) + "\n", encoding="utf-8", newline="\n")
    outcome = validation.measure(contract.load_profile(f"{run / (stem + '-profile.json')}"), f"{source}")
    missed = [check for check in outcome.checks if check.verdict == validation.MISSED and check.column == "rare_code"]
    assert missed


# -- the oracle (A-P4-59) ---------------------------------------------------


def _oracle() -> object:
    import importlib.util

    path = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"
    spec = importlib.util.spec_from_file_location("make_generation_reference_vectors", path)
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def test_the_oracle_writes_the_same_cells(tmp_path: pathlib.Path) -> None:
    # Method G8.3b from its own words: the product's and the oracle's cells of
    # the same blocks, a class each and both. Mutant: the even share changed.
    oracle = _oracle()
    for rare, kept, word_too in (
        ("7", ("1", "2", "3"), False), ("RARE", ("ALPHA", "BRAVO"), False), ("UNK", ("1", "2", "3"), True),
        ("Y", ("N",), False), ("1", ("0",), False), ("09:15", ("08:30", "10:45"), False),
        ("2024-02-03", ("2024-01-05", "2024-01-06"), False), ("T", ("A", "C", "G"), False), ("9 mo", ("6 mo", "12 mo"), False),
    ):
        columns = _people_and_cells(rare, kept)
        if word_too:
            columns["code_col"] = ["7" if 20 <= index < 40 else cell for index, cell in enumerate(columns["code_col"])]
        document = _described(columns, forced_codes=["code_col"])
        block = _block_of(document, "code_col")
        assert "pool_in_people" in block
        written = generation_cells(document, tmp_path)
        assert sorted(written) == sorted(oracle._label_content(json.loads(json.dumps(block))))  # type: ignore[attr-defined]


# THE FROZEN VECTORS OF METHOD G8.3d (the orchestrator's LANE PL RULINGS 1 (3)):
# each case's invented table, as the oracle's thirty-second file names it.
FROZEN = pathlib.Path(__file__).resolve().parent / "reference" / "generation-branch-vectors-32.json"
FROZEN_TABLES = {
    "pool_number_countdown": ("7", ("1", "2", "3"), False),
    "pool_word_countdown": ("RARE", ("ALPHA", "BRAVO"), False),
    "pool_both_classes": ("UNK", ("1", "2", "3"), True),
    "pool_yes_no_member": ("Y", ("N",), False),
    "pool_zero_one_member": ("1", ("0",), False),
    "pool_clock_walk": ("09:15", ("08:30", "10:45"), False),
    "pool_date_walk": ("2024-02-03", ("2024-01-05", "2024-01-06"), False),
    "pool_alphabet_walk": ("T", ("A", "C", "G"), False),
    "pool_unit_kept": ("9 mo", ("6 mo", "12 mo"), False),
}


@pytest.mark.parametrize("name", [*sorted(FROZEN_TABLES), "thin_words_written"])
def test_the_product_writes_the_frozen_content(name: str, tmp_path: pathlib.Path) -> None:
    # The profiler writes the frozen block (its starts chosen as the method
    # says) and the generator the oracle's content, cell for cell as counts.
    # Red without the rule: the pool's branch, a walk or a start removed.
    case = json.loads(FROZEN.read_text(encoding="utf-8"))["cases"][name]
    if name == "thin_words_written":
        document = _described(_thin(cell="word", holders=5))
        assert _block_of(document, "thin_col") == case["block"]
        written = [cell for cell in _twin_column(document, tmp_path, "thin_col") if cell]
    else:
        rare, kept, word_too = FROZEN_TABLES[name]
        columns = _people_and_cells(rare, kept)
        if word_too:
            columns["code_col"] = ["7" if 20 <= index < 40 else cell for index, cell in enumerate(columns["code_col"])]
        document = _described(columns, forced_codes=["code_col"])
        assert _block_of(document, "code_col") == case["block"]
        written = generation_cells(document, tmp_path)
    counted: "dict[str, int]" = {}
    for cell in written:
        counted[cell] = counted.get(cell, 0) + 1
    assert counted == case["content"], name


def generation_cells(document: "dict[str, object]", folder: pathlib.Path) -> "list[str]":
    path = fixtures.write_profile(folder, "t-profile.json", document)
    from synthtwin import generation

    plan = generation.plan_generation(contract.load_profile(f"{path}"))
    for column in plan.columns:
        if column.column.name == "code_col":
            return generation._label_content(column)[0]
    raise AssertionError("no plan")


def _twin_column(document: "dict[str, object]", folder: pathlib.Path, name: str) -> "list[str]":
    """One column of the twin the product writes of a description, at seed 0."""
    from synthtwin import generation

    twin = generation.generate(contract.load_profile(f"{fixtures.write_profile(folder, 't-profile.json', document)}"), 0)
    return list(twin.columns[twin.names.index(name)])


# -- the workbook writer ----------------------------------------------------


def test_a_workbook_keeps_the_pool_and_the_blank_column(tmp_path: pathlib.Path) -> None:
    # The workbook's writer, at 600 rows: numbers stay numbers, a stand-in is
    # none of the real values, and the real workbook meets its own description.
    import kpi_shapes

    columns = _people_and_cells("RARE", ("ALPHA", "BRAVO"))
    numbers = _people_and_cells("7")["code_col"]
    blank = ["1" if index < 20 else "" for index in range(len(numbers))]
    head = ["patient_key", "word_col", "code_col", "thin_col"]
    rows = [
        [columns["patient_key"][place], columns["code_col"][place], numbers[place], blank[place]]
        for place in range(len(numbers))
    ]
    table = tmp_path / "book.xlsx"
    kpi_shapes._workbook(table, head, rows)
    from synthtwin import cli

    arguments = ["--identifier", "patient_key", "--code", "word_col", "--code", "code_col"]
    assert cli.main(["profile", f"{table}", "--replace", *arguments], small_tables_refused=False) in (0, 3)
    described = tmp_path / "book-profile.json"
    document = json.loads(described.read_text(encoding="utf-8"))
    assert _block_of(document, "word_col")["pool_in_people"]["word_from"]
    assert _block_of(document, "code_col")["pool_in_people"]["number_from"]
    assert _block_of(document, "thin_col")["n_present"] == 0
    # The sheet's census of the column prints no count of its cells either.
    # Mutant: the census left: `text 20` beside `empty 1180`.
    census = document["source"]["workbook"]["columns"][head.index("thin_col")]
    assert set(census["cell_classes"].values()) == {None}
    assert cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=False) == 0
    outcome = validation.measure(contract.load_profile(f"{described}"), f"{table}")
    assert [one for one in outcome.checks if one.verdict == validation.MISSED and one.column != "patient_key"] == []
    twin = validation.measure(contract.load_profile(f"{described}"), f"{tmp_path / 'book-twin.xlsx'}")
    assert [one for one in twin.checks if one.verdict == validation.MISSED and one.column != "patient_key"] == []


def _differences(left: object, right: object, path: str = "") -> "list[str]":
    if isinstance(left, dict) and isinstance(right, dict):
        found: "list[str]" = []
        for key in sorted(set(left) | set(right)):
            found += _differences(left.get(key), right.get(key), f"{path}.{key}")
        return found
    if isinstance(left, list) and isinstance(right, list) and len(left) == len(right):
        found = []
        for place in range(len(left)):
            found += _differences(left[place], right[place], f"{path}[{place}]")
        return found
    return [] if left == right else [path]


def test_nothing_tells_a_column_counted_absent_from_a_blank_one() -> None:
    # Every byte of the description but the column's own evidence and key is the
    # description of the same table with those cells blank: no count in any file.
    columns = _thin()
    blank = dict(columns)
    blank["thin_col"] = ["" for _cell in columns["thin_col"]]
    found = _differences(_described(columns), _described(blank))
    place = list(columns).index("thin_col")
    assert found == [f".columns[{place}].detection_evidence", f".columns[{place}].present_count_withheld"]


@pytest.mark.parametrize(
    ("one", "other", "kept"),
    [
        ("7", "6", ("1", "2", "3")), ("RAREA", "OTHER", ("ALPHA", "BRAVO")), ("9", "1234", ("1", "2", "3")), ("Y", "QQQ", ("N",)),
        # A held level the build's walk met (the statistics skeptic's item 1):
        # `8` or `6` beside 1 to 5, `88` or `09` beside 01 to 05, `Z` or `Q`
        # beside N and M. Mutant: the start read off the real cells.
        ("8", "6", ("1", "2", "3", "4", "5")), ("88", "09", ("01", "02", "03", "04", "05")), ("Z", "Q", ("N", "M")),
        # ...and one standing in the walk's own first spelling: `88` held beside
        # 1 to 5 widened the build's start to `888`, `77` left it `88`.
        ("88", "77", ("1", "2", "3", "4", "5")),
    ],
)
def test_nothing_in_a_description_says_which_level_few_people_hold(one: str, other: str, kept: "tuple[str, ...]") -> None:
    # Any value the few people might hold writes the same description, its width
    # and letters included: never named, in no file. Only a value standing in the
    # walk's own way moves its start, the case above the gate names.
    first = _described(_people_and_cells(one, kept), forced_codes=["code_col"])
    second = _described(_people_and_cells(other, kept), forced_codes=["code_col"])
    assert _differences(first, second) == []
