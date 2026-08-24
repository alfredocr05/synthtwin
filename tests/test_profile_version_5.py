"""Profile version 5: the three additions, and the reading rule.

The contract is `docs/spec/profile-contract-v5.md`, which carries
version 4 by reference; the rulings behind it are the owner's of
2026-08-17 and plan amendments A-P3-27 and A-P3-28. Version 4's own five
additions are `tests/test_profile_version_4.py` and every one of them is
still a rule of the shipped format.

WHAT VERSION 5 IS FOR, IN ONE SENTENCE. A description has to answer
"how did a cell of this table become 'no value'?" -- the READING RULE --
because `synthtwin validate` re-describes a file with the profiler's own
machinery and has nothing else to rebuild that rule from. A version 4
description did not carry it, and the consequence was not a missing
feature but a wrong answer: a table checked against its own genuine
description came back with obligations reported as missed.

THE THREE PARTS, one section each below:

1. the spelling is stored EXACTLY and escaped only where it is printed
   (contract 5 section 4);
2. the blank count and the pooled count leave the spellings map, so the
   map holds one key space -- the table's own (section 5);
3. the two declaration records name which members of this package's own
   thirteen published words were typed, and never the person's text
   (section 6).

AND WHAT IT DOES NOT CLOSE, section 7, asserted here at the same width
as what it does: a column that publishes no value of the table publishes
no marker word either, and a spelling fewer than `small_cell_floor`
cells share is pooled and unnamed. Both are limits, not defects.

THE RED CHECKS. Every test below goes red under one of five
reinstatements, named in `_reinstated` and each of which puts back
exactly one thing version 5 changed:

    REINSTATE=A-P3-28-1   the key is escaped before it is stored
    REINSTATE=A-P3-28-2   the two counts go back inside the map
    REINSTATE=A-P3-28-3   the vocabulary lists come back empty
    REINSTATE=A-P3-28-V   the producer writes 4 and the loader reads it
    REINSTATE=A-P3-28-B   a stored key reaches a page unescaped
    REINSTATE=A-P3-28-L   the loader stops checking the source accounting
    REINSTATE=A-P3-28-P   the publication class stops emptying a block

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import copy
import json
import os
import pathlib
import typing

import pytest

import fixtures
from synthtwin import (
    canonical,
    contract,
    errors,
    generation,
    parsing,
    profile,
    reading,
    rendering,
    summary,
    taxonomy,
    validation,
)

_FLOOR = taxonomy.Settings().small_cell_floor

# The two spellings of one printed form: a real control character, and
# the printable characters the display boundary writes it as. Version 4
# stored one key for both.
_RAW = "X\x01Y"
_SHOWN = "X\\x01Y"

# This package's own word for a pooled remainder -- which a cell of
# somebody's table can also literally spell.
_POOL_WORD = "(withheld)"


@pytest.fixture(scope="module", autouse=True)
def _reinstated() -> "typing.Iterator[None]":
    """Put one part of version 4 back when REINSTATE asks for it.

    MODULE-SCOPED, because the descriptions below are built in
    module-scoped fixtures and a function-scoped patch would be applied
    after they were built -- a red check run against a patch nobody
    used.
    """
    monkeypatch = pytest.MonkeyPatch()
    asked = os.environ.get("REINSTATE")
    original = taxonomy._missing_maps

    def _escaped(missing: list, settings: taxonomy.Settings) -> tuple:
        """Version 4's storage rule: the key crosses the boundary first."""
        by_source, by_class, blank, withheld = original(missing, settings)
        shown: dict = {}
        for key in sorted(by_source):
            seen = parsing.visible(key)
            if seen in shown:
                shown[seen] = shown[seen] + by_source[key]
            else:
                shown[seen] = by_source[key]
        return shown, by_class, blank, withheld

    def _one_map(missing: list, settings: taxonomy.Settings) -> tuple:
        """Version 4's two key spaces: both counts back inside the map."""
        by_source, by_class, blank, withheld = original(missing, settings)
        mixed = dict(by_source)
        if blank:
            mixed[parsing.MISSING_BLANK] = blank
        if withheld:
            mixed[parsing.MISSING_WITHHELD] = withheld
        return mixed, by_class, 0, 0

    if asked == "A-P3-28-1":
        monkeypatch.setattr(taxonomy, "_missing_maps", _escaped)
    if asked == "A-P3-28-2":
        monkeypatch.setattr(taxonomy, "_missing_maps", _one_map)
    if asked == "A-P3-28-3":
        monkeypatch.setattr(
            taxonomy, "built_in_values_named", lambda _spellings: ((), ())
        )
    if asked == "A-P3-28-V":
        # The version bump undone in BOTH halves at once, so that the
        # rest of this file still has documents to look at: the producer
        # writes 4 again and the loader stops refusing it.
        versioned = contract._versioned

        def _lenient(parsed: object, shown: str) -> dict:
            if isinstance(parsed, dict) and parsed.get("profile_version") == 4:
                return parsed
            return versioned(parsed, shown)

        monkeypatch.setattr(profile, "PROFILE_VERSION", 4)
        monkeypatch.setattr(contract, "_versioned", _lenient)
    if asked == "A-P3-28-B":
        # The display boundary withdrawn from every surface, which is
        # what the printed-form test rests on: with it gone, the stored
        # key reaches the page as it stands.
        monkeypatch.setattr(parsing, "visible", lambda text: text)
        monkeypatch.setattr(parsing, "visible_lines", lambda text: text)
    if asked == "A-P3-28-L":
        monkeypatch.setattr(
            contract,
            "_missing_by_source",
            lambda value, where, n_missing, floor, nothing, blank, held: (
                dict(value) if isinstance(value, dict) else {}
            ),
        )
    if asked == "A-P3-28-P":
        monkeypatch.setattr(
            taxonomy,
            "publishes_no_values",
            lambda _role, _declared: False,
        )
    yield
    monkeypatch.undo()


