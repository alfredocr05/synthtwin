"""P1-R8-F1: the write transaction has no unguarded seam left.

THE DEFECT. The round-7 repair moved the failure handler in `_commit`
"to the first line" and recorded the remainder as one bytecode boundary.
It was not one boundary and it was not the whole remainder:

* `progress = _Progress()` ran BEFORE the `try`, at a moment when both
  working files existed and held the complete real-derived text. A stop
  there left both on disk and left the disk sentence empty;
* the handler read `target`, `summary_target`, `new_profile`,
  `new_summary` and `both`, each of which was assigned INSIDE the `try`
  it was meant to guard. A stop at any of those assignments replaced the
  person's failure with `UnboundLocalError`, so the reason the run
  stopped was lost as well as the files;
* `except ProfileError: raise` treated a TYPE as proof that a cleanup
  had already run. `ProfileError` is the package's ordinary refusal and
  any code in the transaction's reach can raise one; an unexpected one
  from a rename went straight out with both parts still on disk;
* a second stop arriving during the cleanup replaced the first, so the
  caller lost the failure it had advice for;
* a stop after both renames had finished reported a failed run with no
  state at all, although both files were written and correct.

THE SHAPE THIS TESTS. No statement may run between "a file synthtwin
made is on disk" and "a handler that will clear it away and name it is
in force". `write_both_files` now binds everything its handler needs
BEFORE the guard -- which is possible only there, because at that moment
nothing of synthtwin's making exists on disk -- and does all the rest
inside it, the renaming included. A context manager whose entry made
the claim and whose exit did the reporting would express the same rule;
it is not available here, because the offline scanner refuses
`__enter__` and `__exit__` (it refuses every double-underscore name
outside a short allowed list), so the guard is a plain `try` whose body
is the whole of the work.

HOW IT IS CHECKED. Not by reading the source: a failure is injected at
every statement boundary the transaction executes, by raising from a
line-event trace function, and the same three questions are asked after
each one. Did the person's own failure reach them unchanged? Is every
working file that survived NAMED to them? Is neither output left
holding anything but its old text or its new text? The sweep runs with
and without an earlier profile in place, so the set-aside path is swept
too.
"""

import pathlib
import sys
import types

import pytest

import fixtures
from synthtwin import errors, profile, writing
from synthtwin.cli import main

PROFILE_TEXT = '{\n  "profile_version": 2,\n  "note": "PROFILE-DERIVED"\n}\n'
SUMMARY_TEXT = "A summary of the table, for a person to read.\n"
OLD_PROFILE = "last week's profile\n"
OLD_SUMMARY = "last week's summary\n"

# The filename every code object compiled from the module holding the
# write transaction carries, taken from one of that module's own
# functions. That module is `writing.py` since plan P2-D1 moved the
# transaction out of `profile.py`, which imports the reader's own table
# type; the name is READ OFF the function rather than written here, so
# the move did not have to be transcribed into this test and a later one
# will not have to be either.
#
# It used to be rebuilt as `str(Path(profile.__file__).resolve())`, and
# the two are not the same string on every platform. On Windows the
# hosted run imported the package through a path spelled one way while
# `Path.resolve()` handed back the spelling the disk itself keeps, and
# the `!=` in `_call` below then rejected every frame of profile.py: the
# tracer never raised, nothing was ever injected, and both parts of the
# sweep passed while asserting nothing whatever. The floor at the end of
# each of them is what turned that into a red test rather than a silent
# one -- `only 0 boundaries were injected into` -- and it is the reason
# those floors are there.
#
# Reading the name off a code object removes the mismatch instead of
# papering over it with a case-blind or resolved comparison: this IS,
# by construction, what `frame.f_code.co_filename` holds for every
# function in the module, on every platform and every interpreter.
_SOURCE = writing.write_both_files.__code__.co_filename

# The two frames that hold the guard and everything the guard's handler
# depends on. The review's required closure names the prologue and every
# setup assignment, and these are where they live.
_GUARD_FRAMES = ("write_both_files", "_move_into_place")


def _outputs(folder: pathlib.Path) -> "tuple[pathlib.Path, pathlib.Path]":
    return (folder / "clinic-profile.json", folder / "clinic-profile.txt")


