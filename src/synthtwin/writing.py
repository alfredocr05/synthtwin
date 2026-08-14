"""Writing files without ever leaving a half-written one (plan P1-D11).

THE TRANSACTION, MOVED HERE AND OTHERWISE UNCHANGED (plan P2-D1). Every
line below was in `profile.py`, which imports the reader's own table
type. Phase 2's generator has to write two files by the same rule -- two
files or neither, and a person told by name what is on disk after a stop
-- and it may not import a module that reaches the reader, because a
boundary that holds only as long as nobody calls the wrong function is
not a boundary at all. So the transaction lives in a module that imports
neither the reader nor the taxonomy, and `profile.py` re-exports what it
always exported.

THE WORDS ARE NOW AN ARGUMENT TOO (plan P2-D10). The machinery is one
piece of code for every command that writes, but the files are not the
same files:
`profile` writes a profile and a summary from a table, `generate` writes
a twin and a report from a profile. A refusal that named the profiler's
files whatever was running would have told somebody in a stopped
`generate` run that their PROFILE could not be written -- the one file
that run never writes to -- and sent them to check a table the command
never had. So every refusal composed here that names a file by
vocabulary takes an `errors.ArtifactWords`, the nouns live in
`errors.py` with every other word a person reads, and the public entry
points default to the profiler's set.

That default is why the profiler's messages are the same byte for byte
as before, and it is also the one thing here a caller can get wrong in
silence: a command writing something other than a profile that forgets
to pass its own set gets the profiler's, and nothing in this module can
tell that it did. Two things narrow that. Inside this module the words
are a required argument at every step -- no private helper defaults them,
so a step that forgot them would not run at all -- and the suite reads
this module's own syntax to check that every one of these refusals is
composed with the words it was handed, rather than trusting a list
somebody has to remember to update.

AND THE COUNT OF FILES IS NOW AN ARGUMENT TOO (plan P3-D1). A third
command writes ONE artifact, the quality report, so the transaction has
a one-target form beside the two-file one: `write_one_file`. It keeps
every rule below except the one that has nothing to hold on to -- there
is no pair to leave half-published -- and it widens one: the file a
command may not write over is a SET here, because `validate` is handed
two files and neither the description nor the file being measured may
be landed on. The same-file machinery is the shipped one, asked once per
input, and asked a second time once the output exists.

THE RULE THIS MODULE KEEPS, stated once so it can be checked: when
`write_both_files` returns, both files hold the text it was given -- and
when `write_one_file` returns, the one output name does; when either
raises, each output name holds exactly what it held before -- the
earlier file or nothing -- unless the person is told otherwise, and they
are told by name, every file that is on disk and what each one holds,
checked by looking rather than assumed from what was attempted. Each
function's own docstring states the bounds of that claim, including the
residuals it does not close.

Imports here stay within the allowlist (plan D6.2): dataclasses,
pathlib, and this package's own modules. Nothing here reads a table, and
no path arrives except from the caller.
"""

import dataclasses
import pathlib

from synthtwin import errors, parsing
from synthtwin.paths import PathValidationError, validate_local_path


@dataclasses.dataclass
class DiskState:
    """A place for the write transaction to leave what is on disk.

    `write_both_files` composes its own refusals and puts the state of
    every name inside them, so a caller normally needs nothing else. But
    a failure the transaction did not compose -- memory exhausted inside
    the write, a person pressing Ctrl-C, a defect in this package --
    must not be rewritten on its way out: the caller recognizes it by
    its type and has advice of its own for it, and that advice is what
    the person needs to read (review item P1-R7-F1).

    So the transaction cleans up, writes one sentence here saying what
    is at each name afterwards, and lets the original failure continue
    untouched. The caller prints this sentence and then its own message:
    one says what they are holding, the other says why it stopped.

    `sentence` is empty on every ordinary run and after every refusal
    the transaction composed itself -- those already carry the state in
    their own words, and saying it twice is worse than saying it once.

    `both_files_written` covers the other end of the run. Once both
    renames have finished there is nothing left to undo: the two output
    names hold this run's files, and a failure arriving after that
    moment is not a rollback and must not be described as one. The flag
    says so, and `left_behind` names the one working file that can
    still be occupied -- the working name an earlier profile was moved
    to, which is the reader's own file and is never removed. It is a
    single name rather than a list because at that moment it is the
    only working name in play: the two parts have become the two
    outputs, and every other name this run reached for was either
    withdrawn by the filesystem or never reached at all.

    `target_written` is the one-target form's answer to the same
    question (plan P3-D1). It is a second field rather than a reuse of
    `both_files_written` because a run that wrote ONE file did not write
    both, and a caller reading a flag whose name says "both" would
    report two files where one was written. Each entry point sets its
    own, and neither reads the other's.

    All four fields are for the caller to print; nothing here decides
    what to say about them.
    """

    sentence: str = ""
    both_files_written: bool = False
    target_written: bool = False
    left_behind: str = ""



def _what_is_there(target: pathlib.Path) -> str:
    """What is at ``target`` right now, in one word. Never raises.

    One of "file", "folder", "link", "other", "nothing", or "unknown".
    Every question this asks the filesystem can fail -- a folder whose
    permissions changed, a disconnected drive -- and an unhandled
    failure here escaped as a traceback with no advice in it (review
    item P1-R6-F5). "unknown" is the answer whenever the filesystem
    would not say, and every caller treats "unknown" as a reason to
    stop rather than a reason to guess.

    A link is reported as a link and never as the file it points at: a
    name that leads somewhere else is not a place a description of real
    data may be written.
    """
    place = pathlib.Path(target)
    try:
        if place.is_symlink():
            return "link"
        if not place.exists():
            return "nothing"
        if place.is_dir():
            return "folder"
        if place.is_file():
            return "file"
    except OSError:
        return "unknown"
    return "other"


def _can_be_seen(target: pathlib.Path) -> str:
    """Is a file reachable at ``target``: "yes", "no", or "unknown".

    This follows a link to whatever it leads to, exactly as asking
    whether the path exists always has: a link leading nowhere is "no",
    because nothing is reachable through it. The whole point of the
    function is the third answer -- the question can FAIL, and a
    failure that escapes as a traceback is a defect (review item
    P1-R6-F5).
    """
    place = pathlib.Path(target)
    try:
        if place.exists():
            return "yes"
    except OSError:
        return "unknown"
    return "no"


def refuse_if_folder(
    target: pathlib.Path,
    words: errors.ArtifactWords = errors.PROFILE_WORDS,
) -> None:
    """Refuse, before anything is written, if a folder owns ``target``.

    Guarantees:

    - Inputs: one output path, which is looked at and never written to,
      and the words this command uses for its own files. Left out, the
      profiler's words are used.
    - Determinism: the answer is whatever the filesystem says at that
      moment; nothing is remembered between calls.
    - Errors raised: ProfileError, with a plain-language message, when
      a folder owns the name and when the name cannot be examined at
      all. A name this code could not look at is one it cannot promise
      anything about, so it is refused rather than written through.
    - Boundary: nothing is created, written or removed here.
    """
    place = pathlib.Path(target)
    what = _what_is_there(place)
    if what == "folder":
        raise errors.ProfileError(errors.output_is_a_folder(f"{place}"))
    if what == "unknown":
        raise errors.ProfileError(
            errors.output_not_writable(
                f"{place}", errors.COULD_NOT_CHECK, words
            )
        )


def _refuse_unless_plain_file(
    target: pathlib.Path, words: errors.ArtifactWords
) -> None:
    """Refuse an existing target that is not an ordinary file.

    A pipe accepts everything written to it and sends it to whoever is
    reading; a device swallows it. Neither is a place a description of
    real data may go, and neither is caught by asking whether the path
    is local (review item P1-R2-F7). A name that cannot be examined at
    all is refused too: an output this code could not look at is one it
    cannot promise anything about.

    ``words`` has no default here, and none of the private helpers below
    has one either. A default on an inside function is a way for one
    command's vocabulary to reach another command's message without
    anybody writing it down; the two public entry points carry the only
    defaults, where a caller can see what it is getting.
    """
    place = pathlib.Path(target)
    what = _what_is_there(place)
    if what == "folder":
        raise errors.ProfileError(errors.output_is_a_folder(f"{place}"))
    if what == "link" or what == "other":
        raise errors.ProfileError(
            errors.output_is_not_a_plain_file(f"{place}")
        )
    if what == "unknown":
        raise errors.ProfileError(
            errors.output_not_writable(
                f"{place}", errors.COULD_NOT_CHECK, words
            )
        )


