"""G16.3's SPREAD TEST (lane CHG-b, plan P4-D492 part b; LANE CHG RULINGS 2 (2)(c)): a number whose spread differs between
a grouping's bands, with no difference in its mean, keeps that grouping's spreads.

THE DEFECT IT CLOSES (lane CHG's skeptic 1, item 1): the grouping gate reads a `within` target's band MEANS alone, so
a measurement spread 0.25 in six wards and 0.9 in six, its means flat, was dropped whole and its band spreads left to
the walk: the twin's ratio of the wide wards' spread to the narrow ones' 1.02 against the table's 3.52.

THE PRICE, MEASURED FIRST (the ruling's condition, "built only at 0 chance targets kept"): on the three null tables'
route-S descriptions (ST5, table seeds 1 to 3, 98 `within` entries of a number each, every one chance) the test keeps
none; the normal-theory spread chi-square keeps 14, 10 and 14 (the skewed codes' heavy tails). The test reads the
column's published kurtosis for those tails: each band's log variance weighted by its readings less one over two plus
the excess kurtosis.

WHAT IS HELD, each red on its mutant:
- on published-fact inputs (a spread by group, a skewed column's chance spreads, flat spreads, no kurtosis
  published), the statistic and the decision are the oracle's to the bit; the means' own test drops all four;
- at 20,000 rows, a table whose `temp` spreads by ward and whose `marker` (a skewed number) does not: the plan holds
  `temp`'s target on `ward` (its means held at the walk's level, its spreads aimed at) and nothing of `marker` on
  `ward`; the twin's spread ratio moves as far as the polish's frame allows (the ungated polish's 1.26 against the
  gated twin's 1.08 without the test; the table 3.61, which needs the chain to read the ward finer); `marker`'s ratio
  stays a fresh draw's.
"""

import json
import math
import pathlib
import random

import pytest

from synthtwin import chain_moments, contract, generation

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
FROZEN = json.loads((REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))["chain"]


