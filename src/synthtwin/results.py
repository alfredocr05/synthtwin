"""What one run of synthtwin did, as data (plan P4-D395; lane S5a, plan P4-D437).

`synthtwin.cli.run` returns one `Result` for every command line -- a
profile, a twin generated, a file validated, a doctor's check, the help
page, the version and the status page -- and prints nothing of its own.
A caller tells a good run from a bad one by reading this object, never
by reading what the run showed (stage 5's gate, STATE's row 5).

Guarantees:

- THE STANDARD LIBRARY ONLY, AND NO MODULE OF THIS PACKAGE. A validate
  run imports this module, so it reaches no table reader, no random
  source and no generator through it (CLAUDE.md, "Rules of the road";
  plan P2-D1, P3-D1).
- Frozen records and two functions: `tier_of`, the rank decided once
  (plan P4-D395 part 2), and `exit_code`, the exit status read from a
  result alone (part 4). No code path chooses an exit status of its own.
- No record holds a cell of a twin, and a validate result holds no
  string read from the file it measured: every text field is copied
  from what the producer (the validator, the generator, the command)
  already shows a person, under the same rules (plan P4-D395 part 1).
- Determinism: every function here is a pure function of its arguments.
  No I/O of any kind.
"""

import dataclasses

# -- the commands a result is about -----------------------------------
PROFILE = "profile"
GENERATE = "generate"
VALIDATE = "validate"
DOCTOR = "doctor"
TWIN = "twin"
HELP = "help"
VERSION = "version"
STATUS = "status"
COMMANDS = (PROFILE, GENERATE, VALIDATE, DOCTOR, TWIN, HELP, VERSION, STATUS)

# -- the four verdicts (part 1) ---------------------------------------
# `no-miss`: the run reached its end, wrote every file it names and
# missed no obligation it could judge -- and claims no more: the tally
# and `unjudged` stand beside it. `missed`: it reached its end with at
# least one miss. `refused`: it could not finish. `unusable`: the
# command line could not be used.
NO_MISS = "no-miss"
MISSED = "missed"
REFUSED = "refused"
UNUSABLE = "unusable"
VERDICTS = (NO_MISS, MISSED, REFUSED, UNUSABLE)

# -- where a run that could not finish stopped (part 1, `refusal`) ----
STEP_COMMAND_LINE = "command-line"
STEP_INPUT = "input"
STEP_OUTPUTS = "outputs"
STEP_CONTENT = "content"
STEP_QUESTIONS = "questions"
STEP_WRITING = "writing"
STEP_MEMORY = "memory"
STEP_NESTING = "nesting"
STEP_ENVIRONMENT = "environment"
STEPS = (
    STEP_COMMAND_LINE,
    STEP_INPUT,
    STEP_OUTPUTS,
    STEP_CONTENT,
    STEP_QUESTIONS,
    STEP_WRITING,
    STEP_MEMORY,
    STEP_NESTING,
    STEP_ENVIRONMENT,
)

# -- the rank (part 2): a miss's tier, in the order they stand --------
# `form`: the file as a whole and each column's name and position;
# `writing`: which spellings one column's values may wear and how they
# are read; `count`: every other miss decided exactly; `window`: a miss
# judged against a bound the method grants. An order of dependence, not
# a ranking of the owner's two goals.
TIER_FORM = "form"
TIER_WRITING = "writing"
TIER_COUNT = "count"
TIER_WINDOW = "window"
TIERS = (TIER_FORM, TIER_WRITING, TIER_COUNT, TIER_WINDOW)
TIER_ORDER = {TIER_FORM: 0, TIER_WRITING: 1, TIER_COUNT: 2, TIER_WINDOW: 3}

# How the producer decided a miss, set where the miss is made.
JUDGED_EXACT = "exact"
JUDGED_WINDOW = "window"

