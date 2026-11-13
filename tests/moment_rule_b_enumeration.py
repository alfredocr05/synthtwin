"""K-S6-08's moment fixtures under the owner's rule B (contract 4.6d.0 and 4.6d.7, plan P4-D455), by exhaustive enumeration.

Rule B publishes a moment only where every count it implies DIRECTLY is 0
or at least the floor `f`. These enumerations run the PRODUCT's own
functions (`chain_moments.within_moments`, `pair_moments` and
`column_moments`) on every small configuration of counts, and count, for
every moment published, the direct counts inside 1 to `f - 1`:

- a binary's share within the two bands of a grouping column: each band's
  readings `n_g`, its rows without a reading `T_g - n_g`, and its two
  levels' rows; and RULE W1 where a band holds an own-fact group of the
  grouping column (`small`): such a band shows at least two of its
  levels' rows and its absent rows;
- a number's mean and spread within the two bands: each band's readings
  and its rows without one;
- the same read on the `L2` bands where the `L1` bands cannot all pass:
  three `L1` bands, the first two one `L2` band;
- the correlation of two numbers: the four cells of the pair's presence
  table, the rows holding both, each column's readings outside them and
  the rows holding neither (a column's own unread count, where the other
  column holds a reading on every row, stands: it is a count the column
  publishes about itself);
- a binary's own share: its two levels' rows.

`leaking` must be 0 on the product. Each MUTANT drops one check (the
level floor, the absent rows' floor, the readings' floor, RULE W1, the
outside readings' floor, the neither cell's floor) and must leak, which is
the fixtures' discrimination. Nothing here reads a description: the counts
are the moment's direct ones by construction.
"""

import itertools
import random

from synthtwin import chain, chain_check, chain_moments, chain_rules, errors, taxonomy

DECLARED = {"code": False, "measurement": False, "decimal_comma": False}


def _rows(splits: "list[tuple[int, int, int]]") -> "tuple[bytes, bytearray, list[int], tuple[int, ...]]":
    """Rows for a grouping of bands and one column: each band's (ones, zeros, absent)."""
    values = bytearray()
    present = bytearray()
    bands: "list[int]" = []
    totals: "list[int]" = []
    for band in range(len(splits)):
        ones, zeros, absent = splits[band]
        values += bytes([1] * ones + [0] * zeros + [0] * absent)
        present += bytes([1] * (ones + zeros) + [0] * absent)
        bands += [band] * (ones + zeros + absent)
        totals += [ones + zeros + absent]
    return bytes(values), present, bands, tuple(totals)


def _band_leaks(split: "tuple[int, int, int]", floor: int, kind: str, small: bool) -> bool:
    """One published band's direct counts, and W1 where it holds an own-fact group: True where one lies in 1 to f - 1."""
    ones, zeros, absent = split
    direct = [ones + zeros, absent] + ([ones, zeros] if kind == chain_moments.KIND_BINARY else [])
    if any(0 < count < floor for count in direct):
        return True
    return kind == chain_moments.KIND_BINARY and small and len([part for part in split if part]) < 2


def _mutant_within(splits: "list[tuple[int, int, int]]", floor: int, drop: str, kind: str, small: "frozenset[int]") -> bool:
    """Rule B's band check with one direct count, or RULE W1, left unread: True where it would publish."""
    for band in range(len(splits)):
        ones, zeros, absent = splits[band]
        n = ones + zeros
        checks = {"readings": n, "absent": absent}
        if kind == chain_moments.KIND_BINARY:
            checks = {"readings": n, "absent": absent, "ones": ones, "zeros": zeros}
        for name in checks:
            if name != drop and not chain_moments.passes(checks[name], floor):
                return False
        if drop != "W1" and kind == chain_moments.KIND_BINARY and band in small and len([part for part in splits[band] if part]) < 2:
            return False
    return True


