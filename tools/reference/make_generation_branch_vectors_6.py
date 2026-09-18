"""The eighth file of synthtwin's generation reference vectors.

This is the EIGHTH entry point of one oracle, not an eighth oracle.  It
asks `make_generation_reference_vectors.py` for the seven cases the extra
review round of 2026-09-18 added to method section G14.3 -- the five of
its date pass (plans P4-D254 to P4-D258) and the two of its number pass,
G6.5a's last resort on the representable grid (plan P4-D269) and G6.5's
visiting order for the distinct-spelling repair (plan P4-D265).

**Why they are an eighth file.**  The two passes were built on branches of
their own and each added its cases to the seventh file.  Merged, that file
held thirteen cases and measured 276235 bytes against the provenance
manifest's 250000-byte cap (G14.2), so it could not carry them: the seven
move here whole and the seventh keeps the six it held before the round.
No case was dropped, no proof was shortened and the cap was not raised --
which is the reason the fourth, fifth, sixth and seventh files exist, and
it is written here rather than left to be worked out from a byte count.
Everything the second entry point says holds for this one word for word:
the transform, the proof layer, the words-as-inputs rule and every case
builder live in `make_generation_reference_vectors.py` beside this file,
and two copies of a proof layer would be two things that can drift apart.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import path,
so a plain `import` of the module beside it would not resolve.  Running it
by path is the same mechanism the guard runner itself uses, and it is
permitted in tools/ (the D6 restriction applies to src/ only).  Nothing
about the oracle's own rule changes: it still imports neither synthtwin,
nor numpy, nor pandas, and a test asserts that of every entry point.

Usage:  python3 make_generation_branch_vectors_6.py --seed 0 --out <path>
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
    """Write the eighth case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove every
    number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["SIXTH_BRANCH_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
