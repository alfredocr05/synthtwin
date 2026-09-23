"""Text-level parsing: what a cell of a CSV file means (plan P1-D4).

Everything here works on the text exactly as it appeared in the file.
No value is ever guessed at: each rule is written out, tested character
by character, and refuses anything it does not recognize. There is no
regular expression and no locale-dependent parser in this module, so
the same text yields the same reading on every computer.

Three rules are worth stating up front because they decide what the
twin will look like:

* Only ASCII digits count as digits. Other numbering systems exist in
  Unicode and Python's own int() accepts several of them; a table that
  mixes them would silently become numbers whose text nobody can round
  trip, so they are read as text instead.
* "nan", "inf" and their spellings are NOT numbers here, even though
  Python's float() accepts them. A not-a-number value that entered the
  statistics would poison every summary computed from the column.
* Dates are matched against an explicit, ordered table of formats. A
  guessing parser would be unauditable, so a format that is not in the
  table is simply not a date.

Imports here stay within the allowlist (plan D6.2): this module imports
nothing at all.

Functions in this module gate their text parameters with an explicit
isinstance check. The values arrive from the CSV readers, which always
produce text, so the check never fires in practice; it is the shape
the offline scanner recognizes before it accepts a text method call
(plan P1-D10, extension E4), and it is a real invariant check besides.
"""

_NOT_TEXT = (
    "synthtwin internal check: a cell value reached the parser as "
    "something other than text. Both readers produce text for every "
    "cell, so this means a bug in synthtwin; please report it."
)

# Spellings that mean "no value", compared after trimming and case
# folding (plan P1-D4). Every one of them is reported per column, by
# spelling, so a reader can see exactly where the missing values came
# from.
#
# THE MEMBER IS WRITTEN IN THE VOCABULARY'S OWN SPELLING, which for the
# first ten is lower case and for the seven spreadsheet literals is the
# form a spreadsheet writes (contract 14.4 lists all eighteen). BOTH
# sides of a folded comparison are folded, so the member's own capitals
# cost nothing at the comparison and are what a document records --
# which is what a producer written from the contract emits and what
# this loader must accept.
MISSING_TEXTS = (
    "",
    "-",
    "--",
    ".",
    "?",
    "n/a",
    "na",
    "nan",
    "none",
    "null",
    # THE SEVEN SPREADSHEET ERROR LITERALS (plan P4-D6.2). Each is a
    # machine artifact whose folded form collides with no human word,
    # which is the criterion that keeps `unknown` and `missing` OUT: a
    # human word carries meaning somewhere, and a column where it does
    # would be hollowed by reading it as absence. What these buy is
    # stated plainly in the decision: a column of numbers with a few
    # artifact cells stops losing its whole distribution to the parse
    # line, so the twin of it is a column of numbers rather than free
    # text.
    "#DIV/0!",
    "#N/A",
    "#NAME?",
    "#NULL!",
    "#NUM!",
    "#REF!",
    "#VALUE!",
)

# ...and the ONE member matched byte for byte instead.
#
# WHY IT IS NOT IN THE LIST ABOVE, which is the whole of the owner
# ruling of 2026-08-19 that admitted it. The list is compared after
# trimming and case folding, and this literal's folded form is a
# person's name -- so a folded member would read a name column's cells
# as absence and hollow it in silence. Compared raw, the collision
# cannot arise: a cell reads as absent here only if it is exactly these
# three characters, with no spaces around them and the capitals as
# written.
#
# ONE OPERATION, APPLIED IDENTICALLY WHEREVER THE VOCABULARY IS
# CONSULTED. `is_missing_text` below is that operation, and everything
# that asks the vocabulary a question asks it through
# `missing_text_matches` beside it -- recognition, the recording of a
# declaration, the published-vocabulary guards and the validator's
# reconstruction alike. A second reading of this rule anywhere is how
# the exception becomes a hole.
MISSING_TEXTS_EXACT = ("NaT",)

# Numbers that are conventionally used to mean "no value". They count
# as missing only when they are also distribution outliers; the rule is
# in taxonomy.py, and every candidate's fate is reported either way.
NUMERIC_SENTINELS = (-9999.0, -999.0, 9999.0)

# Dates conventionally used to mean "no value" -- the placeholder a
# person types into an open-ended row. They count as missing only when
# they are also distribution outliers, by the same rule the numbers
# above are judged under, transposed to day ordinals; the rule is in
# taxonomy.py and every candidate's fate is reported either way.
#
# THEIR IDENTITY IS THE WRITTEN CALENDAR DAY (plan amendment A-P4-1
# item 3). A cell matches a placeholder when its own written fields,
# under the column's own format, denote that day: no shared-clock
# normalization and no offset arithmetic enters the question, because
# the placeholder is a writing convention and the writer typed that
# day.
CALENDAR_PLACEHOLDERS = ("1900-01-01", "9999-12-31")


def calendar_placeholders() -> "tuple[str, ...]":
    """The built-in placeholder days, as canonical ISO spellings.

    Guarantees: returns the same tuple on every call, of this package's
    own constants. Raises nothing. No I/O of any kind.
    """
    return CALENDAR_PLACEHOLDERS


def placeholder_day_of(text: str, format_name: str) -> "str | None":
    """The placeholder day a cell denotes under one format, or None.

    THE WRITTEN DAY AND NOTHING ELSE. The cell is read under the
    column's own format and its DATE part is compared with the
    placeholder; any time of day and any offset the cell carries are
    not consulted, because a placeholder is a writing convention rather
    than an instant and the person typed a day.

    Guarantees: accepts a cell's text and a format member; returns the
    placeholder it denotes or None; raises TypeError if handed anything
    that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    found = parse_datetime(text, format_name)
    if found is None:
        return None
    written = found[0][0:10]
    for candidate in CALENDAR_PLACEHOLDERS:
        if written == candidate:
            return candidate
    return None

# The date and time formats, in the order they are tried. The first
# format that parses at least the required share of a column's values
# wins, and the profile records which one it was.
DATE_FORMATS = (
    "iso-date",
    "iso-datetime",
    "slashed-iso-date",
    "iso-month",
    "compact-date",
    "month-first-date",
    "day-first-date",
    "textual-day-first-date",
    "textual-month-first-date",
    "dotted-month-first-date",
    "dotted-day-first-date",
    "two-digit-month-first-date",
    "two-digit-day-first-date",
    # THE SAME TWO-FIGURE YEAR WRITTEN WITH DOTS (residual R-P4-4,
    # landing L18). `19.08.24` is how a great many European exports
    # write a date, and it was the one shape of that family no member
    # read: the four-figure dotted pair above needs `19.08.2024`, and
    # the two-figure pair needs slashes. Measured before this landing,
    # a 300-row column of them took the AFFIXED role -- read as the
    # number 19.08 wearing the text `.24` -- and published a ladder
    # from 1.01 to 28.12 over day-and-month numbers, with 151 of its
    # 300 twin cells holding months like 74 and 85.
    #
    # AFTER the slashed two-figure pair, so no spelling that already
    # reads keeps its reading only by luck of the order.
    "dotted-two-digit-month-first-date",
    "dotted-two-digit-day-first-date",
    "month-first-datetime",
    "day-first-datetime",
    # THE YEAR-FIRST SLASHED STAMP (landing 2b.3). `2024/03/17 14:05` is
    # how a great many exports write a moment, and no member read it: the
    # date-only `slashed-iso-date` needs exactly ten characters and the
    # two slashed stamps above need the year last. A column of them was
    # read as free text and its twin wrote made-up strings. The year
    # leads, so the reading is as unambiguous as `slashed-iso-date`'s,
    # and its clock is the time-of-day role's two forms, as the two
    # slashed stamps' is. AFTER every member a column already read under,
    # so no spelling that reads today changes its reading.
    "slashed-iso-datetime",
    "year-quarter",
    # LAST, AND THAT IS THE RULE RATHER THAN A PLACE IN A LIST. The
    # single-format pass runs first and its verdict stands wherever it
    # clears -- a column of ninety-nine ISO dates and one datetime cell
    # is a date column with one unparsed cell, as it is today. Only
    # where NO single format clears does the joint reading get a turn,
    # which is what putting it after every other member means.
    "iso-mixed",
)

# The three readings whose clock stands after ONE space and is the
# time-of-day role's own two forms, with no fraction and no offset (plan
# amendment A-P4-1 item 2; the year-first stamp since landing 2b.3).
SLASHED_STAMPS = (
    "month-first-datetime",
    "day-first-datetime",
    "slashed-iso-datetime",
)

_FORMAT_EXAMPLES = {
    "iso-date": "2024-03-17",
    "iso-datetime": "2024-03-17 14:05:00",
    "slashed-iso-date": "2024/03/17",
    "iso-month": "2024-03",
    "iso-mixed": "2024-03-17 and 2024-03-17 14:05:00 together",
    "compact-date": "20240317",
    "month-first-date": "03/17/2024 (month first)",
    "day-first-date": "17/03/2024 (day first)",
    "textual-day-first-date": "17 Mar 2024",
    "textual-month-first-date": "Mar 17, 2024",
    "dotted-month-first-date": "03.17.2024 (month first)",
    "dotted-day-first-date": "17.03.2024 (day first)",
    "two-digit-month-first-date": "03/17/24 (month first)",
    "two-digit-day-first-date": "17/03/24 (day first)",
    "dotted-two-digit-month-first-date": "03.17.24 (month first)",
    "dotted-two-digit-day-first-date": "17.03.24 (day first)",
    "month-first-datetime": "03/17/2024 14:05 (month first)",
    "day-first-datetime": "17/03/2024 14:05 (day first)",
    "slashed-iso-datetime": "2024/03/17 14:05",
    "year-quarter": "2024-Q1",
}

_DAYS_IN_MONTH = (31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)


def format_example(name: str) -> str:
    """Return a human-readable example of one date format name.

    Guarantees: accepts any string; returns a short example for a name
    in DATE_FORMATS and the name itself for anything else. Raises
    nothing. No I/O of any kind.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    if name not in _FORMAT_EXAMPLES:
        return name
    return _FORMAT_EXAMPLES[name]


# Every character that instructs a display instead of showing something
# of its own, defined by the Unicode general category it belongs to
# rather than by a list of the characters somebody happened to notice.
# The earlier list named thirteen characters by hand and was extended
# twice by review; each extension left the next hole open (review items
# P1-R3-F9, P1-R4-F4 and P1-R6-F11). The categories below are the whole
# of what "instructs a display" means:
#
#   Cc  the C0 and C1 control ranges and DEL -- escape, carriage
#       return, backspace, and the rest of the sequences a terminal
#       obeys rather than prints;
#   Cf  the format and bidirectional controls, which reorder, join or
#       hide the text around them while occupying no space of their
#       own. U+061C, U+200B, U+2060 and U+206A-U+206F live here and
#       were all absent from the hand-written list;
#   Zl  the line separator U+2028, and
#   Zp  the paragraph separator U+2029, either of which can break a
#       message into what look like two messages;
#   Cs  the surrogate range. This is not text at all: it is what a byte
#       the computer could not read as text becomes. It can never be
#       shown and cannot be written back out, so leaving one in place
#       turns a refusal into a crash with no message.
#
# Positions still reserved inside the blocks Unicode set aside for
# format controls are covered too -- U+2065, the rest of the shorthand
# and Egyptian-hieroglyph format blocks, and the reserved part of the
# tag block -- so a character assigned there by a later Unicode version
# is already handled here.
#
# Nothing else is touched. Letters, marks, digits, punctuation and
# symbols of every script -- accented Latin, Greek, Cyrillic, CJK,
# Arabic, Hebrew -- fall outside all five categories, and so does every
# space separator, the no-break space included. Over-escaping would be
# its own defect: a researcher whose column names are not English must
# read them as they wrote them.
#
# The table is checked character by character against Python's own
# Unicode database by tests/test_p1r6f11_display_boundary.py, over the
# whole code space, in both directions. A category that grows in a
# later Unicode version turns a test red instead of quietly leaving a
# character unescaped.
_DISPLAY_CONTROL_RANGES = (
    (0x0000, 0x001F),  # Cc: the C0 controls
    (0x007F, 0x009F),  # Cc: DEL and the C1 controls
    (0x00AD, 0x00AD),  # Cf: soft hyphen
    (0x0600, 0x0605),  # Cf: Arabic number signs
    (0x061C, 0x061C),  # Cf: Arabic letter mark
    (0x06DD, 0x06DD),  # Cf: Arabic end of ayah
    (0x070F, 0x070F),  # Cf: Syriac abbreviation mark
    (0x0890, 0x0891),  # Cf: Arabic pound and piastre marks
    (0x08E2, 0x08E2),  # Cf: Arabic disputed end of ayah
    (0x180E, 0x180E),  # Cf: Mongolian vowel separator
    (0x200B, 0x200F),  # Cf: zero-width marks, left/right-to-left marks
    (0x2028, 0x202E),  # Zl, Zp, Cf: separators and the bidi overrides
    (0x2060, 0x206F),  # Cf: word joiner, the isolates, deprecated marks
    (0xD800, 0xDFFF),  # Cs: surrogates -- bytes that are not text
    (0xFEFF, 0xFEFF),  # Cf: zero-width no-break space (byte-order mark)
    (0xFFF9, 0xFFFB),  # Cf: interlinear annotation marks
    (0x110BD, 0x110BD),  # Cf: Kaithi number sign
    (0x110CD, 0x110CD),  # Cf: Kaithi number sign above
    (0x13430, 0x1343F),  # Cf: Egyptian hieroglyph format controls
    (0x1BCA0, 0x1BCAF),  # Cf: shorthand format controls
    (0x1D173, 0x1D17A),  # Cf: musical beam and slur controls
    (0xE0000, 0xE00FF),  # Cf: language tag and the tag characters
)

# The one display control a composed document is allowed to keep. A
# line feed is how synthtwin writes its own layout; escaping it would
# reduce every message and the whole summary to a single line. It is
# escaped in a VALUE, where it is not layout but a way of forging a
# line that looks like one synthtwin wrote.
_LINE_FEED = 10


def _commands_a_display(code: int) -> bool:
    """True when the character numbered ``code`` instructs a display.

    The two leading tests are the ASCII shortcut, not a separate rule:
    they answer for the characters nearly every message is made of
    without walking the table, and they agree with it exactly.
    """
    if code < 32:
        return True
    if code < 127:
        return False
    for start, end in _DISPLAY_CONTROL_RANGES:
        if code < start:
            return False
        if code <= end:
            return True
    return False


def _written_out(code: int) -> str:
    """One display control written as text that shows itself.

    The spelling is Python's own: two hex digits for a byte, four for a
    character inside the first plane, eight beyond it. A reader who
    pastes it into a search engine finds out what it was.
    """
    if code < 256:
        return "\\x" + format(code, "02x")
    if code < 65536:
        return "\\u" + format(code, "04x")
    return "\\U" + format(code, "08x")


# The three widths `_written_out` writes a display control at, and the
# mark each one starts with. Read back here so that the question "could
# this text have come OUT of the boundary?" is answered from the same
# two functions that put text through it, and cannot drift from them.
_ESCAPE_FORMS = (("\\x", 2), ("\\u", 4), ("\\U", 8))


def _lower_hex(text: str) -> bool:
    """True when ``text`` is one or more lower-case ASCII hex digits."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text:
        return False
    for character in text:
        if "0" <= character <= "9":
            continue
        if "a" <= character <= "f":
            continue
        return False
    return True


def _boundary_wrote_this_at(text: str, index: int) -> bool:
    """True when a display control's own written form starts at ``index``."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    for mark, digits in _ESCAPE_FORMS:
        head = text[index : index + len(mark)]
        if head != mark:
            continue
        body = text[index + len(mark) : index + len(mark) + digits]
        if len(body) != digits:
            continue
        if not _lower_hex(body):
            continue
        code = int(body, 16)
        if not _commands_a_display(code):
            continue
        if _written_out(code) == mark + body:
            return True
    return False


def shows_only_itself(text: str) -> bool:
    """True when ``text`` is the ONLY text the boundary shows as ``text``.

    The display boundary is not reversible, and a caller that reads a
    published spelling back out of a report field has to know where it
    may and may not do so (review item P3-V7-F1). `visible` replaces
    each display control with its own written form, so two different
    texts can leave it identical: the three characters ``X``, U+0001,
    ``Y`` and the six printable characters ``X\\x01Y`` both come out
    ``X\\x01Y``, and no reading of that result can tell which one it
    was.

    THIS IS THE DECIDABLE HALF, and the proof is short. Every character
    `visible` does not pass through is replaced by `_written_out`'s form
    for it. So if no such form STARTS anywhere in ``text``, no text
    holding a display control can show as ``text``, which leaves
    ``text`` itself -- which the boundary passes through unchanged -- as
    the only text that does. Where such a form does start, at least two
    texts show as ``text`` and this returns False; it never claims the
    two are distinguishable.

    It is deliberately conservative in one direction and exact in the
    other: a form the boundary could not have written, such as
    ``\\x41`` for an ordinary letter or ``\\u0001`` for a character
    written ``\\x01``, is not treated as ambiguous, because
    `_written_out` would not have produced it.

    Guarantees: accepts text; returns a truth value; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    for index in range(len(text)):
        if _boundary_wrote_this_at(text, index):
            return False
    return True


def _made_visible(text: str, keep_line_feed: bool) -> str:
    """Show every display control in ``text``; the shared implementation."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    out = ""
    for character in text:
        code = ord(character)
        if code == _LINE_FEED and keep_line_feed:
            out = out + character
        elif _commands_a_display(code):
            out = out + _written_out(code)
        else:
            out = out + character
    return out


def visible(text: str) -> str:
    """Return one VALUE with everything that commands a display shown.

    A value in the user's table, or a path they typed, can contain an
    escape sequence. Printed as it stands it instructs the terminal --
    one header cleared the screen immediately after the disclosure that
    must be read before any file is written, another reordered the text
    around it, and a path cleared the screen from a refusal message
    (review items P1-R2-F14, P1-R3-F9, P1-R4-F4 and P1-R6-F11).

    Use this for anything synthtwin did not write itself: a cell, a
    column name, a path, a detail quoted from a library, a message
    built by another module. NOTHING survives -- the line feed included,
    because a value is not layout, and a line feed inside one forges a
    line that reads as though synthtwin wrote it.

    Applying this twice changes nothing: what it puts in place of a
    display control is ordinary printable ASCII, which a second pass
    leaves alone. That is what lets the emitter apply the boundary again
    without spoiling text that already crossed it.

    Guarantees: accepts text; returns text; raises TypeError if handed
    anything that is not a string instance. Ordinary printable text of
    every script is returned unchanged. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return _made_visible(text, False)


def visible_lines(text: str) -> str:
    """Return one composed DOCUMENT with display controls shown.

    The same boundary as `visible`, with one exception: the line feed
    is kept, because it is the layout synthtwin itself wrote. Use this
    for a whole message or the whole summary, where the line breaks
    belong to synthtwin and the values inside have already been through
    `visible`. It is the net under every human-facing sink: a value
    that reached a screen without being shown safely still cannot
    instruct the display.

    Guarantees: accepts text; returns text; raises TypeError if handed
    anything that is not a string instance. Every character except the
    line feed is treated exactly as `visible` treats it. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return _made_visible(text, True)


def spelled_out(text: str) -> str:
    """Return ``text`` with EVERY character written out as itself.

    The display boundary above shows the characters that command a
    display and leaves every other one alone, which is right for a value
    a person reads. It is not enough for a value whose whole content is
    space: a description may publish `" "`, `"  "` or a no-break space
    among the spellings a column's absent cells wore (5.4.3), and a
    report printing those keys as they stand shows a count beside
    nothing at all -- so a reader cannot tell one space from two, or a
    space from a no-break space, in the one place the report exists to
    tell them.

    The spelling is the boundary's own, read back from the same
    function, so the two cannot drift: two hex digits for a byte, four
    for a character inside the first plane, eight beyond it.

    Guarantees: accepts text; returns text made only of printable ASCII;
    raises TypeError if handed anything that is not a string instance.
    Determinism: a fixed function of the text. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    shown = ""
    for character in text:
        shown = shown + _written_out(ord(character))
    return shown


def trimmed(text: str) -> str:
    """Return ``text`` without surrounding whitespace.

    Guarantees: accepts text; returns text; raises TypeError if handed
    anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return text.strip()


def folded(text: str) -> str:
    """Return ``text`` trimmed and case-folded, for comparing labels.

    Case folding is Unicode-aware, so 'YES', 'Yes' and 'yes' compare
    equal, and so do letters outside English.

    Guarantees: accepts text; returns text; raises TypeError if handed
    anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return text.strip().casefold()


def is_missing_text(text: str) -> bool:
    """True when ``text`` is one of the documented spellings of "no value".

    Guarantees: accepts text; returns a truth value; raises TypeError
    if handed anything that is not a string instance. The comparison is
    against MISSING_TEXTS after trimming and case folding, and against
    MISSING_TEXTS_EXACT byte for byte. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if text in MISSING_TEXTS_EXACT:
        return True
    body = folded(text)
    for member in MISSING_TEXTS:
        if body == folded(member):
            return True
    return False


