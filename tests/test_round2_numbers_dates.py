"""The second Codex round of 2026-09-19: its number and date items.

Codex reviewed 05e7d89 in five passes. Three items of its NUMBERS pass
and two of its DATES pass are reproduced here from the review's own
inputs and its own figures, each with the measurement taken BEFORE the
repair beside it, and each paired with a MUTANT test that withdraws the
repair and shows the review's own numbers coming back.

Every table is built by seeded neutral code at runtime (plan D13) and no
value here comes from any real table.
"""

import collections
import csv
import dataclasses
import io
import json
import pathlib
import re
import statistics
import zipfile

import pytest

from synthtwin import contract, generation, sheetwriting
from tests import fixtures, workbooks
from tests.test_extra_round_numbers import _exit_of, _round_trip


# -- the numbers pass, item 1: the mode's published FREQUENCY ---------


_MODE_VALUES = (-1.8, -0.9, -0.6, 0.8, 1.8, 3.3, 3.5)
_MODE_COUNTS = (9, 18, 28, 23, 8, 30, 23)


def _mode_frequency_cells() -> "list[str]":
    """Codex's own column: seven one-place values at its own counts."""
    cells: "list[str]" = []
    for place in range(len(_MODE_VALUES)):
        for _each in range(_MODE_COUNTS[place]):
            cells += [f"{_MODE_VALUES[place]:.1f}"]
    return cells


@pytest.mark.parametrize("seed", ["4", "0", "1", "7", "13"])
def test_a_mode_held_at_the_wrong_frequency_is_named(
    tmp_path: pathlib.Path, seed: str
) -> None:
    """The published pair is a PAIR, and the count is half of it.

    MEASURED before the repair, at seeds 4, 0, 1, 7 and 13 alike: the
    description publishes the mode 3.3 at a count of 30; the ladder gives
    3.3 a stratum of ONE cell and no stratum at all is 30 cells, so the
    twin wrote 3.3 once and its commonest numbers were -0.6 and 3.4 at 28
    each. The mean moved 1.17338 -> 1.06619 and the spread
    1.92529 -> 2.08471, every executable check passed on both files, and
    the report named NOTHING: the pass returned successfully wherever
    some stratum held the mode's VALUE, whatever that stratum's size.

    THE CELLS CANNOT MOVE UNDER THIS PASS, AND THAT IS A NARROWER CLAIM
    THAN THE FIRST VERSION OF THIS DOCSTRING MADE (the skeptic's finding
    5, 2026-09-19). No stratum of this ladder is 30 cells -- the sizes
    are 27, 28, 23, 9, 1, 28 and 23 -- and this pass resizes no stratum,
    so no move it may make reaches the pair. The pair itself IS
    reachable by some conforming table: the real table here holds 3.3
    exactly thirty times and `validate` exits 0 on it against this same
    description, at all five seeds. Its 139 sorted values put 3.3 at
    ranks 86 to 115, which carries p75 (rank 103.5) at 3.3 and p90 (rank
    124.2) at 3.5 exactly as the ladder publishes them -- so what would
    have to change to reach the pair is which values the ladder invents
    between its rungs and how many cells it gives each, which is the
    spread of the column and the owner's DEFERRED stage-3 item. What the
    repair owes here is that the difference be REPORTED rather than
    silently accepted.
    """
    cells = _mode_frequency_cells()
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "mode", cells, ("--smallest-group", "11"), seed
    )
    assert block["mode"] == 3.3
    assert block["mode_count"] == 30
    held = collections.Counter(written)
    assert held["3.3"] == 1
    assert held.most_common(1)[0][1] == 28
    numbers = [float(cell) for cell in written]
    assert round(statistics.fmean(numbers), 5) == 1.06619
    assert round(statistics.stdev(numbers), 5) == 2.08471
    # ...and the report says so, against the published count.
    report = (tmp_path / "mode" / "real-twin-report.txt").read_text(
        encoding="utf-8"
    )
    assert "'value' -- mode_count" in report
    assert "the description says: 30" in report
    assert "the twin holds:       1" in report
    assert twin_exit == 0
    assert real_exit == 0