# -- what is carried (part 1) -----------------------------------------
CLASS_APPROXIMATE = "approximate"
CLASS_NOT_CARRIED = "not-carried"
# A column whose description publishes no values; a label column's
# cells the floor keeps back; a column's counted cells the description
# carries no value for (out of range, contradictory, not a number, a
# date that did not read); and the table, between whose columns
# nothing is carried while its statistical block is null.
REASON_MADE_UP = "made-up"
REASON_HELD_BACK = "held-back"
REASON_UNCARRIED = "uncarried"
REASON_NOT_MODELED = "not-modeled"
# An approximate entry's reason: the contract calls the fact APPROXIMATED.
REASON_APPROXIMATED = "approximated"
REASONS = (
    REASON_MADE_UP,
    REASON_HELD_BACK,
    REASON_UNCARRIED,
    REASON_NOT_MODELED,
    REASON_APPROXIMATED,
)
# The validate verdict a carried entry got, beside the census words.
REPORT_ONLY = "REPORT-ONLY"

# -- the next command's purposes (part 1, `next_command`) -------------
# A closed list: the landing that makes a new one adds its key.
PURPOSE_PROFILE = "profile"
PURPOSE_DOCTOR = "doctor"
PURPOSE_GENERATE = "generate"
PURPOSE_VALIDATE = "validate"
PURPOSE_ANSWER_QUESTIONS = "answer-questions"
PURPOSE_TWIN = "twin"
PURPOSES = (
    PURPOSE_PROFILE,
    PURPOSE_DOCTOR,
    PURPOSE_GENERATE,
    PURPOSE_VALIDATE,
    PURPOSE_ANSWER_QUESTIONS,
    PURPOSE_TWIN,
)

# -- the cautions a run gives (part 1, `warnings`) --------------------
# One key for each builder in `cli` that composes a caution today, so a
# caller never reads its words to know which caution it is. A warning
# never moves the verdict (plan P4-D2 item 5).
CAUTION_MADE_UP_COLUMNS = "made-up-columns"
CAUTION_LOWERED_FLOOR = "lowered-floor"
CAUTION_LOWERED_FLOOR_REMINDER = "lowered-floor-reminder"
CAUTION_DECLARED_WORDS = "declared-words"
CAUTION_SMALL_POPULATION = "small-population"
CAUTION_COUNTED_IN_ROWS = "counted-in-rows"
CAUTION_COUNTED_IN_PEOPLE = "counted-in-people"
CAUTION_WITHHELD = "withheld-until-answered"
CAUTION_LEFT_BEHIND = "left-behind"
CAUTION_QUESTIONS_NOT_WRITTEN = "questions-not-written"
CAUTION_QUESTIONS_WOULD_REPLACE = "questions-would-replace"
CAUTION_DECLARATION_DID_NOT_REACH = "declaration-did-not-reach"
CAUTION_ANSWER_REACHED_NOTHING = "answer-reached-nothing"
CAUTION_ANSWER_LEFT_WORDS = "answer-left-typed-words"
CAUTION_ANSWERED_AWAY = "declaration-answered-away"
CAUTION_CHAIN = "chain"
CAUTIONS = (
    CAUTION_MADE_UP_COLUMNS,
    CAUTION_LOWERED_FLOOR,
    CAUTION_LOWERED_FLOOR_REMINDER,
    CAUTION_DECLARED_WORDS,
    CAUTION_SMALL_POPULATION,
    CAUTION_COUNTED_IN_ROWS,
    CAUTION_COUNTED_IN_PEOPLE,
    CAUTION_WITHHELD,
    CAUTION_LEFT_BEHIND,
    CAUTION_QUESTIONS_NOT_WRITTEN,
    CAUTION_QUESTIONS_WOULD_REPLACE,
    CAUTION_DECLARATION_DID_NOT_REACH,
    CAUTION_ANSWER_REACHED_NOTHING,
    CAUTION_ANSWER_LEFT_WORDS,
    CAUTION_ANSWERED_AWAY,
    CAUTION_CHAIN,
)

# -- the kinds of file a run writes (part 1, `files`) -----------------
FILE_DESCRIPTION = "description"
FILE_SUMMARY = "summary"
FILE_QUESTIONS = "questions"
FILE_TWIN = "twin"
FILE_TWIN_REPORT = "twin-report"
FILE_QUALITY_REPORT = "quality-report"


