"""G16.3's GROUPING GATE (lane CHG, plan P4-D492; LANE CHG RULINGS 1): the polish aims at a grouping moment only where
the published facts show it beyond chance.

THE DEFECT IT CLOSES (lane CHON's statistics check, LANE CHON RULINGS 6 (1)): on a table whose columns are drawn
independently, the switched twin called about one pair in seven associated (a fresh sample one in twenty), because
the polish aimed at EVERY published grouping moment, the real table's chance pattern included, and kept the walk's
own fresh noise beside it: a `within` target meets the published group means along their one direction only, so
the twin carries the table's chance pattern there and a fresh one in the other directions.

WHAT IS HELD, each red on its mutant and on lane CHON's head `875b1b93`, which aims at every grouping moment:
- the gate's point is Wilson and Hilferty's cube at z = 3.0902 in binary64 `+ - * /` and `sqrt`, the oracle's to
  the last bit on the eleven counts of degrees of freedom it froze (1 to 1,000), and on every count from 1 to 5,000
  never below the exact 0.001 point and within 3.1 per cent of it;
- on published-fact inputs at both sides of the level (a 12-band `within` entry, a two-band split, a binary's
  shares in 11 bands, and since repair 1 two entries whose bands hold no reading in places: tested on the bands
  holding a count, a single such band dropped with no test), each goal, statistic and decision is the oracle's; the
  level 0.05 keeps four of them;
- on a description of three numbers, a binary and a 12-level grouping column the gated plan is the oracle's:
  every correlation kept, field for field the ungated plan's; each grouping target kept only where it passes,
  none with a goal of nought; its four mutants (the gate off; the level 0.05; a dropped target kept at nought;
  the correlations gated too) give other plans;
- a target of a kind the gate has no test for is refused, with the gate on or off;
- on invented families of independent columns at 20,000 rows the gated plan keeps no chance grouping target and
  the twin's group means stand at a fresh draw's distance: tests/test_polish_grouping_gate_families.py, a file of
  its own so that each file stays under three CPU minutes, holds those cases on this file's helpers
  (`_family_text`, `_chained`, `_copy_and_chi_square`);
- with the gate off, `K-S6-16`'s chained fixture is the head's description and twin byte for byte;
- what the gate leaves to the walk is stated where the owner reads (repair 1): a number's spread by group, whose
  entry is tested on its band means alone, and a yes/no column's effect after adjusting, in the method page's and
  the plan decision's limits and in the contract's, the plan's and the CHANGELOG's plain words;
- THE ONE SLOW LINE, the null table ST5 at 20,000 rows through the commands a person types (lane MU's route S),
  stands since repair 1 in tests/test_polish_grouping_gate_null_table.py, a file of its own so that each file
  stays under three CPU minutes (lane MU's current route S walks more `synthtwin profile` rounds, the checklist
  answered, and this file read 183.6 CPU seconds with the line in it).
"""

import dataclasses
import inspect
import json
import math
import pathlib
import random

import pytest

from synthtwin import chain, chain_moments, contract, errors, generation, profile, reading, taxonomy

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
FROZEN = json.loads((REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))
GATE = FROZEN["chain"]["polish_gate"]
KEY = bytes(range(32))
Z_005 = 1.6449


def _column(name: str, published: "list[int]") -> contract.MomentColumn:
    """A moment column from its published units: a number's mean, spread and count, or a binary's share and count."""
    if len(published) == 3:
        mean, sd, n = published
        return contract.MomentColumn(
            name, chain_moments.KIND_NUMBER, n, mean=mean / chain_moments.unit(chain_moments.SCALE_MEAN, n),
            sd=sd / chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, n), clip=(0.0, 255.0),
        )
    share, n = published
    return contract.MomentColumn(name, chain_moments.KIND_BINARY, n, share=share / chain_moments.unit(chain_moments.SCALE_SHARE, n))


