"""P2-D10: the write transaction's refusals name the RIGHT files.

THE DEFECT THIS CLOSES. The two-file write transaction was built for the
profiler and is now the generator's too (plan P2-D1 moved it to
`writing.py`). The machinery is genuinely one piece of code, but the
refusals it composes named the profiler's files in plain words: "The
profile could not be written to ...", "... next to your table", "a
profile and a summary from two different runs do not describe the same
table", "... replaced your own table". A stopped `generate` run would
have handed a person a sentence about a profile it never writes to and a
table the command never had, and somebody acting on that sentence looks
at the wrong file.

WHAT IS CHECKED HERE, in four parts:

1. **Byte-identity.** Every one of those messages, composed the way the
   profiler composes it, is the same string it was before the words
   became an argument. The expected strings are written out in full
   rather than rebuilt, so this test fails on a wording change whether
   or not the change was meant.
2. **The generator's words**, in full, on the same terms -- and each
   held to the same shape rules the rest of the catalog is held to.
3. **No table, and no misnamed output**, anywhere in the generator's
   set. This is the property the whole change exists for, so it is
   asserted directly rather than left to be read out of part 2.
4. **The thread-through is complete.** Every function in `writing.py`
   that composes one of these refusals takes the words, checked by
   reading the module's own syntax rather than by trusting a list -- so a
   site added later without them fails here instead of shipping.

Parts 1 to 3 are exact-shape tests; part 4 and the transaction runs at
the end are the reachability half: the sentences are produced by driving
the real transaction, not by calling the builders.
"""

import ast
import pathlib

import pytest

from synthtwin import errors, writing

# ---------------------------------------------------------------------------
# part 1 -- what the profiler said before, to the byte
# ---------------------------------------------------------------------------

_DISK = [
    ("/d/t-profile.json", errors.ON_DISK_NEW),
    ("/d/t-profile.txt", errors.ON_DISK_BEFORE),
    ("/d/t-profile.json.synthtwin-kept-1", errors.ON_DISK_SET_ASIDE),
]

_PROFILE_ROLLBACK = (
    "synthtwin could not put things back as they were. This is what is "
    "at each name now: /d/t-profile.json holds the new description this "
    "run produced; /d/t-profile.txt holds the file that was there before "
    "this run, unchanged; /d/t-profile.json.synthtwin-kept-1 holds the "
    "description from before this run, which synthtwin moved here and "
    "could not move back. Check each one before you use it, and finish "
    "by hand what synthtwin could not: a profile and a summary from two "
    "different runs do not describe the same table."
)

_PROFILE_FOLDER_MISSING = (
    "The folder /reports does not exist, so synthtwin cannot write the "
    "profile there. Create the folder first, or leave the option out to "
    "write the profile next to your table."
)

_PROFILE_NOT_WRITABLE = (
    "The profile could not be written to /reports/out.json (read-only "
    "file system). Please check that you have permission to write there "
    "and that the file is not open in another program, then run the "
    "command again."
)

_PROFILE_WOULD_REPLACE = (
    "synthtwin stopped because writing the description would have "
    "replaced your own table at /data/table.csv. That would have "
    "destroyed the data you asked it to describe. This usually means a "
    "file of the profile's name is a link pointing back at the table. "
    "Remove that link, or use the option for a different output folder, "
    "then run the command again. Nothing was written."
)


def test_the_profiler_says_exactly_what_it_said_before() -> None:
    # The whole point of the default on every one of these builders: a
    # command that was already right keeps every byte it had. Anything
    # here failing means the profiler's own messages moved under the
    # generator's change, which is the one thing this parameter was
    # required not to do.
    assert errors.rollback_failed([], _DISK) == _PROFILE_ROLLBACK
    assert errors.output_folder_missing("/reports") == _PROFILE_FOLDER_MISSING
    assert (
        errors.output_not_writable(
            "/reports/out.json", "read-only file system"
        )
        == _PROFILE_NOT_WRITABLE
    )
    assert (
        errors.output_would_replace_the_table("/data/table.csv")
        == _PROFILE_WOULD_REPLACE
    )


