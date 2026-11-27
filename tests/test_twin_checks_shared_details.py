"""Release 37, lane PRIVACY: C4 counts a twin cell equal to a real person's detail only where 1 to 10 people hold it.

THE FINDING (measured on the shipped route at the owner's floor): the type
battery's clinical table failed C4 on release 36 because its column of dates
with unknown parts holds 36 months of a year with the day unknown
(`UNK-03-2022`), each on about 120 patients' rows; the readers of a person's
details read such a cell as one, and the twin's 3,994 cells of those shared
months were counted as copies of a person's details. A value eleven people
or more share is what the floor lets a description publish everywhere
else, so C4 now counts a twin cell EQUAL to a real detail cell only where 1
to `twin_checks.RARE_HOLDERS_MOST` people hold it (`_details_held`); a real
telephone number one person holds, written in the twin, still fails, and the
names and numbers inside every real detail cell, however many share it,
are still looked for in other words (the batch 4w review's item 4 stands).
"""

from __future__ import annotations

import csv
import pathlib
import random

import pytest

from synthtwin import twin_checks

_PEOPLE = 4000
_MONTHS = [f"UNK-{month:02d}-{year}" for year in (2021, 2022, 2023) for month in range(1, 13)]


def _rows(seed: int) -> "list[list[str]]":
    """Each person's five rows: a date with unknown parts (a month and a year shared by many, or a whole date) and the person's own telephone number."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for person in range(_PEOPLE):
        phone = f"call 319-555-{person:04d}"
        for _row in range(5):
            dated = draw.choice(_MONTHS) if draw.random() < 0.5 else f"{draw.randint(1, 28):02d}-{draw.randint(1, 12):02d}-2022"
            rows += [[f"P{100000 + person}", dated, phone]]
    draw.shuffle(rows)
    return rows


def _written(path: pathlib.Path, rows: "list[list[str]]") -> str:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["person_key", "dated", "contact"])
        writer.writerows(rows)
    return str(path)


def _c4(real: str, twin: str) -> twin_checks.Check:
    outcome = twin_checks.run_checks(real, twin, person="person_key", identifiers=("person_key",),
                                     small_tables_refused=True)
    return next(check for check in outcome.checks if check.code == "C4")


@pytest.fixture()
def tables(tmp_path: pathlib.Path) -> "tuple[str, list[list[str]]]":
    return _written(tmp_path / "real.csv", _rows(1)), _rows(2)


def _twin_phones_made_up(rows: "list[list[str]]") -> "list[list[str]]":
    """The twin's own person keys and telephone numbers, its dates with unknown parts drawn as the real ones are."""
    return [[key.replace("P", "Q"), dated, phone.replace("319-555-", "319-777-")] for key, dated, phone in rows]


def test_shared_months_are_no_persons_detail(tmp_path: pathlib.Path, tables) -> None:
    """A twin whose cells of shared months (each held by about 270 people) are the real ones, its keys and telephone numbers made up: C4 passes, the months' line reading 0."""
    real, twin_rows = tables
    check = _c4(real, _written(tmp_path / "twin.csv", _twin_phones_made_up(twin_rows)))
    assert "Text column dated: 0 twin cells equal a real cell holding a person's details." in check.lines
    assert check.passed is True


def test_shared_months_are_red_on_their_mutant(tmp_path: pathlib.Path, tables, monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: every real detail cell read, however many people share it -- the shared months fail C4."""
    real, twin_rows = tables
    monkeypatch.setattr(twin_checks, "RARE_HOLDERS_MOST", 10 ** 9)
    check = _c4(real, _written(tmp_path / "twin.csv", _twin_phones_made_up(twin_rows)))
    assert check.passed is False
    assert not any(line.startswith("Text column dated: 0 twin cells equal") for line in check.lines)


def test_a_real_telephone_number_one_person_holds_still_fails(tmp_path: pathlib.Path, tables) -> None:
    """One real telephone number, held by one person on five rows, written in one twin cell: C4 fails."""
    real, twin_rows = tables
    made = _twin_phones_made_up(twin_rows)
    made[7][2] = "call 319-555-0042"
    check = _c4(real, _written(tmp_path / "twin.csv", made))
    assert check.passed is False
    assert "Identifier column contact: 1 twin cells equal a real one." in check.lines


def _remarks(seed: int, prefix: str) -> "list[list[str]]":
    """2,000 people by 10 rows: a remark, one in a hundred naming the same son (about 200 rows of 190 people share it), the others a word or a review in days."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for at in range(20000):
        roll = draw.random()
        remark = ("son Talvo Brisk to call back" if roll < 0.01 else "no change" if roll < 0.6
                  else f"review in {draw.randint(1, 60)} days, plan {draw.randint(1, 9)}")
        rows += [[f"{prefix}{at // 10:05d}", f"{draw.gauss(70, 9):.1f}", remark]]
    return rows


def _c4_remarks(path: pathlib.Path, rows: "list[list[str]]") -> str:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["patient_id", "pulse", "remark"])
        writer.writerows(rows)
    return str(path)


def test_a_shared_cells_name_in_other_words_is_still_counted(tmp_path: pathlib.Path,
                                                             monkeypatch: pytest.MonkeyPatch) -> None:
    """A relative's name in a remark about 190 people share, written in a twin cell of other words: the remark is no whole copy C4 counts, but the name inside it is still met (`elements` read from every real detail cell) and C4 fails; MUTANT: the elements read from the cells few people hold alone -- C4 passes."""
    real = _c4_remarks(tmp_path / "real.csv", _remarks(1, "P"))
    made = _remarks(2, "Q")
    made = [[key, pulse, "no change" if remark.startswith("son ") else remark] for key, pulse, remark in made]
    made[40][2] = "please ring son Talvo Brisk today"
    twin = _c4_remarks(tmp_path / "twin.csv", made)
    outcome = twin_checks.run_checks(real, twin, person="patient_id", identifiers=("patient_id",), small_tables_refused=True)
    check = next(one for one in outcome.checks if one.code == "C4")
    assert "Text column remark: 0 twin cells equal a real cell holding a person's details." in check.lines
    assert "Text column remark: 1 twin cells hold a name or a number of a real cell holding a person's details." in check.lines
    assert check.passed is False
    real_held = twin_checks._details_held

    def rare_alone(cells, read, units):  # type: ignore[no-untyped-def]
        _every, rare = real_held(cells, read, units)
        return rare, rare

    monkeypatch.setattr(twin_checks, "_details_held", rare_alone)
    outcome = twin_checks.run_checks(real, twin, person="patient_id", identifiers=("patient_id",), small_tables_refused=True)
    assert next(one for one in outcome.checks if one.code == "C4").passed is True
