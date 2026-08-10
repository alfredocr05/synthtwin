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

# Version 2: the settings block no longer reproduces the values the
# person declared with --keep-value and --missing-value; it records how
# many were named each way and the rule that matched them (review item
# P1-R7-F2). The field exists so that a change of this kind is explicit
# rather than something a consumer has to detect (plan P1-D5), so it
# moves with the change rather than after it.
#
# The wording of DECLARATION_PUBLICATION below was corrected afterwards
# without moving this number, and deliberately: no key changed shape and
# no key appeared or left, so a consumer's reading code is unaffected,
# and the token IS its own discriminator -- it names the rule in force,
# which is the one thing it exists to do. Version 2 has never been
# published, so the only profiles carrying the earlier token were
# written by a development tree.
#
# Version 3: a column the person declared with --identifier carries one
# new key, `n_distinct_by_occurrences` -- how many different values of
# it cover one row, two rows, and so on (review item P1-R8-F4, closed by
# owner decision). A key APPEARED, and a consumer that reads a v2
# profile will not find it, which is exactly the kind of change this
# number exists to make explicit rather than leave to be detected. Under
# v2 two declared columns with different repetition patterns serialized
# to identical bytes, so the profile could not be the generator's only
# input for them; `taxonomy._n_distinct_by_occurrences` states the key
# form and what the mapping does and does not disclose. Nothing else
# about the document moved: no other role gained or lost a key, and no
# value of any column is published that was not published before.
PROFILE_VERSION = 3

# The two files a run writes, as suffixes added to the table's name.
PROFILE_SUFFIX = "-profile.json"
SUMMARY_SUFFIX = "-profile.txt"

# What the profile's SETTINGS BLOCK records about a value the person
# declared with --keep-value or --missing-value, what it deliberately
# does not, and -- just as important -- what it does not claim about the
# rest of the document.
#
# A declaration is compared against every cell of every column, and the
# person types one BECAUSE that value is in their table. Writing the
# spelling into the settings therefore publishes a source value out of
# every column at once -- including the columns whose values never
# appear in a profile at all (record numbers, free text) and the labels
# held back for being shared by too few rows. The settings block did
# exactly that: a rare narrative value supplied as --missing-value was
# serialized verbatim while the column holding it published nothing,
# and the summary said nothing about it (review item P1-R7-F2).
#
# THE RULE: the settings block carries the POLICY -- how many values
# were named each way, and the rule that matched them -- and never a
# spelling. That is what the settings block was always for: a reader has
# to be able to tell WHICH RULES produced a profile, never which values
# the table held. No per-column exemption is made, and the reasons are
# that a declaration is table-wide (one spelling is compared against
# every cell of every column, so it could only be published if it were
# publishable in all of them, free-text and record-number columns
# included), that the typing of it is itself evidence about the source
# table whether or not any one cell matches, and that an exemption would
# have to be re-derived for every role and every publication rule added
# later -- which is a rule that will one day be missed.
#
# WHAT THIS RULE DOES NOT SAY. It governs the settings block and nothing
# else. Declaring a value does not withdraw that value from its own
# column: one named with --keep-value is data from that point on and is
# described wherever its column publishes values, and one named with
# --missing-value is counted as absent, its spelling reaching
# `missing_by_source` under the same small-cell floor and the same role
# rule as any other missing spelling. The first wording of this token,
# `counts_only_no_spellings`, read as a claim about the whole document,
# and that claim is false: 200 readings and three cells of `-999`,
# profiled with `--keep-value -999`, publish `"min": -999.0`. That
# publication is CORRECT -- a kept value is an ordinary number of the
# column and a range is made of real values -- and it is not "counts
# only, no spellings". The token now names its own scope, so that a
# consumer or an auditor reading it cannot draw the wider conclusion.
DECLARATION_PUBLICATION = "settings_counts_only_columns_unchanged"


