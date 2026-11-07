"""The twin meets rule B (lane MPg, plan P4-D456): G16.2 step 2's implied slope and G16.3's polish.

WHAT IS HELD, each red on its mutant:
- the walk's arithmetic is written out: the logarithm and the normal
  quantile in `+ - * /` and `sqrt` agree with the library's to 1e-8, and
  `chain_walk` calls no other `math` function;
- the implied slope mirrors the chain oracle (A-P4-59): each family's
  coefficients, spread, cell means and every row's latent order are the
  frozen vectors' to the last bit (`walk40_implied`), and the walk under it
  deals other rows than the walk by hidden scores alone (its mutant, also
  frozen); the 20,000-row arrangement case of
  tests/test_stage6_chain_generate.py holds the whole product to the
  oracle's walk with it;
- the polish mirrors the oracle (repair 1): on a 64-row twin of three
  numbers, a binary and a grouping column, after every re-sort of every
  round the places, aims, spread factors and the polished grouping
  column's bands are the frozen case's (`polish`), and its mutants (each
  row kept in its `L0` band; the aims never moved; a moved column's bands
  never read again; no band's spread scaled; the aims never scaled
  together) give theirs and not the polish's; the projection of goals no
  data can hold is the oracle's to the bit (`psd_projection`);
- the plan reads the description alone: a number's means in a correlated
  partner's bands are no target, a binary with both levels published is
  aimed at a number's split by it and at its shares at its threshold's
  slopes, the goals come from the projected matrix, and a round runs from
  the finest frame to the coarsest; a correlation's aim stays inside
  0.999, or for a pair half way from its goal to 1 past it (repair 2);
- repair 2: a binary's frame key stays exact past four bytes (a helper
  case and a clinic twin with every key column widened by 2 ** 32); an
  implied slope that fits nothing is the oracle's (frozen at 20 rows a
  cell and at the floor); K-S6-13's projected hours read OPEN-held off the
  quiet machine; only a common row set is projected, an unpublished pair is
  no goal, the goals of Codex's two probes keep their published 0.9 (the
  twin misses them: limit (g), plan P4-D456), and a number aims at its 24
  largest published correlations (all to the oracle's bits); an
  incomplete pair's own spreads reach the polish and K-S6-12's driver, and
  at 21,000 rows the twin's complete-case slope is the real one where the
  frame holds it and nearer the real one than with the spreads dropped;
- on a product twin: every band a target reads is read again after each
  round (a polished number at chain level `L2` grouping another), each
  polished row's code is the chain's reading of its cell, the rounds are
  eight; G1 and HIPAA first: every column keeps its multiset of cells and
  its blanks, a held identifier column and a two-valued column with a held
  level keep their bytes, every family table and band total still reads
  HELD in validation, the plan counts every word, and the twin is the same
  bytes at the same seed; through `synthtwin profile` at 20,000 rows a
  top-coded age moves only among its own cells, so no twin age exceeds 90,
  and the held record key keeps its bytes and equals no real key;
- the published correlations are nearer on the polished twin than on the
  walk's, and on the invented table of two nearly collinear pairs at
  20,000 rows the 0.995 pair's correlation on codes comes back within
  K-S6-12's bound and the 0.95 pair, a stated limit there, closes at least
  half of the walk's gap (mutant: the polish off);
- repair 4 (LANE MPg RULINGS 14 (3)): the polish's sort, held to a plain
  sort of (score, row) tuples on a 20,000-row twin and its ties to the
  lower row, stands in tests/test_moment_polish_sort.py, a file of its own
  because this one passed 180 CPU seconds with it (LANE MPg RULINGS 13 (2)).
"""

import dataclasses
import fractions
import hashlib
import importlib.util
import json
import math
import pathlib
import random
import statistics

import chain_twins
import fixtures
import pytest

from synthtwin import asking, chain, chain_moments, chain_walk, cli, contract, generation, profile, reading, taxonomy, twinstore

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
REFERENCE = REPOSITORY / "tools" / "reference"
FROZEN = json.loads((REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))["chain"]


def _load(name):  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("mpg_" + name, REFERENCE / (name + ".py"))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def _float(text: "str | None") -> "float | None":
    return None if text is None else float.fromhex(text)


# -- THE ARITHMETIC THE WALK WRITES OUT ----------------------------------------


def test_the_normal_quantile_and_the_logarithm_are_written_out() -> None:
    """`chain_walk.normal_score` and `natural_log` against the standard library to 1e-8 and 1e-15,
    and `chain_walk` reaches `math` only for `frexp` and `sqrt` (zone G's set)."""
    normal = statistics.NormalDist()
    worst = max(abs(chain_walk.normal_score(k / 4001) - normal.inv_cdf(k / 4001)) for k in range(1, 4001))
    assert worst < 1e-8
    assert abs(chain_walk.normal_score(2.5e-7) - normal.inv_cdf(2.5e-7)) < 1e-8
    for x in (1e-300, 2.5e-7, 0.02425, 0.5, 0.7071067811865476, 1.0):
        assert abs(chain_walk.natural_log(x) - math.log(x)) <= 1e-15 * max(1.0, abs(math.log(x)))
    source = (REPOSITORY / "src" / "synthtwin" / "chain_walk.py").read_text(encoding="utf-8")
    used = {word.split("(")[0] for word in source.split("math.")[1:] if "(" in word.split()[0]}
    assert used <= {"frexp", "sqrt"}, used
    with pytest.raises(ValueError):
        chain_walk.normal_score(1.0)


# -- THE IMPLIED SLOPE AGAINST THE ORACLE (A-P4-59) ------------------------------


def test_the_implied_slope_is_the_oracle_s_to_the_last_bit() -> None:
    """Each family of the frozen 40-row walk: the product's band scores, `implied_slope` and
    `implied_latent` on the same published table, ranks and hidden sums give the oracle's bits;
    the walk under it is met and deals other rows than the walk by hidden scores alone."""
    case = FROZEN["walk40_implied"]
    mutant = FROZEN["walk40_implied_mutant_hidden_score_only"]
    assert all(case["met"]) and all(mutant["met"])
    assert case["index"] != mutant["index"]
    for fi, family in case["families"].items():
        computed = [chain_walk.band_scores(totals, valued) for totals, valued in family["level_totals"].values()]
        frozen = family["parent_scores"] + [family["child_scores"]]
        assert [[None if v is None else v.hex() for v in row] for row in computed] == frozen, fi
        parent_scores = [[_float(v) for v in row] for row in family["parent_scores"]]
        slope = chain_walk.implied_slope(
            tuple(tuple(row) for row in family["table"]), family["sizes"], parent_scores, family["used"],
            [_float(v) for v in family["child_scores"]],
        )
        assert [b.hex() for b in slope.beta] == family["beta"], fi
        assert slope.sigma.hex() == family["sigma"], fi
        assert [None if m is None else m.hex() for m in slope.means] == family["means"], fi
        names = ["X", "Y"]
        ranks = []
        for at in family["used"]:
            name = names[at]
            held = chain_walk.packed(40, 1)
            for row in range(40):
                rank = case["ranks"][name][row]
                chain_walk.put(held, row, case["readings"][name] if rank is None else rank)
            ranks += [(held, case["readings"][name])]
        latent = chain_walk.implied_latent(family["cells"], slope, ranks, family["sums"])
        assert [x.hex() for x in latent] == family["latent"], fi


