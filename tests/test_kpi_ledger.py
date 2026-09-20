"""Every KPI the ledger measures with a test of its own.

`tests/kpi/ledger.json` is the record of what each phase and stage
delivered, stated as a number and a rule. An entry marked
`NEW_FAST_TEST` there owns exactly one function here, named after its id
(`K-P2-05` -> `test_k_p2_05`), and `tests/test_kpi_ledger_integrity.py`
holds the two sets equal.

Each test MEASURES, RECORDS AND JUDGES, in that order:

* it measures the value on the product's own path -- the real reader,
  producer, loader, generator and validator, nothing stubbed -- from a
  seeded shape in `tests/kpi_shapes.py`;
* it records the value with pytest's `record_property("kpi", ...)`, so
  `tools/measurements/kpi_run.py` can print the number and not only a
  pass or a fail;
* it judges the value with `kpi_rules.judge` against the ledger's own
  rule, so this file and the runner can never judge one value two ways.

A GREEN entry fails here when its rule fails. An OPEN or ACCEPTED_LIMIT
entry fails only when its value is WORSE than its must-not-get-worse
bound; it passes while it is held, which keeps the suite green while the
owner's board shows the entry open. Moving a bound is an edit to the
ledger, in a commit whose CHANGELOG entry names the id.
"""

from __future__ import annotations

import ast
import collections
import csv
import datetime
import importlib.util
import io
import json
import os
import pathlib
import random
import shutil
import statistics
import subprocess
import sys
import time

import pytest

import fixtures
import kpi_rules
import kpi_shapes as S
from synthtwin import (
    contract,
    generation,
    parsing,
    rendering,
    taxonomy,
)

LEDGER = kpi_rules.load_ledger()
ENTRIES = kpi_rules.entries_by_id(LEDGER)
REPO = kpi_rules.REPO_ROOT


def _kpi(record_property, entry_id: str, value: object, detail: str = "") -> None:
    """Record the measured value, then judge it by the ledger's rule."""
    entry = ENTRIES[entry_id]
    record_property(
        "kpi", json.dumps({"id": entry_id, "value": value, "detail": detail}, sort_keys=True)
    )
    # Every key of the rule this test measures must be recorded: a key it
    # stops recording fails here, not only in the runner. Only an entry
    # whose driver measures the rest is judged in part.
    verdict = kpi_rules.judge(
        kpi_rules.test_part(entry), value, kpi_rules.seconds_judged_here(LEDGER)[0],
        partial=bool(entry.get("driver")),
    )
    assert not verdict.is_drop, (
        f"{entry_id} ({entry['name']}): {verdict.word}: {verdict.message}. "
        f"Measured {value!r}; the ledger's rule is: {entry['rule']}"
    )


def _load_tool(relative: str, name: str) -> object:
    """A script under tools/ loaded as a module, without adding tools/ to the path."""
    spec = importlib.util.spec_from_file_location(name, REPO / relative)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# -- shared runs, built once per module ----------------------------------


@pytest.fixture(scope="module")
def every_role(tmp_path_factory: pytest.TempPathFactory) -> "dict":
    """The every-role table described at the shipped floor (1) and at 11, headed."""
    home = tmp_path_factory.mktemp("kpi-every-role")
    return {floor: S.every_role(home / f"f{floor}", floor) for floor in (1, 11)}


@pytest.fixture(scope="module")
def every_role_twins(every_role: "dict") -> "dict":
    """The twin text at the golden seed and at seeds 1 and 2, for both floors."""
    return {
        (floor, seed): S.twin_text(every_role[floor], seed)
        for floor in (1, 11)
        for seed in (S.GOLDEN_SEED, 1, 2)
    }


@pytest.fixture(scope="module")
def eight(tmp_path_factory: pytest.TempPathFactory) -> "list[dict]":
    """The eight realistic shapes through a whole run at floors 1 and 11 (K-2B-40 and kin)."""
    return S.eight_shapes(tmp_path_factory.mktemp("kpi-eight-shapes"), (1, 11))


def _tag(run: "dict") -> str:
    return f"{run['family']}_{run['kind']}_f{run['floor']}"


# -- Phase 0 --------------------------------------------------------------


def test_k_p0_05(record_property) -> None:
    """The decontamination scan walks the repository, not nothing (non-vacuity half)."""
    check = _load_tool("tools/decontamination/check.py", "kpi_decontamination_check")
    listed = check.tracked_files(REPO)  # type: ignore[attr-defined]
    _kpi(record_property, "K-P0-05", {"files_listed": len(listed)})


def test_k_p0_07(record_property) -> None:
    """The signed attestation verifies end to end: signature, shape, tree, manifest."""
    if shutil.which("ssh-keygen") is None:
        pytest.skip("ssh-keygen is not installed here, so the signature cannot be checked")
    verify = _load_tool(
        "tools/decontamination/verify_attestation.py", "kpi_verify_attestation"
    )
    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(sys, "stdout", io.StringIO())
        code = verify.main()  # type: ignore[attr-defined]
    _kpi(record_property, "K-P0-07", {"exit": code})


# -- Phase 1 --------------------------------------------------------------


def _steps_apart(computed: float, expected: float) -> int:
    import struct

    def place(value: float) -> int:
        bits = struct.unpack("<Q", struct.pack("<d", value))[0]
        magnitude = bits & 0x7FFF_FFFF_FFFF_FFFF
        return -magnitude if bits >> 63 else magnitude

    return abs(place(computed) - place(expected))


