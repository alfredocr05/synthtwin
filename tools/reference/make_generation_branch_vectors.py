"""The branch half of synthtwin's generation reference vectors.

This is the SECOND entry point of one oracle, not a second oracle.  The
transform, the proof layer, the words-as-inputs rule and every case
builder live in `make_generation_reference_vectors.py` beside this file;
this script asks that oracle for the case set method section G14.3 adds
for the branches its first nine leave unexercised (review items
P2-C3-F3 and P2-C4-C3), and writes it to the path given by `--out`.

**Why there are two files rather than one.**  A committed fixture must
stay under the provenance manifest's 100000-byte cap, and the nine cases
of the first file already spend 88207 of it.  The five cases here spend
another 35562.  One file would carry about 123000 bytes and break the
cap, so the review that asked for these cases said in as many words that
they may live in a second small fixture.  They are not a second oracle:
two copies of a proof layer are two things that can drift apart, and the
whole point of this artifact is that it cannot drift.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import
path, so a plain `import` of the module beside it would not resolve.
Running it by path is the same mechanism the guard runner itself uses,
and it is permitted in tools/ (the D6 restriction applies to src/ only).
Nothing about the oracle's own rule changes: it still imports neither
synthtwin, nor numpy, nor pandas, and a test asserts that of both files.

Usage:  python3 make_generation_branch_vectors.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed
        transform of given words rather than a random sample).
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the branch case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove
    every number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
