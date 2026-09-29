"""The two mixture censuses bound what a reader of the WHOLE block can take (plan P4-D356).

THE DEFECT (the review of follow-up B). Plan P4-D352 let a census of marks
or notations that holds every convention under the line pool where the
vocabulary's size allowed it, and counted a larger pool under its commonest
convention (the band). Both read the vocabulary alone, and the rest of the
block bounds more than the vocabulary does:

1. ten `12.00-` beside nine each of `-12`, `(12)` and `-12` written with
   the minus sign, seventy-three `12` and one `12.50`, at a floor of
   eleven, published `{"trailing_minus": 37}` beside a forms map leaving
   too few cells with a point for 37 trailing minuses, so a reader knew
   the band had spoken, that no notation reached eleven, and so that the
   commonest held exactly ten;
2. ten `1,234`, ten `1 234` and eighty `12` published `{"(withheld)":
   20}` beside three different spellings, so the pool held two marks at
   most, both at exactly ten, and the comma warning named one of them;
3. a hand-written census naming five marks at sixteen beside a pool of
   twenty loaded, and its twin, writing all twenty with one mark, held;
4. seven `1,234.00` and seven `1 234.00` beside eighty-six bare -- and,
   now that that pool is counted under one mark, five, five and four
   over three marks -- came back with eight spellings where the source
   shows three or four suffice.

Every column here is built by seeded neutral code at test time.
"""

import collections
import pathlib
import random

import pytest

from synthtwin import (
    contract,
    dialect,
    errors,
    parsing,
    profile,
    reading,
    taxonomy,
    validation,
)
from tests import fixtures
from tests.test_stage2_round_trip import _round_trip

LINE = 11
MARKS = parsing.GROUP_MARKS
SEEDS = ("0", "1", "2", "3", "4")


def _document(cells: "list[str]", floor: int = LINE) -> "dict[str, object]":
    """The producer's description of one measured column, loaded back once."""
    table = reading.Table(
        ["value"], [cells], len(cells), dialect.ENCODING_UTF8, False,
        reading.HEADER_FROM_FILE, reading._TAKEN_BY_CONVENTION, True,
    )
    document = profile.build_document(
        table, taxonomy.Settings(small_cell_floor=floor), [],
        forced_measurements=["value"],
    )
    contract._validated(document)
    return document


def _block(cells: "list[str]", floor: int = LINE) -> "dict[str, object]":
    column = _document(cells, floor)["columns"]
    assert isinstance(column, list)
    block = column[0]
    assert isinstance(block, dict)
    return block


def _refusal(document: "dict[str, object]", folder: pathlib.Path) -> str:
    """What the strict loader says of a description written in its exact form."""
    path = fixtures.write_profile(folder, "hand-profile.json", document)
    try:
        contract.load_profile(str(path))
    except errors.ProfileError as refused:
        return str(refused)
    return "accepted"


# ---------------------------------------------------------------- the shapes

ITEM_ONE = (
    ["12.00-"] * 10 + ["-12"] * 9 + ["(12)"] * 9 + ["\u221212"] * 9
    + ["12"] * 73 + ["12.50"]
)
ITEM_TWO = ["1,234"] * 10 + ["1 234"] * 10 + ["12"] * 80


def _seven_marks_of_ten() -> "list[str]":
    """Seventy whole numbers, ten per mark, each a lone group; a hundred small."""
    draw = random.Random("seven marks of ten, lone groups")
    cells: "list[str]" = []
    for mark in MARKS:
        cells += [
            f"{draw.randint(10, 99)}{mark}{draw.randint(0, 999):03d}"
            for _ in range(10)
        ]
    cells += [str(draw.randint(1, 999)) for _ in range(100)]
    return cells


def _band_beside_whole() -> "list[str]":
    """Ten `x.yy-` beside nine each of `(x)`, `-x` and `-x` with the minus sign."""
    draw = random.Random(601)
    out = [f"{draw.randint(1, 999)}.{draw.randint(0, 99):02d}-" for _ in range(10)]
    out += [f"({draw.randint(1, 999)})" for _ in range(9)]
    out += [f"-{draw.randint(1, 999)}" for _ in range(9)]
    out += [f"\u2212{draw.randint(1, 999)}" for _ in range(9)]
    out += [
        f"{draw.randint(1, 999)}" if draw.random() < 0.5
        else f"{draw.randint(1, 999)}.{draw.randint(0, 99):02d}"
        for _ in range(130)
    ]
    draw.shuffle(out)
    return out