# -- the builders ------------------------------------------------------


def _numbers(count: int) -> "list[str]":
    """Decimals whose written form is already the canonical one."""
    found: list[str] = []
    seen: dict[str, int] = {}
    step = 3
    while len(found) < count:
        step = step + 7
        text = f"{step / 10:.1f}"
        if text.endswith("0") or text in seen:
            continue
        seen[text] = 1
        found = found + [text]
    return found


def _comments(count: int, length: int) -> "list[str]":
    """Distinct sentences long enough to read as free text."""
    words = ("alpha", "bravo", "cedar", "delta", "eagle", "flint", "gamma")
    found: list[str] = []
    for index in range(count):
        built = f"note {index:03d}"
        step = index
        while len(built) < length:
            step = step + 1
            built = built + " " + words[step % len(words)]
        found = found + [built[:length]]
    return found


class Described(typing.NamedTuple):
    """One table through the real producer and the real loader."""

    document: dict
    loaded: contract.Profile
    path: str


def _built(
    folder: pathlib.Path,
    stem: str,
    values: "list[str]",
    settings: taxonomy.Settings,
    name: str = "reading",
) -> "tuple[dict, str]":
    """One column of ``values`` through the producer, and nothing more.

    Separate from `_describe` because a test about what the PRODUCER
    writes has to be able to look at the document before the loader sees
    it: where the two disagree, the interesting failure is the first
    one, not the refusal that follows it.
    """
    text = fixtures.single_column_table(name, values)
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    return profile.build_document(table, settings, []), str(path)


def _describe(
    folder: pathlib.Path,
    stem: str,
    values: "list[str]",
    settings: taxonomy.Settings,
    name: str = "reading",
) -> Described:
    """Describe one column of ``values``, all the way to a loaded profile."""
    document, path = _built(folder, stem, values, settings, name)
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )
    return Described(document, loaded, path)


def _describe_beside_a_filler(
    folder: pathlib.Path,
    stem: str,
    values: "list[str]",
    settings: taxonomy.Settings,
) -> "tuple[Described, contract.ColumnBlock]":
    """The same, with a second column, for values that include blanks.

    A blank cell in a ONE-column table is a blank LINE, and the reader
    refuses that file rather than guess whether it is a record with no
    value or a stray line -- so every witness holding blanks needs a
    neighbour column. The neighbour is a repeated label with nothing to
    say, and the block returned is the one under test.
    """
    rows = [[fixtures.REGIONS[index % 4], value]
            for index, value in enumerate(values)]
    text = fixtures.rows_to_csv(["region", "reading"], rows)
    path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, settings, [])
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )
    described = Described(document, loaded, str(path))
    return described, loaded.columns[1]


def _summary_of(described: Described) -> str:
    """The plain-language page beside the description, as a person sees it."""
    return parsing.visible_lines(summary.render(described.document, ""))


def _report_of(described: Described) -> str:
    """The generation report, as a person sees it."""
    return parsing.visible_lines(
        rendering.report(
            described.loaded, generation.generate(described.loaded, 0)
        )
    )


@pytest.fixture(scope="module")
def folder(tmp_path_factory: pytest.TempPathFactory) -> pathlib.Path:
    """One folder for every description this file builds."""
    return tmp_path_factory.mktemp("version-five")


# -- part 1: the spelling is stored exactly ----------------------------