def _within(column: str, by: str, groups: "list[list[int]]") -> contract.MomentWithin:
    """A `within` entry from its published bands, each read in the unit its own count sets, as the loader reads it (a
    band holding none of the column's readings, `[0]`, as `contract.MomentGroup(0)`)."""
    found = []
    for group in groups:
        n = group[0]
        if n == 0:
            found += [contract.MomentGroup(0)]
        elif len(group) == 3:
            found += [contract.MomentGroup(n, mean=group[1] / chain_moments.unit(chain_moments.SCALE_MEAN, n),
                                           sd=group[2] / chain_moments.unit(chain_moments.SCALE_SPREAD, n))]
        else:
            found += [contract.MomentGroup(n, share=group[1] / chain_moments.unit(chain_moments.SCALE_SHARE, n))]
    return contract.MomentWithin(column, by, tuple(found), 1)


@dataclasses.dataclass
class _Profile:
    relationships: contract.RelationshipManifest


def _gate_profile() -> _Profile:
    """The oracle's `polish_gate_plan` description: numbers A, B and C, a binary F, a 12-level grouping column G."""
    oc_columns = {"A": [1200, 30000, 12000], "B": [900, 20000, 12000], "C": [700, 10000, 12000], "F": [3000, 12000]}
    printed = {("B", "A"): 300000000000, ("C", "A"): 10000000000, ("C", "B"): 20000000000}
    numbers = ["A", "B", "C"]
    triangle = tuple(
        tuple((printed[(numbers[a], numbers[b])] / 10**12, 12000) for b in range(a)) for a in range(len(numbers))
    )
    split = [[8400, 697, 300], [3600, 707, 300]]

    def alternating(base: int, step: int, groups: int, n: int, sd: "int | None" = None) -> "list[list[int]]":
        out = []
        for g in range(groups):
            value = base if groups % 2 == 1 and g == groups - 1 else base + (step if g % 2 == 0 else -step)
            out += [[n, value] if sd is None else [n, value, sd]]
        return out

    within = (
        _within("A", "G", alternating(1200, 16, 12, 1000, 300)),
        _within("B", "G", alternating(900, 10, 12, 1000, 200)),
        _within("C", "F", split),
        _within("A", "F", [[8400, 1199, 300], [3600, 1202, 300]]),
        _within("B", "F", [[8400, 898, 200], [3600, 906, 200]]),
        _within("F", "G", alternating(3000, 200, 12, 1000)),
        _within("F", "B", alternating(3000, 300, 4, 3000)),
    )
    moments = contract.RuleBMoments(
        (_column("A", oc_columns["A"]), _column("B", oc_columns["B"]), _column("F", oc_columns["F"]),
         _column("C", oc_columns["C"])),
        triangle, within,
    )
    ladder = (
        contract.LadderEntry("A", tuple(((f"p{k}", f"p{k + 1}"),) for k in range(4)), (3000, 3000, 3000, 3000)),
        contract.LadderEntry("B", tuple(((f"p{k}", f"p{k + 1}"),) for k in range(4)), (3000, 3000, 3000, 3000),
                             ((0,), (1,), (2,), (3,))),
        contract.LadderEntry("F", ((("0",),), (("1",),)), (8400, 3600), ((0,), (1,)), ((0,), (1,))),
        contract.LadderEntry("C", tuple(((f"p{k}", f"p{k + 1}"),) for k in range(3)), (4000, 4000, 4000)),
        contract.LadderEntry("G", tuple(((f"g{k:02d}",),) for k in range(12)), tuple(1000 for _k in range(12))),
    )
    return _Profile(dataclasses.replace(contract.RelationshipManifest(slots=()), ladder=ladder, moments=moments))


def _listed(plan: "list[tuple[str, list[generation._PolishTarget]]]") -> "dict[str, list[list[str]]]":
    return {name: [[t.kind, t.name, t.goal.hex()] for t in targets] for name, targets in plan}


# -- THE POINT AND ITS ARITHMETIC ------------------------------------------------------------------------------


