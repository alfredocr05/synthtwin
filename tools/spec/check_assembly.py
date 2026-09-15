"""Mechanical checks over the version 6 contract, section by section.

Written because the one identifier collision this build has found so
far was found by READING -- a section had numbered its note forms in
lettered groups whose letters were already invariant families in the
same document, so `D1` and `B5` each named two different rules. That
was luck. A document of this size has more identifiers than a person
checks reliably, and the failure it produces is the worst kind: two
implementations obeying different rules while both believe they are
obeying the text.

The checks here are the ones a machine can settle and a reader cannot:

1. **Identifier uniqueness.** Every identifier a section DEFINES,
   collected across the whole build, with duplicates named.
2. **Cross-references resolve.** Every identifier a section CITES,
   checked against the set of defined ones.
3. **No delta framing.** The self-contained document may not say
   "supersedes", "carried", "unchanged from version 5", "as version 4
   has it", or carry a `C6-` LETTER identifier. Each of those means a
   rule is being pointed at rather than stated, which is exactly what
   the rewrite exists to end.
4. **Stated counts match written lists.** Where a section says an
   enumeration has N members and then writes the members out, the two
   are compared.

It reads the assembled contract, `docs/spec/profile-contract-v6.md`, by
default: that document is the only source since residual R-P4-113
closed, when the section build folder and its assembler were deleted.
The argument may still name another document or a folder of section
files. The shipped contract is
checked on every suite by `tests/test_contract_self_check.py`, which
holds it to zero items. It exits non-zero on
any item, so it can be a gate rather than a report somebody reads.

This is a build tool, not product code: nothing here is imported by
`synthtwin` and nothing here runs at profile, generate or validate
time.
"""

from __future__ import annotations

import argparse
import collections
import pathlib
import re
import sys

# An identifier DEFINITION: a bolded identifier opening a clause, as in
# "**D1 (the format bindings).**" or "**C6-12.**". The families are the
# lettered ones the sealed documents and the test suite cite by name.
_FAMILIES = (
    "A|AF|B|C6|D|E|F|I|K|L|LT|M|N|NF|NG|P|Q|RM|S|T|TY|U|V|W|X"
)
# A definition appears in these shapes in this document, and all of
# them are real: a bolded clause opener, a bolded "Invariant Nn."
# opener, a row of the one-list invariant table, a heading, a bolded
# opener at the start of a bullet (`- **P9c (the sum).**`), and a
# bolded opener starting a new sentence part way along a line
# (`...the same thing. **P5b (the sum).**`). A checker that knew only
# the first would report every other shape as a dangling citation, and
# a reader would learn to ignore it -- which is what happened: on the
# shipped contract it reported eight items that were not defects.
_DEFINITION = re.compile(
    r"(?:^(?:\*\*(?:Invariant\s+)?|\|\s*|#{2,6}\s+)"
    r"|^[ \t]*[-*][ \t]+\*\*(?:Invariant\s+)?"
    r"|(?<=[.:;)][ \t])\*\*(?:Invariant\s+)?)"
    r"(" + _FAMILIES + r")-?(\d+[a-z]?)"
    # A DEFINITION opener, not a mention. "**D5 (which clock)**" and
    # "| D5 |" define; "**D5 is a published fact...**" discusses one.
    # The difference is what follows the identifier, so the lookahead
    # admits punctuation, a parenthetical or a table pipe, and refuses
    # a running word. A point followed by a letter or a figure is not
    # a full stop: `**P5b.a — ...**` is a CASE of P5b, not P5b again.
    # And a comma followed by another identifier is a LIST being
    # discussed -- "**P6c, P7c and P9c do not reach producer obligation
    # XW-P**" -- and not a rule being opened.
    r"(?=\.(?![A-Za-z0-9])|,(?!\s*(?:" + _FAMILIES + r")-?\d)|:|\)"
    r"|\s*\||\*\*|\s*\(|\s*—)",
    re.MULTILINE,
)

