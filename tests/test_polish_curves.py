"""G16.3's CURVES and WHOLE VECTOR (lane CHG-b, plan P4-D492 part b): a bend finer than a partner's bands, and every band
of a label, as the published facts show them.

THE DEFECTS THEY ADDRESS (measured by the lane on invented tables of 20,000 rows through the commands a person types):
- a number is re-sorted on its partners' rank scores in a straight line, so a bend finer than the partner's bands
  was lost: a blood pressure rising with the square of age kept 0.15 to 0.24 of its squared term (the table 1.05).
  THE CURVES ARE BUILT, MEASURED AND OFF (`_POLISH_CURVES`, G16.3's paragraph of 2026-11-17): they raised that term
  to 0.25 to 0.29, but on lane E0b's ST1 at table seed 2 a curve of age on a censored follow-up moved the yes/no
  event polished after it off its ties (the estimates inside the half-split yardstick 0.537 against 0.669 without
  curves). Their arithmetic and mechanism are held here for a later design;
- a `within` or `share` target is one covariance, its band means read as one direction, so on a label of three
  levels or more the twin met that direction and left the others to the walk: a physical-status class of five
  levels came out with death shares 0.152, 0.149, 0.268, 0.532 and 0.857 by class against the table's 0.089, 0.175,
  0.305, 0.479 and 0.667, and the class's effect after adjusting fell to 0.13 against 0.40.

WHAT IS HELD, each red on its mutant:
- a CURVE target is made from published facts alone: the partner's band mean rank scores, the weighted straight
  line through the number's published band means, the departures and their chi-square against the gate's 0.001
  point on `k - 2` degrees of freedom, the feature (the departures joined between the band scores) and its variance:
  each the oracle's to the bit on a bend (kept), a straight line and a small bend (both dropped);
- on the oracle's 64-row twin with a curve target, every re-sort's places, aims and bands are the frozen case's, and
  the curve dropped gives another trail;
- on an invented 6,000-row state (a test size; the mechanism is per row), a number whose published band means bend
  comes back with its squared term (at least 0.8 of the table's) where its curve is aimed at, and with a fifth of it
  at most where only its straight correlation is (the curves switched off);
- on an invented state, a yes/no column aimed at its published shares in a five-level label's bands meets every
  level's share within 0.02 with the whole vector, and misses one by more than 0.025 with the one encoding (the whole
  vector switched off); the oracle's description keeps eleven band targets for its twelve-level label
  (tests/test_polish_grouping_gate.py).
"""

import dataclasses
import hashlib
import importlib.util
import json
import math
import pathlib
import random

import pytest

from synthtwin import chain_moments, chain_walk, contract, generation

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = REPOSITORY / "tools" / "reference"
FROZEN = json.loads((REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))["chain"]


def _load(name):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("chgbc_" + name, REFERENCE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _digest(values: "list[float] | tuple[float, ...]") -> str:
    return hashlib.sha256(",".join(v.hex() for v in values).encode("ascii")).hexdigest()


def _bands_ladder(name: str, totals: "list[int]") -> contract.LadderEntry:
    """A number's ladder of value bands, each its own `L1` band."""
    bands = tuple(((f"p{k}", f"p{k + 1}"),) for k in range(len(totals)))
    joined = tuple((k,) for k in range(len(totals)))
    return contract.LadderEntry(name, bands, tuple(totals), joined, ((tuple(range(len(totals))),)))


def _number(name: str, published: "list[int]") -> contract.MomentColumn:
    mean, sd, n = published
    return contract.MomentColumn(
        name, chain_moments.KIND_NUMBER, n, mean=mean / chain_moments.unit(chain_moments.SCALE_MEAN, n),
        sd=sd / chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, n), clip=(0.0, 255.0),
    )


