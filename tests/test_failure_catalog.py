"""The refusal catalog: every message, and every message reachable.

Plan P1-D7. "Errors speak human" is a promise that can rot quietly: a
message is added, the code that raises it is refactored away, and the
catalog keeps a sentence nobody will ever see. Two things are checked
here -- that every message has the shape a person can act on, and that
every message in the catalog is actually raised by some code path.
"""

import contextlib
import inspect
import os
import pathlib
import stat

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
    # The same three refusals for a file `synthtwin validate` was only
    # pointed at (plan P3-D1, V9). Every argument is a POSITION: on that
    # path the file may not be the reader's own table, and a refusal
    # travels as freely as a report does. The test below walks their
    # arguments and asserts no spelling from a file can be among them.
    "checked_file_readers_disagree_about_a_name": ("/data/checked.csv", 2),
    "checked_file_readers_disagree_about_a_value": (
        "/data/checked.csv",
        7,
        2,
    ),
    "checked_file_unreadable_as_csv": ("/data/checked.csv",),
    "checked_file_repeats_a_column_name": ("/data/checked.csv",),
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
    # Checking a written file against a description (plan P3-D1). The
    # first two belong to the command, the third to the machine. The
    # source noun in the second is one of the two written out in
    # errors.py beside `QUALITY_WORDS`, never a value out of a file: on
    # this path the measured file may not be the reader's own table and
    # a refusal travels as freely as a report does.
    "quality_target_already_there": ("/data/clinic-twin-quality.txt",),
    "output_would_replace_an_input": (
        "/data/clinic-profile.json",
        "description",
    ),
    "quality_out_of_memory": ("/data/clinic-profile.json",),
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
    """Every function in the catalog that builds a MESSAGE.

    A builder is recognised by what it returns and not by a list of
    names kept beside it: `errors` also holds `shape_refusal`, which
    builds a refusal OBJECT carrying which of the reader's shape
    refusals it is (review item P3-V4-F3), and a name list would have
    had to grow by hand for it and for the next one. The rules below are
    about the sentence a person reads, so what they govern is every
    function that hands one back.
    """
    found = {}
    for name, value in vars(errors).items():
        if name.startswith("_") or not inspect.isfunction(value):
            continue
        if value.__module__ != errors.__name__:
            continue
        if inspect.signature(value).return_annotation is not str:
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
    #
    # WHAT THIS PROVES AND WHAT IT DOES NOT (review item P3-V4-F10).
    # This is a SOURCE SEARCH, and a source search settles a necessary
    # condition and nothing more: a builder no module names cannot be
    # raised, so its absence here is real news. The converse does not
    # follow, and the plan asks for the converse (P3-D6: "each with
    # exact-shape and reachability tests"). A regression that let a
    # `PermissionError` escape as a traceback would leave the token
    # `errors.file_unreadable(` sitting in `validation.py`, and this
    # would go on passing while the person got a stack trace.
    #
    # So the refusals plan P3-D6 names are DRIVEN below, through the
    # shipped command, at the condition that produces each one. This
    # test keeps its place because it is total over the catalog and the
    # driven battery is not: ninety-odd messages cannot each be reached
    # by a real run in a test suite, and pretending otherwise would be a
    # worse claim than the honest small one.
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


CHECKED_FILE_FORMS = (
    "checked_file_readers_disagree_about_a_name",
    "checked_file_readers_disagree_about_a_value",
    "checked_file_unreadable_as_csv",
    "checked_file_repeats_a_column_name",
)


@pytest.mark.parametrize("name", CHECKED_FILE_FORMS)
def test_a_checked_file_refusal_takes_positions_and_nothing_else(
    name: str,
) -> None:
    """V9: every refusal reachable from validate names positions.

    The rule is checked at the SIGNATURE, which is where it can be kept:
    a builder that takes only a path and whole numbers has nothing out
    of the file to put in its sentence, whatever anybody writes in it
    later. The profiler's own forms of these three take the name and
    the value beside the position, which is why they are three separate
    builders rather than one with a flag.
    """
    given = CASES[name]
    assert given[0] == "/data/checked.csv"
    for argument in given[1:]:
        assert isinstance(argument, int), (
            f"{name} takes something that is not a position: a refusal "
            f"about a file nobody promised was the reader's may name "
            f"which column and which row, and nothing else"
        )
    message = _builders()[name](*given)
    assert "may not be your own table" in message, (
        f"{name} should say why it is not showing what it found"
    )


