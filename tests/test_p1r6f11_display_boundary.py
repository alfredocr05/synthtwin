"""The one display boundary (review item P1-R6-F11, from P1-R4-F4).

A path or a value can carry characters a terminal obeys rather than
prints. The demonstrated failure: running the command on a missing path
containing the bytes for ``/tmp/r6-<ESC>[2J.csv`` put the raw escape
sequence on the error stream, and a terminal cleared the display instead
of showing the path.

Two separate things are checked here.

1.  THE SET. What counts as a character that instructs a display is
    defined by Unicode general category -- Cc, Cf, Zl, Zp, and the
    surrogate range, which is not text at all -- and the table in
    ``parsing`` is compared against Python's own Unicode database over
    the whole code space, in both directions. Under-covering leaves the
    next hole open; over-covering is its own defect, because a
    researcher whose column names are Greek or Arabic must read them as
    they wrote them.

2.  THE BOUNDARY. Every human-facing sink of the command -- the screen,
    the error stream, the summary file -- is fed through the two
    emitters in ``cli``, and the source of that module is read here so
    that a third way to print cannot appear unnoticed.

Every non-ASCII character in this file is written as an escape, so the
source itself stays readable and no invisible character hides in it.

These tests import ``unicodedata`` and ``ast``: the offline import
allowlist governs ``src/``, which is the tree the scanner is run over.
"""

import ast
import pathlib
import unicodedata

import pytest

import fixtures
from synthtwin import cli, parsing

# The Unicode general categories that mean "this character instructs a
# display rather than showing something of its own", plus the surrogate
# range, which is what a byte the computer could not read as text
# becomes and which can never be shown at all.
_CONTROL_CATEGORIES = frozenset({"Cc", "Cf", "Cs", "Zl", "Zp"})

# What a code point inside the table is allowed to be. "Cn" is an
# unassigned position: the table deliberately covers the reserved
# positions inside the blocks Unicode set aside for format controls, so
# that a character assigned there later is already handled.
_ALLOWED_IN_THE_TABLE = _CONTROL_CATEGORIES | frozenset({"Cn"})

_ESC = b"\x1b"
_CLEAR_THE_SCREEN = "\x1b[2J"


def _in_the_table(code: int) -> bool:
    for start, end in parsing._DISPLAY_CONTROL_RANGES:
        if start <= code <= end:
            return True
    return False


def _escaped_spelling(character: str) -> str:
    code = ord(character)
    if code < 256:
        return "\\x" + format(code, "02x")
    if code < 65536:
        return "\\u" + format(code, "04x")
    return "\\U" + format(code, "08x")


# --------------------------------------------------------------------
# 1. The set, checked against Python's own Unicode database
# --------------------------------------------------------------------


def test_p1r6f11_the_table_covers_every_unicode_display_control() -> None:
    """Nothing in Cc, Cf, Cs, Zl or Zp may be missing from the table.

    This is the check the hand-written list could not pass. It walks
    the whole code space, so a format control nobody thought of -- and
    a category that grows in a later Unicode version -- turns this red
    rather than leaving a character to reach a terminal unescaped.
    """
    missing = []
    for code in range(0x110000):
        control = unicodedata.category(chr(code)) in _CONTROL_CATEGORIES
        if control and not _in_the_table(code):
            missing.append(code)
    assert not missing, (
        "these code points instruct a display but are outside "
        "parsing._DISPLAY_CONTROL_RANGES: "
        + ", ".join(f"U+{code:04X}" for code in missing[:20])
    )


