"""Codex's review of batch 4q, item 3: F10 names a column of dates whose twin writes record numbers (lane ST, P4-D458).

Both new reports graded F10 (code run unchanged) `E (exact) within columns` on every switched description, also
where a held date column found no room for its made-up dates (its `made_up_years` published empty, remark NF137)
and its twin's cells are record numbers, not dates: Codex's case is the 20,000-row reverse-width births of
`tests/test_held_dates_off_the_real_shapes.py` (`Random(7)`, `_both_widths(..., True)`), held with
`--identifier`, the chain's switch on and no chain published; every source cell reads as a date and no twin cell
does. F10 now names such a column and reads N inside it, in the shared report and in the private one alike, from
the description's own facts by one rule (`generation.dates_written_as_record_numbers`): a column whose published
`made_up_years` holds no run of a kind of year one of its date layouts, or its grain's reading, writes -- empty,
or beside remark NF137 where one kind of year has room and the other none. The owned price itself (no dates
where there is no safe room) is not this item's.
"""

from __future__ import annotations

import contextlib
import csv
import io
import json
import os
import pathlib
import random

import pytest

from synthtwin import asking, chain_grades, cli, contract, generation, rendering

import chain_twins
import test_held_dates_off_the_real_shapes as shapes

ROWS = 20_000


