"""A missed obligation says what the file holds, or why it may not say.

THE FINDING (review item P3-V12-F2 clause (a); plan amendment A-P3-45).
Profile a one-column table of sixty readings written to two decimal
places -- `1.20` through `60.20` -- and validate that same file against
its own genuine description. The page printed:

    styles.spelled [numeric.numeric_styles]: MISSED
        the description asks for: every cell written as a number
        spelled in one of the six published forms of its own value

and stopped. No found line, no reason, nothing: a researcher told that
their file failed and not what it holds. The report was worse than
silent about it, because two of its own sentences promise that every
missed obligation is printed with what the file was found to hold.

WHY THE REPAIR IS NOT "PRINT IT". What the measurement holds there is a
cell's own text, and V5.4's first rule is that no string read out of a
measured file is ever printed -- which is what lets one report be handed
to a person holding no file. So the line says WHY instead, and the two
rules that keep a measured side back each say themselves:
`_NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE` and
`_NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE`. Nothing measured is printed that
was not printed before this file existed.

WHAT THIS FILE HOLDS THE TREE TO, in four bars.

1. The reviewer's own table, end to end, says why it cannot say.
2. Every MISSED verdict in a corpus reaching all sixteen obligation
   families that a blind MISS can land in either shows what was found
   or names the rule keeping it back -- and NAMES it, rather than
   falling to the floor sentence, which no shipped subcheck may need.
   The two bars are separate on purpose: the floor means a blind line
   can never reach a page, so only the second of them can tell a
   subcheck whose reason was never filled in from one whose reason is
   its own.
3. Every call in `validation.py` that keeps a measurement back names one
   of the two rules, read off the module's own syntax. This is the half
   that covers what no corpus reaches: `styles.spill` and
   `styles.canonical.<form>` settle against the room a file's own
   description leaves, so a file that description settles does not
   readily miss them, and they are call sites like the rest.
4. HELD is left silent on purpose, and the two reasons carry nothing
   measured -- they are the same words on every file.

THE RED CHECKS.

* `REINSTATE=P3-V12-F2` puts `_silent` back as it shipped -- a MISSED
  verdict with no found value and no reason. Measured on the commit that
  adds this file: **3 of the 8 fail**.
* `REINSTATE=P3-V12-F2-map` puts the multiplicity map's own MISSED back
  the same way, which is the one blind verdict `_silent` does not build.
  Measured: **2 fail**.
* `REINSTATE=P3-V12-F2-floor` makes `_readable` return what it was
  given, so a check naming no reason reaches a page blank. Measured:
  **1 fails**.
* `REINSTATE=P3-V12-F2-promise` puts the summary's sentence back to the
  one that promised what the page did not deliver. Measured: **1
  fails**.
* The syntax walk reads a TRACKED file, so no monkeypatch reaches it.
  Deleting the reason from one call site in the working tree -- the one
  building `header.names` -- and running this module: **1 fails and 4
  error**, the failure being
  `test_every_call_that_keeps_a_measurement_back_names_its_rule` naming
  that call site's line. Measured the same way, on the same commit.
"""

import ast
import dataclasses
import os
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    profile,
    quality,
    reading,
    taxonomy,
    validation,
)

REPOSITORY = pathlib.Path(__file__).resolve().parent.parent
MODULE = REPOSITORY / "src" / "synthtwin" / "validation.py"

# The two rules a line may name, by the name the module gives each. A
# third entry here would be a policy change and not a wording one, which
# is why the set is written down rather than read off the module.
_THE_TWO_RULES = (
    "_NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE",
    "_NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE",
)

# What a reader must find under a blind MISSED line, whichever rule it
# is. Read as substrings of the joined note rather than whole sentences:
# a test pinning the paragraph word for word would be a second copy of
# it and would fail on a clearer rewording.
_OWED = (
    (
        "NOT SHOWN",
        "that the measured side is missing on purpose and not by loss",
    ),
    (
        "and this is why",
        "that a reason follows, rather than the line simply stopping",
    ),
    (
        "does not hold that file",
        "what the rule buys, which is the only reason it costs anything",
    ),
    (
        "was made in full",
        "that the verdict above is a real comparison and not a shrug",
    ),
)

