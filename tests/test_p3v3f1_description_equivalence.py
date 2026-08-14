"""Two files one description cannot tell apart get one report.

REVIEW ITEMS P3-V3-F1 AND P3-V3-F2, and plan amendment A-P3-5. V5.1
says the quality report may state about the measured file only what
`synthtwin profile`, run on THAT FILE under the profile's own settings,
would publish about it, and V5.3 says that covers the VERDICT and not
only the value. The whole of that rule, tested directly, is: **two files
whose own descriptions are the same bytes must get the same report.**

WHY THE SHIPPED VALIDATOR BROKE IT. V2.4 counts presence by BLANKNESS so
that a file cannot buy silence with marker cells, and amendment V2.4-A1
made every presence-dependent obligation take its number from a second
description built that way. But the producer counts presence by its own
absence rules, and the two differ exactly on the cells that are non-blank
and read as holes -- and HOW MANY such cells a column has is a floored
fact, named per spelling in `missing_by_source` at or above
`small_cell_floor` and pooled into one unnamed total below it. So
fifty-nine labels and one empty cell, beside fifty-nine labels and one
`n/a`, are two files the producer describes byte for byte alike, and the
shipped validator gave them 48 HELD, 0 MISSED at exit 0 and 40 HELD, 8
MISSED at exit 3.

WHAT IS ASSERTED HERE, AND WHY IT IS A PROPERTY. A repair that satisfied
the one witness would leave the class open -- and the class was wider
than the witness: the style clauses settle their recounts against room
that `_unread_cells` widens by exactly the disputed cells, so the same
pair of files moved SEVEN style subchecks as well, which no test naming
the presence counts would have caught. So the battery crosses every
marker class the producer knows, every column of a multi-role table, and
counts from one cell up to one below the floor, asserts of each pair that
the two files really are described identically, and then asserts the
reports are equal field for field.

AND THE OTHER DIRECTION IS ASSERTED BESIDE IT, because a validator that
answered this conflict by going quiet would have traded a confidentiality
defect for the vacuity V3.4 refuses. Two things are pinned: where the
description NAMES its missing sources the blank split still bites, so a
file whose every cell spells a marker still misses; and the repair
introduces no withholding at all, so the one-cell silence lever amendment
V2.4-A1 closed stays closed.

Every table is built at test time by the seeded neutral builders in
`fixtures.py`; no data-format file enters the repository (plan D13).
"""

import dataclasses
import json
import pathlib

import pytest

import fixtures
from synthtwin import (
    contract,
    parsing,
    profile,
    quality,
    reading,
    taxonomy,
    validation,
)

# The two shapes of cell whose presence the producer and the blank split
# read differently, taken from the product's own constants so that a new
# marker cannot be added without this battery seeing it.
MARKER_TEXTS = tuple(
    spelling for spelling in parsing.MISSING_TEXTS if spelling
)
SENTINEL_TEXTS = tuple(f"{value:g}" for value in parsing.NUMERIC_SENTINELS)


def _table(rows: "list[list[str]]", names: "list[str]") -> str:
    """One CSV, written the way the twin writer writes one."""
    lines = [",".join(names)]
    for row in rows:
        lines = lines + [",".join(row)]
    return "\n".join(lines) + "\n"


def _describe(
    folder: pathlib.Path, text: str, stem: str
) -> contract.Profile:
    """Profile one table through the real producer and the strict loader."""
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(table_path), first_row=reading.FIRST_ROW_AUTOMATIC
    )
    document = profile.build_document(table, taxonomy.Settings(), [])
    written = fixtures.write_profile(folder, f"{stem}-profile.json", document)
    return contract.load_profile(str(written))


def _own_description(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
    stem: str,
) -> str:
    """What `synthtwin profile` publishes about THIS file, as bytes.

    Built with the validator's own reconstructed settings, which is what
    V5.1 names: the file's own description, under the profile's settings.
    """
    table_path = fixtures.write(folder, f"{stem}.csv", text)
    table = reading.read_table(
        str(table_path),
        first_row=(
            reading.FIRST_ROW_NAMES
            if described.source.header_source == reading.HEADER_FROM_FILE
            else reading.FIRST_ROW_DATA
        ),
    )
    document = profile.build_document(
        table, validation.settings_for(described), []
    )
    return json.dumps(document, sort_keys=True, default=str)


