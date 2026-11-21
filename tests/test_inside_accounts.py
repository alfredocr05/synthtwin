"""Gate file of lane W5-ACC: the invented accounts table (the battery's T7) twinned end to end at the table floor.

THE TABLE. T7 holds 20,000 accounts naming their patient (11,091 patients at
seed 1), a guarantor shared by several accounts (5,873 guarantors), a
subscriber who is the patient exactly where the relationship is `Self`,
and the member of staff who registered the account (40 of them), beside
a plan, a balance and the day the account was opened.

WHY IT WAS NEVER TWINNED. The battery read the person question every
shipped run puts ("identifies the person", beside `record`) as a record
number's question and answered `identifier` there for the guarantor's and
the staff member's keys, which says that each names the person the rows
are about. Profile then counted the people as the rows sharing a value of
EITHER key (plan P4-D479: two columns said to name the person count as
their union), the 40 staff numbers joined every row into one person, and
the owner's table floor refused the table as "1 person". The floor read
what it was told; the answers were wrong. Answered as the person who holds
the table answers -- `keep` at the person question for every key but the
patient's, then `identifier` when each is asked as record numbers -- the
people are counted by the patient key alone, and the table is above the
floor by every count.

THE FLOOR IS UNCHANGED (the owner, 2026-10-22 and 2026-11-04; plan
P4-D425): 20,000 rows that hold a value and, where one person has several
rows, 1,000 people. Every command here runs with the floor on (the
command's own `small_tables_refused=True`), the five checks with theirs.

WHAT IT HOLDS (each clause red on its mutant):

* At 20,000 rows the shipped commands twin the table: profile with the
  truthful answers, generate (the inside record written, the twin drawn
  from it), validate exit 0, and the five checks PASS with the people
  counted by the patient key (mutant: the person question read in its
  first wording alone, and profile refuses the table).
* One row under the row floor the same table is refused, nothing written
  (mutant: the floor's row clause off).
* At 20,000 rows over 999 patients the table is refused at the people
  floor (mutant: the floor's people clause off).
* Answers that say both other keys name the person still refuse the table,
  counted as one person by the two keys together: no table is accepted on
  a count the floor reads under it (mutant: the floor's people clause off).
"""

from __future__ import annotations

import contextlib
import csv
import io
import pathlib

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, installation, parsing, twin_checks

TABLE = "T7"
FILE = T.FILES[TABLE]
PERSON = T.PERSON[TABLE]
# The keys of other people the person question is put about: the guarantor's and the staff member's, the record
# numbers beside the patient's whose values stand on two rows or more each on average (the account's own key and
# the subscriber's stand on fewer and are asked as record numbers alone).
OTHER_PEOPLE = (T.T7_COLUMNS[2], T.T7_COLUMNS[5])
HEAD = "THIS TWIN WAS DRAWN FROM THE INSIDE RECORD"
FLOOR_WORDS = "synthtwin makes twins of large tables only, and this table is below its floor."


def _places(folder: pathlib.Path) -> inside.Places:
    """The run's own installation's private folder, as `reliability_battery.installed` makes it."""
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


def _rows(text: str) -> "list[dict[str, str]]":
    return list(csv.DictReader(io.StringIO(text)))


def _command(folder: pathlib.Path, argv: "list[str]") -> "tuple[int, str]":
    """One command with the floor on, as a person types it: its exit code and everything it said."""
    said = io.StringIO()
    with B.installed(folder), contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(argv, small_tables_refused=True)
    return int(code), said.getvalue()


def _described(folder: pathlib.Path, text: str) -> "tuple[int, str]":
    """Route S's rounds (`reliability_battery.make_twins`) with the floor on, the last command's screen kept whole."""
    source = pathlib.Path(folder, "table", FILE)
    out = pathlib.Path(folder, "out")
    source.parent.mkdir(parents=True, exist_ok=True)
    out.mkdir(parents=True, exist_ok=True)
    source.write_text(text, encoding="utf-8", newline="\n")
    questions = out / f"{source.stem}-questions.json"
    code, said = _command(folder, ["profile", f"{source}", "--out-dir", f"{out}", "--replace"])
    for _round in range(B.ROUNDS):
        if code != 0:
            break
        written, _left = B.answer_questions(questions, TABLE)
        if not written:
            break
        again = ["profile", f"{source}", "--out-dir", f"{out}", "--answers", f"{questions}"]
        code, said = _command(folder, again)
        if code != 0:
            code, said = _command(folder, again + ["--replace-description"])
    return code, said