@dataclasses.dataclass(frozen=True)
class Miss:
    """One miss of the run, with the rank it stands at (part 2).

    ``tier``, ``place`` and ``arrival`` are its rank: the tier read from
    `tier_of`; the column's position in the description, counted from 1,
    or 0 for the file as a whole; and its index in its own producer's
    order (`validation.Outcome.checks` or `generation.Twin.deviations`).
    ``fact`` is the disposition registry's `group.field`; ``subcheck``
    the validator's identity (empty on generate); ``partner`` a pair's
    second column (empty until stage 6 publishes one); ``judged`` how
    the producer decided it. ``published``, ``achieved`` and ``note``
    are the producer's own text, as the report prints it; ``shown`` is
    false exactly where the producer keeps the measured side back.
    """

    tier: str
    place: int
    arrival: int
    column: str
    fact: str
    subcheck: str
    judged: str
    published: str
    achieved: str
    shown: bool
    note: "tuple[str, ...]" = ()
    partner: str = ""

    def rank(self) -> "tuple[int, int, int]":
        """The key the misses stand in: (tier, place, arrival), and no other."""
        return (TIER_ORDER[self.tier], self.place, self.arrival)


@dataclasses.dataclass(frozen=True)
class Unjudged:
    """One obligation whose outcome the run could not say.

    Validate: a WITHHELD check, with the key of the rule that kept its
    outcome back and no measured value. Doctor: a check that could not
    be made, keyed by the check that composes it (``fact`` empty).
    """

    column: str
    fact: str
    subcheck: str
    key: str


@dataclasses.dataclass(frozen=True)
class Measure:
    """An approximate entry's measurement: the text the report prints, with the answer.

    ``inside`` is true, false, or None wherever the measured side is
    kept back or the subject could not be checked, so a result neither
    shows a withheld outcome nor states one never measured.
    """

    published: str
    achieved: str
    lowest: str
    highest: str
    inside: "bool | None"
    covers_published: "bool | None"


@dataclasses.dataclass(frozen=True)
class Carried:
    """What the run holds only approximately, or does not carry.

    ``subject`` is empty for the table, one name for a column, two in
    schema order for a pair. ``fact`` is the disposition registry's
    `group.field`, named as a miss names it, so an approximation and
    the miss its bound makes join by key; ``subcheck`` the validator's
    identity (one rung of a ladder, one tail), empty off validate.
    ``kind`` is the page's `class` (`approximate` or `not-carried`; a
    pair's class read verbatim once stage 6 publishes pairs) and
    ``reason`` its reason; ``verdict`` the census word its validate
    check got, or REPORT-ONLY, and empty off validate.
    """

    subject: "tuple[str, ...]"
    fact: str
    kind: str
    reason: str
    subcheck: str = ""
    words: str = ""
    verdict: str = ""
    measures: "tuple[Measure, ...]" = ()


@dataclasses.dataclass(frozen=True)
class Caution:
    """One caution the run gave: its key, the column it names, its words as shown."""

    key: str
    column: str
    words: str


@dataclasses.dataclass(frozen=True)
class FileWritten:
    """A file the run wrote and that exists when it returns: its kind and its path."""

    kind: str
    path: str


@dataclasses.dataclass(frozen=True)
class NextCommand:
    """The words a person types next, unquoted, from `synthtwin` on, and why.

    Quoting them for a shell is the renderer's and is never stored.
    """

    words: "tuple[str, ...]"
    purpose: str


@dataclasses.dataclass(frozen=True)
class Refusal:
    """Why a run could not finish: its step, its catalog key, its words, what is on disk."""

    step: str
    key: str
    words: str
    on_disk: str = ""


# -- what a profile asks (part 1, `questions`; lane S5b, plan P4-D441) --
# The sections of the questions file an entry stands in, in the file's
# order: questions about the file itself (plan P4-D81), the columns
# asked one by one, the checklist's columns under its one question, and
# the columns declared as counted dates that did not read so, held
# (plan P4-D406), which no answer gives back.
SECTION_ABOUT_FILE = "about_your_file"
SECTION_ASKED = "asked"
SECTION_CHECKLIST = "checklist"
SECTION_HELD = "held"
SECTIONS = (SECTION_ABOUT_FILE, SECTION_ASKED, SECTION_CHECKLIST, SECTION_HELD)


