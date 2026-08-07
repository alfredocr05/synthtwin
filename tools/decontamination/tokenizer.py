"""The canonical matching-contract tokenizer (Phase 0 plan D7, as ratified).

This module is the single shared implementation: the public scanner imports
it, and the maintainer-private extraction pipeline imports THIS file from
the repository, so the candidate token streams on both sides are identical
by construction. Its digest is bound in the signed attestation; any change
requires a fresh private coverage run and re-signing.

Contract order (ratification condition R2-C1):
  1. NFKC-normalize the complete input string;
  2. find maximal Unicode-alphanumeric chunks (underscore excluded) in the
     normalized string;
  3. split each chunk at case transitions (lower->UPPER, and the last
     capital of an UPPER run followed by lowercase) and letter/digit
     boundaries;
  4. casefold each subtoken.

Compatibility spellings (fullwidth, enclosed alphanumerics) therefore
yield the same token stream as their ASCII forms.
"""

import re
import unicodedata
from collections.abc import Iterator

_CHUNK = re.compile(r"[^\W_]+", re.UNICODE)


def _split_chunk(chunk: str) -> Iterator[str]:
    if not chunk:
        return
    start = 0
    n = len(chunk)
    for i in range(1, n):
        p, c = chunk[i - 1], chunk[i]
        nxt = chunk[i + 1] if i + 1 < n else ""
        if (
            p.isdigit() != c.isdigit()
            or (p.islower() and c.isupper())
            or (p.isupper() and c.isupper() and nxt.islower())
        ):
            yield chunk[start:i]
            start = i
    yield chunk[start:]


def tokenize(text: str) -> Iterator[str]:
    """Yield normalized tokens of ``text`` per the ratified contract."""
    normalized = unicodedata.normalize("NFKC", text)
    for chunk in _CHUNK.findall(normalized):
        for sub in _split_chunk(chunk):
            tok = sub.casefold()
            if tok:
                yield tok
