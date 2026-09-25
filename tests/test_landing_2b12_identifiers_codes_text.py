"""Landing 2b.12: identifiers and codes keep their shape.

Every shape here is one the spelling audit or the review of landing 2b.8
measured, written as it was measured there, and each is a ROUND TRIP:
the table is described, a twin is built, the twin is described AGAIN,
and both the twin and the real table are validated. The fact the item
was about is asserted directly -- the spelling that comes back, the
count it comes back at -- rather than a proxy for it, because every one
of these defects passed the checks that were being made at the time.

The audit's own numbers are in each docstring, so a regression says
what it broke.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import json
import pathlib
import random

import pytest

from synthtwin import parsing


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    flags: "tuple[str, ...]" = (),
    seed: str = "4",
    by_command: bool = True,
) -> "tuple[dict, dict, list[str], int, int]":
    """Describe, build, describe again, validate the twin AND the table.

    A SECOND COLUMN STANDS BESIDE THE ONE UNDER TEST, and it is not
    decoration: a ONE-column table holding an empty cell is refused,
    because nothing in a CSV tells a blank line apart from a record
    whose one value is missing. That refusal is landing 2b.8's named
    limit (plan P4-D74) and every shape here holds absent cells, so the
    filler is what lets the shape be measured at all. It is the same
    helper `test_landing_2b8_labels_text_missing.py` uses, for the same
    reason.

    ``by_command`` FALSE DESCRIBES WITH THE PRODUCER (plan P4-D341).
    `synthtwin profile` refuses a table under the population floor and
    writes nothing, and a shape whose ROLE depends on the table's ROW
    count -- the categorical ceiling is a share of them -- becomes a
    different shape if it is padded up to that floor. `build_document`
    refuses no table for its size, so such a shape is described that
    way and its twin is still built and checked through `generate` and
    `validate`.
    """
    import csv
    import io

    from tests import fixtures
    from tests.test_stage2_round_trip import _exit_of

    folder.mkdir(parents=True, exist_ok=True)
    rows = [[cells[index], f"row{index}"] for index in range(len(cells))]
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value", "other"], rows),
        encoding="utf-8",
        newline="",
    )
    from tests.test_stage2_round_trip import describe_with_the_producer

    described = ["profile", str(table), "--out-dir", str(folder), "--replace"]
    profile_path = folder / "real-profile.json"
    if by_command:
        assert _exit_of(described + list(flags)) == 0
    else:
        describe_with_the_producer(table, profile_path, flags)
    assert _exit_of([
        "generate", str(profile_path), "--out-dir", str(folder),
        "--seed", seed, "--replace",
    ]) == 0
    twin = folder / "real-twin.csv"
    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    if by_command:
        assert _exit_of(
            ["profile", str(copied), "--out-dir", str(again), "--replace"]
            + list(flags)
        ) == 0
    else:
        describe_with_the_producer(
            copied, again / "twin-profile.json", flags
        )
    first = json.loads(profile_path.read_text(encoding="utf-8"))["columns"][0]
    second = json.loads(
        (again / "twin-profile.json").read_text(encoding="utf-8")
    )["columns"][0]
    written = [
        row[0]
        for row in csv.reader(
            io.StringIO(twin.read_text(encoding="utf-8")), strict=False
        )
    ][1:]
    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of([
        "validate", str(profile_path), "--twin", str(twin),
        "--out-dir", str(checked), "--replace",
    ])
    real_checked = folder / "check-real"
    real_checked.mkdir()
    real_exit = _exit_of([
        "validate", str(profile_path), "--twin", str(table),
        "--out-dir", str(real_checked), "--replace",
    ])
    return first, second, written, twin_exit, real_exit


def _counted(cells: "list[str]") -> "dict[str, int]":
    seen: "dict[str, int]" = {}
    for cell in cells:
        seen[cell] = (seen[cell] if cell in seen else 0) + 1
    return seen


# -- P4-D85: a column publishing no value still names synthtwin's words --


def _notes_with_absent_words(seed: int) -> "list[str]":
    """The audit's LTM-2 column: prose beside `NA`, `N/A` and blanks."""
    draw = random.Random(seed)
    words = ("review", "pending", "checked", "repeat", "sample", "result")
    built: "list[str]" = []
    for _row in range(500):
        pick = draw.random()
        if pick < 0.20:
            built += ["N/A"]
        elif pick < 0.38:
            built += ["NA"]
        elif pick < 0.55:
            built += [""]
        else:
            built += [
                " ".join(
                    draw.choice(words) for _word in range(draw.randrange(2, 5))
                )
            ]
    return built


