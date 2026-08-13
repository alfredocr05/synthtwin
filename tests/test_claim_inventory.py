"""P2-D11: the repository-wide claim inventory, asserted rather than kept.

TWO FAMILIES OF CLAIM LIVE HERE. The first is the RECORD claim, and it
is what this file was written for; it is described immediately below.
The second arrived with review item P2-C1-F7 and is described under
"THE SECOND FAMILY" further down: what the twin CARRIES, which phase
the project is in, which commands exist, and how many libraries it
depends on. They share this file because they share a failure mode --
true text going stale on a surface nobody re-read -- and because a
reader who trusts one of these sentences has no way to tell which
family it came from.

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

WHAT IS DELIBERATELY OUT OF SCOPE. `docs/plans/` and its review record
are the project's audit trail: they record what was claimed, reviewed,
rejected and repaired at each date, and rewriting them to match today's
wording would destroy the very thing they exist to preserve. They make
no claim to a user. `tests/` is out for the same reason, plus the
obvious one that this file must be able to name the retired forms.

The failure messages here name the file and say what to write, because
whoever trips this test is mid-sentence in a document, not debugging.
"""

import pathlib

REPO_ROOT = pathlib.Path(__file__).resolve().parents[1]

# Every surface that speaks to a user, an auditor or a packaging index
# in synthtwin's own voice. The two spec documents are included because
# an institution's reviewer reads them as the normative statement of
# what the profile and the twin carry.
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
    "docs/spec/generation-method-v1.md",
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

# The handling rule has to name every artifact a run can produce, and
# the count moved from three to four when `synthtwin validate` shipped
# (plan P3-D3, P3-D7 stage 2): the quality report states measurements
# taken from the file it checked, so it is real-derived exactly as the
# profile, the twin and the twin's report are.
#
# Several phrasings are accepted, because the surfaces are written in
# several registers and forcing one sentence on all of them would make
# some of them read worse: the documents a person reads use articles;
# the normative contract lists the artifacts bare; and the files a run
# writes for a reader call the profile "the description", which is the
# word those files use for it throughout and the word a non-programmer
# recognizes. Every accepted form names every artifact of the run it is
# speaking about, which is the whole point, and none of them can be
# satisfied by naming the profile alone.
#
# THE THREE-ARTIFACT FORMS ARE STILL ACCEPTED, and that is deliberate
# rather than an unfinished migration. A surface speaking about what a
# PROFILE-AND-GENERATE run produces names three files and is telling the
# truth; the profile contract is such a surface, and it is a sealed
# document that no code change may rewrite in passing. What the rule
# keeps out is the lonely sentence -- the profile named as real-derived
# with the other files left unmentioned -- and every form here keeps it
# out.
ARTIFACT_HANDLING_FORMS = (
    "the profile, the twin, the twin's report and the quality report",
    "the profile, the twin, this report and the quality report",
    (
        "the description, the twin, the twin's report and the quality "
        "report"
    ),
    "the description, this twin, this report and the quality report",
    "the profile, the twin, the twin's report and this quality report",
    "the description, the twin, the twin's report and this quality report",
    "the profile, the twin and the report",
    "profile, twin and report",
    "the description, this twin and this report",
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
# 4. Without the three-artifact rule, naming only the profile reads as
#    permission for the twin and the report.
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
        ARTIFACT_HANDLING_FORMS,
        (
            "the handling rule naming every artifact of the run it "
            "describes, so that the institution's rules are not read as "
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
# `CLAIM_BEARING` plus two modules, for the reason the module docstring
# gives: `generation.py` is the code that makes columns independently,
# and the charter requires a module's docstring to state the guarantees
# it upholds.
#
# `validation.py` joined them when the validator shipped (plan P3-D7,
# stage 2), and its reason is the sharper one. A validator's silence is
# read as coverage: somebody holding a quality report that missed
# nothing will believe the file was checked for whatever they care
# about, and this version checks not one cross-column fact -- because
# the description publishes none. A module that measures obligations and
# does not say which obligations do not exist has left out the largest
# thing about itself.
STRUCTURE_BEARING = CLAIM_BEARING + (
    "src/synthtwin/generation.py",
    "src/synthtwin/validation.py",
)

# Where a person finds out which commands exist. Both command words are
# required on each, because naming one and not the other is how the
# front page came to describe an installed command as a future phase.
COMMAND_BEARING = (
    "CLAUDE.md",
    "README.md",
    "src/synthtwin/__init__.py",
    "src/synthtwin/cli.py",
)
# All three command words are required on each. `synthtwin validate`
# joined them when the validator shipped (plan P3-D7, stage 2): a
# surface that teaches two thirds of the workflow leaves a zero-code
# reader with no way to learn that the third command exists, which is
# exactly what the front page's old "[planned]" tag amounted to for
# `generate`.
COMMAND_WORDS = (
    "synthtwin profile",
    "synthtwin generate",
    "synthtwin validate",
)

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

    What the collapse deliberately does not do is remove quotes, commas
    or other punctuation, so a phrase split across two adjacent string
    literals in Python source still does not match. That is intended: a
    surface that has to state a claim states it in one readable piece.

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
    return " ".join(path.read_text(encoding="utf-8").lower().split())


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
    """Wherever a surface says the profile is real-derived, all three are.

    P2-D11 requires institutional handling to apply to the profile, the
    twin and the report. The failure mode is not a wrong sentence but a
    lonely one: a surface that names the profile as real-derived
    material and stops there tells a reader, by omission, that the other
    two files are free to move. So every surface that raises the subject
    at all must also carry the three-artifact phrase.
    """
    subject = "rules for real-derived material"
    silent: list[str] = []
    for relative in SURFACES:
        text = _text(relative)
        if subject not in text:
            continue
        if not any(form in text for form in ARTIFACT_HANDLING_FORMS):
            silent.append(relative)
    assert not silent, (
        "These surfaces state the institutional-handling rule but name "
        "only the profile:\n  "
        + "\n  ".join(silent)
        + "\n\nEvery artifact a full run produces -- the profile, the "
        "twin, the twin's report and the quality report -- carries facts "
        "computed from real data. Naming one of them and stopping reads "
        "as permission for the others. Add the sentence that names them "
        "all beside the rule."
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
