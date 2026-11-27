"""G16.3's HELD FEATURES (lane CHG-b, plan P4-D492 part b; LANE CHG RULINGS 3 (1)): a yes/no column the grouping gate
still polishes keeps the targets the gate dropped from it, held at the level the walk left.

THE DEFECT IT CLOSES (lane CHG's statistics check, item 1): the gate keeps a yes/no column's split of one number
(an exposure's difference in blood pressure, a strong real effect) and drops its chance targets (its shares in the
bands of age, glucose and the labels, its splits of the other numbers). The polish then re-sorts the column toward
high blood pressure alone, and blood pressure rises with age and glucose, so the twin's exposure takes on age and
glucose: its marginal difference is met (3.95 against the table's 3.91) while its effect after adjusting falls to
0.78 of the table's (3.40 against 4.00; a Cox term 0.21 against 0.28; a rate ratio 0.27 against 0.34).

WHAT IS HELD, each red on its mutant (the held features dropped, lane CHG's polish):
- the gated plan of the oracle's description keeps the three `by` and `share` targets the gate drops from its
  yes/no column, marked held (tests/test_polish_grouping_gate.py, beside the gate's other mutants);
- on the oracle's 64-row twin, with the binary's share target held: the goal and aim set when its first round
  starts, the binary's aims after each of its re-sorts and the digests of every re-sort's places, aims and the
  polished grouping column's bands over two rounds are the frozen case's (`polish_held`), and the held feature
  dropped gives another trail (`polish_held_mutant_dropped`);
- on an invented 6,000-row state (a test size; the mechanism is per row) where a yes/no column weakly tied to a
  number `X` by the walk is re-sorted toward its published split of a number `Y` that rises with `X`: with the
  held feature the column's correlation with `X` stays at the walk's own level and the split is met; with it
  dropped, the column takes on `X` and its effect after adjusting falls; aimed at nought, the walk's tie is erased;
- a held feature never enters a column that keeps no target, nor a number's plan.
"""

import dataclasses
import importlib.util
import json
import math
import pathlib
import random

import pytest

from synthtwin import chain_walk, contract, generation

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = REPOSITORY / "tools" / "reference"
FROZEN = json.loads((REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))["chain"]


def _load(name):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("chgb_" + name, REFERENCE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


@dataclasses.dataclass
class _FakeWalk:
    columns: "dict[str, generation._WalkColumn]"


def _target(t: "dict[str, object]") -> generation._PolishTarget:
    """An oracle target dict as the product's target."""
    return generation._PolishTarget(
        str(t["kind"]), str(t["name"]), float(t["goal"]), tuple(float(v) for v in t["encoding"]),  # type: ignore[union-attr]
        float(t["aim"]), int(t["level"]), tuple(float(v) for v in t.get("sds", [])),  # type: ignore[union-attr, call-overload]
        [float(v) for v in t.get("scales", [])], float(t["slope"]),  # type: ignore[union-attr, call-overload]
        float(t["most"]) if "most" in t else generation._POLISH_AIM_MOST, bool(t.get("held", False)),  # type: ignore[call-overload]
    )


def _product_held(
    held: bool, monkeypatch: pytest.MonkeyPatch, within: bool = False
) -> "tuple[list[list[object]], list[dict[str, object]]]":
    """`generation._polish_round` on the oracle's `polish_setup` with `B`'s share target held (or, the mutant,
    dropped), two rounds in plan order, the second the last: the held goals as set and every re-sort's trail."""
    oc = _load("oracle_cases")
    n, columns, setup, plan, sums = oc.polish_setup()
    for name, listed in plan:
        if name == "B":
            if held:
                listed[1].update(goal=0, aim=0, held=True)
                if within:
                    # ...A HELD `within` TARGET the spread test keeps (batch 4v's outside review, item 6), read over
                    # the column's rows as a `share` target is.
                    listed.append(dict(listed[1], kind="within", sds=[], scales=[]))
            else:
                del listed[1]
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
    walk = _FakeWalk(walk_columns)
    ranks = {}
    for name, values in setup["ranks"].items():
        packed = bytearray(2 * n)
        for row in range(n):
            chain_walk.write_code(packed, 2, row, values[row])
        ranks[name] = packed
    state = generation._PolishState(
        [(name, [_target(t) for t in listed]) for name, listed in plan],
        n,
        {name: bytearray(values) for name, values in setup["codes"].items() if name != "B"},
        {name: bytearray(values) for name, values in setup["has"].items() if name != "B"},
        ranks,
        {key: bytes(values) for key, values in setup["bands"].items()},
        {name: (float(pair[0]), float(pair[1])) for name, pair in setup["spreads"].items() if name != "B"},
        [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS))
         for step in range(generation._POLISH_RANK_STEPS)],
        {"B": [("X", 2)]},
    )
    trail: "list[dict[str, object]]" = []
    goals: "list[list[object]]" = []
    inner = generation._polish_column
    set_goals = generation._held_goals

    def recorded_goals(held_state, name, targets):  # type: ignore[no-untyped-def]
        set_goals(held_state, name, targets)
        goals.append([name, [[t.kind, t.name, t.goal.hex(), t.aim.hex()] for t in targets if t.held]])

    def recorded(column, name, targets, hidden, held_state, held_walk, moving):  # type: ignore[no-untyped-def]
        inner(column, name, targets, hidden, held_state, held_walk, moving)
        index = column.index
        assert index is not None
        trail.append({"column": name, "index": [chain_walk.read_code(index, 3, row) for row in range(n)],
                      "aims": [t.aim.hex() for t in targets], "x_bands": list(held_state.bands[("X", 1)])})

    monkeypatch.setattr(generation, "_polish_column", recorded)
    monkeypatch.setattr(generation, "_held_goals", recorded_goals)
    turn = 0
    for rnd in range(2):
        for at in range(len(plan)):
            hidden = chain_walk.packed(n, chain_walk.SUM_WIDTH)
            for row in range(n):
                chain_walk.put(hidden, row, sums[turn][row])
            generation._polish_round(state, walk, at, hidden, rnd)  # type: ignore[arg-type]
            turn += 1
    return goals, trail


