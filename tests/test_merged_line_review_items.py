"""Batch 4s's fix round: the seven items of the outside review of the merged line (the orchestrator's LANE I4s RULINGS 1).

Each item has its case on the reviewer's own table at the owner's floor (20,000 rows; 1,000 people of 20 rows where a
person column stands beside), RED on the merged head ce75ec54 and green here, a generated case behind it, and a mutant
that turns it red, in the ruling's order:

(1) ITEM 1: mixed-unit pooling writes the one band past 89 in years (`taxonomy.pooled_band`): `12+ months`, the
commonest band open upward beside `0-17 years` to `90-94 years`, wrote `90+ months` on 5,000 of 20,000 rows.
(2) ITEM 6: a band description recording `top_coded_bands` beside no pooling rule is read with its bands by every
reader -- the profile's forced description, the validator's top-code and the chain's reader -- as the generator
reads it: they kept `90-94` and `95+` where the twin wrote `90+` on 8,000 rows.
(3) ITEM 5: the patient layer keeps the band marker (`patient_layer.SAFE_HARBOR_MARKS`): the cells read through the
published block kept `75-99` and `100+` on 4,000 rows each.
(4) ITEM 4: a band is an age of the reach only beside the column's own numbers (`taxonomy.safe_harbor_reach`): a
score's `40-79`, `80-109` and `110-125` were written `40-79` and `80+`.
(5) ITEM 3: a zone word is rewritten at the pooling handoff (`grains.with_offset`): 20,000 Eastern stamps of 2024 in
`EST` and `EDT` were held and written in 2028.
(6) ITEM 2: a label's bound moves inward onto its grid at every size (`contract._on_the_label_grid`): `<1000.00000025`
on a grid of six places was placed at 1000.0 and the twin wrote `1000.000000` on 11 cells below the limit.
(7) ITEM 7: the exclusion step reads a column's present runs once (`taxonomy._RealRuns`), its exclusions as they were.

Invented tables only; every table case runs the commands a person types, nobody at the keyboard, the floor on.
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import os
import pathlib
import random

import pytest

import fixtures
import health_zoo as zoo
from synthtwin import chain, cli, contract, grains, parsing, patient_layer, profile, reading, taxonomy, validation


def _counts(values: "list[str]") -> "dict[str, int]":
    found: "dict[str, int]" = {}
    for value in values:
        found[value] = (found[value] if value in found else 0) + 1
    return found


@contextlib.contextmanager
def _nobody_at_the_keyboard():  # type: ignore[no-untyped-def]
    asked = cli._there_is_somebody_to_ask
    cli._there_is_somebody_to_ask = lambda: False
    try:
        yield
    finally:
        cli._there_is_somebody_to_ask = asked


def _twin_columns(path: pathlib.Path) -> "dict[str, list[str]]":
    with open(path, encoding="utf-8", newline="") as handle:
        rows = list(csv.reader(handle))
    return {name: [row[place] for row in rows[1:]] for place, name in enumerate(rows[0])}


def _commands(folder: pathlib.Path, stem: str, header: "list[str]", rows: "list[list[str]]",
              answers: "dict[str, str] | None" = None) -> "dict[str, object]":
    """Profile the table (nobody at the keyboard, the table floor on), one answers round where ``answers`` names a
    column and an answer it is offered, and generate at seed 0: the description, the questions file and the twin."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / f"{stem}.csv"
    source.write_bytes(zoo.csv_bytes(header, rows))
    described, questions = folder / f"{stem}-profile.json", folder / f"{stem}-questions.json"
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{source}", "--replace"], small_tables_refused=True) == 0
        if answers:
            document = json.loads(questions.read_text(encoding="utf-8"))
            for entry in zoo._entries(document):
                column = f"{entry.get('column', '')}"
                if column in answers and answers[column] in zoo._offered(entry):
                    entry["your_answer"] = answers[column]
            questions.write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")
            assert cli.main(["profile", f"{source}", "--replace", "--answers", f"{questions}"],
                            small_tables_refused=True) == 0
        assert cli.main(["generate", f"{described}", "--replace", "--seed", "0"], small_tables_refused=True) == 0
    return {"description": json.loads(described.read_text(encoding="utf-8")), "source": source, "described": described,
            "questions": json.loads(questions.read_text(encoding="utf-8")),
            "twin": _twin_columns(folder / f"{stem}-twin.csv")}


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    return [block for block in document["columns"] if block["name"] == name][0]  # type: ignore[index,union-attr]


# -- (1) ITEM 1: THE ONE BAND PAST 89 IS WRITTEN IN YEARS -------------------------------------------------------------

_MIXED_UNITS = ("0-17 years", "18-89 years", "90-94 years", "12+ months")


def test_codex_s_mixed_unit_bands_pool_in_years_at_the_table_floor(tmp_path: pathlib.Path) -> None:
    """Codex's item 1 (HIGH): 5,000 rows each of `0-17 years`, `18-89 years`, `90-94 years` and `12+ months`. The
    description, the twin and the validator's top-code of the real cells write the one band past 89 as `90+ years`
    and never `90+ months` (on ce75ec54: `90+ months` on 5,000 rows in all three, a group from seven and a half
    years, loaded strictly and validated clean)."""
    cells = [_MIXED_UNITS[index % 4] for index in range(20000)]
    seen = _commands(tmp_path, "bands", ["age_group"], [[cell] for cell in cells])
    block = _block(seen["description"], "age_group")  # type: ignore[arg-type]
    assert block["top_coded"] == 90 and block["top_coded_bands"] is True
    assert {f"{level['label']}": level["count"] for level in block["levels"]} == {  # type: ignore[index,union-attr]
        "0-17 years": 5000, "18-89 years": 5000, "12+ months": 5000, "90+ years": 5000}
    assert "90+ months" not in json.dumps(seen["description"])
    assert _counts(seen["twin"]["age_group"]).get("90+ years") == 5000  # type: ignore[index]
    assert "90+ months" not in seen["twin"]["age_group"]  # type: ignore[index]
    coded = validation._top_coded_table(reading.read_table(f"{seen['source']}"), {"age_group": 90}, {}, [], (), (),
                                        None, None, frozenset({"age_group"}))
    assert _counts(coded.columns[0]) == {"0-17 years": 5000, "18-89 years": 5000, "12+ months": 5000, "90+ years": 5000}


