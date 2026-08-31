"""Seeded neutral table builders for the Phase 1 tests (plan P1-D8).

No data file is ever committed (plan D13). Every table a test needs is
built here, from code, with a fixed seed, so the same test run produces
the same bytes on every machine and the repository holds no data-format
file at all.

The vocabulary is deliberately neutral and made up on the spot: labels
like "north" and "batch", column names like "reading" and "recorded_on".
Nothing here is derived from any real table.

`write_profile` lives here for the same reason the tables do: it is the
one place that decides the bytes of a description a test hands to the
loader, so no test has to decide them and no test can decide them
wrongly. Its docstring says what goes wrong when they are decided
anywhere else.
"""

import pathlib
import random

from synthtwin import canonical, contract as _contract

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent

# THE CONTRACT THAT GOVERNS, derived ONCE from the loader's own
# constant. Every check that reads the CURRENT contract takes it from
# here; only a reader that is deliberately historical names a version.
#
# Residual R-P4-25 is what this exists to stop happening again: the
# producer and the loader moved to version 6 and the governance checks
# went on reading version 4, agreeing by luck rather than by design.
# Six readers were pinned to a literal when that residual closed, and
# three review rounds found them in three passes -- so a bump that
# edited the producer and the loader alone would have left them
# certifying a document that no longer governs.
#
# THE PATH IS BUILT AT IMPORT AND CHECKED WHEN IT IS READ, not when it
# is built. The source distribution ships `tests` and `tools` and does
# NOT ship `docs`, and several measurement tools import this module
# without ever opening the contract; asserting at import time made
# `import fixtures` raise in an unpacked distribution for a tool that
# had no use for the document (review item P4-A1-R4-F3).
GOVERNING_CONTRACT = (
    REPO_ROOT
    / "docs"
    / "spec"
    / f"profile-contract-v{_contract.PROFILE_VERSION}.md"
)


def governing_contract_text() -> str:
    """The governing contract's text, or a refusal that says why.

    The check lives HERE, where the document is actually wanted, so a
    caller that never reads it is never stopped.
    """
    if not GOVERNING_CONTRACT.is_file():
        raise AssertionError(
            f"the contract that governs is version "
            f"{_contract.PROFILE_VERSION} and {GOVERNING_CONTRACT.name} is "
            "not in the tree: a version bump moves the producer, the loader "
            "and every current-contract reader together, or the governance "
            "checks go back to reading a document that governs nothing "
            "(residual R-P4-25). In a source distribution, note that `docs` "
            "is not shipped."
        )
    return GOVERNING_CONTRACT.read_text(encoding="utf-8")

# Neutral label pools. Small, plain words with no meaning outside these
# tests.
REGIONS = ("north", "south", "east", "west")
LABELS = ("alpha", "beta", "gamma", "delta", "epsilon")


def write(folder: pathlib.Path, name: str, text: str) -> pathlib.Path:
    """Write ``text`` as a UTF-8 file with newline endings; return its path."""
    target = folder / name
    target.write_text(text, encoding="utf-8", newline="\n")
    return target


def write_profile(
    folder: pathlib.Path, name: str, document: dict
) -> pathlib.Path:
    """Write ``document`` as a description file; return its path.

    THE GUARANTEE. The file left on disk is byte for byte the file
    `synthtwin profile` writes for that same document, on every
    platform. Two things carry it, and both are the product's own: the
    text is `canonical.serialize`, the serializer the loader re-writes
    with and compares against, and the write fixes the line ending
    rather than leaving it to the platform, exactly as
    `writing.write_text_file` does (plan D12).

    WHY IT EXISTS. A text-mode write with no ``newline`` argument
    translates every line ending to the platform's own, so the same two
    lines of Python leave newline bytes on Linux and macOS and
    carriage-return-newline bytes on Windows. The loader reads the file,
    writes the parsed document out again under the canonical rules, and
    refuses the file if the bytes differ -- so a description carrying
    the platform's line ending is a description it must refuse, and is
    right to refuse, because synthtwin did not write it. That is not a
    hypothetical: every Windows job of the test suite failed on it while
    every macOS and Linux job passed, with the loader and the writer
    both behaving exactly as specified. So the bytes are decided here,
    once, and a test that wants a description asks for one rather than
    building the file itself.

    Inputs: the folder to write into, the name of the file to write, and
    the profile document. Determinism: the same document gives the same
    bytes every time, on every platform.

    A test that deliberately needs bytes synthtwin would NOT write --
    proving the loader refuses them -- must not come through here. It
    writes its own exact bytes, with an explicit ``newline`` argument so
    that what it writes is what it meant on every platform too.
    """
    return write(folder, name, canonical.serialize(document))


