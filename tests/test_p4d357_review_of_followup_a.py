"""Plan P4-D357 A: the review of follow-up A (P4-D353), item by item.

1. THE COST RULE DECIDES ON THE BLOCK THE LOADER READS. An affixed column
   wearing one wrapper set its two cell-population keys after the tail
   rule had run, so the rule asked the windows of a block nobody reads:
   `1 mg` to `99 mg`, `210 mg` and one text cell published the high
   tail's pair at a floor of eleven where the published block, both
   pairs withheld, keeps both moments. Held for every nested numeric
   role by asking, of each block a cost-rule call returns, that it IS
   the block published and that the call asked the loader's own reading
   of it.

Every table is built at test time from a fixed seed string or a closed
formula; no data-format file enters the repository (plan D13).
"""

from __future__ import annotations

import copy
import dataclasses
import pathlib
import random

import pytest

import cost_rule_window as window
import kpi_shapes
from synthtwin import contract, taxonomy, validation


def _one_column(cells: "list[str]") -> str:
    return "value\n" + "\n".join(cells) + "\n"


# -- 1. the cost rule decides on the final block ------------------------------

# The review's shape: ninety-nine consecutive amounts and one far one, each
# wearing ` mg`, beside one cell of ordinary text.
_REVIEW_AFFIXED = [f"{value} mg" for value in range(1, 100)] + ["210 mg", "review_marker"]


def _loader_windows(described: kpi_shapes.Described, block: "dict") -> "dict[str, bool]":
    """Per moment, does the window the LOADER's reading of this column draws miss its value?"""
    facts = described.loaded.columns[0].facts
    assert isinstance(facts, contract.AffixedFacts)
    drawn = validation._windows_of(None, facts.numbers, described.loaded.settings.small_cell_floor)
    return {
        name: name in drawn and not drawn[name][0] <= block[name] <= drawn[name][1]
        for name in ("mean", "std")
    }


def test_an_affixed_pair_is_published_only_where_the_published_block_would_miss(
    tmp_path: pathlib.Path,
) -> None:
    """The review's affixed column withholds both pairs: its final block keeps both moments without them.

    PREMISE, from the checker's own windows over the loaded block: with
    neither pair the mean and the spread both lie inside their windows. So
    the owner's "only where it costs" publishes neither, and the twin still
    meets both moments at seeds 0, 4 and 9. On the base 2af1f03 the high
    pair was published, decided on a block whose `n_left_out_of_statistics`
    still read 0 and whose spread window ended at 32.734867, short of the
    published 32.751590.
    """
    described = kpi_shapes.describe(tmp_path, "affixed", _one_column(_REVIEW_AFFIXED), 11)
    block = described.document["columns"][0]
    assert block["role"] == "affixed_number" and block["n_left_out_of_statistics"] == 1, (
        "premise: one straggler beside a hundred cores"
    )
    assert _loader_windows(described, window.withheld(block, ("low", "high"))) == {
        "mean": False,
        "std": False,
    }, "premise: the final block with both pairs withheld keeps both moments"
    published = [side for side in ("low", "high") if block["tails"][side]["mean_distance"] is not None]
    assert published == [], f"the rule published {published} where withholding costs nothing"
    for seed in (0, 4, 9):
        text = kpi_shapes.twin_text(described, seed)
        outcome = kpi_shapes.measure(described, text, f"twin-{seed}.csv")
        moments = [one for one in kpi_shapes.missed(outcome) if "moments." in one]
        assert moments == [], f"seed {seed}: {moments}"