def test_passing_the_profilers_words_is_the_same_as_leaving_them_out() -> None:
    # The default and the named set must be one thing, or the profile
    # command and a caller being explicit about it would drift apart.
    assert (
        errors.rollback_failed([], _DISK, errors.PROFILE_WORDS)
        == _PROFILE_ROLLBACK
    )
    assert (
        errors.output_folder_missing("/reports", errors.PROFILE_WORDS)
        == _PROFILE_FOLDER_MISSING
    )
    assert (
        errors.output_not_writable(
            "/reports/out.json", "read-only file system", errors.PROFILE_WORDS
        )
        == _PROFILE_NOT_WRITABLE
    )
    assert (
        errors.output_would_replace_the_table(
            "/data/table.csv", errors.PROFILE_WORDS
        )
        == _PROFILE_WOULD_REPLACE
    )


# ---------------------------------------------------------------------------
# part 2 -- what the generator says, in full
# ---------------------------------------------------------------------------

_TWIN_DISK = [
    ("/d/t-twin.csv", errors.ON_DISK_NEW),
    ("/d/t-twin-report.txt", errors.ON_DISK_BEFORE),
]

# AND IT SAYS THE TWIN (review item P3-V4-F11). This read "holds the
# new DESCRIPTION this run produced" about `/d/t-twin.csv`, which is a
# sentence about a file `generate` never writes, printed beside the
# name of the file it does. The words a command carries now reach the
# clause that says what is at each name.
_TWIN_ROLLBACK = (
    "synthtwin could not put things back as they were. This is what is "
    "at each name now: /d/t-twin.csv holds the new twin this run "
    "produced; /d/t-twin-report.txt holds the file that was there before "
    "this run, unchanged. Check each one before you use it, and finish "
    "by hand what synthtwin could not: a report from one run does not "
    "describe the twin from another."
)

_TWIN_FOLDER_MISSING = (
    "The folder /reports does not exist, so synthtwin cannot write the "
    "twin there. Create the folder first, or leave the option out to "
    "write the twin next to your profile."
)

_TWIN_NOT_WRITABLE = (
    "The twin could not be written to /reports/out.csv (read-only file "
    "system). Please check that you have permission to write there and "
    "that the file is not open in another program, then run the command "
    "again."
)

_TWIN_WOULD_REPLACE = (
    "synthtwin stopped because writing the twin would have replaced your "
    "own profile at /d/clinic-profile.json. That would have destroyed "
    "the description your twin is built from. This usually means a file "
    "of the twin's name is a link pointing back at the profile. Remove "
    "that link, or use the option for a different output folder, then "
    "run the command again. Nothing was written."
)

_TWIN_MESSAGES = {
    "rollback_failed": _TWIN_ROLLBACK,
    "output_folder_missing": _TWIN_FOLDER_MISSING,
    "output_not_writable": _TWIN_NOT_WRITABLE,
    "output_would_replace_the_table": _TWIN_WOULD_REPLACE,
}


def test_the_generators_words_compose_exactly_these_sentences() -> None:
    assert (
        errors.rollback_failed([], _TWIN_DISK, errors.TWIN_WORDS)
        == _TWIN_ROLLBACK
    )
    assert (
        errors.output_folder_missing("/reports", errors.TWIN_WORDS)
        == _TWIN_FOLDER_MISSING
    )
    assert (
        errors.output_not_writable(
            "/reports/out.csv", "read-only file system", errors.TWIN_WORDS
        )
        == _TWIN_NOT_WRITABLE
    )
    assert (
        errors.output_would_replace_the_table(
            "/d/clinic-profile.json", errors.TWIN_WORDS
        )
        == _TWIN_WOULD_REPLACE
    )


@pytest.mark.parametrize("name", sorted(_TWIN_MESSAGES))
def test_each_generator_message_reads_as_a_sentence_a_person_can_act_on(
    name: str,
) -> None:
    # The same shape rules the catalog test applies to every other
    # message. An inherited message that gained a second wording gained a
    # second way to be unreadable, so the new wording is held to the rule
    # rather than trusted for having been derived from a good one.
    message = _TWIN_MESSAGES[name]
    assert len(message) > 40
    assert message[0].isupper() or message.split(" ")[0] == "synthtwin"
    assert message.rstrip().endswith(".")
    # Something the reader can DO, drawn from the same set the catalog
    # test holds every other message to.
    assert any(
        hint in message
        for hint in ("Please", "Check", "check", "Create", "Remove", "run the command again")
    ), f"{name} says what went wrong but not what to do: {message!r}"
    for jargon in ("traceback", "exception", "None", "null", "invalid input"):
        assert jargon not in message