@pytest.mark.parametrize("case,held", [("polish_held", True), ("polish_held_mutant_dropped", False)])
def test_the_held_feature_is_the_oracle_s_round_for_round(case: str, held: bool, monkeypatch: pytest.MonkeyPatch) -> None:
    """On the oracle's 64-row twin with the binary `B`'s share target in `G`'s bands held: the goal and aim
    `_held_goals` sets when `B`'s first round starts are the oracle's bits, and after every re-sort the places, the
    aims and `X`'s `L1` bands are the frozen case's; with the held feature dropped (lane CHG's polish) they are the
    mutant's frozen case's, and that trail is not the held one."""
    goals, found = _product_held(held, monkeypatch)
    frozen = FROZEN[case]
    oc = _load("oracle_cases")
    assert frozen["multiset_kept"] and frozen["b_levels_kept"]
    assert goals == frozen["held_goals"]
    assert len(found) == frozen["steps"] == 15
    assert [step["aims"] for step in found if step["column"] == "B"] == frozen["b_aims"]
    for field in ("index", "aims", "x_bands"):
        assert oc.held_trail_digest(found, field) == frozen[field + "_sha256"], field
    if held:
        assert len(goals) == 1 and len(goals[0][1]) == 1 and float.fromhex(goals[0][1][0][2]) != 0.0
        mutant = FROZEN["polish_held_mutant_dropped"]
        assert mutant["index_sha256"] != frozen["index_sha256"] and mutant["b_aims"] != frozen["b_aims"]
    else:
        assert goals == []


# -- THE MECHANISM ON AN INVENTED STATE ------------------------------------------------------------------------------

ROWS = 6000


def _number_column(values: "list[float]") -> "tuple[bytearray, bytearray, bytearray]":
    """Each row's value code (0 to 255), presence and rank code (two bytes, `generation._POLISH_RANK_STEPS` steps)."""
    codes = bytearray(min(255, max(0, int(128 + 32 * v))) for v in values)
    has = bytearray(1 for _v in values)
    order = sorted(range(len(values)), key=lambda r: (values[r], r))
    ranks = bytearray(2 * len(values))
    for place, row in enumerate(order):
        code = (generation._POLISH_RANK_STEPS * (2 * place + 1)) // (2 * len(values))
        ranks[2 * row] = code & 255
        ranks[2 * row + 1] = code >> 8
    return codes, has, ranks


