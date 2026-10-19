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
    before any question is worked out, and each of these values is one
    person's, so the column is described blank -- its cells counted with
    the blanks -- and route three's question, which no answer could turn
    into a published value, is not put.
    """
    seen = shapes.run(tmp_path, kind, _ROWS)
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    assert seen["validate_exit"] == 0, seen
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    assert seen["role"] == taxonomy.ROLE_EMPTY
    assert seen["forced_identifiers"] == ["patient"]
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