# ------------------------------------------------------- item 1, the band


def test_a_band_takes_no_notation_some_negative_cannot_wear() -> None:
    """The review's column: 37 negatives, a point on ten of them.

    Derived from the rule: no notation reaches eleven and 37 is more than
    three notations hold below it, so the census is counted under one
    notation. The commonest is the trailing minus (10), which only a
    figure with a point can wear, and 27 negatives carry none; of the
    three others, nine each, the first in the contract's order is the
    hyphen-minus. So `{"minus": 37}` and `negative_form` `minus`.
    At 2af1f03 it published `{"trailing_minus": 37}` beside the forms map
    `plain 100, decimal 11`, which no table writing 37 negatives with a
    point stands beside, and so fixed the trailing minuses at ten.
    Mutation: `_reader_bounds` answering every notation wearable turns
    it red.
    """
    block = _block(ITEM_ONE)
    assert block["numeric_styles"] == {"plain": 100, "decimal": 11}
    assert block["negative_notations"] == {"minus": 37}
    assert block["negative_form"] == "minus"


def test_a_band_counted_under_the_hyphen_minus_is_written_so(tmp_path) -> None:
    """The same band on a column of amounts, through the three commands.

    The shape the trailing-minus gate carried as `band-beside-whole` until
    this review: every negative the twin writes wears the hyphen-minus in
    front, the twin's own description counts all 37 there, and both files
    validate.
    """
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path, _band_beside_whole(), (), seed="0"
    )
    assert first["negative_notations"] == {"minus": 37}
    assert second["negative_notations"] == {"minus": 37}
    assert first["negative_form"] == second["negative_form"] == "minus"
    assert twin_exit == 0 and real_exit == 0
    assert sum(1 for cell in written if cell.endswith("-")) == 0


def test_a_band_keeps_a_trailing_minus_where_every_negative_has_a_point() -> None:
    """The control: ten `12.50-` beside nine each of the others, all pointed."""
    cells = (
        ["12.50-"] * 10 + ["-12.25"] * 9 + ["(12.75)"] * 9
        + ["\u221212.05"] * 9 + ["12"] * 73
    )
    assert _block(cells)["negative_notations"] == {"trailing_minus": 37}


def test_the_comma_warning_keeps_a_band_of_marks_from_speaking() -> None:
    """Seven marks of ten whole lone groups each, beside the comma warning.

    At 2af1f03 the band published `{",": 70}` while the comma warning said
    fewer than eleven cells wrote a comma that reads either way: seventy
    commas would have said seventy, so a reader knew the band had spoken
    and each mark held exactly ten. Counted under the comma the warning's
    count moves up, under any other mark down to nought, so no mark keeps
    it and the census is silent, `{}`, with no mark published.
    Mutation: `_reader_bounds` answering every mark wearable turns it red.
    """
    block = _block(_seven_marks_of_ten())
    assert block["thousands_marks"] == {}
    assert block["group_separator"] == ""
    assert any("comma" in remark for remark in block["remarks"])


# -------------------------------------------------- item 2, the lone pool


def test_a_pool_its_spellings_fix_is_not_published() -> None:
    """The review's column: twenty grouped cells of one value, two marks.

    Derived from the rule: the pooled cells hold two spellings, so a
    reader sees at most two marks, and twenty is more than one mark holds
    below eleven -- the pool may not stand. Counted under the comma the
    warning would count twenty, under the space nought, so the census is
    silent. At 2af1f03 it published `{"(withheld)": 20}`.
    Mutation: `parsing.mixture_pool_holds` reading the room as the
    vocabulary's size turns it red.
    """
    block = _block(ITEM_TWO)
    assert block["n_distinct"] == 3
    assert block["thousands_marks"] == {}
    assert block["group_separator"] == ""


def test_a_pool_of_notations_its_spellings_fix_is_counted_under_one() -> None:
    """Ten `(12)` and ten `-12`: two spellings, so two notations at most.

    At 2af1f03 `{"(withheld)": 20}` beside three different spellings fixed
    both notations at ten. Twenty is more than one notation holds below
    eleven, so it is counted under one: brackets and the hyphen-minus
    both hold ten, and the first in the contract's order is `minus`.
    """
    block = _block(["(12)"] * 10 + ["-12"] * 10 + ["5"] * 100)
    assert block["negative_notations"] == {"minus": 20}
    assert block["negative_form"] == "minus"


