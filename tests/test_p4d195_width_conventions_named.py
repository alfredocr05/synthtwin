"""Plan P4-D195: a census of several date widths is named where it differs.

THE REPRODUCTION (final skeptic of stage 2's close, MAJOR). 900 dates, half
written `1/5/2021` and half `01/05/2021`, publish `date_field_widths
{"padded": 369, "unpadded": 381}`. The twin held 381 and 393 at seed 4, the
validator printed `widths.padded` and `widths.unpadded` HELD against "at
least 1", and the twin's report named nothing. The widths a census of one
convention counts come back exactly (P4-D192); a census naming several is
spread over the values and held only at its floor, so a count the twin does
not keep must be SAID.

Every test is a round trip: describe, generate, describe the twin, and
validate the twin and the real table at exit 0. The mutations named are the
generator's recount limited to one convention again, and the validator's
verdict printed HELD whatever the count.
"""

import json
import pathlib
import random
from datetime import date, timedelta

import pytest

from tests.test_files_review_repairs import _held, _trip


def _two_widths(rows: int, seed: int) -> bytes:
    draw = random.Random(seed)
    lines = ["visit,group"]
    for index in range(rows):
        day = date(2021, 1, 1) + timedelta(days=draw.randrange(900))
        written = (
            f"{day.month}/{day.day}/{day.year}"
            if draw.random() < 0.5
            else day.strftime("%m/%d/%Y")
        )
        lines += [f"{written},{index % 3}"]
    return ("\n".join(lines) + "\n").encode("utf-8")


def _quality(folder: pathlib.Path, name: str) -> "dict[str, str]":
    verdicts: "dict[str, str]" = {}
    for line in (folder / name).read_text(encoding="utf-8").splitlines():
        body = line.strip()
        if body.startswith("widths.") and "[datetime.date_field_widths]" in body:
            verdicts[body.split(" ")[0]] = body.rsplit(": ", 1)[1]
    return verdicts


@pytest.mark.parametrize("seed", [4, 11])
def test_a_census_of_two_widths_is_named_and_not_held(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """Mutation: with either half withdrawn, the report or the verdict lies.

    Before: `widths.padded: HELD` on a twin holding 381 against 369, with no
    note. After: every convention whose recount differs is named in the
    twin's report with both counts, and printed WITHIN-BOUND; the real
    table's own counts are printed HELD.
    """
    result = _trip(tmp_path, "visits", _two_widths(900, 5), suffix=".csv", seed=seed)
    _held(result)
    published = result["document"]["columns"][0]["date_field_widths"]
    again = result["again"]["columns"][0]["date_field_widths"]
    assert len(published) == 2, published
    twin = _quality(tmp_path / "twin-check", "visits-twin-quality.txt")
    real = _quality(tmp_path / "real-check", "visits-quality.txt")
    report = (tmp_path / "visits-twin-report.txt").read_text(encoding="utf-8")
    differing = 0
    for key in sorted(published):
        held = again[key] if key in again else 0
        assert real[f"widths.{key}"] == "HELD", real
        if held == published[key]:
            assert twin[f"widths.{key}"] == "HELD", (key, twin)
            continue
        differing += 1
        assert twin[f"widths.{key}"] == "WITHIN-BOUND", (key, twin)
        assert f"{published[key]} values written {key}" in report
        assert f"{held} values written {key}" in report
    assert differing >= 1, (published, again)


def test_the_real_table_s_own_census_of_two_widths_is_held_count_for_count(
    tmp_path: pathlib.Path,
) -> None:
    """The checker counts a census of several widths as the producer does.

    THE REPRODUCTION (the carried date items of 2026-09-18). Plan P4-D278
    counts every date showing no width into the column's commonest width,
    and the producer does it on a census of several widths too: the
    900 visits above publish `{"padded": 369, "unpadded": 531}`, which is
    381 cells showing `unpadded` and 150 whose two fields are both ten or
    more. The checker absorbed only where the census named ONE width, so
    it compared the published 531 with the file's bare 381 and printed
    the real table's own count WITHIN-BOUND of the census it had just
    been described with. Counted the producer's way, the file holds what
    its description says, and the number printed is that count.

    Mutation: the absorption asked only of a one-width census again turns
    `widths.unpadded` WITHIN-BOUND and prints 381.
    """
    from synthtwin import contract, validation
    from tests.test_files_review_repairs import _exit_of

    source = tmp_path / "visits.csv"
    source.write_bytes(_two_widths(900, 5))
    code, said = _exit_of(["profile", str(source), "--out-dir", str(tmp_path)])
    assert code == 0, said[-600:]
    described = contract.load_profile(str(tmp_path / "visits-profile.json"))
    published = json.loads(
        (tmp_path / "visits-profile.json").read_text(encoding="utf-8")
    )["columns"][0]["date_field_widths"]
    assert published == {"padded": 369, "unpadded": 381 + 150}
    outcome = validation.measure(described, str(source))
    found = {
        check.subcheck: (check.verdict, check.achieved)
        for check in outcome.checks
        if check.fact == "datetime.date_field_widths"
        and check.subcheck != "widths.unnamed"
    }
    assert found == {
        f"widths.{key}": (validation.HELD, f"{count}")
        for key, count in published.items()
    }
