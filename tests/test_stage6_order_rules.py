"""Order rules carried through their difference D, behind the chain's switch (contract 4.6b.7; lane RO, plan P4-D459).

THE GATE OF LANE RO. Every rule of the rules page (MR.1 to MR.13) that
lane RO builds is pinned here by a case red on its mutant:

- the product's pure functions against the oracle's frozen vectors
  (`tools/reference/chain_oracle.py`, A-P4-59): the inference limit, D's
  nested levels and right-closed bands, rule 1 as repaired on skeptic
  1's tied-rungs table (red on the first text's rule 1), Proposition T
  read for the whole partition, rules 1 to 6 of a derived option (red
  with rule 5 off), D's readings in the twin (the band holding 0 giving
  exactly its count, the highest band at `up(lo)`, a tied lowest edge
  written on every rank), the computed column's forms and a clock held
  at the day's last minute, and the rule step's word and draw;
- the inference (MR.3) on invented tables: a heap at 0 still opens its
  step (red on a builder's condition), a source needs whole readings in
  a unit its grain writes (red on a source offered always or on
  `integer_valued` alone), a top-coded or E-notation computed column is
  never computed, a table of several rows a person carries no count;
- the twin (G16.2 step 5): `B` written in its OWN layout, on `D`'s side
  of `A` at `B`'s minute, a source's sum held at the day's last minute,
  the failing rows of a count class placed exactly;
- the loader (S28) and the validator (V12): a computed column publishing
  a count is refused, a computed column gives no cell (G16.5), a rule's
  line prints no count.

Every table is invented (`tests/rules_event_table.py`); at most a few
thousand rows, so the file stays inside the suite's time (the 20,000-row
checks are `tools/measurements/kpi_chain_rules.py`'s, under `kpi_run
--slow`). The floor is the product's default, 11.
"""

import csv
import dataclasses
import fractions
import importlib.util
import io
import json
import pathlib

import pytest

import fixtures
import rules_event_table as events

from synthtwin import (
    chain,
    chain_check,
    chain_order,
    chain_rules,
    chain_validation,
    chain_walk,
    contract,
    errors,
    generation,
    profile,
    quality,
    reading,
    rendering,
    taxonomy,
    validation,
)

ROOT = pathlib.Path(__file__).resolve().parents[1]
FROZEN = json.loads((ROOT / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))["chain"]
TEST_KEY = bytes(range(32))
FLOOR = 11
F = fractions.Fraction