def is_the_same_file(first: pathlib.Path, second: pathlib.Path) -> bool:
    """True when two paths lead to one file, and on any doubt at all.

    Three rules, in order, and the order is the point (review items
    P1-R2-F7 and P1-R3-F5):

    1. equal resolved paths are the same destination whether or not
       anything is there yet. Two names that are both dangling links to
       one missing file resolve equal, and the earlier version answered
       "different" because neither existed -- so both writes went to
       one file and the machine-readable profile was lost;
    2. when both entries exist, the filesystem's own identity settles
       it, which is what catches a hard link;
    3. if the filesystem cannot answer, the answer is YES. A check that
       protects the user's data must fail closed: refusing a run that
       might have been fine costs a re-run, and permitting one that
       overwrites their table costs the table. That rule now covers the
       existence questions too: they are metadata calls like any other
       and can fail like any other (review item P1-R6-F5).

    What this cannot settle on its own: two names that do not exist yet
    and are spelled differently, but that the filesystem treats as one
    file anyway -- two spellings of the same accented letter, say, on a
    host that folds them together. Nothing can be asked about a file
    that is not there. `write_both_files` therefore asks this question
    again once the first file IS on disk, when the answer is decidable,
    and undoes the run if the two names have become one.
    """
    left = pathlib.Path(first)
    right = pathlib.Path(second)
    try:
        here = left.resolve()
        there = right.resolve()
        if here == there:
            return True
        # Many filesystems treat names differing only in case as one
        # file. Comparing case-blind can refuse a pair that really is
        # two files on a case-sensitive system; that costs a re-run,
        # while missing the pair costs one of the two outputs (review
        # item P1-R4-F3).
        if parsing.folded(f"{here}") == parsing.folded(f"{there}"):
            return True
    except OSError:
        return True
    here_is = _can_be_seen(left)
    there_is = _can_be_seen(right)
    if here_is == "unknown" or there_is == "unknown":
        return True
    if here_is == "no" or there_is == "no":
        return False
    try:
        return left.samefile(right)
    except OSError:
        return True




# Names synthtwin writes under while a run is in flight. Nothing is ever
# written directly to a name the user reads.
#
# A working name is never simply used: it is CREATED, and created in a
# way the filesystem refuses if anything of that name is there already.
# The earlier version composed one fixed working name per output and
# wrote to it, so a link left at that name sent the profile wherever it
# pointed -- including over the user's own table, the one file this tool
# exists to protect -- and an unrelated file of that name was silently
# written over and then deleted (review item P1-R6-F5). Nothing
# synthtwin did not create is ever written to or removed.
PART_SUFFIX = ".synthtwin-part"
KEPT_SUFFIX = ".synthtwin-kept"

# How many working names are tried beside one output before the run
# stops and says why. A search with no end is a hang; and dozens of
# leftovers beside one output is not a thing to write through, it is a
# thing for a person to look at.
WORKING_NAME_ATTEMPTS = 64

# How far a run got with one working name it reached for. The two states
# are kept apart because they permit different things, and confusing
# them in either direction is a defect:
#
# * CLAIM_MADE -- the exclusive creation handed back, so this run made
#   the file and may remove it;
# * CLAIM_REACHED -- the creation was attempted and this run never saw
#   it finish, so the name MAY hold a file this run made and may equally
#   hold one that was already there. It may be named to the person and
#   may never be removed.
CLAIM_MADE = "made"
CLAIM_REACHED = "reached"


@dataclasses.dataclass
class _Claimed:
    """Every working name this run reached for, and how far each got.

    THE WINDOW THIS EXISTS TO CLOSE. Creating a file is one step for the
    operating system and two moments for this program: the file appears
    on disk, and only afterwards does the creating call hand back to
    Python. A person pressing Ctrl-C in between leaves a file synthtwin
    made under a name this run never recorded, so the cleanup did not
    consider it and the sentence about what is on disk did not name it
    -- a file synthtwin made and did not tell them about (review item
    P1-R8-F1).

    So the name is claimed BEFORE the creation is attempted rather than
    after it succeeds. The record then covers the name whether or not
    the creation finished, and the interrupt window falls inside the
    claim instead of outside it.

    Each entry is a working name and one of the two states above. A
    caller reads them through `_unclaimed`, which hands back only the
    names its own bookkeeping has not already covered.
    """

    entries: "list[tuple[pathlib.Path, str]]"


def _reach_for(claimed: "_Claimed | None", place: pathlib.Path) -> None:
    """Record a working name BEFORE trying to create it.

    From this call onward the run owns the QUESTION of that name even
    if it never owns the file: whatever happens next, the name is one
    the person can be told about.
    """
    if claimed is None:
        return
    claimed.entries = claimed.entries + [
        (pathlib.Path(place), CLAIM_REACHED)
    ]


def _settle(
    claimed: "_Claimed | None", place: pathlib.Path, state: str
) -> None:
    """Say what is now known about a claimed name; "" withdraws it.

    A claim is withdrawn only when the filesystem itself has said that
    this run created nothing at that name, which is what a refusal for
    an existing name says and nothing else does.
    """
    if claimed is None:
        return
    wanted = f"{pathlib.Path(place)}"
    kept: list[tuple[pathlib.Path, str]] = []
    for one, code in claimed.entries:
        if f"{one}" == wanted:
            continue
        kept = kept + [(one, code)]
    if state:
        kept = kept + [(pathlib.Path(place), state)]
    claimed.entries = kept


def _unclaimed(
    claimed: "_Claimed | None", known: "list[str]"
) -> "list[tuple[pathlib.Path, str]]":
    """The claimed names the caller's own bookkeeping has not covered.

    ``known`` holds every path the caller is already describing, spelled
    out. Anything named there is left to the caller, which knows more
    about it than this record does -- and one of those names is the
    working name an earlier profile was moved to, which must never be
    removed by anybody.

    What comes back is in the shape `_clear_away` takes, and the state
    decides the code: a name this run is known to have made is an empty
    working file to be removed, and a name it merely reached for carries
    the code that `_clear_away` refuses to remove.
    """
    if claimed is None:
        return []
    extra: list[tuple[pathlib.Path, str]] = []
    for place, state in claimed.entries:
        if f"{place}" in known:
            continue
        if state == CLAIM_MADE:
            extra = extra + [(place, errors.ON_DISK_EMPTY_WORKING)]
        else:
            extra = extra + [(place, errors.ON_DISK_CLAIMED_WORKING)]
    return extra


def _create_empty(
    candidate: pathlib.Path, claimed: "_Claimed | None" = None
) -> "tuple[str, str]":
    """Create ``candidate`` as a new empty file; say how that went.

    Four answers, and the fourth is the point:

    * ("made", "") -- the name is synthtwin's and holds an ordinary
      empty file;
    * ("taken", "") -- something of that name was there already, so the
      name belongs to somebody else and nothing was touched;
    * ("uncertain", detail) -- the exclusive creation SUCCEEDED and the
      look afterwards did not confirm an ordinary file. The name is
      synthtwin's from the moment the creation succeeded, so the caller
      OWNS it and has to clear it away or name it to the person;
    * ("refused", detail) -- the creation itself failed. In the ordinary
      reading of that nothing was created, and the caller looks rather
      than assuming it: the creation is an open and then a close
      underneath, and a failure of the second leaves the file there.

    The creation is exclusive: the filesystem itself settles who gets
    the name, in one step, and refuses when the name exists -- including
    when it is a link, whether or not the link leads anywhere. That is
    what makes a working name safe without any guessing about what is
    on the disk a moment before.

    THE CLAIM COMES FIRST. ``claimed`` is recorded before the creation
    is attempted, never after it succeeds, so that a run stopped inside
    the creation -- the file already on disk, the call not yet handed
    back -- still holds the name and can tell the person about it
    (review item P1-R8-F1). The claim is upgraded to CLAIM_MADE the
    moment the creation hands back, and withdrawn only when the
    filesystem says the name was already taken, which is proof that this
    run created nothing there.
    """
    place = pathlib.Path(candidate)
    _reach_for(claimed, place)
    try:
        place.touch(exist_ok=False)
    except FileExistsError:
        # The filesystem refused because something of that name is
        # already there. That is proof this run created nothing here, so
        # the claim goes, and the file that IS there is left alone: it
        # belongs to somebody else.
        _settle(claimed, place, "")
        return ("taken", "")
    except OSError as error:
        # The claim STAYS. Nothing was created in the ordinary reading of
        # this failure, but "ordinary" is not "certain", and a name this
        # run may have made a file at is a name the person may be told
        # about. It is never removed on that reasoning alone.
        return ("refused", f"{error}")
    _settle(claimed, place, CLAIM_MADE)
    if _what_is_there(place) != "file":
        # Created a moment ago and already not an ordinary file: hand
        # it back rather than write a description of real data into it.
        #
        # OWNERSHIP STARTS AT THE CREATION, not at the check that
        # follows it. Reporting this as a plain refusal threw away the
        # name synthtwin had just claimed, and the run could then report
        # a clean folder while a file of synthtwin's own making sat in
        # it (review item P1-R7-F1).
        return ("uncertain", errors.COULD_NOT_CHECK)
    return ("made", "")


def _is_one_of(
    candidate: pathlib.Path, forbidden: "list[pathlib.Path]"
) -> bool:
    """True when ``candidate`` leads to one of the files to be spared."""
    for other in forbidden:
        if is_the_same_file(candidate, other):
            return True
    return False


