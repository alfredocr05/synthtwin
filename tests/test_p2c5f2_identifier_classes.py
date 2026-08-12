"""Review item P2-C5-F2: declared identifiers meet their class counts.

THE OBLIGATION IS THE PLAN'S, AND IT IS EXACT. P2-D6 puts `n_numeric`,
`n_not_numeric`, `n_out_of_range` and `n_contradictory` in the
EXACT-OBSERVABLE column "by class-preserving construction", on every
role; contract 9.2 says the same. This file holds the declared
identifier path to it.

WHY THIS IS THE THIRD FILE ON ONE OBLIGATION, stated so the next
reviewer can see what each closure actually proved:

- round 1 (P2-C1-F1) found the band walk sending every group to the
  figures whenever `all_whole_numbers` was true. The repair packed the
  two published ALPHABET counts over whole groups and proved it on the
  columns the item named;
- round 2 (P2-C2-F1) found the class counts and the alphabet counts
  being walked separately on free text, and the repair packed them
  together THERE. The identifier path kept the alphabet-only walk,
  because G9.6 said its bands read the alphabet counts "and nothing
  else";
- round 4 (P2-C4-F2) reopened the free-text half on the SHAPE -- which
  group carries each published length end -- and closed it with a
  search over shapes. G9.6 again said the search could not reach a
  declared identifier, "because no group's length is an input to it";
- round 5 (P2-C5-F2) found both of those sentences false. A group
  written from an alphabet reads back as whatever the classifier makes
  of it, so an alphabet-only packing READS a class count off a
  construction instead of meeting it; and once the classes are packed a
  group's length IS an input, because one character cannot be a number
  and stand outside the figures at the same time.

So the claim this file makes is the general one, over descriptions the
shipped producer built:

1. the two columns the review item describes, cell for cell;
2. 200 producer-emitted declared-identifier descriptions, generated at
   4 seeds -- 800 runs -- with every present cell reclassified through
   the shipped parser and every one of the six exact counts asserted;
3. the same runs assert `all_whole_numbers`, both published lengths and
   the repetition facts, because the class packing could have bought
   the class counts with any of them;
4. a mutant restoring the alphabet-only band walk, which must put the
   review item's own column back out of reach.
"""

import pathlib
import random

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    parsing,
    profile,
    reading,
    taxonomy,
)

SEEDS = (0, 1, 17, 63)

# How many descriptions the battery builds. The docstring's "200
# descriptions, 800 runs" is this number and the seeds above; a battery
# that quietly shrank would leave every claim here true of nothing, so
# the count is asserted rather than described.
BATTERY_SIZE = 200

# Concrete failure scenario 1 of the review item: a 49-row declared
# identifier whose own five values are a joint exact assignment.
FIRST = ["N_7"] * 13 + ["no!!"] * 5 + ["x-y"] * 8 + ["913"] * 12 + ["-3"] * 11

# Concrete failure scenario 2: five normal numbers, seven text values,
# eleven contradictory values and thirteen out-of-range values.
SECOND = ["7"] * 5 + ["ab"] * 7 + ["(-5)"] * 11 + ["1e999"] * 13

# The alphabet the battery draws letters from, written out here so no
# value in this file comes from anywhere but this file.
LETTERS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"

# The six exact counts a declared identifier owes, by the contract's own
# field names: the four parser classes of 9.2 and the two alphabet
# counts of 9.7.
CLASS_FACTS = (
    ("n_numeric", parsing.NUMBER),
    ("n_not_numeric", parsing.NOT_A_NUMBER),
    ("n_out_of_range", parsing.NUMBER_OUT_OF_RANGE),
    ("n_contradictory", parsing.NUMBER_CONTRADICTORY),
)


def _described(
    folder: pathlib.Path, values: "list[str]"
) -> "tuple[dict, contract.Profile]":
    """Write a one-column table, declare it an identifier, describe, load."""
    path = fixtures.write(
        folder, "table.csv", fixtures.single_column_table("code", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), ["code"])
    target = fixtures.write_profile(folder, "table-profile.json", document)
    return document, contract.load_profile(str(target))


def _a_value(rng: random.Random, length: int) -> str:
    """One made-up identifier of one of the six shapes the battery uses."""
    kind = rng.randrange(6)
    if kind == 0:
        return "".join(
            rng.choice("0123456789") for _step in range(max(length, 1))
        )
    if kind == 1:
        return "".join(
            rng.choice(LETTERS + "0123456789-_")
            for _step in range(max(length, 1))
        )
    if kind == 2:
        return rng.choice("!@#$%^&*") + "".join(
            rng.choice(LETTERS + "!.") for _step in range(max(length - 1, 0))
        )
    if kind == 3:
        return "-" + "".join(
            rng.choice("0123456789") for _step in range(max(length - 1, 1))
        )
    if kind == 4:
        return "".join(
            rng.choice("123456789") for _step in range(max(length - 4, 1))
        ) + "e999"
    return "(-" + "".join(
        rng.choice("0123456789") for _step in range(max(length - 3, 1))
    ) + ")"


