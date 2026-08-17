"""P2-D11: the repository-wide claim inventory, asserted rather than kept.

FOUR FAMILIES OF CLAIM LIVE HERE. The first is the RECORD claim, and it
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
making, which no surface may go on making for it. They share this file
because they share a failure mode -- true text going stale on a surface
nobody re-read -- and because a reader who trusts one of these
sentences has no way to tell which family it came from.

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
from synthtwin import cli, contract, profile, reading, summary, taxonomy

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
    "docs/plans/phase-2-generator.md",
    "docs/plans/phase-3-product.md",
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
    words = tuple(re.findall(r"'([a-z][a-z-]*)'", found.group(1)))
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
    ("CLAUDE.md", "the current phase is phase 3"),
    ("README.md", "status: early (phase 3"),
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
def _version_claim() -> "re.Pattern[str]":
    """The ban's pattern, built from whichever naming half is in force."""
    return re.compile(
        _WHO_IS_SYNTHTWIN
        + r"[^.!?\n]{0,140}?"
        + r"\b(?:writes?|writing|reads?|reading|emits?|produces?|accepts?)\b"
        + r"[^.!?\n]{0,60}?"
        + _naming_half(),
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
#                             `test_the_ban_catches_every_ordinary_...`.
_THE_STALE_OPENING = (
    "**Status: written before any code, which is this repository's "
    "standing process.** The shipped producer writes version 4 today "
    "and the shipped loader reads version 4 and nothing else."
)


def _subjectless_claim() -> "re.Pattern[str]":
    """The naming half alone, which is the ban drawn without a subject."""
    return re.compile(_naming_half(), re.IGNORECASE)


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
        return _version_claim().sub("(the wire sentence, deleted)", text)
    return text


def _claim_pattern() -> "re.Pattern[str]":
    """The ban's pattern, or the over-wide one a red check asks for."""
    if os.environ.get("REINSTATE") == "A-P3-30-wide":
        return _subjectless_claim()
    return _version_claim()


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
    pattern = _claim_pattern()
    stale: list[str] = []
    for relative in VERSION_SURFACES:
        text = _surface_text(relative)
        for found in pattern.finditer(text):
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
            for found in _claim_pattern().finditer(_surface_text(relative))
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

    THE LAST FOUR ARRIVED WITH THE WIDENING (review item P3-V9-F8). The
    naming half now reads a bare `v4`, and this repository is full of
    document names, clause numbers and release strings that hold a `v`
    next to a digit. Each of those is written out here, so a future
    narrowing of the two exclusions has to face them.
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
    )
    caught = [
        sentence
        for sentence in permitted
        if _claim_pattern().search(sentence) is not None
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
    missed = []
    for sentence in bypasses:
        found = _claim_pattern().search(sentence)
        if found is None or int(found.group("number")) == shipped:
            missed.append(sentence)
    assert not missed, (
        "These sentences claim synthtwin speaks a version it does not, "
        "and the ban walks past every one of them:\n  "
        + "\n  ".join(missed)
        + "\n\nWiden `_NAMES_A_VERSION`. A ban that catches one "
        "spelling of what it forbids reports a clean tree."
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
# round. A denial carried further than `_RETENTION_CARRY`, and a denial
# built from none of the verbs below, are both still missed. The naming
# half is a composition and not a phrase list, but the value NOUNS it
# composes over are finite, and no finite list is sound.
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

# THE DENIAL. Every verb this repository has used for a thing not
# reaching a file, plus the two that are about keeping rather than
# writing -- the retired summary sentence was about keeping.
_NOT_KEPT = (
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


def _unscoped_denials_in(sentence: str) -> "list[str]":
    """Every denial in one statement that names no place it holds in."""
    loose: list[str] = []
    for mark in _NOT_KEPT:
        for found in re.finditer(mark, sentence):
            if _scope_of(sentence, found) is None:
                loose.append(found.group(0))
    return loose


def _names_your_word(sentence: str) -> "str | None":
    """How this sentence names the value the person typed, or None."""
    for mark in _YOURS + _NOT_OURS:
        if re.search(mark, sentence) is not None:
            return mark
    return None


def _denies_retention(text: str) -> "list[tuple[str, str, str]]":
    """Every sentence of one surface that denies what version 5 keeps.

    Returns the sentence, the wording that named the person's own typed
    value, and the denial left without a scope -- so a failure message
    shows a maintainer which two collided rather than telling them a
    document is wrong somewhere.

    Guarantees:

    - Inputs: one surface's text, lowercased and space-collapsed by
      `_text`.
    - Determinism: a fixed function of that text and of the derived
      clean places; nothing is read here.
    - Errors raised: none.
    - Boundary: pure text; opens nothing.
    """
    found: list[tuple[str, str, str]] = []
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
            found.append((said, named, loose[0]))
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
#                              run-driven measurement.
_THE_RETIRED_CLOSE = (
    " for any other word you typed, keep a note of the command you ran; "
    "synthtwin will not keep one for you."
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
        for sentence, named, denied in _denies_retention(_text(relative)):
            offenders.append(
                f"{relative}: {named!r} denied by {denied!r}\n"
                f"      {sentence[:300]}"
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


# The sentences this guard has to catch, kept as its own red cases. The
# first five are what shipped, in the five wordings they shipped in; the
# rest are shapes a review would write to walk through a narrower ban --
# a paraphrase using none of those verbs, the possessive form, and the
# denial split across a full stop.
DENIALS_THAT_SHIPPED = (
    (
        "the summary's closing sentence, split across a semicolon",
        (
            "For any other word you typed, keep a note of the command "
            "you ran; synthtwin will not keep one for you."
        ),
    ),
    (
        "the summary's opening claim, scoped and then unscoped in one breath",
        (
            "A word of YOUR OWN is not written into its settings, and it "
            "is not written here."
        ),
    ),
    (
        "the security document's reason clause",
        (
            "The word guessed at can never be a name, a code, a diagnosis "
            "or a free-text answer, because a value outside that list is "
            "written nowhere at all."
        ),
    ),
    (
        "the security document's what-is-not-relaxed",
        (
            "A declared value that is not one of the thirteen is still "
            "recorded nowhere."
        ),
    ),
    (
        "the contract's own invariant",
        "A declared value that is neither is written nowhere.",
    ),
    (
        "the contract's what-a-reader-can-infer",
        (
            "It can never be a name, a code, a diagnosis or a free-text "
            "answer, because a value outside the list is never written."
        ),
    ),
    (
        "the plan's description of its own test",
        (
            "It checks that a word which is nobody's but the person's is "
            "written nowhere."
        ),
    ),
    (
        "a paraphrase using none of those verbs",
        "Any marker you type is never stored by synthtwin.",
    ),
    (
        "the denial split across a full stop",
        (
            "You may name a word of your own after --missing-value. It is "
            "never written."
        ),
    ),
)


@pytest.mark.parametrize("shape,passage", DENIALS_THAT_SHIPPED)
def test_the_sixth_family_would_notice_the_assurance_it_replaced(
    shape: str, passage: str
) -> None:
    """Each false sentence is one this guard now reports.

    Run against `_denies_retention` directly rather than against a file,
    because what is held here is the RULE and not any surface's current
    wording.
    """
    found = _denies_retention(" ".join(passage.lower().split()))
    assert found, (
        f"this sentence denies what the description keeps -- {shape} -- "
        f"and the guard reported nothing:\n  {passage}"
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


def test_the_derivation_reads_the_producer_and_not_a_list() -> None:
    """The two derived sets are what the family is checked against.

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