def test_k_p1_04(record_property) -> None:
    """Mean, SD, skewness and 11 rungs against the exact-arithmetic oracle, both row orders."""
    document = json.loads(
        (REPO / "tests" / "reference" / "numeric-reference-vectors.json").read_text("utf-8")
    )
    graded = exact = beyond = order_dependent = 0
    for name in sorted(document["cases"]):
        case = document["cases"][name]
        values = [float(text) for text in case["values_float64_repr"]]
        moments = taxonomy._moments(values)
        ladder = taxonomy._quantiles(values)
        pairs = [(moments["mean"], case["mean"]["float64"])]
        for statistic in ("std", "skew"):
            if case[statistic] is not None:
                pairs += [(moments[statistic], case[statistic]["float64"])]
        for label, _num, _den in taxonomy.LADDER:
            pairs += [(ladder[label], case["ladder_exact_p"][label]["float64"])]
        for computed, expected in pairs:
            graded += 1
            steps = _steps_apart(computed, expected)
            exact += steps == 0
            beyond += steps > 1
        backward = list(reversed(values))
        if taxonomy._moments(backward) != moments or taxonomy._quantiles(backward) != ladder:
            order_dependent += 1
    _kpi(
        record_property,
        "K-P1-04",
        {"graded": graded, "beyond_one_step": beyond, "exact": exact,
         "order_dependent_cases": order_dependent},
    )


# -- Phase 2 --------------------------------------------------------------


def test_k_p2_01(record_property) -> None:
    """The frozen cases and cells have a floor: deleting cases cannot pass by editing G14.3."""
    import test_generation_reference as reference

    cells = sum(len(reference._case(name)["cells"]) for name in reference.ALL_CASES)
    _kpi(
        record_property,
        "K-P2-01",
        {"cases": len(reference.EVERY_CASE), "column_cases": len(reference.ALL_CASES),
         "column_cells": cells},
    )


def _golden_copies(every_role: "dict", every_role_twins: "dict", floor: int) -> "tuple[int, int]":
    real = S.csv_rows(every_role[floor].table)
    twin = list(csv.reader(io.StringIO(every_role_twins[(floor, S.GOLDEN_SEED)], newline="")))
    return S.row_copies(real, twin, real[0].index("record_code"))


def test_k_p2_05(
    record_property, every_role: "dict", every_role_twins: "dict", eight: "list[dict]"
) -> None:
    """No twin row is a real row: the golden table, and the realistic shapes with no identifier."""
    value = {}
    for floor in (1, 11):
        whole, near = _golden_copies(every_role, every_role_twins, floor)
        value[f"golden_f{floor}_whole"] = whole
        value[f"golden_f{floor}_ignoring_identifier"] = near
    for run in eight:
        if run["kind"] == "csv" and not run["family_spec"]["identifier"]:
            whole, _near = S.row_copies(S.csv_rows(run["path"]), S.csv_rows(run["twin"]), None)
            value[f"{_tag(run)}_whole"] = whole
    _kpi(record_property, "K-P2-05", value)


# -- Phase 3 --------------------------------------------------------------


def test_k_p3_02(record_property, every_role: "dict") -> None:
    """The real every-role table, checked against its own description, misses nothing."""
    value = {}
    for floor in (1, 11):
        described = every_role[floor]
        outcome = S.measure(described, described.table.read_text("utf-8"), "real-again.csv")
        value[f"missed_f{floor}"] = outcome.census.missed
        value[f"withheld_f{floor}"] = outcome.census.withheld
        value[f"held_f{floor}"] = outcome.census.held
    _kpi(record_property, "K-P3-02", value)


# -- Phase 4 --------------------------------------------------------------


def test_k_p4_01(
    record_property, every_role: "dict", every_role_twins: "dict",
    tmp_path: pathlib.Path,
) -> None:
    """A twin of the every-role table misses nothing, with no carve-out, headed and headerless."""
    missed: "list[str]" = []
    withheld = runs = 0
    for floor, seed in ((1, S.GOLDEN_SEED), (11, S.GOLDEN_SEED), (11, 1)):
        outcome = S.measure(every_role[floor], every_role_twins[(floor, seed)], f"twin-{seed}.csv")
        missed += [f"headed f{floor} s{seed} {m}" for m in S.missed(outcome)]
        withheld += outcome.census.withheld
        runs += 1
    bare = S.every_role(tmp_path, 11, headed=False)
    outcome = S.measure(bare, S.twin_text(bare, S.GOLDEN_SEED), "bare-twin.csv")
    missed += [f"headerless f11 {m}" for m in S.missed(outcome)]
    withheld += outcome.census.withheld
    runs += 1
    _kpi(record_property, "K-P4-01",
         {"missed": len(missed), "withheld": withheld, "runs": runs}, "; ".join(missed))


