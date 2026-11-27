"""The fourth file of synthtwin's generation reference vectors.

This is the FOURTH ENTRY POINT of one oracle, not a fourth oracle.  It
asks `make_generation_reference_vectors.py` for the cases method section
G14.3 adds for the transforms that produce a WHOLE DOCUMENT rather than
one column's cells -- the written form of a delimited file (method G2),
the arrangement of its rows (G2.1), the twin of a workbook (G2.2), the
lines before a table and the mark a twin may write for one (G2, contract
FD11), and the reading that settles which delimiter a file is written
with.  They live in a file of their own because the third file holds
245567 bytes against the provenance manifest's 250000-byte cap, which
leaves room for no case of any size (G14.2).

Everything the second and third entry points say of themselves holds
here word for word, and the two paragraphs that matter are repeated
rather than pointed at.

**Why there is a fourth file rather than one.**  A committed fixture
must stay under the provenance manifest's byte cap.  That is a rule
about a committed FILE; the case list of G14.3 is a rule about
COVERAGE, and the one may never be satisfied by breaking the other.  So
a case is never dropped and a proof is never shortened to fit: when a
file approaches the cap the next case opens a new file, exactly as the
third file was opened when the second approached it.  What must NOT
happen is a second copy of the oracle: a proof layer that exists twice
is two things that can drift apart, and the whole point of this
artifact is that it cannot drift.

**Why the oracle is loaded rather than imported by name.**  The
provenance guard runs a fixture generator as

    python tools/provenance/guard_runner.py <script> --seed <seed> --out <path>

through `runpy`, which leaves this file's own folder off the import
path, so a plain `import` of the module beside it would not resolve.
Running it by path is the same mechanism the guard runner itself uses,
and it is permitted in tools/ (the D6 restriction applies to src/ only).
Nothing about the oracle's own rule changes: it still imports neither
synthtwin, nor numpy, nor pandas, and a test asserts that of every one
of these files.

Usage:  python3 make_generation_document_vectors.py --seed 0 --out <path>
        (the command line the data-provenance guard uses; the seed is
        accepted and ignored, because these vectors are a fixed
        transform of given inputs rather than a random sample -- and
        these cases draw no word at all, because none of the transforms
        they freeze consumes one.)
"""

import os
import runpy
import sys

ORACLE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)),
    "make_generation_reference_vectors.py",
)


def main(argv=None):
    """Write the document case set to the path given by --out.

    Returns the oracle's own outcome, so a run that could not prove
    every number it would publish stops here exactly as it stops there.
    """
    oracle = runpy.run_path(ORACLE)
    return oracle["main"](
        sys.argv[1:] if argv is None else argv, part=oracle["DOCUMENT_PART"]
    )


if __name__ == "__main__":
    raise SystemExit(main())