def test_the_gate_point_is_wilson_and_hilferty_s_cube_to_the_oracle_s_last_bit(monkeypatch: pytest.MonkeyPatch) -> None:
    """The 0.001 point on the eleven counts of degrees of freedom the oracle froze (1 to 1,000) is its binary64 value
    (and at the 0.05 level its mutant's); on EVERY count from 1 to 5,000 it is never below the exact point (scipy's
    `chi2.isf`) and at most 3.1 per cent above it (one degree of freedom; 0.6 per cent from ten); and the gate's two
    functions call no `math` function but `sqrt`."""
    from scipy.stats import chi2

    for df, value in GATE["points"].items():
        assert generation._gate_point(int(df)).hex() == value, df
    assert len(GATE["points"]) == 11 and max(int(df) for df in GATE["points"]) == 1000
    exact = chi2.isf(0.001, list(range(1, 5001)))
    for df in range(1, 5001):
        point = generation._gate_point(df)
        assert float(exact[df - 1]) <= point <= float(exact[df - 1]) * (1.031 if df < 10 else 1.006), df
    monkeypatch.setattr(generation, "_POLISH_GATE_Z", Z_005)
    for df, value in GATE["points_005"].items():
        assert generation._gate_point(int(df)).hex() == value, df
    for function in (generation._gate_point, generation._beyond_chance):
        source = inspect.getsource(function)
        used = {word.split("(")[0] for word in source.split("math.")[1:]}
        assert used <= {"sqrt"}, used
    assert generation._POLISH_GATE_Z == Z_005 and GATE["points"]["1"] != GATE["points_005"]["1"]


def test_the_gate_decides_at_both_sides_of_its_level_on_published_facts(monkeypatch: pytest.MonkeyPatch) -> None:
    """Each published-fact input of the oracle's edges (a 12-band `within` entry 1.5 and 1.6 codes either side, a
    two-band split 0.9 and 1.0 either side and 0.6 between the two levels, a binary's shares in 11 bands 0.0218 and
    0.0219 either side): the product's goal and statistic are the oracle's bits and its decision is the oracle's;
    the level 0.05 (its mutant) keeps the four the 0.001 level drops. AND THE TWO ENTRIES WITH EMPTY BANDS (repair 1,
    skeptic 1's item 2; a band holding no reading, `[0]`, which the contract allows: a measurement taken in some
    bands only): a 12-band entry with two empty bands is tested on 9 degrees of freedom, k the bands holding a count
    (its statistic lies between the points on 9 and on 11, so a gate that counted every band would drop it); an
    entry with one band holding readings is dropped with no exception (no point exists on nought degrees)."""
    assert GATE["edges"]["empty12_live10"]["df"] == 9 and GATE["edges"]["empty12_live1"]["df"] == 0
    between = float.fromhex(GATE["edges"]["empty12_live10"]["statistic"])
    assert generation._gate_point(9) < between < generation._gate_point(11)
    flipped = 0
    for label, edge in GATE["edges"].items():
        groups = edge["groups"]
        within = _within("X", "Y", groups)
        if edge["kind"] == "within":
            entry = _column("X", edge["column"])
            target = generation._within_target(entry, within, "within", "Y")
        else:
            entry = _column("X", edge["column"])
            target = generation._share_target(entry, within)
        assert target is not None, label
        assert target.goal.hex() == edge["goal"], label
        count = sum(group[0] for group in groups if group[0] > 0)
        assert (count * target.goal).hex() == edge["statistic"], label
        assert generation._beyond_chance(within, target.goal) is edge["kept"], label
        with monkeypatch.context() as local:
            local.setattr(generation, "_POLISH_GATE_Z", Z_005)
            assert generation._beyond_chance(within, target.goal) is edge["kept_005"], label
        flipped += 1 if edge["kept_005"] and not edge["kept"] else 0
    assert flipped == 4
    assert [label for label, edge in GATE["edges"].items() if edge["kept"]] == [
        "within12_over", "split_over", "shares11_over", "empty12_live10"]


# -- THE PLAN ------------------------------------------------------------------------------------------------------


