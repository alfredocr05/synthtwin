"""Owner ruling of 2026-09-17, item 1: a record number's literal prefix.

THE GAP LANDING 2b.15 MEASURED. A declared identifier published the
LAYOUT of its values -- which kind of character stood at each position --
and never a letter of them, so `P00123` came back `X17879` and
`REC1234567` came back `FPQ7317879`. On 800 rows `^P\\d{5}$` matched 800
real cells and 30 twin cells, `^REC\\d{7}$` 800 and 0, `^ABC-\\d{4}$` 800
and 0, and both files passed their own description at exit 0.

THE RULING. Where every present cell of a declared identifier opens with
the same literal prefix and the column clears the smallest group size,
the prefix is published and the twin writes it (contract 7.12a, plan
P4-D202); invariants I3 and F3 are amended for that case only. Where the
column holds two layouts each wearing its own prefix -- `REC` and seven
figures beside `E` and six -- each named layout publishes its own, which
is this version's reading of the ruling and is flagged to the owner.

Every shape is a ROUND TRIP: the table is described, a twin built, the
twin described again, and BOTH files validated at exit 0 -- beside a
pattern and a starts-with test written against the twin and run
unchanged on the table, which is the ruling's whole point. The rules
that keep the prefix from saying more than the ruling allows are pinned
beside them, each with the shape that would break it.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import pathlib
import random
import re

import pytest

from synthtwin import contract
from synthtwin import errors
from synthtwin import parsing
from tests import fixtures
from tests.test_landing_2b18_identifier_layout import _round_trip

ROWS = 800


def _prefixed_five(seed: int) -> "list[str]":
    draw = random.Random(seed)
    return [f"P{draw.randrange(0, 100000):05d}" for _row in range(ROWS)]


def _record_numbers(seed: int) -> "list[str]":
    draw = random.Random(seed)
    return [f"REC{draw.randrange(1000000, 9999999)}" for _row in range(ROWS)]


def _site_codes(seed: int) -> "list[str]":
    draw = random.Random(seed)
    return [f"ABC-{draw.randrange(1000, 9999)}" for _row in range(ROWS)]


def _two_systems(seed: int) -> "list[str]":
    draw = random.Random(seed)
    built = []
    for _row in range(ROWS):
        if draw.random() < 0.70:
            built += [f"REC{draw.randrange(1000000, 9999999)}"]
        else:
            built += [f"E{draw.randrange(100000, 999999)}"]
    return built


def _matching(values: "list[str]", pattern: str) -> int:
    rule = re.compile(pattern)
    return len([value for value in values if rule.fullmatch(value)])


def _opening(values: "list[str]", prefix: str) -> int:
    return len([value for value in values if value[: len(prefix)] == prefix])


@pytest.mark.parametrize(
    "name,build,pattern,prefix",
    [
        ("prefixed-five", _prefixed_five, r"P\d{5}", "P"),
        ("record-numbers", _record_numbers, r"REC\d{7}", "REC"),
        ("site-codes", _site_codes, r"ABC-\d{4}", "ABC-"),
    ],
)
@pytest.mark.parametrize("floor", [None, 11])
def test_a_prefix_every_cell_shares_is_published_and_written(
    name: str,
    build: object,
    pattern: str,
    prefix: str,
    floor: "int | None",
    tmp_path: pathlib.Path,
) -> None:
    """The ruling's own case, on landing 2b.15's three shapes.

    Mutation: with `generation._templated_facts` answering the description
    unchanged, the twin's letters are filled from the step and the pattern
    matches nought or thirty twin cells, and the twin misses
    `prefix.(column)` at exit 3.
    """
    assert callable(build)
    cells = build(5)
    got = _round_trip(tmp_path / f"{name}-{floor}", cells, floor=floor)
    assert got["source"]["layout_prefixes"] == {"(column)": prefix}
    assert got["twin_profile"]["layout_prefixes"] == {"(column)": prefix}
    assert got["twin_profile"]["layout_forms"] == got["source"]["layout_forms"]
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    twin = got["cells"]
    assert _matching(twin, pattern) == _matching(cells, pattern) == ROWS
    assert _opening(twin, prefix) == _opening(cells, prefix) == ROWS
    # ...and the made-up values stay as different as the table's.
    assert len(set(twin)) == len(set(cells))


def test_two_layouts_each_publish_their_own_prefix(
    tmp_path: pathlib.Path,
) -> None:
    """The per-layout reading, flagged to the owner (contract C6-140).

    No prefix is shared by the whole column, so each named layout
    publishes the prefix its own cells share, and the twin writes each
    layout's cells with it. Before the ruling `^(REC\\d{7}|E\\d{6})$`
    matched 800 real cells and 9 twin cells.
    """
    cells = _two_systems(5)
    got = _round_trip(tmp_path / "two", cells, floor=11)
    assert got["source"]["layout_prefixes"] == {
        "@%%%%%%": "E",
        "@@@%%%%%%%": "REC",
    }
    assert got["twin_profile"]["layout_prefixes"] == (
        got["source"]["layout_prefixes"]
    )
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    twin = got["cells"]
    pattern = r"REC\d{7}|E\d{6}"
    assert _matching(twin, pattern) == _matching(cells, pattern) == ROWS
    for prefix in ("REC", "E"):
        assert _opening(twin, prefix) == _opening(cells, prefix)


def test_a_prefix_a_few_rows_write_otherwise_is_not_published(
    tmp_path: pathlib.Path,
) -> None:
    """The disclosure rule, asked of the prefix (contract C6-140).

    796 cells of `P` and five figures beside four of `Q` and seven: the
    column shares no prefix, the four are pooled at a floor of eleven, and
    the layout `@%%%%%` holds only `P` cells. Publishing `P` for that
    layout would say that the present cells not opening with `P` number
    four -- a group under the smallest group size -- so it is not
    published.

    Mutation: with `parsing.prefix_nameable` answering True the source
    publishes `{"@%%%%%": "P"}`.
    """
    cells = _prefixed_five(6)
    draw = random.Random(16)
    for place in range(4):
        cells[100 * place] = f"Q{draw.randrange(1000000, 9999999)}"
    got = _round_trip(tmp_path / "few-otherwise", cells, floor=11)
    assert got["source"]["layout_forms"] == {"(withheld)": 4, "@%%%%%": 796}
    assert got["source"]["layout_prefixes"] == {}
    assert got["twin_exit"] == 0 and got["real_exit"] == 0


def test_the_rules_that_keep_a_prefix_a_prefix() -> None:
    """C6-139's four cuts, each on the shape that would break it.

    Mutation: dropping any one cut publishes the text beside it.
    """
    plain = parsing.LAYOUT_PLAIN
    # (1) no figure: the noughts of `P00123` are part of the number.
    assert parsing.literal_prefix(["P00123", "P00456"], plain) == "P"
    # (2) a figure or a letter of every value stands after it, so no value
    # is published whole even beside the marks its layout names.
    assert parsing.literal_prefix(["no##", "no##", "no##"], plain) == ""
    # (3) no half a run of letters.
    assert parsing.literal_prefix(["REC1", "MRX2"], plain) == ""
    assert parsing.literal_prefix(["ST-A123", "ST-B456"], plain) == "ST-"
    # (4) only characters a layout carries as they are, and a letter.
    assert parsing.literal_prefix(["Né-1", "Né-2"], plain) == ""
    assert parsing.literal_prefix(["{A1}", "{B2}"], plain) == ""
    # ...and rule (3) asked of a hexadecimal column's own figures, where
    # every letter is one of them (plan P4-D233): `ab` is half a number,
    # and a prefix there always ends in a mark.
    hexadecimal = parsing.LAYOUT_HEX_LOWER
    assert parsing.literal_prefix(["ab12", "ab34"], hexadecimal) == ""
    assert parsing.literal_prefix(["DE-a1b2", "DE-c3d4"], hexadecimal) == "DE-"


def test_a_file_not_opening_with_the_prefix_misses_it(
    tmp_path: pathlib.Path,
) -> None:
    """The obligation can fail: a file of the right layout without the prefix.

    The description of `P` and five figures is checked against a file of
    `Q` and five figures: every layout count holds, and `prefix.(column)`
    is MISSED at exit 3 without printing the prefix or the count.
    """
    from tests.test_stage2_round_trip import _exit_of

    cells = _prefixed_five(7)
    got = _round_trip(tmp_path / "source", cells, floor=11)
    assert got["real_exit"] == 0
    wrong = tmp_path / "wrong.csv"
    source = (tmp_path / "source" / "real.csv").read_text(encoding="utf-8")
    wrong.write_text(source.replace("\nP", "\nQ"), encoding="utf-8", newline="")
    checked = tmp_path / "checked"
    checked.mkdir()
    code = _exit_of(
        [
            "validate", str(tmp_path / "source" / "real-profile.json"),
            "--twin", str(wrong), "--out-dir", str(checked), "--replace",
        ]
    )
    assert code == 3
    report = next(checked.glob("*quality*")).read_text(encoding="utf-8")
    assert "prefix.(column) [identifier.layout_prefixes]: MISSED" in report
    assert "forms.published.@%%%%%" in report


def test_what_the_pooled_walk_still_writes_is_named() -> None:
    """The limit C6-142 states, pinned with its numbers.

    790 `P` and five figures beside ten `P` and six at a floor of eleven:
    the six-figure cells are pooled, the band walk writes them, and the
    prefix is overwritten onto them -- all 800 twin cells open with `P`,
    both files validate at exit 0 -- but `^P\\d{5,6}$` matches 790 twin
    cells against 800, because the walk's own shapes are not figures.
    """
    import tempfile

    draw = random.Random(7)
    cells = [f"P{draw.randrange(0, 100000):05d}" for _row in range(790)] + [
        f"P{draw.randrange(0, 1000000):06d}" for _row in range(10)
    ]
    with tempfile.TemporaryDirectory() as folder:
        got = _round_trip(pathlib.Path(folder) / "pooled", cells, floor=11)
    assert got["source"]["layout_prefixes"] == {"(column)": "P"}
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    assert _opening(got["cells"], "P") == ROWS
    assert _matching(got["cells"], r"P\d{5,6}") == 790
    assert _matching(cells, r"P\d{5,6}") == ROWS


def test_a_hand_edited_prefix_is_refused_without_quoting_it(
    tmp_path: pathlib.Path,
) -> None:
    """The loader checks the one text the block carries (C6-141).

    A prefix holding a figure is text `parsing.literal_prefix` never
    writes; the refusal names the key and does not print the text.

    Mutation: with the check of `parsing.is_a_literal_prefix` withdrawn
    from `contract._layout_prefixes`, the document loads.
    """
    import json

    cells = _prefixed_five(8)
    got = _round_trip(tmp_path / "source", cells, floor=11)
    assert got["source"]["layout_prefixes"] == {"(column)": "P"}
    path = tmp_path / "source" / "real-profile.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["columns"][0]["layout_prefixes"] = {"(column)": "PQ7"}
    edited = fixtures.write_profile(tmp_path, "edited.json", document)
    with pytest.raises(errors.ProfileError) as raised:
        contract.load_profile(str(edited))
    spoken = f"{raised.value}"
    assert "layout_prefixes" in spoken, spoken
    assert "PQ7" not in spoken, spoken
    assert not parsing.is_a_literal_prefix("@R")
    assert not parsing.is_a_literal_prefix(" R")
    assert parsing.is_a_literal_prefix("AB ")


def test_a_partner_keeps_the_prefix_where_its_family_allows(
    tmp_path: pathlib.Path,
) -> None:
    """Method G9.6a step 5, and the one partner it cannot reach, named.

    750 record numbers of `REC` and seven figures, and fifty of them
    again with a trailing space: the column publishes `(column)` `REC`,
    and the twin owes fifty fold-collision partners. A case flip of a
    parent is `rEC...`, so the edge-spaced member is taken first, and 799
    of 800 twin cells open with `REC`. The one that does not is the
    partner pinned to the published longest length, where only a case
    flip fits; the twin's report names it under `layout_prefixes`, and the
    twin misses at exit 3 -- as it already did on the layout count
    before the ruling, on this very shape.

    Mutation: with the partner walk handed no prefixes, the case flips
    come first and 750 twin cells open with `REC`.
    """
    draw = random.Random(9)
    base = [f"REC{draw.randrange(1000000, 9999999)}" for _row in range(750)]
    cells = base + [value + " " for value in base[:50]]
    got = _round_trip(tmp_path / "partners", cells, floor=11)
    assert got["source"]["layout_prefixes"] == {"(column)": "REC"}
    assert got["real_exit"] == 0
    assert _opening(got["cells"], "REC") == ROWS - 1
    report = (tmp_path / "partners" / "real-twin-report.txt").read_text(
        encoding="utf-8"
    )
    assert "layout_prefixes.(column)" in report
    assert got["twin_exit"] == 3


def test_a_template_is_worn_only_with_its_letters_and_no_mix_takes_a_named_layout() -> None:
    """Method G9.6a steps 2 and 3, asked of the generator's own predicates.

    Neither is reached by a column the round trips above describe, so
    each is pinned where it is decided. A cell of the layout `@@@-%%%%`
    that does not hold `ABC` does not wear the template `ABC-%%%%`. And
    of two layouts published with their own prefixes, `ST` for `@@-@%%%`
    and `XY` for `@@-%%%%`, the pooled cells' first mix over `ST-@%%%` is
    `ST-%%%%`, whose layout is the named `@@-%%%%`: a cell written to it
    would be counted into that layout without its prefix, so the mix is
    stepped over.

    Mutation: without the letter test `XYZ-1234` wears `ABC-%%%%`; without
    the named-layout test the stand-in is `ST-` and four figures.
    """
    from synthtwin import generation

    plain = parsing.LAYOUT_PLAIN
    assert generation._wears_template("ABC-1234", "ABC-%%%%", plain)
    assert not generation._wears_template("XYZ-1234", "ABC-%%%%", plain)
    facts = contract.IdentifierFacts(
        min_length=7,
        max_length=7,
        all_whole_numbers=False,
        n_all_digits=0,
        n_code_alphabet=800,
        n_distinct_by_occurrences={"1": 800},
        layout_forms={"@@-@%%%": 400, "@@-%%%%": 390, "(withheld)": 10},
        layout_prefixes={"@@-@%%%": "ST", "@@-%%%%": "XY"},
    )
    templated = generation._templated_facts(facts)
    assert sorted(templated.layout_forms) == [
        "(withheld)", "ST-@%%%", "XY-%%%%",
    ]
    stand_in = generation._layout_stand_in(
        generation._CLASS_TEXT,
        generation._BAND_CODE,
        (7, 7),
        plain,
        templated,
        generation._layout_stand_in_bases(templated),
        {},
        {},
        {},
        {},
    )
    assert stand_in is not None
    assert parsing.layout_form(stand_in, plain) not in facts.layout_forms