def rows_to_csv(header: list[str], rows: list[list[str]]) -> str:
    """Turn a header and rows into CSV text, quoting only when needed."""
    lines = [",".join(header)]
    for row in rows:
        cells = []
        for cell in row:
            if "," in cell or '"' in cell or "\n" in cell:
                escaped = cell.replace('"', '""')
                cells.append(f'"{escaped}"')
            else:
                cells.append(cell)
        lines.append(",".join(cells))
    return "\n".join(lines) + "\n"


def every_role_table(seed: int = 20260807, n_rows: int = 240) -> str:
    """A table with one column for (almost) every role in the taxonomy.

    Columns, in order: a record number; a category with one rare label
    that the small-cell floor must withhold; whole numbers with blank
    cells; whole numbers using -999 as a stand-in for "no value"; a
    measured number; an ISO date; a two-value column; free text; a
    column that is entirely blank; a column with one repeated value;
    a column of numbers each wearing one shared piece of text; and a
    long tail of labels -- mostly one-off notes, with two words enough
    rows share to publish.

    The last of those is here because the battery is what stops the
    roles rotting: a role missing from this table is a role whose
    generator branch, validator checks and dispositions nothing walks,
    and every fix to it could be undone silently while the suite
    stayed green.
    """
    rng = random.Random(seed)
    header = [
        "record_code",
        "region",
        "visits",
        "reading",
        "amount",
        "recorded_on",
        "answer",
        "comment",
        "unused",
        "batch",
        "dose",
        "seen_at",
        "note",
    ]
    rows = []
    for index in range(n_rows):
        record = f"R{index:05d}"
        region = "outlying" if index % 37 == 0 else REGIONS[index % 4]
        visits = "" if index % 23 == 0 else str(rng.randint(0, 9))
        reading = "-999" if index % 19 == 0 else str(rng.randint(1, 400))
        amount = f"{rng.uniform(0.5, 99.5):.2f}"
        recorded = f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}"
        answer = "yes" if rng.random() < 0.3 else "no"
        # Drawn from a pool SMALLER than the number of filled cells, so
        # the column's repetition map holds more than one group size.
        # A column of eighty singletons has a map nothing can perturb --
        # every edit leaves it eighty singletons -- and the family
        # stops being reachable by any red case.
        # ALL DIFFERENT, which several batteries depend on: this is
        # one of the two columns that carry the all-different
        # obligation, and the length statistics of a column of unique
        # sentences are what the approximation bounds are calibrated
        # against. A column that REPEATS -- which the free-text
        # repetition family needs to be able to miss -- is built in the
        # battery that needs it, not here.
        comment = "" if index % 3 else _PROSE_POOL[index % len(_PROSE_POOL)]
        # A number wearing one shared piece of text. Whole cores, so
        # the role's own `integer_valued` is exercised, and a spread
        # wide enough for a ladder with distinct rungs.
        # THE CORES REPEAT ON PURPOSE, and the two reasons are
        # different sides of the same fact. Two hundred and forty whole
        # numbers ALL DIFFERENT inside a range two hundred and forty
        # wide is the one permutation of that range, so no twin could
        # carry the published distinctness except by drawing it
        # exactly. Widening the range fixes that and leaves the second
        # reason standing: an all-different column publishes a distinct
        # count equal to its own present count, G12.8's envelope then
        # reaches from one value to every value the column can hold,
        # and the check is dropped as proving nothing. A column whose
        # cores repeat publishes a count the envelope can bracket, so
        # the affixed role's distinctness is CHECKED here rather than
        # listed as uncheckable.
        # ...AND THE CORES CARRY A POINT, so the census of fraction
        # widths is exercised on THIS role and not only on the plain
        # numeric columns. Whole cores left the affixed half of that
        # machinery unwitnessed: the code that strips the pair before
        # recounting a width could be deleted and every battery stayed
        # green, which is the state this shared table exists to prevent.
        # Two widths, both clearing the floor, so the census names two
        # keys rather than pooling one away.
        dose = f"{10 + (index * 37) % 180}.{index % 10}"
        if index % 3 == 0:
            dose = f"{10 + (index * 37) % 180}.{index % 10}0"
        dose = f"{dose} mg"
        # A COLUMN OF CLOCK TIMES, shaped against four things the
        # affixed column had to be reshaped three times to satisfy.
        # Its values come from `index` alone, so no draw of the shared
        # generator moves when this column is added. They REPEAT --
        # a hundred and twenty different times over two hundred and
        # forty rows -- because that is the shape whose distinctness
        # falls to the envelope of amendment A-P4-20, and a fixture
        # that only ever held all-different values would never walk it.
        # The all-different case is exact and is pinned in the role's
        # own test file, where the construction is held to carrying
        # every value. And two rows hold text no clock reading accepts, so
        # `n_unparsed` is exercised rather than sitting at zero: two is
        # the most a hundred-and-ninety-nine-hundredths parse line
        # leaves room for at this length.
        seen_at = f"{7 + (index % 120) // 60:02d}:{(index % 120) % 60:02d}"
        if index in (100, 200):
            seen_at = "not recorded"
        # A LONG TAIL OF LABELS: two sentences enough rows share to
        # clear the publication floor, and a one-off for every other
        # row. Free text is what this column was before plan P4-D5, and
        # the whole point of the role is that such a column is not the
        # same thing as a column of names -- so the battery needs one,
        # or its generator branch, its validator checks and its
        # dispositions are walked by nothing.
        # The one-offs come from the prose pool, whose sentences vary
        # at BOTH ends: a family sharing a first or last word would
        # wear an affix pair, and the affixed rule -- which is tested
        # before this one -- would read the column instead. The two
        # shared labels are single words, which is what keeps the
        # entry table's subcheck names readable.
        note_text = _PROSE_POOL[index % len(_PROSE_POOL)]
        if index % 20 == 0:
            note_text = "clinic"
        elif index % 21 == 0:
            note_text = "referral"
        rows.append(
            [
                record,
                region,
                visits,
                reading,
                amount,
                recorded,
                answer,
                comment,
                "",
                "one",
                dose,
                seen_at,
                note_text,
            ]
        )
    return rows_to_csv(header, rows)


