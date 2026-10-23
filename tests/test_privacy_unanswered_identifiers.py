"""P4-D401 (lane HX): no real identifier is published while its question is open.

THE FINDING (wave6/ZOO/CRITIC.md item 1, measured at 68dae22f). A long
table -- 600 rows over 44 patients, `record` written `REC1000xxxx` on each
patient's rows -- profiled with the person question offered and nobody
answering: `record` was read as labels and the description named 26 of the
44 real record numbers, every one on 11 rows or more, and the twin wrote
them back. The owner's principle (2026-10-01): the one threat is HIPAA
exposure, and a record number is a direct identifier whatever its count.

THE RULE, in the owner's pattern of 2026-09-17 (ruling 8: "do not guess,
ask"), applied literally by the orchestrator's ruling of 2026-10-16. A
column put a question offering `identifier` -- the person question, the
two-numbers question, the questions asked of padded, fixed-width or
grouped figures, of points, of date counts, of dates written like codes;
any question but the checklist of columns read as numbers -- that nobody
answered is described as record numbers until it is answered: no level
name, prefix, rung, percentile, mode, tail value or example, and the twin
writes made-up record numbers there. The question is still asked. Any
answer gives back what that answer describes, byte for byte, and a table
where no such question is put is described as before.

THE GATE, one case per shape at 600 rows (20,000 rows through
`tools/measurements/kpi_run.py --slow`, ledger K-S3-64): 0 real values and
0 fragments in the description, the summary, the questions file and the
screen, 0 in the twin, and the question still asked. Three shapes no
question flags -- a name, a street address, a full birth date -- on a long
table with no subject column are a STATED LIMIT (P4-D406 item (a)), pinned
as strict expected failures that turn red the day it closes; beside a
patient key the count in people of lane HX2 holds them
(`tests/test_stage4_counted_in_persons.py`).
"""

from __future__ import annotations

import json
import pathlib
import random
import re

import pytest

from synthtwin import asking, cli, profile, reading, taxonomy

import unanswered_identifier_shapes as shapes

_ROWS = 600


def _check_held(seen: "dict[str, object]", kind: str) -> None:
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    # THE TWIN MEETS ITS OWN DESCRIPTION (lane HX's tripwire, item 4),
    # but where the generator misses a declared record number the same
    # way (`shapes.VALIDATION_LIMITS`, plan P4-D401).
    if kind not in shapes.VALIDATION_LIMITS:
        assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    # THE QUESTION IS STILL ASKED, `identifier` among its answers, and the
    # file says what leaving it blank keeps.
    asked = seen["asked"]
    assert isinstance(asked, list) and asked
    assert asking.ANSWER_IDENTIFIER in asked[0]
    assert seen["read_as_now"] == [asking.ANSWER_IDENTIFIER]
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert seen["evidence"] == taxonomy.rendered(
        taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ()
    )
    assert "COLUMNS HELD BACK UNTIL YOU ANSWER" in f"{seen['screen']}"


