"""The twin checks' first run reads the person's answers beside the real table (lane ZOO-Y, plan P4-D517).

A claims table writes a place code: two figures of a public list of
settings of care, in a column whose name reads as a place. The checks
read a column named as a place as an identifier (`twin_checks._kind_of`),
so C4 counted each twin code -- every one a published code -- as a
copied identifier. MEASURED (lane ZOO-X's
data-type zoo, 20,000 rows): the checks run as a first run types them
failed on the codes table for that column alone, and passed once the
person typed `--not-identifier`. The person HAD answered, in the
questions file `synthtwin profile` wrote beside the table: `code`.

So a run given no plan reads that file (`place_names_answered`): a
column named as a place, answered `code`, `measurement` or `no`, and
never `identifier` or `yes`, is no identifier. A column answered `yes`
stays one, and with no file every column is read as before. The tables
are invented and drawn from their seeds here, about 3,000 rows (below
the floor, read with the checks' internal switch off).
"""

from __future__ import annotations

import csv
import json
import pathlib
import random

import pytest

from synthtwin import twin_checks

HEADER = ["patient_id", "place_code", "lab_value"]
CODES = ("11", "21", "22", "23", "02", "12", "31", "81", "19", "20")


def _claims(seed: int, prefix: str) -> "list[list[str]]":
    rng = random.Random(seed)
    rows: "list[list[str]]" = []
    for person in range(500):
        for _visit in range(rng.randint(5, 8)):
            rows += [[f"{prefix}{person:06d}", rng.choice(CODES), f"{rng.gauss(5.0, 1.2):.2f}"]]
    return rows


def _write(path: pathlib.Path, rows: "list[list[str]]") -> str:
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(HEADER)
        writer.writerows(rows)
    return f"{path}"


# What each answer's question offers, as `synthtwin profile` writes it: the reading's two, and Safe Harbor's two.
_OFFERED = {"code": ("code", "measurement"), "measurement": ("code", "measurement"), "identifier": ("identifier", "keep"),
            "no": ("no", "yes"), "yes": ("no", "yes")}


def _answered(folder: pathlib.Path, answers: "list[tuple[str, str]]", table: str = "claims.csv") -> None:
    """A questions file beside the real table, in synthtwin's own shape, naming ``table`` (no value of the table)."""
    entries = [{"column": column, "your_answer": answer,
                "answers_you_can_give": [{"answer": offered} for offered in _OFFERED[answer]]}
               for column, answer in answers]
    document = {"table": table, "about_your_file": [], "asked": entries, "checklist": {"columns": []}}
    (folder / "claims-questions.json").write_text(json.dumps(document, indent=2), encoding="utf-8", newline="\n")


def _c4(folder: pathlib.Path) -> bool:
    real = _write(folder / "claims.csv", _claims(1, "P"))
    twin = _write(folder / "claims-twin.csv", _claims(2, "T"))
    outcome = twin_checks.run_checks(real, twin, small_tables_refused=False)
    return {check.code: check.passed for check in outcome.checks}["C4"]


def test_a_place_named_column_answered_a_code_is_no_identifier(tmp_path: pathlib.Path) -> None:
    """Answered `code` in the questions file: C4 passes; with no file, as before, it fails on the codes."""
    assert not _c4(tmp_path), "premise: read by its name, the column's codes are counted as copied identifiers"
    _answered(tmp_path, [("place_code", "code"), ("place_code", "no")])
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ("place_code",)
    assert _c4(tmp_path)


def test_a_place_answered_yes_stays_an_identifier(tmp_path: pathlib.Path) -> None:
    """Answered `code`, then `yes` to its Safe Harbor question: it names a place, and C4 still reads it."""
    _answered(tmp_path, [("place_code", "code"), ("place_code", "yes")])
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ()
    assert not _c4(tmp_path)


def test_a_column_not_named_as_a_place_is_not_read_from_the_file(tmp_path: pathlib.Path) -> None:
    """The file frees a column named as a place and no other: an answer about another column moves nothing."""
    _answered(tmp_path, [("lab_value", "measurement"), ("patient_id", "code")])
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ()


def test_an_answer_typed_on_the_command_line_is_not_overruled(tmp_path: pathlib.Path) -> None:
    """`--identifier place_code` stands over the file's `code`: C4 reads the column."""
    _answered(tmp_path, [("place_code", "code")])
    real = _write(tmp_path / "claims.csv", _claims(1, "P"))
    twin = _write(tmp_path / "claims-twin.csv", _claims(2, "T"))
    outcome = twin_checks.run_checks(real, twin, identifiers=("place_code",), small_tables_refused=False)
    assert not {check.code: check.passed for check in outcome.checks}["C4"]


@pytest.mark.parametrize("text", ["{not json", "[]", '{"answered_before": "code"}'])
def test_a_questions_file_that_cannot_be_read_frees_nothing(tmp_path: pathlib.Path, text: str) -> None:
    (tmp_path / "claims-questions.json").write_text(text, encoding="utf-8", newline="\n")
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ()


def test_a_file_not_synthtwins_or_about_another_table_frees_nothing(tmp_path: pathlib.Path) -> None:
    """Any JSON holding a column and an answer, or synthtwin's file about another table: C4 still reads the column.

    The outside review of batch 4z, item 4: a file beside the table holding
    only `{"arbitrary": [{"column": "zip_code", "your_answer": "no"}]}` had
    turned C4 green on a twin holding the real table's 20,000 ZIP codes.
    The file is read as `synthtwin profile --answers` reads it, and its
    `table` must name this table.
    """
    hostile = {"arbitrary": [{"column": "place_code", "your_answer": "code"}, {"column": "place_code", "your_answer": "no"}]}
    (tmp_path / "claims-questions.json").write_text(json.dumps(hostile), encoding="utf-8", newline="\n")
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ()
    assert not _c4(tmp_path)
    (tmp_path / "claims-questions.json").write_text(json.dumps(dict(hostile, table="claims.csv")), encoding="utf-8", newline="\n")
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ()
    _answered(tmp_path, [("place_code", "code"), ("place_code", "no")], table="other-claims.csv")
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ()
    assert not _c4(tmp_path)
    _answered(tmp_path, [("place_code", "code"), ("place_code", "no")])
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ("place_code",)


def test_the_file_is_read_only_once_its_path_is_checked_as_local(tmp_path: pathlib.Path, monkeypatch) -> None:  # type: ignore[no-untyped-def]
    """Item 5: the path is checked (`validate_local_path`) before anything looks at it; a path refused frees nothing."""
    _answered(tmp_path, [("place_code", "code")])
    looked: "list[str]" = []

    def refused(raw: str, *, purpose: str) -> pathlib.Path:
        looked.append(purpose)
        raise twin_checks.PathValidationError("not a local path")

    monkeypatch.setattr(twin_checks, "validate_local_path", refused)
    assert twin_checks.place_names_answered(f"{tmp_path / 'claims.csv'}", HEADER) == ()
    assert looked == ["questions file"]