_IDENTIFIER = r"(?:" + _FAMILIES + r")-?\d+[a-z]?"

# A definition in PROSE: "One binds, and its identifier is Q20." The
# paragraph it opens states the rule, so the identifier is defined
# there. The plural, "their identifiers are P6c, P7c and P9c", names
# rules that are each then opened as a bullet of their own; a prose name
# already opened in its own region adds no second definition, so the
# two shapes are not counted as a collision.
_PROSE_DEFINITION = re.compile(
    r"\bidentifiers?\s+(?:is|are)\s+("
    + _IDENTIFIER
    + r"(?:(?:,\s*|,?\s+and\s+)"
    + _IDENTIFIER
    + r")*)"
)

# A LANDING NAME, not a rule: "landing L16", "(landing L18)". The `L`
# family is also the ladder invariants' (L1, L3), so a landing name
# reads as a citation of an invariant nobody wrote. It is struck out
# before citations are collected, and only where the word "landing"
# stands directly before it, across a line break included.
_LANDING = re.compile(
    r"\blandings?\s+L\d+[a-z]?(?:(?:,\s*|,?\s+and\s+)L\d+[a-z]?)*"
)

# A CITATION: the same shape, anywhere in running text, not at the
# start of a bolded clause. Deliberately narrow -- it must be preceded
# by a word boundary and followed by one, so "D1" inside a wire
# spelling or a hash does not count.
_CITATION = re.compile(
    r"(?<![A-Za-z0-9_-])(" + _FAMILIES + r")-?(\d+[a-z]?)(?![A-Za-z0-9_])"
)

# Phrases that mean a rule is pointed at rather than stated.
_DELTA_FRAMING = (
    ("supersede", "a self-contained document replaces nothing"),
    ("carried by reference", "the rule must be written out"),
    ("unchanged from version 5", "state the rule, not its history"),
    ("as version 4 has it", "state the rule, not its history"),
    ("version 5's rule stands", "state the rule, not its history"),
)

# A `C6-` LETTER identifier: these existed only to name what they
# superseded, under a convention amendment A-P4-11 abolishes.
# Inline code: a wire spelling or an example value, never an identifier.
_CODE_SPAN = re.compile(r"`[^`\n]*`")

_C6_LETTER = re.compile(r"\bC6-[A-Z]{2,}\b")

# "**Roles (13):**" and the like -- a count stated beside a list.
_STATED_COUNT = re.compile(r"\*\*([^*]{2,60}?)\s*\((\d+)\)[:.]?\*\*")

_WORDS = {
    "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7,
    "eight": 8, "nine": 9, "ten": 10, "eleven": 11, "twelve": 12,
    "thirteen": 13, "seventeen": 17, "eighteen": 18, "twenty-three": 23,
    "thirty-eight": 38, "forty-one": 41,
}


def _sections(folder: pathlib.Path) -> list[pathlib.Path]:
    """Every section file, excluding the notes that sit beside them.

    A path naming one document is that document alone.
    """
    if folder.is_file():
        return [folder]
    return sorted(
        path
        for path in folder.glob("*.md")
        if not path.name.endswith("_meta.md")
        and path.name != "ASSEMBLY.md"
    )


def _identifier(match: re.Match[str]) -> str:
    family, number = match.group(1), match.group(2)
    return f"{family}-{number}" if family == "C6" else f"{family}{number}"


# Two sections say of THEMSELVES that they restate rules stated
# elsewhere: the one-list invariant walk, and the enumeration appendix.
# A rule appearing in its own section and again in one of those is not
# a collision -- it is the restatement doing its job. What IS a defect
# is a restatement row for a rule nothing defines, so the two are
# counted separately rather than merged.
_RESTATEMENT = ("a8a", "a8b1", "a8b2", "a14app")

