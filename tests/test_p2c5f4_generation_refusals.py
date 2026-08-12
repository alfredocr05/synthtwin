"""The two descriptions the ratified plan says to REFUSE (P2-C5-F4).

Plan P2-D6's feasibility rule 5 is the sentence under test: "Refusal is
reserved for documents no rule above can satisfy, and is a refusal of
GENERATION, never a claim that the profile is invalid: the message says
the profile is valid, names the two facts that cannot both hold, and
gives remediation that does not assume the person holds the table."

Until this file existed, two such descriptions were GENERATED instead --
a twin was written, the exact fact was recounted as missed, and a line
of the report named it. That is the inverse of the usual defect and it
is worse than an unnecessary stop: the person receives a twin the plan
says they were never to get, and nothing in the run tells them the
description was one no table can hold.

The two are the ones round 5 named:

1. a producer profile for twenty-two one-character declared record
   numbers in two groups, with `all_whole_numbers` alone edited to true
   while an alphabet count still requires a value outside the figures;
2. twelve distinct three-character, two-word free-text values with
   `words.max` alone edited from 2 to 3.

Each is built by the REAL producer from a seeded neutral table and then
edited at ONE key, so what is exercised is a genuine description with a
hand edit in it -- which is the only way either pair can arise, since no
table produces either.

Four things are asserted for each: that generation is refused, that the
message is the one the plan fixes, that the command leaves the folder
exactly as it found it, and that the refusal is NARROW -- the same
description without the edit, and the nearest description in which the
two facts CAN both hold, are generated as before. The last of those is
what stops a refusal from being a way to avoid building anything, and a
producer battery at the end counts how many descriptions still generate.
"""

import json
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
    taxonomy,
)
from synthtwin.cli import main

Document = dict[str, typing.Any]


# -- producer-built descriptions, edited at one key -------------------


def _document(
    folder: pathlib.Path, text: str, declared: "list[str] | None" = None
) -> Document:
    """The producer's own description of a seeded neutral table."""
    path = fixtures.write(folder, "table.csv", text)
    table = reading.read_table(str(path))
    built = profile.build_document(
        table, taxonomy.Settings(), declared if declared else []
    )
    return typing.cast(Document, json.loads(json.dumps(built)))


def _write(folder: pathlib.Path, document: Document, stem: str) -> pathlib.Path:
    """Write a description exactly as `synthtwin profile` writes one."""
    target = folder / f"{stem}-profile.json"
    target.write_text(
        canonical.serialize(document), encoding="utf-8", newline="\n"
    )
    return target


def _loaded(folder: pathlib.Path, document: Document, stem: str = "edited"):
    """Load a description from the bytes of a file, as the command does."""
    return contract.load_profile(str(_write(folder, document, stem)))


def _identifier_table() -> str:
    """Twenty-two one-character record numbers in two equal groups."""
    return fixtures.single_column_table("code", ["a"] * 11 + ["7"] * 11)


def _two_word_table() -> str:
    """Twelve different three-character values, two words in each."""
    pairs = [
        f"{first} {second}"
        for first, second in zip("abcdefghijkl", "mnopqrstuvwx")
    ]
    return fixtures.single_column_table("note", pairs)


def _column(document: Document, name: str) -> Document:
    for block in document["columns"]:
        if block["name"] == name:
            return typing.cast(Document, block)
    raise AssertionError(f"the description has no column named {name}")


# -- what the plan requires every one of these messages to say --------


def _speaks_the_plan(message: str, column: str, facts: "tuple[str, ...]") -> None:
    """P2-D6 rule 5, checked clause by clause on the message itself."""
    assert "is valid" in message, message
    assert f"'{parsing.visible(column)}'" in message, message
    assert "cannot build a twin column from it" in message, message
    for said in facts:
        assert said in message, (said, message)
    assert "Nothing has been written" in message, message
    # Remediation the person can carry out WITHOUT the table, which is
    # the clause four repairs kept losing. The description file is what
    # they are holding, so it is what the message reaches for first.
    assert "description file is all synthtwin needs" in message, message
    assert "neither edit asks you for the table" in message, message
    # ...and the table is still offered to the people who do have it.
    assert "synthtwin profile" in message, message


