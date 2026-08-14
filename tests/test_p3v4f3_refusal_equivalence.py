"""The report on a refused file is the reader's refusal, by construction.

REVIEW ITEM P3-V4-F3, and plan amendment A-P3-10 clause 2. V9 makes a
structural mismatch a MISSED verdict with a plain explanation rather
than a refusal, so `synthtwin validate` REPORTS on two of the reader's
own refusals -- a file with no rows to describe, and one whose first row
leaves a name blank or uses a name twice -- and V5.1-A1 says such a
report may state what that refusal states and nothing else.

WHAT WAS WRONG, AND WHY IT WAS A CLASS AND NOT A LIST. The two questions
were answered by a walk of this module's own, taken BEFORE the reader
was called, and the branch was taken on that walk. The reader answers
the same two questions itself, in its own order, with a zero-byte check
and a ragged check standing between them -- so the two readings had a
precedence to agree about as well as a pair of answers, and they did
not. Four ways were found in one round: moving a repeated name's
positions moved the report; adding one data row to a NUL-bearing header
turned a report into a refusal; a ragged file changed refusal class when
a name was repeated in it; and the report named the positions of a
repeated name where the profiler's own refusal quotes the NAME and names
no position at all. Round 3 repaired the paths it was shown and the
class stayed open, which is what a rule kept in step by hand does.

THE REPAIR IS A CONSTRUCTION. There is no second walk: `measure` calls
the reader, catches its refusal, and chooses the report from WHICH
refusal it is. So the property this file asserts is not a list of pairs
but the rule itself -- **two files `synthtwin profile` refuses with the
same sentence get the same report** -- driven over a battery that
crosses every refusal the reader has, with the four named routes among
them as named cases and the other direction beside it: files the
producer refuses DIFFERENTLY may differ, or the guarantee would be the
vacuity V3.4 refuses.

WHAT IS LEFT OPEN, at its own size and by an owner's ruling. Against a
ZERO-ROW description the gate does not close, plan amendment A-P3-7
clause 3 rules that so and says what closing it would cost, and this
repair does not touch that path. The last case here pins that residual
where it is, so that a change to it is a change somebody chose.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import dataclasses
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

SEED = 20260814

# The three byte rules amendment A-P3-3 clause 6 ruled outside V5.1's
# envelope: no cell, no name, no count and no person is in a line
# ending, a terminal newline or a byte-order mark, and the producer
# publishes none of them about any file at any count. Two files the
# producer refuses alike may still differ at these, and the battery
# below measures what MAY escape beside what may not.
_OUTSIDE_THE_ENVELOPE = (
    "bytes.line-endings",
    "bytes.terminal-newline",
    "bytes.byte-order-mark",
)

_ROWS = "\n".join(f"{30 + index % 40},north,n{index % 3}" for index in range(40))


def _described(folder: pathlib.Path, text: str, stem: str) -> contract.Profile:
    """One table through the real producer and the strict loader."""
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_NAMES
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


@pytest.fixture(scope="module")
def headed(tmp_path_factory: pytest.TempPathFactory) -> contract.Profile:
    """A description publishing forty rows and three named columns."""
    folder = tmp_path_factory.mktemp("f3-headed")
    return _described(
        folder,
        fixtures.rows_to_csv(
            ["age", "site", "note"],
            [
                [f"{30 + index % 40}", fixtures.REGIONS[index % 4], f"n{index % 3}"]
                for index in range(60)
            ],
        ),
        "headed",
    )


def _written(folder: pathlib.Path, body: "str | bytes") -> pathlib.Path:
    """One measured file, always under the SAME name.

    The name is an input to the report (V7.1-A1) and to the reader's own
    refusal sentence, so holding it equal is what makes every comparison
    here about the file's bytes and not about what somebody typed.
    """
    target = folder / "measured.csv"
    if isinstance(body, bytes):
        target.write_bytes(body)
    else:
        target.write_text(body, encoding="utf-8", newline="")
    return target


def _the_producer_says(folder: pathlib.Path, body: "str | bytes") -> str:
    """What `synthtwin profile` publishes about this file: read, or refused.

    This is V5.1's envelope in one string. The reader is asked in the
    QUOTING form, which is the form the person who owns the table gets,
    because that is the run whose output the envelope is drawn round.
    """
    target = _written(folder, body)
    try:
        reading.read_table(str(target), first_row=reading.FIRST_ROW_NAMES)
    except errors.ProfileError as refusal:
        return f"refused: {refusal}"
    return "described"


def _the_report_says(
    folder: pathlib.Path, described: contract.Profile, body: "str | bytes"
) -> "tuple[object, ...]":
    """Every verdict of one run, or the refusal it came back with instead.

    The three ruled-out byte rules come off the verdict list AND out of
    the census, because the census is counted from the verdicts and a
    difference at a ruled-out rule would otherwise arrive here as a
    difference in a total. What is left is every statement the report
    makes that V5.1 governs.
    """
    target = _written(folder, body)
    try:
        outcome = validation.measure(described, str(target))
    except errors.ProfileError as refusal:
        return ("refused", f"{refusal}")
    governed = [
        check
        for check in outcome.checks
        if check.subcheck not in _OUTSIDE_THE_ENVELOPE
    ]
    counted = {verdict: 0 for verdict in validation.VERDICTS}
    for check in governed:
        counted[check.verdict] = counted[check.verdict] + 1
    return (
        "reported",
        tuple(sorted(counted.items())),
        outcome.census.not_checkable,
    ) + tuple(
        (
            check.column,
            check.fact,
            check.subcheck,
            check.verdict,
            check.published,
            check.achieved,
            check.citation,
        )
        for check in governed
    )


# Every shape of file the two paths and the refusals around them can be
# reached with. The four routes the review named are here by name; the
# rest are the ones re-deriving the class turned up, and the ordinary
# files are here so that the property below is not green by refusing
# everything.
_BATTERY: "dict[str, str | bytes]" = {
    # -- files the producer refuses for holding no rows ---------------
    "the published names": "age,site,note\n",
    "two other names": "foo,bar,baz\n",
    "a different width": "one,two\n",
    "one name": "only\n",
    "the names and blank lines": "age,site,note\n\n\n",
    "a name holding a line break": '"age\nsite"\n',
    "no bytes at all": "",
    "blank lines alone": "\n\n",
    # -- files whose first row cannot name columns --------------------
    "a repeated name, first and last": "dup,a,dup\n" + _ROWS + "\n",
    "a repeated name, last two": "a,dup,dup\n" + _ROWS + "\n",
    "a repeated name, first two": "dup,dup,c\n" + _ROWS + "\n",
    "another name repeated": "qq,ww,qq\n" + _ROWS + "\n",
    "a repeated name behind a blank line": "\ndup,a,dup\n" + _ROWS + "\n",
    "a blank name at one": ",b,c\n" + _ROWS + "\n",
    "a blank name at two": "a,,c\n" + _ROWS + "\n",
    "a blank name and a repeat": ",dup,dup\n" + _ROWS + "\n",
    # -- files the producer refuses for something else ---------------
    "a NUL in the header": b"a\x00b,c,d\n",
    "a NUL in the header, one row": b"a\x00b,c,d\n1,2,3\n",
    "a NUL beside a repeated name": b"dup,dup,c\n1,2,3\n\x00,2,3\n",
    "ragged": "a,b,c\n1,2\n3,4,5\n",
    "ragged with a repeated name": "dup,dup,c\n1,2\n3,4,5\n",
    "ragged with a blank name": ",b,c\n1,2\n3,4,5\n",
    "an unclosed quotation mark": 'a,b,c\n"1,2,3\n',
    # -- files the producer reads ------------------------------------
    "the table itself": "age,site,note\n" + _ROWS + "\n",
    "a table with other names": "aa,bb,cc\n" + _ROWS + "\n",
}


def test_two_files_the_producer_refuses_alike_get_one_report(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """THE PROPERTY, over the whole battery.

    V5.1 in one sentence: the report may state about the measured file
    only what `synthtwin profile`, run on THAT FILE, would publish about
    it. So where two files draw the same sentence out of the producer,
    they must draw the same report out of the validator -- and where the
    producer describes them both, the reports may of course differ,
    which is why the ordinary files below are grouped by their own
    sentence too.

    The three byte rules amendment A-P3-3 clause 6 ruled outside the
    envelope are left out of the comparison and asserted separately, so
    what may escape is measured beside what may not rather than folded
    into it.
    """
    folder = tmp_path / "property"
    folder.mkdir()
    grouped: dict[str, list[str]] = {}
    for label in sorted(_BATTERY):
        said = _the_producer_says(folder, _BATTERY[label])
        grouped.setdefault(said, [])
        grouped[said] = grouped[said] + [label]
    checked = 0
    for said in sorted(grouped):
        labels = grouped[said]
        if said == "described" or len(labels) < 2:
            continue
        first = _the_report_says(folder, headed, _BATTERY[labels[0]])
        for label in labels[1:]:
            other = _the_report_says(folder, headed, _BATTERY[label])
            assert first == other, (
                f"{labels[0]!r} and {label!r} draw one sentence out of "
                f"`synthtwin profile` and two different reports out of "
                f"`synthtwin validate`, so a candidate description reads "
                f"off the report something describing the file never "
                f"publishes (V5.1)"
            )
            checked = checked + 1
    assert checked >= 6, (
        f"the battery grouped into {len(grouped)} classes and compared "
        f"{checked} pairs; if the producer tells every one of these files "
        f"apart the property above is green by being empty"
    )


@pytest.mark.parametrize(
    ("one", "two"),
    (
        ("a repeated name, first and last", "a repeated name, last two"),
        ("a NUL in the header", "a NUL in the header, one row"),
        ("ragged", "ragged with a repeated name"),
        ("ragged", "ragged with a blank name"),
        ("the published names", "two other names"),
        ("a repeated name, first two", "a repeated name, first and last"),
    ),
)
def test_the_named_routes(
    tmp_path: pathlib.Path, headed: contract.Profile, one: str, two: str
) -> None:
    """The four routes the review named, and two beside them.

    Each pair is two files `synthtwin profile` cannot tell apart, named
    so a reader of the failure knows which route reopened:

    * the positions of a repeated name -- the profiler's refusal quotes
      the NAME and names no position, so `dup,a,dup` and `a,dup,dup` are
      one file to it;
    * whether a NUL-bearing header is followed by a row -- the reader
      raises the zero-byte refusal inside its own streaming loop, before
      it has counted a row, so the row's existence is not in its reply;
    * whether a ragged file also repeats a name, or leaves one blank --
      the reader refuses for raggedness first, so the header fault is
      not in its reply either;
    * two header-only files under one name, which is round 3's own
      witness kept where it can see this repair.
    """
    folder = tmp_path / "routes"
    folder.mkdir()
    said_one = _the_producer_says(folder, _BATTERY[one])
    said_two = _the_producer_says(folder, _BATTERY[two])
    assert said_one == said_two, (
        "the premise of this route: one sentence for both files"
    )
    first = _the_report_says(folder, headed, _BATTERY[one])
    second = _the_report_says(folder, headed, _BATTERY[two])
    assert first == second


def test_a_report_never_names_where_a_repeated_name_stands(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """The one thing the report used to say that the refusal does not.

    Amendment A-P3-7 clause 2 held that naming the column NUMBERS
    publishes strictly less than describing the file would. It does not:
    the profiler's refusal quotes the repeated NAME and names no
    position, so the numbers are a fact of their own. A-P3-10 clause 2
    corrects that account. What the report says now is the fact the
    refusal carries, and this asserts both halves -- no position, and
    still a MISS.
    """
    folder = tmp_path / "positions"
    folder.mkdir()
    for label in (
        "a repeated name, first and last",
        "a repeated name, last two",
        "a repeated name, first two",
    ):
        target = _written(folder, _BATTERY[label])
        outcome = validation.measure(headed, str(target))
        named = [
            check
            for check in outcome.checks
            if check.subcheck in ("header.names", "columns.order")
        ]
        assert len(named) == 2, label
        for check in named:
            assert check.verdict == validation.MISSED, (label, check)
            assert "column number" not in check.achieved, (label, check)
        spoken = " ".join(
            f"{check.published} {check.achieved} {check.citation}"
            for check in outcome.checks
        )
        for spelling in ("dup", "qq", "ww"):
            assert spelling not in spoken, (label, spelling)


def test_a_blank_name_still_names_the_position_its_refusal_names(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """The other direction: what the refusal DOES carry is still said.

    The profiler's refusal for a blank name names the column number, so
    a report may state it and two files with the blank in different
    columns may differ. A repair that answered the positions problem by
    taking every number off would have taken this with it, and the
    report would then say less than the person gets by running the
    producer -- which is the vacuity V3.4 refuses, in the small.
    """
    folder = tmp_path / "blank"
    folder.mkdir()
    first = _the_report_says(folder, headed, _BATTERY["a blank name at one"])
    second = _the_report_says(folder, headed, _BATTERY["a blank name at two"])
    assert first != second, (
        "two files the profiler refuses with two different sentences got "
        "one report, so the report says less than running the producer "
        "would"
    )
    target = _written(folder, _BATTERY["a blank name at two"])
    outcome = validation.measure(headed, str(target))
    named = [
        check for check in outcome.checks if check.subcheck == "header.names"
    ]
    assert len(named) == 1
    assert named[0].verdict == validation.MISSED
    assert "column number 2" in named[0].achieved


def test_a_file_the_reader_refuses_for_anything_else_is_refused(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """V1.5-A1: a report is never built on a file nobody could read.

    Raggedness, a zero byte, an unclosed quotation mark: the producer
    refuses each of these and publishes not one word about the file, so
    there is nothing for a report to be made of. The refusal comes back
    instead, and it names no value out of the file (V9).
    """
    folder = tmp_path / "refused"
    folder.mkdir()
    for label in (
        "a NUL in the header",
        "a NUL in the header, one row",
        "a NUL beside a repeated name",
        "ragged",
        "ragged with a repeated name",
        "ragged with a blank name",
        "an unclosed quotation mark",
    ):
        target = _written(folder, _BATTERY[label])
        with pytest.raises(errors.ProfileError) as raised:
            validation.measure(headed, str(target))
        spoken = f"{raised.value}"
        for spelling in ("dup", "qq", "ww"):
            assert spelling not in spoken, (label, spelling)


def test_the_branch_is_the_readers_own_word_and_nothing_else(
    tmp_path: pathlib.Path,
    headed: contract.Profile,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The construction itself, asserted rather than inferred.

    The property above would also be green if `measure` happened to
    agree with the reader on this battery while still deciding for
    itself. This pins the mechanism: the reader is replaced by one that
    raises each shape refusal in turn on a file that is ORDINARY -- the
    table itself, which the real reader reads without complaint -- and
    the report that comes back is the one that refusal chooses. A
    `measure` reading the file for itself would report on what it found
    there and not on the word it was handed.
    """
    folder = tmp_path / "branch"
    folder.mkdir()
    target = _written(folder, _BATTERY["the table itself"])
    shapes = {
        errors.NO_DATA_TO_DESCRIBE: "no-rows",
        errors.HEADER_NAME_MISSING: "unusable-header",
        errors.HEADER_NAME_REPEATED: "unusable-header",
    }
    seen: dict[str, str] = {}
    for kind in sorted(shapes):

        def _refuse(
            *_args: object, _kind: str = kind, **_named: object
        ) -> reading.Table:
            raise errors.shape_refusal("stood in for the reader", _kind, 2)

        monkeypatch.setattr(reading, "read_table", _refuse)
        outcome = validation.measure(headed, str(target))
        rows = [
            check for check in outcome.checks if check.subcheck == "rows.n_rows"
        ]
        assert len(rows) == 1, kind
        seen[kind] = (
            "unusable-header"
            if rows[0].verdict == validation.WITHHELD
            else "no-rows"
        )
        assert rows[0].citation == validation._GATE_REFUSED or (
            rows[0].verdict == validation.MISSED
        )
    assert seen == shapes


