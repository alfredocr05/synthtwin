"""Landing 2b.18: a record number keeps its LAYOUT.

Four audit items were SILENT here -- LTM-5, LTM-6, NC-9 and NC-9's
MISSED item M1 -- and silent in the worst way: a declared identifier
published its two length ends and its two alphabet counts, both files
passed their own description at exit 0, and the twin matched none of
its own rows. A column of UUIDs came back
`A----------------------------------J`; a braced GUID came back as
thirty-four interior spaces with no braces; `02254257` came back as
`10000020`, counting upward.

Every shape here is a ROUND TRIP, which is the gate this landing is
held to: the table is described, a twin is built, the twin is
DESCRIBED AGAIN under the same declaration, the layout facts are
asserted to come back, and BOTH the twin and the real table are
validated at exit 0. Beside that, each shape carries a
PATTERN-MATCHING CHECK written against the twin -- a regular
expression, a length test and a case test -- and run UNCHANGED on the
real table, asserting the same match count on both. That is the whole
point of the landing: code developed on the twin runs on the table.

Two limits were pinned here as limits rather than left to be
rediscovered, each with its measured numbers: the LITERAL RUN, which
invariants I3 and F3 forbade this version to publish until the owner's
ruling of 2026-09-17 (item 1, plan P4-D202) published a shared prefix --
the test that pinned it now pins the ruling -- and the SMALL-SUPPLY rule,
which refuses a layout that would name the values it describes.

Every table is built by seeded neutral code at runtime (plan D13).
"""

import csv
import io
import pathlib
import random
import re

import pytest

from synthtwin import parsing
from tests import fixtures

ROWS = 800

# THREE SOURCE SEEDS, so a shape that passes is a shape and not a draw.
SOURCE_SEEDS = (1, 2, 3)


def _round_trip(
    folder: pathlib.Path,
    cells: "list[str]",
    seed: str = "4",
    floor: "int | None" = None,
    declared: bool = True,
) -> dict:
    """Describe, build, describe AGAIN, validate the twin AND the table.

    A SECOND COLUMN STANDS BESIDE THE ONE UNDER TEST for the reason
    landing 2b.8 named (plan P4-D74): a one-column table holding an
    empty cell is refused, because nothing in a CSV tells a blank line
    apart from a record whose one value is missing.
    """
    import json

    from tests.test_stage2_round_trip import _exit_of

    folder.mkdir(parents=True, exist_ok=True)
    rows = [[cells[index], f"row{index % 7}"] for index in range(len(cells))]
    table = folder / "real.csv"
    table.write_text(
        fixtures.rows_to_csv(["value", "other"], rows),
        encoding="utf-8",
        newline="",
    )
    described = ["profile", str(table), "--out-dir", str(folder), "--replace"]
    if declared:
        described += ["--identifier", "value"]
    if floor is not None:
        described += ["--smallest-group", str(floor)]
    assert _exit_of(described) == 0
    profile = folder / "real-profile.json"
    assert _exit_of(
        ["generate", str(profile), "--out-dir", str(folder), "--seed", seed,
         "--replace"]
    ) == 0
    twin = folder / "real-twin.csv"

    again = folder / "again"
    again.mkdir()
    copied = again / "twin.csv"
    copied.write_bytes(twin.read_bytes())
    redo = ["profile", str(copied), "--out-dir", str(again), "--replace"]
    if declared:
        redo += ["--identifier", "value"]
    if floor is not None:
        redo += ["--smallest-group", str(floor)]
    assert _exit_of(redo) == 0

    written = list(csv.reader(io.StringIO(twin.read_text(encoding="utf-8"))))
    spot = written[0].index("value")
    twin_cells = [row[spot] for row in written[1:]]

    checked = folder / "check-twin"
    checked.mkdir()
    twin_exit = _exit_of(
        ["validate", str(profile), "--twin", str(twin), "--out-dir",
         str(checked), "--replace"]
    )
    real_checked = folder / "check-real"
    real_checked.mkdir()
    real_exit = _exit_of(
        ["validate", str(profile), "--twin", str(table), "--out-dir",
         str(real_checked), "--replace"]
    )
    return {
        "source": json.loads(profile.read_text(encoding="utf-8"))["columns"][0],
        "twin_profile": json.loads(
            (again / "twin-profile.json").read_text(encoding="utf-8")
        )["columns"][0],
        "cells": twin_cells,
        "real_cells": cells,
        "twin_exit": twin_exit,
        "real_exit": real_exit,
    }