def _oracle():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("ro_chain_oracle", ROOT / "tools" / "reference" / "chain_oracle.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@dataclasses.dataclass
class Described:
    table: reading.Table
    document: "dict[str, object]"
    settings: taxonomy.Settings
    chained: chain.Chained
    inference: "chain_order.Inference | None"


def _describe(tmp_path: pathlib.Path, header: "tuple[str, ...]", rows: "list[list[str]]", name: str, person: "list[str] | None" = None, patch: "dict[str, dict[str, object]] | None" = None) -> Described:
    """Profile an invented table and describe it with the chain's switch, keeping the inference."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(tmp_path, f"{name}.csv", events.as_text(header, rows))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    if person:
        written = json.loads(json.dumps(document))
        written["settings"]["person_columns"] = person
        document = written
    if patch:
        for block in document["columns"]:  # type: ignore[union-attr]
            if block["name"] in patch:
                block.update(patch[block["name"]])
    seen: "list[chain_order.Inference]" = []
    original = chain._rule_steps

    def keeping(inference, switch, names):  # type: ignore[no-untyped-def]
        seen.append(inference)
        return original(inference, switch, names)

    chain._rule_steps = keeping  # type: ignore[assignment]
    try:
        chained = chain.describe(table, document, settings, chain.ChainSwitch(name, TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=True))
    finally:
        chain._rule_steps = original  # type: ignore[assignment]
    return Described(table, document, settings, chained, seen[0] if seen else None)


def _rule(described: Described, computed: str, first: str) -> "chain_order.Inferred | None":
    assert described.inference is not None
    for rule in described.inference.rules:
        if rule.computed == computed and rule.inputs == (first,):
            return rule
    return None


def _twin(tmp_path: pathlib.Path, described: Described, seed: int = 0) -> "tuple[contract.Profile, str, pathlib.Path]":
    """The switched description written with its rules, loaded behind the switch, and its twin's text."""
    written = chain.with_rules(described.document, described.chained)
    path = fixtures.write_profile(tmp_path, "switched.json", written)
    loaded = contract.load_profile(str(path), chain=True)
    twin = generation.generate_held(loaded, seed)
    text = "".join(rendering.twin_csv_pieces(twin))
    return loaded, text, path


def _column(text: str, name: str) -> "list[str]":
    rows = list(csv.reader(io.StringIO(text)))
    at = rows[0].index(name)
    return [row[at] for row in rows[1:]]


# -- the product against the oracle (A-P4-59) -------------------------------------------


def test_the_inference_limit_is_the_oracles():
    """MR.1: `L(n) = max(f, floor(n / 100))` (MUTANT: the design's 40 at every size)."""
    for n, limit in FROZEN["rules_limit"]:
        assert chain_rules.rule_limit(n, FLOOR) == limit
    assert chain_rules.rule_limit(2000000, FLOOR) == 20000 != 40


def test_rule_one_as_repaired_refuses_skeptic_ones_tied_rungs():
    """MR.6 (e): on skeptic 1's table the deciles' edges are 0.1, 1.2, 3, 4.4, 5.5, 6.6, 7 and 8.9, every
    band at least 22 rows, and `k(25) - k(20) = 11 < 12` refuses the level; the oracle's first text's
    rule 1 (no rank-gap clause, no empty highest band) keeps it (the MUTANT, red)."""
    oracle = _oracle()
    readings = []
    for value, rows in zip(range(10), (24, 23, 1, 23, 22, 23, 23, 47, 22, 24)):
        readings += [value] * rows
    histogram = [(F(value), readings.count(value)) for value in sorted(set(readings))]
    product = []
    for name, percents, edges in chain_rules.derived_levels(histogram):
        totals = chain_rules.derived_totals(edges, histogram)
        product += [{"name": name, "edges": [chain_rules.decimal_text(edge) for edge in edges], "totals": totals,
                     "rule1": chain_rules.rule_one_refusal(totals, percents, FLOOR) is None}]
    assert product == FROZEN["rules_levels"]
    assert product[0]["rule1"] is False and FROZEN["rules_levels_mutant_first_text"][0]["rule1"] is True
    assert oracle.rule_one(product[0]["totals"], (10, 20, 25, 30, 40, 50, 60, 70, 75, 80, 90), FLOOR, first_text=True)


def test_row_nines_one_test_reads_the_whole_partition():
    """Proposition T at `f` = 11 and `L` = 200: the count classes pass together only where `R` is not 12 to 210."""
    passing = [r for r in range(11, 213) if chain_rules.partition_passes(r, FLOOR, 200)]
    assert passing == FROZEN["rules_partition"]["passing"] == [11, 211, 212]
    for v, readings, klass in FROZEN["rules_partition"]["classes"]:
        assert f"{chain_rules.class_of(v, readings, FLOOR, 200, False)}" == klass
    assert [f"{chain_rules.class_of(v, 300, FLOOR, 200, True)}" for v in (10, 11)] == FROZEN["rules_partition"]["phrase_only"]


def test_the_exact_count_under_the_floor_is_never_published():
    """MR.1: every `v` from 1 to `f - 1` reads the phrase (MUTANT: the exact count, red)."""
    for v in range(0, FLOOR):
        assert chain_rules.class_of(v, 1000, FLOOR, 200, False) == chain_rules.CLASS_PHRASE


def test_rules_two_to_six_are_the_oracles():
    """Rule 5 refuses a count class whose band holding 0 cuts into 15 below and 9 at or above 0; the phrase
    class keeps the same table; rule 6 refuses an inner band holding no multiple of the grain (MUTANT: rule 5
    off, red: the oracle's frozen mutant keeps it)."""
    edges = (F(0), F(4))
    table = [[24, 60, 60, 0], [0, 0, 0, 30]]
    counted = chain_rules.derived_option_refusal(("L1", (25, 75), edges), [24, 60, 60], table, {1}, True, set(), 15, F(1), FLOOR)
    phrase = chain_rules.derived_option_refusal(("L1", (25, 75), edges), [24, 60, 60], table, {1}, True, set(), "phrase", F(1), FLOOR)
    sixth = chain_rules.derived_option_refusal(("L1", (25, 75), (F(1, 4), F(3, 4))), [24, 60, 60], table, {1}, True, set(), "phrase", F(1), FLOOR)
    assert (counted is None, phrase is None, sixth is None) == (
        FROZEN["rules_family"]["count"][0], FROZEN["rules_family"]["phrase"][0], FROZEN["rules_family"]["rule6"][0]
    )
    assert counted is not None and counted.startswith("rule 5") and sixth is not None and sixth.startswith("rule 6")
    assert FROZEN["rules_family_mutant_rule5_off"]["count"][0] is True


def test_rule_three_refuses_a_family_cell_below_the_floor():
    """Rule 3: every cell of `{D | A}` is 0 or at least `f` (MUTANT: rule 3 off, red)."""
    table = [[12, 30, 5, 0], [12, 30, 55, 0], [0, 0, 0, 30]]
    refused = chain_rules.derived_option_refusal(("L1", (25, 75), (F(1), F(4))), [24, 60, 60], table, {2}, True, set(), "phrase", F(1), FLOOR)
    assert refused is not None and refused.startswith("rule 3")


def _steps_of(case: "dict[str, object]", percents: "tuple[int, ...]", failing: int) -> "list[list[str]]":
    edges = [chain_rules.decimal_value(text) for text in case["edges"]]  # type: ignore[union-attr]
    pairs = [(edge.numerator, edge.denominator) for edge in edges if edge is not None]
    totals = list(case["totals"])  # type: ignore[call-overload]
    steps = chain_walk.derived_readings(pairs, totals, totals, percents, failing)
    return [[chain_rules.decimal_text(F(step)) for step in band] for band in steps]


def test_ds_readings_in_the_twin_are_the_oracles():
    """MR.2's readings, repaired twice: a gap of 7 on every row comes back 7 on every row (a tied lowest edge);
    gaps of 0 and 1 day on half the rows each keep the median's edge 1/2 and the highest band reads `up(lo)` =
    1, never 1.5; a count class of 15 places exactly 15 readings below 0; an L1 level spreads each inner band
    over its multiples; an empty highest band writes the top edge from the top rung's first rank."""
    levels = dict(chain_rules.DERIVED_LEVELS)
    cases = FROZEN["rules_readings"]
    assert _steps_of(cases["seven"], levels["L0"], 0) == cases["seven"]["readings"]
    assert _steps_of(cases["halves"], levels["L2"], 0) == cases["halves"]["readings"] == [["0"] * 100, ["1"] * 100]
    counted = _steps_of(cases["count15"], levels["L2"], 15)
    assert counted == cases["count15"]["readings"]
    assert sum(1 for band in counted for text in band if text.startswith("-")) == 15
    assert _steps_of(cases["spread_l1"], levels["L1"], 0) == cases["spread_l1"]["readings"]
    assert _steps_of(cases["capped_l2"], levels["L2"], 0) == cases["capped_l2"]["readings"]


def test_the_computed_columns_forms_are_the_oracles():
    """MR.2's table of number forms in `B`'s own first form, and a clock sum held at the day's last minute."""
    forms = [
        chain_walk.written_sum(43, 0, "plain", 0, ""),
        chain_walk.written_sum(142, 2, "decimal", 0, ""),
        chain_walk.written_sum(43, 0, "leading_plus", 0, ""),
        chain_walk.written_sum(43, 0, "leading_zero", 5, ""),
        chain_walk.written_sum(1043, 0, "plain", 0, ","),
        chain_walk.written_sum(-5, 0, "leading_plus", 0, ""),
        chain_walk.written_sum(-25, 1, "decimal", 0, ""),
    ]
    assert forms == FROZEN["rules_written"]["forms"]
    assert [chain_walk.held_clock(86280, 180, 60), chain_walk.held_clock(86270, 30, 60), chain_walk.held_clock(3600, -30, 60)] == FROZEN["rules_written"]["clock"]


def test_the_rule_steps_word_is_keyed_by_the_rules_identity():
    """4.6b.4, MR.4 (f): the word reads `[kind, computed, inputs]` beside the columns, never the step's place,
    so a step added before it moves no word (MUTANT: the place, red)."""
    columns = ["started_on", "ended_on", "opened_at", "closed_at"]
    for case in FROZEN["rules_step"]:
        inputs = ["opened_at"] if case["computed"] == "closed_at" else ["started_on"]
        word = chain.step_word(TEST_KEY, "event", chain_rules.STEP_RULE, chain_rules.rule_key("order", case["computed"], inputs), columns)
        assert word.hex() == case["word"]
        assert chain_rules.choose(word, chain_rules.weights_of([F(0), F(1000), F(1003)], chain_rules.TAU)) == case["choice"]
    first = chain_order.Inferred("order", "closed_at", ("opened_at",), "date", "A", True, F(60), (), "", False)
    second = chain_order.Inferred("order", "ended_on", ("started_on",), "date", "A", False, F(1), (), "", False)
    switch = chain.ChainSwitch("event", TEST_KEY, rows_per_person=chain.ROWS_UNASKED)
    alone = chain._rule_steps(chain_order.Inference((first,), (), (), 0), switch, columns)
    behind = chain._rule_steps(chain_order.Inference((second, first), (), (), 0), switch, columns)
    assert alone[1][-1] == behind[1][-1]
    by_place = chain.step_word(TEST_KEY, "event", "rule", 0, columns)
    assert by_place != chain.step_word(TEST_KEY, "event", "rule", 1, columns)


def test_a_computed_columns_role_is_its_rules_never_its_cells():
    """MR.6 (a): `A` and `B` whole numbers but 3 rows of `B` written `n.5`: `B`'s own block reads
    `continuous`, which would say a row breaks `B = A + D`; the computed block publishes `A`'s role
    (MUTANT: the role read from `B`'s cells, red), and no count of `B`'s."""
    own = {"name": "b", "position": 2, "role": "continuous", "n_present": 2000, "numeric_styles": {"plain": 1997, "decimal": 3},
           "fraction_widths": {"1": 3}, "integer_valued": False, "mean": 4.5}
    template = {"name": "a", "position": 1, "role": "count", "n_present": 2000, "numeric_styles": {"plain": 2000},
                "fraction_widths": {}, "integer_valued": True, "mean": 3.0}
    role = chain_rules.computed_role(chain_rules.RULE_ORDER, ["count"])
    block = chain_order.computed_block(own, template, role, FLOOR)
    assert block["role"] == "count" and block["name"] == "b" and block["position"] == 2
    assert block["numeric_styles"] == ["plain"] and block["fraction_widths"] == []
    assert block["n_present"] is None and block["integer_valued"] is None and block["mean"] is None
    assert chain_rules.computed_role(chain_rules.RULE_FORMULA, ["count", "continuous"]) == "continuous"


# -- the inference (MR.3) -----------------------------------------------------------------


def test_a_heap_at_zero_opens_its_step_and_the_ninety_nine_in_a_hundred_item_reads_99(tmp_path):
    """MR.3: a builder may add no condition: gaps nearly all 0 still open the step (MUTANT: 'the gaps are not
    half zero', red). MR.7's heap item reads 99 of 100: at 2,000 rows a heap at 0 with 21 rows above holds
    the gap 0 on 98.95 per cent of the rows, so no flat option is worth carrying (MUTANT: the item at 90, red)."""
    described = _describe(tmp_path, events.HEAP_HEADER, events.heap_rows(rows=2000, above=21), "heap")
    rule = _rule(described, "closed_on", "opened_on")
    assert rule is not None and rule.antecedent
    assert chain_order.HEAP_LINE == F(99, 100)
    flat = [option for option in rule.options if option.level is not None and not option.level[2]]
    assert flat and all(not option.worth for option in flat)
    assert F(1979, 2000) < chain_order.HEAP_LINE and F(1979, 2000) >= F(90, 100)


def test_a_source_needs_whole_readings_in_a_unit_its_grain_writes(tmp_path):
    """MR.3's source conditions: a stay length written `n.5` on 3 rows publishes `integer_valued` false and is
    no source; a length in hours beside two dates is no source (the unit finer than the grain's day) (MUTANT:
    a source offered always, or on `integer_valued` alone, red)."""
    import random

    draw = random.Random(5)
    half: "list[list[str]]" = []
    hours: "list[list[str]]" = []
    for row in range(2000):
        admit = events._FIRST_DAY + __import__("datetime").timedelta(days=draw.randrange(720))
        gap = int(draw.expovariate(1 / 3.5))
        end = admit + __import__("datetime").timedelta(days=gap)
        half += [[admit.isoformat(), end.isoformat(), f"{gap}.5" if row < 3 else f"{gap}", draw.choice(events._SITES)]]
        hours += [[admit.isoformat(), end.isoformat(), f"{24 * gap}", draw.choice(events._SITES)]]
    for rows, name in ((half, "stay_days"), (hours, "stay_hours")):
        header = ("admitted_on", "released_on", name, "site")
        described = _describe(tmp_path / name, header, rows, name)
        rule = _rule(described, "released_on", "admitted_on")
        assert rule is not None
        assert all(option.carrier == chain_rules.CARRIER_DERIVED for option in rule.options)
    # The same day counts as a source, with whole readings in days.
    whole = [[row[0], row[1], row[2] if not row[2].endswith(".5") else row[2][:-2], row[3]] for row in half]
    described = _describe(tmp_path / "whole", ("admitted_on", "released_on", "stay_days", "site"), whole, "whole")
    rule = _rule(described, "released_on", "admitted_on")
    assert rule is not None and any(option.carrier == "stay_days" and option.unit == "day" for option in rule.options)


def test_a_top_coded_or_e_notation_column_is_never_computed(tmp_path):
    """OPEN1: a column the age top-code reaches is never computed (MUTANT: OPEN1 without the top-code, red),
    and neither is one first written in E-notation."""
    described = _describe(
        tmp_path / "ages", events.AGES_HEADER, events.ages_rows(rows=2000), "ages",
        patch={"age_at_discharge": {"top_coded": 90}},
    )
    assert _rule(described, "age_at_discharge", "age_at_admit") is None
    assert all(rule.computed != "age_at_discharge" for rule in described.inference.rules)  # type: ignore[union-attr]
    plain = _describe(tmp_path / "plain", events.AGES_HEADER, events.ages_rows(rows=2000), "plain")
    assert _rule(plain, "age_at_discharge", "age_at_admit") is not None
    exponent = _describe(tmp_path / "exp", events.EXPONENT_HEADER, events.exponent_rows(rows=2000), "exp")
    assert exponent.inference is None or all(rule.computed != "dose_given" for rule in exponent.inference.rules)


def test_no_count_class_on_a_table_of_several_rows_a_person(tmp_path):
    """MR.3: with a person column declared, no count class is published (the table layer reaches no such table:
    since lane GRa's patient layer, plan P4-D449, merged before this lane at batch 4q, it is described in patients
    behind the switch, where no rule step runs, so it publishes no rule and the describe takes no inference), and
    the inference offers no derived option there."""
    described = _describe(tmp_path, events.PERSON_HEADER, events.person_rows(rows=2000), "person", person=["subject_id"])
    statistical = described.chained.statistical
    assert statistical is None or statistical["rules"] == []
    assert described.inference is None
    joint = {(1, 1): 150, (1, -1): 12, (2, 2): 150}
    ladder = chain_rules.Ladder("a", (("missing",), ((None, "p50"),), (("p50", None),)), ((0, 1, 2), (0, 1, 2), (0, 1, 2)), (3, 3, 3), (0, 162, 150), (False, True, True))
    on_a_person_table, _why = chain_order.derived_options(joint, ladder, frozenset(), 12, F(1), F(1), FLOOR, 200, True, 312)
    elsewhere, _why = chain_order.derived_options(joint, ladder, frozenset(), 12, F(1), F(1), FLOOR, 200, False, 312)
    assert any(option.klass == 12 for option in elsewhere)
    assert not any(isinstance(option.klass, int) for option in on_a_person_table)


# -- the twin (G16.2 step 5) ----------------------------------------------------------------


def test_the_twin_writes_b_in_its_own_layout_and_never_before_a(tmp_path):
    """MR.6 (a): `B` is written in its OWN first layout (month first), never `A`'s (MUTANT, red), and in the
    phrase class no twin row has `B` before `A`."""
    described = _describe(tmp_path, events.LAYOUT_HEADER, events.layout_rows(rows=2000), "layout")
    assert any(rule["computed"] == "filled_on" for rule in described.chained.statistical["rules"])  # type: ignore[index]
    _loaded, text, _path = _twin(tmp_path, described)
    ordered = _column(text, "ordered_on")
    filled = _column(text, "filled_on")
    import datetime

    for first, second in zip(ordered, filled):
        assert len(second) == 10 and second[2] == "/" and second[5] == "/"
        later = datetime.datetime.strptime(second, "%m/%d/%Y").date()
        assert later >= datetime.date.fromisoformat(first)


def test_b_written_to_the_minute_stands_on_ds_side_of_a(tmp_path):
    """REPAIR 2: clocks to the second beside the next minute written to the minute: no twin row has `B` below
    `A` (MUTANT: the sum cut down to `B`'s minute, red)."""
    described = _describe(tmp_path, events.SECONDS_HEADER, events.seconds_rows(rows=2000, any_second=True), "seconds")
    assert any(rule["computed"] == "ended_at" for rule in described.chained.statistical["rules"])  # type: ignore[index]
    _loaded, text, _path = _twin(tmp_path, described)
    for began, ended in zip(_column(text, "began_at"), _column(text, "ended_at")):
        if began and ended:
            seconds = int(began[:2]) * 3600 + int(began[3:5]) * 60 + int(began[6:8])
            assert int(ended[:2]) * 3600 + int(ended[3:5]) * 60 >= seconds


def test_a_sources_sum_is_held_at_the_last_minute(tmp_path):
    """REPAIR 2: clocks at 23:57 to 23:59 beside a source length of 0 to 3 minutes, one sum past the day's end:
    held at 23:59 the table fails on 0 rows and the source carries the rule (MUTANT: the sum as it stands
    fails one row, red), and the twin writes `ended_at` held there on every row."""
    described = _describe(tmp_path, events.DAY_END_HEADER, events.day_end_rows(rows=2000), "dayend")
    rule = _rule(described, "ended_at", "began_at")
    assert rule is not None and any(option.carrier == "minutes" and option.unit == "minute" for option in rule.options)
    names = list(events.DAY_END_HEADER)
    blocks = {block["name"]: block for block in described.document["columns"]}  # type: ignore[union-attr]
    tabled = list(range(described.table.n_rows))
    declared = {"code": False, "measurement": False, "decimal_comma": False}
    a = chain_order.read_under(described.table, names.index("began_at"), blocks["began_at"], "clock", described.settings, declared, "", tabled)
    b = chain_order.read_under(described.table, names.index("ended_at"), blocks["ended_at"], "clock", described.settings, declared, "", tabled)
    d = chain_order.read_under(described.table, names.index("minutes"), blocks["minutes"], "number", described.settings, declared, "", tabled)
    pair = chain_order.pair_reading("clock", blocks["began_at"], blocks["ended_at"], a, b)
    assert chain_order.source_failing(pair, a, b, d, 60, 86340, FLOOR) == 0
    assert chain_order.source_failing(pair, a, b, d, 60, None, FLOOR) == 1
    _loaded, text, _path = _twin(tmp_path, described)
    for began, length, ended in zip(_column(text, "began_at"), _column(text, "minutes"), _column(text, "ended_at")):
        start = int(began[:2]) * 60 + int(began[3:5])
        assert ended == f"{min(start + int(length), 23 * 60 + 59) // 60:02d}:{min(start + int(length), 23 * 60 + 59) % 60:02d}"


def test_a_count_class_places_exactly_its_failing_rows_and_v12_holds_it(tmp_path):
    """MR.1: a derived carrier in a count class: the twin breaks the rule on exactly its count (MUTANT: the band
    holding 0 spread evenly, red), and V12's two lines read HELD, printing the verdict and no count of rows."""
    rows = events.event_rows(rows=2000, keyed_rows=15)
    described = _describe(tmp_path, events.HEADER, rows, "event15")
    entries = [rule for rule in described.chained.statistical["rules"] if rule["computed"] == "closed_at"]  # type: ignore[index]
    assert entries and entries[0]["class"] == 15
    loaded, text, path = _twin(tmp_path, described)
    import datetime

    broken = 0
    for opened, closed in zip(_column(text, "opened_at"), _column(text, "closed_at")):
        if opened and closed and datetime.datetime.strptime(closed, "%Y-%m-%d %H:%M") < datetime.datetime.strptime(opened, "%Y-%m-%d %H:%M"):
            broken += 1
    assert broken == 15
    twin_path = tmp_path / "twin.csv"
    twin_path.write_text(text, encoding="utf-8", newline="")
    document = json.loads(path.read_text(encoding="utf-8"))
    outcome = validation.measure(loaded, str(twin_path), chain_document=document)
    assert outcome.chain is not None
    lines = [rule for rule in outcome.chain.rules if rule.computed == "closed_at"]
    assert [line.verdict for line in lines] == [validation.HELD, validation.HELD]
    for rule in outcome.chain.rules:
        assert [field.name for field in dataclasses.fields(rule)] == ["index", "computed", "inputs", "carrier", "klass", "line", "verdict", "reason"]
    # One more failing row in the file: MISSED, and the line prints no measured count (V12.3, V12.5).
    altered = list(csv.reader(io.StringIO(text)))
    at = altered[0].index("closed_at")
    opened_at = altered[0].index("opened_at")
    for row in altered[1:]:
        if row[at] and row[opened_at] and row[at] >= row[opened_at]:
            row[at] = "2020-01-01 00:00"
            break
    out = io.StringIO()
    csv.writer(out, lineterminator="\n").writerows(altered)
    twin_path.write_text(out.getvalue(), encoding="utf-8", newline="")
    missed = validation.measure(loaded, str(twin_path), chain_document=document)
    assert missed.chain is not None
    verdicts = [rule.verdict for rule in missed.chain.rules if rule.computed == "closed_at"]
    assert verdicts[0] == validation.MISSED
    report = "\n".join(quality._chain_lines(missed.chain))
    rule_lines = [line for line in report.splitlines() if line.startswith("  rule ")]
    assert rule_lines and all("16" not in line for line in rule_lines)
    assert any("MISSED" in line for line in rule_lines)


# -- the loader (S28) and G16.5 ----------------------------------------------------------


def test_a_computed_column_publishing_any_count_is_refused(tmp_path):
    """S28 as the page amends it: a computed column's block holds nothing read from its cells (MUTANT: its
    `n_present` published, red)."""
    rows = events.event_rows(rows=2000)
    described = _describe(tmp_path, events.HEADER, rows, "eventcount")
    written = chain.with_rules(described.document, described.chained)
    chain_check.check(written)
    computed = [rule["computed"] for rule in described.chained.statistical["rules"]]  # type: ignore[index]
    assert computed
    for block in written["columns"]:  # type: ignore[union-attr]
        if block["name"] == computed[0]:
            block["n_present"] = 2000
    with pytest.raises(errors.ProfileError) as caught:
        chain_check.check(written)
    assert "S28" in f"{caught.value}"


def test_a_column_a_rule_computes_or_reads_gives_no_cell(tmp_path):
    """G16.5: the stray rows' givers keep every column a carried rule computes or reads (MUTANT: a computed
    column giving a cell, red)."""
    rows = events.event_rows(rows=2000)
    described = _describe(tmp_path, events.HEADER, rows, "eventgivers")
    loaded, _text, _path = _twin(tmp_path, described)
    plan = generation.plan_generation(loaded)
    reservation = generation._reservation(loaded, plan.columns, __import__("synthtwin").dialect.arranging(loaded.source.dialect, loaded.n_rows, len(plan.columns)))
    assert reservation is not None
    givers = {loaded.columns[place].name for place in range(len(loaded.columns)) if reservation[2][place]}
    for rule in loaded.relationships.rules:
        assert rule.computed not in givers and not set(rule.inputs) & givers
        assert rule.carrier not in givers


# -- lane RO's repair 1: `B`'s own forms, MR.7's items as amended, the person state, G4's reads -------------


def _described_with(tmp_path: pathlib.Path, header: "tuple[str, ...]", rows: "list[list[str]]", name: str, commas: "tuple[str, ...]" = ()) -> Described:
    """`_describe` for a table whose cells hold the delimiter (quoted), with columns read with a decimal comma."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    tmp_path.mkdir(parents=True, exist_ok=True)
    out = io.StringIO()
    writer = csv.writer(out, lineterminator="\n")
    writer.writerow(header)
    writer.writerows(rows)
    path = fixtures.write(tmp_path, f"{name}.csv", out.getvalue())
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    # The comma declared to the profile and to the describe alike, as the command declares it (lane RO's repair 2).
    document = profile.build_document(table, settings, [], forced_decimal_commas=list(commas))
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=True), forced_decimal_commas=list(commas))
    return Described(table, document, settings, chained, None)


def _carried(described: Described) -> "list[dict[str, object]]":
    statistical = described.chained.statistical
    return list(statistical["rules"]) if isinstance(statistical, dict) else []  # type: ignore[arg-type]


def test_b_keeps_as_offset_its_month_names_its_affix_and_its_decimal_comma(tmp_path):
    """MR.2 and MR.6 (a): `B` is written in its OWN first form. A stamp keeps `A`'s offset where `B`'s first
    published offset is one (MUTANT: no offset written, red); a date writes its month names and field widths
    (MUTANT: the layout's name alone, `11 May 2023`, red); a number its affix and its declared decimal comma
    (MUTANT: the bare sum, red). Code parsing the real column parses the twin's (G1)."""
    assert [
        chain_walk.written_form(chain_walk.written_sum(123456, 2, "decimal", 0, ","), True, None, None),
        chain_walk.written_form(chain_walk.written_sum(1769, 0, "plain", 0, ""), False, "", " mg"),
        chain_walk.written_form(chain_walk.written_sum(-25, 1, "decimal", 0, ""), True, "$ ", ""),
        chain_walk.written_form(chain_walk.written_sum(43, 0, "leading_zero", 5, ""), False, None, None),
    ] == FROZEN["rules_forms"]["forms"]
    models = (("+02:00", 7200, "upper"), ("+0200", 7200, "upper"), ("-05", -18000, "upper"), ("+05", 19800, "upper"),
              ("Z", 0, "lower"), ("+00:00", 0, "upper"), ("Z", 3600, "upper"))
    assert [generation._offset_like(seconds, model, zulu) for model, seconds, zulu in models] == FROZEN["rules_forms"]["offsets"]
    cases = (
        ("offset", events.OFFSET_HEADER, events.offset_rows(rows=2000), "left_at", (), r"\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d\+02:00"),
        ("months", events.MONTH_HEADER, events.month_rows(rows=2000), "release_on", (), r"\d\d-[A-Z][a-z]{2}-\d{4}"),
        ("affix", events.AFFIX_HEADER, events.affix_rows(rows=2000), "dose_end", (), r"\d+ mg"),
        ("comma", events.COMMA_HEADER, events.comma_rows(rows=2000), "level_end", ("level_start", "level_end"), r"\d+,\d\d"),
    )
    import re

    for name, header, rows, computed, commas, form in cases:
        described = _described_with(tmp_path / name, header, rows, name, commas)
        assert [rule["computed"] for rule in _carried(described)] == [computed], name
        _loaded, text, _path = _twin(tmp_path / name, described)
        cells = [cell for cell in _column(text, computed) if cell]
        assert cells and all(re.fullmatch(form, cell) for cell in cells), (name, cells[:3])


def test_a_level_with_no_edge_is_not_worth_carrying_unless_the_gap_is_heaped(tmp_path):
    """MR.7's one-band item per option (AMENDED 2026-11-05, the orchestrator's ruling): a level of `D` with no
    edge writes `B` as `A`; it scores `-w_rule n` unless the gap is 0 on 99 of 100 rows where both read, even
    where a level with an edge is eligible (MUTANT: the build's reading, judged only where every eligible level
    has no edge, red). A heap at 0 with every row at 0 keeps its one band."""
    for case in FROZEN["rules_one_band"]:
        edges = (F(0),) * case["edges"]
        worth = chain_order.derived_option_worth(edges, case["zero"], case["both"])
        assert worth == case["worth"]
        assert f"{chain_order.option_score(worth, F(-30), 20000)}" == case["score"]
    assert [case["worth"] for case in FROZEN["rules_one_band_mutant_build"]] != [case["worth"] for case in FROZEN["rules_one_band"]]
    described = _describe(tmp_path / "stay", events.STAY_HEADER, events.stay_rows(rows=2000, keyed=11), "stay")
    assert described.inference is not None
    for rule in described.inference.rules:
        flat = [option for option in rule.options if option.level is not None and not option.level[2]]
        edged = [option for option in rule.options if option.level is not None and option.level[2] and option.worth]
        if flat and edged:
            assert all(not option.worth and option.score < 0 for option in flat), rule.computed
    heaped = _describe(tmp_path / "heap", events.HEAP_HEADER, events.heap_rows(rows=2000, above=0), "heap0")
    rule = _rule(heaped, "closed_on", "opened_on")
    assert rule is not None and any(option.level is not None and not option.level[2] and option.worth for option in rule.options)


def test_the_tighter_rule_reads_an_input_not_computed(tmp_path):
    """MR.7: another worth rule refuses a rule by a smaller median gap only from an input NOT computed (MUTANT:
    the build's loop, which let `left_at` from `seen_at`, a column `seen_at`'s own rule computes, refuse
    `left_at` from `arrived_at`, red)."""
    described = _describe(tmp_path, events.CHAIN_HEADER, events.chain_rows(rows=2000), "chain")
    rule = _rule(described, "left_at", "arrived_at")
    seen = _rule(described, "seen_at", "arrived_at")
    assert rule is not None and seen is not None
    assert not seen.why and not rule.why, (seen.why, rule.why)


def test_the_association_item_reads_what_b_dealt_apart_would_keep(tmp_path):
    """MR.7's association item (AMENDED 2026-11-05, lane RO's repair 1): a visit's length set by its acuity
    is lost by computing the departure, but a departure dealt apart from the arrival keeps none of it, so the
    rule is worth carrying (MUTANT: `D`'s share alone, the build's, refuses it, red)."""
    described = _describe(tmp_path, events.ACUITY_HEADER, events.acuity_rows(rows=2000), "acuity")
    rule = _rule(described, "left_at", "arrived_at")
    assert rule is not None and not rule.why, rule.why if rule is not None else None
    stride = chain_order._stride(2000)
    assert stride == 1


def test_a_cell_of_eighteen_figures_is_read_exactly(tmp_path):
    """MR.2: binary64 never decides a failing row. Two readings of 18 significant figures, the second one unit
    of the last figure below the first on 30 rows: read exactly, 30 rows fail, over the limit of 20 at 2,000
    rows, and no step opens (MUTANT: the figures read through binary64, every row equal, a step opens, red)."""
    assert chain_order.exact_cell("1.00000000000000001", 1.0, "", "", False) == (100000000000000001, 17)
    assert chain_order.exact_cell("1.234,5", 1234.5, "", "", True) == (12345, 1)
    assert chain_order.exact_cell("1769 mg", 1769.0, "", " mg", False) == (1769, 0)
    described = _describe(tmp_path, events.FIGURES_HEADER, events.figures_rows(rows=2000), "figures")
    assert _rule(described, "reading_b", "reading_a") is None
    assert _rule(described, "reading_a", "reading_b") is None


def test_the_inference_offers_the_phrase_alone_on_a_person_table_and_describe_hands_it_the_state(tmp_path):
    """MR.3: where a person column is declared, answered or open on a table of several rows a person, a step
    offers the phrase only and no derived option, through `infer_rules` itself; and `describe` hands the
    inference the state it computes, never a constant (MUTANT: `False` handed, red)."""
    import ast
    import inspect

    tree = ast.parse(inspect.getsource(chain.describe))
    calls = [
        node for node in ast.walk(tree)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr == "infer_rules"
    ]
    assert len(calls) == 1 and isinstance(calls[0].args[-1], ast.Name) and calls[0].args[-1].id == "person_state"
    captured: "list[tuple[object, ...]]" = []
    original = chain_order.infer_rules

    def keeping(*arguments):  # type: ignore[no-untyped-def]
        captured.append(arguments)
        return original(*arguments)

    chain_order.infer_rules = keeping  # type: ignore[assignment]
    try:
        _describe(tmp_path, events.HEADER, events.event_rows(rows=2000, keyed_rows=12), "eventperson")
    finally:
        chain_order.infer_rules = original  # type: ignore[assignment]
    assert len(captured) == 1 and captured[0][-1] is False
    elsewhere = original(*captured[0][:-1], False)
    on_a_person_table = original(*captured[0][:-1], True)
    assert any(option.carrier == chain_rules.CARRIER_DERIVED for rule in elsewhere.rules for option in rule.options)
    for rule in on_a_person_table.rules:
        assert all(option.carrier != chain_rules.CARRIER_DERIVED for option in rule.options)
        assert all(option.klass == chain_rules.CLASS_PHRASE for option in rule.options)


def test_the_inference_reads_no_column_of_the_file_again_and_holds_few_bytes(tmp_path, monkeypatch):
    """G4 (LANE RO RULINGS 2 (1)): the inference takes its readings from the cells the describe reads. On a
    table read one column a group, the describe with the rule steps reads the file exactly as often as without
    them, and never calls the validator's own reader (MUTANT: the build's inference, which read every column
    again under each kind, red); the readings it holds are at most 4 bytes a cell."""
    monkeypatch.setattr(reading, "GROUP_BYTES", 1)
    rows = events.stay_rows(rows=2000, keyed=11)
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    path = fixtures.write(tmp_path, "stay.csv", events.as_text(events.STAY_HEADER, rows))
    reads: "list[int]" = []
    read_group = reading._read_group

    def counting(source, places):  # type: ignore[no-untyped-def]
        reads.append(len(places))
        return read_group(source, places)

    monkeypatch.setattr(reading, "_read_group", counting)
    held: "list[int]" = []
    original = chain_order.infer_rules

    def measuring(*arguments):  # type: ignore[no-untyped-def]
        held.append(chain_order.gathered_bytes(arguments[0]))
        return original(*arguments)

    def refused(*_arguments):  # type: ignore[no-untyped-def]
        raise AssertionError("the inference read a column again")

    counted = {}
    for rules_on in (False, True):
        table = reading.read_table(str(path), small_cell_floor=FLOOR, in_groups=True)
        assert table.source is not None
        document = profile.build_document(table, settings, [], [], [])
        reads.clear()
        monkeypatch.setattr(chain_order, "infer_rules", measuring)
        monkeypatch.setattr(chain_order, "read_under", refused)
        chain.describe(table, document, settings, chain.ChainSwitch("stay", TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=rules_on))
        counted[rules_on] = len(reads)
    assert counted[True] == counted[False], counted
    assert held and held[0] <= 4 * 2000 * len(events.STAY_HEADER), held


def test_mr7s_amended_items_are_the_oracles(tmp_path):
    """MR.7 as amended 2026-11-05 (LANE RO RULINGS 3 (3) to (5)), against the oracle's frozen vectors: the
    association item reads the smaller of `D`'s share and `B`'s own (MUTANT: `D`'s alone, red), the
    tighter-rule item skips an input a worth rule computes and breaks a tie of medians by the smaller mean
    (MUTANT: the build's loop, red), and the presence item reads a presence's share between bands; on the
    battery's survival table, whose event dates are present exactly where the status is not `censored`, the
    event date's rule is NOT WORTH carrying for its presence (MUTANT: no presence item, red)."""
    items = FROZEN["rules_items"]
    d_ten = [x % 10 for x in range(40)]
    flat = [x // 4 for x in range(40)]
    groups = [x % 4 for x in range(40)]
    shares = [
        (chain_order._share_between(list(d_ten), d_ten, 10), chain_order._share_between(list(flat), d_ten, 10)),
        (chain_order._share_between(list(d_ten), groups, 4), chain_order._share_between(list(d_ten), groups, 4)),
    ]
    assert [[f"{lost}", f"{kept}"] for lost, kept in shares] == items["shares"]
    assert f"{max(chain_order.association_lost_share(lost, kept) for lost, kept in shares)}" == items["association"]
    assert items["association"] != FROZEN["rules_items_mutant_build"]["association"]
    assert f"{chain_order._share_between([1, 1, 1, 0, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 2, 2], 3)}" == items["presence"]

    def candidate(a: str, median: int, mean: int) -> "chain_order._Candidate":
        return chain_order._Candidate(a, "left_at", "date", chain_order.PairReading("date", "A", True, 1, 1), 0, 100, 0, F(median), F(1), F(60), 0, (), F(mean))

    worth = {("arrived_at", "left_at"): True, ("seen_at", "left_at"): True}
    tight = [
        bool(chain_order.tighter_rule(candidate("arrived_at", 60, 70), [candidate("seen_at", 30, 40)], worth, {"seen_at"})),
        bool(chain_order.tighter_rule(candidate("arrived_at", 0, 40), [candidate("seen_at", 0, 0)], worth, set())),
        bool(chain_order.tighter_rule(candidate("arrived_at", 0, 0), [candidate("seen_at", 0, 40)], worth, set())),
    ]
    assert tight == items["tighter"] != FROZEN["rules_items_mutant_build"]["tighter"]
    import analyst_tables

    rows = list(csv.reader(io.StringIO(analyst_tables.text("ST3", 2000, 1))))
    described = _describe(tmp_path, tuple(rows[0]), rows[1:], "survival")
    rule = _rule(described, "event_date", "entry_date")
    assert rule is not None and rule.why == "B's presence follows another column", rule.why if rule is not None else None


# -- lane RO's repair 2: the outside review's items and the verify's, each red on its mutant --------------


def test_bs_own_point_negative_form_and_fraction_are_the_oracles():
    """MR.2's table: a first fraction width of 0 writes a point after figures holding no places (`42.` + 1 is
    `43.`; MUTANT: the point dropped, red), a negative wears its column's published negative form, brackets
    included (MUTANT: the minus always, red), and a stamp's fraction is `A`'s count of figures in zeros, to
    the second where it is none (MUTANT: the second always, red), against the oracle's frozen vectors."""
    from synthtwin import parsing

    case = FROZEN["rules_repair2"]
    assert [
        chain_walk.written_sum(43, 0, "plain", 0, "", True),
        parsing.with_negative_notation(chain_walk.written_sum(-43, 0, "plain", 0, "", True), "brackets"),
        parsing.with_negative_notation(chain_walk.written_sum(-125, 2, "decimal", 0, ""), "brackets"),
        parsing.with_negative_notation(chain_walk.written_sum(-125, 2, "decimal", 0, ""), "trailing_minus"),
        parsing.with_negative_notation(chain_walk.written_sum(-43, 0, "plain", 0, ""), "trailing_minus"),
        parsing.with_negative_notation(chain_walk.written_sum(-43, 0, "plain", 0, ""), "minus_sign"),
        chain_walk.written_sum(425, 2, "decimal", 0, "", True),
    ] == case["forms"]
    words = (("subsecond", 3), ("subsecond", 0), ("second", 3), ("minute", 6))
    assert [list(chain_walk.stamp_fraction(word, digits)) for word, digits in words] == case["fraction"]


def test_a_band_reaching_far_below_zero_reads_its_failing_rows_one_by_one():
    """The outside review's item 9: the band holding 0 gives its failing rows the multiples above its lower
    edge, in turn, read one by one and never its whole span (MUTANT: the span held, red: a band from a
    million grains below 0 held a million integers). Its own case: 600 gaps of -10**9, -1, 0, 1, 2 and 3 at a
    grain of 10**-6, class 200, its L1 level, whose straddling band reaches 250,000,000,749,999 grains below
    0: exactly 200 readings below 0, as the oracle reads them."""
    import tracemalloc

    tracemalloc.start()
    small = chain_walk.derived_readings([(-1000000, 1), (5, 1)], [100, 100, 100], [100, 100, 100], (25, 75), 150)
    peak = tracemalloc.get_traced_memory()[1]
    tracemalloc.stop()
    assert peak < 1000000, peak
    assert sum(1 for band in small for step in band if step < 0) == 150
    case = FROZEN["rules_repair2"]["wide"]
    levels = dict(chain_rules.DERIVED_LEVELS)
    bands = _steps_of(case, levels["L1"], 200)
    summary = [[len(band), band[0] if band else "", band[-1] if band else "", sum(1 for text in band if text.startswith("-"))] for band in bands]
    assert summary == case["bands"]
    assert sum(entry[3] for entry in summary) == 200


def test_more_than_255_utc_offsets_are_held_and_read_back():
    """The outside review's item 11, its own case: stamps at the 256 offsets `+00:00` to `+04:15`, eighty rows
    each (20,480 rows), are held and each row reads its own offset back (MUTANT: the offset's second byte
    not read, red; the build raised on the 256th)."""
    import datetime

    texts: "list[str]" = []
    for row in range(20480):
        minutes = row % 256
        stamp = datetime.datetime(2023, 3, 1, 8, 0) + datetime.timedelta(minutes=minutes)
        texts += [stamp.strftime("%Y-%m-%dT%H:%M") + f"+{minutes // 60:02d}:{minutes % 60:02d}"]
    spelled = {text: ("date", None, text) for text in texts}
    block = {"name": "began_at", "role": "datetime", "format": "iso-datetime", "n_present": len(texts)}
    declared = {"code": False, "measurement": False, "decimal_comma": False}
    held = chain_order.readings_of(texts, spelled, block, chain_order.KIND_DATE, declared, range(len(texts)))
    assert held.offset_palette is not None and len(held.offset_palette) == 257
    assert [chain_order.offset_at(held, row) for row in (0, 255, 256, 511, 20479)] == [0, 255 * 60, 0, 255 * 60, 255 * 60]
    assert chain_order.offsets_in(held, 254, 258) == [254 * 60, 255 * 60, 0, 60]


def test_a_computed_number_keeps_its_affix_its_point_and_its_brackets(tmp_path):
    """The outside review's items 1 and 2: `B` keeps its OWN form whatever the rule's role. An affixed `B`
    beside an `A` written bare keeps `mg` (MUTANT: the affix read from the rule's role, red), a `B` written
    `43.` keeps its point (MUTANT: dropped, red) and a `B` below 0 written in brackets keeps them (MUTANT: the
    minus, red): code converting the real column converts the twin's (G1)."""
    import re

    bare = [[row[0].replace(" mg", ""), row[1], row[2]] for row in events.affix_rows(rows=2000)]
    cases = (
        ("bare", events.AFFIX_HEADER, bare, "dose_end", r"\d+ mg"),
        ("point", events.POINT_HEADER, events.point_rows(rows=2000), "dose_high", r"\d+\."),
        ("brackets", events.BRACKET_HEADER, events.bracket_rows(rows=2000), "balance_high", r"\(\d+\)"),
    )
    for name, header, rows, computed, form in cases:
        described = _described_with(tmp_path / name, header, rows, name)
        assert [rule["computed"] for rule in _carried(described)] == [computed], name
        _loaded, text, _path = _twin(tmp_path / name, described)
        cells = [cell for cell in _column(text, computed) if cell]
        assert cells and all(re.fullmatch(form, cell) for cell in cells), (name, cells[:3])


def test_a_carried_rule_reads_its_input_as_the_polish_leaves_it(tmp_path):
    """G16.2 step 5 after G16.3 (batch 4q's merge of lane RO beside lane MPg's polish; method G16.3's "a column a
    carried rule reads"): an input that rule B's moments give a polish target (`dose_start`, correlated with
    `weight`) is polished and placed before its rule computes its column, so the twin's `dose_end` stands on or
    after `dose_start` on every row. MUTANT: step 5 run inside the walk before G16.3 and before the polished
    columns are placed, red: 992 of 2,000 rows end before they start (0 on the merge)."""
    described = _described_with(tmp_path, events.POLISHED_HEADER, events.polished_rows(rows=2000), "polished")
    assert [rule["computed"] for rule in _carried(described)] == ["dose_end"]
    loaded, text, _path = _twin(tmp_path, described)
    assert loaded.relationships.moments is not None
    assert "dose_start" in [name for name, _targets in generation._polish_layout(loaded).plan]
    pairs = [(int(a), int(b)) for a, b in zip(_column(text, "dose_start"), _column(text, "dose_end")) if a and b]
    assert len(pairs) > 1900
    assert [pair for pair in pairs if pair[1] < pair[0]] == []


def test_a_sources_placeholder_is_no_reading_and_a_declared_comma_bands_a(tmp_path):
    """The outside review's items 3 and 4. A source whose `-99` the reader is told means no value carries
    `B`, absent there on the real table: the twin writes no `B` beside the placeholder (MUTANT: the
    placeholder read as -99, red: every such row written below `A`). Amounts written with a declared decimal
    comma are banded by their own reading: no twin row stands outside the published family's cells (MUTANT:
    the comma ignored, red: every amount read in the lowest band)."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR, declared_missing_values=("-99",))
    path = fixtures.write(tmp_path, "marker.csv", events.as_text(events.MARKER_HEADER, events.marker_rows(rows=2000)))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("marker", TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=True))
    described = Described(table, document, settings, chained, None)
    assert [(rule["computed"], rule["carrier"]) for rule in _carried(described)] == [("end_units", "added_units")]
    _loaded, text, _path = _twin(tmp_path, described)
    added, ended = _column(text, "added_units"), _column(text, "end_units")
    assert any(cell == "-99" for cell in added)
    assert not any(ended[row] for row in range(len(added)) if added[row] == "-99")
    commas = ("level_low", "level_high")
    grouped = _described_with(tmp_path / "grouped", events.GROUPED_HEADER, events.grouped_rows(rows=2000), "grouped", commas)
    rules = [rule for rule in _carried(grouped) if rule["computed"] == "level_high" and rule["carrier"] == "derived"]
    assert rules
    derived = rules[0]["derived"]
    ladder = [entry for entry in grouped.chained.statistical["ladder"] if entry["column"] == "level_low"][0]  # type: ignore[index]
    joined = {"L0": [[band] for band in range(len(ladder["l0"]))], "L1": ladder["l1"], "L2": ladder["l2"]}[derived["parent"]["level"]]
    level_of = {place: at for at in range(len(joined)) for place in joined[at]}
    edges = [F(edge) for edge in derived["edges"]]
    _loaded, text, _path = _twin(tmp_path / "grouped", grouped)
    outside = 0
    for low, high in zip(_column(text, "level_low"), _column(text, "level_high")):
        gap = F(high.replace(",", ".")) - F(low.replace(",", "."))
        band = sum(1 for edge in edges if gap > edge)
        outside += 0 if derived["table"][level_of[events.GROUPED_STARTS.index(low)]][band] > 0 else 1
    assert outside == 0


def test_the_copy_detector_and_break_read_ds_own_scale_and_instants():
    """The outside review's items 5 and 8. `A = j/10`, `B = (j+k)/10` and `C = k` for `j, k` from 1 to 10: `D`
    is `C/10`, so `C` copies no `D` (MUTANT: the pair's own `10**p` left out, red: `C` read as a copy and
    its association dropped), while a `C` written `k/10` does. Stamps at 100 minutes from midnight at
    `+00:00` beside the instant a minute later written at `+10:00`: BREAK reads the instants, 4851/10000,
    the review's own figure (MUTANT: the local clocks, red: 0)."""
    declared = {"code": False, "measurement": False, "decimal_comma": False}

    def held(texts: "list[str]", name: str, role: str = "continuous", kind: str = chain_order.KIND_NUMBER, form: str = "") -> "chain_order.Readings":
        if kind == chain_order.KIND_NUMBER:
            spelled = {text: ("number", float(text), text) for text in texts}
        else:
            spelled = {text: ("date", None, text) for text in texts}
        block = {"name": name, "role": role, "format": form, "n_present": len(texts)}
        return chain_order.readings_of(texts, spelled, block, kind, declared, range(len(texts)))

    js = [1 + row % 10 for row in range(100)]
    ks = [1 + row // 10 for row in range(100)]
    a = held([f"{j / 10:.1f}" for j in js], "dose_a")
    b = held([f"{(j + k) / 10:.1f}" for j, k in zip(js, ks)], "dose_b")
    pair = chain_order.pair_reading(chain_order.KIND_NUMBER, {"role": "continuous"}, {"role": "continuous"}, a, b)
    gaps = chain_order.pair_gaps(pair, a, b)[0]
    power = 10 ** max(a.places, b.places)
    assert not chain_order._copies_the_gap(gaps, held([f"{k}" for k in ks], "steps_c", "count"), chain_order.KIND_NUMBER, False, power)
    assert chain_order._copies_the_gap(gaps, held([f"{k / 10:.1f}" for k in ks], "steps_c"), chain_order.KIND_NUMBER, False, power)
    rows = events.instant_rows(rows=20000)
    sent = held([row[0] for row in rows], "sent_at", "datetime", chain_order.KIND_DATE, "iso-datetime")
    seen = held([row[1] for row in rows], "seen_at", "datetime", chain_order.KIND_DATE, "iso-datetime")
    blocks = [{"role": "datetime", "resolution_mix": {"iso-datetime": 20000}, "format": "iso-datetime"}] * 2
    stamped = chain_order.pair_reading(chain_order.KIND_DATE, blocks[0], blocks[1], sent, seen)
    assert stamped.seconds and stamped.instants
    assert chain_order._break_share(sent, seen, stamped) == F(4851, 10000)


def test_v12_reads_the_derived_families_and_counts_their_withheld_lines(tmp_path):
    """The outside review's items 6 and 14. A score cycling through 1 to 100 and a second 1 above it to 50,
    100 above it past: its derived family carried. A file whose five rows (1, 2) read (0, 1) keeps `A`'s band
    totals, but its new small group of `A` is confined by `D`: W1 with the derived family refuses it, so the
    rule's lines are WITHHELD, gate closed (MUTANT: the derived families left out of V12.3, red: HELD). A file
    missing its rows of scores 1 to 3 misses `A`'s band totals: the rule's two lines read WITHHELD, not
    judged, and the reason census counts them beside the family lines (MUTANT: left out, red)."""
    described = _describe(tmp_path, events.STEP_HEADER, events.step_rows(rows=2000), "step")
    assert [rule["computed"] for rule in _carried(described)] == ["score_b"]
    loaded, text, path = _twin(tmp_path, described)
    document = json.loads(path.read_text(encoding="utf-8"))
    real = events.step_rows(rows=2000)
    moved = 0
    for row in real:
        if row[0] == "1" and moved < 5:
            row[0], row[1] = "0", "1"
            moved += 1
    measured = tmp_path / "moved.csv"
    measured.write_text(events.as_text(events.STEP_HEADER, real), encoding="utf-8", newline="")
    outcome = validation.measure(loaded, str(measured), chain_document=document)
    assert outcome.chain is not None
    assert [(line.line, line.verdict) for line in outcome.chain.rules] == [("rule", validation.WITHHELD), ("derived family", validation.WITHHELD)]
    kept = [row for row in events.step_rows(rows=2000) if row[0] not in ("1", "2", "3")]
    measured.write_text(events.as_text(events.STEP_HEADER, kept), encoding="utf-8", newline="")
    missed = validation.measure(loaded, str(measured), chain_document=document)
    assert missed.chain is not None
    withheld = [line for line in missed.chain.rules if line.verdict == validation.WITHHELD and line.reason == chain_validation.NOT_JUDGED]
    families = [line for line in missed.chain.families if line.verdict == validation.WITHHELD and line.reason == chain_validation.NOT_JUDGED]
    assert len(withheld) == 2 and missed.chain.not_judged == len(families) + 2
    handling = "".join(quality.report_pieces(loaded, missed)).split("HOW TO KEEP THIS FILE", 1)[1]
    assert f"{missed.chain.not_judged} more between-columns family or rule line(s) read" in handling


def test_a_source_option_never_reads_a_computed_column(tmp_path):
    """The outside review's item 7, its own branch: on `base_a, next_c, extra_x, total_b` with `next_c` a few
    above `base_a` and `total_b = extra_x + next_c`, the draw carrying `next_c` from `base_a` and then
    `total_b` from `extra_x` by each step's last option (legal under the uniform share) offers no source
    `next_c`, already computed: the description loads behind the switch (MUTANT: the option offered, red: S28
    refuses the description it wrote)."""
    settings = taxonomy.Settings(small_cell_floor=FLOOR)
    path = fixtures.write(tmp_path, "summed.csv", events.as_text(events.SUMMED_HEADER, events.summed_rows(rows=2000)))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, [], [], [])
    original = chain._rule_steps

    def two(inference, switch, names):  # type: ignore[no-untyped-def]
        wanted = tuple(rule for rule in inference.rules if (rule.computed, rule.inputs[0]) in (("next_c", "base_a"), ("total_b", "extra_x")))
        assert len(wanted) == 2 and wanted[1].options[-1].carrier == "next_c"
        return original(chain_order.Inference(wanted, inference.near, inference.notes, inference.pairs_read), switch, names)

    choose = chain.rules.choose
    chain.rules.choose = lambda word, weights: len(weights) - 1  # type: ignore[assignment]
    chain._rule_steps = two  # type: ignore[assignment]
    try:
        chained = chain.describe(table, document, settings, chain.ChainSwitch("summed", TEST_KEY, rows_per_person=chain.ROWS_UNASKED, rules=True))
    finally:
        chain.rules.choose = choose  # type: ignore[assignment]
        chain._rule_steps = original  # type: ignore[assignment]
    described = Described(table, document, settings, chained, None)
    carried = [(rule["computed"], rule["carrier"]) for rule in _carried(described)]
    assert carried[0] == ("next_c", "derived") and ("total_b", "next_c") not in carried
    _twin(tmp_path, described)


def test_a_millisecond_stamp_computed_keeps_its_fraction(tmp_path):
    """The verify's item 1: two stamps to the millisecond, the second 0 to 5 seconds after: every computed
    cell parses with `%S.%f`, as the real column's and the twin's without rules do, and none stands before
    `A` (MUTANT: the to-the-second writer, red)."""
    import datetime

    described = _describe(tmp_path, events.MILLISECOND_HEADER, events.millisecond_rows(rows=2000), "ms")
    assert [rule["computed"] for rule in _carried(described)] == ["acked_at"]
    _loaded, text, _path = _twin(tmp_path, described)
    form = "%Y-%m-%d %H:%M:%S.%f"
    sent, acked = _column(text, "sent_at"), _column(text, "acked_at")
    assert any(acked) and all(len(cell.split(".")[-1]) == 3 for cell in acked if cell)
    for before, after in zip(sent, acked):
        if before and after:
            assert datetime.datetime.strptime(after, form) >= datetime.datetime.strptime(before, form), (before, after)


def test_a_partial_date_holds_no_reading_and_a_finer_stamp_is_not_worth_computing(tmp_path):
    """The sibling check of the verify's item 1 (LANE RO RULINGS 6 (1)). A month written year and month alone
    beside a date holds no reading and opens no step, as MR.2 says of a partial date (MUTANT: read as a
    whole date, red: the describe with the rule steps raised). A stamp written to the microsecond beside one
    to the second is finer than `A`, more places than `A`, MR.7's item: computing it would write `A`'s
    places and erase its own (MUTANT: the item read on numbers alone, red)."""
    billed = _describe(tmp_path / "billed", events.BILLED_HEADER, events.billed_rows(rows=2000), "billed")
    assert not [rule for rule in _carried(billed) if rule["computed"] == "billed_month"]
    finer = _describe(tmp_path / "finer", events.FINER_HEADER, events.finer_rows(rows=2000), "finer")
    rule = _rule(finer, "ended_at", "began_at")
    assert rule is not None and rule.why == "B is finer than A: more places than A", rule.why if rule is not None else None


def test_a_stamp_in_another_zone_or_to_fewer_figures_than_its_input_is_not_computed(tmp_path):
    """Lane RO's follow-up, LANE RO RULINGS 7 (1) and (2) (the second verify of repair 2, items 1 and 2). A
    computed stamp is written at `A`'s UTC offset and to `A`'s figures after the second (MR.2; MR.12's
    departure (7)), so a `B` written otherwise would lose its own form. `sent_at` at `-05:00` beside `seen_at`
    a minute later at the instant, written at `+03:00`, is not computed, nor is the outside review's
    `+00:00` beside `+10:00`, and the twin writes every `seen_at` at `+03:00` (MUTANT: the offset item
    removed, red: carried, every cell at `-05:00`). Two stamps of one zone across its clock change hold the
    same offsets and keep their rule, as the zoo's encounters do (LANE RO RULINGS 3 (4); MUTANT: any row
    holding a different offset, red). A stamp to the millisecond beside one to the microsecond is not
    computed, and the twin writes every `acked_at` to three figures (MUTANT: today's comparison, `B`'s
    figures above `A`'s alone, red: carried, six figures on every cell)."""
    other_zone = "B's UTC offset is other than A's: computing it would erase it"
    zoned = _describe(tmp_path / "zoned", events.ZONED_HEADER, events.zoned_rows(rows=2000), "zoned")
    rule = _rule(zoned, "seen_at", "sent_at")
    assert rule is not None and rule.why == other_zone, rule.why if rule is not None else None
    assert not [one for one in _carried(zoned) if one["computed"] == "seen_at"]
    _loaded, text, _path = _twin(tmp_path / "zoned", zoned)
    seen = [cell for cell in _column(text, "seen_at") if cell]
    assert seen and all(cell.endswith("+03:00") for cell in seen)
    review = _describe(tmp_path / "review", events.INSTANT_HEADER, events.instant_rows(rows=2000), "review")
    rule = _rule(review, "seen_at", "sent_at")
    assert rule is not None and rule.why == other_zone, rule.why if rule is not None else None
    changed = _describe(tmp_path / "changed", events.CLOCK_CHANGE_HEADER, events.clock_change_rows(rows=2000), "changed")
    rule = _rule(changed, "left_at", "arrived_at")
    assert rule is not None and not rule.why, rule.why if rule is not None else None
    coarser = _describe(tmp_path / "coarser", events.COARSER_HEADER, events.coarser_rows(rows=2000), "coarser")
    rule = _rule(coarser, "acked_at", "sent_at")
    fewer = "B writes fewer figures after the second than A: computing it would write A's"
    assert rule is not None and rule.why == fewer, rule.why if rule is not None else None
    _loaded, text, _path = _twin(tmp_path / "coarser", coarser)
    acked = [cell for cell in _column(text, "acked_at") if cell]
    assert acked and all(len(cell.split(".")[-1]) == 3 for cell in acked)


def test_the_inferences_held_bytes_count_what_is_held():
    """The outside review's item 10: twelve-place readings whose scaled span passes 2 to the 32 are held as
    the interpreter's whole numbers, and `held_bytes` counts them, about 40 bytes a cell (MUTANT: 8 a cell,
    the slots alone, red)."""
    texts = [f"{row / 97:.12f}" for row in range(5000)]
    spelled = {text: ("number", float(text), text) for text in texts}
    declared = {"code": False, "measurement": False, "decimal_comma": False}
    held = chain_order.readings_of(texts, spelled, {"name": "x", "role": "continuous", "n_present": 5000}, chain_order.KIND_NUMBER, declared, range(5000))
    assert held.plain is not None
    assert chain_order.held_bytes(held) >= 32 * 5000


def _driver():  # type: ignore[no-untyped-def]
    spec = importlib.util.spec_from_file_location("ro_kpi_chain_rules", ROOT / "tools" / "measurements" / "kpi_chain_rules.py")
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_k_bc_10s_readings_judge_each_twin_and_read_every_fixtures_inventory():
    """The outside review's items 12 and 13. A keyed class of 150 read 149, 150 and 150 on three twins is
    stamped 149, the twin farthest from its class (MUTANT: the largest, 150, red), and each twin's
    placement is judged: one PLACED check off (MUTANT: the seeds' worst alone, red); K-S6-06 binds it at 0.
    Every carried rule and every inferred rule left uncarried of a fixture is read, the chain of events'
    included: its three carried rules are PLACED checks and its uncarried pair is UNPLACED (MUTANT: the
    event table's fixed pairs alone, red)."""
    driver = _driver()
    for counts in ((149, 150, 150), (150, 150, 149), (150, 151, 149)):
        worst = None
        for count in counts:
            worst = driver._farthest(worst, count, 150)
        assert worst == counts[[abs(count - 150) for count in counts].index(max(abs(count - 150) for count in counts))]
    cells = {"arrived_at": ["2023-01-02 10:00", "2023-01-02 10:00", "2023-01-02 10:00"],
             "seen_at": ["2023-01-02 10:05", "2023-01-02 09:55", ""],
             "left_at": ["2023-01-02 10:03", "2023-01-02 11:00", "2023-01-02 11:00"]}
    carried = [{"inputs": ["arrived_at"], "computed": "seen_at", "carrier": "derived", "class": "phrase", "unit": None},
               {"inputs": ["arrived_at"], "computed": "left_at", "carrier": "derived", "class": "phrase", "unit": None}]
    tally: "dict[str, object]" = {"rules_placed_checked": 0, "rules_placed_off": 0, "rules_unplaced_pairs": 0, "rules_unplaced_rows": 0, "rules_unplaced_reasons": {}}
    driver._readings_of(cells, carried, [("seen_at", "left_at", "blocked by a rule carried before it")], tally)
    assert tally == {"rules_placed_checked": 2, "rules_placed_off": 1, "rules_unplaced_pairs": 1, "rules_unplaced_rows": 1,
                     "rules_unplaced_reasons": {"blocked by a rule carried before it": 1}}
    ledger = json.loads((ROOT / "tests" / "kpi" / "ledger.json").read_text(encoding="utf-8"))
    entry = [one for one in ledger["entries"] if one["id"] == "K-S6-06"][0]
    assert entry["expected"]["rules_placed_off"] == 0
