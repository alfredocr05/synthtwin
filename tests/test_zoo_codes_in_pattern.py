"""P4-D439 (lane CODES-1): held-back codes written in pattern -- rules A1, A2 and A3.

WHAT WAS MEASURED (the health data zoo's plan, wave6/ZOO/PLAN.md section 2.2
and rows 2, 17, 24, 26, 29, 44, 49 and 56; the stand-ins page, P4-D422's
ZS.2; measured on 589f3d72 at 600 rows, wave6/CODES-1/smoke-base-600.log):

(a) A form the floor pooled was owed nowhere, so its held-back codes were
    written `group-N`: ICD-10 codes with a seventh character, 13 cells;
    blood type `AB-`, 4 cells.
(b) A stand-in was filled from the whole alphabet: tumour stages `A0A0A0`
    and `L8D8G3` (91 cells out of `T[0-4]N[0-3]M[01]`), Glasgow coma scores
    every one of 600 cells (`Z2S4F4`), a LOINC code `00000-0`, primary
    sites `A000`, and `=` was no mark, so a Gleason score `3+4=7` had no
    form and its held-back scores were `group-N`.
(c) PCORnet diagnoses: the held-back numbers owed `%%%.%` 7 of their 29
    cells, the class split handed the 29 out as 10, 9, 6 and 4, and the
    twin wrote 24 cells of `%%%.%` against the published 21 (validate 3).

THE RULE (plan P4-D439). A1: on the four label roles a `(withheld)` form
pool that is exactly the floor's (`taxonomy.floor_pooled_forms`), of forms
no number can wear and no clock or stamp, is counted in the commonest named
form, named in `shape_forms_absorbed` (contract C6-31g), and the validator
counts a measured file's pooled forms there alike. A2: the published
characters of each named form, place by place, and a floored census of
what the held-back cells hold at each place (`shape_form_places`, C6-31h:
characters on the census line of cells or more, a forced place refused, in
people beside a subject column, nothing while any question offering
`identifier` is open), chained into stages the twin walks, the largest
stand-ins first in balanced order, widening from the last place so a
vocabulary prefix is kept longest; the validator holds each listed
character on the line. A3: where no searched class split leaves the forms
settleable, the sizes drawn for each class are taken. The mark set gains
`=`; the page's other four, a list's separators, wait for lane LISTS
(a held column of listed record numbers wore forms its twin filled with
a real key). The oracle mirrors each (A-P4-59).

Every case runs the library at 600 rows through the floor the test gives
(the table floor is the command's rule; the 20,000-row proof is
K-HZ-10 and K-HZ-11's driver, tools/measurements/kpi_codes_in_pattern.py),
and each is red on the mutant its docstring names.

THE REPAIRS (plan P4-D439's repair 1 and 2 paragraphs). Most cases after
`_described_at` run at 20,000 rows, one table a writer: a census whose
lists, read as a product, name held-back spellings is refused; a clock
keeps its bytes beside the census and beside the drawn split; a declared
code keeps its ends only where they leave room, and its walk crosses its
grain in one step; the recount in people keeps nothing a row; an older
description holding `=` loads and a cell opening with `=` wears no form;
a form nothing lists opens as the published codes do; an open free-text
person question holds every census through the command; small letters
are kept; a listed character left short is swapped to the line; and the
oracle mirrors the code ends, their room, the clock rule and the swap.
"""

from __future__ import annotations

import collections
import contextlib
import importlib.util
import io
import json
import pathlib
import random
import re
import tracemalloc

import pytest