# ------------------------------------------------------------- the shapes


def uuid_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """A UUID column as a warehouse exports one: lower hex, 8-4-4-4-12."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        figures = "".join(draw.choice("0123456789abcdef") for _c in range(32))
        built += [
            f"{figures[:8]}-{figures[8:12]}-{figures[12:16]}"
            f"-{figures[16:20]}-{figures[20:]}"
        ]
    return built


def guid_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """A braced GUID: upper hex inside braces, as many exports write one."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        figures = "".join(draw.choice("0123456789ABCDEF") for _c in range(32))
        built += [
            "{"
            f"{figures[:8]}-{figures[8:12]}-{figures[12:16]}"
            f"-{figures[16:20]}-{figures[20:]}"
            "}"
        ]
    return built


def site_code_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """A site-subject code: three capitals, a hyphen, four figures."""
    draw = random.Random(seed)
    sites = ("BOS", "NYC", "SFO", "CHI", "HOU", "SEA")
    built = []
    for _row in range(rows):
        built += [f"{draw.choice(sites)}-{draw.randrange(1000, 9999)}"]
    return built


def padded_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """NC-9's own shape: a zero-filled width, so every cell leads with 0."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        built += [f"{draw.randrange(0, 9999999):08d}"]
    return built


def lower_hex_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """A bare lower-case hexadecimal token: no mark at all, 12 wide."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        built += ["".join(draw.choice("0123456789abcdef") for _c in range(12))]
    return built


def mixed_length_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """M1's own shape: two systems, a three-letter run and a one-letter one."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        if draw.random() < 0.71:
            built += [f"REC{draw.randrange(1000000, 9999999)}"]
        else:
            built += [f"E{draw.randrange(100000, 999999)}"]
    return built


def wide_mixed_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """Zero-padded eight wide beside bare four: the same number, two ways."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        if draw.random() < 0.6:
            built += [f"{draw.randrange(1, 9999999):08d}"]
        else:
            built += [str(draw.randrange(1000, 9999))]
    return built


def tiny_mixed_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """`007` beside `7`: the same number, two ways, at a tiny width."""
    draw = random.Random(seed)
    built = []
    for _row in range(rows):
        if draw.random() < 0.55:
            built += [f"{draw.randrange(0, 999):03d}"]
        else:
            built += [str(draw.randrange(0, 9))]
    return built


# Each shape, with the PATTERN a person writes after reading the twin:
# a regular expression, and beside it the length and case tests the same
# person writes. Every one of the three is run UNCHANGED on the real
# table and must find the same number of cells.
SHAPES = {
    "uuid": (
        uuid_cells,
        r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}",
        36,
        "lower",
    ),
    "guid": (
        guid_cells,
        r"\{[0-9A-F]{8}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{4}-[0-9A-F]{12}\}",
        38,
        "upper",
    ),
    "site_code": (site_code_cells, r"[A-Z]{3}-[0-9]{4}", 8, "upper"),
    "padded": (padded_cells, r"0[0-9]{7}", 8, "either"),
    "lower_hex": (lower_hex_cells, r"[0-9a-f]{12}", 12, "lower"),
    # The mixed-length column's pattern is the one the PUBLISHED facts
    # support: three capitals and seven figures, or one capital and six.
    # The LITERAL run is the owner's question, pinned separately below.
    "mixed_length": (
        mixed_length_cells, r"([A-Z]{3}[0-9]{7}|[A-Z][0-9]{6})", 10, "upper"
    ),
}


def _matching(cells: "list[str]", pattern: str) -> int:
    rule = re.compile(pattern)
    return len([cell for cell in cells if rule.fullmatch(cell)])


def _at_length(cells: "list[str]", width: int) -> int:
    return len([cell for cell in cells if len(cell) == width])


def _in_case(cells: "list[str]", case: str) -> int:
    if case == "lower":
        return len([cell for cell in cells if cell.lower() == cell])
    if case == "upper":
        return len([cell for cell in cells if cell.upper() == cell])
    return len(cells)