def _claim_working_name(
    target: pathlib.Path,
    suffix: str,
    forbidden: "list[pathlib.Path]",
    words: errors.ArtifactWords,
    claimed: "_Claimed | None" = None,
) -> "tuple[pathlib.Path | None, str, list[tuple[pathlib.Path, str]]]":
    """Create a new empty working file beside ``target``.

    Beside it, in the same folder, because renaming within one folder
    is a single filesystem operation while moving between folders is a
    copy that can fail halfway. A folder the system chose instead -- a
    temp folder -- is usually a different filesystem, so it is not an
    option here.

    The name is made unique by CREATING it: numbered candidates are
    tried in order and the filesystem's exclusive creation decides. No
    random source is involved, because the profile's bytes must not
    depend on anything but its inputs (plan D12), and no working name
    reaches the published output anyway.

    Every candidate is passed over, never overwritten, when anything of
    that name exists, and refused when it leads to the user's table or
    to either output file.

    Returns (path, "", []) when a name was claimed. On a refusal it
    returns (None, trouble, owned): ``trouble`` is the message for the
    person, and ``owned`` names every file THIS CALL itself created and
    could not use, each with what it holds, so the caller's own cleanup
    covers them and its message names whatever survives.

    That third item is why this hands back a refusal instead of raising
    one. A file created a moment before the check that then could not
    be settled belongs to synthtwin, and an exception carried the
    message out of here while leaving the name behind: the caller
    cleaned an inventory that did not mention it and could truthfully
    say nothing was left, with an empty file of synthtwin's making
    sitting in the folder (review item P1-R7-F1).

    ``claimed`` covers the one moment a returned value cannot: the
    creation of a candidate, where the file can be on disk before this
    function is in a position to hand anything back at all (review item
    P1-R8-F1). Every name reached for is recorded there before it is
    reached for, and the caller reads it through `_unclaimed` for
    whatever a stop in that moment left uncovered.

    ``words`` names this command's own files in the refusals composed
    here. `working_name_unavailable` needs none of them -- a working file
    is synthtwin's own and is called that in every command -- so only the
    two "could not be written" refusals carry it.
    """
    place = pathlib.Path(target)
    tried: list[str] = []
    number = 1
    while number <= WORKING_NAME_ATTEMPTS:
        candidate = pathlib.Path(f"{place}{suffix}-{number}")
        if len(tried) < 3:
            tried = tried + [f"{candidate}"]
        number = number + 1
        try:
            validate_local_path(f"{candidate}", purpose="working file")
        except PathValidationError as error:
            return (
                None,
                errors.output_not_writable(
                    f"{candidate}", f"{error}", words
                ),
                [],
            )
        if _what_is_there(candidate) != "nothing":
            continue
        if _is_one_of(candidate, forbidden):
            continue
        outcome, detail = _create_empty(candidate, claimed)
        if outcome == "made":
            return (candidate, "", [])
        if outcome == "taken":
            continue
        trouble = errors.output_not_writable(f"{candidate}", detail, words)
        if outcome == "uncertain":
            return (
                None,
                trouble,
                [(candidate, errors.ON_DISK_UNCERTAIN_WORKING)],
            )
        # The creation itself failed. Usually that means nothing is
        # there, and usually is not good enough for a name this run may
        # have made a file at, so the question is settled by looking. A
        # file found here is NAMED and left alone: this run cannot tell
        # its own empty file from one another program put there in the
        # same moment, and deleting somebody else's file is far worse
        # than mentioning one of ours (review item P1-R8-F1).
        if _what_is_there(candidate) == "nothing":
            return (None, trouble, [])
        return (
            None,
            trouble,
            [(candidate, errors.ON_DISK_CLAIMED_WORKING)],
        )
    return (
        None,
        errors.working_name_unavailable(
            f"{place}", tried, WORKING_NAME_ATTEMPTS
        ),
        [],
    )


def _remove_and_check(target: pathlib.Path) -> bool:
    """Delete one of synthtwin's own working files; True when it is gone.

    The answer comes from looking afterwards, not from the delete call
    returning quietly: a cleanup that is reported but not checked is
    how a file holding real-derived text gets left behind while the
    message says the folder is clean (review item P1-R6-F5).
    """
    place = pathlib.Path(target)
    try:
        place.unlink()
    except OSError:
        # Includes the file already being gone. Either way the question
        # is settled by looking.
        return _what_is_there(place) == "nothing"
    return _what_is_there(place) == "nothing"


def _clear_away(
    places: "list[tuple[pathlib.Path, str]]",
) -> "list[tuple[str, str]]":
    """Remove each working file; describe the ones still there.

    Each pair is a working file and the code saying what it holds, so
    that a leftover holding a full description of the table is never
    reported as an empty one.

    ONE CODE IS NOT REMOVED. `ON_DISK_CLAIMED_WORKING` marks a name this
    run had claimed and was still creating when it stopped, so anything
    there may be the empty file synthtwin made and may be a file that
    was already under that name. Removing it on the chance that it is
    ours would turn a run that failed to mention a file into a run that
    destroyed somebody's data, which is far worse, so it is looked at
    and named instead (review item P1-R8-F1). The rule lives here, with
    the removal, rather than at each caller: a list reaching this
    function is handled by what its codes say, whoever built it.
    """
    left: list[tuple[str, str]] = []
    for place, code in places:
        if code == errors.ON_DISK_CLAIMED_WORKING:
            # Named only if something is really there. A claim that came
            # to nothing is not a file, and a message that invents one
            # sends the reader looking for it.
            if _what_is_there(place) == "nothing":
                continue
            left = left + [(f"{pathlib.Path(place)}", code)]
            continue
        if _remove_and_check(place):
            continue
        left = left + [(f"{pathlib.Path(place)}", code)]
    return left


def _named_state(
    target: pathlib.Path, present: str, missing: str
) -> "tuple[str, str]":
    """Look at one output name and say what is there, in the caller's terms.

    ``present`` and ``missing`` are the codes that apply when a file is
    or is not there, which only the caller knows -- an empty name means
    "as it was" after a failure that touched nothing, and "the earlier
    file could not be put back" after a rollback that did not finish.
    A name that cannot be examined is reported as exactly that.
    """
    place = pathlib.Path(target)
    what = _what_is_there(place)
    if what == "unknown":
        return (f"{place}", errors.ON_DISK_UNCHECKED)
    if what == "nothing":
        return (f"{place}", missing)
    return (f"{place}", present)


def _put_back(kept: "pathlib.Path | None", target: pathlib.Path) -> bool:
    """Restore a file that was set aside; True when the name is as before."""
    if kept is None:
        return True
    source = pathlib.Path(kept)
    place = pathlib.Path(target)
    try:
        source.replace(place)
    except OSError:
        return False
    return _what_is_there(place) == "file"


def _take_out(kept: "pathlib.Path | None", target: pathlib.Path) -> bool:
    """Undo an installed profile; True when the name is as it was before.

    With a set-aside file, that means putting it back. WITHOUT one it
    means removing what was just installed: the name held nothing
    before, and an earlier version simply left the new profile sitting
    there while the message said nothing had been written (review item
    P1-R6-F5).
    """
    if kept is not None:
        return _put_back(kept, target)
    return _remove_and_check(target)


def _after_undo(kept: "pathlib.Path | None") -> str:
    """The code for the profile's name once an install has been undone."""
    if kept is None:
        return errors.ON_DISK_BEFORE
    return errors.ON_DISK_RESTORED


def _state_nothing_published(
    target: pathlib.Path,
    summary_target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    words: errors.ArtifactWords,
    target_code: str = errors.ON_DISK_BEFORE,
) -> str:
    """Clear away the working files; say what is at each name afterwards.

    For a stop BEFORE either output name was touched, which is where
    every failure of the two working-file writes happens: the outputs
    hold what they held, and the only names that can have changed are
    synthtwin's own working files, each of which is removed here or
    named with what it holds.
    """
    left = _clear_away(leftovers)
    on_disk = [
        _named_state(target, target_code, errors.ON_DISK_ABSENT),
        _named_state(
            summary_target, errors.ON_DISK_BEFORE, errors.ON_DISK_ABSENT
        ),
    ] + left
    return errors.nothing_was_written([], on_disk, words)


def _state_part_way_through(
    target: pathlib.Path,
    summary_target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    kept: "pathlib.Path | None",
    kept_holds_the_earlier_profile: bool,
    words: errors.ArtifactWords,
) -> str:
    """The same, for a stop once the renaming into place had begun.

    Here the two output names are between one state and another, and
    this code cannot say which side of the move each one is on -- the
    exception arrived from outside the transaction's own reasoning, so
    the only honest answer about a file that IS there is that synthtwin
    cannot say which of the run's files ended up under that name. A name
    that is EMPTY is described by what this run did: if an earlier
    profile was set aside, it was taken away and is named under its
    working name; if there was never a file there, nothing is there now
    either.

    The set-aside name is the one place where a guess would cost
    something irreplaceable, so it is not guessed at. Once the move of
    the earlier profile is known to have finished, that name holds the
    earlier profile and is described as holding it. While the move was
    still in flight it holds either that profile or the empty file
    synthtwin created for it, and it is described as the uncertain thing
    it is -- and it is never removed here, because the one file under
    these names that this run did not produce is the reader's own
    earlier profile.

    ``words`` supplies the closing clause: why the two files must not be
    left as this run left them. That reason is about what the two files
    ARE, so it is the running command's to say and not this function's.
    """
    left = _clear_away(leftovers)
    if kept is None:
        empty_target = errors.ON_DISK_ABSENT
    else:
        empty_target = errors.ON_DISK_TAKEN_AWAY
    on_disk = [
        _named_state(target, errors.ON_DISK_UNSETTLED, empty_target),
        _named_state(
            summary_target, errors.ON_DISK_UNSETTLED, errors.ON_DISK_ABSENT
        ),
    ]
    if kept is not None:
        holds = errors.ON_DISK_UNSETTLED
        if kept_holds_the_earlier_profile:
            holds = errors.ON_DISK_SET_ASIDE
        on_disk = on_disk + [
            _named_state(kept, holds, errors.ON_DISK_ABSENT)
        ]
    return errors.rollback_failed([], on_disk + left, words)


def _remember(state: "DiskState | None", sentence: str) -> None:
    """Leave the disk state where the caller will look for it.

    Nothing is printed here and nothing is raised: this module composes
    words and the caller decides what to do with them. A caller that
    passed no DiskState gets the behavior it had before -- the failure
    and nothing else.
    """
    if state is None:
        return
    state.sentence = sentence