def _parts(largest: int, kind: str, counts: "tuple[int, ...]" = ()) -> "list[tuple[int, int, int]]":
    """A band's (ones, zeros, absent): every split up to `largest` rows, or each part drawn from `counts`."""
    if counts:
        return [split for split in itertools.product(counts, repeat=3) if kind == chain_moments.KIND_BINARY or split[1] == 0]
    if kind == chain_moments.KIND_NUMBER:
        return [(o, 0, a) for o in range(largest + 1) for a in range(largest + 1 - o)]
    return [(o, z, a) for o in range(largest + 1) for z in range(largest + 1 - o) for a in range(largest + 1 - o - z)]


def shares(
    floor: int,
    largest: int,
    kind: str = chain_moments.KIND_BINARY,
    drop: str = "",
    small: "frozenset[int]" = frozenset(),
    counts: "tuple[int, ...]" = (),
) -> "dict[str, int]":
    """Every two-band configuration up to `largest` rows a band (or with each part drawn from `counts`): moments
    published, and published with a direct count of 1 to f - 1 (or a W1 band of one part)."""
    parts = _parts(largest, kind, counts)
    published = leaking = configurations = 0
    for first, second in itertools.product(parts, parts):
        configurations += 1
        if drop:
            publishes = _mutant_within([first, second], floor, drop, kind, small)
        else:
            values, present, bands, totals = _rows([first, second])
            column = chain_moments.Released("y", kind, values, present)
            grouping = chain_moments.Grouping("x", bands, totals, small, (0, 1))
            publishes = chain_moments.within_moments(column, grouping, floor)[0] is not None
        if not publishes:
            continue
        published += 1
        if any(_band_leaks(split, floor, kind, band in small) for band, split in enumerate((first, second))):
            leaking += 1
    return {"configurations": configurations, "published": published, "leaking": leaking}


def coarse(floor: int, counts: "tuple[int, ...]", kind: str = chain_moments.KIND_BINARY) -> "dict[str, int]":
    """Three `L1` bands, the first two one `L2` band: the first two bands' parts drawn from `counts`, the third from
    a short list (empty, at the floor, and one part of 1): moments published at either level, and published with a
    direct count of 1 to f - 1 at the level published (or a W1 band of one part, the second `L1` band holding an
    own-fact group)."""
    parts = [split for split in itertools.product(counts, repeat=3) if kind == chain_moments.KIND_BINARY or split[1] == 0]
    thirds = [(0, 0, 0), (floor, floor, 0), (floor, 0, floor), (1, floor, 0), (floor, floor, 1)]
    thirds = [split for split in thirds if kind == chain_moments.KIND_BINARY or split[1] == 0]
    published = leaking = configurations = coarser = 0
    small = frozenset({1})
    for first_two in itertools.product(parts, repeat=2):
        for third in thirds:
            splits = (first_two[0], first_two[1], third)
            configurations += 1
            values, present, bands, totals = _rows(list(splits))
            column = chain_moments.Released("y", kind, values, present)
            grouping = chain_moments.Grouping("x", bands, totals, small, (0, 0, 1))
            groups, _share, _why, level = chain_moments.within_moments(column, grouping, floor)
            if groups is None:
                continue
            published += 1
            if level == chain_moments.LEVEL_COARSE:
                coarser += 1
                first, second, _third = splits
                read = [((first[0] + second[0], first[1] + second[1], first[2] + second[2]), True), (third, False)]
            else:
                read = [(split, band in small) for band, split in enumerate(splits)]
            if any(_band_leaks(split, floor, kind, held) for split, held in read):
                leaking += 1
    return {"configurations": configurations, "published": published, "leaking": leaking, "coarser": coarser}


