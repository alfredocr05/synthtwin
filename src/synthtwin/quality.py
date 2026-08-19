"""The quality report: what a check measured, in words (V7, plan P3-D3).

The fourth artifact. `validation.measure` produces verdicts; this turns
one `validation.Outcome` into the file a person reads and the text the
command prints. It is one module rather than a section of `rendering.py`
for a boundary reason, stated here because it looks like an arbitrary
split and is not: `rendering.py` imports the generation module, and the
generation module imports a random number generator. The Phase 3 plan
(P3-D1) makes two promises about a `validate` run -- that it never
imports the generator, whose planning defects a second opinion may not
inherit, and that it consumes no randomness. A quality report living in
`rendering.py` would break both the moment the command imported it. So
the twin's two artifacts are rendered there and the check's one artifact
is rendered here, and each module imports only what its own command may
reach.

WHAT THE SECOND PROMISE DOES AND DOES NOT SAY (amendment A-P3-4, review
item P3-V2-F-F2). It used to be written here as "no random source is in
its closure at all", and that sentence was false. A validate run must
read a CSV, reading a CSV means pandas, and pandas imports numpy, which
brings `numpy.random` into the process -- a live `default_rng` is
reachable by attribute from this very module. What is true, and what is
enforced, is narrower and is the property the report's bytes actually
depend on: no module of this package on the validate path imports a
random source, and a validate run DRAWS from none. The second half is
not a hope; `tests/test_cli_validate.py` traps every door in the
process and runs the whole command at them.

WHAT THE SUMMARY MAY SAY, AND WHAT NO WORDING HERE CAN SAY (V7.2). The
summary is generated FROM THE CENSUS ALONE -- five verdict counts and
the number of obligations no CSV can evidence. There is no sentence of
the form "every published fact was found", and none can be written from
these counts: on a description with authorized corners or approximated
facts it would be false by construction. A pass means exactly one thing
-- no checkable obligation was missed -- and the other counts stand
BESIDE it rather than being folded into it.

WHAT NEVER REACHES THIS MODULE. A string read from the measured file.
`validation` guarantees that no field of any result holds one, so every
name printed here is either the description's own published text or the
measured file's NAME off the command line, and every other word is fixed
by this module or by that one. Nothing here opens a file, and nothing
here knows a PATH: the outcome carries the last component of the name
the person typed and no folder above it, so the report says which file
it is about (V7.1) and the same check still writes the same bytes
wherever its file is put (V10).

The name is here because the report used to say "It is a report about
ONE file" and never say which, while its own file name came from the
DESCRIPTION -- so measuring `tampered.csv` wrote `clinic-twin-quality.txt`,
beside the twin, naming the twin, about neither (review item P3-V2-G).

THE DISPLAY BOUNDARY (contract 13.5). Every interpolated string passes
`parsing.visible` ONCE, on its way into a line -- a published label out
of somebody's table can carry an escape sequence, and this file is
opened in a terminal as often as in an editor. The caller puts the
finished text through `parsing.visible_lines` on its way to the screen
and to disk, exactly as the twin's report is treated.

Imports here stay within the allowlist (plan D6.2): this module imports
only from this package, and only modules that reach the generator
through no route and import a random source in none of their own
source. `validation` reaches `reading` and `reading` reaches pandas, so
`numpy.random` is in the process by way of this module's own imports;
what no module in that chain does is ask it for a number.
"""

from synthtwin import contract, parsing, validation

_RULE = "=" * 66
_NEWLINE = "\n"

# What each verdict is called in the report, and the one-line gloss that
# says what it means. The words a person reads live beside each other so
# that no two sections can drift into calling one verdict two things.
_VERDICT_WORDS = {
    validation.HELD: "the exact obligation was met",
    validation.WITHIN_BOUND: "inside the window this method states",
    validation.AUTHORIZED_DEVIATION: (
        "a lesser outcome the plan authorizes here"
    ),
    # NOT "measured, and not shown" (review item P3-V2-E-F6). That gloss
    # was true of one class of withholding and false of the others, and
    # the class it was true of is gone: the presence-split withholds it
    # was written for are measurements now (amendment V2.4-A1). What is
    # true of every withheld line is that nothing is shown and the line
    # says why, so that is what the word says. The per-line citation
    # carries the reason, and the section further down names both.
    #
    # IT IS A LEGEND AND IS WORDED AS ONE (review of the shipped
    # reports, 2026-08-15). "not shown -- the line below says why"
    # printed beside a count of 0 sends a reader down the page after
    # lines that are not there. What the word means is a fact about the
    # vocabulary and not about this run; the count beside it is the
    # fact about this run.
    validation.WITHHELD: "not shown -- such a line says why",
    validation.MISSED: "set by the description, not met by this file",
}

# The order the census is printed in, which is also the order the five
# verdicts are explained in. MISSED is last because it is the one the
# summary sentence above the table has already stated.
_CENSUS_ORDER = (
    validation.HELD,
    validation.WITHIN_BOUND,
    validation.AUTHORIZED_DEVIATION,
    validation.WITHHELD,
    validation.MISSED,
)