def test_p1r6f11_the_table_holds_no_ordinary_character() -> None:
    """Over-escaping is its own defect, so the table is checked both ways.

    Every code point the table covers must be a control, a format
    control, a separator, a surrogate, or a position Unicode has not
    assigned. A letter, mark, digit, punctuation mark, symbol, or space
    separator inside the table would mean ordinary text is mangled on
    its way to the screen.
    """
    wrong = []
    for start, end in parsing._DISPLAY_CONTROL_RANGES:
        for code in range(start, end + 1):
            if unicodedata.category(chr(code)) not in _ALLOWED_IN_THE_TABLE:
                wrong.append(code)
    assert not wrong, (
        "these ordinary characters sit inside "
        "parsing._DISPLAY_CONTROL_RANGES and would be escaped for no "
        "reason: " + ", ".join(f"U+{code:04X}" for code in wrong[:20])
    )


def test_p1r6f11_the_format_controls_the_old_list_missed_are_shown() -> None:
    """The four the reviewer named, and the rest of U+206A-U+206F."""
    named = ["\u061c", "\u200b", "\u2060"]
    for code in range(0x206A, 0x2070):
        named.append(chr(code))
    for character in named:
        shown = parsing.visible(character)
        assert shown != character, (
            f"U+{ord(character):04X} is a Unicode format control and must "
            f"not reach a screen as itself"
        )
        assert shown == _escaped_spelling(character)


def test_p1r6f11_the_c0_c1_and_separator_controls_are_shown() -> None:
    """The categories the earlier revision did cover, kept covered."""
    for character in ("\x00", "\x1b", "\x7f", "\x9b", "\u2028", "\u2029"):
        assert parsing.visible(character) == _escaped_spelling(character)


def test_p1r6f11_a_surrogate_is_shown_rather_than_crashing_the_print() -> None:
    """A byte the computer could not read as text is not text.

    A path holding bytes that are not valid UTF-8 arrives as lone
    surrogates. Left in place they cannot even be written back out, so
    the refusal would end as a crash with no message at all.
    """
    assert parsing.visible("\udcff") == "\\udcff"
    assert parsing.visible("a\udcffb").encode("utf-8") == b"a\\udcffb"


# --------------------------------------------------------------------
# 1b. Ordinary non-English text must pass through unchanged
# --------------------------------------------------------------------

# Letters only, no words: accented Latin, Greek, Cyrillic, CJK (Han,
# hiragana, Hangul), Arabic, Hebrew.
_ORDINARY_TEXT = (
    ("accented Latin", "\u00e9\u00fc\u00f1\u0107"),
    ("Greek", "\u0391\u03b2\u03b3"),
    ("Cyrillic", "\u0414\u0430\u044f"),
    ("CJK", "\u5b89\u3042\uc548"),
    ("Arabic", "\u0627\u0644\u0641"),
    ("Hebrew", "\u05d0\u05d1\u05d2"),
)


@pytest.mark.parametrize("script,text", _ORDINARY_TEXT)
def test_p1r6f11_ordinary_non_english_text_is_returned_unchanged(
    script: str, text: str
) -> None:
    """Letters of every script are not controls and are never escaped."""
    assert parsing.visible(text) == text, (
        f"{script} text was altered on its way to a screen; over-escaping "
        f"is its own defect"
    )
    assert parsing.visible_lines(text) == text


def test_p1r6f11_ordinary_spaces_and_marks_are_left_alone() -> None:
    """A no-break space, an ideographic space, and two variation marks.

    None of them instructs a display, and each occurs in ordinary text:
    French typography, CJK typography, and emoji.
    """
    for character in ("\u00a0", "\u3000", "\u202f", "\ufe0f", "\U000e0100"):
        assert parsing.visible(character) == character


# --------------------------------------------------------------------
# 1c. A value versus a document synthtwin composed
# --------------------------------------------------------------------


def test_p1r6f11_a_value_shows_its_line_feed_and_a_document_keeps_its_own(
) -> None:
    """The one difference between the two doors of the boundary."""
    assert parsing.visible("one\ntwo") == "one\\x0atwo"
    assert parsing.visible_lines("one\ntwo") == "one\ntwo"
    # Everything else is treated identically by both.
    assert parsing.visible_lines("one\r\x1btwo") == "one\\x0d\\x1btwo"


