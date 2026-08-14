"""The written form: the twin's own bytes, checked against the method.

REVIEW ITEM P3-V3-F5. Owner decision 7 makes the degenerate zero-row
form's BYTES the executable check -- the file must equal the bytes the
method fixes for that description -- and the shipped check asked for
something else: one physical line ending in a line feed. That is neither
exact nor record-aware, and it was wrong in both directions at once.

* NOT EXACT. For a zero-row description of one column named `reading`
  the renderer writes `reading\\n`, and the file `"reading"\\n` passed
  every check the run filed. Reading the names back is `header.names`'
  question and it is answered by the parsed record, so the quoting was
  nobody's obligation at all -- and a file may be quoted six ways.
* NOT RECORD-AWARE. A published name holding a line feed is written
  `"alpha\\nbeta"\\n`, which is ONE record over two physical lines. The
  conforming file the shipped renderer writes was reported MISSED.

AND THE SAME CLASS REACHED A BYTE RULE, which is what re-deriving it
found. `bytes.line-endings` asked whether a carriage return was among
the file's bytes. The method writes a carriage return inside a quoted
field whenever a published name or label holds one, so that rule also
told a conforming twin it had broken a rule it kept -- and the
measured file was read with the ordinary text reading, which turns
every carriage return into a line feed, so the names read back under a
name the file does not carry and three more checks missed with it.

WHAT IS ASSERTED HERE, in the two forms the finding asks for:

* THE TWO WRITINGS, COMPARED WHERE BOTH MAY BE IMPORTED. The validator
  may not import the renderer (V1.4), so method G2's writing rule is
  written twice -- once in `rendering._line`, once in
  `validation._canonical_record` -- and this file compares them
  character for character over every class of name that quoting turns
  on;
* THE WHOLE ROUND TRIP. For each of those classes, the description is
  built by the real producer, the twin by the real generator, and the
  file the renderer wrote is measured: zero MISSED, on both the
  ordinary and the zero-row form. A conforming file the validator
  rejects is caught here whatever the rule that rejected it.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import dataclasses
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    generation,
    profile,
    reading,
    rendering,
    taxonomy,
    validation,
)

SEED = 20260814

# Every class of column name method G2's writing rule turns on: the four
# characters that force quoting, the doubled quote inside a quoted
# field, the byte-order-mark exception and its near miss, and two that
# must NOT be quoted. Written out one class per line, because a rule
# with an exception is a rule whose exception is the test.
NAME_CLASSES = {
    "plain": ["alpha", "beta"],
    "comma": ["al,pha", "beta"],
    "quote": ['al"pha', "beta"],
    "quoted-whole": ['"alpha"', "beta"],
    "line-feed": ["al\npha", "beta"],
    "carriage-return": ["al\rpha", "beta"],
    "both-breaks": ["al\r\npha", "beta"],
    "mark-led": ["﻿alpha", "beta"],
    "mark-inside": ["al﻿pha", "beta"],
    "spaces": [" alpha ", "beta"],
    "comma-in-the-second": ["alpha", "be,ta"],
    "mark-led-second": ["alpha", "﻿beta"],
}


def _table(names: "list[str]") -> str:
    """Forty rows under ``names``, written the way the renderer would."""
    header = rendering._line(tuple(names), True)
    rows = ""
    for index in range(40):
        rows = rows + (
            f"{index % 9 + 1},{fixtures.REGIONS[index % 4]}\n"
        )
    return header + "\n" + rows


def _described(
    folder: pathlib.Path, names: "list[str]", stem: str
) -> contract.Profile:
    """One such table through the real producer and the strict loader."""
    table_path = folder / f"{stem}.csv"
    table_path.write_text(_table(names), encoding="utf-8", newline="")
    table = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_NAMES
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _measure(
    folder: pathlib.Path, described: contract.Profile, text: str, name: str
) -> validation.Outcome:
    """Write a measured file, byte for byte, and measure it."""
    target = folder / name
    target.write_text(text, encoding="utf-8", newline="")
    return validation.measure(described, str(target))


def _verdicts(outcome: validation.Outcome) -> "dict[str, str]":
    """Every verdict the run filed, by subcheck."""
    return {check.subcheck: check.verdict for check in outcome.checks}


@pytest.fixture(scope="module")
def described_classes(
    tmp_path_factory: pytest.TempPathFactory,
) -> "dict[str, contract.Profile]":
    """One real description per name class, built once."""
    folder = tmp_path_factory.mktemp("written-form")
    built: dict[str, contract.Profile] = {}
    for label in sorted(NAME_CLASSES):
        described = _described(folder, NAME_CLASSES[label], label)
        assert [
            column.name for column in described.columns
        ] == NAME_CLASSES[label], (
            f"{label}: the producer did not carry this name through, so "
            f"the class is not being measured"
        )
        built[label] = described
    return built


def test_the_two_writings_of_the_header_line_agree(
    described_classes: "dict[str, contract.Profile]",
) -> None:
    """V1.4: method G2 written twice, compared where both may be imported.

    The validator derives the canonical header line from the method
    because it may not import the renderer. This is the comparison that
    keeps the two from drifting: same names in, same characters out, for
    every class of name the rule turns on -- including the two
    exceptions, which is where a second writing goes wrong.
    """
    for label in sorted(described_classes):
        names = [
            column.name for column in described_classes[label].columns
        ]
        assert validation._canonical_record(names) == rendering._line(
            tuple(names), True
        ), label


def test_a_zero_row_twin_of_every_name_class_misses_nothing(
    tmp_path: pathlib.Path,
    described_classes: "dict[str, contract.Profile]",
) -> None:
    """THE CONFORMING FILE IS NOT REJECTED, which is half the finding.

    The renderer's own bytes for the zero-row form of each description,
    measured. A name holding a line feed makes one record over two
    physical lines and the shipped check called it MISSED; a name
    holding a carriage return was rejected by the line-ending rule and
    by three more.
    """
    for label in sorted(described_classes):
        zero = dataclasses.replace(described_classes[label], n_rows=0)
        twin = rendering.twin_csv(generation.generate(zero, SEED))
        outcome = _measure(tmp_path, zero, twin, f"{label}-zero.csv")
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ]
        assert not missed, (
            f"{label}: the twin the shipped renderer wrote for this "
            f"description is reported as missing {sorted(set(missed))}"
        )
        assert outcome.census.withheld == 0, label


def test_an_ordinary_twin_of_every_name_class_misses_nothing(
    tmp_path: pathlib.Path,
    described_classes: "dict[str, contract.Profile]",
) -> None:
    """And the same on the ordinary path, because the rule is the same.

    `bytes.line-endings` is filed on every run, so a name holding a
    carriage return was a false accusation on every file of that
    description and not only on the degenerate one.
    """
    for label in sorted(described_classes):
        described = described_classes[label]
        twin = rendering.twin_csv(generation.generate(described, SEED))
        outcome = _measure(tmp_path, described, twin, f"{label}-full.csv")
        missed = [
            check.subcheck
            for check in outcome.checks
            if check.verdict == validation.MISSED
        ]
        assert not missed, f"{label}: {sorted(set(missed))}"


def test_another_spelling_of_the_same_names_misses_the_written_form(
    tmp_path: pathlib.Path,
    described_classes: "dict[str, contract.Profile]",
) -> None:
    """THE OTHER HALF: a file that is not the twin's bytes MISSES.

    Every name quoted, which is a valid CSV spelling of exactly the same
    names -- so the record reads back correctly and `header.names`,
    `columns.order` and `document.n_columns` all HOLD. What is left to
    tell the two files apart is the written form itself, and until this
    repair nothing did: the file passed every check the run filed.

    The `plain` class is where the point is sharpest, and every class is
    walked because a rule with an exception can be right on the ordinary
    case and wrong on the exception.
    """
    for label in sorted(described_classes):
        zero = dataclasses.replace(described_classes[label], n_rows=0)
        names = [column.name for column in zero.columns]
        quoted = ""
        for place in range(len(names)):
            if place:
                quoted = quoted + ","
            body = ""
            for character in names[place]:
                body = body + character
                if character == '"':
                    body = body + '"'
            quoted = quoted + f'"{body}"'
        if quoted == validation._canonical_record(names):
            # This class is already written quoted by the method, so
            # quoting it is not another spelling at all.
            continue
        outcome = _measure(tmp_path, zero, quoted + "\n", f"{label}-quoted.csv")
        verdicts = _verdicts(outcome)
        assert verdicts["bytes.zero-row-form"] == validation.MISSED, label
        assert verdicts["header.names"] == validation.HELD, label
        assert verdicts["columns.order"] == validation.HELD, label
        assert verdicts["columns.n_columns"] == validation.HELD, label


def test_the_written_form_answers_for_the_writing_and_for_the_stop(
    tmp_path: pathlib.Path,
    described_classes: "dict[str, contract.Profile]",
) -> None:
    """What this subcheck owns, and what it hands to its neighbours (V3.6).

    It owns two things nobody else checks: the record is written the way
    the method writes it, and the file stops there. It owns NEITHER the
    line ending nor the terminal newline nor the byte-order mark, each
    of which is a byte rule with its own verdict -- so a file that ends
    `\\r\\n` misses the line-ending rule and NOT this one, and a file
    with no final newline misses the terminal-newline rule and not this
    one. A check that answered for its neighbours' obligations would
    accuse one file twice for one fault, which is what round 2 took the
    names and the order out of this conjunction for.
    """
    zero = dataclasses.replace(described_classes["plain"], n_rows=0)
    written = validation._canonical_record(
        [column.name for column in zero.columns]
    )
    for label, text, form, others in (
        ("exact", written + "\n", validation.HELD, ()),
        (
            "carriage-return",
            written + "\r\n",
            validation.HELD,
            ("bytes.line-endings",),
        ),
        (
            "no-terminal-newline",
            written,
            validation.HELD,
            ("bytes.terminal-newline",),
        ),
        (
            "byte-order-mark",
            "﻿" + written + "\n",
            validation.HELD,
            ("bytes.byte-order-mark",),
        ),
        ("a-second-record", written + "\n" + written + "\n", validation.MISSED, ()),
        ("a-blank-line-after", written + "\n\n", validation.MISSED, ()),
        ("nothing-at-all", "", validation.MISSED, ()),
    ):
        outcome = _measure(tmp_path, zero, text, f"stop-{label}.csv")
        verdicts = _verdicts(outcome)
        assert verdicts["bytes.zero-row-form"] == form, label
        for neighbour in others:
            assert verdicts[neighbour] == validation.MISSED, (
                f"{label}: {neighbour} is the check that owns this fault "
                f"and it did not report it"
            )


def test_a_quoted_break_is_not_a_line_ending(
    tmp_path: pathlib.Path,
    described_classes: "dict[str, contract.Profile]",
) -> None:
    """The byte rule the class reached, from both ends.

    A carriage return inside a quoted field is data the method writes on
    purpose; a carriage return ending a record is the fault V6.2 names.
    The rule has to tell them apart, and asserting only the first would
    leave a rule that says yes to everything.
    """
    described = described_classes["carriage-return"]
    twin = rendering.twin_csv(generation.generate(described, SEED))
    kept = _measure(tmp_path, described, twin, "quoted-return.csv")
    assert _verdicts(kept)["bytes.line-endings"] == validation.HELD
    crlf = twin.replace("\n", "\r\n")
    broken = _measure(tmp_path, described, crlf, "crlf.csv")
    assert _verdicts(broken)["bytes.line-endings"] == validation.MISSED
    plain = described_classes["plain"]
    plain_twin = rendering.twin_csv(generation.generate(plain, SEED))
    lone = _measure(
        tmp_path, plain, plain_twin.replace("\n", "\r"), "lone-return.csv"
    )
    assert _verdicts(lone)["bytes.line-endings"] == validation.MISSED
