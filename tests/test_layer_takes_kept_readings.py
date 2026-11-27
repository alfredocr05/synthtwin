"""The patient layer takes the description's kept readings (lane SCALE; lane CHs, plan P4-D462).

`profile.build_document` keeps, column by column, its own reading of each
column as the chain reads it (`taxonomy.KeptSpellings`), so the chain does
not run taxonomy's whole decision over a column a second time. On a table
naming a person the chain is the patient layer, and the kept readings were
let go before the layer ran (batch 4q's merge): the layer read every one
of its row columns again (`taxonomy.spellings_read` -> `_read_the_column`),
about a tenth of a description round at 100,000 rows by 50 columns and a
fifth of a round of answers (lane SCALE's ladder). These cases hold: the
layer handed the kept readings writes the same chain, `grain` and column
blocks, byte for byte, as the layer handed none; it reads no row column
again where the description kept its reading; and every kept reading is
let go by the end of the chain.
"""

import dataclasses
import json
import random

import pytest

from synthtwin import chain, profile, reading, taxonomy

import fixtures

FLOOR = 11
TEST_KEY = bytes(range(32))


def _visits(patients: int, seed: int, oldest: int = 80, pooled: bool = False) -> "tuple[list[str], list[list[str]]]":
    """An invented visit table: an arm, a gender, an age (to ``oldest``), a visit date, a reading with a trend, a site.

    With ``pooled``, a `dose` column more, of 40 to 80 on every row but five rows of 99: top-coded at 90, its top
    category is held by fewer rows than the floor and pooled into the value below it.
    """
    draw = random.Random(seed)
    rows: "list[list[str]]" = []
    for patient in range(patients):
        arm = draw.choice(["a", "b"])
        gender = draw.choice(["F", "M"])
        age = draw.randint(30, oldest)
        visits = draw.randint(1, 8)
        base = draw.gauss(100, 12)
        slope = 1.5 if arm == "b" else 0.3
        for j in range(visits):
            day = 1 + 30 * j + draw.randint(0, 5)
            date = f"{2024 + day // 336}-{1 + (day // 28) % 12:02d}-{1 + day % 28:02d}"
            rows += [[f"S{patient:05d}", arm, gender, f"{age}", date, f"{base + slope * j + draw.gauss(0, 6):.1f}",
                      draw.choice(["clinic", "home", "phone"]), f"{min(oldest, max(40, age - 10 + j * 3 + draw.randint(-5, 5)))}"]]
    header = ["pid", "arm", "gender", "age", "visit_date", "value", "site", "score"]
    if pooled:
        header = header + ["dose"]
        rows = [row + ["99" if at % 1000 == 7 and at < 5000 else f"{40 + (at * 37) % 41}"] for at, row in enumerate(rows)]
    return header, rows


def _layered(tmp_path, keep: bool, watch: "list[str] | None" = None, top_code: bool = False,
             persons: "tuple[str, ...]" = ("pid",), pooled: bool = False):
    """The table described with its kept readings (``keep``), then its chain; the names of the columns read again.

    With ``top_code`` the ages run to 99 and the description top-codes them (every age past 89 read as 90), so
    the layer reads the age column on cells the description changed, where the kept reading of the file's own
    spellings may not be taken.
    """
    header, rows = _visits(1500, 7, 99 if top_code else 80, pooled)
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(tmp_path, "visits.csv", ",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows))
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=persons)
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    kept: "dict[int, taxonomy.KeptSpellings] | None" = {} if keep else None
    document = profile.build_document(table, settings, list(persons), [], [], subjects=list(persons), kept_spellings=kept,
                                      top_code=top_code)
    handed = sorted(kept) if kept is not None else []
    real_read = taxonomy._read_the_column
    real_spellings = taxonomy.spellings_read
    now = {"name": ""}

    def naming(values, name, *arguments, **keywords):  # type: ignore[no-untyped-def]
        # ...a column read again is one `spellings_read` reads through `_read_the_column` (the patient table the
        # layer describes is read by `build_document`, not here).
        # ...of the row table alone: the patient table, one row a patient, is another table, read on its own.
        now["name"] = name if len(values) == table.n_rows else ""
        try:
            return real_spellings(values, name, *arguments, **keywords)
        finally:
            now["name"] = ""

    def counting(*arguments, **keywords):  # type: ignore[no-untyped-def]
        if watch is not None and now["name"]:
            watch.append(now["name"])
        return real_read(*arguments, **keywords)

    taxonomy.spellings_read = naming
    taxonomy._read_the_column = counting
    try:
        chained = chain.describe(table, document, settings,
                                 chain.ChainSwitch("visits", TEST_KEY, (), rows_per_person=chain.ROWS_PERSON,
                                                   trajectories=False),
                                 kept=kept)
    finally:
        taxonomy.spellings_read = real_spellings
        taxonomy._read_the_column = real_read
    return chained, handed, kept