def _folded(text: str, people: int) -> str:
    """The accounts table with its patients folded onto ``people`` invented keys; a `Self` row's subscriber stays its patient."""
    lines = text.split("\n")
    header = lines[0].split(",")
    key, subscriber, relationship = header.index(PERSON), header.index("subscriber_id"), header.index("relationship")
    keys: "dict[str, str]" = {}
    out = [lines[0]]
    for line in lines[1:]:
        if not line:
            continue
        cells = line.split(",")
        if cells[key] not in keys:
            keys[cells[key]] = f"P{1000000 + len(keys) % people}"
        cells[key] = keys[cells[key]]
        if cells[relationship] == "Self":
            cells[subscriber] = cells[key]
        out += [",".join(cells)]
    return "\n".join(out) + "\n"


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "tuple[pathlib.Path, str, B.Product]":
    """The accounts table at the table floor, twinned by route S with the floor on (the battery's own route)."""
    folder = tmp_path_factory.mktemp("inside-accounts") / "product"
    text = T.text(TABLE, parsing.TABLE_ROW_FLOOR, 1)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        product = B.make_twins(folder, TABLE, text, (0,), False)
    return folder, text, product


def test_the_accounts_table_is_twinned_end_to_end_at_the_floor(made, tmp_path: pathlib.Path) -> None:  # type: ignore[no-untyped-def]
    folder, text, product = made
    assert not product.errors, product.errors
    for column in OTHER_PEOPLE:
        # Asked first whether it names the person (no), then as record numbers (yes): held, joining nobody.
        assert f"{column}=keep" in product.answered and f"{column}=identifier" in product.answered, product.answered
    records = sorted(_places(folder).private.glob(f"*{inside.SUFFIX}"))
    assert len(records) == 1 and inside.carries_marker(records[0])
    report = pathlib.Path(folder, "out", f"{pathlib.Path(FILE).stem}-twin-report.txt").read_text(encoding="utf-8")
    assert report.startswith(HEAD)
    description = pathlib.Path(folder, "out", f"{pathlib.Path(FILE).stem}-profile.json")
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        code, said = _command(folder, ["validate", f"{description}", "--replace"])
    assert code == 0, said[-2000:]
    real = pathlib.Path(tmp_path, FILE)
    twin = pathlib.Path(tmp_path, f"{real.stem}-twin.csv")
    real.write_text(text, encoding="utf-8", newline="\n")
    twin.write_text(product.twins[0], encoding="utf-8", newline="\n")
    outcome = twin_checks.run_checks(f"{real}", f"{twin}", person=PERSON)
    assert outcome.passed, [(check.code, check.lines) for check in outcome.checks if not check.passed]
    people = len({row[PERSON] for row in _rows(text)})
    assert people >= parsing.TABLE_PEOPLE_FLOOR
    assert (outcome.person_column, outcome.real_rows, outcome.real_people) == (PERSON, parsing.TABLE_ROW_FLOOR, people)
    assert len(_rows(product.twins[0])) == parsing.TABLE_ROW_FLOOR


def test_one_row_under_the_row_floor_the_accounts_table_is_refused(tmp_path: pathlib.Path) -> None:
    folder = tmp_path / "product"
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        code, said = _described(folder, T.text(TABLE, parsing.TABLE_ROW_FLOOR - 1, 1))
    assert code == 1, said[-2000:]
    assert FLOOR_WORDS in said and f"{parsing.TABLE_ROW_FLOOR - 1:,} rows that hold a value" in said
    assert sorted(path.name for path in pathlib.Path(folder, "out").iterdir()) == []


def test_an_accounts_table_of_fewer_than_a_thousand_patients_is_refused(tmp_path: pathlib.Path) -> None:
    folder = tmp_path / "product"
    people = parsing.TABLE_PEOPLE_FLOOR - 1
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        code, said = _described(folder, _folded(T.text(TABLE, parsing.TABLE_ROW_FLOOR, 1), people))
    assert code == 1, said[-2000:]
    assert FLOOR_WORDS in said and f"{people:,} people, counted by '{PERSON}'" in said, said[-2000:]
    assert not pathlib.Path(folder, "out", f"{pathlib.Path(FILE).stem}-twin.csv").exists()


def test_answers_saying_both_other_keys_name_the_person_still_refuse_it(tmp_path: pathlib.Path,
                                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    folder = tmp_path / "product"
    truthful = B.truthful

    def said_to_be_the_person(table: str, column: str, choices: "list[str]", people: bool) -> str:
        if column in OTHER_PEOPLE and people and "identifier" in choices:
            return "identifier"
        return truthful(table, column, choices, people)

    monkeypatch.setattr(B, "truthful", said_to_be_the_person)
    monkeypatch.setattr(inside, "default_places", lambda: _places(folder))
    code, said = _described(folder, T.text(TABLE, parsing.TABLE_ROW_FLOOR, 1))
    assert code == 1, said[-2000:]
    assert FLOOR_WORDS in said, said[-2000:]
    assert f"1 person, counted by '{OTHER_PEOPLE[0]} and {OTHER_PEOPLE[1]}'" in said, said[-2000:]