# Four families are stated ONLY in the one-list section, and it says so
# in its own opening: their subject is spread across several sections
# and a home in any one of them would be a home the others reached by
# inference. A FIFTH family appearing only there is still reported --
# that would be a rule nobody wrote, which is what this check is for.
_ONE_LIST_FAMILIES = ("X", "M", "P", "NG")
_REGION = re.compile(r"^<!-- ([a-z0-9_]+): ", re.MULTILINE)


def _regions(text: str) -> list[tuple[str, int, int]]:
    """The assembled document, split by its section markers."""
    marks = list(_REGION.finditer(text))
    if not marks:
        return [("", 0, len(text))]
    spans = []
    for index, mark in enumerate(marks):
        end = marks[index + 1].start() if index + 1 < len(marks) else len(text)
        spans.append((mark.group(1), mark.start(), end))
    return spans


def _restates(name: str) -> bool:
    return any(name.startswith(prefix) for prefix in _RESTATEMENT)


def check_identifiers(paths: list[pathlib.Path]) -> list[str]:
    """Every identifier defined once, and every citation resolving."""
    items: list[str] = []
    defined: dict[str, list[str]] = collections.defaultdict(list)
    restated: dict[str, list[str]] = collections.defaultdict(list)

    for path in paths:
        text = path.read_text(encoding="utf-8")
        for region, start, end in _regions(text):
            bucket = restated if (
                _restates(region) or _restates(path.stem)
            ) else defined
            opened: set[str] = set()
            for match in _DEFINITION.finditer(text[start:end]):
                line = text[: start + match.start()].count("\n") + 1
                bucket[_identifier(match)].append(f"{path.name}:{line}")
                opened.add(_identifier(match))
            for match in _PROSE_DEFINITION.finditer(text[start:end]):
                line = text[: start + match.start()].count("\n") + 1
                for named in _CITATION.finditer(match.group(1)):
                    if _identifier(named) not in opened:
                        bucket[_identifier(named)].append(
                            f"{path.name}:{line}"
                        )

    for name, sites in sorted(defined.items()):
        if len(sites) > 1:
            items.append(
                f"DUPLICATE IDENTIFIER {name} defined at {', '.join(sites)}"
                " -- one identifier, two rules, and a reader cannot tell"
                " which is meant"
            )

    known = set(defined)
    # A citation is plain text. Wire spellings, example values and key
    # names live in backticks, and one of them -- a prefixed code column
    # written `A-101` -- reads as an identifier if inline code is
    # scanned. Strip it before looking for citations.
    for name, sites in sorted(restated.items()):
        if name[:2] in _ONE_LIST_FAMILIES or name[:1] in _ONE_LIST_FAMILIES:
            continue
        if name not in known:
            items.append(
                f"RESTATED BUT NEVER STATED: {name} appears at {sites[0]}"
                " in a section that restates rules stated elsewhere, and no"
                " section states it"
            )

    for path in paths:
        text = _CODE_SPAN.sub(" ", path.read_text(encoding="utf-8"))
        text = _LANDING.sub(" ", text)
        cited = {_identifier(m) for m in _CITATION.finditer(text)}
        for name in sorted(cited - known - set(restated)):
            items.append(
                f"{path.name}: cites {name}, which no section defines"
            )
    return items


# The section that STATES the no-carrying rule has to use these words
# in order to say the document contains none of them. Exempting it by
# name would exempt too much, so the test is on the sentence: a phrase
# inside a clause that denies it is a definition, not a delta.
_NEGATORS = (
    "no ", "not ", "never", "nothing", "none", "cannot", "may not",
    "would be defective", "no longer", "n't",
)


def _marked_paragraphs(lines: list[str]) -> set[int]:
    """Line numbers inside a paragraph carrying the exemption marker.

    The marker excuses the paragraph it opens, and nothing else: the
    run ends at the next blank line, so an exemption cannot spread
    down a document by being forgotten.
    """
    marked: set[int] = set()
    inside = False
    for number, line in enumerate(lines, 1):
        if _MARKER in line:
            inside = True
        elif not line.strip():
            inside = False
        if inside:
            marked.add(number)
    return marked


