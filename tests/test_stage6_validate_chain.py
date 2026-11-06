"""Validator V12 for the chain's families, layer L1, behind the chain's switch (lane CHv, plan P4-D430).

THE GATE OF LANE CHv. `synthtwin validate` handed the chain's switch
(`cli.main(..., chain=...)`, which no command-line option sets) reads a
description's chain and adds V12's lines (validation method V12.2): an
`L0` band-total line a column and a line a family, each HELD or MISSED,
and every candidate pair with its published word, a pair reading
`implied` beside the table the chain implies and its dealing spread
(REPORT-ONLY). This file holds:

- EVERY EXACT LINE HELD on the switched table itself and on a twin the
  oracle's walk (method G16.2, `tools/reference/chain_oracle.py`) deals
  from the published chain, and MISSED on its mutant: V12.4's mutants 1
  to 6, each red on its line, and the green whole-row shuffle;
- THE REPORT-ONLY LINES printed: the implied shares equal a brute-force
  product of the published families, and the dealing spread lies in the
  oracle's certified enclosure;
- THE SCREEN'S ONE LINE, the written report's whole section;
- WHAT IS NEVER PRINTED (V12.3): a file off by 3 and one off by 30 print
  the same section; every number in a published-table line is 0 or at
  least the floor; a gate closed by the file's own facts prints V5.3's
  sentence whatever the table;
- S12 BYTE IDENTITY: a description carrying no chain is validated, with
  the switch and without it, to the same report, screen and exit code,
  and a switched description is refused without the switch;
- CHo's ORACLE AGREES with V12's EXACT lines on the switched case of
  `tests/test_chain_oracle.py` (its table, its `ward` answered `keep`,
  the oracle's test key): every family's table counted by the oracle on
  the file equals the published one exactly where V12 reads HELD;
- the loader's invariants S23 to S27 refusing a broken chain before a
  byte of the file is read;
- REPAIR 1's cases, each red on its mutant: RULE WE on the file's own
  records holding nothing, each own-fact source alone, the NOT CHECKABLE
  lines, the verdict's census and the "not judged" count, the file's
  calendar censuses, a file counted in people, a miss between columns
  only, the three-argument call without the switch, the implied bounds
  and the forest, the printed details, records of spaces and the
  one-byte codes;
- REPAIR 2's cases, each red on its mutant: the verdict's two kinds of
  NOT CHECKABLE line, the clock census as the file's own fact, each
  source of the people rule alone, the walk's held bound, RULE WE's room
  outside the ladder and the published blanks of a column the file lacks.

Every fixture is invented here; the key is the oracle's fixed test key.
"""

import json
import random
import re
from fractions import Fraction

import pytest

import fixtures
from chain_twins import (
    FLOOR,
    HEADER,
    REPOSITORY,
    Described,
    _band_codes,
    _clinic_rows,
    _dropped_parent,
    _families,
    _family_with_parents,
    _holding,
    _off_by,
    _oracle_chain,
    _oracle_ladder,
    _quiet,
    _section,
    _verdicts,
    _walk_twin,
    _write,
    co,
    oc,
)

from synthtwin import chain_rules, chain_validation, cli, quality, validation


@pytest.fixture(scope="module", autouse=True)
def _the_small_table_refusal_off_for_the_module_s_fixtures():
    """The suite's default without the table floor (tests/conftest.py, plan P4-D425), set before this module's own.

    The clinic and the split table are described in MODULE-SCOPED fixtures, which pytest sets up before the
    conftest's function-scoped default; lane CHv was built before lane POP's floor, so at batch 4k's merge its
    800-row clinic met the floor's refusal. An autouse fixture of the module's scope comes first.
    """
    with pytest.MonkeyPatch.context() as own:
        own.setitem(cli.main.__kwdefaults__, "small_tables_refused", False)
        yield


@pytest.fixture(scope="module")
def clinic(tmp_path_factory):
    with pytest.MonkeyPatch.context() as patch:
        folder = tmp_path_factory.mktemp("clinic")
        for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
            patch.setenv(name, str(folder / "home"))
        described = Described(folder, HEADER, _clinic_rows())
        yield described



# -- EVERY EXACT LINE HELD ON A SWITCHED TWIN ---------------------------------


def test_every_exact_line_holds_on_the_table_and_on_a_twin_the_walk_deals(clinic):
    """The switched table checked against its own description: every band
    total and every family HELD, exit 0, the chain's lines counted in the
    verdict. A twin the oracle's walk deals from the published chain (each
    column's cells the table's own, rearranged into rows by G16.2) holds
    every published table too, while most of its rows are new."""
    for rows in (clinic.rows, _walk_twin(clinic)):
        code, report, _screen = clinic.validate(rows)
        totals, families = _verdicts(report)
        assert set(totals.values()) == {"HELD"} and len(totals) == len(clinic.statistical["ladder"])
        assert set(families.values()) == {"HELD"} and sorted(families) == list(range(len(_families(clinic))))
        assert code == 0
    twin = _walk_twin(clinic)
    assert sum(1 for a, b in zip(twin, clinic.rows) if a != b) > len(twin) // 2


# -- V12.4's mutants, each red on its line --------------------------------------



def test_mutant_1_one_column_swapped_between_parent_cells_misses_that_family(clinic):
    """Mutant 1: one family's child cells exchanged between two rows lying in
    DIFFERENT cells of its parents and in DIFFERENT bands of the child at
    the family's level, every band total kept: that family MISSED, every
    band total HELD, exit 3. An exchange inside one band moves nothing
    (every line HELD)."""
    at, family = _family_with_parents(clinic)
    codes = _band_codes(clinic, clinic.rows)
    level = int(family["level"][1])

    def cell_of(row):
        out = []
        for parent in family["parents"]:
            lad, row_l0 = codes[parent["column"]]
            out += [lad.coarsen(int(parent["level"][1]))[row_l0[row]]]
        return tuple(out)

    child_lad, child_l0 = codes[family["child"]]
    to_level = child_lad.coarsen(level)
    first = 0
    second = next(r for r in range(1, len(clinic.rows)) if cell_of(r) != cell_of(first) and to_level[child_l0[r]] != to_level[child_l0[first]])
    place = clinic.header.index(family["child"])
    rows = [list(row) for row in clinic.rows]
    rows[first][place], rows[second][place] = rows[second][place], rows[first][place]
    code, report, _screen = clinic.validate(rows)
    totals, families = _verdicts(report)
    assert families[at] == "MISSED" and set(totals.values()) == {"HELD"}
    assert code == 3
    same = next(r for r in range(1, len(clinic.rows)) if child_l0[r] == child_l0[first] and clinic.rows[r][place] != clinic.rows[first][place])
    rows = [list(row) for row in clinic.rows]
    rows[first][place], rows[same][place] = rows[same][place], rows[first][place]
    code, report, _screen = clinic.validate(rows)
    assert set(_verdicts(report)[1].values()) == {"HELD"} and code == 0


@pytest.mark.parametrize("column", ["pressure", "age"])
def test_mutant_2_one_column_shuffled_alone_misses_every_family_holding_it(clinic, column):
    """Mutant 2: one column shuffled on its own. Every family holding it as a
    child under a parent, or as a parent, MISSED; its own band totals are
    kept, so a family where it is the child of NO parent stays HELD, and so
    does every family not holding it."""
    place = clinic.header.index(column)
    order = list(range(len(clinic.rows)))
    random.Random(11).shuffle(order)
    rows = [list(row) for row in clinic.rows]
    for at in range(len(rows)):
        rows[at][place] = clinic.rows[order[at]][place]
    code, report, _screen = clinic.validate(rows)
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"}
    holding = _holding(clinic, column)
    for at, family in enumerate(_families(clinic)):
        rootless_child = family["child"] == column and not family["parents"]
        if at in holding and not rootless_child:
            assert families[at] == "MISSED", (column, at)
        else:
            assert families[at] == "HELD", (column, at)
    assert code == 3