def _shown(value: object) -> str:
    """One value out of a description, safe to put into the report.

    The same boundary the twin's report keeps: a published label, a
    column name or a recorded sentence came out of somebody's table and
    can carry an escape sequence. Nothing that reaches here came out of
    the MEASURED file -- `validation` never puts such a string in a
    result -- so this is the description's own text and this module's
    own words, and both pass the boundary the same way.
    """
    return parsing.visible(f"{value}")


def _counted(census: validation.Census) -> "dict[str, int]":
    """The five verdict counts, keyed by verdict."""
    return {
        validation.HELD: census.held,
        validation.WITHIN_BOUND: census.within_bound,
        validation.AUTHORIZED_DEVIATION: census.authorized_deviation,
        validation.WITHHELD: census.withheld,
        validation.MISSED: census.missed,
    }


def checkable_total(census: validation.Census) -> int:
    """How many obligations were checkable, as the five counts add up.

    Guarantees:

    - Inputs: one census. Nothing is read and nothing is written.
    - Determinism: a sum of five whole numbers.
    - Errors raised: none.
    - Boundary: this is the identity the report prints and a test walks
      -- checkable subchecks equal the five verdict counts added
      together, with the not-checkable listings counted separately and
      never inside it. A verdict that fell out of the census on its way
      to a page would show up here as a total that does not add up.
    """
    counted = _counted(census)
    total = 0
    for verdict in _CENSUS_ORDER:
        total = total + counted[verdict]
    return total


def _opening_lines(
    description: contract.Profile, measured_name: str
) -> "list[str]":
    """What this file is and which file it is about, before any count.

    THE NAME COMES FIRST FOR A REASON (review item P3-V2-G). This report
    used to say "It is a report about ONE file" and then never say
    which. Its own file name was built from the DESCRIPTION's name, so
    measuring `tampered.csv` against `clinic-profile.json` wrote
    `clinic-twin-quality.txt`, whose bytes contained the word `tampered`
    nowhere at all: a report named after the twin, sitting beside the
    twin, about a different file, with nothing in it that let a reader
    tell. Which file was measured is also the one fact about the run
    that a reader cannot recover from anywhere else once the shell
    scrollback is gone -- the description is named by the file's own
    name, the verdicts are in the body, and the measured file existed
    only in the command line.
    """
    return [
        _RULE,
        "synthtwin: how one file measured up to a description",
        _RULE,
        "",
        f"THE FILE MEASURED: {_shown(measured_name)}",
        "",
        "synthtwin read a description and that one CSV file, described",
        "the file again with the same rules the description was made",
        "with, and compared the two. This report is what it found.",
        "",
        "It is a report about THAT ONE file and no other. The name above",
        "is the name the file was given on the command line; where it",
        "sits is not recorded here, so this report says the same thing",
        "wherever it is kept. synthtwin was not told, and has no way of",
        "telling, whether the file it measured is the twin built from",
        "this description, some other synthetic file, or a real table:",
        "nothing in a CSV proves where its rows came from.",
        "",
        (
            f"The description publishes "
            f"{len(description.columns)} column(s) and "
            f"{description.n_rows} row(s)."
        ),
    ]