def test_the_checked_file_forms_say_no_more_than_the_position() -> None:
    """The quoting forms and the position forms, side by side.

    The profiler's form of each of these carries a spelling out of the
    file; the checking form carries the column number in its place. This
    is the assertion that the second really is the first with the
    spelling taken out, rather than the first under a new name.
    """
    quoting = errors.readers_disagree_about_a_name(
        "/data/checked.csv", 2, "age", "agee"
    )
    position = errors.checked_file_readers_disagree_about_a_name(
        "/data/checked.csv", 2
    )
    assert "age" in quoting and "agee" in quoting
    assert "agee" not in position
    assert "column number 2" in position

    quoting = errors.readers_disagree_about_a_value(
        "/data/checked.csv", 7, "age"
    )
    position = errors.checked_file_readers_disagree_about_a_value(
        "/data/checked.csv", 7, 2
    )
    assert "'age'" in quoting
    assert "'age'" not in position
    assert "row 7" in position and "column number 2" in position

    quoting = errors.unreadable_as_csv("/data/checked.csv", "line 4, saw 9")
    position = errors.checked_file_unreadable_as_csv("/data/checked.csv")
    assert "line 4, saw 9" in quoting
    assert "line 4, saw 9" not in position


def test_out_of_memory_message_carries_the_size_in_megabytes() -> None:
    message = errors.out_of_memory("/t.csv", 4_000_000_000)
    assert "3814 MB" in message


# ---------------------------------------------------------------------
# V9: what may be RAISED from a validate run (review item P3-V2-D-F1)
# ---------------------------------------------------------------------


def _carries_no_text(value: object) -> bool:
    """Whether one argument can hold a string at all, however nested.

    `ragged_rows` is why this is not a flat `isinstance(int)`: it takes
    a LIST of (row number, value count) pairs, and a list of whole
    numbers is as incapable of carrying a spelling as a whole number is.
    """
    if isinstance(value, bool):
        return False
    if isinstance(value, int):
        return True
    if isinstance(value, (list, tuple)):
        for item in value:
            if not _carries_no_text(item):
                return False
        return True
    return False


def _names_positions_only(name: str) -> bool:
    """Whether this builder's own arguments can carry a measured string.

    THE RULE IS CHECKED AT THE SIGNATURE, which is where it can be kept:
    a builder whose arguments are a path and whole numbers has nothing
    out of the file to put in its sentence, whatever anybody writes into
    it later. The path is the one the person typed on the command line
    and is theirs already (V9's own reading). Driven from the catalog
    above, so a builder added to `errors.py` is inside this rule the day
    it is added and cannot be left out of a list somebody maintains by
    hand.
    """
    given = CASES[name]
    if not given:
        return True
    if not isinstance(given[0], str):
        return _carries_no_text(given[0]) and all(
            _carries_no_text(argument) for argument in given[1:]
        )
    for argument in given[1:]:
        if not _carries_no_text(argument):
            return False
    return True