def test_k_p4_03(record_property, tmp_path: pathlib.Path) -> None:
    """A column of 19.08.24 is read as dates, and every twin cell parses as %d.%m.%y."""
    described = S.describe(
        tmp_path, "thing",
        fixtures.single_column_table("thing", S.dotted_two_figure_dates()),
    )
    failures = missed = cells = 0
    for seed in (1, 3, 7):
        twin = generation.generate(described.loaded, seed)
        written = [cell for cell in twin.columns[0] if cell]
        cells += len(written)
        for cell in written:
            try:
                datetime.datetime.strptime(cell, "%d.%m.%y")
            except ValueError:
                failures += 1
        missed += len(S.missed(S.measure(described, rendering.twin_csv(twin), f"t{seed}.csv")))
    _kpi(record_property, "K-P4-03",
         {"role_is_date": described.block("thing")["role"] == "datetime",
          "unparsed_cells": failures, "missed": missed, "cells": cells})


def test_k_p4_05(record_property, tmp_path: pathlib.Path) -> None:
    """Blood pressure: 13 first numbers, 9 second, 110 readings, systolic on top, nothing missed."""
    text = "reading\n" + "\n".join(S.pressure_rows()) + "\n"
    described = S.describe(tmp_path, "pressure", text, measured=["reading"])
    column = described.loaded.columns[0]
    firsts, seconds = (part.n_distinct_values for part in column.facts.parts)
    exact_seeds = 0
    missed: "list[str]" = []
    seeds = range(8)
    for seed in seeds:
        twin = generation.generate(described.loaded, seed)
        cells = [cell for cell in twin.columns[0] if cell]
        pairs = [cell.split("/") for cell in cells]
        held = (
            len({parsing.exact_of_spelling(a) for a, _b in pairs}),
            len({parsing.exact_of_spelling(b) for _a, b in pairs}),
            len(set(cells)),
            sum(1 for a, b in pairs if float(a) > float(b)),
        )
        exact_seeds += held == (firsts, seconds, column.n_distinct, column.facts.part_above[0])
        missed += S.missed(S.measure(described, rendering.twin_csv(twin), f"t{seed}.csv"))
    _kpi(record_property, "K-P4-05",
         {"seeds_exact": exact_seeds, "seeds": len(seeds), "missed": len(missed),
          "published": [firsts, seconds, column.n_distinct]}, "; ".join(missed))


def test_k_p4_09(record_property, tmp_path: pathlib.Path) -> None:
    """Dental and vaccine codes keep their field width at every one of 40 seeds."""
    import test_p4d30_field_widths as widths

    value = {}
    for name, rows, prefix, wanted in (
        ("dental", widths._dental_rows(), "D", {4: 300}),
        ("vaccine", widths._vaccine_rows(), "", {3: 230}),
    ):
        _document, loaded = widths._described(tmp_path, name, "code", rows)
        off = [
            seed for seed in range(1, 41)
            if widths._field_widths_of(widths._twin_cells(tmp_path, name, loaded, seed)[0], prefix)
            != wanted
        ]
        value[f"{name}_seeds_off_width"] = len(off)
    _kpi(record_property, "K-P4-09", value)


def test_k_p4_11(record_property, tmp_path: pathlib.Path) -> None:
    """Eighteen coding systems: profiled, generated AND validated, in their own shapes."""
    import test_p4d19_declared_codes as codes

    subset = equal = clean = full = 0
    notes: "list[str]" = []
    for system in sorted(codes._SYSTEMS):
        values = codes._SYSTEMS[system]
        declared = [system] if system in codes._DIGIT_ONLY else []
        described = S.describe(
            tmp_path / system, system,
            fixtures.single_column_table(system, values), floor=1, codes=declared,
        )
        twin = generation.generate(described.loaded, 3)
        real_shapes = {codes._shape(value) for value in values}
        written = {codes._shape(cell) for cell in twin.columns[0]}
        subset += written <= real_shapes
        equal += written == real_shapes
        full += len(twin.columns[0]) == len(values)
        found = S.missed(S.measure(described, rendering.twin_csv(twin), "twin.csv"))
        clean += not found
        if found or written != real_shapes:
            notes += [f"{system}: missed {found}, shapes not written {sorted(real_shapes - written)}"]
    _kpi(record_property, "K-P4-11",
         {"systems": len(codes._SYSTEMS), "shapes_a_subset": subset, "shapes_equal": equal,
          "validate_clean": clean, "rows_kept": full}, "; ".join(notes))


def test_k_p4_17(record_property, tmp_path: pathlib.Path) -> None:
    """A lab column of 295 readings and 5 markers keeps both, and every distinct cell."""
    described = S.describe(
        tmp_path, "result", fixtures.single_column_table("result", S.readings_and_markers())
    )
    block = described.block("result")
    good = missed = 0
    for seed in range(8):
        twin = generation.generate(described.loaded, seed)
        cells = [cell for cell in twin.columns[0] if cell]
        numbers = [cell for cell in cells if parsing.parse_number(cell) is not None]
        found = S.missed(S.measure(described, rendering.twin_csv(twin), f"t{seed}.csv"))
        missed += len(found)
        good += (len(numbers), len(cells) - len(numbers), len(set(cells))) == (
            block["n_numeric_cells"], block["n_label_cells"], block["n_distinct"]
        )
    _kpi(record_property, "K-P4-17",
         {"role": block["role"], "seeds_exact": good, "seeds": 8, "missed": missed})


def test_k_p4_20(record_property) -> None:
    """The shipped smallest group is 1: nothing is held back unless asked."""
    _kpi(record_property, "K-P4-20",
         {"settings_default": taxonomy.Settings().small_cell_floor,
          "contract_default": contract.DEFAULT_SMALL_CELL_FLOOR})