def _lowered_floor_lines(description: contract.Profile) -> "list[str]":
    """Said only where the description was made under a lowered floor.

    THIS REPORT IS ONE OF THE FOUR THAT MUST SAY IT, and it is the one
    with a second duty (owner ruling 2026-08-14, plan amendment
    A-P3-11). The other three say what the description publishes. This
    one says what THIS FILE was measured to hold, group by group, and
    the number it may print down to is the description's own floor -- so
    lowering that floor turns `synthtwin validate` into a second place
    the small counts appear, in a file whose whole purpose is to be
    forwarded to somebody who is deciding whether to trust a twin.
    Saying so is the difference between a consequence taken and a
    consequence discovered.

    IT IS CONDITIONAL, unlike the four bounds under "what this report
    does not say". Those are true of every run and are printed on every
    run so that nobody comes to expect their absence. This is a fact
    about ONE description, false of an ordinary one, and a paragraph
    that appears on every run saying the floor was NOT lowered is how a
    reader is trained to skip the paragraph that matters.

    AND THE FLOOR-OF-ONE PARAGRAPH SAYS WHICH KIND OF WITHHOLDING IT IS
    TALKING ABOUT (review item P3-V5-F1, plan amendment A-P3-16 clause
    3). It read "At 1 nothing is withheld at all: every count this
    description carries is named exactly, and every line below that
    would have read WITHHELD carries its number instead." Both halves
    are false, and measurably: a floor-of-one
    description checked against a file whose columns hold words where it
    publishes numbers printed that sentence and then eighty-three
    obligation lines reading WITHHELD, with "83 WITHHELD" in the verdict
    summary fourteen lines further down. Two rules put a line there and
    only one of them is the floor's -- `_floor_gate_lines` below has
    said so correctly all along, in the words "nothing is held back this
    way" -- so this paragraph now says the same bounded thing and names
    the other rule rather than promising it away.

    Guarantees:

    - Inputs: the description this check was run against. Nothing else.
    - Determinism: a fixed function of one number in it.
    - Errors raised: none.
    - Boundary: no value of any table reaches it; it names counts.
    """
    floor = description.settings.small_cell_floor
    if floor >= contract.DEFAULT_SMALL_CELL_FLOOR:
        return []
    usual = contract.DEFAULT_SMALL_CELL_FLOOR
    lines = [
        _RULE,
        (
            f"THIS DESCRIPTION WAS MADE WITH THE SMALLEST GROUP SIZE "
            f"LOWERED TO {floor}"
        ),
        _RULE,
        "",
        (
            f"synthtwin normally publishes a value only where at least "
            f"{usual} rows"
        ),
        "of the real table shared it. This description publishes values as",
        f"few as {floor} row(s) shared, and prints how many rows that is.",
        "",
    ]
    # "a group of 1 is 1 people" is not English, so at a floor of one the
    # sentence is the one that is true there rather than the general one
    # with a bad number in it.
    if floor < 2:
        lines = lines + [
            "A published group can be a single row. If one row of the real",
            "table is one person, this description says out loud that exactly",
            "one person -- on their own -- had that value.",
            "",
        ]
    else:
        lines = lines + [
            f"If one row of the real table is one person, a group of {floor}",
            f"is {floor} people.",
            "",
        ]
    lines = lines + [
        "READ WHAT THAT DOES TO THIS REPORT, because it is not only the",
        "description that carries the small counts now. The rule further",
        "down decides what may be shown by asking what a description of",
        "the measured file would publish about it -- and under a floor of",
        f"{floor} such a description names groups of {floor}. So the",
        "obligation lines below print published counts and measured counts",
        f"down to {floor} row(s), where at {usual} they would have been",
        "withheld. This report is forwarded more often than the",
        "description is: it goes to whoever is deciding whether to trust a",
        "file, and it carries those counts with it.",
        "",
    ]
    if floor < 2:
        lines = lines + [
            "At 1 nothing is held back FOR BEING A SMALL GROUP: every count",
            "this description carries is named exactly, and no line below",
            "reads WITHHELD for that reason. Lines below may still read",
            "WITHHELD for the other reason -- that describing the checked",
            "file publishes no measurement of that kind at all -- which is",
            "a fact about that file and not about the floor. The count of",
            "them stands in THE VERDICT.",
            "",
        ]
    return lines + [
        "What that can mean for a person: somebody who already knows one",
        "true thing about someone in the real table -- that they are in it",
        "at all -- can find the small group that person must be in and read",
        "off everything else these two files say about that group. That is",
        f"what the usual {usual} prevents and what this description does",
        "not. Whoever approves data leaving your environment should be told",
        "this before this report moves.",
        "",
    ]


def _summary_lines(census: validation.Census) -> "list[str]":
    """The verdict summary, generated from the census and nothing else.

    V7.2. Every sentence here is a function of six whole numbers. There
    is deliberately no wording available for "every published fact was
    found": a description with an authorized corner or an approximated
    fact makes that sentence false by construction, and the way to keep
    it out of a report is to leave it unwritable rather than to remember
    not to write it.
    """
    counted = _counted(census)
    total = checkable_total(census)
    lines = [
        _RULE,
        "THE VERDICT",
        _RULE,
        "",
        (
            f"This description sets {total} obligation(s) that a written "
            f"file can be"
        ),
        "checked against. Each one landed on exactly one of five outcomes:",
        "",
    ]
    for verdict in _CENSUS_ORDER:
        lines = lines + [
            (
                f"  {counted[verdict]:>6}  {_shown(verdict)} -- "
                f"{_VERDICT_WORDS[verdict]}"
            )
        ]
    lines = lines + [
        "",
        (
            f"Those five numbers add to {total}, which is every obligation "
            f"this"
        ),
        "description sets that a file can be measured against.",
        "",
        (
            f"A further {census.not_checkable} obligation(s) are NOT "
            f"CHECKABLE from a CSV at"
        ),
        "all. They carry no verdict, they are not part of the count above,",
        "and every one of them is listed further down with the reason.",
        "",
    ]
    if census.missed == 0:
        lines = lines + [
            "NO CHECKABLE OBLIGATION WAS MISSED.",
            "",
            "That sentence is the whole of what this report concludes, and",
            "it is worth reading for what it leaves out. It is not a",
            "statement that this file carries everything the description",
            "publishes: the four counts above stand BESIDE it and are",
            "never folded into it.",
            "",
            (
                f"  {census.within_bound} obligation(s) landed inside a "
                f"stated window rather than"
            ),
            "  on the published value.",
            (
                f"  {census.authorized_deviation} took a lesser outcome "
                f"the ratified plan names for"
            ),
            "  this description.",
            f"  {census.withheld} were withheld.",
            f"  {census.not_checkable} could not be checked at all.",
        ]
    else:
        lines = lines + [
            f"{census.missed} CHECKABLE OBLIGATION(S) WERE MISSED.",
            "",
            "Each one is named first in the section below, with what the",
            "description asks for, and with what the file was found to",
            "hold or the reason that may not be printed here. A missed",
            "obligation is a fact the description publishes that this",
            "file does not carry; it is not a judgement about whether the",
            "file is useful for anything.",
        ]
    return lines