def test_the_mutant_accepts_the_wrong_frequency_in_silence(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the frequency unasked, and the report silent again."""
    held = generation._mode_held

    def withdrawn(
        column: "object", facts: "object", layout: "object", values: "object"
    ) -> "object":
        mode = facts.mode  # type: ignore[attr-defined]
        for value in values:  # type: ignore[attr-defined]
            if value == mode:
                return values, []
        return held(column, facts, layout, values)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_mode_held", withdrawn)
    _block, _written, twin_exit, real_exit = _round_trip(
        tmp_path / "unasked", _mode_frequency_cells(),
        ("--smallest-group", "11"), "4",
    )
    report = (tmp_path / "unasked" / "real-twin-report.txt").read_text(
        encoding="utf-8"
    )
    assert "mode_count" not in report
    assert twin_exit == 0
    assert real_exit == 0


# -- the numbers pass, item 2: a record number's absorbed counts ------


_ABSORBED_CELLS = ["12"] * 230 + ["Z"] * 10


def _identifier_round_trip(
    folder: pathlib.Path,
) -> "tuple[dict[str, object], list[str], int, int]":
    """Codex's own declared record number, described, built and checked."""
    folder.mkdir(parents=True, exist_ok=True)
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(
            ["record"], [[cell] for cell in _ABSORBED_CELLS]
        ),
        encoding="utf-8",
        newline="",
    )
    assert _exit_of([
        "profile", str(table), "--out-dir", str(folder), "--replace",
        "--identifier", "record", "--smallest-group", "11",
    ]) == 0
    description = folder / "real-profile.json"
    assert _exit_of([
        "generate", str(description), "--out-dir", str(folder),
        "--seed", "4", "--replace",
    ]) == 0
    twin = folder / "real-twin.csv"
    written = [
        row[0]
        for row in csv.reader(io.StringIO(twin.read_text(encoding="utf-8")))
        if row
    ][1:]
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of([
        "validate", str(description), "--twin", str(twin),
        "--out-dir", str(checked), "--replace",
    ])
    looked = folder / "check-real"
    looked.mkdir()
    real_exit = _exit_of([
        "validate", str(description), "--twin", str(table),
        "--out-dir", str(looked), "--replace",
    ])
    block = json.loads(description.read_text(encoding="utf-8"))["columns"][0]
    return block, written, twin_exit, real_exit


def _every_cell_whole(written: "list[str]") -> bool:
    """Whether every cell reads as a whole number, as pandas would read it."""
    for cell in written:
        if re.fullmatch(r"-?\d+", cell) is None:
            return False
    return True


def test_an_absorbed_reading_keeps_the_columns_usable_type(
    tmp_path: pathlib.Path
) -> None:
    """A feasible reading is offered, so the twin reads back as text.

    MEASURED before the repair, at a floor of eleven and seed 4: the ten
    `Z` cells fall below the floor, so the published counts absorb to
    `n_numeric 240`, `n_all_digits 240`, `n_code_alphabet 240` and
    `all_whole_numbers false`. 87,845 other readings of those counts
    exist and exactly FOUR of them any packing of whole groups can meet;
    the offer's first 256 held one of the four and the reading the
    column's own values make stood at position 17,773, so the twin came
    back `16` on 230 rows and `0` on ten -- every cell a whole number
    against a description that says not every value is one. `validate`
    exited 3 on the twin and 0 on the real table, and `pandas` reads the
    source's column as text and that twin's as whole numbers.
    """
    block, written, twin_exit, real_exit = _identifier_round_trip(
        tmp_path / "absorbed"
    )
    assert block["all_whole_numbers"] is False
    assert block["n_numeric"] == 240
    assert block["n_all_digits"] == 240
    assert block["n_code_alphabet"] == 240
    counted = collections.Counter(written)
    assert len(counted) == 2
    assert sorted(counted.values()) == [10, 230]
    assert not _every_cell_whole(written)
    assert not _every_cell_whole(_ABSORBED_CELLS)
    assert twin_exit == 0
    assert real_exit == 0