def test_k_p4_22(record_property, every_role: "dict", every_role_twins: "dict") -> None:
    """Clause 3 at the SHIPPED floor: published values held by one row, and the twin writing them."""
    value = {}
    for floor in (1, 11):
        described = every_role[floor]
        real = S.csv_rows(described.table)
        header = real[0]
        tally = {name: collections.Counter(row[i] for row in real[1:]) for i, name in enumerate(header)}
        levels_of_one: "set[tuple[str, str]]" = set()
        for block in described.document["columns"]:
            for level in block.get("levels") or []:
                if isinstance(level, dict) and level.get("count") == 1:
                    levels_of_one.add((block["name"], level["label"]))
        twin = list(csv.reader(io.StringIO(every_role_twins[(floor, S.GOLDEN_SEED)], newline="")))
        written = {
            (header[i], cell) for row in twin[1:] for i, cell in enumerate(row)
        }
        ends_of_one = 0
        for block in described.document["columns"]:
            column = header.index(block["name"])
            for key in ("earliest", "latest"):
                if isinstance(block.get(key), str) and tally[block["name"]][block[key]] == 1:
                    ends_of_one += 1
            ladder = block.get("percentiles")
            if isinstance(ladder, dict) and block["role"] in ("count", "continuous"):
                for key in ("min", "max"):
                    held = sum(
                        1 for row in real[1:]
                        if parsing.parse_number(row[column]) == ladder[key]
                    )
                    ends_of_one += held == 1
        value[f"levels_of_one_f{floor}"] = len(levels_of_one)
        value[f"twin_writes_levels_of_one_f{floor}"] = len(levels_of_one & written)
        value[f"ends_held_by_one_row_f{floor}"] = ends_of_one
    _kpi(record_property, "K-P4-22", value)


# The branches the Phase 4 closure names under acceptance criterion 8 as
# carried with no frozen case and mutant, each by the plan decision that
# built it. A branch is covered once a registered mutant of the oracle
# names its decision (tests/test_generation_reference.py).
CRITERION_EIGHT_BRANCHES = {
    "the width pass": "P4-D30",
    "the empty-bin pass": "P4-D32",
    "the mode's own stratum": "P4-D267",
    "the anchors and the dressing": "P4-D268",
}


def test_k_p4_23(record_property) -> None:
    """Phase 4 criterion 8: generation branches with no frozen case and registered mutant."""
    import re

    import test_generation_reference as reference

    texts = [mutant.branch for mutant in reference.CASE_MUTANTS.values()]
    for mutants in reference.DOCUMENT_MUTANTS.values():
        texts += [mutant.branch for mutant in mutants]
    uncovered = sorted(
        branch for branch, decision in CRITERION_EIGHT_BRANCHES.items()
        if not any(re.search(re.escape(decision) + r"\b", text) for text in texts)
    )
    _kpi(record_property, "K-P4-23",
         {"uncovered": len(uncovered), "mutants": len(texts)}, ", ".join(uncovered))


def _roles(described: S.Described, tag: str) -> "dict[str, str]":
    return {f"{tag}/{block['name']}": block["role"] for block in described.document["columns"]}


# Decision 7's re-reading transitions, both directions (plan P4-D11.2,
# acceptance criterion 4): the spreadsheet error literals read as holes
# can move a column between EXISTING roles, and only in the direction
# re-reading produces. Each column is described twice through the command
# line -- as shipped, and with the literals kept as data by --keep-value,
# the route the decision leaves for a table where they are data.
_ARTIFACTS = ("#DIV/0!", "#N/A", "#NAME?", "#NULL!", "#NUM!", "#REF!")
DECISION_SEVEN = {
    # a two-valued column half-full of error literals: binary with the
    # literals as data, constant once they read as holes
    "binary_to_constant": (["yes", "#N/A"] * 50, ["#N/A"]),
    # a numeric column the literals polluted past the parse line: free
    # text with them as data, numeric again once they read as holes
    # (the case of test_p4d62_machine_artifacts, pinned beside this)
    "numeric_recovered": (
        [f"{10 + place % 90}" for place in range(114)] + list(_ARTIFACTS),
        list(_ARTIFACTS),
    ),
}


def _decision_seven_roles(home: pathlib.Path) -> "dict[str, str]":
    roles: "dict[str, str]" = {}
    for name, (cells, kept) in DECISION_SEVEN.items():
        for reading_of, flags in (
            ("literals_as_holes", []),
            ("literals_kept_as_data", [f for one in kept for f in ("--keep-value", one)]),
        ):
            folder = home / f"{name}-{reading_of}"
            folder.mkdir(parents=True)
            path = fixtures.write(
                folder, "thing.csv", fixtures.single_column_table("thing", cells)
            )
            run = S.cycle(path, flags, generate=False)
            key = f"decision_7/{name}/{reading_of}"
            if run["profile"] != 0:
                roles[key] = f"profile exit {run['profile']}"
                continue
            document = json.loads(run["description"].read_text(encoding="utf-8"))
            roles[key] = document["columns"][0]["role"]
    return roles