def test_no_refusal_that_can_quote_the_file_is_reachable_from_measure(
    tmp_path: pathlib.Path,
) -> None:
    """V9: every refusal reachable from validate names positions.

    REVIEW ITEM P3-V2-D-F1, AND THE TEST WHOSE ABSENCE LET IT THROUGH.
    Round 1 repaired two header faults by settling them before the
    reader is called, and the test written for that repair checked the
    SIGNATURES of three builders named by hand. Nothing asked the only
    question that matters -- which builders a validate run can actually
    reach -- so two files walked straight past the pre-check into the
    reader's own repeated-name refusal, which QUOTES the repeated name,
    and printed a string out of the measured file on the screen.

    So this drives the whole catalog: every builder in it is wrapped,
    `validation.measure` is run over a battery of hostile files, and
    every builder that fired has to be one whose own arguments cannot
    carry a spelling out of the file. The battery is not a proof of
    absence and does not claim to be; what it is is the question being
    asked at all, of every builder there is, in the shape that turns red
    the day one of them starts being reachable.
    """
    import fixtures
    from synthtwin import contract, profile, reading, taxonomy, validation

    table = fixtures.rows_to_csv(
        ["reading", "region"],
        [
            [f"{index + 1}", fixtures.REGIONS[index % 4]]
            for index in range(40)
        ],
    )
    written = fixtures.write(tmp_path, "table.csv", table)
    read = reading.read_table(str(written))
    document = profile.build_document(read, taxonomy.Settings(), [])
    described = contract.load_profile(
        str(fixtures.write_profile(tmp_path, "t-profile.json", document))
    )

    marker = "zzmarkerzz"
    hostile = {
        "twin": table,
        "duplicate-names": f"{marker},{marker}\n1,2\n3,4\n",
        "blank-first-line": f"\n{marker},{marker}\n1,2\n3,4\n",
        "quoted-newline-name": f'"{marker}\nx","{marker}\nx"\n1,2\n3,4\n',
        "blank-name": "\n,x\n1,2\n3,4\n",
        "header-only": "reading,region\n",
        "header-and-blank-lines": "reading,region\n\n\n",
        "one-newline": "\n",
        "no-bytes": "",
        "spaces": "   \n",
        "unclosed-quote": 'reading,region\n1,"unclosed\n',
        "ragged": "reading,region\n1,north,extra\n2,south\n",
        "one-column": "reading\n1\n2\n",
        "extra-column": "reading,region,extra\n1,north,x\n2,south,y\n",
        "carriage-returns": "reading,region\r\n1,north\r\n",
        "carriage-only": "reading,region\r1,north\r",
        "byte-order-mark": "﻿reading,region\n1,north\n",
        "blank-line-inside": "reading\n1\n\n2\n",
        "long-field": "reading,region\n" + "1" * 200 + ",north\n",
    }

    fired: set[str] = set()
    builders = _builders()
    for name in sorted(CASES):
        setattr(errors, name, _recording(builders[name], name, fired))
    try:
        for label in sorted(hostile):
            target = tmp_path / f"{label}.csv"
            target.write_text(hostile[label], encoding="utf-8", newline="")
            try:
                validation.measure(described, str(target))
            except errors.ProfileError:
                pass
    finally:
        for name in sorted(CASES):
            setattr(errors, name, builders[name])

    assert fired, (
        "no refusal fired at all, so this battery proved nothing -- a "
        "file the reader stops on has to be in it"
    )
    quoting = sorted(name for name in fired if not _names_positions_only(name))
    assert not quoting, (
        "these refusals are reachable from a validate run and their own "
        "arguments can carry a spelling out of the measured file, which "
        f"V9 forbids on a file nobody promised was the reader's: {quoting}"
    )


def _recording(builder, name, fired):
    """One builder, wrapped so that calling it is recorded."""

    def wrapper(*arguments, **keywords):
        fired.add(name)
        return builder(*arguments, **keywords)

    return wrapper


# ---------------------------------------------------------------------
# P3-D6's reachability half, driven (review item P3-V4-F10)
# ---------------------------------------------------------------------
#
# THE DEFECT THIS CLOSES. The plan requires the validate-side additions
# to this catalog to have "exact-shape AND reachability tests". The
# exact-shape half is above. The reachability half was
# `test_the_catalog_is_reachable_from_the_code_that_raises_it`, which
# searches source text -- so a refusal whose raise site had stopped
# being reached would pass it with the token still in the file, and the
# person would meet a traceback instead of a sentence.
#
# Each case below builds the condition and runs the SHIPPED COMMAND at
# it. Three things are asserted of every one: the named builder fired,
# the command returned the refusal code rather than raising, and the
# sentence reached the screen. An escaping exception fails the second;
# a message composed but never printed fails the third.


def _builders_recording(fired: "set[str]") -> "dict[str, object]":
    """Wrap every builder in the catalog so that calling it is recorded."""
    import synthtwin.errors as module

    builders = _builders()
    for name, builder in builders.items():
        setattr(module, name, _recording(builder, name, fired))
    return builders


def _put_the_builders_back(builders: "dict[str, object]") -> None:
    import synthtwin.errors as module

    for name, builder in builders.items():
        setattr(module, name, builder)


def _a_described_table(folder: "pathlib.Path") -> "pathlib.Path":
    """A real table, described by the real command; returns the profile."""
    import fixtures
    from synthtwin.cli import main

    rows = [
        [fixtures.REGIONS[index % 4], f"{index % 7}"] for index in range(48)
    ]
    table = fixtures.write(
        folder, "clinic.csv", fixtures.rows_to_csv(["region", "visits"], rows)
    )
    assert main(["profile", f"{table}"]) == 0
    return folder / "clinic-profile.json"


def _with_a_twin(folder: "pathlib.Path") -> "pathlib.Path":
    from synthtwin.cli import main

    description = _a_described_table(folder)
    assert main(["generate", f"{description}"]) == 0
    return description


