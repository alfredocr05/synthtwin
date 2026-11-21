"""The audited array helper against its as-built references, byte for byte (lane ARR-a, plan P4-D466).

`synthtwin.arrays` holds the polish's row passes (method G16.3) as numpy
array operations under the run-time checks of plan P4-D409 part 3 (e).
Its one promise is G1's: the bytes the plain loops give. Every function
is held here to lane MPg's loops at aea59493, frozen in
tests/arrays_as_built.py, on vectors from fixed seeds at 1,000 and
200,000 rows (a third of the scores tied, both zeros, subnormals,
magnitudes to 1e300, a band holding no row, one band holding every row,
keys 2 ** 32 apart and a key bound past 2 ** 63, and 0, 1 and 2 rows),
on numpy's path and on the plain-Python path; `exact_sum` against
`math.fsum` on 10,000 random multisets; the boundary list of P4-D409
part 3 (e); the types every output holds (a numpy scalar would print
differently); and the product mutants, each red. Machine-free: nothing
is timed here (the CPU seconds are measured in the lane's notes).
"""

import functools
import inspect
import math
import random
import struct
import warnings

import numpy
import pytest

import arrays_as_built as built
from synthtwin import arrays

SIZES = (1000, 200_000)


# -- vectors from fixed seeds ---------------------------------------------


def _mask(rng, rows, share):
    """A byte a row: 1 with probability `share`, else 0."""
    return bytearray(1 if rng.random() < share else 0 for _row in range(rows))


def _floats_bytes(values):
    return struct.pack("<%dd" % len(values), *values)


