"""A date column's exact counts come back, or are named where they cannot (P4-D191, P4-D192).

THE REPRODUCTION. The final skeptic's clinical export: admission dates
written `m/d/yyyy` and discharge moments `mm/dd/yyyy hh:mm` between seven
in the morning and seven at night. Described again, the twin gave back
different counts than the table at two seeds -- `n_distinct` 1077 came
back 1065 and 1107, `date_field_widths {"unpadded": 1635}` came back 1657
and 1667, and a discharge column with no value at midnight, whose count
is therefore withheld, came back with two -- while validation passed:
the first count was held to an envelope from 11 to 1460, the second to
its floor, and the third was listed as asking nothing.

The generator now reaches all three by moving ranks inside their own
gaps (method G7.3), and the validator holds the first two exactly where
the construction reaches them and the third on the side it was withheld
from. Where a pass is withdrawn, the twin's report names each miss and
the validator reports it MISSED -- the half that says so instead of
passing silently.

Every test is a round trip: describe, generate, describe the twin, and
validate the twin AND the real table at exit 0.
"""

import pathlib
import random
from datetime import date, datetime, timedelta

import pytest

from synthtwin import generation
from tests.test_files_review_repairs import _held, _missed, _trip


def _clinic(rows: int, seed: int) -> bytes:
    draw = random.Random(seed)
    lines = ["patient,admission_date,discharge_time"]
    for index in range(rows):
        admitted = date(2019, 1, 1) + timedelta(days=draw.randrange(1460))
        stay = max(0, int(draw.expovariate(1 / 5)))
        left = datetime(
            admitted.year, admitted.month, admitted.day,
            draw.randrange(7, 20), draw.randrange(60),
        ) + timedelta(days=stay)
        lines += [
            f"P{100000 + index},{admitted.month}/{admitted.day}/{admitted.year},"
            f"{left.strftime('%m/%d/%Y %H:%M')}"
        ]
    return ("\r\n".join(lines) + "\r\n").encode("utf-8")


def _clinic_reviewed(rows: int, seed: int) -> bytes:
    """The clinical export with a third column: a November review date.

    Every review falls in November, written `11/5/2021`, so a date whose
    day is below ten shows the SECOND field's width alone and the census
    names the one-field word `second-field-unpadded`. The first two
    columns are `_clinic`'s own cells, byte for byte; the third is drawn
    from a stream of its own so that nothing of theirs moves.
    """
    draw = random.Random(seed + 1)
    lines = _clinic(rows, seed).decode("utf-8").split("\r\n")
    joined = [lines[0] + ",review_date"]
    for line in lines[1:]:
        if not line:
            continue
        reviewed = date(2019 + draw.randrange(4), 11, 1 + draw.randrange(30))
        joined += [f"{line},{reviewed.month}/{reviewed.day}/{reviewed.year}"]
    return ("\r\n".join(joined) + "\r\n").encode("utf-8")


def _column(document: "dict[str, object]", name: str) -> "dict[str, object]":
    for column in document["columns"]:
        if column["name"] == name:
            return column
    raise AssertionError(name)


_FACTS = ("n_distinct", "n_distinct_folded", "date_field_widths", "n_at_midnight")


@pytest.mark.parametrize("seed", [4, 11])
def test_the_twin_gives_back_every_date_count(tmp_path: pathlib.Path, seed: int) -> None:
    result = _trip(tmp_path, "clinic", _clinic(900, 20260917), suffix=".csv", seed=seed)
    _held(result)
    for name in ("admission_date", "discharge_time"):
        real = _column(result["document"], name)
        again = _column(result["again"], name)
        for fact in _FACTS:
            assert again[fact] == real[fact], (name, fact, real[fact], again[fact])
    assert _column(result["document"], "discharge_time")["n_at_midnight"] is None
    assert _column(result["document"], "admission_date")["date_field_widths"]


