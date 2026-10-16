"""P4-D401 (lane HX): no real identifier is published while its question is open.

THE FINDING (wave6/ZOO/CRITIC.md item 1, measured at 68dae22f). A long
table -- 600 rows over 44 patients, `mrn` written `MRN1000xxxx` on each
patient's rows -- profiled with the person question offered and nobody
answering: `mrn` was read as labels and the description named 26 of the 44
real record numbers, every one on 11 rows or more, and the twin wrote them
back. The owner's principle (2026-10-01): the one threat is HIPAA exposure,
and a record number is a direct identifier whatever its count.

THE RULE, in the owner's pattern of 2026-09-17 (ruling 8: "do not guess,
ask"). A column a question offering `identifier` was put to -- the person
question, a question asked because every value is the same number of
figures, or the two-numbers question of a column written as telephone or
social security numbers -- and that nobody answered is described as record
numbers until it is answered: no level name, prefix, rung or example, and
the twin writes made-up record numbers there. The question is still asked.
Any answer gives back what that answer describes, byte for byte, and a
table where no such question is put is described as before.

THE GATE, one case per shape at 600 rows (20,000 rows through
`tools/measurements/kpi_run.py --slow`, ledger K-S3-64): 0 real values and
0 fragments in the description, the summary and the questions file, 0 in
the twin, and the question still asked. The three shapes no question flags
-- a patient's name, a street address, a full birth date -- are STATED
LIMITS owned by lane CODES-2's allowlist, each pinned below as a strict
expected failure that turns red the day it closes.
"""

from __future__ import annotations

import json
import pathlib

import pytest

from synthtwin import asking, cli, profile, reading, taxonomy

import unanswered_identifier_shapes as shapes

_ROWS = 600


