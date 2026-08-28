"""P2-D11: the repository-wide claim inventory, asserted rather than kept.

SEVEN FAMILIES OF CLAIM LIVE HERE. The first is the RECORD claim, and it
is what this file was written for; it is described immediately below.
The second arrived with review item P2-C1-F7 and is described under
"THE SECOND FAMILY" further down: what the twin CARRIES, which phase
the project is in, which commands exist, and how many libraries it
depends on. The third arrived with review item P3-V3-F8 and is the one
that is not a list of sentences at all: how MANY commands the tool has
and how many files a run leaves behind, counted from the product and
checked against every surface. The fourth arrived with the owner's
ruling of 2026-08-14 and is described under "THE FOURTH FAMILY" at the
foot: a confidentiality guarantee this product deliberately stopped
making, which no surface may go on making for it. The fifth counts
which wire version synthtwin speaks, and the sixth what the description
keeps of the words a person typed. The seventh arrived with the owner's
instruction of 2026-08-26: an EXEMPTION FROM AN OBLIGATION, which being
synthetic does not grant and which no surface here may say it does.
They share this file because they share a failure mode -- true text
going stale on a surface nobody re-read -- and because a reader who
trusts one of these sentences has no way to tell which family it came
from.

THE COUNT IN THE SENTENCE ABOVE SAID "FOUR" UNTIL 2026-08-26, while six
families stood in the file. The fifth and sixth were added without it
moving. That is this file's own failure mode landing on this file, it
is recorded rather than quietly corrected, and it is why the seventh
carries a test that counts the family headings.

WHAT WENT WRONG, AND WHY A TEST IS THE ONLY REPAIR THAT HOLDS. synthtwin
said, in eight places, that the twin holds no record of yours: twice in
the charter, twice on the front page, once in the package docstring,
once in the installable package's own description, once in the command's
help, and once in the summary printed on every profiling run. That is a
promise no tool which reproduces published counts EXACTLY can keep: an
11-row single-column table whose one label clears the small-cell floor
publishes that label with the count 11, so the twin must write it in all
11 rows, and each of those rows is a row the real table has. Nothing was
copied and no source table was opened; the arithmetic left no other
answer. The plan (P2-D11) therefore replaces the categorical claim with a
QUALIFIED one -- a claim about provenance -- and requires the
institutional-handling rule to name all THREE artifacts a run produces
rather than the profile alone.

Fixing eight sentences is easy. Keeping them fixed is not: this text
lives on surfaces owned by different work -- a charter, a readme, a
security document, a package docstring, command output, the summary a
person reads after profiling, the report written beside every twin --
and the categorical form is the one that comes naturally to anybody
writing a sentence about a synthetic twin. So the inventory is a test.

WHAT IT CHECKS, IN TWO DIRECTIONS. A one-directional test is worth
little here. Deleting a sentence satisfies a ban, and adding a sentence
nobody reads satisfies a requirement; only both together mean the
surface actually carries the qualified claim.

* NEGATIVE: no surface in `SURFACES` contains any categorical form in
  `RETIRED_CLAIMS`, in any capitalization. A surface that quotes the
  retired wording to say it was retired trips this too, deliberately:
  an exception list is how a ban like this rots, so the surfaces that
  discuss the withdrawal describe the old wording instead of spelling
  it.
* POSITIVE: every surface in `CLAIM_BEARING` carries all four marks of
  the qualified claim -- the provenance statement, the acknowledgement
  that exact allocation can force the match, the absence of a formal
  guarantee, and the three-artifact handling rule.

THE SECOND FAMILY: WHAT THE TWIN CARRIES, AND WHAT IS BUILT (review
item P2-C1-F7). The record claim was repaired on every surface and the
inventory went green while, on those same surfaces, four other material
claims were false.

* RELATIONSHIP FIDELITY. The package docstring promised "same
  relationships" and the charter promised the same relationships and a
  relationship summary among the outputs. This phase generates every
  column independently and publishes eight EMPTY relationship slots, so
  those were claims about a capability that does not exist. Measured
  rather than argued: a table of two identical columns, every real row
  holding `left == right`, produces a twin in which zero rows of 200
  do. Someone who believed the docstring could develop and accept code
  on the twin that behaves oppositely on every real row.
* PHASE STATUS. The front page said Phase 1 and the charter marked
  Phase 0 as current, months after both closed.
* COMMAND AVAILABILITY. The front page told a reader that generation
  was planned, while `synthtwin generate` was installed and working --
  a zero-code user's whole route to the product, described as absent.
* DEPENDENCY COUNT. The front page said numpy was not a dependency and
  the security document counted one third-party function, after numpy
  had returned as a declared direct dependency with its own enumerated
  scanner surface.

The repair is the same shape as the first family's: a negative list of
the claim forms that may never appear, a positive list of the marks
every deciding surface must carry, and a vacuity floor proving the
negative list still matches the text it was written to keep out. What
the four positive marks say is the plain truth of this phase -- the twin
reproduces the published facts of each column ON ITS OWN, it carries no
cross-column structure of any kind, rows are treated as independent and
the grain is undescribed, and cross-column structure arrives in a later
phase.

WHY THE SURFACE LISTS DIFFER BETWEEN THE TWO FAMILIES. The record claim
is decided at the moment a person moves a file, so it belongs on the
surfaces a person reads before moving one. The structure claim is
decided at the moment a person draws a conclusion from a twin, so it
additionally belongs in the generator itself: `generation.py` is what
makes columns independently, and a module whose docstring states its
guarantees (charter rule) may not leave out the largest one.

WHAT IS DELIBERATELY OUT OF SCOPE, AND WHERE THAT LINE MOVED. The
review record is the project's audit trail: it records what was
claimed, reviewed, rejected and repaired at each date, and rewriting it
to match today's wording would destroy the very thing it exists to
preserve. It makes no claim to a user. `tests/` is out for the same
reason, plus the obvious one that this file must be able to name the
retired forms.

`docs/plans/` was out on that same reasoning and it was too wide by one
family (review item P3-V6-F3). A plan that GOVERNS is not a record of
what was once thought: it is edited by amendment, it fixes what the code
owes, and an institution's reviewer reads it. So the two GOVERNING plans
are walked by the withdrawn-defence ban -- `DEFENCE_SURFACES` -- because
a promise about what somebody can be stopped from doing is normative
wherever it stands. The other three families still stop at the surfaces
above, because they count what the product HAS today and a roadmap says
what it will have, in as many words, on purpose. The plans of closed
phases and every review stay out entirely.

The failure messages here name the file and say what to write, because
whoever trips this test is mid-sentence in a document, not debugging.
"""

import ast
import contextlib
import io
import os
import pathlib
import re

import pytest

import dispositions
import fixtures
from synthtwin import (
    cli,
    contract,
    errors,
    profile,
    reading,
    summary,
    taxonomy,
)

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]
PACKAGE = REPO_ROOT / "src" / "synthtwin"

# Every surface that speaks to a user, an auditor or a packaging index
# in synthtwin's own voice. The three spec documents are included
# because an institution's reviewer reads them as the normative
# statement of what the profile, the twin and the quality report carry.
#
# THE VALIDATION METHOD JOINED LATE, and its absence was a gap of the
# kind this file exists to close: it is the normative statement of what
# a quality report may say about a measured file -- the document an
# institution's reviewer reads before deciding whether a report may
# leave the building -- and until the fourth family below was written
# it was the one specification no ban in this file covered. Adding it
# cost nothing: every check here was already true of it.
SURFACES = (
    "CLAUDE.md",
    "AGENTS.md",
    "README.md",
    "SECURITY.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "pyproject.toml",
    "src/synthtwin/__init__.py",
    "src/synthtwin/canonical.py",
    "src/synthtwin/cli.py",
    "src/synthtwin/contract.py",
    "src/synthtwin/errors.py",
    "src/synthtwin/generation.py",
    "src/synthtwin/parsing.py",
    "src/synthtwin/paths.py",
    "src/synthtwin/profile.py",
    "src/synthtwin/quality.py",
    "src/synthtwin/reading.py",
    "src/synthtwin/rendering.py",
    "src/synthtwin/summary.py",
    "src/synthtwin/taxonomy.py",
    "src/synthtwin/validation.py",
    "src/synthtwin/writing.py",
    "docs/spec/profile-contract-v4.md",
    "docs/spec/profile-contract-v5.md",
    # THE GOVERNING CONTRACT IS A SURFACE LIKE ANY OTHER, and it has to
    # be: the ban's positive half asks that SOME surface state the
    # shipped version, and the contract that governs it is where a
    # reader looks first. Leaving it out let the ban be satisfied by
    # silence on the one document whose whole job is to say what the
    # tree speaks.
    "docs/spec/profile-contract-v6.md",
    "docs/spec/generation-method-v1.md",
    "docs/spec/validation-method-v1.md",
)

# THE SURFACES THE WITHDRAWN-DEFENCE BAN WALKS, which is every one of
# the above and the GOVERNING PLANS besides (review item P3-V6-F3).
#
# The ban named the plan's own P3-D3 as one of the passages the
# 2026-08-14 ruling had to correct, and the plan was not walked -- so
# the guard claimed a reach it did not have, which is the shape this
# whole file exists to refuse. A plan that GOVERNS is not audit trail:
# it is edited by amendment, it decides what the code owes, and an
# institution's reviewer reads it as normative.
#
# WHY THIS FAMILY AND NOT THE OTHER THREE. The other families count what
# the product HAS -- how many commands, how many files, which capability
# is built -- and a plan states those about phases that do not exist
# yet, in as many words, on purpose. Holding a roadmap to a count of
# today's commands would be holding it to the one thing it is not for.
# A PROMISE about what somebody can be stopped from doing is different:
# it is normative wherever it is written, and a plan that makes it makes
# it. `test_every_governing_document_is_a_surface` holds this list to
# the disposition seal's own governing set, so the next governing
# document cannot be left out by being forgotten.
DEFENCE_SURFACES = SURFACES + (
    # Round 1 item 4: the working-state page CLAUDE.md makes the
    # mandatory first read, and the plain-language status page, were
    # both outside every ban -- while STATE.md itself asserts that the
    # seventh family guards this rule.
    "docs/STATE.md",
    "STATUS.md",
    "docs/plans/phase-2-generator.md",
    "docs/plans/phase-3-product.md",
    "docs/plans/phase-4-columns.md",
)

# The categorical forms, retired by P2-D11. Each is the shape of a
# sentence that promises non-equality rather than provenance. They are
# matched as substrings of the lowercased file, so a longer sentence
# containing one is caught too.
RETIRED_CLAIMS = (
    "no real records",
    "no real record",
    "not one real record",
    "zero real records",
    "zero real record",
    "not a single real record",
    "no real rows",
    "no real row",
    "zero real rows",
    "zero real row",
    "none of your real rows",
    "none of the real rows",
    "not one real row",
)

# ---------------------------------------------------------------------
# THE THIRD FAMILY: WHAT THE PRODUCT HAS, COUNTED FROM THE PRODUCT
# (review item P3-V3-F8)
# ---------------------------------------------------------------------
#
# The two families above are lists of sentences. That is what made the
# third one possible: `synthtwin validate` shipped, and the sentences
# saying the tool has two commands and a run leaves three artifacts
# stayed exactly where they were, on six surfaces, while every test in
# this file passed. The guard could not see them because it was looking
# for wording somebody had thought to write down, and nobody writes down
# the sentence they are about to forget.
#
# So the third family is not a list. It is a COUNT, taken from the
# product itself: how many commands the shipped command line offers, and
# how many files a full run leaves on disk. Every surface is then held to
# those two numbers, and a fourth command or a sixth output file makes
# every stale total in the repository red on the commit that ships it,
# with no list to remember to update.


def _shipped_command_words() -> "tuple[str, ...]":
    """`synthtwin <word>` for every word the shipped command line takes.

    Read from the parser the product builds, not from a list here: the
    parser is what a person's typing actually meets, so a command that
    exists is one this returns and a command that does not is one it
    cannot. The route is the parser's own refusal of a word it does not
    know, which names the argument and then lists the choices -- the one
    place argparse states the whole set in text.

    Guarantees:

    - Inputs: none.
    - Determinism: a fixed function of the shipped parser; nothing
      outside this repository is consulted and nothing is written.
    - Errors raised: `AssertionError` if the refusal cannot be read, so
      that a parser this can no longer question fails loudly rather than
      returning a short list that would make every check below vacuous.
    - Boundary: no file is opened and no command is run; the parser is
      built in this process and handed one word it will reject.
    """
    complaint = io.StringIO()
    with (
        contextlib.redirect_stderr(complaint),
        contextlib.suppress(SystemExit),
    ):
        cli._parse_arguments(["a-word-no-command-can-be"])
    said = complaint.getvalue()
    found = re.search(r"argument command:[^(]*\(choose from ([^)]*)\)", said)
    assert found is not None, (
        "The shipped command line no longer refuses an unknown command "
        "in a form this test can read, so the command inventory below "
        "would be derived from nothing. What argparse said was:\n"
        f"{said}\n"
        "Update this function to read the new form -- never replace it "
        "with a hand-written list, which is the defect review item "
        "P3-V3-F8 exists to close."
    )
    # Both spellings argparse has used, because the words are read out
    # of a sentence it writes and it has rewritten that sentence: 3.10,
    # 3.11, 3.13 and 3.14 quote each choice, and 3.12 does not. Reading
    # only the quoted form returned NOTHING on 3.12 and turned every
    # check below vacuous -- caught by CI, which is the only place 3.12
    # runs, and only after the version check above it stopped skipping
    # the whole job.
    words = tuple(
        word
        for word in (
            piece.strip().strip("'\"") for piece in found.group(1).split(",")
        )
        if word and all(c.islower() or c == "-" for c in word)
    )
    assert len(words) >= 3, (
        "The shipped command line offers fewer than the three commands "
        f"this project has built ({list(words)}). If a command was "
        "removed, say so on every surface in the same commit; if this "
        "stopped reading the parser correctly, fix the reading."
    )
    return tuple(f"synthtwin {word}" for word in words)


# What a full run leaves on disk, counted the same way: by reading the
# endings the product's own modules give the files they write. A run is
# `profile`, then `generate`, then `validate`, and the five names below
# are every file those three commands create. The filter is the ending
# itself -- the transaction's working names end `.synthtwin-part` and
# `.synthtwin-kept` and are not files a run leaves behind, so they are
# not here and cannot be.
_OUTPUT_ENDINGS = (".json", ".csv", ".txt")


def _text_of(node: ast.expr) -> "str | None":
    """The string this expression is, or None where it is not one.

    Constants, implicit and explicit concatenation of them, and an
    f-string with nothing to fill in. What this is NOT is an evaluator:
    a name, a call, or a field of a value is not text this can read, and
    the run-driven count below is what covers an output name arrived at
    that way.
    """
    if isinstance(node, ast.Constant):
        return node.value if isinstance(node.value, str) else None
    if isinstance(node, ast.BinOp) and isinstance(node.op, ast.Add):
        left = _text_of(node.left)
        right = _text_of(node.right)
        return None if left is None or right is None else left + right
    if isinstance(node, ast.JoinedStr):
        pieces: list[str] = []
        for part in node.values:
            piece = _text_of(part)
            if piece is None:
                return None
            pieces.append(piece)
        return "".join(pieces)
    return None


def _output_endings_in(source: str) -> "list[str]":
    """Every output-file ending one module's syntax declares.

    Takes source as TEXT, so the reading can be put through each way a
    name can be spelled rather than trusted -- which is what
    `test_the_output_reading_sees_a_name_however_it_is_spelled` does
    with the four spellings review item P3-V4-F7 named.
    """
    found: list[str] = []
    for node in ast.walk(ast.parse(source)):
        if isinstance(node, ast.Assign):
            value: ast.expr | None = node.value
        elif isinstance(node, ast.AnnAssign):
            value = node.value
        else:
            continue
        if value is None:
            continue
        ending = _text_of(value)
        if ending is None:
            continue
        if ending.endswith(_OUTPUT_ENDINGS) and ending not in found:
            found.append(ending)
    return found


def _shipped_output_suffixes() -> "tuple[str, ...]":
    """Every ending a file a full run leaves behind can carry.

    HOW THE SPELLING STOPPED MATTERING (review item P3-V4-F7). This read
    the source for `NAME_SUFFIX = "..."` in double quotes at the start
    of a line, so a sixth output declared as `_AUDIT: str = '-audit.txt'`
    -- a typed constant, single-quoted, under a name ending in nothing
    in particular -- left the total at five and every stale "five files"
    sentence in the repository green. It now reads the package's own
    SYNTAX: every assignment whose value is a string, however it is
    spelled, named or annotated.

    A name this cannot read at all -- built by a call, or by joining a
    stem to something -- is not covered here and is not meant to be.
    `test_a_full_run_leaves_exactly_the_files_this_file_counts` drives
    the three commands and counts what lands on the disk, so an output
    arrived at by any route whatever is caught there.

    Guarantees:

    - Inputs: none; reads the package's own modules from this
      repository.
    - Determinism: sorted; a fixed function of the tracked source.
    - Errors raised: `AssertionError` when fewer are found than the
      three commands can write, because a derivation that quietly
      returns a short list is worse than a hand-written one.
    - Boundary: reads only `src/synthtwin/*.py`, and only their text.
    """
    found: list[str] = []
    for module in sorted(PACKAGE.glob("*.py")):
        for ending in _output_endings_in(module.read_text(encoding="utf-8")):
            if ending not in found:
                found.append(ending)
    assert len(found) >= 5, (
        "Fewer output-file endings were found in the package than the "
        f"three commands write ({sorted(found)}). Either an output name "
        "stopped being a module constant -- in which case give it one, "
        "so that what a run writes stays countable -- or this reading "
        "broke. Do not replace it with a list."
    )
    return tuple(sorted(found))


COMMAND_WORDS = _shipped_command_words()
COMMAND_TOTAL = len(COMMAND_WORDS)
RUN_OUTPUT_SUFFIXES = _shipped_output_suffixes()
FILE_TOTAL = len(RUN_OUTPUT_SUFFIXES)
# The KINDS of thing a run produces, which is one fewer than the files
# because the description is written twice -- once for a program and
# once in words -- and both halves end `-profile`. The charter counts
# artifacts; the handling rule counts files, because a person deciding
# what may leave their machine is looking at a folder.
ARTIFACT_TOTAL = len({name.rsplit(".", 1)[0] for name in RUN_OUTPUT_SUFFIXES})

# What each of those files is CALLED in a sentence a person reads. The
# keys are the derived endings, so an output file that ships without a
# name here fails the floor below rather than quietly escaping the
# handling rule -- which is exactly how the quality report escaped it
# for a whole phase.
#
# Each entry is a regular expression rather than a substring because two
# of the names contain another: "the twin's report" contains "twin", so
# a sentence that dropped the twin itself would otherwise still look as
# though it named it. The twin's own pattern therefore refuses the
# possessive and refuses the word "report" following it.
FILE_NAMES = (
    ("-profile.json", r"\b(profile|description)\b", "the profile itself"),
    ("-profile.txt", r"\bsummary\b", "the plain-language summary"),
    ("-twin.csv", r"\btwin\b(?!'s)(?! report)(?!-report)", "the twin"),
    (
        "-twin-report.txt",
        r"(twin's report|twin report|this report|generation report)",
        "the twin's report",
    ),
    ("-quality.txt", r"quality report", "the quality report"),
)

# The handling rule has to name every file a run can leave behind, and
# what it has to name moved twice: from the profile alone to three files
# when P2-D11 landed, and to FIVE when `synthtwin validate` shipped
# beside the fact -- found by this file's own count, not by a reviewer --
# that the profiler writes its description twice and the plain-language
# half was never named at all (plan amendment A-P3-8). The summary is the
# half a person actually reads: it prints the real labels the profile
# publishes, on the screen and into a file, so a rule that names four
# files and stops tells a reader by omission that the fifth may travel.
#
# Several phrasings are accepted, because the surfaces are written in
# several registers and forcing one sentence on all of them would make
# some of them read worse: the documents a person reads use articles,
# and the files a run writes for a reader call the profile "the
# description", which is the word those files use for it throughout and
# the word a non-programmer recognizes. Every accepted form names every
# file, and the floor below proves it of each one rather than trusting
# the eye that wrote it.
HANDLING_FORMS = (
    (
        "the profile, the plain-language summary beside it, the twin, "
        "the twin's report and the quality report"
    ),
    (
        "the profile, the plain-language summary beside it, the twin, "
        "the twin's report and this quality report"
    ),
    (
        "the description, the plain-language summary beside it, the "
        "twin, the twin's report and the quality report"
    ),
    (
        "the description, the plain-language summary beside it, this "
        "twin, this report and the quality report"
    ),
    (
        "the description, the plain-language summary beside it, the "
        "twin, the twin's report and this quality report"
    ),
    (
        "the profile, the plain-language summary beside it, this twin, "
        "this report and the quality report"
    ),
)

# The four marks of the qualified claim. Each entry is a tuple of
# accepted phrasings, so a surface may say it in its own register while
# the load-bearing words stay identical and greppable.
#
# Why each one is required, and not just the first:
#
# 1. Provenance alone reads as the old promise to most people. It is
#    necessary and it is not sufficient.
# 2. Without the forced-match acknowledgement, the surface has said
#    where values come from and left the reader to conclude the rest --
#    which is exactly the mistake being repaired.
# 3. Without the disclaimer, a reader may take the acknowledgement as a
#    bounded exception to a guarantee that does not exist.
# 4. Without the whole-run rule, naming only the profile reads as
#    permission for every other file the run left in the folder.
QUALIFIED_MARKS = (
    (
        ("samples or copies no row",),
        (
            "the provenance statement: generation reads no source table "
            "and samples or copies no row of one"
        ),
    ),
    (
        ("force a twin row to match a real one",),
        (
            "the acknowledgement that exact allocation of published "
            "counts can force a twin row to equal a real row, with "
            "nothing copied"
        ),
    ),
    (
        ("no formal privacy guarantee",),
        "the statement that synthtwin offers no formal privacy guarantee",
    ),
    (
        HANDLING_FORMS,
        (
            "the handling rule naming every file a full run leaves "
            "behind, so that the institution's rules are not read as "
            "applying to the profile alone"
        ),
    ),
)

# The surfaces that must carry the whole qualified claim. Every surface
# in SURFACES is banned from the categorical form; these additionally
# have to state the true one, because each is somewhere a person decides
# whether to trust the twin or to move a file: the charter, the front
# page, the security document, the package's own docstring, the command
# a person runs with no arguments, the summary printed on every
# profiling run, and the report written beside every twin. The last one
# matters most and is easiest to forget -- it is the only one of these
# that travels WITH the twin, so it is the only one a person who
# receives a twin from a colleague is guaranteed to have.
CLAIM_BEARING = (
    "CLAUDE.md",
    "README.md",
    "SECURITY.md",
    "src/synthtwin/__init__.py",
    "src/synthtwin/cli.py",
    "src/synthtwin/quality.py",
    "src/synthtwin/rendering.py",
    "src/synthtwin/summary.py",
    # `validation.py` joined at the validator's landing, which plan
    # P3-D7 stage 2 requires of BOTH new modules and which review item
    # P3-V1-F14 found had reached only one of them. Its reason is the
    # module's own: it decides what a person is told about a file that
    # was measured, so a claim weakened there is a claim weakened on the
    # surface a reader acts on, and checking it only under the narrower
    # structure list left the record claim unpinned in the module that
    # produces the verdict.
    "src/synthtwin/validation.py",
)

# -- the second family: what the twin carries, and what is built ------

# The claim forms retired by review item P2-C1-F7. Each is the shape of
# a sentence saying that the twin keeps something that holds BETWEEN two
# columns, or between the rows of one. None of them is true of this
# phase, and the shapes are banned rather than the exact old sentences,
# so the same claim cannot return in a paraphrase.
#
# Two shapes a reader might expect here are deliberately absent.
# "cross-column structure is preserved" is not banned, because the
# truthful sentence this repository now carries -- no cross-column
# structure is preserved at all -- contains it, and a ban that the truth
# trips is a ban that gets an exception list. And the artifact NAMES (a
# relationships file, the relationship summary) are not banned either:
# naming a thing that does not exist yet, in a section that says it does
# not exist, is how a roadmap is written.
RETIRED_RELATIONSHIP_CLAIMS = (
    "same relationships",
    "the twin preserves them",
    "how that structure was preserved",
    "relationships are preserved",
    "relationships between columns are preserved",
    "preserves the relationships",
    "same missing-data patterns",
)

# The claim forms that describe a BUILT capability as absent, or a
# closed phase as current. Every one of these was on a public surface
# while the capability it denies was installed and working.
RETIRED_CAPABILITY_CLAIMS = (
    "status: early (phase 0",
    "status: early (phase 1",
    "generating the twin itself",
    "synthtwin will create",
    "what synthtwin will do [planned]",
    "[planned]** generation",
    "synthetic twin [planned]",
    "are separate [planned]",
    "determinism [planned]",
    # Any parenthesized "this one is the current phase" marker. The
    # phase state is stated ONCE, in the sentence the positive check
    # below reads, so that two places can never disagree about it --
    # which is exactly how the charter came to call Phase 0 current
    # while Phase 2 was being built.
    "(current phase",
)

# The claim forms that undercount what synthtwin depends on. numpy
# returned as a declared direct dependency in this phase, with its own
# enumerated scanner surface; a reader auditing the supply chain from
# any of these sentences would look for one library and find two.
RETIRED_DEPENDENCY_CLAIMS = (
    "one runtime dependency",
    "one direct runtime dependency",
    "only direct runtime dependency",
    "single runtime dependency",
    "numpy is not a dependency",
    "one function of one third-party library",
    "exactly one function of one third-party",
)

# The four marks of the truthful statement of this phase. As with
# `QUALIFIED_MARKS`, each entry is a tuple of accepted phrasings so a
# surface may speak in its own register while the load-bearing words
# stay identical and greppable. The registers are: the normative one
# (charter, security document, package and module docstrings), which
# says "rows are treated as independent"; and the plain one (the front
# page, the status screen, the two files a run writes for a person),
# which says a row "is built on its own". A person reading the report
# beside their twin is not reading a specification.
#
# Why each mark and not only the first:
#
# 1. "No cross-column structure" is the fact itself, and it is stated
#    absolutely -- no correlation, no formula, no shared pattern of
#    empty cells, no ordering between two event columns -- because a
#    hedged version of it reads as "mostly".
# 2. Without the row mark, a reader takes the column statement as the
#    whole of the limit, and the twin of a repeated-measures table
#    misdescribes the subject-level truth while every column of it is
#    right on its own.
# 3. The grain mark says WHY the row one holds: the description never
#    says what one row of the real table is, so this is not something
#    the generator neglected to carry.
# 4. Without the later-phase mark, the first three read as a permanent
#    property of the product rather than as the bound of the built
#    phase, and a reader who needs cross-column structure has no idea
#    whether waiting is an option.
STRUCTURE_MARKS = (
    (
        ("no cross-column structure",),
        (
            "the statement that the twin carries no cross-column "
            "structure at all"
        ),
    ),
    (
        (
            "rows are treated as independent",
            "every row was built on its own",
            "every row is built on its own",
        ),
        "the statement that rows are treated as independent",
    ),
    (
        (
            "never says what one row",
            "never said what one row",
            "the grain is undescribed",
        ),
        (
            "the statement that the grain is undescribed -- that the "
            "description never says what one row of the real table is"
        ),
    ),
    (
        (
            "cross-column structure arrives in a later phase",
            "cross-column structure arrives in a later version",
        ),
        (
            "the statement that cross-column structure arrives in a "
            "later phase, so that the three limits above read as this "
            "phase's bound rather than as the product's nature"
        ),
    ),
)

# The surfaces that must carry the whole structure statement. These are
# `CLAIM_BEARING` plus one module, for the reason the module docstring
# gives: `generation.py` is the code that makes columns independently,
# and the charter requires a module's docstring to state the guarantees
# it upholds.
#
# `validation.py` is not named again here because it is in
# `CLAIM_BEARING` now (plan P3-D7 stage 2, closed by review item
# P3-V1-F14) and this list is built from that one. Its reason for
# carrying the structure statement is the sharper of the two: a
# validator's silence is read as coverage, somebody holding a quality
# report that missed nothing will believe the file was checked for
# whatever they care about, and this version checks not one
# cross-column fact -- because the description publishes none. A module
# that measures obligations and does not say which obligations do not
# exist has left out the largest thing about itself.
STRUCTURE_BEARING = CLAIM_BEARING + ("src/synthtwin/generation.py",)

# Where a person finds out which commands exist. Both command words are
# required on each, because naming one and not the other is how the
# front page came to describe an installed command as a future phase.
COMMAND_BEARING = (
    "CLAUDE.md",
    "README.md",
    "src/synthtwin/__init__.py",
    "src/synthtwin/cli.py",
)
# Every command word the shipped parser takes is required on each, and
# the list is DERIVED (`_shipped_command_words`) rather than written
# here: `synthtwin validate` joined them when the validator shipped
# (plan P3-D7, stage 2), and a hand-written list is a list that joins
# late. A surface that teaches two thirds of the workflow leaves a
# zero-code reader with no way to learn that the third command exists,
# which is exactly what the front page's old "[planned]" tag amounted to
# for `generate`.
#
# Naming a command is necessary and it is not sufficient: a walkthrough
# that runs two of them and stops has taught the reader to skip the
# third. `test_a_taught_sequence_does_not_stop_short` is that half.

# Where the phase state is stated, and the exact sentence each states
# it in. One sentence per surface, so the ban on parenthesized currency
# markers above leaves exactly one place per file that can be stale.
PHASE_STATEMENTS = (
    ("CLAUDE.md", "the current phase is phase 4"),
    ("README.md", "status: early (phase 4"),
)

# Where the dependency count is stated, and what it must name. The
# accepted forms differ because the front page counts DIRECT
# dependencies in the sentence a contributor reads and the security
# document counts runtime dependencies in the sentence an auditor
# reads; both are the same two libraries, and both must name them.
DEPENDENCY_BEARING = (
    "README.md",
    "SECURITY.md",
    "pyproject.toml",
)
DEPENDENCY_COUNT_FORMS = (
    "two runtime dependencies",
    "two direct runtime dependencies",
)
DEPENDENCY_NAMES = ("pandas", "numpy")

# The front page tags every capability built or planned, and promises
# in its own opening paragraph that it does. These are the tags that
# have to be there for the promise to be kept: the three commands that
# exist, tagged built; the capabilities that do not, tagged planned; and
# the two section headings that separate the one group from the other.
# Pinned as exact wording rather than counted, because a page that
# tagged everything "[built]" would satisfy any count.
#
# VALIDATION MOVED FROM PLANNED TO BUILT when `synthtwin validate`
# shipped (plan P3-D7, stage 2), and the tag moved in the same commit as
# the command. Relationships between columns did NOT move and must not:
# the description still publishes eight empty slots, the twin still
# carries no cross-column structure, and the quality report checks no
# cross-column fact because there is none to check.
FRONT_PAGE_TAGS = (
    ("## what synthtwin does today [built]", "the built-capability heading"),
    (
        "## what synthtwin does not do yet [planned]",
        (
            "the planned-capability heading, which is what makes the "
            "built one mean anything"
        ),
    ),
    ("**[built]** `synthtwin profile`", "the profiler, tagged built"),
    ("**[built]** `synthtwin generate`", "the generator, tagged built"),
    ("**[built]** `synthtwin validate`", "the validator, tagged built"),
    (
        "**[planned]** relationships between columns",
        "cross-column structure, tagged planned",
    ),
    (
        "**[planned]** pypi publication",
        (
            "the release, tagged planned, which is what keeps the "
            "planned group from being emptied now that validation has "
            "left it"
        ),
    ),
)


def _text(relative: str) -> str:
    """The whole of one surface, lowercased, with runs of space collapsed.

    WHY THE COLLAPSE. Every surface here is hard-wrapped at some column,
    and where a line happens to break is not a claim anybody made. A
    naive substring search would report that the charter fails to say
    the twin's values come from the profile purely because the sentence
    wrapped between "copies" and "no row". Collapsing every run of
    whitespace to one space compares what the sentence SAYS. It also
    strengthens the ban in the other direction: a categorical claim
    cannot hide by being wrapped either.

    WHAT ELSE IS JOINED, AND WHY ONLY THAT. Two of these surfaces are
    reports, and a report is written as a LIST OF LINES: a sentence a
    person reads across two lines is two string literals in the source,
    one per line. So a literal that ends a source line is joined to the
    literal that begins the next -- exactly the join the report itself
    performs when it prints them -- and the claim is then checked as it
    is READ rather than as it happens to be laid out. Nothing else is
    joined: two literals side by side on ONE line stay two, so a phrase
    assembled inside a tuple or a call still does not match, and a
    surface that has to state a claim still states it as running text.

    Guarantees:

    - Inputs: a path relative to the repository root, as written in
      `SURFACES`. It must exist: a surface that has been renamed or
      deleted without this list being updated is a gap in the inventory,
      so the missing file fails the test rather than being skipped.
    - Determinism: reads the file as UTF-8, lowercases it and collapses
      whitespace runs; nothing else, and nothing outside the file is
      consulted.
    - Errors raised: `AssertionError` when the file is absent;
      `UnicodeDecodeError` if a surface is not UTF-8, which is itself a
      defect in this repository.
    - Boundary: reads only inside the repository, and only files this
      module names.
    """
    path = REPO_ROOT / relative
    assert path.is_file(), (
        f"{relative} is named in the claim inventory but is not in the "
        f"repository. If it was renamed or removed, update SURFACES and "
        f"CLAIM_BEARING in this file in the same change -- an inventory "
        f"that silently skips a surface is not an inventory."
    )
    read = re.sub(r'",\s*\n\s*"', " ", path.read_text(encoding="utf-8"))
    return " ".join(read.lower().split())