def _denied(line: str, phrase: str) -> bool:
    """True where the line uses the phrase in order to forbid it."""
    lowered = line.lower()
    position = lowered.find(phrase)
    clause = lowered[max(0, position - 160) : position + len(phrase) + 60]
    return any(negator in clause for negator in _NEGATORS)


# An explicit, auditable exemption. A paragraph explaining WHY the
# document is self-contained has to describe the delta it replaced, and
# no sentence test separates that from a rule being pointed at. So the
# author marks it, in the text, where a reader will meet the mark
# beside the words it excuses.
_MARKER = "<!-- framing-ok:"


def check_framing(paths: list[pathlib.Path]) -> list[str]:
    """No rule may be pointed at instead of stated."""
    items: list[str] = []
    exempted: list[str] = []
    for path in paths:
        lines = path.read_text(encoding="utf-8").split("\n")
        marked = _marked_paragraphs(lines)
        for number, line in enumerate(lines, 1):
            if number in marked:
                continue
            lowered = line.lower()
            for phrase, why in _DELTA_FRAMING:
                if phrase in lowered:
                    if _denied(line, phrase):
                        exempted.append(
                            f"  {path.name}:{number}: {phrase!r} used to"
                            " forbid it"
                        )
                        continue
                    items.append(
                        f"{path.name}:{number}: delta framing {phrase!r}"
                        f" -- {why}"
                    )
            for match in _C6_LETTER.finditer(line):
                items.append(
                    f"{path.name}:{number}: `C6-` letter identifier"
                    f" {match.group(0)} -- it names a supersession that no"
                    " longer exists"
                )
    if exempted:
        # Printed rather than silently dropped: an exemption a reader
        # cannot see is an exemption that will one day be wrong.
        print(
            f"{len(exempted)} framing phrase(s) exempted as definitions:"
        )
        for line in exempted:
            print(line)
        print()
    return items


def check_counts(paths: list[pathlib.Path]) -> list[str]:
    """A stated count, against the list written beside it."""
    items: list[str] = []
    for path in paths:
        text = path.read_text(encoding="utf-8")
        for match in _STATED_COUNT.finditer(text):
            subject, stated = match.group(1), int(match.group(2))
            window = text[match.end() : match.end() + 1400]
            window = window.split("\n\n")[0]
            written = len(set(re.findall(r"`([^`]+)`", window)))
            if written and written != stated:
                line = text[: match.start()].count("\n") + 1
                items.append(
                    f"{path.name}:{line}: {subject!r} states {stated}"
                    f" and {written} distinct wire spellings follow it"
                )
    return items


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "folder",
        nargs="?",
        default="docs/spec/profile-contract-v6.md",
        help="the assembled contract by default, which is the only source;"
        " or another document, or a folder of section files",
    )
    parser.add_argument(
        "--counts",
        action="store_true",
        help="also compare stated counts with the lists beside them,"
        " which is advisory: it reads prose and will have opinions",
    )
    arguments = parser.parse_args()

    folder = pathlib.Path(arguments.folder)
    if not folder.is_dir() and not folder.is_file():
        print(f"no such folder or document: {folder}", file=sys.stderr)
        return 2

    paths = _sections(folder)
    if not paths:
        print(f"no section files in {folder}", file=sys.stderr)
        return 2

    items = check_identifiers(paths) + check_framing(paths)
    if arguments.counts:
        items += check_counts(paths)

    for item in items:
        print(item)
    print(
        f"\n{len(paths)} sections, {len(items)} item"
        f"{'' if len(items) == 1 else 's'}"
    )
    return 1 if items else 0


if __name__ == "__main__":
    raise SystemExit(main())