# ---------------------------------------------------------------------------
# part 3 -- the property the change exists for
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("name", sorted(_TWIN_MESSAGES))
def test_no_generator_message_sends_anyone_to_look_at_a_table(
    name: str,
) -> None:
    # `generate` reads a profile and writes a twin and a report. It never
    # opens a table, so a table has no place in anything it says: a
    # person told to check one would go looking for a file this command
    # never touched, or -- worse -- conclude that it did touch it.
    #
    # THE SCOPE OF THIS CLAIM is these four messages, which are the four
    # the plan named (P2-D10). It is not a claim about every sentence a
    # stopped generate run can produce: the words describing what is at
    # one name on disk are a separate list in `errors.py`, they are not
    # parameterized, and one of them -- the one for a working file that
    # could not be cleared away -- still says "text taken from your
    # table". That wording is only reached when a working file survives
    # the cleanup, which the runs below do not produce.
    assert "table" not in _TWIN_MESSAGES[name].casefold()


def test_no_generator_message_says_the_profile_could_not_be_written() -> None:
    # The profile is the file the person handed in. It is the one file a
    # `generate` run is forbidden to write to, so a refusal claiming
    # synthtwin failed to write it is not merely the wrong noun -- it
    # describes a run that would have been a defect if it had happened.
    for message in _TWIN_MESSAGES.values():
        assert "The profile could not be written" not in message
        assert "cannot write the profile" not in message


def test_the_generators_words_still_name_the_profile_as_the_input() -> None:
    # The other half of the same rule: dropping the word everywhere would
    # leave the person with advice that names no file at all.
    assert "next to your profile" in _TWIN_FOLDER_MISSING
    assert "replaced your own profile" in _TWIN_WOULD_REPLACE
    assert "pointing back at the profile" in _TWIN_WOULD_REPLACE


def test_every_field_of_the_record_reaches_a_message() -> None:
    # A field nobody reads is a wording somebody will write, believe they
    # changed something, and ship. Each field is given a marker of its
    # own and every marker has to turn up.
    marked = errors.ArtifactWords(
        produced="PRODUCED-MARK",
        given="GIVEN-MARK",
        new_file="NEW-FILE-MARK",
        loss="LOSS-MARK.",
        mismatch="MISMATCH-MARK",
        published="PUBLISHED-MARK",
        working_holds="WORKING-HOLDS-MARK",
    )
    left_behind = [
        ("/d/t-twin.csv", errors.ON_DISK_NEW),
        ("/d/t-twin.csv.synthtwin-part-1", errors.ON_DISK_WORKING),
    ]
    composed = " ".join(
        [
            errors.rollback_failed([], _TWIN_DISK, marked),
            errors.rollback_failed([], left_behind, marked),
            errors.nothing_was_written([], left_behind, marked),
            errors.output_folder_missing("/reports", marked),
            errors.output_not_writable("/reports/out.csv", "why", marked),
            errors.output_would_replace_the_table("/d/p.json", marked),
        ]
    )
    for field in (
        "PRODUCED",
        "GIVEN",
        "NEW-FILE",
        "LOSS",
        "MISMATCH",
        "PUBLISHED",
        "WORKING-HOLDS",
    ):
        assert f"{field}-MARK" in composed, (
            f"nothing a person reads uses the {field} field, so changing "
            f"it would change nothing"
        )


# ---------------------------------------------------------------------------
# part 4 -- the thread-through is complete, read off the module itself
# ---------------------------------------------------------------------------

# The builders whose wording depends on which command is running. A call
# to one of these from a function that does not take the words is a
# message in one command's voice composed inside the other's run.
_WORD_TAKING = {
    "rollback_failed",
    # The sentence a stopped run ends with, which said "No new
    # DESCRIPTION was published" out of a `validate` run that had just
    # written a quality report and put an earlier one back (review item
    # P3-V4-F11). It is here for the same reason the four below are:
    # composed without the words, it names a file the running command
    # does not write.
    "nothing_was_written",
    "output_folder_missing",
    "output_not_writable",
    "output_would_replace_the_table",
    # The one-target transaction's own guarded-source refusal (plan
    # P3-D1). It takes the words for the same reason the four above do:
    # composed without them it would tell somebody in a stopped
    # `validate` run that writing THE DESCRIPTION would have replaced
    # one of its inputs, when the description is a file that command
    # never writes.
    "output_would_replace_an_input",
}

_TRANSACTION = ast.parse(
    pathlib.Path(writing.__file__).read_text(encoding="utf-8")
)


