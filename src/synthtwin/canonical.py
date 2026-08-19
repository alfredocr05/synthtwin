"""The shape of a profile document that both halves must agree on
(plan D12, P2-D1).

WHAT IS HERE RATHER THAN IN `profile.py`, AND WHY. Everything in this
module is a fact about the document that the producer and the loader
have to answer the same way: the canonical bytes, and which of the
document's mappings key themselves on the table's own text.

The canonical form is what both halves of the product agree on: the
profiler writes it, and Phase 2's loader re-writes a parsed document
under the same rules and compares the bytes, which is how a duplicated
key, a reordered object, a non-canonical number spelling and a stray
newline are all caught by one check (plan P2-D2).

That makes it code the generation path has to reach, and the generation
path may not reach the module that reads the real table. `profile.py`
imports the reader's own table type, so every module that imports
`profile.py` inherits that reach whether it uses it or not, and a
boundary proved by "it is not called" is not proved at all (plan P2-D1).
So the serializer moved here, to a module that imports `json` and
nothing else -- not the reader, not the taxonomy, not this package's own
error messages.

`profile.serialize` still exists and still means the serializer below:
it is re-exported there, so every caller written against the earlier
shape keeps working and nothing about the published bytes moves.

The key-space table below is here for the same reason, arrived at the
hard way (review item P3-V9-F2). The producer and the loader each held
their own answer to "is this key one of synthtwin's own words, or is it
a spelling out of somebody's table?", each named ONE mapping, and both
were short by one -- so a table with a categorical label reading
`n_missing_withheld` wrote a description its own loader refused, and a
table with a label reading `(withheld)` stopped the profiler outright.
Two lists cannot disagree if there is one list.

Imports here stay within the allowlist (plan D6.2): json, and nothing
else at all.
"""

import json

# One step of a path that stands for "any place in a list", so that the
# two callers can write the same path with the shapes they each have:
# the producer's publication table walks a document it is building and
# writes `[]`, the loader's walk carries the real list index it reached.
EACH = "[]"

# THE MAPPINGS OF A DESCRIPTION WHOSE KEYS ARE THE TABLE'S OWN TEXT
# (contract 5 C5-N5, C5-1 to C5-4; plan amendment A-P3-32).
#
# Everywhere else in the format a mapping key is drawn from a vocabulary
# synthtwin publishes -- a class word, a percentile name, a UTC offset,
# a numeric style, a group size written in figures -- so reading a key
# as one of this package's own words is sound. In the two mappings named
# here it is NOT: a key is a spelling some cell of the table held,
# character for character, and the table decides it. `(withheld)`,
# `n_missing_withheld` and `n_sentinel_candidates_unpublished` are all
# things a cell can say, and version 5 exists precisely so that a table
# saying one of them can still be described.
#
# WHAT USES THIS, AND WHY IT IS ONE TABLE. Both halves of the product
# ask the same question of the same document. `profile._remainder_is_published`
# decides what may be WRITTEN; `contract._held_back_in` decides what may
# be LOADED. When each held its own answer they disagreed with the
# format and agreed with each other, which is the shape that makes a
# defect invisible: the producer refused to write a legitimate label,
# and the loader refused to read a description the producer did write.
#
# IT IS CHECKED AGAINST THE PRODUCER'S OWN RULES rather than trusted.
# `profile.PUBLICATION_RULES` gives every path of the finished document
# a kind, and the kind of a mapping's key says outright whether a
# spelling of the table may stand there. The suite derives this tuple
# from that table and fails if the two differ, so a mapping added to the
# format with the table's text for keys turns the suite red until it is
# named here (`tests/test_p3v9f2_one_key_space.py`).
TABLE_TEXT_KEY_SPACES = (
    ("columns", EACH, "levels", EACH, "variants"),
    ("columns", EACH, "missing_by_source"),
)


def keys_are_the_tables_own_text(path: "tuple[object, ...]") -> bool:
    """Whether the mapping standing at this path is keyed by the table.

    Guarantees:

    - Inputs: the path of the MAPPING itself -- not of a key inside it
      -- as a tuple of steps. A step is either a field name or a place
      in a list, and a list place may be written as this module's `EACH`
      or as the whole number the walk actually reached.
    - Determinism: a fixed function of the path and the table above.
    - Errors raised: none. A path this format does not have answers
      False, which reads every key there as synthtwin's own word -- the
      answer that refuses a document rather than accepting one.
    - Boundary: nothing is opened, and no key or value is looked at. The
      answer is about the PLACE, so no text of any table reaches it.
    """
    steps: list[object] = []
    for step in path:
        if isinstance(step, bool):
            return False
        if isinstance(step, int):
            steps = steps + [EACH]
        else:
            steps = steps + [step]
    return tuple(steps) in TABLE_TEXT_KEY_SPACES


def serialize(document: dict[str, object]) -> str:
    """Turn a profile document into its canonical text (plan D12).

    Guarantees: UTF-8 text with newline line endings, sorted keys, a
    two-space indent and fixed separators, and a trailing newline. The
    same document always produces exactly the same text. Raises
    ValueError through json if a value is not serializable, which
    cannot happen for documents `profile.build_document` builds.

    Boundary: nothing is opened, nothing is read, and no value of the
    real table is consulted -- the argument is the whole of the input.
    """
    return (
        json.dumps(
            document,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )
