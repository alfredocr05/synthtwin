"""The chain's table layer finished (lane CHa2, plan P4-D451), behind the switch.

Contract 4.6b.2's RULE ONE_BAND, 4.6b.3's bound on the screen, and the
loader's reading of both: each case is red on the mutant its docstring
names (the lane's run of them: `planning-notes`, not the suite). Every
table here is invented and small, and the file takes seconds. K-S6-08's
driver enumerates RULE ONE_BAND exactly on a small fixture (90 rows); the
lane's 20,000- and 200,000-row measurements are plan P4-D451's record, not
a test.
"""
import fractions
import json
import pathlib
import sys

import pytest

from synthtwin import chain, chain_rules, chain_validation, contract, errors, generation, profile, reading, rendering, taxonomy

REPOSITORY = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY / "tests"))

import chain_enumeration as enumeration  # noqa: E402
import fixtures  # noqa: E402

TEST_KEY = bytes(range(32))


FROZEN = json.loads((REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))["chain"]


def _described(folder, name, text, key=TEST_KEY):  # type: ignore[no-untyped-def]
    path = folder / f"{name}.csv"
    path.write_text(text, encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch(name, key, rows_per_person=chain.ROWS_UNASKED))
    return document, chained


def _with_chain(folder, name, document, statistical):  # type: ignore[no-untyped-def]
    written = dict(document)
    block = dict(written["relationships"])
    block["statistical"] = statistical
    written["relationships"] = block
    return fixtures.write_profile(folder, f"{name}-on.json", written)


def _visits_table(rows=1000, blanks=0, top=2):  # type: ignore[no-untyped-def]
    """`visits` nought on 62 rows in 100, then 1 up to `top`; `group` follows it, `flag` beside them."""
    lines = ["visits,group,flag"]
    for at in range(rows):
        share = at % 100
        visits = 0 if share < 62 else (1 if share < 82 else top)
        group = ("a" if at % 3 else "b") if visits == 0 else ("b" if at % 4 else "c")
        cell = "" if at < blanks else f"{visits}"
        lines += [f"{cell},{group},{'y' if at % 5 < 2 else 'n'}"]
    return "\n".join(lines) + "\n"


def _entry(statistical, name):  # type: ignore[no-untyped-def]
    for one in statistical["ladder"]:
        if one["column"] == name:
            return one
    raise AssertionError(name)


def test_a_count_mostly_nought_reads_the_lowest_l1_cut(tmp_path):
    """Nought on 620 of 1,000 rows: `p50` is the lowest value and no row lies under it, so today's
    `L2` is one band and the column leaves the chain. RULE ONE_BAND reads `L1`'s lowest cut, 620
    against 380. MUTANT: `coarsest_level` returning the old level, `visits` ineligible `one_band`."""
    document, chained = _described(tmp_path, "zero", _visits_table())
    statistical = chained.statistical
    assert statistical is not None
    entry = _entry(statistical, "visits")
    assert entry["totals"] == [620, 200, 180]
    assert entry["l1"] == [[0], [1], [2]]
    assert entry["l2"] == [[0], [1, 2]]
    assert "visits" not in [one["column"] for one in statistical["ineligible"]]
    contract.load_profile(str(_with_chain(tmp_path, "zero", document, statistical)), chain=True)


def test_the_old_level_leaves_the_column_out(tmp_path, monkeypatch):
    """The rule's mutant at the producer: the column is `one_band` again, the description before the rule."""
    monkeypatch.setattr(chain_rules, "coarsest_level", lambda start, bands, second, third, totals: third)
    _document, chained = _described(tmp_path, "zero", _visits_table())
    statistical = chained.statistical
    assert statistical is not None
    assert {"column": "visits", "reason": "one_band"} in statistical["ineligible"]


def test_a_description_at_another_cut_is_refused_by_its_loader(tmp_path):
    """S23: `L2` is the lowest cut, not any other (the highest `L1` cut, 820 against 180, refused),
    and not the old one band (each written by hand). MUTANT: the loader reading `l2` unchecked."""
    document, chained = _described(tmp_path, "zero", _visits_table())
    statistical = json.loads(json.dumps(chained.statistical))
    for wrong in ([[0, 1], [2]], [[0, 1, 2]]):
        _entry(statistical, "visits")["l2"] = wrong
        with pytest.raises(errors.ProfileError, match="S23"):
            contract.load_profile(str(_with_chain(tmp_path, "zero", document, statistical)), chain=True)


