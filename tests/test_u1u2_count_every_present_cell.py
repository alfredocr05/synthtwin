"""U1 and U2 are margins over the PRESENT cells, ordinary text included.

The defect this pins, stated plainly because the test is worthless if a
later reader cannot tell what it protects: the profiler used to leave a
cell of ordinary text out of both the whole-number family and the sign
family, while `n_present` counted it. On any column that reaches
`numeric_unrepresentable` with a non-numeric straggler -- a column of
numerals too long for the format holding a stray word, which the parse
line tolerates -- the two families then summed to less than
`n_present`, and the shipped loader refused the description its own
profiler had just written.

What made it worse than a crash is what the refusal SAID. The loader's
message for a broken U1 tells the reader "this file has been changed
since it was written" and asks them to make the description again --
blaming a person who had done nothing and sending them round a loop
that would produce the same file. `synthtwin profile` followed by
`synthtwin generate` is the whole product; there is no smaller way to
fail it.

Three artifacts agree on the rule and only the producer disagreed:
contract version 4 section 6.2 states U1 and U2 over `n_present` and
glosses all six keys as "present cells whose notation settles ...";
the sealed generation method's construction table (G10.5 step 1) ties
the "ordinary text" shape to `n_whole_unknown` and `n_sign_unknown`;
and the loader enforces the sum. So the producer was repaired.

Found while transcribing this rule into the version 6 contract, which
is the argument for transcribing rules rather than carrying them by
reference: nobody reads a rule as closely as somebody who has to write
it out.
"""

import csv
import json

from synthtwin import cli, parsing, taxonomy


def _column(values):
    return taxonomy.profile_column(
        "c", 0, values, len(values), taxonomy.Settings()
    )


def test_the_two_families_close_on_present_with_a_text_straggler():
    """The reported shape: wide numerals plus two ordinary words."""
    values = ["9" * 400] * 198 + ["apple", "pear"]
    profile = _column(values)
    assert profile.role == taxonomy.ROLE_UNREPRESENTABLE
    assert profile.n_present == 200
    details = profile.details
    assert (
        details["n_whole"] + details["n_fraction"] + details["n_whole_unknown"]
        == profile.n_present
    ), "U1 must count every present cell"
    assert (
        details["n_positive"]
        + details["n_negative"]
        + details["n_sign_unknown"]
        == profile.n_present
    ), "U2 must count every present cell"


def test_the_text_cells_land_where_the_generation_method_puts_them():
    """G10.5 step 1: ordinary text answers for the two `unknown` counts.

    Asserted as exact numbers rather than as a sum, because a sum that
    closes says nothing about WHICH count grew.
    """
    values = ["9" * 400] * 198 + ["apple", "pear"]
    details = _column(values).details
    assert details["n_whole"] == 198
    assert details["n_fraction"] == 0
    assert details["n_whole_unknown"] == 2
    assert details["n_positive"] == 198
    assert details["n_negative"] == 0
    assert details["n_sign_unknown"] == 2


def test_a_text_cell_is_never_counted_as_an_unrepresentable_negative():
    """The repair must not make text look like a negative number.

    Dropping the guard sends every present cell through the sign
    branches, so the repair rests entirely on `_classify` giving
    ordinary text SIGN_UNKNOWN. Were text ever to arrive carrying
    SIGN_NEGATIVE it would be counted as a negative value of the
    column, and U2 would still close -- a wrong answer that sums
    correctly, which is the failure this test exists to catch.
    """
    values = ["-9" + str(n).rjust(400, "0") for n in range(198)]
    values += ["apple", "pear"]
    profile = _column(values)
    assert profile.role == taxonomy.ROLE_UNREPRESENTABLE
    details = profile.details
    assert details["n_negative"] == 198, "the wide numerals, and only those"
    assert details["n_sign_unknown"] == 2, "the two words settle no sign"
    assert details["n_positive"] == 0


def test_the_two_families_are_total_over_every_cell_shape():
    """Both margins answer for every cell, whatever shape it is.

    Stated over the classifier rather than over a profile, because no
    single column reaches `numeric_unrepresentable` while holding all
    six shapes of the generation method's table -- a column with that
    many in-range numbers is a numeric column, and one with few enough
    distinct spellings is a label column. The property being pinned is
    not about any role: it is that the sign family and the whole-number
    family each give exactly one answer per present cell, which is what
    makes U1 and U2 sums over `n_present` rather than over a subset.
    """
    values = [
        "9" * 400,  # too large
        "0." + "0" * 400 + "1",  # too small
        "12",  # whole, in range
        "1.5",  # fraction, in range
        "apple",  # ordinary text
        "1.2.3",  # notation that conflicts with itself
    ]
    signs = {parsing.SIGN_NEGATIVE, parsing.SIGN_POSITIVE, parsing.SIGN_ZERO}
    wholes = {parsing.WHOLE_YES, parsing.WHOLE_NO}
    for cell in taxonomy._classify_all(values):
        assert (
            cell.sign in signs or cell.sign == parsing.SIGN_UNKNOWN
        ), "every cell answers the sign question exactly once"
        assert (
            cell.whole in wholes or cell.whole == parsing.WHOLE_UNKNOWN
        ), "every cell answers the whole-number question exactly once"


def test_profile_then_generate_survives_the_reported_shape(tmp_path):
    """The end-to-end failure: the product's own two commands.

    This is the test that would have caught the defect at the size a
    person meets it, and no unit test above replaces it: the profiler
    was self-consistent and the loader was self-consistent, and only
    running one against the other showed the tool refusing itself.
    """
    table = tmp_path / "t.csv"
    with table.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.writer(handle)
        writer.writerow(["c"])
        for _ in range(198):
            writer.writerow(["9" * 400])
        writer.writerow(["apple"])
        writer.writerow(["pear"])

    out = tmp_path / "out"
    out.mkdir()
    assert cli.main(["profile", str(table), "--out-dir", str(out)]) == 0

    document = json.loads((out / "t-profile.json").read_text(encoding="utf-8"))
    block = document["columns"][0]
    assert (
        block["n_whole"] + block["n_fraction"] + block["n_whole_unknown"]
        == block["n_present"]
    )

    assert (
        cli.main(
            [
                "generate",
                str(out / "t-profile.json"),
                "--out-dir",
                str(out),
                "--seed",
                "1",
            ]
        )
        == 0
    ), "the loader must accept the description the profiler just wrote"


def test_the_classifier_gives_text_the_two_unknown_answers():
    """The property the repair rests on, pinned so it cannot drift.

    If `_classify` ever settled a sign or a whole-number status for a
    cell of ordinary text, the repaired loop would count that text into
    a settled family and U1 would still close -- silently wrongly. This
    test fails there, where the sum tests would not.
    """
    values = ["apple", "pear", "not a number at all"]
    for cell in taxonomy._classify_all(values):
        assert cell.kind == parsing.NOT_A_NUMBER
        assert cell.sign == parsing.SIGN_UNKNOWN
        assert cell.whole == parsing.WHOLE_UNKNOWN
