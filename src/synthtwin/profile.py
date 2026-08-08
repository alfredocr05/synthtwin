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
from synthtwin.paths import validate_local_path
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


def _refuse_if_folder(target: pathlib.Path) -> None:
    """Refuse, before anything is written, if a folder owns ``target``."""
    place = pathlib.Path(target)
    if place.is_dir():
        raise errors.ProfileError(errors.output_is_a_folder(f"{place}"))


def _refuse_unless_plain_file(target: pathlib.Path) -> None:
    """Refuse an existing target that is not an ordinary file.

    A pipe accepts everything written to it and sends it to whoever is
    reading; a device swallows it. Neither is a place a description of
    real data may go, and neither is caught by asking whether the path
    is local (review item P1-R2-F7).
    """
    place = pathlib.Path(target)
    if not place.exists():
        return
    if place.is_dir():
        raise errors.ProfileError(errors.output_is_a_folder(f"{place}"))
    if not place.is_file():
        raise errors.ProfileError(
            errors.output_is_not_a_plain_file(f"{place}")
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
       overwrites their table costs the table.
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
    if not left.exists() or not right.exists():
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
PART_SUFFIX = ".synthtwin-part"
KEPT_SUFFIX = ".synthtwin-kept"


def _working_neighbour(target: pathlib.Path, suffix: str) -> pathlib.Path:
    """A working name beside ``target``, in the same folder.

    The same folder matters: renaming within one folder is a single
    filesystem operation, while moving between folders is a copy that
    can fail halfway.
    """
    place = pathlib.Path(target)
    return pathlib.Path(f"{place}{suffix}")


def _remove_quietly(target: pathlib.Path) -> bool:
    """Delete ``target``; return True when it is gone afterwards."""
    place = pathlib.Path(target)
    try:
        place.unlink()
    except FileNotFoundError:
        return True
    except OSError:
        return False
    return True


def _tidy_away(places: "list[pathlib.Path]") -> "list[str]":
    """Remove each working file; return the ones that would not go."""
    stubborn: list[str] = []
    for place in places:
        if not _remove_quietly(place):
            stubborn = stubborn + [f"{pathlib.Path(place)}"]
    return stubborn


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
    return True


def _commit(
    first: pathlib.Path,
    second: pathlib.Path,
    first_part: pathlib.Path,
    second_part: pathlib.Path,
) -> None:
    """Move both written files into place, or put everything back."""
    target = pathlib.Path(first)
    summary_target = pathlib.Path(second)
    new_profile = pathlib.Path(first_part)
    new_summary = pathlib.Path(second_part)
    kept: pathlib.Path | None = None
    if target.exists():
        kept = _working_neighbour(target, KEPT_SUFFIX)
        try:
            target.replace(kept)
        except OSError as error:
            trouble = errors.output_not_writable(f"{target}", f"{error}")
            stubborn = _tidy_away([new_profile, new_summary])
            raise errors.ProfileError(
                f"{trouble} {errors.nothing_was_written(stubborn)}"
            ) from error
    try:
        new_profile.replace(target)
    except OSError as error:
        trouble = errors.output_not_writable(f"{target}", f"{error}")
        undone = _put_back(kept, target)
        stubborn = _tidy_away([new_profile, new_summary])
        if undone:
            raise errors.ProfileError(
                f"{trouble} {errors.nothing_was_written(stubborn)}"
            ) from error
        left = stubborn
        if kept is not None:
            left = left + [f"{kept}"]
        raise errors.ProfileError(
            f"{trouble} {errors.rollback_failed(left)}"
        ) from error
    try:
        new_summary.replace(summary_target)
    except OSError as error:
        trouble = errors.output_not_writable(f"{summary_target}", f"{error}")
        undone = _put_back(kept, target)
        stubborn = _tidy_away([new_summary])
        if undone:
            raise errors.ProfileError(
                f"{trouble} {errors.nothing_was_written(stubborn)}"
            ) from error
        # The new profile is at the profile's name and the earlier one
        # could not be put back. Both are named, so the user can finish
        # by hand what synthtwin could not finish for them.
        left = [f"{target}"] + stubborn
        if kept is not None:
            left = left + [f"{kept}"]
        raise errors.ProfileError(
            f"{trouble} {errors.rollback_failed(left)}"
        ) from error
    if kept is not None:
        _remove_quietly(kept)


def write_both_files(
    profile_path: pathlib.Path,
    summary_path: pathlib.Path,
    profile_text: str,
    summary_text: str,
) -> None:
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
    file that is left and what it is.

    How: each file is written in full under a working name in the same
    folder, and only then are the two renamed into place, with an
    existing profile set aside first so it can be restored.

    What this does NOT promise: the two renames are two steps, not one,
    so a machine that loses power between them can leave a new profile
    beside an old summary. No filesystem this package may reach offers a
    two-file atomic commit, and the call that forces a write to the disk
    is outside the import allowlist (plan D6.2), so durability against a
    power cut is not claimed. What IS claimed is that no error this code
    can see -- a full disk, a refused permission, a vanished folder --
    leaves a partial file or an unrecoverable one.

    Raises ProfileError with a plain-language message.
    """
    first = pathlib.Path(profile_path)
    second = pathlib.Path(summary_path)
    _refuse_unless_plain_file(first)
    _refuse_unless_plain_file(second)
    if is_the_same_file(first, second):
        raise errors.ProfileError(
            errors.outputs_are_the_same_file(f"{first}", f"{second}")
        )
    first_part = _working_neighbour(first, PART_SUFFIX)
    second_part = _working_neighbour(second, PART_SUFFIX)
    # Two output names that differ can still produce two working names
    # that do not. The same fail-closed identity test that guards the
    # outputs guards these.
    if is_the_same_file(first_part, second_part):
        raise errors.ProfileError(
            errors.outputs_are_the_same_file(f"{first_part}", f"{second_part}")
        )
    try:
        write_text_file(first_part, profile_text)
        write_text_file(second_part, summary_text)
    except errors.ProfileError as error:
        stubborn = _tidy_away([first_part, second_part])
        raise errors.ProfileError(
            f"{error} {errors.nothing_was_written(stubborn)}"
        ) from error
    _commit(first, second, first_part, second_part)


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