def _report(
    folder: pathlib.Path,
    described: contract.Profile,
    text: str,
    name: str,
) -> "tuple[tuple[object, ...], validation.Census]":
    """Every verdict of one run, in a form two runs can be compared by.

    The measured file's NAME is deliberately the same on both sides: it
    is an input to the report's bytes (V10) and this asserts about
    everything else.
    """
    target = fixtures.write(folder, name, text)
    outcome = validation.measure(described, str(target))
    return (
        tuple(
            (
                check.column,
                check.fact,
                check.subcheck,
                check.verdict,
                check.published,
                check.achieved,
                check.citation,
            )
            for check in outcome.checks
        ),
        outcome.census,
    )


# -- the battery of pairs one description cannot tell apart -----------


def _pairs() -> "list[tuple[str, str, int]]":
    """Every (marker spelling, column, count) this battery crosses."""
    built: list[tuple[str, str, int]] = []
    for spelling in MARKER_TEXTS + SENTINEL_TEXTS:
        for column in ("label", "number"):
            for count in (1, 2, 10):
                built = built + [(spelling, column, count)]
    return built


def _two_files(
    spelling: str, column: str, count: int
) -> "tuple[str, str, list[str]]":
    """The same table with `count` holes written empty, and written `spelling`.

    Two columns, so that a hole is an empty FIELD rather than an empty
    line -- which a one-column table cannot express and the reader
    refuses by name.
    """
    names = ["label", "number"]
    blank_rows: list[list[str]] = []
    marked_rows: list[list[str]] = []
    for index in range(60):
        label = "north" if index % 2 else "south"
        number = f"{100 + index}.5"
        hole = index < count
        blank_rows = blank_rows + [
            [
                "" if hole and column == "label" else label,
                "" if hole and column == "number" else number,
            ]
        ]
        marked_rows = marked_rows + [
            [
                spelling if hole and column == "label" else label,
                spelling if hole and column == "number" else number,
            ]
        ]
    return _table(blank_rows, names), _table(marked_rows, names), names


@pytest.mark.parametrize(
    ("spelling", "column", "count"),
    _pairs(),
    ids=lambda value: str(value).replace("/", "-"),
)
def test_identically_described_files_get_identical_reports(
    tmp_path: pathlib.Path, spelling: str, column: str, count: int
) -> None:
    """V5.1 and V5.3, as the one property they amount to.

    The precondition is asserted rather than assumed: where the two
    files are NOT described alike the pair proves nothing and the case
    says so, and the count of pairs that DO describe alike is asserted
    by the census test below, so the battery cannot quietly empty.
    """
    folder = tmp_path / "pair"
    folder.mkdir()
    blank_text, marked_text, _names = _two_files(spelling, column, count)
    described = _describe(folder, blank_text, "submitted")
    own_blank = _own_description(folder, described, blank_text, "own-blank")
    own_marked = _own_description(folder, described, marked_text, "own-marked")
    if own_blank != own_marked:
        pytest.skip(
            "these two files are not described alike, so V5 says nothing "
            "about them"
        )
    blank_checks, blank_census = _report(
        folder, described, blank_text, "measured.csv"
    )
    marked_checks, marked_census = _report(
        folder, described, marked_text, "measured.csv"
    )
    assert blank_census == marked_census, (
        "two files `synthtwin profile` describes byte for byte alike got "
        "different censuses, so the report states about the measured file "
        "something describing that file would not publish (V5.1)"
    )
    assert blank_checks == marked_checks, (
        "two files `synthtwin profile` describes byte for byte alike got "
        "different verdicts (V5.3)"
    )