def _working_files(folder: pathlib.Path) -> "list[pathlib.Path]":
    """Every working file left in ``folder``, sorted by name."""
    found = [
        entry
        for entry in folder.iterdir()
        if profile.PART_SUFFIX in entry.name or profile.KEPT_SUFFIX in entry.name
    ]
    return sorted(found, key=lambda entry: entry.name)


def _what_escapes(
    work: "object", *args: object, **named: object
) -> "BaseException | None":
    """Run ``work`` and hand back whatever came out of it, or None.

    `pytest.raises` is the right tool when the expected failure is an
    Exception. It is the wrong one here: several of these tests expect a
    KeyboardInterrupt, and a regression that raises a DIFFERENT one
    sends that interrupt out of the test body, where pytest reads it as
    the person stopping the whole run and abandons every remaining test
    and every teardown. Catching it here turns a regression into one red
    test with a message.
    """
    try:
        work(*args, **named)  # type: ignore[operator]
    except BaseException as failed:  # noqa: BLE001 -- the point of the test
        return failed
    return None


def _interrupt_the_unlink_under(
    monkeypatch: pytest.MonkeyPatch, folder: pathlib.Path
) -> None:
    """Make every delete inside ``folder`` raise a KeyboardInterrupt.

    Bounded to the folder on purpose. `Path.unlink` is what pytest uses
    to clear its own temporary directories, so an unbounded patch that
    outlived a test would stop the session in its own housekeeping.
    """
    real = pathlib.Path.unlink
    inside = f"{folder}"

    def interrupted(self: pathlib.Path, missing_ok: bool = False) -> None:
        if f"{self}".startswith(inside):
            raise KeyboardInterrupt()
        real(self, missing_ok=missing_ok)

    monkeypatch.setattr(pathlib.Path, "unlink", interrupted)


class _Stop:
    """Raise one failure at the nth statement boundary inside profile.py.

    A local trace function that raises makes the traced frame raise at
    exactly that line, which is the finest boundary a test can inject at
    without rewriting bytecode. Only frames belonging to profile.py are
    traced, and only one failure is ever injected: the flag is set before
    the raise, so the cleanup the injection triggers runs untouched.
    """

    def __init__(
        self, nth: int, failure: BaseException, frames: "tuple[str, ...] | None"
    ) -> None:
        self.nth = nth
        self.failure = failure
        self.frames = frames
        self.seen = 0
        self.fired = False

    def _line(
        self, frame: types.FrameType, event: str, _arg: object
    ) -> "object":
        if event != "line" or self.fired:
            return self._line
        self.seen = self.seen + 1
        if self.seen == self.nth:
            self.fired = True
            raise self.failure
        return self._line

    def _call(
        self, frame: types.FrameType, _event: str, _arg: object
    ) -> "object":
        if frame.f_code.co_filename != _SOURCE:
            return None
        if self.frames is not None and frame.f_code.co_name not in self.frames:
            return None
        return self._line


def _run_with_a_stop(
    folder: pathlib.Path,
    nth: int,
    failure: BaseException,
    earlier: bool,
    frames: "tuple[str, ...] | None" = None,
) -> "tuple[BaseException | None, profile.DiskState, _Stop]":
    """One whole transaction with one injected stop; report what happened."""
    first, second = _outputs(folder)
    if earlier:
        first.write_text(OLD_PROFILE, encoding="utf-8", newline="")
        second.write_text(OLD_SUMMARY, encoding="utf-8", newline="")
    state = profile.DiskState()
    stop = _Stop(nth, failure, frames)
    caught: BaseException | None = None
    sys.settrace(stop._call)
    try:
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )
    except BaseException as failed:  # noqa: BLE001 -- the point of the test
        caught = failed
    finally:
        sys.settrace(None)
    return (caught, state, stop)