def _within(column: str, by: str, groups: "list[list[int]]") -> contract.MomentWithin:
    found = []
    for n, mean, sd in groups:
        found += [contract.MomentGroup(n, mean=mean / chain_moments.unit(chain_moments.SCALE_MEAN, n),
                                       sd=sd / chain_moments.unit(chain_moments.SCALE_SPREAD, n))]
    return contract.MomentWithin(column, by, tuple(found), 1)


def test_a_curve_target_is_the_oracle_s_on_published_facts() -> None:
    """The partner's band scores, the grid, and for each published-fact input the curve's decision, statistic, goal,
    knots, residuals and feature are the oracle's to the last bit: the bend kept, a bend past the point whose feature's
    mean square is under 0.01 dropped by the floor, the straight line and the small bend dropped; a yes/no column's shares read on the threshold's scale likewise (its aim and slope too), the bend
    kept and the near-straight probit dropped; both kinds of curve measured and not adopted (the switches off); and the
    curve functions call no `math` function but `fsum` and `sqrt`."""
    oc = _load("oracle_cases")
    frozen = FROZEN["polish_curve"]
    partner = _bands_ladder("X", [2400] * 5)
    scores = generation._band_mean_scores(partner, 1)
    assert _digest([v for pair in scores if pair is not None for v in pair]) == frozen["scores_sha256"]
    grid = generation._curve_grid()
    assert len(grid) == generation._POLISH_CURVE_BINS == 4096 and _digest(grid) == frozen["grid_sha256"]
    kept = []
    for label, groups, column in oc.polish_curve_inputs():
        made = generation._curve_target(_number("Y", column), _within("Y", "X", groups), partner, grid)
        expect = frozen["inputs"][label]
        if not expect["kept"]:
            assert made is None, label
            continue
        assert made is not None, label
        target, statistic = made
        kept += [label]
        assert target.kind == "curve" and target.name == "X" and target.level == 1
        assert statistic.hex() == expect["statistic"] and target.goal.hex() == expect["goal"] and target.aim == 0.0
        assert _digest(target.knots) == expect["knots_sha256"] and _digest(target.encoding) == expect["departures_sha256"]
        assert _digest(target.table) == expect["table_sha256"]
    for label, groups, column in oc.polish_binary_curve_inputs():
        share, n = column
        entry = contract.MomentColumn("B", chain_moments.KIND_BINARY, n,
                                      share=share / chain_moments.unit(chain_moments.SCALE_SHARE, n))
        within = contract.MomentWithin("B", "X", tuple(
            contract.MomentGroup(g[0], share=g[1] / chain_moments.unit(chain_moments.SCALE_SHARE, g[0])) for g in groups), 1)
        made = generation._binary_curve_target(entry, within, partner, grid)
        expect = frozen["inputs"][label]
        if not expect["kept"]:
            assert made is None, label
            continue
        assert made is not None, label
        target, statistic = made
        kept += [label]
        assert target.kind == "curve" and statistic.hex() == expect["statistic"] and target.goal.hex() == expect["goal"]
        assert target.aim.hex() == expect["aim"] and target.slope.hex() == expect["slope"]
        assert _digest(target.knots) == expect["knots_sha256"] and _digest(target.encoding) == expect["departures_sha256"]
        assert _digest(target.table) == expect["table_sha256"]
    assert kept == ["bend", "binary_bend"]
    # The yes/no curves are measured and not adopted (G16.3's switch off: on ST1 they invented curve terms), and so are
    # a number's (on ST1 at table seed 2 a curve of age moved the yes/no event polished after it off its ties).
    assert generation._POLISH_BINARY_CURVES is False and generation._POLISH_CURVES is False
    import inspect

    for function in (generation._curve_target, generation._binary_curve_target, generation._bent_feature,
                     generation._curve_value, generation._band_mean_scores, generation._curve_grid):
        used = {word.split("(")[0] for word in inspect.getsource(function).split("math.")[1:]}
        assert used <= {"fsum", "sqrt"}, (function.__name__, used)