@pytest.fixture(scope="module")
def boundary_pair(folder: pathlib.Path) -> "tuple[Described, Described]":
    """Two tables whose markers version 4's display boundary merged."""
    built: list[Described] = []
    for stem, marker in (("raw", _RAW), ("shown", _SHOWN)):
        built = built + [
            _describe(
                folder,
                stem,
                _numbers(60) + [marker] * 12,
                taxonomy.Settings(declared_missing_values=(marker,)),
            )
        ]
    return (built[0], built[1])


def test_the_stored_key_is_the_spelling_character_for_character(
    boundary_pair: "tuple[Described, Described]",
) -> None:
    """C5-1, and it is the whole of part one.

    Version 4 rewrote a key into its printable form BEFORE storing it,
    which is a rule about not scrambling somebody's terminal doing a
    protection rule's work. `variants` next door has always stored its
    keys exactly, for the reason version 4 states about it: a key
    something has to read back is a key that must survive being written
    down.
    """
    raw, shown = boundary_pair
    assert raw.loaded.columns[0].missing_by_source == {_RAW: 12}
    assert shown.loaded.columns[0].missing_by_source == {_SHOWN: 12}


def test_two_tables_the_boundary_merges_describe_differently(
    boundary_pair: "tuple[Described, Described]",
) -> None:
    """C5-N7, the producer obligation the contract states by name.

    A loader holds no table and cannot check that a key is the source
    spelling, so the contract says in as many words that it is proved on
    the producer's side by this test: two tables differing only in a
    spelling the display boundary would merge must produce different
    descriptions. Under version 4 these two files were byte for byte
    alike at 3,580 bytes each.
    """
    raw, shown = boundary_pair
    assert canonical.serialize(raw.document) != canonical.serialize(
        shown.document
    )


def test_the_printed_form_is_the_one_version_four_printed(
    boundary_pair: "tuple[Described, Described]",
) -> None:
    """C5-3 and C5-4: the file moved, the page did not.

    Every surface a person reads puts a key through the display boundary
    at the moment of SHOWING and never stores the result. So both tables
    print the same characters, and they are the characters version 4
    printed -- which is what makes storing the raw spelling safe.
    """
    raw, shown = boundary_pair
    first = _summary_of(raw)
    second = _summary_of(shown)
    assert _SHOWN in first
    assert _SHOWN in second
    assert _RAW not in first
    told = _report_of(raw)
    assert _SHOWN in told
    assert _RAW not in told


def test_the_floor_falls_on_the_exact_spelling_and_names_fewer_groups(
    folder: pathlib.Path,
) -> None:
    """C5-8: the one delta that runs the other way.

    Version 4 applied the floor to the ESCAPED key, so two different
    spellings that escape alike were counted as one group and their
    combined count could reach the floor although neither alone did --
    naming a group no single spelling of the table reached. Version 5
    counts each on its own, so here twelve cells split six and six are
    named nowhere, where version 4 would have published one key of
    twelve.
    """
    described = _describe(
        folder,
        "merged",
        _numbers(60) + [_RAW] * 6 + [_SHOWN] * 6,
        taxonomy.Settings(declared_missing_values=(_RAW, _SHOWN)),
    )
    column = described.loaded.columns[0]
    assert column.n_missing == 12
    assert column.missing_by_source == {}
    assert column.n_missing_withheld == 12


# -- part 2: the two counts leave the map ------------------------------


@pytest.fixture(scope="module")
def collision(folder: pathlib.Path) -> "tuple[Described, Described]":
    """The pool word as somebody's data, and the pool itself."""
    literal = _describe(
        folder,
        "pool-literal",
        _numbers(60) + [_POOL_WORD] * 12,
        taxonomy.Settings(declared_missing_values=(_POOL_WORD,)),
    )
    pooled = _describe(
        folder,
        "pool-really",
        _numbers(60)
        + [" " * (index + 1) + _POOL_WORD for index in range(12)],
        taxonomy.Settings(declared_missing_values=(_POOL_WORD,)),
    )
    return (literal, pooled)


def test_a_key_of_the_map_is_never_one_of_our_own_words(
    collision: "tuple[Described, Described]",
) -> None:
    """C5-N5, and the collision that made it necessary.

    Version 4 put `(blank)` and `(withheld)` into this map beside the
    person's spellings with nothing to tell them apart, so a table whose
    cells literally read `(withheld)` published the key the pool wears
    and two descriptions needing opposite readings came out byte for
    byte alike. The map holds one key space now: a key reading
    `(withheld)` means cells of the table held exactly that text.
    """
    literal, pooled = collision
    assert literal.loaded.columns[0].missing_by_source == {_POOL_WORD: 12}
    assert literal.loaded.columns[0].n_missing_withheld == 0
    assert pooled.loaded.columns[0].missing_by_source == {}
    assert pooled.loaded.columns[0].n_missing_withheld == 12
    assert canonical.serialize(literal.document) != canonical.serialize(
        pooled.document
    )


