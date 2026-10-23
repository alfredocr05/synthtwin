"""P4-D428 (lane CODES-3): identifiers with numeric roots, float record numbers, prefixed ids, plain keys.

WHAT WAS MEASURED (the health data zoo's plan, wave6/ZOO/PLAN.md rows 19, 42 and
43; push critic 13's MAJOR 5 for the plain keys; measured on af69aaef):

(a) A DICOM UID column (`1.2.840.113619.2.55.3.` and three more arcs) was
    read as free text, asked nothing, and its twin wrote filler (600 of 600
    cells outside the UID grammar); declared, its root was lost and 496 of
    600 cells broke the grammar (a nought leading an arc).
(b) Cerner record numbers exported as decimals (`31000000.00`), declared,
    published `all_whole_numbers true` beside the layout `%%%%%%%%.%%`, and
    the twin drew the places after the point: 595 of 600 cells no whole
    number, validate at exit 3.
(c) VCF rsIDs (`rs` and four to nine figures), declared: the nine cells of
    the withheld layout pool were written `rs----1`, `A------`, one without
    the prefix, validate at exit 3.
(d) A plain column of keys below five figures -- `R1000` to `R1039`,
    `AB100` to `AB139`, padded `0100` to `0139`, one key a cell -- is held
    while every cell is a key, and ONE ordinary word published all 40 keys
    as labels (40 of 40 and 599 twin cells at 600 rows, 19,999 at 20,000).

THE RULE (plan P4-D428). (a) Q-ID, one more shape of HX's question about
figures (plan P4-D401; ZR.2 of P4-D419), puts `keep`, `code` and
`identifier` to a free-text column every cell of which is a UID with two
points or more, every value different, and holds it until answered;
declared, the arcs every cell shares are published as its prefix (owner
ruling 1) and the twin writes no arc led by a nought. (b) A declared record
number publishing `all_whole_numbers true` writes `0` at every place after
the point. (c) Rule A1 (P4-D422's ZS.2): a declared record number
publishing a `(column)` prefix counts its pooled cells in its commonest
layout, producer and validator alike. (d) Route two of the person rule sets
aside up to one present cell in three written as ordinary words beside
lettered keys, and route four asks padded keys of one width beside them.

Each case runs the product's own command line, nobody at the keyboard, and
each is red on the mutant its docstring names (wave6/CODES-3/mutants.log).
"""

from __future__ import annotations

import contextlib
import csv
import datetime
import io
import json
import pathlib
import random
import re

import pytest

from synthtwin import asking, cli, parsing

import unanswered_identifier_shapes as shapes

UID = re.compile(r"[012](\.(0|[1-9]\d*))+")
ROOT = "1.2.840.113619.2.55.3."
SIZES = (600, 20_000)


def _pick(draw: random.Random, pool: "tuple[tuple[str, float], ...]") -> str:
    total = sum(weight for _value, weight in pool)
    point = draw.random() * total
    for value, weight in pool:
        point -= weight
        if point <= 0:
            return value
    return pool[-1][0]


def uid_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A PACS export's study UID beside a modality: the zoo's `imaging.study_uid` shape."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            f"{ROOT}{draw.randint(100000000, 999999999)}.{draw.randint(100, 999)}"
            f".{1600000000 + index}",
            _pick(draw, (("CT", 4.0), ("MR", 3.0), ("CR", 3.0))),
        ]]
    return ["study_uid", "modality"], rows


def cerner_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A Cerner Millennium CCL export (zoo plan row 42): record numbers written as decimals.

    The zoo critic's own shape (wave6/ZOO/PLAN-v2-work/probe_shapes.py,
    `cerner`), draw for draw, so K-HZ-04's baseline is the plan's.
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for index in range(n):
        moment = datetime.datetime(2023, 1, 1) + datetime.timedelta(minutes=draw.randint(0, 900000))
        rows += [[
            f"{31000000 + index}.00",
            f"{15000000 + draw.randint(0, 149)}.00",
            moment.strftime("%d-%b-%Y %H:%M:%S").upper(),
            _pick(draw, (("309308", 40.0), ("309309", 30.0), ("309310", 20.0),
                         ("2555137051", 9.0), ("19962820", 1.0))),
            _pick(draw, (("Positive", 20.0), ("Negative", 70.0), ("Indeterminate", 8.0),
                         ("See Comment", 2.0))),
        ]]
    return ["ENCNTR_ID", "PERSON_ID", "REG_DT_TM", "ENCNTR_TYPE_CD", "RESULT_VAL"], rows