def _functions() -> "list[ast.FunctionDef]":
    """Every function defined at any depth in `writing.py`."""
    found: list[ast.FunctionDef] = []
    for node in ast.walk(_TRANSACTION):
        if isinstance(node, ast.FunctionDef):
            found = found + [node]
    return found


def _word_taking_calls(function: "ast.FunctionDef") -> "list[ast.Call]":
    """Every call in ``function`` to a builder whose wording varies."""
    found: list[ast.Call] = []
    for node in ast.walk(function):
        if not isinstance(node, ast.Call):
            continue
        target = node.func
        if not isinstance(target, ast.Attribute):
            continue
        holder = target.value
        if not isinstance(holder, ast.Name) or holder.id != "errors":
            continue
        if target.attr in _WORD_TAKING:
            found = found + [node]
    return found


def _hands_over_the_words(call: "ast.Call") -> bool:
    """True when this call actually passes ``words`` along.

    Both spellings count, because both are used: as the last positional
    argument, and as a named one. What does NOT count is leaving it out,
    which is the whole point -- a builder called without it composes the
    profiler's wording wherever the call happens to be running.
    """
    for given in call.args:
        if isinstance(given, ast.Name) and given.id == "words":
            return True
    for named in call.keywords:
        value = named.value
        named_words = named.arg == "words"
        if named_words and isinstance(value, ast.Name) and value.id == "words":
            return True
    return False


def _calls_a_word_taking_builder(function: "ast.FunctionDef") -> bool:
    return len(_word_taking_calls(function)) > 0


def _parameter_names(function: "ast.FunctionDef") -> "list[str]":
    spec = function.args
    given = spec.posonlyargs + spec.args + spec.kwonlyargs
    return [one.arg for one in given]


def test_every_function_that_composes_one_of_these_takes_the_words() -> None:
    missing = [
        function.name
        for function in _functions()
        if _calls_a_word_taking_builder(function)
        and "words" not in _parameter_names(function)
    ]
    assert not missing, (
        f"these functions in writing.py compose a refusal whose wording "
        f"differs between the two commands, but take no words to compose "
        f"it with, so they will speak in the profiler's voice inside a "
        f"generate run: {missing}"
    )


def test_every_call_site_hands_the_words_over() -> None:
    # Taking the words and USING them are two different things, and the
    # difference is invisible: a call that leaves them out still runs,
    # still composes a grammatical sentence, and still names the
    # profiler's files -- inside a generate run, on a line nobody looks
    # at twice. Ten of these calls sit in one function, so "the function
    # takes them" is not the property that matters.
    dropped = [
        f"{function.name}, line {call.lineno}"
        for function in _functions()
        for call in _word_taking_calls(function)
        if not _hands_over_the_words(call)
    ]
    assert not dropped, (
        f"these calls in writing.py compose a refusal without passing the "
        f"words along, so each one speaks in the profiler's voice whatever "
        f"command is running: {dropped}"
    )


def test_a_wording_site_is_actually_being_checked() -> None:
    # The floor under the two tests above. If nobody composes one of
    # these any more -- renamed, refactored away -- both pass by finding
    # nothing, which is the shape of a check that cannot fail.
    composing = [
        function.name
        for function in _functions()
        if _calls_a_word_taking_builder(function)
    ]
    calls = [
        call
        for function in _functions()
        for call in _word_taking_calls(function)
    ]
    assert len(composing) >= 5, (
        f"only {composing} compose one of these refusals; the completeness "
        f"tests above would be passing over an empty set"
    )
    assert len(calls) >= 10, (
        f"only {len(calls)} call sites were found; the call-site test "
        f"above would be passing over almost nothing"
    )


def test_only_the_public_entry_points_carry_a_default() -> None:
    # A default on an inside function is how one command's vocabulary
    # reaches the other command's message with nobody writing it down:
    # the caller forgets the argument, nothing complains, and the wrong
    # word ships. The two entry points a command actually calls carry the
    # only defaults, where the caller can see what it is getting.
    for function in _functions():
        names = _parameter_names(function)
        if "words" not in names:
            continue
        spec = function.args
        positional = spec.posonlyargs + spec.args
        defaults = dict(
            zip(
                [one.arg for one in positional[len(positional) - len(spec.defaults):]],
                spec.defaults,
                strict=True,
            )
        )
        has_default = "words" in defaults
        if function.name.startswith("_"):
            assert not has_default, (
                f"{function.name} is inside the transaction and defaults "
                f"its words, so a caller can forget them and get the "
                f"profiler's wording in a generate run"
            )
            continue
        assert has_default, (
            f"{function.name} is a public entry point and every caller "
            f"written before this parameter existed calls it without one"
        )
        given = defaults["words"]
        assert isinstance(given, ast.Attribute)
        assert given.attr == "PROFILE_WORDS", (
            f"{function.name} defaults to something other than the "
            f"profiler's words, so the profiler's messages have moved"
        )