@pytest.mark.parametrize("seed", [201, 302, 411])
def test_a_free_text_column_keeps_the_words_its_holes_wore(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """LTM-2, the commonest shape: a note column with `NA` and `N/A`.

    Measured before this landing, at two source seeds and two generate
    seeds: `missing_by_source` was `{}`, both absence counts were 0, the
    twin wrote 275 empty cells where the table wrote 101, and the REAL
    TABLE failed its own description at exit 3 -- `presence.n_present`
    asking 225 against the 399 the file was found to hold, because a
    description naming no spelling cannot be read back.
    """
    cells = _notes_with_absent_words(seed)
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"notes-{seed}", cells
    )
    source = _counted(cells)
    published = first["missing_by_source"]

    # The words come back, at the counts the table wrote them at.
    assert published == {"N/A": source["N/A"], "NA": source["NA"]}
    # ...and the blanks are counted as blanks, not as spellings.
    assert first["n_missing_blank"] == source[""]
    assert first["n_missing_withheld"] == 0

    # The twin writes each spelling at its published count, and leaves
    # exactly the published number of cells blank -- not one more.
    twin = _counted(written)
    assert twin["N/A"] == source["N/A"]
    assert twin["NA"] == source["NA"]
    assert twin[""] == source[""]

    # The twin re-describes to the same map, which is what makes the
    # field EXACT-OBSERVABLE rather than merely written.
    assert second["missing_by_source"] == published
    assert second["n_missing_blank"] == first["n_missing_blank"]

    # And both files meet the description: the twin, and the table the
    # description was written from.
    assert twin_exit == 0
    assert real_exit == 0


@pytest.mark.parametrize("seed", [201, 302])
def test_a_declared_identifier_keeps_the_words_its_holes_wore(
    tmp_path: pathlib.Path, seed: int
) -> None:
    """LTM-2 on the role declared precisely to keep its values in.

    Measured before: `NA` 59 and 52 blanks published as nothing at all,
    the twin writing 111 empty cells, and the real table missing both
    presence counts at exit 3.
    """
    draw = random.Random(seed)
    cells: "list[str]" = []
    for _row in range(600):
        pick = draw.random()
        if pick < 0.08:
            cells += ["NA"]
        elif pick < 0.14:
            cells += [""]
        else:
            cells += [f"Z{draw.randrange(100000, 999999)}"]

    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path / f"record-{seed}", cells, flags=("--identifier", "value")
    )
    source = _counted(cells)

    assert first["role"] == "identifier"
    assert first["missing_by_source"] == {"NA": source["NA"]}
    assert first["n_missing_blank"] == source[""]
    assert _counted(written)["NA"] == source["NA"]
    assert second["missing_by_source"] == first["missing_by_source"]
    assert twin_exit == 0
    assert real_exit == 0

    # The DECLARATION still holds: no value of the column is anywhere in
    # its block. The words named are synthtwin's own and no table's.
    block = json.dumps(first)
    for cell in cells:
        if cell and not parsing.names_a_published_word(cell):
            assert cell not in block