_OTHER_UNIT_OPENS = ("{}+ months", "{}+ mos", ">= {} months", "{}+ weeks", "{}+ wks", "{}+ days", "> {} days", "{}+ m")
_YEAR_BANDS = ("{}-{} years", "{}-{} yrs", "{}-{}", "{} to {} years", "{}-{} y")
_YEAR_OPENS = ("{}+ years", "{}+", ">= {} yrs", "{} and over", "{}+ y")


def _mixed_unit_columns(draw: random.Random, count: int) -> "list[tuple[list[str], int]]":
    """Columns of age bands of years beside bands open upward written in months, weeks or days, each with the mark of
    its column's unit: closed bands of years chained from 0 or 18 past 90, sometimes a band of years open upward past
    89, and one to three bands of another unit open upward, each band on a drawn number of rows."""
    found: "list[tuple[list[str], int]]" = []
    for _column in range(count):
        mark = draw.choice((90, 90, 90, 1080, 4695, 32871))
        closed = draw.choice(_YEAR_BANDS)
        if mark != 90 and "y" not in closed:
            closed = "{}-{} years"
        cells: "list[str]" = []
        first = draw.choice((0, 18))
        while first < 90 + draw.choice((0, 5, 10)):
            last = min(first + draw.choice((4, 9, 17, 26, 44)), 104)
            cells += [closed.format(first, last)] * draw.randint(20, 60)
            first = last + 1
        if draw.random() < 0.4:
            opened = draw.choice(_YEAR_OPENS)
            if mark != 90 and "y" not in opened:
                opened = "{}+ years"
            cells += [opened.format(first)] * draw.randint(20, 60)
        for _other in range(draw.randint(1, 3)):
            cells += [draw.choice(_OTHER_UNIT_OPENS).format(draw.randint(1, 60))] * draw.randint(40, 200)
        draw.shuffle(cells)
        found += [(cells, mark)]
    return found


def _in_years(band: "taxonomy.AgeBand", mark: int) -> bool:
    """Whether a band reads in years: a unit word of years, or none in a column of years (read here from the unit
    word itself, apart from the product's `_band_cutoff`, which the mutant below changes)."""
    return taxonomy._age_unit_of(band.unit) == "y" if band.unit else mark == taxonomy.TOP_CODE


def _wrongly_pooled(cells: "list[str]", mark: int) -> "list[str]":
    """The cells the top-code writes as the one band past 89 that are no band of years from its first age."""
    coded = taxonomy.top_coded_cells(cells, False, frozenset(), mark)
    start = taxonomy._band_holding_90(cells, frozenset(), mark) if taxonomy.age_bands_past_89(
        cells, frozenset(), True, mark) else taxonomy.TOP_CODE
    wrong: "list[str]" = []
    for written, cell in zip(coded, cells):
        if written == cell:
            continue
        band = taxonomy.a_band_cell(written)
        if band is None or band.end >= 0 or band.start != start or not _in_years(band, mark):
            wrong += [written]
    return wrong


def test_every_generated_mixed_unit_column_writes_its_one_band_in_years() -> None:
    """The class behind item 1, generated: 3,000 columns of bands of years beside bands of months, weeks or days open
    upward, in columns of every unit; every cell the top-code pools is a band open upward IN YEARS from the one band's
    first age (90, or that of a band holding 90), read back by the band reader in the column's unit."""
    draw = random.Random(4561)
    columns = _mixed_unit_columns(draw, 3000)
    pooled = 0
    for cells, mark in columns:
        assert _wrongly_pooled(cells, mark) == [], (mark, sorted(set(cells))[:8])
        pooled += taxonomy.top_coded_cells(cells, False, frozenset(), mark) != cells
    assert pooled > 1200, pooled


