"""The independent reader the suite cross-checks synthtwin against.

WHAT openpyxl IS HERE, AND WHAT IT IS NOT. synthtwin reads and writes
workbooks with its own code and imports openpyxl NOWHERE: the offline
scanner holds `src` to `zipfile`, `xml.parsers.expat` and the standard
library beside them. openpyxl exists in the SUITE alone, as a second
opinion, so that a fault in synthtwin's own workbook reader cannot hide
behind itself -- a twin that holds every published fact can still hand
a reader a different table, and this is the reader that says so.

WHY THIS MODULE EXISTS. Because openpyxl is not a dependency, it is not
always installed, and the one cell of CI that proves that -- `minimums`,
which installs the declared floors from requirements-min.lock and then
the wheel with `--no-deps` -- has no openpyxl in it at all. Twenty-five
cases FAILED there rather than skipping: some reached for openpyxl
directly, and more reached for it through `pandas.read_excel`, which
opens an `.xlsx` through openpyxl and raises `ImportError: Missing
optional dependency 'openpyxl'` when it cannot. A test that cannot run
is a test that skips and says why; a test that goes red on a missing
development convenience tells CI the product is broken when it is not.

So the dependency is named ONCE, here, and every cross-check in the
suite asks through this module. A twenty-sixth case tomorrow inherits
the skip by calling `reader()` or `read_excel()` instead of carrying a
copy of the condition.

WHERE THE CALL GOES IN A TEST, WHICH IS THE POINT OF THE DESIGN. These
functions skip AT THE POINT OF USE, not at the top of the test, and the
suite calls them as late as it can. Almost every case here drives
synthtwin end to end -- describe a workbook, generate its twin,
validate both, describe the twin again -- and then asks the independent
reader one question about the result. The synthtwin half of such a test
is the half that exercises the product, and it must not be skipped
because a development convenience is absent: without openpyxl the body
runs, every assertion about synthtwin's own reading and writing is made
and can still go red, and only the cross-check at the end is skipped.
Where a case is nothing BUT the cross-check, the skip lands on its
first line and the whole case skips, which is the honest report.

THREE REASONS, NOT ONE, BECAUSE THE THREE ARE DIFFERENT FACTS. A shared
skip message is printed once for every case carrying it -- `-rs` prints
`SKIPPED [n] tests/crosscheck.py:NN` against ONE line -- so a message
that is true of most of them and false of the rest tells a reader of
the `minimums` log the opposite of what happened. The review of
2026-09-21 found one message asserting "everything it asks synthtwin's
own workbook code ran before this point" over four cases where nothing
of synthtwin had run at all. So:

- `reader()` and `read_excel()` carry `REASON`: the case drove
  synthtwin and is asking a SECOND reader about the result. This is
  the late skip, and its message may say the synthtwin half ran.
- `fixture_writer()` carries `REASON_FIXTURE`: the case's SOURCE
  workbook is written BY openpyxl, so without it there is no file for
  synthtwin to read and the whole case skips honestly. Nothing of
  synthtwin ran, and the message says so.
- `part_not_measured()` carries `REASON_PART`: the case measured
  everything it could and asserted it, and is reporting the one named
  part it could not measure. It is the ending for a case that must not
  hand back a whole verdict on half the evidence -- `test_k_2b_46`,
  whose every-role CSV half is the owner's first-stated goal and needs
  no second reader at all, is the case that found it.

`present()` carries no message because it never skips: it is how a
case asks whether the reader is here and then decides for itself,
which is what lets the measurable half of a case be measured.
`read_excel_present()` is the workbook read for such a case -- the
same call as `read_excel()` with the skip taken out, because the
caller has already decided. A KPI test may use ONLY those two and
`part_not_measured`, which
`tests/test_kpi_ledger_integrity.py::test_no_kpi_test_can_be_skipped_by_the_absent_cross_check_reader`
holds it to: a headline that skips is a headline nobody measured.
"""

import pytest