import fixtures
from synthtwin import (
    cli,
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

FLOOR = 11
ROWS = 600
ORACLE = pathlib.Path(__file__).resolve().parents[1] / "tools" / "reference" / "make_generation_reference_vectors.py"


# -- the shapes (made-up codes, written from each system's public grammar) --


def _zipf(draw: random.Random, values: "list[str]", count: int, power: float) -> "list[str]":
    weights = [1.0 / ((rank + 1) ** power) for rank in range(len(values))]
    return draw.choices(values, weights=weights, k=count)


ICD10 = [
    "E11.9", "I10", "J45.909", "Z00.00", "M54.5", "F32.9", "K21.9", "N39.0", "C50.911",
    "F41.1", "I50.9", "S72.001A", "U07.1", "A41.9", "J18.9", "T81.4XXA", "W19.XXXA",
    "E78.5", "G47.33", "R51.9",
]
ICD10_PATTERN = r"[A-Z][0-9][0-9A-Z](\.[0-9A-Z]{1,4})?"


def _icd10(draw: random.Random) -> "list[str]":
    return _zipf(draw, ICD10, ROWS, 1.3)


def _tnm(draw: random.Random) -> "list[str]":
    cells: "list[str]" = []
    for _row in range(ROWS):
        t = draw.choices("1234", weights=[40, 35, 15, 10])[0]
        n = draw.choices("0123", weights=[60, 25, 10, 5])[0]
        m = draw.choices("01", weights=[92, 8])[0]
        cells += [f"T{t}N{n}M{m}"]
    return cells


TNM_PATTERN = r"T[0-4]N[0-3]M[01]"


def _gcs(draw: random.Random) -> "list[str]":
    return [
        f"E{draw.randint(1, 4)}V{draw.randint(1, 5)}M{draw.randint(1, 6)}"
        for _row in range(ROWS)
    ]


GCS_PATTERN = r"E[1-4]V[1-5]M[1-6]"


def _gleason(draw: random.Random) -> "list[str]":
    scores = ["3+3=6", "3+4=7", "4+3=7", "4+4=8", "4+5=9", "5+4=9", "5+5=10", "3+5=8"]
    return draw.choices(scores, weights=[40, 30, 15, 8, 3, 2, 1, 1], k=ROWS)


GLEASON_PATTERN = r"[1-5]\+[1-5]=([2-9]|10)"


def _concepts(draw: random.Random) -> "list[str]":
    common = [f"ICD10CM:{code}" for code in ("E11.9", "J45.9", "K21.9", "N39.0", "M54.5", "F32.9")]
    rare = [f"ICD10CM:{letter}{number:02d}.{digit}" for letter, number, digit in (
        ("A", 41, 9), ("B", 20, 1), ("C", 34, 1), ("D", 64, 9), ("G", 43, 9), ("H", 10, 9),
        ("L", 40, 0), ("R", 51, 9), ("Z", 79, 4), ("Q", 21, 1), ("S", 82, 1), ("T", 78, 4),
    )]
    cells = draw.choices(common, weights=[30, 25, 15, 12, 10, 8], k=ROWS - 5 * len(rare))
    for code in rare:
        cells += [code] * 5
    draw.shuffle(cells)
    return cells


CONCEPT_PATTERN = r"ICD10CM:[A-Z]\d{2}\.\d"


def _pcornet_dx(draw: random.Random) -> "list[str]":
    common = ["E11.9"] * 120 + ["I10"] * 80 + ["401.9"] * 14 + ["250.00"] * 27 + ["44054006"] * 12
    common += ["J45.909"] * 60 + ["Z00.00"] * 40 + ["M54.5"] * 40 + ["F32.9"] * 30
    rare = ["R07.9"] * 10 + ["486"] * 8 + ["311"] * 4 + ["272.4"] * 4 + ["585.3"] * 3
    rare += ["38341003"] * 5 + ["233604007"] * 4 + ["431855005"] * 1
    cells = common + rare
    cells += ["E11.9"] * (ROWS - len(cells))
    draw.shuffle(cells)
    return cells


def _letters_staged(draw: random.Random) -> "list[str]":
    """Letter-only codes the oracle reasons about: `T?-N?-M?` of letters."""
    cells: "list[str]" = []
    for _row in range(ROWS):
        a = draw.choices("ABCD", weights=[40, 35, 15, 10])[0]
        b = draw.choices("EFGH", weights=[60, 25, 10, 5])[0]
        c = draw.choices("JK", weights=[92, 8])[0]
        cells += [f"T{a}-N{b}-M{c}"]
    return cells


def _letters_absorbed(draw: random.Random) -> "list[str]":
    """Letter-only codes whose rare forms the floor pools (rule A1)."""
    cells = ["AB-CD"] * 300 + ["XY-ZW"] * 200 + ["PQ-RS"] * 60
    cells += ["ABC-DE"] * 4 + ["XYZ-WV"] * 3 + ["MN-OP"] * 5 + ["QR-ST"] * 4 + ["UV-WX"] * 3
    cells += ["AB-CD"] * (ROWS - len(cells))
    draw.shuffle(cells)
    return cells


def _letters_long_tail(draw: random.Random) -> "list[str]":
    """A letter-only long tail beside a small form its census bounds.

    Nine hundred `@@@-@@` codes over 5,952 rows, and twelve `ZQ-?A` codes
    on four rows each: the small form's census lists `Z`, `Q` and `A`, its
    stages hold 24 spellings, and the long tail's settlement, over more
    than 256 places, hands its 48 cells out afresh -- where the sizes drawn
    for each word form are taken instead (`generation._drawn_word_forms`).
    """
    letters = "ABCDEFGHIJKLMNOPRSTUVWXY"
    big = list(dict.fromkeys(
        "".join(draw.choice(letters) for _ in range(3)) + "-" + "".join(draw.choice(letters) for _ in range(2))
        for _ in range(900)
    ))
    cells = _zipf(draw, big, 5952, 1.1)
    cells += [f"ZQ-{letter}A" for letter in "BCDEFGHIJKLM" for _row in range(4)]
    draw.shuffle(cells)
    return cells


# -- one round: describe, generate, validate ------------------------------


def _round(
    tmp_path: pathlib.Path,
    cells: "list[str]",
    seed: int = 0,
    unanswered: "list[str] | None" = None,
    subjects: "list[str] | None" = None,
    people: "list[str] | None" = None,
) -> "tuple[dict, list[str], list[str], list[str]]":
    """(the code column's block, its twin cells, the twin's misses, the table's misses)."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    header = ["code", "other"] if people is None else ["code", "patient"]
    rows = [[cell, "x" if people is None else people[place]] for place, cell in enumerate(cells)]
    table = fixtures.write(tmp_path, "t.csv", fixtures.rows_to_csv(header, rows))
    document = profile.build_document(
        reading.read_table(f"{table}", small_cell_floor=FLOOR),
        taxonomy.Settings(small_cell_floor=FLOOR),
        [] if subjects is None else list(subjects),
        forced_codes=["code"],
        unanswered=unanswered,
        subjects=subjects,
    )
    written = fixtures.write_profile(tmp_path, "t.json", document)
    described = contract.load_profile(f"{written}")
    twin = generation.generate(described, seed)
    path = fixtures.write(tmp_path, "twin.csv", rendering.twin_csv(twin))

    def missed(file: pathlib.Path) -> "list[str]":
        outcome = validation.measure(described, f"{file}")
        return [check.subcheck for check in outcome.checks if check.verdict == validation.MISSED]

    return document["columns"][0], list(twin.columns[0]), missed(path), missed(table)


def _out_of(pattern: str, cells: "list[str]") -> int:
    return sum(1 for cell in cells if cell and not re.fullmatch(pattern, cell))


# -- A1: the pool counted in the commonest named form ---------------------


def test_a1_the_pooled_forms_are_written_in_the_commonest_one(tmp_path: pathlib.Path) -> None:
    """ICD-10 with seventh characters, and blood type `AB-`: no `group-N`, both files valid.

    MUTANT: `taxonomy.pool_absorbed` returning the census as it was -- the
    13 ICD-10 cells and the 4 `AB-` cells come back `group-N`.
    """
    block, twin, twin_missed, source_missed = _round(tmp_path / "icd", _icd10(random.Random(0)))
    assert taxonomy.SUPPRESSED_LABEL not in block["shape_forms"]
    assert block["shape_forms_absorbed"] == "@%%.%"
    assert block["shape_forms"]["@%%.%"] == 374
    assert not [cell for cell in twin if cell.startswith("group-")]
    assert _out_of(ICD10_PATTERN, twin) == 0
    assert twin_missed == [] and source_missed == []
    draw = random.Random(0)
    blood = draw.choices(["O+", "A+", "B+", "O-", "A-", "AB+", "B-", "AB-"], weights=[38, 34, 9, 7, 6, 3, 2, 1], k=ROWS)
    block, twin, twin_missed, source_missed = _round(tmp_path / "blood", blood)
    assert block["shape_forms_absorbed"] == "@+"
    assert not [cell for cell in twin if cell.startswith("group-")]
    assert twin_missed == [] and source_missed == []


def test_a1_red_without_the_absorption(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(taxonomy, "pool_absorbed", lambda published, *_args: (published, ""))
    block, twin, _twin_missed, _source_missed = _round(tmp_path, _icd10(random.Random(0)))
    assert block["shape_forms"][taxonomy.SUPPRESSED_LABEL] == 13
    assert len([cell for cell in twin if cell.startswith("group-")]) == 13


def test_a1_the_validator_absorbs_as_the_producer_did(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the validator's recount absorbing nothing -- the real table misses `@%%.%`."""
    _block, _twin, _twin_missed, source_missed = _round(tmp_path / "now", _icd10(random.Random(0)))
    assert source_missed == []
    recount = validation._form_recount
    monkeypatch.setattr(
        validation, "_form_recount",
        lambda census, cells, floor, absorbing="", distinct=0: recount(census, cells, floor),
    )
    _block, _twin, _twin_missed, source_missed = _round(tmp_path / "mutant", _icd10(random.Random(0)))
    assert "forms.published.@%%.%" in source_missed


def test_a1_moves_nothing_beside_a_clock() -> None:
    """A clock's or a stamp's key keeps the census as it was (plans P4-D373, P4-D393)."""
    for key in ("%%:%%", "%:%% @@", "%%:%%:%%.%%%", "%%%%-%%-%% %%:%%"):
        assert parsing.is_a_time_key(key), key
    for key in ("@%%.%", "%+%=%", "@@@%%@@:@%%.%", "%%%%%-%"):
        assert not parsing.is_a_time_key(key), key
    assert generation._place_plans({"%%:%%": 600, "%:%%": 30}, ["09:15", "9:05"], {}) == {}


# -- A2: the published characters and the floored census -----------------


@pytest.mark.parametrize("seed", [0, 1, 2])
def test_a2_tumour_stages_and_coma_scores_in_pattern(tmp_path: pathlib.Path, seed: int) -> None:
    """TNM and GCS at 600 rows: every stand-in in pattern, both files valid."""
    block, twin, twin_missed, source_missed = _round(tmp_path / "tnm", _tnm(random.Random(seed)), seed)
    lists = block["shape_form_places"]["@%@%@%"]
    assert lists[0] == "T" and lists[2] == "N" and lists[4] == "M"
    assert _out_of(TNM_PATTERN, twin) == 0
    assert twin_missed == [] and source_missed == []
    block, twin, twin_missed, source_missed = _round(tmp_path / "gcs", _gcs(random.Random(seed)), seed)
    assert block["shape_form_places"]["@%@%@%"] == ["E", "1234", "V", "12345", "M", "123456"]
    assert _out_of(GCS_PATTERN, twin) == 0
    assert twin_missed == [] and source_missed == []


def test_a2_red_without_the_census(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: no census published -- every coma score's stand-in is out of pattern."""
    monkeypatch.setattr(taxonomy, "held_back_places", lambda *_args: {})
    _block, twin, _twin_missed, _source_missed = _round(tmp_path, _gcs(random.Random(0)))
    assert _out_of(GCS_PATTERN, twin) > 500


def test_a2_red_without_the_published_characters(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: no stepping plan -- tumour stages filled from the alphabet again."""
    monkeypatch.setattr(generation, "_place_plans", lambda *_args: {})
    _block, twin, _twin_missed, _source_missed = _round(tmp_path, _tnm(random.Random(0)))
    assert _out_of(TNM_PATTERN, twin) > 20


def test_a2_keeps_the_vocabulary_prefix(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """i2b2's `ICD10CM:` kept on every stand-in (row 49).

    MUTANT: no stepping plan -- the prefix is filled from the alphabet (`AAA00AA:`).
    """
    block, twin, twin_missed, source_missed = _round(tmp_path / "now", _concepts(random.Random(0)))
    assert block["suppressed_levels"] > 0
    assert block["shape_form_places"]["@@@%%@@:@%%.%"][:8] == ["I", "C", "D", "1", "0", "C", "M", ""]
    assert _out_of(CONCEPT_PATTERN, twin) == 0
    assert twin_missed == [] and source_missed == []
    monkeypatch.setattr(generation, "_place_plans", lambda *_args: {})
    _block, twin, _twin_missed, _source_missed = _round(tmp_path / "mutant", _concepts(random.Random(0)))
    assert _out_of(CONCEPT_PATTERN, twin) > 0


def test_a2_gleason_scores_wear_a_form_now(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`=` is a mark: a held-back Gleason score is a score, not `group-N`.

    MUTANT: the mark set without `=` -- the census names no form and the
    held-back scores are `group-N`.
    """
    block, twin, twin_missed, _source = _round(tmp_path / "now", _gleason(random.Random(0)))
    assert "%+%=%" in block["shape_forms"]
    assert _out_of(GLEASON_PATTERN, twin) == 0 and twin_missed == []
    monkeypatch.setattr(parsing, "SHAPE_MARKS", "-./_:#*()[]+,")
    _block, twin, _twin_missed, _source = _round(tmp_path / "mutant", _gleason(random.Random(0)))
    assert [cell for cell in twin if cell.startswith("group-")]


def test_a2_a_forced_place_publishes_no_census() -> None:
    """ZS.5's forced case: an empty place beside more than (a - 1)(f - 1) held-back cells.

    Ninety-one held-back cells `X0` to `X9`, each figure on 9 or 10 cells,
    fix every figure's count inside 1..10, so the form is not named; at 90
    cells the bound holds and the place lists nothing.
    """
    def held(total: int) -> "list[str]":
        cells = [f"X{figure}" for figure in range(10) for _cell in range(9)]
        return cells + [f"X{figure}" for figure in range(total - 90)]

    census = {"@%": 500}
    assert taxonomy.held_back_places(held(91), ["A1"], census, 11) == {}
    assert taxonomy.held_back_places(held(90), ["A1"], census, 11) == {"@%": ["X", ""]}


def test_a2_counts_its_characters_in_people(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Beside a person column, `M1` on 48 held-back rows of 3 patients is not listed.

    Twelve stages with `M1`, four rows each, all held back by the floor,
    put `M1` on 48 rows -- the census line in rows -- and on 3 patients.
    MUTANT: the people recount left out -- `M1` listed from its rows.
    """
    draw = random.Random(0)
    cells = [cell for cell in _tnm(draw) if cell.endswith("M0")][: ROWS - 48]
    rare = [f"T{t}N{n}M1" for t in "123" for n in "0123"]
    cells += [code for code in rare for _row in range(4)]
    people = [f"P{place % 300:04d}" for place in range(len(cells) - 48)]
    people += [f"Q{place % 3}" for place in range(48)]
    block, _twin, _twin_missed, _source = _round(tmp_path / "now", cells, subjects=["patient"], people=people)
    assert block["role"] in ("categorical", "long_tail_labels")
    assert block["shape_form_places"]["@%@%@%"][5] == "0"
    monkeypatch.setattr(profile, "_places_in_subjects", lambda described, *_args: described)
    block, _twin, _twin_missed, _source = _round(tmp_path / "mutant", cells, subjects=["patient"], people=people)
    assert block["shape_form_places"]["@%@%@%"][5] == "01"


def test_rule_u_no_census_while_an_identifier_question_is_open(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """HX's case (plan P4-D401; the stand-ins page's rule U): another column's open question holds the census.

    MUTANT: the hold left out -- the tumour stages' census is published
    while the record number's question is open.
    """
    cells = _tnm(random.Random(0))
    people = [f"{100000 + place}" for place in range(ROWS)]
    block, twin, _twin_missed, _source = _round(tmp_path / "now", cells, unanswered=["patient"], people=people)
    assert "shape_form_places" not in block
    monkeypatch.setattr(taxonomy, "without_places", lambda column: column)
    block, _twin, _twin_missed, _source = _round(tmp_path / "mutant", cells, unanswered=["patient"], people=people)
    assert "shape_form_places" in block


def test_a2_the_validator_holds_each_listed_character(tmp_path: pathlib.Path) -> None:
    """A twin writing the census's `M1` on no cell misses `places.published.@%@%@%`."""
    cells = _tnm(random.Random(0))
    block, twin, twin_missed, _source = _round(tmp_path, cells)
    assert twin_missed == []
    described = contract.load_profile(f"{tmp_path / 't.json'}")
    published = {entry["label"] for entry in block["levels"]}
    rewritten = [
        cell[:5] + "0" if cell and parsing.folded(cell) not in published and cell.endswith("M1") else cell
        for cell in twin
    ]
    rows = [[cell, "x"] for cell in rewritten]
    path = fixtures.write(tmp_path, "short.csv", fixtures.rows_to_csv(["code", "other"], rows))
    outcome = validation.measure(described, f"{path}")
    assert "places.published.@%@%@%" in [check.subcheck for check in outcome.checks if check.verdict == validation.MISSED]


def test_a2_the_twin_s_report_measures_the_census(tmp_path: pathlib.Path) -> None:
    """The twin's report measures the census where it is published, as V16.2 holds it (method G12.12a).

    The registry and the label matrix dispose `shape_form_places` APPROXIMATED,
    so the twin's report carries one record for a column that publishes a
    census: the listed characters against those the twin's held-back cells
    hold on the line, both ends the listed count. The tumour stages' twin is
    inside; the same cells with `M1` written `M0` fall short of the line, as
    the validator's `places.published.@%@%@%` says, and the record is outside.
    A column with no census carries no record. Red on the mutant that drops
    the record (`_places_approximations` answering nothing).
    """
    cells = _tnm(random.Random(0))
    block, twin_cells, twin_missed, _source = _round(tmp_path, cells)
    assert block.get("shape_form_places") and twin_missed == []
    described = contract.load_profile(f"{tmp_path / 't.json'}")
    column = described.columns[0]
    assert isinstance(column.facts, contract.LabelFacts)
    listed = 0
    for _form, lists in column.shape_form_places:
        for characters in lists:
            listed = listed + len(characters)
    twin = generation.generate(described, 0)
    records = [found for found in twin.outcomes[0].approximations if found.fact == "shape_form_places"]
    assert [(found.published, found.achieved, found.lowest, found.highest, found.inside) for found in records] == [
        (f"{listed}", f"{listed}", f"{listed}", f"{listed}", True)
    ]
    assert [found.fact for found in twin.outcomes[1].approximations if found.fact == "shape_form_places"] == []
    published = {entry["label"] for entry in block["levels"]}
    rewritten = [
        cell[:5] + "0" if cell and parsing.folded(cell) not in published and cell.endswith("M1") else cell
        for cell in twin_cells
    ]
    short = generation._places_approximations(column, column.facts, rewritten, FLOOR)
    assert len(short) == 1 and not short[0].inside and int(short[0].achieved) < listed


# -- A3: a held-back number is written in its own form --------------------


def test_a3_row_44_meets_its_published_form(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """PCORnet diagnoses: `%%%.%` at 21 on the twin, validate clean (row 44).

    MUTANT: the drawn split refused -- the 29 numbers come back 10, 9, 6
    and 4 and the twin writes `%%%.%` on 24 cells.
    """
    block, twin, twin_missed, source_missed = _round(tmp_path / "now", _pcornet_dx(random.Random(0)))
    assert block["shape_forms"]["%%%.%"] == 21
    assert sum(1 for cell in twin if parsing.shape_form(cell) == "%%%.%") == 21
    assert twin_missed == [] and source_missed == []
    monkeypatch.setattr(generation, "_drawn_split_stands", lambda *_args: False)
    _block, twin, twin_missed, _source = _round(tmp_path / "mutant", _pcornet_dx(random.Random(0)))
    assert sum(1 for cell in twin if parsing.shape_form(cell) == "%%%.%") == 24
    assert "forms.published.%%%.%" in twin_missed


def _loinc_20000(draw: random.Random) -> "list[str]":
    """LOINC codes over 20,000 rows, as K-HZ-11's driver writes them (its seed 2)."""
    found: "dict[str, int]" = {}
    while len(found) < 2000:
        body = draw.randrange(100, 100000)
        found[f"{body}-{sum(int(c) for c in f'{body}') % 10}"] = 1
    return _zipf(draw, list(found), 20000, 1.1)


def test_a2_a_census_form_keeps_the_labels_it_was_drawn(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """One case at the table floor (20,000 rows): LOINC's three-figure form keeps its census.

    Its 40 held-back cells, whose census lists a last `0` on the line,
    take the ten labels its stages' ten free spellings allow, not forty
    of one row each. MUTANT: the settlement's own arrangement kept
    (`_drawn_word_forms` returning it) -- the twin misses
    `places.published.%%%-%`.
    """
    cells = _loinc_20000(random.Random(4393))
    block, _twin, twin_missed, source_missed = _round(tmp_path / "now", cells, 2)
    assert block["shape_form_places"]["%%%-%"][4] == "0"
    assert twin_missed == [] and source_missed == []
    monkeypatch.setattr(generation, "_drawn_word_forms", lambda shared, *_args: shared)
    _block, _twin, twin_missed, _source = _round(tmp_path / "mutant", cells, 2)
    assert "places.published.%%%-%" in twin_missed


def test_a2_no_leading_nought_where_the_column_writes_none(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The same 20,000 LOINC codes: a first place nothing lists opens as the published codes open.

    The three-figure form's census lists nothing at its first place and no
    published code wears the form; every published code opens with a
    figure from 1 to 9, so no stand-in opens with a nought (K-HZ-11 at
    seed 2: 9 cells `005-0` before). MUTANT: `_opening_figures` answering
    all ten figures -- the twin writes `005-0` again.
    """
    cells = _loinc_20000(random.Random(4393))
    real = set(cells)
    block, twin, twin_missed, _source = _round(tmp_path / "now", cells, 2)
    assert block["shape_form_places"]["%%%-%"][0] == ""
    assert not any(level["label"].startswith("0") for level in block["levels"])
    stand_ins = [cell for cell in twin if cell and cell not in real]
    assert stand_ins and not [cell for cell in stand_ins if not re.fullmatch(r"[1-9]\d{0,5}-\d", cell)]
    assert twin_missed == []
    monkeypatch.setattr(generation, "_opening_figures", lambda _written: "0123456789")
    _block, twin, _missed, _source = _round(tmp_path / "mutant", cells, 2)
    assert [cell for cell in twin if cell and cell not in real and cell.startswith("0")]


def test_a3_a_revenue_code_keeps_its_last_nought(monkeypatch: pytest.MonkeyPatch) -> None:
    """K-P4-11's UB-04 fixture at a floor of 11: every made-up code ends in 0.

    Every published revenue code is a multiple of ten, so the ladder and the
    pooled placement step on ten (`parsing.whole_number_grain`) and the
    validator's window on the pooled mean is drawn on that grid; both files
    validate. MUTANT: no grain -- `4583` and the like, as before.
    """
    import test_p4d19_declared_codes as codes

    def stand_ins() -> "list[str]":
        values = codes._SYSTEMS["ub04_rev"]
        document = codes._described(values, name="ub04_rev", codes=["ub04_rev"], floor=FLOOR)
        twin = generation.generate(codes._loaded(document), 3)
        real = set(values)
        return [cell for cell in twin.columns[0] if cell and cell not in real]

    made = stand_ins()
    assert made and all(cell.endswith("0") for cell in made)
    assert parsing.whole_number_grain([450, 250, 1000]) == 10
    assert parsing.whole_number_grain([450]) == 1
    assert taxonomy.pooled_window(["0450", "0250", "alpha"]) == 20.0
    monkeypatch.setattr(parsing, "whole_number_grain", lambda _values, _held=0: 1)
    assert [cell for cell in stand_ins() if not cell.endswith("0")]


# -- the repair of lane CODES-1 (its first skeptic and its statistics skeptic)


def _described_at(
    tmp_path: pathlib.Path, cells: "list[str]", floor: int, people: "list[str] | None" = None
) -> "tuple[dict, contract.Profile]":
    """The code column's block and the loaded description at ``floor`` (``people`` declared)."""
    tmp_path.mkdir(parents=True, exist_ok=True)
    rows = [[cell, "x" if people is None else people[place]] for place, cell in enumerate(cells)]
    table = fixtures.write(tmp_path, "t.csv", fixtures.rows_to_csv(["code", "patient"], rows))
    subjects = None if people is None else ["patient"]
    document = profile.build_document(
        reading.read_table(f"{table}", small_cell_floor=floor),
        taxonomy.Settings(small_cell_floor=floor),
        [] if subjects is None else list(subjects),
        forced_codes=["code"],
        subjects=subjects,
    )
    written = fixtures.write_profile(tmp_path, "t.json", document)
    return document["columns"][0], contract.load_profile(f"{written}")


def _one_level_forced(floor: int, declared: bool) -> "tuple[list[str], list[str] | None]":
    """The first skeptic's Z99 shape at 20,000 rows (wave6/CODES-1-sk1-work/pin.py).

    Forty published codes on the bulk of the rows; held back, `Z99` on the
    census line less one cell and two stragglers `Z98` and `Y99`, each
    sharing all but one place with it, so each place lists one character
    on the line -- in people too where each held-back cell is its own
    person.
    """
    draw = random.Random(0)
    line = parsing.census_floor(floor)
    common = [f"{'ABCDEFGHIJKLMNOPQRST'[i % 20]}{i % 10}{(3 * i) % 10}" for i in range(40)]
    held = ["Z99"] * (line - 1) + ["Z98", "Y99"]
    cells = [draw.choice(common) for _ in range(20000 - len(held))] + held
    people = [f"P{draw.randrange(2000):06d}" for _ in range(20000 - len(held))]
    people += [f"Q{place:06d}" for place in range(len(held))]
    order = list(range(20000))
    draw.shuffle(order)
    return [cells[i] for i in order], ([people[i] for i in order] if declared else None)


def test_a2_a_census_naming_one_held_back_spelling_is_refused(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first skeptic's item 2 (HIPAA; the owner's R1/Q7): no census pins a held-back level.

    `Z99` held back on the line less one cell beside `Z98` and `Y99`: each
    place lists one character, so H - k(H - line) cells are `Z99` and the
    description's own counts would fix its count at 9 or 10 (floor 11) or
    18 or 19 (floor 20). At 20,000 rows, floor 11 and 20, the person column
    absent and declared, the form is not named and the twin writes no
    `Z99`. MUTANT: `taxonomy.places_name_a_spelling` answering False (the
    rows' path and the people's alike) -- `{"@%%": ["Z", "9", "9"]}`.
    """
    for floor in (11, 20):
        for declared in (False, True):
            cells, people = _one_level_forced(floor, declared)
            block, described = _described_at(tmp_path / f"{floor}-{declared}", cells, floor, people)
            assert "@%%" in block["shape_forms"]
            assert "@%%" not in (block.get("shape_form_places") or {}), (floor, declared)
            if floor == 11 and not declared:
                assert "Z99" not in generation.generate(described, 0).columns[0]
    assert taxonomy.places_name_a_spelling("@%%", ["Z", "9", "9"], 12, 11)
    assert not taxonomy.places_name_a_spelling("@%%", ["Z", "9", "89"], 22, 11)
    assert not taxonomy.places_name_a_spelling("@%%", ["Z", "9", "9"], 22, 11)
    monkeypatch.setattr(taxonomy, "places_name_a_spelling", lambda *_args: False)
    for declared in (False, True):
        cells, people = _one_level_forced(11, declared)
        block, _described = _described_at(tmp_path / f"mutant-{declared}", cells, 11, people)
        assert block["shape_form_places"]["@%%"] == ["Z", "9", "9"], declared


def test_a2_the_people_recount_refuses_a_forced_place(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first skeptic's item 4 (a): a place the people recount empties beside more than (a - 1)(f - 1) cells.

    Twenty held-back codes `X0` to `Y9`, six rows each: in rows every
    figure holds 12 cells and is listed, but each figure's cells belong to
    five patients, so the recount in people empties the second place
    beside 120 held-back cells, more than 9 x 10: every figure would then
    hold one cell to ten, a count the description would fix, and the form
    is not named. MUTANT: the people path's forced refusal off (`refused`
    left False, the skeptic's M11) -- `{"@%": ["XY", ""]}` is published.
    """
    common = [f"A{figure}" for figure in "12345"]
    draw = random.Random(0)
    cells = [draw.choice(common) for _ in range(ROWS - 120)]
    people = [f"P{draw.randrange(300):04d}" for _ in range(ROWS - 120)]
    for letter in "XY":
        for figure in "0123456789":
            for row in range(6):
                cells += [f"{letter}{figure}"]
                people += [f"Q{figure}{row % 5}"]
    block, _described = _described_at(tmp_path / "now", cells, FLOOR, people)
    assert block["suppressed_levels"] == 20
    assert "@%" not in (block.get("shape_form_places") or {})
    taken = profile._places_in_subjects

    def unrefused(described: taxonomy.ColumnProfile, *args: object) -> taxonomy.ColumnProfile:
        places = dict(described.details["shape_form_places"])
        recounted = taken(described, *args)  # type: ignore[arg-type]
        if "@%" in places and "@%" not in recounted.details.get("shape_form_places", {}):
            return taxonomy.with_places(recounted, {"@%": [places["@%"][0], ""]})
        return recounted

    monkeypatch.setattr(profile, "_places_in_subjects", unrefused)
    block, _described = _described_at(tmp_path / "mutant", cells, FLOOR, people)
    assert block["shape_form_places"]["@%"] == ["XY", ""]


def _from_the_first(form: str, stages: "tuple[tuple[str, ...], ...]", closed: bool) -> "list[list[str]]":
    """`generation._plan_blocks` widening from the FIRST place (the first skeptic's M5)."""
    positions = [at for at in range(len(form)) if form[at] in generation._PLACE_ALPHABETS]
    whole = tuple([generation._PLACE_ALPHABETS[form[at]] for at in positions])
    chain = [tuple([stage[at] if stage[at] else whole[index] for index, at in enumerate(positions)]) for stage in stages]
    if closed:
        chain += [whole]
    blocks: "list[list[str]]" = [list(chain[0])]
    for later in range(1, len(chain)):
        before, after = chain[later - 1], chain[later]
        for cut in range(len(positions)):
            gained = "".join(mark for mark in after[cut] if mark not in before[cut])
            if gained:
                blocks += [list(before[:cut]) + [gained] + list(after[cut + 1 :])]
    return blocks


def test_a2_the_prefix_outlasts_the_narrow_sets(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first skeptic's item 4 (b): row 49's prefix kept where stages (1) and (2) run out.

    Two published concepts and 37 held-back ones, each `ICD10CM:A24.0`
    with one place changed: every place lists one character, stages (1)
    and (2) hold 24 spellings, so the walk reaches the alphabet (stage 3),
    which widens from the LAST place: every stand-in keeps `ICD10CM:`.
    MUTANT: widening from the first place (the skeptic's M5) -- the
    alphabet opens on the prefix's `I` and stand-ins lose `ICD10CM:`.
    """
    held: "list[str]" = []
    for letter in "BCDFGHJKLN":
        held += [f"ICD10CM:{letter}24.0"]
    for figure in "013456789":
        held += [f"ICD10CM:A{figure}4.0", f"ICD10CM:A2{figure if figure != '4' else '2'}.0", f"ICD10CM:A24.{figure if figure != '0' else '2'}"]
    held = list(dict.fromkeys(held))
    cells = [code for code in held for _row in range(5)]
    cells += ["ICD10CM:E11.9"] * 250 + ["ICD10CM:E11.8"] * (ROWS - 250 - len(cells))
    random.Random(0).shuffle(cells)
    real = set(cells)
    block, twin, twin_missed, source_missed = _round(tmp_path / "now", cells)
    lists = block["shape_form_places"]["@@@%%@@:@%%.%"]
    assert lists == ["I", "C", "D", "1", "0", "C", "M", "", "A", "2", "4", "", "0"]
    published = {level["label"] for level in block["levels"]}
    held_back = [cell for cell in twin if cell and cell not in published]
    assert len(set(held_back)) > 24
    assert all(cell.startswith("ICD10CM:") for cell in held_back)
    assert _out_of(CONCEPT_PATTERN, twin) == 0
    assert twin_missed == [] and source_missed == []
    monkeypatch.setattr(generation, "_plan_blocks", _from_the_first)
    _block, twin, _twin_missed, _source = _round(tmp_path / "mutant", cells)
    assert [cell for cell in twin if cell and cell not in real and not cell.startswith("ICD10CM:")]


def _mixed_clocks() -> "list[str]":
    """The first skeptic's column of clock times beside words (wave6/CODES-1-sk1-work/clocks.py)."""
    draw = random.Random(7)
    common = ["09:15", "10:30", "pending", "N/A"]
    rare = [f"{h:02d}:{m:02d}" for h in range(24) for m in range(0, 60, 7)] + [f"note{k}" for k in range(300)]
    return [draw.choice(common) if draw.random() > 0.2 else draw.choice(rare) for _row in range(20000)]


def test_a2_a_census_on_words_moves_no_clock_byte(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The first skeptic's item 3 (MUST NOT change a clock or stamp byte), at 20,000 rows.

    Clock times beside words: the census on the words' forms leaves every
    clock cell of the twin where and as the description without that
    census writes it (the base's bytes: wave6/CODES-1/repair1/probes
    clk-base and clk-head). MUTANT: the census's label bound entering the
    draw of sizes beside a clock's key (`_census_bounds_labels` answering
    True) -- one clock cell moves (`19:32` 5 to 4, `18:06` 1 to 2).
    """
    cells = _mixed_clocks()
    block, described = _described_at(tmp_path / "now", cells, FLOOR)
    assert block["shape_form_places"]
    document = json.loads((tmp_path / "now" / "t.json").read_text(encoding="utf-8"))
    del document["columns"][0]["shape_form_places"]
    bare = contract.load_profile(f"{fixtures.write_profile(tmp_path, 'bare.json', document)}")

    def clocks(loaded: contract.Profile) -> "list[tuple[int, str]]":
        twin = generation.generate(loaded, 0).columns[0]
        return [(at, cell) for at, cell in enumerate(twin) if re.fullmatch(r"\d\d:\d\d", cell)]

    kept = clocks(bare)
    assert len(kept) > 9000 and clocks(described) == kept
    monkeypatch.setattr(generation, "_census_bounds_labels", lambda _census: True)
    assert clocks(described) != kept


def _distinct_codes(draw: random.Random, make: "object", count: int) -> "list[str]":
    found: "dict[str, int]" = {}
    while len(found) < count:
        found[make(draw)] = 1  # type: ignore[operator]
    return list(found)


def _icd10_20000(draw: random.Random) -> "list[str]":
    """ICD-10 codes over 20,000 rows, as K-HZ-11's driver writes them (its seed 0)."""
    def make(d: random.Random) -> str:
        head = f"{d.choice('ABCDEFGHIJKLMNOPQRSTVWXYZ')}{d.randrange(0, 100):02d}"
        tail = d.choice(["", f".{d.randrange(0, 10)}", f".{d.randrange(0, 100):02d}", f".{d.randrange(0, 1000):03d}{d.choice('ADS')}"])
        return head + tail
    return _zipf(draw, _distinct_codes(draw, make, 1500), 20000, 1.15)


def test_a2_the_places_of_a_stand_in_do_not_step_together(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The statistics skeptic's item 1: no lockstep across places, at 20,000 rows.

    A tie between the fewest-tallied characters of a place breaks by a
    fixed keyed word, independent at each place (`generation._tie_word`),
    so ICD-10's `@%%.%` stand-ins hold every figure equal on at most 3 %
    of their cells (the real held-back cells: about 1 %). MUTANT: the
    first listed on a tie -- `A00.0`, `B11.1`, `C22.2`: 36 % before.
    """
    cells = _icd10_20000(random.Random(4391))
    real = set(cells)
    block, described = _described_at(tmp_path, cells, FLOOR)
    assert block["shape_form_places"]["@%%.%"]

    def share() -> float:
        made = [cell for cell in generation.generate(described, 0).columns[0] if cell and cell not in real]
        tail = [cell for cell in made if parsing.shape_form(cell) == "@%%.%"]
        assert len(tail) > 100
        return sum(1 for cell in tail if len(set(cell[1] + cell[2] + cell[4])) == 1) / len(tail)

    assert share() <= 0.03
    monkeypatch.setattr(generation, "_tie_word", lambda *_args: 0)
    assert share() > 0.2


def test_a3_a_declared_code_keeps_the_published_widths_and_ends(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The statistics skeptic's item 2: APC codes at 20,000 rows keep four figures inside the published ends.

    Every published APC code is a whole number of four figures from 1,054
    to 9,971 (K-HZ-10's driver, seed 0): every made-up code is too.
    MUTANT: the ladder unbounded (`_with_code_ends` returning the ladder
    as it was) -- `905` to `990` and `1000` to `1053`, as on the base.
    """
    draw = random.Random(4390)
    cells = _zipf(draw, _distinct_codes(draw, lambda d: f"{d.randrange(1000, 9999)}", 3000), 20000, 1.1)
    real = set(cells)
    block, described = _described_at(tmp_path, cells, FLOOR)
    published = [int(level["label"]) for level in block["levels"]]
    low, high = min(published), max(published)

    def off() -> int:
        made = [cell for cell in generation.generate(described, 0).columns[0] if cell and cell not in real]
        assert len(made) > 1000 and all(cell.isdigit() for cell in made)
        return sum(1 for cell in made if len(cell) != 4 or not low <= int(cell) <= high)

    assert off() == 0
    monkeypatch.setattr(generation, "_with_code_ends", lambda ladder, _column, _owed: ladder)
    assert off() > 0


def test_a3_a_published_number_below_nought_keeps_the_ladder(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Rule A3's ends and widths hold only where no published number is below nought (the oracle's own condition, A-P4-59).

    APC's shape at 20,000 rows with `-1` on 2,000 of them: a number below
    nought is not figures alone, so the twin is the one G8.3a's ladder as
    it was writes. MUTANT: `_with_code_ends` keeping the ends below nought
    too (part 36's `ladder.lowest < 0` dropped), the product then parting
    from the oracle's `with_code_ends`.
    """
    draw = random.Random(4390)
    cells = _zipf(draw, _distinct_codes(draw, lambda d: f"{d.randrange(1000, 9999)}", 3000), 18000, 1.1)
    cells = cells + ["-1"] * 2000
    draw.shuffle(cells)
    _block, described = _described_at(tmp_path, cells, FLOOR)
    kept = generation.generate(described, 0).columns[0]
    assert "-1" in kept
    monkeypatch.setattr(generation, "_with_code_ends", lambda ladder, _column, _owed: ladder)
    assert generation.generate(described, 0).columns[0] == kept


# -- the second repair of lane CODES-1 (its combined verify and Codex's review)


def _singles_only(form: str, lists: "list[str]", held: int, line: int, _published: int = 0) -> bool:
    """`taxonomy.places_name_a_spelling` as the first repair wrote it: one character at every place."""
    places = 0
    for at in range(len(form)):
        if form[at] not in taxonomy.PLACE_ALPHABETS:
            continue
        if at >= len(lists) or len(lists[at]) != 1:
            return False
        places = places + 1
    return places > 0 and held - places * (held - line) >= 1


def _pair_held(floor: int, declared: bool) -> "tuple[list[str], list[str] | None]":
    """The combined verify's item 1 shape at 20,000 rows (wave6/CODES-1-verify-work/pair.py).

    Forty published codes `A0` to `D9`; held back, `X8` and `X9` on the
    census line less one cell each and two stragglers `W8` and `W9`, each
    held-back cell its own patient where the person column is declared.
    """
    draw = random.Random(0)
    line = parsing.census_floor(floor)
    common = [f"{letter}{figure}" for letter in "ABCD" for figure in "0123456789"]
    held = ["X8"] * (line - 1) + ["X9"] * (line - 1) + ["W8", "W9"]
    cells = [draw.choice(common) for _ in range(20000 - len(held))] + held
    people = [f"P{draw.randrange(2000):06d}" for _ in range(20000 - len(held))]
    people += [f"Q{place:06d}" for place in range(len(held))]
    order = list(range(20000))
    draw.shuffle(order)
    return [cells[i] for i in order], ([people[i] for i in order] if declared else None)


def test_a2_a_census_naming_a_product_of_held_back_spellings_is_refused(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 1 (HIPAA; the owner's R1/Q7): no census pins held-back levels read as a product.

    `X` listed beside `8` and `9`: at least f(1 + 2) - H = f cells hold
    `X8` or `X9` (H = 2f), more than the one spelling's f - 1, so both are
    held-back levels the description would name, each pinned inside
    1..f-1. At 20,000 rows, floors 11 and 20, the person column absent and
    declared, the form is not named. MUTANT: the first repair's helper,
    one character at every place (`_singles_only`) -- `{"@%": ["X", "89"]}`.
    """
    assert taxonomy.places_name_a_spelling("@%", ["X", "89"], 22, 11)
    assert taxonomy.places_name_a_spelling("@%", ["X", "89"], 40, 20)
    assert not taxonomy.places_name_a_spelling("@%", ["XY", "89"], 44, 11)
    for floor in (11, 20):
        for declared in (False, True):
            cells, people = _pair_held(floor, declared)
            block, _described = _described_at(tmp_path / f"{floor}-{declared}", cells, floor, people)
            assert "@%" in block["shape_forms"]
            assert "@%" not in (block.get("shape_form_places") or {}), (floor, declared)
    monkeypatch.setattr(taxonomy, "places_name_a_spelling", _singles_only)
    for declared in (False, True):
        cells, people = _pair_held(11, declared)
        block, _described = _described_at(tmp_path / f"mutant-{declared}", cells, 11, people)
        assert block["shape_form_places"]["@%"] == ["X", "89"], declared


def _product_only(form: str, lists: "list[str]", held: int, line: int, _published: int = 0) -> bool:
    """The combined verify's own reading of item 1: the list sizes as a product, no other bound."""
    sizes = [len(lists[at]) for at in range(len(form)) if form[at] in taxonomy.PLACE_ALPHABETS]
    if not sizes or 0 in sizes:
        return False
    best = {1: 0}
    for size in sizes:
        reached: "dict[int, int]" = {}
        for product, total in best.items():
            for taken in range(1, size + 1):
                reached[product * taken] = max(reached.get(product * taken, 0), total + taken)
        best = reached
    for product, total in best.items():
        named = line * total - (len(sizes) - 1) * held
        if named >= 1 and named > (product - 1) * (line - 1):
            return True
    return False


def _unlisted_and_published(shape: str) -> "list[str]":
    """Two censuses the sizes alone let through, at 20,000 rows (lane CODES-1's second repair).

    `unlisted`: `B0` to `B9` on 10 cells each beside `A5` to `Z5` on 245
    between them, the other codes of the form published: listed `B` and
    `5`. `published`: `X9` held back on 10 cells beside a published `X8`
    and stragglers `W8`, `W9`, `V8`, `X7`: listed `X` and `89`.
    """
    draw = random.Random(0)
    if shape == "unlisted":
        letters = "ACDEFGHIJKLMNOPQRSTUVWXYZ"
        held = [f"B{figure}" for figure in range(10) for _row in range(10)]
        held += [f"{letter}5" for letter in letters for _row in range(10)][:245]
        common = [f"{letter}{figure}" for letter in letters for figure in range(10) if figure != 5]
    else:
        held = ["X9"] * 10 + ["W8"] * 5 + ["W9"] + ["V8"] * 6 + ["X7"]
        common = [f"{letter}{figure}" for letter in "ABCD" for figure in range(10)] + ["X8"]
    cells = [draw.choice(common) for _row in range(20000 - len(held))] + held
    draw.shuffle(cells)
    return cells


def test_a2_a_census_its_unlisted_characters_or_published_spellings_force_is_refused(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane CODES-1's second repair (HIPAA; the owner's R1/Q7): two bounds the list sizes alone leave out.

    An unlisted character holds at most f - 1 held-back cells, so beside
    `B` and `5` alone 95 of the 345 held-back cells begin with `B`, more
    than nine spellings hold: all ten `B?` and all twenty-six `?5` are
    named. And a published spelling holds no held-back cell, so the ten
    cells of `{X8, X9}` lie on `X9` alone, its count fixed at ten. At
    20,000 rows neither census is published. MUTANT: the list sizes read
    as a product alone (`_product_only`, the verify's reading) --
    `{"@%": ["B", "5"]}` and `{"@%": ["X", "89"]}`.
    """
    for shape, lists in (("unlisted", ["B", "5"]), ("published", ["X", "89"])):
        block, _described = _described_at(tmp_path / shape, _unlisted_and_published(shape), FLOOR)
        assert "@%" in block["shape_forms"]
        assert "@%" not in (block.get("shape_form_places") or {}), shape
        monkeypatch.setattr(taxonomy, "places_name_a_spelling", _product_only)
        block, _described = _described_at(tmp_path / f"{shape}-mutant", _unlisted_and_published(shape), FLOOR)
        assert block["shape_form_places"]["@%"] == lists, shape
        monkeypatch.undo()


def _dense_scale(name: str) -> "list[str]":
    """Declared whole-number scales whose every number between the published ends is published (20,000 rows)."""
    draw = random.Random(100)
    if name == "status":
        cells = draw.choices(["1", "2", "3", "4", "5"], weights=[20, 40, 30, 8, 2], k=19995) + ["6"] * 5
    elif name == "codex":
        cells = ["200"] * 9990 + ["201"] * 9990 + ["198", "199", "202", "203"] * 5
    else:
        cells = []
        for _row in range(20000):
            eye = int(draw.choices("1234", weights=[2, 3, 10, 85])[0])
            verbal = int(draw.choices("12345", weights=[2, 2, 3, 8, 85])[0])
            motor = int(draw.choices("123456", weights=[1, 1, 2, 3, 8, 85])[0])
            cells += [f"E{eye}V{verbal}M{motor}" if draw.random() < 0.6 else f"{eye + verbal + motor}"]
    draw.shuffle(cells)
    return cells


def test_a3_a_dense_scale_keeps_its_ladder(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 2 and Codex's item 1: the ends are kept only where they leave room.

    A physical-status class 1 to 5 holding back a 6, `200` and `201` holding back
    `198`, `199`, `202` and `203`, and Glasgow components beside totals 8 to
    15 holding back 7 and 6: every whole number between the published ends
    is published, so the walk steps past the end as before -- no `group-N`
    and the twin validating, at 20,000 rows. MUTANT: the ends kept whatever
    the room (`_free_inside_the_code_ends` answering a thousand million) --
    the held-back cells are written `group-N` and the twin misses its count
    of numbers.
    """
    for name in ("status", "codex", "gcs"):
        _block, twin, twin_missed, source_missed = _round(tmp_path / name, _dense_scale(name))
        assert not [cell for cell in twin if cell.startswith("group-")], name
        assert twin_missed == [] and source_missed == [], name
    monkeypatch.setattr(generation, "_free_inside_the_code_ends", lambda _ladder: 10 ** 9)
    _block, twin, twin_missed, _source = _round(tmp_path / "mutant", _dense_scale("status"))
    assert [cell for cell in twin if cell.startswith("group-")] and twin_missed


def test_a3_the_ladder_crosses_its_grain_in_one_step(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 3: the walk's work does not grow with the codes' magnitude.

    `g` and `9g` on 9,990 rows each beside `2g` and `8g` on ten: a full
    generation asks `_outward_at` a few times at a grain of 10^3 and of
    10^10 alike, and writes what the walk one position at a time writes.
    MUTANT: no position crossed in one step (`_ladder_jump` answering
    nought) -- 4,000 positions at 10^3, the same twin.
    """
    real = generation._outward_at

    def walked(exponent: int) -> "tuple[int, list[str]]":
        grain = 10 ** exponent
        cells = [f"{grain}"] * 9990 + [f"{9 * grain}"] * 9990 + [f"{2 * grain}"] * 10 + [f"{8 * grain}"] * 10
        random.Random(0).shuffle(cells)
        _block, described = _described_at(tmp_path / f"{exponent}", cells, FLOOR)
        asked = [0]

        def counted(*args: object, **kwargs: object) -> "tuple[int, int, int]":
            asked[0] = asked[0] + 1
            return real(*args, **kwargs)  # type: ignore[arg-type]

        monkeypatch.setattr(generation, "_outward_at", counted)
        twin = list(generation.generate(described, 0).columns[0])
        monkeypatch.setattr(generation, "_outward_at", real)
        return asked[0], twin

    small, kept = walked(3)
    large, _twin = walked(10)
    assert small <= 50 and large <= 50
    assert [cell for cell in kept if cell not in ("1000", "9000")]
    monkeypatch.setattr(generation, "_ladder_jump", lambda *_args, **_kwargs: 0)
    slow, stepped = walked(3)
    assert slow > 1000 and stepped == kept


def _pcornet_clocks() -> "list[str]":
    """Codex's item 2 shape: a declared code column of clock times beside PCORnet's diagnoses (20,000 rows)."""
    spec = [
        ("09:15", 19908), ("250.00", 27), ("401.9", 14), ("44054006", 12), ("09:17", 10),
        ("486", 8), ("38341003", 5), ("311", 4), ("272.4", 4), ("233604007", 4),
        ("585.3", 3), ("431855005", 1),
    ]
    cells = [value for value, rows in spec for _row in range(rows)]
    random.Random(0).shuffle(cells)
    return cells


def test_a3_the_drawn_split_moves_no_clock_byte(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 2 (MUST NOT change a clock or stamp byte): the split the sizes were drawn for stands beside no clock.

    The ten held-back `09:17` cells are written as on the base, 589f3d72:
    `00:00` once, `01:37` and `02:14` twice each, `03:51` five times.
    MUTANT: the drawn split taken beside a clock's key (`_drawn_split_kept`
    keeping it) -- `00:00` ten times.
    """
    _block, described = _described_at(tmp_path, _pcornet_clocks(), FLOOR)

    def held_clocks() -> "dict[str, int]":
        twin = generation.generate(described, 0).columns[0]
        return dict(collections.Counter(cell for cell in twin if re.fullmatch(r"\d\d:\d\d", cell) and cell != "09:15"))

    assert held_clocks() == {"00:00": 1, "01:37": 2, "02:14": 2, "03:51": 5}
    monkeypatch.setattr(generation, "_drawn_split_kept", lambda intended, _census: intended)
    assert held_clocks() == {"00:00": 10}


def test_a2_the_people_recount_keeps_nothing_a_row(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 4: the recount in people keeps no key a held-back row.

    Codes of `A` and 23 figures, 2,000 of them on ten rows each beside one
    published code, 2,000 patients: the recount's traced peak stays under
    200 bytes a held-back row (about 41), and its census is the one a key
    a row wrote. MUTANT: a fresh key a row, kept for the walk
    (`_rows_keyed` materialised) -- about 2,100 bytes a held-back row.
    """
    draw = random.Random(0)
    rare = sorted({"A" + "".join(draw.choice("0123456789") for _ in range(23)) for _ in range(2000)})
    cells = ["A" + "0" * 23] * 11 + [code for code in rare for _row in range(10)]
    people = [f"P{draw.randrange(2000):05d}" for _ in cells]
    taken = profile._places_in_subjects
    peaks: "list[int]" = []

    def measured(*args: object) -> taxonomy.ColumnProfile:
        tracemalloc.start()
        try:
            return taken(*args)  # type: ignore[arg-type]
        finally:
            peaks.append(tracemalloc.get_traced_memory()[1])
            tracemalloc.stop()

    monkeypatch.setattr(profile, "_places_in_subjects", measured)
    block, _described = _described_at(tmp_path / "now", cells, FLOOR, people)
    assert block["shape_form_places"] and len(peaks) == 1
    assert peaks[0] < 200 * (len(cells) - 11)

    def fresh(rows: "list[str]", keyed: "dict[str, tuple[str, tuple[str, ...]]]") -> "list[tuple[str, ...]]":
        return [tuple([(key + "\u0000")[:-1] for key in keyed[cell][1]]) if cell in keyed else () for cell in rows]

    monkeypatch.setattr(profile, "_rows_keyed", fresh)
    mutant, _described = _described_at(tmp_path / "mutant", cells, FLOOR, people)
    assert mutant["shape_form_places"] == block["shape_form_places"]
    assert peaks[1] > 1000 * (len(cells) - 11)


def test_an_older_description_holding_equals_still_loads(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 5: a description written before `=` was a mark loads and its twin validates.

    10,000 `3+4=7` beside 10,000 `4+4=8`, written as before the lane: its
    census `{}`, each level's `shape_form_cells` 0. MUTANT: a level holding
    `=` not read as written before the mark (`SHAPE_MARK_SINCE_CODES`
    another character) -- W8 refuses the unchanged document.
    """
    _block, _twin, _missed, _source = _round(tmp_path / "now", ["3+4=7"] * 10000 + ["4+4=8"] * 10000)
    document = json.loads((tmp_path / "now" / "t.json").read_text(encoding="utf-8"))
    column = document["columns"][0]
    column["shape_forms"] = {}
    for level in column["levels"]:
        level["shape_form_cells"] = 0
    for key in ("shape_form_places", "shape_forms_absorbed"):
        column.pop(key, None)
    path = fixtures.write_profile(tmp_path, "older.json", document)
    older = contract.load_profile(f"{path}")
    twin = fixtures.write(tmp_path, "older-twin.csv", rendering.twin_csv(generation.generate(older, 0)))
    assert [check.subcheck for check in validation.measure(older, f"{twin}").checks if check.verdict == validation.MISSED] == []
    monkeypatch.setattr(parsing, "SHAPE_MARK_SINCE_CODES", "\u0000")
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(f"{path}")
    assert "W8" in f"{raised.value}"


def test_a2_a_form_nothing_lists_opens_as_the_published_codes(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 6: the opening rule reaches a form no published spelling wears and no census lists.

    `1234-5` on 19,978 rows beside eleven `ddd-d` codes on two rows each:
    the census names `%%%-%` for 22 cells and lists nothing; no stand-in
    opens with a nought, as no published code does. MUTANT: such a form
    left unplanned (the first repair's skip) -- `000-0`.
    """
    draw = random.Random(3)
    rare: "list[str]" = []
    while len(rare) < 11:
        code = f"{draw.randrange(100, 1000)}-{draw.randrange(10)}"
        if code not in rare:
            rare += [code]
    cells = ["1234-5"] * 19978 + [code for code in rare for _row in range(2)]
    draw.shuffle(cells)
    block, twin, twin_missed, _source = _round(tmp_path / "now", cells)
    assert block["shape_forms"]["%%%-%"] == 22 and not block.get("shape_form_places")
    made = [cell for cell in twin if cell != "1234-5"]
    assert len(made) == 22 and not [cell for cell in made if cell.startswith("0")]
    assert twin_missed == []
    taken = generation._place_plans

    def published_or_listed(
        census: "dict[str, int]", written: "list[str]", listed: "dict[str, tuple[str, ...]]", decimal_comma: bool = False
    ) -> "dict[str, object]":
        plans = taken(census, written, listed, decimal_comma)
        worn = generation._published_places(census, written, decimal_comma)
        return {form: plans[form] for form in plans if form in worn or form in listed}

    monkeypatch.setattr(generation, "_place_plans", published_or_listed)
    _block, twin, _twin_missed, _source = _round(tmp_path / "mutant", cells)
    assert [cell for cell in twin if cell != "1234-5" and cell.startswith("0")]


def test_a_cell_opening_with_equals_wears_no_form(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 7: no form a made-up value could never open with.

    `=999` on 19,800 rows beside `=100` to `=119` on ten each: the census
    names no form opening with `=`, as before the mark, and the twin
    validates. MUTANT: a leading `=` given a form (`SHAPE_MARK_SINCE_CODES`
    another character) -- `=%%%` on 20,000 cells, its held-back cells
    `group-N`, the twin missing the form census.
    """
    cells = ["=999"] * 19800 + [f"={value}" for value in range(100, 120) for _row in range(10)]
    random.Random(0).shuffle(cells)
    block, _twin, twin_missed, _source = _round(tmp_path / "now", cells)
    assert not [form for form in block["shape_forms"] if form.startswith("=")]
    assert twin_missed == []
    monkeypatch.setattr(parsing, "SHAPE_MARK_SINCE_CODES", "\u0000")
    block, _twin, twin_missed, _source = _round(tmp_path / "mutant", cells)
    assert block["shape_forms"]["=%%%"] == 20000 and twin_missed


def test_rule_u_an_open_free_text_person_question_holds_every_census(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 8 (rule U, the stand-ins page's ZS.1 (c)): through the shipped command, at 20,000 rows.

    2,000 letter-only patient names on ten rows each, read as free text
    and put the person question, beside a declared code column of
    `E4V5M6` on 18,810 rows and every other `E1..4V1..5M1..6` on ten: while
    that question is open no census is published. MUTANT: the command's
    rule over every open question offering `identifier` left out
    (`profile.without_census_places` handing the description back) -- the
    code column lists every component.
    """
    draw = random.Random(0)
    names: "list[str]" = []
    while len(names) < 2000:
        name = "".join(draw.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(8))
        if name not in names:
            names += [name]
    codes = ["E4V5M6"] * 18810
    for eye in "1234":
        for verbal in "12345":
            for motor in "123456":
                if (eye, verbal, motor) != ("4", "5", "6"):
                    codes += [f"E{eye}V{verbal}M{motor}"] * 10
    people = [name for name in names for _row in range(10)]
    draw.shuffle(codes)
    draw.shuffle(people)
    table = fixtures.write(tmp_path, "t.csv", fixtures.rows_to_csv(["patient", "code"], [[p, c] for p, c in zip(people, codes)]))

    def described(folder: str) -> "dict[str, dict]":
        out = tmp_path / folder
        out.mkdir()
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            assert cli.main(["profile", f"{table}", "--code", "code", "--out-dir", f"{out}"]) == 0
        document = json.loads(next(out.glob("*profile.json")).read_text(encoding="utf-8"))
        return {block["name"]: block for block in document["columns"]}

    blocks = described("now")
    assert blocks["patient"]["role"] == "free_text"
    assert "shape_form_places" not in blocks["code"]
    monkeypatch.setattr(profile, "without_census_places", lambda document: document)
    assert "shape_form_places" in described("mutant")["code"]


PATHOLOGICAL_PATTERN = r"(y?p)?T[0-4][ab]?N[0-3][ab]?M[01]"


def _pathological(prefixes: "list[str]") -> "list[str]":
    """Pathological tumour stages, `pT1aN1bM0` and `ypT2N0M1` (wave6/CODES-1/repair2/tnm2.py, seed 0; 20,000 rows)."""
    draw = random.Random(77)
    cells: "list[str]" = []
    for _row in range(20000):
        size = draw.choices("01234", weights=[2, 40, 35, 15, 8])[0]
        nodes = draw.choices("0123", weights=[60, 25, 10, 5])[0]
        spread = draw.choices("01", weights=[97, 3])[0]
        prefix = prefixes[0] if len(prefixes) == 1 else draw.choice(prefixes)
        cells += [f"{prefix}T{size}{draw.choice(['', 'a', 'b'])}N{nodes}{draw.choice(['', 'a', 'b'])}M{spread}"]
    return cells


def test_a2_a_place_written_in_small_letters_keeps_them(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """The combined verify's item 3 (code runs unchanged): small letters written as the source wrote them.

    Pathological stages with sub-letters, `pT1aN1bM0` and `ypT2bN0M1`, at
    20,000 rows: the census lists `p`, `y` and the sub-letters `ab`, and
    every held-back cell of the twin keeps the TNM grammar. MUTANT: every
    letter place read as capitals, in the census and the twin
    (`taxonomy._capitals_at` marking each, `generation._place_alphabet`
    the capitals) -- `PT4N2M1`, `BT0KN2M1`, every stand-in off.
    """
    for prefixes in (["p"], ["p", "yp"]):
        block, twin, twin_missed, _source = _round(tmp_path / "-".join(prefixes), _pathological(prefixes))
        assert block["shape_form_places"]["@@%@@%@@%"] == ["p", "T", "01234", "ab", "N", "0123", "ab", "M", "01"]
        published = {level["label"] for level in block["levels"]}
        made = [cell for cell in twin if cell and parsing.folded(cell) not in published]
        assert len(made) > 300 and _out_of(PATHOLOGICAL_PATTERN, made) == 0
        assert twin_missed == []

    def all_capitals(cell: str, form: str, capitals: "dict[str, dict[int, bool]]") -> None:
        for at in range(len(form)):
            if form[at] == parsing.SHAPE_LETTER:
                capitals.setdefault(form, {})[at] = True

    monkeypatch.setattr(taxonomy, "_capitals_at", all_capitals)
    monkeypatch.setattr(generation, "_place_alphabet", lambda kind, _marks: generation._PLACE_ALPHABETS[kind])
    block, twin, _twin_missed, _source = _round(tmp_path / "mutant", _pathological(["p"]))
    published = {level["label"] for level in block["levels"]}
    made = [cell for cell in twin if cell and parsing.folded(cell) not in published]
    assert _out_of(PATHOLOGICAL_PATTERN, made) > len(made) // 2


def _clocks_beside_words(seed: int) -> "list[str]":
    """Clock times beside words of letters alone, which the oracle reasons about (20,000 rows).

    `NOTE-` and one or two letters: the census lists `NOTE` and at most a
    few last letters, so the stages of `@@@@-@@` hold fewer free spellings
    than its labels and the census's label bound binds -- the draw that
    moves a clock where the bound is taken beside one.
    """
    draw = random.Random(seed)
    letters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    words = [f"NOTE-{first}" for first in letters] + [f"NOTE-{first}{second}" for first in "AB" for second in letters]
    common = ["09:15", "10:30", "pending"]
    rare = [f"{hour:02d}:{minute:02d}" for hour in range(24) for minute in range(0, 60, 7)] + words
    return [draw.choice(common) if draw.random() > 0.2 else draw.choice(rare) for _row in range(20000)]


def _oracle_agrees(gen: object, block: dict, twin: "list[str]", declared: bool) -> bool:
    column = json.loads(json.dumps(block))
    column["_code_declared"] = declared
    column["_parse_rate"] = 0.9
    oracle = collections.Counter(gen._label_content(column))  # type: ignore[attr-defined]
    return collections.Counter(cell for cell in twin if cell) == oracle


def test_the_oracle_keeps_a_declared_code_s_ends_and_their_room(tmp_path: pathlib.Path) -> None:
    """The combined verify's item 4 (A-P4-59): the oracle's mirror of rule A3's ends and their room.

    APC codes (the ends kept) and the physical-status class (no room: the ladder as it
    was), declared, at 20,000 rows: the oracle's `_label_content` writes
    the product's twin. MUTANTS: the oracle never keeping the ends
    (`with_code_ends` handing the ladder back; the verify's ORACLE_ends_off)
    -- APC parts; the oracle keeping them whatever the room
    (`free_inside_the_code_ends` a thousand million) -- the physical-status class parts.
    """
    draw = random.Random(4390)
    apc = _zipf(draw, _distinct_codes(draw, lambda d: f"{d.randrange(1000, 9999)}", 3000), 20000, 1.1)
    shapes = {"apc": apc, "status": _dense_scale("status")}
    rounds = {name: _round(tmp_path / name, cells) for name, cells in shapes.items()}
    gen = _oracle()
    for name in shapes:
        block, twin, _missed, _source = rounds[name]
        assert _oracle_agrees(gen, block, twin, True), name
    ends = gen.with_code_ends  # type: ignore[attr-defined]
    gen.with_code_ends = lambda ladder, _column, _owed: ladder  # type: ignore[attr-defined]
    assert not _oracle_agrees(gen, rounds["apc"][0], rounds["apc"][1], True)
    gen.with_code_ends = ends  # type: ignore[attr-defined]
    gen.free_inside_the_code_ends = lambda _ladder: 10 ** 9  # type: ignore[attr-defined]
    assert not _oracle_agrees(gen, rounds["status"][0], rounds["status"][1], True)


def test_the_oracle_keeps_a_clock_s_bytes_beside_a_census(tmp_path: pathlib.Path) -> None:
    """The combined verify's item 4 (A-P4-59): the oracle's mirror of the clock rule.

    Clock times beside words of letters alone, the words' form censused,
    declared and not, at 20,000 rows: the oracle writes the product's
    twin. MUTANT: the oracle's label bound and drawn split taken beside a
    clock's key (`census_bounds_labels` answering True; the verify's
    ORACLE_clock_bound_always) -- the clock cells part.
    """
    gen = _oracle()
    cells = _clocks_beside_words(7)
    found = []
    for declared in (False, True):
        folder = tmp_path / f"{declared}"
        folder.mkdir()
        rows = [[cell, "x"] for cell in cells]
        table = fixtures.write(folder, "t.csv", fixtures.rows_to_csv(["code", "other"], rows))
        document = profile.build_document(
            reading.read_table(f"{table}", small_cell_floor=FLOOR),
            taxonomy.Settings(small_cell_floor=FLOOR),
            [],
            forced_codes=["code"] if declared else [],
        )
        block = document["columns"][0]
        assert block["shape_form_places"]
        loaded = contract.load_profile(f"{fixtures.write_profile(folder, 't.json', document)}")
        twin = list(generation.generate(loaded, 0).columns[0])
        assert _oracle_agrees(gen, block, twin, declared), declared
        found += [(block, twin, declared)]
    gen.census_bounds_labels = lambda _census: True  # type: ignore[attr-defined]
    assert not any([_oracle_agrees(gen, block, twin, declared) for block, twin, declared in found])


def _letter_stages(seed: int) -> "list[str]":
    """Clinical tumour stages written in letters, `T-B-N-C-M-A` (20,000 rows): the oracle reasons about them."""
    draw = random.Random(seed)
    letters = "ABCDE"
    cells: "list[str]" = []
    for _row in range(20000):
        size = int(draw.choices("01234", weights=[2, 40, 35, 15, 8])[0])
        nodes = int(draw.choices("0123", weights=[60, 25, 10, 5])[0])
        spread = int(draw.choices("01", weights=[97, 3])[0])
        cells += [f"T-{letters[size]}-N-{letters[nodes]}-M-{letters[spread]}"]
    return cells


def test_a2_a_short_listed_character_is_swapped_to_the_line(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """Lane CODES-1's second repair: the balanced walk leaves no listed character short where a swap of sizes reaches the line.

    Clinical stages written in letters at 20,000 rows (seed 26): the walk
    hands a listed node letter's few free spellings small stand-ins, and
    two stand-ins' spellings are swapped so every listed character holds
    the line; the twin validates and the oracle writes it. MUTANTS: no
    swap in the product (`_swapped_to_the_line` doing nothing) -- the twin
    misses `places.published`; no swap in the oracle -- it parts from the
    product. (The figure-written stages it was found on, `pT1aN1bM0` beside
    `T1N0M0` and `ypT2N0M1` at 20,000 rows, the oracle cannot run.)
    """
    cells = _letter_stages(26)
    block, twin, twin_missed, _source = _round(tmp_path / "now", cells)
    assert block["shape_form_places"] and twin_missed == []
    gen = _oracle()
    assert _oracle_agrees(gen, block, twin, True)
    gen.swapped_to_the_line = lambda *_args: None  # type: ignore[attr-defined]
    assert not _oracle_agrees(gen, block, twin, True)
    monkeypatch.setattr(generation, "_swapped_to_the_line", lambda *_args: None)
    _block, _twin, twin_missed, _source = _round(tmp_path / "mutant", cells)
    assert [check for check in twin_missed if check.startswith("places.published")]


# -- the contract's two new keys ------------------------------------------


def test_the_loader_reads_both_keys_and_refuses_them_misspoken(tmp_path: pathlib.Path) -> None:
    block, _twin, _missed, _source = _round(tmp_path, _tnm(random.Random(0)))
    document = json.loads((tmp_path / "t.json").read_text(encoding="utf-8"))
    loaded = contract.load_profile(f"{tmp_path / 't.json'}")
    assert dict(loaded.columns[0].shape_form_places)["@%@%@%"][0] == "T"
    cases = [
        ("C6-31h", lambda column: column["shape_form_places"]["@%@%@%"].__setitem__(1, "4321")),
        ("C6-31h", lambda column: column["shape_form_places"]["@%@%@%"].append("")),
        ("C6-31h", lambda column: column["shape_form_places"].__setitem__("@%@%@%", ["", "", "", "", "", ""])),
    ]
    for rule, spoil in cases:
        spoiled = json.loads(json.dumps(document))
        spoil(spoiled["columns"][0])
        path = fixtures.write_profile(tmp_path, "spoiled.json", spoiled)
        with pytest.raises(errors.ProfileError) as raised:
            contract.load_profile(f"{path}")
        assert rule in f"{raised.value}"
    icd = _round(tmp_path / "icd", _icd10(random.Random(0)))[0]
    absorbed = json.loads((tmp_path / "icd" / "t.json").read_text(encoding="utf-8"))
    absorbed["columns"][0]["shape_forms_absorbed"] = "@%%"
    path = fixtures.write_profile(tmp_path, "misnamed.json", absorbed)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(f"{path}")
    assert "C6-31g" in f"{raised.value}"
    assert icd["shape_forms_absorbed"] == "@%%.%"


# -- the oracle agrees (A-P4-59) ------------------------------------------


def _oracle() -> object:
    spec = importlib.util.spec_from_file_location("codes1_oracle", ORACLE)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("shape", ["staged", "absorbed", "drawn"])
def test_the_oracle_writes_the_same_stand_ins(tmp_path: pathlib.Path, shape: str) -> None:
    """Letter-only code columns (the oracle reasons only about stand-ins with no figure):
    the oracle's `_label_content` and the product's twin hold the same cells."""
    gen = _oracle()
    builders = {"staged": _letters_staged, "absorbed": _letters_absorbed, "drawn": _letters_long_tail}
    for seed in (0, 1, 2):
        cells = builders[shape](random.Random(seed))
        block, twin, twin_missed, _source = _round(tmp_path / f"{seed}", cells, seed)
        assert twin_missed == []
        if shape == "staged":
            assert "shape_form_places" in block
        elif shape == "absorbed":
            assert block["shape_forms_absorbed"] == "@@-@@"
        else:
            assert block["shape_form_places"]["@@-@@"] == ["Z", "Q", "", "", "A"]
        column = json.loads(json.dumps(block))
        column["_code_declared"] = True
        column["_parse_rate"] = 0.9
        oracle_cells = collections.Counter(gen._label_content(column))  # type: ignore[attr-defined]
        assert collections.Counter(cell for cell in twin if cell) == oracle_cells
