"""Building and writing the profile document (plan P1-D5, P1-D11).

The profile is the boundary artifact: everything downstream -- the
generator, the validator, the quality report -- will read this file and
never the real table. It is therefore written to be read by a program
AND by a person who wants to check what left their compliant
environment.

Two properties are deliberate:

* Nothing that varies between runs appears in it. There is no
  timestamp, no source path, no machine name, and no random anything,
  so the same table always produces the same bytes and a golden-hash
  test means what it says.
* Everything the rules decided travels with the result: the settings
  that produced the roles, the evidence for each role, and the notes
  saying what was withheld and why. A reader never has to guess which
  version of the rules made this file.

Imports here stay within the allowlist (plan D6.2): dataclasses,
importlib.metadata.version, json, pathlib, and this package's own
modules.
"""

import dataclasses
import importlib.metadata
import json
import pathlib

from synthtwin import errors, parsing, taxonomy
from synthtwin.paths import PathValidationError, validate_local_path
from synthtwin.reading import Table

PROFILE_VERSION = 1

# The two files a run writes, as suffixes added to the table's name.
PROFILE_SUFFIX = "-profile.json"
SUMMARY_SUFFIX = "-profile.txt"


@dataclasses.dataclass(frozen=True)
class WrittenProfile:
    """Where a run put its two files, and what it put in them."""

    document: dict[str, object]
    profile_path: pathlib.Path
    summary_path: pathlib.Path


def _version() -> str:
    """The installed synthtwin version, or a plain placeholder."""
    try:
        return importlib.metadata.version("synthtwin")
    except Exception:  # noqa: BLE001 -- the import allowlist (plan
        # D6.2) permits only importlib.metadata.version, so the
        # specific PackageNotFoundError name cannot be referenced.
        return "0+unknown"


def _settings_block(
    settings: taxonomy.Settings, forced_identifiers: list[str]
) -> dict[str, object]:
    """The rules that produced this profile, recorded inside it.

    Every setting is written out by name. The offline policy forbids
    reaching an attribute through a name computed while the program
    runs (plan D6.2), and a hand-written list is what a reader can
    check anyway. A setting added to Settings and forgotten here fails
    the completeness test in the suite, which compares this block with
    the dataclass's own field list.
    """
    return {
        "small_cell_floor": settings.small_cell_floor,
        "identifier_uniqueness": settings.identifier_uniqueness,
        "identifier_minimum_rows": settings.identifier_minimum_rows,
        "minimum_parse_rate": settings.minimum_parse_rate,
        "numeric_majority": settings.numeric_majority,
        "categorical_repetition": settings.categorical_repetition,
        "categorical_numeric_ceiling": settings.categorical_numeric_ceiling,
        "categorical_ceiling": settings.categorical_ceiling,
        "code_minimum_width": settings.code_minimum_width,
        "sentinel_outlier_iqr_multiple": (
            settings.sentinel_outlier_iqr_multiple
        ),
        "sentinel_minimum_share": settings.sentinel_minimum_share,
        "kept_values": sorted(settings.kept_values),
        "declared_missing_values": sorted(settings.declared_missing_values),
        "near_threshold_slack": settings.near_threshold_slack,
        "forced_identifiers": sorted(forced_identifiers),
    }


def _column_block(column: taxonomy.ColumnProfile) -> dict[str, object]:
    """One column's entry in the profile document."""
    missing: dict[str, int] = {}
    for spelling in sorted(column.missing_by_source):
        missing[spelling] = column.missing_by_source[spelling]
    classes: dict[str, int] = {}
    for name in sorted(column.missing_by_class):
        classes[name] = column.missing_by_class[name]
    block: dict[str, object] = {
        "name": column.name,
        "position": column.position,
        "role": column.role,
        "detection_evidence": column.detection_evidence,
        "n_present": column.n_present,
        "n_missing": column.n_missing,
        "missing_by_source": missing,
        "missing_by_class": classes,
        "remarks": column.remarks,
        # Always present, on every role: a count that appears only where
        # someone remembered it goes missing exactly when it matters
        # (review items P1-R3-F3 and P1-R1-F9). These are fields of
        # ColumnProfile rather than keys of `details`, so the profile
        # cannot carry them for one role and drop them for another.
        "n_numeric": column.n_numeric,
        "n_out_of_range": column.n_out_of_range,
        "n_contradictory": column.n_contradictory,
        "n_not_numeric": column.n_not_numeric,
        "n_distinct": column.n_distinct,
        "n_distinct_folded": column.n_distinct_folded,
        "sentinel_verdicts": column.sentinel_verdicts,
        "n_sentinel_candidates_unpublished": (
            column.n_sentinel_candidates_unpublished
        ),
    }
    for key in sorted(column.details):
        block[key] = column.details[key]
    return block