# ---------------------------------------------------------------------
# A FILE THIS HOST WILL NOT LET SYNTHTWIN READ (review item P3-V4-F10,
# round 5 item 10)
# ---------------------------------------------------------------------
#
# WHY THIS IS NOT ONE LINE OF CODE. `os.chmod(path, 0)` is the POSIX
# spelling of "nobody may read this", and for one round it was the whole
# of this condition, guarded by `os.geteuid() == 0` -- a function
# Windows does not have. Every Windows cell of the governed matrix (the
# `tests` job of `.github/workflows/ci.yml`) therefore ended in an
# AttributeError before it proved anything, and the charter requires CI
# green before a merge. Guarding the guard with `sys.platform` would
# have swapped the error for a skip, which is the same defect wearing a
# different coat: this refusal exists for the person whose file cannot
# be read, and Windows is where that most often happens -- the file is
# open in another program. A proof that steps aside on the platform it
# is most needed on proves nothing there.
#
# So the condition is written once per platform, in the mechanism that
# platform actually has, and EVERY mechanism IS CHECKED before the
# command is run: the file has to still be there and has to refuse to
# open. A mechanism that fails that check is undone and not used; if no
# mechanism on this host achieves it, the case fails and names the host,
# rather than passing or skipping. The one configuration in which no
# mechanism can exist is named in `_a_file_that_will_not_open`.


def _present_but_will_not_open(place: pathlib.Path) -> bool:
    """Whether ``place`` is still there and still refuses to be read.

    BOTH HALVES MATTER. `validation.measure` asks three questions in
    order -- is anything there, is it a folder, do its bytes come back
    -- and only the third produces `file_unreadable`. A mechanism that
    makes the file disappear, or that stops the filesystem answering
    about it at all (which is what `Path.exists` reports), would drive
    the command to `file_missing` instead: a different refusal, reached
    for a different reason, with this case none the wiser. So the
    witness is checked against the same two questions the product asks
    before the one it is here to prove.
    """
    if not place.exists():
        return False
    try:
        place.read_bytes()
    except OSError:
        return True
    return False


def _mode_bits_forbid_everybody(place: pathlib.Path) -> "object | None":
    """POSIX: take every read permission off the file.

    This is the mechanism the person meets as "permission denied", and
    it is the one the ordinary CI accounts (`runner` on the hosted
    Linux and macOS images) can produce. It does nothing for a
    superuser, who reads a file whose mode bits forbid everybody; the
    caller checks, so that configuration is named rather than passed.
    """
    was = stat.S_IMODE(place.stat().st_mode)
    os.chmod(place, 0)

    def undo() -> None:
        os.chmod(place, was)

    return undo


def _a_lock_over_every_byte(place: pathlib.Path) -> "object | None":
    """Windows: lock the whole file against every other handle.

    THE REAL WINDOWS CONDITION, not a translation of the POSIX one.
    `chmod` on Windows moves the read-only attribute and nothing else,
    so the file stays perfectly readable and the POSIX mechanism proves
    nothing there. What actually stops a Windows user reading their own
    file is another program holding it: locks on Windows are mandatory,
    and a read of a locked region through any other handle fails with a
    permission error -- which is the exception `validation.measure`
    turns into this refusal.

    The lock is taken through the C runtime's own call (`msvcrt`, a
    standard-library module that exists only on Windows), over the
    file's whole length from byte zero, and it is released and the
    handle closed by the undo -- both because the case must leave the
    folder as it found it and because Windows will not delete a file
    with an open handle on it, which would strand the temporary folder.

    The handle is opened in BINARY read-write mode: `msvcrt.locking`
    needs a descriptor that may write, and a binary handle translates
    no byte on its way anywhere, which is what the suite's own
    line-ending rule asks of every handle it opens.
    """
    try:
        import msvcrt
    except ImportError:  # pragma: no cover -- not a Windows host
        return None

    size = place.stat().st_size
    if size == 0:
        return None
    # A context manager is exactly what this must not be: the lock has
    # to outlive this call, because it is held while the command runs,
    # and the undo below is what closes the handle.
    handle = open(place, "r+b")  # noqa: SIM115 -- outlives this call
    try:
        os.lseek(handle.fileno(), 0, os.SEEK_SET)
        msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, size)
    except OSError:
        handle.close()
        return None

    def undo() -> None:
        try:
            os.lseek(handle.fileno(), 0, os.SEEK_SET)
            msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, size)
        except OSError:
            pass
        finally:
            handle.close()

    return undo