def _shape_table(shape):  # type: ignore[no-untyped-def]
    """One of the oracle's frozen RULE ONE_BAND shapes as a table: `visits`, then two columns beside it."""
    values = [""] * shape["blank"]
    for value, rows in shape["counts"]:
        values += [f"{value}"] * rows
    lines = ["visits,group,flag"]
    for at in range(len(values)):
        lines += [f"{values[at]},{'x' if (at * 7) % 3 else 'y'},{'p' if (at * 5) % 4 else 'q'}"]
    return "\n".join(lines) + "\n"


@pytest.mark.parametrize(
    "name",
    ["one_band", "one_band_beside_blanks", "one_band_at_the_exact_rung", "one_band_median_named_by_a_lower_rung", "one_band_no_cut_beside_blanks"],
)
def test_the_product_publishes_the_oracle_s_frozen_shapes(tmp_path, name):
    """Each frozen shape of the oracle (lane CHa2's repair, Codex's item 2): the product publishes the
    rungs the case gives, so the case's inputs are what a profile writes, and its ladder is the case's.
    MUTANT: the product's rule removed, or the oracle's (the vectors then move)."""
    shape = FROZEN["one_band_shapes"][name]
    document, chained = _described(tmp_path, name, _shape_table(shape))
    rungs = chain_rules.rung_ladder(document["columns"][0])
    assert rungs is not None
    for key in shape["rungs"]:
        assert fractions.Fraction(f"{rungs[key]}") == fractions.Fraction(shape["rungs"][key]), key
    assert chained.statistical is not None
    entry = _entry(chained.statistical, "visits")
    case = FROZEN[name]
    l0 = [[(["range"] + one if isinstance(one, list) else one) for one in band] for band in entry["l0"]]
    assert [l0, entry["totals"], entry["l1"], entry["l2"]] == [case["l0"], case["totals"], case["l1"], case["l2"]]


def test_the_generator_and_the_validator_read_the_rule(tmp_path):
    """A description at the rule's `L2` generates and its twin meets the column's bands; V12 reads the
    `L2` the description publishes, which S23 held to its record's cut. MUTANT: `chain_validation`
    re-deriving `L2` at `p50` alone."""
    document, chained = _described(tmp_path, "zero", _visits_table())
    assert chained.statistical is not None
    entry = _entry(chained.statistical, "visits")
    loaded = contract.load_profile(str(_with_chain(tmp_path, "zero", document, chained.statistical)), chain=True)
    twin = generation.generate_held(loaded, 3)
    lines = "".join(rendering.twin_csv_pieces(twin)).splitlines()
    place = lines[0].split(",").index("visits")
    cells = [line.split(",")[place] for line in lines[1:]]
    assert [cells.count("0"), cells.count("1"), cells.count("2")] == [620, 200, 180]
    scale, _start = chain_validation._published_scale(entry, document["columns"][0])  # type: ignore[misc]
    assert scale.maps[2] == (0, 1, 1)


def test_the_rule_stands_beside_blank_cells(tmp_path):
    """Blanks keep their spread band beside the two: without the rule the column stays eligible on
    blank against present alone, and its values never reach `L2`. MUTANT: spread bands joined in."""
    _document, chained = _described(tmp_path, "blanks", _visits_table(blanks=30))
    assert chained.statistical is not None
    entry = _entry(chained.statistical, "visits")
    assert entry["l0"][0] == ["missing"]
    assert entry["l2"][0] == [0]
    assert len(entry["l2"]) == 3


def test_a_median_that_cuts_stays_the_cut(tmp_path):
    """Values on both sides of `p50`: `L2` is `p50`, the rule reaches nothing. MUTANT: the lowest
    `L1` cut read for every column, which would cut at `p25` here."""
    lines = ["score,group"]
    for at in range(1000):
        lines += [f"{at % 40},{'a' if at % 40 < 18 or at % 7 == 0 else 'b'}"]
    _document, chained = _described(tmp_path, "plain", "\n".join(lines) + "\n")
    assert chained.statistical is not None
    entry = _entry(chained.statistical, "score")
    first, second = entry["l2"]
    assert sum(entry["totals"][at] for at in first) == 500 and sum(entry["totals"][at] for at in second) == 500