def _nested_blocks(block: "dict") -> "list[tuple[str, dict]]":
    """Every numeric block a published column holds, named."""
    role = block["role"]
    if role in (taxonomy.ROLE_COUNT, taxonomy.ROLE_CONTINUOUS):
        return [("column", block)]
    if role == taxonomy.ROLE_AFFIXED:
        found = [("commonest wrapper", block)]
        for place, entry in enumerate(block["affix_variants"]):
            found += [(f"wrapper {place}", entry["numbers"])]
        return found
    if role == taxonomy.ROLE_JOINED:
        return [(f"part {place}", part) for place, part in enumerate(block["parts"])]
    if role == taxonomy.ROLE_COMPOUND:
        return [("numbers", block["numbers"])]
    return []


def _nested_facts(facts: object) -> "list[contract.NumericFacts]":
    """The loader's reading of each block `_nested_blocks` names, in the same order."""
    if isinstance(facts, contract.NumericFacts):
        return [facts]
    if isinstance(facts, contract.AffixedFacts):
        return [facts.numbers] + [entry.numbers for entry in facts.affix_variants]
    if isinstance(facts, contract.JoinedFacts):
        return list(facts.parts)
    if isinstance(facts, contract.CompoundFacts):
        return [facts.numbers]
    return []


def _spelling_free(facts: contract.NumericFacts) -> contract.NumericFacts:
    """The facts without a count column's spelling census, which the role adds after the block."""
    return dataclasses.replace(facts, number_spellings={})


_CORES = [str(value) for value in range(1, 100)] + ["210"]


def _pairs() -> "list[str]":
    draw = random.Random("p4d357/joined")
    return [f"{core}/{draw.randint(40, 90)}" for core in _CORES]


# (name, cells, the role): every role whose block holds a numeric block with
# tails, each beside cells its population keys count and its cores do not.
_NESTED_SHAPES = (
    ("count_beside_text", _CORES + ["review_marker"], taxonomy.ROLE_COUNT),
    ("continuous_beside_text", [f"-{core}" for core in _CORES] + ["review_marker"], taxonomy.ROLE_CONTINUOUS),
    ("affixed_beside_text", _REVIEW_AFFIXED, taxonomy.ROLE_AFFIXED),
    ("affixed_beside_a_bare_number", [f"{core} mg" for core in _CORES] + ["300"], taxonomy.ROLE_AFFIXED),
    ("affixed_two_wrappers", [f"{core} mg" for core in _CORES] + [f"{core} kg" for core in _CORES] + ["review_marker"], taxonomy.ROLE_AFFIXED),
    ("joined_beside_text", _pairs() + ["review_marker"], taxonomy.ROLE_JOINED),
    ("joined_far_in_both", [f"{core}/{core}" for core in _CORES] + ["review_marker"], taxonomy.ROLE_JOINED),
    ("numbers_beside_labels", _CORES + ["absent"] * 12, taxonomy.ROLE_COMPOUND),
)