def _census_of(cells: "list[str]") -> "dict[str, int]":
    """The layout census, recounted off a column of cells."""
    convention = parsing.layout_convention(list(cells))
    counted: dict[str, int] = {}
    for cell in cells:
        layout = parsing.layout_form(cell, convention)
        if not layout:
            continue
        counted[layout] = counted.get(layout, 0) + 1
    return counted


@pytest.mark.parametrize("name", sorted(SHAPES))
@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_the_twin_wears_its_column_s_own_layout(
    name: str, source_seed: int, tmp_path: pathlib.Path
) -> None:
    """The round trip, and the same check run on both files.

    THE PATTERN IS WRITTEN AGAINST THE TWIN AND RUN ON THE TABLE. That
    is the obligation this landing exists for, and on the base every
    one of these shapes matched 800 real cells and 0 twin cells while
    both files passed their own description at exit 0.

    The twin holds as many distinct identifiers as the table, and on the
    shapes whose layout holds at least a hundred million spellings no
    twin cell is one of the table's own -- the walk fills a layout from a
    counter and reads no value, so a shared cell there would be a defect
    and not a coincidence.
    """
    make, pattern, width, case = SHAPES[name]
    cells = make(source_seed)
    got = _round_trip(tmp_path / f"{name}-{source_seed}", cells)

    # ...the layout facts come back when the twin is described again.
    published = got["source"]["layout_forms"]
    assert published, f"{name} publishes no layout at all"
    assert got["twin_profile"]["layout_forms"] == published, (
        f"{name}: the twin described again does not carry its own "
        f"published layouts. Published {published}, the twin's own "
        f"description says {got['twin_profile']['layout_forms']}."
    )

    # ...and BOTH files pass the description with nothing missed.
    assert got["twin_exit"] == 0, f"{name}: the twin misses its description"
    assert got["real_exit"] == 0, f"{name}: the table misses its description"

    # ...the three checks, written against the twin, run on the table.
    twin_cells = got["cells"]
    assert _matching(twin_cells, pattern) == len(twin_cells)
    assert _matching(cells, pattern) == _matching(twin_cells, pattern), (
        f"{name}: the regular expression matches "
        f"{_matching(cells, pattern)} real cells and "
        f"{_matching(twin_cells, pattern)} twin cells"
    )
    if width is not None:
        assert _at_length(cells, width) == _at_length(twin_cells, width)
    assert len(set(twin_cells)) == len(set(cells))
    if min(parsing.layout_room(layout) for layout in published) >= 10**8:
        assert not set(twin_cells) & set(cells), (
            f"{name}: the twin writes a cell of the table's own"
        )
    assert _in_case(cells, case) == _in_case(twin_cells, case), (
        f"{name}: the case test finds {_in_case(cells, case)} real cells "
        f"and {_in_case(twin_cells, case)} twin cells"
    )