def _stopped_clean(
    trouble: str,
    target: pathlib.Path,
    summary_target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    words: errors.ArtifactWords,
    target_code: str = errors.ON_DISK_BEFORE,
) -> errors.TransactionRefusal:
    """The refusal for a failure that published nothing, with the disk in it.

    One of the two places a `TransactionRefusal` is built, and the type
    is true here: `_state_nothing_published` clears the working files
    away and looks at every name before this returns, so the object
    handed back carries a cleanup that has run and a message that names
    every file. The transaction's handler relies on exactly that.
    """
    stated = _state_nothing_published(
        target, summary_target, leftovers, words, target_code
    )
    return errors.TransactionRefusal(f"{trouble} {stated}")


def _stopped_broken(
    trouble: str,
    target: pathlib.Path,
    summary_target: pathlib.Path,
    kept: "pathlib.Path | None",
    leftovers: "list[tuple[pathlib.Path, str]]",
    words: errors.ArtifactWords,
) -> errors.TransactionRefusal:
    """The refusal for a failure whose own undoing did not finish.

    The profile name holds the new description if anything at all, the
    summary name holds whatever it held before, and a set-aside earlier
    profile is named where one is still sitting.

    The other of the two places a `TransactionRefusal` is built, on the
    same terms: the cleanup below runs and every name is looked at
    before the object exists.
    """
    left = _clear_away(leftovers)
    on_disk = [
        _named_state(target, errors.ON_DISK_NEW, errors.ON_DISK_TAKEN_AWAY),
        _named_state(
            summary_target, errors.ON_DISK_BEFORE, errors.ON_DISK_ABSENT
        ),
    ]
    if kept is not None:
        on_disk = on_disk + [
            _named_state(
                kept, errors.ON_DISK_SET_ASIDE, errors.ON_DISK_ABSENT
            )
        ]
    return errors.TransactionRefusal(
        f"{trouble} {errors.rollback_failed([], on_disk + left, words)}"
    )


@dataclasses.dataclass
class _Progress:
    """How far the renaming got, for the handler that has to report it.

    `_move_into_place` composes a refusal for every failure it can
    foresee, and each of those refusals already carries the state of
    every name. This record is for the failures it cannot foresee: it
    lets the handler around it say what is at each name WITHOUT
    guessing, because the answers it needs -- had the renaming started,
    was an earlier profile set aside, did that move finish, and did both
    renames complete -- are known only inside.

    `installed` is the last of those and it is a different KIND of
    answer from the others. While it is false the handler describes a
    run between two states; once it is true the run's work is done and
    there is nothing to put back, so a failure arriving afterwards must
    not be reported as a rollback that failed. It is set after the
    second rename has returned, which leaves one statement boundary --
    named in `write_both_files` -- where the rename may have landed and
    this record does not yet say so.
    """

    kept: "pathlib.Path | None" = None
    moving: bool = False
    aside: bool = False
    installed: bool = False


def _finished(
    state: "DiskState | None", kept: "pathlib.Path | None"
) -> None:
    """Record that both files reached their names, for a stop after that.

    Both renames have returned, so the two output names hold this run's
    files and there is nothing to put back. A failure arriving from here
    on is not a rollback and may not be described as one: the wording
    for a run caught between two states would send the reader looking
    for damage that is not there.

    The only working name that can still be occupied at this point is
    the one an earlier profile was moved to. It is the reader's own
    file, so it is looked at and NAMED, never removed. The two parts
    have become the two outputs, and every other name this run reached
    for was either withdrawn by the filesystem or never reached, so
    there is nothing else to name.

    Nothing is raised here and nothing is printed; the caller decides
    what to say. `left_behind` is set before the flag, so a second stop
    inside this function can cost the whole report but can never
    announce two written files while keeping a leftover to itself.
    """
    if state is None:
        return
    if kept is not None and _what_is_there(kept) != "nothing":
        state.left_behind = f"{pathlib.Path(kept)}"
    state.both_files_written = True


def _move_into_place(
    first: pathlib.Path,
    second: pathlib.Path,
    first_part: pathlib.Path,
    second_part: pathlib.Path,
    forbidden: "list[pathlib.Path]",
    progress: _Progress,
    words: errors.ArtifactWords,
    claimed: "_Claimed | None" = None,
) -> "list[str]":
    """The renaming itself; `write_both_files` holds the handler around it.

    Nothing is set up in here that the handler needs. Every name the
    handler describes it already had before it opened, and the two
    answers only this function can give -- how far the renaming got, and
    whether both files reached their names -- are written into
    ``progress`` as they become true, never inferred afterwards.

    ``words`` travels through to every refusal composed in here, which is
    where most of the "could not be written" wordings a person ever sees
    are built.
    """
    target = pathlib.Path(first)
    summary_target = pathlib.Path(second)
    new_profile = pathlib.Path(first_part)
    new_summary = pathlib.Path(second_part)
    both = [
        (new_profile, errors.ON_DISK_WORKING),
        (new_summary, errors.ON_DISK_WORKING),
    ]

    what = _what_is_there(target)
    if what == "unknown":
        raise _stopped_clean(
            errors.output_not_writable(
                f"{target}", errors.COULD_NOT_CHECK, words
            ),
            target,
            summary_target,
            both,
            words,
        )
    if what == "folder":
        raise _stopped_clean(
            errors.output_is_a_folder(f"{target}"),
            target,
            summary_target,
            both,
            words,
        )
    if what == "link" or what == "other":
        raise _stopped_clean(
            errors.output_is_not_a_plain_file(f"{target}"),
            target,
            summary_target,
            both,
            words,
        )

    kept: pathlib.Path | None = None
    if what == "file":
        # An earlier profile is there. It moves to a working name of
        # synthtwin's own making -- not over anything -- so that it can
        # come back if the rest of the run does not finish.
        spare = forbidden + [new_profile, new_summary]
        aside_name, trouble, owned = _claim_working_name(
            target, KEPT_SUFFIX, spare, words, claimed
        )
        if aside_name is None:
            raise _stopped_clean(
                trouble, target, summary_target, both + owned, words
            )
        kept = aside_name
        progress.kept = aside_name
        # From here the outputs are between one state and another, and
        # a failure this function did not foresee can no longer be
        # described as "nothing was touched".
        progress.moving = True
        try:
            target.replace(kept)
        except OSError as error:
            raise _stopped_clean(
                errors.output_not_writable(f"{target}", f"{error}", words),
                target,
                summary_target,
                both + [(kept, errors.ON_DISK_EMPTY_WORKING)],
                words,
            ) from error
        # And now that name holds the earlier profile for certain, which
        # is a different thing to tell a person from "it holds either
        # that profile or an empty file synthtwin made".
        progress.aside = True

    progress.moving = True
    try:
        new_profile.replace(target)
    except OSError as error:
        trouble = errors.output_not_writable(f"{target}", f"{error}", words)
        if _put_back(kept, target):
            raise _stopped_clean(
                trouble,
                target,
                summary_target,
                both,
                words,
                _after_undo(kept),
            ) from error
        raise _stopped_broken(
            trouble, target, summary_target, kept, both, words
        ) from error

    # Now that a file really is at the profile's name, the question the
    # earlier check could not settle becomes decidable: are these two
    # names one file after all? Two spellings a filesystem folds
    # together answer "no" while neither exists and "yes" the moment one
    # does (review item P1-R6-F5). Asking now costs one metadata call
    # and saves the summary from landing on the profile.
    if is_the_same_file(target, summary_target):
        trouble = errors.outputs_are_the_same_file(
            f"{target}", f"{summary_target}"
        )
        if _take_out(kept, target):
            raise _stopped_clean(
                trouble,
                target,
                summary_target,
                [(new_summary, errors.ON_DISK_WORKING)],
                words,
                _after_undo(kept),
            )
        raise _stopped_broken(
            trouble,
            target,
            summary_target,
            kept,
            [(new_summary, errors.ON_DISK_WORKING)],
            words,
        )

    try:
        new_summary.replace(summary_target)
    except OSError as error:
        trouble = errors.output_not_writable(
            f"{summary_target}", f"{error}", words
        )
        if _take_out(kept, target):
            raise _stopped_clean(
                trouble,
                target,
                summary_target,
                [(new_summary, errors.ON_DISK_WORKING)],
                words,
                _after_undo(kept),
            ) from error
        raise _stopped_broken(
            trouble,
            target,
            summary_target,
            kept,
            [(new_summary, errors.ON_DISK_WORKING)],
            words,
        ) from error

    # Both names now hold this run's files. From here there is nothing
    # to put back, and a failure that arrives after this line must not
    # be described as a rollback that could not finish (review item
    # P1-R8-F1). The rename above and this line are two statements: a
    # stop between them is the one place where the move may have landed
    # and this record does not yet say so, and `write_both_files` states
    # that bound rather than papering over it.
    progress.installed = True

    if kept is None:
        return []
    if _remove_and_check(kept):
        return []
    # Both files are written and correct; the only thing wrong is that
    # the earlier profile is still sitting under a working name. It is
    # real-derived material, so it is handed back to the caller to be
    # reported rather than passed over in silence.
    return [f"{kept}"]