@pytest.mark.parametrize("case", ["implied_nofit", "implied_nofit_floor"])
def test_an_implied_slope_that_fits_nothing_is_the_oracle_s(case: str) -> None:
    """Repair 2 (Codex's item 4, LANE MPg RULINGS 9 (4)): a family whose published cells never hold a reading
    of every used parent (table ((0, 20), (20, 0)), parent scores (None, 0), child scores (None, 0), one ranged
    parent; and the same at 10,000 a cell, the floor's 20,000 rows) fits no coefficient, and every row's latent
    order is `sigma z + mu_c`: the product's and the oracle's frozen values agree to the bit (the oracle had
    read a coefficient it never fitted and raised IndexError)."""
    frozen = FROZEN[case]
    oc = _load("oracle_cases")
    half = frozen["half"]
    table, cells, ranks, sums = oc.implied_nofit_inputs(half)
    slope = chain_walk.implied_slope(tuple(tuple(row) for row in table), [2], [[None, 0.0]], [0], [None, 0.0])
    assert [b.hex() for b in slope.beta] == frozen["beta"] == []
    assert slope.sigma.hex() == frozen["sigma"]
    assert [None if m is None else m.hex() for m in slope.means] == frozen["means"]
    held = chain_walk.packed(2 * half, 2)
    for row in range(2 * half):
        chain_walk.put(held, row, half if ranks[row] is None else ranks[row])
    latent = [x.hex() for x in chain_walk.implied_latent(cells, slope, [(held, half)], sums)]
    if "latent" in frozen:
        assert latent == frozen["latent"]
    else:
        assert len(latent) == frozen["count"] and latent[:4] == frozen["head"]
        assert hashlib.sha256(",".join(latent).encode("ascii")).hexdigest() == frozen["sha256"]


# -- THE POLISH AGAINST THE ORACLE ------------------------------------------------


def _product_polish(
    frame_l0: bool, adjust: bool, spreads: bool, monkeypatch: pytest.MonkeyPatch, feasible: bool = True
) -> "list[dict[str, object]]":
    """`generation._polish_round` on the oracle's `polish_setup`, two rounds in plan order (the second the last)."""
    oc = _load("oracle_cases")
    n, columns, setup, plan, sums = oc.polish_setup()
    # The shipped switches stand for the polish's own case, so a changed default is red there.
    if frame_l0:
        monkeypatch.setattr(generation, "_POLISH_FRAME_L0", True)
    if not spreads:
        monkeypatch.setattr(generation, "_POLISH_SPREADS", False)
    if not feasible:
        monkeypatch.setattr(generation, "_POLISH_FEASIBLE", False)
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 2)
    walk_columns = {}
    for name, held in columns.items():
        maps = (tuple(held["maps"][0]), tuple(held["maps"][1]), tuple(held["maps"][2]))
        counts = (2, 2, 2) if name == "B" else (8, 8, 4)
        column = generation._WalkColumn(0, 2, maps, counts, ())
        column.index = bytearray(3 * n)
        column.index_width = 3
        for row in range(n):
            chain_walk.write_code(column.index, 3, row, held["index"][row])
        column.codes = bytearray(held["frame"])
        column.width = 1
        column.slot_l0 = bytearray(held["slot_l0"])
        if name == "B":
            column.levels = (0, 1)
        else:
            column.slot_codes = bytearray(held["slot_codes"])
            column.slot_has = bytearray(held["slot_has"])
            column.slot_rank = bytearray(2 * n)
            for place in range(n):
                chain_walk.write_code(column.slot_rank, 2, place, held["slot_rank"][place])
        walk_columns[name] = column

    @dataclasses.dataclass
    class _FakeWalk:
        columns: "dict[str, generation._WalkColumn]"

    walk = _FakeWalk(walk_columns)
    ranks = {}
    for name, values in setup["ranks"].items():
        packed = bytearray(2 * n)
        for row in range(n):
            chain_walk.write_code(packed, 2, row, values[row])
        ranks[name] = packed
    state = generation._PolishState(
        [(name, [
            generation._PolishTarget(
                t["kind"], t["name"], float(t["goal"]), tuple(float(v) for v in t["encoding"]), float(t["aim"]), t["level"],
                tuple(float(v) for v in t.get("sds", [])), [float(v) for v in t.get("scales", [])], float(t["slope"]),
                float(t["most"]) if "most" in t else generation._POLISH_AIM_MOST,
            )
            for t in listed
        ]) for name, listed in plan],
        n,
        {name: bytearray(values) for name, values in setup["codes"].items() if name != "B"},
        {name: bytearray(values) for name, values in setup["has"].items() if name != "B"},
        ranks,
        {key: bytes(values) for key, values in setup["bands"].items()},
        {name: (float(pair[0]), float(pair[1])) for name, pair in setup["spreads"].items() if name != "B"},
        [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS)) for step in range(generation._POLISH_RANK_STEPS)],
        {"B": [("X", 2)]},
    )
    trail: "list[dict[str, object]]" = []
    inner = generation._polish_column

    def recorded(column, name, targets, hidden, held_state, held_walk, moving):  # type: ignore[no-untyped-def]
        if not adjust:
            moving = False
        inner(column, name, targets, hidden, held_state, held_walk, moving)
        index = column.index
        assert index is not None
        trail.extend([{
            "column": name,
            "index": [chain_walk.read_code(index, 3, row) for row in range(n)],
            "aims": [t.aim.hex() for t in targets],
            "scales": [[v.hex() for v in t.scales] for t in targets],
            "x_bands": list(held_state.bands[("X", 1)]),
        }])

    monkeypatch.setattr(generation, "_polish_column", recorded)
    turn = 0
    for rnd in range(2):
        for at in range(len(plan)):
            hidden = chain_walk.packed(n, chain_walk.SUM_WIDTH)
            for row in range(n):
                chain_walk.put(hidden, row, sums[turn][row])
            generation._polish_round(state, walk, at, hidden, rnd)  # type: ignore[arg-type]
            turn += 1
    return trail


