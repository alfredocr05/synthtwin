"""Release 37, lane PRIVACY: C3, the patient-copy check, judged against what chance gives a fresh real sample.

THE FINDING (measured on the shipped route at the owner's floor): the type
battery's clinical and flowsheet tables failed C3 on release 36 -- 3 of
1,830 and 1 of 1,841 twin patients' readings equal a real patient's, where
the two real halves matched none and C3, held to the STRICT rule, allowed
none. Read inside, each match is a patient of five rows whose few readings
of a common, coarse measure (`59 %` to `72 %`, a saturation and a rhythm)
are another patient's set; and the same tables drawn again from their own
grammar at six other seeds -- FRESH REAL SAMPLES, no twin at all -- failed
C3 eight times in twelve (0 to 5 matches each). A check that a fresh draw
of the real table fails cannot tell a copy from chance there.

THE FIX (`twin_checks._dealt_again`, `_patient_rate_check`): beside the
halves, C3 reads what chance makes at the twin's own size -- the real
table's own rows dealt again among its patients, each pseudo-patient
keeping a real patient's number of rows, in four rounds of a fixed mix of
the seed -- and allows that rate and three standard errors of it where it
is wider than the halves' strict allowance. Where the dealt rows meet no
real patient's set, as where a history is a list of exact values or dates,
C3 stays strict: one copied patient fails it (the batch 4w review's items
5 and 6 stand). A twin that copies patients at scale fails it everywhere.

Every case below is a generated table of 20,000 rows: 1,800 patients of
five rows and the rest of four, one reading a row drawn from a normal
law, each red on its mutant.
"""

from __future__ import annotations

import csv
import math
import pathlib
import random

import pytest

from synthtwin import twin_checks

_FIVE_ROW_PATIENTS = 1800
_SPREAD = 17.0
_FRESH_SEEDS = (2, 3, 4, 5, 6, 7, 8, 9)


def _rows(seed: int, decimals: int = 0) -> "list[list[str]]":
    """A real table's rows by this file's grammar: 1,800 patients of five readings, then patients of four until 20,000 rows, shuffled."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    person = 0
    while len(rows) < 20000 or person < _FIVE_ROW_PATIENTS:
        for _row in range(5 if person < _FIVE_ROW_PATIENTS else 4):
            value = draw.gauss(65, _SPREAD)
            rows += [[f"P{100000 + person}", f"{value:.{decimals}f}" if decimals else f"{round(value)}"]]
        person += 1
    draw.shuffle(rows)
    return rows


def _written(path: pathlib.Path, rows: "list[list[str]]") -> str:
    with open(path, "w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, lineterminator="\n")
        writer.writerow(["person_key", "reading"])
        writer.writerows(rows)
    return str(path)


def _c3(real: str, twin: str) -> twin_checks.Check:
    outcome = twin_checks.run_checks(real, twin, person="person_key", identifiers=("person_key",),
                                     not_identifiers=("reading",), small_tables_refused=True)
    return next(check for check in outcome.checks if check.code == "C3")


def _matches(check: twin_checks.Check) -> int:
    return int(check.lines[0].split("On readings: ")[1].split(" of ")[0])


@pytest.fixture(scope="module")
def real(tmp_path_factory: pytest.TempPathFactory) -> str:
    return _written(tmp_path_factory.mktemp("c3") / "real.csv", _rows(1))


def test_fresh_real_samples_pass_c3(tmp_path: pathlib.Path, real: str) -> None:
    """Eight fresh real samples of the same grammar, read as the twin: C3 passes each, though half of them hold a patient whose readings are a real patient's by chance and the halves matched none."""
    found = []
    for seed in _FRESH_SEEDS:
        check = _c3(real, _written(tmp_path / f"fresh{seed}.csv", _rows(seed)))
        found += [(check.passed, _matches(check))]
    assert all(passed for passed, _count in found)
    assert sum(1 for _passed, count in found if count) >= 4
    assert "A fresh half of the real table against the other: 0.00 per 10,000" in check.lines[1]
    assert "the real table's own rows dealt again among its patients: 0.00 per 10,000" not in check.lines[1]


def test_the_strict_rule_is_red_on_fresh_samples(tmp_path: pathlib.Path, real: str,
                                                 monkeypatch: pytest.MonkeyPatch) -> None:
    """MUTANT: no round of rows dealt again, the halves' strict rule alone, as before the fix -- fresh real samples fail it."""
    monkeypatch.setattr(twin_checks, "SHUFFLE_ROUNDS", 0)
    failed = [seed for seed in _FRESH_SEEDS if not _c3(real, _written(tmp_path / f"fresh{seed}.csv", _rows(seed))).passed]
    assert len(failed) >= 3


def test_a_twin_copying_patients_still_fails(tmp_path: pathlib.Path, real: str) -> None:
    """A fresh sample in which 18 patients of five rows (one in a hundred) hold a real patient's five readings, under the twin's own keys: C3 fails."""
    real_rows = _rows(1)
    by_person: "dict[str, list[str]]" = {}
    for key, reading in real_rows:
        by_person.setdefault(key, []).append(reading)
    copied = [readings for readings in by_person.values() if len(readings) == 5][:18]
    twin_rows = _rows(2)
    targets = sorted({key for key, _reading in twin_rows if key < f"P{100000 + _FIVE_ROW_PATIENTS}"})[:18]
    replaced: "dict[str, list[str]]" = dict(zip(targets, copied))
    used: "dict[str, int]" = {}
    for row in twin_rows:
        if row[0] in replaced:
            place = used.get(row[0], 0)
            row[1] = replaced[row[0]][place]
            used[row[0]] = place + 1
    check = _c3(real, _written(tmp_path / "copied.csv", twin_rows))
    assert check.passed is False
    assert _matches(check) >= 18


def test_c3_stays_strict_where_chance_makes_no_copy(tmp_path: pathlib.Path) -> None:
    """Readings written with three decimals: the rows dealt again meet no real patient's set, so C3 allows none -- a fresh sample passes with no match, and one patient copied fails it."""
    real_rows = _rows(1, decimals=3)
    real = _written(tmp_path / "real3.csv", real_rows)
    fresh = _c3(real, _written(tmp_path / "fresh3.csv", _rows(2, decimals=3)))
    assert fresh.passed is True and _matches(fresh) == 0
    assert "the real table's own rows dealt again among its patients: 0.00 per 10,000; allowed up to 0.00" in fresh.lines[1]
    source = [reading for key, reading in real_rows if key == "P100000"]
    twin_rows = _rows(2, decimals=3)
    place = 0
    for row in twin_rows:
        if row[0] == "P100001":
            row[1] = source[place]
            place += 1
    assert place == 5
    assert _c3(real, _written(tmp_path / "one3.csv", twin_rows)).passed is False


@pytest.mark.parametrize("expected", [0.05, 0.25, 0.5, 1.125, 2.0, 5.0, 20.0, 60.0, 99.0])
def test_the_chance_count_is_the_poisson_tail_past_three_standard_errors(expected: float) -> None:
    """`_chance_count_at_most`: the least count a Poisson count of the mean passes with a probability of at most 0.00135, computed here apart with the exponential function."""
    count = 0
    term = math.exp(-expected)
    below = term
    while 1.0 - below > 0.00135:
        count += 1
        term = term * expected / count
        below = below + term
    assert twin_checks._chance_count_at_most(expected) == count