def _write_part(
    part: pathlib.Path, text: str, words: errors.ArtifactWords
) -> "tuple[str, str]":
    """Fill one working file; say what went wrong and what it holds now.

    Returns ("", ON_DISK_WORKING) when the text is on disk. On a refusal
    the first item is the message for the person and the second is what
    the working file holds at that moment: a refusal from the path check
    happens BEFORE a byte is written, so the file is still the empty one
    that was created, while a refusal from the write itself can leave
    part of the text there. The two are different things to hand to
    somebody who has to decide what to do with a leftover, so they are
    not reported as one.

    Both of the refusals this function can DESCRIBE are caught here, and
    they are caught by name because each has its own wording and its own
    answer to what the working file now holds. `write_text_file` puts the
    working name through the locality check immediately before writing,
    and that check raises PathValidationError, not ProfileError. Only
    ProfileError was caught, so a path refusal on the SECOND working file
    escaped the whole transaction: the first working file -- holding a
    complete description built from the real table -- was left in the
    user's folder, no cleanup ran, and the message discussed only the
    path (review item P1-R7-F1). On Windows that refusal has an ordinary
    route: a component check fails when permission is refused or another
    program is holding the component.

    ANYTHING ELSE IS NOT CAUGHT HERE, and that is deliberate. Two
    repairs in a row each caught the exception types their author had
    thought of, and the next type escaped: a MemoryError from the write
    itself passed through this function, through the transaction, and out
    to the command, which printed advice about memory that named no file
    while a complete description of the real table sat in a working file
    nobody had been told about. Naming a third type would have invited a
    fourth. `write_both_files` therefore holds a handler that does not
    ask what was raised at all.

    ``words`` reaches both the refusal composed here and the one
    `write_text_file` composes underneath, so a stop in either place
    names the file the running command is actually writing.
    """
    place = pathlib.Path(part)
    try:
        write_text_file(place, text, words)
    except PathValidationError as error:
        return (
            errors.output_not_writable(f"{place}", f"{error}", words),
            errors.ON_DISK_EMPTY_WORKING,
        )
    except errors.ProfileError as error:
        return (f"{error}", errors.ON_DISK_WORKING)
    return ("", errors.ON_DISK_WORKING)


def _describe_the_stop(
    state: "DiskState | None",
    first: pathlib.Path,
    second: pathlib.Path,
    first_part: "pathlib.Path | None",
    first_holds: str,
    second_part: "pathlib.Path | None",
    second_holds: str,
    progress: _Progress,
    claimed: "_Claimed | None",
    words: errors.ArtifactWords,
) -> None:
    """Clear up after a failure nobody composed, and say what is on disk.

    Everything this needs arrives as an argument. That is the point:
    the handler that calls it holds no value it had to compute after
    the guard opened, so no stop inside the guarded work can leave a
    name unbound and turn the person's failure into an
    UnboundLocalError raised from the cleanup (review item P1-R8-F1).
    A working file that was never claimed arrives as None and is simply
    not described.

    Which of the three accounts is given depends on how far ``progress``
    says the run got, never on what was raised:

    * both renames finished -- there is nothing to put back, so the run
      is recorded as having written both files, and the working name an
      earlier profile was moved to is named if it is still occupied;
    * the renaming had begun -- the two names are between one state and
      another, so each is looked at and described as the unsettled thing
      it is;
    * neither -- nothing was published, the outputs hold what they held,
      and only synthtwin's own working files can have changed.

    In the two accounts that consult the claim record, the set-aside
    earlier profile is passed to `_unclaimed` as already known, so that
    record can never propose removing the one file under these names
    that this run did not produce. The first account does not consult it
    at all: a run that got both files into place claimed exactly the two
    parts and that one name, and all three are described here.
    """
    if progress.installed:
        _finished(state, progress.kept)
        return
    waiting: list[tuple[pathlib.Path, str]] = []
    if first_part is not None:
        waiting = waiting + [(first_part, first_holds)]
    if second_part is not None:
        waiting = waiting + [(second_part, second_holds)]
    # And then whatever a stop inside a creation left uncovered: a
    # working name whose file reached the disk before the call that made
    # it could hand the name back to the two variables above.
    known = [f"{first}", f"{second}"]
    for place, _code in waiting:
        known = known + [f"{place}"]
    if progress.kept is not None:
        known = known + [f"{progress.kept}"]
    extra = _unclaimed(claimed, known)
    if progress.moving:
        _remember(
            state,
            _state_part_way_through(
                first,
                second,
                waiting + extra,
                progress.kept,
                progress.aside,
                words,
            ),
        )
        return
    if progress.kept is not None:
        # Claimed for the earlier profile, and the move of that profile
        # into it had not begun: the name holds the empty file synthtwin
        # created there, which is synthtwin's own to clear away.
        waiting = waiting + [(progress.kept, errors.ON_DISK_EMPTY_WORKING)]
    _remember(
        state, _state_nothing_published(first, second, waiting + extra, words)
    )