def test_the_mutant_spends_the_candidate_limit_on_infeasible_readings(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: nothing sifted, and the whole-number fact lost again."""
    monkeypatch.setattr(
        generation, "_whole_groups_reach", lambda reached, total: True
    )
    _block, written, twin_exit, real_exit = _identifier_round_trip(
        tmp_path / "unsifted"
    )
    assert _every_cell_whole(written)
    assert twin_exit == 3
    assert real_exit == 0


# -- the numbers pass, item 3: the exponent form's own scale ----------


def _exponent_cells(sign: str) -> "list[str]":
    """Codex's own column, at a positive and at a negative exponent."""
    cells = ["alpha"] * 100
    cells += [f"1.10e{sign}7"] * 20
    cells += [f"1.11e{sign}7"] * 10
    return cells + [f"1.12e{sign}7"] * 10


@pytest.mark.parametrize("sign", ["+", "-"])
def test_every_cell_of_an_exponent_form_wears_it(
    tmp_path: pathlib.Path, sign: str
) -> None:
    """Forty cells of `%.%%&x%`, not twenty and twenty bare numbers.

    MEASURED before the repair, at a floor of eleven and seed 4: the
    description requires `shape_forms {"%.%%&+%": 40}` and the source
    passes all 45 executable checks, while the twin wrote the form TWENTY
    times and spelled the other twenty `10999999` and `11000001` -- a
    ladder walking in hundredths where the form can only spell hundreds
    of thousands, and a dressing that counts figures into figure places
    and so has no room for eight of them. The twin missed the form count
    and exited 3 where the real table exited 0. The negative exponent
    failed the same way.
    """
    cells = _exponent_cells(sign)
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"exponent{'up' if sign == '+' else 'down'}",
        cells, ("--smallest-group", "11"), "4",
    )
    form = f"%.%%&{sign}%"
    assert block["shape_forms"] == {form: 40}
    wearing = [cell for cell in written if re.fullmatch(
        r"\d\.\d\de" + re.escape(sign) + r"\d", cell
    )]
    assert len(wearing) == 40
    assert collections.Counter(written)[f"1.10e{sign}7"] == 20
    # ...and every made-up number stands at the column's own magnitude.
    for cell in wearing:
        assert cell[5:] == f"{sign}7"
    assert twin_exit == 0
    assert real_exit == 0


def test_the_mutant_walks_the_mantissas_bare_places(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the exponent's scale withdrawn, and the form unpaid."""
    monkeypatch.setattr(
        generation,
        "_form_scale",
        lambda form, ladder, decimal_comma: generation._form_places(
            form, decimal_comma
        ),
    )
    monkeypatch.setattr(
        generation, "_exponent_fittings", lambda *arguments: []
    )
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "bare", _exponent_cells("+"),
        ("--smallest-group", "11"), "4",
    )
    assert block["shape_forms"] == {"%.%%&+%": 40}
    wearing = [
        cell for cell in written if re.fullmatch(r"\d\.\d\de\+\d", cell)
    ]
    assert len(wearing) == 20
    assert "10999999" in written
    assert "11000001" in written
    assert twin_exit == 3
    assert real_exit == 0


def _zero_anchor_cells(published: str) -> "list[str]":
    """A hundred `alpha` beside forty cells of `%.%%&+%` at exponent nought.

    ``published`` is the level the floor of eleven leaves standing; the
    other two are held back and the twin must make its own spellings for
    them.
    """
    levels = ["0.00e+0", "1.10e+0", "2.20e+0"]
    cells = ["alpha"] * 100 + [published] * 20
    for level in levels:
        if level != published:
            cells += [level] * 10
    return cells