_CHROMOSOMES = tuple(
    (f"chr{name}", weight)
    for name, weight in [(f"{place}", 30.0 - place) for place in range(1, 23)]
    + [("X", 6.0), ("Y", 1.0), ("M", 0.5)]
)


def vcf_rows(n: int, seed: int) -> "tuple[list[str], list[list[str]]]":
    """A flattened VCF (zoo plan row 43): rsIDs of `rs` and four to nine figures.

    The zoo critic's own shape (probe_shapes.py, `vcf`), draw for draw.
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for _index in range(n):
        reference = draw.choice("ACGT")
        other = draw.choice([base for base in "ACGT" if base != reference] + [reference + draw.choice("ACGT")])
        rows += [[
            _pick(draw, _CHROMOSOMES),
            f"{draw.randint(10_000, 240_000_000)}",
            f"rs{draw.randint(1000, 999_999_999)}",
            reference,
            other,
            f"{draw.uniform(20, 3000):.2f}",
            _pick(draw, (("0/1", 45.0), ("1/1", 20.0), ("0/0", 15.0), ("0|1", 10.0),
                         ("1|0", 8.0), ("./.", 2.0))),
        ]]
    return ["CHROM", "POS", "ID", "REF", "ALT", "QUAL", "GT"], rows


PLAIN_KEYS = {
    "R": [f"R{1000 + place}" for place in range(40)],
    "AB": [f"AB{100 + place}" for place in range(40)],
    "PAD": [f"{100 + place:04d}" for place in range(40)],
}
# One ordinary word: on no cell, on one cell, and on one cell in three.
WORD_SHARES = (("pure", 0), ("one", -1), ("third", 3))


def plain_rows(form: str, share: int, n: int) -> "tuple[list[str], list[list[str]]]":
    """One key a cell of `PLAIN_KEYS[form]`, beside a test name and a value; `OTHER` as `share` says."""
    draw = random.Random(20261023)
    keys = PLAIN_KEYS[form]
    words = 0 if share == 0 else 1 if share < 0 else n // share
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            "OTHER" if index < words else keys[index % len(keys)],
            draw.choice(("Sodium", "Potassium", "Glucose")),
            f"{draw.uniform(3, 150):.1f}",
        ]]
    return ["key", "test", "value"], rows


def _write(folder: pathlib.Path, header: "list[str]", rows: "list[list[str]]") -> pathlib.Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "t.csv"
    with open(path, "w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(header)
        writer.writerows(rows)
    return path


def run(
    folder: pathlib.Path,
    header: "list[str]",
    rows: "list[list[str]]",
    column: str,
    declared: "tuple[str, ...]" = (),
) -> "dict[str, object]":
    """Profile (nobody at the keyboard), generate at seed 0 and validate; what one column came to."""
    path = _write(folder, header, rows)
    typed: "list[str]" = []
    for name in declared:
        typed += ["--identifier", name]
    screen = io.StringIO()
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(screen), contextlib.redirect_stderr(screen):
            profiled = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace"] + typed)
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            generated = cli.main(["generate", f"{folder / 't-profile.json'}", "--out-dir",
                                  f"{folder}", "--seed", "0", "--replace"])
            validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin",
                                  f"{folder / 't-twin.csv'}", "--out-dir", f"{folder}", "--replace"])
    texts = [(folder / name).read_text(encoding="utf-8")
             for name in ("t-profile.json", "t-profile.txt", "t-questions.json")]
    texts += [screen.getvalue()]
    document = json.loads(texts[0])
    block = [one for one in document["columns"] if one["name"] == column][0]
    questions = json.loads(texts[2])
    asked = [[choice["answer"] for choice in entry["answers_you_can_give"]]
             for entry in questions["asked"] if entry["column"] == column]
    with open(folder / "t-twin.csv", encoding="utf-8", newline="") as handle:
        table = list(csv.reader(handle))
    place = table[0].index(column)
    return {
        "exits": (profiled, generated, validated),
        "block": block,
        "held": column in document["settings"]["forced_identifiers"],
        "asked": asked,
        "texts": texts,
        "cells": [row[place] for row in table[1:]],
        "real": [row[header.index(column)] for row in rows],
    }


# -- (a) DICOM UIDs ------------------------------------------------------


@pytest.mark.parametrize("n", SIZES)
def test_a_declared_uid_keeps_its_root_and_its_grammar(tmp_path: pathlib.Path, n: int) -> None:
    """(a): declared, every twin cell a UID opening with the real root, validate at exit 0.

    Mutants: `parsing.is_a_literal_prefix` without the UID arm (the root is
    lost: no prefix published, every cell off the root); `parsing.uid_unled`
    answering True (arcs led by a nought, the grammar broken).
    """
    header, rows = uid_rows(n, 19)
    seen = run(tmp_path / "uid", header, rows, "study_uid", declared=("study_uid",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert seen["block"]["layout_prefixes"] == {"(column)": ROOT}
    cells = seen["cells"]
    assert len(cells) == n
    assert sum(1 for cell in cells if UID.fullmatch(cell) is None) == 0
    assert sum(1 for cell in cells if not cell.startswith(ROOT)) == 0
    # No real UID is written, whole, in the twin.
    assert not set(cells) & set(seen["real"])


def test_q_id_is_hx_s_question_put_once_and_holds_until_answered(tmp_path: pathlib.Path) -> None:
    """(a) and HX's case: unanswered, Q-ID is the one question, and the column is held.

    One entry for the column in the questions file, offering `keep`,
    `code` and `identifier`, the column described as record numbers (its
    name among the forced identifiers), no root and no UID in any file.
    Mutants: Q-ID's trigger removed from `questions_and_splits_for` (no
    question, nothing held); `BECAUSE_FIGURES_JOINED_BY_POINTS` taken out of
    `HOLDING_REASONS` (asked, not held).
    """
    header, rows = uid_rows(600, 23)
    seen = run(tmp_path / "open", header, rows, "study_uid")
    assert seen["exits"][0] == 0 and seen["exits"][1] == 0
    assert seen["asked"] == [[asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER]]
    assert seen["held"] is True
    assert seen["block"]["role"] == "identifier"
    assert seen["block"]["layout_prefixes"] == {}
    for text in seen["texts"]:
        assert ROOT not in text
        assert "113619" not in text
    counted = shapes.count_real(seen["real"], seen["texts"], seen["cells"])
    assert counted["description_values"] == 0 and counted["twin_cells"] == 0


def test_q_id_reaches_no_column_but_uids_every_one_different() -> None:
    """Q-ID's trigger, and the columns it must not reach (ZR.2's goldens, figures and marks).

    Mutant: the trigger reading a cell of figures and points without the
    grammar (`parsing.is_a_uid` answering True for any text): `1.25`-style
    numbers and `120/80` pressures would be asked.
    """
    uids = [f"1.2.840.{place}.{place + 7}" for place in range(1, 200)]
    assert asking._uids_every_one_different(uids)
    assert not asking._uids_every_one_different(uids + [uids[0]])
    assert not asking._uids_every_one_different([f"{place}.{place % 7}5" for place in range(200)])
    assert not asking._uids_every_one_different([f"{100 + place}/{60 + place % 30}" for place in range(200)])
    assert not asking._uids_every_one_different([f"1.02.{place}" for place in range(200)])
    assert not asking._uids_every_one_different([f"3.2.{place}" for place in range(200)])
    assert not asking._uids_every_one_different([f"1.{place}" for place in range(200)])
    assert parsing.is_a_uid_root("1.2.840.113619.") and not parsing.is_a_uid_root("1.2.840")
    assert not parsing.is_a_literal_prefix("12.") and not parsing.is_a_literal_prefix("P00")
    assert parsing.uid_root(uids) == "1.2.840."
    assert parsing.uid_root(uids + ["REC1"]) == ""


# -- (b) float record numbers --------------------------------------------


@pytest.mark.parametrize("n", SIZES)
def test_b_a_whole_record_number_writes_its_noughts(tmp_path: pathlib.Path, n: int) -> None:
    """(b): declared, every twin cell `\\d+\\.00`, `all_whole_numbers` met, validate at exit 0.

    Mutant: `generation._whole_places` returning the layout unchanged (the
    places after the point drawn: 595 of 600 cells bad, exit 3).
    """
    header, rows = cerner_rows(n, 42)
    for column in ("ENCNTR_ID", "PERSON_ID"):
        seen = run(tmp_path / column, header, rows, column, declared=("ENCNTR_ID", "PERSON_ID"))
        assert seen["exits"] == (0, 0, 0), seen["exits"]
        assert seen["block"]["all_whole_numbers"] is True
        assert seen["block"]["layout_forms"] == {"%%%%%%%%.%%": n}
        assert sum(1 for cell in seen["cells"] if re.fullmatch(r"\d+\.00", cell) is None) == 0


# -- (c) prefixed ids of several lengths ---------------------------------


@pytest.mark.parametrize("n", SIZES)
def test_c_a_prefixed_id_s_rare_layouts_are_counted_in_its_commonest(tmp_path: pathlib.Path, n: int) -> None:
    """(c): declared, no `(withheld)` pool, every twin cell `rs` and figures, validate at exit 0.

    Mutants: `taxonomy.absorbs_its_layout_pool` answering False (the pool
    kept and written `rs----1`, one cell without its prefix: exit 3 at 600
    rows); the validator's absorption removed (the real file misses its
    own census).
    """
    header, rows = vcf_rows(n, 43)
    seen = run(tmp_path / "vcf", header, rows, "ID", declared=("ID",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    block = seen["block"]
    assert block["layout_prefixes"] == {"(column)": "rs"}
    assert "(withheld)" not in block["layout_forms"]
    assert sum(block["layout_forms"].values()) == n
    assert sum(1 for cell in seen["cells"] if re.fullmatch(r"rs\d+", cell) is None) == 0
    # ...and the real file meets the census, the prefix and the lengths it
    # was described with. (Its repetition pattern, `{"1": n}`, is missed on
    # af69aaef as here: not this lane's, and not read below.)
    real = tmp_path / "vcf" / "t.csv"
    (tmp_path / "real").mkdir()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        cli.main(["validate", f"{tmp_path / 'vcf' / 't-profile.json'}", "--twin", f"{real}",
                  "--out-dir", f"{tmp_path / 'real'}", "--replace"])
    report = (tmp_path / "real" / "t-quality.txt").read_text(encoding="utf-8")
    missed = [line for line in report.splitlines() if line.rstrip().endswith("MISSED")]
    for line in missed:
        assert "layout" not in line and "prefix" not in line and "length" not in line, line


# -- (d) plain keys below five figures, beside one ordinary word ---------


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("form", sorted(PLAIN_KEYS))
@pytest.mark.parametrize("share", [label for label, _share in WORD_SHARES])
def test_d_plain_keys_beside_a_word_are_held_with_the_question_put(
    tmp_path: pathlib.Path, n: int, form: str, share: str
) -> None:
    """(d): 0 keys in any file and in the twin, the column held, HX's question put once.

    Mutants: `asking._keys_beside_words` answering False (`R` and `AB`
    beside words publish 40 of 40); `asking._padded_beside_words` answering
    False (`PAD` beside words publishes 40 of 40 at 20,000 rows).
    """
    header, rows = plain_rows(form, dict(WORD_SHARES)[share], n)
    seen = run(tmp_path / f"{form}-{share}".lower(), header, rows, "key")
    assert seen["exits"][0] == 0 and seen["exits"][1] == 0
    assert seen["held"] is True
    assert len(seen["asked"]) == 1 and asking.ANSWER_IDENTIFIER in seen["asked"][0]
    counted = shapes.count_real(PLAIN_KEYS[form], seen["texts"][:3], seen["cells"])
    assert counted["description_values"] == 0, counted
    assert counted["twin_cells"] == 0, counted


def test_d_codes_and_scales_beside_words_are_not_asked() -> None:
    """(d)'s false alarms, by shape: short codes beside words reach neither new arm.

    ICD-10 `E11` and `E11.9`, a scale `A1` to `A9`, LOINC `2345-7`, a stage
    `pT1c`, two- and three-figure padded codes and years, each beside
    `Unknown` on a fifth of the cells. Mutant: `_a_lettered_key` taking one
    figure or more (the scale and `E11` beside words are asked).
    """
    draw = random.Random(5)
    shapes_of = {
        "icd": [draw.choice(["E11", "I10", "J45", "N18", "K21"]) for _row in range(600)],
        "icd_dotted": [draw.choice(["E11.9", "I10.0", "J45.9"]) for _row in range(600)],
        "scale": [f"A{draw.randint(1, 9)}" for _row in range(600)],
        "loinc": [draw.choice(["2345-7", "718-7", "2160-0"]) for _row in range(600)],
        "stage": [draw.choice(["pT1c", "pT2", "pT3", "pT1a"]) for _row in range(600)],
        "padded2": [f"{draw.randint(1, 12):02d}" for _row in range(600)],
        "padded3": [f"{draw.randint(1, 99):03d}" for _row in range(600)],
        "years": [f"{draw.randint(2015, 2024)}" for _row in range(600)],
    }
    for name, cells in shapes_of.items():
        beside = ["Unknown"] * 120 + cells[120:]
        assert not asking._keys_beside_words(beside), name
        assert not asking._a_key_of_figures_repeating(beside), name


# -- K-HZ-04: the zoo's identifier cells out of pattern ------------------


def _zoo_reader(path: pathlib.Path) -> "dict[str, object]":
    import pandas

    return {"inferred": pandas.read_csv(path), "text": pandas.read_csv(path, dtype=str),
            "raw": pandas.read_csv(path, dtype=str, keep_default_na=False)}


def zoo_identifier_cells_out_of_pattern(folder: pathlib.Path, n: int) -> "dict[str, int]":
    """K-HZ-04 (plan P4-D428): twin cells out of pattern, each table answered with the zoo's general facts.

    The zoo's own `imaging` export (its `study_uid` against the UID grammar
    and the real root), and the zoo plan's Cerner export (rows 42: its
    `ENCNTR_ID` and `PERSON_ID` against `\\d+\\.00`) and flattened VCF
    (row 43: its `ID` against `rs\\d+`), each run through
    `health_zoo.run_table` -- profiled, answered as the person holding the
    table would (`identifier` where the question offers it), generated
    and validated. A cell is out of pattern where it is present and fails
    its column's pattern; a table whose twin was not written counts every
    real cell. Also returned: how many of the three twins validate at exit
    other than 0. On af69aaef: 600, 595, 595, 9 and two.
    """
    import health_zoo

    tables = (
        (next(table for table in health_zoo.TABLES if table.name == "imaging"), 20261016,
         {"study_uid": lambda cell: UID.fullmatch(cell) is not None and cell.startswith(ROOT)}),
        (health_zoo.Table(
            "cerner_ccl", ".csv", cerner_rows, health_zoo.csv_bytes,
            {"cerner_ccl": tuple(cerner_rows(1, 0)[0])},
            {"ENCNTR_ID": "identifier", "PERSON_ID": "identifier"}, _zoo_reader, ()), 4252,
         {"ENCNTR_ID": lambda cell: re.fullmatch(r"\d+\.00", cell) is not None,
          "PERSON_ID": lambda cell: re.fullmatch(r"\d+\.00", cell) is not None}),
        (health_zoo.Table(
            "vcf_flat", ".csv", vcf_rows, health_zoo.csv_bytes,
            {"vcf_flat": tuple(vcf_rows(1, 0)[0])}, {"ID": "identifier"}, _zoo_reader, ()), 4250,
         {"ID": lambda cell: re.fullmatch(r"rs\d+", cell) is not None}),
    )
    found: "dict[str, int]" = {}
    failing = 0
    for table, seed, patterns in tables:
        place = folder / table.name
        result = health_zoo.run_table(table, place, n, seed)
        if result["steps"].get("validate", {}).get("exit") != 0:
            failing += 1
        twin = place / f"{table.name}-twin.csv"
        source = place / f"{table.name}.csv"
        with open(twin if twin.is_file() else source, encoding="utf-8", newline="") as handle:
            rows = list(csv.reader(handle))
        for column, fits in patterns.items():
            at = rows[0].index(column)
            cells = [row[at] for row in rows[1:] if row[at]]
            found[column] = (
                sum(1 for cell in cells if not fits(cell)) if twin.is_file() else len(cells)
            )
    found["total"] = sum(found.values())
    found["twins_failing_validation"] = failing
    return found