def build_document(
    table: Table,
    settings: taxonomy.Settings,
    forced_identifiers: list[str],
) -> dict[str, object]:
    """Describe a whole table: the profile document, ready to serialize.

    Guarantees:

    - Inputs: a Table as produced by the reader, the settings that
      govern the taxonomy, and the names of columns the user declared
      to be record numbers.
    - Determinism: the document depends only on those inputs. No clock,
      no environment, no random source, and every mapping written out
      is written in sorted key order.
    - Errors raised: TypeError if a cell is not text (an internal
      invariant of the readers).
    - Boundary: no file is opened here, and no value of a suppressed
      kind reaches the document.
    """
    columns: list[dict[str, object]] = []
    notes: list[dict[str, str]] = []
    for position, name in enumerate(table.column_names, start=1):
        described = taxonomy.profile_column(
            name,
            position,
            table.columns[position - 1],
            table.n_rows,
            settings,
            name in forced_identifiers,
        )
        columns = columns + [_column_block(described)]
        for note in described.publication_notes:
            notes = notes + [{"column": name, "note": note}]
    return {
        "profile_version": PROFILE_VERSION,
        "created_with": _version(),
        "settings": _settings_block(settings, forced_identifiers),
        # How the table was read. It belongs in the profile because the
        # twin has to be written in a form the same tools can open, and
        # it is fixed by the input bytes, so it does not make two runs
        # over the same file differ.
        "source": {
            "encoding": table.encoding,
            "used_fallback_encoding": table.used_fallback_encoding,
            # Where the column names came from: the file's own first row,
            # or names synthtwin generated because the reader could not
            # tell and the user said the first row was data. A consumer
            # must be able to tell those apart.
            "header_source": table.header_source,
            # Whether that first row was READ as names because the file
            # showed it was, or merely ASSUMED to be names because nothing
            # in the file said otherwise. The two are not the same claim,
            # and a consumer of this profile -- including Phase 2 -- must
            # not have to guess which one it is holding. When this is
            # true, the names may in fact be somebody's first record, and
            # `--first-row data` re-reads the file that way.
            "header_by_convention": table.header_by_convention,
            # The verdict in words, so a person reading the profile sees
            # the same sentence the summary gave them.
            "header_evidence": table.header_evidence,
        },
        "n_rows": table.n_rows,
        "n_columns": len(table.column_names),
        "columns": columns,
        "publication_notes": notes,
    }


def serialize(document: dict[str, object]) -> str:
    """Turn a profile document into its canonical text (plan D12).

    Guarantees: UTF-8 text with newline line endings, sorted keys, a
    two-space indent and fixed separators, and a trailing newline. The
    same document always produces exactly the same text. Raises
    ValueError through json if a value is not serializable, which
    cannot happen for documents this module builds.
    """
    return (
        json.dumps(
            document,
            sort_keys=True,
            indent=2,
            separators=(",", ": "),
            ensure_ascii=False,
            allow_nan=False,
        )
        + "\n"
    )


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


def _refuse_if_folder(target: pathlib.Path) -> None:
    """Refuse, before anything is written, if a folder owns ``target``."""
    place = pathlib.Path(target)
    what = _what_is_there(place)
    if what == "folder":
        raise errors.ProfileError(errors.output_is_a_folder(f"{place}"))
    if what == "unknown":
        raise errors.ProfileError(
            errors.output_not_writable(f"{place}", errors.COULD_NOT_CHECK)
        )