def test_the_two_counts_are_the_numbers_version_four_published(
    folder: pathlib.Path,
) -> None:
    """5.5: part two publishes nothing new, under two names.

    Sixty numbers, twelve blank cells and three cells of one rare
    spelling. Version 4 wrote `{"(blank)": 12, "(withheld)": 3}` inside
    the map; version 5 writes the same two numbers, computed by the same
    rules under the same floor, in two fields of their own.
    """
    _described, column = _describe_beside_a_filler(
        folder,
        "blank-and-pool",
        _numbers(60) + [""] * 12 + ["rare"] * 3,
        taxonomy.Settings(declared_missing_values=("rare",)),
    )
    assert column.n_missing == 15
    assert column.n_missing_blank == 12
    assert column.n_missing_withheld == 3
    assert column.missing_by_source == {}


def test_the_blank_count_is_under_the_floor_like_every_other_group(
    folder: pathlib.Path,
) -> None:
    """C5-N4, with no exemption left.

    Version 4's invariant exempted its two class keys although the
    producer floored them anyway. In version 5 the exemption is gone, so
    a blank group below the floor is not named at all -- it is pooled
    with everything else the floor held back.
    """
    _described, column = _describe_beside_a_filler(
        folder,
        "few-blanks",
        _numbers(60) + [""] * 3 + _numbers(12),
        taxonomy.Settings(),
    )
    assert column.n_missing == 3
    assert column.n_missing_blank == 0
    assert column.n_missing_withheld == 3


def test_the_source_accounting_closes_on_every_column(
    folder: pathlib.Path,
) -> None:
    """C5-N3: the spellings, the blanks and the pool come to the holes.

    Asserted over a table of every role rather than over one column,
    because an accounting rule that holds on the column somebody thought
    of is not an accounting rule.
    """
    path = fixtures.write(
        folder, "every-role.csv", fixtures.every_role_table()
    )
    table = reading.read_table(str(path))
    document = profile.build_document(
        table, taxonomy.Settings(), ["record_code"]
    )
    loaded = contract.load_profile(
        str(fixtures.write_profile(folder, "every-role.json", document))
    )
    seen_publishing = 0
    seen_silent = 0
    for column in loaded.columns:
        named = 0
        for spelling in sorted(column.missing_by_source):
            # C5-N5 with it: no key of this map is one of our own words,
            # so the accounting below is over the table's spellings and
            # two counts, never over three kinds of key in one place.
            assert spelling not in parsing.MISSING_CLASSES, column.name
            named = named + column.missing_by_source[spelling]
        publishes_nothing = taxonomy.publishes_no_values(
            column.role, column.structural_role == "identifier"
        )
        if publishes_nothing:
            seen_silent = seen_silent + 1
            assert column.missing_by_source == {}, column.name
            assert column.n_missing_blank == 0, column.name
            assert column.n_missing_withheld == 0, column.name
            continue
        seen_publishing = seen_publishing + 1
        total = named + column.n_missing_blank + column.n_missing_withheld
        assert total == column.n_missing, column.name
    assert seen_publishing >= 5
    assert seen_silent >= 2


# -- part 3: which of this package's own words were named --------------


@pytest.fixture(scope="module")
def declarations(folder: pathlib.Path) -> Described:
    """Three values named: two of ours, one of the person's own."""
    return _describe(
        folder,
        "declared",
        _numbers(200),
        taxonomy.Settings(
            kept_values=(" N/A ", "-999.00"),
            declared_missing_values=("wombat",),
        ),
    )


def test_only_a_member_of_the_published_vocabulary_is_written(
    declarations: Described,
) -> None:
    """C5-17 and C5-K1, and the worked example of contract section 6.2.

    The person typed `" N/A "`, `-999.00` and `wombat`. The document
    holds `n/a` and `-999.0` -- the vocabulary MEMBERS, in this
    package's own spelling, not their spacing and not their capitals.
    It holds `wombat` nowhere, and the reason is worth stating exactly,
    because the shorter reason was a defect on four other surfaces
    (review item P3-V9-F1): `wombat` is on no list of ours, so it
    reaches neither vocabulary list -- AND no column of this fixture
    names it, because none of its cells wore the word. A table that did
    wear it, at the floor, would publish it in `missing_by_source`.
    """
    settings = declarations.loaded.settings
    assert settings.kept_values.built_in_texts == ("n/a",)
    assert settings.kept_values.built_in_numbers == (-999.0,)
    assert settings.kept_values.n_declared == 2
    assert settings.declared_missing_values.built_in_texts == ()
    assert settings.declared_missing_values.built_in_numbers == ()
    assert settings.declared_missing_values.n_declared == 1
    written = canonical.serialize(declarations.document)
    assert " N/A " not in written
    assert "-999.00" not in written
    assert "wombat" not in written


