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
"""

import pytest

REASON = (
    "openpyxl is the suite's independent cross-check reader and is not a "
    "dependency of synthtwin; it is absent here (the `minimums` CI cell "
    "installs the declared floors and the wheel with --no-deps), so what "
    "this test asks a SECOND reader cannot be asked. Everything it asks "
    "synthtwin's own workbook code ran before this point."
)


def reader() -> object:
    """openpyxl, or skip the rest of this test saying why it is absent.

    The import is written here and nowhere else in the suite. It is
    caught as `ImportError` rather than `ModuleNotFoundError` because
    both are what an absent optional dependency raises -- a missing
    module raises the narrower one, and a module that fails to load
    raises the wider -- and neither is a fact about synthtwin.
    """
    try:
        import openpyxl
    except ImportError:
        pytest.skip(REASON)
    return openpyxl


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