@dataclasses.dataclass
class _FakeWalk:
    columns: "dict[str, generation._WalkColumn]"


@pytest.mark.parametrize("case,curve", [("polish_curve", True), ("polish_curve_mutant_none", False)])
def test_the_curve_polish_is_the_oracle_s_round_for_round(case: str, curve: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    """On the oracle's 64-row twin with `Y` given the kept bend as a curve target on `X`: `Y`'s aims after each of its
    re-sorts and the digests of every re-sort's places, aims and `X`'s bands over two rounds are the frozen case's; the
    curve dropped gives the mutant's frozen trail, not the curve's."""
    import test_polish_held_features as held

    oc = _load("oracle_cases")
    frozen = FROZEN[case]
    _n, _columns, _setup, plan, _sums = oc.polish_setup()
    extra = None
    if curve:
        groups, column = oc.polish_curve_inputs()[0][1], oc.polish_curve_inputs()[0][2]
        made = generation._curve_target(_number("Y", column), _within("Y", "X", groups), _bands_ladder("X", [2400] * 5),
                                        generation._curve_grid())
        assert made is not None
        extra = made[0]
    found = _trail(held, monkeypatch, extra)
    assert len(found) == frozen["steps"] == 15
    assert [step["aims"] for step in found if step["column"] == "Y"] == frozen["y_aims"]
    for field in ("index", "aims", "x_bands"):
        assert oc.held_trail_digest(found, field) == frozen[field + "_sha256"], field
    if curve:
        assert frozen["index_sha256"] != FROZEN["polish_curve_mutant_none"]["index_sha256"]


def _trail(held, monkeypatch: pytest.MonkeyPatch, extra: "generation._PolishTarget | None") -> "list[dict[str, object]]":  # type: ignore[no-untyped-def]
    """The oracle's `polish_setup` twin through `_polish_round`, `Y` given `extra` as its last target (none held)."""
    oc = _load("oracle_cases")
    n, columns, setup, plan, sums = oc.polish_setup()
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 2)
    walk_columns = {}
    for name, column_held in columns.items():
        maps = (tuple(column_held["maps"][0]), tuple(column_held["maps"][1]), tuple(column_held["maps"][2]))
        counts = (2, 2, 2) if name == "B" else (8, 8, 4)
        column = generation._WalkColumn(0, 2, maps, counts, ())
        column.index = bytearray(3 * n)
        column.index_width = 3
        for row in range(n):
            chain_walk.write_code(column.index, 3, row, column_held["index"][row])
        column.codes = bytearray(column_held["frame"])
        column.width = 1
        column.slot_l0 = bytearray(column_held["slot_l0"])
        if name == "B":
            column.levels = (0, 1)
        else:
            column.slot_codes = bytearray(column_held["slot_codes"])
            column.slot_has = bytearray(column_held["slot_has"])
            column.slot_rank = bytearray(2 * n)
            for place in range(n):
                chain_walk.write_code(column.slot_rank, 2, place, column_held["slot_rank"][place])
        walk_columns[name] = column
    ranks = {}
    for name, values in setup["ranks"].items():
        packed = bytearray(2 * n)
        for row in range(n):
            chain_walk.write_code(packed, 2, row, values[row])
        ranks[name] = packed
    built = [(name, [held._target(t) for t in listed]) for name, listed in plan]
    if extra is not None:
        for name, targets in built:
            if name == "Y":
                targets += [extra]
    state = generation._PolishState(
        built, n,
        {name: bytearray(values) for name, values in setup["codes"].items() if name != "B"},
        {name: bytearray(values) for name, values in setup["has"].items() if name != "B"},
        ranks, {key: bytes(values) for key, values in setup["bands"].items()},
        {name: (float(pair[0]), float(pair[1])) for name, pair in setup["spreads"].items() if name != "B"},
        [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS))
         for step in range(generation._POLISH_RANK_STEPS)],
        {"B": [("X", 2)]},
    )
    trail: "list[dict[str, object]]" = []
    inner = generation._polish_column

    def recorded(column, name, targets, hidden, held_state, held_walk, moving):  # type: ignore[no-untyped-def]
        inner(column, name, targets, hidden, held_state, held_walk, moving)
        index = column.index
        assert index is not None
        trail.append({"column": name, "index": [chain_walk.read_code(index, 3, row) for row in range(n)],
                      "aims": [t.aim.hex() for t in targets], "x_bands": list(held_state.bands[("X", 1)])})

    monkeypatch.setattr(generation, "_polish_column", recorded)
    turn = 0
    for rnd in range(2):
        for at in range(len(built)):
            hidden = chain_walk.packed(n, chain_walk.SUM_WIDTH)
            for row in range(n):
                chain_walk.put(hidden, row, sums[turn][row])
            generation._polish_round(state, _FakeWalk(walk_columns), at, hidden, rnd)  # type: ignore[arg-type]
            turn += 1
    return trail


