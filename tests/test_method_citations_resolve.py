"""Every citation of the generation method names a section that exists.

WHY THIS FILE EXISTS. Two bounds shipped citing sections of
`docs/spec/generation-method-v1.md` that were never written:

- the clock role's rung and distinctness envelopes cited **G12.9** from
  the day the role landed, when the method stopped at G12.8. For weeks
  a reader who followed either citation found nothing. Then G12.9 was
  written -- about rank agreement between the positions of a joined
  column -- and the two clock citations silently began to RESOLVE, to a
  rule about a different role with a window of `0.02` that means
  nothing for a time of day. The second state is worse than the first:
  a dangling pointer announces itself, and a wrong one does not;
- the kurtosis bound cited **G12.3a** in three docstrings, and the
  method went straight from G12.3 to G12.4. A report counted both
  kurtoses among its approximated facts and told the reader their
  ranges were promises of a method that made no such promise.

Both were found by adversarial review (item P4-G3-R1, items F4 and
F5) and neither could have been found by any test that existed, because
every test asked whether the NUMBERS were right and none asked whether
the citation beside them pointed anywhere. A citation is a promise to
the reader that the rule is written down and findable; this file holds
the code to that promise mechanically.

The rule is not "these particular citations": it is EVERY citation, so
a section named by a bound written next year is checked the day it is
written.
"""

import ast
import pathlib
import re

METHOD = pathlib.Path("docs/spec/generation-method-v1.md")
SOURCE = pathlib.Path("src/synthtwin")

# `G5`, `G12.3`, `G12.3a` -- a section, a subsection, and a subsection
# with a letter. The trailing `(?![\w.])` stops `G12.3` matching inside
# `G12.31` and stops a sentence's full stop being read as a level.
_CITED = re.compile(r"\bG(\d+)(?:\.(\d+)([a-z])?)?(?![\w.])")


# A lettered item inside a section's body: `**(c) A permutation.**`.
# G3.4 defines its three primitives this way and the source cites them
# as `G3.4c`, which is a real and findable thing even though it is not
# a heading of its own.
_LETTERED = re.compile(r"^\*\*\(([a-z])\)")


def _sections() -> "set[str]":
    """Every section id the method defines, headings and lettered items.

    A citation resolves if a reader following it FINDS THE RULE. That
    is true of a heading, and it is equally true of `G3.4c` where G3.4's
    body carries an item labelled `(c)`. What it is not true of is
    `G5.4a`, whose section body has no lettered item at all -- so this
    is a wider net than headings alone and still catches that.
    """
    found: "set[str]" = set()
    head = ""
    for line in METHOD.read_text().splitlines():
        if line.startswith("#"):
            words = line.lstrip("#").strip().split()
            if not words:
                continue
            here = words[0].rstrip(".")
            if _CITED.fullmatch(here):
                found.add(here)
                head = here
            else:
                head = ""
            continue
        lettered = _LETTERED.match(line)
        if lettered and head:
            found.add(f"{head}{lettered.group(1)}")
    return found


def _cited_in(text: str) -> "set[str]":
    """Every method section a piece of text names."""
    found: "set[str]" = set()
    for match in _CITED.finditer(text):
        whole, level, letter = match.group(1), match.group(2), match.group(3)
        if level is None:
            found.add(f"G{whole}")
        else:
            found.add(f"G{whole}.{level}{letter or ''}")
    return found


# THE ONE-LINE FORM ALONE WAS NOT ENOUGH (review item P4-G3-R2-F8).
# `ENVELOPE_NUMERIC_RUNGS` is written across four lines, so a pattern
# anchored to `NAME = "..."` never read it, and pointing it at a
# section that does not exist would have left the other nine matching
# and this file green.
#
# AND THE CENSUS IS DERIVED A DIFFERENT WAY FROM THE CITATIONS (review
# item P4-G3-R3-F6). A first repair counted the constants with the SAME
# pattern that read them, so the two could only ever agree: a constant
# the pattern skipped was missing from both sides and the equality held
# over nothing. The count now comes from PARSING THE MODULE -- every
# module-level assignment to a name beginning `ENVELOPE_`, as Python
# itself sees it -- while the citations are read from the source text.
# A constant the text reader cannot see is then a mismatch, and a
# citation split across string pieces is caught by the same parse.
_NAMES_A_SECTION = re.compile(
    r"docs/spec/generation-method-v1\.md\s+(G\d+(?:\.\d+[a-z]?)?)"
)


def _envelope_nodes() -> "list[tuple[str, str]]":
    """Every `ENVELOPE_*` constant and its full string value, parsed.

    Read with `ast`, so an assignment written across four lines, or
    built from several adjacent string pieces, is one value here
    exactly as it is one value at runtime.
    """
    tree = ast.parse((SOURCE / "validation.py").read_text())
    found: "list[tuple[str, str]]" = []
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        for target in node.targets:
            if not isinstance(target, ast.Name):
                continue
            if not target.id.startswith("ENVELOPE_"):
                continue
            value = ast.literal_eval(node.value)
            if isinstance(value, str):
                found = found + [(target.id, value)]
    return found


def _declared_envelopes() -> int:
    """How many envelope constants the module defines, by parsing it."""
    return len(_envelope_nodes())


def _envelopes() -> "list[tuple[str, str]]":
    """Every envelope constant and the method section it names."""
    found: "list[tuple[str, str]]" = []
    for name, value in _envelope_nodes():
        said = _NAMES_A_SECTION.search(value)
        if said:
            found = found + [(name, said.group(1))]
    return found


