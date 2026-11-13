"""The twin's report says what the twin actually does with repeated rows.

RESIDUAL R-P5-1, opened and closed 2026-09-11, before any relationship
content was designed.

**THE CLAUSE WAS FALSE.** The report told every reader: "If your table
holds several rows per person, per visit or per site, **the twin does
not**: its rows are independent of each other." The twin does. Measured
on 335 rows over 100 subjects with uneven visit counts, at seed 7:

| visits per subject | 1 | 2 | 3 | 5 | 8 |
|---|---|---|---|---|---|
| real | 32 | 17 | 20 | 13 | 18 |
| twin | 32 | 17 | 20 | 13 | 18 |

It is not luck. The identifier role publishes
`n_distinct_by_occurrences` -- the multiset of how often each identity
repeats -- and the generator reproduces it. That is a per-column fact,
inside Phase 4's one-column bound, and it has been true since the role
shipped.

**THE ERROR RAN IN THE SAFE DIRECTION AND WAS STILL WORTH REPAIRING.**
Understating what the twin carries is not a disclosure risk. It is a
sentence a person ACTS on: a researcher with a repeated-measures design,
told the twin holds no several-rows-per-person, could discard a twin
whose group-size distribution is exactly the one they needed.

**WHAT IS STILL TRUE, and the clause now says only this:** which
identity gets which count is arbitrary, which rows share an identity
carries nothing further, and the rows of one subject hold unrelated
values in every other column -- so anything that groups rows still
behaves differently.
"""

import collections
import csv
import io
import pathlib
import random

import fixtures
from synthtwin import contract, generation, parsing, rendering, taxonomy
from synthtwin import profile as profile_module
from synthtwin import reading as reading_module


def _uneven() -> "tuple[list[str], list[str]]":
    """One identity column with uneven repeats, and a value beside it."""
    draw = random.Random(5)
    names: list[str] = []
    scores: list[str] = []
    for subject in range(1, 101):
        for _visit in range(draw.choice([1, 1, 2, 3, 5, 8])):
            names += [f"S{subject:04d}"]
            scores += [f"{draw.randint(10, 99)}"]
    return names, scores


def _built(
    folder: pathlib.Path,
) -> "tuple[contract.Profile, generation.Twin]":
    names, scores = _uneven()
    rows = [[names[place], scores[place]] for place in range(len(names))]
    table = fixtures.write(
        folder,
        "cohort.csv",
        fixtures.rows_to_csv(["subject_id", "score"], rows),
    )
    read = reading_module.read_table(f"{table}")
    document = profile_module.build_document(
        read, taxonomy.Settings(), ["subject_id"]
    )
    written = fixtures.write_profile(folder, "cohort-profile.json", document)
    loaded = contract.load_profile(f"{written}")
    return loaded, generation.generate(loaded, seed=7)


def _said(loaded: contract.Profile, twin: generation.Twin) -> str:
    """The report as a person READS it, with the wrapping collapsed.

    Every line of this page is hard-wrapped at a fixed column, and
    where a sentence happens to break is not a claim anybody made --
    the same reasoning `tests/test_claim_inventory.py` gives for its
    own collapse.
    """
    return " ".join(
        parsing.visible_lines(rendering.report(loaded, twin)).split()
    )


def _repeat_shape(cells: str) -> "dict[int, int]":
    rows = list(csv.DictReader(io.StringIO(cells)))
    per = collections.Counter(row["subject_id"] for row in rows)
    return dict(collections.Counter(per.values()))


def test_the_twin_repeats_its_identities_in_the_same_pattern(
    tmp_path: pathlib.Path,
) -> None:
    """The measurement the false clause denied."""
    loaded, twin = _built(tmp_path)
    names, _scores = _uneven()
    real = dict(collections.Counter(collections.Counter(names).values()))
    assert _repeat_shape(rendering.twin_csv(twin)) == real, (
        "the identifier role publishes how often each identity repeats "
        "and the generator holds it; a report saying otherwise is false"
    )
    assert real != {1: 100}, "the fixture must actually be uneven"


def test_the_report_no_longer_says_the_twin_holds_no_repeats(
    tmp_path: pathlib.Path,
) -> None:
    loaded, twin = _built(tmp_path)
    said = _said(loaded, twin)
    assert (
        "several rows per person, per visit or per site, the twin does not"
        not in said
    ), "the clause that was false"
    assert "the twin does repeat its identities in the same pattern" in said


def test_the_report_still_says_what_grouping_costs(
    tmp_path: pathlib.Path,
) -> None:
    """The repair may not become a softening.

    What carries nothing is which rows share an identity. A reader who
    took the new clause as permission to run a repeated-measures model
    on the twin would be worse off than one who read the false one.
    """
    loaded, twin = _built(tmp_path)
    said = _said(loaded, twin)
    for owed in (
        "EVERY ROW WAS BUILT ON ITS OWN",
        "What carries nothing further is WHICH identity gets which "
        "count, and which rows share one",
        "the rows of a subject in the twin hold unrelated dates, "
        "readings and outcomes",
        "behaves differently on the twin than it will on your table",
        "misdescribes the subject-level truth",
    ):
        assert owed in said, owed


def test_the_rows_of_one_identity_carry_nothing_together(
    tmp_path: pathlib.Path,
) -> None:
    """And the limitation the clause names is measured, not asserted.

    A check that cannot fail is a defect. This one would fail if the
    twin ever started grouping a subject's values together, which is
    exactly what Phase 5's `grain` slot is for -- so it is the witness
    that says when that phase has arrived.
    """
    loaded, twin = _built(tmp_path)
    rows = list(csv.DictReader(io.StringIO(rendering.twin_csv(twin))))
    real_names, real_scores = _uneven()
    by_subject: "dict[str, list[int]]" = {}
    for row in rows:
        by_subject.setdefault(row["subject_id"], [])
        by_subject[row["subject_id"]] += [int(row["score"])]
    spreads = [
        max(values) - min(values)
        for values in by_subject.values()
        if len(values) > 2
    ]
    assert spreads, "the fixture must hold subjects with several rows"
    widest = max(spreads)
    assert widest > 30, (
        "a subject's rows in the twin are unrelated draws, so their "
        "values spread as widely as the column does; if this ever "
        "narrows, the twin has begun carrying a grain and the clause "
        "above has to move with it"
    )