def _load(name):  # type: ignore[no-untyped-def]
    import importlib.util

    spec = importlib.util.spec_from_file_location("chgbs_" + name, REPOSITORY / "tools" / "reference" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


def test_the_spread_test_is_the_oracle_s_on_published_facts() -> None:
    """Each published-fact input read as a `within` target: the spread statistic and decision are the oracle's bits, and
    the band means' own test drops every one (the means flat). The by-group spreads are kept (about 4,539 against the
    point on eleven degrees of freedom), the skewed column's chance spreads dropped (about 12: its kurtosis of 29 makes a
    band's log variance that much less sure), flat spreads dropped, and no kurtosis published means no test; the
    functions call no `math` function."""
    oc = _load("oracle_cases")
    frozen = FROZEN["polish_spread"]
    for label, groups, column, kurtosis in oc.polish_spread_inputs():
        mean, sd, n = column
        entry = contract.MomentColumn(
            "T", chain_moments.KIND_NUMBER, n, mean=mean / chain_moments.unit(chain_moments.SCALE_MEAN, n),
            sd=sd / chain_moments.unit(chain_moments.SCALE_COLUMN_SPREAD, n), clip=(0.0, 255.0))
        within = contract.MomentWithin("T", "W", tuple(
            contract.MomentGroup(g[0], mean=g[1] / chain_moments.unit(chain_moments.SCALE_MEAN, g[0]),
                                 sd=g[2] / chain_moments.unit(chain_moments.SCALE_SPREAD, g[0])) for g in groups), 1)
        target = generation._within_target(entry, within, "within", "W")
        assert target is not None
        published = None if kurtosis is None else float(kurtosis)
        found = generation._spread_statistic(target, published)
        expect = frozen[label]
        assert (None if found is None else found[0].hex()) == expect["statistic"], label
        assert generation._spreads_beyond_chance(target, published) is expect["kept"], label
        assert generation._beyond_chance(within, target.goal) is expect["means_kept"] is False, label
    assert [label for label, e in frozen.items() if e["kept"]] == ["by_group"]
    import inspect

    for function in (generation._spread_statistic, generation._spreads_beyond_chance):
        assert "math." not in inspect.getsource(function), function.__name__


WARDS = [f"w{k:02d}" for k in range(12)]


def _spread_text(rows: int, seed: int) -> str:
    """`ward` (12 equal levels), `temp` 37.0 plus a normal draw of spread 0.25 in wards 0 to 5 and 0.9 in wards 6 to 11
    (one decimal), and `marker`, a skewed reading (a log-normal draw, one decimal) apart from both, each column from a
    stream of its own."""
    draws = {name: random.Random(seed * 7919 + at) for at, name in enumerate(("ward", "temp", "marker"))}
    out = ["ward,temp,marker"]
    for _row in range(rows):
        ward = draws["ward"].randrange(12)
        spread = 0.25 if ward < 6 else 0.9
        temp = 37.0 + draws["temp"].gauss(0.0, spread)
        marker = math.exp(draws["marker"].gauss(1.5, 0.9))
        out += [f"{WARDS[ward]},{temp:.1f},{marker:.1f}"]
    return "\n".join(out) + "\n"


def _ratio(text: str, column: str) -> float:
    """The ratio of a column's spread in wards 6 to 11 to its spread in wards 0 to 5."""
    lines = text.splitlines()
    head = lines[0].split(",")
    w_at, v_at = head.index("ward"), head.index(column)
    wide, narrow = [], []
    for line in lines[1:]:
        cells = line.split(",")
        if cells[v_at] == "":
            continue
        (wide if int(cells[w_at][1:]) >= 6 else narrow).append(float(cells[v_at]))

    def sd(values: "list[float]") -> float:
        m = sum(values) / len(values)
        return math.sqrt(sum((v - m) ** 2 for v in values) / (len(values) - 1))

    return sd(wide) / sd(narrow)


def test_a_spread_by_group_comes_back_and_a_chance_one_stays_away(tmp_path: pathlib.Path,
                                                                  monkeypatch: pytest.MonkeyPatch) -> None:
    """At 20,000 rows, described with the chain under the fixed test key: the plan holds `temp`'s target on `ward` as a
    held feature with its band spreads (the ward's published bands, eleven at this seed: two wards share one; the means
    flat, so the means' test drops it) and nothing of `marker` on `ward`. The twin at seed 0 moves `temp`'s spread ratio
    as far as the polish's frame allows: the chain draws `temp` from `ward`'s two coarsest bands, which do not part the
    narrow wards from the wide ones (the walk alone 1.02 against the table's 3.61), and the polish moves a value only
    inside its own band of `temp`; with the test the ratio reads the ungated polish's (1.26, lane MPg's polish aiming at
    every target) and more than 0.1 over the gated twin without it (1.08); `marker`'s ratio stays near one on all three.
    Reproducing the table's ratio needs the chain to read `ward` finer (a stated limit of the walk)."""
    import test_polish_grouping_gate as gate

    from synthtwin import rendering

    text = _spread_text(20000, 3)
    loaded = gate._chained(tmp_path / "spread", "spread", text)
    assert loaded is not None
    plan = dict(generation._polish_layout(loaded).plan)
    temp = [t for t in plan.get("temp", []) if t.kind == "within" and t.name == "ward"]
    assert len(temp) == 1 and temp[0].held and len(temp[0].sds) == len(temp[0].counts) >= 10, plan.get("temp")
    assert not [t for t in plan.get("marker", []) if t.name == "ward" and t.kind == "within"]

    def twin_with(setting: str, value: bool) -> str:
        with monkeypatch.context() as local:
            local.setattr(generation, setting, value)
            return "".join(rendering.twin_csv_pieces(generation.generate_held(loaded, 0)))

    real = _ratio(text, "temp")
    twin = "".join(rendering.twin_csv_pieces(generation.generate_held(loaded, 0)))
    without = twin_with("_POLISH_SPREAD_TEST", False)
    ungated = twin_with("_POLISH_GATE", False)
    assert real > 3.0, real
    assert _ratio(twin, "temp") - _ratio(without, "temp") > 0.1, (_ratio(twin, "temp"), _ratio(without, "temp"))
    assert abs(_ratio(twin, "temp") - _ratio(ungated, "temp")) <= 0.05, (_ratio(twin, "temp"), _ratio(ungated, "temp"))
    for version in (twin, without, ungated):
        assert abs(_ratio(version, "marker") - 1.0) < 0.1, _ratio(version, "marker")