@pytest.mark.parametrize(
    "case,frame_l0,adjust,spreads,feasible",
    [
        ("polish", False, True, True, True),
        ("polish_mutant_l0_frame", True, True, True, True),
        ("polish_mutant_aims_fixed", False, False, True, True),
        ("polish_mutant_no_spreads", False, True, False, True),
        ("polish_mutant_aims_apart", False, True, True, False),
    ],
)
def test_the_polish_is_the_oracle_s_round_for_round(
    case: str, frame_l0: bool, adjust: bool, spreads: bool, feasible: bool, monkeypatch: pytest.MonkeyPatch
) -> None:
    """G16.3 on the oracle's 64-row twin (three numbers, a binary, a grouping column): after every
    re-sort, the product's places, aims, spread factors and the polished grouping column `X`'s `L1`
    bands are the frozen case's, and each mutant's are its own and not the polish's; the frozen mutant
    whose moved column's bands are never read again (stale) is not the polish either, `X`'s bands as the
    product reads them are the bands of its places, and the binary keeps its 24 rows of level 1."""
    found = _product_polish(frame_l0, adjust, spreads, monkeypatch, feasible)
    frozen = FROZEN[case]
    assert frozen["multiset_kept"] and frozen["b_levels_kept"]
    assert [step["column"] for step in found] == [step["column"] for step in frozen["trail"]]
    assert [step["index"] for step in found] == [step["index"] for step in frozen["trail"]]
    assert [step["aims"] for step in found] == [step["aims"] for step in frozen["trail"]]
    assert [step["scales"] for step in found] == [step["scales"] for step in frozen["trail"]]
    assert [step["x_bands"] for step in found] == [step["x_bands"] for step in frozen["trail"]]
    if case != "polish":
        assert frozen["trail"] != FROZEN["polish"]["trail"]
    else:
        stale = FROZEN["polish_mutant_stale_bands"]["trail"]
        assert [step["index"] for step in stale] != [step["index"] for step in frozen["trail"]]
        assert stale[-1]["x_bands"] != frozen["trail"][-1]["x_bands"]
        x_places = [step["index"] for step in found if step["column"] == "X"][-1]
        assert found[-1]["x_bands"] == [(8 * place) // 64 for place in x_places]


def test_the_psd_projection_is_the_oracle_s_to_the_last_bit() -> None:
    """LANE MPg RULINGS 2 (2): the polish's correlation goals projected to the nearest positive
    semidefinite matrix where they are not one (the cyclic Jacobi method, each eigenvalue under 1e-4
    set to it, the diagonal rescaled to 1): the product's projected matrix, least eigenvalue and largest
    change are the oracle's frozen bits on two impossible matrices, and a positive definite one (the
    probe's near pair) comes back unchanged."""
    cases = FROZEN["psd_projection"]
    for case in cases:
        matrix = [[float.fromhex(x) for x in row] for row in case["matrix"]]
        projected, least, change = generation._nearest_correlations(matrix)
        assert [[x.hex() for x in row] for row in projected] == case["projected"]
        assert least.hex() == case["least"] and change.hex() == case["change"]
        values, _vectors = generation._jacobi(projected)
        assert min(values) > 0.0
    assert float.fromhex(cases[0]["least"]) < 0.0 < float.fromhex(cases[0]["change"])
    assert float.fromhex(cases[2]["change"]) == 0.0


# -- G1 AND HIPAA FIRST ON A PRODUCT TWIN ------------------------------------------


def _rows(n_rows: int = 2000, seed: int = 11) -> "list[list[str]]":
    """An invented clinic with a record key, blanks in two measurements and two label columns."""
    draw = random.Random(seed)
    rows = []
    for place in range(n_rows):
        age = draw.randint(18, 90)
        gender = draw.choice(["f", "m"])
        group = draw.choice(["a", "b", "c"]) if age < 50 else draw.choice(["c", "d"])
        pressure = "" if draw.random() < 0.06 else f"{round(100 + age * 0.5 + draw.gauss(0, 8), 1)}"
        lab = "" if draw.random() < 0.04 else f"{round(3 + 0.02 * age + (0.6 if gender == 'm' else 0) + draw.gauss(0, 1), 2)}"
        event = "1" if draw.random() < 0.05 + age / 120 else "0"
        rows += [[f"{age}", gender, group, pressure, lab, event]]
    return rows


@pytest.fixture(scope="module", autouse=True)
def _the_small_table_refusal_off_for_the_module_s_fixtures():  # type: ignore[no-untyped-def]
    """The suite's default without the table floor (tests/conftest.py), set before the module's own fixture."""
    with pytest.MonkeyPatch.context() as own:
        own.setitem(cli.main.__kwdefaults__, "small_tables_refused", False)
        own.setitem(cli.run.__kwdefaults__, "small_tables_refused", False)
        yield


@pytest.fixture(scope="module")
def clinic(tmp_path_factory):  # type: ignore[no-untyped-def]
    with pytest.MonkeyPatch.context() as patch:
        folder = tmp_path_factory.mktemp("polish")
        for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
            patch.setenv(name, str(folder / "home"))
        yield chain_twins.Described(folder, ["age", "gender", "group", "pressure", "lab", "event"], _rows())


def _columns(twin: "generation.Twin") -> "list[list[str]]":
    return [list(generation.twin_column(twin, at)) for at in range(len(twin.names))]


def _correlations(described: "chain_twins.Described", columns: "list[list[str]]") -> "list[float]":
    """Each published pair's gap |r_twin - r_published| on the twin's cells read as numbers."""
    moments = described.statistical["moments"]
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    names = described.header
    gaps = []
    for i, row in enumerate(moments["correlations"]):
        for j, pair in enumerate(row):
            if pair is None:
                continue
            a = columns[names.index(numbers[i])]
            b = columns[names.index(numbers[j])]
            both = [(float(x), float(y)) for x, y in zip(a, b) if x != "" and y != ""]
            gaps += [abs(statistics.correlation([x for x, _ in both], [y for _, y in both]) - pair[0] / 10**12)]
    return gaps


def test_the_polish_keeps_every_cell_blank_and_table(clinic, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """The shipped twin against the twin with the polish off (the same seed, so the same cells and
    the same walk): each column the same multiset of cells and the same blank rows; a column the
    polish does not move the same bytes; validation reads every band total and family HELD; the
    plan counts every word; the same seed the same bytes; the published correlations nearer."""
    loaded = contract.load_profile(str(clinic.path), chain=True)
    assert loaded.relationships.moments is not None
    planned = generation._polish_plan(loaded)
    polished = [name for name, _targets in planned]
    assert set(polished) == {"age", "pressure", "lab", "gender", "event"}, polished
    shipped = generation.generate_held(loaded, 3)
    again = generation.generate_held(loaded, 3)
    assert _columns(shipped) == _columns(again)
    assert generation.plan_generation(loaded).words_planned == shipped.words_drawn
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 0)
    walked = generation.generate_held(loaded, 3)
    monkeypatch.undo()
    names = list(shipped.names)
    moved = _columns(shipped)
    before = _columns(walked)
    for at, name in enumerate(names):
        assert sorted(moved[at]) == sorted(before[at]), name
        assert [cell == "" for cell in moved[at]] == [cell == "" for cell in before[at]], name
        if name not in polished:
            assert moved[at] == before[at], name
        else:
            assert moved[at] != before[at], name
    rows = [[moved[at][r] for at in range(len(names))] for r in range(len(moved[0]))]
    code, report, _screen = clinic.validate(rows)
    totals, families = chain_twins._verdicts(report)
    assert set(totals.values()) == {"HELD"} and set(families.values()) == {"HELD"}, (totals, families)
    assert code == 0
    after = _correlations(clinic, moved)
    walk = _correlations(clinic, before)
    assert after and sum(after) < 0.8 * sum(walk), (after, walk)


def test_the_rounds_read_fresh_bands_and_the_chain_s_codes(clinic, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """G16.3 on the clinic, whose `pressure` is polished at chain level `L2` and groups `age` by its
    `L1` bands (the plan made to read a number's means in a partner's bands): after every round, each
    band a target reads is the band of the column's places at the
    target's level (`maps[level]` of each place's `L0` band), read here apart (mutants: the bands never
    read again after a round; the `L0` band read for the `L1`); after the last round each polished
    column's code on every row is the chain's reading of the cell the row holds (contract 4.6d.1:
    `linear_code` on the published clip; mutant: another clip); and the rounds are G16.3's eight, each
    polished column once a round (mutant: one round)."""
    # The shipped plan reads no number's means in the bands of a partner it is correlated with
    # (repair 1); here they are read, so a polished number at chain level L2 groups another.
    monkeypatch.setattr(generation, "_POLISH_WITHIN_PARTNERS", True)
    loaded = contract.load_profile(str(clinic.path), chain=True)
    planned = generation._polish_plan(loaded)
    assert any(t.kind == "within" and t.name == "pressure" and t.level == 1 for _n, ts in planned for t in ts)
    block_of = {block["name"]: block for block in json.loads(clinic.path.read_text(encoding="utf-8"))["columns"]}
    calls: "list[str]" = []
    checked: "list[tuple[str, object]]" = []
    held_state: "list[generation._PolishState]" = []
    inner = generation._polish_round
    placed = generation._polish_placed

    def fresh(column: "generation._WalkColumn", level: int, rows: int) -> "list[int]":
        index, slot_l0 = column.index, column.slot_l0
        assert index is not None and slot_l0 is not None
        return [
            column.maps[level][chain_walk.read_code(slot_l0, column.l0_width, chain_walk.read_code(index, column.index_width, row))]
            for row in range(rows)
        ]

    def counted(state, walk, at, sums, turn):  # type: ignore[no-untyped-def]
        inner(state, walk, at, sums, turn)
        calls.extend([state.plan[at][0]])
        for (name, level), held in state.bands.items():
            assert list(held) == fresh(walk.columns[name], level, state.rows), (name, level, turn)
            checked.extend([(name, level)])

    def counted_state(state, walk, at, sums, turn):  # type: ignore[no-untyped-def]
        counted(state, walk, at, sums, turn)
        held_state.extend([state])

    def read_back(walk, finished, arranging, sheet_dealt):  # type: ignore[no-untyped-def]
        placed(walk, finished, arranging, sheet_dealt)
        state = held_state[-1]
        for name, _targets in state.plan:
            if name not in state.ranks:
                continue
            column = walk.columns[name]
            found = chain_moments.codes_of(block_of[name])
            assert found is not None
            cells = twinstore.column_cells(finished[column.step])
            for at in range(state.rows):
                cell = cells[chain_walk.item(walk.arranged, at)]
                if state.has[name][at]:
                    assert state.codes[name][at] == chain_moments.linear_code(found, fractions.Fraction(float(cell))), (name, at)
                else:
                    assert cell == "", (name, at)
            checked.extend([(name, "codes")])

    monkeypatch.setattr(generation, "_polish_round", counted_state)
    monkeypatch.setattr(generation, "_polish_placed", read_back)
    generation.generate_held(loaded, 5)
    assert calls == [name for name, _targets in planned] * 8
    assert ("pressure", 1) in checked
    assert {(name, "codes") for name, _targets in planned if name in ("age", "pressure", "lab")} <= set(checked)


def test_a_held_identifier_column_never_moves(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """HIPAA first: a record key held by the chain's switch is no moment column and groups nothing,
    so the polish moves none of its cells: its twin column is the same bytes with the polish on and
    off, and so is every column the polish does not name."""
    rows = [[f"R{100000 + place}"] + row for place, row in enumerate(_rows(1500, 13))]
    text = "record,age,gender,group,pressure,lab,event\n" + "".join(",".join(row) + "\n" for row in rows)
    source = tmp_path / "held.csv"
    source.write_text(text, encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(source), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("held", bytes(range(32)), ("record",), rows_per_person=chain.ROWS_UNASKED))
    assert chained.statistical is not None and chained.statistical["moments"] is not None
    written = dict(document)
    written["relationships"] = dict(written["relationships"], statistical=chained.statistical)
    path = fixtures.write_profile(tmp_path, "held-profile.json", written)
    loaded = contract.load_profile(str(path), chain=True)
    moments = loaded.relationships.moments
    assert moments is not None
    assert "record" not in [entry.column for entry in moments.columns] + [entry.by for entry in moments.within]
    polished = [name for name, _targets in generation._polish_plan(loaded)]
    assert polished and "record" not in polished
    shipped = generation.generate_held(loaded, 1)
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 0)
    walked = generation.generate_held(loaded, 1)
    for at, name in enumerate(loaded.columns):
        if name.name not in polished:
            assert list(generation.twin_column(shipped, at)) == list(generation.twin_column(walked, at)), name.name


def test_a_two_valued_column_with_a_held_level_never_moves(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """HIPAA first: a two-valued column beside a third level on 7 rows (held back, under the floor) is no
    binary of rule B, so no moment names it and the polish re-assigns none of its cells: its twin column
    is the same bytes with the polish on and off, while the binary beside it, both levels published, is
    re-assigned (repair 1)."""
    draw = random.Random(23)
    rows = []
    for place, row in enumerate(_rows(2000, 29)):
        flag = "9" if place % 300 == 5 else ("1" if draw.random() < 0.3 + float(row[0]) / 300 else "0")
        rows += [row + [flag]]
    assert sum(1 for row in rows if row[-1] == "9") == 7
    described = chain_twins.Described(tmp_path, ["age", "gender", "group", "pressure", "lab", "event", "flag"], rows)
    loaded = contract.load_profile(str(described.path), chain=True)
    moments = loaded.relationships.moments
    assert moments is not None
    assert "flag" not in [entry.column for entry in moments.columns]
    polished = [name for name, _targets in generation._polish_plan(loaded)]
    assert "event" in polished and "flag" not in polished, polished
    shipped = generation.generate_held(loaded, 4)
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 0)
    walked = generation.generate_held(loaded, 4)
    names = [column.name for column in loaded.columns]
    assert list(generation.twin_column(shipped, names.index("flag"))) == list(generation.twin_column(walked, names.index("flag")))
    assert list(generation.twin_column(shipped, names.index("event"))) != list(generation.twin_column(walked, names.index("event")))


def test_two_nearly_collinear_pairs_come_back_within_their_bound(tmp_path, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """Lane MPg's skeptic 1, item 1 (one case at 20,000 rows): on the invented table of two pairs whose
    correlation on the chain's codes is about 0.95 and about 0.995 (tests/moment_polish_tables.py), the
    shipped twin's correlation on codes lies within K-S6-12's bound of the published one for the 0.995 pair
    (half a step of Fisher's z read on r plus twice root two standard errors at the pair's count), and
    the walk's does not (mutant: the polish off); the 0.95 pair, a stated limit at this size, closes at least
    half of the walk's gap."""
    import moment_polish_tables

    source = tmp_path / "pairs.csv"
    source.write_text(moment_polish_tables.collinear_text(20000, 1), encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(source), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("pairs", bytes(range(32)), rows_per_person=chain.ROWS_UNASKED))
    assert chained.statistical is not None and chained.statistical["moments"] is not None
    written = dict(document)
    written["relationships"] = dict(written["relationships"], statistical=chained.statistical)
    path = fixtures.write_profile(tmp_path, "pairs-profile.json", written)
    loaded = contract.load_profile(str(path), chain=True)
    moments = chained.statistical["moments"]
    blocks = {block["name"]: block for block in written["columns"]}
    numbers = [entry["column"] for entry in moments["columns"] if entry["kind"] == "number"]
    names = [column.name for column in loaded.columns]

    def code_r(twin: "generation.Twin", first: str, second: str) -> float:
        found_a = chain_moments.codes_of(blocks[first])
        found_b = chain_moments.codes_of(blocks[second])
        assert found_a is not None and found_b is not None
        a = list(generation.twin_column(twin, names.index(first)))
        b = list(generation.twin_column(twin, names.index(second)))
        pairs = [
            (chain_moments.linear_code(found_a, fractions.Fraction(float(x))), chain_moments.linear_code(found_b, fractions.Fraction(float(y))))
            for x, y in zip(a, b) if x != "" and y != ""
        ]
        return statistics.correlation([float(x) for x, _y in pairs], [float(y) for _x, y in pairs])

    shipped = generation.generate_held(loaded, 0)
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 0)
    walked = generation.generate_held(loaded, 0)
    gaps = {}
    for first, second in (("pa", "pb"), ("qa", "qb")):
        i, j = sorted((numbers.index(first), numbers.index(second)), reverse=True)
        pair = moments["correlations"][i][j]
        assert pair is not None
        published = pair[0] / 10**12
        bound = 0.0005 * (1 - published * published) + 2 * math.sqrt(2.0) * (1 - published * published) / math.sqrt(pair[1])
        gaps[first] = (abs(code_r(shipped, first, second) - published), abs(code_r(walked, first, second) - published), bound)
    # The near-identical pair comes back inside its bound; the walk's does not.
    assert gaps["qa"][0] <= gaps["qa"][2] < gaps["qa"][1], gaps
    # THE STATED LIMIT (plan P4-D456): at 20,000 rows `pa`'s chain level is L0 and its family's parents leave out
    # the age it is correlated with, so its frame leaves the 0.95 pair outside its bound; the polish still closes
    # at least half of the walk's gap. When the limit is lifted, this line asks for the bound.
    assert gaps["pa"][0] <= 0.5 * gaps["pa"][1], gaps


def test_a_top_coded_age_moves_only_among_its_own_cells(tmp_path, monkeypatch: pytest.MonkeyPatch, capsys) -> None:  # type: ignore[no-untyped-def]
    """HIPAA first, at the size the command's top-code reaches (one case at 20,000 rows): through
    `synthtwin profile`, which reads every age over 89 as 90 (its Safe Harbor rule), the age is a
    moment column on its clipped code (lane MPp's eligibility) and the polish only re-assigns the
    twin's own age cells among the rows holding one: no twin age exceeds 90, the column keeps its
    multiset and blanks, and the record key, held by its open question, is no moment column, keeps
    its bytes and equals no real key (mutant: the polish off leaves the ages where the walk put them)."""
    monkeypatch.chdir(tmp_path)
    rows = [[f"R{100000 + place}"] + row for place, row in enumerate(_rows(20000, 17))]
    for at in range(0, len(rows), 50):
        rows[at][1] = f"{91 + (at // 50) % 14}"
    text = "record,age,gender,group,pressure,lab,event\n" + "".join(",".join(row) + "\n" for row in rows)
    (tmp_path / "aged.csv").write_text(text, encoding="utf-8", newline="\n")
    capsys.readouterr()
    assert cli.main(["profile", "aged.csv"], chain=cli.ChainRun(rows_per_person=asking.ANSWER_ONE_ROW_EACH, folder=str(tmp_path / "data"))) == 0
    capsys.readouterr()
    loaded = contract.load_profile(str(tmp_path / "aged-profile.json"), chain=True)
    assert loaded.relationships.moments is not None
    polished = [name for name, _targets in generation._polish_plan(loaded)]
    assert "age" in polished and "record" not in polished, polished
    names = [column.name for column in loaded.columns]
    shipped = generation.generate_held(loaded, 2)
    monkeypatch.setattr(generation, "_POLISH_ROUNDS", 0)
    walked = generation.generate_held(loaded, 2)
    monkeypatch.undo()
    age = names.index("age")
    moved = list(generation.twin_column(shipped, age))
    before = list(generation.twin_column(walked, age))
    assert moved != before
    assert sorted(moved) == sorted(before)
    assert [cell == "" for cell in moved] == [cell == "" for cell in before]
    assert max(float(cell) for cell in moved if cell != "") <= 90
    record = names.index("record")
    keys = list(generation.twin_column(shipped, record))
    assert keys == list(generation.twin_column(walked, record))
    assert not set(keys) & {row[0] for row in rows}


def test_the_plan_is_a_function_of_the_description() -> None:
    """`_polish_plan` reads the description alone: a number moment column with a clip, its partners
    in the moments' order, then its `within` entries; none where no moment is published."""
    moments = contract.RuleBMoments(
        (
            contract.MomentColumn("a", "number", 100, mean=120.0, sd=30.0, clip=(0.0, 10.0)),
            contract.MomentColumn("f", "binary", 100, share=0.4),
            contract.MomentColumn("b", "number", 100, mean=90.0, sd=20.0, clip=(1.0, 9.0)),
        ),
        ((), ((0.25, 100),)),
        (
            contract.MomentWithin(
                "a", "f", (contract.MomentGroup(40, 110.0, 30.0), contract.MomentGroup(60, 127.0, 28.0), contract.MomentGroup(0)), 2
            ),
        ),
    )
    ladder = (contract.LadderEntry("a", (), ()), contract.LadderEntry("f", (), ()), contract.LadderEntry("b", (), ()))
    relationships = dataclasses.replace(contract.RelationshipManifest(slots=()), ladder=ladder, moments=moments)

    @dataclasses.dataclass
    class _Profile:
        relationships: contract.RelationshipManifest

    plan = generation._polish_plan(_Profile(relationships))  # type: ignore[arg-type]
    assert [name for name, _targets in plan] == ["a", "b"]
    first = plan[0][1]
    assert [(t.kind, t.name, t.level) for t in first] == [("pair", "b", 1), ("within", "f", 2)]
    assert first[0].goal == 0.25
    assert first[1].encoding == ((110.0 - 120.0) / 30.0, (127.0 - 120.0) / 30.0, 0.0) and first[1].goal > 0.0
    bare = dataclasses.replace(relationships, moments=None)
    assert generation._polish_plan(_Profile(bare)) == []  # type: ignore[arg-type]


def test_the_plan_reads_partners_binaries_and_the_projected_goals() -> None:
    """Repair 1's plan, from the description alone: a number's means in the bands of a partner it holds a
    published correlation with are no target of it (a partner `b`; the binary `f` stays a grouping); a
    binary with both levels published is polished toward a number's split by it (`by`, its slope the
    split times the normal density at its share) and its shares in a grouping's bands (`share`, the
    density over its spread), each aim starting at its goal over its slope; and correlation goals no data
    can hold (0.9, 0.9, -0.9) are the projected matrix's, the oracle's frozen bits; a round runs the
    numbers from the finest frame (most bands at the chain level) to the coarsest, then the binaries."""
    frozen = FROZEN["psd_projection"][0]
    moments = contract.RuleBMoments(
        (
            contract.MomentColumn("a", "number", 100, mean=120.0, sd=30.0, clip=(0.0, 10.0)),
            contract.MomentColumn("f", "binary", 100, share=0.4),
            contract.MomentColumn("b", "number", 100, mean=90.0, sd=20.0, clip=(1.0, 9.0)),
            contract.MomentColumn("c", "number", 100, mean=70.0, sd=10.0, clip=(1.0, 9.0)),
        ),
        ((), ((0.9, 100),), ((0.9, 100), (-0.9, 100))),
        (
            contract.MomentWithin("a", "b", (contract.MomentGroup(50, 110.0, 30.0), contract.MomentGroup(50, 130.0, 28.0))),
            contract.MomentWithin("a", "f", (contract.MomentGroup(60, 110.0, 30.0), contract.MomentGroup(40, 135.0, 28.0))),
            contract.MomentWithin("f", "b", (contract.MomentGroup(50, share=0.3), contract.MomentGroup(50, share=0.5))),
        ),
    )
    ladder = (
        contract.LadderEntry("a", ((("p01", "p50"),), (("p50", "p99"),)), (50, 50)),
        contract.LadderEntry("f", ((("0",),), (("1",),)), (60, 40), ((0,), (1,)), ((0,), (1,))),
        contract.LadderEntry("b", tuple(((f"p{k}", f"p{k + 1}"),) for k in range(5)), (20, 20, 20, 20, 20)),
        contract.LadderEntry("c", tuple(((f"p{k}", f"p{k + 1}"),) for k in range(3)), (30, 30, 40)),
    )
    relationships = dataclasses.replace(contract.RelationshipManifest(slots=()), ladder=ladder, moments=moments)

    @dataclasses.dataclass
    class _Profile:
        relationships: contract.RelationshipManifest

    ordered = generation._polish_plan(_Profile(relationships))  # type: ignore[arg-type]
    assert [name for name, _targets in ordered] == ["b", "c", "a", "f"]
    plan = dict(ordered)
    assert [(t.kind, t.name) for t in plan["a"]] == [("pair", "b"), ("pair", "c"), ("within", "f")]
    projected = [[float.fromhex(x) for x in row] for row in frozen["projected"]]
    assert [t.goal for t in plan["a"][:2]] == [projected[0][1], projected[0][2]]
    assert [t.goal for t in plan["b"] if t.kind == "pair"] == [projected[1][0], projected[1][2]]
    assert [(t.kind, t.name) for t in plan["f"]] == [("by", "a"), ("share", "b")]
    density = generation._normal_density(0.4)
    by, share = plan["f"]
    assert by.slope == (by.encoding[1] - by.encoding[0]) * density and by.aim == by.goal / by.slope
    assert share.slope == density / math.sqrt(0.4 * 0.6) and share.aim == share.goal / share.slope
    assert abs(density - 0.38634) < 1e-4


def test_a_correlation_s_aim_stays_inside_its_bound(monkeypatch: pytest.MonkeyPatch) -> None:
    """Repair 1: an aim of a pair, a correlation, never leaves (-0.999, 0.999), however far the round fell
    short of its goal (the oracle's 64-row twin, `X` aiming at 0.998 with `W`, whose rows the round
    cannot pair that closely); a within target's aim is not bounded so."""
    oc = _load("oracle_cases")
    n, columns, setup, _plan, sums = oc.polish_setup()
    target = generation._PolishTarget("pair", "W", 0.998, (), 0.998)
    holder = {"X": [target]}
    walk_columns = {}
    for name in ("X", "W"):
        held = columns[name]
        column = generation._WalkColumn(0, 2, (tuple(held["maps"][0]), tuple(held["maps"][1]), tuple(held["maps"][2])), (8, 8, 4), ())
        column.index = bytearray(3 * n)
        for row in range(n):
            chain_walk.write_code(column.index, 3, row, held["index"][row])
        column.codes = bytearray(held["frame"])
        column.slot_l0 = bytearray(held["slot_l0"])
        column.slot_codes = bytearray(held["slot_codes"])
        column.slot_has = bytearray(held["slot_has"])
        column.slot_rank = bytearray(2 * n)
        for place in range(n):
            chain_walk.write_code(column.slot_rank, 2, place, held["slot_rank"][place])
        walk_columns[name] = column
    ranks = {}
    for name in ("X", "W"):
        packed = bytearray(2 * n)
        for row in range(n):
            chain_walk.write_code(packed, 2, row, setup["ranks"][name][row])
        ranks[name] = packed
    state = generation._PolishState(
        [("X", holder["X"])], n,
        {name: bytearray(setup["codes"][name]) for name in ("X", "W")},
        {name: bytearray(setup["has"][name]) for name in ("X", "W")},
        ranks, {},
        {name: (float(setup["spreads"][name][0]), float(setup["spreads"][name][1])) for name in ("X", "W")},
        [chain_walk.normal_score((2 * step + 1) / (2 * generation._POLISH_RANK_STEPS)) for step in range(generation._POLISH_RANK_STEPS)],
        {},
    )
    hidden = chain_walk.packed(n, chain_walk.SUM_WIDTH)
    for row in range(n):
        chain_walk.put(hidden, row, sums[0][row])
    generation._polish_column(walk_columns["X"], "X", holder["X"], hidden, state, None, True)  # type: ignore[arg-type]
    assert target.aim == 0.999
    # Repair 2: a pair's bound follows its goal, half way from it to 1 past 0.999 (LANE MPg RULINGS 8 (2)).
    near = generation._PolishTarget("pair", "W", 0.9999, (), 0.9999, most=(1.0 + 0.9999) / 2.0)
    generation._polish_column(walk_columns["X"], "X", [near], hidden, state, None, True)  # type: ignore[arg-type]
    assert near.aim == (1.0 + 0.9999) / 2.0


def test_a_binary_s_frame_keys_stay_exact_past_four_bytes(clinic, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """Repair 2 (Codex's item 1, LANE MPg RULINGS 9 (1)): a binary's frame key `group * count + band` is
    renumbered before it is stored in four bytes, so two keys `2 ** 32` apart stay two groups (the helper
    alone; mutant: the key stored first, then renumbered); and on the clinic, whose two-valued `event` is
    crossed with two or more columns by its families, every key column's band count widened by `2 ** 32`
    gives the same twin, every band total and family table HELD in validation."""
    found = chain_walk.packed(3, 4)
    for row, value in enumerate((0, 1, 0)):
        chain_walk.put(found, row, value)
    generation._joint_groups(found, b"\x00\x00\x01", 2**32, 3)
    assert [chain_walk.item(found, row) for row in range(3)] == [0, 1, 2]
    loaded = contract.load_profile(str(clinic.path), chain=True)
    crossed = [
        name for family in loaded.relationships.chain
        for name in ([parent for parent, _level in family.parents] if family.child == "event" else
                     [family.child] + [parent for parent, _level in family.parents if parent != "event"]
                     if any(parent == "event" for parent, _level in family.parents) else [])
    ]
    assert len(set(crossed)) >= 2, crossed
    shipped = generation.generate_held(loaded, 3)
    monkeypatch.setattr(generation, "_POLISH_KEY_WIDTH", 2**32)
    wide = generation.generate_held(loaded, 3)
    moved = _columns(wide)
    assert moved == _columns(shipped)
    names = list(wide.names)
    rows = [[moved[at][r] for at in range(len(names))] for r in range(len(moved[0]))]
    code, report, _screen = clinic.validate(rows)
    totals, families = chain_twins._verdicts(report)
    assert code == 0 and set(totals.values()) == {"HELD"} and set(families.values()) == {"HELD"}, (totals, families)


def test_k_s6_13_is_never_green_off_the_quiet_machine() -> None:
    """Repair 2 (Codex's item 5, LANE MPg RULINGS 9 (5)): K-S6-13's projected hours are a machine kind
    (`seconds_below`) beside its projected peak (`peak_memory_below`), so its recorded loaded-machine run,
    judged with seconds not counted, reads OPEN-held and never IMPROVED (mutant: the hours key judged
    as an ordinary bound)."""
    import kpi_rules

    ledger = json.loads((REPOSITORY / "tests" / "kpi" / "ledger.json").read_text(encoding="utf-8"))
    entry = [one for one in ledger["entries"] if one["id"] == "K-S6-13"][0]
    assert entry["key_kinds"]["projected_2m_hours_describe_chain_and_shipped_generate"] == "seconds_below"
    assert entry["value_at"]["value"]["seconds_load_disturbed"] is True
    verdict = kpi_rules.judge(entry, entry["value_at"]["value"], seconds_count=False)
    assert verdict.word == kpi_rules.OPEN_HELD, verdict.message


def _goal_profile(columns: "list[tuple[str, int]]", pairs: "dict[tuple[int, int], tuple[int, int]]"):  # type: ignore[no-untyped-def]
    """A description holding only rule B's moments for `columns` (numbers in the moments' order) and `pairs`."""
    entries = tuple(contract.MomentColumn(name, "number", n, mean=100.0, sd=10.0, clip=(0.0, 200.0)) for name, n in columns)
    triangle = tuple(
        tuple(
            (pairs[(a, b)][0] / 10**12, pairs[(a, b)][1]) if (a, b) in pairs else None for b in range(a)
        )
        for a in range(len(columns))
    )
    moments = contract.RuleBMoments(entries, triangle, ())
    ladder = tuple(contract.LadderEntry(name, (), ()) for name, _n in columns)
    relationships = dataclasses.replace(contract.RelationshipManifest(slots=()), ladder=ladder, moments=moments)

    @dataclasses.dataclass
    class _Profile:
        relationships: contract.RelationshipManifest

    return _Profile(relationships)


def test_the_goals_project_only_inside_a_common_row_set() -> None:
    """Repair 2 (Codex's item 2, LANE MPg RULINGS 9 (2)): published correlations are each taken on their
    pair's own rows, so only a COMMON ROW SET (pairs holding every reading of both columns) is projected,
    and an unpublished pair is no goal, never an observed nought. Codex's two probes at 20,000 rows keep
    their published 0.9 (X on the first half, Z on the second, Y throughout; three disjoint cohorts of
    10,000 rows publishing +0.9, +0.9 and -0.9), where the zero-filled projection moved them to about 0.729
    and 0.5 (mutant); one row set whose correlations no data can hold is projected, each move past
    rounding returned to be disclosed; one positive definite row set keeps its goals; all to the oracle's
    bits. A number's partners are the 24 published correlations largest in size, ties in the moments'
    order (the verify's item 2: no number aims at more), each pair's aim bounded by the larger of 0.999
    and half way from its goal to 1."""
    oc = _load("oracle_cases")
    frozen = FROZEN["polish_targets"]
    for label, (columns, pairs) in oc.polish_target_inputs().items():
        profile = _goal_profile(columns, pairs)
        names = [name for name, _n in columns]
        goals, moves, _spreads = generation._target_correlations(profile, names)  # type: ignore[arg-type]
        assert [[None if g is None else g.hex() for g in row] for row in goals] == frozen[label]["goals"], label
        assert [[names.index(m.first), names.index(m.second), m.published.hex(), m.goal.hex()] for m in moves] == frozen[label]["moves"], label
        if label in ("halves", "cohorts", "one_row_set_kept"):
            assert moves == [] and all(
                goals[a][b] == pairs[(a, b)][0] / 10**12 for a, b in pairs
            ), label
        if label == "one_row_set":
            assert len(moves) == 3 and all(abs(m.goal) < 0.6 for m in moves)
        plan = dict(generation._polish_plan(profile))  # type: ignore[arg-type]
        if label == "partners":
            chosen = [t.name for t in plan["N00"] if t.kind == "pair"]
            assert chosen == [names[at] for at in frozen[label]["chosen"]] and len(chosen) == 24
            assert "N06" not in chosen and "N05" in chosen
        for name, targets in plan.items():
            for t in targets:
                if t.kind == "pair":
                    assert t.most == max(0.999, (1.0 + abs(t.goal)) / 2.0)
    # A pair published past 0.999 (LANE MPg RULINGS 8 (2)): its bound is half way from its goal to 1 (mutant: 0.999).
    near = dict(generation._polish_plan(_goal_profile([("A", 20000), ("B", 20000)], {(1, 0): (999900000000, 20000)})))  # type: ignore[arg-type]
    assert near["A"][0].goal == 0.9999 and near["A"][0].most == (1.0 + 0.9999) / 2.0


def _complete_case(columns: "list[list[str]]") -> "tuple[float, float, float]":
    """The least-squares slope of the second column on the first over the rows holding both, the first's spread there,
    and the slope's allowance: 2 root two times its standard error, floored as K-S6-12 floors a correlation's
    (`|slope| max(1 - r ** 2, 0.05) / sqrt(n)`, so a relation without noise keeps an allowance)."""
    both = [(float(a), float(b)) for a, b in zip(columns[0], columns[1]) if a != "" and b != ""]
    n = len(both)
    mx = sum(a for a, _b in both) / n
    my = sum(b for _a, b in both) / n
    sxx = sum((a - mx) ** 2 for a, _b in both)
    sxy = sum((a - mx) * (b - my) for a, b in both)
    syy = sum((b - my) ** 2 for _a, b in both)
    slope = sxy / sxx
    r = sxy / math.sqrt(sxx * syy)
    error = max(math.sqrt(max(syy - slope * sxy, 0.0) / (n - 2) / sxx), abs(slope) * max(1.0 - r * r, 0.05) / math.sqrt(n))
    return slope, math.sqrt(sxx / (n - 1)), 2 * math.sqrt(2.0) * error


def test_an_incomplete_pair_s_own_spreads_are_read_and_aimed_at(tmp_path) -> None:  # type: ignore[no-untyped-def]
    """Repair 2 (Codex's item 3, LANE MPg RULINGS 9 (3)): an incomplete pair's `[r, n, [sd, sd]]` keeps both
    spreads through the loader, and the column whose rows the pair does not cover aims at its own spread over
    the pair's rows (the column whose every reading the pair holds has nothing to aim at). At 21,000 rows: on
    Codex's case (`x` on 0 to 20 and 100 to 120, `y` blank beside the second block) the twin's complete-case
    slope of `y` on `x` is the real one within half a rounding unit plus 2 root two standard errors (`x`'s
    bands part the two blocks, so the frame holds it with or without the spreads); where `y` is blank beside
    the high `x` softly, the spreads read by the polish bring the twin's complete-case spread of `x` at least
    half way nearer the real one than the twin with them dropped (mutant: the loader's spreads empty), a
    frame that keeps `x`'s `L2` bands leaving the rest (P4-D456's stated limit)."""
    import moment_polish_tables

    for label, text in (("blocks", moment_polish_tables.blocks_text()), ("soft", moment_polish_tables.missing_beside_high_text())):
        source = tmp_path / f"{label}.csv"
        source.write_text(text, encoding="utf-8", newline="\n")
        settings = taxonomy.Settings(small_cell_floor=11)
        table = reading.read_table(str(source), small_cell_floor=11)
        document = profile.build_document(table, settings, [], [], [])
        chained = chain.describe(table, document, settings, chain.ChainSwitch(label, bytes(range(32)), rows_per_person=chain.ROWS_UNASKED))
        written = dict(document)
        written["relationships"] = dict(written["relationships"], statistical=chained.statistical)
        path = fixtures.write_profile(tmp_path, f"{label}-profile.json", written)
        loaded = contract.load_profile(str(path), chain=True)
        moments = loaded.relationships.moments
        assert moments is not None
        published = chained.statistical["moments"]["correlations"][1][0]
        assert len(published) == 3 and moments.spreads[1][0] is not None
        unit = chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, published[1])
        assert moments.spreads[1][0] == (published[2][0] / unit, published[2][1] / unit)
        plan = dict(generation._polish_plan(loaded))
        x_pair = [t for t in plan["x"] if t.kind == "pair" and t.name == "y"][0]
        assert x_pair.sds == (moments.spreads[1][0][1],) and x_pair.scales == [1.0]
        assert all(not t.sds for t in plan["y"] if t.kind == "pair")
        real = _complete_case([[row.split(",")[0] for row in text.splitlines()[1:]], [row.split(",")[1] for row in text.splitlines()[1:]]])
        shipped = _complete_case(_columns(generation.generate_held(loaded, 0))[:2])
        if label == "blocks":
            assert abs(shipped[0] - real[0]) <= real[2], (shipped, real)
            continue
        dropped_profile = dataclasses.replace(
            loaded, relationships=dataclasses.replace(loaded.relationships, moments=dataclasses.replace(moments, spreads=()))
        )
        dropped = _complete_case(_columns(generation.generate_held(dropped_profile, 0))[:2])
        assert abs(shipped[1] - real[1]) <= 0.5 * abs(dropped[1] - real[1]), (shipped, dropped, real)
        assert abs(shipped[0] - real[0]) < abs(dropped[0] - real[0]), (shipped, dropped, real)


def test_k_s6_12_judges_an_incomplete_pair_s_own_spreads(clinic) -> None:  # type: ignore[no-untyped-def]
    """Repair 2 (Codex's item 3, LANE MPg RULINGS 9 (3)): K-S6-12's driver judges each incomplete pair's two own
    spreads (`pair spread`) as a column's spread is judged; on the clinic's own rows every one lies inside half a
    unit plus 2 root two standard errors, and with one published pair spread made ten times larger that one is
    outside, so the KPI answers the published spreads (it had read the correlation alone)."""
    spec = importlib.util.spec_from_file_location("kpi_moment_polish_gate", REPOSITORY / "tools" / "measurements" / "kpi_moment_polish.py")
    assert spec is not None and spec.loader is not None
    kpi = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(kpi)
    table = reading.read_table(str(clinic.table), small_cell_floor=11)
    document = json.loads(clinic.path.read_text(encoding="utf-8"))
    statistical = json.loads(json.dumps(clinic.statistical))
    found = [row for row in kpi.moments_on(table, document, statistical) if row[0] == "pair spread"]
    assert found and all(good for _kind, good in kpi.inside(found, 2 * math.sqrt(2.0)))
    line = statistical["moments"]["correlations"]
    at, other = [(i, j) for i in range(len(line)) for j in range(i) if line[i][j] is not None and len(line[i][j]) == 3][0]
    line[at][other][2][0] = 10 * line[at][other][2][0]
    moved = [row for row in kpi.moments_on(table, document, statistical) if row[0] == "pair spread"]
    assert [good for _kind, good in kpi.inside(moved, 2 * math.sqrt(2.0))].count(False) == 1


def test_a_moved_goal_is_disclosed_in_the_twin_s_report(clinic, monkeypatch: pytest.MonkeyPatch) -> None:  # type: ignore[no-untyped-def]
    """Repair 2 (LANE MPg RULINGS 9 (2)): every published correlation the projection moves past its rounding is
    KEPT and DISCLOSED in the twin's report, its published r beside the goal the polish aims at (the plan had
    discarded the projection's figures); the plan is made once a run, by `plan_generation` (mutant: the moves
    never reach the report)."""
    loaded = contract.load_profile(str(clinic.path), chain=True)
    made: "list[int]" = []
    inner = generation._polish_layout

    def moved(profile):  # type: ignore[no-untyped-def]
        made.extend([1])
        layout = inner(profile)
        return generation._PolishLayout(layout.plan, [generation._PolishMove("age", "pressure", 0.5, 0.25)])

    monkeypatch.setattr(generation, "_polish_layout", moved)
    twin = generation.generate_held(loaded, 3)
    assert made == [1]
    found = [d for d in twin.deviations if d.fact.startswith("relationships.statistical.moments.correlations")]
    assert [(d.column, d.published, d.achieved) for d in found] == [("pressure", "0.500000000000", "aimed at 0.250000000000")]