@dataclasses.dataclass(frozen=True)
class WrittenProfile:
    """Where a run put its two files, and what it put in them."""

    document: dict[str, object]
    profile_path: pathlib.Path
    summary_path: pathlib.Path


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

    All three fields are for the caller to print; nothing here decides
    what to say about them.
    """

    sentence: str = ""
    both_files_written: bool = False
    left_behind: str = ""


def _version() -> str:
    """The installed synthtwin version, or a plain placeholder."""
    try:
        return importlib.metadata.version("synthtwin")
    except Exception:  # noqa: BLE001 -- the import allowlist (plan
        # D6.2) permits only importlib.metadata.version, so the
        # specific PackageNotFoundError name cannot be referenced.
        return "0+unknown"


def _declaration_record(spellings: "tuple[str, ...]") -> dict[str, object]:
    """How many values were declared this way -- and never which ones.

    Guarantees:

    - Inputs: the spellings the person typed for one of the two options.
    - Determinism: the record depends only on how many there are.
    - Errors raised: none.
    - Boundary: no spelling reaches the result, so nothing a person
      typed can travel out of this machine through the settings block
      (review item P1-R7-F2). The reason it may not is in
      DECLARATION_PUBLICATION above.

    The shape is deliberately NOT a list. A consumer holding a profile
    written before this rule finds a list of spellings under the same
    key; one written after it finds this record, and can tell the two
    apart without guessing. Dropping the key instead would have made the
    two indistinguishable, which is the failure this shape avoids.
    """
    return {
        "n_declared": len(spellings),
        "values_recorded": False,
    }


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

    Two of those settings are recorded by POLICY rather than by value:
    `kept_values` and `declared_missing_values` hold values of the real
    table, so what appears here is how many were named each way, beside
    the matching rule and the publication rule that governs them. The
    block still carries a key for every field of Settings, so the
    completeness check is unchanged; what changed is that two of those
    keys no longer reproduce source text (review item P1-R7-F2).
    """
    return {
        "small_cell_floor": settings.small_cell_floor,
        "identifier_uniqueness": settings.identifier_uniqueness,
        "identifier_minimum_rows": settings.identifier_minimum_rows,
        "minimum_parse_rate": settings.minimum_parse_rate,
        "categorical_share": settings.categorical_share,
        "categorical_ceiling": settings.categorical_ceiling,
        "categorical_floor": settings.categorical_floor,
        "sentinel_outlier_iqr_multiple": (
            settings.sentinel_outlier_iqr_multiple
        ),
        "sentinel_minimum_share": settings.sentinel_minimum_share,
        "kept_values": _declaration_record(settings.kept_values),
        "declared_missing_values": _declaration_record(
            settings.declared_missing_values
        ),
        "declaration_matching": settings.declaration_matching,
        "declaration_publication": DECLARATION_PUBLICATION,
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
      kind reaches the document. The settings block records how many
      values were named with --keep-value and --missing-value and the
      rule that matched them, never the spellings (review item
      P1-R7-F2). Declaring a value does not take it out of its own
      column, and this docstring does not claim it does: a kept value
      is data from that point on and is described wherever its column
      publishes values, and a declared-missing value is counted absent
      with its spelling published only under the same floor and role
      rules as any other missing spelling. DECLARATION_PUBLICATION
      above states the scope of the settings rule exactly.
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
                errors.output_not_writable(f"{candidate}", f"{error}"),
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
        trouble = errors.output_not_writable(f"{candidate}", detail)
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
    return errors.nothing_was_written([], on_disk)


def _state_part_way_through(
    target: pathlib.Path,
    summary_target: pathlib.Path,
    leftovers: "list[tuple[pathlib.Path, str]]",
    kept: "pathlib.Path | None",
    kept_holds_the_earlier_profile: bool,
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
    return errors.rollback_failed([], on_disk + left)


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
    target_code: str = errors.ON_DISK_BEFORE,
) -> errors.TransactionRefusal:
    """The refusal for a failure that published nothing, with the disk in it.

    One of the two places a `TransactionRefusal` is built, and the type
    is true here: `_state_nothing_published` clears the working files
    away and looks at every name before this returns, so the object
    handed back carries a cleanup that has run and a message that names
    every file. The transaction's handler relies on exactly that.
    """
    return errors.TransactionRefusal(
        f"{trouble} "
        f"{_state_nothing_published(target, summary_target, leftovers, target_code)}"
    )


def _stopped_broken(
    trouble: str,
    target: pathlib.Path,
    summary_target: pathlib.Path,
    kept: "pathlib.Path | None",
    leftovers: "list[tuple[pathlib.Path, str]]",
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
        f"{trouble} {errors.rollback_failed([], on_disk + left)}"
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
    claimed: "_Claimed | None" = None,
) -> "list[str]":
    """The renaming itself; `write_both_files` holds the handler around it.

    Nothing is set up in here that the handler needs. Every name the
    handler describes it already had before it opened, and the two
    answers only this function can give -- how far the renaming got, and
    whether both files reached their names -- are written into
    ``progress`` as they become true, never inferred afterwards.
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
        spare = forbidden + [new_profile, new_summary]
        aside_name, trouble, owned = _claim_working_name(
            target, KEPT_SUFFIX, spare, claimed
        )
        if aside_name is None:
            raise _stopped_clean(
                trouble, target, summary_target, both + owned
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
                errors.output_not_writable(f"{target}", f"{error}"),
                target,
                summary_target,
                both + [(kept, errors.ON_DISK_EMPTY_WORKING)],
            ) from error
        # And now that name holds the earlier profile for certain, which
        # is a different thing to tell a person from "it holds either
        # that profile or an empty file synthtwin made".
        progress.aside = True

    progress.moving = True
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


def _write_part(part: pathlib.Path, text: str) -> "tuple[str, str]":
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
    """
    place = pathlib.Path(part)
    try:
        write_text_file(place, text)
    except PathValidationError as error:
        return (
            errors.output_not_writable(f"{place}", f"{error}"),
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
            ),
        )
        return
    if progress.kept is not None:
        # Claimed for the earlier profile, and the move of that profile
        # into it had not begun: the name holds the empty file synthtwin
        # created there, which is synthtwin's own to clear away.
        waiting = waiting + [(progress.kept, errors.ON_DISK_EMPTY_WORKING)]
    _remember(state, _state_nothing_published(first, second, waiting + extra))