def _bounds_lines() -> "list[str]":
    """The limits this report carries on every run (V7.3).

    None of these is conditional on what was measured. A limit that
    appears only sometimes is a limit nobody comes to expect, which is
    the reasoning the twin's own report is written under.

    The load-bearing phrases are the same ones the charter, `README.md`,
    `SECURITY.md`, the package docstring, the command's status screen,
    the profiler's summary and the twin's report use, and
    `tests/test_claim_inventory.py` holds all of them to it.
    """
    return [
        _RULE,
        "WHAT THIS REPORT DOES NOT SAY",
        _RULE,
        "",
        "1. NO CROSS-COLUMN STRUCTURE WAS VALIDATED, because none is",
        "   carried. This version of synthtwin describes and builds every",
        "   column on its own and carries",
        "   no cross-column structure at all: no fact about how two",
        "   columns move together, so there is nothing of the kind for a",
        "   check to measure -- not a correlation, not a formula tying one",
        "   column to another, not a shared pattern of which cells are",
        "   empty, not an ordering between two event columns. A file that",
        "   passes every check in this report can still behave nothing",
        "   like your table under any analysis that uses two columns at",
        "   once.",
        "   Cross-column structure arrives in a later version of synthtwin.",
        "",
        "2. ROWS ARE TREATED AS INDEPENDENT, and this description",
        "   never says what one row of the real table is. Nothing here",
        "   checks anything about groups of rows -- rows per person, per",
        "   visit, per site -- because the description carries no such",
        "   fact.",
        "",
        "3. NUMBERS COMPUTED ON THE TWIN ARE NOT RESEARCH RESULTS. Develop",
        "   your analysis against a twin, then run the finished analysis on",
        "   your real table, inside the environment that holds it. That is",
        "   as true of a file that passed every check as of one that did",
        "   not.",
        "",
        "4. WHAT A PASS MEANS, exactly. A passing report means no checkable",
        "   obligation was missed -- with the within-window, lesser-outcome,",
        "   withheld and not-checkable counts standing beside it. It is not",
        "   a verdict that the file is fit for any analysis; it validates",
        "   nothing this description does not publish; and it cannot tell a",
        "   synthetic file from a real one, because nothing in a CSV proves",
        "   where its rows came from.",
    ]


def _where(check: validation.Check) -> str:
    """Which column an obligation belongs to, in the report's words."""
    if not check.column:
        return "the file as a whole"
    return f"'{_shown(check.column)}'"


def _detail_of(check: validation.Check) -> "list[str]":
    """One obligation, its verdict, and whatever may be shown beside it.

    ``published`` and ``achieved`` are empty wherever the disclosure gate
    closed over the check or wherever there was never anything to show,
    and an empty field simply does not print: a line reading "the file
    holds:" with nothing after it invites the reader to think something
    was lost.

    THAT IS RIGHT FOR EVERY VERDICT BUT ONE (review item P3-V12-F2
    clause (a); amendment A-P3-45). Under MISSED an absent found line
    is not restraint, it is a page telling a researcher that their file
    failed and refusing to say what it holds -- measured on a table of
    sixty readings written to two decimal places, checked against its
    own genuine description, which printed `styles.spelled ... MISSED`
    and one line under it. So a MISSED check carries either the found
    value or a note saying which rule keeps it back, `validation` fills
    that note and floors it, and the two sentences above this section
    promise exactly that and no longer more.

    THE CITATION FIELD IS THREE DIFFERENT THINGS and is introduced as
    whichever one it is. On an authorized deviation it is the passage
    that authorizes the lesser outcome; on a within-bound verdict it is
    the document the window was taken from; on a withheld one it is the
    sentence saying why neither the measurement nor its outcome is
    shown. Calling all three "the authority" would tell a reader that a
    withholding had been authorized by somebody, which is not what
    happened.

    ``note`` is the last line and is the check's own sentence about
    what its window means -- printed under the citation because it is
    read after the reader knows where the window came from.
    """
    lines = [
        (
            f"  {_shown(check.subcheck)} [{_shown(check.fact)}]: "
            f"{_shown(check.verdict)}"
        )
    ]
    if check.published:
        lines = lines + [
            f"      the description asks for: {_shown(check.published)}"
        ]
    if check.achieved:
        lines = lines + [
            f"      the file was found to hold: {_shown(check.achieved)}"
        ]
    if check.citation:
        opening = "on the authority of"
        if check.verdict == validation.WITHIN_BOUND:
            opening = "the window comes from"
        if check.verdict == validation.WITHHELD:
            opening = "why nothing is shown"
        lines = lines + [f"      {opening}: {_shown(check.citation)}"]
    return lines + _note_lines(check)