def test_p1r6f11_showing_text_twice_changes_nothing() -> None:
    """The boundary may be applied again at emission without harm."""
    once = parsing.visible(_CLEAR_THE_SCREEN + "\u202e\n")
    assert parsing.visible(once) == once
    assert parsing.visible_lines(once) == once


# --------------------------------------------------------------------
# 2. The boundary, at the command's own sinks, checked byte by byte
# --------------------------------------------------------------------


def _missing_path(tmp_path: pathlib.Path, name: str) -> str:
    """A path naming nothing on disk, so a refusal is what comes back."""
    return f"{tmp_path / name}"


def test_p1r6f11_a_missing_path_with_an_escape_sequence_reaches_no_terminal(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The exact example in the review: r6-<ESC>[2J.csv, not on disk.

    The refusal for a missing file is built in `errors`, which puts the
    path into the message as it stands; it reaches the screen through
    `cli`, and that is where the boundary has to hold.
    """
    named = _missing_path(tmp_path, "r6-" + _CLEAR_THE_SCREEN + ".csv")
    assert cli.main(["profile", named]) == 1
    captured = capsys.readouterr()
    assert _ESC not in captured.err.encode("utf-8", "surrogatepass")
    assert _ESC not in captured.out.encode("utf-8", "surrogatepass")
    assert "\\x1b[2J" in captured.err


def test_p1r6f11_a_missing_path_with_a_line_feed_cannot_forge_a_line(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """A refusal in the catalog is one paragraph, so it stays one line.

    A line feed inside the path would otherwise let a value write what
    reads as a sentence of synthtwin's own.
    """
    named = _missing_path(tmp_path, "r6\ndecoy.csv")
    assert cli.main(["profile", named]) == 1
    error = capsys.readouterr().err
    assert error.count("\n") == 1, (
        "a path carrying a line feed split the refusal into more than "
        f"one line: {error!r}"
    )


def test_p1r6f11_a_missing_path_with_bidi_and_format_controls_is_shown(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """Right-to-left override, zero-width space, word joiner, and more."""
    hidden = "\u202e\u200b\u2060\u061c\u206a\u2066\ufeff"
    named = _missing_path(tmp_path, "r6-" + hidden + ".csv")
    assert cli.main(["profile", named]) == 1
    error = capsys.readouterr().err
    for character in hidden:
        assert character not in error, (
            f"U+{ord(character):04X} reached the error stream as itself"
        )
        assert _escaped_spelling(character) in error


def test_p1r6f11_a_missing_path_of_non_english_letters_is_printed_as_written(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The other half: nothing ordinary may be mangled on the way out."""
    letters = "\u00e9-\u0394-\u0414-\u5b89-\u0627-\u05d0"
    named = _missing_path(tmp_path, letters + ".csv")
    assert cli.main(["profile", named]) == 1
    error = capsys.readouterr().err
    for character in letters:
        assert character in error, (
            f"U+{ord(character):04X} is an ordinary letter and must reach "
            f"the screen unchanged"
        )
        assert _escaped_spelling(character) not in error


def test_p1r6f11_a_column_name_with_an_escape_sequence_reaches_no_sink(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """The screen and the summary file are both human-facing sinks."""
    header = "reading" + _CLEAR_THE_SCREEN
    rows = [[f"{n}", "north"] for n in range(12)]
    text = fixtures.rows_to_csv([header, "region"], rows)
    table = fixtures.write(tmp_path, "clinic.csv", text)
    assert cli.main(["profile", f"{table}"]) == 0
    captured = capsys.readouterr()
    written = (tmp_path / "clinic-profile.txt").read_bytes()
    assert _ESC not in captured.out.encode("utf-8", "surrogatepass")
    assert _ESC not in written
    assert b"\\x1b[2J" in written
    # The screen and the file must still carry the same text.
    assert written.decode("utf-8") in captured.out


def test_p1r6f11_a_word_the_command_line_did_not_understand_is_shown(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """argparse copies unrecognized words out exactly as they were typed.

    That report is the one message of argparse's own that does not quote
    the value, so the words are taken back and refused here instead.
    """
    table = fixtures.write(tmp_path, "clinic.csv", "a\n1\n")
    with pytest.raises(SystemExit) as caught:
        cli.main(["profile", f"{table}", "extra" + _CLEAR_THE_SCREEN])
    assert caught.value.code == 2
    error = capsys.readouterr().err
    assert _ESC not in error.encode("utf-8", "surrogatepass")
    assert "\\x1b[2J" in error
    assert "not understood" in error
    assert "synthtwin --help" in error


def test_p1r6f11_an_option_value_the_parser_refuses_is_shown(
    capsys: pytest.CaptureFixture[str],
) -> None:
    """argparse's remaining refusals quote the value with Python's repr.

    repr shows every character Python's Unicode data calls unprintable,
    so those messages are already safe; recording it here means a later
    change to the option set cannot quietly undo that.
    """
    with pytest.raises(SystemExit) as caught:
        cli.main(["--first-row", _CLEAR_THE_SCREEN, "profile", "x.csv"])
    assert caught.value.code == 2
    error = capsys.readouterr().err
    assert _ESC not in error.encode("utf-8", "surrogatepass")


# --------------------------------------------------------------------
# 2b. The boundary is structural: the source of the module is checked
# --------------------------------------------------------------------


def _command_module_tree() -> ast.Module:
    source = pathlib.Path(f"{cli.__file__}").read_text(encoding="utf-8")
    return ast.parse(source)


def _every_print(tree: ast.Module) -> list[tuple[str, int]]:
    """(enclosing function name, line) for every call to print."""
    found: list[tuple[str, int]] = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.FunctionDef):
            continue
        for inner in ast.walk(node):
            if not isinstance(inner, ast.Call):
                continue
            target = inner.func
            if isinstance(target, ast.Name) and target.id == "print":
                found.append((node.name, inner.lineno))
    return found


def test_p1r6f11_only_the_two_emitters_print_in_the_command_module() -> None:
    """The defect that kept coming back was a sink written without the
    escaping. A sink cannot skip a boundary it cannot reach around: if
    the only calls to print live inside `_say` and `_warn`, every
    message is covered whether or not its author thought about it.
    """
    printing = _every_print(_command_module_tree())
    assert printing, "the command module must still print something"
    outside = [
        (name, line)
        for name, line in printing
        if name not in ("_say", "_warn")
    ]
    assert not outside, (
        "cli.py prints outside its two emitters, so that message skips "
        "the display boundary: "
        + ", ".join(f"{name} (line {line})" for name, line in outside)
        + ". Print through _say or _warn instead."
    )


def test_p1r6f11_both_emitters_apply_the_boundary() -> None:
    """And each of the two really does escape what it is handed."""
    tree = _command_module_tree()
    for wanted in ("_say", "_warn"):
        defined = [
            node
            for node in ast.walk(tree)
            if isinstance(node, ast.FunctionDef) and node.name == wanted
        ]
        assert len(defined) == 1, f"cli.{wanted} must be defined exactly once"
        called = [
            node.func.attr
            for node in ast.walk(defined[0])
            if isinstance(node, ast.Call)
            and isinstance(node.func, ast.Attribute)
        ]
        assert "visible_lines" in called, (
            f"cli.{wanted} prints without putting the text through "
            f"parsing.visible_lines first"
        )


def test_p1r6f11_the_command_module_writes_to_no_stream_directly() -> None:
    """A .write call would be a third way out, past both emitters."""
    tree = _command_module_tree()
    writes = [
        node.lineno
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr == "write"
    ]
    assert not writes, (
        "cli.py writes to a stream directly at line(s) "
        + ", ".join(f"{line}" for line in writes)
        + "; every message must go through _say or _warn."
    )
