"""The eighth file of synthtwin's generation reference vectors.

This is the EIGHTH entry point of one oracle, not an eighth oracle.  It
asks `make_generation_reference_vectors.py` for the seven cases the extra
review round of 2026-09-18 added to method section G14.3 -- the five of
its date pass (plans P4-D254 to P4-D258) and the two of its number pass,
G6.5a's last resort on the representable grid (plan P4-D269) and G6.5's
visiting order for the distinct-spelling repair (plan P4-D265) -- and for
the two the carried date items of the same day added when plan P4-D294
left P4-D258's two merges unreached: `date_two_kinds_traded` and
`date_two_kinds_nonadjacent`, each a one-field width census whose unnamed
remainder stands on days of the other kind -- and for the one the repair
pass of that day added, `date_both_fields_disagree`, which pins the joint
word a rank showing both fields takes under a census naming one-field
words alone (plan P4-D294, amended).  The repair pass also rebuilt the two
before it from the descriptions the producer writes of their tables.
They came here as the paragraph below says the next cases go, and the
file then stood at 150714 bytes -- and for the two the readings of an
absorbed count added (plan P4-D298), `free_text_absorbed_figures` and
`identifier_absorbed_figure` -- and for `judged_stand_in_written`, G10.1's
write rule with a judged stand-in among a column's absent cells (plan
P4-D6.4), built on a branch of its own that went here for the same
reason, which bring it to thirteen cases.

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

**WHERE THE NEXT CASE GOES, SO THE CHOICE IS NOT MADE UNDER A FAILING
GATE** (plan P4-D295, the merge-close of 2026-09-18).  The merge skeptic
measured the eight committed files against the 250000-byte cap and found
518 bytes of headroom on the second, not the twenty-five thousand the
round's brief assumed: `generation-branch-vectors-2.json` stands at
249482 bytes, the first at 248177 and the third at 246851, while THIS
file's output stands at 129683 and the fifth at 162596.  A case routed
into a full file is discovered by `tools/provenance/check_provenance.py`
refusing the build, which is the worst moment to be choosing a file.  So
it is chosen here instead: **the next case goes in this file**, and the
one after it too, until this file's output passes 200000 bytes -- at
which point a ninth entry point is written the way this one was, by
moving cases whole rather than by raising the cap.  **THAT POINT WAS
REACHED** on the branch of the carried numbers pass of 2026-09-18, whose
four cases took this file's output to 235440 bytes; its repair pass of
2026-09-19 opened the ninth entry point, `make_generation_branch_vectors_7.py`,
writing `tests/reference/generation-branch-vectors-7.json`.  When the
carried passes were integrated, this file also held the three cases of the
carried date items and the two of the readings of an absorbed count, and
with all nine new cases it would have passed the 250000-byte cap -- so the
numbers pass's four moved WHOLE into the ninth file, beside the two its
repair pass put there, and this file holds twelve cases.  The next case
goes here again, until this file's output passes 200000 bytes.  The first
three files are FULL and take no case; the fifth takes one only where this
file cannot.

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