def test_the_zero_row_residual_is_where_the_amendment_left_it(
    tmp_path: pathlib.Path, headed: contract.Profile
) -> None:
    """A-P3-7 clause 3, pinned rather than quietly changed.

    Against a ZERO-ROW description the gate does not close: V1.5 says
    the profiler's reader refuses the degenerate forms and this one
    accepts them, so withholding there would leave V6.4's byte form
    unable to HOLD on any file at all. The residual that leaves open is
    that two header-only files still get different reports there, and
    this repair does not touch that path.

    The case is here so the residual is a thing somebody CHOSE and not a
    thing nobody noticed: if a later repair closes it, this test is what
    goes red, and the amendment says what closing it costs.
    """
    folder = tmp_path / "zero"
    folder.mkdir()
    zero_row = dataclasses.replace(headed, n_rows=0)
    first = _the_report_says(folder, zero_row, "age,site,note\n")
    second = _the_report_says(folder, zero_row, "foo,bar,baz\n")
    assert first != second, (
        "the zero-row residual amendment A-P3-7 clause 3 records is "
        "closed; that is an owner decision with a stated cost, so say so "
        "in the plan rather than here"
    )
    # ...and against a description that publishes rows, the same two
    # files are one file, which is the line clause 3 draws.
    third = _the_report_says(folder, headed, "age,site,note\n")
    fourth = _the_report_says(folder, headed, "foo,bar,baz\n")
    assert third == fourth