@dataclasses.dataclass(frozen=True)
class Offer:
    """One answer a question offers: its key, what it means, what the description then publishes."""

    answer: str
    means: str
    publishes: str


@dataclasses.dataclass(frozen=True)
class Asked:
    """One entry of the questions file, as data (plan P4-D395 part 1; lane S5b).

    ``section`` and ``order`` place it in the file (its order counted
    from 1 within its section); ``column`` is the description's name,
    empty for a question about the file; ``role`` and ``reason`` are its
    kind (`asking.Question.role` and `.reason`); ``saw`` the file's
    `what_synthtwin_saw`, a count, a width or a separator and never a
    cell; ``read_as_now`` the reading that stands unanswered; ``offers``
    the answers it offers, in order; ``put`` whether it was put at a
    prompt in this run, rather than only written down. A held entry
    offers nothing and stands under no reading. Every text field is the
    words `asking` composes for the file today, so the file is rendered
    from these records (`asking.questions_document_of`) byte for byte.
    """

    section: str
    order: int
    column: str
    role: str
    reason: str
    saw: str
    read_as_now: str
    offers: "tuple[Offer, ...]" = ()
    put: bool = False


@dataclasses.dataclass(frozen=True)
class Result:
    """One run of synthtwin, as data (plan P4-D395 part 1).

    ``misses`` stand in rank order and are never cut short; ``tally``
    is the command's own counts as (key, count) pairs in a fixed order;
    ``floor`` is the description's smallest group size where the
    command reads or writes one, with ``floor_lowered`` beside it;
    ``refusal`` is set exactly when the verdict is `refused` or
    `unusable`; ``steps`` is the `twin` command's (lane TT's).
    ``questions`` is profile's (lane S5b, plan P4-D441): one record for
    each entry its questions file holds, in the file's order, whether or
    not the file could be written.
    """

    command: str
    verdict: str
    misses: "tuple[Miss, ...]" = ()
    unjudged: "tuple[Unjudged, ...]" = ()
    carried: "tuple[Carried, ...]" = ()
    tally: "tuple[tuple[str, int], ...]" = ()
    floor: "int | None" = None
    floor_lowered: bool = False
    warnings: "tuple[Caution, ...]" = ()
    questions: "tuple[Asked, ...]" = ()
    files: "tuple[FileWritten, ...]" = ()
    left_behind: "tuple[str, ...]" = ()
    next_command: "NextCommand | None" = None
    refusal: "Refusal | None" = None
    steps: "tuple[Result, ...]" = ()