# -- case 1: one-character record numbers published as whole numbers --


def test_one_character_whole_number_identifiers_refuse_generation(
    tmp_path: pathlib.Path,
) -> None:
    """Failure scenario 1 of review item P2-C5-F4.

    One character that reads as a whole number IS a figure, so a
    description saying every value is a whole number and that eleven of
    twenty-two are not written in figures alone is a description no
    table can hold. It used to be generated, with `all_whole_numbers`
    named as missed.
    """
    document = _document(tmp_path, _identifier_table(), ["code"])
    block = _column(document, "code")
    assert block["role"] == "identifier"
    assert block["max_length"] == 1
    assert block["n_all_digits"] == 11
    assert block["n_present"] == 22
    assert block["all_whole_numbers"] is False
    block["all_whole_numbers"] = True
    described = _loaded(tmp_path, document)
    with pytest.raises(errors.ProfileError) as raised:
        generation.plan_generation(described)
    _speaks_the_plan(
        f"{raised.value}",
        "code",
        ("every value reads as a whole number", "11 of the 22 values"),
    )


def test_a_one_character_shortest_value_with_no_figures_refuses(
    tmp_path: pathlib.Path,
) -> None:
    """The same proof from the other end of the length range.

    Where the SHORTEST published length is one character and NONE of the
    values is written in figures alone, the value carrying that length
    would have to be a one-character whole number -- which is a figure.
    The pair is decided by the published numbers, not by any walk.
    """
    document = _document(
        tmp_path,
        fixtures.single_column_table("code", ["a"] * 9 + ["bb"] * 9),
        ["code"],
    )
    block = _column(document, "code")
    assert block["min_length"] == 1
    assert block["n_all_digits"] == 0
    block["all_whole_numbers"] = True
    described = _loaded(tmp_path, document)
    with pytest.raises(errors.ProfileError) as raised:
        generation.plan_generation(described)
    _speaks_the_plan(
        f"{raised.value}",
        "code",
        (
            "every value reads as a whole number",
            "none of the 18 values is written in figures alone",
        ),
    )


def test_the_whole_number_refusal_is_narrow(tmp_path: pathlib.Path) -> None:
    """A description one character wider is BUILT, not refused.

    Two characters carry `1.` and three carry `1e0`, so the moment the
    published range leaves a whole-number spelling outside the figures
    the description is one a rule can meet -- and a refusal there would
    be a stop nobody asked for. The unedited description is built too.
    """
    document = _document(tmp_path, _identifier_table(), ["code"])
    plain = _loaded(tmp_path, document, "plain")
    assert generation.generate(plain, 0).columns

    widened = _document(
        tmp_path,
        fixtures.single_column_table("code", ["ab"] * 11 + ["70"] * 11),
        ["code"],
    )
    block = _column(widened, "code")
    assert block["max_length"] == 2
    block["all_whole_numbers"] = True
    built = generation.generate(_loaded(tmp_path, widened, "wide"), 0)
    assert built.columns


# -- case 2: more words than the published length can hold ------------


def test_more_words_than_the_longest_value_can_hold_refuses(
    tmp_path: pathlib.Path,
) -> None:
    """Failure scenario 2 of review item P2-C5-F4.

    Three characters hold at most two space-separated words, so a
    description publishing three words in a column no value of which is
    longer than three characters is one no table can hold. It used to be
    generated, with the word count brought down and `words.max` named as
    missed.
    """
    document = _document(tmp_path, _two_word_table())
    block = _column(document, "note")
    assert block["role"] == "free_text"
    assert block["length"] == {"min": 3, "max": 3, "mean": 3.0, "p50": 3.0}
    assert block["words"]["max"] == 2
    block["words"]["max"] = 3
    described = _loaded(tmp_path, document)
    with pytest.raises(errors.ProfileError) as raised:
        generation.plan_generation(described)
    _speaks_the_plan(
        f"{raised.value}",
        "note",
        (
            "the largest number of words in a value is 3",
            "no value is longer than 3 characters",
            "holds at most 2 words",
            "3 words need 5 characters",
        ),
    )