# ---------------------------------------------------------------------------
# reachability: the sentences a real stopped run produces
# ---------------------------------------------------------------------------

TWIN_TEXT = "site,age\nA,41\nB,52\n"
REPORT_TEXT = "What this twin is, and what it is not.\n"


def _twin_targets(
    folder: pathlib.Path,
) -> "tuple[pathlib.Path, pathlib.Path]":
    return (folder / "clinic-twin.csv", folder / "clinic-twin-report.txt")


def test_a_stopped_generate_run_names_the_twin_not_the_profile(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Driven through the transaction itself, with one filesystem call
    # made to fail, exactly as the rest of the battery does it. What is
    # asserted is the sentence the person would read.
    twin, report = _twin_targets(tmp_path)

    def refuse(self: pathlib.Path, *rest: object, **named: object) -> None:
        raise OSError(30, "Read-only file system")

    monkeypatch.setattr(pathlib.Path, "write_text", refuse)
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_both_files(
            twin, report, TWIN_TEXT, REPORT_TEXT, words=errors.TWIN_WORDS
        )
    message = f"{stopped.value}"
    assert "The twin could not be written to" in message
    assert "The profile could not be written to" not in message
    assert not twin.exists() and not report.exists()


def test_the_same_stop_in_a_profile_run_still_names_the_profile(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The other side of the same seam. The profiler's own run is what the
    # certified battery covers, and this asserts the words did not move
    # under it when the generator's were added.
    first = tmp_path / "clinic-profile.json"
    second = tmp_path / "clinic-profile.txt"

    def refuse(self: pathlib.Path, *rest: object, **named: object) -> None:
        raise OSError(30, "Read-only file system")

    monkeypatch.setattr(pathlib.Path, "write_text", refuse)
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_both_files(first, second, "{}\n", "summary\n")
    assert "The profile could not be written to" in f"{stopped.value}"


def test_a_generate_run_refuses_to_write_over_the_profile_it_was_given(
    tmp_path: pathlib.Path
) -> None:
    # `table_path` is the file the command was handed, whichever command
    # it is. Here it is the profile document, and the refusal has to say
    # so: telling somebody their TABLE was nearly destroyed by a command
    # that never opened one sends them to check a file that is not
    # involved.
    document = tmp_path / "clinic-profile.json"
    document.write_text('{"profile_version": 4}\n', encoding="utf-8", newline="\n")
    report = tmp_path / "clinic-twin-report.txt"
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_both_files(
            document,
            report,
            TWIN_TEXT,
            REPORT_TEXT,
            document,
            words=errors.TWIN_WORDS,
        )
    message = f"{stopped.value}"
    assert "replaced your own profile" in message
    assert "table" not in message.casefold()
    assert document.read_text(encoding="utf-8") == '{"profile_version": 4}\n'
    assert not report.exists()


def test_a_generate_run_stopped_mid_move_says_why_the_pair_must_match(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The rollback wording, reached the way it is really reached: a
    # failure the transaction did not compose, arriving once the renaming
    # had begun. The sentence lands in the DiskState rather than in the
    # message, because a failure of that kind travels to the caller
    # untouched (review item P1-R7-F1).
    twin, report = _twin_targets(tmp_path)
    real = pathlib.Path.replace

    def give_out(self: pathlib.Path, other: object) -> object:
        raise MemoryError("not enough memory")

    state = writing.DiskState()
    monkeypatch.setattr(pathlib.Path, "replace", give_out)
    with pytest.raises(MemoryError):
        writing.write_both_files(
            twin,
            report,
            TWIN_TEXT,
            REPORT_TEXT,
            state=state,
            words=errors.TWIN_WORDS,
        )
    monkeypatch.setattr(pathlib.Path, "replace", real)
    assert "a report from one run does not describe the twin" in state.sentence
    assert "a profile and a summary" not in state.sentence
    assert "table" not in state.sentence.casefold()
