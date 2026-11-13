"""The reference for rule B's moments (contract 4.6d.0, plan P4-D455): each published moment, computed apart.

WHAT IT IS. An independent statement, in exact fractions and in decimal
arithmetic, of every number rule B publishes and of the counts each
implies DIRECTLY, written from the contract's words and not from the
product's code (`chain_moments`), so a test can hold the two against each
other on the same rows. It reads ROWS ALREADY CODED: for each moment
column one value a row (a number's linear code 0 to 255, a binary's 0 or
1) or None where the row holds no reading, and for each grouping column
one `L1` band a row with the band's published total and the `L2` band
holding each `L1` band. How a cell becomes a code is the chain's reading
(contract 4.6b.2 and 4.6d.1), shared by the product and this reference;
what is computed from the codes is not shared.

THE MOMENTS, ONE FUNCTION EACH (lane MPg's twin is judged against these):
- `column_mean`, `column_sd`, `column_share`: a column over its readings;
- `correlation`: a pair of numbers over the rows holding both, and
  `published_r`, the form rule B publishes it in: Fisher's z rounded to
  its count's grid, and the hyperbolic tangent of that grid point printed
  to 12 decimals (the decimal module's ln and exp, correctly rounded);
- `band_mean`, `band_sd`, `band_share`: a column inside one band of a
  grouping column;
- `slope`: the least-squares slope of one number on another over the rows
  holding both, never published apart, and `published_slope`, the same
  slope DERIVED from the published object: r times the pair's spread of
  the second over the pair's spread of the first (the pair's own spreads
  where it holds fewer rows than either column's readings, the columns'
  own where it holds them all);
- `spread_top`: the largest spread `n` codes can hold (half at 0, half at
  255, the `n - 1` divisor), the ceiling a loader reads a spread against.
`unit` states each moment's unit at its own count (one decimal place finer
for each 100-fold, or part of one, the count exceeds 20,000; a column's
and a pair's spreads in thousandths of a code at the floor, a band's in
tenths, a mean in tenths, a share in ten-thousandths), `rounded`
puts a moment on it, half away from nought, and `grid_z` puts Fisher's z
on its grid (ten-thousandths of z at 20,000 rows or fewer, LANE MPp
RULINGS 7), at most the grid point whose tanh is 0.999999. `direct_counts` lists the counts a published moment implies
directly, each of which rule B requires to be 0 or at least the floor (a
pair's four presence cells; a count a column publishes about itself
stands). `describe` assembles the whole object as the contract states it.
"""

from decimal import ROUND_FLOOR, ROUND_HALF_UP, Decimal, localcontext
from fractions import Fraction

SCALES = {"column_sd": 1000, "correlation": 10**12, "fisher_z": 10000, "mean": 10, "sd": 10, "share": 10000}
FLOOR_ROWS = 20000
R_TOP = Fraction(999999, 1000000)
PARTNERS = 24


def unit(scale, n):
    """The contract's unit for a moment over `n`: `scale`, times ten for each 100-fold (or part of one) past 20,000."""
    places = 0
    while n > FLOOR_ROWS * 100**places:
        places += 1
    return scale * 10**places


def _present(values):
    return [v for v in values if v is not None]


def column_mean(values):
    """The mean of a column's readings, exactly."""
    held = _present(values)
    return Fraction(sum(held), len(held))


def column_sd(values):
    """The sample standard deviation (divisor n - 1) of a column's readings, as its square, exactly."""
    held = _present(values)
    mean = Fraction(sum(held), len(held))
    return sum((Fraction(v) - mean) ** 2 for v in held) / (len(held) - 1)


def column_share(values):
    """The share of a binary's second level among its readings, exactly."""
    return column_mean(values)


def correlation(first, second):
    """Pearson's correlation over the rows holding both, as (its square, its sign); None without spread."""
    pairs = [(a, b) for a, b in zip(first, second) if a is not None and b is not None]
    n = len(pairs)
    ma = Fraction(sum(a for a, _b in pairs), n)
    mb = Fraction(sum(b for _a, b in pairs), n)
    cross = sum((a - ma) * (b - mb) for a, b in pairs)
    va = sum((a - ma) ** 2 for a, _b in pairs)
    vb = sum((b - mb) ** 2 for _a, b in pairs)
    if va == 0 or vb == 0:
        return None
    return cross * cross / (va * vb), (-1 if cross < 0 else 1)


