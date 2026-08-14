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
    validation.WITHHELD: "not shown -- the line below says why",
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
            "description asks for and what the file was found to hold. A",
            "missed obligation is a fact the description publishes that",
            "this file does not carry; it is not a judgement about whether",
            "the file is useful for anything.",
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

    THE LAST FIELD IS THREE DIFFERENT THINGS and is introduced as
    whichever one it is. On an authorized deviation it is the passage
    that authorizes the lesser outcome; on a within-bound verdict it is
    the document the window was taken from; on a withheld one it is the
    sentence saying why neither the measurement nor its outcome is
    shown. Calling all three "the authority" would tell a reader that a
    withholding had been authorized by somebody, which is not what
    happened.
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
        "description sets, what it asks for, and what the file holds.",
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


def _not_checkable_lines(outcome: validation.Outcome) -> "list[str]":
    """The census of obligations no CSV can evidence, and why (V3.3).

    These carry no verdict and are never counted toward a pass. Their
    failure mode is this list: a line missing from it is an obligation
    the report quietly stopped mentioning, so the report's exact-shape
    tests hold the list to its length.
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
        if listing.subcheck:
            # The same identity a verdict would have carried, so that a
            # reader comparing this census with an ordinary run's sees
            # the same obligations named the same way.
            named = f"{_shown(listing.subcheck)} [{named}]"
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


def _handling_lines() -> "list[str]":
    """Where the numbers came from, and how the five files are handled.

    V7.5. This report states measured facts about a file derived from
    real data, so it is real-derived material exactly as the description,
    the twin and the generation report are, and it says so in as many
    words rather than leaving a reader to infer that a verdict is
    somehow safer to move than the thing it measured.

    The load-bearing phrases are deliberately the same ones the charter,
    `README.md`, `SECURITY.md`, the package docstring, the command's
    status screen, the profiler's summary and the twin's report use.
    """
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
        "Some obligations carry no verdict at all and the report says",
        "WITHHELD where the verdict would have stood. One rule puts them",
        "there: this report may say about the file it checked only what",
        "describing THAT FILE on its own would publish about it. It",
        "happens two ways, and the line itself says which.",
        "",
        "  Describing the file publishes no measurement of that kind at",
        "  all. A column the description calls numbers, holding words",
        "  here, has no average for an average to be compared with, and",
        "  nothing was measured.",
        "  Describing the file publishes the kind and pools the number.",
        "  A group fewer rows carry than the publication floor is never",
        "  named in any description -- that is what the floor is for --",
        "  so a count of it is not something a description of this file",
        "  carries either. The comparison was made; what cannot be shown",
        "  is which way it came out, because two files no description",
        "  tells apart would come out differently.",
        "",
        "A withheld count therefore stands on the verdict above rather",
        "than being quietly dropped: the obligation was set, and this",
        "report is not able to tell you whether this file met it.",
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
    lines = lines + _summary_lines(outcome.census) + [""]
    lines = lines + _bounds_lines() + [""]
    lines = lines + _detail_lines(outcome)
    lines = lines + _not_checkable_lines(outcome) + [""]
    lines = lines + _expectations_lines() + [""]
    lines = lines + _handling_lines()
    # The lines are joined by hand: the offline policy accepts a text
    # method only with arguments it has resolved, and a list built while
    # the program runs is not one (plan D6.2).
    text = ""
    for line in lines:
        text = text + line + _NEWLINE
    return text