def test_a_column_with_no_cut_stays_out(tmp_path):
    """Nought on 970 rows, one on 15 and two on 15: every rung is nought, no `L1` cut has rows on both sides, and
    the column stays `one_band`: the rule invents no cut. MUTANT: one `L2` band with rows read as enough to take
    part. The rule's `filled` read as at least one is EQUIVALENT in the product (the `L0` merge leaves no value
    band without a row, so `L1`'s one value band with rows is its only one: plan P4-D451); the oracle's mirror of
    it writes an empty band, red on the frozen vectors (`tests/test_chain_oracle.py`)."""
    lines = ["rare,group,other"]
    for at in range(1000):
        lines += [f"{1 if at < 15 else (2 if at < 30 else 0)},{'a' if at % 7 else 'b'},{'x' if at % 7 else 'y'}"]
    _document, chained = _described(tmp_path, "rare", "\n".join(lines) + "\n")
    assert chained.statistical is not None
    assert {"column": "rare", "reason": "one_band"} in chained.statistical["ineligible"]


def test_a_date_whose_median_is_its_earliest_takes_the_rule(tmp_path):
    """The same reading for a date: six rows in ten on one day. MUTANT: the rule read on numbers alone."""
    lines = ["seen,group"]
    for at in range(2000):
        day = 1 if at % 100 < 60 else 1 + at % 28
        lines += [f"2024-03-{day:02d},{'a' if day == 1 or at % 5 == 0 else 'b'}"]
    _document, chained = _described(tmp_path, "date", "\n".join(lines) + "\n")
    assert chained.statistical is not None
    assert "seen" not in [one["column"] for one in chained.statistical["ineligible"]]
    entry = _entry(chained.statistical, "seen")
    assert len(entry["l2"]) == 2


def test_k_s6_08_reads_the_rule_by_exact_enumeration():
    """Every table of the rule's fixture and every description: 0 leaking; its mutant, RULE W1 reading
    the level the rule replaced, publishes the band confined and leaks the six rows."""
    found = enumeration.one_band("filter")
    assert found["descriptions_leaking"] == 0
    assert found["tables"] == 1575
    mutant = enumeration.one_band("old_level")
    assert mutant["descriptions_leaking"] >= 1


def test_the_every_role_table_loads(tmp_path):
    """S23 on the base: a clock's `other` band joined with its first value band, with no `labels` and
    no `missing` cell between them, read as not adjacent. A spread band with no cell is no band
    (4.6b.2). MUTANT: adjacency read over every starting band, `seen_at` refused at 2,000 rows."""
    document, chained = _described(tmp_path, "every", fixtures.every_role_table(n_rows=2000))
    assert chained.statistical is not None
    entry = _entry(chained.statistical, "seen_at")
    assert entry["l0"][0][0] == "other" and isinstance(entry["l0"][0][1], list)
    contract.load_profile(str(_with_chain(tmp_path, "every", document, chained.statistical)), chain=True)


def test_a_titled_report_loads(tmp_path):
    """The zoo's `titled_report` at 2,000 rows, refused on the base at `column_1`. MUTANT: as above."""
    import health_zoo as zoo

    table = {one.name: one for one in zoo.catalogue()}["titled_report"]
    header, rows = table.build(2000, zoo.seed_of(table))
    path = tmp_path / f"titled{table.suffix}"
    path.write_bytes(table.write(header, rows))
    settings = taxonomy.Settings(small_cell_floor=11)
    read = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(read, settings, [], [], [])
    chained = chain.describe(read, document, settings, chain.ChainSwitch("titled", TEST_KEY, rows_per_person=chain.ROWS_UNASKED))
    assert chained.statistical is not None
    contract.load_profile(str(_with_chain(tmp_path, "titled", document, chained.statistical)), chain=True)


def test_the_loader_still_refuses_a_band_that_skips_a_band(tmp_path):
    """A spread band joined past a value band that stands between them is refused as before."""
    document, chained = _described(tmp_path, "every", fixtures.every_role_table(n_rows=2000))
    statistical = json.loads(json.dumps(chained.statistical))
    entry = _entry(statistical, "seen_at")
    first, second, third = entry["l0"][0], entry["l0"][1], entry["l0"][2]
    entry["l0"][0] = ["other", third[0]]
    entry["l0"][2] = [first[1]]
    entry["l0"][1] = second
    with pytest.raises(errors.ProfileError, match="S23"):
        contract.load_profile(str(_with_chain(tmp_path, "every", document, statistical)), chain=True)


