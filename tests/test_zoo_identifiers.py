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

THE RULE (plan P4-D428, with its repair round 1). (a) Q-ID, one more shape
of HX's question about figures (plan P4-D401; ZR.2 of P4-D419), puts
`keep`, `code` and `identifier` to a column every cell of which, words
aside, is a UID with two points or more -- every value different, or
repeating with an arc after its organisation's root -- and holds it until
answered; declared, its organisation's root is published as its prefix
(owner ruling 1; cut before the first arc of five figures or more, the
orchestrator's ruling of 2026-10-23, and three arcs after the organisation
arc at the latest, repair round 2), the twin writes no arc led by a
nought and the validator checks the grammar. (b) A declared record number
publishing `all_whole_numbers true` writes `0` at every place after the
point, and such a layout is named only where its figures before the point
leave room; unanswered, the same noughts on every cell are read as the
bare figures. (c) Rule A1 (P4-D422's ZS.2): a declared record number of one
opening and figures counts every cell of a layout its published census
does not name, or whose room the opening would take, in its commonest
layout, producer and validator alike; and a whole one written as a decimal
with no prefix the same way. (d) Route two of the person rule sets aside
every cell holding no figure, and every placeholder for nobody, beside
lettered keys filling the floor's cells, and route four asks padded keys
of one width beside them.

Each case runs the product's own command line, nobody at the keyboard, and
each is red on the mutant its docstring names (wave6/CODES-3/mutants.log,
and repair1/mutants-r1.log).
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

import fixtures
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


def plain_rows(
    form: str, share: int, n: int, word: str = "OTHER"
) -> "tuple[list[str], list[list[str]]]":
    """One key a cell of `PLAIN_KEYS[form]`, beside a test name and a value; ``word`` as `share` says."""
    draw = random.Random(20261023)
    keys = PLAIN_KEYS[form]
    words = 0 if share == 0 else 1 if share < 0 else n // share
    rows: "list[list[str]]" = []
    for index in range(n):
        rows += [[
            word if index < words else keys[index % len(keys)],
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
    validate: bool = True,
) -> "dict[str, object]":
    """Profile (nobody at the keyboard), generate at seed 0 and validate; what one column came to.

    ``validate`` False leaves the twin unchecked (its exit reads -1): the
    cases that ask only what is published and what the twin writes.
    """
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
            validated = -1
            if validate:
                validated = cli.main(["validate", f"{folder / 't-profile.json'}", "--twin",
                                      f"{folder / 't-twin.csv'}", "--out-dir", f"{folder}",
                                      "--replace"])
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


def test_q_id_reaches_no_column_but_a_column_of_uids() -> None:
    """Q-ID's trigger, and the columns it must not reach (ZR.2's goldens, figures and marks).

    Different UIDs are asked; repeating ones where every value holds an
    arc after its organisation's root (a study, series or instance
    number); words aside whatever their share where the floor's UIDs
    remain (skeptic 1, items 4 and 9; the verify of repair 1, items 4
    and 5); never a column under the DICOM standard's root. Mutants: the
    trigger reading a cell of figures and points without the grammar
    (`parsing.is_a_uid` answering True for any text: `1.25`-style numbers
    and `120/80` pressures asked); `_an_arc_naming_an_item` answering True
    (version numbers `2.1.0` repeating asked); it asking an arc of five
    figures (the short-arc study UIDs repeating not asked) or of seven
    (the verify's V7: five- and six-figure arcs not asked); the standard's
    root asked (SOP Class and Transfer Syntax UIDs held); words capped at
    a third (`UNKNOWN` on 100 of 299 cells not asked).
    """
    uids = [f"1.2.840.{place}.{place + 7}" for place in range(1, 200)]
    assert asking._a_column_of_uids(uids)
    assert not asking._a_column_of_uids(uids + [uids[0]])
    assert not asking._a_column_of_uids([f"{place}.{place % 7}5" for place in range(200)])
    assert not asking._a_column_of_uids([f"{100 + place}/{60 + place % 30}" for place in range(200)])
    assert not asking._a_column_of_uids([f"1.02.{place}" for place in range(200)])
    assert not asking._a_column_of_uids([f"3.2.{place}" for place in range(200)])
    assert not asking._a_column_of_uids([f"1.{place}" for place in range(200)])
    assert not asking._a_column_of_uids(["2.1.0", "2.0.1", "3.0.2"] * 100)
    series = [f"{ROOT}604688119.868.1599999999.{place // 20 + 1}" for place in range(600)]
    assert asking._a_column_of_uids(series)
    assert asking._a_column_of_uids(["UNKNOWN"] + uids)
    assert asking._a_column_of_uids(["Not known."] * 66 + uids)
    assert asking._a_column_of_uids(["UNKNOWN"] * 100 + uids)
    assert not asking._a_column_of_uids(["UNKNOWN"] * 100 + uids[:10])
    for arc in (41000, 410000):
        assert asking._a_column_of_uids([f"{ROOT}{arc + k // 10}.{k // 10 % 50 + 1}" for k in range(600)])
    assert asking._a_column_of_uids([f"{ROOT}4021.1015.{1000 + k // 10}" for k in range(600)])
    for standard in (
        ["1.2.840.10008.5.1.4.1.1.2", "1.2.840.10008.5.1.4.1.1.4", "1.2.840.10008.5.1.4.1.1.6.1"],
        ["1.2.840.10008.1.2", "1.2.840.10008.1.2.1", "1.2.840.10008.1.2.4.70"],
        ["2.16.840.1.113883.6.96", "2.16.840.1.113883.6.1", "2.16.840.1.113883.6.90"],
    ):
        assert not asking._a_column_of_uids(standard * 200), standard
    assert parsing.is_a_uid_root("1.2.840.113619.") and not parsing.is_a_uid_root("1.2.840")
    assert not parsing.is_a_literal_prefix("12.") and not parsing.is_a_literal_prefix("P00")
    assert parsing.uid_root(uids) == "1.2.840."
    assert parsing.uid_root(uids + ["REC1"]) == ""


# THE ROOT ENDS BEFORE THE FIRST ARC THAT COULD NAME A STUDY, A SERIES, A
# DEVICE OR A MOMENT (skeptic 1, item 1; the orchestrator's ruling of
# 2026-10-23 16:56): cut at the last point before the first arc of five
# figures or more, the organisation arc after `1.2.840.` aside.
SERIES = f"{ROOT}604688119.868.1599999999.123"
STUDY = f"{ROOT}604688119.868.1599999999"
SIEMENS = "1.3.12.2.1107.5.2.32.35162."
# A study UID whose own arcs hold four figures or fewer: a site arc, then
# month-day and hour-minute (the verify of repair 1, finding 1).
SHORT_STUDY = f"{ROOT}4021.1015.1230"
# The verify of repair 2, findings 1 and 3: a study UID under a root of
# short arcs with no organisation arc (`1.2.276.0.12.34.56`), one under a
# vendor's single product arc (`1.2.840.113619.2.4021.1015.1230`), and one
# under Siemens' product arcs (`1.3.12.2.1107.5.2.32.4021.1015.1230`).
SHORT_NO_ORGANISATION = "1.2.276.0.12.34.56"
ONE_PRODUCT_ARC = "1.2.840.113619.2.4021.1015.1230"
SIEMENS_SHORT = "1.3.12.2.1107.5.2.32.4021.1015.1230"
SHORT_ROOTS = {
    "ge": (SHORT_STUDY, ROOT),
    "noorg": (SHORT_NO_ORGANISATION, "1.2.276.0.12."),
    "one_product_arc": (ONE_PRODUCT_ARC, "1.2.840.113619.2."),
    "siemens": (SIEMENS_SHORT, "1.3.12.2.1107.5.2.32."),
}


def test_the_root_is_the_organisation_s_and_names_no_study_series_or_device() -> None:
    """The ruling's cut on its four named roots. Mutants: `_root_of_the_organisation`
    returning the shared arcs whole (the series and study UIDs published);
    no cap on the arcs after the organisation arc (the short-arc study UID
    published); five-figure arcs kept (a serial of five figures published)."""
    assert parsing.uid_root([f"{SERIES}.{place}" for place in range(1, 50)]) == ROOT
    assert parsing.uid_root([f"{STUDY}.{place % 20 + 1}.{place}" for place in range(1, 50)]) == ROOT
    assert parsing.uid_root([f"{SIEMENS}{place}.1" for place in range(1, 50)]) == "1.3.12.2.1107.5.2.32."
    assert parsing.uid_root([f"1.2.276.0.7230010.3.1.4.{place}" for place in range(1, 50)]) == "1.2.276.0."
    assert parsing.uid_root([f"1.2.840.10008.5.1.4.1.1.{place}" for place in range(1, 50)]) == "1.2.840.10008.5.1.4."
    # ...and at most three arcs after the organisation arc (the verify of
    # repair 1, finding 1): a site arc, month-day and hour-minute of four
    # figures or fewer are cut, every root above unmoved.
    assert parsing.uid_root([f"{SHORT_STUDY}.{place}" for place in range(1, 50)]) == ROOT
    assert parsing.uid_root([f"{ROOT}402.101.123.{place}" for place in range(1, 50)]) == ROOT
    assert parsing.uid_root([f"1.2.826.0.1.3680043.8.498.{place}" for place in range(1, 50)]) == "1.2.826.0.1."
    # ...after the organisation arc, only arcs of three figures at most,
    # and at most five arcs where no organisation arc is found (the
    # verify of repair 2, findings 1 and 3; LANE CODES-3 ADDENDUM 3).
    # Mutants: no cap without an organisation arc (the study UID under
    # `1.2.276.0.12.34.56` published); arcs of four figures kept after the
    # organisation arc (`1.2.840.113619.2.4021.1015.` published);
    # `_ORGANISATION_ARC_FIGURES_AT_LEAST` 5 (Siemens' 1107 read as no
    # organisation arc: `1.3.12.2.1107.` instead of its product root).
    for study, root in SHORT_ROOTS.values():
        assert parsing.uid_root([f"{study}.{place}" for place in range(1, 50)]) == root, study
    assert parsing.uid_root([f"2.16.840.1.113883.3.464.1003.{place}" for place in range(1, 50)]) == "2.16.840.1.113883.3.464."
    assert parsing.uid_root([f"1.2.40.0.13.1.5.{place}" for place in range(1, 50)]) == "1.2.40.0.13."
    # A serial of five figures where no organisation arc came first is
    # cut too (mutant: `_ROOT_ARC_FIGURES_AT_MOST` 5, the serial published).
    assert parsing.uid_root([f"1.2.276.0.72300.3.{place}" for place in range(1, 50)]) == "1.2.276.0."


def _uid_table(cells: "list[str]") -> "tuple[list[str], list[list[str]]]":
    draw = random.Random(len(cells))
    return ["uid", "modality"], [[cell, draw.choice(("CT", "MR", "CR"))] for cell in cells]


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("shape", ["sop", "study"])
def test_a_declared_root_is_the_organisation_s_and_the_twin_writes_no_real_uid(
    tmp_path: pathlib.Path, n: int, shape: str
) -> None:
    """Skeptic 1, item 1: SOP UIDs of one series, instances of one study, declared.

    The published root is GE's, never the series or study UID; no real
    UID in any file or the twin; every cell under the root and the grammar.
    Mutant "all shared arcs" (`_root_of_the_organisation` returning its
    root whole): the series UID published, 278 real SOP UIDs in the twin.
    """
    cells = [f"{SERIES}.{k + 1}" if shape == "sop" else f"{STUDY}.{k % 20 + 1}.{k // 20 + 1}"
             for k in range(n)]
    header, rows = _uid_table(cells)
    seen = run(tmp_path / shape, header, rows, "uid", declared=("uid",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert seen["block"]["layout_prefixes"] == {"(column)": ROOT}
    for text in seen["texts"]:
        assert STUDY not in text
    assert not set(seen["cells"]) & set(cells)
    assert sum(1 for cell in seen["cells"] if UID.fullmatch(cell) is None) == 0
    assert sum(1 for cell in seen["cells"] if not cell.startswith(ROOT)) == 0


def test_a_siemens_root_is_cut_before_the_scanner_serial(tmp_path: pathlib.Path) -> None:
    """The ruling's Siemens case at 600 rows: `35162` is a scanner serial, never published."""
    draw = random.Random(35162)
    cells = [f"{SIEMENS}{draw.randint(10**8, 10**9 - 1)}.{draw.randint(1, 999)}.{1600000000 + k}"
             for k in range(600)]
    header, rows = _uid_table(cells)
    seen = run(tmp_path / "siemens", header, rows, "uid", declared=("uid",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert seen["block"]["layout_prefixes"] == {"(column)": "1.3.12.2.1107.5.2.32."}
    for text in seen["texts"]:
        assert "35162" not in text


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("shape", sorted(SHORT_ROOTS))
def test_a_short_arc_study_uid_is_never_published_as_the_root(
    tmp_path: pathlib.Path, n: int, shape: str
) -> None:
    """The verifies of repairs 1 and 2 (HIPAA): instances of one study whose arcs are short.

    Declared, `<study>.<k>`: the root published is the organisation's,
    never the study UID, and no real instance UID is in any file or the
    twin. `ge` (`...2.55.3.4021.1015.1230`; before repair 2: the study UID
    published, 332 of 600 and 2,222 of 20,000 real UIDs in the twin);
    `noorg` (`1.2.276.0.12.34.56`, no organisation arc; on 1cf6f3c3: the
    study UID published, 332 of 600 and 2,222 of 20,000 real), red on the
    mutant "no cap without an organisation arc"; `one_product_arc`
    (`1.2.840.113619.2.4021.1015.1230`; on 1cf6f3c3 `...2.4021.1015.`
    published, a site arc and a month-day), red on the mutant "arcs of
    four figures kept after the organisation arc"; `siemens`
    (`1.3.12.2.1107.5.2.32.4021.1015.1230`), red on the mutant
    `_ORGANISATION_ARC_FIGURES_AT_LEAST` 5 (332 of 600 real under it on
    1cf6f3c3).
    """
    study, root = SHORT_ROOTS[shape]
    cells = [f"{study}.{k + 1}" for k in range(n)]
    header, rows = _uid_table(cells)
    seen = run(tmp_path / "short", header, rows, "uid", declared=("uid",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert seen["block"]["layout_prefixes"] == {"(column)": root}
    for text in seen["texts"]:
        assert study + "." not in text
    # Under `1.2.276.0.12.` the twin's two-figure arcs spell `34.56` once
    # in 8,100 draws, and the instance numbers then fill their room:
    # chance alone, nothing real read, 1 cell of 20,000 at seed 0 (stated
    # limit (4)); 0 for every other shape and at 600 rows.
    real = set(cells)
    equal = sum(1 for cell in seen["cells"] if cell in real)
    assert equal <= n // 4000, equal
    assert sum(1 for cell in seen["cells"] if UID.fullmatch(cell) is None) == 0
    assert sum(1 for cell in seen["cells"] if not cell.startswith(root)) == 0


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("shape", ["sop_class", "transfer_syntax"])
def test_the_dicom_standard_s_own_uids_are_not_asked(tmp_path: pathlib.Path, n: int, shape: str) -> None:
    """The verify of repair 1, finding 5 (i): SOP Class and Transfer Syntax UIDs repeating.

    They name a kind of object or an encoding, the same in every hospital:
    no question and no hold, read as af69aaef read them. Mutant: Q-ID put
    to a column under the standard's root `1.2.840.10008.` (both held).
    """
    values = (["1.2.840.10008.5.1.4.1.1.2", "1.2.840.10008.5.1.4.1.1.4", "1.2.840.10008.5.1.4.1.1.1",
               "1.2.840.10008.5.1.4.1.1.6.1"] if shape == "sop_class"
              else ["1.2.840.10008.1.2", "1.2.840.10008.1.2.1", "1.2.840.10008.1.2.4.70",
                    "1.2.840.10008.1.2.4.90"])
    draw = random.Random(8)
    header, rows = _uid_table([draw.choice(values) for _row in range(n)])
    seen = run(tmp_path / shape, header, rows, "uid", validate=False)
    assert seen["asked"] == []
    assert seen["held"] is False


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("shape", ["short_tail", "sop_series"])
def test_a_declared_uid_of_several_tail_lengths_keeps_its_root(
    tmp_path: pathlib.Path, n: int, shape: str
) -> None:
    """Skeptic 1, items 5 and 10: instance numbers 1..N under one root, declared.

    The layouts whose room the root would take below the line are counted
    in the commonest one that keeps it (rule A1 widened), so every twin
    cell carries the root and passes the grammar, validate at exit 0.
    Mutant: A1 kept to a published `(column)` prefix (the root lost on the
    layouts the room rule refuses: 99 cells off the root at 600 rows).
    """
    cells = [f"{ROOT}{k + 1}" if shape == "short_tail" else f"{SERIES}.{k + 1}" for k in range(n)]
    header, rows = _uid_table(cells)
    seen = run(tmp_path / shape, header, rows, "uid", declared=("uid",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert seen["block"]["layout_prefixes"] == {"(column)": ROOT}
    assert sum(seen["block"]["layout_forms"].values()) == n
    assert sum(1 for cell in seen["cells"] if UID.fullmatch(cell) is None) == 0
    assert sum(1 for cell in seen["cells"] if not cell.startswith(ROOT)) == 0


REPEATING = {
    20: lambda k: f"{STUDY}.{k // 20 + 1}",
    40: lambda k: f"{ROOT}{604688119 + (k // 40) * 7919}.868.{1600000000 + k // 40}",
    # The verify of repair 1, finding 6 (V7) and finding 1: the longest arc
    # after the organisation's five or six figures, or four.
    5: lambda k: f"{ROOT}{41000 + k // 10}.{k // 10 % 50 + 1}",
    6: lambda k: f"{ROOT}{410000 + k // 10}.{k // 10 % 50 + 1}",
    4: lambda k: f"{SHORT_STUDY}.{k // 10 + 1}",
}


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("every", sorted(REPEATING))
def test_repeating_uids_are_put_q_id_and_held(tmp_path: pathlib.Path, n: int, every: int) -> None:
    """Skeptic 1, item 4: a series UID on the rows of its images, read as labels, is held.

    Q-ID put once, the column held, 0 real UIDs in any file or the twin.
    Mutants: Q-ID's trigger asking every value different (the labels print
    30 series UIDs at 600 rows and the twin writes them on every row); it
    asking an arc of seven figures (the five- and six-figure shapes
    published) or of five (the short-arc shape published).
    """
    cells = [REPEATING[every](k) for k in range(n)]
    header, rows = _uid_table(cells)
    seen = run(tmp_path / f"rep{every}", header, rows, "uid", validate=False)
    assert seen["asked"] == [[asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER]]
    assert seen["held"] is True
    assert _found_linear(sorted(set(cells)), seen["texts"], seen["cells"]) == (0, 0)


def test_uids_beside_one_word_are_put_q_id_and_held(tmp_path: pathlib.Path) -> None:
    """Skeptic 1, item 9: UIDs beside one `UNKNOWN` (a number with words) are put Q-ID.

    Mutant: `_uid_cells` setting no word aside (no question; the twin
    leads arcs with noughts under the number-with-words reading).
    """
    draw = random.Random(9)
    cells = ["UNKNOWN"] + [f"{ROOT}{draw.randint(10**8, 10**9 - 1)}.{1600000000 + k}" for k in range(599)]
    header, rows = _uid_table(cells)
    seen = run(tmp_path / "word", header, rows, "uid", validate=False)
    assert seen["asked"] == [[asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER]]
    assert seen["held"] is True
    counted = shapes.count_real(cells[1:], seen["texts"], seen["cells"])
    assert counted["description_values"] == 0 and counted["twin_cells"] == 0, counted


# -- (b) float record numbers --------------------------------------------


@pytest.mark.parametrize("n", SIZES)
def test_b_a_whole_record_number_writes_its_noughts(tmp_path: pathlib.Path, n: int) -> None:
    """(b): declared, every twin cell `\\d+\\.00`, `all_whole_numbers` met, validate at exit 0.

    Mutant: `parsing.whole_places_layout` returning the layout unchanged
    (the places after the point drawn: 595 of 600 cells bad, exit 3).
    """
    header, rows = cerner_rows(n, 42)
    for column in ("ENCNTR_ID", "PERSON_ID"):
        seen = run(tmp_path / column, header, rows, column, declared=("ENCNTR_ID", "PERSON_ID"))
        assert seen["exits"] == (0, 0, 0), seen["exits"]
        assert seen["block"]["all_whole_numbers"] is True
        assert seen["block"]["layout_forms"] == {"%%%%%%%%.%%": n}
        assert sum(1 for cell in seen["cells"] if re.fullmatch(r"\d+\.00", cell) is None) == 0


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("places", [".00", ".0"])
def test_b_whole_record_numbers_written_as_decimals_are_held_unanswered(
    tmp_path: pathlib.Path, n: int, places: str
) -> None:
    """Skeptic 1, item 3: `31000000.00` (and `.0`), nobody at the keyboard, is held.

    Read as its bare figures, the fixed-width question is put once and the
    column held, as the same numbers written without the point are: 0 real
    values in any file, and in the twin none beyond chance. Mutant: `_without_nought_places`
    answering [] (read as a count, its mean and percentiles published, 598
    of 600 real encounter numbers in the twin).
    """
    cells = [f"{31000000 + k}{places}" for k in range(n)]
    draw = random.Random(3)
    rows = [[cell, draw.choice(("Sodium", "Glucose"))] for cell in cells]
    seen = run(tmp_path / "enc", ["ENCNTR_ID", "test"], rows, "ENCNTR_ID", validate=False)
    assert len(seen["asked"]) == 1 and asking.ANSWER_IDENTIFIER in seen["asked"][0]
    assert seen["held"] is True
    found, equal = _found_linear(cells, seen["texts"], seen["cells"], decimals=True)
    # Made-up eight-figure numbers equal a real one only by chance: about
    # n x n / 9 x 10^7 cells, 4 at 20,000 rows (stated limit (4)).
    assert found == 0 and equal <= n // 1000, (found, equal)


def _found_linear(
    real: "list[str]", texts: "list[str]", cells: "list[str]", decimals: bool = False
) -> "tuple[int, int]":
    """Real values found in the texts, and twin cells equal to one, in time linear in the cells.

    A value counts as found where its text stands in a text; a record
    number written as a decimal (``decimals``) also where its figures
    before the point stand as a run of figures with none against them,
    and a twin cell counts where its figures before the point are a real
    value's (`shapes.count_real`'s readings: its pairwise search over
    20,000 twin cells and 20,000 values runs for hours).
    """
    joined = "\n".join(texts)
    runs: "set[str]" = set()
    if decimals:
        runs = set(re.findall(r"(?<![0-9.])[0-9]+(?![0-9])", joined))
    found = sum(
        1 for value in real
        if value in joined or (decimals and value.split(".")[0] in runs)
    )
    keys = {value.split(".")[0] if decimals else value for value in real}
    equal = sum(1 for cell in cells if (cell.split(".")[0] if decimals else cell) in keys)
    return found, equal


@pytest.mark.parametrize("n", SIZES)
def test_b_record_numbers_of_three_widths_write_their_noughts(tmp_path: pathlib.Path, n: int) -> None:
    """The verify of repair 1, finding 2: `1500+k`, `150000+k` and `15000000+k`, each `.00`, declared.

    At 20,000 rows the four-figure layout's room (9,000) is refused beside
    20,000 values, and its cells were written in the pool writer's
    spelling (`001112.`: 2,864 cells off `\\d+\\.00`). Rule A1 without a
    prefix counts them in the commonest whole-places layout of the same
    places, producer and validator alike: every twin cell `\\d+\\.00`,
    validate at exit 0, and the source validated against its own
    description misses no layout or length. Mutant: the whole-places arm
    of A1 removed (`taxonomy._with_whole_places_absorbed` returning the
    column).
    """
    draw = random.Random(7)
    cells = [f"{draw.choice([1500, 150000, 15000000]) + k}.00" for k in range(n)]
    rows = [[cell, draw.choice(("CT", "MR"))] for cell in cells]
    seen = run(tmp_path / "widths", ["ID", "other"], rows, "ID", declared=("ID",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert sum(seen["block"]["layout_forms"].values()) == n
    assert sum(1 for cell in seen["cells"] if re.fullmatch(r"\d+\.00", cell) is None) == 0
    document = json.loads(seen["texts"][0])
    missed = _validated(tmp_path / "source", document, cells)
    assert "layout" not in missed and "length" not in missed, missed


def test_b_grouped_and_partly_decimal_record_numbers(tmp_path: pathlib.Path) -> None:
    """Skeptic 1, items 8 and 12 (X4), at 600 rows.

    `31,000,000.00` declared writes its noughts after the point (the
    group mark allowed before it; mutant: `parsing._GROUP_MARKS` empty, 595
    cells bad). Record numbers whose places are not all noughts publish
    `all_whole_numbers false`, and the twin draws them (mutant X4: the
    noughts written without `all_whole_numbers`, every cell `.00`).
    """
    grouped = [f"{31000000 + k:,}.00" for k in range(600)]
    rows = [[cell, "x"] for cell in grouped]
    seen = run(tmp_path / "grouped", ["ID", "other"], rows, "ID", declared=("ID",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    assert sum(1 for cell in seen["cells"] if re.fullmatch(r"\d{1,3}(,\d{3})*\.00", cell) is None) == 0
    draw = random.Random(4)
    decimals = [f"{draw.randint(10**7, 10**8 - 1)}.{draw.randint(10, 99)}" for _row in range(600)]
    seen = run(tmp_path / "decimals", ["ID", "other"], [[cell, "x"] for cell in decimals], "ID",
               declared=("ID",))
    assert seen["block"]["all_whole_numbers"] is False
    assert sum(1 for cell in seen["cells"] if cell.endswith(".00")) < 60


def test_b_a_whole_places_layout_spells_only_its_figures_before_the_point(
    tmp_path: pathlib.Path,
) -> None:
    """Codex's item 1 (b): `00.00` to `99.00` declared is no hundred-cell layout.

    Writing noughts after the point leaves `%%.%%` a hundred cells, so the
    layout is not named (`taxonomy.layout_census` counts the room before
    the point) and the twin writes fewer than all hundred real values.
    Mutant: the census's whole-places room removed (`%%.%%` named, the
    twin writing all 100 real values).
    """
    assert parsing.whole_places_layout("%%,%%%,%%%.%%") == "%%,%%%,%%%.00"
    assert parsing.whole_places_layout("@%%.%%") == "@%%.%%"
    assert parsing.whole_places_room("%%.%%") == 100
    cells = [f"{k % 100:02d}.00" for k in range(600)]
    seen = run(tmp_path / "hundred", ["ID", "other"], [[cell, "x"] for cell in cells], "ID",
               declared=("ID",))
    assert "%%.%%" not in seen["block"]["layout_forms"]
    assert len(set(seen["cells"]) & set(cells)) < 100


# -- (c) prefixed ids of several lengths ---------------------------------


@pytest.mark.parametrize("n", SIZES)
def test_c_a_prefixed_id_s_rare_layouts_are_counted_in_its_commonest(tmp_path: pathlib.Path, n: int) -> None:
    """(c): declared, no `(withheld)` pool, every twin cell `rs` and figures, validate at exit 0.

    Mutants: rule A1 off in the producer (the pool kept and written
    `rs----1`, one cell without its prefix: exit 3 at 600 rows); the
    validator's absorption removed (the real file misses its own census).
    """
    header, rows = vcf_rows(n, 43)
    seen = run(tmp_path / "vcf", header, rows, "ID", declared=("ID",))
    assert seen["exits"] == (0, 0, 0), seen["exits"]
    block = seen["block"]
    assert block["layout_prefixes"] == {"(column)": "rs"}
    assert "(withheld)" not in block["layout_forms"]
    assert sum(block["layout_forms"].values()) == n
    assert sum(1 for cell in seen["cells"] if re.fullmatch(r"rs\d+", cell) is None) == 0
    # ...and at 600 rows the real file meets the census, the prefix and the
    # lengths it was described with. (Its repetition pattern, `{"1": n}`,
    # is missed on af69aaef as here: not this lane's, and not read below.
    # At 20,000 rows the real file misses: the strict xfail below.)
    if n == 600:
        _the_real_file_meets_its_forms(tmp_path)


def _the_real_file_meets_its_forms(tmp_path: pathlib.Path) -> None:
    """The source of `tmp_path / 'vcf'` validated against its own description: no form MISSED."""
    real = tmp_path / "vcf" / "t.csv"
    (tmp_path / "real").mkdir()
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        checked = cli.main(["validate", f"{tmp_path / 'vcf' / 't-profile.json'}", "--twin",
                            f"{real}", "--out-dir", f"{tmp_path / 'real'}", "--replace"])
    assert checked in (0, 3), checked
    report = (tmp_path / "real" / "t-quality.txt").read_text(encoding="utf-8")
    missed = [line for line in report.splitlines() if line.rstrip().endswith("MISSED")]
    for line in missed:
        assert "layout" not in line and "prefix" not in line and "length" not in line, line


@pytest.mark.xfail(
    strict=True,
    reason="plan P4-D428's stated limit (10), owner lane CODES-1 part C: at 20,000 rows "
    "C6-131b takes back the 20 six-figure rsIDs so that the one of five figures is not "
    "named, rule A1 keeps that decision, and the REAL file, not the twin, misses its own "
    "census and length.min",
)
def test_c_the_real_vcf_meets_its_own_forms_at_20000(tmp_path: pathlib.Path) -> None:
    """The owner's floor size, the real file against its description (the verify of repair 1, finding 7).

    Kept as a strict xfail pinned to stated limit (10): it turns red the
    day the real file meets its forms, so the limit is closed in the plan
    then.
    """
    header, rows = vcf_rows(20_000, 43)
    seen = run(tmp_path / "vcf", header, rows, "ID", declared=("ID",), validate=False)
    assert seen["exits"][:2] == (0, 0), seen["exits"]
    _the_real_file_meets_its_forms(tmp_path)


def _rs_mix(n: int, unique: bool) -> "list[str]":
    """rsIDs of four to nine figures, the rare widths clearing the floor at 20,000 rows (skeptic 1, item 7)."""
    draw = random.Random(11)
    used: "set[int]" = set()
    cells: "list[str]" = []
    for _row in range(n):
        width = draw.choice([4] * 3 + [5] * 3 + [6] * 4 + [8] * 400 + [9] * 590)
        value = draw.randint(10 ** (width - 1), 10 ** width - 1)
        while unique and value in used:
            value = draw.randint(10 ** (width - 1), 10 ** width - 1)
        used.add(value)
        cells += [f"rs{value}"]
    return cells


def test_c_rare_widths_that_clear_the_floor_keep_the_prefix_at_20000(
    tmp_path: pathlib.Path,
) -> None:
    """Skeptic 1, item 7: rsIDs of four figures (room 10^4 beside 20,000 values) keep `rs`.

    The layout whose room the prefix would take below the line is counted
    in the commonest one (rule A1 widened). Every twin cell `rs` and
    figures. Mutant: A1 kept to a published `(column)` prefix (60 cells
    without `rs`). (Three values repeated make the declared column the
    table's person column, `cli._population_of`, whose census is counted
    in people: plan P4-D428 names that line and its owner.)
    """
    cells = _rs_mix(20_000, True)
    seen = run(tmp_path / "rs", ["ID", "other"], [[cell, "x"] for cell in cells], "ID",
               declared=("ID",))
    assert seen["block"]["layout_prefixes"] == {"(column)": "rs"}
    assert sum(seen["block"]["layout_forms"].values()) == 20_000
    assert sum(1 for cell in seen["cells"] if re.fullmatch(r"rs\d+", cell) is None) == 0


def test_c_the_pool_goes_into_the_commonest_layout_and_no_other(tmp_path: pathlib.Path) -> None:
    """Skeptic 1, item 12 (X5): the 8-figure layout's count is its own cells', exactly.

    Mutant: A1 counting the pool in the RAREST named layout.
    """
    header, rows = vcf_rows(600, 43)
    seen = run(tmp_path / "vcf", header, rows, "ID", declared=("ID",), validate=False)
    forms = seen["block"]["layout_forms"]
    eight = sum(1 for row in rows if re.fullmatch(r"rs\d{8}", row[2]))
    nine = sum(1 for row in rows if re.fullmatch(r"rs\d{9}", row[2]))
    assert forms["&&%%%%%%%%"] == eight
    assert forms["&&%%%%%%%%%"] == 600 - eight > nine


def _validated(folder: pathlib.Path, document: "dict[str, object]", cells: "list[str]") -> str:
    """A description validated against a file of ``cells``: the quality report's MISSED lines."""
    folder.mkdir(parents=True, exist_ok=True)
    fixtures.write_profile(folder, "d-profile.json", document)
    _write(folder, ["ID", "other"], [[cell, "x"] for cell in cells])
    with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
        checked = cli.main(["validate", f"{folder / 'd-profile.json'}", "--twin", f"{folder / 't.csv'}",
                            "--out-dir", f"{folder}", "--replace"])
    assert checked in (0, 3), checked
    report = (folder / "t-quality.txt").read_text(encoding="utf-8")
    return "\n".join(line for line in report.splitlines() if line.rstrip().endswith("MISSED"))


def test_c_an_older_description_is_read_as_it_was_written(tmp_path: pathlib.Path) -> None:
    """Codex's item 5 and skeptic 1's X9: a census that left cells to subtraction is no A1.

    `P10000` to `P10789` beside `P0` to `P9`, its short layout too small a
    supply to name: the description publishes `@%%%%%: 790`, the prefix
    and the true shortest length 2. Validated against its own source,
    nothing is MISSED. Mutant: the validator absorbing wherever no pool
    is written (length.min 6 against 2, the census 800 against 790).
    """
    cells = [f"P{10000 + k}" for k in range(790)] + [f"P{k}" for k in range(10)]
    seen = run(tmp_path / "made", ["ID", "other"], [[cell, "x"] for cell in cells], "ID",
               declared=("ID",), validate=False)
    document = json.loads(seen["texts"][0])
    block = [one for one in document["columns"] if one["name"] == "ID"][0]
    block["layout_forms"] = {"@%%%%%": 790}
    block["layout_prefixes"] = {"(column)": "P"}
    block["min_length"] = 2
    block["max_length"] = 6
    assert _validated(tmp_path / "older", document, cells) == ""


def test_c_a1_leaves_a_layout_the_person_floor_took_back(tmp_path: pathlib.Path) -> None:
    """Codex's item 3: a layout nine people wear stays unnamed after A1.

    100 people, six rows each, the person column declared beside a
    distinct record number: 70 people `P` and five figures, 20 six
    figures, nine seven figures, the last five five-figure ids and one of
    eight. The seven-figure layout, worn by nine people, is never
    published. Mutant: A1 recounting the rows (`@%%%%%%%: 54` republished).
    """
    rows: "list[list[str]]" = []
    serial = 0
    for person in range(100):
        for visit in range(6):
            serial += 1
            width = 5 if person < 70 else 6 if person < 90 else 7 if person < 99 else (8 if visit == 5 else 5)
            rows += [[f"S{person:03d}", f"P{10 ** (width - 1) + serial}", "x"]]
    folder = tmp_path / "people"
    path = _write(folder, ["person", "ID", "other"], rows)
    with shapes.nobody_at_the_keyboard():
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            profiled = cli.main(["profile", f"{path}", "--out-dir", f"{folder}", "--replace",
                                 "--identifier", "person", "--identifier", "ID"])
    assert profiled == 0
    document = json.loads((folder / "t-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "ID"][0]
    assert "@%%%%%%%" not in block["layout_forms"]


@pytest.mark.parametrize("shape", ["case", "marks"])
def test_c_a1_moves_no_cell_whose_obligations_would_conflict(tmp_path: pathlib.Path, shape: str) -> None:
    """Codex's item 4: A1 moves only the prefix and figures, so every obligation stays true.

    590 `REC-A10000`.. beside ten `REC-a10000`.. (folded identities), and
    580 `P` and five figures beside ten `P.1000`.. and ten `P:1000`..
    (alphabet counts): no cell is moved and the description is today's,
    its pool kept (the pool writer's fillers are CODES-1 part C's stated
    limit). Mutant: `_a1_tail_fits` answering True (600 upper-case cells
    beside 590 folded identities, a layout deviation all checks report
    HELD).
    """
    if shape == "case":
        cells = [f"REC-A{10000 + k}" for k in range(590)] + [f"REC-a{10000 + k}" for k in range(10)]
    else:
        cells = ([f"P{10000 + k}" for k in range(580)] + [f"P.{1000 + k}" for k in range(10)]
                 + [f"P:{1000 + k}" for k in range(10)])
    seen = run(tmp_path / shape, ["ID", "other"], [[cell, "x"] for cell in cells], "ID",
               declared=("ID",), validate=False)
    assert seen["exits"][:2] == (0, 0), seen["exits"]
    forms = seen["block"]["layout_forms"]
    assert sum(forms.values()) < 600 or "(withheld)" in forms, forms


def test_c_a_uid_root_stands_only_over_a_column_of_uids(tmp_path: pathlib.Path) -> None:
    """Codex's items 1 (a) and 2: no numeric prefix but over a whole column of UIDs, and room counted unled.

    200 `1.2.10000`.. beside eleven `1.2.` publish no prefix (the cells of
    one layout are no column of UIDs); `1.2.100` to `1.2.999`, 900
    different, leave `1.2.%%%` 900 tails, not a thousand, so no root is
    published and the twin writes fewer than all 900 real values.
    Mutants: the per-layout prefix reading a UID root; `parsing.uid_room`
    counting a thousand.
    """
    cells = [f"1.2.{10000 + k % 200}" for k in range(589)] + ["1.2."] * 11
    seen = run(tmp_path / "mixed", ["ID", "other"], [[cell, "x"] for cell in cells], "ID",
               declared=("ID",), validate=False)
    assert seen["block"]["layout_prefixes"] == {}
    cells = [f"1.2.{100 + k % 900}" for k in range(1800)]
    seen = run(tmp_path / "nine", ["ID", "other"], [[cell, "x"] for cell in cells], "ID",
               declared=("ID",), validate=False)
    assert seen["block"]["layout_prefixes"] == {}
    assert len(set(seen["cells"]) & set(cells)) < 900
    assert parsing.uid_room("%%%") == 900 and parsing.uid_room("%.%%") == 900


def test_c_the_validator_reads_the_uid_grammar(tmp_path: pathlib.Path) -> None:
    """Codex's item 6: cells whose arc is led by a nought miss the published root's grammar.

    800 UIDs `1.2.840.{1000+i}.{2000+i}` described; checked against cells
    whose first variable arc is `i` in four figures, every one led by a
    nought: `uid.grammar` MISSED, though layout, prefix and lengths hold.
    The source itself misses nothing of the grammar. Mutant:
    `validation._uid_grammar_checks` returning [].
    """
    cells = [f"1.2.840.{1000 + k}.{2000 + k}" for k in range(800)]
    seen = run(tmp_path / "made", ["ID", "other"], [[cell, "x"] for cell in cells], "ID",
               declared=("ID",), validate=False)
    document = json.loads(seen["texts"][0])
    assert "uid.grammar" not in _validated(tmp_path / "real", document, cells)
    led = [f"1.2.840.{k:04d}.{2000 + k}" for k in range(800)]
    assert "uid.grammar" in _validated(tmp_path / "led", document, led)


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


# THE EIGHT WORDS SKEPTIC 1 MEASURED (item 2): placeholders and words with
# spaces or marks beside the keys, each publishing every key on the
# head it reviewed. (form, word, share)
MEASURED_WORDS = (
    ("R", "Not known.", -1),
    ("R", "-1", -1),
    ("R", "0", -1),
    ("R", "Other (specify)", -1),
    ("AB", "-1", 5),
    ("PAD", "NOT KNOWN", -1),
    ("PAD", "Unknown.", -1),
    ("PAD", "N.K.", -1),
    # The verify of repair 1, finding 6 (V3): placeholders of two and three
    # figures on one cell in five.
    ("R", "-99", 5),
    ("R", "-999", 5),
    ("PAD", "-99", 5),
    ("PAD", "-999", 5),
)


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("case", range(len(MEASURED_WORDS)))
def test_d_keys_beside_any_word_or_placeholder_are_held(
    tmp_path: pathlib.Path, n: int, case: int
) -> None:
    """Skeptic 1, item 2: 0 keys in any file and the twin, the question put once.

    Mutant: `_set_aside_beside_keys` setting aside words of letters alone
    (each of the eight publishes its keys as labels or percentiles).
    """
    form, word, share = MEASURED_WORDS[case]
    header, rows = plain_rows(form, share, n, word)
    seen = run(tmp_path / f"w{case}", header, rows, "key", validate=False)
    assert seen["held"] is True
    assert len(seen["asked"]) == 1 and asking.ANSWER_IDENTIFIER in seen["asked"][0]
    counted = shapes.count_real(PLAIN_KEYS[form], seen["texts"][:3], seen["cells"])
    assert counted["description_values"] == 0, counted
    assert counted["twin_cells"] == 0, counted


def two_in_five_rows(form: str, n: int, word: str) -> "tuple[list[str], list[list[str]]]":
    """`PLAIN_KEYS[form]` beside ``word`` on two cells in five: a mostly missing reference column."""
    draw = random.Random(25)
    keys = PLAIN_KEYS[form]
    rows = [[word if index % 5 < 2 else keys[index % len(keys)], draw.choice(("Sodium", "Glucose"))]
            for index in range(n)]
    return ["key", "test"], rows


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("form", sorted(PLAIN_KEYS))
@pytest.mark.parametrize("word", ["Unknown", "Not recorded"])
def test_d_keys_beside_words_on_two_cells_in_five_are_held(
    tmp_path: pathlib.Path, n: int, form: str, word: str
) -> None:
    """The verify of repair 1, finding 4 (HIPAA): words past one cell in three set aside.

    `Unknown` on two cells in five made the keys labels: 24 keys printed
    and 360 of 600 real twin cells (12,000 of 20,000). Words with no
    figure are set aside whatever their share: 0 keys in any file and the
    twin, held, the question put once. Mutant: words capped at one present
    cell in three again (`_set_aside_within_reach` counting words in the
    cap).
    """
    header, rows = two_in_five_rows(form, n, word)
    seen = run(tmp_path / f"{form}-{word[:3]}".lower(), header, rows, "key", validate=False)
    assert seen["held"] is True
    assert len(seen["asked"]) == 1 and asking.ANSWER_IDENTIFIER in seen["asked"][0]
    counted = shapes.count_real(PLAIN_KEYS[form], seen["texts"][:3], seen["cells"])
    assert counted["description_values"] == 0, counted
    assert counted["twin_cells"] == 0, counted


@pytest.mark.parametrize("n", SIZES)
@pytest.mark.parametrize("form", ["R", "PAD"])
def test_d_keys_beside_a_placeholder_on_two_cells_in_five_are_held(
    tmp_path: pathlib.Path, n: int, form: str
) -> None:
    """Keys beside `-99` on two cells in five: no measurement is written `R1000`, or `0100` to `0139`.

    Before, the lettered keys were labels (25 keys printed) and the padded
    ones a count (one key in its percentiles, 19,801 of 20,000 twin cells
    real). Mutant: the one-in-three cap kept for placeholders of figures
    (`_set_aside_within_reach` capped).
    """
    header, rows = two_in_five_rows(form, n, "-99")
    seen = run(tmp_path / "m99", header, rows, "key", validate=False)
    assert seen["held"] is True
    assert len(seen["asked"]) == 1 and asking.ANSWER_IDENTIFIER in seen["asked"][0]
    counted = shapes.count_real(PLAIN_KEYS[form], seen["texts"][:3], seen["cells"])
    assert counted["description_values"] == 0 and counted["twin_cells"] == 0, counted


def test_d_words_beside_a_stray_key_are_not_asked() -> None:
    """The floor's key cells: words beside fewer than eleven key cells are not asked.

    Mutant: no floor of key cells (`_KEY_CELLS_AT_LEAST` 1: a column of
    `Yes`/`No` beside ten `R1000`-shaped cells asked).
    """
    draw = random.Random(10)
    words = [draw.choice(["Yes", "No", "Unknown"]) for _row in range(590)]
    assert not asking._keys_beside_words(words + [f"R{1000 + k % 5}" for k in range(10)])
    assert asking._keys_beside_words(words + [f"R{1000 + k % 5}" for k in range(11)])
    padded = ["Unknown"] * 590 + [PLAIN_KEYS["PAD"][k % 5] for k in range(10)]
    assert not asking._padded_beside_words(padded)


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