def _check_one_stop(
    folder: pathlib.Path,
    caught: "BaseException | None",
    state: profile.DiskState,
    failure: BaseException,
    earlier: bool,
    where: str,
) -> None:
    """The questions asked after one injected stop."""
    first, second = _outputs(folder)

    # 1. The person's own failure reached them, as itself. An
    #    UnboundLocalError here is the round-7 defect exactly.
    if caught is not None:
        assert caught is failure, (
            f"{where}: the injected failure was replaced by "
            f"{type(caught).__name__}: {caught}"
        )

    # 2. Every working file that survived is NAMED to them -- in the
    #    sentence for a stop that undid the run, or in `left_behind` for
    #    a stop that arrived after both files were written.
    told = state.sentence
    if state.left_behind:
        told = f"{told} {state.left_behind}"
    for leftover in _working_files(folder):
        assert f"{leftover}" in told, (
            f"{where}: {leftover.name} survived and is named nowhere. It "
            f"holds {leftover.read_text(encoding='utf-8')!r}"
        )

    # 3. Neither output holds anything but what it held or what this run
    #    wrote. A rename is one filesystem step, so a half file here
    #    would mean something wrote to an output name directly.
    allowed_first = [PROFILE_TEXT] + ([OLD_PROFILE] if earlier else [])
    allowed_second = [SUMMARY_TEXT] + ([OLD_SUMMARY] if earlier else [])
    if first.exists():
        assert first.read_text(encoding="utf-8") in allowed_first, (
            f"{where}: the profile's name holds neither the file that was "
            f"there before nor the one this run wrote"
        )
    if second.exists():
        assert second.read_text(encoding="utf-8") in allowed_second, (
            f"{where}: the summary's name holds neither the file that was "
            f"there before nor the one this run wrote"
        )

    # 3b. And the reader's own earlier profile is still SOMEWHERE until
    #     the new one is really in place. It is the one file under these
    #     names that this run did not produce, so no failure path may
    #     delete it -- only move it and name where it went.
    installed = (
        first.exists() and first.read_text(encoding="utf-8") == PROFILE_TEXT
    )
    if earlier and not installed:
        survivors = [first] + _working_files(folder)
        assert any(
            place.exists() and place.read_text(encoding="utf-8") == OLD_PROFILE
            for place in survivors
        ), (
            f"{where}: the profile from before this run is gone and the "
            f"new one is not in its place"
        )

    # 4. A run reported as finished really did finish.
    if state.both_files_written:
        assert first.read_text(encoding="utf-8") == PROFILE_TEXT
        assert second.read_text(encoding="utf-8") == SUMMARY_TEXT

    # 5. And nothing may be claimed and reported at once.
    assert not (state.sentence and state.both_files_written), (
        f"{where}: the run cannot both have published nothing and have "
        f"written both files"
    )


# ---------------------------------------------------------------------
# 0. the injector is aimed at the module it is supposed to trace
# ---------------------------------------------------------------------


def test_the_injector_recognizes_the_frames_it_has_to_stop(
    tmp_path: pathlib.Path,
) -> None:
    """The name `_call` compares against is a name real frames carry.

    Everything below rests on this one string comparison, and when it
    matched nothing on the hosted Windows runs the whole of section 1
    passed without injecting a single failure. The floors at the end of
    those two tests caught it, but they say only that the count was
    zero; this says which comparison produced the zero, so the next
    person reads a diagnosis instead of a symptom.
    """
    assert _SOURCE.endswith("writing.py"), (
        f"the injector is aimed at {_SOURCE!r}, which is not the module "
        f"holding the write transaction"
    )
    assert writing._move_into_place.__code__.co_filename == _SOURCE, (
        "both frames the guard lives in must be recognized, not just one"
    )
    first, second = _outputs(tmp_path)
    caught, _state, stop = _run_with_a_stop(
        tmp_path, 1, MemoryError("injected"), False, _GUARD_FRAMES
    )
    assert stop.fired, (
        "the very first statement of the transaction was not traced, so "
        "no failure can be injected anywhere and every check below is "
        "vacuous"
    )
    assert isinstance(caught, MemoryError)
    assert not first.exists() and not second.exists()


# ---------------------------------------------------------------------
# 1. the sweep: every statement boundary, all three failure kinds
# ---------------------------------------------------------------------