# The column name the joined role needs declared, so no caller has to
# remember the pair. It is NOT `reading`: the shared table already has
# a column of that name, and two columns cannot share one.
JOINED_COLUMN = "pressure"


def every_role_and_joined_table(n_rows: int = 240) -> str:
    """`every_role_table` with a JOINED column beside it.

    THE SHARED TABLE CANNOT CARRY THIS ROLE ON ITS OWN. An undeclared
    column of two numbers in one cell is not `joined_numbers` (plan
    P4-D23), so every one of that table's call sites would have to pass
    `--measurement` and any that missed it would give the column
    another role in silence -- which is residual R-P4-62's own defect
    in a new place. So the joined column is added HERE, for the
    surfaces that claim to cover every role, and those surfaces declare
    `JOINED_COLUMN`.

    Without this, the no-regression run and the whole-product surfaces
    said "every role in the taxonomy" while excluding the one that
    carries a blood pressure (review item P4-A2-R3-F4).
    """
    lines = [line for line in every_role_table(n_rows=n_rows).split("\n") if line]
    joined = [
        line.split(",")[0]
        for line in joined_numbers_table(n_rows=n_rows).split("\n")[1:]
        if line
    ]
    rows = [f"{lines[0]},{JOINED_COLUMN}"]
    for index, line in enumerate(lines[1:]):
        rows.append(f"{line},{joined[index]}")
    return "\n".join(rows) + "\n"


def joined_column_text(n_rows: int = 240) -> "list[str]":
    """Just the joined column's cells, for a caller splicing its own table.

    `test_generation` builds its every-role text by appending a column
    of its own to the shared table, and a column inserted BEFORE that
    one shifts its draws: one stream feeds every column in order, so
    where a column sits decides what it is handed (review item
    P4-A2-R4-F1). A caller that already appends can append this too and
    keep its own column last.
    """
    return [
        line.split(",")[0]
        for line in joined_numbers_table(n_rows=n_rows).split("\n")[1:]
        if line
    ]