def _mechanism(held: bool, monkeypatch: pytest.MonkeyPatch) -> "dict[str, float]":
    """The invented state: `X` a number, `Y = 0.6 X + 0.8 e` (both standard), `B` a yes/no column of share 0.3
    drawn apart from both by the walk, its frame one group. `B`'s plan: its published split of `Y` (a difference
    of 0.5 standard deviations, kept) and of `X` (a chance 0.02, which the gate drops: held, or dropped). Four
    rounds of `B`. Returns the twin's correlation of `B` with `X`, `B`'s difference in `Y`, and `B`'s
    coefficient in the least squares of `Y` on `X` and `B`."""
    draw = random.Random(20261117)
    x = [draw.gauss(0.0, 1.0) for _row in range(ROWS)]
    y = [0.6 * a + 0.8 * draw.gauss(0.0, 1.0) for a in x]
    ones = int(0.3 * ROWS)
    b_slots = [0] * (ROWS - ones) + [1] * ones
    # The walk deals `B` with a weak tie to `X` of its own (a latent 0.08 X plus noise, its highest 30 per cent at
    # level one): the level a held feature keeps, which a target aimed at nought would erase.
    latent = sorted(range(ROWS), key=lambda r: (0.08 * x[r] + draw.gauss(0.0, 1.0), r))
    zeros_places = list(range(ROWS - ones))
    ones_places = list(range(ROWS - ones, ROWS))
    draw.shuffle(zeros_places)
    draw.shuffle(ones_places)
    perm = [0] * ROWS
    for at, row in enumerate(latent):
        perm[row] = zeros_places[at] if at < ROWS - ones else ones_places[at - (ROWS - ones)]
    column = generation._WalkColumn(0, 1, ((0, 1), (0, 1), (0, 1)), (2, 2, 2), ())
    column.index = bytearray(3 * ROWS)
    column.index_width = 3
    for row in range(ROWS):
        chain_walk.write_code(column.index, 3, row, perm[row])
    column.slot_l0 = bytearray(b_slots)
    column.levels = (0, 1)
    walk = _FakeWalk({"B": column})
    x_codes, x_has, x_ranks = _number_column(x)
    y_codes, y_has, y_ranks = _number_column(y)
    share = 0.3
    density = generation._normal_density(share)

    def split_target(name: str, difference: float, keep_held: bool) -> generation._PolishTarget:
        encoding = (-share * difference, (1.0 - share) * difference)
        goal = share * (1.0 - share) * difference * difference
        slope = difference * density
        return generation._PolishTarget("by", name, 0.0 if keep_held else goal, encoding,
                                        0.0 if keep_held else goal / slope, 1, (), [1.0, 1.0], slope,
                                        held=keep_held)

    targets = [split_target("Y", 0.5, False)]
    if held:
        targets += [split_target("X", 0.02, True)]
    b_bands = bytes(b_slots[perm[row]] for row in range(ROWS))
    state = generation._PolishState(
        [("B", targets)], ROWS,
        {"X": x_codes, "Y": y_codes}, {"X": x_has, "Y": y_has}, {"X": x_ranks, "Y": y_ranks},
        {("B", 1): b_bands},
        {"X": generation._code_spread(x_codes, x_has), "Y": generation._code_spread(y_codes, y_has)},
        [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS))
         for step in range(generation._POLISH_RANK_STEPS)],
        {"B": []},
    )
    walk_b = [float(b_slots[perm[row]]) for row in range(ROWS)]
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 4)
    words = random.Random(7)
    for turn in range(4):
        hidden = chain_walk.packed(ROWS, chain_walk.SUM_WIDTH)
        for row in range(ROWS):
            chain_walk.put(hidden, row, sum(words.getrandbits(16) for _k in range(12)))
        generation._polish_round(state, walk, 0, hidden, turn)  # type: ignore[arg-type]
    b = [float(state.codes["B"][row]) for row in range(ROWS)]
    xs = [float(c) for c in x_codes]
    ys = [float(c) for c in y_codes]

    def centred(values: "list[float]") -> "list[float]":
        mean = math.fsum(values) / len(values)
        return [v - mean for v in values]

    cb, cx, cy = centred(b), centred(xs), centred(ys)
    sbb, sxx = math.fsum(v * v for v in cb), math.fsum(v * v for v in cx)
    sbx, sby, sxy = math.fsum(p * q for p, q in zip(cb, cx)), math.fsum(p * q for p, q in zip(cb, cy)), math.fsum(
        p * q for p, q in zip(cx, cy))
    adjusted = (sby * sxx - sbx * sxy) / (sbb * sxx - sbx * sbx)
    cw = centred(walk_b)
    walk_corr = math.fsum(p * q for p, q in zip(cw, cx)) / math.sqrt(math.fsum(v * v for v in cw) * sxx)
    ones_y = [ys[r] for r in range(ROWS) if b[r] == 1.0]
    zeros_y = [ys[r] for r in range(ROWS) if b[r] == 0.0]
    return {"corr_bx": sbx / math.sqrt(sbb * sxx), "walk_corr_bx": walk_corr,
            "difference": math.fsum(ones_y) / len(ones_y) - math.fsum(zeros_y) / len(zeros_y),
            "adjusted": adjusted, "ones": float(sum(1 for v in b if v == 1.0))}