def test_a_trailing_minus_on_few_points_bounds_the_pool_too() -> None:
    """Three `12.50-` beside twenty-two whole negatives, a pool of 25.

    Three notations of ten and a trailing minus of three hold 23 with the
    hyphen-minus absent, so a pool of 25 said the hyphen-minus was
    written. At 2af1f03 it published `{"(withheld)": 25}`; counted under
    the commonest notation every negative can wear it is `{"minus": 25}`.
    """
    draw = random.Random("few points")
    cells = (
        ["12.50-"] * 3 + ["-12"] * 9 + ["(12)"] * 9 + ["\u221212"] * 4
        + [str(draw.randint(1, 999)) for _ in range(100)]
    )
    assert _block(cells)["negative_notations"] == {"minus": 25}


def test_the_spelling_room_is_the_census_rule_on_a_full_vocabulary() -> None:
    """With every capacity at the line and a full room it is `census_pools`, and never looser.

    Where the line is more than the vocabulary -- eight and up for the
    marks, five and up for the notations, so at the default floor of
    eleven for both -- the two agree cell for cell; under it the rule that
    no count stands in every reading refuses more.
    """
    for floor in (2, 3, 5, 8, 11, 31):
        for names in (4, 7):
            for population in range(0, 8 * max(2, floor)):
                mixture = parsing.mixture_pool_holds(
                    population, floor, [population] * names, 99
                )
                closed = parsing.census_pools(population, floor, names)
                if max(2, floor) > names:
                    assert mixture == closed
                else:
                    assert closed or not mixture


@pytest.mark.parametrize(
    "population,floor,capacities,room,holds",
    (
        (20, 11, [20] * 7, 2, False),  # two marks at most: ten each
        (10, 11, [10] * 7, 2, True),  # one mark could hold it all
        (20, 11, [20] * 7, 3, True),  # three: two could, and any one absent
        (30, 11, [30] * 4, 4, True),  # three notations of ten
        (31, 11, [31] * 4, 4, False),  # past three notations of ten
        (25, 11, [25, 25, 25, 3], 4, False),  # 10 + 10 + 3 without a minus
        (23, 11, [23, 23, 23, 3], 4, True),  # exactly that
        (5, 2, [5] * 7, 5, False),  # at a line of two every pool is ones
        (12, 11, [12] * 7, 1, False),  # one spelling: one mark at twelve
        (3, 3, [3] * 4, 3, False),  # two and one, or three ones: a one in each
        (4, 3, [4] * 4, 4, True),  # two twos, a two and two ones, four ones
        (19, 11, [19] * 7, 3, True),  # three marks: 10 9, 10 8 1 ... no count in all
        (29, 11, [29] * 4, 3, False),  # two notations hold twenty at most
    ),
)
def test_the_pool_rule_on_hand_worked_rows(population, floor, capacities, room, holds) -> None:
    """Each row worked from the rule: one convention fewer than the room holds it, and any one may be absent."""
    assert parsing.mixture_pool_holds(population, floor, capacities, room) is holds


# ---------------------------------------------------------------- the loader


def test_the_loader_refuses_a_pool_its_spellings_fix(tmp_path) -> None:
    """Item 2's description as 2af1f03 wrote it: refused under TM1.

    The column publishes three different spellings, so its twenty grouped
    cells show two marks at most, and one mark holds ten below eleven.
    """
    document = _document(ITEM_TWO)
    column = document["columns"][0]
    column["thousands_marks"] = {"(withheld)": 20}
    said = _refusal(document, tmp_path)
    assert "TM1" in said and "20 grouped numbers are held back beside 3" in said


def test_the_loader_refuses_a_pool_of_notations_its_spellings_fix(tmp_path) -> None:
    """Ten `(12)` and ten `-12` beside a hundred `5`, pooled by hand: NS2."""
    document = _document(["(12)"] * 10 + ["-12"] * 10 + ["5"] * 100)
    column = document["columns"][0]
    column["negative_notations"] = {"(withheld)": 20}
    said = _refusal(document, tmp_path)
    assert "NS2" in said and "20 negative numbers are held back beside 3" in said