@pytest.mark.parametrize("kind", shapes.HELD)
def test_an_unanswered_identifier_publishes_nothing_real(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """0 real values or fragments anywhere published and in the twin; still asked."""
    seen = shapes.run(tmp_path, kind, _ROWS)
    _check_held(seen, kind)
    assert seen["forced_identifiers"] == [kind]
    # The population is still counted as it was.
    assert seen["person_columns"] == []


@pytest.mark.parametrize("kind", shapes.BESIDE)
def test_an_identifier_beside_a_declared_person_column_is_held(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """Beside a declared person column, no value of a register one person holds is published.

    Lane HX2 (plan P4-D406): every value is counted in the declared people
    as the column is described, and each of these values is one person's,
    so the column is held as a record number counted in people (NF126)
    before any question is worked out; no answer could give a value back.
    """
    seen = shapes.run(tmp_path, kind, _ROWS)
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert seen["evidence"] == taxonomy.rendered(taxonomy.EVIDENCE_HELD_IN_PEOPLE, ())
    assert seen["forced_identifiers"] == sorted(["patient", kind])
    assert seen["person_columns"] == ["patient"]
    assert "VALUES HELD BY FEWER THAN 11 PEOPLE" in f"{seen['screen']}"


@pytest.mark.parametrize("kind", shapes.STATED)
@pytest.mark.xfail(
    strict=True,
    reason=(
        "STATED LIMIT (P4-D401, P4-D406 item (a)): a name, a street address "
        "or a birth date on a long table with no subject column -- nothing "
        "declared and no person question put -- has no people to count in; "
        "beside a patient key (`shapes.COUNTED`) lane HX2 holds them"
    ),
)
def test_a_shape_no_question_flags_is_a_stated_limit(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """Strict: it fails while the limit stands, and turns red when it closes."""
    seen = shapes.run(tmp_path, kind, _ROWS)
    assert seen["description_values"] == 0 and seen["twin_cells"] == 0


# -- what the count counts (Codex's review of lane HX, item 4) -----------


def test_the_count_finds_a_value_wrapped_in_other_characters() -> None:
    """A real value inside a twin cell, or a text, is found by substring."""
    real = ["REC10000000", "REC10000007"]
    clean = shapes.count_real(real, ["nothing here", "RECORD HELD BACK"], ["APT07388860"])
    assert clean == {"description_values": 0, "description_fragments": 0,
                     "twin_cells": 0, "twin_fragments": 0}
    wrapped = shapes.count_real(real, ["a summary naming xxREC10000007yy"],
                                ["ZZREC10000000ZZ", "APT07388860"])
    assert wrapped["description_values"] == 1
    assert wrapped["description_fragments"] >= 1
    assert wrapped["twin_cells"] == 1 and wrapped["twin_fragments"] >= 1
    # ...and a published prefix, standing alone.
    prefix = shapes.count_real(real, ['"layout_prefixes": {"REC": 40}'], [])
    assert prefix["description_fragments"] == 1


def test_the_count_finds_figures_printed_as_a_number() -> None:
    """`02100` printed `2100.0`, and `123,456,789` printed `123456789`."""
    zips = shapes.count_real(["02100"], ['"p50": 2100.0'], ["2100"])
    assert zips["description_values"] == 1 and zips["twin_cells"] == 1
    grouped = shapes.count_real(["123,456,789"], ["mode 123456789"], [])
    assert grouped["description_values"] == 1
    assert shapes.count_real(["02100"], ['"rows": 21000'], [])["description_values"] == 0


def test_the_measurement_runs_scripted_whatever_the_terminal(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Codex's item 5: a terminal on the process's own handles asks nothing.

    Redirecting Python's output leaves descriptors 0 and 1 on the
    terminal, so the run would see a person and wait for one; the
    measurement says nobody is there, and the column is held.
    """
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)

    def _nobody_answers(*_given: object) -> str:
        raise AssertionError("the measurement waited for a person")

    monkeypatch.setattr(cli, "_read_one_answer", _nobody_answers)
    seen = shapes.run(tmp_path, "record", _ROWS)
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert cli._there_is_somebody_to_ask() is True, "and it is put back"


# -- the answers ----------------------------------------------------------


def _answer(
    folder: pathlib.Path, kind: str, answer: "str | None",
    extra: "list[dict[str, object]] | None" = None,
) -> "tuple[int, dict[str, object]]":
    """Answer the column's question in the file the run wrote, and run again.

    ``answer`` None hands the file back as it was written.
    """
    questions = folder / f"{kind}_long-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    if answer is not None:
        for entry in document["asked"]:
            if entry["column"] == kind:
                entry["your_answer"] = answer
    if extra:
        document["about_your_file"] = list(document.get("about_your_file", [])) + extra
    answers = folder / "answers.json"
    answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    table = folder / f"{kind}_long.csv"
    with shapes.nobody_at_the_keyboard():
        code = cli.main(["profile", f"{table}", "--out-dir", f"{folder}",
                         "--replace", "--answers", f"{answers}"])
    return code, json.loads(
        (folder / f"{kind}_long-profile.json").read_text(encoding="utf-8")
    )


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    columns = document["columns"]
    assert isinstance(columns, list)
    return [one for one in columns if one["name"] == name][0]


def _asked_of(folder: pathlib.Path, kind: str) -> "list[dict[str, object]]":
    asked = json.loads(
        (folder / f"{kind}_long-questions.json").read_text(encoding="utf-8")
    )["asked"]
    return [entry for entry in asked if entry["column"] == kind]


def test_answering_keep_gives_back_the_labels(tmp_path: pathlib.Path) -> None:
    """`keep` is the reading the rules made: the levels are back, named."""
    shapes.run(tmp_path, "record", _ROWS)
    code, document = _answer(tmp_path, "record", asking.ANSWER_KEEP)
    assert code == 0
    block = _block(document, "record")
    assert block["role"] == taxonomy.ROLE_CATEGORICAL
    assert block["levels"], "the answer `keep` publishes the levels it names"
    settings = document["settings"]
    assert isinstance(settings, dict) and settings["forced_identifiers"] == []
    # ...and the file asks again under the reading in force, as before.
    assert [entry["read_as_now"] for entry in _asked_of(tmp_path, "record")] == [
        asking.ANSWER_KEEP
    ]


def test_a_keep_survives_the_file_it_wrote_handed_back_blank(
    tmp_path: pathlib.Path,
) -> None:
    """Three runs: held, `keep`, and the rewritten file handed back unchanged.

    The skeptic's item 4 and Codex's item 3: the file the second run
    writes asks again under `read_as_now: keep`, and says a blank keeps
    the reading it names -- so the third run keeps the labels.
    """
    shapes.run(tmp_path, "record", _ROWS)
    code, second = _answer(tmp_path, "record", asking.ANSWER_KEEP)
    assert code == 0
    code, third = _answer(tmp_path, "record", None)
    assert code == 0
    assert _block(third, "record")["role"] == taxonomy.ROLE_CATEGORICAL
    assert profile.serialize(third) == profile.serialize(second)


def test_a_keep_under_an_answer_that_moves_the_columns_is_asked_again(
    tmp_path: pathlib.Path,
) -> None:
    """A `keep` beside a delimiter answer may name another column: held."""
    shapes.run(tmp_path, "record", _ROWS)
    delimiter = {
        "column": asking.DELIMITER_SUBJECT,
        "answers_you_can_give": [{"answer": "comma"}, {"answer": "semicolon"}],
        "your_answer": "comma",
    }
    code, document = _answer(tmp_path, "record", asking.ANSWER_KEEP, [delimiter])
    assert code == 0
    assert _block(document, "record")["role"] == taxonomy.ROLE_IDENTIFIER
    assert [entry["read_as_now"] for entry in _asked_of(tmp_path, "record")] == [
        asking.ANSWER_IDENTIFIER
    ]


def test_the_held_entry_says_what_a_blank_keeps(tmp_path: pathlib.Path) -> None:
    """Rows still counted as rows; typing `identifier` declares, under the floor."""
    shapes.run(tmp_path, "record", _ROWS)
    entry = _asked_of(tmp_path, "record")[0]
    said = f"{entry['what_synthtwin_saw']}"
    assert said.endswith(asking.HELD_BACK_SAID)
    assert "the rows are still counted as rows" in said
    assert "Leaving the answer blank keeps it so" in said


def test_answering_code_on_the_fixed_width_question_gives_back_the_codes(
    tmp_path: pathlib.Path,
) -> None:
    """`code` declares the column a code, and its values are published so."""
    shapes.run(tmp_path, "account", _ROWS)
    code, document = _answer(tmp_path, "account", asking.ANSWER_CODE)
    assert code == 0
    assert _block(document, "account")["role"] != taxonomy.ROLE_IDENTIFIER
    settings = document["settings"]
    assert isinstance(settings, dict)
    assert settings["forced_codes"] == ["account"]
    assert settings["forced_identifiers"] == []


def test_answering_identifier_counts_the_people(tmp_path: pathlib.Path) -> None:
    """`identifier` is the declaration: 44 people is under the floor, refused."""
    shapes.run(tmp_path, "record", _ROWS)
    questions = tmp_path / "record_long-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        entry["your_answer"] = asking.ANSWER_IDENTIFIER
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard():
        code = cli.main(["profile", f"{tmp_path / 'record_long.csv'}", "--out-dir",
                         f"{tmp_path / 'again'}", "--answers", f"{answers}"])
    assert code == 1, "44 people is under the population floor"


def test_a_person_at_the_keyboard_has_answered(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Enter at the keyboard is an answer: the reading it keeps is published."""
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    monkeypatch.setattr(cli, "_read_one_answer", lambda standing: "")
    table, _real = shapes.write_table(tmp_path, "record", _ROWS)
    assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}"]) == 0
    document = json.loads(
        (tmp_path / "record_long-profile.json").read_text(encoding="utf-8")
    )
    assert _block(document, "record")["role"] == taxonomy.ROLE_CATEGORICAL


# -- what is not held -----------------------------------------------------


def _profile_rows(folder: pathlib.Path, name: str, lines: "list[str]",
                  extra: "list[str] | None" = None) -> "tuple[int, dict[str, object]]":
    table = folder / f"{name}.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    with shapes.nobody_at_the_keyboard():
        code = cli.main(["profile", f"{table}", "--out-dir", f"{folder}"] + (extra or []))
    document: "dict[str, object]" = {}
    described = folder / f"{name}-profile.json"
    if described.is_file():
        document = json.loads(described.read_text(encoding="utf-8"))
    return code, document


def test_the_checklist_holds_nothing(tmp_path: pathlib.Path) -> None:
    """A lab value on the checklist keeps its statistics beside a held column."""
    seen = shapes.run(tmp_path, "record", _ROWS)
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    document = json.loads(
        (tmp_path / "record_long-profile.json").read_text(encoding="utf-8")
    )
    block = _block(document, "value")
    assert block["role"] == taxonomy.ROLE_CONTINUOUS and "percentiles" in block
    listed = json.loads(
        (tmp_path / "record_long-questions.json").read_text(encoding="utf-8")
    )["checklist"]["columns"]
    assert [entry["column"] for entry in listed] == ["value"]


def test_a_register_of_codes_the_person_question_reaches_beside_declared_people(
    tmp_path: pathlib.Path,
) -> None:
    """With who the rows are about declared, a code register is not asked."""
    codes = ("HCC18", "HCC19", "HCC85", "HCC96", "HCC108", "HCC111",
             "HCC22", "HCC40", "HCC48", "HCC59", "HCC86", "HCC88")
    draw = random.Random(5)
    lines = ["patient,dx,value"] + [
        f"REC{20000000 + 7 * draw.randrange(150):08d},"
        f"{codes[draw.randrange(len(codes))]},{draw.uniform(1, 9):.1f}"
        for _row in range(_ROWS)
    ]
    code, document = _profile_rows(tmp_path, "dx_long", lines,
                                   ["--identifier", "patient"])
    assert code == 0
    block = _block(document, "dx")
    assert block["role"] == taxonomy.ROLE_CATEGORICAL and block["levels"]
    asked = json.loads(
        (tmp_path / "dx_long-questions.json").read_text(encoding="utf-8")
    )["asked"]
    assert [entry for entry in asked if entry["column"] == "dx"] == []


@pytest.mark.parametrize("shape", ["clock", "stamp", "point"])
def test_a_question_about_dates_or_times_holds_nothing(
    tmp_path: pathlib.Path, shape: str
) -> None:
    """Clock times put the two-numbers question, HL7 stamps the codes question: kept.

    Each question offers `identifier`, and neither is about record
    numbers: the cells were read as times of day or as dates, and held
    they would write record numbers where the times and dates stood.
    ...and the question of a point between thousands (`12.345`), which
    is about how a number is written and is not one the ruling names.
    """
    draw = random.Random(3)
    cells: "list[str]" = []
    for _row in range(_ROWS):
        if shape == "clock":
            cells += [f"{draw.randint(0, 23)}:{('00', '15', '30', '45')[draw.randrange(4)]}"]
        elif shape == "stamp":
            cells += [f"2023{draw.randint(1, 12):02d}{draw.randint(1, 28):02d}"
                      f"{draw.randint(0, 23):02d}{draw.randint(0, 59):02d}"
                      f"{draw.randint(0, 59):02d}"]
        elif draw.random() < 0.5:
            cells += [f"{draw.randint(1, 99)}.{draw.randint(0, 999):03d}"]
        else:
            cells += [f"{draw.randint(1, 999)}"]
    code, document = _profile_rows(
        tmp_path, shape, ["t,value"] + [f"{cell},{draw.randint(1, 9)}" for cell in cells]
    )
    assert code == 0
    expected = {"clock": taxonomy.ROLE_CLOCK, "stamp": taxonomy.ROLE_DATETIME,
                "point": taxonomy.ROLE_CONTINUOUS}[shape]
    assert _block(document, "t")["role"] == expected
    assert document["settings"]["forced_identifiers"] == []
    asked = json.loads(
        (tmp_path / f"{shape}-questions.json").read_text(encoding="utf-8")
    )["asked"]
    offered = [
        [choice["answer"] for choice in entry["answers_you_can_give"]]
        for entry in asked if entry["column"] == "t"
    ]
    assert offered and asking.ANSWER_IDENTIFIER in offered[0], "still asked"


def test_a_column_of_free_text_put_the_person_question_is_not_held(
    tmp_path: pathlib.Path,
) -> None:
    """Free text publishes no value already; it is asked, and left as it is."""
    words = ("pain", "fever", "cough", "rash", "nausea", "fatigue", "dizzy",
             "swelling", "itch", "chills")
    remarks = [
        f"patient reports {words[one % 10]} and {words[(one // 10) % 10]} "
        f"since visit {one} and follow up advised in {one % 7 + 1} weeks"
        for one in range(300)
    ]
    lines = ["remark,value"] + [
        f"{remarks[row % 300]},{row % 9 + 1}" for row in range(_ROWS)
    ]
    code, document = _profile_rows(tmp_path, "remarks", lines)
    assert code == 0
    block = _block(document, "remark")
    assert not asking.publishes_its_values(f"{block['role']}")
    assert "remark" not in document["settings"]["forced_identifiers"]
    asked = json.loads(
        (tmp_path / "remarks-questions.json").read_text(encoding="utf-8")
    )["asked"]
    assert [entry for entry in asked if entry["column"] == "remark"], "still asked"


def test_a_declared_comma_is_an_answer(tmp_path: pathlib.Path) -> None:
    """Codex's item 1: `--decimal-comma` declares, so nothing is held twice."""
    lines = ["amount,value"] + [
        f"{10000000 + row % 40},{row % 9 + 1}" for row in range(_ROWS)
    ]
    code, document = _profile_rows(tmp_path, "amounts", lines,
                                   ["--decimal-comma", "amount"])
    assert code == 0
    settings = document["settings"]
    assert isinstance(settings, dict)
    assert "amount" not in settings["forced_identifiers"]
    # ...and the description it wrote loads: the twin is built from it.
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["generate", f"{tmp_path / 'amounts-profile.json'}",
                         "--out-dir", f"{tmp_path}", "--seed", "0"]) == 0


def test_a_sign_placeholder_does_not_silence_the_width_question() -> None:
    """`-1` beside keys all one width; a third of the cells or more is a measurement."""
    keys = [f"{100000 + one % 60}" for one in range(588)] + ["-1"] * 12
    assert asking._beside_sign_placeholders(keys) == keys[:588]
    assert asking.why_worth_asking(keys) is None
    assert asking.why_worth_asking(asking._beside_sign_placeholders(keys)) == (
        asking.BECAUSE_FIXED_WIDTH
    )
    many = [f"{100 + one % 60}" for one in range(20)] + ["-1"] * 11
    assert asking._beside_sign_placeholders(many) == []
    assert asking._beside_sign_placeholders(["-1", "-2"]) == []
    assert asking._beside_sign_placeholders(["100", "-10"]) == []


def test_the_held_census_is_the_even_one_the_two_counts_imply(
    tmp_path: pathlib.Path,
) -> None:
    """No group size of the table reaches the held block's census of repetition."""
    def census_of(weights: "list[float]", folder: pathlib.Path) -> object:
        draw = random.Random(3)
        people = [f"REC{10000000 + 7 * one:08d}" for one in range(40)]
        cells = [people[one] for one in range(40)] + draw.choices(
            people, weights, k=_ROWS - 40
        )
        folder.mkdir()
        code, document = _profile_rows(folder, "even", ["record,value"] + [
            f"{cell},{place % 9 + 1}" for place, cell in enumerate(cells)
        ])
        assert code == 0
        block = _block(document, "record")
        assert block["role"] == taxonomy.ROLE_IDENTIFIER
        assert block["n_present"] == _ROWS and block["n_distinct"] == 40
        return block["n_distinct_by_occurrences"]

    flat = census_of([1.0] * 40, tmp_path / "flat")
    steep = census_of([1.0 + one * one for one in range(40)], tmp_path / "steep")
    assert flat == steep == {"15": 40}


def test_the_held_census_fits_each_layout() -> None:
    """Each layout's values are what it can write, the largest remainders closing.

    Lane HX's tripwire, item 4, at 20,000 rows: a six-figure key beside a
    lone `0` on 620 rows gave the `0` two values, which one figure written
    `0` cannot be, and the twin failed its own validation. A layout of one
    figure holds ten values at most.
    """
    assert taxonomy._even_census(20000, {"444": 45}, {"%%%%%%": 19380}) == {
        "440": 24, "441": 20, "620": 1,
    }
    assert taxonomy._even_census(600, {"20": 30}, {"%": 300, "%%%%%%": 300}) == {
        "15": 20, "30": 10,
    }


def test_no_column_held_back_describes_the_table_as_before(
    tmp_path: pathlib.Path,
) -> None:
    """`unanswered` empty or absent is the same description, byte for byte."""
    table, _real = shapes.write_table(tmp_path, "record", _ROWS)
    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", small_cell_floor=settings.small_cell_floor
    )
    before = profile.serialize(profile.build_document(read, settings, []))
    again = profile.serialize(
        profile.build_document(read, settings, [], unanswered=[])
    )
    assert before == again


def test_the_data_rules_name_no_blood_pressure_code_or_date() -> None:
    """Route three's cells against their neighbours, and judged by share."""
    for one in ("a.b@host.org", "c@d.co", "Pat 3 <pat3.x1@mailhost.org>",
                "319-555-1234", "123-45-6789", "+1-319-555-1234", "319 555 1234",
                "319.555.1234", "+1 (319) 555-1234", "1-319-555-1234",
                "319-555-1234 x12", "319-555-1234 ext. 7", "123 45 6789",
                "4111 1111 1111 1111", "4111-1111-1111-1111", "10.0.12.254",
                "https://portal.example.org/p/12345", "www.example.org/p",
                "1EG4TE5MK73", "9AA0-CC0-DE12"):
        assert asking._names_one_person(one), one
    for neighbour in ("120/80", "12345-6789-01", "2024-01-05", "1:2:3",
                      "(319) 555-12345", "12.5.2024", "a@b", "x@y.z w",
                      "nobody", "0EG4TE5MK73", "1SG4TE5MK73", "HCC108", "I10",
                      "1EG4TE5MK7", "NM_000546.6", "10.0.12.256", "1.2.3",
                      "319-555-1234 x", "http:/x", "2024-01-05 x12"):
        assert not asking._names_one_person(neighbour), neighbour
    # BY SHARE (lane HX's tripwire, item 2): one cell in three may be
    # something else, not more.
    addresses = ["a.b@host.org", "c@d.co"]
    assert asking._a_register_naming_one_person_a_cell(addresses + ["not given"])
    assert not asking._a_register_naming_one_person_a_cell(
        addresses + ["not given", "none"]
    )
    assert not asking._a_register_naming_one_person_a_cell([])


def test_route_four_reaches_a_key_of_figures_and_no_scale() -> None:
    """A repeating key five figures wide, beside placeholders; no bounded scale."""
    def rows_of(keys: "list[str]", each: int = 3) -> "list[str]":
        return [key for key in keys for _row in range(each)]

    wide = [f"{100000 + 211 * one}" for one in range(44)]
    assert asking._a_key_of_figures_repeating(rows_of(wide))
    # Across a power of ten: more than half the keys five figures wide.
    assert asking._a_key_of_figures_repeating(
        rows_of([f"{9900 + 13 * one}" for one in range(44)])
    )
    # Exported as decimals, grouped by points, or beside what a key
    # writes for nobody -- under half of the cells.
    assert asking._a_key_of_figures_repeating(rows_of([f"{key}.0" for key in wide]))
    assert asking._a_key_of_figures_repeating(
        rows_of([f"{123456789 + 1013 * one:,}".replace(",", ".") for one in range(44)])
    )
    for nobody in ("0", "-1", "-99", "-999", "UNKNOWN"):
        assert asking._a_key_of_figures_repeating(rows_of(wide) + [nobody] * 60), nobody
    assert not asking._a_key_of_figures_repeating(rows_of(wide) + ["-1"] * 132)
    # NOT a key: a scale or a weight under five figures, a key on one row
    # each, one value, a decimal, or a cell that is neither.
    assert not asking._a_key_of_figures_repeating(rows_of([f"{one}" for one in range(11)], 50))
    assert not asking._a_key_of_figures_repeating(
        rows_of([f"{2500 + 10 * one}" for one in range(200)])
    )
    assert not asking._a_key_of_figures_repeating(wide)
    assert not asking._a_key_of_figures_repeating(["100000"] * 60)
    assert not asking._a_key_of_figures_repeating(rows_of([f"{one}.25" for one in wide]))
    assert not asking._a_key_of_figures_repeating(rows_of(wide) + ["n/a"])
    # Only five figures or more count as wide: half of them is not more
    # than half.
    half = [f"{1000 + one}" for one in range(22)] + wide[:22]
    assert not asking._a_key_of_figures_repeating(rows_of(half))


def test_route_four_is_put_to_a_column_of_counts(tmp_path: pathlib.Path) -> None:
    """A key read as a count gets the person question, and no question of dates."""
    seen = shapes.run(tmp_path, "randkey", _ROWS)
    assert seen["asked"] == [[asking.ANSWER_KEEP, asking.ANSWER_IDENTIFIER]]
    _check_held(seen, "randkey")


def test_a_wider_placeholder_and_a_narrow_measurement() -> None:
    """`0` and nines beside a six-figure key; a three-figure reading is no key."""
    keys = [f"{100000 + one % 60}" for one in range(588)]
    for nobody in ("0", "999999999", "-1"):
        assert asking._beside_sign_placeholders(keys + [nobody] * 12) == keys
    # A systolic pressure writing `-1` or `-9` for a missing reading keeps
    # its description (lane HX's tripwire, item 7).
    systolic = [f"{100 + one % 81}" for one in range(588)]
    assert asking._beside_sign_placeholders(systolic + ["-9"] * 12) == []
    weights = [f"{2500 + one % 1500}" for one in range(588)]
    assert asking._beside_sign_placeholders(weights + ["-1"] * 12) == []


def test_a_three_figure_measurement_beside_minus_one_is_asked_nothing(
    tmp_path: pathlib.Path,
) -> None:
    """Platelets in thousands, `-1` for a missing count: described as before."""
    draw = random.Random(7)
    cells = [f"{draw.randint(150, 450)}" if draw.random() > 0.02 else "-1"
             for _row in range(_ROWS)]
    code, document = _profile_rows(tmp_path, "platelets", ["platelets"] + cells)
    assert code == 0
    block = _block(document, "platelets")
    assert block["role"] != taxonomy.ROLE_IDENTIFIER
    settings = document["settings"]
    assert isinstance(settings, dict) and settings["forced_identifiers"] == []


def test_income_in_whole_thousands_is_held_and_keep_gives_back_the_count(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """A repeating measurement five figures wide is held; `keep` is 68dae22f's.

    Lane HX's second verify, item 1 (P4-D401's price beyond the
    batteries): route four reaches a repeating whole-number measurement
    whose values are mostly five figures or more. Income in whole
    thousands, 15,000 to 180,000 on one row a person, repeats at 600
    rows, so a scripted run asks it the person question and holds it;
    68dae22f read it as a count and asked nothing. The answer `keep`
    gives back, byte for byte, the description made where route four
    asks nothing -- 68dae22f's own.
    """
    draw = random.Random(11)
    lines = ["age,income"] + [
        f"{draw.randint(18, 90)},{draw.randint(15, 180) * 1000}" for _row in range(_ROWS)
    ]
    table = tmp_path / "income.csv"
    table.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")

    def described(folder: pathlib.Path, extra: "list[str]") -> bytes:
        folder.mkdir(exist_ok=True)
        with shapes.nobody_at_the_keyboard():
            code = cli.main(["profile", f"{table}", "--out-dir", f"{folder}"] + extra)
        assert code == 0
        return (folder / "income-profile.json").read_bytes()

    # 68dae22f's reading: the description where route four asks nothing.
    with monkeypatch.context() as before_route_four:
        before_route_four.setattr(
            asking, "_a_key_of_figures_repeating", lambda present: False
        )
        before = described(tmp_path / "before", [])
    assert _block(json.loads(before), "income")["role"] == taxonomy.ROLE_COUNT

    held = json.loads(described(tmp_path / "held", []))
    assert _block(held, "income")["role"] == taxonomy.ROLE_IDENTIFIER
    settings = held["settings"]
    assert isinstance(settings, dict) and settings["forced_identifiers"] == ["income"]
    questions = json.loads(
        (tmp_path / "held" / "income-questions.json").read_text(encoding="utf-8")
    )
    asked = [entry for entry in questions["asked"] if entry["column"] == "income"]
    assert [
        [choice["answer"] for choice in entry["answers_you_can_give"]] for entry in asked
    ] == [[asking.ANSWER_KEEP, asking.ANSWER_IDENTIFIER]]
    assert [entry["read_as_now"] for entry in asked] == [asking.ANSWER_IDENTIFIER]

    for entry in asked:
        entry["your_answer"] = asking.ANSWER_KEEP
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(questions), encoding="utf-8", newline="\n")
    kept = described(tmp_path / "held", ["--replace", "--answers", f"{answers}"])
    assert kept == before


@pytest.mark.parametrize("answer", [asking.ANSWER_MEASUREMENT, asking.ANSWER_CODE])
def test_an_answer_survives_the_file_it_wrote_handed_back(
    tmp_path: pathlib.Path, answer: str
) -> None:
    """Three runs: held, answered, and the rewritten file handed back unchanged.

    Lane HX's tripwire, item 6: the file the answering run writes carries
    the answer beside its entry, so the third description is the second.
    """
    shapes.run(tmp_path, "plain6", _ROWS)
    code, second = _answer(tmp_path, "plain6", answer)
    assert code == 0
    assert _block(second, "plain6")["role"] != taxonomy.ROLE_IDENTIFIER
    assert _asked_of(tmp_path, "plain6") == [], "no longer asked"
    written = json.loads(
        (tmp_path / "plain6_long-questions.json").read_text(encoding="utf-8")
    )
    assert [
        (one["column"], one["read_as_now"], one["your_answer"])
        for one in written["answered_before"]
    ] == [("plain6", answer, answer)]
    code, third = _answer(tmp_path, "plain6", None)
    assert code == 0
    assert profile.serialize(third) == profile.serialize(second)


def test_the_count_finds_figures_beside_letters() -> None:
    """`ACC30000484` printed as a number, as the tripwire measured it."""
    real = ["ACC30000484"]
    assert shapes.count_real(real, ['"mode": 30000484.0'], [])["description_values"] == 1
    assert shapes.count_real(real, ['"p50": 130000484.0'], [])["description_values"] == 0
    assert shapes.count_real(real, ['"p50": 0.30000484'], [])["description_values"] == 0
    assert shapes.count_real(real, [], ["KXA30000484"])["twin_cells"] == 1
    # ...and figures alone are not found inside a decimal of another column.
    assert shapes.count_real(["100000"], ['"p53": 82.34100000000001'], [])[
        "description_values"
    ] == 0


def test_the_contract_quotes_the_sentence_the_product_writes() -> None:
    """NF125's quoted line is `rendered(EVIDENCE_UNANSWERED_IDENTITY)`, character for character."""
    contract = (
        pathlib.Path(__file__).resolve().parents[1]
        / "docs" / "spec" / "profile-contract-v6.md"
    ).read_text(encoding="utf-8")
    entry = contract[contract.index("**NF125. `evidence_unanswered_identity`"):]
    quoted = entry[entry.index("\n\n> ") + len("\n\n> "):]
    said = taxonomy.rendered(taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ())
    assert quoted[: quoted.index("\n")] == said


# -- a list of record numbers in one cell (plan P4-D424, lane HX4) ----------
#
# Measured on 91ee9374 by lane ZR-a's second repair (`probe-where.log`):
# one to three six-figure record numbers a cell, drawn from 40, read as a
# long tail, published two record numbers as levels and asked nothing.
# Here each form is held at 600 and 20,000 rows: at 600 rows by the list
# question, which offers `code` and `identifier` beside `keep`; at 20,000
# rows the person question reaches the whole cells first (more different
# cells than the categories ceiling, repeating) and the list question is
# never put as a second question, except beside a declared person column,
# where the person question is not put.
#
# LANE HX4'S REPAIR 1 adds the shapes that published record numbers on
# 6c566d3c (`shapes.LISTED`): marks mixed cell by cell, one list cell
# among single record numbers, a mark closing each list cell, and
# comma-grouped keys separated by spaces.

_LIST_ANSWERS = [asking.ANSWER_KEEP, asking.ANSWER_CODE, asking.ANSWER_IDENTIFIER]
# At 20,000 rows the person question reaches these whole cells first; every
# other register list is put the list question at both sizes.
_PERSON_FIRST = ("reglist6", "reglist7", "reglistR", "reglisttrail6", "reglistgrouped")
# ...and these read as free text at 600 rows, which publishes no value: the
# list question is put, and nothing needs holding.
_FREE_TEXT_AT_600 = ("reglisttrail6", "reglistgrouped")


def _check_list_held(seen: "dict[str, object]", rows: int, kind: str) -> None:
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    if kind not in shapes.VALIDATION_LIMITS:
        assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    if rows == _ROWS and kind in _FREE_TEXT_AT_600:
        assert seen["role"] == taxonomy.ROLE_TEXT
    else:
        assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    asked = seen["asked"]
    assert isinstance(asked, list) and len(asked) == 1, "one question, never two"
    if rows != _ROWS and kind in _PERSON_FIRST:
        assert asked == [[asking.ANSWER_KEEP, asking.ANSWER_IDENTIFIER]]
    else:
        assert asked == [_LIST_ANSWERS]


@pytest.mark.parametrize("rows", (_ROWS, 20000))
@pytest.mark.parametrize("kind", shapes.LISTED)
def test_a_list_of_record_numbers_is_held_until_answered(
    tmp_path: pathlib.Path, kind: str, rows: int
) -> None:
    """0 of the 40 record numbers published, 0 twin cells holding one; one question."""
    seen = shapes.run(tmp_path, kind, rows)
    _check_list_held(seen, rows, kind)
    if rows == _ROWS:
        assert "THESE COLUMNS HOLD SEVERAL VALUES IN A CELL" in f"{seen['screen']}"
    if rows == _ROWS and kind not in _FREE_TEXT_AT_600:
        assert seen["read_as_now"] == [asking.ANSWER_IDENTIFIER]
        assert seen["evidence"] == taxonomy.rendered(
            taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ()
        )
        assert "COLUMNS HELD BACK UNTIL YOU ANSWER" in f"{seen['screen']}"


def _listing_off(monkeypatch: pytest.MonkeyPatch) -> None:
    """The tree before lane HX4: no list is asked about."""
    monkeypatch.setattr(
        asking, "listed_record_number_questions", lambda *named, **said: []
    )


def test_mutant_the_list_rule_off_publishes_record_numbers(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the rule off, the six-figure form publishes record numbers (2 at 600 rows)."""
    _listing_off(monkeypatch)
    seen = shapes.run(tmp_path, "reglist6", _ROWS)
    assert seen["description_values"] > 0 and seen["twin_cells"] > 0
    with pytest.raises(AssertionError):
        _check_list_held(seen, _ROWS, "reglist6")


def _answered_list(
    folder: pathlib.Path, answer: str, questions: "pathlib.Path | None" = None
) -> "tuple[int, pathlib.Path]":
    """Answer reglist6's question in the file a run wrote (or hand `questions` back), into a folder of its own."""
    source = questions or folder / "reglist6_long-questions.json"
    document = json.loads(source.read_text(encoding="utf-8"))
    if questions is None:
        for entry in document["asked"]:
            if entry["column"] == "reglist6":
                entry["your_answer"] = answer
    answers = folder / f"answers-{answer}.json"
    answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    out = folder / f"answered-{answer}"
    out.mkdir()
    with shapes.nobody_at_the_keyboard():
        code = cli.main(["profile", f"{folder / 'reglist6_long.csv'}", "--out-dir",
                         f"{out}", "--answers", f"{answers}"])
    return code, out


def _described_before(
    folder: pathlib.Path, name: str, typed: "list[str]", monkeypatch: pytest.MonkeyPatch
) -> pathlib.Path:
    """The same table described with the list rule off (today's tree), `typed` on the command line."""
    out = folder / name
    out.mkdir()
    with monkeypatch.context() as patched:
        _listing_off(patched)
        with shapes.nobody_at_the_keyboard():
            assert cli.main(["profile", f"{folder / 'reglist6_long.csv'}", "--out-dir",
                             f"{out}"] + typed) == 0
    return out


@pytest.mark.parametrize(
    ("answer", "typed"),
    [
        (asking.ANSWER_KEEP, []),
        (asking.ANSWER_CODE, ["--code", "reglist6"]),
        (asking.ANSWER_IDENTIFIER, ["--identifier", "reglist6"]),
    ],
)
def test_each_answer_to_the_list_question_gives_todays_bytes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, answer: str, typed: "list[str]"
) -> None:
    """`keep` and `code` read the list as today; `identifier` keeps it held.

    Each answered description and summary are byte for byte today's tree's
    with nothing typed (`keep`), `--code` typed (`code`) or `--identifier`
    typed (`identifier`, which publishes no value).
    """
    shapes.run(tmp_path, "reglist6", _ROWS)
    code, out = _answered_list(tmp_path, answer)
    assert code == 0
    before = _described_before(tmp_path, f"before-{answer}", typed, monkeypatch)
    for page in ("reglist6_long-profile.json", "reglist6_long-profile.txt"):
        assert (out / page).read_bytes() == (before / page).read_bytes(), page
    block = _block(json.loads((out / "reglist6_long-profile.json").read_text(encoding="utf-8")),
                   "reglist6")
    if answer == asking.ANSWER_IDENTIFIER:
        assert block["role"] == taxonomy.ROLE_IDENTIFIER
    else:
        assert block["role"] != taxonomy.ROLE_IDENTIFIER


def _code_kept(folder: pathlib.Path) -> None:
    """Answered `code`, then the file that run wrote handed back blank: still read as codes."""
    shapes.run(folder, "reglist6", _ROWS)
    code, out = _answered_list(folder, asking.ANSWER_CODE)
    assert code == 0
    code, again = _answered_list(folder, "again", out / "reglist6_long-questions.json")
    assert code == 0
    document = json.loads((again / "reglist6_long-profile.json").read_text(encoding="utf-8"))
    settings = document["settings"]
    assert isinstance(settings, dict)
    assert settings["forced_codes"] == ["reglist6"], "the answer was lost"
    assert _block(document, "reglist6")["role"] != taxonomy.ROLE_IDENTIFIER


def test_the_list_answer_is_kept_in_the_questions_file(tmp_path: pathlib.Path) -> None:
    """The questions file keeps the answer (plan P4-D408): a second round reads it again."""
    _code_kept(tmp_path)


def test_mutant_the_list_answer_lost_is_seen(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the file a run writes keeps no earlier answer, so the list is held again."""
    monkeypatch.setattr(asking, "answered_before", lambda given: [])
    with pytest.raises(AssertionError, match="the answer was lost"):
        _code_kept(tmp_path)


def _list_cells(values: "list[str]", mark: str, rows: int, seed: int = 7) -> "list[str]":
    draw = random.Random(seed)
    return [mark.join(draw.sample(values, draw.randint(1, 3))) for _row in range(rows)]


def test_the_list_rule_reaches_record_numbers_and_no_short_code() -> None:
    """The three forms on every mark, the identity routes on values; short codes, sums and words not."""
    draw = random.Random(11)
    six = [f"{draw.randint(100000, 999999)}" for _key in range(40)]
    for mark in (";", "|", ",", " "):
        assert asking._listed_record_numbers(_list_cells(six, mark, 600), "free_text") == (
            mark, "wide")
    seven = [f"0{one}" for one in six]
    lettered = [f"R{one}" for one in six]
    for keys in (seven, lettered):
        assert asking._listed_record_numbers(_list_cells(keys, ";", 600), "long_tail_labels")[1] == "wide"
    padded = [f"0{draw.randint(100, 999)}" for _key in range(40)]
    assert asking._listed_record_numbers(_list_cells(padded, "|", 600), "free_text")[1] == "padded"
    codes = [f"A{draw.randint(10, 99)}B" for _key in range(30)]
    assert asking._listed_record_numbers(_list_cells(codes, ";", 600), "free_text")[1] == "codes"
    mails = [f"pat{one}@mailhost.org" for one in range(40)]
    assert asking._listed_record_numbers(_list_cells(mails, "; ", 600), "free_text")[1] == "persons"
    # Most values not wide (four-figure keys and `UNKNOWN`), fewer than
    # half `UNKNOWN`, most different keys five figures: route four (at one
    # value in two, lane HX4's repair 2, a key list with fewer than half
    # placeholders is wide first).
    mostly = six[:21] + [f"{draw.randint(1000, 9999)}" for _key in range(19)]
    keyed = _list_cells(mostly, ";", 600, seed=5) + ["UNKNOWN"] * 300
    assert asking._listed_record_numbers(keyed, "free_text")[1] == "keys"
    # NOT REACHED: three-figure codes 101 to 106, of mixed widths 3 and 4,
    # all four figures; grouped thousands and decimal commas; ICD codes
    # with points; free text; one cell of two values; a list read as dates.
    short = [f"{one}" for one in range(101, 107)]
    mixed = [f"{draw.choice([draw.randint(100, 999), draw.randint(1000, 9999)])}" for _key in range(20)]
    four = [f"{draw.randint(1000, 9999)}" for _key in range(20)]
    for values in (short, mixed, four):
        for mark in (";", ","):
            for rows in (_ROWS, 20000):
                assert asking._listed_record_numbers(_list_cells(values, mark, rows), "categorical") == ("", "")
    sums = [f"{draw.randint(1, 9999):,}" for _row in range(600)] + ["12,05", "3,75"]
    icd = _list_cells(["E11.9", "I10", "J45.909", "N18.3"], ";", 600)
    words = [" ".join(draw.choice(["pain", "fever", "cough"]) for _word in range(5)) for _row in range(600)]
    for cells in (sums, icd, words):
        assert asking._listed_record_numbers(cells, "free_text") == ("", "")
    # ONE LIST CELL IS A LIST (lane HX4's repair 1, skeptic 1's item 2): at
    # two cells, this column read `count` and published 40 of 40.
    once = [six[0]] * 599 + [f"{six[0]};{six[1]}"]
    assert asking._listed_record_numbers(once, "free_text") == (";", "wide")
    assert asking._listed_record_numbers(_list_cells(six, ";", 600), taxonomy.ROLE_DATETIME) == ("", "")


def test_mutant_the_five_figure_bound_ignored_reaches_short_codes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The mutant: a run of one figure taken as wide, so a list of three- and four-figure codes is held."""
    draw = random.Random(11)
    mixed = [f"{draw.choice([draw.randint(100, 999), draw.randint(1000, 9999)])}" for _key in range(20)]
    cells = _list_cells(mixed, ";", _ROWS)
    assert asking._listed_record_numbers(cells, "categorical") == ("", "")
    monkeypatch.setattr(asking, "_KEY_FIGURES", 1)
    assert asking._listed_record_numbers(cells, "categorical") == (";", "wide")


def test_a_list_of_three_figure_codes_is_held_by_the_person_question_alone(
    tmp_path: pathlib.Path,
) -> None:
    """Codes 101 to 106, one to three a cell, are not this rule's: what holds them is today's.

    At 600 rows the person question reaches the whole cells (more different
    cells than the categories ceiling of 60, repeating), offering `keep` and
    `identifier` as today, and the list question is not put. At 20,000 rows
    nothing holds them: 156 combinations under the ceiling of 1,000 read as
    categories, published as today (the rule's own reading is asserted in
    `test_the_list_rule_reaches_record_numbers_and_no_short_code`).
    """
    cells = _list_cells([f"{one}" for one in range(101, 107)], ";", _ROWS)
    draw = random.Random(3)
    lines = ["codes,value"] + [f"{cell},{draw.uniform(1, 9):.1f}" for cell in cells]
    code, document = _profile_rows(tmp_path, "codes_long", lines)
    assert code == 0
    asked = json.loads(
        (tmp_path / "codes_long-questions.json").read_text(encoding="utf-8")
    )["asked"]
    offered = [[choice["answer"] for choice in entry["answers_you_can_give"]]
               for entry in asked if entry["column"] == "codes"]
    assert offered == [[asking.ANSWER_KEEP, asking.ANSWER_IDENTIFIER]]
    assert _block(document, "codes")["role"] == taxonomy.ROLE_IDENTIFIER


# -- lane HX4's repair 1: each escape pinned, each by its mutant -------------


def _first_mark_only(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: only the first mark that makes a list is judged (6c566d3c's rule)."""
    judged: "list[str]" = []
    real = asking._listed_on

    def first_only(present: "list[str]", mark: str, values: int) -> str:
        judged.append(mark)
        return real(present, mark, values) if len(judged) == 1 else ""

    monkeypatch.setattr(asking, "_listed_on", first_only)


def test_mutant_6c566d3cs_rule_publishes_mixed_lists(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1's item 1: marks drawn from `;`, `,` and `|` published 40 of 40 at 20,000 rows.

    The mutant is 6c566d3c's rule whole: only the first mark judged, every
    value wide. Either repair alone holds this shape (the share of the
    addendum reads its other marks' cells as the third that is no key), so
    each is pinned apart too: the first mark alone below, every value
    wide by Codex's case of the addendum.
    """
    _first_mark_only(monkeypatch)
    monkeypatch.setattr(asking, "_LIST_NO_KEY_SHARE", 10**9)
    seen = shapes.run(tmp_path, "reglistmix6", 20000)
    assert seen["description_values"] > 0 and seen["twin_cells"] > 0
    with pytest.raises(AssertionError):
        _check_list_held(seen, 20000, "reglistmix6")


def _mostly_on_commas() -> "list[str]":
    """Six-figure lists, one cell in ten on `;` and the rest on `,`."""
    draw = random.Random(13)
    six = [f"{draw.randint(100000, 999999)}" for _key in range(40)]
    return [(";" if place % 10 == 0 else ",").join(draw.sample(six, draw.randint(1, 3)))
            for place in range(_ROWS)]


def test_a_list_mostly_on_a_later_mark_is_judged_on_it(monkeypatch: pytest.MonkeyPatch) -> None:
    """Every mark is judged: on `;` most values are `185380,928534` and no key; on `,` they are keys.

    The mutant judges the first mark that makes a list alone (6c566d3c),
    and the column is not reached.
    """
    cells = _mostly_on_commas()
    assert asking._listed_record_numbers(cells, "long_tail_labels") == (",", "wide")
    _first_mark_only(monkeypatch)
    assert asking._listed_record_numbers(cells, "long_tail_labels") == ("", "")


def _codex_grouped_lines() -> "list[str]":
    """Codex's item 1, its exact column: space-separated lists of comma-grouped keys."""
    keys = [f"{123000 + one:,}" for one in range(1, 41)]
    cells = [first + " " + second for first in keys for second in keys if first != second][:588]
    cells += [keys[0]] * 12
    return ["ids,value"] + [f'"{cell}",{place % 7}' for place, cell in enumerate(cells)]


def _texts_of(folder: pathlib.Path, name: str) -> str:
    """The description, its summary and the questions file a run wrote, as one text."""
    return "".join(
        (folder / f"{name}-{page}").read_text(encoding="utf-8")
        for page in ("profile.json", "profile.txt", "questions.json")
    )


def test_codex_grouped_keys_split_by_spaces_are_held(tmp_path: pathlib.Path) -> None:
    """Codex's item 1: `123,001 123,002` is judged on the spaces too; `123,001` is not published.

    On 6c566d3c the comma was judged first, its parts reached nothing, the
    spaces were never tried, and the profile published `123,001` on 12 rows.
    """
    keys = [f"{123000 + one:,}" for one in range(1, 41)]
    cells = [first + " " + second for first in keys for second in keys if first != second][:588]
    assert asking._listed_record_numbers(cells + [keys[0]] * 12, "long_tail_labels") == (" ", "keys")
    code, document = _profile_rows(tmp_path, "grouped", _codex_grouped_lines())
    assert code == 0
    assert _block(document, "ids")["role"] == taxonomy.ROLE_IDENTIFIER
    texts = _texts_of(tmp_path, "grouped")
    for key in keys:
        assert key not in texts and key.replace(",", "") not in texts


def test_mutant_only_the_first_mark_judged_publishes_codex_grouped_keys(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant publishes `123,001`, as 6c566d3c did."""
    _first_mark_only(monkeypatch)
    code, _document = _profile_rows(tmp_path, "grouped", _codex_grouped_lines())
    assert code == 0
    assert "123,001" in _texts_of(tmp_path, "grouped")


def test_mutant_two_list_cells_needed_publishes_the_register(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Skeptic 1's item 2: at two cells, one list cell among the keys published 40 of 40."""
    monkeypatch.setattr(asking, "_LIST_CELLS_AT_LEAST", 2)
    seen = shapes.run(tmp_path, "reglistonce6", _ROWS)
    assert seen["description_values"] > 0 and seen["twin_cells"] > 0
    with pytest.raises(AssertionError):
        _check_list_held(seen, _ROWS, "reglistonce6")


def _list_parts_before(cell: str, mark: str) -> "list[str]":
    """6c566d3c's split: a mark closing a cell leaves an empty value, so the cell is no list."""
    parts: "list[str]" = []
    for piece in cell.split(mark):
        one = piece.strip()
        if one or mark != " ":
            parts += [one]
    return parts


def _trail_lines() -> "tuple[list[str], list[str]]":
    """Skeptic 1's item 3 at 600 rows: a `;` closes each list cell; the keys and the table."""
    draw = random.Random(7)
    keys: "list[str]" = []
    while len(keys) < 40:
        one = f"{draw.randint(100000, 999999)}"
        if one not in keys:
            keys += [one]
    cells = _list_cells(keys, ";", _ROWS, seed=1)
    cells = [cell + ";" if ";" in cell else cell for cell in cells]
    lines = ["ids,test,value"] + [
        f"{cell},{('Sodium', 'Potassium', 'Glucose')[place % 3]},{(place * 37) % 140 + 3}.{place % 10}"
        for place, cell in enumerate(cells)
    ]
    return keys, lines


def test_a_mark_closing_each_list_cell_is_held(tmp_path: pathlib.Path) -> None:
    """Skeptic 1's item 3: `185380;928534;` is a list of two; 0 of 40 published at 600 rows."""
    keys, lines = _trail_lines()
    assert asking._listed_record_numbers([line.split(",")[0] for line in lines[1:]],
                                         "long_tail_labels") == (";", "wide")
    code, document = _profile_rows(tmp_path, "trail", lines)
    assert code == 0
    assert _block(document, "ids")["role"] == taxonomy.ROLE_IDENTIFIER
    texts = _texts_of(tmp_path, "trail")
    assert [key for key in keys if key in texts] == []


def test_mutant_a_closing_mark_left_as_a_value_publishes(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant (6c566d3c's split) reads the column as a long tail and publishes a record number."""
    monkeypatch.setattr(asking, "_list_parts", _list_parts_before)
    keys, lines = _trail_lines()
    code, document = _profile_rows(tmp_path, "trail", lines)
    assert code == 0
    texts = _texts_of(tmp_path, "trail")
    assert [key for key in keys if key in texts] != []


def test_brackets_quotes_and_tabs_around_a_list_are_taken_off() -> None:
    """Skeptic 1's item 6: `[185380, 928534]`, `'185380', '928534'` and a tab between are lists.

    Each published 1 of 40 at 600 rows on 6c566d3c. A `+` between values
    stays lane LISTS' (plan P4-D424).
    """
    draw = random.Random(11)
    six = [f"{draw.randint(100000, 999999)}" for _key in range(40)]
    listed = _list_cells(six, ";", _ROWS)
    bracketed = ["[" + cell.replace(";", ", ") + "]" for cell in listed]
    quoted = [", ".join("'" + one + "'" for one in cell.split(";")) for cell in listed]
    tabbed = [cell.replace(";", "\t") for cell in listed]
    assert asking._listed_record_numbers(bracketed, "long_tail_labels") == (",", "wide")
    assert asking._listed_record_numbers(quoted, "long_tail_labels") == (",", "wide")
    assert asking._listed_record_numbers(tabbed, "long_tail_labels") == (asking._ANY_MARK, "wide")
    assert asking._listed_record_numbers([cell.replace(";", "+") for cell in listed],
                                         "long_tail_labels") == ("", "")


def test_mutant_quotes_kept_reach_no_quoted_list(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: quotes left on each value, so the quoted list is not reached."""
    draw = random.Random(11)
    six = [f"{draw.randint(100000, 999999)}" for _key in range(40)]
    quoted = [", ".join("'" + one + "'" for one in cell.split(";"))
              for cell in _list_cells(six, ";", _ROWS)]
    monkeypatch.setattr(asking, "_LIST_QUOTES", "")
    assert asking._listed_record_numbers(quoted, "long_tail_labels") == ("", "")


def _amounts() -> "list[str]":
    """Codex's item 3: numbers written with a decimal comma and four decimals."""
    return ["amount,value"] + [f'"{place % 12 + 1},0{place % 30 + 1:03}",{place % 7}'
                               for place in range(_ROWS)]


def test_a_declared_decimal_comma_is_asked_nothing(tmp_path: pathlib.Path) -> None:
    """Codex's item 3: `--decimal-comma amount` settles the column; the list question is not put."""
    code, document = _profile_rows(tmp_path, "amounts", _amounts(), ["--decimal-comma", "amount"])
    assert code == 0
    assert _block(document, "amount")["role"] == taxonomy.ROLE_CONTINUOUS
    asked = json.loads((tmp_path / "amounts-questions.json").read_text(encoding="utf-8"))["asked"]
    assert [entry for entry in asked if entry["column"] == "amount"] == []


def test_mutant_the_declaration_unread_asks_the_list_question(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: the declared columns not handed to the list rule, so it asks."""
    real = asking.listed_record_number_questions

    def unread(*named: object, **said: object) -> "list[asking.Question]":
        return real(*named[:6])

    monkeypatch.setattr(asking, "listed_record_number_questions", unread)
    code, _document = _profile_rows(tmp_path, "amounts", _amounts(), ["--decimal-comma", "amount"])
    assert code == 0
    asked = json.loads((tmp_path / "amounts-questions.json").read_text(encoding="utf-8"))["asked"]
    assert [entry["column"] for entry in asked] == ["amount"]


def test_keep_says_what_a_column_read_as_numbers_publishes(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Codex's item 3: `keep` on a column read as numbers names its statistics, not its values."""
    for role in asking.NUMERIC_ROLES:
        kept = asking._listed_choices(role, 11)[0]
        assert kept.answer == asking.ANSWER_KEEP
        assert kept.publishes == "what it publishes now: " + asking._publishes_under(
            asking.ANSWER_MEASUREMENT, role, 11)
    labels = asking._listed_choices(taxonomy.ROLE_LONG_TAIL, 11)[0]
    assert labels.publishes == asking._publishes_under(asking.ANSWER_KEEP, taxonomy.ROLE_LONG_TAIL, 11)
    monkeypatch.setattr(asking, "NUMERIC_ROLES", ())
    assert asking._listed_choices(taxonomy.ROLE_COUNT, 11)[0].publishes.startswith(
        "what it publishes now: every value")


def _names_every_character(said: str) -> bool:
    """Whether the wide sentence names each kind of character `parsing.is_code_text` admits."""
    for character, word in (("A", "letters"), ("7", "figures"), ("-", "hyphens"),
                            ("_", "underscores")):
        assert asking.parsing.is_code_text(character)
        if word not in said:
            return False
    return True


def test_the_shape_sentence_names_every_character_the_rule_reads() -> None:
    """Codex's item 4: `R_123456` is reached, and the sentence names underscores."""
    draw = random.Random(11)
    keys = [f"R_{draw.randint(100000, 999999)}" for _key in range(40)]
    assert asking._listed_record_numbers(_list_cells(keys, ";", _ROWS), "long_tail_labels") == (
        ";", "wide")
    assert _names_every_character(asking._LISTED_SAID[asking._LISTED_WIDE])


def test_mutant_the_sentence_without_underscores_is_seen() -> None:
    """The mutant: 6c566d3c's sentence, letters, figures and hyphens alone."""
    assert not _names_every_character(
        "every part is written in letters, figures and hyphens, with a run "
        "of five figures or more"
    )


def test_the_list_question_stands_beside_the_dates_question_as_hxs_does(
    tmp_path: pathlib.Path,
) -> None:
    """Codex's item 2, measured: ONE question offering `identifier`; Q6 beside it as beside HX's.

    598 cells of `2024001` to `2024030` and two of `2024001;2024002`: the
    list question and question Q6 (`keep` or `dates`), as the same column
    without its list cells is put P4-D401's width question and Q6. Q6
    asks whether the column holds dates; it holds nothing (P4-D401), and
    its family is kept apart by the questions file (P4-D408).
    """
    plain = ["days,value"] + [f"{2024001 + place % 30},{place % 7}" for place in range(_ROWS)]
    listed = plain[: _ROWS - 1] + ["2024001;2024002,1", "2024001;2024002,2"]
    families: "list[list[list[str]]]" = []
    for name, lines in (("plain", plain), ("listed", listed)):
        folder = tmp_path / name
        folder.mkdir()
        code, document = _profile_rows(folder, name, lines)
        assert code == 0
        assert _block(document, "days")["role"] == taxonomy.ROLE_IDENTIFIER
        asked = json.loads((folder / f"{name}-questions.json").read_text(encoding="utf-8"))["asked"]
        offered = [[choice["answer"] for choice in entry["answers_you_can_give"]]
                   for entry in asked if entry["column"] == "days"]
        assert len([one for one in offered if asking.ANSWER_IDENTIFIER in one]) == 1
        families += [[one for one in offered if asking.ANSWER_IDENTIFIER not in one]]
    assert families[0] == families[1] == [[asking.ANSWER_KEEP, asking.ANSWER_DATES]]


# -- the orchestrator's addendum (2026-10-22 18:23): one ordinary word ------


def _codex_other_cells() -> "list[str]":
    """Codex's case from its third round on lane ZR-a's page, exactly as the addendum gives it.

    `R100000` to `R100039`: 40 single cells, 240 cyclic pairs (i, i+s) for s
    of 1 to 6 and 320 cyclic triples (i, i+s, i+s+1) for s of 1 to 8, the
    indices modulo 40; the first cell closes `;OTHER`.
    """
    keys = [f"R{100000 + one}" for one in range(40)]
    cells = [keys[one] for one in range(40)]
    cells += [f"{keys[one]};{keys[(one + step) % 40]}" for step in range(1, 7) for one in range(40)]
    cells += [f"{keys[one]};{keys[(one + step) % 40]};{keys[(one + step + 1) % 40]}"
              for step in range(1, 9) for one in range(40)]
    cells[0] = cells[0] + ";OTHER"
    assert len(cells) == _ROWS
    return cells


def test_one_ordinary_word_does_not_undo_the_list_hold(tmp_path: pathlib.Path) -> None:
    """Codex's case at 600 rows: the list question is put, and 0 of the 40 record numbers published."""
    cells = _codex_other_cells()
    assert asking._listed_record_numbers(cells, "long_tail_labels") == (";", "wide")
    lines = ["ids,value"] + [f"{cell},{place % 7}" for place, cell in enumerate(cells)]
    code, _document = _profile_rows(tmp_path, "other", lines)
    assert code == 0
    asked = json.loads((tmp_path / "other-questions.json").read_text(encoding="utf-8"))["asked"]
    offered = [[choice["answer"] for choice in entry["answers_you_can_give"]]
               for entry in asked if entry["column"] == "ids"]
    assert offered == [_LIST_ANSWERS]
    texts = _texts_of(tmp_path, "other")
    assert [one for one in range(40) if f"{100000 + one}" in texts] == []


def test_mutant_every_value_wide_lets_one_word_undo_the_hold(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The mutant: every value must be wide (6c566d3c's arm), so `OTHER` leaves the list unasked.

    Since lane HX4's repair 2, route two sets aside one value in three too
    (the orchestrator's addendum 2), and reaches `R100000` to `R100039`
    as codes repeating: either arm alone holds Codex's case, so the
    mutant takes both all-or-nothing, and the wide arm alone is seen
    giving way to route two.
    """
    monkeypatch.setattr(asking, "_LIST_NO_KEY_SHARE", 10**9)
    assert asking._listed_record_numbers(_codex_other_cells(), "long_tail_labels") == (";", "codes")
    monkeypatch.setattr(asking, "_LIST_ROUTE_SHARE", 10**9)
    assert asking._listed_record_numbers(_codex_other_cells(), "long_tail_labels") == ("", "")


# -- lane HX4's repair 2: one value a cell, a key and a word, line breaks ----


def _one_a_cell(form: str) -> "list[str]":
    """600 cells of one record number of 40 each, written in ``form`` (`{}` for the number)."""
    draw = random.Random(17)
    six = [f"{draw.randint(100000, 999999)}" for _key in range(40)]
    return [form.format(six[place % 40]) for place in range(_ROWS)]


# Item 1 of lane HX4's verify on 5cd84df6: each published 40 of 40 at 600 and
# 20,000 rows, every twin cell a real one; the mark the rule names.
_ONE_A_CELL = (("{};", ";"), ("R{};", ";"), ("{},", ","), ("[{}]", ";"), ("[R{}]", ";"),
               ("'{}'", ";"), ("'{}", ";"), ('"{}"', ";"), ("['{}']", ";"))


def test_one_record_number_wrapped_as_a_list_is_reached() -> None:
    """`185380;`, `185380,`, `[185380]`, `'185380'` and the `R` forms are lists; bare keys are not."""
    for form, mark in _ONE_A_CELL:
        assert asking._listed_record_numbers(_one_a_cell(form), "categorical") == (mark, "wide"), form
    # A bare key, a cell of one bracket or quote alone, and words in quotes are not.
    assert asking._listed_record_numbers(_one_a_cell("{}"), "categorical") == ("", "")
    assert asking._listed_record_numbers(["[]", "''", "'"] * 200, "categorical") == ("", "")
    assert asking._listed_record_numbers(["'Yes'", "'No'"] * 300, "categorical") == ("", "")


def _two_values_a_list_cell(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: 5cd84df6's rule, a list cell holds two values or more."""
    monkeypatch.setattr(asking, "_a_list_cell", lambda cell, parts: len(parts) >= 2)


def test_mutant_one_value_no_list_reaches_no_wrapped_record_number(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The mutant reaches none of the wrapped forms."""
    _two_values_a_list_cell(monkeypatch)
    for form, _mark in _ONE_A_CELL:
        assert asking._listed_record_numbers(_one_a_cell(form), "categorical") == ("", ""), form


def test_mutant_one_value_no_list_publishes_every_record_number(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant publishes the record numbers of `185380;` a cell, as 5cd84df6 did (40 of 40)."""
    _two_values_a_list_cell(monkeypatch)
    seen = shapes.run(tmp_path, "reglistone6", _ROWS)
    assert seen["description_values"] > 0 and seen["twin_cells"] > 0
    with pytest.raises(AssertionError):
        _check_list_held(seen, _ROWS, "reglistone6")


def test_a_key_and_a_word_in_every_cell_is_reached() -> None:
    """Item 2: `185380;pending` and `R185380;done` are one value in two record numbers."""
    draw = random.Random(19)
    six = [f"{draw.randint(100000, 999999)}" for _key in range(40)]
    worded = [f"{six[place % 40]};pending" for place in range(_ROWS)]
    lettered = [f"R{six[place % 40]};{('pending', 'done', 'open')[place % 3]}" for place in range(_ROWS)]
    for cells in (worded, lettered):
        assert asking._listed_record_numbers(cells, "categorical") == (";", "wide")
    # Words beside one key in two cells are more than one value in two: no list of record numbers.
    sparse = [f"{six[place % 40]};{'pending'};{'done'}" for place in range(_ROWS)]
    assert asking._listed_record_numbers(sparse, "categorical") == ("", "")


def test_mutant_one_in_three_lets_a_word_a_cell_publish(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The mutant: repair 1's share (one value in three), so `185380;pending` publishes record numbers."""
    monkeypatch.setattr(asking, "_LIST_NO_KEY_SHARE", 3)
    seen = shapes.run(tmp_path, "reglistword6", _ROWS)
    assert seen["description_values"] > 0 and seen["twin_cells"] > 0
    with pytest.raises(AssertionError):
        _check_list_held(seen, _ROWS, "reglistword6")


def _broken(between: str) -> "list[str]":
    draw = random.Random(23)
    six = [f"{draw.randint(100000, 999999)}" for _key in range(40)]
    return _list_cells(six, between, _ROWS)


def test_a_line_break_or_a_no_break_space_between_values_is_a_space() -> None:
    """Item 3: six-figure lists on a line break or a no-break space are lists (1 of 40 published on 5cd84df6).

    A `/`, a `.` or a doubled `;;` between values stays lane LISTS' (plan P4-D424).
    """
    for between in ("\n", "\r\n", "\u00a0"):
        assert asking._listed_record_numbers(_broken(between), "long_tail_labels") == (
            asking._ANY_MARK, "wide"), repr(between)
    for between in ("/", ".", ";;"):
        assert asking._listed_record_numbers(_broken(between), "long_tail_labels") == ("", "")


def test_mutant_a_line_break_read_as_no_mark_reaches_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """The mutant: a tab alone read as a space (5cd84df6), so the broken lists are not reached."""
    monkeypatch.setattr(asking, "_READ_AS_SPACE", "\t")
    for between in ("\n", "\u00a0"):
        assert asking._listed_record_numbers(_broken(between), "long_tail_labels") == ("", "")


# The orchestrator's addenda 2 (2026-10-22 21:32, from lane ZR-a's verify 3)
# and 3 (2026-10-23 07:20, from its close 4): Codex's construction on keys
# the wide arm, route two and the padded route reach, pure and with `;OTHER`
# closing the first cell, at 600 AND 20,000 rows (the 600 cells repeating
# in order). At 20,000 rows today's product (98c0fce6) published 40 of 40
# keys of every shape as whole-cell categorical levels, and 5cd84df6 those
# of the three `;OTHER` shapes below five figures; the reason each is
# reached by.
_ROUTE_KEYS = (("R{}", 100000, "wide"), ("R{}", 1000, "codes"), ("AB{}", 100, "codes"),
               ("0{}", 100, "padded"))


def _codex_route_cells(form: str, first: int, rows: int, other: bool) -> "tuple[list[str], list[str]]":
    """The keys and Codex's cells: 40 singles, 240 cyclic pairs s = 1..6, 320 cyclic triples s = 1..8."""
    keys = [form.format(first + one) for one in range(40)]
    cells = [keys[one] for one in range(40)]
    cells += [f"{keys[one]};{keys[(one + step) % 40]}" for step in range(1, 7) for one in range(40)]
    cells += [f"{keys[one]};{keys[(one + step) % 40]};{keys[(one + step + 1) % 40]}"
              for step in range(1, 9) for one in range(40)]
    assert len(cells) == _ROWS
    cells = [cells[place % _ROWS] for place in range(rows)]
    if other:
        cells[0] = cells[0] + ";OTHER"
    return keys, cells


def _keys_found(keys: "list[str]", text: str) -> "list[str]":
    """The keys standing in a text as a whole token (not inside a longer run of letters and figures)."""
    return [key for key in keys if re.search(rf"(?<![0-9A-Za-z]){key}(?![0-9A-Za-z])", text)]


@pytest.mark.parametrize("rows", (_ROWS, 20000))
@pytest.mark.parametrize("other", (False, True))
@pytest.mark.parametrize(("form", "first", "why"), _ROUTE_KEYS)
def test_one_word_undoes_no_route_of_the_list_hold(
    tmp_path: pathlib.Path, form: str, first: int, why: str, other: bool, rows: int
) -> None:
    """Every key form, pure or with `;OTHER`: the list question is put, 0 keys in any file or twin cell."""
    keys, cells = _codex_route_cells(form, first, rows, other)
    assert asking._listed_record_numbers(cells, "free_text") == (";", why)
    lines = ["ids,value"] + [f"{cell},{place % 7}" for place, cell in enumerate(cells)]
    code, _document = _profile_rows(tmp_path, "route", lines)
    assert code == 0
    asked = json.loads((tmp_path / "route-questions.json").read_text(encoding="utf-8"))["asked"]
    offered = [[choice["answer"] for choice in entry["answers_you_can_give"]]
               for entry in asked if entry["column"] == "ids"]
    assert offered == [_LIST_ANSWERS]
    assert _keys_found(keys, _texts_of(tmp_path, "route")) == []
    with shapes.nobody_at_the_keyboard():
        assert cli.main(["generate", f"{tmp_path / 'route-profile.json'}", "--out-dir",
                         f"{tmp_path}", "--seed", "0", "--replace"]) == 0
    twin = (tmp_path / "route-twin.csv").read_text(encoding="utf-8")
    assert _keys_found(keys, twin) == []


@pytest.mark.parametrize("other", (False, True))
@pytest.mark.parametrize(("form", "first", "why"), _ROUTE_KEYS)
def test_mutant_all_or_nothing_routes_let_one_word_undo_the_hold(
    monkeypatch: pytest.MonkeyPatch, form: str, first: int, why: str, other: bool
) -> None:
    """The mutant: every route all-or-nothing (5cd84df6's routes, every value wide), so `;OTHER` reaches nothing.

    Pure, the mutant still reaches each shape: the word is what it lets undo the hold.
    """
    monkeypatch.setattr(asking, "_LIST_ROUTE_SHARE", 10**9)
    monkeypatch.setattr(asking, "_LIST_NO_KEY_SHARE", 10**9)
    for rows in (_ROWS, 20000):
        _keys, cells = _codex_route_cells(form, first, rows, other)
        found = asking._listed_record_numbers(cells, "free_text")
        assert found == (("", "") if other else (";", why)), (rows, found)


@pytest.mark.parametrize(("form", "first", "why"), _ROUTE_KEYS[1:])
def test_mutant_all_or_nothing_routes_publish_every_key_at_20000_rows(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, form: str, first: int, why: str
) -> None:
    """The mutant at the owner's floor size: `;OTHER` read as categories, the keys published (40 of 40 on 5cd84df6)."""
    monkeypatch.setattr(asking, "_LIST_ROUTE_SHARE", 10**9)
    keys, cells = _codex_route_cells(form, first, 20000, True)
    lines = ["ids,value"] + [f"{cell},{place % 7}" for place, cell in enumerate(cells)]
    code, _document = _profile_rows(tmp_path, "route", lines)
    assert code == 0
    assert _keys_found(keys, _texts_of(tmp_path, "route")) != []