def test_identically_described_files_get_identical_report_bytes(
    tmp_path: pathlib.Path,
) -> None:
    """The same property on the surface V5 actually governs.

    The census and the verdict list are what the tests above compare,
    and they are what a repair would naturally be aimed at. What
    TRAVELS is the quality report, which V7.5 says is real-derived
    material exactly as the profile is -- and V5.1's guarantee is
    precisely that it is no more disclosive than the profile of the same
    file. So the rendered bytes are compared here as well, so that a
    leak in the rendering layer rather than in the measurement cannot
    pass. The measured NAME is held equal on both sides because V10
    makes it an input to those bytes on purpose.
    """
    folder = tmp_path / "bytes"
    folder.mkdir()
    blank_text, marked_text, _names = _two_files("n/a", "label", 1)
    described = _describe(folder, blank_text, "submitted")
    own_blank = _own_description(folder, described, blank_text, "own-blank")
    own_marked = _own_description(folder, described, marked_text, "own-marked")
    assert own_blank == own_marked
    rendered: list[str] = []
    for index, text in enumerate((blank_text, marked_text)):
        target = fixtures.write(folder, f"same-name-{index}.csv", text)
        outcome = validation.measure(described, str(target))
        outcome = dataclasses.replace(outcome, measured_name="measured.csv")
        rendered = rendered + [quality.quality_report(described, outcome)]
    assert rendered[0] == rendered[1], (
        "the report that travels states something about the measured file "
        "that describing that file would not publish (V5.1, V7.5)"
    )


def test_the_equivalence_battery_is_not_empty(tmp_path: pathlib.Path) -> None:
    """The battery above proves nothing if every pair skips.

    So the number of pairs that really are described alike is counted
    here, and both kinds of disputed cell must be represented: a
    built-in marker TEXT and a numeric stand-in for "no value". A future
    change to the producer that made every pair distinguishable would
    turn the parametrized test green by emptying it, and this is what
    stops that.
    """
    folder = tmp_path / "count"
    folder.mkdir()
    alike: dict[str, int] = {}
    for index, (spelling, column, count) in enumerate(_pairs()):
        blank_text, marked_text, _names = _two_files(spelling, column, count)
        described = _describe(folder, blank_text, f"s{index}")
        own_blank = _own_description(
            folder, described, blank_text, f"b{index}"
        )
        own_marked = _own_description(
            folder, described, marked_text, f"m{index}"
        )
        if own_blank == own_marked:
            alike[spelling] = alike.get(spelling, 0) + 1
    texts = [name for name in alike if name in MARKER_TEXTS]
    assert len(texts) >= 5, alike
    assert sum(alike.values()) >= 20, alike


def test_the_repair_introduces_no_withholding(
    tmp_path: pathlib.Path,
) -> None:
    """Amendment A-P3-5 clause 1: the answer is a verdict, never a silence.

    A silence here is one any file could buy by writing a single marker
    cell, which is verbatim the defect amendment V2.4-A1 exists to
    close. So the repair is asserted to move NOTHING to WITHHELD: on
    both sides of the witness pair every obligation still lands on a
    verdict taken from one description or the other.
    """
    folder = tmp_path / "quiet"
    folder.mkdir()
    blank_text, marked_text, _names = _two_files("n/a", "label", 1)
    described = _describe(folder, blank_text, "submitted")
    for name, text in (("blank", blank_text), ("marked", marked_text)):
        checks, census = _report(folder, described, text, f"{name}.csv")
        assert census.withheld == 0, name
        for check in checks:
            assert check[3] != validation.WITHHELD, check


def test_the_blank_split_still_bites_where_the_sources_are_named(
    tmp_path: pathlib.Path,
) -> None:
    """The other direction, and the reason this is not a blanket retreat.

    Amendment A-P3-5 takes the blank split's number wherever the file's
    own description NAMES the source of every missing cell -- which is
    every column with no missing cells at all, and every twin whose
    blanks reach the publication floor. Here thirty cells spell one
    marker, which clears the floor of eleven, so `missing_by_source`
    names that spelling and its count exactly: the split is derivable
    from what describing the file publishes, and V2.4's measurement
    stands. This is round 2's own witness, and it must still miss.
    """
    folder = tmp_path / "named"
    folder.mkdir()
    names = ["label", "number"]
    rows: list[list[str]] = []
    for index in range(60):
        rows = rows + [
            ["n/a" if index < 30 else "north", f"{100 + index}.5"]
        ]
    text = _table(rows, names)
    described = _describe(folder, text, "submitted")
    assert described.columns[0].n_present == 30
    checks, census = _report(folder, described, text, "again.csv")
    # Keyed by (column, subcheck): every column carries `presence.n_present`,
    # so a dict on the subcheck alone answers for whichever column came last.
    named = {(check[0], check[2]): check[3] for check in checks}
    assert named[("label", "presence.n_present")] == validation.MISSED, named
    assert named[("label", "distinct.n_distinct")] == validation.MISSED, named
    assert census.missed > 0
    # ...and the reason it bites is the published source map, not luck.
    own = _own_description(folder, described, text, "own")
    assert '"n/a": 30' in own