def _bytes(chained: chain.Chained) -> str:
    return json.dumps([chained.statistical, chained.grain, chained.columns], sort_keys=True, default=str)


@pytest.mark.parametrize("top_code", [False, True])
def test_the_layer_handed_the_kept_readings_is_the_layer_handed_none_byte_for_byte(tmp_path, top_code):
    taken, handed, _kept = _layered(tmp_path / "taken", True, top_code=top_code)
    alone, _none, _kept_none = _layered(tmp_path / "alone", False, top_code=top_code)
    assert taken.grain is not None and handed
    assert _bytes(taken) == _bytes(alone)


def test_the_layer_reads_no_row_column_again_where_the_description_kept_its_reading(tmp_path):
    again: "list[str]" = []
    chained, handed, _kept = _layered(tmp_path / "taken", True, again)
    assert chained.grain is not None
    names = ["pid", "arm", "gender", "age", "visit_date", "value", "site", "score"]
    kept_names = [names[place] for place in handed]
    assert kept_names, "the description keeps readings for the chain"
    assert not set(again) & set(kept_names), again
    without: "list[str]" = []
    _layered(tmp_path / "alone", False, without)
    assert set(kept_names) <= set(without), without


def test_every_kept_reading_is_let_go_by_the_end_of_the_chain(tmp_path):
    _chained, handed, kept = _layered(tmp_path / "taken", True)
    assert handed and kept == {}


def test_every_kept_reading_is_let_go_where_the_layer_stops_before_its_columns(tmp_path):
    """Two person columns turn the layer off at its gate, before any column is read: the chain lets go of every reading."""
    chained, handed, kept = _layered(tmp_path / "two", True, persons=("pid", "site"))
    assert chained.grain is None and handed and kept == {}


def test_a_column_whose_cells_the_description_changed_is_read_again_on_those_cells(tmp_path):
    """`value` runs past 89 and is top-coded at 90 by the description: its kept reading is of the file's spellings,
    so the layer reads it again on the cells as described, as `chain.read_as_described` does, and never with it."""
    again: "list[str]" = []
    chained, handed, _kept = _layered(tmp_path / "coded", True, again, top_code=True)
    assert chained.grain is not None and 3 + 2 in handed
    # ...twice: for its recount (`chain.read_as_described`) and for its readings, each on the cells as described.
    assert again.count("value") == 2, again
    assert "site" not in again and "score" not in again, again


# -- validate's chain lines take the measured file's own readings (lane SCALE) ---------------------------------------


def _lines(tmp_path, keep: bool, watch: "list[str] | None" = None, layer: bool = True):
    """The chain's lines of the visits table against its own switched description, with or without its kept readings.

    ``layer``: the patient layer's lines (`grain` standing); otherwise the table's chain of a table of independent
    rows, the person column left out.
    """
    from synthtwin import chain_validation

    tmp_path.mkdir(parents=True, exist_ok=True)
    if layer:
        chained, _handed, _kept = _layered(tmp_path / "described", False)
        path = tmp_path / "described" / "visits.csv"
        persons: "list[str]" = ["pid"]
    else:
        header, rows = _visits(1500, 9)
        path = fixtures.write(tmp_path, "rows.csv", ",".join(header[1:]) + "\n"
                              + "".join(",".join(row[1:]) + "\n" for row in rows))
        persons = []
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=tuple(persons))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    plain = profile.build_document(table, settings, list(persons), [], [], subjects=list(persons))
    if not layer:
        chained = chain.describe(table, plain, settings, chain.ChainSwitch("rows", TEST_KEY, (), rows_per_person=chain.ROWS_ONE,
                                                                          trajectories=False))
        assert chained.statistical is not None and chained.grain is None
    switched = json.loads(json.dumps(chain.with_rules(plain, chained)))
    if chained.grain is not None:
        switched["relationships"]["grain"] = chained.grain
    if chained.columns is not None:
        switched["columns"] = chained.columns
    kept: "dict[int, taxonomy.KeptSpellings] | None" = {} if keep else None
    redescribed = profile.build_document(table, settings, list(persons), [], [], subjects=list(persons),
                                         kept_spellings=kept)
    real_read = taxonomy._read_the_column
    real_spellings = taxonomy.spellings_read
    now = {"name": ""}

    def naming(values, name, *arguments, **keywords):  # type: ignore[no-untyped-def]
        now["name"] = name if len(values) == table.n_rows else ""
        try:
            return real_spellings(values, name, *arguments, **keywords)
        finally:
            now["name"] = ""

    def counting(*arguments, **keywords):  # type: ignore[no-untyped-def]
        if watch is not None and now["name"]:
            watch.append(now["name"])
        return real_read(*arguments, **keywords)

    taxonomy.spellings_read = naming
    taxonomy._read_the_column = counting
    try:
        lines = chain_validation.lines_of(switched, table, redescribed, settings, list(persons), [], [],
                                          profile.stored_as_of(table, settings), kept)
    finally:
        taxonomy.spellings_read = real_spellings
        taxonomy._read_the_column = real_read
    return lines, sorted(kept) if kept is not None else []