# The obligation families a MISSED verdict can reach with nothing to
# show, as the sweep of the whole suite found them. The corpus below
# reaches all of them; the number is a floor so that a corpus which
# stopped building one of these tables fails here rather than passing on
# less.
_FAMILIES = (
    "document.n_rows",
    "universal.name",
    "document.columns",
    "numeric.numeric_styles",
    "label.label",
    "label.levels",
    "label.variants",
    "label.variants_withheld",
    "label.suppressed_level_counts",
    "datetime.earliest",
    "datetime.latest",
    "datetime.earliest_utc_offset",
    "datetime.latest_utc_offset",
    "datetime.date_percentiles.min",
    "datetime.date_percentiles.max",
    "free_text.n_distinct_by_occurrences",
)

# The three roles that publish a repetition pattern -- free text, record
# numbers and numbers this format cannot hold -- are one builder,
# `_occurrences`, and are reached here through the first of them. The
# other two would be the same function measured twice.

# How many calls keep a measurement back. A floor, not a count: adding a
# subcheck of this kind is ordinary, deleting the reason from one is
# what this number is here to catch.
_CALL_SITES = 20

# The reviewer's own table: sixty readings written to two decimal
# places, which is how a spreadsheet, an instrument export and a
# currency column all write numbers.
_PADDED = [f"{index}.20" for index in range(1, 61)]


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """Put one piece of the pre-amendment behaviour back on request."""
    asked = os.environ.get("REINSTATE")
    if asked == "P3-V12-F2":
        # `_silent` exactly as it shipped: HELD or MISSED off one
        # expression, and a MISSED verdict carrying no measured side and
        # no account of where it went.
        def _blind(
            column: str,
            fact: str,
            subcheck: str,
            published: str,
            held: "bool | None",
            kept_back: "tuple[str, ...]",
            why: str = validation._GATE_CLOSED,
        ) -> validation.Check:
            if held is None:
                return validation.Check(
                    column, fact, subcheck, validation.WITHHELD, published,
                    "", why,
                )
            verdict = validation.HELD if held else validation.MISSED
            return validation.Check(column, fact, subcheck, verdict, published)

        monkeypatch.setattr(validation, "_silent", _blind)
    if asked == "P3-V12-F2-map":
        kept = validation._occurrences

        def _blind_map(
            name: str,
            fact: str,
            published: "dict[str, int]",
            block: "dict[str, object]",
        ) -> validation.Check:
            check = kept(name, fact, published, block)
            if check.verdict != validation.MISSED:
                return check
            return dataclasses.replace(check, note=())

        monkeypatch.setattr(validation, "_occurrences", _blind_map)
    if asked == "P3-V12-F2-floor":
        monkeypatch.setattr(
            validation, "_readable", lambda checks: list(checks)
        )
    if asked == "P3-V12-F2-promise":
        kept_summary = quality._summary_lines

        def _overpromising(census: validation.Census) -> "list[str]":
            lines = kept_summary(census)
            said = []
            for line in lines:
                if line.startswith("description asks for, and with what"):
                    said = said + [
                        (
                            "description asks for and what the file was "
                            "found to hold. A"
                        )
                    ]
                    continue
                if line.startswith("hold or the reason that may not"):
                    continue
                said = said + [line]
            return said

        monkeypatch.setattr(quality, "_summary_lines", _overpromising)


