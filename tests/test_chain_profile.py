"""The chain's profile side, behind its switch (lane CHa, plan P4-D418; contract 4.6b, NOT IN FORCE).

THE GATE OF LANE CHa. Stage 6's first layer is built, but invariant S12
stands until the landing that ships stage 6 whole: `synthtwin profile`
never turns the chain on, so every shipped description, summary and
twin is byte for byte today's. The chain runs only where a caller hands
`cli.main` (or `chain.describe`) its switch. This file holds:

- SWITCH OFF IS TODAY'S BYTES, and switch on adds the chain alone: the
  switched description is the unswitched one with `statistical` filled;
- a RE-PROFILE reproduces the description byte for byte (one table, one
  name, one key);
- the method page's cases MADE LIVE (`tests/test_chain_method_page.py`
  computed them by hand; here the product decides them): RULE WE on
  Codex's 133-row table, RULE W1 on the red team's part C and in full
  through a derived family, the content hash's framing, the sample of
  equal rows, a step's word before and after one more eligible column
  and across floors, the whole-description digest;
- A RAISE NEVER FORCES: a time-and-event pair and the screen's seeds
  change an option's weight and never which options are eligible;
- the KEY FILE's mode and the LEDGER's refusals and warning, each in
  its `os.name == 'nt'` form too, and the key reaching no output;
- the LOADER's invariants S23 to S28 on a switched description, each
  red on a mutation of it;
- ONE MUTANT RED PER RULE: the floor, W3, NE, W1, WE, the `L0` merge and
  the draw's uniform share, each case computed both ways.

Every fixture is invented here; the key is a fixed test key.
"""

import fractions
import io
import json
import pathlib
import random

import pytest

import fixtures
import workbooks

from synthtwin import (
    chain,
    chain_check,
    chain_rules,
    cli,
    contract,
    errors,
    installation,
    profile,
    reading,
    taxonomy,
)

FLOOR = 11
TEST_KEY = bytes(range(32))


def _csv(header: "list[str]", rows: "list[list[str]]") -> str:
    out = io.StringIO()
    out.write(",".join(header) + "\n")
    for row in rows:
        out.write(",".join(row) + "\n")
    return out.getvalue()


def _clinic(n_rows: int = 800, seed: int = 7) -> str:
    """An invented clinic table: ages, a group, a blood pressure, a follow-up time and its event."""
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for place in range(n_rows):
        age = draw.randint(18, 90)
        sex = draw.choice(["F", "M"])
        group = draw.choice(["a", "b", "c", "d"])
        pressure = "" if draw.random() < 0.05 else f"{round(100 + age * 0.5 + draw.gauss(0, 12), 1)}"
        died = "1" if draw.random() < 0.1 + age / 300 else "0"
        days = f"{draw.randint(1, 400)}"
        rows += [[f"P{place:05d}", f"{age}", sex, group, pressure, days, died]]
    return _csv(["record", "age", "sex", "group", "pressure", "followup_days", "event"], rows)


def _describe(tmp_path: pathlib.Path, text: str, name: str = "clinic", key: bytes = TEST_KEY, floor: int = FLOOR):
    settings = taxonomy.Settings(small_cell_floor=floor)
    tmp_path.mkdir(parents=True, exist_ok=True)
    table_path = fixtures.write(tmp_path, f"{name}.csv", text)
    table = reading.read_table(str(table_path), small_cell_floor=floor)
    document = profile.build_document(table, settings, [], [], [])
    return table, document, settings, chain.describe(table, document, settings, chain.ChainSwitch(name, key))


def _profile(folder: pathlib.Path, table: str, run: "cli.ChainRun | None", capsys) -> "tuple[int, str]":
    capsys.readouterr()
    code = cli.main(["profile", table], chain=run)
    captured = capsys.readouterr()
    return code, captured.out + captured.err


# -- SWITCH OFF IS TODAY'S BYTES; SWITCH ON ADDS THE CHAIN ALONE ----------