def test_k_p4_24(record_property, every_role: "dict", tmp_path: pathlib.Path) -> None:
    """Phase 4 criterion 4: every fixture column keeps the role the ledger commits to,
    and both directions of decision 7's re-reading happen exactly as stated."""
    roles: "dict[str, str]" = _decision_seven_roles(tmp_path / "decision-7")
    for floor in (1, 11):
        roles.update(_roles(every_role[floor], f"every_role_and_joined/f{floor}"))
        for name, text in (
            ("numbers_with_labels", fixtures.numbers_with_labels_table()),
            ("joined_numbers", fixtures.joined_numbers_table()),
            ("every_withholding", fixtures.every_withholding_table()),
        ):
            described = S.describe(tmp_path / f"{name}-{floor}", name, text, floor)
            roles.update(_roles(described, f"{name}/f{floor}"))
    _kpi(record_property, "K-P4-24", roles)


# -- Stage 1 --------------------------------------------------------------


def _key_calls(runs: int, repeated_scan: bool) -> int:
    """How many adjacent pairs one merge down to 30 strata weighs: an operation count.

    A pair is weighed either through `generation._pair_key`, which the
    heap merge calls once per candidate, or inside a call of
    `generation._merge_nearest`, which weighs every adjacent pair of the
    runs it is handed. Both are counted on both paths, so a merge that
    went back to the repeated scan would be counted at the scan's cost.
    """
    draw = random.Random(runs)
    held = sorted(draw.gauss(50, 10) for _ in range(runs))
    lengths = [1] * runs
    calls = 0
    pair_key = generation._pair_key
    merge_nearest = generation._merge_nearest

    def counted_key(*arguments: object) -> object:
        nonlocal calls
        calls += 1
        return pair_key(*arguments)  # type: ignore[arg-type]

    def counted_scan(left: "list[int]", right: "list[float]", cap: int = 0) -> object:
        nonlocal calls
        calls += len(left) - 1
        return merge_nearest(left, right, cap)

    with pytest.MonkeyPatch.context() as patch:
        patch.setattr(generation, "_merge_nearest", counted_scan)
        patch.setattr(generation, "_pair_key", counted_key)
        if repeated_scan:
            left, right = list(lengths), list(held)
            while len(left) > 30:
                left, right = generation._merge_nearest(left, right, 0)
        else:
            generation._merge_down(list(lengths), list(held), 30, 0)
    return calls


def test_k_s1_03(record_property) -> None:
    """The heap merge's work grows as n log n and is a small fraction of the repeated scan's."""
    heap_small, heap_large = _key_calls(2000, False), _key_calls(8000, False)
    scan_small = _key_calls(2000, True)
    _kpi(record_property, "K-S1-03",
         {"heap_key_calls_2000": heap_small, "heap_key_calls_8000": heap_large,
          "scan_key_calls_2000": scan_small,
          "scan_over_heap_2000": round(scan_small / heap_small, 1),
          "heap_growth_4x_runs": round(heap_large / heap_small, 2)})


def _generate_seconds(described: S.Described) -> float:
    started = time.perf_counter()
    generation.generate(described.loaded, 0)
    return time.perf_counter() - started


def test_k_s1_07(record_property, tmp_path: pathlib.Path) -> None:
    """Generation grows linearly: four times the rows costs well under eight times the time.

    The small size starts at 2,000 rows and doubles until one generation
    takes at least a second, so on a fast machine as on a slow one the
    ratio is of two times long enough that scheduler noise cannot move
    it past its bound; the ledger holds the probe that chose the size to
    that second.
    """
    rows = 2000
    small = S.describe(tmp_path / f"small-{rows}", "small", S.gaussian_table(rows))
    probe = _generate_seconds(small)
    while probe < 1.0 and rows < 64000:
        rows *= 2
        small = S.describe(tmp_path / f"small-{rows}", "small", S.gaussian_table(rows))
        probe = _generate_seconds(small)
    large = S.describe(tmp_path / f"large-{rows}", "large", S.gaussian_table(4 * rows))
    pairs = [(_generate_seconds(small), _generate_seconds(large)) for _ in range(3)]
    small_s = statistics.median(a for a, _b in pairs)
    large_s = statistics.median(b for _a, b in pairs)
    _kpi(record_property, "K-S1-07",
         {"ratio_4x_rows": round(large_s / small_s, 2), "small_rows": rows,
          "small_seconds_probe": round(probe, 2),
          "small_seconds": round(small_s, 2), "large_seconds": round(large_s, 2)})


# -- Stage 2 --------------------------------------------------------------


def test_k_s2_01(record_property) -> None:
    """The stage-2 round trip still covers every shape it was built on."""
    import test_stage2_round_trip as trip

    _kpi(record_property, "K-S2-01", {"shapes": len(trip._shapes())})


@pytest.fixture(scope="module")
def charges(tmp_path_factory: pytest.TempPathFactory) -> "tuple[list[str], list[str]]":
    """600 comma-grouped charges and their twin's cells at seed 4."""
    import test_stage2_spellings_survive as spellings

    home = tmp_path_factory.mktemp("kpi-charges")
    real = spellings._charges(600)
    described = S.describe(home, "charges", fixtures.rows_to_csv(["charge"], [[c] for c in real]))
    twin = generation.generate(described.loaded, 4)
    return real, [cell for cell in twin.columns[0] if cell]