def _an_open_handle_that_shares_nothing(
    place: pathlib.Path,
) -> "object | None":
    """Windows, second mechanism: hold the file open sharing nothing.

    A file opened with no sharing cannot be opened again by anybody,
    which is the sharing violation a Windows user meets as "the file is
    in use by another program". It is second rather than first because
    it is the more invasive of the two: a handle that shares nothing
    also refuses the open that `stat` would like to make, and the
    product asks `Path.exists` before it reads. Modern CPython answers
    `stat` from the directory entry when the file cannot be opened, so
    this should still leave a file that is present and unreadable -- and
    `_present_but_will_not_open` is what settles whether it does on the
    host in front of us, rather than this comment.
    """
    try:
        import _winapi
    except ImportError:  # pragma: no cover -- not a Windows host
        return None

    generic_read = 0x80000000
    share_nothing = 0
    open_existing = 3
    try:
        handle = _winapi.CreateFile(
            f"{place}", generic_read, share_nothing, 0, open_existing, 0, 0
        )
    except OSError:
        return None

    def undo() -> None:
        _winapi.CloseHandle(handle)

    return undo


def _mechanisms_on_this_host() -> "tuple[object, ...]":
    """Every way THIS platform has of taking a read away.

    Windows gets both of its own, in the order that disturbs the file
    least first. POSIX gets the one it has. A platform nobody has
    written a mechanism for gets none, and the caller says so by name.
    """
    if os.name == "nt":
        return (_a_lock_over_every_byte, _an_open_handle_that_shares_nothing)
    return (_mode_bits_forbid_everybody,)


def _a_file_that_will_not_open(place: pathlib.Path) -> "object":
    """Make ``place`` refuse to be read here, and hand back the undo.

    Guarantees:

    - The file is present and refuses to open when this returns; that
      is checked, not assumed, whatever mechanism achieved it.
    - The returned callable puts the file back exactly as it was.
    - It SKIPS in exactly one configuration -- a POSIX superuser, who
      reads a file whose mode bits forbid everybody, and for whom this
      platform's other mechanisms (advisory locks) do not stop a read
      either. No governed CI cell is one: the hosted Linux and macOS
      images run the suite as an ordinary account, and the Windows
      cells do not take this branch at all.
    - On every other host it either produces the condition or FAILS.
      A file nobody can read is what this refusal is for, so a host
      where the case cannot be built is news about the case, and news
      is not something to skip past.
    """
    for mechanism in _mechanisms_on_this_host():
        undo = mechanism(place)
        if undo is None:
            continue
        if _present_but_will_not_open(place):
            return undo
        undo()  # type: ignore[operator]
    if os.name != "nt" and os.geteuid() == 0:
        pytest.skip(
            "this account is a POSIX superuser, which reads a file whose "
            "mode bits forbid everybody; no CI cell runs as one"
        )
    pytest.fail(
        f"no mechanism this file knows about made {place.name} refuse to "
        f"be read on this host (os.name={os.name!r}), so the refusal for "
        f"a file that cannot be read has no reachability proof here. "
        f"Write the mechanism this platform has and add it to "
        f"_mechanisms_on_this_host; do not skip the case, because the "
        f"person whose file will not open is on this platform too"
    )


# One entry per refusal plan P3-D6 names for the validate path: the
# builder that must fire, a phrase of its sentence that must reach the
# screen, and the condition, built in a folder of the case's own. Each
# builder is handed an `undo` stack for whatever it has to put back
# afterwards -- a locked file has to be unlocked and a mode restored
# before the temporary folder can be swept up, and on Windows a file
# with a handle still on it cannot be deleted at all.
def _missing_measured_file(folder, description, undo):
    return ["validate", f"{description}", "--twin", f"{folder / 'gone.csv'}"]


def _measured_file_is_a_folder(folder, description, undo):
    (folder / "a-folder").mkdir()
    return ["validate", f"{description}", "--twin", f"{folder / 'a-folder'}"]


def _measured_file_cannot_be_read(folder, description, undo):
    twin = folder / "clinic-twin.csv"
    undo.callback(_a_file_that_will_not_open(twin))
    return ["validate", f"{description}"]


def _measured_file_holds_a_field_too_long(folder, description, undo):
    import fixtures

    bad = fixtures.write(
        folder, "wide.csv", "region,visits\n" + "a" * 20_000_000 + ",1\n"
    )
    return ["validate", f"{description}", "--twin", f"{bad}"]


def _measured_file_is_not_text_a_reader_can_take(folder, description, undo):
    target = folder / "binary.csv"
    target.write_bytes(b"region,visits\n\x00\x01\x02,1\n")
    return ["validate", f"{description}", "--twin", f"{target}"]