def test_the_person_s_own_text_is_still_recorded_nowhere(
    declarations: Described,
) -> None:
    """C5-S7 and C5-18: what version 5 did NOT relax.

    `values_recorded` stays false in both records, and the shortfall
    between the count and the two lists is the whole of what a consumer
    is told about a value that is not one of ours: that it was not one
    of ours.
    """
    settings = declarations.loaded.settings
    assert settings.kept_values.values_recorded is False
    assert settings.declared_missing_values.values_recorded is False
    kept = settings.kept_values
    assert len(kept.built_in_texts) + len(kept.built_in_numbers) == 2
    assert kept.n_declared == 2
    absent = settings.declared_missing_values
    assert len(absent.built_in_texts) + len(absent.built_in_numbers) == 0
    # THE SHORTFALL IS THE WHOLE OF WHAT A CONSUMER IS TOLD about a
    # value that is not one of ours: it was not one of ours (C5-18). One
    # value was named as missing and no list carries it, so the reader
    # knows one word was named and never which.
    assert absent.n_declared == 1


def test_the_lists_are_a_function_of_the_command_line_alone(
    folder: pathlib.Path,
) -> None:
    """C5-K5, the second producer obligation the contract states by name.

    A loader holds no command line and cannot check this, so the
    contract says it is proved here: the same options over two different
    tables -- one holding the named word in every one of its absent
    cells, one holding it in none -- must write identical lists. If they
    did not, the field would be evidence about the table, which is
    exactly what section 6 exists not to be.
    """
    settings = taxonomy.Settings(declared_missing_values=("n/a",))
    held = _describe(
        folder, "vocab-held", _numbers(60) + ["n/a"] * 12, settings
    )
    absent = _describe(folder, "vocab-absent", _numbers(60), settings)
    assert held.document["settings"]["declared_missing_values"] == (
        absent.document["settings"]["declared_missing_values"]
    )
    assert absent.loaded.settings.declared_missing_values.built_in_texts == (
        "n/a",
    )
    assert held.loaded.columns[0].n_missing == 12
    assert absent.loaded.columns[0].n_missing == 0


def test_the_whole_of_the_kept_side_is_recorded(folder: pathlib.Path) -> None:
    """C5-19, which is what makes part three a closure and not a start.

    The values for which `--keep-value` can change how any cell is read
    are exactly the members of the published vocabulary, so recording
    those records the WHOLE of the kept side's effect on the reading
    rule. The witness is the review's own: `--keep-value n/a` on a
    column of numbers, where no level, no variant and no sentinel
    verdict can carry the word.

    AND THE VALIDATOR READS IT (plan amendment A-P3-29). This assertion
    was `== ()` while the producer stage stood alone, which was true of
    the validator and never of the format; the settings block is where
    the word is, and `kept_spellings` is what reads it.
    """
    described = _describe(
        folder,
        "rescued",
        _numbers(200) + ["n/a"],
        taxonomy.Settings(kept_values=("n/a",)),
    )
    column = described.loaded.columns[0]
    assert column.n_present == 201
    assert column.n_missing == 0
    assert column.n_not_numeric == 1
    assert described.loaded.settings.kept_values.built_in_texts == ("n/a",)
    assert validation.kept_spellings(described.loaded) == ("n/a",)
    for block in described.document["columns"]:
        assert "n/a" not in json.dumps(block), (
            "a column block carries the rescued word, so the closure "
            "rests on something other than the settings block"
        )


# -- the version rule and the refusal ----------------------------------


def test_the_producer_writes_five_and_the_loader_reads_five(
    declarations: Described,
) -> None:
    """C5-VER and C5-24 -- and the number has moved past both.

    This file is the record of what the version 5 landing added, and
    the additions below are all still true of the producer. The NUMBER
    is not: Phase 4 carried its own wire changes and the version moved
    to six with them, so what this test pins is that the move happened
    and that the producer and the loader moved together. A version
    number one of them could drift from is a version number nothing
    pins.
    """
    assert profile.PROFILE_VERSION == 6
    assert contract.PROFILE_VERSION == 6
    assert declarations.document["profile_version"] == 6
    assert declarations.loaded.profile_version == 6