def test_a_column_publishing_no_spellings_keeps_its_presence_teeth(
    tmp_path: pathlib.Path,
) -> None:
    """A-P3-5 clause 1: the two counts ask the WEAKER question.

    Three roles publish no value of the table anywhere in their block --
    free text, declared identifier, unrepresentable -- so their
    `missing_by_source` is empty by policy and the SPELLINGS of their
    holes are never derivable from their description. But
    `missing_by_class` uses only synthtwin's own five words, so it is
    published for every role, and where its pooled remainder is empty it
    says exactly how many holes are non-blank.

    So the two counts the blank split owns still verdict here, and the
    round-2 witness is still caught on such a column: thirty holes all
    spelled one way clear the floor, the class map names them, and
    `presence.n_present` misses. Distinctness, which would need the
    spellings, falls back to the description. A gate that asked both the
    same way would have thrown the first half away, and this is what
    would go red.
    """
    folder = tmp_path / "textual"
    folder.mkdir()
    names = ["note", "tag"]
    rows = [
        [
            "n/a" if index < 30 else f"a sentence of some length number {index}",
            f"t{index % 7}",
        ]
        for index in range(60)
    ]
    text = _table(rows, names)
    described = _describe(folder, text, "submitted")
    own = json.loads(_own_description(folder, described, text, "own"))
    block = own["columns"][0]
    assert block["role"] in taxonomy.ROLES_PUBLISHING_NOTHING
    assert block["missing_by_source"] == {}
    checks, _census = _report(folder, described, text, "again.csv")
    named = {(check[0], check[2]): check[3] for check in checks}
    assert named[("note", "presence.n_present")] == validation.MISSED, named
    assert named[("note", "presence.n_missing")] == validation.MISSED, named


def test_the_named_source_threshold_is_the_publication_floor(
    tmp_path: pathlib.Path,
) -> None:
    """Where the line falls, asserted rather than assumed.

    One below the floor the description pools the source and the split
    may not be reported; at the floor it names it and the split governs.
    Nothing else about the two files differs.
    """
    folder = tmp_path / "edge"
    folder.mkdir()
    floor = taxonomy.Settings().small_cell_floor
    seen: dict[int, bool] = {}
    for count in (floor - 1, floor):
        names = ["label", "number"]
        rows = [
            [
                "n/a" if index < count else "north",
                f"{100 + index}.5",
            ]
            for index in range(60)
        ]
        text = _table(rows, names)
        described = _describe(folder, text, f"submitted{count}")
        blank = _table(
            [
                ["" if index < count else "north", f"{100 + index}.5"]
                for index in range(60)
            ],
            names,
        )
        marked_checks, _marked = _report(
            folder, described, text, f"marked{count}.csv"
        )
        blank_checks, _blank = _report(
            folder, described, blank, f"blank{count}.csv"
        )
        seen[count] = marked_checks == blank_checks
    assert seen[floor - 1] is True, (
        "below the floor the two files are described alike and must get "
        "one report"
    )
    assert seen[floor] is False, (
        "at the floor the description names the spelling and its count, so "
        "the two files are told apart by their own descriptions and the "
        "report may tell them apart too -- a repair that made these agree "
        "would have thrown V2.4's measurement away"
    )


# -- P3-V3-F2: the ruling on canonical spelling ------------------------


