"""Gate file of lane IN-2 (plan P4-D496): the twin built from the inside record through the shipped commands.

THE PATH. `synthtwin profile` writes, once the description is written,
the inside record in the private folder (its marginals and relations
zones, bound to the description's bytes); `synthtwin generate` of that
description draws the twin from it and opens the twin's report with the
columns it drew. The route is lane RU-a's route S (`reliability_battery
.make_twins`: profile, the truthful answers round by round, generate) on
the visits table at the table floor of 20,000 rows (the silence case at
2,000, by the internal test device `small_tables_refused=False`), the
private folder pointed at the run's own installation.

WHAT IT HOLDS, each clause red on its mutant (lane IN-2's report):

* The record is written beside the description: the protected marker,
  mode 0600, a relations zone drawing a patient's arm once a patient and
  the visit number as each row's place (mutant: the record is never
  read at generate, so the report's opening and the patient's arm go).
* The twin is drawn from it: its report opens with the drawn columns,
  a patient's arm is one value, and the visit counts the patient's rows.
* IN-1's five checks pass on the drawn twin.
* A record written beside another version of the description is not
  read, and a caution says so (mutant: the digest is not compared).
* Where the private folder is a temporary one (a test's), no record is
  written, nothing is said, and the twin is the description's (mutant:
  the refusal is said in a temporary folder too).
"""

from __future__ import annotations

import contextlib
import csv
import io
import os
import pathlib

import typing

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, installation, twin_checks

# The drawn twin at the table floor (the five checks read an age the description reads as a number only
# there); the silence case at a test size.
FLOOR_ROWS = 20000
SMALL_ROWS = 2000
HEAD = "THIS TWIN WAS DRAWN FROM THE INSIDE RECORD"
# The visits table's person column, as the battery names it.
PERSON = T.PERSON["T2"]


def _places(folder: pathlib.Path, temporary: "tuple[pathlib.Path, ...]" = ()) -> inside.Places:
    """The run's own installation's private folder, as `reliability_battery.installed` makes it."""
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), temporary, (),
                         installation.system_name(), ())


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "tuple[pathlib.Path, str, B.Product]":
    folder = tmp_path_factory.mktemp("inside-made") / "product"
    text = T.text("T2", FLOOR_ROWS, 1)
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(inside, "default_places", lambda: _places(folder))
        product = B.make_twins(folder, "T2", text, (0,), False)
    return folder, text, product


def _records(folder: pathlib.Path) -> "list[pathlib.Path]":
    private = _places(folder).private
    return sorted(private.glob(f"*{inside.SUFFIX}")) if private.exists() else []


def _rows(text: str) -> "list[dict[str, str]]":
    return list(csv.DictReader(io.StringIO(text)))


def test_profile_writes_the_record_beside_the_description(made) -> None:  # type: ignore[no-untyped-def]
    folder, _text, product = made
    assert not product.errors, product.errors
    records = _records(folder)
    assert [path.name[: len("visits-profile-")] for path in records] == ["visits-profile-"]
    assert inside.carries_marker(records[0])
    if os.name != "nt":
        assert records[0].stat().st_mode & 0o777 == 0o600
    zone = inside.load_record(records[0])["zones"]["relations"]  # type: ignore[index]
    levels = {entry["name"]: entry.get("level") for entry in zone["columns"]}  # type: ignore[index]
    assert levels["arm"] == "patient" and levels["visit"] == "sequence", levels


def test_generate_draws_the_twin_from_the_record(made) -> None:  # type: ignore[no-untyped-def]
    folder, _text, product = made
    report = pathlib.Path(folder, "out", "visits-twin-report.txt").read_text(encoding="utf-8")
    assert report.startswith(HEAD)
    arms: "dict[str, set[str]]" = {}
    seen: "dict[str, int]" = {}
    for row in _rows(product.twins[0]):
        arms.setdefault(row[PERSON], set()).add(row["arm"])
        seen[row[PERSON]] = seen.get(row[PERSON], 0) + 1
        assert row["visit"] == f"{seen[row[PERSON]]}"
    assert all(len(held) == 1 for held in arms.values())


