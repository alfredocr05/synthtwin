"""The review of landing 3b.G1 (plan P4-D375), items 2 to 4, each reproduced and pinned.

Item 1 -- a description written before the plan loads -- has its own
file, `tests/test_p4d375_earlier_descriptions.py`, because it holds
668f276's document whole.

- ITEM 2 (MEDIUM): `K-S3-50` recorded 35.7 % of the span as the furthest
  a numeric twin writes past the real range, and an evenly spaced
  column reaches further. The review's 101 measurements 0.25 to 25.25,
  two decimals, at a floor of 50: every twin writes 0.01 to 41.43, the
  maximum 64.7 % of the span past the real one; the mean comes back
  13.029 for 12.75, the spread 7.865 for 7.325, the skew 0.378 for 0 and
  the kurtosis 3.08 for 1.80, every one WITHIN-BOUND and nothing MISSED.
  The cause is the outward move of method G5.3b step 4 (`d1 * H(rows)`,
  where the largest of `rows` draws of an exponential tail of that mean
  is expected), made whatever the fitted power: the high tail fits power
  0, its outermost row reads the real maximum exactly, and the move
  stands it 28.68 past its boundary of 12.75; 668f276 writes the same
  twin, so it is not a regression of the landing. It is
  RECORDED, not repaired: `K-S3-50` counts these twins apart under
  `grid_*` keys, and the test below holds the review's column to the
  ceiling the ledger records, which on 110cb46 was 357 and failed.
- ITEM 3 (MEDIUM): a checked file whose own tail pair binary64 cannot
  hold, on a role whose producer writes no reason remark, was explained
  by the deleted rules -- "withholds them where they would give back an
  outer cell or how many outer cells hold one value ... or where beside
  the exact mean and spread they could give the other tail's back".
  The file's own description is the current producer's, whose one reason
  is the pair binary64 cannot hold, and that is what is said now.
- ITEM 4 (MEDIUM): three surfaces still described the withdrawn
  protection as current -- STATE said `edge_pinned` is 0 where the
  ledger records 14, and called the cost rule active and a date one
  forthcoming; `K-S3-13`'s evidence said 38 tails still go to the
  back-solve the landing deleted; and `taxonomy._tail_side` said a pair
  never names a row, which is false on a table sorted by that column.
"""

from __future__ import annotations

import pathlib

import kpi_rules
import kpi_shapes
from synthtwin import parsing, taxonomy, validation

ROOT = pathlib.Path(__file__).resolve().parents[1]


def _ledger_entry(entry_id: str) -> "dict":
    return kpi_rules.entries_by_id(kpi_rules.load_ledger())[entry_id]


# -- item 2 ---------------------------------------------------------------


def _grid_table() -> str:
    return "measurement\n" + "".join(f"{0.25 * (step + 1):.2f}\n" for step in range(101))


def _numbers(text: str) -> "list[float]":
    found: "list[float]" = []
    for line in text.split("\n")[1:]:
        number = parsing.parse_number(line) if line else None
        if number is not None:
            found += [number]
    return found


def test_an_evenly_spaced_column_reaches_past_its_range_within_k_s3_50s_ceiling(tmp_path) -> None:
    """The review's column at a floor of 50: 64.7 % of the span past the real maximum, nothing MISSED.

    The overshoot is held to the furthest `K-S3-50` records for any of
    its batteries, so a reach beyond what the ledger says turns this red
    -- on 110cb46, whose ledger said 357 thousandths, it did. Its moments
    stand inside their windows, which is why no check sees it.
    """
    described = kpi_shapes.describe(tmp_path, "grid", _grid_table(), 50)
    real = _numbers(_grid_table())
    expected = _ledger_entry("K-S3-50")["expected"]
    ceiling = max(expected[key] for key in expected if key.endswith("overshoot_permille"))
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        twin = _numbers(text)
        past = max(twin) - max(real)
        permille = int(round(1000.0 * past / (max(real) - min(real))))
        assert permille == 647, (seed, min(twin), max(twin))
        assert permille <= ceiling, (permille, ceiling)
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        assert [check.subcheck for check in outcome.checks if check.verdict == validation.MISSED] == []
        moments = {check.subcheck: check.verdict for check in outcome.checks if check.subcheck.startswith("moments.")}
        assert moments["moments.mean"] == validation.WITHIN_BOUND, moments
        assert moments["moments.std"] == validation.WITHIN_BOUND, moments


# -- item 3 ---------------------------------------------------------------


def test_a_file_tail_binary64_cannot_hold_is_explained_by_that_and_not_by_the_withdrawn_rules(tmp_path) -> None:
    """The review's affixed column: both pair checks WITHHELD, each saying the numbers are too large.

    Described from "100 mg" to "199 mg"; the checked file holds eleven
    cells near -1.7e308 and eighty-nine near 1.68e308, so its own lower
    tail's pair overflows binary64 and its own description withholds it.
    """
    described = kpi_shapes.describe(tmp_path, "dose", "dose\n" + "".join(f"{100 + step} mg\n" for step in range(100)), None)
    assert described.document["columns"][0]["role"] == taxonomy.ROLE_AFFIXED, "premise: an affixed column"
    cells = [repr(-1.7e308 + step * 1e305) + " mg" for step in range(11)]
    cells += [repr(1.68e308 + step * 1e304) + " mg" for step in range(89)]
    outcome = kpi_shapes.measure(described, "dose\n" + "".join(cell + "\n" for cell in cells), "checked.csv")
    withheld = [check for check in outcome.checks if check.verdict == validation.WITHHELD]
    assert sorted(check.subcheck for check in withheld) == ["tails.low.mean_distance", "tails.low.rms_distance"]
    for check in withheld:
        assert "too large for this file format to hold" in check.citation, check.citation
        assert "outer cell" not in check.citation and "other tail" not in check.citation, check.citation


# -- item 4 ---------------------------------------------------------------


def test_state_says_what_the_ledger_records_of_the_published_pairs() -> None:
    """STATE does not say `edge_pinned` is 0 while `K-S3-11` records more, nor call the cost rule live."""
    state = (ROOT / "docs" / "STATE.md").read_text(encoding="utf-8")
    flat = " ".join(state.split())
    edge = _ledger_entry("K-S3-11")["value_at"]["value"]["edge_pinned"]
    assert edge > 0, "premise: the ledger records edge-pinned tails"
    assert "`edge_pinned` is 0" not in flat
    assert f"{edge} edge-pinned" in flat
    assert "a withheld tail pair is published wherever withholding it would leave" not in flat
    assert "its own cost rule is a later landing" not in flat


def test_k_s3_13_does_not_claim_the_back_solve_the_landing_removed() -> None:
    """`K-S3-13`'s evidence names no back-solve its nodes run: the test that ran it is gone."""
    entry = _ledger_entry("K-S3-13")
    assert "put to the back-solve across" not in entry["evidence"]
    gate = (ROOT / "tests" / "test_stage3_gate.py").read_text(encoding="utf-8")
    assert "def test_no_tail_of_the_battery_back_solves_to_the_value_it_withheld" not in gate


def test_the_tail_producer_states_the_sorted_table_exception() -> None:
    """`taxonomy._tail_side` says a pair names no row EXCEPT on a table sorted by that column."""
    said = " ".join((taxonomy._tail_side.__doc__ or "").split())
    assert "it never names a row or another column" not in said
    assert "never a row EXCEPT on a table sorted by that column" in said
    assert "`row_order`" in said