def test_mutant_3_records_holding_nothing_placed_by_single_cell_exchanges(tmp_path, monkeypatch):
    """Mutant 3: a table with twelve records holding nothing (published,
    twelve being at least the floor), the twin placing its own twelve by
    G2.1 step 2's old exchanges: in each column on its own, the cells of
    twelve chosen rows exchanged with the blank cells, each column pairing
    them its own way. The file again holds twelve records holding nothing
    and every band total, while each row that took the cells is made of several rows:
    a family MISSED. The same twelve rows emptied WHOLE (every column paired
    alike) moves no table: every line HELD."""
    for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    rows = _clinic_rows()
    empty_at = set(range(100, 112))
    described = Described(tmp_path, HEADER, rows, empty_at)
    assert chain_rules.records_holding_nothing(described.document) == 12
    code, report, _screen = described.validate(rows, empty_at=empty_at)
    assert code == 0 and set(_verdicts(report)[1].values()) == {"HELD"}
    chosen = list(range(400, 412))
    blank = sorted(empty_at)
    grid = []
    for at in range(len(rows)):
        if at in empty_at:
            grid += [[""] * len(HEADER)]
        grid += [list(rows[at])]
    blank_rows = [b + sorted(empty_at).index(b) for b in blank]
    chosen_rows = [c + len(empty_at) for c in chosen]
    for pairing in ("whole", "per column"):
        mutated = [list(row) for row in grid]
        for place in range(len(HEADER)):
            shift = place if pairing == "per column" else 0
            for k in range(len(chosen_rows)):
                target = blank_rows[(k + shift) % len(blank_rows)]
                mutated[target][place], mutated[chosen_rows[k]][place] = mutated[chosen_rows[k]][place], mutated[target][place]
        code, report, _screen = described.validate(mutated)
        totals, families = _verdicts(report)
        assert set(totals.values()) == {"HELD"}, pairing
        if pairing == "whole":
            assert set(families.values()) == {"HELD"} and code == 0
        else:
            assert "MISSED" in families.values() and code == 3


def test_mutant_4_whole_rows_shuffled_moves_nothing(clinic):
    """Mutant 4: whole rows shuffled together: every line exactly as before,
    the chain's section byte for byte, the same exit code."""
    order = list(range(len(clinic.rows)))
    random.Random(5).shuffle(order)
    code, report, _screen = clinic.validate([clinic.rows[at] for at in order])
    code_before, report_before, _screen = clinic.validate(clinic.rows)
    assert code == code_before == 0
    assert _section(report) == _section(report_before)



def test_mutant_5_a_chain_that_dropped_a_parent_misses_that_family(clinic):
    """Mutant 5: a twin dealt from a copy of the chain whose family F lost
    one parent (its table summed over that parent), checked against the
    original description: F MISSED, every band total HELD. The twin dealt
    from the original chain with the same words holds every family."""
    at, dropped, families = _dropped_parent(clinic)
    code, report, _screen = clinic.validate(_walk_twin(clinic, families, salt="drop"))
    totals, verdicts = _verdicts(report)
    assert verdicts[at] == "MISSED", (at, dropped)
    assert set(totals.values()) == {"HELD"} and code == 3
    code, report, _screen = clinic.validate(_walk_twin(clinic, salt="drop"))
    assert set(_verdicts(report)[1].values()) == {"HELD"} and code == 0



def test_mutant_6_band_totals_differ_and_their_families_are_not_judged_in_the_same_words(clinic):
    """Mutant 6: a file whose band totals differ from the published ones, by
    3 rows and by 30: `pressure`'s total line MISSED, every family holding
    it 'not judged' in V12.3's fixed words, every other line HELD, and the
    two files' sections the SAME bytes: no number tells how far off."""
    sections = []
    for moved in (3, 30):
        code, report, _screen = clinic.validate(_off_by(clinic, moved))
        totals, families = _verdicts(report)
        assert totals["pressure"] == "MISSED"
        assert all(verdict == "HELD" for name, verdict in totals.items() if name != "pressure")
        for at in range(len(_families(clinic))):
            assert families[at] == ("WITHHELD" if at in _holding(clinic, "pressure") else "HELD"), (moved, at)
        assert chain_validation.NOT_JUDGED in report
        assert code == 3
        sections += [_section(report)]
    assert sections[0] == sections[1]


def test_a_cell_in_no_published_band_misses_its_total_line(clinic):
    """A file holding one more row whose cells stand in no published band
    (a word in a number column, a blank where the table held none) keeps
    every band's count, yet its total lines read MISSED: the file holds a
    row the published bands do not, and the families holding those columns
    are not judged. Read as a count alone, every total would be HELD."""
    rows = [list(row) for row in clinic.rows] + [["unknown", "", "", "unknown", ""]]
    code, report, _screen = clinic.validate(rows)
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"MISSED"}, totals
    assert set(families.values()) == {"WITHHELD"} and code == 3


# -- what a report may print (V12.3) ------------------------------------------


def test_no_measured_number_and_no_published_cell_of_one_to_ten_is_printed(clinic):
    """Every number on a published-table or a total line is 0 or at least
    the floor: those lines print the description's own numbers only. A
    measured cell of 1 to 10 (the mutant 1 file's moved table holds cells
    the published one does not) prints nowhere: the section of a file that
    misses is the section of one that holds, the verdict words aside."""
    code, report, _screen = clinic.validate(clinic.rows)
    section = _section(report)
    for line in section.split("\n"):
        if re.match(r"^\s+(\(\d[\d, ]*\) )?\d[\d, ]*$", line) or "published L0 totals" in line:
            numbers = [int(x) for x in re.findall(r"\d+", line.split("totals")[-1] if "totals" in line else re.sub(r"^\s+\([\d, ]*\)", "", line))]
            assert all(x == 0 or x >= FLOOR for x in numbers), line
    at, _family = _family_with_parents(clinic)
    place = clinic.header.index(_families(clinic)[at]["child"])
    rows = [list(row) for row in clinic.rows]
    order = list(range(len(rows)))
    random.Random(3).shuffle(order)
    for row in range(len(rows)):
        rows[row][place] = clinic.rows[order[row]][place]
    code_missed, missed, _screen = clinic.validate(rows)
    assert code_missed == 3
    assert re.sub(r"HELD|MISSED", "V", _section(missed)) == re.sub(r"HELD|MISSED", "V", section)


def test_a_gate_the_file_s_own_facts_close_prints_v5_3_s_sentence_whatever_the_table(tmp_path, monkeypatch):
    """V12.3: a verdict stands only where the published tables are eligible
    beside the FILE's own facts (RULE W1 read with the file's own-fact
    groups). `level` holds 1 to 20, thirty rows each, and `flag` is 1
    exactly above 10, so the published `flag | level` at `L2` is
    [[300, 0], [0, 300]]: each band of `level` reaches one band of `flag`.
    The table holds no small group of `level`, so the table's own check
    reads every line HELD. A file writing five of its `level` 1 cells as 0
    keeps every band total, but its own description holds a group of five
    rows inside `level`'s lowest band, which the published table would
    confine to one band of `flag`: every family line prints V5.3's
    sentence, never HELD or MISSED, both for that file and for one whose
    `flag` is turned round as well (a table the published one is not), the
    two sections the same bytes."""
    for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    draw = random.Random(4)
    rows = []
    for row in range(600):
        level = 1 + row % 20
        rows += [[f"{level}", "1" if level > 10 else "0", draw.choice(["x", "y"])]]
    draw.shuffle(rows)
    described = Described(tmp_path, ["level", "flag", "other"], rows)
    flags = [f for f in _families(described) if f["child"] == "flag"]
    assert flags and flags[0]["table"] == [[300, 0], [0, 300]], _families(described)
    code, report, _screen = described.validate(rows)
    assert code == 0 and set(_verdicts(report)[1].values()) == {"HELD"}
    ones = [at for at in range(len(rows)) if rows[at][0] == "1"][:5]
    grouped = [list(row) for row in rows]
    for at in ones:
        grouped[at][0] = "0"
    flipped = [list(row) for row in grouped]
    for row in flipped:
        row[1] = "0" if row[1] == "1" else "1"
    sections = []
    for candidate in (grouped, flipped):
        code, report, _screen = described.validate(candidate)
        totals, families = _verdicts(report)
        assert set(totals.values()) == {"HELD"}, totals
        assert set(families.values()) == {"WITHHELD"}, families
        assert validation.CHAIN_GATE_CLOSED in _section(report)
        sections += [_section(report)]
    assert sections[0] == sections[1]


# -- the REPORT-ONLY lines ------------------------------------------------------


def _brute_implied(statistical, first, second):
    """The implied joint of two columns, by multiplying EVERY family's conditional over every joint cell (no elimination)."""
    ladder = {e["column"]: e for e in statistical["ladder"]}
    chain = statistical["chain"]
    level = {f["child"]: int(f["level"][1]) for f in chain}

    def bands(name, lv):
        entry = ladder[name]
        return len(entry["l0"]) if lv == 0 else len(entry["l1"] if lv == 1 else entry["l2"])

    def coarsen(name, finer, coarser):
        entry = ladder[name]
        groups = [[[i] for i in range(len(entry["l0"]))], entry["l1"], entry["l2"]]
        to = {}
        for b, members in enumerate(groups[coarser]):
            for i in members:
                to[i] = b
        return [to[members[0]] for members in groups[finer]]

    names = [f["child"] for f in chain]
    out = {}

    def walk(at, cell, share):
        if share == 0:
            return
        if at == len(chain):
            key = (cell[first], cell[second])
            out[key] = out.get(key, Fraction(0)) + share
            return
        family = chain[at]
        index = 0
        for parent in family["parents"]:
            p, lv = parent["column"], int(parent["level"][1])
            index = index * bands(p, lv) + coarsen(p, level[p], lv)[cell[p]]
        row = family["table"][index]
        total = sum(row)
        for band in range(len(row)):
            if row[band]:
                walk(at + 1, dict(cell, **{family["child"]: band}), share * Fraction(row[band], total))

    walk(0, {}, Fraction(1))
    del names
    return [[out.get((a, b), Fraction(0)) for b in range(bands(second, level[second]))] for a in range(bands(first, level[first]))]


