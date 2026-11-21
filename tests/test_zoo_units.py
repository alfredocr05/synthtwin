"""The affix guards and the decimal comma inferred (plan P4-D443).

Lane UN-1b of the zoo-fix track (`wave6/ZOO/PLAN.md` section 2.1b v2.1),
stacked on lane UN-1a (plan P4-D438). Each case is red on the mutant its
docstring names:

- (0) bare-number parity: a unit column read as numbers publishes what
  the same numbers written bare publish, no stricter and no looser (the
  orchestrator's LANE UN-1a RULINGS 2 (2); UN-1a's own cases in
  `tests/test_zoo_units_order.py` cover the rows and the people);
- (b) the digit guard refuses only a set of wrappers that become equal
  once their digits are removed (feet and inches), and a set whose
  longest numbers cut through a number is read at its leading numbers
  (`mL/min/1.73m2`, `x10^9/L`); a unit holding figures is a unit
  (`10*3/uL` beside `mmol/L`); units that each stand apart and each
  write one way sit together (`kg` to one figure beside whole `lb`);
- (c) a decimal comma is inferred only where every condition holds (one
  comma a cell; the number part one number under the comma; 1, 2 or 4+
  figures after it; no point in the column), with the list VETO; the
  `d,d` question; the two two-pick signatures (sorted picks; one shared
  vocabulary in click order) sending a column to the question, never to
  decimals; the mirror question for exactly three figures; an inferred
  column published among `forced_decimal_commas`, so the twin is written
  and validated alike; the answer `keep` carried across rounds;
- (d) units holding figures and the EU decimal comma beyond vitals
  (`98,5 %`, `<0,5` beside `1,2`) read as numbers.

Most tables here are under the table floor (P4-D425), through the
suite's internal switch (`tests/conftest.py`). The zoo's 600- and
20,000-row proof is the KPI driver's (`tools/measurements/kpi_zoo_units.py`,
K-HZ-08 and K-HZ-09, under `kpi_run --slow`).
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import pathlib
import random

import pytest

from synthtwin import asking, cli, parsing, profile, reading, taxonomy

import unanswered_identifier_shapes as shapes


def _write(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> pathlib.Path:
    buffer = io.StringIO()
    writer = csv.writer(buffer, lineterminator="\n")
    writer.writerow(header)
    for row in rows:
        writer.writerow(row)
    table = folder / "t.csv"
    table.write_text(buffer.getvalue(), encoding="utf-8", newline="")
    return table


def _run(args: "list[str]") -> int:
    said = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            # The table floor's refusal off here too: a module-scoped fixture
            # runs before the suite's autouse switch (`tests/conftest.py`).
            code = cli.main(args, small_tables_refused=False)
    if code not in (0,):
        print(said.getvalue()[-2000:])
    return code


def _profile(folder: pathlib.Path, column: "list[str]", *typed: str, name: str = "x", each: int = 2) -> int:
    """One column beside a declared person column of ``each`` rows a person, so no identity question reaches it (P4-D401)."""
    rows = [[cell, f"P{100000 + place // each}"] for place, cell in enumerate(column)]
    table = _write(folder, [name, "patient_id"], rows)
    return _run(
        ["profile", f"{table}", "--out-dir", f"{folder}", "--replace", "--identifier", "patient_id"] + list(typed)
    )


def _document(folder: pathlib.Path) -> "dict[str, object]":
    return json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))


def _block(folder: pathlib.Path, column: str = "x") -> "dict[str, object]":
    return [one for one in _document(folder)["columns"] if one["name"] == column][0]  # type: ignore[union-attr,index]


def _asked(folder: pathlib.Path, column: str = "x") -> "list[dict[str, object]]":
    document = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    return [entry for entry in document["asked"] if entry["column"] == column]


def _offers(folder: pathlib.Path, column: str = "x") -> "list[list[str]]":
    """Each question put to the column, as the answers it offers (the file names no reason)."""
    return [[f"{one['answer']}" for one in entry["answers_you_can_give"]] for entry in _asked(folder, column)]  # type: ignore[union-attr]


# Question Q-COMMA's answers, and its mirror's (plan P4-D443).
_Q_COMMA = [asking.ANSWER_KEEP, asking.ANSWER_DECIMAL_COMMA]
_Q_MIRROR = [asking.ANSWER_MEASUREMENT, asking.ANSWER_DECIMAL_COMMA, asking.ANSWER_CODE]


def _comma(value: float, places: int) -> str:
    return f"{value:.{places}f}".replace(".", ",")


# -- (0) bare-number parity ------------------------------------------------

# What a block publishes about its unit or its reading, set aside when a
# unit column is compared with the same numbers written bare.
_AFFIX_OWN = (
    "affix_", "detection_evidence", "n_affixed", "n_core_", "n_numeric",
    "n_not_numeric", "role", "statistical_type", "number_spellings", "remarks",
    "all_whole_numbers",
)


def _numeric_facts(block: "dict[str, object]") -> "dict[str, object]":
    return {key: value for key, value in block.items() if not any(key.startswith(word) for word in _AFFIX_OWN)}


def _unit_shapes() -> "dict[str, tuple[list[str], str]]":
    """Unit shapes no Safe Harbor reach and no width question tells apart from their bare numbers.

    A bare column of whole numbers all three figures wide is put P4-D401's
    width question and held, and one of numbers from 0 to 125 some above
    89 the Safe Harbor question (P4-D427), which judge a unit by its word:
    both are other rules than the floor's, so the shapes here stay clear
    of them (the zoo's own columns, beside their patients, are measured in
    the lane's notes).
    """
    draw = random.Random(3)
    return {
        "percent": ([f"{min(9.0, max(4.0, draw.gauss(6.5, 0.9))):.1f}" for _row in range(600)], "%"),
        "length_cm": ([f"{min(150, max(95, round(draw.gauss(122, 9))))}" for _row in range(600)], " cm"),
        "kelvin": ([f"{min(312.0, max(308.0, draw.gauss(310.0, 0.8))):.1f}" for _row in range(600)], " K"),
        "weight_lb": ([f"{min(140, max(95, round(draw.gauss(118, 9))))}" for _row in range(600)], " lb"),
        "rare_middle": (["10"] * 299 + ["21"] * 2 + ["30"] * 299, " cm"),
    }


@pytest.mark.parametrize("shape", sorted(_unit_shapes()))
def test_each_unit_shape_publishes_what_its_bare_numbers_publish(tmp_path: pathlib.Path, shape: str) -> None:
    """(0) P4-D35 parity: every published fact of the numbers, one for one, unit and bare alike.

    Each shape is described twice, written with its unit (`6.5%`, `150 cm`,
    `310.2 K`, `172 lb`, and UN-1a's `21 cm` held by two rows between two
    common values) and with the unit taken off; the unit column is read
    as `affixed_number` and its block, the facts about the unit and the
    reading aside, equals the bare column's. Red on the mutant restoring
    UN-1a's guard (a unit column with a level below the floor kept as
    labels).
    """
    numbers, unit = _unit_shapes()[shape]
    assert _profile(tmp_path, [f"{number}{unit}" for number in numbers], each=1) == 0
    with_unit = _block(tmp_path)
    assert _profile(tmp_path, numbers, each=1) == 0
    bare = _block(tmp_path)
    assert with_unit["role"] == taxonomy.ROLE_AFFIXED, shape
    assert bare["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS), shape
    assert _numeric_facts(with_unit) == _numeric_facts(bare), shape


# -- (b) the affix guards ---------------------------------------------------


def _reading(cells: "list[str]", comma: bool = False) -> "taxonomy._Affixed | None":
    settings = taxonomy.Settings()
    tallied = taxonomy._tally(taxonomy._classify_all(cells, comma), len(cells), settings, comma)
    return taxonomy._affixed_reading(tallied, True)


def _cycled(values: "list[str]", each: int) -> "list[str]":
    return [value for _turn in range(each) for value in values]


def test_feet_and_inches_cut_through_a_number_and_are_refused() -> None:
    """(b) the signature: wrappers equal once their digits are removed are refused, at either number.

    `4'5"` to `6'2"` read at the inches wear `4'`, `5'`, `6'` before one
    `"`; read at the feet, `'5"`, `'11"` behind them. Both sets cut
    through a number, so neither is a set of units, and the column is
    no quantity. Red on the mutant whose signature never fires.
    """
    heights = _cycled([f"{inches // 12}'{inches % 12}\"" for inches in range(58, 76)], 40)
    assert taxonomy._cut_through_a_number([("4'", '"'), ("5'", '"')])
    assert taxonomy._cut_through_a_number([("", "'5\""), ("", "'11\"")])
    assert not taxonomy._cut_through_a_number([("", " 10*3/uL"), ("", " mmol/L")])
    assert _reading(heights) is None


def test_a_unit_holding_figures_beside_other_units_is_read() -> None:
    """(b) the zoo's laboratory result: `10*3/uL` beside `mmol/L`, `mg/dL`, `g/dL` and `%` is one set of units.

    The digit guard refused any set with a figure in a wrapper, so the
    column fell to labels (F-units item 4a: 566 bad cells at 600 rows).
    Red on the mutant restoring that guard.
    """
    draw = random.Random(5)
    units = ("mmol/L", "mg/dL", "g/dL", "%", "10*3/uL")
    cells = [f"{draw.gauss(5.5, 1.4):.1f} {units[row % 5]}" for row in range(600)]
    reading = _reading(cells)
    assert reading is not None
    assert (" 10*3/uL" in [suffix for _prefix, suffix in taxonomy._pairs_of(reading)])


def test_a_unit_whose_figures_are_its_longest_number_is_read_at_the_leading_number() -> None:
    """(b) an eGFR `56 mL/min/1.73m2` beside `>60 mL/min/1.73m2` is 56 before its unit, not 1.73.

    The longest number is the core (`taxonomy.affixed_split`), so every
    value wore a wrapper of its own in front of `1.73`: the set cut
    through a number. Read at its leading numbers it wears one unit,
    with `>` in front of the censored cells; `7 x10^9/L` likewise. Red
    on the mutant without the leading split.
    """
    draw = random.Random(7)
    egfr = []
    for _row in range(600):
        value = round(draw.gauss(70, 25))
        egfr += [">60 mL/min/1.73m2" if value > 60 else f"{max(5, value)} mL/min/1.73m2"]
    reading = _reading(egfr)
    assert reading is not None
    assert {suffix for _prefix, suffix in taxonomy._pairs_of(reading)} == {" mL/min/1.73m2"}
    assert sorted(float(core) for core in reading.cores)[:1] == [5.0]
    counts = [f"{max(1, round(draw.gauss(7.0, 2.0)))} x10^9/L" for _row in range(600)]
    whole = _reading(counts)
    assert whole is not None and taxonomy._pairs_of(whole) == [("", " x10^9/L")]


def test_kilograms_beside_whole_pounds_are_read_and_a_noun_in_front_is_not() -> None:
    """(b) `_written_alike` relaxed for units that each stand apart and each write one way (zoo row 18).

    `78.4 kg` to one figure beside `172 lb` written whole shared no
    written form, so the set was refused (F-units: 1,938 bad cells at
    2,000 rows). Each wrapper is a unit standing apart, written one way:
    read. Readings to one figure beside `note 3` keep the refusal: a
    noun in front of an index is no unit, beside a unit or not. Red on the mutant without the
    relaxation, and on the mutant that relaxes it for a noun in front.
    """
    draw = random.Random(9)
    weights = [
        f"{draw.gauss(78, 14):.1f} kg" if row % 10 < 7 else f"{draw.gauss(172, 30):.0f} lb"
        for row in range(600)
    ]
    reading = _reading(weights)
    assert reading is not None
    assert sorted(suffix for _prefix, suffix in taxonomy._pairs_of(reading)) == [" kg", " lb"]
    notes = [f"{draw.gauss(50, 10):.1f} kg" for _row in range(240)] + ["note 3"] * 60
    assert _reading(notes) is None


# -- (c) the decimal comma inferred ------------------------------------------


@pytest.mark.parametrize(
    "cells, verdict",
    [
        (["72,5 kg", "80,1 kg", "75 kg"], parsing.COMMA_INFERRED),
        (["36,9 °C", "37,25 °C"], parsing.COMMA_INFERRED),
        (["<0,5", "1,2", "12,3"], parsing.COMMA_INFERRED),
        (["98,1234", "12,0034", "7,5"], parsing.COMMA_INFERRED),
        # the veto: two of one list mark in a cell
        (["1,3,5", "2,5", "4,5"], ""),
        (["12,5", "3;4;5"], ""),
        # a point anywhere in the column
        (["12,5", "13.5"], ""),
        # a comma cell that is no one number under the comma
        (["12,5", "1,2-3,4"], ""),
        (["12,5", "ca 1,2"], ""),
        # three figures after a comma beside others: no reading at all
        (["12,5", "1,250"], ""),
        # exactly three after every comma: the mirror question
        (["1,250", "12,500", "800"], parsing.COMMA_THREE_FIGURES),
        # one figure either side: the d,d question
        (["1,2", "2,5", "3"], parsing.COMMA_ONE_FIGURE_EACH_SIDE),
        # two picks, sorted, and in click order
        (["3,11", "2,7", "10,12"], parsing.COMMA_TWO_PICKS),
        (["11,3", "3,11", "11", "7,2", "2"], parsing.COMMA_TWO_PICKS),
        # no comma at all
        (["12", "13"], ""),
    ],
)
def test_each_condition_of_the_inference(cells: "list[str]", verdict: str) -> None:
    """(c) every condition of 2.1b, one case each: read, vetoed, refused, or sent to a question.

    Red on the mutants dropping the veto, the point condition, the
    one-number condition, the three-figures exclusion, the `d,d` rule and
    either two-pick signature.
    """
    assert parsing.decimal_comma_inferred(cells) == verdict


def _vitals_weight(rows: int, seed: int) -> "list[str]":
    draw = random.Random(seed)
    return [f"{_comma(draw.gauss(78, 14), 1)} kg" for _row in range(rows)]


@pytest.fixture(scope="module")
def weight_inferred(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """The zoo's vitals `weight` (`72,5 kg`), described, generated at seed 0 and validated once."""
    folder = tmp_path_factory.mktemp("weight")
    assert _profile(folder, _vitals_weight(600, 1), name="weight") == 0
    profile = folder / "t-profile.json"
    assert _run(["generate", f"{profile}", "--out-dir", f"{folder}", "--replace", "--seed", "0"]) == 0
    assert _run(["validate", f"{profile}", "--out-dir", f"{folder}", "--replace"]) == 0
    return folder