def _naive_mean(cells: "list[str]") -> float:
    kept = []
    for cell in cells:
        try:
            kept += [float(cell)]
        except ValueError:
            continue
    return statistics.mean(kept)


def test_k_s2_02(record_property, charges: "tuple[list[str], list[str]]") -> None:
    """Code built on the twin fails exactly as it does on the real table (a naive float())."""
    real, twin = charges
    true_mean = statistics.mean(float(c.replace(",", "")) for c in real)
    naive_real, naive_twin = _naive_mean(real), _naive_mean(twin)
    _kpi(record_property, "K-S2-02",
         {"naive_gap_share": round(abs(naive_twin - naive_real) / naive_real, 4),
          "naive_real_share_of_true": round(naive_real / true_mean, 4),
          "naive_twin_share_of_true": round(naive_twin / true_mean, 4)})


def test_k_s2_03(record_property, charges: "tuple[list[str], list[str]]") -> None:
    """A thousands comma is written on every twin cell of a thousand or more."""
    _real, twin = charges
    big = [c for c in twin if float(c.replace(",", "")) >= 1000]
    _kpi(record_property, "K-S2-03",
         {"ungrouped_cells_over_a_thousand": sum(1 for c in big if "," not in c),
          "cells_over_a_thousand": len(big)})


# -- Stage 2b -------------------------------------------------------------


def test_k_2b_18(record_property, tmp_path: pathlib.Path) -> None:
    """ACCEPTED LIMIT: real record numbers reach the twin where the identifier has little room."""
    value = {}
    for figures in (4, 5, 6, 7, None):
        rows = S.room_rows(figures)
        _document, twin, _exits = S.privacy_trip(
            tmp_path / f"room-{figures}", ["id", "cohort"], rows,
            ["--smallest-group", "11", "--identifier", "id"], validate=False,
        )
        real = {row[0] for row in rows}
        key = "bare_989" if figures is None else f"rec_{figures}_figures"
        value[key] = sum(1 for row in twin[1:] if row[0] in real)
    _kpi(record_property, "K-2B-18", value)


# The sweep behind K-2B-19. The skeptic's thirty randomised shapes were
# not kept, so this commits a fresh sweep of the same family: the pinned
# column of tests/test_extra_round_numbers.py first, then thirty columns
# of a common word beside signed numbers, some of them held back below
# the floor of 11. Only label columns that hold something back are
# measured, because only there is a spelling held back at all.
SWEEP_SEED = 20260918


def _sweep_shapes() -> "list[list[str]]":
    shapes = [["alpha"] * 100 + ["+10"] * 20 + ["+11"] * 10 + ["+12"] * 10]
    draw = random.Random(SWEEP_SEED)
    for _ in range(30):
        cells = [draw.choice(["alpha", "none", "n/a", "pending"])] * draw.randrange(60, 140)
        sign = draw.choice(["+", "-", ""])
        start = draw.randrange(1, 90)
        step = draw.choice([1, 1, 2, 5])
        for place in range(draw.randrange(1, 3)):
            cells += [f"{sign}{start + place * step}"] * draw.randrange(11, 30)
        base = start + draw.randrange(1, 3) * step
        for place in range(draw.randrange(1, 4)):
            cells += [f"{sign}{base + (place + 1) * step}"] * draw.randrange(2, 11)
        shapes += [cells]
    return shapes


def test_k_2b_19(record_property, tmp_path: pathlib.Path) -> None:
    """ACCEPTED LIMIT: the twin can rebuild a held-back rare value exactly."""
    held_back_cells = reproduced = rebuilt_columns = measured = 0
    for place, cells in enumerate(_sweep_shapes()):
        described = S.describe(
            tmp_path / f"s{place}", "value",
            fixtures.rows_to_csv(["value", "other"], [[c, "k"] for c in cells]), floor=11,
        )
        block = described.block("value")
        if block["role"] not in ("categorical", "long_tail_labels") or not block.get(
            "suppressed_levels"
        ):
            continue
        measured += 1
        published = {level["label"] for level in block["levels"]}
        real = collections.Counter(c for c in cells if c not in published)
        twin = collections.Counter(generation.generate(described.loaded, 4).columns[0])
        held_back_cells += sum(real.values())
        reproduced += sum(min(count, twin[label]) for label, count in real.items())
        rebuilt_columns += {label: twin[label] for label in real} == dict(real)
    _kpi(record_property, "K-2B-19",
         {"held_back_cells": held_back_cells, "reproduced_cells": reproduced,
          "columns_measured": measured, "columns_rebuilt_exactly": rebuilt_columns})


def test_k_2b_22b(record_property, tmp_path: pathlib.Path) -> None:
    """A headerless table with NO title line publishes none of its first record as names."""
    import test_merge_close_2026_09_18 as close

    read = close._described(tmp_path, close._bare_records())
    lead = close._LEAD.split(",")
    _kpi(record_property, "K-2B-22b",
         {"record_cells_published_as_names": sum(1 for name in read["names"] if name in lead),
          "record_text_in_published_files": sum(1 for text in lead if text in read["written"]),
          "rows_counted": read["n_rows"]})