def _note_lines(check: validation.Check) -> "list[str]":
    """The check's own further lines, already broken where they break."""
    lines: list[str] = []
    for note in check.note:
        lines = lines + [_shown(note)]
    return lines


def _missed_lines(outcome: validation.Outcome) -> "list[str]":
    """Every missed obligation, first in the detail (plan P3-D2)."""
    missed = [
        check for check in outcome.checks if check.verdict == validation.MISSED
    ]
    if not missed:
        return [
            "Nothing was missed, so this part of the section is empty. Every",
            "obligation and its outcome is listed under it, column by column.",
            "",
        ]
    lines = [
        "WHAT THIS FILE DOES NOT CARRY. Each line names one obligation the",
        "description sets, what it asks for, and what the file holds --",
        "or, where what the file holds may not be printed here, why.",
        "",
    ]
    for check in missed:
        lines = lines + [f"{_where(check)}"] + _detail_of(check) + [""]
    return lines


def _column_order(outcome: validation.Outcome) -> "list[str]":
    """The columns that carry a check, in the order the checks arrive.

    The order is the description's own -- `validation.measure` walks the
    document-level obligations first and then the columns as the schema
    lists them -- so it is read off the checks rather than sorted, which
    would put a report's sections in an order the description never
    used.
    """
    seen: list[str] = []
    for check in outcome.checks:
        if check.column not in seen:
            seen = seen + [check.column]
    return seen


def _detail_lines(outcome: validation.Outcome) -> "list[str]":
    """The fact-by-fact detail: every obligation, with its outcome."""
    lines = [
        _RULE,
        "FACT BY FACT",
        _RULE,
        "",
    ]
    lines = lines + _missed_lines(outcome)
    lines = lines + [
        "EVERY OBLIGATION, IN THE DESCRIPTION'S OWN ORDER.",
        "",
    ]
    for column in _column_order(outcome):
        heading = "the file as a whole"
        if column:
            heading = f"'{_shown(column)}'"
        lines = lines + [heading]
        for check in outcome.checks:
            if check.column != column:
                continue
            lines = lines + _detail_of(check)
        lines = lines + [""]
    return lines


# What each REPORT-ONLY obligation IS, in the words a report may use.
#
# A REPORT-ONLY fact has no finer grain to name, so its listing entry
# carries no subcheck, and the line printed the registry identifier on
# its own: "'seen_on' -- universal.n_sentinel_candidates_unpublished",
# under a heading promising to name what could not be checked, in a
# report whose every verdict line above it leads with a readable name
# (review of the shipped reports, 2026-08-15). Charter principle 2 asks
# every message to be written for a human, and a dotted field path out
# of a machine-readable format is not one. The identifier stays, in
# brackets, so a reader with the contract in front of them can still
# look the fact up.
#
# The table is total over the REPORT-ONLY facts by test rather than by
# hope: `_listing_name` returns "" for a fact it does not know, and the
# suite asserts that no line of any battery's report prints one.
_LISTING_WORDS = {
    "document.source.encoding": "how your table's bytes were read",
    "document.source.used_fallback_encoding": (
        "whether reading your table fell back to a second encoding"
    ),
    "document.source.header_by_convention": (
        "whether the first row was taken as the column names by "
        "convention"
    ),
    "document.source.header_evidence": (
        "what showed the first row of your table to be column names"
    ),
    "universal.missing_by_class": (
        "why each absent cell of your column was counted absent"
    ),
    "universal.missing_by_source": (
        "the spellings the absent cells of your column wore"
    ),
    "universal.n_missing_blank": (
        "how many absent cells of your column had nothing written in "
        "them"
    ),
    "universal.n_missing_withheld": (
        "how many absent cells of your column wore a spelling too few "
        "rows shared for the description to name"
    ),
    "universal.n_sentinel_candidates_unpublished": (
        "how many stand-in numbers were too rare for the description to "
        "name"
    ),
    "universal.sentinel_verdicts": (
        "what was decided about each stand-in number, and why"
    ),
    "universal.detection_evidence": (
        "why your column was read as this kind of column"
    ),
    "universal.remarks": (
        "the remarks the description records about your column"
    ),
    "datetime.format": (
        "the date spelling your column was written in"
    ),
}


def _listing_name(listing: validation.Listing) -> str:
    """What one not-checkable obligation is called on the page.

    The subcheck where the obligation has one -- the same identity the
    verdict lines carry, so a reader comparing this census with an
    ordinary run's sees one obligation named one way. Otherwise the
    plain words above. "" where neither exists, which is what the
    suite refuses.
    """
    if listing.subcheck:
        return listing.subcheck
    if listing.fact in _LISTING_WORDS:
        return _LISTING_WORDS[listing.fact]
    return ""