def pairs(floor: int, largest: int, drop: str = "") -> "dict[str, int]":
    """Every presence table of two numbers up to `largest` rows a cell (both, only x, only y, neither): correlations
    published, and published with a direct count of 1 to f - 1 other than a column's own unread count; and, for each
    the product publishes, the loader's S41 (`chain_check._pair_counts`) read in both pair orders: `loader_refused`
    counts those it refuses (the verify's item 1 on repair 1: 12 at f = 3, 60 at f = 11, each beside a complete
    column, before the waiver read the right column)."""
    published = leaking = configurations = loader_refused = 0
    for both, only_x, only_y, neither in itertools.product(range(largest + 1), repeat=4):
        if both < 2:
            continue
        configurations += 1
        x_full = only_y == 0 and neither == 0
        y_full = only_x == 0 and neither == 0
        if drop == "outside":
            publishes = both >= floor and chain_moments.passes(neither, floor)
        elif drop == "neither":
            publishes = both >= floor and (chain_moments.passes(only_x, floor) or x_full) and (chain_moments.passes(only_y, floor) or y_full)
        else:
            rows = both + only_x + only_y + neither
            px = bytearray([1] * (both + only_x) + [0] * (only_y + neither))
            py = bytearray([1] * both + [0] * only_x + [1] * only_y + [0] * neither)
            xs = bytes((r * 7) % 256 if px[r] else 0 for r in range(rows))
            ys = bytes((r * 13 + r * r) % 256 if py[r] else 0 for r in range(rows))
            pair, _why = chain_moments.pair_moments(
                chain_moments.Released("x", chain_moments.KIND_NUMBER, xs, px),
                chain_moments.Released("y", chain_moments.KIND_NUMBER, ys, py),
                floor,
            )
            publishes = pair is not None
            if publishes:
                for one, two in ((both + only_x, both + only_y), (both + only_y, both + only_x)):
                    try:
                        chain_check._pair_counts("x and y", both, one, two, floor, rows)
                    except errors.ProfileError:
                        loader_refused += 1
                        break
        if not publishes:
            continue
        published += 1
        direct = [both, neither] + ([] if x_full else [only_x]) + ([] if y_full else [only_y])
        if any(0 < count < floor for count in direct):
            leaking += 1
    return {"configurations": configurations, "published": published, "leaking": leaking, "loader_refused": loader_refused}


def columns(floor: int, largest: int) -> "dict[str, int]":
    """Every binary of up to `largest` readings: shares published, and published with a level of 1 to f - 1 rows."""
    published = leaking = 0
    for ones in range(largest + 1):
        for zeros in range(largest + 1 - ones):
            column = chain_moments.Released("y", chain_moments.KIND_BINARY, bytes([1] * ones + [0] * zeros), bytearray([1] * (ones + zeros)))
            if chain_moments.column_moments(column, floor)[0] is None:
                continue
            published += 1
            if any(0 < count < floor for count in (ones, zeros, ones + zeros)):
                leaking += 1
    return {"published": published, "leaking": leaking}


def _coarse_counts(floor: int) -> "tuple[int, ...]":
    return (0, 1, floor - 1, floor, floor + 1)


def w1_counts(floor: int) -> "tuple[int, ...]":
    """The parts W1's enumeration draws from: nought, one, the floor's neighbours and twice the floor."""
    return (0, 1, floor - 1, floor, floor + 1, 2 * floor)


def measure(floors: "tuple[tuple[int, int], ...]" = ((3, 8), (11, 14))) -> "dict[str, int]":
    """K-S6-08's moment keys: published and leaking at each floor, each mutant's leaks (at least 1 each), and the
    presence tables the product publishes that the loader's S41 refuses in either pair order (0)."""
    out: "dict[str, int]" = {}
    for floor, largest in floors:
        found = [
            shares(floor, largest),
            shares(floor, largest, chain_moments.KIND_NUMBER),
            shares(floor, largest, small=frozenset({0}), counts=w1_counts(floor)),
            shares(floor, largest, small=frozenset({0, 1}), counts=w1_counts(floor)),
            coarse(floor, _coarse_counts(floor)),
            coarse(floor, _coarse_counts(floor), chain_moments.KIND_NUMBER),
            pairs(floor, 2 * floor + 2),
        ]
        own = columns(floor, 4 * floor)
        out[f"moment_published_f{floor}"] = sum(part["published"] for part in found) + own["published"]
        out[f"moment_configurations_f{floor}"] = sum(part["configurations"] for part in found)
        out[f"moment_leaking_f{floor}"] = sum(part["leaking"] for part in found) + own["leaking"]
        out[f"moment_coarser_f{floor}"] = sum(part.get("coarser", 0) for part in found)
        out[f"moment_loader_refused_f{floor}"] = sum(part.get("loader_refused", 0) for part in found)
        mutants = [
            shares(floor, largest, drop="ones")["leaking"],
            shares(floor, largest, drop="absent")["leaking"],
            shares(floor, largest, chain_moments.KIND_NUMBER, drop="readings")["leaking"],
            shares(floor, largest, drop="W1", small=frozenset({0}), counts=w1_counts(floor))["leaking"],
            pairs(floor, 2 * floor + 2, drop="outside")["leaking"],
            pairs(floor, 2 * floor + 2, drop="neither")["leaking"],
        ]
        out[f"moment_mutants_f{floor}"] = len(mutants)
        out[f"moment_mutants_leaking_f{floor}"] = len([found_ for found_ in mutants if found_ > 0])
    return out