@pytest.mark.parametrize("layer", [True, False])
def test_validate_s_chain_lines_with_the_file_s_own_readings_are_the_lines_without_them(tmp_path, layer):
    taken, handed = _lines(tmp_path / "taken", True, layer=layer)
    alone, _none = _lines(tmp_path / "alone", False, layer=layer)
    assert taken is not None and handed
    assert repr(taken) == repr(alone)


@pytest.mark.parametrize("layer", [True, False])
def test_validate_s_chain_lines_read_no_column_again_where_the_file_s_reading_was_kept(tmp_path, layer):
    again: "list[str]" = []
    _lines(tmp_path / "taken", True, again, layer=layer)
    without: "list[str]" = []
    _lines(tmp_path / "alone", False, without, layer=layer)
    assert without, "without the readings the lines read the file's columns again"
    assert len(again) < len(without), (again, without)
    assert not again, again


def _validated(tmp_path, keep: bool) -> "tuple[bytes, list[str], int]":
    """`synthtwin validate` of the visits table against its own switched description (the patient layer standing):
    the quality report's bytes, the columns its chain lines read again, and how many readings they were handed.

    A table under the floor draws no chain through `synthtwin profile`, so the switched description is the
    library's (`chain.with_rules` with the layer's `grain` and blocks, as a switched run writes it).
    """
    from synthtwin import chain_validation, cli

    chained, _handed, _kept = _layered(tmp_path, False)
    path = tmp_path / "visits.csv"
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    plain = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"])
    switched = json.loads(json.dumps(chain.with_rules(plain, chained)))
    switched["relationships"]["grain"] = chained.grain
    switched["columns"] = chained.columns
    described = fixtures.write_profile(tmp_path, "visits-profile.json", switched)
    real_lines = chain_validation.lines_of
    real_read = taxonomy._read_the_column
    real_spellings = taxonomy.spellings_read
    seen = {"inside": False, "name": "", "handed": 0}
    again: "list[str]" = []

    def lines(*arguments, **keywords):  # type: ignore[no-untyped-def]
        given = list(arguments)
        if not keep:
            given = given[:8] + [None]
        seen["handed"] = len(given[8]) if len(given) > 8 and given[8] is not None else 0
        seen["inside"] = True
        try:
            return real_lines(*given, **keywords)
        finally:
            seen["inside"] = False

    def naming(values, name, *arguments, **keywords):  # type: ignore[no-untyped-def]
        seen["name"] = name if seen["inside"] else ""
        try:
            return real_spellings(values, name, *arguments, **keywords)
        finally:
            seen["name"] = ""

    def counting(*arguments, **keywords):  # type: ignore[no-untyped-def]
        if seen["name"]:
            again.append(f"{seen['name']}")
        return real_read(*arguments, **keywords)

    chain_validation.lines_of = lines
    taxonomy.spellings_read = naming
    taxonomy._read_the_column = counting
    try:
        code = cli.main(["validate", str(described), "--twin", str(path), "--out-dir", str(tmp_path)])
    finally:
        chain_validation.lines_of = real_lines
        taxonomy.spellings_read = real_spellings
        taxonomy._read_the_column = real_read
    assert code in (0, 3), code
    reports = sorted(tmp_path.glob("*-quality.txt"))
    assert len(reports) == 1, reports
    return reports[0].read_bytes(), again, int(seen["handed"])


def test_validate_hands_its_chain_lines_the_file_s_own_readings_and_reports_the_same_bytes(tmp_path, capsys):
    taken, again, handed = _validated(tmp_path / "taken", True)
    alone, without, _none = _validated(tmp_path / "alone", False)
    capsys.readouterr()
    assert handed > 0, "validate keeps the measured file's readings for its chain lines"
    # ...the same report but for the folder each was written in.
    assert taken.replace(str(tmp_path / "taken").encode(), b"<folder>") == alone.replace(
        str(tmp_path / "alone").encode(), b"<folder>")
    assert without and len(again) < len(without), (again, without)