def test_canonical_spelling_stays_checkable_on_every_file(
    tmp_path: pathlib.Path,
) -> None:
    """Amendment A-P3-5 clause 3, and the test that settles the ruling.

    The ruling is that whether a numeric cell's TEXT is a spelling its
    own value licenses is a fact about the file's own form rather than
    about the table it holds, on the ground that the producer publishes
    it about NO file at ANY count. That ground is asserted here directly:
    two files differing only in a trailing zero on every decimal cell are
    described byte for byte alike, so no floor and no window could ever
    settle the clause, and withholding it would withhold it forever --
    the vacuity V3.4 refuses by name.

    So the subcheck keeps its verdict, and this pins that it can still
    MISS. If the owner reverses the ruling, this test is the one that
    goes red, and A-P3-5 clause 4 says what to put in its place.
    """
    folder = tmp_path / "spelling"
    folder.mkdir()
    names = ["amount", "tag"]
    canonical = [[f"{index}.5", f"t{index % 7}"] for index in range(60)]
    padded = [[f"{index}.50", f"t{index % 7}"] for index in range(60)]
    text_a, text_b = _table(canonical, names), _table(padded, names)
    described = _describe(folder, text_a, "submitted")
    own_a = _own_description(folder, described, text_a, "own-a")
    own_b = _own_description(folder, described, text_b, "own-b")
    assert own_a == own_b, (
        "the premise of the ruling: the producer publishes nothing that "
        "separates a canonical spelling from a padded one"
    )
    checks_a, _census_a = _report(folder, described, text_a, "a.csv")
    checks_b, _census_b = _report(folder, described, text_b, "b.csv")
    verdicts_a = {check[2]: check[3] for check in checks_a}
    verdicts_b = {check[2]: check[3] for check in checks_b}
    assert verdicts_a["styles.spelled"] == validation.HELD
    assert verdicts_b["styles.spelled"] == validation.MISSED


def test_the_spelling_subcheck_takes_no_number_from_the_description(
    tmp_path: pathlib.Path,
) -> None:
    """A property this subcheck has, kept though it is no longer owed.

    A-P3-5 clause 3 rules canonicality outside V5.1's envelope, and it
    stated two bounds for the pair: that neither prints a measured
    count, and that no sequence of candidate descriptions can
    binary-search anything through them. The SECOND is no longer owed by
    any ruling -- V5-A1 puts the person who writes the descriptions out
    of scope (owner ruling 2026-08-14, plan amendment A-P3-13) -- but it
    is TRUE of `styles.spelled`, whose only profile input is the boolean
    `integer_valued`, and a true property that costs nothing to keep is
    kept: it is asserted here so that a later edit which starts feeding
    this subcheck a published count is seen for what it is. The bound
    that is still owed -- no measured count printed -- is asserted with
    the ceiling in `tests/test_p3v4f2_canonical_ceiling.py`.
    """
    folder = tmp_path / "unsearchable"
    folder.mkdir()
    names = ["amount", "tag"]
    padded = _table(
        [[f"{index}.50", f"t{index % 7}"] for index in range(60)], names
    )
    answers: list[str] = []
    for spread in (0, 7, 19):
        rows = [
            [
                f"0{index}.5" if index < spread else f"{index}.5",
                f"t{index % 7}",
            ]
            for index in range(60)
        ]
        described = _describe(folder, _table(rows, names), f"cand{spread}")
        checks, _census = _report(
            folder, described, padded, f"probe{spread}.csv"
        )
        for check in checks:
            if check[2] == "styles.spelled":
                answers = answers + [check[3]]
    assert answers, "the subcheck did not run"
    assert len(set(answers)) == 1, (
        "descriptions publishing different style counts read different "
        "answers off `styles.spelled`, so it has started taking a number "
        "from the submitted description, which its docstring denies"
    )


def test_the_form_counts_stay_gated_under_the_ruling(
    tmp_path: pathlib.Path,
) -> None:
    """A-P3-5 clause 3's last paragraph: the ruling reaches spelling only.

    WHICH of the six forms a cell wears IS published and IS floored, and
    amendment A-P3-3 clause 1's window is what keeps a verdict from
    telling two pooled files apart. Nothing in the spelling ruling
    relaxes it, and this asserts the window is still doing its work: two
    files differing only in whether one pooled cell is written `1e5` or
    `1E5` get one report.
    """
    folder = tmp_path / "forms"
    folder.mkdir()
    names = ["amount", "tag"]
    body = [[f"{index}.5", f"t{index % 7}"] for index in range(59)]
    lower = _table(body + [["1e5", "t0"]], names)
    upper = _table(body + [["1E5", "t0"]], names)
    described = _describe(folder, lower, "submitted")
    own_lower = _own_description(folder, described, lower, "own-lower")
    own_upper = _own_description(folder, described, upper, "own-upper")
    if own_lower != own_upper:
        pytest.skip("these two files are not described alike")
    checks_lower, census_lower = _report(folder, described, lower, "l.csv")
    checks_upper, census_upper = _report(folder, described, upper, "u.csv")
    assert census_lower == census_upper
    assert checks_lower == checks_upper