def _a_column(seed: int) -> "list[str]":
    """One producer-bound column: groups, fold pairs, and absent cells."""
    rng = random.Random(seed)
    values: list[str] = []
    for _group in range(rng.randrange(2, 9)):
        text = _a_value(rng, rng.randrange(1, 7))
        values = values + [text] * rng.randrange(1, 18)
    if rng.random() < 0.35:
        # Values differing only before the fold, so folded is below raw
        # and the collision path of G9.3 is exercised.
        pool = [
            one for one in sorted(set(values)) if one.lower() != one.upper()
        ]
        for one in pool[: rng.randrange(1, 3)]:
            turned = one.upper() if one.islower() else one.lower()
            values = values + [turned] * rng.randrange(1, 4)
    if rng.random() < 0.25:
        # An all-different column, which is the ordinary key column.
        values = [
            _a_value(rng, rng.randrange(1, 7))
            for _step in range(rng.randrange(4, 40))
        ]
    rng.shuffle(values)
    if rng.random() < 0.2:
        values = values + [""] * rng.randrange(1, 5)
    return values


def _classes(twin: generation.Twin) -> "dict[str, int]":
    """Every present cell of the twin, sorted by the shipped classifier."""
    counted: dict[str, int] = {}
    for cell in twin.columns[0]:
        if cell == "":
            continue
        found = parsing.classify_number(cell)
        counted[found] = counted.get(found, 0) + 1
    return counted


_BUILT: "list[tuple[str, dict, contract.Profile]]" = []


def _battery(
    tmp_path_factory: pytest.TempPathFactory,
) -> "list[tuple[str, dict, contract.Profile]]":
    """The battery, built once per session through the real producer."""
    if _BUILT:
        return _BUILT
    root = tmp_path_factory.mktemp("identifier-battery")
    for seed in range(BATTERY_SIZE):
        here = root / f"case-{seed}"
        here.mkdir()
        document, loaded = _described(here, _a_column(seed))
        if document["columns"][0]["role"] != "identifier":
            continue
        _BUILT.append((f"case-{seed}", document, loaded))
    return _BUILT


# -- 1. the two columns the review item describes ----------------------


def test_the_first_reviewed_column_meets_every_published_count(
    tmp_path: pathlib.Path,
) -> None:
    """Scenario 1: `N_7`, `no!!`, `x-y`, `913`, `-3`.

    The description publishes 23 cells that read as numbers and 26 that
    do not, with the alphabet counts, the occurrence counts and the
    length range beside them, and its own five values are a joint exact
    assignment. Seeds 0 and 63 wrote `n_numeric: 12` and
    `n_not_numeric: 37` and named both.
    """
    document, loaded = _described(tmp_path, FIRST)
    column = document["columns"][0]
    assert column["role"] == "identifier"
    assert column["n_numeric"] == 23
    assert column["n_not_numeric"] == 26
    assert column["n_all_digits"] == 12
    assert column["n_code_alphabet"] == 44
    assert (column["min_length"], column["max_length"]) == (2, 4)

    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        counted = _classes(twin)
        assert counted.get(parsing.NUMBER, 0) == 23, seed
        assert counted.get(parsing.NOT_A_NUMBER, 0) == 26, seed
        assert list(twin.deviations) == [], seed


def test_the_second_reviewed_column_meets_every_published_count(
    tmp_path: pathlib.Path,
) -> None:
    """Scenario 2: `7`, `ab`, `(-5)`, `1e999`.

    Five normal numbers, seven text values, eleven values whose notation
    conflicts with itself and thirteen too large to hold. Seeds 0, 1 and
    63 wrote five numbers and thirty-one text values, with no
    contradictory and no out-of-range cell at all -- so a user checking
    what a pipeline does with an oversized or self-contradicting
    identifier found no such row in the twin.
    """
    document, loaded = _described(tmp_path, SECOND)
    column = document["columns"][0]
    assert column["role"] == "identifier"
    assert column["n_numeric"] == 5
    assert column["n_not_numeric"] == 7
    assert column["n_contradictory"] == 11
    assert column["n_out_of_range"] == 13

    for seed in SEEDS:
        twin = generation.generate(loaded, seed)
        counted = _classes(twin)
        assert counted.get(parsing.NUMBER, 0) == 5, seed
        assert counted.get(parsing.NOT_A_NUMBER, 0) == 7, seed
        assert counted.get(parsing.NUMBER_CONTRADICTORY, 0) == 11, seed
        assert counted.get(parsing.NUMBER_OUT_OF_RANGE, 0) == 13, seed
        assert list(twin.deviations) == [], seed