def _refuse_unless_plain_file(target: pathlib.Path) -> None:
    """Refuse an existing target that is not an ordinary file.

    A pipe accepts everything written to it and sends it to whoever is
    reading; a device swallows it. Neither is a place a description of
    real data may go, and neither is caught by asking whether the path
    is local (review item P1-R2-F7). A name that cannot be examined at
    all is refused too: an output this code could not look at is one it
    cannot promise anything about.
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
            errors.output_not_writable(f"{place}", errors.COULD_NOT_CHECK)
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


def _without_table_suffix(name: str) -> str:
    """Drop a .csv or .txt ending from a file name, whatever its case."""
    if not isinstance(name, str):
        raise TypeError("internal check: a file name was not text")
    # Each ending is tested on its own: the offline policy accepts a
    # text method only with arguments it has resolved, and a tuple
    # built at the call site is not one (plan D6.2).
    lowered = name.casefold()
    if lowered.endswith(".csv"):
        return name[: len(name) - 4]
    if lowered.endswith(".txt"):
        return name[: len(name) - 4]
    return name


def default_output_paths(
    table_path: pathlib.Path, out_dir: "str | None"
) -> "tuple[pathlib.Path, pathlib.Path]":
    """Where the two files go: beside the table unless a folder is given.

    Raises ProfileError with a plain-language message when a given
    folder does not exist, and PathValidationError when it is not a
    plain local path.
    """
    source = pathlib.Path(table_path)
    stem = _without_table_suffix(f"{source.name}")
    if out_dir is None:
        folder = pathlib.Path(source.parent)
    else:
        validated = validate_local_path(out_dir, purpose="output folder")
        folder = pathlib.Path(validated)
        if not folder.is_dir():
            raise errors.ProfileError(errors.output_folder_missing(f"{folder}"))
    # Every exact target goes through the locality gate, not just the
    # folder the user named. Phase 0's D6.1 rule covers output paths,
    # and review round 1 found the gap: a link left at the profile's
    # name sent the file wherever it pointed -- including, on POSIX,
    # over the user's own table.
    profile_target = validate_local_path(
        f"{folder / (stem + PROFILE_SUFFIX)}", purpose="output file"
    )
    summary_target = validate_local_path(
        f"{folder / (stem + SUMMARY_SUFFIX)}", purpose="output file"
    )
    first = pathlib.Path(profile_target)
    second = pathlib.Path(summary_target)
    _refuse_if_folder(first)
    _refuse_if_folder(second)
    return (first, second)




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


def _create_empty(candidate: pathlib.Path) -> "tuple[str, str]":
    """Create ``candidate`` as a new empty file; say how that went.

    Returns ("made", ""), ("taken", "") when something of that name is
    there already, or ("refused", detail) for anything else.

    The creation is exclusive: the filesystem itself settles who gets
    the name, in one step, and refuses when the name exists -- including
    when it is a link, whether or not the link leads anywhere. That is
    what makes a working name safe without any guessing about what is
    on the disk a moment before.
    """
    place = pathlib.Path(candidate)
    try:
        place.touch(exist_ok=False)
    except FileExistsError:
        return ("taken", "")
    except OSError as error:
        return ("refused", f"{error}")
    if _what_is_there(place) != "file":
        # Created a moment ago and already not an ordinary file: hand
        # it back rather than write a description of real data into it.
        return ("refused", errors.COULD_NOT_CHECK)
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
) -> pathlib.Path:
    """Create a new empty working file beside ``target`` and return it.

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
    to either output file. Raises ProfileError, with a message naming
    the leftovers to look at, when no candidate can be claimed.
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
            raise errors.ProfileError(
                errors.output_not_writable(f"{candidate}", f"{error}")
            ) from error
        if _what_is_there(candidate) != "nothing":
            continue
        if _is_one_of(candidate, forbidden):
            continue
        outcome, detail = _create_empty(candidate)
        if outcome == "made":
            return candidate
        if outcome == "taken":
            continue
        raise errors.ProfileError(
            errors.output_not_writable(f"{candidate}", detail)
        )
    raise errors.ProfileError(
        errors.working_name_unavailable(
            f"{place}", tried, WORKING_NAME_ATTEMPTS
        )
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
    """
    left: list[tuple[str, str]] = []
    for place, code in places:
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


def _stopped_clean(
    trouble: str,
    target: pathlib.Path,
    summary_target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    target_code: str = errors.ON_DISK_BEFORE,
) -> errors.ProfileError:
    """The refusal for a failure that published nothing, with the disk in it."""
    left = _clear_away(leftovers)
    on_disk = [
        _named_state(target, target_code, errors.ON_DISK_ABSENT),
        _named_state(
            summary_target, errors.ON_DISK_BEFORE, errors.ON_DISK_ABSENT
        ),
    ] + left
    return errors.ProfileError(
        f"{trouble} {errors.nothing_was_written([], on_disk)}"
    )


def _stopped_broken(
    trouble: str,
    target: pathlib.Path,
    summary_target: pathlib.Path,
    kept: "pathlib.Path | None",
    leftovers: "list[tuple[pathlib.Path, str]]",
) -> errors.ProfileError:
    """The refusal for a failure whose own undoing did not finish.

    The profile name holds the new description if anything at all, the
    summary name holds whatever it held before, and a set-aside earlier
    profile is named where one is still sitting.
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
    return errors.ProfileError(
        f"{trouble} {errors.rollback_failed([], on_disk + left)}"
    )


def _commit(
    first: pathlib.Path,
    second: pathlib.Path,
    first_part: pathlib.Path,
    second_part: pathlib.Path,
    forbidden: "list[pathlib.Path]",
) -> "list[str]":
    """Move both written files into place, or put everything back.

    Returns the working files still on disk when everything else
    succeeded -- normally none.
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
            errors.output_not_writable(f"{target}", errors.COULD_NOT_CHECK),
            target,
            summary_target,
            both,
        )
    if what == "folder":
        raise _stopped_clean(
            errors.output_is_a_folder(f"{target}"), target, summary_target, both
        )
    if what == "link" or what == "other":
        raise _stopped_clean(
            errors.output_is_not_a_plain_file(f"{target}"),
            target,
            summary_target,
            both,
        )

    kept: pathlib.Path | None = None
    if what == "file":
        # An earlier profile is there. It moves to a working name of
        # synthtwin's own making -- not over anything -- so that it can
        # come back if the rest of the run does not finish.
        try:
            spare = forbidden + [new_profile, new_summary]
            kept = _claim_working_name(target, KEPT_SUFFIX, spare)
        except errors.ProfileError as error:
            raise _stopped_clean(
                f"{error}", target, summary_target, both
            ) from error
        try:
            target.replace(kept)
        except OSError as error:
            raise _stopped_clean(
                errors.output_not_writable(f"{target}", f"{error}"),
                target,
                summary_target,
                both + [(kept, errors.ON_DISK_EMPTY_WORKING)],
            ) from error

    try:
        new_profile.replace(target)
    except OSError as error:
        trouble = errors.output_not_writable(f"{target}", f"{error}")
        if _put_back(kept, target):
            raise _stopped_clean(
                trouble,
                target,
                summary_target,
                both,
                _after_undo(kept),
            ) from error
        raise _stopped_broken(
            trouble, target, summary_target, kept, both
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
                _after_undo(kept),
            )
        raise _stopped_broken(
            trouble,
            target,
            summary_target,
            kept,
            [(new_summary, errors.ON_DISK_WORKING)],
        )

    try:
        new_summary.replace(summary_target)
    except OSError as error:
        trouble = errors.output_not_writable(f"{summary_target}", f"{error}")
        if _take_out(kept, target):
            raise _stopped_clean(
                trouble,
                target,
                summary_target,
                [(new_summary, errors.ON_DISK_WORKING)],
                _after_undo(kept),
            ) from error
        raise _stopped_broken(
            trouble,
            target,
            summary_target,
            kept,
            [(new_summary, errors.ON_DISK_WORKING)],
        ) from error

    if kept is None:
        return []
    if _remove_and_check(kept):
        return []
    # Both files are written and correct; the only thing wrong is that
    # the earlier profile is still sitting under a working name. It is
    # real-derived material, so it is handed back to the caller to be
    # reported rather than passed over in silence.
    return [f"{kept}"]


def write_both_files(
    profile_path: pathlib.Path,
    summary_path: pathlib.Path,
    profile_text: str,
    summary_text: str,
    table_path: "pathlib.Path | None" = None,
) -> "list[str]":
    """Write the two files as one outcome, or leave the folder untouched.

    The two files are one thing: the machine-readable profile is what
    the twin gets built from, and the summary is the only place the
    person is told what of their real data the profile carries. One of
    them alone is a failure state, and an earlier version produced
    several -- a half-written profile, a half-written summary nobody
    mentioned, and an earlier profile replaced with no way back (review
    item P1-R2-F11).

    THE RULE, stated so it can be checked: when this returns, both files
    hold the text it was given. When it raises, each of the two names
    holds exactly what it held before -- the earlier file, or nothing --
    unless the message says otherwise, and the message then names every
    file that is on disk and what each one holds, checked by looking
    rather than assumed from what was attempted.

    How: each file is written in full under a working name of
    synthtwin's own making in the same folder, and only then are the two
    renamed into place, with an existing profile set aside first so it
    can be restored.

    Guarantees:

    - Inputs: the two output paths, the two texts, and optionally the
      path of the table being described. Nothing but those texts is
      written anywhere, so the published bytes never depend on which
      working name a run happened to use.
    - Files touched: only files synthtwin itself created, plus the two
      output names. A file of any other name that was already there is
      never written to and never removed -- the run stops instead and
      says which files are in the way.
    - The table: ``table_path``, when given, is checked against every
      output and every working name, and the run stops before anything
      is written if any of them would lead to it.
    - Returns: the working files still on disk after an otherwise
      complete run, so the caller can report them. Normally empty.
    - Errors raised: ProfileError with a plain-language message, and
      PathValidationError for a path that is not a plain local one.

    What this does NOT promise: the two renames are two steps, not one,
    so a machine that loses power between them can leave a new profile
    beside an old summary. No filesystem this package may reach offers a
    two-file atomic commit, and the call that forces a write to the disk
    is outside the import allowlist (plan D6.2), so durability against a
    power cut is not claimed. Nor is safety against another program
    changing these very names in the moment between synthtwin looking
    and synthtwin writing; that residual is named in SECURITY.md. What
    IS claimed is that no error this code can see -- a full disk, a
    refused permission, a vanished folder, a name already taken -- leaves
    a partial file, an unrecoverable one, or a file this run did not
    describe honestly in its message.
    """
    first = pathlib.Path(profile_path)
    second = pathlib.Path(summary_path)
    _refuse_unless_plain_file(first)
    _refuse_unless_plain_file(second)
    if is_the_same_file(first, second):
        raise errors.ProfileError(
            errors.outputs_are_the_same_file(f"{first}", f"{second}")
        )
    forbidden = [first, second]
    if table_path is not None:
        source = pathlib.Path(table_path)
        if is_the_same_file(first, source) or is_the_same_file(second, source):
            raise errors.ProfileError(
                errors.output_would_replace_the_table(f"{source}")
            )
        forbidden = forbidden + [source]

    try:
        first_part = _claim_working_name(first, PART_SUFFIX, forbidden)
    except errors.ProfileError as error:
        raise _stopped_clean(f"{error}", first, second, []) from error
    try:
        second_part = _claim_working_name(
            second, PART_SUFFIX, forbidden + [first_part]
        )
    except errors.ProfileError as error:
        raise _stopped_clean(
            f"{error}",
            first,
            second,
            [(first_part, errors.ON_DISK_EMPTY_WORKING)],
        ) from error

    try:
        write_text_file(first_part, profile_text)
    except errors.ProfileError as error:
        raise _stopped_clean(
            f"{error}",
            first,
            second,
            [
                (first_part, errors.ON_DISK_WORKING),
                (second_part, errors.ON_DISK_EMPTY_WORKING),
            ],
        ) from error
    try:
        write_text_file(second_part, summary_text)
    except errors.ProfileError as error:
        raise _stopped_clean(
            f"{error}",
            first,
            second,
            [
                (first_part, errors.ON_DISK_WORKING),
                (second_part, errors.ON_DISK_WORKING),
            ],
        ) from error
    return _commit(first, second, first_part, second_part, forbidden)


def write_text_file(target: pathlib.Path, text: str) -> None:
    """Write ``text`` to ``target`` as UTF-8 with newline line endings.

    The newline is fixed rather than left to the platform, so a profile
    written on Windows and one written on Linux are the same bytes
    (plan D12).

    Raises ProfileError with a plain-language message when the location
    cannot be written.
    """
    validated = validate_local_path(f"{target}", purpose="output file")
    destination = pathlib.Path(validated)
    try:
        destination.write_text(text, encoding="utf-8", newline="\n")
    except OSError as error:
        raise errors.ProfileError(
            errors.output_not_writable(f"{destination}", f"{error}")
        ) from error
