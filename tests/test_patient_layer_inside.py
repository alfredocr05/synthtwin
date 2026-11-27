"""Gate file of lane W5-PL: the patient layer on the inside path, beside the inside record and its dates zone.

The patient layer (contract 4.6c; lanes GRa and GRb) describes a table of several rows a patient in patients: the
patients' census, their fixed columns, each position-like column's list of one value a position, the families of
their rows. `synthtwin generate` makes the twin's patients from it by the patient walk (`patient_walk`), and where the
inside record stands beside the description its trajectories zone (lane IN-3) sets each patient's rows to the real
census, numbers each patient's visits 1, 2, ... again and deals the repeated numbers and yes/no outcomes by their
latent scores, while the dates zone (lane IN-5) writes each patient's dates again as one timeline in its rows' order,
every day of the month made up.

THE TABLE: the battery's invented visits table (`reliability_tables`, T2) at the owner's floor, 20,000 rows of about
2,500 patients, through the commands a person types (`reliability_battery.make_twins`: profile, the truthful answers
round by round, generate) with the inside record written in the run's own private folder.

WHAT IT HOLDS (each clause red on its mutant):

* The shipped command draws the patient layer on a table at the owner's floor, the inside record with its
  trajectories zone beside the description, and draws none on a table under the floor, described under a test's
  internal switch (mutants: the sub-switch `cli._PATIENT_LAYER_SHIPPED` off, the description holding no `grain`; the
  floor rule `ChainRun.layer_at_the_floor` read as off, `grain` standing under the floor).
* A position-like column's block publishes no count (S30), so `synthtwin validate` holds a twin to its list alone
  (V12.7's `positions` line) and lists the block's obligations with the sentence saying why; validate finds no miss
  outside the calendar counts of the made-up date column (mutant: `contract.position_like` names no column, and the
  emptied block's counts read MISSED against the walk's positions).
* The twin's patients follow the record: the census of rows a patient is the real one, each patient's visits are
  numbered 1, 2, ... in its rows' order, each patient's dates are one timeline in that order, and lane IN-1's five
  checks pass, none of them loosened (mutant: the trajectories zone's hook in `generate` left out).
"""

from __future__ import annotations

import collections
import contextlib
import csv
import io
import pathlib
import typing

import pytest

import reliability_battery as B
import reliability_tables as T
from synthtwin import cli, inside, installation, twin_checks, validation

TABLE = "T2"
ROWS = 20000
SEED = 3
PERSON = T.PERSON[TABLE]
# The date facts the excusal of a drawn twin may move: excused, or judged in their sampling window (the owner's
# ruling of 2026-11-22, batch 4z's fix round).
DATE_FACTS = frozenset(fact for fact in cli._INSIDE_EXCUSED_DATE_FACTS | cli._INSIDE_WINDOWED_DATE_FACTS)


def _places(folder: pathlib.Path) -> inside.Places:
    return inside.Places(pathlib.Path(folder, "installation", "synthtwin", "inside"), (), (),
                         installation.system_name(), ())


@contextlib.contextmanager
def _inside_path(folder: pathlib.Path) -> "typing.Iterator[None]":
    """The run's own private folder takes the inside record, whose sub-switch is on; the layer's is the shipped one."""
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr("synthtwin.cli._INSIDE_RECORD_SHIPPED", True)
        patch.setattr(inside, "default_places", lambda: _places(folder))
        yield


@pytest.fixture(scope="module")
def made(tmp_path_factory: pytest.TempPathFactory) -> "dict[str, typing.Any]":
    folder = tmp_path_factory.mktemp("layer-inside") / "product"
    text = T.text(TABLE, ROWS, SEED)
    with _inside_path(folder):
        product = B.make_twins(folder, TABLE, text, (0,), False)
    assert not product.errors, product.errors
    out = folder / "out"
    return {"folder": folder, "text": text, "twin": product.twins[0], "description": out / "visits-profile.json",
            "measured": out / "visits-twin.csv", "table": folder / "table" / T.FILES[TABLE]}


def _columns(text: str) -> "dict[str, list[str]]":
    rows = list(csv.reader(io.StringIO(text)))
    return {name: [row[at] for row in rows[1:]] for at, name in enumerate(rows[0])}


def _validated(made: "dict[str, typing.Any]") -> "tuple[int, validation.Outcome]":
    """`synthtwin validate` of the twin: its exit code and its outcome before the relabel of a drawn twin."""
    seen: "dict[str, validation.Outcome]" = {}
    original = cli._outcome_of_a_drawn_twin

    def watched(described, checked, outcome):  # type: ignore[no-untyped-def]
        seen["outcome"] = outcome
        return original(described, checked, outcome)

    folder = made["folder"]
    with _inside_path(folder), pytest.MonkeyPatch.context() as patch:
        patch.setattr(cli, "_outcome_of_a_drawn_twin", watched)
        with B.installed(folder), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            code = int(cli.main(["validate", f"{made['description']}", "--replace"], small_tables_refused=False))
    return code, seen["outcome"]


