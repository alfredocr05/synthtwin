"""The one-target transaction: the proof matrix, and the fault sweep.

REVIEW ITEM P3-V1-F12. Plan P3-D1 requires two things of the
generalized transaction, and neither existed:

* THE PROOF MATRIX. "The quality report may not resolve onto the
  profile or the measured file by lexical path, by resolved path, by
  link, by alias, or between-check-and-write substitution; EACH INPUT
  CROSSED WITH EACH ALIAS CLASS IS A TEST, extending the shipped
  same-file machinery from one guarded source to a set." What was
  shipped was two symlink cases and one lexical case, all through the
  command, and one direct call whose assertion could not fail -- the
  generic special-entry refusal it really met carries the word
  "description" inside an unrelated sentence, so asserting that the
  noun appears proved nothing. Both halves are repaired here: the
  transaction now answers the source-aware question FIRST, and the
  matrix below is every input against every class.
* THE FAULT SWEEP. "The statement and opcode fault-injection
  measurement is RE-RUN against the generalized code, exactly as P2-D10
  required when the transaction moved modules." The shipped sweep names
  `write_both_files` and `_move_into_place` and reaches neither of the
  one-target functions. The sweep at the end of this file is the same
  instrument -- a failure injected at every statement boundary the
  transaction executes -- aimed at `write_one_file` and
  `_move_one_into_place`, asking the same questions after each stop.

Every fixture is built at test time; no data-format file enters the
repository (plan D13).
"""

import os
import pathlib
import sys
import types

import pytest

from synthtwin import errors, writing

DESCRIPTION_TEXT = '{\n  "profile_version": 4,\n  "note": "DESCRIPTION"\n}\n'
MEASURED_TEXT = "reading\n1\n2\n3\n"
REPORT_TEXT = "the quality report, for a person to read\n"
OLD_REPORT = "last week's quality report\n"

# The two inputs a check is handed, with the noun each refusal has to
# call it by. They are not interchangeable to the person reading the
# message: one is the description the verdicts came from and the other
# may be their own table.
INPUTS = (
    ("description", errors.INPUT_DESCRIPTION),
    ("measured", errors.INPUT_MEASURED_FILE),
)


def _inputs(folder: pathlib.Path) -> "dict[str, pathlib.Path]":
    """The two files a check reads, written into ``folder``."""
    description = folder / "clinic-profile.json"
    # The line ending is fixed rather than left to the platform: a file
    # named like a description has to be the same bytes everywhere, and
    # `test_description_line_endings.py` holds every test to it.
    description.write_text(DESCRIPTION_TEXT, encoding="utf-8", newline="\n")
    measured = folder / "clinic-twin.csv"
    measured.write_text(MEASURED_TEXT, encoding="utf-8", newline="\n")
    return {"description": description, "measured": measured}


def _guarded(
    places: "dict[str, pathlib.Path]",
) -> "list[tuple[pathlib.Path, str]]":
    """Both inputs with their nouns, as the command hands them over."""
    return [
        (places["description"], errors.INPUT_DESCRIPTION),
        (places["measured"], errors.INPUT_MEASURED_FILE),
    ]


# -- the alias classes, one builder each -------------------------------
#
# Each returns the OUTPUT NAME to hand the transaction, having set up
# whatever makes that name lead back to the input. A class that cannot
# be built on this host returns None and the matrix says so by name
# rather than passing quietly.


def _lexical(folder: pathlib.Path, source: pathlib.Path) -> "pathlib.Path | None":
    """The output name IS the input's name, spelled the same way."""
    return source


def _resolved(folder: pathlib.Path, source: pathlib.Path) -> "pathlib.Path | None":
    """The output name reaches the input through a link in the folder."""
    inside = folder / "by-another-route"
    try:
        inside.symlink_to(folder, target_is_directory=True)
    except OSError:
        return None
    return inside / source.name


def _link(folder: pathlib.Path, source: pathlib.Path) -> "pathlib.Path | None":
    """A symbolic link at the output name, pointing at the input."""
    target = folder / "clinic-twin-quality.txt"
    try:
        target.symlink_to(source)
    except OSError:
        return None
    return target


def _hardlink(folder: pathlib.Path, source: pathlib.Path) -> "pathlib.Path | None":
    """A second NAME for the input's own file, with no link to follow.

    The resolved paths differ and neither is a symbolic link, so only
    the filesystem's own identity settles this one -- which is the rule
    `is_the_same_file` keeps for exactly this case.
    """
    target = folder / "clinic-twin-quality.txt"
    try:
        os.link(source, target)
    except OSError:
        return None
    return target