def test_the_one_band_in_years_is_red_on_the_unit_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: every band read in years (`_band_cutoff` 90) takes a band of months as the form: Codex's column pools
    to `90+ months` again, and the generated columns write bands of other units."""
    cells = [_MIXED_UNITS[index % 4] for index in range(400)]
    assert set(taxonomy.top_coded_cells(cells)) == {"0-17 years", "18-89 years", "12+ months", "90+ years"}
    monkeypatch.setattr(taxonomy, "_band_cutoff", lambda band, mark=90: 90)
    assert "90+ months" in taxonomy.top_coded_cells(cells)
    assert sum(1 for cells_of, mark in _mixed_unit_columns(random.Random(4561), 200) if _wrongly_pooled(cells_of, mark)) > 50


# -- (2) ITEM 6: EVERY READER RECOGNISES THE BAND MARKER ALONE ---------------------------------------------------------

_OLDEST_APART = ("0-17", "18-44", "45-89", "90-94", "95+")


def _band_description_without_its_pool(folder: pathlib.Path) -> "tuple[contract.Profile, dict[str, object], reading.Table, pathlib.Path]":
    """Codex's item 6 table: 4,000 rows each of `0-17`, `18-44`, `45-89`, `90-94` and `95+`, its description written
    with the Safe Harbor top-code and only the optional pooling field removed (`top_coded=90`, `top_coded_bands`, no
    `top_category_pooled`), loaded strictly."""
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "bands.csv"
    source.write_bytes(zoo.csv_bytes(["age_group"], [[_OLDEST_APART[index % 5]] for index in range(20000)]))
    table = reading.read_table(f"{source}")
    document = profile.build_document(table, taxonomy.Settings(), [], top_code=True, five_figures=[], ages_held=[],
                                      harbor_year=taxonomy.SAFE_HARBOR_REFERENCE_YEAR, harbor_reasons={},
                                      ages_established={})
    block = document["columns"][0]  # type: ignore[index]
    assert block["top_coded"] == 90 and block["top_coded_bands"] is True and "top_category_pooled" in block  # type: ignore[index]
    del block["top_category_pooled"]  # type: ignore[attr-defined]
    block.pop("top_category_people", None)  # type: ignore[attr-defined]
    described = contract.load_profile(f"{fixtures.write_profile(folder, 'bands-profile.json', document)}")
    column = described.columns[0]
    assert column.top_coded == 90 and column.top_coded_bands and column.top_category_pooled < 0
    return described, block, table, source  # type: ignore[return-value]


def _each_reader(described: contract.Profile, block: "dict[str, object]", table: reading.Table,
                 source: pathlib.Path) -> "dict[str, object]":
    """What each reader of the block makes of the real cells: the validator's top-code, the forced description the
    validator runs again, the chain's reader, and the validator's MISSED obligations of the real table."""
    coded = validation._top_coded_table(table, {"age_group": 90}, {}, [], (), (), None, None,
                                        validation._top_banded_here(described, table))
    again = profile.build_document(table, taxonomy.Settings(), [], top_coded_only={"age_group": 90}, top_pooled_only={},
                                   top_banded_only=validation._top_banded_here(described, table))
    chained = chain.described_cells(table, 0, block, taxonomy.Settings(),
                                    {"code": False, "measurement": False, "decimal_comma": False}, "", True)
    outcome = validation.measure(described, f"{source}")
    return {
        "validator": _counts(coded.columns[0]),
        "forced": sorted(f"{level['label']}" for level in again["columns"][0]["levels"]),  # type: ignore[index]
        "chain": _counts(chained),
        "missed": [check.subcheck for check in outcome.checks if check.verdict == validation.MISSED],
    }


_POOLED_AT_90 = {"0-17": 4000, "18-44": 4000, "45-89": 4000, "90+": 8000}


def test_codex_s_band_description_without_its_pool_marker_is_read_with_its_bands(tmp_path: pathlib.Path) -> None:
    """Codex's item 6: the generator writes `90+` on 8,000 rows, and so does every other reader of the block -- the
    validator's top-code, the forced description it runs again (no `90-94`, no `95+` published) and the chain's
    reader -- and the real table meets its own description (on ce75ec54 each kept `90-94` and `95+` on 4,000 rows
    each and the real table missed 10 obligations)."""
    described, block, table, source = _band_description_without_its_pool(tmp_path)
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["generate", f"{tmp_path / 'bands-profile.json'}", "--replace", "--seed", "0"],
                        small_tables_refused=True) == 0
    assert _counts(_twin_columns(tmp_path / "bands-twin.csv")["age_group"]) == _POOLED_AT_90
    read = _each_reader(described, block, table, source)
    assert read == {"validator": _POOLED_AT_90, "forced": ["0-17", "18-44", "45-89", "90+"], "chain": _POOLED_AT_90,
                    "missed": []}, read


def test_every_reader_recognises_the_band_marker_alone_on_generated_blocks() -> None:
    """The class behind item 6, generated: every set of the three markers a top-coded block may record without its
    pooling rule (words, ends, bands; 2,000 generated columns of bands with ages written beside them): wherever the
    band marker stands, the validator's top-code and the chain's reader write the bands past 89 as one band, as the
    generator reads the block."""
    draw = random.Random(4562)
    checked = 0
    for _column in range(2000):
        scheme = draw.choice((["0-17", "18-44", "45-89", "90-94", "95+"], ["0-4", "5-9", "85-89", "90-94", "95-99", "100+"],
                              ["18-64", "65-89", "90+"], ["Age 18-44", "Age 45-89", "Age 90-94", "age >= 95"]))
        cells = [draw.choice(scheme) for _cell in range(draw.randint(60, 200))]
        words, ends = draw.random() < 0.5, draw.random() < 0.5
        table = reading.Table(["age"], [cells], len(cells), "utf-8", False, reading.HEADER_FROM_FILE)
        coded = validation._top_coded_table(table, {"age": 90}, {}, [], (), (), ["age"] if words else None,
                                            {"age": (0, 125)} if ends else None, frozenset({"age"}))
        block: "dict[str, object]" = {"name": "age", "top_coded": 90, "top_coded_bands": True}
        if words:
            block["top_coded_words"] = True
        if ends:
            block["top_coded_ends"] = [0, 125]
        past = {cell for cell in cells if taxonomy.a_band_cell(cell) is not None
                and taxonomy._band_is_past_89(taxonomy.a_band_cell(cell))}  # type: ignore[arg-type]
        chained = chain.described_cells(table, 0, block, taxonomy.Settings(),
                                        {"code": False, "measurement": False, "decimal_comma": False}, "", True)
        if len(past) > 1:
            assert not set(coded.columns[0]) & past and not set(chained) & past, (scheme, words, ends)
            checked += 1
    assert checked > 1000, checked


def test_the_band_marker_is_red_on_the_mutants_that_do_not_read_it(tmp_path: pathlib.Path,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANTS: the validator not finding the marker (its top-code and the forced description it runs again), and the
    chain's reader not reading it: each keeps `90-94` and `95+` again, and the real table misses its own
    description."""
    described, block, table, source = _band_description_without_its_pool(tmp_path)
    with monkeypatch.context() as away:
        away.setattr(validation, "_top_banded_here", lambda description, checked: frozenset())
        read = _each_reader(described, block, table, source)
    assert read["validator"]["90-94"] == 4000 and "90-94" in read["forced"] and read["missed"]  # type: ignore[index,operator]
    real_get = chain._get
    with monkeypatch.context() as away:
        away.setattr(chain, "_get", lambda mapping, key: None if key == "top_coded_bands" else real_get(mapping, key))
        chained = chain.described_cells(table, 0, block, taxonomy.Settings(),
                                        {"code": False, "measurement": False, "decimal_comma": False}, "", True)
    assert _counts(chained).get("95+") == 4000