def _grouped_hundred() -> "dict[str, object]":
    return _document([f"{1234.25 + step:,.2f}" for step in range(100)])


def test_the_loader_refuses_a_pool_beside_named_marks(tmp_path) -> None:
    """Item 3: five marks named at sixteen beside a pool of twenty.

    No producer writes it -- a mark under the line is counted into the
    commonest named one -- and it fixed the two unnamed marks at ten each.
    At 2af1f03 the strict loader took it. Mutation: the
    `_pool_stands_alone` call withdrawn from TM1 turns it red.
    """
    document = _grouped_hundred()
    column = document["columns"][0]
    column["group_separator"] = ""
    column["thousands_marks"] = {
        ",": 16, " ": 16, "'": 16, "\u2019": 16, "\u00a0": 16, "(withheld)": 20,
    }
    said = _refusal(document, tmp_path)
    assert "TM1" in said and "held back beside a named count" in said


def test_the_loader_refuses_a_pool_beside_a_named_notation(tmp_path) -> None:
    """The same on the notations: brackets named at twenty beside a pool of eleven."""
    cells = ["(12)"] * 20 + ["-13"] * 6 + ["\u221214"] * 5 + ["5"] * 100
    document = _document(cells)
    column = document["columns"][0]
    assert column["negative_notations"] == {"brackets": 31}
    column["negative_notations"] = {"brackets": 20, "(withheld)": 11}
    said = _refusal(document, tmp_path)
    assert "NS2" in said and "held back beside a named count" in said


def test_a_pool_beside_named_marks_is_an_obligation_too() -> None:
    """Item 3's twin, checked as the checker would if such a census reached it.

    The census says twenty cells wore marks it does not name, each on
    fewer than eleven. A file naming one of those marks at twenty has not
    written the pool; at 2af1f03 only the five named counts were compared
    and it held. One pooling fifteen beside the same five has not written
    it either. A file pooling the same twenty, beside the same five, holds.
    Mutation: the pooled count's comparison withdrawn turns the first two
    red.
    """
    census = {",": 16, " ": 16, "'": 16, "\u2019": 16, "\u00a0": 16, "(withheld)": 20}
    named = {",": 16, " ": 16, "'": 16, "\u2019": 16, "\u00a0": 16}
    one_mark = dict(named, **{"\u202f": 20})
    fewer = dict(named, **{"(withheld)": 15})
    pooled = dict(named, **{"(withheld)": 20})
    order = parsing.PUBLISHED_GROUP_MARKS
    verdicts = [
        validation._mixture_check("value", "thousands_marks", census, file, order, 100, LINE, 100).verdict
        for file in (one_mark, fewer, pooled)
    ]
    assert verdicts == [validation.MISSED, validation.MISSED, validation.HELD]


# ------------------------------------------------- item 4, the marks spent


def _three_marks_one_value() -> "list[str]":
    return (
        ["1,234.00"] * 5 + ["1 234.00"] * 5 + ["1'234.00"] * 4 + ["1234.00"] * 86
    )


@pytest.mark.parametrize("seed", SEEDS)
def test_a_lone_pool_is_spent_over_no_more_marks_than_the_spellings_allow(seed, tmp_path) -> None:
    """Five, five and four grouped cells of one value over three marks.

    Derived from the rule: the census pools fourteen beside four different
    spellings. Seven marks over one value write eight spellings, six seven,
    five six, four five and three four, so three marks are spent -- and
    three is also the fewest whose rooms, two of ten, hold fourteen, so the
    twin's own description pools it again. At 2af1f03 the twin wrote eight
    spellings at five seeds of five and both distinctness checks passed as
    authorized deviations. Mutation: `_pool_mark_count` answering seven
    turns every seed red.
    """
    first, second, written, twin_exit, real_exit = _round_trip(
        tmp_path, _three_marks_one_value(), (), seed=seed
    )
    assert first["thousands_marks"] == {"(withheld)": 14}
    assert first["n_distinct"] == 4
    assert len(set(written)) == 4
    assert second["thousands_marks"] == {"(withheld)": 14}
    assert second["n_distinct"] == 4
    assert twin_exit == 0 and real_exit == 0