def test_k_2b_25(record_property) -> None:
    """One shared disclosure line: no inline copy of max(floor, 2) outside parsing.census_floor."""
    copies: "list[str]" = []
    for path in sorted((REPO / "src" / "synthtwin").glob("*.py")):
        tree = ast.parse(path.read_text("utf-8"))
        owners = {}
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                for inner in ast.walk(node):
                    owners.setdefault(id(inner), node.name)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "max"
                and len(node.args) == 2
                and any(isinstance(a, ast.Constant) and a.value == 2 for a in node.args)
                and not (path.name == "parsing.py" and owners.get(id(node)) == "census_floor")
            ):
                copies += [f"{path.name}:{node.lineno}"]
    _kpi(record_property, "K-2B-25",
         {"inline_copies": len(copies), "census_floor_1": parsing.census_floor(1),
          "census_floor_11": parsing.census_floor(11)}, ", ".join(copies))


def _lone_counts(tmp_path: pathlib.Path, names: "tuple[str, ...]") -> "dict":
    """The named count of one, and any other count of one, on each named shape."""
    value = {}
    for name, (header, rows, flags, column, key) in S.lone_count_shapes().items():
        if name not in names:
            continue
        document, _twin, _exits = S.privacy_trip(
            tmp_path / name, header, rows, flags, generate=False, validate=False
        )
        block = next(b for b in document["columns"] if b["name"] == column)
        ones = [path for path in S.ones_in(block) if path != "/position"]
        mirrors = {f"/{key}"} | (
            {"/n_missing_withheld", "/missing_by_class/(withheld)"} if key == "n_missing" else set()
        )
        value[f"{name}_named_count"] = block.get(key)
        value[f"{name}_other_ones"] = len([p for p in ones if p not in mirrors])
    return value


def test_k_2b_28(record_property, tmp_path: pathlib.Path) -> None:
    """Two counts of one LEFT AS IS on 2026-09-18, and none new beside them.

    Free text's `n_numeric` and a pooled label's `n_missing`: the owner
    asked, the answers were given, and neither was closed. They are not
    owner-accepted limits, so the entry is OPEN with its note.
    """
    _kpi(record_property, "K-2B-28", _lone_counts(tmp_path, ("free_text", "pooled_labels")))


def test_k_2b_48(record_property, tmp_path: pathlib.Path) -> None:
    """ACCEPTED LIMIT: a date column's `n_unparsed` of one, and none new beside it."""
    _kpi(record_property, "K-2B-48", _lone_counts(tmp_path, ("dates",)))


def test_k_2b_29(record_property, tmp_path: pathlib.Path) -> None:
    """ACCEPTED LIMIT: only an Excel autofilter publishes an ambiguous first row as names."""
    value = {}
    for with_filter in (False, True):
        folder = tmp_path / f"filter-{with_filter}"
        folder.mkdir()
        book = folder / "table.xlsx"
        book.write_bytes(S.autofilter_book(with_filter))
        S.quiet_cli(["profile", str(book), "--out-dir", str(folder), "--replace",
                     "--smallest-group", "5"])
        written = (folder / "table-profile.json").read_text("utf-8") + (
            folder / "table-profile.txt"
        ).read_text("utf-8")
        key = "with_autofilter" if with_filter else "without_autofilter"
        value[f"{key}_canaries_published"] = sum(
            1 for word in ("PERSON_CANARY", "PRIVATE_CANARY") if word in written
        )
    _kpi(record_property, "K-2B-29", value)


def test_k_2b_30(record_property, tmp_path: pathlib.Path) -> None:
    """Made-up identifiers coincide with real ones only at the chance rate."""
    rows = S.subject_rows()
    real = {row[0] for row in rows}
    whole = set(map(tuple, rows))
    value = {}
    for seed in ("4", "11"):
        _document, twin, _exits = S.privacy_trip(
            tmp_path / f"subj-{seed}", ["subject_id", "age"], rows,
            ["--identifier", "subject_id"], seed, validate=False,
        )
        value[f"coincident_ids_seed{seed}"] = sum(1 for row in twin[1:] if row[0] in real)
        value[f"whole_real_rows_seed{seed}"] = sum(1 for row in twin[1:] if tuple(row) in whole)
    _kpi(record_property, "K-2B-30", value)


_BOMB = r"""
import json, resource, sys, time
import workbooks as w
from synthtwin import errors, reading
n = 1_048_576
rows = [(r, [w.cell(f"A{r}", "", "", 1)]) for r in range(1, n + 1)]
body = w.sheet(rows)
data = w.package([
    ("[Content_Types].xml", w._content_types(1, False, False, False)),
    ("_rels/.rels", w._root_rels()),
    ("xl/workbook.xml", w._workbook([("Data", "")])),
    ("xl/_rels/workbook.xml.rels", w._workbook_rels(1, False)),
    ("xl/styles.xml", w._styles()),
    ("xl/worksheets/sheet1.xml", body)])
open(sys.argv[1], "wb").write(data)
del rows, body, data
started = time.perf_counter()
message = ""
try:
    reading.read_table(sys.argv[1])
except errors.ProfileError as refusal:
    message = str(refusal)
seconds = time.perf_counter() - started
peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
peak_mb = peak / 1e6 if sys.platform == "darwin" else peak / 1e3
print(json.dumps({"refused": bool(message), "seconds": seconds, "peak_mb": peak_mb,
                  "message": message[:200]}))
"""