def test_a_held_feature_keeps_the_column_off_the_other_causes_of_what_it_is_sorted_toward(
        monkeypatch: pytest.MonkeyPatch) -> None:
    """A yes/no column re-sorted toward its published split of `Y` (half a standard deviation, 16 codes), with `Y`
    rising with `X` (correlation 0.6) and the column tied to `X` by the walk only weakly (about 0.064): WITH the
    dropped split of `X` held, the twin's correlation of the column with `X` stays at the walk's own (within 0.01:
    measured 0.0648 against 0.0636), the split of `Y` is the published one within a tenth, and the coefficient
    after adjusting for `X` is the walk's tie's (13.35 of a 15.95 split); DROPPED (lane CHG's polish), the column
    takes on `X` (0.131, more than 0.05 over the walk's) and its adjusted coefficient falls (10.80, under 0.85 of
    the held twin's); a held feature aimed at nought (the goal never set from the walk, the ruled mutant) erases
    the walk's own tie instead (0.0002) and fails the first clause. The column keeps its 1,800 rows of level one."""
    with_held = _mechanism(True, monkeypatch)
    without = _mechanism(False, monkeypatch)
    published = 0.5 * 32.0
    assert with_held["ones"] == without["ones"] == 1800.0
    assert abs(with_held["corr_bx"] - with_held["walk_corr_bx"]) < 0.01, with_held
    assert abs(with_held["difference"] - published) <= 0.1 * published, with_held
    assert without["corr_bx"] - without["walk_corr_bx"] > 0.05, without
    assert without["adjusted"] < 0.85 * with_held["adjusted"], (with_held, without)


def test_no_feature_is_held_for_a_number_or_a_column_the_gate_leaves_with_nothing(monkeypatch: pytest.MonkeyPatch) -> None:
    """The oracle's description with every grouping target beyond chance removed from the yes/no column `F` leaves `F`
    out of the plan whole (no held feature without a kept target), and no number of the plan holds one."""
    import test_polish_grouping_gate as gate

    described = gate._gate_profile()
    moments = described.relationships.moments
    assert moments is not None
    quiet = tuple(w for w in moments.within if not (w.column == "F" and w.by == "B") and not (w.column == "C" and w.by == "F"))
    changed = dataclasses.replace(described.relationships, moments=dataclasses.replace(moments, within=quiet))
    plan = generation._polish_layout(gate._Profile(changed)).plan  # type: ignore[arg-type]
    assert "F" not in {name for name, _targets in plan}
    full = generation._polish_layout(described).plan  # type: ignore[arg-type]
    for name, targets in full:
        assert name == "F" or not any(t.held for t in targets), name
    assert isinstance(described.relationships, contract.RelationshipManifest)


def test_a_held_within_target_is_the_oracle_s_goal_and_aim(monkeypatch: pytest.MonkeyPatch) -> None:
    """Batch 4v's outside review, item 6: the product's `_held_goals` reads a held `within` target as a `share` target
    (the spread test's kept spread of a number); the oracle deleted it. On the 64-row twin with a held `within` target
    beside the share target, the goal and aim the oracle sets are the product's bits, and the oracle keeps both
    targets. Red where the oracle reads only `share` and `by` (it then leaves one target and no goal for the other)."""
    goals, _found = _product_held(True, monkeypatch, within=True)
    oc = _load("oracle_cases")
    n, _columns, state, plan, _sums = oc.polish_setup()
    oracle = _load("chain_oracle")
    for name, listed in plan:
        if name == "B":
            listed[1].update(goal=oracle.F(0), aim=oracle.F(0), held=True)
            listed.append(dict(listed[1], kind="within", sds=[], scales=[]))
            oracle.held_goals(name, listed, state)
            found = [[t["kind"], t["name"], oracle.b64_hex(t["goal"]), oracle.b64_hex(t["aim"])] for t in listed if t.get("held")]
    assert len(found) == 2 and len(goals) == 1 and len(goals[0][1]) == 2
    assert goals[0][1] == found
    assert goals[0][1][0][2] == goals[0][1][1][2]