def _described(
    folder: pathlib.Path, name: str, text: str
) -> "tuple[contract.Profile, pathlib.Path]":
    """One table, described the way `synthtwin profile` describes it."""
    folder.mkdir(parents=True, exist_ok=True)
    table = fixtures.write(folder, name, text)
    read = reading.read_table(
        f"{table}", first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(read, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{name}-profile.json", document)
    return contract.load_profile(f"{written}"), table


def _blind(outcome: validation.Outcome) -> "list[validation.Check]":
    """Every MISSED verdict with no measured side printed beside it."""
    return [
        check
        for check in outcome.checks
        if check.verdict == validation.MISSED and not check.achieved
    ]


def _stamps(year: int, sign: str) -> "list[str]":
    """Sixty instants, each carrying a UTC offset."""
    return [
        f"{year}-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}"
        f"T0{index % 8}:00:00{sign}0{(index % 3) + 1}:00"
        for index in range(60)
    ]


_SENTENCES = fixtures.prose(120)


def _corpus(root: pathlib.Path) -> "list[tuple[str, validation.Outcome]]":
    """Files measured against descriptions, chosen to miss in every way.

    Each pair is here for the family it reaches, and the families are
    written down in `_FAMILIES` so that a pair which stopped reaching
    one fails rather than quietly measuring less.
    """
    measured: list[tuple[str, validation.Outcome]] = []

    # The reviewer's own table, against its own genuine description.
    padded, table = _described(
        root / "padded",
        "padded.csv",
        fixtures.single_column_table("reading", _PADDED),
    )
    measured = measured + [
        ("padded against itself", validation.measure(padded, f"{table}"))
    ]

    # Every role at once, against a table of the same shape built from
    # another seed, and against one whose header renames a column.
    roles, _table = _described(
        root / "roles", "roles.csv", fixtures.every_role_table()
    )
    other = fixtures.write(
        root / "roles",
        "other.csv",
        fixtures.every_role_table(seed=20260901),
    )
    measured = measured + [
        ("every role, another table", validation.measure(roles, f"{other}"))
    ]
    rows = fixtures.every_role_table().splitlines()
    renamed = fixtures.write(
        root / "roles",
        "renamed.csv",
        rows[0].replace("region", "area")
        + "\n"
        + "\n".join(rows[1:])
        + "\n",
    )
    measured = measured + [
        ("every role, renamed header", validation.measure(roles, f"{renamed}"))
    ]

    # Free text that REPEATS, against the same column repeating
    # differently. The every-role table's own free-text column is all
    # different by design -- other batteries rest on that -- so a file
    # whose repetition map can MOVE has to be built here, and without
    # it the free-text repetition family is unreachable and this
    # battery measures less than it was written for.
    repeated = [_SENTENCES[index % 40] for index in range(240)]
    grouped, _table = _described(
        root / "grouped",
        "grouped.csv",
        fixtures.single_column_table("comment", repeated),
    )
    regrouped = fixtures.write(
        root / "grouped",
        "regrouped.csv",
        fixtures.single_column_table(
            "comment", [_SENTENCES[index % 26] for index in range(240)]
        ),
    )
    measured = measured + [
        ("free text regrouped", validation.measure(grouped, f"{regrouped}"))
    ]

    # A description of no rows at all, against a file holding two lines.
    counted, _table = _described(
        root / "zero",
        "zero.csv",
        fixtures.single_column_table("reading", ["1", "2", "3"]),
    )
    two_lines = fixtures.write(root / "zero", "two.csv", "reading\nreading\n")
    measured = measured + [
        (
            "no rows, two lines",
            validation.measure(
                dataclasses.replace(counted, n_rows=0), f"{two_lines}"
            ),
        )
    ]

    # Whole numbers written plainly, against the same numbers wearing
    # every other form the format holds.
    plain = [f"{index % 400 + 1}" for index in range(240)]
    numbers, _table = _described(
        root / "styles",
        "styles.csv",
        fixtures.single_column_table("reading", plain),
    )
    dressed: list[str] = []
    for index in range(240):
        value = index % 400 + 1
        if index % 3 == 0:
            dressed = dressed + [f"0{value}"]
        elif index % 3 == 1:
            dressed = dressed + [f"+{value}"]
        else:
            dressed = dressed + [f"{value}E2"]
    worn = fixtures.write(
        root / "styles",
        "worn.csv",
        fixtures.single_column_table("reading", dressed),
    )
    measured = measured + [
        ("plain numbers, dressed", validation.measure(numbers, f"{worn}"))
    ]

    # Labels: one file whose rare spellings the floor holds back, and
    # another whose rare spellings are different ones.
    held_back = [
        fixtures.LABELS[index % 5].upper()
        if index % 29 == 0
        else fixtures.LABELS[index % 5]
        for index in range(240)
    ]
    labels, _table = _described(
        root / "labels",
        "labels.csv",
        fixtures.single_column_table("region", held_back),
    )
    others = [
        fixtures.LABELS[index % 5].title()
        if index % 13 == 0
        else fixtures.LABELS[index % 5]
        for index in range(240)
    ]
    spelled = fixtures.write(
        root / "labels",
        "spelled.csv",
        fixtures.single_column_table("region", others),
    )
    measured = measured + [
        ("labels, other spellings", validation.measure(labels, f"{spelled}"))
    ]

    # Labels rare enough that the floor names none of them, so the count
    # of what it holds back is itself an obligation.
    rare = [
        fixtures.LABELS[index % 5] if index % 31 else f"rare{index}"
        for index in range(240)
    ]
    pooled, _table = _described(
        root / "rare",
        "rare.csv",
        fixtures.single_column_table("region", rare),
    )
    odd = [
        fixtures.LABELS[index % 5] if index % 17 else f"odd{index}"
        for index in range(240)
    ]
    strange = fixtures.write(
        root / "rare",
        "strange.csv",
        fixtures.single_column_table("region", odd),
    )
    measured = measured + [
        ("labels, other rare ones", validation.measure(pooled, f"{strange}"))
    ]

    # Labels, against a file whose labels are other words entirely, so
    # that the set the description publishes and each label in it are
    # obligations the file misses one by one.
    plain_labels = [fixtures.LABELS[index % 5] for index in range(240)]
    named, _table = _described(
        root / "named",
        "named.csv",
        fixtures.single_column_table("region", plain_labels),
    )
    elsewhere_labels = fixtures.write(
        root / "named",
        "elsewhere.csv",
        fixtures.single_column_table(
            "region", [fixtures.REGIONS[index % 4] for index in range(240)]
        ),
    )
    measured = measured + [
        ("labels, other words", validation.measure(named, f"{elsewhere_labels}"))
    ]

    # Instants with UTC offsets, against a year and a hemisphere away.
    when, _table = _described(
        root / "stamps",
        "stamps.csv",
        fixtures.single_column_table("seen_at", _stamps(2024, "+")),
    )
    elsewhere = fixtures.write(
        root / "stamps",
        "elsewhere.csv",
        fixtures.single_column_table("seen_at", _stamps(2025, "-")),
    )
    measured = measured + [
        ("instants, elsewhere", validation.measure(when, f"{elsewhere}"))
    ]

    # A column of record numbers, and one of free text: each publishes a
    # repetition pattern and nothing that names a value.
    codes = [f"R{index:05d}" for index in range(240)]
    numbered, _table = _described(
        root / "codes",
        "codes.csv",
        fixtures.single_column_table("record_code", codes),
    )
    repeated = fixtures.write(
        root / "codes",
        "repeated.csv",
        fixtures.single_column_table(
            "record_code", [f"R{index % 60:05d}" for index in range(240)]
        ),
    )
    measured = measured + [
        ("record numbers, repeated", validation.measure(numbered, f"{repeated}"))
    ]
    sentences = [
        f"observation {index} written out in several plain words"
        for index in range(240)
    ]
    written, _table = _described(
        root / "text",
        "text.csv",
        fixtures.single_column_table("comment", sentences),
    )
    fewer = fixtures.write(
        root / "text",
        "fewer.csv",
        fixtures.single_column_table(
            "comment",
            [
                f"observation {index % 30} written out in several plain words"
                for index in range(240)
            ],
        ),
    )
    measured = measured + [
        ("free text, fewer of them", validation.measure(written, f"{fewer}"))
    ]
    return measured


@pytest.fixture
def corpus(tmp_path: pathlib.Path) -> "list[tuple[str, validation.Outcome]]":
    """The measured corpus, rebuilt for each test that asks for it.

    Rebuilt rather than shared, because a module-scoped fixture is built
    BEFORE the function-scoped one that reinstates the old behaviour --
    so the red checks would measure the repaired tree and report green.
    """
    return _corpus(tmp_path)


def test_the_reviewers_own_table_is_told_why_it_cannot_be_told(
    tmp_path: pathlib.Path,
) -> None:
    """The exact scenario, from the CSV to the page a person reads."""
    description, table = _described(
        tmp_path / "padded",
        "padded.csv",
        fixtures.single_column_table("reading", _PADDED),
    )
    outcome = validation.measure(description, f"{table}")
    spelled = [
        check for check in outcome.checks if check.subcheck == "styles.spelled"
    ]
    assert len(spelled) == 1, (
        "the table this finding was reported on no longer carries the "
        "subcheck it was reported on, so this test is measuring something "
        "else"
    )
    check = spelled[0]
    assert check.verdict == validation.MISSED, (
        "sixty readings written to two decimal places no longer miss "
        "`styles.spelled` against their own description -- if that was "
        "repaired, amendment A-P3-46's owner decision was taken and this "
        "test should be reading the route that replaced it"
    )
    assert not check.achieved, (
        "this subcheck now prints a measured side, which would be a "
        "change to V5.4 and not to this amendment"
    )
    report = quality.quality_report(description, outcome)
    where = report.find("styles.spelled")
    assert where >= 0
    said = report[where : where + 1400]
    # Read with the line breaks taken out: the paragraph is broken to
    # the report's own width, and a phrase this file owes may fall
    # across two lines of it.
    unbroken = " ".join(said.split())
    missing = [
        f"{owed!r} -- {what_it_is}"
        for owed, what_it_is in _OWED
        if owed not in unbroken
    ]
    assert not missing, (
        "the one line this file exists for is missing part of what it "
        "owes a reader who has just been told their file failed:\n  "
        + "\n  ".join(missing)
        + "\n\nA MISSED verdict that says nothing about the file is the "
        "defect; a MISSED verdict that says why it can say nothing is "
        "the repair."
    )


def test_the_summarys_promise_about_a_missed_line_is_true_of_the_page(
    tmp_path: pathlib.Path,
) -> None:
    """What the verdict section promises is what the detail delivers.

    The page said every missed obligation was printed "with what the
    description asks for and what the file was found to hold", above a
    section that printed one of those two things. That is the round-7
    family -- a report saying something not true of the run that printed
    it -- and it is repaired by making the sentence true and by making
    the section carry the other half.
    """
    description, table = _described(
        tmp_path / "padded",
        "padded.csv",
        fixtures.single_column_table("reading", _PADDED),
    )
    outcome = validation.measure(description, f"{table}")
    report = quality.quality_report(description, outcome)
    assert "or the reason that may not be printed here" in report, (
        "the verdict section promises a found value under every missed "
        "obligation, and the detail below it prints one only where V5.4 "
        "lets it: the promise is false on this very page"
    )
    assert "or, where what the file holds may not be printed here, why." in (
        report
    ), (
        "the detail section's own heading promises what the file holds "
        "under every line, and does not say what stands there instead "
        "where it may not be printed"
    )
    assert "what the file was found to hold. A" not in report, (
        "the sentence that made the promise the page could not keep is "
        "back on the page"
    )


def test_no_missed_obligation_in_this_corpus_shows_nothing_and_says_nothing(
    corpus: "list[tuple[str, validation.Outcome]]",
) -> None:
    """The bar itself, over every family that can reach a blind MISS."""
    silent: list[str] = []
    reached: set[str] = set()
    for name, outcome in corpus:
        for check in _blind(outcome):
            reached.add(check.fact)
            if not check.note:
                silent = silent + [
                    f"{name}: {check.subcheck} [{check.fact}]"
                ]
    assert not silent, (
        "these missed obligations tell a person that their file failed "
        "and then say nothing whatever about what the file holds:\n  "
        + "\n  ".join(silent)
    )
    unreached = [family for family in _FAMILIES if family not in reached]
    assert not unreached, (
        "the corpus no longer reaches a blind MISSED verdict in these "
        "obligation families, so the bar above is measured on less than "
        "it was written for:\n  " + "\n  ".join(unreached)
    )


def test_every_missed_obligation_names_one_of_the_two_rules(
    corpus: "list[tuple[str, validation.Outcome]]",
) -> None:
    """The floor sentence is a floor, and no shipped subcheck needs it."""
    fell: list[str] = []
    for name, outcome in corpus:
        for check in _blind(outcome):
            if check.note == validation._NOT_SHOWN_AND_THIS_LINE_CANNOT_SAY_WHY:
                fell = fell + [f"{name}: {check.subcheck} [{check.fact}]"]
                continue
            assert check.note in (
                validation._NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
                validation._NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
            ), (
                f"{name}: {check.subcheck} keeps its measured side back "
                f"and gives a reason that is neither of the two this "
                f"repository states"
            )
    assert not fell, (
        "these subchecks reached the floor sentence, which says that "
        "synthtwin cannot say why it is silent. It is there for a "
        "subcheck written after this amendment; a shipped one reaching "
        "it means the reason was never filled in:\n  " + "\n  ".join(fell)
    )


def test_every_call_that_keeps_a_measurement_back_names_its_rule() -> None:
    """Read off the module's own syntax, not off what a file measured.

    THIS IS THE HALF NO CORPUS CARRIES. `styles.spill` and
    `styles.canonical.<form>` settle against the room a file's own
    description leaves, so a file that description settles does not
    readily miss them -- and they are call sites like every other, which
    is what this reads.
    """
    tree = ast.parse(MODULE.read_text(encoding="utf-8"))
    unnamed: list[str] = []
    named = 0
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        if not isinstance(node.func, ast.Name) or node.func.id != "_silent":
            continue
        if len(node.args) < 6:
            unnamed = unnamed + [
                f"line {node.lineno}: names no rule at all"
            ]
            continue
        reason = node.args[5]
        if isinstance(reason, ast.Name) and reason.id in _THE_TWO_RULES:
            named = named + 1
            continue
        if isinstance(reason, ast.Name):
            named = named + 1
            # A local standing for one of the two, as the label maps do:
            # the assignments in that function are read below.
            continue
        unnamed = unnamed + [
            (
                f"line {node.lineno}: names something that is not one of "
                f"the two rules"
            )
        ]
    assert not unnamed, (
        "these calls keep a measured value back without saying which "
        "rule keeps it, so the MISSED verdict they build prints a blank "
        "where a reader needs a sentence:\n  " + "\n  ".join(unnamed)
    )
    assert named >= _CALL_SITES, (
        f"only {named} calls keep a measurement back and name their "
        f"rule, where {_CALL_SITES} did when this bar was written -- a "
        f"call site that lost its reason is what this number is here to "
        f"catch"
    )
    text = MODULE.read_text(encoding="utf-8")
    for rule in _THE_TWO_RULES:
        assert f"{rule} = (" in text, (
            f"{rule} is no longer defined in the module whose lines it "
            f"is printed on"
        )


def test_the_floor_answers_for_a_subcheck_that_names_no_reason() -> None:
    """A blind MISSED verdict cannot reach a page, whoever built it."""
    blind = validation.Check(
        "reading",
        "numeric.numeric_styles",
        "styles.invented-next-year",
        validation.MISSED,
        "something this description asks for",
    )
    outcome = validation._assembled([blind], [], "table.csv")
    assert outcome.checks[0].note, (
        "a MISSED verdict naming neither what was found nor why it is "
        "not shown reached an assembled outcome, so a report can still "
        "print a verdict with nothing under it"
    )
    assert (
        outcome.checks[0].note
        == validation._NOT_SHOWN_AND_THIS_LINE_CANNOT_SAY_WHY
    )
    said = "\n".join(quality._detail_of(outcome.checks[0]))
    assert "defect in synthtwin" in said, (
        "the floor sentence no longer tells the reader that the silence "
        "is ours and not a fact about their file"
    )


def test_a_held_obligation_is_left_silent(
    corpus: "list[tuple[str, validation.Outcome]]",
) -> None:
    """The bound, stated as a test rather than as a hope.

    Nothing failed on a HELD line, so nobody is waiting to be told what
    their file holds there. Putting the reason under every verdict would
    add a paragraph to every line of a passing report and teach a reader
    to skip all of them.
    """
    noisy: list[str] = []
    for name, outcome in corpus:
        for check in outcome.checks:
            if check.verdict != validation.HELD:
                continue
            if check.note in (
                validation._NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
                validation._NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
                validation._NOT_SHOWN_AND_THIS_LINE_CANNOT_SAY_WHY,
            ):
                noisy = noisy + [f"{name}: {check.subcheck}"]
    assert not noisy, (
        "a HELD obligation now carries the paragraph written for a "
        "MISSED one:\n  " + "\n  ".join(noisy)
    )


def test_the_two_reasons_carry_nothing_measured(
    corpus: "list[tuple[str, validation.Outcome]]",
) -> None:
    """The same words on every file, which is what makes them safe.

    A sentence explaining why a measurement is withheld would be a poor
    joke if it carried one. These are constants: two runs on two
    different columns of two different kinds print them character for
    character alike.
    """
    seen: set[tuple[str, ...]] = set()
    for _name, outcome in corpus:
        for check in _blind(outcome):
            seen.add(check.note)
    assert seen, "no blind MISSED verdict in the corpus at all"
    assert seen <= {
        validation._NOT_SHOWN_IT_IS_TEXT_OF_THE_FILE,
        validation._NOT_SHOWN_IT_IS_A_COUNT_OF_THE_FILE,
    }, (
        "a reason printed under a missed obligation differs between "
        "files, so it is carrying something measured"
    )
    for reason in seen:
        for line in reason:
            assert not any(character.isdigit() for character in line), (
                f"a reason line carries a figure: {line!r}. These "
                f"sentences are printed instead of a measurement and "
                f"may not hold one."
            )