def missing_text_matches(spelling: str, member: str) -> bool:
    """Whether one spelling names one member of the built-in vocabulary.

    THE ONE OPERATION (plan P4-D6.2, owner ruling 2026-08-19). Every
    side that has to agree about what a member names asks this: the
    recording of a declaration, the guards over the published
    vocabulary, and the validator's reconstruction of what a
    description was written under. The rule is the member's own -- a
    folded member matches after trimming and case folding, and the
    exact member matches byte for byte -- so the exception cannot come
    apart from the rule it excepts by living in two places.

    Guarantees: accepts two strings; returns a truth value; raises
    TypeError if handed anything that is not a string instance. No I/O
    of any kind.
    """
    if not isinstance(spelling, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(member, str):
        raise TypeError(_NOT_TEXT)
    if member in MISSING_TEXTS_EXACT:
        return spelling == member
    return folded(spelling) == folded(member)


def built_in_missing_texts() -> "tuple[str, ...]":
    """Every built-in spelling of "no value", both matching rules over.

    Sorted, and the empty spelling is in it: a caller that wants the
    NAMEABLE half filters it out, as the ones that publish do.

    Guarantees: returns the same tuple on every call, of this package's
    own constants. Raises nothing. No I/O of any kind.
    """
    return tuple(sorted(MISSING_TEXTS + MISSING_TEXTS_EXACT))


def names_a_published_word(spelling: str) -> bool:
    """Whether one absent-cell spelling names a member of the vocabulary.

    THE QUESTION A COLUMN THAT PUBLISHES NO VALUE HAS TO ASK (plan
    P4-D85). Such a column may say that some of its absent cells were
    spelled `NA` -- because `NA` is not a value of anybody's table, it
    is a word this package ships, the same in every installation, and
    the published vocabulary "contains no text from any table". What it
    may not say is anything else. Both sides of that rule ask HERE: the
    producer, deciding which keys survive its publication class, and the
    loader, refusing a document whose key names no member. A second
    reading of it in either module is how the two would come apart.

    THE COMPARISON IS `missing_text_matches` AND NOT A LOOKUP, so the
    folded members match after trimming and case folding while the
    exact-spelling member matches byte for byte -- the same operation
    the producer read the cell by in the first place.

    A SPELLING OF NOTHING BUT SPACE NAMES THE EMPTY MEMBER, stated
    rather than left to fall out of the folding: the empty spelling is a
    member and folding trims, so ` `, two spaces and a tab each name it.
    That is what admits a whitespace key on a column publishing no
    value -- the same key landing 2b.8 admitted on every column that
    publishes one -- so the two rules cannot part.

    Guarantees: accepts one spelling; returns a truth value.
    Determinism: a function of the spelling and of this package's own
    constants; no table, no clock and no random source is consulted.
    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(spelling, str):
        raise TypeError(_NOT_TEXT)
    for member in built_in_missing_texts():
        if missing_text_matches(spelling, member):
            return True
    return False


def _all_ascii_digits(text: str) -> bool:
    """True when ``text`` is one or more ASCII digits and nothing else."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text:
        return False
    for character in text:
        if not ("0" <= character <= "9"):
            return False
    return True


def _digits_at(text: str, start: int, length: int) -> "str | None":
    """Return the ASCII digits of a fixed-width field, or None."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    piece = text[start : start + length]
    if len(piece) != length:
        return None
    if not _all_ascii_digits(piece):
        return None
    return piece


def _plain_number_shape(text: str) -> bool:
    """True when ``text`` is a plain decimal number written in ASCII.

    Accepted: an optional sign, digits with at most one decimal point
    and at least one digit, and an optional exponent (``e`` or ``E``,
    optional sign, at least one digit). Everything else -- including
    the words Python's float() would accept for not-a-number and
    infinity, hexadecimal forms, and digits from other numbering
    systems -- is refused.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text:
        return False
    index = 0
    if text[0] == "+" or text[0] == "-":
        index = 1
    mantissa_digits = 0
    dots = 0
    while index < len(text):
        character = text[index]
        if "0" <= character <= "9":
            mantissa_digits = mantissa_digits + 1
        elif character == ".":
            dots = dots + 1
            if dots > 1:
                return False
        elif character == "e" or character == "E":
            break
        else:
            return False
        index = index + 1
    if mantissa_digits == 0:
        return False
    if index >= len(text):
        return True
    # An exponent: the character at index is 'e' or 'E'.
    index = index + 1
    if index < len(text) and (text[index] == "+" or text[index] == "-"):
        index = index + 1
    return _all_ascii_digits(text[index:])


def _mantissa_has_nonzero_digit(text: str) -> bool:
    """True when the part before any exponent holds a digit from 1 to 9.

    The scan stops at the exponent on purpose: '0e5' is a zero written
    with an exponent, and refusing it would be wrong.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    for character in text:
        if character == "e" or character == "E":
            return False
        if "1" <= character <= "9":
            return True
    return False


# THE MARKS A CELL MAY WRITE BETWEEN ITS THOUSANDS, as the file spells
# them (landing 2b.2, 2026-09-15). The comma was the only one until this
# landing, and a charge written `2 198.92`, `2'198.92` or with a
# no-break space between its groups was read as free text: the column's
# numbers vanished from the description and the twin wrote stand-ins
# where they stood. The right single quotation mark is here because
# typographic exports write `1\u2019234` where a keyboard writes
# `1'234`; the no-break space, the narrow no-break space and the thin
# space U+2009 because a word processor puts them where a person typed a
# space. The thin space arrived with the verification of this landing,
# which measured a salary column grouped with it still read as free
# text with nothing said.
#
# A POINT IS NOT ON THIS LIST, and that is not an omission: a cell
# written `12.345` is read with the point as its decimal point, and a
# point between thousands is read only on a column declared
# `--decimal-comma`, whose cells are translated before any rule reads
# them. The asking stage names the column where the reading could be
# the other one (`asking.why_worth_asking`).
#
# THE GROUPS ARE THREE FIGURES EACH, after a first group of one to
# three, and ONE KIND OF MARK stands in a cell. That is what keeps a
# postcode `123 45`, a telephone number `01 23 45 67 89` and a cell
# mixing two marks out of the numbers. It also keeps out the Indian
# grouping `12,34,567`, whose later groups are two figures: such a
# column is read as text, and that is a stated limit rather than an
# oversight.
#
# A FIRST GROUP MAY BEGIN WITH A ZERO, for every mark alike, because the
# comma always allowed it (`012,345` has read as 12345 since Phase 1).
# Such a cell is written in the padded form and a padded form is never
# grouped, so it withholds the mark from its column.
GROUP_MARKS = (",", " ", "'", "\u2019", "\u00a0", "\u202f", "\u2009")

# EVERY MARK A DESCRIPTION MAY PUBLISH BETWEEN THOUSANDS: none, the seven
# above, and the point a declared decimal comma writes (contract GS1).
PUBLISHED_GROUP_MARKS = (
    "", ",", ".", " ", "'", "\u2019", "\u00a0", "\u202f", "\u2009"
)

# EACH PUBLISHED MARK IN THE WORDS A PAGE USES FOR IT, because four of
# them cannot be seen when printed. One list, read by the summary and by
# the quality report alike, so the two name a mark one way.
GROUP_MARK_WORDS = (
    ("", "no mark"),
    (",", "a comma"),
    (".", "a point"),
    (" ", "a space"),
    ("'", "an apostrophe"),
    ("\u2019", "a right single quotation mark"),
    ("\u00a0", "a no-break space"),
    ("\u202f", "a narrow no-break space"),
    ("\u2009", "a thin space"),
)

# THE MINUS SIGN of the character tables, which typeset exports write
# where a keyboard writes the hyphen-minus. Read as a minus (landing
# 2b.2): before, `\u22126.09` was an affixed number wearing the sign as
# its prefix, and its column published no negative value at all.
MINUS_SIGN = "\u2212"

# HOW A NEGATIVE NUMBER IS WRITTEN, one name per notation the reader
# accepts (landing 2b.2). The hyphen-minus in front; accounting brackets
# around the figures; the minus sign of the character tables in front;
# and the hyphen-minus AFTER the figures, which accounting systems write
# as `1,483.65-`. The first is the default a description publishes.
NEGATIVE_MINUS = "minus"
NEGATIVE_BRACKETS = "brackets"
NEGATIVE_MINUS_SIGN = "minus_sign"
NEGATIVE_TRAILING = "trailing_minus"
NEGATIVE_FORMS = (
    NEGATIVE_MINUS,
    NEGATIVE_BRACKETS,
    NEGATIVE_MINUS_SIGN,
    NEGATIVE_TRAILING,
)

# WHETHER A COLUMN'S WIDE RUNS OF FIGURES ARE THEIR OWN VALUES' TEXT
# (landing 2b.13, plan P4-D90, closing the canonical residual of
# P4-D66.2). Past 2**53 more than one run of figures reads back as one
# binary64, so "a spelling of its own value" stops picking out a single
# text and the canonical question has to be asked of the column rather
# than derived from the number. These three words are the answer, and a
# description carries exactly one of them:
#
# * `none` -- the column wrote no point-free cell at or past 2**53, so
#   there is no such run to ask about;
# * `canonical` -- it wrote some, and FEWER of them than the census
#   floor are anything but the text their own values write;
# * `respelled` -- it wrote some, and at least the census floor of them
#   are not.
#
# The word is a fact about the column's WRITER and never about a cell:
# it names no count, no position and no figure. AND NO ONE CELL MOVES
# IT (plan P4-D140, the final Codex review's first BLOCKER). The first
# version put the line between nought and one, so 800 canonical keys
# published `canonical` and the same column with ONE key respelled
# published `respelled`: a reader who knew the other 799 cells read off
# the last one's spelling from the word alone. The line now stands at
# `census_floor`, where a word moves only when a group moves it.
WIDE_NONE = "none"
WIDE_CANONICAL = "canonical"
WIDE_RESPELLED = "respelled"
WIDE_RUNS = (
    WIDE_NONE,
    WIDE_CANONICAL,
    WIDE_RESPELLED,
)

# THE SMALLEST GROUP A RUN USES WHEN NOBODY ASKS FOR ANOTHER, and the one
# place the number is written (owner, 2026-09-22; plan P4-D316). It is 11,
# the value it held before amendment A-P4-37 and the same number as the
# notice line (`contract.SMALL_GROUP_NOTICE_LINE`), so a run nobody
# lowered names no group of fewer than eleven rows. It lives in this
# module because every module that needs it -- the taxonomy's settings,
# the loader, the reader, the file's written form and the command line
# -- already imports this one and this one imports nothing, so no module
# gains an edge in the import graph by reading it. `--smallest-group`
# below it stays legal and keeps its lowered-floor alarm.
DEFAULT_SMALL_CELL_FLOOR = 11


def census_floor(floor: int) -> int:
    """The smallest count a spelling census publishes: two, or the floor.

    NEVER ONE, WHATEVER THE SETTINGS FLOOR (owner twin definition,
    clause 3; plan P4-D65.1). A published count of one names an
    individual outright, and a person may lower the settings floor to
    one with `--smallest-group 1`.

    ONE STATEMENT OF THE RULE, read by the producer, the loader and the
    checker alike (plan P4-D140). It lives in this module because it is
    the one all three import.

    Guarantees: accepts the settings floor; returns two or the floor,
    whichever is larger. Determinism: a fixed function of the floor.
    Raises nothing. No I/O of any kind.
    """
    if floor > 2:
        return floor
    return 2


def census_nameable(
    counts: "list[int]", populations: "list[int]", floor: int
) -> bool:
    """Whether a census may print these counts: THE DISCLOSURE RULE, once.

    Written once for every spelling census landings 2b.2 and 2b.7 added
    (plan P4-D140, closing the final Codex review's grouping BLOCKER),
    so no census states its own version and drifts from the others. The
    four censuses of how a column's dates were written ask it too (plan
    P4-D131, through `disclosed_census` and the loader's D17 to D20),
    and so does the letter-case and layout census of the label roles
    wherever it asks whether a reading names one row.
    It says two things, and a census that fails either prints no count:

    1. EVERY COUNT NAMES A GROUP. Each count it would print -- a named
       convention and a pooled remainder alike -- reaches
       `census_floor`, so none of them is one.
    2. SO DOES EVERY COMPLEMENT A READER CAN TAKE. For each population
       handed in -- the cells a reader can subtract the printed total
       from, such as the cells written with a point, the cells that
       could be grouped, or every number of the column -- what is left
       once the printed counts are taken off is either nought or
       reaches `census_floor` too. Measured without this clause: 1,200
       grouped prices at a floor of eleven, one of them rewritten bare,
       published `{",": 1199}` beside a row count of 1,200, and the one
       ungrouped cell was read off by subtraction.

    NOUGHT LEFT OVER IS ALLOWED, and that is a decision rather than an
    oversight: it says every such cell was written one way, which is a
    fact about the column's writer. What a census that cannot speak
    publishes instead is the census's own decision, and each one states
    it; none of them may publish a state a reader can tell from the
    state nought reaches, where the category is implied.

    Guarantees: accepts the counts that would be printed, the
    populations a reader can subtract them from and the settings floor;
    returns a bool. Determinism: a fixed function of the three. Raises
    nothing. No I/O of any kind.
    """
    least = census_floor(floor)
    total = 0
    for count in counts:
        if count < least:
            return False
        total = total + count
    for population in populations:
        rest = population - total
        if rest != 0 and rest < least:
            return False
    return True


def width_census_breaches(
    styles: "dict[str, int]",
    padded: "dict[str, int]",
    fields: "dict[str, int]",
    floor: int,
) -> "tuple[bool, list[str]]":
    """Where the width censuses let a reader subtract a count too small to name.

    THE DISCLOSURE RULE OF `census_nameable`, ASKED OF THE SIBLING
    CENSUSES A READER SUBTRACTS FROM EACH OTHER (plan P4-D148, the repair
    pass of the final Codex review). Each width census floors its own
    counts, and that is not enough: two published counts can each be a
    group while their difference is one person. Measured at a floor of
    eleven, both on the tool as the review found it and after P4-D145:

    1. THE PLUS ROUTE. `pad_widths` counts every `leading_zero` cell and
       every plus-signed padded one, and `numeric_styles` names the
       `leading_zero` count, so the census's total less that count is
       the number of plus-signed padded cells, and the `leading_plus`
       count less THAT is the plus-signed cells with no pad. 800 padded
       keys, fifty `+k` and one `+00123` published `pad_widths {"5":
       801}` beside `leading_zero: 800`.
    2. THE WIDTH ROUTE. At a width both censuses name, `field_widths`
       less `pad_widths` is the number of cells written at that width
       with no pad. 800 padded five-figure codes beside one `12345`
       published `field_widths {"5": 801}` beside `pad_widths {"5":
       800}`. Where `pad_widths` pools and `field_widths` does not, and
       exactly one field width of two figures or more is left that the
       padded census does not name, the pool is at that width and is
       subtracted there too.

    Each difference is nought or reaches `census_floor`. A pooled
    remainder of a width census is a mixture of widths no reader can
    take apart, and is not a count this rule asks about.

    AT EVERY FLOOR, A FLOOR OF ONE INCLUDED (plan P4-D221; stage 2
    closed by the owner rulings of 2026-09-17). This rule was not asked at
    a settings floor of one, where the width censuses named counts of one
    outright and invariant S13 forbade the pool its remedy needs. The
    censuses now name no count below `census_floor`, whose line is two
    there, and their pools stand at a floor of one
    (`canonical.POOLED_AT_ANY_FLOOR`), so a difference of one is refused
    at every floor. The plus route also subtracts from the forms map's
    pool where `leading_plus` is held back in it.

    Guarantees: accepts the forms map, the two width censuses and the
    settings floor, as published; returns whether the plus route breaks
    the rule and the field widths, in ascending key order, at which the
    width route does. Determinism: a fixed function of the four. Raises
    nothing. No I/O of any kind.
    """
    least = census_floor(floor)
    pool = MISSING_WITHHELD
    total = 0
    for width in padded:
        total = total + padded[width]
    plus_broken = False
    plus_cells = -1
    if STYLE_LEADING_ZERO in styles:
        plus_cells = total - styles[STYLE_LEADING_ZERO]
    elif pool not in styles:
        plus_cells = total
    if plus_cells > 0:
        rest: "list[int]" = []
        if STYLE_LEADING_PLUS in styles:
            rest = [styles[STYLE_LEADING_PLUS]]
        elif pool in styles:
            rest = [styles[pool]]
        plus_broken = not census_nameable([plus_cells], rest, floor)
    named: "list[int]" = []
    for width in fields:
        if width != pool:
            named += [int(width)]
    unnamed: "list[str]" = []
    for figures in sorted(named):
        width = f"{figures}"
        if width not in padded and figures >= 2:
            unnamed += [width]
    broken: "list[str]" = []
    for figures in sorted(named):
        width = f"{figures}"
        known = padded[width] if width in padded else 0
        if pool in padded and pool not in fields and unnamed == [width]:
            known = known + padded[pool]
        if known < 1:
            continue
        rest_cells = fields[width] - known
        if rest_cells != 0 and rest_cells < least:
            broken += [width]
    return plus_broken, broken



# THE FIRST WHOLE NUMBER BINARY64 CANNOT KEEP EVERY FIGURE OF. Below it
# a whole number is held exactly and one run of figures reads back as
# it; at it and past it the spacing reaches two and neighbouring runs
# collapse onto one value. Written out rather than computed so that the
# reader, the loader and the checker all read one number.
WIDE_RUN_FLOOR = 9007199254740992.0


def is_a_wide_run(text: str, value: float) -> bool:
    """Whether one cell is a bare run of figures past what binary64 keeps.

    The class the canonical question is asked of, and the same class
    `validation._wears_a_whole_number_text` admits: a point-free run of
    base-ten figures, with or without a leading sign, whose value is at
    or past `WIDE_RUN_FLOOR` in either direction.

    ASKED OF THE CORE, for the reason `fraction_width` and `pad_width`
    are (landing 2b.13's repair pass, plan P4-D91). This rule read the
    RAW text when it arrived, while the form it is filed beside came off
    `number_core` and the checker's own class test came off the trimmed,
    minus-first cell -- so a cell wearing accounting brackets, the minus
    sign of the character tables, a surrounding space or a thousands
    mark was one class to the producer and another to the checker. Two
    defects came out of that one split, both measured through the real
    command line at 800 rows and floor eleven, on two seeds each:

    * ONE cell of eight hundred given a leading space and respelled made
      a REAL table fail its own description at exit 3 on
      `styles.canonical.wide`, while its twin passed -- the very false
      accusation plan P4-D66.2 exists to end. A column of bracketed
      negatives respelled on the bracketed half did the same, 388 and
      392 cells moved;
    * a column of 800 wide runs written with thousands marks, or with a
      leading space on every cell, published `none` -- a false statement
      about the file -- and the respelling this fact exists to catch
      went unseen on all 800.

    One core for every reader of a cell's form is the rule those two
    broke, and it is the rule `number_core`'s own docstring states.

    Guarantees: accepts a written cell and the value it read back as;
    returns whether it is one of that class. Determinism: a fixed
    function of the two. Raises TypeError if handed anything that is not
    a string instance, through `number_core`. No I/O of any kind.
    """
    digits = number_core(text)
    if digits[:1] == "-" or digits[:1] == "+":
        digits = digits[1:]
    if not digits:
        return False
    for character in digits:
        if character < "0" or character > "9":
            return False
    return value <= -WIDE_RUN_FLOOR or value >= WIDE_RUN_FLOOR


def wide_run_figures(value: float) -> str:
    """The figures the value itself writes, without its sign.

    The canonical point-free text of method G6.2 read for one value:
    past `WIDE_RUN_FLOOR` every binary64 is a whole number, so the exact
    integer is the value and `int` loses nothing taking it.
    """
    whole = int(value)
    if whole < 0:
        whole = -whole
    return f"{whole}"


def _minus_written_first(body: str) -> str:
    """The text with a minus sign or a trailing minus written in front.

    Two notations for "negative" are rewritten as the hyphen-minus in
    front, which is the only one every rule below reads: `\u22125` and
    `5-` both become `-5`. A trailing minus is taken only where nothing
    else signs the text, so `-5-` and `+5-` stay what they were -- text
    this reader refuses -- and a lone `-` is not a sign of anything.
    Everything else comes back unchanged.
    """
    if not isinstance(body, str):
        raise TypeError(_NOT_TEXT)
    if body[:1] == MINUS_SIGN:
        return "-" + body[1:]
    if (
        len(body) > 1
        and body[len(body) - 1 : len(body)] == "-"
        and body[:1] != "-"
        and body[:1] != "+"
        and _written_as_an_amount(body)
    ):
        return "-" + body[: len(body) - 1]
    return body


def _written_as_an_amount(body: str) -> bool:
    """Whether figures carry a decimal point.

    THE TRAILING MINUS IS READ ONLY ON AN AMOUNT (landing 2b.2).
    Accounting systems write `1,483.65-` and `12.50-`; a grade or a code
    writes `3-`, and nothing in one such cell tells the two apart. So a
    hyphen-minus after the figures is read as a minus only where the
    figures carry a decimal point, and `3-` stays text.

    NOT A THOUSANDS MARK, and it was one until the verification of this
    landing. A ledger of whole amounts writes `1,234-` beside `500-`:
    read on a mark, the first was a negative number and the second text,
    so one column split into two classes by the size of each value, and
    its twin wrote a different count of numbers on 1 seed of 6. A point
    is a fact of the column's form -- a column of amounts written with
    cents writes one on every cell -- while a mark is a fact of a value's
    size. A whole amount's minus after its figures is kept as text in
    every cell alike, and contract NF57 names it.
    """
    for character in body:
        if character == ".":
            return True
    return False


def _groups_marked(head: str) -> str:
    """The one mark grouping ``head``'s figures, or "" where none is valid.

    ``head`` is a whole part with no sign, no point and no exponent. The
    answer is a mark of `GROUP_MARKS` only where exactly one kind of mark
    stands in it and the figures read as thousands groups around it.
    """
    seen = ""
    for character in head:
        if character in GROUP_MARKS and character not in seen:
            seen = seen + character
    if len(seen) != 1:
        return ""
    if not _groups_by_threes(head, seen):
        return ""
    return seen


def _without_group_separators(text: str) -> "str | None":
    """Remove valid thousands separators, or return None if they are not.

    A mark of `GROUP_MARKS` is accepted only where a thousands separator
    can appear: the part before the decimal point must read as groups of
    exactly three digits after a first group of one to three digits,
    with ONE kind of mark between them. '1,234,567.89' and '1 234 567.89'
    become '1234567.89'; '1,23', '12,3456', '123 45' and '1,234 567' are
    refused, because accepting them would turn a mistyped value, a
    postcode or a mixed spelling into a plausible number. A mark after
    the point is refused the same way.

    AN EXPONENT IS TAKEN OFF FIRST, and it was not until 2026-08-26
    (residual R-P4-32). `1,001e2` is admitted by the documented grammar
    -- valid group separators, an optional exponent -- and `1,001` and
    `1001e2` are both read as numbers, but the pair together was not:
    with no point, everything after the last comma was taken as a
    group, `001e2` is not three figures, and the cell was not a number
    at all. The affix rule could then claim the column and publish a
    mean over the mantissas. The exponent is split off before the
    groups are counted and put back after.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    marked = False
    for character in text:
        if character in GROUP_MARKS:
            marked = True
    if not marked:
        return text
    sign = ""
    body = text
    if text[0] == "+" or text[0] == "-":
        sign = text[0]
        body = text[1:]
    # The exponent, if this cell carries one, kept aside while the
    # groups are counted. Only a well-formed one is taken: figures,
    # after an optional sign, after a single `e` or `E`. Anything else
    # stays in the body and is refused by the group rule as before.
    exponent = ""
    for marker in ("e", "E"):
        # The LAST place the marker stands, found by walking rather than
        # by `rfind`: the offline audit clears an enumerated set of
        # string methods and `rfind` is not in it.
        at = -1
        seat = 0
        while seat < len(body):
            if body[seat] == marker:
                at = seat
            seat = seat + 1
        if at <= 0:
            continue
        after = body[at + 1 :]
        digits = after
        if digits and (digits[0] == "+" or digits[0] == "-"):
            digits = digits[1:]
        if digits and _all_ascii_digits(digits):
            exponent = body[at:]
            body = body[:at]
        break
    point = body.find(".")
    if point < 0:
        head = body
        tail = ""
    else:
        head = body[:point]
        tail = body[point:]
    for character in tail:
        if character in GROUP_MARKS:
            return None
    mark = _groups_marked(head)
    if not mark:
        return None
    joined = ""
    for character in head:
        if character != mark:
            joined = joined + character
    return sign + joined + tail + exponent


def number_core(text: str) -> str:
    """One numeric cell reduced to the figures every form rule reads.

    Surrounding spaces come off; a matching pair of accounting brackets
    is unwrapped and trimmed again and read as a minus in front; a minus
    sign or a trailing minus is written as the hyphen-minus in front;
    and every mark of `GROUP_MARKS` is dropped. `(1,234.50)`,
    `1 234.50-` and `\u22121'234.50` all come back `-1234.50`, and
    `+1 234.5` comes back `+1234.5`.

    ONE CORE FOR EVERY READER OF A CELL'S FORM (landing 2b.2). The form
    ladder, the fraction and padding widths and the whole-figure count
    each stripped the comma and the brackets for themselves; a reader
    that learned the new marks or the new signs while its neighbour did
    not would count one cell in two forms, which is the defect class
    `fraction_width`'s docstring names.

    Guarantees: accepts any text; returns text. Sensible only for a cell
    that reads as a number; any other text comes back with the same
    rewriting applied and means nothing. Determinism: a fixed function
    of the text. Raises TypeError if handed anything that is not a
    string instance, through `trimmed`. No I/O of any kind.
    """
    body = trimmed(text)
    bracketed = False
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        bracketed = True
        body = trimmed(body[1 : len(body) - 1])
    body = _minus_written_first(body)
    core = ""
    for character in body:
        if character not in GROUP_MARKS:
            core = core + character
    if bracketed and core[:1] != "-" and core[:1] != "+":
        core = "-" + core
    return core


def thousands_mark(text: str) -> str:
    """The mark this cell writes between its thousands, or "" for none.

    A mark of `GROUP_MARKS`, answered only where the cell's whole part
    reads as thousands groups around ONE kind of mark -- the same rule
    `_without_group_separators` reads a number by, asked of a cell that
    may carry brackets, any accepted sign and an exponent. `2 198.92`
    answers a space, `(1,234.50)` a comma, `1234.50` and `123 45` the
    empty string.

    Guarantees: accepts any text; returns "" or one mark of
    `GROUP_MARKS`. Determinism: a fixed function of the text. Raises
    TypeError if handed anything that is not a string instance. Boundary:
    no figure of the cell travels out through it. No I/O of any kind.
    """
    body = trimmed(text)
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        body = trimmed(body[1 : len(body) - 1])
    body = _minus_written_first(body)
    if body[:1] == "+" or body[:1] == "-":
        body = body[1:]
    cut = len(body)
    for place in range(len(body)):
        if body[place] == "." or body[place] == "e" or body[place] == "E":
            cut = place
            break
    for character in body[cut:]:
        if character in GROUP_MARKS:
            return ""
    return _groups_marked(body[:cut])


def negative_notation(text: str) -> str:
    """How one cell that reads as a negative number wrote its sign.

    One of `NEGATIVE_FORMS`: brackets around the figures, the minus sign
    of the character tables in front, a hyphen-minus after the figures,
    or the hyphen-minus in front. Asked only of a cell the reader has
    classified as a negative number; a cell written any other way
    answers `NEGATIVE_MINUS`, which is what a reader who learned none of
    the other three would have taken it for.

    Guarantees: accepts any text; returns one of the four names.
    Determinism: a fixed function of the text. Raises TypeError if
    handed anything that is not a string instance. Boundary: the answer
    is a word of this module's own vocabulary. No I/O of any kind.
    """
    body = trimmed(text)
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        return NEGATIVE_BRACKETS
    if body[:1] == MINUS_SIGN:
        return NEGATIVE_MINUS_SIGN
    if _minus_written_first(body) != body:
        return NEGATIVE_TRAILING
    return NEGATIVE_MINUS


def with_negative_notation(text: str, form: str) -> str:
    """A number written with a hyphen-minus in front, in ``form`` instead.

    A TRAILING MINUS IS WRITTEN ONLY WHERE IT READS BACK AS ONE: a figure
    field carrying no point keeps its hyphen-minus in front, because
    `12-` and `1,234-` are not read as numbers (`_written_as_an_amount`)
    and writing either would change the cell's class.

    The write rule of `negative_form`: `-1,234.50` becomes `(1,234.50)`,
    `\u22121,234.50` or `1,234.50-`. Text that does not begin with a
    hyphen-minus -- a positive value, a zero, a stand-in -- comes back
    unchanged, and so does every text under `NEGATIVE_MINUS`. Brackets
    never hold a sign, so a written negative can never be mistaken for
    the contradictory-notation stand-in `(-5)`.

    Guarantees: accepts a written number and one of `NEGATIVE_FORMS`;
    returns text. Determinism: a fixed function of the two. Raises
    TypeError if handed anything that is not a string instance. No I/O.
    """
    if not isinstance(text, str) or not isinstance(form, str):
        raise TypeError(_NOT_TEXT)
    if text[:1] != "-":
        return text
    body = text[1:]
    if form == NEGATIVE_BRACKETS:
        return "(" + body + ")"
    if form == NEGATIVE_MINUS_SIGN:
        return MINUS_SIGN + body
    if form == NEGATIVE_TRAILING:
        if not _written_as_an_amount(body):
            return text
        return body + "-"
    return text


# The longest cell a shape form is taken of. A form is a fact about the
# WRITING of a value, and on a short cell it is a fact about a code; on
# a long one it would start to be a fact about a sentence -- word
# lengths, where the commas fall -- which is a different thing to
# publish and is not what the form is for.
SHAPE_FORM_LIMIT = 24

# THE ONLY CHARACTERS A FORM MAY CARRY BESIDE THE TWO PLACEHOLDERS,
# and the list
# is CLOSED and belongs to this tool (plan P4-D18, review round 1). A
# cell holding a character the list omits has no form: a space, or a
# mark no coding scheme uses.
#
# WHY A CLOSED LIST RATHER THAN "EVERY OTHER CHARACTER STANDS". Because
# the guarantee this census rests on is that a key carries no fragment
# of anybody's value, and "replace the ASCII letters and figures" does
# not give it: a column of Japanese clinical text published a key still
# holding the words themselves, since no ASCII rule reached them. That
# is a leak in the one field these roles have for saying what their
# values look like. A closed list is checkable -- a key holds `9`, `A`
# and marks from this string, or it is refused -- and what it costs is
# a form for cells nobody was going to read as codes anyway.
#
# THE SPACE IS EXCLUDED ON ITS OWN GROUND, not as an oversight. Two
# hundred and forty different short sentences written to one template
# all share the form `AAAAA, AAAA!`, and that names every word's
# length, where the spaces fall and where the punctuation falls -- a
# fact about a sentence, which is what the length limit was already
# there to keep out. Without a space, the cells that share a form are
# the cells written to a scheme.
SHAPE_MARKS = "-./_:#*()[]+,"

# THE TWO PLACEHOLDERS, AND WHY THEY ARE NOT `9` AND `A` (review round
# 2 finding 1). They were, and they read beautifully, and they were
# wrong: a form built from `9`, `A` and marks is a string a CELL can
# also be spelled with, so a form could BE a value. Every form of
# length one to three over that alphabet -- all 1230 of them -- was its
# own form. `A99` is a real diagnosis code, so a column holding three
# patients coded `A99` had that code held back by the floor and
# published straight back as a census key.
#
# THE PROPERTY THESE TWO BUY, and it holds without looking at any data.
# A form carries at least one placeholder, because a form needs two of
# the three kinds and two of the three ARE the placeholders. A cell
# that HAS a form carries only letters, digits and marks. Neither
# placeholder is any of those. So NO CELL THAT HAS A FORM CAN BE
# SPELLED THE SAME AS ANY FORM -- in any column, in any table.
#
# Both are already outside `SHAPE_MARKS`, so no cell loses a form it
# had before: the only thing that changes is how a key is spelled.
# `%` and `@` are what a number-format language calls a digit and a
# text placeholder, so the pair is not invented here. The cost is
# read-ability -- `@%%.%` is not `A99.9` -- and it is paid in prose,
# in the sentence the report prints beside every form it names.
SHAPE_DIGIT = "%"
SHAPE_LETTER = "@"
# THE THIRD PLACEHOLDER, AND IT IS A CENSUS KEY'S ALONE (landing 2b.18
# part 2, plan P4-D121, audit LTM-6). `shape_form` never writes it: the
# form of a cell stays blind to case, so no level, no variant and no
# per-level count moves. What writes it is the census, and only for the
# cells of one form whose every letter was lower case, where enough of
# them share that form to be named on their own (C6-31a). A column of
# `e9z-1i1` published `@%@-%@%` and its twin came back `Y6O-7P3` on
# every row, so a case-sensitive pattern matched 800 real cells and 0
# twin cells while both files passed. `&` is outside the letters, the
# figures and `SHAPE_MARKS`, so no cell that has a form can be spelled
# like a key carrying it, which is the property the other two buy.
SHAPE_LOWER = "&"


def _is_a_digit(character: str) -> bool:
    """Whether one character is a figure `0` to `9`.

    THE RANGE IS FIXED HERE AND NOT ASKED OF THE INTERPRETER (review
    round 2 finding 14). It was `str.isdigit`, which answers out of the
    Unicode database the running Python carries -- and this package
    supports five of them. U+16AC0 TANGSA DIGIT ZERO is a digit on
    3.11 and not on 3.10; U+1E4D0 NAG MUNDARI LETTER O is a letter on
    3.12 and not on 3.11; U+10D50 GARAY CAPITAL A is a letter on 3.14
    and not on 3.13. So the same table produced a different census, a
    different profile and a different twin on two supported
    interpreters -- and, measured, a twin built on one and validated on
    another was reported as MISSING two exact counts it in fact held.

    A cell holding any character outside these ranges has no form at
    all, which is the `else` branch of `shape_form`. That costs a
    column of non-ASCII codes its census -- and it was going to lose it
    anyway, because a twin can only write the alphabets G9.1 gives it
    and none of them holds a letter outside ASCII, so the band check
    refuses every spelling of such a form. What is bought is a census
    that says the same thing on every interpreter this package runs on.
    """
    if not isinstance(character, str):
        raise TypeError(_NOT_TEXT)
    return "0" <= character <= "9"


def _is_a_letter(character: str) -> bool:
    """Whether one character is a letter `a` to `z` or `A` to `Z`.

    The range is fixed here for the reason `_is_a_digit` gives: a
    census that asks the interpreter what a letter is answers
    differently on different supported interpreters.
    """
    if not isinstance(character, str):
        raise TypeError(_NOT_TEXT)
    return ("a" <= character <= "z") or ("A" <= character <= "Z")


def shape_form(text: str) -> str:
    """The shape of one cell: its figures and letters, its marks kept.

    Every FIGURE `0`-`9` becomes `SHAPE_DIGIT`, every LETTER `a`-`z`
    or `A`-`Z` becomes `SHAPE_LETTER`, and every other character must
    be one of `SHAPE_MARKS` and stands as itself, because the marks are
    the STRUCTURE and the letters and figures are the content. A
    diagnosis code `E11.9` has the form `@%%.%`; a laboratory code
    `4548-4` has `%%%%-%`; a blood pressure `120/80` has `%%%/%%`; a
    dispensed-drug code `0002-8215-01` has `%%%%-%%%%-%%`.

    A CELL HOLDING ANYTHING ELSE HAS NO FORM -- a letter of another
    alphabet, a space, a mark this list leaves out, a placeholder. The
    two rules that narrow it were each learned from a defect. Letting
    an unreplaced character STAND let a column of Japanese clinical
    text publish a key holding the words (review round 1 finding 1);
    asking the INTERPRETER what a letter is made the census depend on
    which Unicode database it carries, and five supported versions
    disagree (round 2 finding 14).

    AND A FORM CARRIES TWO OF THE THREE KINDS, or it is not a form.
    `@@@@@` says five letters, which `length` and the two alphabet
    counts already say between them; what a form is FOR is the ORDER
    of the kinds and where the marks fall between them.

    WHAT THIS IS FOR. A column whose values the disclosure floor holds
    back publishes nothing about them today, so its twin holds
    `group-14` -- which is not a code, is not the right length, and on
    a column of hyphenated codes even splits into two parts and reads
    as one. A form lets the twin hold something of the right shape
    without holding anything of the value: `@%%.%` says a letter, two
    figures, a point and a figure, and says nothing about WHICH.

    WHAT IT DELIBERATELY WILL NOT DO. A cell has NO FORM when it is
    empty, when it is longer than `SHAPE_FORM_LIMIT`, or when it holds
    any character that is neither a letter, nor a digit, nor one of
    `SHAPE_MARKS` -- a space among them. On a note or an address a form
    would carry where the spaces and the commas fall and how long each
    word is, which is a fact about a sentence rather than about a code,
    and this census is not the place to decide whether that may be
    published. Such a cell answers the empty string.

    Guarantees: accepts any string; returns a form built only from the
    two placeholders and `SHAPE_MARKS`, or "" for a cell this census does not
    describe. Determinism: the answer depends only on the text. Raises
    TypeError if handed anything that is not a string instance.
    Boundary: no figure and no letter of the cell survives into the
    answer -- only how many there were, and where the marks between
    them fell. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text or len(text) > SHAPE_FORM_LIMIT:
        return ""
    form = ""
    kinds = 0
    figures = 0
    letters = 0
    marks = 0
    for character in text:
        if character == SHAPE_DIGIT or character == SHAPE_LETTER:
            # A CELL CARRYING A PLACEHOLDER HAS NO FORM. This is what
            # makes the disjointness above a property and not a hope:
            # without it a cell spelled `@%%` would have the form
            # `@%%` and be its own form again.
            return ""
        if _is_a_digit(character):
            form = form + SHAPE_DIGIT
            figures = 1
        elif _is_a_letter(character):
            form = form + SHAPE_LETTER
            letters = 1
        elif character in SHAPE_MARKS:
            form = form + character
            marks = 1
        else:
            return ""
    kinds = figures + letters + marks
    if kinds < 2:
        # A FORM OF ONE KIND OF SYMBOL SAYS NOTHING NEW, so it is not a
        # form. `AAAAA` says five letters and `99999` says five
        # figures -- and `length` already publishes the five exactly,
        # while `n_all_digits` and `n_code_alphabet` already publish
        # which alphabet the cell was drawn from. Naming those adds a
        # published fact that carries no information and costs a
        # disclosure line, and it made a column of four region names
        # publish a census nobody could use.
        #
        # WHAT A FORM IS FOR is the ORDER of the kinds and where the
        # marks fall between them: `A9999` says a letter and then four
        # figures, which no other published fact says; `9999-9` says
        # where the hyphen is. Two kinds is exactly the line between
        # the two.
        return ""
    return form


def form_room(name: str) -> int:
    """How many different cells could have worn this form.

    Every `SHAPE_DIGIT` of it stands for one of ten figures, every
    `SHAPE_LETTER` for one of fifty-two letters and every `SHAPE_LOWER`
    for one of twenty-six lower-case ones; the marks stand for
    themselves. So a form is a COUNT of the cells it could have come
    from, and that count is what says whether naming it tells a reader
    anything they did not already have.

    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    room = 1
    for character in name:
        if character == SHAPE_DIGIT:
            room = room * 10
        elif character == SHAPE_LETTER:
            room = room * 52
        elif character == SHAPE_LOWER:
            # A LOWER-CASE LETTER IS ONE OF TWENTY-SIX, not fifty-two,
            # so the small-supply rule asks a lower-case key for its own
            # room and never for the case-blind form's (P4-D121).
            room = room * 26
    return room


def is_a_written_form(name: str) -> bool:
    """Whether ``name`` is a written form: THE one definition of it.

    The producer builds a form (`shape_form`), the loader admits a
    census key, and the publication guard refuses one -- and those three
    were three separate readings of the same rule, which is how the
    loader and the guard came to accept `AAAA`, `9999` and `----`,
    keys the producer can never write and every recount then misses
    (review round 2 finding 2). There is one definition now and the
    other two call it.

    A form is one to `SHAPE_FORM_LIMIT` characters, every one of them a
    placeholder or a mark from the closed list, carrying at least TWO
    of the three kinds -- figure, letter, mark. Two kinds, because a
    key of one kind says nothing `length` and the two alphabet counts
    do not already say. A letter is written `@` or, in a key the census
    names for lower-case cells, `&` -- one or the other throughout, and
    never both in one key (plan P4-D121).

    Guarantees: accepts any string; answers only from the characters.
    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    if not name or len(name) > SHAPE_FORM_LIMIT:
        return False
    figures = 0
    letters = 0
    lower = 0
    marks = 0
    for character in name:
        if character == SHAPE_DIGIT:
            figures = 1
        elif character == SHAPE_LETTER:
            letters = 1
        elif character == SHAPE_LOWER:
            lower = 1
        elif character in SHAPE_MARKS:
            marks = 1
        else:
            return False
    if letters and lower:
        # A KEY IS WRITTEN IN ONE CONVENTION OR THE OTHER (P4-D121).
        # The census writes `&` for EVERY letter of a form whose cells
        # were all lower case and `@` for every letter otherwise, so a
        # key mixing the two is one no producer writes and no recount
        # can ever meet.
        return False
    return figures + max(letters, lower) + marks >= 2


def is_lower_case_text(text: str) -> bool:
    """Whether a cell holds a letter and every letter it holds is lower case.

    The letters are `a`-`z` and `A`-`Z` and nothing else, for the reason
    `_is_a_letter` gives. A cell with no letter at all is not lower
    case: it has no case to keep, and its form has no letter to mark.

    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    seen = False
    for character in text:
        if "A" <= character <= "Z":
            return False
        if "a" <= character <= "z":
            seen = True
    return seen


def lower_case_form(form: str) -> str:
    """The census key a form takes for its lower-case cells (P4-D121).

    Every `SHAPE_LETTER` becomes `SHAPE_LOWER` and every other character
    stands. A form with no letter has no lower-case key and answers "".

    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(form, str):
        raise TypeError(_NOT_TEXT)
    if SHAPE_LETTER not in form:
        return ""
    built = ""
    for character in form:
        if character == SHAPE_LETTER:
            built = built + SHAPE_LOWER
            continue
        built = built + character
    return built


def census_form(text: str, census: "dict[str, int]") -> str:
    """The key of a form census one cell is counted under (C6-31a).

    THE ONE READING A GENERATOR AND A RECOUNT BOTH USE, so what the twin
    is written to and what it is measured by cannot part. A cell's form
    is `shape_form`, blind to case. Where every letter of the cell is
    lower case AND the census names that form's lower-case key, the cell
    is counted there; every other cell is counted under its form as
    `shape_form` writes it. So a census naming `&&%` beside `@@%` counts
    `ab1` under the first and `AB1` or `Ab1` under the second, and a
    census naming only `@@%` counts all three under it, exactly as
    before the lower-case key existed.

    Guarantees: accepts a string and a census; returns a key or "" for a
    cell with no form. Determinism: a function of the two arguments
    alone. Raises TypeError if handed a cell that is not a string. No
    I/O of any kind.
    """
    form = shape_form(text)
    if not form or SHAPE_LETTER not in form:
        return form
    if not is_lower_case_text(text):
        return form
    lower = lower_case_form(form)
    if lower in census:
        return lower
    return form


# -- the disclosure rule, asked by the label roles (plan P4-D150) -----


def census_names_one_row(
    counts: "dict[str, int]",
    totals: "list[tuple[int, int]]",
    floor: int = 1,
) -> int:
    """Which reading of a census names one row of the table, or -1.

    THE ONE DISCLOSURE RULE, `census_nameable`, ASKED AT ITS LINE OF TWO
    (plan P4-D150), so that the producer that writes a label role's form
    or layout census and the loader that reads one ask ONE question and
    cannot part. The line is two and not the settings floor because these
    censuses pool what falls below the floor by design (invariant S13):
    their named counts already reach the floor, and what this asks is
    whether any reading is ONE. This is not a second statement of the
    rule: at the merge of the labels repair into the integration, where
    the numbers repair had already written the rule once, this function
    was re-expressed as `census_nameable` at a floor of one, whose line is
    two, over each reading in turn, so that it can say WHICH reading
    failed. A census names one row in two ways, and both are refused:

    - a count it publishes is one, the pool included;
    - a total the reader holds beside it, less the cells the census
      covers inside that total, is one. ``totals`` is those pairs, each
      ``(total, covered)``. A pair is read only where the census covers
      at least one cell of that total, because a census that says
      NOTHING about a total -- the empty census above all -- leaves the
      reader nothing to subtract: an absent census is absent, and the
      total beside it is a fact published on its own terms.

    The answer is ``-2`` for a count of one, the place in ``totals`` of
    the first pair whose difference is one, and ``-1`` where the census
    names no row, so a producer can repair the reading that failed.

    ``floor`` NAMES THE LINE, AND IT DEFAULTS TO THE LINE OF TWO (round
    2 of the review, the disclosure pass, item 2; the repair pass of
    this landing). Every caller written before this argument leaves it
    out and asks exactly what it asked, because `census_floor(1)` is
    two. It is here for the reading whose S13 reasoning does NOT hold:
    a census's own pooled remainder is published beside it, so what the
    reader gets back by subtracting it is already a fact the description
    states, and the question is only whether any reading is ONE. A
    judged stand-in number's `n_occurrences` less its named spellings
    is not like that -- the cells it counts wear spellings the
    description never names and publishes no total for -- so that
    reading is asked at the settings floor, and `taxonomy._missing_maps`
    and the loader's V5 both pass it.

    Guarantees: reads only its arguments; returns an int. Determinism:
    a function of the arguments; the keys are read in sorted order.
    Raises nothing. No I/O of any kind.
    """
    for key in sorted(counts):
        # A count of nought names nobody, and it is no reading to refuse.
        if counts[key] >= 1 and not census_nameable([counts[key]], [], floor):
            return -2
    place = 0
    for total, covered in totals:
        rest = total - covered
        if (
            covered >= 1
            and rest >= 1
            and not census_nameable([], [rest], floor)
        ):
            return place
        place = place + 1
    return -1


# The characters a form key of a cell read as a number can hold: figures,
# the point and the comma, a sign, accounting brackets, and the one
# letter an exponent is written with, in either case (plan P4-D175).
_NUMBER_FORM_MARKS = SHAPE_DIGIT + SHAPE_LETTER + SHAPE_LOWER + ".,+-()"


def form_never_a_number(key: str) -> bool:
    """Whether no cell written in this form can be read as a number.

    THE THIRD TOTAL A READER HOLDS BESIDE THE FORM CENSUS (plan P4-D175,
    closing the final skeptic's BLOCKER). Every role that carries
    `shape_forms` publishes `n_not_numeric`, and a named form no number
    can wear counts cells inside that total, so a census naming 399
    `&&&-%%%` codes beside `n_not_numeric` 400 said that exactly one cell
    of the column was text of some other shape -- measured on 400
    five-figure numbers, 399 codes and one `hello` at a floor of eleven.
    The answer is read off the KEY alone, so the producer and the loader
    ask one question and a reader can ask it too: a number as
    `parse_number` reads it is written in figures, points and commas, a
    sign, accounting brackets and at most one exponent letter, which
    stands after a figure or a point and before a figure or a sign. So a
    key with no figure, any other mark, a second letter, or a letter
    anywhere else is never one. The answer errs toward False (a key that
    might be a number), which only ever leaves a total out of the
    question -- the direction that publishes less.

    Guarantees: accepts a form key; returns a bool. Determinism: a
    function of the key alone. Raises nothing. No I/O of any kind.
    """
    figures = 0
    letters = 0
    before = ""
    place = 0
    for character in key:
        if character not in _NUMBER_FORM_MARKS:
            return True
        if character == SHAPE_DIGIT:
            figures = figures + 1
        elif character == SHAPE_LETTER or character == SHAPE_LOWER:
            letters = letters + 1
            after = key[place + 1 : place + 2]
            if before not in (SHAPE_DIGIT, ".") or after not in (
                SHAPE_DIGIT, "+", "-"
            ):
                return True
        before = character
        place = place + 1
    return figures == 0 or letters > 1


# -- the LAYOUT of a record number (contract 7.12) --------------------
#
# WHY THIS IS NOT `shape_form` WITH A LARGER LIMIT, stated here because
# reusing that census was the obvious move and it is the wrong one.
# `SHAPE_FORM_LIMIT` is 24 and a UUID is 36, so every UUID has no form
# at all; but raising that limit would change the census the five label
# roles publish, on columns this landing does not touch, and the limit
# is not a performance bound -- it is C6-31a's judgement about where a
# fact stops being about a code and starts being about a sentence. That
# judgement is right for those roles and does not reach this one: a
# DECLARED record number is a record number because its owner said so,
# and no run of prose arrives here. So the identifier role gets a
# census of its own, and the form census is left exactly as it was.
#
# The limit is sixty-four because the widest identifier scheme in
# ordinary use is a braced GUID at thirty-eight characters.
LAYOUT_FORM_LIMIT = 64

# The one refusal this census raises on its own account: a convention
# no member of `LAYOUT_CONVENTIONS` names. It is a mistake in a CALLER
# and never in a document, so it is a plain ValueError and carries no
# spelling of anybody's table.
_NOT_A_LAYOUT_CONVENTION = (
    "a layout convention must be one of the three this module names: "
    "plain, lower-hexadecimal or upper-hexadecimal"
)

# THE MARKS A LAYOUT MAY CARRY: the thirteen C6-31a names, and the two
# BRACES. A braced GUID -- `{B8B6D8FE-...-E52DB2221A58}`, which is how
# SQL Server and many .NET exports write one -- wears braces, and a
# closed list that omitted them would give that column no layout at
# all while appearing to describe it.
LAYOUT_MARKS = "-./_:#*()[]+,{}"

# ...AND ONE SPACE BETWEEN TWO OTHER CHARACTERS (plan P4-D127). A
# national number is written in groups -- `657 240 7282` -- and a census
# that refused the space gave that column no layout at all: measured,
# 800 real cells matched `\d{3} \d{3} \d{4}` and 0 twin cells did, both
# files at exit 0. What the space was kept out for is prose, and a run
# of prose is kept out by the rest of this rule: a space may not open or
# close a cell and may not stand beside another space, so a sentence's
# own spacing is never what a layout reads. The column is declared a
# record number by its owner, and nothing here admits a tab, a line
# break or any other space character.
LAYOUT_SPACE = " "

# THE SIX PLACEHOLDERS, and each one says a KIND of character and never
# which character it was.
LAYOUT_DIGIT = "%"
LAYOUT_UPPER = "@"
LAYOUT_LOWER = "&"
LAYOUT_LOWER_HEX = "~"
LAYOUT_UPPER_HEX = "^"
# ...with ONE exception, which is stated rather than hidden: this mark
# says a figure of a cell written in FIGURES ALONE was a nought of its
# ZERO FILL -- a nought standing before every other figure and not the
# last character of the cell. It is the writer's field width, the
# `%08d` of NC-9, and it is the fact a reader loses when pandas or R
# reads `01586982` as 1586982 and silently drops the zero.
#
# EVERY NOUGHT OF THE FILL IS MARKED, NOT ONLY THE FIRST (plan
# P4-D126). Marking only the first said a cell was zero-filled and not
# how far: measured on 800 cells of `%08d` over 1 to 499,999, the real
# column opened `00` on 800 cells and the twin on 78, and
# `len(x.lstrip('0')) <= 5` counted 158 real cells against 1 -- so code
# stripping a fill and testing the number's width met a different column.
# The count of noughts in the fill is how many decades short of the
# width the number was, which is a coarse census of magnitudes under the
# floor and never a value. `0` alone and `000` are written by a fill of
# nought and one of two, so the LAST character is never marked: `0` is
# `%` and `000` is `!!%`.
#
# It can name no text anybody chose, because it stands only where the
# whole cell is figures, and it is never written in a hexadecimal
# column, where a figure is one character of sixteen and a leading
# nought is not a fill anybody wrote (plan P4-D125). A literal RUN of
# letters -- a hospital's own record prefix, or `ABC-` in front of a
# study number -- is a different thing, is a fragment of every value in
# its column, and is NOT built here: it waits for the owner's ruling on
# clause 3 (landing 2b.15).
LAYOUT_LEADING_ZERO = "!"

_LAYOUT_PLACEHOLDERS = "%@&~^!"

# The three conventions a COLUMN of record numbers is written in. The
# choice is the COLUMN's and never one cell's, and that is the whole of
# why this census works where a per-character rule does not: measured
# on eight hundred braced GUIDs, a hex mark decided character by
# character gives 800 different layouts and not one of them reaches two
# cells, because a figure is ambiguous between the two cases; and on a
# column of site codes `BOS-1234` it gives three, because `B` is a
# hexadecimal letter and `O` is not. Decided once for the column, the
# same two columns give exactly one layout each.
LAYOUT_PLAIN = "plain"
LAYOUT_HEX_LOWER = "lower-hexadecimal"
LAYOUT_HEX_UPPER = "upper-hexadecimal"
LAYOUT_CONVENTIONS = (LAYOUT_PLAIN, LAYOUT_HEX_LOWER, LAYOUT_HEX_UPPER)

_HEX_LOWER_LETTERS = "abcdef"
_HEX_UPPER_LETTERS = "ABCDEF"


def _could_carry_a_layout(text: str) -> bool:
    """Whether one cell is one this census describes at all.

    A cell is described where it is not empty, is no longer than
    `LAYOUT_FORM_LIMIT`, holds at least one figure or letter, and holds
    nothing but figures, ASCII letters, `LAYOUT_MARKS` and single
    spaces, none of which opens or closes the cell (plan P4-D127).

    THE TWO EDGES ARE EACH A PROPERTY AND NOT A PREFERENCE. A cell
    carrying a PLACEHOLDER is refused, and a cell of marks ALONE is
    refused: between them they are what makes "no cell that has a
    layout can be spelled the same as any layout" true. Without the
    second, a cell spelled `----` would have the layout `----` and be
    its own key again, which is the collision `SHAPE_DIGIT` and
    `SHAPE_LETTER` were chosen to rule out for the form census.
    """
    if not text or len(text) > LAYOUT_FORM_LIMIT:
        return False
    content = 0
    before = ""
    for character in text:
        if character in _LAYOUT_PLACEHOLDERS:
            return False
        if _is_a_digit(character) or _is_a_letter(character):
            content = content + 1
            before = character
            continue
        if character in LAYOUT_MARKS:
            before = character
            continue
        if character == LAYOUT_SPACE and before not in ("", LAYOUT_SPACE):
            before = character
            continue
        return False
    return content >= 1 and before != LAYOUT_SPACE


def layout_convention(values: "list[str]") -> str:
    """Which alphabet convention a whole column of record numbers uses.

    HEXADECIMAL exactly where every letter of every described cell is
    one of `abcdef` in EITHER case and at least one letter appears
    anywhere. The case the column is written in is the case MOST of
    those letters wear -- lower where the two are as many -- and a cell
    written in the other case wears the same layout (plan P4-D125).
    Everything else is `LAYOUT_PLAIN`, where a letter is marked by its
    CASE instead.

    WHY THE CASE IS NOT ALL OR NOTHING ANY MORE. It was, and one
    upper-case UUID among 799 lower-case ones turned the whole column
    PLAIN: every UUID then wore its own mask of figures and letters, 800
    layouts of one cell each, and at a floor of eleven the census was
    nothing but its pool and the twin wrote `A----...J` on every row.
    A letter's case is not what makes a character hexadecimal, so it
    does not decide the convention; it decides only which case the
    column's marks say, and a cell in the minority case -- one cell, or
    too few to name -- is never counted apart, so nothing about it is
    published at all.

    The letter test itself stays all-or-nothing. A column one of whose
    letters is not a hexadecimal one is not a hexadecimal column, so a
    site code `BOS-1234` keeps `@@@-%%%%` and does not shatter into one
    layout per site.

    AND A LETTER THAT NEVER TRADES PLACES WITH A FIGURE IS A LETTER
    (plan P4-D154). Letters inside `a` to `f` do not make a column
    hexadecimal on their own: `A1000000`, `B1000001` ... `F1000799` hold
    no other letter, and read as hexadecimal the column published
    `^^^^^^^^` and its twin wrote 786 of 800 cells with a figure where
    every real cell has its letter -- `[A-Z][0-9]{7}` matched 800 real
    cells and 14 twin cells, and both files passed. What a hexadecimal
    encoding shows that a letter-then-figures scheme does not is a
    POSITION holding a letter in one cell and a figure in another, so
    the column is hexadecimal only where, among its described cells of
    one length, some position holds both.

    Guarantees: accepts a list of strings; reads only them; returns one
    member of `LAYOUT_CONVENTIONS`. Determinism: the answer depends
    only on the values. Raises TypeError if handed anything that is not
    a list of string instances. No I/O of any kind.
    """
    if not isinstance(values, list):
        raise TypeError(_NOT_TEXT)
    lower = 0
    upper = 0
    # What each (length, position) has held: 1 a figure, 2 a letter.
    held: "dict[tuple[int, int], int]" = {}
    traded = False
    for value in values:
        if not isinstance(value, str):
            raise TypeError(_NOT_TEXT)
        if not _could_carry_a_layout(value):
            continue
        place = 0
        for character in value:
            place = place + 1
            kind = 0
            if _is_a_digit(character):
                kind = 1
            if _is_a_letter(character):
                kind = 2
                if character in _HEX_LOWER_LETTERS:
                    lower = lower + 1
                elif character in _HEX_UPPER_LETTERS:
                    upper = upper + 1
                else:
                    return LAYOUT_PLAIN
            if not kind:
                continue
            spot = (len(value), place)
            seen = held[spot] if spot in held else 0
            held[spot] = seen | kind
            if held[spot] == 3:
                traded = True
    if lower + upper < 1 or not traded:
        return LAYOUT_PLAIN
    if upper > lower:
        return LAYOUT_HEX_UPPER
    return LAYOUT_HEX_LOWER


def _layout_mark(character: str, convention: str, filling: bool) -> str:
    """The one mark that stands for one character of a cell.

    ``filling`` says the character is a nought of the cell's zero fill,
    which `layout_form` settles for the whole cell.
    """
    if _is_a_digit(character):
        if filling:
            return LAYOUT_LEADING_ZERO
        if convention == LAYOUT_HEX_LOWER:
            return LAYOUT_LOWER_HEX
        if convention == LAYOUT_HEX_UPPER:
            return LAYOUT_UPPER_HEX
        return LAYOUT_DIGIT
    if _is_a_letter(character):
        if convention == LAYOUT_HEX_LOWER:
            return LAYOUT_LOWER_HEX
        if convention == LAYOUT_HEX_UPPER:
            return LAYOUT_UPPER_HEX
        if "a" <= character <= "z":
            return LAYOUT_LOWER
        return LAYOUT_UPPER
    return character


def layout_form(text: str, convention: str) -> str:
    """The LAYOUT of one record number: its kinds, position by position.

    Every character becomes one mark saying what KIND of character stood
    there -- a figure, an upper-case letter, a lower-case letter, a
    hexadecimal character -- and every mark of `LAYOUT_MARKS`, and every
    single interior space, stands as itself. A UUID
    `a46d6753-ec14-8cb4-8e73-ca47ea90a8f0` in a lower-hexadecimal column
    has the layout `~~~~~~~~-~~~~-~~~~-~~~~-~~~~~~~~~~~~`; a site code
    `NYC-7480` has `@@@-%%%%`; a record number `REC4972605` has
    `@@@%%%%%%%`; a national number `657 240 7282` has `%%% %%% %%%%`;
    and `00282669`, being figures alone with a fill of two noughts, has
    `!!%%%%%%`.

    ONE MARK PER CHARACTER, WHICH IS WHY THE LENGTH RIDES IN THE KEY.
    A layout is exactly as long as the cell it came from, so the census
    of layouts IS the census of lengths, and the length mix NC-9 found
    collapsing -- `{10: 573, 7: 227}` written back as `{7: 799, 10: 1}`
    -- is carried by the same key that carries the shape. Nothing
    separate has to be published for it, and nothing separate can drift
    out of step with it.

    THE ZERO FILL is every nought before the first other figure of a
    cell written in figures alone, the last character excepted, and is
    marked only in a PLAIN column (see `LAYOUT_LEADING_ZERO`).

    A CELL `_could_carry_a_layout` REFUSES HAS NO LAYOUT AT ALL and
    answers the empty string, exactly as a formless cell does in the
    form census, and it is counted nowhere rather than pooled.

    Guarantees: accepts any string; returns a layout built only from
    the six placeholders, `LAYOUT_MARKS` and single interior spaces, or
    "" for a cell this census does not describe. Determinism: the
    answer depends only on the text and the convention. Raises
    TypeError if handed anything that is not a string instance, and
    ValueError for a convention this module does not name. Boundary: no
    figure and no letter of the cell survives into the answer -- only
    what KIND stood at each position, and where the marks between them
    fell. No I/O of any kind.
    """
    if not isinstance(text, str) or not isinstance(convention, str):
        raise TypeError(_NOT_TEXT)
    if convention not in LAYOUT_CONVENTIONS:
        raise ValueError(_NOT_A_LAYOUT_CONVENTION)
    if not _could_carry_a_layout(text):
        return ""
    fill = 0
    if convention == LAYOUT_PLAIN and _all_ascii_digits(text):
        while fill < len(text) - 1 and text[fill] == "0":
            fill = fill + 1
    built = ""
    place = 0
    for character in text:
        built = built + _layout_mark(character, convention, place < fill)
        place = place + 1
    return built


def is_a_layout_form(name: str) -> bool:
    """Whether one census key is a layout: THE one definition of it.

    The producer builds a layout, the loader admits a key and the
    publication guard refuses one, and the form census learned at cost
    what happens when those are three readings of one rule rather than
    three callers of one predicate (review round 2 finding 2). There is
    one definition here and the others call it.

    A layout is one to `LAYOUT_FORM_LIMIT` characters, every one of them
    a placeholder, a mark from the closed list or a single space that
    neither opens nor closes the key, carrying AT LEAST ONE placeholder.
    The last clause is what keeps a key of marks alone out, and with it
    the property that no cell wearing a layout is spelled like any
    layout. AND A ZERO FILL IS A KEY OF FIGURES ALONE: a key holding `!`
    is a run of `!` followed by at least one `%` and nothing else, which
    is the only thing `layout_form` ever writes it as (plan P4-D126).

    THERE IS NO TWO-KINDS RULE HERE, and that is a difference from the
    form census rather than an oversight. `@@@@@` is refused there
    because `length` and the two alphabet counts already say five
    letters. On this role they do not: `min_length` and `max_length`
    give only the two ends, so `%%%%%%%` and `%%%%%%%%%%` on one column
    say how many cells are seven characters and how many are ten --
    the very fact NC-9 found lost -- and `!%%%%%%%` says the zero fill
    besides. A key of one kind carries information here.

    Guarantees: accepts any string; answers only from the characters.
    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    if not name or len(name) > LAYOUT_FORM_LIMIT:
        return False
    placeholders = 0
    before = ""
    for character in name:
        if character in _LAYOUT_PLACEHOLDERS:
            placeholders = placeholders + 1
            before = character
            continue
        if character in LAYOUT_MARKS:
            before = character
            continue
        if character == LAYOUT_SPACE and before not in ("", LAYOUT_SPACE):
            before = character
            continue
        return False
    if placeholders < 1 or before == LAYOUT_SPACE:
        return False
    if LAYOUT_LEADING_ZERO not in name:
        return True
    return _is_a_fill_key(name)


def _is_a_fill_key(name: str) -> bool:
    """Whether a key holding `!` is a run of `!` then at least one `%`."""
    place = 0
    while place < len(name) and name[place] == LAYOUT_LEADING_ZERO:
        place = place + 1
    if place < 1 or place >= len(name):
        return False
    while place < len(name):
        if name[place] != LAYOUT_DIGIT:
            return False
        place = place + 1
    return True


def layout_fill(name: str) -> int:
    """How many noughts of zero fill one layout says, 0 for none.

    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    fill = 0
    while fill < len(name) and name[fill] == LAYOUT_LEADING_ZERO:
        fill = fill + 1
    return fill


def layout_shallower(name: str) -> str:
    """The layout one nought SHALLOWER than a zero-filled one, or "".

    A key of two or more fill noughts gives up its last `!` for a `%`:
    `!!!%%%%%` gives `!!%%%%%%`. It is the ONE step the census takes
    when a fill depth is too rare to name (contract C6-130, plan
    P4-D126): the rare depth's cells are counted under the next
    shallower depth, which is a true statement about them -- a cell
    filled with three noughts was filled with at least two -- and the
    step stops at one nought, below which a cell is not zero-filled at
    all and nothing shallower is true of it. "" for any key with fewer
    than two fill noughts.

    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    depth = layout_fill(name)
    if depth < 2:
        return ""
    return name[: depth - 1] + LAYOUT_DIGIT + name[depth:]


def layout_room(name: str) -> int:
    """How many different cells could have worn this layout.

    Each placeholder stands for its own alphabet -- ten figures,
    twenty-six letters of one case, sixteen hexadecimal characters --
    and `LAYOUT_LEADING_ZERO` stands for exactly one character, the
    nought, which is what it says. The marks and the space stand for
    themselves. So a layout is a COUNT of the cells it could have come
    from, and that count is what tells a generator whether it can spell
    as many different values as the layout is asked for.

    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    room = 1
    for character in name:
        if character == LAYOUT_DIGIT:
            room = room * 10
        elif character == LAYOUT_UPPER or character == LAYOUT_LOWER:
            room = room * 26
        elif character == LAYOUT_LOWER_HEX or character == LAYOUT_UPPER_HEX:
            room = room * 16
    return room


def layout_supply(name: str) -> int:
    """How many different cells could have been COUNTED under this layout.

    THE CAPACITY THE DISCLOSURE RULE ASKS, which is not the enumeration
    capacity `layout_room` gives (Codex blocker 1 of the extra round,
    2026-09-18; plan P4-D260). `layout_room` counts the spellings a
    generator can build from the marks; this counts the cells
    `layout_form` would put UNDER the key, and on a key of figures alone
    the two differ, because the zero fill takes the leading noughts away
    into a key of their own.

    A key of figures alone -- `!` and `%` and nothing else -- is written
    only under `LAYOUT_PLAIN`, where `layout_form` marks every nought
    before the first other figure, the last character excepted. So the
    first `%` of such a key stands for a figure that is NOT a nought
    whenever another `%` follows it: `%%%` is worn by `100` to `999` and
    never by `012`, which wears `!%%`. Its supply is 900 and not a
    thousand, and `!%%` is 90 and not a hundred. Where the key holds one
    `%` alone that figure is the last character, which the fill rule
    excepts, so every figure stands and the supply is ten.

    MEASURED, AND IT IS WHY THIS EXISTS: 900 record numbers `100` to
    `999` at a floor of eleven published `layout_forms={"%%%": 900}`
    beside `n_distinct` 900, because 1,000 clears 900 plus the floor.
    The census named every one of the 900 cells that wear the layout, so
    the layout's own supply WAS the source's value set, the twin
    generated all 900, and both files validated at exit 0. With the
    supply counted here the layout is refused and its cells are pooled.

    Every other key answers exactly `layout_room`: a mark or a space
    anywhere stops `_all_ascii_digits`, so no fill is marked, and a
    letter or a hexadecimal place is never a nought of a fill.

    Guarantees: accepts a string; returns a whole number of one or more.
    Determinism: a function of the argument. Raises TypeError if handed
    anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    room = layout_room(name)
    figures = 0
    for character in name:
        if character == LAYOUT_DIGIT:
            figures = figures + 1
        elif character != LAYOUT_LEADING_ZERO:
            return room
    if figures < 2:
        return room
    return room - room // 10


# -- the literal PREFIX of a record number (owner ruling 2026-09-17) ---
#
# THE ONE FRAGMENT A LAYOUT CENSUS MAY CARRY, AND ONLY BY RULING. A
# layout replaces every letter of a cell with a mark saying its case,
# so `P00123`, `REC1234567` and `ABC-1234` came back as `X17879`,
# `FPQ7317879` and `JOD-7879`: measured at 800 rows (landing 2b.15),
# `^P\d{5}$` matched 800 real cells and 30 twin cells, `^REC\d{7}$` 800
# and 0, `^ABC-\d{4}$` 800 and 0, and both files validated at exit 0.
# The owner's ruling of 2026-09-17, item 1, settles clause 3 for this
# case: where every present cell of a declared record number opens with
# the SAME literal text and the column clears the smallest group size,
# that text is published and the twin writes it. It amends contract
# invariants I3 and F3 for this case and no other.

# The key of `layout_prefixes` that says EVERY present cell of the
# column opens with the prefix. It holds lower-case letters, which no
# layout ever holds, so it can never be mistaken for a layout key.
PREFIX_OF_THE_COLUMN = "(column)"


def literal_prefix(values: "list[str]", convention: str) -> str:
    """The literal text every one of ``values`` opens with, or "".

    THE ONE DEFINITION (owner ruling 2026-09-17, item 1; contract 7.12a).
    The producer asks it of a column's present cells and of the cells of
    each named layout, and nothing else restates it. The prefix is the
    longest opening every value shares, cut back by four rules, each of
    which keeps what is published a label the column's writer put in
    front of the number rather than part of anybody's number:

    1. NO FIGURE. It stops before the first figure, so `P00123` beside
       `P00456` publishes `P` and not `P00`: the noughts are part of
       the number, and saying every number is below a thousand is a fact
       about values.
    2. A FIGURE OR A LETTER OF EVERY VALUE STANDS AFTER IT, so no value
       is ever published whole -- not even as a prefix and the marks its
       layout already names: `no#` in front of every `no##` would be.
    3. NO HALF A RUN OF LETTERS. Where it ends in a letter and some value
       goes on with another letter, it is cut back to the last character
       that is not a letter: `REC` beside `REX` publishes nothing, and
       `ST-A123` beside `ST-B456` publishes `ST-`.
    4. ONLY CHARACTERS A LAYOUT CARRIES AS THEY ARE: ASCII letters, the
       marks of `LAYOUT_MARKS`, and a single space that does not open the
       prefix or stand beside another. An opening holding anything else
       publishes nothing, and so does one holding no letter at all,
       because marks alone are already in the layout.

    A HEXADECIMAL COLUMN IS READ UNDER RULE 3 AND NOT BARRED (plan
    P4-D233, closing the limit P4-D202 put to the owner). Every letter
    of such a column is one of `abcdef` in either case, so every letter
    is a figure of base sixteen and rule 3 -- no half a run of figures
    -- cuts the opening back to the last character that is NOT one. A
    prefix there therefore always ends in a mark: 800 cells of `DE-`
    and six hexadecimal figures publish `DE-`, where `ab12` beside
    `ab34` still publishes nothing, because `ab` is half a number.
    Nothing else about the rules changes, and `is_a_literal_prefix`
    admits the same text whatever the column.

    Guarantees: accepts a list of strings and a member of
    `LAYOUT_CONVENTIONS`; returns "" or a string satisfying
    `is_a_literal_prefix`. Determinism: a function of the arguments.
    Raises TypeError for anything that is not a list of strings. No I/O
    of any kind.
    """
    if not isinstance(values, list):
        raise TypeError(_NOT_TEXT)
    if convention not in LAYOUT_CONVENTIONS or not values:
        return ""
    common = ""
    shortest = -1
    first = True
    for value in values:
        if not isinstance(value, str):
            raise TypeError(_NOT_TEXT)
        # Where this value's last figure or letter stands: the prefix
        # must end before it (rule 2).
        last = -1
        place = 0
        for character in value:
            if _is_a_digit(character) or _is_a_letter(character):
                last = place
            place = place + 1
        if first:
            common = value
            shortest = last
            first = False
            continue
        shortest = min(shortest, last)
        place = 0
        while (
            place < len(common)
            and place < len(value)
            and common[place] == value[place]
        ):
            place = place + 1
        common = common[:place]
    place = 0
    while place < len(common) and not _is_a_digit(common[place]):
        place = place + 1
    common = common[: min(place, max(shortest, 0))]
    while common and _is_a_letter(common[len(common) - 1]):
        goes_on = False
        for value in values:
            if _is_a_letter(value[len(common)]):
                goes_on = True
        if not goes_on:
            break
        common = common[: len(common) - 1]
    # RULE 3 IN A HEXADECIMAL COLUMN. There a letter is a figure of base
    # sixteen, so a prefix ending in one ends inside a number and is cut
    # back to the last character that is not a figure of the base.
    if convention != LAYOUT_PLAIN:
        while common and _is_a_hex_figure(common[len(common) - 1]):
            common = common[: len(common) - 1]
    if not is_a_literal_prefix(common):
        return ""
    return common


def _is_a_hex_figure(character: str) -> bool:
    """Whether one character is a figure of base sixteen, in either case.

    A hexadecimal column's letters are all inside `abcdef`
    (`layout_convention`), so this asks the same question of a letter
    whichever case the column's marks say.
    """
    return (
        _is_a_digit(character)
        or character in _HEX_LOWER_LETTERS
        or character in _HEX_UPPER_LETTERS
    )


def is_a_literal_prefix(text: str) -> bool:
    """Whether one published prefix is text `literal_prefix` can write.

    One to `LAYOUT_FORM_LIMIT` less one characters, every one an ASCII
    letter, a mark of `LAYOUT_MARKS` or a single space that does not open
    it and does not follow another space, with at least one letter and no
    figure. The producer, the loader and the publication guard ask this
    one predicate. A key carrying a placeholder is refused here, so no
    prefix can be read as a layout.

    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text or len(text) >= LAYOUT_FORM_LIMIT:
        return False
    letters = 0
    before = ""
    for character in text:
        if _is_a_letter(character):
            letters = letters + 1
        elif character == LAYOUT_SPACE:
            if before in ("", LAYOUT_SPACE):
                return False
        elif character not in LAYOUT_MARKS:
            return False
        before = character
    return letters >= 1


def prefix_layout(text: str, convention: str) -> str:
    """The layout a column gives a literal prefix, mark by mark.

    Every letter takes the mark its own column's convention gives it --
    `LAYOUT_UPPER` or `LAYOUT_LOWER` by its case in a plain column, the
    column's hexadecimal mark in a hexadecimal one (plan P4-D233) --
    and every other character stands as itself, so a prefix belongs to
    a layout exactly where the layout opens with this. It is
    `layout_form`'s own reader, asked character by character, so the
    two can never drift: `REC` under a plain column is `@@@` and `DE-`
    under a lower-hexadecimal one is `~~-`.

    Raises TypeError if handed anything that is not a string instance,
    and ValueError for a convention this module does not name. No I/O
    of any kind.
    """
    if not isinstance(text, str) or not isinstance(convention, str):
        raise TypeError(_NOT_TEXT)
    if convention not in LAYOUT_CONVENTIONS:
        raise ValueError(_NOT_A_LAYOUT_CONVENTION)
    built = ""
    for character in text:
        built = built + _layout_mark(character, convention, False)
    return built


def prefix_nameable(carrying: int, present: int, floor: int) -> bool:
    """Whether a prefix ``carrying`` of ``present`` cells open with may print.

    THE DISCLOSURE RULE, asked once and not restated: `census_nameable`
    with the cells opening with the prefix as the count and the column's
    present cells as the population a reader subtracts it from. So the
    cells carrying it reach the line, and the cells NOT carrying it are
    nought -- the whole column -- or reach the line too. A prefix that
    every cell of one layout wears, and all but one cell of the column,
    would otherwise say that one row of the table is written otherwise.

    Guarantees: a fixed function of the three. Raises nothing. No I/O.
    """
    return census_nameable([carrying], [present], floor)


def absorbed_total(count: int, population: int, floor: int) -> int:
    """One scalar count of a published population, as the disclosure rule allows.

    THE SHARED RULE ASKED OF A SCALAR AND NOT OF A CENSUS (plan P4-D277).
    A block that publishes no value of the table still publishes counts
    that SPLIT its cells: how many read as a number, how many are figures
    alone, how many lie inside the code alphabet. Each is a census of two
    groups written as one number, and `census_nameable` governs it as it
    governs a census of ten: the count names a group, and so does what it
    leaves of the population.

    **Measured** at a floor of eleven, on 999 declared record numbers of
    `REC` and seven figures beside one `42`: the block published
    `n_numeric 1`, `n_all_digits 1` and `n_not_numeric 999` against
    `n_present 1000`, each of them naming that one record; with `X Y` in
    its place, `n_code_alphabet 999` beside `n_present 1000` named the
    one identifier outside the alphabet. Layouts were withheld for
    exactly this reason and these counts were not.

    WHERE THE PAIR CANNOT SPEAK, THE SMALLER SIDE IS COUNTED INTO THE
    LARGER, which is ruling 6 of 2026-09-17 again: the description is the
    description of the table with those cells written the way most of its
    cells were, and describing the table again says the same thing, so
    the table passes its own description. A population too small for
    either side to reach the line is counted wholly to the larger side,
    ties to the population.

    Guarantees: accepts the count, the population it is taken from and
    the settings floor; returns the count, nought, or the population.
    Determinism: a fixed function of the three. Raises nothing. No I/O.
    """
    if census_nameable([count], [population], floor):
        return count
    if count * 2 >= population:
        return population
    return 0


def counts_absorbed_to(published: int, population: int, floor: int) -> "list[int]":
    """Every measured count `absorbed_total` publishes as ``published``.

    A PUBLISHED ABSORBED COUNT NAMES A SET OF TABLES, NOT ONE COUNT (plan
    P4-D298). Where the pair cannot speak, `absorbed_total` publishes
    nought or the whole population, and a column whose measured count is
    one below either end publishes the same number as a column holding
    it exactly. A twin meets the published count wherever describing it
    again publishes that number -- which is how the validator reads it,
    since it describes the twin with this module's own producer -- and
    the table itself does so only in that sense: 999 figures beside one
    `ab` publish `n_all_digits 1000`, and the table's own count is 999.

    So this is the reading the generator packs against. **Measured** on
    the free-text battery of review item P2-C4-F2 at e53d5f4: 158 of
    3,186 producer columns published an absorbed alphabet count that no
    assignment of whole groups meets EXACTLY beside the four class
    counts, the length ends and the word ends the same block publishes --
    a column of eleven figures and one `ab` publishes `n_all_digits 12`
    beside `n_numeric 11` -- and every one of them fell to the fallback
    packing, although its own values meet the published description.

    Guarantees: accepts the published count, the population it was taken
    from and the settings floor; returns every count from nought to the
    population that `absorbed_total` publishes as ``published``, the
    published count first where it is one of them, then in ascending
    distance from it, ties to the smaller. Empty where no count is. A
    count the rule can move lies within the census line of an end, so at
    most `2 * census_floor(floor) + 1` counts are asked. Determinism: a
    fixed function of the three. Raises nothing. No I/O of any kind.
    """
    line = census_floor(floor)
    offered: dict[int, int] = {}
    if 0 <= published <= population:
        offered[published] = 1
    for count in range(0, min(line, population + 1)):
        offered[count] = 1
    for count in range(max(population - line + 1, 0), population + 1):
        offered[count] = 1
    ranked = sorted(
        [(abs(count - published), count) for count in sorted(offered)]
    )
    found: list[int] = []
    for pair in ranked:
        if absorbed_total(pair[1], population, floor) == published:
            found += [pair[1]]
    return found


def count_as_published(
    count: int, population: int, published: int, floor: int
) -> int:
    """A recounted count as the description it is held to would print it.

    THE ONE READING A RECOUNT OF AN ABSORBED COUNT MAKES (plan P4-D298).
    A count equal to the published one is met as it stands; any other is
    read through `absorbed_total`, which is what describing the cells
    again would publish. The first clause is what keeps a description
    written before plan P4-D277 -- or by hand -- held to the count it
    prints: its twin holds that count exactly and is never named for it.

    Guarantees: accepts the recounted count, the population it was taken
    from, the published count and the settings floor; returns the count
    itself or its absorbed reading. Determinism: a fixed function of the
    four. Raises nothing. No I/O of any kind.
    """
    if count == published:
        return count
    return absorbed_total(count, population, floor)


def parts_as_published(
    parts: "list[int]", published: "list[int]", floor: int
) -> "list[int]":
    """A recounted partition as the description it is held to would print it.

    `count_as_published` for the four-way partition of invariant X2 (plan
    P4-D298): a partition equal to the published one stands, and any
    other is read through `absorbed_parts`. Guarantees: returns four
    counts. Determinism: a fixed function of the three. Raises nothing.
    No I/O of any kind.
    """
    if parts == published:
        return [part for part in parts]
    return absorbed_parts(parts, floor)


def absorbed_parts(parts: "list[int]", floor: int) -> "list[int]":
    """A declared record number's four-way partition, as X2 publishes it.

    THE RULE OF CONTRACT INVARIANT X2 (plan P4-D277), stated once so the
    producer that publishes the four counts and the generator that owes
    them read one partition the same way (plan P4-D298). ``parts`` is
    what the cells read as -- numbers, numerals out of range, numerals
    contradicting themselves, text -- in the contract's own order. A part
    below `census_floor(floor)` is counted into the LARGEST part, ties to
    the first of the four, which is ruling 6 of 2026-09-17 again; the
    sum is unchanged.

    Guarantees: accepts the four measured counts and the settings floor;
    returns the four published counts, summing to the same total.
    Determinism: a fixed function of the two. Raises nothing. No I/O.
    """
    line = census_floor(floor)
    largest = 0
    place = 0
    for part in parts:
        if part > parts[largest]:
            largest = place
        place = place + 1
    taken = 0
    kept = [0 for _each in parts]
    place = 0
    for part in parts:
        if place != largest and 0 < part < line:
            taken = taken + part
        else:
            kept[place] = part
        place = place + 1
    kept[largest] = kept[largest] + taken
    return kept


def parts_absorbed_to(
    published: "list[int]", floor: int
) -> "list[list[int]]":
    """Every measured partition `absorbed_parts` publishes as ``published``.

    The partition's reading of `counts_absorbed_to` (plan P4-D298): a
    declared record number publishing `n_numeric 25` and nothing else
    describes a column of 25 numbers, and equally one of 23 numbers, one
    cell of text and one numeral out of range, since both are published
    alike. The published largest part is the measured largest part --
    the rule only adds to it -- so every other part published as nought
    may have measured anything below the census line, and the largest
    gives up what they take.

    Guarantees: accepts the four published counts and the settings
    floor; returns every partition of the same total that
    `absorbed_parts` publishes as ``published``, the published one first
    where it is one of them, then by the number of cells moved, ties in
    ascending order of the four counts. At most `census_floor(floor)`
    cubed partitions are asked. Determinism: a fixed function of the
    two. Raises nothing. No I/O of any kind.
    """
    line = census_floor(floor)
    largest = 0
    place = 0
    for part in published:
        if part > published[largest]:
            largest = place
        place = place + 1
    free: list[int] = []
    place = 0
    for part in published:
        if place != largest and part == 0:
            free += [place]
        place = place + 1
    ranked: list[tuple[int, tuple[int, ...]]] = []
    wheel = [0 for _each in free]
    while True:
        moved = 0
        for value in wheel:
            moved = moved + value
        measured = [part for part in published]
        for step in range(len(free)):
            measured[free[step]] = wheel[step]
        measured[largest] = published[largest] - moved
        if measured[largest] >= 0 and absorbed_parts(measured, floor) == (
            published
        ):
            ranked += [(moved, tuple(measured))]
        turned = len(free) - 1
        while turned >= 0 and wheel[turned] == line - 1:
            wheel[turned] = 0
            turned = turned - 1
        if turned < 0:
            break
        wheel[turned] = wheel[turned] + 1
    found: list[list[int]] = []
    for pair in sorted(ranked):
        found += [[part for part in pair[1]]]
    return found


def prefix_room(layout: str, prefix: str, convention: str) -> int:
    """How many different cells a layout still spells once a prefix is fixed.

    THE ROOM RULE, ASKED OF THE PREFIX (plan P4-D270). `layout_room`
    counts the cells a layout could have come from while every one of
    its positions is free. A published prefix fixes some of them: a
    reader who holds `@@@%%%` beside the prefix `REC` does not hold
    17,576,000 possible cells, they hold a THOUSAND, because the three
    letters are spelt out for them. So the count that has to clear the
    census's own room is this one, and it is the only count that ever
    was -- the prefix simply did not exist when `layout_census` wrote
    the rule.

    The prefix is read into its own layout by `prefix_layout`, which is
    `layout_form`'s reader, so a prefix belongs to a layout exactly
    where the layout opens with it. Where it does not, the layout's room
    is untouched and this answers `layout_room`.

    Raises TypeError if handed anything that is not a string instance,
    and ValueError for a convention this module does not name. No I/O of
    any kind.
    """
    opening = prefix_layout(prefix, convention)
    if layout[: len(opening)] != opening:
        return layout_room(layout)
    return layout_room(layout[len(opening):])


def prefix_leaves_room(
    layout: str, prefix: str, convention: str, distinct: int, floor: int
) -> bool:
    """Whether a prefix may stand beside a layout without spelling the column.

    THE OWNER'S RULING OF 2026-09-17, ITEM 1, HELD TO THE GUARD THAT WAS
    ALREADY THERE (plan P4-D270, contract invariant LP3). `layout_census`
    names a layout only where it could have come from at least
    `n_distinct + floor` different cells, so that the named shape never
    spells out the column's own value set. Publishing the prefix is the
    ruling's own amendment of invariants I3 and F3, and it does not
    amend that guard: it feeds it.

    MEASURED, on the shape the final review of 2026-09-18 built. 1,000
    record numbers `REC000` to `REC999` at a floor of eleven, declared,
    beside a constant second column, published `layout_forms
    {"@@@%%%": 1000}`, `layout_prefixes {"(column)": "REC"}` and
    `n_distinct 1000`. Those three facts have exactly one solution, and
    at seed 4 the twin held all 1,000 of the table's own record numbers,
    every one of its rows a row of the table, with both files at exit 0.
    `layout_room("@@@%%%")` is 17,576,000 and clears 1,011 easily;
    `prefix_room` is 1,000 and does not.

    WHAT GIVES WAY IS THE PREFIX AND NOT THE CENSUS, because the census
    is what the twin's shape is built from and the prefix may only stand
    beside a named layout at all (invariant LP1): taking the census back
    would leave the prefix nothing to stand on, and taking the prefix
    back leaves a column whose layout still clears the room rule on its
    own. So the coarser fact is published and the sharper one is not.
    The ruling is unmoved everywhere it can be kept -- `REC` and seven
    figures over 800 rows leaves 10,000,000 cells for 811 and is
    published exactly as before.

    Guarantees: accepts a layout, a prefix, the census's convention, the
    column's different values and the settings floor; returns a bool.
    Determinism: a fixed function of the five. Raises TypeError for a
    non-string, and ValueError for an unnamed convention. No I/O.
    """
    return prefix_room(layout, prefix, convention) >= distinct + floor


def pool_names_a_level(
    levels: int, rows: int, published_rows: int
) -> bool:
    """Whether the published pool FORCES a count of ONE.

    THE OWNER'S RULING OF 2026-09-17, ITEM 5 (plan P4-D231, contract
    invariant B4b): a label column's lone row that could be read by
    subtraction is counted as missing, so that no count of one can be
    derived. A label column publishes how many levels the floor held
    back and how many rows they cover TOGETHER, and no size of any one
    of them (P4-D201). Every held-back level covers at least one row, so
    where the rows come to fewer than TWICE the levels at least
    ``2 * levels - rows`` of them are provably single rows -- and where
    that holds the pair is a count of one whatever else the reader knows.
    ONE level over ONE row was the first case measured: 480 `F`, 519 `M`
    and one `U` at a floor of eleven said that one row holds a third
    value, and `n_present` less the published counts reads the one even
    with both keys left out (invariant B3). One row is one person.

    THE RULE IS THE WHOLE FORCED BAND AND NOT ITS SHARPEST POINT (plan
    P4-D239, the repair of the final review of 2026-09-18). `levels == 1
    and rows == 1` was built first and it left the ordinary shape open:
    a clinical `site` column of 2,000 rows at a floor of eleven with
    three one-patient sites published THREE levels over THREE rows, and
    the plain summary said in English that three values are each shared
    by fewer than eleven rows and cover three rows in total. Three
    levels over three rows can only be one and one and one, so a reader
    is told without arithmetic that three named sites hold one patient
    each, and the twin wrote three single-row labels. `rows < 2 * levels`
    is the condition the contract's own paragraph already computed two
    sentences above the rule, and it is the exact band in which a
    singleton is forced.

    Where this answers True the cells of every held-back level are
    counted as MISSING instead, so the description is that of the table
    with those cells blank and the pool is nought.

    TWO WIDER READINGS WERE BUILT AND MEASURED BEFORE THIS ONE, and each
    is recorded here because the next reader will reach for them (plan
    P4-D231 puts both to the owner).

    (a) *A pool of one LEVEL, whatever its size.* One level over seven
    rows publishes that level's own count by subtraction, and seven is
    below the floor, so it is a count the floor exists to refuse. It is
    strictly wider than the band this asks -- `rows < 2 * levels` closes
    one level over one row and leaves one level over seven standing. Its
    reach is wide because the shape is common: on the full suite it
    moved 53 witnesses, among them every column whose one rare value is
    counted out -- a `constant` column of four cells below the floor
    becomes an EMPTY column, and a column of 98 readings beside two
    `trace` cells becomes a column of numbers with two holes.

    (b) *A pool that does not reach `census_floor`.* That is the one
    disclosure rule asked of the subtraction, and it empties the
    held-back machinery P4-D201 built wherever the floor is high: on the
    full suite, 66 witnesses, three frozen cases unwritable, and the
    rare VALUES of every small column at a raised floor turned into
    holes. A pool of ten rows over four levels says nothing about any
    one of them.

    Neither is built. The ruling names a count of one, and the forced
    band is exactly where one is derivable; a pool that leaves every
    held-back level free to cover two rows or more derives none.

    AND THE POOL HAS TO BE AN EXCEPTION BESIDE THE COLUMN'S OWN LABELS,
    which is the second half of the rule and is measured, not argued.
    The band above is true of EVERY LONG TAIL: 780 record numbers each
    written once beside one value of twenty rows hold 780 levels over
    780 rows, and counting those cells as missing empties the column.
    Nothing is derived there that the block did not already say --
    `n_present` and `n_distinct_folded` beside each other say every
    value is unique -- and the ruling names a LABEL column's lone row,
    which is a row standing OUT from the labels a column is made of. So
    the pool must also be SMALLER THAN EVERYTHING THE COLUMN PUBLISHES:
    three one-patient sites beside 1,997 published rows are an
    exception, 780 unique codes beside one published value of 20 are the
    column. Measured: without this half, fifteen witnesses of the code
    and long-tail batteries turn red and their columns come back blank.

    THE EXCEPTION IS MEASURED AGAINST THE PUBLISHED ROWS AND NOT AGAINST
    THE SMALLEST PUBLISHED LEVEL (plan P4-D271, the repair of the extra
    review round of 2026-09-18). The smallest published level is a
    function of the FLOOR, not of the column: at a floor of eleven it
    can be eleven on a column of two thousand rows, and a pool of twelve
    then clears it and escapes a rule the pool is squarely inside.
    **Measured** at a floor of eleven: 1,977 `NORTH`, 11 `SOUTH` and
    twelve one-row sites published `suppressed_levels 12`,
    `suppressed_rows 12` and no missing cell at all -- twelve levels over
    twelve rows, which can only be twelve single rows -- and the twin
    wrote twelve single-row labels while both files validated at exit 0.

    THE LINE IS HALF OF WHAT THE COLUMN PUBLISHES, and that width was
    measured rather than chosen. A pool covering a third of the column
    or more IS the column's own shape: 100 codes written once beside two
    codes of a hundred rows each, at a floor of eleven, is a code
    register with a long tail, and counting its tail out left the whole
    column two values wide and its form census one key (`tests/
    test_final_review_labels.py`). A pool covering less than half of
    what the column publishes is an exception beside it: twelve rows
    against 1,988, or three one-patient sites against 1,997. And 780
    unique codes against one published value of twenty are the column at
    any width. Every reading this rule was pinned at is unmoved, because
    in each of them the pool stands on the same side of both counts.

    AND THE EXCEPTION MAY NOT RESCUE A POOL THAT IS ALL SINGLE ROWS
    (plan P4-D271, as amended by the repair pass of 2026-09-18). The
    exception above is a width, and a width lets the band's SHARPEST
    point through wherever the pool is wide enough: `suppressed_levels`
    equal to `suppressed_rows` says every held-back level covers exactly
    one row -- not "at least one of them is a single row" but a count of
    one for each of them, read off two published numbers by subtraction,
    which is squarely what ruling 5 names. **Measured** at a floor of
    eleven, on the commit this landing was cut from and on the landing
    itself: 100 `NORTH` and 100 `SOUTH` beside 120 site codes written
    once each published `suppressed_levels 120`, `suppressed_rows 120`
    and `n_missing 0`, and the twin wrote 120 labels each covering one
    row; 600 and 600 beside 700 such codes did the same at 700. Both
    cleared the width, because 240 is not below 200 and 1,400 is not
    below 1,200.

    So a PINNED pool is read by subtraction outright, wherever it is
    smaller than what the column publishes. That last clause is the
    second half of the rule kept whole: 780 unique codes over 780 rows
    beside one published value of twenty are pinned too, and they are
    still the column rather than an exception beside it, so they still
    stand -- as do 99 codes over 100 rows beside 200 published rows,
    which are not pinned at all. After the amendment the two shapes
    above publish no pool, count their 120 and their 700 rows as
    missing, and both files validate at exit 0. Every reading this rule
    was pinned at is unmoved, in the unit battery and in the round trips
    alike.

    Guarantees: accepts how many levels were held back, how many rows
    they cover, and how many rows the column's published levels cover
    between them (nought where it publishes none); returns True exactly
    where a level is published, a level is held back, and either the
    rows equal the levels held back while falling short of the published
    rows, or the rows come to fewer than twice the levels held back
    while twice the pool's rows come to fewer than the published rows.
    Determinism: a fixed function of the three. Raises nothing. No I/O
    of any kind.
    """
    if levels < 1 or published_rows < 1:
        return False
    if rows == levels and rows < published_rows:
        return True
    if rows * 2 >= published_rows:
        return False
    return rows < 2 * levels


# What one cell says about the comma inside it.
COMMA_NONE = "no-comma"
COMMA_GROUPED = "proves-a-thousands-separator"
COMMA_DECIMAL = "proves-a-decimal-comma"
COMMA_EITHER = "reads-either-way"


def _groups_by_threes(body: str, mark: str) -> bool:
    """Whether the fields ``mark`` separates read as thousands groups.

    The first field is one to three figures and every later one is
    exactly three, which is what tells `1.234.567,89` -- a million and
    a bit, written the German way -- from `1.2.3,4`, which is a version
    identifier and no number at all.
    """
    fields: "list[str]" = []
    current = ""
    for character in body:
        if character == mark:
            fields += [current]
            current = ""
            continue
        current = current + character
    fields += [current]
    head = fields[0]
    if not head or len(head) > 3 or not _all_ascii_digits(head):
        return False
    for field in fields[1:]:
        if len(field) != 3 or not _all_ascii_digits(field):
            return False
    return True


def groups_thousands(text: str) -> bool:
    """Whether this cell PROVES its comma separates thousands.

    The gate `group_separator` is published through, and it is
    deliberately narrow. A cell proves a thousands separator only where
    `comma_reading` says so: a point somewhere after the comma
    (`1,234.56`), or a second comma (`1,234,567`). A lone `1,795`
    settles nothing -- it reads either way -- and contributes no
    evidence at all, so a decimal-comma column is never mistaken for a
    grouped one and the ambiguity costs no new judgement here. That
    reasoning, and the four constants it turns on, are `comma_reading`'s
    and this only asks the question.

    Guarantees: accepts text; answers True only where the cell itself
    settles the reading as grouping. Determinism: the answer depends
    only on the text. Raises TypeError if handed anything that is not a
    string instance. Boundary: no figure of the cell travels out
    through it. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return comma_reading(text) == COMMA_GROUPED


def with_group_separator(figures: str, mark: str) -> str:
    """`figures` with `mark` between each group of three whole figures.

    THE WRITE RULE FOR A GROUPED COLUMN, and the reason the twin can
    hold one at all. What used to stand here was the ruling that a
    thousands separator can never be written because "the comma breaks
    the CSV row itself". That is FALSE and it is the whole reason the
    defect existed: `rendering.twin_csv` already quotes any cell
    holding a comma, so `"$2,198.92"` is written, quoted, and read back
    by this module's own reader unchanged.

    Only the whole part is grouped, and only from four figures up. A
    sign, a decimal point, anything after the point and any exponent
    are left exactly as they were: an exponent's mantissa never reaches
    four whole figures, and a padded field is a code whose width a
    separator would corrupt, so neither is ever handed here.

    Guarantees: accepts a written number and one separator character;
    returns the same number with the separator between each group of
    three whole figures, or the number unchanged where its whole part
    is shorter than four figures or where `mark` is empty. Determinism:
    a fixed function of the two. Raises TypeError if handed anything
    that is not a string instance. No I/O of any kind.
    """
    if not isinstance(figures, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(mark, str):
        raise TypeError(_NOT_TEXT)
    if mark == "":
        return figures
    sign = ""
    body = figures.strip()
    if body[:1] == "+" or body[:1] == "-":
        sign = body[:1]
        body = body[1:]
    point = body.find(".")
    whole = body if point < 0 else body[:point]
    rest = "" if point < 0 else body[point:]
    if len(whole) < 4 or not _all_ascii_digits(whole):
        return figures
    lead = len(whole) % 3
    if lead == 0:
        lead = 3
    grouped = whole[:lead]
    place = lead
    while place < len(whole):
        grouped = grouped + mark + whole[place : place + 3]
        place += 3
    return sign + grouped + rest


def comma_reading(text: str) -> str:
    """What one cell settles about the comma it carries, if anything.

    `1,795` is one thousand seven hundred and ninety-five where a comma
    groups thousands, and 1.795 where a comma is the decimal point --
    and most of the world writes the second. THAT ONE CELL SETTLES
    NOTHING. But many cells do, and an earlier revision of this package
    said flatly that none could, which was wrong in both directions:

    - A POINT AFTER THE COMMA settles it as a thousands separator, and
      so does a SECOND COMMA. `1,234.56` and `1,234,567` are not
      ambiguous at all, and a column of them was being told it might be
      a thousand times out when it was not.
    - A GROUP THAT IS NOT THREE FIGURES settles it as a decimal comma
      -- `12,5`, `1,23` -- and so does a FIRST GROUP OF MORE THAN THREE
      figures, because `1000,000` cannot be thousands-grouped at all.
      A point BEFORE a comma settles it the same way: `22.008,28` is
      grouped with points.

    So a three-decimal European column DOES carry evidence as soon as
    one of its values reaches a thousand, and a column that reaches
    none is the one that settles nothing. The difference is the whole
    of what NF44 has to say to a person.

    Guarantees: accepts text; answers one of the four constants above.
    Determinism: the answer depends only on the text. Raises TypeError
    if handed anything that is not a string instance. Boundary: no
    figure of the cell travels out through it. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = text.strip()
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        body = body[1 : len(body) - 1].strip()
    if body[:1] == "+" or body[:1] == "-":
        body = body[1:]
    # NOTHING BUT FIGURES, POINTS AND COMMAS MAY SPEAK HERE, and this
    # guard is the whole reason the second count is safe to publish. A
    # cell is evidence about how NUMBERS are written only if it is
    # trying to be a number: without this, `Hello.World,Foo` -- a point
    # before a comma -- was read as proof of a decimal comma, and a
    # column of names or addresses would have been told in capital
    # letters that this file writes the decimal point as a comma. A
    # false alarm in a loud sentence is worse than no sentence, which
    # is the same lesson the first read taught about `1,234.56`.
    # AN EXPONENT IS PART OF THE NUMBER AND NOT PART OF THE QUESTION.
    # `1,001e2` is a spelling the documented grammar admits, and
    # reading the exponent as ordinary characters made the whole cell
    # answer "no comma" -- so a column of them was neither read as
    # numbers nor warned about. The mantissa is what the comma sits in,
    # so the mantissa is what is classified.
    # The two marks are written out rather than walked: this audit
    # accepts a data method only where what it is handed is a literal
    # or a value it watched being built, and a loop variable is
    # neither.
    at_mark = body.find("e")
    if at_mark < 0:
        at_mark = body.find("E")
    if at_mark >= 0:
        exponent = body[at_mark + 1 :]
        if exponent[:1] == "+" or exponent[:1] == "-":
            exponent = exponent[1:]
        if exponent and _all_ascii_digits(exponent):
            body = body[:at_mark]
    commas = 0
    points = 0
    figures = 0
    for character in body:
        if character == ",":
            commas = commas + 1
            continue
        if character == ".":
            points = points + 1
            continue
        if not ("0" <= character <= "9"):
            return COMMA_NONE
        figures = figures + 1
    # AT LEAST ONE FIGURE, and where there is more than one point they
    # must GROUP. A software version `1.2.3,4` carries only figures,
    # points and commas, and its point before a comma read as PROOF of
    # a decimal comma -- so a column of versions would have been told
    # in capital letters that this file writes decimals with commas.
    # But `1.234.567,89` is how German writes a million and a bit, and
    # refusing every second point would have silenced exactly the
    # convention this note exists for. What tells them apart is the
    # grouping: a thousands group is three figures, so `234` and `567`
    # are one and `2` and `3` are not.
    if not figures:
        return COMMA_NONE
    if points > 1:
        # The grouping is asked of the part BEFORE the comma, which is
        # where the points sit in `1.234.567,89`; the figures after it
        # are the fraction and group nothing.
        before = body[: body.find(",")]
        if not _groups_by_threes(before, "."):
            return COMMA_NONE
    if not commas:
        return COMMA_NONE
    if commas > 1:
        return COMMA_GROUPED
    at = body.find(",")
    point = body.find(".")
    if point >= 0:
        return COMMA_GROUPED if point > at else COMMA_DECIMAL
    head = body[:at]
    tail = body[at + 1 :]
    if not _all_ascii_digits(head) or not _all_ascii_digits(tail):
        return COMMA_NONE
    if len(tail) != 3 or len(head) > 3 or not head:
        return COMMA_DECIMAL
    return COMMA_EITHER


def carries_a_group_comma(text: str) -> bool:
    """Whether this cell reads as a number and settles nothing about it.

    The cells NF44 counts: a number this package read by treating a
    comma as a thousands separator, where the cell itself did not
    settle that the comma was one. A cell that settles it either way is
    not a choice and is not counted.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if comma_reading(text) != COMMA_EITHER:
        return False
    return classify_number(text.strip()) == NUMBER


def written_with_a_decimal_comma(text: str) -> str:
    """One cell of a decimal-comma column, written the way this reads.

    A person whose file writes `1,5` for one and a half is telling this
    tool two things at once: the COMMA is their decimal point, and the
    POINT is their thousands separator. Both roles swap, so the
    transform is one pass -- drop every point, then read every comma as
    a point -- and `1.234,56` becomes `1234.56`.

    WHY THIS EXISTS AT ALL (plan P4-D26, residual R-P4-31). Without a
    declaration such a file is not merely unread, it is read WRONG:
    `1,5` is not a number to this reader at all, so the value is lost,
    and `1,234` IS one -- a valid thousands group -- so it reads as one
    thousand two hundred thirty-four where the person meant one and a
    quarter. The second is the dangerous one, because nothing about it
    looks like a failure.

    THIS IS A TEXT TRANSFORM AND NOT A READING. It says what the cell
    would have looked like written the way this tool reads, so every
    rule downstream is the rule it always was. It is applied only to
    columns a person NAMED, because a comma inside an address or a
    note is not a decimal point and no rule here can tell the
    difference -- which is exactly why the declaration exists.

    Guarantees: accepts any string; returns a string; raises TypeError
    if handed anything that is not a string instance. Determinism: a
    function of the text. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    out = ""
    for character in text:
        if character == ".":
            continue
        if character == ",":
            out = out + "."
            continue
        out = out + character
    return out


def parse_number(text: str) -> "float | None":
    """Read ``text`` as a number, or return None if it is not one.

    Accepted forms (plan P1-D4): a plain decimal number, optionally
    signed, optionally with an exponent; surrounding whitespace; valid
    thousands separators of `GROUP_MARKS`; accounting parentheses for
    negatives, so '(1,234.50)' reads as -1234.5; and, since landing
    2b.2, the minus sign of the character tables in front and a
    hyphen-minus after the figures, so '\u22121234.5' and '1,234.50-'
    read as -1234.5 too.

    Guarantees: accepts text; returns a finite float or None; raises
    TypeError if handed anything that is not a string instance. The
    reading is exact and platform-independent: the same text always
    yields the same number. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = text.strip()
    if not body:
        return None
    negative_parentheses = False
    if body[0] == "(" and body[len(body) - 1] == ")":
        negative_parentheses = True
        body = _minus_written_first(trimmed(body[1 : len(body) - 1]))
        # Parentheses mean "negative" in accounting. A sign inside them
        # is a contradiction -- '(-1)' says negative twice and '(+5)'
        # says both -- and guessing which the writer meant is how a
        # column of debts came out positive (review item P1-R2-F6). It
        # is not a number this reader will interpret. A minus sign or a
        # trailing minus inside them is the same contradiction.
        if body and (body[0] == "+" or body[0] == "-"):
            return None
    else:
        # A MINUS SIGN IN FRONT OR A HYPHEN-MINUS BEHIND is read as the
        # minus it is (landing 2b.2): `\u22126.09` and `1,483.65-` were
        # text, and a column of them published its negatives as
        # positive magnitudes under an affix.
        body = _minus_written_first(body)
    ungrouped = _without_group_separators(body)
    if ungrouped is None:
        return None
    if not _plain_number_shape(ungrouped):
        return None
    value = float(ungrouped)
    # Both ends of the representable range are refused, and for the same
    # reason: the file holds a number this format cannot hold, so any
    # value we put in its place would be one the table does not contain.
    # A huge exponent becomes infinity; a tiny one collapses to zero,
    # which is far more dangerous because zero is a plausible reading.
    # `number_out_of_range` below reports this as its own outcome, so
    # such a value is not mistaken for ordinary text.
    # Not-a-number cannot arise here: the only text that produces it is
    # the word "nan", which the shape check above has already refused.
    if value == float("inf") or value == float("-inf"):
        return None
    if value == 0.0 and _mantissa_has_nonzero_digit(ungrouped):
        return None
    if negative_parentheses:
        return -value
    return value


# What one cell turns out to be, numerically. Every cell gets exactly one
# of these, and the answer is carried through every later gate rather
# than recomputed (review items P1-R3-F3 and P1-R3-F4).
NUMBER = "number"
NUMBER_OUT_OF_RANGE = "out_of_range"
NUMBER_CONTRADICTORY = "contradictory"
NOT_A_NUMBER = "text"

# HOW a numeric cell was written, as opposed to what it is worth. The
# six forms of owner decision 10, and the first-match ladder that reads
# one off a finished cell.
#
# IT LIVES HERE, and not beside the describing code, because BOTH sides
# of the profile/generator boundary have to answer this question with
# one rule: the describer counts the forms of the real column, and the
# generator recounts the forms of the twin it just wrote to check that
# it met the published counts. The generator may not import the
# describing module, so a ladder kept there would have had to be copied
# to be used -- and two copies of a normative ladder drift, which is the
# defect class review item P2-C1-F8 is about. One rule, in the module
# both sides already depend on.
STYLE_PLAIN = "plain"
STYLE_LEADING_ZERO = "leading_zero"
STYLE_LEADING_PLUS = "leading_plus"
STYLE_DECIMAL = "decimal"
STYLE_EXPONENT_LOWER = "exponent_lower"
STYLE_EXPONENT_UPPER = "exponent_upper"


def numeric_style(text: str) -> str:
    """Which of the six forms one numeric cell was written in.

    THE LADDER IS FIRST-MATCH-WINS AND ITS ORDER IS PART OF THE
    CONTRACT (section 7.5.4), because a producer and a consumer that
    test the marks in different orders disagree about a cell carrying
    more than one:

    0. surrounding spaces come off; a value wrapped in a matching pair
       of accounting brackets is unwrapped and trimmed again; thousands
       separators are dropped. What is left is the CORE;
    1. `exponent_upper` -- the core holds an `E`;
    2. `exponent_lower` -- the core holds an `e`;
    3. `decimal` -- the core holds a `.`;
    4. `leading_plus` -- the core begins with `+`;
    5. `leading_zero` -- after any leading `-`, the core begins with `0`
       and is longer than that single `0`;
    6. `plain` -- everything else.

    WHY THE TYPE-BEARING FORMS ARE TESTED FIRST. A reader infers a
    decimal column from a decimal point or an exponent anywhere in it,
    so the mark that decides the inferred type is the one that must be
    counted when a cell carries two. `+0.5` is therefore counted as
    `decimal` and its leading plus is lost for that cell; the totals
    still close, and that is the trade this order makes deliberately.

    TWO SOURCE FORMS ARE NOT FORMS HERE, and the consequence is
    recorded rather than left to be discovered: accounting brackets and
    thousands separators are classified by the digits inside them.
    Brackets are outside the spellings a twin may write, so they are
    not reproduced. A thousands separator IS reproduced, but not as a
    seventh form: a grouped cell is also a `plain` or `decimal` cell,
    and the styles map is a partition that must close on the numeric
    count, so grouping is published beside it as `group_separator`.

    THIS DOCSTRING USED TO GIVE ANOTHER REASON, AND IT WAS FALSE. It
    said a comma would break a CSV row. The CSV writer quotes any cell
    holding a comma and this module's own reader reads it back
    unchanged; the false reason was the whole cause of a grouped charge
    column coming back ungrouped.

    Guarantees:

    - Inputs: the text of one cell, exactly as the file spells it.
      Sensible only for a cell that reads as a number this format can
      hold; every other cell is counted elsewhere.
    - Determinism: the answer depends only on the text.
    - Errors raised: TypeError if handed anything that is not a string
      instance, through `trimmed`.
    - Boundary: the answer is one of six words of this module's own
      vocabulary, so no spelling and no magnitude of the cell can
      travel out through it. No I/O of any kind.
    """
    core = number_core(text)
    if "E" in core:
        return STYLE_EXPONENT_UPPER
    if "e" in core:
        return STYLE_EXPONENT_LOWER
    if "." in core:
        return STYLE_DECIMAL
    if core[:1] == "+":
        return STYLE_LEADING_PLUS
    digits = core
    if digits[:1] == "-":
        digits = digits[1:]
    if digits[:1] == "0" and len(digits) > 1:
        return STYLE_LEADING_ZERO
    return STYLE_PLAIN


def fraction_width(text: str) -> int:
    """How many figures one `decimal`-styled cell writes after its point.

    THE CORE IS THE ONE `numeric_style` READS, and that is the whole
    reason this lives beside it rather than anywhere else. A width taken
    off the raw text and a form taken off the unwrapped core are two
    readings of the same cell, and the census would then name a width
    for a cell the styles map counted under another form -- so the
    brackets come off here exactly as they come off there, and the
    thousands separators with them.

    A point with nothing after it is a width of ZERO, not no width:
    `12.` is a decimal-styled cell and the census must be able to say
    how many figures it wrote, which is none.

    Guarantees:

    - Inputs: the text of one cell, exactly as the file spells it.
      Sensible only for a cell `numeric_style` calls `decimal`; a cell
      of any other form has no point to read and answers 0.
    - Determinism: the answer depends only on the text.
    - Errors raised: TypeError if handed anything that is not a string
      instance, through `trimmed`.
    - Boundary: the answer is a COUNT of characters. No figure of the
      cell, and no magnitude, travels out through it. No I/O of any
      kind.
    """
    core = number_core(text)
    seen = False
    width = 0
    for character in core:
        if seen:
            width = width + 1
        elif character == ".":
            seen = True
    return width


def pad_width(text: str) -> int:
    """How wide the figure field of one zero-padded cell is written.

    THE FACT A FORMS MAP CANNOT SAY, and the reason a census of it has
    to exist at all. `numeric_styles` counts how many cells began with
    a redundant zero; it cannot say whether they were written five
    figures wide or nine. A code column of five-figure cells and a
    record number nine figures wide are both "leading_zero" to that
    map, so a twin honouring the map exactly can still write a field of
    another width -- and a person whose code reads a fixed-width code,
    slices it, or joins on it is holding a twin their code cannot run
    against.

    THE CORE IS THE ONE `numeric_style` READS, for the reason it is in
    `fraction_width`: a width taken off the raw text and a form taken
    off the unwrapped core are two readings of the same cell.

    THE SIGN IS NOT A FIGURE. `-000123` writes six figures, as
    `000123` does, because the width a person sees in a code column is
    the field, not the character count.

    Guarantees:

    - Inputs: the text of one cell, exactly as the file spells it.
      Sensible only for a cell whose value is whole; a cell carrying a
      point answers the figures BEFORE it, which is what padding is
      written into.
    - Determinism: the answer depends only on the text.
    - Errors raised: TypeError if handed anything that is not a string
      instance, through `trimmed`.
    - Boundary: the answer is a COUNT of characters. No figure of the
      cell, and no magnitude, travels out through it. No I/O of any
      kind.
    """
    core = number_core(text)
    if core[:1] == "-" or core[:1] == "+":
        core = core[1:]
    width = 0
    for character in core:
        if character == ".":
            return width
        width = width + 1
    return width


def is_padded(text: str) -> bool:
    """Whether one numeric cell wrote its figure field with a redundant zero.

    THE PAD IS NOT A FORM, AND A PLUS DOES NOT HIDE IT (plan P4-D145, the
    final Codex review's item 6). The ladder of `numeric_style` files a
    cell under ONE form, and a leading plus is tested before a leading
    zero, so `+00100000000000000000` is `leading_plus` and its two zeros
    were counted by no census: 800 such cells at a floor of eleven
    published `field_widths {"20": 800}` beside `pad_widths {}`, and the
    twin wrote every one of them two figures narrower. A cell is padded
    where its form is `leading_zero`, or where it is `leading_plus` and
    the figures after the plus begin with a zero and are more than that
    zero alone; every such cell is counted by the padding census, and a
    twin pads it back.

    Guarantees: accepts the text of one cell that reads as a number this
    format holds; returns a bool. Determinism: a fixed function of the
    text. Raises TypeError if handed anything that is not a string
    instance, through `trimmed`. Boundary: the answer is a truth value.
    No I/O of any kind.
    """
    style = numeric_style(text)
    if style == STYLE_LEADING_ZERO:
        return True
    if style != STYLE_LEADING_PLUS:
        return False
    core = number_core(text)
    return core[1:2] == "0" and pad_width(text) > 1


def classify_number(text: str) -> str:
    """Say, once, what a cell is numerically.

    Returns NUMBER for a value this format can hold;
    NUMBER_OUT_OF_RANGE for a well-formed number too large or too small
    to hold; NUMBER_CONTRADICTORY for numeric notation whose meaning
    conflicts with itself, which today means a sign inside accounting
    parentheses -- '(-5)' says negative twice and '(+5)' says both, and
    guessing either way once published a column of debts as positive;
    and NOT_A_NUMBER for everything else.

    The first three are all NUMERIC-LOOKING: the writer meant a number.
    A column of them is described as numbers rather than being pushed
    into another role by a spent straggler budget, and the counts of
    the two unusable kinds are published so nothing is silent.

    Guarantees: accepts text; returns one of the four names above;
    raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = text.strip()
    if not body:
        return NOT_A_NUMBER
    if body[0] == "(" and body[len(body) - 1] == ")":
        inner = _minus_written_first(trimmed(body[1 : len(body) - 1]))
        if inner and (inner[0] == "+" or inner[0] == "-"):
            # Only contradictory if the rest really is a number; '(-a)'
            # is just text.
            rest = _without_group_separators(inner[1:])
            if rest is not None and _plain_number_shape(rest):
                return NUMBER_CONTRADICTORY
            return NOT_A_NUMBER
    if parse_number(body) is not None:
        return NUMBER
    if number_out_of_range(body):
        return NUMBER_OUT_OF_RANGE
    return NOT_A_NUMBER


def number_out_of_range(text: str) -> bool:
    """True when ``text`` is a number this format cannot hold.

    A well-formed number whose magnitude is too large or too small for a
    64-bit floating-point value. Such a value is NOT ordinary text: it
    is a number the profile cannot carry, and the column is still
    described as numbers with these values counted separately.

    Guarantees: accepts text; returns a truth value; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = text.strip()
    if not body:
        return False
    if body[0] == "(" and body[len(body) - 1] == ")":
        body = _minus_written_first(trimmed(body[1 : len(body) - 1]))
        if body and (body[0] == "+" or body[0] == "-"):
            return False
    else:
        body = _minus_written_first(body)
    ungrouped = _without_group_separators(body)
    if ungrouped is None:
        return False
    if not _plain_number_shape(ungrouped):
        return False
    value = float(ungrouped)
    if value == float("inf") or value == float("-inf"):
        return True
    return value == 0.0 and _mantissa_has_nonzero_digit(ungrouped)


def is_whole_number(value: float) -> bool:
    """True when ``value`` is a whole number (5.0 is, 5.5 is not).

    Guarantees: accepts a finite float; returns a truth value; raises
    nothing for finite input. No I/O of any kind.
    """
    return value == float(int(value))


def valid_date(year: int, month: int, day: int) -> bool:
    """True when the year, month and day name a real calendar date.

    The leap-year rule is the Gregorian one: a year divisible by four
    is a leap year, except a century that is not divisible by four
    hundred.

    It is PUBLIC because the twin's WORKBOOK writer asks the same
    question of the cells it is about to store as dates
    (`dialect.sheet_date_is_real`), and a calendar stated twice is a
    calendar that can be repaired once (plan P4-D291).

    Guarantees: accepts three whole numbers; returns a truth value;
    raises nothing for whole-number input. No I/O of any kind.
    """
    if year < 1 or month < 1 or month > 12 or day < 1:
        return False
    limit = _DAYS_IN_MONTH[month - 1]
    if month == 2 and (year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)):
        limit = 29
    return day <= limit


def _canonical_date(year: str, month: str, day: str) -> "str | None":
    """Return 'YYYY-MM-DD' when the three digit fields name a real date."""
    if not isinstance(year, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(month, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(day, str):
        raise TypeError(_NOT_TEXT)
    if not valid_date(int(year), int(month), int(day)):
        return None
    return f"{year}-{month}-{day}"


def _padded_field(field: str) -> "str | None":
    """One or two ASCII digits, written as two, or None.

    THE FIELD IS PADDED RATHER THAN REFUSED (plan amendment A-P4-1
    item 1). A table that writes `3/5/2024` is writing the same day as
    one that writes `03/05/2024`, and the earlier reader refused the
    first over a leading zero nobody typed. What is published is the
    canonical day either way, so the two spell one date and not two.
    """
    if not isinstance(field, str):
        raise TypeError(_NOT_TEXT)
    if len(field) < 1 or len(field) > 2:
        return None
    if not _all_ascii_digits(field):
        return None
    if len(field) == 1:
        return f"0{field}"
    return field


def _slashed_fields(body: str) -> "tuple[str, str, str] | None":
    """The three fields of a year-last slashed date, each at its width.

    The year is FOUR figures and comes last; the two fields before it
    are one or two figures each. That grammar is what keeps the four
    families apart: `slashed-iso-date` leads with a four-figure year,
    the compact family is eight figures and no delimiter, and no
    spelling can satisfy two of the three.

    Guarantees: accepts a string; returns the month-or-day field, the
    day-or-month field and the year, padded to two, two and four
    figures, or None where the text is not this grammar. Raises
    TypeError if handed anything that is not a string instance. No I/O.
    """
    if not isinstance(body, str):
        raise TypeError(_NOT_TEXT)
    return _delimited_fields(body, "/", 4)


# The month names this package reads, in calendar order, each as the
# three-letter abbreviation and the full word. ENGLISH ONLY, and that
# is a limit rather than an oversight: a name read in one language and
# not another would give one table its dates and the next table beside
# it free text, which is worse than reading neither. Matched with the
# folding rule the rest of this module uses, so `MAR`, `Mar` and `mar`
# are one name.
_MONTH_NAMES = (
    ("jan", "january"),
    ("feb", "february"),
    ("mar", "march"),
    ("apr", "april"),
    ("may", "may"),
    ("jun", "june"),
    ("jul", "july"),
    ("aug", "august"),
    ("sep", "september"),
    ("oct", "october"),
    ("nov", "november"),
    ("dec", "december"),
)


def month_of_name(word: str) -> "str | None":
    """The month a written name stands for, as two figures, or None.

    Guarantees: accepts any string; answers `01` through `12` for a
    name in this package's English vocabulary, abbreviated or written
    in full, whatever its case; answers None for everything else.
    Raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(word, str):
        raise TypeError(_NOT_TEXT)
    # THE PACKAGE HAS ONE FOLDING OPERATION AND THIS IS IT. An earlier
    # revision reached for `.lower()`, which is not the same rule:
    # Unicode case folding maps the long s to `s`, so `ſep` folds to
    # `sep` and lower-casing leaves it alone. The contract says CASE
    # FOLDING, and a second spelling of "the same word" living in one
    # function is how an exception comes apart from the rule it excepts
    # -- this repository has paid for that four times over.
    name = folded(word)
    if not name:
        return None
    place = 0
    for short, whole in _MONTH_NAMES:
        place = place + 1
        if name == short or name == whole:
            if place < 10:
                return f"0{place}"
            return f"{place}"
    return None


def _carries_space(field: str) -> bool:
    """Whether one field of a textual date carries space of its own.

    Written as a function of its own, with the type gate at the top,
    because the offline audit traces a value it can read as a string
    and refuses a method call on anything else -- and a field sliced
    out of a body inside a loop is not something it can follow.
    """
    if not isinstance(field, str):
        raise TypeError(_NOT_TEXT)
    return field != field.strip()


def _textual_fields(
    body: str, comma_after_middle: bool
) -> "tuple[str, str, str] | None":
    """The three fields of a date written with a month NAME.

    THE SEPARATOR IS ONE CHARACTER AND THE SAME ONE BOTH TIMES -- a
    space or a hyphen -- because `17 Mar-2024` is not a shape anybody
    writes, and admitting it would let this member reach for spellings
    the next member is meant to have.

    THE COMMA BELONGS TO ONE SHAPE AND NOT THE OTHER, which is what
    ``comma_after_middle`` decides. `Mar 17, 2024` is written with one
    because the comma follows a DAY; `17 Mar, 2024` puts a comma after
    a month name, which no writer does and no member of this contract
    owns. Stripping it before either member was consulted let the
    day-first member accept a spelling the contract does not describe,
    so a column of them became a date column under a grammar nobody
    had written down.

    Guarantees: accepts a string; returns the first field, the middle
    field and the last field exactly as written, or None where the text
    is not this grammar. Raises TypeError if handed anything that is
    not a string instance. No I/O of any kind.
    """
    if not isinstance(body, str):
        raise TypeError(_NOT_TEXT)
    for mark in (" ", "-"):
        marks: list[int] = []
        place = 0
        for character in body:
            if character == mark:
                marks += [place]
            place = place + 1
        if len(marks) != 2:
            continue
        first = body[0 : marks[0]]
        middle = body[marks[0] + 1 : marks[1]]
        last = body[marks[1] + 1 :]
        if middle[len(middle) - 1 : len(middle)] == ",":
            if not comma_after_middle:
                continue
            middle = middle[0 : len(middle) - 1]
        if not first or not middle or not last:
            continue
        # NO FIELD CARRIES SPACE OF ITS OWN, which is what makes "one
        # separator character, the same one both times" true rather
        # than nearly true. `month_of_name` trims before it matches, so
        # a middle field of ` Mar` answered `03` and `17- Mar-2024` was
        # read as a date under a grammar that permits no such spelling.
        # The day and year fields were never exposed to this -- both
        # ask for ASCII digits and a space is not one -- so the guard
        # is written over all three rather than over the one that
        # happened to need it.
        if _carries_space(first):
            continue
        if _carries_space(middle):
            continue
        if _carries_space(last):
            continue
        return first, middle, last
    return None


def _delimited_fields(
    body: str, mark: str, year_width: int, padded_only: bool = False
) -> "tuple[str, str, str] | None":
    """Three year-last fields split on one delimiter, each at its width.

    The generalization of `_slashed_fields` over the delimiter and the
    width of the year, which is what keeps the dotted and two-digit
    families reading by the same rule as the slashed one rather than by
    a second copy of it. The year comes LAST and is exactly
    ``year_width`` figures; the two fields before it are one or two
    figures each.

    THAT GRAMMAR IS WHAT KEEPS THE FAMILIES APART. A four-figure year
    after slashes is the `month-first-date` pair; a two-figure year
    after slashes is the two-digit pair; a four-figure year after dots
    is the dotted pair; and no spelling satisfies two of them.

    ``padded_only`` REFUSES A ONE-FIGURE FIELD, and it exists for the
    dotted family alone. `1.2.2024` is how a version identifier is
    written, and it is also, character for character, how an unpadded
    dotted date is written -- so a column of versions cleared the date
    line, became a `datetime` column, published endpoints and a ladder
    it had no business publishing, and handed back a twin of ISO days
    where the real column held version numbers. Nothing about the cell
    settles which it is. What does settle it, well enough to be worth a
    rule, is the PADDING: a dotted date is written `17.03.2024` in the
    places that write dotted dates, and a version is not written
    `01.02.2024` anywhere. The unpadded dotted date is therefore read
    as text, which is what it was before this family existed, and the
    version column keeps its own values.

    Guarantees: accepts strings and a positive width; returns the
    first field, the second field and the year, the first two padded to
    two figures and the year exactly as written, or None where the text
    is not this grammar. Raises TypeError if handed anything that is
    not a string instance. No I/O of any kind.
    """
    if not isinstance(body, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(mark, str):
        raise TypeError(_NOT_TEXT)
    marks: list[int] = []
    place = 0
    for character in body:
        if character == mark:
            marks += [place]
        place = place + 1
    if len(marks) != 2:
        return None
    year = body[marks[1] + 1 :]
    if len(year) != year_width or not _all_ascii_digits(year):
        return None
    written_first = body[0 : marks[0]]
    written_second = body[marks[0] + 1 : marks[1]]
    if padded_only and (
        len(written_first) != 2 or len(written_second) != 2
    ):
        return None
    first = _padded_field(written_first)
    second = _padded_field(written_second)
    if first is None or second is None:
        return None
    return first, second, year


# The year a two-figure year stands for, split at the POSIX pivot: 00
# to 68 are this century, 69 to 99 the last one.
TWO_DIGIT_YEAR_PIVOT = 68


def names_a_zero_field(text: str) -> bool:
    """Whether a padded dotted triple carries a zero where a date cannot.

    THE EVIDENCE THAT A DOTTED TRIPLE IS A VERSION AND NOT A DATE
    (review round 1 of landing L18, item 2). The padding rule separates
    `1.2.24` from `17.03.24` and is silent about `01.00.24`, which is
    padded, is shaped exactly like a date, and is not one: no month is
    the zeroth month and no day is the zeroth day. A firmware column of
    `01.02.24`, `01.03.24`, `01.04.24` and one `01.00.24` therefore had
    299 of its 300 cells read as dates, cleared the parse line with the
    odd one counted as a stray, and became a date column -- where
    before this family existed it kept its versions as a set of
    categories.

    A STRAY IS NOT THE SAME AS A CONTRADICTION, which is why this asks
    about the SHAPE and not about parsing. A cell that is no dotted
    triple at all -- a blank, a marker, a word -- is a stray and the
    parse line exists to tolerate it. A cell that IS a dotted triple
    and names a zero field is the column telling you what it holds, and
    tolerating it reads the column against its own evidence.

    Guarantees: accepts one cell as text; returns whether it is a
    padded dotted triple with a two-figure last field naming a zero.
    Determinism: a function of that text. Raises nothing. No I/O.
    """
    fields = _delimited_fields(text, ".", 2, True)
    if fields is None:
        return False
    first, second, _year = fields
    return first == "00" or second == "00"


def year_of_two_figures(year: str) -> str:
    """The four-figure year a two-figure year is read as.

    THIS IS A GUESS AND THE PACKAGE SAYS SO WHEREVER IT MAKES ONE. A
    two-figure year does not carry its century: `24` is 2024 in most
    tables and 1924 in a table of birth dates, and nothing in the cell
    settles which. The pivot is the POSIX one because it is the
    convention the tools around this one already use, so a person who
    knows any of them knows this. The column's remarks name the rule
    wherever this family is read, so nobody meets it by surprise.

    Guarantees: accepts a string of exactly two ASCII digits; returns
    four figures. Raises TypeError if handed anything that is not a
    string instance. No I/O of any kind.
    """
    if not isinstance(year, str):
        raise TypeError(_NOT_TEXT)
    figures = int(year)
    if figures <= TWO_DIGIT_YEAR_PIVOT:
        return f"20{year}"
    return f"19{year}"


def _parse_clock(text: str) -> "str | None":
    """Return 'HH:MM:SS' for a time of day, or None.

    Accepts HH:MM and HH:MM:SS, with an optional fractional part that
    is read and discarded (the profile records whole seconds).
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    hours = _digits_at(text, 0, 2)
    if hours is None or len(text) < 5 or text[2] != ":":
        return None
    minutes = _digits_at(text, 3, 2)
    if minutes is None:
        return None
    seconds = "00"
    rest = text[5:]
    if rest:
        if rest[0] != ":":
            return None
        found = _digits_at(rest, 1, 2)
        if found is None:
            return None
        seconds = found
        fraction = rest[3:]
        if fraction:
            if fraction[0] != ".":
                return None
            if not _all_ascii_digits(fraction[1:]):
                return None
    if int(hours) > 23 or int(minutes) > 59 or int(seconds) > 60:
        return None
    return f"{hours}:{minutes}:{seconds}"


# THE TWO FORMS A COLUMN OF CLOCK VALUES CAN WEAR, and the names the
# profile publishes them under. They are this package's own words, not
# anybody's text: a document naming one of them says which shape the
# column's cells had and nothing about what any cell said.
CLOCK_HH_MM = "hh-mm"
CLOCK_HH_MM_SS = "hh-mm-ss"
CLOCK_FORMS = (CLOCK_HH_MM, CLOCK_HH_MM_SS)

# How many different values each form can spell, which is the whole of
# what a column of that form can hold: a day has 1,440 minutes and
# 86,400 seconds. The generator needs it to know whether a published
# count of different values is reachable at all.
CLOCK_CAPACITY = {CLOCK_HH_MM: 1440, CLOCK_HH_MM_SS: 86400}

# The unit each form counts in, seconds per step: a minute for `hh-mm`
# and a second for `hh-mm-ss`.
_CLOCK_STEP = {CLOCK_HH_MM: 60, CLOCK_HH_MM_SS: 1}


def clock_form(text: str) -> "str | None":
    """Which of the two clock forms one cell wears, or None.

    EXACTLY `HH:MM` OR `HH:MM:SS`, and the word exactly is the rule
    rather than a summary of it. Two ASCII digits in every field, hours
    at most 23, minutes and seconds at most 59, nothing before and
    nothing after. Four shapes a reader might expect are refused, and
    each is refused on purpose:

    - a FRACTIONAL part. A reading that dropped it would describe every
      such cell approximately while publishing an exact ladder;
    - a LEAP SECOND, `23:59:60`. The ordinal space this role counts in
      has no faithful point for it, and making one up would put a value
      in the twin that no clock shows;
    - a SINGLE-DIGIT hour, `9:30`. The published spellings are
      fixed-width, so a column of them could not be written back;
    - anything else around the digits -- a date, an offset, a name.

    A column of cells this refuses takes a later rule, which is where
    such a column already goes today.

    NOTHING COMES OFF FIRST, and that is the fifth refusal rather than
    an oversight. Every other reader in this module trims its cell
    before looking at it; this one may not, because what it publishes
    are the CELLS THEMSELVES -- the two endpoints and eleven ladder
    rungs are values some row of the table wore, character for
    character. Trimming would let a column of ` 09:30 ` cells publish
    `09:30`, a string no row of that table holds, and the ladder would
    stop being a selection of real cells. So a cell with a space, a
    tab or a no-break space around it is a cell this role does not
    read, and it is counted with the rest.

    Guarantees:

    - Inputs: the text of one cell, exactly as the file spells it, and
      exactly as it is judged.
    - Determinism: the answer depends only on the text.
    - Errors raised: TypeError if handed anything that is not a string
      instance.
    - Boundary: the answer is one of two words of this module's own
      vocabulary, or nothing, so no spelling of any cell travels out
      through it. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = text
    hours = _digits_at(body, 0, 2)
    if hours is None or len(body) < 5 or body[2] != ":":
        return None
    minutes = _digits_at(body, 3, 2)
    if minutes is None:
        return None
    if int(hours) > 23 or int(minutes) > 59:
        return None
    if len(body) == 5:
        return CLOCK_HH_MM
    if len(body) != 8 or body[5] != ":":
        return None
    seconds = _digits_at(body, 6, 2)
    if seconds is None or int(seconds) > 59:
        return None
    return CLOCK_HH_MM_SS


def clock_ordinal(text: str, form: str) -> "int | None":
    """Where one cell stands in its own form's unit, or None.

    Minutes of day for `hh-mm`, seconds of day for `hh-mm-ss` -- the
    unit the form itself sets, so every ordinal has a spelling in that
    form and no value the generator interpolates is ever truncated or
    widened to fit a cell.

    None where the cell does not wear the form asked about, which is
    how a cell of the OTHER form is counted unparsed rather than
    silently re-read.

    Guarantees: accepts one cell's text and one of `CLOCK_FORMS`;
    returns a whole number below that form's capacity, or nothing.
    Determinism: a function of the two. Errors raised: TypeError
    through `trimmed`; ValueError for a form this module does not know.
    Boundary: the answer is a COUNT. No I/O of any kind.
    """
    if form not in _CLOCK_STEP:
        raise ValueError(_NOT_TEXT)
    if clock_form(text) != form:
        return None
    body = text
    hours = int(body[0:2])
    minutes = int(body[3:5])
    if form == CLOCK_HH_MM:
        return hours * 60 + minutes
    return (hours * 3600) + (minutes * 60) + int(body[6:8])


def clock_spelling(ordinal: int, form: str) -> str:
    """The one spelling of one ordinal in one form.

    The inverse of `clock_ordinal` and the only way a clock value is
    written, so a producer and a generator cannot spell the same moment
    two ways.

    Guarantees: accepts a whole number below the form's capacity and
    one of `CLOCK_FORMS`; returns fixed-width text. Determinism: a
    function of the two. Errors raised: ValueError for an unknown form
    or an ordinal outside the form's space. Boundary: the text is built
    from the number handed in. No I/O of any kind.
    """
    if form not in _CLOCK_STEP:
        raise ValueError(_NOT_TEXT)
    if isinstance(ordinal, bool) or not isinstance(ordinal, int):
        raise ValueError(_NOT_TEXT)
    if ordinal < 0 or ordinal >= CLOCK_CAPACITY[form]:
        raise ValueError(_NOT_TEXT)
    if form == CLOCK_HH_MM:
        return f"{ordinal // 60:02d}:{ordinal % 60:02d}"
    hours = ordinal // 3600
    rest = ordinal % 3600
    return f"{hours:02d}:{rest // 60:02d}:{rest % 60:02d}"


def _split_offset(text: str) -> "tuple[str, str] | None":
    """Split a time from its UTC offset. Returns (time, offset marker).

    The offset marker is '' when there is none, 'Z' for a trailing Z,
    and the signed offset text otherwise. Returns None when a trailing
    offset is present but malformed.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text:
        return None
    last = text[len(text) - 1]
    if last == "Z" or last == "z":
        return text[: len(text) - 1], "Z"
    if len(text) >= 6:
        marker = text[len(text) - 6]
        if marker == "+" or marker == "-":
            offset = text[len(text) - 6 :]
            hours = _digits_at(offset, 1, 2)
            if hours is None or offset[3] != ":":
                return None
            minutes = _digits_at(offset, 4, 2)
            if minutes is None:
                return None
            # A UTC offset has real bounds: no zone is further than 14
            # hours from UTC and no zone's minute field reaches 60.
            # '+99:99' and '+24:60' used to be accepted and published as
            # though they named a place (review item P1-R1-F9).
            if int(hours) > 14 or int(minutes) > 59:
                return None
            if int(hours) == 14 and int(minutes) != 0:
                return None
            return text[: len(text) - 6], offset
    return text, ""


def parse_datetime(text: str, format_name: str) -> "tuple[str, str] | None":
    """Read ``text`` under one named format; return (canonical, offset).

    The canonical form is 'YYYY-MM-DD' for a date, 'YYYY-MM-DD HH:MM:SS'
    for a date and time, and 'YYYY-Qn' for a quarter -- all of which
    sort correctly as plain text, which is how the profile compares
    them. The second element records the UTC offset that was present:
    '' for none, 'Z', or the signed offset exactly as written.

    Guarantees: accepts text and a name from DATE_FORMATS; returns the
    pair or None; raises TypeError if handed anything that is not a
    string instance, and never raises for unparseable text. A date that
    does not exist in the calendar (a 31st of February, a 13th month)
    is not parsed. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    body = text.strip()
    if not body:
        return None
    if format_name == "iso-date":
        if len(body) != 10 or body[4] != "-" or body[7] != "-":
            return None
        year = _digits_at(body, 0, 4)
        month = _digits_at(body, 5, 2)
        day = _digits_at(body, 8, 2)
        if year is None or month is None or day is None:
            return None
        canonical = _canonical_date(year, month, day)
        if canonical is None:
            return None
        return canonical, ""
    if format_name == "iso-datetime":
        if len(body) < 16 or body[4] != "-" or body[7] != "-":
            return None
        separator = body[10]
        if separator != "T" and separator != " " and separator != "t":
            return None
        year = _digits_at(body, 0, 4)
        month = _digits_at(body, 5, 2)
        day = _digits_at(body, 8, 2)
        if year is None or month is None or day is None:
            return None
        date_part = _canonical_date(year, month, day)
        if date_part is None:
            return None
        split = _split_offset(body[11:])
        if split is None:
            return None
        clock = _parse_clock(split[0])
        if clock is None:
            return None
        return f"{date_part} {clock}", split[1]
    if format_name == "iso-mixed":
        # THE JOINT ISO READING. A cell conforms when EITHER ISO member
        # reads it, and a whole date is read at the family's finest
        # resolution -- midnight of that day -- because the column is
        # described at that resolution and a date-form cell has no
        # other place in it.
        found = parse_datetime(text, "iso-datetime")
        if found is not None:
            return found
        whole = parse_datetime(text, "iso-date")
        if whole is None:
            return None
        return f"{whole[0]} 00:00:00", whole[1]
    if format_name == "slashed-iso-date":
        # THE YEAR LEADS, WHICH IS WHAT MAKES IT UNAMBIGUOUS. A slashed
        # date whose first field is four figures cannot be read the
        # other way round -- there is no calendar in which the day or
        # the month is a four-figure number -- so this form joins the
        # table without the day-first question the two-figure slashed
        # forms carry (plan P4-D4.3 item 1).
        if len(body) != 10 or body[4] != "/" or body[7] != "/":
            return None
        year = _digits_at(body, 0, 4)
        month = _digits_at(body, 5, 2)
        day = _digits_at(body, 8, 2)
        if year is None or month is None or day is None:
            return None
        canonical = _canonical_date(year, month, day)
        if canonical is None:
            return None
        return canonical, ""
    if format_name == "compact-date":
        if len(body) != 8 or not _all_ascii_digits(body):
            return None
        canonical = _canonical_date(body[0:4], body[4:6], body[6:8])
        if canonical is None:
            return None
        return canonical, ""
    if (
        format_name == "textual-day-first-date"
        or format_name == "textual-month-first-date"
    ):
        # A DAY, A MONTH NAME AND A FOUR-FIGURE YEAR, in the order the
        # member names (plan P4-D15). The name is what makes this pair
        # unambiguous where the slashed pair is not: no evidence and no
        # setting is consulted, because `Mar` cannot be a day.
        fields = _textual_fields(
            body, format_name == "textual-month-first-date"
        )
        if fields is None:
            return None
        first, middle, last = fields
        if len(last) != 4 or not _all_ascii_digits(last):
            return None
        if format_name == "textual-day-first-date":
            day = _padded_field(first)
            month = month_of_name(middle)
        else:
            month = month_of_name(first)
            day = _padded_field(middle)
        if day is None or month is None:
            return None
        canonical = _canonical_date(last, month, day)
        if canonical is None:
            return None
        return canonical, ""
    if (
        format_name == "two-digit-month-first-date"
        or format_name == "two-digit-day-first-date"
        or format_name == "dotted-two-digit-month-first-date"
        or format_name == "dotted-two-digit-day-first-date"
    ):
        # A DATE WHOSE YEAR IS TWO FIGURES (plan P4-D15; the dotted
        # half is residual R-P4-4, landing L18). The century is not in
        # the cell, so it is decided by the pivot `year_of_two_figures`
        # fixes and named in the column's remarks.
        #
        # ONE BRANCH FOR BOTH PUNCTUATIONS, because they are one
        # grammar: three year-last fields on one mark, the year two
        # figures. Writing the dotted half as a second copy is how the
        # families come to disagree, which is the reason
        # `_delimited_fields` exists at all.
        dotted = format_name.startswith("dotted-")
        # PADDED ONLY WHERE THE MARK IS A DOT, and for the reason the
        # four-figure dotted family gives: `1.2.24` is how a version
        # identifier is written and, character for character, how an
        # unpadded dotted date is written. Nothing in the cell settles
        # it; the padding does, well enough to be worth a rule. A
        # slashed `1/2/24` carries no such rival and keeps its reading.
        fields = _delimited_fields(
            body, "." if dotted else "/", 2, dotted
        )
        if fields is None:
            return None
        first, second, short = fields
        year = year_of_two_figures(short)
        if format_name.endswith("month-first-date"):
            canonical = _canonical_date(year, first, second)
        else:
            canonical = _canonical_date(year, second, first)
        if canonical is None:
            return None
        return canonical, ""
    if (
        format_name == "dotted-month-first-date"
        or format_name == "dotted-day-first-date"
    ):
        # THE SAME GRAMMAR WRITTEN WITH DOTS (plan P4-D15). Two dots and
        # a four-figure year last, which no decimal number satisfies:
        # `17.03` carries one dot and is a number, `17.03.2024` carries
        # two and is not.
        fields = _delimited_fields(body, ".", 4, True)
        if fields is None:
            return None
        first, second, year = fields
        if format_name == "dotted-month-first-date":
            canonical = _canonical_date(year, first, second)
        else:
            canonical = _canonical_date(year, second, first)
        if canonical is None:
            return None
        return canonical, ""
    if format_name == "month-first-date" or format_name == "day-first-date":
        # PADDED OR NOT, AND THE FAMILIES STILL DO NOT OVERLAP (plan
        # amendment A-P4-1 item 1). The ten-character rule retired here
        # and here only: the year still has to be four figures and
        # still has to come last, which is what keeps `3/5/2024` out of
        # every other member's reach.
        fields = _slashed_fields(body)
        if fields is None:
            return None
        first, second, year = fields
        if format_name == "month-first-date":
            canonical = _canonical_date(year, first, second)
        else:
            canonical = _canonical_date(year, second, first)
        if canonical is None:
            return None
        return canonical, ""
    if (
        format_name == "month-first-datetime"
        or format_name == "day-first-datetime"
    ):
        # A SLASHED DATE, ONE SPACE, THEN A CLOCK (plan amendment
        # A-P4-1 item 2). The date half is the same grammar the two
        # date-only slashed members read, padded or not; the clock half
        # is the time-of-day role's own two forms and nothing wider, so
        # a stamp this reads is one whose two halves are each already
        # read somewhere in this module.
        mark = 0
        place = 0
        for character in body:
            if character == " ":
                mark = place
            place = place + 1
        if mark < 1:
            return None
        fields = _slashed_fields(body[0:mark])
        if fields is None:
            return None
        first, second, year = fields
        if format_name == "month-first-datetime":
            date_part = _canonical_date(year, first, second)
        else:
            date_part = _canonical_date(year, second, first)
        if date_part is None:
            return None
        # THE CLOCK HALF IS THE TIME-OF-DAY ROLE'S OWN TWO FORMS AND
        # NOTHING WIDER, which is what the amendment fixes and what
        # keeps these two members from quietly accepting a fractional
        # second the contract's row for them does not mention.
        if clock_form(body[mark + 1 :]) is None:
            return None
        clock = _parse_clock(body[mark + 1 :])
        if clock is None:
            return None
        return f"{date_part} {clock}", ""
    if format_name == "slashed-iso-datetime":
        # A `slashed-iso-date`, ONE space, then a clock in the time-of-day
        # role's two forms (landing 2b.3). Both halves are read by readers
        # this module already has, exactly as the two slashed stamps
        # above are built, so a stamp this accepts is one whose date half
        # `slashed-iso-date` accepts and whose clock half `clock_form`
        # does; a fraction, an offset or a second space is refused.
        mark = 0
        place = 0
        for character in body:
            if character == " ":
                mark = place
            place = place + 1
        if mark != 10:
            return None
        whole = parse_datetime(body[0:mark], "slashed-iso-date")
        if whole is None:
            return None
        if clock_form(body[mark + 1 :]) is None:
            return None
        clock = _parse_clock(body[mark + 1 :])
        if clock is None:
            return None
        return f"{whole[0]} {clock}", ""
    if format_name == "iso-month":
        # A MONTH NAMES A SPAN, WHICH IS WHY IT HAS A SPACE OF ITS OWN
        # (plan P4-D4.3 item 2). `2024-03` is not a day and turning it
        # into one would put a value in the column that no cell holds,
        # so the canonical form IS the text and it sorts as text.
        if len(body) != 7 or body[4] != "-":
            return None
        year = _digits_at(body, 0, 4)
        month = _digits_at(body, 5, 2)
        if year is None or month is None:
            return None
        if int(month) < 1 or int(month) > 12:
            return None
        # THE YEAR IS ONE THE CALENDAR HAS. `valid_date` refuses year
        # zero for every reader that names a day, and the two SPAN
        # readers have to refuse it for the same reason: the contract's
        # canonical form runs from `0001` up, and a producer that
        # published `0000-01` would write a description its own loader
        # is meant to refuse (review item P4-DATE3-F4).
        if int(year) < 1:
            return None
        return f"{year}-{month}", ""
    if format_name == "year-quarter":
        if len(body) != 7 or body[4] != "-":
            return None
        marker = body[5]
        if marker != "Q" and marker != "q":
            return None
        year = _digits_at(body, 0, 4)
        quarter = body[6]
        if year is None or quarter < "1" or quarter > "4":
            return None
        # The same year rule, and it was missing here before the month
        # made it visible (review item P4-DATE3-F4).
        if int(year) < 1:
            return None
        return f"{year}-Q{quarter}", ""
    return None


# -- how a date was WRITTEN, beside what it was read as (landing 2b.6) --
#
# THE REVERSAL OF OWNER DECISION 5 (owner ruling of 2026-09-15: the twin
# writes anything as the original source wrote it). Everything above this
# line READS a cell and answers which instant it names, and a reading is
# deliberately lossy about spelling: `03/17/2024`, `3/17/2024`,
# `17.03.2024` and `17-MAR-2024` all answer `2024-03-17`. Decision 5 then
# had the twin write that answer back in ISO, so a month-first table got
# ISO twin dates and every parsing call a person had written against
# their own export failed on every cell of the twin.
#
# What follows is the other direction: the vocabulary of the conventions
# one member admits, a reader per convention so that the describing step
# can COUNT them, and one writer that is the inverse of `parse_datetime`
# under a member and a style. Every census here counts FORMS -- how cells
# were written -- and never a value of anybody's table.

# The members whose month and day fields may be written with one figure
# or with two. Everything else fixes both widths, so nothing is left for
# a census to say: the dotted families are padded by C6-22, and the ISO,
# slashed-ISO and compact families are fixed width by their own readers.
VARIABLE_WIDTH_MEMBERS = (
    "month-first-date",
    "day-first-date",
    "two-digit-month-first-date",
    "two-digit-day-first-date",
    "month-first-datetime",
    "day-first-datetime",
)

# The two members that write the month as an English NAME.
TEXTUAL_MEMBERS = (
    "textual-day-first-date",
    "textual-month-first-date",
)

# The members whose year is written with TWO figures.
TWO_FIGURE_MEMBERS = (
    "two-digit-month-first-date",
    "two-digit-day-first-date",
    "dotted-two-digit-month-first-date",
    "dotted-two-digit-day-first-date",
)

# The members written with dots, which are padded on both fields.
DOTTED_MEMBERS = (
    "dotted-month-first-date",
    "dotted-day-first-date",
    "dotted-two-digit-month-first-date",
    "dotted-two-digit-day-first-date",
)

# Which of the two numeric fields comes first, written out rather than
# worked out from the member's name: `month-first-datetime` does not end
# in `-date`, and a rule that read the name got that one member wrong.
MONTH_FIRST_MEMBERS = (
    "month-first-date",
    "dotted-month-first-date",
    "two-digit-month-first-date",
    "dotted-two-digit-month-first-date",
    "month-first-datetime",
    "textual-month-first-date",
)
DAY_FIRST_MEMBERS = (
    "day-first-date",
    "dotted-day-first-date",
    "two-digit-day-first-date",
    "dotted-two-digit-day-first-date",
    "day-first-datetime",
    "textual-day-first-date",
)

# HOW WIDE A CELL WROTE THE FIELDS THAT COULD SHOW IT, as ONE word per
# cell rather than one per field. The skeptic of the spelling audit
# measured why: on a column half written `%m/%d/%Y` and half `m/d/yyyy`,
# not one real cell mixed the two, and two independent rotations would
# have written about half the cells that could show it in a style no row
# used -- `03/5/2024`. So the census is JOINT, over the cell.
#
# A field SHOWS its width only where its value is below ten. `17` is two
# figures under either convention, so a cell whose month and day are both
# above nine is counted under no key at all, and this census's total is
# the cells that could show something.
#
# AND A CELL WHERE ONLY ONE FIELD SHOWS says WHICH field it was (plan
# P4-D132). The four joint words are about a cell whose two fields are
# both below ten; a cell with one such field is counted under the field
# that showed it. Counted under the bare `padded` or `unpadded` instead,
# as the first revision did, a column written `m/dd/yyyy` published
# `unpadded` for every January-to-September date past the ninth and
# `padded` for every October-to-December date before the tenth, and its
# twin spent those words on cells whose OTHER field showed: measured on
# 400 dates, 106 twin cells were written `5/4/2024` or `08/28/2022`,
# conventions no real cell used.
WIDTH_PADDED = "padded"
WIDTH_UNPADDED = "unpadded"
WIDTH_FIRST_PADDED = "first-padded"
WIDTH_SECOND_PADDED = "second-padded"
WIDTH_FIRST_FIELD_PADDED = "first-field-padded"
WIDTH_FIRST_FIELD_UNPADDED = "first-field-unpadded"
WIDTH_SECOND_FIELD_PADDED = "second-field-padded"
WIDTH_SECOND_FIELD_UNPADDED = "second-field-unpadded"
# The four words for a cell whose two fields both show a width.
FIELD_WIDTH_STYLES_BOTH = (
    WIDTH_PADDED,
    WIDTH_UNPADDED,
    WIDTH_FIRST_PADDED,
    WIDTH_SECOND_PADDED,
)
# The two words for a cell whose FIRST field alone shows one, and the two
# for its SECOND field alone.
FIELD_WIDTH_STYLES_FIRST = (WIDTH_FIRST_FIELD_PADDED, WIDTH_FIRST_FIELD_UNPADDED)
FIELD_WIDTH_STYLES_SECOND = (
    WIDTH_SECOND_FIELD_PADDED,
    WIDTH_SECOND_FIELD_UNPADDED,
)
FIELD_WIDTH_STYLES = (
    FIELD_WIDTH_STYLES_BOTH
    + FIELD_WIDTH_STYLES_FIRST
    + FIELD_WIDTH_STYLES_SECOND
)

# HOW A MONTH NAME WAS WRITTEN, again as one joint word: the case, the
# length, the mark between the fields and whether a comma followed the
# day. Joint for the reason the widths are: a hand-entered column mixing
# `17-MAR-2024` with `17 Mar 2024` carries the case and the mark
# together, and independent rotations would invent `17 MAR 2024`.
NAME_CASES = ("upper", "title", "lower")
NAME_LENGTHS = ("abbreviated", "full")
NAME_MARKS = ("space", "hyphen")
NAME_COMMAS = ("comma", "no-comma")
# THE LENGTH A NAME OF MAY SHOWS, which is neither (plan P4-D133). `May`
# is its own abbreviation, so a cell of May says nothing about length --
# but it says everything else: its case, its mark and its comma. The
# first revision counted such a cell under no key at all, so a column of
# `17-MAY-2024` published an empty census and its twin was written
# `17 May 2024`: `%d-%b-%Y` read 240 real cells of 240 and no twin cell.
NAME_LENGTH_EITHER = "either"


def _name_styles() -> "tuple[str, ...]":
    """Every joint month-name style, built from the four vocabularies."""
    built: "list[str]" = []
    for case in NAME_CASES:
        for length in NAME_LENGTHS:
            for mark in NAME_MARKS:
                for comma in NAME_COMMAS:
                    built += [f"{case}-{length}-{mark}-{comma}"]
    return tuple(built)


MONTH_NAME_STYLES_RESOLVED = _name_styles()


def _either_styles(no_comma: bool) -> "tuple[str, ...]":
    """Every joint style a cell of MAY can show, its length `either`."""
    built: "list[str]" = []
    for case in NAME_CASES:
        for mark in NAME_MARKS:
            for comma in NAME_COMMAS:
                if no_comma and comma == "comma":
                    continue
                built += [f"{case}-{NAME_LENGTH_EITHER}-{mark}-{comma}"]
    return tuple(built)


MONTH_NAME_STYLES_EITHER = _either_styles(False)
MONTH_NAME_STYLES = MONTH_NAME_STYLES_RESOLVED + MONTH_NAME_STYLES_EITHER


def _no_comma_styles() -> "tuple[str, ...]":
    """The styles a DAY-FIRST textual column can wear.

    `17 Mar, 2024` puts a comma after a month name, which no writer does
    and which `_textual_fields` refuses, so half the joint vocabulary is
    unreachable for that member and the contract says so rather than
    leaving a loader to accept a count no producer can write.
    """
    built: "list[str]" = []
    for case in NAME_CASES:
        for length in NAME_LENGTHS:
            for mark in NAME_MARKS:
                built += [f"{case}-{length}-{mark}-no-comma"]
    return tuple(built)


MONTH_NAME_STYLES_NO_COMMA_RESOLVED = _no_comma_styles()
MONTH_NAME_STYLES_NO_COMMA_EITHER = _either_styles(True)
MONTH_NAME_STYLES_NO_COMMA = (
    MONTH_NAME_STYLES_NO_COMMA_RESOLVED + MONTH_NAME_STYLES_NO_COMMA_EITHER
)


def name_styles_of(format_name: str) -> "tuple[str, ...]":
    """The styles naming a LENGTH that one textual member's cells can show."""
    if format_name == "textual-day-first-date":
        return MONTH_NAME_STYLES_NO_COMMA_RESOLVED
    return MONTH_NAME_STYLES_RESOLVED


def name_styles_either_of(format_name: str) -> "tuple[str, ...]":
    """The `either` styles one textual member's cells of MAY can show."""
    if format_name == "textual-day-first-date":
        return MONTH_NAME_STYLES_NO_COMMA_EITHER
    return MONTH_NAME_STYLES_EITHER


def name_style_at_length(style: str, to_either: bool) -> str:
    """One joint style with its length set aside or set (plan P4-D133).

    `to_either` true gives the `either` word a cell of May writes;
    false gives the abbreviated word, which is the length a rank that must
    show one takes where the census names no length at all -- the same
    length `DEFAULT_NAME_STYLE` has always carried.

    Guarantees: accepts a joint style word; returns a joint style word.
    Determinism: a function of the two. Raises TypeError for a style that
    is not text. No I/O of any kind.
    """
    case, _length, mark, comma = _name_parts(style)
    length = NAME_LENGTH_EITHER if to_either else "abbreviated"
    return f"{case}-{length}-{mark}-{comma}"

# The two width words a member with ONE numeric field can show: the
# textual members write the month as a name, so there is no second field
# for `first-padded` or `second-padded` to be about.
FIELD_WIDTH_STYLES_ONE_FIELD = (WIDTH_PADDED, WIDTH_UNPADDED)

# What a cell the census cannot reach is written in where the census
# names nothing at all: the commonest export spelling, `17 Mar 2024`.
DEFAULT_NAME_STYLE = "title-abbreviated-space-no-comma"
DEFAULT_FIELD_WIDTH = WIDTH_PADDED

# The case of the letter Q in a quarter, and of a zulu offset marker.
# Each is its own census rather than a second key of the map beside it:
# `z` as a second `utc_offsets` key would count as a second OFFSET and
# trip D5 and the shared-clock reading, when it is one offset written
# two ways.
QUARTER_MARKER_CASES = ("upper", "lower")
ZULU_CASES = ("upper", "lower")


def _upper_text(text: str) -> str:
    """Upper case, behind a gate, so the audit can follow the value."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return text.upper()


def _lower_text(text: str) -> str:
    """Lower case, behind a gate, for the reason above."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return text.lower()


def _titled(text: str) -> str:
    """One capital and the rest in lower case, built rather than called.

    There is no `title` among the string methods this package's offline
    audit admits, and there should not be: `title` capitalises after
    every non-letter, which is not what a month name wants.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return f"{_upper_text(text[0:1])}{_lower_text(text[1:])}"


def _name_case(name: str) -> "str | None":
    """Which of the three cases one written month name wears, or None.

    None for a spelling outside the three -- `mAr` -- which is counted
    under no key rather than forced into one.
    """
    if not isinstance(name, str):
        raise TypeError(_NOT_TEXT)
    if name == _upper_text(name):
        return "upper"
    if name == _lower_text(name):
        return "lower"
    if name == _titled(name):
        return "title"
    return None


def _one_field_style(written: str) -> "str | None":
    """Whether one written numeric field shows a width, and which.

    `05` is padded, `5` is unpadded, and `17` shows nothing: it is two
    figures under either convention.
    """
    if not isinstance(written, str):
        raise TypeError(_NOT_TEXT)
    if len(written) == 1:
        return WIDTH_UNPADDED
    if len(written) == 2 and written[0] == "0":
        return WIDTH_PADDED
    return None


def day_shows_width(word: str, format_name: str, month: int, day: int) -> bool:
    """Whether a date on this day is counted under THIS width word (P4-D256).

    `date_field_style` read from the other side: it gives the word one
    written cell shows, and this says which days can show a given word.
    The two are one rule, and this is the one a producer needs -- the
    census names a convention, and a twin that puts its dates on days
    which show ANOTHER convention publishes that other one however
    carefully it writes each cell.

    A one-field word needs its OWN field below ten and the other at ten
    or more, which is the whole of what that word says: a cell whose two
    fields both show is counted under a joint word, and a census naming
    the joint word beside it is a second key the single-key census does
    not have. A JOINT word is met by either -- a cell showing one field
    is folded into the joint word its column's own cells wrote
    (`folded_width_tally`), so it is counted under that word in the end.
    A textual member writes its month as a name, so its day is the one
    field that can show anything and only the joint words are reachable.

    Guarantees: accepts a member of `FIELD_WIDTH_STYLES`, the member the
    column is read under and a calendar month and day; returns a bool,
    and False for a member that fixes both widths. Determinism: a fixed
    function of the four. Raises nothing. No I/O of any kind.
    """
    if format_name in TEXTUAL_MEMBERS:
        return day < 10 and word in FIELD_WIDTH_STYLES_BOTH
    if format_name not in VARIABLE_WIDTH_MEMBERS:
        return False
    first = month
    second = day
    if format_name in DAY_FIRST_MEMBERS:
        first = day
        second = month
    if word in FIELD_WIDTH_STYLES_FIRST:
        return first < 10 and second >= 10
    if word in FIELD_WIDTH_STYLES_SECOND:
        return second < 10 and first >= 10
    if word in FIELD_WIDTH_STYLES_BOTH:
        return first < 10 or second < 10
    return False


def pair_widths(width: str) -> "tuple[bool, bool]":
    """One width word as a padding decision per field (plan P4-D132).

    A joint word decides both fields. A one-field word decides its own
    field and leaves the other at the padded default, which is never
    seen on the cells that word is counted over: the other field is ten
    or more there.

    Guarantees: accepts a member of `FIELD_WIDTH_STYLES` (anything else
    reads as padded on both); returns (first padded, second padded).
    Determinism: a function of the word. Raises nothing. No I/O.
    """
    if width == WIDTH_UNPADDED:
        return False, False
    if width == WIDTH_FIRST_PADDED:
        return True, False
    if width == WIDTH_SECOND_PADDED:
        return False, True
    if width == WIDTH_FIRST_FIELD_UNPADDED:
        return False, True
    if width == WIDTH_SECOND_FIELD_UNPADDED:
        return True, False
    return True, True


def joint_width(first_padded: bool, second_padded: bool) -> str:
    """The joint word for a padding decision per field: `pair_widths` reversed."""
    if first_padded and second_padded:
        return WIDTH_PADDED
    if first_padded:
        return WIDTH_FIRST_PADDED
    if second_padded:
        return WIDTH_SECOND_PADDED
    return WIDTH_UNPADDED


def field_width_word(which: int, padded: bool) -> str:
    """The one-field word for field 1 or 2, padded or not (plan P4-D132)."""
    if which == 2:
        return WIDTH_SECOND_FIELD_PADDED if padded else WIDTH_SECOND_FIELD_UNPADDED
    return WIDTH_FIRST_FIELD_PADDED if padded else WIDTH_FIRST_FIELD_UNPADDED


def width_of_field_word(word: str) -> str:
    """The joint word a rank counted under a one-field word is written with.

    `padded` for a padded field and `unpadded` for an unpadded one: the
    other field is ten or more on every such rank, so it is written in
    two figures either way and only this field's decision shows.
    """
    if word == WIDTH_FIRST_FIELD_UNPADDED or word == WIDTH_SECOND_FIELD_UNPADDED:
        return WIDTH_UNPADDED
    if word == WIDTH_FIRST_FIELD_PADDED or word == WIDTH_SECOND_FIELD_PADDED:
        return WIDTH_PADDED
    return word


def _raw_pair(body: str, mark: str) -> "tuple[str, str] | None":
    """The two fields before the year, exactly as they were written.

    `_delimited_fields` pads what it returns, because what it answers is
    the DATE; this answers the writing, so nothing is padded here.
    """
    if not isinstance(body, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(mark, str):
        raise TypeError(_NOT_TEXT)
    marks: "list[int]" = []
    place = 0
    for character in body:
        if character == mark:
            marks += [place]
        place = place + 1
    if len(marks) != 2:
        return None
    return body[0 : marks[0]], body[marks[0] + 1 : marks[1]]


def _date_half(body: str, format_name: str) -> str:
    """The date part of a slashed stamp, or the whole of a date cell."""
    if not isinstance(body, str):
        raise TypeError(_NOT_TEXT)
    if format_name not in SLASHED_STAMPS:
        return body
    mark = 0
    place = 0
    for character in body:
        if character == " ":
            mark = place
        place = place + 1
    return body[0:mark]


def _textual_written(
    body: str, month_first: bool
) -> "tuple[str, str, str, bool] | None":
    """A textual date's day field, month name, mark and comma, as written.

    `_textual_fields` answers what the cell MEANS and strips the comma
    on the way; this answers how it was written, so the comma comes back
    as a fact of its own. The grammar is the same one, character for
    character, because two readings of one shape is how the families
    come apart.
    """
    if not isinstance(body, str):
        raise TypeError(_NOT_TEXT)
    for mark in (" ", "-"):
        marks: "list[int]" = []
        place = 0
        for character in body:
            if character == mark:
                marks += [place]
            place = place + 1
        if len(marks) != 2:
            continue
        first = body[0 : marks[0]]
        middle = body[marks[0] + 1 : marks[1]]
        last = body[marks[1] + 1 :]
        comma = False
        if middle[len(middle) - 1 : len(middle)] == ",":
            if not month_first:
                continue
            middle = middle[0 : len(middle) - 1]
            comma = True
        if not first or not middle or not last:
            continue
        if _carries_space(first):
            continue
        if _carries_space(middle):
            continue
        if _carries_space(last):
            continue
        name_mark = "space" if mark == " " else "hyphen"
        if month_first:
            return middle, first, name_mark, comma
        return first, middle, name_mark, comma
    return None


def _name_parts(style: str) -> "tuple[str, str, str, str]":
    """One joint month-name style word, taken back apart."""
    if not isinstance(style, str):
        raise TypeError(_NOT_TEXT)
    parts = style.split("-")
    if len(parts) < 4:
        return "title", "abbreviated", "space", "no-comma"
    comma = "comma"
    if parts[3] == "no":
        comma = "no-comma"
    return parts[0], parts[1], parts[2], comma


def name_style_agrees(published: str, written: str) -> bool:
    """Whether a written month-name style meets a published one (P4-D257).

    THE PERMITTED READING OF `either`, STATED ONCE so the generator and
    the checker cannot hold two (the extra review of c5d09d5, item 8).
    `May` is its own abbreviation, so a column every cell of which falls
    in May says nothing about length and publishes `either`: 240 cells
    written `01-MAY-2020` publish `upper-either-hyphen-no-comma`. A twin
    of it writes other months, each of which must resolve that length
    one way -- the generator writes the abbreviated name -- and the
    checker counted every one of those 240 spellings as a style nobody
    published, so the file failed `names.unnamed` while its generation
    report named no deviation at all.

    A published `either` is met by the same case, mark and comma at
    EITHER length, and by nothing else: the three parts the source did
    settle are still exact. A published length is met by itself alone.

    Guarantees: accepts a published style and a written one; returns a
    bool, and True only for styles agreeing in case, mark and comma.
    Determinism: a fixed function of the two. Raises TypeError if either
    is not a string instance. No I/O of any kind.
    """
    if published == written:
        return True
    first = _name_parts(published)
    second = _name_parts(written)
    if first[1] != NAME_LENGTH_EITHER:
        return False
    return (
        first[0] == second[0]
        and first[2] == second[2]
        and first[3] == second[3]
    )


def date_field_style(text: str, format_name: str) -> "str | None":
    """The width convention one written cell shows, or None.

    One of the four joint words where both numeric fields are below ten,
    and the word of the field that showed where only one is (plan
    P4-D132). None where the member fixes both widths, where the cell
    does not read under the member, or where no field of it could show a
    width at all -- which is what makes this census's total the cells
    that could show something rather than every parsed cell.

    Guarantees: accepts one cell and the member it parsed under; returns
    a member of `FIELD_WIDTH_STYLES` or nothing. Determinism: a function
    of the two. Raises TypeError if either is not a string instance. No
    I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    numeric = format_name in VARIABLE_WIDTH_MEMBERS
    if not numeric and format_name not in TEXTUAL_MEMBERS:
        return None
    if parse_datetime(text, format_name) is None:
        return None
    body = text.strip()
    if not numeric:
        found = _textual_written(
            body, format_name == "textual-month-first-date"
        )
        if found is None:
            return None
        return _one_field_style(found[0])
    pair = _raw_pair(_date_half(body, format_name), "/")
    if pair is None:
        return None
    first = _one_field_style(pair[0])
    second = _one_field_style(pair[1])
    if first is None and second is None:
        return None
    if first is None:
        # Only the second field showed, and the word says so (P4-D132).
        if second == WIDTH_PADDED:
            return WIDTH_SECOND_FIELD_PADDED
        return WIDTH_SECOND_FIELD_UNPADDED
    if second is None:
        if first == WIDTH_PADDED:
            return WIDTH_FIRST_FIELD_PADDED
        return WIDTH_FIRST_FIELD_UNPADDED
    if first == second:
        return first
    if first == WIDTH_PADDED:
        return WIDTH_FIRST_PADDED
    return WIDTH_SECOND_PADDED


def month_name_style(text: str, format_name: str) -> "str | None":
    """The joint month-name style one written cell shows, or None.

    A cell whose month is MAY, whose two written forms are one word,
    shows no length: nothing in `May` says whether the column abbreviates.
    It still shows its case, its mark and its comma, so it is counted
    under the `either` word that carries those (plan P4-D133) rather than
    under no key -- which is what left a column of `17-MAY-2024` with an
    empty census and a twin written `17 May 2024`. None for a spelling
    outside the three cases.

    Guarantees: accepts one cell and the member it parsed under; returns
    a member of `MONTH_NAME_STYLES` or nothing. Determinism: a function
    of the two. Raises TypeError if either is not a string instance. No
    I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    if format_name not in TEXTUAL_MEMBERS:
        return None
    if parse_datetime(text, format_name) is None:
        return None
    body = text.strip()
    found = _textual_written(body, format_name == "textual-month-first-date")
    if found is None:
        return None
    name = found[1]
    case = _name_case(name)
    if case is None:
        return None
    length = "abbreviated" if len(name) == 3 else "full"
    if folded(name) == "may":
        # ITS LENGTH SHOWS NOTHING, AND THE REST DOES (plan P4-D133).
        length = NAME_LENGTH_EITHER
    comma = "comma" if found[3] else "no-comma"
    return f"{case}-{length}-{found[2]}-{comma}"


def quarter_marker_case(text: str, format_name: str) -> "str | None":
    """Whether a quarter cell wrote its marker upper or lower case."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    if format_name != "year-quarter":
        return None
    if parse_datetime(text, format_name) is None:
        return None
    body = text.strip()
    if body[5] == "Q":
        return "upper"
    if body[5] == "q":
        return "lower"
    return None


def zulu_case(text: str, format_name: str) -> "str | None":
    """Whether a cell carrying a zulu offset wrote it upper or lower case."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    if format_name != "iso-datetime" and format_name != "iso-mixed":
        return None
    found = parse_datetime(text, format_name)
    if found is None or found[1] != "Z":
        return None
    body = text.strip()
    last = body[len(body) - 1]
    if last == "Z":
        return "upper"
    if last == "z":
        return "lower"
    return None


def month_spelling(month: int, length: str, case: str) -> str:
    """One month written as a name: the inverse of `month_of_name`.

    The one place a month NAME is built, as `clock_spelling` is the one
    place a clock is, so a producer counting names and a generator
    writing them cannot spell the same month two ways.

    Guarantees: accepts a month from 1 to 12, one of `NAME_LENGTHS` and
    one of `NAME_CASES`; returns the name. Determinism: a function of the
    three. Raises ValueError for a month outside the calendar. No I/O.
    """
    if isinstance(month, bool) or not isinstance(month, int):
        raise ValueError(_NOT_TEXT)
    if month < 1 or month > 12:
        raise ValueError(_NOT_TEXT)
    pair = _MONTH_NAMES[month - 1]
    name = pair[1] if length == "full" else pair[0]
    if case == "upper":
        return _upper_text(name)
    if case == "lower":
        return _lower_text(name)
    return _titled(name)


def _field_text(value: int, padded: bool) -> str:
    """One numeric field at the width its style asks for."""
    if padded or value >= 10:
        return f"{value:02d}"
    return f"{value}"


def written_date(
    year: int,
    month: int,
    day: int,
    format_name: str,
    width: str = DEFAULT_FIELD_WIDTH,
    name_style: str = DEFAULT_NAME_STYLE,
) -> str:
    """One day written the way this member's own source wrote it.

    THE INVERSE OF `parse_datetime` for every member that names a day,
    and the whole of what reversing owner decision 5 means for the date
    half of a cell: field order, delimiter, the width of each field, the
    two-figure year, the month name's case and length, the mark between
    a textual date's fields and the comma after its day.

    Guarantees: accepts a calendar date, one member of `DATE_FORMATS`
    that names a day, one of `FIELD_WIDTH_STYLES` and one of
    `MONTH_NAME_STYLES`; returns the cell's date half, which
    `parse_datetime` reads back under the same member as the same day.
    Determinism: a function of its arguments. Raises ValueError through
    `month_spelling` for a month outside the calendar. No I/O of any kind.
    """
    if format_name == "compact-date":
        return f"{year:04d}{month:02d}{day:02d}"
    if format_name == "slashed-iso-date" or format_name == "slashed-iso-datetime":
        return f"{year:04d}/{month:02d}/{day:02d}"
    if format_name in TEXTUAL_MEMBERS:
        case, length, mark, comma = _name_parts(name_style)
        name = month_spelling(month, length, case)
        between = " " if mark == "space" else "-"
        day_text = _field_text(day, width != WIDTH_UNPADDED)
        if format_name == "textual-day-first-date":
            return f"{day_text}{between}{name}{between}{year:04d}"
        tail = "," if comma == "comma" else ""
        return f"{name}{between}{day_text}{tail}{between}{year:04d}"
    if format_name not in MONTH_FIRST_MEMBERS and (
        format_name not in DAY_FIRST_MEMBERS
    ):
        # Every ISO member, and anything a later landing adds without
        # saying how it is written: the form that has always been safe.
        return f"{year:04d}-{month:02d}-{day:02d}"
    dotted = format_name in DOTTED_MEMBERS
    between = "." if dotted else "/"
    first_padded, second_padded = pair_widths(width)
    if dotted:
        # C6-22: the dotted families are read padded and only padded,
        # because `1.2.2024` is how a version identifier is written.
        first_padded = True
        second_padded = True
    first_value = month
    second_value = day
    if format_name in DAY_FIRST_MEMBERS:
        first_value = day
        second_value = month
    year_text = f"{year:04d}"
    if format_name in TWO_FIGURE_MEMBERS:
        year_text = f"{year % 100:02d}"
    first_text = _field_text(first_value, first_padded)
    second_text = _field_text(second_value, second_padded)
    return f"{first_text}{between}{second_text}{between}{year_text}"


def written_quarter(year: int, quarter: int, marker: str) -> str:
    """One quarter written with the marker case its source wrote."""
    letter = "Q" if marker != "lower" else "q"
    return f"{year:04d}-{letter}{quarter}"


def written_offset(offset: str, case: str) -> str:
    """One offset written as its source wrote it: `Z` or `z`."""
    if not isinstance(offset, str):
        raise TypeError(_NOT_TEXT)
    if offset == "Z" and case == "lower":
        return "z"
    return offset


EXACTLY_ZERO: "tuple[int, tuple[str, ...], int]" = (0, (), 0)

_ASCII_ZERO = ord("0")


def _exact_digits(text: str) -> "tuple[int, tuple[str, ...], int]":
    """The canonical triple of a spelling ALREADY READ AS A NUMBER.

    Asked only about text the reader of record has classified as a
    number this format can hold, which is what lets the scan below be
    arithmetic over the characters rather than a second opinion about
    what the cell is: nothing here decides whether a spelling is a
    number, so nothing here can disagree with the answer already given.

    Guarantees: accepts text the reader has accepted; returns the
    canonical triple denoting exactly that number; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    body = trimmed(text)
    negative = False
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        # Accounting parentheses mean negative, and the reader has
        # already refused a sign inside them, so nothing can say
        # "negative" twice here.
        negative = True
        body = trimmed(body[1 : len(body) - 1])
    body = _minus_written_first(body)
    if body[:1] == "-":
        negative = True
        body = body[1:]
    elif body[:1] == "+":
        body = body[1:]
    # One pass over the characters. The digits are collected in order
    # with the leading zeros left out, the decimal places are counted,
    # and the exponent is added up after the `e`. A thousands separator
    # is none of those things and contributes nothing to the value, so
    # it falls through every branch, which is exactly right.
    digits: list[str] = []
    places = 0
    after_point = False
    in_exponent = False
    exponent_negative = False
    magnitude = 0
    for character in body:
        if in_exponent:
            if character == "-":
                exponent_negative = True
            elif "0" <= character <= "9" and len(digits):
                # The exponent is added up only while a digit that is
                # not a leading zero has been seen. That keeps `0e`
                # followed by a thousand nines cheap -- such a spelling
                # is zero whatever its exponent says -- and it is why
                # the magnitude below stays small: a spelling this
                # format can hold, whose digits are not all zeros, has
                # an exponent within a few hundred of the number of
                # digits written.
                magnitude = magnitude * 10 + (ord(character) - _ASCII_ZERO)
        elif "0" <= character <= "9":
            if after_point:
                places = places + 1
            if character != "0" or len(digits):
                digits += [character]
        elif character == ".":
            after_point = True
        elif character == "e" or character == "E":
            in_exponent = True
    if not len(digits):
        return EXACTLY_ZERO
    if exponent_negative:
        power = -places - magnitude
    else:
        power = -places + magnitude
    kept = len(digits)
    while kept > 0 and digits[kept - 1] == "0":
        kept = kept - 1
        power = power + 1
    return (-1 if negative else 1, tuple(digits[:kept]), power)


def exact_of_accepted_number(
    text: str,
) -> "tuple[int, tuple[str, ...], int]":
    """The same triple, for text the reader has ALREADY accepted.

    The entry point below classifies first, which is right for a caller
    holding an arbitrary spelling. A caller that has just asked
    `classify_number` itself and got NUMBER would be paying for that
    answer twice, and one such caller reads every cell of every
    column -- so the two doors are both here rather than one of them
    being a private name somebody reaches around.

    Guarantees: accepts text the reader has accepted; returns the
    canonical triple denoting exactly that number; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return _exact_digits(text)


def exact_of_spelling(text: str) -> "tuple[int, tuple[str, ...], int] | None":
    """The exact number a spelling denotes, or None when it denotes none.

    THE RULE OF RECORD FOR "ARE THESE TWO SPELLINGS ONE NUMBER", and it
    lives here because every module imports this one. It decides FIRST,
    through `classify_number`, whether the text is a number this format
    can hold: nothing is exact about a spelling the rest of the tool
    refuses, and asking that question a second way is how two parts of
    one program come to disagree about what a value is.

    Two texts give equal triples exactly when they denote the same
    number, and unequal triples exactly when they denote different
    numbers, HOWEVER CLOSE the binary64 values they round to. That is
    the whole point: `-999` and `-999.00000000000001` are two numbers a
    person can tell apart, and a comparison made after rounding calls
    them one.

    Guarantees: accepts any text; returns the canonical triple or None;
    raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if classify_number(text) != NUMBER:
        return None
    return _exact_digits(text)


def token_count(text: str) -> int:
    """Count whitespace-separated words in ``text``.

    Guarantees: accepts text; returns a count of zero or more; raises
    TypeError if handed anything that is not a string instance. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return len(text.split())


# What a cell's sign is, when the text alone settles it. A value too
# large or too small for this format to hold still has a visible sign,
# and that sign is enough to rule out a column of counts (review items
# P1-R4-F2 and P1-R5-F2). "unknown" is a real answer, never guessed at.
SIGN_NEGATIVE = "negative"
SIGN_ZERO = "zero"
SIGN_POSITIVE = "positive"
SIGN_UNKNOWN = "unknown"

# Whether a cell is a whole number, when the text alone settles it. A
# number too LARGE to hold is whole -- its decimal point sits beyond
# every digit it has. A number too SMALL to hold lies strictly between
# zero and one, so it is a fraction. Neither fact needs the value.
WHOLE_YES = "whole"
WHOLE_NO = "fraction"
WHOLE_UNKNOWN = "unknown"

# The named classes a missing cell is counted under. They are
# synthtwin's own words: not one of them carries anything from the
# user's table, which is what lets them appear on a column whose values
# are never published (review items P1-R1-F10 and P1-R1-F17).
MISSING_BLANK = "(blank)"
MISSING_TEXT_CODE = "(text-code)"
MISSING_NUMERIC_SENTINEL = "(numeric-sentinel)"
MISSING_DATE_SENTINEL = "(date-sentinel)"
MISSING_DECLARED = "(declared-missing)"
MISSING_WITHHELD = "(withheld)"

# In code-point order, which is the order the contract enumerates them
# in and the order every total walk over them takes.
MISSING_CLASSES = (
    MISSING_BLANK,
    MISSING_DATE_SENTINEL,
    MISSING_DECLARED,
    MISSING_NUMERIC_SENTINEL,
    MISSING_TEXT_CODE,
    MISSING_WITHHELD,
)

# THE SMALLEST GROUP A COUNT OF VALUES AT MIDNIGHT MAY NAME, on either
# side of itself, whatever the run's own smallest group size is
# (landing 2b.6; the owner's twin definition, clause 3).
#
# One is not a group. A count of one names the one person who holds the
# value, and a count leaving exactly one off midnight names the one
# person who does not -- and at the then default smallest group size of one
# both used to be published. Measured on 400 moments a day apart at
# noon, described once as they stood and once with a single row moved to
# midnight: the two descriptions differed in `n_at_midnight: 0 -> 1` and
# in nothing else anywhere, so a reader holding the other 399 values
# read that row's time of day off the difference.
#
# It lives here because the producer, the loader and the document guard
# each hold the rule to the same number, and a floor written out three
# times is a floor that disagrees with itself. The counts stage 3 raises
# for the older facts raise past this one; this is the floor below which
# no run may go.
MIDNIGHT_DISCLOSURE_FLOOR = 2


def _tally_add(tally: "dict[str, int]", name: str, count: int) -> None:
    """Add a count under a name, opening the name where it is new."""
    if name in tally:
        tally[name] = tally[name] + count
    else:
        tally[name] = count


def width_is_value_bound(name: str) -> bool:
    """Whether a width word is one only a cell's VALUE lets it show (P4-D139).

    The four one-field words: a date is counted under one only where its
    other field is ten or more, so how many a column holds is a fact
    about its dates rather than about how it wrote them.
    """
    return name in FIELD_WIDTH_STYLES_FIRST or name in FIELD_WIDTH_STYLES_SECOND


def name_is_value_bound(name: str) -> bool:
    """Whether a month-name style is one only a name of May shows (P4-D139)."""
    return _name_parts(name)[1] == NAME_LENGTH_EITHER


def folded_width_tally(tally: "dict[str, int]") -> "dict[str, int]":
    """A tally of widths with each one-field count joined to a joint word.

    A CELL THAT SHOWS ONE FIELD IS CONSISTENT WITH TWO JOINT WORDS, and
    it goes to whichever of them the column's own cells showing both
    fields wrote more often -- vocabulary order on a tie -- so that a
    column writing `m/dd/yyyy` counts `5/17/2024` and `12/05/2024` under
    the `second-padded` its `5/04/2024` cells wrote. A one-field count
    with no joint word agreeing with it stays under its own word.

    WHY (plan P4-D139; skeptic of the review of 158c811, items 2 and
    3). Counted apart, the one-field classes put a floor on how many of a
    twin's dates happen to fall past the ninth of a month or in October
    to December: 150 dates written `m/d/yyyy` at a smallest group of
    eleven published `second-field-unpadded` at 14, and the twin whose
    dates held fewer than eleven such cells failed its own check.

    Guarantees: accepts a raw tally of width words; returns a tally over
    the same total with keys in sorted order. Determinism: a function of
    the tally. Raises nothing. No I/O of any kind.
    """
    folded: "dict[str, int]" = {}
    for name in sorted(tally):
        if not width_is_value_bound(name):
            _tally_add(folded, name, tally[name])
    for name in sorted(tally):
        if not width_is_value_bound(name):
            continue
        which = 1 if name in FIELD_WIDTH_STYLES_FIRST else 2
        padded = name == WIDTH_FIRST_FIELD_PADDED or name == WIDTH_SECOND_FIELD_PADDED
        best = ""
        for joint in FIELD_WIDTH_STYLES_BOTH:
            if joint not in tally:
                continue
            if pair_widths(joint)[which - 1] != padded:
                continue
            if not best or tally[joint] > tally[best]:
                best = joint
        _tally_add(folded, best if best else name, tally[name])
    return {name: folded[name] for name in sorted(folded)}


def folded_name_tally(tally: "dict[str, int]") -> "dict[str, int]":
    """A tally of month-name styles with each name of May joined to a length.

    A NAME OF MAY IS WRITTEN THE SAME AT EITHER LENGTH, so a cell of May
    goes to the style of the same case, mark and comma that the column's
    other cells wrote more often -- the abbreviated one on a tie -- and
    stays under its `either` word only where no other cell wrote that
    case, mark and comma at all (plan P4-D139).

    WHY (skeptic of the review of 158c811, finding 2). Counted apart, one
    `15-MAY-2023` among 269 `DD-MON-YYYY` dates was a count of one, the
    disclosure rule withheld the whole census for it, and the twin was
    written `20 Jan 2022`: `%d-%b-%Y` read 269 of 269 twin cells on
    158c811 and none after it.

    Guarantees: accepts a raw tally of style words; returns a tally over
    the same total with keys in sorted order. Determinism: a function of
    the tally. Raises nothing. No I/O of any kind.
    """
    folded: "dict[str, int]" = {}
    for name in sorted(tally):
        if not name_is_value_bound(name):
            _tally_add(folded, name, tally[name])
    for name in sorted(tally):
        if not name_is_value_bound(name):
            continue
        case, _length, mark, comma = _name_parts(name)
        best = ""
        for length in NAME_LENGTHS:
            sibling = f"{case}-{length}-{mark}-{comma}"
            if sibling not in tally:
                continue
            if not best or tally[sibling] > tally[best]:
                best = sibling
        _tally_add(folded, best if best else name, tally[name])
    return {name: folded[name] for name in sorted(folded)}


def disclosed_census(
    counts: "dict[str, int]", population: int, floor: int
) -> "dict[str, int]":
    """A tally of written forms, cut to what the disclosure rule allows.

    THE CENSUSES OF HOW A COLUMN'S DATES WERE WRITTEN (plan P4-D131) ask
    the ONE disclosure rule, `census_nameable`, with its line
    `census_floor`, and add one thing of their own: NOTHING IS POOLED. A
    census names a handful of forms, and a pool beside them is the count
    of whichever forms are left: where one form is left the pool IS that
    form's count. Measured on 400 moments at noon with one lower-case
    `z`: at a floor of eleven the census read `{"upper": 399,
    "(withheld)": 1}`, which names the one row as plainly as `{"lower":
    1, "upper": 399}` did. `population` is the total the document already
    publishes for the cells the census counts over, so what the named
    counts leave of it is a count a reader can subtract.

    (Written once at the merge of the date and number repairs: the date
    repair had stated the same rule a second time, as `census_discloses`
    and `disclosure_line`, and two statements of one rule are two things
    that can part.)

    Every form counted at the line or above is named, a form below it is
    left out with no pool, and the whole census is withheld -- published
    `{}` -- where what is left would not disclose. `{}` is also what a
    column whose dates cannot show the convention publishes, so no reader
    can tell a withheld census from an empty one by its form.

    Guarantees: accepts the full tally, the published total it counts
    over and the run's smallest group size; returns a census with no
    `(withheld)` key for which `census_nameable` over that total holds,
    keys in sorted order. Determinism: a function of the three. Raises
    nothing. No I/O of any kind.
    """
    line = census_floor(floor)
    named: "dict[str, int]" = {}
    printed: "list[int]" = []
    for name in sorted(counts):
        if name != MISSING_WITHHELD and counts[name] >= line:
            named[name] = counts[name]
            printed += [counts[name]]
    if not census_nameable(printed, [population], floor):
        return {}
    return named


def census_pools(population: int, floor: int, names: int) -> bool:
    """Whether a census none of whose names reaches the line may be one pool.

    THE ONE STATEMENT, read by the producer through `absorbed_census`, by
    the loader (contract D12 and P6) and by the checker, of where the
    older spelling censuses hold their whole count back (plan P4-D222;
    stage 2 closed by the owner rulings of 2026-09-17).

    A POOL SAYS EVERY NAME WAS WRITTEN BY FEWER CELLS THAN THE LINE. On an
    open vocabulary -- the offsets and the widths, ``names`` nought -- that
    names nobody. On a CLOSED one -- three marks between day and clock,
    one on a slashed stamp, six forms of a number -- a pool over more
    cells than ``names - 1`` names can hold below the line tells a reader
    that EVERY name was written by at least one cell: the state nought
    reaches is told apart from the state a below-floor count reaches.
    Measured on the branch this repairs: 7, +8, 09, 1.5e3 and 2.5E3 among
    995 prices at a floor of one published a pool of five beside the
    decimals, each form exactly one cell. So a closed census over more
    than ``(names - 1) * (line - 1)`` cells is never a pool: above
    ``names * (line - 1)`` some name reaches the line, and in the band
    between, where none may, `absorbed_census` writes the vocabulary's
    default name for the whole population instead. A population below the
    line is always a pool, whatever the vocabulary.

    Guarantees: accepts the population, the settings floor and the size
    of the closed vocabulary (nought for an open one); returns a bool.
    Determinism: a fixed function of the three. Raises nothing. No I/O.
    """
    line = census_floor(floor)
    if population < line or names < 1:
        return True
    return population <= (names - 1) * (line - 1)


def absorbed_census(
    counts: "dict[str, int]",
    population: int,
    floor: int,
    names: int,
    default: str = "",
) -> "dict[str, int]":
    """A tally of marks, offsets, forms or widths, as the disclosure rule allows.

    THE OLDER SPELLING CENSUSES -- `utc_offsets`, `datetime_separators`,
    `numeric_styles`, `fraction_widths`, `pad_widths` and `field_widths`
    -- ask the ONE disclosure rule, `census_nameable` with its line
    `census_floor` (plans P4-D220, P4-D221 and P4-D222; stage 2 closed by
    the owner rulings of 2026-09-17). Until P4-D220 each named a count
    where it reached the settings floor and pooled the rest under
    `(withheld)`, so at the then default floor of one 400 moments with one `t`
    published `{"lower_t": 1, "upper_t": 399}` and at a floor of eleven
    `{"upper_t": 399, "(withheld)": 1}`: both name the row.

    A COUNT BELOW THE LINE IS COUNTED INTO THE COMMONEST NAMED COUNT
    (plan P4-D222), as ruling 4 of 2026-09-17 counts missing-value words
    below a raised floor as absent: the description is the description
    of the table with its rare spellings written the way most of its
    cells were, so the table passes its own description and its twin
    writes the column's own spelling. The pool this replaces (P4-D220,
    P4-D221) could not stand beside a named count without naming the
    rows it held, so a pool below the line took in the commonest named
    count as well -- and one `T` among 5,000 space-separated moments, one
    `Z` among offsets, or one `120` among 999 prices pooled the whole
    census, and the twin wrote `T` on 4,998 rows, no offset on half the
    column and prices at fifteen places. Nothing is pooled beside a named
    count now, so no printed count and no count left by subtraction from
    the population is below the line, and a name below the line is never
    told apart from a name no cell wrote.

    WHERE NO NAME REACHES THE LINE the census is one pool of the
    population the block already prints -- except on a closed vocabulary
    where `census_pools` refuses the pool, and there the whole population
    is counted under the COMMONEST NAME THE CELLS WROTE, ties to the
    first in sorted order, exactly as a rare count is counted into the
    commonest named one above. ``default``, the name the caller gives
    for the vocabulary, is written only where no cell wrote any name at
    all, which a population above nought cannot reach.

    IT WAS ``default`` OUTRIGHT UNTIL PLAN P4-D242, and that published a
    name no cell of the column wore: twenty-four moments written twelve
    with a space and twelve with a lower-case `t`, at a floor of eleven,
    published `{"upper_t": 24}`, and the twin wrote twenty-four `T`. The
    fidelity that is lost where no spelling clears the line is ruling
    6's own cost and stands; naming a spelling the column never used is
    not, because the description is the description of the table with
    its rare spellings written the way most of its cells were, and
    `upper_t` was not one of them.

    Ties for the commonest count go to the first name in sorted order,
    and the name that took the rest in is always the largest printed
    count: nothing else can grow.

    Guarantees: accepts the full tally (no `(withheld)` key), the
    published total it covers, the settings floor, the size of the
    closed vocabulary (nought for an open one) and its default name;
    returns `{}` for no population, a single `(withheld)` pool or the
    single commonest name the cells wrote where no count reaches the
    line, and otherwise the names at the line or above, keys in sorted
    order, summing to the population. Determinism: a function of the five. Raises nothing. No
    I/O of any kind.
    """
    if population <= 0:
        return {}
    line = census_floor(floor)
    named: "dict[str, int]" = {}
    commonest = ""
    total = 0
    for name in sorted(counts):
        if name == MISSING_WITHHELD or counts[name] < line:
            continue
        named[name] = counts[name]
        total = total + counts[name]
        if not commonest or counts[name] > named[commonest]:
            commonest = name
    if not commonest:
        if not census_pools(population, floor, names):
            # ...AND THE NAME IT TAKES IS ONE THE CELLS WROTE (plan
            # P4-D242). The vocabulary's own default name stood here and
            # published a name NO CELL of the column wore: twenty-four
            # moments written twelve with a space and twelve with a
            # lower-case `t`, at a floor of eleven, published
            # `{"upper_t": 24}`. Ruling 6 counts a rare spelling into
            # the column's COMMONEST spelling, and where no spelling
            # reaches the line the commonest is still one of them.
            written = ""
            for name in sorted(counts):
                if name == MISSING_WITHHELD:
                    continue
                if not written or counts[name] > counts[written]:
                    written = name
            if written:
                return {written: population}
            if default:
                return {default: population}
        return {MISSING_WITHHELD: population}
    named[commonest] = named[commonest] + population - total
    return named


def absorbed_room(census: "dict[str, int]", floor: int) -> "tuple[str, int]":
    """Which name of a published census took rare counts in, and how many at most.

    `absorbed_census` read from the other side (plan P4-D222), so that the
    producer reads a value at the offset its rare one was counted into,
    the checker bounds the cells a width census counts at a width it does
    not name, and the generator knows which form a cell no named form can
    write is owed from (plan P4-D235), without a second statement of the
    rule. The name is the largest count, the first in sorted order on a
    tie. What it took in is at most its count less the line -- it was
    named before it took anything -- and less the next largest count,
    which it was no smaller than.

    IT IS ASKED OF A CLOSED VOCABULARY TOO. It was written for the open
    ones, the offsets and the widths; the six forms of a number are
    closed, and the bound holds there unchanged, because a name below
    the line is counted into the commonest whichever kind of vocabulary
    it belongs to. Where the census is the vocabulary's DEFAULT name over
    the whole population -- the band `census_pools` refuses a pool in --
    that name is the commonest and the bound is its count less the line,
    which is what it can take in there as well.

    Guarantees: accepts a published census and the settings floor; returns
    `("", 0)` for an empty census or a pool, and otherwise the name and a
    whole number of at least nought. Determinism: a fixed function of the
    two. Raises nothing. No I/O of any kind.
    """
    line = census_floor(floor)
    commonest = ""
    for name in sorted(census):
        if name == MISSING_WITHHELD:
            return "", 0
        if not commonest or census[name] > census[commonest]:
            commonest = name
    if not commonest:
        return "", 0
    room = census[commonest] - line
    for name in sorted(census):
        if name != commonest:
            room = min(room, census[commonest] - census[name])
    return commonest, max(room, 0)


# How finely a datetime column states its time of day.
PRECISION_QUARTER = "quarter"
PRECISION_MONTH = "month"
PRECISION_DATE = "date"
PRECISION_MINUTE = "minute"
PRECISION_SECOND = "second"
PRECISION_SUBSECOND = "subsecond"

# Finest first: a column is described by the finest precision any of its
# values carries, because that is the precision the twin must be able to
# write.
PRECISION_ORDER = (
    PRECISION_SUBSECOND,
    PRECISION_SECOND,
    PRECISION_MINUTE,
    PRECISION_DATE,
    # A MONTH IS COARSER THAN A DAY AND FINER THAN A QUARTER, so it
    # sits between them: three months make a quarter and a month holds
    # twenty-eight days or more (plan P4-D4.3 item 2).
    PRECISION_MONTH,
    PRECISION_QUARTER,
)


def is_digit_text(text: str) -> bool:
    """True when ``text`` is one or more ASCII digits and nothing else.

    Guarantees: accepts text; returns a truth value; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return _all_ascii_digits(text)


def is_code_text(text: str) -> bool:
    """True when every character of ``text`` belongs to the code alphabet.

    The code alphabet is ASCII letters, ASCII digits, the hyphen and the
    underscore -- and nothing else. It is the positive evidence the
    identifier rule needs: a currency amount carries a currency sign and
    a decimal point, a percentage carries a percent sign, a time of day
    carries a colon, and none of those is a record number. Values
    outside ASCII are refused here on purpose; such a column becomes
    free text, which withholds its values just as an identifier does
    (review item P1-R1-F8).

    Guarantees: accepts text; returns a truth value; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text:
        return False
    for character in text:
        if "0" <= character <= "9":
            continue
        if "a" <= character <= "z":
            continue
        if "A" <= character <= "Z":
            continue
        if character == "-" or character == "_":
            continue
        return False
    return True


def overflowed(text: str) -> bool:
    """True when ``text`` is a number too LARGE for this format to hold.

    Distinguishes the two ways `number_out_of_range` can be true. A huge
    magnitude is a whole number; a tiny one is a fraction between zero
    and one. Telling them apart is what stops `1e-999` being published
    as a whole-number count (review item P1-R5-F2).

    Guarantees: accepts text; returns a truth value; raises TypeError if
    handed anything that is not a string instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    body = text.strip()
    if not body:
        return False
    if body[0] == "(" and body[len(body) - 1] == ")":
        body = _minus_written_first(trimmed(body[1 : len(body) - 1]))
        if body and (body[0] == "+" or body[0] == "-"):
            return False
    else:
        body = _minus_written_first(body)
    ungrouped = _without_group_separators(body)
    if ungrouped is None:
        return False
    if not _plain_number_shape(ungrouped):
        return False
    value = float(ungrouped)
    return value == float("inf") or value == float("-inf")


def numeric_sign(text: str) -> str:
    """The sign of a numeric-looking cell, from the text alone.

    Returns SIGN_NEGATIVE, SIGN_ZERO, SIGN_POSITIVE, or SIGN_UNKNOWN.
    An out-of-range value keeps its sign: `-1e999` and `(1e999)` are
    both visibly negative even though neither can be held, and that is
    enough to rule out a column of counts. Contradictory notation and
    ordinary text are SIGN_UNKNOWN, never guessed at.

    Guarantees: accepts text; returns one of the four names above;
    raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    kind = classify_number(text)
    if kind == NOT_A_NUMBER or kind == NUMBER_CONTRADICTORY:
        return SIGN_UNKNOWN
    body = text.strip()
    negative = False
    if body[0] == "(" and body[len(body) - 1] == ")":
        negative = True
        body = trimmed(body[1 : len(body) - 1])
    body = _minus_written_first(body)
    if body and body[0] == "-":
        negative = True
        body = body[1:]
    elif body and body[0] == "+":
        body = body[1:]
    ungrouped = _without_group_separators(body)
    if ungrouped is None:
        return SIGN_UNKNOWN
    if not _mantissa_has_nonzero_digit(ungrouped):
        return SIGN_ZERO
    if negative:
        return SIGN_NEGATIVE
    return SIGN_POSITIVE


def numeric_whole(text: str) -> str:
    """Whether a numeric-looking cell is a whole number, from the text.

    Returns WHOLE_YES, WHOLE_NO, or WHOLE_UNKNOWN. A value this format
    can hold is decided by the value; a value too large to hold is
    whole; a value too small to hold is a fraction strictly between zero
    and one; contradictory notation and ordinary text are unknown.

    Guarantees: accepts text; returns one of the three names above;
    raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    kind = classify_number(text)
    if kind == NUMBER:
        value = parse_number(text)
        if value is None:
            return WHOLE_UNKNOWN
        if is_whole_number(value):
            return WHOLE_YES
        return WHOLE_NO
    if kind == NUMBER_OUT_OF_RANGE:
        if overflowed(text):
            return WHOLE_YES
        return WHOLE_NO
    return WHOLE_UNKNOWN


def days_from_civil(year: int, month: int, day: int) -> int:
    """Days from a fixed epoch to a proleptic-Gregorian calendar date.

    Whole-number arithmetic only, so the answer is exact and identical
    on every machine. This is what lets two datetimes written in
    different UTC offsets be compared as the instants they name rather
    than as the wall-clock text they happen to carry. The leap rule is
    the Gregorian one: a year divisible by four is a leap year, except a
    century that is not divisible by four hundred.

    Guarantees: accepts three whole numbers naming a calendar date;
    returns a whole number of days, which is negative before the epoch;
    raises nothing for whole-number input, and does not check that the
    date exists in the calendar -- `valid_date` is where that is asked.
    No I/O of any kind.

    It is PUBLIC because the generation method requires exactly this
    function and its inverse below, and names them: the twin's dates are
    built in the same ordinal space the profile's were read in, so the
    two halves of the product cannot drift apart on a calendar rule.
    """
    shifted = year
    if month <= 2:
        shifted = year - 1
    era = shifted // 400
    year_of_era = shifted - era * 400
    if month > 2:
        day_of_year = (153 * (month - 3) + 2) // 5 + day - 1
    else:
        day_of_year = (153 * (month + 9) + 2) // 5 + day - 1
    day_of_era = (
        year_of_era * 365 + year_of_era // 4 - year_of_era // 100 + day_of_year
    )
    return era * 146097 + day_of_era - 719468


def civil_from_days(days: int) -> "tuple[int, int, int]":
    """The calendar date a whole number of days from the epoch names.

    Guarantees: accepts a whole number of days, before or after the
    epoch; returns the year, month and day it names; raises nothing for
    whole-number input. No I/O of any kind. It is public for the reason
    `days_from_civil` above is.

    The exact inverse of `days_from_civil`, in whole-number arithmetic
    only. It exists so that a column mixing UTC offsets can PUBLISH the
    same quantity it was ORDERED by: without it the profile sorted by
    the instant and then wrote out the local wall clock, so `earliest`
    could read later than `latest` and the eleven date rungs could run
    backwards.
    """
    shifted = days + 719468
    era = shifted // 146097
    day_of_era = shifted - era * 146097
    year_of_era = (
        day_of_era
        - day_of_era // 1460
        + day_of_era // 36524
        - day_of_era // 146096
    ) // 365
    year = year_of_era + era * 400
    day_of_year = day_of_era - (
        365 * year_of_era + year_of_era // 4 - year_of_era // 100
    )
    month_index = (5 * day_of_year + 2) // 153
    day = day_of_year - (153 * month_index + 2) // 5 + 1
    month = month_index + 3
    if month_index >= 10:
        month = month_index - 9
    if month <= 2:
        year = year + 1
    return year, month, day


def utc_canonical(canonical: str, offset: str) -> "str | None":
    """``canonical`` rewritten as the same instant read at UTC.

    Returns None when the value names no instant (a quarter) or when the
    instant would fall outside the four-digit years the canonical form
    can spell.

    Guarantees: accepts two strings; returns text or None; raises
    TypeError if handed anything that is not a string instance. Whole-
    number arithmetic throughout, so the answer is identical on every
    machine. No I/O of any kind.
    """
    if not isinstance(canonical, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(offset, str):
        raise TypeError(_NOT_TEXT)
    seconds = instant_key(canonical, offset)
    if seconds is None:
        return None
    days = seconds // 86400
    rest = seconds - days * 86400
    year, month, day = civil_from_days(days)
    if year < 1 or year > 9999:
        return None
    if len(canonical) < 19:
        return f"{year:04d}-{month:02d}-{day:02d}"
    hours = rest // 3600
    minutes = (rest - hours * 3600) // 60
    return (
        f"{year:04d}-{month:02d}-{day:02d} "
        f"{hours:02d}:{minutes:02d}:{rest - hours * 3600 - minutes * 60:02d}"
    )


def instant_key(canonical: str, offset: str) -> "int | None":
    """The instant a canonical datetime names, in whole seconds.

    The UTC offset is subtracted, so `2024-01-01 00:30:00+14:00` sorts
    BEFORE `2023-12-31 23:45:00-12:00`, which is the order in which the
    two moments actually happened. Sorting the local wall-clock text
    reported the opposite (review item P1-R1-F9).

    Returns None for a canonical form that names no instant -- a
    quarter, above all.

    Guarantees: accepts two strings; returns a whole number or None;
    raises TypeError if handed anything that is not a string instance.
    No I/O of any kind.
    """
    if not isinstance(canonical, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(offset, str):
        raise TypeError(_NOT_TEXT)
    if len(canonical) < 10:
        return None
    year = _digits_at(canonical, 0, 4)
    month = _digits_at(canonical, 5, 2)
    day = _digits_at(canonical, 8, 2)
    if year is None or month is None or day is None:
        return None
    seconds = days_from_civil(int(year), int(month), int(day)) * 86400
    if len(canonical) >= 19:
        hours = _digits_at(canonical, 11, 2)
        minutes = _digits_at(canonical, 14, 2)
        rest = _digits_at(canonical, 17, 2)
        if hours is None or minutes is None or rest is None:
            return None
        seconds = seconds + int(hours) * 3600 + int(minutes) * 60 + int(rest)
    if not offset or offset == "Z":
        return seconds
    if len(offset) != 6:
        return None
    hours = _digits_at(offset, 1, 2)
    minutes = _digits_at(offset, 4, 2)
    if hours is None or minutes is None:
        return None
    shift = int(hours) * 3600 + int(minutes) * 60
    if offset[0] == "-":
        return seconds + shift
    return seconds - shift


def _clock_of(text: str, format_name: str) -> "str | None":
    """The time-of-day part of an iso-datetime cell, offset removed.

    THE JOINT READING IS ANSWERED CELL BY CELL. Under `iso-mixed` some
    cells carry a time of day and some are whole dates, so the question
    is asked of the cell rather than of the column: a whole date is
    shorter than the guard below and answers None, which is the same
    answer it gives under any date-only form.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    body = text.strip()
    if format_name in SLASHED_STAMPS:
        # THE SLASHED STAMPS ANSWER FROM THEIR OWN TEXT. Their date
        # half is not ten characters wide, so the ISO cut below finds
        # nothing; the clock is what stands after the one space, and it
        # is the time-of-day role's own two forms, so the same answer
        # comes back here as the reader accepted.
        if parse_datetime(text, format_name) is None:
            return None
        mark = 0
        place = 0
        for character in body:
            if character == " ":
                mark = place
            place = place + 1
        if mark < 1:
            return None
        return body[mark + 1 :]
    if format_name != "iso-datetime" and format_name != "iso-mixed":
        return None
    if len(body) < 16:
        return None
    split = _split_offset(body[11:])
    if split is None:
        return None
    return split[0]


def datetime_precision(text: str, format_name: str) -> str:
    """How finely one datetime cell states its time of day.

    A profile that says only "datetime" cannot tell a twin whether to
    write whole minutes or thousandths of a second, and the earlier
    revision threw the fractional part away entirely (review item
    P1-R1-F9).

    Guarantees: accepts two strings; returns one of the PRECISION_
    names; raises TypeError if handed anything that is not a string
    instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    if format_name == "year-quarter":
        return PRECISION_QUARTER
    if format_name == "iso-month":
        return PRECISION_MONTH
    clock = _clock_of(text, format_name)
    if clock is None:
        return PRECISION_DATE
    if len(clock) < 8 or clock[5] != ":":
        return PRECISION_MINUTE
    if len(clock) > 9 and clock[8] == ".":
        return PRECISION_SUBSECOND
    return PRECISION_SECOND


def subsecond_digits(text: str, format_name: str) -> int:
    """How many digits of a second one datetime cell writes.

    Guarantees: accepts two strings; returns zero or more; raises
    TypeError if handed anything that is not a string instance. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    clock = _clock_of(text, format_name)
    if clock is None:
        return 0
    if len(clock) <= 9 or clock[8] != ".":
        return 0
    return len(clock) - 9


# THE MARK BETWEEN A MOMENT'S DAY AND ITS CLOCK (stage 2, plan P4-D39).
# `parse_datetime` accepts three and returns the canonical form, which
# discards which one the cell wore; these are the names the description
# publishes them under. Names and not the characters, as `numeric_styles`
# names its styles: a key that is a single space is a key nobody can see.
# In sorted order, which is the order the generator's rotation breaks a
# tie in.
SEPARATOR_LOWER_T = "lower_t"
SEPARATOR_SPACE = "space"
SEPARATOR_UPPER_T = "upper_t"
DATETIME_SEPARATORS = (SEPARATOR_LOWER_T, SEPARATOR_SPACE, SEPARATOR_UPPER_T)
SEPARATOR_MARKS = {
    SEPARATOR_LOWER_T: "t",
    SEPARATOR_SPACE: " ",
    SEPARATOR_UPPER_T: "T",
}


def separator_names(format_name: str) -> int:
    """How many marks between day and clock a reading can write (P4-D222).

    Three, and one -- a space -- on the slashed stamps, whose clock stands
    after one space. The size of the closed vocabulary
    `census_pools` reads for the census of marks; the loader asks it
    with the same answer. Raises nothing. No I/O of any kind.
    """
    if format_name in SLASHED_STAMPS:
        return 1
    return len(DATETIME_SEPARATORS)


def datetime_separator(text: str, format_name: str) -> "str | None":
    """The name of the mark between a moment's day and its clock, or None.

    Only a cell that writes a clock has one. A whole-date cell of an
    `iso-mixed` column writes none, and is decided by the same reading
    `taxonomy._resolution_mix` counts it by. The two slashed members
    split their halves on exactly one space, so their mark is always
    `space`.

    Guarantees: accepts one cell and the format member it parsed under;
    returns a member of `DATETIME_SEPARATORS`, or None for a cell that
    writes no clock or does not parse. Determinism: a function of the
    two. Raises TypeError if either is not a string instance. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    if _clock_of(text, format_name) is None:
        return None
    if format_name in SLASHED_STAMPS:
        return SEPARATOR_SPACE
    if parse_datetime(text, "iso-datetime") is None:
        return None
    body = text.strip()
    mark = body[10]
    if mark == "T":
        return SEPARATOR_UPPER_T
    if mark == "t":
        return SEPARATOR_LOWER_T
    if mark == " ":
        return SEPARATOR_SPACE
    return None


def clock_at_midnight(text: str, format_name: str) -> bool:
    """Whether a parsed cell names exactly the first instant of its day.

    A cell that writes no clock names midnight of its day: that is how
    the joint ISO reading reads a whole date, and it is what a whole
    date means. The describing step asks this only of columns published
    at `datetime` resolution, so a column of dates cannot claim the
    fact through this answer. A cell that writes a clock names midnight
    only where every figure of it is a zero -- hours, minutes, any
    seconds and every fractional digit -- so `00:00:00.001` does not.

    Guarantees: accepts one cell and its format member; returns False
    for a cell that does not parse under that member. Determinism: a
    function of the two. Raises TypeError if either is not a string
    instance. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    if parse_datetime(text, format_name) is None:
        return False
    clock = _clock_of(text, format_name)
    if clock is None:
        return True
    if len(clock) < 5 or clock[0:5] != "00:00":
        return False
    rest = clock[5:]
    if len(rest) == 0:
        return True
    if len(rest) < 3 or rest[0:3] != ":00":
        return False
    fraction = rest[3:]
    place = 1
    while place < len(fraction):
        if fraction[place] != "0":
            return False
        place += 1
    return True


def looks_like_a_column_name(text: str) -> bool:
    """True when ``text`` could be a column name rather than a value.

    Used only to catch a file whose first row is data (plan P1-D3). A
    name that reads as a number is the tell-tale sign; an empty name is
    handled separately, with its own message.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return parse_number(text) is None


def _average_ranks(values: "list[float]") -> "list[float]":
    """The rank of each value, ties sharing the average of their ranks."""
    # PAIRS SORTED PLAINLY, not a sort with a key of its own: the
    # offline audit accepts no function handed to a callee it did not
    # scan, and a tuple sorts on its first member anyway.
    pairs: "list[tuple[float, int]]" = []
    for seat in range(len(values)):
        pairs += [(values[seat], seat)]
    pairs = sorted(pairs)
    ranks = [0.0 for _each in values]
    at = 0
    while at < len(pairs):
        last = at
        while last + 1 < len(pairs) and pairs[last + 1][0] == pairs[at][0]:
            last = last + 1
        shared = (at + last) / 2.0
        for seat in range(at, last + 1):
            ranks[pairs[seat][1]] = shared
        at = last + 1
    return ranks


def rank_agreement(first: "list[float]", second: "list[float]") -> float:
    """How strongly two positions of a cell move together, -1 to 1.

    Guarantees:

    - Inputs: two equally long lists of the numbers one position held,
      in row order.
    - Determinism: a fixed function of them. Nothing here reads a clock
      or a random source.
    - Errors raised: none. A position whose values are all the same has
      no ranks to agree on and answers 0.0.
    - Boundary: returns ONE number about the whole column. No value of
      any cell reaches it or leaves it.

    THE RANKS AND NOT THE VALUES, and that is the point rather than a
    convenience. What each position holds is already published exactly,
    down to the last cell, so nothing about the values is left to say.
    What is NOT published is which of them met in a row -- and rank
    agreement is exactly that and nothing else: it does not move when a
    position's own numbers change, only when the PAIRING does. So it
    adds the one fact the description was missing and repeats none it
    already carries.
    """
    if len(first) != len(second) or len(first) < 2:
        return 0.0
    left = _average_ranks(first)
    right = _average_ranks(second)
    middle = (len(left) - 1) / 2.0
    top = 0.0
    spread_left = 0.0
    spread_right = 0.0
    for seat in range(len(left)):
        away_left = left[seat] - middle
        away_right = right[seat] - middle
        top = top + away_left * away_right
        spread_left = spread_left + away_left * away_left
        spread_right = spread_right + away_right * away_right
    if spread_left <= 0.0 or spread_right <= 0.0:
        return 0.0
    return float(top / ((spread_left * spread_right) ** 0.5))



def reads_as_two_numbers(text: str) -> bool:
    """Whether this spelling denotes a DIFFERENT number under the two
    numeric grammars this tool can read a column with.

    THE ONE PLACE A PER-COLUMN READING AND A TABLE-WIDE DECLARATION
    COLLIDE (plan amendment for P4-D26; review items P4-G3-R6-F1, F2
    and F5). `--decimal-comma` names COLUMNS; `--keep-value` and
    `--missing-value` name VALUES and reach the whole table. A spelling
    whose number depends on which grammar reads it therefore means one
    thing on a declared column and another everywhere else, and the
    description has one settings block in which to record it. That is
    not a bug in any one function -- it is a fact about the two
    declarations, and it cannot be recorded truthfully.

    Most spellings are safe: `NA`, `unknown` and `-999` read the same
    way under both, because neither carries a mark the two grammars
    disagree about. `-9.99`, `1,234` and `-999,0` do not.

    Guarantees: accepts one spelling; returns whether its number
    differs between the two readings, counting "no number at all" as a
    reading of its own. Determinism: a fixed function of the text.
    Errors raised: TypeError if handed anything that is not a string.
    No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError("reads_as_two_numbers needs text")
    swapped = written_with_a_decimal_comma(text)
    if swapped == text:
        return False
    return exact_of_spelling(text) != exact_of_spelling(swapped)

# HOW CLOSE A TWIN'S RANK AGREEMENT HAS TO COME, method G12.9, kept
# HERE rather than beside either reader of it.
#
# Two places hold a twin to this number and they must never drift: the
# generation report, which measures the twin it just wrote, and the
# validator, which re-describes a file and checks it. If the report
# promised one reach while the check used another, one of them would
# call a twin sound and the other would call a file of the very same
# numbers missed -- and which of the two a person believed would depend
# on which command they happened to run.
#
# It cannot live in `generation`: the validator may not import the
# generator, so that its verdicts cannot inherit the planner's own
# defects. It cannot live in `validation` for the mirror reason. This
# module is imported by both and already owns `rank_agreement`, the
# function that computes the very quantity the window bounds, so the
# number and its meaning stay in one place.
RANK_AGREEMENT_WINDOW = 0.02

# The places a published rank agreement is written to, so the number a
# report prints and the number a re-description would find are the same
# number. `profile` rounds the published value here; anything measuring
# a twin against it has to round the same way or the two disagree at
# the edge of the window -- 0.020018 is outside a reach of 0.02 raw and
# inside it once rounded, and a fact cannot be both.
RANK_AGREEMENT_PLACES = 4


# HOW MANY BINS A HISTOGRAM OF NUMBERS HAS, and it is a fixed count on
# purpose (plan P4-D4.7, owner instruction 2026-08-26). The generator
# holds only the description, so whatever picks the bin edges has to be
# reproducible from the description alone; a rule that consulted the
# values would be a rule the generator cannot run. Thirty-two equal
# bins between the published minimum and maximum need no fact the
# description does not already carry, and a column with fewer values
# than bins simply writes fewer keys, because an empty bin has no key.
#
# WHY A HISTOGRAM AND NOT MORE RUNGS. Moments and percentiles cannot
# show two peaks: a column of two populations -- treated and untreated
# -- has the same mean, spread, skew and ladder as one smooth
# population at eleven rungs, so a twin built from those facts is
# smooth where the real column is not, and anybody plotting a
# distribution or fitting a mixture gets a different answer on the
# twin. Nothing else in the numeric block fixes that.
HISTOGRAM_BINS = 32


def histogram_bin(value: float, lowest: float, highest: float) -> int:
    """Which of the `HISTOGRAM_BINS` bins one value falls in.

    The bins are equal in width and half-open at the top -- a value on
    a shared edge belongs to the UPPER bin, the one that STARTS there
    -- except the last, which is closed so the published maximum has
    somewhere to go. A column whose values are all one number has no
    width to divide and everything falls in the first bin.

    THIS SENTENCE SAID "LOWER" UNTIL 2026-09-04 and the arithmetic
    below never did: `int(share * HISTOGRAM_BINS)` puts a value whose
    share is exactly `k / 32` in bin `k`, which is the bin that starts
    at that edge. Contract C6-31f now states the rule normatively, in
    the arithmetic's own terms, so a producer written to the document
    and this module place a boundary value in the same bin.

    THE RULE LIVES HERE because three modules must agree on it: the
    producer that counts the bins, the loader that checks the count,
    and the generator that has to land its values in them. A rule
    two of them shared and the third re-derived is a rule that comes
    apart.

    Guarantees: accepts a value and the two published ends; returns a
    bin number from zero to `HISTOGRAM_BINS - 1`. Raises nothing. No
    I/O of any kind.
    """
    # A NUMBER THIS FORMAT CANNOT HOLD HAS NO PLACE ON A SCALE. An
    # infinite end makes every division by the range a NaN, and a NaN
    # is not a bin number; a column reaching that state publishes no
    # histogram at all, and this returns the first bin so the rule is
    # TOTAL rather than raising into a caller with no answer.
    #
    # `x - x` IS THE TEST, and it is written that way because this
    # module imports nothing -- not even `math` -- and is the one place
    # the producer, the loader and the generator all read this rule
    # from. It is zero for every finite number, and NaN for an infinity
    # and for a NaN, and NaN is equal to nothing including itself.
    if value - value != 0.0:
        return 0
    if lowest - lowest != 0.0 or highest - highest != 0.0:
        return 0
    if not highest > lowest:
        return 0
    # AND THE SUBTRACTION ITSELF CAN LEAVE THE FORMAT even where both
    # ends are inside it: a column running from about -1e308 to about
    # 1e308 has finite ends and an infinite WIDTH, and dividing one
    # overflow by another gives a NaN. Every derived quantity is
    # therefore tested the same way the inputs were.
    reach = highest - lowest
    if reach - reach != 0.0 or not reach > 0.0:
        return 0
    # A VALUE OUTSIDE THE SCALE IS ANSWERED BEFORE ANY SUBTRACTION.
    # The subtraction can leave the format even where the reach does
    # not: on a scale of -1e308 to 0, a value of 1e308 makes
    # `value - lowest` an infinity, the share a NaN, and the guard
    # below answered bin ZERO for a value above the MAXIMUM. Comparing
    # against the two ends first answers those values by the same
    # clamp the arithmetic would have reached, and reaches the
    # subtraction only with a value the scale contains.
    if value <= lowest:
        return 0
    if value >= highest:
        return HISTOGRAM_BINS - 1
    share = (value - lowest) / reach
    if share - share != 0.0:
        return 0
    # THE CLAMP COMES BEFORE THE MULTIPLICATION, and it has to. A value
    # far outside a narrow scale gives a finite share that overflows
    # when it is multiplied -- `histogram_bin(1e308, -1.0, 1.0)` made
    # `share` 5e307, `share * 32` an infinity, and `int` of an infinity
    # raises, which is a crash inside a function whose contract says it
    # raises nothing. Clamping first answers the same bin the clamp
    # below would have answered and reaches the multiplication only
    # with a share this format can hold.
    if share <= 0.0:
        return 0
    if share >= 1.0:
        return HISTOGRAM_BINS - 1
    place = int(share * HISTOGRAM_BINS)
    if place < 0:
        return 0
    if place >= HISTOGRAM_BINS:
        return HISTOGRAM_BINS - 1
    return place


def scale_bin(value: float, lowest: float, highest: float) -> int:
    """The bin of a value on a TAIL block's scale, or -1 outside it.

    A tail block's bins divide the stretch between its two boundary rungs
    (contract C6-31f as amended by stage 3, plan P4-D325), and the rows
    beyond those rungs are described by the tail facts and stand in NO
    bin. The clamp of `histogram_bin` would read a tail value below the
    low boundary as bin nought, and method G6.7 would then walk it onto
    the scale: measured on a 40-value block whose bin nought was empty,
    twelve of its low ranks were dragged just above the boundary. Inside
    the scale this is `histogram_bin` exactly.

    Guarantees: accepts a value and the two boundary rungs; returns a bin
    number, or -1 for a value outside `[lowest, highest]` or a scale with
    no width. Raises nothing. No I/O of any kind.
    """
    if value - value != 0.0:
        return -1
    if lowest - lowest != 0.0 or highest - highest != 0.0:
        return -1
    if not highest > lowest:
        return -1
    if value < lowest or value > highest:
        return -1
    return histogram_bin(value, lowest, highest)


# THE FEWEST UNITS A TAIL SPANS WHATEVER THE FLOOR (stage 3, plan
# P4-D321). Two published moments over one or two cells solve for those
# cells exactly, so a tail never holds fewer than three units. Here,
# beside the bins, because the producer, the loader and the validator's
# re-description all ask it and each already imports this module.
TAIL_MINIMUM = 3


def tail_units(floor: int) -> int:
    """The fewest units each tail spans: the floor, and never below three."""
    return max(floor, TAIL_MINIMUM)


def tail_percent(count: int, units: int) -> "int | None":
    """The boundary percent of one side of a tail block (contract L4).

    The smallest whole percent `p` from 1 to 50 whose type-7 reading
    `floor((count - 1) p / 100)` leaves at least ``units`` order
    statistics strictly outside it -- so no published rung reads any of
    the outermost ``units`` values. None where no percent does, which is
    a block of fewer than `2 units + 1` values. The high side's percent
    is a hundred less the same answer.

    Guarantees: accepts the count of used values and the units the tail
    must span; returns a percent or None. Determinism: a fixed function
    of the two. Raises nothing. No I/O of any kind.
    """
    for percent in range(1, 51):
        if ((count - 1) * percent) // 100 >= units:
            return percent
    return None


def tail_rows(count: int, percent: int, side: str) -> int:
    """How many rows one tail holds (contract T3).

    Low: the positions below `h = (count - 1) percent / 100`, which are
    `ceil(h)` of them. High: the positions above it, `count - 1 -
    floor(h)`. A rung at `h` reads `floor(h)` and `ceil(h)`, and neither
    is a tail row.
    """
    steps = (count - 1) * percent
    if side == "low":
        return -((-steps) // 100)
    return count - 1 - steps // 100
