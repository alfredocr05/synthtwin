"""The spreadsheet artifacts join the built-in "no value" vocabulary.

Plan P4-D6.2, with the owner ruling of 2026-08-19 that admitted an
eighth member under a rule of its own. The vocabulary grew from thirteen
to twenty-one.

WHAT IS PINNED HERE, and each of it is a rule the decision states:

- the seven spreadsheet error literals are FOLDED members, matched after
  trimming and case folding like every member before them;
- the eighth is the one EXACT-SPELLING member, matched byte for byte,
  because its folded form is a person's name and a folded member would
  hollow a column of names in silence;
- ONE operation answers the vocabulary everywhere -- recognition, the
  recording of a declaration, the publication guards and the validator's
  reconstruction -- because an exception living in two places is an
  exception that comes apart from the rule it excepts;
- the criterion that keeps human words OUT is unweakened: `unknown` and
  `missing` are still data;
- what it buys is the case the decision names: a column of numbers with
  a few artifact cells stops losing its whole distribution to the parse
  line;
- and `--keep-value` is still the route for the table where an artifact
  really is data.
"""

import pathlib
import tempfile

import fixtures
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

ARTIFACTS = (
    "#DIV/0!",
    "#N/A",
    "#NAME?",
    "#NULL!",
    "#NUM!",
    "#REF!",
    "#VALUE!",
)

ABSENT_TIME = "NaT"


def _described(
    values: "list[str]", settings: "taxonomy.Settings | None" = None
) -> "tuple[dict, contract.Profile, pathlib.Path]":
    """One single-column table, described and read back."""
    folder = pathlib.Path(tempfile.mkdtemp())
    table = fixtures.write(
        folder, "thing.csv", fixtures.single_column_table("thing", values)
    )
    document = profile.build_document(
        reading.read_table(f"{table}"), settings or taxonomy.Settings(), []
    )
    written = fixtures.write_profile(folder, "thing.json", document)
    return document, contract.load_profile(f"{written}"), folder


# -- the seven folded members -----------------------------------------


def test_each_artifact_reads_as_no_value() -> None:
    """Trimmed and case folded, like every member before them."""
    for spelling in ARTIFACTS:
        assert parsing.is_missing_text(spelling), spelling
        assert parsing.is_missing_text(f"  {spelling}  "), spelling
        assert parsing.is_missing_text(spelling.lower()), spelling


def test_a_human_word_is_still_data() -> None:
    """The criterion that keeps the vocabulary honest is unweakened.

    A human word carries meaning somewhere, and a column where it does
    would be hollowed by reading it as absence.
    """
    for spelling in ("unknown", "missing", "pending", "refused", "other"):
        assert not parsing.is_missing_text(spelling), spelling


def test_a_column_of_numbers_keeps_its_distribution() -> None:
    """THE CASE THE DECISION IS FOR, and it is the whole of what it buys.

    A hundred and fourteen readings and six artifact cells. Before this
    landing the six read as text, the column missed the parse line, and
    it was described as free text -- which publishes no smallest value,
    no largest, and no distribution at all. So a person's code that
    took a mean of that column ran on their table and not on the twin.
    """
    values = [f"{10 + place % 90}" for place in range(114)] + list(
        ARTIFACTS[:6]
    )
    document, described, folder = _described(values)
    block = document["columns"][0]
    assert block["role"] in ("count", "continuous")
    assert block["n_present"] == 114
    assert block["n_missing"] == 6
    assert "percentiles" in block

    twin = generation.generate(described, 3)
    written = fixtures.write(folder, "twin.csv", rendering.twin_csv(twin))
    outcome = validation.measure(described, f"{written}")
    missed = [
        check.subcheck
        for check in outcome.checks
        if check.verdict == validation.MISSED
    ]
    assert missed == []


def test_the_artifacts_are_counted_as_holes_not_published() -> None:
    """Below the floor they are pooled, like any other hole spelling."""
    values = [f"{10 + place % 90}" for place in range(114)] + list(
        ARTIFACTS[:6]
    )
    document, _loaded, _folder = _described(values)
    block = document["columns"][0]
    assert block["missing_by_source"] == {}
    assert block["missing_by_class"]["(withheld)"] == 6


def test_the_rescue_test_asks_the_member_s_own_rule() -> None:
    """Contract C6-32 names this test explicitly, and it was folded.

    A person typing `--keep-value nat` took effect on cells spelled
    `NaT` while the settings recorded no member as named -- so their
    own word was recorded as a word of their own, the count of members
    named stayed at zero, and the reading rule the description was
    written under could not be rebuilt from it.
    """
    loose, _one, _folder = _described(
        [ABSENT_TIME] * 60 + ["ok"] * 60,
        taxonomy.Settings(kept_values=("nat",)),
    )
    block = loose["columns"][0]
    assert block["n_present"] == 60
    assert block["n_missing"] == 60
    assert loose["settings"]["kept_values"]["built_in_texts"] == []

    exact, _two, _also = _described(
        [ABSENT_TIME] * 60 + ["ok"] * 60,
        taxonomy.Settings(kept_values=(ABSENT_TIME,)),
    )
    other = exact["columns"][0]
    assert other["n_present"] == 120
    assert other["n_missing"] == 0
    assert exact["settings"]["kept_values"]["built_in_texts"] == [ABSENT_TIME]