def _triples(count, few=lambda place: False):  # type: ignore[no-untyped-def]
    return chain.screen_triples([few(place) for place in range(count)])


def test_every_triple_is_read_up_to_fifty_columns():
    """`C(50, 3)` is the bound, so a table of 50 columns reads every triple, in the order it always
    did. MUTANT: a smaller bound, or an order other than schema order."""
    found = _triples(50)
    assert len(found) == 19600 == chain.SCREEN_TRIPLES
    assert found == sorted(found)
    assert found[0] == (0, 1, 2) and found[-1] == (47, 48, 49)
    assert len(_triples(3)) == 1 and _triples(2) == []


@pytest.mark.parametrize("count", [51, 130, 230, 302, 400, 2000, 20000])
def test_past_fifty_columns_the_list_is_bounded_and_narrow_first(count):
    """The wide table's list by construction: never past the bound, whatever the columns, every
    triple of span 2 (three columns side by side) in it. MUTANT: the bound unread (cubic)."""
    found = _triples(count)
    assert len(found) <= chain.SCREEN_TRIPLES
    assert len(found) == len(set(found)) and found == sorted(found)
    assert (0, 1, 2) in set(found)
    assert (count - 3, count - 2, count - 1) in set(found) or count > chain.SCREEN_TRIPLES // 2


def test_the_few_level_class_is_read_first():
    """On 302 columns, one in five few-level: every triple of them narrowest first, up to half of the
    budget (contract 4.6b.3's 9,800), whatever their distance in the schema, and the rest of the budget
    read over every column. MUTANTS: the few-level list left out, (0, 5, 10) gone since its span is 10
    in the schema; the class given the whole budget, so no triple outside it is read."""
    assert chain.SCREEN_FEW_TRIPLES == 9800 == chain.SCREEN_TRIPLES // 2
    few = lambda place: place % 5 == 0  # noqa: E731
    found = set(_triples(302, few))
    assert (0, 5, 10) in found
    assert len(found) == chain.SCREEN_TRIPLES
    all_few = len([one for one in found if few(one[0]) and few(one[1]) and few(one[2])])
    assert chain.SCREEN_FEW_TRIPLES <= all_few < len(found)


def test_the_list_reads_nothing_of_the_table():
    """The list is a function of places and classes alone (no cell reaches it): the screen's seeds
    change with the table, the triples it reads do not. MUTANT: a column's counts in the signature."""
    import inspect

    assert list(inspect.signature(chain.screen_triples).parameters) == ["few"]


def test_the_screen_counts_only_the_list(monkeypatch):
    """`screen_seeds` scores the list's triples, each once. MUTANT: the old triple loop scoring all."""
    monkeypatch.setattr(chain, "SCREEN_TRIPLES", 40)
    monkeypatch.setattr(chain, "SCREEN_FEW_TRIPLES", 20)
    scored: "list[int]" = []
    real = chain._triple_score

    def counting(table, a, b, c):  # type: ignore[no-untyped-def]
        scored.extend([a])
        return real(table, a, b, c)

    monkeypatch.setattr(chain, "_triple_score", counting)
    ladder = enumeration.binary_scale("c", 15, 15)
    columns = [
        chain.Column(f"c{at}", ladder, (b"", b"", b""), frozenset(), bytes((row + at) % 2 for row in range(30)), 2, True, 0)
        for at in range(12)
    ]
    chain.screen_seeds(columns)
    assert len(scored) == 40


# -- A HELD COLUMN THAT REPEATS: THE HOLD STAYS, THE NOTE SAYS WHAT IS KNOWN (plan P4-D451) --


def _beside_a_repeating_column(folder, name, **switch):  # type: ignore[no-untyped-def]
    lines = ["place,person,score,group"]
    for at in range(1000):
        score = at % 40
        lines += [f"Z{at % 12},P{at % 300},{score},{'a' if score < 18 or at % 7 == 0 else 'b'}"]
    path = folder / f"{name}.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    return chain.describe(table, document, settings, chain.ChainSwitch(name, TEST_KEY, **{"rows_per_person": chain.ROWS_UNASKED, **switch}))


