"""G16.3's GROUPING GATE on independent columns at 20,000 rows (lane CHG, plan P4-D492; LANE CHG RULINGS 1 (8)).

The gate's unit cases at the table floor, in a file of their own beside tests/test_polish_grouping_gate.py so that
each file stays under the suite's three CPU minutes. Two invented families, every column drawn from a stream of its
own (`_family_text`): a 12-level label and a skewed number blank on about a third of its rows, and the same with a
binary of share 0.2, at table seeds 1 to 12, each described with the chain (the fixed test key, one row a person)
and generated at twin seed 0. WHAT IS HELD, each red on lane CHON's head `875b1b93` and on the gate's mutants (the
gate off; a dropped target kept with a goal of nought): wherever the chain is drawn the head aims at the label's and
the binary's chance groupings and the gated plan at none, and over those tables the gated twin's group means of the
number by the label copy the real table's chance pattern less than half way, at a fresh draw's distance.
"""

import pytest
import test_polish_grouping_gate as gate

from synthtwin import generation, rendering

FAMILIES = {"U2s": ["ward", "marker"], "U3": ["ward", "marker", "flag"]}
TABLE_SEEDS = range(1, 13)


@pytest.fixture(scope="module")
def independent_families(tmp_path_factory: pytest.TempPathFactory) -> "dict[tuple[str, int], dict[str, object]]":
    """Each invented family at 20,000 rows, table seeds 1 to 12, every column drawn independently: whether its chain
    is drawn, the grouping targets the plan aims at with the gate on and off, and, where drawn, the twin's (twin seed
    0) copy ratio and group chi-square of the number's means in the label's groups. Measured once for the module."""
    folder = tmp_path_factory.mktemp("families")
    found: "dict[tuple[str, int], dict[str, object]]" = {}
    for family, columns in FAMILIES.items():
        for seed in TABLE_SEEDS:
            text = gate._family_text(20000, seed, columns)
            loaded = gate._chained(folder / f"{family}-{seed}", f"{family.lower()}{seed}", text)
            if loaded is None:
                found[(family, seed)] = {"drawn": False}
                continue
            with pytest.MonkeyPatch.context() as local:
                local.setattr(generation, "_POLISH_GATE", False)
                head = generation._polish_layout(loaded).plan
            gated = generation._polish_layout(loaded).plan
            twin = rendering.twin_csv(generation.generate(loaded, 0))
            ratio, square = gate._copy_and_chi_square(text, twin, "ward", "marker")
            found[(family, seed)] = {
                "drawn": True, "ratio": ratio, "square": square,
                "gated": [(name, t.kind) for name, targets in gated for t in targets if t.kind != "pair"],
                "head": [(name, t.kind) for name, targets in head for t in targets if t.kind != "pair"],
            }
    return found


def test_no_chance_grouping_target_on_independent_columns_at_20000_rows(
    independent_families: "dict[tuple[str, int], dict[str, object]]",
) -> None:
    """On every invented table of the two families at 20,000 rows (table seeds 1 to 12) whose chain is drawn, the head
    aims at the label's and the binary's chance groupings (one target on the first family, five on the second) and
    the gated plan at none, so nothing of the table's chance pattern is copied; a table whose chain's keyed choice
    draws no family publishes nothing between columns and is not polished either way (two of the first family's)."""
    drawn = {key: one for key, one in independent_families.items() if one["drawn"]}
    assert len(drawn) >= 16, sorted(independent_families)
    for key, one in drawn.items():
        assert one["gated"] == [], key
        assert len(one["head"]) >= 1, (key, one["head"])  # type: ignore[arg-type]


def test_the_twin_s_group_means_stand_at_a_fresh_draw_s_distance_at_20000_rows(
    independent_families: "dict[tuple[str, int], dict[str, object]]",
) -> None:
    """Over the same tables whose chain is drawn, the gated twin's means of the number in the label's groups copy the
    real table's chance pattern less than half way (mean copy ratio under 0.5; measured 0.45 over 22 tables, the
    head's twin 0.92) and stand at a fresh draw's distance (mean group chi-square under 13 on 11 degrees of freedom;
    measured 11.8, the head's twin 14.6, the real tables 10.9). What copying remains is the walk's (each family table
    is the real table's own, its rows dealt on fresh scores): with no target kept, nothing is polished."""
    drawn = [one for one in independent_families.values() if one["drawn"]]
    ratios = [float(one["ratio"]) for one in drawn]  # type: ignore[arg-type]
    squares = [float(one["square"]) for one in drawn]  # type: ignore[arg-type]
    assert sum(ratios) / len(ratios) < 0.5, ratios
    assert sum(squares) / len(squares) < 13.0, squares
