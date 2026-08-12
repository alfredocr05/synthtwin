"""The canonical text of a profile document (plan D12, P2-D1).

ONE FUNCTION, AND IT IS HERE RATHER THAN IN `profile.py` FOR A REASON.
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

`profile.serialize` still exists and still means this function: it is
re-exported there, so every caller written against the earlier shape
keeps working and nothing about the published bytes moves.

Imports here stay within the allowlist (plan D6.2): json, and nothing
else at all.
"""

import json


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