@pytest.mark.parametrize("name,cells,role", _NESTED_SHAPES, ids=[case[0] for case in _NESTED_SHAPES])
def test_every_nested_block_the_cost_rule_decides_is_the_block_the_loader_reads(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, name: str, cells: "list[str]", role: str
) -> None:
    """Each block a cost-rule call returns IS the nested block published, and the call asked its loaded reading.

    Two halves, and each is a way the producer's question can part from the
    checker's: a key set on the block after the rule ran (review item 1:
    the affixed column's two cell-population keys), and a count handed to
    the loader's reading that is not the one the loader uses for that
    block (`taxonomy._Population`). The memo is emptied before every call,
    so every candidate is asked afresh.
    """
    asked: "list[contract.NumericFacts]" = []
    returned: "list[tuple[dict, list[contract.NumericFacts]]]" = []
    reading = contract.numeric_block_facts
    deciding = taxonomy._pairs_that_cost

    def spy_reading(*arguments: object, **named: object) -> contract.NumericFacts:
        found = reading(*arguments, **named)  # type: ignore[arg-type]
        asked.extend([found])
        return found

    def spy_deciding(*arguments: object, **named: object) -> "dict":
        taxonomy._MOMENTS_MISSED.clear()
        start = len(asked)
        found = deciding(*arguments, **named)  # type: ignore[arg-type]
        returned.extend([(copy.deepcopy(found), list(asked[start:]))])
        return found

    monkeypatch.setattr(contract, "numeric_block_facts", spy_reading)
    monkeypatch.setattr(taxonomy, "_pairs_that_cost", spy_deciding)
    described = kpi_shapes.describe(tmp_path, name, _one_column(cells), 11)
    block = described.document["columns"][0]
    assert block["role"] == role, f"premise: read as {role}, not {block['role']}"
    blocks = _nested_blocks(block)
    loaded = _nested_facts(described.loaded.columns[0].facts)
    assert len(blocks) == len(loaded)
    decided = 0
    for (label, published), facts in zip(blocks, loaded):
        mine = [
            (answer, readings)
            for answer, readings in returned
            if answer["tails"] == published["tails"]
            and answer["percentiles"] == published["percentiles"]
            and answer["mean"] == published["mean"]
        ]
        if not mine:
            continue
        decided = decided + 1
        for answer, readings in mine:
            moved = [key for key in answer if key not in published or published[key] != answer[key]]
            assert moved == [], f"{label}: set after the cost rule decided: {moved}"
            assert _spelling_free(facts) in [_spelling_free(one) for one in readings], (
                f"{label}: the cost rule asked a reading the loader does not make of the published block"
            )
    assert decided > 0, "premise: the cost rule decided at least one published block"


# -- 4. the cross-side closure, whatever withheld the first side ---------------


def _far_apart(low_first: bool) -> "list[str]":
    """Eleven values near `-1.7e308` beside 89 near `1.68e308` (the review's item 4), or its mirror."""
    near = [str((-17000 + place) * 1e304) for place in range(11)]
    far = [str((16800 + place) * 1e304) for place in range(89)]
    if low_first:
        return near + far
    return [str(-float(cell)) for cell in near + far]


@pytest.mark.parametrize("unheld", ("low", "high"))
def test_a_side_binary64_cannot_hold_closes_the_other_side_s_pair(
    tmp_path: pathlib.Path, monkeypatch: pytest.MonkeyPatch, unheld: str
) -> None:
    """The other side's pair is withheld, and says why, where it keeps no moment.

    PREMISE: the far side's own pair is too large for binary64 (its remark
    says so) and the other side's back-solve leaves it open. The cross-side
    rule (plan P4-D353 part 2) withholds that open pair wherever the rule
    publishes nothing, and it asks nothing about why the first side has no
    pair: on 2af1f03 the pair was published, about `6.38e304` and
    `7.254e304`, and the checker's windows missed both moments with it and
    without it.
    """
    other = "high" if unheld == "low" else "low"
    cells = _one_column(_far_apart(unheld == "low"))
    with monkeypatch.context() as patched:
        patched.setattr(taxonomy, "_pairs_that_cost", lambda _cells, shaped, *_rest: shaped)
        opened = kpi_shapes.describe(tmp_path / "open", "far", cells, 11).document["columns"][0]
    described = kpi_shapes.describe(tmp_path, f"far-{unheld}", cells, 11)
    block = described.document["columns"][0]
    remarks = block["remarks"]
    assert taxonomy.tail_withheld_because(remarks, unheld) == taxonomy.TAIL_WITHHELD_UNHOLDABLE, (
        "premise: binary64 cannot hold the far side's pair"
    )
    assert opened["tails"][other]["mean_distance"] is not None, "premise: the other side's own walk leaves it open"
    assert window.missed(opened, 11) == window.missed(block, 11), "premise: the pair keeps no moment the closure loses"
    assert block["tails"][other]["mean_distance"] is None, (
        f"the {other} side published its pair beside a side binary64 cannot hold"
    )
    assert taxonomy.tail_withheld_because(remarks, other) == taxonomy.TAIL_WITHHELD_FOR_THE_OTHER