def _not_checkable_lines(outcome: validation.Outcome) -> "list[str]":
    """The census of obligations no CSV can evidence, and why (V3.3).

    These carry no verdict and are never counted toward a pass. Their
    failure mode is this list: a line missing from it is an obligation
    the report quietly stopped mentioning, so the report's exact-shape
    tests hold the list to its length.

    EVERY LINE NAMES ITS OBLIGATION IN WORDS, with the registry
    identifier beside it in brackets -- the same two-part shape every
    verdict line above carries. `_LISTING_WORDS` says why.
    """
    lines = [
        _RULE,
        "WHAT COULD NOT BE CHECKED, AND WHY",
        _RULE,
        "",
        "These are obligations the description sets that no written CSV can",
        "evidence either way. They are not failures and they are not",
        "passes: they are counted on their own line of the verdict above",
        "and named here so that silence never reads as a pass.",
        "",
    ]
    if not outcome.listings:
        return lines + [
            "On this description there are none: every obligation it sets",
            "could be measured against the file.",
        ]
    for listing in outcome.listings:
        where = "the file as a whole"
        if listing.column:
            where = f"'{_shown(listing.column)}'"
        named = _shown(listing.fact)
        words = _listing_name(listing)
        if words:
            named = f"{_shown(words)} [{named}]"
        lines = lines + [
            f"  {where} -- {named}",
            f"      {_shown(listing.reason)}",
        ]
    return lines


def _expectations_lines() -> "list[str]":
    """The analyst-expectations section (V7.4).

    One fixed section answering the question a methodologist brings:
    which of the checks I care about does this report perform? It
    promises nothing about later versions -- no version number, no slot,
    no date -- because a promise about unbuilt work is exactly the kind
    of sentence this project's claim inventory exists to keep out.
    """
    return [
        _RULE,
        "IF YOU CAME TO THIS REPORT WITH A QUESTION",
        _RULE,
        "",
        "CHECKED IN THIS VERSION, one column at a time:",
        "",
        "  * the share of each published label, against the count the",
        "    description publishes for it;",
        "  * where a column's values sit along its distribution ladder --",
        "    the smallest and largest exactly, the nine steps between them",
        "    against the window this method states for each;",
        "  * spread and shape summaries, against their stated windows;",
        "  * how many cells are empty and how many hold a value;",
        "  * value-format read-back: that the file writes its numbers,",
        "    dates and times in the forms the description publishes, so",
        "    that reading the file back gives the same kinds of column.",
        "",
        "NOT CHECKABLE IN THIS VERSION, and named rather than left out:",
        "",
        "  * any target that ties two columns together -- a rate within a",
        "    subgroup defined by another column, a model coefficient, a",
        "    time-to-event structure, agreement between a prediction",
        "    column and an outcome column;",
        "  * any target about how rows group -- per person, per visit, per",
        "    site.",
        "",
        "Both of those need cross-column structure that this version of",
        "synthtwin deliberately does not carry: the description publishes",
        "none, so there is nothing for a check to measure against. Carrying",
        "them is later work with its own plan and its own change to what a",
        "description publishes. Nothing here promises when.",
    ]


def _floor_gate_lines(floor: int) -> "list[str]":
    """The second way a line is withheld, said at the floor it runs at.

    A FLOOR OF ONE MAKES THE GENERAL SENTENCE ABSURD, so it does not get
    the general sentence. "A group fewer than 1 rows carry is named in no
    description" is true and unreadable: nothing is held back at a floor
    of one at all, and that is the thing a reader needs to be told. Every
    other floor -- the default among them -- gets the sentence with its
    own number in it (plan amendment A-P3-11 clause 3).

    AND THE MOOD IS THE RULE'S, NOT THE RUN'S (review of the shipped
    reports, 2026-08-15). "The comparison was made; what cannot be shown
    is which way it came out" is a sentence about lines this report
    carries, and it was printed word for word on reports carrying none.
    What is fixed here is the rule, which holds whether or not it bit
    today; how many times it bit is said once, by the caller, from the
    census.
    """
    if floor < 2:
        return [
            "  This description's publication floor is 1, so nothing is",
            "  held back this way at all: every count it carries is named",
            "  exactly, and no line of this report can read WITHHELD for",
            "  being a group too small to name. At any higher floor one",
            "  could.",
        ]
    return [
        f"  The publication floor of this description is {floor}: a group",
        f"  fewer than {floor} rows carry is named in no description",
        "  written under it -- that is what a floor is for -- so a count",
        "  of it is not something a description of this file carries",
        "  either. Where that closes over a check, the comparison is",
        "  still made and what cannot be shown is which way it came out,",
        "  because two files no description tells apart would come out",
        "  differently.",
    ]


def _withheld_census_lines(withheld: int) -> "list[str]":
    """How many times the rule above bit on THIS run, said from the census.

    THE DEFECT THIS CLOSES (review of the shipped reports,
    2026-08-15). The paragraph explaining WITHHELD was written in the
    present indicative about lines the report carries -- "Some
    obligations carry no verdict at all and the report says WITHHELD
    where the verdict would have stood ... the line itself says which"
    -- and it printed unchanged on a report whose census read
    `0 WITHHELD`. A reader was sent looking for lines that are not
    there, and a page that describes itself wrongly is wrong however
    right its arithmetic is. The rule above is now stated as a rule,
    which is true either way; this says what happened here, and it is
    generated from the census exactly as the verdict summary is, so it
    cannot claim more than the count supports.
    """
    if not withheld:
        return [
            "On this file the rule closed over nothing: no line of this",
            "report reads WITHHELD, so every obligation counted in the",
            "verdict above carries an outcome you can read. The rule is",
            "written out anyway, because whether it bites is a fact about",
            "this description and this file rather than about synthtwin.",
        ]
    return [
        f"On this file it closed over {withheld} obligation(s), and each",
        "of them reads WITHHELD above. A withheld count stands on the",
        "verdict rather than being quietly dropped: the obligation was",
        "set, and this report is not able to tell you whether this file",
        "met it.",
    ]