# -- (3) ITEM 5: THE PATIENT LAYER KEEPS THE BAND MARKER ---------------------------------------------------------------

_PATIENT_BANDS = ("0-17", "18-44", "45-74", "75-99", "100+")
_TEST_KEY = bytes(range(32))


def test_codex_s_patient_fixed_bands_keep_their_marker_behind_the_chain_switch(tmp_path: pathlib.Path) -> None:
    """Codex's item 5: 1,000 people of 20 rows, patient-fixed bands `0-17` to `100+`, 200 people each, the person
    column declared, the subject question open, the chain's switch on: the published block records the band marker
    the rows' block records, loads with the chain, and the cells read through it write `75+` on all 8,000 rows of
    `75-99` and `100+` (on ce75ec54 the marker was lost and 4,000 rows each kept their band)."""
    rows = [[f"P{person:05d}", _PATIENT_BANDS[person // 200], f"{(person * 37 + visit * 11) % 97}.{visit % 10}"]
            for person in range(1000) for visit in range(20)]
    source = tmp_path / "groups.csv"
    source.write_bytes(zoo.csv_bytes(["pid", "age_group", "value"], rows))
    data = tmp_path / "data"
    data.mkdir(mode=0o700)
    if os.name != "nt":
        data.chmod(0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    if os.name != "nt":
        key.chmod(0o600)
    key.write_bytes(_TEST_KEY)
    out = tmp_path / "out"
    out.mkdir()
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{source}", "--out-dir", f"{out}", "--identifier", "pid", "--replace"],
                        chain=cli.ChainRun(rows_per_person="", folder=str(data))) == 0
    document = json.loads((out / "groups-profile.json").read_text(encoding="utf-8"))
    classes = {entry["column"]: entry["class"] for entry in document["relationships"]["grain"]["classes"]}
    assert classes["age_group"] == "patient_fixed"
    block = _block(document, "age_group")
    assert block["top_coded"] == 90 and block["top_coded_bands"] is True, block
    assert contract.load_profile(f"{out / 'groups-profile.json'}", chain=True) is not None
    table = reading.read_table(f"{source}")
    through = chain.described_cells(table, table.column_names.index("age_group"), block, taxonomy.Settings(),
                                    {"code": False, "measurement": False, "decimal_comma": False}, "", True)
    assert _counts(through) == {"0-17": 4000, "18-44": 4000, "45-74": 4000, "75+": 8000}


def _published_marks(marks: "tuple[str, ...]") -> "dict[str, object]":
    """The published block of one patient-fixed column whose rows' block records each of ``marks`` and whose
    patient table's own block records none (`patient_layer._blocks_as_published`)."""
    values = {"top_coded": 90, "top_category_pooled": 11, "top_category_people": ["pid"], "top_coded_words": True,
              "top_coded_ends": [18, 89], "top_coded_year": 1937, "top_coded_bands": True}
    row_block: "dict[str, object]" = {"name": "age_group", "position": 2, "role": "categorical"}
    for mark in marks:
        row_block[mark] = values[mark]
    patient_block: "dict[str, object]" = {"name": "age_group", "position": 1, "role": "categorical"}
    person = {"name": "pid", "position": 1, "role": "identifier"}
    published = patient_layer._blocks_as_published(
        [person, row_block], ["pid", "age_group"], {"pid": "person", "age_group": "patient_fixed"}, "pid",
        {"age_group": patient_block}, 11)
    return published[1]


_EVERY_MARK = ("top_coded", "top_category_pooled", "top_category_people", "top_coded_words", "top_coded_ends",
               "top_coded_year", "top_coded_bands")


def test_every_set_of_the_rows_safe_harbor_marks_stands_on_the_published_block() -> None:
    """The class behind item 5, generated: each of the 128 sets of the seven Safe Harbor marks a rows' block may
    record stands, every mark of it, on the published block of a patient-fixed column whose patient table records
    none."""
    for size in range(1 << len(_EVERY_MARK)):
        marks = tuple(mark for place, mark in enumerate(_EVERY_MARK) if size >> place & 1)
        published = _published_marks(marks)
        assert all(mark in published for mark in marks), (marks, published)


def test_the_band_marker_is_red_on_the_patient_layer_mutant(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the marks of the patient layer before the fix (no `top_coded_bands`): the band marker is lost."""
    assert _published_marks(("top_coded", "top_coded_bands")).get("top_coded_bands") is True
    monkeypatch.setattr(patient_layer, "SAFE_HARBOR_MARKS", tuple(mark for mark in _EVERY_MARK if mark != "top_coded_bands"))
    assert "top_coded_bands" not in _published_marks(("top_coded", "top_coded_bands"))


# -- (4) ITEM 4: A BAND IS AN AGE OF THE REACH ONLY BESIDE NUMBERS -----------------------------------------------------

def _score_bands() -> "list[str]":
    cells = ["40-79"] * 6000 + ["80-109"] * 7000 + ["110-125"] * 7000
    return [cells[(index * 7919) % 20000] for index in range(20000)]


def test_codex_s_score_bands_are_no_ages_at_the_table_floor(tmp_path: pathlib.Path) -> None:
    """Codex's item 4: a `score_band` of `40-79` on 6,000 rows and `80-109` and `110-125` on 7,000 each is no age
    column: no top-code, no `80+`; it is put the question of its two numbers parted by a dash and held until answered,
    as on the public head, and answered `keep` it publishes and writes its three bands as written (on ce75ec54 it was
    top-coded: `40-79` on 6,000 rows and `80+` on 14,000, the answer `keep` never offered)."""
    seen = _commands(tmp_path, "scores", ["score_band"], [[cell] for cell in _score_bands()], {"score_band": "keep"})
    block = _block(seen["description"], "score_band")  # type: ignore[arg-type]
    assert "top_coded" not in block or block["top_coded"] is None, block
    assert {f"{level['label']}": level["count"] for level in block["levels"]} == {  # type: ignore[index,union-attr]
        "40-79": 6000, "80-109": 7000, "110-125": 7000}
    assert _counts(seen["twin"]["score_band"]) == {"40-79": 6000, "80-109": 7000, "110-125": 7000}  # type: ignore[index]
    assert taxonomy.safe_harbor_reach(_score_bands(), False, frozenset(), 11) == ""


def _band_only_column(draw: random.Random) -> "list[str]":
    """A column of bands alone, no number among them: closed bands `A-B` of drawn openings and widths within 0 to
    125 and sometimes a band open upward, each on a drawn number of rows."""
    cells: "list[str]" = []
    first = draw.randint(0, 70)
    while first <= 125 and len(cells) < 400:
        last = min(first + draw.randint(1, 40), 125)
        cells += [f"{first}-{last}"] * draw.randint(11, 60)
        first = last + 1
    if first <= 125 and draw.random() < 0.5:
        cells += [f"{first}+"] * draw.randint(11, 60)
    draw.shuffle(cells)
    return cells


def _ages_beside_bands(draw: random.Random) -> "tuple[list[str], set[str]]":
    """Ages 0 to 89 written as numbers (bare or after `Age`) beside the oldest written as bands past 89, and the
    band spellings past 89."""
    worded = draw.random() < 0.5
    tops = draw.choice((["90-94", "95+"], ["90+"], [">= 90"], ["90-99", "100+"], ["90 to 94", "95 and over"]))
    cells = [(f"Age {age}" if worded else f"{age}") for age in (draw.randint(0, 89) for _cell in range(draw.randint(150, 400)))]
    past = {(f"Age {top}" if worded and top[0].isdigit() else top) for top in tops}
    cells += [draw.choice(sorted(past)) for _cell in range(draw.randint(11, 80))]
    draw.shuffle(cells)
    return cells, past


def test_the_reach_adds_nothing_to_the_band_reader_for_bands_alone_and_reads_bands_beside_numbers() -> None:
    """The class behind item 4, generated: 2,000 columns of bands alone are in the age reach exactly where the band
    reader's own decision reads them as ages (`age_bands_past_89`), and 2,000 columns of ages written as numbers
    beside bands past 89 (the combined case's shape) are all reached, their top-code writing one band past 89 alone,
    open upward from 90 (the source's own `90+` or `>= 90` where it writes that one already)."""
    draw = random.Random(4564)
    decided = 0
    for _column in range(2000):
        cells = _band_only_column(draw)
        alone = taxonomy.age_bands_past_89(cells, frozenset(), False)
        assert (taxonomy.safe_harbor_reach(cells, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES) is alone, sorted(set(cells))
        decided += not alone
    assert decided > 500, decided
    for _column in range(2000):
        cells, past = _ages_beside_bands(draw)
        assert taxonomy.safe_harbor_reach(cells, False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES, sorted(past)
        written = set(taxonomy.top_coded_cells(cells))
        oldest = [taxonomy.a_band_cell(cell) for cell in written if taxonomy.a_band_cell(cell) is not None
                  and taxonomy._band_is_past_89(taxonomy.a_band_cell(cell))]  # type: ignore[arg-type]
        assert len(oldest) == 1 and oldest[0].start == 90 and oldest[0].end < 0, (sorted(past), oldest)  # type: ignore[union-attr]


def test_the_reach_is_red_on_the_mutant_that_reads_every_band_as_a_number(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: every band read as an age of the reach whatever stands beside it (step 9's extension unrestricted, its
    bands taken for numbers): the score's bands are reached again."""
    real = taxonomy._safe_harbor_kind

    def every_band_a_number(cell, comma, mark, words):  # type: ignore[no-untyped-def]
        kind = real(cell, comma, mark, words)
        band = taxonomy.a_band_cell(cell) if kind[0] == taxonomy._AGE_OTHER else None
        if band is not None:
            return (taxonomy._AGE_ABOVE if taxonomy._band_is_past_89(band, mark) else taxonomy._AGE_IN, kind[1], kind[2])
        return kind

    monkeypatch.setattr(taxonomy, "_safe_harbor_kind", every_band_a_number)
    assert taxonomy.safe_harbor_reach(_score_bands(), False, frozenset(), 11) == taxonomy.SAFE_HARBOR_AGES


# -- (5) ITEM 3: A ZONE WORD IS REWRITTEN AT THE POOLING HANDOFF -------------------------------------------------------

_DST_2024 = (datetime.datetime(2024, 3, 10, 7, 0), datetime.datetime(2024, 11, 3, 6, 0))


def _eastern_stamps(rows: int) -> "list[tuple[datetime.datetime, int]]":
    """Evenly spread Eastern wall times of 2024 with the offset in force at each (hours)."""
    found = []
    for index in range(rows):
        utc = datetime.datetime(2024, 1, 1, 5, 0) + datetime.timedelta(seconds=(366 * 86400 * index) // rows)
        offset = -4 if _DST_2024[0] <= utc < _DST_2024[1] else -5
        found += [(utc + datetime.timedelta(hours=offset), offset)]
    return found


def _words_in_force(local: datetime.datetime) -> "set[str]":
    """The words an Eastern wall time of 2024 may wear: both in the hour the clocks repeat, none in the one they skip."""
    found = set()
    for offset, word in ((-5, "EST"), (-4, "EDT")):
        utc = local - datetime.timedelta(hours=offset)
        if (offset == -4) == (_DST_2024[0] <= utc < _DST_2024[1]):
            found.add(word)
    return found


def test_codex_s_zone_word_stamps_pool_by_the_month_at_the_table_floor(tmp_path: pathlib.Path) -> None:
    """Codex's item 3: 20,000 Eastern stamps of 2024 evenly spread, each with the word in force (`EST`, `EDT`), 1,000
    people of 20 rows, the person question open: the column is published at the month under the rule `us -05:00` as
    the same stamps with numeric offsets are, and the twin writes 20,000 stamps of 2024, each with the word in force on
    its own date (on ce75ec54 the column was held and all 20,000 twin stamps were written in 2028)."""
    rows = [[f"P{index % 1000:05d}", local.strftime("%Y-%m-%d %H:%M:%S") + (" EDT" if offset == -4 else " EST")]
            for index, (local, offset) in enumerate(_eastern_stamps(20000))]
    seen = _commands(tmp_path, "visits", ["patient_ref", "seen_at"], rows)
    block = _block(seen["description"], "seen_at")  # type: ignore[arg-type]
    assert block["role"] == "datetime" and block["offset_rule"] == "us -05:00", block.get("detection_evidence")
    assert block["time_grain"]["rung"] == "month"  # type: ignore[index]
    twin = seen["twin"]["seen_at"]  # type: ignore[index]
    assert _counts([cell[:4] for cell in twin]) == {"2024": 20000}
    assert [cell for cell in twin if cell[20:] not in _words_in_force(datetime.datetime.strptime(cell[:19], "%Y-%m-%d %H:%M:%S"))] == []


def _zone_member(family: str) -> str:
    return "layout {YYYY}-{MM}-{DD} {HH}:{MI}:{SS} {" + family + "}"


def _family_words(family: str) -> "dict[str, str]":
    """Each offset a zone family names and its word, read off the closed list in its order (its words and its
    offsets), apart from the product's own accessor."""
    words = [word for word in parsing.zone_words() if parsing.zone_family_of(word) == family]
    offsets = parsing.zone_family_offsets(family)
    assert len(words) == len(offsets)
    return dict(zip(offsets, words))


def test_every_zone_word_is_rewritten_as_its_family_writes_the_new_offset() -> None:
    """The class behind item 3, generated: every zone family of the closed list, 300 drawn stamps each at each of its
    words, rewritten to each of its offsets: the family's word for the new offset, read back at it with the same wall
    time, as the same stamp written with a numeric offset is rewritten; an offset the family names no word for gives
    none."""
    draw = random.Random(4565)
    families = sorted({parsing.zone_family_of(word) for word in parsing.zone_words()})
    assert len(families) == 9
    for family in families:
        member = _zone_member(family)
        assert parsing.layout_offset_field(member) == family
        reading_of = grains.Reading(grains.STAMP, member)
        words = _family_words(family)
        for _stamp in range(300):
            wall = datetime.datetime(2024, 1, 1) + datetime.timedelta(seconds=draw.randrange(366 * 86400))
            text = wall.strftime("%Y-%m-%d %H:%M:%S")
            for old in words:
                cell = f"{text} {words[old]}"
                assert parsing.parse_datetime(cell, member) == (text, old)
                for new in tuple(words) + ("+09:00",):
                    moved = grains.with_offset(cell, reading_of, _seconds(new))
                    numeric = grains.with_offset(f"{text}{old}", grains.Reading(grains.STAMP, "iso-datetime"), _seconds(new))
                    if new == old:
                        assert moved == cell
                    elif new not in words:
                        assert moved is None, (cell, new)
                    else:
                        assert moved == f"{text} {words[new]}", (cell, new, moved)
                        assert parsing.parse_datetime(moved, member) == (text, new)
                        assert numeric == f"{text}{new}"


def _seconds(offset: str) -> int:
    sign = -1 if offset[0] == "-" else 1
    return sign * (int(offset[1:3]) * 3600 + int(offset[4:6]) * 60)


def test_the_zone_word_is_red_on_the_mutant_that_names_no_word(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the family names no word for any offset (the handoff before the fix, which read numbers alone): an
    `EST` stamp moved to `-04:00` gives none again."""
    reading_of = grains.Reading(grains.STAMP, _zone_member("EST/EDT"))
    assert grains.with_offset("2024-07-15 08:00:00 EST", reading_of, -4 * 3600) == "2024-07-15 08:00:00 EDT"
    monkeypatch.setattr(parsing, "zone_family_word", lambda field, offset: "")
    assert grains.with_offset("2024-07-15 08:00:00 EST", reading_of, -4 * 3600) is None


# -- (6) ITEM 2: A LABEL'S BOUND MOVES INWARD AT EVERY SIZE ------------------------------------------------------------

def _limit_table(side: str) -> "list[list[str]]":
    """Codex's witness: Random(21); `TND` below 0.35, the limit below 0.5, else a load past it to six places."""
    draw = random.Random(21)
    rows = []
    for index in range(20000):
        roll = draw.random()
        if roll < 0.35:
            load = "TND"
        elif roll < 0.5:
            load = "<1000.00000025" if side == "low" else ">999.99999975"
        else:
            step = (1 + int(draw.lognormvariate(8, 2))) / 1000000
            load = f"{1000 + step:.6f}" if side == "low" else f"{1000 - step:.6f}"
        rows += [[f"S{100000 + index}", load]]
    return rows


def _past(cells: "list[str]", side: str) -> int:
    found = 0
    for cell in cells:
        try:
            value = float(cell)
        except ValueError:
            continue
        found += value < 1000.00000025 if side == "low" else value > 999.99999975
    return found


@pytest.mark.parametrize("side", ["low", "high"])
def test_codex_s_detection_limit_writes_no_number_past_it_at_the_table_floor(side: str, tmp_path: pathlib.Path) -> None:
    """Codex's item 2, both directions: `<1000.00000025` beside loads of 1000.000001 and more (and its mirror,
    `>999.99999975` beside loads of 999.999999 and less): the bound read is the grid point inside the limit, and the
    twin writes no number past it (on ce75ec54 both bounds were read as 1000.0 and the twin wrote `1000.000000` on 11
    cells past each limit, every check of the column met)."""
    seen = _commands(tmp_path, "loads", ["sample_id", "load"], _limit_table(side))
    described = contract.load_profile(f"{seen['described']}")
    facts = [column for column in described.columns if column.name == "load"][0].facts
    assert facts.numbers.label_bounds == ((1000.000001, None) if side == "low" else (None, 999.999999))  # type: ignore[union-attr]
    assert _past(seen["twin"]["load"], side) == 0  # type: ignore[index]


def _drawn_bound(draw: random.Random) -> "tuple[float, int, int, int]":
    """A bound written in figures as a label writes it, off its grid: a drawn number of whole steps of ``places``
    places (up to a thousand billion of them) and a fraction of a step written in one or two more places; with the
    whole steps below and above it."""
    places = draw.randint(0, 6)
    steps = draw.randint(0, 10 ** draw.randint(1, 12))
    extra = draw.randint(1, 2)
    fraction = draw.randint(1, 10 ** extra - 1)
    text = f"{steps}{fraction:0{extra}d}".rjust(places + extra + 1, "0")
    whole = text[: len(text) - places - extra] or "0"
    written = f"{whole}.{text[len(text) - places - extra:]}"
    return float(written), places, steps, steps + 1


def test_a_generated_bound_lands_inside_on_its_grid_at_every_size() -> None:
    """The class behind item 2, generated: 20,000 bounds off their grid, of up to a thousand billion steps of zero to
    six places and one or two places finer: a low bound lands on the step above it, a high bound on the step below,
    each a point of the grid on the bound's own side (the tolerance of a billionth of the bound's size read a whole
    step as noise past a billion steps); and 5,000 bounds on their grid stay there, a strict one a step inside."""
    draw = random.Random(4566)
    for _bound in range(20000):
        value, places, below, above = _drawn_bound(draw)
        scale = 10.0 ** places
        figures = places if places else -2
        assert contract._on_the_label_grid(value, True, False, figures) == above / scale, (value, places)
        assert contract._on_the_label_grid(value, False, False, figures) == below / scale, (value, places)
    for _bound in range(5000):
        places = draw.randint(0, 6)
        steps = draw.randint(1, 10 ** draw.randint(1, 12))
        scale = 10.0 ** places
        value = float(f"{steps / scale:.{places}f}")
        figures = places if places else -2
        assert contract._on_the_label_grid(value, True, False, figures) == steps / scale, (value, places)
        assert contract._on_the_label_grid(value, True, True, figures) == (steps + 1) / scale, (value, places)
        assert contract._on_the_label_grid(value, False, True, figures) == (steps - 1) / scale, (value, places)


def test_the_bound_is_red_on_the_mutant_of_the_old_tolerance(monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the tolerance of a billionth of the scaled bound's size: Codex's bounds land on 1000.0 again, both
    directions, outside their limits."""
    assert contract._on_the_label_grid(1000.00000025, True, False, 6) == 1000.000001
    assert contract._on_the_label_grid(999.99999975, False, False, 6) == 999.999999
    monkeypatch.setattr(contract, "_grid_noise", lambda scaled: 1e-9 * max(1.0, abs(scaled)))
    assert contract._on_the_label_grid(1000.00000025, True, False, 6) == 1000.0
    assert contract._on_the_label_grid(999.99999975, False, False, 6) == 1000.0


# -- (7) ITEM 7: THE EXCLUSION STEP READS A COLUMN'S RUNS ONCE ---------------------------------------------------------

def _interior_serials(rows: int, layouts: int) -> "list[str]":
    """A column whose every layout's exclusion writes a figure inside its run, so each asks the real runs: `#` and
    seven figures from 2,000,000 on a quarter of the rows beside `#`, one to ``layouts`` - 1 letters `M`, `R` and
    seven figures."""
    return [f"#{2_000_000 + i}" if i % 4 == 0 else "#" + "M" * (1 + i % (layouts - 1)) + "R" + f"{(1 + i % 9) * 1_000_000 + i // 9}"
            for i in range(rows)]


def _exclusions_counted(folder: pathlib.Path, cells: "list[str]", monkeypatch: pytest.MonkeyPatch) -> "tuple[dict[str, object], dict[str, int]]":
    """The column described by the command, declared a record number, and how often the step asked the real runs
    and read them."""
    asked = {"questions": 0, "reads": 0, "scans": 0}
    real_scan = taxonomy._a_real_run_written

    def scan(present, figures, given):  # type: ignore[no-untyped-def]
        asked["scans"] += 1
        return real_scan(present, figures, given)

    monkeypatch.setattr(taxonomy, "_a_real_run_written", scan)
    # ...the index, where the tree has one (the merged head ce75ec54 scanned every row for each question instead).
    if hasattr(taxonomy, "_a_real_run_indexed"):
        real_indexed, real_read = taxonomy._a_real_run_indexed, taxonomy._real_runs_read

        def indexed(index, figures, given):  # type: ignore[no-untyped-def]
            asked["questions"] += 1
            return real_indexed(index, figures, given)

        def read(index):  # type: ignore[no-untyped-def]
            asked["reads"] += 1
            return real_read(index)

        monkeypatch.setattr(taxonomy, "_a_real_run_indexed", indexed)
        monkeypatch.setattr(taxonomy, "_real_runs_read", read)
    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "serials.csv"
    source.write_bytes(zoo.csv_bytes(["serial"], [[cell] for cell in cells]))
    with _nobody_at_the_keyboard(), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        assert cli.main(["profile", f"{source}", "--replace", "--identifier", "serial"], small_tables_refused=True) == 0
    block = _block(json.loads((folder / "serials-profile.json").read_text(encoding="utf-8")), "serial")
    return block["layout_exclusions"], asked  # type: ignore[return-value]


def test_the_exclusion_step_reads_the_real_runs_once_for_fifty_layouts(tmp_path: pathlib.Path,
                                                                     monkeypatch: pytest.MonkeyPatch) -> None:
    """Codex's item 7 at the table floor: 20,000 rows of fifty layouts, each asking the real runs (49 questions): the
    present cells are read once for the column, never once a layout (on ce75ec54 the 49 questions read all 20,000 rows
    each, 980,000 row visits), and the exclusions are the ones the scan of every row gives."""
    cells = _interior_serials(20000, 50)
    exclusions, asked = _exclusions_counted(tmp_path / "index", cells, monkeypatch)
    assert asked == {"questions": 49, "reads": 1, "scans": 0}, asked
    monkeypatch.undo()
    real_scan = taxonomy._a_real_run_written
    monkeypatch.setattr(taxonomy, "_a_real_run_indexed", lambda index, figures, given: real_scan(index.present, figures, given))
    with_scan, _asked = _exclusions_counted(tmp_path / "scan", cells, monkeypatch)
    assert exclusions == with_scan and len(exclusions) == 51


def _drawn_cells(draw: random.Random, count: int) -> "list[str]":
    cells = []
    for _cell in range(count):
        parts = []
        for _part in range(draw.randint(1, 3)):
            parts += [draw.choice(("#", "MR", "A-", " ", "/")), "0" * draw.choice((0, 0, 1, 2)),
                      f"{draw.randint(1, 9)}{draw.randrange(10 ** draw.randint(3, 8)):0d}"]
        cells += ["".join(parts)]
    return cells


def test_the_real_runs_index_answers_every_generated_question_as_the_scan_does() -> None:
    """The class behind item 7, generated: 300 columns of drawn cells holding runs of figures of five to ten merged
    figures, noughts before some, and 40 drawn questions each (a width and figures written at drawn places of the
    run): the index answers each as the scan of every present cell does."""
    draw = random.Random(4567)
    answered = {True: 0, False: 0}
    for _column in range(300):
        present = _drawn_cells(draw, draw.randint(20, 300))
        widths = {width: True for width in range(5, 11)}
        index = taxonomy._real_runs(present, widths)
        runs = sorted({run.lstrip("0") for cell in present for run in _runs_of(cell) if len(run.lstrip("0")) >= 5})
        for _question in range(40):
            if runs and draw.random() < 0.5:
                run = draw.choice(runs)
                figures = len(run)
                spots = sorted(draw.sample(range(figures), draw.randint(1, min(3, figures))))
                written = [(spot, run[spot] if draw.random() < 0.8 else f"{draw.randint(0, 9)}") for spot in spots]
            else:
                figures = draw.randint(5, 10)
                spots = sorted(draw.sample(range(figures), draw.randint(1, 3)))
                written = [(spot, f"{draw.randint(0, 9)}") for spot in spots]
            expected = taxonomy._a_real_run_written(present, figures, written)
            assert taxonomy._a_real_run_indexed(index, figures, written) is expected, (present[:3], figures, written)
            answered[expected] += 1
    assert answered[True] > 1000 and answered[False] > 1000, answered


def _runs_of(cell: str) -> "list[str]":
    found, run = [], ""
    for character in cell + " ":
        if "0" <= character <= "9":
            run += character
        elif run:
            found, run = found + [run], ""
    return found


def test_the_runs_are_read_once_a_layout_on_the_mutant(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: the step hands each layout the present cells again (the index made anew for each question, as the scan
    read every row for each): the 49 questions read the present cells 49 times."""
    real_held = taxonomy._an_opening_held
    monkeypatch.setattr(taxonomy, "_an_opening_held", lambda found, runs, held, present, index=None: real_held(
        found, runs, held, present))
    _exclusions, asked = _exclusions_counted(tmp_path, _interior_serials(20000, 50), monkeypatch)
    assert asked["reads"] == 49, asked