def test_no_public_surface_makes_the_categorical_record_claim() -> None:
    """No surface promises that the twin holds no real record.

    This is the negative half of P2-D11's inventory. It runs over every
    surface, including the ones not obliged to state the qualified claim
    -- an error message or a module docstring may not need to explain
    the whole position, but none of them may assert the position that
    was withdrawn.
    """
    offenders: list[str] = []
    for relative in SURFACES:
        text = _text(relative)
        for retired in RETIRED_CLAIMS:
            if retired in text:
                offenders.append(f"{relative}: {retired!r}")
    assert not offenders, (
        "These surfaces make the categorical record claim that plan "
        "P2-D11 withdrew:\n  "
        + "\n  ".join(offenders)
        + "\n\nThe twin is built without reading the table and without "
        "sampling or copying a row -- that is a claim about where the "
        "values come from. It is NOT a claim that no twin row can equal "
        "a real row: reproducing published counts exactly can force the "
        "match with nothing copied. Say the provenance claim instead, "
        "and if the sentence is about the withdrawal itself, describe "
        "the old wording rather than quoting it."
    )


def test_claim_bearing_surfaces_state_the_qualified_claim() -> None:
    """The six deciding surfaces each carry all four marks.

    The positive half. Deleting the categorical sentence and writing
    nothing in its place would pass the negative test and leave a person
    with no statement at all, which is worse than the wrong statement
    because nothing signals that a question was ever settled.
    """
    missing: list[str] = []
    for relative in CLAIM_BEARING:
        text = _text(relative)
        for forms, what_it_is in QUALIFIED_MARKS:
            if not any(form in text for form in forms):
                missing.append(
                    f"{relative} is missing {what_it_is} "
                    f"(expected one of {list(forms)})"
                )
    assert not missing, (
        "These surfaces have to state the qualified claim of plan "
        "P2-D11 in full, and each is missing part of it:\n  "
        + "\n  ".join(missing)
        + "\n\nAll four parts are load-bearing: provenance alone reads "
        "as the promise that was withdrawn, and naming only the profile "
        "reads as permission for the twin and the report."
    )


def test_the_handling_rule_is_never_left_at_the_profile_alone() -> None:
    """Wherever a surface says the profile is real-derived, all five are.

    P2-D11 requires institutional handling to apply to every file the
    run leaves behind, and P3-D3 with plan amendment A-P3-8 fixed which
    files those are. The failure mode is not a wrong sentence but a
    lonely one: a surface that names the profile as real-derived
    material and stops there tells a reader, by omission, that the other
    four files are free to move. So every surface that raises the
    subject at all must also carry the whole-run phrase.
    """
    subject = "rules for real-derived material"
    silent: list[str] = []
    for relative in SURFACES:
        text = _text(relative)
        if subject not in text:
            continue
        if not any(form in text for form in HANDLING_FORMS):
            silent.append(relative)
    assert not silent, (
        "These surfaces state the institutional-handling rule but name "
        "only the profile:\n  "
        + "\n  ".join(silent)
        + "\n\nEvery file a full run leaves behind -- the profile, the "
        "plain-language summary beside it, the twin, the twin's report "
        "and the quality report -- carries facts computed from real "
        "data. Naming one of them and stopping reads as permission for "
        "the others. Add the sentence that names them all beside the "
        "rule."
    )


def test_security_document_states_the_label_spelling_disclosure() -> None:
    """SECURITY.md names version 4's label-variant fact, at its true width.

    Owner decision 11 required this entry and required it to be honest
    about the delta. The trap it exists to close: the fold the producer
    applies is a Unicode case fold after trimming, so describing the new
    fact as "capitalization" understates what leaves the machine. The
    assertions below check that the entry names the wire shape, names
    the withheld pool, names the floor that governs it, and does NOT
    stop at capitals.
    """
    text = _text("SECURITY.md")
    required = (
        ("variants", "the key each published label now carries"),
        (
            "variants_withheld",
            (
                "the anonymous count of the spellings held back, "
                "without which a reader cannot tell one label of eleven "
                "rows from eleven one-off spellings"
            ),
        ),
        (
            "casefold",
            (
                "the fold by name, because a reader who assumes "
                "capitals-to-lowercase will underestimate the delta"
            ),
        ),
        (
            "small_cell_floor",
            (
                "the floor that governs each variant exactly as it "
                "governs a whole label"
            ),
        ),
    )
    missing = [
        f"{token!r} -- {why}" for token, why in required if token not in text
    ]
    assert not missing, (
        "SECURITY.md's label-spelling entry (owner decision 11) is "
        "missing:\n  " + "\n  ".join(missing)
    )


def test_security_document_states_the_numeric_style_disclosure() -> None:
    """SECURITY.md names version 4's `numeric_styles` fact, as form only.

    Owner decision 10 published a fact about HOW numbers were written so
    that a twin can be read back as the same type. The entry has to name
    the key, enumerate the styles so a reader can see the whole of what
    is published, name the floor, and say plainly that the fact carries
    no value -- otherwise "how the numbers were written" reads as though
    the numbers themselves are in it.
    """
    text = _text("SECURITY.md")
    required = (
        ("numeric_styles", "the key by name"),
        ("plain", "the plain style"),
        ("leading_zero", "the leading-zero style"),
        ("leading_plus", "the leading-plus style"),
        ("decimal", "the decimal style"),
        ("exponent_lower", "the lower-case exponent style"),
        ("exponent_upper", "the upper-case exponent style"),
        ("small-cell floor", "the floor that governs a rare style"),
        (
            "carries no value",
            (
                "the statement that the fact is about form and holds no "
                "value, no magnitude and no spelling"
            ),
        ),
    )
    missing = [
        f"{token!r} -- {why}" for token, why in required if token not in text
    ]
    assert not missing, (
        "SECURITY.md's numeric-style entry (owner decision 10) is "
        "missing:\n  " + "\n  ".join(missing)
    )


def test_the_inventory_itself_would_notice_a_categorical_claim() -> None:
    """A vacuity floor: the ban is checked against text that must fail it.

    A ban expressed as a substring search passes trivially if the search
    is wrong -- a typo in a pattern, a lowercasing that never happens, a
    loop that never runs. This constructs the sentence the repository
    used to carry and asserts the same rule rejects it, so the negative
    test above is known to be capable of failing.
    """
    old_sentence = (
        "Create a synthetic twin of your tabular data: same shape, "
        "same statistics, no real records."
    ).lower()
    caught = [
        retired for retired in RETIRED_CLAIMS if retired in old_sentence
    ]
    assert caught, (
        "The retired-claim patterns no longer match the wording this "
        "test exists to keep out. Whatever changed, the ban is now "
        "vacuous: fix the patterns rather than this assertion."
    )
    assert RETIRED_CLAIMS, "the retired-claim list must not be empty"
    assert CLAIM_BEARING, "the claim-bearing surface list must not be empty"
    for relative in CLAIM_BEARING:
        assert relative in SURFACES, (
            f"{relative} must also be in SURFACES, so that the ban on "
            f"the categorical claim covers it too"
        )


# ---------------------------------------------------------------------
# the second family: what the twin carries, and what is built
# (review item P2-C1-F7)
# ---------------------------------------------------------------------


def test_no_public_surface_claims_relationship_fidelity() -> None:
    """No surface says the twin keeps what holds between two columns.

    The negative half of the structure claim. It runs over every
    surface, not only the deciding ones: a module docstring need not
    explain the whole limit, but none of them may assert the capability
    this phase does not have. The package docstring's "same
    relationships" is the sentence this test was written for -- it sat
    two lines from an accurate description of the boundary, and it was
    the one line a person would quote.
    """
    offenders: list[str] = []
    for relative in SURFACES:
        text = _text(relative)
        for retired in RETIRED_RELATIONSHIP_CLAIMS:
            if retired in text:
                offenders.append(f"{relative}: {retired!r}")
    assert not offenders, (
        "These surfaces claim a fidelity this phase does not have:\n  "
        + "\n  ".join(offenders)
        + "\n\nEvery column of the twin is generated on its own from the "
        "facts published about that column, and the profile's eight "
        "relationship slots are empty. Nothing that holds BETWEEN two "
        "columns -- a correlation, a formula, a shared pattern of empty "
        "cells, an ordering between two event dates -- is in the twin, "
        "and rows are treated as independent while the grain is "
        "undescribed. Say that instead, and name the later phase the "
        "structure arrives in."
    )


def test_structure_bearing_surfaces_state_the_whole_limit() -> None:
    """The deciding surfaces each carry all four marks of the limit.

    The positive half. Deleting "same relationships" satisfies the ban
    above and leaves a reader with no statement at all, which is the
    worse failure of the two: a person who is told nothing assumes the
    twin behaves like their table, because that is what a twin is for.
    """
    missing: list[str] = []
    for relative in STRUCTURE_BEARING:
        text = _text(relative)
        for forms, what_it_is in STRUCTURE_MARKS:
            if not any(form in text for form in forms):
                missing.append(
                    f"{relative} is missing {what_it_is} "
                    f"(expected one of {list(forms)})"
                )
    assert not missing, (
        "These surfaces have to state what the twin carries and what it "
        "does not, in full, and each is missing part of it:\n  "
        + "\n  ".join(missing)
        + "\n\nAll four parts are load-bearing: the column statement "
        "alone leaves a repeated-measures reader believing the twin "
        "describes their subjects, and all three limits without the "
        "later-phase mark read as the product's nature rather than as "
        "this phase's bound."
    )


def test_no_public_surface_describes_a_built_capability_as_absent() -> None:
    """Nothing shipped is described as planned, and no closed phase is
    called current.

    The zero-code failure this closes is concrete: a person installs
    synthtwin, reads the front page, and is told that the command they
    already have does not exist yet. They stop there. Nothing crashes
    and no test elsewhere fails.
    """
    offenders: list[str] = []
    for relative in SURFACES:
        text = _text(relative)
        for retired in RETIRED_CAPABILITY_CLAIMS:
            if retired in text:
                offenders.append(f"{relative}: {retired!r}")
    assert not offenders, (
        "These surfaces describe something that is built as though it "
        "were not, or mark a closed phase as current:\n  "
        + "\n  ".join(offenders)
        + "\n\nBoth commands are built and installed, the generator "
        "writes the twin and its report, and the current phase is the "
        "one named in the sentence "
        "`test_the_phase_record_is_current` reads. A capability that "
        "exists is tagged built; a capability that does not is named "
        "with the phase it arrives in and never written about as "
        "though it were here."
    )


def test_the_built_commands_are_named_where_a_person_looks() -> None:
    """Both command words appear on every surface that teaches the tool.

    The positive half of the availability check. A surface may not
    teach one command and stay silent about the other: silence about
    `generate` is what the front page's "[planned]" tag amounted to,
    and a zero-code user has no other way to learn that the second half
    of the workflow exists.
    """
    missing: list[str] = []
    for relative in COMMAND_BEARING:
        text = _text(relative)
        for word in COMMAND_WORDS:
            if word not in text:
                missing.append(f"{relative} never names `{word}`")
    assert not missing, (
        "These surfaces teach the tool and leave out a command that "
        "exists:\n  "
        + "\n  ".join(missing)
        + "\n\nBoth halves of the workflow are installed. Name both, "
        "and say what each writes."
    )


def test_the_front_page_separates_what_is_built_from_what_is_planned() -> (
    None
):
    """The [built]/[planned] tagging the front page promises is real.

    The page opens by telling a reader that every capability on it is
    tagged one way or the other, so that there is no ambiguity about
    which is which. That promise is worth exactly as much as the tags:
    while generation was tagged planned and already installed, the
    tagging was worse than none, because it invited the reader to trust
    it. Both halves are pinned here -- the two commands that exist and
    the two outputs that do not -- so neither group can be quietly
    emptied.
    """
    text = _text("README.md")
    missing = [
        f"{tag!r} -- {what_it_is}"
        for tag, what_it_is in FRONT_PAGE_TAGS
        if tag not in text
    ]
    assert not missing, (
        "README.md promises that every capability on it is tagged "
        "[built] or [planned], and these tags are missing or "
        "reworded:\n  "
        + "\n  ".join(missing)
        + "\n\nIf a capability moved from planned to built, move its "
        "tag and update the expected wording in FRONT_PAGE_TAGS in the "
        "same commit."
    )


def test_the_phase_record_is_current() -> None:
    """Each surface that states the phase states the phase that is running.

    One sentence per surface, checked by exact wording, so that the
    parenthesized currency markers banned above cannot come back and
    disagree with it. When the phase advances, this tuple is the list
    of sentences to change, and the test names them.
    """
    missing: list[str] = []
    for relative, sentence in PHASE_STATEMENTS:
        if sentence not in _text(relative):
            missing.append(f"{relative} no longer says {sentence!r}")
    assert not missing, (
        "The phase record is stale or was reworded:\n  "
        + "\n  ".join(missing)
        + "\n\nIf the phase itself advanced, change the sentence in the "
        "file AND the expected wording in PHASE_STATEMENTS in the same "
        "commit -- that pairing is the whole point of pinning the "
        "sentence rather than the number."
    )


def test_no_public_surface_undercounts_the_dependencies() -> None:
    """No surface says one library where two are declared.

    An auditor reads one of these sentences, opens `pyproject.toml`,
    and finds a library the document did not mention. The document is
    then worth less than nothing: it has taught the auditor that the
    inventory is not maintained.
    """
    offenders: list[str] = []
    for relative in SURFACES:
        text = _text(relative)
        for retired in RETIRED_DEPENDENCY_CLAIMS:
            if retired in text:
                offenders.append(f"{relative}: {retired!r}")
    assert not offenders, (
        "These surfaces undercount what synthtwin depends on:\n  "
        + "\n  ".join(offenders)
        + "\n\nThere are two declared direct runtime dependencies: "
        "pandas, reduced by the scanner to `read_csv` and fenced by the "
        "run-time path check, and numpy, reduced to "
        "`numpy.random.default_rng` and the one drawing call on the "
        "stream it returns. Count both, and say what each is reduced to."
    )


def test_the_dependency_bearing_surfaces_name_both_libraries() -> None:
    """Where the count is stated, it is stated completely.

    The positive half. Deleting the word "one" would satisfy the ban
    above and leave a supply-chain section that counts nothing at all.
    """
    missing: list[str] = []
    for relative in DEPENDENCY_BEARING:
        text = _text(relative)
        if not any(form in text for form in DEPENDENCY_COUNT_FORMS):
            missing.append(
                f"{relative} states no dependency count (expected one "
                f"of {list(DEPENDENCY_COUNT_FORMS)})"
            )
        for name in DEPENDENCY_NAMES:
            if name not in text:
                missing.append(f"{relative} never names {name}")
    assert not missing, (
        "These surfaces state the dependency inventory and leave part "
        "of it out:\n  "
        + "\n  ".join(missing)
        + "\n\nThe count and both names belong together: a count with "
        "no names cannot be checked against `pyproject.toml`, and names "
        "with no count do not say whether the list is complete."
    )


def test_the_second_family_of_bans_would_notice_the_old_wording() -> None:
    """A vacuity floor for every ban added by review item P2-C1-F7.

    Same reasoning as the floor above, applied to three more lists: a
    substring ban passes trivially when the substring is wrong. Each
    sentence below is one this repository actually carried, taken from
    the surfaces the review item names, and each must still be caught.
    """
    retired_text = {
        "the package docstring's relationship promise": (
            "Same columns, same types, same distributions, same "
            "relationships, same missing-data patterns."
        ),
        "the charter's relationship output": (
            "The relationship summary -- which columns move together "
            "and how that structure was preserved."
        ),
        "the front page's status line": (
            "Status: early (Phase 1). What exists today is the "
            "profiler."
        ),
        "the front page's planned generation": (
            "- **[planned]** Generation, validation, and the quality "
            "report."
        ),
        "the front page's dependency count": (
            "synthtwin has exactly one direct runtime dependency, "
            "pandas, and numpy is not a dependency of synthtwin."
        ),
        "the security document's allowlist count": (
            "an exact, enumerated list of standard-library APIs, plus "
            "exactly one function of one third-party library."
        ),
        "the charter's phase marker": (
            "Phase 0 -- public skeleton and security baseline. "
            "(Current phase; see the plan.)"
        ),
    }
    bans = (
        RETIRED_RELATIONSHIP_CLAIMS
        + RETIRED_CAPABILITY_CLAIMS
        + RETIRED_DEPENDENCY_CLAIMS
    )
    uncaught = [
        f"{what}: {sentence!r}"
        for what, sentence in retired_text.items()
        if not any(ban in sentence.lower() for ban in bans)
    ]
    assert not uncaught, (
        "These sentences were on public surfaces of this repository and "
        "are no longer caught by any ban:\n  "
        + "\n  ".join(uncaught)
        + "\n\nThe bans are now vacuous for that wording. Fix the "
        "patterns rather than this assertion."
    )
    assert RETIRED_RELATIONSHIP_CLAIMS and RETIRED_CAPABILITY_CLAIMS
    assert RETIRED_DEPENDENCY_CLAIMS and STRUCTURE_MARKS
    for relative in STRUCTURE_BEARING + COMMAND_BEARING + DEPENDENCY_BEARING:
        assert relative in SURFACES, (
            f"{relative} must also be in SURFACES, so that every ban in "
            f"this file covers it too"
        )
    for relative, _sentence in PHASE_STATEMENTS:
        assert relative in SURFACES, (
            f"{relative} must also be in SURFACES, so that every ban in "
            f"this file covers it too"
        )


# ---------------------------------------------------------------------
# the third family: what the product has, counted from the product
# (review item P3-V3-F8)
# ---------------------------------------------------------------------

# The words a total is written in. "one" is deliberately absent: "one
# command calls its own files" is English for "a single command" and is
# not a claim about how many there are, so counting it would put the ban
# in a fight with ordinary prose and earn itself an exception list.
_COUNT_WORDS = {
    "both": 2,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
}
_COUNTS = "|".join(sorted(_COUNT_WORDS, key=len, reverse=True))

# Up to two words may stand between the number and its noun -- "all
# three PHASE 2 artifacts", "all four files a full run produces" -- so
# that a total cannot escape by qualifying its noun.
_GAP = r"(?:[a-z0-9'-]+ ){0,2}?"

# Another tool's commands are not this tool's commands, and a
# walkthrough that installs by hash names two of pip's. The words below
# are the only ones that may stand between a number and the noun
# "commands" without the count being read as synthtwin's own -- which is
# a statement about scope, not an exception: "both pip commands" is a
# sentence about pip.
_OTHER_TOOLS = ("pip", "git", "python", "python3", "shell", "install")

# What each countable noun is counted against, and where a count of it
# is a claim about the whole set. The totals are derived at import from
# the shipped parser and the shipped output names, so a fourth command
# or a sixth output file reddens every stale total in the repository on
# the commit that ships it.
#
# The three nouns need three different reaches, and the reason is what
# each word means when it is NOT talking about the whole product:
#
# * "commands" almost always is. `profile`, `generate` and `validate`
#   are the set, so a bare count of them is checked, with "other"
#   subtracting the speaker's own.
# * "artifacts" is checked under a totality word ("all four artifacts")
#   or under the run ("four artifacts a full run produces"). Bare counts
#   are ordinary prose about a subset -- "the twin's two artifacts" is
#   true and says nothing about the run.
# * "files" is checked under the run, and under HANDLING. Two commands
#   each write a pair, so "both files", "the two files this run writes"
#   and their kin are true sentences on nearly every page of this
#   repository; a count of files is a claim about the whole run exactly
#   when it says so, and then it is checked hard.
#
#   AND WHEN IT SAYS SO BY SAYING WHAT IS DONE WITH THEM (review item
#   P3-V4-F7). The run was the only anchor, and the sentence that got
#   away said instead "how the FOUR FILES are handled" -- in the
#   docstring of the very helper that prints the five-file handling
#   rule, in `quality.py`, a surface this file has always guarded. The
#   handling rule is a claim about everything a run leaves behind by
#   definition: there is no subset of the files it applies to. So a
#   count of files inside a passage about handling real-derived
#   material is measured against the whole, exactly as one under the
#   run is.
_NOUN_RULES = (
    (
        r"artifacts?",
        ARTIFACT_TOTAL,
        "the kinds of thing a full run produces",
        ("totality", "run"),
    ),
    (
        r"files?",
        FILE_TOTAL,
        "the files a full run leaves behind",
        ("run", "handling"),
    ),
    (
        r"commands?",
        COMMAND_TOTAL,
        "the commands the tool offers",
        ("totality", "run", "bare"),
    ),
)

# The verbs the handling rule uses when it states its total without
# repeating the noun -- "keep all four under the rules your institution
# applies". Checked only where the sentence is about real-derived
# material, because "the previous paragraph's own words apply to all
# three" is a true sentence about three date pairs in the generation
# method and has nothing to do with this rule.
_TOTAL_VERBS = (
    "apply to all",
    "applies to all",
    "applying to all",
    "keep all",
    "keeps all",
    "covers all",
    "cover all",
    "handled under the same rules, all",
)
_HANDLING_CONTEXT = ("real-derived", "institution")
_CONTEXT_WINDOW = 250


def _about_handling(text: str, found: "re.Match[str]") -> bool:
    """Whether this count stands inside a passage about handling.

    The same window and the same marks the total-verb rule uses, so
    there is one answer in this file to "is this sentence about
    material derived from real data" rather than two that can drift.
    """
    near = text[
        max(0, found.start() - _CONTEXT_WINDOW) : found.end() + _CONTEXT_WINDOW
    ]
    return any(mark in near for mark in _HANDLING_CONTEXT)


def _totals_stated(text: str) -> "list[tuple[int, int, str, str]]":
    """Every total one surface states about a countable of the product.

    Returns one entry per statement: the number said, the number that is
    true, what was counted, and the words it was said in. A statement
    beginning "other" is measured against one FEWER, because a command
    speaking about "the other two commands" is right exactly when three
    exist -- so the phrase moves with the count instead of being
    exempted from it.

    Guarantees:

    - Inputs: one surface's text, lowercased and space-collapsed.
    - Determinism: a fixed function of that text and of the totals
      derived at import; nothing is read here.
    - Errors raised: none.
    - Boundary: pure text; opens nothing.
    """
    seen: list[tuple[int, int, str, str]] = []
    at: set[int] = set()
    for noun, total, what, reaches in _NOUN_RULES:
        patterns = {
            # "all three artifacts", "both commands"
            "totality": (
                (
                    rf"\ball (?P<count>{_COUNTS}) (?P<gap>{_GAP})"
                    rf"(?P<noun>{noun})\b"
                ),
                rf"\b(?P<count>both) (?P<gap>{_GAP})(?P<noun>{noun})\b",
            ),
            # "the other three files a full run makes"
            "run": (
                (
                    rf"\b(?P<other>other )?(?P<count>{_COUNTS}) "
                    rf"(?P<gap>{_GAP})(?P<noun>{noun}) "
                    rf"(?:a|of a|that a|the) (?:full|whole) run"
                ),
            ),
            # "the write transaction serves two commands". No gap is
            # allowed here, because without a totality word or the run
            # to anchor it the number has to sit against the noun to be
            # a count of it: "the four modules this command imports"
            # counts modules.
            "bare": (
                (
                    rf"\b(?P<other>other )?(?P<count>{_COUNTS}) (?P<gap>)"
                    rf"(?P<noun>{noun})\b(?! line| lines| word| words)"
                ),
            ),
            # "how the four files are handled", inside a passage about
            # material derived from real data (review item P3-V4-F7).
            # The handling rule has no subset: it is about everything a
            # run leaves behind, so a count of files stated inside it is
            # a count of all of them.
            #
            # The anchor is the HANDLING ITSELF, not the neighbourhood.
            # A count of files near the word "institution" is ordinary
            # prose -- "both files are as they were before this run" is
            # a true sentence about a two-file transaction -- so what is
            # read is the count standing as the subject of being
            # handled, or the handling of a counted set.
            "handling": (
                (
                    rf"\b(?P<other>other )?(?P<count>{_COUNTS}) "
                    rf"(?P<gap>{_GAP})(?P<noun>{noun}) (?:are|is) handled"
                ),
                (
                    rf"handling of (?:the |all )?(?P<count>{_COUNTS}) "
                    rf"(?P<gap>{_GAP})(?P<noun>{noun})\b"
                ),
                (
                    rf"\b(?P<count>{_COUNTS}) (?P<gap>{_GAP})(?P<noun>{noun})"
                    rf" (?:a |this )?(?:run |command )?"
                    rf"(?:carry|carries|hold|holds) facts computed"
                ),
            ),
        }
        for reach in reaches:
            for pattern in patterns[reach]:
                for found in re.finditer(pattern, text):
                    where = found.start("noun")
                    gap = (found.groupdict().get("gap") or "").split()
                    if where in at or any(word in _OTHER_TOOLS for word in gap):
                        continue
                    if reach == "handling" and not _about_handling(text, found):
                        continue
                    at.add(where)
                    said = _COUNT_WORDS[found.group("count")]
                    other = "other" in (found.groupdict().get("other") or "")
                    true = total - 1 if other else total
                    if said != true:
                        seen.append((said, true, what, found.group(0)))
    for verb in _TOTAL_VERBS:
        for found in re.finditer(rf"{re.escape(verb)} (?P<count>{_COUNTS})\b", text):
            near = text[
                max(0, found.start() - _CONTEXT_WINDOW) : found.end()
                + _CONTEXT_WINDOW
            ]
            if not any(mark in near for mark in _HANDLING_CONTEXT):
                continue
            said = _COUNT_WORDS[found.group("count")]
            if said != FILE_TOTAL:
                seen.append(
                    (
                        said,
                        FILE_TOTAL,
                        "the files a full run leaves behind",
                        found.group(0),
                    )
                )
    return seen


def test_no_surface_states_a_stale_total() -> None:
    """No surface counts the commands or the run's files wrongly.

    THE DEFECT THIS CLOSES (review item P3-V3-F8). `synthtwin validate`
    shipped; the sentences saying the tool has two commands and that a
    run leaves three artifacts stayed where they were, on six surfaces,
    and every test in this file passed. The concrete harm is not a
    stylistic one: an auditor who follows `rendering.report`'s stated
    contract reads that all three artifacts need controlled handling and
    leaves the quality report -- which carries measurements taken from
    the file that was checked -- outside the institution's rules.

    The totals are counted from the product, not written down here, so
    the same sentence cannot go stale twice.
    """
    wrong: list[str] = []
    for relative in SURFACES:
        for said, true, what, words in _totals_stated(_text(relative)):
            wrong.append(
                f"{relative}: {words!r} says {said} where {true} is the "
                f"count of {what}"
            )
    assert not wrong, (
        "These surfaces state a total the product does not have:\n  "
        + "\n  ".join(wrong)
        + f"\n\nThe tool offers {COMMAND_TOTAL} commands "
        + f"({', '.join(COMMAND_WORDS)}), and a full run leaves "
        + f"{FILE_TOTAL} files behind, of {ARTIFACT_TOTAL} kinds "
        + f"({', '.join(RUN_OUTPUT_SUFFIXES)}). Each total is counted "
        "from the shipped parser and the shipped output names, so if a "
        "number here surprises you the surface is stale, not the count."
    )


def test_the_output_reading_sees_a_name_however_it_is_spelled() -> None:
    """The four evasions review item P3-V4-F7 named, put through it.

    The reading this replaces matched one spelling: an unannotated,
    double-quoted `NAME_SUFFIX` at column zero. Each source below
    declares a sixth output file some other way, and every one of them
    used to leave the guarded total at five -- so every "five files"
    sentence in the repository stayed green beside a run that wrote
    six. The reading is put through them here rather than trusted,
    because a reading nobody questions is how the first one got its
    shape.
    """
    spellings = {
        "a typed constant": '_AUDIT_SUFFIX: str = "-audit.txt"\n',
        "single quotes": "_AUDIT_SUFFIX = '-audit.txt'\n",
        "a computed name": '_AUDIT_SUFFIX = "-audit" + ".txt"\n',
        "a name ending in nothing in particular": '_AUDIT = "-audit.txt"\n',
        "a name inside a class": 'class Names:\n    audit = "-audit.txt"\n',
        "an f-string with nothing to fill in": '_AUDIT = f"-audit.txt"\n',
        "a lower-case module variable": 'audit_suffix = "-audit.txt"\n',
    }
    missed = [
        f"{how}: {source!r}"
        for how, source in spellings.items()
        if "-audit.txt" not in _output_endings_in(source)
    ]
    assert not missed, (
        "these ways of declaring a sixth output file are invisible to "
        "the reading that counts what a run leaves behind, so a "
        "maintainer using one of them would leave every handling rule "
        "in this repository naming five files while six were "
        "written:\n  " + "\n  ".join(sorted(missed))
    )
    # ...and the reading is not simply saying yes. A module that
    # declares no output name must yield none, or the count above would
    # be a number with no meaning.
    assert not _output_endings_in(
        'HOW_LONG = 12\nWORDS = "the table you asked about"\n'
    )