def test_an_exponent_column_anchored_at_nought_wears_its_form(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's finding 3: the one neighbouring shape item 3 missed.

    MEASURED on 05e7d89 AND on the first repair of item 3 alike, at a
    floor of eleven and seeds 4 and 13: a hundred `alpha` beside twenty
    `0.00e+0`, ten `1.10e+0` and ten `2.20e+0` publishes
    `shape_forms {"%.%%&+%": 40}` and passes every executable check, and
    the twin wore the form TWENTY times and wrote the other twenty as
    the bare figures `1` and `2`, missing the form count at exit 3 while
    the real table exited 0. Every other shape of the same defect the
    first repair fixed -- exponents e+0 to e+6 and e+17, either sign of
    the value, either letter case, no sign, one mantissa decimal.

    The residue was a column whose published magnitude is NOUGHT:
    `_form_scale` read the exponent off the largest published magnitude,
    nought has none, and the rule stood aside and answered the plain
    places, which sends the scaled walk back at its first line. A column
    publishing nought alone publishes it as its form spells it, so the
    exponent is nought and the scaled place is the mantissa's own
    `after`.

    `zero_not_lowest` -- the same three levels with `1.10e+0` published
    instead -- is the control: its magnitude is not nought, it was
    already settled at forty of forty, and it must not move.
    """
    for seed in ("4", "13"):
        block, written, twin_exit, real_exit = _round_trip(
            tmp_path / f"zero{seed}", _zero_anchor_cells("0.00e+0"),
            ("--smallest-group", "11"), seed,
        )
        assert block["shape_forms"] == {"%.%%&+%": 40}
        wearing = [
            cell for cell in written if re.fullmatch(r"\d\.\d\de\+\d", cell)
        ]
        assert len(wearing) == 40
        assert collections.Counter(written)["0.00e+0"] == 20
        for cell in wearing:
            assert cell[5:] == "+0"
        assert twin_exit == 0
        assert real_exit == 0
        # THE CONTROL, at the same seed: a published magnitude that is
        # not nought is untouched by this repair.
        _block, control, control_twin, control_real = _round_trip(
            tmp_path / f"notlowest{seed}", _zero_anchor_cells("1.10e+0"),
            ("--smallest-group", "11"), seed,
        )
        assert sorted(collections.Counter(control).items()) == [
            ("1.08e+0", 10), ("1.09e+0", 10), ("1.10e+0", 20), ("alpha", 100),
        ]
        assert control_twin == 0
        assert control_real == 0


def test_the_mutant_reads_a_published_nought_at_the_plain_place(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: a nought magnitude sent back to the plain places."""
    scale = generation._form_scale

    def stood_aside(form: str, ladder: object, decimal_comma: bool) -> int:
        letters = generation._form_letters(form)
        lead, _after = generation._form_mantissa(form, decimal_comma)
        units = max(abs(ladder.lowest), abs(ladder.highest))
        if letters == 1 and lead >= 1 and ladder.anchored and units == 0:
            return generation._form_places(form, decimal_comma)
        return scale(form, ladder, decimal_comma)

    monkeypatch.setattr(generation, "_form_scale", stood_aside)
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "plainplace", _zero_anchor_cells("0.00e+0"),
        ("--smallest-group", "11"), "4",
    )
    assert block["shape_forms"] == {"%.%%&+%": 40}
    wearing = [
        cell for cell in written if re.fullmatch(r"\d\.\d\de\+\d", cell)
    ]
    assert len(wearing) == 20
    assert "1" in written
    assert "2" in written
    assert twin_exit == 3
    assert real_exit == 0


# -- the dates pass, item 1: the calendar repair and published text ---


def _mixed_storage_book() -> bytes:
    """60 `2024-03-01` stored as dates beside 60 `2024-02-30` stored as text."""
    rows: "list[tuple[int, list[str]]]" = [
        (1, [workbooks.cell("A1", "0", "s")])
    ]
    for place in range(120):
        number = 2 + place
        if place % 2 == 0:
            rows += [(
                number,
                [workbooks.cell(f"A{number}", "2024-03-01", "d")],
            )]
            continue
        rows += [(
            number,
            [workbooks.cell(f"A{number}", "2024-02-30", "inlineStr")],
        )]
    return workbooks.package([
        (
            "[Content_Types].xml",
            workbooks._content_types(1, True, False, False),
        ),
        ("_rels/.rels", workbooks._root_rels()),
        ("xl/workbook.xml", workbooks._workbook([("Data", "")])),
        ("xl/_rels/workbook.xml.rels", workbooks._workbook_rels(1, True)),
        ("xl/styles.xml", workbooks._styles()),
        ("xl/sharedStrings.xml", workbooks._shared_strings(["observed"])),
        (
            "xl/worksheets/sheet1.xml",
            workbooks.sheet(rows, dimension="A1:A121"),
        ),
    ])


