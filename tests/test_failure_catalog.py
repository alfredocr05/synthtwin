"""The refusal catalog: every message, and every message reachable.

Plan P1-D7. "Errors speak human" is a promise that can rot quietly: a
message is added, the code that raises it is refactored away, and the
catalog keeps a sentence nobody will ever see. Two things are checked
here -- that every message has the shape a person can act on, and that
every message in the catalog is actually raised by some code path.
"""

import inspect
import pathlib

import pytest

from synthtwin import errors

# The builders and one set of plausible arguments for each. Adding a
# builder to errors.py without adding it here fails the completeness
# test below.
CASES: "dict[str, tuple[object, ...]]" = {
    "file_missing": ("/data/table.csv",),
    "path_is_a_folder": ("/data",),
    "file_unreadable": ("/data/table.csv", "permission denied"),
    "not_utf8_or_latin1": ("/data/table.csv",),
    "looks_like_utf16": ("/data/table.csv",),
    "file_is_empty": ("/data/table.csv",),
    "no_data_rows": ("/data/table.csv",),
    "header_looks_like_data": ("/data/table.csv", "every value reads as a number"),
    "duplicate_column_names": (["age", "age"],),
    "empty_column_name": (3,),
    "ragged_rows": ("/data/table.csv", 4, [(2, 3), (7, 5)], 9),
    "field_too_long": ("/data/table.csv", 10_000_000),
    "unreadable_as_csv": ("/data/table.csv", "unexpected end of data"),
    "readers_disagree": ("/data/table.csv", "12 rows", "13 rows"),
    "out_of_memory": ("/data/table.csv", 4_000_000_000),
    "output_folder_missing": ("/reports",),
    "output_not_writable": ("/reports/out.json", "read-only file system"),
    "floor_not_positive": ("0",),
    "first_row_could_be_a_record": ("/data/table.csv", 3),
    "readers_disagree_about_a_name": ("/data/table.csv", 2, "age", "agee"),
    "readers_disagree_about_a_value": ("/data/table.csv", 7, "age"),
    "blank_line_in_one_column": ("/data/table.csv", 4),
    "nothing_was_written": ([],),
    "rollback_failed": (["/reports/a-profile.json"],),
    "output_is_a_folder": ("/reports/table-profile.json",),
    "output_would_replace_the_table": ("/data/table.csv",),
    "unknown_column_named": ("holding record numbers", "agee", ["age", "site"]),
    "out_of_memory_while_describing": ("/data/table.csv",),
    "output_is_not_a_plain_file": ("/reports/table-profile.json",),
    "outputs_are_the_same_file": ("/r/a-profile.json", "/r/a-profile.txt"),
}


# Two entries are CLAUSES, appended to a refusal that already says what
# happened and what to do. They still need coverage -- they name files
# left on disk -- but the instruction belongs to the sentence they join,
# so the actionable-wording rule is checked on that sentence, not here.
FRAGMENTS = {"nothing_was_written", "rollback_failed"}


def _builders() -> "dict[str, object]":
    found = {}
    for name, value in vars(errors).items():
        if name.startswith("_") or not inspect.isfunction(value):
            continue
        if value.__module__ != errors.__name__:
            continue
        found[name] = value
    return found


def test_every_builder_in_the_catalog_is_covered_here() -> None:
    assert sorted(_builders()) == sorted(CASES), (
        "every refusal message needs a case in this file: a message with "
        "no test is a message nobody has read"
    )


@pytest.mark.parametrize("name", sorted(CASES))
def test_every_message_says_what_happened_and_what_to_do(name: str) -> None:
    message = _builders()[name](*CASES[name])
    assert isinstance(message, str)
    assert len(message) > 40, f"{name} is too short to explain anything"
    opening = message.split(" ")[0]
    assert (
        message[0].isupper()
        or opening == "synthtwin"
        or not message[0].isalpha()
    ), f"{name} should read as a sentence, not a fragment: {message!r}"
    assert message.rstrip().endswith((".", "!")), f"{name} is not a sentence"
    if name in FRAGMENTS:
        # A clause must still be safe to append: it may not open with a
        # capital that would read as a new sentence mid-line.
        assert not message.startswith("The "), f"{name} reads as a new sentence"
    # Something the reader can do next. Every message must contain at
    # least one instruction, not only a diagnosis.
    actionable = (
        "Please",
        "please",
        "Check",
        "check",
        "Fix",
        "fix",
        "Create",
        "Add",
        "Rename",
        "Restore",
        "Open",
        "Close",
        "Make sure",
        "make sure",
        "open it",
        "Give a",
        "run the command again",
        "try again",
        "use that path",
    )
    if name not in FRAGMENTS:
        assert any(hint in message for hint in actionable), (
            f"{name} tells the reader what went wrong but not what to do "
            f"next: {message!r}"
        )


@pytest.mark.parametrize("name", sorted(CASES))
def test_no_message_speaks_in_jargon(name: str) -> None:
    message = _builders()[name](*CASES[name])
    for word in (
        "traceback",
        "exception",
        "stderr",
        "utf-8 codec",
        "None",
        "null",
        "dtype",
        "parse error",
        "invalid input",
    ):
        assert word not in message, (
            f"{name} uses '{word}', which is programmer's language"
        )


def test_the_catalog_is_reachable_from_the_code_that_raises_it() -> None:
    # A message nobody raises is dead weight that reads like a promise.
    # Every builder must be named in the source of a module that raises
    # ProfileError.
    root = pathlib.Path(errors.__file__).parent
    sources = "\n".join(
        path.read_text(encoding="utf-8")
        for path in sorted(root.glob("*.py"))
        if path.name != "errors.py"
    )
    unused = [name for name in CASES if f"errors.{name}(" not in sources]
    assert not unused, (
        f"these messages are never raised by any code path: {unused}. "
        "Either raise them where they belong or delete them."
    )


def test_ragged_row_message_names_positions_as_data_rows() -> None:
    message = errors.ragged_rows("/t.csv", 4, [(2, 3)], 1)
    assert "row 2 has 3" in message
    assert "counted after the first row" in message, (
        "a file line number can land in the middle of a quoted value, so "
        "the message has to say which numbering it means"
    )


def test_out_of_memory_message_carries_the_size_in_megabytes() -> None:
    message = errors.out_of_memory("/t.csv", 4_000_000_000)
    assert "3814 MB" in message
