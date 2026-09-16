"""A report about a file the producer refuses (V5.1-A1, V9).

REVIEW ITEM P3-V3-F3. Two questions are settled ahead of the reader --
whether the file holds any rows, and whether its first row can name a
table's columns -- and each of them is settled about a file
`synthtwin profile` REFUSES. Validation reports on those rather than
refusing, because V9 makes a structural mismatch a verdict and not a
refusal; and reporting on them it stated four structural obligations and
every column's position against a header line nothing describing that
file publishes a word of.

THE WITNESS, MEASURED. Against a description publishing two hundred and
forty rows, the header-only files `age,site` and `foo,bar` under one
name gave 11 HELD, 1 WITHHELD, 73 MISSED and 6 HELD, 1 WITHHELD, 78
MISSED -- five verdicts apart. A person who holds such a file and can
run this command reads its header off those five, one candidate
description at a time, which is the attack V5.3 says the gate exists to
stop. On the other path, two duplicate-header files differing only in
how many data rows they carried printed different achieved row counts,
while the profiler's refusal of them does not change with the rows at
all.

WHAT IS ASSERTED HERE, in the shape plan amendment A-P3-7 fixes:

* THE EQUIVALENCE. Files the producer refuses in the same class get the
  SAME REPORT, check for check -- not merely the same census. The two
  byte rules amendment A-P3-3 clause 6 rules outside the envelope are
  the two exceptions and they are named, because a rule about what
  escapes has to say what does.
* THE TEETH. Nothing was bought with that silence: each of these files
  still misses its row count or its header, and every obligation of
  every column, so the report is an exit-3 report whatever the file
  holds.
* THE LINE. The zero-row predicates keep their verdicts, because there
  the conforming twin is itself a file the producer refuses and
  withholding would leave V6.4's byte form unable to hold on any file
  at all (V3.4). That is a residual and the plan states its size; what
  is asserted here is that it is exactly the zero-row predicate and
  nothing wider.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    errors,
    profile,
    reading,
    taxonomy,
    validation,
)

# The byte rules amendment A-P3-3 clause 6 ruled OUTSIDE V5.1's
# envelope, on the test A-P3-5 clause 3 wrote down: the producer
# published them about no file at any count. SINCE PLAN P4-D75 IT
# PUBLISHES THEM ABOUT EVERY FILE -- `source.dialect` records the line
# endings, the final newline and the byte-order mark -- so by that same
# test they are inside the envelope now, and on a file the producer
# refuses they are withheld like every other rule. Two files it refuses
# alike therefore differ at none of them. The tuple is kept, and the
# assertions below it are subset checks, so a report that began saying
# them apart again would still have to name one of these three to pass,
# and the assertions that ask for no difference at all say so.
_OUTSIDE_THE_ENVELOPE = (
    "bytes.line-endings",
    "bytes.terminal-newline",
    "bytes.byte-order-mark",
)


def _described(
    folder: pathlib.Path,
    text: str,
    stem: str,
    first_row: str = reading.FIRST_ROW_AUTOMATIC,
) -> contract.Profile:
    """One table through the real producer and the strict loader."""
    written = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(str(written), first_row=first_row)
    document = profile.build_document(table, taxonomy.Settings(), [])
    return contract.load_profile(
        str(fixtures.write_profile(folder, f"{stem}-profile.json", document))
    )


def _measure(
    folder: pathlib.Path, described: contract.Profile, body: "str | bytes"
) -> validation.Outcome:
    """Measure one file under a NAME THAT DOES NOT MOVE.

    The report says which file it is about (V7.1-A1), so two candidates
    compared here are written to the same name: a difference in the name
    is a difference the person typed and not one the file bought.
    """
    target = folder / "measured.csv"
    if isinstance(body, bytes):
        target.write_bytes(body)
    else:
        target.write_text(body, encoding="utf-8", newline="")
    return validation.measure(described, str(target))


def _apart(
    one: validation.Outcome, two: validation.Outcome
) -> "list[str]":
    """Every subcheck the two reports answer differently."""
    mine = {
        (check.column, check.fact, check.subcheck): check for check in one.checks
    }
    theirs = {
        (check.column, check.fact, check.subcheck): check for check in two.checks
    }
    found = []
    for key in sorted(set(mine) | set(theirs)):
        if mine.get(key) != theirs.get(key):
            found = found + [key[2]]
    return found


@pytest.fixture(scope="module")
def headed(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """A description publishing 240 rows, whose names came from a file."""
    folder = tmp_path_factory.mktemp("refused-headed")
    return _described(
        folder,
        fixtures.rows_to_csv(
            ["age", "site"],
            [
                [f"{30 + index % 40}", fixtures.REGIONS[index % 4]]
                for index in range(240)
            ],
        ),
        "headed",
    )


@pytest.fixture(scope="module")
def headerless(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """A description publishing 240 rows, whose names were generated."""
    folder = tmp_path_factory.mktemp("refused-headerless")
    return _described(
        folder,
        fixtures.rows_to_csv(
            ["41", "north"],
            [
                [f"{41 + index % 20}", fixtures.REGIONS[index % 4]]
                for index in range(240)
            ],
        ),
        "headerless",
        reading.FIRST_ROW_DATA,
    )


# -- the no-data path -------------------------------------------------


# Files a description publishing rows can be pointed at that hold no
# record at all. Every one of them is a file `synthtwin profile` refuses
# with the same words -- this file has no rows to describe -- so every
# one of them must come back with the same report.
_NO_DATA = {
    "the published names": "age,site\n",
    "two other names": "foo,bar\n",
    "four names": "one,two,three,four\n",
    "one name": "only\n",
    "the names and blank lines": "age,site\n\n\n",
    "the names, quoted": '"age","site"\n',
    "a name holding a line break": '"age\nsite"\n',
    # ...and the three the byte rules of A-P3-3 clause 6 are allowed to
    # tell apart, in the set so that what MAY escape is measured beside
    # what may not.
    "a byte-order mark": "﻿age,site\n",
    "carriage returns": "age,site\r\n",
    "no newline at the end": "age,site",
}


def test_two_files_the_producer_refuses_alike_get_one_report(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """V5.1: nothing describing these files publishes a header at all.

    The report may state what the profiler's refusal states -- this file
    holds no rows -- and the header line is not in it. So the width, the
    presence, the names, the order and each column's position are
    withheld, and every file here comes back with the same report but
    for the byte rules that are outside the envelope by a ruling.
    """
    reports = {
        label: _measure(tmp_path, headed, _NO_DATA[label])
        for label in sorted(_NO_DATA)
    }
    first = reports["four names"]
    for label in sorted(reports):
        found = _apart(first, reports[label])
        assert set(found) <= set(_OUTSIDE_THE_ENVELOPE), (
            f"the report on {label!r} differs from the report on a file "
            f"the producer refuses in the same class, at {found} -- so "
            f"the header of a file with no rows can be read off the "
            f"verdicts"
        )


def test_the_encoding_of_a_file_with_no_rows_is_not_told_by_the_reply(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """A file with no rows is one file whether or not its bytes are UTF-8.

    Plan amendment A-P3-7 clause 4. The question was asked of the UTF-8
    reading alone, so one of these came back a REFUSAL at exit 1 with no
    report and the other a full report at exit 3. That difference is the
    file's own encoding, told by the shape of the reply rather than by a
    verdict, and the producer publishes it about neither.
    """
    text = _measure(tmp_path, headed, "age,site\n")
    other = _measure(tmp_path, headed, "âge,sïte\n".encode("latin-1"))
    assert not _apart(text, other)
    assert other.census.missed == text.census.missed


def test_the_silence_on_that_path_buys_a_file_nothing(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """V3.4: what is withheld here is what no file was ever owed.

    A withholding that let a file off would be the defect amendment
    V2.4-A1 exists to close, in another place. This description
    publishes rows, so every one of the withheld obligations still
    answers on its own twin -- and the file that reaches this path
    misses its row count and every obligation of every column whatever
    its header says.
    """
    for label in sorted(_NO_DATA):
        outcome = _measure(tmp_path, headed, _NO_DATA[label])
        verdicts = [
            check.verdict
            for check in outcome.checks
            if check.subcheck == "rows.n_rows"
        ]
        assert verdicts == [validation.MISSED], label
        assert outcome.census.missed > 60, label
        for column in headed.columns:
            mine = [
                check
                for check in outcome.checks
                if check.column == column.name
                and check.verdict == validation.MISSED
            ]
            assert len(mine) > 5, (label, column.name)


def test_the_withheld_ones_say_which_gate_closed(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """V5.3: one fixed sentence, and it is the one that is true here.

    Amendment V3.4-A1 fixed that WITHHELD says one thing only --
    describing this file would not publish what this check measures --
    and that using it for a gap in the validator turns a gap into a
    silence a reader cannot tell from a confidentiality rule. These are
    withheld for the reason the sentence gives: there is no description
    of this file at all.
    """
    outcome = _measure(tmp_path, headed, "age,site\n")
    withheld = {
        check.subcheck: check
        for check in outcome.checks
        if check.verdict == validation.WITHHELD
    }
    for subcheck in (
        "columns.n_columns",
        "header.presence",
        "header.names",
        "columns.order",
        "position.at",
    ):
        assert subcheck in withheld, subcheck
        assert withheld[subcheck].citation == validation._GATE_REFUSED
        assert not withheld[subcheck].achieved


def test_a_headerless_description_still_answers_what_no_records_show(
    tmp_path: pathlib.Path, headerless: contract.Profile
) -> None:
    """The header question there is not about the file's own header.

    A description whose names were generated asks for NO header line,
    and a file holding no record carries no line of any kind: the answer
    is the same for every file that reaches here, so it is a verdict
    rather than a withholding. The two byte rules outside the envelope
    are the only thing two such files may still differ at.
    """
    empty = _measure(tmp_path, headerless, "")
    newlines = _measure(tmp_path, headerless, "\n\n")
    assert set(_apart(empty, newlines)) <= set(_OUTSIDE_THE_ENVELOPE)
    for outcome in (empty, newlines):
        verdicts = [
            check.verdict
            for check in outcome.checks
            if check.subcheck == "header.presence"
        ]
        assert verdicts == [validation.HELD]


# -- the header the reader used to refuse ----------------------------


# Files whose first row repeats a name or leaves one blank. Until plan
# P4-D75 the profiler refused each of these at that row, and the report
# on them withheld the width and the record count. Since then the
# reader NAMES such a column the way pandas names it and publishes the
# cell as written, so these are files the producer DESCRIBES: their row
# and column counts are stated, and their header misses by what it is.
#
# The names are spelled so that finding one in a report is finding it:
# a one-letter name is a letter every sentence in the report holds
# anyway, and a test that looked for it would pass on prose.
_REPEATED = {
    "two rows": "qqzz,qqzz\n1,2\n3,4\n",
    "four rows": "qqzz,qqzz\n1,2\n3,4\n5,6\n7,8\n",
    "three columns wide": "wwvv,wwvv,wwvv\n1,2,3\n",
    "many rows and wide": "xxyy,xxyy,xxyy,xxyy\n" + "1,2,3,4\n" * 30,
    "a byte-order mark": "\ufeffqqzz,qqzz\n1,2\n",
    "carriage returns": "qqzz,qqzz\r\n1,2\r\n",
}


def test_a_repeated_name_is_described_so_its_counts_are_stated(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """The counts the refusal used to keep back are now the file's own.

    The producer describes each of these files, so how many records it
    holds and how many columns are facts describing it publishes, and
    the report states them: never WITHHELD for a refusal that no longer
    happens.
    """
    for label in sorted(_REPEATED):
        outcome = _measure(tmp_path, headed, _REPEATED[label])
        for check in outcome.checks:
            if check.subcheck in ("rows.n_rows", "columns.n_columns"):
                assert check.verdict in (
                    validation.HELD,
                    validation.MISSED,
                ), (label, check)
                assert check.citation != validation._GATE_REFUSED, label


def test_a_repeated_name_misses_by_what_it_is_and_quotes_nothing(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """The teeth, without the file's own spelling.

    The header the file writes is not the header the description
    publishes, so the names miss; the file writes header cells the
    description does not record as written, so that rule misses too; and
    no string of the file is anywhere in the report.
    """
    for label in sorted(_REPEATED):
        outcome = _measure(tmp_path, headed, _REPEATED[label])
        for subcheck in ("header.names", "bytes.written-names"):
            verdicts = [
                check.verdict
                for check in outcome.checks
                if check.subcheck == subcheck
            ]
            assert verdicts == [validation.MISSED], (label, subcheck)
        body = " ".join(
            f"{check.published} {check.achieved} {check.citation}"
            for check in outcome.checks
        )
        for spelling in ("qqzz", "wwvv", "xxyy"):
            assert spelling not in body, (label, spelling)


def test_a_blank_name_is_read_and_misses_the_same_way(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """The other header the reader used to refuse, on the same terms."""
    outcome = _measure(tmp_path, headed, ",x\n1,2\n3,4\n")
    for subcheck in ("header.names", "bytes.written-names"):
        verdicts = [
            check.verdict
            for check in outcome.checks
            if check.subcheck == subcheck
        ]
        assert verdicts == [validation.MISSED], subcheck
    for check in outcome.checks:
        if check.subcheck in ("rows.n_rows", "columns.n_columns"):
            assert check.verdict != validation.WITHHELD, check


# -- the line: where the gate does NOT close --------------------------


def _zero_row(described: contract.Profile) -> contract.Profile:
    """The same description with its row count taken down to zero."""
    return fixtures.zero_rows(described)


def test_the_zero_row_predicate_keeps_every_verdict(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """V3.4 against V5.1, and the plan settles it (A-P3-7 clause 3).

    A zero-row description's own conforming twin IS a file the producer
    refuses: V1.5 says the profiler's reader refuses these forms and
    this one accepts them, and owner decision 7 makes the expected byte
    form the executable subcheck. Closing the gate there would leave
    that subcheck unable to HOLD on any file at all and would take
    review item P3-V3-F5's repair with it, so it stays open -- and the
    residual is stated at its size in the plan rather than left here to
    be found.
    """
    zero = _zero_row(headed)
    good = _measure(tmp_path, zero, "age,site\n")
    bad = _measure(tmp_path, zero, "other,name\n")
    for subcheck in (
        "bytes.zero-row-form",
        "header.names",
        "columns.order",
        "columns.n_columns",
        "header.presence",
    ):
        verdicts = [
            check.verdict
            for check in good.checks
            if check.subcheck == subcheck
        ]
        assert verdicts == [validation.HELD], subcheck
    assert bad.census.missed
    assert good.census.missed == 0


def test_the_gate_closes_on_no_other_path(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """The ordinary run is untouched: nothing is withheld for refusal.

    The gate of this amendment is reached only where the producer
    refuses the measured file. A file it can describe -- a conforming
    twin, a file with the wrong values in it, a file that stops one
    column short -- keeps every verdict it had, and this asserts it on
    the shipped table rather than trusting the branch.
    """
    twin = fixtures.rows_to_csv(
        ["age", "site"],
        [
            [f"{30 + index % 40}", fixtures.REGIONS[index % 4]]
            for index in range(240)
        ],
    )
    short = "\n".join(
        line.split(",")[0] for line in twin.split("\n") if line
    )
    for body in (twin, twin.replace("north", "south"), f"{short}\n"):
        outcome = _measure(tmp_path, headed, body)
        for check in outcome.checks:
            assert check.citation != validation._GATE_REFUSED, check


def test_a_file_that_cannot_be_walked_is_a_refusal_and_not_a_report(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """V1.5-A1, kept: an unfinished reading is not a file with no rows.

    The no-data question is asked of the text the reader settled on now,
    which is one more reading than it used to be asked of. It is still
    not asked of a walk that stopped part way: a file neither reading
    can parse is the catalogued refusal V9 asks for, not a report built
    on the records one of them happened to reach.
    """
    huge = "x" * (reading.FIELD_SIZE_LIMIT + 1)
    with pytest.raises(errors.ProfileError):
        _measure(tmp_path, headed, f"age,site\n{huge},north\n")
