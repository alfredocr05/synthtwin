"""The reference of the polish's sort (lane MPg's repair 4, plan P4-D456; LANE MPg RULINGS 14 (3)).

`polish_column` is G16.3's column step, `generation._polish_column`, as
lane MPg's repair 3 shipped it (`03ead853`), copied line for line but for
one block: inside each frame group the rows holding a reading are sorted
as plain `(score, row)` tuples, the row last, so two equal scores go to
the lower row, and they take the group's places listed by a plain sort (a
binary's `(level, place)` pairs). Nothing here calls the product's own
key (`_score_key`: the score's exponent and fraction and the row as one
whole number, repair 2's memory) or its packed groups and places
(`_rows_by_group`, `_places_by_group`). The product's other names are
read at call time (`generation._feature`, `_frame_groups`, `_row_bands`,
`_solved` and the `_POLISH_*` settings), so a test that changes a setting
changes it for both.

tests/test_moment_polish_sort.py swaps it in for `generation._polish_column`
and asks the shipped twin of a 20,000-row table to be its twin byte for
byte. IT IS THE NET FOR LANE ARR-b, which rewrites the polish's sorts and
sums with the audited array helper: whatever that lane writes, the twin
stays these bytes. A lane that changes the meaning or the interface of a
helper this text calls freezes that helper's text here, as built, beside
this one; a lane that changes what the polish does on purpose (lane
MPg2) copies this text again from its own head and says so in its plan
decision.
"""

import math

from synthtwin import chain_walk, generation


