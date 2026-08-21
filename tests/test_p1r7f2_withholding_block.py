"""P1-R7-F2, through the per-column block: a role that publishes no
values publishes no values ANYWHERE in its block.

The settings block was closed in the previous round. `sentinel_verdicts`
was not: it is written per column, it carries the exact spelling of a
numeric stand-in under `candidate`, and nothing looked at the column's
role before writing it. So a column the person had declared with
`--identifier` -- declared precisely to keep its values out of the
profile -- published `-999` in one field while the same run's summary
said of that column that it carries nothing at all of its values.

The repair is not a check inside that one field. A blacklist of the
fields that carry a spelling is the shape that failed twice: the levels
were closed, `missing_by_source` was closed, and the field added
afterwards was open. What is checked here is the block-level property:

* every item a nothing-publishing column publishes is either a named
  count, a length, or `(withheld)`;
* the facts that carry no value survive -- how many candidates were
  named, how many rows each accounted for, what was decided and why --
  so a reader can still see that a decision happened and which way it
  went;
* the neighbour: a role that DOES publish values still names the
  candidate, so the repair did not close the field for everybody;
* nothing about the block, including the ORDER of its lines, depends on
  a value of the table.
"""

import json
import pathlib

import pytest

import fixtures
from synthtwin import profile, reading, summary, taxonomy
from synthtwin.cli import main

SETTINGS = taxonomy.Settings()

# The item's own input, exactly as it was reported: one column, 180
# record numbers, 20 rows of the stand-in, and the person naming both
# the column and the value.
IDENTIFIERS = [f"{100000 + index}" for index in range(180)]
SENTINEL = "-999"


def describe(
    values: list[str],
    settings: taxonomy.Settings = SETTINGS,
    forced: bool = False,
) -> taxonomy.ColumnProfile:
    """Profile a single column of ``values``."""
    return taxonomy.profile_column(
        "column", 1, values, len(values), settings, forced
    )


def published_block(described: taxonomy.ColumnProfile) -> str:
    """Everything about a column that reaches a file, as one string."""
    return (
        json.dumps(profile._column_block(described), sort_keys=True)
        + " ".join(described.remarks)
        + " ".join(described.publication_notes)
    )


def _run(
    tmp_path: pathlib.Path,
    name: str,
    values: list[str],
    options: list[str],
    capsys: pytest.CaptureFixture[str],
) -> "tuple[dict, str, str]":
    """Profile one column through the real command line.

    Returns the profile document, the profile file exactly as it was
    written, and the summary file beside it -- because a value that
    escapes escapes into a FILE, and asserting on the object the
    profiler returned would not have caught this item.
    """
    text = fixtures.single_column_table(name, values)
    table = f"{fixtures.write(tmp_path, f'{name}.csv', text)}"
    assert main(["profile", table] + options) == 0
    capsys.readouterr()
    written = (tmp_path / f"{name}-profile.json").read_text(encoding="utf-8")
    said = (tmp_path / f"{name}-profile.txt").read_text(encoding="utf-8")
    document = json.loads(written)
    assert isinstance(document, dict)
    return document, written, said


# -- the reported input, through the real command ---------------------