def test_a_version_four_description_is_refused_in_the_contract_s_words(
    folder: pathlib.Path, declarations: Described
) -> None:
    """C5-26, word for word, with only the two versions filled in.

    The message has three jobs and this test holds it to all three: say
    which version each side is, say WHY the older file cannot be read,
    and say what to do in a way that can be followed -- which means
    naming EVERY option that changes what the description says, because
    a description made again without one of them reads the person's
    table differently and, for two of the five, publishes more of it.

    It named two options until 2026-08-17 and the two could disclose
    (review item P3-V9-F6; plan amendment A-P3-36). The measurement is
    in `tests/test_p3v9f6_migration_names_every_option.py`, which also
    holds the set of options named here to the shipped parser's own, so
    a new option cannot be forgotten by this sentence.
    """
    older = copy.deepcopy(json.loads(json.dumps(declarations.document)))
    older["profile_version"] = 4
    written = fixtures.write_profile(folder, "older.json", older)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{written}")
    said = f"{refused.value}"
    assert said == (
        "This description was written by an older version of synthtwin: "
        "it says it is version 4, and this synthtwin reads version 6. A "
        "version 6 description records things an older description does "
        'not \u2014 which of synthtwin\'s own words for "no value" you '
        "named on the command line, and how dates whose day and month "
        "are both numbers were read "
        "\u2014 so this file cannot be read back "
        "exactly. Please make the description again by running "
        "'synthtwin profile' on your table, giving it every option you "
        "gave the first time: --keep-value, --missing-value, "
        "--identifier, --smallest-group, --first-row and --day-first. "
        "Every one of "
        "them changes what the description PUBLISHES about your table, "
        "so any option you leave out can put something into the new "
        "description that the old one held back: without the "
        "--smallest-group you gave, a value that fewer rows share can "
        "be named; without the --identifier you gave, a column of "
        "record numbers is described like any other column; without "
        "the --missing-value you gave, a stand-in is read as a real "
        "reading, and the stand-in itself can be published as the "
        "column's smallest value; without the --keep-value you gave, a "
        "word you had counted as an ordinary value becomes a gap, "
        "which can change what kind of column synthtwin sees and "
        "publish both that word and the column's own numbers; "
        "without the --first-row you gave, the first line of your file "
        "is read as the column names and published as them; and "
        "without the --day-first you gave, a date whose day and month "
        "are both written as numbers \u2014 with slashes, with dots, or "
        "with a two-figure year \u2014 can be read "
        "the other way round, which changes the dates the description "
        "publishes and can leave the column described as text instead. "
        "If you do not hold the table yourself, ask whoever made this "
        "description to run it again for you. Read the "
        "summary page synthtwin writes beside the new description "
        "before either file goes anywhere, and use the description "
        "exactly as synthtwin writes it."
    )


def test_the_version_bump_loosened_no_other_refusal(
    folder: pathlib.Path, declarations: Described
) -> None:
    """Every refusal that fired before the bump still fires.

    This is a version bump, not a loosening, so the list below is the
    rules the strict loader raised by name before it and it is checked
    as a SET rather than as examples: a rule that stopped being raised
    would leave this list holding a name nothing produces.
    `tests/test_contract_loader.py` carries one refused description per
    rule; what this adds is the promise that the set did not shrink when
    the version moved.
    """
    before = {
        "S1", "S2", "S4", "S5", "S6", "S8", "S9", "S10", "S11",
        "A1", "A2", "A3", "A4",
        "X1", "X2", "X3", "X4",
        "N1", "N2",
        "V1", "V2", "V3", "V4",
        "B1", "B2", "B3", "B4", "B5", "B6", "B7",
        "E1",
    }
    named = set(contract.INVARIANTS)
    kept = before & named
    assert len(kept) >= 25, sorted(before - named)
    # AND THE FOUR THE CONTRACT RENAMED ARE STILL THERE, under the names
    # version 5 gives them (its section 9): a superseded rule is a rule
    # that moved, never a rule that went.
    for rule in ("C5-N3", "C5-N4", "C5-S7", "C5-S13"):
        assert rule in named, rule
    # ...and the loader really raises with them, which a list of names
    # cannot show on its own.
    broken = json.loads(json.dumps(declarations.document))
    broken["columns"][0]["n_missing_blank"] = 3
    written = fixtures.write_profile(folder, "broken.json", broken)
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(f"{written}")
    assert "C5-N3" in f"{refused.value}"