def test_the_review_s_two_marks_are_counted_under_one(tmp_path) -> None:
    """Seven `1,234.00` and seven `1 234.00`: two spellings, a band of fourteen.

    The review's own column for item 4. Its pooled cells hold two
    spellings, so the pool may not stand (one mark holds ten below
    eleven); the comma warning reads neither `1,234.00` nor its space
    twin, so the band keeps it, and the comma is first on the tie. The
    twin writes fourteen commas and holds the three published spellings.
    """
    cells = ["1,234.00"] * 7 + ["1 234.00"] * 7 + ["1234.00"] * 86
    first, second, written, twin_exit, real_exit = _round_trip(tmp_path, cells, (), seed="0")
    assert first["thousands_marks"] == {",": 14}
    assert first["n_distinct"] == 3
    assert len(set(written)) == 3
    assert twin_exit == 0 and real_exit == 0


# ----------------------------------------------------------------- the battery
#
# A READER OF THE WHOLE BLOCK, written here and not taken from the producer.
# Where a census is a lone pool, every world the block admits is enumerated:
# counts under the line, a trailing minus on no more cells than carry a
# point, no more conventions than the pooled cells' different spellings,
# and the comma written wherever the comma warning counts a cell. The pool
# may leave no count forced -- none a convention must take, none every
# world holds -- and no convention forced to be written. Where a census
# names ONE convention over cells that each held fewer than the line (a
# band), the table with every such cell written in that convention is
# described again, and it must publish the same block but for its count
# of different spellings and the remark that reads it -- which a table
# can make up with a spelling in a form the forms census counts into its
# commonest, `+1 234` or `012` -- otherwise a reader tells the band from
# a table that wrote one convention.

BATTERY = 240


def _hyphen_first(text: str) -> str:
    """A negative cell with its notation read back to the hyphen-minus in front."""
    body = text.strip()
    if body[:1] == "(" and body[-1:] == ")":
        return "-" + body[1:-1]
    if body[:1] == "\u2212":
        return "-" + body[1:]
    if body[-1:] == "-":
        return "-" + body[:-1]
    return body


def _grouped(value: int, mark: str) -> str:
    text = f"{value:,}"
    return text.replace(",", mark)


def _battery_shapes() -> "list[tuple[str, list[str], int, list[str], list[str]]]":
    """(kind, cells, floor, the counted cells, their conventions), seeded."""
    draw = random.Random("mixture reader battery")
    shapes: "list[tuple[str, list[str], int, list[str], list[str]]]" = []
    for _index in range(BATTERY):
        floor = draw.choice((3, 5, 11, 11, 11, 31))
        line = max(2, floor)
        values = [draw.randint(1000, 99999) for _ in range(draw.choice((1, 1, 2, 3, 40)))]
        counted: "list[str]" = []
        worn: "list[str]" = []
        if draw.random() < 0.5:
            kind = "marks"
            pointed = draw.random() < 0.5
            for mark in draw.sample(MARKS, draw.randint(1, 7)):
                for _cell in range(draw.randint(1, line + 2)):
                    text = _grouped(draw.choice(values), mark)
                    counted += [text + (".50" if pointed else "")]
                    worn += [mark]
        else:
            kind = "notations"
            share = draw.choice((0.0, 0.3, 1.0))
            small = [draw.randint(1, 99) for _ in range(len(values))]
            for form in draw.sample(parsing.NEGATIVE_FORMS, draw.randint(1, 4)):
                for _cell in range(draw.randint(1, line + 2)):
                    value = draw.choice(small)
                    point = form == parsing.NEGATIVE_TRAILING or draw.random() < share
                    text = f"-{value}.25" if point else f"-{value}"
                    counted += [parsing.with_negative_notation(text, form)]
                    worn += [form]
        rest = [str(draw.randint(1, 999)) for _ in range(120)]
        cells = counted + rest
        draw.shuffle(cells)
        shapes += [(kind, cells, floor, counted, worn)]
    return shapes


def _partitions(total: int, parts: int, most: int) -> "list[tuple[int, ...]]":
    """Every way to write ``total`` as ``parts`` counts of 1 to ``most``, descending."""
    found: "list[tuple[int, ...]]" = []

    def walk(left: int, room: int, cap: int, taken: "tuple[int, ...]") -> None:
        if room == 0:
            if left == 0:
                found.extend([taken])
            return
        for part in range(min(cap, left), 0, -1):
            if part * room < left:
                break
            walk(left - part, room - 1, part, taken + (part,))

    walk(total, parts, most, ())
    return found