def test_the_shipped_command_draws_the_layer_at_the_floor_alone(made: "dict[str, typing.Any]",
                                                                tmp_path: pathlib.Path) -> None:
    """The flip: at the owner's floor the description holds `grain` and the record its trajectories zone; under it,
    described under a test's internal switch, no `grain` (mutants: the sub-switch off; the floor rule read as off)."""
    import json

    assert cli._PATIENT_LAYER_SHIPPED is True and cli._PATIENT_LAYER_AT_THE_FLOOR is True
    document = json.loads(made["description"].read_text(encoding="utf-8"))
    grain = document["relationships"]["grain"]
    assert isinstance(grain, dict) and grain["person"] == PERSON
    records = sorted((made["folder"] / "installation" / "synthtwin" / "inside").glob("*"))
    assert records and "trajectories" in inside.load_record(records[0])["zones"]  # type: ignore[operator]
    folder = tmp_path / "under"
    with _inside_path(folder):
        product = B.make_twins(folder, TABLE, T.text(TABLE, 3000, SEED), (), True)
    assert not product.errors, product.errors
    under = json.loads((folder / "out" / "visits-profile.json").read_text(encoding="utf-8"))
    assert isinstance(under["relationships"], dict) and under["relationships"].get("grain") is None


def test_a_position_column_is_held_to_its_list_alone(made: "dict[str, typing.Any]") -> None:
    """The visit number's emptied block is not read against the walk's positions; its list is (mutant: `contract.position_like` names no column)."""
    import json

    document = json.loads(made["description"].read_text(encoding="utf-8"))
    grain = document["relationships"]["grain"]
    listed = [entry["column"] for entry in grain["positions"]]
    assert "visit" in listed
    code, outcome = _validated(made)
    missed = [(check.column, check.fact) for check in outcome.checks if check.verdict == validation.MISSED]
    assert [each for each in missed if each[0] == "visit"] == []
    assert [each for each in missed if each[1] not in DATE_FACTS] == []
    assert code == 0
    # The counts of its block are listed with the sentence saying why, never checked; its place stays a check.
    block = {"presence.n_present", "presence.n_missing", "axes.role", "counts.n_numeric", "distinct.n_distinct"}
    checked = {check.subcheck for check in outcome.checks if check.column == "visit"}
    listed = {listing.subcheck for listing in outcome.listings if listing.column == "visit"
              and "list of one value a position" in listing.reason}
    assert checked & block == set() and block <= listed, (checked, listed)
    assert "position.at" in checked
    assert outcome.chain is not None
    lines = [(line.kind, line.subject, line.verdict) for line in outcome.chain.patient if line.kind == "positions"]
    assert ("positions", "visit", validation.HELD) in lines


def test_a_repetition_pattern_the_layer_withholds_is_withheld_not_missed() -> None:
    """A column holding values whose published pattern is empty is one the patient layer withholds (S29): its check is
    WITHHELD with the sentence saying why; an empty column's empty pattern is still checked (mutant: the withheld
    reading left out, and the walk's own repetition reads MISSED against a pattern nobody published)."""
    found = {"n_distinct_by_occurrences": {"1": 12, "40": 3}}
    withheld = validation._occurrences("staff", "identifier.n_distinct_by_occurrences", {}, found, 132)
    assert withheld.verdict == validation.WITHHELD and "patient layer withholds" in withheld.citation
    empty = validation._occurrences("staff", "identifier.n_distinct_by_occurrences", {}, {"n_distinct_by_occurrences": {}}, 0)
    assert empty.verdict == validation.HELD
    published = {"1": 12, "40": 3}
    assert validation._occurrences("staff", "identifier.n_distinct_by_occurrences", published, found, 132).verdict == validation.HELD
    other = {"n_distinct_by_occurrences": {"1": 10, "41": 3}}
    assert validation._occurrences("staff", "identifier.n_distinct_by_occurrences", published, other, 132).verdict == validation.MISSED


def test_the_twin_s_patients_follow_the_record_and_its_dates(made: "dict[str, typing.Any]") -> None:
    """The real census of rows a patient, visits 1, 2, ... and one timeline a patient, the five checks passing (mutant: the trajectories zone's hook in `generate` left out)."""
    real = _columns(made["text"])
    twin = _columns(made["twin"])

    def census(columns: "dict[str, list[str]]") -> "list[int]":
        return sorted(collections.Counter(columns[PERSON]).values())

    assert census(twin) == census(real)
    rows_of: "dict[str, list[int]]" = {}
    for row, key in enumerate(twin[PERSON]):
        if key not in rows_of:
            rows_of[key] = []
        rows_of[key] += [row]
    for rows in rows_of.values():
        assert [twin["visit"][row] for row in rows] == [f"{k + 1}" for k in range(len(rows))]
        dates = [twin["visit_date"][row] for row in rows if twin["visit_date"][row]]
        assert dates == sorted(dates)
    outcome = twin_checks.run_checks(f"{made['table']}", f"{made['measured']}", person=PERSON,
                                     small_tables_refused=False)
    assert outcome.passed, twin_checks.report_lines(outcome)