# -- a reading kept at the owner's floor is taken (lane SCALE) ------------------------------------------------------


def test_a_reading_kept_under_a_naming_rule_reads_as_the_chain_reads_it():
    """`held_back_named` (how a column may name its held-back levels) moves no spelling's reading: kept under it, the
    reading is the chain's own, and the chain takes it."""
    values = ["1.5", "2.5", "", "4.0", "7", "9.25", "a", "b"] * 40
    settings = taxonomy.Settings(small_cell_floor=11)
    for named in (taxonomy.HELD_BACK_NAMED_SCREENED, taxonomy.HELD_BACK_NAMED_ANSWERED, taxonomy.HELD_BACK_NAMED_CHECKED):
        under = dataclasses.replace(settings, held_back_named=named)
        read = taxonomy._read_the_column(values, len(values), under)
        held = taxonomy.HeldReading(values, len(values), under, False, False, False, False, False, (), (), read)
        kept = taxonomy.keep_spellings(held)
        assert isinstance(kept, taxonomy.KeptSpellings)
        assert kept.spellings == taxonomy.spellings_read(values, "x", settings)
        assert taxonomy.spellings_read(values, "x", settings, kept=kept) is kept.spellings
    other = taxonomy.KeptSpellings(len(values), dataclasses.replace(settings, small_cell_floor=12), False, False, False, "",
                                   {"1.5": ("stand-in", None, "1.5")})
    assert taxonomy.spellings_read(values, "x", settings, kept=other) is not other.spellings


def test_at_the_floor_the_layer_takes_the_kept_readings(tmp_path, monkeypatch):
    """At the owner's floor every column the description reads may name its held-back levels: the layer still takes
    each kept reading and reads no kept column again, and writes the same bytes. (The floor is lowered for the case,
    as a table of 20,000 rows would make it slow; `_held_back_named_here` reads it off the table it describes.)"""
    from synthtwin import parsing

    monkeypatch.setattr(parsing, "TABLE_ROW_FLOOR", 1000)
    again: "list[str]" = []
    taken, handed, _kept = _layered(tmp_path / "taken", True, again)
    alone, _none, _kept_none = _layered(tmp_path / "alone", False)
    names = ["pid", "arm", "gender", "age", "visit_date", "value", "site", "score"]
    assert handed and taken.grain is not None
    assert not set(again) & {names[place] for place in handed}, again
    assert _bytes(taken) == _bytes(alone)


def test_a_column_s_own_reading_of_the_file_s_cells_takes_the_kept_reading(tmp_path, monkeypatch):
    """`chain.described_cells` with ``exact`` reads the column's own reading of the FILE's cells (the spellings it
    counts absent): handed the description's kept reading, it hands it to `taxonomy.spellings_read` (which takes it
    where it matches), and the cells are the ones it gives without it."""
    header, rows = _visits(1500, 7, 99)
    tmp_path.mkdir(parents=True, exist_ok=True)
    path = fixtures.write(tmp_path, "visits.csv", ",".join(header) + "\n" + "".join(",".join(row) + "\n" for row in rows))
    settings = dataclasses.replace(taxonomy.Settings(small_cell_floor=FLOOR), person_columns=("pid",))
    table = reading.read_table(str(path), small_cell_floor=FLOOR)
    kept: "dict[int, taxonomy.KeptSpellings]" = {}
    document = profile.build_document(table, settings, ["pid"], [], [], subjects=["pid"], kept_spellings=kept,
                                      top_code=True)
    blocks = {f"{block['name']}": block for block in document["columns"]}
    place = header.index("age")
    assert blocks["age"].get("top_coded") and place in kept
    declared = {"code": False, "measurement": False, "decimal_comma": False}
    handed: "list[object]" = []
    real = taxonomy.spellings_read

    def watching(values, name, *arguments, **keywords):  # type: ignore[no-untyped-def]
        handed.append(keywords.get("kept"))
        return real(values, name, *arguments, **keywords)

    monkeypatch.setattr(taxonomy, "spellings_read", watching)
    taken = chain.described_cells(table, place, blocks["age"], settings, declared, "", True, 0, kept[place])
    alone = chain.described_cells(table, place, blocks["age"], settings, declared, "", True, 0)
    assert handed and handed[0] is kept[place] and handed[-1] is None
    assert taken == alone