def test_a_withdrawn_pass_is_named_and_missed(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The passes withdrawn: the report names each miss and validation fails.

    A discharge column whose drawn times land at midnight is forced by
    pinning every moment's minute to nought, so the withheld count is
    broken on purpose; the count of different admission dates misses on
    its own once the ranks are left where they were drawn.

    RE-ARMED FOR THE WIDTHS (plan P4-D278). The admission column's census
    is a JOINT word, and since P4-D278 a joint word's count is every
    parsed cell -- a date showing no width is counted into it -- so
    leaving its ranks where they were drawn can no longer miss it, and
    this test's widths half stopped biting. The widths half of the pass
    still decides a ONE-FIELD census, so the table carries a column of
    one: November review dates publishing `second-field-unpadded`, whose
    twin misses that word as soon as a rank is left on a day of another
    month. The admission column's widths not being named is asserted
    too, as the witness of the ruling that moved them.
    """
    monkeypatch.setattr(
        generation, "_units_settled",
        lambda column, facts, ordinals, *rest: list(ordinals),
    )
    real_off = generation._kept_off_midnight

    def onto_midnight(facts, ordinals, parsed, whole, lows, highs, floor, offsets=None):
        moved = real_off(facts, ordinals, parsed, whole, lows, highs, floor, offsets)
        pinned = generation._ranks_the_tail_pins(parsed)
        for rank in range(0, parsed, 25):
            if not pinned[rank] and lows[rank] <= moved[rank] - moved[rank] % 86400:
                moved[rank] = moved[rank] - moved[rank] % 86400
        return sorted(moved)

    monkeypatch.setattr(generation, "_kept_off_midnight", onto_midnight)
    result = _trip_allowing_misses(tmp_path, _clinic_reviewed(900, 20260917))
    report = (tmp_path / "clinic-twin-report.txt").read_text(encoding="utf-8")
    described = (tmp_path / "clinic-profile.json").read_text(encoding="utf-8")
    assert '"second-field-unpadded": 900' in described
    missed = result
    assert any("distinct.n_distinct [datetime.n_distinct]" in line for line in missed), missed
    assert any(
        "widths.second-field-unpadded [datetime.date_field_widths]" in line
        for line in missed
    ), missed
    assert any("midnight.withheld [datetime.n_at_midnight]" in line for line in missed), missed
    assert "'admission_date' -- n_distinct\n" in report
    assert "'review_date' -- date_field_widths\n" in report
    assert "'admission_date' -- date_field_widths\n" not in report
    assert "'discharge_time' -- n_at_midnight\n" in report
    assert "a count too small on one side to publish" in report


def _trip_allowing_misses(folder: pathlib.Path, data: bytes) -> "list[str]":
    """Describe, generate at seed 4 and validate the twin; its missed lines."""
    from tests.test_files_review_repairs import _exit_of

    folder.mkdir(parents=True, exist_ok=True)
    source = folder / "clinic.csv"
    source.write_bytes(data)
    code, said = _exit_of(["profile", str(source), "--out-dir", str(folder)])
    assert code == 0, said[-400:]
    described = folder / "clinic-profile.json"
    code, said = _exit_of(["generate", str(described), "--seed", "4"])
    assert code == 0, said[-400:]
    checked = folder / "check"
    checked.mkdir()
    code, _said = _exit_of(
        ["validate", str(described), "--twin", str(folder / "clinic-twin.csv"),
         "--out-dir", str(checked)]
    )
    assert code == 3
    return _missed(checked / "clinic-twin-quality.txt")


def _around_midnight() -> bytes:
    """Visits a minute before midnight on odd days and a minute after on even.

    No visit stands at midnight, so the description withholds its count;
    the pins stand either side of midnight in turn, so ranks drawn between
    a `23:59` and the next day's `00:01` land in the minute of midnight
    often -- five, three and one of a hundred at seeds 0, 4 and 11 before
    the rule.
    """
    lines = ["visit,shift"]
    for day in range(1, 21):
        for index in range(5):
            clock = "23:59" if day % 2 else "00:01"
            lines += [f"03/{day:02d}/2024 {clock},{'ab'[index % 2]}"]
    return ("\n".join(lines) + "\n").encode("utf-8")


@pytest.mark.parametrize("seed", [0, 4])
def test_a_withheld_count_at_midnight_stays_withheld(
    tmp_path: pathlib.Path, seed: int
) -> None:
    result = _trip(tmp_path, "visits", _around_midnight(), suffix=".csv", seed=seed)
    _held(result)
    assert _column(result["document"], "visit")["n_at_midnight"] is None
    assert _column(result["again"], "visit")["n_at_midnight"] is None
    twin = (tmp_path / "visits-twin.csv").read_text(encoding="utf-8").splitlines()
    # WITHHELD MEANS BELOW THE LINE THE COUNT IS PUBLISHED AT (contract
    # D15): the larger of two and the description's floor, which is the
    # default of 11 here since plan P4-D316 -- it was two while the
    # default was 1.
    from synthtwin import parsing

    line = max(
        parsing.MIDNIGHT_DISCLOSURE_FLOOR,
        result["document"]["settings"]["small_cell_floor"],
    )
    assert sum(1 for line_text in twin if " 00:00," in line_text) < line
