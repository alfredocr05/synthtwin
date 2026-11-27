"""The twenty-fifth file of synthtwin's generation reference vectors.

This is the TWENTY-FIFTH entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the cases landing R2a
adds to method section G14.3 (plan P4-D383): G7.5's writer of a layout of
the closed grammar of dates -- SAS's month word, HL7's fraction and its
`+HHMM` offset, an offset after one space, a whole-hour offset, the zulu
word `UTC`, an offset some cells omit, two flexible fields in the
layout's own order, a weekday lead, and a two-figure year read in the
century the person chose.

**Why a twenty-fifth file.**  Each landing of stage 3b gives its cases a
file of their own, so lanes building at once never add to one file's case
set; the integrator gives this landing the number.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_25.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed transform
        of given words rather than a random sample).
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the twenty-fifth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv,
        part=oracle["TWENTY_FIFTH_BRANCH_PART"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
