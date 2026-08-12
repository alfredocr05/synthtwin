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
    # The two messages about the disk take the arguments profile.py
    # actually passes: the caller has LOOKED at each name and hands over
    # what it saw. The older one-list form is still accepted, but no
    # code path produces it, so testing it would test nothing a person
    # can read.
    #
    # This one is the clean stop: the run failed before it published
    # anything, both names are as they were, and there is genuinely
    # nothing for the reader to do about it -- which is why it keeps the
    # exemption below.
    "nothing_was_written": (
        [],
        [
            ("/reports/table-profile.json", errors.ON_DISK_ABSENT),
            ("/reports/table-profile.txt", errors.ON_DISK_ABSENT),
        ],
    ),
    # And this one is the stop that could not undo itself: a new profile
    # at the profile's name, last week's summary beside it, and the
    # earlier profile stranded under a working name.
    "rollback_failed": (
        [],
        [
            ("/reports/table-profile.json", errors.ON_DISK_NEW),
            ("/reports/table-profile.txt", errors.ON_DISK_BEFORE),
            (
                "/reports/table-profile.json.synthtwin-kept-1",
                errors.ON_DISK_SET_ASIDE,
            ),
        ],
    ),
    "working_name_unavailable": (
        "/reports/table-profile.json",
        [
            "/reports/table-profile.json.synthtwin-part-1",
            "/reports/table-profile.json.synthtwin-part-2",
            "/reports/table-profile.json.synthtwin-part-3",
        ],
        64,
    ),
    "output_is_a_folder": ("/reports/table-profile.json",),
    "output_would_replace_the_table": ("/data/table.csv",),
    "unknown_column_named": ("holding record numbers", "agee", ["age", "site"]),
    "out_of_memory_while_describing": ("/data/table.csv",),
    "output_is_not_a_plain_file": ("/reports/table-profile.json",),
    "outputs_are_the_same_file": ("/r/a-profile.json", "/r/a-profile.txt"),
    # Reading a description back: the strict loader's nineteen refusals,
    # catalogued as R1 to R19 in `docs/spec/profile-contract-v4.md`
    # section 10.7. Each is raised by `contract.py`, and the battery in
    # `test_contract_loader.py` reaches every one of them with a real
    # file; what is checked here is the wording, beside every other
    # message the product can print.
    "profile_file_missing": ("/reports/table-profile.json",),
    "profile_file_unreadable": (
        "/reports/table-profile.json",
        "permission denied",
    ),
    "profile_path_is_a_folder": ("/reports",),
    "profile_not_text": ("/reports/table-profile.json",),
    "profile_not_json": ("/reports/table-profile.json", 12, 5),
    "profile_holds_unwritable_text": ("/reports/table-profile.json",),
    "profile_holds_a_number_that_is_not_one": (
        "/reports/table-profile.json",
    ),
    "profile_nested_too_deeply": ("/reports/table-profile.json", 32),
    "profile_number_too_long": ("/reports/table-profile.json", 64),
    "profile_not_canonical": ("/reports/table-profile.json",),
    "profile_version_is_older": (3, 4),
    "profile_version_is_newer": (5, 4),
    "profile_unknown_key": ("weather", "in the block for the column 'age'"),
    "profile_missing_key": (
        "n_present",
        "in the block for the column 'age'",
        "every column",
    ),
    "profile_wrong_type": (
        "n_rows",
        "at the top of the description",
        "a piece of text",
        "a whole number",
    ),
    "profile_out_of_range": (
        "small_cell_floor",
        "in the block of rules that produced the description",
        "3",
        "a whole number of 11 or more",
    ),
    "profile_out_of_range_unquoted": (
        "n_rows",
        "at the top of the description",
        "a whole number of 0 or more",
    ),
    "profile_invariant_broken": (
        "X1",
        (
            "the values a column holds and the cells it leaves empty "
            "together come to the number of rows in the table"
        ),
        "in the block for the column 'age'",
        "the column holds 20 values and leaves 21 cells empty",
        "the description gives the table a different number of rows",
    ),
    "profile_relationships_carried": ("grain",),
    "profile_out_of_memory": ("/reports/table-profile.json",),
    # Building the twin: the three refusals that belong to the command
    # rather than to the loader or to the method (plan P2-D10), plus the
    # one for a machine that ran out of memory building it. The seed
    # arrives as the TEXT that was typed, because whether it is a number
    # at all is the question these two messages answer.
    "seed_not_in_figures": ("-1", "18446744073709551615"),
    "seed_too_large": ("18446744073709551616", "18446744073709551615"),
    "outputs_already_there": (
        "/data/clinic-twin.csv",
        "/data/clinic-twin-report.txt",
        ["/data/clinic-twin.csv"],
    ),
    "twin_out_of_memory": ("/data/clinic-profile.json",),
    # The publication guard's one refusal (plan P2-D2, review item
    # P2-C1-F3). Its argument is the PLACE in the description, written
    # from the guard's own path steps: no key of the document and no
    # value of the table reaches it, because the run is stopping
    # precisely because synthtwin cannot account for the text that
    # stood there.
    "publication_guard_stopped": ("publication_notes[].note",),
}


# One entry is APPENDED to a refusal that already says what happened and
# what to do: profile.py builds `f"{trouble} {nothing_was_written(...)}"`.
# Its job is to describe the disk afterwards, and after a stop that
# published nothing and left nothing behind, it has -- rightly -- nothing
# to ask of the reader. The instruction is in the sentence it joins, so
# the actionable-wording rule is checked there, not here. Every other
# rule below still applies to it.
#
# `rollback_failed` used to sit here too, on the same reasoning, and its
# exemption is now stale: the rewritten wording ends "Check each one
# before you use it, and finish by hand what synthtwin could not", in
# every form the code can produce. A stale exemption is a hole waiting
# for the next message to fall through, so it was taken away rather than
# left standing.
APPENDED = {"nothing_was_written"}


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
    if name in APPENDED:
        # An appended message follows a complete sentence, so it has to
        # open one of its own. The general check above lets a message
        # start with a non-letter; one that lands mid-paragraph may not.
        assert message[0].isupper() or opening == "synthtwin", (
            f"{name} is appended to a refusal, so it must open a new "
            f"sentence rather than trail off the last one: {message!r}"
        )
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
    if name not in APPENDED:
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