def test_the_five_checks_pass_on_the_drawn_twin(made, tmp_path: pathlib.Path) -> None:  # type: ignore[no-untyped-def]
    _folder, text, product = made
    real = pathlib.Path(tmp_path, "visits.csv")
    twin = pathlib.Path(tmp_path, "visits-twin.csv")
    real.write_text(text, encoding="utf-8", newline="\n")
    twin.write_text(product.twins[0], encoding="utf-8", newline="\n")
    outcome = twin_checks.run_checks(f"{real}", f"{twin}", person=PERSON, small_tables_refused=False)
    assert outcome.passed, [(check.code, check.lines) for check in outcome.checks if not check.passed]


def _generate(folder: pathlib.Path, description: pathlib.Path, out: pathlib.Path) -> "tuple[int, str]":
    out.mkdir(parents=True, exist_ok=True)
    said = io.StringIO()
    with B.installed(folder), contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["generate", f"{description}", "--out-dir", f"{out}", "--seed", "0", "--replace"],
                        small_tables_refused=False)
    return code, said.getvalue()


def test_a_record_written_beside_another_version_of_the_description_is_not_read(made, tmp_path: pathlib.Path,
                                                                                 monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    folder, _text, _product = made
    description = pathlib.Path(folder, "out", "visits-profile.json")
    places = _places(folder)
    monkeypatch.setattr(inside, "default_places", lambda: places)
    record_path = _records(folder)[0]
    kept = record_path.read_bytes()
    record = inside.load_record(record_path)
    record["table"]["description"]["digest"] = "0" * 16  # type: ignore[index]
    try:
        inside.write_record(record, record_path, places)
        code, said = _generate(folder, description, pathlib.Path(tmp_path, "other"))
    finally:
        record_path.write_bytes(kept)
    assert code == 0, said[-400:]
    assert "was written beside another version of this description" in said
    report = pathlib.Path(tmp_path, "other", "visits-twin-report.txt").read_text(encoding="utf-8")
    assert not report.startswith(HEAD)


def test_in_a_temporary_folder_no_record_is_written_and_nothing_is_said(tmp_path: pathlib.Path,
                                                                       monkeypatch: pytest.MonkeyPatch) -> None:
    folder = pathlib.Path(tmp_path, "product")
    monkeypatch.setattr(inside, "default_places", lambda: _places(folder, (tmp_path,)))
    outputs: "list[str]" = []

    def recording(argv: "list[str]", below_floor: bool) -> "tuple[int, str]":
        said = io.StringIO()
        with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
            code = cli.main(argv, small_tables_refused=not below_floor)
        outputs.append(said.getvalue())
        return int(code), said.getvalue()[-600:]

    monkeypatch.setattr(B, "command", recording)
    product = B.make_twins(folder, "T2", T.text("T2", SMALL_ROWS, 2), (0,), True)
    assert not product.errors, product.errors
    assert _records(folder) == []
    # NOTHING IS SAID OF A RECORD OF THIS RUN (release 36's landing): since lane DOCS (plan P4-D541) every summary and
    # report says what the twin carries and names the inside record in general terms, so the words alone are no
    # longer a sign; what a temporary folder must never print is a sentence about THIS run's record -- that one was
    # written and where (`inside.describe`), that it was not written, or that the twin was drawn from it.
    of_this_run = ("inside record (stays on this computer):", "inside record was not written", cli._INSIDE_REPORT_HEAD)
    assert outputs and not [text for text in outputs for said in of_this_run if said in text]
    report = pathlib.Path(folder, "out", "visits-twin-report.txt").read_text(encoding="utf-8")
    assert not report.startswith(HEAD)


@pytest.fixture(scope="module", autouse=True)
def _inside_record_switched_on() -> "typing.Iterator[None]":
    """The inside record's sub-switch is on for this file (`cli._inside_record_switched_on`)."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        yield