def _handling_lines(
    description: contract.Profile, withheld: int
) -> "list[str]":
    """Where the numbers came from, and how the five files are handled.

    V7.5. This report states measured facts about a file derived from
    real data, so it is real-derived material exactly as the description,
    the twin and the generation report are, and it says so in as many
    words rather than leaving a reader to infer that a verdict is
    somehow safer to move than the thing it measured.

    The load-bearing phrases are deliberately the same ones the charter,
    `README.md`, `SECURITY.md`, the package docstring, the command's
    status screen, the profiler's summary and the twin's report use.

    THE WITHHOLDING RULE NAMES ITS OWN NUMBER (owner ruling 2026-08-14,
    plan amendment A-P3-11). It used to read "a group fewer rows carry
    than the publication floor is never named in any description", which
    was written when every description had the same floor. It is not one
    number any more: the owner ruled `--smallest-group` through end to
    end, so the floor is a property of the description in front of the
    reader, and a sentence about "any description" now invites a reader
    to supply the default and be wrong about what this report is showing
    them. The number is therefore printed, on every run, at the point
    where it decides something -- which is also the one place a reader
    of an ordinary report is told what protects them.

    AND THE WITHHOLDING RULE SAYS BOTH WHAT IT IS AND WHAT IT IS NOT
    (owner ruling 2026-08-14, plan amendment A-P3-13). The rule is about
    what one report says: this page answers questions about the one file
    it was handed, and a number it withholds is a number it does not
    print anywhere. It is not a defence against a person who holds the
    checked file and re-runs the check with descriptions of their own,
    watching which lines move; the owner ruled that defence out of
    scope, because such a person can read the file. A reader who is not
    told that will read WITHHELD as a promise it never made, so the
    limit is printed beside the rule rather than kept in a plan.

    IT IS SAID ONCE, in the register `rendering` uses for what a report
    IS NOT -- two short paragraphs closing the part that says what
    WITHHELD means, in words a researcher can act on rather than in the
    method's. Repeating it elsewhere teaches a reader to skip it.

    AND IT SAYS IT IS NOT PERMISSION TO MOVE THE PAGE, because on a
    lowered floor it would otherwise read as one. Read the two sections
    together on a description made with `--smallest-group 3`: this one
    says the withholding protects the page for a reader who holds no
    file, and the section at the head of the report says that same page
    now carries counts down to three rows and that whoever approves data
    leaving the environment should be told before it moves. A sentence
    ending "so this page can be handed to somebody who has no copy of
    the file" -- which is what stood here first -- puts those two in a
    fight the reader has to settle. What the rule buys is silence about
    what it withholds, not a licence for the report, and the paragraph
    now says so in the same breath.
    """
    floor = description.settings.small_cell_floor
    return [
        _RULE,
        "HOW TO KEEP THIS FILE",
        _RULE,
        "",
        "This report holds counts and measurements taken from the file it",
        "checked, and the file it checked was built from -- or is -- data",
        "derived from a real table. It also holds the NAME of that file,",
        "at the top, because a report that does not say what it measured",
        "can be read as being about a file it is not -- so if you chose a",
        "file name that says something about your study, this report",
        "carries it wherever it goes. All five files a full run produces",
        "-- the description, the plain-language summary beside it, the",
        "twin, the twin's report and this quality report -- carry facts",
        "computed from your real data. Keep all five under the rules your",
        "institution applies to the table itself, and check with whoever",
        "approves data leaving your environment before you move any of",
        "them anywhere.",
        "",
        "WHAT SYNTHTWIN SAYS ABOUT THE ROWS OF A TWIN, unchanged by any",
        "verdict here. Building a twin reads no table: it",
        "samples or copies no row of yours, and every cell is worked out",
        "from the description and the seed. That says where the values came",
        "from. It does NOT say that no row of a twin can equal a row of",
        "your table -- holding a published count exactly can",
        "force a twin row to match a real one, with nothing copied, and",
        "this report checking that count does not change it.",
        "synthtwin offers no formal privacy guarantee.",
        "",
        "WHEN AN OBLIGATION CARRIES NO VERDICT AT ALL, the line reads",
        "WITHHELD where the verdict would have stood. One rule puts it",
        "there: this report may say about the file it checked only what",
        "describing THAT FILE on its own would publish about it. That",
        "can close over a check in two ways, and a line it closes over",
        "says which of the two.",
        "",
        "  Describing the file would publish no measurement of that kind",
        "  at all. A column the description calls numbers, holding words",
        "  in the file, has no average for an average to be compared",
        "  with, so nothing is measured.",
        "  Describing the file would publish the kind and pool the",
        "  number.",
    ] + _floor_gate_lines(floor) + [
        "",
    ] + _withheld_census_lines(withheld) + [
        "",
        "WHAT WITHHELD PROTECTS, AND WHAT IT DOES NOT -- said here rather",
        "than left for you to assume. What it protects is this page, for a",
        "reader who has no copy of the file it is about: every question",
        "this report answers is a question about the one file it was",
        "given, and a number it withholds is a number it does not print --",
        "not in this file, not on the screen, not in a message that stops",
        "the command. That is a rule about what the page SAYS, and it is",
        "not permission to move the page: everything above about keeping",
        "these five files applies to this one unchanged.",
        "",
        "What it is NOT is a barrier against somebody who HAS the checked",
        "file and runs this check on it again and again, each time with a",
        "description they wrote themselves, watching which lines move. That",
        "person can narrow a number withheld here, and synthtwin does not",
        "try to stop them: whoever can run this check on a file can read",
        "the file. So who may hold the file is a decision of its own, and",
        "this report being careful is not a substitute for making it.",
    ]