@pytest.mark.parametrize(
    "make_failure",
    [
        lambda: MemoryError("injected"),
        lambda: KeyboardInterrupt(),
        lambda: SystemExit(1),
    ],
    ids=["memory", "ctrl-c", "exit"],
)
@pytest.mark.parametrize("earlier", [False, True], ids=["fresh", "replacing"])
def test_a_stop_at_every_boundary_of_the_guard_is_covered(
    tmp_path: pathlib.Path,
    make_failure: "object",
    earlier: bool,
) -> None:
    # The prologue and every setup assignment of the transaction and of
    # the renaming step, one statement at a time. Before the repair, a
    # stop at the transaction's own first line after the writes left both
    # parts on disk with an empty sentence, and a stop at any of five
    # assignments turned the failure into UnboundLocalError.
    nth = 1
    ran_to_the_end = 0
    last_fired = 0
    while nth <= 400:
        folder = tmp_path / f"run-{nth}"
        folder.mkdir()
        failure = make_failure()  # type: ignore[operator]
        caught, state, stop = _run_with_a_stop(
            folder, nth, failure, earlier, _GUARD_FRAMES
        )
        if not stop.fired:
            # Past the last boundary the run executes: the transaction
            # finished, so there is nothing left to inject into.
            ran_to_the_end = ran_to_the_end + 1
            assert caught is None
            assert _working_files(folder) == []
            if ran_to_the_end > 2:
                break
            nth = nth + 1
            continue
        last_fired = nth
        _check_one_stop(
            folder, caught, state, failure, earlier, f"boundary {nth}"
        )
        nth = nth + 1
    assert ran_to_the_end > 0, "the sweep never reached the end of the run"
    # A floor on the sweep itself. A tracer that quietly stopped tracing
    # would make every assertion above vacuous, and a test that passes
    # by checking nothing is worse than no test.
    assert last_fired >= 50, (
        f"only {last_fired} boundaries were injected into; the two frames "
        f"holding the guard execute more than that"
    )


def test_a_stop_anywhere_in_the_module_is_covered_too(
    tmp_path: pathlib.Path,
) -> None:
    # The same sweep widened to every function of profile.py the
    # transaction calls -- the claim of a working name, the writes, the
    # renames, the cleanup helpers -- so that the guarantee is about the
    # work and not only about the two frames that hold the guard.
    nth = 1
    ran_to_the_end = 0
    last_fired = 0
    while nth <= 700:
        folder = tmp_path / f"run-{nth}"
        folder.mkdir()
        failure = MemoryError("injected")
        caught, state, stop = _run_with_a_stop(folder, nth, failure, True, None)
        if not stop.fired:
            ran_to_the_end = ran_to_the_end + 1
            assert caught is None
            if ran_to_the_end > 2:
                break
            nth = nth + 1
            continue
        last_fired = nth
        _check_one_stop(
            folder, caught, state, failure, True, f"module boundary {nth}"
        )
        nth = nth + 1
    assert ran_to_the_end > 0, "the sweep never reached the end of the run"
    assert last_fired >= 400, (
        f"only {last_fired} boundaries were injected into; a run that "
        f"replaces an earlier profile executes more than that"
    )


# ---------------------------------------------------------------------
# 2. the two boundaries the review named, on their own
# ---------------------------------------------------------------------