def test_the_producer_never_writes_what_its_own_loader_refuses(
    folder: pathlib.Path,
) -> None:
    """The property the whole format rests on, over the new fields too.

    Every shape the producer can write for the two new counts is walked:
    a column with no absent cells at all, one whose absent cells are all
    blank, one whose blanks fall below the floor, one that pools a
    spelling, one that names a spelling, and a column publishing no
    value of the table. Each is described by the real producer, checked
    by the producer's own publication guard, and read back by the strict
    loader.
    """
    shapes = {
        "none": (_numbers(60), taxonomy.Settings()),
        "all-blank": (
            _numbers(60) + [""] * 12 + _numbers(12), taxonomy.Settings()
        ),
        "few-blank": (
            _numbers(60) + [""] * 3 + _numbers(12), taxonomy.Settings()
        ),
        "pooled": (
            _numbers(60) + ["rare"] * 3,
            taxonomy.Settings(declared_missing_values=("rare",)),
        ),
        "named": (
            _numbers(60) + ["XX"] * 12,
            taxonomy.Settings(declared_missing_values=("XX",)),
        ),
        "floor-of-one": (
            _numbers(60) + [""] * 3 + ["XX"] * 2 + _numbers(12),
            taxonomy.Settings(
                small_cell_floor=1, declared_missing_values=("XX",)
            ),
        ),
        # THE CORNER THE POOLED-REMAINDER WALK HAD TO BE TAUGHT ABOUT
        # (contract 5 C5-N5, C5-S13). At a floor of one nothing may be
        # held back, and both halves of the product find a held-back
        # count by the word it stands under. A table whose cells
        # literally read `(withheld)` publishes that word as a KEY of
        # the spellings map, where it is the table's text and not a
        # pool -- so a guard that read it as a pool would refuse the
        # very description version 5 exists to make writable.
        "pool-word-at-one": (
            _numbers(60) + [_POOL_WORD] * 2,
            taxonomy.Settings(
                small_cell_floor=1, declared_missing_values=(_POOL_WORD,)
            ),
        ),
    }
    for stem, (values, settings) in shapes.items():
        described, column = _describe_beside_a_filler(
            folder, f"shape-{stem}", values, settings
        )
        profile.check_publication(described.document)
        assert column.n_missing_blank >= 0, stem
        assert column.n_missing_withheld >= 0, stem
    _pooled, named = _describe_beside_a_filler(
        folder,
        "shape-pool-word-at-one-again",
        _numbers(60) + [_POOL_WORD] * 2,
        taxonomy.Settings(
            small_cell_floor=1, declared_missing_values=(_POOL_WORD,)
        ),
    )
    assert named.missing_by_source == {_POOL_WORD: 2}
    assert named.n_missing_withheld == 0
    text = _describe(
        folder,
        "shape-text",
        _comments(60, 50) + ["ZZZ"] * 12,
        taxonomy.Settings(declared_missing_values=("ZZZ",)),
        name="note",
    )
    profile.check_publication(text.document)
    assert text.loaded.columns[0].role == taxonomy.ROLE_TEXT
    assert text.loaded.columns[0].n_missing_withheld == 0


# -- what version 5 does NOT close, at the same width ------------------


def test_a_column_that_publishes_no_value_publishes_no_marker(
    folder: pathlib.Path,
) -> None:
    """C5-21, and it is a genuine conflict rather than an omission.

    Publishing the marker word on a free-text column would publish text
    out of a column that exists to publish none, so the source
    accounting is empty there whatever made the cells absent -- and the
    two counts are zero with it, because they are the same accounting
    under two other names.
    """
    document, _path = _built(
        folder,
        "free-text",
        _comments(60, 50) + ["ZZZ"] * 12,
        taxonomy.Settings(declared_missing_values=("ZZZ",)),
        name="note",
    )
    # THE PRODUCER'S OWN DOCUMENT, read before the loader sees it: what
    # this rule is about is what the producer may WRITE.
    block = document["columns"][0]
    assert block["role"] == taxonomy.ROLE_TEXT
    assert block["n_missing"] == 12
    assert block["missing_by_source"] == {}
    assert block["n_missing_blank"] == 0
    assert block["n_missing_withheld"] == 0
    assert "ZZZ" not in canonical.serialize(document)
    described = _describe(
        folder,
        "free-text-again",
        _comments(60, 50) + ["ZZZ"] * 12,
        taxonomy.Settings(declared_missing_values=("ZZZ",)),
        name="note",
    )
    column = described.loaded.columns[0]
    assert column.missing_by_source == {}