def joined_numbers_table(n_rows: int = 120) -> str:
    """A column of two numbers written in one cell, for the battery.

    THE ROLE NO COMPLETENESS SURFACE REACHED (residual R-P4-62). Three
    guards proved their own completeness against a table that does not
    contain this role, so each passed by never looking: the disposition
    registry disposed none of its eight facts, the approximation walk
    enumerated thirteen roles without it, and the entry table's red
    battery had no joined column, so no perturbation there could turn
    one of its checks red.

    IT IS A FIXTURE OF ITS OWN AND NOT A FOURTEENTH COLUMN of
    `every_role_table`, on the precedent `_unrepresentable_table` set
    in the entry table's own file. Two reasons, both measured. The role
    REQUIRES a `--measurement` declaration -- an undeclared `120/80`
    column is not this role, by design (plan P4-D23) -- so every one of
    the shared table's profiling sites would have to pass one, and any
    that missed it would give the column another role silently, which
    is the same blindness in a new place. And widening that table moves
    every golden and every fixture-derived count in the suite.

    THE SHAPE IS CHOSEN, not arbitrary, and each choice was measured:

    * **TWO positions, never three.** A three-position column cannot
      honour its (1,2) pair -- the pairing walk moves only the last
      position (residual R-P4-51) -- so it would build a known miss
      into a battery that requires none.
    * **All different.** A column whose cells repeat overshoots its
      published count of different cells badly: 80 published against
      210 held on one measured column, because each position is drawn
      to its own ladder and the pairing then makes more distinct pairs
      than a repeating source had.
    * **Bands that OVERLAP, on purpose.** An earlier version put the
      two numbers in bands that could not meet, so the upper was above
      the lower on every row and `part_above` equalled `n_joined`
      exactly. That makes the fact TAUTOLOGICAL: an implementation
      that returned the joined count without comparing the positions
      at all would pass the green run, and its registered red case
      would fire for an unrelated reason (review item P4-A2-R1-F5).
      The bands overlap now and the count is 102 of 120 -- a number
      only a real comparison produces, and one the twin still meets
      along with every other published fact.
    * **A SECOND COLUMN, and it is not decoration.** The battery's
      quality axis moves only when a whole column is emptied, and that
      perturbation is not built for a one-column description, where it
      would leave a file holding no table at all. Without a second
      column the joined column's `axes.quality_state` would be a site
      no edit could turn red -- and this battery excuses nothing, on
      the ground that an exemption argued rather than constructed is
      how its last hole was made. The companion is a constant, which
      is the cheapest column that carries one.
    """
    rows = []
    for index in range(n_rows):
        upper = 100 + (index % 120)         # 100 to 219
        lower = 60 + (index * 13) % 100     # 60 to 159, an overlapping band
        rows.append([f"{upper}/{lower}", "one"])
    return rows_to_csv(["reading", "clinic"], rows)


def every_withholding_table(seed: int = 20260814, n_rows: int = 240) -> str:
    """A table that makes the floor hold something back in every way.

    THIS IS THE FIXTURE A DERIVATION STANDS ON. Described twice -- once
    at the default floor and once at a floor of one -- the two documents
    differ at exactly the positions the small-cell floor governs, and
    `tests/test_p3v5f1_floor_one.py` reads that difference off rather
    than trusting a list of field names somebody wrote down. A field the
    floor governs that this table does not exercise is a field that
    derivation cannot see, so every way the format has of holding
    something back is given a column here:

    * `region` -- one label that about seven rows share, so the floor
      suppresses a LEVEL and fills `suppressed_levels`,
      `suppressed_rows` and `suppressed_level_counts`;
    * `visits` -- blank cells plus three rare spellings of "no value",
      so `missing_by_source` pools a REMAINDER and `missing_by_class`
      pools the class those spellings fell into;
    * `reading` -- a common stand-in number and a rare one, so
      `n_sentinel_candidates_unpublished` counts a candidate too rare to
      name;
    * `amount` -- mostly plain decimals with one exponent and one signed
      value, so `numeric_styles` pools a FORM;
    * `stamped_at` -- times stamped in UTC with two rare offsets, so
      `utc_offsets` pools an OFFSET;
    * `answer` -- a two-value column where one row shouts its label, so
      one level's `variants_withheld` holds a SPELLING back;
    * `comment`, `unused`, `batch`, `record_code` -- free text, an empty
      column, a constant and an all-distinct column, so the roles that
      publish nothing are in the walk too.

    Every value is made up here with a fixed seed, exactly as the other
    builders in this file are (plan D13).
    """
    rng = random.Random(seed)
    header = [
        "record_code",
        "region",
        "visits",
        "reading",
        "amount",
        "stamped_at",
        "answer",
        "comment",
        "unused",
        "batch",
    ]
    rows = []
    for index in range(n_rows):
        if index % 23 == 0:
            visits = ""
        elif index == 5:
            visits = "n/a"
        elif index == 9:
            visits = "N/A"
        elif index == 11:
            visits = "unknown"
        else:
            visits = str(rng.randint(0, 9))
        if index % 19 == 0:
            reading = "-999"
        elif index in (3, 7):
            reading = "9999"
        else:
            reading = str(rng.randint(1, 400))
        if index == 13:
            amount = "1.5e3"
        elif index == 17:
            amount = "+12.25"
        else:
            amount = f"{rng.uniform(0.5, 99.5):.2f}"
        if index == 21:
            offset = "+02:00"
        elif index == 29:
            offset = "-05:00"
        else:
            offset = "Z"
        answer = "yes" if rng.random() < 0.3 else "no"
        if answer == "yes" and index % 31 == 0:
            answer = "YES"
        rows.append(
            [
                f"R{index:05d}",
                "outlying" if index % 37 == 0 else REGIONS[index % 4],
                visits,
                reading,
                amount,
                (
                    f"2024-{(index % 12) + 1:02d}-{(index % 28) + 1:02d}"
                    f"T{index % 10:02d}:15:00{offset}"
                ),
                answer,
                (
                    ""
                    if index % 3
                    else _PROSE_POOL[index % len(_PROSE_POOL)]
                ),
                "",
                "one",
            ]
        )
    return rows_to_csv(header, rows)