def test_the_vitals_weight_is_inferred_and_asked_nothing(weight_inferred: pathlib.Path) -> None:
    """(c) the zoo's `72,5 kg` is read as kilograms with a comma for the point, and no comma question is put.

    Red on the mutant that sends every inferred column to the question.
    """
    block = _block(weight_inferred, "weight")
    assert block["role"] == taxonomy.ROLE_AFFIXED
    assert block["affix_suffix"] == " kg"
    assert 74.0 < float(block["mean"]) < 82.0  # type: ignore[arg-type]
    offers = _offers(weight_inferred, "weight")
    assert _Q_COMMA not in offers and _Q_MIRROR not in offers


def test_an_inferred_column_is_published_and_its_twin_written_alike(weight_inferred: pathlib.Path) -> None:
    """(c) recorded as an inferred declaration among `forced_decimal_commas`: written with the comma, validated alike.

    `synthtwin generate` spells the numbers with the comma, and
    `synthtwin validate` re-reads the twin under the description's own
    declarations, so the twin's `weight` is the same reading (validate
    exit 0 in the fixture). Red on the mutant leaving the inferred
    column out of the published list.
    """
    assert "weight" in _document(weight_inferred)["settings"]["forced_decimal_commas"]  # type: ignore[index]
    text = (weight_inferred / "t-twin.csv").read_text(encoding="utf-8")
    twin = [row[0] for row in csv.reader(io.StringIO(text))][1:]
    assert twin and all("," in cell and "." not in cell and cell.endswith(" kg") for cell in twin)