def test_a_word_floor_the_shortest_value_cannot_reach_refuses(
    tmp_path: pathlib.Path,
) -> None:
    """The same proof at the other end: `words.min` against `length.min`.

    `words.min` is a floor under EVERY value, so the value carrying the
    shortest published length has to reach it too.
    """
    # Twelve five-character values of three words each, and one value of
    # two characters: the average word count stays above two, so the
    # loader's own F1 rule accepts the edited floor and the pair reaches
    # the feasibility stage, which is where it has to be settled.
    document = _document(
        tmp_path,
        fixtures.single_column_table(
            "note",
            [
                f"{one} {two} {three}"
                for one, two, three in zip("abcdefghijkl", "mnopqrstuvwx", "ABCDEFGHIJKL")
            ]
            + ["yz"],
        ),
    )
    block = _column(document, "note")
    assert block["role"] == "free_text"
    assert block["length"]["min"] == 2
    assert block["words"]["min"] == 1
    block["words"]["min"] = 2
    described = _loaded(tmp_path, document)
    with pytest.raises(errors.ProfileError) as raised:
        generation.plan_generation(described)
    _speaks_the_plan(
        f"{raised.value}",
        "note",
        (
            "no value holds fewer than 2 words",
            "the shortest value is 2 characters long",
            "holds at most one word",
        ),
    )


def test_the_word_refusal_is_narrow(tmp_path: pathlib.Path) -> None:
    """A description whose own lengths carry its word counts is BUILT.

    Five characters hold three words, so the same edit on a column of
    five-character values is a description a rule can meet and the run
    goes on to build it. The unedited description is built too.
    """
    document = _document(tmp_path, _two_word_table())
    plain = _loaded(tmp_path, document, "plain")
    assert generation.generate(plain, 0).columns

    wider = _document(
        tmp_path,
        fixtures.single_column_table(
            "note",
            [f"{one}{one} {two}{two}" for one, two in zip("abcdef", "ghijkl")],
        ),
    )
    block = _column(wider, "note")
    assert block["length"]["max"] == 5
    assert block["words"]["max"] == 2
    block["words"]["max"] = 3
    built = generation.generate(_loaded(tmp_path, wider, "wide"), 0)
    assert built.columns


# -- nothing reaches the disk on a refused run ------------------------


@pytest.mark.parametrize("case", ["identifier", "free_text"])
def test_a_refused_run_writes_no_twin_and_no_report(
    tmp_path: pathlib.Path, case: str, capsys: pytest.CaptureFixture[str]
) -> None:
    """The command stops with nothing written, at every seed it is given.

    The closure check round 5 wrote for this item: no output is
    committed. The folder is listed before and after, so a working file
    left behind would fail this as loudly as a twin would.
    """
    if case == "identifier":
        document = _document(tmp_path, _identifier_table(), ["code"])
        _column(document, "code")["all_whole_numbers"] = True
    else:
        document = _document(tmp_path, _two_word_table())
        _column(document, "note")["words"]["max"] = 3
    description = _write(tmp_path, document, "table")
    before = sorted(path.name for path in tmp_path.iterdir())
    for seed in ("0", "17", "63"):
        assert main(["generate", f"{description}", "--seed", seed]) == 1
        spoken = capsys.readouterr()
        assert "is valid" in spoken.err, spoken.err
        assert sorted(path.name for path in tmp_path.iterdir()) == before
    assert not (tmp_path / "table-twin.csv").exists()
    assert not (tmp_path / "table-twin-report.txt").exists()


# -- and the descriptions a producer writes are still all built -------