def test_k_2b_38(record_property, tmp_path: pathlib.Path) -> None:
    """A million-cell zip bomb is refused by its cap, in bounded memory.

    The seconds are recorded and not judged: an absolute time belongs to
    the slow tier on the reference machine, and this runs in the suite.
    """
    if sys.platform == "win32":
        pytest.skip("peak memory is read through the resource module, which Windows lacks")
    environment = dict(os.environ)
    environment["PYTHONPATH"] = os.pathsep.join(
        [str(REPO / "src"), str(REPO / "tests")] + [environment.get("PYTHONPATH", "")]
    )
    done = subprocess.run(
        [sys.executable, "-c", _BOMB, str(tmp_path / "bomb.xlsx")],
        capture_output=True, text=True, env=environment, cwd=str(tmp_path), check=False,
    )
    assert done.returncode == 0, done.stderr[-2000:]
    found = json.loads(done.stdout.strip().splitlines()[-1])
    _kpi(record_property, "K-2B-38",
         {"refused": found["refused"], "seconds": round(found["seconds"], 2),
          "peak_mb": round(found["peak_mb"])}, found["message"])


def test_k_2b_40(record_property, eight: "list[dict]") -> None:
    """Real tables pass their own description, and their twins do too, at floors 1 and 11."""
    value: "dict[str, int]" = {}
    failed = []
    for run in eight:
        for side in ("real", "twin"):
            key = f"{side}_pass_f{run['floor']}"
            value[key] = value.get(key, 0) + (run[f"validate_{side}"] == 0)
            if run[f"validate_{side}"] != 0:
                failed += [f"{_tag(run)} {side} exit {run[f'validate_{side}']}"]
    _kpi(record_property, "K-2B-40", value, "; ".join(failed))


def test_k_2b_45(record_property, eight: "list[dict]") -> None:
    """Whole real rows through a made-up identifier that meets a real one (OPEN: not put to the owner)."""
    value = {}
    for run in eight:
        identifier = run["family_spec"]["identifier"]
        if run["kind"] == "csv" and identifier:
            real = S.csv_rows(run["path"])
            twin = S.csv_rows(run["twin"])
            place = real[0].index(identifier)
            whole, near = S.row_copies(real, twin, place)
            ids = {row[place] for row in real[1:]}
            value[f"{_tag(run)}_whole"] = whole
            value[f"{_tag(run)}_ignoring_identifier"] = near
            value[f"{_tag(run)}_coincident_ids"] = sum(1 for row in twin[1:] if row[place] in ids)
    _kpi(record_property, "K-2B-45", value)


def test_k_2b_46(
    record_property, every_role: "dict", every_role_twins: "dict", eight: "list[dict]"
) -> None:
    """Code runs unchanged: pandas gives every twin column the dtype it gives the real one."""
    import pandas

    mismatched: "set[str]" = set()
    for floor in (1, 11):
        real = pandas.read_csv(every_role[floor].table)
        for seed in (S.GOLDEN_SEED, 1, 2):
            twin = pandas.read_csv(io.StringIO(every_role_twins[(floor, seed)]))
            if list(twin.columns) != list(real.columns):
                mismatched |= {f"columns ({list(real.columns)} vs {list(twin.columns)})"}
                continue
            mismatched |= {
                f"{name} ({real[name].dtype} vs {twin[name].dtype})"
                for name in real.columns
                if str(real[name].dtype) != str(twin[name].dtype)
            }
    files = []
    for run in eight:
        spec = run["family_spec"]
        if run["kind"] == "xlsx":
            real, twin = pandas.read_excel(run["path"]), pandas.read_excel(run["twin"])
        else:
            real = pandas.read_csv(run["path"], sep=spec["mark"], encoding="utf-8-sig")
            twin = pandas.read_csv(run["twin"], sep=spec["mark"], encoding="utf-8-sig")
        differ = [
            name for name in real.columns
            if name not in twin or str(real[name].dtype) != str(twin[name].dtype)
        ]
        if differ or list(real.columns) != list(twin.columns):
            files += [f"{_tag(run)}: {differ}"]
    _kpi(record_property, "K-2B-46",
         {"every_role_columns_mismatched": len({m.split(" ")[0] for m in mismatched}),
          "eight_shape_files_mismatched": len(files)},
         "; ".join(sorted(mismatched) + files))


# -- Stage 6 (a baseline measured now) --------------------------------------


def test_k_s6_01(record_property, tmp_path: pathlib.Path) -> None:
    """Statistics across columns: what the twin loses today (the known gap until stage 6)."""
    import pandas

    described = S.describe(tmp_path, "real", S.association_table())
    frames = {
        "real": pandas.read_csv(described.table),
        "twin": pandas.read_csv(io.StringIO(S.twin_text(described, 4))),
    }
    measured = {}
    for side, frame in frames.items():
        old = frame.age > 65
        measured[side] = (
            float(frame.age.rank().corr(frame.sbp.rank())),
            float((frame.died[old] == "yes").mean() - (frame.died[~old] == "yes").mean()),
        )
    _kpi(record_property, "K-S6-01",
         {"rank_correlation_gap": round(abs(measured["twin"][0] - measured["real"][0]), 3),
          "death_rate_gap_lost": round(abs(measured["twin"][1] - measured["real"][1]), 3),
          "real_rank_correlation": round(measured["real"][0], 3),
          "twin_rank_correlation": round(measured["twin"][0], 3)})