# Text NO RULE READS, for the many tests that need a column which
# publishes nothing.
#
# It is here rather than written out at each site because the shape
# that stands for "free text" moved once and would otherwise have to
# move in a dozen files again. Every such fixture used to be a
# template with a counter in it -- `note 0`, `note 1`, `code7` -- and
# the affixed-number rule reads exactly that: a number wearing one
# shared piece of text, which is what those strings are. A template
# cannot stand for prose any more.
#
# What this returns instead varies at both ends and holds no digit, so
# no rule claims it: not the numeric rules, which find no number; not
# the date rules; not the affixed rule, which finds no core; and not
# the categorical rule, given enough of them to clear the ceiling.
# Every part is ONE word, so a sentence is always five words long
# while its LENGTH varies. That split matters to the red-case battery:
# a perturbation that writes a one-word cell has to move the word
# average decisively, which it cannot do if the average is already
# ragged, and a perturbation that lengthens every cell has to move the
# length statistics without touching the word count.
_PROSE_PARTS = (
    ("seen", "review", "pending", "noted", "checked"),
    ("clinic", "telephone", "home", "ward", "consultation"),
    ("with", "without", "after", "before", "despite"),
    ("nurse", "doctor", "family", "physiotherapist", "team"),
    ("unchanged", "improving", "worse", "unclear", "resolved"),
)


def prose(count: int) -> list[str]:
    """``count`` sentences that no reading rule claims.

    Every sentence is distinct up to 3,125 of them, which is past the
    categorical ceiling of any table these tests build. The parts vary
    at BOTH ends on purpose: a family sharing a first or last word
    would wear an affix pair, and the affixed-number rule would read
    it -- which is exactly the trap the templates these replaced fell
    into.
    """
    built: list[str] = []
    for index in range(count):
        place = index
        words: list[str] = []
        for part in _PROSE_PARTS:
            words = words + [part[place % len(part)]]
            place = place // len(part)
        built = built + [" ".join(words)]
    return built


# Short sentences that are still text no rule reads. The red-case
# battery needs a perturbation that writes cells SHORTER than any the
# column held, without collapsing the column onto so few distinct
# values that the categorical rule claims it -- five two-word cells in
# eighty rows is a set of categories, not free text, and the free-text
# checks would stop running.
_SHORT_PARTS = (
    ("ok", "up", "in", "on", "at"),
    ("now", "soon", "late", "next", "past"),
    ("here", "there", "home", "ward", "desk"),
)


def short_prose(count: int) -> list[str]:
    """``count`` short sentences that no reading rule claims.

    Distinct up to 125, and every one is shorter than any `prose`
    sentence, which is what makes it usable as the short end of a
    length perturbation.
    """
    built: list[str] = []
    for index in range(count):
        place = index
        words: list[str] = []
        for part in _SHORT_PARTS:
            words = words + [part[place % len(part)]]
            place = place // len(part)
        built = built + [" ".join(words)]
    return built


# Built once, after `prose` is defined, and read by the two tables
# above at call time. Rebuilding it per row was measurably wasteful and
# said nothing extra.
_PROSE_POOL = prose(200)


def single_column_table(name: str, values: list[str]) -> str:
    """A one-column table holding exactly ``values``."""
    return rows_to_csv([name], [[value] for value in values])


def numbers(seed: int, count: int, low: int, high: int) -> list[str]:
    """``count`` whole numbers written as text, drawn with ``seed``."""
    rng = random.Random(seed)
    return [str(rng.randint(low, high)) for _index in range(count)]


def labels(seed: int, count: int, pool: tuple[str, ...] = LABELS) -> list[str]:
    """``count`` labels drawn from ``pool`` with ``seed``."""
    rng = random.Random(seed)
    return [pool[rng.randrange(len(pool))] for _index in range(count)]