# -- THE MECHANISMS ON INVENTED STATES -----------------------------------------------------------------------------

ROWS = 6000


def _ranks_of(values: "list[float]") -> bytearray:
    order = sorted(range(len(values)), key=lambda r: (values[r], r))
    ranks = bytearray(2 * len(values))
    for place, row in enumerate(order):
        code = (generation._POLISH_RANK_STEPS * (2 * place + 1)) // (2 * len(values))
        ranks[2 * row] = code & 255
        ranks[2 * row + 1] = code >> 8
    return ranks


def _quadratic(x: "list[float]", y: "list[float]") -> float:
    """The squared term of the least squares of `y` on `x` and `x ** 2` (the normal equations, solved in order)."""
    rows = [(1.0, a, a * a) for a in x]
    m = [[math.fsum(r[i] * r[j] for r in rows) for j in range(3)] + [math.fsum(r[i] * b for r, b in zip(rows, y))]
         for i in range(3)]
    for i in range(3):
        pivot = m[i][i]
        m[i] = [v / pivot for v in m[i]]
        for k in range(3):
            if k != i:
                factor = m[k][i]
                m[k] = [a - factor * b for a, b in zip(m[k], m[i])]
    return m[2][3]


def _bent(curve: bool, monkeypatch: pytest.MonkeyPatch) -> "tuple[float, float]":
    """`Y = 12 X + 9 (X ** 2 - 1) + 20 e` in codes about 128 (a bend), published as the table holds it: its mean,
    spread and correlation with `X` and its means in `X`'s five equal bands. The walk deals `Y` apart from `X`; the
    polish aims at the correlation and, with `curve`, at the curve the band means show, four rounds in one frame.
    Returns the table's squared term and the twin's."""
    draw = random.Random(20261118)
    x = [draw.gauss(0.0, 1.0) for _row in range(ROWS)]
    y_real = [min(255, max(0, int(round(128 + 12 * a + 9 * (a * a - 1) + 20 * draw.gauss(0.0, 1.0))))) for a in x]
    x_codes = bytearray(min(255, max(0, int(round(128 + 32 * a)))) for a in x)
    order = sorted(range(ROWS), key=lambda r: (x[r], r))
    bands = [0] * ROWS
    for place, row in enumerate(order):
        bands[row] = (5 * place) // ROWS
    n = ROWS
    mean = sum(y_real) / n
    sd = math.sqrt(sum((v - mean) ** 2 for v in y_real) / (n - 1))
    groups = []
    for band in range(5):
        members = [y_real[r] for r in range(n) if bands[r] == band]
        m = sum(members) / len(members)
        s = math.sqrt(sum((v - m) ** 2 for v in members) / (len(members) - 1))
        groups += [[len(members), int(round(10 * m)), int(round(10 * s))]]
    entry = _number("Y", [int(round(10 * mean)), int(round(1000 * sd)), n])
    xs = [float(c) for c in x_codes]
    mx = sum(xs) / n
    r = sum((a - mx) * (b - mean) for a, b in zip(xs, y_real)) / math.sqrt(
        sum((a - mx) ** 2 for a in xs) * sum((b - mean) ** 2 for b in y_real))
    targets = [generation._PolishTarget("pair", "X", r, (), r, 1, most=max(generation._POLISH_AIM_MOST, (1 + abs(r)) / 2))]
    if curve:
        made = generation._curve_target(entry, _within("Y", "X", groups), _bands_ladder("X", [n // 5] * 5),
                                        generation._curve_grid())
        assert made is not None
        targets += [made[0]]
    cells = sorted(y_real)
    perm = list(range(n))
    draw.shuffle(perm)
    column = generation._WalkColumn(0, 0, ((0,), (0,), (0,)), (1, 1, 1), ())
    column.index = bytearray(3 * n)
    column.index_width = 3
    for row in range(n):
        chain_walk.write_code(column.index, 3, row, perm[row])
    column.codes = bytearray(n)
    column.width = 1
    column.slot_l0 = bytearray(n)
    column.slot_codes = bytearray(cells)
    column.slot_has = bytearray(1 for _c in cells)
    column.slot_rank = bytearray(2 * n)
    for place in range(n):
        chain_walk.write_code(column.slot_rank, 2, place, (generation._POLISH_RANK_STEPS * (2 * place + 1)) // (2 * n))
    y_codes = bytearray(cells[perm[row]] for row in range(n))
    y_ranks = bytearray(2 * n)
    for row in range(n):
        code = (generation._POLISH_RANK_STEPS * (2 * perm[row] + 1)) // (2 * n)
        y_ranks[2 * row] = code & 255
        y_ranks[2 * row + 1] = code >> 8
    has = bytearray(1 for _r in range(n))
    state = generation._PolishState(
        [("Y", targets)], n, {"X": x_codes, "Y": y_codes}, {"X": has, "Y": bytearray(has)},
        {"X": _ranks_of(x), "Y": y_ranks}, {},
        {"X": generation._code_spread(x_codes, has), "Y": generation._code_spread(y_codes, has)},
        [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS))
         for step in range(generation._POLISH_RANK_STEPS)], {},
    )
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 4)
    words = random.Random(11)
    for turn in range(4):
        hidden = chain_walk.packed(n, chain_walk.SUM_WIDTH)
        for row in range(n):
            chain_walk.put(hidden, row, sum(words.getrandbits(16) for _k in range(12)))
        generation._polish_round(state, _FakeWalk({"Y": column}), 0, hidden, turn)  # type: ignore[arg-type]
    twin = [float(state.codes["Y"][row]) for row in range(n)]
    real = [float(v) for v in y_real]
    centred = [(a - mx) / 32.0 for a in xs]
    return _quadratic(centred, real), _quadratic(centred, twin)