def test_the_plan_keeps_every_correlation_and_only_the_grouping_targets_beyond_chance(monkeypatch: pytest.MonkeyPatch) -> None:
    """The gated plan of the oracle's description is the oracle's (each column's targets, kinds, names and goals);
    every correlation of the ungated plan is in it field for field; each grouping target in it passes the test and
    none holds a goal of nought; the gate off and the level 0.05 give the oracle's mutant plans, and the plans of
    the other two mutants (a dropped target kept at nought, the correlations gated too) differ from it."""
    described = _gate_profile()
    gated = generation._polish_layout(described).plan  # type: ignore[arg-type]
    assert _listed(gated) == GATE["plan"]
    entries = {(w.column, w.by, w.level): w for w in described.relationships.moments.within}  # type: ignore[union-attr]
    for name, targets in gated:
        for target in targets:
            if target.kind != "pair":
                key = (target.name, name, 1) if target.kind == "by" else (name, target.name, 1)
                assert target.goal > 0.0 and generation._beyond_chance(entries[key], target.goal), (name, target.kind)
    with monkeypatch.context() as local:
        local.setattr(generation, "_POLISH_GATE", False)
        ungated = generation._polish_layout(described).plan  # type: ignore[arg-type]
    assert _listed(ungated) == GATE["plan_ungated"] == GATE["plan_mutant_off"]
    kept_pairs = {(name, t.name): t for name, targets in gated for t in targets if t.kind == "pair"}
    head_pairs = {(name, t.name): t for name, targets in ungated for t in targets if t.kind == "pair"}
    assert kept_pairs == head_pairs and len(head_pairs) == 6
    with monkeypatch.context() as local:
        local.setattr(generation, "_POLISH_GATE_Z", Z_005)
        assert _listed(generation._polish_layout(described).plan) == GATE["plan_mutant_level_005"]  # type: ignore[arg-type]
    for mutant in ("plan_mutant_off", "plan_mutant_level_005", "plan_mutant_nought", "plan_mutant_pairs"):
        assert GATE[mutant] != GATE["plan"], mutant
    assert any(goal == (0.0).hex() for targets in GATE["plan_mutant_nought"].values() for _k, _n, goal in targets)
    assert all(kind != "pair" or name in ("B", "A") for targets in GATE["plan_mutant_pairs"].values()
               for kind, name, _goal in targets)


def test_a_target_kind_the_gate_has_no_test_for_is_refused(monkeypatch: pytest.MonkeyPatch) -> None:
    """A target of a kind the gate neither keeps whole nor tests (a later lane's, say a trajectory over visits) is
    refused with the gate on and off, and wherever the plan made it (a binary's share target turned into one)."""
    strange = generation._PolishTarget("trajectory", "visit", 0.5)
    for setting in (True, False):
        with monkeypatch.context() as local:
            local.setattr(generation, "_POLISH_GATE", setting)
            with pytest.raises(errors.ProfileError, match="no test for"):
                generation._gate_keeps("A", strange, {})
    made = generation._share_target

    def renamed(entry: contract.MomentColumn, within: contract.MomentWithin) -> "generation._PolishTarget | None":
        found = made(entry, within)
        return None if found is None else dataclasses.replace(found, kind="trajectory")

    monkeypatch.setattr(generation, "_share_target", renamed)
    with pytest.raises(errors.ProfileError, match="no test for"):
        generation._polish_layout(_gate_profile())  # type: ignore[arg-type]