def _battery(folder: pathlib.Path) -> "list[tuple[str, contract.Profile]]":
    """Producer descriptions across the roles the two refusals reach.

    Every one is emitted by the Phase 1 producer from a seeded neutral
    table, so each is a description of a table that exists -- which is
    exactly the set no refusal may reach, since a real table's own
    values are a witness that its published facts can all hold.
    """
    cases: list[tuple[str, str, list[str]]] = [
        ("every role", fixtures.every_role_table(), ["record_code"]),
        (
            "one-character record numbers",
            _identifier_table(),
            ["code"],
        ),
        (
            "whole-number record numbers, two characters",
            fixtures.single_column_table("code", ["1."] * 11 + ["7"] * 11),
            ["code"],
        ),
        (
            "whole-number record numbers, three bands",
            fixtures.single_column_table(
                "code", ["1."] * 5 + ["2e0"] * 6 + ["3"] * 7
            ),
            ["code"],
        ),
        (
            "record numbers of mixed width",
            fixtures.single_column_table(
                "code",
                [f"N_{index}" for index in range(13)]
                + ["no!!"] * 5
                + ["x-y"] * 8
                + ["913"] * 12
                + ["-3"] * 11,
            ),
            ["code"],
        ),
        ("two-word free text", _two_word_table(), []),
        (
            "one-word free text",
            fixtures.single_column_table(
                "note", [f"note{index}" for index in range(24)]
            ),
            [],
        ),
        (
            "free text of many widths",
            fixtures.single_column_table(
                "note",
                [
                    " ".join(["w" * (index % 4 + 1)] * (index % 3 + 1))
                    for index in range(30)
                ],
            ),
            [],
        ),
        (
            "free text with a long tail",
            fixtures.single_column_table(
                "note",
                [f"line {index} of the note" for index in range(18)]
                + [f"x{index}" for index in range(6)],
            ),
            [],
        ),
        (
            "numbers too large to hold",
            fixtures.single_column_table(
                "value",
                ["9" * 320, "-" + "9" * 320, "0." + "0" * 400 + "1"] * 9,
            ),
            [],
        ),
        (
            "labels and whole numbers",
            fixtures.rows_to_csv(
                ["region", "visits"],
                [
                    [fixtures.REGIONS[index % 4], f"{index % 7}"]
                    for index in range(48)
                ],
            ),
            [],
        ),
    ]
    built: list[tuple[str, contract.Profile]] = []
    for index, (name, text, declared) in enumerate(cases):
        here = folder / f"case{index}"
        here.mkdir()
        document = _document(here, text, declared)
        built.append((name, _loaded(here, document, f"case{index}")))
    return built


def test_no_description_a_producer_wrote_is_refused(
    tmp_path: pathlib.Path,
) -> None:
    """The count that says the two refusals cost nothing legitimate.

    Eleven producer descriptions at three seeds: every one of the
    thirty-three runs has to produce a twin, and any refusal at all
    fails this test with the description that caused it named.
    """
    battery = _battery(tmp_path)
    assert len(battery) == 11
    generated = 0
    refused: list[str] = []
    for name, described in battery:
        for seed in (0, 17, 63):
            try:
                twin = generation.generate(described, seed)
            except errors.ProfileError as raised:
                refused.append(f"{name} at seed {seed}: {raised}")
                continue
            assert len(twin.columns) == len(described.columns)
            generated += 1
    assert refused == []
    assert generated == 33


def test_the_battery_reaches_the_two_stages_that_now_refuse(
    tmp_path: pathlib.Path,
) -> None:
    """A battery that never reached either check would prove nothing.

    So the two shapes are asserted to be present in it: a declared
    identifier published as whole numbers, and a column of free text
    whose values hold more than one word.
    """
    battery = _battery(tmp_path)
    whole = 0
    worded = 0
    for _name, described in battery:
        for column in described.columns:
            facts = column.facts
            if isinstance(facts, contract.IdentifierFacts):
                whole += 1 if facts.all_whole_numbers else 0
            if isinstance(facts, contract.TextFacts):
                worded += 1 if facts.words.maximum > 1 else 0
    assert whole >= 2, whole
    assert worded >= 2, worded
