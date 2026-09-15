'''Assemble the version 6 contract from its section files -- REFUSED.

THIS SCRIPT NO LONGER WRITES ANYTHING (residual R-P4-113). It was
written so that a repair would land in a section file under
`docs/spec/v6-build/` and the document would be rebuilt from them. That
is not what happened: every repair since 2026-08-26, stage 2's
included, went straight into `docs/spec/profile-contract-v6.md`, and
the section files did not move. Run on the tree of 2026-09-15 the
rebuild wrote 385 lines and deleted 3,375 of the shipped contract,
silently discarding every one of those repairs.

Which copy is the source is the owner's question and is not answered
here: either the sections become the source again, which means carrying
every repair back into them, or the assembled document is declared the
source and the section files and this script are retired. Until the
owner answers, the rebuild refuses to run, so that the one command that
could throw the shipped contract away cannot be run by accident. The
section files are left exactly as they are.

The mechanical checks over the shipped document are
`tools/spec/check_assembly.py`, which `tests/test_contract_self_check.py`
runs on every suite.

The rebuild itself is not kept here: it wrote the shipped document
from the section files, and it stands in this file's history at commit
53bb012 for whichever answer the owner gives.
'''
import sys

# The order the section files were assembled in, kept because it is the
# one record of which section of the shipped document came from which
# file.

ORDER = [
    ("s1", "scope, authority, completeness; terms"),
    ("s3", "encoding and canonical serialization"),
    ("s4", "the document: top level and settings"),
    ("s45", "publication notes, the note grammar, relationships"),
    ("s5", "the column block: universal keys and the axes"),
    ("a7a_53", "the multiplicity map"),
    ("s5b", "the vocabulary, the absent cells, verdicts, the ladder"),
    ("r1", "the roles; empty; numeric_unrepresentable"),
    ("r2", "the label roles; constant; binary"),
    ("r3", "categorical and datetime"),
    ("r4a", "count and continuous"),
    ("r4b", "identifier and free_text"),
    ("r6", "the publication class and the forbidden-key matrix"),
    ("r5a", "affixed_number"),
    ("r5b", "time_of_day"),
    ("r5c", "long_tail_labels"),
    ("a7a_72", "multiplicity parity and the relationship manifest"),
    ("a7b1", "label spelling variants"),
    ("a7c", "numeric styles and fraction widths"),
    ("a7d", "the twin reproduces the recorded hole spellings"),
    ("a8a", "every invariant, part one"),
    ("a8b1", "every invariant: the value-bearing families"),
    ("a8b2", "every invariant: the new roles and the producer obligations"),
    ("a9", "the disposition matrix"),
    ("a10a", "the loader"),
    ("a10b", "the version rule, the refusals, the message"),
    ("a14", "capacity, the disclosure inventory, the decisions"),
    ("a14app", "appendix: every enumeration in one place"),
]

REFUSAL = (
    "tools/spec/assemble_v6.py refuses to run (residual R-P4-113): the"
    " section files in docs/spec/v6-build/ stopped moving on 2026-08-26"
    " while every repair since went into docs/spec/profile-contract-v6.md,"
    " so a rebuild would throw those repairs away. Which of the two copies"
    " is the source is a question for the owner, and nothing is written"
    " until it is answered."
)


def build() -> int:
    """Refuse, and name why. Writes nothing, reads nothing."""
    raise SystemExit(REFUSAL)


if __name__ == "__main__":
    print(REFUSAL, file=sys.stderr)
    raise SystemExit(2)