def write_both_files(
    profile_path: pathlib.Path,
    summary_path: pathlib.Path,
    profile_text: str,
    summary_text: str,
    table_path: "pathlib.Path | None" = None,
    state: "DiskState | None" = None,
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
      of the table being described, and optionally a DiskState for the
      sentence described above. Nothing but those texts is written
      anywhere, so the published bytes never depend on which working
      name a run happened to use.
    - Files touched: only files synthtwin itself created, plus the two
      output names. A file of any other name that was already there is
      never written to and never removed -- the run stops instead and
      says which files are in the way.
    - The table: ``table_path``, when given, is checked against every
      output and every working name, and the run stops before anything
      is written if any of them would lead to it.
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
            first, PART_SUFFIX, forbidden, claimed
        )
        if first_part is None:
            raise _stopped_clean(trouble, first, second, owned)
        second_part, trouble, owned = _claim_working_name(
            second, PART_SUFFIX, forbidden + [first_part], claimed
        )
        if second_part is None:
            raise _stopped_clean(
                trouble,
                first,
                second,
                [(first_part, errors.ON_DISK_EMPTY_WORKING)] + owned,
            )

        first_holds = errors.ON_DISK_WORKING
        trouble, holds = _write_part(first_part, profile_text)
        if trouble:
            raise _stopped_clean(
                trouble,
                first,
                second,
                [
                    (first_part, holds),
                    (second_part, errors.ON_DISK_EMPTY_WORKING),
                ],
            )
        second_holds = errors.ON_DISK_WORKING
        trouble, holds = _write_part(second_part, summary_text)
        if trouble:
            raise _stopped_clean(
                trouble,
                first,
                second,
                [
                    (first_part, errors.ON_DISK_WORKING),
                    (second_part, holds),
                ],
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