@pytest.mark.parametrize("held", [("person",), ("place",)])
def test_a_held_column_that_repeats_holds_the_chain(tmp_path, held):
    """A held column repeats, a key or a place: nothing published tells them apart nor says each row is
    another person, so no count in rows, and the note says only that the table may hold several rows
    per person. MUTANT: a held place let through, the rows of one person counted as people."""
    off = _beside_a_repeating_column(tmp_path, "held", held=held)
    assert off.statistical is None
    assert off.notes[-1] == f"no chain is published: {chain.OFF_HELD_REPEATS}"
    assert "may hold several rows per person" in chain.OFF_HELD_REPEATS


def test_a_declared_person_column_keeps_its_own_note(tmp_path):
    """The declared person column says so: a different fact from a held column repeating."""
    assert chain.OFF_PERSON != chain.OFF_HELD_REPEATS
    assert "declared person column" in chain.OFF_PERSON


def test_a_held_column_that_never_repeats_ends_nothing(tmp_path):
    """A held column of all different values holds no chain and stands in no family. MUTANT: any held column stopping the search."""
    lines = ["record,score,group"]
    for at in range(1000):
        score = at % 40
        lines += [f"R{at:06d},{score},{'a' if score < 18 or at % 7 == 0 else 'b'}"]
    path = tmp_path / "unique.csv"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    settings = taxonomy.Settings(small_cell_floor=11)
    table = reading.read_table(str(path), small_cell_floor=11)
    document = profile.build_document(table, settings, [], [], [])
    found = chain.describe(table, document, settings, chain.ChainSwitch("unique", TEST_KEY, held=("record",), rows_per_person=chain.ROWS_UNASKED))
    assert found.statistical is not None
    assert all(family["child"] != "record" for family in found.statistical["chain"])


def test_w_te_is_decided_at_nought_and_the_pair_is_still_read():
    """Contract 4.6b.14's row, decided on the product (plan P4-D451): `procedure` records it, and the
    detector still names the pair, so a later value slots in. MUTANT: `W_TE` at 1, the pair forced first."""
    assert chain_rules.W_TE == 0
    assert chain_rules.procedure_record(20000)["w_te"] == "0"
    assert chain_rules.procedure_record(20000)["l2_cut"] == "one_band"
    blocks = [{"name": "follow_up_days", "role": "count"}, {"name": "event", "role": "binary"}, {"name": "ward", "role": "categorical"}]
    found = chain.time_event_pairs(blocks, ["follow_up_days", "event", "ward"])  # type: ignore[arg-type]
    assert ("follow_up_days", "event") in found and ("event", "follow_up_days") in found


# -- A DESCRIPTION WRITTEN BEFORE THE RULE STILL LOADS (4.6b.5; Codex's item 1 on the build) --


def _written_before_the_rule(folder, monkeypatch, name, text):  # type: ignore[no-untyped-def]
    """The description the base wrote: `L2` at `p50` alone, `w_te` "1", the record without `l2_cut`."""
    with monkeypatch.context() as earlier:
        earlier.setattr(chain_rules, "coarsest_level", lambda start, bands, second, third, totals: third)
        earlier.setattr(chain_rules, "W_TE", fractions.Fraction(1))
        document, chained = _described(folder, name, text)
    statistical = json.loads(json.dumps(chained.statistical))
    statistical["procedure"] = chain_rules.earlier_procedure_record(document["n_rows"])
    return document, statistical