def test_a_stop_at_the_first_boundary_after_the_writes_names_both_parts(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The reviewer's own probe: a stop at the entry of the renaming step,
    # when both working files exist and hold the complete real-derived
    # text. It used to leave both on disk with `state.sentence` empty.
    first, second = _outputs(tmp_path)
    failure = MemoryError("injected at the renaming step")

    def refuse(*_args: object, **_kwargs: object) -> "list[str]":
        raise failure

    monkeypatch.setattr(writing, "_move_into_place", refuse)
    state = profile.DiskState()
    with pytest.raises(MemoryError) as caught:
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert caught.value is failure
    assert _working_files(tmp_path) == [], (
        "both working files held the whole description at that moment"
    )
    assert "PROFILE-DERIVED" not in state.sentence
    assert f"{first}" in state.sentence and f"{second}" in state.sentence
    assert "No new description was published" in state.sentence
    assert "There is nothing left to clear up" in state.sentence


def test_a_working_file_left_at_that_boundary_is_named(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    failure = MemoryError("injected at the renaming step")

    def refuse(*_args: object, **_kwargs: object) -> "list[str]":
        raise failure

    real_unlink = pathlib.Path.unlink

    def stubborn(self: pathlib.Path, missing_ok: bool = False) -> None:
        if f"{self}" == f"{first_part}":
            raise PermissionError(13, "Operation not permitted")
        real_unlink(self, missing_ok=missing_ok)

    monkeypatch.setattr(writing, "_move_into_place", refuse)
    monkeypatch.setattr(pathlib.Path, "unlink", stubborn)
    state = profile.DiskState()
    with pytest.raises(MemoryError):
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert first_part.read_text(encoding="utf-8") == PROFILE_TEXT
    assert f"{first_part}" in state.sentence
    assert "holds text taken from your table" in state.sentence


# ---------------------------------------------------------------------
# 3. an unexpected ProfileError is not proof that a cleanup ran
# ---------------------------------------------------------------------


def _break_the_rename_of(
    monkeypatch: pytest.MonkeyPatch,
    doomed: pathlib.Path,
    failure: BaseException,
) -> None:
    real = pathlib.Path.replace
    wanted = f"{doomed}"

    def brittle(self: pathlib.Path, target: object) -> pathlib.Path:
        if f"{self}" == wanted:
            raise failure
        return real(self, target)  # type: ignore[arg-type]

    monkeypatch.setattr(pathlib.Path, "replace", brittle)


def test_an_unexpected_profile_error_from_a_rename_gets_the_full_cleanup(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The review's second probe. A ProfileError the transaction did not
    # compose used to be waved through by `except ProfileError: raise`,
    # which left both parts on disk and the sentence empty.
    first, second = _outputs(tmp_path)
    first_part = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    failure = errors.ProfileError("a refusal from somewhere else entirely")
    _break_the_rename_of(monkeypatch, first_part, failure)
    state = profile.DiskState()
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert caught.value is failure, "the failure must reach the caller as itself"
    assert f"{caught.value}" == "a refusal from somewhere else entirely", (
        "and with its own message, not one this module composed for it"
    )
    assert _working_files(tmp_path) == []
    assert f"{first}" in state.sentence and f"{second}" in state.sentence


def test_a_refusal_the_transaction_composed_still_says_it_once(
    tmp_path: pathlib.Path
) -> None:
    # The other direction, and the property the type distinction exists
    # to keep: a refusal built inside the transaction has already cleaned
    # up and already names every file, so no second sentence is added.
    first, second = _outputs(tmp_path)
    occupied = pathlib.Path(f"{first}{profile.PART_SUFFIX}-1")
    number = 1
    while number <= profile.WORKING_NAME_ATTEMPTS:
        pathlib.Path(f"{first}{profile.PART_SUFFIX}-{number}").write_text(
            "not synthtwin's\n", encoding="utf-8"
        )
        number = number + 1
    state = profile.DiskState()
    with pytest.raises(errors.ProfileError) as caught:
        profile.write_both_files(
            first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
        )

    assert isinstance(caught.value, errors.TransactionRefusal)
    assert state.sentence == "", "the message already carries the state"
    assert f"{first}" in f"{caught.value}"
    assert occupied.read_text(encoding="utf-8") == "not synthtwin's\n", (
        "a file synthtwin did not create is never removed"
    )


# ---------------------------------------------------------------------
# 4. a second stop during the cleanup does not replace the first
# ---------------------------------------------------------------------


def test_a_second_stop_during_the_cleanup_keeps_the_original_failure(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # The person presses Ctrl-C while the first failure is being
    # described. The failure the caller has advice for is the first one,
    # so that is what continues; before this, the second replaced it.
    first, second = _outputs(tmp_path)
    second_part = pathlib.Path(f"{second}{profile.PART_SUFFIX}-1")
    original = MemoryError("the first failure")
    real_write = pathlib.Path.write_text

    def brittle(
        self: pathlib.Path,
        data: str,
        encoding: "str | None" = None,
        errors_: "str | None" = None,
        newline: "str | None" = None,
    ) -> int:
        if f"{self}" == f"{second_part}":
            raise original
        return real_write(self, data, encoding=encoding, newline=newline)

    monkeypatch.setattr(pathlib.Path, "write_text", brittle)
    _interrupt_the_unlink_under(monkeypatch, tmp_path)
    state = profile.DiskState()
    # Caught by hand rather than with `pytest.raises`: a regression here
    # sends a KeyboardInterrupt out of the test, and pytest treats one
    # of those as the person stopping the whole run.
    caught = _what_escapes(
        profile.write_both_files,
        first,
        second,
        PROFILE_TEXT,
        SUMMARY_TEXT,
        state=state,
    )

    assert caught is original, (
        f"the second stop must not become what the caller is told about, "
        f"and {type(caught).__name__} did"
    )
    # And the stated bound: the sentence is what is lost, whole.
    assert state.sentence == ""


# ---------------------------------------------------------------------
# 5. a stop after both files are written is not reported as a rollback
# ---------------------------------------------------------------------


def test_a_stop_after_both_renames_reports_a_finished_write(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    # Both files are in place and correct; the run stops before it can
    # say so. It used to say nothing at all, and describing it as a
    # rollback that failed would send the reader looking for damage that
    # is not there.
    first, second = _outputs(tmp_path)
    first.write_text(OLD_PROFILE, encoding="utf-8", newline="")
    kept = pathlib.Path(f"{first}{profile.KEPT_SUFFIX}-1")

    _interrupt_the_unlink_under(monkeypatch, tmp_path)
    state = profile.DiskState()
    caught = _what_escapes(
        profile.write_both_files,
        first,
        second,
        PROFILE_TEXT,
        SUMMARY_TEXT,
        state=state,
    )
    assert isinstance(caught, KeyboardInterrupt)

    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT
    assert state.both_files_written is True
    assert state.sentence == "", (
        "there was nothing to put back, so nothing may say there was"
    )
    assert state.left_behind == f"{kept}"
    assert kept.read_text(encoding="utf-8") == OLD_PROFILE, (
        "the earlier profile is the one file no failure path may delete"
    )


def test_the_command_says_both_files_were_written_and_names_the_leftover(
    tmp_path: pathlib.Path,
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    # The whole of it through the words a person would type.
    table = fixtures.write(
        tmp_path,
        "clinic.csv",
        fixtures.single_column_table("age", ["41"] * 30),
    )
    first, _second = _outputs(tmp_path)
    first.write_text(OLD_PROFILE, encoding="utf-8", newline="")
    kept = pathlib.Path(f"{first}{profile.KEPT_SUFFIX}-1")

    _interrupt_the_unlink_under(monkeypatch, tmp_path)
    caught = _what_escapes(main, ["profile", f"{table}"])
    told = capsys.readouterr()
    assert isinstance(caught, KeyboardInterrupt)

    assert "Written:" in told.out, (
        "both files are on disk and correct; saying nothing would leave "
        "the reader believing nothing was written"
    )
    assert f"{kept}" in told.err
    assert "keep" in told.err and "delete" in told.err
    assert "could not put things back" not in told.err, (
        "nothing needed putting back, so nothing may say it did"
    )


# ---------------------------------------------------------------------
# 6. and the ordinary run is still ordinary
# ---------------------------------------------------------------------


def test_a_plain_table_still_profiles_cleanly_through_the_command(
    tmp_path: pathlib.Path, capsys: pytest.CaptureFixture[str]
) -> None:
    table = fixtures.write(
        tmp_path,
        "clinic.csv",
        fixtures.single_column_table("age", [f"{40 + n % 20}" for n in range(60)]),
    )
    assert main(["profile", f"{table}"]) == 0
    told = capsys.readouterr()
    first, second = _outputs(tmp_path)

    assert "Written:" in told.out
    assert told.err == ""
    assert first.exists() and second.exists()
    assert _working_files(tmp_path) == []
    assert sorted(entry.name for entry in tmp_path.iterdir()) == [
        "clinic-profile.json",
        "clinic-profile.txt",
        "clinic.csv",
    ]


def test_an_ordinary_run_leaves_every_field_of_the_record_empty(
    tmp_path: pathlib.Path,
) -> None:
    first, second = _outputs(tmp_path)
    state = profile.DiskState()
    left = profile.write_both_files(
        first, second, PROFILE_TEXT, SUMMARY_TEXT, state=state
    )
    assert left == []
    assert state.sentence == ""
    assert state.both_files_written is False, (
        "the record is for a run that stopped; a run that returned says "
        "so by returning"
    )
    assert state.left_behind == ""
    assert first.read_text(encoding="utf-8") == PROFILE_TEXT
    assert second.read_text(encoding="utf-8") == SUMMARY_TEXT