@pytest.mark.parametrize("kind", shapes.HELD)
def test_an_unanswered_identifier_publishes_nothing_real(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """0 real values or fragments in the description and the twin; still asked."""
    seen = shapes.run(tmp_path, kind, _ROWS)
    assert seen["profile_exit"] == 0 and seen["generate_exit"] == 0
    assert seen["description_values"] == 0, seen
    assert seen["description_fragments"] == 0, seen
    assert seen["twin_cells"] == 0, seen
    assert seen["twin_fragments"] == 0, seen
    # THE QUESTION IS STILL ASKED, `identifier` among its answers, and the
    # file says what leaving it blank keeps.
    assert seen["asked"] and asking.ANSWER_IDENTIFIER in seen["asked"][0]
    assert seen["read_as_now"] == [asking.ANSWER_IDENTIFIER]
    # Described as record numbers, saying nobody answered, and the
    # population still counted as it was.
    assert seen["role"] == taxonomy.ROLE_IDENTIFIER
    assert seen["evidence"] == taxonomy.rendered(
        taxonomy.EVIDENCE_UNANSWERED_IDENTITY, ()
    )
    assert seen["forced_identifiers"] == [kind]
    assert seen["person_columns"] == []
    assert "COLUMNS HELD BACK UNTIL YOU ANSWER" in f"{seen['screen']}"


@pytest.mark.parametrize("kind", shapes.STATED)
@pytest.mark.xfail(
    strict=True,
    reason=(
        "STATED LIMIT owned by lane CODES-2's allowlist (P4-D401): no "
        "question flags a name, a street address or a birth date, and no "
        "general rule reaches them without hiding columns that identify "
        "nobody"
    ),
)
def test_a_shape_no_question_flags_is_a_stated_limit(
    tmp_path: pathlib.Path, kind: str
) -> None:
    """Strict: it fails while the limit stands, and turns red when it closes."""
    seen = shapes.run(tmp_path, kind, _ROWS)
    assert seen["description_values"] == 0 and seen["twin_cells"] == 0


def _answer(folder: pathlib.Path, kind: str, answer: str) -> "dict[str, object]":
    """Answer the column's question in the file the run wrote, and run again."""
    questions = folder / f"{kind}_long-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        if entry["column"] == kind:
            entry["your_answer"] = answer
    answers = folder / "answers.json"
    answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    table = folder / f"{kind}_long.csv"
    code = cli.main(["profile", f"{table}", "--out-dir", f"{folder}",
                     "--replace", "--answers", f"{answers}"])
    assert code == 0
    return json.loads(
        (folder / f"{kind}_long-profile.json").read_text(encoding="utf-8")
    )


def _block(document: "dict[str, object]", name: str) -> "dict[str, object]":
    columns = document["columns"]
    assert isinstance(columns, list)
    return [one for one in columns if one["name"] == name][0]


def test_answering_keep_gives_back_the_labels(tmp_path: pathlib.Path) -> None:
    """`keep` is the reading the rules made: the levels are back, named."""
    shapes.run(tmp_path, "mrn", _ROWS)
    document = _answer(tmp_path, "mrn", asking.ANSWER_KEEP)
    block = _block(document, "mrn")
    assert block["role"] == taxonomy.ROLE_CATEGORICAL
    assert block["levels"], "the answer `keep` publishes the levels it names"
    settings = document["settings"]
    assert isinstance(settings, dict) and settings["forced_identifiers"] == []
    # ...and the file asks again under the reading in force, as before.
    asked = json.loads(
        (tmp_path / "mrn_long-questions.json").read_text(encoding="utf-8")
    )["asked"]
    assert [entry["read_as_now"] for entry in asked if entry["column"] == "mrn"] == [
        asking.ANSWER_KEEP
    ]


def test_answering_code_on_the_fixed_width_question_gives_back_the_codes(
    tmp_path: pathlib.Path,
) -> None:
    """`code` declares the column a code, and its values are published so."""
    shapes.run(tmp_path, "account", _ROWS)
    document = _answer(tmp_path, "account", asking.ANSWER_CODE)
    block = _block(document, "account")
    assert block["role"] != taxonomy.ROLE_IDENTIFIER
    settings = document["settings"]
    assert isinstance(settings, dict)
    assert settings["forced_codes"] == ["account"]
    assert settings["forced_identifiers"] == []


def test_answering_identifier_counts_the_people(tmp_path: pathlib.Path) -> None:
    """`identifier` is the declaration: 44 people is under the floor, refused."""
    shapes.run(tmp_path, "mrn", _ROWS)
    questions = tmp_path / "mrn_long-questions.json"
    document = json.loads(questions.read_text(encoding="utf-8"))
    for entry in document["asked"]:
        entry["your_answer"] = asking.ANSWER_IDENTIFIER
    answers = tmp_path / "answers.json"
    answers.write_text(json.dumps(document), encoding="utf-8", newline="\n")
    code = cli.main(["profile", f"{tmp_path / 'mrn_long.csv'}", "--out-dir",
                     f"{tmp_path / 'again'}", "--answers", f"{answers}"])
    assert code == 1, "44 people is under the population floor"


def test_a_person_at_the_keyboard_has_answered(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Enter at the keyboard is an answer: the reading it keeps is published."""
    monkeypatch.setattr(cli, "_there_is_somebody_to_ask", lambda: True)
    monkeypatch.setattr(cli, "_read_one_answer", lambda standing: "")
    table, _real = shapes.write_table(tmp_path, "mrn", _ROWS)
    assert cli.main(["profile", f"{table}", "--out-dir", f"{tmp_path}"]) == 0
    document = json.loads(
        (tmp_path / "mrn_long-profile.json").read_text(encoding="utf-8")
    )
    assert _block(document, "mrn")["role"] == taxonomy.ROLE_CATEGORICAL


def test_no_column_held_back_describes_the_table_as_before(
    tmp_path: pathlib.Path,
) -> None:
    """`unanswered` empty or absent is the same description, byte for byte."""
    table, _real = shapes.write_table(tmp_path, "mrn", _ROWS)
    settings = taxonomy.Settings()
    read = reading.read_table(
        f"{table}", small_cell_floor=settings.small_cell_floor
    )
    before = profile.serialize(profile.build_document(read, settings, []))
    again = profile.serialize(
        profile.build_document(read, settings, [], unanswered=[])
    )
    assert before == again


def test_the_two_data_rules_name_no_blood_pressure_code_or_date() -> None:
    """The e-mail route and the telephone layouts, against their neighbours."""
    assert asking._a_register_of_addresses(["a.b@host.org", "c@d.co"])
    assert not asking._a_register_of_addresses(["a.b@host.org", "nobody"])
    assert not asking._a_register_of_addresses(["a@b", "x@y.z w"])
    assert asking._telephone_or_social_security(["319-555-1234", "123-45-6789"])
    for neighbour in (["120/80"], ["12345-6789-01"], ["2024-01-05"], ["1:2:3"],
                      ["(319) 555-12345"]):
        assert not asking._telephone_or_social_security(neighbour)