def _installation(folder: pathlib.Path) -> pathlib.Path:
    """A chain installation of the tests' own key, as lane ST's gate makes one."""
    data = folder / "data"
    data.mkdir(mode=0o700)
    if os.name != "nt":
        data.chmod(0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    if os.name != "nt":
        key.chmod(0o600)
    key.write_bytes(chain_twins.oc.TEST_KEY)
    return data


def _f10(lines: "list[str]") -> str:
    found = [line for line in lines if "F10 " in line]
    assert len(found) == 1, lines
    return found[0]


def test_f10_names_a_held_date_column_whose_twin_writes_record_numbers(tmp_path: pathlib.Path) -> None:
    """Codex's case through the command with the chain's switch on: both reports' F10 name `dob` and read N inside
    it. Red on 29fdf3aa (`E (exact) within columns` and nothing else). MUTANT: `generation.
    dates_written_as_record_numbers` naming no column.
    """
    draw = random.Random(7)
    cells = [shapes._both_widths(draw, place, True) for place in range(ROWS)]
    out = tmp_path / "out"
    out.mkdir()
    table = out / "t.csv"
    other = random.Random(3)
    with open(table, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["dob", "test", "value"])
        for cell in cells:
            writer.writerow([cell, ("Sodium", "Chloride", "Urea")[other.randrange(3)], f"{other.uniform(2, 140):.1f}"])
    data = _installation(tmp_path)
    run = cli.ChainRun(folder=f"{data}", name="t", rows_per_person=asking.ANSWER_ONE_ROW_EACH)
    said = io.StringIO()
    with contextlib.redirect_stdout(said), contextlib.redirect_stderr(said):
        code = cli.main(["profile", f"{table}", "--out-dir", f"{out}", "--replace", "--identifier", "dob"], chain=run)
    assert code == 0, said.getvalue()[-2000:]
    document = json.loads((out / "t-profile.json").read_text(encoding="utf-8"))
    block = [one for one in document["columns"] if one["name"] == "dob"][0]
    assert block["role"] == "identifier" and block["made_up_years"] == [], block.get("made_up_years")
    loaded = contract.load_profile(f"{out / 't-profile.json'}", chain=True)
    assert loaded.relationships.switched
    said_here = "except within dob, whose twin writes record numbers where the table holds dates, which read N"
    twin = generation.generate(loaded, 1)
    shared = _f10(rendering._between_columns_lines(loaded, twin))
    assert said_here in shared, shared
    reports = sorted((data / "private-reports").iterdir())
    assert len(reports) == 1, reports
    private = _f10(reports[0].read_text(encoding="utf-8").splitlines())
    assert said_here in private, private
    assert cli._dates_not_carried(document) == ("dob",)
    assert said_here.startswith(f"except within dob, {chain_grades.NOT_DATES}")
    # ...and the twin is what the line says: no cell of `dob` is a date.
    assert not any(_a_date(cell) for cell in twin.columns[twin.names.index("dob")])


def _a_date(cell: str) -> bool:
    """Whether a cell reads as a day in either width of year the fixture writes."""
    import datetime

    for form in ("%Y-%m-%d", "%y-%m-%d", "%d/%m/%Y", "%d/%m/%y", "%m/%d/%Y", "%m/%d/%y"):
        try:
            datetime.datetime.strptime(cell.strip(), form)
        except ValueError:
            continue
        return True
    return False


ISO = "%%%%-%%-%%"
TWO = "%%/%%/%%"


@pytest.mark.parametrize(
    ("layouts", "years", "kind", "member", "named"),
    [
        # The date pass: no run at all (Codex's case), and one kind of year with room beside one with none (NF137).
        ([ISO], (), None, "", True),
        ([ISO, TWO], ((2028, 2100),), None, "", True),
        ([ISO, TWO], ((28, 60),), None, "", True),
        ([ISO, TWO], ((28, 60), (2028, 2100)), None, "", False),
        ([ISO], ((2028, 2100),), None, "", False),
        ([ISO, contract.WITHHELD], ((2028, 2100),), None, "", False),
        # A description of the release before publishes no made-up years: written as before.
        ([ISO], None, None, "", False),
        # Layouts of no date: nothing to name.
        (["@%%%%%%%"], (), None, "", False),
        # The G1 floor: the grain's reading decides; a grain reading no dates is written from its own span.
        ([ISO], (), "date", "iso-date", True),
        ([ISO], ((2028, 2100),), "date", "iso-date", False),
        ([TWO], ((2028, 2100),), "date", "two-digit-month-first-date", True),
        ([TWO], ((28, 60),), "date", "two-digit-month-first-date", False),
        (["%%%%-%%-%% %%:%%"], (), "stamp", "iso-datetime", False),
    ],
)
def test_the_rule_both_reports_read(
    layouts: "list[str]", years: "tuple[tuple[int, int], ...] | None", kind: "str | None", member: str, named: bool
) -> None:
    """`dates_written_as_record_numbers`, the twin's own rule for a held column's date layouts, read off the facts:
    NF137's case beside a published run of the other kind of year is named too. MUTANT: the rule reading only an
    empty `made_up_years` (the first builder's), which misses the two NF137 cases."""
    assert generation.dates_written_as_record_numbers(layouts, years, kind, member) is named


def test_the_private_report_reads_the_blocks_as_written_by_the_same_rule() -> None:
    """`cli._dates_not_carried` reads the column blocks as written, each by the same rule; a name that could forge a
    line is shown as text."""
    document = {"columns": [
        {"name": "a", "role": "identifier", "made_up_years": [[2028, 2030]], "layout_forms": {ISO: 5}},
        {"name": "b", "role": "identifier", "made_up_years": [], "layout_forms": {ISO: 5},
         "time_grain": {"kind": "clock", "reading": "%%:%%"}},
        {"name": "c", "role": "identifier", "layout_forms": {ISO: 5}},
        {"name": "d", "role": "date", "made_up_years": [], "layout_forms": {ISO: 5}},
        {"name": "e", "role": "identifier", "made_up_years": [], "layout_forms": {ISO: 5},
         "time_grain": {"kind": "date", "reading": "iso-date"}},
        {"name": "f", "role": "identifier", "made_up_years": [], "layout_forms": {ISO: 5}},
        {"name": "g", "role": "identifier", "made_up_years": [[2028, 2030]], "layout_forms": {ISO: 5, TWO: 5}},
        {"name": "h\nF10 forged", "role": "identifier", "made_up_years": [], "layout_forms": {ISO: 5}},
    ]}
    found = cli._dates_not_carried(document)
    assert found[:3] == ("e", "f", "g") and len(found) == 4 and "\n" not in found[3], found
    assert cli._dates_not_carried({"columns": "none"}) == () and cli._dates_not_carried({}) == ()


def test_the_grades_name_no_column_where_every_twin_is_its_kind() -> None:
    """With no such column the two lines read as before, word for word, so no other report moves."""
    assert chain_grades.off_grades()[9][2] == "E (exact) within columns; N (not carried) between columns"
    assert chain_grades.family_grades(False, False)[9][2] == (
        "E (exact) within columns; A (approximate) between columns, where no rule is published"
    )
    assert chain_grades.off_grades(("a", "b"))[9][2] == (
        f"E (exact) within columns, except within a, b, {chain_grades.NOT_DATES}, which read N (not carried); "
        "N (not carried) between columns"
    )