def write_both_files(
    profile_path: pathlib.Path,
    summary_path: pathlib.Path,
    profile_text: str,
    summary_text: str,
    table_path: "pathlib.Path | None" = None,
    state: "DiskState | None" = None,
    words: errors.ArtifactWords = errors.PROFILE_WORDS,
) -> "list[str]":
    """Write the two files as one outcome, or leave the folder untouched.

    The two files are one thing: the machine-readable profile is what
    the twin gets built from, and the summary is the only place the
    person is told what of their real data the profile carries. One of
    them alone is a failure state, and an earlier version produced
    several -- a half-written profile, a half-written summary nobody
    mentioned, and an earlier profile replaced with no way back (review
    item P1-R2-F11).

    THE SAME IS TRUE OF THE GENERATOR'S PAIR, which is why this takes
    ``words`` (plan P2-D10). A twin without its report is a table of
    synthetic values with nothing beside it saying which of them were
    approximated, which column can hold duplicates the real one could
    not, and what the twin may not be used for; a report without its twin
    describes a file that is not there. The parameter names are still the
    profiler's, because the two files arriving here are still the first
    and the second whatever a command calls them, and renaming them would
    have changed every call in the suite to say nothing new.

    THE RULE, stated so it can be checked: when this returns, both files
    hold the text it was given. When it raises -- with ANY exception,
    not only the ones named in this catalog -- each of the two names
    holds exactly what it held before, the earlier file or nothing,
    unless the person is told otherwise; and they are told by name,
    every file that is on disk and what each one holds, checked by
    looking rather than assumed from what was attempted. The rule is
    about ONE failure. A second one arriving while the first is being
    described can cost the telling, and RESIDUAL ONE below says so.

    That telling takes one of two forms, and the difference is only in
    where the sentence travels. A refusal this module composed carries
    it in its own message. A failure this module did NOT compose -- a
    MemoryError from the write, a person pressing Ctrl-C, a defect in
    this package -- must reach the caller unchanged, because the caller
    recognizes it by type and has its own advice for it; so the sentence
    is left in ``state`` instead and the failure continues untouched
    (review item P1-R7-F1).

    Which of the two it is, is not decided by asking what was raised.
    `ProfileError` is the package's ordinary refusal and any code in
    reach can raise one, so treating that type as proof that a cleanup
    had run let an unexpected one out of the first rename with both
    working files still on disk and nothing said (review item P1-R8-F1).
    The two places that compose a refusal in here build the narrower
    `errors.TransactionRefusal`, which is constructed only after its own
    cleanup has run and its own message names every file. That type, and
    only that type, is passed straight out; everything else -- including
    an unexpected `ProfileError` -- goes through the full cleanup.

    How: each file is written in full under a working name of
    synthtwin's own making in the same folder, and only then are the two
    renamed into place, with an existing profile set aside first so it
    can be restored.

    Guarantees:

    - Inputs: the two output paths, the two texts, optionally the path
      of the file the command was given, optionally a DiskState for the
      sentence described above, and optionally the words this command
      uses for its own files. Nothing but those texts is written
      anywhere, so the published bytes never depend on which working
      name a run happened to use, and ``words`` reaches the messages
      only -- no name, no byte and no decision here depends on it.
    - The words: left out, the profiler's set is used, which is what
      makes every message this transaction composed before the parameter
      existed the same byte for byte. A command whose files are not a
      profile and a summary MUST pass its own set; nothing here can
      detect that it did not, and the cost of the omission is a person
      being sent to look at the wrong file.
    - Files touched: only files synthtwin itself created, plus the two
      output names. A file of any other name that was already there is
      never written to and never removed -- the run stops instead and
      says which files are in the way.
    - The file the command was given: ``table_path``, when given, is
      checked against every output and every working name, and the run
      stops before anything is written if any of them would lead to it.
      For `profile` that file is the user's table; for `generate` it is
      the profile document. The rule is one rule in both -- nothing
      synthtwin writes may land on the file it was asked to read -- and
      ``words`` decides which of the two the refusal names.
    - Returns: the working files still on disk after an otherwise
      complete run, so the caller can report them. Normally empty.
    - Errors raised: ProfileError -- as `errors.TransactionRefusal`, one
      of its subclasses -- with a plain-language message for every
      refusal this module can describe. A path refusal raised inside the
      transaction is turned into one of these, carrying the state of
      every name, rather than escaping as a PathValidationError that no
      cleanup had seen (review item P1-R7-F1). Only
      `default_output_paths`, which runs before this, still hands a path
      refusal back in its own type. Anything else that can be raised in
      here leaves as itself, with the same type and the same message it
      had, after the cleanup has run and ``state`` has been given the
      sentence: the transaction may not rewrite a failure whose meaning
      belongs to somebody else.
    - The guard's own bounds: the handler is entered before the first
      working name is reached for, and every value it uses is bound
      before that -- so there is NO statement between "a file synthtwin
      made is on disk" and "a handler that will clear it away and name
      it is in force". The two residuals that remain are stated below;
      neither is that seam, because that seam no longer exists.

    The interrupt is covered from the first moment a working name is
    reached for, not from the moment one is successfully created. A file
    appears on disk a moment before the call that creates it hands the
    name back, and a run stopped in that moment used to hold a file it
    had made under a name it had never recorded: the cleanup did not
    consider it and the sentence did not mention it (review item
    P1-R8-F1). The name is now recorded before the creation is
    attempted, so it is covered whether or not the creation finished.

    RESIDUAL ONE: a second failure during the cleanup. The handler
    itself can be stopped -- a person pressing Ctrl-C again while the
    first stop is being described. That second failure is dropped and
    the first continues to the caller, because the caller's advice
    belongs to the first. What the person loses is the report: the
    sentence is composed and stored in one step, so it is lost whole
    rather than in part, and the record of a finished write is filled in
    leftover-first, so it can be lost whole but can never announce two
    written files while keeping a leftover to itself. A failure inside
    the two-line handler that drops the second one is not covered.
    Before this, the second failure replaced the first and the working
    files went unnamed.

    RESIDUAL TWO: one statement boundary after the last rename. Both
    files are in place the moment `Path.replace` returns, and the record
    that says so is set on the next line. A stop in between is reported
    as a run caught mid-move: every name is looked at and named, the
    set-aside earlier profile is named and not removed, and the two
    outputs are described as holding a file synthtwin cannot attribute
    to one side of the move or the other. Two things about that report
    are worse than the facts -- it opens by saying synthtwin could not
    put things back, when nothing needed putting back, and it says the
    outputs cannot be attributed, when the move had landed. Nothing it
    says is a claim of safety that is not there: it sends the reader to
    look at files that are in fact correct. It is one statement wide,
    and there is nowhere to put the record that would close it, because
    a rename returning and the recording of that return cannot be one
    operation. A stop anywhere AFTER that line, including on the way
    back out of this function, is reported exactly: both files written,
    and the set-aside earlier profile named if it is still there.

    What this does NOT promise: the two renames are two steps, not one,
    so a machine that loses power between them can leave a new profile
    beside an old summary. No filesystem this package may reach offers a
    two-file atomic commit, and the call that forces a write to the disk
    is outside the import allowlist (plan D6.2), so durability against a
    power cut is not claimed. A power cut is also the one failure that
    leaves no sentence anywhere, because nothing runs afterwards to
    write one -- an interrupted PROGRAM is covered, a stopped MACHINE is
    not. Nor is there safety against another program changing these very
    names in the moment between synthtwin looking and synthtwin writing;
    that residual is named in SECURITY.md.

    Nor is a stop inside a creation promised a CLEAN folder, and the
    reason is a bound worth stating plainly. Exclusive creation also
    fails when the name was already taken, so a name reached for and
    never seen to be created may hold an empty file synthtwin made and
    may equally hold a file that was already there or that another
    program made in the same moment. Nothing here can tell those apart,
    and deleting the second would turn a run that failed to mention a
    file into a run that destroyed somebody's data. So such a name is
    NAMED to the person and never removed: a run stopped in that one
    moment can leave one empty file of synthtwin's making behind, and
    the sentence says where it is and why it was left.

    What IS claimed, and the scope is ONE failure: no single failure
    this code can observe -- a full disk, a refused permission, a
    vanished folder, a name already taken, memory exhausted, a person
    pressing Ctrl-C, at any statement of the writes, of the renames, or
    of the creation of a working name -- leaves a partial file, an
    unrecoverable one, or a file this run did not name to the person.
    A SECOND failure arriving while the first is being described can
    leave a working file unnamed; that is RESIDUAL ONE above, and it is
    the reason the claim says "single" rather than "any".
    """
    first = pathlib.Path(profile_path)
    second = pathlib.Path(summary_path)
    _refuse_unless_plain_file(first, words)
    _refuse_unless_plain_file(second, words)
    if is_the_same_file(first, second):
        raise errors.ProfileError(
            errors.outputs_are_the_same_file(f"{first}", f"{second}")
        )
    forbidden = [first, second]
    if table_path is not None:
        source = pathlib.Path(table_path)
        if is_the_same_file(first, source) or is_the_same_file(second, source):
            raise errors.ProfileError(
                errors.output_would_replace_the_table(f"{source}", words)
            )
        forbidden = forbidden + [source]

    # EVERYTHING THE HANDLER WILL NEED IS BOUND HERE, before the guard
    # opens -- and this is the only place it can be done, because right
    # now nothing of synthtwin's making is on disk. Not one file has
    # been created and not one name has been reached for, so a stop
    # anywhere in these six lines leaves the folder exactly as the run
    # found it and there is nothing to clear away or name.
    #
    # From the `try` below to the end of this function there is no other
    # setup: the guard is entered first and the work happens inside it,
    # so no statement can run at a moment when a file synthtwin made is
    # on disk and no handler is watching. The earlier shape kept a
    # second guard further in and built part of its inventory after
    # opening it, which left both windows the review found: a stop
    # before that guard, and stops inside it that raised
    # UnboundLocalError from the handler and lost the original failure
    # (review item P1-R8-F1).
    #
    # What each working file can be holding if this stops right now:
    # both start empty, and each is marked as possibly holding text
    # BEFORE its write begins rather than after, because a write that
    # stops half way has already put some of the description there.
    first_part: pathlib.Path | None = None
    second_part: pathlib.Path | None = None
    first_holds = errors.ON_DISK_EMPTY_WORKING
    second_holds = errors.ON_DISK_EMPTY_WORKING
    # Every working name this run reaches for, recorded BEFORE it is
    # reached for. A local variable can only hold a name once the call
    # that produced it has handed back, and the file is on disk a moment
    # earlier than that (review item P1-R8-F1).
    claimed = _Claimed([])
    # And how far the renaming got, which only `_move_into_place` can
    # say. It is made HERE rather than in there so that the renaming
    # step needs no prologue of its own to be guarded.
    progress = _Progress()
    try:
        first_part, trouble, owned = _claim_working_name(
            first, PART_SUFFIX, forbidden, words, claimed
        )
        if first_part is None:
            raise _stopped_clean(trouble, first, second, owned, words)
        second_part, trouble, owned = _claim_working_name(
            second, PART_SUFFIX, forbidden + [first_part], words, claimed
        )
        if second_part is None:
            raise _stopped_clean(
                trouble,
                first,
                second,
                [(first_part, errors.ON_DISK_EMPTY_WORKING)] + owned,
                words,
            )

        first_holds = errors.ON_DISK_WORKING
        trouble, holds = _write_part(first_part, profile_text, words)
        if trouble:
            raise _stopped_clean(
                trouble,
                first,
                second,
                [
                    (first_part, holds),
                    (second_part, errors.ON_DISK_EMPTY_WORKING),
                ],
                words,
            )
        second_holds = errors.ON_DISK_WORKING
        trouble, holds = _write_part(second_part, summary_text, words)
        if trouble:
            raise _stopped_clean(
                trouble,
                first,
                second,
                [
                    (first_part, errors.ON_DISK_WORKING),
                    (second_part, holds),
                ],
                words,
            )

        # The renaming runs INSIDE this same guard rather than under one
        # of its own. There is no instant between the two, because there
        # are no longer two: the call, the arguments it evaluates, and
        # everything the renaming does are all under the handler that was
        # opened before the first working name existed.
        return _move_into_place(
            first,
            second,
            first_part,
            second_part,
            forbidden,
            progress,
            words,
            claimed,
        )
    except errors.TransactionRefusal:
        # Composed by this transaction, which is a fact about the object
        # and not a guess from its type: `_stopped_clean` and
        # `_stopped_broken` are the only two places that build one, and
        # each has run the cleanup and put the state of every name into
        # the message before handing it back. Doing either again would
        # give the reader two different accounts of one folder.
        raise
    except BaseException:
        # ANYTHING else, and the handler does not ask what. This is the
        # repair for review item P1-R7-F1: two earlier versions each
        # caught the exception types their author had thought of, and
        # the next type escaped with a data-bearing working file behind
        # it. An unexpected `ProfileError` reaches here too, and must:
        # the type says which words a refusal uses, never that a cleanup
        # has run (review item P1-R8-F1). A failure that reaches here
        # keeps its type and its message -- the caller has advice for it
        # that this module does not -- and what this module owes the
        # person is the other half: the working files gone, and a
        # sentence saying what is at each name.
        try:
            _describe_the_stop(
                state,
                first,
                second,
                first_part,
                first_holds,
                second_part,
                second_holds,
                progress,
                claimed,
                words,
            )
        except BaseException:  # noqa: BLE001,S110 -- the drop IS the repair.
            # A SECOND failure while the first was being described. It
            # is dropped, and the first continues below with its own
            # type and message: the caller's advice belongs to the
            # first, and replacing it would leave the person reading
            # about an interrupt they pressed instead of the reason the
            # run stopped. The sentence is composed and stored in one
            # step, so what is lost here is the whole sentence, never
            # half of one; the record of a finished write is filled in
            # leftover-first, so it too is lost whole rather than left
            # announcing two files while keeping a leftover back.
            pass
        raise


