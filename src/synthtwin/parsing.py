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
    "month-first-datetime",
    "day-first-datetime",
    "year-quarter",
    # LAST, AND THAT IS THE RULE RATHER THAN A PLACE IN A LIST. The
    # single-format pass runs first and its verdict stands wherever it
    # clears -- a column of ninety-nine ISO dates and one datetime cell
    # is a date column with one unparsed cell, as it is today. Only
    # where NO single format clears does the joint reading get a turn,
    # which is what putting it after every other member means.
    "iso-mixed",
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
    "month-first-datetime": "03/17/2024 14:05 (month first)",
    "day-first-datetime": "17/03/2024 14:05 (day first)",
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


def _without_group_separators(text: str) -> "str | None":
    """Remove valid thousands separators, or return None if they are not.

    A comma is accepted only where a thousands separator can appear: the
    part before the decimal point must read as groups of exactly three
    digits after a first group of one to three digits. '1,234,567.89'
    becomes '1234567.89'; '1,23' and '12,3456' are refused, because
    accepting them would turn a mistyped value into a plausible number.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if "," not in text:
        return text
    sign = ""
    body = text
    if text[0] == "+" or text[0] == "-":
        sign = text[0]
        body = text[1:]
    point = body.find(".")
    if point < 0:
        head = body
        tail = ""
    else:
        head = body[:point]
        tail = body[point:]
    if "," in tail:
        return None
    groups = head.split(",")
    if len(groups) < 2:
        return None
    if not _all_ascii_digits(groups[0]) or len(groups[0]) > 3:
        return None
    joined = groups[0]
    for group in groups[1:]:
        if not _all_ascii_digits(group) or len(group) != 3:
            return None
        joined = joined + group
    return sign + joined + tail


# The longest cell a shape form is taken of. A form is a fact about the
# WRITING of a value, and on a short cell it is a fact about a code; on
# a long one it would start to be a fact about a sentence -- word
# lengths, where the commas fall -- which is a different thing to
# publish and is not what the form is for.
SHAPE_FORM_LIMIT = 24

SHAPE_DIGIT = "9"
SHAPE_LETTER = "A"


def shape_form(text: str) -> str:
    """The shape of one cell: its figures and letters, its marks kept.

    Every ASCII digit becomes `9`, every ASCII letter becomes `A`, and
    every other character stands as itself, because the marks are the
    STRUCTURE and the letters and figures are the content. A diagnosis
    code `E11.9` has the form `A99.9`; a laboratory code `4548-4` has
    `9999-9`; a blood pressure `120/80` has `999/99`; a dispensed-drug
    code `0002-8215-01` has `9999-9999-99`.

    WHAT THIS IS FOR. A column whose values the disclosure floor holds
    back publishes nothing about them today, so its twin holds
    `group-14` -- which is not a code, is not the right length, and on
    a column of hyphenated codes even splits into two parts and reads
    as one. A form lets the twin hold something of the right shape
    without holding anything of the value: `A99.9` says a letter, two
    figures, a point and a figure, and says nothing about WHICH.

    WHAT IT DELIBERATELY WILL NOT DO. A cell longer than
    `SHAPE_FORM_LIMIT` has no form. On a note or an address the form
    would carry where the spaces and the commas fall and how long each
    word is, which is a fact about a sentence rather than about a code,
    and this census is not the place to decide whether that may be
    published. Such a cell answers the empty string and its column
    counts it among the forms it holds back.

    Guarantees: accepts any string; returns a form, or "" for a cell
    that is empty or longer than the limit. Determinism: the answer
    depends only on the text. Raises TypeError if handed anything that
    is not a string instance. Boundary: no figure and no letter of the
    cell survives into the answer -- only how many there were, and
    where the marks between them fell. No I/O of any kind.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not text or len(text) > SHAPE_FORM_LIMIT:
        return ""
    form = ""
    for character in text:
        if "0" <= character <= "9":
            form = form + SHAPE_DIGIT
        elif ("a" <= character <= "z") or ("A" <= character <= "Z"):
            form = form + SHAPE_LETTER
        else:
            form = form + character
    return form


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
            fields = fields + [current]
            current = ""
            continue
        current = current + character
    fields = fields + [current]
    head = fields[0]
    if not head or len(head) > 3 or not _all_ascii_digits(head):
        return False
    for field in fields[1:]:
        if len(field) != 3 or not _all_ascii_digits(field):
            return False
    return True


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