def coded(table: object, document: "dict[str, object]", statistical: "dict[str, object]", floor: int) -> "tuple[list[tuple[str, str, list[object]]], list[tuple[str, list[int], list[int], set[int], list[int]]]]":
    """Each eligible column's rows read as the chain reads them (its ladder from the description, its cells through
    `chain.read_column`): the moment columns' codes (None where a row holds no reading) and every column's `L1`
    bands with their published totals, the bands holding an own-fact group and each band's `L2` band, in the reference's form
    (`tools/reference/moment_rule_b.py`'s `describe`). The table has no records holding nothing."""
    settings = taxonomy.Settings(small_cell_floor=floor)
    blocks = {f"{block['name']}": block for block in document["columns"]}  # type: ignore[index, union-attr, attr-defined]
    names = [f"{block['name']}" for block in document["columns"]]  # type: ignore[index, union-attr, attr-defined]
    rows = table.n_rows  # type: ignore[attr-defined]
    # Which `L2` the description was cut under, read from its own record as
    # the loader reads it (S24; RULE ONE_BAND, lane CHa2, plan P4-D451).
    one_band = chain_rules.reads_one_band(statistical["procedure"], rows)
    assert one_band is not None, "the description's procedure record is of neither version"
    columns: "list[tuple[str, str, list[object]]]" = []
    groupings: "list[tuple[str, list[int], list[int], set[int], list[int]]]" = []
    for entry in statistical["ladder"]:  # type: ignore[attr-defined]
        name = entry["column"]
        block = blocks[name]
        scale, _start = chain_check._ladder_of(entry, block, floor, rows, 0, one_band)
        read = chain.read_column(table, names.index(name), block, settings, DECLARED, "", 0)  # type: ignore[arg-type]
        assert read is not None
        to_l0: "dict[object, int]" = {}
        for at in range(len(scale.l0)):
            for one in scale.l0[at]:
                to_l0[one] = at
        l0 = [to_l0[read.start.names[code]] for code in read.codes]
        l1 = [scale.maps[1][band] for band in l0]
        small_l0 = chain_rules.small_group_bands(block, read.start, scale, floor) | chain.value_run_bands(
            block, read.start, scale, floor, read.readings
        )
        groupings += [(name, l1, chain_rules.totals_at(scale, 1), {scale.maps[1][band] for band in small_l0}, chain_rules.coarsen(scale, 1, 2))]
        if block["role"] in chain_rules.NUMBER_ROLES and read.linear is not None and chain_moments.fine(block):
            linear = read.linear
            columns += [(name, chain_moments.KIND_NUMBER, [linear[r] if read.has_reading[r] else None for r in range(rows)])]
        elif block["role"] == chain_rules.ROLE_BINARY and chain_moments.binary_levels(scale) is not None:
            levels = chain_moments.binary_levels(scale)
            assert levels is not None
            columns += [(name, chain_moments.KIND_BINARY, [1 if b == levels[1] else 0 if b == levels[0] else None for b in l0])]
    return columns, groupings