def test_a_list_of_choices_is_vetoed_and_stays_labels(tmp_path: pathlib.Path) -> None:
    """(c) the VETO: a Qualtrics multi-select (`1,3,5`) is never read as decimals, and no comma question is put.

    The critic's `Q5_multi`: one to three picks of six, sorted. Its
    three-pick cells are refused by `_comma_core` (a second comma is no
    number's), which holds this shape with the veto off (repair 1,
    skeptic 1 item 6); the veto is pinned by the `;` shape below.
    """
    draw = random.Random(11)
    cells = [",".join(map(str, sorted(draw.sample(range(1, 7), draw.choice((1, 1, 2, 2, 3)))))) for _row in range(600)]
    assert _profile(tmp_path, cells) == 0
    assert _block(tmp_path)["role"] not in (taxonomy.ROLE_CONTINUOUS, taxonomy.ROLE_AFFIXED, taxonomy.ROLE_COUNT)
    assert "x" not in _document(tmp_path)["settings"]["forced_decimal_commas"]  # type: ignore[index]
    assert _Q_COMMA not in _offers(tmp_path)


def _two_picks(rows: int, codes: int, sorted_picks: bool, seed: int) -> "list[str]":
    draw = random.Random(seed)
    cells = []
    for _row in range(rows):
        picks = draw.sample(range(1, codes + 1), draw.choice((1, 2)))
        cells += [",".join(map(str, sorted(picks) if sorted_picks else picks))]
    return cells