# THE LATE SKIP: the case drove synthtwin and is asking a second reader.
REASON = (
    "openpyxl is the suite's independent cross-check reader and is not a "
    "dependency of synthtwin; it is absent here (the `minimums` CI cell "
    "installs the declared floors and the wheel with --no-deps), so what "
    "this test asks a SECOND reader cannot be asked. Everything it asks "
    "synthtwin's own workbook code ran before this point."
)

# THE HONEST WHOLE SKIP: openpyxl was to WRITE the source this case reads.
REASON_FIXTURE = (
    "openpyxl is the suite's independent cross-check reader and is not a "
    "dependency of synthtwin; it is absent here (the `minimums` CI cell "
    "installs the declared floors and the wheel with --no-deps). This "
    "case's SOURCE workbook is written BY openpyxl, so without it there "
    "is no file for synthtwin to read and NOTHING OF SYNTHTWIN HAS RUN: "
    "the whole case skips. Salvaging it would take a fixture built some "
    "other way, which would no longer be the shape that was measured."
)

# THE PART THAT COULD NOT BE MEASURED: everything else already was.
REASON_PART = (
    "openpyxl is the suite's independent cross-check reader and is not a "
    "dependency of synthtwin; it is absent here (the `minimums` CI cell "
    "installs the declared floors and the wheel with --no-deps). This "
    "case measured and ASSERTED everything that does not need it -- a "
    "regression in that half is still RED here -- and is reporting the "
    "one part it could not measure, rather than claiming a whole verdict "
    "on half the evidence. Not measured here: "
)


def _found() -> "object | None":
    """openpyxl if it imports, else None: the one import of it in the suite.

    It is caught as `ImportError` rather than `ModuleNotFoundError`
    because both are what an absent optional dependency raises -- a
    missing module raises the narrower one, and a module that fails to
    load raises the wider -- and neither is a fact about synthtwin.
    """
    try:
        import openpyxl
    except ImportError:
        return None
    return openpyxl


def present() -> bool:
    """Whether the cross-check reader is here. THIS NEVER SKIPS.

    A case with a half that needs no second reader asks this, measures
    that half whatever the answer, and reports the rest through
    `part_not_measured`. A case that is nothing BUT the cross-check
    calls `reader` instead and lets the skip land.
    """
    return _found() is not None


def reader() -> object:
    """openpyxl, or skip the rest of this test saying why it is absent."""
    found = _found()
    if found is None:
        pytest.skip(REASON)
    return found


def fixture_writer() -> object:
    """openpyxl as the WRITER of this case's source workbook, or skip whole.

    The same module, a different fact: here openpyxl builds the file
    synthtwin is to read, so its absence leaves nothing to test rather
    than one question unasked.
    """
    found = _found()
    if found is None:
        pytest.skip(REASON_FIXTURE)
    return found


def read_excel(*args: object, **kwargs: object) -> object:
    """`pandas.read_excel`, or skip: pandas opens an `.xlsx` through openpyxl.

    pandas itself is a declared floor and is always present; the reader
    it delegates to for a workbook is not. Asking for openpyxl first
    turns pandas' `ImportError: Missing optional dependency 'openpyxl'`
    -- a red test that says the product is broken -- into a skip that
    says what is missing.
    """
    reader()
    pandas = pytest.importorskip("pandas")
    return pandas.read_excel(*args, **kwargs)


def read_excel_present(*args: object, **kwargs: object) -> object:
    """`pandas.read_excel` for a caller that has ALREADY asked `present()`.

    THIS NEVER SKIPS, which is what a KPI test needs: asking here would
    throw away the half of its measurement that needs no second reader,
    which is exactly the defect of 2026-09-21. It raises rather than
    skipping if it is reached with the reader absent, because that is a
    caller that did not ask.
    """
    assert present(), (
        "read_excel_present() is for a caller that has already asked "
        "present() and decided for itself; a caller that wants the skip "
        "calls read_excel()"
    )
    import pandas

    return pandas.read_excel(*args, **kwargs)


def part_not_measured(part: str) -> None:
    """End a case that measured all it could: name the part that needs the reader.

    The caller has already asserted its measurable half, so this is a
    REPORT, not an escape, and it is the last statement of such a case.
    """
    pytest.skip(REASON_PART + part)