def grid_z(square, scale):
    """Fisher's z of a correlation whose square is `square`, `atanh(|r|)`, on its grid: whole units of `1 / scale`, half
    up, at most the largest grid point whose tanh is 0.999999 (an exact linear tie takes that top)."""
    with localcontext() as context:
        context.prec = 100
        bound = Decimal(R_TOP.numerator) / R_TOP.denominator
        top = int((((1 + bound) / (1 - bound)).ln() / 2 * scale).to_integral_value(rounding=ROUND_FLOOR))
        if square >= 1:
            return top
        size = (Decimal(square.numerator) / Decimal(square.denominator)).sqrt()
        z = ((1 + size) / (1 - size)).ln() / 2
        units = int((z * scale).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return min(units, top)


def published_r(square, sign, n):
    """A pair's published r at `n` rows: the tanh of its grid point of z, in units of 1e-12, half away from nought."""
    scale = unit(SCALES["fisher_z"], n)
    units = grid_z(square, scale)
    with localcontext() as context:
        context.prec = 100
        grown = (Decimal(2 * units) / scale).exp()
        printed = int((((grown - 1) / (grown + 1)) * SCALES["correlation"]).quantize(Decimal(1), rounding=ROUND_HALF_UP))
    return sign * printed


def slope(first, second):
    """The least-squares slope of `second` on `first` over the rows holding both (complete pairs), exactly as a fraction:
    r times the spread of `second` over the spread of `first`, both spreads taken over those same rows."""
    pairs = [(a, b) for a, b in zip(first, second) if a is not None and b is not None]
    n = len(pairs)
    ma = Fraction(sum(a for a, _b in pairs), n)
    mb = Fraction(sum(b for _a, b in pairs), n)
    va = sum((a - ma) ** 2 for a, _b in pairs)
    return sum((a - ma) * (b - mb) for a, b in pairs) / va


def pair_spreads(first, second):
    """The two sample variances (divisor n - 1) over the rows holding both columns, exactly: (of `first`, of `second`)."""
    pairs = [(a, b) for a, b in zip(first, second) if a is not None and b is not None]
    return column_sd([a for a, _b in pairs]), column_sd([b for _a, b in pairs])


def spread_top(n, scale):
    """The largest published spread of `n` codes of 0 to 255, in units of `1 / scale`: half the readings at each end, so
    the squared deviations total floor(n / 2) * ceil(n / 2) * 255 ** 2 / n, over n - 1, rounded as a spread is."""
    low = n // 2
    return rounded(Fraction(low * (n - low) * 255 * 255, n * (n - 1)), scale, root=True)


def published_slope(moments, first, second):
    """The slope of `second` on `first` DERIVED from a published object (the interface lane MPg's walk reads): r times
    the pair's spread of `second` over the pair's spread of `first`, each in the unit of its count; None where the
    pair is not published."""
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    own = {entry["column"]: entry for entry in moments["columns"]}
    at, other = numbers.index(first), numbers.index(second)
    row, place = max(at, other), min(at, other)
    pair = moments["correlations"][row][place]
    if pair is None:
        return None
    r = Fraction(pair[0], moments["scales"]["correlation"])
    if len(pair) == 3:
        scale = unit(moments["scales"]["column_sd"], pair[1])
        found = {numbers[row]: Fraction(pair[2][0], scale), numbers[place]: Fraction(pair[2][1], scale)}
    else:
        found = {name: Fraction(own[name]["sd"], unit(moments["scales"]["column_sd"], own[name]["n"])) for name in (first, second)}
    return r * found[second] / found[first]


def _inside(values, bands, band):
    return [v for v, g in zip(values, bands) if g == band and v is not None]


def band_mean(values, bands, band):
    """A column's mean among the rows of one band, exactly."""
    held = _inside(values, bands, band)
    return Fraction(sum(held), len(held))


def band_sd(values, bands, band):
    """A column's sample variance among the rows of one band, exactly."""
    return column_sd(_inside(values, bands, band))


def band_share(values, bands, band):
    """A binary's share of its second level among the rows of one band, exactly."""
    return band_mean(values, bands, band)


def rounded(value, scale, root=False, sign=1):
    """`value` (or its square root, `root`) in units of `1 / scale`, half away from nought, by decimal arithmetic."""
    with localcontext() as context:
        context.prec = 60
        number = Decimal(value.numerator) / Decimal(value.denominator)
        if root:
            number = number.sqrt()
        units = (number * scale).quantize(Decimal(1), rounding=ROUND_HALF_UP)
    return sign * int(units)


def direct_counts(kind, n, total_rows_of_band=None, ones=None, outside=(), tabled=None, own=()):
    """The counts a moment implies directly: its rows, a band's rows without a reading, a binary's two levels, and a
    pair's readings outside it and rows holding neither (`tabled` the table's rows). `own` names the outside counts
    that equal a column's own unread count (the other column read on every tabled row), which stand."""
    found = [n]
    if total_rows_of_band is not None:
        found += [total_rows_of_band - n]
    if kind == "binary" and ones is not None:
        found += [ones, n - ones]
    found += [count for at, count in enumerate(outside) if at not in own]
    if tabled is not None and len(outside) == 2:
        found += [tabled - (n + outside[0]) - (n + outside[1]) + n]
    return found


def passes(count, floor):
    return count == 0 or count >= floor


def _band_level(kind, values, bands, totals, small, floor):
    """A column's groups over one level's bands, all or none: (groups, share between) or None."""
    groups, between = [], Fraction(0)
    for band in range(len(totals)):
        held = _inside(values, bands, band)
        n = len(held)
        ones = sum(held) if kind == "binary" else None
        if not all(passes(c, floor) for c in direct_counts(kind, n, totals[band], ones)):
            return None
        if kind == "binary" and band in small and len([c for c in (ones, n - ones, totals[band] - n) if c]) < 2:
            return None
        if n == 0:
            groups += [[0]]
            continue
        mean = Fraction(sum(held), n)
        between += n * mean * mean
        if kind == "binary":
            groups += [[n, rounded(mean, unit(SCALES["share"], n))]]
        else:
            groups += [[n, rounded(mean, unit(SCALES["mean"], n)), rounded(column_sd(held), unit(SCALES["sd"], n), root=True)]]
    held_all = [v for v, g in zip(values, bands) if v is not None]
    mean_all = Fraction(sum(held_all), len(held_all))
    whole = sum((Fraction(v) - mean_all) ** 2 for v in held_all)
    share = (between - len(held_all) * mean_all * mean_all) / whole if whole else Fraction(0)
    return groups, share


def describe(columns, groupings, floor):
    """Rule B's whole object from coded rows.

    `columns`: [(name, kind, values)], kind "number" or "binary", values one
    code or None a row, in schema order; `groupings`: [(name, bands,
    totals, small, coarsest)], bands one `L1` band a row, totals the
    published `L1` totals, small the `L1` bands holding an own-fact group
    of 1 to `f - 1` rows, coarsest the `L2` band of each `L1` band, in
    schema order. RULE W1 (contract 4.6b.3) for a binary: a band holding
    such a group holds two of the binary's levels or its absence. A
    grouping whose `L1` bands do not all pass is read on its `L2` bands.
    Returns (object or None, refused count).
    """
    entries, kept, refused = [], [], 0
    for name, kind, values in columns:
        held = _present(values)
        n = len(held)
        if n < floor or n < 2:
            refused += 1
            continue
        if kind == "binary":
            ones = sum(held)
            if not all(passes(c, floor) for c in direct_counts(kind, n, ones=ones)):
                refused += 1
                continue
            entries += [{"column": name, "kind": kind, "n": n, "share": rounded(column_share(values), unit(SCALES["share"], n))}]
        else:
            entries += [{"column": name, "kind": kind, "mean": rounded(column_mean(values), unit(SCALES["mean"], n)), "n": n,
                         "sd": rounded(column_sd(values), unit(SCALES["column_sd"], n), root=True)}]
        kept += [(name, kind, values)]
    numbers = [(name, values) for name, kind, values in kept if kind == "number"]
    triangle = []
    for at in range(len(numbers)):
        line = []
        for other in range(at):
            first, second = numbers[at][1], numbers[other][1]
            tabled = len(first)
            both = sum(1 for a, b in zip(first, second) if a is not None and b is not None)
            outside = (len(_present(first)) - both, len(_present(second)) - both)
            own = [at_ for at_, column in enumerate((first, second)) if len(_present(column)) == tabled]
            found = correlation(first, second) if both >= 2 else None
            counts = direct_counts("number", both, outside=outside, tabled=tabled, own=own)
            if both < floor or not all(passes(c, floor) for c in counts) or found is None:
                line += [None]
                refused += 1
                continue
            entry = [published_r(found[0], found[1], both), both]
            if both < len(_present(first)) or both < len(_present(second)):
                spreads = pair_spreads(first, second)
                scale = unit(SCALES["column_sd"], both)
                entry += [[rounded(spreads[0], scale, root=True), rounded(spreads[1], scale, root=True)]]
            line += [entry]
        triangle += [line]
    within = []
    for name, kind, values in kept:
        ranked = []
        for place, (by, bands, totals, small, coarsest) in enumerate(groupings):
            if by == name:
                continue
            found = _band_level(kind, values, bands, totals, small, floor)
            level = 1
            if found is None and len(set(coarsest)) < len(totals):
                level = 2
                coarse_totals = [0] * (max(coarsest) + 1)
                for band, total in enumerate(totals):
                    coarse_totals[coarsest[band]] += total
                found = _band_level(kind, values, [coarsest[b] for b in bands], coarse_totals, {coarsest[b] for b in small}, floor)
            if found is None:
                refused += 1
                continue
            groups, share = found
            entry = {"by": by, "column": name, "groups": groups}
            if level == 2:
                entry["level"] = 2
            ranked += [(share, place, entry)]
        ranked.sort(key=lambda held: (-held[0], held[1]))
        within += [entry for _share, _place, entry in sorted(ranked[:PARTNERS], key=lambda held: held[1])]
    if not entries:
        return None, refused
    return {"columns": entries, "correlations": triangle, "partners": PARTNERS, "rule": "B",
            "scales": dict(SCALES), "within": within}, refused