@pytest.mark.parametrize(
    "cells, label",
    [
        (["1,2", "2,5", "3,4", "4"] * 150, "d,d"),
        (_two_picks(600, 12, True, 1), "two_pick_of_12 sorted"),
        (_two_picks(600, 12, False, 1), "two_pick_of_12 in click order"),
    ],
)
def test_a_column_the_cells_cannot_settle_is_asked_never_read_as_decimals(
    tmp_path: pathlib.Path, cells: "list[str]", label: str
) -> None:
    """(c) the `d,d` rule and the two two-pick signatures send the column to Q-COMMA.

    The column keeps its reading (no decimal comma published) and is put
    question Q-COMMA, whose answers are the values kept (Enter) and
    `decimal_comma`. Red on the mutants without the `d,d` rule, without
    the sorted-picks signature and without the shared-vocabulary one:
    each read the column as decimals.
    """
    assert _profile(tmp_path, cells) == 0
    assert "x" not in _document(tmp_path)["settings"]["forced_decimal_commas"], label  # type: ignore[index]
    assert _offers(tmp_path) == [_Q_COMMA], label


def test_q_comma_answered_decimal_comma_reads_the_column_and_keep_is_not_asked_again(tmp_path: pathlib.Path) -> None:
    """(c) the answer is honoured, and an answer given is not asked again (P4-D408; LANE UN-1a RULINGS 1 (2)).

    `decimal_comma` reads `1,2` as 1.2; `keep` keeps the labels and is
    carried in `answered_before`, so round two puts nothing to the
    column. Red on the mutant that does not carry `keep`.
    """
    cells = ["1,2", "2,5", "3,4", "4"] * 150
    table = _write(tmp_path, ["x"], [[cell] for cell in cells])
    answers = tmp_path / "t-questions.json"
    for answer in (asking.ANSWER_DECIMAL_COMMA, asking.ANSWER_KEEP):
        assert _run(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
        document = json.loads(answers.read_text(encoding="utf-8"))
        for entry in document["asked"]:
            if entry["column"] == "x":
                entry["your_answer"] = answer
        answers.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
        assert _run(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--answers", f"{answers}"]) == 0
        if answer == asking.ANSWER_DECIMAL_COMMA:
            assert _block(tmp_path)["role"] == taxonomy.ROLE_CONTINUOUS
            continue
        assert _asked(tmp_path) == []
        kept = json.loads(answers.read_text(encoding="utf-8"))
        assert [
            entry["your_answer"] for entry in kept.get("answered_before", []) if entry["column"] == "x"
        ] == [asking.ANSWER_KEEP]
        assert _run(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--answers", f"{answers}"]) == 0
        assert _asked(tmp_path) == []


def test_three_figures_after_every_comma_puts_the_mirror_question(tmp_path: pathlib.Path) -> None:
    """(c) the mirror of the point question: `1,250` beside values below a thousand is asked, read as thousands meanwhile.

    Red on the mutant without the mirror question.
    """
    draw = random.Random(13)
    cells = [f"{draw.randint(1, 9)},{draw.randint(0, 999):03d}" if row % 3 else f"{draw.randint(1, 999)}" for row in range(600)]
    assert _profile(tmp_path, cells) == 0
    block = _block(tmp_path)
    assert block["role"] in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS)
    assert "x" not in _document(tmp_path)["settings"]["forced_decimal_commas"]  # type: ignore[index]
    assert _offers(tmp_path) == [_Q_MIRROR]


# -- (d) units holding figures, and the EU comma beyond vitals ---------------


@pytest.mark.parametrize(
    "shape",
    ["98,5 %", "<0,5 beside 1,2"],
)
def test_the_eu_decimal_comma_beyond_vitals_is_read_as_numbers(tmp_path: pathlib.Path, shape: str) -> None:
    """(d) F-units row 38 at 600 rows: `98,5 %` and `<0,5` beside `1,2` are numbers with their unit.

    Red on the mutant without the inference (both were labels or text,
    with made-up cells in their twins).
    """
    draw = random.Random(17)
    if shape == "98,5 %":
        cells = [f"{_comma(min(100.0, max(85.0, draw.gauss(97, 2))), 1)} %" for _row in range(600)]
    else:
        cells = []
        for _row in range(600):
            value = draw.lognormvariate(1.0, 1.0)
            cells += ["<0,5" if value < 0.5 else _comma(value, 1)]
    assert _profile(tmp_path, cells) == 0
    block = _block(tmp_path)
    # `98,5 %` a number beside its unit; `<0,5` a label beside numbers, as
    # the same column written with points reads (`numbers_with_labels`).
    assert block["role"] in (taxonomy.ROLE_AFFIXED, taxonomy.ROLE_COMPOUND), shape
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == ["x"], shape  # type: ignore[index]
    assert "mean" in json.dumps(block), shape


def test_stage_2_stays_a_label_and_the_sentinels_are_unchanged(tmp_path: pathlib.Path) -> None:
    """MUST NOT (2.1b): `Stage 2` is never read as a number, and NUMERIC_SENTINELS is not widened."""
    assert parsing.NUMERIC_SENTINELS == (-9999.0, -999.0, 9999.0)
    stages = _cycled(["Stage 1", "Stage 2", "Stage 3"], 100) + ["Stage 4"] * 3
    assert _profile(tmp_path, stages) == 0
    assert _block(tmp_path)["role"] == taxonomy.ROLE_CATEGORICAL


# -- repair 1 (skeptic 1 and Codex, plan P4-D443) ----------------------------


def test_a_cell_of_thousands_of_figures_reads_without_an_integer() -> None:
    """Repair 1, skeptic 1 item 2 and Codex item 7: figures are compared as text, never turned into an int.

    Python 3.11 refuses to turn more than 4,300 figures into an integer,
    so a whole number of 5,001 figures beside comma decimals, a pick
    pair of 5,001 figures, and 4,301 nines beside a word crashed the
    inference before the column was read at all. Red on the mutant
    keeping `int()` (ValueError).
    """
    assert parsing.decimal_comma_inferred(["9" * 5001, "12,5", "13,25"]) == parsing.COMMA_INFERRED
    assert parsing.decimal_comma_inferred(["1," + "9" * 5000, "2," + "8" * 5000]) == parsing.COMMA_TWO_PICKS
    assert parsing.decimal_comma_inferred(["11,3", "3,11", "11", "3", "9" * 5000]) == parsing.COMMA_TWO_PICKS
    assert parsing.decimal_comma_inferred(["9" * 4301, "x"] * 30) == ""


def test_a_wrapper_holding_a_figure_outside_a_unit_is_refused_in_a_set() -> None:
    """Repair 1, skeptic 1 item 3 and Codex item 5: a figure in a set's wrapper stands only in a unit apart.

    `note 0` .. `note 227` beside twelve `9999-12-31` proposed `("note ",
    "")` and `("", "-12-31")`, which never become equal once their digits
    go, so the narrowed guard took the date's other half for a unit and a
    far placeholder date for a missing 9999. Feet and inches cut at
    different numbers (`4'5"` at its feet, `5'10"` at its inches) wear
    `'5"` and `5'` likewise. Both are refused; a unit standing apart
    (` x10^9/L`, ` 10*3/uL`) is not. Red on the mutant without the clause.
    """
    assert not taxonomy._figures_only_in_units([("note ", ""), ("", "-12-31")])
    assert not taxonomy._figures_only_in_units([("", "'5\""), ("5'", '"')])
    assert taxonomy._figures_only_in_units([("", " x10^9/L"), ("", " mmol/L"), ("", "%")])
    heights = _cycled(["4'5\"", "5'10\"", "5'11\""], 200)
    assert _reading(heights) is None
    notes = [f"note {index}" for index in range(228)] + ["9999-12-31"] * 12
    assert _reading(notes) is None


def test_the_leading_number_keeps_a_point_in_front_of_its_figures() -> None:
    """Repair 1, Codex item 1: `.5 mL/min/1.73m2` is 0.5 beside its unit, never 5 with `.` in front.

    The leading split moved the point into the prefix and read the cores
    `5`, `06` and `7`, so the twin wrote `.05` and `.6` and the mean moved
    from 0.42 to 0.45. Red on the mutant that leaves the point out of
    the number.
    """
    assert taxonomy._leading_split(".5 mL/min/1.73m2") == ("", ".5", " mL/min/1.73m2")
    assert taxonomy._leading_split("-.5 x") == ("", "-.5", " x")
    cells = _cycled([".5 mL/min/1.73m2", ".06 mL/min/1.73m2", ".7 mL/min/1.73m2"], 200)
    reading = _reading(cells)
    assert reading is not None and taxonomy._pairs_of(reading) == [("", " mL/min/1.73m2")]
    cores = [float(core) for core in reading.cores]
    assert abs(sum(cores) / len(cores) - 0.42) < 1e-9


def test_a_unit_holding_figures_is_counted_in_people_at_its_published_number(tmp_path: pathlib.Path) -> None:
    """Repair 1, Codex item 2, at the floor's 20,000 rows: one person's `5 mL/min/1.73m2` is counted as 5, as `5` bare is.

    1,000 declared people of 20 rows each; person 0 always holds 5, the
    others 6 + (person mod 50), once beside the eGFR's unit and once
    bare. The count in people read `1.73` from every unit cell and never
    counted the person holding 5, so the unit column published `5.0` in
    its low tail where the bare column is held. Read inside the block's
    published wrappers, both are held alike. Red on the mutant without
    the wrappers (`profile._number_inside`).
    """
    rows = []
    for person in range(1000):
        value = 5 if person == 0 else 6 + person % 50
        rows += [[f"{value} mL/min/1.73m2", f"{value}", f"P{100000 + person}"]] * 20
    table = _write(tmp_path, ["unit", "bare", "patient_id"], rows)
    assert _run(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "patient_id", "--measurement", "unit"]
    ) == 0
    unit = _block(tmp_path, "unit")
    bare = _block(tmp_path, "bare")
    assert unit["role"] == bare["role"], (unit["role"], bare["role"])
    assert "5.0" not in json.dumps(unit)


@pytest.mark.parametrize(
    "cells",
    [
        ["1,2 ", "2,5", "3,4", "4"],
        [" 3,11", "2,7", "10,12"],
        ["11,3 ", "3,11", "11 ", "7,2", "2"],
    ],
)
def test_one_padding_space_changes_no_verdict(cells: "list[str]") -> None:
    """Repair 1, Codex item 3: every signature reads the cell trimmed, as `_comma_core` does.

    One trailing space on the first cell sent the `d,d` column, sorted
    picks and click-order picks to decimals. Red on the mutant reading
    the untrimmed cell.
    """
    assert parsing.decimal_comma_inferred(cells) == parsing.decimal_comma_inferred([cell.strip() for cell in cells])
    assert parsing.decimal_comma_inferred(cells) != parsing.COMMA_INFERRED


def _padded_picks(rows: int, singles: bool, seed: int) -> "list[str]":
    draw = random.Random(seed)
    cells = []
    for _row in range(rows):
        picks = draw.sample(range(1, 16), draw.choice((1, 2)) if singles else 2)
        cells += [",".join(f"{pick:02d}" for pick in picks)]
    return cells


@pytest.mark.parametrize(
    "cells, label",
    [
        (_padded_picks(600, False, 3), "padded two picks of 15 in click order"),
        (_padded_picks(600, True, 3), "padded picks of 15, one or two, in click order"),
        (["0101,0134", "0134,0101", "0167,0101"] * 200, "four-figure padded codes"),
    ],
)
def test_padded_codes_picked_in_click_order_are_asked_never_read_as_decimals(
    tmp_path: pathlib.Path, cells: "list[str]", label: str
) -> None:
    """Repair 1, skeptic 1 item 4: `05,12` is no decimal's spelling; a column of such pairs is put Q-COMMA.

    The shared vocabulary refused any figures after a comma opening with
    a nought, and click order is not sorted, so padded codes were read as
    decimals and the twin wrote `4,15` for `04,15`. Red on the mutant
    without the padded clause.
    """
    assert parsing.decimal_comma_inferred(cells) == parsing.COMMA_TWO_PICKS, label
    assert _profile(tmp_path, cells) == 0
    assert "x" not in _document(tmp_path)["settings"]["forced_decimal_commas"], label  # type: ignore[index]
    # Four-figure codes are put P4-D401's width question first (one question a column).
    assert _offers(tmp_path) in ([_Q_COMMA], [[asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER]]), label


def _below_one(rows: int, seed: int) -> "list[str]":
    draw = random.Random(seed)
    return [_comma(min(0.55, max(0.3, draw.gauss(0.42, 0.04))), 2) for _row in range(rows)]


@pytest.mark.parametrize("rows", [600, 20000])
def test_a_decimal_below_one_with_two_places_is_inferred(tmp_path: pathlib.Path, rows: int) -> None:
    """Repair 1, skeptic 1 item 5: a hematocrit `0,42` (L/L) is read as 0.42, at 600 and the floor's 20,000 rows.

    Every pair held the sorted-picks signature (0 < 42), so the column
    was sent to the question, Q-UNIT reached it first, and its answer
    `measurement` published a mean of 42. No list picks code 0 first in
    every cell: listed among `forced_decimal_commas`, its twin written
    `0,4x` and validated (exit 0). `0,4` with one figure stays with the
    `d,d` question. Red on the mutant without the lone-0 clause.
    """
    assert parsing.decimal_comma_inferred(["0,4", "0,5", "0,3"]) == parsing.COMMA_ONE_FIGURE_EACH_SIDE
    assert _profile(tmp_path, _below_one(rows, 19)) == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == ["x"]  # type: ignore[index]
    assert 0.40 < float(_block(tmp_path)["mean"]) < 0.44  # type: ignore[arg-type]
    profile = tmp_path / "t-profile.json"
    assert _run(["generate", f"{profile}", "--out-dir", f"{tmp_path}", "--replace", "--seed", "0"]) == 0
    assert _run(["validate", f"{profile}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    text = (tmp_path / "t-twin.csv").read_text(encoding="utf-8")
    twin = [row[0] for row in csv.reader(io.StringIO(text))][1:]
    assert twin and all(cell[:2] == "0," and len(cell) == 4 for cell in twin)


def test_a_list_exported_with_semicolons_is_vetoed(tmp_path: pathlib.Path) -> None:
    """Repair 1, skeptic 1 item 6: Q5 exported with `;` (`1;3;5`) beside `2,5` is a list: no inference and no question.

    `_comma_core` already refuses a cell with a second comma, so the
    comma-exported Q5 above holds without the veto; this shape needs it.
    Red on the veto's mutant (Q-COMMA put to a list).
    """
    draw = random.Random(23)
    cells = []
    for _row in range(600):
        picks = sorted(draw.sample(range(1, 7), draw.choice((1, 2, 3))))
        cells += [";".join(map(str, picks)) if len(picks) != 2 else ",".join(map(str, picks))]
    assert parsing.decimal_comma_inferred(cells) == ""
    assert _profile(tmp_path, cells) == 0
    assert "x" not in _document(tmp_path)["settings"]["forced_decimal_commas"]  # type: ignore[index]
    assert _Q_COMMA not in _offers(tmp_path)


def test_each_part_of_the_new_rules_on_its_own_case() -> None:
    """Repair 1, skeptic 1 item 7: the parts that survived their mutants, one case each.

    - X3: `7,05` beside `5,7`, `5` and `7` is a decimal: figures after a
      comma opening with a nought are no pick (the vocabulary's clause);
    - (X9 is an equivalent mutant: a written form is pointed or not, so
      two wrappers sharing none each write one way; the clause is gone);
    - X8: `4.2 H` is a flag and `12 Jan` a day, never a unit standing apart;
    - X7: figures stand in a unit only behind a space (` x10^9/L`, not
      `x10^9/L` or `-1234`).
    """
    assert parsing.decimal_comma_inferred(["7,05", "5,7", "5", "7"]) == parsing.COMMA_INFERRED
    assert not taxonomy._a_unit_standing_apart(("", " H"))
    assert not taxonomy._a_unit_standing_apart(("", " Jan"))
    assert taxonomy._a_unit_standing_apart(("", " kg"))
    assert taxonomy._figures_stand_in_a_unit(" x10^9/L")
    assert not taxonomy._figures_stand_in_a_unit("x10^9/L")
    assert not taxonomy._figures_stand_in_a_unit("-1234")


@pytest.mark.parametrize("typed", ["--code", "--identifier"])
def test_a_column_named_a_code_or_a_record_number_is_never_inferred(tmp_path: pathlib.Path, typed: str) -> None:
    """Repair 1, skeptic 1 item 7 (X10, X11): `--code x` and `--identifier x` keep the comma as written.

    Red on the mutants that infer over the declaration.
    """
    draw = random.Random(31)
    cells = [_comma(draw.gauss(25, 4), 2) for _row in range(600)]
    assert parsing.decimal_comma_inferred(cells) == parsing.COMMA_INFERRED
    assert _profile(tmp_path, cells, typed, "x") == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == []  # type: ignore[index]


def test_record_numbers_with_a_check_digit_are_not_inferred() -> None:
    """Repair 1, skeptic 1 item 8, and repair 2: `1002345,7` is P4-D401's, never a decimal, at ANY count of keys.

    Five figures or more before every comma: `COMMA_RECORD_NUMBERS`, read
    with the comma only after the identity question is answered `keep`,
    however few different numbers (repair 1 read 60, 500 and 1,000 keys
    as decimals, under the categories ceiling). Four figures before a
    comma is a measurement's. Red on the mutant without the clause.
    """
    for keys in (3, 60, 200, 2000):
        cells = [f"{1002345 + key},{key % 10}" for key in range(keys)] * 3
        assert parsing.decimal_comma_inferred(cells) == parsing.COMMA_RECORD_NUMBERS, keys
    assert parsing.decimal_comma_inferred(["12345,6", "12346,25"]) == parsing.COMMA_RECORD_NUMBERS
    assert parsing.decimal_comma_inferred(["1234,5", "12346,25"]) == parsing.COMMA_INFERRED


def test_a_missing_value_read_by_the_grammar_keeps_the_comma_from_being_inferred(tmp_path: pathlib.Path) -> None:
    """Repair 1, Codex item 4: `--missing-value=-9.98` is -998 under a comma, so no comma is inferred beside it.

    Declared `--decimal-comma`, the combination is refused; inferred, it
    let the profile and the validator read the declaration two ways.
    Red on the mutant that infers past the check.
    """
    cells = ["-998"] * 30 + [f"{20 + index % 30},05" for index in range(570)]
    rows = [[cell, f"{-1000 + index % 30}", f"P{100000 + index // 2}"] for index, cell in enumerate(cells)]
    table = _write(tmp_path, ["x", "plain", "patient_id"], rows)
    assert _run(
        ["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace", "--identifier", "patient_id", "--missing-value=-9.98"]
    ) == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == []  # type: ignore[index]


def test_the_mirror_question_reaches_a_unit_column(tmp_path: pathlib.Path) -> None:
    """Repair 1, Codex item 6: `1,250 mg` beside `800 mg` is asked as `1,250` beside `800` is.

    `NUMERIC_ROLES` left `affixed_number` out, and the cells were judged
    whole (`800 mg` is no plain number), so a unit column read 1,000
    times too large was asked nothing. Red on the mutant without the
    unit role, and on the mutant judging whole cells.
    """
    cells = [f"{index % 30 + 1},{(index * 113) % 1000:03d} mg" if index % 3 else f"{(index * 7) % 999 + 1} mg" for index in range(600)]
    assert _profile(tmp_path, cells) == 0
    assert _block(tmp_path)["role"] == taxonomy.ROLE_AFFIXED
    assert _offers(tmp_path) == [_Q_MIRROR]


def test_both_comma_notices_say_what_was_published() -> None:
    """Repair 1, Codex item 8: Q-COMMA's notice names labels or text; the mirror's says only the comma cells move.

    Red on the first wording (every column "a list of values, each with
    its count"; "every average ... a thousand times too large").
    """
    put = [
        asking.Question("x", taxonomy.ROLE_TEXT, asking.BECAUSE_COMMA, "", [], asking.ANSWER_KEEP),
        asking.Question("y", taxonomy.ROLE_COUNT, asking.BECAUSE_COMMA_THOUSANDS, "", [], asking.ANSWER_MEASUREMENT),
    ]
    said = " ".join(cli._assumptions_notice(put).split())
    assert "as labels or as text, never as numbers" in said
    assert "as text, no value is published" in said
    assert "each value written with a comma is being read a thousand times too large" in said
    assert "a value written without one reads the same either way" in said
    assert "every average" not in said


def test_record_numbers_with_a_check_digit_are_held_with_the_identity_question(tmp_path: pathlib.Path) -> None:
    """The orchestrator's LANE UN-1b RULINGS 1 (1), at the floor's 20,000 rows: 2,000 keys `1002345,7`, ten rows each.

    The comma inference never removes P4-D401's question: the column is
    put the question offering `identifier` and held, no mean, rung or
    tail published, and no comma inferred. Red on the head 6a908499's
    inference (it read the keys as decimals and published their mean,
    nine rungs and tails, asking nothing).
    """
    cells = [f"{1002345 + key},{(key * 7) % 10}" for key in range(2000) for _row in range(10)]
    table = _write(tmp_path, ["x"], [[cell] for cell in cells])
    assert _run(["profile", f"{table}", "--out-dir", f"{tmp_path}", "--replace"]) == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == []  # type: ignore[index]
    block = _block(tmp_path)
    assert block["role"] not in (taxonomy.ROLE_CONTINUOUS, taxonomy.ROLE_COUNT, taxonomy.ROLE_AFFIXED)
    assert "mean" not in block and "p50" not in block and "tails" not in block
    published = json.dumps(_document(tmp_path))
    assert "1002" not in published and "1004" not in published
    assert any(asking.ANSWER_IDENTIFIER in offer for offer in _offers(tmp_path))


# -- repair 2 (the combined verify of a5f6d2d2) ------------------------------


def _keys_with_a_check_digit(keys: int, rows: int) -> "list[str]":
    """``keys`` record numbers of seven figures and a check digit, each on ``rows // keys`` rows in turn."""
    draw = random.Random(11)
    made = [f"{1000000 + draw.randint(0, 8999999)},{draw.randint(0, 9)}" for _key in range(keys)]
    return [made[row * keys // rows] for row in range(rows)]


def _alone(folder: pathlib.Path, cells: "list[str]", *typed: str) -> int:
    table = _write(folder, ["x"], [[cell] for cell in cells])
    return _run(["profile", f"{table}", "--out-dir", f"{folder}", "--replace"] + list(typed))


def _real_keys_in(folder: pathlib.Path, cells: "list[str]") -> int:
    """How many real record numbers the column's block names, as the text or as the number the comma reads."""
    real = set(cells)
    numbers = {float(cell.replace(",", ".")) for cell in real}
    found = 0
    waiting: "list[object]" = [_block(folder)]
    while waiting:
        leaf = waiting.pop()
        if isinstance(leaf, dict):
            waiting += list(leaf.values())
        elif isinstance(leaf, list):
            waiting += leaf
        elif isinstance(leaf, str) and leaf in real:
            found = found + 1
        elif isinstance(leaf, (int, float)) and not isinstance(leaf, bool) and float(leaf) in numbers:
            found = found + 1
    return found


@pytest.mark.parametrize("keys, rows", [(500, 20000), (1000, 20000)])
def test_few_record_numbers_with_a_check_digit_are_held_with_the_identity_question(
    tmp_path: pathlib.Path, keys: int, rows: int
) -> None:
    """Repair 2 (the verify's finding 1, HIPAA; LANE UN-1b RULINGS 1 (1)): at or under the categories ceiling too.

    500 keys of 40 rows and 1,000 of 20 at 20,000 rows: no comma
    inferred, the question offering `identifier` put, no real key in the
    block. Red on a5f6d2d2's ceiling, which read them as decimals with no
    question and published 13 and 2 real keys (mode, min, max, tails).
    """
    cells = _keys_with_a_check_digit(keys, rows)
    assert _alone(tmp_path, cells) == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == []  # type: ignore[index]
    assert _block(tmp_path)["role"] not in (taxonomy.ROLE_CONTINUOUS, taxonomy.ROLE_COUNT, taxonomy.ROLE_AFFIXED)
    assert any(asking.ANSWER_IDENTIFIER in offer for offer in _offers(tmp_path))
    assert _real_keys_in(tmp_path, cells) == 0


def test_sixty_record_numbers_at_600_rows_are_held_and_their_twin_writes_none(tmp_path: pathlib.Path) -> None:
    """Repair 2: 60 keys of ten rows at 600 rows (the library; identifier holds apply at every size, P4-D425 (3)).

    `profile.build_document` reads no comma, and the command holds the
    column with the question offering `identifier`, its twin writing no
    real key. Red on a5f6d2d2's ceiling (60 keys under 600 rows' ceiling
    read as decimals: 90 real-key hits in the block, 230 twin cells equal
    to a real key).
    """
    cells = _keys_with_a_check_digit(60, 600)
    table = _write(tmp_path, ["x"], [[cell] for cell in cells])
    described = profile.build_document(reading.read_table(f"{table}"), taxonomy.Settings(), [])
    assert described["settings"]["forced_decimal_commas"] == []  # type: ignore[index]
    assert _alone(tmp_path, cells) == 0
    assert any(asking.ANSWER_IDENTIFIER in offer for offer in _offers(tmp_path))
    assert _real_keys_in(tmp_path, cells) == 0
    assert _run(["generate", f"{tmp_path / 't-profile.json'}", "--out-dir", f"{tmp_path}", "--replace", "--seed", "0"]) == 0
    with open(tmp_path / "t-twin.csv", encoding="utf-8", newline="") as handle:
        twin = [row[0] for row in csv.reader(handle)][1:]
    assert len(twin) == 600 and not set(twin) & set(cells)


def _answered(folder: pathlib.Path, answer: str) -> pathlib.Path:
    document = json.loads((folder / "t-questions.json").read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == "x":
            entry["your_answer"] = answer
    answers = folder / f"answers-{answer}.json"
    answers.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
    return answers


def test_record_numbers_answered_keep_are_read_with_the_comma_and_code_keeps_them_codes(tmp_path: pathlib.Path) -> None:
    """Repair 2: read once the identity question is answered other than `identifier` (RULINGS 1 (1) and 2 (1)).

    `keep` reads the column with its comma, recorded among
    `forced_decimal_commas`, and the next round, handed the file it
    wrote, asks nothing and reads it alike. `code` reads codes, never
    free text, the comma kept in each label: the contract refuses a
    column among both `forced_codes` and `forced_decimal_commas` (as
    `--code` keeps it, X10). Red on the mutant that never infers on
    record numbers, and on the command that hands over no kept answer.
    """
    cells = _keys_with_a_check_digit(60, 600)
    assert _alone(tmp_path, cells) == 0
    kept = _answered(tmp_path, asking.ANSWER_KEEP)
    coded = _answered(tmp_path, asking.ANSWER_CODE)
    assert _alone(tmp_path, cells, "--answers", f"{kept}") == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == ["x"]  # type: ignore[index]
    assert _block(tmp_path)["role"] == taxonomy.ROLE_CONTINUOUS
    assert _offers(tmp_path) == []
    again = tmp_path / "answers-again.json"
    again.write_text((tmp_path / "t-questions.json").read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    assert _alone(tmp_path, cells, "--answers", f"{again}") == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == ["x"]  # type: ignore[index]
    assert _offers(tmp_path) == []
    assert _alone(tmp_path, cells, "--answers", f"{coded}") == 0
    assert _document(tmp_path)["settings"]["forced_decimal_commas"] == []  # type: ignore[index]
    assert _block(tmp_path)["role"] == taxonomy.ROLE_CATEGORICAL


def test_powers_of_ten_in_a_unit_and_a_figure_in_front_are_refused_in_a_set() -> None:
    """Repair 2 (the verify's finding 2): each clause of the set guard on a case of its own.

    ` x10^9/L` beside ` x10^6/L` (and ` 10*3/uL` beside ` 10*6/uL`)
    become equal once their digits go: refused, so the column stays
    labels as on the base, red on the mutant without
    `_cut_through_a_number`. `v2 5 mg` beside `5 mg` holds a figure in
    front of its number: refused, red on the mutant without the prefix
    clause of `_figures_only_in_units`.
    """
    draw = random.Random(5)
    for big, small in ((" x10^9/L", " x10^6/L"), (" 10*3/uL", " 10*6/uL")):
        cells = [f"{max(0.5, draw.gauss(7, 2)):.1f}{big}" if row % 2 else f"{max(0.5, draw.gauss(4.5, 0.5)):.1f}{small}" for row in range(600)]
        assert taxonomy._cut_through_a_number([("", big), ("", small)])
        assert _reading(cells) is None, big
    versions = [f"v2 {draw.randint(1, 60)} mg" if row % 2 else f"{draw.randint(1, 60)} mg" for row in range(600)]
    assert not taxonomy._figures_only_in_units([("v2 ", " mg"), ("", " mg")])
    assert _reading(versions) is None
