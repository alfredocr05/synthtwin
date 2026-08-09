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
)

# Numbers that are conventionally used to mean "no value". They count
# as missing only when they are also distribution outliers; the rule is
# in taxonomy.py, and every candidate's fate is reported either way.
NUMERIC_SENTINELS = (-9999.0, -999.0, 9999.0)

# The date and time formats, in the order they are tried. The first
# format that parses at least the required share of a column's values
# wins, and the profile records which one it was.
DATE_FORMATS = (
    "iso-date",
    "iso-datetime",
    "compact-date",
    "month-first-date",
    "day-first-date",
    "year-quarter",
)

_FORMAT_EXAMPLES = {
    "iso-date": "2024-03-17",
    "iso-datetime": "2024-03-17 14:05:00",
    "compact-date": "20240317",
    "month-first-date": "03/17/2024 (month first)",
    "day-first-date": "17/03/2024 (day first)",
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
    against MISSING_TEXTS after trimming and case folding. No I/O.
    """
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    return text.strip().casefold() in MISSING_TEXTS


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
    if format_name == "compact-date":
        if len(body) != 8 or not _all_ascii_digits(body):
            return None
        canonical = _canonical_date(body[0:4], body[4:6], body[6:8])
        if canonical is None:
            return None
        return canonical, ""
    if format_name == "month-first-date" or format_name == "day-first-date":
        if len(body) != 10 or body[2] != "/" or body[5] != "/":
            return None
        first = _digits_at(body, 0, 2)
        second = _digits_at(body, 3, 2)
        year = _digits_at(body, 6, 4)
        if first is None or second is None or year is None:
            return None
        if format_name == "month-first-date":
            canonical = _canonical_date(year, first, second)
        else:
            canonical = _canonical_date(year, second, first)
        if canonical is None:
            return None
        return canonical, ""
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
        return f"{year}-Q{quarter}", ""
    return None


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
MISSING_DECLARED = "(declared-missing)"
MISSING_WITHHELD = "(withheld)"

MISSING_CLASSES = (
    MISSING_BLANK,
    MISSING_DECLARED,
    MISSING_NUMERIC_SENTINEL,
    MISSING_TEXT_CODE,
    MISSING_WITHHELD,
)

# How finely a datetime column states its time of day.
PRECISION_QUARTER = "quarter"
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


def _days_from_civil(year: int, month: int, day: int) -> int:
    """Days from a fixed epoch to a proleptic-Gregorian calendar date.

    Whole-number arithmetic only, so the answer is exact and identical
    on every machine. This is what lets two datetimes written in
    different UTC offsets be compared as the instants they name rather
    than as the wall-clock text they happen to carry.
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


def _civil_from_days(days: int) -> "tuple[int, int, int]":
    """The calendar date a whole number of days from the epoch names.

    The exact inverse of `_days_from_civil`, in whole-number arithmetic
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
    year, month, day = _civil_from_days(days)
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
    seconds = _days_from_civil(int(year), int(month), int(day)) * 86400
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
    """The time-of-day part of an iso-datetime cell, offset removed."""
    if not isinstance(text, str):
        raise TypeError(_NOT_TEXT)
    if not isinstance(format_name, str):
        raise TypeError(_NOT_TEXT)
    if format_name != "iso-datetime":
        return None
    body = text.strip()
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