# -- the one-target form (plan P3-D1) ---------------------------------
#
# `validate` writes ONE file. Two-files-or-neither is not a rule it can
# keep, because there is no second file to keep it with -- so the
# transaction gains a form that keeps every OTHER rule: the working name
# of synthtwin's own making, the rename into place, the earlier file set
# aside so it can come back, the cleanup that looks rather than assumes,
# and the sentence naming every file on disk after a stop.
#
# What is genuinely different is the guarded source. The two-file form
# spares ONE file the command was handed. This one spares a SET, because
# `validate` is handed two files and neither may be written over: the
# description the verdicts are measured against, and the file being
# measured, which may be somebody's own table. The same-file machinery
# is the shipped one -- `is_the_same_file` and `_is_one_of`, unchanged --
# and what widens is only the list it is asked about.
#
# Every primitive below this comment is shared with the two-file form:
# the working-name claim, the part write, the removal that checks by
# looking, the state codes, and both sentences a person reads. Only the
# ORDER of steps is written twice, because one rename is not two.


def _state_nothing_published_one(
    target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    words: errors.ArtifactWords,
    target_code: str = errors.ON_DISK_BEFORE,
) -> str:
    """The nothing-was-published sentence, for one output name.

    `_state_nothing_published`'s reasoning at one file: the output holds
    what it held, and the only names that can have changed are
    synthtwin's own working files, each of which is removed here or
    named with what it holds.
    """
    left = _clear_away(leftovers)
    on_disk = [
        _named_state(target, target_code, errors.ON_DISK_ABSENT)
    ] + left
    return errors.nothing_was_written([], on_disk, words)


def _state_part_way_through_one(
    target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    kept: "pathlib.Path | None",
    kept_holds_the_earlier_file: bool,
    words: errors.ArtifactWords,
) -> str:
    """The same, for a stop once the rename into place had begun.

    The output name is between one state and another and this code
    cannot say which side of the move it is on, so a file that IS there
    is described as the unsettled thing it is. A name that is EMPTY is
    described by what this run did: with an earlier file set aside, it
    was taken away and is named under its working name; with none, there
    was never a file there and there is none now.

    The set-aside name is never guessed at and never removed, for the
    reason the two-file form gives: it is the one file under these names
    that this run did not produce.
    """
    left = _clear_away(leftovers)
    if kept is None:
        empty_target = errors.ON_DISK_ABSENT
    else:
        empty_target = errors.ON_DISK_TAKEN_AWAY
    on_disk = [_named_state(target, errors.ON_DISK_UNSETTLED, empty_target)]
    if kept is not None:
        holds = errors.ON_DISK_UNSETTLED
        if kept_holds_the_earlier_file:
            holds = errors.ON_DISK_SET_ASIDE
        on_disk = on_disk + [
            _named_state(kept, holds, errors.ON_DISK_ABSENT)
        ]
    return errors.rollback_failed([], on_disk + left, words)


def _stopped_clean_one(
    trouble: str,
    target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    words: errors.ArtifactWords,
    target_code: str = errors.ON_DISK_BEFORE,
) -> errors.TransactionRefusal:
    """One-target refusal for a failure that published nothing.

    The type is true here on the same terms as the two-file form's:
    `_state_nothing_published_one` clears the working files away and
    looks at every name before this returns, so the object handed back
    carries a cleanup that has run and a message that names every file.
    """
    return errors.TransactionRefusal(
        f"{trouble} "
        f"{_state_nothing_published_one(target, leftovers, words, target_code)}"
    )


def _stopped_broken_one(
    trouble: str,
    target: pathlib.Path,
    kept: "pathlib.Path | None",
    leftovers: "list[tuple[pathlib.Path, str]]",
    words: errors.ArtifactWords,
) -> errors.TransactionRefusal:
    """One-target refusal for a failure whose own undoing did not finish."""
    left = _clear_away(leftovers)
    on_disk = [
        _named_state(target, errors.ON_DISK_NEW, errors.ON_DISK_TAKEN_AWAY)
    ]
    if kept is not None:
        on_disk = on_disk + [
            _named_state(
                kept, errors.ON_DISK_SET_ASIDE, errors.ON_DISK_ABSENT
            )
        ]
    return errors.TransactionRefusal(
        f"{trouble} {errors.rollback_failed([], on_disk + left, words)}"
    )


def _finished_one(
    state: "DiskState | None", kept: "pathlib.Path | None"
) -> None:
    """Record that the file reached its name, for a stop after that.

    `_finished`'s reasoning at one file: the rename has returned, so the
    output name holds this run's file and there is nothing to put back.
    A failure arriving from here on is not a rollback and may not be
    described as one.

    `left_behind` is set before the flag, so a second stop inside this
    function can cost the whole report but can never announce a written
    file while keeping a leftover to itself.
    """
    if state is None:
        return
    if kept is not None and _what_is_there(kept) != "nothing":
        state.left_behind = f"{pathlib.Path(kept)}"
    state.target_written = True


def _describe_the_stop_one(
    state: "DiskState | None",
    target: pathlib.Path,
    part: "pathlib.Path | None",
    holds: str,
    progress: _Progress,
    claimed: "_Claimed | None",
    words: errors.ArtifactWords,
) -> None:
    """Clear up after a failure nobody composed; say what is on disk.

    Everything this needs arrives as an argument, for the reason
    `_describe_the_stop` gives: the handler that calls it holds no value
    it had to compute after the guard opened, so no stop inside the
    guarded work can turn the person's failure into an UnboundLocalError
    raised from the cleanup.
    """
    if progress.installed:
        _finished_one(state, progress.kept)
        return
    waiting: list[tuple[pathlib.Path, str]] = []
    if part is not None:
        waiting = waiting + [(part, holds)]
    known = [f"{target}"]
    for place, _code in waiting:
        known = known + [f"{place}"]
    if progress.kept is not None:
        known = known + [f"{progress.kept}"]
    extra = _unclaimed(claimed, known)
    if progress.moving:
        _remember(
            state,
            _state_part_way_through_one(
                target, waiting + extra, progress.kept, progress.aside, words
            ),
        )
        return
    if progress.kept is not None:
        # Claimed for the earlier file, and the move of that file into it
        # had not begun: the name holds the empty file synthtwin created
        # there, which is synthtwin's own to clear away.
        waiting = waiting + [(progress.kept, errors.ON_DISK_EMPTY_WORKING)]
    _remember(
        state, _state_nothing_published_one(target, waiting + extra, words)
    )


def _move_one_into_place(
    target: pathlib.Path,
    part: pathlib.Path,
    forbidden: "list[pathlib.Path]",
    sources: "list[tuple[pathlib.Path, str]]",
    progress: _Progress,
    words: errors.ArtifactWords,
    claimed: "_Claimed | None" = None,
) -> "list[str]":
    """The rename itself; `write_one_file` holds the handler around it.

    Nothing is set up in here that the handler needs. Every name the
    handler describes it already had before it opened, and the two
    answers only this function can give -- how far the move got, and
    whether the file reached its name -- are written into ``progress`` as
    they become true, never inferred afterwards.

    THE SECOND SAME-FILE QUESTION IS ASKED HERE, once the file really is
    at the output name (plan P3-D1: no substitution between the check
    and the write). Before the rename, a guarded source and an output
    name that does not exist yet can be one file on a filesystem that
    folds their spellings together, and the shipped identity check
    answers what it can from the resolved paths alone. Afterwards both
    names exist and the filesystem itself settles it -- so it is asked
    again, and a run that finds the output has become one of its own
    inputs is undone rather than reported as finished.
    """
    place = pathlib.Path(target)
    new_file = pathlib.Path(part)
    holding = [(new_file, errors.ON_DISK_WORKING)]

    what = _what_is_there(place)
    if what == "unknown":
        raise _stopped_clean_one(
            errors.output_not_writable(
                f"{place}", errors.COULD_NOT_CHECK, words
            ),
            place,
            holding,
            words,
        )
    if what == "folder":
        raise _stopped_clean_one(
            errors.output_is_a_folder(f"{place}"), place, holding, words
        )
    if what == "link" or what == "other":
        raise _stopped_clean_one(
            errors.output_is_not_a_plain_file(f"{place}"),
            place,
            holding,
            words,
        )

    kept: pathlib.Path | None = None
    if what == "file":
        # An earlier report is there. It moves to a working name of
        # synthtwin's own making -- not over anything -- so that it can
        # come back if the rest of the run does not finish.
        spare = forbidden + [new_file]
        aside_name, trouble, owned = _claim_working_name(
            place, KEPT_SUFFIX, spare, words, claimed
        )
        if aside_name is None:
            raise _stopped_clean_one(trouble, place, holding + owned, words)
        kept = aside_name
        progress.kept = aside_name
        # From here the output is between one state and another, and a
        # failure this function did not foresee can no longer be
        # described as "nothing was touched".
        progress.moving = True
        try:
            place.replace(kept)
        except OSError as error:
            raise _stopped_clean_one(
                errors.output_not_writable(f"{place}", f"{error}", words),
                place,
                holding + [(kept, errors.ON_DISK_EMPTY_WORKING)],
                words,
            ) from error
        # And now that name holds the earlier report for certain, which
        # is a different thing to tell a person from "it holds either
        # that report or an empty file synthtwin made".
        progress.aside = True

    progress.moving = True
    try:
        new_file.replace(place)
    except OSError as error:
        # The move did not happen, so the working file is still sitting
        # at its own name holding the whole report. It goes in the
        # leftovers, where the cleanup removes it and the message names
        # it if it will not go -- passing an empty list here would
        # report a clean folder with a real-derived file in it.
        trouble = errors.output_not_writable(f"{place}", f"{error}", words)
        if _take_out(kept, place):
            raise _stopped_clean_one(
                trouble, place, holding, words, _after_undo(kept)
            ) from error
        raise _stopped_broken_one(
            trouble, place, kept, holding, words
        ) from error

    # From here the working name is EMPTY: the move succeeded, so the
    # file that was under it is the file at the output name now. The two
    # refusals below therefore hand over no leftovers -- there is nothing
    # of this run's making left to clear away but the output itself,
    # which `_take_out` handles.
    landed = _lands_on_a_source(place, sources)
    if landed:
        trouble = errors.output_would_replace_an_input(
            f"{place}", landed, words
        )
        if _take_out(kept, place):
            raise _stopped_clean_one(
                trouble, place, [], words, _after_undo(kept)
            )
        raise _stopped_broken_one(trouble, place, kept, [], words)

    # The name now holds this run's file. From here there is nothing to
    # put back, and a failure that arrives after this line must not be
    # described as a rollback that could not finish. The rename above
    # and this line are two statements: a stop between them is the one
    # place where the move may have landed and this record does not yet
    # say so, and `write_one_file` states that bound rather than papering
    # over it.
    progress.installed = True

    if kept is None:
        return []
    if _remove_and_check(kept):
        return []
    # The file is written and correct; the only thing wrong is that the
    # earlier report is still sitting under a working name. It is
    # real-derived material, so it is handed back to the caller to be
    # reported rather than passed over in silence.
    return [f"{kept}"]