def test_the_method_defines_the_sections_this_test_relies_on() -> None:
    """The vacuity guard: the reader of headings must find headings.

    If the heading pattern ever stopped matching, every assertion below
    would pass against an empty document and this file would check
    nothing at all.
    """
    sections = _sections()
    assert len(sections) > 40, (
        f"only {len(sections)} sections were read out of the method, so "
        "the heading pattern has stopped matching and every check in "
        "this file is now vacuous"
    )
    for expected in ("G12.3", "G12.3a", "G12.9", "G12.10", "G12.11"):
        assert expected in sections
    assert "G3.4c" in sections, (
        "the reader of lettered items has stopped working, and the "
        "check below would then flag a citation that does resolve"
    )
    assert "G5.4a" not in sections, (
        "G5.4 has no lettered items; if this ever passes, the reader "
        "has become too generous to catch the miscitation it was "
        "written for"
    )


def test_every_envelope_constant_names_a_section_that_exists() -> None:
    """The nine `ENVELOPE_*` citations the quality report prints.

    These are the ones a READER meets: the report prints them beside a
    verdict so a person can go and read the rule the verdict rests on.
    """
    named = [section for _name, section in _envelopes()]
    assert len(named) == _declared_envelopes(), (
        f"{len(named)} envelope citations were read out of "
        f"{_declared_envelopes()} constants, so this check no longer "
        "covers every one of them -- which is exactly the hole review "
        "item P4-G3-R2-F8 found"
    )
    sections = _sections()
    missing = [one for one in named if one not in sections]
    assert not missing, (
        "a quality report sends its reader to a section of the "
        f"generation method that does not exist: {missing}"
    )


def test_no_two_envelope_constants_share_a_section() -> None:
    """Two bounds citing one section is how the clock defect hid.

    It is not wrong in principle for two facts to share a rule, but
    every envelope here is a DIFFERENT bound on a different role, so a
    shared citation means one of them is pointing at the other's rule.
    """
    seen: "dict[str, str]" = {}
    for name, section in _envelopes():
        assert section not in seen, (
            f"{name} and {seen[section]} both cite {section}; one of "
            "them is pointing at a rule written for the other"
        )
        seen[section] = name


# What a citation looks like in prose: the words `method` or `methods`
# or the file's own name, then one or more section ids joined by
# commas, `and`, `to` or `or`. ALL of them are read, not just the first
# (review item P4-G3-R5-F4): `# methods G99.1 and G99.2` used to have
# its second id ignored entirely.
_IN_PROSE = re.compile(
    r"(?:methods?|generation-method-v1\.md)\s+"
    r"(G\d+(?:\.\d+[a-z]?)?"
    # An Oxford comma puts BOTH a comma and a word between the last two
    # ids -- `G12.2, G12.3, and G99.1` -- and a pattern taking one or
    # the other stopped at the comma and dropped the last id in silence
    # (review item P4-G3-R6-F8).
    r"(?:[\s,]*(?:and|to|or)?[\s,]*G\d+(?:\.\d+[a-z]?)?)*)"
)


def _cited_in_prose(text: str) -> "set[str]":
    """Every method section a body of prose names."""
    found: "set[str]" = set()
    for run in _IN_PROSE.findall(text):
        for one in re.findall(r"G\d+(?:\.\d+[a-z]?)?", run):
            found.add(one)
    return found


def test_every_method_citation_in_the_source_resolves() -> None:
    """And the ones in docstrings, which is where G12.3a hid.

    A docstring citation is read by the next implementer rather than by
    a user, which makes it easier to leave dangling and no less of a
    promise. `_tails_window` said "method G12.3a" for the whole of its
    life against a document that had no such section.

    WHAT THIS COVERS, said exactly, because the file used to promise
    more than it checked (review item P4-G3-R5-F4). It reads the whole
    of each governed file rather than one line at a time, so a citation
    wrapped across lines is caught; it reads EVERY id in a list, not
    the first; and it covers the product source AND the specifications
    and plans, not just `src/`. What it does not cover is a citation
    written in some other form of words entirely -- there is no way to
    check prose nobody can recognise as a citation.
    """
    sections = _sections()
    governed = sorted(SOURCE.glob("*.py")) + sorted(
        pathlib.Path("docs").rglob("*.md")
    )
    trouble: "list[str]" = []
    for path in governed:
        if path.name == METHOD.name:
            continue
        for one in sorted(_cited_in_prose(path.read_text())):
            if one not in sections:
                trouble = trouble + [f"{path.name}: {one}"]
    assert not trouble, (
        "a citation names a section of the generation method that does "
        f"not exist: {sorted(set(trouble))}"
    )


def test_the_prose_reader_takes_every_id_in_a_list() -> None:
    """The vacuity guard on the reader above.

    A reader that stopped at the first id would pass over
    `methods G12.2 and G99.1` in silence, which is the hole review item
    P4-G3-R5-F4 found.
    """
    assert _cited_in_prose("see methods G12.2 and G99.1 for this") == {
        "G12.2",
        "G99.1",
    }
    assert _cited_in_prose("method G5.1, G5.2, G5.3") == {
        "G5.1",
        "G5.2",
        "G5.3",
    }
    assert _cited_in_prose("no citation here at all") == set()