# -- 2 and 3. the general claim, over a producer battery ---------------


def test_the_battery_is_the_size_this_file_claims(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """The coverage is asserted, not described."""
    cases = _battery(tmp_path_factory)
    assert len(cases) == BATTERY_SIZE, len(cases)
    assert len(cases) * len(SEEDS) == 800
    for _name, document, _loaded in cases:
        assert document["columns"][0]["role"] == "identifier"


def test_every_class_and_alphabet_count_is_written_exactly(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Point 2, over all 800 runs and every present cell.

    The four parser classes are recounted by running the SHIPPED
    classifier over the finished cells, which is what the contract's own
    disposition means, and the two alphabet counts are recounted the
    same way. Not one of the six may move.
    """
    for name, document, loaded in _battery(tmp_path_factory):
        column = document["columns"][0]
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            counted = _classes(twin)
            for field, reading_back in CLASS_FACTS:
                assert counted.get(reading_back, 0) == column[field], (
                    name, seed, field, column[field], counted
                )
            present = [
                parsing.trimmed(cell)
                for cell in twin.columns[0]
                if cell != ""
            ]
            digits = len(
                [one for one in present if one and parsing.is_digit_text(one)]
            )
            code = len(
                [one for one in present if one and parsing.is_code_text(one)]
            )
            assert digits == column["n_all_digits"], (name, seed)
            assert code == column["n_code_alphabet"], (name, seed)


def test_the_class_counts_are_not_bought_with_another_exact_fact(
    tmp_path_factory: pytest.TempPathFactory,
) -> None:
    """Point 3: what the class packing is not allowed to spend.

    Packing the classes moves which alphabet a group takes, which length
    it is written at and which slot carries a fold collision, so the
    facts those decide are recounted here beside the class counts: the
    two published lengths, the whole-number fact, the counts of present
    and absent cells, and the count of different spellings.
    """
    for name, document, loaded in _battery(tmp_path_factory):
        column = document["columns"][0]
        for seed in SEEDS:
            twin = generation.generate(loaded, seed)
            cells = twin.columns[0]
            present = [cell for cell in cells if cell != ""]
            assert len(present) == column["n_present"], (name, seed)
            assert len(cells) - len(present) == column["n_missing"], (
                name, seed
            )
            assert min(len(cell) for cell in present) == (
                column["min_length"]
            ), (name, seed)
            assert max(len(cell) for cell in present) == (
                column["max_length"]
            ), (name, seed)
            whole = True
            for cell in present:
                if parsing.numeric_whole(
                    parsing.trimmed(cell)
                ) != parsing.WHOLE_YES:
                    whole = False
            assert whole == column["all_whole_numbers"], (name, seed)
            assert len(set(present)) == column["n_distinct"], (name, seed)


# -- 4. the mutant that makes the three above mean something -----------


def test_the_alphabet_only_walk_puts_the_reviewed_column_back(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Mutant: pack the alphabets alone, as revision 2's G9.6 said to.

    `_identifier_families` reverted to a single-margin packing over the
    three bands, with every group permitted every band and the ends on
    the description's own first two groups, is exactly the rule round 5
    found. The reviewed column must then miss a class count again -- if
    it does not, nothing in this file is proving anything about the
    joint packing.
    """
    document, loaded = _described(tmp_path, FIRST)
    assert _classes(generation.generate(loaded, 0)).get(
        parsing.NUMBER, 0
    ) == 23

    def alphabets_alone(column, facts, groups, folded, partners):
        """The band packing of revision 2, and its class-free reading."""
        quotas = [
            facts.n_all_digits,
            facts.n_code_alphabet - facts.n_all_digits,
            column.n_present - facts.n_code_alphabet,
        ]
        permitted = [
            generation._every_bucket(len(generation._BANDS))
            for _each in groups
        ]
        chosen = generation._allocation(groups, quotas, permitted)
        width = len(generation._BANDS)
        text = generation._CLASSES.index(generation._CLASS_TEXT)
        return (
            [text * width + place for place in chosen],
            generation._FIRST_TWO,
        )

    monkeypatch.setattr(
        generation, "_identifier_families", alphabets_alone
    )
    counted = _classes(generation.generate(loaded, 0))
    assert counted.get(parsing.NUMBER, 0) != 23, counted
    assert document["columns"][0]["n_numeric"] == 23