def _case_folded(
    folder: pathlib.Path, source: pathlib.Path
) -> "pathlib.Path | None":
    """The input's own name spelled in capitals.

    On a folding filesystem the two names ARE one file; on a
    case-sensitive one they are two, and synthtwin refuses anyway, for
    the reason `is_the_same_file` states: refusing a pair that really is
    two files costs a re-run, and missing one costs the file.
    """
    return folder / source.name.upper()


ALIAS_CLASSES = (
    ("lexical", _lexical),
    ("resolved", _resolved),
    ("link", _link),
    ("hardlink", _hardlink),
    ("case-fold", _case_folded),
)


@pytest.mark.parametrize("which,noun", INPUTS, ids=[name for name, _n in INPUTS])
@pytest.mark.parametrize(
    "alias,build", ALIAS_CLASSES, ids=[name for name, _b in ALIAS_CLASSES]
)
def test_the_report_may_not_land_on_either_input_by_any_alias(
    tmp_path: pathlib.Path,
    which: str,
    noun: str,
    alias: str,
    build: "object",
) -> None:
    """Each input crossed with each alias class, as plan P3-D1 requires.

    Three things are asserted after every refusal, because a refusal
    that stops the run and destroys the file is not a refusal:

    * the run stopped, with the transaction's own refusal;
    * the message says WHICH of the two inputs it caught, in that
      input's own noun and in the sentence that says the write would
      have replaced it -- not merely somewhere in the prose, which the
      generic special-entry refusal satisfies by accident;
    * the input still holds exactly its own bytes.
    """
    folder = tmp_path / f"{which}-{alias}"
    folder.mkdir()
    places = _inputs(folder)
    source = places[which]
    before = source.read_bytes()
    target = build(folder, source)  # type: ignore[operator]
    if target is None:
        pytest.skip(f"this host cannot build the {alias} alias")
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_one_file(
            target,
            REPORT_TEXT,
            sources=_guarded(places),
            words=errors.QUALITY_WORDS,
        )
    said = f"{stopped.value}"
    assert f"replaced the {noun}" in said, (
        f"the {alias} alias of the {which} was refused, and the refusal "
        f"does not say which of the two inputs it caught: {said}"
    )
    assert source.read_bytes() == before
    assert REPORT_TEXT not in source.read_text(encoding="utf-8")


def test_the_refusal_names_the_input_and_not_merely_the_special_entry(
    tmp_path: pathlib.Path,
) -> None:
    """The assertion the shipped direct test could not make.

    A link at the output name pointing back at the description is BOTH a
    special entry and an input. The transaction used to answer the
    plain-file question first, and its message -- true, and about a pipe
    or a device -- contains the word "description" inside an unrelated
    clause, so a test asserting that the noun appeared passed while the
    refusal it asserted about was never reached. This distinguishes
    them: the special-entry sentence must be ABSENT.
    """
    folder = tmp_path / "which-refusal"
    folder.mkdir()
    places = _inputs(folder)
    target = folder / "clinic-twin-quality.txt"
    target.symlink_to(places["description"])
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_one_file(
            target,
            REPORT_TEXT,
            sources=_guarded(places),
            words=errors.QUALITY_WORDS,
        )
    said = f"{stopped.value}"
    assert f"replaced the {errors.INPUT_DESCRIPTION}" in said
    assert "not an ordinary file" not in said, (
        "the generic special-entry refusal answered first, so the person "
        "is told a pipe might be in the way instead of being told the "
        "name they gave leads to the description they are checking"
    )


def test_a_special_entry_that_is_not_an_input_still_meets_its_refusal(
    tmp_path: pathlib.Path,
) -> None:
    """The other half of the swap, which the swap may not cost.

    Asking the source-aware question first must not stop the plain-file
    question being asked at all: a link at the output name pointing
    somewhere harmless is still not a place a real-derived report may
    go.
    """
    folder = tmp_path / "harmless-link"
    folder.mkdir()
    places = _inputs(folder)
    elsewhere = folder / "somewhere-else.txt"
    elsewhere.write_text("not an input\n", encoding="utf-8")
    target = folder / "clinic-twin-quality.txt"
    target.symlink_to(elsewhere)
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_one_file(
            target,
            REPORT_TEXT,
            sources=_guarded(places),
            words=errors.QUALITY_WORDS,
        )
    assert "not an ordinary file" in f"{stopped.value}"
    assert elsewhere.read_text(encoding="utf-8") == "not an input\n"