@pytest.mark.parametrize("name", ("uuid", "padded"))
@pytest.mark.parametrize("generate_seed", ("4", "7"))
def test_a_second_generate_seed_keeps_the_layout(
    name: str, generate_seed: str, tmp_path: pathlib.Path
) -> None:
    """The layout is a fact of the description, not of one seed."""
    make, pattern, _width, _case = SHAPES[name]
    cells = make(1)
    got = _round_trip(
        tmp_path / f"{name}-{generate_seed}", cells, seed=generate_seed
    )
    assert got["twin_exit"] == 0
    assert got["real_exit"] == 0
    assert _matching(got["cells"], pattern) == len(got["cells"])


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_the_census_recounted_on_the_twin_is_the_published_census(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """The recount identity of contract 7.12, asserted on the cells.

    Read the layout off each twin cell and the published counts come
    back. This is the obligation the validator files; it is asserted
    here directly, on the cells, so a regression says what it broke
    rather than moving an exit code.
    """
    cells = uuid_cells(source_seed)
    got = _round_trip(tmp_path / f"recount-{source_seed}", cells)
    assert _census_of(got["cells"]) == got["source"]["layout_forms"]
    assert _census_of(cells) == got["source"]["layout_forms"]


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_a_zero_filled_width_comes_back_zero_filled(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """NC-9: the classic dtype defect, and the one mark that answers it.

    On the base the twin wrote `10000009`, `10000010`, … counting
    upward from ten million with 0 of 800 leading noughts against the
    table's 800. A reader who never meets a leading nought on the twin
    never writes the `zfill` the real table needs.
    """
    cells = padded_cells(source_seed)
    got = _round_trip(tmp_path / f"zero-{source_seed}", cells)
    leading = len([cell for cell in got["cells"] if cell[:1] == "0"])
    assert leading == len(cells), (
        f"the twin writes {leading} leading noughts of {len(cells)}"
    )
    # MOVED AT THE REPAIR PASS (plan P4-D126), and what moved is the
    # census, not the rule this test holds. This column was published
    # `{"!%%%%%%%": 800}`, which said a fill and not its width, and the
    # twin opened `00` on 77 cells of 800 where the table opened it on
    # 77, 75 and 86 at seeds 1-3 only by chance. Every nought of the fill
    # is marked now, so the census names each depth that reaches the line
    # -- one nought, two, and three -- and each depth comes back.
    published = got["source"]["layout_forms"]
    assert sum(published.values()) == len(cells)
    assert all(key[:1] == "!" for key in published), published
    # THE DEPTHS OWED ARE THE DEPTHS THE CENSUS NAMES (plan P4-D126), and
    # at the default floor of 11 (plan P4-D316) a depth fewer than eleven
    # cells wear -- three noughts, on 8 and 7 of 800 at these seeds -- is
    # counted one nought shallower, so the twin writes it shallower. So
    # the twin's cells are counted by exact fill depth and held to the
    # published count at each depth.
    owed: "dict[int, int]" = {}
    for key, count in published.items():
        depth = len(key) - len(key.lstrip("!"))
        owed[depth] = owed.get(depth, 0) + count
    wrote: "dict[int, int]" = {}
    for cell in got["cells"]:
        depth = len(cell) - len(cell.lstrip("0"))
        wrote[depth] = wrote.get(depth, 0) + 1
    assert wrote == owed, (wrote, owed)
    assert got["twin_exit"] == 0 and got["real_exit"] == 0


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_both_spellings_of_one_number_come_back_at_their_counts(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """The MISSED item of the numbers-and-codes audit, closed.

    A whole-number code column mixing a zero-padded spelling with a
    bare one invented codes the source never wrote: on the base the
    twin wrote 799 four-figure cells and one eight-figure cell against
    a table holding 480 zero-filled eight-figure cells and 320 bare
    four-figure ones. NO SPELLING CLASS THE SOURCE DID NOT WRITE may
    appear in the twin, which is what the recount guard of 7.12 buys:
    before it, 33 of the 320 four-character cells came out with a
    leading nought, a zero-filled four-figure spelling the source
    never wrote.
    """
    cells = wide_mixed_cells(source_seed)
    got = _round_trip(tmp_path / f"widths-{source_seed}", cells)
    assert got["twin_exit"] == 0 and got["real_exit"] == 0

    def classes(values: "list[str]") -> "dict[str, int]":
        found: dict[str, int] = {}
        for value in values:
            kind = "pad" if value[:1] == "0" and len(value) > 1 else "bare"
            key = f"{kind}-{len(value)}"
            found[key] = found.get(key, 0) + 1
        return {name: found[name] for name in sorted(found)}

    assert classes(got["cells"]) == classes(cells), (
        "the twin writes a spelling class the source never wrote"
    )
    assert _census_of(got["cells"]) == got["source"]["layout_forms"]


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_a_code_column_at_a_floor_of_twenty_keeps_its_length_mix(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """Landing 2b.12's carried item, re-measured and closed.

    A code column at a floor of twenty came back about a third SHORT:
    the base twin's mean cell length was 4.004 against the table's
    6.126, with the length mix collapsed from `{4: 233, 7: 567}` to
    `{4: 799, 7: 1}`, because the enumeration walks by ascending length
    from the shortest published and the shortest room fills first. The
    layout census IS the length census, so the mix comes back.
    """
    draw = random.Random(source_seed)
    cells = []
    for _row in range(ROWS):
        if draw.random() < 0.7:
            cells += [f"AB{draw.randrange(10000, 99999)}"]
        else:
            cells += [f"Z{draw.randrange(100, 999)}"]
    got = _round_trip(tmp_path / f"floor-{source_seed}", cells, floor=20)

    def widths(values: "list[str]") -> "dict[int, int]":
        found: dict[int, int] = {}
        for value in values:
            found[len(value)] = found.get(len(value), 0) + 1
        return found

    assert widths(got["cells"]) == widths(cells)
    mean_real = sum(len(cell) for cell in cells) / len(cells)
    mean_twin = sum(len(cell) for cell in got["cells"]) / len(got["cells"])
    assert mean_twin == pytest.approx(mean_real, abs=1e-9)
    assert got["twin_exit"] == 0 and got["real_exit"] == 0


# ----------------------------------------------- the two limits, pinned


def test_the_literal_run_is_published_by_ruling_and_the_twin_writes_it(
    tmp_path: pathlib.Path,
) -> None:
    """The owner's clause-3 question, answered (ruling of 2026-09-17, item 1).

    This test pinned the cost of NOT publishing a constant run: the
    layout-level pattern matched every twin cell and the prefix predicate
    none, with a note that it is the test that changes if the owner rules
    the literal publishable. The owner so ruled, and invariants I3 and F3
    are amended for that case (contract 7.12a, plan P4-D202). The column
    here holds `REC` and seven figures beside `E` and six, so no prefix is
    shared by the whole column and each layout publishes its own -- the
    per-layout reading of the ruling, flagged to the owner.
    """
    cells = mixed_length_cells(1)
    got = _round_trip(tmp_path / "literal", cells)
    twin = got["cells"]
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    assert got["source"]["layout_prefixes"] == {
        "@%%%%%%": "E", "@@@%%%%%%%": "REC",
    }

    # What the layouts bought before the ruling: the shape, the widths.
    layout_rule = re.compile(r"([A-Z]{3}[0-9]{7}|[A-Z][0-9]{6})")
    assert _matching(twin, layout_rule.pattern) == len(twin)
    assert _matching(cells, layout_rule.pattern) == len(cells)

    def widths(values: "list[str]") -> "dict[int, int]":
        found: dict[int, int] = {}
        for value in values:
            found[len(value)] = found.get(len(value), 0) + 1
        return found

    assert widths(twin) == widths(cells)

    # ...and what the ruling buys: the literal pattern selects the same rows.
    literal = r"(REC[0-9]{7}|E[0-9]{6})"
    assert _matching(twin, literal) == _matching(cells, literal) == len(cells)
    for prefix in ("REC", "E"):
        real_prefixed = len(
            [cell for cell in cells if cell[: len(prefix)] == prefix]
        )
        twin_prefixed = len(
            [cell for cell in twin if cell[: len(prefix)] == prefix]
        )
        assert real_prefixed > 0
        assert twin_prefixed == real_prefixed


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_a_layout_with_a_small_supply_is_not_published(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """The disclosure rule refusing a layout that names its own values.

    A column of `007` beside `7` publishes `%%%` and nothing else: `%`
    has exactly ten possible cells and `!%%` a hundred, and a layout
    whose supply is smaller than `n_distinct` plus the floor would hand
    a reader the values it describes. The one-figure and zero-filled
    three-figure cells are therefore NOT held to a layout, and this
    test pins that as the disclosure rule working rather than as a
    defect to be repaired.
    """
    cells = tiny_mixed_cells(source_seed)
    got = _round_trip(tmp_path / f"tiny-{source_seed}", cells)
    published = got["source"]["layout_forms"]
    assert set(published) <= {"%%%"}, (
        f"a layout with a small supply reached the page: {published}"
    )
    assert parsing.layout_room("%") == 10
    assert parsing.layout_room("!%%") == 100
    assert got["real_exit"] == 0


def repeating_cells(seed: int, rows: int = ROWS) -> "list[str]":
    """A two-system key of VISITS: identities recur, and some are missing.

    Each identity is written one, two or three times, in either system,
    and about one row in twenty is missing -- written `NA` or left empty
    -- which is what an encounter table keyed by a record number looks
    like.
    """
    draw = random.Random(seed)
    built: list[str] = []
    while len(built) < rows:
        if draw.random() < 0.05:
            built += [draw.choice(["NA", ""])]
            continue
        if draw.random() < 0.7:
            value = f"REC{draw.randrange(1000000, 9999999)}"
        else:
            value = f"E{draw.randrange(100000, 999999)}"
        built += [value] * draw.choice([1, 1, 2, 3])
    built = built[:rows]
    draw.shuffle(built)
    return built


def _recurrence_by_layout(cells: "list[str]") -> "dict[str, list[int]]":
    """For each layout, how many times its identities recur, as a set."""
    convention = parsing.layout_convention(list(cells))
    seen: dict[str, int] = {}
    for cell in cells:
        seen[cell] = seen.get(cell, 0) + 1
    found: dict[str, set] = {}
    for cell, many in seen.items():
        layout = parsing.layout_form(cell, convention)
        if layout:
            found.setdefault(layout, set()).add(many)
    return {layout: sorted(found[layout]) for layout in sorted(found)}


@pytest.mark.parametrize("source_seed", SOURCE_SEEDS)
def test_a_repeating_key_spreads_its_layouts_and_keeps_its_missing_cells(
    source_seed: int, tmp_path: pathlib.Path
) -> None:
    """The census is SPREAD over the identities, and the gaps stay gaps.

    MEASURED before the rotation of G9.6 existed: the walk reaches the
    identities written once before those written more often, and taking
    the first layout with room left gave the one-letter system 217
    singletons and no repeat at all while the table's one-letter system
    recurred one, two and three times. Code counting visits per record
    system met a system where nobody came back. Both systems recur on
    the table, so both recur on the twin.

    AND THE MISSING SPELLINGS COME BACK AT THEIR COUNTS: the `NA` cells
    and the empty cells of the table are written as `NA` and as empty
    cells on the twin, as many of each, and no identity is written in
    their place.
    """
    cells = repeating_cells(source_seed)
    got = _round_trip(tmp_path / f"repeat-{source_seed}", cells)
    assert got["twin_exit"] == 0 and got["real_exit"] == 0
    twin = got["cells"]
    published = got["source"]["layout_forms"]
    assert got["twin_profile"]["layout_forms"] == published
    assert _recurrence_by_layout(twin) == _recurrence_by_layout(cells)
    for spelling in ("NA", ""):
        assert twin.count(spelling) == cells.count(spelling), spelling
    rule = r"([A-Z]{3}[0-9]{7}|[A-Z][0-9]{6})"
    assert _matching(twin, rule) == _matching(cells, rule)
    assert _at_length(twin, 10) == _at_length(cells, 10)
    assert _in_case(twin, "upper") == _in_case(cells, "upper")


def test_a_twin_off_its_layout_is_missed_by_name(tmp_path: pathlib.Path) -> None:
    """The validator RECOUNTS the census; it does not take it on trust.

    Every cell of a real site-code column is turned one place to the
    right -- `NYC-2033` becomes `3NYC-203` -- which keeps its length,
    its alphabet, its class and its distinctness exactly and moves only
    what KIND of character stands where. Every other published fact
    holds, so the one check that can say MISSED is the census of
    layouts, and it has to say it by the layout's own name.
    """
    import json

    from tests.test_stage2_round_trip import _exit_of

    cells = site_code_cells(1)
    got = _round_trip(tmp_path / "base", cells)
    assert got["real_exit"] == 0
    turned = [cell[-1:] + cell[:-1] for cell in cells]
    folder = tmp_path / "turned"
    folder.mkdir()
    measured = folder / "turned.csv"
    measured.write_text(
        fixtures.rows_to_csv(
            ["value", "other"],
            [[turned[index], f"row{index % 7}"] for index in range(len(turned))],
        ),
        encoding="utf-8",
        newline="",
    )
    profile = tmp_path / "base" / "real-profile.json"
    published = json.loads(profile.read_text(encoding="utf-8"))["columns"][0][
        "layout_forms"
    ]
    assert published == {"@@@-%%%%": len(cells)}
    checked = folder / "check"
    checked.mkdir()
    assert _exit_of(
        ["validate", str(profile), "--twin", str(measured), "--out-dir",
         str(checked), "--replace"]
    ) == 3
    report = (checked / "turned-quality.txt").read_text(encoding="utf-8")
    missed = [line for line in report.splitlines() if "MISSED" in line]
    assert any("@@@-%%%%" in line for line in missed), missed