# THE RANK TABLE (plan P4-D395 part 2): the tier of a miss decided
# exactly, keyed by the disposition registry's `group.field` -- or
# `group.*` for a whole group -- and, where one fact holds subchecks of
# two tiers, by a subcheck prefix beside it ("" for any). The first row
# that matches decides, so a fact's own rows stand above its group's.
# `tests/test_stage5_gate.py` holds it total over every fact of
# `tests/dispositions.py`'s registry and every key a miss carries on the
# battery, and red on a key it lacks.
#
# WHY THESE ROWS. `form`: every check on no column (the header, the
# names and their order, the counts of columns and rows, the encoding,
# the line endings and dialect, the workbook block) and each column's
# name and position -- every column is read through them. `writing`:
# a column's role and type, its date and clock formats and what they
# are read at, its separators and decimal marks, its layouts, a label's
# spelling map and variants, which spellings mean no value, and a
# cell wearing no spelling its value admits (`styles.spelled`) -- every
# value of the column is read through them. Every other fact decided
# exactly is a `count`, the style, width and mark censuses among them
# (a census dropping a spelling to nought ranks `count`, because ranking
# it otherwise would make the order turn on the measured side, which V5
# keeps back for those counts). THE FORM AND MARK CENSUSES OF A WRITING
# FACT RANK `count` TOO (lane S5a's repair 1): an identifier's layout
# forms and a number column's spellings are each checked as the cells
# that wear one published form (`validation._form_checks`), and a
# datetime column's marks as the cells that wear one published mark,
# each a census of cells; the cells that wear no mark the census names
# (`marks.unnamed`) stay `writing`, as `styles.spelled` does. AND THE
# CENSUS OF CELLS PER MISSING SPELLING RANKS `count` (the orchestrator's
# ruling of 2026-10-26, lane S5a's repair 2): `universal.missing_by_source`
# holds each published spelling of "no value" at exactly its count of
# cells (`holes.by_source.*`), an exact census, so it falls to
# `universal.*`; which spellings mean "no value" stays `writing` through
# `sentinel_verdicts`. A JOINED COLUMN'S POSITION RANKS AS A COLUMN OF
# NUMBERS (lane S5a's repair 2, Codex's item 6): the validator and the
# generator rename a position's numeric fact `numeric.X` to
# `joined.parts[N].X`, its subcheck led by `number N+1`, so `_ranked`
# reads it back as `numeric.X` and the subcheck after that lead, and a
# position's type or spelling miss stands where the same miss of a plain
# number column stands.
_RANKS: "tuple[tuple[str, str, str], ...]" = (
    ("identifier.layout_forms", "forms.published", TIER_COUNT),
    ("numeric.number_spellings", "spellings.published", TIER_COUNT),
    ("datetime.datetime_separators", "marks.unnamed", TIER_WRITING),
    ("datetime.datetime_separators", "marks", TIER_COUNT),
    ("document.*", "", TIER_FORM),
    ("universal.name", "", TIER_FORM),
    ("universal.position", "", TIER_FORM),
    ("universal.role", "", TIER_WRITING),
    ("universal.statistical_type", "", TIER_WRITING),
    ("universal.structural_role", "", TIER_WRITING),
    ("universal.sentinel_verdicts", "", TIER_WRITING),
    ("numeric.numeric_styles", "styles.spelled", TIER_WRITING),
    ("numeric.group_separator", "", TIER_WRITING),
    ("numeric.decimal_plus", "", TIER_WRITING),
    ("numeric.negative_form", "", TIER_WRITING),
    ("numeric.integer_valued", "", TIER_WRITING),
    ("numeric.number_spellings", "", TIER_WRITING),
    ("affixed.affix_prefix", "", TIER_WRITING),
    ("affixed.affix_suffix", "", TIER_WRITING),
    ("affixed.affix_variants", "", TIER_WRITING),
    ("datetime.format", "", TIER_WRITING),
    ("datetime.datetimes_read_at", "", TIER_WRITING),
    ("datetime.count_form", "", TIER_WRITING),
    ("datetime.datetime_separators", "", TIER_WRITING),
    ("datetime.zulu_case", "", TIER_WRITING),
    ("datetime.quarter_marker_case", "", TIER_WRITING),
    ("datetime.subsecond_digits", "", TIER_WRITING),
    ("datetime.time_precision", "", TIER_WRITING),
    ("datetime.resolution", "", TIER_WRITING),
    ("clock.clock_form", "", TIER_WRITING),
    ("joined.separator", "", TIER_WRITING),
    ("label.variants", "", TIER_WRITING),
    ("label.variants_withheld", "", TIER_WRITING),
    ("identifier.layout_forms", "", TIER_WRITING),
    ("identifier.layout_prefixes", "", TIER_WRITING),
    ("identifier.all_whole_numbers", "", TIER_WRITING),
    ("universal.*", "", TIER_COUNT),
    ("empty.*", "", TIER_COUNT),
    ("numeric.*", "", TIER_COUNT),
    ("affixed.*", "", TIER_COUNT),
    ("datetime.*", "", TIER_COUNT),
    ("clock.*", "", TIER_COUNT),
    ("joined.*", "", TIER_COUNT),
    ("compound.*", "", TIER_COUNT),
    ("label.*", "", TIER_COUNT),
    ("free_text.*", "", TIER_COUNT),
    ("identifier.*", "", TIER_COUNT),
    ("numeric_unrepresentable.*", "", TIER_COUNT),
)


def _forms(fact: str) -> "list[str]":
    """The keys a fact is looked up under, the most particular first.

    `numeric.percentiles.min` is looked up as itself, then as
    `numeric.percentiles`; `joined.part_above[2]` as `joined.part_above`;
    each then under its group's `group.*`. Built a character at a time,
    for the offline audit's reason (no method of the value is called).
    """
    if not isinstance(fact, str):
        raise TypeError("a fact is named by text")
    plain = ""
    cuts: "list[int]" = []
    for character in fact:
        if character == "[":
            break
        if character == ".":
            cuts += [len(plain)]
        plain = plain + character
    found = [plain]
    place = len(cuts) - 1
    while place >= 1:
        found += [plain[: cuts[place]]]
        place = place - 1
    if cuts:
        found += [plain[: cuts[0]] + ".*"]
    return found