def test_a_substitution_between_the_check_and_the_write_is_undone(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """The class no check made beforehand can catch (plan P3-D1, V1.3).

    Both names are asked about before the write, and two names that do
    not exist yet can still be one file underneath. So the question is
    asked AGAIN once the report really is at its output name -- and here
    the output name is MADE into a second name for the description
    between the two, by a patch standing where another program on the
    machine would stand.

    What must then be true is not only that the run stops: the
    description has to still hold its own bytes, and the report must not
    be left sitting at the output name as though the run had finished.
    """
    folder = tmp_path / "substituted"
    folder.mkdir()
    places = _inputs(folder)
    description = places["description"]
    target = folder / "clinic-twin-quality.txt"
    before = description.read_bytes()
    real_replace = pathlib.Path.replace

    def substituted(
        self: pathlib.Path, other: "str | os.PathLike[str]"
    ) -> pathlib.Path:
        landed = real_replace(self, other)
        if f"{other}" == f"{target}":
            # The instant after the report reached its name, and the
            # instant the second question exists to ask about: the name
            # is now a second name for the description.
            target.unlink()
            os.link(description, target)
        return landed

    monkeypatch.setattr(pathlib.Path, "replace", substituted)
    with pytest.raises(errors.ProfileError) as stopped:
        writing.write_one_file(
            target,
            REPORT_TEXT,
            sources=_guarded(places),
            words=errors.QUALITY_WORDS,
        )
    said = f"{stopped.value}"
    assert f"replaced the {errors.INPUT_DESCRIPTION}" in said
    assert description.read_bytes() == before
    assert REPORT_TEXT not in description.read_text(encoding="utf-8")


# ---------------------------------------------------------------------
# the fault sweep, re-run against the one-target transaction (P2-D10)
# ---------------------------------------------------------------------

# The filename every code object of the module holding the transaction
# carries, read off one of its own functions for the reason the shipped
# sweep gives: a rebuilt path is spelled differently on some platforms,
# and a comparison that then matches nothing makes the whole sweep pass
# while injecting nothing at all.
_SOURCE = writing.write_one_file.__code__.co_filename

# The two frames that hold the one-target guard and everything its
# handler depends on.
_GUARD_FRAMES = ("write_one_file", "_move_one_into_place")


def _working_files(folder: pathlib.Path) -> "list[pathlib.Path]":
    """Every working file left in ``folder``, sorted by name."""
    found = [
        entry
        for entry in folder.iterdir()
        if writing.PART_SUFFIX in entry.name
        or writing.KEPT_SUFFIX in entry.name
    ]
    return sorted(found, key=lambda entry: entry.name)


class _Stop:
    """Raise one failure at the nth statement boundary inside writing.py.

    The shipped sweep's instrument, unchanged: a local trace function
    that raises makes the traced frame raise at exactly that line, which
    is the finest boundary a test can inject at without rewriting
    bytecode. Only one failure is ever injected, so the cleanup it
    triggers runs untouched.
    """

    def __init__(
        self,
        nth: int,
        failure: BaseException,
        frames: "tuple[str, ...] | None",
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
) -> "tuple[BaseException | None, writing.DiskState, _Stop]":
    """One whole one-target transaction with one injected stop."""
    places = _inputs(folder)
    target = folder / "clinic-twin-quality.txt"
    if earlier:
        target.write_text(OLD_REPORT, encoding="utf-8")
    state = writing.DiskState()
    stop = _Stop(nth, failure, frames)
    caught: BaseException | None = None
    sys.settrace(stop._call)
    try:
        writing.write_one_file(
            target,
            REPORT_TEXT,
            sources=_guarded(places),
            state=state,
            words=errors.QUALITY_WORDS,
        )
    except BaseException as failed:  # noqa: BLE001 -- the point of the test
        caught = failed
    finally:
        sys.settrace(None)
    return (caught, state, stop)


def _check_one_stop(
    folder: pathlib.Path,
    caught: "BaseException | None",
    state: writing.DiskState,
    failure: BaseException,
    earlier: bool,
    where: str,
) -> None:
    """The questions asked after one injected stop.

    The same four the two-file sweep asks, minus the one that cannot be
    asked of a single artifact -- no pair can be left half-published,
    because there is no pair -- plus the one this transaction adds: the
    two inputs are still exactly what they were, whatever happened.
    """
    target = folder / "clinic-twin-quality.txt"

    # 1. The person's own failure reached them, as itself. An
    #    UnboundLocalError here is the defect the shipped sweep exists
    #    for, in the code that sweep does not reach.
    if caught is not None:
        assert caught is failure, (
            f"{where}: the injected failure was replaced by "
            f"{type(caught).__name__}: {caught}"
        )

    # 2. Every working file that survived is NAMED to the person.
    told = state.sentence
    if state.left_behind:
        told = f"{told} {state.left_behind}"
    for leftover in _working_files(folder):
        assert f"{leftover}" in told, (
            f"{where}: {leftover.name} survived and is named nowhere. It "
            f"holds {leftover.read_text(encoding='utf-8')!r}"
        )

    # 3. The output holds nothing but what it held or what this run
    #    wrote. A rename is one filesystem step, so a half file here
    #    would mean something wrote to the output name directly.
    allowed = [REPORT_TEXT] + ([OLD_REPORT] if earlier else [])
    if target.exists():
        assert target.read_text(encoding="utf-8") in allowed, (
            f"{where}: the report's name holds neither the file that was "
            f"there before nor the one this run wrote"
        )

    # 3b. The earlier report is still SOMEWHERE until the new one is in
    #     place: it is real-derived material this run did not produce.
    installed = (
        target.exists()
        and target.read_text(encoding="utf-8") == REPORT_TEXT
    )
    if earlier and not installed:
        survivors = [target] + _working_files(folder)
        assert any(
            place.exists()
            and place.read_text(encoding="utf-8") == OLD_REPORT
            for place in survivors
        ), (
            f"{where}: the report from before this run is gone and the "
            f"new one is not in its place"
        )

    # 4. And BOTH INPUTS are untouched, which is this transaction's own
    #    promise: validation never writes, moves, truncates or
    #    re-encodes the description or the file it measured (V1.3).
    assert (folder / "clinic-profile.json").read_text(
        encoding="utf-8"
    ) == DESCRIPTION_TEXT, f"{where}: the description was written over"
    assert (folder / "clinic-twin.csv").read_text(
        encoding="utf-8"
    ) == MEASURED_TEXT, f"{where}: the measured file was written over"


def test_the_injector_recognizes_the_frames_it_has_to_stop(
    tmp_path: pathlib.Path,
) -> None:
    """The one string comparison every sweep below rests on.

    When this comparison matched nothing on a hosted Windows run of the
    shipped sweep, every assertion in it passed without a single
    injection. Saying which comparison produced the zero is a diagnosis;
    the floors below say only that the count was zero.
    """
    assert _SOURCE.endswith("writing.py"), (
        f"the injector is aimed at {_SOURCE!r}, which is not the module "
        f"holding the write transaction"
    )
    assert writing._move_one_into_place.__code__.co_filename == _SOURCE, (
        "both frames the one-target guard lives in must be recognized"
    )
    folder = tmp_path / "aimed"
    folder.mkdir()
    caught, _state, stop = _run_with_a_stop(
        folder, 1, MemoryError("injected"), False, _GUARD_FRAMES
    )
    assert stop.fired, (
        "the very first statement of the one-target transaction was not "
        "traced, so no failure can be injected and every check below is "
        "vacuous"
    )
    assert isinstance(caught, MemoryError)
    assert not (folder / "clinic-twin-quality.txt").exists()


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
def test_a_stop_at_every_boundary_of_the_one_target_guard_is_covered(
    tmp_path: pathlib.Path,
    make_failure: "object",
    earlier: bool,
) -> None:
    """P2-D10's measurement, re-run against the generalized code."""
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
    # A floor on the sweep itself: a tracer that quietly stopped tracing
    # would make every assertion above vacuous.
    assert last_fired >= 30, (
        f"only {last_fired} boundaries were injected into; the two frames "
        f"holding the one-target guard execute more than that"
    )


def test_a_stop_anywhere_in_the_module_is_covered_too(
    tmp_path: pathlib.Path,
) -> None:
    """The same sweep widened to every function the transaction calls."""
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
    assert last_fired >= 150, (
        f"only {last_fired} boundaries were injected into; a run that "
        f"replaces an earlier report executes more than that"
    )