def _float_list(data):
    return list(struct.unpack("<%dd" % (len(data) // 8), bytes(data)))


def _bits(value):
    return struct.unpack("<q", struct.pack("<d", value))[0]


# The largest magnitudes a vector carries: to 1e300 (numpy's path of the
# moves is not taken at 2 ** 500 and above, about 3.27e150, so those
# vectors hold the plain path to the reference), and to 1e150 (below
# it, so numpy's path is held to the reference on the same shape).
HUGE = (1e300, -1e300, 3.5e299)
BELOW_2_500 = (1e150, -1e150, 3.5e149)


def _special_scores(rng, rows, large=HUGE):
    """A third of the scores tied, both zeros, subnormals and magnitudes to 1e300 (or `large`), the rest spread."""
    tied = [rng.choice((0.25, -1.5, 3.0)) for _k in range(5)]
    out = []
    for row in range(rows):
        pick = rng.random()
        if pick < 0.33:
            out += [rng.choice(tied)]
        elif pick < 0.38:
            out += [rng.choice((0.0, -0.0))]
        elif pick < 0.41:
            out += [rng.choice((5e-324, -5e-324, 2.2250738585072014e-308, -1e-310))]
        elif pick < 0.412 and row % 97 == 0:
            out += [rng.choice(large)]
        else:
            out += [rng.gauss(0.0, 1.0)]
    return out


@functools.lru_cache(maxsize=None)
def _column(rows, seed=7):
    """One polished column's state, as the polish holds it: codes, readings, ranks, bands and its partners."""
    rng = random.Random(seed * 1_000_003 + rows)
    own = bytearray(rng.randrange(256) for _row in range(rows))
    present = _mask(rng, rows, 0.8)
    partner = bytearray(rng.randrange(256) for _row in range(rows))
    both = _mask(rng, rows, 0.7)
    ranks = bytearray(rng.randrange(256) for _row in range(2 * rows))
    # Eight bands, the fourth holding no row (and the eighth none here, a
    # test fills it), codes at and past the encoding's end left out as
    # the polish leaves them.
    of_row = bytearray(rng.choice((0, 1, 2, 4, 5, 6, 9, 200)) for _row in range(rows))
    wide_bands = [rng.randrange(300) for _row in range(rows)]
    sums = [rng.randrange(12 * 65535 + 1) for _row in range(rows)]
    return {
        "own": own,
        "present": present,
        "partner": partner,
        "both": both,
        "ranks": ranks,
        "of_row": of_row,
        "wide_bands": wide_bands,
        "sums": sums,
        "sums_store": built.packed_store(sums, 3),
    }


@functools.lru_cache(maxsize=None)
def _normal():
    rng = random.Random(11)
    return [rng.gauss(0.0, 1.0) for _k in range(65536)]


def _table(centre, spread):
    return [(code - centre) / spread for code in range(256)]


# -- the adjust step's sums: counts and an exact sum rounded once -----------


@pytest.mark.parametrize("rows", SIZES)
def test_the_pair_sums_are_the_polish_s_sums(rows):
    """n, sx, sxx, sy, syy and sxy of a pair: ONE joint count and exact sums, equal to the five math.fsum passes."""
    state = _column(rows)
    table = _table(127.3, 51.9)
    other = _table(80.1, 33.7)
    own, present, partner, both = state["own"], state["present"], state["partner"], state["both"]
    expected = built.pair_sums(own, present, partner, both, table, other)
    own_counts = arrays.code_counts(own, present, both, 256)
    partner_counts = arrays.code_counts(partner, present, both, 256)
    joint = arrays.joint_counts(own, partner, 256, 256, present, both)
    got = (
        sum(own_counts),
        arrays.exact_sum(own_counts, table),
        arrays.exact_sum(own_counts, [value * value for value in table]),
        arrays.exact_sum(partner_counts, other),
        arrays.exact_sum(partner_counts, [value * value for value in other]),
        arrays.exact_sum(joint, [table[a] * other[b] for a in range(256) for b in range(256)]),
    )
    assert got[0] == expected[0]
    assert [_bits(value) for value in got[1:]] == [_bits(value) for value in expected[1:]]
    # The joint count's margins are the two counts (no row lost by the joint code).
    assert [sum(joint[256 * a:256 * a + 256]) for a in range(256)] == own_counts


@pytest.mark.parametrize("rows", SIZES)
def test_the_by_and_grouping_sums_are_the_polish_s_sums(rows):
    state = _column(rows)
    number = _table(101.0, 47.25)
    table = _table(127.3, 51.9)
    encoding = [-1.25, 0.5, 2.0, 0.0, -0.75, 1.5, -2.5, 0.125]
    own, present, of_row = state["own"], state["present"], state["of_row"]
    holding = state["both"]
    m, sx, sy, sxy = built.by_sums(state["partner"], holding, number, of_row, encoding)
    counts = arrays.code_counts(state["partner"], holding, None, 256)
    band_counts = arrays.code_counts(of_row, holding, None, len(encoding))
    joint = arrays.joint_counts(state["partner"], of_row, 256, len(encoding), holding, None)
    products = [number[a] * encoding[b] for a in range(256) for b in range(len(encoding))]
    assert sum(counts) == m
    assert _bits(arrays.exact_sum(counts, number)) == _bits(sx)
    assert _bits(arrays.exact_sum(band_counts, encoding)) == _bits(sy)
    assert _bits(arrays.exact_sum(joint, products)) == _bits(sxy)
    whole_x, sy, sxy = built.grouping_sums(own, present, table, of_row, encoding)
    assert _bits(arrays.exact_sum(arrays.code_counts(own, present, None, 256), table)) == _bits(whole_x)
    assert _bits(arrays.exact_sum(arrays.code_counts(of_row, present, None, len(encoding)), encoding)) == _bits(sy)
    joint = arrays.joint_counts(own, of_row, 256, len(encoding), present, None)
    products = [table[a] * encoding[b] for a in range(256) for b in range(len(encoding))]
    assert _bits(arrays.exact_sum(joint, products)) == _bits(sxy)


@pytest.mark.parametrize("rows", SIZES)
def test_the_spread_factors_whole_numbers_are_the_polish_s(rows):
    """Codes squared as whole numbers (a code of 255 squared is 65,025: never a byte's square)."""
    state = _column(rows)
    own, present, both, of_row = state["own"], state["present"], state["both"], state["of_row"]
    counts = arrays.code_counts(own, present, both, 256)
    held, total, squares = built.pair_spread_sums(own, present, both)
    assert sum(counts) == held
    assert sum(code * counts[code] for code in range(256)) == total
    assert sum(code * code * counts[code] for code in range(256)) == squares
    bands = 8
    joint = arrays.joint_counts(of_row, own, bands, 256, present, None)
    held, totals, squares = built.within_spread_sums(own, present, of_row, bands)
    for band in range(bands):
        cells = joint[256 * band:256 * band + 256]
        assert sum(cells) == held[band]
        assert sum(code * cells[code] for code in range(256)) == totals[band]
        assert sum(code * code * cells[code] for code in range(256)) == squares[band]


def test_a_list_of_bands_past_a_byte_counts_as_the_polish_reads_it():
    state = _column(1000)
    wide = state["wide_bands"]
    counted = arrays.code_counts(wide, state["present"], None, 280)
    expected = [0 for _band in range(280)]
    for row in range(1000):
        if state["present"][row] and wide[row] < 280:
            expected[wide[row]] = expected[wide[row]] + 1
    assert counted == expected


# -- exact_sum is math.fsum's value -------------------------------------------


def _multiset(rng, bins):
    values = []
    for _bin in range(bins):
        pick = rng.random()
        if pick < 0.1:
            values += [rng.choice((0.0, -0.0))]
        elif pick < 0.15:
            values += [rng.choice((5e-324, -5e-324, 1e-310, -2.2250738585072014e-308))]
        else:
            values += [math.ldexp(rng.uniform(-1.0, 1.0), rng.randrange(-1000, 1000))]
    counts = [rng.randrange(6) for _bin in range(bins)]
    if rng.random() < 0.3 and bins >= 2:
        # Cancellation to zero: a value and its negation, the same count.
        values[1] = -values[0]
        counts[1] = counts[0]
        for other in range(2, bins):
            counts[other] = 0
    return counts, values


def test_exact_sum_is_math_fsum_on_ten_thousand_multisets():
    rng = random.Random(20261105)
    for trial in range(10_000):
        bins = 1 if trial % 10 == 0 else rng.randrange(1, 24)
        counts, values = _multiset(rng, bins)
        expanded = [values[at] for at in range(bins) for _k in range(counts[at])]
        assert _bits(arrays.exact_sum(counts, values)) == _bits(math.fsum(expanded)), (counts, values)


def test_exact_sum_on_65536_bins_and_the_signs_of_a_zero_sum():
    rng = random.Random(3)
    values = [math.ldexp(rng.uniform(-1.0, 1.0), rng.randrange(-60, 60)) for _bin in range(65536)]
    counts = [rng.randrange(4) for _bin in range(65536)]
    expanded = [values[at] for at in range(65536) for _k in range(counts[at])]
    assert _bits(arrays.exact_sum(counts, values)) == _bits(math.fsum(expanded))
    for counts, values in (
        ([1], [-0.0]),
        ([2], [-0.0]),
        ([1, 1], [0.0, -0.0]),
        ([1, 1], [1.0, -1.0]),
        ([0], [5.0]),
        ([], []),
        ([5, 1], [-0.0, 0.0]),
        ([2, 1, 3], [1.0, -2.0, -0.0]),
        ([1, 1, 1], [1e16, 1.0, -1e16]),
    ):
        expanded = [values[at] for at in range(len(values)) for _k in range(counts[at])]
        assert _bits(arrays.exact_sum(counts, values)) == _bits(math.fsum(expanded)), (counts, values)


def test_exact_sum_where_math_fsum_overflows_on_the_way():
    """math.fsum raises on an intermediate overflow whose exact sum is finite; exact_sum gives that sum rounded once (the oracle's fsum)."""
    with pytest.raises(OverflowError):
        math.fsum([1e308, 1e308, -1e308])
    assert arrays.exact_sum([1, 1, 1], [1e308, 1e308, -1e308]) == 1e308


def test_exact_sum_refuses_what_math_fsum_would_not_sum_exactly():
    with pytest.raises(ValueError):
        arrays.exact_sum([1], [math.inf])
    with pytest.raises(ValueError):
        arrays.exact_sum([1], [math.nan])
    with pytest.raises(ValueError):
        arrays.exact_sum([-1], [1.0])
    with pytest.raises(ValueError):
        arrays.exact_sum([1, 2], [1.0])
    with pytest.raises(OverflowError):
        arrays.exact_sum([2], [1.7e308])


# -- the score build ------------------------------------------------------------


def _partners(rows, state, rng):
    partners = []
    for j in range(24):
        weight = rng.choice((0.0, -0.0)) if j == 5 else rng.uniform(-2.0, 2.0)
        if j % 2 == 0:
            has = _mask(rng, rows, 0.75)
            partners += [("rank", weight, bytes(state["ranks"]), has)]
        elif j == 23:
            encoding = [rng.uniform(-3.0, 3.0) for _band in range(280)]
            partners += [("band", weight, state["wide_bands"], encoding)]
        elif j == 21:
            partners += [("band", weight, state["of_row"], [])]
        else:
            encoding = [rng.uniform(-3.0, 3.0) for _band in range(8)]
            partners += [("band", weight, bytes(state["of_row"]), encoding)]
    return partners


@pytest.mark.parametrize("rows", SIZES)
def test_the_scores_are_the_polish_s_scores(rows):
    state = _column(rows)
    rng = random.Random(rows)
    partners = _partners(rows, state, rng)
    noise = 0.37
    expected = built.scores(state["present"], partners, _normal(), noise, state["sums"])
    out = bytearray(8 * rows)
    arrays.score_rows(state["present"], partners, _normal(), noise, state["sums_store"], out)
    assert bytes(out) == _floats_bytes(expected)


def test_the_score_refuses_a_rank_code_past_the_normal_scores():
    present = bytearray([1, 1])
    out = bytearray(16)
    partner = ("rank", 1.0, bytes([5, 0, 0, 0]), bytearray([1, 0]))
    with pytest.raises(ValueError):
        arrays.score_rows(present, [partner], [0.5, 0.25], 0.1, bytes(6), out)
    with pytest.raises(ValueError):
        arrays.score_rows(present, [("rank", math.inf, bytes(4), bytearray(2))], _normal(), 0.1, bytes(6), out)


# -- the two spread moves: Python's running sums ----------------------------------


@pytest.mark.parametrize(
    "rows, large", [(1000, BELOW_2_500), (200_000, BELOW_2_500), (1000, HUGE)], ids=["1000", "200000", "1000-1e300"]
)
def test_the_band_means_and_moves_are_the_polish_s(rows, large):
    state = _column(rows)
    rng = random.Random(rows + 1)
    score = _special_scores(rng, rows, large)
    # One band whose every held score is -0.0: its running total is 0.0,
    # the sum from the leading 0.0 (a sum started at its first value
    # would keep -0.0).
    of_row = bytearray(state["of_row"])
    for row in range(0, rows, 11):
        of_row[row] = 7
        score[row] = -0.0
    scales = [0.5, 1.25, 2.0, 1.0, 0.75, 3.5, 0.25, 1.5]
    expected = list(score)
    totals, counts, means = built.within_move(expected, state["present"], of_row, scales)
    store = bytearray(_floats_bytes(score))
    got_totals, got_counts = arrays.running_totals(store, state["present"], None, of_row, len(scales))
    assert got_counts == counts
    assert [_bits(value) for value in got_totals] == [_bits(value) for value in totals]
    assert _bits(got_totals[7]) == _bits(0.0)
    got_means = [got_totals[band] / got_counts[band] if got_counts[band] else 0.0 for band in range(len(scales))]
    assert [_bits(value) for value in got_means] == [_bits(value) for value in means]
    arrays.move_from_means(store, state["present"], None, of_row, got_means, scales)
    assert bytes(store) == _floats_bytes(expected)


@pytest.mark.parametrize(
    "rows, large", [(1000, BELOW_2_500), (200_000, BELOW_2_500), (1000, HUGE)], ids=["1000", "200000", "1000-1e300"]
)
def test_the_pair_s_own_spread_is_the_polish_s(rows, large):
    state = _column(rows)
    rng = random.Random(rows + 2)
    score = _special_scores(rng, rows, large)
    expected = list(score)
    pair_total, pair_rows = built.pair_move(expected, state["present"], state["both"], 1.75)
    store = bytearray(_floats_bytes(score))
    totals, counts = arrays.running_totals(store, state["present"], state["both"], None, 1)
    assert counts == [pair_rows]
    assert _bits(totals[0]) == _bits(pair_total)
    arrays.move_from_means(store, state["present"], state["both"], None, [totals[0] / counts[0]], [1.75])
    assert bytes(store) == _floats_bytes(expected)


def test_a_band_holding_every_row_and_one_holding_none():
    rows = 1000
    rng = random.Random(5)
    score = _special_scores(rng, rows)
    every = bytes(rows)
    present = bytes([1]) * rows
    expected = list(score)
    totals, counts, means = built.within_move(expected, present, every, [2.0, 0.5])
    store = bytearray(_floats_bytes(score))
    got = arrays.running_totals(store, present, None, every, 2)
    assert got[1] == counts == [rows, 0]
    assert [_bits(value) for value in got[0]] == [_bits(value) for value in totals]
    arrays.move_from_means(store, present, None, every, means, [2.0, 0.5])
    assert bytes(store) == _floats_bytes(expected)


# -- the counting sorts, the order by score, the write-back -------------------------


def _groups(rng, rows, top):
    return built.packed_store([rng.randrange(top) for _row in range(rows)], 4)


@pytest.mark.parametrize("rows", SIZES)
@pytest.mark.parametrize("group_count", (10, 300))
def test_the_frame_sort_and_the_order_by_score_are_the_polish_s(rows, group_count):
    """Ten groups (each sorted on its own) and three hundred (two stable sorts over every slot): the plain order."""
    state = _column(rows)
    rng = random.Random(rows + 3)
    present = state["present"]
    groups = _groups(rng, rows, group_count)
    count = sum(1 for row in range(rows) if present[row])
    grouped, width, starts, ordered = arrays.rows_by_group(groups, 4, present)
    expected = built.rows_by_group(groups, present, count)
    assert (bytes(grouped), width, starts, ordered) == (bytes(expected[0]), expected[1], expected[2], expected[3])
    score = _special_scores(rng, rows)
    store = _floats_bytes(score)
    got = arrays.order_by_score(grouped, width, starts, store)
    assert built.packed_values(got, width) == built.ordered_rows(grouped, width, starts, score)


@pytest.mark.parametrize("rows", SIZES)
@pytest.mark.parametrize("binary", (False, True))
def test_the_places_and_the_write_back_are_the_polish_s(rows, binary):
    state = _column(rows)
    rng = random.Random(rows + 4 + binary)
    present = state["present"]
    places = rows
    order = list(range(places))
    rng.shuffle(order)
    index_width = 3
    index = built.packed_store(order, index_width)
    groups = _groups(rng, rows, 6)
    slot_codes = bytearray(rng.randrange(2) if binary else rng.randrange(256) for _place in range(places))
    count = sum(1 for row in range(rows) if present[row])
    grouped, width, starts, ordered = arrays.rows_by_group(groups, 4, present)
    got = arrays.places_by_group(groups, 4, present, starts, ordered, index, index_width, slot_codes, binary)
    expected = built.places_by_group(groups, present, starts, ordered, index, index_width, slot_codes, binary)
    assert bytes(got) == bytes(expected)
    score = _special_scores(rng, rows)
    rows_in_order = arrays.order_by_score(grouped, width, starts, _floats_bytes(score))
    slot_rank = bytearray(rng.randrange(256) for _byte in range(2 * places))
    own_h, ranks_h, index_h = bytearray(state["own"]), bytearray(state["ranks"]), bytearray(index)
    own_b, ranks_b, index_b = bytearray(state["own"]), bytearray(state["ranks"]), bytearray(index)
    places_width = built.width_for(max(places - 1, 0))
    arrays.scatter_places(rows_in_order, width, got, places_width, index_h, index_width, own_h, slot_codes, ranks_h, slot_rank)
    built.write_back(
        built.packed_values(rows_in_order, width), got, places_width, index_b, index_width, own_b, slot_codes, ranks_b, slot_rank
    )
    assert (own_h, ranks_h, index_h) == (own_b, ranks_b, index_b)
    assert count == starts[-1]


def test_the_places_take_the_plain_path_where_a_place_repeats():
    """Two held rows naming one place: the plain loop's last write stands."""
    present = bytearray([1, 1, 1, 0])
    groups = built.packed_store([0, 1, 0, 1], 4)
    index = built.packed_store([2, 2, 0, 1], 3)
    slot_codes = bytearray([0, 1, 0, 1])
    grouped, width, starts, ordered = arrays.rows_by_group(groups, 4, present)
    got = arrays.places_by_group(groups, 4, present, starts, ordered, index, 3, slot_codes, False)
    assert bytes(got) == bytes(built.places_by_group(groups, present, starts, ordered, index, 3, slot_codes, False))


@pytest.mark.parametrize("count", (7, 1 << 32, 1 << 62))
def test_the_joint_groups_are_the_polish_s_keys_2_32_apart_and_past_2_63(count):
    """Renumbered by first meeting; with a band count of 2 ** 32 the plain keys stand 2 ** 32 apart, with 2 ** 62 they pass 2 ** 63."""
    rng = random.Random(count % 1000)
    rows = 1000
    found = built.packed_store([rng.randrange(9) for _row in range(rows)], 4)
    bands = bytearray(rng.randrange(5) for _row in range(rows))
    expected = bytearray(found)
    built.joint_groups(expected, bands, count, rows)
    got = bytearray(found)
    arrays.joint_groups(got, 4, bands, count)
    assert got == expected


def test_the_joint_groups_at_200000_rows_and_a_list_of_bands():
    rng = random.Random(9)
    rows = 200_000
    found = built.packed_store([rng.randrange(40) for _row in range(rows)], 4)
    bands = [rng.randrange(300) for _row in range(rows)]
    expected = bytearray(found)
    built.joint_groups(expected, bands, 300, rows)
    got = bytearray(found)
    arrays.joint_groups(got, 4, bands, 300)
    assert got == expected


# -- the draw and the gathers ----------------------------------------------------------


@pytest.mark.parametrize("rows", SIZES)
def test_the_hidden_sums_are_the_walk_s(rows):
    """Each row's twelve 16-bit pieces summed: the draw's words through a `<u2` view, never uint64 arithmetic."""
    words = numpy.random.default_rng(rows).integers(0, 18446744073709551615, size=3 * rows, dtype="uint64", endpoint=True)
    words[0:3] = 18446744073709551615
    words[3:6] = 0
    expected = built.hidden_sums([int(word) for word in words])
    out = bytearray(3 * (rows + 5))
    arrays.hidden_sums(words, out, 5)
    assert built.packed_values(out, 3) == [0] * 5 + expected
    assert expected[0] == 12 * 65535


def test_the_hidden_sums_refuse_what_is_not_three_eight_byte_words_a_row():
    words = numpy.zeros(4, dtype="uint64")
    with pytest.raises(ValueError):
        arrays.hidden_sums(words, bytearray(6), 0)
    narrow = numpy.zeros(6, dtype="uint32")
    with pytest.raises(ValueError):
        arrays.hidden_sums(narrow, bytearray(6), 0)
    with pytest.raises(ValueError):
        arrays.hidden_sums(numpy.zeros(3, dtype="uint64"), bytearray(3), 1)


@pytest.mark.parametrize("rows", SIZES)
def test_the_bands_through_their_places_are_the_polish_s(rows):
    rng = random.Random(rows + 5)
    places = rows + 17
    order = [rng.randrange(places) for _row in range(rows)]
    index = built.packed_store(order, 4)
    slot_l0 = built.packed_store([rng.randrange(40) for _place in range(places)], 2)
    to_level = [rng.randrange(9) for _code in range(40)]
    expected = built.row_bands(index, 4, slot_l0, 2, to_level, rows)
    out = bytearray(rows)
    assert arrays.take_codes(index, 4, slot_l0, 2, to_level, out, 1) is None
    assert list(out) == expected
    assert arrays.take_codes(index, 4, slot_l0, 2, to_level, None, 1) == expected
    ranks = arrays.take_codes(index, 4, bytes(range(256)) * (2 * places // 256 + 1), 1, None, None, 1)
    assert ranks == [(order[row]) % 256 for row in range(rows)]


# -- 0, 1 and 2 rows ---------------------------------------------------------------------


@pytest.mark.parametrize("rows", (0, 1, 2))
def test_every_function_on_no_row_one_row_and_two(rows):
    present = bytearray([1]) * rows
    own = bytearray(range(rows))
    assert arrays.code_counts(own, present, None, 4) == [1 if code < rows else 0 for code in range(4)]
    assert arrays.joint_counts(own, own, 4, 4, present, present) == [
        1 if (cell // 4 == cell % 4 and cell // 4 < rows) else 0 for cell in range(16)
    ]
    out = bytearray(8 * rows)
    arrays.score_rows(present, [], [0.5], 0.25, bytes(3 * rows), out)
    assert _float_list(out) == built.scores(present, [], [0.5], 0.25, [0] * rows)
    store = bytearray(_floats_bytes([1.5 * row - 0.0 for row in range(rows)]))
    assert arrays.running_totals(store, present, None, None, 1)[1] == [rows]
    arrays.move_from_means(store, present, None, None, [0.5], [2.0])
    groups = bytes(4 * rows)
    grouped, width, starts, ordered = arrays.rows_by_group(groups, 4, present)
    assert starts == ([0, rows] if rows else [0]) and ordered == ([0] if rows else [])
    places = arrays.places_by_group(groups, 4, present, starts, ordered, bytes(range(rows)), 1, bytes(rows), False)
    assert built.packed_values(places, 1) == list(range(rows))
    if rows:
        got = arrays.order_by_score(grouped, width, starts, bytes(store))
        assert built.packed_values(got, width) == built.ordered_rows(grouped, width, starts, _float_list(store))
    found = bytearray(4 * rows)
    arrays.joint_groups(found, 4, bytes(rows), 3)
    assert found == bytes(4 * rows)
    arrays.hidden_sums(numpy.zeros(3 * rows, dtype="uint64"), bytearray(3 * rows), 0)
    assert arrays.take_codes(bytes(rows), 1, bytes([7]), 1, None, None, 1) == [7] * rows


# -- the plain-Python path ------------------------------------------------------------------


def test_the_plain_python_path_gives_the_same_bytes(monkeypatch):
    """A big-endian computer takes the plain loops: the bytes are the same."""
    state = _column(1000)
    rng = random.Random(41)
    partners = _partners(1000, state, rng)
    score = _special_scores(rng, 1000)
    groups = _groups(rng, 1000, 7)
    index = built.packed_store(rng.sample(range(1000), 1000), 3)
    slot_codes = bytearray(rng.randrange(2) for _place in range(1000))
    words = numpy.random.default_rng(1).integers(0, 18446744073709551615, size=3000, dtype="uint64", endpoint=True)

    def results():
        out = bytearray(8000)
        arrays.score_rows(state["present"], partners, _normal(), 0.5, state["sums_store"], out)
        store = bytearray(_floats_bytes(score))
        totals = arrays.running_totals(store, state["present"], None, state["of_row"], 8)
        arrays.move_from_means(store, state["present"], None, state["of_row"], [0.5] * 8, [1.5] * 8)
        grouped, width, starts, ordered = arrays.rows_by_group(groups, 4, state["present"])
        places = arrays.places_by_group(groups, 4, state["present"], starts, ordered, index, 3, slot_codes, True)
        ranked = arrays.order_by_score(grouped, width, starts, bytes(store))
        own, index_out = bytearray(state["own"]), bytearray(index)
        arrays.scatter_places(ranked, width, places, 2, index_out, 3, own, slot_codes, None, None)
        found = bytearray(groups)
        arrays.joint_groups(found, 4, state["of_row"], 300)
        sums = bytearray(3000)
        arrays.hidden_sums(words, sums, 0)
        return (
            bytes(out),
            totals,
            bytes(store),
            bytes(grouped),
            starts,
            ordered,
            bytes(places),
            bytes(ranked),
            bytes(own),
            bytes(index_out),
            bytes(found),
            bytes(sums),
            arrays.code_counts(state["own"], state["present"], state["both"], 256),
            arrays.joint_counts(state["own"], state["of_row"], 256, 8, state["present"], None),
            arrays.take_codes(index, 3, bytes(range(256)) * 4, 1, None, None, 1),
        )

    fast = results()
    monkeypatch.setattr(arrays.sys, "byteorder", "big")
    assert not arrays._fast()
    plain = results()
    assert plain == fast


# -- the boundary list of P4-D409 part 3 (e) ---------------------------------------------------


def test_the_boundaries_are_refused_or_python_s_bytes():
    """Each boundary of P4-D409 part 3 (e), refused or Python's bytes.

    - an int64 product past 2 ** 63: a joint code past 65,536 cells is
      refused, and a whole number past int64 does not enter;
    - a sum past 2 ** 63: an eight-byte store is refused (seven bytes,
      below 2 ** 56, is the widest read), and so is a count of bins at
      2 ** 62;
    - a uint8 square: codes are widened before any operator (the spread
      factors' squares above are Python's), here a byte shifted left;
    - uint64 beside int64: the draw's words at 2 ** 64 - 1 are summed
      through a `<u2` view (test_the_hidden_sums_are_the_walk_s);
    - an int64 / above 2 ** 53: no whole number past 2 ** 53 becomes a
      float (refused), and the hidden score divides a number below 2 **
      20 by 65,536, exactly;
    - a zero divisor and -2 ** 63 // -1: `//` and `%` are refused names
      on an array (tests/test_offline_scan.py), and the helper divides
      by nothing but the constant 65,536;
    - 1 << 63: a store's bytes are put together by shifts of eight from
      below 2 ** 56; a value that does not fit its store is refused;
    - a shift by 64: refused by the audit (a literal from 0 to 63);
    - ~ on unsigned storage: no `~` is written in the helper at all.
    """
    with pytest.raises(ValueError):
        arrays.joint_counts(bytes(4), bytes(4), 257, 256, None, None)
    with pytest.raises(OverflowError):
        arrays.code_counts([1 << 63], None, None, 4)
    with pytest.raises(ValueError):
        arrays.take_codes(bytes(8), 8, bytes(8), 1, None, None, 1)
    with pytest.raises(ValueError):
        arrays.code_counts(bytes(4), None, None, 1 << 62)
    assert built.packed_values(arrays._wide(bytes([255]) * 7, 7), 8) == [(1 << 56) - 1]
    assert built.packed_values(arrays._wide(bytes([255, 255, 255]), 3), 8) == [(1 << 24) - 1]
    with pytest.raises(ValueError):
        arrays.score_rows(bytearray(1), [("band", 1.0, [0], [(1 << 54) | 1])], [0.0], 0.0, bytes(3), bytearray(8))
    with pytest.raises(ValueError):
        arrays._packed(arrays._wide(bytes([0, 0, 0, 1]), 4), 3)
    source = inspect.getsource(arrays)
    code_lines = [line.split("#", 1)[0] for line in source.splitlines()]
    assert not any("~" in line for line in code_lines), "the helper writes no ~"
    assert not any("//" in line or "%" in line or "**" in line for line in code_lines if "numpy" in line)


# -- lane ARR-a's repair (LANE ARR RULINGS 4): the two fallbacks, the checks on both paths, nothing printed --------
#
# Each case runs on numpy's path and on the plain-Python path (a big-endian
# computer, sys.byteorder set to "big"), and each is red on a mutant that
# removes the check or the fallback it pins (the lane's notes,
# wave6/ARR-a/repair1/).


def _on(path, monkeypatch):
    """Take numpy's path ("numpy") or the plain-Python path ("plain")."""
    if path == "plain":
        monkeypatch.setattr(arrays.sys, "byteorder", "big")
    assert arrays._fast() == (path == "numpy")


PATHS = ("numpy", "plain")


@pytest.mark.parametrize("path", PATHS)
def test_a_band_at_or_past_the_count_keeps_the_plain_loop_s_numbers(path, monkeypatch):
    """Groups 0, 1, 0 beside bands 3, 0, 0 at a count of 3: the plain keys 3, 3 and 0 number the rows 0, 0, 1 (two pairs share a key); two stable sorts would number them 0, 1, 2."""
    _on(path, monkeypatch)
    found = built.packed_store([0, 1, 0], 4)
    expected = bytearray(found)
    built.joint_groups(expected, [3, 0, 0], 3, 3)
    assert built.packed_values(expected, 4) == [0, 0, 1]
    got = bytearray(found)
    arrays.joint_groups(got, 4, bytes([3, 0, 0]), 3)
    assert got == expected
    rng = random.Random(23)
    found = built.packed_store([rng.randrange(9) for _row in range(1000)], 4)
    bands = [rng.randrange(7) for _row in range(1000)]
    expected = bytearray(found)
    built.joint_groups(expected, bands, 5, 1000)
    got = bytearray(found)
    arrays.joint_groups(got, 4, bands, 5)
    assert got == expected


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("groups", (1, 65))
def test_a_group_whose_rows_fall_is_ordered_as_the_plain_sort(path, groups, monkeypatch):
    """Rows 2, 0, 1 in one group with tied scores: the plain sort of (score, row) gives 0, 1, 2; a stable sort of the slots by score alone would keep 2, 0, 1."""
    _on(path, monkeypatch)
    rows = [2, 0, 1] + list(range(3, groups + 2))
    starts = [0] + list(range(3, groups + 3))
    grouped = built.packed_store(rows, 1)
    score = [1.0] * len(rows)
    expected = built.ordered_rows(grouped, 1, starts, score)
    assert expected[:3] == [0, 1, 2]
    got = arrays.order_by_score(grouped, 1, starts, _floats_bytes(score))
    assert built.packed_values(got, 1) == expected


@pytest.mark.parametrize("path", PATHS)
def test_many_bands_and_one_holding_only_minus_zero_total_from_the_leading_zero(path, monkeypatch):
    """Seventy bands (the stable sort's path past 64), the last holding only -0.0: its total is 0.0, the sum from the leading 0.0."""
    _on(path, monkeypatch)
    rows = 5000
    rng = random.Random(29)
    score = _special_scores(rng, rows)
    of_row = bytearray(rng.randrange(69) for _row in range(rows))
    for row in range(0, rows, 13):
        of_row[row] = 69
        score[row] = -0.0
    present = _mask(rng, rows, 0.9)
    totals, counts, _means = built.within_move(list(score), present, of_row, [1.0] * 70)
    got_totals, got_counts = arrays.running_totals(_floats_bytes(score), present, None, of_row, 70)
    assert got_counts == counts and counts[69] > 0
    assert [_bits(value) for value in got_totals] == [_bits(value) for value in totals]
    assert _bits(got_totals[69]) == _bits(0.0)


_REFUSED = {
    "an infinity in the normal scores": lambda: arrays.score_rows(bytearray([1]), [], [math.inf], 0.0, bytes(3), bytearray(8)),
    "NaN in the normal scores": lambda: arrays.score_rows(bytearray([1]), [], [math.nan], 0.0, bytes(3), bytearray(8)),
    "an infinity in the means": lambda: arrays.move_from_means(bytearray(8), None, None, None, [math.inf], [1.0]),
    "NaN in the means": lambda: arrays.move_from_means(bytearray(8), None, None, None, [math.nan], [1.0]),
    "an infinity in an encoding": lambda: arrays.score_rows(
        bytearray([1]), [("band", 1.0, bytes(1), [0.5, math.inf])], [0.5], 0.0, bytes(3), bytearray(8)
    ),
    "NaN in an encoding": lambda: arrays.score_rows(
        bytearray([1]), [("band", 1.0, bytes(1), [0.5, math.nan])], [0.5], 0.0, bytes(3), bytearray(8)
    ),
    "an infinite score summed": lambda: arrays.running_totals(_floats_bytes([1.0, -math.inf]), None, None, None, 1),
    "an infinite score moved": lambda: arrays.move_from_means(bytearray(_floats_bytes([math.inf, 1.0])), None, None, None, [0.0], [1.0]),
    "an infinite score ordered": lambda: arrays.order_by_score(bytes([0, 1]), 1, [0, 2], _floats_bytes([1.0, math.inf])),
    "1.5 in a list of codes": lambda: arrays.code_counts([1, 1.5, 2], None, None, 4),
    "1.5 in a list of bands": lambda: arrays.running_totals(_floats_bytes([1.0, 2.0]), None, None, [0, 1.5], 2),
    "-1 in a list of bands summed": lambda: arrays.running_totals(_floats_bytes([1.0, 2.0]), None, None, [0, -1], 2),
    "-1 in a list of bands moved": lambda: arrays.move_from_means(bytearray(16), None, None, [0, -1], [0.5, 0.25], [2.0, 3.0]),
    "-1 in a list of a partner's bands": lambda: arrays.score_rows(
        bytearray([1, 1]), [("band", 1.0, [0, -1], [0.5, 0.25])], [0.5], 0.0, bytes(6), bytearray(16)
    ),
    "-1 in a list of joint bands": lambda: arrays.joint_groups(bytearray(8), 4, [0, -1], 2),
}


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("case", sorted(_REFUSED))
def test_an_infinity_nan_a_fraction_or_a_negative_band_is_refused_on_both_paths(case, path, monkeypatch):
    _on(path, monkeypatch)
    with pytest.raises(ValueError):
        _REFUSED[case]()


_MALFORMED = {
    "a tuple as the encoding": lambda: arrays.score_rows(
        bytes([1, 1, 1]), [("band", 1.0, [0, 0, 0], (1.0,))], [0.5], 1.0, bytes(9), bytearray(24)
    ),
    "rank codes too short": lambda: arrays.score_rows(
        bytes([1, 1, 1]), [("rank", 1.0, bytes(2), bytes(3))], [0.5], 1.0, bytes(9), bytearray(24)
    ),
    "a band list too short": lambda: arrays.score_rows(
        bytes([1, 1, 1]), [("band", 1.0, [0, 0], [1.0])], [0.5], 1.0, bytes(9), bytearray(24)
    ),
    "a rank code past the normal scores": lambda: arrays.score_rows(
        bytes([1, 1, 1]), [("rank", 1.0, bytes([5, 0]) * 3, bytes([1, 1, 1]))], [0.5], 1.0, bytes(9), bytearray(24)
    ),
    "a scatter row past its store": lambda: arrays.scatter_places(
        bytes([9]), 1, bytes([0]), 1, bytearray(3), 1, bytearray(3), bytes([1]), None, None
    ),
    "a take place past its table": lambda: arrays.take_codes(bytes([9, 0]), 1, bytes([1]), 1, None, None, 1),
    "a take code past the mapping": lambda: arrays.take_codes(bytes([0, 0]), 1, bytes([5]), 1, [0, 1], None, 1),
    "a slot's row past the scores": lambda: arrays.order_by_score(bytes([0, 5]), 1, [0, 2], _floats_bytes([1.0, 2.0])),
    "a place past the places": lambda: arrays.places_by_group(
        bytes(4), 4, bytes([1]), [0, 1], [0], bytes([7]), 1, bytes(3), False
    ),
    "a draw of four bytes a word": lambda: arrays.hidden_sums(numpy.zeros(3, dtype="uint32"), bytearray(3), 0),
    # Lane ARR-a's repair 2 (the verify of repair 1, item 1): take_codes' out_width from one to seven.
    "an out_width of eight": lambda: arrays.take_codes(bytes([0, 0]), 1, bytes([1]), 1, None, bytearray(16), 8),
    "an out_width of nought": lambda: arrays.take_codes(bytes([0, 0]), 1, bytes([1]), 1, None, bytearray(0), 0),
    # Lane ARR-a's repair 2 (LANE ARR RULINGS 5 (3), Codex's item 3): a buffer written handed again as one read.
    "Codex's own handed as the places' codes": lambda: (
        lambda own: arrays.scatter_places(bytes([0, 1]), 1, bytes([1, 0]), 1, bytearray(2), 1, own, own, None, None)
    )(bytearray([7, 8])),
    "Codex's rank codes handed as the places' rank codes": lambda: (
        lambda ranks: arrays.scatter_places(
            bytes([0, 1]), 1, bytes([1, 0]), 1, bytearray(2), 1, bytearray(2), bytes([5, 6]), ranks, ranks
        )
    )(bytearray([1, 2, 3, 4])),
    # Lane ARR-a's repair 2 (LANE ARR RULINGS 5 (4), Codex's item 4): a draw of size (3, 1), each entry an array.
    "Codex's draw of three words by one": lambda: arrays.hidden_sums(
        numpy.random.default_rng(1).integers(0, 18446744073709551615, size=(3, 1), dtype="uint64", endpoint=True),
        bytearray(3),
        0,
    ),
    "a fraction among the starts": lambda: arrays.places_by_group(
        b"\0", 1, b"\1", [0, 1.5], [0], b"\0", 1, b"\0", False
    ),
    # Lane ARR-a's repair 2 (LANE ARR RULINGS 5 (4), the lane's own sweep of the same class): a count, a width or
    # a start written as a float failed on the two paths with two different errors.
    "a store's width as a float": lambda: arrays.rows_by_group(bytes([1, 0, 1, 2]), 1.0, bytes([1, 1, 0, 1])),
    "a group width as a float": lambda: arrays.places_by_group(
        bytes([1, 0, 1, 2]), 1.0, bytes([1, 1, 0, 1]), [0, 1, 2, 3], [0, 1, 2], bytes([2, 0, 1, 3]), 1, bytes(4), False
    ),
    "bins as a float": lambda: arrays.code_counts(bytes([0, 1]), None, None, 2.0),
    "a pair's bins as a float": lambda: arrays.joint_counts(bytes([0, 1]), bytes([1, 0]), 2, 2.0, None, None),
    "a count of bands as a float": lambda: arrays.running_totals(_floats_bytes([1.0, 2.0]), None, None, None, 1.0),
    "a joint count as a float": lambda: arrays.joint_groups(bytearray(2), 1, bytes(2), 2.0),
    "an out_width as a float": lambda: arrays.take_codes(bytes([0]), 1, bytes([1]), 1, None, bytearray(1), 1.0),
    "a start as a float": lambda: arrays.hidden_sums(numpy.zeros(3, dtype="uint64"), bytearray(3), 0.0),
}


@pytest.mark.parametrize("case", sorted(_MALFORMED))
def test_a_malformed_input_raises_the_same_value_error_on_both_paths(case, monkeypatch):
    """Every check is made before the path is chosen: the same ValueError, word for word, on a little- and a big-endian computer."""
    raised = []
    for path in PATHS:
        _on(path, monkeypatch)
        with pytest.raises(ValueError) as caught:
            _MALFORMED[case]()
        raised += [str(caught.value)]
    assert raised[0] == raised[1]


_OVERFLOWS = {
    "scores of 1.7e308 moved by a factor of 3": lambda: arrays.move_from_means(
        bytearray(_floats_bytes([1.7e308, -1.7e308, 1.0])), None, None, None, [0.0], [3.0]
    ),
    "a weight of 1e300 times an encoding of 1e300": lambda: arrays.score_rows(
        bytes([1, 1, 1]), [("band", 1e300, [0, 0, 0], [1e300])], [0.5], 1.0, bytes(9), bytearray(24)
    ),
    "an infinity read as a float": lambda: arrays._floats([math.inf]),
    # Lane ARR-a's repair 2 (the verify of repair 1, item 1): the noise's,
    # the normal scores' and an encoding's 2 ** 500 bounds, each a product
    # that would overflow on numpy's path.
    "a noise of 1.7e308 times a hidden score near 6": lambda: arrays.score_rows(
        bytes([1]), [], [0.5], 1.7e308, bytes([0xF4, 0xFF, 0x0B]), bytearray(8)
    ),
    "a normal score of 1.7e308 weighed by 2": lambda: arrays.score_rows(
        bytes([1]), [("rank", 2.0, bytes(2), bytes([1]))], [1.7e308], 0.0, bytes(3), bytearray(8)
    ),
    "an encoding of 1.7e308 weighed by 2": lambda: arrays.score_rows(
        bytes([1]), [("band", 2.0, [0], [1.7e308])], [0.5], 0.0, bytes(3), bytearray(8)
    ),
}


@pytest.mark.parametrize("path", PATHS)
@pytest.mark.parametrize("case", sorted(_OVERFLOWS))
def test_numpy_prints_nothing_the_plain_loop_does_not(case, path, monkeypatch, capfd):
    """G1's printed text: an overflow is refused on both paths, no warning is raised and nothing reaches the screen."""
    _on(path, monkeypatch)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        with pytest.raises(ValueError):
            _OVERFLOWS[case]()
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        with pytest.raises(ValueError):
            _OVERFLOWS[case]()
    assert [str(warning.message) for warning in caught] == []
    printed = capfd.readouterr()
    assert (printed.out, printed.err) == ("", "")


def test_numpy_s_path_of_the_moves_and_the_score_ends_at_2_500(monkeypatch):
    """Below 2 ** 500 in every input numpy's path is taken; at 2 ** 500 the plain loop; the plain loop's bytes either way."""
    plain_writes = []
    write = arrays._plain_floats_into

    def spy(values, out):
        plain_writes.append(len(values))
        write(values, out)

    monkeypatch.setattr(arrays, "_plain_floats_into", spy)
    top = math.ldexp(1.0, 500)
    below = math.nextafter(top, 0.0)
    for largest, plain in ((below, False), (top, True)):
        for scores, mean, factor in (
            ([largest, -1.0, 0.5], 0.25, 1.5),
            ([1.0, -1.0, 0.5], largest, 1.5),
            ([1.0, -1.0, 0.5], 0.25, largest),
        ):
            plain_writes.clear()
            store = bytearray(_floats_bytes(scores))
            arrays.move_from_means(store, None, None, None, [mean], [factor])
            assert bytes(store) == _floats_bytes([mean + factor * (value - mean) for value in scores])
            assert bool(plain_writes) == plain
        plain_writes.clear()
        out = bytearray(8)
        arrays.score_rows(bytes([1]), [("band", largest, [0], [0.5])], [0.5], 0.0, bytes([0xFA, 0xFF, 0x05]), out)
        assert _float_list(out) == [largest * 0.5]
        assert bool(plain_writes) == plain
        # Lane ARR-a's repair 2 (the verify of repair 1, item 1): the same
        # bound on the noise (beside a hidden sum of 786,420, a hidden score
        # of (786420 - 393210) / 65536, near 6), on a rank partner's normal
        # scores and on a band partner's encoding.
        for partners, normal, noise, sums, expected in (
            ([], [0.5], largest, bytes([0xF4, 0xFF, 0x0B]), 0.0 + largest * ((786420 - 393210) / 65536)),
            ([("rank", 0.5, bytes(2), bytes([1]))], [largest], 0.0, bytes([0xFA, 0xFF, 0x05]), 0.5 * largest),
            ([("band", 0.5, [0], [largest])], [0.5], 0.0, bytes([0xFA, 0xFF, 0x05]), 0.5 * largest),
        ):
            plain_writes.clear()
            out = bytearray(8)
            arrays.score_rows(bytes([1]), partners, normal, noise, sums, out)
            assert _float_list(out) == [expected]
            assert bool(plain_writes) == plain


# -- the types every output holds -------------------------------------------------------------


def _plain_value(value):
    """True when a value and everything inside it is a built-in: no numpy scalar or array."""
    if type(value) in (int, float, bool, bytes, bytearray, type(None)):
        return True
    if type(value) in (list, tuple):
        return all(_plain_value(item) for item in value)
    return False


def test_every_output_is_a_built_in_value():
    """`type(x) is float` and `is int`: a numpy float64 prints as np.float64(...) and would move a printed byte."""
    state = _column(1000)
    store = bytearray(_floats_bytes(_special_scores(random.Random(2), 1000)))
    grouped = arrays.rows_by_group(_groups(random.Random(3), 1000, 5), 4, state["present"])
    outputs = [
        arrays.code_counts(state["own"], state["present"], None, 256),
        arrays.joint_counts(state["own"], state["own"], 256, 256, None, None),
        arrays.exact_sum([1, 2], [0.5, 0.25]),
        arrays.running_totals(store, state["present"], None, state["of_row"], 8),
        grouped,
        arrays.order_by_score(grouped[0], grouped[1], grouped[2], store),
        arrays.take_codes(bytes(range(10)), 1, bytes(range(10)), 1, None, None, 1),
    ]
    for output in outputs:
        assert _plain_value(output), output
    assert type(arrays.exact_sum([1, 2], [0.5, 0.25])) is float
    assert all(type(count) is int for count in outputs[0])
    assert all(type(total) is float for total in outputs[3][0])


# -- the product mutants, each red ------------------------------------------------------------
#
# Each mutant changes what the helper computes -- through the numpy it
# calls, swapped for a stand-in that breaks one promise, or by the one
# step written out the wrong way -- and the check above it goes red.


class _NumpyWith:
    """numpy with some of its functions replaced (the helper's own code, run against a library that breaks one promise)."""

    def __init__(self, **replaced):
        self._replaced = replaced

    def __getattr__(self, name):
        if name in self._replaced:
            return self._replaced[name]
        return getattr(numpy, name)


def test_mutant_an_unstable_sort_on_the_tie_vector_is_red(monkeypatch):
    state = _column(200_000)
    rng = random.Random(6)
    score = [rng.choice((0.0, -0.0, 1.0, -1.0)) for _row in range(200_000)]
    grouped, width, starts, _ordered = arrays.rows_by_group(_groups(rng, 200_000, 3), 4, state["present"])
    expected = built.ordered_rows(grouped, width, starts, score)
    assert built.packed_values(arrays.order_by_score(grouped, width, starts, _floats_bytes(score)), width) == expected

    def unstable(values, kind=None):
        return numpy.argsort(values, kind="quicksort")

    monkeypatch.setattr(arrays, "numpy", _NumpyWith(argsort=unstable))
    got = arrays.order_by_score(grouped, width, starts, _floats_bytes(score))
    assert built.packed_values(got, width) != expected


def test_mutant_numpy_sum_for_the_exact_sum_is_red():
    def summed_by_numpy(counts, values):
        return float(numpy.sum(numpy.repeat(numpy.array(values), counts)))

    counts, values = [1, 1, 1], [1e16, 1.0, -1e16]
    assert arrays.exact_sum(counts, values) == math.fsum([1e16, 1.0, -1e16]) == 1.0
    assert summed_by_numpy(counts, values) != arrays.exact_sum(counts, values)


def test_mutant_a_missing_leading_zero_is_red():
    """A band whose every score is -0.0 totals 0.0 from the leading 0.0; a sum started from its first value keeps -0.0."""
    present = bytes([1, 1, 1])
    store = _floats_bytes([-0.0, -0.0, -0.0])
    assert _bits(arrays.running_totals(store, present, None, None, 1)[0][0]) == _bits(0.0)
    gathered = _float_list(store)
    started = gathered[0]
    for value in gathered[1:]:
        started = started + value
    assert _bits(started) == _bits(-0.0) != _bits(0.0)


def test_mutant_the_composite_key_formed_first_on_the_2_32_case_is_red():
    rows = 64
    count = 1 << 62
    groups = [row % 8 for row in range(rows)]
    found = built.packed_store(groups, 4)
    bands = bytearray(row % 3 for row in range(rows))
    expected = bytearray(found)
    built.joint_groups(expected, bands, count, rows)
    got = bytearray(found)
    arrays.joint_groups(got, 4, bands, count)
    assert got == expected

    def keyed_first(found, width, bands, count):
        group = numpy.frombuffer(arrays._wide(found, width), dtype="<i8")
        band = numpy.frombuffer(arrays._codes(bands), dtype="<i8")
        with numpy.errstate(over="ignore"):
            key = group * numpy.int64(count) + band
        seen = {}
        renumbered = [seen.setdefault(int(value), len(seen)) for value in key]
        found[0:len(found)] = built.packed_store(renumbered, width)

    mutated = bytearray(found)
    keyed_first(mutated, 4, bands, count)
    assert mutated != expected


class _Leaking:
    """A counted array whose tolist hands back numpy scalars, as a function returning numpy's own values would."""

    def __init__(self, counted):
        self._counted = counted

    def tolist(self):
        return list(self._counted)


def test_mutant_a_numpy_scalar_returned_is_red(monkeypatch):
    assert _plain_value(arrays.code_counts(bytes([1, 2, 2]), None, None, 4))
    monkeypatch.setattr(arrays, "numpy", _NumpyWith(bincount=lambda *args, **kw: _Leaking(numpy.bincount(*args, **kw))))
    got = arrays.code_counts(bytes([1, 2, 2]), None, None, 4)
    assert got == [0, 1, 2, 0]
    assert not _plain_value(got)
    assert type(got[1]) is not int


def test_mutant_a_repeated_scatter_index_is_red(monkeypatch):
    """A slot list naming one row twice takes the plain path (the plain loop's last write stands); a check that let it through would not."""
    taken = []
    plain = arrays._plain_scatter_places

    def spy(*args):
        taken.append(True)
        plain(*args)

    monkeypatch.setattr(arrays, "_plain_scatter_places", spy)
    order = built.packed_store([0, 1, 0], 1)
    places = built.packed_store([2, 1, 0], 1)
    index, own = bytearray(3), bytearray(3)
    arrays.scatter_places(order, 1, places, 1, index, 1, own, bytes([7, 8, 9]), None, None)
    assert taken == [True]
    expected_index, expected_own = bytearray(3), bytearray(3)
    built.write_back([0, 1, 0], places, 1, expected_index, 1, expected_own, bytes([7, 8, 9]), None, None)
    assert (index, own) == (expected_index, expected_own)
    taken.clear()
    # The uniqueness check blinded (every row counted once): the scatter runs on numpy's path.
    monkeypatch.setattr(arrays, "numpy", _NumpyWith(bincount=lambda values, **kw: numpy.zeros(len(values), dtype="<i8") + 1))
    arrays.scatter_places(order, 1, places, 1, bytearray(3), 1, bytearray(3), bytes([7, 8, 9]), None, None)
    assert taken == []


# -- lane ARR-a's repair 2 (LANE ARR RULINGS 5 (3) and (4); Codex's items 3 and 4) -------------
#
# A buffer the scatter writes, handed again as another of its arguments,
# gave numpy's path and the plain loop different bytes (the plain loop
# reads the places' codes and rank codes between its writes): every such
# alias is refused before the path is chosen, on both paths. The other
# writers read every input before they write, so an alias there gives one
# result on both paths. A whole float among the places' starts is read as
# its whole number on both paths, and a draw of more than one dimension
# is refused on both.

_SCATTER_SLOTS = {"order": 0, "places": 2, "index": 4, "own": 6, "slot_codes": 7, "ranks": 8, "slot_rank": 9}

# (a buffer written, another buffer): rows, places, the order's, the places' and the index's widths -- chosen so
# that the two buffers hold the same number of bytes and every other check passes.
_SCATTER_ALIASES = {
    ("index", "order"): (2, 2, 1, 1, 1),
    ("index", "places"): (2, 2, 1, 1, 1),
    ("index", "own"): (2, 2, 1, 1, 1),
    ("index", "slot_codes"): (2, 2, 1, 1, 1),
    ("index", "ranks"): (2, 2, 1, 1, 2),
    ("index", "slot_rank"): (2, 2, 1, 1, 2),
    ("own", "order"): (2, 2, 1, 1, 1),
    ("own", "places"): (2, 2, 1, 1, 1),
    ("own", "slot_codes"): (2, 2, 1, 1, 1),
    ("own", "ranks"): (0, 2, 1, 1, 1),
    ("own", "slot_rank"): (2, 1, 1, 1, 1),
    ("ranks", "order"): (2, 2, 2, 1, 1),
    ("ranks", "places"): (2, 2, 1, 2, 1),
    ("ranks", "slot_codes"): (2, 4, 1, 1, 1),
    ("ranks", "slot_rank"): (2, 2, 1, 1, 1),
}


def _scatter_arguments(rows, places, order_width, places_width, index_width):
    """A valid write-back: rows 1 and 0 (none where there are no rows) take the last place and the first."""
    taken = [1, 0][:rows]
    return [
        bytearray(built.packed_store(taken, order_width)),
        order_width,
        bytearray(built.packed_store([places - 1, 0][: len(taken)], places_width)),
        places_width,
        bytearray(rows * index_width),
        index_width,
        bytearray(rows),
        bytearray(range(5, 5 + places)),
        bytearray(2 * rows),
        bytearray(range(1, 1 + 2 * places)),
    ]


@pytest.mark.parametrize("pair", sorted(_SCATTER_ALIASES), ids=[" is ".join(pair) for pair in sorted(_SCATTER_ALIASES)])
def test_a_scatter_buffer_written_and_handed_again_is_refused_on_both_paths(pair, monkeypatch):
    raised = []
    for path in PATHS:
        _on(path, monkeypatch)
        handed = _scatter_arguments(*_SCATTER_ALIASES[pair])
        handed[_SCATTER_SLOTS[pair[0]]] = handed[_SCATTER_SLOTS[pair[1]]]
        with pytest.raises(ValueError) as caught:
            arrays.scatter_places(*handed)
        raised += [str(caught.value)]
    assert raised == ["a buffer written is no other buffer handed in"] * 2


def test_a_scatter_of_distinct_buffers_still_writes_the_plain_loop_s_bytes(monkeypatch):
    """Each configuration above, unaliased, writes what the frozen loop writes, on both paths."""
    for config in sorted(set(_SCATTER_ALIASES.values())):
        expected = _scatter_arguments(*config)
        built.write_back(
            built.packed_values(expected[0], expected[1]), *expected[2:]
        )
        for path in PATHS:
            if path == "plain":
                monkeypatch.setattr(arrays.sys, "byteorder", "big")
            got = _scatter_arguments(*config)
            arrays.scatter_places(*got)
            assert got == expected, (config, path)
        monkeypatch.undo()


def _writer_results(case):
    """One aliased call of a writer other than the scatter, and every buffer it holds afterwards."""
    if case == "the groups renumbered beside themselves as bands":
        found = bytearray([0, 1, 0, 1, 2, 2])
        arrays.joint_groups(found, 1, found, 3)
        return bytes(found)
    if case == "the codes taken into their own index":
        index = bytearray([1, 0, 2])
        arrays.take_codes(index, 1, bytes([4, 5, 6]), 1, [0, 1, 2, 3, 4, 5, 6], index, 1)
        return bytes(index)
    if case == "the codes taken into their own table":
        table = bytearray([2, 0, 1])
        arrays.take_codes(bytes([1, 0, 2]), 1, table, 1, None, table, 1)
        return bytes(table)
    raise AssertionError(case)


@pytest.mark.parametrize(
    "case",
    ["the groups renumbered beside themselves as bands", "the codes taken into their own index", "the codes taken into their own table"],
)
def test_the_other_writers_read_every_input_before_they_write(case, monkeypatch):
    fast = _writer_results(case)
    monkeypatch.setattr(arrays.sys, "byteorder", "big")
    assert _writer_results(case) == fast


@pytest.mark.parametrize("path", PATHS)
def test_a_whole_float_among_the_starts_reads_as_its_whole_number(path, monkeypatch):
    """Codex's case: [0, 1.0] as the starts gave a nought byte on numpy's path and a TypeError on the plain one."""
    _on(path, monkeypatch)
    expected = arrays.places_by_group(b"\0", 1, b"\1", [0, 1], [0], b"\0", 1, b"\0", False)
    assert expected == bytearray(b"\0")
    assert arrays.places_by_group(b"\0", 1, b"\1", [0, 1.0], [0], b"\0", 1, b"\0", False) == expected
    assert arrays.places_by_group(b"\0", 1, b"\1", [0, 1], [0.0], b"\0", 1, b"\0", False) == expected
