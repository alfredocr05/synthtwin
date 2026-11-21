"""Counts and spellings as a text writes them: one word rule for the tests that read a text.

WHY THIS EXISTS (batch 4r's tests-and-tools round HYG-1, LANE I4r
RULINGS 6). Several closed gate tests read a value out of a text by where its
spaces fall. Four read the counts of a validation check's own text as
`[int(w) for w in text.replace(",", " ").split() if w.isdigit()]`, so a
count followed by a point, a bracket, a semicolon or a closing quotation
mark was never read, and a count written with a thousands separator was
read as two counts. One layout gate looked for its column's cells in the
serialized questions file with needles that need a space or a quotation
mark beside the cell, so a cell at a string's end, before a point, in
brackets or before a semicolon was never seen. This module reads by the
WORDS instead: a text is split on any whitespace (a tab, a line break and
a no-break space too), and a word sheds at its two ends every character
that is no letter, figure or combining mark (Unicode categories L, N and
M): punctuation, quotation marks, brackets, symbols and invisible format
characters. It is the rule of `tools/measurements/kpi_chain_recount.py`'s
scan, written again here because a test does not load a tool to read a
text.

THE WRITER OF THE COUNTS. `validation._census_lines` writes each census
group's count with `validation._shown_count` (`f"{value}"`: figures alone,
no separator) after the group's name and a space, a short group as
`fewer than <line>`, and joins the groups with a comma and a space; the
notes beside them say `fewer than <line> of`. So every count of those
texts is a word of figures today. A thousands separator is read whole as
well (`1,234` is one count), so that a writer that ever groups its figures
cannot split a count in two.

Guarantees: pure functions of their arguments; no I/O of any kind; the
standard library only.
"""

from __future__ import annotations

import json
import unicodedata

# The marks the gate tests' own cases write a count or a cell before: a point,
# the closing brackets, a semicolon, and the closing quotation marks,
# straight and curly.
CLOSING_MARKS = (".", ")", "]", "}", ";", '"', "'", "”", "’", "»")


def sheddable(one: str) -> bool:
    """Whether a word sheds the character ``one`` at its ends.

    Anything but a letter, a figure or a combining mark (Unicode
    categories L, N and M): `.`, `,`, `;`, `:`, `%`, brackets, every
    quotation mark, signs, symbols such as the degree sign, and invisible
    format characters such as a zero-width space.
    """
    return unicodedata.category(one)[0] not in "LNM"


def shed(word: str) -> "tuple[str, str, str]":
    """``word`` cut into the marks it sheds at its front, its inside, and the marks it sheds at its back.

    A word of marks alone is all front: `("--", "", "")`.
    """
    start = 0
    while start < len(word) and sheddable(word[start]):
        start += 1
    end = len(word)
    while end > start and sheddable(word[end - 1]):
        end -= 1
    return word[:start], word[start:end], word[end:]


def count_of(word: str) -> "int | None":
    """The count one word writes once its ends are shed, or None where it writes none.

    A count is decimal figures alone (`345`, and `345.`, `(345)`,
    `345;`, `"345"` once shed), or figure groups joined by a thousands
    separator: a comma before each later group of exactly three figures,
    after a first group of one to three figures that no nought leads
    (`1,234`, `12,345,678`). Anything else is no count: a word with a
    letter (`1st`, `28-day`), a decimal (`12.5`, `36,8`), a clock time
    (`09:05`), a range (`1-10`), a word with a combining mark or a
    superscript figure.
    """
    groups = shed(word)[1].split(",")
    if not all(group != "" and group.isdecimal() for group in groups):
        return None
    if len(groups) > 1 and (
        len(groups[0]) > 3 or groups[0][0] == "0" or any(len(group) != 3 for group in groups[1:])
    ):
        return None
    return int("".join(groups))


def counts_in(text: str) -> "list[int]":
    """Every count ``text`` writes, in the order written: each word split on any whitespace, read by `count_of`."""
    found: "list[int]" = []
    for word in text.split():
        count = count_of(word)
        if count is not None:
            found += [count]
    return found


def part_counts(text: str) -> "list[int]":
    """The count that ends each part of a census line, in order; a part that ends in no count gives none.

    The parts are joined by a comma and a space, as
    `validation._comma_joined` joins them. A group's name may hold
    figures of its own (`minute :07`, `09:00-09:59`), so only the word
    that ends each part, split on any whitespace, is read by `count_of`.
    """
    found: "list[int]" = []
    for part in text.split(", "):
        words = part.split()
        count = count_of(words[-1]) if words else None
        if count is not None:
            found += [count]
    return found


def texts_of(decoded: object) -> "list[str]":
    """Every text of a decoded JSON value, at any depth.

    Each key and each string, and each number as JSON writes it (`-1`,
    `2023076`), so a value the file writes as a number is read as well;
    true, false and null are no text.
    """
    found: "list[str]" = []
    waiting: "list[object]" = [decoded]
    while waiting:
        one = waiting.pop()
        if isinstance(one, str):
            found += [one]
        elif isinstance(one, bool) or one is None:
            continue
        elif isinstance(one, (int, float)):
            found += [json.dumps(one)]
        elif isinstance(one, dict):
            for key in one:
                found += [f"{key}"]
                waiting += [one[key]]
        elif isinstance(one, (list, tuple)):
            waiting += one
    return found


def seen_in(decoded: object) -> "set[str]":
    """Every spelling a decoded JSON value writes as a whole text or as one word of a text.

    Each text of `texts_of` whole; and each of its words, split on any
    whitespace, with its ends shed every way -- from none of the marks
    at each end to all of them -- so that a spelling with marks of its
    own at its ends (`-1`, `N/A`) is seen where a word sheds down to it,
    and never where a letter or a figure stands beside it (`x-1`, `-10`).
    A word of marks alone is seen whole only. A spelling of several
    words is seen only as a whole text.
    """
    seen: "set[str]" = set()
    for text in texts_of(decoded):
        seen.add(text)
        for word in text.split():
            front, inside, back = shed(word)
            if inside == "":
                seen.add(word)
                continue
            for start in range(len(front) + 1):
                for end in range(len(back) + 1):
                    seen.add(front[start:] + inside + back[:end])
    return seen