def polish_column(
    column: "generation._WalkColumn",
    name: str,
    targets: "list[generation._PolishTarget]",
    sums: "chain_walk.Packed",
    state: "generation._PolishState",
    walk: "generation._Walk",
    adjust: bool,
) -> None:
    """G16.3's column step as shipped, but the frame groups sorted as (score, row) tuples, the row last (see the module)."""
    index = column.index
    slot_codes = column.slot_codes
    if index is None or column.slot_l0 is None or slot_codes is None:
        return
    own = state.codes[name]
    present = state.has[name]
    ranks = state.ranks[name] if name in state.ranks else None
    slot_rank = column.slot_rank
    rows = len(own)
    count = 0
    for row in range(rows):
        count = count + present[row]
    if count < 2:
        return
    width = len(targets)
    taken = min(count, generation._POLISH_SAMPLE)
    positions = chain_walk.spread_positions(count, taken)
    sampled: "list[int]" = []
    seen = 0
    for row in range(rows):
        if not present[row]:
            continue
        if len(sampled) < taken and positions[len(sampled)] == seen:
            sampled += [row]
        seen = seen + 1
    positions = []
    centred: "list[list[float]]" = []
    # A partner's rank score is read in units of its spread on the sample,
    # so its aim is a correlation (repair 1); an encoding keeps its own.
    unit = [1.0 for _target in targets]
    for j in range(width):
        target = targets[j]
        values = generation._feature(target, sampled, state)
        centre = math.fsum(values) / taken
        shifted = [value - centre for value in values]
        if target.kind in ("pair", "by"):
            spread_j = math.sqrt(math.fsum([value * value for value in shifted]) / taken)
            if spread_j > 0.0:
                unit[j] = 1.0 / spread_j
                shifted = [value * unit[j] for value in shifted]
        centred += [shifted]
    matrix = [[0.0 for _c in range(width)] for _a in range(width)]
    for a in range(width):
        for c in range(a, width):
            matrix[a][c] = math.fsum([x * y for x, y in zip(centred[a], centred[c])]) / taken
            matrix[c][a] = matrix[a][c]
        matrix[a][a] = matrix[a][a] + generation._POLISH_RIDGE
    centred = []
    aims = [target.aim for target in targets]
    beta = generation._solved(matrix, aims)
    explained = 0.0
    for j in range(width):
        explained = explained + beta[j] * aims[j]
    rest = 1.0 - explained
    noise = math.sqrt(rest if rest > generation._POLISH_LEAST_NOISE else generation._POLISH_LEAST_NOISE)
    # Every row's score, built a chunk of rows at a time (0.0 on a row holding no reading).
    score = [0.0 for _row in range(rows)]
    for start in range(0, rows, generation._POLISH_CHUNK):
        members = [row for row in range(start, min(rows, start + generation._POLISH_CHUNK)) if present[row]]
        part = [0.0 for _row in members]
        for j in range(width):
            values = generation._feature(targets[j], members, state)
            weight = beta[j] * unit[j]
            part = [total + weight * value for total, value in zip(part, values)]
            values = []
        for at in range(len(members)):
            row = members[at]
            score[row] = part[at] + noise * chain_walk.hidden_score(chain_walk.item(sums, row))
        members = []
        part = []
    # Each band's spread toward the published one: a row's score moved from its band's mean by the band's factor.
    if generation._POLISH_SPREADS:
        for target in targets:
            if target.kind == "pair" and target.scales:
                # A pair's own spread of the column (repair 2): the rows whose
                # partner holds a reading, one band, its scores moved from
                # their mean by the pair's factor; the other rows untouched.
                both = state.has[target.name]
                pair_total = 0.0
                pair_rows = 0
                for row in range(rows):
                    if present[row] and both[row]:
                        pair_total = pair_total + score[row]
                        pair_rows = pair_rows + 1
                if pair_rows:
                    pair_middle = pair_total / pair_rows
                    pair_factor = target.scales[0]
                    for row in range(rows):
                        if present[row] and both[row]:
                            score[row] = pair_middle + pair_factor * (score[row] - pair_middle)
                continue
            if target.kind != "within" or not target.scales:
                continue
            of_row = state.bands[(target.name, target.level)]
            bands = len(target.scales)
            totals = [0.0 for _band in range(bands)]
            counts = [0 for _band in range(bands)]
            for row in range(rows):
                if present[row] and of_row[row] < bands:
                    totals[of_row[row]] = totals[of_row[row]] + score[row]
                    counts[of_row[row]] = counts[of_row[row]] + 1
            means = [totals[band] / counts[band] if counts[band] else 0.0 for band in range(bands)]
            factors = target.scales
            for row in range(rows):
                if present[row] and of_row[row] < bands:
                    band = of_row[row]
                    score[row] = means[band] + factors[band] * (score[row] - means[band])
    # THE REFERENCE (lane MPg's repair 4): inside each frame group, the
    # rows holding a reading, sorted as (score, row) tuples, take the
    # group's places in rising order (a binary's: level 0, then 1).
    index_width = column.index_width
    groups = generation._frame_groups(column, name, state, walk)
    binary = name in state.keys
    members_of: "dict[int, list[int]]" = {}
    for row in range(rows):
        if present[row]:
            group = chain_walk.item(groups, row)
            if group not in members_of:
                members_of[group] = []
            members_of[group] += [row]
    for group in sorted(members_of):
        members = members_of[group]
        if binary:
            places = [
                pair[1]
                for pair in sorted(
                    (slot_codes[chain_walk.read_code(index, index_width, row)], chain_walk.read_code(index, index_width, row))
                    for row in members
                )
            ]
        else:
            places = sorted(chain_walk.read_code(index, index_width, row) for row in members)
        ranked = sorted((score[row], row) for row in members)
        for k in range(len(ranked)):
            row = ranked[k][1]
            place = places[k]
            chain_walk.write_code(index, index_width, row, place)
            own[row] = slot_codes[place]
            if ranks is not None and slot_rank is not None:
                ranks[2 * row] = slot_rank[2 * place]
                ranks[2 * row + 1] = slot_rank[2 * place + 1]
    members_of = {}
    score = []
    # A COLUMN MOVED EARLIER IS READ AS MOVED (G16.3): a row moved inside
    # its frame may now stand in another of the column's finer bands, so
    # every band of it a target reads is read again here.
    for key in [key for key in state.bands if key[0] == name]:
        state.bands[key] = generation._row_bands(column, key[1], len(own))
    if not adjust:
        return
    centre, spread = state.spreads[name]
    if spread <= 0.0:
        return
    table = [(code - centre) / spread for code in range(256)]
    whole_x = math.fsum(table[own[row]] for row in range(rows) if present[row])
    for j in range(width):
        target = targets[j]
        got = 0.0
        if target.kind == "pair":
            other_centre, other_spread = state.spreads[target.name]
            other = [((code - other_centre) / other_spread if other_spread > 0.0 else 0.0) for code in range(256)]
            partner = state.codes[target.name]
            both = state.has[target.name]
            n = 0
            for row in range(rows):
                if present[row] and both[row]:
                    n = n + 1
            if n < 2:
                continue
            sx = math.fsum(table[own[row]] for row in range(rows) if present[row] and both[row])
            sxx = math.fsum(table[own[row]] * table[own[row]] for row in range(rows) if present[row] and both[row])
            sy = math.fsum(other[partner[row]] for row in range(rows) if present[row] and both[row])
            syy = math.fsum(other[partner[row]] * other[partner[row]] for row in range(rows) if present[row] and both[row])
            sxy = math.fsum(table[own[row]] * other[partner[row]] for row in range(rows) if present[row] and both[row])
            vx = sxx - sx * sx / n
            vy = syy - sy * sy / n
            if vx <= 0.0 or vy <= 0.0:
                continue
            got = (sxy - sx * sy / n) / math.sqrt(vx * vy)
        elif target.kind == "by":
            # The number's split by this binary, read on the number's rows (the binary's bands just read again).
            number_centre, number_spread = state.spreads[target.name]
            if number_spread <= 0.0:
                continue
            number = [(code - number_centre) / number_spread for code in range(256)]
            number_codes = state.codes[target.name]
            holding = state.has[target.name]
            encoding = target.encoding
            of_row = state.bands[(name, target.level)]
            m = 0
            for row in range(rows):
                if holding[row]:
                    m = m + 1
            if m < 2:
                continue
            sx = math.fsum(number[number_codes[row]] for row in range(rows) if holding[row])
            sy = math.fsum(encoding[of_row[row]] for row in range(rows) if holding[row] and of_row[row] < len(encoding))
            sxy = math.fsum(
                number[number_codes[row]] * encoding[of_row[row]] for row in range(rows) if holding[row] and of_row[row] < len(encoding)
            )
            got = sxy / m - (sx / m) * (sy / m)
        else:
            encoding = target.encoding
            of_row = state.bands[(target.name, target.level)]
            sy = math.fsum(encoding[of_row[row]] for row in range(rows) if present[row] and of_row[row] < len(encoding))
            sxy = math.fsum(
                table[own[row]] * encoding[of_row[row]] for row in range(rows) if present[row] and of_row[row] < len(encoding)
            )
            got = sxy / count - (whole_x / count) * (sy / count)
        target.aim = target.aim + generation._POLISH_STEP * (target.goal - got) / target.slope
        if target.kind != "within":
            # A correlation, a binary's latent one too, aims at most at its
            # bound either way (`most`: `_POLISH_AIM_MOST`, or for a pair
            # half way from its goal to 1, repair 2): past it the score is
            # already the features alone, so a larger aim only stores up
            # what the noise of earlier rounds missed (repair 1).
            target.aim = min(target.most, max(-target.most, target.aim))
        if generation._POLISH_SPREADS and target.kind == "pair" and target.scales:
            # The pair's own spread of the column: its factor moved by the
            # published spread over the spread its codes now hold on the
            # rows whose partner holds a reading (repair 2).
            both = state.has[target.name]
            held_pair = 0
            total_pair = 0
            squares_pair = 0
            for row in range(rows):
                if present[row] and both[row]:
                    code = own[row]
                    held_pair = held_pair + 1
                    total_pair = total_pair + code
                    squares_pair = squares_pair + code * code
            wanted = target.sds[0]
            if held_pair >= 2 and wanted > 0.0:
                spread_now = (held_pair * squares_pair - total_pair * total_pair) / (held_pair * (held_pair - 1))
                if spread_now > 0.0:
                    factor = target.scales[0] * wanted / math.sqrt(spread_now)
                    target.scales[0] = min(generation._POLISH_SPREAD_MOST, max(generation._POLISH_PAIR_SPREAD_LEAST, factor))
        if generation._POLISH_SPREADS and target.kind == "within" and target.scales:
            of_row = state.bands[(target.name, target.level)]
            bands = len(target.scales)
            held = [0 for _band in range(bands)]
            totals = [0 for _band in range(bands)]
            squares = [0 for _band in range(bands)]
            for row in range(rows):
                if present[row] and of_row[row] < bands:
                    band = of_row[row]
                    code = own[row]
                    held[band] = held[band] + 1
                    totals[band] = totals[band] + code
                    squares[band] = squares[band] + code * code
            for band in range(bands):
                wanted = target.sds[band]
                if held[band] < 2 or wanted <= 0.0:
                    continue
                spread_now = (held[band] * squares[band] - totals[band] * totals[band]) / (held[band] * (held[band] - 1))
                if spread_now <= 0.0:
                    continue
                factor = target.scales[band] * wanted / math.sqrt(spread_now)
                target.scales[band] = min(generation._POLISH_SPREAD_MOST, max(generation._POLISH_SPREAD_LEAST, factor))
    if generation._POLISH_FEASIBLE:
        # THE AIMS STAY FEASIBLE TOGETHER (repair 1): where the moved aims ask
        # the score for more than its whole spread (`a . (C + ridge I)^-1 a`
        # past `1 - _POLISH_LEAST_NOISE`, on this round's sample), every aim
        # is scaled down by one factor to that edge, so no aim stores up what
        # the others' fresh draws missed and the next re-sort answers its aims.
        moved = [target.aim for target in targets]
        asked = generation._solved(matrix, moved)
        whole = 0.0
        for j in range(width):
            whole = whole + asked[j] * moved[j]
        edge = 1.0 - generation._POLISH_LEAST_NOISE
        if whole > edge:
            factor = math.sqrt(edge / whole)
            for target in targets:
                target.aim = target.aim * factor