def test_a_description_written_before_the_rule_loads_and_reads_its_own_l2(tmp_path, monkeypatch):
    """Blank on 30 rows, then nought on 62 in 100: the base wrote `L2` as blank against every value,
    [[0], [1, 2, 3]], under `w_te` "1". This version loads it as written, and V12's reading keeps its
    `L2`; the same description under this version's record is refused at S23, and the earlier record
    beside this version's `L2` too. MUTANTS: the loader requiring this version's record (S24), the
    loader reading RULE ONE_BAND whatever the record (S23), V12 re-deriving `L2` by the rule."""
    document, statistical = _written_before_the_rule(tmp_path, monkeypatch, "before", _visits_table(blanks=30))
    entry = _entry(statistical, "visits")
    assert entry["l2"] == [[0], [1, 2, 3]] and statistical["procedure"]["w_te"] == "1"
    assert "l2_cut" not in statistical["procedure"]
    loaded = contract.load_profile(str(_with_chain(tmp_path, "before", document, statistical)), chain=True)
    assert generation.generate_held(loaded, 3) is not None
    scale, _start = chain_validation._published_scale(entry, document["columns"][0])  # type: ignore[misc]
    assert scale.maps[2] == (0, 1, 1, 1)
    as_now = json.loads(json.dumps(statistical))
    as_now["procedure"] = chain_rules.procedure_record(document["n_rows"])
    with pytest.raises(errors.ProfileError, match="S23"):
        contract.load_profile(str(_with_chain(tmp_path, "as-now", document, as_now)), chain=True)
    _document, chained = _described(tmp_path, "now", _visits_table(blanks=30))
    mixed = json.loads(json.dumps(chained.statistical))
    assert _entry(mixed, "visits")["l2"] == [[0], [1], [2, 3]]
    mixed["procedure"] = chain_rules.earlier_procedure_record(document["n_rows"])
    with pytest.raises(errors.ProfileError, match="S23"):
        contract.load_profile(str(_with_chain(tmp_path, "mixed", document, mixed)), chain=True)


def test_a_record_of_neither_version_is_refused(tmp_path, monkeypatch):
    """S24: the earlier record with this version's `w_te`, or this version's with the earlier `w_te`,
    or the earlier record with any other constant changed (`tau` 3, say), is the record of no version.
    MUTANTS: the loader reading `l2_cut` alone; the loader reading `w_te` and `l2_cut` alone."""
    document, statistical = _written_before_the_rule(tmp_path, monkeypatch, "neither", _visits_table(blanks=30))
    earlier = statistical["procedure"]
    changes = [("w_te", "0"), ("l2_cut", "one_band"), ("tau", "3")]
    changes += [(key, earlier[key] + 1 if isinstance(earlier[key], int) else f"{earlier[key]}1") for key in sorted(earlier) if key not in ("w_te", "tau")]
    assert len(changes) == len(earlier) + 1
    for key, value in changes:
        wrong = json.loads(json.dumps(statistical))
        wrong["procedure"][key] = value
        with pytest.raises(errors.ProfileError, match="S24 at 'procedure'"):
            contract.load_profile(str(_with_chain(tmp_path, "neither", document, wrong)), chain=True)


# -- WHERE THE RULE REACHES NOTHING (skeptic 1's item 4; Codex's item 4 on the build) --


def test_on_a_label_column_the_rule_reaches_nothing(tmp_path):
    """Two levels of 498 rows each beside four rows held back: the held-back pool joins the first
    level, so `L1` holds two filled bands and `L2` (the commonest level against the rest) one. The
    column stays `one_band`. MUTANT (the skeptic's P7): the rule read on label columns too, which
    cuts `L2` at `L1` and makes the column eligible."""
    lines = ["kind,group,flag"]
    for at in range(996):
        lines += [f"{'a' if at % 2 == 0 else 'b'},{'x' if at % 3 else 'y'},{'p' if at % 4 else 'q'}"]
    for at in range(4):
        lines += [f"rare{at},{'x' if at % 2 else 'y'},p"]
    _document, chained = _described(tmp_path, "label", "\n".join(lines) + "\n")
    assert chained.statistical is not None
    assert {"column": "kind", "reason": "one_band"} in chained.statistical["ineligible"]


def test_a_column_with_no_cut_stays_eligible_through_its_blanks(tmp_path):
    """Nought on 970 of 1,000 rows beside 30 blanks: no `L1` cut has rows on both sides, so the rule
    reaches nothing, and the column stays eligible on blank against present, as before the rule, and
    loads. MUTANT: the rule writing such a column as one band, blank joined with present. The rule's
    `filled` read as at least one is EQUIVALENT in the product (the case above); the oracle's mirror of
    it writes an empty band, red on the frozen vectors (`tests/test_chain_oracle.py`)."""
    shape = FROZEN["one_band_shapes"]["one_band_no_cut_beside_blanks"]
    document, chained = _described(tmp_path, "noblank", _shape_table(shape))
    assert chained.statistical is not None
    assert "visits" not in [one["column"] for one in chained.statistical["ineligible"]]
    assert _entry(chained.statistical, "visits")["l2"] == [[0], [1]]
    contract.load_profile(str(_with_chain(tmp_path, "noblank", document, chained.statistical)), chain=True)