def test_the_gate_off_is_the_head_byte_for_byte(tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """`K-S6-16`'s chained fixture through the shipped command (1,500 rows, a test size): with the gate off its
    description and twin are the head's bytes, the earlier golden, and every word drawn is planned; with it on
    (`K-S6-16`'s own case) the description is the same bytes and only the twin moves, one column fewer polished. So
    the gate moves nothing but which grouping targets the polish aims at."""
    import test_stage6_switch_on as switch_on

    monkeypatch.setattr(generation, "_POLISH_GATE", False)
    described, twin, drawn, planned = switch_on.golden_record(tmp_path / "ungated")
    assert (described, twin) == (switch_on.GOLDEN_DESCRIPTION, switch_on.GOLDEN_TWIN_UNGATED)
    assert drawn == planned == 174556


# -- WHAT THE GATE LEAVES TO THE WALK, STATED ----------------------------------------------------------------------

# The owner's plain words for the two fidelity costs the reviews of repair 1 measured (LANE CHG RULINGS 2 (2) and
# 3 (1)), each in contract 4.6b.13's and plan P4-D464's plain words and in the CHANGELOG's entry.
SPREAD_WORDS = "a difference between groups in how widely a measurement spreads, with no difference in its average, is not reproduced"
EFFECT_WORDS = "can come out a fifth to a third smaller on the twin"
# And the null table's words restated from `K-BC-03`'s nine readings through lane MU's current route S (the
# statistics check's item 2): a median of 7.6 per cent of the pairs, the largest 9.5, a fresh sample 2.9.
NULL_WORDS = "about one pair in thirteen tests as related on the twin, one in ten at the most"


def _section(text: str, start: str, end: str) -> str:
    at = text.index(start)
    return text[at:text.index(end, at + len(start))]


def test_what_the_gate_leaves_to_the_walk_is_stated_where_the_owner_reads() -> None:
    """Two fidelity costs of the gate, measured by repair 1's reviews, are named in every record that says what the
    twin supports (LANE CHG RULINGS 2 (2) and 3 (1); owner part b, CHG-b), each red where its sentence is taken out.

    (d) and (6), THE SPREAD OF A NUMBER BY GROUP: the gate reads a `within` target's band MEANS alone, while the
    target also carries the band spreads it aims at; so an entry whose bands differ in spread (1.8 against 6.0) and
    not in mean is dropped whole (its statistic nought), its spreads left to the walk (skeptic 1 measured a published
    spread ratio of 3.52 at 1.02 on the gated twin). (e) and (7), A YES/NO COLUMN'S EFFECT AFTER ADJUSTING: where
    the chain does not carry it, the twin's adjusted effect shrinks (the statistics check: 3.40 against 4.00). And the
    null table's words, restated from `K-BC-03`'s nine readings (the statistics check's item 2: the build's 'one pair
    in eleven to fifteen' read two readings of another harness), with what its share is made of in limit (5)."""
    groups = [[1000, 370, 18 if g % 2 else 60] for g in range(12)]
    within = _within("X", "Y", groups)
    target = generation._within_target(_column("X", [370, 4400, 12000]), within, "within", "Y")
    assert target is not None and target.goal == 0.0 and not generation._beyond_chance(within, target.goal)
    assert max(target.sds) / min(target.sds) > 3.0
    method = (REPOSITORY / "docs" / "spec" / "generation-method-v1.md").read_text(encoding="utf-8")
    gate = _section(method, "**AMENDED Wednesday 2026-11-11: THE GROUPING GATE", "### G16.4")
    plan = (REPOSITORY / "docs" / "plans" / "phase-4-columns.md").read_text(encoding="utf-8")
    decision = plan[plan.index("## Decision P4-D492"):]
    supports = _section(plan, "**What the switched twin supports, in plain words**", "## Decision")
    contract_text = (REPOSITORY / "docs" / "spec" / "profile-contract-v6.md").read_text(encoding="utf-8")
    plain = _section(contract_text, "*Amended Wednesday 2026-11-11 (plan P4-D492, lane CHG)", "\n\n")
    changelog = (REPOSITORY / "CHANGELOG.md").read_text(encoding="utf-8")
    entry = _section(changelog, "### Lane CHG:", "\n### ")
    for label, text in (("G16.3", gate), ("P4-D492", decision)):
        assert "THE SPREAD OF A NUMBER BY GROUP" in text and "A YES/NO COLUMN'S EFFECT AFTER ADJUSTING" in text, label
        assert text.count("CHG-b") >= 2 and "3.52" in text and "3.40" in text, label
    assert "(d) THE SPREAD OF A NUMBER BY GROUP" in gate and "(e) A YES/NO COLUMN'S EFFECT" in gate
    assert "(6) THE SPREAD OF A NUMBER BY GROUP" in decision and "(7) A YES/NO COLUMN'S EFFECT" in decision
    for label, text in (("4.6b.13", plain), ("P4-D464", supports), ("CHANGELOG", entry)):
        assert SPREAD_WORDS in " ".join(text.split()) and EFFECT_WORDS in " ".join(text.split()), label
    for label, text in (("G16.3", gate), ("P4-D492", decision)):
        assert "eleven counts of degrees of freedom from 1 to 1,000" in text, label
    for label, text in (("4.6b.13", plain), ("P4-D464", supports)):
        flat = " ".join(text.split())
        assert NULL_WORDS in flat and "one pair in eleven to fifteen" not in flat, label
    assert "(5) WHAT THE NULL TABLE'S SHARE IS MADE OF" in decision and "one pair of 105 under its bar" in decision


# -- INDEPENDENT COLUMNS AT 20,000 ROWS ----------------------------------------------------------------------------

LEVELS = [f"w{k:02d}" for k in range(12)]


def _family_text(rows: int, seed: int, columns: "list[str]") -> str:
    """An invented family, every column from a stream of its own: `ward` a label of 12 equal levels; `marker` a
    skewed number to one decimal (a log-normal reading), blank on about a third of the rows; `flag` a binary of
    share 0.2."""
    streams = {name: random.Random(seed * 104729 + 31 * at + 7) for at, name in enumerate(("ward", "marker", "flag"))}
    out = [",".join(columns)]
    for _row in range(rows):
        cells = []
        for name in columns:
            draw = streams[name]
            if name == "ward":
                cells += [LEVELS[draw.randrange(12)]]
            elif name == "marker":
                value = math.exp(draw.gauss(1.5, 0.9))
                cells += ["" if draw.random() < 1.0 / 3.0 else f"{value:.1f}"]
            else:
                cells += ["1" if draw.random() < 0.2 else "0"]
        out += [",".join(cells)]
    return "\n".join(out) + "\n"


def _chained(folder: pathlib.Path, stem: str, text: str) -> "contract.Profile | None":
    """The table described with the chain (the fixed test key, one row a person), written through the rule steps and
    loaded with the chain, as every switched writer does; None where the chain's keyed choice draws no family (then
    nothing between columns is published and nothing is polished)."""
    import fixtures

    folder.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(folder, f"{stem}.csv", text)
    settings = taxonomy.Settings()
    found = reading.read_table(str(path), small_cell_floor=settings.small_cell_floor)
    document = profile.build_document(found, settings, [], [], [])
    chained = chain.describe(found, document, settings, chain.ChainSwitch(stem, KEY, rows_per_person=chain.ROWS_ONE))
    if chained.statistical is None:
        return None
    written = chain.with_rules(dict(document), chain.Chained(chained.statistical, (), {}, (), (), ""))
    return contract.load_profile(str(fixtures.write_profile(folder, f"{stem}-profile.json", written)), chain=True)


def _group_means(text: str, group: str, value: str) -> "dict[str, list[float]]":
    lines = text.splitlines()
    header = lines[0].split(",")
    g, v = header.index(group), header.index(value)
    out: "dict[str, list[float]]" = {}
    for line in lines[1:]:
        cells = line.split(",")
        if cells[g] == "" or cells[v] == "":
            continue
        held = out.setdefault(cells[g], [0.0, 0.0, 0.0])
        number = float(cells[v])
        held[0] += 1.0
        held[1] += number
        held[2] += number * number
    return out


def _copy_and_chi_square(real: str, twin: str, group: str, value: str) -> "tuple[float, float]":
    """The copy ratio of the twin's standardized group means on the real table's (1 a copy, 0 independent) and the
    twin's group chi-square, `sum n (m_g - m)^2 / var` (k - 1 expected where nothing is associated)."""
    r, t = _group_means(real, group, value), _group_means(twin, group, value)
    levels = sorted(set(r) & set(t))

    def centred(acc: "dict[str, list[float]]") -> "tuple[dict[str, float], float]":
        n = sum(acc[k][0] for k in levels)
        mean = sum(acc[k][1] for k in levels) / n
        return {k: acc[k][1] / acc[k][0] - mean for k in levels}, sum(acc[k][2] for k in levels) / n - mean * mean

    rc, rv = centred(r)
    tc, tv = centred(t)
    rs = {k: rc[k] / math.sqrt(rv) for k in levels}
    ts = {k: tc[k] / math.sqrt(tv) for k in levels}
    ratio = sum(t[k][0] * ts[k] * rs[k] for k in levels) / sum(t[k][0] * rs[k] * rs[k] for k in levels)
    return ratio, sum(t[k][0] * tc[k] ** 2 for k in levels) / tv