def test_a_declared_identifier_publishes_no_stand_in_spelling(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    document, written, said = _run(
        tmp_path,
        "record_id",
        IDENTIFIERS + [SENTINEL] * 20,
        ["--identifier", "record_id", f"--keep-value={SENTINEL}"],
        capsys,
    )
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_IDENTIFIER
    # THE COLUMN BLOCK, WHICH IS WHERE THE SPELLING ESCAPED. A sentinel
    # verdict must not carry a value around the declaration that was
    # made to keep this column's values out.
    #
    # It is the block rather than the whole file because contract
    # version 5 records, in the SETTINGS, which of synthtwin's own three
    # stand-in numbers was named on the command line -- a fact about the
    # command line, written the same whatever table it is run on, and
    # priced in plan amendment A-P3-27. This test is about the column,
    # and the column is checked at the width the finding was about.
    for block in document["columns"]:
        assert SENTINEL not in json.dumps(block), (
            "the person named this column to keep its values out of the "
            "profile; a sentinel verdict must not carry one around that"
        )
    assert SENTINEL not in said
    for value in IDENTIFIERS[:20]:
        assert value not in written
        assert value not in said


def test_the_decision_survives_without_the_spelling(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # What must NOT be lost with the spelling: that 20 rows held a
    # number synthtwin checks as a stand-in for "no value", that it was
    # kept as data, and that it was kept because the person said so. A
    # reader who cannot see this cannot tell a column with no stand-in
    # from a column whose stand-in was silently removed.
    document, _written, said = _run(
        tmp_path,
        "record_id",
        IDENTIFIERS + [SENTINEL] * 20,
        ["--identifier", "record_id", f"--keep-value={SENTINEL}"],
        capsys,
    )
    column = document["columns"][0]
    assert column["sentinel_verdicts"] == [
        {
            "candidate": taxonomy.SUPPRESSED_LABEL,
            "verdict": taxonomy.VERDICT_KEPT,
            "reason": taxonomy.REASON_KEPT_BY_USER,
            "n_occurrences": 20,
        }
    ]
    assert column["n_missing"] == 0, "a kept value is not a missing value"
    assert "stand-ins for 'no value'" in said
    # The row count, the decision and the reason all survive. What the
    # line must NOT do is print the pooled name where the number goes:
    # `(withheld)` is synthtwin's word for "not published here", and
    # "(withheld), in 20 row(s): kept as a number" reads as a spelling
    # this table wrote (review of the shipped reports, 2026-08-15).
    assert "a number not named here, in 20 row(s)" in said
    assert taxonomy.SUPPRESSED_LABEL not in said
    assert "kept as a number" in said


def test_the_summary_claim_about_such_a_column_is_true(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The other half of the item: the words and the record disagreed.
    # The run said of this column that it carries no value at all, while
    # the profile beside it carried one.
    document, written, said = _run(
        tmp_path,
        "record_id",
        IDENTIFIERS + [SENTINEL] * 20,
        ["--identifier", "record_id", f"--keep-value={SENTINEL}"],
        capsys,
    )
    assert "No value at all, in any form" in said
    assert "record_id" in said
    for column in document["columns"]:
        assert column["role"] in taxonomy.ROLES_PUBLISHING_NOTHING
        assert SENTINEL not in json.dumps(column)
    assert SENTINEL not in said
    # And what the settings DO carry is the vocabulary member, which is
    # synthtwin's own number and not this column's value: the sentence
    # the summary prints is about what the COLUMNS publish, and every
    # column of this run publishes nothing.
    assert document["settings"]["kept_values"]["built_in_numbers"] == [
        -999.0
    ]
    assert written.count("-999.0") == 1


# -- the neighbour: the field still works where values may appear -----


def test_a_publishing_role_still_names_the_candidate(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The same column, the same option, the same value -- and no
    # --identifier. Nothing about this column is withheld, so the
    # verdict names the number, exactly as it did before. A repair that
    # withheld it here would have broken the field for every ordinary
    # numeric column.
    document, _written, said = _run(
        tmp_path,
        "reading",
        IDENTIFIERS + [SENTINEL] * 20,
        [f"--keep-value={SENTINEL}"],
        capsys,
    )
    column = document["columns"][0]
    assert column["role"] in taxonomy.ROLES_PUBLISHING_RANGES
    assert column["sentinel_verdicts"] == [
        {
            "candidate": SENTINEL,
            "verdict": taxonomy.VERDICT_KEPT,
            "reason": taxonomy.REASON_KEPT_BY_USER,
            "n_occurrences": 20,
        }
    ]
    assert column["percentiles"]["min"] == -999.0, (
        "a kept value is data, so it is the smallest number of this column"
    )
    assert f"{SENTINEL}, in 20 row(s)" in said


# -- the same rule on the other nothing-publishing roles --------------


def test_a_numeric_unrepresentable_column_withholds_it_too(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # This role is reached by no declaration at all: the column is
    # written as numbers, and almost none of them is a number this file
    # format can hold. It publishes no value either, and the same rule
    # has to reach it without anybody naming it.
    values = ["1e999"] * 189 + [SENTINEL] * 11
    document, written, _said = _run(tmp_path, "huge", values, [], capsys)
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_UNREPRESENTABLE
    assert SENTINEL not in written
    assert column["sentinel_verdicts"] == [
        {
            "candidate": taxonomy.SUPPRESSED_LABEL,
            "verdict": taxonomy.VERDICT_KEPT,
            "reason": taxonomy.REASON_TOO_FEW_OTHERS,
            "n_occurrences": 11,
        }
    ]


def test_free_text_reaches_this_field_with_nothing_in_it() -> None:
    # Free text is the third nothing-publishing role, and it cannot
    # carry a verdict at all: the sentinels are judged only for a column
    # written as numbers at the one parse rate, and such a column is
    # never described as free text. The field is still present and
    # empty, which is what makes the profile's shape the same on every
    # role.
    described = describe(
        fixtures.prose(60)
        + [SENTINEL] * 20
    )
    assert described.role == taxonomy.ROLE_TEXT
    assert described.sentinel_verdicts == []
    assert SENTINEL not in published_block(described)


# -- the property, on every nothing-publishing role -------------------


def _nothing_publishing() -> "dict[str, taxonomy.ColumnProfile]":
    """One profiled column per role that publishes no values."""
    return {
        taxonomy.ROLE_IDENTIFIER: describe(
            IDENTIFIERS + [SENTINEL] * 20,
            settings=taxonomy.Settings(kept_values=(SENTINEL,)),
            forced=True,
        ),
        taxonomy.ROLE_UNREPRESENTABLE: describe(
            ["1e999"] * 189 + [SENTINEL] * 11
        ),
        taxonomy.ROLE_TEXT: describe(
            fixtures.prose(60)
        ),
    }


@pytest.mark.parametrize("role", sorted(taxonomy.ROLES_PUBLISHING_NOTHING))
def test_every_published_item_is_a_named_count_or_withheld(role: str) -> None:
    """The block-level property, stated as the code states it.

    This is the test that would have caught the item without anybody
    thinking of `sentinel_verdicts` first: it does not name a field. It
    walks everything the block publishes and requires each item to be a
    key this module has named as carrying no value, or the withheld
    label. A field added tomorrow fails this until somebody names it.
    """
    described = _nothing_publishing()[role]
    assert described.role == role, "the fixture must exercise the named role"
    for key in described.details:
        assert (
            key in taxonomy.KEYS_THAT_CARRY_NO_VALUE
            or described.details[key] == taxonomy.SUPPRESSED_LABEL
        ), f"{key} of a {role} block is neither a named count nor withheld"
    for entry in described.sentinel_verdicts:
        for key in entry:
            assert (
                key in taxonomy.KEYS_THAT_CARRY_NO_VALUE
                or entry[key] == taxonomy.SUPPRESSED_LABEL
            ), f"{key} of a {role} verdict is neither a count nor withheld"
    assert described.missing_by_source == {}


@pytest.mark.parametrize("role", sorted(taxonomy.ROLES_PUBLISHING_NOTHING))
def test_no_value_of_the_column_reaches_the_block(role: str) -> None:
    described = _nothing_publishing()[role]
    block = published_block(described)
    assert SENTINEL not in block
    assert "1e999" not in block
    for value in IDENTIFIERS[:20]:
        assert value not in block


def test_the_names_of_the_counts_are_not_a_wish_list() -> None:
    # A whitelist that named keys nothing produces would be a whitelist
    # nobody maintains. Every name on it must be a key a real block
    # carries, or the two lists have drifted apart -- except the three
    # that belong to a verdict, which are checked with the verdicts
    # above.
    carried = {"n_occurrences", "reason", "verdict"}
    for described in _nothing_publishing().values():
        for key in described.details:
            carried = carried | {key}
    for key in taxonomy.KEYS_THAT_CARRY_NO_VALUE:
        assert key in carried, (
            f"{key} is named as carrying no value but no block carries it"
        )


# -- the declaration outlives the role it did not get -----------------


def test_a_declared_column_of_nothing_but_no_value_publishes_nothing(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The same item through the door the role rule cannot see.

    A column whose cells are ALL spellings meaning "no value" never
    reaches the identifier role: the empty-column rule settles it before
    any rule runs, so the block is built for a role that is not on the
    nothing-publishing list. It published the person's own spelling,
    200 rows of it, in `missing_by_source` -- from a column they had
    declared with --identifier, and while the summary was telling them
    that a column of record numbers publishes nothing either way.
    """
    token = "ZZ-777"
    document, written, said = _run(
        tmp_path,
        "record_id",
        [token] * 200,
        ["--identifier", "record_id", f"--missing-value={token}"],
        capsys,
    )
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_EMPTY
    assert column["missing_by_source"] == {}
    assert column["missing_by_class"]["(declared-missing)"] == 200, (
        "the rows are still counted, and still counted under the class "
        "that says the person decided them"
    )
    assert token not in written
    assert token not in said


def test_an_undeclared_empty_column_still_names_its_spellings(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    # The neighbour, and the reason the rule above is written as a
    # DECLARATION rather than as a change to the empty role: an ordinary
    # column that is entirely "NA" is not a column anybody withheld, and
    # naming the spelling that filled it is how its owner finds out
    # which one it was.
    document, _written, _said = _run(tmp_path, "unused", ["NA"] * 200, [], capsys)
    column = document["columns"][0]
    assert column["role"] == taxonomy.ROLE_EMPTY
    assert column["missing_by_source"] == {"NA": 200}


def test_the_rule_is_stated_where_it_can_be_read() -> None:
    # The class is a function, not a condition buried in a branch, so a
    # reader can ask it directly and a later field cannot answer
    # differently.
    assert taxonomy.publishes_no_values(taxonomy.ROLE_EMPTY, True)
    assert not taxonomy.publishes_no_values(taxonomy.ROLE_EMPTY, False)
    for role in taxonomy.ROLES_PUBLISHING_NOTHING:
        assert taxonomy.publishes_no_values(role, False)
    for role in taxonomy.ROLES_PUBLISHING_LABELS + taxonomy.ROLES_PUBLISHING_RANGES:
        assert not taxonomy.publishes_no_values(role, False)
        assert taxonomy.publishes_no_values(role, True)


# -- the order carries nothing either ---------------------------------


def test_the_order_of_withheld_verdicts_follows_the_facts() -> None:
    """Position must not say which candidate is the smaller number.

    Candidates are judged in the order of the numbers they are, which is
    the readable order for a block that names them. On a block that
    withholds the name, that order is the one thing left that depends on
    the value: with two `(withheld)` lines, the reader could tell which
    of the two known stand-ins came first. The withheld list is ordered
    by what it publishes instead.
    """
    values = IDENTIFIERS + ["-9999"] * 20 + [SENTINEL] * 12
    settings = taxonomy.Settings(kept_values=("-9999", SENTINEL))
    described = describe(values, settings=settings, forced=True)
    assert described.role == taxonomy.ROLE_IDENTIFIER
    counts = [entry["n_occurrences"] for entry in described.sentinel_verdicts]
    assert counts == [12, 20], (
        "-9999 is the smaller number and holds 20 rows, so candidate order "
        "and fact order disagree; the published order must be the facts'"
    )
    for entry in described.sentinel_verdicts:
        assert entry["candidate"] == taxonomy.SUPPRESSED_LABEL
    assert "-9999" not in published_block(described)


def test_the_same_two_candidates_keep_number_order_where_named() -> None:
    # The neighbour for the order: where the spelling is published there
    # is nothing to hide, and the readable order is the order of the
    # numbers. This is what stops the repair above from quietly
    # reordering every ordinary numeric column.
    values = [str(index) for index in range(1, 200)]
    settings = taxonomy.Settings(kept_values=("-9999", SENTINEL))
    described = describe(
        values + ["-9999"] * 20 + [SENTINEL] * 12, settings=settings
    )
    assert described.role in taxonomy.ROLES_PUBLISHING_RANGES
    named = [entry["candidate"] for entry in described.sentinel_verdicts]
    assert named == ["-9999", "-999"]


# -- the words say the same thing -------------------------------------


def test_the_summary_prints_what_the_profile_holds(
    tmp_path: pathlib.Path,
) -> None:
    # The summary is rendered from the document, so it can neither hide
    # a spelling the profile carries nor invent one the profile
    # withholds. Both directions in one table.
    rows = []
    for index in range(200):
        stand_in = index % 10 == 0
        rows = rows + [
            [
                SENTINEL if stand_in else IDENTIFIERS[index % 180],
                SENTINEL if stand_in else f"{index % 400 + 1}",
            ]
        ]
    path = fixtures.write(
        tmp_path, "both.csv", fixtures.rows_to_csv(["record_id", "measure"], rows)
    )
    document = profile.build_document(
        reading.read_table(str(path)),
        taxonomy.Settings(kept_values=(SENTINEL,)),
        ["record_id"],
    )
    said = summary.render(document, "read as UTF-8.")
    withheld = document["columns"][0]
    named = document["columns"][1]
    assert withheld["role"] == taxonomy.ROLE_IDENTIFIER
    assert named["role"] in taxonomy.ROLES_PUBLISHING_RANGES
    assert withheld["sentinel_verdicts"] and named["sentinel_verdicts"], (
        "both columns must reach the field, or this proves nothing"
    )
    for entry in withheld["sentinel_verdicts"]:
        assert entry["candidate"] == taxonomy.SUPPRESSED_LABEL
        # The profile's pooled name reaches the page as what it means --
        # "not published here" -- and never as a spelling of the table.
        assert "a number not named here, in" in said
    assert taxonomy.SUPPRESSED_LABEL not in said
    for entry in named["sentinel_verdicts"]:
        assert entry["candidate"] == SENTINEL
        assert f"{SENTINEL}, in" in said