# -- THE ROUND TRIP: EVERY DESCRIPTION THE PRODUCT WRITES, ITS LOADER READS -----
#
# LANE MPp RULINGS 5 (1): random tables of codes 0 to 255 (bands of 11 to 40
# readings, complete and blank-bearing columns, extreme spreads, both pair
# orders) through `chain_moments.released`, each object read back by the
# loader's own `chain_check.check_moments` against blocks and a ladder a column
# that state what the object assumes (a number's readings, a binary's levels, a
# grouping's totals at each level and its own-fact bands). The hole it
# closes: the product equalled the reference while its loader refused it.

RUNGS = {"p01": 1.0, "p05": 5.0, "p10": 10.0, "p25": 25.0, "p50": 50.0, "p75": 75.0, "p90": 90.0, "p95": 95.0, "p99": 99.0}


def number_block(name: str, n: int) -> "dict[str, object]":
    """A FINE number's block as the loader reads it: its role, its `n` readings, its rungs and more than 20 different readings."""
    return {"name": name, "role": chain_rules.ROLE_CONTINUOUS, "n_used_in_statistics": n, "n_distinct_values": 21 if n != 21 else 22, "percentiles": dict(RUNGS)}


def binary_ladder(name: str, zeros: int, ones: int, absent: int) -> "chain_rules.Ladder":
    """A binary's ladder: its two levels, each one published band, and its rows without a reading."""
    l0 = ((("0",),), (("1",),), (chain_rules.MISSING,))
    same = (0, 1, 2)
    return chain_rules.Ladder(name, l0, (same, same, same), (3, 3, 3), (zeros, ones, absent), (False, False, False))


def grouping_ladder(name: str, totals: "tuple[int, ...]", coarsest: "tuple[int, ...]") -> "chain_rules.Ladder":
    """A grouping column's ladder: its `L1` bands as its `L0` bands, and the `L2` band holding each."""
    same = tuple(range(len(totals)))
    l0 = tuple(((f"b{band}",),) for band in same)
    counts = (len(totals), len(totals), max(coarsest) + 1)
    return chain_rules.Ladder(name, l0, (same, same, tuple(coarsest)), counts, tuple(totals), tuple(True for _band in same))


def loader_inputs(
    columns: "list[chain_moments.Released]", groupings: "list[chain_moments.Grouping]"
) -> "tuple[dict[str, dict[str, object]], list[str], dict[str, chain_rules.Ladder], int, dict[str, set[int]]]":
    """What `chain_check.check_moments` reads beside the object: the blocks, the eligible columns in schema order (the
    moment columns, then the groupings), a ladder for each, the tabled rows and each grouping's own-fact bands."""
    blocks: "dict[str, dict[str, object]]" = {}
    scales: "dict[str, chain_rules.Ladder]" = {}
    small: "dict[str, set[int]]" = {}
    for column in columns:
        n = sum(column.present)
        if column.kind == chain_moments.KIND_NUMBER:
            blocks[column.name] = number_block(column.name, n)
            continue
        ones = sum(value for value, has in zip(column.values, column.present) if has)
        blocks[column.name] = {"name": column.name, "role": chain_rules.ROLE_BINARY}
        scales[column.name] = binary_ladder(column.name, n - ones, ones, len(column.present) - n)
        small[column.name] = set()
    for grouping in groupings:
        blocks[grouping.name] = {"name": grouping.name, "role": "categorical"}
        scales[grouping.name] = grouping_ladder(grouping.name, grouping.totals, grouping.coarsest)
        small[grouping.name] = set(grouping.small)
    eligible = [column.name for column in columns] + [grouping.name for grouping in groupings]
    return blocks, eligible, scales, len(columns[0].present), small


def _drawn_codes(draw: random.Random, shape: str, rows: int) -> "list[int]":
    """One number's codes: spread over the code, at its two ends only, or bunched."""
    if shape == "ends":
        return [255 * draw.randrange(2) for _row in range(rows)]
    if shape == "bunched":
        middle = draw.randrange(20, 236)
        return [min(255, max(0, middle + draw.randint(-12, 12))) for _row in range(rows)]
    return [draw.randrange(256) for _row in range(rows)]