def test_switch_off_writes_todays_bytes_and_switch_on_adds_only_the_chain(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    off_folder = tmp_path / "off"
    on_folder = tmp_path / "on"
    off_folder.mkdir()
    on_folder.mkdir()
    text = _clinic()
    fixtures.write(off_folder, "clinic.csv", text)
    fixtures.write(on_folder, "clinic.csv", text)
    monkeypatch.chdir(off_folder)
    code, _said = _profile(off_folder, "clinic.csv", None, capsys)
    assert code == 0
    monkeypatch.chdir(on_folder)
    data = tmp_path / "data"
    code, said = _profile(on_folder, "clinic.csv", cli.ChainRun(folder=str(data)), capsys)
    assert code == 0
    assert "Between columns:" in said
    off = json.loads((off_folder / "clinic-profile.json").read_text(encoding="utf-8"))
    on = json.loads((on_folder / "clinic-profile.json").read_text(encoding="utf-8"))
    assert off["relationships"]["statistical"] is None
    assert on["relationships"]["statistical"] is not None
    on["relationships"]["statistical"] = None
    assert on == off
    # The summary is the same text either way, and no unswitched file names the chain.
    assert (off_folder / "clinic-profile.txt").read_bytes() == (on_folder / "clinic-profile.txt").read_bytes()
    questions_off = json.loads((off_folder / "clinic-questions.json").read_text(encoding="utf-8"))
    questions_on = json.loads((on_folder / "clinic-questions.json").read_text(encoding="utf-8"))
    assert "between_columns" not in questions_off
    assert questions_on["between_columns"]["add"] == [] and questions_on["between_columns"]["drop"] == []
    del questions_on["between_columns"]
    assert questions_on == questions_off
    # The unswitched run made no key, no record and no lock anywhere.
    assert not (off_folder / "data").exists()
    # And generate and validate keep S12 word for word: the switched description is refused.
    with pytest.raises(errors.ProfileError) as refused:
        contract.load_profile(str(on_folder / "clinic-profile.json"))
    assert "statistical" in str(refused.value)


def test_a_re_profile_reproduces_the_description_byte_for_byte(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    fixtures.write(tmp_path, "clinic.csv", _clinic())
    run = cli.ChainRun(folder=str(tmp_path / "data"))
    assert _profile(tmp_path, "clinic.csv", run, capsys)[0] == 0
    first = (tmp_path / "clinic-profile.json").read_bytes()
    assert _profile(tmp_path, "clinic.csv", run, capsys)[0] == 0
    assert (tmp_path / "clinic-profile.json").read_bytes() == first
    loaded = contract.load_profile(str(tmp_path / "clinic-profile.json"), chain=True)
    assert loaded.n_rows == 800


def test_the_key_reaches_no_output(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    fixtures.write(tmp_path, "clinic.csv", _clinic())
    data = tmp_path / "data"
    code, said = _profile(tmp_path, "clinic.csv", cli.ChainRun(folder=str(data)), capsys)
    assert code == 0
    key = (data / installation.KEY_FILE).read_bytes()
    assert len(key) == 32
    hex_key = "".join(f"{byte:02x}" for byte in key)
    for output in ("clinic-profile.json", "clinic-profile.txt", "clinic-questions.json"):
        body = (tmp_path / output).read_bytes()
        assert key not in body and hex_key.encode("ascii") not in body
    assert hex_key not in said
    ledger = (data / installation.LEDGER_FILE).read_text(encoding="utf-8")
    assert hex_key not in ledger and installation.fingerprint(key) in ledger


# -- THE LEDGER: ONE DESCRIPTION PER TABLE AND NAME (4.6b.4) --------------


def test_the_ledger_refuses_a_second_name_and_warns_on_a_name_reused(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    fixtures.write(tmp_path, "clinic.csv", _clinic())
    fixtures.write(tmp_path, "other.csv", _clinic(seed=8))
    data = str(tmp_path / "data")
    assert _profile(tmp_path, "clinic.csv", cli.ChainRun(folder=data), capsys)[0] == 0
    code, said = _profile(tmp_path, "clinic.csv", cli.ChainRun(name="renamed", folder=data), capsys)
    assert code == 1
    assert "described before under the name 'clinic'" in said and "--name clinic" in said
    code, said = _profile(tmp_path, "other.csv", cli.ChainRun(name="clinic", folder=data), capsys)
    assert code == 0
    assert "A different table was described before under the name 'clinic'" in said


@pytest.mark.parametrize("os_name", ["posix", "nt"])
def test_the_ledger_decides_each_case_in_both_forms(tmp_path, os_name):
    folder = installation.data_folder(
        os_name=os_name,
        environ={"LOCALAPPDATA": str(tmp_path / "local"), "XDG_DATA_HOME": str(tmp_path / "xdg")},
        home=str(tmp_path),
        platform="linux",
    )
    if os_name == "nt":
        assert folder == pathlib.Path(tmp_path / "local", "synthtwin")
    else:
        assert folder == pathlib.Path(tmp_path / "xdg", "synthtwin")
    opened = installation.open_installation(folder, os_name=os_name)
    assert not opened.refusal and len(opened.key) == 32
    assert any("A new private key was made" in line for line in opened.lines)
    entry = installation.Entry("clinic", "c1", installation.fingerprint(opened.key), "d1", True)
    installation.record(opened, entry)
    installation.release(opened)
    again = installation.open_installation(folder, os_name=os_name)
    assert again.key == opened.key and again.entries == (entry,)
    decide = installation.decide
    assert decide(again, "clinic", "c1", "d1", True).verdict == installation.PROCEED
    changed = decide(again, "clinic", "c1", "d2", True)
    assert changed.verdict == installation.REFUSE and "--replace-description" in changed.words
    assert decide(again, "clinic", "c1", "d2", True, replace=True).verdict == installation.PROCEED
    other_name = decide(again, "renamed", "c1", "d1", True)
    assert other_name.verdict == installation.REFUSE and "--name clinic" in other_name.words
    reused = decide(again, "clinic", "c2", "d3", True)
    assert reused.verdict == installation.WARN
    other_key = installation.Opened(again.folder, bytes(32), again.entries, (), "", False)
    assert decide(other_key, "clinic", "c1", "d1", True).verdict == installation.REFUSE
    # Two descriptions that both publish nothing between columns are the base product's.
    plain = installation.Opened(again.folder, again.key, (installation.Entry("t", "c9", entry.fingerprint, "d8", False),), (), "", False)
    assert decide(plain, "t", "c9", "d9", False).verdict == installation.PROCEED
    # One run at a time: a second open finds the lock the first holds.
    blocked = installation.open_installation(folder, os_name=os_name)
    assert "Another synthtwin profile is running" in blocked.refusal
    installation.release(blocked)
    assert (folder / installation.LOCK_FILE).exists()
    installation.release(again)
    assert not (folder / installation.LOCK_FILE).exists()
    # A ledger without its key is refused before anything is read.
    installation.key_path(folder).unlink()
    missing = installation.open_installation(folder, os_name=os_name)
    assert "is missing, but this installation has described tables before" in missing.refusal
    installation.release(missing)
    renewed = installation.open_installation(folder, new_key=True, os_name=os_name)
    assert not renewed.refusal and renewed.key != opened.key
    installation.release(renewed)
    # A damaged ledger is refused.
    (folder / installation.LEDGER_FILE).write_text("{", encoding="utf-8", newline="\n")
    damaged = installation.open_installation(folder, os_name=os_name)
    assert "cannot be read" in damaged.refusal
    installation.release(damaged)


def test_a_key_file_others_can_read_is_refused_on_posix(tmp_path):
    folder = tmp_path / "data"
    opened = installation.open_installation(folder, os_name="posix")
    installation.release(opened)
    key_file = installation.key_path(folder)
    assert key_file.stat().st_mode & 0o777 == 0o600
    assert folder.stat().st_mode & 0o777 == 0o700
    key_file.chmod(0o644)
    refused = installation.open_installation(folder, os_name="posix")
    assert "can be read or changed by other accounts" in refused.refusal
    installation.release(refused)
    # The nt form reads no POSIX mode: the folder is the user's own local data.
    accepted = installation.open_installation(folder, os_name="nt")
    assert not accepted.refusal
    installation.release(accepted)


def test_the_digest_reads_the_whole_description_less_its_stamp():
    statistical = {"chain": []}
    at_11 = {"settings": {"small_cell_floor": 11}, "columns": [{"x": 1}], "relationships": {"statistical": statistical}, "created_with": "1"}
    at_12 = {"settings": {"small_cell_floor": 12}, "columns": [{"x": 2}], "relationships": {"statistical": statistical}, "created_with": "1"}
    newer = dict(at_11)
    newer["created_with"] = "2"
    assert installation.description_digest(at_11) != installation.description_digest(at_12)
    assert installation.description_digest(at_11) == installation.description_digest(newer)
    assert installation.publishes_between(at_11)
    assert not installation.publishes_between({"relationships": {"statistical": None}})


# -- THE CONTENT HASH AND THE SAMPLE (4.6b.8) -----------------------------


def _hashes(tmp_path: pathlib.Path, name: str, text: str) -> "list[bytes]":
    table = reading.read_table(str(fixtures.write(tmp_path, name, text)), small_cell_floor=FLOOR)
    return chain.row_hashes(table)[0]


def test_framing_keeps_two_rows_apart_that_separator_bytes_join(tmp_path):
    first = _hashes(tmp_path, "a.csv", '"A","B"\n"x\x1eB\x1fy","z"\n')
    second = _hashes(tmp_path, "b.csv", '"A","B"\n"x","y\x1eB\x1fz"\n')
    assert first != second


def test_the_content_hash_is_free_of_row_and_column_order_and_reads_names(tmp_path):
    rows = [[f"{place}", f"{place % 3}"] for place in range(50)]
    base = chain.content_hash(_hashes(tmp_path, "a.csv", _csv(["a", "b"], rows)))
    shuffled = rows[25:] + rows[:25]
    assert chain.content_hash(_hashes(tmp_path, "b.csv", _csv(["a", "b"], shuffled))) == base
    swapped = [[row[1], row[0]] for row in rows]
    assert chain.content_hash(_hashes(tmp_path, "c.csv", _csv(["b", "a"], swapped))) == base
    assert chain.content_hash(_hashes(tmp_path, "d.csv", _csv(["a", "renamed"], rows))) != base


def test_a_workbook_and_a_csv_of_one_table_give_one_hash(tmp_path):
    book = tmp_path / "book.xlsx"
    book.write_bytes(workbooks.plain_book(40))
    from_book = reading.read_table(str(book), small_cell_floor=FLOOR)
    names = list(from_book.column_names)
    columns = [reading.column_values(from_book, place) for place in range(len(names))]
    rows = [[columns[place][row] for place in range(len(names))] for row in range(from_book.n_rows)]
    from_text = _hashes(tmp_path, "book.csv", _csv(names, rows))
    assert chain.content_hash(chain.row_hashes(from_book)[0]) == chain.content_hash(from_text)


def test_the_sample_takes_exactly_its_rows_however_many_repeat():
    first = bytes(32)
    second = bytes([1] * 32)
    hashes = [first] * 2000 + [second] * 2000
    taken = chain.sample_rows(hashes, list(range(4000)), 400)
    assert len(taken) == 400 and len(set(taken)) == 400
    share = len([at for at in taken if at < 2000])
    assert 150 < share < 250
    assert len(chain.sample_rows(hashes, list(range(4000)), 10000)) == 4000


# -- THE DRAW'S WORDS AND ITS CHOICE (4.6b.4) -----------------------------


def test_one_more_eligible_column_changes_every_word_and_a_floor_none():
    before = ["age", "group", "stay", "died"]
    after = ["age", "group", "record_answered", "stay", "died"]
    same = sum(
        chain.step_word(TEST_KEY, "clinic", "place", step, before)
        == chain.step_word(TEST_KEY, "clinic", "place", step, after)
        for step in range(40)
    )
    assert same == 0
    # The floor is no input of a word.
    assert chain.step_word(TEST_KEY, "clinic", "place", 3, before) == chain.step_word(TEST_KEY, "clinic", "place", 3, list(before))
    # Another name, other words.
    assert chain.step_word(TEST_KEY, "other", "place", 3, before) != chain.step_word(TEST_KEY, "clinic", "place", 3, before)


def test_the_stated_exponential_is_the_polynomial_the_page_states():
    assert chain_rules.stated_exponential(0.0) == 1.0
    assert chain_rules.stated_exponential(5000.0) == 0.0
    for y in (0.5, 1.0, 2.0, 10.0, 30.0, 700.0):
        exact = fractions.Fraction(1)
        term = fractions.Fraction(1)
        for k in range(1, 200):
            term = term * fractions.Fraction(-y) / k
            exact += term
        if y <= 30.0:
            # The stated polynomial is deterministic, not correctly rounded: its
            # degree-13 remainder stays under 1e-13 of the value.
            assert abs(chain_rules.stated_exponential(y) - float(exact)) <= 1e-13 * float(exact)
    assert chain_rules.TAYLOR[0] == 1.0 and chain_rules.TAYLOR[1] == -0.6931471805599453


def test_the_uniform_share_reaches_an_option_of_no_weight():
    """A word whose top 30 bits are clear places the option at (U2 * m) >> 64 whatever the weights.

    Mutant: the weighted choice alone, which never places an option of
    weight 0.0."""
    weights = [1.0, 0.0, 0.0, 0.0]
    word = bytes(4) + bytes([3]) + bytes(3) + bytes([0xC0]) + bytes(7)
    assert chain_rules.choose(word, weights) == 3
    weighted = bytes([255]) + bytes(7) + bytes([0xC0]) + bytes(7)
    assert chain_rules.choose(weighted, weights) == 0


# -- THE METHOD PAGE'S CASES, MADE LIVE ------------------------------------


def _codex_census_table() -> str:
    """Codex's 133 rows: three presence columns, 33 records holding nothing (11 each place)."""
    cells = {"000": 0, "001": 22, "100": 22, "101": 6, "010": 11, "011": 11, "110": 11, "111": 17}
    rows: "list[list[str]]" = []
    for code in ("000", "001", "010", "011", "100", "101", "110", "111"):
        for _copy in range(cells[code]):
            rows += [["1" if code[0] == "1" else "", "1" if code[1] == "1" else "", "1" if code[2] == "1" else ""]]
    empty = [["", "", ""]] * 11
    return _csv(["a", "b", "c"], empty + rows[:50] + empty + rows[50:] + empty)


def test_rule_we_refuses_every_root_pair_on_codexs_census_table(tmp_path, monkeypatch):
    """Codex's item 1, decided by the product: the census of records holding nothing leaves no
    tabled row blank in all three columns, so every root pair whose cell bound at the blank cell
    exceeds `Z + P` (here 0) is refused, and no chain is published. Mutant: no RULE WE."""
    _table, document, _settings, chained = _describe(tmp_path, _codex_census_table(), name="census")
    assert chain_rules.records_holding_nothing(document) == 33
    assert chained.statistical is None
    assert chained.counts["we_refusals"] > 0
    monkeypatch.setattr(chain_rules, "blank_record_room", lambda _document, _floor: 10**9)
    _table, _document, _settings, mutant = _describe(tmp_path / "m", _codex_census_table(), name="census")
    assert mutant.counts["we_refusals"] == 0


def _scale(column: str, totals: "list[int]", l1: "list[int]", l2: "list[int]") -> chain_rules.Ladder:
    names = tuple(((f"b{at}",),) for at in range(len(totals)))
    return chain_rules.Ladder(
        column,
        names,
        (tuple(range(len(totals))), tuple(l1), tuple(l2)),
        (len(totals), max(l1) + 1, max(l2) + 1),
        tuple(totals),
        tuple(True for _total in totals),
    )


def test_w1_in_full_refuses_a_confinement_through_a_derived_family():
    """Codex's item 2 on 100 rows, decided by `w1_refusals`: C's first band (its six absent cells
    merged in, a group) admits A at 0 and 2, two bands of A's L2, so the pairs holding A pass; but
    the family {D | A} sends both to D's first band, so "the six AND D below 15" is fixed at 6.
    The chain is written as a junction tree with D's family last, the same published zeros.
    Mutant: the shortcut reading only the pairs holding A, which passes."""
    scales = {
        "c": _scale("c", [50, 50], [0, 1], [0, 1]),
        "a": _scale("a", [25, 25, 25, 25], [0, 1, 2, 3], [0, 0, 1, 1]),
        "d": _scale("d", [50, 50], [0, 1], [0, 1]),
    }
    chain_of = [
        chain_rules.Family("c", 0, (), None, (50, 50)),
        chain_rules.Family("a", 0, (("c", 0),), 0, (25, 0, 25, 0, 0, 25, 0, 25)),
        chain_rules.Family("d", 0, (("a", 0),), 1, (25, 0, 0, 25, 25, 0, 0, 25)),
    ]
    groups = {"c": {0}}
    assert ("c", 0, "d") in chain_rules.w1_refusals(chain_of, scales, groups)
    assert chain_rules.w1_refusals(chain_of[:2], scales, groups) == []


def test_w1_refuses_the_red_teams_part_c_and_its_mutant_passes():
    """The red team's part C: `n_zero` 6 inside a band of 25 rows reading post-op (25, 0) fixes
    "day 0 AND post-op 0" at 6. W1 refuses the family; the design's own clause read at L0 beside
    an L0-cut parent whose two cells share one L2 band (case 1 of 4.6b.9 (c)) passes."""
    scales = {
        "day": _scale("day", [25, 75], [0, 1], [0, 1]),
        "post": _scale("post", [50, 50], [0, 1], [0, 1]),
    }
    families = [
        chain_rules.Family("day", 0, (), None, (25, 75)),
        chain_rules.Family("post", 0, (("day", 0),), 0, (25, 0, 25, 50)),
    ]
    assert ("day", 0, "post") in chain_rules.w1_refusals(families, scales, {"day": {0}})
    # Case 1: a parent cut at L0 whose two non-zero cells beside the band lie below its median.
    scales["dose"] = _scale("dose", [25, 25, 25, 25], [0, 1, 2, 3], [0, 0, 1, 1])
    case_one = [
        chain_rules.Family("day", 0, (), None, (25, 75)),
        chain_rules.Family("dose", 0, (("day", 0),), 0, (12, 13, 0, 0, 13, 12, 25, 25)),
    ]
    design_clause = len([cell for cell in case_one[1].table[0:4] if cell]) >= 2
    assert design_clause
    assert ("day", 0, "dose") in chain_rules.w1_refusals(case_one, scales, {"day": {0}})


def test_the_fast_check_agrees_with_the_full_check_on_every_option(tmp_path, monkeypatch):
    """`chain._w1_holds` reads only the pairs holding a new child (adding a family whose child is
    new never narrows an earlier support, S25). On random small tables, for every option a search
    weighs, the fast answer equals `w1_refusals` read in full over the chain with the option placed.
    Mutant: a fast check that reads nothing, which passes options the full check refuses."""
    original = chain._w1_holds
    asked = [0, 0]

    def both(search, clamps, anchor_at, anchor, child, parents, levels, table):
        fast = original(search, clamps, anchor_at, anchor, child, parents, levels, table)
        parent_rows = tuple((parents[at], levels[at + 1]) for at in range(len(parents)))
        if anchor is None:
            parent = parents[0]
            totals = tuple(chain_rules.totals_at(search.scales[parent], levels[1]))
            placed = [
                chain_rules.Family(parent, levels[1], (), None, totals),
                chain_rules.Family(child, levels[0], parent_rows, 0, table),
            ]
        else:
            placed = list(clamps.support.families) + [
                chain_rules.Family(child, levels[0], parent_rows, anchor_at, table)
            ]
        groups = {family.child: set(search.columns[family.child].groups) for family in placed}
        full = chain_rules.w1_refusals(placed, search.scales, groups) == []
        assert fast == full
        asked[0] += 1
        asked[1] += 0 if full else 1
        return fast

    monkeypatch.setattr(chain, "_w1_holds", both)
    for seed in range(3):
        draw = random.Random(seed)
        rows = []
        for _place in range(1500):
            a = draw.randint(0, 40)
            b = a + draw.randint(0, 10) if draw.random() < 0.7 else draw.randint(0, 60)
            c = draw.choice(["x", "y", "z"]) if a < 30 else "x"
            # z holds exactly seven zeros, a small group in its lowest band, and w
            # reads one level all through that band: a confinement W1 refuses.
            z = 0 if _place < 7 else draw.randint(1, 100)
            w = "u" if z < 10 else draw.choice(["u", "v"])
            rows += [[f"{a}", f"{b}", c, f"{z}", w]]
        _describe(tmp_path / f"s{seed}", _csv(["a", "b", "c", "z", "w"], rows), name=f"w{seed}")
    assert asked[0] > 50
    assert asked[1] > 0


def test_a_raise_never_forces_an_option(tmp_path, monkeypatch):
    """Time-and-event pairs and the screen's seeds change weights only: the root step offers the
    same eligible options, in the same order, with and without them (4.6b.3), and only scores move.
    Mutant: a raise that drops options below a weight, which changes the list."""
    text = _clinic(600)
    seen: "list[list[tuple[str, tuple[str, ...], tuple[int, ...], fractions.Fraction]]]" = []
    original = chain._root_options

    def recording(search, x0, room):
        options = original(search, x0, room)
        seen.append([(option.child, option.parents, option.levels, option.score) for option in options])
        return options

    monkeypatch.setattr(chain, "_root_options", recording)
    _describe(tmp_path / "with", text)
    monkeypatch.setattr(chain, "time_event_pairs", lambda _blocks, _eligible: frozenset())
    monkeypatch.setattr(chain, "screen_seeds", lambda _columns: ())
    _describe(tmp_path / "without", text)
    raised, plain = seen
    assert [entry[:3] for entry in raised] == [entry[:3] for entry in plain]
    assert any(first[3] != second[3] for first, second in zip(raised, plain))


def test_a_time_and_event_pair_is_read_from_roles_and_names():
    blocks = [
        {"name": "followup_days", "role": "count"},
        {"name": "event", "role": "binary"},
        {"name": "age", "role": "count"},
        {"name": "sex", "role": "binary"},
    ]
    pairs = chain.time_event_pairs(blocks, ["followup_days", "event", "age", "sex"])
    assert pairs == frozenset({("followup_days", "event"), ("event", "followup_days")})


# -- ONE MUTANT RED PER RULE ------------------------------------------------


def test_rule_w3_coarsens_a_member_that_fails_the_product_of_the_others():
    """A child of 4 bands of 30 beside a parent of 4: 30 < 11 x 4, so the child goes coarser.
    Mutant: no W3, which offers L0 and so a table with cells under the floor."""
    child = _scale("child", [30, 30, 30, 30], [0, 1, 2, 3], [0, 0, 1, 1])
    parent = _scale("parent", [30, 30, 30, 30], [0, 0, 1, 1], [0, 0, 1, 1])
    margins = chain_rules.parent_cells({"parent": parent}, ("parent",), None)
    offered = chain_rules.offered_levels([child, parent], [0, 0], [1, 0], margins, 120, FLOOR)
    assert offered is not None and offered != [0, 0]
    assert offered[0] >= 1 or offered[1] >= 1


def test_rule_ne_coarsens_until_every_expected_cell_reaches_the_floor_and_one():
    """Two columns of 30 and 970 rows in 1,000: W3 holds (30 >= 11 x 2), but the expected cell
    30 x 30 / 1,000 is under 12, so NE coarsens the parent (ties to the earlier in schema order)
    until it holds. Mutant: no NE, which offers both at L0."""
    child = _scale("child", [30, 970], [0, 1], [0, 1])
    parent = _scale("parent", [30, 970], [0, 1], [0, 0])
    margins = chain_rules.parent_cells({"parent": parent}, ("parent",), None)
    offered = chain_rules.offered_levels([child, parent], [0, 0], [1, 0], margins, 1000, FLOOR)
    assert offered == [0, 2]


def test_the_floor_refuses_a_table_with_a_cell_of_one_to_ten():
    assert chain._floored((0, 11, 25), FLOOR)
    assert not chain._floored((0, 10, 25), FLOOR)


def test_the_l0_merge_leaves_every_total_nought_or_at_least_the_floor():
    """A number column's bands of 40, 5, 40, 0 and 30: the empty band joins its neighbour and the
    band of 5 joins its smaller neighbour. Mutant: no merge, which prints 5."""
    start = chain_rules.Starting(
        ("missing", (None, "p10"), ("p10", "p50"), ("p50", "p75"), ("p75", None)),
        ((-3, 0, 1, 2, 3), (-3, 0, 0, 1, 2), (-3, 0, 0, 1, 1)),
        (False, True, True, True, True),
        False,
        (1.0, 5.0, 7.0),
    )
    merged = chain_rules.merge_ladder("x", start, [40, 5, 40, 0, 30], FLOOR)
    assert merged is not None
    assert all(total == 0 or total >= FLOOR for total in merged.totals)
    assert sum(merged.totals) == 115
    assert 5 not in merged.totals


def test_the_score_is_pearsons_chi_square_less_its_degrees_of_freedom():
    table = [30, 10, 10, 30]
    expected = 4 * (10 * 10) / 20  # each (O - E)^2 / E with E = 20
    assert chain_rules.score(table, 2, 2) == fractions.Fraction(int(expected)) - 1
    assert chain_rules.score([20, 20, 20, 20], 2, 2) == -1


# -- THE LOADER'S INVARIANTS S23 TO S28 ------------------------------------


def _switched_document(tmp_path: pathlib.Path) -> "dict[str, object]":
    _table, document, _settings, chained = _describe(tmp_path, _clinic())
    assert chained.statistical is not None
    written = dict(document)
    relationships = dict(written["relationships"])
    relationships["statistical"] = chained.statistical
    written["relationships"] = relationships
    return written


def test_the_loader_accepts_the_chain_and_refuses_each_mutation(tmp_path):
    document = _switched_document(tmp_path)
    chain_check.check(document)
    statistical = document["relationships"]["statistical"]

    def refused(change) -> str:
        mutated = json.loads(json.dumps(document))
        change(mutated["relationships"]["statistical"])
        with pytest.raises(errors.ProfileError) as caught:
            chain_check.check(mutated)
        return str(caught.value)

    def small_cell(st):
        for family in st["chain"]:
            for row in family["table"]:
                for at in range(len(row)):
                    if row[at] >= FLOOR + 2:
                        row[at] = 5
                        return

    assert "S25" in refused(small_cell)
    assert "S23" in refused(lambda st: st["ladder"][0]["totals"].__setitem__(0, st["ladder"][0]["totals"][0] + 1))
    assert "S27" in refused(lambda st: st["words"].reverse())
    assert "S28" in refused(lambda st: st["rules"].append({"kind": "order"}))
    assert "S26" in refused(lambda st: st["chain"][1].__setitem__("slopes", {"parents": [], "sigma": 0}))
    assert "S24" in refused(lambda st: st["procedure"].__setitem__("k_max", 4))
    assert statistical["moments"] is None and statistical["rules"] == []


def test_the_loader_reads_the_chain_only_behind_its_switch(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    fixtures.write(tmp_path, "clinic.csv", _clinic())
    assert _profile(tmp_path, "clinic.csv", cli.ChainRun(folder=str(tmp_path / "data")), capsys)[0] == 0
    described = str(tmp_path / "clinic-profile.json")
    assert contract.load_profile(described, chain=True).n_columns == 7
    with pytest.raises(errors.ProfileError):
        contract.load_profile(described)


# -- WHAT A SWITCHED DESCRIPTION PUBLISHES ---------------------------------


def test_every_published_count_is_nought_or_at_least_the_floor(tmp_path):
    _table, document, _settings, chained = _describe(tmp_path, _clinic())
    statistical = chained.statistical
    assert statistical is not None
    for entry in statistical["ladder"]:
        assert all(total == 0 or total >= FLOOR for total in entry["totals"])
    for family in statistical["chain"]:
        assert family["slopes"] is None
        for row in family["table"]:
            assert all(cell == 0 or cell >= FLOOR for cell in row)
    assert statistical["moments"] is None and statistical["withheld"] == [] and statistical["rules"] == []
    assert statistical["procedure"] == chain_rules.procedure_record(800)


def test_a_table_of_several_rows_per_person_gets_no_chain(tmp_path):
    rows = [[f"P{place // 3:04d}", f"{place % 50}", "a" if place % 2 else "b"] for place in range(600)]
    settings = taxonomy.Settings()
    table_path = fixtures.write(tmp_path, "visits.csv", _csv(["person", "value", "kind"], rows))
    table = reading.read_table(str(table_path), small_cell_floor=FLOOR)
    document = profile.build_document(table, settings, ["person"], [], [])
    chained = chain.describe(table, document, settings, chain.ChainSwitch("visits", TEST_KEY))
    assert chained.statistical is None
    assert any("several rows per person" in note for note in chained.notes)