def _book_round_trip(
    folder: pathlib.Path,
) -> "tuple[dict[str, object], str, str, int, int]":
    """Describe the mixed-storage book, build its twin and check both."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "real.xlsx"
    source.write_bytes(_mixed_storage_book())
    assert _exit_of([
        "profile", str(source), "--out-dir", str(folder), "--replace",
        "--first-row", "names", "--smallest-group", "5",
    ]) == 0
    description = folder / "real-profile.json"
    assert _exit_of([
        "generate", str(description), "--out-dir", str(folder),
        "--seed", "0", "--replace",
    ]) == 0
    twin = folder / "real-twin.xlsx"
    with zipfile.ZipFile(twin) as package:
        sheet = package.read("xl/worksheets/sheet1.xml").decode("utf-8")
        shared = package.read("xl/sharedStrings.xml").decode("utf-8")
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of([
        "validate", str(description), "--twin", str(twin),
        "--out-dir", str(checked), "--replace",
    ])
    looked = folder / "check-real"
    looked.mkdir()
    real_exit = _exit_of([
        "validate", str(description), "--twin", str(source),
        "--out-dir", str(looked), "--replace",
    ])
    block = json.loads(description.read_text(encoding="utf-8"))["columns"][0]
    return block, sheet, shared, twin_exit, real_exit


def test_a_published_text_label_survives_the_calendar_repair(
    tmp_path: pathlib.Path
) -> None:
    """A cell the source stored as legal TEXT is not an invalid date cell.

    MEASURED before the repair, at a floor of five and seed 0: the
    profile publishes both labels at 60 rows each and generation keeps
    both, and the workbook serialization rewrote all 60 text cells as
    `2024-02-29`. The source had zero validation misses and the
    serialized twin had six label-related misses, `validate` exiting 3.
    """
    block, sheet, shared, twin_exit, real_exit = _book_round_trip(
        tmp_path / "mixed"
    )
    labels = sorted(level["label"] for level in block["levels"])
    assert labels == ["2024-02-30", "2024-03-01"]
    assert "2024-02-30" in shared
    assert "2024-02-29" not in shared
    assert "2024-02-29" not in sheet
    # Every cell actually stored as a date names a real day.
    assert sheet.count('t="d"><v>2024-03-01</v>') == 60
    assert twin_exit == 0
    assert real_exit == 0


def test_the_mutant_rewrites_the_published_label(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: no spelling held back, and the label moves a day."""
    monkeypatch.setattr(
        sheetwriting, "_published_spellings", lambda column: frozenset()
    )
    _block, sheet, shared, twin_exit, real_exit = _book_round_trip(
        tmp_path / "rewritten"
    )
    assert "2024-02-29" in shared or "2024-02-29" in sheet
    assert twin_exit == 3
    assert real_exit == 0


# -- the dates pass, item 2: the paid merge and midnight --------------


_MIDNIGHT_CELLS = (
    ["2024-03-01T00:00:00"] * 40
    + ["2024-03-02T00:00:00"] * 40
    + ["2024-03-03T12:00:00"] * 40
)


def test_a_stranded_non_midnight_run_is_merged_by_a_paid_trade(
    tmp_path: pathlib.Path
) -> None:
    """Three published timestamps, and three in the twin.

    MEASURED before the repair, at a floor of eleven and seed 4: the twin
    held those three values 41, 39 and 35 times beside FIVE invented
    `2024-03-01T16:13:10` cells, missing `n_distinct` and
    `n_distinct_folded`, four against three, while the source passed.
    P4-D258's paid merge trades WIDTH alone and returns at its first line
    on this column, so the extra non-midnight run stranded between
    midnight pins had no merge of any kind.
    """
    block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "midnight", _MIDNIGHT_CELLS,
        ("--smallest-group", "11"), "4",
    )
    assert block["n_distinct"] == 3
    assert block["n_distinct_folded"] == 3
    assert len(set(written)) == 3
    assert sorted(set(written)) == sorted(set(_MIDNIGHT_CELLS))
    # ...and the midnight census is exactly where it was.
    at_midnight = [cell for cell in written if cell.endswith("T00:00:00")]
    assert len(at_midnight) == 80
    assert twin_exit == 0
    assert real_exit == 0