def random_table(seed: int) -> "tuple[list[chain_moments.Released], list[chain_moments.Grouping]]":
    """One seeded random table: a grouping of 2 to 4 bands of 11 to 40 rows (a second grouping shuffled across them),
    2 to 4 numbers and 0 to 2 binaries, each complete, blank on 1 to 10 rows, or blank on many."""
    draw = random.Random(seed)
    sizes = [draw.randint(11, 40) for _band in range(draw.randint(2, 4))]
    rows = sum(sizes)
    first = [band for band in range(len(sizes)) for _row in range(sizes[band])]
    order = list(range(rows))
    draw.shuffle(order)
    second = [0] * rows
    band = start = 0
    while start < rows:
        width = draw.randint(11, 40)
        if rows - start - width < 11:
            width = rows - start
        for place in order[start : start + width]:
            second[place] = band
        start += width
        band += 1
    groupings: "list[chain_moments.Grouping]" = []
    for name, bands in (("g1", first), ("g2", second)):
        count = max(bands) + 1
        totals = tuple(bands.count(at) for at in range(count))
        coarsest = tuple(at // 2 for at in range(count)) if draw.random() < 0.5 else tuple(range(count))
        small = frozenset(at for at in range(count) if draw.random() < 0.2)
        groupings += [chain_moments.Grouping(name, bytes(bands), totals, small, coarsest)]
    columns: "list[chain_moments.Released]" = []
    for place in range(draw.randint(2, 4)):
        codes = _drawn_codes(draw, draw.choice(["spread", "spread", "ends", "bunched"]), rows)
        present = bytearray([1] * rows)
        blanks = draw.choice([0, 0, draw.randint(1, 10), draw.randint(11, max(11, rows // 3))])
        for row in draw.sample(range(rows), min(blanks, rows - 2)):
            present[row] = 0
            codes[row] = 0
        columns += [chain_moments.Released(f"x{place}", chain_moments.KIND_NUMBER, bytes(codes), present)]
    for place in range(draw.randint(0, 2)):
        share = draw.random()
        values = [1 if draw.random() < share else 0 for _row in range(rows)]
        present = bytearray([1] * rows)
        for row in draw.sample(range(rows), draw.choice([0, 0, draw.randint(11, max(11, rows // 4))])):
            present[row] = 0
            values[row] = 0
        columns += [chain_moments.Released(f"y{place}", chain_moments.KIND_BINARY, bytes(values), present)]
    return columns, groupings


def round_trip(tables: int, floor: int = 11, first_seed: int = 0) -> "dict[str, object]":
    """`tables` seeded random tables through the product and back through its loader: those publishing moments, those
    the loader refuses (with the first refusal's words), and the pairs and bands each kind published."""
    published = refused = pairs = spreads = bands = ends = 0
    first_refusal = ""
    for seed in range(first_seed, first_seed + tables):
        columns, groupings = random_table(seed)
        moments, _counts = chain_moments.released(columns, groupings, floor)
        if moments is None:
            continue
        published += 1
        for line in moments["correlations"]:  # type: ignore[union-attr]
            for pair in line:
                pairs += 1 if pair is not None else 0
                spreads += 1 if pair is not None and len(pair) == 3 else 0
        for entry in moments["within"]:  # type: ignore[union-attr]
            for group in entry["groups"]:
                bands += 1 if group[0] else 0
                ends += 1 if len(group) == 3 and group[2] > 128 * chain_moments.SCALE_SPREAD else 0
        blocks, eligible, scales, tabled, small = loader_inputs(columns, groupings)
        try:
            chain_check.check_moments(moments, blocks, eligible, scales, floor, tabled, small)
        except errors.ProfileError as refusal:
            refused += 1
            first_refusal = first_refusal or f"seed {seed}: {refusal}"
    return {
        "tables": tables,
        "published": published,
        "refused": refused,
        "first_refusal": first_refusal,
        "pairs": pairs,
        "pairs_with_spreads": spreads,
        "bands": bands,
        "band_spreads_past_128": ends,
    }