def _the_report_is_already_there(folder, description, undo):
    from synthtwin.cli import main

    assert main(["validate", f"{description}"]) == 0
    return ["validate", f"{description}"]


def _the_report_would_land_on_the_description(folder, description, undo):
    report = folder / "clinic-twin-quality.txt"
    report.unlink(missing_ok=True)
    report.symlink_to(description)
    return ["validate", f"{description}", "--replace"]


def _the_report_would_land_on_the_measured_file(folder, description, undo):
    report = folder / "clinic-twin-quality.txt"
    report.unlink(missing_ok=True)
    report.symlink_to(folder / "clinic-twin.csv")
    return ["validate", f"{description}", "--replace"]


DRIVEN = (
    ("file_missing", "There is no file at", False, _missing_measured_file),
    ("path_is_a_folder", "is a folder", False, _measured_file_is_a_folder),
    (
        "file_unreadable",
        "could not be opened",
        True,
        _measured_file_cannot_be_read,
    ),
    (
        "field_too_long",
        "more text than synthtwin will read in a single value",
        True,
        _measured_file_holds_a_field_too_long,
    ),
    (
        "looks_like_utf16",
        "it contains the zero bytes those formats use",
        True,
        _measured_file_is_not_text_a_reader_can_take,
    ),
    (
        "quality_target_already_there",
        "something is already at the name it would write",
        True,
        _the_report_is_already_there,
    ),
    (
        "output_would_replace_an_input",
        "would have replaced",
        True,
        _the_report_would_land_on_the_description,
    ),
    (
        "output_would_replace_an_input",
        "would have replaced",
        True,
        _the_report_would_land_on_the_measured_file,
    ),
)


@pytest.mark.parametrize(
    "name,phrase,needs_a_twin,build",
    DRIVEN,
    ids=[f"{name}-{build.__name__}" for name, _p, _t, build in DRIVEN],
)
def test_a_p3d6_refusal_is_reached_by_running_the_command(
    name: str,
    phrase: str,
    needs_a_twin: bool,
    build: object,
    tmp_path: pathlib.Path,
    capsys: "pytest.CaptureFixture[str]",
) -> None:
    """The refusal, produced by the shipped command at a real condition.

    NOTHING HERE ASKS WHAT PLATFORM IT IS ON. Each condition builds
    itself in the mechanism its host has, and says so if it cannot; a
    test body that reached for a POSIX-only call to decide whether to
    run was what stopped the whole Windows matrix executing (round 5
    item 10).
    """
    from synthtwin.cli import main

    with contextlib.ExitStack() as undo:
        description = (
            _with_a_twin(tmp_path)
            if needs_a_twin
            else _a_described_table(tmp_path)
        )
        capsys.readouterr()
        fired: set[str] = set()
        builders = _builders_recording(fired)
        try:
            argv = build(tmp_path, description, undo)  # type: ignore[operator]
            code = main(argv)
        finally:
            _put_the_builders_back(builders)
        printed = capsys.readouterr()
    said = printed.out + printed.err
    assert code == 1, (
        f"the command returned {code} where 1 is the code for a run that "
        f"could not be made at all. A condition that ends in a traceback "
        f"or in a verdict is not this refusal being reached"
    )
    assert name in fired, (
        f"{name} did not fire; what did was {sorted(fired)}. Either the "
        f"condition no longer produces this refusal -- in which case the "
        f"catalog's claim that it is reachable is what is wrong -- or "
        f"the condition here has stopped being the one it names"
    )
    assert phrase in said, (
        f"{name} was composed and no part of it reached the person: "
        f"{said!r}"
    )


def test_the_driven_battery_covers_the_refusals_the_plan_names() -> None:
    """The battery is not allowed to shrink quietly.

    Every builder it drives is one the catalog carries, and the count is
    written down: a case deleted from `DRIVEN` takes a refusal's only
    reachability proof with it, and this is what says so.
    """
    driven = {name for name, _phrase, _twin, _build in DRIVEN}
    unknown = sorted(driven - set(CASES))
    assert not unknown, (
        f"these driven cases name a builder the catalog does not carry: "
        f"{unknown}"
    )
    assert len(DRIVEN) == 8 and len(driven) == 7, (
        f"the driven battery is {len(DRIVEN)} case(s) over {len(driven)} "
        f"refusal(s), and was 8 over 7. A case that leaves takes a "
        f"refusal's only reachability proof with it, so say why in the "
        f"same commit"
    )