def quality_report(
    description: contract.Profile, outcome: validation.Outcome
) -> str:
    """The whole quality report, as the text printed and written.

    Guarantees:

    - Inputs: the description this check was run against, loaded by
      `contract.load_profile`, and the outcome `validation.measure`
      produced from it. Nothing else: no path, no table, no file, no
      clock. The report names the measured file -- its NAME, carried on
      the outcome, never a folder and never a path -- so the same check
      writes the same report wherever its file is put, and a reader who
      finds the file later can tell what it is about (V7.1).
    - Determinism: a fixed function of those two values, which makes the
      report's bytes a fixed function of the description's bytes, the
      measured file's name and the measured file's bytes (V10). The name
      is an input to the bytes and is stated as one: the same file
      renamed and measured again gives a different report, which is the
      whole point of printing it. Every list it prints is in the
      description's own order, and nothing here consults the environment
      or draws from a random source. One is reachable by attribute --
      this module imports `validation`, which imports `reading`, which
      imports pandas -- and saying otherwise was a false guarantee
      (amendment A-P3-4). Nothing here asks it for anything.
    - Errors raised: none, for a description the loader accepted and an
      outcome measured from it.
    - Boundary: no file is opened and no file is written. No string read
      from the measured file appears anywhere in the text -- the outcome
      carries none, by `validation`'s own guarantee -- so every name here
      is either the description's own published text or the measured
      file's name off the command line, and both pass the display
      boundary the same way.
    - Display: every interpolated string passes `parsing.visible` once
      on its way into a line (contract 13.5). The caller puts the
      finished text through `parsing.visible_lines` on its way to the
      screen and to disk, as the twin's report is treated.

    THE ORDER IS FIXED (V7.1): the verdict summary, then the honest
    bounds, then the fact-by-fact detail with anything missed at the head
    of it, then the obligations no CSV can evidence, then the
    analyst-expectations section, then the handling rule.

    ONE SECTION SITS ABOVE THE VERDICT AND APPEARS ONLY WHERE IT IS
    TRUE: that the description was made with the smallest group size
    LOWERED below the default, what that does to what the lines below
    print, and what a group that small can reveal about a person (owner
    ruling 2026-08-14, plan amendment A-P3-11). `_lowered_floor_lines`
    carries the reasoning for its being conditional. On a description
    made at the default floor this report's bytes differ from the
    version before that ruling in one place only: the withholding rule
    at the foot now prints the floor it is running at.

    THE SUMMARY IS GENERATED FROM THE CENSUS ALONE (V7.2). It states how
    many obligations were met exactly, how many landed inside a stated
    window, how many took a lesser outcome the ratified plan names for
    this description, how many were withheld, how many were missed, and
    how many could not be checked at all. A pass means no checkable
    obligation was missed and nothing more; the other counts stand beside
    it and are never folded into it. No wording available to this module
    can say that every published fact was found.
    """
    lines = _opening_lines(description, outcome.measured_name) + [""]
    # HIGH IN THE PAGE, above the verdict a reader came for. Nothing at
    # all -- not even a blank line -- on a description made at the
    # default floor, so an ordinary report's bytes are unchanged by the
    # existence of this section.
    lowered = _lowered_floor_lines(description)
    if lowered:
        lines = lines + lowered + [""]
    lines = lines + _summary_lines(outcome.census) + [""]
    lines = lines + _bounds_lines() + [""]
    lines = lines + _detail_lines(outcome)
    lines = lines + _not_checkable_lines(outcome) + [""]
    lines = lines + _expectations_lines() + [""]
    lines = lines + _handling_lines(description, outcome.census.withheld)
    # The lines are joined by hand: the offline policy accepts a text
    # method only with arguments it has resolved, and a list built while
    # the program runs is not one (plan D6.2).
    text = ""
    for line in lines:
        text = text + line + _NEWLINE
    return text