def parse_number(text: str) -> "float | None":
    """Read ``text`` as a number, or return None if it is not one.

    Accepted forms (plan P1-D4): a plain decimal number, optionally
    signed, optionally with an exponent; surrounding whitespace; valid
    thousands separators; and accounting parentheses for negatives, so
    '(1,234.50)' reads as -1234.5.

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
        body = body[1 : len(body) - 1].strip()
        # Parentheses mean "negative" in accounting. A sign inside them
        # is a contradiction -- '(-1)' says negative twice and '(+5)'
        # says both -- and guessing which the writer meant is how a
        # column of debts came out positive (review item P1-R2-F6). It
        # is not a number this reader will interpret.
        if body and (body[0] == "+" or body[0] == "-"):
            return None
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
    thousands separators are classified by the digits inside them. A
    comma would break a CSV row, and brackets are outside the spellings
    a twin may write, so neither could be reproduced and neither is
    counted as its own form.

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
    body = trimmed(text)
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        body = trimmed(body[1 : len(body) - 1])
    core = ""
    for character in body:
        if character != ",":
            core = core + character
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
    body = trimmed(text)
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        body = trimmed(body[1 : len(body) - 1])
    core = ""
    for character in body:
        if character != ",":
            core = core + character
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
    body = trimmed(text)
    if body[:1] == "(" and body[len(body) - 1 : len(body)] == ")":
        body = trimmed(body[1 : len(body) - 1])
    core = ""
    for character in body:
        if character != ",":
            core = core + character
    if core[:1] == "-" or core[:1] == "+":
        core = core[1:]
    width = 0
    for character in core:
        if character == ".":
            return width
        width = width + 1
    return width


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
        inner = body[1 : len(body) - 1].strip()
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
        body = body[1 : len(body) - 1].strip()
        if body and (body[0] == "+" or body[0] == "-"):
            return False
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


def _valid_date(year: int, month: int, day: int) -> bool:
    """True when the year, month and day name a real calendar date.

    The leap-year rule is the Gregorian one: a year divisible by four
    is a leap year, except a century that is not divisible by four
    hundred.
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
    if not _valid_date(int(year), int(month), int(day)):
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
                marks = marks + [place]
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
            marks = marks + [place]
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
    ):
        # A SLASHED DATE WHOSE YEAR IS TWO FIGURES (plan P4-D15). The
        # century is not in the cell, so it is decided by the pivot
        # `year_of_two_figures` fixes and named in the column's
        # remarks.
        fields = _delimited_fields(body, "/", 2)
        if fields is None:
            return None
        first, second, short = fields
        year = year_of_two_figures(short)
        if format_name == "two-digit-month-first-date":
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
        # THE YEAR IS ONE THE CALENDAR HAS. `_valid_date` refuses year
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
        body = body[1 : len(body) - 1].strip()
        if body and (body[0] == "+" or body[0] == "-"):
            return False
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
        body = body[1 : len(body) - 1].strip()
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
    date exists in the calendar -- `_valid_date` is where that is asked.
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
    if (
        format_name == "month-first-datetime"
        or format_name == "day-first-datetime"
    ):
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


def looks_like_a_column_name(text: str) -> bool:
    """True when ``text`` could be a column name rather than a value.

    Used only to catch a file whose first row is data (plan P1-D3). A
    name that reads as a number is the tell-tale sign; an empty name is
    handled separately, with its own message.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return parse_number(text) is None