def _lone_pool_leak(kind: str, pool: int, floor: int, counted: "list[str]", comma: bool) -> str:
    """Why the worlds a lone pool admits pin a count, or ""."""
    line = max(2, floor)
    names = 7 if kind == "marks" else 4
    room = min(names, len({parsing.folded(text) for text in counted}))
    if kind == "notations":
        points = sum(1 for text in counted if "." in text)
        worlds = []
        for minus in range(line):
            for brackets in range(line):
                for sign in range(line):
                    trailing = pool - minus - brackets - sign
                    if not 0 <= trailing <= min(line - 1, points):
                        continue
                    world = (minus, brackets, sign, trailing)
                    if sum(1 for count in world if count) <= room:
                        worlds += [world]
        for place in range(4):
            seen = {world[place] for world in worlds}
            if 0 not in seen:
                return f"{parsing.NEGATIVE_FORMS[place]} is always written: {sorted(seen)}"
        shared = None
        for world in worlds:
            held = {count for count in world if count}
            shared = held if shared is None else shared & held
        return f"every world holds a count of {sorted(shared)}" if shared else ""
    partitions = []
    for parts in range(1, room + 1):
        partitions += _partitions(pool, parts, line - 1)
    shared = None
    for partition in partitions:
        shared = set(partition) if shared is None else shared & set(partition)
    if shared:
        return f"every world holds a count of {sorted(shared)}"
    if all(len(partition) >= names for partition in partitions):
        return "every mark is written in every world"
    if comma:
        seen = set()
        for partition in partitions:
            seen |= set(partition)
        if len(seen) < 2:
            return f"the comma the warning names holds {sorted(seen)}"
    return ""


def _band_leak(block, cells, floor, counted, worn, kind, name) -> str:
    """Where the table writing every counted cell in the band's convention publishes otherwise."""
    rewritten = []
    lookup = {}
    for text, convention in zip(counted, worn):
        if kind == "marks":
            lookup[text] = parsing.with_thousands_mark(text, name)
        else:
            lookup[text] = parsing.with_negative_notation(_hyphen_first(text), name)
    for text in cells:
        rewritten += [lookup.get(text, text)]
    other = _block(rewritten, floor)
    for key in sorted(set(block) | set(other)):
        if key in ("n_distinct", "n_distinct_folded"):
            continue
        mine, theirs = block.get(key), other.get(key)
        if key == "remarks":
            mine = [said for said in mine if not said.startswith(EVERY_DIFFERENT)]
            theirs = [said for said in theirs if not said.startswith(EVERY_DIFFERENT)]
        if mine != theirs:
            return f"{key}: {mine!r} against {theirs!r}"
    return ""


# The remark that reads the count of different spellings against the rows.
EVERY_DIFFERENT = "every value in this column is different"


def test_no_mixture_census_lets_a_reader_of_the_whole_block_pin_a_count() -> None:
    """240 seeded columns, each census read by the reader above.

    At 2af1f03 this reader pins counts on the review's two shapes and on
    their siblings in the battery (the measurement is in plan P4-D356); it
    finds none now. Mutations, each run: `mixture_pool_holds` reading the
    room as the vocabulary's size, and `_reader_bounds` answering every
    convention wearable, each turn it red.
    """
    leaks: "list[str]" = []
    pools = bands = 0
    for index, (kind, cells, floor, counted, worn) in enumerate(_battery_shapes()):
        block = _block(cells, floor)
        census = block["thousands_marks" if kind == "marks" else "negative_notations"]
        line = max(2, floor)
        tally = collections.Counter(worn)
        if census == {"(withheld)": len(counted)}:
            pools += 1
            comma = kind == "marks" and any(
                "read either way" in remark or "either way" in remark
                for remark in block["remarks"]
            )
            said = _lone_pool_leak(kind, len(counted), floor, counted, comma)
            if said:
                leaks += [f"{index} {kind} pool {len(counted)} at {floor}: {said}"]
        elif len(census) == 1 and max(tally.values()) < line:
            name = next(iter(census))
            if census[name] == len(counted) and name != "(unavailable)":
                bands += 1
                said = _band_leak(block, cells, floor, counted, worn, kind, name)
                if said:
                    leaks += [f"{index} {kind} band {name!r} at {floor}: {said}"]
    assert leaks == []
    assert pools >= 30 and bands >= 15