def test_the_mutant_trades_widths_only_and_strands_the_run(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the midnight trade withdrawn, and four values again."""
    traded = generation._traded_merges

    def widths_only(*arguments: "object") -> int:
        if len(arguments) > 12 and arguments[12]:
            return 0
        return traded(*arguments)  # type: ignore[arg-type]

    monkeypatch.setattr(generation, "_traded_merges", widths_only)
    _block, written, twin_exit, real_exit = _round_trip(
        tmp_path / "stranded", _MIDNIGHT_CELLS,
        ("--smallest-group", "11"), "4",
    )
    assert len(set(written)) == 4
    assert twin_exit == 3
    assert real_exit == 0


def _one_level(withheld: "dict[str, int]") -> "contract.LevelEntry":
    """One published level of a date-shaped label, with a withheld map."""
    return contract.LevelEntry(
        label="2024-02-30",
        count=60,
        variants={"2024-02-30": 54, "2024-2-30": 6},
        variants_withheld=dict(withheld),
        shape_form_cells=0,
    )


def _label_block_with(
    folder: pathlib.Path, level: "contract.LevelEntry"
) -> "contract.ColumnBlock":
    """A real published label column, carrying one hand-written level.

    The block is a described column of synthtwin's own producer, loaded
    back through `contract.load_profile`, so every other fact on it is
    one a description really carries; only the level is written here,
    because a `variants_withheld` map with anything in it is one the
    producer never writes (the owner's ruling of 2026-09-17) and a
    hand-written description is the door it comes through.
    """
    made = folder / f"level{len(level.variants_withheld)}"
    made.mkdir(parents=True, exist_ok=True)
    table = made / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(
            ["value"], [[cell] for cell in ["alpha"] * 60 + ["beta"] * 60]
        ),
        encoding="utf-8",
        newline="",
    )
    # THE PRODUCT WRITES THE DESCRIPTION THIS TEST LOADS, here rather than
    # through a helper, so the line-endings rule can see it do so.
    described = ["profile", str(table), "--out-dir", str(made), "--replace"]
    assert _exit_of(described + ["--smallest-group", "11"]) == 0
    document = contract.load_profile(str(made / "real-profile.json"))
    column = document.columns[0]
    facts = column.facts
    assert isinstance(facts, contract.LabelFacts)
    return dataclasses.replace(
        column, facts=dataclasses.replace(facts, levels=[level])
    )


def _withheld_walked(column: "contract.ColumnBlock") -> "frozenset[str]":
    """The FIRST version of `_published_spellings`, withheld keys and all."""
    facts = column.facts
    if not isinstance(facts, contract.LabelFacts):
        return frozenset()
    spellings: "list[str]" = []
    for level in facts.levels:
        spellings += [level.label]
        for spelling in level.variants:
            spellings += [spelling]
        for spelling in level.variants_withheld:
            spellings += [spelling]
    return frozenset(spellings)


def test_a_withheld_row_count_is_not_a_published_spelling(
    tmp_path: pathlib.Path,
) -> None:
    """The skeptic's finding 2: `variants_withheld` is a multiplicity map.

    Its KEYS are zero-padded ROW COUNTS and its values are how many
    held-back spellings stood at that count -- contract 7.4.8, and the
    way `contract.py` reads it back. The first version of
    `_published_spellings` walked those keys as though they were
    spellings, so a level with `{"003": 2, "010": 1}` told
    `_onto_the_calendar` to step over any cell whose text is `003` or
    `010`.

    MEASURED on that exact level: the first version answers
    `['003', '010', '2024-02-30', '2024-2-30']` and this one answers the
    two spellings the description really prints. Nothing moved in a twin
    synthtwin's own producer described -- the owner's ruling of
    2026-09-17 counts a below-floor spelling into the commonest, so every
    `variants_withheld` it writes is empty -- but the loader accepts a
    description written by hand, and that is the door the row counts
    came through.
    """
    block = _label_block_with(tmp_path, _one_level({"003": 2, "010": 1}))
    assert sheetwriting._published_spellings(block) == frozenset(
        {"2024-02-30", "2024-2-30"}
    )
    # Every member is a spelling the description prints, and no member is
    # a bare count of rows.
    for spelling in sheetwriting._published_spellings(block):
        assert not spelling.isdigit()
    # An empty map answers the same two, so the repair costs the ordinary
    # description nothing.
    assert sheetwriting._published_spellings(
        _label_block_with(tmp_path, _one_level({}))
    ) == frozenset({"2024-02-30", "2024-2-30"})


def test_the_mutant_walks_the_withheld_multiplicity_keys(
    tmp_path: pathlib.Path,
) -> None:
    """The mutant: the first version's loop, and the row counts return."""
    block = _label_block_with(tmp_path, _one_level({"003": 2, "010": 1}))
    assert sorted(_withheld_walked(block)) == [
        "003", "010", "2024-02-30", "2024-2-30",
    ]
    assert _withheld_walked(block) != sheetwriting._published_spellings(block)
