"""The measured file may not choose which of its own checks run.

REVIEW ITEM P3-V2-A1. `synthtwin validate` re-describes the measured
file with the profiler's own producer (V2.1) and counts presence by
BLANKNESS (V2.4). The two readings of "which cells are present" can
disagree, because the producer reads a cell spelling a built-in missing
marker -- and a number it judges to be a stand-in for "no value" -- as
an absence, while a twin writes every absent cell empty.

WHAT WENT WRONG, AND WHY IT IS THE WORST DEFECT THE REVIEW FOUND. The
version this suite was written against WITHHELD every presence-dependent
obligation of a column wherever the two disagreed. Nothing required the
presence counts themselves to have missed first, so writing ONE cell
spelling `NA` into a column turned every level, distinctness and
suppression obligation of that column from a potential MISS into a
withholding. Two files differing in exactly one cell measured 14 MISSED
and exit 3, and 0 MISSED and exit 0. Scaled to fifteen such cells, a
file holding none of its published labels, counts of 700000 where
hundreds were published and dates in the wrong century reported 200 of
315 obligations WITHHELD, 0 MISSED, and printed "no checkable obligation
was missed". Every registered red case could be defeated the same way.

V2.4 states the bound that breaks in terms: "No gap in the
reconstruction can move a verdict; the worst it can do is withhold a
measurement that could have been printed." A gap moved a verdict from
MISSED to WITHHELD.

WHAT IS ASSERTED HERE, AND WHY IT IS A PROPERTY AND NOT A LIST OF CASES.
A repair that satisfied the one witness would leave the class open, so
these tests take the shipped fixtures and the shipped perturbation
battery -- every registered red case among them -- and inject marker
cells into every column of each, then assert what may not happen:

* a file that missed something may not stop missing everything, so a
  worse file can never buy a pass;
* which obligations a file is measured against never depends on what it
  holds;
* silence is never free -- a WITHHELD verdict must carry the disclosure
  gate's own citation AND be accompanied by that column's ROLE reported
  MISSED, so the report always says out loud why it went quiet.

The last one is the line the repair draws. Withholding is legitimate
when it is about DISCLOSURE: the measured file's own description would
not publish this, so the report must not print it. It is not legitimate
when it is about the validator's own reconstruction difficulty.

WHAT IS NOT ASSERTED, SAID PLAINLY. Not that the MISSED count can never
fall. A marker cell is a value, and a value can genuinely satisfy a
count the file was short of: writing one into a column whose published
`n_distinct` the file was one under makes that subcheck HELD, honestly.
The properties above are the ones a correct validator can actually
carry.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import os
import pathlib
import typing

import pytest

import fixtures
import test_p3v1f2_entry_table as entry_table
import test_p3v10f4_named_markers_are_holes as named_markers_are_holes
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = entry_table.SEED

# The two shapes of cell that make the producer's reading of presence
# differ from blankness, and the only two: a spelling in the built-in
# table of missing markers, and a number conventionally used to mean "no
# value". Both are taken from the product's own constants rather than
# written out here, so a spelling added to either table is covered by
# these tests on the commit that adds it.
MARKERS = (parsing.MISSING_TEXTS[5], f"{parsing.NUMERIC_SENTINELS[1]:g}")


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """`REINSTATE=P3-V10-F4` pins every built-in word to data again.

    MODULE-SCOPED, because the runs this file reads are built in
    module-scoped fixtures and a function-scoped patch would arrive
    after them.
    """
    patch = pytest.MonkeyPatch()
    if os.environ.get("REINSTATE") == "P3-V10-F4":
        named_markers_are_holes.reinstate(patch)
    yield
    patch.undo()


# -- the shipped fixtures, and the marker injection -------------------


@pytest.fixture(scope="module")
def runs(
    tmp_path_factory: pytest.TempPathFactory,
) -> "list[tuple[str, contract.Profile, str]]":
    """The same five fixtures the entry table is walked over.

    Reached through the entry table's own builders rather than copied,
    so a fixture added there is measured here too.
    """
    folder = tmp_path_factory.mktemp("presence-split")
    built: list[tuple[str, contract.Profile, str]] = []
    for name, text, declared, first_row in (
        (
            "every-role",
            fixtures.every_role_table(),
            ["record_code"],
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "unrepresentable",
            entry_table._unrepresentable_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "pooled",
            entry_table._pooled_styles_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "spelled",
            entry_table._spelled_styles_table(),
            None,
            reading.FIRST_ROW_AUTOMATIC,
        ),
        (
            "headerless",
            fixtures.rows_to_csv(
                ["1", "north"],
                [
                    [value, fixtures.REGIONS[index % 4]]
                    for index, value in enumerate(
                        fixtures.numbers(41, 60, 1, 400)
                    )
                ],
            ),
            None,
            reading.FIRST_ROW_DATA,
        ),
    ):
        described = entry_table._described(
            folder, text, declared, stem=name, first_row=first_row
        )
        twin = rendering.twin_csv(generation.generate(described, SEED))
        built = built + [(name, described, twin)]
    return built


def _marked(text: str, marker: str) -> str:
    """One cell of every column overwritten with a marker spelling.

    The LAST non-blank cell of each column, so that the perturbations
    applied on top of this -- which reach for the first record -- edit a
    different cell and the two survive together.
    """
    rows = entry_table._rows_of(text)
    if len(rows) < 2:
        return text
    for column in range(len(rows[len(rows) - 1])):
        for index in range(len(rows) - 1, 0, -1):
            row = rows[index]
            if column < len(row) and parsing.trimmed(row[column]):
                row[column] = marker
                break
    return entry_table._rebuilt(rows)


@pytest.fixture(scope="module")
def battery(
    tmp_path_factory: pytest.TempPathFactory,
    runs: "list[tuple[str, contract.Profile, str]]",
) -> "list[tuple[str, str, str, validation.Outcome, validation.Outcome]]":
    """Every perturbation of every fixture, with and without markers.

    Each row is (fixture, perturbation, marker, plain outcome, marked
    outcome). The marker goes into the TWIN and the perturbation is
    applied on top, so a byte-level perturbation is still the last thing
    that touches the file and stays what it is. Built once: this is
    several hundred whole validate runs.
    """
    folder = tmp_path_factory.mktemp("presence-split-battery")
    built: list[
        tuple[str, str, str, validation.Outcome, validation.Outcome]
    ] = []
    for name, described, twin in runs:
        plain = {"none": twin}
        for label, _kind, text in entry_table._perturbations(described, twin):
            plain[label] = text
        measured = {
            label: entry_table._measured(
                folder, described, plain[label], f"{name}-{label}.csv"
            )
            for label in sorted(plain)
        }
        for index, marker in enumerate(MARKERS):
            base = _marked(twin, marker)
            marked = {"none": base}
            for label, _kind, text in entry_table._perturbations(
                described, base
            ):
                marked[label] = text
            for label in sorted(marked):
                if label not in measured:
                    continue
                built = built + [
                    (
                        name,
                        label,
                        marker,
                        measured[label],
                        entry_table._measured(
                            folder,
                            described,
                            marked[label],
                            f"{name}-{label}-marked{index}.csv",
                        ),
                    )
                ]
    return built


def _verdicts(
    outcome: validation.Outcome,
) -> "dict[tuple[str, str], validation.Check]":
    """Every check of one run, by the identity a red case names."""
    return {
        (check.column, check.subcheck): check for check in outcome.checks
    }


# -- the property ------------------------------------------------------


def test_marker_cells_never_turn_a_failing_file_into_a_pass(
    battery: "list[tuple[str, str, str, validation.Outcome, validation.Outcome]]",
) -> None:
    """A worse file may not buy a pass (V2.4, V6.5, and the charter).

    The census's MISSED count is what the exit code and the headline are
    both written from, so a file that missed something before the marker
    cells went in and misses nothing after them is a file that talked
    its way to exit 0. Under the version this replaces, fifteen marker
    cells did exactly that on a file carrying none of its published
    labels.
    """
    assert battery
    bought: list[str] = []
    for name, label, marker, before, after in battery:
        if before.census.missed and not after.census.missed:
            bought = bought + [
                (
                    f"{name}/{label}: {before.census.missed} MISSED "
                    f"became none once a '{marker}' cell was written "
                    f"into every column "
                    f"({after.census.withheld} withheld)"
                )
            ]
    assert not bought, (
        "these files stopped missing anything by being made worse:\n  "
        + "\n  ".join(bought)
    )


def test_nothing_a_file_holds_decides_which_obligations_it_owes(
    battery: "list[tuple[str, str, str, validation.Outcome, validation.Outcome]]",
) -> None:
    """The obligation set is the description's, cells or no cells (V3.1).

    The marker cells change what the file HOLDS and may change every
    verdict; they may not change which obligations were asked. This is
    the half of the census that made the defect hard to see -- the lines
    were all still there, so nothing looked thin, and each of them said
    WITHHELD.
    """
    assert battery
    for name, label, _marker, before, after in battery:
        assert set(_verdicts(before)) == set(_verdicts(after)), (
            f"{name}/{label}: the obligations this file was measured "
            f"against changed when its cells did, and they are a "
            f"function of the description alone"
        )


# The measurements a column's own published `std_unrepresentable` fact
# decides the existence of. It is exactly the spread: a file whose
# values reach both ends of what a number can hold still has a mean and
# a shape the producer publishes, and has no deviation it can state.
_SPREAD_SUBCHECKS = ("moments.std",)


def test_silence_is_never_free_and_never_the_validator_s_own_difficulty(
    battery: "list[tuple[str, str, str, validation.Outcome, validation.Outcome]]",
) -> None:
    """The one thing that may withhold is the disclosure gate (V5.3).

    THIS IS THE LINE THE REPAIR DRAWS, and it is asserted absolutely
    rather than as a before-and-after: over every run in the battery,
    perturbed and marker-injected alike, a WITHHELD verdict must satisfy
    both halves of what withholding MEANS.

    * Its citation is the disclosure gate's own sentence. No other
      reason for silence may exist -- and the version this replaces had
      one, a second sentence saying the file held non-blank cells its
      description read as absent, which is a statement about the
      validator's reconstruction and not about what the file's own
      description would publish.
    * The same run reports MISSED a check of that column which decides
      whether the file's own description publishes such a measurement at
      all. For nearly every silence that check is the ROLE axis: the
      gate closes because the file's own description publishes a
      different class of fact for the column, and the role axis is a
      check of its own. For the spread it is
      `type.std_unrepresentable`, and amendment V2.4-A2 records why the
      role alone was too narrow to be true: a column whose values sit at
      both ends of what a number can hold is still a column of numbers,
      so its role is HELD and its role is right, and the producer
      publishes for it that the spread CANNOT be held -- which is a
      published fact of its own, is reported as a MISSED check of its
      own, and is exactly the reason no spread is shown. Either way a
      reader is never told nothing: the report says out loud, in a
      verdict, why the rest of the column went quiet.

    Together these say a measured file cannot buy silence. Making a file
    worse can make its obligations MISS, and it can make the file's own
    description publish a different class of fact -- which is reported
    -- but it can never make an obligation quietly stop being measured.

    ONE SECOND REASON EXISTS AND IT IS FENCED RATHER THAN TRUSTED
    (review item P3-V2-D-F2; plan amendment A-P3-3). A style clause over
    a count fewer cells carry than the publication floor cannot be
    reported at all: every description of that file pools those cells
    into one total, so a verdict over them states what no description of
    the file carries. That silence IS bought by the file, and the
    amendment says so in those words rather than claiming otherwise --
    what is asserted here is the fence: the reason may appear on a
    subcheck measured from the written cells and nowhere else, so it
    cannot become a general excuse for going quiet.
    """
    assert battery
    unexplained: list[str] = []
    for name, label, marker, before, after in battery:
        for outcome in (before, after):
            missed = {
                (check.column, check.subcheck)
                for check in outcome.checks
                if check.verdict == validation.MISSED
            }
            spoken = {
                check.column: check.verdict
                for check in outcome.checks
                if check.subcheck == "axes.role"
            }
            for check in outcome.checks:
                if check.verdict != validation.WITHHELD:
                    continue
                if check.citation == validation._GATE_POOLED:
                    # THE SECOND WAY THE GATE CLOSES, AND THE FENCE
                    # ROUND IT (review item P3-V2-D-F2). A count fewer
                    # cells carry than the publication floor is one no
                    # description of that file names, so a style clause
                    # over it cannot be reported without saying what
                    # every description of the file withholds. That
                    # reason belongs to the style family and to nothing
                    # else: the assertion here is not that it is
                    # allowed, but that it cannot spread. A withholding
                    # under this citation anywhere but a subcheck
                    # measured from the written cells is the old defect
                    # coming back under a new sentence.
                    if check.subcheck in validation._MEASURED_FROM_THE_CELLS:
                        continue
                    unexplained = unexplained + [
                        (
                            f"{name}/{label}/{marker}: {check.column} "
                            f"{check.subcheck} was withheld as a pooled "
                            f"count, which only a style clause may be"
                        )
                    ]
                    continue
                if check.citation != validation._GATE_CLOSED:
                    unexplained = unexplained + [
                        (
                            f"{name}/{label}/{marker}: {check.column} "
                            f"{check.subcheck} was withheld for a "
                            f"reason that is not the disclosure gate"
                        )
                    ]
                    continue
                if (check.column, "axes.role") in missed:
                    continue
                if check.subcheck in _SPREAD_SUBCHECKS and (
                    check.column,
                    "type.std_unrepresentable",
                ) in missed:
                    continue
                unexplained = unexplained + [
                    (
                        f"{name}/{label}/{marker}: {check.column} "
                        f"{check.subcheck} went silent while that "
                        f"column's role was reported "
                        f"{spoken.get(check.column, 'nothing')}"
                    )
                ]
    assert not unexplained, (
        "these obligations went silent with nothing in the report "
        "saying the file's own description would not publish them:\n  "
        + "\n  ".join(sorted(set(unexplained)))
    )


# -- the mechanism -----------------------------------------------------


def test_one_marker_cell_leaves_every_miss_standing(
    tmp_path: pathlib.Path,
) -> None:
    """The review's own witness, in one file pair (P3-V2-A1).

    Two measured files differing in EXACTLY ONE CELL, both holding four
    labels the description never published. The first misses every level
    obligation the description sets. Under the version this replaces the
    second -- one cell spelling `NA` -- missed nothing at all and exited
    0 with every one of those obligations WITHHELD.
    """
    folder = tmp_path / "witness"
    folder.mkdir()
    published = ["north", "south", "east", "west"]
    values = [published[index % 4] for index in range(60)]
    described = _describe(folder, "region", values)
    unpublished = ["kappa", "lambda", "mu", "nu"]
    carried = [unpublished[index % 4] for index in range(60)]
    control = _measure(folder, described, "region", carried, "control.csv")
    hijack = _measure(
        folder,
        described,
        "region",
        ["NA"] + carried[1:],
        "hijack.csv",
    )
    assert control.census.missed >= 4
    assert hijack.census.missed >= control.census.missed
    assert not control.census.withheld
    assert not hijack.census.withheld
    for label in published:
        assert (
            _one(hijack, f"levels.{label}.count").verdict == validation.MISSED
        )


def test_the_gate_still_comes_from_the_file_s_own_description(
    tmp_path: pathlib.Path,
) -> None:
    """V5.2 and V5.3 survive the repair, and V2.4 says which side wins.

    The measurement is taken over the blank split; WHETHER IT MAY BE
    SHOWN is still decided by the description `synthtwin profile` would
    write about this file, and by nothing else. Here a column published
    as a numeric one is rewritten to two values, which the producer
    routes to a label role and withholds below the floor -- V5.2's named
    attack. Every numeric obligation must be WITHHELD, and no number
    measured over the split may reach the result.
    """
    folder = tmp_path / "gate"
    folder.mkdir()
    described = _describe(
        folder, "reading", [f"{index + 100}" for index in range(60)]
    )
    outcome = _measure(
        folder,
        described,
        "reading",
        ["5" if index % 2 else "7" for index in range(60)],
        "twovalued.csv",
    )
    for subcheck in ("ladder.p50", "moments.mean", "ladder.min"):
        check = _one(outcome, subcheck)
        assert check.verdict == validation.WITHHELD, check
        assert check.achieved == ""
    # ...and the gate closing is itself reported, so the withholding is
    # never the only thing a reader is told.
    assert _one(outcome, "axes.role").verdict == validation.MISSED


def test_the_two_sides_build_the_same_obligations_in_the_same_order(
    tmp_path: pathlib.Path,
) -> None:
    """The precondition the two sides are paired on, asserted directly.

    The measurement and the gate are built by the SAME walk over the
    same description and are then paired position by position, which is
    sound exactly because which obligations exist is a function of the
    description alone -- no builder branches on a re-described block for
    what to build, only for what to fill in. If one ever did, the
    pairing would put one obligation's gate beside another's
    measurement, so the property is pinned here rather than left to be
    noticed: the same column, built against a numeric block, a label
    block and no block at all, yields one sequence of identities.
    """
    folder = tmp_path / "pairing"
    folder.mkdir()
    for name, values, other in (
        ("reading", [f"{index + 100}" for index in range(60)], "north"),
        (
            "region",
            [fixtures.REGIONS[index % 4] for index in range(60)],
            "17",
        ),
    ):
        described = _describe(folder, name, values)
        column = described.columns[0]
        mine = validation._corner_names(
            validation.corners_of(described), column.name
        )
        floor = described.settings.small_cell_floor
        rewritten = [other for _index in range(60)]
        blocks = [{}]
        for cells in (values, rewritten):
            target = fixtures.write(
                folder,
                f"{name}-{cells[0]}.csv",
                fixtures.single_column_table(name, cells),
            )
            table = reading.read_table(
                str(target), first_row=reading.FIRST_ROW_NAMES
            )
            for settings in (
                validation.settings_for(described),
                validation.settings_over_the_split(described),
            ):
                document = profile.build_document(table, settings, [])
                blocks = blocks + [document["columns"][0]]
        seen = []
        for block in blocks:
            built = validation._universal_checks(column, block, mine)
            built = built + validation._role_checks(
                column, block, values, floor, mine
            )
            seen = seen + [
                [(check.fact, check.subcheck) for check in built]
            ]
        for built in seen:
            assert built == seen[0]


def test_the_measurement_settings_differ_in_one_key_and_read_no_file(
    tmp_path: pathlib.Path,
) -> None:
    """V2.2 and V2.4: two settings, fifteen keys, one difference.

    The measurement side is the producer's own machinery over the same
    cells with absence pinned to blankness, and the only way it says so
    is the kept set -- the producer's own switch for "this spelling is
    data, not a hole". Every other key is the description's own, so the
    file is still described under the rules the description was written
    under, and nothing read from the file reaches either settings
    object: the extra spellings are the product's own constants.
    """
    folder = tmp_path / "settings"
    folder.mkdir()
    described = _describe(
        folder, "region", [f"{fixtures.REGIONS[index % 4]}" for index in range(60)]
    )
    gate = validation.settings_for(described)
    split = validation.settings_over_the_split(described)
    for field in (
        "small_cell_floor",
        "identifier_uniqueness",
        "identifier_minimum_rows",
        "minimum_parse_rate",
        "categorical_share",
        "categorical_ceiling",
        "categorical_floor",
        "sentinel_outlier_iqr_multiple",
        "sentinel_minimum_share",
        "declared_missing_values",
        "declaration_matching",
        "near_threshold_slack",
    ):
        assert getattr(gate, field) == getattr(split, field), field
    added = [
        spelling
        for spelling in split.kept_values
        if spelling not in gate.kept_values
    ]
    assert added
    for spelling in added:
        assert parsing.trimmed(spelling)
        assert parsing.is_missing_text(spelling) or spelling in [
            f"{value:g}" for value in parsing.NUMERIC_SENTINELS
        ]
    # The blank spelling is never kept: a blank cell is absent under
    # both readings, and keeping it would make every empty field a value.
    for spelling in split.kept_values:
        assert parsing.trimmed(spelling)


def test_the_split_description_counts_every_non_blank_cell(
    tmp_path: pathlib.Path,
) -> None:
    """V2.4's rule, read straight off the two descriptions.

    The file's own description reads the marker cells as absences; the
    measurement description reads them as the values V2.4 says they are.
    That is the whole mechanism, and it is asserted here on the
    producer's own output rather than through a verdict.

    THE MARKER IS ONE THE DESCRIPTION PASSES NO VERDICT ON, which from
    plan amendment A-P3-38 is where the pin lives. The description here
    is written from a table of thirty labels and five marker cells --
    five is below the publication floor of eleven, so no column names
    the spelling -- and the file measured against it wears the marker
    thirty times. Nothing in the description rules on those cells, so
    the split reads every one of them as a value, which is what
    residual R-P2-13 asks for.
    """
    folder = tmp_path / "split"
    folder.mkdir()
    described = _describe(
        folder,
        "region",
        ["north" for _index in range(20)]
        + ["south" for _index in range(10)]
        + ["n/a" for _index in range(5)],
    )
    # Empty because five cells sit below the publication floor, not
    # because this column's role publishes no spelling of its own.
    assert described.columns[0].role not in taxonomy.ROLES_PUBLISHING_NOTHING
    assert described.columns[0].missing_by_source == {}
    assert described.columns[0].n_missing_withheld == 5
    values = ["north" for _index in range(30)] + [
        "n/a" for _index in range(30)
    ]
    target = fixtures.write(
        folder, "again.csv", fixtures.single_column_table("region", values)
    )
    table = reading.read_table(
        str(target), first_row=reading.FIRST_ROW_NAMES
    )
    own = profile.build_document(
        table, validation.settings_for(described), []
    )
    split = profile.build_document(
        table, validation.settings_over_the_split(described), []
    )
    assert own["columns"][0]["n_present"] == 30
    assert split["columns"][0]["n_present"] == 60
    assert split["columns"][0]["n_missing"] == 0


def test_a_named_marker_is_a_hole_on_both_sides(
    tmp_path: pathlib.Path,
) -> None:
    """And where the description DOES rule on it, both sides agree.

    Review item P3-V10-F4, plan amendment A-P3-38. `missing_by_source`
    is the description naming the spelling its holes wore, so reading
    that spelling as a value on the measurement side would describe the
    file under a rule its description was not written under. The two
    descriptions of the same file then agree cell for cell, which is
    what stops the table a description came from being reported against
    it.
    """
    folder = tmp_path / "named"
    folder.mkdir()
    values = ["north" for _index in range(30)] + [
        "n/a" for _index in range(30)
    ]
    described = _describe(folder, "region", values)
    assert described.columns[0].missing_by_source == {"n/a": 30}
    assert "n/a" not in validation.settings_over_the_split(
        described
    ).kept_values
    target = fixtures.write(
        folder, "again.csv", fixtures.single_column_table("region", values)
    )
    table = reading.read_table(
        str(target), first_row=reading.FIRST_ROW_NAMES
    )
    own = profile.build_document(
        table, validation.settings_for(described), []
    )
    split = profile.build_document(
        table, validation.settings_over_the_split(described), []
    )
    assert own["columns"][0]["n_present"] == 30
    assert split["columns"][0]["n_present"] == 30
    assert split["columns"][0]["n_missing"] == 30


# -- one column, described and measured -------------------------------


def _describe(
    folder: pathlib.Path, name: str, values: "list[str]"
) -> contract.Profile:
    """One single-column table through the producer and the loader."""
    target = fixtures.write(
        folder, f"{name}.csv", fixtures.single_column_table(name, values)
    )
    table = reading.read_table(
        str(target), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{name}-profile.json", document)
    return contract.load_profile(str(written))


def _measure(
    folder: pathlib.Path,
    described: contract.Profile,
    name: str,
    values: "list[str]",
    written: str,
) -> validation.Outcome:
    """One measured file of one column, measured."""
    target = fixtures.write(
        folder, written, fixtures.single_column_table(name, values)
    )
    return validation.measure(described, str(target))


def _one(outcome: validation.Outcome, subcheck: str) -> validation.Check:
    """The one check filed under a subcheck identity."""
    found = [check for check in outcome.checks if check.subcheck == subcheck]
    assert len(found) == 1, subcheck
    return found[0]
