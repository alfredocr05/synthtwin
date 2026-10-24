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
  byte of the file is read.

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
