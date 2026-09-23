"""The eleventh file of synthtwin's generation reference vectors.

This is the ELEVENTH entry point of one oracle, not an eleventh oracle.
It asks `make_generation_reference_vectors.py` for three of the six
cases stage 3's tail rule adds to method section G14.3 (landing 3.3,
plans P4-D321 to P4-D327): the listed tail of G5.3e and the counts
solved for it (`tail_listed_counts`), the sign rule of G5.5a on a
derived end (`tail_sign_clamped`) and the moment ladder of G5.3c
(`tail_moment_ladder`). The other three are the tenth file beside it.

**Why they are an eleventh file.**  Plan P4-D295 draws the line: an entry
point takes the next case until its output passes 200000 bytes, and then
the next entry point is written the way the last one was.  The seventh,
the eighth and the ninth all stand past that line, so stage 3's cases
open this one.  Every other file's own account names this one, as each
of them names all the others, so a reader who opens any of the ten is
told at once that it is part of one artifact rather than all of it.

**Why these six columns could not go in an earlier file.**  Each of them
publishes NO rung outside its two boundary percents -- the tail rule of
contract 6.7a -- and no case committed before stage 3 does.  Withdrawn
from the oracle, the whole of the rule would leave the other nine files
byte-identical.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

**WHERE THE NEXT CASE GOES** (plan P4-D295): here, while this file's
output stands under 200000 bytes; the first three files are full and take
no case, and the seventh, eighth and ninth stand past that line.

Usage:  python3 make_generation_branch_vectors_9.py --seed 0 --out <path>
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
    """Write the eleventh case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["NINTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
