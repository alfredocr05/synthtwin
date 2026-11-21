"""The thirtieth file of synthtwin's generation reference vectors.

This is the THIRTIETH entry point of one oracle, not a second oracle.
It asks `make_generation_reference_vectors.py` for the three cases lane
GG's repair 2 adds to method section G14.3 (plan P4-D440): G6.9's listed
census beside a one-cell edge left off the list,
`listed_supply_edge_left_off`; written forms handed on through a form
met before, `listed_forms_handed_on`; and a mode kept where its count
must give way, `listed_mode_takes_the_room`.

**Why a thirtieth file.**  Beside the lane's first four in the
twenty-ninth, the three stood at 303,350 bytes against the manifest's
250,000-byte cap; plan P4-D295 opens a file by moving cases whole, never
by raising the cap, and plan P4-D364's numbering gives the next number no
lane holds.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_30.py --seed 0 --out <path>
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
    """Write the thirtieth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv,
        part=oracle["THIRTIETH_BRANCH_PART"],
    )


if __name__ == "__main__":
    raise SystemExit(main())