def test_the_validator_reconstruction_asks_it_too() -> None:
    """The same crack from the other side (contract C6-32).

    A column CAN publish the key `nat` -- under a declaration of the
    person's own -- and the reconstruction fold-matched that key to the
    member `NaT`, un-pinning it from the measured side's kept values.
    """
    values = ["nat"] * 20 + [f"{10 + place}" for place in range(100)]
    document, described, _folder = _described(
        values, taxonomy.Settings(declared_missing_values=("nat",))
    )
    assert document["columns"][0]["missing_by_source"] == {"nat": 20}
    split = validation.settings_over_the_split(described)
    assert ABSENT_TIME in split.kept_values


def test_an_artifact_above_the_floor_is_named_like_any_hole() -> None:
    """The publication rules did not change; only the vocabulary did."""
    values = [f"{10 + place % 90}" for place in range(200)] + ["#N/A"] * 20
    document, _loaded, _folder = _described(values)
    block = document["columns"][0]
    assert block["missing_by_source"] == {"#N/A": 20}


# -- the one exact-spelling member ------------------------------------


def test_the_absent_time_literal_matches_byte_for_byte() -> None:
    """No trimming and no case folding, which is the whole ruling."""
    assert parsing.is_missing_text(ABSENT_TIME)
    for near in (" NaT ", "nat", "NAT", "Nat", "nAt", "NaT ", " NaT"):
        assert not parsing.is_missing_text(near), near


def test_a_column_of_names_is_not_hollowed() -> None:
    """The collision the ratified text guarded against, made a case.

    `Nat` is a person's name. Under a folded rule this column would
    have lost every cell to absence; under the exact rule it keeps all
    of them.
    """
    values = ["Nat", "NAT", "nat", " NaT "] * 30
    document, _loaded, _folder = _described(values)
    block = document["columns"][0]
    assert block["n_present"] == 120
    assert block["n_missing"] == 0


def test_the_exact_member_is_still_absence_where_it_is_written() -> None:
    """It IS a member, and a column writing it exactly loses those cells."""
    values = [f"{10 + place % 90}" for place in range(114)] + [
        ABSENT_TIME
    ] * 6
    document, _loaded, _folder = _described(values)
    block = document["columns"][0]
    assert block["n_present"] == 114
    assert block["n_missing"] == 6


# -- one operation, everywhere ----------------------------------------


def test_the_matching_rule_is_asked_the_member_s_own_way() -> None:
    """`missing_text_matches` is the one operation the decision fixes."""
    for spelling in ("#n/a", "#N/A", "  #N/A  "):
        assert parsing.missing_text_matches(spelling, "#N/A")
    assert parsing.missing_text_matches(ABSENT_TIME, ABSENT_TIME)
    for near in (" NaT ", "nat", "NAT"):
        assert not parsing.missing_text_matches(near, ABSENT_TIME)


def test_the_declaration_record_uses_the_same_rule() -> None:
    """A declaration naming a member records THAT member, its own way.

    A rule read a second time here is how the exception becomes a hole:
    the settings would record `NaT` as named by a person who typed
    ` nat `, and the validator would then read a name column's cells as
    absence when it checked a file against that description.
    """
    named, _numbers, _days = taxonomy.built_in_values_named((ABSENT_TIME,))
    assert ABSENT_TIME in named
    loose, _also, _more_days = taxonomy.built_in_values_named((" nat ",))
    assert ABSENT_TIME not in loose
    folded, _more, _also_days = taxonomy.built_in_values_named(("  #n/a  ",))
    assert "#N/A" in folded


def test_a_declared_artifact_is_data_again() -> None:
    """`--keep-value` is the stated route, and it still works.

    The decision names it as the route for the table where an artifact
    really is data, so a person whose column genuinely holds `#N/A` as
    a category is not left without one.
    """
    values = ["#N/A"] * 60 + ["ok"] * 60
    document, _loaded, _folder = _described(
        values, taxonomy.Settings(kept_values=("#N/A",))
    )
    block = document["columns"][0]
    assert block["n_present"] == 120
    assert block["n_missing"] == 0
    assert block["role"] == "binary"


# -- the count, on every surface that states it -----------------------


def test_the_vocabulary_is_twenty_one_members() -> None:
    """Eighteen spellings and three stand-in numbers.

    Every surface that STATES the size moves with the list, which is
    what the decision requires of a wire event: a reader who counts
    thirteen somewhere and twenty-one somewhere else cannot tell which
    document is describing the tool they are holding.
    """
    spellings = parsing.built_in_missing_texts()
    assert len(spellings) == 18
    assert len(parsing.NUMERIC_SENTINELS) == 3
    # THE MEMBER'S OWN SPELLING, which for these seven is the form a
    # spreadsheet writes (contract 14.4). A producer written from the
    # contract emits `#DIV/0!`, and a loader holding the folded form
    # would refuse it.
    for spelling in ARTIFACTS:
        assert spelling in spellings
    assert ABSENT_TIME in spellings


def test_no_shipped_surface_still_counts_thirteen() -> None:
    """The counted re-seal the decision asks for, asserted."""
    root = pathlib.Path(__file__).resolve().parent.parent
    for name in ("README.md", "SECURITY.md"):
        body = (root / name).read_text(encoding="utf-8")
        for line in body.split("\n"):
            if "thirteen" not in line:
                continue
            # The one permitted mention is the record of the change
            # itself, which says the list GREW from thirteen.
            assert "grew from thirteen" in line, f"{name}: {line}"
    # TAXONOMY IS IN THE WALK, and it was the one module where the
    # stale count survived this guard: a guard that names the modules
    # it happens to remember is a guard the next module escapes.
    for name in ("profile.py", "summary.py", "taxonomy.py", "cli.py"):
        body = (root / "src" / "synthtwin" / name).read_text(
            encoding="utf-8"
        )
        assert "thirteen published words" not in body, name