def test_a_persons_own_word_is_named_nowhere_on_such_a_column(
    tmp_path: pathlib.Path,
) -> None:
    """The narrowing this decision takes, pinned as a rule and not a gap.

    A spelling of the person's OWN words is not admitted on a column
    that publishes no value, declared or not, because a declaration is
    recorded as a count and never as text (C5-17): no loader holding one
    document could tell it from a value of the column. Those cells stay
    in the pooled remainder.
    """
    draw = random.Random(77)
    words = ("review", "pending", "checked", "repeat", "sample")
    cells: "list[str]" = []
    for _row in range(400):
        pick = draw.random()
        if pick < 0.15:
            cells += ["Not documented"]
        elif pick < 0.30:
            cells += ["NA"]
        else:
            cells += [
                " ".join(
                    draw.choice(words) for _word in range(draw.randrange(2, 5))
                )
            ]

    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "declared",
        cells,
        flags=("--missing-value", "Not documented"),
    )
    source = _counted(cells)

    # This package's own word is named; the person's own word is not,
    # anywhere in the block.
    assert first["missing_by_source"] == {"NA": source["NA"]}
    assert "Not documented" not in json.dumps(first)

    # ...and its cells are counted by NOTHING, which is what makes N3 an
    # upper bound on such a column. They are NOT put in the pooled
    # remainder: that remainder is what the FLOOR held back, and this
    # description was written at a floor of one, where S13 says nothing
    # is held back at all.
    assert first["n_missing_withheld"] == 0
    accounted = (
        sum(first["missing_by_source"].values())
        + first["n_missing_blank"]
        + first["n_missing_withheld"]
    )
    assert accounted == first["n_missing"] - source["Not documented"]
    assert accounted < first["n_missing"]

    # The twin therefore writes those cells blank, which is the stated
    # cost of the rule rather than a silent loss.
    assert _counted(written)["NA"] == source["NA"]
    assert "Not documented" not in written
    assert twin_exit == 0
    assert real_exit == 0


def test_a_spelling_of_nothing_but_space_names_the_empty_member(
    tmp_path: pathlib.Path,
) -> None:
    """The whitespace key landing 2b.8 admitted reaches this role too.

    The empty spelling is a member of the vocabulary and the comparison
    trims, so a cell holding one space names it. Without this rule the
    two landings would disagree about one key on one column.
    """
    draw = random.Random(91)
    cells: "list[str]" = []
    for _row in range(400):
        pick = draw.random()
        if pick < 0.18:
            cells += [" "]
        elif pick < 0.30:
            cells += [""]
        else:
            cells += [f"Z{draw.randrange(100000, 999999)}"]

    first, _second, written, twin_exit, real_exit = _round_trip(
        tmp_path / "spaces", cells, flags=("--identifier", "value")
    )
    source = _counted(cells)

    assert first["missing_by_source"] == {" ": source[" "]}
    assert first["n_missing_blank"] == source[""]
    assert _counted(written)[" "] == source[" "]
    assert twin_exit == 0
    assert real_exit == 0


def test_the_loader_refuses_a_key_that_is_no_word_of_its_own(
    tmp_path: pathlib.Path,
) -> None:
    """The half of P4-D85 a producer cannot be trusted with.

    The rule is checkable exactly because the vocabulary is closed, so a
    hand-edited document naming a spelling out of the column is refused
    by name rather than loaded. Without this check the publication class
    would rest on the producer's good behaviour.
    """
    from synthtwin import contract, errors

    draw = random.Random(55)
    words = ("review", "pending", "checked", "repeat")
    cells = [
        " ".join(draw.choice(words) for _word in range(draw.randrange(2, 5)))
        if draw.random() < 0.7
        else "NA"
        for _row in range(300)
    ]
    folder = tmp_path / "refusal"
    _first, _second, _written, _twin, _real = _round_trip(folder, cells)

    written = folder / "real-profile.json"
    document = json.loads(written.read_text(encoding="utf-8"))
    block = document["columns"][0]
    # One key moved from this package's word to a word of the table's.
    count = block["missing_by_source"].pop("NA")
    block["missing_by_source"]["pending review"] = count
    from tests import fixtures

    # WRITTEN THE WAY THE PRODUCER WRITES, so that the canonical-form
    # check passes and this reaches the rule under test. Dumped any
    # other way the loader refuses the BYTES before it reads a key, and
    # the test would pass while proving nothing about the publication
    # class.
    edited = fixtures.write_profile(folder, "edited.json", document)

    with pytest.raises(errors.ProfileError) as refusal:
        contract.load_profile(f"{edited}")
    said = f"{refusal.value}"
    assert "publishes no value of the table" in said
    # The refusal names the rule and never quotes the spelling back.
    assert "pending review" not in said