def test_a_curve_brings_back_a_bend_finer_than_the_bands(monkeypatch: pytest.MonkeyPatch) -> None:
    """A number bending with the square of its partner (squared term 9 codes a squared standard deviation) and dealt
    apart from it by the walk: aimed at its correlation and at the curve its five published band means show, the twin's
    squared term comes back to at least 0.8 of the table's; aimed at its correlation alone (the curves switched off,
    lane CHG's polish), at most a fifth of it."""
    real, with_curve = _bent(True, monkeypatch)
    _real, straight = _bent(False, monkeypatch)
    assert real > 7.0, real
    assert with_curve >= 0.8 * real, (real, with_curve)
    assert straight <= 0.2 * real, (real, straight)


def _levels(whole: bool, monkeypatch: pytest.MonkeyPatch) -> "tuple[list[float], list[float]]":
    """A yes/no column `B` of share 0.2 aimed at its published shares in the five levels of a label `G` (0.05, 0.10,
    0.20, 0.30 and 0.45 on 1,200 rows each, the overall 0.22), dealt by the walk with the shares 0.30, 0.10, 0.10,
    0.30 and 0.30 (the published direction partly met, the others not); its frame one group, four rounds; `whole` the
    whole vector on or off. Returns the published shares and the twin's."""
    n = 6000
    published = [0.05, 0.10, 0.20, 0.30, 0.45]
    walk_shares = [0.30, 0.10, 0.10, 0.30, 0.30]
    level = [row // 1200 for row in range(n)]
    ones = sum(int(round(1200 * s)) for s in walk_shares)
    assert ones == sum(int(round(1200 * s)) for s in published) == 1320
    walk_b = []
    for g in range(5):
        k = int(round(1200 * walk_shares[g]))
        walk_b += [1] * k + [0] * (1200 - k)
    # The walk's cell list: level 0 places first (in the binary's band order), then level 1.
    zeros = [row for row in range(n) if walk_b[row] == 0]
    ones_rows = [row for row in range(n) if walk_b[row] == 1]
    place_of = {}
    for at, row in enumerate(zeros + ones_rows):
        place_of[row] = at
    column = generation._WalkColumn(0, 1, ((0, 1), (0, 1), (0, 1)), (2, 2, 2), ())
    column.index = bytearray(3 * n)
    column.index_width = 3
    for row in range(n):
        chain_walk.write_code(column.index, 3, row, place_of[row])
    column.slot_l0 = bytearray([0] * len(zeros) + [1] * len(ones_rows))
    column.levels = (0, 1)
    share = ones / n
    entry = contract.MomentColumn("B", chain_moments.KIND_BINARY, n, share=share)
    within = contract.MomentWithin("B", "G", tuple(contract.MomentGroup(1200, share=s) for s in published), 1)
    target = generation._share_target(entry, within)
    assert target is not None
    density = generation._normal_density(share)
    target.slope = density / math.sqrt(share * (1.0 - share))
    target.aim = target.goal / target.slope
    monkeypatch.setattr(generation, "_POLISH_WHOLE", whole)
    targets = generation._whole_vectors([target], {"G"}) if whole else [target]
    assert len(targets) == (4 if whole else 1)
    state = generation._PolishState(
        [("B", targets)], n, {}, {}, {}, {("G", 1): bytes(level), ("B", 1): bytes(walk_b)}, {},
        [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS))
         for step in range(generation._POLISH_RANK_STEPS)], {"B": []},
    )
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 4)
    words = random.Random(5)
    for turn in range(4):
        hidden = chain_walk.packed(n, chain_walk.SUM_WIDTH)
        for row in range(n):
            chain_walk.put(hidden, row, sum(words.getrandbits(16) for _k in range(12)))
        generation._polish_round(state, _FakeWalk({"B": column}), 0, hidden, turn)  # type: ignore[arg-type]
    codes = state.codes["B"]
    twin = [sum(codes[row] for row in range(n) if level[row] == g) / 1200 for g in range(5)]
    return published, twin


def test_the_whole_vector_meets_every_level_of_a_label(monkeypatch: pytest.MonkeyPatch) -> None:
    """A yes/no column whose published shares rise over five levels (0.05 to 0.45) and which the walk deals with other
    shares: with the whole vector every level's share is the published one within 0.02; with the one encoding (lane
    CHG's polish) the covariance along it is met but a level misses by more than 0.025 (0.0325 measured: with one
    frame group the score re-sorts the column whole, so the miss is the probit's shape; on the cohort at 20,000 rows,
    where the column's frame keeps the walk's pattern, the misses reach 0.19)."""
    published, whole = _levels(True, monkeypatch)
    _published, single = _levels(False, monkeypatch)
    assert max(abs(a - b) for a, b in zip(published, whole)) <= 0.02, whole
    assert max(abs(a - b) for a, b in zip(published, single)) > 0.025, single