def test_the_report_only_lines_print_the_implied_table_and_its_spread(clinic):
    """Every candidate pair has one line with the word the description
    publishes, and no other words; a pair reading `implied` prints the
    shares the published families imply, here equal (exactly, before the
    four decimals) to a brute-force product of every family's conditional,
    and the dealing spread inside the oracle's certified enclosure. On
    CHo's frozen case (A, B | A, C | B on 80 rows) the shares are 1/4, 1/4,
    1/8, 3/8 and the spread 0.0940."""
    code, report, _screen = clinic.validate(clinic.rows)
    words = clinic.statistical["words"]
    assert all(sorted(entry) == ["columns", "word"] for entry in words)
    section = _section(report)
    for entry in words:
        a, b = entry["columns"]
        assert len(re.findall(rf"^  '{a}' and '{b}': {entry['word']}", section, re.M)) == 1
    implied = [entry["columns"] for entry in words if entry["word"] == "implied"]
    assert implied, "the fixture's chain leaves a pair implied"
    lines = chain_validation.lines_of(
        clinic.document,
        __import__("synthtwin.reading", fromlist=["read_table"]).read_table(str(clinic.table), small_cell_floor=FLOOR),
        clinic.document,
        validation.settings_for(__import__("synthtwin.contract", fromlist=["load_profile"]).load_profile_document(str(clinic.path))[0]),
        [],
        [],
        [],
        (),
    )
    tabled = clinic.document["n_rows"]
    for pair in lines.pairs:
        if pair.word != "implied":
            assert pair.shares == () and pair.spread == ""
            continue
        expected = _brute_implied(clinic.statistical, *pair.columns)
        assert [[Fraction(n, d) for n, d in row] for row in pair.shares] == expected
        counts = [[share * tabled for share in row] for row in expected]
        _radicands, low, high = co.dealing_spread(counts, tabled)
        assert Fraction(int(pair.spread.replace(".", "")), 10000) - Fraction(1, 20000) <= high
        assert low <= Fraction(int(pair.spread.replace(".", "")), 10000) + Fraction(1, 20000)
        assert f"implied; dealing spread {pair.spread}" in section
    # CHo's frozen case, through the product's own functions.
    scales = {
        "A": chain_rules.Ladder("A", (("a0",), ("a1",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (40, 40), (True, True)),
        "B": chain_rules.Ladder("B", (("b0",), ("b1",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (40, 40), (True, True)),
        "C": chain_rules.Ladder("C", (("c0",), ("c1",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (30, 50), (True, True)),
    }
    families = [
        chain_rules.Family("A", 0, (), None, (40, 40)),
        chain_rules.Family("B", 0, (("A", 0),), 0, (30, 10, 10, 30)),
        chain_rules.Family("C", 0, (("B", 0),), 1, (25, 15, 5, 35)),
    ]
    shares = chain_validation.implied_shares(families, scales, "A", "C")
    assert shares == [[(1, 4), (1, 4)], [(1, 8), (3, 8)]]
    frozen = json.loads((REPOSITORY / "tests" / "reference" / "chain-oracle-vectors.json").read_text(encoding="utf-8"))["chain"]["implied_pair"]
    assert frozen["implied"] == [["20", "20"], ["10", "30"]]
    low, high = chain_validation.dealing_spread(shares, 80)
    assert Fraction(low, 2**61) <= Fraction(frozen["spread_high"]) and Fraction(frozen["spread_low"]) <= Fraction(high, 2**61)
    assert chain_validation.spread_text(low) == "0.0940"


# -- the screen's one line ------------------------------------------------------


def test_the_screen_keeps_one_line_and_the_written_report_the_section(clinic):
    """The written report holds the whole section; the screen prints the same
    report with the section as ONE summary line, and nothing else of it."""
    code, report, screen = clinic.validate(clinic.rows)
    assert "BETWEEN COLUMNS: THE CHAIN'S FAMILY TABLES (V12)" in report
    assert "BETWEEN COLUMNS: THE CHAIN'S FAMILY TABLES (V12)" not in screen
    between = [line for line in screen.split("\n") if line.startswith("Between columns:")]
    assert len(between) == 1 and "HELD" in between[0]
    assert "published L0 totals" not in screen and "dealing spread" not in screen
    assert report.split("BETWEEN COLUMNS")[0].split("\n")[-3] in screen


# -- S12: with the switch at its default nothing moves --------------------------


def test_a_description_without_a_chain_validates_to_the_same_bytes_either_way(tmp_path, monkeypatch, clinic):
    """A description carrying no chain, validated with the switch and without
    it: the same written report byte for byte, the same screen and the same
    exit code. And the switched description is refused WITHOUT the switch,
    invariant S12 word for word."""
    monkeypatch.chdir(tmp_path)
    table = _write(tmp_path / "plain.csv", HEADER, _clinic_rows(300, seed=2))
    code, said = _quiet(lambda: cli.main(["profile", str(table), "--out-dir", str(tmp_path)]))
    assert code == 0, said
    described = tmp_path / "plain-profile.json"
    assert json.loads(described.read_text(encoding="utf-8"))["relationships"]["statistical"] is None
    runs = []
    for switched in (False, True):
        out = tmp_path / f"out-{switched}"
        out.mkdir()
        run = cli.ChainRun() if switched else None
        code, said = _quiet(lambda: cli.main(["validate", str(described), "--twin", str(table), "--out-dir", str(out)], chain=run))
        runs += [(code, (out / "plain-quality.txt").read_bytes(), said.replace(str(out), "OUT"))]
    assert runs[0] == runs[1]
    code, report, said = clinic.validate(clinic.rows, switched=False)
    assert code == 1 and report == "" and "statistical" in said


def test_an_outcome_without_chain_lines_renders_the_same_on_the_screen(clinic):
    """`quality.report_pieces(..., screen=True)` changes nothing on an outcome carrying no chain lines."""
    from synthtwin import contract

    loaded = contract.load_profile_document(str(clinic.path))[0]
    outcome = validation.measure(loaded, str(clinic.table))
    assert outcome.chain is None
    assert quality.report_pieces(loaded, outcome) == quality.report_pieces(loaded, outcome, screen=True)


# -- CHo's oracle agrees with V12's EXACT lines -----------------------------------


def test_the_oracle_agrees_with_v12_s_exact_lines_on_the_switched_case(tmp_path, monkeypatch):
    """`tests/test_chain_oracle.py`'s switched case (its 600-row table, `ward`
    answered `keep` in round two, the oracle's test key): V12 on the table
    itself reads every line HELD, and the oracle's own count of every
    family on the file (`chain_oracle.table_of` at the published levels)
    equals the published table. On a file whose `score` cells are
    exchanged between rows of different `ward` (its band totals kept), V12
    reads MISSED exactly on the families whose oracle count differs from
    the published table, and HELD on the rest."""
    for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.setenv(name, str(tmp_path / "home"))
    rows = [["%d" % (20 + (r * 7) % 61), "w%d" % (r % 3), "%d" % ((r * 13) % 97)] for r in range(600)]
    header = ["age", "ward", "score"]
    table = _write(tmp_path / "trial.csv", header, rows)
    data = tmp_path / "data"
    data.mkdir(mode=0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    key.write_bytes(oc.TEST_KEY)
    code, said = _quiet(lambda: cli.main(["profile", str(table), "--out-dir", str(tmp_path)]))
    assert code == 0, said
    questions = tmp_path / "trial-questions.json"
    asked = json.loads(questions.read_text(encoding="utf-8"))
    for entry in asked["asked"]:
        if entry["column"] == "ward":
            entry["your_answer"] = "keep"
    questions.write_text(json.dumps(asked, indent=1) + "\n", encoding="utf-8", newline="\n")
    code, said = _quiet(
        lambda: cli.main(["profile", str(table), "--out-dir", str(tmp_path), "--answers", str(questions)], chain=cli.ChainRun(folder=str(data)))
    )
    assert code == 0, said
    path = tmp_path / "trial-profile.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    statistical = document["relationships"]["statistical"]
    assert statistical is not None and statistical["chain"]
    blocks = {block["name"]: block for block in document["columns"]}
    real = {name: [row[at] for row in rows] for at, name in enumerate(header)}
    lads = {e["column"]: _oracle_ladder(e["column"], blocks[e["column"]], real[e["column"]], position=header.index(e["column"])) for e in statistical["ladder"]}
    chain = _oracle_chain(statistical)
    place = header.index("score")
    mutated = [list(row) for row in rows]
    ward = [row[1] for row in rows]
    swaps = 0
    for r in range(0, 600, 2):
        partner = r + 1
        if ward[r] != ward[partner] and lads["score"].row_l0[r] != lads["score"].row_l0[partner]:
            mutated[r][place], mutated[partner][place] = mutated[partner][place], mutated[r][place]
            swaps += 1
    assert swaps > 0
    for candidate in (rows, mutated):
        out = tmp_path / f"v{len(list(tmp_path.glob('v*')))}"
        out.mkdir()
        measured = _write(out / "file.csv", header, candidate)
        code, said = _quiet(lambda: cli.main(["validate", str(path), "--twin", str(measured), "--out-dir", str(out)], chain=cli.ChainRun()))
        report = (out / "file-quality.txt").read_text(encoding="utf-8")
        totals, families = _verdicts(report)
        assert set(totals.values()) == {"HELD"}
        by_text = {name: {real[name][r]: lads[name].row_l0[r] for r in range(600)} for name in lads}
        recoded = {}
        for name, lad in lads.items():
            values = [row[header.index(name)] for row in candidate]
            recoded[name] = co.Ladder(lad.name, lad.role, lad.l0, lad.totals, lad.l1, lad.l2, [by_text[name][v] for v in values], lad.taken_in, lad.ordered, lad.position)
        for at, family in enumerate(chain):
            counted = co.table_of(recoded, family.child, family.level, family.parents) if family.parents else [recoded[family.child].band_totals(family.level)]
            assert families[at] == ("HELD" if counted == family.table else "MISSED"), at
        assert code == (0 if candidate is rows else 3)


# -- the loader's invariants ------------------------------------------------------


@pytest.mark.parametrize(
    "invariant, damage",
    [
        ("S25", lambda st: st["chain"][1]["table"][0].__setitem__(0, st["chain"][1]["table"][0][0] - 5) or st["chain"][1]["table"][0].__setitem__(1, st["chain"][1]["table"][0][1] + 5)),
        ("S23", lambda st: st["ladder"][0]["totals"].__setitem__(0, st["ladder"][0]["totals"][0] + 1)),
        ("S27", lambda st: st["words"][0].__setitem__("word", "implied" if st["words"][0]["word"] == "exact" else "exact")),
        ("S24", lambda st: st["chain"][1].__setitem__("anchor", 3)),
    ],
)
def test_the_loader_refuses_a_broken_chain_before_reading_the_file(clinic, invariant, damage, tmp_path):
    """S23 to S27, as V12 states them, are the loader's: a description whose
    chain breaks one is refused by `validate` with the switch, exit 1, the
    invariant named, and no report written."""
    document = json.loads(clinic.path.read_text(encoding="utf-8"))
    damage(document["relationships"]["statistical"])
    broken = fixtures.write_profile(tmp_path, "broken-profile.json", document)
    code, report, said = clinic.validate(clinic.rows, description=broken)
    assert code == 1 and report == ""
    assert f"breaks its rule {invariant}" in said, said


# -- REPAIR 1 (lane CHv, plan P4-D430): each item pinned by a case red on its mutant --


def _home(monkeypatch, folder):
    for name in ("HOME", "APPDATA", "LOCALAPPDATA", "XDG_DATA_HOME"):
        monkeypatch.setenv(name, str(folder / "home"))


def _write_lines(path, header, rows, before=0, inside=0, after=0, cell=""):
    """A file of `rows` with records holding nothing written before, at the middle of and after them."""
    blank = ",".join([cell] * len(header))
    middle = len(rows) // 2
    lines = [",".join(header)] + [blank] * before
    lines += [",".join(row) for row in rows[:middle]] + [blank] * inside
    lines += [",".join(row) for row in rows[middle:]] + [blank] * after
    path.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
    return path


def _validate_file(described, path):
    out = path.parent
    code, said = _quiet(lambda: cli.main(["validate", str(described.path), "--twin", str(path), "--out-dir", str(out)], chain=cli.ChainRun()))
    return code, (out / (path.stem + "-quality.txt")).read_text(encoding="utf-8"), said


@pytest.fixture(scope="module")
def split(tmp_path_factory):
    """`level` 1 to 20 (thirty rows each), `flag` 1 exactly above 10, `other` blank on a third of `flag` 0's rows.

    The published chain: `level` at `L2`; `flag | level` [[300, 0], [0,
    300]]; `other | flag`, its blank band reached by `flag` 0 alone.
    """
    with pytest.MonkeyPatch.context() as patch:
        folder = tmp_path_factory.mktemp("split")
        _home(patch, folder)
        draw = random.Random(3)
        rows = []
        for row in range(600):
            level = 1 + row % 20
            flag = "1" if level > 10 else "0"
            rows += [[f"{level}", flag, "" if flag == "0" and row % 3 == 0 else draw.choice(["x", "y"])]]
        draw.shuffle(rows)
        described = Described(folder, ["level", "flag", "other"], rows)
        tables = {f["child"]: f["table"] for f in _families(described)}
        assert tables["flag"] == [[300, 0], [0, 300]] and tables["other"][1][0] == 0, _families(described)
        yield described


def test_rule_w1_reads_the_file_s_own_spellings_of_nothing(split):
    """Item 4 (b) of skeptic 1: an own-fact group only `chain_rules.small_group_bands`
    reads. Five of `other`'s blank cells written `NA` keep every band
    total (both read as nothing), but the file's own description counts
    the spelling `NA` on five rows, a group inside `other`'s blank band
    that `other | flag` confines to `flag` 0: every family line prints
    V5.3's sentence. The table's own check reads every line HELD."""
    code, report, _screen = split.validate(split.rows)
    assert code == 0 and set(_verdicts(report)[1].values()) == {"HELD"}
    rows = [list(row) for row in split.rows]
    for at in [at for at in range(len(rows)) if rows[at][2] == ""][:5]:
        rows[at][2] = "NA"
    code, report, _screen = split.validate(rows)
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"}, totals
    assert set(families.values()) == {"WITHHELD"}, families
    assert validation.CHAIN_GATE_CLOSED in _section(report)


def test_rule_w1_reads_the_file_s_own_runs_of_values(split):
    """Item 4 (c) of skeptic 1: an own-fact group only `chain.value_run_bands` reads.
    Twenty-two of `level`'s 2 cells written 1 keep `level`'s lowest band
    (1 and 2) at its published 60 rows, and the file's own description
    then names the mode 1 on 52 rows: the band less its mode holds 8 rows,
    a group `flag | level` confines to `flag` 0. No count the file's own
    block publishes is under the floor, so the block's list alone sees
    nothing: every family line prints V5.3's sentence only because the
    file's own values are read."""
    rows = [list(row) for row in split.rows]
    for at in [at for at in range(len(rows)) if rows[at][0] == "2"][:22]:
        rows[at][0] = "1"
    code, report, _screen = split.validate(rows)
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"}, totals
    assert set(families.values()) == {"WITHHELD"}, families
    assert validation.CHAIN_GATE_CLOSED in _section(report)


def test_a_column_the_file_lacks_is_read_as_holding_a_group_in_every_band(split, tmp_path):
    """Items 5 and V12's reading (c): a file without `level` reads `level`'s
    total and both families holding it NOT CHECKABLE, never 'not judged',
    and, read for RULE W1 as holding a group in every band, closes the
    gate over the one family it does not hold (`other | flag`), which
    prints V5.3's sentence rather than HELD."""
    rows = [row[1:] for row in split.rows]
    code, report, _screen = split.validate(rows, header=["flag", "other"])
    totals, families = _verdicts(report)
    assert totals == {"level": "NOT CHECKABLE", "flag": "HELD", "other": "HELD"}, totals
    index = {f["child"]: at for at, f in enumerate(_families(split))}
    assert families[index["level"]] == "NOT CHECKABLE" and families[index["flag"]] == "NOT CHECKABLE"
    assert families[index["other"]] == "WITHHELD", families
    section = _section(report)
    assert chain_validation.NO_SUCH_COLUMN in section and chain_validation.A_MEMBER_NOT_CHECKABLE in section
    assert chain_validation.NOT_JUDGED not in section


@pytest.mark.parametrize("case", ["no gender", "pressure as words"])
def test_not_checkable_lines_on_the_clinic(clinic, case):
    """Item 5 of skeptic 1 (V3.3): a file without `gender` reads gender's total
    and every family holding it NOT CHECKABLE, the others HELD; `pressure`
    written as words reads under another role, and its total and every
    family holding it are NOT CHECKABLE, never MISSED."""
    column = "gender" if case == "no gender" else "pressure"
    place = clinic.header.index(column)
    if case == "no gender":
        header = [name for name in clinic.header if name != column]
        rows = [[cell for at, cell in enumerate(row) if at != place] for row in clinic.rows]
    else:
        header = None
        rows = [list(row) for row in clinic.rows]
        for row in rows:
            row[place] = "high" if Fraction(row[place]) > 130 else "low"
    code, report, _screen = clinic.validate(rows, header=header)
    totals, families = _verdicts(report)
    for name, verdict in totals.items():
        assert verdict == ("NOT CHECKABLE" if name == column else "HELD"), (name, verdict)
    holding = _holding(clinic, column)
    for at, verdict in families.items():
        assert verdict == ("NOT CHECKABLE" if at in holding else "HELD"), (at, verdict)
    reason = chain_validation.NO_SUCH_COLUMN if case == "no gender" else chain_validation.ANOTHER_ROLE
    assert reason in _section(report)


def _verdict_counts(report):
    """The verdict summary's printed count of each outcome, and its NOT CHECKABLE count."""
    top = report.split("THE VERDICT", 1)[1].split("WHAT THIS REPORT DOES NOT SAY", 1)[0]
    counts = {verdict: int(number) for number, verdict in re.findall(r"^\s+(\d+)  (HELD|WITHIN BOUND|AUTHORIZED DEVIATION|WITHHELD|MISSED) --", top, re.M)}
    counts["NOT CHECKABLE"] = int(re.search(r"A further (\d+) obligation\(s\) are NOT", top).group(1))
    return counts


@pytest.mark.parametrize("case", ["off by 30", "no gender"])
def test_the_verdict_counts_every_chain_line_and_says_why_each_is_withheld(clinic, case, tmp_path):
    """Item 6 of skeptic 1: the verdict at the top counts every chain line, HELD,
    MISSED, WITHHELD and NOT CHECKABLE, on top of the single-column
    obligations; and the handling paragraph counts the lines V5.3's rule
    closed over apart from the family lines read 'not judged', naming the
    other reason. The screen's one line prints the chain's own counts."""
    from synthtwin import contract

    if case == "off by 30":
        header, rows = None, _off_by(clinic, 30)
    else:
        place = clinic.header.index("gender")
        header = [name for name in clinic.header if name != "gender"]
        rows = [[cell for at, cell in enumerate(row) if at != place] for row in clinic.rows]
    code, report, screen = clinic.validate(rows, header=header)
    measured = _write(tmp_path / "file.csv", header or clinic.header, rows)
    loaded, document = contract.load_profile_document(str(clinic.path))
    plain = validation.measure(loaded, str(measured)).census
    chained = validation.measure(loaded, str(measured), "", document)
    lines = chained.chain
    counts = _verdict_counts(report)
    assert counts["HELD"] == plain.held + lines.held
    assert counts["MISSED"] == plain.missed + lines.missed
    assert counts["WITHHELD"] == plain.withheld + lines.withheld
    assert counts["NOT CHECKABLE"] == plain.not_checkable + lines.not_checkable
    if case == "off by 30":
        judged_not = len(_holding(clinic, "pressure"))
        assert lines.not_judged == judged_not == lines.withheld and lines.missed == 1
        handling = report.split("HOW TO KEEP THIS FILE", 1)[1]
        assert f"{judged_not} more between-columns family line(s) read WITHHELD for another" in handling
        closed = plain.withheld
        if closed:
            assert f"On this file it closed over {closed} obligation(s)" in handling
        else:
            assert "On this file the rule closed over nothing" in handling
    else:
        assert lines.not_checkable == 1 + len(_holding(clinic, "gender")) and lines.not_judged == 0
    between = [line for line in screen.split("\n") if line.startswith("Between columns:")]
    assert between == [
        f"Between columns: {lines.held} band-total and family line(s) HELD, {lines.missed} MISSED, "
        f"{lines.withheld} withheld or not judged, {lines.not_checkable} not checkable, over "
        f"{len(lines.families)} published family table(s); "
        f"{sum(1 for pair in lines.pairs if pair.word == 'implied')} pair(s) of columns not in one family "
        f"(the chain only implies them; not checked). The written report holds every line, with the published tables."
    ]


def test_rule_we_reads_the_file_s_own_records_holding_nothing(tmp_path, monkeypatch):
    """Item 4 (a) of skeptic 1 (V12.3, RULE WE read with the file's own census
    of records holding nothing). Three label columns with 200, 200 and 25
    blank cells and no record holding nothing; the file is the same rows
    and 33 records holding nothing, 11 before, 11 inside and 11 after them,
    so its own description leaves no room for a row blank in every column
    while the published tables count at least 25 such rows: every total
    HELD, every family line V5.3's sentence. The same file with `C`'s 25
    blank cells written `NA` (still nothing, so every total holds) holds
    no blank cell of `C` at all: no row is blank in every column, and every
    family line is judged, HELD."""
    _home(monkeypatch, tmp_path)
    draw = random.Random(9)
    rows = []
    for _row in range(3000):
        a = draw.choice(["x", "y"])
        b = ("u" if a == "x" else "v") if draw.random() < 0.8 else draw.choice(["u", "v"])
        rows += [[a, b, draw.choice(["p", "q", "s"])]]
    for at in range(0, 200):
        rows[at][0] = ""
    for at in range(170, 370):
        rows[at][1] = ""
    for at in range(1000, 1025):
        rows[at][2] = ""
    draw.shuffle(rows)
    header = ["A", "B", "C"]
    described = Described(tmp_path, header, rows)
    assert chain_rules.records_holding_nothing(described.document) == 0
    code, report, _screen = described.validate(rows)
    assert code == 0 and set(_verdicts(report)[1].values()) == {"HELD"}
    (tmp_path / "we").mkdir()
    code, report, _said = _validate_file(described, _write_lines(tmp_path / "we" / "twin.csv", header, rows, 11, 11, 11))
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"} and set(families.values()) == {"WITHHELD"}, (totals, families)
    assert validation.CHAIN_GATE_CLOSED in _section(report)
    spelled = [row[:2] + ["NA" if row[2] == "" else row[2]] for row in rows]
    (tmp_path / "na").mkdir()
    code, report, _said = _validate_file(described, _write_lines(tmp_path / "na" / "twin.csv", header, spelled, 11, 11, 11))
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"} and set(families.values()) == {"HELD"}, (totals, families)


def test_the_file_s_calendar_censuses_are_its_own_facts(tmp_path, monkeypatch):
    """Codex's item 1 on the build: RULE W1 reads the file's own-fact groups,
    and a periodic census draws some of them, so V12's own description of
    the file holds its calendar censuses. 4,000 weekly visits, a day later
    from row 2,000 on, `flag` yes from row 1,992; the described table has
    row 800 moved to a Tuesday. The file with that row back on its Monday
    holds every band total, and its weekday census places 8 Mondays among
    the 2,000 Tuesdays of the later band, a group `flag | visit` confines:
    every family line prints V5.3's sentence (with the censuses left out,
    both read HELD)."""
    import datetime

    _home(monkeypatch, tmp_path)

    def day(row, moved):
        shift = 7 * (row // 8) + (1 if row >= 2000 else 0) + (1 if moved and row == 800 else 0)
        return (datetime.date(2010, 1, 4) + datetime.timedelta(days=shift)).isoformat()

    rows = [[day(row, True), "no" if row < 1992 else "yes"] for row in range(4000)]
    described = Described(tmp_path, ["visit", "flag"], rows)
    assert [f["table"] for f in _families(described)] == [[[1992, 2008]], [[0, 1992], [2008, 0]]], _families(described)
    code, report, _screen = described.validate(rows)
    assert code == 0 and set(_verdicts(report)[1].values()) == {"HELD"}
    code, report, _screen = described.validate([[day(row, False), rows[row][1]] for row in range(4000)])
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"} and set(families.values()) == {"WITHHELD"}, (totals, families)
    assert validation.CHAIN_GATE_CLOSED in _section(report)


def test_a_file_whose_record_numbers_repeat_is_counted_in_people(tmp_path, monkeypatch):
    """Codex's item 2 on the build: `id` declared as record numbers, one a row
    in the described table; the file writes each id on ten rows (100
    people). Its own description counts every value in people and
    publishes no family (the chain's `OFF_PERSON`), so no published band
    applies: every total and family line NOT CHECKABLE, in the words that
    say why. The table itself reads every line HELD."""
    _home(monkeypatch, tmp_path)
    rows = []
    for row in range(1000):
        a = "alpha" if row < 50 else "beta" if row < 100 else "gamma" if row < 550 else "delta"
        rows += [[f"{100000 + row}", a, "yes" if (a in ("alpha", "gamma")) != (row % 10 < 3) else "no"]]
    table = _write(tmp_path / "clinic.csv", ["id", "a", "b"], rows)
    data = tmp_path / "data"
    data.mkdir(mode=0o700)
    key = data / "chain-key"
    key.touch(mode=0o600)
    key.write_bytes(oc.TEST_KEY)
    code, said = _quiet(lambda: cli.main(["profile", str(table), "--out-dir", str(tmp_path), "--identifier", "id"], chain=cli.ChainRun(folder=str(data))))
    assert code == 0, said
    path = tmp_path / "clinic-profile.json"
    assert json.loads(path.read_text(encoding="utf-8"))["relationships"]["statistical"]["chain"]
    verdicts = []
    for name, candidate in (("self", rows), ("people", [[f"{100000 + at // 10}"] + row[1:] for at, row in enumerate(rows)])):
        (tmp_path / name).mkdir()
        measured = _write(tmp_path / name / "file.csv", ["id", "a", "b"], candidate)
        code, said = _quiet(lambda: cli.main(["validate", str(path), "--twin", str(measured), "--out-dir", str(tmp_path / name)], chain=cli.ChainRun()))
        report = (tmp_path / name / "file-quality.txt").read_text(encoding="utf-8")
        verdicts += [(_verdicts(report), report)]
    (totals, families), _report = verdicts[0]
    assert set(totals.values()) == {"HELD"} and set(families.values()) == {"HELD"}
    (totals, families), report = verdicts[1]
    assert set(totals.values()) == {"NOT CHECKABLE"} and set(families.values()) == {"NOT CHECKABLE"}, (totals, families)
    assert chain_validation.COUNTED_IN_PEOPLE in _section(report)


def test_a_miss_between_columns_only_is_named_where_it_is(clinic):
    """Codex's item 3 and skeptic 1's item 7: a file missing one family alone
    (mutant 1, every single-column obligation met) says no single-column
    obligation was missed and where the between-columns misses are, never
    'Nothing was missed'; the verdict names them too; and under the switch
    the report says which tables between columns were checked, never that
    none is carried."""
    from synthtwin import contract

    at, family = _family_with_parents(clinic)
    codes = _band_codes(clinic, clinic.rows)
    level = int(family["level"][1])

    def cell_of(row):
        return tuple(codes[p["column"]][0].coarsen(int(p["level"][1]))[codes[p["column"]][1][row]] for p in family["parents"])

    child_lad, child_l0 = codes[family["child"]]
    to_level = child_lad.coarsen(level)
    second = next(r for r in range(1, len(clinic.rows)) if cell_of(r) != cell_of(0) and to_level[child_l0[r]] != to_level[child_l0[0]])
    place = clinic.header.index(family["child"])
    rows = [list(row) for row in clinic.rows]
    rows[0][place], rows[second][place] = rows[second][place], rows[0][place]
    code, report, _screen = clinic.validate(rows)
    loaded, document = contract.load_profile_document(str(clinic.path))
    measured = _write(clinic.folder / "only-family.csv", clinic.header, rows)
    assert validation.measure(loaded, str(measured)).census.missed == 0
    missed = validation.measure(loaded, str(measured), "", document).chain.missed
    assert code == 3 and _verdicts(report)[1][at] == "MISSED" and missed >= 1
    assert "Nothing was missed" not in report
    assert "No obligation of a single column was missed" in report
    assert f"the section is empty. {missed} between-columns line(s) were" in report
    assert f"Of them, {missed} are between-columns line(s)" in report
    assert "NO CROSS-COLUMN STRUCTURE WAS VALIDATED" not in report
    assert "BETWEEN COLUMNS, ONLY THE PUBLISHED FAMILY TABLES WERE CHECKED." in report
    assert "CHECKED BETWEEN COLUMNS: each table of counts" in report
    assert "the description publishes\nnone" not in report and "the description publishes" in report


def test_the_default_call_to_measure_is_the_three_argument_call(tmp_path, monkeypatch):
    """Skeptic 1's item 1: a run without the switch hands `validation.measure`
    the three arguments it always took, so a caller wrapping it with that
    signature (the health zoo's battery) runs and reads the same report."""
    monkeypatch.chdir(tmp_path)
    table = _write(tmp_path / "plain.csv", HEADER, _clinic_rows(300, seed=2))
    code, said = _quiet(lambda: cli.main(["profile", str(table), "--out-dir", str(tmp_path)]))
    assert code == 0, said
    real = validation.measure
    reports = []
    for wrapped in (False, True):
        if wrapped:

            def keep(description, path, sheet=""):
                return real(description, path, sheet)

            monkeypatch.setattr(validation, "measure", keep)
        out = tmp_path / f"out-{wrapped}"
        out.mkdir()
        code, said = _quiet(lambda: cli.main(["validate", str(tmp_path / "plain-profile.json"), "--twin", str(table), "--out-dir", str(out)]))
        assert code == 0, said
        reports += [(out / "plain-quality.txt").read_bytes()]
    assert reports[0] == reports[1]


def test_an_implied_table_past_its_bounds_is_named_and_not_worked_out(clinic, monkeypatch):
    """Codex's item 4: an implied table is worked out only within the report's
    bounds, decided from the description alone: two root columns of 40
    bands give 1,600 cells (more than 1,024), and no work at all is spent
    on them; a budget spent stops the product. A pair past a bound prints
    its word and why, and no share or spread; the clinic's pairs print
    so when the bound is lowered."""
    def ladder(name, bands):
        return chain_rules.Ladder(name, tuple((f"{name}{k}",) for k in range(bands)), (tuple(range(bands)),) * 3, (bands,) * 3, (11,) * bands, (True,) * bands)

    scales = {"A": ladder("A", 40), "B": ladder("B", 40)}
    families = [chain_rules.Family("A", 0, (), None, (11,) * 40), chain_rules.Family("B", 0, (), None, (11,) * 40)]
    work = chain_validation._Work(5)
    assert chain_validation.implied_shares(families, scales, "A", "B", work) is None and work.left == 5
    small = {"A": ladder("A", 4), "B": ladder("B", 4), "C": ladder("C", 4)}
    linked = [
        chain_rules.Family("A", 0, (), None, (11,) * 4),
        chain_rules.Family("B", 0, (("A", 0),), 0, (11, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11)),
        chain_rules.Family("C", 0, (("B", 0),), 1, (11, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11)),
    ]
    assert chain_validation.implied_shares(linked, small, "A", "C", chain_validation._Work(3)) is None
    assert chain_validation.implied_shares(linked, small, "A", "C")[0] == [(1, 4), (0, 1), (0, 1), (0, 1)]
    # Two trees of the forest: a root column no family reads beside `A` is independent of it.
    small["D"] = ladder("D", 4)
    forest = linked + [chain_rules.Family("D", 0, (), None, (22, 11, 11, 0))]
    assert chain_validation.implied_shares(forest, small, "A", "D")[0] == [(1, 8), (1, 16), (1, 16), (0, 1)]
    assert chain_validation.implied_shares(forest, small, "D", "C")[0] == [(1, 8), (1, 8), (1, 8), (1, 8)]
    monkeypatch.setattr(chain_validation, "IMPLIED_CELLS_AT_MOST", 1)
    code, report, _screen = clinic.validate(clinic.rows)
    section = _section(report)
    implied = [entry["columns"] for entry in clinic.statistical["words"] if entry["word"] == "implied"]
    for a, b in implied:
        assert re.search(rf"^  '{a}' and '{b}': implied\n      {re.escape(chain_validation.TOO_MANY_CELLS)}$", section, re.M)
    assert "implied; dealing spread" not in section and "implied shares" not in section


def test_the_printed_details_of_the_section(clinic):
    """Skeptic 1's item 8: the details a reader reads off the section, each
    pinned. A share prints to four decimals rounded half up; each band's
    legend prints the description's own words; a family's row labels run
    over its parents' bands in the parents' order, the first slowest; an
    `exact` pair names the first family holding both; each row and share
    of an implied table is named by its band words; the dealing spread is
    said in words."""
    assert [quality._chain_share(share) for share in ((1, 3), (2, 3), (1, 8), (1, 20000), (1, 1), (0, 1))] == [
        "0.3333",
        "0.6667",
        "0.1250",
        "0.0001",
        "1.0000",
        "0.0000",
    ]
    code, report, _screen = clinic.validate(clinic.rows)
    section = _section(report)
    for entry in clinic.statistical["ladder"]:
        for at, band in enumerate(entry["l0"]):
            words = []
            for one in band:
                if isinstance(one, list) and len(one) == 2:
                    low, high = one
                    words += ["every value" if low is None and high is None else f"below {high}" if low is None else f"{low} and above" if high is None else f"{low} to below {high}"]
                else:
                    words += [f"{one[0]}" if isinstance(one, list) else f"{one}"]
            assert f"    band {at}: {' + '.join(words)}\n" in section, (entry["column"], at)
    at, family = max(enumerate(_families(clinic)), key=lambda pair: len(pair[1]["parents"]))
    widths = []
    for parent in family["parents"]:
        entry = next(e for e in clinic.statistical["ladder"] if e["column"] == parent["column"])
        widths += [len(entry["l0"]) if parent["level"] == "L0" else len(entry["l1" if parent["level"] == "L1" else "l2"])]
    assert len(widths) >= 2 and min(widths) >= 2, widths
    block = section.split(f"  family {at}: ", 1)[1].split("\n  family ", 1)[0].split("Every pair", 1)[0]
    labels = re.findall(r"^        \(([\d, ]+)\) ", block, re.M)
    import itertools

    assert labels == [", ".join(f"{k}" for k in cell) for cell in itertools.product(*[range(w) for w in widths])]
    for entry in clinic.statistical["words"]:
        a, b = entry["columns"]
        if entry["word"] == "exact":
            first = next(k for k, f in enumerate(_families(clinic)) if {a, b} <= {f["child"]} | {p["column"] for p in f["parents"]})
            assert f"  '{a}' and '{b}': exact (family {first})\n" in section
    lines = chain_validation.lines_of(
        clinic.document,
        __import__("synthtwin.reading", fromlist=["read_table"]).read_table(str(clinic.table), small_cell_floor=FLOOR),
        clinic.document,
        validation.settings_for(__import__("synthtwin.contract", fromlist=["load_profile"]).load_profile_document(str(clinic.path))[0]),
        [],
        [],
        [],
        (),
    )
    legends = {legend.column: legend for legend in lines.legends}
    for pair in lines.pairs:
        if pair.word != "implied":
            continue
        first, second = pair.columns
        for row_at, row in enumerate(pair.shares):
            said = "; ".join(
                f"{quality._chain_band_words(legends[second], pair.levels[1], k)} {quality._chain_share(share)}" for k, share in enumerate(row)
            )
            assert f"        '{first}' {quality._chain_band_words(legends[first], pair.levels[0], row_at)}: {said}\n" in section
    assert "how far a twin dealt at random from these shares would typically" in section


def test_records_of_spaces_hold_nothing(tmp_path, monkeypatch):
    """Skeptic 1's item 8: a record of cells holding only spaces or tabs holds
    nothing (contract 4.1), so the file whose twelve records holding
    nothing are written as spaces sets them aside as the description did:
    every line HELD."""
    _home(monkeypatch, tmp_path)
    rows = _clinic_rows()
    empty_at = set(range(100, 112))
    described = Described(tmp_path, HEADER, rows, empty_at)
    for cell in ("  ", "\t"):
        place = tmp_path / f"cell{len(cell)}{ord(cell[0])}"
        place.mkdir()
        lines = [",".join(HEADER)]
        for at in range(len(rows)):
            if at in empty_at:
                lines += [",".join([cell] * len(HEADER))]
            lines += [",".join(rows[at])]
        (place / "twin.csv").write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")
        code, report, _said = _validate_file(described, place / "twin.csv")
        totals, families = _verdicts(report)
        assert set(totals.values()) == {"HELD"} and set(families.values()) == {"HELD"}, (cell, totals, families)


def test_codes_are_held_one_byte_a_row_where_the_ladder_allows(clinic):
    """Skeptic 1's item 10 and Codex's item 5: a column's codes are held in one
    byte a tabled row where its ladder has at most 254 bands, as a list of
    whole numbers otherwise, and both count the same totals and tables."""
    assert isinstance(chain_validation._code_store(254, 3), bytearray)
    assert chain_validation._code_store(255, 3) == [0, 0, 0]
    narrow = bytearray([1, 2, 2, 0])
    assert chain_validation._band_totals(narrow, 2) == ([1, 2], False)
    assert chain_validation._band_totals([1, 2, 2, 0], 2) == ([1, 2], False)
    scales = {
        "A": chain_rules.Ladder("A", (("a0",), ("a1",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (2, 2), (True, True)),
        "B": chain_rules.Ladder("B", (("b0",), ("b1",)), ((0, 1), (0, 1), (0, 1)), (2, 2, 2), (2, 2), (True, True)),
    }
    family = chain_rules.Family("B", 0, (("A", 0),), 0, (1, 1, 1, 1))
    as_bytes = chain_validation._measured_table(family, scales, {"A": bytearray([1, 1, 2, 2]), "B": bytearray([1, 2, 1, 2])}, 4)
    as_words = chain_validation._measured_table(family, scales, {"A": [1, 1, 2, 2], "B": [1, 2, 1, 2]}, 4)
    assert as_bytes == as_words == [1, 1, 1, 1]


# -- REPAIR 2 (lane CHv, plan P4-D430): the verify's items, each pinned by a case red on its mutant --


def test_the_verdict_names_both_kinds_of_not_checkable_line(clinic):
    """The verify's item 1 on repair 1: a file without `gender` counts, on the
    verdict's NOT CHECKABLE line, the obligations no CSV can evidence AND
    the between-columns lines the file cannot be checked for; the verdict
    says how many of each and where each kind is named, and the list of
    obligations no CSV can evidence says where the others are. The table
    itself (no such line) keeps the sentence it always had."""
    from synthtwin import contract

    place = clinic.header.index("gender")
    header = [name for name in clinic.header if name != "gender"]
    rows = [[cell for at, cell in enumerate(row) if at != place] for row in clinic.rows]
    code, report, _screen = clinic.validate(rows, header=header)
    measured = _write(clinic.folder / "no-gender.csv", header, rows)
    loaded, document = contract.load_profile_document(str(clinic.path))
    outcome = validation.measure(loaded, str(measured), "", document)
    kept = outcome.chain.not_checkable
    from_csv = outcome.census.not_checkable - kept
    assert kept == 1 + len(_holding(clinic, "gender")) and from_csv == len(outcome.listings) > 0
    top = report.split("THE VERDICT", 1)[1].split("WHAT THIS REPORT DOES NOT SAY", 1)[0]
    assert (
        f"A further {outcome.census.not_checkable} obligation(s) are NOT CHECKABLE: {from_csv} from a CSV\n"
        "at all, each listed further down with the reason, and\n"
        f"{kept} between-columns line(s) this file cannot be checked for (a\n"
        "column it lacks, reads under another role, or counts in people),\n"
        "named in the section BETWEEN COLUMNS. They carry no verdict and\n"
        "they are not part of the count above.\n"
    ) in top
    assert "CHECKABLE from a CSV at\nall." not in top
    listed = report.split("WHAT COULD NOT BE CHECKED, AND WHY", 1)[1].split("BETWEEN COLUMNS: THE CHAIN'S", 1)[0]
    assert len(re.findall(r"^  \S.* -- ", listed, re.M)) == from_csv
    assert f"Beside them, {kept} between-columns line(s) counted on the\nsame line of the verdict" in listed
    assert "BETWEEN COLUMNS below." in listed
    code, report, _screen = clinic.validate(clinic.rows)
    top = report.split("THE VERDICT", 1)[1].split("WHAT THIS REPORT DOES NOT SAY", 1)[0]
    assert "CHECKABLE from a CSV at\nall. They carry no verdict, they are not part of the count above,\n" in top
    assert "Beside them," not in report


def test_the_file_s_clock_census_is_its_own_fact_too(tmp_path, monkeypatch):
    """The verify's item 2 on repair 1 (Codex's item 1 on the build, for times
    of day): 4,000 visit times on ten-minute steps, `flag` yes from 11:30
    on, the clock's `L2` edge at its published median 11:30, so `flag |
    visit` confines each half. The file keeps every band total but holds
    five rows at 11:20 and five at 11:30 (the rest moved an hour within
    their bands): its clock census pools them into one group across the
    edge, which leaves 1 to 10 rows on each side of it, an own-fact group
    in a band the family confines, so every family line prints V5.3's
    sentence. With the clock left out of the calendar's columns, both read
    HELD."""
    _home(monkeypatch, tmp_path)

    def hhmm(minutes):
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    low = [360 + 10 * ((row * 33) // 1999) for row in range(1999)]
    high = [690 + 10 * ((row * 39) // 2001) for row in range(2001)]
    rows = [[hhmm(m), "no"] for m in low] + [[hhmm(m), "yes"] for m in high]
    described = Described(tmp_path, ["visit", "flag"], rows)
    assert described.blocks["visit"]["role"] == "time_of_day"
    assert [f["table"] for f in _families(described)] == [[[1999, 2001]], [[0, 1999], [2001, 0]]], _families(described)
    code, report, _screen = described.validate(rows)
    assert code == 0 and set(_verdicts(report)[1].values()) == {"HELD"}
    thinned = []
    kept = {680: 0, 690: 0}
    for text, flag in rows:
        minutes = int(text[:2]) * 60 + int(text[3:])
        if minutes in kept and kept[minutes] >= 5:
            thinned += [[hhmm(minutes - 60 if minutes == 680 else minutes + 60), flag]]
            continue
        if minutes in kept:
            kept[minutes] += 1
        thinned += [[text, flag]]
    code, report, _screen = described.validate(thinned)
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"} and set(families.values()) == {"WITHHELD"}, (totals, families)
    assert validation.CHAIN_GATE_CLOSED in _section(report)
    monkeypatch.setattr(chain_validation, "reads_a_calendar", lambda document: False)
    code, report, _screen = described.validate(thinned)
    assert set(_verdicts(report)[1].values()) == {"HELD"}


def test_each_source_of_the_people_rule_holds_alone(tmp_path):
    """The verify's item 3 on repair 1: the rule that reads a file as counted in
    people has three sources, each pinned alone on `_counted_in_people`:
    the description's declared record numbers (`forced_identifiers`, or
    `person_columns` alone), a column the description reads as record
    numbers, and a column the file's own description alone reads so. A
    written description reads a column as record numbers exactly where its
    settings declare it, and validate's own description of a file is built
    under the description's declarations, so no written file separates
    them (P4-D430); this function's cases do. A column whose values never
    repeat names rows, not people, and fires nothing."""
    from synthtwin import reading

    rows = [[f"{100000 + at // 10}", "x" if at % 3 else "y"] for at in range(200)]
    table = reading.read_table(str(_write(tmp_path / "file.csv", ["id", "a"], rows)), small_cell_floor=FLOOR)
    single = reading.read_table(str(_write(tmp_path / "rows.csv", ["id", "a"], [[f"{100000 + at}", row[1]] for at, row in enumerate(rows)])), small_cell_floor=FLOOR)

    def holder(forced=(), people=(), role="count"):
        return {"settings": {"forced_identifiers": list(forced), "person_columns": list(people)}, "columns": [{"name": "id", "role": role}, {"name": "a", "role": "binary"}]}

    plain = holder()
    counted = chain_validation._counted_in_people
    assert counted(table, plain, plain) is False
    assert counted(table, holder(forced=["id"]), plain) is True
    assert counted(table, holder(people=["id"]), plain) is True
    assert counted(table, holder(role="identifier"), plain) is True
    assert counted(table, plain, holder(forced=["id"], role="identifier")) is True
    assert counted(table, plain, holder(role="identifier")) is True
    assert counted(single, holder(forced=["id"], role="identifier"), holder(forced=["id"], role="identifier")) is False


def test_the_walk_s_held_cells_are_bounded_too(clinic, monkeypatch):
    """The verify's item 4 on repair 1, `IMPLIED_HELD_AT_MOST`: a chain of three
    columns of four bands, each pair of 16 cells (under 1,024), whose walk
    holds 8 joint cells after its second family: under a bound of 5 the
    pair is not worked out, and spends nothing past the bound; under the
    report's bound it is. Through a report, a bound of 1 names every
    implied pair as not worked out, in the words for the work."""
    def ladder(name, bands):
        return chain_rules.Ladder(name, tuple((f"{name}{k}",) for k in range(bands)), (tuple(range(bands)),) * 3, (bands,) * 3, (11,) * bands, (True,) * bands)

    small = {"A": ladder("A", 4), "B": ladder("B", 4), "C": ladder("C", 4)}
    diagonal = (11, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11, 0, 0, 0, 0, 11)
    linked = [chain_rules.Family("A", 0, (), None, (11,) * 4), chain_rules.Family("B", 0, (("A", 0),), 0, diagonal), chain_rules.Family("C", 0, (("B", 0),), 1, diagonal)]
    assert chain_validation.implied_shares(linked, small, "A", "C")[0] == [(1, 4), (0, 1), (0, 1), (0, 1)]
    monkeypatch.setattr(chain_validation, "IMPLIED_HELD_AT_MOST", 5)
    assert chain_validation.implied_shares(linked, small, "A", "C") is None
    monkeypatch.setattr(chain_validation, "IMPLIED_HELD_AT_MOST", 1)
    code, report, _screen = clinic.validate(clinic.rows)
    section = _section(report)
    implied = [entry["columns"] for entry in clinic.statistical["words"] if entry["word"] == "implied"]
    assert implied
    for a, b in implied:
        assert re.search(rf"^  '{a}' and '{b}': implied\n      {re.escape(chain_validation.TOO_MUCH_WORK)}$", section, re.M)


def _we_rows():
    """The three label columns of RULE WE's case: 200, 200 and 25 blank cells, no record holding nothing."""
    draw = random.Random(9)
    rows = []
    for _row in range(3000):
        a = draw.choice(["x", "y"])
        b = ("u" if a == "x" else "v") if draw.random() < 0.8 else draw.choice(["u", "v"])
        rows += [[a, b, draw.choice(["p", "q", "s"])]]
    for at in range(0, 200):
        rows[at][0] = ""
    for at in range(170, 370):
        rows[at][1] = ""
    for at in range(1000, 1025):
        rows[at][2] = ""
    draw.shuffle(rows)
    return rows


def test_rule_we_counts_the_cells_outside_the_ladder_as_room(tmp_path, monkeypatch):
    """The verify's item 4 on repair 1, RULE WE's `P`: RULE WE's case with a
    fourth column outside the ladder (free text, a value on every row). The
    file's 33 records holding nothing leave no room for a row blank in
    every column, but a row blank in every column of the ladder may hold
    a value of the free text, and the file's own description counts 3,000
    such cells: the gate stands open and every family line is judged,
    HELD."""
    import hashlib

    _home(monkeypatch, tmp_path)
    rows = [row + [hashlib.sha256(f"{at}".encode()).hexdigest()[:10]] for at, row in enumerate(_we_rows())]
    header = ["A", "B", "C", "note"]
    described = Described(tmp_path, header, rows)
    assert [entry["column"] for entry in described.statistical["ladder"]] == ["A", "B", "C"]
    (tmp_path / "we").mkdir()
    code, report, _said = _validate_file(described, _write_lines(tmp_path / "we" / "twin.csv", header, rows, 11, 11, 11))
    totals, families = _verdicts(report)
    assert set(totals.values()) == {"HELD"} and set(families.values()) == {"HELD"}, (totals, families)


def test_rule_we_reads_a_column_the_file_lacks_at_its_published_blanks(tmp_path, monkeypatch):
    """The verify's item 4 on repair 1, the published blank count of a column
    that is not checkable: RULE WE's case, the file without `C` and with
    `B`'s blank cells moved off `A`'s (every band total kept), so no row
    of the file is blank in both. Only `C`'s 25 published blank cells,
    read for the column the file lacks, place a row blank in every column
    of the ladder, and with no room left for one every family line not
    holding `C` prints V5.3's sentence; those holding it are NOT
    CHECKABLE."""
    _home(monkeypatch, tmp_path)
    rows = _we_rows()
    header = ["A", "B", "C"]
    described = Described(tmp_path, header, rows)
    both = [at for at in range(len(rows)) if rows[at][0] == "" and rows[at][1] == ""]
    free = [at for at in range(len(rows)) if rows[at][0] != "" and rows[at][1] != ""][: len(both)]
    moved = [list(row) for row in rows]
    for one, other in zip(both, free):
        moved[one][1], moved[other][1] = moved[other][1], moved[one][1]
    assert both and not [row for row in moved if row[0] == "" and row[1] == ""]
    (tmp_path / "we").mkdir()
    code, report, _said = _validate_file(described, _write_lines(tmp_path / "we" / "twin.csv", ["A", "B"], [row[:2] for row in moved], 11, 11, 11))
    totals, families = _verdicts(report)
    assert totals == {"A": "HELD", "B": "HELD", "C": "NOT CHECKABLE"}, totals
    holding = _holding(described, "C")
    assert len(holding) < len(families)
    for at, verdict in families.items():
        assert verdict == ("NOT CHECKABLE" if at in holding else "WITHHELD"), (at, verdict)
    assert validation.CHAIN_GATE_CLOSED in _section(report)