def test_a_full_run_leaves_exactly_the_files_this_file_counts(
    tmp_path: pathlib.Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """The count, taken off the DISK rather than off a spelling.

    WHAT THIS CLOSES (review item P3-V4-F7). `_shipped_output_suffixes`
    reads the package's source, and a reading of source can always be
    got around by how a constant is spelled: the version this replaces
    recognized only an unannotated, double-quoted `NAME_SUFFIX` at the
    start of a line, so a sixth output declared any other way left the
    guarded total at five and every "five files" sentence in the
    repository green beside a run that wrote six. Widening the reading
    helps and does not settle it -- a name built by a call is not text
    any reader of source can see.

    So the count is settled here, by running `profile`, then
    `generate`, then `validate` on a table built in this folder and
    counting what is left on the disk. A sixth output cannot hide from
    this by any spelling, because it has to BE there. If the two
    numbers disagree, one of them is what the product does and the
    other is what every stale-total sentence in the repository is
    checked against, and the message says which is which.
    """
    import fixtures

    rows = [
        [fixtures.REGIONS[index % 4], f"{index % 7}"] for index in range(48)
    ]
    table = fixtures.write(
        tmp_path, "table.csv", fixtures.rows_to_csv(["region", "visits"], rows)
    )
    assert cli.main(["profile", f"{table}"]) == 0
    description = tmp_path / "table-profile.json"
    assert cli.main(["generate", f"{description}"]) == 0
    assert cli.main(["validate", f"{description}"]) == 0
    capsys.readouterr()
    left = sorted(
        path.name for path in tmp_path.iterdir() if path.name != table.name
    )
    assert len(left) == FILE_TOTAL, (
        f"a full run left {len(left)} files on disk ({left}) and this "
        f"file counts {FILE_TOTAL} from the package's own source "
        f"({list(RUN_OUTPUT_SUFFIXES)}). Every handling rule and every "
        f"stale-total check in this repository is measured against the "
        f"second number, so an output the source reading cannot see is "
        f"an output no rule names."
    )
    unnamed = [
        name for name in left if not name.endswith(RUN_OUTPUT_SUFFIXES)
    ]
    assert not unnamed, (
        f"a full run left {unnamed} on disk, and no ending this file "
        f"counts fits them. Give the output name a module constant, so "
        f"that what a run writes stays countable."
    )
    for ending in RUN_OUTPUT_SUFFIXES:
        assert sum(1 for name in left if name.endswith(ending)) == 1, (
            f"the ending {ending} is not the ending of exactly one file "
            f"a full run leaves behind ({left}), so counting endings is "
            f"no longer counting files"
        )


def test_every_handling_form_names_every_file_a_run_writes() -> None:
    """A floor: no accepted handling form can leave a file out.

    The positive check above is worth exactly as much as the forms it
    accepts, and the forms are the part a person edits. This holds each
    one to the derived list: every file the product writes has a name in
    `FILE_NAMES`, every accepted form matches every one of those names,
    and the form's own list is as long as the count -- so deleting one
    file from a form fails here rather than quietly narrowing the rule
    on every surface at once.
    """
    endings = {ending for ending, _pattern, _what in FILE_NAMES}
    assert endings == set(RUN_OUTPUT_SUFFIXES), (
        "The product writes files this file has no name for, or names "
        "files it no longer writes:\n"
        f"  written: {sorted(RUN_OUTPUT_SUFFIXES)}\n"
        f"  named:   {sorted(endings)}\n"
        "A new output file joins FILE_NAMES and joins every handling "
        "form in the same commit -- a file nobody named is a file the "
        "institution's rules were never stated about."
    )
    missing: list[str] = []
    for form in HANDLING_FORMS:
        for _ending, pattern, what in FILE_NAMES:
            if re.search(pattern, form) is None:
                missing.append(f"{form!r} never names {what}")
        parts = form.count(",") + form.count(" and ")
        if parts != FILE_TOTAL - 1:
            missing.append(
                f"{form!r} lists {parts + 1} names where a full run "
                f"leaves {FILE_TOTAL} files"
            )
    assert not missing, (
        "These accepted handling forms do not name every file a run "
        "leaves behind:\n  " + "\n  ".join(missing)
    )


# The wording that puts a thing in a phase rather than in the product.
# Only unambiguous placements are here. "will be" is deliberately absent:
# "the description the twin will be built from" is a true sentence about
# a step the reader has not taken yet, and a ban the truth trips is a ban
# that gets an exception list. What is here is the tool speaking about
# its own work as somebody else's later work.
# Saying a built thing IS a phase, or arrives in one, is enough on its
# own: it is a statement about when the thing exists.
_PHASE_PLACEMENTS = (
    r"\bare phase\b",
    r"\bis phase\b",
    r"arrives in phase",
    r"comes in phase",
    r"arrives with phase",
    r"does not exist yet",
)
# A future verb is a defect only when it is attached to a PHASE. "The
# profile will say so" is a true sentence about a file that has not been
# written yet in the reader's own run; "the quality report of Phase 3
# will say so" is the tool describing its own shipped work as somebody
# else's later work.
_FUTURE_VERBS = (
    r"will say",
    r"will name",
    r"will report",
    r"will tell",
    r"will arrive",
    r"will exist",
    r"will check",
    r"will measure",
)
_PHASE_MENTIONS = (r"phase \d", r"a later phase", r"a later version")
_FUTURE_WINDOW = 70
# A marker in the NEXT sentence is not a claim about this one, so the
# window stops where the sentence does.
_SENTENCE_ENDS = (".", ";", " -- ")


def _built_things() -> "tuple[str, ...]":
    """What is built, in the words a surface would name it by.

    Derived: the command words come from the shipped parser and the
    file names from the shipped output endings, so a capability that
    ships is one no surface may go on describing as later work.
    """
    names = ["fidelity measurement"]
    for _ending, _pattern, what in FILE_NAMES:
        names.append(what.replace("plain-language ", "").replace(" itself", ""))
    return tuple(COMMAND_WORDS) + tuple(names)


def _rest_of_sentence(text: str, start: int) -> str:
    """What follows a name, up to the end of the sentence it is in."""
    tail = text[start : start + _FUTURE_WINDOW]
    for end in _SENTENCE_ENDS:
        if end in tail:
            tail = tail[: tail.index(end)]
    return tail


def _puts_it_in_a_phase(tail: str) -> "str | None":
    """The wording that placed this thing in a phase, or nothing."""
    for mark in _PHASE_PLACEMENTS:
        if re.search(mark, tail) is not None:
            return mark
    if not any(re.search(mark, tail) is not None for mark in _PHASE_MENTIONS):
        return None
    for mark in _FUTURE_VERBS:
        if re.search(mark, tail) is not None:
            return mark
    return None


def test_no_surface_puts_a_built_capability_in_a_future_phase() -> None:
    """Nothing that ships is described as a phase's later work.

    The sibling of the built-capability ban above, and the shape it
    could not see: not "[planned]" beside a command, but a sentence
    written while the thing was genuinely future and left standing after
    it shipped. Two survived the validator's landing -- the front page
    telling a reader that the quality report of Phase 3 WILL say so
    plainly, and the generation method telling an independent
    implementer that fidelity measurement and the quality report ARE
    Phase 3. A reader who believes either one does not run the command
    that would have answered their question.
    """
    offenders: list[str] = []
    for relative in SURFACES:
        text = _text(relative)
        for thing in _built_things():
            for found in re.finditer(re.escape(thing), text):
                mark = _puts_it_in_a_phase(_rest_of_sentence(text, found.end()))
                if mark is not None:
                    tail = _rest_of_sentence(text, found.end())
                    offenders.append(
                        f"{relative}: {thing!r} is put in a phase by "
                        f"{mark!r} -- {thing + tail!r}"
                    )
    assert not offenders, (
        "These surfaces put something that is built into the future:\n  "
        + "\n  ".join(offenders)
        + "\n\nEvery command the parser takes and every file a run "
        "writes exists today. Say what it does, in the present tense; "
        "if the sentence is about what a LATER phase adds, name that "
        "phase and the capability it adds rather than the built one."
    )


# What a reader can copy and run in order. A step is a line that starts
# with the tool's own name or with one of the few shell words a
# walkthrough needs to set up a machine; anything else -- prose, a blank
# line, a description indented under an example -- ends the sequence.
_SETUP_STEPS = ("git ", "cd ", "pip ", "python ", "python3 ")


def _taught_sequences(relative: str) -> "list[list[str]]":
    """Every runnable sequence one surface puts in front of a reader."""
    sequences: list[list[str]] = []
    running: list[str] = []
    path = REPO_ROOT / relative
    for line in path.read_text(encoding="utf-8").splitlines():
        step = line.strip().lstrip("$").strip()
        if step.startswith("synthtwin ") or step.startswith(_SETUP_STEPS):
            running = running + [step]
            continue
        if running:
            sequences = sequences + [running]
            running = []
    if running:
        sequences = sequences + [running]
    return sequences


def test_a_taught_sequence_does_not_stop_short() -> None:
    """A walkthrough that runs two commands runs all of them.

    Naming the third command somewhere on the page is not the same as
    teaching it, and the difference is what a person actually does. The
    front page's install section walked a reader from a clone to a
    profile to a twin and stopped, so a README-only reader -- exactly
    the zero-code reader this project is for -- could follow it to the
    end and never learn that the file they now hold can be checked.

    A sequence that invokes one command is a worked example of that
    command and is left alone. A sequence that invokes two has begun to
    teach the workflow, and the workflow does not end at the twin.
    """
    short: list[str] = []
    for relative in SURFACES:
        for sequence in _taught_sequences(relative):
            named = [
                word
                for word in COMMAND_WORDS
                if any(step.startswith(word) for step in sequence)
            ]
            if len(named) < 2 or len(named) == COMMAND_TOTAL:
                continue
            absent = [word for word in COMMAND_WORDS if word not in named]
            short.append(
                f"{relative}: a sequence runs {', '.join(named)} and "
                f"never {', '.join(absent)}:\n      "
                + "\n      ".join(sequence)
            )
    assert not short, (
        "These runnable sequences teach part of the workflow and stop:\n  "
        + "\n  ".join(short)
        + "\n\nA reader follows the last line and believes they are "
        "finished. Add the missing step, or split the sequence so that "
        "each block is a worked example of one command."
    )


def test_the_third_family_would_notice_the_wording_it_replaced() -> None:
    """A vacuity floor: every rule above is checked against live text.

    Same reasoning as the two floors before it. Each sentence below was
    on a public surface of this repository at the commit review item
    P3-V3-F8 was written against, and each must still be caught -- the
    counts by the count rule, the future placements by the future rule,
    and the truncated walkthrough by the sequence rule.
    """
    stale = {
        "the twin's report, on all three artifacts": (
            "that all three artifacts carry facts computed from real "
            "data and are kept under the institution's rules"
        ),
        "the twin's report's module docstring": (
            "that all three files of a full run carry facts computed "
            "from real data"
        ),
        "the write transaction's own account of itself": (
            "the write transaction serves two commands. `profile` reads "
            "a table and writes a profile beside a summary"
        ),
        "the transaction module's docstring": (
            "the machinery is one piece of code for both commands, but "
            "the files are not the same files"
        ),
        "the profiler summary's count of what a run makes": (
            "the same is true of the other three files a full run makes."
        ),
        "the handling rule before the summary was named": (
            "all four files a full run produces -- the profile, the "
            "twin, the twin's report and the quality report -- carry "
            "facts computed from your real data"
        ),
    }
    uncaught = [
        f"{what}: {sentence!r}"
        for what, sentence in stale.items()
        if not _totals_stated(sentence)
    ]
    assert not uncaught, (
        "These stale totals were live on public surfaces and are no "
        "longer caught:\n  " + "\n  ".join(uncaught)
    )
    future = {
        "the front page's small-table row": (
            "the quality report of phase 3 will say so plainly"
        ),
        "the generation method's scope paragraph": (
            "fidelity measurement and the quality report are phase 3."
        ),
    }
    still_future = []
    for what, sentence in future.items():
        caught = False
        for thing in _built_things():
            for found in re.finditer(re.escape(thing), sentence):
                tail = _rest_of_sentence(sentence, found.end())
                caught = caught or _puts_it_in_a_phase(tail) is not None
        if not caught:
            still_future.append(f"{what}: {sentence!r}")
    assert not still_future, (
        "These sentences put a built capability in a future phase and "
        "are no longer caught:\n  " + "\n  ".join(still_future)
    )
    assert _COUNT_WORDS and _PHASE_PLACEMENTS and _FUTURE_VERBS and FILE_NAMES
    assert COMMAND_TOTAL >= 3 and FILE_TOTAL >= 5 and ARTIFACT_TOTAL >= 4


# ---------------------------------------------------------------------
# THE FOURTH FAMILY: A GUARANTEE THIS PRODUCT STOPPED MAKING
# (owner ruling 2026-08-14; plan amendment A-P3-13; validation method
# V5-A1)
# ---------------------------------------------------------------------
#
# WHAT WAS GIVEN UP. The quality report's disclosure rule was written to
# hold against two different readers. One is handed a report and may
# hold no file at all; every rule still binds exactly as written for
# that reader. The other HOLDS the checked file, writes descriptions of
# their own, runs `synthtwin validate` again with each, and reads a
# number the report withholds off which verdicts moved. The owner ruled
# the second reader out of scope -- running the check on a file requires
# holding the file -- and required the product to say so instead of
# quietly going on implying otherwise.
#
# WHY THAT NEEDS A TEST AND NOT A MEMO. The withdrawn half is the half
# that comes naturally to anyone writing about a confidentiality rule:
# "so the number cannot be recovered" is the sentence that makes the
# rule sound worth having, and it is one clause away from every true
# sentence about withholding in this repository. Three review rounds
# found routes open to that reader while six surfaces went on promising
# it was closed, and one of the six was a governing document. A sentence
# is not repaired by a maintainer remembering; it is repaired by the
# suite going red.
#
# HOW IT IS CAUGHT, AND WHY NOT BY A LIST OF SENTENCES. The three
# families above ban wordings. That works where the claim has a settled
# phrasing, and this one does not: it was written five different ways in
# five different places, and a ban anchored on any one shape catches
# that shape only. So this family is COMPOSITIONAL. A sentence trips it
# when it does two things at once --
#
#   * it NAMES the reader the ruling put out of scope, in any of the
#     ways English names somebody choosing what the description says and
#     running the check more than once; and
#   * it makes a PROMISE about them: that they cannot, are stopped, are
#     defended against, will never, get no closer than.
#
# -- and neither half alone is a defect. Naming the reader is required
# of five surfaces (the positive check at the foot of this section);
# promising is ordinary English about the many things this product does
# refuse. It is the pair, in one sentence, that states the guarantee
# that was withdrawn.
#
# AND A SURFACE MAY STILL DISCUSS THE WITHDRAWAL, which is why the cure
# is a WINDOW rather than an exception list. A passage that names the
# reader and says the defence is gone -- "no longer", "out of scope",
# "used to", "is not a defence", "does not try to stop them" -- is the
# honest paragraph this ruling requires, not the claim it bans, and the
# marker may stand anywhere within `_CURE_WINDOW` characters of the
# naming rather than inside the same sentence, because a comment block
# that spends three sentences on the history before withdrawing it in
# the fourth is exactly how this repository writes. What a surface may
# NOT do is state the promise with no withdrawal anywhere near it. That
# is the one shape round 4 found in a governing document, and it is the
# shape this catches.
#
# THE RED CHECKS, AND THERE ARE TWO, because this family can fail in two
# directions and only one of them is a missing sentence.
#
# * `REINSTATE=A-P3-13-promised` puts the withdrawn guarantee back on
#   every surface at once, by adding one sentence of it to what `_text`
#   returns. `test_no_public_surface_promises_a_defence_against_re_
#   running` goes red, which is the ban being capable of failing at all.
# * `REINSTATE=A-P3-13-one-shape` narrows the ban to the single wording
#   the plan and the specification happened to use -- "candidate
#   descriptions" and nothing else, which is a ban a reviewer would call
#   thorough. Seven of the eleven wordings the vacuity floor records
#   then walk straight past it, and
#   `test_the_fourth_family_would_notice_the_promise_it_replaced` goes
#   red naming each. That is the round-4 lesson made executable: a guard
#   anchored on one sentence shape catches one sentence shape.
#
# Both were measured on the commit that added this section, and the
# withdrawn promise was additionally put back BY HAND in eight wordings
# across eight tracked files -- the front page, the security document,
# the charter, the validation method, and `quality.py`, `validation.py`,
# `rendering.py` and `summary.py` -- with all eight turning the suite
# red and none of them relying on a phrase written down here.


@pytest.fixture(autouse=True)
def _reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """The two red checks above, driven from the environment."""
    asked = os.environ.get("REINSTATE")
    if asked == "A-P3-13-promised":
        kept = _text

        def _with_the_promise(relative: str) -> str:
            return (
                kept(relative)
                + " no sequence of candidate descriptions can narrow a "
                "number this report withholds."
            )

        monkeypatch.setitem(globals(), "_text", _with_the_promise)
    if asked == "A-P3-13-one-shape":
        monkeypatch.setitem(
            globals(), "_CHOSEN_MARKS", (r"\bcandidate descriptions\b",)
        )
        monkeypatch.setitem(globals(), "_REPEAT_MARKS", ())
        monkeypatch.setitem(globals(), "_SEARCHER_ALONE", ())
        monkeypatch.setitem(globals(), "_REASON_MARKS", ())

# NAMING THE READER IS ITSELF COMPOSED, so that a paraphrase which uses
# none of the old nouns still counts as naming them. The reader does two
# things -- they CHOOSE what the description says, and they run the check
# MORE THAN ONCE -- and each of the patterns below is one of those two
# ATTACHED to the word for a description, with up to two words allowed
# in between. So "one profile of their own after another", "descriptions
# they wrote themselves" and "a sweep of hand-edited profiles" are all
# caught without any of them being written down here as a phrase.
#
# THE ATTACHMENT IS THE PRECISION, and it was measured rather than
# assumed. A first version of this looked for a choosing word anywhere
# within sixty characters of a description word, and went red on
# twenty-eight true sentences of this repository -- "the things the
# rules cannot settle on their own" beside the word `profile` on the
# front page, "a candidate declared missing never reaches this function"
# in the taxonomy, "how many values you named ... never the values
# themselves" in the profiler's summary. `profile` and `candidate` are
# two of the commonest words here and they usually mean something else,
# so what identifies this reader is not the vocabulary but the grammar:
# the choosing has to be MODIFYING the description.
_GAP_WORDS = r"(?:[a-z0-9'-]+ ){0,2}"
# THE NOUNS FOR A DESCRIPTION. `specification` and `spec` joined on
# review item P3-V6-F3, whose second probe -- "a succession of custom
# specifications leaves a suppressed tally unknowable" -- named this
# reader in a word this list did not hold and went undetected.
#
# THIS LIST IS THE ONE PLACE IN THIS FAMILY WHERE A MISS IS A FALSE
# NEGATIVE, and that is said here rather than discovered later. A
# missing WITHDRAWAL word makes the guard shout at a true sentence,
# which a maintainer fixes in a minute; a missing word for the READER
# makes the guard silent about a false one. No finite list of nouns
# bounds an infinite set of paraphrases, so this is a guard and not a
# proof, and what would be a proof is written in plan amendment
# A-P3-17: one canonical passage, quoted, with every other mention of
# this reader refused outright.
_DESCRIPTIONS = r"(?:description|profile|specification|spec)s?\b"
# ...and the plural, where the singular means something else. ONE
# hand-written description is an ordinary thing to write about: it is a
# profile somebody edited into a state its own facts contradict, and the
# generation method spends two paragraphs on what the walk does with it.
# HAND-WRITTEN DESCRIPTIONS, plural, is a sweep and is nothing else.
_DESCRIPTIONS_MANY = r"(?:description|profile|specification|spec)s\b"
# The same nouns, plus the words for one RUN of the check, wherever a
# pattern below counts things rather than naming what they say.
_RUN_NOUNS = (
    r"(?:description|profile|specification|spec|run|report|guess)s\b"
)

# Choosing what the description says. "submitted" is deliberately absent:
# the submitted description is what `synthtwin validate` is always handed
# and is the ordinary word for it throughout this repository, so banning
# it would put this in a fight with every true sentence about the gate.
# "its own" is absent for the same reason -- a file's own description is
# the envelope V5.1 is drawn round, not somebody's invention.
_CHOSEN_MARKS = (
    rf"\bcandidate {_GAP_WORDS}{_DESCRIPTIONS}",
    rf"\b(?:their|your|his|her) own {_GAP_WORDS}{_DESCRIPTIONS}",
    rf"\b{_DESCRIPTIONS} of (?:their|your|his|her) own\b",
    (
        rf"\b{_DESCRIPTIONS} {_GAP_WORDS}"
        r"(?:they|you|somebody|someone|anybody|anyone) "
        r"(?:wrote|write|writes|chose|choose|chooses|made|make|makes|"
        r"craft|crafts|crafted|invent|invents|invented|pick|picks|"
        r"picked)\b"
    ),
    (
        r"\bhand-(?:crafted|written|edited|picked|chosen|made) "
        rf"{_GAP_WORDS}{_DESCRIPTIONS_MANY}"
    ),
    rf"\bmade[- ]up {_GAP_WORDS}{_DESCRIPTIONS_MANY}",
)

# Running it more than once, attached the same way.
_REPEAT_MARKS = (
    rf"\b{_DESCRIPTIONS} {_GAP_WORDS}after (?:an)?other\b",
    rf"\b{_DESCRIPTIONS} {_GAP_WORDS}one by one\b",
    (
        rf"\brepeated {_GAP_WORDS}"
        r"(?:description|profile|specification|spec|run|report|check|"
        r"guess|candidate)s\b"
    ),
    (
        r"\b(?:a |any |no )?(?:sequence|series|succession|sweep) of "
        rf"{_GAP_WORDS}(?:candidate |custom |hand-\w+ )?{_RUN_NOUNS}"
    ),
    (
        rf"\b(?:many|several|eleven|six|dozens of) {_GAP_WORDS}"
        r"(?:candidate |custom |hand-\w+ )?"
        r"(?:description|profile|specification|spec|guess)s\b"
    ),
)

# ...and the terms that name this reader on their own, because in this
# repository they mean nothing else. Each was grepped over every surface
# before it was put here: `sweep` appears in the changelog, in
# `validation.py` and in the validation method and is about this and
# nothing else every time; `again and again` and `over and over` appear
# nowhere but in the paragraphs this ruling wrote.
_SEARCHER_ALONE = (
    r"binary[ -]search",
    r"one guess at a time",
    r"count oracle",
    r"no matter how many",
    r"however many (?:times|runs|descriptions|profiles|reports|tries)",
    r"which verdicts? (?:change|move|flip)",
    r"watching which (?:verdict|line|check|number)s?",
    r"\bsweep(?:s|ing)?\b",
    r"\bagain and again\b",
    r"\bover and over\b",
    r"\btime after time\b",
    r"\bre-?runs? (?:this|the) check\b",
    r"\bre-?running (?:this|the) check\b",
)

# "Run the command again" is NOT here, and could not be: it is the last
# sentence of half the refusals in `errors.py`, telling a person to fix
# their file and try once more. Repetition on its own is not this
# reader; repetition of a description this person chose is.

# Two shapes a reader might expect above are deliberately absent, for the
# reason the second family's list gives about bans the truth trips: a
# bare count of runs ("two runs of the same description and seed write
# the same cells" is the determinism guarantee) and a bare "however many"
# ("however many figures it takes" is the number formatter) say nothing
# about anybody searching, and banning them would earn this an exception
# list within a week.

# The promise. These are the words a guarantee is made of, and none of
# them is a defect on its own -- this product refuses, stops and
# protects a great many things. What they may not do is stand in a
# sentence that names the reader above.
_PREVENTION_MARKS = (
    r"\bcannot\b",
    r"\bcan not\b",
    r"\bcan't\b",
    r"\bcould not\b",
    r"\bcouldn't\b",
    r"\bunable\b",
    r"\bimpossible\b",
    r"\bno way\b",
    r"\bprevent",
    r"\bstop",
    r"\bdefen[cs]e",
    r"\bdefend",
    r"\bprotect",
    r"\bguards? against\b",
    r"\bbarrier\b",
    r"\bimmune\b",
    r"\bresists?\b",
    r"\bproof against\b",
    r"\bnever\b",
    (
        r"\bno (?:sequence|number|amount|series|set|report|run|candidate|"
        r"description|profile|guess)\b"
    ),
    r"\bno closer\b",
    r"\bfoil",
    r"\bdefeat",
    r"\bsafe from\b",
)
# "block" is deliberately absent, and so are "at most" and "bounded":
# a block is a piece of a description throughout this repository, "at
# most N cells" is how every ceiling obligation is worded, and a bound
# is what half the generation method states. None of the three says
# anybody is being kept out of anything.

# THE OTHER WAY THE GUARANTEE IS MADE, and the way it was actually
# written every time it went wrong: not as "they cannot" but as the
# REASON a rule exists. "Repeated candidate profiles would OTHERWISE
# binary-search a value the file's own profile withholds" is P3-D3's
# own sentence, and it promises the defence exactly as hard as the
# negative form does -- it says this rule is here to stop them, so with
# it they are stopped. A ban that read only the negative form would have
# passed every one of the six surfaces the ruling had to correct.
_REASON_MARKS = (
    r"\botherwise\b",
    r"would (?:then|otherwise|be able)",
    r"\bthe attack\b",
    r"exists to\b",
    r"\bwhich is why\b",
    r"\bthat is why\b",
    r"for that reason\b",
    r"on that ground\b",
    r"\bthe (?:whole )?(?:reason|ground) (?:this|the|it|that)\b",
    (
        r"so (?:the |this |its )?(?:gate|rule|verdict|subcheck|check|"
        r"report|line) (?:closes|close|is|are|was|were|withholds|"
        r"stays|must)"
    ),
    # Naming the disclosure gate in the same breath as this reader IS
    # the promise, whatever verb stands between them: the gate is the
    # thing that was said to stop them.
    r"\b(?:the|this) gate\b",
)

# A THIRD WAY THE GUARANTEE IS MADE, and the one the review walked
# straight through (review item P3-V6-F3). Not "they cannot" and not
# "the rule is here to stop them", but "they end up knowing nothing":
# "repeated profiles reveal nothing about a count this report withholds"
# promises the defence exactly as hard as the other two and used none of
# their words. What identifies this shape is a word for KNOWING NOTHING
# standing in a sentence that names the reader -- the promise is in the
# outcome rather than in the barrier.
#
# "nothing" BARE is deliberately absent, and the reason is the reason
# every other list here gives for what it leaves out. The naming half
# has false matches of its own -- "a battery of eleven producer
# descriptions" in the changelog is a test fixture and not a sweep --
# and a bare "nothing" beside one of those turns a true sentence red
# for no reason at all. What identifies this shape is nothing paired
# with KNOWING: nothing ABOUT something, or a verb of learning with
# nothing after it.
_KNOWING = (
    r"learn|reveal|tell|show|say|give|leak|yield|betray|disclose|"
    r"narrow|recover|deduce|infer|locate|expose|pin down|work out"
)
_KNOWLEDGE_MARKS = (
    rf"\b(?:{_KNOWING})[a-z]* (?:nothing|no more)\b",
    r"\bnothing (?:about|of|more|at all)\b",
    rf"\bnothing (?:{_KNOWING})",
    r"\bunknowable\b",
    r"\bno more than\b",
    rf"\bnot [a-z0-9 ,'`-]{{0,24}}(?:{_KNOWING})",
)

# What makes a passage the honest account rather than the claim. Any one
# of these standing near the naming says the defence is not being
# offered, which is the sentence the ruling requires rather than the one
# it bans.
_WITHDRAWN_MARKS = (
    r"no longer",
    r"out of scope",
    r"withdraw",
    r"used to",
    r"stopped promising",
    r"not a defen[cs]e",
    r"not a barrier",
    r"not protection",
    r"no rule",
    (
        r"(?:does|do|did|is|are|was|were|would|will) not "
        r"[a-z0-9 ,'`-]{0,24}(?:try|defend|stop|protect|promise|claim|"
        r"prevent|bar|guard)"
    ),
    r"not (?:owed|promised|claimed|in scope)",
    r"this lowers",
    r"ruled? (?:it |that |them |the )?out",
    r"superseded",
    # ...and the forms the governing plans use when they report a
    # question and its answer, or quote what a passage USED to say.
    # A missing entry here costs a false red on a true sentence, which
    # is the safe direction and is why this list may grow freely.
    r"the ruling was: no",
    r"what was promised",
    r"is what stood here",
    r"is withdrawn",
    r"put (?:it |them |that )?out of scope",
    r"reverses? (?:on its own|by)",
    r"no longer (?:true|promised|claimed|offered|says|stands)",
)

# HOW FAR A WITHDRAWAL REACHES, AND IN WHICH DIRECTION (review item
# P3-V6-F3). It used to reach three hundred characters either way, and
# the review walked through the half that reached FORWARD: "this
# protection is no longer offered. no sequence of candidate descriptions
# can narrow a number this report withholds" passed, because the
# withdrawal in the first sentence cured the promise restored in the
# second. A withdrawal followed by the promise is not an honest account;
# it is the promise, with a disclaimer in front of it.
#
# So the reach is asymmetric, and it follows how the prose is actually
# written. Naming the old promise and THEN withdrawing it is the shape
# every honest passage here takes -- the history is told, then the
# ruling -- so a withdrawal that stands AFTER the naming still cures it
# within a paragraph. A withdrawal that stands BEFORE it cures only what
# is in its own statement, because anything further on is a new
# assertion and reads as one.
_CURE_WINDOW = 300

# Where one statement ends and the next begins, in the collapsed text.
# The same three enders `_SENTENCE_ENDS` uses above, for the same
# reason, plus the exclamation and question marks no surface here uses.
# A COLON IS NOT AN ENDER: "what is withdrawn is the half that claimed:
# that somebody who writes their own descriptions cannot narrow a
# withheld number" is one sentence which withdraws the claim it spells,
# and splitting it at the colon would read the second half alone and
# call the honest changelog entry a defect.
_STATEMENT_END = re.compile(r"(?<=[a-z0-9)\]\"'*])[.;!?] | -- ")

# WHEN THE PROMISE IS IN THE NEXT STATEMENT (review item P3-V7-F8).
# "A person can re-run the check with descriptions they wrote
# themselves; the withheld number remains unknowable" promises the
# withdrawn defence exactly as hard as any one-statement wording of it,
# and every word of it was already in the lists. It walked past because
# the rule read ONE STATEMENT AT A TIME: the first half named the reader
# and promised nothing, the second half promised and named nobody, and
# `_STATEMENT_END` split them at the semicolon.
#
# SO THE PROMISE MAY BE CARRIED FORWARD, AND THE PRICE OF THAT IS
# MEASURED RATHER THAN HOPED FOR. Carrying a bare promise mark forward
# reports honest prose: "...is normally the person holding the table.
# A newer description means this synthtwin is behind, and the advice is
# to update synthtwin and never to re-run a profiler" collides `never`
# with a naming that was about something else, and there are between
# four and ten such collisions on this tree depending on how far the
# carry reaches. So a carried promise has to be ABOUT THE WITHHELD
# THING, in the format's own words for it. With that requirement the
# carry reports NOTHING on this tree at any reach up to four hundred
# characters, and reports the sentence above.
#
# WHAT THIS DOES NOT CLOSE, said here rather than left to the next
# round. A promise carried further than `_CURE_WINDOW`, and a promise
# about the withheld number that uses none of these words for it, are
# both still missed. The naming half is unchanged and keeps the standing
# bound written beside `_DESCRIPTIONS`: it is a finite list of nouns,
# no such list is sound, and the sound alternative -- one canonical
# passage, every other mention refused -- was measured at thirty-four
# statements to rewrite and is an owner decision (plan amendment
# A-P3-17 clause 1).
_THE_WITHHELD_THING = (
    r"\b(?:withheld|withholds|withhold|withholding|suppressed|held back)\b"
)


def _promise_marks_in(statement: str) -> "list[str]":
    """Every wording in one statement that makes the withdrawn promise."""
    return [
        mark
        for mark in _PREVENTION_MARKS + _REASON_MARKS + _KNOWLEDGE_MARKS
        if re.search(mark, statement)
    ]


def _carried_promise(after: "list[str]") -> "tuple[str, str] | None":
    """The promise a following statement makes about the withheld thing.

    ``after`` is the statements that follow the naming one, in order.
    They are read while they stay within `_CURE_WINDOW` of it, which is
    the same reach the cure is allowed and is inside the four hundred
    characters measured clean above.
    """
    reached = 0
    for statement in after:
        reached = reached + len(statement)
        if reached > _CURE_WINDOW:
            return None
        if re.search(_THE_WITHHELD_THING, statement) is None:
            continue
        promised = _promise_marks_in(statement)
        if not promised:
            continue
        if _withdrawn_in(statement):
            return None
        return (statement, promised[0])
    return None


def _names_the_reader(sentence: str) -> "str | None":
    """How this sentence names the reader the ruling put out of scope.

    Either by a term that means nothing else in this repository, or by
    attaching a word for CHOOSING a description, or for running it MORE
    THAN ONCE, to the word for a description. Both halves are needed:
    neither is a defect on its own, and every paraphrase of this reader
    has to write both.
    """
    for mark in _SEARCHER_ALONE + _CHOSEN_MARKS + _REPEAT_MARKS:
        if re.search(mark, sentence) is not None:
            return mark
    return None


def _promises_a_defence(text: str) -> "list[tuple[str, str, str]]":
    """Every sentence of one surface that promises the withdrawn defence.

    Returns the sentence, the wording that named the out-of-scope
    reader, and the wording that made the promise about them -- so the
    failure message can show a maintainer which two words collided
    rather than telling them a document is wrong somewhere.

    A PROMISE IS ANY OF THREE FORMS. Saying they cannot is one; giving
    them as the reason a rule exists is the second, and it was the
    commoner of the two in the text this replaced; saying they end up
    knowing nothing is the third, and it is the one review item
    P3-V6-F3 walked through.

    AND IT NEED NOT BE IN THE SAME STATEMENT AS THE NAMING (review item
    P3-V7-F8). A statement that names the reader and promises nothing,
    followed by one that promises something about the WITHHELD THING and
    names nobody, is the promise written across a semicolon. The reach
    and the price of carrying it are measured beside
    `_THE_WITHHELD_THING`, with what it still does not close.

    AND THE CURE IS DIRECTIONAL. A withdrawal after the naming cures it
    within a paragraph, which is how every honest passage here is
    written. A withdrawal BEFORE it cures only its own statement: a
    promise that follows a disclaimer is a promise.

    Guarantees:

    - Inputs: one surface's text, lowercased and space-collapsed by
      `_text`.
    - Determinism: a fixed function of that text; nothing is read here.
    - Errors raised: none.
    - Boundary: pure text; opens nothing.
    """
    found: list[tuple[str, str, str]] = []
    at = 0
    statements = _STATEMENT_END.split(text)
    for index, sentence in enumerate(statements):
        start = text.find(sentence, at)
        at = start + len(sentence)
        named = _names_the_reader(sentence)
        if named is None:
            continue
        if _withdrawn_in(sentence):
            continue
        promised = _promise_marks_in(sentence)
        said = sentence
        if not promised:
            carried = _carried_promise(statements[index + 1 :])
            if carried is None:
                continue
            said = f"{sentence}; {carried[0]}"
            promised = [carried[1]]
        if _withdrawn_in(text[at : at + _CURE_WINDOW]):
            continue
        found.append((said, named, promised[0]))
    return found


def _withdrawn_in(passage: str) -> bool:
    """Whether this passage says the defence is not being offered."""
    for mark in _WITHDRAWN_MARKS:
        if re.search(mark, passage) is not None:
            return True
    return False


def test_no_public_surface_promises_a_defence_against_re_running() -> None:
    """No surface says a person choosing the description can be stopped.

    The negative half of the fourth family. It runs over every surface,
    including the ones with no obligation to state the limit at all: a
    module comment need not explain the ruling, but none of them may
    give the withdrawn defence as a live reason for a rule -- which is
    exactly the shape the ruling found in three comment blocks of
    `validation.py`, in two passages of the validation method, and in
    the plan's own P3-D3.
    """
    offenders: list[str] = []
    for relative in DEFENCE_SURFACES:
        for sentence, named, promised in _promises_a_defence(_text(relative)):
            offenders.append(
                f"{relative}: {named!r} promised against by {promised!r}\n"
                f"      {sentence[:300]}"
            )
    assert not offenders, (
        "These surfaces promise a defence the owner withdrew on "
        "2026-08-14 (plan amendment A-P3-13, validation method "
        "V5-A1):\n  "
        + "\n  ".join(offenders)
        + "\n\nWhat synthtwin promises is about ONE report: a number the "
        "quality report withholds is a number it does not print, "
        "anywhere, so the report can be handed to a person who holds no "
        "file. It promises NOTHING about a person who holds the checked "
        "file and runs the check again with descriptions of their own -- "
        "that person can narrow a withheld number, and the reason it is "
        "not defended against is that they can read the file instead. "
        "Say what the rule does, and say what it does not; if the "
        "sentence is about the withdrawal itself, say the defence is "
        "gone in the same breath as naming it."
    )


def test_every_governing_document_is_a_surface() -> None:
    """The surface list cannot omit a document that GOVERNS.

    REVIEW ITEM P3-V6-F3. Three of the five governing documents were
    walked and two were not, and the ban above named a passage of one of
    the two as a place the 2026-08-14 ruling had to correct -- so the
    guard claimed a reach it did not have. The governing set is the
    disposition seal's own, which is where the question "does this
    document decide what the code owes" is already answered, so this
    cannot drift with a list somebody forgot to extend.
    """
    missing = [
        relative
        for relative in dispositions.GOVERNING
        if relative not in DEFENCE_SURFACES
    ]
    assert not missing, (
        "these documents govern what synthtwin owes and no claim in "
        "this file is checked against them:\n  " + "\n  ".join(missing)
        + "\n\nA governing document is not audit trail: it is edited by "
        "amendment and a reviewer reads it as the normative statement. "
        "Add it to SURFACES."
    )
    assert len(dispositions.GOVERNING) >= 5, dispositions.GOVERNING


# The three sentences review round 6 wrote to walk through this guard,
# kept as the guard's own red cases. Each promises the withdrawn defence
# in a shape the lists did not hold: the outcome rather than the barrier,
# a word for a description the nouns did not carry, and a withdrawal
# standing in FRONT of the promise it was read as curing.
WALKED_THROUGH = (
    (
        "the outcome instead of the barrier",
        (
            "Repeated profiles reveal nothing about a count this report "
            "withholds."
        ),
    ),
    (
        "a word for a description the nouns did not carry",
        (
            "A succession of custom specifications leaves a suppressed "
            "tally unknowable."
        ),
    ),
    (
        "a withdrawal in front of the promise it was read as curing",
        (
            "This protection is no longer offered. No sequence of "
            "candidate descriptions can narrow a number this report "
            "withholds."
        ),
    ),
    # ...and round 7's, which used no new vocabulary at all: every word
    # of it was already in the lists, and it walked past because the
    # rule read one statement at a time (review item P3-V7-F8).
    (
        "the promise split across two statements",
        (
            "A person can re-run the check with descriptions they wrote "
            "themselves; the withheld number remains unknowable."
        ),
    ),
    (
        "the naming and the promise in two full stops",
        (
            "Somebody can hand synthtwin one profile of their own after "
            "another. Not one of them will narrow a number this report "
            "withholds."
        ),
    ),
)


@pytest.mark.parametrize("shape,passage", WALKED_THROUGH)
def test_the_guard_catches_the_sentences_that_walked_through_it(
    shape: str, passage: str
) -> None:
    """Each probe the review wrote is a defect this guard now reports.

    Run against `_promises_a_defence` directly rather than against a
    file, because what is being held here is the RULE and not any
    surface's current wording.
    """
    found = _promises_a_defence(" ".join(passage.lower().split()))
    assert found, (
        f"this sentence promises the withdrawn defence -- {shape} -- and "
        f"the guard reported nothing:\n  {passage}"
    )


def test_a_withdrawal_after_the_promise_still_cures_it() -> None:
    """The cure did not become no cure, which would be the other defect.

    A guard that reported every honest passage would be turned off
    within a week, so the direction the prose is actually written in --
    name the old promise, then withdraw it -- has to keep passing.
    """
    honest = (
        "no sequence of candidate descriptions can narrow a number this "
        "report withholds. that is what this repository used to say, and "
        "the owner ruled it out on 2026-08-14."
    )
    assert not _promises_a_defence(honest), (
        "a passage that states the old promise and withdraws it in the "
        "next breath is the sentence the ruling asks for"
    )


# Where the withdrawn guarantee has to be replaced by the true statement,
# and not merely left unsaid. Deleting the promise satisfies the ban
# above and leaves WITHHELD reading exactly as it did -- as a bound on
# what the tool can be made to reveal -- which is the worse of the two
# failures, because nothing signals that a question was ever settled.
#
# The five are the surfaces a person meets the withholding on: the
# charter an implementer works from, the front page's limits table, the
# security document an institution weighs, the module that decides what
# a report may say, and the module that writes the report a researcher
# reads. The rendered report itself is held to the same statement by
# `tests/test_ap313_stated_limit.py`, which reads the text a run
# actually produces rather than the source that produces it -- both are
# needed, because a paragraph can be present in the source and
# unreachable in the page.
LIMIT_BEARING = (
    "CLAUDE.md",
    "README.md",
    "SECURITY.md",
    "src/synthtwin/quality.py",
    "src/synthtwin/validation.py",
)

# The four marks of the true statement. As with the other families, each
# entry is a tuple of accepted phrasings so a surface may speak in its
# own register -- the charter and the two modules in the normative one,
# the front page and the security document in the one a person deciding
# whether to use the tool reads.
#
# Why each mark and not only the last:
#
# 1. Without "one report", the limit reads as though the withholding
#    were worthless, and it is not: it is what lets a report travel.
# 2. Without the person who runs it again, the reader has no idea who is
#    outside the promise, and will supply their own guess.
# 3. Without the reason, the limit reads as an oversight somebody will
#    fix, rather than as a decision with a ground -- and the ground is
#    the actionable part: hold the file closely, because the report is
#    not what is protecting it.
# 4. Without the plain statement that synthtwin does not try, a reader
#    takes the first three as a description of a weak defence rather
#    than of no defence.
NARROWED_MARKS = (
    (
        ("one report", "a single report"),
        (
            "the statement that the rule is about what ONE report says, "
            "which is what the withholding still buys"
        ),
    ),
    (
        (
            "again and again",
            "over and over",
            "re-runs the check",
            "re-run the check",
            "one after another",
        ),
        (
            "the person the rule is NOT about: somebody who has the "
            "checked file and runs the check again with descriptions of "
            "their own"
        ),
    ),
    (
        (
            "can read the file",
            "can read it",
            "requires holding",
            "in front of them",
            "holds the file",
        ),
        (
            "the reason, which is the actionable half -- whoever can run "
            "this check on a file can read that file"
        ),
    ),
    (
        ("does not try to stop", "do not try to stop"),
        (
            "the plain statement that synthtwin does not try to stop "
            "them, so that no reader takes the limit for a weak defence "
            "rather than none"
        ),
    ),
)


def test_the_limit_bearing_surfaces_state_the_narrowed_promise() -> None:
    """The five deciding surfaces each carry all four marks of the limit.

    The positive half of the fourth family, and the half that is easy to
    lose: a guarantee that is quietly dropped leaves every reader who
    learned it still believing it, and there is no wording left on the
    page for the ban above to catch.
    """
    missing: list[str] = []
    for relative in LIMIT_BEARING:
        text = _text(relative)
        for forms, what_it_is in NARROWED_MARKS:
            if not any(form in text for form in forms):
                missing.append(
                    f"{relative} is missing {what_it_is} "
                    f"(expected one of {list(forms)})"
                )
    assert not missing, (
        "These surfaces have to state what the quality report's "
        "withholding protects and what it does not, in full, and each "
        "is missing part of it:\n  "
        + "\n  ".join(missing)
        + "\n\nAll four parts are load-bearing: the protection without "
        "the limit is the promise the owner withdrew, and the limit "
        "without the protection reads as though withholding did nothing "
        "at all."
    )


def test_the_fourth_family_would_notice_the_promise_it_replaced() -> None:
    """A vacuity floor, in both directions, over many wordings.

    THE FIRST HALF. A compositional ban passes trivially when one of its
    two lists is wrong, and a ban on a claim written five ways in five
    places has to be shown against more than one of them. Every sentence
    below is either one this repository actually carried before the
    ruling -- taken from the plan, the validation method and
    `validation.py` -- or a plain rewording of it of the kind somebody
    would write next time. Each must still be caught, with no
    withdrawal near it.

    THE SECOND HALF, and it is not decoration. A ban this broad could
    make the honest paragraph unwritable, and then the positive check
    above and this one would be at war: whoever satisfied one would trip
    the other, and the way that argument ends is with an exception list.
    So the truthful statements are put through it too, and must pass.
    """
    promised = {
        "the plan's P3-D3, as it stood": (
            "a within-bound or missed line against a candidate value is "
            "itself a measurement-derived statement, and repeated "
            "candidate profiles would otherwise binary-search a value "
            "the file's own profile withholds."
        ),
        "the validation method's V5.3, as it stood": (
            "repeated candidate profiles would binary-search a number "
            "the file's own description withholds, so where the gate "
            "closes over a subcheck its verdict is withheld."
        ),
        "the pooled-style comment in validation.py": (
            "a verdict that told them apart would state about the file a "
            "count the file's own description withheld, and repeated "
            "candidate descriptions would then read the count off the "
            "verdicts, which is the attack V5.3 says the gate exists to "
            "stop."
        ),
        "the refused-file comment in validation.py": (
            "repeated candidate descriptions would then read the header "
            "off the verdicts, which is the attack the gate exists to "
            "stop."
        ),
        "the rounding function's own docstring": (
            "what a candidate sweep can still learn is which block the "
            "count lies in, and no sequence of candidate descriptions "
            "can get closer than that."
        ),
        "A-P3-5 clause 3's bound": (
            "styles.spelled takes no number from the submitted "
            "description at all, so no sequence of candidate "
            "descriptions can binary-search anything through it."
        ),
        "a rewording with none of the old nouns": (
            "somebody feeding the tool one profile of their own after "
            "another is stopped by this rule, whatever they try."
        ),
        "a rewording in the second person": (
            "however many times you run the check with descriptions you "
            "wrote yourself, the withheld number never appears."
        ),
        "a rewording as a security property": (
            "the quality report is immune to a sweep of hand-written "
            "descriptions."
        ),
        "a rewording as a bound rather than an absolute": (
            "a person running this check again and again with their own "
            "descriptions gets no closer than a floor-wide block."
        ),
        "a rewording that never says the word description": (
            "watching which verdicts change over repeated runs reveals "
            "nothing: the search is defeated by the gate."
        ),
        "a rewording that puts the promise in the next statement": (
            "a person can re-run the check with descriptions they wrote "
            "themselves. the suppressed count cannot be narrowed."
        ),
    }
    uncaught = [
        f"{what}: {sentence!r}"
        for what, sentence in promised.items()
        if not _promises_a_defence(" ".join(sentence.lower().split()))
    ]
    assert not uncaught, (
        "These statements of the withdrawn guarantee are no longer "
        "caught by the fourth family, so the ban is vacuous for that "
        "wording:\n  "
        + "\n  ".join(uncaught)
        + "\n\nFix the naming marks or the promise marks rather than "
        "this assertion."
    )
    honest = {
        "the quality report's own page": (
            "what it is not is a barrier against somebody who has the "
            "checked file and runs this check on it again and again, "
            "each time with a description they wrote themselves, "
            "watching which lines move. that person can narrow a number "
            "withheld here, and synthtwin does not try to stop them: "
            "whoever can run this check on a file can read the file."
        ),
        "the validator module's contract": (
            "it is not a defence against somebody who holds the measured "
            "file and runs this check over and over with descriptions "
            "they wrote themselves, watching which verdicts change: that "
            "person can narrow a number a single report withholds, and "
            "this module does not try to stop them."
        ),
        "a comment telling the history before withdrawing it": (
            "this line rounded the recount down to a whole number of "
            "publication floors, so that a person trying one candidate "
            "description after another could locate the count no closer "
            "than a floor-wide block. that defence is no longer owed."
        ),
        "the changelog entry that spells what it withdraws": (
            "what is withdrawn is the second half the rule used to "
            "claim: that somebody who writes their own descriptions and "
            "runs the check again and again cannot narrow a withheld "
            "number by watching which verdicts change."
        ),
        # The two halves of the widening the other way (review item
        # P3-V7-F8): the carry may not turn an honest naming into a
        # defect because a later statement happens to hold one of the
        # promise words, and the honest statement of the limit is
        # written across statements more often than not.
        "the true account, written across two statements": (
            "a person can re-run the check with descriptions they wrote "
            "themselves. the number this report withholds can be "
            "narrowed that way, and synthtwin does not try to stop them."
        ),
        "a naming beside a promise word about something else": (
            "the advice is to describe the table again with descriptions "
            "of their own, which is safe because whoever holds an old "
            "description of a table normally holds the table. a newer "
            "description means this synthtwin is behind, and the advice "
            "is never to re-run a profiler."
        ),
    }
    wrongly_caught = [
        f"{what}: {found[0][0]!r}"
        for what, sentence in honest.items()
        if (found := _promises_a_defence(" ".join(sentence.lower().split())))
    ]
    assert not wrongly_caught, (
        "The fourth family now catches the truthful statement the "
        "ruling requires, which would leave a maintainer no way to "
        "write either one:\n  "
        + "\n  ".join(wrongly_caught)
        + "\n\nWiden `_WITHDRAWN_MARKS` or narrow the two lists above -- "
        "do not add a surface to an exception list, which is how every "
        "ban in this file would rot."
    )
    assert _CHOSEN_MARKS and _REPEAT_MARKS and _SEARCHER_ALONE
    assert _PREVENTION_MARKS and _REASON_MARKS and _WITHDRAWN_MARKS
    for relative in LIMIT_BEARING:
        assert relative in SURFACES, (
            f"{relative} must also be in SURFACES, so that the ban above "
            f"covers the surface the limit is stated on"
        )


# ---------------------------------------------------------------------
# THE FIFTH FAMILY: WHICH WIRE VERSION SYNTHTWIN SPEAKS, COUNTED FROM
# THE PRODUCT (owner ruling 2026-08-17; plan amendment A-P3-30)
# ---------------------------------------------------------------------
#
# WHAT WENT WRONG, ONCE MORE AND IN THE WORST PLACE. The format moved
# from version 4 to version 5 in three stages -- the specification, then
# the producer and the loader, then the validator. Each stage corrected
# the sentences it could see. What no stage saw was the top of
# `docs/spec/profile-contract-v5.md` itself, which opened by saying that
# the shipped producer wrote version 4, that the shipped loader read
# version 4 and nothing else, and that nothing in it might be written
# about anywhere in this repository as though it were built. By then the
# changelog, the security document and the plan all correctly described
# version 5 as shipped, the producer wrote it and the loader read it --
# so the one document that GOVERNS the format was the one document still
# denying it, and an institution's reviewer opening the contract first
# would have read the opposite of the truth in the first paragraph.
#
# This is the fourth family's failure mode wearing a number instead of a
# sentence, and it is the third family's answer that fits it: do not keep
# a list of wordings somebody has to remember to update. Take the number
# from the product and hold every surface to it.
#
# WHAT IS BANNED, AND WHAT IS DELIBERATELY NOT. Only a PRESENT-TENSE
# claim about what SYNTHTWIN ITSELF writes, reads, emits, produces or
# accepts. History is not banned and must not be: "version 4 rewrote
# each spelling before storing it" is how a format change is explained,
# and "the version 4 document governs for a version 4 profile" is the
# rule that keeps the older contract a record. Nor is the refusal
# banned: "a version 4 document is refused" is the behaviour, not a
# claim to be one. The pattern therefore needs a SUBJECT that is
# synthtwin -- the producer, the loader, the profiler, the package, the
# tool -- and a verb in the present, and only then does the number after
# it have to be the number the product carries.
#
# WHICH SURFACES. Every surface of `SURFACES`, and BOTH GOVERNING PLANS
# besides, for the withdrawn-defence family's reason rather than the
# count families': the wire version is not a roadmap statement about a
# phase that does not exist. A plan that says which version the shipped
# producer writes is stating today's fact, and the plan said it twice.
# `docs/spec/profile-contract-v4.md` is walked too and passes, because
# its own text describes what a version 4 READER and a version 4
# document do, never what this synthtwin does.
VERSION_SURFACES = DEFENCE_SURFACES

# The subject has to be synthtwin. `reader`, `consumer`, `producer of
# another kind` and every other actor a specification reasons about are
# deliberately absent: a contract that says what a version 3 reader does
# with a version 4 block is doing its job.
_WHO_IS_SYNTHTWIN = (
    r"(?:this |the )?(?:shipped )?"
    r"(?:synthtwin|producer|loader|profiler|package|tool)"
)

# HOW A VERSION IS NAMED, and this half was the bypass (review item
# P3-V9-F8; plan amendment A-P3-38 clause 1). The pattern used to
# require the two literal words `version 4`, so `synthtwin writes v4
# profiles.` walked straight through a ban whose subject and verb it
# satisfied outright -- no exotic noun, no trick, the ordinary way a
# person writes a version number in a sentence. A guard that catches one
# spelling of the thing it bans is a guard that reports a clean tree.
#
# So the naming half is the SPELLINGS, not a spelling: `version 4`,
# `version-4`, `version4`, `profile_version 4`, `v4`, `V4`, `v. 4`.
#
# TWO THINGS IT DELIBERATELY DOES NOT READ AS A VERSION, because this
# repository writes both of them constantly and a ban that fires on them
# is a ban somebody switches off:
#
#   * a `v` that is part of a path or a name -- `profile-contract-v4.md`,
#     `validation-method-v1.md` -- caught by the lookbehind, which
#     refuses a `v` preceded by a word character, a slash, a dot or a
#     hyphen;
#   * a clause reference or a dotted release -- `V2.4`, `v0.1.0` --
#     caught by the lookahead, which refuses a number followed by a dot
#     and another digit. A sentence-ending full stop is NOT refused,
#     because `synthtwin writes v4.` is exactly the sentence being
#     banned.
#
# Both exclusions were measured against every surface in
# `VERSION_SURFACES` before this landed: the widened pattern reports
# nothing on the tree, and `test_the_version_ban_reads_history_...`
# below holds it to the sentences this repository has to keep writing.
_NAMES_A_VERSION = (
    r"(?:(?<![A-Za-z0-9])version[ _-]*|(?<![\w/.-])v\.?[ ]?)"
    r"(?P<number>\d+)\b(?![\w-]|\.\d)"
)

# The narrow naming half as it shipped, kept for the red check below
# rather than described in a comment: a reinstatement that has to be
# written out again is a reinstatement nobody trusts.
_NAMED_THE_NARROW_WAY = r"\bversion (?P<number>\d+)\b"


def _naming_half() -> str:
    """How a version may be named, or the narrow way a red check asks for."""
    if os.environ.get("REINSTATE") == "P3-V9-F8":
        return _NAMED_THE_NARROW_WAY
    return _NAMES_A_VERSION


# The verb has to be present-tense and about speaking the format. The
# window between subject and verb, and between verb and number, is
# capped and may not cross a sentence end, so that two unrelated
# sentences cannot be read as one claim.
_SPEAKING_IT = r"(?:writes?|writing|reads?|reading|emits?|produces?|accepts?)"

# The same verbs as things DONE, for the passive shape below, and the
# be-forms that carry it. Both are needed and neither is a widening on
# its own: a bare participle is how this repository writes history
# ("the spelling was written into the file"), and it is the PRESENT
# be-form in front of it that makes the sentence a claim about today.
# `was` and `were` are deliberately absent for exactly that reason.
_SPOKEN = r"(?:written|read|emitted|produced|accepted)"
_IS_BEING = r"(?:is|are|be|being|been)"

# WHERE ONE CLAUSE ENDS AND THE NEXT BEGINS (review item P3-V10-F6).
# The fronted half below reads a version NUMBER first and a subject and
# verb after it, so it needs to know when it has left the clause the
# number is in -- otherwise "it says it is version 4, and this synthtwin
# reads version 5" reads as a claim about version 4, and that sentence
# is R11's own message.
#
# English joins clauses with function words, which is a CLOSED class,
# and that is why this half can be written at all. A bare `that`,
# `which` or `where` with no comma in front of it is NOT a join: it is
# the relative link the fronted shape is built out of ("version 4 is
# the version that synthtwin writes"), so only the comma'd form counts.
_A_NEW_CLAUSE = (
    r"(?:[;:]"
    r"|,?\s+(?:and|but|or|nor|yet|so|while|whereas)\b"
    r"|,\s+(?:that|which|where|when)\b"
    r"|\s+--\s+)"
)


def _within_the_clause(width: int) -> str:
    """Up to `width` characters that stay inside one clause."""
    return r"(?:(?!" + _A_NEW_CLAUSE + r")[^.!?\n]){0," + f"{width}" + r"}?"


def _version_claim() -> "re.Pattern[str]":
    """The FORWARD half: subject, then verb, then the version."""
    return re.compile(
        _WHO_IS_SYNTHTWIN
        + r"[^.!?\n]{0,140}?"
        + r"\b"
        + _SPEAKING_IT
        + r"\b[^.!?\n]{0,60}?"
        + _naming_half(),
        re.IGNORECASE,
    )


def _fronted_version_claim() -> "re.Pattern[str]":
    """The FRONTED half: the version first, and the claim after it.

    THE DEFECT THIS EXISTS FOR (review item P3-V10-F6; plan amendment
    A-P3-42 clause 3). The family read one arrangement of the three
    marks a wire claim is made of -- synthtwin, a verb about speaking
    the format, and a number -- and English has more than one:

        Version 4 profiles are what synthtwin writes.
        Version 4 profiles are written by synthtwin.
        Version 4 is the version the loader reads.

    Every one of those satisfies the family's own subject list, its own
    verb list and its own naming rule, and every one walked through the
    ban, because the ban was written as an ORDER. At the next format
    bump a true version 6 sentence elsewhere satisfies the positive
    half while one of these stays behind saying the opposite.

    SO THE ARRANGEMENT IS THE THING THAT IS CLOSED, and this half reads
    the other two arrangements over the same three marks:

      * the cleft -- number, then the subject, then the verb, with the
        relative link (`what`, `that`, `the version`) between them;
      * the passive -- number, then a PRESENT be-form, then the verb as
        a thing done, then `by` and the subject.

    Both stop at a clause join, because a number in one clause and a
    subject-verb pair in another are two statements and not one claim,
    and both refuse to fire where the verb already carries a version of
    its own -- that sentence is the forward half's business, and it is
    judged there on its own number.

    WHAT THIS DOES NOT CLOSE is written out and asserted in
    `test_the_version_ban_states_its_residue`. The verb is still a list,
    the arrangement rule cannot see across a clause join or a line
    break, and four of the five verbs are the same word in the present
    and the past, so a fronted HISTORY sentence built on one of them is
    reported and has to be reworded rather than excused.
    """
    return re.compile(
        _naming_half()
        + _within_the_clause(140)
        + r"(?:"
        + _WHO_IS_SYNTHTWIN
        + _within_the_clause(60)
        + r"\b"
        + _SPEAKING_IT
        + r"\b"
        + r"|\b"
        + _IS_BEING
        + r"\b"
        + _within_the_clause(40)
        + r"\b"
        + _SPOKEN
        + r"\b"
        + _within_the_clause(40)
        + r"by\s+"
        + _WHO_IS_SYNTHTWIN
        + r")"
        # A verb that carries its own version right after it is the
        # forward half's sentence, judged there against its own number.
        + r"(?!"
        + _within_the_clause(60)
        + _naming_half().replace("(?P<number>", "(?:")
        + r")",
        re.IGNORECASE,
    )


# THE RED CHECKS FOR THIS FAMILY. Each puts back exactly what stood
# before the repair, in memory, so that a guard which cannot fail is
# caught here rather than trusted:
#
#   REINSTATE=A-P3-30         the stale opening paragraph of the
#                             contract, word for word as it shipped --
#                             reds `test_no_surface_says_...`;
#   REINSTATE=A-P3-30-silent  every wire sentence deleted instead of
#                             corrected, which is what a ban satisfied
#                             by silence looks like -- reds
#                             `test_the_wire_version_is_actually_...`;
#   REINSTATE=A-P3-30-wide    the ban drawn without a synthtwin subject,
#                             which is the widening that would forbid
#                             explaining a format change at all -- reds
#                             `test_the_version_ban_reads_history_...`;
#   REINSTATE=P3-V9-F8        the naming half narrowed back to the two
#                             literal words `version N`, which is the
#                             bypass this family shipped with -- reds
#                             `test_the_ban_catches_every_ordinary_...`;
#   REINSTATE=P3-V10-F6       the FORWARD half alone, which is the
#                             arrangement this family shipped reading --
#                             reds `test_the_ban_catches_a_claim_...`
#                             and the second half of the residue check.
_THE_STALE_OPENING = (
    "**Status: written before any code, which is this repository's "
    "standing process.** The shipped producer writes version 4 today "
    "and the shipped loader reads version 4 and nothing else."
)


# THE VERSION AS A NOUN, with no number attached to it. This is what the
# third arrangement below needs and neither of the other two has: a
# sentence can name the version, say whose it is, and only then give the
# number, and the two words are then nowhere near each other.
_A_VERSION_NOUN = (
    r"(?:profile |description |document |format |wire |on-disk )?"
    r"versions?\b"
)

# The present copula that hands the number over. `was` and `were` are
# deliberately absent for the same reason they are absent from the
# passive shape: "the version synthtwin wrote was 4" is history, and
# history is not what this ban is drawn around.
_AMOUNTS_TO = r"(?:is|are)\b"


def _predicative_version_claim() -> "re.Pattern[str]":
    """The PREDICATIVE half: the version named, the number supplied later.

    THE DEFECT THIS EXISTS FOR (review item P3-V11-F3). The family read
    two arrangements and both of them require the version WORD and the
    version NUMBER to stand together, because both were built out of
    `_NAMES_A_VERSION`, which is a rule about a number with `version` or
    `v` in front of it. English does not require that:

        The profile version synthtwin writes is 4.
        The version this synthtwin reads is 4.
        The description version the loader accepts is 4.

    Each uses this family's own version noun, its own subject and its
    own verb, in the ordinary arrangement that names a thing, says whose
    it is and then says what it amounts to -- and each walked straight
    through, because the number arrives after a copula with nothing in
    front of it. At the next format bump one true sentence elsewhere
    satisfies the positive half while one of these sits behind a green
    suite saying the opposite on a governed surface.

    So this half reads the version as a NOUN and takes the number from
    the copula, in the two orders the relative clause can take:

      * the zero relative or `that`/`which` -- the version noun, then
        the subject, then the verb, then `is` and the number;
      * the reduced passive -- the version noun, the verb as a thing
        done, `by` and the subject, then `is` and the number.

    Everything between stays inside one clause, on the fronted half's
    own rule, so a version noun in one clause and a number in another
    are two statements rather than one claim.

    WHAT IT DOES NOT CLOSE is asserted in
    `test_the_version_ban_states_its_residue`: the verb is still a list,
    neither window crosses a clause join or a line break, and a claim
    whose number arrives through a verb other than `is`/`are` -- "comes
    to 4", "stands at 4" -- is a copula list and is missed.
    """
    number = (
        r"(?:still |now |currently )?"
        r"(?:version[ _-]*|v\.?[ ]?)?(?P<number>\d+)\b(?![\w-]|\.\d)"
    )
    return re.compile(
        r"\b"
        + _A_VERSION_NOUN
        + r"(?:"
        + _within_the_clause(40)
        + r"\b"
        + _WHO_IS_SYNTHTWIN
        + r"\b"
        + _within_the_clause(30)
        + r"\b"
        + _SPEAKING_IT
        + r"\b"
        + r"|"
        + _within_the_clause(20)
        + r"\b"
        + _SPOKEN
        + r"\b"
        + _within_the_clause(20)
        + r"by\s+"
        + _WHO_IS_SYNTHTWIN
        + r"\b"
        + r")"
        + r"\s+"
        + _AMOUNTS_TO
        + r"\s+"
        + number,
        re.IGNORECASE,
    )


def _subjectless_claim() -> "re.Pattern[str]":
    """The naming half alone, which is the ban drawn without a subject."""
    return re.compile(_naming_half(), re.IGNORECASE)


def _claim_patterns() -> "tuple[re.Pattern[str], ...]":
    """Every arrangement the ban reads, or the one a red check asks for.

    Two patterns rather than one alternation, because both halves need
    the same `number` group and Python's own engine will not hold two
    groups of one name. Every check below reads this tuple, so a half
    added here is a half every check gains.
    """
    if os.environ.get("REINSTATE") == "A-P3-30-wide":
        return (_subjectless_claim(),)
    if os.environ.get("REINSTATE") == "P3-V10-F6":
        return (_version_claim(),)
    if os.environ.get("REINSTATE") == "P3-V11-F3":
        # The two arrangements this family shipped reading, which are the
        # two that need the version word and the number side by side.
        return (_version_claim(), _fronted_version_claim())
    return (
        _version_claim(),
        _fronted_version_claim(),
        _predicative_version_claim(),
    )


def _claims_in(text: str) -> "list[re.Match[str]]":
    """Every wire claim any arrangement finds, earliest first."""
    found: list[re.Match[str]] = []
    for pattern in _claim_patterns():
        found = found + list(pattern.finditer(text))
    return sorted(found, key=lambda match: match.start())


def _surface_text(relative: str) -> str:
    """One surface's text as the version ban reads it.

    The single door every version check goes through, so that a red
    check can put the retired wording back without touching the tree.
    """
    text = (REPO_ROOT / relative).read_text(encoding="utf-8")
    asked = os.environ.get("REINSTATE")
    if asked == "A-P3-30" and relative.endswith("profile-contract-v5.md"):
        return _THE_STALE_OPENING + "\n" + text
    if asked == "A-P3-30-silent":
        for pattern in _claim_patterns():
            text = pattern.sub("(the wire sentence, deleted)", text)
        return text
    return text


def _shipped_wire_version() -> int:
    """The profile version this product speaks, read from the product.

    Read from BOTH module constants, because they can disagree: a bump
    applied to one and not the other ships a loader that refuses its own
    producer's output, and every sentence below would then be checked
    against a number only half the product carries.

    That the producer actually WRITES this number into a description is
    checked separately by
    `test_the_producer_writes_the_version_its_constant_names`, which
    needs a folder to write a table into and so cannot live in here.

    Guarantees:

    - Inputs: none.
    - Determinism: a fixed function of the shipped package; nothing is
      read from disk and nothing is written.
    - Errors raised: `AssertionError` where the two constants disagree,
      so that a half-applied version bump fails here rather than in the
      field.
    - Boundary: no file of any kind is opened.
    """
    assert profile.PROFILE_VERSION == contract.PROFILE_VERSION, (
        "The producer and the loader name different profile versions "
        f"({profile.PROFILE_VERSION} and {contract.PROFILE_VERSION}). "
        "A version bump is applied to both in one commit, or the "
        "shipped loader refuses the shipped producer's own output."
    )
    return int(profile.PROFILE_VERSION)


def test_the_producer_writes_the_version_its_constant_names(
    tmp_path: pathlib.Path,
) -> None:
    """The constant the sentences are checked against is the wire itself.

    Without this, a constant that stopped reaching the document would
    leave every version sentence in the repository checked against a
    number no description carries -- which is the same class of quiet
    drift the families above exist to refuse.
    """
    text = fixtures.single_column_table(
        "only", [str(row) for row in range(30)]
    )
    path = fixtures.write(tmp_path, "table.csv", text)
    table = reading.read_table(str(path))
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = document["profile_version"]
    if os.environ.get("REINSTATE") == "A-P3-30-drift":
        # The red check: a constant that stopped reaching the wire. Both
        # halves of this file's version family read the constant, so a
        # drift here would leave every sentence checked against a number
        # no description carries.
        written = int(written) + 1  # type: ignore[arg-type]
    assert written == _shipped_wire_version(), (
        f"The producer writes profile_version {written} while its own "
        f"constant says {_shipped_wire_version()}. Every version "
        "sentence in this repository is checked against the constant, "
        "so the two may not differ."
    )


def test_no_surface_says_synthtwin_speaks_a_version_it_does_not() -> None:
    """Every present-tense wire claim names the version the product has.

    The negative half of the fifth family. A surface may say anything it
    likes ABOUT version 4 -- what it meant, what it lost, why it was
    replaced, that it is refused -- and may not say that synthtwin
    writes, reads, emits, produces or accepts it.
    """
    shipped = _shipped_wire_version()
    stale: list[str] = []
    for relative in VERSION_SURFACES:
        text = _surface_text(relative)
        for found in _claims_in(text):
            if int(found.group("number")) == shipped:
                continue
            line = text.count("\n", 0, found.start()) + 1
            said = " ".join(found.group(0).split())
            stale.append(f"{relative}:{line}: {said!r}")
    assert not stale, (
        "These sentences say synthtwin speaks a profile version it does "
        f"not. The product writes and reads version {shipped}:\n  "
        + "\n  ".join(stale)
        + "\n\nIf the version bumped, correct every sentence in the same "
        "commit. If the sentence is HISTORY -- what an older version "
        "did, or what an older document still means -- write it in the "
        "past tense and without a present-tense verb about synthtwin, "
        "which is what the ban is drawn around. Do not add a surface to "
        "an exception list: that is how every ban in this file rots."
    )


def test_the_wire_version_is_actually_claimed_somewhere() -> None:
    """The positive half, so that deleting the sentences is not a pass.

    A ban on saying the wrong number is satisfied by a repository that
    says no number at all, and the document a researcher is sent to when
    their description is refused has to say which version this synthtwin
    speaks. So at least one surface must make the claim, and the
    contract that governs the format must be one of them.
    """
    shipped = _shipped_wire_version()
    saying = [
        relative
        for relative in VERSION_SURFACES
        if any(
            int(found.group("number")) == shipped
            for found in _claims_in(_surface_text(relative))
        )
    ]
    assert saying, (
        f"No surface says synthtwin writes or reads version {shipped}. "
        "The ban above is satisfied by silence, which is not what it is "
        "for: state the shipped version on the contract that governs it."
    )
    governing = f"docs/spec/profile-contract-v{shipped}.md"
    assert governing in saying, (
        f"{governing} does not say that synthtwin writes or reads "
        f"version {shipped}. That document is the first thing an "
        "institution's reviewer opens, and it is the document that was "
        "found still denying the version it governs."
    )


def test_the_version_ban_reads_history_and_refusals_as_permitted() -> None:
    """What the ban must NOT catch, asserted rather than hoped.

    Every sentence below is one this repository needs to be able to
    write. If a future widening of `_NAMES_A_VERSION` or of the claim
    pattern catches one of them, the widening is wrong: a format change
    cannot be explained without naming the version it came from.

    A STALE number is what is checked for, not a match, because the ban
    is a ban on the wrong number and several of these sentences make the
    TRUE claim in passing -- R11's message says both versions in one
    breath, and it has to.

    THE LAST FOUR ARRIVED WITH THE WIDENING (review item P3-V9-F8). The
    naming half now reads a bare `v4`, and this repository is full of
    document names, clause numbers and release strings that hold a `v`
    next to a digit. Each of those is written out here, so a future
    narrowing of the two exclusions has to face them.

    THE FOUR AFTER THEM ARRIVED WITH THE FRONTED HALF (review item
    P3-V10-F6). Reading the version FIRST puts a number in front of
    every sentence in this repository that mentions one, so the half has
    to know where a clause ends. Three of the four are real sentences of
    this tree, measured before the half landed -- R11's own message, the
    version 4 contract's rule about what a version 4 loader accepts, and
    the plan's account of the stale paragraph it corrected -- and the
    fourth is the past tense of the shape the half reads. Each is here
    so that a future widening of the clause rule has to face them.
    """
    permitted = (
        (
            "version 4 rewrote each spelling into a printable form "
            "before storing it."
        ),
        (
            "the version 4 document governs for a version 4 profile, "
            "and this document governs for a version 5 profile."
        ),
        (
            "a version 4 document is refused with the message section "
            "10.2 fixes word for word."
        ),
        (
            "a version 3 reader that dispatches on role reads a "
            "version 4 column block correctly."
        ),
        "version 5 is version 4 with the changes in sections 4, 5 and 6.",
        "no group that version 4 withheld becomes named.",
        # The four the widened naming half has to walk past.
        "the loader reads docs/spec/profile-contract-v4.md and refuses it.",
        "the validator follows docs/spec/validation-method-v1.md.",
        "the producer writes the bytes the method's V2.4 fixes.",
        "synthtwin writes v0.1.0.dev0 into created_with.",
        # The four the FRONTED half has to walk past. The first three
        # are sentences of this tree.
        (
            "it says it is version 5, and this synthtwin reads "
            "version 6."
        ),
        (
            "a profile that exceeds the invention capacity is a valid "
            "version 4 profile and the loader accepts it."
        ),
        # The shape of the plan's own account of the paragraph it
        # corrected: a list of things a document said, joined with
        # `, that`, which is a clause boundary and not the relative
        # link the fronted shape is built out of.
        "the plan records version 4, that the loader reads nothing else.",
        "version 4 was what synthtwin wrote before the bump.",
        # The three the PREDICATIVE half has to walk past (review item
        # P3-V11-F3). The first is history, carried by a past copula the
        # half does not read; the second is a sentence about a reader,
        # which is deliberately not a synthtwin subject; the third names
        # the version the older CONTRACT governs for, which is the rule
        # that keeps that document a record.
        "the version synthtwin wrote before the bump was 4.",
        "the version a version 4 reader accepts is 4.",
        "the version the version 4 document governs for is 4.",
    )
    shipped = _shipped_wire_version()
    caught = [
        sentence
        for sentence in permitted
        if [
            found
            for found in _claims_in(sentence)
            if int(found.group("number")) != shipped
        ]
    ]
    assert not caught, (
        "The version ban now catches sentences this repository has to "
        "be able to write:\n  " + "\n  ".join(caught) + "\n\nNarrow "
        "`_NAMES_A_VERSION` -- never add an exception list."
    )


def test_the_ban_catches_every_ordinary_way_of_naming_a_version() -> None:
    """The positive half of the naming rule (review item P3-V9-F8).

    THE DEFECT THIS EXISTS FOR. The family shipped with a naming half
    that required the two literal words `version 4`, so
    `synthtwin writes v4 profiles.` passed both of its tests -- the
    negative one found no stale claim and the positive one found the
    true claim elsewhere, and both stayed green while a governed surface
    said synthtwin speaks a version it does not. No exotic noun was
    needed and none of the family's known finite lists was touched: the
    bypass is the ordinary way a person writes a version number.

    So the spellings are asserted rather than assumed. Each sentence
    below has the subject and the verb the ban is drawn around and names
    a version that is not the shipped one, and each must be caught.
    """
    shipped = _shipped_wire_version()
    stale = shipped + 1
    bypasses = (
        f"synthtwin writes v{stale} profiles.",
        f"the loader reads v{stale} and nothing else.",
        f"this synthtwin produces V{stale} descriptions.",
        f"the producer writes version-{stale} documents.",
        f"the profiler emits version{stale} files.",
        f"the tool accepts v. {stale} descriptions.",
        f"synthtwin writes profile_version {stale} into the description.",
        f"the shipped loader reads version {stale}.",
    )
    missed = [
        sentence
        for sentence in bypasses
        if not [
            found
            for found in _claims_in(sentence)
            if int(found.group("number")) != shipped
        ]
    ]
    assert not missed, (
        "These sentences claim synthtwin speaks a version it does not, "
        "and the ban walks past every one of them:\n  "
        + "\n  ".join(missed)
        + "\n\nWiden `_NAMES_A_VERSION`. A ban that catches one "
        "spelling of what it forbids reports a clean tree."
    )


def test_the_ban_catches_a_claim_written_the_other_way_round() -> None:
    """THE FINDING (review item P3-V10-F6), and it is an ARRANGEMENT.

    The family read one order of the three marks a wire claim is made
    of. `Version 4 profiles are what synthtwin writes.` uses the ban's
    own subject, its own verb and its own naming rule, in the ordinary
    English that fronts what a sentence is about -- and walked straight
    through, because the pattern was written as subject, then verb, then
    number and nothing else.

    What that costs is not hypothetical at a format bump: the positive
    half is satisfied by ONE true sentence anywhere in the tree, so a
    stale sentence in this shape sits behind a green suite saying the
    opposite of the truth on a governed surface.

    Both other arrangements are asserted here, in every spelling of the
    subject and of the verb the family holds.
    """
    shipped = _shipped_wire_version()
    stale = shipped + 1
    the_other_way_round = (
        # the cleft: the version, then the subject, then the verb
        f"Version {stale} profiles are what synthtwin writes.",
        f"Version {stale} is the version the loader reads.",
        f"v{stale} documents are what the producer emits.",
        f"version-{stale} files are what the profiler writes.",
        f"V{stale} is what this synthtwin reads.",
        f"version {stale} is the format the package produces.",
        f"v. {stale} descriptions are what the tool accepts.",
        # the passive: the version, a present be-form, the verb as a
        # thing done, and the subject after `by`
        f"Version {stale} profiles are written by synthtwin.",
        f"Version {stale} descriptions are accepted by the loader.",
        f"Version {stale} profiles are read by the loader.",
        f"v{stale} files are produced by the profiler.",
    )
    missed = [
        sentence
        for sentence in the_other_way_round
        if not [
            found
            for found in _claims_in(sentence)
            if int(found.group("number")) != shipped
        ]
    ]
    assert not missed, (
        "These sentences say synthtwin speaks a version it does not, "
        "written the way English fronts what a sentence is about, and "
        "the ban walks past them:\n  " + "\n  ".join(missed) + "\n\nThe "
        "arrangement is what has to be widened -- the subject list, the "
        "verb list and the naming rule already hold every one of these."
    )


def test_the_ban_catches_a_claim_whose_number_arrives_after_a_copula() -> None:
    """THE FINDING (review item P3-V11-F3), and it is an ARRANGEMENT again.

    Both arrangements the family read were built out of `_NAMES_A_VERSION`,
    which is a rule about a NUMBER with the version word in front of it.
    So both required the two to stand together, and

        The profile version synthtwin writes is 4.

    walked through on the family's own version noun, its own subject and
    its own verb, in the ordinary English that names a thing and then
    says what it amounts to. The cost is the same as last time and is not
    hypothetical: one true sentence anywhere satisfies the positive half
    while this one sits on a governed surface saying the opposite.

    Every spelling of the subject and of the verb is asserted, in both
    orders the relative clause takes.
    """
    shipped = _shipped_wire_version()
    stale = shipped + 1
    after_the_copula = (
        f"The profile version synthtwin writes is {stale}.",
        f"The version this synthtwin reads is {stale}.",
        f"The description version the loader accepts is {stale}.",
        f"The format version the producer emits is {stale}.",
        f"The version the profiler produces is {stale}.",
        f"The wire version the package writes is {stale}.",
        f"The version the tool accepts is {stale}.",
        # The same claim with the number spelled the other ways the
        # naming half already reads.
        f"The profile version synthtwin writes is v{stale}.",
        f"The profile version synthtwin writes is version {stale}.",
        f"The profile version synthtwin writes is still {stale}.",
        # ... and the reduced passive, where the subject arrives last.
        f"The version written by synthtwin is {stale}.",
        f"The document version accepted by the loader is {stale}.",
        f"The versions produced by the profiler are {stale}.",
    )
    missed = [
        sentence
        for sentence in after_the_copula
        if not [
            found
            for found in _claims_in(sentence)
            if int(found.group("number")) != shipped
        ]
    ]
    assert not missed, (
        "These sentences say synthtwin speaks a profile version it does "
        "not, with the number handed over by a copula rather than "
        "written against the version word, and the ban walks past "
        "them:\n  " + "\n  ".join(missed) + "\n\nThe arrangement is what "
        "has to be widened -- the subject list, the verb list and the "
        "version noun already hold every one of these."
    )


def test_the_version_ban_states_its_residue() -> None:
    """What this ban does NOT read, measured rather than implied.

    Four things stand open, and each is asserted here as a MISS so
    that nobody reads the three arrangements above as coverage. A later
    rule that closes any of them reds this test, which is the point:
    the closing is then argued in the open instead of assumed.

    1. THE VERB IS A LIST, and English has no closed one for putting a
       format on a wire. An invented verb is missed in every
       arrangement -- and the same claim is caught the moment it is
       written with a verb the list holds, which is what makes this a
       statement about the list rather than about the pattern.
    2. THE CLAUSE RULE CUTS BOTH WAYS. The fronted half stops at a
       clause join so that a number in one clause and a subject in the
       next are not read as one claim; the price is that a claim really
       written across a join is missed.
    3. A LINE BREAK HIDES A CLAIM FROM EVERY HALF. No window crosses a
       newline, deliberately -- two rows of a table and two items of a
       list must never be read as one sentence -- so a claim that
       happens to wrap is missed. This is the oldest of the three and
       was never stated.
    4. THE COPULA IS A LIST TOO, and it arrived with the predicative
       half (review item P3-V11-F3). That half takes the number from
       `is` or `are`, because those are what a claim about today is
       written with; a number handed over by any other verb -- "the
       version synthtwin writes comes to 4", "stands at 4" -- is
       missed. It is the same fact about English as the first: a list of
       verbs is a sample. The half is not thereby worthless, because
       the claim is caught the moment it is written with the copula
       everybody actually writes, and that is asserted beside the miss.

    THE TENSE IS READ ONLY AS FAR AS ENGLISH MARKS IT, and that is the
    fourth thing. `read` is the same word in the present and the past,
    and `emitted`, `produced` and `accepted` are the same word as a past
    tense and as a thing done. The passive shape can tell them apart,
    because it needs a PRESENT be-form in front of the verb and
    `was`/`were` are not in that list. Neither the forward shape nor the
    cleft can, so a HISTORY sentence that puts a synthtwin subject
    beside a version across one of those words is reported and has to be
    reworded rather than excused -- which is over-catching, not
    under-catching, and is the safe direction for a ban to fail in. One
    sentence of the plan was in exactly that shape and was passing only
    because of where its line happened to wrap; it now says `took`, so
    nothing about this family rests on a line break falling where it
    falls today.
    """
    shipped = _shipped_wire_version()
    stale = shipped + 1

    def stale_claims(sentence: str) -> list:
        return [
            found
            for found in _claims_in(sentence)
            if int(found.group("number")) != shipped
        ]

    # 1. A verb no list here holds, in both arrangements.
    invented = (
        f"synthtwin renders version {stale} profiles.",
        f"version {stale} profiles are what synthtwin renders.",
    )
    for sentence in invented:
        assert not stale_claims(sentence), (
            "The verb half is a list, and this test says so by asserting "
            f"that {sentence!r} is MISSED. It is now caught, which means "
            "the verb rule has changed. That is good news and it is not "
            "free: say in the open what closed it, and rewrite this "
            "clause to state whatever residue is left."
        )
    # ... and the same claim, in a verb the list does hold, is caught in
    # both arrangements. Without this the assertion above would pass on
    # a ban that had stopped working altogether.
    for sentence in (
        f"synthtwin writes version {stale} profiles.",
        f"version {stale} profiles are what synthtwin writes.",
    ):
        assert stale_claims(sentence), (
            "The ban no longer reads its own verbs; the residue "
            "assertions above are meaningless until that is fixed."
        )

    # 2. A claim split across a clause join.
    across_a_join = (
        f"Version {stale} is the old format, and it is what synthtwin "
        "writes."
    )
    assert not stale_claims(across_a_join), (
        "The fronted half now reads across a clause join. Check what it "
        "does to R11's own message -- 'it says it is version 4, and "
        "this synthtwin reads version 5' -- before calling this closed."
    )

    # 3. A claim broken by a line break.
    wrapped = f"synthtwin writes\nversion {stale} profiles."
    assert not stale_claims(wrapped), (
        "A wire claim wrapped across a line is now read. Say so in the "
        "open, and check the same widening against a two-row table and "
        "a two-item list before keeping it."
    )
    assert stale_claims(wrapped.replace("\n", " ")), (
        "The unwrapped form of that sentence is not caught either, so "
        "the assertion above is measuring nothing."
    )

    # 4. The predicative half's copula, and where the miss stops.
    another_copula = f"The profile version synthtwin writes comes to {stale}."
    assert not stale_claims(another_copula), (
        "The predicative half now takes its number from a verb other "
        f"than `is` or `are`:\n  {another_copula}\n\nThat is good news "
        "and it is a change to what this ban promises. Say so where the "
        "promise is written: the half's own docstring, amendment "
        "A-P3-43 in the plan, and this clause."
    )
    for sentence in (
        f"The profile version synthtwin writes is {stale}.",
        f"The version written by synthtwin is {stale}.",
    ):
        assert stale_claims(sentence), (
            "The predicative half no longer reads its own copula, so "
            "the miss asserted above is measuring nothing."
        )


# ---------------------------------------------------------------------
# THE SIXTH FAMILY: WHAT THE DESCRIPTION KEEPS OF THE WORDS YOU TYPED,
# READ FROM THE PRODUCER'S OWN PUBLICATION RULES (review item P3-V9-F1;
# owner ruling 2026-08-17; plan amendment A-P3-31)
# ---------------------------------------------------------------------
#
# WHAT WENT WRONG, AND IT IS THE ONE THIS FILE EXISTS FOR. `synthtwin
# profile my-table.csv --missing-value <a marker of your own>` publishes
# that marker in the description and prints it on the summary page,
# under the count of cells that wore it. Correctly: contract 5 section
# 3.2 way 4 is what makes a description readable back, and it is the
# whole reason version 5 exists. The SAME summary page told the reader,
# four screens lower, that synthtwin would keep no record of any word
# they typed outside its own thirteen; `SECURITY.md` said such a value
# was written nowhere at all; the governing contract said it twice, and
# the governing plan twice more.
#
# THE HARM IS THE ONE THE PROFILE'S SAFETY RESTS ON. A description is
# safer to move than the table because of what it withholds. A
# researcher who reads that a diagnosis code or a patient identifier is
# absent from it, and it is not, hands the file on. A false assurance
# about withholding is worse than no assurance, and this is the second
# time in this repository a confidentiality sentence went false when the
# format under it moved (the first is the fifth family, one number
# instead of one sentence).
#
# WHY NOT A LIST OF SENTENCES, AGAIN. The five that shipped were written
# five ways -- "written nowhere", "recorded nowhere", "nowhere at all",
# "never written", "will not keep one for you" -- across a page, a
# security document, a contract and a plan, by four separate hands. A
# ban anchored on any one of them catches one of them. So this family
# reads the PRODUCER, exactly as the third and fifth do:
#
#   * `profile.PUBLICATION_RULES` is the whole map of what may stand at
#     each path of a finished description, and one of its kinds --
#     `_SPELLING` -- means "text out of the person's table, character
#     for character". Every path carrying that kind is derived here.
#     `missing_by_source`'s KEY is one of them, and that single fact is
#     what makes every unscoped denial in this repository false.
#   * The regions that carry NO such text are derived from the same map
#     by subtraction, and the settings block is one of them. That is
#     what makes a SCOPED denial true, and it is why the cure below is
#     not a list of allowed phrases either: if a later format put a
#     spelling into the settings, `settings` would drop out of the
#     derived cure set and every scoped sentence in the repository
#     would go red on the commit that did it.
#   * And a run-driven test writes a real description with a real
#     declared word and reads the word back out of both files, because
#     a rule that permits a spelling is not yet a producer that writes
#     one.
#
# WHAT IS BANNED, AND WHAT IS DELIBERATELY NOT. A sentence trips this
# when it does two things at once: it NAMES the person's own typed value
# -- by possession, or by exclusion from synthtwin's own list -- and it
# DENIES that the thing is written, kept, recorded or stored. Neither
# half alone is a defect. Naming is required of six surfaces below;
# denying is ordinary English about the settings block, about a spelling
# the floor pooled, and about a column that publishes no value of the
# table, all three of which are TRUE and all three of which this
# repository has to be able to say.
#
# SO THE CURE IS A SCOPE, AND IT HAS TO BE ATTACHED TO THE DENIAL. This
# is the precision the whole finding turns on, and it was measured
# rather than assumed. The sentence that shipped on the summary page
# said, in one breath, that a word of the reader's own is not written
# into the settings AND that it is not written here -- the first half
# scoped and true, the second unscoped and false, four screens under the
# word itself. A rule that cured a whole statement would have read the
# first half and passed the second. So the scope must stand in the
# denial's OWN clause: from the nearest comma, semicolon, colon or
# joining word before it, to the next joining word after it.
#
# AND THE DENIAL MAY BE IN THE NEXT STATEMENT, on the fourth family's
# finding: the retired summary sentence named the reader's other words
# before a semicolon and denied after it, and a rule reading one
# statement at a time reported nothing.
#
# WHAT THIS DOES NOT CLOSE, said here rather than left for the next
# round, and amended by A-P3-41 because one of the three shrank, and by
# A-P3-43 because the model under it was wrong. A denial carried further
# than `_RETENTION_CARRY` is still missed. A denial built from a verb the
# list below does not hold is still missed WHEN IT NAMES NO PLACE --
# where it names one, the place half reads it whatever the verb, which is
# the half review item P3-V10-F1 bought and
# `test_the_verb_half_is_a_list_and_this_is_its_residue` measures. The
# naming half is a composition and not a phrase list, but the value
# NOUNS it composes over are finite, and no finite list is sound.
#
# AND THE THIRD SHAPE, WHICH IS WHY THIS FAMILY WAS WRONG TWICE MORE
# (review item P3-V11-F1; plan amendment A-P3-43). Everything above
# models a denial as "the thing is not somewhere". A denial of retention
# is also written the other way round -- AS A REDUCTION, saying what IS
# kept and letting the reader work out what is not:
#
#     A value you typed is kept only as a count, not which value it was.
#     The description records how many values were declared, and never
#       the person's own text.
#     A version 5 description keeps how many, never which.
#
# Not one of those says a thing is nowhere. Each says the description
# holds a QUANTITY where the person gave a VALUE, and the false part is
# the reader's own inference: that the identity went. The first of them
# uses this family's own listed verb, in one statement, with an existing
# value noun -- so it is none of the four residues stated above, and the
# guard reported nothing about it. The model was wrong, not short.
#
# THE MODEL THAT REPLACES IT. A retention claim has three constituents:
# the PLACE the thing would stand in, the ACT of putting it there or
# taking it away, and the OBJECT -- the value, and its IDENTITY, which is
# what a description publishes and what a count does not. A denial is a
# NEGATION reaching one of the three, and English marks negation with a
# closed class of function words. So the closedness of each half is
# decided by its constituent and not by anybody's diligence:
#
#   * negation on the PLACE     -- closed on both halves. The negators
#                                  are function words and the places are
#                                  the document's own, derived below.
#   * negation on the IDENTITY  -- closed on both halves. The negators
#                                  are the same function words, and the
#                                  identity of a value is named with the
#                                  value nouns this family already
#                                  composes over and with the four
#                                  pro-forms English has for "which one
#                                  it was". This is the reduction shape's
#                                  recognisable half, and it is new.
#   * negation on the ACT       -- a LIST, because the verbs are open.
#
# AND THE HALF OF THE REDUCTION SHAPE THAT CANNOT BE READ AT ALL, stated
# as the headline of this repair rather than buried. Strip the contrast
# and the sentence carries no negation whatever:
#
#     A value you typed is kept only as a count.
#
# What makes that false is a judgement that "a count" is a REDUCTION of
# what was given, and the words for a reduction are as open a class as
# the verbs: a count, a tally, how many, the number, the total, the
# arithmetic, a summary. Reading the limiter instead of the complement
# does not work either, and that was measured before it was rejected: a
# rule reporting an unscoped `only`, `just`, `merely`, `solely` or
# `alone` in any statement that names the person's own value fires on 29
# statements of this tree today and every one of them is TRUE, because
# a restrictive limiter is what careful writing about a bound is made
# of. So this shape is refused STRUCTURALLY instead, by
# `test_the_sentences_the_product_shows_say_where_your_word_stands`,
# which reads no verb, no negation and no limiter at all: every sentence
# the product SHOWS that names the person's own value must name a place
# out of the producer's publication table. That census is default-deny
# and it is affordable because its corpus is written down as DATA --
# `contract.INVARIANTS` and the command line's own option help -- rather
# than assembled from fragments at run time. Its reach and the reason it
# stops where it does are asserted in that test.
_SPELLING_KIND = profile._SPELLING


def _paths_that_carry_your_text() -> "tuple[tuple[str, ...], ...]":
    """Every path of a description where the table's own text is written.

    Read from `profile.PUBLICATION_RULES`, which is the producer's whole
    statement of what may stand at each path and is refusal-by-default:
    a path missing from it cannot be written at all. The kind
    `_SPELLING` is the one that means an authorized spelling out of the
    person's table, so this is the derived answer to "where can a word
    somebody typed end up".

    Guarantees:

    - Inputs: none; reads the shipped producer's own map.
    - Determinism: sorted; a fixed function of that map.
    - Errors raised: `AssertionError` when `missing_by_source`'s key is
      not among them, because that key is what every sentence in this
      family is checked against and a derivation that quietly lost it
      would make the whole family vacuous.
    - Boundary: nothing is opened and nothing is written.
    """
    found = [
        path
        for path, kind in profile.PUBLICATION_RULES.items()
        if kind == _SPELLING_KIND
    ]
    keys = [path for path in found if path[-2:] == ("missing_by_source", "<key>")]
    assert keys, (
        "The producer's publication rules no longer say that a key of a "
        "column's `missing_by_source` is a spelling out of the person's "
        "table. Either the format changed -- in which case every "
        "sentence about what a declared word leaves behind moves in the "
        "same commit, starting with SECURITY.md and contract 5 section "
        "3.2 -- or this derivation broke. Do not replace it with a list."
    )
    return tuple(sorted(found))


def _regions_that_carry_none_of_it() -> "tuple[str, ...]":
    """The top-level blocks of a description that hold no table text.

    The same map, by subtraction. `settings` is here, which is what
    makes "a word of your own is written nowhere in the settings" a true
    sentence and the cure below a derived set rather than an allow-list
    of phrasings somebody liked.
    """
    everything = {path[0] for path in profile.PUBLICATION_RULES if path}
    carrying = {path[0] for path in _paths_that_carry_your_text()}
    clean = tuple(sorted(everything - carrying))
    assert "settings" in clean, (
        "The settings block now carries text out of the person's table. "
        "That is the Phase 1 rule at review item P1-R7-F2 and contract 5 "
        "section 6.6 lowered again, and it cannot be done by editing a "
        "publication rule: every surface that says a word of the "
        "person's own is written nowhere in the settings is false the "
        "moment it is, and this file holds six of them."
    )
    return clean


RETENTION_SURFACES = DEFENCE_SURFACES

# The NOUNS a sentence of this repository uses for the thing somebody
# typed. Finite, and the bound is written down beside the family: what
# makes the naming precise is not the noun but what is ATTACHED to it.
_A_VALUE = r"(?:word|value|spelling|text|marker|characters?)s?"
_VALUE_GAP = r"(?:[a-z0-9'`\"()-]+ ){0,3}"

# HOW ENGLISH MARKS A NEGATION, which is the one class in this whole
# family that is closed by the language rather than by anybody's care.
# Every half below composes over it: what differs between the halves is
# WHICH constituent of the claim the negation is reaching, and that is
# what decides whether the half is closed or is a sample.
_A_NEGATOR = (
    r"(?:not|never|nor|no|none of|nothing of|rather than|instead of)"
)
_JUST_THE_ONE = r"(?:the |a |any |its |their |your |which )?"

# NAMING BY POSSESSION: the value noun tied to whoever typed it. Both
# orders, because this repository writes both -- "a word of your own"
# and "your own word" -- and the third form is the verb rather than the
# pronoun, "a value you typed".
_YOURS = (
    (
        rf"\b{_A_VALUE} {_VALUE_GAP}?of (?:your|their|his|her|the person's|"
        rf"somebody's|someone's|a person's|the user's|nobody's) own\b"
    ),
    (
        rf"\b(?:your|their|the person's|somebody's|a person's) own "
        rf"{_VALUE_GAP}?{_A_VALUE}\b"
    ),
    (
        rf"\b{_A_VALUE} {_VALUE_GAP}?(?:you|somebody|someone|a person|they|"
        rf"the person) (?:typed|named|wrote|type|name)\b"
    ),
    rf"\bthe {_A_VALUE} themselves\b",
    rf"\b{_A_VALUE} that is not on (?:synthtwin's|this package's|our) list\b",
    rf"\b{_A_VALUE} which is nobody's\b",
)

# NAMING BY EXCLUSION: the value noun tied to being outside synthtwin's
# own list. This is how the contract and the security document named it,
# and it is the form a reader of a specification meets first.
_NOT_OURS = (
    (
        rf"\b{_A_VALUE} {_VALUE_GAP}?(?:outside|not a member of|not one of|"
        rf"not on)\b"
    ),
    rf"\b{_A_VALUE} that is neither\b",
    rf"\bany other {_A_VALUE}\b",
    rf"\bno other {_A_VALUE}\b",
)

# NAMING BY THE CONTRAST ITSELF (review item P3-V11-F1). "A version 5
# description keeps how many, never which" names the person's value with
# no value noun at all: the pair `how many` / `which` IS the naming,
# because a quantity contrasted with an identity has nothing else it can
# be about here. This is the naming half's answer to the reduction shape,
# and it is written as a composition over the same closed negator class
# rather than as a phrase somebody liked -- the second sentence review
# item P3-V11-F1 found was invisible to the family for this reason and
# not for the denial's.
#
# IT IS TIED TO A DECLARATION, and that bound is the whole of its
# soundness. A quantity contrasted with an identity is an ordinary and
# TRUE thing to say about the other reductions this format publishes --
# "how often things repeat, never which things", "how many cells the
# pooled style covered and never which form they took" -- and a naming
# rule that read those would be reporting sentences about numeric styles
# and repeat counts in a family about declared values. So the contrast
# names the person's value only where the sentence also says that a
# DECLARATION is what is being counted, in the words the product itself
# uses for one.
_HOW_MANY = r"\bhow (?:many|often|much)\b"
_A_DECLARATION = (
    r"(?:\bdeclar(?:ed|ation|ations)\b|--missing-value|--keep-value"
    r"|\b(?:you|somebody|someone|a person|they|the person) "
    r"(?:typed|named|wrote)\b)"
)
_NAMED_BY_THE_CONTRAST = (
    rf"{_HOW_MANY}[^.;]{{0,80}}\b{_A_NEGATOR} {_JUST_THE_ONE}which\b",
    rf"\b{_A_NEGATOR} {_JUST_THE_ONE}which\b[^.;]{{0,80}}{_HOW_MANY}",
)

# THE DENIAL, AND IT HAS TWO SHAPES THAT ARE NOT ALIKE (review item
# P3-V10-F1). A denial is one claim -- that the person's word is not
# somewhere -- and English builds that claim two ways. Only one of the
# two can be recognised without a list of anybody's verbs, and the
# difference between them is where the negation sits.
#
# SHAPE ONE: THE NEGATION SITS ON THE PLACE, and the verb is then
# carrying nothing. "The document holds it nowhere." "It goes nowhere."
# "No copy of the file has it." "It is not in the summary." `nowhere` IS
# a negation and a place in one token; `no` and `not` in the others sit
# directly on a place a description has. Read that way the claim is
# complete without the verb, so a rule for this shape catches EVERY
# verb, including the ones nobody has written yet. Both halves of it are
# closed: English negation is a handful of function words, and the
# places are the document's own, derived below from the producer.
#
# THIS IS THE HALF THE SHIPPED GUARD DID NOT HAVE, and the sentence it
# missed was in the governing contract. Version 5's worked example said
# the person typed a word of their own and that the document held it
# nowhere -- a plain transitive sentence, verb first, pronoun in the
# middle. Of the eleven marks in the retired set, ten named a verb; the
# one that also names a place spells the place AFTER the verb, so it
# reads "written nowhere" and "recorded nowhere" and not the ordinary
# order, and the eleventh, `nowhere at all`, needs those two extra
# words. So the one document an institution's reviewer opens first
# carried the exact false assurance this family exists to refuse, and
# the family reported nothing, because it was reading for verbs.
#
# SHAPE TWO: THE NEGATION SITS ON THE VERB AND NO PLACE IS NAMED AT
# ALL. "It is never written." "Any marker you type is never stored."
# "Your own word is discarded." Here the verb is the whole claim, and
# English has no closed list of verbs for putting a thing somewhere or
# taking it away again -- write, record, keep, store, publish, retain,
# save, preserve, omit, exclude, discard, drop, strip, redact, scrub,
# purge, and as many more as somebody writing a sentence next year
# reaches for. THE SECOND HALF IS THEREFORE A LIST, A LIST IS A SAMPLE,
# AND THE RESIDUE IS REAL: a denial built from a verb this list does
# not hold, naming no place at all, is missed.
#
# THE RESIDUE IS STATED AT ITS SIZE rather than left for the next round,
# by `test_the_verb_half_is_a_list_and_this_is_its_residue`, which
# misses one invented verb on purpose and then catches that same verb
# three times over the moment a place is attached to it. That is the
# boundary between the two shapes drawn where it actually falls, and a
# later rule that closes any of it has to move that test, in the open.
_A_PAGE = (
    r"(?:files?|documents?|descriptions?|profiles?|pages?|summary|reports?)"
)
_THE_PAGE = r"(?:the|this|that|every|either|both|these|those)"

# SHAPE ONE. No verb appears in any of these.
_NO_PLACE_FOR_IT = (
    r"\bnowhere\b",
    r"\b(?:not|never|nor) anywhere\b",
    r"\banywhere at all\b",
    rf"\b(?:in|into|inside|within) (?:no|none of the) {_A_PAGE}\b",
    rf"\bno (?:part|copy|trace) of {_THE_PAGE} {_A_PAGE}\b",
    rf"\bnot (?:in|into|inside|within) {_THE_PAGE} {_A_PAGE}\b",
    rf"\b(?:out of|outside) {_THE_PAGE} {_A_PAGE}\b",
)

# SHAPE TWO, and this tuple is the sample the paragraph above admits to
# being. Everything this repository has actually written, the four
# wordings review item P3-V10-F1 named as missing, and the removal verbs
# beside them. Adding a verb here is ordinary maintenance; believing the
# tuple is complete is the mistake it is written to prevent.
_NOT_KEPT = (
    (
        r"\bnever (?:written|recorded|kept|stored|published|retained|"
        r"carried|carries|saved|preserved)\b"
    ),
    (
        r"\b(?:is|are) not (?:written|recorded|kept|stored|published|"
        r"retained|saved|preserved)\b"
    ),
    r"\bwill not keep\b",
    r"\bdoes not keep\b",
    r"\bnot retained\b",
    r"\bkeeps none\b",
    r"\brecords nothing\b",
    r"\bno character\b[^.;]{0,60}\breaches\b",
    (
        r"\b(?:omitted|excluded|discarded|redacted|scrubbed|purged|"
        r"thrown away)\b"
    ),
    (
        r"\b(?:left out of|dropped from|removed from|deleted from|"
        r"stripped from|stripped out of)\b"
    ),
    rf"\b(?:absent|missing) from {_THE_PAGE} {_A_PAGE}\b",
)

# SHAPE THREE: THE NEGATION SITS ON THE OBJECT'S IDENTITY, and the claim
# is a REDUCTION -- what is kept is a quantity, and which value it was is
# denied (review item P3-V11-F1). Both halves are closed.
#
# The negators are the same function words English builds every other
# negation out of. The identity of a value is named two ways and no
# more: with one of the value nouns this family already composes over,
# marked as the thing ITSELF; or with the pro-form English uses when the
# identity is the question -- `which`, `which value`, `what value`, `what
# it was`. A count answers "how many"; these answer "which", and a
# sentence that negates one of them is denying exactly the thing a
# `missing_by_source` key carries.
#
# NO VERB IS READ HERE, and no word for a reduction either. "Kept only
# as a count, not which value it was" is caught by `not which value`,
# and would be caught the same way if it said hoarded, banked or
# jettisoned, and if it said a tally, a headcount or the arithmetic.
_THE_IDENTITY = (
    r"which(?: one)?\b",
    rf"which {_A_VALUE}\b",
    rf"what {_A_VALUE}\b",
    r"what it was\b",
    r"what they were\b",
    rf"{_A_VALUE} (?:itself|themselves)\b",
)

# AND THE VALUE ITSELF, negated in the same seat. "…and never the
# person's own text" is the same claim as "…and never which value it
# was", written with the value named instead of pointed at, and it is
# the sentence review item P3-V11-F1 found in the loader's own rule
# table. The naming used here is POSSESSION only -- `_YOURS`, not
# `_NOT_OURS` -- and that is a measured bound, not a preference: naming
# by exclusion reads "no word can take it outside that band", which is
# a sentence about a random draw in three modules of this tree and
# about nothing this family governs.
_KEPT_ONLY_AS = tuple(
    rf"\b{_A_NEGATOR} {_JUST_THE_ONE}{mark}" for mark in _THE_IDENTITY
) + tuple(
    rf"\b{_A_NEGATOR} {_JUST_THE_ONE}(?:{mark[2:]})"
    if mark.startswith(r"\b")
    else rf"\b{_A_NEGATOR} {_JUST_THE_ONE}(?:{mark})"
    for mark in _YOURS
)

# Which of the two reported a denial, carried through the report so a
# maintainer reading a failure knows whether the guard understood the
# sentence or merely recognised a word in it -- and so the floor below
# can assert WHICH half catches each of its cases. A case that claims to
# be caught structurally and is in fact caught by a verb in the list is
# the defect P3-V10-F1 found in this file's own battery.
_BY_THE_PLACE = "the place half, which reads no verb"
_BY_THE_VERB = "the verb half, which is a list"
_BY_THE_REDUCTION = "the identity half, which reads no verb and no limiter"

# The two limits of contract 5 section 7, which are normative, measured
# and not defects: a spelling fewer rows than the floor wrote is pooled
# unnamed, and a column that publishes no value of the table publishes
# an empty source map whatever made its cells absent. A denial scoped to
# either is true and must stay sayable. `free text` alone is NOT one of
# them, deliberately: the sentence this family was written to catch ends
# "can never be a name, a code, a diagnosis or a free-text answer", and
# a looser mark cured the very sentence it was hunting.
_STATED_LIMITS = (
    r"\bbelow the floor\b",
    r"\bfewer than the floor\b",
    r"\bpooled\b",
    r"\bpublishes no value\b",
    r"\bpublishing nothing\b",
    r"\bnothing-publishing\b",
    r"\bfree[- ]text column\b",
    r"\bcolumn that publishes nothing\b",
)


def _clean_places() -> "tuple[str, ...]":
    """Where a denial may be scoped to, derived plus the stated limits.

    The document regions come from the publication rules, so this set
    tracks the format. The list-level names beside them are the two
    fields contract 5 section 6.2 adds, which are inside `settings` and
    are how the contract itself writes the scope.
    """
    regions = tuple(rf"\b{name}\b" for name in _regions_that_carry_none_of_it())
    return (
        regions
        + (
            r"\bthese (?:two )?lists\b",
            r"\beither list\b",
            r"\bneither list\b",
            r"\bthis block\b",
            r"\bthat block\b",
            r"\bthis record\b",
            r"\bthrough these\b",
        )
        + _STATED_LIMITS
    )


# Where one clause ends and the next begins. The scope has to stand in
# the denial's OWN clause, and the two lists differ on purpose: a comma
# or a colon OPENS a clause that a scope may sit in, while only a
# joining word CLOSES the reach forward, because "written nowhere in the
# settings" and "recorded nowhere, in the settings block" are both one
# claim and "is never written, and the settings hold counts" is two.
_CLAUSE_OPENS = (", ", " and ", " but ", " though ", " while ", " yet ",
                 "; ", ": ")
_CLAUSE_CLOSES = (" and ", " but ", " though ", " while ", " yet ", "; ")
_SCOPE_REACH = 80
_RETENTION_CARRY = 200


def _scope_of(sentence: str, found: "re.Match[str]") -> "str | None":
    """The place this denial is scoped to, or None where it names none."""
    opened = 0
    for mark in _CLAUSE_OPENS:
        at = sentence.rfind(mark, 0, found.start())
        if at != -1 and at + len(mark) > opened:
            opened = at + len(mark)
    closed = len(sentence)
    for mark in _CLAUSE_CLOSES:
        at = sentence.find(mark, found.end())
        if at != -1 and at < closed:
            closed = at
    clause = sentence[opened : min(closed, found.end() + _SCOPE_REACH)]
    for mark in _clean_places():
        if re.search(mark, clause) is not None:
            return mark
    return None


def _the_three_halves() -> "tuple[tuple[str, tuple[str, ...]], ...]":
    """The three constituents a negation can reach, and their marks.

    One place, so that a half added here is a half every check in this
    family gains and a red check can take one away. The order is the
    order a maintainer should read them in: the two that are closed
    first, and the list last.
    """
    return (
        (_BY_THE_PLACE, _NO_PLACE_FOR_IT),
        (_BY_THE_REDUCTION, _KEPT_ONLY_AS),
        (_BY_THE_VERB, _NOT_KEPT),
    )


def _unscoped_denials_in(sentence: str) -> "list[tuple[str, str]]":
    """Every denial in one statement that names no place it holds in.

    Each is returned with the half that reported it, because the two
    are not worth the same: the place half read the claim, and the verb
    half recognised a word somebody happened to use.
    """
    loose: list[tuple[str, str]] = []
    for half, marks in _the_three_halves():
        for mark in marks:
            for found in re.finditer(mark, sentence):
                if _scope_of(sentence, found) is None:
                    loose.append((found.group(0), half))
    return loose


def _names_your_word(sentence: str) -> "str | None":
    """How this sentence names the value the person typed, or None.

    Three routes, and the third carries a bound the other two do not:
    a quantity contrasted with an identity names the person's value only
    where the sentence also says a DECLARATION is what is counted. Every
    other reduction this format publishes -- pooled numeric styles,
    repeat counts -- is written the same way and is true, so the bound
    is what keeps this route from reporting them (review item
    P3-V11-F1).
    """
    for mark in _YOURS + _NOT_OURS:
        if re.search(mark, sentence) is not None:
            return mark
    if re.search(_A_DECLARATION, sentence) is None:
        return None
    for mark in _NAMED_BY_THE_CONTRAST:
        if re.search(mark, sentence) is not None:
            return mark
    return None


def _denies_retention(text: str) -> "list[tuple[str, str, str, str]]":
    """Every sentence of one surface that denies what version 5 keeps.

    Returns the sentence, the wording that named the person's own typed
    value, the denial left without a scope, and which of the two halves
    above reported it -- so a failure message shows a maintainer which
    two collided rather than telling them a document is wrong somewhere,
    and so a check on this function can hold it to HOW it recognised a
    sentence and not merely to whether it did.

    Guarantees:

    - Inputs: one surface's text, lowercased and space-collapsed by
      `_text`.
    - Determinism: a fixed function of that text and of the derived
      clean places; nothing is read here.
    - Errors raised: none.
    - Boundary: pure text; opens nothing.
    """
    found: list[tuple[str, str, str, str]] = []
    statements = _STATEMENT_END.split(text)
    for index, sentence in enumerate(statements):
        named = _names_your_word(sentence)
        if named is None:
            continue
        loose = _unscoped_denials_in(sentence)
        said = sentence
        if not loose:
            # The denial may be in the next statement, on the fourth
            # family's finding. It is carried only while no NEW naming
            # has begun, so two unrelated claims cannot be read as one.
            reached = 0
            for following in statements[index + 1 :]:
                reached = reached + len(following)
                if reached > _RETENTION_CARRY:
                    break
                if _names_your_word(following) is not None:
                    break
                carried = _unscoped_denials_in(following)
                if carried:
                    loose = carried
                    said = f"{sentence}; {following}"
                    break
        if loose:
            denied, half = loose[0]
            found.append((said, named, denied, half))
    return found


# THE RED CHECKS FOR THIS FAMILY, each putting back in memory exactly
# what stood before the repair:
#
#   REINSTATE=A-P3-31          the summary's retired closing sentence,
#                              word for word as it shipped, added to
#                              every surface -- reds the ban;
#   REINSTATE=A-P3-31-silent   every true retention sentence deleted
#                              instead of written, which is what a ban
#                              satisfied by silence looks like -- reds
#                              the positive half;
#   REINSTATE=A-P3-31-loose    the cure drawn as a whole STATEMENT
#                              rather than the denial's own clause,
#                              which is the rule a reviewer would call
#                              thorough and which reads the scoped half
#                              of the summary's own sentence and passes
#                              the unscoped half -- reds the floor;
#   REINSTATE=A-P3-31-withheld the derivation made to claim the
#                              description keeps none of it -- reds the
#                              run-driven measurement;
#   REINSTATE=A-P3-41          the governing contract's retired worked
#                              example, word for word as it shipped,
#                              added to every surface -- reds the ban on
#                              the sentence review item P3-V10-F1 found;
#   REINSTATE=A-P3-41-verbs    the denial set as it shipped, which is
#                              the verb half alone -- reds every case of
#                              the floor that the place half is what
#                              catches, and reds the residue check's
#                              second half, where an invented verb is
#                              caught three ways over by its place.
_THE_RETIRED_CLOSE = (
    " for any other word you typed, keep a note of the command you ran; "
    "synthtwin will not keep one for you."
)

# The contract's worked example as it stood at review item P3-V10-F1: a
# researcher reading section 6.2 was told they typed their own word and
# that the document held it nowhere, in the document an institution's
# reviewer opens first.
_THE_RETIRED_EXAMPLE = (
    " - the person typed `wombat`, which is their own word; the document "
    "holds it nowhere, and `n_declared` counts it."
)

# The denial set as it shipped -- one tuple, every entry a verb, and the
# place spelled only after the verb. This is what let the sentence above
# through.
# The three sentences the census was built to refuse, in the wordings
# that shipped at review item P3-V11-F1 -- the loader's own rule for
# `values_recorded`, and the two option helps that a person reads before
# deciding what to type. Every one of them speaks about a declared value
# and names no place, and not one of them contains a denial the wording
# guard of that day could see.
_THE_SENTENCES_THAT_SHIPPED = (
    (
        "contract invariant C5-S7, as it shipped",
        (
            "the description records how many values were declared, and "
            "never the person's own text -- only which of synthtwin's "
            "own published words were among them"
        ),
    ),
    (
        "the help for --keep-value, as it shipped",
        (
            "The profile records how many different values you named, "
            "the rule that matched them, and -- where what you named is "
            "one of synthtwin's own words for 'no value', such as NA or "
            "-999 -- which of those words it was."
        ),
    ),
    (
        "the help for --missing-value, as it shipped",
        (
            "The profile also records how many different values you "
            "named, the rule that matched them, and -- where what you "
            "named is one of synthtwin's own words for 'no value' -- "
            "which of those words it was."
        ),
    ),
)

_THE_SHIPPED_DENIALS = (
    r"\b(?:written|recorded|held|kept|stored|published) nowhere\b",
    r"\bnowhere at all\b",
    r"\bnever (?:written|recorded|kept|stored|published)\b",
    r"\bis not (?:written|recorded|kept|stored)\b",
    r"\bare not (?:written|recorded|kept|stored)\b",
    r"\bwill not keep\b",
    r"\bdoes not keep\b",
    r"\bnot retained\b",
    r"\bkeeps none\b",
    r"\brecords nothing\b",
    r"\bno character\b[^.;]{0,60}\breaches\b",
)


@pytest.fixture(autouse=True)
def _retention_reinstated(monkeypatch: pytest.MonkeyPatch) -> None:
    """The red checks above, driven from the environment."""
    asked = os.environ.get("REINSTATE")
    if asked == "A-P3-31":
        kept = _text

        def _with_the_denial(relative: str) -> str:
            return kept(relative) + _THE_RETIRED_CLOSE

        monkeypatch.setitem(globals(), "_text", _with_the_denial)
    if asked == "A-P3-31-silent":
        kept_text = _text

        def _without_the_truth(relative: str) -> str:
            # Only the first mark's wordings are deleted. The second
            # mark is the FLOOR, which four other families in this file
            # also look for, and a red check that reds somebody else's
            # test proves nothing about its own.
            said = kept_text(relative)
            for pattern in _KEPT_MARKS[0][1]:
                said = re.sub(pattern, "(the sentence, deleted)", said)
            return said

        monkeypatch.setitem(globals(), "_text", _without_the_truth)
    if asked == "A-P3-31-loose":

        def _whole_statement(
            sentence: str, found: "re.Match[str]"
        ) -> "str | None":
            for mark in _clean_places():
                if re.search(mark, sentence) is not None:
                    return mark
            return None

        monkeypatch.setitem(globals(), "_scope_of", _whole_statement)
    if asked == "A-P3-41":
        kept_example = _text

        def _with_the_example(relative: str) -> str:
            return kept_example(relative) + _THE_RETIRED_EXAMPLE

        monkeypatch.setitem(globals(), "_text", _with_the_example)
    if asked == "A-P3-41-verbs":
        monkeypatch.setitem(globals(), "_NO_PLACE_FOR_IT", ())
        monkeypatch.setitem(globals(), "_KEPT_ONLY_AS", ())
        monkeypatch.setitem(globals(), "_NOT_KEPT", _THE_SHIPPED_DENIALS)
    if asked == "P3-V11-F1":
        # The guard's model as it stood at review item P3-V11-F1: a
        # denial is a negation reaching the PLACE or the ACT, and the
        # OBJECT is not a seat a negation can sit in. Both halves of
        # that model are put back -- the third set of marks and the
        # naming route that reads a quantity against an identity.
        monkeypatch.setitem(globals(), "_KEPT_ONLY_AS", ())
        monkeypatch.setitem(globals(), "_NAMED_BY_THE_CONTRAST", ())
    if asked == "P3-V11-F1-census":
        # The corpus as it stood at the finding: the loader's rule table
        # and the two option helps in the wordings that shipped, word
        # for word. Written out rather than described, so the census is
        # run against the sentences it was built to refuse rather than
        # against an empty corpus -- a red check that empties a
        # default-deny rule proves nothing about it.
        kept = _the_products_own_sentences

        def _as_they_shipped() -> "list[tuple[str, str]]":
            return list(kept()) + list(_THE_SENTENCES_THAT_SHIPPED)

        monkeypatch.setitem(
            globals(), "_the_products_own_sentences", _as_they_shipped
        )
    if asked == "P3-V12-F1":
        # The census's own predicate as it stood at review item
        # P3-V12-F1: a place MENTIONED anywhere in the sentence
        # answered, whatever the sentence then said about it.
        monkeypatch.setitem(
            globals(), "_speaks_falsely_of_the_place", _a_place_was_mentioned
        )
    if asked == "P3-V12-F1-census":
        # The two sentences the reviewer walked the shipped rule through,
        # put where a person would meet them: in the corpus itself.
        kept_corpus = _the_products_own_sentences

        def _with_the_bypasses() -> "list[tuple[str, str]]":
            walked = [
                (what, said)
                for what, said, _why in _THE_SENTENCES_THAT_ANSWERED_WITH_A_PLACE
            ]
            return list(kept_corpus()) + walked

        monkeypatch.setitem(
            globals(), "_the_products_own_sentences", _with_the_bypasses
        )
    if asked == "P3-V12-F1-corpus":
        # The corpus as it stood: two tables, and the refusals the
        # loader assembles left outside it.

        def _two_tables_only() -> "list[tuple[str, str]]":
            return []

        monkeypatch.setitem(
            globals(),
            "_THE_PRODUCTS_OWN_TABLES",
            ("the loader's rule table", "the option help"),
        )
        monkeypatch.setitem(
            globals(), "_the_refusals_the_loader_assembles", _two_tables_only
        )
    if asked == "P3-V12-F1-clause":
        # A reduction written into one clause of one refusal, which is
        # the route the corpus gained this round: the clause is written
        # down at a call site, the sentence a person reads is assembled
        # from it, and nothing else in this file would report it.
        kept_refusals = _the_refusals_the_loader_assembles

        def _with_a_reduction_in_a_clause() -> "list[tuple[str, str]]":
            written = errors.profile_invariant_broken(
                "C5-S7",
                contract.INVARIANTS["C5-S7"],
                "in the block of rules that produced the description",
                "the record says the declared values were kept",
                _A_REDUCTION_WITH_NO_NEGATION,
            )
            return list(kept_refusals()) + [
                ("the refusal a maintainer would have written", written)
            ]

        monkeypatch.setitem(
            globals(),
            "_the_refusals_the_loader_assembles",
            _with_a_reduction_in_a_clause,
        )


def test_no_surface_denies_what_the_description_keeps_of_your_words() -> None:
    """No surface says a word you typed is written nowhere, unscoped.

    The negative half of the sixth family. A surface may say -- and six
    of them must say -- that the settings block carries no spelling of
    the person's own, that a spelling the floor pooled is named nowhere,
    and that a column publishing no value of the table publishes none of
    it either. What no surface may do is make the denial without saying
    where it holds, because the place it does NOT hold is the ordinary
    one: a column of numbers, at the default floor, publishing the
    marker somebody typed.
    """
    offenders: list[str] = []
    for relative in RETENTION_SURFACES:
        for sentence, named, denied, half in _denies_retention(_text(relative)):
            offenders.append(
                f"{relative}: {named!r} denied by {denied!r} -- reported by "
                f"{half}\n      {sentence[:300]}"
            )
    assert not offenders, (
        "These surfaces deny that synthtwin keeps a word the person "
        "typed, without saying where the denial holds:\n  "
        + "\n  ".join(offenders)
        + "\n\nWhat is true: a value named with --missing-value is "
        "counted absent, and its spelling is then written into that "
        "column's `missing_by_source` character for character, wherever "
        "at least `small_cell_floor` rows share it and the column "
        "publishes any values at all (contract 5 section 3.2, way 4). "
        "So a description can carry a diagnosis code or an identifier. "
        "What is ALSO true, and is what these sentences were reaching "
        "for: the settings block carries no spelling of the person's "
        "own, a spelling the floor pooled is named nowhere, and a "
        "column that publishes no value of the table publishes none "
        "either way. Say which of those you mean, in the same clause as "
        "the denial. Do not add a surface to an exception list: that is "
        "how every ban in this file rots."
    )


# Where the true statement has to be MADE, and not merely left unsaid.
# Deleting a denial satisfies the ban above and leaves a reader with no
# idea that their own word travels, which is the worse of the two
# failures: the summary's retired sentence was at least visible.
#
# The six are the surfaces a person meets the decision on: the front
# page they read before installing, the security document an institution
# weighs, the contract that governs the format, the command line that
# takes the word, the page printed beside the description, and the
# producer that writes it.
KEPT_BEARING = (
    "README.md",
    "SECURITY.md",
    "docs/spec/profile-contract-v5.md",
    "src/synthtwin/cli.py",
    "src/synthtwin/summary.py",
    "src/synthtwin/profile.py",
)

# The marks of the true statement. Each entry is a tuple of accepted
# phrasings, so a surface may speak in its own register -- the contract
# and the producer normatively, the front page and the command line in
# the words a researcher deciding what to type will read.
_KEPT_MARKS = (
    (
        "that the word itself is written into the description",
        (
            r"the word itself is written into",
            r"the word itself is then written into",
            r"word itself is written into the description",
            r"puts that word into a column's `missing_by_source`",
            r"its spelling reaching\s+`missing_by_source`",
            r"spelling goes into that column's `missing_by_source`",
            r"is written into the description",
            r"these words are written into it",
            r"reaches `missing_by_source`",
            r"reaches its column's\s+`missing_by_source`",
            r"does reach\s+`missing_by_source`",
        ),
    ),
    (
        "the bound it is written under -- the floor and the column",
        (
            r"small_cell_floor",
            r"smallest-group",
            r"rows share (?:that spelling|it)",
            r"rows hold it",
            r"floor permits",
            r"under the ordinary floor",
        ),
    ),
)


def test_the_surfaces_that_decide_say_the_word_itself_travels() -> None:
    """The positive half, so that deleting the denial is not a pass.

    A ban on a false assurance is satisfied by a repository that says
    nothing about what a declared word leaves behind, and silence is
    what put review item P3-V9-F1 in front of a researcher: the page
    printed the word and explained the settings.
    """
    missing: list[str] = []
    for relative in KEPT_BEARING:
        said = _text(relative)
        for what, patterns in _KEPT_MARKS:
            if not any(re.search(mark, said) for mark in patterns):
                missing.append(f"{relative}: does not say {what}")
    assert not missing, (
        "These surfaces decide whether a person types a word after "
        "--missing-value, or whether a file may travel, and they do not "
        "say what the description keeps of it:\n  " + "\n  ".join(missing)
        + "\n\nSay that the word itself is written into the column's "
        "description, and say the bound it is written under: at least "
        "`small_cell_floor` rows sharing the spelling, on a column that "
        "publishes values at all."
    )


def test_the_producer_writes_the_word_the_person_typed(
    tmp_path: pathlib.Path,
) -> None:
    """The measurement, because a permitted spelling is not a written one.

    The derivation above reads what the publication rules ALLOW. This
    runs the producer over a table holding a declared marker and reads
    the marker back out of both files a `profile` run writes, so that a
    format which permitted the spelling while the producer stopped
    writing it could not leave the sentences above checked against a
    permission nothing exercises.

    It also measures the other half, which is what makes the scoped
    sentences of six surfaces true: the marker is NOT in the settings
    block.
    """
    floor = taxonomy.Settings().small_cell_floor
    marker = "a-word-no-vocabulary-holds"
    values = [str(row) for row in range(60)] + [marker] * (floor + 1)
    path = fixtures.write(
        tmp_path, "table.csv", fixtures.single_column_table("reading", values)
    )
    table = reading.read_table(str(path))
    document = profile.build_document(
        table,
        taxonomy.Settings(declared_missing_values=(marker,)),
        [],
    )
    written = profile.serialize(document)
    said = summary.render(document, "read as utf-8")
    if os.environ.get("REINSTATE") == "A-P3-31-withheld":
        # The red check: a producer that stopped writing the spelling.
        # Every sentence this family requires of six surfaces would then
        # be describing a document nobody gets, and the ban would be
        # forbidding a true denial.
        written = written.replace(marker, "(withheld)")
        said = said.replace(marker, "(withheld)")
    assert marker in written, (
        "The producer no longer writes a declared marker into the "
        "description. If that is deliberate, it is a format change: "
        "contract 5 section 3.2 way 4 and every sentence the sixth "
        "family requires of `KEPT_BEARING` move in the same commit, and "
        "the denials those six surfaces scope become sayable again."
    )
    assert marker in said, (
        "The description holds the declared marker and the "
        "plain-language summary beside it does not name it. A person is "
        "handed one of the five files, not the set, and the one they "
        "can read has to say which of their own words it carries."
    )
    settings = written[written.index('"settings"') :]
    settings = settings[: settings.index('"source"')]
    assert marker not in settings, (
        "The settings block now carries a spelling of the person's own. "
        "That is the Phase 1 rule at review item P1-R7-F2, and six "
        "surfaces say in as many words that it does not."
    )
    assert summary.words_of_your_own(document) == [(marker, "reading", floor + 1)], (
        summary.words_of_your_own(document)
    )


# THE FLOOR: every wording of this denial that is known, with the half
# that has to catch each. Not a sample of them (review item P3-V10-F1).
#
# WHAT WAS WRONG WITH THE LIST THIS REPLACES. It called one of its own
# cases "a paraphrase using none of those verbs" and then wrote
# `stored`, which was the fifth entry of the verb list it claimed to
# walk around. So the one case that said it proved the guard generalises
# proved the opposite of nothing: it exercised the list. That is why
# every case now carries the half that must report it, and why the check
# asserts the half and not merely that something was reported -- a case
# that claims the place half and is caught by a verb is exactly the
# false assurance this file exists to refuse, and it now fails.
#
# WHAT IS HERE. The five sentences that shipped, in their own wordings;
# the four the plan's own text describes -- the possessive form, the
# split across a semicolon, the split across a full stop, and a
# paraphrase now labelled as what it is; the contract sentence review
# item P3-V10-F1 found, verb first and place last; the four wordings
# that review named as missed -- omitted, excluded, discarded, left out;
# and three that carry a verb no list holds, to show the place half
# reading a claim rather than recognising a word.
DENIALS_THAT_SHIPPED = (
    (
        "the summary's closing sentence, split across a semicolon",
        (
            "For any other word you typed, keep a note of the command "
            "you ran; synthtwin will not keep one for you."
        ),
        _BY_THE_VERB,
    ),
    (
        "the summary's opening claim, scoped and then unscoped in one breath",
        (
            "A word of YOUR OWN is not written into its settings, and it "
            "is not written here."
        ),
        _BY_THE_VERB,
    ),
    (
        "the security document's reason clause",
        (
            "The word guessed at can never be a name, a code, a diagnosis "
            "or a free-text answer, because a value outside that list is "
            "written nowhere at all."
        ),
        _BY_THE_PLACE,
    ),
    (
        "the security document's what-is-not-relaxed",
        (
            "A declared value that is not one of the thirteen is still "
            "recorded nowhere."
        ),
        _BY_THE_PLACE,
    ),
    (
        "the contract's own invariant",
        "A declared value that is neither is written nowhere.",
        _BY_THE_PLACE,
    ),
    (
        "the contract's what-a-reader-can-infer",
        (
            "It can never be a name, a code, a diagnosis or a free-text "
            "answer, because a value outside the list is never written."
        ),
        _BY_THE_VERB,
    ),
    (
        "the plan's description of its own test",
        (
            "It checks that a word which is nobody's but the person's is "
            "written nowhere."
        ),
        _BY_THE_PLACE,
    ),
    (
        # This case used to be labelled "a paraphrase using none of
        # those verbs" and it uses `stored`, which the shipped list held
        # (review item P3-V10-F1). It is kept, because it is a real
        # wording, and it is labelled as what it is. The cases that
        # actually walk around the list are the three at the end.
        "a paraphrase, in a verb the list does hold",
        "Any marker you type is never stored by synthtwin.",
        _BY_THE_VERB,
    ),
    (
        "the denial split across a full stop",
        (
            "You may name a word of your own after --missing-value. It is "
            "never written."
        ),
        _BY_THE_VERB,
    ),
    (
        (
            "the governing contract's worked example, which review item "
            "P3-V10-F1 found -- the verb first and the place last"
        ),
        (
            "The person typed WOMBAT, which is their own word; the "
            "document holds it nowhere, and n_declared counts it."
        ),
        _BY_THE_PLACE,
    ),
    (
        "omitted, which the shipped list did not hold",
        "A value of your own is omitted.",
        _BY_THE_VERB,
    ),
    (
        "excluded, which the shipped list did not hold",
        "The marker you typed is excluded.",
        _BY_THE_VERB,
    ),
    (
        "discarded, which the shipped list did not hold",
        "A word of your own is discarded once the description is built.",
        _BY_THE_VERB,
    ),
    (
        # Deliberately not "left out of the description": that names a
        # place, so the place half reads it and this case would stop
        # measuring the verb it is here for.
        "left out, which the shipped list did not hold",
        "The word you typed is left out of everything synthtwin writes.",
        _BY_THE_VERB,
    ),
    (
        "a verb no list holds, put beyond every place there is",
        "A word of your own is jettisoned, so it ends up nowhere.",
        _BY_THE_PLACE,
    ),
    (
        "a verb no list holds, with the places named one by one",
        "A marker you type is smuggled into none of the files.",
        _BY_THE_PLACE,
    ),
    (
        "a verb no list holds, with the place named by exclusion",
        "The value you typed stays outside the description.",
        _BY_THE_PLACE,
    ),
    # THE REDUCTION SHAPE (review item P3-V11-F1). The first is the
    # sentence review wrote to show the model was wrong -- a listed
    # verb, one statement, an existing value noun, and nothing the
    # stated residues covered. The next two are the two sentences of the
    # loader's own module. The last two carry a verb and a word for a
    # quantity that no list here holds, which is what makes this half a
    # claim about the OBJECT rather than a fourth list.
    (
        "the reduction, contrasted -- what review wrote to show the model",
        "A value you typed is kept only as a count, not which value it was.",
        _BY_THE_REDUCTION,
    ),
    (
        "the loader's own rule table, as it shipped",
        (
            "The description records how many values were declared, and "
            "never the person's own text."
        ),
        _BY_THE_REDUCTION,
    ),
    (
        "the loader's own refusal, as it shipped",
        "A version 5 description keeps how many values were declared, never which.",
        _BY_THE_REDUCTION,
    ),
    (
        "a reduction in a verb no list holds",
        "A word of your own is jettisoned, and never the word itself.",
        _BY_THE_REDUCTION,
    ),
    (
        "a reduction to a quantity no list here names",
        (
            "The description banks a tally of the markers you typed, not "
            "which marker it was."
        ),
        _BY_THE_REDUCTION,
    ),
)


@pytest.mark.parametrize("shape,passage,half", DENIALS_THAT_SHIPPED)
def test_the_sixth_family_would_notice_the_assurance_it_replaced(
    shape: str, passage: str, half: str
) -> None:
    """Each false sentence is one this guard now reports, and by which half.

    Run against `_denies_retention` directly rather than against a file,
    because what is held here is the RULE and not any surface's current
    wording.

    THE HALF IS ASSERTED, AND THAT IS THE POINT OF THIS CHECK. A case
    written to show that the guard reads a claim rather than recognising
    a word proves that only if the place half is what reported it. The
    list this replaced asserted neither, and its one generalisation case
    was being caught by the verb list all along.
    """
    found = _denies_retention(" ".join(passage.lower().split()))
    assert found, (
        f"this sentence denies what the description keeps -- {shape} -- "
        f"and the guard reported nothing:\n  {passage}"
    )
    reported = {caught[3] for caught in found}
    assert half in reported, (
        f"this sentence is reported, but not by the half that has to "
        f"read it -- {shape}.\n  {passage}\n  expected: {half}\n  "
        f"reported by: {sorted(reported)}\n\nA case whose whole purpose "
        f"is to show the guard reading a CLAIM proves nothing if a verb "
        f"in the list is what caught it."
    )


def test_a_scoped_denial_is_read_as_the_true_sentence_it_is() -> None:
    """What the ban must NOT catch, asserted rather than hoped.

    Every sentence below is one this repository needs to be able to
    write, and each is true: the settings block, the two vocabulary
    lists inside it, the floor, and a column that publishes no value of
    the table. A guard that reported these would be turned off within a
    week, and turning it off is how the false sentence comes back.
    """
    permitted = (
        "a word of your own is written nowhere in the settings.",
        "a word of your own is never written into the settings block.",
        (
            "a declared value that is neither reaches neither list, and no "
            "character a person typed reaches the document through these "
            "lists."
        ),
        (
            "a spelling fewer rows than the floor wrote is pooled and "
            "recorded nowhere."
        ),
        (
            "a word the person named on a nothing-publishing column is "
            "recorded nowhere."
        ),
        "on a free-text column the marker a person typed is written nowhere.",
        # The three the widened rule had to be held against: each says
        # its place in the same clause, in one of the new wordings.
        (
            "a word of your own that the floor pooled is left out of the "
            "description."
        ),
        "a word of your own is omitted from the settings block.",
        "below the floor the spelling you typed is in none of the files.",
    )
    caught = [
        sentence
        for sentence in permitted
        if _denies_retention(" ".join(sentence.lower().split()))
    ]
    assert not caught, (
        "The retention ban now catches sentences this repository has to "
        "be able to write, every one of them true:\n  "
        + "\n  ".join(caught)
        + "\n\nNarrow the rule -- never add an exception list."
    )


# One verb no list here holds and no sentence of this repository uses.
# It is deliberately not a synonym anybody would reach for: a synonym
# would be an argument about whether the list should have held it, and
# what is being measured is that the list is a LIST.
_A_VERB_NO_LIST_HOLDS = "a word of your own is jettisoned by the profiler"


def test_the_verb_half_is_a_list_and_this_is_its_residue() -> None:
    """What the guard misses, at its size, and where the miss stops.

    Review item P3-V10-F1 asked whether a denial can be recognised
    structurally rather than by enumerating verbs. Half of it can, and
    that half is asserted everywhere above. This is the other half,
    written down rather than left to be found by the round after next.

    THE RESIDUE. A denial whose negation sits on a verb the list does
    not hold, naming no place at all, is missed. One sentence, asserted
    to be missed, so the residue has a size instead of a hand-wave -- if
    a later rule closes it, this line goes red and somebody says so in
    the open rather than discovering the guard quietly grew.

    WHERE THE MISS STOPS, which is the more useful half of the
    measurement. The same invented verb is caught three times over the
    moment the claim says WHERE: beyond every place, into none of the
    named ones, or outside one of them. So what is missing is not "the
    guard cannot read this verb" but "a claim that says nothing about
    where has only its verb to be recognised by", which is a fact about
    English and not about this file.
    """
    missed = _denies_retention(f"{_A_VERB_NO_LIST_HOLDS}.")
    assert not missed, (
        "The verb half has stopped being a sample -- this sentence is "
        "now caught, and the residue this test records is smaller than "
        f"it says:\n  {_A_VERB_NO_LIST_HOLDS}\n  reported: {missed}\n\n"
        "That is good news and it is a change to what the guard "
        "promises. Say so where the promise is written: the family's "
        "own comment above, amendment A-P3-41 in the plan, and this "
        "test."
    )
    for said in (
        f"{_A_VERB_NO_LIST_HOLDS}, so it ends up nowhere.",
        f"{_A_VERB_NO_LIST_HOLDS} and goes into none of the files.",
        f"{_A_VERB_NO_LIST_HOLDS}, which leaves it outside the description.",
    ):
        caught = _denies_retention(" ".join(said.lower().split()))
        assert caught, (
            "The place half no longer reads a claim whose verb it does "
            f"not know:\n  {said}\n\nThat is the half review item "
            "P3-V10-F1 was closed with, and without it the guard is the "
            "verb list again."
        )
        assert caught[0][3] == _BY_THE_PLACE, (
            f"reported, but by {caught[0][3]!r} rather than by the place "
            f"half:\n  {said}\n\nThe verb in this sentence is one no "
            "list here holds, so a verb-half report means a list grew "
            "and this measurement stopped measuring anything."
        )


def test_the_guard_that_shipped_passed_the_governing_sentence(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """The measurement that made review item P3-V10-F1 blocking.

    Both halves of it are here because both are the finding: the
    sentence was in the governing contract, AND the family written one
    commit earlier to forbid exactly that sentence reported nothing
    about it. A repair that only fixed the contract would leave the
    second half true and the next such sentence unopposed, so the
    shipped denial set is kept as a constant and run against the shipped
    sentence, in this file, forever.
    """
    said = " ".join(_THE_RETIRED_EXAMPLE.lower().split())
    caught = _denies_retention(said)
    assert caught and caught[0][3] == _BY_THE_PLACE, (
        "The contract's own retired worked example is no longer caught, "
        f"or is caught by the wrong half:\n  {said}\n  reported: "
        f"{caught}"
    )
    monkeypatch.setitem(globals(), "_NO_PLACE_FOR_IT", ())
    monkeypatch.setitem(globals(), "_NOT_KEPT", _THE_SHIPPED_DENIALS)
    assert not _denies_retention(said), (
        "The denial set as it shipped now reports this sentence, so the "
        "constant recording what P3-V10-F1 measured has drifted from "
        "what actually shipped. Fix the constant, not this assertion: "
        "it is the evidence that a guard reading for verbs passed an "
        "ordinary transitive denial in the one document an "
        "institution's reviewer opens first."
    )


# THE HALF OF THE REDUCTION SHAPE THAT NO RULE READING WORDS CAN SEE,
# and it is the headline of this repair rather than a footnote to it
# (review item P3-V11-F1; plan amendment A-P3-43).
_A_REDUCTION_WITH_NO_NEGATION = (
    "a value you typed is kept only as a count"
)

# The limiters a rule for that shape would have to fire on, and the
# measurement that killed the idea. Each of these is what precise
# writing about a bound is MADE of, which is why the count below is what
# it is.
_RESTRICTIVE = (
    r"\bonly\b", r"\bjust\b", r"\bmerely\b", r"\bsolely\b", r"\balone\b",
    r"\bnothing but\b", r"\bno more than\b",
)

# Measured on this tree at the commit that wrote this line, over the
# statements of `RETENTION_SURFACES` that name the person's own value.
# It is asserted rather than quoted, so a tree that drifts away from it
# fails here instead of leaving a number in a comment nobody rechecks.
#
# IT IS A FLOOR AND NOT AN EQUALITY, on purpose. The claim it carries is
# that the count is LARGE -- that a limiter rule would have to speak
# about this repository's ordinary careful prose -- and an equality
# would red on every unrelated paragraph anybody writes, which is how a
# measurement becomes a nuisance and then gets deleted. What has to red
# is the count COLLAPSING, because that is the day the limiter rule
# becomes worth having and this residue can close.
_TRUE_SENTENCES_A_LIMITER_RULE_WOULD_REPORT = 28


def test_the_reduction_that_carries_no_negation_cannot_be_read() -> None:
    """THE HEADLINE. A reduction with no contrast is not lexically visible.

    Review item P3-V11-F1 asked whether "we keep only Y of X" can be
    recognised soundly. It SPLITS, and both halves are asserted here so
    that neither is read as the other.

    THE HALF THAT CAN. Where the sentence says which value it was and
    negates that, the negation is a function word and the identity is
    named with the value nouns this family already composes over. That
    half is closed, it is `_KEPT_ONLY_AS`, and every wording of it is in
    the floor above.

    THE HALF THAT CANNOT, asserted as a MISS. Strip the contrast and
    nothing in the sentence is negative at all:

        A value you typed is kept only as a count.

    What makes it false is a judgement that a count is a REDUCTION of
    what was given, and the words for a reduction are as open a class as
    the verbs -- a count, a tally, how many, the total, the arithmetic,
    a summary, and whatever somebody reaches for next year. There is no
    seat for a negation to sit in, so there is nothing for a rule about
    negation to read.

    AND THE ONE ALTERNATIVE IS MEASURED RATHER THAN WAVED AWAY. The only
    other lexical handle is the LIMITER, and a rule reporting an
    unscoped limiter in any statement that names the person's own value
    fires on this tree's own true sentences at the size asserted below.
    A guard that reports two dozen true sentences is a guard somebody
    turns off, and turning it off is how the false sentence comes back.

    SO THE SHAPE IS REFUSED STRUCTURALLY INSTEAD, by
    `test_the_sentences_the_product_shows_say_where_your_word_stands`,
    which reads no verb, no negation and no limiter and would report
    this exact sentence.
    """
    said = f"{_A_REDUCTION_WITH_NO_NEGATION}."
    missed = _denies_retention(said)
    assert not missed, (
        "A reduction carrying no negation is now caught by the wording "
        f"guard:\n  {said}\n  reported: {missed}\n\nThat is a change to "
        "what this family promises and it has to be argued in the open: "
        "say what closed it, and say what it costs on the sentences "
        "`test_a_scoped_denial_is_read_as_the_true_sentence_it_is` "
        "requires this repository to be able to write."
    )
    # ... and the same claim IS caught the moment it says which value,
    # which is what makes the miss a statement about the shape and not
    # about the guard having stopped working.
    contrasted = f"{_A_REDUCTION_WITH_NO_NEGATION}, not which value it was."
    caught = _denies_retention(contrasted)
    assert caught and caught[0][3] == _BY_THE_REDUCTION, (
        "The contrasted half of the reduction shape is no longer read, "
        f"or is read by the wrong half:\n  {contrasted}\n  {caught}"
    )
    # ... and the measurement that rules the limiter out. It counts
    # STATEMENTS and reads no scope, so it measures the same thing under
    # every red check in this file: how much of this tree a rule for the
    # bare reduction would have to speak about.
    would_report = 0
    for relative in RETENTION_SURFACES:
        for sentence in _STATEMENT_END.split(_text(relative)):
            if _names_your_word(sentence) is None:
                continue
            if any(re.search(mark, sentence) for mark in _RESTRICTIVE):
                would_report = would_report + 1
    assert would_report >= _TRUE_SENTENCES_A_LIMITER_RULE_WOULD_REPORT, (
        "The measurement this residue rests on has collapsed: a rule "
        "reporting a restrictive limiter in a statement that names the "
        f"person's own value now fires on {would_report} statements of "
        "this tree, and the floor beside this test says "
        f"{_TRUE_SENTENCES_A_LIMITER_RULE_WOULD_REPORT}. READ them "
        "before touching the floor. If they have genuinely become few, "
        "and each of them is a claim about what a description keeps, "
        "the limiter rule is worth having, this residue can close and "
        "the argument for closing it belongs in the plan. If the "
        "statement splitter or the naming half moved instead, the "
        "measurement is the thing that broke."
    )


# THE STRUCTURAL CENSUS, which is the answer to the half above. Every
# sentence the PRODUCT SHOWS that names the person's own value is
# checked against what the producer's publication table says stands in
# the place that sentence puts it in. It reads no verb, no denial and
# no word for a quantity, so no wording walks around it; what it costs
# is that its corpus has to be enumerable, and that is what fixes its
# reach.
#
# WHAT IT ASKED FIRST, AND WHY THAT WAS NOT A CHECK (review item
# P3-V12-F1). The first census asked whether a sentence NAMED a place
# out of the publication table -- a region carrying none of the
# person's text, or a path carrying it -- and stopped there, on the
# reasoning that what the sentence then said about that place was the
# wording guard's business. But the wording guard cannot read a
# reduction that carries no negation; that is the finding above and it
# has not changed. So "names a place" was the whole of the check, and
# naming a place is not making a true claim about one. Two sentences
# walked straight through, both reproduced against the shipped tree and
# both kept in `_THE_SENTENCES_THAT_ANSWERED_WITH_A_PLACE` below:
#
#     In `missing_by_source`, a value you typed is kept only as a count.
#
# which enters the one place the producer's table says the spelling
# stands in, character for character, and says a count stands there
# instead; and
#
#     The settings block records the rule, and the description keeps
#     only a tally of a value you typed.
#
# which answers with a place standing in a different claim of the same
# sentence, about a different thing.
#
# SO THE PREDICATE IS RE-DERIVED ON THE CLAIM AND THE PLACE TOGETHER,
# and it is derived from the same publication table as before rather
# than from a fourth list of wordings. Three questions, asked of every
# CLAIM -- not of the sentence, because a sentence carries several and
# a place standing in one of them says nothing about the next:
#
#   1. WHERE. A claim that ENTERS no place speaks for the whole
#      description, and the whole description is the one thing about
#      which no denial is true. Entering is not mentioning: `the
#      settings block records the rule` names the settings and puts
#      nothing in them, which is exactly how the second bypass answered
#      for a claim it had nothing to do with. English marks entering
#      with a closed class of function words, the same way it marks
#      negation, and that class is `_WHERE_IT_GOES` below.
#
#   2. WHAT STANDS THERE. Where the claim enters a place the table
#      says CARRIES the person's text, the table has already said what
#      stands there: the spelling itself, character for character. So
#      the claim has to say that. A claim that enters `missing_by_source`
#      and says anything less is refused without the rule reading what
#      the less is -- which is the whole point, because "a count", "a
#      tally", "the arithmetic" and whatever somebody reaches for next
#      year are an open class and the reason the wording guard cannot
#      close this shape.
#
#   3. WHETHER IT BOUNDS. A restrictive limiter -- `only`, `just`,
#      `merely`, `solely`, `alone` -- is English's own mark that what
#      follows is ALL there is, and it is closed. It may stand in a
#      claim bounded to a place that carries none of the person's text,
#      because there the bound is true and this repository has to be
#      able to write it. It may not stand in a claim that bounds what
#      is kept with no such place to hold the bound. This question is
#      asked of every claim of a sentence that names the person's value
#      anywhere in it, because English drops the subject across a
#      joining word -- `never written into the settings block and
#      counted only as a tally` is two claims about one value.
#
# WHICH PLACE A CLAIM IS ABOUT, WHERE IT ENTERS SEVERAL, is not
# guessed. The claim is checked against every place it enters, and the
# carrying places' question is the strict one, so a claim that enters
# both a clean room and a carrying place must satisfy the carrying
# place's question: a sentence whose subject cannot be settled is
# refused rather than read charitably.
#
# WHAT THIS STILL MISSES, at its size and written down rather than
# waited for:
#
#   * A reduction carrying no limiter in a claim that DOES say the
#     spelling itself stands there -- "the word itself is kept in
#     `missing_by_source` as a count" -- is missed. Both closed classes
#     are satisfied and the falsity is again the reader's inference.
#     The measurement in
#     `test_the_census_states_what_it_still_cannot_read` holds that
#     residue at one sentence.
#   * A sentence that never names the person's value in this family's
#     words is not examined at all, which is the naming half's own
#     bound and is stated with the naming half.
#   * A place entered and then taken back inside the same claim -- "in
#     the settings block or not" -- answers, because reading the taking
#     back means reading a negation the claim never puts on the place.
#     That is not new here: every scope mark in this family, including
#     the wording guard's, is cured by naming the scope, and the fourth
#     family's `_withdrawn_in` is the only place a withdrawal is read
#     at all.
#
# WHY THIS CORPUS AND NOT THE WHOLE TREE. Default-deny is affordable
# exactly where the product's sentences are enumerable. Over the whole
# of `RETENTION_SURFACES` the same rule would report scores of the
# statements that name the person's value, most of them saying nothing
# about where anything goes; that measurement is in
# `test_the_census_would_report_this_tree_and_that_is_its_bound`.
#
# THE THIRD TABLE, WHICH THE FINDING ASKED FOR. A refusal a person
# reads is not written down anywhere as a sentence: the loader hands a
# rule and two clauses to a template in `errors.py`, and the sentence
# exists only on the screen. That was the reason the first census
# stopped at two tables -- and it was the wrong reason, because the
# PIECES are written down as data, one call site at a time, and the
# template that joins them is written down too. So the refusals are
# assembled here from the shipped pieces by the shipped template and
# censused whole. A run-time piece -- a count, a key out of the file --
# is stood in for by `_FILLED_IN_LATER`, which names no place and no
# value, so a clause whose place is only ever supplied at run time must
# say the place in words. One did, and now does.
_THE_PRODUCTS_OWN_TABLES = (
    "the loader's rule table",
    "the option help",
    "the refusals the loader assembles",
)

# A sentence ends at a full stop, a semicolon, a question or an
# exclamation -- and NOT at an em-dash aside, unlike the wording guard
# above. An aside is inside one sentence, and a census that cut there
# would be reading half-claims (`the profile records how many values you
# named -- where one is synthtwin's own word -- which of those it was`
# is one claim, and the reader meets it as one).
_SENTENCE_END = re.compile(r"(?<=[a-z0-9)\]\"'*`])[.;!?] ")

# WHERE ONE CLAIM ENDS AND THE NEXT BEGINS, and it is the file's own
# notion of a joining word rather than a second one: `_CLAUSE_CLOSES`
# is what stops the wording guard's scope reaching forward, for the
# same reason it stops a place here. A comma is deliberately NOT a
# claim boundary -- `In the settings block, a value you typed is kept
# only as a count` is one claim and its place stands in front of it --
# and the comma splice that a boundary would have caught is caught by
# the entering rule instead, which is where it belongs.
def _the_claims_in(sentence: str) -> "list[str]":
    """One sentence, cut into the claims a joining word separates."""
    claims = [sentence]
    for join in _CLAUSE_CLOSES:
        cut: list[str] = []
        for claim in claims:
            cut = cut + claim.split(join)
        claims = cut
    return [claim for claim in claims if claim.strip()]


# HOW ENGLISH SAYS A THING IS IN A PLACE. A closed class of function
# words: the prepositions that put something somewhere, and the two
# relative adverbs that say where something happens. This is the same
# kind of set as `_A_NEGATOR` -- closed by the language and not by
# anybody's diligence -- and it is what makes the difference between a
# place a claim ENTERS and a place a sentence merely mentions.
_WHERE_IT_GOES = (
    r"(?:in|into|inside|within|under|onto|through|out of|outside|at|"
    r"from|beside|where|wherever)"
)

# What may stand between the preposition and the place: determiners,
# possessives, and the marks this repository quotes a field name with.
_ON_THE_WAY_THERE = r"(?:[a-z0-9'`_-]+ ){0,3}[`'\"(\[]*"

# WHAT THE TABLE SAYS STANDS IN A CARRYING PLACE, said. The rule kind
# at every carrying path is `_SPELLING` -- an authorized spelling out
# of the person's table -- so a true claim about one of those places
# says the value ITSELF stands there. English marks that with the
# intensive pronoun, which is a function word, and this repository
# writes one idiom beside it.
#
# THIS IS A CURE AND NOT AN ACCUSATION, and the difference is the whole
# argument for having it. An accusation list misses a wording and a
# false sentence lands green; a cure list misses a wording and a TRUE
# sentence is refused until it says the plain thing. The census stays
# default-deny either way, so nothing here is got round with an
# invented verb, an invented limiter or an invented word for a quantity.
_THE_SPELLING_ITSELF = (
    rf"\b{_A_VALUE} (?:itself|themselves)\b",
    r"\bcharacter for character\b",
    (
        r"\bas (?:you|they|somebody|someone|the person) "
        r"(?:typed|named|wrote) it\b"
    ),
)

# The three answers, as constants, so a red check can hold this rule to
# WHICH question reported a sentence and not merely to whether one did.
# A case that claims to be caught for entering the spelling's own place
# and is in fact caught for entering none is a case that would keep
# passing once the first question moved.
_ENTERS_NO_PLACE = "it enters no place, so it speaks for the whole description"
_NOT_WHAT_STANDS_THERE = (
    "it enters a place the person's spelling stands in and does not say "
    "the spelling stands there"
)
_A_BOUND_WITH_NOWHERE_TO_HOLD = (
    "it bounds what is kept, and enters no place that carries none of "
    "the person's text"
)


def _clean_rooms() -> "tuple[str, ...]":
    """The clean places a claim can put something IN.

    `_clean_places()` holds two kinds of answer and the census needs
    them apart. The document's own regions are rooms: a claim enters
    one, or does not. The stated limits of contract 5 section 7 --
    below the floor, pooled, a column publishing nothing -- are
    CONDITIONS rather than rooms, and a claim carrying one is bounded
    to a case where nothing of the person's text is published at all,
    whatever place it names. Derived by subtraction so a limit added to
    one set cannot fall out of both.
    """
    return tuple(mark for mark in _clean_places() if mark not in _STATED_LIMITS)


def _entered_in(claim: str, places: "tuple[str, ...]") -> "list[str]":
    """Every one of those places this claim puts something into."""
    found: list[str] = []
    for mark in places:
        for where in re.finditer(mark, claim):
            before = claim[: where.start()]
            if re.search(rf"\b{_WHERE_IT_GOES} {_ON_THE_WAY_THERE}$", before):
                found.append(mark)
                break
    return found


def _says_the_spelling_itself_stands(claim: str) -> bool:
    """Whether this claim says the person's own value itself is there.

    A mark with a negator in front of it is the opposite claim and does
    not answer: "not the word itself" denies the identity, which is the
    wording guard's business and never a cure here.
    """
    for mark in _THE_SPELLING_ITSELF:
        for said in re.finditer(mark, claim):
            before = claim[: said.start()]
            if re.search(rf"\b{_A_NEGATOR} {_JUST_THE_ONE}$", before):
                continue
            return True
    return False


def _speaks_falsely_of_the_place(said: str) -> "list[tuple[str, str]]":
    """Every claim of one shown text that fails one of the three questions.

    Guarantees:

    - Inputs: one text the product can show, in any casing.
    - Determinism: a fixed function of that text, of the producer's
      publication table and of the two closed function-word classes;
      nothing is read here and nothing is run.
    - Errors raised: none. A caller reports; this counts.
    - Boundary: pure text; opens nothing.
    """
    found: list[tuple[str, str]] = []
    for sentence in _SENTENCE_END.split(" ".join(said.lower().split())):
        claims = _the_claims_in(sentence)
        theirs = [
            claim for claim in claims if _names_your_word(claim) is not None
        ]
        if not theirs:
            continue
        for claim in theirs:
            if any(re.search(mark, claim) for mark in _STATED_LIMITS):
                continue
            if _entered_in(claim, _carrying_places()):
                if not _says_the_spelling_itself_stands(claim):
                    found.append((_NOT_WHAT_STANDS_THERE, claim.strip()))
                continue
            if not _entered_in(claim, _clean_rooms()):
                found.append((_ENTERS_NO_PLACE, claim.strip()))
        for claim in claims:
            if not any(re.search(mark, claim) for mark in _RESTRICTIVE):
                continue
            if any(re.search(mark, claim) for mark in _STATED_LIMITS):
                continue
            if _entered_in(claim, _clean_rooms()):
                continue
            found.append((_A_BOUND_WITH_NOWHERE_TO_HOLD, claim.strip()))
    return found


def _carrying_places() -> "tuple[str, ...]":
    """The names of the paths that DO carry the person's text.

    Derived from the same publication rules the clean regions are
    derived from, by taking the steps of every `_SPELLING` path rather
    than the top-level blocks that hold none. So a sentence may answer
    the census either way -- by entering a place that carries none of
    it, or by entering the place it stands in and saying it stands
    there -- and both answers move on the commit that moves the format.
    """
    names: set[str] = set()
    for path in _paths_that_carry_your_text():
        for step in path:
            if step in ("[]", "<key>"):
                continue
            names.add(step)
            if step.endswith("s"):
                names.add(step[:-1])
    return tuple(rf"\b{name}\b" for name in sorted(names))


# WHAT A RUN-TIME PIECE BECOMES when a refusal is assembled here. It
# names no place, no value and no quantity, so it can neither cure a
# clause nor accuse one, and a maintainer reading a failure sees
# exactly where the message would have filled something in.
_FILLED_IN_LATER = "(...)"


def _every_text_of(node: "ast.expr") -> "list[str]":
    """Every text this argument can be, run-time pieces stood in for.

    A constant is itself; a formatted text is its literal parts with
    `_FILLED_IN_LATER` where a value goes; a choice between two texts
    is BOTH, because a person meets one of them. Anything else is a
    piece this file cannot read, and it is stood in for rather than
    guessed at.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return [node.value]
    if isinstance(node, ast.JoinedStr):
        said = [""]
        for part in node.values:
            if isinstance(part, ast.Constant) and isinstance(part.value, str):
                said = [start + part.value for start in said]
            else:
                said = [start + _FILLED_IN_LATER for start in said]
        return said
    if isinstance(node, ast.IfExp):
        return _every_text_of(node.body) + _every_text_of(node.orelse)
    return [_FILLED_IN_LATER]


def _every_filling(pieces: "list[list[str]]") -> "list[tuple[str, ...]]":
    """Every way one call site's arguments can read, in a fixed order."""
    ways: list[tuple[str, ...]] = [()]
    for piece in pieces:
        ways = [way + (said,) for way in ways for said in piece]
    return ways


def _an_invariant_broken(filling: "tuple[str, ...]") -> str:
    """R17, assembled: the rule's own words and the two clauses."""
    rule, where, first, second = filling
    words = contract.INVARIANTS.get(rule, _FILLED_IN_LATER)
    return errors.profile_invariant_broken(rule, words, where, first, second)


def _a_wrong_kind(filling: "tuple[str, ...]") -> str:
    """R15, assembled. What was found is a KIND and is never quoted."""
    key, where, _found, required = filling
    return errors.profile_wrong_type(key, where, _FILLED_IN_LATER, required)


def _out_of_its_range(filling: "tuple[str, ...]") -> str:
    """R16, assembled: what stood there and what is allowed there."""
    key, where, shown, permitted = filling
    return errors.profile_out_of_range(key, where, shown, permitted)


def _out_of_range_unquoted(filling: "tuple[str, ...]") -> str:
    """R16 for a count no message may quote."""
    key, where, permitted = filling
    return errors.profile_out_of_range_unquoted(key, where, permitted)


def _a_key_that_is_missing(filling: "tuple[str, ...]") -> str:
    """R14, assembled: the entry, where it belongs, and what has one."""
    key, where, required_by = filling
    return errors.profile_missing_key(key, where, required_by)


def _a_key_nobody_knows(filling: "tuple[str, ...]") -> str:
    """R13, assembled."""
    key, where = filling
    return errors.profile_unknown_key(key, where)


# EVERY WAY THE LOADER BUILDS A REFUSAL, with the number of pieces each
# takes. The arity is written down so that a wrapper gaining an
# argument fails this file loudly instead of quietly dropping its call
# sites out of the corpus -- a census over a corpus that shrank is a
# census that passes everything it stopped reading.
_THE_LOADERS_TEMPLATES = {
    "_broken": (4, _an_invariant_broken),
    "_wrong_type": (4, _a_wrong_kind),
    "_out_of_range": (4, _out_of_its_range),
    "_row_count_out_of_range": (3, _out_of_range_unquoted),
    "_missing": (3, _a_key_that_is_missing),
    "_unknown": (2, _a_key_nobody_knows),
}


def _the_refusals_the_loader_assembles() -> "list[tuple[str, str]]":
    """Every refusal the loader can build, assembled from its own pieces.

    Read out of the loader's own syntax rather than by running it: the
    clauses are written down at the call sites, the templates are
    written down in `errors.py`, and the sentence a person reads is the
    two joined. That join is done here with the shipped template, so
    the census reads the sentence rather than the fragments.

    Guarantees:

    - Inputs: none; reads the shipped loader's source and the shipped
      message templates.
    - Determinism: the order of the loader's own syntax tree, and a
      fixed function of it.
    - Errors raised: `AssertionError` where a template's call site does
      not carry the number of pieces the template takes.
    - Boundary: no description is loaded, no file of anybody's is read,
      and no refusal is raised.
    """
    found: list[tuple[str, str]] = []
    source = ast.parse((PACKAGE / "contract.py").read_text(encoding="utf-8"))
    for node in ast.walk(source):
        if not (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)):
            continue
        if node.func.id not in _THE_LOADERS_TEMPLATES:
            continue
        pieces, template = _THE_LOADERS_TEMPLATES[node.func.id]
        assert len(node.args) == pieces, (
            f"{node.func.id} at contract.py:{node.lineno} is called with "
            f"{len(node.args)} pieces and this file assembles {pieces}. "
            "The loader's refusal changed shape: move the arity here, in "
            "the same commit, or the census stops reading this route."
        )
        seat = (
            f"the refusal {node.func.id} builds at "
            f"contract.py:{node.lineno}"
        )
        for filling in _every_filling(
            [_every_text_of(argument) for argument in node.args]
        ):
            found.append((seat, template(filling)))
    return found


def _the_products_own_sentences() -> "list[tuple[str, str]]":
    """Every sentence the product can show that is written down as data.

    Guarantees:

    - Inputs: none; reads the shipped loader's rule table, the shipped
      command line's own option help, and the refusals the loader
      assembles out of its own clauses.
    - Determinism: sorted by table and then by the order each table
      itself has.
    - Errors raised: `AssertionError` from the check below where the
      corpus comes back empty, because a census over an empty corpus
      passes everything.
    - Boundary: only this repository's own source is read, no command
      line is parsed, no argument acted on and no description loaded.
    """
    found: list[tuple[str, str]] = []
    if "the loader's rule table" in _THE_PRODUCTS_OWN_TABLES:
        for rule in sorted(contract.INVARIANTS):
            found.append((f"contract invariant {rule}", contract.INVARIANTS[rule]))
    if "the option help" in _THE_PRODUCTS_OWN_TABLES:
        for option, said in _the_option_help():
            found.append((f"the help for {option}", said))
    if "the refusals the loader assembles" in _THE_PRODUCTS_OWN_TABLES:
        found = found + _the_refusals_the_loader_assembles()
    return found


def _the_option_help() -> "list[tuple[str, str]]":
    """Each command-line option's own help, read off the shipped parser.

    Read out of the module's own syntax rather than by building the
    parser, because building it means running the function that reads a
    command line, and this file may not do that to learn what a screen
    says. A help written as a constant is followed to the constant, so
    `--missing-value`'s -- which is held apart on purpose -- is read
    whole.
    """
    said: list[tuple[str, str]] = []
    source = ast.parse((PACKAGE / "cli.py").read_text(encoding="utf-8"))
    for node in ast.walk(source):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        if not (isinstance(func, ast.Attribute) and func.attr == "add_argument"):
            continue
        named = "an option"
        if node.args and isinstance(node.args[0], ast.Constant):
            named = f"{node.args[0].value}"
        for keyword in node.keywords:
            if keyword.arg != "help":
                continue
            if isinstance(keyword.value, ast.Constant):
                said.append((named, f"{keyword.value.value}"))
            elif isinstance(keyword.value, ast.Name):
                said.append((named, f"{getattr(cli, keyword.value.id)}"))
    return said


def test_the_sentences_the_product_shows_say_where_your_word_stands() -> None:
    """THE STRUCTURAL HALF, and it reads no word list of any kind.

    THE DEFECT THIS EXISTS FOR (review items P3-V11-F1, P3-V12-F1).
    Four rounds running, a false retention claim reached a governed
    surface and the wording guard built to catch it missed the one that
    landed. Each time the miss was a new SHAPE. The third one -- a
    claim that what is kept is a reduction of what was given -- has a
    half no model of denial can reach, because the sentence carries no
    denial: it says what is kept and stops. The fourth was this
    census's own first predicate, which asked only whether a place was
    NAMED and passed a sentence that named the very place the spelling
    stands in.

    SO THIS DOES NOT TRY TO RECOGNISE A DENIAL, AND IT DOES NOT ACCEPT
    A MENTION. It asks three questions of every claim the product shows
    that names the person's own value, and answers all three out of the
    producer's publication table: does the claim enter a place; where
    that place carries the person's spelling, does the claim say the
    spelling itself stands there; and where the claim bounds what is
    kept, is the bound held by a place that carries none of their text.
    The comment above this test states each question, why its class is
    closed, and what the three together still miss.

    THE RED CHECKS. `REINSTATE=P3-V12-F1` puts the shipped predicate
    back -- a place mentioned anywhere in the sentence answers -- and
    `REINSTATE=P3-V12-F1-clause` writes a reduction into a clause of a
    refusal the loader assembles, which is the route the corpus gained
    this round. Either reds this.
    """
    corpus = _the_products_own_sentences()
    if _THE_PRODUCTS_OWN_TABLES:
        assert corpus, (
            "The census has no corpus, so it passes everything. The "
            "loader's rule table, the command line's options or the "
            "loader's own refusals have moved out from under it."
        )
    silent: list[str] = []
    for seat, said in corpus:
        for why, claim in _speaks_falsely_of_the_place(said):
            silent.append(f"{seat}: {claim[:200]}\n      -- {why}")
    assert not silent, (
        "These claims the product SHOWS speak about a value the person "
        "typed, and what they say is not what the producer's own "
        "publication table says stands in the place they put it in:\n  "
        + "\n  ".join(silent)
        + "\n\nWhat the table says: the spelling goes into a column's "
        "`missing_by_source`, character for character, wherever at "
        "least `small_cell_floor` rows share it and the column "
        "publishes values at all. So a claim that enters that place "
        "has to say the spelling itself stands there; a claim that "
        "enters no place at all has spoken for the whole description, "
        "and the whole description is the one thing about which no "
        "denial is true; and a claim that bounds what is kept has to "
        "bound it to a place that carries none of their text -- the "
        "settings block, the two vocabulary lists, below the floor, a "
        "column that publishes nothing. This check reads no verb and "
        "no negation, so rewording will not satisfy it and is not "
        "meant to."
    )


def test_the_census_reads_no_verb_and_no_word_for_a_quantity() -> None:
    """What the census is, asserted against what a word list would be.

    Three sentences, each a reduction, each written with a different
    verb and a different word for the quantity, and none of them
    carrying a negation at all. A word list catches none; this rule
    catches all three, because it is not reading any of that.

    The three beside them are the same claims WITH their place, and
    they must pass -- otherwise the rule would be a ban on mentioning a
    declared value, which is a ban this repository could not live
    under.
    """
    for silent in (
        "A value you typed is kept only as a count.",
        "The words you typed are banked as a tally and no more.",
        "Synthtwin hoards the arithmetic of the markers you named.",
    ):
        assert _speaks_falsely_of_the_place(silent), (
            f"the census stopped reporting a placeless claim:\n  {silent}"
        )
    for answered in (
        "A value you typed is kept only as a count in the settings block.",
        (
            "The word you typed stands in that column's "
            "`missing_by_source`, character for character."
        ),
        "Below the floor the word you typed is pooled and named nowhere.",
    ):
        assert not _speaks_falsely_of_the_place(answered), (
            "the census now reports a sentence that says where:\n  "
            f"{answered} -- {_speaks_falsely_of_the_place(answered)}"
        )


# THE TWO SENTENCES THAT ANSWERED WITH A PLACE, word for word as review
# item P3-V12-F1 wrote them, each with the question it must now fail.
# They are kept here for the reason every retired false sentence in
# this file is kept: a surface that reproduces one is making it again,
# and a rule that stops reporting one has stopped being the repair it
# was written as.
_THE_SENTENCES_THAT_ANSWERED_WITH_A_PLACE = (
    (
        "the direct carrying-place bypass",
        "In `missing_by_source`, a value you typed is kept only as a count.",
        _NOT_WHAT_STANDS_THERE,
    ),
    (
        "the unrelated clean-place bypass",
        (
            "The settings block records the rule, and the description "
            "keeps only a tally of a value you typed."
        ),
        _ENTERS_NO_PLACE,
    ),
    (
        "the same bypass joined by a comma rather than a word",
        (
            "The settings block records the rule, the description keeps "
            "only a tally of a value you typed."
        ),
        _ENTERS_NO_PLACE,
    ),
    (
        "the bypass with the subject dropped after the joining word",
        (
            "A word of your own is never written into the settings block "
            "and is counted only as a tally."
        ),
        _A_BOUND_WITH_NOWHERE_TO_HOLD,
    ),
    (
        "a reduction at the carrying place with no limiter to read",
        "In `missing_by_source`, what a value you typed leaves is a tally.",
        _NOT_WHAT_STANDS_THERE,
    ),
)

# The predicate as it shipped at review item P3-V12-F1: any clean or
# carrying place, mentioned anywhere in the sentence, answered. Kept as
# a constant and run against the sentences above, so the finding is
# evidence in this file forever rather than a paragraph in a review
# nobody reads again.
def _a_place_was_mentioned(said: str) -> "list[tuple[str, str]]":
    """The shipped census, exactly: mention a place and the claim passes."""
    places = _clean_places() + _carrying_places()
    found: list[tuple[str, str]] = []
    for sentence in _SENTENCE_END.split(" ".join(said.lower().split())):
        if _names_your_word(sentence) is None:
            continue
        if any(re.search(mark, sentence) is not None for mark in places):
            continue
        found.append((_ENTERS_NO_PLACE, sentence.strip()))
    return found


def test_the_census_reads_the_claim_against_the_place_it_names() -> None:
    """The two bypasses, and why each of them is now reported.

    THE MEASUREMENT THAT MADE THIS BLOCKING. Both halves are here
    because both are the finding: the sentences passed, AND the rule
    written one round earlier to refuse exactly this class reported
    nothing about them. A repair that only reported the two sentences
    would leave the second half true, so the shipped predicate is kept
    as a function in this file and run against them.

    Each case names the question it must fail by, so a case that starts
    being reported for entering no place when it was written to test
    what stands in the place it enters fails here rather than passing
    for the wrong reason.
    """
    for what, said, why in _THE_SENTENCES_THAT_ANSWERED_WITH_A_PLACE:
        reported = _speaks_falsely_of_the_place(said)
        assert reported, (
            f"The census no longer reports {what}:\n  {said}\n\nThis is "
            "one of the sentences review item P3-V12-F1 walked through "
            "the shipped rule with. If a later repair genuinely makes "
            "this sentence true, the publication table moved and every "
            "sentence about what a declared word leaves behind moves "
            "with it."
        )
        assert reported[0][0] == why, (
            f"{what} is reported, but for the wrong reason:\n  {said}\n  "
            f"expected: {why}\n  reported: {reported}"
        )
    for what, said, _why in _THE_SENTENCES_THAT_ANSWERED_WITH_A_PLACE[:2]:
        assert not _a_place_was_mentioned(said), (
            "The predicate as it shipped now reports this sentence, so "
            "the constant recording what P3-V12-F1 measured has drifted "
            f"from what actually shipped:\n  {what}: {said}\n\nFix the "
            "constant, not this assertion: it is the evidence that a "
            "rule asking only whether a place was NAMED passed a claim "
            "that named the one place the spelling stands in."
        )


def test_the_census_states_what_it_still_cannot_read() -> None:
    """The residue, at its size, and where it stops.

    A reduction that carries no limiter AND says the spelling itself
    stands in the place is missed: both closed classes are satisfied
    and what makes it false is again a judgement that a count is less
    than what was given. One sentence, asserted to be missed, so the
    residue has a size instead of a hand-wave.

    WHERE THE MISS STOPS, which is the more useful half. The same
    sentence is reported the moment it bounds what it says -- and the
    same claim without the cure is reported whatever verb or word for a
    quantity it reaches for. So what is missing is not "the census
    cannot read this wording" but "a claim that says the spelling is
    there and then says something else is there too has said two true
    things in one sentence", which is a fact about English and not
    about this file.
    """
    missed = (
        "In `missing_by_source` the word itself is kept as a count of a "
        "value you typed."
    )
    assert not _speaks_falsely_of_the_place(missed), (
        "The census now reports the sentence this residue is measured "
        f"by:\n  {missed}\n\nThat is good news and it is a change to "
        "what this family promises. Say so where the promise is "
        "written: the comment above the census, amendment A-P3-44 in "
        "the plan, and this test."
    )
    for reported in (
        (
            "In `missing_by_source` the word itself is kept only as a "
            "count of a value you typed."
        ),
        "In `missing_by_source` a value you typed is kept as a count.",
    ):
        assert _speaks_falsely_of_the_place(reported), (
            "The census stopped reporting a claim about the place the "
            f"spelling stands in:\n  {reported}\n\nWithout this the "
            "residue above is not a residue, it is the rule."
        )


# Measured on this tree at the commit that wrote this line, over every
# governed surface rather than over the corpus. It is a FLOOR and not an
# equality, for the reason the limiter measurement above is one: an
# equality reds on every unrelated paragraph anybody writes, and what
# has to red is the count COLLAPSING, because that is the day the census
# becomes affordable tree-wide and this bound can close.
_CLAIMS_A_TREE_WIDE_CENSUS_WOULD_REPORT = 250


def test_the_census_would_report_this_tree_and_that_is_its_bound() -> None:
    """Why the corpus is the corpus: the same rule over every surface.

    Default-deny is affordable where the sentences are enumerable. This
    measures what it would cost everywhere else, so the bound is a
    number this suite recomputes rather than a sentence somebody wrote
    once. If it ever collapses, the corpus can grow and the argument
    for growing it belongs in the plan.
    """
    would_report = 0
    for relative in RETENTION_SURFACES:
        would_report = would_report + len(
            _speaks_falsely_of_the_place(_text(relative))
        )
    assert would_report >= _CLAIMS_A_TREE_WIDE_CENSUS_WOULD_REPORT, (
        "A census over every governed surface now reports "
        f"{would_report} claims, and the floor beside this test says "
        f"{_CLAIMS_A_TREE_WIDE_CENSUS_WOULD_REPORT}. READ them before "
        "touching the floor: if they have genuinely become few, and "
        "each is a claim about what a description keeps, the corpus is "
        "affordable at that width and this bound can close."
    )


# One clause of one refusal a person actually meets, word for word as
# the loader writes it. The anchor is a CLAUSE and not a whole message:
# what has to be proved is that the clause and its rule's own words are
# joined into one sentence by the shipped template, which is the thing
# the first census could not read.
_A_CLAUSE_OF_A_REFUSAL_A_PERSON_MEETS = (
    "in a version 5 description no text of the person's own stands in "
    "that block"
)


def test_the_census_reads_the_refusals_the_loader_assembles() -> None:
    """The third table, and the vacuity floor under it.

    Review item P3-V12-F1 held that the run-time-assembly limitation
    was real but not irreducible: a refusal is a template plus the
    clauses written at each call site, and both are written down, so
    the whole is enumerable and a false reduction in one of those
    clauses is user-facing. It is in the corpus now, and this is what
    keeps that from becoming a claim nobody rechecks.

    THREE THINGS ARE ASSERTED. That the corpus is not empty. That every
    way the loader builds a refusal reaches the census, counted a
    second time by a plain text search of the same file, so a syntax
    walk that quietly stopped walking fails here rather than shrinking
    the corpus under a rule that would still pass. And that one refusal
    a person actually meets is present whole -- its rule's own words
    and the clause written beside them, joined -- so the assembly is
    checked against a sentence and not only against a count.

    THE RED CHECK. `REINSTATE=P3-V12-F1-corpus` takes the assembled
    refusals back out of the corpus, which is what this round's absence
    looked like, and reds this.
    """
    assembled = _the_refusals_the_loader_assembles()
    assert assembled, (
        "The loader assembles no refusals this file can read. Either "
        "the wrapper names in `_THE_LOADERS_TEMPLATES` moved, or the "
        "census lost the whole route review item P3-V12-F1 asked for."
    )
    source = (PACKAGE / "contract.py").read_text(encoding="utf-8")
    for name in sorted(_THE_LOADERS_TEMPLATES):
        counted = len(re.findall(rf"raise {name}\(", source))
        assert counted, (
            f"This file assembles refusals through {name} and the "
            "loader raises none. A route the loader stopped using is a "
            "route that leaves this map in the same commit -- leaving "
            "it here makes the count below pass on nothing."
        )
        reached = {
            seat
            for seat, _said in assembled
            if seat.startswith(f"the refusal {name} builds")
        }
        assert len(reached) == counted, (
            f"The loader raises {name} at {counted} places and "
            f"{len(reached)} of them reached the census. A refusal "
            "route that leaves the corpus is a route this rule stops "
            "reading, which is how a default-deny census comes to pass "
            "everything."
        )
    whole = [" ".join(said.lower().split()) for _seat, said in assembled]
    anchored = [
        said
        for said in whole
        if _A_CLAUSE_OF_A_REFUSAL_A_PERSON_MEETS in said
        and " ".join(contract.INVARIANTS["C5-S7"].lower().split()) in said
    ]
    assert anchored, (
        "The refusal this test anchors on is no longer assembled out of "
        "its rule's words and its own clause. If the message changed, "
        "move the constant in the same commit: it is what proves the "
        "census reads the sentence a person meets rather than the "
        "fragments it is built from."
    )


def test_the_derivation_reads_the_producer_and_not_a_list() -> None:
    """The three derived sets are what the family is checked against.

    Without this, a publication map that stopped naming the key -- or a
    settings block that started carrying one -- would leave every
    sentence in the repository checked against a rule the producer no
    longer follows, which is the drift the third and fifth families
    exist to refuse.
    """
    carrying = _paths_that_carry_your_text()
    assert ("columns", "[]", "missing_by_source", "<key>") in carrying, carrying
    clean = _regions_that_carry_none_of_it()
    assert "settings" in clean and "columns" not in clean, clean
    # The cure set is BUILT from those regions, so a region leaving the
    # clean set takes its cure with it. Asserted rather than assumed,
    # because the cure is what makes every scoped sentence pass.
    assert r"\bsettings\b" in _clean_places()
    assert r"\bcolumns\b" not in _clean_places()
    # And the census's two halves of that set are a partition of it:
    # the rooms a claim can enter, and the stated limits that bound a
    # claim wherever it stands. A limit that fell into both would let a
    # claim enter a place by naming a condition.
    assert set(_clean_rooms()) | set(_STATED_LIMITS) == set(_clean_places())
    assert not set(_clean_rooms()) & set(_STATED_LIMITS)


# ---------------------------------------------------------------------
# THE SEVENTH FAMILY: AN EXEMPTION THE TWIN DOES NOT GRANT
# (owner instruction 2026-08-26)
# ---------------------------------------------------------------------
#
# WHAT THE OWNER SAID, AND WHY IT IS A TEST. Describing the product, the
# owner wrote that synthtwin lets people develop statistical code with
# an assistant "without HIPAA constraints (because is synthetic)". The
# first half of that thought is exactly what this tool is for. The
# second half is a claim about somebody's OBLIGATIONS, and it is one
# this project is in no position to make: the charter's own limits say
# all five files a run leaves behind carry facts computed from real
# data, and at the default floor of one every value in the table is
# named in the description with the number of rows that held it.
#
# No surface here has ever made that claim -- a search for it before
# this family was written returned nothing, which is why the repair is
# a guard and not a correction. What is being fixed is the VACUUM: the
# sentence is the one that comes naturally to anybody describing a
# synthetic twin, it is one clause away from every true sentence here
# about privacy, and it is the sentence a review board stops on. The
# charter and the front page now state the honest form; this keeps them
# stating it.
#
# WHY COMPOSITIONAL, LIKE THE FOURTH AND NOT LIKE THE FIRST. The claim
# has no settled phrasing. "Not subject to", "does not apply", "removes
# the need for", "falls outside", "without needing" are five ways to
# say it and there is no reason to think a sixth will not be written.
# The fourth family learned this at review round 4 -- a ban anchored on
# one sentence shape catches one sentence shape -- so this one fires on
# a PAIR, in one statement:
#
#   * it NAMES an obligation regime, in any of the ways English names a
#     privacy rule, an institution's own rules, an ethics approval, a
#     data-use agreement or a compliance requirement; and
#   * it makes an EXEMPTION claim about it -- does not apply, is not
#     subject to, is exempt from, removes the need for, falls outside.
#
# Neither half alone is a defect, and both halves alone are required
# here: the charter NAMES those regimes in order to say they still
# bind, and ordinary English about what this product refuses to do uses
# the exemption words constantly.
#
# AND THE CURE IS A WINDOW, on the fourth family's own precedent and
# for its reason: a passage that names a regime, states the exemption
# and then refuses it -- "still applies", "apply to all five", "is not
# a finding that", "for the people who set it" -- is the honest
# paragraph this instruction requires rather than the claim it bans,
# and this repository writes exactly that way. What a surface may not
# do is state the exemption with no refusal anywhere near it.
#
# MEASURED BEFORE LANDING: zero statements on the whole governed tree
# match the pair, and all six wordings in `_EXEMPTIONS_THAT_MUST_TRIP`
# are caught. The vacuity floor below is that measurement, kept.

_OBLIGATION_NAMES = (
    r"\bprivacy (?:rules?|laws?|regulations?|requirements?|polic(?:y|ies))\b",
    r"\bdata[- ]protection (?:rules?|laws?|regulations?)\b",
    r"\bhealth[- ]information (?:privacy )?(?:rules?|laws?)\b",
    r"\b(?:your |the )?institution'?s? (?:own )?(?:rules?|policies|requirements?)\b",
    r"\binstitutional (?:rules?|policies|requirements?|approval)\b",
    r"\breview board\b",
    r"\bethics (?:review|committee|approval)\b",
    r"\bdata[- ]use agreements?\b",
    r"\bgoverning (?:rules?|regulations?)\b",
    r"\bcompliance (?:rules?|requirements?|obligations?)\b",
    r"\bhuman[- ]subjects?\b",
    r"\brules? for real-derived material\b",
    # Round 1 item 3: ordinary prose the first list missed.
    r"\bregulatory (?:rules?|requirements?|obligations?|constraints?)\b",
    r"\binstitutional polic(?:y|ies)\b",
    r"\b(?:the )?review board'?s? (?:jurisdiction|remit|reach)\b",
    r"\bethics (?:board|oversight)\b",
    r"\bapprovals? (?:is|are) (?:needed|required|necessary)\b",
    # NOT a bare `approval`, and the reason is measured rather than
    # argued. A draft used the bare noun to catch "approval is
    # unnecessary when the table is synthetic", and the contract's own
    # honest sentence -- "a privacy approval given for an earlier
    # description does not cover a marked row", which says an
    # obligation reaches FURTHER than a reader might think -- was
    # reported as the banned claim. The shape is named instead of the
    # noun widened.
    r"\bapprovals? (?:is|are) (?:unnecessary|not needed|not required)\b",
)

# The claim that an obligation has been LIFTED. Deliberately not here:
# any wording about what the TOOL does not guarantee. "Offers no formal
# privacy guarantee" is a true sentence this repository is required to
# carry, and a ban that caught it would be a ban nobody could satisfy.
_EXEMPTION_MARKS = (
    r"\b(?:does|do) not apply\b",
    r"\bno longer applies?\b",
    r"\bstops? applying\b",
    r"\bnot subject to\b",
    r"\bexempt from\b",
    r"\bexempts? (?:you|your|the user)\b",
    r"\bremoves? the need for\b",
    r"\bwithout (?:needing|requiring|the need for)\b",
    r"\bfrees? (?:you|your team) from\b",
    r"\bfalls? outside\b",
    r"\bnot covered by\b",
    r"\bno (?:approval|review|oversight|permission) (?:is )?(?:needed|required)\b",
    r"\bside[- ]steps?\b",
    # Round 1 item 3: ordinary prose the first list missed.
    r"\bneed not comply\b",
    r"\bneed not (?:be )?(?:seek|obtain|follow|meet)\b",
    r"\bis unnecessary\b",
    r"\b(?:is|are|falls?|sits?) outside\b",
    r"\bdoes not (?:govern|bind|apply to|extend to)\b",
    r"\bdo not (?:govern|bind|apply to|extend to)\b",
    r"\b(?:is|are) not governed by\b",
    r"\b(?:is|are) not (?:required|necessary)\b",
    r"\bno .{0,24}?(?:review|approval|oversight) is (?:necessary|needed|required)\b",
    r"\bobviates? the need\b",
    r"\b(?:is|are) beyond\b",
    # Round 3 item 4.
    r"\bdoes not need\b",
    r"\bdo not need\b",
    r"\bcan be skipped\b",
    r"\b(?:is|are) exempt under\b",
    r"\blets? you ignore\b",
    r"\bignore .{0,30}?(?:rules?|requirements?|policy|policies)\b",
    # Round 4.
    r"\bceases? to apply\b",
    r"\b(?:is|are) excluded from\b",
    r"\b(?:is|are) inapplicable\b",
    r"\bno longer (?:binds?|governs?|reaches?|covers?)\b",
    r"\bare exempt\b",
    r"\bis exempt\b",
)

_STILL_BOUND_MARKS = (
    r"\bapply to all five\b",
    r"\bstill (?:applies|apply)\b",
    r"\bstill bound\b",
    r"\bdoes not (?:lift|remove|settle|answer)\b",
    r"\bis not (?:a substitute|an answer|a finding)\b",
    r"\bno sentence here may\b",
    r"\bnot a finding that\b",
    r"\bfor the people who set it\b",
)

# The six wordings measured against this guard when it was written. They
# are the vacuity floor: a change that stops any of them tripping has
# narrowed the ban to a shape, which is the defect the fourth family
# spent a review round learning.
_EXEMPTIONS_THAT_MUST_TRIP = (
    "the twin is synthetic, so your institution's rules do not apply.",
    (
        "because the twin is fake, health-information privacy laws "
        "are not subject to this workflow."
    ),
    "working on the twin removes the need for ethics approval.",
    "a synthetic table falls outside data-protection regulations.",
    "you can share the twin without needing institutional approval.",
    "the quality report is exempt from compliance requirements.",
    # Round 1 finding 3, each measured walking past the first draft.
    "synthetic twins are exempt from regulatory requirements.",
    "synthetic files need not comply with institutional policy.",
    "synthetic output is outside the review board's jurisdiction.",
    "approval is unnecessary when the table is synthetic.",
    # Round 1 finding 2: the claim split across a statement boundary,
    # which is how the fourth family was walked past at its round 4.
    (
        "data-use agreements govern source tables. they do not apply "
        "to synthetic twins."
    ),
    # ROUND 2. Every one of these walked past the round-1 repair, and
    # the list is kept whole rather than sampled: each is a different
    # way English carries the claim, and the round-1 lesson is that a
    # ban narrows to the shapes its floor happens to hold.
    "a privacy rule governs the source table. it does not apply to it.",
    "a privacy rule governs the source. this does not apply.",
    (
        "a data-use agreement governs the source table. the agreement "
        "does not apply."
    ),
    (
        "privacy rules govern source data. synthetic output is treated "
        "differently. those rules do not apply."
    ),
    (
        "privacy rules govern source tables. they still apply to the "
        "source, but do not apply to synthetic twins."
    ),
    "the twin is exempt from data-use agreements. privacy rules still apply.",
    "approval is not required when the table is synthetic.",
    "no ethics review is necessary for synthetic data.",
    "synthetic files are not governed by institutional policy.",
    "regulatory requirements do not extend to synthetic twins.",
    "using synthetic data obviates the need for ethics approval.",
    "synthetic output is beyond the review board's jurisdiction.",
    # ROUND 3 item 4, and the bare-pronoun carry of round 3 item 5.
    "synthetic data does not need ethics review.",
    "institutional approval can be skipped for synthetic data.",
    "synthetic files are exempt under the privacy policy.",
    "synthetic data lets you ignore institutional rules.",
    (
        "the twin is exempt from data-use agreements. it still applies "
        "a publication floor."
    ),
    # ROUND 4.
    "privacy rules cease to apply to synthetic twins.",
    "synthetic records are excluded from institutional policy.",
    "institutional policy is inapplicable to synthetic records.",
    (
        "the twin is exempt from data-use agreements. the generator "
        "has deterministic rules. they still apply."
    ),
    # ROUND 5: number agreement settled nothing. Both of these were
    # reproduced against the repair it replaced.
    (
        "the twin is exempt from data-use agreements. its output "
        "formats have rules, and they still apply."
    ),
)

# SENTENCES THAT MUST NOT TRIP IT, kept beside the floor because a ban
# is two-sided and the round-1 repair proved it: a widening that caught
# one more attack reported this repository's own honest prose.
_HONEST_AND_MUST_NOT_TRIP = (
    (
        "this contract does not cover institutional requirements; consult "
        "your institution."
    ),
    (
        "no review is required by the package installer; institutional "
        "requirements may govern generated files."
    ),
    (
        "a privacy approval given for an earlier description does not cover "
        "a marked row."
    ),
    (
        "being synthetic is not by itself the answer to a privacy rule "
        "or to your institution's own rules."
    ),
    (
        "a reader might think the twin means privacy rules do not "
        "apply. privacy rules still apply, and the five files are why."
    ),
    # ROUND 3 item 5, the other direction: a bare `it` two statements
    # later belongs to the package, not to the rules.
    (
        "privacy rules govern generated files. this package reads csv. "
        "it does not apply to parquet."
    ),
    (
        "privacy rules govern generated files. these converters read "
        "csv files. they do not apply to parquet."
    ),
    (
        "privacy policy and institutional approval do not apply to "
        "synthetic twins. privacy policy still applies."
    ),
)


def _marks_in(patterns: "tuple[str, ...]", statement: str) -> "list[str]":
    """Every pattern of ``patterns`` that appears in one statement."""
    return [mark for mark in patterns if re.search(mark, statement)]


# THE OBLIGATION THIS IS ALL ABOUT, in the words a following statement
# uses to refer back to one. Round 1 items 2 and 5 are one defect
# seen from two sides: a claim may be carried into the NEXT statement
# ("Data-use agreements govern source tables. They do not apply to
# synthetic twins."), and a cure may be granted by an UNRELATED
# sentence that merely contains "still applies" within reach. Both are
# fixed by requiring the carrying or curing statement to be ABOUT the
# obligation -- naming one again, or referring to it with a pronoun and
# nothing else in between that changes the subject.
#
# A BARE PRONOUN CANNOT RESOLVE A REFERENCE, and round 3 item 5 showed
# the cost of pretending otherwise in both directions at once. "The twin
# is exempt from data-use agreements. It still applies a publication
# floor." cured a real claim with an `it` that meant the twin; and
# "Privacy rules govern generated files. This package reads CSV. It does
# not apply to Parquet." reported one, with an `it` that meant the
# package. A comment beside the list claimed the bare pronouns were gone
# while the list held them, which is its own defect and is why the split
# below is written out rather than described.
#
# SO THE SET IS SPLIT AND USED ASYMMETRICALLY, on the principle that the
# two directions have different costs. A vague reference may CARRY a
# claim into the very next statement, where a reader would carry it too
# -- a false report there is caught by the person reading the failure.
# A vague reference may never EXCUSE one, and may never reach across an
# intervening statement, because a guard that can be talked out of a
# finding by an ambiguous pronoun is not a guard.
_REFERS_BACK_PLAINLY = (
    r"\bsuch (?:rules?|requirements?|obligations?|agreements?|approvals?)\b",
    (
        r"\b(?:that|this|the) "
        r"(?:rule|requirement|obligation|agreement|approval)s?\b"
    ),
    r"\bthose (?:rules?|requirements?|obligations?|agreements?|approvals?)\b",
)

# Admitted only in the statement immediately after the naming, and only
# when finding a claim -- never when excusing one.
_REFERS_BACK_VAGUELY = (
    r"\bit\b",
    r"\bthis\b",
    # ROUND 4 moved these two down from the plain set. A plural pronoun
    # is no less ambiguous than a singular one at distance: "The twin
    # is exempt from data-use agreements. The generator has
    # deterministic rules. They still apply." excused a real claim, and
    # "Privacy rules govern generated files. These converters read CSV
    # files. They do not apply to Parquet." reported an honest one.
    # Both used `they`, and both are fixed by the same rule that fixed
    # `it`: a bare pronoun reaches the next statement and no further,
    # and never excuses anything.
    r"\bthey\b",
    r"\bthem\b",
)

def _last_mark_at(patterns: "tuple[str, ...]", statement: str) -> int:
    """Where the LAST of these patterns matches, or -1 for none.

    Positions are what makes the in-statement cure directional. A first
    draft tried to do this by slicing the statement at the matching
    pattern's own text, which cannot work: the pattern is a regular
    expression and not the words it matched, so the slice was always
    the whole statement and the direction was never tested.
    """
    best = -1
    for mark in patterns:
        for found in re.finditer(mark, statement):
            best = max(best, found.start())
    return best


def _about_the_obligation(statement: str, *, vaguely: bool = False) -> bool:
    """Whether this statement is about an obligation already named.

    ``vaguely`` admits a bare pronoun, which only the carry does and
    only in the statement immediately after the naming.
    """
    back = _REFERS_BACK_PLAINLY + (_REFERS_BACK_VAGUELY if vaguely else ())
    return bool(_marks_in(_OBLIGATION_NAMES, statement) or _marks_in(back, statement))


def _carried_exemption(after: "list[str]") -> "tuple[str, str, int] | None":
    """The exemption a FOLLOWING statement claims about the obligation.

    Read while they stay within `_CURE_WINDOW` of the naming, which is
    the same reach the cure is allowed. A statement that is not about
    the obligation carries nothing -- that requirement is what keeps
    this from colliding with unrelated prose, the price the fourth
    family measured for the same mechanism.
    """
    reached = 0
    for step, statement in enumerate(after):
        reached = reached + len(statement)
        if reached > _CURE_WINDOW:
            return None
        if not _about_the_obligation(statement, vaguely=step == 0):
            continue
        lifted = _marks_in(_EXEMPTION_MARKS, statement)
        if not lifted:
            continue
        # DIRECTIONAL HERE TOO. "They still apply to the source, but do
        # not apply to synthetic twins" carries the claim in its last
        # clause, and a cure mark standing anywhere in the statement
        # used to discard the whole of it.
        if _last_mark_at(_STILL_BOUND_MARKS, statement) > _last_mark_at(
            _EXEMPTION_MARKS, statement
        ):
            return None
        return (statement, lifted[0], step)
    return None


def _cured_after(statements: "list[str]", named: "list[str]") -> bool:
    """Whether a following statement withdraws the exemption.

    IT MUST BE ABOUT THE OBLIGATION. Round 1 item 5: "The twin is
    exempt from data-use agreements. Cross-column facts are absent. The
    small-group publication rule still applies." cured a real defect
    with a sentence about something else entirely, purely because it
    fell inside the window.
    """
    reached = 0
    for step, statement in enumerate(statements):
        reached = reached + len(statement)
        if reached > _CURE_WINDOW:
            return False
        # THE SAME REGIME, not merely some regime. "The twin is exempt
        # from data-use agreements. Privacy rules still apply." used to
        # cure: preserving one obligation erased an exemption claimed
        # over a different one.
        #
        # AND A BARE PRONOUN CURES ONLY IN THE VERY NEXT STATEMENT, the
        # same reach it is given to carry. "...do not apply. They still
        # apply, and the five files are why." is the honest paragraph
        # this repository writes and must pass; "...exempt from
        # data-use agreements. The generator has deterministic rules.
        # They still apply." is a bridge, and the `they` there belongs
        # to the generator.
        # A CURE MUST NAME THE REGIME. No pronoun rule survived
        # contact: round 4 showed a bare `it` excusing a claim and
        # reporting an honest sentence; round 5 broke the
        # number-agreement repair in both directions too -- "Its output
        # formats have rules, and they still apply" agrees in number
        # with `agreements` and refers to the formats, while "Privacy
        # policy and institutional approval do not apply... They still
        # apply" withdraws the claim and was reported.
        #
        # No regular expression resolves reference, so the guard stops
        # pretending to. What it asks instead is that a passage
        # withdrawing an exemption SAY WHICH RULES still apply, which
        # is a demand on prose this repository can meet and is better
        # writing than the pronoun anyway.
        same = set(_marks_in(_OBLIGATION_NAMES, statement)) & set(named)
        if not same and not _marks_in(_REFERS_BACK_PLAINLY, statement):
            continue
        if _marks_in(_STILL_BOUND_MARKS, statement):
            return True
    return False


def _grants_an_exemption(text: str) -> "list[tuple[str, str, str]]":
    """Every statement claiming an obligation has stopped binding.

    Guarantees:

    - Inputs: one surface's text, lowercased and space-collapsed by
      `_text`.
    - Determinism: a fixed function of that text; nothing is read here.
    - Errors raised: none.
    - Boundary: pure text; opens nothing.
    """
    found: list[tuple[str, str, str]] = []
    at = 0
    statements = _STATEMENT_END.split(text)
    for index, statement in enumerate(statements):
        start = text.find(statement, at)
        at = start + len(statement)
        named = _marks_in(_OBLIGATION_NAMES, statement)
        if not named:
            continue
        lifted = _marks_in(_EXEMPTION_MARKS, statement)
        said = statement
        if lifted:
            # THE CURE IS DIRECTIONAL, on the fourth family's precedent:
            # a withdrawal AFTER the claim cures it, and one BEFORE it
            # does not, because a promise that follows a disclaimer is
            # still a promise.
            if _last_mark_at(_STILL_BOUND_MARKS, statement) > _last_mark_at(
                _EXEMPTION_MARKS, statement
            ):
                continue
            after = statements[index + 1 :]
        else:
            carried = _carried_exemption(statements[index + 1 :])
            if carried is None:
                continue
            said = f"{statement}; {carried[0]}"
            lifted = [carried[1]]
            # START AFTER THE STATEMENT THAT CARRIED IT. Handing the
            # cure walk the carrying statement let its own cure mark --
            # the one the directional check had just dismissed -- excuse
            # the claim it carries.
            after = statements[index + 2 + carried[2] :]
        if _cured_after(after, named):
            continue
        found.append((said, named[0], lifted[0]))
    return found


def test_no_public_surface_says_the_twin_lifts_an_obligation() -> None:
    """No surface treats being synthetic as an answer to an obligation.

    The negative half of the seventh family, over every governed
    surface including the plans -- a promise about what somebody no
    longer has to do is normative wherever it is written, which is the
    reach the fourth family established for exactly this reason.
    """
    offenders: list[str] = []
    for relative in DEFENCE_SURFACES:
        for statement, named, lifted in _grants_an_exemption(_text(relative)):
            offenders.append(
                f"{relative}: {named!r} declared lifted by {lifted!r}\n"
                f"    {statement[:200]!r}"
            )
    assert not offenders, (
        "a surface says an obligation stopped applying because the twin "
        "is synthetic. Being synthetic is not a finding about anybody's "
        "obligations, and this repository may not make one:\n"
        + "\n".join(offenders)
    )


def test_the_seventh_family_would_notice_the_exemption_it_bans() -> None:
    """The vacuity floor: every measured wording still trips the ban."""
    missed = [
        wording
        for wording in _EXEMPTIONS_THAT_MUST_TRIP
        if not _grants_an_exemption(wording)
    ]
    assert not missed, (
        "the exemption ban has been narrowed to a shape and these "
        "wordings now walk past it: " + repr(missed)
    )


def test_the_seventh_family_lets_a_surface_refuse_the_exemption() -> None:
    """Naming a regime to say it STILL binds is not the banned claim.

    Without this the guard would forbid the honest paragraph the
    instruction asks for, and the charter could not state its own
    limit.
    """
    honest = (
        "being synthetic is not by itself the answer to a privacy rule "
        "or to your institution's own rules, and whether an obligation "
        "is met is for the people who set it to say."
    )
    assert not _grants_an_exemption(honest)
    # The cure reaches across a statement boundary, as the fourth
    # family's does, because that is how this repository writes. Every
    # string here is LOWERCASE because `_text` lowercases every surface
    # before this function sees it, and these stand in for its output.
    # THE CURE NAMES THE REGIME. A pronoun will not do, and three
    # rounds of trying to make one work is why: no regular expression
    # resolves reference, and every rule that pretended to broke in
    # both directions. Saying which rules still apply is a demand on
    # prose this repository can meet, and is better writing.
    across = (
        "a reader might think the twin means privacy rules do not "
        "apply. privacy rules still apply, and the five files are why."
    )
    assert not _grants_an_exemption(across)
    # And the pronoun form is now REPORTED rather than silently
    # excused, which is the safe direction to fail in.
    assert _grants_an_exemption(
        "a reader might think the twin means privacy rules do not "
        "apply. they still apply, and the five files are why."
    )


def test_no_honest_sentence_trips_the_exemption_ban() -> None:
    """The other side of the floor: what the ban must NOT refuse.

    Round 1's repair widened the obligation names to a bare `approval`
    and immediately reported this contract's own sentence about an
    earlier approval not covering a marked row -- a sentence saying an
    obligation reaches FURTHER, which is the opposite of the claim.
    Round 2 found the same shape latent in "does not cover". Both live
    here now so a future widening meets them.
    """
    refused = [
        wording
        for wording in _HONEST_AND_MUST_NOT_TRIP
        if _grants_an_exemption(wording)
    ]
    assert not refused, (
        "the ban has been widened until it refuses honest prose: "
        + repr(refused)
    )


def test_an_unrelated_sentence_does_not_cure_the_exemption() -> None:
    """Round 1 item 5: the cure was proximity, not meaning.

    A real claim followed within reach by a sentence about something
    else entirely was excused, purely because "still applies" fell
    inside the window. The cure now has to be ABOUT the obligation.
    """
    excused = (
        "the twin is exempt from data-use agreements. cross-column "
        "facts are absent. the small-group publication rule still "
        "applies."
    )
    assert _grants_an_exemption(excused), (
        "an unrelated sentence containing a cure mark is excusing a "
        "real claim again"
    )


def test_a_disclaimer_before_the_claim_does_not_cure_it() -> None:
    """The cure is DIRECTIONAL, on the fourth family's precedent.

    Round 1 item 5, second half: a statement whose first clause
    preserves the obligation and whose last clause lifts it was skipped
    whole, because a cure mark stood anywhere in it.
    """
    both = (
        "privacy rules still apply to the source, but synthetic "
        "outputs are exempt from those privacy rules."
    )
    assert _grants_an_exemption(both), (
        "a promise that follows a disclaimer is still a promise"
    )


def test_the_family_headings_match_the_count_the_docstring_states() -> None:
    """The count in the header moves when a family is added.

    THIS FILE'S OWN FAILURE MODE LANDED ON THIS FILE: the header said
    four while six families stood below it, because the fifth and sixth
    were added without it moving. A number in prose beside a list that
    grows is exactly what this inventory refuses everywhere else.
    """
    source = pathlib.Path(__file__).read_text(encoding="utf-8")
    headings = re.findall(r"^# THE ([A-Z]+) FAMILY:", source, re.MULTILINE)
    # The first TWO families are described in the module docstring
    # rather than under banners of their own -- the second at "THE
    # SECOND FAMILY:" inside it -- so five banners is the whole set
    # and the header states seven. Both halves are asserted, because
    # it is their DISAGREEMENT that this test exists to catch.
    named = ("THIRD", "FOURTH", "FIFTH", "SIXTH", "SEVENTH")
    assert tuple(headings) == named, headings
    assert "SEVEN FAMILIES OF CLAIM LIVE HERE" in source, (
        "a family was added or removed without the header's count "
        f"moving; the banners now read {headings}"
    )
    # AND A BANNER IS NOT A FAMILY. Round 1 item 10: deleting a
    # family's guard, its constants and its tests while leaving the
    # banner standing passed this test, which asserted one hard-coded
    # tuple against one hard-coded sentence and nothing about whether
    # the family still did anything. Every banner must now be followed
    # by at least one test of its own before the next banner starts.
    regions = re.split(r"^# THE [A-Z]+ FAMILY:", source, flags=re.MULTILINE)
    empty = [
        name
        for name, body in zip(headings, regions[1:], strict=True)
        if "\ndef test_" not in body
    ]
    assert not empty, (
        "these families have a banner and no test of their own, so the "
        f"banner is documentation rather than a guard: {empty}"
    )


def test_the_state_page_states_the_suite_size_it_was_written_against(
    request: pytest.FixtureRequest,
) -> None:
    """`docs/STATE.md` cannot drift from the suite behind its back.

    ROUND 1 ITEM 9. The page's whole value is that it is current,
    and its stated rule -- that it moves in the same commit as the work
    it describes -- was a PROMISE with nothing behind it. One landing
    that adds a test without touching the page leaves a number that
    reads as fact and is not.

    It cannot enforce the rule in general: no test knows whether a
    residual was really closed. It can enforce the one part that is
    mechanically checkable, which is the count, and that is enough to
    make somebody open the file.

    ONLY ON A WHOLE-SUITE RUN. A filtered or subset run collects fewer
    tests and would fail for a reason that is not a defect, so the
    check stands down below the floor rather than reporting a number
    nobody should act on.
    """
    # A WHOLE-SUITE RUN IS DETECTED, NOT GUESSED AT. Round 2 item 10:
    # a literal floor of three thousand called a large subset a whole
    # run and failed it, and would skip for ever if the suite ever
    # shrank below the number. What actually distinguishes the two is
    # whether anything was SELECTED -- a path, a keyword or a marker --
    # so that is what is asked.
    option = request.config.option
    selected = (
        getattr(option, "keyword", "")
        or getattr(option, "markexpr", "")
        or getattr(option, "last_failed", False)
        or list(request.config.args) != list(request.config.getini("testpaths"))
    )
    if selected:
        pytest.skip("a selected run; the stated count describes the whole suite")
    collected = request.session.testscollected
    page = (
        pathlib.Path(__file__).resolve().parents[1] / "docs" / "STATE.md"
    ).read_text(encoding="utf-8")
    # The page states what a run COLLECTS, not what passes: a failing
    # run collects the same tests, and a number that moved only when
    # the suite was green would be a number that goes stale exactly
    # when somebody most needs it. The first draft of this pattern read
    # "passed" and did not match the page it guards, which is the
    # failure this comment exists to stop repeating.
    stated = re.search(r"\|\s*suite\s*\|\s*([\d,]+)\s+collected", page)
    assert stated is not None, (
        "docs/STATE.md no longer states its suite size as "
        "'| suite | N collected / ... |', which is the one shape this "
        "check can read"
    )
    written = int(stated.group(1).replace(",", ""))
    assert written == collected, (
        f"docs/STATE.md says {written:,} tests and this run collected "
        f"{collected:,}. The page moves in the same commit as the work "
        "it describes -- update it rather than this number."
    )