# A joined column's position, as the validator and the generator name its
# numeric facts (`joined.parts[N].X`, subcheck `number N+1 ...`).
_PART_OPEN = "joined.parts["
_PART_CLOSE = "]."
_PART_LEAD = "number "
_FIGURES = "0123456789"


def _figures_from(text: str, place: int) -> int:
    """Where the run of figures starting at ``place`` in ``text`` ends."""
    while place < len(text) and text[place] in _FIGURES:
        place = place + 1
    return place


def _as_a_number_column(fact: str, subcheck: str) -> "tuple[str, str] | None":
    """A joined position's fact and subcheck as a plain number column's, or None.

    `joined.parts[0].integer_valued` is `numeric.integer_valued`, and its
    subcheck `number 1 integer.valued` is `integer.valued`: the rename
    the validator (`_joined_style_checks`, `_joined_numeric_checks`) and
    the generator (`parts[N].fact`) make, read back. A subcheck without
    the lead (generate's, which is empty) is kept as it is. Built without
    a method of the value, for the offline audit's reason.
    """
    if fact[: len(_PART_OPEN)] != _PART_OPEN:
        return None
    place = _figures_from(fact, len(_PART_OPEN))
    if place == len(_PART_OPEN):
        return None
    if fact[place : place + len(_PART_CLOSE)] != _PART_CLOSE:
        return None
    field = fact[place + len(_PART_CLOSE) :]
    if not field:
        return None
    inner = subcheck
    if subcheck[: len(_PART_LEAD)] == _PART_LEAD:
        after = _figures_from(subcheck, len(_PART_LEAD))
        if after > len(_PART_LEAD) and subcheck[after : after + 1] == " ":
            inner = subcheck[after + 1 :]
    return ("numeric." + field, inner)


def _ranked(fact: str, subcheck: str) -> "str | None":
    """The tier the rank table gives a fact decided exactly, or None where it has none."""
    if not isinstance(subcheck, str):
        raise TypeError("a subcheck is named by text")
    if not isinstance(fact, str):
        raise TypeError("a fact is named by text")
    part = _as_a_number_column(fact, subcheck)
    if part is not None:
        return _ranked(part[0], part[1])
    for form in _forms(fact):
        for key, prefix, tier in _RANKS:
            if key != form:
                continue
            if prefix and not (
                subcheck == prefix or subcheck[: len(prefix) + 1] == prefix + "."
            ):
                continue
            return tier
    return None


def tier_of(fact: str, subcheck: str, judged: str) -> str:
    """The tier a miss stands in, decided once (plan P4-D395 part 2).

    Guarantees: `window` exactly where the miss was judged against a
    bound the method grants (``judged`` is `window`), read off that and
    nothing else; otherwise the rank table's tier for the fact and the
    subcheck. A key the table lacks is ranked `count` -- one stated
    fallback, met on no battery, so a person's run never stops over a
    rank. Determinism: a pure function of the three. Raises nothing.
    """
    if judged == JUDGED_WINDOW:
        return TIER_WINDOW
    found = _ranked(fact, subcheck)
    return TIER_COUNT if found is None else found


def exit_code(result: Result) -> int:
    """The exit status of a run, read from its command and verdict alone (part 4).

    `no-miss` 0; `missed` 3 on `validate` and `twin`, 0 on `generate`
    (a twin that gave a fact up is written, and its report names the
    fact: 0 means both files were written, as before); `refused` 1, a
    doctor check made that failed included; `unusable` 2. These are the
    statuses the commands returned before results existed, case for
    case. Raises nothing; an unknown verdict reads as `refused`.
    """
    if result.verdict == NO_MISS:
        return 0
    if result.verdict == MISSED:
        return 3 if result.command in (VALIDATE, TWIN) else 0
    if result.verdict == UNUSABLE:
        return 2
    return 1