def _lands_on_a_source(
    target: pathlib.Path, sources: "list[tuple[pathlib.Path, str]]"
) -> str:
    """The noun of the guarded input ``target`` leads to, or "".

    `_is_one_of` answers the same question for a list of paths; this one
    is needed instead because a refusal has to say WHICH input was
    caught, and the two inputs of a check are not interchangeable to the
    person reading it.
    """
    for place, noun in sources:
        if is_the_same_file(target, place):
            return noun
    return ""


def write_one_file(
    target: pathlib.Path,
    text: str,
    sources: "list[tuple[pathlib.Path, str]] | None" = None,
    state: "DiskState | None" = None,
    words: errors.ArtifactWords = errors.PROFILE_WORDS,
) -> "list[str]":
    """Write one file whole, or leave the folder exactly as it was.

    THE ONE-TARGET FORM OF THE TRANSACTION (plan P3-D1). `validate`
    produces a single artifact, so two-files-or-neither is not a rule it
    can keep; every other rule this module keeps is kept here, in the
    same code, with the same wordings.

    THE RULE, stated so it can be checked: when this returns, the output
    name holds the text it was given. When it raises -- with ANY
    exception, not only the ones in this catalog -- that name holds
    exactly what it held before, the earlier file or nothing, unless the
    person is told otherwise; and they are told by name, every file that
    is on disk and what each one holds, checked by looking rather than
    assumed from what was attempted. The rule is about ONE failure: a
    second one arriving while the first is being described can cost the
    telling, which is `write_both_files`'s RESIDUAL ONE, unchanged.

    Guarantees:

    - Inputs: the output path, the whole text to put there, the files
      this command was handed with the noun each is called by, optionally
      a DiskState for the sentence a failure this module did not compose
      leaves behind, and optionally the words this command uses for its
      own files. Nothing but that text is written anywhere, so the
      published bytes never depend on which working name a run used.
    - THE GUARDED SOURCES ARE A SET, and that is the difference from the
      two-file form (plan P3-D1). Each is checked against the output
      name and against every working name, by lexical path, by resolved
      path, by the case-folded spelling a folding filesystem would treat
      as one, and by the filesystem's own identity where both names
      exist -- the shipped `is_the_same_file`, asked once per input. The
      question is asked AGAIN once the file is at the output name, where
      a substitution made between the check and the write becomes
      decidable, and a run that finds the output has become one of its
      inputs is undone. Left out, no source is guarded, which is right
      only for a caller that was handed no file.
    - The words: left out, the profiler's set is used, which is what
      makes every message this transaction composed before the parameter
      existed the same byte for byte. A command whose output is neither
      a profile nor a twin MUST pass its own set; nothing here can
      detect that it did not, and the cost of the omission is a person
      being sent to look at the wrong file.
    - Files touched: only files synthtwin itself created, plus the
      output name. A file of any other name that was already there is
      never written to and never removed -- the run stops instead and
      says which files are in the way.
    - Returns: the working files still on disk after an otherwise
      complete run, so the caller can report them. Normally empty.
    - Errors raised: ProfileError -- as `errors.TransactionRefusal`, one
      of its subclasses -- with a plain-language message for every
      refusal this module can describe, each carrying the state of every
      name. Anything else that can be raised in here leaves as itself,
      with the same type and the same message it had, after the cleanup
      has run and ``state`` has been given the sentence: the transaction
      may not rewrite a failure whose meaning belongs to somebody else.
    - The guard's own bounds: the handler is entered before the first
      working name is reached for, and every value it uses is bound
      before that -- so there is NO statement between "a file synthtwin
      made is on disk" and "a handler that will clear it away and name
      it is in force".

    What this does NOT promise is what the two-file form does not
    promise either: durability against a power cut, since the call that
    forces a write to the disk is outside the import allowlist (plan
    D6.2); safety against another program changing these very names
    between synthtwin looking and synthtwin writing, which SECURITY.md
    names; and a clean folder after a stop inside a creation, where a
    name reached for may hold an empty file synthtwin made and may
    equally hold one that was already there. Such a name is NAMED to the
    person and never removed.

    One promise the two-file form makes is absent here because there is
    nothing to promise: no pair of outputs can be left half-published,
    since there is no pair.
    """
    place = pathlib.Path(target)
    guarded = sources if sources is not None else []
    # THE SOURCE-AWARE QUESTION IS ASKED FIRST, and the order is the
    # whole of what it buys (review item P3-V1-F12). A link at the output
    # name pointing back at an input is BOTH a special entry and an
    # input, and the plain-file refusal answered first: the person was
    # told that something which is not an ordinary file is in the way,
    # which is true and is not the news. The news is that the name they
    # gave leads to one of the two files the check reads, and which one.
    # Nothing is lost by the swap -- a target that is a special entry and
    # not an input still meets the refusal below, on the next line.
    landed = _lands_on_a_source(place, guarded)
    if landed:
        raise errors.ProfileError(
            errors.output_would_replace_an_input(f"{place}", landed, words)
        )
    _refuse_unless_plain_file(place, words)
    forbidden = [place]
    for source, _noun in guarded:
        forbidden = forbidden + [pathlib.Path(source)]

    # EVERYTHING THE HANDLER WILL NEED IS BOUND HERE, before the guard
    # opens, and this is the only place it can be done: right now nothing
    # of synthtwin's making is on disk, so a stop anywhere in these four
    # lines leaves the folder exactly as the run found it. From the `try`
    # below to the end of this function there is no other setup.
    part: pathlib.Path | None = None
    holds = errors.ON_DISK_EMPTY_WORKING
    claimed = _Claimed([])
    progress = _Progress()
    try:
        part, trouble, owned = _claim_working_name(
            place, PART_SUFFIX, forbidden, words, claimed
        )
        if part is None:
            raise _stopped_clean_one(trouble, place, owned, words)

        # Marked as possibly holding text BEFORE the write begins rather
        # than after, because a write that stops half way has already put
        # some of the report there.
        holds = errors.ON_DISK_WORKING
        trouble, holding = _write_part(part, text, words)
        if trouble:
            raise _stopped_clean_one(
                trouble, place, [(part, holding)], words
            )

        # The rename runs INSIDE this same guard rather than under one of
        # its own. There is no instant between the two, because there are
        # no longer two.
        return _move_one_into_place(
            place, part, forbidden, guarded, progress, words, claimed
        )
    except errors.TransactionRefusal:
        # Composed by this transaction, which is a fact about the object
        # and not a guess from its type: the two `_stopped_*_one`
        # builders are the only places that make one, and each has run
        # the cleanup and put the state of every name into the message
        # before handing it back.
        raise
    except BaseException:
        # ANYTHING else, and the handler does not ask what -- the repair
        # `write_both_files` carries, kept here rather than reasoned
        # about again. A failure that reaches here keeps its type and its
        # message, because the caller has advice for it that this module
        # does not.
        try:
            _describe_the_stop_one(
                state, place, part, holds, progress, claimed, words
            )
        except BaseException:  # noqa: BLE001,S110 -- the drop IS the repair.
            # A SECOND failure while the first was being described. It is
            # dropped and the first continues below with its own type and
            # message, for the reason `write_both_files` states: the
            # caller's advice belongs to the first.
            pass
        raise


def write_text_file(
    target: pathlib.Path,
    text: str,
    words: errors.ArtifactWords = errors.PROFILE_WORDS,
) -> None:
    """Write ``text`` to ``target`` as UTF-8 with newline line endings.

    Guarantees:

    - Inputs: one local path, the whole text to put there, and the words
      this command uses for its own files. Left out, the profiler's
      words are used, which is the wording this function's refusal has
      always had.
    - Determinism: the same text gives the same bytes on every platform.
      The newline is fixed rather than left to the platform, so a profile
      written on Windows and one written on Linux are the same bytes
      (plan D12).
    - Errors raised: PathValidationError when the path is not a plain
      local one -- the check runs immediately before the write, so it is
      raised from here rather than settled by the caller earlier -- and
      ProfileError, with a plain-language message naming the file the
      running command writes, when the location cannot be written.
    - Boundary: one file is written and nothing is read.
    """
    validated = validate_local_path(f"{target}", purpose="output file")
    destination = pathlib.Path(validated)
    try:
        destination.write_text(text, encoding="utf-8", newline="\n")
    except OSError as error:
        raise errors.ProfileError(
            errors.output_not_writable(f"{destination}", f"{error}", words)
        ) from error