def test_a_spelling_below_the_floor_is_published_nowhere(
    folder: pathlib.Path,
) -> None:
    """C5-22, checked over the WHOLE document rather than one field.

    A spelling fewer than `small_cell_floor` cells share is pooled and
    unnamed, in version 5 exactly as in version 4. The check walks every
    string the finished description carries, key and value alike,
    because a field added later is a field this rule has to reach.
    """
    marker = "rarespelling"
    described = _describe(
        folder,
        "below-floor",
        _numbers(60) + [marker] * 3,
        taxonomy.Settings(declared_missing_values=(marker,)),
    )
    column = described.loaded.columns[0]
    assert column.n_missing == 3
    assert column.n_missing_withheld == 3
    assert marker not in canonical.serialize(described.document)
    assert marker not in _summary_of(described)
    assert marker not in _report_of(described)


# -- the analysis's own witnesses, walked one by one --------------------


def test_the_five_witnesses_of_the_analysis_land_where_it_says(
    folder: pathlib.Path,
) -> None:
    """The whole ruling, checked against the cases that produced it.

    The analysis the owner ruled from built six witnesses. Five of them
    are about what a description must carry, and this test asks each one
    the same question: does the description hold enough to rebuild the
    reading rule for that column? Four say yes now, and the fifth says
    no BY DESIGN and is the one contract 5 section 7.1 states as a limit
    no version of this format closes.

    1. A rescued word: 200 readings and one cell of `n/a`, described
       with `--keep-value n/a`. The word is one of this package's own
       ten, so the settings block names the member -- and section 6.4
       proves that is the WHOLE of what a rescue can change.
    2. An invisible character in a named word: the key is the spelling
       character for character, so the two tables that used to describe
       alike do not.
    3. Free text: the source accounting is empty whatever made the cells
       absent, because publishing the marker there would publish text
       out of a column that publishes none. NOT closed, and this is the
       one case where publishing safely and describing completely
       genuinely conflict.
    4. The person's data colliding with this package's own word: the map
       holds one key space, so a key reading `(withheld)` means cells
       held exactly that text and the pooled count is a field of its
       own.
    5. The good case, which always worked: a named marker above the
       floor is published by name, and still is.
    """
    # 1 -- the rescued word.
    rescued = _describe(
        folder,
        "w1",
        _numbers(200) + ["n/a"],
        taxonomy.Settings(kept_values=("n/a",)),
    )
    assert rescued.loaded.settings.kept_values.built_in_texts == ("n/a",)

    # 2 -- the invisible character, and the table that wears its
    # printable form.
    first = _describe(
        folder,
        "w2-raw",
        _numbers(60) + [_RAW] * 12,
        taxonomy.Settings(declared_missing_values=(_RAW,)),
    )
    second = _describe(
        folder,
        "w2-shown",
        _numbers(60) + [_SHOWN] * 12,
        taxonomy.Settings(declared_missing_values=(_SHOWN,)),
    )
    assert first.loaded.columns[0].missing_by_source == {_RAW: 12}
    assert second.loaded.columns[0].missing_by_source == {_SHOWN: 12}
    assert canonical.serialize(first.document) != canonical.serialize(
        second.document
    )

    # 3 -- free text, and it is NOT closed.
    text = _describe(
        folder,
        "w3",
        _comments(60, 50) + ["ZZZ"] * 12,
        taxonomy.Settings(declared_missing_values=("ZZZ",)),
        name="note",
    )
    assert text.loaded.columns[0].missing_by_source == {}
    assert text.loaded.columns[0].n_missing == 12
    assert "ZZZ" not in canonical.serialize(text.document)

    # 4 -- the collision, both halves.
    literal = _describe(
        folder,
        "w4-literal",
        _numbers(60) + [_POOL_WORD] * 12,
        taxonomy.Settings(declared_missing_values=(_POOL_WORD,)),
    )
    rare = _describe(
        folder,
        "w4-rare",
        _numbers(60)
        + ["r1"] * 3 + ["r2"] * 3 + ["r3"] * 3 + ["r4"] * 3,
        taxonomy.Settings(
            declared_missing_values=("r1", "r2", "r3", "r4")
        ),
    )
    assert literal.loaded.columns[0].missing_by_source == {_POOL_WORD: 12}
    assert literal.loaded.columns[0].n_missing_withheld == 0
    assert rare.loaded.columns[0].missing_by_source == {}
    assert rare.loaded.columns[0].n_missing_withheld == 12
    assert canonical.serialize(literal.document) != canonical.serialize(
        rare.document
    )

    # 5 -- the good case, unchanged.
    good = _describe(
        folder,
        "w5",
        _numbers(60) + ["XX"] * 12,
        taxonomy.Settings(declared_missing_values=("XX",)),
    )
    assert good.loaded.columns[0].missing_by_source == {"XX": 12}
    assert good.loaded.columns[0].n_missing_withheld == 0
